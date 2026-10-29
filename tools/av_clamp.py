"""测两边 DLL 的速度钳位：受控 island（两盒重叠成接触）里给定 lv/av，step 后读回。

用法：$PY32 tools/av_clamp.py
判据：
  - 饱和点 = 钳位上界（输入继续加大而输出不变）
  - 若饱和点随 dt 变化（≈0.5π/dt）⇒ "每步最大旋转"式钳位；若与 dt 无关 ⇒ 常数钳位（250 类）
"""
import ctypes
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILES = {"orig": os.path.join(ROOT, "bin", "gametop", "b2Physics.dll"),
         "ours": os.path.join(ROOT, "build", "Release", "b2Physics.dll")}


class Vec2(ctypes.Structure):
    _fields_ = [("x", ctypes.c_float), ("y", ctypes.c_float)]


class AABB(ctypes.Structure):
    _fields_ = [("lo", Vec2), ("hi", Vec2)]


class BodyDef(ctypes.Structure):
    _fields_ = [("world", ctypes.c_void_p), ("f4", ctypes.c_float), ("f8", ctypes.c_float),
                ("b12", ctypes.c_ubyte), ("b13", ctypes.c_ubyte), ("b14", ctypes.c_ubyte)]


class BoxDef(ctypes.Structure):
    _fields_ = [("body", ctypes.c_void_p), ("friction", ctypes.c_float),
                ("restitution", ctypes.c_float), ("density", ctypes.c_float),
                ("sensor", ctypes.c_ubyte), ("cx", ctypes.c_float), ("cy", ctypes.c_float),
                ("hw", ctypes.c_float), ("hh", ctypes.c_float)]


def load(which):
    lib = ctypes.CDLL(FILES[which])
    lib.b2_CreateWorld.restype = ctypes.c_void_p
    lib.b2_CreateWorld.argtypes = [ctypes.POINTER(AABB), ctypes.POINTER(Vec2)]
    lib.b2_World_CreateBody.restype = ctypes.c_void_p
    lib.b2_World_CreateBody.argtypes = [ctypes.POINTER(BodyDef)]
    lib.b2_Body_CreateShape_Box.restype = ctypes.c_void_p
    lib.b2_Body_CreateShape_Box.argtypes = [ctypes.POINTER(BoxDef)]
    lib.b2_Body_SetMassFromShapes.argtypes = [ctypes.c_void_p]
    lib.b2_World_Step.argtypes = [ctypes.c_void_p, ctypes.c_float, ctypes.c_int, ctypes.c_int]
    return lib


def make(which, vx, w, dt):
    lib = load(which)
    box = AABB(Vec2(-100.0, -100.0), Vec2(100.0, 100.0))
    g = Vec2(0.0, 0.0)
    world = lib.b2_CreateWorld(ctypes.byref(box), ctypes.byref(g))
    a = lib.b2_World_CreateBody(ctypes.byref(BodyDef(world, 0.0, 0.0, 0, 0, 0)))
    lib.b2_Body_CreateShape_Box(ctypes.byref(BoxDef(a, 0.3, 0.0, 1.0, 0, 0.0, 0.0, 1.0, 1.0)))
    b = lib.b2_World_CreateBody(ctypes.byref(BodyDef(world, 0.0, 0.0, 1, 0, 0)))
    lib.b2_Body_CreateShape_Box(ctypes.byref(BoxDef(b, 0.3, 0.0, 1.0, 0, 0.0, 0.6, 1.0, 1.0)))
    lib.b2_Body_SetMassFromShapes(b)
    f = ctypes.c_float.from_address
    f(b + 68).value = vx
    f(b + 72).value = 0.0
    f(b + 76).value = w
    lib.b2_World_Step(world, dt, 10, 10)
    return (f(b + 68).value, f(b + 76).value, f(b + 60).value,
            f(b + 132).value, f(b + 136).value)


def main():
    ws = [1.0, 50.0, 140.0, 150.0, 155.0, 157.0, 158.0, 160.0, 200.0, 249.0, 250.0,
          251.0, 300.0, 1000.0, -300.0, -1000.0, 1e4]
    print(f'{"w_in":>9} | {"orig.dt=.01 (vx,w,a)":>34} | {"ours.dt=.01 (vx,w,a)":>34}')
    for w in ws:
        o = make("orig", 0.0, w, 0.01)
        u = make("ours", 0.0, w, 0.01)
        print(f'{w:9.1f} | {o[1]:14.5f} {o[2]:12.4f} {o[4]:9.2f} | '
              f'{u[1]:14.5f} {u[2]:12.4f} {u[4]:9.2f}')
    print(f"\n{'w_in':>9} | dt=0.02 原版 w_out | dt=0.02 我们 w_out | dt=0.005 原版 | dt=0.005 我们")
    for w in (300.0, -300.0, 1e4):
        o2 = make("orig", 0.0, w, 0.02)[1]
        u2 = make("ours", 0.0, w, 0.02)[1]
        o5 = make("orig", 0.0, w, 0.005)[1]
        u5 = make("ours", 0.0, w, 0.005)[1]
        print(f'{w:9.1f} | {o2:18.5f} | {u2:18.5f} | {o5:15.5f} | {u5:15.5f}')
    print(f"\n线速度钳位（w=0，vx 扫）：")
    for vx in (100.0, 200.0, 500.0, -500.0):
        o = make("orig", vx, 0.0, 0.01)
        u = make("ours", vx, 0.0, 0.01)
        print(f'  vx={vx:>7.1f} -> orig {o[0]:10.4f} | ours {u[0]:10.4f}')


if __name__ == "__main__":
    main()
