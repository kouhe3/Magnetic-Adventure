"""一条命令跑完当前所有机器可判的门禁，输出 PASS/FAIL 表 + 每个门禁的耗时。

为什么要有它：迭代速度卡在测试速度上时，第一瓶颈通常是**每次都要人记命令、人读输出**。
这个脚本把已有门禁固定成一套：判定口径写死在这里，输出只有表格与首个分歧。

用法：
    python tools/verify.py            # 快速集（约 1 分钟，不含全量物理重放）
    python tools/verify.py --full     # 追加 52 份录制的全量重放（8 路并行，约 17 分钟）
    python tools/verify.py --only window,exports

判据（每项都是"能产生反例"的，不是"跑通即通过"）：
    exports:b2      build/Release/b2Physics.dll 导出 87/87，missing/extra/ordinal_mismatch 全 0
    exports:squall  build/Release/Squall.dll 导出 99/99
    window          tools/wincompare.py：原版 vs 自建宿主 15 个窗口字段 diffs=0
    squall:contract 17 个宿主导入的 20 步契约探针，两侧逐项相同
    squall:decode   35 个 pak 内 OGG 的解码元数据两侧相同
    physics:sample  抽样录制的 FFI 重放 bounded=PASS 且 bodies_bad 不超过该录制的 A/A 地板
    physics:full    （--full）52 份全量，写 work/sweep.jsonl 并重生成 docs/levels.md

覆盖边界：不含"人眼看画面/听声音"的项目（像素 diff、PCM 波形），那些要么在别的工具里
（audio_capture/audio_diff、frame_probe），要么还没建（T4.2 的 GL 调用 diff）。
"""
import argparse
import os
import re
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY32 = os.environ.get("PY32") or (
    r"C:/Users/K/.local/bin/python3.12.exe"
    if os.path.exists(r"C:/Users/K/.local/bin/python3.12.exe") else sys.executable)

# 抽样原则：步数最少的可判定录制（重放快 + 覆盖加载期与常规关）。
# 别把 12k 步的录制放进快集——单份就要好几分钟，"快集"就失去意义。
SAMPLE_RECS = ["rec_20261029_135715", "rec_20261029_135534", "rec_20261029_135616"]
BUILD = os.path.join(ROOT, "build", "Release")
ORACLE = os.path.join(ROOT, "bin", "gametop")


def run(cmd, timeout=900):
    t0 = time.time()
    p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=timeout)
    return p.returncode, (p.stdout or "") + (p.stderr or ""), time.time() - t0


def check_exports(dll, csv=None):
    cmd = [sys.executable, "tools/check_exports.py", dll] + ([csv] if csv else [])
    rc, out, dt = run(cmd)
    m = re.search(r"missing=(\d+)\s+extra=(\d+)\s+ordinal_mismatch=(\d+)", out)
    ok = rc == 0 and m and all(v == "0" for v in m.groups())
    return ok, (out.strip().splitlines() or [""])[-1], dt


def check_window():
    rc, out, dt = run([sys.executable, "tools/wincompare.py",
                       "--orig", "work/winprobe_game", "--ours", "build/Release"])
    m = re.search(r"diffs=(\d+)", out)
    ok = rc == 0 and m and m.group(1) == "0"
    return ok, (m.group(0) if m else out.strip().splitlines()[-1:] or [""]), dt


def check_contract():
    rc, out, dt = run([PY32, "tools/squall_contract.py",
                       "bin/gametop/Squall.dll", "build/Release/Squall.dll"])
    ok = rc == 0
    return ok, "rc=%d" % rc, dt


def check_decode():
    rc, out, dt = run([PY32, "tools/squall_decode_ab.py",
                       "bin/gametop/Squall.dll", "build/Release/Squall.dll", "work/pak_baseline"])
    m = re.search(r"diffs=(\d+)", out)
    ok = rc == 0 and m and m.group(1) == "0"
    return ok, (m.group(0) if m else "rc=%d" % rc), dt


def check_physics_sample():
    # sweep 逐份跑，行写回 work/sweep.jsonl；这里只判定抽样行是否 PASS
    for rec in SAMPLE_RECS:
        run([PY32, "tools/sweep.py", "--only", rec], timeout=900)
    import json
    rows = {}
    path = os.path.join(ROOT, "work", "sweep.jsonl")
    if not os.path.exists(path):
        return False, "no sweep.jsonl", 0.0
    for line in open(path, encoding="utf-8"):
        try:
            r = json.loads(line)
        except Exception:
            continue
        rows[r.get("rec")] = r
    bad = []
    for rec in SAMPLE_RECS:
        r = rows.get(rec)
        if not r:
            bad.append("%s: 缺行" % rec)
        elif r.get("verdict") not in ("PASS",) and not r.get("ok"):
            bad.append("%s: %s" % (rec, r.get("verdict")))
    return (not bad), ("; ".join(bad) if bad else "3/3 PASS"), 0.0


def check_e2e():
    """无人值守跑一遍 Introduction（会改存档，前后自动备份/还原）。"""
    import shutil
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    import profile as saveprofile
    bak = saveprofile.PROFILE + ".verify.bak"
    shutil.copy2(saveprofile.PROFILE, bak)
    try:
        before = saveprofile.parse(saveprofile.decode()).get("LastCompleteLevel")
        subprocess.run([sys.executable, "tools/profile.py", "set", "LastCompleteLevel", "0"],
                       cwd=ROOT, capture_output=True)
        rc, out, dt = run([sys.executable, "tools/e2e_tutorial.py",
                           "--dir", "work/winprobe_game",
                           "--anchors", "work/uianchors.npz", "--clicks", "40",
                           "--exit-mode", "kill"], timeout=600)
        after = saveprofile.parse(saveprofile.decode()).get("LastCompleteLevel")
        ok = rc == 0 and after != "0"
        return ok, "rc=%d progress 0->%r (原值 %r)" % (rc, after, before), dt
    finally:
        shutil.copy2(bak, saveprofile.PROFILE)


def check_physics_full():
    rc, out, dt = run([PY32, "tools/sweep.py"], timeout=3600)
    rc2, out2, dt2 = run([sys.executable, "tools/report_sweep.py", "--write"], timeout=300)
    ok = rc == 0 and rc2 == 0
    return ok, ("sweep rc=%d report rc=%d" % (rc, rc2)), dt + dt2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--full", action="store_true", help="追加全量物理重放")
    ap.add_argument("--e2e", action="store_true", help="追加无人值守跑一关（会改存档，前后自动还原）")
    ap.add_argument("--only", default="", help="逗号分隔的门禁名")
    args = ap.parse_args()

    if not os.path.isdir(ORACLE):
        print("缺 %s（bin/ 不入库，需自行恢复）" % ORACLE)
        return 2

    checks = [
        ("exports:b2", lambda: check_exports(os.path.join(BUILD, "b2Physics.dll"))),
        ("exports:squall", lambda: check_exports(os.path.join(BUILD, "Squall.dll"),
                                                 "mapping/squall-exports.csv")),
        ("window", check_window),
        ("squall:contract", check_contract),
        ("squall:decode", check_decode),
        ("physics:sample", check_physics_sample),
    ]
    if args.full:
        checks.append(("physics:full", check_physics_full))
    if args.e2e or any(n.startswith("e2e:") for n in (args.only.split(",") if args.only else [])):
        checks.append(("e2e:introduction", check_e2e))
    if args.only:
        want = {s.strip() for s in args.only.split(",") if s.strip()}
        checks = [c for c in checks if c[0] in want]

    print("%-16s %-6s %-8s %s" % ("gate", "result", "secs", "detail"))
    fails = 0
    for name, fn in checks:
        try:
            ok, detail, dt = fn()
        except Exception as e:  # noqa
            ok, detail, dt = False, "exception: %s" % e, 0.0
        if not ok:
            fails += 1
        print("%-16s %-6s %-8.1f %s" % (name, "PASS" if ok else "FAIL", dt, detail))
    print("\ngates=%d fail=%d" % (len(checks), fails))
    return 0 if fails == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
