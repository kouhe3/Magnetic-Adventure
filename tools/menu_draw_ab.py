"""菜单帧 A/B：两份 GLFFI02 日志逐 draw 比几何/UV/alpha（纹理按**素材名**对齐，不靠 id）。

为什么按素材名：GL 纹理 id 是"首次上传顺序"，两个实现的创建/绘制顺序不同 ⇒ id 不可比；
宿主侧的 id 用 `glTexpack.load_uploads` 的像素 CRC 反查（F183 的机制），原版侧用
`mapping/textures.csv`（同一份 CRC 产物）。

用法:
  python tools/menu_draw_ab.py --ref work/glprobe/glidle.bin --ref-frame 10 \
      --cand work/host_menu19.bin --cand-frame 2 [--pak work/pak_gametop] [--tol 0.5]

判据（PASS 条件）:
  ① 两边解析出的素材序列一致（缺/多会把缺的列出来）；
  ② 每个 draw 的设计空间 bbox、UV 矩形、alpha 在 --tol 内。

输出：逐 draw 一行（资产/bbox/Δ），末行 `mismatches=N first=...`；退出码 0=PASS。
覆盖边界:
  - 只比"画了什么、在哪、什么透明度"；不比混合方式/caps（那是 gl_seq_ab.py 的事）。
  - 设计空间换算默认 1018×739（F188），别的分辨率要显式给 --design。
  - 候选侧纹理必须是原尺寸上传（不做 POT 缩放），否则 CRC 反查会 miss（会报出来）。
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile
import zlib

import gl_texpack


def load_id_asset(log, pak):
    """GL 纹理 id → 素材名（按像素 CRC）。返回 (map, missed_ids)。"""
    ups = gl_texpack.load_uploads(log)
    lab = gl_texpack.index_assets(pak)
    out, missed = {}, []
    for tid, w, h, fmt, crc, n in ups:
        hit = None
        for name, im in lab.get((w, h), []):
            for _tag, b in gl_texpack.variants(im, fmt):
                if len(b) == n and (zlib.crc32(b) & 0xFFFFFFFF) == crc:
                    hit = name
                    break
            if hit:
                break
        if hit:
            out[tid] = hit
        else:
            missed.append((tid, w, h))
    return out, missed


def draws_of(log, frame):
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    try:
        r = subprocess.run([sys.executable, os.path.join("tools", "gl_drawlist.py"), log,
                            "--frame", str(frame), "--json", path],
                           capture_output=True, text=True, errors="replace")
        if r.returncode != 0:
            raise SystemExit("gl_drawlist 失败: " + (r.stdout or r.stderr)[-500:])
        return json.load(open(path, encoding="utf-8"))["draws"]
    finally:
        os.unlink(path)


def to_design(d, w, h):
    xs = [p[0] for p in d["v"]]
    ys = [p[1] for p in d["v"]]
    x0 = (min(xs) + 1) * 0.5 * w
    x1 = (max(xs) + 1) * 0.5 * w
    y0 = (1 - max(ys)) * 0.5 * h
    y1 = (1 - min(ys)) * 0.5 * h
    us = [u for u, _ in d["uv"]]
    vs = [v for _, v in d["uv"]]
    return (x0, y0, x1, y1), (min(us), min(vs), max(us), max(vs))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", required=True)
    ap.add_argument("--ref-frame", type=int, required=True)
    ap.add_argument("--cand", required=True)
    ap.add_argument("--cand-frame", type=int, required=True)
    ap.add_argument("--pak", default="work/pak_gametop")
    ap.add_argument("--ref-csv", default="mapping/textures.csv")
    ap.add_argument("--design", default="1018x739")
    ap.add_argument("--tol", type=float, default=0.5)
    a = ap.parse_args()
    w, h = (float(x) for x in a.design.split("x"))

    ref_map = {}
    for line in open(a.ref_csv, encoding="utf-8").read().splitlines()[1:]:
        if not line.strip():
            continue
        tid, asset = line.split(",")[:2]
        ref_map[int(tid)] = asset
    cand_map, missed = load_id_asset(a.cand, a.pak)
    if missed:
        print("候选纹理 CRC 未匹配 %d 条（id,w,h）: %s" % (len(missed), missed[:6]))

    ref = [(ref_map.get(d["tex"], "tex=%s" % d["tex"]), d) for d in draws_of(a.ref, a.ref_frame)]
    cand = [(cand_map.get(d["tex"], "tex=%s" % d["tex"]), d) for d in draws_of(a.cand, a.cand_frame)]
    print("ref draws=%d cand draws=%d" % (len(ref), len(cand)))

    # 按素材名对齐：同名的按出现顺序配对；候选缺的报 missing。
    from collections import defaultdict
    buckets = defaultdict(list)
    for i, (name, d) in enumerate(cand):
        buckets[name].append(i)
    used = set()
    pairs = []
    for name, d in ref:
        if buckets.get(name):
            j = buckets[name].pop(0)
            used.add(j)
            pairs.append((name, d, cand[j][1]))
    missing = [n for n, _ in cand if n not in {p[0] for p in pairs}]
    unmatched_ref = [n for n, d in ref if not any(p[1] is d for p in pairs)]

    bad = 0
    first = None
    for name, rd, cd in pairs:
        rb, ru = to_design(rd, w, h)
        cb, cu = to_design(cd, w, h)
        db = max(abs(rb[k] - cb[k]) for k in range(4))
        du = max(abs(ru[k] - cu[k]) for k in range(4))
        da = abs(rd["rgba"][3] - cd["rgba"][3])
        ok = db <= a.tol and du <= 1e-3 and da <= 1e-3
        if not ok:
            bad += 1
            if first is None:
                first = "%s bbox d=%.2f uv d=%.4f alpha d=%.3f" % (name, db, du, da)
        print("%-16s ref=(%7.1f,%7.1f)-(%7.1f,%7.1f) cand=(%7.1f,%7.1f)-(%7.1f,%7.1f) "
              "dbbox=%5.2f duv=%.4f da=%.3f %s"
              % (name, rb[0], rb[1], rb[2], rb[3], cb[0], cb[1], cb[2], cb[3], db, du, da,
                 "PASS" if ok else "FAIL"))
    print("pairs=%d mismatches=%d first=%s" % (len(pairs), bad, first))
    if unmatched_ref:
        print("ref 独有（例如文本层未实现）: %s" % unmatched_ref)
    if missing:
        print("cand 独有: %s" % missing)
    return 0 if bad == 0 and not missing else 1


if __name__ == "__main__":
    sys.exit(main())
