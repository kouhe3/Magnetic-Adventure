#!/usr/bin/env python3
"""重放 record.py 录制的 JSONL，并在结束后截图 +（可选）模板断言。

用法:
  python tools/replay.py work/rec_level1.jsonl [--speed 1.0] [--shot work/replay_end.png]
                          [--expect work/level_complete.png] [--post 3]

坐标按录制时的窗口内归一化值映射到当前游戏窗口，窗口移动/缩放不影响重放。
"""
import ctypes
import ctypes.wintypes as wt
import json
import os
import subprocess
import sys
import time

u = ctypes.windll.user32
u.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def game_window():
    pid = None
    pf = os.path.join(ROOT, "work", "game_pid.txt")
    if os.path.exists(pf):
        pid = int(open(pf).read().strip())
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


def main():
    if len(sys.argv) < 2:
        print("usage: replay.py <jsonl> [--speed N] [--shot png] [--expect png] [--post s]")
        return 2
    rec_path = sys.argv[1]
    speed = 1.0
    shot = os.path.join(ROOT, "work", "replay_end.png")
    expect = None
    post = 3.0
    for i, a in enumerate(sys.argv):
        if a == "--speed":
            speed = float(sys.argv[i + 1])
        elif a == "--shot":
            shot = sys.argv[i + 1]
        elif a == "--expect":
            expect = sys.argv[i + 1]
        elif a == "--post":
            post = float(sys.argv[i + 1])

    win = game_window()
    if not win:
        print(json.dumps({"ok": False, "error": "game window not found"}))
        return 3
    x0, y0, w, h = win
    events = [json.loads(line) for line in open(rec_path, encoding="utf-8") if line.strip()]
    print(json.dumps({"events": len(events), "window": win, "speed": speed}))

    start = time.time()
    for e in events:
        target = e["t"] / 1000.0 / speed
        dt = target - (time.time() - start)
        if dt > 0:
            time.sleep(dt)
        if "nx" in e:
            sx = int(x0 + e["nx"] * w)
            sy = int(y0 + e["ny"] * h)
            u.SetCursorPos(sx, sy)
        kind = e["kind"]
        if kind == "down":
            u.mouse_event(0x0002 if e.get("button") != "right" else 0x0008, 0, 0, 0, 0)
        elif kind == "up":
            u.mouse_event(0x0004 if e.get("button") != "right" else 0x0010, 0, 0, 0, 0)
        elif kind == "wheel":
            u.mouse_event(0x0800, 0, 0, e.get("delta", 0), 0)
        elif kind == "key":
            vk = int(e["vk"])
            u.keybd_event(vk, 0, 0, 0)
            u.keybd_event(vk, 0, 2, 0)

    time.sleep(post)
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-f", "gdigrab",
                    "-offset_x", str(x0), "-offset_y", str(y0),
                    "-video_size", f"{w}x{h}", "-framerate", "1", "-i", "desktop",
                    "-frames:v", "1", "-y", shot], check=False)
    result = {"ok": True, "shot": shot}
    if expect:
        try:
            import cv2  # type: ignore
            img = cv2.imread(shot)
            tpl = cv2.imread(expect)
            res = cv2.matchTemplate(img, tpl, cv2.TM_CCOEFF_NORMED)
            _, maxv, _, maxloc = cv2.minMaxLoc(res)
            result.update({"match": round(float(maxv), 4), "at": list(maxloc),
                           "passed": bool(maxv >= 0.8)})
        except ImportError:
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            from tmatch import match  # type: ignore
            r = match(shot, expect)
            result.update({"match": round(r.get("score", 0.0), 4), "at": r.get("at"),
                           "passed": bool(r.get("score", 0.0) >= 0.8)})
        except Exception as ex:  # noqa: BLE001
            result.update({"match_error": str(ex)})
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
