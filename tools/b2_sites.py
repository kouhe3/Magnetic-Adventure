"""按调用点归因 b2Physics 调用，并解码已知结构（B2FFI02 日志）。

用法:
  python tools/b2_sites.py <log> sites [--export NAME] [--top N]
  python tools/b2_sites.py <log> bodies
  python tools/b2_sites.py <log> xforms [--lua <lvlNN.jsonl>]
  python tools/b2_sites.py <log> shapes

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


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('log')
    ap.add_argument('mode', choices=['sites', 'bodies', 'xforms', 'shapes'])
    ap.add_argument('--export')
    ap.add_argument('--site', help='逗号分隔的返回地址（0x…），仅 xforms')
    ap.add_argument('--lua', help='lvlNN.jsonl，仅 xforms：按顺序对齐建体绑定')
    ap.add_argument('--top', type=int, default=0)
    a = ap.parse_args()
    if a.site:
        a.site = {int(s, 0) for s in a.site.split(',') if s.strip()}
    try:
        return {'sites': cmd_sites, 'bodies': cmd_bodies, 'xforms': cmd_xforms,
                'shapes': cmd_shapes}[a.mode](a)
    except OSError as exc:      # Windows 上 `| head` 关管道会报 OSError(22)
        if getattr(exc, 'errno', None) == 22:
            return 0
        raise


if __name__ == '__main__':
    raise SystemExit(main())
