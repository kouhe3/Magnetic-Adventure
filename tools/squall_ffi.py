"""Squall 代理日志（SQFFI01）解析器。

用法:
  python tools/squall_ffi.py <log> [--show N]     # 默认显示前 20 条
判据: 每条调用应有 pre(kind=0) 与 post(kind=1)，且 seq 递增；pre/post 数量应 1:1。
输出: header + 统计 + 前 N 条（id → mapping/squall-exports.csv 的名字，args 前 3 个 dword）。
覆盖边界: args 只记前 16 个 dword，内存只有 arg0/arg1 的前 128 字节；
          浮点返回值在 ST0 时不可见（本 DLL 的 17 个宿主导入全是 int/void）。
"""
import csv
import pathlib
import struct
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
HDR = struct.Struct("<8sIII")
PRE = struct.Struct("<6I16I128s128s")
POST = struct.Struct("<4I128s128s")


def names():
    d = {}
    with (ROOT / "mapping" / "squall-exports.csv").open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            d[int(r["ordinal"])] = r["name"]
    return d


def main(path, show=20):
    d = open(path, "rb").read()
    magic, pid, game_base, orig_base = HDR.unpack_from(d, 0)
    magic = magic.rstrip(b"\0")
    if magic != b"SQFFI01":
        print(f"bad magic {magic!r}")
        return 1
    print(f"magic={magic.decode()} pid={pid} game={game_base:#x} orig={orig_base:#x} bytes={len(d)}")
    off = HDR.size
    nm = names()
    pre = post = 0
    shown = 0
    while off < len(d):
        kind, = struct.unpack_from("<I", d, off)
        if kind == 0:
            k, rid, ret, ecx, edx, seq, a0, a1, a2 = PRE.unpack_from(d, off)[:9]
            pre += 1
            if shown < show:
                print(f"  [{seq:5d}] call {nm.get(rid, rid):36s} ret={ret:#010x} args=({a0:#x},{a1:#x},{a2:#x})")
                shown += 1
            off += PRE.size
        elif kind == 1:
            k, rid, retval, seq = POST.unpack_from(d, off)[:4]
            post += 1
            if shown < show:
                print(f"  [{seq:5d}]  ret {nm.get(rid, rid):36s} eax={retval:#x} ({retval})")
                shown += 1
            off += POST.size
        else:
            print(f"unknown kind {kind} at {off}")
            return 1
    print(f"pre={pre} post={post} paired={'yes' if pre == post else 'NO'}")
    return 0 if pre == post else 1


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(2)
    n = 20
    if "--show" in args:
        i = args.index("--show")
        n = int(args[i + 1])
        del args[i:i + 2]
    sys.exit(main(args[0], n))
