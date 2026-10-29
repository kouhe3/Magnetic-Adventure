#!/usr/bin/env python3
"""常驻游戏驱动（异步命令通道）：从 stdin 读一行命令，执行后回一行 JSON。

命令:
  start [dll_path]       启动 game.exe（可先替换 b2Physics.dll），等待窗口
  shot <png_path>        截游戏窗口（ffmpeg gdigrab 区域抓取）
  click <fx> <fy>        窗口内相对坐标点击（真实光标）
  move <fx> <fy>         只移动光标
  down / up              按下/抬起左键
  key <vk>               发送按键（keybd_event）
  kill                   结束游戏
  quit                   退出驱动
输出: 每行一个 JSON，例如 {"ok":true,"cmd":"shot","path":"..."}
"""
import ctypes
import ctypes.wintypes as wt
import json
import os
import subprocess
import sys
import time

ROOT = r"C:\tmp\Magnetic Adventure"
GAME_DIR = os.path.join(ROOT, "work", "integration")
PID_FILE = os.path.join(ROOT, "work", "game_pid.txt")

u = ctypes.windll.user32
k = ctypes.windll.kernel32
u.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))

WNDENUMPROC = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
proc = None


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


def window():
    if not os.path.exists(PID_FILE):
        return None
    return find_window(int(open(PID_FILE).read().strip()))


def reply(**kw):
    kw.setdefault("ok", True)
    print(json.dumps(kw, ensure_ascii=False), flush=True)


def cmd_start(dll):
    global proc
    child_env = dict(os.environ)
    child_env.pop("B2PHYSICS_LOG", None)
    subprocess.run(["taskkill", "/IM", "game.exe", "/F"], capture_output=True)
    time.sleep(0.6)
    if dll:
        src = dll if os.path.isabs(dll) else os.path.join(ROOT, dll)
        subprocess.run(["cmd", "/c", "copy", "/Y", src, os.path.join(GAME_DIR, "b2Physics.dll")],
                       capture_output=True)
    proc = subprocess.Popen([os.path.join(GAME_DIR, "game.exe")], cwd=GAME_DIR, env=child_env)
    os.makedirs(os.path.dirname(PID_FILE), exist_ok=True)
    open(PID_FILE, "w").write(str(proc.pid))
    end = time.time() + 45
    while time.time() < end:
        w = find_window(proc.pid)
        if w:
            reply(cmd="start", pid=proc.pid, hwnd=w[0], rect=list(w[1:]))
            return
        time.sleep(0.5)
    reply(ok=False, cmd="start", error="window timeout")


def cmd_shot(path):
    w = window()
    if not w:
        reply(ok=False, cmd="shot", error="no window")
        return
    h, l, t, r, b = w
    out = path if os.path.isabs(path) else os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-f", "gdigrab",
                    "-offset_x", str(l), "-offset_y", str(t),
                    "-video_size", f"{r-l}x{b-t}", "-framerate", "1",
                    "-i", "desktop", "-frames:v", "1", "-y", out], check=False)
    reply(cmd="shot", path=out, rect=[l, t, r - l, b - t])


def to_screen(fx, fy):
    w = window()
    if not w:
        return None
    h, l, t, r, b = w
    return int(l + (r - l) * float(fx)), int(t + (b - t) * float(fy))


def cmd_move(fx, fy):
    p = to_screen(fx, fy)
    if not p:
        reply(ok=False, cmd="move", error="no window")
        return
    u.SetCursorPos(*p)
    reply(cmd="move", x=p[0], y=p[1])


def cmd_click(fx, fy):
    p = to_screen(fx, fy)
    if not p:
        reply(ok=False, cmd="click", error="no window")
        return
    u.SetCursorPos(*p)
    time.sleep(0.08)
    u.mouse_event(0x0002, 0, 0, 0, 0)
    time.sleep(0.05)
    u.mouse_event(0x0004, 0, 0, 0, 0)
    reply(cmd="click", x=p[0], y=p[1])


def cmd_key(vk):
    vk = int(vk, 0)
    u.keybd_event(vk, 0, 0, 0)
    time.sleep(0.03)
    u.keybd_event(vk, 0, 2, 0)
    reply(cmd="key", vk=vk)


def main():
    reply(ready=True, game_dir=GAME_DIR)
    for line in sys.stdin:
        parts = line.strip().split()
        if not parts:
            continue
        c = parts[0]
        try:
            if c == "start":
                cmd_start(parts[1] if len(parts) > 1 else None)
            elif c == "shot":
                cmd_shot(parts[1] if len(parts) > 1 else "work/shot.png")
            elif c == "click":
                cmd_click(parts[1], parts[2])
            elif c == "move":
                cmd_move(parts[1], parts[2])
            elif c == "down":
                u.mouse_event(0x0002, 0, 0, 0, 0)
                reply(cmd="down")
            elif c == "up":
                u.mouse_event(0x0004, 0, 0, 0, 0)
                reply(cmd="up")
            elif c == "key":
                cmd_key(parts[1])
            elif c == "kill":
                subprocess.run(["taskkill", "/IM", "game.exe", "/F"], capture_output=True)
                reply(cmd="kill")
            elif c == "quit":
                reply(cmd="quit")
                break
            else:
                reply(ok=False, error=f"unknown {c}")
        except Exception as ex:  # noqa: BLE001
            reply(ok=False, cmd=c, error=str(ex))


if __name__ == "__main__":
    main()
