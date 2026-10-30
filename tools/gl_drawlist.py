"""把 `GLFFI02` 日志里的一帧还原成「绘制列表」（sprite 级），供渲染器对拍。

做法：单遍模拟 OpenGL 状态机 —— 矩阵栈（modelview/projection）、`glBindTexture`、
当前颜色、`glBegin..glEnd` 里的顶点/纹理坐标，最后把顶点乘上**绘制时的 modelview**
得到世界坐标。不做深度/混合/光照模拟（那是渲染器的事），只还原「画了什么、在哪」。

用法:
  python tools/gl_drawlist.py <log> --frame K [--limit 40] [--json out.json]
  python tools/gl_drawlist.py <log> --frame K --summary        # 只出统计

输出字段：prim / tex / rgba / n / v[i]=(x,y,z) / uv[i]=(u,v)（世界坐标，列主序矩阵）。

覆盖边界：
  - 只处理 `GLFFI02`（v01 没有 payload，矩阵/颜色/UV 都读不到）。
  - 立即模式（`glBegin`）之外的绘制（`glDrawArrays`/`glCallList`）不还原——
    F178 实测游戏每帧只用 25 次 `glBegin`，`glDrawArrays` 全生命周期只有 1 次。
  - `glTexCoord2f/glVertex2f/glVertex3f` 的实参在栈上（v02 的 args[12] 够），
    `*fv` 变体读 mem0。
  - 光照/材质（`glLight*`/`glMaterial*`）只记录不模拟；纹理像素只有 192 B 前缀（F179）。

依据：docs/facts.md F178（一帧 25 个 quad、100 顶点、24 次 BindTexture）、
      F179（payload 与相机）。
"""
import argparse
import json
import struct
import sys

import gl_ffi


def ident():
    return [1.0, 0.0, 0.0, 0.0,
            0.0, 1.0, 0.0, 0.0,
            0.0, 0.0, 1.0, 0.0,
            0.0, 0.0, 0.0, 1.0]


def mul(a, b):
    """列主序 4x4 相乘：c = a * b（b 先作用）。"""
    c = [0.0] * 16
    for col in range(4):
        for row in range(4):
            c[col * 4 + row] = (a[0 * 4 + row] * b[col * 4 + 0] +
                                a[1 * 4 + row] * b[col * 4 + 1] +
                                a[2 * 4 + row] * b[col * 4 + 2] +
                                a[3 * 4 + row] * b[col * 4 + 3])
    return c


def xform(m, p):
    x, y, z = p
    return (m[0] * x + m[4] * y + m[8] * z + m[12],
            m[1] * x + m[5] * y + m[9] * z + m[13],
            m[2] * x + m[6] * y + m[10] * z + m[14])


def f32(x):
    return struct.unpack("<f", struct.pack("<I", x & 0xFFFFFFFF))[0]


PRIMS = {0x0000: "POINTS", 0x0001: "LINES", 0x0003: "LINE_STRIP", 0x0004: "LINE_LOOP",
         0x0005: "TRIANGLES", 0x0006: "TRIANGLE_STRIP", 0x0007: "TRIANGLE_FAN",
         0x0008: "QUADS", 0x0009: "QUAD_STRIP", 0x000A: "POLYGON"}
MODES = {0x1700: "MODELVIEW", 0x1701: "PROJECTION", 0x1702: "TEXTURE"}


class State:
    def __init__(self):
        self.stacks = {"MODELVIEW": [ident()], "PROJECTION": [ident()], "TEXTURE": [ident()]}
        self.mode = "MODELVIEW"
        self.cur = ident()
        self.tex = None
        self.rgba = (1.0, 1.0, 1.0, 1.0)
        self.in_begin = None
        self.verts = []
        self.uv = (0.0, 0.0)
        self.draws = []
        self.skipped = 0

    def m(self):
        return self.stacks[self.mode][-1]


def vertex(st, x, y, z):
    # GL 的变换链是 P·M·v：世界坐标永远乘 MODELVIEW，与当前 glMatrixMode 无关。
    st.verts.append((xform(st.stacks["MODELVIEW"][-1], (x, y, z)), st.uv))


def flush(st):
    if not st.verts:
        return
    st.draws.append({"prim": st.in_begin, "tex": st.tex, "rgba": st.rgba,
                     "n": len(st.verts),
                     "v": [p[0] for p in st.verts], "uv": [p[1] for p in st.verts]})
    st.verts = []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("log")
    ap.add_argument("--frame", type=int, required=True)
    ap.add_argument("--limit", type=int, default=40)
    ap.add_argument("--json")
    ap.add_argument("--summary", action="store_true")
    a = ap.parse_args()

    nm = gl_ffi.names()
    s = gl_ffi.load(a.log)
    s["path"] = a.log
    if s["ver"] != b"02":
        raise SystemExit("需要 GLFFI02（当前 %s）：矩阵/颜色/UV 只在 v02 里" % s["ver"].decode())
    fb = gl_ffi.frame_bounds(s["ids"], gl_ffi.swap_ids(nm))
    if not (0 <= a.frame < len(fb)):
        raise SystemExit("frame 越界：共 %d 帧" % len(fb))
    start, end = fb[a.frame]

    with open(a.log, "rb") as fh:
        fh.seek(gl_ffi.HDR_SIZE + start * s["rec"].size)
        blob = fh.read((end - start + 1) * s["rec"].size)

    st = State()
    for r in s["rec"].iter_unpack(blob):
        name = nm.get(r[0], "")
        args = r[6:18]
        mem0 = r[18][:192]
        if name == "glMatrixMode":
            st.mode = MODES.get(args[0], st.mode)
        elif name == "glLoadIdentity":
            st.stacks[st.mode][-1] = ident()
        elif name == "glLoadMatrixf":
            st.stacks[st.mode][-1] = list(struct.unpack("<16f", mem0[:64]))
        elif name == "glMultMatrixf":
            st.stacks[st.mode][-1] = mul(st.m(), list(struct.unpack("<16f", mem0[:64])))
        elif name == "glPushMatrix":
            st.stacks[st.mode].append(list(st.m()))
        elif name == "glPopMatrix":
            if len(st.stacks[st.mode]) > 1:
                st.stacks[st.mode].pop()
        elif name == "glTranslatef":
            x, y, z = (f32(v) for v in args[:3])
            t = ident(); t[12], t[13], t[14] = x, y, z
            st.stacks[st.mode][-1] = mul(st.m(), t)
        elif name == "glTranslated":
            x, y, z = struct.unpack("<3d", struct.pack("<6I", *args[:6]))
            t = ident(); t[12], t[13], t[14] = x, y, z
            st.stacks[st.mode][-1] = mul(st.m(), t)
        elif name == "glScalef":
            x, y, z = (f32(v) for v in args[:3])
            t = ident(); t[0], t[5], t[10] = x, y, z
            st.stacks[st.mode][-1] = mul(st.m(), t)
        elif name == "glRotatef":
            ang, x, y, z = (f32(v) for v in args[:4])
            import math
            c, s1 = math.cos(math.radians(ang)), math.sin(math.radians(ang))
            n = math.sqrt(x * x + y * y + z * z) or 1.0
            x, y, z = x / n, y / n, z / n
            t = [x * x * (1 - c) + c, y * x * (1 - c) + z * s1, x * z * (1 - c) - y * s1, 0.0,
                 x * y * (1 - c) - z * s1, y * y * (1 - c) + c, y * z * (1 - c) + x * s1, 0.0,
                 x * z * (1 - c) + y * s1, y * z * (1 - c) - x * s1, z * z * (1 - c) + c, 0.0,
                 0.0, 0.0, 0.0, 1.0]
            st.stacks[st.mode][-1] = mul(st.m(), t)
        elif name == "glBindTexture":
            st.tex = args[1]
        elif name == "glColor4fv":
            st.rgba = tuple(struct.unpack("<4f", mem0[:16]))
        elif name == "glColor4f":
            st.rgba = tuple(f32(v) for v in args[:4])
        elif name == "glBegin":
            st.in_begin = PRIMS.get(args[0], hex(args[0]))
            st.verts = []
        elif name == "glEnd":
            flush(st)
            st.in_begin = None
        elif name in ("glTexCoord2f",):
            st.uv = (f32(args[0]), f32(args[1]))
        elif name in ("glTexCoord2fv",):
            u, v = struct.unpack("<2f", mem0[:8])
            st.uv = (u, v)
        elif name == "glVertex2f":
            vertex(st, f32(args[0]), f32(args[1]), 0.0)
        elif name == "glVertex3f":
            vertex(st, f32(args[0]), f32(args[1]), f32(args[2]))
        elif name in ("glVertex2fv", "glVertex3fv"):
            if name == "glVertex2fv":
                x, y = struct.unpack("<2f", mem0[:8]); vertex(st, x, y, 0.0)
            else:
                x, y, z = struct.unpack("<3f", mem0[:12]); vertex(st, x, y, z)

    if a.json:
        with open(a.json, "w", encoding="utf-8") as f:
            json.dump({"frame": a.frame, "draws": st.draws}, f, ensure_ascii=False)
        print("wrote %s (%d draws)" % (a.json, len(st.draws)))
    print("frame=%d calls=%d draws=%d" % (a.frame, end - start + 1, len(st.draws)))
    if a.summary:
        import collections
        cnt = collections.Counter((d["prim"], d["tex"]) for d in st.draws)
        for (prim, tex), n in cnt.most_common(20):
            print("%4d %-10s tex=%-5s" % (n, prim, tex))
    for d in st.draws[:a.limit]:
        v = d["v"]
        xs = [p[0] for p in v]; ys = [p[1] for p in v]
        print("%-10s tex=%-4s n=%-2d bbox=(%.2f,%.2f)-(%.2f,%.2f) rgba=(%.2f,%.2f,%.2f,%.2f)"
              % (d["prim"], d["tex"], d["n"], min(xs), min(ys), max(xs), max(ys), *d["rgba"]))
        if d["n"] <= 6:
            for (p, uv) in list(zip(v, d["uv"]))[:6]:
                print("      v=(%8.3f,%8.3f,%6.2f) uv=(%.3f,%.3f)" % (p[0], p[1], p[2], uv[0], uv[1]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
