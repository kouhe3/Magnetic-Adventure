/* 进程内崩溃记录器：first-chance VEH + 可选 minidump。
 *
 * 用途：宿主（game.exe / magnet.exe，LCL 0.9.28.3）的异常会被 TApplication.ShowException
 * 用 MB_OKCANCEL 对话框吞掉，点 Cancel 走 Halt(0) ⇒ 退出码 0、崩溃现场丢失（F315）。
 * 本 DLL 在进程内注册 VEH（先于 SEH/LCL），把 OS 异常记录、上下文、模块+RVA、栈扫描
 * 同步落盘；设置 CRASHLOG_DUMP=1 时再写 minidump。
 *
 * 开关（默认全关，不建文件、不注册 VEH）：
 *   CRASHLOG_DIR=<dir>   日志与 dump 目录（文件名 crash_<owner>_<pid>.log）
 *   CRASHLOG_LOG=<path>  指定日志文件（目录取父目录）
 *   CRASHLOG_DUMP=1      写 minidump（MiniDumpNormal + 线程信息）
 *   CRASHLOG_DUMP_ALL=1  每条异常都写 dump（默认只写 seq=1）
 *   CRASHLOG_FULL=1      全内存 dump（体积大）
 *   CRASHLOG_DIALOG=1    轮询本进程的 #32770 对话框，把标题/正文写进日志
 *                        （覆盖 FPC raise 这类没有 OS 异常的弹窗）
 *
 * 日志格式（行式、key=value）：
 *   CL1 v=1 pid=… owner=… exe=… t=YYYY-MM-DDTHH:MM:SS
 *   MOD base=0x… size=0x… name=…
 *   EXC seq=… second=… tid=… code=0x… flags=0x… addr=0x… mod=… rva=0x… nparams=… p0=0x…
 *   CTX eip=… esp=… ebp=… eax=… ebx=… ecx=… edx=… esi=… edi=… efl=…
 *   FRM i=… addr=… mod=… rva=… src=ebp
 *   SCN i=… addr=… mod=… rva=… src=stack
 *   DMP path=… ok=1 size=…
 *
 * 依据：docs/facts.md F315（LCL 弹窗与 Halt(0)）、F316（VEH 捕获待证）。
 */
#include <windows.h>
#include <winternl.h>
#include <dbghelp.h>
#include <float.h>
#include <stdint.h>

#include "crashlog.h"

#ifndef CRASHLOG_STANDALONE
#define CRASHLOG_STANDALONE 0
#endif

#define CL_MAX_MODULES 384
#define CL_MAX_RECORDS 128
#define CL_BUF_SIZE (64 * 1024)
#define CL_STACK_SCAN (256 * 1024)
#define CL_MAX_FRAMES 160

typedef struct {
    uint32_t base;
    uint32_t size;
    char name[64];
} ClMod;

/* SDK 的 winternl.h 故意隐去 SizeOfImage / BaseDllName；按 x86 真实布局自己展开。
 * 实机偏移：InMemoryOrderLinks +0x08、DllBase +0x18、SizeOfImage +0x20、
 * FullDllName +0x24、BaseDllName +0x2C。 */
typedef struct {
    LIST_ENTRY InLoadOrderLinks;
    LIST_ENTRY InMemoryOrderLinks;
    LIST_ENTRY InInitializationOrderLinks;
    PVOID DllBase;
    PVOID EntryPoint;
    ULONG SizeOfImage;
    UNICODE_STRING FullDllName;
    UNICODE_STRING BaseDllName;
} ClLdrEntry;

static HANDLE g_log = INVALID_HANDLE_VALUE;
static HANDLE g_mutex = NULL;
static char g_log_path[MAX_PATH];
static char g_dump_dir[MAX_PATH];
static char g_owner[64];
static CRITICAL_SECTION g_cs;
static int g_cs_ready = 0;
static volatile LONG g_installed = 0;
static PVOID g_veh = NULL;
static LPTOP_LEVEL_EXCEPTION_FILTER g_prev_filter = NULL;
static LONG g_records = 0;
static int g_dump = 0;
static int g_dump_full = 0;
static int g_dump_all = 0;
static HMODULE g_dbghelp = NULL;
static HANDLE g_dlg_thread = NULL;
static volatile LONG g_dlg_stop = 0;
static char g_dlg_last[1024];
static uint32_t g_probe[3];   /* IsBadReadPtr/WritePtr/CodePtr 的入口，过滤其内部探测 AV */
static volatile LONG g_last_exc_seq = 0;   /* 弹窗出现时用来指回最近一条 EXC */

typedef BOOL (WINAPI *ClMiniDumpWriteDumpFn)(HANDLE, DWORD, HANDLE, MINIDUMP_TYPE,
    const PMINIDUMP_EXCEPTION_INFORMATION,
    const PMINIDUMP_USER_STREAM_INFORMATION,
    const PMINIDUMP_CALLBACK_INFORMATION);
static ClMiniDumpWriteDumpFn g_minidump = NULL;

static ClMod g_mods[CL_MAX_MODULES];
static int g_nmods = 0;
static int g_mods_emitted = 0;
static __declspec(thread) int t_in = 0;
static char g_buf[CL_BUF_SIZE];

/* ---------- 无 CRT 的定界格式化 ---------- */

static char* Out(char* p, char* end, const char* s) {
    while (*s && p < end) *p++ = *s++;
    if (p < end) *p = 0;
    return p;
}

static char* OutCh(char* p, char* end, char c) {
    if (p < end) {
        *p++ = c;
        if (p < end) *p = 0;
    }
    return p;
}

static char* OutHex(char* p, char* end, uint32_t v, int digits) {
    static const char hex[] = "0123456789ABCDEF";
    int i;
    if (digits <= 0) digits = 8;
    if (digits > 8) digits = 8;
    for (i = digits - 1; i >= 0; --i) {
        if (p < end) *p++ = hex[(v >> (i * 4)) & 0xF];
    }
    if (p < end) *p = 0;
    return p;
}

static char* OutDec(char* p, char* end, uint32_t v) {
    char tmp[12];
    int n = 0;
    do {
        tmp[n++] = (char)('0' + (v % 10));
        v /= 10;
    } while (v && n < (int)sizeof(tmp));
    while (n-- > 0) {
        if (p < end) *p++ = tmp[n];
    }
    if (p < end) *p = 0;
    return p;
}

static char* OutDec2(char* p, char* end, uint32_t v) {
    if (v < 10 && p < end) *p++ = '0';
    return OutDec(p, end, v);
}

static void StrCopy(char* dst, int cap, const char* src) {
    int i = 0;
    if (cap <= 0) return;
    while (src[i] && i < cap - 1) {
        dst[i] = src[i];
        ++i;
    }
    dst[i] = 0;
}

static void StrAppend(char* dst, int cap, const char* src) {
    int i = 0;
    int j;
    if (cap <= 0) return;
    while (dst[i] && i < cap - 1) ++i;
    j = 0;
    while (src[j] && i < cap - 1) dst[i++] = src[j++];
    dst[i] = 0;
}

/* ---------- 模块表（PEB 链表，不分配内存） ---------- */

static void RefreshModules(void) {
    int n = 0;
    __try {
        PPEB peb = (PPEB)NtCurrentTeb()->ProcessEnvironmentBlock;
        if (peb && peb->Ldr) {
            LIST_ENTRY* head = &peb->Ldr->InMemoryOrderModuleList;
            LIST_ENTRY* it = head->Flink;
            while (it && it != head && n < CL_MAX_MODULES) {
                ClLdrEntry* e =
                    CONTAINING_RECORD(it, ClLdrEntry, InMemoryOrderLinks);
                uint32_t base = (uint32_t)(uintptr_t)e->DllBase;
                uint32_t size = (uint32_t)e->SizeOfImage;
                if (base && size) {
                    int k = 0;
                    g_mods[n].base = base;
                    g_mods[n].size = size;
                    if (e->BaseDllName.Buffer) {
                        int len = e->BaseDllName.Length / 2;
                        for (; k < len && k < (int)sizeof(g_mods[n].name) - 1; ++k) {
                            WCHAR c = e->BaseDllName.Buffer[k];
                            g_mods[n].name[k] = (c > 0 && c < 128) ? (char)c : '?';
                        }
                    }
                    g_mods[n].name[k] = 0;
                    ++n;
                }
                it = it->Flink;
            }
        }
    } __except (EXCEPTION_EXECUTE_HANDLER) {
        /* 保留已枚举到的部分 */
    }
    g_nmods = n;
}

static ClMod* ModByAddr(uint32_t a) {
    int i;
    for (i = 0; i < g_nmods; ++i) {
        if (a >= g_mods[i].base && a - g_mods[i].base < g_mods[i].size)
            return &g_mods[i];
    }
    return NULL;
}

static int ModResolve(uint32_t a, char* name, int cap, uint32_t* rva) {
    ClMod* m = ModByAddr(a);
    if (!m) return 0;
    if (name && cap > 0) StrCopy(name, cap, m->name);
    if (rva) *rva = a - m->base;
    return 1;
}

/* ---------- 写日志 ---------- */

static void ClWrite(const char* s, DWORD n) {
    DWORD written = 0;
    if (g_log == INVALID_HANDLE_VALUE || !n) return;
    WriteFile(g_log, s, n, &written, NULL);
    FlushFileBuffers(g_log);
}

static void ClWriteStr(const char* s) {
    DWORD n = 0;
    while (s[n]) ++n;
    ClWrite(s, n);
}

/* ---------- 对话框正文监视（可选，覆盖 Pascal raise） ---------- */

static BOOL CALLBACK ClDlgEnumChild(HWND hwnd, LPARAM lp) {
    char* p = (char*)lp;
    char* end = p + 2047;
    WCHAR w[512];
    char utf8[1024];
    int n;
    char cls[64];
    if (!InternalGetWindowText(hwnd, w, (int)(sizeof(w) / sizeof(w[0])))) return TRUE;
    if (!w[0]) return TRUE;
    n = WideCharToMultiByte(CP_UTF8, 0, w, -1, utf8, sizeof(utf8), NULL, NULL);
    if (n <= 1) return TRUE;
    {
        int k;
        for (k = 0; utf8[k]; ++k) {
            if (utf8[k] == '\r' || utf8[k] == '\n') utf8[k] = ' ';
        }
    }
    GetClassNameA(hwnd, cls, sizeof(cls));
    if (lstrcmpA(cls, "Button") == 0) return TRUE;   /* 按钮文字不是崩溃信息 */
    p = Out(p, end, " | ");
    p = Out(p, end, cls);
    p = Out(p, end, ":");
    Out(p, end, utf8);
    return TRUE;
}

static BOOL CALLBACK ClDlgEnumWindow(HWND hwnd, LPARAM lp) {
    DWORD pid = 0;
    char cls[64];
    char title[512];
    char text[2048];
    char line[3072];
    char* p;
    char* end;
    (void)lp;
    GetWindowThreadProcessId(hwnd, &pid);
    if (pid != GetCurrentProcessId()) return TRUE;
    if (!GetClassNameA(hwnd, cls, sizeof(cls)) || lstrcmpA(cls, "#32770") != 0) return TRUE;
    title[0] = 0;
    GetWindowTextA(hwnd, title, sizeof(title));
    text[0] = 0;
    EnumChildWindows(hwnd, ClDlgEnumChild, (LPARAM)text);
    p = line;
    end = line + sizeof(line) - 1;
    *p = 0;
    p = Out(p, end, "DLG hwnd=0x");
    p = OutHex(p, end, (uint32_t)(uintptr_t)hwnd, 8);
    p = Out(p, end, " title=");
    p = Out(p, end, title);
    p = Out(p, end, " last_exc=");
    p = OutDec(p, end, (uint32_t)g_last_exc_seq);
    p = Out(p, end, " text=");
    p = Out(p, end, text);
    p = OutCh(p, end, '\n');
    if (g_cs_ready) EnterCriticalSection(&g_cs);
    if (lstrcmpA(g_dlg_last, line) != 0) {
        int i;
        for (i = 0; line[i] && i < (int)sizeof(g_dlg_last) - 1; ++i) g_dlg_last[i] = line[i];
        g_dlg_last[i] = 0;
        ClWrite(line, (DWORD)(p - line));
    }
    if (g_cs_ready) LeaveCriticalSection(&g_cs);
    return TRUE;
}

static DWORD WINAPI ClDialogThread(LPVOID param) {
    (void)param;
    while (!g_dlg_stop) {
        Sleep(250);
        EnumWindows(ClDlgEnumWindow, 0);
    }
    return 0;
}

/* 主线程消息循环里提前加载 dbghelp：避免崩溃时在 VEH 里 LoadLibrary（可能撞 loader lock）。 */
static void CALLBACK ClPreloadTimer(HWND hwnd, UINT msg, UINT_PTR id, DWORD tick) {
    (void)hwnd;
    (void)msg;
    (void)tick;
    KillTimer(NULL, id);
    if (!g_minidump) {
        __try {
            g_dbghelp = LoadLibraryA("dbghelp.dll");
            if (g_dbghelp)
                g_minidump = (ClMiniDumpWriteDumpFn)GetProcAddress(g_dbghelp,
                                                                   "MiniDumpWriteDump");
        } __except (EXCEPTION_EXECUTE_HANDLER) {
            g_minidump = NULL;
        }
    }
}

static char* EmitModules(char* p, char* end) {
    int i;
    for (i = 0; i < g_nmods; ++i) {
        p = Out(p, end, "MOD base=0x");
        p = OutHex(p, end, g_mods[i].base, 8);
        p = Out(p, end, " size=0x");
        p = OutHex(p, end, g_mods[i].size, 8);
        p = Out(p, end, " name=");
        p = Out(p, end, g_mods[i].name);
        p = OutCh(p, end, '\n');
    }
    g_mods_emitted = g_nmods;
    return p;
}

static const char* ExcNote(uint32_t code) {
    switch (code) {
    case 0xC0000005: return "access-violation";
    case 0xC000001D: return "illegal-instruction";
    case 0xC000008E: return "float-divide-by-zero";
    case 0xC0000090: return "float-invalid-operation";
    case 0xC0000091: return "float-overflow";
    case 0xC0000093: return "float-underflow";
    case 0xC0000094: return "integer-divide-by-zero";
    case 0xC0000096: return "privileged-instruction";
    case 0xC00000FD: return "stack-overflow";
    case 0x80000003: return "breakpoint";
    case 0xE06D7363: return "msvc-cpp-exception";
    case 0x0EEDFADE: return "delphi-exception";
    default: return "";
    }
}

static char* EmitAddr(char* p, char* end, const char* tag, int idx,
                      uint32_t addr, const char* src) {
    char name[64];
    uint32_t rva = 0;
    p = Out(p, end, tag);
    p = OutCh(p, end, ' ');
    p = OutDec(p, end, (uint32_t)idx);
    p = Out(p, end, " addr=0x");
    p = OutHex(p, end, addr, 8);
    if (ModResolve(addr, name, sizeof(name), &rva)) {
        p = Out(p, end, " mod=");
        p = Out(p, end, name);
        p = Out(p, end, " rva=0x");
        p = OutHex(p, end, rva, 8);
    }
    if (src) {
        p = Out(p, end, " src=");
        p = Out(p, end, src);
    }
    p = OutCh(p, end, '\n');
    return p;
}

/* EBP 链 + 线性栈扫描。栈上的指针只作候选返回地址，符号化由 tools/crashlog_symbolize.py 做。 */
static char* ScanStack(char* p, char* end, uint32_t esp, uint32_t ebp) {
    int idx = 0;
    int emitted = 0;
    uint32_t fp;
    uint32_t lo;
    uint32_t hi;
    uint32_t last = 0;
    MEMORY_BASIC_INFORMATION mbi;

    __try {
        fp = ebp;
        while (emitted < CL_MAX_FRAMES && idx < 64) {
            uint32_t ret;
            uint32_t next;
            if (fp < esp || fp > esp + 0x100000) break;
            if (IsBadReadPtr((const void*)(uintptr_t)fp, 8)) break;
            ret = *(const uint32_t*)(uintptr_t)(fp + 4);
            if (ModByAddr(ret)) {
                p = EmitAddr(p, end, "FRM", idx++, ret, "ebp");
                ++emitted;
            }
            next = *(const uint32_t*)(uintptr_t)fp;
            if (next <= fp) break;
            fp = next;
        }

        lo = esp & ~3u;
        hi = esp + CL_STACK_SCAN;
        if (VirtualQuery((const void*)(uintptr_t)esp, &mbi, sizeof(mbi)) == sizeof(mbi)) {
            uint32_t region_end =
                (uint32_t)(uintptr_t)mbi.BaseAddress + (uint32_t)mbi.RegionSize;
            if (region_end > esp && region_end < hi) hi = region_end;
        }
        while (emitted < CL_MAX_FRAMES && lo + 4 <= hi) {
            uint32_t v;
            if (IsBadReadPtr((const void*)(uintptr_t)lo, 4)) break;
            v = *(const uint32_t*)(uintptr_t)lo;
            if (v != last && ModByAddr(v)) {
                p = EmitAddr(p, end, "SCN", idx++, v, "stack");
                ++emitted;
                last = v;
            }
            lo += 4;
        }
    } __except (EXCEPTION_EXECUTE_HANDLER) {
        /* 扫描失败就保留已产出的行 */
    }
    return p;
}

static void ClWriteDump(PEXCEPTION_POINTERS ep, LONG seq) {
    char path[MAX_PATH];
    char line[512];
    char num[12];
    char* p;
    char* end;
    HANDLE h;
    MINIDUMP_EXCEPTION_INFORMATION mei;
    MINIDUMP_TYPE type;
    BOOL ok = FALSE;
    DWORD err = 0;
    DWORD size = 0;

    if (!g_dump) return;
    if (seq != 1 && !g_dump_all) return;
    if (!g_minidump) {
        __try {
            g_dbghelp = LoadLibraryA("dbghelp.dll");
            if (g_dbghelp)
                g_minidump = (ClMiniDumpWriteDumpFn)GetProcAddress(g_dbghelp,
                                                                   "MiniDumpWriteDump");
        } __except (EXCEPTION_EXECUTE_HANDLER) {
            g_minidump = NULL;
        }
    }
    if (!g_minidump) {
        ClWriteStr("DMP err=dbghelp-unavailable\n");
        return;
    }

    StrCopy(path, sizeof(path), g_dump_dir);
    StrAppend(path, sizeof(path), "\\crash_");
    StrAppend(path, sizeof(path), g_owner);
    StrAppend(path, sizeof(path), "_");
    OutDec(num, num + sizeof(num) - 1, (uint32_t)GetCurrentProcessId());
    StrAppend(path, sizeof(path), num);
    StrAppend(path, sizeof(path), "_");
    OutDec(num, num + sizeof(num) - 1, (uint32_t)seq);
    StrAppend(path, sizeof(path), num);
    StrAppend(path, sizeof(path), ".dmp");

    h = CreateFileA(path, GENERIC_WRITE, FILE_SHARE_READ, NULL,
                    CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
    if (h == INVALID_HANDLE_VALUE) {
        err = GetLastError();
    } else {
        mei.ThreadId = GetCurrentThreadId();
        mei.ExceptionPointers = ep;
        mei.ClientPointers = FALSE;
        type = (MINIDUMP_TYPE)(MiniDumpNormal | MiniDumpWithThreadInfo |
                               MiniDumpWithUnloadedModules);
        if (g_dump_full) {
            type = (MINIDUMP_TYPE)(type | MiniDumpWithFullMemory |
                                   MiniDumpWithFullMemoryInfo | MiniDumpWithHandleData);
        }
        __try {
            ok = g_minidump(GetCurrentProcess(), GetCurrentProcessId(), h, type,
                            &mei, NULL, NULL);
        } __except (EXCEPTION_EXECUTE_HANDLER) {
            ok = FALSE;
        }
        err = ok ? 0 : GetLastError();
        size = GetFileSize(h, NULL);
        CloseHandle(h);
    }

    p = line;
    end = line + sizeof(line) - 1;
    *p = 0;
    p = Out(p, end, "DMP path=");
    p = Out(p, end, path);
    p = Out(p, end, " ok=");
    p = Out(p, end, ok ? "1" : "0");
    p = Out(p, end, " err=");
    p = OutDec(p, end, err);
    p = Out(p, end, " size=");
    p = OutDec(p, end, size);
    p = OutCh(p, end, '\n');
    ClWrite(line, (DWORD)(p - line));
}


/* IsBad*Ptr 用 SEH 探测不可读页，会先触发一次 first-chance AV；这些不是崩溃。
 * 过滤入口后 0x80 字节内的异常（实测 KERNEL32!IsBadReadPtr+0x2E）。 */
static int ClIsProbe(uint32_t addr) {
    int i;
    for (i = 0; i < 3; ++i) {
        if (g_probe[i] && addr >= g_probe[i] && addr < g_probe[i] + 0x80)
            return 1;
    }
    return 0;
}

static void ResolveProbeFuncs(void) {
    HMODULE k = GetModuleHandleA("kernel32.dll");
    if (!k) return;
    g_probe[0] = (uint32_t)(uintptr_t)GetProcAddress(k, "IsBadReadPtr");
    g_probe[1] = (uint32_t)(uintptr_t)GetProcAddress(k, "IsBadWritePtr");
    g_probe[2] = (uint32_t)(uintptr_t)GetProcAddress(k, "IsBadCodePtr");
}

static void ClLogException(PEXCEPTION_POINTERS ep, int second) {
    EXCEPTION_RECORD* er;
    uint32_t code;
    uint32_t flags;
    uint32_t addr;
    uint32_t rva = 0;
    char mname[64];
    int hasmod = 0;
    LONG seq = 0;
    char* p;
    char* end;

    if (g_log == INVALID_HANDLE_VALUE) return;
    if (t_in) return;
    t_in = 1;
    if (g_cs_ready && !TryEnterCriticalSection(&g_cs)) {
        t_in = 0;
        return;
    }

    __try {
        er = ep->ExceptionRecord;
        code = (uint32_t)er->ExceptionCode;
        flags = (uint32_t)er->ExceptionFlags;
        addr = (uint32_t)(uintptr_t)er->ExceptionAddress;
        if (!ClIsProbe(addr)) {
            seq = InterlockedIncrement(&g_records);
            if (seq <= CL_MAX_RECORDS || second) {
                RefreshModules();
                hasmod = ModResolve(addr, mname, sizeof(mname), &rva);

                p = g_buf;
                end = g_buf + sizeof(g_buf) - 1;
                *p = 0;

                p = Out(p, end, "EXC seq=");
                p = OutDec(p, end, (uint32_t)seq);
                p = Out(p, end, " second=");
                p = Out(p, end, second ? "1" : "0");
                p = Out(p, end, " tid=");
                p = OutDec(p, end, GetCurrentThreadId());
                p = Out(p, end, " code=0x");
                p = OutHex(p, end, code, 8);
                p = Out(p, end, " flags=0x");
                p = OutHex(p, end, flags, 8);
                p = Out(p, end, " addr=0x");
                p = OutHex(p, end, addr, 8);
                if (hasmod) {
                    p = Out(p, end, " mod=");
                    p = Out(p, end, mname);
                    p = Out(p, end, " rva=0x");
                    p = OutHex(p, end, rva, 8);
                }
                p = Out(p, end, " nparams=");
                p = OutDec(p, end, er->NumberParameters);
                {
                    DWORD i;
                    for (i = 0; i < er->NumberParameters && i < 4; ++i) {
                        p = Out(p, end, " p");
                        p = OutDec(p, end, i);
                        p = Out(p, end, "=0x");
                        p = OutHex(p, end, (uint32_t)er->ExceptionInformation[i], 8);
                    }
                }
                if (code == 0xC0000005u && er->NumberParameters >= 2) {
                    uint32_t op = (uint32_t)er->ExceptionInformation[0];
                    p = Out(p, end, " av=");
                    p = Out(p, end, op == 0 ? "read" : op == 1 ? "write" : op == 8 ? "execute" : "?");
                    p = Out(p, end, " fault=0x");
                    p = OutHex(p, end, (uint32_t)er->ExceptionInformation[1], 8);
                }
                {
                    const char* note = ExcNote(code);
                    if (note[0]) {
                        p = Out(p, end, " note=");
                        p = Out(p, end, note);
                    }
                }
                p = OutCh(p, end, '\n');

                if (g_mods_emitted != g_nmods || !hasmod) p = EmitModules(p, end);

    #if defined(_M_IX86)
                {
                    CONTEXT* c = ep->ContextRecord;
                    if (c) {
                        p = Out(p, end, "CTX eip=0x");
                        p = OutHex(p, end, (uint32_t)c->Eip, 8);
                        p = Out(p, end, " esp=0x");
                        p = OutHex(p, end, (uint32_t)c->Esp, 8);
                        p = Out(p, end, " ebp=0x");
                        p = OutHex(p, end, (uint32_t)c->Ebp, 8);
                        p = Out(p, end, " eax=0x");
                        p = OutHex(p, end, (uint32_t)c->Eax, 8);
                        p = Out(p, end, " ebx=0x");
                        p = OutHex(p, end, (uint32_t)c->Ebx, 8);
                        p = Out(p, end, " ecx=0x");
                        p = OutHex(p, end, (uint32_t)c->Ecx, 8);
                        p = Out(p, end, " edx=0x");
                        p = OutHex(p, end, (uint32_t)c->Edx, 8);
                        p = Out(p, end, " esi=0x");
                        p = OutHex(p, end, (uint32_t)c->Esi, 8);
                        p = Out(p, end, " edi=0x");
                        p = OutHex(p, end, (uint32_t)c->Edi, 8);
                        p = Out(p, end, " efl=0x");
                        p = OutHex(p, end, (uint32_t)c->EFlags, 8);
                        p = OutCh(p, end, '\n');
                        p = ScanStack(p, end, (uint32_t)c->Esp, (uint32_t)c->Ebp);
                    }
                }
    #endif

                ClWrite(g_buf, (DWORD)(p - g_buf));
                InterlockedExchange(&g_last_exc_seq, seq);
                ClWriteDump(ep, seq);
            }
        }
    } __except (EXCEPTION_EXECUTE_HANDLER) {
        /* 记录器自身出错时保持静默，绝不能把宿主再弄崩 */
    }

    LeaveCriticalSection(&g_cs);
    t_in = 0;
}

static LONG CALLBACK ClVeh(PEXCEPTION_POINTERS ep) {
    ClLogException(ep, 0);
    return EXCEPTION_CONTINUE_SEARCH;
}

static LONG WINAPI ClTopFilter(PEXCEPTION_POINTERS ep) {
    ClLogException(ep, 1);
    if (g_prev_filter) return g_prev_filter(ep);
    return EXCEPTION_CONTINUE_SEARCH;
}

/* ---------- 安装 ---------- */

static int EnvFlag(const char* name) {
    char v[16];
    DWORD n = GetEnvironmentVariableA(name, v, sizeof(v));
    return n > 0 && n < sizeof(v) && v[0] != '0';
}

static void OwnerName(void) {
    HMODULE h = NULL;
    char path[MAX_PATH];
    const char* base;
    int i;
    int j = 0;

    if (!GetModuleHandleExA(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS |
                                GET_MODULE_HANDLE_EX_FLAG_UNCHANGED_REFCOUNT,
                            (LPCSTR)(uintptr_t)&CrashLogInstallFromEnv, &h)) {
        h = NULL;
    }
    if (!h || !GetModuleFileNameA(h, path, sizeof(path))) {
        StrCopy(g_owner, sizeof(g_owner), "crashlog");
        return;
    }
    base = path;
    for (i = 0; path[i]; ++i) {
        if (path[i] == '\\' || path[i] == '/') base = path + i + 1;
    }
    for (i = 0; base[i] && base[i] != '.' && j < (int)sizeof(g_owner) - 1; ++i)
        g_owner[j++] = base[i];
    g_owner[j] = 0;
    if (!g_owner[0]) StrCopy(g_owner, sizeof(g_owner), "crashlog");
}

static void BuildPaths(const char* dir, const char* explicit_log) {
    char pid[12];
    int n;

    OutDec(pid, pid + sizeof(pid) - 1, (uint32_t)GetCurrentProcessId());

    if (explicit_log) {
        int i;
        int cut = -1;
        StrCopy(g_log_path, sizeof(g_log_path), explicit_log);
        StrCopy(g_dump_dir, sizeof(g_dump_dir), explicit_log);
        for (i = 0; g_dump_dir[i]; ++i) {
            if (g_dump_dir[i] == '\\' || g_dump_dir[i] == '/') cut = i;
        }
        if (cut > 0) g_dump_dir[cut] = 0;
        else StrCopy(g_dump_dir, sizeof(g_dump_dir), ".");
        return;
    }

    StrCopy(g_log_path, sizeof(g_log_path), dir);
    n = 0;
    while (g_log_path[n]) ++n;
    if (n > 0 && g_log_path[n - 1] != '\\' && g_log_path[n - 1] != '/')
        StrAppend(g_log_path, sizeof(g_log_path), "\\");
    StrAppend(g_log_path, sizeof(g_log_path), "crash_");
    StrAppend(g_log_path, sizeof(g_log_path), g_owner);
    StrAppend(g_log_path, sizeof(g_log_path), "_");
    StrAppend(g_log_path, sizeof(g_log_path), pid);
    StrAppend(g_log_path, sizeof(g_log_path), ".log");
    StrCopy(g_dump_dir, sizeof(g_dump_dir), dir);
}

void CrashLogInstallFromEnv(void) {
    char dir[MAX_PATH * 2];
    char explicit_log[MAX_PATH * 2];
    char mutex_name[64];
    char pid[12];
    char* p;
    char* end;
    DWORD n;
    int have_dir = 0;
    int have_log = 0;

    if (InterlockedCompareExchange(&g_installed, 1, 0) != 0) return;

    n = GetEnvironmentVariableA("CRASHLOG_DIR", dir, sizeof(dir));
    if (n > 0 && n < sizeof(dir) && dir[0]) have_dir = 1;
    n = GetEnvironmentVariableA("CRASHLOG_LOG", explicit_log, sizeof(explicit_log));
    if (n > 0 && n < sizeof(explicit_log) && explicit_log[0]) have_log = 1;

    if (!have_dir && !have_log) {
        g_installed = 0;
        return;
    }

    /* 每个进程只允许一个安装者（b2/Squall/GL 代理可能同时带本记录器）。 */
    OutDec(pid, pid + sizeof(pid) - 1, (uint32_t)GetCurrentProcessId());
    StrCopy(mutex_name, sizeof(mutex_name), "Local\\CrashLogInst_");
    StrAppend(mutex_name, sizeof(mutex_name), pid);
    g_mutex = CreateMutexA(NULL, FALSE, mutex_name);
    if (g_mutex && GetLastError() == ERROR_ALREADY_EXISTS) {
        CloseHandle(g_mutex);
        g_mutex = NULL;
        g_installed = 0;
        return;
    }

    OwnerName();
    BuildPaths(have_dir ? dir : "", have_log ? explicit_log : NULL);
    g_dump = EnvFlag("CRASHLOG_DUMP") || EnvFlag("CRASHLOG_FULL");
    g_dump_full = EnvFlag("CRASHLOG_FULL");
    g_dump_all = EnvFlag("CRASHLOG_DUMP_ALL");

    if (!g_cs_ready) {
        InitializeCriticalSection(&g_cs);
        g_cs_ready = 1;
    }

    g_log = CreateFileA(g_log_path, GENERIC_WRITE,
                        FILE_SHARE_READ | FILE_SHARE_WRITE, NULL,
                        OPEN_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
    if (g_log == INVALID_HANDLE_VALUE) {
        /* 目录不存在时兜底建一级；仍失败就静默关闭（默认零成本）。 */
        CreateDirectoryA(g_dump_dir, NULL);
        g_log = CreateFileA(g_log_path, GENERIC_WRITE,
                            FILE_SHARE_READ | FILE_SHARE_WRITE, NULL,
                            OPEN_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
    }
    if (g_log == INVALID_HANDLE_VALUE) {
        if (g_mutex) {
            CloseHandle(g_mutex);
            g_mutex = NULL;
        }
        g_installed = 0;
        return;
    }
    SetFilePointer(g_log, 0, NULL, FILE_END);

    ResolveProbeFuncs();

    if (EnvFlag("CRASHLOG_DIALOG")) {
        g_dlg_stop = 0;
        g_dlg_thread = CreateThread(NULL, 0, ClDialogThread, NULL, 0, NULL);
    }

    g_veh = AddVectoredExceptionHandler(1, ClVeh);
    g_prev_filter = SetUnhandledExceptionFilter(ClTopFilter);
    if (g_dump) SetTimer(NULL, 0, 1000, ClPreloadTimer);

    RefreshModules();

    /* 用 64 KB 主缓冲：模块表通常 2–4 KB，1024 会截断并让下一条记录粘在残行上。 */
    p = g_buf;
    end = g_buf + sizeof(g_buf) - 1;
    *p = 0;
    p = Out(p, end, "CL1 v=1 pid=");
    p = OutDec(p, end, GetCurrentProcessId());
    p = Out(p, end, " owner=");
    p = Out(p, end, g_owner);
    p = Out(p, end, " exe=");
    {
        char exe[MAX_PATH];
        if (GetModuleFileNameA(NULL, exe, sizeof(exe))) p = Out(p, end, exe);
    }
    p = Out(p, end, " t=");
    {
        SYSTEMTIME st;
        GetLocalTime(&st);
        p = OutDec(p, end, st.wYear);
        p = OutCh(p, end, '-');
        p = OutDec2(p, end, st.wMonth);
        p = OutCh(p, end, '-');
        p = OutDec2(p, end, st.wDay);
        p = OutCh(p, end, 'T');
        p = OutDec2(p, end, st.wHour);
        p = OutCh(p, end, ':');
        p = OutDec2(p, end, st.wMinute);
        p = OutCh(p, end, ':');
        p = OutDec2(p, end, st.wSecond);
    }
    p = OutCh(p, end, '\n');
    p = EmitModules(p, end);
    ClWrite(g_buf, (DWORD)(p - g_buf));
}

void CrashLogUninstall(void) {
    if (g_dlg_thread) {
        InterlockedExchange(&g_dlg_stop, 1);
        if (WaitForSingleObject(g_dlg_thread, 1000) == WAIT_OBJECT_0) {
            CloseHandle(g_dlg_thread);
            g_dlg_thread = NULL;
        } else {
            /* 线程卡在窗口枚举里：保留日志与临界区，避免 use-after-free */
            return;
        }
    }
    if (g_veh) {
        RemoveVectoredExceptionHandler(g_veh);
        g_veh = NULL;
    }
    if (g_prev_filter) {
        SetUnhandledExceptionFilter(g_prev_filter);
        g_prev_filter = NULL;
    }
    if (g_cs_ready) {
        __try {
            if (g_log != INVALID_HANDLE_VALUE) {
                FlushFileBuffers(g_log);
                CloseHandle(g_log);
                g_log = INVALID_HANDLE_VALUE;
            }
        } __except (EXCEPTION_EXECUTE_HANDLER) {
            g_log = INVALID_HANDLE_VALUE;
        }
        DeleteCriticalSection(&g_cs);
        g_cs_ready = 0;
    }
}

/* ---------- 自测入口（仅独立 DLL 导出，不进代理导出表） ---------- */

#if CRASHLOG_STANDALONE

__declspec(dllexport) void __stdcall crashlog_selftest_av(void) {
    __try {
        *(volatile int*)(uintptr_t)0 = 1;
    } __except (EXCEPTION_EXECUTE_HANDLER) {
        /* 故意吞掉：验证 VEH 在 SEH 之前仍能看到 first-chance */
    }
}

__declspec(dllexport) void __stdcall crashlog_selftest_fp(void) {
    unsigned old = _controlfp(0, 0);
    __try {
        _controlfp(0, _EM_INVALID);   /* 清 invalid 屏蔽 ⇒ NaN/0÷0 触发 0xC0000090 */
        {
            volatile double z = 0.0;
            volatile double v = z / z;
            (void)v;
        }
    } __finally {
        /* 异常可能被外层的 ctypes/宿主接走；无论如何恢复控制字 */
        _controlfp(old, _MCW_EM);
    }
}

__declspec(dllexport) void __stdcall crashlog_selftest_raise(void) {
    DWORD args[2];
    args[0] = 1;
    args[1] = 0xDEADBEEF;
    __try {
        RaiseException(0xC0000005u, 0, 2, args);
    } __except (EXCEPTION_EXECUTE_HANDLER) {
        /* 故意吞掉：验证 RaiseException 形式的异常也能被 VEH 记录 */
    }
}

BOOL WINAPI DllMain(HINSTANCE inst, DWORD reason, LPVOID reserved) {
    (void)reserved;
    if (reason == DLL_PROCESS_ATTACH) {
        DisableThreadLibraryCalls(inst);
        CrashLogInstallFromEnv();
    } else if (reason == DLL_PROCESS_DETACH) {
        CrashLogUninstall();
    }
    return TRUE;
}

#endif /* CRASHLOG_STANDALONE */
