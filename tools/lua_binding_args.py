"""从 144 个 Lua 绑定的反汇编恢复参数表，产出 mapping/lua-binding-args.csv。

用法:
    # 1) 在 IDA MCP 里导出反汇编（一次性，产物 work/lua_bindings_asm.json）
    #    code = open(r"tools/ida_lua_asm.py", encoding="utf-8").read()
    # 2) 离线解析
    python tools/lua_binding_args.py
    python tools/lua_binding_args.py --check-probe work/lua_probe_e0.jsonl work/lua_probe_e1.jsonl
    python tools/lua_binding_args.py --check-probe          # 默认扫 work/lua_probe*.jsonl

产物:
    mapping/lua-binding-args.csv   每绑定一行：args DSL / ret / factories / status
    work/lua_binding_args.json     完整结构（每次 helper 调用的原始寄存器/栈记录）

args DSL:
    `<idx>:<kind>=<default>`，多条用 `;` 分隔；动态段写 `<from>..<to_expr>:<kind>=<default>`。
    kind ∈ int/float/str/any；default 为常量、`none`（helper 缺省时不写）、或 `?`（未识别）。

判据:
    stdout `rows=144 ok=.. noargs=.. dynamic=.. conflicts=0`；
    --check-probe 追加 `probe_calls=.. kind_mismatch=0 arity_gt=0`（语料只覆盖 47/144，作交叉验证）。

覆盖边界:
    - 只解析寄存器/栈上的直接常量；动态索引（循环读参）只有两个已知形态，写在 SPECIAL。
    - `none` 表示 helper 在参数缺失时不写变量（调用方栈值），不是 0。
    - factories 只记直接 `call sub_58xxxx/sub_59xxxx`；虚调用（`[reg+off]`）静态不可见。
    - j_lua_type/j_lua_tonumber/j_lua_tolstring 的直接读取按 `any/int/str` 记，类型分支不展开。

依据: docs/facts.md F201（144/144 反编译 + helper 语义）、F239（参数表）。
"""
import argparse
import collections
import glob
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASM_JSON = os.path.join(ROOT, "work", "lua_bindings_asm.json")
BINDINGS_CSV = os.path.join(ROOT, "mapping", "lua-bindings.csv")
OUT_CSV = os.path.join(ROOT, "mapping", "lua-binding-args.csv")
OUT_JSON = os.path.join(ROOT, "work", "lua_binding_args.json")

# helper 语义（F201 + 2026-10-31 反汇编复核）
#   slots4 : L@EAX, base@EDX, slot0@ECX, [esp]=float default, s1/s2/s3 指针；槽0 走 int 截断
#   slots3 : L@EAX, base@EDX, slot0@ECX, s1/s2 指针；全 float，缺省不写
#   optnum : L@EAX, idx@EDX, [esp]=float default
#   optint : L@EAX, idx@EDX, default@ECX
#   optstr : L@EAX, idx@EDX, default@ECX（lua_tolstring）
#   objattr_int / strarg : L@EAX, idx@EDX，无默认值
HELPERS = {
    "sub_596C50": "slots4",
    "sub_596BA0": "slots3",
    "sub_596900": "optnum",
    "sub_5969F0": "optint",
    "sub_596940": "optstr",
    "sub_598990": "objattr_int",
    "sub_595D20": "strarg",
}
KIND = {
    "slots4": "slots4", "slots3": "slots3", "optnum": "float",
    "optint": "int", "optstr": "str", "objattr_int": "int", "strarg": "str",
}

# 动态索引：汇编里的索引是循环变量，不是立即数。
#   Do_Command            00596B2C-00596B51：i=0..arg3-1 读 idx=4+i
#   Attach_ShapePolygon   0059B2EF-0059B339：i=0..arg5-1 读 idx=6+2i / 7+2i
#   Add_Rope              005976C2-0059771A：idx=5 起循环读 number，直到 lua_type!=number
# name -> (from, to_expr | None, kind, default)
SPECIAL = {
    "Do_Command": [(4, "3+arg3", "float", "0")],
    "Attach_ShapePolygon": [(6, "5+2*arg5", "float", "0")],
    "Add_Rope": [(5, None, "float", "none")],
}

# 脚本多传、函数不读的已知例外（逐个核对过反汇编）；不算参数表缺口。
KNOWN_EXTRA = {
    "Stop_AllMusic": "脚本传 1 个，函数无参数读取（0x59C9E0）",
    "Add_JointNail": "脚本传 6 个，函数只读 1..5（0x598210）",
    "Set_ScrObjPos": "脚本传 5..7 个，函数只读 1..4（0x59A210）",
}


def imm(s):
    """解析 IDA 立即数：1 / -3 / 0Ah / 10h / 0x10。"""
    if s is None:
        return None
    s = s.strip()
    if re.fullmatch(r"0x[0-9A-Fa-f]+", s):
        return int(s, 16)
    if re.fullmatch(r"[0-9A-Fa-f]+h", s):
        return int(s[:-1], 16)
    if re.fullmatch(r"-?\d+", s):
        return int(s)
    return None


def parse_func(x):
    """正序数据流：记录每次 call 时的 EAX/EDX/ECX 与自上次 call 以来的栈参数。"""
    reg = {"eax": None, "edx": None, "ecx": None}
    pushes = []
    fpend = None
    calls = []
    for _ea, t in [(e, s.strip()) for e, s in x["insns"]]:
        if t.startswith("mov ebp, esp"):
            pushes = []
            continue
        m = re.match(r"mov\s+(eax|edx|ecx),\s*(.+)$", t)
        if m:
            reg[m.group(1)] = m.group(2).strip()
            continue
        m = re.match(r"lea\s+(eax|edx|ecx),\s*(.+)$", t)
        if m:
            reg[m.group(1)] = "&" + m.group(2).strip()
            continue
        if t == "fldz":
            fpend = "0.0"
            continue
        if t == "fld1":
            fpend = "1.0"
            continue
        m = re.match(r"fld\s+(.+)$", t)
        if m:
            fpend = m.group(1).strip()
            continue
        m = re.match(r"push\s+(.+)$", t)
        if m:
            op = m.group(1).strip()
            if op == "ebp":  # prologue
                continue
            if op in reg and reg[op] is not None:
                v = reg[op]
                pushes.append(("ptr" if v.startswith("&") else "val", v.lstrip("&")))
            else:
                pushes.append(("val", op))
            continue
        if re.match(r"fstp\s+\[esp.*\]", t):
            pushes.append(("float", fpend if fpend is not None else "?"))
            continue
        m = re.match(r"call\s+(sub_[0-9A-Fa-f]+)$", t)
        if m:
            calls.append(dict(callee=m.group(1), kind=HELPERS.get(m.group(1), "sub"),
                              edx=reg["edx"], ecx=reg["ecx"],
                              pushes=list(pushes), fpend=fpend))
            pushes = []
            fpend = None
            continue
        m = re.match(r"call\s+(j_lua_[a-z]+)$", t)
        if m:
            calls.append(dict(callee=m.group(1), kind="direct", pushes=list(pushes)))
            pushes = []
            continue
    return calls


def ret_const(x):
    """FPC 函数的返回值个数写在 `[ebp+var_4]`；失败分支通常为 0，取所有赋值的最大值。

    例：Local_ToWorld 成功路径 `=2`、失败路径 `=0` ⇒ 2；Get_JointLimits 分支各 push 1 个
    number、末尾 `=3` ⇒ 3（静态 push 调用是 4 次，不能当返回个数）。
    """
    vals = []
    for _ea, t in x["insns"]:
        m = re.match(r"mov\s+\[ebp\+var_4\],\s*(.+)$", t.strip())
        if m:
            v = imm(m.group(1))
            if v is not None:
                vals.append(v)
    return max(vals) if vals else None


def build_spec(name, x):
    calls = parse_func(x)
    args = {}          # idx -> (kind, default)
    dyn = []           # (from, to_expr, kind, default)
    rets = []
    facs = set()
    notes = []
    conflicts = []
    type_only = []

    def put(idx, kind, default):
        if idx is None:
            return
        if idx in args:
            old = args[idx]
            if old[0] == "any" or kind == "any":
                args[idx] = ("any", old[1] if old[0] == "any" else default)
                return
            if old[0] != kind:
                pair = {old[0], kind}
                if pair <= {"int", "float"}:
                    args[idx] = ("float", old[1])       # tonumber 读整数也合法
                elif "str" in pair:
                    args[idx] = ("any", old[1])         # number 或 string 分支
                else:
                    conflicts.append("idx%d:%s->%s" % (idx, old[0], kind))
            return
        args[idx] = (kind, default)

    for c in calls:
        k = c["kind"]
        if k in ("slots4", "slots3"):
            base = imm(c["edx"])
            if base is None:
                conflicts.append("dynbase:%s" % c["edx"])
                continue
            if k == "slots4":
                st = list(reversed(c["pushes"]))
                dflt = st[0][1] if st and st[0][0] == "float" else "?"
                put(base, "int", "0")
                for j in range(1, 4):
                    put(base + j, "float", dflt)
            else:
                # 3 槽读取器缺省时不写变量（调用方栈值），见 sub_596BA0 的 loc_596C38
                for j in range(3):
                    put(base + j, "float", "none")
        elif k in ("optnum", "optint", "optstr"):
            idx = imm(c["edx"])
            if idx is None:
                continue  # 动态索引，由 SPECIAL 覆盖
            if k == "optnum":
                dflt = c["pushes"][0][1] if c["pushes"] else "?"
            else:
                dflt = c["ecx"] if c["ecx"] is not None else "?"
            put(idx, KIND[k], dflt)
        elif k == "objattr_int":
            # sub_598990(L, prop)：EDX 是对象属性编号，不是 Lua 索引；Lua 参数固定是对象 id
            notes.append("prop=%s" % (c["edx"] or "?"))
            put(1, "int", "none")
        elif k == "strarg":
            put(imm(c["edx"]), "str", "none")
        elif k == "direct":
            if c["callee"] == "j_lua_pushinteger":
                rets.append("int")
            elif c["callee"] == "j_lua_pushnumber":
                rets.append("float")
            elif c["callee"] in ("j_lua_type", "j_lua_tonumber", "j_lua_tolstring"):
                idx = None
                for _kind, v in c["pushes"]:
                    iv = imm(v)
                    if iv is not None:
                        idx = iv
                        break
                if c["callee"] == "j_lua_type":
                    type_only.append(idx)   # 只是类型检查，具体读取由后面的 tonumber/tolstring 决定
                else:
                    put(idx, "float" if c["callee"] == "j_lua_tonumber" else "str", "none")
        elif k == "sub":
            a = int(c["callee"][4:], 16)
            if 0x580000 <= a < 0x5B0000 and c["callee"] not in HELPERS:
                facs.add(c["callee"])

    for f in SPECIAL.get(name, []):
        dyn.append(f)

    for idx in type_only:
        if idx is not None and idx not in args:
            args[idx] = ("any", "none")

    # 动态索引与固定槽重叠时，以动态段为准，删掉重叠的固定槽
    for start, _to, _kind, _dflt in dyn:
        for idx in [i for i in args if i >= start]:
            del args[idx]

    ret = "none" if not rets else (
        "int" if all(r == "int" for r in rets) else
        "float" if all(r == "float" for r in rets) else "mixed")
    status = "noargs" if (not args and not dyn and not facs) else ("dynamic" if dyn else "ok")
    if conflicts:
        status = "partial"
    return dict(args=args, dyn=dyn, ret=ret, ret_count=ret_const(x),
                facs=sorted(facs), status=status, conflicts=conflicts,
                notes=notes, calls=calls)


def fmt_spec(spec):
    parts = []
    for idx in sorted(spec["args"]):
        kind, dflt = spec["args"][idx]
        parts.append("%d:%s=%s" % (idx, kind, dflt))
    for start, to, kind, dflt in spec["dyn"]:
        if to is None:
            parts.append("%d..:%s=%s" % (start, kind, dflt))
        else:
            parts.append("%d..%s:%s=%s" % (start, to, kind, dflt))
    return ";".join(parts)


def check_probe(rows_by_name, files):
    total = mism = arity = known = 0
    examples = []
    for f in files:
        for line in open(f, encoding="utf-8"):
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            total += 1
            name = d.get("call")
            spec = rows_by_name.get(name)
            if spec is None:
                mism += 1
                examples.append((name, "unknown binding"))
                continue
            a = d.get("args") or []
            max_fixed = max(spec["args"]) if spec["args"] else 0
            has_dyn = bool(spec["dyn"])
            if len(a) > max_fixed and not has_dyn:
                if name in KNOWN_EXTRA:
                    known += 1
                else:
                    arity += 1
                    examples.append((name, "arity %d > %d" % (len(a), max_fixed)))
            for i, v in enumerate(a, 1):
                if v is None:
                    continue
                if i > max_fixed and (has_dyn or name in KNOWN_EXTRA):
                    continue  # 动态段或已知多传，不按固定槽检查
                kind = spec["args"].get(i, (None,))[0]
                if kind is None:
                    arity += 1
                    examples.append((name, "arg%d no spec" % i))
                    continue
                ok = (kind == "any" or kind == "float" or
                      (kind == "int" and (isinstance(v, int) or
                                          (isinstance(v, float) and float(v).is_integer()))) or
                      (kind == "str" and isinstance(v, str)))
                if not ok:
                    mism += 1
                    examples.append((name, "arg%d kind=%s value=%r" % (i, kind, v)))
    return total, mism, arity, known, examples


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--asm", default=ASM_JSON)
    ap.add_argument("--check-probe", nargs="*", default=None,
                    help="语料 JSONL；不带值时扫 work/lua_probe*.jsonl")
    args = ap.parse_args()

    asm = json.load(open(args.asm, encoding="utf-8"))
    rows = []
    rows_by_name = {}
    for x in asm:
        spec = build_spec(x["name"], x)
        rows_by_name[x["name"]] = spec
        rows.append((x, spec))

    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    with open(OUT_CSV, "w", encoding="utf-8", newline="\r\n") as fp:
        fp.write("lua_name,cfunc,size,args,argc,ret,ret_count,factories,status,notes\r\n")
        for x, s in rows:
            argc = max(s["args"]) if s["args"] else (s["dyn"][0][0] - 1 if s["dyn"] else 0)
            fp.write(",".join([
                x["name"], x["ea"], str(x["size"]), fmt_spec(s), str(argc), s["ret"],
                str(s["ret_count"]), ";".join(s["facs"]), s["status"],
                ";".join(s["conflicts"]),
            ]) + "\r\n")

    payload = []
    for x, s in rows:
        payload.append(dict(name=x["name"], ea=x["ea"], size=x["size"],
                            args={str(k): v for k, v in s["args"].items()},
                            dyn=s["dyn"], ret=s["ret"], ret_count=s["ret_count"],
                            ret_const=ret_const(x), factories=s["facs"],
                            status=s["status"], conflicts=s["conflicts"],
                            calls=s["calls"]))
    with open(OUT_JSON, "w", encoding="utf-8") as fp:
        json.dump(payload, fp, indent=1)

    statuses = collections.Counter(s["status"] for _x, s in rows)
    print("rows=%d ok=%d noargs=%d dynamic=%d partial=%d conflicts=%d factories=%d" % (
        len(rows), statuses["ok"], statuses["noargs"], statuses["dynamic"],
        statuses["partial"], sum(len(s["conflicts"]) for _x, s in rows),
        sum(1 for _x, s in rows if s["facs"])))

    if args.check_probe is not None:
        files = args.check_probe or sorted(glob.glob(os.path.join(ROOT, "work", "lua_probe*.jsonl")))
        total, mism, arity, known, examples = check_probe(rows_by_name, files)
        print("probe_calls=%d kind_mismatch=%d arity_gt=%d known_extra=%d" % (
            total, mism, arity, known))
        for e in examples[:15]:
            print("  ", e)


if __name__ == "__main__":
    main()
