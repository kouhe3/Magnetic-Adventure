#!/usr/bin/env python3
"""场景图元 JSONL 对拍：Python 模型 vs Pascal 移植（T6.4a-r-2d）。

用法:
    python tools/scene_from_lua.py --level 0 --ref ... --frame ... \
        --dump-objects work/obj_py_lvl00.jsonl
    build/scene_model/scenemodel_cli.exe work/lua_probe/lvl00.jsonl \
        work/pak_gametop work/obj_pas_lvl00.jsonl
    python tools/scenemodel_ab.py work/obj_py_lvl00.jsonl work/obj_pas_lvl00.jsonl

判据:
    行数相同（含首行 `_camera`），逐对象 `kind/asset/space/root` 相等、数值
    `x/y/angle/w/h/alpha` 相对差 ≤1e-4；退出码 0=PASS。

覆盖边界:
    - 只比 build() 的静态图元（不含从 ref 拟合的齿轮/摆臂相位、不含 GL 调用）；
    - Python 侧数值是 double，Pascal 侧按 `FloatToStrF(ffGeneral,9)` 落盘，
      容差留到 1e-4；跨关比较（拿错 level 的 dump）应当报 >0。
"""
from __future__ import annotations

import json
import sys

NUMERIC = ("x", "y", "angle", "w", "h", "alpha")
KEYS = ("kind", "asset", "space", "root")


def load(path):
    rows = []
    with open(path, encoding="utf-8", errors="replace") as fp:
        for line in fp:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def near(a, b, tol=1e-4):
    return abs(a - b) <= tol * max(1.0, abs(a), abs(b))


def compare(rows_a, rows_b):
    if not rows_a or not rows_b:
        return ["empty dump"]
    if (rows_a[0].get("kind") != "_camera"
            or rows_b[0].get("kind") != "_camera"):
        return ["missing _camera header"]
    bad = []
    if not (near(rows_a[0]["x"], rows_b[0]["x"])
            and near(rows_a[0]["y"], rows_b[0]["y"])):
        bad.append("camera %r vs %r" % (rows_a[0], rows_b[0]))
    n = min(len(rows_a), len(rows_b))
    for i in range(1, n):
        a, b = rows_a[i], rows_b[i]
        for k in KEYS:
            if a.get(k) != b.get(k):
                bad.append("#%d %s %r vs %r" % (i, k, a.get(k), b.get(k)))
        for k in NUMERIC:
            if not near(a.get(k, 0.0), b.get(k, 0.0)):
                bad.append("#%d %s %r vs %r" % (i, k, a.get(k), b.get(k)))
        if len(bad) > 8:
            break
    if len(rows_a) != len(rows_b):
        bad.append("count %d vs %d" % (len(rows_a), len(rows_b)))
    return bad


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        return 2
    a, b = load(sys.argv[1]), load(sys.argv[2])
    bad = compare(a, b)
    print("objects_a=%d objects_b=%d mismatches=%d"
          % (len(a) - 1, len(b) - 1, len(bad)))
    for line in bad[:8]:
        print("  " + line)
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
