"""无人值守跑通 Introduction：状态机等菜单 → 点 Play → 循环点对话 X → 读存档确认通关 → 正常退出。

判据（全部机器可判，不靠看画面文字）：
  * 起点：存档 `LastCompleteLevel` 的初值记下来；
  * 过程：`uistate` 确认到 menu，`uitemplate` 定位对话气泡的 X 并真实点击；
  * 终点：**存档 `LastCompleteLevel` 比初值大**（游戏自己写的进度），且进程从菜单正常退出。

为什么用存档而不是找结算页：进度值是游戏自己写的状态，比"认图"稳；结算页文字/位置会变。

用法：
    python tools/e2e_tutorial.py --dir work/winprobe_game --anchors work/uianchors.npz
        [--clicks 40] [--shots work/e2e]
"""
import argparse
import ctypes
import ctypes.wintypes as wt
import os
import subprocess
import sys
import time

import numpy as np

TOOLS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, TOOLS)
import uistate      # noqa: E402
import uitemplate   # noqa: E402
import profile as saveprofile  # noqa: E402

u = uistate.u

PLAY = (0.35, 0.41)
GEAR = (0.965, 0.04)
MAIN_MENU = (0.845, 0.305)
EXIT = (0.677, 0.722)
EXIT_YES = (0.378, 0.722)


def progress():
    return saveprofile.parse(saveprofile.decode()).get("LastCompleteLevel")


def click_screen(x, y):
    u.SetCursorPos(int(x), int(y))
    time.sleep(0.12)
    u.mouse_event(0x0002, 0, 0, 0, 0)
    time.sleep(0.05)
    u.mouse_event(0x0004, 0, 0, 0, 0)


def click_frac(win, frac):
    h, l, t, r, b = win
    u.SetForegroundWindow(h)
    time.sleep(0.25)
    x, y = int(l + (r - l) * frac[0]), int(t + (b - t) * frac[1])
    click_screen(x, y)
    print("  click %r -> %d,%d" % (frac, x, y))


def wait_state(anchors, win, want, timeout, poll=0.4):
    t0 = time.time()
    last = None
    while time.time() - t0 < timeout:
        st, score, margin, _ = uistate._state_from_win(anchors, win)
        last = (st, score, margin)
        if st == want:
            print("  state=%s after %.1fs (score=%.1f margin=%.2f)" % (st, time.time() - t0, score, margin))
            return True
        time.sleep(poll)
    print("  TIMEOUT %s last=%r" % (want, last))
    return False


def shot(win, out):
    h, l, t, r, b = win
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-f", "gdigrab",
                    "-offset_x", str(l), "-offset_y", str(t),
                    "-video_size", "%dx%d" % (r - l, b - t), "-framerate", "1", "-i", "desktop",
                    "-frames:v", "1", "-y", out], check=False)


def pids():
    TH32CS_SNAPPROCESS = 0x00000002
    class PE(ctypes.Structure):
        _fields_ = [("dwSize", wt.DWORD), ("cntUsage", wt.DWORD), ("th32ProcessID", wt.DWORD),
                    ("th32DefaultHeapID", ctypes.POINTER(ctypes.c_ulong)), ("th32ModuleID", wt.DWORD),
                    ("cntThreads", wt.DWORD), ("th32ParentProcessID", wt.DWORD),
                    ("pcPriClassBase", ctypes.c_long), ("dwFlags", wt.DWORD),
                    ("szExeFile", wt.CHAR * 260)]
    k32 = ctypes.windll.kernel32
    snap = k32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
    e = PE()
    e.dwSize = ctypes.sizeof(e)
    out = {}
    if k32.Process32First(snap, ctypes.byref(e)):
        while True:
            out[e.th32ProcessID] = e.szExeFile.decode("mbcs", "ignore")
            if not k32.Process32Next(snap, ctypes.byref(e)):
                break
    k32.CloseHandle(snap)
    return out


def browser_pids():
    return {pid for pid, name in pids().items()
            if name.lower() in ("chrome.exe", "msedge.exe", "firefox.exe", "iexplore.exe",
                                "brave.exe", "opera.exe")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=r"C:\tmp\Magnetic Adventure\work\winprobe_game")
    ap.add_argument("--exe", default="game.exe")
    ap.add_argument("--anchors", default=r"work\uianchors.npz")
    ap.add_argument("--template", default=r"work\templates\close_x.png")
    ap.add_argument("--clicks", type=int, default=40)
    ap.add_argument("--shots", default="work/e2e")
    ap.add_argument("--exit-mode", choices=("kill", "menu"), default="kill",
                    help="kill=直接杀进程（默认，无副作用）；menu=走游戏内退出链"
                         "（会触发 SQUALL_Free 等收尾，但原版会 ShellExecute 打开网页广告，F173）")
    ap.add_argument("--keep", action="store_true")
    args = ap.parse_args()

    anchors = np.load(args.anchors, allow_pickle=False)
    tpl = uitemplate.to_gray(uitemplate.Image.open(args.template))
    os.makedirs(args.shots, exist_ok=True)

    start = progress()
    pids_before = browser_pids()
    print("start LastCompleteLevel=%r" % start)

    p = subprocess.Popen([os.path.join(args.dir, args.exe)], cwd=args.dir)
    print("pid=%d" % p.pid)
    try:
        win = None
        for _ in range(120):
            time.sleep(0.5)
            win = uistate.find_window(p.pid)
            if win:
                break
        if not win:
            print("error=no_window")
            return 1

        print("[1] wait menu")
        if not wait_state(anchors, win, "menu", 45):
            shot(win, os.path.join(args.shots, "fail_menu.png"))
            return 2

        print("[2] click Play")
        click_frac(win, PLAY)
        time.sleep(1.5)
        if uistate._state_from_win(anchors, win)[0] == "menu":
            print("  Play 未生效")
            shot(win, os.path.join(args.shots, "fail_play.png"))
            return 3
        shot(win, os.path.join(args.shots, "01_level.png"))

        # 用户实测：气泡位置固定 ⇒ 优先点固定坐标；模板命中时改点模板中心（更准）。
        # 注意单位：抓到的客户区是**物理**像素 1527x1108（游戏 DPI-unaware 被放 1.5x），
        # 不是游戏自己的 1018x739；比例必须按抓图尺寸算（踩过一次：用 1018 算成 0.908）。
        X_FRAC = (0.605, 0.552)
        print("[3] advance dialogues at %r, progress was %r" % (X_FRAC, start))
        done = False
        for i in range(args.clicks):
            img, (ox, oy) = uitemplate.grab_client(win)
            cx, cy, score = uitemplate.ncc_match(uitemplate.to_gray(img), tpl)
            cur = progress()
            if cur != start:
                print("  progress %r -> %r after %d clicks" % (start, cur, i))
                done = True
                break
            cw, ch = img.size
            if score >= 0.7:
                sx, sy = ox + cx + tpl.shape[1] // 2, oy + cy + tpl.shape[0] // 2
                click_screen(sx, sy)
                print("  click X #%d at %d,%d (bubble score=%.2f)" % (i + 1, sx, sy, score))
            else:
                sx, sy = ox + int(cw * X_FRAC[0]), oy + int(ch * X_FRAC[1])
                click_screen(sx, sy)
                print("  未见气泡(score=%.2f)，点固定坐标 %d,%d" % (score, sx, sy))
            time.sleep(1.5)
        shot(win, os.path.join(args.shots, "02_after_dialogue.png"))
        if not done:
            print("  dialog 循环耗尽，progress 仍是 %r" % progress())
            return 4

        if args.exit_mode == "menu":
            print("[4] graceful exit (游戏内退出链；会弹网页广告，F173)")
            for frac in (GEAR, MAIN_MENU, EXIT, EXIT_YES):
                click_frac(win, frac)
                time.sleep(2.5)
        else:
            print("[4] exit-mode=kill（默认）：不触发退出链的广告弹窗")
            subprocess.run(["taskkill", "/PID", str(p.pid), "/F"], capture_output=True)
            time.sleep(0.5)
        for _ in range(20):
            if p.poll() is not None:
                break
            time.sleep(0.5)
        exited = p.poll() is not None
        print("  process_exited=%s rc=%r" % (exited, p.returncode))
        # 原版退出链会用 ShellExecute 打开一个网页（"广告弹窗"，F173）：只在默认浏览器里
        # 新开标签，不算失败；这里只报告，不动用户的浏览器
        if args.exit_mode == "menu":
            new = browser_pids() - pids_before
            if new:
                print("  ad_popup_pids=%r（退出链用 ShellExecute 打开的网页，F173）" % sorted(new))
        return 0 if exited else 5
    finally:
        if not args.keep and p.poll() is None:
            subprocess.run(["taskkill", "/PID", str(p.pid), "/F"], capture_output=True)
            print("killed=1")


if __name__ == "__main__":
    sys.exit(main())
