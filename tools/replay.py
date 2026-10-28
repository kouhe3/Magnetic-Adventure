#!/usr/bin/env python3
"""重放 recorder_gui.py 录制的 JSONL：按真实时间轴驱动鼠标/键盘，结束后截图 +（可选）模板断言。

支持曲线拖拽：录到的 move 点是 62 Hz 采样，相邻点之间按时间线性插值补齐
（间隔 > 25 ms 或距离 > 3 px 时），让游戏每帧都能采到中间位置——直接跳点会把曲线拉直。

坐标优先用窗口内归一化值 (nx, ny)，窗口移动/缩放不影响重放；没有则退回屏幕坐标 (x, y)。

用法:
  python tools/replay.py work/rec_xxx/events.jsonl [--speed 1.0] [--shot out.png]
                          [--expect ref.png] [--post 3]

输出一行 JSON：events / drift_ms / shot / match / passed。
"""
import ctypes
import ctypes.wintypes as wt
import json
import os
import queue
import sys
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import record as rc  # noqa: E402

u = ctypes.windll.user32
u.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MOUSEEVENTF_LEFTDOWN, MOUSEEVENTF_LEFTUP = 0x0002, 0x0004
MOUSEEVENTF_RIGHTDOWN, MOUSEEVENTF_RIGHTUP = 0x0008, 0x0010
MOUSEEVENTF_WHEEL = 0x0800


def game_window():
    pid = None
    pf = os.path.join(ROOT, "work", "game_pid.txt")
    if os.path.exists(pf):
        try:
            pid = int(open(pf).read().strip())
        except ValueError:
            pid = None
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
    return found[0] if found else None


def screen_xy(ev, rect):
    x0, y0, w, h = rect
    if "nx" in ev and "ny" in ev:
        return int(x0 + ev["nx"] * w), int(y0 + ev["ny"] * h)
    if "x" in ev:
        return int(ev["x"]), int(ev["y"])
    return None


def main():
    if len(sys.argv) < 2:
        print("usage: replay.py <jsonl> [--speed N] [--shot png] [--expect png] [--post s]")
        return 2
    path = sys.argv[1]
    speed, post, expect = 1.0, 3.0, None
    shot = os.path.join(ROOT, "work", "replay_end.png")
    for i, a in enumerate(sys.argv):
        if a == "--speed":
            speed = float(sys.argv[i + 1])
        elif a == "--shot":
            shot = sys.argv[i + 1]
        elif a == "--expect":
            expect = sys.argv[i + 1]
        elif a == "--post":
            post = float(sys.argv[i + 1])

    rect = game_window()
    if not rect:
        print(json.dumps({"ok": False, "error": "game window not found"}))
        return 3

    # 每次点击时抓一帧，跑完和录制的参照帧逐张比对——能指出重放从第几次交互开始跑偏
    outdir = os.path.dirname(os.path.abspath(shot))
    os.makedirs(outdir, exist_ok=True)
    shotq = queue.Queue()
    captured = []

    def _grabber():
        while True:
            item = shotq.get()
            if item is None:
                break
            idx, out = item
            try:
                rc.grab_screen(rect, out)
            except Exception:
                pass
            captured.append((idx, out))

    grab = threading.Thread(target=_grabber, daemon=True)
    grab.start()

    events = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            ev = json.loads(line)
            if ev.get("kind") in ("move", "down", "up", "wheel", "key"):
                events.append(ev)
    events.sort(key=lambda e: e["t"])

    t0 = time.perf_counter()
    pos = None
    drift = 0.0
    click_no = 0

    for ev in events:
        target = ev["t"] / 1000.0 / speed
        wait = target - (time.perf_counter() - t0)
        if wait < 0:
            drift = max(drift, -wait * 1000.0)
            wait = 0.0
        xy = screen_xy(ev, rect)
        kind = ev["kind"]

        if kind == "move" and xy is not None:
            if pos is not None and wait > 0.006:
                # 曲线拖拽：把这一段的等待时间摊成若干中间位置，
                # 游戏每帧 GetCursorPos 才采得到弧线上的点，而不是两个采样点连线。
                steps = min(32, max(2, int(wait / 0.008)))
                sx, sy = pos
                for i in range(1, steps + 1):
                    f = i / steps
                    u.SetCursorPos(int(sx + (xy[0] - sx) * f), int(sy + (xy[1] - sy) * f))
                    time.sleep(wait / steps)
            else:
                if wait:
                    time.sleep(wait)
                u.SetCursorPos(xy[0], xy[1])
            pos = (xy[0], xy[1])
            continue

        if wait:
            time.sleep(wait)
        if kind == "down":
            click_no += 1
            if ev.get("shot"):
                shotq.put((click_no, os.path.join(outdir, f"replay_click_{click_no:02d}.png")))
            if xy:
                u.SetCursorPos(xy[0], xy[1])
                pos = (xy[0], xy[1])
            u.mouse_event(MOUSEEVENTF_RIGHTDOWN if ev.get("button") == "right" else MOUSEEVENTF_LEFTDOWN,
                          0, 0, 0, 0)
        elif kind == "up":
            if xy:
                u.SetCursorPos(xy[0], xy[1])
                pos = (xy[0], xy[1])
            u.mouse_event(MOUSEEVENTF_RIGHTUP if ev.get("button") == "right" else MOUSEEVENTF_LEFTUP,
                          0, 0, 0, 0)
        elif kind == "wheel":
            u.mouse_event(MOUSEEVENTF_WHEEL, 0, 0, int(ev.get("delta", 0)), 0)
        elif kind == "key":
            vk = int(ev["vk"])
            u.keybd_event(vk, 0, 0, 0)
            u.keybd_event(vk, 0, 2, 0)

    time.sleep(post)
    shotq.put(None)
    grab.join(timeout=5)
    ok = rc.grab_screen(rect, shot)
    result = {"ok": True, "events": len(events), "shot": shot,
              "drift_ms": round(drift, 1), "captured": bool(ok)}
    if expect:
        try:
            from tmatch import match  # type: ignore
            r = match(shot, expect)
            score = float(r.get("score", 0.0))
            result.update({"match": round(score, 4), "at": r.get("at"),
                           "passed": bool(score >= 0.8)})
        except Exception as ex:  # noqa: BLE001
            result.update({"match_error": str(ex)})
    # 逐次点击的帧比对
    refs = {}
    n = 0
    for ev in events:
        if ev["kind"] == "down":
            n += 1
            if ev.get("shot"):
                refs[n] = ev["shot"]
    if refs:
        try:
            from tmatch import match  # type: ignore
            pairs = []
            for idx, got in captured:
                ref = refs.get(idx)
                if not ref or not os.path.exists(ref):
                    continue
                sc = float(match(got, ref).get("score", 0.0))
                pairs.append({"click": idx, "score": round(sc, 4),
                              "ref": os.path.basename(ref), "got": os.path.basename(got)})
            if pairs:
                result["clicks"] = pairs
                result["min_score"] = min(p["score"] for p in pairs)
                bad = [p for p in pairs if p["score"] < 0.8]
                result["first_bad"] = bad[0]["click"] if bad else None
        except Exception as ex:  # noqa: BLE001
            result["clicks_error"] = str(ex)

    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
