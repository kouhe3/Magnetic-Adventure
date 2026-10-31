"""单进程全量采集：起原版 → 注入 objlog.dll → 带时间戳追踪日志 → 按静默切分 burst。

用法：
  python tools/objlog_session.py --log work/objlog_session.txt --out work/objlog_session.jsonl

它不点击、不抢前台：由用户自己进 Map 点关卡。检查点：
  * 每行 `#HB` 记墙钟时间；相邻两行间隔 > --gap 秒视为新的一关（burst）。
  * burst 结束时打印对象数，供与 work/lua_probe/ 的 Add_* 计数对拍。
  * Ctrl+C（或杀掉进程）后文件已完整落盘；再用 tools/objlog_split.py 切分成逐关 JSONL。

注入需要 32 位 Python（objlog.dll 是 x86）：内部以子进程调用 tools/inject_dll.py。
"""
import argparse
import os
import subprocess
import sys
import time

import level_capture as lc
import uistate as us

PY32 = os.environ.get("PY32", r"C:\Users\K\.local\bin\python3.12.exe")
GAME_DIR = r"C:\tmp\Magnetic Adventure\work\winprobe_game"
DLL = r"C:\tmp\Magnetic Adventure\build\Release\objlog.dll"
INJECT = r"C:\tmp\Magnetic Adventure\tools\inject_dll.py"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--gap", type=float, default=1.2)
    ap.add_argument("--idle", type=float, default=180.0, help="idle seconds before auto-stop")
    ap.add_argument("--game-dir", default=GAME_DIR)
    a = ap.parse_args()
    a.log = os.path.abspath(a.log)
    a.out = os.path.abspath(a.out)

    if os.path.exists(a.log):
        os.remove(a.log)
    env = dict(os.environ)
    env["OBJLOG"] = a.log
    p = subprocess.Popen([a.game_dir + r"\game.exe"], cwd=a.game_dir, env=env)
    print("game pid", p.pid, flush=True)
    win = None
    for _ in range(300):
        win = us.find_window(p.pid)
        if win:
            break
        time.sleep(0.2)
    if win:
        lc.force_fg(win[0])          # 游戏 WM_KILLFOCUS 会自动暂停；从后台服务启动时必须先给焦点
        print("focus", flush=True)
    print("menu:", lc.wait_menu(p.pid, 60), flush=True)
    r = subprocess.run([PY32, INJECT, str(p.pid), DLL], capture_output=True, text=True)
    print("inject:", r.stdout.strip() or r.stderr.strip(), flush=True)
    if not os.path.exists(a.log):
        print("objlog 未创建，注入失败", flush=True)
        return 2

    out = open(a.out, "w", encoding="utf-8")
    seen = 0
    burst = 0
    count = 0
    last_t = 0.0
    last_line_t = time.time()
    print("recording… 由用户点击关卡；静默 %.1fs 切分" % a.gap, flush=True)
    try:
        while True:
            with open(a.log, encoding="utf-8", errors="replace") as fh:
                lines = fh.read().splitlines()
            for line in lines[seen:]:
                seen += 1
                if not line.startswith("#HB "):
                    continue
                t = time.time()
                if t - last_t > a.gap:
                    if burst:
                        print("burst %d: %d objects" % (burst, count), flush=True)
                    burst += 1
                    count = 0
                last_t = t
                count += 1
                out.write('{"t": %.3f, "burst": %d, "line": %s}\n'
                          % (t, burst, __import__("json").dumps(line)))
                out.flush()
                last_line_t = t
            if time.time() - last_line_t > a.idle:
                print("idle %.0fs，自动结束" % a.idle, flush=True)
                break
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        if burst:
            print("burst %d: %d objects" % (burst, count), flush=True)
        out.close()
        subprocess.run(["taskkill", "/PID", str(p.pid), "/F"], capture_output=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
