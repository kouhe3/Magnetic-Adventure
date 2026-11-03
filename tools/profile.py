#!/usr/bin/env python3
"""读写/比较游戏的玩家档案（%APPDATA%\\Magnet's Story\\hg_lmpgl.prf）。

格式：UTF-16LE，字节按 0xB8 单字节异或，内容是若干 <Player> 块；
每块 key = "value"。档案可以有多名玩家（例如 ooo 与 Active="1" 的 KKK）。

用法:
  python tools/profile.py show [--file PATH]
  python tools/profile.py players [--file PATH]
  python tools/profile.py get KEY [--file PATH] [--player NAME]
  python tools/profile.py set KEY VALUE [--file PATH] [--player NAME]
  python tools/profile.py diff A B [--player NAME]
  python tools/profile.py backup [--file PATH]

玩家选择：--player NAME 精确匹配 UserName；省略时，单玩家档案直接用该玩家，
多玩家档案用 Active="1" 的那个，没有 Active 则报错（不会猜第一个）。
diff 按玩家比较 key/value；完全相同退出 0，有差异退出 1 并打印差异行。

写操作默认写回真实档案；测试请用 --file 指向 work/ 下的副本。
"""
import argparse
import os
import shutil
import sys

PROFILE = os.path.join(os.environ["APPDATA"], "Magnet's Story", "hg_lmpgl.prf")
KEY = 0xB8


def decode(path=PROFILE):
    b = open(path, "rb").read()
    if b[:2] != b"\xff\xfe":
        raise ValueError("not UTF-16LE BOM")
    units = [b[i] | (b[i + 1] << 8) for i in range(2, len(b) - 1, 2)]
    return "".join(chr((u & 0xFF) ^ KEY) for u in units)


def encode(text, path=PROFILE):
    out = bytearray(b"\xff\xfe")
    for ch in text:
        out += bytes([ord(ch) ^ KEY, 0])
    open(path, "wb").write(out)


def parse(text):
    data = {}
    for line in text.splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            data[k.strip()] = v.strip().strip('"')
    return data


def blocks(text):
    """Return [(start_line, end_line, {key: value})] for each <Player> block."""
    lines = text.splitlines()
    out = []
    start = None
    for i, line in enumerate(lines):
        s = line.strip().lower()
        if s == "<player>":
            start = i
        elif s == "</player>" and start is not None:
            data = {}
            for j in range(start + 1, i):
                if "=" in lines[j]:
                    k, v = lines[j].split("=", 1)
                    data[k.strip()] = v.strip().strip('"')
            out.append((start, i, data))
            start = None
    return lines, out


def pick(lines, spans, player):
    """Pick the target <Player> block (see module docstring)."""
    if player is not None:
        for start, end, data in spans:
            if data.get("UserName") == player:
                return start, end, data
        raise SystemExit("player %r not found" % player)
    if len(spans) == 1:
        return spans[0]
    active = [b for b in spans if b[2].get("Active") == "1"]
    if len(active) == 1:
        return active[0]
    raise SystemExit("multiple players and no unique Active; pass --player")


def read(path):
    return decode(path)


def cmd_show(a):
    text = read(a.file)
    print(text, end="" if text.endswith("\n") else "\n")
    return 0


def cmd_players(a):
    _, spans = blocks(read(a.file))
    for start, end, data in spans:
        print("%s%s" % (data.get("UserName", "?"),
                        " (active)" if data.get("Active") == "1" else ""))
    return 0 if spans else 1


def cmd_get(a):
    _, spans = blocks(read(a.file))
    start, end, data = pick(None, spans, a.player)
    if a.key in data:
        print(data[a.key])
        return 0
    print("%s: no such key" % a.key, file=sys.stderr)
    return 1


def cmd_set(a):
    text = read(a.file)
    lines, spans = blocks(text)
    start, end, data = pick(lines, spans, a.player)
    new = '%s = "%s"' % (a.key, a.value)
    for j in range(start + 1, end):
        if "=" in lines[j] and lines[j].split("=", 1)[0].strip() == a.key:
            lines[j] = new
            break
    else:
        lines.insert(end, new)
    encode("\n".join(lines) + "\n", a.file)
    print("%s = %s (%s)" % (a.key, a.value, data.get("UserName", "?")))
    return 0


def cmd_diff(a):
    pa = {d.get("UserName", "?"): d for _, _, d in blocks(read(a.a))[1]}
    pb = {d.get("UserName", "?"): d for _, _, d in blocks(read(a.b))[1]}
    if a.player is not None:
        if a.player not in pa or a.player not in pb:
            print("player %r missing in %s" % (a.player,
                  a.a if a.player not in pa else a.b), file=sys.stderr)
            return 1
        pa = {a.player: pa[a.player]}
        pb = {a.player: pb[a.player]}
    diffs = []
    for name in sorted(set(pa) | set(pb)):
        if name not in pa:
            diffs.append("+ player %s" % name)
            continue
        if name not in pb:
            diffs.append("- player %s" % name)
            continue
        for k in sorted(set(pa[name]) | set(pb[name])):
            va, vb = pa[name].get(k, "<missing>"), pb[name].get(k, "<missing>")
            if va != vb:
                diffs.append("%s.%s: %r -> %r" % (name, k, va, vb))
    for line in diffs:
        print(line)
    return 0 if not diffs else 1


def cmd_backup(a):
    dst = a.file + ".bak"
    shutil.copy2(a.file, dst)
    print(dst)
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    def add_file(p, default=PROFILE):
        p.add_argument("--file", default=default)

    p = sub.add_parser("show")
    add_file(p)
    p.set_defaults(func=cmd_show)
    p = sub.add_parser("players")
    add_file(p)
    p.set_defaults(func=cmd_players)
    p = sub.add_parser("get")
    p.add_argument("key")
    add_file(p)
    p.add_argument("--player")
    p.set_defaults(func=cmd_get)
    p = sub.add_parser("set")
    p.add_argument("key")
    p.add_argument("value")
    add_file(p)
    p.add_argument("--player")
    p.set_defaults(func=cmd_set)
    p = sub.add_parser("diff")
    p.add_argument("a")
    p.add_argument("b")
    p.add_argument("--player")
    p.set_defaults(func=cmd_diff)
    p = sub.add_parser("backup")
    add_file(p)
    p.set_defaults(func=cmd_backup)

    a = ap.parse_args()
    return a.func(a)


if __name__ == "__main__":
    sys.exit(main())
