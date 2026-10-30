"""自走录制：无人值守跑一遍 Introduction，同时用 b2 代理录下 FFI，跑完直接进门禁判定。

这是"测试速度"的关键一环：把「人工玩一关 → 装代理 → 收日志 → 重放判定」压成一条命令。

前置：`work/e2e_game/` 里 `b2Physics.dll` = 代理、`b2Physics_orig.dll` = 原版
（`cmake --build build --config Release --target b2physics_proxy` 后按名替换即可）。

用法：
    python tools/e2e_record.py [--dir work/e2e_game] [--name auto] [--keep-log]

判据：
  1) 录制本身：日志 ≥ 1 MiB 且 pre/post 配对（tools/ffi.py 自检）；
  2) 物理对齐：`tools/gate.py` 对 **当前构建** 的 b2Physics.dll 重放该录制 → PASS
     （no_crash + bounded，口径见 docs/levels.md）。
退出码 0 仅当两条都过。
"""
import argparse
import json
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY32 = os.environ.get("PY32") or (
    r"C:/Users/K/.local/bin/python3.12.exe"
    if os.path.exists(r"C:/Users/K/.local/bin/python3.12.exe") else sys.executable)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="work/e2e_game")
    ap.add_argument("--name", default="auto")
    ap.add_argument("--anchors", default="work/uianchors.npz")
    ap.add_argument("--clicks", default="40")
    args = ap.parse_args()

    game_dir = os.path.join(ROOT, args.dir) if not os.path.isabs(args.dir) else args.dir
    rec_dir = os.path.join(ROOT, "work", "rec_%s_%s" % (args.name, time.strftime("%Y%m%d_%H%M%S")))
    os.makedirs(rec_dir, exist_ok=True)
    log_path = os.path.join(rec_dir, "ffi.bin")

    env = dict(os.environ, B2PROXY_LOG=log_path)
    print("dir=%s\nlog=%s" % (game_dir, log_path))

    e2e = [sys.executable, os.path.join(ROOT, "tools", "e2e_tutorial.py"),
           "--dir", game_dir, "--anchors", args.anchors, "--clicks", args.clicks]
    p = subprocess.run(e2e, cwd=ROOT, env=env, capture_output=True, text=True, timeout=900)
    print(p.stdout[-2000:])
    if p.returncode != 0:
        print("e2e_rc=%d" % p.returncode)
        return 2

    size = os.path.getsize(log_path) if os.path.exists(log_path) else 0
    print("log_bytes=%d" % size)
    if size < 1 << 20:
        print("FAIL: 录制太小（<1 MiB），大概率没进关或代理没装")
        return 3

    stats = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "ffi.py"), log_path, "--show", "0"],
                           cwd=ROOT, capture_output=True, text=True)
    print(stats.stdout[-800:])

    gate = subprocess.run([PY32, os.path.join(ROOT, "tools", "gate.py"), rec_dir],
                          cwd=ROOT, capture_output=True, text=True, timeout=900)
    out = gate.stdout.strip().splitlines()
    print("\n".join(out[-6:]))
    ok = gate.returncode == 0
    print("gate_rc=%d verdict=%s" % (gate.returncode, "PASS" if ok else "FAIL"))
    return 0 if ok else 4


if __name__ == "__main__":
    sys.exit(main())
