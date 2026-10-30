/* GL 转发 DLL 核心：占住 opengl32.dll 文件名，把 368 个导出尾跳给改名副本
 * opengl32_orig.dll（失败再退到系统目录全路径加载），记录每次调用的
 * (id, tick, QPC, 返回地址, ecx/edx, 栈上前 6 个 dword)。
 *
 * 本版只记「名字面 + 时序」，不解码指针 payload（纹理像素、顶点数组）：
 * 先回答"原版一帧调了哪些函数、什么顺序、什么频率、有没有走扩展"。
 *
 * 记录格式（小端）：
 *   header: "GLFFI01" + u32 pid + u32 game_base + u32 orig_base
 *   record: u32 id, u32 tick, u64 qpc, u32 ret, u32 ecx, u32 edx, u32 args[6]
 * 字符串：wglGetProcAddress 的入参首次出现时追加到 "<log>.names"（一行一个）
 *
 * 依据：docs/facts.md F175（opengl32 不在 KnownDLLs、导入面 53+6 / GLU32 32）、
 *       F176（透明性待证）。
 * 生成物：tools/gen_proxy.py --csv mapping/opengl32-exports.csv --library opengl32
 */
#include <windows.h>
#include <stdint.h>
#include <string.h>

#define ARG_DWORDS 6
#define OUT_BUF_SIZE (4u << 20)
#define FLUSH_MS 200
#define MAX_NEW_NAMES 256

#pragma pack(push, 4)
typedef struct {
    uint32_t id;
    uint32_t tick;      /* GetTickCount（毫秒，粗细 10–16 ms） */
    uint64_t qpc;       /* QueryPerformanceCounter：帧/子帧的稳定时间轴 */
    uint32_t ret;       /* 原返回地址 */
    uint32_t ecx;
    uint32_t edx;
    uint32_t args[ARG_DWORDS];
} Rec;
#pragma pack(pop)

extern const int g_n_exports;
extern const char* const g_names[];
extern FARPROC g_slot[];

static HANDLE g_file = INVALID_HANDLE_VALUE;
static HANDLE g_names_file = INVALID_HANDLE_VALUE;
static HMODULE g_orig = 0;
static char g_out[OUT_BUF_SIZE];
static DWORD g_out_used = 0;
static DWORD g_last_flush = 0;
static CRITICAL_SECTION g_cs;
static int g_cs_ready = 0;
static int g_in = 0;

static __declspec(thread) uint32_t g_lastret = 0;
static __declspec(thread) uint32_t g_pend[16];
static __declspec(thread) int g_pdepth = 0;

static uint32_t g_id_wglproc = 0;
static char g_seen[MAX_NEW_NAMES][64];
static int g_nseen = 0;

static void OutFlush(void) {
    DWORD written = 0;
    if (g_file == INVALID_HANDLE_VALUE || !g_out_used) return;
    WriteFile(g_file, g_out, g_out_used, &written, NULL);
    g_out_used = 0;
}

static void Emit(const void* p, DWORD n) {
    if (g_file == INVALID_HANDLE_VALUE) return;
    if (n >= OUT_BUF_SIZE) {
        OutFlush();
        {
            DWORD written = 0;
            WriteFile(g_file, p, n, &written, NULL);
        }
        return;
    }
    if (g_cs_ready) EnterCriticalSection(&g_cs);
    if (g_out_used + n > OUT_BUF_SIZE) OutFlush();
    memcpy(g_out + g_out_used, p, n);
    g_out_used += n;
    if (g_cs_ready) LeaveCriticalSection(&g_cs);
}

/* wglGetProcAddress 的参数：记下字符串（去重），用于判断是否用了 1.1 之外的扩展 */
static void NoteName(const char* s) {
    int i;
    char line[72];
    int n = 0;
    if (!s || g_names_file == INVALID_HANDLE_VALUE) return;
    if (IsBadReadPtr(s, 1)) return;
    for (i = 0; i < g_nseen; ++i)
        if (!strcmp(g_seen[i], s)) return;
    if (g_nseen >= MAX_NEW_NAMES) return;
    while (s[n] && n < 63) { g_seen[g_nseen][n] = s[n]; ++n; }
    g_seen[g_nseen][n] = 0;
    ++g_nseen;
    memcpy(line, g_seen[g_nseen - 1], (size_t)n + 1);
    line[n] = '\n';
    {
        DWORD written = 0;
        WriteFile(g_names_file, line, (DWORD)(n + 1), &written, NULL);
    }
}

/* 桩入口：id, 栈指针（指向返回地址）, edx, ecx */
void __cdecl log_call(unsigned id, uint32_t esp0, uint32_t edx, uint32_t ecx) {
    FARPROC fn;
    if (g_in) return;
    if (id == 0 || (int)id >= g_n_exports) return;

    fn = g_slot[id];
    if (!fn) {
        fn = GetProcAddress(g_orig, g_names[id]);
        if (fn) {
            InterlockedCompareExchangePointer((PVOID volatile*)&g_slot[id], (PVOID)fn, NULL);
            fn = g_slot[id];
        }
    }
    if (!fn) return;                    /* 解析失败：桩会 jmp NULL，问题立刻暴露 */
    if (g_file == INVALID_HANDLE_VALUE) return;

    g_in = 1;
    {
        Rec r;
        LARGE_INTEGER q;
        QueryPerformanceCounter(&q);
        r.id = id;
        r.tick = GetTickCount();
        r.qpc = (uint64_t)q.QuadPart;
        r.ret = *(const uint32_t*)(uintptr_t)esp0;
        r.ecx = ecx;
        r.edx = edx;
        memcpy(r.args, (const void*)((uintptr_t)esp0 + 4), ARG_DWORDS * 4);
        Emit(&r, (DWORD)sizeof r);
        if (id == g_id_wglproc)
            NoteName((const char*)(uintptr_t)r.args[0]);
        if (GetTickCount() - g_last_flush > FLUSH_MS) {
            OutFlush();
            g_last_flush = GetTickCount();
        }
    }
    g_in = 0;
}

/* 桩把调用转给原 DLL 之前：压入「原返回地址」 */
void __cdecl save_ret(unsigned id, uint32_t orig_ret) {
    int d = g_pdepth;
    if (d < 0) d = 0;
    if (d < 16) {
        g_pend[d] = orig_ret;
        g_pdepth = d + 1;
    }
    (void)id;
}

/* 原函数返回到 post 桩：取回原返回地址，暂存 EAX 供 get_ret 还原 */
uint32_t __cdecl finish_call(unsigned id, uint32_t retval, uint32_t args_ptr) {
    uint32_t orig_ret = 0;
    int d = g_pdepth - 1;
    if (d >= 0 && d < 16) {
        orig_ret = g_pend[d];
        g_pdepth = d;
    }
    g_lastret = retval;
    (void)id;
    (void)args_ptr;
    return orig_ret;
}

/* post 桩把返回值放回 EAX 用（finish_call 的返回过程会破坏 EAX） */
uint32_t __cdecl get_ret(void) { return g_lastret; }

static void JoinDir(char* dst, const char* dir, const char* leaf) {
    int i = 0;
    while (dir[i]) { dst[i] = dir[i]; ++i; }
    {
        int j = 0;
        while (leaf[j]) { dst[i + j] = leaf[j]; ++j; }
        dst[i + j] = 0;
    }
}

/* 加载真身：优先改名副本；退到系统目录全路径（但要防回落到自己） */
static HMODULE LoadOrig(const char* selfdir, HINSTANCE self) {
    const char* cand[] = { "opengl32_orig.dll", "opengl32.orig.dll", "orig\\opengl32.dll" };
    HMODULE m;
    int i;
    char path[MAX_PATH];
    for (i = 0; i < 3; ++i) {
        JoinDir(path, selfdir, cand[i]);
        m = LoadLibraryA(path);
        if (m) return m;
    }
    {
        UINT n = GetSystemDirectoryA(path, MAX_PATH);
        if (n && n < MAX_PATH) {
            JoinDir(path + n, "\\", "opengl32.dll");
            m = LoadLibraryA(path);
            if (m && m != (HMODULE)self) return m;
            if (m) FreeLibrary(m);     /* 回落到自己：无限递归，必须放弃 */
        }
    }
    return 0;
}

BOOL WINAPI DllMain(HINSTANCE inst, DWORD reason, LPVOID reserved) {
    (void)reserved;
    if (reason == DLL_PROCESS_ATTACH) {
        char self[MAX_PATH];
        char dir[MAX_PATH];
        char log[MAX_PATH];
        char names[MAX_PATH];
        DWORD n;
        int i;

        DisableThreadLibraryCalls(inst);
        n = GetModuleFileNameA(inst, self, MAX_PATH);
        i = (int)(n ? n - 1 : 0);
        while (i > 0 && self[i] != '\\') --i;
        memcpy(dir, self, (size_t)i + 1);
        dir[i + 1] = 0;

        g_orig = LoadOrig(dir, inst);

        for (i = 1; i < g_n_exports; ++i) {
            if (g_names[i] && !strcmp(g_names[i], "wglGetProcAddress"))
                g_id_wglproc = (uint32_t)i;
        }

        n = GetEnvironmentVariableA("GLPROXY_LOG", log, MAX_PATH);
        if (n == 0 || n >= MAX_PATH) JoinDir(log, dir, "glffi.bin");
        g_file = CreateFileA(log, GENERIC_WRITE, FILE_SHARE_READ, NULL,
                             CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
        JoinDir(names, log, ".names");
        g_names_file = CreateFileA(names, GENERIC_WRITE, FILE_SHARE_READ, NULL,
                                   CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
        if (g_file != INVALID_HANDLE_VALUE) {
            struct {
                char magic[8];
                uint32_t pid;
                uint32_t game_base;
                uint32_t orig_base;
            } hdr;
            memcpy(hdr.magic, "GLFFI01", 8);
            hdr.pid = GetCurrentProcessId();
            hdr.game_base = (uint32_t)(uintptr_t)GetModuleHandleA(NULL);
            hdr.orig_base = (uint32_t)(uintptr_t)g_orig;
            InitializeCriticalSection(&g_cs);
            g_cs_ready = 1;
            g_last_flush = GetTickCount();
            Emit(&hdr, sizeof hdr);
        }
    } else if (reason == DLL_PROCESS_DETACH) {
        if (g_file != INVALID_HANDLE_VALUE) {
            OutFlush();
            FlushFileBuffers(g_file);
            CloseHandle(g_file);
            g_file = INVALID_HANDLE_VALUE;
        }
        if (g_names_file != INVALID_HANDLE_VALUE) {
            CloseHandle(g_names_file);
            g_names_file = INVALID_HANDLE_VALUE;
        }
        if (g_orig) {
            FreeLibrary(g_orig);
            g_orig = 0;
        }
    }
    return TRUE;
}
