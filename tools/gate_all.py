#!/usr/bin/env python3
"""批量门禁：对 work/rec_*/ 里每个录制跑一次 gate（抓包 + 离线重放）。

用法:
  python tools/gate_all.py [--only rec_20261028_192846] [--no-visual] [--skip-capture]

每个录制一条：kill 游戏 → 换代理 DLL → 起游戏 → 重放录制（抓 FFI）→ 杀游戏 →
离线重放（我们的 DLL）→ 判 no_crash + bounded。汇总成一张表。
"""
import argparse
import glob
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = sys.executable


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("--visual", action="store_true")
    ap.add_argument("--skip-capture", action="store_true")
    a = ap.parse_args()

    recs = []
    for d in sorted(glob.glob(os.path.join(ROOT, "work", "rec_*"))):
        ev = os.path.join(d, "events.jsonl")
        if a.only and a.only not in d:
            continue
        if not (os.path.exists(ev) and os.path.getsize(ev) > 0):
            continue
        try:   # 过滤自测留下的小录制（<3 次点击或 <50 事件）
            m = json.load(open(os.path.join(d, "meta.json"), encoding="utf-8"))
            if m.get("clicks", 0) < 3 or m.get("events", 0) < 50:
                continue
        except Exception:  # noqa: BLE001
            pass
        recs.append(ev)
    if not recs:
        print("no recordings found")
        return 1

    rows = []
    for rec in recs:
        name = os.path.basename(os.path.dirname(rec)).replace("rec_", "")
        cmd = [PY, os.path.join(ROOT, "tools", "gate.py"),
               os.path.dirname(rec), "--name", name]
        if a.visual:
            cmd.append("--visual")
        if a.skip_capture:
            cmd.append("--skip-capture")
        out = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
        path = os.path.join(ROOT, "work", f"gate_{name}.json")
        try:
            g = json.load(open(path, encoding="utf-8"))
        except Exception:  # noqa: BLE001
            rows.append((name, "ERROR", (out.stdout or out.stderr)[-120:]))
            continue
        off = g.get("offline", {})
        b = g.get("bounded", {})
        rows.append((name, g["verdict"],
                     f"calls={off.get('calls')} steps={off.get('steps')} "
                     f"bad={off.get('bodies_bad')} bounded={b.get('head')}->{b.get('tail')}"))
        print(f"[{g['verdict']}] {name}: {rows[-1][2]}")

    print("\nname                 verdict  detail")
    for r in rows:
        print(f"{r[0]:<20} {r[1]:<8} {r[2]}")
    return 0 if all(r[1] == "PASS" for r in rows) else 1


if __name__ == "__main__":
    sys.exit(main())
