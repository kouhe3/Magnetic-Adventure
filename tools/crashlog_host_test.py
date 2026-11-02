#!/usr/bin/env python3
"""crashlog 宿主探针：在真实 game.exe 里验证 proxy 内置的 VEH 捕获宿主崩溃。

做法：
  1. 把 bin/gametop 的 game.exe/data + 运行库复制到 work/crashlog_host/<ts>/；
  2. 装 build/proxy/Release/b2Physics.dll（代理）与 b2Physics_orig.dll（原版）；
  3. 设 B2RTLPROBE_DLL=build/Release/crashtest.dll：代理的 1.5 s 主线程定时器
     会调 rp_host_entry()，在宿主主线程写空指针（模拟“异常逃逸到 LCL”的崩溃）；
  4. 设 CRASHLOG_DIR/CRASHLOG_DUMP，断言 crash_*.log 里出现：
       EXC seq=1 code=0xC0000005 mod=crashtest.dll av=write
       CTX eip=…
       ≥2 条 FRM … mod=game.exe    （证明拿到宿主调用栈）
       DMP … ok=1                  （minidump 可识别）
  5. 若 LCL 的 MB_OKCANCEL 弹窗出现，额外打印其文本（F315 的现场证据；不作判据，
     因为跨模块 AV 的收尾路径受 F247 影响，可能循环而不是弹窗）。

用法：
    python tools/crashlog_host_test.py [--timeout 60] [--keep]

依据：docs/facts.md F315（LCL 弹窗/Halt(0)）、F316（VEH 捕获）。
"""
from __future__ import annotations

import argparse
import ctypes
import glob
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GAME_SRC = ROOT / "bin" / "gametop"
PROXY = ROOT / "build" / "proxy" / "Release" / "b2Physics.dll"
ORIG = GAME_SRC / "b2Physics.dll"
CRASHTEST = ROOT / "build" / "Release" / "crashtest.dll"
COPY_NAMES = [
    "game.exe", "data", "lua51.dll", "Squall.dll",
    "msvcp100.dll", "msvcp110.dll", "msvcp120.dll",
    "msvcr100.dll", "msvcr110.dll", "libpng13.dll", "zlib1.dll",
]


def build() -> None:
    cmd = ["cmake", "--build", str(ROOT / "build"), "--config", "Release",
           "--target", "b2physics_proxy", "crashlog_crashtest"]
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit("crashlog_host_test: 构建失败\n" + r.stdout[-3000:] + r.stderr[-3000:])


def prepare() -> Path:
    for p in (GAME_SRC / "game.exe", GAME_SRC / "data", PROXY, ORIG, CRASHTEST):
        if not p.exists():
            sys.exit(f"crashlog_host_test: 缺少 {p}")
    stamp = time.strftime("%Y%m%d_%H%M%S")
    dst = ROOT / "work" / "crashlog_host" / f"{stamp}_{os.getpid()}"
    shutil.rmtree(dst, ignore_errors=True)
    dst.mkdir(parents=True)
    (dst / "logs").mkdir()
    for name in COPY_NAMES:
        shutil.copy2(GAME_SRC / name, dst / name)
    shutil.copy2(PROXY, dst / "b2Physics.dll")
    shutil.copy2(ORIG, dst / "b2Physics_orig.dll")
    shutil.copy2(CRASHTEST, dst / "crashtest.dll")
    return dst


def enum_windows(pid: int) -> list[tuple[int, str, str]]:
    user32 = ctypes.windll.user32
    out: list[tuple[int, str, str]] = []

    @ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
    def cb(hwnd, _lp):
        owner = ctypes.c_ulong()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(owner))
        if owner.value == pid:
            cls = ctypes.create_unicode_buffer(256)
            title = ctypes.create_unicode_buffer(512)
            user32.GetClassNameW(hwnd, cls, 256)
            user32.GetWindowTextW(hwnd, title, 512)
            out.append((hwnd, cls.value, title.value))
        return True

    user32.EnumWindows(cb, None)
    return out


def dialog_text(hwnd: int) -> list[str]:
    user32 = ctypes.windll.user32
    out: list[str] = []

    @ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
    def cb(h, _lp):
        cls = ctypes.create_unicode_buffer(64)
        txt = ctypes.create_unicode_buffer(2048)
        user32.GetClassNameW(h, cls, 64)
        user32.GetWindowTextW(h, txt, 2048)
        if txt.value:
            out.append(f"{cls.value}: {txt.value}")
        return True

    user32.EnumChildWindows(hwnd, cb, None)
    return out


def check(cond: bool, what: str, failures: list[str]) -> None:
    print(("PASS  " if cond else "FAIL  ") + what)
    if not cond:
        failures.append(what)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--timeout", type=float, default=60.0)
    ap.add_argument("--keep", action="store_true", help="保留工作目录（默认也保留）")
    ap.add_argument("--no-build", action="store_true")
    args = ap.parse_args()

    if not args.no_build:
        build()
    dst = prepare()
    logs = dst / "logs"

    env = {k: v for k, v in os.environ.items() if not k.startswith("CRASHLOG_")}
    env.update({
        "CRASHLOG_DIR": str(logs),
        "CRASHLOG_DUMP": "1",
        "CRASHLOG_DIALOG": "1",
        "B2PROXY_LOG": str(logs / "b2ffi.bin"),
        "B2RTLPROBE_DLL": str(dst / "crashtest.dll"),
    })
    env.pop("B2PROXY_HOT", None)
    p = subprocess.Popen([str(dst / "game.exe")], cwd=dst, env=env)
    print(f"game pid={p.pid} dir={dst}")

    log_path = None
    deadline = time.time() + args.timeout
    while time.time() < deadline:
        cands = sorted(glob.glob(str(logs / "crash_*.log")))
        for cand in cands:
            text = Path(cand).read_text(encoding="utf-8", errors="replace")
            if "\nEXC " in text or text.startswith("EXC "):
                log_path = Path(cand)
                break
        if log_path:
            break
        if p.poll() is not None:
            break
        time.sleep(0.3)

    failures: list[str] = []
    if not log_path:
        print(f"FAIL  在 {args.timeout:.0f}s 内没有 crash 日志（game rc={p.poll()}）")
        for h, cls, title in enum_windows(p.pid):
            print(f"  window {h} {cls!r} {title!r}")
        if p.poll() is None:
            p.kill()
        return 1

    text = log_path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    exc = [ln for ln in lines if ln.startswith("EXC ")]
    first = next((ln for ln in exc if "seq=1 " in ln), "")
    print(f"log: {log_path}  ({len(text)} B, EXC={len(exc)})")
    check("code=0xC0000005" in first, "seq=1 是 access violation", failures)
    check("mod=crashtest.dll" in first, "seq=1 定位到注入的 crashtest.dll", failures)
    check("av=write" in first and "fault=0x00000000" in first, "seq=1 是写 0 地址", failures)
    check(any(ln.startswith("CTX ") and "eip=0x" in ln for ln in lines),
          "记录 CONTEXT", failures)
    host_frames = [ln for ln in lines
                   if ln.startswith("FRM ") and " mod=game.exe" in ln]
    check(len(host_frames) >= 2, f"宿主调用栈（game.exe 帧 {len(host_frames)} 条）", failures)
    check(any(ln.startswith("MOD ") and "name=game.exe" in ln for ln in lines),
          "模块表含 game.exe", failures)

    dumps = []
    for _ in range(30):
        dumps = sorted(glob.glob(str(logs / "crash_*.dmp")))
        if dumps and Path(dumps[0]).stat().st_size > 4096:
            break
        time.sleep(0.1)
    check(bool(dumps), "生成 minidump", failures)
    if dumps:
        d = Path(dumps[0])
        check(d.read_bytes()[:4] == b"MDMP" and d.stat().st_size > 4096,
              f"dump 可识别（{d.name}, {d.stat().st_size} B）", failures)

    wins = enum_windows(p.pid)
    dlg = next((w for w in wins if w[1] == "#32770"), None)
    if dlg:
        print(f"INFO  LCL 弹窗 {dlg[0]} {dlg[2]!r}:")
        for ln in dialog_text(dlg[0]):
            print("  " + ln)
    else:
        print("INFO  本轮没有抓到 #32770 弹窗（跨模块 AV 收尾受 F247 影响，不作判据）")

    if p.poll() is None:
        p.kill()
    try:
        p.wait(timeout=5)
    except subprocess.TimeoutExpired:
        pass

    print(f"\ndir: {dst}")
    if failures:
        print(f"crashlog_host_test: FAIL ({len(failures)})")
        return 1
    print("crashlog_host_test: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
