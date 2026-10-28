/* 转发 DLL 核心：加载原 b2Physics.dll 为 b2Physics_orig.dll，记录每次导出的
 * 实参（cdecl 栈上 32 个 dword）+ ecx/edx + 返回地址，并 dump 第 2/3 个实参
 * 指向的 64 字节（用于结构体布局：body/shape/joint def）。
 *
 * 记录格式（小端，同 tools/ffi.py）：
 *   header: "B2FFI01" + u32 pid + u32 game_base + u32 orig_base
 *   record: u32 id, ret, ecx, edx, u32 args[32], u8 m0[64], m1[64], m2[64], u32 seq
 *
 * 依据：docs/facts.md F34（关节 def 布局未知）、F38（ReFilter 参数）、
 *       F29/F32/F40（已实测布局用本日志复核）。
 */
#include <windows.h>
#include <stdint.h>
#include <string.h>

#define ARG_DWORDS 32
#define MEM_DUMP 64

#pragma pack(push, 4)
typedef struct {
    uint32_t id;
    uint32_t ret;
    uint32_t ecx;
    uint32_t edx;
    uint32_t args[ARG_DWORDS];
    uint8_t m0[MEM_DUMP];
    uint8_t m1[MEM_DUMP];
    uint8_t m2[MEM_DUMP];
    uint32_t seq;
} Rec;
#pragma pack(pop)

extern const int g_n_exports;
extern const char* const g_names[];
extern FARPROC g_slot[];

static HANDLE g_file = INVALID_HANDLE_VALUE;
static HMODULE g_orig = 0;
static volatile LONG g_count = 0;
static __declspec(thread) int g_in = 0;

static int Readable(const void* p) {
    if (!p || (uint32_t)p < 0x10000) return 0;
    return !IsBadReadPtr(p, MEM_DUMP);
}

/* cdecl( unsigned id, uint32_t esp0, uint32_t edx, uint32_t ecx ) */
void __cdecl log_call(unsigned id, uint32_t esp0, uint32_t edx, uint32_t ecx) {
    if (g_in) return;
    if (id == 0 || (int)id >= g_n_exports) return;

    FARPROC fn = g_slot[id];
    if (!fn) {
        fn = GetProcAddress(g_orig, g_names[id]);
        InterlockedCompareExchangePointer((PVOID volatile*)&g_slot[id], (PVOID)fn, NULL);
        fn = g_slot[id];
    }
    if (!fn) return;              /* 解析失败：由调用方 jmp 0 暴露问题 */
    if (g_file == INVALID_HANDLE_VALUE) return;

    g_in = 1;
    {
        Rec r;
        DWORD written = 0;
        memset(&r, 0, sizeof r);
        r.id = id;
        r.ecx = ecx;
        r.edx = edx;
        r.ret = *(const uint32_t*)esp0;
        memcpy(r.args, (const void*)((uintptr_t)esp0 + 4), ARG_DWORDS * 4);
        if (Readable((const void*)(uintptr_t)r.args[0]))
            memcpy(r.m0, (const void*)(uintptr_t)r.args[0], MEM_DUMP);
        if (Readable((const void*)(uintptr_t)r.args[1]))
            memcpy(r.m1, (const void*)(uintptr_t)r.args[1], MEM_DUMP);
        if (Readable((const void*)(uintptr_t)r.args[2]))
            memcpy(r.m2, (const void*)(uintptr_t)r.args[2], MEM_DUMP);
        r.seq = (uint32_t)InterlockedIncrement(&g_count);
        WriteFile(g_file, &r, sizeof r, &written, NULL);
        if ((r.seq & 1023) == 0) FlushFileBuffers(g_file);
    }
    g_in = 0;
}

static void JoinDir(char* dst, const char* dir, const char* leaf) {
    int i = 0;
    while (dir[i]) { dst[i] = dir[i]; ++i; }
    int j = 0;
    while (leaf[j]) { dst[i + j] = leaf[j]; ++j; }
    dst[i + j] = 0;
}

BOOL WINAPI DllMain(HINSTANCE inst, DWORD reason, LPVOID reserved) {
    (void)reserved;
    if (reason == DLL_PROCESS_ATTACH) {
        char self[MAX_PATH];
        char orig[MAX_PATH];
        char log[MAX_PATH];
        DWORD n;
        int i;

        DisableThreadLibraryCalls(inst);
        n = GetModuleFileNameA(inst, self, MAX_PATH);
        i = (int)(n ? n - 1 : 0);
        while (i > 0 && self[i] != '\\') --i;
        self[i + 1] = 0;

        JoinDir(orig, self, "b2Physics_orig.dll");
        g_orig = LoadLibraryA(orig);
        if (!g_orig) {
            JoinDir(orig, self, "b2Physics.orig.dll");
            g_orig = LoadLibraryA(orig);
        }

        n = GetEnvironmentVariableA("B2PROXY_LOG", log, MAX_PATH);
        if (n == 0 || n >= MAX_PATH) JoinDir(log, self, "b2ffi.log");
        g_file = CreateFileA(log, GENERIC_WRITE, FILE_SHARE_READ, NULL,
                             CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
        if (g_file != INVALID_HANDLE_VALUE) {
            struct {
                char magic[8];
                uint32_t pid;
                uint32_t game_base;
                uint32_t orig_base;
            } hdr;
            DWORD written = 0;
            memcpy(hdr.magic, "B2FFI01", 8);
            hdr.pid = GetCurrentProcessId();
            hdr.game_base = (uint32_t)(uintptr_t)GetModuleHandleA(NULL);
            hdr.orig_base = (uint32_t)(uintptr_t)g_orig;
            WriteFile(g_file, &hdr, sizeof hdr, &written, NULL);
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
    }
    return TRUE;
}
