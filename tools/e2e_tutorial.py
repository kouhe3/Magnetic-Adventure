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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=r"C:\tmp\Magnetic Adventure\work\winprobe_game")
    ap.add_argument("--exe", default="game.exe")
    ap.add_argument("--anchors", default=r"work\uianchors.npz")
    ap.add_argument("--template", default=r"work\templates\close_x.png")
    ap.add_argument("--clicks", type=int, default=40)
    ap.add_argument("--shots", default="work/e2e")
    ap.add_argument("--keep", action="store_true")
    args = ap.parse_args()

    anchors = np.load(args.anchors, allow_pickle=False)
    tpl = uitemplate.to_gray(uitemplate.Image.open(args.template))
    os.makedirs(args.shots, exist_ok=True)

    start = progress()
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

        # 用户实测：气泡位置固定 ⇒ 直接点固定客户区坐标；模板只用于"有没有气泡"的存在性检测
        X_FRAC = (0.908, 0.827)   # = 模板中心在客户区 1018x739 上的比例
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
            sx, sy = ox + int(cw * X_FRAC[0]), oy + int(ch * X_FRAC[1])
            if score >= 0.7:
                click_screen(sx, sy)
                print("  click X #%d at %d,%d (bubble score=%.2f)" % (i + 1, sx, sy, score))
            else:
                click_screen(sx, sy)
                print("  未见气泡(score=%.2f)，仍点一次固定坐标 %d,%d" % (score, sx, sy))
            time.sleep(1.5)
        shot(win, os.path.join(args.shots, "02_after_dialogue.png"))
        if not done:
            print("  dialog 循环耗尽，progress 仍是 %r" % progress())
            return 4

        print("[4] graceful exit")
        for frac in (GEAR, MAIN_MENU, EXIT, EXIT_YES):
            click_frac(win, frac)
            time.sleep(2.5)
        for _ in range(20):
            if p.poll() is not None:
                break
            time.sleep(0.5)
        exited = p.poll() is not None
        print("  process_exited=%s rc=%r" % (exited, p.returncode))
        return 0 if exited else 5
    finally:
        if not args.keep and p.poll() is None:
            subprocess.run(["taskkill", "/PID", str(p.pid), "/F"], capture_output=True)
            print("killed=1")


if __name__ == "__main__":
    sys.exit(main())
