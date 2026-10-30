#!/usr/bin/env python3
"""GLFFI02 调用序 A/B 对拍 —— T6.2 的判据仪器。

用法:
  python tools/gl_seq_ab.py A.bin B.bin
  python tools/gl_seq_ab.py A.bin B.bin --a-skip 1 --b-skip 0 --frames 60
  python tools/gl_seq_ab.py A.bin A.bin --json        # A/A 地板

判据: PASS = 比较窗口内每个调用（名字 + 已知签名参数）逐条相同。
      首个分歧给出 frame / call / 双方名字与参数；不报一致率。

覆盖边界（读结论前必看）:
  - 只覆盖代理写进日志的 368 个 opengl32 导出；经 wglGetProcAddress 直连
    驱动的调用本日志看不到（`.names` 只证明被请求过）。
  - 参数只比较下方 SPEC 表里的签名；表外函数只比名字（计入 name-only）。
    未列出的尾部 dword 可能是栈上垃圾，不比较。
  - 纹理/对象 id 不做归一；两次运行的 id 序列不同会作为分歧报出。
  - 帧边界 = wglSwapBuffers（与 tools/gl_ffi.py 一致）；capture 时间窗
    可能从半帧开始，默认 a-skip/b-skip = 1 丢掉首帧。
  - v01 只有 6 个 dword、没有 mem 块；依赖指针内容的签名记为未覆盖。

地板: 同一 exe、同一脚本/时间窗抓两次，跑本工具。非 0 条分歧即噪声地板；
      地板不为 0 时，A/B 的"差异"只在显著高于地板时才成立。

已量地板（`work/aa_gl_a.bin` vs `aa_gl_b.bin`，原版、菜单、T0=17000 T1=19000）:
  - 结构（--names-only）1–13 帧: 11,232 调用 / 0 bad_frames；
    1–60 帧: 2 bad_frames（首个 frame14 call0 glLightModelfv vs glGetIntegerv，
    窗口激活/上下文事件；有效窗口取 13 帧或把 2 帧当噪声）。
  - 参数 --float-tol 1e-3 1–13 帧: 0 bad_frames；逐位比较时 glRotatef 有
    1e-4 级差（光标旋转随帧相位），glColorMask 的 GLboolean 高字节是栈残渣
    （已按低字节比较，见 BYTE_ARGS）。

依据: docs/facts.md F175（代理可行性）、F176（透明性）、F181（逐帧 draw）、
      F213/F214（库层与窗口层已复原，渲染判据转调用序）。
"""
import argparse
import json
import struct
import sys

import gl_ffi


# 无参数 / 参数不可比（指针）的函数：只比名字。
NO_ARGS = {
    "glEnd", "glLoadIdentity", "glPushMatrix", "glPopMatrix", "glGetError",
    "glFinish", "glFlush", "wglSwapBuffers",
}
INT_ARGS = {
    "glMatrixMode": 1, "glEnable": 1, "glDisable": 1, "glDepthMask": 1,
    "glBegin": 1, "glClear": 1, "glHint": 2, "glShadeModel": 1,
    "glLightModeli": 2, "glTexEnvi": 3, "glColorMask": 4, "glBlendFunc": 2,
    "glDepthFunc": 1, "glViewport": 4, "glScissor": 4, "glBindTexture": 2,
    "glGetFloatv": 1, "glGetIntegerv": 1,
}
# GLboolean 参数在 FPC/GLScene 里只写低字节（高字节是栈残渣，A/A 自己都不等）：
# glColorMask 四个参数实测低字节恒 1、高位随机（F215）。
BYTE_ARGS = {
    "glColorMask": 4, "glDepthMask": 1,
}
FLOAT_ARGS = {
    "glVertex2f": 2, "glVertex3f": 3, "glTexCoord2f": 2,
    "glColor3f": 3, "glColor4f": 4, "glNormal3f": 3,
    "glTranslatef": 3, "glScalef": 3, "glRotatef": 4, "glClearColor": 4,
}
MEM_FLOATS = {
    "glMultMatrixf": 16, "glLoadMatrixf": 16,
    "glColor4fv": 4, "glNormal3fv": 3, "glTexCoord2fv": 2,
}

DEFAULT_IGNORE = ",".join([
    "glGetError",
    "wglMakeCurrent", "wglGetProcAddress", "wglGetPixelFormat",
    "wglDescribePixelFormat", "wglCreateContext", "wglDeleteContext",
    "wglSetPixelFormat", "wglChoosePixelFormat", "wglGetCurrentDC",
])


def _f32(args, n):
    return struct.unpack("<%df" % n, struct.pack("<%dI" % n, *args[:n]))


def _f64(args, n):
    return struct.unpack("<%dd" % n, struct.pack("<%dI" % (n * 2), *args[:n * 2]))


def _fsame(a, b, tol):
    if tol <= 0:
        return struct.pack("<f", a) == struct.pack("<f", b)
    return abs(a - b) <= tol * max(1.0, abs(a), abs(b))


def _ints_same(a, b, n):
    return tuple(a[:n]) == tuple(b[:n])


def _mem_float_values(call, n):
    _name, _args, mem = call
    if len(mem[0]) < n * 4:
        return None
    return _f32(struct.unpack("<%dI" % n, mem[0][:n * 4]), n)


def compare_call(a, b, tol):
    """返回 (ok, covered, detail_a, detail_b)。covered=False 表示只比了名字。"""
    name_a, args_a, mem_a = a
    name_b, args_b, _mem_b = b
    if name_a != name_b:
        return False, True, describe(a), describe(b)
    if name_a in NO_ARGS:
        return True, True, "", ""
    if name_a in BYTE_ARGS:
        n = BYTE_ARGS[name_a]
        ok = all((args_a[i] & 0xFF) == (args_b[i] & 0xFF) for i in range(n))
        return ok, True, describe(a), describe(b)
    if name_a in INT_ARGS:
        n = INT_ARGS[name_a]
        ok = _ints_same(args_a, args_b, n)
        return ok, True, describe(a), describe(b)
    if name_a in FLOAT_ARGS:
        n = FLOAT_ARGS[name_a]
        ok = all(_fsame(x, y, tol) for x, y in
                 zip(_f32(args_a, n), _f32(args_b, n)))
        return ok, True, describe(a), describe(b)
    if name_a == "glTexEnvf":
        ok = _ints_same(args_a, args_b, 2) and _fsame(
            _f32(args_a[2:], 1)[0], _f32(args_b[2:], 1)[0], tol)
        return ok, True, describe(a), describe(b)
    if name_a in MEM_FLOATS:
        n = MEM_FLOATS[name_a]
        va = _mem_float_values(a, n)
        vb = _mem_float_values(b, n)
        if va is None or vb is None:
            return True, False, "", ""
        ok = all(_fsame(x, y, tol) for x, y in zip(va, vb))
        return ok, True, describe(a), describe(b)
    if name_a == "glOrtho":
        ok = all(_fsame(x, y, tol) for x, y in
                 zip(_f64(args_a, 6), _f64(args_b, 6)))
        return ok, True, describe(a), describe(b)
    if name_a == "glTranslated":
        ok = all(_fsame(x, y, tol) for x, y in
                 zip(_f64(args_a, 3), _f64(args_b, 3)))
        return ok, True, describe(a), describe(b)
    if name_a == "glTexImage2D":
        ok = _ints_same(args_a, args_b, 8) and mem_a[2][:9] == b[2][:9]
        return ok, True, describe(a), describe(b)
    if name_a in ("glTexEnvfv", "glLightModelfv"):
        # 只比枚举；数组指针不参与（args[1]/args[2] 指向的 mem 不在 dump 里）。
        ok = _ints_same(args_a, args_b, 1 if name_a == "glLightModelfv" else 2)
        return ok, True, describe(a), describe(b)
    if name_a == "wglGetPixelFormat":
        return True, False, "", ""
    return True, False, "", ""


def describe(call):
    name, args, mem = call
    if name in FLOAT_ARGS:
        n = FLOAT_ARGS[name]
        return "%s(%s)" % (name, " ".join("%.6g" % v for v in _f32(args, n)))
    if name == "glTexEnvf":
        return "%s(%#x,%#x,%.6g)" % ((name,) + tuple(args[:2]) + (_f32(args[2:], 1)[0],))
    if name in MEM_FLOATS:
        vals = _mem_float_values(call, MEM_FLOATS[name])
        if vals:
            return "%s[%s]" % (name, " ".join("%.6g" % v for v in vals))
    if name == "glOrtho":
        return "%s(%s)" % (name, " ".join("%.6g" % v for v in _f64(args, 6)))
    if name == "glTranslated":
        return "%s(%s)" % (name, " ".join("%.6g" % v for v in _f64(args, 3)))
    if name == "glTexImage2D":
        return "%s(%#x,%d,%#x,%dx%d,b%d,%#x,%#x,crc=%s)" % (
            name, args[0], args[1], args[2], args[3], args[4], args[5],
            args[6], args[7], mem[2][:9].hex())
    return "%s %s" % (name, " ".join("%08x" % x for x in args[:6]))


def load_frames(path, max_frames=0):
    nm = gl_ffi.names()
    sw = gl_ffi.swap_ids(nm)
    frames = []
    cur = []
    for ver, r in gl_ffi.iter_records(path):
        if ver == b"02":
            args = tuple(r[6:18])
            blob = r[18]
            mem = (blob[:192], blob[192:384], blob[384:576])
        else:
            args = tuple(r[6:12])
            mem = (b"", b"", b"")
        cur.append((nm.get(r[0], "?%d" % r[0]), args, mem))
        if r[0] in sw:
            frames.append(cur)
            cur = []
            if max_frames and len(frames) >= max_frames:
                break
    if cur and not (max_frames and len(frames) >= max_frames):
        frames.append(cur)
    return frames, nm


def compare(frames_a, frames_b, a_skip, b_skip, max_frames, tol, ignore,
            names_only=False):
    n = min(len(frames_a) - a_skip, len(frames_b) - b_skip)
    if max_frames:
        n = min(n, max_frames)
    first = None
    bad_frames = 0
    calls = 0
    name_only = 0
    for k in range(max(0, n)):
        fa = [c for c in frames_a[a_skip + k] if c[0] not in ignore]
        fb = [c for c in frames_b[b_skip + k] if c[0] not in ignore]
        this_bad = False
        for i in range(min(len(fa), len(fb))):
            calls += 1
            if names_only:
                ok, covered, da, db = (fa[i][0] == fb[i][0]), False, describe(fa[i]), describe(fb[i])
            else:
                ok, covered, da, db = compare_call(fa[i], fb[i], tol)
            if not covered:
                name_only += 1
            if not ok:
                this_bad = True
                if first is None:
                    first = {"frame": a_skip + k, "call": i,
                             "a": da, "b": db}
        if len(fa) != len(fb):
            this_bad = True
            if first is None:
                first = {"frame": a_skip + k, "call": min(len(fa), len(fb)),
                         "a": "A end (%d calls)" % len(fa),
                         "b": "B end (%d calls)" % len(fb)}
        bad_frames += 1 if this_bad else 0
    return {"frames": max(0, n), "calls": calls, "name_only": name_only,
            "bad_frames": bad_frames, "first": first}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("a")
    ap.add_argument("b")
    ap.add_argument("--a-skip", type=int, default=1)
    ap.add_argument("--b-skip", type=int, default=1)
    ap.add_argument("--frames", type=int, default=0, help="最多比较几帧（0=全部）")
    ap.add_argument("--float-tol", type=float, default=0.0,
                    help="浮点相对容差；0 = 逐位比较")
    ap.add_argument("--ignore", default=DEFAULT_IGNORE,
                    help="逗号分隔的函数名，比较时忽略（如 glGetError）")
    ap.add_argument("--names-only", action="store_true",
                    help="只比调用名序列（结构），不比参数")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    ignore = {s for s in a.ignore.split(",") if s}
    max_load = a.frames + max(a.a_skip, a.b_skip) + 1 if a.frames else 0
    frames_a, _nm = load_frames(a.a, max_load)
    frames_b, _nm = load_frames(a.b, max_load)
    res = compare(frames_a, frames_b, a.a_skip, a.b_skip, a.frames,
                  a.float_tol, ignore, a.names_only)
    res["a_frames"] = len(frames_a)
    res["b_frames"] = len(frames_b)
    res["verdict"] = "PASS" if res["first"] is None and res["frames"] > 0 else (
        "UNUSABLE" if res["frames"] <= 0 else "FAIL")
    if a.json:
        print(json.dumps(res, ensure_ascii=False))
    else:
        print("A: frames=%d  B: frames=%d" % (len(frames_a), len(frames_b)))
        print("compare frames=%d calls=%d name-only=%d bad_frames=%d"
              % (res["frames"], res["calls"], res["name_only"], res["bad_frames"]))
        if res["first"]:
            f = res["first"]
            print("FAIL first divergence frame=%d call=%d" % (f["frame"], f["call"]))
            print("  A %s" % f["a"])
            print("  B %s" % f["b"])
        else:
            print("PASS")
    return 0 if res["verdict"] == "PASS" else 1 if res["verdict"] == "FAIL" else 2


if __name__ == "__main__":
    sys.exit(main())
