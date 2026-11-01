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

# T6.3c：建体/形状绑定的真实语义（PhysWorld 单元）。参数位置见 F276/F277。
# 钩子放在 NextId 之后、返回值 push 之前；只写 b2 状态，不改 JSONL 与返回值。
HOOKS = {
    "Add_SimplePhysicObject": ["  PhysAddSimplePhysicObject(id, v1, v2, v3);"],
    "Add_SimplePhysCircle": ["  PhysAddSimplePhysCircle(id, v2, v3, v4, v5, v6);"],
    "Add_WoodGear": ["  PhysAddWoodGear(id, v2, v3, v4, v5);"],
    "Add_WoodWall": ["  PhysAddWoodWall(id, v2, v3, v4);"],
    "Add_SwitchArm": ["  PhysAddSwitchArm(id, v2, v3, v4);"],
    "Attach_ShapeCircle": ["  PhysAttachShapeCircle(v1, v2, v3, v4, v5, v6, v7);"],
    "Add_JointNail": ["  PhysAddJointNail(id, v2, v3, v4, v5);"],
    "Add_JointSimpleRevolute": ["  PhysAddJointSimpleRevolute(id, v1, v2, v3, v4);"],
    "Add_JointSimpleGear": ["  PhysAddJointSimpleGear(id, v1, v2, v3, v4, v5);"],
    "Add_JointSimplePrismatic": ["  PhysAddJointSimplePrismatic(id, v1, v2, v3, v4, v5, v6);"],
    "Set_JointLimits": ["  PhysSetJointLimits(v1, v2 <> 0.0, v3, v4);"],
    "Set_JointMotors": ["  PhysSetJointMotors(v1, v2 <> 0.0, v3, v4);"],
    "Set_ScrObjPos": ["  PhysSetBodyPos(v1, v2, v3, v4);"],
    "Set_PhysParams": ["  PhysSetPhysParams(v1, v2, v3, v4);"],
    "Set_PhysFilterData": ["  PhysSetPhysFilter(v1, v2, v3, v4);"],
    "Re_Filter": ["  PhysReFilter(v1);"],
}

# 需要真实返回值（不是 id）的绑定：额外变量行 + 返回 push 行。
CUSTOM_RET = {
    "Get_ScrObjPos": (
        ["  gx, gy, ga: Double;"],
        ["  PhysGetBodyPos(v1, gx, gy, ga);",
         "  Lua.PushNumber(L, gx);",
         "  Lua.PushNumber(L, gy);",
         "  Lua.PushNumber(L, ga);",
         "  Result := 3;"],
    ),
    "Get_PhysParams": (
        ["  gx, gy, ga: Double;"],
        ["  PhysGetPhysParams(v1, gx, gy, ga);",
         "  Lua.PushNumber(L, gx);",
         "  Lua.PushNumber(L, gy);",
         "  Lua.PushNumber(L, ga);",
         "  Result := 3;"],
    ),
}


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
    if name in CUSTOM_RET:
        var_lines += CUSTOM_RET[name][0]

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
    body.append("  id := NextId('%s');" % name)
    body += HOOKS.get(name, [])
    if name in CUSTOM_RET:
        body += CUSTOM_RET[name][1]
    elif ret == "none" or cnt <= 0:
        body.append("  Result := 0;")
    else:
        push = "Lua.PushInteger" if ret in ("int", "mixed") else "Lua.PushNumber"
        body.append("  %s(L, id);" % push)
        for _ in range(1, cnt):
            body.append("  %s(L, 0);" % push)
        body.append("  Result := %d;" % cnt)
    body.append("  LuaLogEnd(id);")

    lines = ["function bind_%s(L: TLuaState): Integer; cdecl;" % name]
    lines.append("var")
    lines.append("  id: Integer;")
    lines += var_lines
    if name == "Attach_ScriptToObject":
        lines.append("  s2, s3: string;")
    lines.append("begin")
    lines.append("  LuaLogBegin(L, '%s');" % name)
    if name == "Attach_ScriptToObject":
        # 必须排在参数读取之后：v1/v2/v3 由下面的读参语句赋值。
        at = len(fixed)
        body[at:at] = ["  if v2 <> nil then s2 := v2;",
                       "  if v3 <> nil then s3 := v3;",
                       "  EventsAdd(v1, s2, s3);"]
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
    parts.append("interface\n\nuses LuaDll, LuaLog, LuaEvents, PhysWorld;\n\nfunction NextId(const Name: string): Integer;\nprocedure ResetIds;\nprocedure RegisterBindings(L: TLuaState);\n\nimplementation\n\nvar\n  g_nextId: Integer = 1000;\n")
    parts.append("function NextId(const Name: string): Integer;\nbegin\n"
                 "  if (Length(Name) >= 4) and (Copy(Name, 1, 4) = 'Add_') then\n  begin\n"
                 "    Inc(g_nextId);\n    Result := g_nextId;\n  end\n  else\n    Result := 0;\nend;\n\n"
                 "procedure ResetIds;\nbegin\n  g_nextId := 1000;\nend;\n")
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
