"""端到端 TOI 观测：受控 2-body world（A 静止、B 动态、可设速度），step 后读 contact 的 m_toi。

为什么不用内部调用：原版 b2Distance 是自定义寄存器约定（F112），ctypes 的 cdecl 调用拿到垃圾；
而 m_toi 只是内存里一个 float（b2Contact+60），读它不需要任何调用约定。

流程（每个 dy 一个独立 world）：
  1. 建 world（重力 0，AABB ±100）
  2. A/B 两盒先重叠放置 → step 一次（让 broadphase 建出 pair/contact）
  3. SetXForm 把 B 挪到目标位姿（sweep 的 c0=c=新位姿）→ 再 step 一次
  4. 读 world->m_contactList，打印每个 contact 的 m_flags / m_manifoldCount / m_toi

用法（32 位 Python）： python tools/toi_scan.py
依据：docs/facts.md F113（用于判定"相同输入下两版 TOI 是否一致"）。
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

class XForm(ctypes.Structure):
    _fields_ = [("x", ctypes.c_float), ("y", ctypes.c_float), ("angle", ctypes.c_float)]

class Dll:
    def __init__(self, which):
        self.lib = ctypes.CDLL(FILES[which])
        self.lib.b2_CreateWorld.restype = ctypes.c_void_p
        self.lib.b2_CreateWorld.argtypes = [ctypes.POINTER(AABB), ctypes.POINTER(Vec2)]
        self.lib.b2_World_CreateBody.restype = ctypes.c_void_p
        self.lib.b2_World_CreateBody.argtypes = [ctypes.POINTER(BodyDef)]
        self.lib.b2_Body_CreateShape_Box.restype = ctypes.c_void_p
        self.lib.b2_Body_CreateShape_Box.argtypes = [ctypes.POINTER(BoxDef)]
        self.lib.b2_Body_SetMassFromShapes.argtypes = [ctypes.c_void_p]
        self.lib.b2_Body_SetXForm.argtypes = [ctypes.c_void_p, ctypes.POINTER(XForm)]
        self.lib.b2_World_Step.argtypes = [ctypes.c_void_p, ctypes.c_float, ctypes.c_int, ctypes.c_int]
        self.lib.b2_Body_GetMass.restype = ctypes.c_float
        self.lib.b2_Body_GetMass.argtypes = [ctypes.c_void_p]
        self.lib.b2_Body_SetVelocity.argtypes = [ctypes.c_void_p, ctypes.POINTER(Vec2)]

    def set_velocity(self, body, vx, vy, w):
        self.lib.b2_Body_SetVelocity(body, ctypes.byref(Vec2(vx, vy)))
        ctypes.c_float.from_address(body + 76).value = w

    def world(self):
        box = AABB(Vec2(-100.0, -100.0), Vec2(100.0, 100.0))
        g = Vec2(0.0, 0.0)
        return self.lib.b2_CreateWorld(ctypes.byref(box), ctypes.byref(g))

    def body(self, world, hw, hh, dynamic):
        bd = BodyDef(world, 0.0, 0.0, 1, 0, 0)
        b = self.lib.b2_World_CreateBody(ctypes.byref(bd))
        sd = BoxDef(b, 0.3, 0.0, 1.0, 0, 0.0, 0.0, hw, hh)
        self.lib.b2_Body_CreateShape_Box(ctypes.byref(sd))
        if dynamic:
            self.lib.b2_Body_SetMassFromShapes(b)
        return b

def contacts(world):
    u32 = ctypes.c_uint32.from_address
    i32 = ctypes.c_int32.from_address
    f32 = ctypes.c_float.from_address
    out = []
    c = u32(world + 102984).value
    n = 0
    while c and n < 256:
        out.append({"s1": u32(c + 52).value, "s2": u32(c + 56).value,
                    "flags": u32(c + 4).value, "mcount": i32(c + 8).value,
                    "toi": f32(c + 60).value})
        c = u32(c + 16).value
        n += 1
    return out

HWA, HHA = 0.687, 3.00
HWB, HHB = 0.77, 0.20
PA = (-1.0499999523162842, 11.40999984741211, 0.0)
PB0 = (-0.9346526861190796, 14.89958381652832)
ANG = 0.5811947          # atan2(c2x, c1x) ≈ 33.3°，与记录到的 R 对应

def one_step_scan(which, dy):
    d = Dll(which)
    w = d.world()
    A = d.body(w, HWA, HHA, dynamic=False)
    B = d.body(w, HWB, HHB, dynamic=True)
    d.lib.b2_Body_SetXForm(A, ctypes.byref(XForm(*PA)))
    # 先重叠（B 下移 0.2）建出 contact
    d.lib.b2_Body_SetXForm(B, ctypes.byref(XForm(PB0[0], PB0[1] - 0.2, ANG)))
    d.lib.b2_World_Step(w, 0.01, 10, 8)
    first = contacts(w)
    # 再挪到目标位姿
    d.lib.b2_Body_SetXForm(B, ctypes.byref(XForm(PB0[0], PB0[1] + dy, ANG)))
    d.set_velocity(B, 0.0239055, 0.0326929, -0.0472059)   # 记录到的速度（F107）
    d.lib.b2_World_Step(w, 0.01, 10, 8)
    second = contacts(w)
    return first, second

def main():
    print(f'{"dy":>7} | {"orig: n mcount toi":>34} | {"ours: n mcount toi":>34}')
    for i in range(0, 46):
        dy = 0.0064 + i * 0.0001
        row = {}
        for k in ("orig", "ours"):
            first, second = one_step_scan(k, dy)
            row[k] = (len(second), [c["mcount"] for c in second], [round(c["toi"], 6) for c in second])
        print(f'{dy:7.3f} | {str(row["orig"]):>34} | {str(row["ours"]):>34}')

if __name__ == "__main__":
    main()
