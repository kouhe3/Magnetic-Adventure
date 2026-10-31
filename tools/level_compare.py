"""Compare captured original Add_* calls with our host's lua_probe logs.

Usage:
  python tools/level_compare.py --capture work/hostcapture --probe work/lua_probe --levels 1-52

capture lvlNN.jsonl is 1-based level order (tools/level_capture.py); probe
lvlNN.jsonl is 0-based (level 1 = lvl00.jsonl, F191). Only Add_* calls take
part: the original capture logs every factory call, while the probe log also
contains setters/commands.

Criteria: per level, the ordered Add_* name sequence must be identical.
Boundaries: compares names only, not arguments (arguments are checked in the
probe vs host JSONL separately).
"""
import argparse
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def cap_names(path):
    return [json.loads(l)["tag"] for l in open(path, encoding="utf-8") if l.strip()]


def probe_names(path):
    out = []
    for l in open(path, encoding="utf-8"):
        if not l.strip():
            continue
        d = json.loads(l)
        c = d.get("call", "")
        if c.startswith("Add_"):
            out.append(c)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--capture", default=os.path.join(ROOT, "work", "hostcapture"))
    ap.add_argument("--probe", default=os.path.join(ROOT, "work", "lua_probe"))
    ap.add_argument("--levels", default="1-52")
    a = ap.parse_args()
    m = re.match(r"(\d+)-(\d+)$", a.levels)
    levels = list(range(int(m.group(1)), int(m.group(2)) + 1)) if m else [int(a.levels)]

    ok = miss = 0
    for lv in levels:
        cp = os.path.join(a.capture, "lvl%02d.jsonl" % lv)
        pp = os.path.join(a.probe, "lvl%02d.jsonl" % (lv - 1))
        if not os.path.exists(cp):
            print("lvl%02d SKIP (no capture)" % lv, flush=True)
            continue
        if not os.path.exists(pp):
            print("lvl%02d SKIP (no probe)" % lv, flush=True)
            continue
        c, p = cap_names(cp), probe_names(pp)
        if c == p:
            print("lvl%02d OK cap=%d probe=%d" % (lv, len(c), len(p)), flush=True)
            ok += 1
            continue
        miss += 1
        i = next((k for k in range(min(len(c), len(p))) if c[k] != p[k]), min(len(c), len(p)))
        print("lvl%02d DIFF cap=%d probe=%d first=%d cap=%r probe=%r" % (
            lv, len(c), len(p), i,
            c[i] if i < len(c) else None, p[i] if i < len(p) else None), flush=True)
    print("summary ok=%d diff=%d" % (ok, miss))


if __name__ == "__main__":
    main()
