"""生成转发 DLL 的 naked 桩 + 同名同序号 .def（默认 b2Physics，可选 Squall）。

原理：把原 DLL 改名为 `<name>_orig.dll`，代理 DLL 占据原文件名，
首次调用时 GetProcAddress 解析真实函数。桩入口保存所有寄存器与 EFLAGS，
把「返回地址 + 前 N 个 dword 实参」（cdecl 全部在栈上）连同 ecx/edx 交给
log_call 记录，然后 popad/popfd + jmp 真实函数 —— 栈与寄存器完全原样，
对宿主与被代理 DLL 都是透明的。不需要知道每个函数各自的签名。

依据：docs/facts.md F35（b2 导出清单与序号）、F38（ReFilter 参数）、
      F131（Squall 99 个导出/序号）、F136（上游源码与原版不等价，需对拍）。

用法：
  python tools/gen_proxy.py
  python tools/gen_proxy.py --csv mapping/squall-exports.csv \
      --out-c src/squallproxy/proxy_stubs.c --out-def src/squallproxy/proxy.def \
      --library Squall --prefix SQUALL_
"""
import argparse
import csv
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
CSV = ROOT / "mapping" / "b2physics-exports.csv"
OUT_C = ROOT / "src" / "proxydll" / "proxy_stubs.c"
OUT_DEF = ROOT / "src" / "proxydll" / "proxy.def"


def load(csv_path, prefix):
    rows = []
    with csv_path.open(encoding="utf-8", errors="replace") as f:
        for r in csv.DictReader(f):
            name = r["name"]
            if not name.startswith(prefix):
                continue  # DllEntryPoint 之类的伪条目
            rows.append((int(r["ordinal"]), name))
    rows.sort()
    return rows


STUB_PRE = """\
__declspec(naked) void proxy_stub_{ord}(void) {{
    __asm {{
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push {ord}
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push {ord}
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_{ord}
        jmp  dword ptr [g_slot+{off}]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }}
}}
"""

STUB_POST = """\
__declspec(naked) void proxy_post_{ord}(void) {{
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {{
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push {ord}
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }}
}}
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default=str(CSV))
    ap.add_argument("--out-c", default=str(OUT_C))
    ap.add_argument("--out-def", default=str(OUT_DEF))
    ap.add_argument("--library", default="b2Physics")
    ap.add_argument("--prefix", default="b2_")
    a = ap.parse_args()
    csv_path = pathlib.Path(a.csv)
    out_c = pathlib.Path(a.out_c)
    out_def = pathlib.Path(a.out_def)
    if not csv_path.is_absolute():
        csv_path = ROOT / csv_path
    if not out_c.is_absolute():
        out_c = ROOT / out_c
    if not out_def.is_absolute():
        out_def = ROOT / out_def

    rows = load(csv_path, a.prefix)
    n = max(o for o, _ in rows)
    parts = [
        "/* 生成文件，勿手改：python tools/gen_proxy.py",
        " * 依据：docs/facts.md F35/F131（导出清单与序号） */",
        "#include <windows.h>",
        "#include <stdint.h>",
        "",
        "extern FARPROC g_slot[];",
        "void __cdecl log_call(unsigned id, uint32_t esp0, uint32_t edx, uint32_t ecx);",
        "void __cdecl save_ret(unsigned id, uint32_t orig_ret);",
        "uint32_t __cdecl finish_call(unsigned id, uint32_t retval, uint32_t args_ptr);",
        "uint32_t __cdecl get_ret(void);",
        "",
        f"const int g_n_exports = {n + 1};",
        "const char* const g_names[] = {",
        '    "",  /* 0 号占位 */',
    ]
    parts += [f'    "{name}",' for _, name in rows]
    parts += ["    0,",
              "};",
              "",
              f"FARPROC g_slot[{n + 2}] = {{0}};",
              ""]
    for off, _ in rows:
        parts.append(STUB_POST.format(ord=off, off=off * 4))
    for off, _ in rows:
        parts.append(STUB_PRE.format(ord=off, off=off * 4))
    out_c.parent.mkdir(parents=True, exist_ok=True)

    # 生成物入库，换行必须与仓库一致：CRLF（`.gitattributes` 的 `* -text`，见 F130）。
    def write_crlf(path, text):
        with path.open("w", encoding="utf-8", newline="\r\n") as f:
            f.write(text)

    write_crlf(out_c, "\n".join(parts))

    d = [f"LIBRARY {a.library}", "EXPORTS"]
    d += [f"{name}=proxy_stub_{ord} @{ord}" for ord, name in rows]
    write_crlf(out_def, "\n".join(d) + "\n")
    print(f"{out_c.relative_to(ROOT)}: {len(rows)} stubs")
    print(f"{out_def.relative_to(ROOT)}: {len(rows)} exports")


if __name__ == "__main__":
    main()
