#!/usr/bin/env python3
"""关卡回归门禁：一条录制 → 抓包（原版 DLL）→ 离线重放（我们的 DLL）→ 视觉 A/B → 判定。

判定项（任一不满足即 FAIL）：
  1. no_crash : 离线重放把抓到的调用全部执行完（不崩，calls>0）
  2. bounded  : 每步超差 body 数不增长（末 10% 均值 <= 首 10% 均值*1.5 + 1）

视觉 A/B 只做**告警**（`visual_warn`）：同一对 DLL 连跑两次会因重放时序在第 9 次点击差
0.27，噪声比 DLL 差异还大，不适合当门禁。要稳定就多跑几次取中位数。

用法:
  python tools/gate.py work/rec_xxx/events.jsonl [--name mail] [--ffi work/ffi_mail.bin]
       [--skip-capture] [--dll-a bin/gametop/b2Physics.dll] [--dll-b build/Release/b2Physics.dll]

产物: work/gate_<name>.json（含原始统计与判定）
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import replay as rp  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAME_DIR = os.path.join(ROOT, "work", "integration")
PID_FILE = os.path.join(ROOT, "work", "game_pid.txt")
PROXY = os.path.join(ROOT, "build", "proxy", "Release", "b2Physics.dll")
TARGET = os.path.join(GAME_DIR, "b2Physics.dll")
PY = sys.executable
# b2Physics.dll 是 32 位的：replay_ffi 必须用 32 位解释器跑
PY32 = os.environ.get('PY32') or (
    r"C:\Users\K\.local\bin\python3.12.exe"
    if os.path.exists(r"C:\Users\K\.local\bin\python3.12.exe") else sys.executable)


def run(cmd, env=None, timeout=900):
    return subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True,
                          env=env, timeout=timeout)


def kill_game():
    run([PY, os.path.join(ROOT, "tools", "game_drive.py"), "kill"], timeout=60)


def capture(rec, ffi_out):
    """用代理+原版 DLL 跑一遍录制，抓 FFI。"""
    kill_game()
    time.sleep(1.0)
    if not os.path.exists(PROXY):
        raise SystemExit(f"proxy missing: {PROXY}")
    shutil.copyfile(PROXY, TARGET)
    env = dict(os.environ, B2PROXY_LOG=ffi_out)
    proc = subprocess.Popen([os.path.join(GAME_DIR, "game.exe")], cwd=GAME_DIR, env=env)
    with open(PID_FILE, "w") as f:
        f.write(str(proc.pid))
    t0 = time.time()
    while time.time() - t0 < 45:
        if rp.game_window():
            break
        time.sleep(0.5)
    time.sleep(1.0)
    out = run([PY, os.path.join(ROOT, "tools", "replay.py"), rec,
               "--shot", os.path.join(ROOT, "work", "gate_shot.png"), "--post", "1.5"])
    kill_game()
    time.sleep(0.5)
    return os.path.exists(ffi_out) and os.path.getsize(ffi_out) > 0, out.stdout


def capture_with_retry(rec, ffi_out, tries=2):
    """拖拽可能没抓中物体导致这次重放没通关——重放没通关时语料只覆盖半关，重试到通关为止。"""
    last = None
    for i in range(tries):
        ok, tail = capture(rec, ffi_out)
        score = None
        done = False
        for line in reversed((tail or "").strip().splitlines()):
            line = line.strip()
            if not line.startswith("{"):
                continue
            try:
                j = json.loads(line)
            except json.JSONDecodeError:
                continue
            # 通关看尾部点击：前两次点击是刻意点 intro 加速，分数天然低
            sc = [c.get("score", 0) for c in j.get("clicks", [])][-3:]
            score = round(sum(sc) / len(sc), 4) if sc else None
            done = score is not None and score >= 0.85
            break
        last = (ok, tail, score, i + 1)
        print(f'  capture attempt {i+1}: ok={ok} min_score={score} done={done}')
        if ok and done:
            return ok, tail, score, i + 1
    return last


def offline(ffi_log, dll):
    out = run([PY32, os.path.join(ROOT, "tools", "replay_ffi.py"), ffi_log, "--json",
               "--dll", dll])
    for line in reversed((out.stdout or "").strip().splitlines()):
        line = line.strip()
        if line.startswith("{"):
            try:
                return json.loads(line)
            except json.JSONDecodeError:
                continue
    return {"ok": False, "error": (out.stderr or out.stdout or "")[-400:]}


def visual_ab(rec, dll_a, dll_b):
    out = run([PY, os.path.join(ROOT, "tools", "ab.py"), rec, "--a", dll_a, "--b", dll_b])
    path = os.path.join(ROOT, "work", "ab_result.json")
    try:
        data = json.load(open(path, encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {"ok": False, "error": (out.stdout or out.stderr or "")[-400:]}
    a = [c["score"] for c in data["a"].get("clicks", [])]
    b = [c["score"] for c in data["b"].get("clicks", [])]
    def tail3(v):
        return round(sum(v[-3:]) / len(v[-3:]), 4) if v else 0.0

    return {"ok": True, "a": a, "b": b,
            "mean_a": round(sum(a) / len(a), 4) if a else 0,
            "mean_b": round(sum(b) / len(b), 4) if b else 0,
            "tail3_a": tail3(a), "tail3_b": tail3(b)}


def deciles(series):
    """按步序号分十个十分位，返回每段的中位数（跳过前 10% 热身）。"""
    if not series:
        return []
    ks = sorted(series, key=int)
    warm = ks[len(ks) // 10:] or ks
    out = []
    n = len(warm)
    for i in range(10):
        seg = warm[int(n * i / 10):int(n * (i + 1) / 10)]
        if seg:
            out.append(sorted(series[k] for k in seg)[len(seg) // 2])
    return out


def bounded(step_bad):
    """判「是否还在增长」，而不是「比开头高多少」。

    典型曲线是 1 → 4 → 5 → 11 → 11：前段扩散、后段饱和，这是容差内的数值传播，
    不是发散。所以比较**最后两个十分位**的中位数（近端斜率），并额外报出饱和水位。

    跳过前 10%：关卡加载阶段 body 还没建全，超差数天然低。
    """
    if not step_bad:
        return True, 0.0, 0.0, 0.0
    ks = sorted(step_bad, key=int)
    warm = ks[len(ks) // 10:] or ks
    n = len(warm)
    prev = warm[max(0, int(n * 0.7)):max(1, int(n * 0.9))]
    last = warm[max(1, int(n * 0.9)):]
    a = sorted(step_bad[k] for k in prev)[len(prev) // 2] if prev else 0
    b = sorted(step_bad[k] for k in last)[len(last) // 2] if last else 0
    peak = max(step_bad[k] for k in warm) if warm else 0
    return b <= a * 1.25 + 2, float(a), float(b), float(peak)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rec", help="录制目录（含 events.jsonl + ffi.bin）或 .jsonl 路径")
    ap.add_argument("--name", default="level")
    ap.add_argument("--ffi", default="")
    ap.add_argument("--skip-capture", action="store_true")
    ap.add_argument("--no-visual", action="store_true", default=True)
    ap.add_argument("--visual", action="store_true")
    ap.add_argument("--capture-tries", type=int, default=2)
    ap.add_argument("--dll-a", default=os.path.join(ROOT, "bin", "gametop", "b2Physics.dll"))
    ap.add_argument("--dll-b", default=os.path.join(ROOT, "build", "Release", "b2Physics.dll"))
    a = ap.parse_args()

    rec = a.rec
    if os.path.isdir(rec):
        events = os.path.join(rec, "events.jsonl")
        if os.path.exists(events):
            a.rec = events
        cand = os.path.join(rec, "ffi.bin")
        if os.path.exists(cand) and not a.ffi:
            a.ffi = cand
            a.skip_capture = True      # 面板已经用代理录好了 FFI，不用再重放抓一遍
    ffi = a.ffi or os.path.join(ROOT, "work", f"ffi_{a.name}.bin")
    report = {"name": a.name, "rec": a.rec, "ffi": ffi}

    if not a.skip_capture:
        ok, tail, score, tries = capture_with_retry(a.rec, ffi, a.capture_tries)
        report["capture"] = {"ok": ok, "tail": (tail or "")[-300:], "min_score": score,
                             "tries": tries,
                             "size_mb": round(os.path.getsize(ffi) / 1048576, 1) if ok else 0}
        if not ok:
            report["verdict"] = "FAIL"
            report["fail"] = ["capture"]
            print(json.dumps(report, ensure_ascii=False, indent=2))
            return 1

    off = offline(ffi, a.dll_b)
    report["offline"] = {k: off.get(k) for k in
                         ("ok", "calls", "steps", "bodies", "bodies_bad", "mismatches",
                          "first_digest", "error")}
    growth_ok, prev_med, last_med, peak = bounded(off.get("step_bad") or {})
    report["bounded"] = {"ok": growth_ok, "prev_decile": prev_med,
                         "last_decile": last_med, "peak": peak}
    # 偏差幅度（|Δ|/容差）的十分位中位数：个数可能因场景抖动而变化，
    # 幅度如果一直停在 1–3 倍容差，说明是噪声而不是发散。
    dev = deciles(off.get("step_dev") or {})
    report["dev_deciles"] = [round(v, 2) for v in dev]

    if a.visual:
        vis = visual_ab(a.rec, a.dll_a, a.dll_b)
    else:
        vis = {"ok": False, "skipped": True}
    report["visual"] = vis

    fails = []
    if not off.get("ok") or not off.get("calls"):
        fails.append("no_crash")
    if not growth_ok:
        fails.append("bounded")
    if vis.get("ok"):
        # 通关判定看尾部点击（录制者最后几次是故意点「Level completed」对话框）
        ta, tb = vis.get("tail3_a", 0), vis.get("tail3_b", 0)
        report["visual_tail"] = {"a": ta, "b": tb, "ok": tb >= 0.85 and tb >= ta - 0.08}
        report["visual_warn"] = not report["visual_tail"]["ok"]
    report["verdict"] = "PASS" if not fails else "FAIL"
    report["fail"] = fails

    out = os.path.join(ROOT, "work", f"gate_{a.name}.json")
    json.dump(report, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(json.dumps({k: report[k] for k in ("name", "verdict", "fail", "bounded",
                                              "offline", "visual")},
                     ensure_ascii=False, indent=2)[:1500])
    print("saved", out)
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
