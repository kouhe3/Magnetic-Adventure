#!/usr/bin/env python3
"""录制面板（Tk）：启动游戏 → 记录鼠标/键盘 + 每次点击时的截图 → STOP 直接杀进程。

为什么杀进程而不是正常退出：GameTop 版在退出时 ShellExecute 打开统计页（F42），
TerminateProcess 跳过宿主的所有退出处理，录制结束不会弹广告。

录制产物（work/rec_<时间戳>/）：
  events.jsonl   每行 {t, kind: move|down|up|wheel|key|shot, x, y, nx, ny, ...}
  shots/click_0001.png 等 —— 每个按下沿（左右键）一张，抓的是游戏客户区
  meta.json      窗口矩形、PID、开始/结束时间

用法:
  python tools/recorder_gui.py                 # 打开面板
  python tools/recorder_gui.py --selftest 15   # 自测：自动开游戏→录 15s→STOP

点击坐标同时记录屏幕坐标 (x,y) 与窗口归一化坐标 (nx,ny)，replay.py 可直接吃。
"""
import ctypes
import ctypes.wintypes as wt
import json
import os
import subprocess
import sys
import queue
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import record as rec  # noqa: E402  复用钩子结构体、grab_window

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAME_DIR = os.path.join(ROOT, "work", "integration")
PID_FILE = os.path.join(ROOT, "work", "game_pid.txt")

u = rec.u
# 显式声明参数宽度：不声明时 ctypes 按 c_int 传参，64 位 LPARAM 会 OverflowError，
# 结果钩子链断了、事件被吞。
u.CallNextHookEx.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_size_t, ctypes.c_ssize_t]
u.CallNextHookEx.restype = ctypes.c_ssize_t
k32 = ctypes.windll.kernel32
WM_MOUSEMOVE, WM_LBUTTONDOWN, WM_LBUTTONUP = 0x0200, 0x0201, 0x0202
WM_RBUTTONDOWN, WM_RBUTTONUP, WM_MOUSEWHEEL = 0x0204, 0x0205, 0x020A
WM_KEYDOWN, WM_SYSKEYDOWN = 0x0100, 0x0104
VK_F8 = 0x77
PROCESS_TERMINATE = 0x0001


def find_window(pid):
    """按 PID 找游戏的可见主窗口，返回 (hwnd, (l, t, w, h))。"""
    found = []

    def cb(h, l):
        p = wt.DWORD()
        u.GetWindowThreadProcessId(h, ctypes.byref(p))
        if p.value == pid and u.IsWindowVisible(h):
            n = ctypes.create_unicode_buffer(256)
            u.GetWindowTextW(h, n, 256)
            r = wt.RECT()
            u.GetWindowRect(h, ctypes.byref(r))
            if "Magnetic" in n.value and r.right - r.left > 100:
                found.append((h, (r.left, r.top, r.right - r.left, r.bottom - r.top)))
        return True

    CB = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
    u.EnumWindows(CB(cb), 0)
    return found[0] if found else (None, None)


def kill_pid(pid):
    """TerminateProcess：跳过宿主的退出处理（GameTop 广告）。"""
    h = k32.OpenProcess(PROCESS_TERMINATE, False, pid)
    if not h:
        return False
    ok = bool(k32.TerminateProcess(h, 1))
    k32.CloseHandle(h)
    return ok


class Session:
    """一次录制：钩子线程 + 点下沿截图 + JSONL。"""

    def __init__(self, out_dir):
        self.out_dir = out_dir
        self.shots = os.path.join(out_dir, "shots")
        os.makedirs(self.shots, exist_ok=True)
        self.jsonl = open(os.path.join(out_dir, "events.jsonl"), "w", encoding="utf-8")
        self.lock = threading.Lock()
        self.pid = 0
        self.hwnd = None
        self.rect = None
        self.running = True
        self.start = time.time()
        self.clicks = 0
        self.events = 0
        self.last_move = 0.0
        self.thread = None
        self.hooks = []
        self.on_update = None
        self.q = queue.Queue()          # 事件 → 写盘线程
        self.shotq = queue.Queue()      # 截图请求 → 截图线程
        self.record_idle_moves = False  # 默认不记空闲移动（只有按住拖拽才记轨迹）
        self.drag = 0
        self.move_hz = 62               # 拖拽轨迹采样上限（16ms）
        self.writer = threading.Thread(target=self._write_loop, daemon=True)
        self.shotter = threading.Thread(target=self._shot_loop, daemon=True)
        self.writer.start()
        self.shotter.start()

    # --- 录制 ---
    def begin(self, pid):
        self.pid = pid
        self.hwnd, self.rect = find_window(pid)
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()

    def _emit(self, kind, x=None, y=None, **kw):
        row = {"t": int((time.time() - self.start) * 1000), "kind": kind}
        if x is not None and self.rect:
            l, t, w, h = self.rect
            row.update(x=x, y=y,
                       nx=round((x - l) / max(1, w), 4),
                       ny=round((y - t) / max(1, h), 4))
        row.update(kw)
        self.q.put(row)            # 钩子回调里只入队，I/O 交给写盘线程
        self.events += 1
        if self.on_update:
            self.on_update()

    def _write_loop(self):
        while True:
            row = self.q.get()
            if row is None:
                break
            batch = [row]
            while len(batch) < 256:
                try:
                    nxt = self.q.get_nowait()
                except queue.Empty:
                    break
                if nxt is None:
                    self.q.put(None)
                    break
                batch.append(nxt)
            with self.lock:
                self.jsonl.write(''.join(json.dumps(r, ensure_ascii=False) + "\n" for r in batch))
                self.jsonl.flush()

    def _shot_loop(self):
        while True:
            item = self.shotq.get()
            if item is None:
                break
            path, rect = item
            try:
                rec.grab_screen(rect, path)
            except Exception:
                pass

    def _shot(self, tag):
        """只预生成文件名并丢给截图线程：GL 窗口抓屏 + PNG 编码都不能占着钩子。"""
        name = os.path.join(self.shots, f"click_{self.clicks:04d}_{tag}.png")
        _, rect = find_window(self.pid)
        if rect:
            self.rect = rect
        self.shotq.put((name, rect or self.rect))
        return name

    def _mouse(self, code, wparam, lparam):
        if code >= 0:
            ms = ctypes.cast(lparam, ctypes.POINTER(rec.MSLLHOOKSTRUCT)).contents
            x, y = ms.pt.x, ms.pt.y
            if wparam == WM_MOUSEMOVE:
                if not (self.record_idle_moves or self.drag):
                    return u.CallNextHookEx(None, code, wparam, lparam)
                now = time.time()
                step = 1.0 / max(1, self.move_hz)
                if now - self.last_move >= step:
                    self.last_move = now
                    self._emit("move", x, y, drag=bool(self.drag))
            elif wparam in (WM_LBUTTONDOWN, WM_RBUTTONDOWN):
                self.clicks += 1
                self.drag = 1
                tag = "left" if wparam == WM_LBUTTONDOWN else "right"
                path = self._shot(tag)          # 点击瞬间截图
                self._emit("down", x, y, button=tag, shot=path)
            elif wparam in (WM_LBUTTONUP, WM_RBUTTONUP):
                self._emit("up", x, y, button="left" if wparam == WM_LBUTTONUP else "right")
                self.drag = 0
            elif wparam == WM_MOUSEWHEEL:
                d = (ms.mouseData >> 16) & 0xFFFF
                self._emit("wheel", x, y, delta=d if d < 0x8000 else d - 0x10000)
        return u.CallNextHookEx(None, code, wparam, lparam)

    def _key(self, code, wparam, lparam):
        if code >= 0:
            kb = ctypes.cast(lparam, ctypes.POINTER(rec.KBDLLHOOKSTRUCT)).contents
            if wparam in (WM_KEYDOWN, WM_SYSKEYDOWN):
                if kb.vkCode == VK_F8:          # F8 = 只停录制，不杀游戏
                    self.running = False
                else:
                    self._emit("key", vk=int(kb.vkCode))
        return u.CallNextHookEx(None, code, wparam, lparam)

    def _loop(self):
        mouse_cb = rec.HOOKPROC(self._mouse)
        key_cb = rec.HOOKPROC(self._key)
        self.hooks = [mouse_cb, key_cb]
        hm = u.SetWindowsHookExW(rec.WH_MOUSE_LL, mouse_cb, None, 0)
        hk = u.SetWindowsHookExW(rec.WH_KEYBOARD_LL, key_cb, None, 0)
        msg = wt.MSG()
        while self.running:
            while u.PeekMessageW(ctypes.byref(msg), None, 0, 0, 1):
                u.TranslateMessage(ctypes.byref(msg))
                u.DispatchMessageW(ctypes.byref(msg))
            time.sleep(0.005)
        if hm:
            u.UnhookWindowsHookEx(hm)
        if hk:
            u.UnhookWindowsHookEx(hk)

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        self.q.put(None)
        self.shotq.put(None)
        self.writer.join(timeout=2)
        self.shotter.join(timeout=2)
        with self.lock:
            try:
                self.jsonl.close()
            except Exception:
                pass
        meta = {"pid": self.pid, "rect": self.rect,
                "start": self.start, "end": time.time(),
                "events": self.events, "clicks": self.clicks}
        with open(os.path.join(self.out_dir, "meta.json"), "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)


class App:
    def __init__(self, selftest=None):
        import tkinter as tk
        from tkinter import messagebox
        self.tk = tk
        self.messagebox = messagebox
        self.proc = None
        self.session = None
        self.selftest = selftest

        self.root = tk.Tk()
        self.root.title("Magnetic Adventure 录制面板")
        self.root.geometry("600x270+0+0")   # 固定在左上角，避免盖住游戏窗口
        self.root.attributes("-topmost", True)

        tk.Label(self.root, text="① 启动游戏 → ② 录制 → ③ STOP 杀进程",
                 font=("Segoe UI", 10, "bold")).pack(pady=(10, 4))

        row = tk.Frame(self.root)
        row.pack(pady=4)
        self.b_start = tk.Button(row, text="启动游戏并录制", width=16, command=self.start_game)
        self.b_start.pack(side="left", padx=4)
        self.b_record = tk.Button(row, text="开始录制", width=10, command=self.toggle_record, state="disabled")
        self.b_record.pack(side="left", padx=4)
        self.b_stop = tk.Button(row, text="STOP：停录 + 杀游戏", width=20,
                                bg="#c0392b", fg="white", command=self.stop_all, state="disabled")
        self.b_stop.pack(side="left", padx=4)

        self.idle = tk.BooleanVar(value=False)
        tk.Checkbutton(self.root, text="同时记录空闲鼠标移动（默认只记按住时的拖拽轨迹）",
                       variable=self.idle, command=self.toggle_idle).pack(anchor="w", padx=12)

        self.status = tk.StringVar(value="未启动")
        tk.Label(self.root, textvariable=self.status, anchor="w", justify="left").pack(
            fill="x", padx=12, pady=8)

        self.out = tk.StringVar(value="")
        tk.Label(self.root, textvariable=self.out, anchor="w", fg="#555").pack(fill="x", padx=12)

        tk.Button(self.root, text="打开输出目录", command=self.open_dir).pack(pady=6)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        if selftest:
            self.root.after(300, self.start_game)
            self.root.after(int(selftest * 1000), self.stop_all)

    # --- 动作 ---
    def launch(self):
        if self.proc and self.proc.poll() is None:
            return self.proc.pid
        exe = os.path.join(GAME_DIR, "game.exe")
        if not os.path.exists(exe):
            self.status.set(f"找不到 {exe}")
            return None
        self.proc = subprocess.Popen([exe], cwd=GAME_DIR)
        os.makedirs(os.path.dirname(PID_FILE), exist_ok=True)
        with open(PID_FILE, "w") as f:
            f.write(str(self.proc.pid))
        return self.proc.pid

    def start_game(self):
        pid = self.launch()
        if not pid:
            return
        self.b_start.config(state="disabled")
        self.b_stop.config(state="normal")
        self.b_record.config(state="normal", text="暂停录制")
        self.begin_session(pid)
        self.status.set(f"游戏已启动 pid={pid}，录制中…")

    def begin_session(self, pid):
        stamp = time.strftime("%Y%m%d_%H%M%S")
        out_dir = os.path.join(ROOT, "work", f"rec_{stamp}")
        self.session = Session(out_dir)
        self.session.on_update = self.refresh
        self.session.begin(pid)
        self.out.set(f"输出：{os.path.relpath(out_dir, ROOT)}")
        self.refresh()

    def toggle_idle(self):
        if self.session:
            self.session.record_idle_moves = bool(self.idle.get())

    def refresh(self):
        if not self.session:
            return
        mode = "全部移动" if self.idle.get() else "仅拖拽"
        self.status.set(f"录制中：{self.session.events} 事件 / {self.session.clicks} 次点击"
                        f"  · 移动采样 {self.session.move_hz} Hz（{mode}）")

    def toggle_record(self):
        if not self.session:
            return
        if self.session.running:
            self.session.stop()
            self.b_record.config(text="继续录制")
            self.status.set("已暂停（游戏还在跑）")
        else:
            pid = self.proc.pid if self.proc else 0
            if not pid:
                return
            s = self.session
            s.running = True
            s.thread = threading.Thread(target=s._loop, daemon=True)
            s.thread.start()
            self.b_record.config(text="暂停录制")
            self.refresh()

    def stop_all(self):
        if self.session:
            self.session.stop()
            self.session = None
        pid = self.proc.pid if self.proc else 0
        if pid:
            kill_pid(pid)          # 直接杀，跳过 GameTop 退出广告
            try:
                self.proc.wait(timeout=3)
            except Exception:
                pass
        self.b_start.config(state="normal")
        self.b_record.config(state="disabled", text="开始录制")
        self.b_stop.config(state="disabled")
        self.status.set("已停止，游戏已结束")
        if self.selftest:
            self.root.after(300, self.root.destroy)

    def open_dir(self):
        if self.session:
            os.startfile(self.session.out_dir)

    def on_close(self):
        if self.proc and self.proc.poll() is None:
            if not self.messagebox.askokcancel("退出", "游戏还在运行，停止录制并杀掉它？"):
                return
            self.stop_all()
        self.root.destroy()

    def run(self):
        self.root.mainloop()


def main():
    selftest = None
    if "--selftest" in sys.argv:
        selftest = float(sys.argv[sys.argv.index("--selftest") + 1])
    App(selftest).run()


if __name__ == "__main__":
    main()
