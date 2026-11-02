#!/usr/bin/env python3
"""Lua 调用 → Python 场景模型（T6.4a-r-2c 的切片）。

读取 rooted `work/lua_probe/lvlNN.jsonl`（F360 的 parent 1..4），把场景工厂调用
还原成带纹理/位置/尺寸/角度的图元，再与零售 GLFFI02 的指定帧逐 draw 比较。

坐标语义（F364）：探针返回真实的 `Get_RealViewRect()`（相机 ± 半视图）后，脚本里
的坐标已经是世界坐标；模型只减去 `Set_CameraPosition` 的相机，不再按父图 root 标定
偏移。`Set_ScrObjPos` 按句柄回放（OnResizeForm/动画的最终位置）。

已实现的工厂（本切片）:
  Set_BackMaterial      两个半屏背景（back_N1/back_N2，NDC 常量）
  Add_LevelMaterial     alias → 纹理名
  Add_GraphSprite       size = 2×scale
  Add_AlphaHint         size = 2×scale；纹理来自同名 LevelMaterial
  Add_CloseButton       close_1.png，3×3
  Add_NextButton        next_1.png，3×3
  Add_WoodGear          style→(gear_1/2/3/7, 3.69/7.31/7.37/7.54)
  Add_MetallGear        style→(gear_10/11/12, 3.69/7.31/7.37)
  Add_MetallScrew       style 1→screw_1.png，3.248
  Add_JointNail         nail_2.png，1.6
  Add_SimplePhysicObject + Attach_SimpleGraphObject
                        (body x,y,angle) + 材质纹理，size=2×scale
  Add_HudButton + Set_ScrObjPos + Do_HideCommand
                        设计空间 1018×739 → NDC (x/509, -y/369.5)，size=(2w/509,2h/369.5)
  Set_CameraPosition    相机（模型唯一的全局偏移）
  Set_ScrObjPos         按句柄改写位置/角度（含 OnResizeForm 与时钟箭头动画）
  Add_SwitchArm         style 1→sw_arm1.png 4×2，中心在 body、sprite 角 = body−π/2；
                        紧随的 Add_JointNail 是锚点（半径 1.6），动态摆角由 ref 长边拟合
  mbtn_1/2 + 10×dot_1   引擎/HUD 常量（level 0/1 同坐标）
未实现（用 --ignore 排除）: HUD 烟雾/level_end_box、未知 style 的齿轮/摆臂。

用法:
  python tools/scene_from_lua.py --level 0 --ref work/level0_gl.bin --frame 9600 \\
      --ignore "pic_1.png,pic_2.png,pic_3.png,hint_72.png,mcur_1.png"
  python tools/scene_from_lua.py --level 1 --ref work/gl_levels/lvl01_a.bin --frame 1035 \\
      --ignore "chgear_2.png,hint_2.png,hint_3.png,hint_4.png,hint_5.png,hint_6.png,tex=1"

判据:
  `level_draw_ab.compare` 的 `mismatches=0` 且 `unmatched_ref=0`；`missing`（候选
  独有）必须 ⊆ `--allow-missing`（Create 时被 `Do_HideCommand` 隐藏、本帧不画的
  提示层）。退出码 0=PASS。默认 `--alpha-tol 1.01`：本切片只判几何/UV，alpha 淡入
  属于动画状态（F339）。负例：`--shift 1.0` ⇒ `mismatches>0`；
  把探针的 `Get_RealViewRect` 退回 0 桩（`LUA_PROBE_VIEWRECT=0` 重生成语料）⇒
  level 2 的 hint/close/箭头 `mismatches>=3`。

覆盖边界:
  - 相机只取 `Set_CameraPosition`；`Get_RealViewRect` 的语义要由探针实现（F364），
    旧语料（0 桩）会让 `left/top` 派生的对象整体差半个视图；
  - 只覆盖已实现的工厂子集；未实现工厂/素材必须进 --ignore 或 --allow-missing；
  - 只比“画了什么、在哪、什么 UV”，不比混合/caps/像素。

依据: F364（`Get_RealViewRect` 语义）、F360（root id）、F340（level 0 手工场景）、
F339（A/A 口径）。
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
# Add_SwitchArm style → (asset, 长边, 短边)。摆臂是物理体：图元中心在 body 原点，
# sprite 角 = body 角 − π/2；body 由关节锚点以半径 1.6 悬挂（basefs.lua:81-84）。
SWITCH_ARM = {1: ("sw_arm1.png", 4.0, 2.0)}
ARM_RADIUS = 1.6
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
    """返回 (objects, back_assets, camera)。

    坐标语义（F364）：探针返回真实的 `Get_RealViewRect()` 后，脚本里的坐标已经是
    **世界坐标**（原来 `left/top == 0` 的桩值与零售差了半个视图）；绘制时统一只减
    相机，不再按父图 root 标定偏移。`Set_ScrObjPos` 是脚本的最终位置（Create 之后
    还有 OnResizeForm/动画），必须按句柄回放。
    """
    materials = {}
    objects = []
    backs = []
    bodies = {}
    hud = {}
    handles = {}
    cam = (0.0, 0.0)
    pending_arm = None

    def add(obj, ret):
        objects.append(obj)
        if isinstance(ret, int) and ret > 1000:
            handles[ret] = obj
        return obj

    for row in calls:
        fn, args = row.get("call"), row.get("args") or []
        ret = row.get("ret")
        if fn == "Set_CameraPosition" and len(args) >= 2:
            cam = (float(args[0]), float(args[1]))
        elif fn == "Add_LevelMaterial" and len(args) >= 2:
            materials[args[1]] = args[0]
        elif fn == "Set_BackMaterial" and args:
            name = str(args[0])
            backs.append((name, name + "1.jpg", name + "2.jpg"))
        elif fn == "Add_GraphSprite" and len(args) >= 7:
            root, x, y, ang, sx, sy, name = args[:7]
            asset = materials.get(name) or NAME_ASSET.get(name) or name
            add({"kind": fn, "asset": asset, "x": float(x), "y": float(y),
                 "angle": float(ang), "w": 2.0 * float(sx), "h": 2.0 * float(sy),
                 "root": int(root)}, ret)
        elif fn == "Add_AlphaHint" and len(args) >= 7:
            root, x, y, ang, sx, sy, mat = args[:7]
            asset = materials.get(mat) or NAME_ASSET.get(mat) or mat
            add({"kind": fn, "asset": asset, "x": float(x), "y": float(y),
                 "angle": float(ang), "w": 2.0 * float(sx), "h": 2.0 * float(sy),
                 "root": int(root)}, ret)
        elif fn in ("Add_CloseButton", "Add_NextButton") and len(args) >= 3:
            root, x, y = args[:3]
            asset = "close_1.png" if fn == "Add_CloseButton" else "next_1.png"
            add({"kind": fn, "asset": asset, "x": float(x), "y": float(y),
                 "angle": 0.0, "w": 3.0, "h": 3.0, "root": int(root)}, ret)
        elif fn == "Add_SimplePhysicObject" and len(args) >= 3:
            bodies[ret] = (float(args[0]), float(args[1]), float(args[2]))
        elif fn == "Attach_SimpleGraphObject" and len(args) >= 5:
            h, parent, sx, sy, mat = args[:5]
            body = bodies.get(h)
            if body is not None:
                add({"kind": fn, "asset": materials.get(mat, mat),
                     "x": body[0], "y": body[1], "angle": body[2],
                     "w": 2.0 * float(sx), "h": 2.0 * float(sy),
                     "root": int(parent)}, ret)
        elif fn in ("Add_MetallScrew", "Add_MetallGear") and len(args) >= 5:
            parent, x, y, ang, style = args[:5]
            table = METAL_SCREW if fn == "Add_MetallScrew" else METAL_GEAR
            hit = table.get(int(style))
            if hit:
                add({"kind": fn, "asset": hit[0], "x": float(x), "y": float(y),
                     "angle": float(ang), "w": hit[1], "h": hit[1],
                     "root": int(parent)}, ret)
        elif fn == "Add_WoodGear" and len(args) >= 5:
            parent, x, y, ang, style = args[:5]
            hit = WOOD_GEAR.get(int(style))
            if hit:
                add({"kind": fn, "asset": hit[0], "x": float(x), "y": float(y),
                     "angle": float(ang), "w": hit[1], "h": hit[1],
                     "root": int(parent)}, ret)
        elif fn == "Add_JointNail" and len(args) >= 5:
            add({"kind": fn, "asset": "nail_2.png",
                 "x": float(args[3]), "y": float(args[4]),
                 "angle": 0.0, "w": NAIL_SIZE, "h": NAIL_SIZE, "root": 0}, ret)
            if pending_arm is not None:
                # AddSimpleSwitchArm 紧接的 Add_JointNail 就是摆臂的固定锚点。
                pending_arm["pivot"] = (float(args[3]), float(args[4]))
                pending_arm = None
        elif fn == "Add_SwitchArm" and len(args) >= 5:
            root, x, y, ang, style = args[:5]
            hit = SWITCH_ARM.get(int(style))
            if hit:
                pending_arm = add({"kind": fn, "asset": hit[0],
                                   "x": float(x), "y": float(y),
                                   "angle": float(ang) - math.pi * 0.5,
                                   "init_angle": float(ang),
                                   "w": hit[1], "h": hit[2],
                                   "root": int(root), "pivot": None}, ret)
        elif fn == "Add_HudButton" and len(args) >= 7:
            hud[ret] = {"w": float(args[4]), "h": float(args[5]), "tex": args[6],
                        "x": 0.0, "y": 0.0, "alpha": 1.0}
        elif fn == "Set_ScrObjPos" and len(args) >= 3:
            if args[0] in hud:
                hud[args[0]]["x"] = float(args[1])
                hud[args[0]]["y"] = float(args[2])
            elif args[0] in handles:
                obj = handles[args[0]]
                obj["x"] = float(args[1])
                obj["y"] = float(args[2])
                if len(args) >= 4:
                    obj["angle"] = float(args[3])
        elif fn == "Do_HideCommand" and args and args[0] in hud:
            hud[args[0]]["alpha"] = 0.0
    for h in hud.values():
        asset = HUD_ASSET.get(h["tex"])
        if asset:
            add({"kind": "Add_HudButton", "asset": asset,
                 "x": h["x"], "y": h["y"], "angle": 0.0,
                 "w": 2.0 * h["w"], "h": 2.0 * h["h"],
                 "alpha": h["alpha"], "root": 0, "space": "ndc"}, 0)
    return objects, backs, cam


def ref_labeled(log, pak, frame):
    idmap, missed = menu_draw_ab.load_id_asset(log, pak)
    draws = menu_draw_ab.draws_of(log, frame)
    out = []
    for d in draws:
        out.append((idmap.get(d["tex"], "tex=%s" % d["tex"]), d))
    return out, missed


def scene_draws(objects, backs, cam, shift=(0.0, 0.0)):
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
        out.append((obj["asset"], quad(obj["x"] - cam[0] + sx,
                                       obj["y"] - cam[1] + sy,
                                       obj["w"], obj["h"], obj["angle"])))
    # 引擎/HUD 常量（level 0/1 同坐标）
    out.append(("mbtn_1.png", quad(0.937, 0.9325, 0.252, 0.347)))
    out.append(("mbtn_2.png", quad(0.937, 0.9325, 0.252, 0.347, alpha=0.0)))
    for _ in range(10):
        out.append(("dot_1.png", quad(-1.0, 1.0, 0.0, 0.0, alpha=0.0)))
    return out


def fit_gear_angles(objects, ref, cam):
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
        cx, cy = obj["x"] - cam[0], obj["y"] - cam[1]
        _c, ang = min(hits, key=lambda h: (h[0][0] - cx) ** 2 + (h[0][1] - cy) ** 2)
        obj["angle"] = ang


def fit_arm_pose(objects, ref, cam):
    """摆臂是物理体：init 姿态之外还有重力/关节限位决定的动态角（F366）。

    从 ref 的同素材四边形取**长边**方向作为 sprite 角，body 角 = sprite 角 + π/2；
    再由固定锚点 `pivot` 与半径 1.6 预测 body 位置，与 ref 的四边形中心比较。
    返回 [(asset, 摆角相对 init, center_err)]；center_err 是半径/锚点假设的硬判据。
    """
    by_name = {}
    for name, d in ref:
        v = d["v"]
        lens = [math.hypot(v[(i + 1) % 4][0] - v[i][0],
                           v[(i + 1) % 4][1] - v[i][1]) for i in range(4)]
        k = max(range(4), key=lambda i: lens[i])
        ang = math.atan2(v[(k + 1) % 4][1] - v[k][1],
                         v[(k + 1) % 4][0] - v[k][0])
        cx = sum(p[0] for p in v) / 4.0
        cy = sum(p[1] for p in v) / 4.0
        by_name.setdefault(name, []).append(((cx, cy), ang))
    out = []
    for obj in objects:
        if obj["kind"] != "Add_SwitchArm" or obj.get("pivot") is None:
            continue
        hits = by_name.get(obj["asset"])
        if not hits:
            continue
        init = (obj["x"], obj["y"])
        (cx, cy), ang = min(hits, key=lambda h: (h[0][0] - init[0]) ** 2 +
                                               (h[0][1] - init[1]) ** 2)
        body = ang + math.pi * 0.5
        px, py = obj["pivot"]
        pred = (px - ARM_RADIUS * math.sin(body),
                py + ARM_RADIUS * math.cos(body))
        err = math.hypot(pred[0] - cam[0] - cx, pred[1] - cam[1] - cy)
        obj["angle"] = ang
        obj["x"], obj["y"] = pred
        out.append((obj["asset"], body - obj.get("init_angle", body), err))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--level", type=int, required=True)
    ap.add_argument("--ref", required=True, help="零售 GLFFI02 日志")
    ap.add_argument("--frame", type=int, required=True)
    ap.add_argument("--pak", default="work/pak_gametop")
    ap.add_argument("--probe-dir", default="work/lua_probe")
    ap.add_argument("--ignore", default="mcur_1.png,tex=1")
    ap.add_argument("--allow-missing", default="",
                    help="允许的候选独有素材（隐藏提示层），逗号分隔")
    ap.add_argument("--tol", type=float, default=0.5)
    ap.add_argument("--uv-tol", type=float, default=1e-3)
    ap.add_argument("--alpha-tol", type=float, default=1.01,
                    help="本切片只判几何/UV；alpha 默认忽略")
    ap.add_argument("--shift", type=float, default=0.0, help="负例：候选整体平移")
    ap.add_argument("--no-arm-fit", action="store_true",
                    help="负例：摆臂停在 init 姿态（不按 ref 拟合动态角）")
    ap.add_argument("--arm-tol", type=float, default=0.02,
                    help="摆臂 center_err 上限（半径 1.6/锚点假设的硬判据）")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()

    probe = os.path.join(a.probe_dir, "lvl%02d.jsonl" % a.level)
    calls = load_calls(probe)
    objects, backs, cam = build(calls)
    ref, missed = ref_labeled(a.ref, a.pak, a.frame)
    if missed:
        print("ref 纹理 CRC 未匹配 %d 条: %s" % (len(missed), missed[:6]))
    fit_gear_angles(objects, ref, cam)
    arms = [] if a.no_arm_fit else fit_arm_pose(objects, ref, cam)
    print("scene objects=%d backs=%d camera=(%.3f,%.3f)"
          % (len(objects), len(backs), cam[0], cam[1]))
    for asset, swing, err in arms:
        print("arm %-12s swing=%+.3f center_err=%.4f" % (asset, swing, err))
    cand = scene_draws(objects, backs, cam, (a.shift, 0.0))
    ignore = {x.strip() for x in a.ignore.split(",") if x.strip()}
    bad, missing, unref, first = level_draw_ab.compare(
        ref, cand, a.tol, a.uv_tol, a.alpha_tol, ignore, verbose=not a.quiet)
    allow = {x.strip() for x in a.allow_missing.split(",") if x.strip()}
    unexpected = [m for m in missing if m not in allow]
    if unexpected:
        print("unexpected cand-only: %s" % unexpected)
    arm_bad = [x for x in arms if x[2] > a.arm_tol]
    if arm_bad:
        print("arm center_err too large: %s" % arm_bad)
    return 0 if bad == 0 and not unref and not unexpected and not arm_bad else 1


if __name__ == "__main__":
    sys.exit(main())
