"""解析转发 DLL 抓到的 FFI 日志（tools/gen_proxy.py + src/proxydll/）。

用法:
  python tools/ffi.py stats <log>
  python tools/ffi.py show <log> <export> [条数]
  python tools/ffi.py sites <log> [export]
  python tools/ffi.py mem <log> <export> <n>      # 打印第 n 条的 m1/m2 内存 dump

依据：docs/facts.md F34/F38（未知布局）、F29/F32/F40（已知布局复核）。
"""
import struct
import sys

HDR = struct.Struct('<8sIII')
REC = struct.Struct('<IIII 32I 64s 64s 64s I')   # 16 + 128 + 192 + 4 = 340

NAMES = [None]


def load_names():
    import pathlib
    root = pathlib.Path(__file__).resolve().parent.parent
    for line in (root / 'src' / 'proxydll' / 'proxy_stubs.c').read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if line.startswith('"b2_'):
            NAMES.append(line.strip('",'))
    return NAMES


def records(path):
    with open(path, 'rb') as f:
        magic, pid, game, orig = HDR.unpack(f.read(HDR.size))
        if magic[:7] != b'B2FFI01':
            raise SystemExit(f'bad magic {magic!r}')
        yield ('hdr', pid, game, orig)
        while True:
            b = f.read(REC.size)
            if len(b) < REC.size:
                return
            v = REC.unpack(b)
            yield ('rec', v)


def rname(i):
    return NAMES[i] if i < len(NAMES) and NAMES[i] else f'#{i}'


def sym(a, game, orig):
    if game and game <= a < game + 0x800000:
        return f'game+0x{a - game:x}'
    if orig and orig <= a < orig + 0x100000:
        return f'orig+0x{a - orig:x}'
    return f'0x{a:08x}'


def main():
    cmd, path = sys.argv[1], sys.argv[2]
    load_names()
    hdr = None
    counts = {}
    sites = {}
    picked = []
    want = sys.argv[3] if len(sys.argv) > 3 else None
    limit = int(sys.argv[4]) if len(sys.argv) > 4 else 3

    for item in records(path):
        if item[0] == 'hdr':
            _, pid, game, orig = item
            hdr = (pid, game, orig)
            continue
        v = item[1]
        rid = v[0]
        name = rname(rid)
        counts[name] = counts.get(name, 0) + 1
        if cmd == 'sites':
            sites.setdefault(name, {}).setdefault(v[1], 0)
            sites[name][v[1]] += 1
        elif cmd == 'show' and name == want and len(picked) < limit:
            picked.append(v)

    if cmd == 'stats':
        pid, game, orig = hdr
        print(f'pid={pid} game=0x{game:08x} orig=0x{orig:08x} calls={sum(counts.values())}')
        for name, c in sorted(counts.items(), key=lambda kv: -kv[1]):
            print(f'{c:9d}  {name}')
        return

    if cmd == 'sites':
        for name, d in sorted(sites.items()):
            if want and name != want:
                continue
            top = sorted(d.items(), key=lambda kv: -kv[1])[:12]
            print(f'{name}  ({sum(d.values())} calls, {len(d)} sites)')
            for ret, c in top:
                print(f'   {c:8d}  {ret:#010x}')
        return

    if cmd == 'show':
        pid, game, orig = hdr
        print(f'{want}: {counts.get(want, 0)} calls total')
        for v in picked:
            rid, ret, ecx, edx = v[0], v[1], v[2], v[3]
            args = v[4:36]
            print(f'\nret={sym(ret, game, orig)} ecx={ecx:08x} edx={edx:08x}')
            for i, a in enumerate(args):
                print(f'  arg{i:<2} {a:#010x}  {struct.unpack("<f", struct.pack("<I", a))[0]:>14.6g}')
            m0, m1, m2 = v[36], v[37], v[38]
            for tag, m, base in (('m0', m0, args[0]), ('m1', m1, args[1]), ('m2', m2, args[2])):
                if any(m):
                    print(f'  {tag} @{base:#010x}:')
                    for o in range(0, 64, 16):
                        q = m[o:o + 16]
                        ints = struct.unpack('<4I', q)
                        flts = struct.unpack('<4f', q)
                        print(f'    +{o:<3} ' + ' '.join(f'{x:08x}' for x in ints)
                              + '   ' + ' '.join(f'{x:>12.5g}' for x in flts))
        return

    raise SystemExit(__doc__)


if __name__ == '__main__':
    main()
