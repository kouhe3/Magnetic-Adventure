"""对比 `B2DUMP_CONTACTS` 产出的两份转储（原版 vs 我们），按 (step, 对象) 找首个差异。

用法：
    python tools/dumpdiff.py work/sg_o.txt work/sg_u.txt [--limit 12] [--step 1168]

转储格式（tools/replay_ffi.py:dump_contacts）：
    step N count C
      c <shape1> <shape2> <176B>
      b <body> <160B>
      s <shape> <body> <288B>
      j <joint> <208B>

判据：先比"对象集合"（多了/少了谁），再比字段（float 按 1e-9 相对、指针按映射后的整数值）。
首个差异按 step 升序、kind 顺序（joins/set → contact → body → shape → joint）报出。
"""
import argparse
import ast
import struct
import sys

# ---- 布局（VC9/vendor x86，见 docs/facts.md Critical Context） ----
BODY_FIELDS = [("flags", 0, "u16"), ("c0x", 40, "f"), ("c0y", 44, "f"),
               ("cx", 48, "f"), ("cy", 52, "f"), ("a0", 56, "f"), ("a", 60, "f"),
               ("t0", 64, "f"), ("lvx", 68, "f"), ("lvy", 72, "f"), ("av", 76, "f"),
               ("sleepT", 148, "f")]
# b2Manifold 布局（vendor/box2d-2.0.2/Box2D/Collision/b2Collision.h:55-71）：
#   points[2] 在 +0（每个 32B），normal 在 +64，pointCount 在 +72；contact 里 manifold 从 +64 起
MANIFOLD_POINT = [("lp1x", 0), ("lp1y", 4), ("lp2x", 8), ("lp2y", 12),
                  ("sep", 16), ("nImp", 20), ("tImp", 24)]
MANIFOLD_BASE = 64


def f(bl, off):
    return struct.unpack_from("<f", bl, off)[0]


def u32(bl, off):
    return struct.unpack_from("<I", bl, off)[0]


def parse(path):
    steps = {}
    cur = None
    for line in open(path, encoding="utf-8"):
        if line.startswith("step "):
            _, n, _, c = line.split()
            cur = int(n)
            steps[cur] = {"count": int(c), "c": {}, "b": {}, "s": {}, "j": {}}
        elif cur is None or not line.startswith("  ") or len(line) < 4:
            continue
        else:
            kind, rest = line[2], line[4:]
            if kind == "c":
                a, b, blob = rest.split(" ", 2)
                steps[cur]["c"][(int(a), int(b))] = ast.literal_eval(blob)
            elif kind == "s":
                a, b, blob = rest.split(" ", 2)
                steps[cur]["s"][int(a)] = (int(b), ast.literal_eval(blob))
            elif kind == "b":
                a, blob = rest.split(" ", 1)
                steps[cur]["b"][int(a)] = ast.literal_eval(blob)
            elif kind == "j":
                a, blob = rest.split(" ", 1)
                steps[cur]["j"][int(a)] = ast.literal_eval(blob)
    return steps


KIND = {"c": "contact", "b": "body", "s": "shape", "j": "joint"}


def kd(k):
    return f"{k:#x}" if isinstance(k, int) else f"{k[0]:#x}/{k[1]:#x}"


def fdiff(a, b, tol=1e-9):
    d = abs(a - b)
    return d > tol * max(1.0, abs(a), abs(b))


def cmp_blob(kind, key, ba, bb, out, limit):
    """返回该对象上发现的差异条数（最多写 limit 条）。"""
    n = 0
    if kind == "body":
        for name, off, ty in BODY_FIELDS:
            if ty == "u16":
                va, vb = struct.unpack_from("<H", ba, off)[0], struct.unpack_from("<H", bb, off)[0]
                if va != vb:
                    out.append(f"  {kind} {kd(key)} {name}: {va:#06x} vs {vb:#06x}")
                    n += 1
            else:
                va, vb = f(ba, off), f(bb, off)
                if fdiff(va, vb):
                    out.append(f"  {kind} {kd(key)} {name}: {va:.9g} vs {vb:.9g}")
                    n += 1
    elif kind == "contact":
        for name, off in (("flags", 4), ("mcount", 8), ("toi", 60)):
            va, vb = u32(ba, off), u32(bb, off)
            if va != vb:
                out.append(f"  {kind} {key[0]:#x}/{key[1]:#x} {name}: {va:#x} vs {vb:#x}")
                n += 1
        pc = u32(ba, MANIFOLD_BASE + 72)
        qc = u32(bb, MANIFOLD_BASE + 72)
        if pc == 0 and qc == 0 and not any((u32(ba, 4), u32(bb, 4), u32(ba, 60), u32(bb, 60))):
            return 0            # 空 manifold 且无 flags/toi：残留字段，跳过
        if pc != qc:
            out.append(f"  {kind} {key[0]:#x}/{key[1]:#x} pointCount: {pc} vs {qc}")
            n += 1
            pc = min(pc, qc, 2)
        for j in range(2 if (pc and qc) else 0):
            va = f(ba, MANIFOLD_BASE + 64 + 4 * j)
            vb = f(bb, MANIFOLD_BASE + 64 + 4 * j)
            if fdiff(va, vb):
                out.append(f"  {kind} {key[0]:#x}/{key[1]:#x} n{j}: {va:.9g} vs {vb:.9g}")
                n += 1
        for i in range(pc):
            for name, off in MANIFOLD_POINT:
                va, vb = f(ba, MANIFOLD_BASE + 32 * i + off), f(bb, MANIFOLD_BASE + 32 * i + off)
                if fdiff(va, vb):
                    out.append(f"  {kind} {key[0]:#x}/{key[1]:#x} p{i}.{name}: {va:.9g} vs {vb:.9g}")
                    n += 1
    elif kind == "shape":
        na, nb = u32(ba, 280), u32(bb, 280)
        if na > 8 or nb > 8:
            return 0            # 非 polygon（circle/edge）或已释放：布局不同，不比较
        if na != nb:
            out.append(f"  shape {kd(key)} vertexCount: {na} vs {nb}")
            n += 1
        for base, cnt in ((48, 1), (88, na), (152, na), (216, na)):
            for i in range(cnt * 2):
                off = base + 4 * i
                if off + 4 > min(len(ba), len(bb)):
                    break
                va, vb = f(ba, off), f(bb, off)
                if fdiff(va, vb, 1e-7):
                    out.append(f"  shape {kd(key)} +{off:#x}: {va:.9g} vs {vb:.9g}")
                    n += 1
    else:  # joint：布局未知，按 4 字节 float 粗比（指针位会贡献噪声，只用来排名）
        for off in range(0, min(len(ba), len(bb)) - 3, 4):
            va, vb = u32(ba, off), u32(bb, off)
            if va == vb:
                continue
            fa, fb = f(ba, off), f(bb, off)
            if not (fa == fa and fb == fb) or fdiff(fa, fb, 1e-7):
                out.append(f"  {kind} {kd(key)} +{off:#x}: {fa:.9g} vs {fb:.9g}")
                n += 1
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("orig")
    ap.add_argument("ours")
    ap.add_argument("--limit", type=int, default=12)
    ap.add_argument("--step", type=int, default=0, help="只看这一步")
    a = ap.parse_args()
    O, U = parse(a.orig), parse(a.ours)
    steps = sorted(set(O) | set(U))
    if a.step:
        steps = [s for s in steps if s == a.step]
    shown = 0
    total = 0
    for s in steps:
        if s not in O or s not in U:
            print(f"step {s}: 只有一边有转储")
            continue
        out = []
        o, u = O[s], U[s]
        for kind in ("b", "c", "s"):
            ko, ku = set(o[kind]), set(u[kind])
            if ko != ku:
                out.append(f"  {kind} 集合差异: 少了 {sorted(ko - ku)[:4]} 多了 {sorted(ku - ko)[:4]}")
            key = (lambda k: k) if kind != "c" else (lambda k: k)
            for k in sorted(ko & ku, key=repr):
                if kind == "s":
                    if o[kind][k][0] != u[kind][k][0]:
                        out.append(f"  s {k:#x} body: {o[kind][k][0]:#x} vs {u[kind][k][0]:#x}")
                    cmp_blob("shape", k, o[kind][k][1], u[kind][k][1], out, a.limit)
                else:
                    cmp_blob(KIND[kind], k, o[kind][k], u[kind][k], out, a.limit)
        total += len(out)
        if out:
            print(f"step {s} count {o['count']} vs {u['count']}: {len(out)} 处")
            for line in out[: max(0, a.limit - shown)]:
                print(line)
            shown += len(out)
            if shown >= a.limit:
                print(f"... 截断（--limit {a.limit}）")
                break
    print(f"\n合计差异行: {total}（首差 step: {steps[0] if steps else '-'}）")
    return 0 if total == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
