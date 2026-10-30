"""模板定位（无 OpenCV）：在截图上找一个小模板的位置，用于"点对话气泡的 X"这类操作。

为什么自己写：本机没有 cv2 / scipy，而 numpy 的 FFT 足够做归一化互相关（NCC）。
判据：score = NCC ∈ [-1,1]，>0.7 视为命中；低于阈值返回 None，不猜。

用法：
    python tools/uitemplate.py --selftest                       # 仪器自证（粘一个模板到已知位置）
    python tools/uitemplate.py --image work/now.png --template work/templates/close_x.png
    python tools/uitemplate.py --live --template work/templates/close_x.png   # 抓游戏客户区并定位

`--live` 输出模板中心在**屏幕物理像素**上的坐标（可直接 SetCursorPos 点击）。
覆盖边界：模板与目标必须同尺度（同一缩放/分辨率）；换缩放后要重新抠模板。
"""
import argparse
import ctypes
import ctypes.wintypes as wt
import json
import sys

import numpy as np
from PIL import Image
from numpy.fft import rfft2, irfft2

u = ctypes.windll.user32
g = ctypes.windll.gdi32
u.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
WNDENUMPROC = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
SRCCOPY = 0x00CC0020

g.CreateCompatibleDC.restype = wt.HDC
g.CreateCompatibleDC.argtypes = (wt.HDC,)
g.CreateDIBSection.restype = wt.HBITMAP
g.CreateDIBSection.argtypes = (wt.HDC, ctypes.c_void_p, wt.UINT, ctypes.POINTER(ctypes.c_void_p),
                               wt.HANDLE, wt.DWORD)
g.SelectObject.restype = wt.HGDIOBJ
g.SelectObject.argtypes = (wt.HDC, wt.HGDIOBJ)
g.BitBlt.argtypes = (wt.HDC, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
                     wt.HDC, ctypes.c_int, ctypes.c_int, wt.DWORD)
g.DeleteDC.argtypes = (wt.HDC,)
g.DeleteObject.argtypes = (wt.HGDIOBJ,)
u.GetDC.restype = wt.HDC
u.GetDC.argtypes = (wt.HWND,)
u.ReleaseDC.argtypes = (wt.HWND, wt.HDC)


def to_gray(img):
    a = np.asarray(img.convert("RGB"), dtype=np.float32)
    return a.mean(axis=2)


def ncc_match(img, tpl):
    """返回 (x, y, score)：模板左上角在 img 中的位置。"""
    img = img.astype(np.float64)
    H, W = img.shape
    h, w = tpl.shape
    if h > H or w > W:
        raise ValueError("template larger than image")
    t = tpl.astype(np.float64) - float(tpl.mean())
    t_energy = float((t ** 2).sum())
    if t_energy <= 1e-6:
        raise ValueError("degenerate template")

    # 相关 = 与翻转核做卷积；必须按 (H+h-1, W+w-1) 做线性卷积再加窗取有效区，
    # 否则环形卷积会绕回来（自检就是这个报出来的：score=-9.2）。
    def conv_valid(a, k):
        fh, fw = H + h - 1, W + w - 1
        full = irfft2(rfft2(a, (fh, fw)) * rfft2(k, (fh, fw)), (fh, fw))
        return full[h - 1:H, w - 1:W]

    corr = conv_valid(img, t[::-1, ::-1])
    ones = np.ones((h, w), np.float32)
    s1 = conv_valid(img, ones)
    s2 = conv_valid(img ** 2, ones)

    N = h * w
    # t 已经零均值 ⇒ Σ(I-Ibar)(T-Tbar) = Σ I·t，不需要再减 s1*mean
    num = corr
    # 局部方差用 float64 算；平坦窗口方差≈0 时 NCC 无定义 ⇒ 直接记 0（否则会炸出 20+ 的假分数）
    var = s2 - s1 ** 2 / N
    flat = var < 25.0
    den = np.sqrt(np.maximum(var, 25.0) * t_energy)
    ncc = np.where(flat, 0.0, num / den)
    ncc = np.clip(ncc, -1.0, 1.0)
    iy, ix = np.unravel_index(int(np.argmax(ncc)), ncc.shape)
    return int(ix), int(iy), float(ncc[iy, ix])


def find_window():
    out = []

    def cb(h, l):
        p = wt.DWORD()
        u.GetWindowThreadProcessId(h, ctypes.byref(p))
        n = ctypes.create_unicode_buffer(256)
        u.GetWindowTextW(h, n, 256)
        r = wt.RECT()
        u.GetWindowRect(h, ctypes.byref(r))
        if "Magnetic" in n.value and u.IsWindowVisible(h) and r.right - r.left > 200:
            out.append((h, r.left, r.top, r.right, r.bottom))
        return True

    u.EnumWindows(WNDENUMPROC(cb), 0)
    return out[0] if out else None


def grab_client(win):
    """1:1 抓客户区，返回 (PIL.Image, 客户区屏幕原点)。"""
    h, l, t, r, b = win
    cr = wt.RECT()
    u.GetClientRect(h, ctypes.byref(cr))
    pt = wt.POINT(0, 0)
    u.ClientToScreen(h, ctypes.byref(pt))
    w, hh = cr.right, cr.bottom
    class BIH(ctypes.Structure):
        _fields_ = [("biSize", wt.DWORD), ("biWidth", wt.LONG), ("biHeight", wt.LONG),
                    ("biPlanes", wt.WORD), ("biBitCount", wt.WORD), ("biCompression", wt.DWORD),
                    ("biSizeImage", wt.DWORD), ("biXPelsPerMeter", wt.LONG),
                    ("biYPelsPerMeter", wt.LONG), ("biClrUsed", wt.DWORD),
                    ("biClrImportant", wt.DWORD)]
    bi = BIH()
    bi.biSize = ctypes.sizeof(bi)
    bi.biWidth = w
    bi.biHeight = -hh
    bi.biPlanes = 1
    bi.biBitCount = 32
    bits = ctypes.c_void_p()
    screen = u.GetDC(0)
    hbm = g.CreateDIBSection(screen, ctypes.byref(bi), 0, ctypes.byref(bits), None, 0)
    memdc = g.CreateCompatibleDC(screen)
    g.SelectObject(memdc, hbm)
    g.BitBlt(memdc, 0, 0, w, hh, screen, pt.x, pt.y, SRCCOPY)
    buf = (ctypes.c_ubyte * (w * hh * 4)).from_address(bits.value)
    arr = np.frombuffer(bytes(buf), dtype=np.uint8).reshape(hh, w, 4)[:, :, :3]
    g.DeleteDC(memdc)
    g.DeleteObject(hbm)
    u.ReleaseDC(0, screen)
    return Image.fromarray(arr), (pt.x, pt.y)


def selftest(tpl_path):
    tpl = to_gray(Image.open(tpl_path))
    h, w = tpl.shape
    img = np.full((400, 500), 128, np.float32)
    img[123:123 + h, 210:210 + w] = tpl
    img += np.random.default_rng(0).normal(0, 2.0, img.shape).astype(np.float32)
    x, y, score = ncc_match(img, tpl)
    ok = abs(x - 210) <= 1 and abs(y - 123) <= 1 and score > 0.9
    print("selftest=%s got=(%d,%d) expect=(210,123) score=%.3f" % ("PASS" if ok else "FAIL", x, y, score))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--template", default=r"work\templates\close_x.png")
    ap.add_argument("--image")
    ap.add_argument("--live", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--threshold", type=float, default=0.7)
    args = ap.parse_args()

    if args.selftest:
        return selftest(args.template)

    tpl = to_gray(Image.open(args.template))
    if args.image:
        img = to_gray(Image.open(args.image))
        x, y, score = ncc_match(img, tpl)
        print(json.dumps({"x": x, "y": y, "score": round(score, 3),
                          "hit": score >= args.threshold}))
        return 0

    if args.live:
        win = find_window()
        if not win:
            print("error=no_window")
            return 2
        img, (ox, oy) = grab_client(win)
        x, y, score = ncc_match(to_gray(img), tpl)
        cx, cy = ox + x + tpl.shape[1] // 2, oy + y + tpl.shape[0] // 2
        print(json.dumps({"client_x": x, "client_y": y, "screen_x": cx, "screen_y": cy,
                          "score": round(score, 3), "hit": score >= args.threshold}))
        return 0 if score >= args.threshold else 1

    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main())
