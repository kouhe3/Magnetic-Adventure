"""从录制生成「每份录制覆盖哪些 b2 导出」表（`mapping/rec_exports.csv`）。

用途: 给 `tools/rec_pick.py` 做覆盖选样的输入；也用来回答「这次改动有没有被任何录制观测过」。

用法:
  python tools/gen_rec_exports.py                        # 解析 work/rec_*/ffi.bin（27.9 GiB，约 2 min）
  python tools/gen_rec_exports.py --from-probe work/oracle_cost_probe.json  # 复用已解析产物（秒级）
  python tools/gen_rec_exports.py --check                # 只比对现存 CSV，不写

输出列:
  rec         录制目录名（work/rec_*）
  levels      mapping/levels.csv 里的关卡名，`|` 分隔（同一份日志可服务多个关卡）
  calls       日志里的 pre 记录数（= 重放要执行的调用数）
  size_bytes  ffi.bin 大小
  exports     该日志出现过 b2 导出名，`|` 分隔

判据:
  退出码 0；行数 == work/rec_*/ffi.bin 的份数；每行 exports 非空。
  `--check` 发现差异时退出码 1 并打印差异行。

边界:
  * 观测单位是**调用**，不回答调用点（`tools/b2_sites.py sites` 才有返回地址）。
  * 不是「原版调用过什么」的全集：代理默认过滤只读 getter（`kHotGetters`，F308），
    要覆盖它们得用 `B2PROXY_HOT=1` 另录。
  * 导出集合与构建无关（录制是原版写的），本表可长期复用；新增/删除录制后重跑。

失效条件: B2FFI02 magic 变化、`tools/ffi.py` 的 NAMES 表变化、mapping/levels.csv 变动。

依据: docs/facts.md F308。
"""
import argparse
import csv
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import ffi  # noqa: E402

OUT = os.path.join(ROOT, "mapping", "rec_exports.csv")
LEVELS = os.path.join(ROOT, "mapping", "levels.csv")
HEADER = ["rec", "levels", "calls", "size_bytes", "exports"]


def load_levels():
    m = {}
    for row in csv.DictReader(open(LEVELS, encoding="utf-8")):
        m.setdefault(row["rec"].strip(), []).append(row["level"].strip())
    return m


def recordings():
    work = os.path.join(ROOT, "work")
    return sorted(d for d in os.listdir(work)
                  if d.startswith("rec_") and
                  os.path.exists(os.path.join(work, d, "ffi.bin")))


def scan(path):
    """数每份日志里出现的导出名（观测单位=调用）。"""
    counts = {}
    n = 0
    for kind, v in ffi.records(path):
        if kind != "pre":
            continue
        n += 1
        rid = v[1]
        name = ffi.NAMES[rid] if 0 < rid < len(ffi.NAMES) else "#%d" % rid
        counts[name] = counts.get(name, 0) + 1
    return n, counts


def from_logs():
    ffi.load_names()
    data = {}
    for rec in recordings():
        path = os.path.join(ROOT, "work", rec, "ffi.bin")
        n, counts = scan(path)
        data[rec] = {"calls": n, "size_bytes": os.path.getsize(path),
                     "exports": sorted(counts)}
        print("%-28s calls=%-9d exports=%d" % (rec, n, len(counts)), flush=True)
    return data


def from_probe(path):
    d = json.load(open(path, encoding="utf-8"))["recs"]
    return {rec: {"calls": v["calls"], "size_bytes": v["size"],
                  "exports": sorted(v["exports"])} for rec, v in d.items()}


def render(data, levels):
    lines = []
    for rec in sorted(data):
        v = data[rec]
        lines.append([rec, "|".join(levels.get(rec, [])), str(v["calls"]),
                      str(v["size_bytes"]), "|".join(v["exports"])])
    return lines


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from-probe", default="", help="复用 work/oracle_cost_probe.json")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()

    if a.from_probe:
        data = from_probe(os.path.join(ROOT, a.from_probe)
                          if not os.path.isabs(a.from_probe) else a.from_probe)
    else:
        data = from_logs()
    levels = load_levels()
    rows = render(data, levels)

    if a.check:
        if not os.path.exists(OUT):
            print("missing", OUT)
            return 1
        old = list(csv.reader(open(OUT, encoding="utf-8")))
        want = [HEADER] + rows
        if old == want:
            print("CHECK OK rows=%d" % (len(want) - 1))
            return 0
        for i, (o, w) in enumerate(zip(old, want)):
            if o != w:
                print("DIFF row %d\n  old %s\n  new %s" % (i, o[:3], w[:3]))
                break
        print("CHECK FAIL old=%d new=%d" % (len(old) - 1, len(want) - 1))
        return 1

    # 仓库追踪的文本统一 CRLF（.gitattributes `* -text`，F130）；
    # newline="" 才能让 lineterminator 原样落盘，不会写成 \r\r\n。
    with open(OUT, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\r\n")
        w.writerow(HEADER)
        w.writerows(rows)
    print("wrote %s rows=%d" % (os.path.relpath(OUT, ROOT), len(rows)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
