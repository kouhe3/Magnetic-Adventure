"""调用 DLL 内部未导出函数（按 RVA 定位），把同一组形状+位形喂给两个 DLL 比返回值。

用途：ctypes 调 DLL 内部未导出函数（按 base+RVA），输入完全可控。

**限制（F112）**：原版 `b2Distance`（RVA 0xA040）是 MSVC 给内部链接函数的**自定义寄存器约定**
（`__usercall`，参数在 eax/edx/esi/edi + 两个栈参数），用这里的 cdecl 调用拿到的是垃圾
（恒定 0、近点恒为 0,0）。目前它只对**我们的构建**（`ours`，外部链接 cdecl）有效；
要比原版，请走端到端的 `tools/toi_scan.py`（读 `m_toi`，不需要调用约定）。

用法（必须 32 位 Python）：
  python tools/dist_probe.py <dll> orig|ours <16 个 float：hwA hhA posAx posAy c1x c1y c2x c2y 同 B>

依据：docs/facts.md F111。RVA 来源：IDA（原版）/ build/Release/b2Physics.map（我们的构建）。
"""
import ctypes
import os
import struct
import sys

RVA_EXPORT_SENTINEL = 0x14F0      # b2_Shape_GetShapeType 的 RVA（mapping/b2physics-exports.csv）
RVA_B2DISTANCE = {"orig": 0x0A040, "ours": 0x13DD0}

class Vec2(ctypes.Structure):
    _fields_ = [("x", ctypes.c_float), ("y", ctypes.c_float)]

class AABB(ctypes.Structure):
    _fields_ = [("lo", Vec2), ("hi", Vec2)]

class BoxDef(ctypes.Structure):
    """宿主实测的 shape def（F32）：body, friction, restitution, density, sensor, center, half"""
    _fields_ = [("body", ctypes.c_void_p), ("friction", ctypes.c_float),
                ("restitution", ctypes.c_float), ("density", ctypes.c_float),
                ("sensor", ctypes.c_ubyte), ("cx", ctypes.c_float), ("cy", ctypes.c_float),
                ("hw", ctypes.c_float), ("hh", ctypes.c_float)]

def load(dll):
    lib = ctypes.CDLL(os.path.abspath(dll))
    # HMODULE 就是加载基址（两个 DLL 的导出 RVA 布局不同，不能用固定 sentinel 反推）
    base = lib._handle
    fn = ctypes.cast(getattr(lib, "b2_Shape_GetShapeType"), ctypes.c_void_p).value
    assert base <= fn < base + 0x100000, (hex(base), hex(fn))
    return lib, base

def main():
    dll, which = sys.argv[1], sys.argv[2]
    vals = [float(x) for x in sys.argv[3:]]
    hwA, hhA, pAx, pAy, a1x, a1y, a2x, a2y = vals[0:8]
    hwB, hhB, pBx, pBy, b1x, b1y, b2x, b2y = vals[8:16]

    lib, base = load(dll)
    print(f"dll={dll}\nbase={base:#x} b2Distance={base + RVA_B2DISTANCE[which]:#x}")

    cw = lib.b2_CreateWorld
    cw.restype = ctypes.c_void_p
    cw.argtypes = [ctypes.POINTER(AABB), ctypes.POINTER(Vec2)]
    box = AABB(Vec2(-100.0, -100.0), Vec2(100.0, 100.0))
    grav = Vec2(0.0, 0.0)
    world = cw(ctypes.byref(box), ctypes.byref(grav))

    class BodyDef(ctypes.Structure):
        _fields_ = [("world", ctypes.c_void_p), ("f4", ctypes.c_float), ("f8", ctypes.c_float),
                    ("b12", ctypes.c_ubyte), ("b13", ctypes.c_ubyte), ("b14", ctypes.c_ubyte)]

    cb = lib.b2_World_CreateBody
    cb.restype = ctypes.c_void_p
    cb.argtypes = [ctypes.POINTER(BodyDef)]
    cs = lib.b2_Body_CreateShape_Box
    cs.restype = ctypes.c_void_p
    cs.argtypes = [ctypes.POINTER(BoxDef)]

    shapes = []
    for hw, hh in ((hwA, hhA), (hwB, hhB)):
        bd = BodyDef(world, 0.0, 0.0, 1, 0, 0)      # b12=1 → dynamic（probe_b2physics 的 slot 5）
        body = cb(ctypes.byref(bd))
        sd = BoxDef(body, 0.3, 0.0, 1.0, 0, 0.0, 0.0, hw, hh)
        shapes.append(cs(ctypes.byref(sd)))
    print("shapes", [hex(s) for s in shapes])

    class XForm(ctypes.Structure):
        _fields_ = [("px", ctypes.c_float), ("py", ctypes.c_float),
                    ("c1x", ctypes.c_float), ("c1y", ctypes.c_float),
                    ("c2x", ctypes.c_float), ("c2y", ctypes.c_float)]

    xfA = XForm(pAx, pAy, a1x, a1y, a2x, a2y)
    xfB = XForm(pBx, pBy, b1x, b1y, b2x, b2y)

    dist = ctypes.CFUNCTYPE(ctypes.c_float, ctypes.POINTER(Vec2), ctypes.POINTER(Vec2),
                            ctypes.c_void_p, ctypes.POINTER(XForm),
                            ctypes.c_void_p, ctypes.POINTER(XForm))(base + RVA_B2DISTANCE[which])
    p1, p2 = Vec2(), Vec2()
    d = dist(ctypes.byref(p1), ctypes.byref(p2), shapes[0], ctypes.byref(xfA),
             shapes[1], ctypes.byref(xfB))
    print(f"b2Distance = {d!r}")
    print(f"  p1=({p1.x:.9g},{p1.y:.9g}) p2=({p2.x:.9g},{p2.y:.9g})")

if __name__ == "__main__":
    main()
