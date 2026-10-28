#!/usr/bin/env python3
"""游戏驱动：保持一个 game.exe 常驻，按窗口坐标截图/点击（DPI 感知，坐标为物理像素）。

用法:
  python tools/game_drive.py start            # 启动并等待窗口
  python tools/game_drive.py shot out.png     # 截窗口区域
  python tools/game_drive.py click 0.267 0.278  # 按窗口内相对坐标点击
  python tools/game_drive.py rect
  python tools/game_drive.py kill
"""
import ctypes
import ctypes.wintypes as wt
import os
import subprocess
import sys
import time

ROOT = r"C:\tmp\Magnetic Adventure"
PID_FILE = os.path.join(ROOT, "work", "game_pid.txt")
GAME_DIR = os.path.join(ROOT, "work", "integration")

u = ctypes.windll.user32
ctypes.windll.user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))

WNDENUMPROC = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)


def find_window(pid):
    found = []

    def cb(h, l):
        p = wt.DWORD()
        u.GetWindowThreadProcessId(h, ctypes.byref(p))
        if p.value == pid and u.IsWindowVisible(h):
            r = wt.RECT()
            u.GetWindowRect(h, ctypes.byref(r))
            n = ctypes.create_unicode_buffer(256)
            u.GetWindowTextW(h, n, 256)
            if "Magnetic" in n.value and r.right - r.left > 100:
                found.append((h, r.left, r.top, r.right, r.bottom))
        return True

    u.EnumWindows(WNDENUMPROC(cb), 0)
    return found[0] if found else None


def current_pid():
    if not os.path.exists(PID_FILE):
        return None
    return int(open(PID_FILE).read().strip())


def wait_window(pid, timeout=40):
    end = time.time() + timeout
    while time.time() < end:
        w = find_window(pid)
        if w:
            return w
        time.sleep(0.5)
    return None


def start():
    subprocess.run(["taskkill", "/IM", "game.exe", "/F"], capture_output=True)
    time.sleep(0.5)
    p = subprocess.Popen([os.path.join(GAME_DIR, "game.exe")], cwd=GAME_DIR)
    os.makedirs(os.path.dirname(PID_FILE), exist_ok=True)
    open(PID_FILE, "w").write(str(p.pid))
    w = wait_window(p.pid)
    print("pid", p.pid, "window", w)


def shot(out):
    pid = current_pid()
    w = find_window(pid) if pid else None
    if not w:
        print("no window")
        return 2
    h, l, t, r, b = w
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-f", "gdigrab",
                    "-offset_x", str(l), "-offset_y", str(t),
                    "-video_size", f"{r-l}x{b-t}", "-framerate", "1", "-i", "desktop",
                    "-frames:v", "1", "-y", out], check=False)
    print("shot", out, l, t, r - l, b - t)
    return 0


def click(fx, fy):
    pid = current_pid()
    w = find_window(pid) if pid else None
    if not w:
        print("no window")
        return 2
    h, l, t, r, b = w
    x = int(l + (r - l) * fx)
    y = int(t + (b - t) * fy)
    u.SetCursorPos(x, y)
    time.sleep(0.25)
    u.mouse_event(0x0002, 0, 0, 0, 0)
    time.sleep(0.12)
    u.mouse_event(0x0004, 0, 0, 0, 0)
    print("click", x, y)
    return 0


def rect():
    pid = current_pid()
    print(find_window(pid) if pid else None)


def kill():
    subprocess.run(["taskkill", "/IM", "game.exe", "/F"], capture_output=True)
    print("killed")


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "start":
        start()
    elif cmd == "shot":
        sys.exit(shot(sys.argv[2]))
    elif cmd == "click":
        sys.exit(click(float(sys.argv[2]), float(sys.argv[3])))
    elif cmd == "rect":
        rect()
    elif cmd == "kill":
        kill()
