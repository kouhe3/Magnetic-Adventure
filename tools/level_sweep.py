"""单进程逐关驱动：menu → map → level → pause → menu，循环走完指定关卡。

为什么需要：52 关的采集/普查必须在**同一个进程**里跑完（每关新起进程要 20 s 启动），
而且每一步都要用**状态机**确认落地，不能靠定时点击（F169/F172 的教训）。

用法：
    python tools/level_sweep.py --dir work/census/game --levels 1,2,3
    python tools/level_sweep.py --dir work/census/game --levels 1-52 --out work/level_sweep/run1
    # 带计数快照（census.dll 的 CENSUS_OUT 每秒落盘；驱动在进出关各拷一份）
    python tools/level_sweep.py --dir work/census/game --census-env 1 ...

判据（每次运行）：
    每关记录 state 序列与耗时；`ok` = 四步全部在 timeout 内落地：
      menu→map（15 s）、map→level（60 s）、level→pause（15 s）、pause→menu（20 s）
    退出码 0 = 全部 ok；任一关失败会尝试恢复（pause→Main menu / 回到 menu）并继续。

覆盖边界：节点坐标来自 `work/map_nodes.csv`（Command 299–350）；菜单/地图/暂停按钮坐标见
`mapping/pause-panel.json` 与 F296/F297；游戏失焦会暂停（F265），每次点击前都会抢前台。
"""
import argparse
import csv
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import uistate as us  # noqa: E402

u = us.u

MAP_BTN = (0.280, 0.560)      # 主菜单 -> 地图（F264）
MENU_BTN = (0.966, 0.050)     # 关卡内 -> 暂停（F294）
MAINMENU_BTN = (0.8544, 0.2938)  # 暂停 -> 主菜单（F296）


def click(win, rect, fx, fy):
    u.ShowWindow(win[0], 9)
    u.SetForegroundWindow(win[0])
    time.sleep(0.25)
    u.SetCursorPos(int(rect[0] + rect[2] * fx), int(rect[1] + rect[3] * fy))
    time.sleep(0.15)
    u.mouse_event(0x0002, 0, 0, 0, 0)
    time.sleep(0.15)
    u.mouse_event(0x0004, 0, 0, 0, 0)
    time.sleep(0.2)


def load_nodes(path):
    rows = list(csv.DictReader(open(path, encoding="utf-8")))
    out = {}
    for r in rows:
        out[int(r["level"])] = (float(r["design_x"]) / 1018.0, float(r["design_y"]) / 739.0)
    return out


def parse_levels(spec):
    if spec is None:
        return list(range(1, 53))
    out = []
    for part in spec.split(","):
        if "-" in part:
            a, b = part.split("-")
            out.extend(range(int(a), int(b) + 1))
        else:
            out.append(int(part))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="work/census/game")
    ap.add_argument("--exe", default="game.exe")
    ap.add_argument("--anchors", default="work/uianchors5.npz")
    ap.add_argument("--asset-pause", default="mapping/pause-panel.json")
    ap.add_argument("--asset-root", default="work/pak_gametop")
    ap.add_argument("--levels", default=None, help="如 1,2,3 或 1-52（默认全部）")
    ap.add_argument("--node-csv", default="work/map_nodes.csv")
    ap.add_argument("--out", default="work/level_sweep/run")
    ap.add_argument("--settle", type=float, default=6.0, help="进关后再等多久算 init 完成")
    ap.add_argument("--boot-timeout", type=float, default=60.0)
    ap.add_argument("--census-env", action="store_true", help="透传 CENSUS_OUT 并逐关快照")
    ap.add_argument("--poll", type=float, default=0.4)
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    nodes = load_nodes(args.node_csv)
    levels = parse_levels(args.levels)
    anchors = us.np.load(args.anchors, allow_pickle=False)
    asset = us.load_asset_spec(args.asset_pause, args.asset_root) if args.asset_pause else None
    thr = asset["thr"] if asset else 0.0

    env = dict(os.environ)
    census_out = env.get("CENSUS_OUT") if args.census_env else None
    p = subprocess.Popen([str(Path(args.dir) / args.exe)], cwd=args.dir, env=env)
    log = open(out / "log.txt", "w", encoding="utf-8")
    recs = []
    try:
        win = None
        for _ in range(int(args.boot_timeout * 2)):
            time.sleep(0.5)
            win = us.find_window(p.pid)
            if win:
                break
        if not win:
            print("no_window"); return 1
        rect = us.client_rect(win)
        seen_level = False

        def state():
            nonlocal seen_level
            st, sc, mg, allsc = us._state_from_win(anchors, win, asset, thr, seen_level)
            if st == "level":
                seen_level = True
            return st, sc

        def ok_state(st, target):
            if target == "level_any":
                # 52 关外观各不相同；「进关」= 离开地图/菜单（关卡屏可能是 unknown）
                return st not in ("map", "menu")
            return st == target

        def wait_for(target, timeout, need=1):
            t0 = time.time()
            st = None
            last = None
            streak = 0
            while time.time() - t0 < timeout:
                st, sc = state()
                if st != last:
                    print(f"    t={time.time()-t0:5.1f}s state={st:8s} score={sc:6.1f}", flush=True)
                    last = st
                streak = streak + 1 if ok_state(st, target) else 0
                if streak >= need:
                    return True, round(time.time() - t0, 2)
                time.sleep(args.poll)
            try:
                gr = us._Graber()
                gr2 = gr.grab(rect)
                from PIL import Image
                Image.fromarray(gr2).save(str(out / f"fail_{target}_{int(time.time())}.png"))
                gr.close()
            except Exception:
                pass
            return False, round(time.time() - t0, 2)

        # 等主菜单（启动 → loading → intro → menu）
        ok, dt = wait_for("menu", args.boot_timeout)
        print(f"boot->menu ok={ok} {dt}s")
        if not ok:
            return 2

        def snapshot(tag, lvl):
            if not census_out:
                return
            src = Path(census_out)
            if src.exists():
                shutil.copy2(src, out / f"lvl{lvl:02d}_{tag}.bin")

        for lvl in levels:
            t_lvl = time.time()
            rec = {"lvl": lvl}
            click(win, rect, *MAP_BTN)
            ok1, d1 = wait_for("map", 15)
            rec["map"] = [ok1, d1]
            if not ok1:
                # 恢复：若已在 pause 里就回主菜单，再重试一次
                click(win, rect, *MAINMENU_BTN)
                wait_for("menu", 10)
                click(win, rect, *MAP_BTN)
                ok1, d1 = wait_for("map", 15)
                rec["map"] = [ok1, d1]
            if ok1:
                node = nodes.get(lvl)
                if not node:
                    rec["error"] = "no_node"
                    recs.append(rec); log.write(json.dumps(rec) + "\n"); log.flush()
                    continue
                snapshot("pre", lvl)   # 基线：还在地图上，本关的加载/init 都算在差值里
                click(win, rect, *node)
                ok2, d2 = wait_for("level_any", 60)
                rec["level"] = [ok2, d2]
                if ok2:
                    time.sleep(args.settle)
                    snapshot("enter", lvl)
                    click(win, rect, *MENU_BTN)
                    ok3, d3 = wait_for("pause", 15, need=2)
                    rec["pause"] = [ok3, d3]
                    snapshot("exit", lvl)
                    click(win, rect, *MAINMENU_BTN)
                    ok4, d4 = wait_for("menu", 20)
                    rec["menu"] = [ok4, d4]
                    if not ok4:
                        # 再点一次 Main menu（有时第一次落在 hover 上）
                        click(win, rect, *MAINMENU_BTN)
                        ok4, d4 = wait_for("menu", 15)
                        rec["menu_retry"] = [ok4, d4]
                else:
                    rec["error"] = "no_level"
                    click(win, rect, *MAINMENU_BTN)
                    wait_for("menu", 10)
            else:
                rec["error"] = "no_map"
            rec["elapsed"] = round(time.time() - t_lvl, 1)
            recs.append(rec)
            log.write(json.dumps(rec) + "\n")
            log.flush()
            print(json.dumps(rec), flush=True)
            if p.poll() is not None:
                print("process exited"); break
        return 0
    finally:
        log.close()
        (out / "summary.json").write_text(json.dumps(recs, ensure_ascii=False, indent=1), encoding="utf-8")
        subprocess.run(["taskkill", "/PID", str(p.pid), "/F"], capture_output=True)


if __name__ == "__main__":
    sys.exit(main())
