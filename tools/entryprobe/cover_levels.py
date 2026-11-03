#!/usr/bin/env python3
"""Per-level entry-probe coverage census with the retail game.

Runs one fresh game process per dispatcher level on a private desktop, with the
1,010-target entryprobe installed from the b2 proxy DllMain
(B2RTLPROBE_EARLY=1), then unions the per-level counters against a historical
union table.

Usage (any 64-bit Python; the child is the 32-bit interpreter):
  python tools/entryprobe/cover_levels.py --levels 0-2 --aa
  python tools/entryprobe/cover_levels.py --levels 0-51 --resume
  python tools/entryprobe/cover_levels.py --report-only

Criterion:
  per level: `ENTRY installed=1010 failed=0`, counts=4,040 B, positive controls
  0x5afcc0 / 0x57a000 / 0x58e5a0 all hit>0; --aa runs every selected level twice
  and requires identical hit>0 sets; the union reports new hits and the
  remaining functions grouped by category.

Coverage boundary:
  * dispatcher indices 0..51, one process per level (level init + idle window);
  * no input drive: magnet/hint/switch interactions are not covered;
  * counters are written every ENTRY_MS=200 ms; at most 200 ms before exit is lost;
  * only the 1,010 targets in --targets; the 2 skipped 1-byte nullsubs are outside.

Failure conditions:
  * PY32 / direct_drive / entryprobe.dll missing; target count != 1010;
  * direct_drive nonzero or its level row not ok;
  * entry.log installed != 1010, counts size mismatch, or a positive control is 0.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import struct
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
TOOLS = ROOT / "tools"
DEFAULT_PY32 = r"C:/Users/K/.local/bin/python3.12.exe"
POSITIVE = (0x5AFCC0, 0x57A000, 0x58E5A0)
ENTRY_RE = re.compile(r"ENTRY installed=(\d+) failed=(\d+) targets=(\d+)")


def parse_levels(spec: str) -> list[int]:
    out: list[int] = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-", 1)
            out.extend(range(int(a), int(b) + 1))
        else:
            out.append(int(part))
    return [i for i in out if 0 <= i < 52]


def load_targets(path: Path) -> list[int]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return [int(t["va"]) for t in data["targets"]]


def load_counts(path: Path, targets: list[int], n: int) -> tuple[list[int], list[int]]:
    """Return (all counts, hit VAs) from one counts.bin."""
    vals = struct.unpack("<%dI" % n, path.read_bytes())
    return list(vals), [va for va, c in zip(targets, vals) if c]


def md5(path: Path) -> str:
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_drive(path: Path) -> tuple[dict | None, dict | None]:
    """Return (level_row, summary_row) from a direct_drive JSONL."""
    level = None
    summary = None
    if not path.exists():
        return level, summary
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if obj.get("event") == "summary":
            summary = obj
        elif "index" in obj:
            level = obj
    return level, summary


def run_one(idx: int, tag: str, args) -> dict:
    out_dir: Path = args.out_dir
    counts = out_dir / f"lvl{idx:02d}_{tag}_counts.bin"
    entry_log = out_dir / f"lvl{idx:02d}_{tag}_entry.log"
    drive_out = out_dir / f"lvl{idx:02d}_{tag}_drive.jsonl"
    for p in (counts, entry_log, drive_out):
        if p.exists():
            p.unlink()

    env = dict(os.environ)
    for key in list(env):
        if key in ("B2PROXY_LOG", "B2PROXY_HOT") or key.startswith("B2CI_"):
            env.pop(key, None)
    env["B2RTLPROBE_DLL"] = str(args.entryprobe)
    env["ENTRY_OUT"] = str(counts)
    env["ENTRY_LOG"] = str(entry_log)
    env["ENTRY_MS"] = "200"
    env["B2RTLPROBE_EARLY"] = "1"

    cmd = [
        args.py32, str(TOOLS / "direct_drive.py"),
        "--dir", str(args.dir),
        "--levels", str(idx),
        "--timeout", str(args.timeout),
        "--gap", str(args.gap),
        "--exit-mode", "clean",
        "--out", str(drive_out),
    ]
    t0 = time.time()
    try:
        p = subprocess.run(cmd, env=env, capture_output=True, text=True,
                           timeout=args.timeout + 90)
        rc = p.returncode
        err = (p.stderr or "")[-600:]
    except subprocess.TimeoutExpired as exc:
        rc = -9
        err = f"subprocess timeout: {exc}"
    ms = int((time.time() - t0) * 1000)

    row: dict = {"level": idx, "tag": tag, "rc": rc, "ms": ms,
                 "counts": str(counts), "entry_log": str(entry_log),
                 "drive": str(drive_out), "status": "ERROR", "reason": ""}
    if rc != 0:
        row["reason"] = "direct_drive failed"
        row["error"] = err
        return row

    level_row, summary = read_drive(drive_out)
    if not level_row or not level_row.get("ok"):
        row["reason"] = "level row not ok"
        row["level_row"] = level_row
        return row
    if summary and summary.get("fail"):
        row["reason"] = "summary fail=%s" % summary.get("fail")
        return row

    text = entry_log.read_text(encoding="utf-8", errors="replace") if entry_log.exists() else ""
    m = ENTRY_RE.search(text)
    if not m:
        row["reason"] = "no ENTRY line"
        row["entry_text"] = text[-300:]
        return row
    installed, failed, targets = map(int, m.groups())
    row.update(installed=installed, failed=failed, targets=targets)
    if installed != 1010 or failed != 0 or targets != args.ntargets:
        row["reason"] = "entry install mismatch"
        return row

    if not counts.exists() or counts.stat().st_size != 4 * args.ntargets:
        row["reason"] = "counts size mismatch"
        row["counts_bytes"] = counts.stat().st_size if counts.exists() else -1
        return row
    vals, hits = load_counts(counts, args.targets, args.ntargets)
    row["nonzero"] = len(hits)
    row["total"] = sum(vals)
    row["positive"] = {hex(va): vals[args.targets.index(va)]
                       for va in POSITIVE if va in args.targets}
    missing = [hex(va) for va in POSITIVE if va in args.targets
               and vals[args.targets.index(va)] == 0]
    if missing:
        row["reason"] = "positive control zero: " + ",".join(missing)
        return row
    row["status"] = "OK"
    row["hit_set"] = hits
    return row


def load_union(path: Path) -> tuple[dict[int, dict], list[str]]:
    rows: dict[int, dict] = {}
    order: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        parts = line.split(",")
        if parts[0] == "rva":
            continue
        rva = int(parts[0], 16)
        rows[rva] = {"rva": parts[0], "class": parts[1], "category": parts[2],
                     "mechanisms": parts[3], "hit": int(parts[4] or 0)}
        order.append(parts[0])
    return rows, order


def report(args, rows: list[dict]) -> int:
    ok: list[dict] = []
    present: set[int] = set()
    for idx in range(52):
        cpath = args.out_dir / f"lvl{idx:02d}_a_counts.bin"
        if not cpath.exists() or cpath.stat().st_size != 4 * args.ntargets:
            continue
        vals, hits = load_counts(cpath, args.targets, args.ntargets)
        pos = {hex(va): vals[args.targets.index(va)]
               for va in POSITIVE if va in args.targets}
        if any(v == 0 for v in pos.values()):
            continue
        ok.append({"level": idx, "counts": str(cpath), "hit_set": hits,
                   "nonzero": len(hits), "total": sum(vals), "positive": pos})
        present.add(idx)
    if not ok:
        print("no OK level rows", flush=True)
        return 1
    union: dict[int, int] = {va: 0 for va in args.targets}
    for r in ok:
        for va in r["hit_set"]:
            union[va] = 1
    hist, order = load_union(args.union)
    missing_hist = [va for va in args.targets if va not in hist]
    for va in missing_hist:
        hist[va] = {"rva": f"0x{va:x}", "class": "?", "category": "unknown",
                    "mechanisms": "", "hit": 0}
        order.append(hist[va]["rva"])
    new = [va for va in args.targets if union[va] and not hist[va]["hit"]]
    remaining = [va for va in args.targets if not union[va]]
    merged = sum(1 for va in args.targets if union[va] or hist[va]["hit"])
    by_cat: dict[str, int] = {}
    for va in remaining:
        c = hist[va]["category"]
        by_cat[c] = by_cat.get(c, 0) + 1
    new_by_cat: dict[str, int] = {}
    for va in new:
        c = hist[va]["category"]
        new_by_cat[c] = new_by_cat.get(c, 0) + 1

    out_csv = args.out_dir / "auto_union.csv"
    with open(out_csv, "w", encoding="utf-8", newline="") as fh:
        fh.write("rva,class,category,mechanisms,hit\n")
        for rva in order:
            row = hist[int(rva, 16)]
            hit = 1 if union.get(int(rva, 16), row["hit"]) else row["hit"]
            fh.write(f"{row['rva']},{row['class']},{row['category']},"
                     f"{row['mechanisms']},{hit}\n")

    summary = {
        "instrument": "tools/entryprobe/cover_levels.py",
        "entryprobe_md5": md5(args.entryprobe),
        "game_md5": md5(args.dir / "game.exe"),
        "targets": args.ntargets,
        "levels_ok": [r["level"] for r in ok],
        "levels_missing": [i for i in range(52) if i not in present],
        "levels_error": [{"level": r["level"], "tag": r.get("tag"),
                          "reason": r.get("reason")} for r in rows
                         if r["status"] != "OK" and r["level"] not in present],
        "positive": ok[0]["positive"],
        "new_run_hits": sum(union.values()),
        "merged_hits": merged,
        "historical_hits": sum(1 for va in args.targets if hist[va]["hit"]),
        "new": [hex(va) for va in new],
        "new_by_category": new_by_cat,
        "remaining": len(remaining),
        "remaining_by_category": by_cat,
        "aa": getattr(args, "aa_result", None),
    }
    (args.out_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("MERGED %d/%d (new run %d, +%d) remaining=%d %s" % (
        merged, args.ntargets, summary["new_run_hits"], len(new), len(remaining),
        json.dumps(by_cat, ensure_ascii=False)), flush=True)
    print("new", json.dumps(new_by_cat, ensure_ascii=False), flush=True)
    print("wrote", out_csv, "and", args.out_dir / "summary.json", flush=True)
    return 0 if not summary["levels_error"] else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--levels", default="0-51")
    ap.add_argument("--dir", default=str(ROOT / "work" / "e2e_game"))
    ap.add_argument("--out-dir", default=str(ROOT / "work" / "entryprobe_lvl1" / "auto"))
    ap.add_argument("--targets", default=str(ROOT / "work" / "entryprobe_lvl1" / "targets.json"))
    ap.add_argument("--union", default=str(ROOT / "work" / "entryprobe_lvl1" / "hits_union.csv"))
    ap.add_argument("--entryprobe", default=None,
                    help="default: <dir>/entryprobe.dll")
    ap.add_argument("--py32", default=os.environ.get("PY32", DEFAULT_PY32))
    ap.add_argument("--timeout", type=float, default=20.0)
    ap.add_argument("--gap", type=float, default=0.5)
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--aa", action="store_true",
                    help="run every selected level twice and compare hit>0 sets")
    ap.add_argument("--report-only", action="store_true")
    args = ap.parse_args()

    args.dir = Path(args.dir).resolve()
    args.out_dir = Path(args.out_dir).resolve()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    args.targets_path = Path(args.targets).resolve()
    args.union = Path(args.union).resolve()
    args.entryprobe = Path(args.entryprobe).resolve() if args.entryprobe \
        else args.dir / "entryprobe.dll"
    args.py32 = args.py32
    if not Path(args.py32).exists():
        print("PY32 not found:", args.py32, file=sys.stderr)
        return 2
    if not args.entryprobe.exists():
        print("entryprobe.dll not found:", args.entryprobe, file=sys.stderr)
        return 2
    args.targets = load_targets(args.targets_path)
    args.ntargets = len(args.targets)
    if args.ntargets != 1010:
        print("expected 1010 targets, got", args.ntargets, file=sys.stderr)
        return 2

    summary_path = args.out_dir / "summary.jsonl"
    rows: list[dict] = []
    done: dict[int, dict] = {}
    if args.resume and summary_path.exists():
        for line in summary_path.read_text(encoding="utf-8", errors="replace").splitlines():
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if obj.get("status") == "OK" and Path(obj["counts"]).exists():
                vals, hits = load_counts(Path(obj["counts"]), args.targets, args.ntargets)
                obj["hit_set"] = hits
                obj["nonzero"] = len(hits)
                obj["total"] = sum(vals)
                obj.setdefault("positive", {
                    hex(va): vals[args.targets.index(va)]
                    for va in POSITIVE if va in args.targets})
                done[obj["level"]] = obj

    wanted = parse_levels(args.levels)
    if not wanted:
        print("no levels selected", file=sys.stderr)
        return 2
    print("levels", wanted, "aa", args.aa, "resume", args.resume, flush=True)

    if args.report_only:
        if not summary_path.exists():
            print("no summary.jsonl for --report-only", file=sys.stderr)
            return 2
        for line in summary_path.read_text(encoding="utf-8", errors="replace").splitlines():
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if obj.get("status") != "OK":
                rows.append(obj)
                continue
            cpath = Path(obj["counts"])
            if not cpath.exists():
                rows.append({**obj, "status": "ERROR", "reason": "counts missing"})
                continue
            vals, hits = load_counts(cpath, args.targets, args.ntargets)
            obj["hit_set"] = hits
            obj["nonzero"] = len(hits)
            obj["total"] = sum(vals)
            obj.setdefault("positive", {
                hex(va): vals[args.targets.index(va)]
                for va in POSITIVE if va in args.targets})
            rows.append(obj)
        print("report-only rows", len(rows), flush=True)
        return report(args, rows)

    if not args.report_only:
        for idx in wanted:
            if idx in done and not args.aa:
                rows.append(done[idx])
                print(f"[{idx:02d}] resume OK nonzero={done[idx]['nonzero']}", flush=True)
                continue
            tags = ("a", "b") if args.aa else ("a",)
            got = []
            for tag in tags:
                print(f"[{idx:02d}] run {tag} ...", flush=True)
                row = run_one(idx, tag, args)
                got.append(row)
                with open(summary_path, "a", encoding="utf-8") as fh:
                    fh.write(json.dumps({k: v for k, v in row.items()
                                         if k != "hit_set"}, ensure_ascii=False) + "\n")
                print(f"    {row['status']} nonzero={row.get('nonzero')} "
                      f"rc={row['rc']} {row.get('reason', '')}", flush=True)
            if args.aa:
                a, b = got
                equal = (a["status"] == "OK" and b["status"] == "OK"
                         and set(a["hit_set"]) == set(b["hit_set"]))
                args.aa_result = getattr(args, "aa_result", {})
                args.aa_result[str(idx)] = {
                    "equal": equal,
                    "a_nonzero": a.get("nonzero"),
                    "b_nonzero": b.get("nonzero"),
                    "only_a": [hex(x) for x in sorted(set(a.get("hit_set", [])) -
                                                      set(b.get("hit_set", [])))],
                    "only_b": [hex(x) for x in sorted(set(b.get("hit_set", [])) -
                                                      set(a.get("hit_set", [])))],
                }
                print(f"    A/A set_equal={equal}", flush=True)
            rows.append(got[0])

    return report(args, rows)


if __name__ == "__main__":
    sys.exit(main())
