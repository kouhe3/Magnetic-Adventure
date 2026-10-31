"""Unattended per-level object capture (Add_* factories) for A Magnetic Adventure.

For each level: fresh game process -> attach headless x64dbg (breakpoints come
from the offline module DB, plugin disabled) -> click Map -> click the level
node -> wait for the `#HB` log burst -> parse to JSONL -> kill.

Usage:
  python tools/level_capture.py --levels 1-3
  python tools/level_capture.py --levels all --outdir work/hostcapture

Inputs:
  work/map_nodes.csv   level -> design coords (tools/map_nodes.py, F264)
  work/add_bps_all.txt 62 breakpoints (tools/moduledb.py inject, F261)
  work/winprobe_game/  game copy whose profile has all levels unlocked

Criteria: level N yields 25+ `#HB` lines and the JSONL tag counts match
`work/lua_probe/lvlNN.jsonl` call sequence. Boundaries: assumes the map view is
fixed (unscaled); a failed click produces 0 hits and is reported as MISS.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import uistate as us

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NO_WINDOW = 0x08000000
HB = re.compile(r"^(\S+) (\S+) (\S+) (\S+) (\S+) (\S+)(.*)$")


def sh(*args):
    return subprocess.run(args, capture_output=True)


def plugin_off():
    rel = r"C:\Users\K\AppData\Local\Microsoft\WinGet\Packages\x64dbg.x64dbg_Microsoft.Winget.Source_8wekyb3d8bbwe\release\x32"
    on = os.path.join(rel, "plugins", "x64dbg-MCP-Server.dp32")
    off = on + ".off"
    moved = False
    if os.path.exists(on):
        os.replace(on, off)
        moved = True
    return moved, off, on



def force_fg(hwnd):
    u = us.u
    fg = u.GetForegroundWindow()
    if fg == hwnd:
        return True
    tid_fg = u.GetWindowThreadProcessId(fg, None)
    tid = us.k.GetCurrentThreadId()
    ok = False
    if tid_fg:
        u.AttachThreadInput(tid, tid_fg, True)
        u.ShowWindow(hwnd, 9)
        u.BringWindowToTop(hwnd)
        ok = bool(u.SetForegroundWindow(hwnd))
        u.AttachThreadInput(tid, tid_fg, False)
    else:
        ok = bool(u.SetForegroundWindow(hwnd))
    return ok or u.GetForegroundWindow() == hwnd

def click_design(pid, dx, dy, hold=150):
    win = us.find_window(pid)
    if not win:
        raise RuntimeError("window not found")
    ox, oy, w, h = us.client_rect(win)
    scale = w / 1018.0
    x, y = int(ox + dx * scale), int(oy + dy * scale)
    u = us.u
    u.ShowWindow(win[0], 9)
    u.SetForegroundWindow(win[0])
    time.sleep(0.25)
    u.SetCursorPos(x, y)
    time.sleep(0.15)
    u.mouse_event(0x0002, 0, 0, 0, 0)
    time.sleep(hold / 1000.0)
    u.mouse_event(0x0004, 0, 0, 0, 0)


def wait_menu(pid, timeout=35):
    t0 = time.time()
    win = None
    while time.time() - t0 < 10:
        win = us.find_window(pid)
        if win:
            break
        time.sleep(0.3)
    if not win:
        return False
    anchors = __import__("numpy").load(os.path.join(ROOT, "work", "uianchors.npz"))
    gr = us._Graber()
    try:
        while time.time() - t0 < timeout:
            st, score, margin, _ = us.classify(anchors, gr.grab(us.client_rect(win)))
            if st == "menu":
                return True
            time.sleep(0.5)
        return False
    finally:
        gr.close()


def parse_log(path):
    rows = []
    for line in open(path, encoding="utf-8", errors="replace"):
        if not line.startswith("#HB "):
            continue
        body = line[4:]
        for mark in ("[STATE]", "[x64dbg"):
            i = body.find(mark)
            if i >= 0:
                body = body[:i]
        m = HB.match(body.rstrip())
        if not m:
            continue
        tag, eax, edx, d0, d8, d12, tail = m.groups()
        rec = {"tag": tag, "eax": "0x" + eax, "edx": "0x" + edx,
               "obj": ["0x" + d0, "0x" + d8, "0x" + d12]}
        q = re.search(r'"([^"]*)"', tail)
        if q:
            rec["name"] = q.group(1)
        rows.append(rec)
    return rows



def stalled(path):
    """True when the log tail is a breakpoint hit with no following #HB line."""
    last_hb = last_bp = -1
    for i, l in enumerate(open(path, encoding="utf-8", errors="replace")):
        if l.startswith("#HB "):
            last_hb = i
        elif l.startswith("INT3 breakpoint"):
            last_bp = i
    return last_bp > last_hb


_MAP_REF = None


def _map_ref():
    global _MAP_REF
    if _MAP_REF is None:
        from PIL import Image
        im = Image.open(os.path.join(ROOT, "work", "map_screen.png")).convert("RGB")
        _MAP_REF = im.crop((1, 39, 1 + 1018, 39 + 739)).resize((255, 185))
    return _MAP_REF


def map_diff(pid):
    """Mean abs diff (sampled) between the current client and the map reference."""
    from PIL import ImageGrab
    win = us.find_window(pid)
    if not win:
        return 999.0
    ox, oy, w, h = us.client_rect(win)
    img = ImageGrab.grab(bbox=(ox, oy, ox + w, oy + h)).convert("RGB").resize((255, 185))
    ref = _map_ref()
    a = list(img.getdata())
    b = list(ref.getdata())
    tot = 0
    n = 0
    for i in range(0, len(a), 7):
        pa, pb = a[i], b[i]
        tot += abs(pa[0] - pb[0]) + abs(pa[1] - pb[1]) + abs(pa[2] - pb[2])
        n += 3
    return tot / max(n, 1)


def open_map(pid):
    for _ in range(3):
        click_design(pid, 285, 414)
        time.sleep(0.9)
        d = map_diff(pid)
        print("  map diff %.1f" % d, flush=True)
        if d < 25.0:
            return True
    return False

def capture_level(level, node, args, headless):
    game_dir = args.game_dir
    pid = subprocess.Popen([os.path.join(game_dir, "game.exe")], cwd=game_dir,
                           creationflags=NO_WINDOW).pid
    log = os.path.join(args.outdir, "lvl%02d.log" % level)
    hd = None
    try:
        if not wait_menu(pid, args.menu_timeout):
            return None, "no menu"
        hd = subprocess.Popen([headless, "-pid", str(pid)], cwd=os.path.dirname(headless),
                              stdout=open(log, "wb"), creationflags=NO_WINDOW)
        time.sleep(args.attach_wait)
        if not open_map(pid):
            return None, "map not opened"
        time.sleep(0.4)
        click_design(pid, node[0], node[1])
        # wait for the Add_* burst
        t0 = time.time()
        last, stable = -1, 0.0
        win = us.find_window(pid)
        while time.time() - t0 < args.burst_timeout:
            time.sleep(0.4)
            if win:
                force_fg(win[0])   # the game pauses on WM_KILLFOCUS; focus loss can stall init
            try:
                n = sum(1 for l in open(log, encoding="utf-8", errors="replace")
                        if l.startswith("#HB "))
            except OSError:
                n = 0
            if n != last:
                print("  burst t=%.1f n=%d" % (time.time() - t0, n), flush=True)
            if n > 0 and n == last:
                stable += 0.4
                if stable >= 8.0:
                    break
            else:
                stable = 0.0
            last = n
        time.sleep(1.5)   # grace so the level screen paints before the kill
    finally:
        sh("taskkill", "/PID", str(pid), "/F")
        if hd:
            sh("taskkill", "/PID", str(hd.pid), "/F")
    rows = parse_log(log)
    with open(os.path.join(args.outdir, "lvl%02d.jsonl" % level), "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    return rows, ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--levels", default="1")
    ap.add_argument("--csv", default=os.path.join(ROOT, "work", "map_nodes.csv"))
    ap.add_argument("--outdir", default=os.path.join(ROOT, "work", "hostcapture"))
    ap.add_argument("--game-dir", default=os.path.join(ROOT, "work", "winprobe_game"))
    ap.add_argument("--bps", default=os.path.join(ROOT, "work", "add_bps_all.txt"))
    ap.add_argument("--headless", default=r"C:\Users\K\AppData\Local\Microsoft\WinGet\Packages\x64dbg.x64dbg_Microsoft.Winget.Source_8wekyb3d8bbwe\release\x32\headless.exe")
    ap.add_argument("--db", default=r"C:\Users\K\AppData\Local\Microsoft\WinGet\Packages\x64dbg.x64dbg_Microsoft.Winget.Source_8wekyb3d8bbwe\release\x32\headless\db\game.exe.dd32")
    ap.add_argument("--menu-timeout", type=float, default=35)
    ap.add_argument("--attach-wait", type=float, default=6)
    ap.add_argument("--burst-timeout", type=float, default=30)
    ap.add_argument("--retries", type=int, default=2)
    a = ap.parse_args()

    nodes = {}
    for line in open(a.csv, encoding="utf-8"):
        p = line.strip().split(",")
        if len(p) == 4 and p[0].isdigit():
            nodes[int(p[0])] = (float(p[2]), float(p[3]))
    if a.levels == "all":
        levels = sorted(nodes)
    else:
        m = re.match(r"(\d+)-(\d+)$", a.levels)
        levels = list(range(int(m.group(1)), int(m.group(2)) + 1)) if m else [int(a.levels)]

    os.makedirs(a.outdir, exist_ok=True)
    moved, off, on = plugin_off()
    sh("python", os.path.join(ROOT, "tools", "moduledb.py"), "inject", a.db,
       os.path.join(a.game_dir, "game.exe"), a.bps)
    try:
        for i, lv in enumerate(levels, 1):
            t0 = time.time()
            probe_n = 0
            pp = os.path.join(ROOT, "work", "lua_probe", "lvl%02d.jsonl" % (lv - 1))
            if os.path.exists(pp):
                probe_n = sum(1 for l in open(pp, encoding="utf-8")
                              if l.strip() and json.loads(l).get("call", "").startswith("Add_"))
            target = max(probe_n - 2, 1)
            best, err = None, ""
            for attempt in range(a.retries + 1):
                rows, err = capture_level(lv, nodes[lv], a, a.headless)
                log = os.path.join(a.outdir, "lvl%02d.log" % lv)
                if rows and (best is None or len(rows) > len(best)):
                    best = rows
                if rows and len(rows) >= target and not stalled(log):
                    break
                if err:
                    break
                time.sleep(1.0)
            rows = best
            tags = {}
            for r in rows or []:
                tags[r["tag"]] = tags.get(r["tag"], 0) + 1
            print("lvl%02d %s hits=%d %s (%.1fs)" % (
                lv, "OK" if rows else "MISS", len(rows or []),
                " ".join("%s=%d" % kv for kv in sorted(tags.items())) or err,
                time.time() - t0), flush=True)
    finally:
        if moved:
            os.replace(off, on)


if __name__ == "__main__":
    main()
