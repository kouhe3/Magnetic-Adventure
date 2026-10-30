"""无人值守跑一关：状态机等到主菜单 → 真实输入点 Play → 进关 → 等结算 → 从菜单正常退出。

为什么这样写：
  * 点击必须用**真实输入**（F162：PostMessage 合成鼠标消息不会触发按钮）；
  * 每一步都先确认界面状态（F169：intro 占 12.5 s，定时点击必然落空）；
  * 退出走游戏自己的菜单链（F143 已验证会触发 `SQUALL_Free` 等收尾调用），
    这样脚本跑完不会留下僵尸进程、也不会污染下一次运行。

用法：
    python tools/e2e_tutorial.py --dir work/winprobe_game --anchors work/uianchors.npz
        [--level-timeout 120] [--shots work/e2e] [--keep]

判据：退出码 0 = 走到了 menu → 点了 Play → 离开 menu → 从菜单退出且进程消失；
      非 0 = 哪一步超时（打印最后状态与当时的 score/margin）。
覆盖边界：只验证"能进关并正常退出"，**不判关内玩得好不好**（那要靠 FFI 重放/像素 diff）；
          结算画面目前没有锚点，用固定等待 + 截图留证。
"""
import argparse
import os
import subprocess
import sys
import time

import numpy as np

TOOLS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, TOOLS)
import uistate  # noqa: E402

u = uistate.u

# 这些比例沿用 F143 的退出链（窗口 1536×1152 / 客户区 1018×739 时标定的）
PLAY = (0.35, 0.41)
GEAR = (0.965, 0.04)
MAIN_MENU = (0.845, 0.305)
EXIT = (0.677, 0.722)
EXIT_YES = (0.378, 0.722)


def state_now(anchors, win):
    return uistate._state_from_win(anchors, win)


def click(win, frac):
    h, l, t, r, b = win
    u.SetForegroundWindow(h)
    time.sleep(0.25)
    x, y = int(l + (r - l) * frac[0]), int(t + (b - t) * frac[1])
    u.SetCursorPos(x, y)
    time.sleep(0.2)
    u.mouse_event(0x0002, 0, 0, 0, 0)
    time.sleep(0.12)
    u.mouse_event(0x0004, 0, 0, 0, 0)
    print("  click %r -> %d,%d" % (frac, x, y))


def wait_for(anchors, win, want, timeout, poll=0.4):
    t0 = time.time()
    last = None
    while time.time() - t0 < timeout:
        st, score, margin, _ = state_now(anchors, win)
        last = (st, score, margin)
        if st == want:
            print("  state=%s after %.1fs (score=%.1f margin=%.2f)" % (st, time.time() - t0, score, margin))
            return True, last
        time.sleep(poll)
    print("  TIMEOUT waiting %s, last=%r" % (want, last))
    return False, last


def shot(win, out):
    h, l, t, r, b = win
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-f", "gdigrab",
                    "-offset_x", str(l), "-offset_y", str(t),
                    "-video_size", "%dx%d" % (r - l, b - t), "-framerate", "1", "-i", "desktop",
                    "-frames:v", "1", "-y", out], check=False)
    print("  shot %s" % out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=r"C:\tmp\Magnetic Adventure\work\winprobe_game")
    ap.add_argument("--exe", default="game.exe")
    ap.add_argument("--anchors", default=r"work\uianchors.npz")
    ap.add_argument("--level-timeout", type=float, default=90)
    ap.add_argument("--shots", default="work/e2e")
    ap.add_argument("--keep", action="store_true")
    args = ap.parse_args()

    anchors = np.load(args.anchors, allow_pickle=False)
    os.makedirs(args.shots, exist_ok=True)

    p = subprocess.Popen([os.path.join(args.dir, args.exe)], cwd=args.dir)
    print("pid=%d" % p.pid)
    ok = False
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
        if not wait_for(anchors, win, "menu", 45)[0]:
            shot(win, os.path.join(args.shots, "fail_menu.png"))
            return 2
        shot(win, os.path.join(args.shots, "01_menu.png"))

        print("[2] click Play")
        click(win, PLAY)
        time.sleep(1.5)
        st, score, margin, _ = state_now(anchors, win)
        print("  after click: state=%s score=%.1f margin=%.2f" % (st, score, margin))
        if st == "menu":
            print("  Play 没生效（仍在 menu）")
            shot(win, os.path.join(args.shots, "fail_play.png"))
            return 3
        shot(win, os.path.join(args.shots, "02_after_play.png"))

        print("[3] let the level run %.0fs（第一关不操作也会 complete）" % args.level_timeout)
        time.sleep(args.level_timeout)
        shot(win, os.path.join(args.shots, "03_after_level.png"))
        st, score, margin, allsc = state_now(anchors, win)
        print("  level result: state=%s score=%.1f margin=%.2f %r" % (st, score, margin, allsc))

        print("[4] graceful exit: gear -> main menu -> exit -> yes")
        for frac, name in ((GEAR, "gear"), (MAIN_MENU, "main_menu"), (EXIT, "exit"), (EXIT_YES, "yes")):
            click(win, frac)
            time.sleep(2.5)
        for _ in range(20):
            if p.poll() is not None:
                break
            time.sleep(0.5)
        shot(win, os.path.join(args.shots, "04_after_exit.png")) if p.poll() is None else None
        ok = p.poll() is not None
        print("  process_exited=%s rc=%r" % (ok, p.returncode))
        return 0 if ok else 4
    finally:
        if not args.keep and p.poll() is None:
            subprocess.run(["taskkill", "/PID", str(p.pid), "/F"], capture_output=True)
            print("killed=1")


if __name__ == "__main__":
    sys.exit(main())
