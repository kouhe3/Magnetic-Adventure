"""从 B2FFI02 日志提取单个 body 的逐 step ApplyForce / ApplyTorque 时间线。

用法:
  python tools/force_timeline.py <log> --body-ptr N --id ID --first-step N
      --out force.txt [--torque torque.txt]

输出:
  force.txt  每行 `host_step id fx fy px py`
              （px/py = 原版 ApplyForce 的施力点，日志 m2 前两 float；
              4 列旧格式仍可读，宿主按 body 中心处理）
  torque.txt 每行 `host_step id torque`
  host_step = 原版 step_no - first_step + 1（step_no 是首次 b2_World_Step
  之前的调用记为 0，之后每有一次 Step 加 1）。

用途:
  把原版拖拽的每步力/扭矩原样喂给宿主（`HOST_MAG_FORCE` /
  `HOST_MAG_TORQUE`），再用 tools/step_ab.py 比 digest。这样把
  “力律”与“物理步”分开验证：力律由 F386 单独判，本工具只证宿主
  b2 步进在相同输入下复现原版轨迹。

覆盖边界:
  * 只导出非零调用（零力是 no-op）；
  * 只覆盖日志窗口内、且 map 到 host_step >= 1 的 step；
  * body 指针是进程内地址，必须与日志同一进程；
  * 不导出接触冲量/约束冲量，那些由 b2 内部处理。

失效条件:
  * B2FFI02 → 03，或 PRE2 记录布局改动；
  * 日志里 ApplyForce 的 body 不在 arg0（ABI 表变化）。
"""
import argparse
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import ffi  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("log")
    ap.add_argument("--body-ptr", type=lambda s: int(s, 0), required=True)
    ap.add_argument("--id", type=int, required=True)
    ap.add_argument("--first-step", type=int, required=True,
                    help="原版 step_no that maps to host step 1")
    ap.add_argument("--out", required=True)
    ap.add_argument("--torque", default=None)
    a = ap.parse_args()

    names = ffi.load_names()
    step = 0
    forces = []
    torques = []
    for kind, v in ffi.records(a.log):
        if kind != "pre":
            continue
        rid = v[1]
        name = names[rid] if 0 < rid < len(names) else ""
        if name == "b2_World_Step":
            step += 1
        elif name == "b2_Body_ApplyForce" and v[6] == a.body_ptr:
            fx, fy = struct.unpack("<2f", v[39][:8])
            px, py = struct.unpack("<2f", v[40][:8])
            if abs(fx) > 1e-12 or abs(fy) > 1e-12:
                forces.append((step, a.id, fx, fy, px, py))
        elif name == "b2_Body_ApplyTorque" and v[6] == a.body_ptr:
            t = struct.unpack("<f", struct.pack("<I", v[7]))[0]
            if abs(t) > 1e-12:
                torques.append((step, a.id, t))

    def host_step(s):
        return s - a.first_step + 1

    nf = 0
    with open(a.out, "w", encoding="utf-8") as f:
        for s, bid, fx, fy, px, py in forces:
            hs = host_step(s)
            if hs < 1:
                continue
            f.write("%d %d %.9g %.9g %.9g %.9g\n" % (hs, bid, fx, fy, px, py))
            nf += 1
    nt = 0
    if a.torque:
        with open(a.torque, "w", encoding="utf-8") as f:
            for s, bid, t in torques:
                hs = host_step(s)
                if hs < 1:
                    continue
                f.write("%d %d %.9g\n" % (hs, bid, t))
                nt += 1
    print("forces=%d torques=%d first_step=%d out=%s" %
          (nf, nt, a.first_step, a.out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
