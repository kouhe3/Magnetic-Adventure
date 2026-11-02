#!/usr/bin/env python3
"""应用层 pending 函数的 `Self` 类型首过表（PE + capstone，不依赖 IDA）。

背景：`mapping/app-functions.csv` 的 1,012 个 pending 函数不全是 Pascal 方法。
本工具按三类硬证据分类，输出 `work/app_self.csv`：

  1. `lua_CFunction`：`mapping/lua-bindings.csv` 的 144 个入口。Lua C 调用约定，
     `lua_State* L` 在栈上（`[ebp+8]`），**不是** Pascal Self；其内部 helper
     可能再把 L 放 EAX（reader 的 `L@EAX`）。
  2. `virtual_method`：在 `.data` 的 VMT 方法表中出现。类名来自 FPC VMT
     `vmt+0x0C` 指向的 Pascal 短字符串；沿 `vmt+8` 父链归到**定义类**，
     `vmt+0x30+4*i` 是方法槽。
  3. `uses_TLevelObjects`：函数体内（任意位置）出现 `mov reg, [0x665334]`。该全局是
     `TLevelObjects` 单例（VMT `0x6431D0`，实例大小 `0xB8`；见 F319）。

其余为 `direct_method`（有 EAX 保存/`[eax+off]` 访问，类未定）或
`static_or_helper`（无 EAX Self 迹象）。这两类需要 call-site/字段数据流，
本工具不猜——输出空 `self_class`，避免把错误类型喂给 A/B harness。

用法：
    python tools/app_self.py
    python tools/app_self.py --csv work/app_self.csv
    python tools/app_self.py --print-vmt

判据：同一 `bin/gametop/game.exe` 下，`virtual_method` 39 个、
`lua_CFunction` 144 个、`uses_TLevelObjects` 102 个（后者是前者的子集；
只看前 30 条指令时是 75）。改 `game.exe` 或 CSV 后数字会变，以输出为准。

覆盖边界：
  - VMT 方法表只覆盖虚方法；非虚方法不在表里，需调用点分析。
  - Lua binding 的内部对象不一定是 TLevelObjects；只有显式读 `0x665334` 才记。
  - 字段偏移聚类太粗（大量 `[eax+4]`/`[eax+16]`），本工具不做类名猜测。
"""
from __future__ import annotations

import argparse
import csv
import struct
from collections import Counter
from pathlib import Path

import capstone

ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / "bin" / "gametop" / "game.exe"
APP_CSV = ROOT / "mapping" / "app-functions.csv"
LUA_CSV = ROOT / "mapping" / "lua-bindings.csv"
TLO_GLOBAL = 0x665334
TLO_VMT = 0x6431D0


class PE:
    def __init__(self, path: Path) -> None:
        self.data = path.read_bytes()
        e = struct.unpack_from("<I", self.data, 0x3C)[0]
        self.image_base = struct.unpack_from("<I", self.data, e + 24 + 28)[0]
        n = struct.unpack_from("<H", self.data, e + 6)[0]
        oh = struct.unpack_from("<H", self.data, e + 20)[0]
        self.sections: list[tuple[str, int, int, int, int]] = []
        off = e + 24 + oh
        for i in range(n):
            b = self.data[off + i * 40: off + i * 40 + 40]
            name = b[:8].rstrip(b"\0").decode("latin1")
            vs, va, rs, ptr = struct.unpack_from("<IIII", b, 8)
            self.sections.append((name, va, vs, rs, ptr))

    def section(self, va: int):
        rva = va - self.image_base
        for s in self.sections:
            name, sva, vs, rs, ptr = s
            if sva <= rva < sva + max(vs, rs):
                return s
        return None

    def read(self, va: int, n: int) -> bytes | None:
        s = self.section(va)
        if not s:
            return None
        name, sva, vs, rs, ptr = s
        off = ptr + (va - self.image_base - sva)
        if off < 0 or off + n > len(self.data):
            return None
        return self.data[off:off + n]

    def u32(self, va: int) -> int | None:
        b = self.read(va, 4)
        return struct.unpack("<I", b)[0] if b and len(b) == 4 else None

    def text_range(self) -> tuple[int, int]:
        for name, sva, vs, rs, ptr in self.sections:
            if name == ".text":
                return self.image_base + sva, self.image_base + sva + max(vs, rs)
        raise SystemExit("app_self: no .text")

    def data_range(self) -> tuple[int, int]:
        for name, sva, vs, rs, ptr in self.sections:
            if name == ".data":
                return self.image_base + sva, self.image_base + sva + max(vs, rs)
        raise SystemExit("app_self: no .data")


def pstring(pe: PE, va: int | None, data_lo: int, data_hi: int) -> str | None:
    if not va or not (data_lo <= va < data_hi):
        return None
    b = pe.read(va, 1)
    if not b:
        return None
    ln = b[0]
    if not (1 <= ln <= 63):
        return None
    s = pe.read(va + 1, ln)
    if not s or len(s) != ln or not all(32 <= c < 127 for c in s):
        return None
    try:
        name = s.decode("ascii")
    except UnicodeDecodeError:
        return None
    if not name.startswith("T") or not all(c.isalnum() or c == "_" for c in name):
        return None
    return name


def resolve_slot(pe: PE, slot: int, text_lo: int, text_hi: int,
                 data_lo: int, data_hi: int):
    for i in range(0x101):
        base = slot - 0x30 - 4 * i
        if base < data_lo:
            break
        m = pe.u32(base + 0x30)
        if not (m is not None and text_lo <= m < text_hi):
            continue
        name = pstring(pe, pe.u32(base + 0x0C), data_lo, data_hi)
        if name:
            return base, name, i
    return None


def defining_class(pe: PE, vmt: int, idx: int, fn: int,
                   text_lo: int, text_hi: int,
                   data_lo: int, data_hi: int) -> tuple[str, int]:
    cur_vmt, cur_name = vmt, pstring(pe, pe.u32(vmt + 0x0C), data_lo, data_hi)
    seen = 0
    while cur_vmt and cur_name and seen < 32:
        seen += 1
        parent = pe.u32(cur_vmt + 8)
        if not parent or not (data_lo <= parent < data_hi):
            break
        if pe.u32(parent + 0x30 + 4 * idx) != fn:
            break
        pn = pstring(pe, pe.u32(parent + 0x0C), data_lo, data_hi)
        if not pn:
            break
        cur_vmt, cur_name = parent, pn
    return cur_name or "?", cur_vmt


def is_mov_eax_save(insn) -> bool:
    if insn.mnemonic != "mov" or len(insn.operands) != 2:
        return False
    a, b = insn.operands
    return (a.type == capstone.x86.X86_OP_MEM and b.type == capstone.x86.X86_OP_REG
            and b.reg == capstone.x86.X86_REG_EAX
            and a.mem.base in (capstone.x86.X86_REG_EBP, capstone.x86.X86_REG_ESP))


def has_self_ref(insn) -> bool:
    for op in insn.operands:
        if (op.type == capstone.x86.X86_OP_MEM
                and op.mem.base == capstone.x86.X86_REG_EAX
                and op.mem.disp >= 0):
            return True
    return False


def is_tlo_load(insn) -> bool:
    if insn.mnemonic != "mov" or len(insn.operands) != 2:
        return False
    dst, src = insn.operands
    return (dst.type == capstone.x86.X86_OP_REG
            and src.type == capstone.x86.X86_OP_MEM
            and src.mem.base == 0 and src.mem.index == 0
            and src.mem.disp == TLO_GLOBAL)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--game", type=Path, default=GAME)
    ap.add_argument("--csv", type=Path, default=ROOT / "work" / "app_self.csv")
    ap.add_argument("--print-vmt", action="store_true")
    args = ap.parse_args()

    pe = PE(args.game)
    text_lo, text_hi = pe.text_range()
    data_lo, data_hi = pe.data_range()
    rows = list(csv.DictReader(APP_CSV.open(newline="", encoding="utf-8")))
    pending = [(int(r["rva"], 16), int(r["size"])) for r in rows if r["status"] == "pending"]
    pset = {a for a, _ in pending}
    lua = {int(r["cfunc"], 16): r["lua_name"]
           for r in csv.DictReader(LUA_CSV.open(newline="", encoding="utf-8"))}

    # ---- 1) VMT 方法表：扫 .data 里指向 pending 起始的 dword ----
    raw = pe.read(data_lo, data_hi - data_lo)
    if raw is None:
        raise SystemExit("app_self: cannot read .data")
    slots: dict[int, list[int]] = {}
    for off in range(0, len(raw) - 4, 4):
        v = struct.unpack_from("<I", raw, off)[0]
        if v in pset:
            slots.setdefault(v, []).append(data_lo + off)
    vmt_defs: dict[int, list[tuple[str, int, int]]] = {}
    for fn, ss in slots.items():
        defs: set[tuple[str, int, int]] = set()
        for s in ss:
            r = resolve_slot(pe, s, text_lo, text_hi, data_lo, data_hi)
            if r:
                nm, v = defining_class(pe, r[0], r[2], fn, text_lo, text_hi, data_lo, data_hi)
                defs.add((nm, v, r[2]))
        if defs:
            vmt_defs[fn] = sorted(defs)

    # ---- 2) 每条 pending 函数的 EAX Self / TLevelObjects 迹象 ----
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    md.detail = True
    out = []
    for va, size in pending:
        buf = pe.read(va, size) or b""
        all_ins = list(md.disasm(buf, va))
        ins = all_ins[:40]
        save = any(is_mov_eax_save(x) for x in ins)
        selfref = any(has_self_ref(x) for x in ins)
        tlo = any(is_tlo_load(x) for x in all_ins)
        kinds = []
        if va in lua:
            kinds.append("lua_CFunction")
        if va in vmt_defs:
            kinds.append("virtual_method")
        if tlo:
            kinds.append("uses_TLevelObjects")
        if not kinds:
            kinds.append("direct_method" if (save or selfref) else "static_or_helper")
        cls = ""
        vmt = ""
        idx = ""
        notes = []
        if va in vmt_defs:
            cls = "|".join(sorted({n for n, _, _ in vmt_defs[va]}))
            vmt = "|".join(sorted({hex(v) for _, v, _ in vmt_defs[va]}))
            idx = "|".join(str(i) for _, _, i in vmt_defs[va])
        elif va in lua:
            cls = "lua_State* / TLevelObjects" if tlo else "lua_State*"
            notes.append("arg0=[ebp+8]")
            if tlo:
                notes.append("internal TLevelObjects @0x665334")
        elif tlo:
            cls = "TLevelObjects"
            notes.append("global 0x665334")
        out.append([hex(va), size, "+".join(kinds), lua.get(va, ""), cls, vmt, idx,
                    "; ".join(notes)])

    args.csv.parent.mkdir(parents=True, exist_ok=True)
    with args.csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["rva", "size", "kind", "lua_name", "self_class", "vmt",
                    "method_index", "notes"])
        w.writerows(out)

    print(f"pending={len(pending)} rows={len(out)} -> {args.csv}")
    print("kind:", dict(Counter(o[2] for o in out)))
    print("TLevelObjects:", sum(1 for o in out if "uses_TLevelObjects" in o[2]),
          "virtual:", len(vmt_defs), "lua:", sum(1 for a in lua if a in pset))
    print("vmt classes:", dict(Counter(o[4] for o in out if o[2] == "virtual_method")))
    if args.print_vmt:
        for va in sorted(vmt_defs):
            for nm, v, i in vmt_defs[va]:
                print(f"{va:#x}\t{nm}\tvmt={v:#x}\tidx={i}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
