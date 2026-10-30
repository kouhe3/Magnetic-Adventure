"""帧变化率仪器：定频率抓屏幕上一小块区域，统计"画面真的变了"的频率。

用途：给出宿主/原版在某个界面上的**可见更新率**（帧率上界），用来回答
「渲染是定时器驱动还是按需重绘」。不注入、不挂钩，只用 GDI StretchBlt + DIB。

用法：
    python tools/frame_probe.py --dir work/winprobe_game [--exe game.exe]
        [--region x,y,w,h] [--seconds 3] [--hz 120] [--click fx,fy] [--wait 20]

    --region  屏幕物理像素矩形，取样区；省略则取窗口客户区中央 40%
    --click   在采样前用真实输入点一下窗口（fraction 坐标），用于进关
    --wait    点击后等待秒数

输出：samples / distinct / changes_per_sec / median_interval_ms / p90_interval_ms。
判据：changes_per_sec 接近 --hz 说明持续重绘；为 0 说明画面静止（按需重绘/阻塞）。
覆盖边界：只反映**被采样矩形**的变化；若该区域被其它窗口遮挡，结果无效（会先抢前台）。
"""
import ctypes
import ctypes.wintypes as wt
import os
import statistics
import subprocess
import sys
import time

u = ctypes.windll.user32
g = ctypes.windll.gdi32
k = ctypes.windll.kernel32
u.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))

WNDENUMPROC = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
SRCCOPY = 0x00CC0020
HALFTONE = 4

# 全部显式声明：句柄是 64 位，默认 c_int 会截断（F 系列踩过的同一坑）
g.CreateCompatibleDC.restype = wt.HDC
g.CreateCompatibleDC.argtypes = (wt.HDC,)
g.CreateDIBSection.restype = wt.HBITMAP
g.CreateDIBSection.argtypes = (wt.HDC, ctypes.c_void_p, wt.UINT, ctypes.POINTER(ctypes.c_void_p),
                               wt.HANDLE, wt.DWORD)
g.SelectObject.restype = wt.HGDIOBJ
g.SelectObject.argtypes = (wt.HDC, wt.HGDIOBJ)
g.DeleteDC.argtypes = (wt.HDC,)
g.DeleteObject.argtypes = (wt.HGDIOBJ,)
g.StretchBlt.argtypes = (wt.HDC, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
                         wt.HDC, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, wt.DWORD)
g.SetStretchBltMode.argtypes = (wt.HDC, ctypes.c_int)
u.GetDC.restype = wt.HDC
u.GetDC.argtypes = (wt.HWND,)
u.ReleaseDC.argtypes = (wt.HWND, wt.HDC)


def find_window(pid):
    out = []

    def cb(h, l):
        p = wt.DWORD()
        u.GetWindowThreadProcessId(h, ctypes.byref(p))
        if p.value == pid and u.IsWindowVisible(h):
            n = ctypes.create_unicode_buffer(256)
            u.GetWindowTextW(h, n, 256)
            r = wt.RECT()
            u.GetWindowRect(h, ctypes.byref(r))
            if "Magnetic" in n.value and r.right - r.left > 200:
                out.append((h, r.left, r.top, r.right, r.bottom))
        return True

    u.EnumWindows(WNDENUMPROC(cb), 0)
    return out[0] if out else None


def click(win, fx, fy):
    h, l, t, r, b = win
    u.SetForegroundWindow(h)
    time.sleep(0.3)
    u.SetCursorPos(int(l + (r - l) * fx), int(t + (b - t) * fy))
    time.sleep(0.2)
    u.mouse_event(0x0002, 0, 0, 0, 0)
    time.sleep(0.12)
    u.mouse_event(0x0004, 0, 0, 0, 0)


def make_dib(w, h):
    class BITMAPINFOHEADER(ctypes.Structure):
        _fields_ = [("biSize", wt.DWORD), ("biWidth", wt.LONG), ("biHeight", wt.LONG),
                    ("biPlanes", wt.WORD), ("biBitCount", wt.WORD), ("biCompression", wt.DWORD),
                    ("biSizeImage", wt.DWORD), ("biXPelsPerMeter", wt.LONG),
                    ("biYPelsPerMeter", wt.LONG), ("biClrUsed", wt.DWORD),
                    ("biClrImportant", wt.DWORD)]

    bi = BITMAPINFOHEADER()
    bi.biSize = ctypes.sizeof(bi)
    bi.biWidth = w
    bi.biHeight = -h  # top-down
    bi.biPlanes = 1
    bi.biBitCount = 32
    bi.biCompression = 0
    bits = ctypes.c_void_p()
    g.CreateDIBSection.restype = wt.HBITMAP
    hbm = g.CreateDIBSection(u.GetDC(0), ctypes.byref(bi), 0, ctypes.byref(bits), None, 0)
    return hbm, bits, bi


def sample_frames(region, seconds, hz):
    x, y, w, h = region
    sw, sh = 160, 120
    hbm, bits, bi = make_dib(sw, sh)
    screen = u.GetDC(0)
    memdc = g.CreateCompatibleDC(screen)
    g.SelectObject(memdc, hbm)
    buf = (ctypes.c_ubyte * (sw * sh * 4)).from_address(bits.value)
    period = 1.0 / hz
    prev = None
    changes = []
    n = 0
    t0 = time.perf_counter()
    while time.perf_counter() - t0 < seconds:
        g.SetStretchBltMode(memdc, HALFTONE)
        g.StretchBlt(memdc, 0, 0, sw, sh, screen, x, y, w, h, SRCCOPY)
        cur = bytes(buf)
        n += 1
        if prev is not None and cur != prev:
            changes.append(time.perf_counter() - t_last)
        prev = cur
        t_last = time.perf_counter()
        nxt = t0 + n * period
        while time.perf_counter() < nxt:
            pass
    g.DeleteDC(memdc)
    g.DeleteObject(hbm)
    u.ReleaseDC(0, screen)
    return n, len(changes), changes


def main():
    argv = sys.argv[1:]

    def arg(name, default=None):
        return argv[argv.index(name) + 1] if name in argv else default

    gdir = arg("--dir", r"C:\tmp\Magnetic Adventure\work\winprobe_game")
    exe = arg("--exe", "game.exe")
    seconds = float(arg("--seconds", "3"))
    hz = float(arg("--hz", "120"))
    wait = float(arg("--wait", "22"))
    click_frac = arg("--click")
    region = arg("--region")

    p = subprocess.Popen([os.path.join(gdir, exe)], cwd=gdir)
    print("pid=%d" % p.pid)
    try:
        win = None
        for _ in range(120):
            time.sleep(0.5)
            win = find_window(p.pid)
            if win:
                break
        if not win:
            print("error=no_window")
            return 1
        h, l, t, r, b = win
        print("window=%r" % (win,))
        if region:
            reg = tuple(int(v) for v in region.split(","))
        else:
            cw, ch = r - l, b - t
            reg = (l + int(cw * 0.30), t + int(ch * 0.30), int(cw * 0.40), int(ch * 0.40))
        print("region=%r" % (reg,))

        time.sleep(6)
        u.SetForegroundWindow(win[0])
        time.sleep(1)
        n, c, gaps = sample_frames(reg, seconds, hz)
        print("[menu]   samples=%d distinct_changes=%d changes_per_sec=%.1f" % (n, c, c / seconds))
        if gaps:
            print("         median_interval_ms=%.1f p90=%.1f" % (
                1000 * statistics.median(gaps), 1000 * sorted(gaps)[int(len(gaps) * 0.9)]))

        if click_frac:
            fx, fy = (float(v) for v in click_frac.split(","))
            click(win, fx, fy)
            time.sleep(wait)
        n, c, gaps = sample_frames(reg, seconds, hz)
        print("[scene]  samples=%d distinct_changes=%d changes_per_sec=%.1f" % (n, c, c / seconds))
        if gaps:
            print("         median_interval_ms=%.1f p90=%.1f" % (
                1000 * statistics.median(gaps), 1000 * sorted(gaps)[int(len(gaps) * 0.9)]))
        return 0
    finally:
        subprocess.run(["taskkill", "/PID", str(p.pid), "/F"], capture_output=True)
        print("killed=1")


if __name__ == "__main__":
    sys.exit(main())
