#!/usr/bin/env python3
"""Decode entry-probe counts for the uncovered Lua binding set.

Usage:
    python tools/entryprobe/check_bindings.py --counts work/cover_game/counts.bin
    python tools/entryprobe/check_bindings.py --counts ... --expect work/coverage_uncovered_235.csv --json

Inputs:
    --counts   raw DWORD counts written by entryprobe (1,010 entries)
    --targets  work/entryprobe_lvl1/targets.json (default)
    --bindings mapping/lua-bindings.csv (name -> cfunc)
    --expect   work/coverage_uncovered_235.csv; rows with reason lua-* and a lua_name
               are the 73 bindings the custom level is supposed to cover.

Criterion:
    exit 0 iff every expected binding has count > 0; print `PASS=hit=73 miss=0`.
    Also prints helper (lua_name empty) hit counts for information only.

Boundary:
    Counts are entry hits, not behavior equivalence. A binding can be hit with
    invalid arguments and still be counted; the test level is responsible for
    supplying valid objects. Counts before the probe mount are excluded unless
    B2RTLPROBE_EARLY=1 was used.

Failure modes:
    counts file length != 4 * len(targets), unknown cfunc, or missing expect rows.
"""
from __future__ import annotations

import argparse
import csv
import json
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def load_targets(path: Path) -> list[int]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return [int(t["va"]) for t in data["targets"]]


def load_bindings(path: Path) -> dict[int, str]:
    out: dict[int, str] = {}
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            out[int(row["cfunc"], 16)] = row["lua_name"]
    return out


def load_expected(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return [
        r
        for r in rows
        if r.get("reason", "").startswith("lua-") and r.get("lua_name", "").strip()
    ]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--counts", required=True, nargs="+", type=Path)
    ap.add_argument("--targets", type=Path, default=ROOT / "work/entryprobe_lvl1/targets.json")
    ap.add_argument("--bindings", type=Path, default=ROOT / "mapping/lua-bindings.csv")
    ap.add_argument("--expect", type=Path, default=ROOT / "work/coverage_uncovered_235.csv")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    targets = load_targets(args.targets)
    by_va: dict[int, int] = {va: 0 for va in targets}
    for path in args.counts:
        blob = path.read_bytes()
        if len(blob) < 4 * len(targets):
            print(f"counts too short: {path} {len(blob)} < {4 * len(targets)}", file=sys.stderr)
            return 2
        counts = struct.unpack("<%dI" % len(targets), blob[: 4 * len(targets)])
        for va, c in zip(targets, counts):
            by_va[va] = max(by_va[va], c)
    names = load_bindings(args.bindings)
    expected = load_expected(args.expect)

    hit = miss = 0
    rows = []
    for r in expected:
        va = int(r["rva"], 16)
        name = names.get(va, r.get("lua_name", ""))
        c = by_va.get(va)
        if c is None:
            print(f"target missing from targets.json: {r['rva']} {name}", file=sys.stderr)
            return 2
        ok = c > 0
        hit += ok
        miss += not ok
        rows.append({"rva": r["rva"], "name": name, "reason": r["reason"], "count": c, "hit": ok})

    # Helpers are informational: they are the factory-downstream functions, not bindings.
    helper_rows = [
        r
        for r in csv.DictReader(args.expect.open(newline="", encoding="utf-8"))
        if r.get("reason", "").startswith("lua-") and not r.get("lua_name", "").strip()
    ]
    helper_hit = sum(1 for r in helper_rows if by_va.get(int(r["rva"], 16), 0) > 0)

    if args.json:
        print(json.dumps({"hit": hit, "miss": miss, "rows": rows,
                          "helper_hit": helper_hit, "helper_total": len(helper_rows)},
                         ensure_ascii=False, indent=2))
    else:
        for r in rows:
            flag = "HIT " if r["hit"] else "MISS"
            print(f"{flag} {r['rva']} {r['name']:<32} {r['reason']:<24} {r['count']}")
        print(f"PASS=hit={hit} miss={miss} expected={len(rows)} helpers={helper_hit}/{len(helper_rows)}")
    return 0 if miss == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
