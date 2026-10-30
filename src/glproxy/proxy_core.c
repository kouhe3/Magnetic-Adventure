/* GL 转发 DLL 核心：占住 opengl32.dll 文件名，把 368 个导出尾跳给改名副本
 * opengl32_orig.dll（失败再退到系统目录全路径加载），记录每次调用。
 *
 * v02（GLFFI02）在 v01 的「名字 + 时序」之上补 payload：栈上 12 个 dword
 * （glOrtho 的 6 个 double 要 12 个）+ 三块 192 B 指针内容
 * （args[0] / args[1] / args[8]——glTexImage2D 的像素指针在 args[8]）。
 * 时间窗：GLPROXY_T0/GLPROXY_T1（毫秒，从 DLL 加载算起），不设则全记。
 *
 * 记录格式（小端）：
 *   header: "GLFFI02" + u32 pid + u32 game_base + u32 orig_base
 *   record: u32 id, u32 tick, u64 qpc, u32 ret, u32 ecx, u32 edx,
 *           u32 args[12], u8 mem0[192], u8 mem1[192], u8 mem2[192]   = 652 B
 * 字符串：wglGetProcAddress 的入参首次出现时追加到 "<log>.names"
 *       每条解析结果追加到 "<log>.wglproc"（name, ret, 模块基名, keep/wrap）——
 *       GLScene 经它拿到的指针若指向 opengl32_orig 或驱动，调用就不进本日志。
 *       GLPROXY_FLUSH=1 每条记录立即落盘：进程被杀（TerminateProcess）时
 *       不会丢掉最后一次 200 ms flush 之后的尾巴——单帧宿主曾因此看起来
 *       "一条绘制调用都没有"。
 *
 * 依据：docs/facts.md F175（opengl32 不在 KnownDLLs）、F176（透明性已证）、
 *       F178（v01 看不到矩阵/纹素）；生成器 tools/gen_proxy.py。
 */
#include <windows.h>
#include <stdint.h>
#include <string.h>

#define ARG_DWORDS 12
#define MEM_DUMP 192
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
    uint8_t mem0[MEM_DUMP];   /* args[0] 指向的内存（矩阵 64B、颜色 16B…） */
    uint8_t mem1[MEM_DUMP];   /* args[1] 指向的内存 */
    uint8_t mem2[MEM_DUMP];   /* args[8] 指向的内存（glTexImage2D 的像素） */
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
static DWORD g_load_tick = 0;
static DWORD g_win_lo = 0;
static DWORD g_win_hi = 0xFFFFFFFFu;
static CRITICAL_SECTION g_cs;
static int g_cs_ready = 0;
static int g_in = 0;

static __declspec(thread) uint32_t g_lastret = 0;
static __declspec(thread) uint32_t g_pend[16];
static __declspec(thread) int g_pdepth = 0;

static uint32_t g_id_wglproc = 0;
static uint32_t g_id_teximage = 0;
static int g_flush_each = 0;
static HANDLE g_proc_file = INVALID_HANDLE_VALUE;
/* GLPROXY_ONLY=名字1,名字2,...：只记这些函数（启动期抓纹理上传/像素格式，
 * 不设则全记）。只影响「写不写记录」，解析/尾跳照旧。 */
static char g_only[512];
static int g_filter = 0;
static char g_seen[MAX_NEW_NAMES][64];
static int g_nseen = 0;
/* wglGetProcAddress 的名字：pre 阶段压栈，post 阶段弹出（同名函数可能重入） */
static __declspec(thread) const char* g_pnames[16];
static __declspec(thread) int g_npnames = 0;

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

static void SafeCopy(uint8_t* dst, uint32_t src, uint32_t n) {
    memset(dst, 0, n);
    if (!src || src < 0x10000) return;
    if (IsBadReadPtr((const void*)(uintptr_t)src, n)) return;
    memcpy(dst, (const void*)(uintptr_t)src, n);
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

static DWORD Since(DWORD tick) { return (DWORD)(tick - g_load_tick); }

/* 指针 → 模块基名（"opengl32_orig.dll"/"nvoglv32.dll"/"opengl32.dll"）。
 * 不落在任何模块（例如返回 0 或垃圾）时给 "?"。 */
static void BaseNameOf(uint32_t p, char* out, int cap) {
    HMODULE h = 0;
    char full[MAX_PATH];
    DWORD len, i;
    out[0] = 0;
    if (!p) return;
    if (!GetModuleHandleExA(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS |
                            GET_MODULE_HANDLE_EX_FLAG_UNCHANGED_REFCOUNT,
                            (LPCSTR)(uintptr_t)p, &h) || !h)
        return;
    len = GetModuleFileNameA(h, full, MAX_PATH);
    if (!len) return;
    i = len;
    while (i > 0 && full[i - 1] != '\\' && full[i - 1] != '/') --i;
    {
        int n = 0;
        while (full[i + n] && n < cap - 1) { out[n] = full[i + n]; ++n; }
        out[n] = 0;
    }
}

/* wglGetProcAddress 的解析结果：name<TAB>ret<TAB>module
 * 目的是把「函数指针是否绕过代理」变成可读的一行，而不是从缺失的调用去猜：
 * ret=0 ⇒ 名字是 1.1 核心函数（调用走静态导入 = 本代理）；ret 落在驱动
 * （如 igxelpicd32.dll）⇒ 扩展函数直连，本日志看不见。 */
static void NoteResolved(const char* name, uint32_t ret) {
    char line[320];
    char mod[MAX_PATH];
    int n = 0, i;
    DWORD written = 0;
    if (g_proc_file == INVALID_HANDLE_VALUE || !name) return;
    if (IsBadReadPtr(name, 1)) return;
    BaseNameOf(ret, mod, MAX_PATH);
    while (name[n] && n < 63) { line[n] = name[n]; ++n; }
    line[n++] = '\t';
    for (i = 7; i >= 0; --i) line[n++] = "0123456789abcdef"[(ret >> (i * 4)) & 0xF];
    line[n++] = '\t';
    i = 0;
    while (mod[i] && n < 300) { line[n++] = mod[i]; ++i; }
    if (!i) line[n++] = '?';
    line[n++] = '\n';
    if (g_cs_ready) EnterCriticalSection(&g_cs);
    WriteFile(g_proc_file, line, (DWORD)n, &written, NULL);
    if (g_cs_ready) LeaveCriticalSection(&g_cs);
}

/* CRC32（zlib 多项式）：Python 侧 zlib.crc32 直接对拍，比 FNV 快一个数量级。 */
static uint32_t Crc32(const unsigned char* p, uint64_t n) {
    static uint32_t table[256];
    static int init = 0;
    uint32_t c;
    uint64_t k;
    if (!init) {
        uint32_t i;
        for (i = 0; i < 256; ++i) {
            uint32_t v = i;
            int b;
            for (b = 0; b < 8; ++b) v = (v & 1) ? (0xEDB88320u ^ (v >> 1)) : (v >> 1);
            table[i] = v;
        }
        init = 1;
    }
    c = 0xFFFFFFFFu;
    for (k = 0; k < n; ++k) c = table[(c ^ p[k]) & 0xFF] ^ (c >> 8);
    return c ^ 0xFFFFFFFFu;
}

/* 桩入口：id, 栈指针（指向返回地址）, edx, ecx */
void __cdecl log_call(unsigned id, uint32_t esp0, uint32_t edx, uint32_t ecx) {
    FARPROC fn;
    if (id == g_id_wglproc) {
        if (g_npnames < 16)
            g_pnames[g_npnames++] = (const char*)(uintptr_t)
                *(const uint32_t*)((uintptr_t)esp0 + 4);
    }
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
    if (g_filter && !g_only[id]) return;

    g_in = 1;
    {
        Rec r;
        LARGE_INTEGER q;
        DWORD now = GetTickCount();
        DWORD rel = Since(now);
        int inwin = (rel >= g_win_lo && rel <= g_win_hi);
        QueryPerformanceCounter(&q);
        r.id = id;
        r.tick = now;
        r.qpc = (uint64_t)q.QuadPart;
        r.ret = *(const uint32_t*)(uintptr_t)esp0;
        r.ecx = ecx;
        r.edx = edx;
        memcpy(r.args, (const void*)((uintptr_t)esp0 + 4), ARG_DWORDS * 4);
        if (id == g_id_wglproc)
            NoteName((const char*)(uintptr_t)r.args[0]);
        if (inwin) {
            SafeCopy(r.mem0, r.args[0], MEM_DUMP);
            SafeCopy(r.mem1, r.args[1], MEM_DUMP);
            SafeCopy(r.mem2, r.args[8], MEM_DUMP);
            /* glTexImage2D：w/h/fmt/type 推出字节数，对整个像素缓冲算 FNV-1a，
             * 前 8 字节覆盖 mem2（hash, bytes）+ bpp。用来把纹理 id 精确映射回
             * pak 素材（192 B 前缀对均匀边界的图不够，见 F183）。 */
            if (id == g_id_teximage) {
                uint32_t w = r.args[3], h = r.args[4], fmt = r.args[6], ty = r.args[7];
                uint32_t ptr = r.args[8], bpp = 0;
                if (ty == 0x1401) {              /* GL_UNSIGNED_BYTE */
                    if (fmt == 0x1907) bpp = 3;      /* GL_RGB */
                    else if (fmt == 0x1908) bpp = 4; /* GL_RGBA */
                    else if (fmt == 0x80E1) bpp = 4; /* GL_BGRA */
                    else if (fmt == 0x1909) bpp = 1; /* GL_LUMINANCE */
                }
                if (bpp && w && h && ptr) {
                    uint64_t n = (uint64_t)w * h * bpp;
                    if (n <= (64u << 20) &&
                        !IsBadReadPtr((const void*)(uintptr_t)ptr, (SIZE_T)n)) {
                        const unsigned char* p = (const unsigned char*)(uintptr_t)ptr;
                        uint32_t hsh = Crc32(p, n), n32 = (uint32_t)n;
                        memcpy(r.mem2, &hsh, 4);
                        memcpy(r.mem2 + 4, &n32, 4);
                        r.mem2[8] = (unsigned char)bpp;
                    }
                }
            }
            Emit(&r, (DWORD)sizeof r);
            if (g_flush_each) OutFlush();
        }
        if (now - g_last_flush > FLUSH_MS) {
            OutFlush();
            g_last_flush = now;
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
    const char* name = 0;
    if (d >= 0 && d < 16) {
        orig_ret = g_pend[d];
        g_pdepth = d;
    }
    if (g_id_wglproc && id == g_id_wglproc) {
        int nd = g_npnames - 1;
        if (nd >= 0 && nd < 16) {
            name = g_pnames[nd];
            g_npnames = nd;
        }
        NoteResolved(name, retval);
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

static DWORD EnvMs(const char* name, DWORD dflt) {
    char buf[32];
    DWORD n = GetEnvironmentVariableA(name, buf, sizeof buf);
    if (n == 0 || n >= sizeof buf) return dflt;
    return (DWORD)strtoul(buf, NULL, 10);
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
        char proc[MAX_PATH];
        DWORD n;
        int i;

        DisableThreadLibraryCalls(inst);
        n = GetModuleFileNameA(inst, self, MAX_PATH);
        i = (int)(n ? n - 1 : 0);
        while (i > 0 && self[i] != '\\') --i;
        memcpy(dir, self, (size_t)i + 1);
        dir[i + 1] = 0;

        g_load_tick = GetTickCount();
        g_win_lo = EnvMs("GLPROXY_T0", 0);
        g_win_hi = EnvMs("GLPROXY_T1", 0xFFFFFFFFu);
        g_flush_each = (int)EnvMs("GLPROXY_FLUSH", 0);

        g_orig = LoadOrig(dir, inst);

        for (i = 1; i < g_n_exports; ++i) {
            if (g_names[i] && !strcmp(g_names[i], "wglGetProcAddress"))
                g_id_wglproc = (uint32_t)i;
            if (g_names[i] && !strcmp(g_names[i], "glTexImage2D"))
                g_id_teximage = (uint32_t)i;
        }

        n = GetEnvironmentVariableA("GLPROXY_LOG", log, MAX_PATH);
        if (n == 0 || n >= MAX_PATH) JoinDir(log, dir, "glffi.bin");
        {
            char want[512];
            DWORD wn = GetEnvironmentVariableA("GLPROXY_ONLY", want, sizeof want);
            if (wn > 0 && wn < sizeof want) {
                char* p = want;
                while (*p) {
                    char* comma = p;
                    int more;
                    while (*comma && *comma != ',') ++comma;
                    more = (*comma != 0);
                    if (*comma) *comma = 0;
                    for (i = 1; i < g_n_exports; ++i)
                        if (g_names[i] && !strcmp(g_names[i], p))
                            g_only[i] = 1;
                    if (!more) break;
                    p = comma + 1;
                }
                g_filter = 1;
            }
        }
        g_file = CreateFileA(log, GENERIC_WRITE, FILE_SHARE_READ, NULL,
                             CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
        JoinDir(names, log, ".names");
        g_names_file = CreateFileA(names, GENERIC_WRITE, FILE_SHARE_READ, NULL,
                                   CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
        JoinDir(proc, log, ".wglproc");
        g_proc_file = CreateFileA(proc, GENERIC_WRITE, FILE_SHARE_READ, NULL,
                                  CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
        if (g_file != INVALID_HANDLE_VALUE) {
            struct {
                char magic[8];
                uint32_t pid;
                uint32_t game_base;
                uint32_t orig_base;
            } hdr;
            memcpy(hdr.magic, "GLFFI02", 8);
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
        if (g_proc_file != INVALID_HANDLE_VALUE) {
            CloseHandle(g_proc_file);
            g_proc_file = INVALID_HANDLE_VALUE;
        }
        if (g_orig) {
            FreeLibrary(g_orig);
            g_orig = 0;
        }
    }
    return TRUE;
}
