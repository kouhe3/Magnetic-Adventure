"""生成转发 DLL（proxy b2Physics.dll）的 87 个 naked 桩 + 同名同序号 .def。

原理：把原 b2Physics.dll 改名为 b2Physics_orig.dll，代理 DLL 占据原文件名，
首次调用时 GetProcAddress 解析真实函数。桩入口保存所有寄存器与 EFLAGS，
把「返回地址 + 前 32 个 dword 实参」（cdecl 全部在栈上）连同 ecx/edx 交给
log_call 记录，然后 popad/popfd + jmp 真实函数 —— 栈与寄存器完全原样，
对宿主与被代理 DLL 都是透明的。不需要知道 87 个函数各自的签名。

依据：docs/facts.md F31/F35（导出清单与序号）、F38（ReFilter 参数）；
实参形状未知项见 F34（关节工厂）。

用法：python tools/gen_proxy.py
"""
import csv
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
CSV = ROOT / "mapping" / "b2physics-exports.csv"
OUT_C = ROOT / "src" / "proxydll" / "proxy_stubs.c"
OUT_DEF = ROOT / "src" / "proxydll" / "proxy.def"


def load():
    rows = []
    with CSV.open(encoding="utf-8", errors="replace") as f:
        for r in csv.DictReader(f):
            name = r["name"]
            if not name.startswith("b2_"):
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
    rows = load()
    n = max(o for o, _ in rows)
    parts = [
        "/* 生成文件，勿手改：python tools/gen_proxy.py",
        " * 依据：docs/facts.md F35（87 个导出/序号）、F31（check_exports 零差异） */",
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
    OUT_C.parent.mkdir(parents=True, exist_ok=True)
    OUT_C.write_text("\n".join(parts), encoding="utf-8")

    d = ["LIBRARY b2Physics", "EXPORTS"]
    d += [f"{name}=proxy_stub_{ord} @{ord}" for ord, name in rows]
    OUT_DEF.write_text("\n".join(d) + "\n", encoding="utf-8")
    print(f"{OUT_C.relative_to(ROOT)}: {len(rows)} stubs")
    print(f"{OUT_DEF.relative_to(ROOT)}: {len(rows)} exports")


if __name__ == "__main__":
    main()
