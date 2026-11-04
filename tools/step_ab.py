"""逐 step 对比宿主物理轨迹与原版 B2FFI02 digest。

用法:
  python tools/step_ab.py <orig.bin> <host_step.log> --body-ptr N --host-id ID
      [--offset auto|N] [--tol 1e-6] [--show K]

输入:
  * orig.bin    —— 原版代理日志（B2FFI02）；kind=2 的 digest 记录给出
                   `ptr` 与 `px,py,angle`（tools/ffi.records）。
  * host_step.log —— 宿主 `TLevelScene.WriteStepDigest` 的输出，每行
                   `step id x y angle`。

对齐:
  host step 1 对应原版 digest 的 `1+offset`。`--offset auto` 用 host 第一步
  的位置去匹配最接近的原版 digest seq，取 `seq-1`。

判据:
  PASS = 选定 body 的逐 step 位置误差最大值 <= --tol（默认 1e-6，相对
  世界单位；F32 级一致时实测 ~6.6e-7）。角度单独报，不参与 PASS：
  原版同一步可能还有 ApplyTorque/接触滚动，力回放未覆盖。

覆盖边界:
  * 只比 digest 的前 13 个 float（ptr/flags/sleep/v/w/px/py/angle）；
  * 只比一个 body；只覆盖日志窗口内的 step；
  * body 指针是进程内地址，必须来自同一份日志。

失效条件:
  * 日志 magic 升级（B2FFI02 → 03）或 BodyDigest 布局改动；
  * 宿主 step digest 的列顺序/格式改动。
"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import ffi  # noqa: E402


def load_orig(path, ptr):
    rows = {}
    for kind, v in ffi.records(path):
        if kind != "digest":
            continue
        seq, bodies = v
        for b in bodies:
            if b[0] == ptr:
                rows[seq] = (b[6], b[7], b[8])
                break
    return rows


def load_host(path, host_id):
    rows = {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        p = line.split()
        if len(p) >= 5 and int(p[1]) == host_id:
            rows[int(p[0])] = (float(p[2]), float(p[3]), float(p[4]))
    return rows


def auto_offset(orig, host):
    if not host or not orig:
        return None
    first = host[min(host)]
    best = None
    for seq, pos in orig.items():
        d = ((pos[0] - first[0]) ** 2 + (pos[1] - first[1]) ** 2) ** 0.5
        if best is None or d < best[0]:
            best = (d, seq)
    return best[1] - 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("log")
    ap.add_argument("host")
    ap.add_argument("--body-ptr", type=lambda s: int(s, 0), required=True)
    ap.add_argument("--host-id", type=int, required=True)
    ap.add_argument("--offset", default="auto")
    ap.add_argument("--tol", type=float, default=1e-6)
    ap.add_argument("--show", type=int, default=6)
    a = ap.parse_args()

    orig = load_orig(a.log, a.body_ptr)
    host = load_host(a.host, a.host_id)
    if a.offset == "auto":
        off = auto_offset(orig, host)
    else:
        off = int(a.offset)
    if off is None:
        raise SystemExit("cannot align: empty digest or host log")

    worst_pos = (0.0, None)
    worst_ang = (0.0, None)
    first_bad = None
    compared = 0
    for i in sorted(host):
        j = i + off
        if j not in orig:
            continue
        hp, op = host[i], orig[j]
        dp = ((hp[0] - op[0]) ** 2 + (hp[1] - op[1]) ** 2) ** 0.5
        da = abs(hp[2] - op[2])
        compared += 1
        if dp > worst_pos[0]:
            worst_pos = (dp, (i, j))
        if da > worst_ang[0]:
            worst_ang = (da, (i, j))
        if dp > a.tol and first_bad is None:
            first_bad = (i, j, dp)

    print("offset=%d compared=%d max_pos=%.9g max_angle=%.9g" %
          (off, compared, worst_pos[0], worst_ang[0]))
    if worst_pos[1]:
        print("worst_pos step=%d orig=%d" % worst_pos[1])
    if worst_ang[1]:
        print("worst_angle step=%d orig=%d" % worst_ang[1])
    if first_bad:
        print("first_pos>tol step=%d orig=%d d=%.9g" % first_bad)
    for i in sorted(host)[:max(0, a.show)]:
        j = i + off
        if j in orig:
            hp, op = host[i], orig[j]
            print("  %d->%d host=(%.6f,%.6f,%.6f) orig=(%.6f,%.6f,%.6f)" %
                  (i, j, hp[0], hp[1], hp[2], op[0], op[1], op[2]))
    ok = compared > 0 and worst_pos[0] <= a.tol
    print("RESULT", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
