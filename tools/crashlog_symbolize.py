#!/usr/bin/env python3
"""把 crashlog 的 module+RVA 栈翻译成函数名（game.exe 用 mapping/app-functions.csv，
我方 DLL 用 MSVC .map 的 Publics by Value）。

用法：
    python tools/crashlog_symbolize.py work/crashlog_host/<ts>/logs/crash_b2Physics_<pid>.log
    python tools/crashlog_symbolize.py <log> --map build/proxy/Release/b2Physics.map

判据：输入日志里每个 EXC/FRM/SCN 的 mod+rva 行都追加 fn=…（game.exe 命中 CSV；
有 map 的模块命中最近的前置符号）。日志格式见 src/crashlog/crashlog.c 顶部。

依据：docs/facts.md F315/F316。
"""
from __future__ import annotations

import argparse
import bisect
import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KV = re.compile(r"(\w+)=([^\s]+)")


def parse_kv(line: str) -> dict[str, str]:
    return {k: v for k, v in KV.findall(line)}


class Symbols:
    def __init__(self) -> None:
        self.by_module: dict[str, tuple[list[int], list[str]]] = {}

    def add(self, module: str, rva: int, name: str) -> None:
        starts, names = self.by_module.setdefault(module, ([], []))
        starts.append(rva)
        names.append(name)

    def finalize(self) -> None:
        for module, (starts, names) in list(self.by_module.items()):
            pairs = sorted(zip(starts, names))
            self.by_module[module] = ([p[0] for p in pairs], [p[1] for p in pairs])

    def lookup(self, module: str, rva: int) -> str | None:
        item = self.by_module.get(module)
        if not item:
            return None
        starts, names = item
        i = bisect.bisect_right(starts, rva) - 1
        if i < 0:
            return None
        return names[i]


def load_app_functions(sym: Symbols) -> int:
    path = ROOT / "mapping" / "app-functions.csv"
    if not path.exists():
        return 0
    n = 0
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            try:
                rva = int(row["rva"], 16)
            except (KeyError, ValueError):
                continue
            sym.add("game.exe", rva, f"{row.get('name') or 'sub'} (0x{rva:08X})")
            n += 1
    return n


def merge_map(sym: Symbols, path: Path) -> tuple[str, int]:
    text = path.read_text(encoding="utf-8", errors="replace").splitlines()
    base = 0
    mm = re.search(r"Preferred load address is ([0-9A-Fa-f]+)", "\n".join(text[:40]))
    if mm:
        base = int(mm.group(1), 16)
    module = path.stem + ".dll"
    hm = re.search(r"(?:^|\s)([A-Za-z0-9_.-]+\.(?:dll|exe))\s*$", "\n".join(text[:10]))
    if hm:
        module = hm.group(1)
    starts: list[int] = []
    names: list[str] = []
    in_publics = False
    for line in text:
        if "Publics by Value" in line:
            in_publics = True
            continue
        if not in_publics:
            continue
        parts = line.split()
        if len(parts) < 3 or not re.fullmatch(r"[0-9A-Fa-f]{4}:[0-9A-Fa-f]{8}", parts[0]):
            continue
        try:
            va = int(parts[2], 16)
        except ValueError:
            continue
        starts.append(va - base if va >= base else va)
        names.append(parts[1])
    for rva, name in zip(starts, names):
        sym.add(module, rva, name)
    return module, len(starts)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("log", type=Path)
    ap.add_argument("--map", action="append", default=[], type=Path)
    ap.add_argument("--all", action="store_true", help="同时打印 MOD/CL1 行")
    args = ap.parse_args()

    if not args.log.exists():
        sys.exit(f"crashlog_symbolize: 找不到 {args.log}")

    sym = Symbols()
    n_app = load_app_functions(sym)
    maps = list(args.map) or [
        ROOT / "build" / "proxy" / "Release" / "b2Physics.map",
        ROOT / "build" / "Release" / "b2Physics.map",
    ]
    loaded = []
    for p in maps:
        if p.exists():
            module, n = merge_map(sym, p)
            loaded.append((module, n, p))
    sym.finalize()

    lines = args.log.read_text(encoding="utf-8", errors="replace").splitlines()
    seen_exc = 0
    for line in lines:
        tag = line.split(" ", 1)[0]
        if tag == "CL1":
            print(line)
            continue
        if tag == "MOD":
            if args.all:
                print(line)
            continue
        if tag not in ("EXC", "CTX", "FRM", "SCN", "DMP"):
            continue
        kv = parse_kv(line)
        out = line
        if tag in ("EXC", "FRM", "SCN") and "mod" in kv and "rva" in kv:
            try:
                rva = int(kv["rva"], 16)
            except ValueError:
                rva = -1
            if rva >= 0:
                name = sym.lookup(kv["mod"], rva)
                if name:
                    out += f" fn={name}"
                elif kv["mod"] in sym.by_module:
                    out += " fn=?"
        if tag == "EXC":
            seen_exc += 1
        print(out)

    print(f"\n# app-functions={n_app} maps={len(loaded)} "
          f"({', '.join(f'{m}:{n}' for m, n, _ in loaded) or 'none'}) exc={seen_exc}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
