#!/usr/bin/env python3
"""录制鼠标/键盘操作到 JSONL（含窗口内归一化坐标），供 replay.py 重放。

用法:
  python tools/record.py work/rec_level1.jsonl [--seconds 60]

停止: 按 ESC（或到达 --seconds）。
每行: {"t": ms, "kind": "move|down|up|wheel|key", "x","y", "nx","ny", "button", "vk"}
"""
import ctypes
import ctypes.wintypes as wt
import json
import os
import sys
import time

from PIL import Image

u = ctypes.windll.user32
u.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))

WH_MOUSE_LL = 14
WH_KEYBOARD_LL = 13
WM_MOUSEMOVE, WM_LBUTTONDOWN, WM_LBUTTONUP = 0x0200, 0x0201, 0x0202
WM_RBUTTONDOWN, WM_RBUTTONUP, WM_MOUSEWHEEL = 0x0204, 0x0205, 0x020A
WM_KEYDOWN, WM_SYSKEYDOWN = 0x0100, 0x0104
VK_ESCAPE = 0x1B

LRESULT = ctypes.c_ssize_t
HOOKPROC = ctypes.WINFUNCTYPE(LRESULT, ctypes.c_int, wt.WPARAM, wt.LPARAM)


class MSLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [("pt", wt.POINT), ("mouseData", wt.DWORD), ("flags", wt.DWORD),
                ("time", wt.DWORD), ("dwExtraInfo", ctypes.c_void_p)]


class KBDLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [("vkCode", wt.DWORD), ("scanCode", wt.DWORD), ("flags", wt.DWORD),
                ("time", wt.DWORD), ("dwExtraInfo", ctypes.c_void_p)]


class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [("biSize", wt.DWORD), ("biWidth", wt.LONG), ("biHeight", wt.LONG),
                ("biPlanes", wt.WORD), ("biBitCount", wt.WORD), ("biCompression", wt.DWORD),
                ("biSizeImage", wt.DWORD), ("biXPelsPerMeter", wt.LONG), ("biYPelsPerMeter", wt.LONG),
                ("biClrUsed", wt.DWORD), ("biClrImportant", wt.DWORD)]


def grab_window(hwnd, path):
    gdi = ctypes.windll.gdi32
    r = wt.RECT()
    u.GetClientRect(hwnd, ctypes.byref(r))
    w, h = r.right, r.bottom
    if w <= 0 or h <= 0:
        return None
    hdc = u.GetDC(hwnd)
    mem = gdi.CreateCompatibleDC(hdc)
    bmp = gdi.CreateCompatibleBitmap(hdc, w, h)
    gdi.SelectObject(mem, bmp)
    gdi.BitBlt(mem, 0, 0, w, h, hdc, 0, 0, 0x00CC0020)
    bi = BITMAPINFOHEADER()
    bi.biSize = ctypes.sizeof(BITMAPINFOHEADER)
    bi.biWidth = w
    bi.biHeight = -h
    bi.biPlanes = 1
    bi.biBitCount = 32
    buf = ctypes.create_string_buffer(w * h * 4)
    gdi.GetDIBits(mem, bmp, 0, h, buf, ctypes.byref(bi), 0)
    gdi.DeleteObject(bmp)
    gdi.DeleteDC(mem)
    u.ReleaseDC(hwnd, hdc)
    img = Image.frombuffer("RGBA", (w, h), buf, "raw", "BGRA", 0, 1).convert("RGB")
    img.save(path)
    return path


def game_hwnd():
    pid = None
    pid_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            "work", "game_pid.txt")
    if os.path.exists(pid_file):
        pid = int(open(pid_file).read().strip())
    found = []

    def cb(h, l):
        p = wt.DWORD()
        u.GetWindowThreadProcessId(h, ctypes.byref(p))
        if (pid is None or p.value == pid) and u.IsWindowVisible(h):
            n = ctypes.create_unicode_buffer(256)
            u.GetWindowTextW(h, n, 256)
            r = wt.RECT()
            u.GetWindowRect(h, ctypes.byref(r))
            if "Magnetic" in n.value and r.right - r.left > 100:
                found.append(h)
        return True

    CB = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
    u.EnumWindows(CB(cb), 0)
    return found[0] if found else None


def game_window():
    pid = None
    pid_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            "work", "game_pid.txt")
    if os.path.exists(pid_file):
        pid = int(open(pid_file).read().strip())
    found = []

    def cb(h, l):
        p = wt.DWORD()
        u.GetWindowThreadProcessId(h, ctypes.byref(p))
        if (pid is None or p.value == pid) and u.IsWindowVisible(h):
            r = wt.RECT()
            u.GetWindowRect(h, ctypes.byref(r))
            n = ctypes.create_unicode_buffer(256)
            u.GetWindowTextW(h, n, 256)
            if "Magnetic" in n.value and r.right - r.left > 100:
                found.append((r.left, r.top, r.right - r.left, r.bottom - r.top))
        return True

    CB = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
    u.EnumWindows(CB(cb), 0)
    return found[0] if found else (0, 0, u.GetSystemMetrics(0), u.GetSystemMetrics(1))


def main():
    out_path = sys.argv[1] if len(sys.argv) > 1 else "work/rec.jsonl"
    seconds = 60
    if "--seconds" in sys.argv:
        seconds = int(sys.argv[sys.argv.index("--seconds") + 1])
    shots_dir = None
    interval = 0.5
    if "--shots" in sys.argv:
        shots_dir = sys.argv[sys.argv.index("--shots") + 1]
        os.makedirs(shots_dir, exist_ok=True)
    if "--interval" in sys.argv:
        interval = float(sys.argv[sys.argv.index("--interval") + 1])
    next_frame = [0.0]
    frame_no = [0]
    hwnd = [game_hwnd()]
    win = game_window()
    f = open(out_path, "w", encoding="utf-8")
    start = time.time()
    state = {"stop": False}
    last_move = [0.0]

    def norm(x, y):
        return round((x - win[0]) / max(1, win[2]), 4), round((y - win[1]) / max(1, win[3]), 4)

    def maybe_frame():
        if not shots_dir or not hwnd[0]:
            return
        now = time.time()
        if now < next_frame[0]:
            return
        next_frame[0] = now + interval
        name = os.path.join(shots_dir, f"frame_{frame_no[0]:06d}.png")
        try:
            if grab_window(hwnd[0], name):
                emit("frame", path=name, n=frame_no[0])
                frame_no[0] += 1
        except Exception:
            pass

    def emit(kind, x=None, y=None, **kw):
        rec = {"t": int((time.time() - start) * 1000), "kind": kind}
        if x is not None:
            rec["x"], rec["y"] = x, y
            rec["nx"], rec["ny"] = norm(x, y)
        rec.update(kw)
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        f.flush()

    def mouse_proc(code, wparam, lparam):
        if code >= 0:
            ms = ctypes.cast(lparam, ctypes.POINTER(MSLLHOOKSTRUCT)).contents
            x, y = ms.pt.x, ms.pt.y
            if wparam == WM_MOUSEMOVE:
                now = time.time()
                if now - last_move[0] >= 0.02:
                    last_move[0] = now
                    emit("move", x, y)
            elif wparam in (WM_LBUTTONDOWN, WM_RBUTTONDOWN):
                emit("down", x, y, button="left" if wparam == WM_LBUTTONDOWN else "right")
            elif wparam in (WM_LBUTTONUP, WM_RBUTTONUP):
                emit("up", x, y, button="left" if wparam == WM_LBUTTONUP else "right")
            elif wparam == WM_MOUSEWHEEL:
                delta = (ms.mouseData >> 16) & 0xFFFF
                emit("wheel", x, y, delta=delta if delta < 0x8000 else delta - 0x10000)
        return u.CallNextHookEx(None, code, wparam, lparam)

    def key_proc(code, wparam, lparam):
        if code >= 0:
            kb = ctypes.cast(lparam, ctypes.POINTER(KBDLLHOOKSTRUCT)).contents
            if wparam in (WM_KEYDOWN, WM_SYSKEYDOWN):
                if kb.vkCode == VK_ESCAPE:
                    state["stop"] = True
                else:
                    emit("key", vk=int(kb.vkCode))
        return u.CallNextHookEx(None, code, wparam, lparam)

    mouse_cb = HOOKPROC(mouse_proc)
    key_cb = HOOKPROC(key_proc)
    hm = u.SetWindowsHookExW(WH_MOUSE_LL, mouse_cb, None, 0)
    hk = u.SetWindowsHookExW(WH_KEYBOARD_LL, key_cb, None, 0)
    print(json.dumps({"recording": out_path, "window": win, "hint": "ESC 停止"}, ensure_ascii=False),
          flush=True)

    msg = wt.MSG()
    while not state["stop"] and (time.time() - start) < seconds:
        while u.PeekMessageW(ctypes.byref(msg), None, 0, 0, 1):
            u.TranslateMessage(ctypes.byref(msg))
            u.DispatchMessageW(ctypes.byref(msg))
        maybe_frame()
        time.sleep(0.005)
    u.UnhookWindowsHookEx(hm)
    u.UnhookWindowsHookEx(hk)
    f.close()
    print(json.dumps({"done": out_path, "seconds": round(time.time() - start, 2)}, ensure_ascii=False),
          flush=True)


if __name__ == "__main__":
    main()
