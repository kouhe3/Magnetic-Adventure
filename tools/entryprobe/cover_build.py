#!/usr/bin/env python3
"""Build work/cover_game with a custom-level pak for Lua binding coverage (F406).

Usage:
    python tools/entryprobe/cover_build.py
    python tools/entryprobe/cover_build.py --o tests/levels/cover_bindings_terminal_roll.lua
    python tools/entryprobe/cover_build.py --out work/cover_game_neg --o ...

Inputs:
    bin/gametop/                         read-only oracle (game.exe + DLLs + data)
    build/proxy/Release/b2Physics.dll    early-mount b2 proxy
    work/entryprobe_lvl1/build/Release/entryprobe.dll   1,010-target probe
    tests/levels/cover_bindings_*.lua    replacement level scripts

Output:
    --out (default work/cover_game) with game.exe, DLLs, rebuilt data pak,
    b2Physics.dll (proxy), b2Physics_orig.dll (oracle), entryprobe.dll.

Criterion:
    `tools/pak.py verify` accepts the rebuilt pak; the game copy is then driven by
    `tools/direct_drive.py --dir <out> --levels 1`. The level entry is verified by
    `tools/entryprobe/check_bindings.py`, not by this builder.

Boundary:
    Same-name replacement only (lvl_o14.lua/lvl_e14.lua); no TOC/entry changes.
    The builder does not launch the game or validate Lua semantics.

Failure modes:
    Missing oracle/proxy/probe/script, or pak_write refuses the replacement.
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ORACLE = os.path.join(ROOT, "bin", "gametop")
PROXY = os.path.join(ROOT, "build", "proxy", "Release", "b2Physics.dll")
PROBE = os.path.join(ROOT, "work", "entryprobe_lvl1", "build", "Release", "entryprobe.dll")
LUA_O = os.path.join(ROOT, "tests", "levels", "cover_bindings_o.lua")
LUA_E = os.path.join(ROOT, "tests", "levels", "cover_bindings_e.lua")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "work", "cover_game"))
    ap.add_argument("--o", default=LUA_O)
    ap.add_argument("--e", default=LUA_E)
    a = ap.parse_args()
    out = os.path.abspath(a.out)
    os.makedirs(out, exist_ok=True)

    skip = (".i64", ".id0", ".id1", ".id2", ".nam", ".til")
    for name in os.listdir(ORACLE):
        src = os.path.join(ORACLE, name)
        if not os.path.isfile(src) or name.endswith(skip) or name == "data":
            continue
        shutil.copy2(src, os.path.join(out, name))
    shutil.copy2(PROXY, os.path.join(out, "b2Physics.dll"))
    shutil.copy2(os.path.join(ORACLE, "b2Physics.dll"), os.path.join(out, "b2Physics_orig.dll"))
    shutil.copy2(PROBE, os.path.join(out, "entryprobe.dll"))

    data = os.path.join(out, "data")
    if os.path.exists(data):
        os.remove(data)
    subprocess.run(
        [sys.executable, os.path.join(ROOT, "tools", "pak_write.py"), "rebuild",
         os.path.join(ORACLE, "data"), data,
         "lvl_o14.lua=" + os.path.abspath(a.o), "lvl_e14.lua=" + os.path.abspath(a.e)],
        check=True,
    )
    subprocess.run([sys.executable, os.path.join(ROOT, "tools", "pak.py"), "verify", data], check=True)
    print("built", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
