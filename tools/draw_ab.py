"""两个 GLDRW02 绘制列表的逐 draw 对拍 —— 宿主现算的布局 vs 原版抓包。

用法:
  python tools/gl_drawlist.py work/glprobe/glffi4.bin --frame 20 --pack work/menu_draw.bin
  HOST_DRAW_DUMP=work/host_draws.bin python tools/shot_window.py build/Release/magnethost.exe ...
  python tools/draw_ab.py work/menu_draw.bin work/host_draws.bin [--tol 0.0015]

判据:
  两边都丢掉 alpha=0 的 draw（原版把悬停/备用态也画成 alpha 0，不可见），
  然后按顺序逐 draw 比：纹理 id、顶点数、每个顶点的 NDC（x,y）、UV。
  tol 单位是 NDC（0.0015 ≈ 设计空间 0.75 px），默认按这个报 PASS/FAIL。
  最大偏差、UV 偏差、tex 序列全部打印 —— 只报"数量一致"不算证据。

覆盖边界: 只比几何/纹理/UV，不比颜色/caps/prim（这些在别处单独核对）。
依据: docs/facts.md F182（21 draw 基准）、F186（prim）、F188（设计空间常量）。
"""
import argparse
import struct
import sys


def load(path):
    b = open(path, "rb").read()
    if b[:8] != b"GLDRW02\0":
        raise SystemExit("%s: 不是 GLDRW02" % path)
    count = struct.unpack_from("<I", b, 8)[0]
    off = 12
    out = []
    for _ in range(count):
        tex, n, caps, prim, src, dst = struct.unpack_from("<6I", b, off)
        rgba = struct.unpack_from("<4f", b, off + 24)
        off += 40
        verts = []
        for _i in range(n):
            x, y, z, u, v = struct.unpack_from("<5f", b, off)
            off += 20
            verts.append((x, y, u, v))
        out.append({"tex": tex, "n": n, "caps": caps, "prim": prim, "rgba": rgba,
                    "v": verts})
    return out


def visible(draws):
    return [d for d in draws if d["rgba"][3] > 0.5]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("oracle")
    ap.add_argument("host")
    ap.add_argument("--tol", type=float, default=0.0015)
    ap.add_argument("--ignore", default="1",
                    help="忽略的纹理 id（逗号分隔）。默认 1=GL 光标：它跟随鼠标，几何与原版抓包的静态帧不可比")
    a = ap.parse_args()
    skip = {int(x) for x in a.ignore.split(",") if x.strip()}
    o = [d for d in visible(load(a.oracle)) if d["tex"] not in skip]
    h = [d for d in visible(load(a.host)) if d["tex"] not in skip]
    print("draws: oracle=%d host=%d (after dropping alpha=0)" % (len(o), len(h)))
    bad = 0
    if len(o) != len(h):
        bad += 1
        print("draw 数量不一致")
    maxd = 0.0
    maxuv = 0.0
    maxy = 0.0
    for i, (x, y) in enumerate(zip(o, h)):
        if x["tex"] != y["tex"] or x["n"] != y["n"]:
            bad += 1
            print("draw %-2d tex/n DIFF oracle=%s/%d host=%s/%d"
                  % (i, x["tex"], x["n"], y["tex"], y["n"]))
            continue
        dx = max(abs(p[0] - q[0]) for p, q in zip(x["v"], y["v"]))
        dy = max(abs(p[1] - q[1]) for p, q in zip(x["v"], y["v"]))
        du = max(abs(p[2] - q[2]) for p, q in zip(x["v"], y["v"]))
        dv = max(abs(p[3] - q[3]) for p, q in zip(x["v"], y["v"]))
        maxd = max(maxd, dx)
        maxy = max(maxy, dy)
        maxuv = max(maxuv, du, dv)
        flag = "" if max(dx, dy) <= a.tol else "  <-- DIFF"
        if max(dx, dy) > a.tol:
            bad += 1
        print("draw %-2d tex=%-2d n=%-2d dx=%.6f dy=%.6f duv=%.2e%s"
              % (i, x["tex"], x["n"], dx, dy, max(du, dv), flag))
    print("\nmax |dx|=%.6f max |dy|=%.6f max |duv|=%.2e tol=%.4f -> %s"
          % (maxd, maxy, maxuv, a.tol, "PASS" if bad == 0 else "FAIL"))
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
