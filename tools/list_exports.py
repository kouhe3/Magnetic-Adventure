"""导出表导出器：把 PE 的导出表打印成 CSV（ordinal,name），给 tools/gen_proxy.py 当输入。

用法：
    python tools/list_exports.py C:/Windows/SysWOW64/opengl32.dll > mapping/opengl32-exports.csv
    python tools/list_exports.py build/Release/Squall.dll | head

为什么需要：转发/代理 DLL 必须导出**同名同序号**的桩，gen_proxy.py 的输入就是这份 CSV。
注意位数：目标 DLL 是 32 位，读 C:/Windows/System32/opengl32.dll 得到的是 64 位版本、
函数集合与序号都不同；本机 32 位 DLL 在 SysWOW64 下。
"""
import struct
import sys


def parse(path):
    d = open(path, "rb").read()
    e = struct.unpack_from("<I", d, 0x3C)[0]
    if d[e:e + 4] != b"PE\0\0":
        raise SystemExit("not PE")
    coff = e + 4
    _machine, nsec, _tds, _p, _n, optsz, _ch = struct.unpack_from("<HHIIIHH", d, coff)
    opt = coff + 20
    magic, = struct.unpack_from("<H", d, opt)
    pe32 = magic == 0x10B
    secs = []
    for i in range(nsec):
        o = opt + optsz + i * 40
        vs, va, rs, ro = struct.unpack_from("<IIII", d, o + 8)
        secs.append((va, max(vs, rs), ro))

    def rva2off(rva):
        for va, size, ro in secs:
            if va <= rva < va + size:
                return ro + rva - va
        return None

    dd = opt + (96 if pe32 else 112)
    eva, esz = struct.unpack_from("<II", d, dd)
    if not eva:
        raise SystemExit("no export directory")
    off = rva2off(eva)
    (_, _, _maj, _min, _, _base, nfuncs, nnames,
     afuncs, anames, aords) = struct.unpack_from("<IIHHIIIIIII", d, off)
    funcs_off = rva2off(afuncs)
    names_off = rva2off(anames)
    ords_off = rva2off(aords)

    by_index = {}
    for i in range(nnames):
        name_rva, = struct.unpack_from("<I", d, names_off + 4 * i)
        idx, = struct.unpack_from("<H", d, ords_off + 2 * i)
        no = rva2off(name_rva)
        name = d[no:d.index(b"\0", no)].decode("latin1")
        by_index[idx] = name

    rows = []
    for idx in range(nfuncs):
        va, = struct.unpack_from("<I", d, funcs_off + 4 * idx)
        if va == 0:
            continue
        rows.append((idx + 1, by_index.get(idx, "")))
    return rows


def main():
    path = sys.argv[1]
    print("ordinal,name")
    for ordinal, name in parse(path):
        print("%d,%s" % (ordinal, name if name else ("noname_%d" % ordinal)))


if __name__ == "__main__":
    main()
