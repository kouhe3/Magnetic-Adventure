#!/usr/bin/env python3
"""录制面板（Tk）：装代理 DLL → 起游戏 → 抓 FFI → STOP 直接杀进程。

只录 FFI（`ffi.bin`）。鼠标/键盘采集、点击截图、鼠标宏重放都已退出流程：
  - 部分关卡初始化用 math.random（F69），鼠标宏无法复现场景；
  - 门禁只看 `no_crash` + `bounded`，数据源是 ffi.bin（视觉默认关闭）。

为什么杀进程而不是正常退出：GameTop 版在退出时 ShellExecute 打开统计页（F42），
TerminateProcess 跳过宿主的所有退出处理，录制结束不会弹广告。

录制产物（work/rec_<时间戳>/）：
  ffi.bin    代理 DLL 写的调用日志（~1–6 MB/s；密度高时 10+ MB/s）
  meta.json  {pid, start, end, size}

用法:
  python tools/recorder_gui.py                 # 打开面板
  python tools/recorder_gui.py --selftest 15   # 自测：自动开游戏→录 15s→STOP
"""
import ctypes
import ctypes.wintypes as wt
import json
import os
import shutil
import subprocess
import sys
import threading
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROXY_DLL = os.path.join(ROOT, "build", "proxy", "Release", "b2Physics.dll")
OURS_DLL = os.path.join(ROOT, "build", "Release", "b2Physics.dll")
GAME_DIR = os.path.join(ROOT, "work", "integration")
PID_FILE = os.path.join(ROOT, "work", "game_pid.txt")

u = ctypes.windll.user32
k32 = ctypes.windll.kernel32
PROCESS_TERMINATE = 0x0001


def find_window(pid):
    """按 PID 找游戏主窗口（只用于把前台焦点给它）。"""
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
                found.append(h)
        return True

    CB = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
    u.EnumWindows(CB(cb), 0)
    return found[0] if found else None


def kill_pid(pid):
    """TerminateProcess：跳过宿主的退出处理（GameTop 广告）。"""
    h = k32.OpenProcess(PROCESS_TERMINATE, False, pid)
    if not h:
        return False
    ok = bool(k32.TerminateProcess(h, 1))
    k32.CloseHandle(h)
    return ok


class RecSession:
    """一次录制：只跟踪输出目录与计时，写 ffi.bin 的是代理 DLL。"""

    def __init__(self, out_dir):
        self.out_dir = out_dir
        self.ffi = os.path.join(out_dir, "ffi.bin")
        os.makedirs(out_dir, exist_ok=True)
        self.start = time.time()
        self.end = None
        self.pid = 0

    def size(self):
        try:
            return os.path.getsize(self.ffi)
        except OSError:
            return 0

    def begin(self, pid):
        self.pid = pid
        self.start = time.time()
        self.shots = os.path.join(self.out_dir, "shots")
        os.makedirs(self.shots, exist_ok=True)
        threading.Thread(target=self._shot_loop, daemon=True).start()

    def _shot_loop(self):
        """1 fps 截图（半尺寸 JPEG）：把 FFI 的步号换算成秒就能调出对应画面。

        步号 → 时间：dt 固定 0.01 s，所以 step N ≈ N/100 秒（F93）。
        """
        try:
            from PIL import ImageGrab
        except ImportError:
            return
        n = 0
        while self.end is None:
            t = time.time() - self.start
            try:
                img = ImageGrab.grab()
                img = img.resize((img.width // 2, img.height // 2))
                img.save(os.path.join(self.shots, f"t{int(t):04d}.jpg"), quality=60)
                n += 1
            except Exception:  # noqa: BLE001
                pass
            time.sleep(max(0.0, 1.0 - (time.time() - self.start - t)))

    def stop(self):
        if self.end is None:
            self.end = time.time()
            with open(os.path.join(self.out_dir, "meta.json"), "w", encoding="utf-8") as f:
                json.dump({"pid": self.pid, "start": self.start, "end": self.end,
                           "size": self.size()}, f)


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
        self.root.geometry("+0+0")          # 固定在左上角；尺寸按内容自适应（run 里定）
        self.root.attributes("-topmost", True)

        tk.Label(self.root, text="① 启动游戏并录制 → ② 进关卡玩 → ③ STOP 杀进程",
                 font=("Segoe UI", 10, "bold")).pack(pady=(10, 4))

        row = tk.Frame(self.root)
        row.pack(pady=6)
        self.b_start = tk.Button(row, text="启动游戏并录制", width=16, command=self.start_game)
        self.b_start.pack(side="left", padx=4)
        self.b_stop = tk.Button(row, text="STOP：停录 + 杀游戏", width=20,
                                bg="#c0392b", fg="white", command=self.stop_all, state="disabled")
        self.b_stop.pack(side="left", padx=4)

        row2 = tk.Frame(self.root)
        row2.pack(pady=(0, 6))
        tk.Button(row2, text="试玩替换 DLL（不录制）", width=26,
                  command=self.play_ours).pack(side="left", padx=4)
        tk.Button(row2, text="打开输出目录", width=16, command=self.open_dir).pack(side="left", padx=4)

        self.status = tk.StringVar(value="未启动")
        tk.Label(self.root, textvariable=self.status, anchor="w", justify="left",
                 font=("Consolas", 9)).pack(fill="x", padx=12, pady=10)

        self.out = tk.StringVar(value="")
        tk.Label(self.root, textvariable=self.out, anchor="w", fg="#555").pack(fill="x", padx=12)

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.after(1000, self._tick)

        if selftest:
            self.root.after(300, self.start_game)
            self.root.after(int(selftest * 1000), self.stop_all)

    # --- 动作 ---
    def install_proxy(self):
        """录制 = 用原版逻辑跑 + 抓 FFI：代理 DLL 占位，b2Physics_orig.dll 放真身。"""
        orig = os.path.join(GAME_DIR, "b2Physics_orig.dll")
        if not os.path.exists(orig):
            src = os.path.join(ROOT, "bin", "gametop", "b2Physics.dll")
            if os.path.exists(src):
                shutil.copyfile(src, orig)
        target = os.path.join(GAME_DIR, "b2Physics.dll")
        if not os.path.exists(PROXY_DLL):
            return False
        try:
            shutil.copyfile(PROXY_DLL, target)
            return True
        except OSError:
            return False

    def launch(self):
        if self.proc and self.proc.poll() is None:
            return self.proc.pid
        exe = os.path.join(GAME_DIR, "game.exe")
        if not os.path.exists(exe):
            self.status.set(f"找不到 {exe}")
            return None
        env = dict(os.environ)
        if self.session:
            env["B2PROXY_LOG"] = self.session.ffi
        else:
            env.pop("B2PROXY_LOG", None)    # 试玩模式：不产生日志
        self.proc = subprocess.Popen([exe], cwd=GAME_DIR, env=env)
        for _ in range(20):                 # 起游戏后把前台焦点给它
            if find_window(self.proc.pid):
                break
            time.sleep(0.5)
        os.makedirs(os.path.dirname(PID_FILE), exist_ok=True)
        with open(PID_FILE, "w") as f:
            f.write(str(self.proc.pid))
        return self.proc.pid

    def start_game(self):
        stamp = time.strftime("%Y%m%d_%H%M%S")
        self.session = RecSession(os.path.join(ROOT, "work", f"rec_{stamp}"))
        self.out.set(f"输出：{os.path.relpath(self.session.out_dir, ROOT)}")
        if not self.install_proxy():
            self.status.set("装代理 DLL 失败（是否有游戏进程占用文件？）")
            return
        pid = self.launch()
        if not pid:
            return
        self.session.begin(pid)
        self.b_start.config(state="disabled")
        self.b_stop.config(state="normal")
        self.status.set(f"录制中 pid={pid}\nFFI 0 MB — 请进入关卡")

    def play_ours(self):
        """人工试玩：装我们的 DLL，起游戏，不抓 FFI。"""
        try:
            shutil.copyfile(OURS_DLL, os.path.join(GAME_DIR, "b2Physics.dll"))
        except OSError as ex:
            self.status.set(f"换 DLL 失败：{ex}")
            return
        self.session = None
        self.out.set("试玩模式：build/Release/b2Physics.dll")
        pid = self.launch()
        if pid:
            self.b_start.config(state="disabled")
            self.b_stop.config(state="normal")
            self.status.set(f"试玩替换 DLL：pid={pid}")

    def _tick(self):
        """每秒刷新：只靠事件驱动会让体积读数停住。"""
        try:
            s = self.session
            if s and s.end is None:
                size = s.size()
                el = max(0.5, time.time() - s.start)
                self.status.set(f"录制中 pid={s.pid} · {el:.0f} s\n"
                                f"FFI {size / 1048576:.1f} MB · {size / 1048576 / el:.2f} MB/s")
        finally:
            self.root.after(1000, self._tick)

    def stop_all(self):
        if self.session:
            self.session.stop()
        pid = self.proc.pid if self.proc else 0
        if pid:
            kill_pid(pid)          # 直接杀，跳过 GameTop 退出广告
            try:
                self.proc.wait(timeout=3)
            except Exception:
                pass
        if self.session:
            size = self.session.size()
            self.status.set(f"已停止 · ffi.bin {size / 1048576:.1f} MB\n"
                            f"跑门禁：python tools/gate.py {os.path.relpath(self.session.out_dir, ROOT)} --name <关卡>")
        else:
            self.status.set("已停止，游戏已结束")
        self.b_start.config(state="normal")
        self.b_stop.config(state="disabled")
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
        self.root.update_idletasks()
        self.root.geometry(f"{self.root.winfo_reqwidth()}x{self.root.winfo_reqheight()}+0+0")
        self.root.mainloop()


def main():
    selftest = None
    if "--selftest" in sys.argv:
        selftest = float(sys.argv[sys.argv.index("--selftest") + 1])
    App(selftest).run()


if __name__ == "__main__":
    main()
