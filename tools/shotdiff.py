"""两张客户区截图的逐像素 A/B —— 原版 vs 自建宿主、以及 A/A 地板。

用法:
  python tools/shotdiff.py work/orig_menu.png work/host_menu.png
  python tools/shotdiff.py work/orig_menu.png work/orig_menu2.png      # A/A：应全 0
  python tools/shotdiff.py a.png b.png --shift 3      # 在 ±N 像素平移里找最优（判几何偏移）
  python tools/shotdiff.py a.png b.png --mask 496,402,60,60   # 掩掉光标区（物理像素）

输出（口径写死在这里，跨结论可比）:
  mean|Δ|  = 所有通道 |a-b| 的均值（0–255）
  p99      = 逐像素 max-channel Δ 的 99 分位
  %>16     = 逐像素 max-channel Δ > 16 的像素占比
  max WxW  = 任意 WxW 窗口内 >16 像素的最大计数，连同窗口左上角（物理像素）。
             判紧凑差异用它，不用整幅百分比：整幅 1.3% 的差异可能只来自
             一个 16x16 块（F194），只报百分比会把它当噪声抹掉。
  shifts   = 若给 --shift，列出各平移组合的 mean|Δ|（(0,0) 最优 ⇒ 无整体偏移）
  regions  = 3×3 分格的 mean|Δ|
- `--mask x,y,w,h[;x,y,w,h]` 在**全局指标与窗口计数之前**把物理像素框置零
  （光标、已知几何差异要单列，不能算进渲染残差，F199）；输出会报告掩掉多少像素。
- `--design S` 额外按物理/设计比例 S（本机 1.5）打印设计坐标，便于和布局常量对照。

覆盖边界：只看最终画面，不区分差异来自纹理过滤、取整还是几何；图尺寸不同时裁到公共
区域并在输出里注明。截图必须是同一窗口客户区的物理像素（shot_window.py 负责）。
依据：docs/facts.md F184（mean/p99/>16）、F194（同状态对 + 16x16 窗口最大计数）、
      F199（光标区单列：掩 60x60 后 205→120，整幅只掉 0.04 个百分点）。
"""
import argparse
import sys

from PIL import Image


def load_pair(a_path, b_path):
    a = Image.open(a_path).convert("RGB")
    b = Image.open(b_path).convert("RGB")
    w = min(a.width, b.width)
    h = min(a.height, b.height)
    if (a.width, a.height) != (b.width, b.height):
        print("裁到公共区域 %dx%d（a=%dx%d b=%dx%d）" %
              (w, h, a.width, a.height, b.width, b.height))
    return a.crop((0, 0, w, h)), b.crop((0, 0, w, h))


def stats(pa, pb, keep=None):
    """返回 (mean_abs_channel, p99_pixel, pct_gt16, per-pixel max-channel list)。"""
    n = len(pa)
    total = 0
    hist = [0] * 256
    px = len(pa) // 3
    used = 0
    for i in range(0, n, 3):
        if keep is not None and not keep[i // 3]:
            continue
        r = abs(pa[i] - pb[i])
        g = abs(pa[i + 1] - pb[i + 1])
        bl = abs(pa[i + 2] - pb[i + 2])
        total += r + g + bl
        m = r if r > g else g
        if bl > m:
            m = bl
        hist[m] += 1
        used += 1
    if not used:
        return 0.0, 0, 0.0, hist
    mean = total / (used * 3)
    cum = 0
    p99 = 0
    for v in range(256):
        cum += hist[v]
        if cum >= used * 0.99:
            p99 = v
            break
    gt16 = sum(hist[17:]) / used * 100.0
    return mean, p99, gt16, hist


def parse_masks(spec, w, h):
    """把 "x,y,w,h;x,y,w,h" 变成逐像素 keep 表（1=参与比较），返回 (keep, masked)。"""
    keep = bytearray(b"\x01") * (w * h)
    masked = 0
    for part in [p for p in spec.split(";") if p.strip()]:
        x, y, mw, mh = (int(v) for v in part.split(","))
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(w, x + mw), min(h, y + mh)
        if x1 <= x0 or y1 <= y0:
            continue
        row = b"\x00" * (x1 - x0)
        for yy in range(y0, y1):
            off = yy * w
            keep[off + x0:off + x1] = row
            masked += x1 - x0
    return keep, masked


def window_max(pa, pb, w, h, win, keep=None):
    """>16 掩码上的任意 win×win 最大计数 + 左上角（物理像素）。"""
    from array import array
    if win <= 0 or win > w or win > h:
        return 0, 0, 0
    integ = array("I", bytes(4 * (w + 1) * (h + 1)))
    stride = w + 1
    for y in range(h):
        rowsum = 0
        base = y * w * 3
        for x in range(w):
            i = x * 3
            if keep is not None and not keep[y * w + x]:
                m = 0
            else:
                a = base + i
                r = abs(pa[a] - pb[a])
                g = abs(pa[a + 1] - pb[a + 1])
                b = abs(pa[a + 2] - pb[a + 2])
                m = r if r > g else g
                if b > m:
                    m = b
            rowsum += 1 if m > 16 else 0
            integ[(y + 1) * stride + x + 1] = integ[y * stride + x + 1] + rowsum
    best, bx, by = 0, 0, 0
    for y in range(0, h - win + 1):
        bottom = (y + win) * stride
        top = y * stride
        for x in range(0, w - win + 1):
            v = (integ[bottom + x + win] - integ[bottom + x]
                 - integ[top + x + win] + integ[top + x])
            if v > best:
                best, bx, by = v, x, y
    return best, bx, by


def shifted_stats(img_a, img_b, dx, dy):
    """把 b 平移 (dx,dy) 后与 a 比（等同测试 a 是否被整体移动）。"""
    from PIL import ImageChops
    b = ImageChops.offset(img_b, dx, dy)
    return stats(img_a.tobytes(), b.tobytes())[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("a")
    ap.add_argument("b")
    ap.add_argument("--shift", type=int, default=0, help="在 ±N 像素里扫平移（0=不扫）")
    ap.add_argument("--regions", action="store_true", help="输出 3×3 分格 mean|Δ|")
    ap.add_argument("--win", type=int, default=16,
                    help="紧凑差异的窗口边长（物理像素，0=不算；默认 16）")
    ap.add_argument("--mask", default="",
                    help="物理像素框 x,y,w,h[;x,y,w,h]，先掩再算指标（光标/已知几何差异）")
    ap.add_argument("--design", type=float, default=0.0,
                    help="物理/设计比例（本机 1.5），>0 时额外打印设计坐标")
    a = ap.parse_args()

    ia, ib = load_pair(a.a, a.b)
    pa, pb = ia.tobytes(), ib.tobytes()
    keep = None
    if a.mask:
        keep, masked = parse_masks(a.mask, ia.width, ia.height)
        print("mask=%d px (%.3f%%)" % (masked, masked * 100.0 / (ia.width * ia.height)))
    mean, p99, gt16, _ = stats(pa, pb, keep)
    print("size=%dx%d mean|Δ|=%.4f p99=%d >16=%.3f%%" % (ia.width, ia.height, mean, p99, gt16))
    if a.win:
        cnt, wx, wy = window_max(pa, pb, ia.width, ia.height, a.win, keep)
        line = "max%dx%d = %d/%d at (%d,%d)" % (
            a.win, a.win, cnt, a.win * a.win, wx, wy)
        if a.design > 0:
            line += " design (%.1f,%.1f)" % (wx / a.design, wy / a.design)
        print(line)
    if a.shift:
        best = None
        for dy in range(-a.shift, a.shift + 1):
            for dx in range(-a.shift, a.shift + 1):
                m = shifted_stats(ia, ib, dx, dy)
                if best is None or m < best[0]:
                    best = (m, dx, dy)
                print("  shift(%+d,%+d) mean|Δ|=%.4f" % (dx, dy, m))
        print("best shift=(%+d,%+d) mean|Δ|=%.4f" % (best[1], best[2], best[0]))
    if a.regions:
        w, h = ia.width // 3, ia.height // 3
        for ry in range(3):
            row = []
            for rx in range(3):
                pa = ia.crop((rx * w, ry * h, (rx + 1) * w, (ry + 1) * h)).tobytes()
                pb = ib.crop((rx * w, ry * h, (rx + 1) * w, (ry + 1) * h)).tobytes()
                row.append("%.3f" % stats(pa, pb)[0])
            print("  region row %d: %s" % (ry, " ".join(row)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
