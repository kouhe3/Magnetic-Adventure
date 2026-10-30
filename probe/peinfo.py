#!/usr/bin/env python3
"""PE 只读探针：头/节/导入/关键标记。用法: python probe/peinfo.py <pe-file>"""
import sys, struct, hashlib, math, datetime
from collections import Counter


def entropy(b):
    if not b:
        return 0.0
    n = len(b)
    return -sum(v / n * math.log2(v / n) for v in Counter(b).values())


def main(path, want=None):
    d = open(path, 'rb').read()
    print(path, len(d), hashlib.md5(d).hexdigest())
    e = struct.unpack_from('<I', d, 0x3c)[0]
    if d[e:e + 4] != b'PE\0\0':
        print('not PE')
        return
    coff = e + 4
    machine, nsec, tds, _, _, optsz, chars = struct.unpack_from('<HHIIIHH', d, coff)
    print(f'  machine=0x{machine:04x} sections={nsec} TimeDate={tds} ({datetime.datetime.fromtimestamp(tds, datetime.UTC)}) chars=0x{chars:04x}')
    opt = coff + 20
    magic, = struct.unpack_from('<H', d, opt)
    pe32 = magic == 0x10b
    entry, = struct.unpack_from('<I', d, opt + 16)
    ib, = struct.unpack_from('<I', d, opt + 28)
    subsys, = struct.unpack_from('<H', d, opt + 68)
    print(f'  magic=0x{magic:x} pe32+={not pe32} entry=0x{entry:x} imagebase=0x{ib:x} subsystem={subsys}')
    secs = []
    for i in range(nsec):
        o = opt + optsz + i * 40
        name = d[o:o + 8].rstrip(b'\0').decode('latin1')
        vs, va, rs, ro = struct.unpack_from('<IIII', d, o + 8)
        secs.append((name, va, vs, ro, rs))
        print(f'  sec {name:8s} va=0x{va:08x} vs=0x{vs:08x} raw=0x{ro:08x} rs=0x{rs:08x} ent={entropy(d[ro:ro + rs]):.2f}')

    def rva2off(rva):
        for name, va, vs, ro, rs in secs:
            if va <= rva < va + max(vs, rs):
                return ro + rva - va
        return None

    dd = opt + (96 if pe32 else 112)
    dirs = [struct.unpack_from('<II', d, dd + 8 * i) for i in range(16)]
    names = ['export', 'import', 'resource', 'exception', 'security', 'basereloc', 'debug',
             'arch', 'globalptr', 'tls', 'loadcfg', 'boundimport', 'iat', 'delayimport', 'clr', 'reserved']
    for n, (va, sz) in zip(names, dirs):
        if va:
            print(f'  dir {n:10s} rva=0x{va:08x} size=0x{sz:x}')
    iva, _ = dirs[1]
    if iva:
        off = rva2off(iva)
        while True:
            ilt, _, _, nm, iat = struct.unpack_from('<IIIII', d, off)
            if nm == 0:
                break
            o2 = rva2off(nm)
            dll = d[o2:d.index(b'\0', o2)].decode('latin1')
            thunk = rva2off(ilt or iat)
            fns = []
            while True:
                v, = struct.unpack_from('<I', d, thunk)
                if v == 0:
                    break
                if v & 0x80000000:
                    fns.append(f'ord#{v & 0xffff}')
                else:
                    oo = rva2off(v & 0x7fffffff)
                    fns.append(d[oo + 2:d.index(b'\0', oo + 2)].decode('latin1'))
                thunk += 4
            if want and want.lower() in dll.lower():
                print(f'  IMPORT {dll} ({len(fns)}):')
                for fn in fns:
                    print(f'    {fn}')
            else:
                print(f'  IMPORT {dll} ({len(fns)}): {", ".join(fns[:10])}{" ..." if len(fns) > 10 else ""}')
            off += 20
    for sig, label in [(b'mscoree', '.NET'), (b'Borland', 'Delphi/Borland'), (b'Lua 5.1', 'Lua5.1'),
                       (b'UPX0', 'UPX'), (b'TGLDirectOpenGL', 'GLScene'), (b'TForm', 'VCL forms')]:
        at = d.find(sig)
        if at >= 0:
            print(f'  marker: {label} @0x{at:x} x{d.count(sig)}')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
