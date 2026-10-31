"""逐行比较两份绑定 JSONL 的 call+args（忽略 ret，因为两侧桩实现不同）。

用法:
    python tools/lua_bind_ab.py work/lua_probe/lvl00.jsonl C:/tmp/magnet_bind.jsonl

判据:
    `mismatches=0` 且行数相同（exit 0）。`ret` 不参与比较：
    C++ lua_probe 与 FPC 宿主的桩都只是约定值，不是原版语义（F224/F241）。

覆盖边界:
    - 只比脚本层调用序与实参；不证明绑定内部读取/工厂调用的正确性。
    - 数值按 JSON 解析后比较（2 与 2.0 视为相等）；字符串逐字节。
"""
import json
import sys


def load(path):
    rows = []
    with open(path, encoding="utf-8", errors="replace") as fp:
        for line in fp:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def is_num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def val_eq(a, b):
    if is_num(a) and is_num(b):
        return abs(a - b) <= 1e-6 * max(1.0, abs(a), abs(b))
    return a == b


def args_eq(a, b):
    return len(a) == len(b) and all(val_eq(x, y) for x, y in zip(a, b))


def main():
    if len(sys.argv) != 3:
        print("usage: python tools/lua_bind_ab.py <a.jsonl> <b.jsonl>")
        return 2
    a = load(sys.argv[1])
    b = load(sys.argv[2])
    n = min(len(a), len(b))
    bad = 0
    first = None
    for i in range(n):
        if a[i].get("call") != b[i].get("call") or not args_eq(a[i].get("args", []), b[i].get("args", [])):
            bad += 1
            if first is None:
                first = (i, a[i], b[i])
    print("lines_a=%d lines_b=%d compared=%d mismatches=%d" % (len(a), len(b), n, bad))
    if first is not None:
        print("first_diff=", first)
    return 0 if (bad == 0 and len(a) == len(b)) else 1


if __name__ == "__main__":
    sys.exit(main())
