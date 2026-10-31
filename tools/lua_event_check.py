"""核对事件派发竖切（T6.3 / OnAddContact）的绑定 JSONL 产物。

用法:
    python tools/lua_event_check.py work/lua_probe/lvl49.jsonl C:/tmp/magnet_evt/lvl49.jsonl \
        [--objlog work/objlog_lvl49.jsonl]
    python tools/lua_event_check.py work/lua_probe/lvl49.jsonl C:/tmp/magnet_evt/lvl49_neg.jsonl \
        --no-tail

判据（全部满足才 PASS，exit 0）:
  1. 前缀：触发前的调用与 `work/lua_probe/lvl49.jsonl` 的 call+args 逐条相同
     —— 事件派发不得改动 init 序列。
  2. 追加段固定 5 条且顺序相同：
       Set_JointLimits, Get_ScrObjPos, Add_JointSimpleRevolute,
       Set_JointLimits, Add_JointSimpleGear
     来自 `work/pak_gametop/lvl_e7.lua:91` 的 `gLSystembBigDialOnAddContact`
     （UnLockSystem → 取坐标 → 两个工厂调用，F272）。
  3. 追加段的 2 个 Add_* 名字与顺序 == objlog burst1 末尾 2 条（原版实跑，F272）。
  4. `Add_JointSimpleGear` 末参 == GearRad/Ratio == 2.4/(6*245/256)（相对 1e-9）。
  5. `Add_JointSimpleRevolute` 实参 [0] == 前面 `Get_ScrObjPos` 的实参，
     [1] == 触发时传入的 Body2 对象 id。

`--no-tail`：用于负例——事件已派发但 Lua 守卫不成立（如 Body2 不是 gear、
或 State 不在 1/2）时，JSONL 必须与 init 参考**逐条相同、无追加**。

覆盖边界:
    - 只覆盖「Attach 登记 + 事件派发 + 回调执行」；真实接触由物理层产生，
      本竖切用 HOST_LUA_FIRE 注入同一事件（见 src/host_lcl/luaevents.pas）。
    - 不证明工厂语义（Add_* 仍返回递增 id），也不覆盖其它事件（OnMove/OnRotate/OnTimer）。
"""
import argparse
import json
import sys

EXPECT_TAIL = [
    "Set_JointLimits",
    "Get_ScrObjPos",
    "Add_JointSimpleRevolute",
    "Set_JointLimits",
    "Add_JointSimpleGear",
]
RATIO = 6 * 245 / 256.0
GEAR_RAD = 2.4
EXPECT_GEAR_ARG = GEAR_RAD / RATIO


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


def val_eq(a, b, tol=1e-6):
    if is_num(a) and is_num(b):
        return abs(a - b) <= tol * max(1.0, abs(a), abs(b))
    return a == b


def row_eq(a, b):
    if a["call"] != b["call"]:
        return False
    aa, ba = a.get("args") or [], b.get("args") or []
    return len(aa) == len(ba) and all(val_eq(x, y) for x, y in zip(aa, ba))


def objlog_factory_tail(path, count=2):
    rows = load(path)
    burst1 = [r for r in rows if r.get("burst") == 1]
    names = [r["line"].split()[1] for r in burst1]
    add = [n for n in names if n.startswith("Add_")]
    return add[-count:] if count else []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("probe", help="init 参考（tools/lua_probe 产物）")
    ap.add_argument("fired", help="HOST_LUA_FIRE 后的宿主 JSONL")
    ap.add_argument("--objlog", default="", help="原版 objlog 记录（可选，校验 factory 名字序）")
    ap.add_argument("--no-tail", action="store_true",
                    help="负例：断言事件触发后没有任何追加调用（与 probe 逐条相同）")
    args = ap.parse_args()

    probe = load(args.probe)
    fired = load(args.fired)
    fails = []

    if args.no_tail:
        if len(fired) != len(probe):
            fails.append("expected no appended calls: probe=%d fired=%d" %
                         (len(probe), len(fired)))
        if len(fired) >= len(probe) and not all(
                row_eq(probe[i], fired[i]) for i in range(len(probe))):
            bad = next(i for i in range(len(probe)) if not row_eq(probe[i], fired[i]))
            fails.append("prefix mismatch at call %d: %r vs %r" %
                         (bad + 1, probe[bad], fired[bad]))
        if fails:
            for f in fails:
                print("FAIL", f)
            print("PASS 0/1")
            return 1
        print("tail=0 calls=%d (guard rejected, identical to init)" % len(fired))
        print("PASS 1/1")
        return 0

    if len(fired) <= len(probe):
        fails.append("no appended calls: probe=%d fired=%d" % (len(probe), len(fired)))
        tail = []
    else:
        if not all(row_eq(probe[i], fired[i]) for i in range(len(probe))):
            bad = next(i for i in range(len(probe)) if not row_eq(probe[i], fired[i]))
            fails.append("prefix mismatch at call %d: %r vs %r" %
                         (bad + 1, probe[bad], fired[bad]))
        tail = fired[len(probe):]

    names = [r["call"] for r in tail]
    if names and names != EXPECT_TAIL:
        fails.append("tail calls %r != %r" % (names, EXPECT_TAIL))

    adds = [r for r in tail if r["call"].startswith("Add_")]
    if args.objlog:
        want = objlog_factory_tail(args.objlog)
        got = [r["call"] for r in adds]
        if got != want:
            fails.append("factory names %r != objlog tail %r" % (got, want))

    if adds:
        gear = adds[-1]
        if gear["call"] == "Add_JointSimpleGear":
            got = (gear.get("args") or [None])[-1]
            if not (is_num(got) and val_eq(got, EXPECT_GEAR_ARG, 1e-9)):
                fails.append("gear ratio %r != %.12f" % (got, EXPECT_GEAR_ARG))
        rev = next((r for r in adds if r["call"] == "Add_JointSimpleRevolute"), None)
        scr = next((r for r in tail if r["call"] == "Get_ScrObjPos"), None)
        if rev and scr:
            ra, sa = rev.get("args") or [], scr.get("args") or []
            if not ra or not sa or ra[0] != sa[0]:
                fails.append("revolute arg0 %r != Get_ScrObjPos arg0 %r" % (ra[:1], sa[:1]))
            if len(ra) < 2 or not is_num(ra[1]) or ra[1] < 1001:
                fails.append("revolute arg1 %r is not an object id" % (ra[1:2],))

    if fails:
        for f in fails:
            print("FAIL", f)
        print("PASS 0/1")
        return 1
    print("tail=%d adds=%d ratio=%.12f" % (len(tail), len(adds), EXPECT_GEAR_ARG))
    print("PASS 1/1")
    return 0


if __name__ == "__main__":
    sys.exit(main())
