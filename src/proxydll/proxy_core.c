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
#define MEM_DUMP 128   /* 多边形 def 最多 24+8*8=88B，64 会截断顶点 */

#pragma pack(push, 4)
/* kind=0：调用前；kind=1：调用后（只看得到返回值与出参） */
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
    uint8_t m2[MEM_DUMP];
} PreRec;
typedef struct {
    uint32_t kind;      /* 1 */
    uint32_t id;
    uint32_t retval;    /* EAX（float 返回值在 ST0，取不到） */
    uint32_t seq;
    uint8_t m0[MEM_DUMP];  /* 调用后 args[0] 指向的内存（出参） */
} PostRec;
#pragma pack(pop)

extern const int g_n_exports;
extern const char* const g_names[];
extern FARPROC g_slot[];

/* post-Step 状态摘要：代理自己记下 CreateBody 返回的 body，每步 dump 一次状态。
 * 字段偏移见 docs/facts.md F26（flags+0, pos+8/+12, sweep.a+60, lv+68/+72, av+76, sleepTime+148）。 */
#define MAX_BODIES 512
static void* g_bodies[MAX_BODIES];
static int g_nbodies = 0;
static uint32_t g_id_step = 0;
static uint32_t g_id_create_body = 0;
static long g_step_no = 0;

static HANDLE g_file = INVALID_HANDLE_VALUE;

/* 8 MB 用户态缓冲：每次调用只做一次 memcpy，攒满再 WriteFile。
 * 之前每条记录一次 WriteFile + 每 1024 条 FlushFileBuffers，是游戏卡顿的主因。 */
#define OUT_BUF_SIZE (8u << 20)
static char g_out[OUT_BUF_SIZE];
static DWORD g_out_used = 0;
static CRITICAL_SECTION g_cs;
static int g_cs_ready = 0;

static void OutFlush(void) {
    DWORD written = 0;
    if (g_file == INVALID_HANDLE_VALUE || !g_out_used) return;
    WriteFile(g_file, g_out, g_out_used, &written, NULL);
    g_out_used = 0;
}

static void Emit(const void* p, DWORD n) {
    if (g_file == INVALID_HANDLE_VALUE) return;
    if (n >= OUT_BUF_SIZE) {                 /* 超大块：先刷再加直写 */
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
static HMODULE g_orig = 0;
static volatile LONG g_count = 0;
static __declspec(thread) int g_in = 0;

/* 每次调用的「原返回地址」栈：宿主可能在 Step 里回调再进我们的导出，所以要按线程嵌套 */
typedef struct { uint32_t id; uint32_t ret; } Pending;
static __declspec(thread) Pending g_pend[16];
static __declspec(thread) int g_pdepth = 0;
static __declspec(thread) uint32_t g_lastret = 0;

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
        PreRec r;
        r.kind = 0;
        r.id = id;
        r.ecx = ecx;
        r.edx = edx;
        r.ret = *(const uint32_t*)esp0;
        memcpy(r.args, (const void*)((uintptr_t)esp0 + 4), ARG_DWORDS * 4);
        memset(r.m0, 0, MEM_DUMP);
        memset(r.m1, 0, MEM_DUMP);
        memset(r.m2, 0, MEM_DUMP);
        if (Readable((const void*)(uintptr_t)r.args[0]))
            memcpy(r.m0, (const void*)(uintptr_t)r.args[0], MEM_DUMP);
        if (Readable((const void*)(uintptr_t)r.args[1]))
            memcpy(r.m1, (const void*)(uintptr_t)r.args[1], MEM_DUMP);
        if (Readable((const void*)(uintptr_t)r.args[2]))
            memcpy(r.m2, (const void*)(uintptr_t)r.args[2], MEM_DUMP);
        r.seq = (uint32_t)InterlockedIncrement(&g_count);
        Emit(&r, (DWORD)sizeof r);
    }
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

static void NoteBody(void* body) {
    int i;
    if (!body) return;
    for (i = 0; i < g_nbodies; ++i)
        if (g_bodies[i] == body) return;
    if (g_nbodies < MAX_BODIES) g_bodies[g_nbodies++] = body;
}

typedef struct { uint32_t kind, seq, count, reserved; } DigestHdr;
typedef struct {
    uint32_t ptr, flags;
    float sleepTime, vx, vy, w, px, py, angle;
    float mass, invMass, I, invI;
} BodyDigest;

static void DumpStepDigest(void) {
    BodyDigest buf[MAX_BODIES];
    DigestHdr hdr;
    int i, n = 0;
    DWORD written = 0;
    if (g_file == INVALID_HANDLE_VALUE) return;
    for (i = 0; i < g_nbodies; ++i) {
        char* b = (char*)g_bodies[i];
        if (IsBadReadPtr(b, 152)) continue;
        buf[n].ptr = (uint32_t)(uintptr_t)b;
        buf[n].flags = *(unsigned short*)(b + 0);
        buf[n].sleepTime = *(float*)(b + 148);
        buf[n].vx = *(float*)(b + 68);
        buf[n].vy = *(float*)(b + 72);
        buf[n].w = *(float*)(b + 76);
        buf[n].px = *(float*)(b + 8);
        buf[n].py = *(float*)(b + 12);
        buf[n].angle = *(float*)(b + 60);
        buf[n].mass = *(float*)(b + 124);
        buf[n].invMass = *(float*)(b + 128);
        buf[n].I = *(float*)(b + 132);
        buf[n].invI = *(float*)(b + 136);
        ++n;
    }
    hdr.kind = 2;
    hdr.seq = (uint32_t)++g_step_no;
    hdr.count = (uint32_t)n;
    hdr.reserved = 0;
    Emit(&hdr, sizeof hdr);
    if (n) Emit(buf, (DWORD)(n * sizeof(BodyDigest)));
}

/* 原 DLL 返回后：取出原返回地址，记录返回值 + 出参内存，返回原返回地址给桩去 jmp */
uint32_t __cdecl finish_call(unsigned id, uint32_t retval, uint32_t args_ptr) {
    uint32_t orig_ret = 0;
    int d = g_pdepth - 1;
    if (d >= 0 && d < 16) {
        orig_ret = g_pend[d].ret;
        g_pdepth = d;
    }
    g_lastret = retval;
    if (id == g_id_create_body) NoteBody((void*)(uintptr_t)retval);
    else if (id == g_id_step) DumpStepDigest();
    if (g_file != INVALID_HANDLE_VALUE && !g_in) {
        PostRec r;
        uint32_t a0 = *(const uint32_t*)args_ptr;
        memset(r.m0, 0, MEM_DUMP);
        r.kind = 1;
        r.id = id;
        r.retval = retval;
        r.seq = (uint32_t)InterlockedIncrement(&g_count);
        if (Readable((const void*)(uintptr_t)a0))
            memcpy(r.m0, (const void*)(uintptr_t)a0, MEM_DUMP);
        g_in = 1;
        Emit(&r, (DWORD)sizeof r);
        g_in = 0;
    }
    return orig_ret;
}

/* 桩把返回值放回 EAX 用（finish_call 里已经写了文件，会破坏 EAX） */
uint32_t __cdecl get_ret(void) { return g_lastret; }

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

        for (i = 0; i < g_n_exports; ++i) {
            if (g_names[i] && !strcmp(g_names[i], "b2_World_Step")) g_id_step = (uint32_t)i;
            if (g_names[i] && !strcmp(g_names[i], "b2_World_CreateBody")) g_id_create_body = (uint32_t)i;
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
            memcpy(hdr.magic, "B2FFI02", 8);   /* 02: MEM_DUMP 64->128 */
            hdr.pid = GetCurrentProcessId();
            hdr.game_base = (uint32_t)(uintptr_t)GetModuleHandleA(NULL);
            hdr.orig_base = (uint32_t)(uintptr_t)g_orig;
            InitializeCriticalSection(&g_cs);
            g_cs_ready = 1;
            Emit(&hdr, sizeof hdr);
        }
    } else if (reason == DLL_PROCESS_DETACH) {
        if (g_file != INVALID_HANDLE_VALUE) {
            OutFlush();
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
