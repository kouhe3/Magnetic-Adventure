"""直接调两个 DLL 的 `b2TimeOfImpact`（cdecl，参数在栈上），喂同一组 shape + sweep，比返回值。

为什么可行：`b2TimeOfImpact` 在原版是栈传参（反汇编 `mov eax,[esp+arg_0]`），与我们构建一样是
cdecl；而 `b2Distance` 才是自定义寄存器约定（F112）。所以 TOI 这一层可以直接对调。

sweep 布局（b2Sweep）：localCenter(0..7) c0(8..15) c(16..23) a0(24..27) a(28..31) t0(32..35)

输入：work/geo_ours.txt 的第 419 步（= 419 步 TOI 调用时 c0 与 c 的实际取值）。
用法（32 位 Python）： python tools/toi_call.py
"""
import ast
import ctypes
import os
import struct

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILES = {"orig": os.path.join(ROOT, "bin", "gametop", "b2Physics.dll"),
         "ours": os.path.join(ROOT, "build", "Release", "b2Physics.dll")}
RVA_TOI = {"orig": 0x18B20, "ours": 0x0E930}
DUMP = os.path.join(ROOT, "work", "geo_ours.txt")
SHA, SHB = 0x2efd26b4, 0x2efd61f4
STEP = 419


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


class Sweep(ctypes.Structure):
    _fields_ = [("lcx", ctypes.c_float), ("lcy", ctypes.c_float),
                ("c0x", ctypes.c_float), ("c0y", ctypes.c_float),
                ("cx", ctypes.c_float), ("cy", ctypes.c_float),
                ("a0", ctypes.c_float), ("a", ctypes.c_float), ("t0", ctypes.c_float)]


def load(step):
    steps = {}
    cur = None
    for line in open(DUMP, encoding="utf-8"):
        if line.startswith("step "):
            cur = int(line.split()[1]); steps[cur] = {"s": {}, "b": {}}
        elif line.startswith("  s "):
            sp, bp, blob = line[4:].rstrip("\n").split(" ", 2)
            steps[cur]["s"][int(sp)] = (int(bp), ast.literal_eval(blob))
        elif line.startswith("  b "):
            bp, blob = line[4:].rstrip("\n").split(" ", 1)
            steps[cur]["b"][int(bp)] = ast.literal_eval(blob)
    return steps[step]


def main():
    d = load(STEP)
    f32 = lambda bl, k: struct.unpack_from("<f", bl, k)[0]
    i32 = lambda bl, k: struct.unpack_from("<i", bl, k)[0]
    specs = []
    for sp in (SHA, SHB):
        bp, bl = d["s"][sp]
        n = i32(bl, 280)
        outer = [(f32(bl, 88 + 8 * i), f32(bl, 92 + 8 * i)) for i in range(n)]
        body = d["b"][bp]
        sweep = Sweep(*[f32(body, k) for k in (32, 36, 40, 44, 48, 52, 56, 60, 64)])
        specs.append({"shape": sp, "hw": max(abs(x) for x, _ in outer), "hh": max(abs(y) for _, y in outer),
                      "sweep": sweep})
        print(f"shape {sp:#x}: hw/hh={specs[-1]['hw']:.4f}/{specs[-1]['hh']:.4f} "
              f"sweep c0=({sweep.c0x:.6f},{sweep.c0y:.6f}) c=({sweep.cx:.6f},{sweep.cy:.6f}) "
              f"a0={sweep.a0:.6f} a={sweep.a:.6f} t0={sweep.t0:.6f} lc=({sweep.lcx:.6f},{sweep.lcy:.6f})")

    for which in ("orig", "ours"):
        lib = ctypes.CDLL(FILES[which])
        lib.b2_CreateWorld.restype = ctypes.c_void_p
        lib.b2_CreateWorld.argtypes = [ctypes.POINTER(AABB), ctypes.POINTER(Vec2)]
        lib.b2_World_CreateBody.restype = ctypes.c_void_p
        lib.b2_World_CreateBody.argtypes = [ctypes.POINTER(BodyDef)]
        lib.b2_Body_CreateShape_Box.restype = ctypes.c_void_p
        lib.b2_Body_CreateShape_Box.argtypes = [ctypes.POINTER(BoxDef)]
        box = AABB(Vec2(-100.0, -100.0), Vec2(100.0, 100.0))
        g = Vec2(0.0, 0.0)
        w = lib.b2_CreateWorld(ctypes.byref(box), ctypes.byref(g))
        shapes = []
        for sp in specs:
            bd = BodyDef(w, 0.0, 0.0, 1, 0, 0)
            b = lib.b2_World_CreateBody(ctypes.byref(bd))
            sd = BoxDef(b, 0.3, 0.0, 1.0, 0, 0.0, 0.0, sp["hw"], sp["hh"])
            shapes.append(lib.b2_Body_CreateShape_Box(ctypes.byref(sd)))
        toi = ctypes.CFUNCTYPE(ctypes.c_float, ctypes.c_void_p, ctypes.POINTER(Sweep),
                               ctypes.c_void_p, ctypes.POINTER(Sweep))(lib._handle + RVA_TOI[which])
        v = toi(shapes[0], ctypes.byref(specs[0]["sweep"]),
                shapes[1], ctypes.byref(specs[1]["sweep"]))
        print(f"{which}: b2TimeOfImpact = {v!r}")


if __name__ == "__main__":
    main()
