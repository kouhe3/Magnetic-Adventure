#!/usr/bin/env python3
"""应用层函数 ↔ 结构体布局 / 字节一致冲撞（PE + capstone，不依赖 IDA）。

用法：
  python tools/app_layout.py --report      # 写 work/app_fields.csv / work/class_layouts.csv / work/app_layout.json
  python tools/app_layout.py --check       # 交叉验证；contradictions>0 时退出码 1
  python tools/app_layout.py --dups        # 字节一致簇（exact / masked）到 work/fn_dups.json
  python tools/app_layout.py --show RVA    # 打印单函数的字段访问与调用（排查用）

判据：
  --check 打印 `functions_self=… ptr_fields=… contradictions=…`，矛盾分四类：
    oob             Self/指针类字段偏移 ≥ 该类实例大小（VMT+0）
    width_conflict  同一 (class,off) 上静态访问宽度不一致（1/2/4/8）
    direct_mismatch 直接调用的目标静态类不是该字段运行时类的祖先
    unlisted        有对象证据的字段在 `work/live_fields.json` 里没有条目（不算矛盾，单列）
  --dups 打印 `exact_groups=… masked_groups=… cross_class=… pilot_dup=…`

输入：
  bin/gametop/game.exe（只读 oracle）、mapping/app-functions.csv、
  mapping/app-self-map.csv（F320 的 540 映射；由 work/app_self_deep.csv 提升）、
  mapping/app-self-fixes.csv（T7.2c 勘误，逐行覆盖 map）、
  mapping/live-fields.json（F320 的运行时指针字段表，单次采样）、
  work/pilot/*_results.json（pilot 目标，可选）。

覆盖边界：
  - 只解析 `.text` 里列出函数体；线性扫描不做 CFG，跳转后的寄存器状态按顺序直通。
  - 只跟踪 EAX 起始的 Self 及其栈溢出槽/寄存器副本；不跟踪参数对象（EDX 等）。
  - `[reg+disp]` 的 `reg` 必须是已知 Self/字段指针；字段指针的二次解引用只到一层。
  - 运行时字段表只在“该偏移当时指向带 VMT 的对象”时有名字：nil、字符串、数组没有条目。

失效条件：
  game.exe、app-functions.csv、app-self-map.csv、live-fields.json 任一变化后重跑；
  类表依赖 FPC 2.2.4 布局（vmtInstanceSize=+0、+4=-size、parent=+8、ClassName=+0xC、方法槽 +0x30+4i）。
"""
from __future__ import annotations

import argparse
import csv
import json
import struct
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

import capstone

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from app_self import PE, pstring  # noqa: E402

GAME = ROOT / "bin" / "gametop" / "game.exe"
APP_CSV = ROOT / "mapping" / "app-functions.csv"
DEEP_CSV = ROOT / "mapping" / "app-self-map.csv"
LIVE_JSON = ROOT / "mapping" / "live-fields.json"
PILOT_GLOB = "work/pilot/*_results.json"

X = capstone.x86
FLOAT_MN = {
    "fld", "fst", "fstp", "fadd", "faddp", "fsub", "fsubp", "fsubr", "fsubrp",
    "fmul", "fmulp", "fdiv", "fdivp", "fdivr", "fdivrp", "fcom", "fcomp",
    "fcompp", "fldz", "fld1",
}
# fild/fist 是整数↔浮点转换：内存里是整数，不是 Single
INT_FLOAT_MN = {"fild", "fist", "fistp"}
CALLER_SAVED = (X.X86_REG_EAX, X.X86_REG_ECX, X.X86_REG_EDX)


# ---------------------------------------------------------------- PE / 类表

@dataclass
class Vmt:
    name: str
    va: int
    size: int
    parent: int


def load_vmts(pe: PE) -> dict[str, Vmt]:
    """扫 .data 找 FPC 2.2.4 VMT。验证器：+4 == -size（TLmt 布局的双份大小）。"""
    dl, dh = pe.data_range()
    raw = pe.read(dl, dh - dl)
    text_lo, text_hi = pe.text_range()
    found: dict[str, list[Vmt]] = defaultdict(list)
    for off in range(0, len(raw) - 0x40, 4):
        va = dl + off
        size = struct.unpack_from("<I", raw, off)[0]
        if not (4 <= size <= 0x10000):
            continue
        if struct.unpack_from("<I", raw, off + 4)[0] != (-size) & 0xFFFFFFFF:
            continue
        parent = struct.unpack_from("<I", raw, off + 8)[0]
        if parent and not (dl <= parent < dh):
            continue
        if parent and pe.u32(parent) > size:
            continue
        name = pstring(pe, pe.u32(va + 0x0C), dl, dh)
        if not name:
            continue
        first = pe.u32(va + 0x30)
        if not first or not (text_lo <= first < text_hi):
            continue
        found[name].append(Vmt(name, va, size, parent))
    out: dict[str, Vmt] = {}
    for name, cands in found.items():
        # 同名多个时取父链最完整的一个（避免同名假 VMT）
        out[name] = max(cands, key=lambda v: (v.parent != 0, -v.va))
    return out


def vmt_by_va(vmts: dict[str, Vmt]) -> dict[int, Vmt]:
    return {v.va: v for v in vmts.values()}


def slot_fn(pe: PE, vmt_va: int, slot: int) -> int | None:
    return pe.u32(vmt_va + 0x30 + 4 * slot)


# ---------------------------------------------------------------- 函数体

@dataclass
class FieldAccess:
    rva: int
    cls: str
    off: int
    width: int
    kind: str
    access: str          # r/w/rw
    site: int
    via: str             # direct | via:CLASS
    funcs: set[int] = field(default_factory=set)


@dataclass
class CallRec:
    rva: int
    cls: str
    site: int
    kind: str            # self_vcall | field_vcall | field_dcall | self_dcall
    off: int = 0
    slot: int = -1
    target: int = 0


def taint_of(insn, op, state, spills):
    if op.type == X.X86_OP_REG:
        return state.get(op.reg)
    if op.type != X.X86_OP_MEM:
        return None
    m = op.mem
    base = m.base
    if base in (X.X86_REG_EBP, X.X86_REG_ESP) and base != 0 and m.index == 0:
        return spills.get((base, m.disp))
    if base == 0 and m.index == 0:
        return None  # 绝对地址（全局变量）
    t = state.get(base)
    if t is None:
        return None
    if t[0] == "self":
        return ("vmt", 0) if m.disp == 0 else ("fld", m.disp, op.size)
    if t[0] == "flda":
        return ("fld", t[1] + t[2] + m.disp, op.size)
    if t[0] == "fld":
        if m.disp == 0:
            return ("vmtf", t[1])
        return ("pfld", t[1], m.disp, op.size)
    return None


def scan_function(pe: PE, md, rva: int, size: int, cls: str, live: dict | None = None):
    """线性扫描一个函数：返回 (字段访问, 调用记录, 证据集合)。"""
    code = pe.read(rva, size)
    if not code:
        return [], [], {}
    insns = list(md.disasm(code, rva))
    state: dict[int, tuple] = {X.X86_REG_EAX: ("self",)}
    spills: dict[tuple[int, int], tuple] = {}
    accesses: list[FieldAccess] = []
    calls: list[CallRec] = []
    ptr_evidence: set[int] = set()

    def rec_access(op, ins, via="direct", owner_off: int | None = None):
        m = op.mem
        off = m.disp
        target_cls = cls
        if via == "direct":
            # 直接 Self：off>0 才是字段；off==0 是 VMT 指针
            if off == 0:
                return
        else:
            # 通过字段指针访问子对象：字段类型由运行时表决定；不是唯一类就跳过
            cands = live_ptrs(live or {}, cls, owner_off or 0)
            if len(cands) != 1:
                return
            target_cls, via = cands[0], "via:" + cls
            if off == 0:
                return
        width = op.size
        kind = "single" if (width == 4 and ins.mnemonic in FLOAT_MN) else {
            1: "byte", 2: "word", 4: "dword", 8: "qword",
        }.get(width, "?%d" % width)
        if ins.mnemonic in INT_FLOAT_MN:
            kind = "dword" if width == 4 else "word" if width == 2 else kind
        acc = {1: "r", 2: "w"}.get(op.access, "?")
        accesses.append(FieldAccess(rva, target_cls, off, width, kind, acc, ins.address, via))

    for ins in insns:
        ops = ins.operands
        # 1) 记录内存访问（先于状态更新）
        for i, op in enumerate(ops):
            if op.type != X.X86_OP_MEM:
                continue
            base = op.mem.base
            t = state.get(base) if base else None
            if t and t[0] == "self" and op.mem.index == 0:
                rec_access(op, ins)
            elif t and t[0] == "fld" and op.mem.index == 0 and op.mem.disp > 0:
                # 通过字段指针读子对象；字段类型由 live 表决定
                rec_access(op, ins, via="field", owner_off=t[1])
        # 2) 调用
        if ins.mnemonic == "call":
            op = ops[0]
            if op.type == X.X86_OP_IMM:
                t = state.get(X.X86_REG_EAX)
                if t and t[0] == "self":
                    calls.append(CallRec(rva, cls, ins.address, "self_dcall", target=op.imm))
                elif t and t[0] == "fld":
                    ptr_evidence.add(t[1])
                    calls.append(CallRec(rva, cls, ins.address, "field_dcall", off=t[1], target=op.imm))
            elif op.type == X.X86_OP_MEM:
                t = state.get(op.mem.base) if op.mem.base else None
                d = op.mem.disp
                if t and t[0] == "vmtf" and d >= 0x30 and (d - 0x30) % 4 == 0:
                    ptr_evidence.add(t[1])
                    calls.append(CallRec(rva, cls, ins.address, "field_vcall", off=t[1],
                                         slot=(d - 0x30) // 4))
                elif t and t[0] == "vmt" and t[1] == 0 and d >= 0x30 and (d - 0x30) % 4 == 0:
                    calls.append(CallRec(rva, cls, ins.address, "self_vcall", slot=(d - 0x30) // 4))
            for r in CALLER_SAVED:
                state.pop(r, None)
            # call 之后 EAX 结果未知
            continue
        # 3) 状态转移
        mn = ins.mnemonic
        if mn in ("mov", "movzx", "movsx", "movsxd") and len(ops) == 2:
            d, s = ops
            t = taint_of(ins, s, state, spills)
            if d.type == X.X86_OP_REG:
                if t:
                    state[d.reg] = t
                else:
                    state.pop(d.reg, None)
            elif d.type == X.X86_OP_MEM and d.mem.base in (X.X86_REG_EBP, X.X86_REG_ESP) and d.mem.index == 0:
                spills[(d.mem.base, d.mem.disp)] = t
            continue
        if mn == "lea" and len(ops) == 2 and ops[0].type == X.X86_OP_REG and ops[1].type == X.X86_OP_MEM:
            s = ops[1]
            t = state.get(s.mem.base) if s.mem.base else None
            if t and t[0] in ("fld", "flda"):
                base_off = t[1] + (t[2] if t[0] == "flda" else 0)
                state[ops[0].reg] = ("flda", base_off, s.mem.disp)
            else:
                state.pop(ops[0].reg, None)
            continue
        if mn in ("add", "sub", "inc", "dec") and ops:
            d = ops[0]
            if d.type == X.X86_OP_REG:
                t = state.get(d.reg)
                if t and t[0] in ("fld", "flda"):
                    delta = 0
                    if len(ops) == 2 and ops[1].type == X.X86_OP_IMM:
                        delta = ops[1].imm if mn in ("add", "inc") else -ops[1].imm
                    elif mn == "dec":
                        delta = -1
                    base_off = t[1] + (t[2] if t[0] == "flda" else 0)
                    state[d.reg] = ("flda", base_off, delta)
                else:
                    state.pop(d.reg, None)
            continue
        # 其它指令：写到的寄存器全部清 taint
        _r, w = ins.regs_access()
        for r in w:
            state.pop(r, None)
    return accesses, calls, {"ptr_offsets": ptr_evidence}


# ---------------------------------------------------------------- 聚合

def load_deep(path: Path) -> list[dict]:
    rows = list(csv.DictReader(path.open(newline="", encoding="utf-8")))
    for r in rows:
        r["rva_i"] = int(r["rva"], 16)
        r["size_i"] = int(r["size"])
    return rows


def apply_fixes(rows: list[dict], path: Path | None) -> None:
    if not path or not path.exists():
        return
    fix = {int(r["rva"], 16): r for r in csv.DictReader(path.open(newline="", encoding="utf-8"))}
    n = 0
    for r in rows:
        f = fix.get(r["rva_i"])
        if not f:
            continue
        if f.get("self_class"):
            r["self_class"] = f["self_class"]
        if f.get("kind"):
            r["kind"] = f["kind"]
        if f.get("evidence"):
            r["evidence"] = f["evidence"]
        n += 1
    print("fixes applied:", n, file=sys.stderr)


def find_pilot_targets() -> set[int]:
    out: set[int] = set()
    for p in ROOT.glob(PILOT_GLOB):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        for f in d.get("functions", []):
            try:
                out.add(int(f["rva"], 16))
            except Exception:
                pass
    return out


def mask_relocs(code: bytes, md) -> bytes:
    """把指令里 4 字节绝对/相对地址字段清零（call/jmp rel32、[abs]、imm32）。"""
    b = bytearray(code)
    for ins in md.disasm(code, 0):
        mask_tail = False
        for op in ins.operands:
            if op.type == X.X86_OP_IMM and op.size == 4 and (
                    ins.mnemonic in ("call", "jmp")
                    or 0x400000 <= (op.imm & 0xFFFFFFFF) < 0x800000):
                mask_tail = True
            if op.type == X.X86_OP_MEM and op.mem.base == 0 and op.mem.index == 0 \
                    and 0x400000 <= (op.mem.disp & 0xFFFFFFFF) < 0x800000:
                mask_tail = True
        if mask_tail:
            base = ins.address  # 以 0 为基址反汇编，address 即函数内偏移
            lo = max(0, len(ins.bytes) - 4)
            for k in range(lo, len(ins.bytes)):
                b[base + k] = 0
    return bytes(b)


# ---------------------------------------------------------------- 报告

def build(pe, vmts, rows, live):
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    md.detail = True
    by_va = vmt_by_va(vmts)
    accesses: list[FieldAccess] = []
    calls: list[CallRec] = []
    for r in rows:
        if r["kind"] in ("static", "helper"):
            continue
        a, c, ev = scan_function(pe, md, r["rva_i"], r["size_i"], r["self_class"] or "?", live)
        accesses.extend(a)
        calls.extend(c)
    return md, accesses, calls


def live_ptrs(live: dict, cls: str, off: int) -> list[str]:
    return list(live.get(cls, {}).get("%02x" % off, []))


def classify_offsets(accesses, live) -> tuple[dict, list[dict]]:
    """按 (class, off) 聚合静态访问与运行时指针表。"""
    per: dict[tuple[str, int], dict] = defaultdict(lambda: {
        "widths": set(), "kinds": set(), "acc": set(), "funcs": set(),
    })
    for a in accesses:
        k = (a.cls, a.off)
        per[k]["widths"].add(a.width)
        per[k]["kinds"].add(a.kind)
        per[k]["acc"].add(a.access)
        per[k]["funcs"].add(a.rva)
    rows_out = []
    for (cls, off), v in sorted(per.items(), key=lambda kv: (kv[0][0], kv[0][1])):
        ptrs = live_ptrs(live, cls, off)
        rows_out.append({
            "class": cls, "off": off, "widths": sorted(v["widths"]),
            "kinds": sorted(v["kinds"]), "access": "".join(sorted(v["acc"])),
            "n_funcs": len(v["funcs"]), "ptr_class": ",".join(ptrs),
            "funcs": sorted(v["funcs"]),
        })
    return per, rows_out


def cmd_report(pe, vmts, rows, live, outdir: Path) -> dict:
    md, accesses, calls = build(pe, vmts, rows, live)
    per, layout_rows = classify_offsets(accesses, live)
    with (outdir / "app_fields.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["rva", "class", "off", "width", "kind", "access", "site", "via"])
        for a in sorted(accesses, key=lambda a: (a.rva, a.site, a.off)):
            w.writerow([hex(a.rva), a.cls, hex(a.off), a.width, a.kind, a.access, hex(a.site), a.via])
    with (outdir / "class_layouts.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["class", "vmt", "size", "off", "widths", "kinds", "access", "n_funcs", "ptr_class", "funcs"])
        for row in layout_rows:
            v = vmts.get(row["class"])
            w.writerow([row["class"], hex(v.va) if v else "", v.size if v else "", hex(row["off"]),
                        "/".join(map(str, row["widths"])), "/".join(row["kinds"]), row["access"],
                        row["n_funcs"], row["ptr_class"],
                        " ".join(hex(x) for x in row["funcs"][:6])])
    # 每个 (class, off) 的证据类别：ptr=运行时类已知；single/byte/word/dword/qword=只由宽度固定
    cat = {"ptr": 0, "single": 0, "byte": 0, "word": 0, "dword": 0, "qword": 0, "mixed": 0}
    per_class: dict[str, dict] = {}
    for row in layout_rows:
        kinds, widths, ptr = row["kinds"], row["widths"], row["ptr_class"]
        if ptr:
            c = "ptr"
        elif kinds == ["single"] or (len(widths) == 1 and widths[0] == 4 and "single" in kinds):
            c = "single"
        elif len(widths) == 1 and widths[0] in (1, 2, 4, 8):
            c = {1: "byte", 2: "word", 4: "dword", 8: "qword"}[widths[0]]
        else:
            c = "mixed"
        cat[c] += 1
        pc = per_class.setdefault(row["class"], {"pinned": 0, "ambiguous": 0, "dword_slots": 0})
        if c in ("ptr", "single"):
            pc["pinned"] += 1
        else:
            pc["ambiguous"] += 1
        v = vmts.get(row["class"])
        if v:
            pc["dword_slots"] = max(pc["dword_slots"], (v.size - 4 + 3) // 4)
    summary = {
        "functions": len([r for r in rows if r["self_class"] not in ("", "?")]),
        "accesses": len(accesses),
        "classes_with_layout": len({r["class"] for r in layout_rows}),
        "offsets": len(layout_rows),
        "calls": len(calls),
        "offset_categories": cat,
        "class_pinning": {k: v for k, v in sorted(
            per_class.items(), key=lambda kv: -(kv[1]["ambiguous"] + kv[1]["pinned"]))[:15]},
    }
    (outdir / "app_layout.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
    return summary


def cmd_check(pe, vmts, rows, live) -> int:
    md, accesses, calls = build(pe, vmts, rows, live)
    by_va = {v.va: v for v in vmts.values()}
    oob: list[tuple] = []
    unlisted: list[tuple] = []
    width_conf: dict[tuple[str, int], set[int]] = defaultdict(set)
    for a in accesses:
        if a.cls in ("", "?"):
            continue
        v = vmts.get(a.cls)
        if v and a.off >= v.size:
            oob.append((hex(a.rva), a.cls, hex(a.off), v.size, a.via))
        width_conf[(a.cls, a.off)].add(a.width)
    # 指针证据：字段被当作对象（deref/vcall/dcall）
    ptr_offsets: dict[tuple[str, int], set[int]] = defaultdict(set)
    for c in calls:
        if c.kind in ("field_vcall", "field_dcall"):
            ptr_offsets[(c.cls, c.off)].add(c.rva)
    for (cls, off) in sorted(ptr_offsets):
        if cls in ("", "?"):
            continue
        if not live_ptrs(live, cls, off):
            unlisted.append((cls, hex(off), sorted(hex(x) for x in ptr_offsets[(cls, off)])))
    # 宽度冲突
    width_bad = {k: sorted(v) for k, v in width_conf.items() if len(v) > 1 and k[0] not in ("", "?")}
    # 直接调用目标类 vs 字段运行时类
    cls_of = {r["rva_i"]: r["self_class"] for r in rows}
    anc_cache: dict[str, set[str]] = {}
    def anc(name: str) -> set[str]:
        if name not in anc_cache:
            s, cur, seen = set(), name, 0
            while cur and cur in vmts and seen < 32:
                s.add(cur)
                p = vmts[cur].parent
                cur = by_va[p].name if p in by_va else ""
                seen += 1
            anc_cache[name] = s
        return anc_cache[name]
    direct_bad = []
    direct_unknown = 0
    for c in calls:
        if c.kind != "field_dcall":
            continue
        cands = live_ptrs(live, c.cls, c.off)
        if not cands:
            continue
        x = cls_of.get(c.target, "")
        if x in ("", "?", "lua_State*"):
            direct_unknown += 1
            continue
        if not any(x in anc(cn) for cn in cands):
            direct_bad.append((hex(c.rva), hex(c.site), c.cls, hex(c.off),
                               ",".join(cands), hex(c.target), x))
    print(f"functions_self={len([r for r in rows if r['self_class'] not in ('', '?')])} "
          f"ptr_fields={len(ptr_offsets)} oob={len(oob)} width_conflict={len(width_bad)} "
          f"direct_mismatch={len(direct_bad)} direct_unknown={direct_unknown} unlisted={len(unlisted)}")
    for label, items in (("OOB", oob), ("WIDTH", list(width_bad.items())), ("DIRECT", direct_bad)):
        for it in items[:20]:
            print(" ", label, it)
    for it in unlisted[:15]:
        print("  UNLISTED", it)
    contradictions = len(oob) + len(width_bad) + len(direct_bad)
    print("contradictions=%d" % contradictions)
    return 0 if contradictions == 0 else 1


def cmd_dups(pe, rows, vmts) -> int:
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    md.detail = True
    exact: dict[bytes, list[int]] = defaultdict(list)
    masked: dict[bytes, list[int]] = defaultdict(list)
    for r in rows:
        code = pe.read(r["rva_i"], r["size_i"])
        if not code:
            continue
        exact[code].append(r["rva_i"])
        masked[mask_relocs(code, md)].append(r["rva_i"])
    cls_of = {r["rva_i"]: (r["self_class"] or "?") for r in rows}
    pilot = find_pilot_targets()

    def group_stats(groups, label):
        multi = {k: v for k, v in groups.items() if len(v) > 1}
        cross = [v for v in multi.values() if len({cls_of.get(x, "?") for x in v} - {"?"}) > 1]
        return {
            "groups": len(multi), "members": sum(len(v) for v in multi.values()),
            "cross_class": len(cross), "cross_examples": cross[:5],
        }

    e = group_stats(exact, "exact")
    m = group_stats(masked, "masked")
    pilot_dup = sorted(x for g in masked.values() if len(g) > 1 for x in g if x in pilot)
    sizes = {r["rva_i"]: r["size_i"] for r in rows}
    groups_out = []
    for members in sorted((v for v in masked.values() if len(v) > 1), key=lambda v: (-len(v), v[0])):
        groups_out.append({
            "size": sizes.get(members[0]),
            "members": [{"rva": hex(x), "class": cls_of.get(x, "?"),
                         "pilot": x in pilot} for x in members],
            "cross_class": len({cls_of.get(x, "?") for x in members} - {"?"}) > 1,
        })
    out = {
        "functions": len(rows),
        "policy": "mask call/jmp rel32、[abs] disp32、imm32 in 0x400000..0x800000",
        "exact": {"groups": e["groups"], "members": e["members"], "cross_class": e["cross_class"]},
        "masked": {"groups": m["groups"], "members": m["members"], "cross_class": m["cross_class"]},
        "pilot_targets": len(pilot),
        "pilot_dup": [hex(x) for x in pilot_dup],
        "groups": groups_out,
    }
    (ROOT / "work" / "fn_dups.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"functions={len(rows)} exact_groups={e['groups']} exact_members={e['members']} "
          f"masked_groups={m['groups']} masked_members={m['members']} "
          f"cross_class={m['cross_class']} pilot_dup={len(pilot_dup)}")
    for g in m["cross_examples"]:
        print("  CROSS", [hex(x) for x in g], [cls_of.get(x, "?") for x in g])
    # 自检：同一成员的 masked key 稳定；翻 1 字节后不再属于原簇
    if masked:
        g = max(masked.values(), key=len)
        if len(g) > 1:
            a, b = g[0], g[1]
            ka = mask_relocs(pe.read(a, dict((r["rva_i"], r["size_i"]) for r in rows)[a]), md)
            kb = mask_relocs(pe.read(b, dict((r["rva_i"], r["size_i"]) for r in rows)[b]), md)
            mut = bytearray(ka)
            mut[0] ^= 0xFF
            ok1 = ka == kb
            ok2 = bytes(mut) != kb
            print(f"  SELFTEST same_masked={ok1} mutated_differs={ok2} -> {'PASS' if ok1 and ok2 else 'FAIL'}")
            if not (ok1 and ok2):
                return 1
    return 0


def cmd_show(pe, vmts, rows, live, rva: int) -> int:
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    md.detail = True
    r = next((x for x in rows if x["rva_i"] == rva), None)
    if not r:
        raise SystemExit("no function at %#x" % rva)
    code = pe.read(rva, r["size_i"])
    for ins in md.disasm(code, rva):
        print("%x  %-8s %s" % (ins.address, ins.mnemonic, ins.op_str))
    a, c, ev = scan_function(pe, md, rva, r["size_i"], r["self_class"] or "?", live)
    print("-- class", r["self_class"], "kind", r["kind"], "evidence", r["evidence"])
    v = vmts.get(r["self_class"])
    print("-- vmt", hex(v.va) if v else None, "size", v.size if v else None)
    for x in a:
        print("  F", hex(x.off), "w", x.width, x.kind, x.access, "site", hex(x.site))
    for x in c:
        print("  C", x.kind, "off", hex(x.off), "slot", x.slot, "target", hex(x.target), "site", hex(x.site))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--game", type=Path, default=GAME)
    ap.add_argument("--app", type=Path, default=APP_CSV)
    ap.add_argument("--deep", type=Path, default=DEEP_CSV)
    ap.add_argument("--live", type=Path, default=LIVE_JSON)
    ap.add_argument("--fixes", type=Path, default=ROOT / "mapping" / "app-self-fixes.csv")
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--dups", action="store_true")
    ap.add_argument("--show", type=lambda s: int(s, 0), default=None)
    args = ap.parse_args()

    pe = PE(args.game)
    vmts = load_vmts(pe)
    rows = load_deep(args.deep)
    apply_fixes(rows, args.fixes)
    live = json.loads(args.live.read_text(encoding="utf-8"))["fields"] if args.live.exists() else {}
    print("vmt_classes=%d live_classes=%d live_covered=%d" % (
        len(vmts), len(live), sum(1 for k in live if k in vmts)), file=sys.stderr)

    outdir = ROOT / "work"
    outdir.mkdir(exist_ok=True)
    rc = 0
    if args.report:
        print(json.dumps(cmd_report(pe, vmts, rows, live, outdir), ensure_ascii=False))
    if args.check:
        rc |= cmd_check(pe, vmts, rows, live)
    if args.dups:
        rc |= cmd_dups(pe, rows, vmts)
    if args.show is not None:
        rc |= cmd_show(pe, vmts, rows, live, args.show)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
