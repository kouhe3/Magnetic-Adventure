#!/usr/bin/env python3
"""资产索引：把两个 pak 的条目合成一张表（名称/类型/大小/hash/像素 hash/OGG 页数）。

用法: python tools/assetindex.py bin/baseline/data bin/gametop/data mapping/assets.csv
"""
import hashlib
import io
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(__file__))
from pak import parse  # noqa: E402


def png_info(blob):
    from PIL import Image
    im = Image.open(io.BytesIO(blob))
    im.load()
    px = hashlib.md5(im.convert('RGBA').tobytes()).hexdigest()
    return im.width, im.height, px


def ogg_info(blob):
    pages = 0
    i = 0
    serials = set()
    while True:
        i = blob.find(b'OggS', i)
        if i < 0 or i + 27 > len(blob):
            break
        serial, = struct.unpack_from('<I', blob, i + 14)
        nseg = blob[i + 26]
        body = sum(blob[i + 27:i + 27 + nseg])
        serials.add(serial)
        pages += 1
        i = i + 27 + nseg + body
    return pages, len(serials)


def load(path):
    d, base, ents, trailer = parse(path)
    out = {}
    for e in list(ents) + [trailer]:
        blob = d[base + e['off']:base + e['off'] + e['size']]
        out[e['name']] = blob
    return out


def main(a_path, b_path, out_path):
    A, B = load(a_path), load(b_path)
    rows = ['name,ext,status,size_a,size_b,md5_a,md5_b,png_w,png_h,pixel_md5,ogg_pages,ogg_serials']
    for name in sorted(set(A) | set(B)):
        a, b = A.get(name), B.get(name)
        ext = os.path.splitext(name)[1].lower().lstrip('.')
        status = 'same' if a is not None and b is not None and a == b else (
            'only_a' if b is None else 'only_b' if a is None else 'diff')
        w = h = px = pages = serials = ''
        probe = a if a is not None else b
        try:
            if ext == 'png' and probe is not None:
                w, h, px = png_info(probe)
            elif ext == 'ogg' and probe is not None:
                pages, serials = ogg_info(probe)
        except Exception:
            pass
        md5a = hashlib.md5(a).hexdigest() if a is not None else ''
        md5b = hashlib.md5(b).hexdigest() if b is not None else ''
        rows.append(','.join([name, ext, status, str(len(a) if a is not None else ''),
                              str(len(b) if b is not None else ''), md5a, md5b,
                              str(w), str(h), px, str(pages), str(serials)]))
    os.makedirs(os.path.dirname(out_path) or '.', exist_ok=True)
    open(out_path, 'w', encoding='utf-8').write('\n'.join(rows) + '\n')
    from collections import Counter
    print(f'{len(rows) - 1} assets -> {out_path}')
    print(Counter(r.split(',')[2] for r in rows[1:]))


if __name__ == '__main__':
    main(*sys.argv[1:4])
