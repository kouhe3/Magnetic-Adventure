"""把 work/sweep_x87.jsonl 与 docs/levels.md 的关卡映射合并成表格。"""
import json
import os
import re
import struct

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def magic(rec):
    p = os.path.join(ROOT, "work", rec, "ffi.bin")
    try:
        with open(p, "rb") as fh:
            m = struct.unpack("<8s", fh.read(8))[0]
        return m.rstrip(b"\0").decode("ascii", "replace")
    except OSError:
        return "?"


def level_map():
    """docs/levels.md 里形如 | name | `rec_xxx` | ... |"""
    out = {}
    try:
        text = open(os.path.join(ROOT, "docs", "levels.md"), encoding="utf-8").read()
    except OSError:
        return out
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        m = re.search(r"`(rec_\d{8}_\d{6})`", line)
        if not m:
            continue
        name = line.split("|")[1].strip()
        out[m.group(1)] = name
    return out


def main():
    lv = level_map()
    rows = []
    with open(os.path.join(ROOT, "work", "sweep_x87.jsonl"), encoding="utf-8") as fh:
        for line in fh:
            try:
                rows.append(json.loads(line))
            except Exception:
                pass
    rows.sort(key=lambda r: r["rec"])
    print(f"{'level':<28}{'rec':<22}{'fmt':<9}{'steps':>7}{'bad':>9}{'first':>7}{'exact':>7}{'stale':>6}")
    clean = v01 = 0
    for r in rows:
        if r.get("skip"):
            print(f"{lv.get(r['rec'], '?'):<28}{r['rec']:<22}{magic(r['rec']):<9}"
                  f"{'-':>7}{'SKIP':>9}{'-':>7}{'-':>7}{'-':>6}")
            continue
        fmt = magic(r["rec"])
        name = lv.get(r["rec"], "?(未登记)")
        print(f"{name:<28}{r['rec']:<22}{fmt:<9}{r['steps']:>7}{r['bad']:>9}"
              f"{str(r['first_tol']):>7}{str(r['first_exact']):>7}{str(r.get('stale')):>6}")
        if fmt.endswith("02") and not r["bad"]:
            clean += 1
        if fmt.endswith("01"):
            v01 += 1
    print(f"\nv02 且 0 差异: {clean}    v01 旧格式: {v01}    总记录: {len(rows)}")


if __name__ == "__main__":
    main()
