"""两个 GLDRW02 绘制列表的逐 draw 对拍 —— 宿主现算的布局 vs 原版抓包。

用法:
  python tools/gl_drawlist.py work/glprobe/glffi4.bin --frame 20 --pack work/menu_draw.bin
  HOST_DRAW_DUMP=work/host_draws.bin python tools/shot_window.py build/Release/magnethost.exe ...
  python tools/draw_ab.py work/menu_draw.bin work/host_draws.bin [--tol 0.0015]

判据（两段分开报）:
  A. 可见 draw（alpha > 0.5）：按顺序逐 draw 比 纹理 id / 顶点数 / 每个顶点的
     NDC（x,y）/ UV。tol 单位是 NDC（0.0015 ≈ 设计空间 0.75 px）。这一段决定退出码。
  B. 隐藏 draw（alpha <= 0.5）：单独成组比，默认只报不判（--strict 时也判 FAIL）。
     它不可见，但数量/状态差异是结构漂移（例：宿主根本不发这批 draw），必须打出来。
  每对 draw 另比状态：caps 位、prim 枚举、blend src/dst、rgba 四通道。
  状态差异默认只报；--strict 时计入 FAIL。

覆盖边界: 只覆盖立即模式单帧、GLDRW02 记录的字段。不覆盖帧间顺序、纹理内容、
  深度/模板缓冲，也不判"alpha=0 是否真被混合吞掉"（那要截图像素验证）。
  纹理内容差异（过滤/mip）不在本工具里。
依据: docs/facts.md F182（21 draw 基准）、F186（prim）、F188（设计空间常量）、
  F197/F198（隐藏 draw 与 caps 的覆盖缺口）。
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
        out.append({"tex": tex, "n": n, "caps": caps, "prim": prim, "blend": (src, dst),
                    "rgba": rgba, "v": verts})
    return out


def visible(draws):
    return [d for d in draws if d["rgba"][3] > 0.5]


def hidden(draws):
    return [d for d in draws if d["rgba"][3] <= 0.5]


def state_diffs(x, y):
    out = []
    if x["caps"] != y["caps"]:
        out.append("caps %d/%d" % (x["caps"], y["caps"]))
    if x["prim"] != y["prim"]:
        out.append("prim %d/%d" % (x["prim"], y["prim"]))
    if x["blend"] != y["blend"]:
        out.append("blend %s/%s" % (x["blend"], y["blend"]))
    if max(abs(p - q) for p, q in zip(x["rgba"], y["rgba"])) > 1e-6:
        out.append("rgba %s/%s" % (tuple(round(c, 3) for c in x["rgba"]),
                                   tuple(round(c, 3) for c in y["rgba"])))
    return out


def compare(o, h, tol, label, judge):
    print("%s: oracle=%d host=%d" % (label, len(o), len(h)))
    bad = states = 0
    mx = my = muv = 0.0
    if len(o) != len(h):
        if judge:
            bad += 1
        print("  !! 数量不一致（%s）" % ("判 FAIL" if judge else "只报"))
    for i, (x, y) in enumerate(zip(o, h)):
        if x["tex"] != y["tex"] or x["n"] != y["n"]:
            if judge:
                bad += 1
            print("  %-2d tex/n DIFF oracle=%s/%d host=%s/%d"
                  % (i, x["tex"], x["n"], y["tex"], y["n"]))
            continue
        dx = max(abs(p[0] - q[0]) for p, q in zip(x["v"], y["v"]))
        dy = max(abs(p[1] - q[1]) for p, q in zip(x["v"], y["v"]))
        du = max(abs(p[2] - q[2]) for p, q in zip(x["v"], y["v"]))
        dv = max(abs(p[3] - q[3]) for p, q in zip(x["v"], y["v"]))
        mx, my, muv = max(mx, dx), max(my, dy), max(muv, du, dv)
        sd = state_diffs(x, y)
        if sd:
            states += 1
        geo_ok = max(dx, dy) <= tol and max(du, dv) <= tol
        if judge and not geo_ok:
            bad += 1
        print("  %-2d tex=%-2d n=%-2d dx=%.6f dy=%.6f duv=%.2e%s%s"
              % (i, x["tex"], x["n"], dx, dy, max(du, dv),
                 "" if geo_ok else "  <-- GEOM",
                 ("  state: " + "; ".join(sd)) if sd else ""))
    print("  -> max |dx|=%.6f |dy|=%.6f |duv|=%.2e  state-diffs=%d" % (mx, my, muv, states))
    return bad, states, mx, my, muv


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("oracle")
    ap.add_argument("host")
    ap.add_argument("--tol", type=float, default=0.0015)
    ap.add_argument("--ignore", default="1",
                    help="忽略的纹理 id（逗号分隔）。默认 1=GL 光标：它跟随鼠标，几何与原版抓包的静态帧不可比")
    ap.add_argument("--strict", action="store_true",
                    help="隐藏 draw 的数量/状态差异、以及任意状态差异都判 FAIL")
    a = ap.parse_args()
    skip = {int(x) for x in a.ignore.split(",") if x.strip()}
    keep = lambda d: d["tex"] not in skip
    od, hd = load(a.oracle), load(a.host)
    bad, st1, mx, my, muv = compare([d for d in visible(od) if keep(d)],
                                    [d for d in visible(hd) if keep(d)],
                                    a.tol, "可见 draw", True)
    bad2, st2, _, _, _ = compare([d for d in hidden(od) if keep(d)],
                                 [d for d in hidden(hd) if keep(d)],
                                 a.tol, "隐藏 draw (alpha<=0.5)", a.strict)
    bad += bad2
    states = st1 + st2
    if a.strict and states:
        bad += 1
    print("\n可见几何: max|dx|=%.6f max|dy|=%.6f max|duv|=%.2e tol=%.4f"
          % (mx, my, muv, a.tol))
    print("状态差异: %d 处（caps/prim/blend/rgba；默认只报，--strict 判 FAIL）" % states)
    print("verdict -> %s" % ("PASS" if bad == 0 else "FAIL"))
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
