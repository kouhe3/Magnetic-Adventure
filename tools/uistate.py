"""界面状态识别：把「游戏现在在 intro / 加载 / 主菜单 / 地图 / 关卡」变成机器判据。

为什么需要：自动化最大的坑不是点不动，而是**不知道点到了哪一屏**——定时点击会把 intro 当主菜单
（本项目实测过）。本工具用「同状态多帧建参考 → 只在高判别力像素上比差」的方式做状态机，并且
**不确定时返回 unknown**，不猜。

用法（四步，全部无人在环）：
  1) 采集      python tools/uistate.py capture --dir work/winprobe_game --out work/states --seconds 45
  2) 标注      python tools/uistate.py label --frames work/states --state intro:0-14 menu:16-30
  3) 建参考    python tools/uistate.py build --frames work/states --out work/uianchors.npz
  4) 判定/等待  python tools/uistate.py wait --dir work/winprobe_game --anchors work/uianchors.npz --state menu --timeout 40

判定口径（`detect` 打印 state/score/margin）：
  score  = 掩码像素上的平均绝对差（0–255，越小越像）
  margin = 次优 score / 最优 score；margin < 1.25 或 score > 25 判 unknown。

覆盖边界：只在**窗口客户区**上比对（尺寸固定 1018×739，物理 1.5×），与分辨率/缩放绑定；
换显示器缩放或窗口尺寸后必须重新 capture+build。动画区域靠"帧间方差"自动排除。
"""
import argparse
import ctypes
import ctypes.wintypes as wt
import json
import os
import subprocess
import sys
import time

import numpy as np
from PIL import Image

u = ctypes.windll.user32
g = ctypes.windll.gdi32
k = ctypes.windll.kernel32
u.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))

WNDENUMPROC = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
SRCCOPY = 0x00CC0020
HALFTONE = 4
SIZE = (320, 240)          # 比对分辨率
SCORE_MAX = 25.0
MARGIN_MIN = 1.25

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
k.OpenProcess.restype = wt.HANDLE
k.OpenProcess.argtypes = (wt.DWORD, wt.BOOL, wt.DWORD)
k.GetProcessTimes.argtypes = (wt.HANDLE, ctypes.POINTER(wt.FILETIME), ctypes.POINTER(wt.FILETIME),
                              ctypes.POINTER(wt.FILETIME), ctypes.POINTER(wt.FILETIME))


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


def client_rect(win):
    h, l, t, r, b = win
    cr = wt.RECT()
    u.GetClientRect(h, ctypes.byref(cr))
    pt = wt.POINT(0, 0)
    u.ClientToScreen(h, ctypes.byref(pt))
    return (pt.x, pt.y, cr.right, cr.bottom)


class _Graber:
    def __init__(self):
        self.sw, self.sh = SIZE
        class BIH(ctypes.Structure):
            _fields_ = [("biSize", wt.DWORD), ("biWidth", wt.LONG), ("biHeight", wt.LONG),
                        ("biPlanes", wt.WORD), ("biBitCount", wt.WORD), ("biCompression", wt.DWORD),
                        ("biSizeImage", wt.DWORD), ("biXPelsPerMeter", wt.LONG),
                        ("biYPelsPerMeter", wt.LONG), ("biClrUsed", wt.DWORD),
                        ("biClrImportant", wt.DWORD)]
        bi = BIH()
        bi.biSize = ctypes.sizeof(bi)
        bi.biWidth = self.sw
        bi.biHeight = -self.sh
        bi.biPlanes = 1
        bi.biBitCount = 32
        bits = ctypes.c_void_p()
        self.screen = u.GetDC(0)
        self.hbm = g.CreateDIBSection(self.screen, ctypes.byref(bi), 0, ctypes.byref(bits), None, 0)
        self.memdc = g.CreateCompatibleDC(self.screen)
        g.SelectObject(self.memdc, self.hbm)
        self.buf = (ctypes.c_ubyte * (self.sw * self.sh * 4)).from_address(bits.value)
        g.SetStretchBltMode(self.memdc, HALFTONE)

    def grab(self, rect):
        x, y, w, h = rect
        g.StretchBlt(self.memdc, 0, 0, self.sw, self.sh, self.screen, x, y, w, h, SRCCOPY)
        arr = np.frombuffer(bytes(self.buf), dtype=np.uint8).reshape(self.sh, self.sw, 4)
        return arr[:, :, :3].mean(axis=2).astype(np.uint8)

    def close(self):
        g.DeleteDC(self.memdc)
        g.DeleteObject(self.hbm)
        u.ReleaseDC(0, self.screen)


def cpu_seconds(pid):
    h = k.OpenProcess(0x1000, False, pid)
    if not h:
        return 0.0
    a, b, c, d = wt.FILETIME(), wt.FILETIME(), wt.FILETIME(), wt.FILETIME()
    k.GetProcessTimes(h, ctypes.byref(a), ctypes.byref(b), ctypes.byref(c), ctypes.byref(d))
    k.CloseHandle(h)

    def ft(f):
        return (f.dwHighDateTime << 32) | f.dwLowDateTime
    return (ft(c) + ft(d)) / 1e7


def cmd_capture(args):
    p = subprocess.Popen([os.path.join(args.dir, args.exe)], cwd=args.dir)
    clicks = []
    for spec in getattr(args, "click_at", None) or []:
        t_str, frac = spec.split(":", 1)
        fx, fy = (float(v) for v in frac.split(","))
        clicks.append((float(t_str), fx, fy))
    clicks.sort()
    keys = []
    for spec in getattr(args, "key_at", None) or []:
        t_str, vk = spec.split(":", 1)
        keys.append((float(t_str), int(vk, 0)))
    keys.sort()
    print("pid=%d" % p.pid)
    os.makedirs(args.out, exist_ok=True)
    meta = open(os.path.join(args.out, "meta.jsonl"), "w", encoding="utf-8")
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
        rect = client_rect(win)
        print("client_rect=%r" % (rect,))
        gr = _Graber()
        t0 = time.time()
        c0 = cpu_seconds(p.pid)
        i = 0
        nxt = t0
        while time.time() - t0 < args.seconds:
            now = time.time() - t0
            while clicks and now >= clicks[0][0]:
                _, fx, fy = clicks.pop(0)
                # 与 tools/click_play.py 同一套（已证）：SW_RESTORE + 前台 + 150 ms 按住
                u.ShowWindow(win[0], 9)
                u.SetForegroundWindow(win[0])
                time.sleep(0.3)
                u.SetCursorPos(int(rect[0] + rect[2] * fx), int(rect[1] + rect[3] * fy))
                time.sleep(0.2)
                u.mouse_event(0x0002, 0, 0, 0, 0)
                time.sleep(0.15)
                u.mouse_event(0x0004, 0, 0, 0, 0)
                time.sleep(0.2)
                print("click at t=%.1f -> %s fg=%d" % (now, (fx, fy), u.GetForegroundWindow() == win[0]))
            while keys and now >= keys[0][0]:
                _, vk = keys.pop(0)
                u.SetForegroundWindow(win[0])
                time.sleep(0.15)
                u.keybd_event(vk, 0, 0, 0)
                time.sleep(0.08)
                u.keybd_event(vk, 0, 2, 0)
                print("key at t=%.1f -> vk=0x%02X" % (now, vk))
            img = gr.grab(rect)
            t = time.time() - t0
            cpu = cpu_seconds(p.pid) - c0
            name = "f%04d.png" % i
            Image.fromarray(img).save(os.path.join(args.out, name))
            meta.write(json.dumps({"i": i, "t": round(t, 3), "cpu_s": round(cpu, 3),
                                   "file": name}) + "\n")
            meta.flush()
            i += 1
            nxt += args.every
            while time.time() < nxt:
                time.sleep(0.002)
        gr.close()
        print("frames=%d dir=%s" % (i, args.out))
        return 0
    finally:
        subprocess.run(["taskkill", "/PID", str(p.pid), "/F"], capture_output=True)
        print("killed=1")


def load_meta(frames):
    rows = []
    with open(os.path.join(frames, "meta.jsonl"), encoding="utf-8") as f:
        for line in f:
            rows.append(json.loads(line))
    return rows


def cmd_label(args):
    rows = load_meta(args.frames)
    labels = {}
    for spec in args.state:
        name, rng = spec.split(":")
        lo, hi = (float(v) for v in rng.split("-"))
        for r in rows:
            if lo <= r["t"] < hi:
                labels[r["file"]] = name
    with open(os.path.join(args.frames, "labels.json"), "w", encoding="utf-8") as f:
        json.dump(labels, f, ensure_ascii=False, indent=1)
    from collections import Counter
    print(Counter(labels.values()))
    return 0


def cmd_build(args):
    rows = load_meta(args.frames)
    labels = json.load(open(os.path.join(args.frames, "labels.json"), encoding="utf-8"))
    by_state = {}
    for r in rows:
        st = labels.get(r["file"])
        if not st:
            continue
        img = np.asarray(Image.open(os.path.join(args.frames, r["file"])), dtype=np.float32)
        by_state.setdefault(st, []).append(img)
    if len(by_state) < 2:
        print("error=need>=2 states, got %r" % list(by_state))
        return 1

    means, stds = {}, {}
    for st, imgs in by_state.items():
        a = np.stack(imgs)
        means[st] = a.mean(axis=0)
        stds[st] = a.std(axis=0)
    states = sorted(means)
    within = np.max(np.stack([stds[s] for s in states]), axis=0)          # 状态内最大波动
    between = np.stack([means[s] for s in states]).std(axis=0)            # 状态间差异
    # 判别力 = 状态间差异 / 状态内波动；取最靠前的百分位（绝对阈值只作下限）。
    # 固定阈值在不同采集上会全灭（intro 内部本身就有多个画面），所以按分布取。
    score = between / (within + 1.0)
    thr = max(float(np.percentile(score, args.percentile)), args.min_score)
    mask = score >= thr
    if mask.sum() < 200:
        k = min(2000, score.size)
        idx = np.argpartition(score.ravel(), -k)[-k:]
        mask = np.zeros(score.size, dtype=bool)
        mask.ravel()[idx] = True
        print("warn=mask_by_ratio_topk(%d)" % mask.sum())
    np.savez(args.out,
             states=np.array(states),
             refs=np.stack([means[s] for s in states]).astype(np.float32),
             mask=mask.reshape(next(iter(means.values())).shape))
    print("anchors=%s states=%s mask_px=%d/%.0f (%.1f%%) thr=%.2f" % (
        args.out, states, mask.sum(), mask.size, 100.0 * mask.sum() / mask.size, thr))
    return 0


def classify(anchors, img):
    refs = anchors["refs"]
    mask = anchors["mask"].astype(bool).reshape(img.shape)
    states = [str(s) for s in anchors["states"]]
    scores = [float(np.abs(refs[i][mask] - img[mask]).mean()) for i in range(len(states))]
    order = np.argsort(scores)
    best, second = order[0], order[1]
    margin = scores[second] / max(scores[best], 1e-6)
    state = states[best]
    if scores[best] > SCORE_MAX or margin < MARGIN_MIN:
        state = "unknown"
    return state, scores[best], margin, dict(zip(states, [round(s, 1) for s in scores]))


def _state_from_win(anchors, win):
    gr = _Graber()
    try:
        return classify(anchors, gr.grab(client_rect(win)))
    finally:
        gr.close()


def cmd_detect(args):
    anchors = np.load(args.anchors, allow_pickle=False)
    p = subprocess.Popen([os.path.join(args.dir, args.exe)], cwd=args.dir)
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
        for _ in range(args.repeat):
            st, score, margin, allsc = _state_from_win(anchors, win)
            print("state=%-8s score=%.1f margin=%.2f %r" % (st, score, margin, allsc))
            time.sleep(args.every)
        return 0
    finally:
        subprocess.run(["taskkill", "/PID", str(p.pid), "/F"], capture_output=True)


def cmd_wait(args):
    anchors = np.load(args.anchors, allow_pickle=False)
    p = subprocess.Popen([os.path.join(args.dir, args.exe)], cwd=args.dir)
    print("pid=%d want=%s" % (p.pid, args.state))
    t0 = time.time()
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
        while time.time() - t0 < args.timeout:
            st, score, margin, allsc = _state_from_win(anchors, win)
            print("t=%.1f state=%-8s score=%.1f margin=%.2f" % (time.time() - t0, st, score, margin))
            if st == args.state:
                print("reached=%s after %.1fs" % (args.state, time.time() - t0))
                return 0
            time.sleep(args.every)
        print("timeout=%.1fs last=%s" % (args.timeout, st))
        return 1
    finally:
        subprocess.run(["taskkill", "/PID", str(p.pid), "/F"], capture_output=True)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("capture")
    c.add_argument("--dir", default=r"C:\tmp\Magnetic Adventure\work\winprobe_game")
    c.add_argument("--exe", default="game.exe")
    c.add_argument("--out", required=True)
    c.add_argument("--seconds", type=float, default=45)
    c.add_argument("--every", type=float, default=0.4)
    c.add_argument("--click-at", nargs="*", default=None,
                   help="t:fx,fy —— 采集途中按真实输入点一下（如 20:0.35,0.41 进关）")
    c.add_argument("--key-at", action="append", default=[],
                   help="t:vk —— 采集途中向前台窗口发按键（ESC=27，可重复）")
    c.set_defaults(func=cmd_capture)

    lb = sub.add_parser("label")
    lb.add_argument("--frames", required=True)
    lb.add_argument("--state", nargs="+", required=True, help="name:lo-hi（秒）")
    lb.set_defaults(func=cmd_label)

    b = sub.add_parser("build")
    b.add_argument("--frames", required=True)
    b.add_argument("--out", required=True)
    b.add_argument("--percentile", type=float, default=92.0,
                   help="按判别力取前百分之多少的像素作为掩码")
    b.add_argument("--min-score", type=float, default=2.0,
                   help="判别力下限（between/(within+1)）")
    b.set_defaults(func=cmd_build)

    d = sub.add_parser("detect")
    d.add_argument("--dir", default=r"C:\tmp\Magnetic Adventure\work\winprobe_game")
    d.add_argument("--exe", default="game.exe")
    d.add_argument("--anchors", required=True)
    d.add_argument("--repeat", type=int, default=5)
    d.add_argument("--every", type=float, default=2.0)
    d.set_defaults(func=cmd_detect)

    w = sub.add_parser("wait")
    w.add_argument("--dir", default=r"C:\tmp\Magnetic Adventure\work\winprobe_game")
    w.add_argument("--exe", default="game.exe")
    w.add_argument("--anchors", required=True)
    w.add_argument("--state", required=True)
    w.add_argument("--timeout", type=float, default=60)
    w.add_argument("--every", type=float, default=0.5)
    w.set_defaults(func=cmd_wait)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
