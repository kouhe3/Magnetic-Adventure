#!/usr/bin/env python3
"""逐关 GL 抓包：私有桌面起原版 → dispatch 进关 → 有界时间窗 GLFFI02 → 找 settled 帧。

为什么一关一进程：GL 代理的 log 按会话写；一关一进程使日志边界天然清楚，也让
WM_CLOSE 的干净退出（F352/F354）只影响这一关。时间窗 `GLPROXY_T0/T1`（毫秒，
从 DLL 加载起算）把 800 MB 级的全量日志压到 ~200 MB：窗口只覆盖 MENU→进关后的
前 1.5 s，进关前的 loading/menu 调用不落盘。

用法:
  python tools/capture_gl_levels.py --levels 0-3 --out-dir work/gl_levels2
  python tools/capture_gl_levels.py --levels 1 --resume
  python tools/capture_gl_levels.py --check work/gl_levels work/gl_levels_b

判据:
  ① 每关摘要 `lvlNN_summary.json` 有 `frames>0`、`settled>=0`、`draws>0`；
  ② `--check A B` 对每关按各自 settled 帧跑 `tools/level_draw_ab.py`
     （默认忽略 `mcur_1.png,tex=1` 光标）⇒ `pairs>0 mismatches=0 missing=0
     unmatched_ref=0`；任一关不满足即退出码 1。
  ③ 负例：`--levels 99` 在启动前退出码 2；`--check` 传一份未进关的 A 目录
     （settled 帧仍是 loading）⇒ `unmatched_ref>0`。

自检:
  python tools/capture_gl_levels.py --self-test
  ⇒ `pick_settled` 的三个纯函数用例：尾段平台起点、平台过短返回 None、
     尾部夹一帧退出帧时仍取平台起点。

覆盖边界:
  * 只覆盖“进关后的绘制帧”，不含像素、音频、输入、逐帧状态；
  * 时间窗以 DLL 加载为 0 点；窗口没罩住进关（机器慢/关卡加载久）会在摘要里
    标 `settled=None`，此时加宽 `--t1` 重采，不要拿它当判据；
  * 纹理 id 是每次运行的首次上传顺序，跨运行不可比：`level_draw_ab` 按像素
    CRC 反查素材名（`work/pak_crc_index.json` 缓存 pak 索引）。
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

import gl_ffi  # noqa: E402

PY32 = os.environ.get("PY32", r"C:\Users\K\.local\bin\python3.12.exe")
DEFAULT_DIR = "work/e2e_gl"


def parse_levels(spec):
    out = []
    for part in spec.split(","):
        if "-" in part:
            a, b = part.split("-", 1)
            out.extend(range(int(a), int(b) + 1))
        else:
            out.append(int(part))
    return out


def pick_settled(counts, need=3):
    """返回尾部稳定平台的起始帧；平台短于 need 或为空返回 None。

    counts 是每帧的 draw 数（glBegin 计数）。原版进关时先画 loading/过渡层
    （draw 数 3→35/59/61→37），之后稳定在关卡层（如 30）。取**最后一个
    长度 ≥ need 的连续平台**：loading 平台虽长但在前，过渡帧平台太短，
    尾部可能夹着短退出帧（draw 数掉回 3）也不会被选中。
    """
    if not counts:
        return None
    runs = []
    start = 0
    for i in range(1, len(counts) + 1):
        if i == len(counts) or counts[i] != counts[start]:
            runs.append((counts[start], start, i - start))
            start = i
    best = None
    for _value, st, ln in runs:
        if ln >= need:
            best = (st, ln)
    return best[0] if best else None


def frame_draw_counts(log):
    """(frames, [每帧 glBegin 数])；帧边界 = wglSwapBuffers。"""
    nm = gl_ffi.names()
    s = gl_ffi.load(log)
    sw = gl_ffi.swap_ids(nm)
    begin = {k for k, v in nm.items() if v == "glBegin"}
    fb = gl_ffi.frame_bounds(s["ids"], sw)
    ids = s["ids"]
    counts = []
    for start, end in fb:
        n = 0
        for i in range(start, end + 1):
            if ids[i] in begin:
                n += 1
        counts.append(n)
    return len(fb), counts


def capture_one(level, out_dir, game_dir, t0, t1, timeout, gap):
    log = (out_dir / ("lvl%02d_gl.bin" % level)).resolve()
    drive = out_dir / ("lvl%02d_drive.jsonl" % level)
    env = os.environ.copy()
    env["GLPROXY_LOG"] = str(log)
    env["GLPROXY_T0"] = str(t0)
    env["GLPROXY_T1"] = str(t1)
    cmd = [PY32, str(TOOLS / "direct_drive.py"), "--dir", game_dir,
           "--levels", str(level), "--out", str(drive),
           "--exit-mode", "wmclose", "--timeout", str(timeout),
           "--gap", str(gap)]
    r = subprocess.run(cmd, env=env, capture_output=True, text=True, errors="replace")
    tail = (r.stdout or "") + (r.stderr or "")
    ok = r.returncode == 0 and log.exists() and log.stat().st_size > 0
    return {"level": level, "log": str(log), "drive": str(drive),
            "rc": r.returncode, "bytes": log.stat().st_size if log.exists() else 0,
            "ok": ok, "tail": tail[-600:] if not ok else ""}


def summarize(row, offset=25):
    if not row["ok"]:
        row.update({"frames": 0, "settled": None, "draws": 0, "error": "capture failed"})
        return row
    try:
        frames, counts = frame_draw_counts(row["log"])
        settled = pick_settled(counts)
    except SystemExit as e:
        row.update({"frames": 0, "settled": None, "draws": 0, "error": str(e)})
        return row
    cmp_frame = min(settled + offset, frames - 1) if settled is not None else None
    row.update({"frames": frames, "settled": settled, "cmp_frame": cmp_frame,
                "draws": counts[settled] if settled is not None else 0,
                "tail": counts[-10:]})
    if not frames or settled is None:
        row["error"] = "no settled plateau (widen --t1?)"
    return row


def check_pair(dir_a, dir_b, levels, out, ignore):
    rows = []
    fa, fb_ = Path(dir_a), Path(dir_b)
    for level in levels:
        sa = json.loads((fa / ("lvl%02d_summary.json" % level)).read_text(encoding="utf-8"))
        sb = json.loads((fb_ / ("lvl%02d_summary.json" % level)).read_text(encoding="utf-8"))
        fa_frame = sa.get("cmp_frame", sa.get("settled"))
        fb_frame = sb.get("cmp_frame", sb.get("settled"))
        if fa_frame is None or fb_frame is None:
            rows.append({"level": level, "ok": False, "error": "no settled frame"})
            continue
        cmd = [sys.executable, str(TOOLS / "level_draw_ab.py"),
               "--ref", sa["log"], "--ref-frame", str(fa_frame),
               "--cand", sb["log"], "--cand-frame", str(fb_frame),
               "--ignore-assets", ignore]
        r = subprocess.run(cmd, capture_output=True, text=True, errors="replace")
        last = [ln for ln in (r.stdout or "").splitlines() if ln.startswith("pairs=")]
        info = {"level": level, "rc": r.returncode,
                "line": last[-1] if last else "", "ok": r.returncode == 0}
        rows.append(info)
        print("lvl%02d %s" % (level, info["line"]), flush=True)
    with open(out, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return 0 if rows and all(r["ok"] for r in rows) else 1


def self_test():
    cases = [
        ([3, 3, 30, 30, 30, 30], 2),
        ([3, 30, 30, 30, 30], 1),
        ([3, 30, 3], None),
        ([30, 30], None),
        ([], None),
        ([3, 35, 61, 37, 30, 30, 30, 3, 3], 4),
    ]
    ok = True
    for counts, want in cases:
        got = pick_settled(counts)
        good = got == want
        ok = ok and good
        print("settle %-40s got=%s want=%s %s"
              % (counts, got, want, "PASS" if good else "FAIL"))
    print("SELFTEST", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--levels", default="", help="dispatcher indices 0..51, e.g. 0-3 or 1,4")
    ap.add_argument("--dir", default=DEFAULT_DIR, help="game dir with opengl32 proxy + orig")
    ap.add_argument("--out-dir", default="work/gl_levels2")
    ap.add_argument("--t0", type=int, default=14000, help="window start ms from DLL load")
    ap.add_argument("--t1", type=int, default=24000, help="window end ms from DLL load")
    ap.add_argument("--timeout", type=float, default=20.0)
    ap.add_argument("--gap", type=float, default=1.5)
    ap.add_argument("--settle-offset", type=int, default=25,
                    help="判据帧 = settled + offset（淡入/入场动画稳定后）")
    ap.add_argument("--retries", type=int, default=1,
                    help="dispatch 超时等瞬时失败的重试次数（每关独立进程）")
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--check", nargs=2, metavar=("DIR_A", "DIR_B"))
    ap.add_argument("--check-out", default="work/gl_levels_check.jsonl")
    ap.add_argument("--ignore-assets", default="mcur_1.png,tex=1")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()

    if a.self_test:
        return self_test()
    if a.check:
        levels = parse_levels(a.levels) if a.levels else []
        if not levels:
            raise SystemExit("--check 需要 --levels（哪些关已采）")
        return check_pair(a.check[0], a.check[1], levels, a.check_out, a.ignore_assets)
    if not a.levels:
        raise SystemExit("--levels is required")
    levels = parse_levels(a.levels)
    bad = [x for x in levels if not (0 <= x < 52)]
    if bad:
        print("bad indices (expect 0..51):", bad)
        return 2
    out_dir = Path(a.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    fails = 0
    for level in levels:
        sfile = out_dir / ("lvl%02d_summary.json" % level)
        if a.resume and sfile.exists():
            prev = json.loads(sfile.read_text(encoding="utf-8"))
            if prev.get("settled") is not None and prev.get("bytes", 0) > 0:
                print("lvl%02d resume skip" % level, flush=True)
                continue
        row = None
        for attempt in range(1 + a.retries):
            print("lvl%02d capture ..." % level, flush=True)
            row = capture_one(level, out_dir, a.dir, a.t0, a.t1, a.timeout, a.gap)
            row = summarize(row, a.settle_offset)
            if row["ok"] and not row.get("error"):
                break
            if attempt < a.retries:
                tail = row.get("tail", "")
                if not isinstance(tail, str):
                    tail = json.dumps(tail, ensure_ascii=False)
                print("lvl%02d retry %d/%d: %s"
                      % (level, attempt + 1, a.retries,
                         tail[-240:].replace("\n", " ")), flush=True)
        sfile.write_text(json.dumps(row, ensure_ascii=False, indent=1) + "\n",
                         encoding="utf-8")
        print("lvl%02d ok=%s bytes=%d frames=%d settled=%s draws=%d %s"
              % (level, row["ok"], row["bytes"], row["frames"], row["settled"],
                 row["draws"], row.get("error", "")), flush=True)
        if not row["ok"] or row.get("error"):
            fails += 1
    return 0 if fails == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
