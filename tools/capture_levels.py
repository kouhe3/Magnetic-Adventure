#!/usr/bin/env python3
"""Capture one B2FFI02 init log per level with the retail game and compare it.

Why one process per level: the b2 proxy keeps an 8 MB user-space buffer and only
writes it when full or on DLL_PROCESS_DETACH (src/proxydll/proxy_core.c).  A
short per-level run stays below 8 MB, so a TerminateProcess would lose the whole
log.  direct_drive.py now asks the target to call kernel32!ExitProcess, which
runs DLL_PROCESS_DETACH and flushes the buffer (F349).  One process also makes
the log boundary trivial: everything before the first b2_World_Step is the
level init.

Usage (any 64-bit Python; the child is the 32-bit interpreter):
  python tools/capture_levels.py --levels 0-51
  python tools/capture_levels.py --levels 0,1,2 --resume
  python tools/capture_levels.py --levels 1 --kill      # negative control

Criterion:
  For each level with a usable recording and no known RNG caveat,
  `python tools/b2_sites.py <capture> compare <rec>/ffi.bin --stop-at-step`
  prints `TOTAL mismatches=0`.  Levels 28/36/42 are reported as RNG (the retail
  RNG state at level entry need not equal the recording's); shared dialogue
  recordings are reported as SHARED.  Both are still captured for downstream
  scene work.

Coverage boundary:
  * dispatcher indices 0..51 (lvl_info.lvl order), not 1-based names;
  * B2 init only: no pixels, audio, input or per-frame state;
  * the child must reach MENU; a timeout is an ERROR, not a mismatch;
  * the active profile must have SOUND/MUSIC = 0 (F348); direct_drive also
    mutes the process via NirCmd.

Failure conditions:
  * no 32-bit interpreter (PY32) or direct_drive missing;
  * a level does not reach the state tuple within --timeout;
  * the capture has no B2FFI02 magic or is empty after a clean exit;
  * b2_sites exits nonzero without a TOTAL line.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

from phys_sweep import (  # noqa: E402
    load_random_map,
    load_rec_map,
    load_skip_map,
    parse_levels,
    pick_rec,
    rec_shared_map,
)

DEFAULT_PY32 = r"C:/Users/K/.local/bin/python3.12.exe"


def log_magic(path: Path) -> str:
    try:
        with open(path, "rb") as fh:
            return fh.read(8).decode("latin1").rstrip("\x00")
    except OSError:
        return ""


def parse_total(stderr: str, stdout: str) -> int | None:
    for line in (stdout + "\n" + stderr).splitlines():
        if "TOTAL mismatches=" in line:
            try:
                return int(line.rsplit("=", 1)[1])
            except ValueError:
                return None
    return None


def run_one(idx: int, name: str, rec: str | None, args) -> dict:
    out_dir: Path = args.out_dir
    log = out_dir / f"lvl{idx:02d}_ffi.bin"
    drive_out = out_dir / f"lvl{idx:02d}_drive.jsonl"
    for p in (log, drive_out):
        if p.exists():
            p.unlink()

    env = dict(os.environ)
    env["B2PROXY_LOG"] = str(log)
    env.pop("B2PROXY_HOT", None)
    cmd = [
        args.py32, str(TOOLS / "direct_drive.py"),
        "--dir", str(args.dir),
        "--levels", str(idx),
        "--timeout", str(args.timeout),
        "--gap", str(args.gap),
        "--out", str(drive_out),
    ]
    if args.no_desktop:
        cmd.append("--no-desktop")
    if args.kill:
        cmd.append("--kill")

    t0 = time.time()
    try:
        p = subprocess.run(cmd, env=env, capture_output=True, text=True,
                           timeout=args.timeout + 90)
        rc = p.returncode
        err = (p.stderr or "")[-600:]
    except subprocess.TimeoutExpired as exc:
        rc = -9
        err = f"subprocess timeout: {exc}"
        p = None
    ms = int((time.time() - t0) * 1000)

    magic = log_magic(log) if log.exists() else ""
    size = log.stat().st_size if log.exists() else 0
    clean = None
    if drive_out.exists():
        for line in drive_out.read_text(encoding="utf-8", errors="replace").splitlines():
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if obj.get("event") == "exit":
                clean = obj
    row = {
        "level": idx, "name": name, "rec": rec, "rc": rc,
        "ms": ms, "log": str(log), "log_bytes": size, "magic": magic,
        "exit": clean, "error": err if rc != 0 else "",
    }
    if rc != 0:
        row["status"] = "ERROR"
        row["reason"] = "direct_drive failed"
        return row
    if magic != "B2FFI02" or size <= 20:
        row["status"] = "ERROR"
        row["reason"] = "empty/truncated b2 log"
        return row
    row["status"] = "CAPTURED"
    return row


def compare(row: dict, args) -> None:
    idx = row["level"]
    rec = row["rec"]
    if not rec:
        row.update(status="NO_REC", mismatches=None)
        return
    rec_log = ROOT / "work" / rec / "ffi.bin"
    if not rec_log.exists():
        row.update(status="NO_REC", mismatches=None, reason="recording missing")
        return
    p = subprocess.run(
        [sys.executable, str(TOOLS / "b2_sites.py"), row["log"], "compare",
         str(rec_log), "--stop-at-step"],
        capture_output=True, text=True,
    )
    mism = parse_total(p.stderr, p.stdout)
    row["mismatches"] = mism
    row["compare_rc"] = p.returncode
    if mism is None:
        row.update(status="ERROR", reason="compare produced no TOTAL")
        row["error"] = (p.stderr or p.stdout)[-600:]
        return
    if idx in args.random_levels:
        row["status"] = "RNG" if mism else "PASS"
    elif row.get("shared"):
        row["status"] = "SHARED" if mism else "PASS"
    elif idx in args.skip_levels:
        row["status"] = "SKIP" if mism else "PASS"
        row["reason"] = args.skip_levels[idx]
    else:
        row["status"] = "PASS" if mism == 0 else "MISMATCH"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--levels", default="0-51")
    ap.add_argument("--dir", default=str(ROOT / "work" / "e2e_game"))
    ap.add_argument("--out-dir", default=str(ROOT / "work" / "capture"))
    ap.add_argument("--levels-file", default=str(ROOT / "work" / "pak_gametop" / "lvl_info.lvl"))
    ap.add_argument("--rec-csv", default=str(ROOT / "mapping" / "levels.csv"))
    ap.add_argument("--random-csv", default=str(ROOT / "mapping" / "phys_random.csv"))
    ap.add_argument("--skip-csv", default=str(ROOT / "mapping" / "phys_skip.csv"))
    ap.add_argument("--py32", default=os.environ.get("PY32", DEFAULT_PY32))
    ap.add_argument("--timeout", type=float, default=30.0)
    ap.add_argument("--gap", type=float, default=1.5)
    ap.add_argument("--resume", action="store_true", help="skip levels already PASS in summary.jsonl")
    ap.add_argument("--kill", action="store_true", help="negative control: TerminateProcess")
    ap.add_argument("--no-desktop", action="store_true")
    args = ap.parse_args()

    if not Path(args.py32).exists():
        print(f"PY32 not found: {args.py32}", file=sys.stderr)
        return 2
    args.dir = Path(args.dir)
    args.out_dir = Path(args.out_dir)
    args.out_dir.mkdir(parents=True, exist_ok=True)

    levels = parse_levels(Path(args.levels_file))
    if len(levels) != 52:
        print(f"expected 52 levels, got {len(levels)}", file=sys.stderr)
        return 2
    rec_map = load_rec_map(Path(args.rec_csv))
    owners = rec_shared_map(rec_map)
    args.random_levels = set(load_random_map(Path(args.random_csv)))
    args.skip_levels = load_skip_map(Path(args.skip_csv))

    wanted = []
    for part in args.levels.split(","):
        if "-" in part:
            a, b = part.split("-", 1)
            wanted.extend(range(int(a), int(b) + 1))
        else:
            wanted.append(int(part))
    wanted = [i for i in wanted if 0 <= i < 52]

    summary_path = args.out_dir / "summary.jsonl"
    done = set()
    if args.resume and summary_path.exists():
        for line in summary_path.read_text(encoding="utf-8", errors="replace").splitlines():
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if obj.get("status") == "PASS":
                done.add(obj.get("level"))

    rows = []
    for idx in wanted:
        if idx in done:
            print(f"[{idx:02d}] {levels[idx]} SKIP(resume)", flush=True)
            continue
        name = levels[idx]
        rec = pick_rec(rec_map.get(name, []))
        shared = bool(rec and len(owners.get(rec, ())) > 1)
        print(f"[{idx:02d}] {name} rec={rec} shared={shared}", flush=True)
        row = run_one(idx, name, rec, args)
        row["shared"] = shared
        if row["status"] == "CAPTURED":
            compare(row, args)
        rows.append(row)
        with open(summary_path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
        print(f"    -> {row['status']} mism={row.get('mismatches')} "
              f"log={row['log_bytes']}B rc={row['rc']} {row.get('reason', '')}",
              flush=True)

    counts = {}
    for r in rows:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    print("SUMMARY", json.dumps(counts, ensure_ascii=False), flush=True)
    return 1 if counts.get("MISMATCH") or counts.get("ERROR") else 0


if __name__ == "__main__":
    sys.exit(main())
