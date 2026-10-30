"""解析 GL 代理日志（`src/glproxy/`，桩由 tools/gen_proxy.py --library opengl32 生成）。

日志 = 20 字节头 + N×52 字节记录（小端）：
  header: "GLFFI01\\0" + u32 pid + u32 game_base + u32 orig_base
  record: u32 id, u32 tick, u64 qpc, u32 ret, u32 ecx, u32 edx, u32 args[6]
同路径 "<log>.names" = 首次出现的 wglGetProcAddress 入参（一行一个，已去重）。

id → 名字用 mapping/opengl32-exports.csv 的序号（368 项）。

用法:
  python tools/gl_ffi.py stats  <log> [--top 40]
  python tools/gl_ffi.py frames <log> [--lo 秒] [--hi 秒] [--every 1]
  python tools/gl_ffi.py frame  <log> --index K            # 第 K 帧（从 0 数）的调用序
  python tools/gl_ffi.py init   <log> [--count 30]
  python tools/gl_ffi.py names  <log>

覆盖边界（读结论前必看）：
  - 只记「名字 + 栈上前 6 个 dword」，**不解码指针 payload**：矩阵内容、纹理像素、
    顶点数据都看不到（glMultMatrixf 只给出指针值）。
  - 经 wglGetProcAddress 拿到的函数指针直连驱动，**代理看不到那些调用**；
    `.names` 只证明「被请求过」，是否真被调用本日志判不了。
  - 记的是「调用发生过」，不是「画面对不对」；qpc 是 QueryPerformanceCounter，
    同机可比，跨进程/跨次运行只可比间隔，不可比绝对时刻。
  - 帧边界 = 相邻两次 wglSwapBuffers。`SwapBuffers` 在 gdi32（KnownDLL，F175），
    这里记到的是 opengl32 的 `wglSwapBuffers`；两者是不是同一次呈现需要另证。

依据：docs/facts.md F175/F176（代理可行与透明性）、F177（渲染节奏）、F178（调用面画像）。
"""
import argparse
import array
import bisect
import collections
import ctypes
import csv
import os
import struct
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV = os.path.join(ROOT, "mapping", "opengl32-exports.csv")

HDR = struct.Struct("<8sIII")
REC = struct.Struct("<IIQ9I")   # 52 B
HDR_SIZE = HDR.size
REC_SIZE = REC.size


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
    """返回 (header, ids, qpcs)。ids/qpcs 是 array，索引即记录号。"""
    with open(path, "rb") as f:
        data = f.read()
    if len(data) < HDR_SIZE:
        raise SystemExit("日志短于头部：%s" % path)
    magic, pid, game, orig = HDR.unpack_from(data, 0)
    if not magic.startswith(b"GLFFI0"):
        raise SystemExit("magic 不符：%r" % magic)
    n = (len(data) - HDR_SIZE) // REC_SIZE
    ids = array.array("I")
    qpcs = array.array("q")
    it = REC.iter_unpack(data[HDR_SIZE:HDR_SIZE + n * REC_SIZE])
    for r in it:
        ids.append(r[0])
        qpcs.append(r[2])
    return {"magic": magic, "pid": pid, "game": game, "orig": orig,
            "bytes": len(data), "n": n, "ids": ids, "qpcs": qpcs,
            "size_ok": (len(data) - HDR_SIZE) % REC_SIZE == 0}


def swap_ids(nm):
    return {k for k, v in nm.items() if v == "wglSwapBuffers"}


def cmd_stats(a):
    nm = names()
    s = load(a.log)
    ids = s["ids"]
    cnt = collections.Counter(ids)
    f = qpf()
    dur = (s["qpcs"][-1] - s["qpcs"][0]) / f if s["n"] else 0
    print("%s pid=%d bytes=%d records=%d exact=%s game=%08x orig=%08x"
          % (s["magic"].rstrip(b"\0").decode(), s["pid"], s["bytes"], s["n"],
             s["size_ok"], s["game"], s["orig"]))
    print("duration=%.3fs rate=%.0f calls/s distinct=%d / %d exports"
          % (dur, s["n"] / dur if dur else 0, len(cnt), len(nm)))
    for k, v in cnt.most_common(a.top):
        print("%9d %-24s" % (v, nm.get(k, "?%d" % k)))


def frame_bounds(ids, qpcs, sw):
    """返回 [(start, end)] —— 每帧是 (上一次 swap, 本次 swap] 的区间。"""
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
    fb = frame_bounds(ids, qpcs, sw)
    if not fb:
        raise SystemExit("没找到 wglSwapBuffers：这不是一次 GL 会话？")
    # 每秒汇总：调用数 / swap / glClear / glBegin
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


def cmd_frame(a):
    nm = names()
    sw = swap_ids(nm)
    s = load(a.log)
    fb = frame_bounds(s["ids"], s["qpcs"], sw)
    if not (0 <= a.index < len(fb)):
        raise SystemExit("index 越界：共 %d 帧" % len(fb))
    start, end = fb[a.index]
    f = qpf()
    t = (s["qpcs"][end] - s["qpcs"][0]) / f
    print("frame %d  rec %d..%d  calls=%d  t=%.3fs" % (a.index, start, end, end - start + 1, t))
    with open(a.log, "rb") as fh:
        fh.seek(HDR_SIZE + start * REC_SIZE)
        blob = fh.read((end - start + 1) * REC_SIZE)
    for i, r in enumerate(REC.iter_unpack(blob)):
        args = " ".join("%08x" % x for x in r[6:12])
        print("%4d %-22s %s" % (i, nm.get(r[0], "?%d" % r[0]), args))


def cmd_init(a):
    nm = names()
    s = load(a.log)
    f = qpf()
    t0 = s["qpcs"][0]
    with open(a.log, "rb") as fh:
        fh.seek(HDR_SIZE)
        blob = fh.read(min(a.count, s["n"]) * REC_SIZE)
    for r in REC.iter_unpack(blob):
        print("%8.3fs %-22s %s" % ((r[2] - t0) / f, nm.get(r[0], "?%d" % r[0]),
                                   " ".join("%08x" % x for x in r[6:12])))


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

    p = sub.add_parser("names")
    p.add_argument("log")
    p.set_defaults(func=cmd_names)

    a = ap.parse_args()
    return a.func(a)


if __name__ == "__main__":
    sys.exit(main())
