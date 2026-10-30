"""两套 FPC 产物的代码级对应率：精确串 → 容忍重定位 → 逐单元。

用途：判定"某棵候选源码树 + 某组编译选项"是否就是原版用的那一份。
判据不是"跑通"，是 **按同一位移能在目标里找回多少字节**。

用法:
    # 1) 两份 PE 的整体对应率（精确 + 同位空隙）
    python tools/code_match.py cover <target.exe> <candidate.exe> [--tail 0x521000]

    # 2) 逐单元（候选必须是 fpc -Xm 编出来的，旁边有 .map）
    python tools/code_match.py units <target.exe> <candidate.exe>

输出:
    cover: 精确串 B/% + 同位空隙 B + 归因总计 B/%，以及 --tail 之后的覆盖率
    units: 每个 .o 的尺寸/归因/百分比（按尺寸倒序），用来区分
           "这个单元原版没有" (≈0%) / "同代但有小差" (60~90%) / "逐位相同" (>95%)

判据口径（重要）:
    - 只比 .text 段，比的是**字节**，不看符号；
    - "精确串" = 连续 ≥64 B 逐字节相同，锚 24 B；
    - "同位空隙" = 相邻两段精确串的位移相同（±8 B），且空隙内每 4 B 字不同率 ≤30%
      （重定位会把绝对地址改掉，所以必须容忍，否则会低估一个数量级）；
    - 结果对**单元链接顺序**不敏感（锚点在全目标段里搜），但对"同样代码被复制多份"会产生
      重复计入——所以看**目标侧覆盖**（去重后）而不是候选侧。

已知边界:
    - 不区分"代码相同但被 ICF 合并"与"真的没有"；
    - 不处理 >4 B 的跨字重定位（如 8 B 指针或跳转表），这类位置会把串截断；
    - 目标侧覆盖率去重后按集合算，内存与目标 .text 同量级（2 MB 级无压力，30 MB 级会很慢）。
"""
import argparse
import collections
import os
import re
import struct
import sys

K = 24            # 锚点长度
MINRUN = 64       # 计入的最短精确串
GAP_TOL = 0.30    # 同位空隙容忍的字不同率


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
    exact, gap, cov = attribute(cand, tgt, runs)
    print(f"精确 {exact} + 空隙 {gap} = 归因 {len(cov)}/{len(cand)} = {100 * len(cov) / len(cand):.1f}%")
    rows = []
    for k, (a, name) in enumerate(ent[:-1]):
        sz = ent[k + 1][0] - a
        if sz <= 0:
            continue
        s0 = a - 0x401000
        hit = sum(1 for x in range(s0, s0 + sz) if x in cov)
        rows.append((name, sz, hit))
    print(f"\n{'unit':24s} {'size':>8s} {'hit':>8s} {'%':>6s}")
    for name, sz, hit in sorted(rows, key=lambda x: -x[1])[:args.top]:
        print(f"{name:24s} {sz:8d} {hit:8d} {100 * hit / sz:5.1f}%")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name, fn in (("cover", cmd_cover), ("units", cmd_units)):
        p = sub.add_parser(name)
        p.add_argument("target")
        p.add_argument("candidate")
        if name == "cover":
            p.add_argument("--tail", type=lambda s: int(s, 0), default=None)
            p.add_argument("--tail-buckets", action="store_true")
        else:
            p.add_argument("--top", type=int, default=24)
        p.set_defaults(func=fn)
    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
