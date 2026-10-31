"""批量把 52 关的脚本喂给 lua_probe（144 个绑定桩），报每关是否能跑完。

用法:
  python tools/lua_probe_all.py
  python tools/lua_probe_all.py --dir work/pak_gametop --probe build/tools/Release/lua_probe.exe

判据: 52/52 rc=0（脚本加载 + BaseFsBeforeCreate/Create/AttachScripts 都不报错）；
      任何失败打印第一行错误与那关的脚本列表。calls/objects 只作画像，不是阈值。

覆盖边界（与 tools/lua_probe.cpp 一致）:
  - 绑定是**桩**：Add_* 返回递增 id、其余返回 0，返回个数由脚本里的单行多值赋值推断。
    ⇒ 能证明"脚本能在 144 个入口齐备的宿主上初始化"，不能证明返回值语义或事件时序。
  - 关卡清单来自 pak 尾部 `lvl_info.lvl`（UTF-16LE）；关卡脚本必须已解包到 --dir。
依据: docs/facts.md F180（关卡=清单+脚本）、F201（144 绑定形态）。
"""
import argparse
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENTRIES = ["BaseFsBeforeCreate", "Create", "AttachScripts"]


def parse_levels(path):
    text = open(path, "rb").read().decode("utf-16")
    levels = []
    for block in re.findall(r"<Level>(.*?)</Level>", text, re.S):
        cap = re.search(r'Caption\s*=\s*"([^"]*)"', block)
        files = re.search(r'LevelFiles\s*=\s*"([^"]*)"', block)
        if not files:
            continue
        levels.append((cap.group(1) if cap else "?",
                       [f.strip() for f in files.group(1).split(",") if f.strip()]))
    return levels


def defined_entries(dirpath, leaves):
    text = ""
    for leaf in leaves:
        p = os.path.join(dirpath, leaf)
        if os.path.exists(p):
            # 必须补换行：上一个文件末尾没有 "\n" 时，下一个文件首行的
            # `function X` 会接在别人行尾，^ 匹配不到（lvl01 的 BaseFsBeforeCreate 就这样漏过）。
            text += "\n" + open(p, encoding="utf-8", errors="replace").read()
    return [e for e in ENTRIES if re.search(r"^function\s+%s\b" % re.escape(e), text, re.M)]


def run_level(probe, csv, dirpath, leaves, entries, out_path):
    cmd = [probe, "--csv", csv, "--dir", dirpath, "--out", out_path,
           "--scripts", ",".join(leaves), "--entries", ",".join(entries)]
    p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    calls = objects = 0
    m = re.search(r"calls=(\d+)\s+objects=(\d+)", p.stderr)
    if m:
        calls, objects = int(m.group(1)), int(m.group(2))
    first_err = ""
    for line in (p.stderr or "").splitlines():
        if line.startswith("script:") or line.startswith("entry:"):
            first_err = line.strip()
            break
    return p.returncode, calls, objects, first_err


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="work/pak_gametop")
    ap.add_argument("--probe", default=os.path.join("build", "tools", "Release", "lua_probe.exe"))
    ap.add_argument("--csv", default="mapping/lua-bindings.csv")
    ap.add_argument("--outdir", default="work/lua_probe")
    ap.add_argument("--json", default="work/lua_probe_all.json")
    a = ap.parse_args()

    probe = a.probe if os.path.isabs(a.probe) else os.path.join(ROOT, a.probe)
    dirpath = a.dir if os.path.isabs(a.dir) else os.path.join(ROOT, a.dir)
    csv = a.csv if os.path.isabs(a.csv) else os.path.join(ROOT, a.csv)
    outdir = a.outdir if os.path.isabs(a.outdir) else os.path.join(ROOT, a.outdir)
    json_path = a.json if os.path.isabs(a.json) else os.path.join(ROOT, a.json)
    os.makedirs(outdir, exist_ok=True)

    levels = parse_levels(os.path.join(dirpath, "lvl_info.lvl"))
    if not levels:
        print("no levels parsed from lvl_info.lvl")
        return 2

    rows = []
    failed = 0
    print("%-3s %-4s %-28s %6s %7s  %s" % ("#", "rc", "caption", "calls", "objects", "files"))
    for i, (caption, leaves) in enumerate(levels):
        entries = defined_entries(dirpath, leaves)
        out_path = os.path.join(outdir, "lvl%02d.jsonl" % i)
        rc, calls, objects, err = run_level(probe, csv, dirpath, leaves, entries, out_path)
        if rc != 0:
            failed += 1
        shown = caption.encode("ascii", "replace").decode("ascii")
        print("%-3d %-4d %-28s %6d %7d  %s%s" % (
            i, rc, shown[:28], calls, objects, ",".join(leaves),
            "" if rc == 0 else "  <= " + err))
        rows.append({"index": i, "caption": caption, "rc": rc, "calls": calls,
                     "objects": objects, "files": leaves, "entries": entries,
                     "error": err})
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({"levels": len(rows), "failed": failed, "rows": rows},
                  f, ensure_ascii=False, indent=1)
    print("\nlevels=%d failed=%d" % (len(rows), failed))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
