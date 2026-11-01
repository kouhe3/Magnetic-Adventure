"""按调用点归因 b2Physics 调用，并解码已知结构（B2FFI02 日志）。

用法:
  python tools/b2_sites.py <log> sites [--export NAME] [--top N]
  python tools/b2_sites.py <log> bodies
  python tools/b2_sites.py <log> xforms [--lua <lvlNN.jsonl>]
  python tools/b2_sites.py <log> shapes
  python tools/b2_sites.py <log> joints
  python tools/b2_sites.py <logA> compare <logB>
      [--stop-at-step]    # 只比首次 b2_World_Step 之前（关卡 init）的调用
      [--joint-limit N]   # 只比前 N 个关节（录制的动态接触会追加关节）
      [--setter-limit N]  # 只比前 N 个 shape/body setter（一次关卡 init 的条数）
      [--body-limit N]    # 只比前 N 个 body / 设位组（录制可能含后续关卡）
      [--shape-limit N]   # 只比前 N 个 shape

判据:
  * sites   —— 每个 (export, 返回地址) 的调用数。返回地址 = 宿主里的调用点，
               用来把 b2 调用归到 app 函数（docs/facts.md F232/F236 的函数表）。
  * bodies  —— `b2_World_CreateBody` 的 def（world / angularDamping / linearDamping /
               allowSleep / fixedRotation / isBullet），用于区分世界边界墙与关卡对象。
  * xforms  —— `b2_Body_SetXForm` 的 (x, y, angle)；按 `args[0]`（body 指针）分组，
               一组的首条记录视为创建位置。
  * xforms --lua —— 把 body 组按出现顺序与 Lua 建体绑定的坐标实参对齐；
               PASS = 每组的 (x, y) 与该绑定实参逐项相同（|Δ| <= 1e-6），
               带角度的绑定再比第二组内的 angle。首个分歧打印对象序号与两侧数值。
  * shapes  —— `b2_Body_CreateShape_Circle|Box|Polygon` 的 def（body / 摩擦 / 弹性 /
               密度 / sensor / localPos 或半宽高），按日志顺序；用于读出工厂常量。
  * compare —— 两份日志的建体/设位/形状序列逐项比较（指针不参与）：
               bodies 比 allowSleep/fixedRot/bullet/damping；xforms 比每组首条 (x,y) 与
               第二条 angle；shapes 比名称与全部数值。PASS = 逐项 |Δ| <= 1e-6。
               setters 比 SetDensity/Friction/Restitution/Filter/ReFilter/SetMass 的
               顺序与实参（body/形状槽位归一）。录制的后续关卡 init 会追加，故用 limit。
               `--stop-at-step` 把两侧都截断在首次 `b2_World_Step` 之前：录制里 init 之后
               的动态建体（接触/触发）不参与比较，宿主自检只跑 init 时可直接对拍。
  * joints  —— `World_Joint_Revolute|Prismatic|Gear` 的 def（body1/body2、anchor/axis、
               limits/motor/collide 或 joint1/joint2/ratio），按日志顺序。

覆盖边界:
  * 只解码 `SetXForm` / `World_CreateBody` / `CreateShape_Circle|Box` 的已知布局
    （src/b2physics/b2physics.h）；其它 export 只出现在 sites 计数里。
  * 动态改位（Set_ScrObjPos）也走 SetXForm，会归入同一 body 组；只有首条参与创建位置比较。
  * 只覆盖日志里出现的调用；被代理过滤的热 getter 不在内（B2PROXY_HOT=1 可全记）。

失效条件:
  * 日志 magic 升级（B2FFI02 → 03）或 def 布局改动；
  * `mapping/lua-binding-args.csv` 的参数表变动（建体绑定的实参位置写在 BODY_CALLS）。

依据：docs/facts.md F34/F45/F46/F276。
"""
import argparse
import collections
import json
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools'))
import ffi  # noqa: E402

# 建体绑定的坐标实参位置（x, y, angle）；None = 该绑定不接受角度。
# 与 mapping/lua-binding-args.csv 的 args DSL 对齐（F239）。
BODY_CALLS = {
    'Add_WoodWall': (1, 2, 3),
    'Add_SimplePhysicObject': (0, 1, 2),
    'Add_SimplePhysCircle': (3, 4, None),
    'Add_WoodGear': (1, 2, 3),
    'Add_SwitchArm': (1, 2, 3),
}

XFORM_SITES = (0x59D5BB, 0x59D61D)   # The Teleport 录制里两处 SetXForm 调用点


def f32(bits):
    return struct.unpack('<f', struct.pack('<I', bits & 0xFFFFFFFF))[0]


def pre_records(path):
    """yield (id, ret_addr, seq, args[32], m0, m1, m2)。"""
    for rec in ffi.records(str(path)):
        if rec[0] != 'pre':
            continue
        v = rec[1]
        yield v[1], v[2], v[5], v[6:38], v[38], v[39], v[40]


def cmd_sites(a):
    ffi.load_names()
    total = collections.Counter()
    for eid, ret, seq, args, m0, m1, m2 in pre_records(a.log):
        name = ffi.NAMES[eid] if eid < len(ffi.NAMES) else str(eid)
        if a.export and name != a.export:
            continue
        total[(name, ret)] += 1
    for (name, ret), n in sorted(total.items(), key=lambda kv: (-kv[1], kv[0][1])):
        print(f'{n:8d}  0x{ret:08X} (game+0x{ret - 0x400000:06x})  {name}')
    if not total:
        print('(no records)')
        return 1
    print(f'sites={len(total)} calls={sum(total.values())}')
    return 0


def cmd_bodies(a):
    ffi.load_names()
    n = 0
    for eid, ret, seq, args, m0, m1, m2 in pre_records(a.log):
        if ffi.NAMES[eid] != 'b2_World_CreateBody':
            continue
        world, = struct.unpack('<I', m0[0:4])
        ad, ld = f32(struct.unpack('<I', m0[4:8])[0]), f32(struct.unpack('<I', m0[8:12])[0])
        allow, fixed, bullet = m0[12], m0[13], m0[14]
        n += 1
        print(f'{n:3d} seq={seq:6d} site=0x{ret:08X} '
              f'world=0x{world:08X} angDamp={ad:g} linDamp={ld:g} '
              f'allowSleep={allow} fixedRot={fixed} bullet={bullet}')
    print(f'bodies={n}')
    return 0


def load_expected(lua_path):
    """Lua 建体绑定的 (name, x, y, angle|None) 列表，按调用顺序。"""
    out = []
    with open(lua_path, encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            d = json.loads(line)
            call = d.get('call', '')
            if call not in BODY_CALLS:
                continue
            ix, iy, ia = BODY_CALLS[call]
            args = d.get('args') or []
            if ix >= len(args) or iy >= len(args):
                continue
            x, y = float(args[ix]), float(args[iy])
            ang = float(args[ia]) if ia is not None and ia < len(args) else None
            out.append((call, x, y, ang))
    return out


def cmd_xforms(a):
    ffi.load_names()
    groups = collections.OrderedDict()
    for eid, ret, seq, args, m0, m1, m2 in pre_records(a.log):
        if ffi.NAMES[eid] != 'b2_Body_SetXForm':
            continue
        if a.site and ret not in a.site:
            continue
        body = args[0]
        x, y, ang = struct.unpack('<3f', m1[:12])
        groups.setdefault(body, []).append((seq, ret, x, y, ang))

    if not a.lua:
        for i, (body, recs) in enumerate(groups.items()):
            seq, ret, x, y, ang = recs[0]
            print(f'{i:3d} body=0x{body:08X} seq={seq:6d} site=0x{ret:08X} '
                  f'({x:.6g}, {y:.6g}, {ang:.6g})  records={len(recs)}')
        print(f'bodies={len(groups)} setxform={sum(len(v) for v in groups.values())}')
        return 0

    exp = load_expected(a.lua)
    pairs = min(len(groups), len(exp))
    bad = 0
    for i in range(pairs):
        body, recs = list(groups.items())[i]
        name, ex, ey, ea = exp[i]
        seq, ret, x, y, ang = recs[0]
        ok = abs(x - ex) <= 1e-6 and abs(y - ey) <= 1e-6
        detail = ''
        if ea is not None:
            if len(recs) < 2:
                ok = False
                detail = ' (no second record for angle)'
            elif abs(recs[1][4] - ea) > 1e-6:
                ok = False
                detail = f' angle {recs[1][4]:.6g} != {ea:.6g}'
        if not ok:
            bad += 1
            print(f'MISMATCH {i:3d} {name}: body=({x:.6g}, {y:.6g}, {ang:.6g}) '
                  f'lua=({ex:.6g}, {ey:.6g}, {ea}){detail}')
        else:
            print(f'ok {i:3d} {name}: ({x:.6g}, {y:.6g}) angle={ang:.6g}')
    if len(groups) != len(exp):
        print(f'COUNT groups={len(groups)} expected={len(exp)} (compared {pairs})')
    print(f'pairs={pairs} mismatches={bad}')
    return 0 if bad == 0 else 1


SHAPE_EXPORTS = ('b2_Body_CreateShape_Circle', 'b2_Body_CreateShape_Box',
                 'b2_Body_CreateShape_Polygon')


def cmd_shapes(a):
    ffi.load_names()
    n = 0
    for eid, ret, seq, args, m0, m1, m2 in pre_records(a.log):
        name = ffi.NAMES[eid]
        if name not in SHAPE_EXPORTS:
            continue
        body = struct.unpack('<I', m0[0:4])[0]
        fric, rest, dens = struct.unpack('<3f', m0[4:16])
        sensor = m0[16]
        av, bv, cv, dv = struct.unpack('<4f', m0[20:36])
        n += 1
        print(f'{n:3d} {name[19:]:8s} seq={seq:6d} site=0x{ret:08X} body=0x{body:08X} '
              f'fric={fric:g} rest={rest:g} dens={dens:g} sensor={sensor} '
              f'a={av:g} b={bv:g} c={cv:g} d={dv:g}')
    print(f'shapes={n}')
    return 0


JOINT_EXPORTS = ('b2_World_Joint_Revolute', 'b2_World_Joint_Prismatic', 'b2_World_Joint_Gear')
SETTER_EXPORTS = ('b2_Shape_SetDensity', 'b2_Shape_SetFriction', 'b2_Shape_SetRestitution',
                  'b2_Shape_SetFilter', 'b2_World_ReFilter', 'b2_Body_SetMassFromShapes')


def collect_seq(path, stop_at_step=False):
    """建体/设位/形状/关节四类序列；关节与 body 指针都归一成创建顺序号。"""
    ffi.load_names()
    bodies, shapes, raw_joints = [], [], []
    raw_setters, shape_entries = [], []
    groups = collections.OrderedDict()
    body_index, joint_index = {}, {}   # ptr -> [(seq, 创建序号)]，指针会复用
    pending_body = pending_joint = pending_shape = None
    for rec in ffi.records(path):
        if rec[0] == 'pre':
            v = rec[1]
            eid, seq, args, m0, m1 = v[1], v[5], v[6:38], v[38], v[39]
            name = ffi.NAMES[eid]
            if stop_at_step and name == 'b2_World_Step':
                break
            if name == 'b2_World_CreateBody':
                ad = f32(struct.unpack('<I', m0[4:8])[0])
                ld = f32(struct.unpack('<I', m0[8:12])[0])
                bodies.append((m0[12], m0[13], m0[14], ad, ld))
                pending_body = (seq, len(bodies) - 1)
            elif name == 'b2_Body_SetXForm':
                x, y, ang = struct.unpack('<3f', m1[:12])
                groups.setdefault(args[0], []).append((x, y, ang))
            elif name in SHAPE_EXPORTS:
                fric, rest, dens = struct.unpack('<3f', m0[4:16])
                if name.endswith('_Polygon'):
                    cnt = struct.unpack_from('<I', m0, 20)[0]
                    vals = []
                    for i in range(8):
                        if i < cnt:
                            vals += list(struct.unpack_from('<2f', m0, 24 + 8 * i))
                        else:
                            vals += [0.0, 0.0]
                    shapes.append((name, fric, rest, dens, cnt) + tuple(vals))
                else:
                    av, bv, cv, dv = struct.unpack('<4f', m0[20:36])
                    # 圆的 def.d 不参与语义（原版这里是栈残渣）；只对盒比 d。
                    shapes.append((name, fric, rest, dens, m0[16], av, bv, cv,
                                   dv if name.endswith('_Box') else None))
                pending_shape = (seq, struct.unpack('<I', m0[0:4])[0])
            elif name in JOINT_EXPORTS:
                raw_joints.append((name, seq, m0))
                pending_joint = (seq, len(raw_joints) - 1)
            elif name in SETTER_EXPORTS:
                raw_setters.append((name, seq, args, m1))
        elif rec[0] == 'post':
            v = rec[1]
            name = ffi.NAMES[v[1]]
            ptr = v[2]
            if name == 'b2_World_CreateBody' and pending_body is not None:
                body_index.setdefault(ptr, []).append(pending_body)
                pending_body = None
            elif name in JOINT_EXPORTS and pending_joint is not None:
                joint_index.setdefault(ptr, []).append(pending_joint)
                pending_joint = None
            elif name in SHAPE_EXPORTS and pending_shape is not None:
                shape_entries.append((ptr, pending_shape[0], pending_shape[1]))
                pending_shape = None
    xforms = [(recs[0][0], recs[0][1], recs[1][2] if len(recs) > 1 else None)
              for recs in groups.values()]
    def at(mapping, ptr, seq):
        """取 seq 之前最近一次创建的序号（指针被 Destroy 后会复用）。"""
        best, best_seq = -1, -1
        for s, idx in mapping.get(ptr, ()):
            if s < seq and s > best_seq:
                best, best_seq = idx, s
        return best

    shape_map = {}
    shape_slots = {}
    for ptr, seq, body_ptr in shape_entries:
        slot = shape_slots.get(body_ptr, 0)
        shape_slots[body_ptr] = slot + 1
        shape_map[ptr] = (at(body_index, body_ptr, seq), slot)

    joints = []
    for name, seq, m0 in raw_joints:
        if name.endswith('Gear'):
            b1, b2, j1, j2 = struct.unpack_from('<4I', m0, 4)
            ratio, = struct.unpack_from('<f', m0, 20)
            joints.append(('Gear', at(body_index, b1, seq), at(body_index, b2, seq),
                           at(joint_index, j1, seq), at(joint_index, j2, seq), ratio))
        elif name.endswith('Revolute'):
            b1, b2 = struct.unpack_from('<2I', m0, 4)
            ax, ay = struct.unpack_from('<2f', m0, 12)
            lo, up = struct.unpack_from('<2f', m0, 24)
            ms, mt = struct.unpack_from('<2f', m0, 36)
            joints.append(('Revolute', at(body_index, b1, seq), at(body_index, b2, seq),
                           ax, ay, m0[20], lo, up, m0[32], ms, mt, m0[44]))
        else:
            b1, b2 = struct.unpack_from('<2I', m0, 4)
            ax, ay, vx, vy = struct.unpack_from('<4f', m0, 12)
            lo, up = struct.unpack_from('<2f', m0, 32)
            ms, mf = struct.unpack_from('<2f', m0, 44)
            joints.append(('Prismatic', at(body_index, b1, seq), at(body_index, b2, seq),
                           ax, ay, vx, vy, m0[28], lo, up, m0[40], ms, mf, m0[52]))
    setters = []
    for name, seq, args, m1 in raw_setters:
        if name == 'b2_Body_SetMassFromShapes':
            setters.append((name, at(body_index, args[0], seq)))
            continue
        bidx, slot = shape_map.get(args[0], (-1, -1))
        if name == 'b2_Shape_SetFilter':
            cat, mask, grp = struct.unpack('<HHh', m1[:6])
            setters.append((name, bidx, slot, cat, mask, grp))
        elif name == 'b2_World_ReFilter':
            setters.append((name, bidx, slot))
        else:
            setters.append((name, bidx, slot, f32(args[1])))
    return bodies, xforms, shapes, joints, setters


def cmp_list(label, a, b, tol=1e-6):
    def close(x, y):
        if isinstance(x, str) or isinstance(y, str):
            return x == y
        if x is None:
            x = 0.0
        if y is None:
            y = 0.0
        return abs(x - y) <= tol

    bad = 0
    for i in range(min(len(a), len(b))):
        if isinstance(a[i], tuple):
            ok = all(close(x, y) for x, y in zip(a[i], b[i]))
        else:
            ok = a[i] == b[i]
        if not ok:
            bad += 1
            print(f'{label} MISMATCH {i}: A={a[i]} B={b[i]}')
    if len(a) != len(b):
        print(f'{label} COUNT a={len(a)} b={len(b)}')
        bad += 1
    print(f'{label} compared={min(len(a), len(b))} mismatches={bad}')
    return bad


def cmd_compare(a):
    ba, xa, sa, ja, ta = collect_seq(a.log, a.stop_at_step)
    bb, xb, sb, jb, tb = collect_seq(a.compare, a.stop_at_step)
    if a.joint_limit:
        ja, jb = ja[:a.joint_limit], jb[:a.joint_limit]
    if a.setter_limit:
        ta, tb = ta[:a.setter_limit], tb[:a.setter_limit]
    if a.body_limit:
        ba, bb = ba[:a.body_limit], bb[:a.body_limit]
        xa, xb = xa[:a.body_limit], xb[:a.body_limit]
    if a.shape_limit:
        sa, sb = sa[:a.shape_limit], sb[:a.shape_limit]
    bad = cmp_list('bodies', ba, bb)
    bad += cmp_list('xforms', xa, xb)
    bad += cmp_list('shapes', sa, sb)
    bad += cmp_list('joints', ja, jb)
    bad += cmp_list('setters', ta, tb)
    print(f'TOTAL mismatches={bad}')
    return 0 if bad == 0 else 1


def cmd_joints(a):
    ffi.load_names()
    n = 0
    for eid, ret, seq, args, m0, m1, m2 in pre_records(a.log):
        name = ffi.NAMES[eid]
        if name not in JOINT_EXPORTS:
            continue
        n += 1
        if name.endswith('Gear'):
            b1, b2, j1, j2 = struct.unpack_from('<4I', m0, 4)
            ratio, = struct.unpack_from('<f', m0, 20)
            print(f'{n:3d} Gear      seq={seq:6d} site=0x{ret:08X} '
                  f'b1=0x{b1:08X} b2=0x{b2:08X} j1=0x{j1:08X} j2=0x{j2:08X} ratio={ratio:g}')
        elif name.endswith('Revolute'):
            b1, b2 = struct.unpack_from('<2I', m0, 4)
            ax, ay = struct.unpack_from('<2f', m0, 12)
            lim = m0[20]
            lo, up = struct.unpack_from('<2f', m0, 24)
            mot = m0[32]
            ms, mt = struct.unpack_from('<2f', m0, 36)
            print(f'{n:3d} Revolute  seq={seq:6d} site=0x{ret:08X} '
                  f'b1=0x{b1:08X} b2=0x{b2:08X} anchor=({ax:g},{ay:g}) '
                  f'lim={lim} lo={lo:g} up={up:g} mot={mot} ms={ms:g} mt={mt:g} col={m0[44]}')
        else:
            b1, b2 = struct.unpack_from('<2I', m0, 4)
            ax, ay, vx, vy = struct.unpack_from('<4f', m0, 12)
            lim = m0[28]
            lo, up = struct.unpack_from('<2f', m0, 32)
            mot = m0[40]
            ms, mf = struct.unpack_from('<2f', m0, 44)
            print(f'{n:3d} Prismatic seq={seq:6d} site=0x{ret:08X} '
                  f'b1=0x{b1:08X} b2=0x{b2:08X} anchor=({ax:g},{ay:g}) axis=({vx:g},{vy:g}) '
                  f'lim={lim} lo={lo:g} up={up:g} mot={mot} ms={ms:g} mf={mf:g} col={m0[52]}')
    print(f'joints={n}')
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('log')
    ap.add_argument('mode', choices=['sites', 'bodies', 'xforms', 'shapes', 'joints', 'compare'])
    ap.add_argument('compare', nargs='?', help='compare 模式的第二份日志')
    ap.add_argument('--export')
    ap.add_argument('--site', help='逗号分隔的返回地址（0x…），仅 xforms')
    ap.add_argument('--lua', help='lvlNN.jsonl，仅 xforms：按顺序对齐建体绑定')
    ap.add_argument('--joint-limit', type=int, default=0, help='compare：只比前 N 个关节')
    ap.add_argument('--stop-at-step', action='store_true',
                    help='compare：只比首次 b2_World_Step 之前（关卡 init）的调用')
    ap.add_argument('--setter-limit', type=int, default=0, help='compare：只比前 N 个 setter')
    ap.add_argument('--body-limit', type=int, default=0, help='compare：只比前 N 个 body/xform 组')
    ap.add_argument('--shape-limit', type=int, default=0, help='compare：只比前 N 个 shape')
    ap.add_argument('--top', type=int, default=0)
    a = ap.parse_args()
    if a.site:
        a.site = {int(s, 0) for s in a.site.split(',') if s.strip()}
    try:
        return {'sites': cmd_sites, 'bodies': cmd_bodies, 'xforms': cmd_xforms,
                'shapes': cmd_shapes, 'joints': cmd_joints, 'compare': cmd_compare}[a.mode](a)
    except OSError as exc:      # Windows 上 `| head` 关管道会报 OSError(22)
        if getattr(exc, 'errno', None) == 22:
            return 0
        raise


if __name__ == '__main__':
    raise SystemExit(main())
