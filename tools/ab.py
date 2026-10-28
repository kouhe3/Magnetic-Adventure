#!/usr/bin/env python3
"""A/B：同一个录制，分别在两个 b2Physics.dll 下重放，逐次点击画面打分。

流程（每个 DLL 一次）：杀游戏 → 换 DLL → 启动 → 等窗口 → replay.py → 收集 JSON → 杀游戏。

用法:
  python tools/ab.py <recording.jsonl> [--a bin/gametop/b2Physics.dll] [--b build/Release/b2Physics.dll]
                     [--out work/ab_result.json]

注意：录制必须从「菜单」开始（重放会从当前画面接着操作）。参照帧是录制时那一版 DLL 的画面，
所以控制组应把录制时用的那一版放在 --a。
"""
import argparse
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import replay as rp  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAME_DIR = os.path.join(ROOT, "work", "integration")
PID_FILE = os.path.join(ROOT, "work", "game_pid.txt")
TARGET = os.path.join(GAME_DIR, "b2Physics.dll")
PY = sys.executable


def kill_game():
    subprocess.run([PY, os.path.join(ROOT, "tools", "game_drive.py"), "kill"],
                   cwd=ROOT, capture_output=True)


def run_one(dll, rec, tag, timeout=45):
    kill_game()
    time.sleep(1.0)
    with open(dll, "rb") as f:
        data = f.read()
    with open(TARGET, "wb") as f:
        f.write(data)
    proc = subprocess.Popen([os.path.join(GAME_DIR, "game.exe")], cwd=GAME_DIR)
    with open(PID_FILE, "w") as f:
        f.write(str(proc.pid))
    t0 = time.time()
    while time.time() - t0 < timeout:
        if rp.game_window():
            break
        time.sleep(0.5)
    else:
        kill_game()
        return {"dll": dll, "ok": False, "error": "window timeout"}
    time.sleep(1.0)                      # 让菜单动画稳定一点
    out = subprocess.run([PY, os.path.join(ROOT, "tools", "replay.py"), rec,
                          "--shot", os.path.join(ROOT, "work", f"ab_{tag}_end.png"),
                          "--post", "1.5"],
                         cwd=ROOT, capture_output=True, text=True)
    kill_game()
    line = (out.stdout or "").strip().splitlines()
    if not line:
        return {"dll": dll, "ok": False, "error": (out.stderr or "")[-300:]}
    try:
        res = json.loads(line[-1])
    except json.JSONDecodeError:
        return {"dll": dll, "ok": False, "error": line[-1][:300]}
    res["dll"] = dll
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rec")
    ap.add_argument("--a", default=os.path.join(ROOT, "bin", "gametop", "b2Physics.dll"))
    ap.add_argument("--b", default=os.path.join(ROOT, "build", "Release", "b2Physics.dll"))
    ap.add_argument("--out", default=os.path.join(ROOT, "work", "ab_result.json"))
    a = ap.parse_args()

    ra = run_one(a.a, a.rec, "a")
    rb = run_one(a.b, a.rec, "b")

    def clicks(r):
        return {c["click"]: c["score"] for c in r.get("clicks", [])}

    def tail(r, k=3):
        sc = [c["score"] for c in r.get("clicks", [])][-k:]
        return round(sum(sc) / len(sc), 4) if sc else 0.0

    ca, cb = clicks(ra), clicks(rb)
    common = sorted(set(ca) & set(cb))
    print(f'A {os.path.basename(os.path.dirname(a.a)):<12} events={ra.get("events")} '
          f'mean={sum(ca.values())/len(ca) if ca else None:.3f} tail3={tail(ra)}')
    print(f'B {os.path.basename(os.path.dirname(a.b)):<12} events={rb.get("events")} '
          f'mean={sum(cb.values())/len(cb) if cb else None:.3f} tail3={tail(rb)}')
    print(f'{"click":>5} {"A":>7} {"B":>7} {"delta":>7}')
    for i in common:
        print(f"{i:>5} {ca[i]:>7.4f} {cb[i]:>7.4f} {cb[i]-ca[i]:>+7.4f}")
    if common:
        worse = [(i, cb[i] - ca[i]) for i in common]
        worst = min(worse, key=lambda t: t[1])
        print(f'worst: click {worst[0]} delta {worst[1]:+.4f}')
    json.dump({"a": ra, "b": rb, "tail3_a": tail(ra), "tail3_b": tail(rb),
               "dll_a": a.a, "dll_b": a.b},
              open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("saved", a.out)


if __name__ == "__main__":
    main()
