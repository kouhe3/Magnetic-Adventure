"""对比两份 Squall 代理日志（SQFFI01）：结构等价，不比指针。

用法: python tools/squall_ab.py <a.bin> <b.bin> [--show N]
判据: 调用序列逐条相同 —— (函数名, 非指针实参, 返回值)。
      指针实参（>= 0x1000000 且非 0）在不同进程/不同堆里必然不同，只比「是否为 0」。
      退出码 0 = 一致；1 = 有分歧（打印前 N 条，默认 8）。
覆盖边界: 内存 dump（m0/m1）不参与比较；浮点返回值不可见（宿主导入全是 int/void）。
"""
import csv
import pathlib
import struct
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
HDR = struct.Struct("<8sIII")
PRE = struct.Struct("<6I16I128s128s")
POST = struct.Struct("<4I128s128s")
SMALL = 0x1000000


def names():
    d = {}
    with (ROOT / "mapping" / "squall-exports.csv").open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            d[int(r["ordinal"])] = r["name"]
    return d


def load(path):
    d = open(path, "rb").read()
    magic, pid, game_base, orig_base = HDR.unpack_from(d, 0)
    if magic.rstrip(b"\0") != b"SQFFI01":
        raise SystemExit(f"{path}: bad magic {magic!r}")
    nm = names()
    off = HDR.size
    ev = []
    while off < len(d):
        kind, = struct.unpack_from("<I", d, off)
        if kind == 0:
            _, rid, ret, ecx, edx, seq, *rest = struct.unpack_from("<6I16I", d, off)
            args = rest[:16]
            # 只保留可比实参：0 或小整数
            keep = tuple(a for a in args[:8] if a == 0 or a < SMALL)
            ev.append(("call", nm.get(rid, rid), keep))
            off += PRE.size
        else:
            _, rid, rv, seq = struct.unpack_from("<4I", d, off)
            ev.append(("ret", nm.get(rid, rid), rv))
            off += POST.size
    return ev


def main(a_path, b_path, show=8):
    A, B = load(a_path), load(b_path)
    diffs = [(i, a, b) for i, (a, b) in enumerate(zip(A, B)) if a != b]
    print(f"a={len(A)} b={len(B)} diffs={len(diffs)}")
    for i, a, b in diffs[:show]:
        print(f"  [{i}] {a}\n      {b}")
    if len(A) != len(B):
        print(f"  length mismatch: {len(A)} vs {len(B)}")
    return 0 if (not diffs and len(A) == len(B)) else 1


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) < 2:
        print(__doc__)
        sys.exit(2)
    n = 8
    if "--show" in args:
        i = args.index("--show")
        n = int(args[i + 1])
        del args[i:i + 2]
    sys.exit(main(args[0], args[1], n))
