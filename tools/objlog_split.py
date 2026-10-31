"""把 objlog_session 的 JSONL 按 burst 切成一关一份，并与 work/lua_probe 的绑定调用序列对拍。

用法：
  python tools/objlog_split.py [--session work/objlog_session.jsonl]
                               [--probe-dir work/lua_probe] [--outdir work/session_levels]

判据：
  * 每个 burst 提取 `Add_*` 名字序列（去掉重复的 `Add_LevelMaterial/Add_AlphaHint` 之外的次序信息也保留）。
  * 先找**序列完全一致**的 probe 关（强匹配）；否则找计数一致且首个名字相同的；再否则记 UNMATCHED。
  * 输出 mapping.tsv：burst、对象数、匹配关卡（0-based probe 索引）、匹配方式、差异摘要。

probe 文件是 tools/lua_probe 的输出（0-based，`lvlNN.jsonl`，每行有 "fn" 字段）。
"""
import argparse
import json
import os
import re
import sys

HB = re.compile(r"^#HB\s+(\S+)")


def load_session(path):
    bursts = []
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        rec = json.loads(line)
        m = HB.match(rec["line"])
        if not m:
            continue
        b = rec["burst"]
        while len(bursts) < b:
            bursts.append([])
        bursts[b - 1].append(m.group(1))
    return bursts


def load_probe(d, n=52):
    out = {}
    for i in range(n):
        p = os.path.join(d, "lvl%02d.jsonl" % i)
        if not os.path.exists(p):
            continue
        tags = []
        for line in open(p, encoding="utf-8"):
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            fn = rec.get("call") or rec.get("fn") or rec.get("func") or rec.get("name")
            if isinstance(fn, str) and fn.startswith("Add_"):
                tags.append(fn)
        out[i] = tags
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--session", default="work/objlog_session.jsonl")
    ap.add_argument("--probe-dir", default="work/lua_probe")
    ap.add_argument("--outdir", default="work/session_levels")
    a = ap.parse_args()

    bursts = load_session(a.session)
    probe = load_probe(a.probe_dir)
    os.makedirs(a.outdir, exist_ok=True)

    rows = []
    used = set()
    for bi, tags in enumerate(bursts, 1):
        cands = [i for i, p in probe.items() if p == tags]
        how = "exact"
        if not cands:
            cands = [i for i, p in probe.items() if len(p) == len(tags) and p and p[0] == tags[0]]
            how = "count+first"
        if not cands:
            # probe 是 burst 的前缀：关卡脚本跑完后（dwell 期）又创建了额外对象
            cands = [i for i, p in probe.items() if tags[:len(p)] == p and len(p) > 0]
            how = "prefix+extra"
        if not cands:
            cands = [i for i, p in probe.items() if len(p) == len(tags)]
            how = "count"
        lvl = None
        if len(cands) == 1:
            lvl = cands[0]
        elif cands:
            lvl = next((i for i in cands if i not in used), cands[0])
            how += " (ambiguous %d)" % len(cands)
        if lvl is not None:
            used.add(lvl)
            with open(os.path.join(a.outdir, "lvl%02d.jsonl" % lvl), "w", encoding="utf-8") as fh:
                for t in tags:
                    fh.write(json.dumps({"fn": t}) + "\n")
        diff = ""
        if lvl is not None and how.startswith("prefix"):
            diff = "extra=%d" % (len(tags) - len(probe[lvl]))
        if lvl is not None and probe[lvl] != tags and not diff:
            n = min(len(probe[lvl]), len(tags))
            k = next((j for j in range(n) if probe[lvl][j] != tags[j]), n)
            diff = "first_diff=%d probe=%d burst=%d" % (k, len(probe[lvl]), len(tags))
        rows.append((bi, len(tags), lvl, how, diff))

    with open(os.path.join(a.outdir, "mapping.tsv"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("burst\tn\tlevel\tmatch\tnote\n")
        for r in rows:
            fh.write("%d\t%d\t%s\t%s\t%s\n" % (r[0], r[1], "-" if r[2] is None else r[2], r[3], r[4]))
    matched = sum(1 for r in rows if r[2] is not None and not r[4])
    print("bursts=%d matched_exact=%d unmatched=%d -> %s"
          % (len(rows), matched, sum(1 for r in rows if r[2] is None), os.path.join(a.outdir, "mapping.tsv")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
