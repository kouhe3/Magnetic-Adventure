"""把 `work/sweep.jsonl` 渲染成关卡表，并写回 `docs/levels.md` 的标记块。

用法:
  python tools/report_sweep.py            # 只打印
  python tools/report_sweep.py --write    # 替换 <!-- sweep:begin --> … <!-- sweep:end -->

数据来源（各管一件事，避免一处漂移）：
  - `mapping/levels.csv`  录制 ↔ 关卡（rec 是录制目录名，一行一份录制，同一关可多份）；
  - `work/sweep.jsonl`    每份录制的判据数字 + 构建指纹（tools/sweep.py 产出）；
  - `work/level_index.json` 关卡的权威清单与顺序（pak 里的 Lua 文件名）。
"""
import argparse
import csv
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEVELS_CSV = os.path.join(ROOT, "mapping", "levels.csv")
SWEEP = os.path.join(ROOT, "work", "sweep.jsonl")
INDEX = os.path.join(ROOT, "work", "level_index.json")
DOC = os.path.join(ROOT, "docs", "levels.md")
BEGIN, END = "<!-- sweep:begin -->", "<!-- sweep:end -->"


def load_map():
    """rec -> [关卡名]，同时给出关卡顺序（以 level_index.json 为准）。"""
    order = []
    try:
        order = [e["cap"] for e in json.load(open(INDEX, encoding="utf-8"))]
    except (OSError, json.JSONDecodeError):
        pass
    rec2lv, seen, notes = {}, set(), {}
    for row in csv.DictReader(open(LEVELS_CSV, encoding="utf-8")):
        rec, lv = row["rec"].strip(), row["level"].strip()
        rec2lv.setdefault(rec, []).append(lv)
        if row.get("note", "").strip():
            notes[rec] = row["note"].strip()
        if lv not in seen:
            seen.add(lv)
            if lv not in order:
                order.append(lv)
    return rec2lv, order, notes


def load_sweep():
    rows = {}
    try:
        for line in open(SWEEP, encoding="utf-8"):
            line = line.strip()
            if line:
                r = json.loads(line)
                rows[r["rec"]] = r
    except OSError:
        pass
    return rows


def fmt_int(v):
    if isinstance(v, bool) or v is None:
        return "-"
    if isinstance(v, float) and v == int(v):
        return f"{int(v):,}"
    return f"{v:,}" if isinstance(v, int) else "-"


def verdict_cell(row):
    v = row.get("verdict", "?")
    b = row.get("bounded") or {}
    note = row.get("_note")
    if v == "PASS" and b.get("last"):
        v = (f"PASS（末段仍有超差：近端中位 {int(b['last'])}，"
             f"阈值 {int(b['prev'] * 1.25 + 2)}）")
    return f"{v}；{note}" if note else v


def render():
    rec2lv, order, notes = load_map()
    rows = load_sweep()
    lv2recs = {}
    for rec, lvs in rec2lv.items():
        for lv in lvs:
            lv2recs.setdefault(lv, []).append(rec)

    out = ["| 关卡 | 录制 | 格式 | 调用 | 步数 | 超差 body-state | 逐位首发 | 首段→末段 | 末段幅度 | 判定 |",
           "|---|---|---|---|---|---|---|---|---|---|"]
    stats = {"level": 0, "pass": 0, "fail": 0, "none": 0, "usable": 0,
             "zero": 0, "v01": 0, "small": 0, "missing_row": []}
    counted = set()          # 一份录制可能服务多个关卡（对话关组），统计时只算一次
    no_corpus = []
    for lv in order:
        recs = lv2recs.get(lv, [])
        if recs:
            stats["level"] += 1
        best = None
        for rec in recs:
            r = rows.get(rec)
            if r is None:
                out.append(f"| {lv} | `{rec}` | ? | - | - | - | - | - | 未跑（sweep 缺行） |")
                stats["missing_row"].append(rec)
                continue
            r["_note"] = notes.get(rec)
            first_sighting = rec not in counted
            counted.add(rec)
            if r.get("verdict") == "UNUSABLE":
                stats["v01"] += first_sighting
            elif r.get("verdict") == "SKIP":
                stats["small"] += first_sighting
            elif r.get("usable"):
                stats["usable"] += first_sighting
                if first_sighting and not r.get("bad"):
                    stats["zero"] += 1
            if r.get("verdict") == "PASS" and best is None:
                best = rec
            b = r.get("bounded") or {}
            dev = r.get("dev_deciles") or []
            amp = f"{dev[-1]:.2g}×" if dev and r.get("bad") else "—"
            out.append("| {} | `{}` | {} | {} | {} | {} | {} | {} → {} | {} | {} |".format(
                lv, rec, r.get("magic", "?"), fmt_int(r.get("calls")),
                fmt_int(r.get("steps")), fmt_int(r.get("bad")),
                r.get("first_exact") if r.get("first_exact") is not None else "—",
                fmt_int(b.get("prev")), fmt_int(b.get("last")), amp, verdict_cell(r)))
        if not recs:
            stats["none"] += 1
            no_corpus.append(lv)
        elif best:
            stats["pass"] += 1
        elif any((rows.get(x) or {}).get("usable") for x in recs):
            stats["fail"] += 1
        else:
            stats["none"] += 1
            no_corpus.append(lv)

    usable_fps = [(r.get("build") or {}) for r in rows.values()
                  if r.get("usable") and (r.get("build") or {}).get("match")]
    fp = {}
    if usable_fps:
        from collections import Counter
        key = Counter(f.get("md5") for f in usable_fps).most_common(1)[0][0]
        fp = next(f for f in usable_fps if f.get("md5") == key)
    summary = [
        "",
        f"> **{stats['level']} 关：PASS {stats['pass']} / FAIL {stats['fail']} / "
        f"无可用录制 {stats['none']}**；录制 {stats['usable']} 份可判定"
        f"（其中全步零超差 {stats['zero']} 份）、{stats['v01']} 份 v01 排除、"
        f"{stats['small']} 份过小跳过。",
    ]
    if no_corpus:
        summary.append(f">\n> 无可用录制的关卡：{('、'.join(no_corpus))}"
                       "（只有 v01 日志或没有录制 → 需要用面板重录，F87）。")
    if fp:
        summary.append(
            f">\n> 构建指纹：`{(fp.get('md5') or '')[:8]}` `/arch:{fp.get('arch')}` "
            f"`/fp:{fp.get('fp')}` `{fp.get('config')}` `{fp.get('flags')}` "
            f"建于 {fp.get('built')}（`build/build_info.json`，F98）。")
    summary.append(">\n> 判据：`no_crash` + `bounded`（末两个十分位中位数 ≤ 前段×1.25+2，"
                   "跳过前 10% 加载期；F56/F65）。`逐位首发` 是不受容差影响的严格口径。")
    summary.append(">\n> **这条结论能撑多重**：判据是个数（每步超差 body 数是否还在涨），不是幅度——"
                   "`末段幅度` 是末个十分位里最坏一具 body 的 |Δ|/容差，被磁力/马达驱动的自由飞行体会把它放大到 1e5 倍，"
                   "但个数饱和就仍是 PASS（F73）。")
    summary.append(">\n> **噪声地板**：原版 DLL 自放同一份日志在容差内 0 差异（F72/F92），只在第 871 步一类位置出现 denormal 级差"
                   "（1e-23 量级，重放进程 FPU/MXCSR 与原版游戏内状态不完全一致，F91⑤）——"
                   "所以「有差异」只在显著高于 denormal 地板时成立。")
    summary.append(">\n> **仪器覆盖不到**：摘要只含 body 的 flags/sleepTime/位置/角度/速度/质量/惯量；"
                   "关节冲量、`sweep.c0/a0`、接触热启动冲量、broadphase fat AABB 都不在其中——"
                   "差异出现在「已覆盖部分逐位相同之后」时，正确结论是「在这里看不见」（F88/F91/F92）。")
    return "\n".join(out + summary)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()
    text = render()
    print(text)
    if not a.write:
        return 0
    doc = open(DOC, encoding="utf-8").read()
    i, j = doc.find(BEGIN), doc.find(END)
    if i < 0 or j < 0:
        raise SystemExit(f"{DOC} 缺标记 {BEGIN} / {END}")
    doc = doc[:i + len(BEGIN)] + "\n" + text + "\n" + doc[j:]
    open(DOC, "w", encoding="utf-8", newline="\n").write(doc)
    print(f"\nwrote {os.path.relpath(DOC, ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
