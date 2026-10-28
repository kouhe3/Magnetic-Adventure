#!/usr/bin/env python3
"""Pak v0.2 只读探针 + 明文 Lua/资源普查。用法: python probe/pakscan.py <data-file>"""
import sys, re, struct, hashlib
from collections import Counter

MAGIC_LEN = 25  # "[Pak Header Info Ver 0.2]"


def toc(d):
    hs, = struct.unpack_from('<I', d, 0)
    magic = d[4:4 + MAGIC_LEN].decode('latin1')
    pos = 4 + MAGIC_LEN
    ents = []
    while pos + 1 < hs:
        n = d[pos]
        if n == 0 or n > 200:
            break
        pos += 1
        name = d[pos:pos + n].decode('latin1'); pos += n
        # 记录尾: 4B 常量标记 + 4B 偏移 + 4B 大小（字段边界仍待证）
        expect = 0 if not ents else ents[-1][2] + ents[-1][3]
        cand = next((skip for skip in (0, 1)
                     if pos + 12 + skip <= len(d)
                     and struct.unpack_from('<I', d, pos + skip + 4)[0] == expect), None)
        if cand is None:
            break
        pos += cand
        stamp, off, sz = struct.unpack_from('<III', d, pos)
        ents.append((name, stamp, off, sz)); pos += 12
    return d, hs, magic, ents, pos


def main(p):
    d = open(p, 'rb').read()
    hs, magic = struct.unpack_from('<I', d, 0)[0], d[4:4 + MAGIC_LEN].decode('latin1')
    print(f'{p} size={len(d)} toc_size={hs} magic={magic!r}')
    _, _, _, ents, end = toc(d)
    print(f'  TOC parsed entries={len(ents)} parse_end={end} (toc_size={hs})')
    print('  ext:', dict(sorted(Counter((e[0].rsplit(".", 1)[-1] if "." in e[0] else "").lower() for e in ents).items(), key=lambda x: -x[1])[:12]))
    print('  first3:', ents[:3])
    fns = sorted(set(re.findall(rb'\nfunction ([A-Za-z_][\w.:]*)\(', d)))
    print(f'  lua top-level functions={len(fns)} sample={[f.decode() for f in fns[:8]]}')
    print(f'  lua-source bytes: {len(b"".join(re.findall(rb"[ \t\r\n\x20-\x7e]{200,}", d)))}')
    print(f'  png sigs={d.count(bytes.fromhex("89504e470d0a1a0a"))} ogg sigs={d.count(b"OggS")} lua names={d.count(b".lua")}')
    print(f'  gzip streams={len(re.findall(rb"\x1f\x8b\x08", d))} utf8-cjk={len(re.findall(rb"(?:[\xe4-\xe9][\x80-\xbf]{2})", d))}')
    print('  md5:', hashlib.md5(d).hexdigest())


if __name__ == '__main__':
    main(sys.argv[1])
