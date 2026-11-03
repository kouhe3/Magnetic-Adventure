#!/usr/bin/env python3
"""Compare two state-transition traces produced by `direct_drive.py --trace`.

Trace format (JSONL): one row per state change, e.g.
  {"t_ms": 0,    "state": "boot",  "lm30": null, ...}
  {"t_ms": 14200,"state": "menu",  "lm30": 2,    ...}
  {"t_ms": 15400,"state": "level", "index": 1,  ...}
  {"t_ms": 21000,"state": "exit",  ...}

Criterion: same state sequence AND every transition time within `--tol-ms`
of the other run (t is relative to process start).  Exit 0 = PASS.

Usage:
  python tools/trace_diff.py A.jsonl B.jsonl [--tol-ms 300]

Boundary: compares only the states the sampler observes (boot/menu/level/exit);
it does not inspect pixels or in-level events.
"""
import argparse
import json
import sys


def load(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("a")
    ap.add_argument("b")
    ap.add_argument("--tol-ms", type=int, default=300)
    a = ap.parse_args()
    ra, rb = load(a.a), load(a.b)
    if not ra or not rb:
        print("empty trace", file=sys.stderr)
        return 2
    sa = [r["state"] for r in ra]
    sb = [r["state"] for r in rb]
    print("A:", " ".join("%s@%d" % (r["state"], r["t_ms"]) for r in ra))
    print("B:", " ".join("%s@%d" % (r["state"], r["t_ms"]) for r in rb))
    issues = []
    if sa != sb:
        issues.append("state sequence differs: %s vs %s" % (sa, sb))
    else:
        for i, (x, y) in enumerate(zip(ra, rb)):
            d = x["t_ms"] - y["t_ms"]
            print("  %-5s tA=%6d tB=%6d dt=%+5d" % (x["state"], x["t_ms"],
                                                    y["t_ms"], d))
            if abs(d) > a.tol_ms:
                issues.append("%s dt=%+d > tol %d" % (x["state"], d, a.tol_ms))
    for msg in issues:
        print("DIFF", msg)
    print("PASS" if not issues else "FAIL")
    return 0 if not issues else 1


if __name__ == "__main__":
    sys.exit(main())
