"""按「改动涉及的 b2 导出」挑最小录制集，给快闸用。

为什么：全量重放 57 份要 15–17 min（F129），而一次改动通常只碰几个导出；
`verify.py` 的固定 3 份抽样只覆盖 33/58 个被观测导出（F308）——改到冷门导出时 PASS 是假阴性。
本工具用 `mapping/rec_exports.csv` 的覆盖表，按「净增覆盖 / 预计秒数」贪心挑集合。

用法:
  python tools/rec_pick.py --exports b2_Body_SetBullet
  python tools/rec_pick.py --changed HEAD~1            # 从 git diff 抓 b2_* 名字
  python tools/rec_pick.py --exports a,b --budget 90 --json
  python tools/rec_pick.py --list b2_                   # 看看哪些导出有录制覆盖

判据:
  * 每个请求的导出要么出现在某个 pick 的覆盖并集里，要么列进 `uncovered`；
  * 预计总时长 ≤ --budget 时不出 `over_budget`；预算不够时**诚实报告**缺的那份及其代价；
  * 退出码 0（有 uncovered / over_budget 也算 0，它们是结论不是错误）。

覆盖边界:
  * 覆盖表来自 `tools/gen_rec_exports.py`（观测单位=调用）；代理默认过滤只读 getter（F308），
    这些导出会落进 `uncovered` —— 要覆盖它们得先做 `B2PROXY_HOT=1` 录制，或走合成契约探针。
  * 成本取 `work/sweep.jsonl` 的 `secs`（最近一次全量、当前并行度下实测）；缺失时按
    `calls / 15000` 估算并在 `cost_src` 标 `est`。
  * 选样只保证「覆盖」，不保证「区分」：录制里有该调用 ≠ 该调用能暴露你的 bug。

失效条件: `mapping/rec_exports.csv` 过期（新增/删除录制）、`work/sweep.jsonl` 换了构建。

依据: docs/facts.md F308。
"""
import argparse
import csv
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TABLE = os.path.join(ROOT, "mapping", "rec_exports.csv")
SWEEP = os.path.join(ROOT, "work", "sweep.jsonl")
DEFAULT_FALLBACK_CPS = 15000       # 只用于缺 secs 的行：每秒调用数（F308 的中位吞吐）


def load_table():
    recs = {}
    for row in csv.DictReader(open(TABLE, encoding="utf-8")):
        recs[row["rec"]] = {
            "levels": [x for x in (row["levels"] or "").split("|") if x],
            "calls": int(row["calls"]),
            "size": int(row["size_bytes"]),
            "exports": set(x for x in (row["exports"] or "").split("|") if x),
        }
    return recs


def load_cost():
    cost = {}
    try:
        for line in open(SWEEP, encoding="utf-8"):
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            if r.get("secs"):
                cost[r["rec"]] = (float(r["secs"]), "measured")
    except OSError:
        pass
    return cost


def cost_of(rec, tbl, cost):
    if rec in cost:
        return cost[rec]
    calls = tbl[rec]["calls"]
    return (max(0.2, calls / DEFAULT_FALLBACK_CPS), "est")


def exports_from_diff(ref):
    p = subprocess.run(["git", "diff", "-U0", ref, "--", "src/b2physics"],
                       cwd=ROOT, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if p.returncode != 0:
        raise SystemExit("git diff 失败: %s" % (p.stderr or "").strip()[:300])
    names = set()
    for line in p.stdout.splitlines():
        if line.startswith(("+++", "---")):
            continue
        if line.startswith("@@"):
            # hunk 头的尾串是「所在函数」的签名：函数体内改动只有这里能看出导出名
            names.update(re.findall(r"\bb2_[A-Za-z0-9_]+", line.split("@@", 2)[-1]))
            continue
        if line[:1] in "+-":
            names.update(re.findall(r"\bb2_[A-Za-z0-9_]+", line))
    return sorted(names)


def pick(requested, tbl, cost, budget):
    want = set(requested)
    known = set().union(*(v["exports"] for v in tbl.values())) if tbl else set()
    uncovered = sorted(want - known)
    remain = want & known
    picks, total = [], 0.0
    pool = {r: v for r, v in tbl.items() if v["exports"] & remain}
    while remain and pool:
        best, best_ratio, best_gain, best_cost, best_src = None, -1.0, 0, 0.0, ""
        for rec, v in pool.items():
            gain = len(v["exports"] & remain)
            if not gain:
                continue
            c, src = cost_of(rec, tbl, cost)
            ratio = gain / c
            if ratio > best_ratio or (ratio == best_ratio and c < best_cost):
                best, best_ratio, best_gain, best_cost, best_src = rec, ratio, gain, c, src
        if best is None:
            break
        if total + best_cost > budget:
            break
        picks.append({"rec": best, "cost_secs": round(best_cost, 1), "cost_src": best_src,
                      "new_exports": sorted(tbl[best]["exports"] & remain),
                      "levels": tbl[best]["levels"]})
        remain -= tbl[best]["exports"]
        total += best_cost
        pool.pop(best, None)

    # 预算不够：把「要继续覆盖还差哪份、多少钱」算出来，不静默丢
    over = []
    while remain and pool:
        best = min(
            pool,
            key=lambda r: (cost_of(r, tbl, cost)[0] / max(1, len(tbl[r]["exports"] & remain)),
                           cost_of(r, tbl, cost)[0]))
        c, src = cost_of(best, tbl, cost)
        over.append({"rec": best, "cost_secs": round(c, 1), "cost_src": src,
                     "new_exports": sorted(tbl[best]["exports"] & remain)})
        remain -= tbl[best]["exports"]
        pool.pop(best, None)

    return {"requested": sorted(want), "picks": picks,
            "total_secs": round(total, 1), "budget": budget,
            "over_budget": over, "uncovered": uncovered}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exports", default="")
    ap.add_argument("--changed", default="", help="git 修订号：从该 rev 到工作树的 src/b2physics diff 里抓 b2_*")
    ap.add_argument("--budget", type=float, default=90.0)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--list", default="", help="列出名字含该子串且被录制观测的导出")
    a = ap.parse_args()

    tbl = load_table()
    if a.list:
        names = sorted({e for v in tbl.values() for e in v["exports"]})
        for n in names:
            if a.list in n:
                owners = [r for r, v in tbl.items() if n in v["exports"]]
                print("%-42s %d rec(s)" % (n, len(owners)))
        return 0

    requested = [x.strip() for x in a.exports.split(",") if x.strip()]
    if a.changed:
        requested += exports_from_diff(a.changed)
    requested = sorted(set(requested))
    if not requested:
        print("没有请求的导出（--exports 为空且 --changed 无 b2_* 改动）")
        return 0

    res = pick(requested, tbl, load_cost(), a.budget)
    if a.json:
        print(json.dumps(res, ensure_ascii=False, indent=1))
        return 0

    print("requested %d export(s), budget %.0fs" % (len(res["requested"]), a.budget))
    for p in res["picks"]:
        print("  PICK %-28s %6.1fs (%s) +%d  %s" % (
            p["rec"], p["cost_secs"], p["cost_src"], len(p["new_exports"]),
            ",".join(p["levels"]) or "-"))
    print("total %.1fs" % res["total_secs"])
    if res["over_budget"]:
        print("OVER BUDGET (还差这些才能覆盖):")
        for o in res["over_budget"]:
            print("  NEED %-28s %6.1fs (%s) +%d" % (
                o["rec"], o["cost_secs"], o["cost_src"], len(o["new_exports"])))
    if res["uncovered"]:
        print("UNCOVERED (没有录制观测过；走 B2PROXY_HOT=1 录制或合成契约探针):")
        for n in res["uncovered"]:
            print("  ", n)
    return 0


if __name__ == "__main__":
    sys.exit(main())
