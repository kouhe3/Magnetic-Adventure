"""全量重放：用当前构建跑一遍所有 `work/rec_*/ffi.bin`，写 `work/sweep.jsonl`。

为什么是它而不是 `gate.py`：批量场景不需要抓包（录制早就在面板里录好）、也不需要视觉 A/B；
需要的是**同一构建、同一判据、一行一份录制**的表，外加能回答「这行出自哪个构建」的指纹。

用法:
  python tools/sweep.py                # 续跑：只补当前构建缺失的行
  python tools/sweep.py --only rec_20261029_134434
  python tools/sweep.py --force        # 忽略已有行，全部重跑
  python tools/sweep.py --dll build/vc9/b2Physics.dll

判定口径与 tools/gate.py 一致：
  - 可判定 = 日志 magic ≥ B2FFI02（F87）；v01 行记 `UNUSABLE`，不重放；
  - `bounded` = 末两个十分位中位数 ≤ 前段×1.25+2（F65）；
  - 每行带 build 指纹（DLL md5 + /arch + /fp），md5 变了旧行自动作废重跑。
"""
import argparse
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import instr  # noqa: E402

PY32 = os.environ.get("PY32") or (
    r"C:/Users/K/.local/bin/python3.12.exe"
    if os.path.exists(r"C:/Users/K/.local/bin/python3.12.exe") else sys.executable)
OUT = os.path.join(ROOT, "work", "sweep.jsonl")
MIN_LOG_BYTES = 1 << 20          # 停在菜单/对话关的极小日志没有物理量


def recordings():
    work = os.path.join(ROOT, "work")
    return sorted(d for d in os.listdir(work)
                  if d.startswith("rec_") and
                  os.path.exists(os.path.join(work, d, "ffi.bin")))


def load_rows():
    rows = {}
    if not os.path.exists(OUT):
        return rows
    for line in open(OUT, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            continue
        rows[r["rec"]] = r
    return rows


def save(rows):
    with open(OUT, "w", encoding="utf-8") as fh:
        for k in sorted(rows):
            fh.write(json.dumps(rows[k], ensure_ascii=False) + "\n")


def fresh(row, md5):
    """这行还能用吗：重放行必须出自同一个 DLL；不可判定/太小的行与构建无关。"""
    if row.get("verdict") in ("UNUSABLE", "SKIP"):
        return True
    return (row.get("build") or {}).get("md5") == md5


def replay(ffi, dll):
    p = subprocess.run([PY32, os.path.join(ROOT, "tools", "replay_ffi.py"), ffi,
                        "--json", "--dll", dll],
                       cwd=ROOT, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    for line in reversed(p.stdout.splitlines()):
        if line.startswith("{"):
            try:
                return json.loads(line)
            except json.JSONDecodeError:
                continue
    return {"ok": False, "error": (p.stderr or p.stdout or "")[-400:]}


def build_row(rec, dll, fp):
    """跑一份录制并算出它那一行（纯函数：不读写共享状态，可并发）。"""
    ffi = os.path.join(ROOT, "work", rec, "ffi.bin")
    size = os.path.getsize(ffi)
    magic = instr.log_magic(ffi)
    row = {"rec": rec, "size": size, "magic": magic, "build": fp}
    if not instr.log_usable(magic):
        row.update({"usable": False, "verdict": "UNUSABLE",
                    "why": "v01 日志缺返回值/出参且 dump 仅 64B（F87）"})
    elif size < MIN_LOG_BYTES:
        row.update({"usable": False, "verdict": "SKIP", "why": "日志过小（停在菜单/对话）"})
    else:
        t0 = time.time()
        r = replay(ffi, dll)
        growth_ok, prev, last, peak = instr.bounded(r.get("step_bad") or {})
        dev = instr.deciles(r.get("step_dev") or {})
        row.update({
            "usable": True,
            "calls": r.get("calls"), "steps": r.get("steps"),
            "bodies": r.get("bodies"), "bad": r.get("bodies_bad"),
            "mismatches": r.get("mismatches"),
            "first_tol": (r.get("first_digest") or {}).get("step"),
            "first_tol_field": (r.get("first_digest") or {}).get("field"),
            "first_exact": (r.get("first_exact") or {}).get("step"),
            "bounded": {"ok": growth_ok, "prev": prev, "last": last, "peak": peak},
            "dev_deciles": [round(v, 2) for v in dev],
            "flags": r.get("flags_groups") or {},
            "flags_only": r.get("flags_only", 0),
            "stale": r.get("stale_body"),
            "error": r.get("error"),
            "secs": round(time.time() - t0, 1),
        })
        ok = bool(r.get("ok") and r.get("calls") and growth_ok)
        row["verdict"] = "PASS" if ok else "FAIL"
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--dll", default=os.path.join(ROOT, "build", "Release", "b2Physics.dll"))
    ap.add_argument("--jobs", type=int, default=0,
                    help="并行重放的进程数（0 = min(8, CPU)）；每条录制一个子进程")
    a = ap.parse_args()

    fp = instr.fingerprint(a.dll)
    print(f"build: md5={fp['md5']} arch={fp['arch']} fp={fp['fp']} match={fp['match']}",
          flush=True)
    if not fp["match"]:
        print("warn: DLL 与 build/build_info.json 不匹配（arch/fp 未知）；"
              "先 cmake --build build --config Release", flush=True)

    rows = load_rows()
    # UNUSABLE/SKIP 行没有测量值，指纹跟着本次运行走；有数字的行只在 md5 相同时保留
    for rec, row in rows.items():
        if row.get("verdict") in ("UNUSABLE", "SKIP"):
            row["build"] = fp
    recs = [r for r in recordings() if a.only in r]
    todo = [r for r in recs if a.force or r not in rows or not fresh(rows[r], fp["md5"])]

    prev_secs = {r: (rows.get(r, {}).get("secs") or 0) for r in todo}
    todo.sort(key=lambda r: -prev_secs[r])          # 长任务先跑，缩短尾巴
    jobs = a.jobs or min(8, os.cpu_count() or 4)
    print(f"{len(recs)} recordings, {len(todo)} to run, jobs={jobs}", flush=True)

    t_start = time.time()
    done = 0
    with ThreadPoolExecutor(max_workers=jobs) as ex:
        futs = {ex.submit(build_row, rec, a.dll, fp): rec for rec in todo}
        for fut in as_completed(futs):
            rec = futs[fut]
            row = fut.result()
            rows[rec] = row
            save(rows)
            done += 1
            b = row.get("bounded") or {}
            elapsed = time.time() - t_start
            eta = elapsed / done * (len(todo) - done) if done else 0
            print(f"[{done}/{len(todo)}] {rec:<26}{row['verdict']:<9}"
                  f"steps={row.get('steps')} bad={row.get('bad')} "
                  f"first_exact={row.get('first_exact')} "
                  f"bounded={b.get('prev')}->{b.get('last')} {row.get('secs', 0)}s "
                  f"(elapsed {elapsed/60:.1f}m, eta {eta/60:.1f}m)", flush=True)

    save(rows)
    print(f"SWEEP DONE -> {os.path.relpath(OUT, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
