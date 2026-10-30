"""两张客户区截图的逐像素 A/B —— 原版 vs 自建宿主、以及 A/A 地板。

用法:
  python tools/shotdiff.py work/orig_menu.png work/host_menu.png
  python tools/shotdiff.py work/orig_menu.png work/orig_menu2.png      # A/A：应全 0
  python tools/shotdiff.py a.png b.png --shift 3      # 在 ±N 像素平移里找最优（判几何偏移）

输出（口径写死在这里，跨结论可比）:
  mean|Δ|  = 所有通道 |a-b| 的均值（0–255）
  p99      = 逐像素 max-channel Δ 的 99 分位
  %>16     = 逐像素 max-channel Δ > 16 的像素占比
  shifts   = 若给 --shift，列出各平移组合的 mean|Δ|（(0,0) 最优 ⇒ 无整体偏移）
  regions  = 3×3 分格的 mean|Δ|

覆盖边界：只看最终画面，不区分差异来自纹理过滤、取整还是几何；图尺寸不同时裁到公共
区域并在输出里注明。截图必须是同一窗口客户区的物理像素（shot_window.py 负责）。
依据：docs/facts.md F184（菜单对拍：mean 1.40/255、p99 24、>16 2.01%、A/A 地板 0.00）。
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


def stats(pa, pb):
    """返回 (mean_abs_channel, p99_pixel, pct_gt16, per-pixel max-channel list)。"""
    n = len(pa)
    total = 0
    hist = [0] * 256
    px = len(pa) // 3
    for i in range(0, n, 3):
        r = abs(pa[i] - pb[i])
        g = abs(pa[i + 1] - pb[i + 1])
        bl = abs(pa[i + 2] - pb[i + 2])
        total += r + g + bl
        m = r if r > g else g
        if bl > m:
            m = bl
        hist[m] += 1
    mean = total / n
    cum = 0
    p99 = 0
    for v in range(256):
        cum += hist[v]
        if cum >= px * 0.99:
            p99 = v
            break
    gt16 = sum(hist[17:]) / px * 100.0
    return mean, p99, gt16, hist


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
    a = ap.parse_args()

    ia, ib = load_pair(a.a, a.b)
    mean, p99, gt16, _ = stats(ia.tobytes(), ib.tobytes())
    print("size=%dx%d mean|Δ|=%.4f p99=%d >16=%.3f%%" % (ia.width, ia.height, mean, p99, gt16))
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
