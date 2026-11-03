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
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#include "../crashlog/crashlog.h"

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
/* 只读 getter（热调用）：记录它们对状态没贡献，但占日志大头（一关里 ~60%）。
 * 保留「返回对象指针」的 getter（GetShapeList / Shape_GetBody / GetNext / GetBody1/2 /
 * GetWorld / GetUserData），因为重放要靠它们的返回值维持指针映射。
 * 设 B2PROXY_HOT=1 可关掉过滤、记录全部。 */
static char g_skip[256];
static const char* const kHotGetters[] = {
    "b2_Body_GetXForm", "b2_Body_GetVelocity", "b2_Body_GetOmega",
    "b2_Body_GetPosition", "b2_Body_GetAngle", "b2_Body_GetMass",
    "b2_Body_GetLocalPoint", "b2_Body_GetWorldVector", "b2_Body_GetLocalVector",
    "b2_Body_IsBullet", "b2_Body_IsFrozen", "b2_Body_GetAngularDamping",
    "b2_Shape_GetDensity", "b2_Body_GetIsSleeping", "b2_Body_GetXForm",
    "b2_Shape_GetFriction", "b2_Shape_GetRestitution", "b2_Shape_GetSensor",
    "b2_Shape_GetShapeType", "b2_Shape_GetCirclePos", "b2_Shape_GetCircleRadius",
    "b2_Shape_GetFilter", "b2_Shape_TestPoint",
    "b2_Joint_GetJointAngle", "b2_Joint_GetJointTranslation", "b2_Joint_GetMotorSpeed",
    "b2_Joint_GetReactionImpulse", "b2_Joint_GetReactionTorqImpulse",
    "b2_Joint_GetAnchor1", "b2_Joint_GetAnchor2", "b2_Joint_GetLimits",
    "b2_Joint_IsMotorEnabled", "b2_Joint_IsLimitEnabled",
    0};

static uint32_t g_id_step = 0;
static uint32_t g_id_create_body = 0;
static uint32_t g_id_destroy_body = 0;
static long g_step_no = 0;

static HANDLE g_file = INVALID_HANDLE_VALUE;
static HANDLE g_trace = INVALID_HANDLE_VALUE;
static int g_live = 0;   /* B2PROXY_LIVE=1：每步 digest 后立即刷盘，供闭环读位姿 */
static int g_light = 0;  /* B2PROXY_LIGHT=1：只写 digest/contacts，不写 pre/post */
/* B2CI_*：无鼠标的 CI 力伺服。磁铁位置 = 物体位置 + 朝目标的速度矢量，
 * 用 PD 力把物体推向目标；默认关闭。 */
static int g_ci_index = -1;
static int g_ci_armed = 0;
static int g_ci_mode = 0;   /* 0=PD force, 1=velocity servo */
static float g_ci_tx = 0.0f, g_ci_ty = 0.0f;
static float g_ci_maxspeed = 8.0f, g_ci_gain = 8.0f;
static float g_ci_force = 30.0f, g_ci_done = 0.4f;
static HANDLE g_ci_trace = INVALID_HANDLE_VALUE;
static char g_ci_cfg[MAX_PATH] = {0};
typedef void (__cdecl *CiForceFn)(void*, const float*, const float*);
typedef void (__cdecl *CiVoidFn)(void*);
static CiForceFn g_ci_force_fn = NULL;
static CiVoidFn g_ci_wake_fn = NULL;

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

static void LiveFlush(void) {
    if (!g_live || g_file == INVALID_HANDLE_VALUE) return;
    if (g_cs_ready) EnterCriticalSection(&g_cs);
    OutFlush();
    if (g_cs_ready) LeaveCriticalSection(&g_cs);
    FlushFileBuffers(g_file);
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
static __declspec(thread) int g_next_skip = 0;     /* 下一条调用的 pre 是否被跳过 */

/* 每次调用的「原返回地址」栈：宿主可能在 Step 里回调再进我们的导出，所以要按线程嵌套 */
typedef struct { uint32_t id; uint32_t ret; int skip; } Pending;
static __declspec(thread) Pending g_pend[16];
static __declspec(thread) int g_pdepth = 0;
static __declspec(thread) uint32_t g_lastret = 0;

static int Readable(const void* p) {
    if (!p || (uint32_t)p < 0x10000) return 0;
    return !IsBadReadPtr(p, MEM_DUMP);
}

/* B2PROXY_TRACE=path：为 ApplyForce 记录「谁调用了 wrapper」。
 * 桩在入口做了 pushfd+pushad；saved EBP 在 esp0-28，[saved EBP+4] 是
 * wrapper 的调用者返回地址。仅诊断用，默认零成本。
 * 附带的 p/tgt/mw 让「游戏自己施磁铁力」可判（F385）：body 位置来自 b2 body
 * 的 +8/+12；tgt/mw 来自 TLevelObjects 全局链（0x665334→+0x48 player→+8 mouse），
 * 用来核对 body == player+0x14 的对象 body、力方向 = mouse_world − body_pos。 */
static uint32_t SafeU32(uint32_t addr) {
    if (!addr || IsBadReadPtr((const void*)(uintptr_t)addr, 4)) return 0;
    return *(uint32_t*)(uintptr_t)addr;
}

static float SafeF32(uint32_t addr) {
    if (!addr || IsBadReadPtr((const void*)(uintptr_t)addr, 4)) return 0.0f;
    return *(float*)(uintptr_t)addr;
}

static void TraceForceCaller(uint32_t esp0, uint32_t body,
                             const unsigned char* force_mem) {
    uint32_t ebp, callers[4] = {0, 0, 0, 0};
    uint32_t fx = 0, fy = 0;
    float ffx = 0.0f, ffy = 0.0f;
    uint32_t base, mgr, player, mouse, target;
    float bx = 0.0f, by = 0.0f, mwx = 0.0f, mwy = 0.0f;
    char buf[320];
    int n;
    int i;
    if (g_trace == INVALID_HANDLE_VALUE) return;
    if (force_mem) {
        memcpy(&fx, force_mem, 4);
        memcpy(&fy, force_mem + 4, 4);
        memcpy(&ffx, force_mem, 4);
        memcpy(&ffy, force_mem + 4, 4);
    }
    if (ffx == 0.0f && ffy == 0.0f) return;  /* 只留非零力；-0.0 的位型非零 */
    if (IsBadReadPtr((const void*)(uintptr_t)(esp0 - 28), 4)) return;
    ebp = *(uint32_t*)(uintptr_t)(esp0 - 28);
    for (i = 0; i < 4; ++i) {
        if (IsBadReadPtr((const void*)(uintptr_t)(ebp + 4), 4)) break;
        callers[i] = *(uint32_t*)(uintptr_t)(ebp + 4);
        if (IsBadReadPtr((const void*)(uintptr_t)ebp, 4)) break;
        ebp = *(uint32_t*)(uintptr_t)ebp;
    }
    base = (uint32_t)(uintptr_t)GetModuleHandleA(NULL);
    mgr = SafeU32(base + 0x265334);
    player = SafeU32(mgr + 0x48);
    mouse = SafeU32(player + 8);
    target = SafeU32(player + 0x14);
    if (body && !IsBadReadPtr((const void*)(uintptr_t)body, 16)) {
        bx = *(float*)(uintptr_t)(body + 8);
        by = *(float*)(uintptr_t)(body + 12);
    }
    if (mouse) {
        mwx = SafeF32(mouse + 0x40);
        mwy = SafeF32(mouse + 0x44);
    }
    n = sprintf(buf, "body=%08x f=%08x,%08x c0=%08x c1=%08x c2=%08x c3=%08x seq=%u "
                     "p=%.4f,%.4f tgt=%08x mw=%.4f,%.4f\r\n",
                body, fx, fy, callers[0], callers[1], callers[2], callers[3],
                (unsigned)g_count, bx, by, target, mwx, mwy);
    {
        DWORD written = 0;
        WriteFile(g_trace, buf, (DWORD)n, &written, NULL);
        FlushFileBuffers(g_trace);
    }
}

static void CiApply(void) {
    void* body;
    char* b;
    float px, py, vx, vy, dx, dy, d, ux, uy, vdes, fx, fy, mag;
    float f[2], p[2];
    char buf[200];
    int n;
    if (g_ci_cfg[0]) {
        FILE* cf = fopen(g_ci_cfg, "r");
        if (cf) {
            int idx;
            float tx, ty;
            if (fscanf(cf, "%d,%f,%f", &idx, &tx, &ty) == 3) {
                g_ci_index = idx;
                g_ci_tx = tx;
                g_ci_ty = ty;
                g_ci_armed = 1;
            }
            fclose(cf);
        }
    }
    if (!g_ci_armed || g_ci_index < 0 || g_ci_index >= g_nbodies) return;
    body = g_bodies[g_ci_index];
    if (!body || IsBadReadPtr(body, 152)) return;
    b = (char*)body;
    px = *(float*)(b + 8);
    py = *(float*)(b + 12);
    vx = *(float*)(b + 68);
    vy = *(float*)(b + 72);
    dx = g_ci_tx - px;
    dy = g_ci_ty - py;
    d = (float)sqrt((double)(dx * dx + dy * dy));
    if (d < g_ci_done) return;
    ux = dx / d;
    uy = dy / d;
    if (!g_ci_force_fn)
        g_ci_force_fn = (CiForceFn)GetProcAddress(g_orig, "b2_Body_ApplyForce");
    if (!g_ci_wake_fn)
        g_ci_wake_fn = (CiVoidFn)GetProcAddress(g_orig, "b2_Body_WakeUp");
    if (g_ci_mode) {
        vdes = d * 4.0f;
        if (vdes < 2.0f) vdes = 2.0f;
        if (vdes > g_ci_maxspeed) vdes = g_ci_maxspeed;
        if (d < g_ci_done) vdes = 0.0f;
        if (g_ci_wake_fn) g_ci_wake_fn(body);
        *(float*)(b + 68) = ux * vdes;
        *(float*)(b + 72) = uy * vdes;
        if (g_ci_trace != INVALID_HANDLE_VALUE) {
            n = sprintf(buf, "seq=%u p=%.4f,%.4f vset=%.4f,%.4f d=%.4f mode=v\r\n",
                        (unsigned)g_count, px, py, ux * vdes, uy * vdes, d);
            if (n > 0) {
                DWORD written = 0;
                WriteFile(g_ci_trace, buf, (DWORD)n, &written, NULL);
            }
        }
        return;
    }
    vdes = d * 2.0f;
    if (vdes < 1.5f) vdes = 1.5f;
    if (vdes > g_ci_maxspeed) vdes = g_ci_maxspeed;
    fx = (ux * vdes - vx) * g_ci_gain;
    fy = (uy * vdes - vy) * g_ci_gain;
    mag = (float)sqrt((double)(fx * fx + fy * fy));
    if (mag > g_ci_force) {
        fx *= g_ci_force / mag;
        fy *= g_ci_force / mag;
    }
    if (g_ci_wake_fn) g_ci_wake_fn(body);
    if (g_ci_force_fn) {
        f[0] = fx;
        f[1] = fy;
        p[0] = px;
        p[1] = py;
        g_ci_force_fn(body, f, p);
    }
    if (g_ci_trace != INVALID_HANDLE_VALUE) {
        n = sprintf(buf, "seq=%u p=%.4f,%.4f v=%.4f,%.4f d=%.4f vdes=%.4f f=%.4f,%.4f\r\n",
                    (unsigned)g_count, px, py, vx, vy, d, vdes, fx, fy);
        if (n > 0) {
            DWORD written = 0;
            WriteFile(g_ci_trace, buf, (DWORD)n, &written, NULL);
        }
    }
}

/* ---------------------------------------------------------------------------
 * B2CI_FAKE_MAGNET：不移动真鼠标，伪造游戏的两个输入采样源，让原版自己走
 * 「按下 → 命中测试 → target 锁定 → min(315/d,30) 施力」的磁铁路径（F385）。
 *
 * 采样链（bin/gametop/game.exe 反汇编）：
 *   sub_561C70 每帧：GetCursorPos → mouse+0x30/+0x34（屏幕）
 *                    sub_4C3DB0(控件) 转客户区 → mouse+0x38/+0x3C
 *                    GetAsyncKeyState(1) → mouse+0x1F
 *                    sub_561D80 → mouse+0x40/+0x44（世界光标）
 *   sub_561F10 把当前按键存 mouse+0x1E（下一帧做边沿）
 *   sub_58E8DD 用 sub_561BB0/sub_561B8F 判按下/松开沿：
 *      按下 → sub_58E810 → sub_58E690（逐对象 vtable+0x74 命中测试）
 *             → 写 player+0x14（目标对象）/+0x10（激活）
 *   TLevelObjects.DoProgress → 0x58E5A0 → 0x58E4A0：读 mouse+0x40 施力
 *
 * 钩子只改 game.exe 的 IAT 槽（0x667330 / 0x66730C），env 未设时完全不动。
 * 配置热切换：B2CI_MAG_CONFIG 文件，内容 `world_x,world_y,button`（逗号分隔），
 * 每 15 ms 重读；button=1 表示按住左键。世界→屏幕用 F381 的 level 1 视口
 * （B2CI_MAG_VIEW 可覆盖：xmin,xmax,ytop,ybottom），客户区原点/尺寸运行时取。
 * 诊断：B2CI_MAG_TRACE=path 每 100 ms 记一行（world/client/screen/button）。
 * ------------------------------------------------------------------------- */

typedef BOOL (WINAPI *MagGetCursorPosFn)(LPPOINT);
typedef SHORT (WINAPI *MagGetAsyncKeyStateFn)(int);

static MagGetCursorPosFn g_real_gcp = NULL;
static MagGetAsyncKeyStateFn g_real_gaks = NULL;
static int g_mag_on = 0;
static char g_mag_cfg[MAX_PATH] = {0};
static HANDLE g_mag_trace = INVALID_HANDLE_VALUE;
static float g_mag_xmin = -28.2395129f, g_mag_xmax = 28.2395129f;
static float g_mag_ytop = 20.5f, g_mag_ybottom = -20.5f;
static float g_mag_wx = 0.0f, g_mag_wy = 0.0f;
static int g_mag_btn = 0;
static int g_mag_cfg_ok = 0;
static LONG g_mag_cfg_tick = 0;
static LONG g_mag_win_tick = 0;
static LONG g_mag_log_tick = 0;
static HWND g_mag_hwnd = NULL;

typedef struct { DWORD pid; HWND best; LONG area; } MagWinCtx;

static BOOL CALLBACK MagEnumProc(HWND h, LPARAM lp) {
    MagWinCtx* c = (MagWinCtx*)(uintptr_t)lp;
    char title[64];
    DWORD pid = 0;
    RECT r;
    LONG area;
    GetWindowThreadProcessId(h, &pid);
    if (pid != c->pid || !IsWindowVisible(h)) return TRUE;
    if (!GetClientRect(h, &r)) return TRUE;
    area = (r.right - r.left) * (r.bottom - r.top);
    if (area < 100 * 100) return TRUE;
    title[0] = 0;
    GetWindowTextA(h, title, sizeof(title));
    if (strstr(title, "Magnetic")) {
        c->best = h;
        c->area = 0x7fffffff;
        return FALSE;
    }
    if (area > c->area) {
        c->best = h;
        c->area = area;
    }
    return TRUE;
}

static HWND MagWindow(void) {
    DWORD now = GetTickCount();
    MagWinCtx c;
    if (g_mag_hwnd && now - (DWORD)g_mag_win_tick < 2000) return g_mag_hwnd;
    g_mag_win_tick = (LONG)now;
    c.pid = GetCurrentProcessId();
    c.best = NULL;
    c.area = 0;
    EnumWindows(MagEnumProc, (LPARAM)(uintptr_t)&c);
    g_mag_hwnd = c.best;
    return g_mag_hwnd;
}

static void MagLogLine(const char* s) {
    DWORD written = 0;
    if (g_mag_trace == INVALID_HANDLE_VALUE) return;
    WriteFile(g_mag_trace, s, (DWORD)strlen(s), &written, NULL);
    FlushFileBuffers(g_mag_trace);
}

static void MagReload(void) {
    DWORD now = GetTickCount();
    FILE* f;
    float x, y;
    int btn;
    if (now - (DWORD)g_mag_cfg_tick < 15) return;
    g_mag_cfg_tick = (LONG)now;
    if (!g_mag_cfg[0]) { g_mag_cfg_ok = 0; return; }
    f = fopen(g_mag_cfg, "r");
    if (!f) { g_mag_cfg_ok = 0; return; }
    if (fscanf(f, "%f,%f,%d", &x, &y, &btn) == 3) {
        g_mag_wx = x;
        g_mag_wy = y;
        g_mag_btn = btn ? 1 : 0;
        g_mag_cfg_ok = 1;
    } else {
        g_mag_cfg_ok = 0;
    }
    fclose(f);
}

static int MagWorldToScreen(float wx, float wy, POINT* out, float* cx_out,
                            float* cy_out) {
    HWND h = MagWindow();
    RECT rc;
    POINT org;
    float w, hh, cx, cy;
    if (!h || !out) return 0;
    if (!GetClientRect(h, &rc)) return 0;
    w = (float)(rc.right - rc.left);
    hh = (float)(rc.bottom - rc.top);
    if (w <= 0.0f || hh <= 0.0f) return 0;
    org.x = 0;
    org.y = 0;
    if (!ClientToScreen(h, &org)) return 0;
    cx = (wx - g_mag_xmin) / (g_mag_xmax - g_mag_xmin) * w;
    cy = (g_mag_ytop - wy) / (g_mag_ytop - g_mag_ybottom) * hh;
    out->x = org.x + (LONG)(cx >= 0.0f ? cx + 0.5f : cx - 0.5f);
    out->y = org.y + (LONG)(cy >= 0.0f ? cy + 0.5f : cy - 0.5f);
    if (cx_out) *cx_out = cx;
    if (cy_out) *cy_out = cy;
    return 1;
}

static void MagTracePoint(const POINT* p, float cx, float cy) {
    char buf[200];
    DWORD now = GetTickCount();
    int n;
    if (g_mag_trace == INVALID_HANDLE_VALUE) return;
    if (now - (DWORD)g_mag_log_tick < 100) return;
    g_mag_log_tick = (LONG)now;
    n = sprintf(buf, "t=%u btn=%d req=%.4f,%.4f client=%.2f,%.2f screen=%ld,%ld\r\n",
                (unsigned)now, g_mag_btn, g_mag_wx, g_mag_wy, cx, cy,
                (long)p->x, (long)p->y);
    if (n > 0) MagLogLine(buf);
}

static BOOL WINAPI MagGetCursorPos(LPPOINT pt) {
    POINT o;
    float cx = 0.0f, cy = 0.0f;
    if (!g_mag_on || !pt || !g_real_gcp) return g_real_gcp ? g_real_gcp(pt) : FALSE;
    MagReload();
    if (!g_mag_cfg_ok || !MagWorldToScreen(g_mag_wx, g_mag_wy, &o, &cx, &cy))
        return g_real_gcp(pt);
    *pt = o;
    MagTracePoint(&o, cx, cy);
    return TRUE;
}

static SHORT WINAPI MagGetAsyncKeyState(int vk) {
    if (!g_mag_on || !g_real_gaks) return g_real_gaks ? g_real_gaks(vk) : 0;
    if (vk == VK_LBUTTON) {
        MagReload();
        if (!g_mag_cfg_ok) return g_real_gaks(vk);
        return g_mag_btn ? (SHORT)0x8000 : 0;
    }
    return g_real_gaks(vk);
}

/* 按名字在 game.exe 的导入表里找 IAT 槽；返回 &slot（槽里是已解析的函数地址）。 */
static void** MagFindIat(HMODULE game, const char* dll, const char* name) {
    BYTE* base = (BYTE*)game;
    IMAGE_DOS_HEADER* dos;
    IMAGE_NT_HEADERS* nt;
    IMAGE_DATA_DIRECTORY* dir;
    IMAGE_IMPORT_DESCRIPTOR* imp;
    if (!game || !base) return NULL;
    dos = (IMAGE_DOS_HEADER*)base;
    if (dos->e_magic != IMAGE_DOS_SIGNATURE) return NULL;
    nt = (IMAGE_NT_HEADERS*)(base + dos->e_lfanew);
    if (nt->Signature != IMAGE_NT_SIGNATURE) return NULL;
    dir = &nt->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_IMPORT];
    if (!dir->VirtualAddress) return NULL;
    imp = (IMAGE_IMPORT_DESCRIPTOR*)(base + dir->VirtualAddress);
    for (; imp->Name; ++imp) {
        DWORD* oft;
        DWORD* ft;
        int i;
        if (_stricmp((const char*)(base + imp->Name), dll)) continue;
        oft = (DWORD*)(base + (imp->OriginalFirstThunk ? imp->OriginalFirstThunk
                                                        : imp->FirstThunk));
        ft = (DWORD*)(base + imp->FirstThunk);
        for (i = 0; oft[i]; ++i) {
            if (oft[i] & 0x80000000u) continue;
            if (strcmp((const char*)(base + (oft[i] & 0x7fffffffu) + 2), name))
                continue;
            return (void**)(ft + i);
        }
        return NULL;
    }
    return NULL;
}

static void MagInstall(void) {
    HMODULE game = GetModuleHandleA(NULL);
    void** s1 = MagFindIat(game, "user32.dll", "GetCursorPos");
    void** s2 = MagFindIat(game, "user32.dll", "GetAsyncKeyState");
    char view[128];
    DWORD prot = 0;
    if (!s1 || !s2) {
        MagLogLine("fake-magnet: IAT slots not found\r\n");
        return;
    }
    g_real_gcp = (MagGetCursorPosFn)*s1;
    g_real_gaks = (MagGetAsyncKeyStateFn)*s2;
    if (GetEnvironmentVariableA("B2CI_MAG_VIEW", view, sizeof(view)) > 0) {
        float a, b, c, d;
        if (sscanf(view, "%f,%f,%f,%f", &a, &b, &c, &d) == 4) {
            g_mag_xmin = a;
            g_mag_xmax = b;
            g_mag_ytop = c;
            g_mag_ybottom = d;
        }
    }
    if (VirtualProtect(s1, sizeof(void*), PAGE_EXECUTE_READWRITE, &prot)) {
        *s1 = (void*)MagGetCursorPos;
        VirtualProtect(s1, sizeof(void*), prot, &prot);
    }
    if (VirtualProtect(s2, sizeof(void*), PAGE_EXECUTE_READWRITE, &prot)) {
        *s2 = (void*)MagGetAsyncKeyState;
        VirtualProtect(s2, sizeof(void*), prot, &prot);
    }
    g_mag_on = 1;
    MagLogLine("fake-magnet: patched IAT GetCursorPos/GetAsyncKeyState\r\n");
}

/* cdecl( unsigned id, uint32_t esp0, uint32_t edx, uint32_t ecx ) */
void __cdecl log_call(unsigned id, uint32_t esp0, uint32_t edx, uint32_t ecx) {
    if (g_in) { g_next_skip = 1; return; }
    if (id == 0 || (int)id >= g_n_exports) return;
    if (id == g_id_step) CiApply();

    FARPROC fn = g_slot[id];
    if (!fn) {
        fn = GetProcAddress(g_orig, g_names[id]);
        InterlockedCompareExchangePointer((PVOID volatile*)&g_slot[id], (PVOID)fn, NULL);
        fn = g_slot[id];
    }
    if (!fn) return;              /* 解析失败：由调用方 jmp 0 暴露问题 */
    if (g_file == INVALID_HANDLE_VALUE) return;
    if (g_skip[id]) { g_next_skip = 1; return; }

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
        if (!g_light) Emit(&r, (DWORD)sizeof r);
        if (id == 1) TraceForceCaller(esp0, r.args[0], r.m1);
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
        g_pend[d].skip = g_next_skip;   /* 跳过意图随栈一起压，嵌套也不会吃错 */
        g_pdepth = d + 1;
    }
    g_next_skip = 0;
}

static void NoteBody(void* body) {
    int i;
    if (!body) return;
    for (i = 0; i < g_nbodies; ++i)
        if (g_bodies[i] == body) return;
    if (g_nbodies < MAX_BODIES) g_bodies[g_nbodies++] = body;
}

/* 销毁的 body 必须从摘要里剔除：指针会指向已释放/被复用的堆内存，
 * 上一版只增不减，导致 700+ 条假差异（F86）。 */
static void ForgetBody(void* body) {
    int i;
    if (!body) return;
    for (i = 0; i < g_nbodies; ++i) {
        if (g_bodies[i] == body) {
            g_bodies[i] = g_bodies[--g_nbodies];
            return;
        }
    }
}

typedef struct { uint32_t kind, seq, count, reserved; } DigestHdr;

/* 接触拓扑：偏移取自我们这份 Box2D 的 offsetof（F77 打印验证），
 * 用来判断"同一步原版和我们的接触对是否一致"——比分体状态更前置。 */
#define OFF_WORLD_CONTACTS   102984
#define OFF_CONTACT_NEXT     16
#define OFF_CONTACT_SHAPE1   52
#define OFF_CONTACT_SHAPE2   56
#define OFF_CONTACT_MANIFOLDS 8
#define MAX_CONTACTS 512
typedef struct { uint32_t shape1, shape2, manifolds; } ContactRec;
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

static void DumpContacts(void* world) {
    ContactRec buf[MAX_CONTACTS];
    DigestHdr hdr;
    uint32_t c;
    int n = 0;
    if (g_file == INVALID_HANDLE_VALUE || !world) return;
    if (IsBadReadPtr((char*)world + OFF_WORLD_CONTACTS, 4)) return;
    c = *(uint32_t*)((char*)world + OFF_WORLD_CONTACTS);
    while (c && n < MAX_CONTACTS) {
        if (IsBadReadPtr((void*)(uintptr_t)c, 60)) break;
        buf[n].shape1 = *(uint32_t*)(uintptr_t)(c + OFF_CONTACT_SHAPE1);
        buf[n].shape2 = *(uint32_t*)(uintptr_t)(c + OFF_CONTACT_SHAPE2);
        buf[n].manifolds = *(uint32_t*)(uintptr_t)(c + OFF_CONTACT_MANIFOLDS);
        ++n;
        c = *(uint32_t*)(uintptr_t)(c + OFF_CONTACT_NEXT);
    }
    hdr.kind = 3;
    hdr.seq = (uint32_t)g_step_no;
    hdr.count = (uint32_t)n;
    hdr.reserved = 0;
    Emit(&hdr, sizeof hdr);
    if (n) Emit(buf, (DWORD)(n * sizeof(ContactRec)));
}

/* 原 DLL 返回后：取出原返回地址，记录返回值 + 出参内存，返回原返回地址给桩去 jmp */
uint32_t __cdecl finish_call(unsigned id, uint32_t retval, uint32_t args_ptr) {
    uint32_t orig_ret = 0;
    int skip = 0;
    int d = g_pdepth - 1;
    if (d >= 0 && d < 16) {
        orig_ret = g_pend[d].ret;
        skip = g_pend[d].skip;
        g_pdepth = d;
    }
    g_lastret = retval;
    if (skip) {   /* 这条调用没记 pre，post 也不记，保持 pre/post 1:1 */
        if (id == g_id_create_body) NoteBody((void*)(uintptr_t)retval);
    else if (id == g_id_destroy_body && !IsBadReadPtr((const void*)(uintptr_t)args_ptr, 8)) {
        uint32_t a0 = *(const uint32_t*)(uintptr_t)args_ptr;
        uint32_t a1 = *(const uint32_t*)((uintptr_t)args_ptr + 4);
        (void)a0;                       /* DestroyBody(world, body) */
        ForgetBody((void*)(uintptr_t)a1);
    }
        else if (id == g_id_step) {
            DumpStepDigest();
            if (!IsBadReadPtr((const void*)(uintptr_t)args_ptr, 4))
                DumpContacts((void*)(uintptr_t)(*(const uint32_t*)(uintptr_t)args_ptr));
            LiveFlush();
        }
        return orig_ret;
    }
    if (id == g_id_create_body) NoteBody((void*)(uintptr_t)retval);
    else if (id == g_id_destroy_body && !IsBadReadPtr((const void*)(uintptr_t)args_ptr, 8)) {
        uint32_t a0 = *(const uint32_t*)(uintptr_t)args_ptr;
        uint32_t a1 = *(const uint32_t*)((uintptr_t)args_ptr + 4);
        (void)a0;                       /* DestroyBody(world, body) */
        ForgetBody((void*)(uintptr_t)a1);
    }
    else if (id == g_id_step) {
        uint32_t world = 0;
        DumpStepDigest();
        if (!IsBadReadPtr((const void*)(uintptr_t)args_ptr, 4))
            world = *(const uint32_t*)(uintptr_t)args_ptr;   /* Step(world, dt, vi, pi) */
        DumpContacts((void*)(uintptr_t)world);
        LiveFlush();
    }
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
        if (!g_light) Emit(&r, (DWORD)sizeof r);
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

/* T7.0 探针挂载：B2RTLPROBE_DLL 指向一个导出 rp_host_entry 的 FPC DLL。
 * 默认零成本（不设环境变量不建线程），只改这一处，不动导出表与日志格式。 */
static char g_probe_dll[MAX_PATH];

/* 定时器回调在主线程的消息循环里执行：探针的堆操作与宿主主线程不并发，
 * 这样测到的才是 RTL 语义本身，而不是两个线程抢同一个堆。 */
static void CALLBACK RtlProbeTimer(HWND hwnd, UINT msg, UINT_PTR id, DWORD tick) {
    HMODULE h;
    FARPROC f;
    (void)hwnd; (void)msg; (void)tick;
    KillTimer(NULL, id);
    h = LoadLibraryA(g_probe_dll);
    if (!h) return;
    f = GetProcAddress(h, "rp_host_entry");
    if (f) ((void (__stdcall *)(void))f)();
}

BOOL WINAPI DllMain(HINSTANCE inst, DWORD reason, LPVOID reserved) {
    (void)reserved;
    if (reason == DLL_PROCESS_ATTACH) {
        char self[MAX_PATH];
        char orig[MAX_PATH];
        char log[MAX_PATH];
        char live[16];
        char trace[MAX_PATH];
        char ci[256];
        DWORD n, tn;
        int i;

        CrashLogInstallFromEnv();   /* 默认零成本；CRASHLOG_DIR/CRASHLOG_LOG 才启用 */
        DisableThreadLibraryCalls(inst);
        n = GetEnvironmentVariableA("B2RTLPROBE_DLL", g_probe_dll, MAX_PATH);
        if (n > 0 && n < MAX_PATH)
            SetTimer(NULL, 0, 1500, RtlProbeTimer);   /* 主线程有消息循环后才回调 */
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
            if (g_names[i] && !strcmp(g_names[i], "b2_World_DestroyBody")) g_id_destroy_body = (uint32_t)i;
        }
        if (!GetEnvironmentVariableA("B2PROXY_HOT", log, MAX_PATH)) {
            int k;
            for (k = 0; kHotGetters[k]; ++k) {
                for (i = 1; i < g_n_exports; ++i) {
                    if (g_names[i] && !strcmp(g_names[i], kHotGetters[k])) g_skip[i] = 1;
                }
            }
        }
        n = GetEnvironmentVariableA("B2PROXY_LOG", log, MAX_PATH);
        g_live = GetEnvironmentVariableA("B2PROXY_LIVE", live, sizeof(live)) > 0;
        g_light = GetEnvironmentVariableA("B2PROXY_LIGHT", live, sizeof(live)) > 0;
        tn = GetEnvironmentVariableA("B2PROXY_TRACE", trace, MAX_PATH);
        if (tn > 0 && tn < MAX_PATH)
            g_trace = CreateFileA(trace, FILE_APPEND_DATA,
                                  FILE_SHARE_READ | FILE_SHARE_WRITE, NULL,
                                  OPEN_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
        if (GetEnvironmentVariableA("B2CI_INDEX", ci, sizeof(ci)) > 0) {
            g_ci_index = atoi(ci);
            if (GetEnvironmentVariableA("B2CI_TARGET", ci, sizeof(ci)) > 0) {
                if (sscanf(ci, "%f,%f", &g_ci_tx, &g_ci_ty) == 2)
                    g_ci_armed = 1;
            }
            if (GetEnvironmentVariableA("B2CI_MAXSPEED", ci, sizeof(ci)) > 0)
                g_ci_maxspeed = (float)atof(ci);
            if (GetEnvironmentVariableA("B2CI_GAIN", ci, sizeof(ci)) > 0)
                g_ci_gain = (float)atof(ci);
            if (GetEnvironmentVariableA("B2CI_FORCE", ci, sizeof(ci)) > 0)
                g_ci_force = (float)atof(ci);
            if (GetEnvironmentVariableA("B2CI_DONE", ci, sizeof(ci)) > 0)
                g_ci_done = (float)atof(ci);
            if (GetEnvironmentVariableA("B2CI_MODE", ci, sizeof(ci)) > 0)
                g_ci_mode = (ci[0] == 'v' || ci[0] == 'V' || atoi(ci) == 1);
            if (GetEnvironmentVariableA("B2CI_TRACE", ci, sizeof(ci)) > 0)
                g_ci_trace = CreateFileA(ci, FILE_APPEND_DATA,
                                         FILE_SHARE_READ | FILE_SHARE_WRITE, NULL,
                                         OPEN_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
        }
        if (GetEnvironmentVariableA("B2CI_FAKE_MAGNET", ci, sizeof(ci)) > 0) {
            GetEnvironmentVariableA("B2CI_MAG_CONFIG", g_mag_cfg, MAX_PATH);
            if (GetEnvironmentVariableA("B2CI_MAG_TRACE", ci, sizeof(ci)) > 0)
                g_mag_trace = CreateFileA(ci, FILE_APPEND_DATA,
                                          FILE_SHARE_READ | FILE_SHARE_WRITE, NULL,
                                          OPEN_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
            MagInstall();
        }
        GetEnvironmentVariableA("B2CI_CONFIG", g_ci_cfg, MAX_PATH);
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
        if (g_mag_trace != INVALID_HANDLE_VALUE) {
            FlushFileBuffers(g_mag_trace);
            CloseHandle(g_mag_trace);
            g_mag_trace = INVALID_HANDLE_VALUE;
        }
        if (g_ci_trace != INVALID_HANDLE_VALUE) {
            FlushFileBuffers(g_ci_trace);
            CloseHandle(g_ci_trace);
            g_ci_trace = INVALID_HANDLE_VALUE;
        }
        if (g_trace != INVALID_HANDLE_VALUE) {
            FlushFileBuffers(g_trace);
            CloseHandle(g_trace);
            g_trace = INVALID_HANDLE_VALUE;
        }
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
        CrashLogUninstall();
    }
    return TRUE;
}
