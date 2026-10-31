"""在 IDA 里导出 mapping/lua-bindings.csv 那 144 个 Lua C 函数的完整反汇编。

用法（IDA 已打开 `bin/gametop/game.exe.i64`，通过 ida MCP 的 execute_python 执行本文件；
`db` 由 MCP 注入，普通 IDA 控制台需要自己 Database.open）:

    code = open(r"tools/ida_lua_asm.py", encoding="utf-8").read()
    # 交给 mcp__ida_execute_python 的 code 参数

产物（work/，gitignore）:
    work/lua_bindings_asm.json  [{name, ea, size, insns:[[ea, "text"], ...]}, ...]

判据:
    打印 `rows=144 disasm=144 missing=[]`。任何一个函数取不到反汇编都会列在 missing。

覆盖边界:
    只导出 `cfunc` 地址处的**函数体**（start_ea..end_ea），不做调用点解析、不推参数表。
    参数表由 `tools/lua_binding_args.py` 离线解析这份 JSON 得到，依据 F201/F239。

依据: docs/facts.md F201（144/144 反编译）、F239（参数表）。
"""
import csv
import json

CSV_PATH = r"C:/tmp/Magnetic Adventure/mapping/lua-bindings.csv"
OUT_PATH = r"C:/tmp/Magnetic Adventure/work/lua_bindings_asm.json"

rows = list(csv.DictReader(open(CSV_PATH, encoding="utf-8")))
funcs = {f.start_ea: f for f in db.functions.get_all()}  # noqa: F821  (db 由 ida MCP 注入)
out = []
missing = []

for r in rows:
    ea = int(r["cfunc"], 16)
    f = funcs.get(ea)
    insns = []
    if f is not None:
        for i in db.instructions.get_between(f.start_ea, f.end_ea):  # noqa: F821
            insns.append([i.ea, db.instructions.get_disassembly(i)])  # noqa: F821
    else:
        missing.append(r["lua_name"])
    out.append(dict(name=r["lua_name"], ea=r["cfunc"], size=int(r["size"]), insns=insns))

with open(OUT_PATH, "w", encoding="utf-8") as fp:
    json.dump(out, fp, indent=0)

print("rows=%d disasm=%d missing=%r insns_total=%d" % (
    len(out), sum(1 for x in out if x["insns"]), missing, sum(len(x["insns"]) for x in out)))
