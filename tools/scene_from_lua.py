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
                        style 2→sw_arm2.png；紧随的 Add_JointNail 是锚点（半径 1.6），
                        静止位姿 = init+0.5（关节限位）+ 锚点半径 1.6
  Add_WoodBox           style 1..3→wbox_N.png，正方形 4.702
  Add_PushButton        style 1→pbut_1.png，3×1.5（平台 button_platform_1→bplatf_1.png）
  Add_BarDoor           style 1→bar_1.png，7×3.5
  mbtn_1/2 + 10×dot_1   引擎/HUD 常量（level 0/1 同坐标）
未接（用 --ignore 排除）: HUD 烟雾/level_end_box 与未知 style。动态项：
level 3 的 train_1/smoke 已由 `apply_time` 按 `DoProgress` 第一段圆弧复现
（F427/F428）；level 4 的 plunger/shank 由曲柄滑块复现（F378）。

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
  level 2 的 hint/close/箭头 `mismatches>=3`；`--no-arm-settle` ⇒ 摆臂失配。

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
    # 引擎内置材质名（没有 Add_LevelMaterial 登记）：平台纹理来自 pak `bplatf_1.png`。
    "button_platform_1": "bplatf_1.png",
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
SWITCH_ARM = {1: ("sw_arm1.png", 4.0, 2.0),
              2: ("sw_arm2.png", 4.0, 2.0)}
ARM_RADIUS = 1.6
# 静态方块/按钮/门：边长由 level 3/4 的零售 draw 对边量出（F367）。
WOOD_BOX = {1: ("wbox_1.png", 4.702), 2: ("wbox_2.png", 4.702),
            3: ("wbox_3.png", 4.702)}
PUSH_BUTTON = {1: ("pbut_1.png", 3.0, 1.5)}
BAR_DOOR = {1: ("bar_1.png", 7.0, 3.5)}
SHANK_ASSET = "shank_1.png"
SHANK_LONG = 1.3          # 杆绘制长边 = 1.3·L、短边 = 0.65·L（F378）
SMOKE_ASSET = "smoke_5.png"
# level 3 DoProgress 的第一段圆弧（F427）：TrainTime 在 4.8 s 封顶；
# ang = 1.652 - 60·t/500；圆心 (127,-183)、半径 500；Scl(24,12)。
TRAIN_CAP = 4.8
TRAIN_ANG0 = 1.652
TRAIN_OMEGA = 0.12          # 60/500
TRAIN_CIRCLE = (127.0, -183.0, 500.0)
TRAIN_SCL = (24.0, 12.0)
TRAIN_SMOKE_OFFSET = 1.3
# smoke 纹理帧的实测相位/周期（F428）：smoke_60 在 t=0.13 首次出现，之后
# 每 0.70 s 进一帧。4 帧循环；单帧关（level 4 的 smoke_5）保持首帧。
SMOKE_PHASE = 0.13
SMOKE_PERIOD = 0.70
HUD_ASSET = {"btn_restart_2": "restart2.png", "btn_next_4": "next_4.png"}
NAME_ASSET["level_end_box"] = "endbox.png"
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


def build(calls, pak_dir="", settle=True):
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
    body_obj = {}      # body handle → Attach_SimpleGraphObject 的图元
    joints = {}        # Add_JointNail handle → (bodyA, bodyB)
    motors = []        # Set_JointMotors: (joint, speed)
    links = []         # Add_JointSimpleGear: (body1, body2, factor)
    hud = {}
    handles = {}
    cam = (0.0, 0.0)
    pending_arm = None

    def asset_of(name):
        """材质名 → 素材文件：先查 Add_LevelMaterial 别名，再查内置表，最后按
        pak 目录里的同名 `.png`/`.jpg`（引擎自带材质没有登记调用）。"""
        hit = materials.get(name) or NAME_ASSET.get(name)
        if hit:
            return hit
        if pak_dir:
            for ext in (".png", ".jpg"):
                if os.path.exists(os.path.join(pak_dir, str(name) + ext)):
                    return str(name) + ext
        return name

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
            asset = asset_of(name)
            add({"kind": fn, "asset": asset, "x": float(x), "y": float(y),
                 "angle": float(ang), "w": 2.0 * float(sx), "h": 2.0 * float(sy),
                 "root": int(root)}, ret)
        elif fn == "Add_AlphaHint" and len(args) >= 7:
            root, x, y, ang, sx, sy, mat = args[:7]
            asset = asset_of(mat)
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
                obj = add({"kind": fn, "asset": asset_of(mat),
                           "x": body[0], "y": body[1], "angle": body[2],
                           "w": 2.0 * float(sx), "h": 2.0 * float(sy),
                           "root": int(parent)}, ret)
                if obj["asset"] == "train_1.png":
                    # bTrain：Lua 的 Set_ScrObjPos 在 DoProgress 里逐帧移动它；
                    # probe 不跑 Update，所以 init 固定在 body (0,0)，由 apply_time 改写。
                    obj["_train"] = True
                body_obj[int(h)] = obj
        elif fn in ("Add_MetallScrew", "Add_MetallGear") and len(args) >= 5:
            parent, x, y, ang, style = args[:5]
            table = METAL_SCREW if fn == "Add_MetallScrew" else METAL_GEAR
            hit = table.get(int(style))
            if hit:
                # 齿轮的 sprite 局部旋转是 π（F373：同 style 的静态关 = ±π；level 0
                # 用 +π 后三只齿轮的相位与零售逐位吻合）；螺丝的偏移是 0。
                off = 0.0 if fn == "Add_MetallScrew" else math.pi
                add({"kind": fn, "asset": hit[0], "x": float(x), "y": float(y),
                     "angle": float(ang) + off, "w": hit[1], "h": hit[1],
                     "root": int(parent), "_init_body": float(ang)}, ret)
        elif fn == "Add_WoodGear" and len(args) >= 5:
            parent, x, y, ang, style = args[:5]
            hit = WOOD_GEAR.get(int(style))
            if hit:
                add({"kind": fn, "asset": hit[0], "x": float(x), "y": float(y),
                     "angle": float(ang) + math.pi, "w": hit[1], "h": hit[1],
                     "root": int(parent), "_init_body": float(ang)}, ret)
        elif fn == "Add_JointNail" and len(args) >= 5:
            add({"kind": fn, "asset": "nail_2.png",
                 "x": float(args[3]), "y": float(args[4]),
                 "angle": 0.0, "w": NAIL_SIZE, "h": NAIL_SIZE, "root": 0}, ret)
            if isinstance(ret, int):
                joints[ret] = (int(args[1]), int(args[2]))
            if pending_arm is not None:
                # AddSimpleSwitchArm 紧接的 Add_JointNail 就是摆臂的固定锚点。
                pending_arm["pivot"] = (float(args[3]), float(args[4]))
                pending_arm = None
        elif fn == "Add_JointShank" and len(args) >= 7:
            root, body_h, gear_h = int(args[0]), int(args[1]), int(args[2])
            ax, ay, bx, by = (float(v) for v in args[3:7])
            plunger = body_obj.get(body_h)
            gear = handles.get(gear_h)
            if plunger is not None and gear is not None:
                L = math.hypot(ax - bx, ay - by)
                obj = {"kind": fn, "asset": SHANK_ASSET,
                       "x": (ax + bx) * 0.5, "y": (ay + by) * 0.5,
                       "angle": math.atan2(by - ay, bx - ax),
                       "w": SHANK_LONG * L, "h": 0.5 * SHANK_LONG * L,
                       "root": root}
                objects.append(obj)   # 关节 handle 不能用于 Set_ScrObjPos
                obj["_crank"] = {
                    "plunger": plunger, "gear": gear,
                    "ax": ax, "ay": ay, "bx": bx, "by": by, "L": L,
                    "off": ay - plunger["y"], "sign": 1.0 if ay >= by else -1.0,
                    "body_x": plunger["x"],
                }
        elif fn == "Add_JointSimpleGear" and len(args) >= 5:
            ratio = float(args[4])
            if ratio != 0.0:
                links.append((int(args[0]), int(args[1]), -1.0 / ratio))
        elif fn == "Set_JointMotors" and len(args) >= 3:
            if int(args[1]) != 0:
                motors.append((int(args[0]), float(args[2])))
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
        elif fn == "Add_WoodBox" and len(args) >= 5:
            root, x, y, ang, style = args[:5]
            hit = WOOD_BOX.get(int(style))
            if hit:
                add({"kind": fn, "asset": hit[0], "x": float(x), "y": float(y),
                     "angle": float(ang), "w": hit[1], "h": hit[1],
                     "root": int(root)}, ret)
        elif fn == "Add_PushButton" and len(args) >= 5:
            root, x, y, ang, style = args[:5]
            hit = PUSH_BUTTON.get(int(style))
            if hit:
                add({"kind": fn, "asset": hit[0], "x": float(x), "y": float(y),
                     "angle": float(ang), "w": hit[1], "h": hit[2],
                     "root": int(root)}, ret)
        elif fn == "Add_BarDoor" and len(args) >= 5:
            root, x, y, ang, style = args[:5]
            hit = BAR_DOOR.get(int(style))
            if hit:
                add({"kind": fn, "asset": hit[0], "x": float(x), "y": float(y),
                     "angle": float(ang), "w": hit[1], "h": hit[2],
                     "root": int(root)}, ret)
        elif fn == "Add_HudButton" and len(args) >= 7:
            hud[ret] = {"w": float(args[4]), "h": float(args[5]), "tex": args[6],
                        "x": 0.0, "y": 0.0, "alpha": 1.0}
        elif fn == "Add_AlphaHudSprite" and len(args) >= 7:
            # T6.4d：完成面板（endbox）是带 alpha 的 HUD sprite；alpha=0 时引擎
            # 不画（与普通 HUD 的 alpha=0 dot 不同），见 F426/F478。
            add({"kind": fn, "asset": asset_of(args[6]),
                 "x": float(args[1]), "y": float(args[2]),
                 "angle": float(args[3]), "w": 2.0 * float(args[4]),
                 "h": 2.0 * float(args[5]), "alpha": 0.0,
                 "root": int(args[0]), "space": "ndc"}, ret)
        elif fn == "Add_AnimateSmoke" and len(args) >= 6:
            # F428：绘制尺寸 = (2·arg4, 4·arg4)，arg5 不参与（level 3 5×10、
            # level 4 4×8）。root=0 是静态世界烟；root≠0 且本关有 bTrain 时
            # 是 DoProgress 驱动的车头烟（level 3）。
            has_train = any(o.get("_train") for o in objects)
            if int(args[0]) == 0 or has_train:
                frames = sorted(k for k in materials
                                if k.startswith("smoke_") and k[6:].isdigit())
                seq = [materials[k] for k in frames] or [SMOKE_ASSET]
                obj = {"kind": fn, "asset": seq[0],
                       "x": float(args[1]), "y": float(args[2]),
                       "angle": float(args[3]),
                       "w": 2.0 * float(args[4]), "h": 4.0 * float(args[4]),
                       "root": int(args[0]), "_smoke_frames": seq}
                if int(args[0]) != 0:
                    obj["_train_smoke"] = True
                add(obj, ret)
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
        elif fn == "Do_HideCommand" and args:
            if args[0] in hud:
                hud[args[0]]["alpha"] = 0.0
            elif (args[0] in handles and
                  handles[args[0]]["kind"] == "Add_AlphaHudSprite"):
                handles[args[0]]["alpha"] = 0.0
        elif fn == "Do_ShowCommand" and args:
            o = handles.get(args[0]) if args else None
            if o is not None and o["kind"] == "Add_AlphaHudSprite":
                o["alpha"] = 1.0
    if settle:
        settle_arms(objects)
    # 齿轮速度：电机直接给关节里的齿轮；Add_JointSimpleGear 按 factor 传播。
    for joint, speed in motors:
        a, b = joints.get(joint, (0, 0))
        for h in (a, b):
            obj = handles.get(h)
            if obj is not None and obj["kind"] in ("Add_WoodGear", "Add_MetallGear"):
                obj["_speed"] = speed
    for _ in range(len(links) + 1):
        for b1, b2, factor in links:
            o1, o2 = handles.get(b1), handles.get(b2)
            if (o1 is not None and o2 is not None and
                    o1.get("_speed") is not None and o2.get("_speed") is None):
                o2["_speed"] = o1["_speed"] * factor
    for h in hud.values():
        asset = HUD_ASSET.get(h["tex"])
        if asset:
            add({"kind": "Add_HudButton", "asset": asset,
                 "x": h["x"], "y": h["y"], "angle": 0.0,
                 "w": 2.0 * h["w"], "h": 2.0 * h["h"],
                 "alpha": h["alpha"], "root": 0, "space": "ndc"}, 0)
    return objects, backs, cam


def apply_time(objects, t):
    """按 F378 的曲柄滑块规则推进 level 4 的 plunger/shank（t 为关卡时间）。

    齿轮 body 角 = init + w·t；连杆铰点在齿轮本体的局部坐标随齿轮旋转；
    plunger 只能沿竖直轴移动，由杆长 L 解出 body_y；杆的绘制中心/角度取
    两端 anchor 的中点/方向。没有电机的齿轮保持 init 角。
    """
    for obj in objects:
        if obj["kind"] in ("Add_WoodGear", "Add_MetallGear"):
            if obj.get("_speed") is not None:
                obj["angle"] = obj["_init_body"] + obj["_speed"] * t + math.pi
    for obj in objects:
        meta = obj.get("_crank")
        if meta is None:
            continue
        gear = meta["gear"]
        speed = gear.get("_speed") or 0.0
        delta = speed * t
        gx, gy = gear["x"], gear["y"]
        dx, dy = meta["bx"] - gx, meta["by"] - gy
        px = gx + dx * math.cos(delta) - dy * math.sin(delta)
        py = gy + dx * math.sin(delta) + dy * math.cos(delta)
        rem = meta["L"] * meta["L"] - (meta["ax"] - px) ** 2
        if rem < 0.0:
            rem = 0.0
        ay = py + meta["sign"] * math.sqrt(rem)
        body_y = ay - meta["off"]
        meta["plunger"]["x"] = meta["body_x"]
        meta["plunger"]["y"] = body_y
        obj["x"] = (meta["ax"] + px) * 0.5
        obj["y"] = (ay + py) * 0.5
        obj["angle"] = math.atan2(py - ay, px - meta["ax"])
    train = next((o for o in objects if o.get("_train")), None)
    if train is not None:
        # F427：DoProgress 的 TrainTime 在 4.8 s 封顶；位置/角度都用封顶后的
        # 时间，纹理动画用真实关卡时间。
        tt = min(t, TRAIN_CAP)
        ang = TRAIN_ANG0 - TRAIN_OMEGA * tt
        cx0, cy0, r = TRAIN_CIRCLE
        cx = cx0 + r * math.cos(ang)
        cy = cy0 + r * math.sin(ang)
        x = TRAIN_SCL[0] * (cx - 512.0) / 1024.0 * 2.0
        y = TRAIN_SCL[1] * (cy - 256.0) / 512.0 * 2.0
        train["x"], train["y"], train["angle"] = x, y + 2.0, ang
        for obj in objects:
            if not obj.get("_train_smoke"):
                continue
            obj["x"] = x - math.sin(ang) * TRAIN_SMOKE_OFFSET
            obj["y"] = y + 2.0 + math.cos(ang) * TRAIN_SMOKE_OFFSET
            obj["angle"] = ang
            seq = obj.get("_smoke_frames") or [SMOKE_ASSET]
            if len(seq) >= 4:
                idx = int(math.floor((t - SMOKE_PHASE) / SMOKE_PERIOD)) % 4
                obj["asset"] = seq[idx]


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
        if (obj.get("kind") == "Add_AlphaHudSprite" and
                obj.get("alpha", 1.0) <= 0.0):
            continue
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
        # 四边形对 π 旋转对称：ref 只能把角度定到 mod π。差为 0/π 时**保留 Lua
        # 的 init 角**（level 1/2 的齿轮没有电机，实测角速度 0）；只有真实旋转
        #（level 0 的电机链）才用 ref 的角。
        delta = (ang - obj["angle"] + math.pi) % (2.0 * math.pi) - math.pi
        if abs(abs(delta) - math.pi) > 1e-3 and abs(delta) > 1e-3:
            obj["angle"] = ang


def settle_arms(objects):
    """摆臂的静止位姿（F374）：body 角 = init + 0.5（关节限位 +0.5），
    位置由锚点 + 半径 1.6 决定；sprite 角 = body − π/2。不再从 ref 拟合。"""
    out = []
    for obj in objects:
        if obj["kind"] != "Add_SwitchArm" or not obj.get("pivot"):
            continue
        body = obj.get("init_angle", obj["angle"] + math.pi * 0.5) + 0.5
        px, py = obj["pivot"]
        obj["x"] = px - ARM_RADIUS * math.sin(body)
        obj["y"] = py + ARM_RADIUS * math.cos(body)
        obj["angle"] = body - math.pi * 0.5
        out.append((obj["asset"], 0.5))
    return out

def dump_objects(objects, cam, path):
    """场景图元 JSONL（与 src/host_lcl/scenemodel.pas 的 SaveJsonl 同 schema）。

    只导出 build() 的结果（含摆臂 settle；不含齿轮动画相位），用于 Pascal 移植对拍。
    """
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write('{"kind":"_camera","x":%s,"y":%s}\n'
                % (num9(cam[0]), num9(cam[1])))
        for o in objects:
            rec = {
                "kind": o["kind"],
                "asset": o["asset"],
                "x": float(o["x"]),
                "y": float(o["y"]),
                "angle": float(o["angle"]),
                "w": float(o["w"]),
                "h": float(o["h"]),
                "alpha": float(o.get("alpha", 1.0)),
                "space": "ndc" if o.get("space") == "ndc" else "world",
                "root": int(o.get("root", 0)),
            }
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def num9(v):
    """与 Pascal FloatToStrF(ffGeneral, 9) 对齐的数值文本。"""
    return ("%.9g" % float(v))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--level", type=int, required=True)
    ap.add_argument("--ref", help="零售 GLFFI02 日志（--dump-objects 时可省）")
    ap.add_argument("--frame", type=int)
    ap.add_argument("--pak", default="work/pak_gametop")
    ap.add_argument("--probe-dir", default="work/lua_probe")
    ap.add_argument("--ignore", default="mcur_1.png,tex=1")
    ap.add_argument("--allow-missing", default="",
                    help="允许的候选独有素材（隐藏提示层），逗号分隔")
    ap.add_argument("--time", type=float, default=None,
                    help="应用 F378 曲柄滑块/齿轮相位（秒）；不给则从 ref 拟合齿轮角")
    ap.add_argument("--tol", type=float, default=0.5)
    ap.add_argument("--uv-tol", type=float, default=1e-3)
    ap.add_argument("--alpha-tol", type=float, default=1.01,
                    help="本切片只判几何/UV；alpha 默认忽略")
    ap.add_argument("--shift", type=float, default=0.0, help="负例：候选整体平移")
    ap.add_argument("--dump-objects", default="",
                    help="把 build() 的图元写成 JSONL（Pascal 模型对拍用）")
    ap.add_argument("--no-arm-settle", action="store_true",
                    help="负例：摆臂停在 init 姿态（不 settle 到关节限位）")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()

    probe = os.path.join(a.probe_dir, "lvl%02d.jsonl" % a.level)
    calls = load_calls(probe)
    objects, backs, cam = build(calls, a.pak, not a.no_arm_settle)
    if a.time is not None:
        apply_time(objects, a.time)
    if a.dump_objects:
        dump_objects(objects, cam, a.dump_objects)
        if not a.ref or a.frame is None:
            return 0
    ref, missed = ref_labeled(a.ref, a.pak, a.frame)
    if missed:
        print("ref 纹理 CRC 未匹配 %d 条: %s" % (len(missed), missed[:6]))
    if a.time is None:
        fit_gear_angles(objects, ref, cam)
    print("scene objects=%d backs=%d camera=(%.3f,%.3f)"
          % (len(objects), len(backs), cam[0], cam[1]))
    if not a.no_arm_settle:
        for o in objects:
            if o["kind"] == "Add_SwitchArm":
                print("arm %-12s swing=+0.500" % o["asset"])
    cand = scene_draws(objects, backs, cam, (a.shift, 0.0))
    ignore = {x.strip() for x in a.ignore.split(",") if x.strip()}
    bad, missing, unref, first = level_draw_ab.compare(
        ref, cand, a.tol, a.uv_tol, a.alpha_tol, ignore, verbose=not a.quiet)
    allow = {x.strip() for x in a.allow_missing.split(",") if x.strip()}
    unexpected = [m for m in missing if m not in allow]
    if unexpected:
        print("unexpected cand-only: %s" % unexpected)
    return 0 if bad == 0 and not unref and not unexpected else 1


if __name__ == "__main__":
    sys.exit(main())
