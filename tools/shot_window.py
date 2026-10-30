"""截「某个 exe 的窗口客户区」为 PNG —— 原版 `game.exe` 与自建宿主共用同一套参数。

用法:
  python tools/shot_window.py work/glprobe/game.exe work/orig_menu.png --wait 19
  python tools/shot_window.py build/Release/magnethost.exe work/host_menu.png
  SHOT_WAIT=19 python tools/shot_window.py <exe> <png>     # 环境变量写法也行

要点（踩过的坑）:
  - 脚本自己 `SetProcessDpiAwarenessContext(-4)`：目标进程是 **DPI-unaware**（F154），
    客户区按**物理像素**拿到的是 1527×1108（= 1018×739 × 1.5）。算点击比例时必须用
    抓图尺寸，不要用游戏自己的逻辑尺寸（F172）。
  - 抓的是屏幕像素（`ImageGrab`）：窗口必须在前台，被遮挡就抓到别的窗口。
  - 结束时直接 kill（`p.kill()`）：游戏内正常退出会 `ShellExecuteA` 弹网页（F173）。
  - 菜单要在启动后 ~17 s 才出现（F169：loading 0–4 s、intro 4–16.5 s），用 `--wait` 等。
"""
import argparse
import ctypes
import ctypes.wintypes as wt
import os
import subprocess
import sys
import time

from PIL import ImageGrab

u = ctypes.windll.user32


def find_window(pid, title):
    found = []
    WNDENUMPROC = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)

    def cb(h, l):
        q = wt.DWORD()
        u.GetWindowThreadProcessId(h, ctypes.byref(q))
        if q.value == pid and u.IsWindowVisible(h):
            n = u.GetWindowTextLengthW(h)
            if n:
                buf = ctypes.create_unicode_buffer(n + 1)
                u.GetWindowTextW(h, buf, n + 1)
                if buf.value == title:
                    found.append(h)
        return True

    u.EnumWindows(WNDENUMPROC(cb), 0)
    return found[0] if found else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("exe")
    ap.add_argument("out")
    ap.add_argument("--title", default="A Magnetic Adventure")
    ap.add_argument("--wait", type=float, default=float(os.environ.get("SHOT_WAIT", "2.0")),
                    help="窗口出现后再等多少秒（菜单要 ~17 s）")
    ap.add_argument("--poll", type=float, default=15.0, help="等窗口出现的上限（秒）")
    ap.add_argument("--mouse", default="",
                    help="截图前把鼠标放到窗口客户区的这个**设计像素**位置（如 900,700）；"
                         "空=不动。菜单悬停/光标对拍必须让两边落在同一点")
    ap.add_argument("--pos", default="0,0",
                    help="截图前把窗口左上角挪到屏幕这个物理坐标（默认 0,0，避免被别的窗口/任务栏盖住）")
    a = ap.parse_args()

    u.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
    exe = os.path.abspath(a.exe)
    out = os.path.abspath(a.out)
    p = subprocess.Popen([exe], cwd=os.path.dirname(exe))
    try:
        win = None
        t0 = time.time()
        while time.time() - t0 < a.poll:
            time.sleep(0.25)
            win = find_window(p.pid, a.title)
            if win:
                break
        if not win:
            print("no window")
            return 1
        # 抓的是**屏幕**像素：先把窗口挪到确定的位置并置前，否则被别的窗口/任务栏盖住的
        # 那几条边会把别人的像素拍进来（踩过：底部 108 px 拍到了前台终端）。
        px, py = (int(v) for v in a.pos.split(","))
        u.SetWindowPos(win, 0, px, py, 0, 0,
                       0x0001 | 0x0004 | 0x0010)  # NOSIZE|NOZORDER|NOACTIVATE
        u.SetForegroundWindow(win)
        # 鼠标必须在窗口摆好之后再放（窗口一挪，原来的悬停位置就失效了），并且要留出
        # 稳定时间：原版磁铁光标有旋转/缩放过渡。
        if a.mouse:
            mx, my = (float(v) for v in a.mouse.split(","))
            pt0 = wt.POINT(0, 0)
            u.ClientToScreen(win, ctypes.byref(pt0))
            scale = max(1.0, u.GetSystemMetrics(0) / 1707.0)  # 逻辑→物理（原版 DPI-unaware，1.5x）
            u.SetCursorPos(pt0.x + int(mx * scale), pt0.y + int(my * scale))
        time.sleep(a.wait)
        r = wt.RECT()
        u.GetClientRect(win, ctypes.byref(r))
        pt = wt.POINT(0, 0)
        u.ClientToScreen(win, ctypes.byref(pt))
        box = (pt.x, pt.y, pt.x + r.right, pt.y + r.bottom)
        print("client", r.right, r.bottom, "at", pt.x, pt.y)
        ImageGrab.grab(bbox=box, all_screens=True).save(out)
        print("saved", out)
        return 0
    finally:
        p.kill()


if __name__ == "__main__":
    sys.exit(main())
