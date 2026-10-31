"""应用层函数清单：用 patch 后 GLScene 骨架从 `game.exe` 里减出「非库」函数（T7.1）。

用途：给 T6.4/T7.5 一份可复核的待复原清单（RVA / 大小 / 指令数 / 直接调用者数）。
判据：候选函数与目标函数的**指令序相似度** sim>=0.95（重定位无关）⇒ 记为库；
      目标侧 0x521000 之上、未被任何候选覆盖的函数 = 待定（应用层上界）。
      清单是**上界**：骨架没链到的 GLScene 单元也会落在 leftover 里。

用法:
    # 1) 目标函数表（IDA 里导出一次；work/ 已 gitignore）
    python - <<'EOF'
    import json
    rows=[{"start":f.start_ea,"end":f.end_ea,"name":f.name} for f in db.functions.get_all()]
    json.dump(rows, open("work/target_funcs.json","w"), ensure_ascii=False)
    EOF

    # 2) 编库骨架（不含宿主代码）并跑清单
    python tools/glskel_build.py work/glscene_patch work/inv_skel3 tools/glskel9.pas
    python tools/app_inventory.py bin/gametop/game.exe work/inv_skel3/glskel9.exe \
        --json work/app_inventory.json --csv mapping/app-functions.csv

前置：FPC 2.2.4 + 自编 LCL 0.9.28.3（见 tasks/HANDOFF.MD §3.2）；patch 树 `work/glscene_patch`。
输出：JSON（汇总 + per_unit + leftover_all）与 CSV（rva,size,insns,callers,status,name）。
      status: `shim` = 单条 jmp 的导入桩（编译器生成，不需要复原）；`pending` = 待复原。

边界:
    - sim 只比指令序列，不是行为等价；sim>=0.95 也可能漏掉真实差异（本项目以 F213 的
      1,054 函数 0 残差自证过工具，但那只覆盖库层）。
    - 只覆盖骨架链接到的 GLScene 单元；补单元后 leftover 会缩小（实测 1,078→1,039→1,030）。
    - 目标函数边界来自 IDA；函数表的 16 B 对齐/尾部填充会影响「大小」列。
    - `callers` 只数 E8 rel32 直接调用；虚方法（vtable）与函数指针调用不计。
"""
import argparse
import collections
import glob
import json
import os
import struct
import sys

import capstone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import code_match as cm

BOUNDARY = 0x521000
IMAGE_BASE = 0x401000


def build_matches(target, candidate):
    tgt, _ = cm.text_of(target)
    cand, _ = cm.text_of(candidate)
    syms = cm.map_symbols(candidate)
    tree = "work/glscene_patch"
    pas = glob.glob(tree + "/Source/**/*.pas", recursive=True)
    gl_units = {os.path.splitext(os.path.basename(p))[0] + ".o" for p in pas}
    sel = [s for s in syms if s[2] in gl_units]

    runs = cm.runs_between(cand, tgt)
    _, dmap, _ = cm.coverage_map(cand, tgt, runs)
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    md.detail = True

    rows = []
    for a, size, unit, name in sel:
        f0 = a - IMAGE_BASE
        if f0 < 0 or f0 + size > len(cand):
            continue
        votes = collections.Counter()
        step = max(1, size // 32)
        for off in range(0, size, step):
            d = dmap[f0 + off]
            if d != cm.NO_D:
                votes[d] += 1
        if size >= 16:
            votes.update(cm._find_votes(cand, tgt, f0, size))
        rows.append([a, size, unit, name, [d for d, _ in votes.most_common(6)]])

    # 单元内位移分段：整单元见过的位移都当候选，限制在单元主位移 ±64 KB
    for unit in {r[2] for r in rows}:
        grp = [r for r in rows if r[2] == unit]
        pooled = collections.Counter()
        for r in grp:
            for d in r[4]:
                pooled[d] += 1
        unit_ds = [d for d, _ in pooled.most_common(8)]
        dom = unit_ds[0] if unit_ds else None
        for r in grp:
            r[4] = [d for d in dict.fromkeys(r[4] + unit_ds)
                    if dom is None or abs(d - dom) <= 0x10000]

    out = []
    for a, size, unit, name, cands in rows:
        f0 = a - IMAGE_BASE
        ranked = sorted([d for d in cands if d is not None],
                        key=lambda d: -cm._word_score(cand, tgt, f0, size, d))[:16]
        best_d, best_s = None, -1.0
        for d in ranked:
            s = cm._sim(md, cand, tgt, f0, size, d)
            if s > best_s:
                best_d, best_s = d, s
        out.append([a, size, unit, name, best_d, best_s])

    # 灰带（0.80–0.95）局部细扫；<0.80 = 骨架里没有对应代码，扫也救不回来
    for r in out:
        if r[5] >= 0.95 or r[4] is None:
            continue
        a, size = r[0], r[1]
        f0 = a - IMAGE_BASE
        cand_d = {d for d in range(r[4] - 0x600, r[4] + 0x601, 0x10) if d + f0 >= 0}
        ranked = sorted(cand_d, key=lambda d: -cm._word_score(cand, tgt, f0, size, d))[:4]
        for d in ranked:
            s = cm._sim(md, cand, tgt, f0, size, d)
            if s > r[5]:
                r[4], r[5] = d, s

    matched = []
    for a, size, unit, name, d, s in out:
        if d is None:
            continue
        t0 = a + d
        if IMAGE_BASE <= t0 and t0 + size <= IMAGE_BASE + len(tgt) and s >= 0.95:
            matched.append((t0, size, s, unit, name))
    return tgt, md, out, matched


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("target")
    ap.add_argument("candidate")
    ap.add_argument("--target-funcs", default="work/target_funcs.json")
    ap.add_argument("--json", default="work/app_inventory.json")
    ap.add_argument("--csv", default=None)
    args = ap.parse_args()

    tgt, md, out, matched = build_matches(args.target, args.candidate)
    upper = [f for f in json.load(open(args.target_funcs, encoding="utf-8"))
             if f["start"] >= BOUNDARY]
    by_page = collections.defaultdict(list)
    exact = {}
    for t0, size, s, unit, name in matched:
        by_page[t0 >> 12].append((t0, size, s, unit, name))
        if t0 >= BOUNDARY:
            prev = exact.get(t0)
            if prev is None or s > prev[0]:
                exact[t0] = (s, size, unit, name)

    def overlap_hit(f):
        best = None
        for page in range(f["start"] >> 12, ((f["end"] - 1) >> 12) + 1):
            for t0, size, s, unit, name in by_page.get(page, ()):
                lo, hi = max(t0, f["start"]), min(t0 + size, f["end"])
                if hi > lo and (hi - lo) >= 0.6 * min(size, f["end"] - f["start"]):
                    if best is None or s > best[0]:
                        best = (s, unit, name, t0)
        return best

    hit, left = [], []
    for f in upper:
        e = exact.get(f["start"]) or overlap_hit(f)
        if e:
            hit.append((f, e))
        else:
            left.append(f)

    callers = collections.Counter()
    for i in range(len(tgt) - 5):
        if tgt[i] == 0xE8:
            to = IMAGE_BASE + i + 5 + struct.unpack_from("<i", tgt, i + 1)[0]
            if IMAGE_BASE <= to < IMAGE_BASE + len(tgt):
                callers[to] += 1

    def insn_stats(f):
        buf = tgt[f["start"] - IMAGE_BASE:f["end"] - IMAGE_BASE]
        ins = list(md.disasm(buf, f["start"]))
        return len(ins), sum(1 for x in ins if x.mnemonic.startswith("j") or
                             x.mnemonic in ("call", "ret", "retn")), (
            1 if len(ins) == 1 and ins[0].mnemonic == "jmp" else 0)

    left_stats = []
    for f in left:
        n, br, shim = insn_stats(f)
        left_stats.append({"start": f["start"], "size": f["end"] - f["start"], "name": f["name"],
                           "insns": n, "branches": br, "callers": callers.get(f["start"], 0),
                           "shim": shim})

    buckets = [(0, 32), (33, 64), (65, 128), (129, 256), (257, 512), (513, 1024), (1025, 1 << 30)]
    hist = []
    for lo, hi in buckets:
        g = [x for x in left_stats if lo <= x["size"] <= hi]
        hist.append({"lo": lo, "hi": hi, "funcs": len(g), "bytes": sum(x["size"] for x in g),
                     "insns": sum(x["insns"] for x in g)})

    result = {
        "boundary": BOUNDARY,
        "upper_funcs": len(upper),
        "upper_bytes": sum(f["end"] - f["start"] for f in upper),
        "matched_095": {"funcs": len(hit), "bytes": sum(f["end"] - f["start"] for f, _ in hit)},
        "leftover": {"funcs": len(left), "bytes": sum(f["end"] - f["start"] for f in left),
                     "insns": sum(x["insns"] for x in left_stats),
                     "shims": sum(x["shim"] for x in left_stats)},
        "hist": hist,
        "leftover_all": left_stats,
        "matched_all": [[t0, size, round(s, 3), unit, name] for t0, size, s, unit, name in matched],
    }
    json.dump(result, open(args.json, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    if args.csv:
        with open(args.csv, "w", encoding="utf-8", newline="") as fh:
            fh.write("rva,size,insns,callers,status,name\r\n")
            for x in left_stats:
                fh.write("%08x,%d,%d,%d,%s,%s\r\n" % (
                    x["start"], x["size"], x["insns"], x["callers"],
                    "shim" if x["shim"] else "pending", x["name"]))
        print("csv:", args.csv, len(left_stats), "rows")

    print(json.dumps({k: result[k] for k in ("upper_funcs", "upper_bytes", "matched_095", "leftover")},
                     ensure_ascii=False, indent=1))
    print("hist:", json.dumps(hist, ensure_ascii=False))


if __name__ == "__main__":
    main()
