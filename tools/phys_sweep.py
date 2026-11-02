"""逐关跑宿主物理 init，并与原版录制逐项对拍，产出 T6.3d 的覆盖图。

用法:
  python tools/phys_sweep.py                          # 全 52 关（宿主 run + 对拍）
  python tools/phys_sweep.py --levels 2,3,5-9         # 子集（0 起，lvl_info.lvl 顺序）
  python tools/phys_sweep.py --no-run                  # 只重解析 work/phys_sweep/ 里已有的宿主日志
  python tools/phys_sweep.py --out work/phys_sweep.json --keep-mismatch 3

判据（每关，二值）:
  PASS     = 首次 `b2_World_Step` 之前，五组序列逐项相同：
             bodies / xforms / shapes / joints / setters（`b2_sites compare --stop-at-step`，
             TOTAL mismatches=0，|Δ| <= 1e-6）。
  MISMATCH = 任一组有差异（打印首个差异与计数差）。
  SKIP     = 录制缺失或 magic < B2FFI02（F87），或宿主 run 退出码非 0/日志缺失。

覆盖边界:
  * 只覆盖**关卡 init**：首次 World_Step 之前的调用。运行期动态建体（接触/触发，
    如 lvl49 的两个 joint，F272）不在内。
  * 录制是单次游玩会话，可能含 init 之后的动态对象；截断在首次 Step 后这些不参与。
  * 对话关 Introduction / Meet the Shaman / The End 共用一份录制，只有第一关可判。
  * 宿主 A/A 已在 F282 量到 0（同一 build 两次运行）。
  * 宿主侧只跑 Lua init（HOST_LUA_SELFTEST=5 + HOST_HEADLESS=1），不建窗、不建 GL、
    不步进、不渲染；无头/有头的 b2 调用序列已对拍一致（F290）。

失效条件:
  * `tools/b2_sites.py` 的 def 布局解码或 B2FFI02 magic 变动；
  * `src/host_lcl/magnet.pas` 的自检 5 入口（HOST_LUA_SELFTEST=5 + HOST_LUA_LEVEL）语义变化；
  * `mapping/levels.csv` 的录制↔关卡映射变动。

依据: docs/facts.md F276–F282（录制驱动逐对象对拍）、F264（关卡顺序）。
"""
import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

sys.path.insert(0, str(ROOT / 'tools'))
import instr  # noqa: E402


def parse_levels(path):
    text = open(path, 'rb').read().decode('utf-16')
    levels = []
    for block in re.findall(r'<Level>(.*?)</Level>', text, re.S):
        cap = re.search(r'Caption\s*=\s*"([^"]*)"', block)
        files = re.search(r'LevelFiles\s*=\s*"([^"]*)"', block)
        if not files:
            continue
        levels.append(cap.group(1) if cap else '?')
    return levels


def log_magic(path):
    try:
        with open(path, 'rb') as fh:
            return fh.read(8).decode('latin1').rstrip('\x00')
    except OSError:
        return ''


def rec_timestamp(name):
    m = re.search(r'rec_(\d{8})_(\d{6})', name)
    if m:
        return int(m.group(1) + m.group(2))
    return 0


def load_rec_map(path):
    """name -> [rec...]，保留 CSV 顺序。"""
    m = {}
    for i, line in enumerate(open(path, encoding='utf-8')):
        if i == 0 or not line.strip():
            continue
        parts = line.rstrip('\n').split(',')
        if len(parts) < 2:
            continue
        rec, name = parts[0].strip(), parts[1].strip()
        m.setdefault(name, []).append(rec)
    return m


def pick_rec(recs):
    """可用的最新录制（B2FFI02 以上）。"""
    usable = []
    for r in recs:
        log = ROOT / 'work' / r / 'ffi.bin'
        if log.exists() and instr.log_usable(log_magic(log)):
            usable.append(r)
    if not usable:
        return None
    usable.sort(key=rec_timestamp)
    return usable[-1]


def rec_shared_map(rec_map):
    """录制目录 -> 用到它的关卡名集合（对话关共用一份日志）。"""
    out = {}
    for name, recs in rec_map.items():
        for r in recs:
            out.setdefault(r, set()).add(name)
    return out


def load_random_map(path):
    """level -> (sequence file, tolerance, provenance)。"""
    out = {}
    if not Path(path).exists():
        return out
    for i, line in enumerate(open(path, encoding='utf-8')):
        if i == 0 or not line.strip():
            continue
        parts = [p.strip() for p in line.rstrip('\n').split(',')]
        if len(parts) < 3:
            continue
        out[int(parts[0])] = (parts[1], float(parts[2]),
                              parts[3] if len(parts) > 3 else '')
    return out


def load_skip_map(path):
    """level -> reason：录制本身不可判（截断/中途开始），不是宿主差异。"""
    out = {}
    if not Path(path).exists():
        return out
    for i, line in enumerate(open(path, encoding='utf-8')):
        if i == 0 or not line.strip():
            continue
        parts = [p.strip() for p in line.rstrip('\n').split(',', 1)]
        if len(parts) == 2:
            out[int(parts[0])] = parts[1]
    return out


def run_host(level, host_dir, data, lua_dir, out_log, timeout, rand_file=None):
    env = dict(os.environ)
    env.update({
        'HOST_DATA': str(data),
        'HOST_LUA_DIR': str(lua_dir),
        'HOST_PHYS': '1',
        'HOST_LUA_SELFTEST': '5',
        'HOST_LUA_LEVEL': str(level),
        'HOST_HEADLESS': '1',
        'B2PROXY_LOG': str(out_log),
    })
    if rand_file:
        env['HOST_LUA_RANDOM'] = str(ROOT / rand_file)
    else:
        env.pop('HOST_LUA_RANDOM', None)
    env.pop('HOST_PHYS_MOVE', None)
    env.pop('HOST_PHYS_STEPS', None)
    if out_log.exists():
        out_log.unlink()
    try:
        p = subprocess.run([str(host_dir / 'magnet.exe')], cwd=str(host_dir), env=env,
                           capture_output=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return None, 'timeout'
    return p.returncode, (p.stderr.decode('latin1', 'replace')[-400:])


def compare(rec_log, host_log, stop_at_step=True, tol=1e-6):
    cmd = [sys.executable, str(ROOT / 'tools' / 'b2_sites.py'), str(rec_log),
           'compare', str(host_log)]
    if stop_at_step:
        cmd.append('--stop-at-step')
    if tol != 1e-6:
        cmd += ['--tol', str(tol)]
    p = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True)
    out = p.stdout
    bad = []
    counts = {}
    for line in out.splitlines():
        if 'MISMATCH' in line or line.startswith(('bodies COUNT', 'xforms COUNT',
                                                  'shapes COUNT', 'joints COUNT',
                                                  'setters COUNT')):
            bad.append(line.strip())
        m = re.match(r'(\w+) compared=(\d+) mismatches=(\d+)', line)
        if m:
            counts[m.group(1)] = (int(m.group(2)), int(m.group(3)))
    total = None
    m = re.search(r'TOTAL mismatches=(\d+)', out)
    if m:
        total = int(m.group(1))
    return total, counts, bad


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--levels', default='0-51', help='关卡下标，0 起（默认全量）')
    ap.add_argument('--host-dir', default=str(ROOT / 'build' / 'host_lcl'))
    ap.add_argument('--data', default=str(ROOT / 'bin' / 'gametop' / 'data'))
    ap.add_argument('--lua-dir', default=str(ROOT / 'work' / 'pak_gametop'))
    ap.add_argument('--levels-file', default=str(ROOT / 'work' / 'pak_gametop' / 'lvl_info.lvl'))
    ap.add_argument('--rec-csv', default=str(ROOT / 'mapping' / 'levels.csv'))
    ap.add_argument('--random-csv', default=str(ROOT / 'mapping' / 'phys_random.csv'))
    ap.add_argument('--skip-csv', default=str(ROOT / 'mapping' / 'phys_skip.csv'))
    ap.add_argument('--out', default=str(ROOT / 'work' / 'phys_sweep.json'))
    ap.add_argument('--log-dir', default=str(ROOT / 'work' / 'phys_sweep'))
    ap.add_argument('--no-run', action='store_true', help='不跑宿主，只重解析已有日志')
    ap.add_argument('--timeout', type=float, default=120.0)
    ap.add_argument('--keep-mismatch', type=int, default=3)
    a = ap.parse_args()

    levels = parse_levels(a.levels_file)
    rec_map = load_rec_map(a.rec_csv)
    rand_map = load_random_map(a.random_csv)
    skip_map = load_skip_map(a.skip_csv)
    log_dir = Path(a.log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)

    want = set()
    for part in a.levels.split(','):
        if '-' in part:
            lo, hi = part.split('-')
            want.update(range(int(lo), int(hi) + 1))
        elif part.strip():
            want.add(int(part))

    rec_owners = rec_shared_map(rec_map)
    name_index = {}
    for i, n in enumerate(levels):
        name_index.setdefault(n, i)

    rows = []
    for idx, name in enumerate(levels):
        if idx not in want:
            continue
        row = {'level': idx, 'name': name}
        recs = rec_map.get(name, [])
        rec = pick_rec(recs)
        if idx in skip_map:
            row.update(status='SKIP', rec=rec, reason=skip_map[idx])
            rows.append(row)
            print(f'[{idx:2d}] {name:32s} SKIP  ({skip_map[idx]})')
            continue
        if not rec:
            row.update(status='SKIP', reason='no usable recording' if recs else 'no recording')
            rows.append(row)
            print(f'[{idx:2d}] {name:32s} SKIP  ({row["reason"]})')
            continue
        shared = len(rec_owners.get(rec, ())) > 1
        if shared:
            first = min(name_index.get(n, 1 << 30) for n in rec_owners[rec])
            if idx != first:
                row.update(status='SKIP', rec=rec,
                           reason=f'shared recording, owned by level {first}')
                rows.append(row)
                print(f'[{idx:2d}] {name:32s} SKIP  (shared with level {first})')
                continue
        rec_log = ROOT / 'work' / rec / 'ffi.bin'
        host_log = log_dir / f'host_lvl{idx:02d}.bin'
        row['rec'] = rec
        rand_file, tol, provenance = rand_map.get(idx, (None, 1e-6, ''))
        if rand_file:
            row['random_replay'] = rand_file
            row['random_tol'] = tol
            row['random_provenance'] = provenance
        if shared:
            row['shared_log'] = True
        if not a.no_run:
            code, err = run_host(idx, Path(a.host_dir), a.data, a.lua_dir, host_log,
                                 a.timeout, rand_file)
            row['exit'] = code
            if code != 0 or not host_log.exists():
                row.update(status='SKIP', reason=f'host exit={code} {err.strip()[:120]}')
                rows.append(row)
                print(f'[{idx:2d}] {name:32s} SKIP  host exit={code}')
                continue
        elif not host_log.exists():
            row.update(status='SKIP', reason='host log missing (--no-run)')
            rows.append(row)
            print(f'[{idx:2d}] {name:32s} SKIP  host log missing')
            continue

        total, counts, bad = compare(rec_log, host_log, tol=tol)
        if total is None:
            row.update(status='SKIP', reason='compare failed')
            rows.append(row)
            print(f'[{idx:2d}] {name:32s} SKIP  compare failed')
            continue
        row['mismatches'] = total
        row['counts'] = {k: {'compared': v[0], 'bad': v[1]} for k, v in counts.items()}
        row['first'] = bad[:a.keep_mismatch]
        if shared:
            row['note'] = 'shared recording; only first level judgeable'
        if total == 0:
            row['status'] = 'PASS'
            print(f'[{idx:2d}] {name:32s} PASS  ' +
                  ' '.join(f'{k}={v[0]}' for k, v in counts.items()))
        else:
            row['status'] = 'MISMATCH'
            counts_s = ' '.join(f'{k}={v[0]}/{v[1]}' for k, v in counts.items())
            print(f'[{idx:2d}] {name:32s} MISMATCH {counts_s}' +
                  ('  [shared]' if shared else ''))
            for line in bad[:a.keep_mismatch]:
                print(f'        {line}')
        rows.append(row)

    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, 'w', encoding='utf-8') as fh:
        json.dump(rows, fh, ensure_ascii=False, indent=1)

    n_pass = sum(1 for r in rows if r['status'] == 'PASS')
    n_mis = sum(1 for r in rows if r['status'] == 'MISMATCH')
    n_skip = sum(1 for r in rows if r['status'] == 'SKIP')
    print(f'\nlevels={len(rows)} PASS={n_pass} MISMATCH={n_mis} SKIP={n_skip} '
          f'→ {out}')
    return 0 if n_mis == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
