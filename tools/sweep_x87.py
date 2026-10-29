"""用当前 build/Release/b2Physics.dll 全量重跑所有录制，输出 JSONL。

用途：x87 构建切换后刷新 docs/levels.md 的数字（F82）。
"""
import json
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY32 = r"C:/Users/K/.local/bin/python3.12.exe"
OUT = os.path.join(ROOT, "work", "sweep_x87.jsonl")


def main():
    recs = sorted(d for d in os.listdir(os.path.join(ROOT, "work"))
                  if d.startswith("rec_") and
                  os.path.exists(os.path.join(ROOT, "work", d, "ffi.bin")))
    done = set()
    if os.path.exists(OUT):
        for line in open(OUT, encoding="utf-8"):
            try:
                done.add(json.loads(line)["rec"])
            except Exception:
                pass
    with open(OUT, "a", encoding="utf-8") as fh:
        for rec in recs:
            if rec in done:
                continue
            ffi = os.path.join(ROOT, "work", rec, "ffi.bin")
            size = os.path.getsize(ffi)
            if size < 1 << 20:          # 停在菜单/对话的 0 字节或极小日志
                fh.write(json.dumps({"rec": rec, "skip": "small", "size": size}) + "\n")
                fh.flush()
                continue
            t0 = time.time()
            p = subprocess.run([PY32, os.path.join(ROOT, "tools", "replay_ffi.py"),
                                ffi, "--json"], capture_output=True, text=True,
                               encoding="utf-8", errors="replace")
            line = next((l for l in reversed(p.stdout.splitlines()) if l.startswith("{")), "{}")
            r = json.loads(line)
            rec_out = {"rec": rec, "size": size, "secs": round(time.time() - t0, 1),
                       "calls": r.get("calls"), "steps": r.get("steps"),
                       "bad": r.get("bodies_bad"),
                       "first_tol": (r.get("first_digest") or {}).get("step"),
                       "first_exact": (r.get("first_exact") or {}).get("step"),
                       "stale": r.get("stale_body"),
                       "flags": r.get("flags_groups")}
            fh.write(json.dumps(rec_out) + "\n")
            fh.flush()
            print(f'{rec:<28} bad={rec_out["bad"]} steps={rec_out["steps"]} '
                  f'first={rec_out["first_tol"]} {rec_out["secs"]}s', flush=True)
    print("SWEEP DONE", len(recs))


if __name__ == "__main__":
    main()
