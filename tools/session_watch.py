"""单进程手动采集的监听器。

用法：
  python tools/session_watch.py --log work/session.log --out work/session_capture.jsonl

它轮询 headless 的日志文件，把每条 `#HB` 行加上墙钟时间戳写入 JSONL；
相邻两行间隔 > --gap 秒就开一个新 burst（= 新的一关的 init 期），
并在 burst 结束时打印该 burst 的对象数。采集结束后用 burst 切分成逐关数据。

不点击、不切前台——用户自己操作游戏。
"""
import argparse
import json
import os
import re
import time

RX = re.compile(r"^#HB\s+(\S+)\s+([0-9A-Fa-f]+)\s+([0-9A-Fa-f]+)\s+([0-9A-Fa-f]+)\s+([0-9A-Fa-f]+)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--gap", type=float, default=1.2, help="seconds of silence that starts a new burst")
    ap.add_argument("--idle-stop", type=float, default=0.0, help="stop after this many idle seconds (0 = never)")
    a = ap.parse_args()

    out = open(a.out, "w", encoding="utf-8")
    seen = 0
    burst = 0
    count = 0
    last_t = 0.0
    last_line_t = 0.0
    print("watching %s" % a.log, flush=True)
    while True:
        try:
            with open(a.log, encoding="utf-8", errors="replace") as fh:
                lines = fh.read().splitlines()
        except FileNotFoundError:
            time.sleep(0.1)
            continue
        new = lines[seen:]
        for line in new:
            seen += 1
            m = RX.match(line.strip())
            if not m:
                continue
            t = time.time()
            if t - last_t > a.gap:
                if burst:
                    print("burst %d done: %d objects" % (burst, count), flush=True)
                burst += 1
                count = 0
            last_t = t
            count += 1
            out.write(json.dumps({"t": round(t, 3), "burst": burst, "tag": m.group(1),
                                  **({"name": ""})}) + "\n")
            out.flush()
        if new:
            last_line_t = time.time()
        if a.idle_stop and last_line_t and time.time() - last_line_t > a.idle_stop:
            print("burst %d done: %d objects (idle stop)" % (burst, count), flush=True)
            return
        time.sleep(0.1)


if __name__ == "__main__":
    main()
