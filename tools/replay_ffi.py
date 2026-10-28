"""把转发 DLL 抓到的真实调用序列，离机重放到我们自己的 b2Physics.dll 上做差分。

原理（docs/facts.md F46）：
  * DLL 不是纯函数：world/body/shape/joint 由 DLL 分配，宿主保存这些指针并回传。
    用「原指针 -> 我方指针」映射表翻译实参；映射由每次调用的返回值自动建立。
  * 宿主内存指针（def 结构、out 缓冲、userData）用 Python 侧 scratch 模拟，
    内容取自日志里 arg0..arg2 的 64 字节 dump，并把其中出现的已映射指针替换掉。
  * 每次调用比对：返回值（指针看映射一致性，int/bool 看值，float 跳过——走 ST0）、
    以及 arg0 的出参内存（ddword 级，指针按反向映射容忍）。

用法:
  python tools/replay_ffi.py <log> [--dll PATH] [--start N] [--max N] [--quiet]

`work/replay_progress.txt` 每次调用更新，原生崩溃后用它定位是第几条。
退出码 0 = 无差异；1 = 有差异；-1 = 中途异常/崩溃。
"""
import argparse
import ctypes
import os
import pathlib
import re
import struct
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools'))
import ffi  # noqa: E402

REC_CAP = 256
PROGRESS = ROOT / 'work' / 'replay_progress.txt'


def parse_protos():
    src = (ROOT / 'src' / 'b2physics' / 'b2physics.cpp').read_text(encoding='utf-8')
    pat = re.compile(r'B2API\s+([A-Za-z_][\w\s\*]*?)\s+(b2_\w+)\s*\(([^)]*)\)\s*\{')
    out = {}
    for m in pat.finditer(src):
        ret = ' '.join(m.group(1).split())
        name = m.group(2)
        body = m.group(3).strip()
        params = []
        if body and body != 'void':
            for piece in body.split(','):
                piece = piece.strip()
                if piece:
                    params.append('*' in piece)
        out[name] = (ret, params)
    return out


def restype_of(ret):
    if ret.endswith('*'):
        return ctypes.c_uint32
    if ret == 'void':
        return None
    if ret == 'float':
        return ctypes.c_float
    if ret == 'bool':
        return ctypes.c_bool
    if ret in ('int', 'int32_t'):
        return ctypes.c_int
    return ctypes.c_uint32


class Replayer:
    def __init__(self, dll, protos, quiet=False, max_report=25):
        self.lib = ctypes.CDLL(str(dll))
        self.protos = protos
        self.quiet = quiet
        self.max_report = max_report
        self.ptrmap = {}
        self.rev = {}
        self.scratch = {}
        self.calls = {}
        self.mismatches = []
        self.skipped = {}
        self.n = 0
        self.stats = {'ret': 0, 'out': 0, 'float_skip': 0, 'void': 0}
        self.call_mem = {}

    def fnb(self, name, restype):
        key = (name, restype, 1)
        if key not in self.calls:
            addr = ctypes.cast(getattr(self.lib, name), ctypes.c_void_p).value
            self.calls[key] = ctypes.CFUNCTYPE(restype, ctypes.c_uint32)(addr)
        return self.calls[key]

    def fn(self, name, restype, nparams):
        key = (name, restype, nparams)
        if key not in self.calls:
            args = [ctypes.c_uint32] * max(nparams, 1)
            addr = ctypes.cast(getattr(self.lib, name), ctypes.c_void_p).value
            self.calls[key] = ctypes.CFUNCTYPE(restype, *args)(addr)
        return self.calls[key]

    # --- 宿主内存 scratch ---
    def scratch_for(self, key, mem):
        buf = self.scratch.get(key)
        if buf is None:
            buf = ctypes.create_string_buffer(REC_CAP)
            self.scratch[key] = buf
        if mem:
            data = bytearray(mem)
            for off in range(0, 64, 4):
                d, = struct.unpack_from('<I', data, off)
                if d in self.ptrmap:
                    struct.pack_into('<I', data, off, self.ptrmap[d])
            buf.raw = bytes(data) + b'\0' * (REC_CAP - len(data))
        return buf

    def translate(self, name, v, idx, pre):
        if v == 0:
            return 0, True
        if v in self.ptrmap:
            return self.ptrmap[v], True
        mem = {0: pre[38], 1: pre[39], 2: pre[40]}.get(idx)
        if mem is not None:
            self.call_mem[idx] = mem
            buf = self.scratch_for((name, idx, v), mem)
            return ctypes.addressof(buf), True
        if idx >= 3:
            return 0, False        # 没有内容可用的宿主指针：跳过这条调用
        buf = self.scratch_for((name, idx, v), None)
        return ctypes.addressof(buf), True

    def note(self, n, name, what, detail):
        if len(self.mismatches) < self.max_report:
            self.mismatches.append((n, name, what, detail))
        if not self.quiet and len(self.mismatches) <= self.max_report:
            print(f'  MISMATCH #{n} {name} {what}: {detail}')

    def compare_out(self, n, name, buf, want):
        if buf is None or not any(want):
            return
        self.stats['out'] += 1
        got = buf.raw[:64]
        for off in range(0, 16, 4):
            a, = struct.unpack_from('<I', got, off)
            b, = struct.unpack_from('<I', want, off)
            if a == b:
                continue
            if self.rev.get(a) == b:
                continue
            fa, = struct.unpack('<f', struct.pack('<I', a))
            fb, = struct.unpack('<f', struct.pack('<I', b))
            if fa == fa and fb == fb and abs(fa - fb) <= 1e-6 * max(1.0, abs(fa), abs(fb)):
                self.stats['near'] = self.stats.get('near', 0) + 1
                continue
            if len(self.mismatches) == 0 and os.environ.get('DUMP_FIRST'):
                pm = self.call_mem.get(0, b'')
                print('  pre :', pm.hex(' '))
                print('  post:', bytes(want).hex(' '))
            self.note(n, name, 'out', f'+{off:#x} got={a:#010x} want={b:#010x}')
            return

    def run(self, log, start, maxcalls, ignore):
        pending = None
        for kind, v in ffi.records(log):
            if kind == 'hdr':
                continue
            if kind == 'post':
                if pending:
                    n, name, ret_t, got, buf, seq = pending
                    pending = None
                    want = v[2]
                    self.compare_out(n, name, buf, v[4])
                    rt = restype_of(ret_t)
                    if rt is None:
                        self.stats['void'] += 1
                    elif rt is ctypes.c_float:
                        self.stats['float_skip'] += 1
                    elif ret_t.endswith('*'):
                        self.stats['ret'] += 1
                        if want == 0:
                            if got:
                                self.note(n, name, 'ret', f'got={got:#x} want=null')
                        elif want in self.ptrmap:
                            if got != self.ptrmap[want]:
                                self.note(n, name, 'ret',
                                          f'got={got:#x} want(mapped)={self.ptrmap[want]:#x}')
                        else:
                            self.ptrmap[want] = got
                            self.rev[got] = want
                    else:
                        self.stats['ret'] += 1
                        if rt is ctypes.c_bool:
                            got = int(bool(got))
                            want = int(bool(want))
                        if got != want:
                            if got in (0, 1) and (want & 0xFF) == got:
                                self.stats['bool'] = self.stats.get('bool', 0) + 1
                            else:
                                self.note(n, name, 'ret', f'got={got:#x} want={want:#x}')
                continue

            rid, ret_addr, ecx, edx, seq = v[1], v[2], v[3], v[4], v[5]
            args = v[6:38]
            name = ffi.NAMES[rid] if 0 < rid < len(ffi.NAMES) else None
            if name is None or name not in self.protos:
                self.skipped[name or f'#{rid}'] = self.skipped.get(name or f'#{rid}', 0) + 1
                continue
            if name in ignore:
                self.skipped[name] = self.skipped.get(name, 0) + 1
                continue
            self.n += 1
            if self.n < start:
                continue
            if maxcalls and self.n - start >= maxcalls:
                break
            ret_t, params = self.protos[name]
            self.call_mem = {}
            call_args = []
            ok = True
            buf0 = None
            for i in range(len(params)):
                if not params[i]:
                    call_args.append(args[i])
                    continue
                if 'CallBack' in name:
                    call_args.append(0)          # 回调指针不能瞎调，给 NULL
                    continue
                val, good = self.translate(name, args[i], i, v)
                if not good:
                    ok = False
                    break
                call_args.append(val)
                if i == 0 and (name, 0, args[0]) in self.scratch:
                    buf0 = self.scratch[(name, 0, args[0])]
            if not ok:
                self.skipped[name] = self.skipped.get(name, 0) + 1
                continue
            restype = restype_of(ret_t)
            f = self.fn(name, restype, len(params))
            if self.n % 64 == 0:
                PROGRESS.write_text(f'{self.n} {name}', encoding='utf-8')
            if self.n <= int(__import__('os').environ.get('TRACE_FIRST', '0')):
                print(f'  #{self.n} {name} ' + ' '.join(f'{x:#x}' for x in call_args[:6]))
            got = f(*call_args)
            dbg = os.environ.get('DD_N')
            if dbg and self.n == int(dbg) and name.startswith('b2_Body_'):
                bod = call_args[1] if len(call_args) > 1 else None
                if bod:
                    sl = self.fnb('b2_Body_GetIsSleeping', ctypes.c_bool)(bod)
                    fl = ctypes.c_uint16.from_address(bod).value
                    st = ctypes.c_float.from_address(bod + 148).value
                    vx = ctypes.c_float.from_address(bod + 68).value
                    print(f'  DBG body={bod:#x} asleep={sl} flags={fl:#06x} sleepTime={st:.3f} vx={vx:.3e}')
            pending = (self.n, name, ret_t, got, buf0, seq)
        return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('log')
    ap.add_argument('--dll', default=str(ROOT / 'build' / 'Release' / 'b2Physics.dll'))
    ap.add_argument('--start', type=int, default=1)
    ap.add_argument('--max', type=int, default=0)
    ap.add_argument('--quiet', action='store_true')
    ap.add_argument('--ignore', default='b2_World_SetContactListenerCallBack,b2_World_SetContactFilterCallBack')
    a = ap.parse_args()
    ffi.load_names()
    protos = parse_protos()
    missing = [n for n in ffi.NAMES[1:] if n not in protos]
    if missing:
        print(f'missing protos ({len(missing)}): {missing[:6]}')
    r = Replayer(a.dll, protos, a.quiet)
    print(f'dll={a.dll}\nprotos={len(protos)} log={a.log}')
    rc = r.run(a.log, a.start, a.max, set(a.ignore.split(',')))
    print(f'calls replayed={r.n} skipped={sum(r.skipped.values())} '
          f'checked: ret={r.stats["ret"]} out={r.stats["out"]} skipped_float_ret={r.stats["float_skip"]}')
    if r.skipped:
        top = sorted(r.skipped.items(), key=lambda kv: -kv[1])[:8]
        print('skipped top:', ', '.join(f'{k}={v}' for k, v in top))
    print(f'mismatches={len(r.mismatches)}')
    if r.mismatches:
        print(f'first: {r.mismatches[0]}')
        return 1
    return rc


if __name__ == '__main__':
    sys.exit(main())
