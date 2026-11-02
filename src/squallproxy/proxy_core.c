/* 转发 DLL 核心（Squall）：加载原 Squall.dll 为 Squall_orig.dll，记录每次导出的
 * 实参（cdecl 栈上前 16 个 dword）+ ecx/edx + 返回地址，以及第 1/2 个实参
 * 指向的 128 字节内存（调用前后各一次，用于出参：GetDeviceName 的缓冲区在 arg1）。
 *
 * 记录格式（小端）：
 *   header: "SQFFI01" + u32 pid + u32 game_base + u32 orig_base
 *   kind=0: u32 kind,id,ret,ecx,edx,seq, args[16], m0[128], m1[128]
 *   kind=1: u32 kind,id,retval,seq, m0[128], m1[128]
 *
 * 依据：docs/facts.md F131（99 个导出、宿主只导入 17 个）、F136（上游源码与原版
 *       不等价，所以契约要以原版调用序为准）、F45/F46（同一套桩/尾跳透明方案）。
 */
#include <windows.h>
#include <stdint.h>
#include <string.h>
#include <stdlib.h>

#include "../crashlog/crashlog.h"

#define ARG_DWORDS 16
#define MEM_DUMP 128
#define ORIG_NAME "Squall_orig.dll"
#define ORIG_NAME_ALT "Squall.orig.dll"
#define ENV_LOG "SQUALL_LOG"

#pragma pack(push, 4)
typedef struct {
    uint32_t kind;      /* 0 */
    uint32_t id;
    uint32_t ret;       /* 原始返回地址 */
    uint32_t ecx;
    uint32_t edx;
    uint32_t seq;
    uint32_t args[ARG_DWORDS];
    uint8_t m0[MEM_DUMP];
    uint8_t m1[MEM_DUMP];
} PreRec;
typedef struct {
    uint32_t kind;      /* 1 */
    uint32_t id;
    uint32_t retval;    /* EAX */
    uint32_t seq;
    uint8_t m0[MEM_DUMP];  /* 调用后 args[0] 指向的内存 */
    uint8_t m1[MEM_DUMP];  /* 调用后 args[1] 指向的内存 */
} PostRec;
#pragma pack(pop)

extern const int g_n_exports;
extern const char* const g_names[];
extern FARPROC g_slot[];

static HANDLE g_file = INVALID_HANDLE_VALUE;
static HMODULE g_orig = 0;
static volatile LONG g_count = 0;
static __declspec(thread) int g_in = 0;

typedef struct { uint32_t id, ret; } Pending;
static __declspec(thread) Pending g_pend[16];
static __declspec(thread) int g_pdepth = 0;
static __declspec(thread) uint32_t g_lastret = 0;
/* 可选：Init 返回后把引擎切到指定设备（环回录制用，SQUALL_FORCE_DEVICE=<n>）。
 * 宿主本身从不调用 SQUALL_SetDevice，所以这只是测量时的旁路，不是契约的一部分。 */
static uint32_t g_id_init = 0;
static int g_force_device = -1;
typedef int (__cdecl *FN_SetDevice)(int);

/* 每条记录直接 WriteFile：录制结束用 TerminateProcess（跳过宿主与 DLL 的 DETACH），
 * 任何用户态缓冲都会丢失 —— 首轮实测 25 秒游戏跑完日志仍是 0 字节。音频调用量小
 * （每秒几十次），逐条写不会像 b2 那样成为卡顿源。 */
static CRITICAL_SECTION g_cs;
static int g_cs_ready = 0;

static void Emit(const void* p, DWORD n) {
    DWORD written = 0;
    if (g_file == INVALID_HANDLE_VALUE) return;
    if (g_cs_ready) EnterCriticalSection(&g_cs);
    WriteFile(g_file, p, n, &written, NULL);
    if (g_cs_ready) LeaveCriticalSection(&g_cs);
}

static int Readable(const void* p) {
    if (!p || (uint32_t)(uintptr_t)p < 0x10000) return 0;
    return !IsBadReadPtr(p, MEM_DUMP);
}

/* cdecl( unsigned id, uint32_t esp0, uint32_t edx, uint32_t ecx ) */
void __cdecl log_call(unsigned id, uint32_t esp0, uint32_t edx, uint32_t ecx) {
    FARPROC fn;
    PreRec r;
    if (g_in) return;                       /* 回调重入：不重复记 */
    if (id == 0 || (int)id >= g_n_exports) return;

    fn = g_slot[id];
    if (!fn) {
        fn = GetProcAddress(g_orig, g_names[id]);
        InterlockedCompareExchangePointer((PVOID volatile*)&g_slot[id], (PVOID)fn, NULL);
        fn = g_slot[id];
    }
    if (!fn || g_file == INVALID_HANDLE_VALUE) return;

    g_in = 1;
    r.kind = 0;
    r.id = id;
    r.ecx = ecx;
    r.edx = edx;
    r.ret = *(const uint32_t*)(uintptr_t)esp0;
    memcpy(r.args, (const void*)((uintptr_t)esp0 + 4), ARG_DWORDS * 4);
    memset(r.m0, 0, MEM_DUMP);
    memset(r.m1, 0, MEM_DUMP);
    if (Readable((const void*)(uintptr_t)r.args[0]))
        memcpy(r.m0, (const void*)(uintptr_t)r.args[0], MEM_DUMP);
    if (Readable((const void*)(uintptr_t)r.args[1]))
        memcpy(r.m1, (const void*)(uintptr_t)r.args[1], MEM_DUMP);
    r.seq = (uint32_t)InterlockedIncrement(&g_count);
    Emit(&r, (DWORD)sizeof r);
    g_in = 0;
}

/* 桩在把调用转给原 DLL 之前：记下「原返回地址」 */
void __cdecl save_ret(unsigned id, uint32_t orig_ret) {
    int d = g_pdepth;
    if (d < 0) d = 0;
    if (d < 16) {
        g_pend[d].id = id;
        g_pend[d].ret = orig_ret;
        g_pdepth = d + 1;
    }
}

/* 原 DLL 返回后：取出原返回地址，记录返回值 + 出参内存 */
uint32_t __cdecl finish_call(unsigned id, uint32_t retval, uint32_t args_ptr) {
    uint32_t orig_ret = 0;
    int d = g_pdepth - 1;
    if (d >= 0 && d < 16) {
        orig_ret = g_pend[d].ret;
        g_pdepth = d;
    }
    g_lastret = retval;
    if (id == g_id_init && g_force_device >= 0 && retval > 0) {
        FN_SetDevice sd = (FN_SetDevice)GetProcAddress(g_orig, "SQUALL_SetDevice");
        if (sd) sd(g_force_device);
        g_force_device = -1;   /* 只切一次 */
    }
    if (g_file != INVALID_HANDLE_VALUE && !g_in && args_ptr) {
        PostRec r;
        uint32_t a0 = *(const uint32_t*)(uintptr_t)args_ptr;
        uint32_t a1 = *(const uint32_t*)(uintptr_t)(args_ptr + 4);
        r.kind = 1;
        r.id = id;
        r.retval = retval;
        r.seq = (uint32_t)InterlockedIncrement(&g_count);
        memset(r.m0, 0, MEM_DUMP);
        memset(r.m1, 0, MEM_DUMP);
        if (Readable((const void*)(uintptr_t)a0))
            memcpy(r.m0, (const void*)(uintptr_t)a0, MEM_DUMP);
        if (Readable((const void*)(uintptr_t)a1))
            memcpy(r.m1, (const void*)(uintptr_t)a1, MEM_DUMP);
        g_in = 1;
        Emit(&r, (DWORD)sizeof r);
        g_in = 0;
    }
    return orig_ret;
}

/* 桩把返回值放回 EAX 用（finish_call 里已经写了文件，会破坏 EAX） */
uint32_t __cdecl get_ret(void) { return g_lastret; }

static void JoinDir(char* dst, const char* dir, const char* leaf) {
    int i = 0, j = 0;
    while (dir[i]) { dst[i] = dir[i]; ++i; }
    while (leaf[j]) { dst[i + j] = leaf[j]; ++j; }
    dst[i + j] = 0;
}

BOOL WINAPI DllMain(HINSTANCE inst, DWORD reason, LPVOID reserved) {
    (void)reserved;
    if (reason == DLL_PROCESS_ATTACH) {
        char self[MAX_PATH];
        char path[MAX_PATH];
        DWORD n;

        CrashLogInstallFromEnv();   /* 默认零成本；CRASHLOG_DIR/CRASHLOG_LOG 才启用 */
        DisableThreadLibraryCalls(inst);
        n = GetModuleFileNameA(inst, self, MAX_PATH);
        n = (n ? n - 1 : 0);
        while (n > 0 && self[n] != '\\') --n;
        self[n + 1] = 0;

        JoinDir(path, self, ORIG_NAME);
        g_orig = LoadLibraryA(path);
        if (!g_orig) {
            JoinDir(path, self, ORIG_NAME_ALT);
            g_orig = LoadLibraryA(path);
        }

        {
            int k;
            for (k = 1; k < g_n_exports; ++k)
                if (g_names[k] && !strcmp(g_names[k], "SQUALL_Init")) g_id_init = (uint32_t)k;
            if (GetEnvironmentVariableA("SQUALL_FORCE_DEVICE", path, MAX_PATH))
                g_force_device = atoi(path);
        }
        n = GetEnvironmentVariableA(ENV_LOG, path, MAX_PATH);
        if (n == 0 || n >= MAX_PATH) JoinDir(path, self, "squallffi.bin");
        g_file = CreateFileA(path, GENERIC_WRITE, FILE_SHARE_READ, NULL,
                             CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
        if (g_file != INVALID_HANDLE_VALUE) {
            struct {
                char magic[8];
                uint32_t pid;
                uint32_t game_base;
                uint32_t orig_base;
            } hdr;
            memcpy(hdr.magic, "SQFFI01", 8);
            hdr.pid = GetCurrentProcessId();
            hdr.game_base = (uint32_t)(uintptr_t)GetModuleHandleA(NULL);
            hdr.orig_base = (uint32_t)(uintptr_t)g_orig;
            InitializeCriticalSection(&g_cs);
            g_cs_ready = 1;
            Emit(&hdr, sizeof hdr);
        }
    } else if (reason == DLL_PROCESS_DETACH) {
        if (g_file != INVALID_HANDLE_VALUE) {
            FlushFileBuffers(g_file);
            CloseHandle(g_file);
            g_file = INVALID_HANDLE_VALUE;
        }
        if (g_orig) {
            FreeLibrary(g_orig);
            g_orig = 0;
        }
        CrashLogUninstall();
    }
    return TRUE;
}
