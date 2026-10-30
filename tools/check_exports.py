#!/usr/bin/env python3
"""比较 DLL 导出表（名字 + 序号）与 mapping/*-exports.csv。

用法: python tools/check_exports.py <dll> [csv]
      默认 csv = mapping/b2physics-exports.csv；Squall 用 mapping/squall-exports.csv。
      表头需含 ordinal 与 name 列（其余列忽略）。
      名字为 DllEntryPoint 的行不算导出，比对时跳过。
"""
import struct
import sys


def exports(path):
    d = open(path, 'rb').read()
    e = struct.unpack_from('<I', d, 0x3c)[0]
    coff = e + 4
    nsec, = struct.unpack_from('<H', d, coff + 2)
    optsz, = struct.unpack_from('<H', d, coff + 16)
    opt = coff + 20
    magic, = struct.unpack_from('<H', d, opt)
    dd = opt + (96 if magic == 0x10b else 112)
    exp_rva, exp_size = struct.unpack_from('<II', d, dd)
    secs = []
    for i in range(nsec):
        o = opt + optsz + i * 40
        vs, va, rs, ro = struct.unpack_from('<IIII', d, o + 8)
        secs.append((va, vs, ro, rs))

    def off(rva):
        for va, vs, ro, rs in secs:
            if va <= rva < va + max(vs, rs):
                return ro + rva - va
        raise ValueError('rva not mapped')

    if not exp_rva:
        return {}
    o = off(exp_rva)
    nnames, = struct.unpack_from('<I', d, o + 24)
    base, = struct.unpack_from('<I', d, o + 16)
    names_rva, ords_rva = struct.unpack_from('<II', d, o + 32)
    out = {}
    for i in range(nnames):
        nr, = struct.unpack_from('<I', d, off(names_rva) + 4 * i)
        s = off(nr)
        name = d[s:d.index(b'\0', s)].decode('latin1')
        ordv, = struct.unpack_from('<H', d, off(ords_rva) + 2 * i)
        out[name] = base + ordv
    return out


def main(dll, csv_path='mapping/b2physics-exports.csv'):
    got = exports(dll)
    lines = open(csv_path, encoding='utf-8').read().splitlines()
    head = lines[0].split(',')
    io, iname = head.index('ordinal'), head.index('name')
    want = {}
    for line in lines[1:]:
        cols = line.split(',')
        name = cols[iname]
        if name == 'DllEntryPoint':
            continue
        want[name] = int(cols[io])
    missing = sorted(set(want) - set(got))
    extra = sorted(set(got) - set(want))
    ordinal_mismatch = sorted(n for n in set(want) & set(got) if want[n] != got[n])
    print(f'dll exports={len(got)} expected={len(want)}')
    print(f'missing={len(missing)} extra={len(extra)} ordinal_mismatch={len(ordinal_mismatch)}')
    for label, items in (('missing', missing), ('extra', extra), ('ord', ordinal_mismatch)):
        if items:
            print(f'  {label}: {items[:10]}')
    return not (missing or extra or ordinal_mismatch)


if __name__ == '__main__':
    sys.exit(0 if main(*sys.argv[1:]) else 1)
