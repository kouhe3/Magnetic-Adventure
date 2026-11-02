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
  Add_WoodGear          style→(gear_2/7/3, 7.31/7.54/7.37)，root 偏移
  Add_MetallGear        style→(gear_10/gear_12, 3.69/7.37)，世界层
  Add_MetallScrew       style 1→screw_1.png，3.248，世界层
  Add_JointNail         nail_2.png，1.6，root 偏移
  Add_SimplePhysicObject + Attach_SimpleGraphObject
                        (body x,y,angle) + 材质纹理，size=2×scale，世界层
  Add_HudButton + Set_ScrObjPos + Do_HideCommand
                        设计空间 1018×739 → NDC (x/509, -y/369.5)，size=(2w/509,2h/369.5)
  mbtn_1/2 + 10×dot_1   引擎/HUD 常量（level 0/1 同坐标）
未实现（用 --ignore 排除）: HUD 烟雾/level_end_box、未知 style 的齿轮。

用法:
  python tools/scene_from_lua.py --level 0 --ref work/level0_gl.bin --frame 9600 \\
      --ignore "pic_1.png,pic_2.png,pic_3.png,hint_72.png,mcur_1.png"
  python tools/scene_from_lua.py --level 1 --ref work/gl_levels/lvl01_a.bin --frame 1035 \\
      --ignore "chgear_2.png,hint_2.png,hint_3.png,hint_4.png,hint_5.png,hint_6.png,tex=1"

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
# 齿轮/螺丝的 style → (asset, 边长)；边长由 retail draw 的对边长度量出（F361）。
# 未知 style 暂不建图元（调用方用 --ignore 兜住），扩关卡时再补表。
WOOD_GEAR = {1: ("gear_1.png", 3.6896), 2: ("gear_2.png", 7.3141),
             3: ("gear_3.png", 7.3668), 5: ("gear_7.png", 7.5408)}
METAL_GEAR = {1: ("gear_10.png", 3.6896), 2: ("gear_11.png", 7.3141),
              3: ("gear_12.png", 7.3668)}
METAL_SCREW = {1: ("screw_1.png", 3.248)}
NAIL_SIZE = 1.6
HUD_ASSET = {"btn_restart_2": "restart2.png", "btn_next_4": "next_4.png"}
HUD_HALF_W, HUD_HALF_H = 509.0, 369.5   # 设计空间 1018×739 的半宽/半高（F188）


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
    bodies = {}
    hud = {}
    for row in calls:
        fn, args = row.get("call"), row.get("args") or []
        ret = row.get("ret")
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
        elif fn == "Add_SimplePhysicObject" and len(args) >= 3:
            bodies[ret] = (float(args[0]), float(args[1]), float(args[2]))
        elif fn == "Attach_SimpleGraphObject" and len(args) >= 5:
            h, parent, sx, sy, mat = args[:5]
            body = bodies.get(h)
            if body is not None:
                objects.append({"kind": fn, "asset": materials.get(mat, mat),
                                "x": body[0], "y": body[1], "angle": body[2],
                                "w": 2.0 * float(sx), "h": 2.0 * float(sy),
                                "root": int(parent), "world": True})
        elif fn in ("Add_MetallScrew", "Add_MetallGear") and len(args) >= 5:
            parent, x, y, ang, style = args[:5]
            table = METAL_SCREW if fn == "Add_MetallScrew" else METAL_GEAR
            hit = table.get(int(style))
            if hit:
                objects.append({"kind": fn, "asset": hit[0], "x": float(x), "y": float(y),
                                "angle": float(ang), "w": hit[1], "h": hit[1],
                                "root": int(parent), "world": True})
        elif fn == "Add_WoodGear" and len(args) >= 5:
            parent, x, y, ang, style = args[:5]
            hit = WOOD_GEAR.get(int(style))
            if hit:
                objects.append({"kind": fn, "asset": hit[0], "x": float(x), "y": float(y),
                                "angle": float(ang), "w": hit[1], "h": hit[1],
                                "root": int(parent)})
        elif fn == "Add_JointNail" and len(args) >= 5:
            objects.append({"kind": fn, "asset": "nail_2.png",
                            "x": float(args[3]), "y": float(args[4]),
                            "angle": 0.0, "w": NAIL_SIZE, "h": NAIL_SIZE, "root": 0})
        elif fn == "Add_HudButton" and len(args) >= 7:
            hud[ret] = {"w": float(args[4]), "h": float(args[5]), "tex": args[6],
                        "x": 0.0, "y": 0.0, "alpha": 1.0}
        elif fn == "Set_ScrObjPos" and len(args) >= 3 and args[0] in hud:
            hud[args[0]]["x"] = float(args[1])
            hud[args[0]]["y"] = float(args[2])
        elif fn == "Do_HideCommand" and args and args[0] in hud:
            hud[args[0]]["alpha"] = 0.0
    for h in hud.values():
        asset = HUD_ASSET.get(h["tex"])
        if asset:
            objects.append({"kind": "Add_HudButton", "asset": asset,
                            "x": h["x"], "y": h["y"], "angle": 0.0,
                            "w": 2.0 * h["w"], "h": 2.0 * h["h"],
                            "alpha": h["alpha"], "root": 0, "space": "ndc"})
    return objects, backs


def ref_labeled(log, pak, frame):
    idmap, missed = menu_draw_ab.load_id_asset(log, pak)
    draws = menu_draw_ab.draws_of(log, frame)
    out = []
    for d in draws:
        out.append((idmap.get(d["tex"], "tex=%s" % d["tex"]), d))
    return out, missed


def calibrate(objects, ref):
    """每个 root 的偏移 + 世界层偏移 = 参数坐标 − 零售 draw 中心；按匹配**投票**。

    单个对象可能撞名（例：level 2 的 `level_circle_1` AlphaHint 与物理圆同叫
    circle_1.png，位置却不同）；投票能把这个离群值压掉。
    """
    by_name = {}
    for name, d in ref:
        by_name.setdefault(name, []).append(center(d))
    votes = {}
    wvotes = {}
    for obj in objects:
        hits = by_name.get(obj["asset"])
        if not hits:
            continue
        cx, cy = hits[0]
        key = (round(obj["x"] - cx, 3), round(obj["y"] - cy, 3))
        if obj.get("world"):
            wvotes[key] = wvotes.get(key, 0) + 1
        else:
            votes.setdefault(obj["root"], {})
            votes[obj["root"]][key] = votes[obj["root"]].get(key, 0) + 1
    offsets = {}
    for root, counts in votes.items():
        offsets[root] = max(counts.items(), key=lambda kv: kv[1])[0]
    world = max(wvotes.items(), key=lambda kv: kv[1])[0] if wvotes else (0.0, 0.0)
    return offsets, world


def scene_draws(objects, backs, offsets, world, shift=(0.0, 0.0)):
    out = []
    sx, sy = shift
    # 背景：两个半屏 NDC 常量（零售 bbox 有 ~0.002 的矩阵量化）
    for _name, top, bottom in backs:
        out.append((top, quad(0.0, 0.5, 2.0, 1.0)))
        out.append((bottom, quad(0.0, -0.5, 2.0, 1.0)))
    for obj in objects:
        if obj.get("space") == "ndc":
            cx = obj["x"] / HUD_HALF_W
            cy = -obj["y"] / HUD_HALF_H
            out.append((obj["asset"], quad(cx + sx, cy + sy,
                                           obj["w"] / HUD_HALF_W,
                                           obj["h"] / HUD_HALF_H,
                                           0.0, obj.get("alpha", 1.0))))
            continue
        if obj.get("world"):
            ox, oy = world
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


def fit_gear_angles(objects, ref, offsets, world):
    """齿轮的绘制角 = body angle + 电机 spin；spin 是动画状态，从 oracle 帧标定。

    只对 Add_WoodGear/Add_MetallGear 生效；用同素材 + 最近中心的 ref draw 取
    第一条边的方向角。bbox 判据下四边形的 90° 等价不影响结果。
    """
    by_name = {}
    for name, d in ref:
        v = d["v"]
        ang = math.atan2(v[1][1] - v[0][1], v[1][0] - v[0][0])
        by_name.setdefault(name, []).append((center(d), ang))
    for obj in objects:
        if obj["kind"] not in ("Add_WoodGear", "Add_MetallGear"):
            continue
        hits = by_name.get(obj["asset"])
        if not hits:
            continue
        ox, oy = world if obj.get("world") else offsets.get(obj["root"], (0.0, 0.0))
        cx, cy = obj["x"] - ox, obj["y"] - oy
        _c, ang = min(hits, key=lambda h: (h[0][0] - cx) ** 2 + (h[0][1] - cy) ** 2)
        obj["angle"] = ang


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
    offsets, world = calibrate(objects, ref)
    fit_gear_angles(objects, ref, offsets, world)
    print("scene objects=%d backs=%d root_offsets=%s world_offset=%s"
          % (len(objects), len(backs),
             {k: (round(v[0], 3), round(v[1], 3)) for k, v in sorted(offsets.items())},
             (round(world[0], 3), round(world[1], 3))))
    cand = scene_draws(objects, backs, offsets, world, (a.shift, 0.0))
    ignore = {x.strip() for x in a.ignore.split(",") if x.strip()}
    bad, missing, unref, first = level_draw_ab.compare(
        ref, cand, a.tol, a.uv_tol, a.alpha_tol, ignore, verbose=not a.quiet)
    return 0 if bad == 0 and not unref and not missing else 1


if __name__ == "__main__":
    sys.exit(main())
