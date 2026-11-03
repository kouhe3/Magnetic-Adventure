#!/usr/bin/env python3
"""应用层函数调用图 / 守卫条件 / 事件-状态分诊（PE + capstone，不依赖 IDA）。

用法：
  python tools/app_graph.py                 # 写 work/app_graph.{json,mmd} + 两张 CSV + 摘要
  python tools/app_graph.py --show RVA      # 打印单函数的出边与守卫（排查）
  python tools/app_graph.py --lvl1          # 额外写 work/app_graph_lvl1.mmd（加载/循环可达子图）
  python tools/app_graph.py --hits PATH     # 额外写 work/app_graph_hits.mmd（某次运行命中子图，边带守卫）
  python tools/app_graph.py --frontier PATH # 额外写 work/app_graph_frontier.mmd（命中→未命中的前沿边 + 守卫）

输入：
  bin/gametop/game.exe、mapping/app-functions.csv、mapping/app-self-map.csv、
  mapping/app-self-fixes.csv、mapping/live-fields.json（运行时指针字段表）。

产出：
  work/app_call_edges.csv   caller, callee, kind(direct/self_vcall/field_vcall/self_dcall/field_dcall),
                            site, slot, guard(最近的前向条件跳转 + 其 cmp/test), guard_site
  work/app_fn_graph.csv     rva, class, ui, in_direct/in_vcall/in_data/in_vmt,
                            reach_loop/reach_dispatch/reach_load, category, guards
  work/app_graph.json       汇总 + 类级边计数 + 未解析间接调用数
  work/app_graph.mmd        类级 Mermaid 图（边权=调用边数，虚/直分列）
  work/app_graph_lvl1.mmd   --lvl1：加载/循环可达函数的明细子图（≤80 节点）

判据：`python tools/app_graph.py` 打印 `functions=… edges=… unresolved_indirect=… categories=…`；
      `--lvl1` 打印 `lvl1_nodes=… lvl1_edges=…`。图只用于分诊，等价判据仍是行为 A/B。

覆盖边界：
  - 只含 app-functions.csv 的 1,012 个 pending 函数之间的边；RTL/LCL/GLScene 外部调用不建边。
  - 虚调用只在接收者类已知时解析（Self 类或字段运行时类）；未知接收者只计 unresolved。
  - 守卫 = 调用点之前最近的一条前向条件跳转及其 cmp/test（线性扫描，不做 CFG/路径敏感）。
  - 事件/状态分诊是启发式：data-ref/VMT 入边 ≈ 事件/虚派发；已知根可达 ≈ 循环/加载/派发。

失效条件：
  game.exe / app-functions.csv / app-self-map.csv / live-fields.json 任一变化后重跑；
  根地址（0x560880/0x57A000/0x58E5A0/0x571610/0x572160/0x5721B0）来自 F342/F383，换版本要重验。
"""
from __future__ import annotations

import argparse
import csv
import json
import struct
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path

import capstone

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import app_layout as AL  # noqa: E402
from app_self import PE  # noqa: E402

X = capstone.x86
GAME = ROOT / "bin" / "gametop" / "game.exe"
APP_CSV = ROOT / "mapping" / "app-functions.csv"
DEEP_CSV = ROOT / "mapping" / "app-self-map.csv"
FIXES = ROOT / "mapping" / "app-self-fixes.csv"
LIVE = ROOT / "mapping" / "live-fields.json"
LUA_CSV = ROOT / "mapping" / "lua-bindings.csv"

# F342/F383：菜单命令派发 / 每帧 DoProgress / 玩家更新 / 关卡选择-构建-启动
ROOTS = {
    0x560880: "dispatch",
    0x57A000: "loop",
    0x58E5A0: "loop",
    0x571610: "load",
    0x572160: "load",
    0x5721B0: "load",
}

UI_ANCESTORS = {"TControl", "TWinControl", "TCustomForm", "TForm", "TApplication",
                "TCustomApplication", "TComponent", "TMenuItem", "TMenu", "TMainMenu"}


@dataclass
class Edge:
    caller: int
    callee: int
    kind: str
    site: int
    slot: int = -1
    guard: str = ""
    guard_site: int = 0


def load_app(pe: PE) -> dict[int, dict]:
    rows = list(csv.DictReader(APP_CSV.open(newline="", encoding="utf-8")))
    out = {}
    for r in rows:
        if r["status"] != "pending":
            continue
        va = int(r["rva"], 16)
        out[va] = {"rva": va, "size": int(r["size"]), "name": r.get("name", "")}
    return out


def guard_scan(insns):
    """返回 {call_site: (guard_text, guard_site)}：最近的前向 jcc + 其前的 cmp/test。"""
    last_cmp = None
    pending = None
    out = {}
    for ins in insns:
        if ins.mnemonic in ("cmp", "test"):
            last_cmp = (ins.address, "%s %s" % (ins.mnemonic, ins.op_str))
        if ins.mnemonic.startswith("j") and ins.mnemonic != "jmp" and ins.operands:
            op = ins.operands[0]
            if op.type == X.X86_OP_IMM and op.imm > ins.address and last_cmp:
                pending = ("%s [%s]" % (ins.mnemonic, last_cmp[1]), last_cmp[0])
            else:
                pending = None
        if ins.mnemonic == "jmp":
            # 无条件跳转之后的条件不再支配后续指令
            pending = None
        if ins.mnemonic == "call" and pending:
            out[ins.address] = pending
    return out


def is_ui(vmts, cls: str) -> bool:
    cur, seen = cls, 0
    by_name = {v.name: v for v in vmts.values()}
    by_va = {v.va: v for v in vmts.values()}
    while cur and cur in by_name and seen < 32:
        if cur in UI_ANCESTORS:
            return True
        p = by_name[cur].parent
        cur = by_va[p].name if p in by_va else ""
        seen += 1
    return False


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--show", type=lambda s: int(s, 0), default=None)
    ap.add_argument("--lvl1", action="store_true")
    ap.add_argument("--max-lvl1", type=int, default=80)
    ap.add_argument("--hits", type=Path, default=None)
    ap.add_argument("--frontier", type=Path, default=None)
    ap.add_argument("--hit-column", choices=["end", "delta"], default="end")
    args = ap.parse_args()

    pe = PE(GAME)
    vmts = AL.load_vmts(pe)
    by_va = {v.va: v for v in vmts.values()}
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    md.detail = True
    funcs = load_app(pe)
    deep = AL.load_deep(DEEP_CSV)
    AL.apply_fixes(deep, FIXES)
    meta = {r["rva_i"]: r for r in deep}
    live = json.loads(LIVE.read_text(encoding="utf-8"))["fields"]
    class_of = {r: (meta.get(r, {}).get("self_class") or "?") for r in funcs}

    # VMT 槽地址表（用于数据引用分类）
    lua_set = {int(r["cfunc"], 16) for r in csv.DictReader(LUA_CSV.open(newline="", encoding="utf-8"))}
    slot_map: dict[int, tuple[str, int]] = {}
    for v in vmts.values():
        for k in range(0, 96):
            addr = v.va + 0x30 + 4 * k
            fn = pe.u32(addr)
            if fn and fn in funcs:
                slot_map[addr] = (v.name, k)

    def resolve_slot(cls: str, slot: int) -> int | None:
        v = vmts.get(cls)
        if not v:
            return None
        f = AL.slot_fn(pe, v.va, slot)
        return f if f in funcs else None

    edges: list[Edge] = []
    unresolved = 0
    guards_per_fn = Counter()
    code_refs: dict[int, list[tuple[int, int]]] = defaultdict(list)  # 目标 -> [(site, caller)]

    for rva, info in funcs.items():
        code = pe.read(rva, info["size"])
        if not code:
            continue
        insns = list(md.disasm(code, rva))
        gmap = guard_scan(insns)
        guards_per_fn[rva] = len(gmap)
        cls = class_of[rva]
        # 1) 直接调用（全部 call rel32 → app 函数）+ 取地址（imm32 == 函数起点）
        for ins in insns:
            if ins.mnemonic == "call" and ins.operands and ins.operands[0].type == X.X86_OP_IMM:
                tgt = ins.operands[0].imm
                if tgt in funcs:
                    g = gmap.get(ins.address, ("", 0))
                    edges.append(Edge(rva, tgt, "direct", ins.address, guard=g[0], guard_site=g[1]))
            if ins.mnemonic in ("call", "jmp") or ins.mnemonic.startswith("j"):
                continue  # 分支/调用的立即数是目标，不是取地址
            for op in ins.operands:
                if op.type == X.X86_OP_IMM and op.imm in funcs and op.imm != ins.address:
                    code_refs[op.imm].append((ins.address, rva))
        # 2) 虚调用 / 字段方法（复用 app_layout 的 taint）
        _, calls, _ = AL.scan_function(pe, md, rva, info["size"], cls, live)
        for c in calls:
            g = gmap.get(c.site, ("", 0))
            if c.kind == "self_vcall":
                tgt = resolve_slot(cls, c.slot) if cls not in ("", "?") else None
                if tgt:
                    edges.append(Edge(rva, tgt, "self_vcall", c.site, c.slot, g[0], g[1]))
                else:
                    unresolved += 1
            elif c.kind == "field_vcall":
                cands = AL.live_ptrs(live, cls, c.off) if cls not in ("", "?") else []
                hit = False
                for cn in cands:
                    tgt = resolve_slot(cn, c.slot)
                    if tgt:
                        edges.append(Edge(rva, tgt, "field_vcall", c.site, c.slot, g[0], g[1]))
                        hit = True
                if not hit:
                    unresolved += 1
            elif c.kind == "field_dcall":
                if c.target in funcs:
                    edges.append(Edge(rva, c.target, "field_dcall", c.site, -1, g[0], g[1]))
            elif c.kind == "self_dcall":
                if c.target in funcs:
                    edges.append(Edge(rva, c.target, "self_dcall", c.site, -1, g[0], g[1]))

    # 3) 数据引用（.data 里指向函数起点的 dword）
    dl, dh = pe.data_range()
    raw = pe.read(dl, dh - dl) or b""
    data_refs: dict[int, list[tuple[int, str, int]]] = defaultdict(list)
    for off in range(0, len(raw) - 4, 4):
        v = struct.unpack_from("<I", raw, off)[0]
        if v in funcs:
            addr = dl + off
            if addr in slot_map:
                cls, k = slot_map[addr]
                data_refs[v].append((addr, "vmt_slot", k))
            else:
                data_refs[v].append((addr, "data", -1))

    # 4) 入边统计 + 根可达
    in_direct = Counter()
    in_vcall = Counter()
    for e in edges:
        if e.kind in ("direct", "self_dcall", "field_dcall"):
            in_direct[e.callee] += 1
        else:
            in_vcall[e.callee] += 1
    in_vmt = Counter()
    in_data = Counter()
    for rva, refs in data_refs.items():
        in_vmt[rva] = sum(1 for _, t, _ in refs if t == "vmt_slot")
        in_data[rva] = sum(1 for _, t, _ in refs if t == "data")
    in_code = Counter({k: len(v) for k, v in code_refs.items()})

    adj: dict[int, set[int]] = defaultdict(set)
    for e in edges:
        adj[e.caller].add(e.callee)

    reach: dict[str, set[int]] = {}
    for kind in ("loop", "dispatch", "load"):
        seen = set()
        stack = [r for r, k in ROOTS.items() if k == kind and r in funcs]
        while stack:
            x = stack.pop()
            if x in seen:
                continue
            seen.add(x)
            stack.extend(adj.get(x, ()))
        reach[kind] = seen

    def mechanisms(rva: int) -> list[str]:
        m = []
        if rva in reach["loop"]:
            m.append("loop")
        if rva in reach["dispatch"]:
            m.append("dispatch")
        if rva in reach["load"]:
            m.append("load")
        if rva in lua_set:
            m.append("lua")
        if in_data[rva]:
            m.append("event_data")
        if in_vmt[rva]:
            m.append("vmt")
        if in_code[rva]:
            m.append("code_ref")
        if in_direct[rva]:
            m.append("direct")
        return m or ["none"]

    def category(rva: int) -> str:
        m = set(mechanisms(rva))
        for k in ("loop", "dispatch", "load"):
            if k in m:
                return "state_" + k
        if "lua" in m:
            return "lua_binding"
        if "event_data" in m or "vmt" in m:
            return "event_virtual"
        if "code_ref" in m:
            return "address_taken"
        if "direct" in m:
            return "direct_unrooted"
        return "unreferenced"

    cats = Counter(category(r) for r in funcs)

    if args.show is not None:
        rva = args.show
        print("== %#x class=%s cat=%s" % (rva, class_of[rva], category(rva)))
        for e in [e for e in edges if e.caller == rva]:
            print("  -> %#08x %-14s %-22s %s" % (e.callee, e.kind, e.guard or "-", class_of[e.callee]))
        return 0

    # 5) 写 CSV
    (ROOT / "work").mkdir(exist_ok=True)
    with (ROOT / "work" / "app_call_edges.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["caller", "caller_class", "callee", "callee_class", "kind", "site", "slot", "guard", "guard_site"])
        for e in sorted(edges, key=lambda e: (e.caller, e.site)):
            w.writerow([hex(e.caller), class_of[e.caller], hex(e.callee), class_of[e.callee],
                        e.kind, hex(e.site), e.slot, e.guard, hex(e.guard_site) if e.guard_site else ""])
    with (ROOT / "work" / "app_fn_graph.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["rva", "class", "ui", "in_direct", "in_vcall", "in_data", "in_vmt", "in_code",
                    "reach_loop", "reach_dispatch", "reach_load", "lua", "mechanisms", "category", "guards"])
        for rva in sorted(funcs):
            cls = class_of[rva]
            w.writerow([hex(rva), cls, int(is_ui(vmts, cls)), in_direct[rva], in_vcall[rva],
                        in_data[rva], in_vmt[rva], in_code[rva], int(rva in reach["loop"]),
                        int(rva in reach["dispatch"]), int(rva in reach["load"]),
                        int(rva in lua_set), ";".join(mechanisms(rva)), category(rva),
                        guards_per_fn[rva]])

    # 6) 类级 Mermaid
    pair = Counter()
    for e in edges:
        a, b = class_of[e.caller], class_of[e.callee]
        pair[(a, b)] += 1
    nodes = sorted({x for p in pair for x in p})
    lines = ["flowchart LR"]
    for i, n in enumerate(nodes):
        lines.append(f'  n{i}["{n}"]')
    idx = {n: i for i, n in enumerate(nodes)}
    for (a, b), c in pair.most_common(60):
        lines.append(f"  n{idx[a]} -->|{c}| n{idx[b]}")
    (ROOT / "work" / "app_graph.mmd").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\r\n")

    # 7) Level-1 子图：load+loop 可达，按出边裁剪
    lvl1_nodes: list[int] = []
    if args.lvl1:
        cand = [r for r in funcs if category(r) in ("state_load", "state_loop")]
        # 只保留 load 种子 2 跳内的节点，避免整棵树
        seeds = [r for r, k in ROOTS.items() if k == "load" and r in funcs]
        keep, frontier = set(seeds), set(seeds)
        for _ in range(2):
            nxt = set()
            for x in frontier:
                nxt |= set(adj.get(x, ()))
            frontier = nxt - keep
            keep |= nxt
        lvl1_nodes = sorted(r for r in keep if r in funcs)
        if len(lvl1_nodes) > args.max_lvl1:
            lvl1_nodes = lvl1_nodes[: args.max_lvl1]
        lines = ["flowchart TD"]
        for i, r in enumerate(lvl1_nodes):
            lines.append(f'  f{i}["{r:#x} {class_of[r]}"]')
        idx = {r: i for i, r in enumerate(lvl1_nodes)}
        for e in edges:
            if e.caller in idx and e.callee in idx:
                g = e.guard.replace('"', "'")
                lab = e.kind + ((" " + g) if g else "")
                lines.append(f'  f{idx[e.caller]} -->|"{lab}"| f{idx[e.callee]}')
        (ROOT / "work" / "app_graph_lvl1.mmd").write_text(
            "\n".join(lines) + "\n", encoding="utf-8", newline="\r\n")
        print("lvl1_nodes=%d lvl1_edges=%d" % (len(lvl1_nodes), sum(
            1 for e in edges if e.caller in idx and e.callee in idx)))

    # 8) 某次运行命中子图（rva,delta CSV；只用 delta>0 的节点）
    if args.hits and args.hits.exists():
        hit = {int(r["rva"], 16) for r in csv.DictReader(args.hits.open(newline="", encoding="utf-8"))
               if int(r.get(args.hit_column, "0")) > 0}
        nodes = sorted(r for r in funcs if r in hit)
        idx = {r: i for i, r in enumerate(nodes)}
        lines = ["flowchart TD"]
        for i, r in enumerate(nodes):
            lines.append(f'  h{i}["{r:#x} {class_of[r]}"]')
        ne = 0
        for e in edges:
            if e.caller in idx and e.callee in idx:
                g = e.guard.replace('"', "'")
                lab = e.kind + ((" " + g) if g else "")
                lines.append(f'  h{idx[e.caller]} -->|"{lab}"| h{idx[e.callee]}')
                ne += 1
        (ROOT / "work" / "app_graph_hits.mmd").write_text(
            "\n".join(lines) + "\n", encoding="utf-8", newline="\r\n")
        print("hits_nodes=%d hits_edges=%d -> work/app_graph_hits.mmd" % (len(nodes), ne))

    # 9) 前沿：命中函数 → 未命中函数（边带守卫）
    if args.frontier and args.frontier.exists():
        col = args.hit_column
        hit = {int(r["rva"], 16) for r in csv.DictReader(args.frontier.open(newline="", encoding="utf-8"))
               if int(r.get(col, "0")) > 0}
        front = [e for e in edges if e.caller in hit and e.callee not in hit]
        nodes = sorted({e.caller for e in front} | {e.callee for e in front})
        idx = {r: i for i, r in enumerate(nodes)}
        lines = ["flowchart LR"]
        for i, r in enumerate(nodes):
            lines.append(f'  q{i}["{r:#x} {class_of[r]}"]')
        for e in front[:120]:
            g = e.guard.replace('"', "'") or "fallthrough"
            lines.append(f'  q{idx[e.caller]} -->|"{e.kind} {g}"| q{idx[e.callee]}')
        (ROOT / "work" / "app_graph_frontier.mmd").write_text(
            "\n".join(lines) + "\n", encoding="utf-8", newline="\r\n")
        print("frontier_nodes=%d frontier_edges=%d -> work/app_graph_frontier.mmd" % (
            len(nodes), len(front)))

    summary = {
        "functions": len(funcs),
        "edges": len(edges),
        "kinds": dict(Counter(e.kind for e in edges)),
        "unresolved_indirect": unresolved,
        "functions_with_guard": sum(1 for r in funcs if guards_per_fn[r]),
        "code_ref_targets": len(code_refs),
        "lua_bindings": len(lua_set),
        "categories": dict(cats),
        "ui_functions": sum(1 for r in funcs if is_ui(vmts, class_of[r])),
        "top_pairs": [{"from": a, "to": b, "n": c} for (a, b), c in pair.most_common(25)],
    }
    (ROOT / "work" / "app_graph.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
    print("functions=%d edges=%d unresolved_indirect=%d functions_with_guard=%d" % (
        summary["functions"], summary["edges"], unresolved, summary["functions_with_guard"]))
    print("kinds", summary["kinds"])
    print("categories", summary["categories"])
    print("ui_functions", summary["ui_functions"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
