"""解析转发 DLL 的 FFI 日志（src/proxydll/ + tools/gen_proxy.py）。

日志 = 20 字节头 + 交替的记录：
  kind=0 PreRec  (536B) 调用前：id, 原返回地址, ecx, edx, seq, args[32], args[0] 指向的 64B
  kind=1 PostRec (144B) 调用后：id, 返回值 EAX, seq, args[0] 指向的 64B（出参）
  kind=2 摘要：u32 kind,seq,count,reserved + count×52B{ptr,flags,7×state,mass,invMass,I,invI}

用法:
  python tools/ffi.py stats  <log>
  python tools/ffi.py show   <log> <export> [条数]   # 入参 + def 内存 + 紧随其后的返回
  python tools/ffi.py rets   <log> <export> [条数]   # 返回值 + 出参
  python tools/ffi.py sites  <log> [export]          # 调用点分布（L1 映射）

依据：docs/facts.md F45。
"""
import struct
import sys

HDR = struct.Struct('<8sIII')
PRE2 = struct.Struct('<IIIII I 32I 128s 128s 128s')   # v02: 24 + 128 + 384 = 536
POST2 = struct.Struct('<IIII 128s')                   # v02: 16 + 128 = 144
PRE1 = struct.Struct('<IIIII I 32I 64s 64s 64s')      # v01: 344
POST1 = struct.Struct('<IIII 64s')                    # v01: 80
PRE, POST = PRE2, POST2

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
        global PRE, POST
        if magic[:7] == b'B2FFI02':
            PRE, POST = PRE2, POST2
        elif magic[:7] == b'B2FFI01':
            PRE, POST = PRE1, POST1
        else:
            raise SystemExit(f'bad magic {magic!r}')
        yield ('hdr', (pid, game, orig))
        while True:
            b = f.read(4)
            if len(b) < 4:
                return
            kind, = struct.unpack('<I', b)
            if kind == 0:
                rest = f.read(PRE.size - 4)
                if len(rest) < PRE.size - 4:
                    return
                yield ('pre', PRE.unpack(b + rest))
            elif kind == 1:
                rest = f.read(POST.size - 4)
                if len(rest) < POST.size - 4:
                    return
                yield ('post', POST.unpack(b + rest))
            elif kind == 2:
                rest = f.read(12)          # seq, count, reserved
                if len(rest) < 12:
                    return
                seq, count, _ = struct.unpack('<III', rest)
                bodies = []
                if count:
                    raw = f.read(52 * count)
                    if len(raw) < 52 * count:
                        return
                    for i in range(count):
                        bodies.append(struct.unpack_from('<II11f', raw, i * 52))
                yield ('digest', (seq, bodies))
            else:
                raise SystemExit(f'bad kind {kind} at {f.tell()}')


def rname(i):
    return NAMES[i] if 0 < i < len(NAMES) and NAMES[i] else f'#{i}'


def sym(a, game, orig):
    if game and game <= a < game + 0x800000:
        return f'game+0x{a - game:x}'
    if orig and orig <= a < orig + 0x100000:
        return f'orig+0x{a - orig:x}'
    return f'{a:#010x}'


def dump_mem(tag, m, base):
    print(f'  {tag} @{base:#010x}:')
    for o in range(0, len(m), 16):
        q = m[o:o + 16]
        ints = struct.unpack('<4I', q)
        flts = struct.unpack('<4f', q)
        print(f'    +{o:<3} ' + ' '.join(f'{x:08x}' for x in ints)
              + '   ' + ' '.join(f'{x:>12.5g}' for x in flts))


def main():
    cmd, path = sys.argv[1], sys.argv[2]
    load_names()
    want = sys.argv[3] if len(sys.argv) > 3 else None
    limit = int(sys.argv[4]) if len(sys.argv) > 4 else 3

    hdr = None
    counts = {}
    posts = {}
    sites = {}
    picked = []
    pending = None   # 最近一条匹配 want 的 pre，等待其 post

    digests = 0
    for kind, v in records(path):
        if kind == 'hdr':
            hdr = v
            continue
        if kind == 'digest':
            digests += 1
            continue
        if kind == 'post':
            rid, retval = v[1], v[2]
            posts[rname(rid)] = posts.get(rname(rid), 0) + 1
            if cmd == 'rets' and rname(rid) == want and len(picked) < limit:
                picked.append(v)
            if cmd == 'show' and pending and pending[0] == rid and len(picked) < limit:
                picked.append(('pair', pending[1], v))
                pending = None
            continue
        rid = v[1]
        name = rname(rid)
        counts[name] = counts.get(name, 0) + 1
        if cmd == 'sites':
            sites.setdefault(name, {}).setdefault(v[2], 0)
            sites[name][v[2]] += 1
        elif cmd == 'show' and name == want and len(picked) < limit:
            pending = (rid, v)

    pid, game, orig = hdr

    if cmd == 'stats':
        print(f'pid={pid} game={game:#010x} orig={orig:#010x} calls={sum(counts.values())} '
              f'rets={sum(posts.values())} digests={digests}')
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

    if cmd == 'rets':
        print(f'{want}: {posts.get(want, 0)} post records')
        for v in picked:
            kind, rid, retval, seq, m = v[0], v[1], v[2], v[3], v[4]
            print(f'\nseq={seq} ret={retval:#010x}  float={struct.unpack("<f", struct.pack("<I", retval))[0]:.6g}')
            if any(m):
                dump_mem('post m0', m, 0)
        return

    if cmd == 'show':
        print(f'{want}: {counts.get(want, 0)} calls / {posts.get(want, 0)} rets')
        for item in picked:
            if item[0] == 'pair':
                _, pre, post = item
                kind, rid, ret, ecx, edx, seq = pre[0], pre[1], pre[2], pre[3], pre[4], pre[5]
                args = pre[6:38]
                print(f'\nseq={seq} call@{sym(ret, game, orig)} ecx={ecx:08x} edx={edx:08x}')
                for i, a in enumerate(args[:12]):
                    print(f'  arg{i:<2} {a:#010x}  {struct.unpack("<f", struct.pack("<I", a))[0]:>14.6g}')
                m0 = pre[38]
                if any(m0):
                    dump_mem('pre m0', m0, args[0])
                print(f'  -> ret={post[2]:#010x}  float={struct.unpack("<f", struct.pack("<I", post[2]))[0]:.6g}')
                if any(post[4]):
                    dump_mem('post m0', post[4], args[0])
        return

    raise SystemExit(__doc__)


if __name__ == '__main__':
    main()
