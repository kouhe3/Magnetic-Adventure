"""两套 FPC 产物的代码级对应率：精确串 → 容忍重定位 → 逐单元。

用途：判定"某棵候选源码树 + 某组编译选项"是否就是原版用的那一份。
判据不是"跑通"，是 **按同一位移能在目标里找回多少字节**。

用法:
    # 1) 两份 PE 的整体对应率（精确 + 同位空隙）
    python tools/code_match.py cover <target.exe> <candidate.exe> [--tail 0x521000]

    # 2) 逐单元（候选必须是 fpc -Xm 编出来的，旁边有 .map）
    python tools/code_match.py units <target.exe> <candidate.exe>

    # 3) 逐函数（要 capstone）：把某单元的函数按"指令序列"与目标对拍
    python tools/code_match.py funcs <target.exe> <candidate.exe> --unit GLObjects.o

输出:
    cover: 精确串 B/% + 同位空隙 B + 归因总计 B/%，以及 --tail 之后的覆盖率
    units: 每个 .o 的尺寸/归因/百分比（按尺寸倒序），用来区分
           "这个单元原版没有" (≈0%) / "同代但有小差" (60~90%) / "逐位相同" (>95%)
    funcs: 每个函数的 size / 对齐位移 d / 指令序相似度 sim / 目标地址

判据口径（重要）:
    - 只比 .text 段，比的是**字节**，不看符号；
    - "精确串" = 连续 ≥64 B 逐字节相同，锚 24 B；
    - "同位空隙" = 相邻两段精确串的位移相同（±8 B），且空隙内每 4 B 字不同率 ≤30%
      （重定位会把绝对地址改掉，所以必须容忍，否则会低估一个数量级）；
    - 结果对**单元链接顺序**不敏感（锚点在全目标段里搜），但对"同样代码被复制多份"会产生
      重复计入——所以看**目标侧覆盖**（去重后）而不是候选侧。
    - units/cover 的百分比**一律在候选坐标系里算**（cov 是目标偏移，混用会把
      "该单元所在地址窗在目标里被覆盖多少"当成"该单元被找回多少"，两者无关，见 F209）；
    - funcs 的 sim 是**重定位无关**的：操作数归一成 寄存器/立即数/内存(基址:变址:比例)，
      所以"只有 call 目标地址不同"不会扣分；sim≥0.95 = 同码，<0.8 = 不是同一个函数。

已知边界:
    - 不区分"代码相同但被 ICF 合并"与"真的没有"；
    - 不处理 >4 B 的跨字重定位（如 8 B 指针或跳转表），这类位置会把串截断；
    - 目标侧覆盖率去重后按集合算，内存与目标 .text 同量级（2 MB 级无压力，30 MB 级会很慢）。
    - funcs 依赖候选 exe 的 .map 里逐函数的 ` .text.n_<符号>` + 地址/尺寸行；
      目标侧没有符号，边界不参与判定，只按位移窗口切；
    - funcs 的位移只从 24 B 锚点投票得到（不是全局最优搜索），函数被整体搬走时
      可能落在错误窗口，此时 sim 会明显偏低——用 `--unit` 看整单元分布，别单看一个函数。
"""
import argparse
import collections
import os
import re
import struct
import sys
from array import array

K = 24            # 锚点长度
MINRUN = 64       # 计入的最短精确串
GAP_TOL = 0.30    # 同位空隙容忍的字不同率
NO_D = -(2 ** 31)  # dmap 的"无位移"哨兵（0 与负数都是合法位移）


def text_of(path):
    b = open(path, "rb").read()
    lf = struct.unpack_from("<I", b, 0x3C)[0]
    n = struct.unpack_from("<H", b, lf + 6)[0]
    opt = lf + 24
    off = opt + struct.unpack_from("<H", b, lf + 20)[0]
    for i in range(n):
        s = b[off + i * 40: off + i * 40 + 40]
        name = s[:8].rstrip(b"\0").decode("latin1")
        vs, va, rs, ra = struct.unpack_from("<IIII", s, 8)
        if name == ".text":
            return b[ra:ra + rs], va + 0x400000
    raise SystemExit(f"{path}: 没有 .text")


def runs_between(cand, target):
    """cand 的每一段 >=MINRUN 的串在 target 里的位置：(cand_off, target_off, len)。"""
    idx = collections.defaultdict(list)
    for i in range(0, len(target) - K):
        idx[target[i:i + K]].append(i)
    for k in idx:
        idx[k] = idx[k][:6]          # 只留 6 个候选位置，够用且快
    out, i = [], 0
    while i < len(cand) - K:
        c = idx.get(cand[i:i + K])
        if not c:
            i += 1
            continue
        best_len, best_j = 0, 0
        for j in c:
            L = K
            while i + L < len(cand) and j + L < len(target) and cand[i + L] == target[j + L]:
                L += 1
            if L > best_len:
                best_len, best_j = L, j
        if best_len >= MINRUN:
            out.append((i, best_j, best_len))
            i += best_len
        else:
            i += 1
    return out


def attribute(cand, target, runs):
    """精确覆盖 ∪ 同位空隙覆盖（目标侧偏移集合）。"""
    cov = set()
    for _, j, L in runs:
        cov.update(range(j, j + L))
    exact = len(cov)
    gap = 0
    for (s1, j1, L1), (s2, j2, L2) in zip(runs, runs[1:]):
        gs, ge = s1 + L1, s2
        if ge <= gs:
            continue
        d = j1 - s1
        if abs(d - (j2 - s2)) > 8:
            continue
        n = ge - gs
        w = n // 4
        if w <= 0:
            continue
        bad = sum(1 for t in range(w)
                  if target[gs + d + 4 * t: gs + d + 4 * t + 4] != cand[gs + 4 * t: gs + 4 * t + 4])
        if bad / w <= GAP_TOL:
            cov.update(range(gs + d, gs + d + n))
            gap += n
    return exact, gap, cov


def coverage_map(cand, target, runs):
    """候选坐标系下的覆盖图 + 每字节的位移：(cov, dmap, gap_bytes)。

    dmap 对"精确串"和"同位空隙"都填（空隙填的是该段自己的位移），
    这样 `funcs` 才能在 relocation 密集的函数里取到位移样本。
    """
    cov = bytearray(len(cand))
    dmap = array("i", [NO_D]) * len(cand)
    for i, j, L in runs:
        cov[i:i + L] = b"\x01" * L
        dmap[i:i + L] = array("i", [j - i]) * L
    gap = 0
    for (s1, j1, L1), (s2, j2, L2) in zip(runs, runs[1:]):
        gs, ge = s1 + L1, s2
        if ge <= gs:
            continue
        d = j1 - s1
        if abs(d - (j2 - s2)) > 8:
            continue
        n = ge - gs
        w = n // 4
        if w <= 0:
            continue
        bad = sum(1 for t in range(w)
                  if target[gs + d + 4 * t: gs + d + 4 * t + 4] != cand[gs + 4 * t: gs + 4 * t + 4])
        if bad / w <= GAP_TOL:
            cov[gs:ge] = b"\x01" * n
            dmap[gs:ge] = array("i", [d]) * n
            gap += n
    return cov, dmap, gap


def candidate_coverage(cand, target, runs):
    """只要候选侧覆盖（`units` 用）。"""
    cov, _, gap = coverage_map(cand, target, runs)
    return cov, gap


def map_symbols(path):
    """从 fpc -Xm 的 .map 里读逐函数符号：(addr, size, unit, name)。"""
    mp = os.path.splitext(path)[0] + ".map"
    if not os.path.exists(mp):
        raise SystemExit(f"缺 {mp}：候选必须用 fpc -Xm 编译")
    lines = open(mp, encoding="latin1", errors="replace").read().splitlines()
    out = []
    i = 0
    while i < len(lines) - 1:
        if lines[i].startswith(" .text.n_"):
            m = re.match(r"\s+0x([0-9A-Fa-f]{8})\s+0x([0-9A-Fa-f]+)\s+(\S+)", lines[i + 1])
            if m:
                out.append((int(m.group(1), 16), int(m.group(2), 16), m.group(3),
                            lines[i].strip()[len(".text.n_"):]))
            i += 2
        else:
            i += 1
    return out


def _insn_tokens(md, buf, base, limit):
    import capstone
    cs = capstone.x86
    out, n = [], 0
    for ins in md.disasm(buf, base):
        toks = [ins.mnemonic]
        for op in ins.operands:
            if op.type == cs.X86_OP_REG:
                toks.append("r:" + ins.reg_name(op.reg))
            elif op.type == cs.X86_OP_IMM:
                toks.append("i")
            elif op.type == cs.X86_OP_MEM:
                m = op.mem
                toks.append("m:%s:%s:%d" % (
                    ins.reg_name(m.base) if m.base else "-",
                    ins.reg_name(m.index) if m.index else "-", m.scale))
            else:
                toks.append("?")
        out.append(" ".join(toks))
        n += ins.size
        if n >= limit:
            break
    return out


def _sim(md, cand, tgt, f0, size, d):
    import difflib
    a = _insn_tokens(md, cand[f0:f0 + size], 0x401000 + f0, size)
    j = f0 + d
    if j < 0 or j >= len(tgt):
        return 0.0
    b = _insn_tokens(md, tgt[j:j + size + 48], 0x401000 + j, size)
    if not a or not b:
        return 0.0
    return difflib.SequenceMatcher(None, a, b).ratio()


def _find_votes(cand, tgt, f0, size, k=16, samples=6, per_key=3):
    """call 密集的函数里 24 B 锚点会跨过 rel32 而失配；用更短的锚点补位移，
    每个锚点的前几处命中都当候选（谁对由 `_sim` 决定，不在这一步下结论）。"""
    votes = collections.Counter()
    step = max(1, size // samples)
    for off in range(0, max(1, size - k + 1), step):
        key = cand[f0 + off:f0 + off + k]
        if len(key) < k:
            continue
        pos = tgt.find(key)
        for _ in range(per_key):
            if pos < 0:
                break
            votes[pos - off] += 1
            pos = tgt.find(key, pos + 1)
    return votes


def _word_score(cand, tgt, f0, size, d):
    """4 B 字相同率——便宜，用来在候选位移里预排（relocation 会压低它，但排序够用）。"""
    j = f0 + d
    if j < 0 or j + size > len(tgt):
        return 0.0
    n = size // 4
    if n == 0:
        return 0.0
    same = 0
    for t in range(n):
        if cand[f0 + 4 * t:f0 + 4 * t + 4] == tgt[j + 4 * t:j + 4 * t + 4]:
            same += 1
    return same / n


def cmd_cover(args):
    tgt, tbase = text_of(args.target)
    cand, _ = text_of(args.candidate)
    runs = runs_between(cand, tgt)
    exact, gap, cov = attribute(cand, tgt, runs)
    print(f"target .text {len(tgt)}   candidate .text {len(cand)}")
    print(f"精确串 {len(runs)} 段 / {exact} B ({100 * exact / len(cand):.1f}%)")
    print(f"+ 同位空隙 {gap} B")
    print(f"归因 {len(cov)}/{len(cand)} = {100 * len(cov) / len(cand):.1f}%   "
          f"目标侧被覆盖 {len(cov)}/{len(tgt)} = {100 * len(cov) / len(tgt):.1f}%")
    if args.tail:
        tail_off = args.tail - tbase
        tc = sum(1 for x in cov if x >= tail_off)
        print(f"--tail {args.tail:#x} 之后：{tc}/{len(tgt) - tail_off} = {100 * tc / (len(tgt) - tail_off):.1f}%")
    if args.tail_buckets:
        tail_off = args.tail - tbase
        print("\n每 32 KB 桶：")
        for s0 in range(tail_off - (tail_off % 0x8000), len(tgt), 0x8000):
            e = min(s0 + 0x8000, len(tgt))
            hit = sum(1 for x in range(s0, e, 16) if x in cov)
            tot = (e - s0) // 16
            print(f"  {tbase + s0:#08x}  {100 * hit / tot:5.1f}%  {'#' * int(30 * hit / tot)}")


def cmd_units(args):
    tgt, _ = text_of(args.target)
    cand, _ = text_of(args.candidate)
    mp = os.path.splitext(args.candidate)[0] + ".map"
    if not os.path.exists(mp):
        raise SystemExit(f"缺 {mp}：候选必须用 fpc -Xm 编译")
    ent = sorted({(int(m.group(1), 16), m.group(3))
                  for m in (re.match(r"\s+\.text\s+0x([0-9A-Fa-f]+)\s+0x([0-9A-Fa-f]+)\s+(\S+)", l)
                            for l in open(mp, encoding="latin1", errors="replace")) if m})
    runs = runs_between(cand, tgt)
    cov, gap = candidate_coverage(cand, tgt, runs)
    covered = sum(cov)
    exact = covered - gap
    print(f"精确 {exact} + 空隙 {gap} = 归因 {covered}/{len(cand)} = {100 * covered / len(cand):.1f}%")
    rows = []
    for k, (a, name) in enumerate(ent[:-1]):
        sz = ent[k + 1][0] - a
        if sz <= 0:
            continue
        s0 = a - 0x401000
        hit = sum(cov[s0:s0 + sz])
        rows.append((name, sz, hit))
    print(f"\n{'unit':24s} {'size':>8s} {'hit':>8s} {'%':>6s}")
    for name, sz, hit in sorted(rows, key=lambda x: -x[1])[:args.top]:
        print(f"{name:24s} {sz:8d} {hit:8d} {100 * hit / sz:5.1f}%")


def cmd_funcs(args):
    try:
        import capstone
    except ImportError:
        raise SystemExit("funcs 需要 capstone：pip install capstone")
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    md.detail = True
    tgt, _ = text_of(args.target)
    cand, _ = text_of(args.candidate)
    syms = map_symbols(args.candidate)
    want = {args.unit} if args.unit else None
    sel = [s for s in syms if want is None or s[2] in want]
    if not sel:
        raise SystemExit(f"--unit {args.unit}: 该单元没有函数符号")
    runs = runs_between(cand, tgt)
    _, dmap, _ = coverage_map(cand, tgt, runs)
    rows = []
    for a, size, unit, name in sel:
        f0 = a - 0x401000
        if f0 < 0 or f0 + size > len(cand):
            continue
        votes = collections.Counter()
        step = max(1, size // 32)
        for off in range(0, size, step):
            d = dmap[f0 + off]
            if d != NO_D:
                votes[d] += 1
        if size >= 16:
            votes.update(_find_votes(cand, tgt, f0, size))
        rows.append([a, size, unit, name, [d for d, _ in votes.most_common(6)]])
    # 单元内的位移是分段的：把**整个单元**见过的位移都当候选，逐函数取 sim 最高的那个
    # （没有锚点的小函数拿不到自己的位移，只靠邻居会误判）
    for unit in {r[2] for r in rows}:
        grp = [r for r in rows if r[2] == unit]
        pooled = collections.Counter()
        for r in grp:
            for d in r[4]:
                pooled[d] += 1
        unit_ds = [d for d, _ in pooled.most_common(8)]
        dom = unit_ds[0] if unit_ds else None
        for r in grp:
            # 只保留单元主位移 ±64 KB 内的候选：短锚的离群命中（别的单元/别的函数）会
            # 让 sim 假低，看起来像"函数不同"
            r[4] = [d for d in dict.fromkeys(r[4] + unit_ds)
                    if dom is None or abs(d - dom) <= 0x10000]
    out = []
    for a, size, unit, name, cands in rows:
        f0 = a - 0x401000
        best_d, best_s = None, -1.0
        cands = [d for d in cands if d is not None]
        ranked = sorted(cands, key=lambda d: -_word_score(cand, tgt, f0, size, d))[:16]
        for d in ranked:
            s = _sim(md, cand, tgt, f0, size, d)
            if s > best_s:
                best_d, best_s = d, s
        out.append([a, size, unit, name, best_d, 0.0 if best_d is None else best_s])

    # 第二轮：没找准位移的函数，以"自己的最佳 d / 相邻函数的 d"为中心做局部细扫。
    # 单元内的位移是逐函数缓慢漂移的（函数长短有差），粗候选常常差 0xE0 这种量级。
    by_unit = collections.defaultdict(list)
    for r in out:
        by_unit[r[2]].append(r)
    for _, grp in by_unit.items():
        grp.sort(key=lambda r: r[0])
        for i, r in enumerate(grp):
            if r[5] >= 0.90:
                continue
            a, size = r[0], r[1]
            f0 = a - 0x401000
            centers = [r[4]] + [grp[j][4] for j in (i - 1, i + 1) if 0 <= j < len(grp)]
            centers = [c for c in centers if c is not None]
            if not centers:
                continue
            cand_d = set()
            for c in centers:
                for d in range(c - 0x600, c + 0x601, 0x10):
                    if d + f0 >= 0:
                        cand_d.add(d)
            ranked = sorted(cand_d, key=lambda d: -_word_score(cand, tgt, f0, size, d))[:4]
            for d in ranked:
                s = _sim(md, cand, tgt, f0, size, d)
                if s > r[5]:
                    r[4], r[5] = d, s
    rows = [(r[2], r[3], r[1], r[4], r[5]) for r in out]
    if args.unit is None:
        print(f"{'unit':18s} {'funcs':>6s} {'bytes':>8s} {'>=95%':>7s} {'80-95%':>7s} {'<80%':>7s}")
        by = collections.defaultdict(list)
        for r in rows:
            by[r[0]].append(r)
        for unit, rs in sorted(by.items(), key=lambda kv: -sum(x[2] for x in kv[1])):
            tot = sum(x[2] for x in rs) or 1
            hi = sum(x[2] for x in rs if x[4] >= 0.95)
            mid = sum(x[2] for x in rs if 0.8 <= x[4] < 0.95)
            lo = tot - hi - mid
            print(f"{unit:18s} {len(rs):6d} {tot:8d} {100 * hi / tot:6.1f}% {100 * mid / tot:6.1f}% {100 * lo / tot:6.1f}%")
        return
    print(f"{'size':>6s} {'sim':>5s} {'d':>8s}  name")
    for unit, name, size, d, s in sorted(rows, key=lambda r: -r[2])[:args.top]:
        print(f"{size:6d} {s:5.2f} {('' if d is None else hex(d)):>8s}  {name}")
    tot = sum(r[2] for r in rows) or 1
    for lo, hi in ((0.95, 1.01), (0.8, 0.95), (0.0, 0.8)):
        b = sum(r[2] for r in rows if lo <= r[4] < hi)
        print(f"  sim {lo:.2f}-{min(hi, 1.0):.2f}: {b:6d} B {100 * b / tot:5.1f}%")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name, fn in (("cover", cmd_cover), ("units", cmd_units), ("funcs", cmd_funcs)):
        p = sub.add_parser(name)
        p.add_argument("target")
        p.add_argument("candidate")
        if name == "cover":
            p.add_argument("--tail", type=lambda s: int(s, 0), default=None)
            p.add_argument("--tail-buckets", action="store_true")
        elif name == "units":
            p.add_argument("--top", type=int, default=24)
        else:
            p.add_argument("--unit", default=None)
            p.add_argument("--top", type=int, default=24)
        p.set_defaults(func=fn)
    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
