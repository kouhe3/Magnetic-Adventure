#!/usr/bin/env python3
"""Pak v0.2 只读解析/解包器。

格式（由 `data` 实测 + 偏移校验得出，见 docs/facts.md F05/F17）：
  u32  toc_size            = 24 * (count + 1)
  char magic[25]           = "[Pak Header Info Ver 0.2]"
  rec  entries[count]      = { u8 namelen; char name[..]; pad; u32 off; u32 size } 共 24B
  rec  trailer             = 同上形状，名字是尾部附加文件
  u8   payload[...]        = 偏移相对 (29 + toc_size)

用法:
  python tools/pak.py list   <data>
  python tools/pak.py verify <data>
  python tools/pak.py extract <data> <outdir>
"""
import os
import struct
import sys

MAGIC = b'[Pak Header Info Ver 0.2]'
REC = 24
HEAD = 4 + len(MAGIC)          # 29


def parse(path):
    d = open(path, 'rb').read()
    toc_size, = struct.unpack_from('<I', d, 0)
    if d[4:4 + len(MAGIC)] != MAGIC:
        raise ValueError('bad magic')
    if toc_size % REC:
        raise ValueError(f'toc_size {toc_size} not multiple of {REC}')
    count = toc_size // REC - 1
    if HEAD + toc_size > len(d):
        raise ValueError('toc_size beyond file')

    def rec(pos):
        n = d[pos]
        if not 1 <= n <= 255:
            raise ValueError(f'bad namelen {n} at {pos:#x}')
        name = d[pos + 1:pos + 1 + n]
        off, size = struct.unpack_from('<II', d, pos + 16)
        return {'name': name.decode('latin1'), 'off': off, 'size': size,
                'pat': d[pos + 1 + n:pos + 16].hex()}, pos + REC

    pos = HEAD
    ents = []
    for _ in range(count):
        e, pos = rec(pos)
        ents.append(e)
    trailer, pos = rec(pos)
    base = HEAD + toc_size
    return d, base, ents, trailer


def verify(path):
    d, base, ents, trailer = parse(path)
    problems = []
    exp = 0
    for e in ents:
        if e['off'] != exp:
            problems.append(f"offset gap at {e['name']}: {e['off']} != {exp}")
            break
        exp += e['size']
    data_end = len(d) - base
    trailer_off = trailer['off'] & 0x7FFFFFFF
    print(f"entries={len(ents)} base={base:#x} sum={exp} data_end={data_end} "
          f"trailer={trailer['name']} size={trailer['size']} field={trailer['off']:#x}")
    if exp != data_end - trailer['size']:
        problems.append(f'sum {exp} != data_end - trailer {data_end - trailer["size"]}')
    if trailer_off not in (exp, exp + 0x8000):
        problems.append(f"trailer field {trailer['off']:#x} unexpected (sum={exp:#x})")
    n_png = n_ogg = n_lua = 0
    for e in ents:
        b = d[base + e['off']:base + e['off'] + e['size']]
        if e['name'].endswith('.png'):
            if not b.startswith(b'\x89PNG') or not b.rstrip(b'\0').endswith(b'IEND\xaeB`\x82'):
                problems.append(f'bad png {e["name"]}')
            n_png += 1
        elif e['name'].endswith('.ogg'):
            if not b.startswith(b'OggS'):
                problems.append(f'bad ogg {e["name"]}')
            n_ogg += 1
        elif e['name'].endswith('.lua'):
            if b'\x00' in b:
                problems.append(f'null byte in lua {e["name"]}')
            n_lua += 1
    print(f"png={n_png} ogg={n_ogg} lua={n_lua}")
    print('OK' if not problems else 'PROBLEMS:\n  ' + '\n  '.join(problems))
    return not problems


def extract(path, outdir):
    d, base, ents, trailer = parse(path)
    for e in ents + [trailer]:
        dst = os.path.join(outdir, *e['name'].split('/'))
        os.makedirs(os.path.dirname(dst) or '.', exist_ok=True)
        with open(dst, 'wb') as f:
            f.write(d[base + e['off']:base + e['off'] + e['size']])
    print(f'extracted {len(ents) + 1} files to {outdir}')


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'list':
        _, base, ents, trailer = parse(sys.argv[2])
        for e in ents:
            print(f"{e['off']:10d} {e['size']:9d}  {e['name']}")
        print(f"{'trailer':>20} {trailer['size']:9d}  {trailer['name']}")
    elif cmd == 'verify':
        sys.exit(0 if verify(sys.argv[2]) else 1)
    elif cmd == 'extract':
        extract(sys.argv[2], sys.argv[3])
    else:
        print(__doc__)
