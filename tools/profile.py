#!/usr/bin/env python3
"""读写游戏的玩家档案（%APPDATA%\\Magnet's Story\\hg_lmpgl.prf）。

格式：UTF-16LE，字节按 0xB8 单字节异或，内容是 <Player> 下的 key = "value" 文本。
用法:
  python tools/profile.py show
  python tools/profile.py set LastCompleteLevel 1
  python tools/profile.py set CompletedLevels "e0,e1"
  python tools/profile.py backup
"""
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


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "show"
    if cmd == "backup":
        dst = PROFILE + ".bak"
        shutil.copy2(PROFILE, dst)
        print(dst)
        return 0
    text = decode()
    if cmd == "show":
        print(text)
        return 0
    if cmd == "set":
        key, value = sys.argv[2], sys.argv[3]
        lines = text.splitlines()
        found = False
        for i, line in enumerate(lines):
            if "=" in line and line.split("=", 1)[0].strip() == key:
                lines[i] = f'{key} = "{value}"'
                found = True
        if not found:
            lines.insert(len(lines) - 1, f'{key} = "{value}"')
        encode("\n".join(lines) + "\n")
        print(f"{key} = {value}")
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
