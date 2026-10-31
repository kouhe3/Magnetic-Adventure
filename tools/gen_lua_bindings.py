"""从 mapping/lua-binding-args.csv 生成 src/host_lcl/luabind.pas（144 个 cdecl 绑定壳）。

用法:
    python tools/gen_lua_bindings.py
    python tools/gen_lua_bindings.py --csv mapping/lua-binding-args.csv --out src/host_lcl/luabind.pas

判据:
    stdout `bindings=144`；生成的单元由 tools/glskel_build.py 编译通过；
    magnet.exe 里 `RegisterBindings` 注册后脚本能 loadfile（T6.3/a1）。

语义（依据 F239/F201）:
    - 参数读取按 args DSL：int/float/str/any，缺省值用 LuaOptInt/LuaOptNumber。
    - 动态段与 tools/lua_binding_args.py 的 SPECIAL 同源：
        Do_Command            4..3+arg3
        Attach_ShapePolygon   6..5+2*arg5
        Add_Rope              5.. 直到 lua_type != number
    - 桩返回值：Add_* 返回递增 id（1001 起，对齐 tools/lua_probe.cpp），其余 0；
      ret_count 个 push 值（int→PushInteger，float→PushNumber，mixed→PushInteger）。

覆盖边界:
    - 这是**桩**：工厂调用（T6.3-b）与真实返回值语义都未实现。
    - 动态段的循环变量只用于读参，读到的值不参与返回。
"""
import argparse
import csv
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_DEFAULT = os.path.join(ROOT, "mapping", "lua-binding-args.csv")
OUT_DEFAULT = os.path.join(ROOT, "src", "host_lcl", "luabind.pas")

FIXED_RE = re.compile(r"^(\d+):(\w+)=(\S+)$")
DYN_RE = re.compile(r"^(\d+)\.\.([^:]*):(\w+)=(\S+)$")


def parse_args(spec):
    fixed, dyn = [], []
    for seg in (spec or "").split(";"):
        seg = seg.strip()
        if not seg:
            continue
        m = FIXED_RE.match(seg)
        if m:
            fixed.append((int(m.group(1)), m.group(2), m.group(3)))
            continue
        m = DYN_RE.match(seg)
        if m:
            dyn.append((int(m.group(1)), m.group(2), m.group(3), m.group(4)))
    return fixed, dyn


def num_default(kind, dflt):
    if kind == "int":
        return dflt if re.fullmatch(r"-?\d+", dflt) else "0"
    return dflt if re.fullmatch(r"-?\d+(\.\d+)?", dflt) else "0.0"


def gen_binding(row):
    name = row["lua_name"]
    fixed, dyn = parse_args(row["args"])
    var_lines = []
    for idx, kind, _dflt in fixed:
        if kind == "str":
            var_lines.append("  v%d: PChar;" % idx)
        elif kind == "int":
            var_lines.append("  v%d: Integer;" % idx)
        else:
            var_lines.append("  v%d: Double;" % idx)
    if dyn:
        var_lines += ["  n, i: Integer;", "  d: Double;"]

    body = []
    for idx, kind, dflt in fixed:
        if kind == "str":
            body.append("  v%d := LuaOptStr(L, %d);" % (idx, idx))
        elif kind == "int":
            body.append("  v%d := LuaOptInt(L, %d, %s);" % (idx, idx, num_default(kind, dflt)))
        else:
            body.append("  v%d := LuaOptNumber(L, %d, %s);" % (idx, idx, num_default(kind, dflt)))

    if name == "Do_Command":
        body += ["  n := v3;", "  for i := 0 to n - 1 do",
                 "    d := LuaOptNumber(L, 4 + i, 0.0);"]
    elif name == "Attach_ShapePolygon":
        body += ["  n := v5;", "  for i := 0 to n - 1 do", "  begin",
                 "    d := LuaOptNumber(L, 6 + 2 * i, 0.0);",
                 "    d := LuaOptNumber(L, 7 + 2 * i, 0.0);", "  end;"]
    elif name == "Add_Rope":
        body += ["  i := 5;", "  while Lua.LType(L, i) = LUA_TNUMBER do", "  begin",
                 "    d := Lua.ToNumber(L, i);", "    Inc(i);", "  end;"]

    ret = row["ret"]
    cnt = int(row["ret_count"] or "0")
    body.append("  Result := NextId('%s');" % name)
    if ret == "none" or cnt <= 0:
        body.append("  Result := 0;")
    else:
        push = "Lua.PushInteger" if ret in ("int", "mixed") else "Lua.PushNumber"
        body.append("  %s(L, Result);" % push)
        for _ in range(1, cnt):
            body.append("  %s(L, 0);" % push)
        body.append("  Result := %d;" % cnt)

    lines = ["function bind_%s(L: TLuaState): Integer; cdecl;" % name]
    if var_lines:
        lines.append("var")
        lines += var_lines
    lines.append("begin")
    lines += body
    lines.append("end;")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default=CSV_DEFAULT)
    ap.add_argument("--out", default=OUT_DEFAULT)
    args = ap.parse_args()

    rows = list(csv.DictReader(open(args.csv, encoding="utf-8")))
    parts = []
    parts.append("unit LuaBind;\n{$mode objfpc}{$H+}")
    parts.append("// 由 tools/gen_lua_bindings.py 从 mapping/lua-binding-args.csv 生成，勿手改。")
    parts.append("// 144 个 Lua 绑定壳：按参数表读参 + 桩返回值（T6.3/a1，F239/F201）。")
    parts.append("// 桩语义：Add_* 返回递增 id（1001 起，对齐 tools/lua_probe.cpp），其余 0。")
    parts.append("interface\n\nuses LuaDll;\n\nfunction NextId(const Name: string): Integer;\nprocedure RegisterBindings(L: TLuaState);\n\nimplementation\n\nvar\n  g_nextId: Integer = 1000;\n")
    parts.append("function NextId(const Name: string): Integer;\nbegin\n"
                 "  if (Length(Name) >= 4) and (Copy(Name, 1, 4) = 'Add_') then\n  begin\n"
                 "    Inc(g_nextId);\n    Result := g_nextId;\n  end\n  else\n    Result := 0;\nend;\n")
    for row in rows:
        parts.append(gen_binding(row) + "\n")
    reg = ["procedure RegisterBindings(L: TLuaState);", "begin"]
    for row in rows:
        name = row["lua_name"]
        reg.append("  Lua.PushCClosure(L, Pointer(@bind_%s), 0);" % name)
        reg.append("  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('%s'));" % name)
    reg.append("end;\n\nend.")
    parts.append("\n".join(reg))

    text = "\n".join(s.replace("\r\n", "\n") for s in parts).replace("\n", "\r\n")
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8", newline="") as fp:
        fp.write(text)
    print("bindings=%d out=%s bytes=%d" % (len(rows), os.path.relpath(args.out, ROOT), len(text)))


if __name__ == "__main__":
    main()
