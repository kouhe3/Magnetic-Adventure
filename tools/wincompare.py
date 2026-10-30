"""T3.1 验收：把 tools/winprobe.py 对「原版」与「自建宿主」各跑一次，逐字段比对。

用法：
    python tools/wincompare.py --orig work/winprobe_game --ours build/Release \
        [--ours-exe magnethost.exe] [--orig-exe game.exe]

判据：下面这些字段必须逐字相同（都是 docs/facts.md F154/F155/F158 记录的实测值）：
    main_title, main_class, main_style, main_exstyle, client_size, dpi, dpi_awareness,
    placement_showcmd, is_zoomed, has_menu, class_hbrBackground,
    viewer(style + rect + client size)
**不参与判定**（只打印）：window_rect / border_x,y —— 自建宿主的非客户区比原版厚 10px
（原版 3/26，我们 8/31），客户区坐标与尺寸已对齐，边框厚度是已知偏差（F154 待证项）。
可比范围外（故意不比）：hwnd/pid、类句柄（hIcon/hCursor/hInstance）、monitor 名字、
top= 列表（含第三方注入窗口如 Groupie/IME）。

注意：两次运行必须串行，且运行前不能有其它 game.exe 实例（F160：疑似单实例，旧实例会让
新实例 60 s 不出窗）。
"""
import re
import subprocess
import sys

ROOT = r"C:\tmp\Magnetic Adventure"
PROBE = ROOT + r"\tools\winprobe.py"

FIELDS = ["main_title", "main_class", "main_style", "main_exstyle", "client_size",
          "dpi", "dpi_awareness", "placement_showcmd", "is_zoomed",
          "has_menu", "class_hbrBackground"]
INFO = ["window_rect", "border_x", "border_y"]


def run_probe(directory, exe):
    out = subprocess.run([sys.executable, PROBE, directory, "--exe", exe],
                         capture_output=True, text=True, timeout=180).stdout
    data = {}
    for line in out.splitlines():
        m3 = re.match(r"border_x=(\d+) border_y=(\d+)", line)
        if m3:
            data["info_border_x"] = m3.group(1)
            data["info_border_y"] = m3.group(2)
            continue
        if line.startswith("child "):
            m = re.search(r"style=(0x[0-9a-f]+).*client=(\d+x\d+)", line)
            if m:
                data["viewer_style"] = m.group(1)
                data["viewer_client"] = m.group(2)
            m2 = re.search(r"rect=(\d+,\d+,\d+,\d+)", line)
            if m2:
                data["viewer_rect"] = m2.group(1)
            continue
        if "=" not in line or line.startswith("top="):
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        if key in FIELDS:
            if key in ("main_style", "main_exstyle"):
                data[key] = val.split(" ")[0]
            elif key == "placement_showcmd":
                # 这行带着 normal_rect（外框位置，属已知偏差），只取 showCmd 与 flags
                data[key] = val.split(" normal_rect=")[0]
            elif key.startswith("is_zoomed"):
                data[key] = val.split(" has_menu=")[0]
            else:
                data[key] = val
        elif key in INFO:
            data["info_" + key] = val
    if "main_class" not in data:
        raise SystemExit("probe 没拿到主窗口：\n" + out)
    return data


def main():
    argv = sys.argv[1:]
    orig = ours = None
    orig_exe, ours_exe = "game.exe", "magnethost.exe"
    if "--orig" in argv:
        orig = argv[argv.index("--orig") + 1]
    if "--ours" in argv:
        ours = argv[argv.index("--ours") + 1]
    if "--orig-exe" in argv:
        orig_exe = argv[argv.index("--orig-exe") + 1]
    if "--ours-exe" in argv:
        ours_exe = argv[argv.index("--ours-exe") + 1]
    if not orig or not ours:
        raise SystemExit(__doc__)

    a = run_probe(orig, orig_exe)
    b = run_probe(ours, ours_exe)

    keys = FIELDS + ["viewer_style", "viewer_rect", "viewer_client"]
    bad = 0
    for k in keys:
        va, vb = a.get(k), b.get(k)
        ok = va == vb
        if not ok:
            bad += 1
        print("%-20s %-30s %-30s %s" % (k, va, vb, "OK" if ok else "DIFF"))
    print("\n-- 仅报告（不判定）--")
    for k in ("window_rect", "border_x", "border_y"):
        print("%-20s %-30s %-30s" % (k, a.get("info_" + k), b.get("info_" + k)))
    print("\nfields=%d diffs=%d" % (len(keys), bad))
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
