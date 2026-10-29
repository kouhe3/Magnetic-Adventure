#!/usr/bin/env python3
"""两个 pak 的资源级差分（按内容 hash，不含文件名）。用法: python probe/assetdiff.py <a.data> <b.data>"""
import sys, re, hashlib
from collections import Counter

PNG_SIG = b'\x89PNG\r\n\x1a\n'


def png_hashes(d):
    out = []
    for m in re.finditer(re.escape(PNG_SIG), d):
        p = m.start()
        e = d.find(b'IEND', p)
        out.append(hashlib.md5(d[p:e + 8]).hexdigest() if e > 0 else 'trunc')
    return out


def ogg_hashes(d):
    return [hashlib.md5(d[m.start():m.start() + 4096]).hexdigest() for m in re.finditer(b'OggS', d)]


def main(pa, pb):
    da, db = open(pa, 'rb').read(), open(pb, 'rb').read()
    for name, fn in (('png', png_hashes), ('ogg-page', ogg_hashes)):
        a, b = fn(da), fn(db)
        print(f'{name}: A={len(a)} B={len(b)} common={len(set(a) & set(b))} onlyA={len(set(a) - set(b))} onlyB={len(set(b) - set(a))}')
    ca = Counter(re.findall(rb'[ -~]{6,}', da)); cb = Counter(re.findall(rb'[ -~]{6,}', db))
    print(f'ascii strings: A={len(ca)} B={len(cb)} common={len(set(ca) & set(cb))}')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
