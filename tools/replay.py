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
from PIL import Image  # noqa: E402

u = ctypes.windll.user32
u.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MOUSEEVENTF_LEFTDOWN, MOUSEEVENTF_LEFTUP = 0x0002, 0x0004
MOUSEEVENTF_RIGHTDOWN, MOUSEEVENTF_RIGHTUP = 0x0008, 0x0010
MOUSEEVENTF_WHEEL = 0x0800



def _is_game_hwnd(pid, h):
    """必须是 game.exe 的窗口：面板/其它标题含 Magnetic 的窗口不算。"""
    p = wt.DWORD()
    u.GetWindowThreadProcessId(h, ctypes.byref(p))
    if pid is not None and p.value != pid:
        return False
    k32 = ctypes.windll.kernel32
    PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
    hp = k32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, p.value)
    if not hp:
        return False
    try:
        buf = ctypes.create_unicode_buffer(1024)
        size = wt.DWORD(1024)
        if not k32.QueryFullProcessImageNameW(hp, 0, buf, ctypes.byref(size)):
            return False
        return buf.value.lower().endswith("game.exe")
    finally:
        k32.CloseHandle(hp)

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
        if _is_game_hwnd(pid, h) and u.IsWindowVisible(h):
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


def game_hwnd():
    pid = None
    pf = os.path.join(ROOT, "work", "game_pid.txt")
    if os.path.exists(pf):
        try:
            pid = int(open(pf).read().strip())
        except ValueError:
            pid = None
    found = []

    def cb(h, l):
        if _is_game_hwnd(pid, h) and u.IsWindowVisible(h):
            found.append(h)
        return True

    CB = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
    u.EnumWindows(CB(cb), 0)
    return found[0] if found else None


def focus_game():
    """脚本启动的游戏不一定拿到前台焦点：不聚焦时鼠标事件打到别的窗口，抓屏也抓到别的窗口。"""
    h = game_hwnd()
    if not h:
        return False
    u.ShowWindow(h, 9)            # SW_RESTORE
    fg = u.GetForegroundWindow()
    tid_fg = u.GetWindowThreadProcessId(fg, None) if fg else 0
    tid_me = ctypes.windll.kernel32.GetCurrentThreadId()
    if tid_fg and tid_fg != tid_me:
        # 前台窗口不属于本线程时 SetForegroundWindow 会被系统忽略，先 AttachThreadInput
        u.AttachThreadInput(tid_me, tid_fg, True)
        u.SetForegroundWindow(h)
        u.AttachThreadInput(tid_me, tid_fg, False)
    else:
        u.SetForegroundWindow(h)
    u.BringWindowToTop(h)
    time.sleep(0.2)
    return u.GetForegroundWindow() == h


def wait_focus_idle(hwnd, timeout):
    """等游戏回到前台；期间**不动鼠标、不抢焦点**（用户可能正 Alt-Tab）。"""
    end = time.time() + timeout
    while time.time() < end:
        if u.GetForegroundWindow() == hwnd:
            return True
        time.sleep(0.1)
    return u.GetForegroundWindow() == hwnd


def ensure_foreground(timeout=6.0):
    """拿不到焦点就返回 False——绝不带着失焦状态去动鼠标（会点错窗口）。"""
    h = game_hwnd()
    if not h:
        return False
    end = time.time() + timeout
    while time.time() < end:
        if u.GetForegroundWindow() == h:
            return True
        focus_game()
        time.sleep(0.2)
    return u.GetForegroundWindow() == h


def screen_xy(ev, rect):
    x0, y0, w, h = rect
    if "nx" in ev and "ny" in ev:
        return int(x0 + ev["nx"] * w), int(y0 + ev["ny"] * h)
    if "x" in ev:
        return int(ev["x"]), int(ev["y"])
    return None


def locate_shift(shot_path, rect, nx, ny, patch=48, radius=140):
    """用录制时的点击帧做模板匹配，找出物体在实时画面里偏移了多少。

    返回 (dx, dy, score)；找不到可信匹配时返回 (0, 0, score)。
    钥匙/信件这类小物体被拖动或惯性漂移后，绝对坐标重放会抓空，这里按实际位置平移整段拖拽。
    """
    try:
        from tmatch import match as tmatch
    except Exception:  # noqa: BLE001
        return 0, 0, 0.0
    try:
        ref = Image.open(shot_path).convert("RGB")
    except Exception:  # noqa: BLE001
        return 0, 0, 0.0
    rw, rh = ref.size
    cx, cy = int(nx * rw), int(ny * rh)
    if cx < patch or cy < patch or cx + patch >= rw or cy + patch >= rh:
        return 0, 0, 0.0
    tpl = ref.crop((cx - patch, cy - patch, cx + patch, cy + patch))

    live_path = os.path.join(ROOT, "work", "_anchor_live.png")
    if not rc.grab_screen(rect, live_path):
        return 0, 0, 0.0
    live = Image.open(live_path).convert("RGB")
    lw, lh = live.size
    x0, y0 = int(nx * lw), int(ny * lh)
    sx0, sy0 = max(0, x0 - radius), max(0, y0 - radius)
    sx1, sy1 = min(lw, x0 + radius), min(lh, y0 + radius)
    scene = live.crop((sx0, sy0, sx1, sy1))
    sp = os.path.join(ROOT, "work", "_anchor_scene.png")
    tp = os.path.join(ROOT, "work", "_anchor_tpl.png")
    scene.save(sp)
    tpl.save(tp)
    try:
        r = tmatch(sp, tp)
    except Exception:  # noqa: BLE001
        return 0, 0, 0.0
    score = float(r.get("score", 0.0))
    at = r.get("at") or [0, 0]
    # 匹配到的模板左上角 -> 模板中心在实时画面里的坐标
    fx = sx0 + at[0] + patch
    fy = sy0 + at[1] + patch
    dx, dy = fx - x0, fy - y0
    if score < 0.7 or abs(dx) > radius or abs(dy) > radius:
        return 0, 0, score
    return dx, dy, score


def main():
    if len(sys.argv) < 2:
        print("usage: replay.py <jsonl> [--speed N] [--shot png] [--expect png] [--post s]")
        return 2
    path = sys.argv[1]
    speed, post, expect = 1.0, 3.0, None
    # 自适应拖拽实测失误率更高（模板匹配会被背景纹理带偏），默认关闭，需要时 --anchor
    anchor = False
    focus_wait = 30.0          # 失焦后最多等这么久，然后中止
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
        elif a == "--anchor":
            anchor = True
        elif a == "--focus-wait":
            focus_wait = float(sys.argv[i + 1])

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
    if not ensure_foreground(8.0):
        print(json.dumps({"ok": False, "error": "game window not focused: 拒绝在失焦状态下驱动鼠标"}))
        return 4

    t0 = time.perf_counter()
    pos = None
    drift = 0.0
    click_no = 0
    shift = (0, 0)
    anchors = []

    hwnd = game_hwnd()
    press_at = None
    for ev in events:
        if u.GetForegroundWindow() != hwnd:
            # 用户切走了：停手等回来。期间不移动鼠标、不抢焦点。
            paused = time.perf_counter()
            if not wait_focus_idle(hwnd, focus_wait):
                print(json.dumps({"ok": False, "at_event": ev["t"],
                                  "error": "focus lost too long: aborted without touching mouse"}))
                return 4
            t0 += time.perf_counter() - paused
        target = ev["t"] / 1000.0 / speed
        wait = target - (time.perf_counter() - t0)
        if wait < 0:
            drift = max(drift, -wait * 1000.0)
            wait = 0.0
        xy = screen_xy(ev, rect)
        kind = ev["kind"]
        if kind == "down":
            shift = (0, 0)          # 每段新的拖拽重新定位，避免上一段的偏移泄漏
            if anchor and ev.get("shot") and xy:
                dx, dy, sc = locate_shift(ev["shot"], rect, ev.get("nx", 0), ev.get("ny", 0))
                shift = (dx, dy)
                anchors.append({"click": click_no + 1, "dx": dx, "dy": dy,
                                "score": round(sc, 3)})
                if dx or dy:
                    xy = (xy[0] + dx, xy[1] + dy)

        if kind == "move" and xy is not None:
            xy = (xy[0] + shift[0], xy[1] + shift[1])
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
            if u.GetForegroundWindow() != game_hwnd() and not ensure_foreground(2.0):
                print(json.dumps({"ok": False, "click": click_no,
                                  "error": "lost focus before click"}))
                return 4
            if ev.get("shot"):
                shotq.put((click_no, os.path.join(outdir, f"replay_click_{click_no:02d}.png")))
            if xy:
                u.SetCursorPos(xy[0], xy[1])
                pos = (xy[0], xy[1])
            u.mouse_event(MOUSEEVENTF_RIGHTDOWN if ev.get("button") == "right" else MOUSEEVENTF_LEFTDOWN,
                          0, 0, 0, 0)
            press_at = time.perf_counter()
        elif kind == "up":
            if press_at is not None:
                held = time.perf_counter() - press_at
                if held < 0.08:          # 游戏按帧轮询输入，太短的点击会被吞掉
                    time.sleep(0.08 - held)
                press_at = None
            if xy:
                xy = (xy[0] + shift[0], xy[1] + shift[1])
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
    result = {"ok": True, "events": len(events), "shot": shot, "anchors": anchors,
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
