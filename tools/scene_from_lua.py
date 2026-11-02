#!/usr/bin/env python3
"""Lua 调用 → Python 场景模型（T6.4a-r-2c 的第一切片）。

读取 rooted `work/lua_probe/lvlNN.jsonl`（F360 的 parent 1..4），把场景工厂调用
还原成带纹理/位置/尺寸/角度的图元，再与零售 GLFFI02 的指定帧逐 draw 比较。

已实现的工厂（本切片）:
  Set_BackMaterial      两个半屏背景（back_N1/back_N2，NDC 常量）
  Add_LevelMaterial     alias → 纹理名
  Add_GraphSprite       size = 2×scale；root 0/1/3 是屏幕层，2/4 是世界层
  Add_AlphaHint         size = 2×scale；纹理来自同名 LevelMaterial
  Add_CloseButton       close_1.png，3×3
  Add_NextButton        next_1.png，3×3
  mbtn_1/2 + 10×dot_1   引擎/HUD 常量（level 0/1 同坐标）
未实现（用 --ignore 排除）: 齿轮/钉/螺丝/SimplePhysicObject/HudButton/HUD 烟雾等。

用法:
  python tools/scene_from_lua.py --level 0 --ref work/level0_gl.bin --frame 9600 \\
      --ignore "gear_2.png,gear_7.png,gear_3.png,nail_2.png,pic_1.png,pic_2.png,pic_3.png,hint_72.png,mcur_1.png"
  python tools/scene_from_lua.py --level 1 --ref work/gl_levels/lvl01_a.bin --frame 1035 \\
      --ignore "gear_12.png,gear_10.png,screw_1.png,bbox_1.png,chgear_2.png,hint_2.png,hint_3.png,hint_4.png,hint_5.png,hint_6.png,restart2.png,next_4.png,tex=1"

判据:
  `level_draw_ab.compare` 的 `mismatches=0` 且 `unmatched_ref=0`（`missing` 里允许
  被 --ignore 排除的未实现图元）；退出码 0=PASS。默认 `--alpha-tol 1.01`：本切片
  只判几何/UV，alpha 淡入属于动画状态（F339）。
  负例：`--shift 1.0` 把候选整体平移 1 世界单位 ⇒ `mismatches>0`。

覆盖边界:
  - root 偏移由 `--ref` 的前几个同素材对象**标定**（root 0/1/3/2/4 各取首个匹配）：
    这是把相机/父图状态从 oracle 解出来，不是从 Lua 脚本算出来（T6.4d 再收）；
  - 只覆盖 level 0/1 的已实现工厂子集，未实现工厂必须进 --ignore；
  - 只比“画了什么、在哪、什么 UV”，不比混合/caps/像素。

依据: F359（层偏移）、F360（root id）、F340（level 0 手工场景）、F339（A/A 口径）。
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT_DIR, "tools"))

import level_draw_ab  # noqa: E402
import menu_draw_ab  # noqa: E402

# 直接纹理名（不是 LevelMaterial alias）的少量映射；由 objlog/GL 帧反查得到。
NAME_ASSET = {
    "magnet_hero_1": "magneth.png",
}
SCREEN_ROOTS = {0, 1, 3}      # 0 = 未指定 parent 的 graph 工厂默认层
WORLD_ROOTS = {2, 4}


def load_calls(path):
    rows = []
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def center(d):
    xs = [p[0] for p in d["v"]]
    ys = [p[1] for p in d["v"]]
    return ((min(xs) + max(xs)) * 0.5, (min(ys) + max(ys)) * 0.5)


def quad(cx, cy, w, h, angle=0.0, alpha=1.0):
    hw, hh = w * 0.5, h * 0.5
    ca, sa = math.cos(angle), math.sin(angle)
    pts = [(-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh)]
    v = [(cx + x * ca - y * sa, cy + x * sa + y * ca, 0.0) for x, y in pts]
    return {"prim": "QUADS", "tex": 0, "n": 4, "rgba": [1.0, 1.0, 1.0, alpha],
            "v": v, "uv": [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]}


def build(calls):
    """返回 (objects, back_assets)。object: dict(kind, asset, x, y, angle, w, h, root)。"""
    materials = {}
    objects = []
    backs = []
    for row in calls:
        fn, args = row.get("call"), row.get("args") or []
        if fn == "Add_LevelMaterial" and len(args) >= 2:
            materials[args[1]] = args[0]
        elif fn == "Set_BackMaterial" and args:
            name = str(args[0])
            backs.append((name, name + "1.jpg", name + "2.jpg"))
        elif fn == "Add_GraphSprite" and len(args) >= 7:
            root, x, y, ang, sx, sy, name = args[:7]
            asset = materials.get(name) or NAME_ASSET.get(name) or name
            objects.append({"kind": fn, "asset": asset, "x": float(x), "y": float(y),
                            "angle": float(ang), "w": 2.0 * float(sx), "h": 2.0 * float(sy),
                            "root": int(root)})
        elif fn == "Add_AlphaHint" and len(args) >= 7:
            root, x, y, ang, sx, sy, mat = args[:7]
            asset = materials.get(mat) or NAME_ASSET.get(mat) or mat
            objects.append({"kind": fn, "asset": asset, "x": float(x), "y": float(y),
                            "angle": float(ang), "w": 2.0 * float(sx), "h": 2.0 * float(sy),
                            "root": int(root)})
        elif fn in ("Add_CloseButton", "Add_NextButton") and len(args) >= 3:
            root, x, y = args[:3]
            asset = "close_1.png" if fn == "Add_CloseButton" else "next_1.png"
            objects.append({"kind": fn, "asset": asset, "x": float(x), "y": float(y),
                            "angle": 0.0, "w": 3.0, "h": 3.0, "root": int(root)})
    return objects, backs


def ref_labeled(log, pak, frame):
    idmap, missed = menu_draw_ab.load_id_asset(log, pak)
    draws = menu_draw_ab.draws_of(log, frame)
    out = []
    for d in draws:
        out.append((idmap.get(d["tex"], "tex=%s" % d["tex"]), d))
    return out, missed


def calibrate(objects, ref):
    """每个 root 的偏移 = 首个同素材对象的参数坐标 − 零售 draw 中心。"""
    by_name = {}
    for name, d in ref:
        by_name.setdefault(name, []).append(center(d))
    offsets = {}
    for obj in objects:
        if obj["root"] in offsets:
            continue
        hits = by_name.get(obj["asset"])
        if not hits:
            continue
        cx, cy = hits[0]
        offsets[obj["root"]] = (obj["x"] - cx, obj["y"] - cy)
    return offsets


def scene_draws(objects, backs, offsets, shift=(0.0, 0.0)):
    out = []
    sx, sy = shift
    # 背景：两个半屏 NDC 常量（零售 bbox 有 ~0.002 的矩阵量化）
    for _name, top, bottom in backs:
        out.append((top, quad(0.0, 0.5, 2.0, 1.0)))
        out.append((bottom, quad(0.0, -0.5, 2.0, 1.0)))
    for obj in objects:
        if obj["root"] in WORLD_ROOTS:
            ox = oy = 0.0
        else:
            ox, oy = offsets.get(obj["root"], (0.0, 0.0))
        out.append((obj["asset"], quad(obj["x"] - ox + sx, obj["y"] - oy + sy,
                                       obj["w"], obj["h"], obj["angle"])))
    # 引擎/HUD 常量（level 0/1 同坐标）
    out.append(("mbtn_1.png", quad(0.937, 0.9325, 0.252, 0.347)))
    out.append(("mbtn_2.png", quad(0.937, 0.9325, 0.252, 0.347, alpha=0.0)))
    for _ in range(10):
        out.append(("dot_1.png", quad(-1.0, 1.0, 0.0, 0.0, alpha=0.0)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--level", type=int, required=True)
    ap.add_argument("--ref", required=True, help="零售 GLFFI02 日志")
    ap.add_argument("--frame", type=int, required=True)
    ap.add_argument("--pak", default="work/pak_gametop")
    ap.add_argument("--probe-dir", default="work/lua_probe")
    ap.add_argument("--ignore", default="mcur_1.png,tex=1")
    ap.add_argument("--tol", type=float, default=0.5)
    ap.add_argument("--uv-tol", type=float, default=1e-3)
    ap.add_argument("--alpha-tol", type=float, default=1.01,
                    help="本切片只判几何/UV；alpha 默认忽略")
    ap.add_argument("--shift", type=float, default=0.0, help="负例：候选整体平移")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()

    probe = os.path.join(a.probe_dir, "lvl%02d.jsonl" % a.level)
    calls = load_calls(probe)
    objects, backs = build(calls)
    ref, missed = ref_labeled(a.ref, a.pak, a.frame)
    if missed:
        print("ref 纹理 CRC 未匹配 %d 条: %s" % (len(missed), missed[:6]))
    offsets = calibrate(objects, ref)
    print("scene objects=%d backs=%d root_offsets=%s"
          % (len(objects), len(backs), {k: (round(v[0], 3), round(v[1], 3))
                                        for k, v in sorted(offsets.items())}))
    cand = scene_draws(objects, backs, offsets, (a.shift, 0.0))
    ignore = {x.strip() for x in a.ignore.split(",") if x.strip()}
    bad, missing, unref, first = level_draw_ab.compare(
        ref, cand, a.tol, a.uv_tol, a.alpha_tol, ignore, verbose=not a.quiet)
    return 0 if bad == 0 and not unref and not missing else 1


if __name__ == "__main__":
    sys.exit(main())
