"""b2Physics 87 个导出的**合成契约探针**：不启动游戏、不用代理、不建窗。

为什么需要它：录制语料只观测到 58/87 个导出（F308）——14 个只读 getter 被代理默认过滤，
15 个（`ClearShapes`/`DestroyShape`/`DestroyWorld`/`ClearJoints`/`Pulley`/`SetGravity`/
`WakeUp`/`PutToSleep`/`SetMass`/`SetOmega`/`SetAngularDamping`/`GetMaxPolygonVertices`/
`Joint_GetBody2`/`GetJointType`/`GetReactionTorqImpulse`）从未被任何会话调用过。
本工具按固定序列建 world/body/shape/joint，**每个导出至少点一次**，两侧各跑一遍比语义值。

用法（必须 32 位 CPython：DLL 是 x86）:
  <PY32> tools/b2_contract.py <dllA> <dllB>          # 对比两侧，退出码 0 = 一致
  <PY32> tools/b2_contract.py --one <dll>            # 单侧，打印 JSON（调试）
  <PY32> tools/b2_contract.py --tolerance 1e-6 A B

判据:
  * `steps` 序列逐项相同（浮点按 `--tolerance` 相对容差，默认 1e-6；整数/字符串/指针符号必须精确）；
  * 两侧实际调用到的导出集合相同，且等于 `mapping/b2physics-exports.csv` 的 87 个；
  * 退出码 0 才表示通过；A/A（同一 DLL 两次）必须是 0 差异。

观测单位与边界:
  * 单位 = **导出调用**（每个导出至少一次）+ 调用后的语义值（返回值/出参/对象类型/状态回读）。
  * 指针一律比**符号**（world/body/shape/joint 的注册名），不比地址。
  * 只覆盖 API 层：固定序列，不含真实关卡的调用时序与依赖；与录制重放互补。
  * 物理步进后的浮点值走容差（原版与我方在 x87 上可能有 1 ULP）。

失效条件:
  * `mapping/b2physics-exports.csv` 增删导出（覆盖集合不再是 87）；
  * `src/b2physics/b2physics.h` 的宿主可见结构布局改动（本文件的 Structure 要同步）；
  * B2FFI 无关：本工具不读日志。

依据: docs/facts.md F308（29 个导出无判据）、F314（本工具的判据与结果）。
"""
import argparse
import csv
import ctypes
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import replay_ffi  # noqa: E402  只用 parse_protos（签名单一事实源）

EXPORTS_CSV = os.path.join(ROOT, "mapping", "b2physics-exports.csv")
c_float, c_int, c_ubyte, c_ushort, c_short = (
    ctypes.c_float, ctypes.c_int, ctypes.c_ubyte, ctypes.c_ushort, ctypes.c_short)
c_void_p, c_bool = ctypes.c_void_p, ctypes.c_bool


class AABB(ctypes.Structure):
    _fields_ = [("minx", c_float), ("miny", c_float),
                ("maxx", c_float), ("maxy", c_float)]


class BodyDef(ctypes.Structure):
    _fields_ = [("world", c_void_p), ("angularDamping", c_float),
                ("linearDamping", c_float), ("allowSleep", c_ubyte),
                ("fixedRotation", c_ubyte), ("isBullet", c_ubyte)]


class ShapeDef(ctypes.Structure):
    _fields_ = [("body", c_void_p), ("friction", c_float), ("restitution", c_float),
                ("density", c_float), ("sensor", c_ubyte),
                ("a", c_float), ("b", c_float), ("c", c_float), ("d", c_float)]


class PolyDef(ctypes.Structure):
    _fields_ = [("body", c_void_p), ("friction", c_float), ("restitution", c_float),
                ("density", c_float), ("userData", c_void_p),
                ("vertexCount", c_int), ("vertices", c_float * 16)]


class JointCommon(ctypes.Structure):
    _fields_ = [("world", c_void_p), ("body1", c_void_p), ("body2", c_void_p)]


class DistanceJoint(JointCommon):
    _fields_ = [("a1x", c_float), ("a1y", c_float), ("a2x", c_float), ("a2y", c_float),
                ("collide", c_ubyte)]


class RevoluteJoint(JointCommon):
    # 宿主布局（F314，逐字节探测）：anchor 12/16、collide 20、lower/upper 24/28、
    # enableLimit 32、maxMotorTorque 36、motorSpeed 40、enableMotor 44
    _fields_ = [("ax", c_float), ("ay", c_float), ("collide", c_ubyte),
                ("lower", c_float), ("upper", c_float), ("enableLimit", c_ubyte),
                ("maxMotorTorque", c_float), ("motorSpeed", c_float),
                ("enableMotor", c_ubyte)]


class PrismaticJoint(JointCommon):
    # 宿主布局（F314）：anchor 12/16、axis 20/24、collide 28、lower/upper 32/36、
    # enableLimit 40、maxMotorForce 44、motorSpeed 48、enableMotor 52
    _fields_ = [("ax", c_float), ("ay", c_float), ("axisX", c_float), ("axisY", c_float),
                ("collide", c_ubyte), ("lower", c_float), ("upper", c_float),
                ("enableLimit", c_ubyte), ("maxMotorForce", c_float),
                ("motorSpeed", c_float), ("enableMotor", c_ubyte)]


class GearJoint(JointCommon):
    _fields_ = [("joint1", c_void_p), ("joint2", c_void_p), ("ratio", c_float)]


class PulleyJoint(JointCommon):
    _fields_ = [("g1x", c_float), ("g1y", c_float), ("g2x", c_float), ("g2y", c_float),
                ("l1x", c_float), ("l1y", c_float), ("l2x", c_float), ("l2y", c_float),
                ("length1", c_float), ("length2", c_float), ("ratio", c_float),
                ("collide", c_ubyte)]


class Filter(ctypes.Structure):
    _fields_ = [("category", c_ushort), ("mask", c_ushort), ("group", c_short)]


class XForm(ctypes.Structure):
    _fields_ = [("x", c_float), ("y", c_float), ("angle", c_float)]


class MassData(ctypes.Structure):
    _fields_ = [("mass", c_float), ("cx", c_float), ("cy", c_float), ("I", c_float)]


def ctype_of(t):
    t = t.replace("const", "").strip()
    if "*" in t:
        return c_void_p
    head = t.split()[0] if t.split() else "void"
    return {"void": None, "float": c_float, "int": c_int, "int32_t": c_int,
            "bool": c_bool, "unsigned": ctypes.c_uint, "char": ctypes.c_char}.get(
                head, c_void_p)


def addr(obj):
    return ctypes.addressof(obj)


def one(dll):
    lib = ctypes.CDLL(dll)
    protos = replay_ffi.parse_protos()
    for name, (ret, params) in protos.items():
        fn = getattr(lib, name)
        fn.restype = ctype_of(ret)
        fn.argtypes = [ctype_of(t) for _, t in params]

    steps = []
    used = set()
    sym = {}

    def rec(tag, v):
        steps.append([tag, v])

    def recb(tag, v):          # 原版这些返回 bool（只写 AL），高位是垃圾（F314）
        steps.append([tag, int(v) & 0xFF])

    def F(name):
        used.add(name)
        return getattr(lib, name)

    def reg(p, name):
        if p:
            sym[p] = name
        return p

    def S(p):
        if not p:
            return "null"
        return sym.get(p, "other")

    def vec(x, y):
        return (c_float * 2)(x, y)

    def rec_vec(tag, fn, *args):
        out = (c_float * 2)()
        fn(addr(out), *args)
        rec(tag + ".x", out[0])
        rec(tag + ".y", out[1])

    def rec_xf(tag, body):
        out = XForm()
        F("b2_Body_GetXForm")(body, addr(out))
        rec(tag + ".x", out.x)
        rec(tag + ".y", out.y)
        rec(tag + ".a", out.angle)

    def rec_mass(tag, body):
        out = MassData()
        F("b2_Body_GetMass")(body, addr(out))
        rec(tag + ".m", out.mass)
        rec(tag + ".cx", out.cx)
        rec(tag + ".cy", out.cy)
        rec(tag + ".I", out.I)

    def shape_count(body):
        n = 0
        p = F("b2_Body_GetShapeList")(body)
        while p and n < 64:
            n += 1
            p = F("b2_Shape_GetNext")(p)
        return n

    # ---------------- world ----------------
    aabb = AABB(-100.0, -100.0, 100.0, 100.0)
    grav = vec(0.0, -10.0)
    world = reg(F("b2_CreateWorld")(addr(aabb), addr(grav)), "world")
    rec("world", S(world))
    rec("maxpoly", F("b2_GetMaxPolygonVertices")())

    # ---------------- body A ----------------
    d = BodyDef()
    d.world = world
    d.angularDamping = 0.3
    d.linearDamping = 0.1
    d.allowSleep = 1
    d.fixedRotation = 0
    d.isBullet = 0
    A = reg(F("b2_World_CreateBody")(addr(d)), "bodyA")
    rec("A", S(A))
    rec("A.world_is", S(F("b2_Body_GetWorld")(A)))
    xf = XForm(0.0, 5.0, 0.0)
    F("b2_Body_SetXForm")(A, addr(xf))
    rec_xf("A.xf0", A)
    rec_vec("A.pos0", F("b2_Body_GetPosition"), A)
    rec_vec("A.vel0", F("b2_Body_GetVelocity"), A)
    rec("A.angle0", F("b2_Body_GetAngle")(A))
    rec("A.omega0", F("b2_Body_GetOmega")(A))
    rec("A.damping0", F("b2_Body_GetAngularDamping")(A))
    recb("A.bullet0", F("b2_Body_IsBullet")(A))
    recb("A.frozen0", F("b2_Body_IsFrozen")(A))
    recb("A.sleeping0", F("b2_Body_GetIsSleeping")(A))
    rec("A.userdata0", int(F("b2_Body_GetUserData")(A) or 0))
    F("b2_Body_SetUserData")(A, 0x1234)
    rec("A.userdata1", int(F("b2_Body_GetUserData")(A) or 0))
    rec_vec("A.localpoint", F("b2_Body_GetLocalPoint"), A, addr(vec(1.0, 0.0)))
    rec_vec("A.worldpoint", F("b2_Body_GetWorldPoint"), A, addr(vec(0.0, 1.0)))
    rec_vec("A.localvec", F("b2_Body_GetLocalVector"), A, addr(vec(1.0, 0.0)))
    rec_vec("A.worldvec", F("b2_Body_GetWorldVector"), A, addr(vec(0.0, 1.0)))

    # ---------------- shapes on A ----------------
    sd = ShapeDef()
    sd.body = A
    sd.friction = 0.4
    sd.restitution = 0.1
    sd.density = 1.0
    sd.sensor = 0
    sd.a, sd.b, sd.c = 0.0, 0.0, 0.5
    s1 = reg(F("b2_Body_CreateShape_Circle")(addr(sd)), "shape1")
    sd2 = ShapeDef()
    sd2.body = A
    sd2.friction = 0.5
    sd2.restitution = 0.2
    sd2.density = 2.0
    sd2.a, sd2.b, sd2.c, sd2.d = 0.0, 1.0, 0.4, 0.4
    s2 = reg(F("b2_Body_CreateShape_Box")(addr(sd2)), "shape2")
    poly = PolyDef()
    poly.body = A
    poly.friction = 0.3
    poly.restitution = 0.05
    poly.density = 1.5
    poly.userData = None
    poly.vertexCount = 4
    for i, (vx, vy) in enumerate(((-0.3, -1.3), (0.3, -1.3), (0.3, -0.7), (-0.3, -0.7))):
        poly.vertices[2 * i] = vx
        poly.vertices[2 * i + 1] = vy
    s3 = reg(F("b2_Body_CreateShape_Polygon")(addr(poly)), "shape3")
    rec("shapes", [S(s1), S(s2), S(s3)])
    rec("list.head", S(F("b2_Body_GetShapeList")(A)))
    rec("s1.next", S(F("b2_Shape_GetNext")(s1)))
    rec("s2.next", S(F("b2_Shape_GetNext")(s2)))
    rec("s3.next", S(F("b2_Shape_GetNext")(s3)))
    for tag, sh in (("s1", s1), ("s2", s2), ("s3", s3)):
        rec(tag + ".type", F("b2_Shape_GetShapeType")(sh))
        rec(tag + ".body_is", S(F("b2_Shape_GetBody")(sh)))
    rec("s1.density", F("b2_Shape_GetDensity")(s1))
    rec("s1.friction", F("b2_Shape_GetFriction")(s1))
    rec("s1.restitution", F("b2_Shape_GetRestitution")(s1))
    recb("s1.sensor", F("b2_Shape_GetSensor")(s1))
    F("b2_Shape_SetDensity")(s1, 2.5)
    F("b2_Shape_SetFriction")(s1, 0.9)
    F("b2_Shape_SetRestitution")(s1, 0.3)
    rec("s1.density2", F("b2_Shape_GetDensity")(s1))
    rec("s1.friction2", F("b2_Shape_GetFriction")(s1))
    rec("s1.restitution2", F("b2_Shape_GetRestitution")(s1))
    recb("s1.sensor1", F("b2_Shape_SetSensor")(s1, 1))
    recb("s1.sensor2", F("b2_Shape_GetSensor")(s1))
    F("b2_Shape_SetSensor")(s1, 0)
    filt = Filter(1, 3, -1)
    F("b2_Shape_SetFilter")(s1, addr(filt))
    out_f = Filter()
    F("b2_Shape_GetFilter")(addr(out_f), s1)   # 原版是 out-first（F314）
    rec("s1.filter", [out_f.category, out_f.mask, out_f.group])
    F("b2_World_ReFilter")(s1)
    rec_vec("s1.circlepos", F("b2_Shape_GetCirclePos"), s1)
    rec("s1.radius", F("b2_Shape_GetCircleRadius")(s1))
    xf0 = XForm(0.0, 5.0, 0.0)
    rec("s1.test_in", F("b2_Shape_TestPoint")(s1, addr(xf0), addr(vec(0.0, 5.0))))
    rec("s1.test_out", F("b2_Shape_TestPoint")(s1, addr(xf0), addr(vec(3.0, 3.0))))

    # ---------------- bodies B/C/D ----------------
    db = BodyDef()
    db.world = world
    db.allowSleep = 1
    B = reg(F("b2_World_CreateBody")(addr(db)), "bodyB")
    F("b2_Body_SetXForm")(B, addr(XForm(0.0, 2.0, 0.0)))
    sb = ShapeDef()
    sb.body = B
    sb.friction, sb.restitution, sb.density = 0.5, 0.1, 1.0
    sb.a, sb.b, sb.c, sb.d = 0.0, 0.0, 0.5, 0.5
    reg(F("b2_Body_CreateShape_Box")(addr(sb)), "shapeB")
    F("b2_Body_SetMassFromShapes")(B)
    rec_mass("B.mass", B)

    dc = BodyDef()
    dc.world = world
    dc.allowSleep = 1
    C = reg(F("b2_World_CreateBody")(addr(dc)), "bodyC")
    F("b2_Body_SetXForm")(C, addr(XForm(5.0, 5.0, 0.0)))
    sc = ShapeDef()
    sc.body = C
    sc.density = 1.0
    sc.a, sc.b, sc.c = 0.0, 0.0, 0.3
    c1 = reg(F("b2_Body_CreateShape_Circle")(addr(sc)), "shapeC1")
    F("b2_Body_SetMassFromShapes")(C)
    rec_mass("C.mass", C)
    rec("C.shapes", shape_count(C))

    dd = BodyDef()
    dd.world = world
    dd.allowSleep = 1
    D = reg(F("b2_World_CreateBody")(addr(dd)), "bodyD")
    F("b2_Body_SetXForm")(D, addr(XForm(0.0, 5.0, 0.0)))
    sd3 = ShapeDef()
    sd3.body = D
    sd3.density = 1.0
    sd3.a, sd3.b, sd3.c, sd3.d = 0.0, 0.0, 1.0, 1.0
    reg(F("b2_Body_CreateShape_Box")(addr(sd3)), "shapeD")
    md0 = MassData(0.0, 0.0, 0.0, 0.0)
    F("b2_Body_SetMass")(D, addr(md0))
    rec_mass("D.mass", D)

    # ---------------- joints ----------------
    jd = DistanceJoint()
    jd.world, jd.body1, jd.body2 = world, A, B
    jd.a1x, jd.a1y, jd.a2x, jd.a2y = 0.0, 5.0, 0.0, 2.0
    jd.collide = 0
    jdist = reg(F("b2_World_Joint_Distance")(addr(jd)), "jointDist")

    jr = RevoluteJoint()
    jr.world, jr.body1, jr.body2 = world, A, B
    jr.ax, jr.ay = 0.0, 3.5
    jr.enableLimit, jr.lower, jr.upper = 1, -0.5, 0.5
    jr.enableMotor, jr.motorSpeed, jr.maxMotorTorque = 1, 2.0, 10.0
    jr.collide = 0
    jrev = reg(F("b2_World_Joint_Revolute")(addr(jr)), "jointRev")

    jp = PrismaticJoint()
    jp.world, jp.body1, jp.body2 = world, A, B
    jp.ax, jp.ay, jp.axisX, jp.axisY = 0.0, 3.5, 1.0, 0.0
    jp.enableLimit, jp.lower, jp.upper = 1, -1.0, 1.0
    jp.enableMotor, jp.motorSpeed, jp.maxMotorForce = 1, 1.0, 5.0
    jp.collide = 0
    jpris = reg(F("b2_World_Joint_Prismatic")(addr(jp)), "jointPrism")

    jg = GearJoint()
    jg.world, jg.body1, jg.body2 = world, A, B
    jg.joint1, jg.joint2, jg.ratio = jrev, jpris, 2.0
    jgear = reg(F("b2_World_Joint_Gear")(addr(jg)), "jointGear")

    jl = PulleyJoint()
    jl.world, jl.body1, jl.body2 = world, A, B
    jl.g1x, jl.g1y, jl.g2x, jl.g2y = -1.0, 4.0, 1.0, 4.0
    jl.l1x, jl.l1y, jl.l2x, jl.l2y = 0.0, 0.0, 0.0, 0.0
    jl.length1, jl.length2, jl.ratio, jl.collide = 3.0, 3.0, 1.0, 0
    jpul = reg(F("b2_World_Joint_Pulley")(addr(jl)), "jointPulley")

    for tag, j in (("dist", jdist), ("rev", jrev), ("pris", jpris),
                   ("gear", jgear), ("pul", jpul)):
        rec(tag + ".type", F("b2_Joint_GetJointType")(j))
        rec(tag + ".b1", S(F("b2_Joint_GetBody1")(j)))
        rec(tag + ".b2", S(F("b2_Joint_GetBody2")(j)))
    rec_vec("rev.anchor1", F("b2_Joint_GetAnchor1"), jrev)
    rec_vec("rev.anchor2", F("b2_Joint_GetAnchor2"), jrev)
    lo, hi = c_float(), c_float()
    F("b2_Joint_GetLimits")(jrev, addr(lo), addr(hi))
    rec("rev.limits", [lo.value, hi.value])
    recb("rev.limit_on", F("b2_Joint_IsLimitEnabled")(jrev))
    recb("rev.motor_on", F("b2_Joint_IsMotorEnabled")(jrev))
    rec("rev.motor_speed", F("b2_Joint_GetMotorSpeed")(jrev))
    rec("rev.angle", F("b2_Joint_GetJointAngle")(jrev))
    rec("pris.translation", F("b2_Joint_GetJointTranslation")(jpris))
    F("b2_Joint_SetLimits")(jrev, -0.2, 0.2)
    F("b2_Joint_GetLimits")(jrev, addr(lo), addr(hi))
    rec("rev.limits2", [lo.value, hi.value])
    F("b2_Joint_EnableLimit")(jrev, 0)
    recb("rev.limit_on2", F("b2_Joint_IsLimitEnabled")(jrev))
    F("b2_Joint_EnableLimit")(jrev, 1)
    F("b2_Joint_EnableMotor")(jpris, 0)
    recb("pris.motor_on2", F("b2_Joint_IsMotorEnabled")(jpris))
    F("b2_Joint_EnableMotor")(jpris, 1)
    F("b2_Joint_SetMotorSpeed")(jpris, 1.5)
    rec("pris.motor_speed2", F("b2_Joint_GetMotorSpeed")(jpris))
    F("b2_Joint_SetMaxMotorTorque")(jrev, 5.0)
    F("b2_Joint_SetMaxMotorForce")(jpris, 5.0)
    rec_vec("rev.impulse0", F("b2_Joint_GetReactionImpulse"), jrev)
    rec("rev.torq0", F("b2_Joint_GetReactionTorqImpulse")(jrev))

    # ---------------- world 2：稳定场景的步进 / 回调 / 反作用力 ----------------
    # world1 把 5 个关节叠在同一对 body 上，是病态约束（原版会出 NaN）；这里另起干净场景：
    # 动态圆 + 静态箱 + 一个 revolute，接触与反作用力都可观测（F314）。
    w2 = reg(F("b2_CreateWorld")(addr(aabb), addr(grav)), "world2")
    dp = BodyDef()
    dp.world = w2
    dp.allowSleep = 1
    P = reg(F("b2_World_CreateBody")(addr(dp)), "bodyP")
    F("b2_Body_SetXForm")(P, addr(XForm(0.0, 5.0, 0.0)))
    sp = ShapeDef()
    sp.body = P
    sp.density = 1.0
    sp.a, sp.b, sp.c = 0.0, 0.0, 0.5
    reg(F("b2_Body_CreateShape_Circle")(addr(sp)), "shapeP")
    F("b2_Body_SetMassFromShapes")(P)
    ds = BodyDef()
    ds.world = w2
    ds.allowSleep = 0
    S = reg(F("b2_World_CreateBody")(addr(ds)), "bodyS")
    F("b2_Body_SetXForm")(S, addr(XForm(0.0, 4.2, 0.0)))
    ss = ShapeDef()
    ss.body = S
    ss.density = 1.0
    ss.a, ss.b, ss.c, ss.d = 0.0, 0.0, 1.0, 0.5
    reg(F("b2_Body_CreateShape_Box")(addr(ss)), "shapeS")
    md_s = MassData(0.0, 0.0, 0.0, 0.0)
    F("b2_Body_SetMass")(S, addr(md_s))
    jr2 = RevoluteJoint()
    jr2.world, jr2.body1, jr2.body2 = w2, P, S
    jr2.ax, jr2.ay = 0.0, 4.2
    jr2.collide = 0
    jr2.enableLimit, jr2.lower, jr2.upper = 0, 0.0, 0.0
    jr2.maxMotorTorque, jr2.motorSpeed, jr2.enableMotor = 0.0, 0.0, 0
    rev2 = reg(F("b2_World_Joint_Revolute")(addr(jr2)), "jointRev2")

    got = [0]
    cb = ctypes.CFUNCTYPE(None, c_void_p)(lambda p: got.__setitem__(0, got[0] + 1))
    fcnt = [0]

    def on_filter(rec4):
        fcnt[0] += 1
        return True
    fcb = ctypes.CFUNCTYPE(c_bool, c_void_p)(on_filter)
    F("b2_World_SetContactListenerCallBack")(w2, ctypes.cast(cb, c_void_p))
    F("b2_World_SetContactFilterCallBack")(w2, ctypes.cast(fcb, c_void_p))
    F("b2_World_SetGravity")(w2, addr(vec(0.0, -10.0)))
    for _ in range(3):
        F("b2_World_Step")(w2, 1.0 / 60.0, 10, 10)
    rec("contact.calls", got[0] > 0)
    rec("filter.calls", fcnt[0] > 0)
    rec_xf("P.xf1", P)
    rec_vec("P.pos1", F("b2_Body_GetPosition"), P)
    rec_vec("P.vel1", F("b2_Body_GetVelocity"), P)
    rec("P.angle1", F("b2_Body_GetAngle")(P))
    rec("P.omega1", F("b2_Body_GetOmega")(P))
    rec_vec("rev2.impulse1", F("b2_Joint_GetReactionImpulse"), rev2)
    rec("rev2.torq1", F("b2_Joint_GetReactionTorqImpulse")(rev2))
    F("b2_DestroyWorld")(w2)

    # ---------------- setters / sleep ----------------
    F("b2_Body_PutToSleep")(A)
    recb("A.sleeping1", F("b2_Body_GetIsSleeping")(A))
    F("b2_Body_WakeUp")(A)
    recb("A.sleeping2", F("b2_Body_GetIsSleeping")(A))
    F("b2_Body_SetOmega")(A, 3.0)
    rec("A.omega2", F("b2_Body_GetOmega")(A))
    F("b2_Body_SetAngularDamping")(A, 0.7)
    rec("A.damping1", F("b2_Body_GetAngularDamping")(A))
    F("b2_Body_SetBullet")(A, 1)
    recb("A.bullet1", F("b2_Body_IsBullet")(A))
    F("b2_Body_SetBullet")(A, 0)
    F("b2_Body_SetVelocity")(A, addr(vec(1.0, 2.0)))
    rec_vec("A.vel2", F("b2_Body_GetVelocity"), A)
    md = MassData(2.0, 0.0, 0.0, 1.0)
    F("b2_Body_SetMass")(C, addr(md))
    rec_mass("C.mass2", C)
    F("b2_Body_SetMassFromShapes")(C)
    rec_mass("C.mass3", C)
    F("b2_Body_ApplyForce")(A, addr(vec(10.0, 0.0)), addr(vec(0.0, 5.0)))
    F("b2_Body_ApplyTorque")(A, 5.0)
    F("b2_Body_ApplyImpulse")(A, addr(vec(0.0, 1.0)), addr(vec(0.0, 5.0)))
    rec_vec("A.vel3", F("b2_Body_GetVelocity"), A)

    # ---------------- destruction ----------------
    rec("C.shapes1", shape_count(C))
    F("b2_Body_DestroyShape")(C, c1)   # 原版是 (body, shape)（F314）
    rec("C.shapes2", shape_count(C))
    s4 = reg(F("b2_Body_CreateShape_Circle")(addr(sc)), "shapeC2")
    s5 = reg(F("b2_Body_CreateShape_Circle")(addr(sc)), "shapeC3")
    rec("C.shapes3", shape_count(C))
    F("b2_Body_ClearShapes")(C)
    rec("C.shapes4", shape_count(C))
    F("b2_World_DestroyJoint")(world, jdist)
    F("b2_World_ClearJoints")(world)
    F("b2_World_DestroyBody")(world, C)
    F("b2_World_DestroyBody")(world, D)
    F("b2_DestroyWorld")(world)
    rec("done", 1)
    rec("coverage", len(used))
    return {"dll": dll, "steps": steps, "used": sorted(used)}


def load_export_names():
    with open(EXPORTS_CSV, encoding="utf-8") as fh:
        # CSV 含 DllEntryPoint（DLL 入口，不是 b2_* API），覆盖判据只算 b2_* 导出
        return sorted(r["name"] for r in csv.DictReader(fh) if r["name"].startswith("b2_"))


def same(a, b, tol):
    if isinstance(a, float) and isinstance(b, float):
        if a == b:
            return True, 0.0
        if a != a and b != b:      # 都是 NaN
            return True, 0.0
        d = abs(a - b) / max(1.0, abs(a), abs(b))
        return d <= tol, d
    return a == b, 0.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dlls", nargs="*")
    ap.add_argument("--one", default="")
    ap.add_argument("--tolerance", type=float, default=1e-6)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    if a.one:
        print(json.dumps(one(a.one), ensure_ascii=False))
        return 0
    if len(a.dlls) != 2:
        print("用法: b2_contract.py <dllA> <dllB> | --one <dll>")
        return 2

    outs = []
    for dll in a.dlls:
        r = subprocess.run([sys.executable, os.path.abspath(__file__), "--one", dll],
                           capture_output=True, text=True)
        if r.returncode != 0 or not r.stdout.strip():
            print("side failed:", dll)
            print((r.stdout or r.stderr)[-800:])
            return 2
        outs.append(json.loads(r.stdout))

    A, B = outs
    names = load_export_names()
    diffs, maxdev, exact_floats = [], 0.0, 0
    for i, (sa, sb) in enumerate(zip(A["steps"], B["steps"])):
        if sa[0] != sb[0]:
            diffs.append((i, sa, sb, "tag"))
            continue
        ok, dev = same(sa[1], sb[1], a.tolerance)
        if not ok:
            diffs.append((i, sa, sb, "value"))
        elif dev:
            exact_floats += 1
            maxdev = max(maxdev, dev)
    if len(A["steps"]) != len(B["steps"]):
        diffs.append((-1, len(A["steps"]), len(B["steps"]), "length"))

    used_a, used_b = set(A["used"]), set(B["used"])
    missing = sorted(set(names) - used_a)
    extra = sorted(used_a - set(names))
    used_diff = sorted(used_a ^ used_b)

    print("steps=%d/%d exported=%d/%d diffs=%d tol_diffs=%d maxdev=%.2g"
          % (len(A["steps"]), len(B["steps"]), len(used_a), len(names),
             len(diffs), exact_floats, maxdev))
    if used_diff:
        print("used set differs:", used_diff[:6])
    if missing:
        print("未被本探针调用到的导出:", missing)
    if extra:
        print("csv 里没有的导出:", extra)
    for i, sa, sb, why in diffs[:12]:
        print("  #%s %s: A=%r B=%r (%s)" % (i, sa[0] if sa else "?", sa, sb, why))

    ok = (not diffs and not used_diff and not missing and not extra
          and len(A["steps"]) == len(B["steps"]))
    if a.json:
        print(json.dumps({"ok": ok, "diffs": len(diffs), "maxdev": maxdev,
                          "steps": len(A["steps"]), "exported": len(used_a),
                          "missing": missing, "used_diff": used_diff},
                         ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
