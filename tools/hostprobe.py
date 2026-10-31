r"""Host probe: attach headless x32dbg to the running original game, arm breakpoints,
drive Play, dump registers + memory at each hit, then stop.

Usage:
  python tools/hostprobe.py --bp 0x59915A=GS --bp 0x5982FF=JN --expect 3 \
      --out work/hostprobe_intro.jsonl [--dir work/winprobe_game] [--no-play] \
      [--mem 0x100] [--timeout 60]

Requirements:
  * system IME = Microsoft Pinyin (Sogou injects *_bundle modules that stop the debugger)
  * x32\headless\headless.ini [Events] all 0 / EntryBreakpoint=0 (tasks/HANDOFF.MD)
  * the caller owns the save state (this tool never edits the profile)

Criteria / output:
  * one JSONL record per breakpoint hit: seq, tag, eip, eax, regs, mem hex
  * A/A: two runs of the same level give the same tag/eip sequence (addresses differ)

Boundary:
  * 32-bit target only; MCP server at 127.0.0.1:9095, bearer token read from
    x32\mcp_config.json; pause is issued as the native `pause` command (F253).
  * synthetic clicks (mouse_event / PostMessage / VK_RETURN) do NOT start a level
    while the debugger is attached (F257) -> run with --no-play and click Play by hand.
"""
import argparse
import ctypes
import ctypes.wintypes as wt
import json
import os
import socket
import subprocess
import sys
import threading
import time

import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import uistate  # noqa: E402

REL = os.path.join(os.environ["LOCALAPPDATA"], "Microsoft", "WinGet", "Packages",
                   "x64dbg.x64dbg_Microsoft.Winget.Source_8wekyb3d8bbwe", "release")
HEADLESS = os.path.join(REL, "x32", "headless.exe")
CONFIG = os.path.join(REL, "x32", "mcp_config.json")
MCP_URL = "http://127.0.0.1:9095/"
# CREATE_NO_WINDOW: 无头调试器/游戏都不要弹控制台挡住游戏窗口（QQ 反馈）
NO_WINDOW = 0x08000000


def load_token():
    with open(CONFIG, encoding="utf-8") as f:
        return json.load(f).get("AuthToken", "")


class MCP:
    def __init__(self, token):
        self.s = requests.Session()
        self.sid = None
        self.next_id = 0
        self.token = token

    def _headers(self):
        h = {"Accept": "application/json, text/event-stream",
             "Content-Type": "application/json",
             "Authorization": "Bearer " + self.token}
        if self.sid:
            h["Mcp-Session-Id"] = self.sid
        return h

    def _post(self, payload, timeout=30):
        r = self.s.post(MCP_URL, json=payload, headers=self._headers(),
                        stream=True, timeout=timeout)
        sid = r.headers.get("Mcp-Session-Id")
        if sid:
            self.sid = sid
        ctype = r.headers.get("Content-Type", "")
        if "text/event-stream" in ctype:
            data = []
            for line in r.iter_lines(decode_unicode=True):
                if line and line.startswith("data:"):
                    data.append(line[5:].strip())
            r.close()
            return json.loads("\n".join(data)) if data else None
        txt = r.text
        r.close()
        return json.loads(txt) if txt.strip() else None

    def initialize(self):
        res = self._post({"jsonrpc": "2.0", "id": 1, "method": "initialize",
                          "params": {"protocolVersion": "2025-03-26",
                                     "capabilities": {},
                                     "clientInfo": {"name": "hostprobe", "version": "0.1"}}})
        self._post({"jsonrpc": "2.0", "method": "notifications/initialized"}, timeout=10)
        return res

    def call(self, name, args=None, timeout=30):
        self.next_id += 1
        res = self._post({"jsonrpc": "2.0", "id": self.next_id, "method": "tools/call",
                          "params": {"name": name, "arguments": args or {}}}, timeout=timeout)
        if res is None:
            return None
        if "error" in res:
            raise RuntimeError("%s: %s" % (name, res["error"]))
        out = res.get("result", {}).get("content", [])
        texts = [c.get("text", "") for c in out if c.get("type") == "text"]
        return "\n".join(texts)


def wait_port(port, timeout=20):
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            with socket.create_connection(("127.0.0.1", port), 0.5):
                return True
        except OSError:
            time.sleep(0.3)
    return False


def parse_state(text):
    st = {}
    for line in (text or "").splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            st[k.strip()] = v.strip()
    return st


def parse_regs(text):
    regs = {}
    for line in (text or "").splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            k = k.strip()
            if k in ("eax", "ebx", "ecx", "edx", "esi", "edi", "ebp", "esp", "eip", "eflags"):
                regs[k] = int(v.strip(), 16)
    return regs


def mem_hex(text):
    # ReadMemory output: "0ADDR: bytes (" hexdump; take everything before the ASCII column
    parts = []
    for line in (text or "").splitlines():
        if ":" in line:
            hexpart = line.split(":", 1)[1]
            hexpart = hexpart.split("(")[0]
            parts.append(hexpart.replace(" ", ""))
    return "".join(parts)


def find_window(pid, timeout=60):
    """只认可见、面积 > 100k px 的自有窗口里最大的那个（同名/隐藏窗口会点空）。"""
    u = uistate.u
    t0 = time.time()
    while time.time() - t0 < timeout:
        found = []

        @ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
        def cb(h, l):
            p = wt.DWORD()
            u.GetWindowThreadProcessId(h, ctypes.byref(p))
            if p.value != pid or not u.IsWindowVisible(h):
                return True
            n = ctypes.create_unicode_buffer(256)
            u.GetWindowTextW(h, n, 256)
            r = wt.RECT()
            u.GetWindowRect(h, ctypes.byref(r))
            area = (r.right - r.left) * (r.bottom - r.top)
            if area > 100000:
                found.append((area, h, n.value, (r.left, r.top, r.right, r.bottom)))
            return True

        u.EnumWindows(cb, 0)
        if found:
            found.sort(key=lambda x: -x[0])
            area, h, title, rect = found[0]
            print("window", hex(h), repr(title), rect, flush=True)
            return (h,) + rect
        time.sleep(0.5)
    return None


def shot(rect, path):
    l, t, r, b = rect
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-f", "gdigrab",
                    "-offset_x", str(l), "-offset_y", str(t),
                    "-video_size", "%dx%d" % (r - l, b - t),
                    "-framerate", "1", "-i", "desktop", "-frames:v", "1", "-y", path],
                   creationflags=NO_WINDOW)


def wait_menu(win, timeout=40):
    anchors = uistate.np.load(os.path.join(ROOT, "work", "uianchors.npz"))
    t0 = time.time()
    while time.time() - t0 < timeout:
        st, score, margin, _ = uistate._state_from_win(anchors, win)
        if st == "menu":
            return True
        time.sleep(0.4)
    return False


def force_foreground(h):
    u = uistate.u
    u.SetForegroundWindow(h)


def foreground_title():
    u = uistate.u
    h = u.GetForegroundWindow()
    n = ctypes.create_unicode_buffer(256)
    u.GetWindowTextW(h, n, 256)
    return hex(h), n.value


def window_pid(h):
    p = wt.DWORD()
    uistate.u.GetWindowThreadProcessId(h, ctypes.byref(p))
    return p.value


def click_play(win, shot_prefix="", want_pid=0):
    h, l, t, r, b = win
    u = uistate.u
    if shot_prefix:
        shot((l, t, r, b), shot_prefix + "_before.png")
    force_foreground(h)
    time.sleep(0.3)
    x = int(l + (r - l) * 0.35)
    y = int(t + (b - t) * 0.41)
    print("  click hwnd", hex(h), "rect", (l, t, r, b), "at", (x, y),
          "fg", foreground_title(), flush=True)
    # 双击：第一次激活窗口，第二次才是按钮（F257 的对照实验里 mouse_event x2 生效；
    # 不要发 VK_RETURN——会触发 Exit，游戏正常退出 exit 0，看起来像崩）。
    pt = wt.POINT(x, y)
    h2 = u.WindowFromPoint(pt)
    print("  WindowFromPoint", hex(h2 or 0), "pid", window_pid(h2) if h2 else 0, flush=True)
    for _ in range(2):
        u.SetCursorPos(x, y)
        time.sleep(0.15)
        u.mouse_event(0x0002, 0, 0, 0, 0)
        time.sleep(0.06)
        u.mouse_event(0x0004, 0, 0, 0, 0)
        time.sleep(0.8)
    if shot_prefix:
        time.sleep(0.6)
        shot((l, t, r, b), shot_prefix + "_after.png")
    return x, y


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=os.path.join(ROOT, "work", "winprobe_game"))
    ap.add_argument("--exe", default="game.exe")
    ap.add_argument("--bp", action="append", default=[],
                    help="RVA=tag, e.g. 0x59915A=Add_GraphSprite; repeatable")
    ap.add_argument("--bp-file", default="", help="lines '0xADDR<TAB>tag'")
    ap.add_argument("--expect", type=int, default=0, help="stop after N hits (0 = until timeout)")
    ap.add_argument("--mem", type=lambda s: int(s, 0), default=0x100,
                    help="bytes to dump at eax (0 = none)")
    ap.add_argument("--out", default=os.path.join(ROOT, "work", "hostprobe.jsonl"))
    ap.add_argument("--no-play", action="store_true")
    ap.add_argument("--timeout", type=float, default=60.0)
    ap.add_argument("--pause-first", action="store_true")
    args = ap.parse_args()

    bps = []
    for spec in args.bp:
        addr, _, tag = spec.partition("=")
        bps.append((int(addr, 0), tag or ("0x%X" % int(addr, 0))))
    if args.bp_file:
        for line in open(args.bp_file, encoding="utf-8"):
            line = line.strip()
            if not line:
                continue
            addr, _, tag = line.partition("\t")
            bps.append((int(addr, 0), tag))

    subprocess.run(["taskkill", "/IM", "headless.exe", "/F"], capture_output=True,
                   creationflags=NO_WINDOW)
    game = subprocess.Popen([os.path.join(args.dir, args.exe)], cwd=args.dir,
                            creationflags=NO_WINDOW)
    print("game pid", game.pid, flush=True)
    win = find_window(game.pid)
    if not win:
        print("FAIL no window")
        return 2
    if not wait_menu(win):
        print("FAIL menu not reached")
        return 2
    print("menu ok", flush=True)

    hd = subprocess.Popen([HEADLESS, "-pid", str(game.pid)],
                          stdout=open(os.path.join(ROOT, "work", "hostprobe_hd.log"), "wb"),
                          stderr=subprocess.STDOUT, creationflags=NO_WINDOW)
    try:
        if not wait_port(9095):
            print("FAIL mcp port")
            return 2
        m = MCP(load_token())
        m.initialize()
        st = {}
        for _ in range(60):
            st = parse_state(m.call("GetDebugState"))
            if st.get("isDebugging") == "true" and st.get("pid") == str(game.pid):
                break
            time.sleep(0.3)
        if st.get("pid") != str(game.pid):
            print("FAIL port 9095 owned by another debugger:", st)
            return 3
        # attach 后引擎要几秒才把模块表建好，过早 SetBPX 会返回 Failed
        time.sleep(2.5)
        print("debugger", st, flush=True)
        # headless 下插件的写操作（SetBreakpoint / `bp`）静默无效（F260），本脚本不再写断点：
        # 断点必须先用 tools/moduledb.py 注入模块库（F261），这里只核对它们已加载。
        if bps:
            lst = (m.call("ListBreakpoints") or "").lower()
            missing = [hex(a) for a, _ in bps if ("0x%X" % a).lower() not in lst]
            print("bps loaded", len(bps) - len(missing), "missing", len(missing), flush=True)
            if missing:
                print("FAIL missing", missing[:8],
                      "-> inject with tools/moduledb.py then restart headless (F261)", flush=True)
                return 3
        if args.pause_first:
            print("pause", m.call("ExecuteDebuggerCommand", {"command": "pause"}), flush=True)
        with open(os.path.join(ROOT, "work", "hostprobe_ready.txt"), "w") as f:
            f.write(str(game.pid))
        if not args.no_play:
            print("click", click_play(
                win, os.path.join(ROOT, "work", "probe_click_0"), want_pid=game.pid),
                flush=True)

        out = open(args.out, "w", encoding="utf-8")
        hits = 0
        t0 = time.time()
        seen = []
        while time.time() - t0 < args.timeout:
            if game.poll() is not None:
                print("GAME EXITED rc=", game.returncode, flush=True)
                try:
                    tail = open(os.path.join(ROOT, "work", "hostprobe_hd.log"),
                                encoding="utf-8", errors="replace").read()[-2000:]
                    print("--- headless log tail ---\n" + tail, flush=True)
                except OSError:
                    pass
                break
            st = parse_state(m.call("GetDebugState"))
            if st.get("isDebugging") == "false":
                print("DEBUG SESSION GONE", st, flush=True)
                break
            if st.get("isRunning") != "false":
                time.sleep(0.2)
                continue
            regs = parse_regs(m.call("GetAllRegisters"))
            hits += 1
            rec = {"seq": hits, "eip": regs.get("eip"), "eax": regs.get("eax"),
                   "regs": regs}
            mem = ""
            if args.mem and regs.get("eax"):
                mem = mem_hex(m.call("ReadMemory", {"address": hex(regs["eax"]),
                                                    "size": args.mem}))
                rec["mem"] = mem
            edx = regs.get("edx")
            if edx and 0x10000 < edx < 0x7FFFFFFF:
                rec["edx_mem"] = mem_hex(m.call("ReadMemory",
                                                {"address": hex(edx), "size": 0x40}))
            tag = dict(bps).get(regs.get("eip"), "")
            rec["tag"] = tag
            out.write(json.dumps(rec) + "\n")
            out.flush()
            seen.append(rec["eip"])
            print("hit", hits, hex(rec["eip"] or 0), "eax", hex(rec["eax"] or 0), flush=True)
            if args.expect and hits >= args.expect:
                break
            # resume; the call blocks until the next pause, so run it in a thread
            threading.Thread(target=lambda: m.call("ExecuteDebuggerCommand",
                                                   {"command": "run"}, timeout=300),
                             daemon=True).start()
            time.sleep(0.3)
        out.close()
        print("hits", hits, "eips", [hex(x or 0) for x in seen], flush=True)
        m.call("StopDebug")
    finally:
        subprocess.run(["taskkill", "/IM", "headless.exe", "/F"], capture_output=True,
                       creationflags=NO_WINDOW)
        subprocess.run(["taskkill", "/PID", str(game.pid), "/F"], capture_output=True,
                       creationflags=NO_WINDOW)
    return 0


if __name__ == "__main__":
    sys.exit(main())
