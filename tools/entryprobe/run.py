"""Entry-probe runner: install the entry-hook DLL into a game copy, run, decode counts.

Why: the F298/F299 census only patches direct `call rel32` sites, so it reports 0 for
functions reached through the Lua VM, vtables or stored function pointers. This probe
patches the function *entry* instead, so those calls are counted too.

usage:
    python tools/entryprobe/run.py --seconds 120          # launch; click in the game; report
    python tools/entryprobe/run.py --keep                 # launch and leave it running
    python tools/entryprobe/run.py --report work/entryprobe/counts.bin
    python tools/entryprobe/run.py --rebuild              # regenerate targets.inc + DLL

outputs (default work/entryprobe/):
    game/                 game copy (data hardlinked from bin/gametop)
    counts.bin            DWORD[EP_N] counters
    entry.log             "ENTRY installed=... failed=... targets=..."
    hits.csv              rva, count, lua name (for the current run)
"""
import argparse
import csv
import json
import os
import shutil
import struct
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
ORACLE = os.path.join(ROOT, "bin", "gametop")
PROXY = os.path.join(ROOT, "build", "proxy", "Release", "b2Physics.dll")
OUT = os.path.join(ROOT, "work", "entryprobe")
BUILD = os.path.join(HERE, "build")


def build(rescan):
    if rescan:
        subprocess.run([sys.executable, os.path.join(HERE, "gen_targets.py")], check=True, cwd=ROOT)
    subprocess.run(["cmake", "-S", HERE, "-B", BUILD, "-G", "Visual Studio 18 2026", "-A", "Win32"],
                   check=True)
    subprocess.run(["cmake", "--build", BUILD, "--config", "Release"], check=True)
    return os.path.join(BUILD, "Release", "entryprobe.dll")


def prepare(dll):
    game = os.path.join(OUT, "game")
    os.makedirs(game, exist_ok=True)
    skip = (".i64", ".id0", ".id1", ".id2", ".nam", ".til")
    for name in os.listdir(ORACLE):
        src = os.path.join(ORACLE, name)
        if not os.path.isfile(src) or name.endswith(skip) or name == "data":
            continue
        dst = os.path.join(game, name)
        if not os.path.exists(dst):
            shutil.copy2(src, dst)
    data = os.path.join(game, "data")
    if not os.path.exists(data):
        os.link(os.path.join(ORACLE, "data"), data)
    shutil.copy2(PROXY, os.path.join(game, "b2Physics.dll"))
    shutil.copy2(os.path.join(ORACLE, "b2Physics.dll"), os.path.join(game, "b2Physics_orig.dll"))
    shutil.copy2(dll, os.path.join(game, "entryprobe.dll"))
    return game


def report(path):
    targets = json.load(open(os.path.join(HERE, "targets.json")))["targets"]
    blob = open(path, "rb").read()
    counts = struct.unpack("<%dI" % len(targets), blob[:4 * len(targets)])
    lua = {int(r["cfunc"], 16): r["lua_name"]
           for r in csv.DictReader(open(os.path.join(ROOT, "mapping", "lua-bindings.csv")))}
    rows = [(t["va"], c, lua.get(t["va"], "")) for t, c in zip(targets, counts) if c]
    rows.sort(key=lambda x: -x[1])
    print(f"{path}: nonzero={len(rows)}/{len(targets)} total={sum(counts)}")
    for va, c, name in rows:
        print(f"  {va:08x} {c:10d} {name}")
    with open(os.path.join(OUT, "hits.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["rva", "count", "lua_name"])
        for va, c, name in rows:
            w.writerow([f"{va:08x}", c, name])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seconds", type=int, default=120, help="run time before killing (ignored with --keep)")
    ap.add_argument("--keep", action="store_true", help="leave the game running")
    ap.add_argument("--rebuild", action="store_true", help="regenerate targets.inc and rebuild the DLL")
    ap.add_argument("--report", help="only decode this counts.bin")
    args = ap.parse_args()

    if args.report:
        report(args.report)
        return
    os.makedirs(OUT, exist_ok=True)
    dll = os.path.join(BUILD, "Release", "entryprobe.dll")
    if args.rebuild or not os.path.exists(dll):
        dll = build(args.rebuild)
    game = prepare(dll)
    counts = os.path.join(OUT, "counts.bin")
    for p in (counts, counts + ".tmp", os.path.join(OUT, "entry.log")):
        if os.path.exists(p):
            os.remove(p)
    env = dict(os.environ)
    env["B2RTLPROBE_DLL"] = os.path.join(game, "entryprobe.dll")
    env["ENTRY_OUT"] = counts
    env["ENTRY_LOG"] = os.path.join(OUT, "entry.log")
    env["ENTRY_MS"] = "500"
    p = subprocess.Popen([os.path.join(game, "game.exe")], cwd=game, env=env)
    print(f"pid={p.pid} game={game}")
    if args.keep:
        print("running; click in the game, then stop it and run --report")
        return
    t0 = time.time()
    while time.time() - t0 < args.seconds and p.poll() is None:
        time.sleep(0.5)
    p.kill()
    p.wait()
    time.sleep(0.5)
    report(counts)


if __name__ == "__main__":
    main()
