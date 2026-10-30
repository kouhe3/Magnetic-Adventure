"""解析 GL 代理日志（`src/glproxy/`，桩由 tools/gen_proxy.py --library opengl32 生成）。

两种记录版本（看头部 magic）：
  GLFFI01  52 B  : u32 id, u32 tick, u64 qpc, u32 ret, u32 ecx, u32 edx, u32 args[6]
  GLFFI02 652 B  : 同上但 args[12] + mem0/mem1/mem2 各 192 B
                   （mem0←args[0]、mem1←args[1]、mem2←args[8]，越界/不可读补零）
  两者都是 20 字节头：magic + u32 pid + u32 game_base + u32 orig_base。
同路径 "<log>.names" = 首次出现的 wglGetProcAddress 入参（一行一个，已去重）。

id → 名字用 mapping/opengl32-exports.csv 的序号（368 项）。

用法:
  python tools/gl_ffi.py stats  <log> [--top 40]
  python tools/gl_ffi.py frames <log> [--lo 秒] [--hi 秒] [--every 1]
  python tools/gl_ffi.py frame  <log> --index K            # 第 K 帧（从 0 数）的调用序 + 解码
  python tools/gl_ffi.py init   <log> [--count 30]
  python tools/gl_ffi.py names  <log>
  python tools/gl_ffi.py window <log> --t0 秒 --t1 秒       # 只看时间窗内的调用序

覆盖边界（读结论前必看）：
  - v01 只有名字 + 6 dword；v02 多了三块 192 B，但仍是**前缀**：矩阵 64 B 够，
    纹理像素只够指纹（192 B），大顶点数组不看。
  - 经 wglGetProcAddress 拿到的函数指针直连驱动，**代理看不到那些调用**；
    `.names` 只证明「被请求过」，是否真被调用本日志判不了。
  - 记的是「调用发生过」，不是「画面对不对」；qpc 是 QueryPerformanceCounter，
    同机可比，跨进程/跨次运行只可比间隔，不可比绝对时刻。
  - 帧边界 = 相邻两次 wglSwapBuffers（opengl32 的导出）。`SwapBuffers` 在 gdi32
    （KnownDLL，F175）——这里记到的是 `wglSwapBuffers`，两者是不是同一次呈现需另证。

依据：docs/facts.md F175（代理可行性）、F176（透明性）、F177（渲染节奏）、F178（调用面）。
"""
import argparse
import array
import collections
import ctypes
import csv
import os
import struct
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV = os.path.join(ROOT, "mapping", "opengl32-exports.csv")

HDR = struct.Struct("<8sIII")
HDR_SIZE = HDR.size
VERSIONS = {
    b"01": struct.Struct("<IIQ9I"),              # 52 B, args[6]
    b"02": struct.Struct("<IIQ15I576s"),        # 652 B, args[12] + 3×192
}


def qpf():
    """QueryPerformanceFrequency —— 显式声明 argtypes/restype，避免 64 位被截成 int。"""
    f = ctypes.c_longlong(0)
    fn = ctypes.windll.kernel32.QueryPerformanceFrequency
    fn.argtypes = [ctypes.POINTER(ctypes.c_longlong)]
    fn.restype = ctypes.c_int
    fn(ctypes.byref(f))
    return f.value or 1


def names():
    with open(CSV, encoding="utf-8", errors="replace") as f:
        return {int(r["ordinal"]): r["name"] for r in csv.DictReader(f)}


def load(path):
    """返回会话字典：ver / rec 结构 / ids / qpcs / n / bytes。"""
    with open(path, "rb") as f:
        head = f.read(HDR_SIZE)
        if len(head) < HDR_SIZE:
            raise SystemExit("日志短于头部：%s" % path)
        magic, pid, game, orig = HDR.unpack(head)
        ver = magic[5:7]
        if not magic.startswith(b"GLFFI0") or ver not in VERSIONS:
            raise SystemExit("magic/版本不符：%r" % magic)
        rec = VERSIONS[ver]
        f.seek(0, os.SEEK_END)
        size = f.tell()
        n = (size - HDR_SIZE) // rec.size
        ids = array.array("I")
        qpcs = array.array("q")
        f.seek(HDR_SIZE)
        for i in range(n):
            chunk = f.read(rec.size)
            if len(chunk) < rec.size:
                break
            r = rec.unpack(chunk)
            ids.append(r[0])
            qpcs.append(r[2])
    return {"magic": magic, "ver": ver, "rec": rec, "pid": pid, "game": game,
            "orig": orig, "bytes": size, "n": n, "ids": ids, "qpcs": qpcs,
            "size_ok": (size - HDR_SIZE) % rec.size == 0}


def iter_records(path):
    """逐条产出 (ver, unpack 后的 tuple)，布局同 VERSIONS[ver].unpack。

    给需要逐条比对的仪器复用（如 tools/gl_seq_ab.py）：读文件与校验 magic
    只在这里定义一次，避免第二个解析器与日志格式分叉。
    """
    with open(path, "rb") as f:
        head = f.read(HDR_SIZE)
        if len(head) < HDR_SIZE:
            raise SystemExit("日志短于头部：%s" % path)
        magic, _pid, _game, _orig = HDR.unpack(head)
        ver = magic[5:7]
        if not magic.startswith(b"GLFFI0") or ver not in VERSIONS:
            raise SystemExit("magic/版本不符：%r" % magic)
        rec = VERSIONS[ver]
        while True:
            chunk = f.read(rec.size)
            if len(chunk) < rec.size:
                break
            yield ver, rec.unpack(chunk)


def swap_ids(nm):
    return {k for k, v in nm.items() if v == "wglSwapBuffers"}


def decode(nm, r, ver):
    """把一条记录解成 (名字, 附加说明)。只解码已知形状，其余给 args 十六进制。"""
    name = nm.get(r[0], "?%d" % r[0])
    args = r[6:18] if ver == b"02" else r[6:12]
    extra = []
    if ver != b"02":
        return name, " ".join("%08x" % x for x in args)
    mem0 = r[18][:192]
    mem1 = r[18][192:384]
    mem2 = r[18][384:576]
    if name in ("glMultMatrixf", "glLoadMatrixf"):
        vals = struct.unpack("<16f", mem0[:64])
        extra.append("m=[%s]" % " ".join("%.3f" % v for v in vals))
    elif name == "glOrtho":
        vals = struct.unpack("<6d", struct.pack("<12I", *args))
        extra.append("ortho=(%s)" % " ".join("%.3f" % v for v in vals))
    elif name == "glTranslated":
        vals = struct.unpack("<3d", struct.pack("<6I", *args[:6]))
        extra.append("t=(%s)" % " ".join("%.3f" % v for v in vals))
    elif name in ("glTranslatef", "glScalef"):
        vals = struct.unpack("<3f", struct.pack("<3I", *args[:3]))
        extra.append("%s=(%s)" % (name[2:5].lower(), " ".join("%.3f" % v for v in vals)))
    elif name == "glRotatef":
        vals = struct.unpack("<4f", struct.pack("<4I", *args[:4]))
        extra.append("rot=(%s)" % " ".join("%.3f" % v for v in vals))
    elif name == "glColor4fv":
        extra.append("rgba=(%s)" % " ".join("%.3f" % v for v in struct.unpack("<4f", mem0[:16])))
    elif name == "glNormal3fv":
        extra.append("n=(%s)" % " ".join("%.3f" % v for v in struct.unpack("<3f", mem0[:12])))
    elif name == "glTexCoord2fv":
        extra.append("uv=(%s)" % " ".join("%.3f" % v for v in struct.unpack("<2f", mem0[:8])))
    elif name == "glTexImage2D":
        w, h = args[3], args[4]
        extra.append("target=%#x level=%d ifmt=%#x %dx%d border=%d fmt=%#x type=%#x px=%08x"
                     % (args[0], args[1], args[2], w, h, args[5], args[6], args[7], args[8]))
        extra.append("px_prefix=%s" % mem2[:32].hex())
    elif name == "glBindTexture":
        extra.append("target=%#x id=%d" % (args[0], args[1]))
    elif name in ("glGetFloatv", "glGetIntegerv"):
        extra.append("pname=%#x out=%08x" % (args[0], args[1]))
    else:
        extra.append(" ".join("%08x" % x for x in args))
    return name, " ".join(extra)


def cmd_stats(a):
    nm = names()
    s = load(a.log)
    ids = s["ids"]
    cnt = collections.Counter(ids)
    f = qpf()
    dur = (s["qpcs"][-1] - s["qpcs"][0]) / f if s["n"] else 0
    print("%s ver=%s pid=%d bytes=%d records=%d exact=%s game=%08x orig=%08x"
          % (s["magic"].rstrip(b"\0").decode(), s["ver"].decode(), s["pid"],
             s["bytes"], s["n"], s["size_ok"], s["game"], s["orig"]))
    print("duration=%.3fs rate=%.0f calls/s distinct=%d / %d exports"
          % (dur, s["n"] / dur if dur else 0, len(cnt), len(nm)))
    for k, v in cnt.most_common(a.top):
        print("%9d %-24s" % (v, nm.get(k, "?%d" % k)))


def frame_bounds(ids, sw):
    out = []
    start = 0
    for i, rid in enumerate(ids):
        if rid in sw:
            out.append((start, i))
            start = i + 1
    return out


def cmd_frames(a):
    nm = names()
    sw = swap_ids(nm)
    s = load(a.log)
    ids, qpcs = s["ids"], s["qpcs"]
    f = qpf()
    t0 = qpcs[0]
    fb = frame_bounds(ids, sw)
    if not fb:
        raise SystemExit("没找到 wglSwapBuffers：这不是一次 GL 会话？")
    clear = {k for k, v in nm.items() if v == "glClear"}
    begin = {k for k, v in nm.items() if v == "glBegin"}
    buck = collections.Counter()
    sbuck = collections.Counter()
    cbuck = collections.Counter()
    bbuck = collections.Counter()
    for i in range(s["n"]):
        sec = int((qpcs[i] - t0) / f)
        buck[sec] += 1
        rid = ids[i]
        if rid in sw:
            sbuck[sec] += 1
        elif rid in clear:
            cbuck[sec] += 1
        elif rid in begin:
            bbuck[sec] += 1
    lo = 0 if a.lo is None else int(a.lo)
    hi = 10 ** 9 if a.hi is None else int(a.hi)
    print("sec  calls  swap clear begin")
    for sec in range(lo, min(hi, max(buck) + 1), max(1, a.every)):
        print("%3d %7d %5d %5d %5d"
              % (sec, buck.get(sec, 0), sbuck.get(sec, 0), cbuck.get(sec, 0),
                 bbuck.get(sec, 0)))
    gaps = sorted((qpcs[fb[i + 1][1]] - qpcs[fb[i][1]]) / f for i in range(len(fb) - 1))
    if gaps:
        def pct(p):
            return gaps[min(len(gaps) - 1, int(len(gaps) * p))] * 1e3
        print("frames=%d swap_gap_ms p50=%.2f p90=%.2f p99=%.2f max=%.1f"
              % (len(fb), pct(.5), pct(.9), pct(.99), gaps[-1] * 1e3))


def _print_records(s, start, end):
    nm = names()
    f = qpf()
    t0 = s["qpcs"][0] if s["n"] else 0
    with open(s["path"], "rb") as fh:
        fh.seek(HDR_SIZE + start * s["rec"].size)
        blob = fh.read((end - start + 1) * s["rec"].size)
    for i, r in enumerate(s["rec"].iter_unpack(blob)):
        name, extra = decode(nm, r, s["ver"])
        print("%4d %8.3fs %-22s %s" % (i, (r[2] - t0) / f, name, extra))


def cmd_frame(a):
    nm = names()
    s = load(a.log)
    s["path"] = a.log
    fb = frame_bounds(s["ids"], swap_ids(nm))
    if not (0 <= a.index < len(fb)):
        raise SystemExit("index 越界：共 %d 帧" % len(fb))
    start, end = fb[a.index]
    print("frame %d  rec %d..%d  calls=%d" % (a.index, start, end, end - start + 1))
    _print_records(s, start, end)


def cmd_window(a):
    s = load(a.log)
    s["path"] = a.log
    f = qpf()
    t0 = s["qpcs"][0]
    idx = [i for i in range(s["n"]) if a.t0 <= (s["qpcs"][i] - t0) / f <= a.t1]
    if not idx:
        raise SystemExit("时间窗内没有记录")
    print("window %.3f..%.3f s -> rec %d..%d (%d 条)"
          % (a.t0, a.t1, idx[0], idx[-1], len(idx)))
    _print_records(s, idx[0], idx[-1])


def cmd_init(a):
    s = load(a.log)
    s["path"] = a.log
    _print_records(s, 0, min(a.count, s["n"]) - 1)


def cmd_names(a):
    p = a.log + ".names"
    if not os.path.exists(p):
        raise SystemExit("没有 %s（本次运行没调用 wglGetProcAddress）" % p)
    for line in open(p, encoding="utf-8", errors="replace"):
        line = line.strip()
        if line:
            print(line)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("stats")
    p.add_argument("log")
    p.add_argument("--top", type=int, default=40)
    p.set_defaults(func=cmd_stats)

    p = sub.add_parser("frames")
    p.add_argument("log")
    p.add_argument("--lo", type=float, default=None)
    p.add_argument("--hi", type=float, default=None)
    p.add_argument("--every", type=int, default=1)
    p.set_defaults(func=cmd_frames)

    p = sub.add_parser("frame")
    p.add_argument("log")
    p.add_argument("--index", type=int, required=True)
    p.set_defaults(func=cmd_frame)

    p = sub.add_parser("init")
    p.add_argument("log")
    p.add_argument("--count", type=int, default=30)
    p.set_defaults(func=cmd_init)

    p = sub.add_parser("window")
    p.add_argument("log")
    p.add_argument("--t0", type=float, required=True)
    p.add_argument("--t1", type=float, required=True)
    p.set_defaults(func=cmd_window)

    p = sub.add_parser("names")
    p.add_argument("log")
    p.set_defaults(func=cmd_names)

    a = ap.parse_args()
    return a.func(a)


if __name__ == "__main__":
    sys.exit(main())
