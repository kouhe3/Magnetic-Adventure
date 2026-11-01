"""从原版 b2 录制里生成宿主物理工厂的「形状常量表」（T6.3d）。

用法:
  python tools/gen_phys_shapes.py                 # 生成 src/host_lcl/phys_shapes_gen.inc
  python tools/gen_phys_shapes.py --out work/x.inc --check

做法:
  1. 逐关读 `mapping/levels.csv` 指向的 B2FFI02 录制，取首次 `b2_World_Step` 之前的 body；
  2. 用 `(x, y)` 把每个 `Add_*` 调用的实参对齐到它创建的 body（顺序 DP，见 F276）；
  3. 同一个绑定的所有实例按 style 实参分组，**逐位**校验同组形状完全一致；
  4. 输出 Pascal 常量（`TGenShape` / `TGenStyle`），供 `src/host_lcl/physworld.pas` 建体用。

判据:
  每组实例形状逐位一致（打印 `OK`）；不一致会拒绝生成并报出分歧的关卡。
  生成后由 `python tools/phys_sweep.py` 判 PASS/MISMATCH（TOTAL mismatches=0）。

覆盖边界:
  * 只覆盖 `CONFIG` 里列出的绑定；形状取自**录制里出现的 style**，新 style 需重跑并补表。
  * 顶点数上限 8（`b2_maxPolygonVertices`，F28）；每个 style 最多 12 个形状。
  * 对话关（Introduction/Meet the Shaman/The End 共用录制）不参与。

失效条件:
  * B2FFI02 def 布局或 `tools/b2_sites.py` 的解码变化；
  * `mapping/levels.csv` 的录制↔关卡映射变化；
  * 原版把形状改为按参数计算（当前表是逐 style 常量）。

依据: docs/facts.md F276、F277、F284、F285。
"""
import argparse
import collections
import json
import os
import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools'))
import ffi  # noqa: E402
import b2_sites as bs  # noqa: E402

NAMES = []

# binding -> (style 实参下标, 是否参与)。实参布局统一是 (name, x, y, angle, style…)。
CONFIG = {
    'Add_Magnet': 4,
    'Add_ScrewDriver': 4,
    'Add_ShankBody': 4,
    'Add_Lamp': 4,
    'Add_Cork': 4,
    'Add_TestTube': 4,
    'Add_ToothGear': 4,
    'Add_WoodDetail': 4,
    'Add_HammerParts': 4,
    'Add_BarDoor': 4,
    'Add_Lock': 4,
    'Add_Key': 4,
    'Add_PushButton': 4,
    'Add_Laser': 4,
    'Add_Rack': 4,
}
MAX_VERTS = 8
MAX_SHAPES = 12
SHARED_LEVELS = ('Introduction', 'Meet the Shaman', 'The End')

# 不建 b2 body 的 Add_*（视觉/HUD/计时/纯逻辑）。这些名字只跳过对齐，不参与生成。
NO_BODY = ('Add_Joint', 'Add_LevelMaterial', 'Add_AlphaHint', 'Add_AlphaHud',
           'Add_AlphaDouble', 'Add_ExtAlphaDouble', 'Add_Animate', 'Add_GraphSprite',
           'Add_HudButton', 'Add_HudGraph', 'Add_SimpleTimer', 'Add_LevelSound',
           'Add_FlyAwayLockIcon', 'Add_NextButton', 'Add_CloseButton',
           'Add_SimpleButton', 'Add_HudSimpleButton', 'Add_LevelMaterial')


def is_body_call(name, args):
    if name.startswith(NO_BODY):
        return False
    if not name.startswith('Add_'):
        return False
    return sum(1 for v in args if isinstance(v, (int, float)) and not isinstance(v, bool)) >= 2


def parse_levels(path):
    text = open(path, 'rb').read().decode('utf-16')
    out = []
    for blk in re.findall(r'<Level>(.*?)</Level>', text, re.S):
        cap = re.search(r'Caption\s*=\s*"([^"]*)"', blk)
        if re.search(r'LevelFiles', blk):
            out.append(cap.group(1) if cap else '?')
    return out


def load_recs(csv):
    m = {}
    for i, line in enumerate(open(csv, encoding='utf-8')):
        if i == 0 or not line.strip():
            continue
        p = line.rstrip('\n').split(',')
        if len(p) >= 2:
            m.setdefault(p[1].strip(), []).append(p[0].strip())
    return m


def pick_rec(recs):
    ok = []
    for r in recs:
        log = ROOT / 'work' / r / 'ffi.bin'
        if not log.exists():
            continue
        with open(log, 'rb') as fh:
            magic = fh.read(8).decode('latin1').rstrip('\x00')
        if magic.startswith('B2FFI') and int(magic[5:]) >= 2:
            ok.append(r)
    return ok[-1] if ok else None


def real(rec):
    """(pre-step) 每个 body 的原始 shape def：[(fric, rest, dens, ('poly'|'box'|'circle', …)), …]。"""
    body_of, bodies = {}, []
    for r in ffi.records(str(ROOT / 'work' / rec / 'ffi.bin')):
        if r[0] == 'pre':
            v = r[1]
            nm = NAMES[v[1]]
            m0, m1 = v[38], v[39]
            if nm == 'b2_World_Step':
                break
            if nm == 'b2_World_CreateBody':
                bodies.append({'shapes': [], 'xf': []})
            elif nm.startswith('b2_Body_CreateShape'):
                bi = body_of.get(struct.unpack('<I', m0[0:4])[0])
                fric, rest, dens = struct.unpack('<3f', m0[4:16])
                if nm.endswith('_Box'):
                    d = ('box', tuple(struct.unpack('<4f', m0[20:36])))
                elif nm.endswith('_Circle'):
                    # 第 4 个 float 是栈残渣（b2_sites 同样丢弃），不参与比较（F277）。
                    d = ('circle', tuple(struct.unpack('<4f', m0[20:36])[:3]))
                else:
                    cnt = struct.unpack_from('<I', m0, 20)[0]
                    d = ('poly', cnt, tuple(struct.unpack_from('<2f', m0, 24 + 8 * i)[j]
                                            for i in range(cnt) for j in (0, 1)))
                if bi is not None:
                    bodies[bi]['shapes'].append((fric, rest, dens, d))
            elif nm == 'b2_Body_SetXForm':
                x, y, a = struct.unpack('<3f', m1[:12])
                bodies[-1]['xf'].append((x, y, a))
        elif r[0] == 'post':
            v = r[1]
            if NAMES[v[1]] == 'b2_World_CreateBody':
                body_of[v[2]] = len(bodies) - 1
    return bodies


def lua_calls(idx):
    out = []
    path = ROOT / 'work' / 'lua_probe' / f'lvl{idx:02d}.jsonl'
    for line in open(path, encoding='utf-8', errors='replace'):
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            continue
        nm = r.get('call') or r.get('name')
        if nm:
            out.append((nm, r.get('args') or []))
    return out


def align(bodies, cand, tol=3e-3):
    """顺序 DP：body 与「建体调用」一一对齐（两侧都可跳过），返回 {body_idx: cand_idx}。"""
    n, m = len(bodies), len(cand)
    NEG = (-1, -1e18)
    dp = [[NEG] * (m + 1) for _ in range(n + 1)]
    bt = [[None] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        dp[i][0] = (0, 0.0)
    for j in range(m):
        for i in range(n + 1):
            cur = dp[i][j]
            if cur == NEG:
                continue
            if cur > dp[i][j + 1]:
                dp[i][j + 1] = cur
                bt[i][j + 1] = ('skipc', i, j, None)
            if i < n and cur > dp[i + 1][j]:
                dp[i + 1][j] = cur
                bt[i + 1][j] = ('skipb', i, j, None)
            if i >= n or not bodies[i]['xf']:
                continue
            x, y = bodies[i]['xf'][0][0], bodies[i]['xf'][0][1]
            _, args = cand[j]
            best = None
            for a in range(len(args)):
                va = args[a]
                if not isinstance(va, (int, float)) or isinstance(va, bool):
                    continue
                for b in range(a + 1, len(args)):
                    vb = args[b]
                    if not isinstance(vb, (int, float)) or isinstance(vb, bool):
                        continue
                    e = abs(va - x) + abs(vb - y)
                    if e <= tol and (best is None or e < best[0]):
                        best = (e, a, b)
            if best is None:
                continue
            e = best[0]
            val = (cur[0] + 1, cur[1] - (1.0 + e + 1e-6 * j))
            if val > dp[i + 1][j + 1]:
                dp[i + 1][j + 1] = val
                bt[i + 1][j + 1] = ('match', i, j, best)
    i, j = n, m
    out = {}
    while i > 0 or j > 0:
        t = bt[i][j]
        if t is None:
            break
        if t[0] == 'match':
            out[t[1]] = t[2]
        i, j = t[1], t[2]
    return out


def collect(binding, style_idx):
    """binding -> {style: [(level, shapes)]}，用顺序 DP 把建体调用对齐到 body（F276）。"""
    out = collections.defaultdict(list)
    levels = parse_levels(ROOT / 'work' / 'pak_gametop' / 'lvl_info.lvl')
    recs = load_recs(ROOT / 'mapping' / 'levels.csv')
    for idx, name in enumerate(levels):
        if name in SHARED_LEVELS:
            continue
        rec = pick_rec(recs.get(name, []))
        if not rec:
            continue
        bodies = real(rec)
        calls = lua_calls(idx)
        cand = [(j, c) for j, c in enumerate(calls) if is_body_call(*c)]
        objs = bodies[4:]
        for bi, cj in align(objs, [c for _, c in cand]).items():
            nm, args = calls[cand[cj][0]]
            if nm != binding or len(args) <= style_idx:
                continue
            style = args[style_idx]
            if not isinstance(style, (int, float)):
                continue
            out[int(style)].append((idx, objs[bi]['shapes']))
    return out


def f32(v):
    return repr(struct.unpack('<f', struct.pack('<f', float(v)))[0])


def emit_style(name, table, out, pool):
    """table: {style: shapes}。形状压进共享 pool，style 只存 (n, off)。"""
    styles = sorted(table)
    lo, hi = styles[0], styles[-1]
    out.append(f'  // {name}: style {lo}..{hi}（n = -1 表示录制里没出现过）')
    infos = []
    for st in range(lo, hi + 1):
        if st not in table:
            infos.append('  (n: -1; off: 0)')
            continue
        shapes = table[st]
        infos.append('  (n: %d; off: %d)' % (len(shapes), len(pool)))
        for (fric, rest, dens, kind) in shapes:
            if kind[0] == 'box':
                vals = list(kind[1])
                pool.append('  (kind: 1; n: 0; f: %s; r: %s; d: %s; v: (%s))'
                            % (f32(fric), f32(rest), f32(dens),
                               ', '.join(f32(v) for v in pad(vals))))
            elif kind[0] == 'circle':
                vals = list(kind[1])
                pool.append('  (kind: 2; n: 0; f: %s; r: %s; d: %s; v: (%s))'
                            % (f32(fric), f32(rest), f32(dens),
                               ', '.join(f32(v) for v in pad(vals))))
            else:
                vals = list(kind[2])
                pool.append('  (kind: 0; n: %d; f: %s; r: %s; d: %s; v: (%s))'
                            % (kind[1], f32(fric), f32(rest), f32(dens),
                               ', '.join(f32(v) for v in pad(vals))))
    out.append(f'  {name}: array[{lo}..{hi}] of TGenStyleInfo = (')
    out.append(',\n'.join(infos))
    out.append('  );')


def pad(vals):
    vals = list(vals)
    if len(vals) > 16:
        raise SystemExit('形状参数超过 16 个：%r' % (vals,))
    return vals + [0.0] * (16 - len(vals))


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--out', default=str(ROOT / 'src' / 'host_lcl' / 'phys_shapes_gen.inc'))
    ap.add_argument('--check', action='store_true', help='只校验一致性，不写文件')
    a = ap.parse_args()

    global NAMES
    NAMES = ffi.load_names()

    out = []
    head = []
    head.append('type')
    head.append('  TGenShape = record')
    head.append('    kind: Byte;                  // 0 = poly, 1 = box, 2 = circle')
    head.append('    n: Integer;                  // poly 顶点数')
    head.append('    f, r, d: Single;             // 摩擦 / 弹性 / 密度')
    head.append('    v: array[0..15] of Single;   // box: cx,cy,hx,hy；circle: lx,ly,r；poly: x0,y0,…')
    head.append('  end;')
    head.append('  TGenStyleInfo = record')
    head.append('    n: Integer;                  // 形状数；-1 = 该 style 录制里没出现')
    head.append('    off: Integer;                // 在 kGenShapes 里的起始下标')
    head.append('  end;')
    head.append('')
    pool = []
    body = []

    bad = 0
    for binding, style_idx in CONFIG.items():
        table = collect(binding, style_idx)
        if not table:
            print(f'{binding:24s} SKIP  (no instances)')
            continue
        checked = {}
        for st, items in sorted(table.items()):
            sigs = collections.Counter(repr(it[1]) for it in items)
            if len(sigs) != 1:
                bad += 1
                print(f'{binding} style {st}: {len(sigs)} 个不同形状！关卡 '
                      f'{[it[0] for it in items]}')
                continue
            checked[st] = items[0][1]
            print(f'{binding:24s} style {st:2d}  x{len(items):2d}  shapes={len(items[0][1])}  OK')
        if checked:
            emit_style(f'k{binding[4:]}', checked, body, pool)

    if bad:
        print(f'\n{bad} 组形状不一致，拒绝生成')
        return 1

    out = head
    out.append('const')
    out.append('  // 由 tools/gen_phys_shapes.py 从 B2FFI02 录制生成，勿手改（F285）。')
    out.append(f'  kGenShapes: array[0..{len(pool)-1}] of TGenShape = (')
    out.append(',\n'.join(pool))
    out.append('  );')
    out.extend(body)
    text = ('\r\n'.join(out) + '\r\n').replace('\r\n', '\n').replace('\n', '\r\n')
    if a.check:
        print(f'\ncheck only, {len(out)} lines')
        return 0
    path = Path(a.out)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'wb') as fh:
        fh.write(text.encode('utf-8'))
    print(f'\nwrote {path} ({len(text)} bytes)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
