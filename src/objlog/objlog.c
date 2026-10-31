// objlog: 进程内对象创建记录器。
//
// 原理：把 game.exe 里每个 `call <工厂>` 点（E8 rel32）改成 `call <thunk_i>`；
// thunk 把栈顶返回地址替换成自己的 ret 桩，再 jmp 到原工厂。工厂返回时落到 ret 桩，
// 桩 pushad/pushfd 后用原栈上的 eax/edx 记一行日志，popad/popfd 后 jmp 回原返回地址。
// 全程不暂停进程、不改变调用约定与栈布局，因此不会像断点那样打断关卡资源加载。
//
// 日志路径：环境变量 OBJLOG，缺省为 game.exe 同目录的 objlog.txt。
// 行格式与原 x64dbg logText 一致：#HB <tag> <eax> <edx> <[eax]> <[eax+8]> <[eax+0xC]> ["name"]

#include <windows.h>
#include "sites.h"

#define THUNK_LEN 36

static HANDLE g_file = INVALID_HANDLE_VALUE;
static CRITICAL_SECTION g_cs;
static BYTE *g_stub = NULL;
static BYTE *g_thunk[128];

static void log_text(const char *text)
{
    DWORD wr = 0;
    DWORD len = lstrlenA(text);
    EnterCriticalSection(&g_cs);
    WriteFile(g_file, text, len, &wr, NULL);
    LeaveCriticalSection(&g_cs);
}

// ---- 格式化（不依赖 CRT） ----
static char *put_hex(char *p, DWORD v)
{
    static const char *H = "0123456789ABCDEF";
    for (int i = 7; i >= 0; --i) *p++ = H[(v >> (i * 4)) & 0xF];
    return p;
}

static int readable(const void *ptr)
{
    DWORD v = (DWORD)(DWORD_PTR)ptr;
    return v >= 0x10000 && v < 0x7FFF0000;
}

static void log_one(int id, DWORD eax, DWORD edx)
{
    const OBJLOG_SITE *s = &kSites[id];
    char buf[256];
    char *p = buf;
    *p++ = '#'; *p++ = 'H'; *p++ = 'B'; *p++ = ' ';
    for (const char *q = s->tag; *q; ++q) *p++ = *q;
    *p++ = ' ';

    p = put_hex(p, eax); *p++ = ' ';
    p = put_hex(p, edx); *p++ = ' ';
    DWORD a = 0, b = 0, c = 0;
    char name[96];
    int name_len = 0;
    // 返回值不一定是有效指针：任何一次解引用都可能 AV，而游戏自己的 SEH 会
    // 捕获它并终止脚本线程（表现为“关卡物件消失”）。字段与名字分两段保护，
    // 避免名字读取失败时把已经读到的字段也清零。
    __try {
        a = *(DWORD *)eax;
        b = *(DWORD *)(eax + 8);
        c = *(DWORD *)(eax + 0xC);
    } __except (EXCEPTION_EXECUTE_HANDLER) {
        a = b = c = 0;
    }
    if (s->named) {
        __try {
            // x64dbg 的 {s:edx+8} 是内联字符串，不是二次指针
            const char *nm = (const char *)(edx + 8);
            for (int i = 0; i < 95 && nm[i]; ++i) name[name_len++] = nm[i];
        } __except (EXCEPTION_EXECUTE_HANDLER) {
            name_len = 0;
        }
    }
    p = put_hex(p, a); *p++ = ' ';
    p = put_hex(p, b); *p++ = ' ';
    p = put_hex(p, c);
    if (name_len) {
        *p++ = ' '; *p++ = '"';
        for (int i = 0; i < name_len; ++i) *p++ = name[i];
        *p++ = '"';
    }
    *p++ = '\n';

    EnterCriticalSection(&g_cs);
    DWORD wr = 0;
    WriteFile(g_file, buf, (DWORD)(p - buf), &wr, NULL);
    LeaveCriticalSection(&g_cs);
}

void __cdecl objlog_c(int id, DWORD eax, DWORD edx)
{
    __try {
        log_one(id, eax, edx);
    } __except (EXCEPTION_EXECUTE_HANDLER) {
    }
}

// ---- 代码生成 ----
static BYTE *emit_jmp(BYTE *p, void *dst)
{
    *p++ = 0xE9;
    *(DWORD *)p = (DWORD)(BYTE *)dst - (DWORD)(BYTE *)(p + 4);
    return p + 4;
}

static BYTE *emit_call(BYTE *p, void *dst)
{
    *p++ = 0xE8;
    *(DWORD *)p = (DWORD)(BYTE *)dst - (DWORD)(BYTE *)(p + 4);
    return p + 4;
}

static BYTE *alloc_stub(DWORD base)
{
    const DWORD size = 0x10000;
    for (DWORD k = 1; k < 0x40; ++k) {
        for (int sign = -1; sign <= 1; sign += 2) {
            BYTE *hint = (BYTE *)(DWORD_PTR)(base + (DWORD)(sign * (LONG)(k << 24)));
            BYTE *p = (BYTE *)VirtualAlloc(hint, size, MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);
            if (p) return p;
        }
    }
    return (BYTE *)VirtualAlloc(NULL, size, MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);
}

static void install(void)
{
    DWORD base = (DWORD)(DWORD_PTR)GetModuleHandleA(NULL);
    int n = (int)(sizeof(kSites) / sizeof(kSites[0]));
    g_stub = alloc_stub(base);
    if (!g_stub) { log_text("#INSTALL FAIL alloc\n"); return; }

    DWORD delta = base - 0x00400000;   // sites.h 里存的是 VA（原版镜像基址 0x400000）
    BYTE *cur = g_stub;
    for (int i = 0; i < n; ++i) {
        const OBJLOG_SITE *s = &kSites[i];
        BYTE *thunk = cur;
        g_thunk[i] = thunk;
        BYTE *ret = cur + 12;
        BYTE *p = thunk;
        *p++ = 0xC7; *p++ = 0x04; *p++ = 0x24;            // mov dword [esp], ret
        *(DWORD *)p = (DWORD)(DWORD_PTR)ret; p += 4;
        p = emit_jmp(p, (void *)(DWORD_PTR)(s->target + delta));  // jmp 原工厂
        p = ret;
        *p++ = 0x60;                                       // pushad
        *p++ = 0x9C;                                       // pushfd
        *p++ = 0x52;                                       // push edx（cdecl 右到左）
        *p++ = 0x50;                                       // push eax
        *p++ = 0x68; *(DWORD *)p = (DWORD)i; p += 4;       // push id
        p = emit_call(p, (void *)objlog_c);                // call objlog_c(id,eax,edx)
        *p++ = 0x83; *p++ = 0xC4; *p++ = 0x0C;             // add esp,12
        *p++ = 0x9D;                                       // popfd
        *p++ = 0x61;                                       // popad
        p = emit_jmp(p, (void *)(DWORD_PTR)(s->site + delta));  // jmp 回原返回地址
        cur = thunk + THUNK_LEN;
    }
    FlushInstructionCache(GetCurrentProcess(), g_stub, (DWORD)(cur - g_stub));

    int patched = 0;
    for (int i = 0; i < n; ++i) {
        const OBJLOG_SITE *s = &kSites[i];
        BYTE *thunk = g_thunk[i];
        BYTE *site = (BYTE *)(DWORD_PTR)(s->site + delta - 5);
        DWORD old = 0;
        if (!VirtualProtect(site, 5, PAGE_EXECUTE_READWRITE, &old)) continue;
        patched++;
        site[0] = 0xE8;
        *(DWORD *)(site + 1) = (DWORD)(BYTE *)thunk - (DWORD)(site + 5);
        VirtualProtect(site, 5, old, &old);
        FlushInstructionCache(GetCurrentProcess(), site, 5);
    }
    {
        char msg[64]; char *q = msg;
        const char *t = "#INSTALL patched=";
        while (*t) *q++ = *t++;
        { char d[8]; int dn = 0, k = patched; do { d[dn++] = (char)('0' + k % 10); k /= 10; } while (k); while (dn) *q++ = d[--dn]; }
        *q++ = '/';
        { char d[8]; int dn = 0, k = n; do { d[dn++] = (char)('0' + k % 10); k /= 10; } while (k); while (dn) *q++ = d[--dn]; }
        *q++ = '\n';
        DWORD wr = 0;
        EnterCriticalSection(&g_cs);
        WriteFile(g_file, msg, (DWORD)(q - msg), &wr, NULL);
        LeaveCriticalSection(&g_cs);
    }
}

static DWORD WINAPI setup_thread(LPVOID param)
{
    (void)param;
    char path[MAX_PATH];
    DWORD n = GetEnvironmentVariableA("OBJLOG", path, MAX_PATH);
    if (n == 0) {
        GetModuleFileNameA(NULL, path, MAX_PATH);
        char *slash = path;
        for (char *c = path; *c; ++c) if (*c == '\\') slash = c;
        *(slash + 1) = 0;
        lstrcatA(path, "objlog.txt");
    }
    g_file = CreateFileA(path, FILE_APPEND_DATA, FILE_SHARE_READ | FILE_SHARE_WRITE,
                         NULL, OPEN_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
    if (g_file == INVALID_HANDLE_VALUE) return 1;
    InitializeCriticalSection(&g_cs);
    if (GetEnvironmentVariableA("OBJLOG_NOPATCH", path, MAX_PATH)) {
        log_text("#INSTALL nopatch\n");
        return 0;
    }
    install();
    return 0;
}

BOOL APIENTRY DllMain(HMODULE mod, DWORD reason, LPVOID reserved)
{
    (void)reserved;
    if (reason == DLL_PROCESS_ATTACH) {
        DisableThreadLibraryCalls(mod);
        HANDLE t = CreateThread(NULL, 0, setup_thread, NULL, 0, NULL);
        if (t) CloseHandle(t);
    }
    return TRUE;
}
