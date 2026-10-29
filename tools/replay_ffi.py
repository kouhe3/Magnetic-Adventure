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
import json
import ctypes
import os
import pathlib
import re
import struct
import sys

FLAG_GROUPS = (('frozen', 0x0002), ('island', 0x0004), ('sleep', 0x0008),
               ('allowSleep', 0x0010), ('bullet', 0x0020), ('fixedRot', 0x0040))
FLAG_KNOWN_MASK = 0x007E


ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools'))
import ffi  # noqa: E402

REC_CAP = 256
PROGRESS = ROOT / 'work' / 'replay_progress.txt'


DLL_OBJECTS = ('b2World', 'b2Body', 'b2Shape', 'b2Joint')


def parse_protos():
    """返回 name -> (ret, [(是否指针, 类型串), ...])。

    区分 DLL 对象指针（b2World/b2Body/b2Shape/b2Joint）和宿主内存指针（def/缓冲区）：
    前者的地址必须来自原版返回值，重放时靠 ptrmap 翻译；后者用 scratch 模拟。
    """
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
                    params.append(('*' in piece, piece))
        out[name] = (ret, params)
    return out


def is_dll_object(type_str):
    """参数串形如 "b2Joint* j"：取类型首词，别把参数名算进去。"""
    t = type_str.replace('const', '').replace('*', '').strip()
    head = t.split()[0] if t.split() else ''
    return head in DLL_OBJECTS


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
        self.stats = {'ret': 0, 'out': 0, 'float_skip': 0, 'void': 0, 'unmapped': 0,
                      'steps': 0, 'bodies': 0, 'digest_bad': 0, 'bodies_bad': 0}
        self.first_digest = None
        self.first_exact = None   # 第一次逐位不等（不受容差影响）
        self.step_bad = {}
        self.step_dev = {}     # 每步 |Δ|/容差 的最大值：看幅度是否增长，而不只是个数
        self.dev_by_field = {}  # 哪个字段在贡献最大偏差
        self.flags_groups = {}  # flags 差异按位分组：sleep/island/bullet/...
        self.flags_only = 0     # flags 有差异但全部 float 字段一致（纯 flags 抖动）
        self.log_contacts = {}  # seq -> {(shape1, shape2)}，来自 kind=3 记录
        self.worst_dev = None   # 全关卡最大偏差的现场（step/body/字段/双方取值）
        self.trace = int(os.environ['B2_TRACE'], 16) if os.environ.get('B2_TRACE') else 0
        self.last_step_ok = False
        self.call_mem = {}
        self.world = 0          # 我们(或被重放 DLL)的 b2World 指针，b2_CreateWorld 返回时记下
        spec = os.environ.get('B2DUMP_CONTACTS', '')
        self.dump_path, self.dump_lo, self.dump_hi = None, 0, -1
        if spec:
            parts = spec.split(',')
            self.dump_path = parts[0]
            self.dump_lo = int(parts[1]) if len(parts) > 1 else 0
            self.dump_hi = int(parts[2]) if len(parts) > 2 else 1 << 30
            open(self.dump_path, 'w', encoding='utf-8').close()

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
            for off in range(0, len(data) - 3, 4):
                d, = struct.unpack_from('<I', data, off)
                if d in self.ptrmap:
                    struct.pack_into('<I', data, off, self.ptrmap[d])
            buf.raw = bytes(data) + b'\0' * (REC_CAP - len(data))
        return buf

    def translate(self, name, v, idx, pre, use_map=True):
        if v == 0:
            return 0, True
        if use_map and v in self.ptrmap:
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

    # --- 接触内部状态转储（摘要覆盖不到的那层，B1 用）---
    # 布局来自 work/shape_off.cpp（VC9 + vendor 头，x86）：
    #   b2World.m_contactList=+102984  m_contactCount=+102992
    #   b2Contact: flags=+4 manifoldCount=+8 next=+16 shape1=+52 shape2=+56
    #   派生类 m_manifold 紧跟基类（sizeof(b2Contact)=64）
    def dump_contacts(self, seq):
        if not self.dump_path or not (self.dump_lo <= seq <= self.dump_hi) or not self.world:
            return
        u32 = ctypes.c_uint32.from_address
        i32 = ctypes.c_int32.from_address
        c = u32(self.world + 102984).value
        lines = [f'step {seq} count {i32(self.world + 102992).value}']
        seen = 0
        bodies = {}
        while c and seen < 4096:
            # 整个 contact 对象前 176 字节：flags/mcount/prev/next/node/shape1/2 + 派生类的 manifold
            blob = ctypes.string_at(c, 176)
            lines.append('  c {} {} {!r}'.format(
                self.rev.get(u32(c + 52).value, u32(c + 52).value),
                self.rev.get(u32(c + 56).value, u32(c + 56).value), blob))
            for off in (52, 56):
                sp = u32(c + off).value
                if sp:
                    b = u32(sp + 12).value
                    if b:
                        bodies[b] = True
            c = u32(c + 16).value
            seen += 1
        # body：flags/xf/sweep(c0,c,a0,a)/lv/av/sleepTime 全在这个窗口里
        for b in bodies:
            lines.append('  b {} {!r}'.format(self.rev.get(b, b), ctypes.string_at(b, 160)))
        # shape：整对象（polygon ~200B：centroid/vertices/normals/coreVertices/count）——
        # 几何本身不摘要里，b2Distance 与 b2CollidePolygons 都吃它
        shapes = {}
        c2 = u32(self.world + 102984).value
        n2 = 0
        while c2 and n2 < 4096:
            for off in (52, 56):
                sp2 = u32(c2 + off).value
                if sp2:
                    shapes[sp2] = True
            c2 = u32(c2 + 16).value
            n2 += 1
        for sp2 in shapes:
            body2 = u32(sp2 + 12).value
            lines.append('  s {} {} {!r}'.format(
                self.rev.get(sp2, sp2), self.rev.get(body2, body2),
                ctypes.string_at(sp2, 288)))

        # joint：整对象（revolute 200B）——冲量、限位状态不在摘要里
        j = u32(self.world + 102956).value
        jn = 0
        while j and jn < 256:
            lines.append('  j {} {!r}'.format(self.rev.get(j, j), ctypes.string_at(j, 208)))
            j = u32(j + 12).value
            jn += 1
        with open(self.dump_path, 'a', encoding='utf-8') as fh:
            fh.write('\n'.join(lines) + '\n')

    # --- post-Step 状态比对 ---
    def check_digest(self, seq, bodies):
        if not bodies:
            return
        self.stats['steps'] += 1
        self.stats['bodies'] += len(bodies)
        dev_max = 0.0
        for rec in bodies:
            # 旧日志里可能残留"已销毁 body"（代理曾只增不减，指针指向已释放内存），
            # 合法标志位只到 0x7E；出现高位就说明这条是堆垃圾，跳过（F86）。
            if rec[1] & ~0x007E:
                self.stats['stale_body'] = self.stats.get('stale_body', 0) + 1
                continue
            ptr, flags, sleep_t, vx, vy, w, px, py, ang, mass, imass, inertia, iinertia = rec
            ours = self.ptrmap.get(ptr)
            if not ours:
                self.note_digest(seq, ptr, 'body', 'missing', ptr)
                self.stats['bodies_bad'] = self.stats.get('bodies_bad', 0) + 1
                continue
            try:
                f = ctypes.c_float.from_address
                i16 = ctypes.c_uint16.from_address
                got = (i16(ours).value, f(ours + 148).value, f(ours + 68).value,
                       f(ours + 72).value, f(ours + 76).value, f(ours + 8).value,
                       f(ours + 12).value, f(ours + 60).value,
                       f(ours + 124).value, f(ours + 128).value,
                       f(ours + 132).value, f(ours + 136).value)
            except Exception as ex:  # noqa: BLE001
                self.note_digest(seq, ptr, 'read', str(ex), 0)
                self.stats['bodies_bad'] = self.stats.get('bodies_bad', 0) + 1
                continue
            if self.trace and ptr == self.trace:
                print(f'  TRACE step {seq} flags {got[0]:#06x}->{flags:#06x} '
                      f'w {got[4]:.4f}->{w:.4f} v ({got[2]:.3f},{got[3]:.3f})->({vx:.3f},{vy:.3f}) '
                      f'p ({got[5]:.3f},{got[6]:.3f})->({px:.3f},{py:.3f}) sleepT {got[1]:.3f}->{sleep_t:.3f} '
                      f'mass {got[8]:.4f}->{mass:.4f} I {got[10]:.4f}->{inertia:.4f} '
                      f'ang {got[7]:.4f}->{ang:.4f}')
            want = (flags, sleep_t, vx, vy, w, px, py, ang, mass, imass, inertia, iinertia)
            names = ('flags', 'sleepTime', 'vx', 'vy', 'w', 'px', 'py', 'angle',
                     'mass', 'invMass', 'I', 'invI')
            state_bad = False
            flags_bad = False
            for n, a, b in zip(names, got, want):
                if n == 'flags':
                    if int(a) != int(b):
                        # 按位分组：休眠/岛标记这类"管线噪声"与 bullet/frozen 这类"真语义"分开
                        d = int(a) ^ int(b)
                        grp = [g for g, bit in FLAG_GROUPS if d & bit]
                        if d & ~FLAG_KNOWN_MASK:
                            grp.append('other')
                        for g in grp:
                            self.flags_groups[g] = self.flags_groups.get(g, 0) + 1
                        self.note_digest(seq, ptr, 'flags',
                                         f'{a:#06x} -> {b:#06x} [{",".join(grp)}]', 1,
                                         f'{px:.3f},{py:.3f}')
                        flags_bad = True
                    continue
                else:
                    tol = {'sleepTime': 1e-3, 'vx': 1e-4, 'vy': 1e-4, 'w': 1e-4,
                           'px': 1e-5, 'py': 1e-5, 'angle': 1e-5,
                           'mass': 1e-4, 'invMass': 1e-4, 'I': 1e-4, 'invI': 1e-4}.get(n, 1e-5)
                    # 质量/惯量这类量级可达几千，绝对容差会低于 float 的 ULP，必须按相对值比
                    scale = max(1.0, abs(a), abs(b)) if n in (
                        'mass', 'invMass', 'I', 'invI') else 1.0
                    if a != b and self.first_exact is None:
                        self.first_exact = {'step': seq, 'body': f'{ptr:#x}', 'field': n,
                                            'ours': float(a), 'theirs': float(b)}
                    dev = abs(a - b) / (tol * scale)      # 1.0 = 刚好踩在容差上
                    if dev > dev_max:
                        dev_max = dev
                    if dev > self.dev_by_field.get(n, 0.0):
                        self.dev_by_field[n] = dev
                    if self.worst_dev is None or dev > self.worst_dev['dev']:
                        self.worst_dev = {'dev': round(dev, 1), 'step': seq,
                                          'body': f'{ptr:#x}', 'field': n,
                                          'ours': round(float(a), 6),
                                          'theirs': round(float(b), 6),
                                          'sleep_ours': bool(got[0] & 0x8),
                                          'sleep_theirs': bool(flags & 0x8)}
                    if a == b or abs(a - b) <= tol * scale:
                        continue
                    self.note_digest(seq, ptr, n, f'{a:.7g} -> {b:.7g}', 2,
                                     f'{px:.3f},{py:.3f}')
                    state_bad = True
                    break
            if flags_bad or state_bad:
                self.stats['bodies_bad'] += 1
                if flags_bad and not state_bad:
                    self.flags_only += 1
        if dev_max > self.step_dev.get(seq, 0.0):
            self.step_dev[seq] = dev_max

    def note_digest(self, seq, body, field, detail, kind, where=''):
        self.stats['digest_bad'] += 1
        self.step_bad[seq] = self.step_bad.get(seq, 0) + 1
        if os.environ.get('DIGEST_ALL') or (self.first_digest is None and not self.quiet):
            print(f'  DIGEST step {seq} body {body:#x} @({where}) {field}: {detail}')
        if self.first_digest is None:
            self.first_digest = {'step': seq, 'body': f'{body:#x}', 'field': field,
                                 'detail': detail, 'kind': kind}

    def run(self, log, start, maxcalls, ignore):
        """日志是**嵌套**的：原版在 CreateJoint / Step 里会触发宿主回调，宿主再调我们的导出，
        所以 pre/post 必须按栈（LIFO）配对，不能假设相邻。
        """
        stack = []
        for kind, v in ffi.records(log):
            if kind == 'hdr':
                continue
            if kind == 'contacts':
                seq, cs = v
                self.log_contacts[seq] = {(a, b) for a, b, _ in cs}
                continue
            if kind == 'digest':
                self.check_digest(v[0], v[1])
                self.dump_contacts(v[0])
                continue
            if kind == 'post':
                rec = stack.pop() if stack else None
                if rec is None:
                    continue
                n, name, ret_t, got, buf, seq, rid = rec
                if rid != v[1]:
                    self.stats['pair_mismatch'] = self.stats.get('pair_mismatch', 0) + 1
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
                        if name == 'b2_CreateWorld':
                            self.world = got
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

            rid, seq = v[1], v[5]
            args = v[6:38]
            name = ffi.NAMES[rid] if 0 < rid < len(ffi.NAMES) else None
            if name is None or name not in self.protos or name in ignore:
                self.skipped[name or f'#{rid}'] = self.skipped.get(name or f'#{rid}', 0) + 1
                stack.append(None)
                continue
            self.n += 1
            if self.n < start:
                stack.append(None)
                continue
            if maxcalls and self.n - start >= maxcalls:
                break
            ret_t, params = self.protos[name]
            self.call_mem = {}
            call_args = []
            if name == 'b2_World_Step':
                _vi = os.environ.get('B2_STEP_VI')
                _pi = os.environ.get('B2_STEP_PI')
                if _vi:
                    args = list(args); args[2] = int(_vi)
                if _pi:
                    args = list(args); args[3] = int(_pi)
            ok = True
            buf0 = None
            for i in range(len(params)):
                if not params[i][0]:
                    call_args.append(args[i])
                    continue
                if 'CallBack' in name:
                    call_args.append(0)
                    continue
                if params[i][1].find('*') >= 0 and is_dll_object(params[i][1]) \
                        and args[i] and args[i] not in self.ptrmap:
                    ok = False
                    self.stats['unmapped'] = self.stats.get('unmapped', 0) + 1
                    break
                # 只有 DLL 对象指针才走映射；def 结构体/缓冲区这类宿主内存永远用 scratch，
                # 否则宿主曾返回过的同地址指针会把 def 解成垃圾。
                _obj = is_dll_object(params[i][1])
                val, good = self.translate(name, args[i], i, v, use_map=_obj)
                if not good:
                    ok = False
                    break
                call_args.append(val)
                if i == 0 and (name, 0, args[0]) in self.scratch:
                    buf0 = self.scratch[(name, 0, args[0])]
            if not ok:
                self.skipped[name] = self.skipped.get(name, 0) + 1
                stack.append(None)
                continue
            restype = restype_of(ret_t)
            f = self.fn(name, restype, len(params))
            if self.n % int(os.environ.get('PROGRESS_EVERY', '8')) == 0:
                PROGRESS.write_text(f'{self.n} {name}', encoding='utf-8')
            if self.n <= int(os.environ.get('TRACE_FIRST', '0')):
                print(f'  #{self.n} {name} ' + ' '.join(f'{x:#x}' for x in call_args[:6]))
            if os.environ.get('DEBUG_ANCHOR') and name == 'b2_Joint_GetAnchor1' \
                    and self.stats.get('dbg_anchor', 0) < 4:
                self.stats['dbg_anchor'] = self.stats.get('dbg_anchor', 0) + 1
                print(f'  [anchor] n={self.n} out={call_args[0]:#x} j={call_args[1]:#x} '
                      f'raw_out={args[0]:#x} raw_j={args[1]:#x} jmap={self.ptrmap.get(args[1], 0):#x}')
            got = f(*call_args)
            if self.trace and args and args[0] == self.trace:
                o = self.ptrmap.get(self.trace) or self.trace
                try:
                    f32 = ctypes.c_float.from_address
                    print(f'  TRCALL {name:<28} v=({f32(o+68).value:8.4f},{f32(o+72).value:8.4f}) '
                          f'w={f32(o+76).value:9.4f} sleepT={f32(o+148).value:7.3f}')
                except Exception:  # noqa: BLE001
                    pass
            stack.append((self.n, name, ret_t, got, buf0, seq, rid))
        if self.log_contacts:
            self.compare_contacts()
        return 0

    def compare_contacts(self):
        """对比接触拓扑：日志记录（原版）vs 我们 DLL 导出的接触表。

        DLL 只在我们这边有指针，所以要反查 ptrmap；按步序号对齐（两边都是每个 Step +1）。
        """
        path = os.environ.get('B2DBG_CONTACTS')
        if not path or not os.path.exists(path):
            self.stats['contacts_skipped'] = 1
            return
        inv = {v: k for k, v in self.ptrmap.items()}
        ours = {}
        with open(path, encoding='utf-8') as f:
            for line in f:
                parts = line.split()
                if len(parts) != 4:
                    continue
                try:
                    seq = int(parts[0]); s1 = int(parts[1]); s2 = int(parts[2])
                except ValueError:
                    continue
                ours.setdefault(seq, set()).add((inv.get(s1, s1), inv.get(s2, s2)))
        miss = extra = steps = 0
        first_diff = None
        for seq, want in self.log_contacts.items():
            if seq not in ours:
                continue
            steps += 1
            got = ours[seq]
            w = {frozenset(p) for p in want}
            g = {frozenset(p) for p in got}
            dm, de = len(w - g), len(g - w)
            miss += dm; extra += de
            if (dm or de) and first_diff is None:
                first_diff = {'step': seq, 'missing': dm, 'extra': de,
                              'missing_pairs': [tuple(hex(x) for x in p) for p in list(w - g)[:3]],
                              'extra_pairs': [tuple(hex(x) for x in p) for p in list(g - w)[:3]]}
        self.stats['contact_steps'] = steps
        self.stats['contact_first'] = first_diff
        self.stats['contact_missing'] = miss
        self.stats['contact_extra'] = extra


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('log')
    ap.add_argument('--dll', default=str(ROOT / 'build' / 'Release' / 'b2Physics.dll'))
    ap.add_argument('--start', type=int, default=1)
    ap.add_argument('--max', type=int, default=0)
    ap.add_argument('--quiet', action='store_true')
    ap.add_argument('--ignore', default='b2_World_SetContactListenerCallBack,b2_World_SetContactFilterCallBack')
    ap.add_argument('--json', action='store_true', help='输出一行 JSON 供 gate.py 解析')
    a = ap.parse_args()
    ffi.load_names()
    protos = parse_protos()
    missing = [n for n in ffi.NAMES[1:] if n not in protos]
    if missing:
        print(f'missing protos ({len(missing)}): {missing[:6]}')
    r = Replayer(a.dll, protos, a.quiet or a.json)
    print(f'dll={a.dll}\nprotos={len(protos)} log={a.log}')
    rc = r.run(a.log, a.start, a.max, set(a.ignore.split(',')))
    print(f'calls replayed={r.n} skipped={sum(r.skipped.values())} '
          f'checked: ret={r.stats["ret"]} out={r.stats["out"]} skipped_float_ret={r.stats["float_skip"]}')
    if r.skipped:
        top = sorted(r.skipped.items(), key=lambda kv: -kv[1])[:8]
        print('skipped top:', ', '.join(f'{k}={v}' for k, v in top))
    if a.json:
        print(json.dumps({
            'ok': True,
            'calls': r.n,
            'steps': r.stats['steps'],
            'bodies': r.stats['bodies'],
            'bodies_bad': r.stats['bodies_bad'],
            'mismatches': len(r.mismatches),
            'first_digest': r.first_digest,
            'first_exact': r.first_exact,
            'step_bad': r.step_bad,
            'step_dev': r.step_dev,
            'dev_by_field': {k: round(v, 1) for k, v in
                             sorted(r.dev_by_field.items(), key=lambda kv: -kv[1])[:6]},
            'flags_groups': dict(sorted(r.flags_groups.items(), key=lambda kv: -kv[1])),
            'flags_only': r.flags_only,
            'stale_body': r.stats.get('stale_body', 0),
            'contacts': {'steps': r.stats.get('contact_steps', 0),
                         'missing': r.stats.get('contact_missing', 0),
                         'extra': r.stats.get('contact_extra', 0),
                         'first': r.stats.get('contact_first')},
            'worst_dev': r.worst_dev,
        }, ensure_ascii=False))
        return 0
    print(f'unmapped_object_args={r.stats.get("unmapped", 0)}')
    print(f'steps={r.stats["steps"]} bodies={r.stats["bodies"]} '
          f'bodies_bad={r.stats["bodies_bad"]} digest_bad={r.stats["digest_bad"]}')
    if r.step_bad:
        ks = sorted(r.step_bad)
        pick = [ks[0], ks[len(ks)//4], ks[len(ks)//2], ks[3*len(ks)//4], ks[-1]]
        print('bad per step (head/mid/tail):', {k: r.step_bad[k] for k in dict.fromkeys(pick)},
              'max', max(r.step_bad.values()))
    if r.first_digest:
        print(f'first digest divergence: {r.first_digest}')
    print(f'mismatches={len(r.mismatches)}')
    if r.mismatches:
        print(f'first: {r.mismatches[0]}')
        return 1
    return rc


if __name__ == '__main__':
    sys.exit(main())
