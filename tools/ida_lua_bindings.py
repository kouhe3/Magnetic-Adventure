"""在 IDA 里批量导出 mapping/lua-bindings.csv 那 144 个 Lua C 函数的反编译文本与调用摘要。

用法（IDA 已打开 `work/ida/game.exe.i64`，且通过 ida MCP 的 execute_python 执行本文件；
`db` 由 MCP 注入，普通 IDA 控制台需要自己 Database.open）:

    code = open(r"tools/ida_lua_bindings.py", encoding="utf-8").read()
    # 交给 mcp__ida_execute_python 的 code 参数

产物（都在 work/，gitignore）:
    work/lua_bindings_decomp.json      每条 {name, ea, size, callees, rets}
    work/lua_bindings_decomp.json.txt  每条完整反编译文本（人读，144 段）
    work/lua_bindings_spec.json        上面那份的同一内容（历史文件名，保留兼容）

判据:
    打印 `rows == ok`（期望 144/144）；任何失败都会列出 (名字, 地址, 异常)。
    反编译成功但函数体为空 → 也算失败（说明地址不是函数入口）。

覆盖边界:
    只做"函数级摘要 + 文本"，不解析 Lua 调用点，也不自动推参数表：
      - 参数读取走两个 helper（F201 已解码）：
          sub_596900 = optnumber(L, idx, default) → float（`lua_type==3` 才是数字）
          sub_596C50 = 4 槽读取器（槽 0 走 lua_tonumber → sub_532260，其余给 float 默认值）
      - 每个函数末尾 lua_pushinteger / lua_pushnumber 决定返回值类型（67 / 30，F201）。
    索引来自寄存器残留，摘要里看不到 —— 要逐函数参数表得再看反汇编。

依据: docs/facts.md F201（144/144 反编译 + helper 语义 + push 类型分布）。
"""
import collections
import csv
import json
import re

CSV = r"C:/tmp/Magnetic Adventure/mapping/lua-bindings.csv"
OUT = r"C:/tmp/Magnetic Adventure/work/lua_bindings_decomp.json"

rows = list(csv.DictReader(open(CSV, encoding="utf-8")))
res = []
fails = []

for r in rows:
    ea = int(r["cfunc"], 16)
    try:
        text = "\n".join(db.pseudocode.get_text(ea))  # noqa: F821  (db 由 ida MCP 注入)
    except Exception as e:
        fails.append((r["lua_name"], r["cfunc"], "%s: %s" % (type(e).__name__, e)))
        continue
    if not text.strip():
        fails.append((r["lua_name"], r["cfunc"], "empty pseudocode"))
        continue
    callees = re.findall(r"(?:sub_[0-9A-Fa-f]+|j_[A-Za-z_0-9]+|lua_[A-Za-z_0-9]+)", text)
    rets = re.findall(r"return (-?\d+);", text)
    res.append(dict(name=r["lua_name"], ea=r["cfunc"], size=int(r["size"]),
                    callees=callees, rets=rets, text=text))

json.dump([{k: v for k, v in d.items() if k != "text"} for d in res], open(OUT, "w"), indent=1)
with open(OUT + ".txt", "w", encoding="utf-8") as f:
    f.write("\n\n".join("=== %s %s ===\n%s" % (d["name"], d["ea"], d["text"]) for d in res))

print("rows=%d ok=%d fail=%d" % (len(rows), len(res), len(fails)))
for f in fails:
    print("  FAIL", f)
print("sizes", collections.Counter(d["size"] for d in res).most_common(8))
print("pushinteger", sum(1 for d in res if "j_lua_pushinteger" in d["callees"]),
      "pushnumber", sum(1 for d in res if "j_lua_pushnumber" in d["callees"]))
print("ret", collections.Counter(d["rets"][-1] if d["rets"] else "-" for d in res).most_common())
print("helper usage", collections.Counter(
    ("sub_596C50" in d["callees"], "sub_596900" in d["callees"]) for d in res).most_common())
