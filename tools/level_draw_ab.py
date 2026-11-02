"""关卡帧 A/B：两份 GLFFI02 日志逐 draw 比世界坐标 bbox / UV / alpha。

与 `menu_draw_ab.py` 的区别：
  - 菜单是 HUD 设计空间，要把 NDC 换回 1018x739；关卡 draw 已经是 MODELVIEW 后的
    世界坐标（相机平移已含在内），所以直接比 bbox，不做设计空间换算。
  - 原版关卡纹理 id（38–49）不在 `mapping/textures.csv`；默认对两侧都按像素 CRC
    反查 pak（`--ref-map/--cand-map` 可传 `gl_texpack.py` 的 manifest 缓存，避免每次
    重解 800 MB 日志）。

用法:
  python tools/level_draw_ab.py --ref work/level0_gl.bin --ref-frame 9600 \
      --cand work/host_lvl0.bin --cand-frame 2 \
      --ref-map work/level0_tex.json --pak work/pak_gametop

判据:
  pairs 两侧按素材名 + 出现顺序配对；每个 draw 的 bbox（世界单位）、UV、alpha
  在容差内 ⇒ PASS；`missing`/`unmatched_ref` 非空即 FAIL。末行
  `pairs=N mismatches=M first=...`，退出码 0=PASS。

覆盖边界:
  - 只比“画了什么、在哪、什么 UV/透明度”；不比 blend/caps/投影（那是 gl_seq_ab）。
  - 只覆盖录到的那一关/那一帧；未录状态不外推。
  - 默认忽略 `mcur_1.png`（鼠标光标，位置由输入决定，不属于场景内容）。

自证:
  python tools/level_draw_ab.py --self-test
  ⇒ A/A mismatches=0；把一个候选 draw 的 bbox 平移 > tol ⇒ mismatches=1。
"""
import argparse
import copy
import json
import os
import sys

import menu_draw_ab


def world_bbox(d):
    xs = [p[0] for p in d["v"]]
    ys = [p[1] for p in d["v"]]
    us = [u for u, _ in d["uv"]]
    vs = [v for _, v in d["uv"]]
    return (min(xs), min(ys), max(xs), max(ys)), (min(us), min(vs), max(us), max(vs))


def load_map(path, log, pak):
    if path:
        data = json.load(open(path, encoding="utf-8"))
        out = {}
        for t in data.get("textures", []):
            if t.get("asset"):
                out[int(t["id"])] = t["asset"]
        return out, []
    return menu_draw_ab.load_id_asset(log, pak)


def labeled(draws, idmap):
    return [(idmap.get(d["tex"], "tex=%s" % d["tex"]), d) for d in draws]


def pair(ref, cand, ignore):
    from collections import defaultdict

    buckets = defaultdict(list)
    for i, (name, d) in enumerate(cand):
        if name not in ignore:
            buckets[name].append(i)
    pairs = []
    used = set()
    for name, d in ref:
        if name in ignore:
            continue
        if buckets.get(name):
            j = buckets[name].pop(0)
            used.add(j)
            pairs.append((name, d, cand[j][1]))
    missing = [n for i, (n, _) in enumerate(cand) if i not in used and n not in ignore]
    unmatched_ref = [n for n, _ in ref if n not in {p[0] for p in pairs} and n not in ignore]
    return pairs, missing, unmatched_ref


def compare(ref, cand, tol, uv_tol, alpha_tol, ignore, verbose=True):
    pairs, missing, unmatched_ref = pair(ref, cand, ignore)
    bad = 0
    first = None
    for name, rd, cd in pairs:
        rb, ru = world_bbox(rd)
        cb, cu = world_bbox(cd)
        db = max(abs(rb[k] - cb[k]) for k in range(4))
        du = max(abs(ru[k] - cu[k]) for k in range(4))
        da = abs(rd["rgba"][3] - cd["rgba"][3])
        ok = db <= tol and du <= uv_tol and da <= alpha_tol
        if not ok:
            bad += 1
            if first is None:
                first = "%s bbox d=%.3f uv d=%.4f alpha d=%.3f" % (name, db, du, da)
        if verbose:
            print("%-18s ref=(%8.3f,%8.3f)-(%8.3f,%8.3f) "
                  "cand=(%8.3f,%8.3f)-(%8.3f,%8.3f) "
                  "dbbox=%7.3f duv=%.4f da=%.3f %s"
                  % (name, rb[0], rb[1], rb[2], rb[3], cb[0], cb[1], cb[2], cb[3],
                     db, du, da, "PASS" if ok else "FAIL"))
    if verbose:
        print("pairs=%d mismatches=%d missing=%d unmatched_ref=%d first=%s"
              % (len(pairs), bad, len(missing), len(unmatched_ref), first))
        if missing:
            print("cand 独有: %s" % missing)
        if unmatched_ref:
            print("ref 独有: %s" % unmatched_ref)
    return bad, missing, unmatched_ref, first


def self_test():
    d1 = {"prim": "QUADS", "tex": 1, "n": 4, "rgba": [1.0, 1.0, 1.0, 1.0],
          "v": [(-1.0, -1.0, 0.0), (1.0, -1.0, 0.0), (1.0, 1.0, 0.0), (-1.0, 1.0, 0.0)],
          "uv": [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]}
    d2 = copy.deepcopy(d1)
    d2["tex"] = 2
    d2["v"] = [(x + 3.0, y - 2.0, z) for x, y, z in d2["v"]]
    ref = labeled([d1, d2], {1: "a.png", 2: "b.png"})
    cand_aa = labeled([copy.deepcopy(d1), copy.deepcopy(d2)], {1: "a.png", 2: "b.png"})
    bad1, miss1, unref1, _ = compare(ref, cand_aa, 0.5, 1e-3, 1e-3, set(), verbose=False)
    cand_bad = labeled([copy.deepcopy(d1), copy.deepcopy(d2)], {1: "a.png", 2: "b.png"})
    cand_bad[1][1]["v"] = [(x + 1.0, y, z) for x, y, z in cand_bad[1][1]["v"]]
    bad2, miss2, unref2, _ = compare(ref, cand_bad, 0.5, 1e-3, 1e-3, set(), verbose=False)
    ok = bad1 == 0 and not miss1 and not unref1 and bad2 == 1
    print("SELFTEST %s aa=%d perturbed=%d" % ("PASS" if ok else "FAIL", bad1, bad2))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref")
    ap.add_argument("--ref-frame", type=int)
    ap.add_argument("--cand")
    ap.add_argument("--cand-frame", type=int)
    ap.add_argument("--ref-map")
    ap.add_argument("--cand-map")
    ap.add_argument("--pak", default="work/pak_gametop")
    ap.add_argument("--tol", type=float, default=0.5)
    ap.add_argument("--uv-tol", type=float, default=1e-3)
    ap.add_argument("--alpha-tol", type=float, default=1e-3)
    ap.add_argument("--ignore-assets", default="mcur_1.png")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if not (a.ref and a.cand and a.ref_frame is not None and a.cand_frame is not None):
        raise SystemExit(__doc__)
    ignore = {x.strip() for x in a.ignore_assets.split(",") if x.strip()}
    ref_map, ref_missed = load_map(a.ref_map, a.ref, a.pak)
    cand_map, cand_missed = load_map(a.cand_map, a.cand, a.pak)
    if ref_missed:
        print("ref 纹理 CRC 未匹配 %d 条: %s" % (len(ref_missed), ref_missed[:6]))
    if cand_missed:
        print("cand 纹理 CRC 未匹配 %d 条: %s" % (len(cand_missed), cand_missed[:6]))
    ref = labeled(menu_draw_ab.draws_of(a.ref, a.ref_frame), ref_map)
    cand = labeled(menu_draw_ab.draws_of(a.cand, a.cand_frame), cand_map)
    print("ref draws=%d cand draws=%d" % (len(ref), len(cand)))
    bad, missing, unmatched_ref, _ = compare(ref, cand, a.tol, a.uv_tol, a.alpha_tol, ignore)
    return 0 if bad == 0 and not missing and not unmatched_ref else 1


if __name__ == "__main__":
    sys.exit(main())
