#!/usr/bin/env python3
"""crashlog 单元探针：在 32 位进程内验证 VEH 捕获 first-chance 异常。

用法（必须 32 位 CPython；脚本会按 PY32 自动重启自己）：
    "C:/Users/K/.local/bin/python3.12.exe" tools/crashlog_test.py [--no-build]

判据（任一失败退出码 1）：
  1. 设 CRASHLOG_DIR + CRASHLOG_DUMP，LoadLibrary build/Release/crashlog.dll，
     调 crashlog_selftest_av（__try/__except 吞掉的写空指针）⇒ 日志出现
     EXC seq=1 code=0xC0000005、mod=crashlog.dll、av=write、CTX、≥2 条 FRM/SCN，
     且 dump 文件存在、magic=MDMP。
  2. 再调 crashlog_selftest_raise（RaiseException 形式的 AV，同样被吞）
     ⇒ 出现 EXC seq=2 且 p1=0xDEADBEEF。
  3. 子进程调 crashlog_selftest_fp（解除 invalid 屏蔽后 0÷0）⇒ 子进程可能以
     0xC0000090 退出，但 crash_*.log 里必须有 code=0xC0000090 /
     note=float-invalid-operation。
  4. 设 CRASHLOG_DIALOG=1，临时弹 MessageBoxW("hello-crashlog") ⇒ 日志出现
     DLG … text=…hello-crashlog（覆盖没有 OS 异常的 FPC raise）。
  5. 负例：子进程不设 CRASHLOG_*，同样调 AV ⇒ 目录里没有 crash_*.log。

依据：docs/facts.md F315（LCL 弹窗/Halt(0)）、F316（VEH 捕获）、F317（弹窗正文）。
"""
from __future__ import annotations

import argparse
import ctypes
import glob
import os
import shutil
import struct
import subprocess
import sys
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DLL = ROOT / "build" / "Release" / "crashlog.dll"
PY32 = os.environ.get("PY32", r"C:/Users/K/.local/bin/python3.12.exe")


def relaunch_as_x86() -> None:
    if struct.calcsize("P") * 8 == 32:
        return
    if os.environ.get("CRASHLOG_TEST_NO_RELAUNCH"):
        sys.exit("crashlog_test: 需要 32 位 CPython（当前 64 位）")
    exe = Path(PY32)
    if not exe.exists():
        sys.exit(f"crashlog_test: 找不到 32 位解释器 {exe}（设 PY32 覆盖）")
    # os.execv 在 Windows 上不会给含空格的脚本路径加引号，改用 subprocess
    rc = subprocess.call([str(exe), str(Path(__file__).resolve()), *sys.argv[1:]])
    sys.exit(rc)


def build_targets() -> None:
    cmd = ["cmake", "--build", str(ROOT / "build"), "--config", "Release",
           "--target", "crashlog", "crashlog_crashtest"]
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit("crashlog_test: 构建失败\n" + r.stdout[-3000:] + r.stderr[-3000:])


def fresh_dir(name: str) -> Path:
    stamp = time.strftime("%Y%m%d_%H%M%S")
    d = ROOT / "work" / "crashlog_test" / f"{name}_{stamp}_{os.getpid()}"
    shutil.rmtree(d, ignore_errors=True)
    d.mkdir(parents=True)
    return d


def read_log(d: Path) -> tuple[Path, str]:
    logs = sorted(glob.glob(str(d / "crash_*.log")))
    if not logs:
        sys.exit(f"crashlog_test: {d} 下没有 crash_*.log")
    p = Path(logs[0])
    return p, p.read_text(encoding="utf-8", errors="replace")


def check(cond: bool, what: str, failures: list[str]) -> None:
    print(("PASS  " if cond else "FAIL  ") + what)
    if not cond:
        failures.append(what)


def negative_child(dll: str) -> int:
    dll_handle = ctypes.WinDLL(dll)  # noqa: F841 - DllMain 不装（无 CRASHLOG_*）
    dll_handle.crashlog_selftest_av()
    print("neg-child-ok")
    return 0


def fp_child(dll: str) -> int:
    dll_handle = ctypes.WinDLL(dll)
    try:
        dll_handle.crashlog_selftest_fp()
    except OSError as e:
        print(f"fp-child-oserror: {e}")
    print("fp-child-done")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-build", action="store_true")
    ap.add_argument("--neg-child", metavar="DLL", help=argparse.SUPPRESS)
    ap.add_argument("--fp-child", metavar="DLL", help=argparse.SUPPRESS)
    args = ap.parse_args()

    if args.neg_child:
        return negative_child(args.neg_child)
    if args.fp_child:
        return fp_child(args.fp_child)

    relaunch_as_x86()
    if not args.no_build:
        build_targets()
    if not DLL.exists():
        sys.exit(f"crashlog_test: 缺少 {DLL}（先构建 crashlog target）")

    failures: list[str] = []
    d = fresh_dir("unit")
    os.environ["CRASHLOG_DIR"] = str(d)
    os.environ["CRASHLOG_DUMP"] = "1"
    os.environ["CRASHLOG_DIALOG"] = "1"
    for k in ("CRASHLOG_LOG", "CRASHLOG_FULL", "CRASHLOG_DUMP_ALL"):
        os.environ.pop(k, None)

    dll = ctypes.WinDLL(str(DLL))
    dll.crashlog_selftest_av()
    time.sleep(0.2)
    dll.crashlog_selftest_raise()
    time.sleep(0.3)

    # 对话框监视：临时弹一个 #32770，正文应被写进同一份日志（覆盖 Pascal raise 的兜底）。
    box = {}

    def show_box() -> None:
        box["rc"] = ctypes.windll.user32.MessageBoxW(
            0, "hello-crashlog", "crashlog-test", 0x1)  # MB_OKCANCEL

    th = threading.Thread(target=show_box, daemon=True)
    th.start()
    hwnd = 0
    for _ in range(30):
        hwnd = ctypes.windll.user32.FindWindowW("#32770", "crashlog-test")
        if hwnd:
            break
        time.sleep(0.1)
    time.sleep(0.8)
    if hwnd:
        ctypes.windll.user32.PostMessageW(hwnd, 0x0111, 1, 0)  # WM_COMMAND IDOK
    th.join(timeout=3)

    log, text = read_log(d)
    lines = text.splitlines()
    exc = [ln for ln in lines if ln.startswith("EXC ")]
    check(len(exc) >= 2, f"两类异常都进日志（EXC={len(exc)}）", failures)

    e1 = next((ln for ln in exc if "seq=1 " in ln), "")
    check("code=0xC0000005" in e1, "seq=1 是 access violation", failures)
    check("mod=crashlog.dll" in e1, "seq=1 定位到 crashlog.dll", failures)
    check("av=write" in e1 and "fault=0x00000000" in e1, "seq=1 是写 0 地址", failures)
    e2 = next((ln for ln in exc if "seq=2 " in ln), "")
    check("p1=0xDEADBEEF" in e2, "seq=2 保留 RaiseException 参数", failures)

    check(any(ln.startswith("CTX ") and "eip=0x" in ln for ln in lines),
          "记录 CONTEXT（eip/esp/ebp）", failures)
    frames = [ln for ln in lines if ln.startswith(("FRM ", "SCN ")) and " mod=" in ln]
    check(len(frames) >= 2, f"栈扫描有模块帧（{len(frames)} 条）", failures)
    check(bool(hwnd), "对话框测试窗口出现", failures)
    check(any(ln.startswith("DLG ") and "hello-crashlog" in ln for ln in lines),
          "对话框正文进日志（Pascal raise 兜底）", failures)

    # x87 invalid（旧 “Invalid floating point operation”）必须在子进程里测：
    # 异常会穿过 ctypes 边界，主进程可能以 0xC0000090 的退出码结束。
    fpdir = fresh_dir("fp")
    fpenv = {k: v for k, v in os.environ.items() if not k.startswith("CRASHLOG_")}
    fpenv["CRASHLOG_DIR"] = str(fpdir)
    rf = subprocess.run([sys.executable, str(Path(__file__).resolve()),
                         "--fp-child", str(DLL)],
                        cwd=ROOT, env=fpenv, capture_output=True, text=True)
    fplogs = sorted(glob.glob(str(fpdir / "crash_*.log")))
    check(bool(fplogs), "FP 子进程写日志", failures)
    if fplogs:
        fpt = Path(fplogs[0]).read_text(encoding="utf-8", errors="replace")
        check("code=0xC0000090" in fpt and "note=float-invalid-operation" in fpt,
              "x87 invalid FP 记录（0xC0000090）", failures)
    print(f"INFO  FP 子进程 rc={rf.returncode}")

    dumps = sorted(glob.glob(str(d / "*.dmp")))
    check(bool(dumps), "生成 minidump", failures)
    if dumps:
        data = Path(dumps[0]).read_bytes()[:4]
        check(data == b"MDMP" and Path(dumps[0]).stat().st_size > 4096,
              f"dump 可识别（{Path(dumps[0]).name}, {Path(dumps[0]).stat().st_size} B）",
              failures)

    # 负例：干净子进程不设 CRASHLOG_*，不应产生日志
    nd = fresh_dir("negative")
    env = {k: v for k, v in os.environ.items() if not k.startswith("CRASHLOG_")}
    r = subprocess.run([sys.executable, str(Path(__file__).resolve()),
                        "--neg-child", str(DLL)],
                       cwd=nd, env=env, capture_output=True, text=True)
    check(r.returncode == 0, "负例子进程正常退出", failures)
    check("neg-child-ok" in r.stdout, "负例子进程执行到 AV 之后", failures)
    check(not glob.glob(str(nd / "crash_*.log")), "未设 CRASHLOG_DIR 时不落盘", failures)

    print(f"\nlog: {log}")
    print(f"dir: {d}")
    if failures:
        print(f"crashlog_test: FAIL ({len(failures)})")
        for f in failures:
            print("  - " + f)
        return 1
    print("crashlog_test: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
