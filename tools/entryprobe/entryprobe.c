// entryprobe - entry-level hit counter for the F299 uncovered app functions.
//
// For each target VA: overwrite the prologue with `jmp stub`; the stub does
// `lock inc dword [count]`, replays the copied prologue bytes, then jumps back to
// target+L. ESP/registers are untouched (no pushfd: flags are not a calling
// convention input; prologues never read incoming flags).
//
// Loaded by the b2 proxy via B2RTLPROBE_DLL -> rp_host_entry (main-thread timer).
// ENTRY_OUT  : raw DWORD counts, EP_N entries, rewritten atomically every ENTRY_MS.
// ENTRY_LOG  : text log (installed/failed/targets).
// ENTRY_MS   : dump period (default 1000, min 200).

#include <windows.h>
#include "targets.inc"

static DWORD g_count[EP_N];
static char g_out[MAX_PATH];
static char g_log[MAX_PATH];
static volatile LONG g_busy;

static void logline(const char *s) {
    HANDLE f;
    DWORD n;
    if (!g_log[0]) return;
    f = CreateFileA(g_log, FILE_APPEND_DATA, FILE_SHARE_READ | FILE_SHARE_WRITE,
                    NULL, OPEN_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
    if (f != INVALID_HANDLE_VALUE) {
        WriteFile(f, s, lstrlenA(s), &n, NULL);
        WriteFile(f, "\r\n", 2, &n, NULL);
        CloseHandle(f);
    }
}

static void dump_counts(void) {
    char tmp[MAX_PATH + 8];
    HANDLE f;
    DWORD n;
    lstrcpyA(tmp, g_out);
    lstrcatA(tmp, ".tmp");
    if (InterlockedExchange(&g_busy, 1) != 0) return;
    f = CreateFileA(tmp, GENERIC_WRITE, 0, NULL, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
    if (f != INVALID_HANDLE_VALUE) {
        WriteFile(f, g_count, sizeof(g_count), &n, NULL);
        CloseHandle(f);
        MoveFileExA(tmp, g_out, MOVEFILE_REPLACE_EXISTING);
    }
    InterlockedExchange(&g_busy, 0);
}

static void CALLBACK dump_timer(HWND h, UINT m, UINT_PTR id, DWORD t) {
    (void)h; (void)m; (void)id; (void)t;
    dump_counts();
}

__declspec(dllexport) void __stdcall rp_host_entry(void) {
    BYTE *base = (BYTE *)GetModuleHandleA(NULL);
    BYTE *pool;
    char ms[32];
    DWORD period = 1000;
    int i, k, installed = 0, failed = 0;
    char buf[160];

    if (!GetEnvironmentVariableA("ENTRY_OUT", g_out, MAX_PATH)) return;
    GetEnvironmentVariableA("ENTRY_LOG", g_log, MAX_PATH);
    if (GetEnvironmentVariableA("ENTRY_MS", ms, sizeof(ms)) > 0) period = (DWORD)atoi(ms);
    if (period < 200) period = 200;

    pool = (BYTE *)VirtualAlloc(NULL, (SIZE_T)EP_N * 40, MEM_COMMIT | MEM_RESERVE,
                                PAGE_EXECUTE_READWRITE);
    if (!pool) return;

    for (i = 0; i < EP_N; i++) {
        BYTE *site = base + (g_va[i] - 0x400000);
        BYTE *code = pool + (SIZE_T)i * 40;
        DWORD old;
        int L = g_len[i];

        /* lock inc dword ptr [&g_count[i]] : F0 FF 05 disp32 */
        code[0] = 0xF0; code[1] = 0xFF; code[2] = 0x05;
        *(DWORD *)(code + 3) = (DWORD)(DWORD_PTR)&g_count[i];
        /* replay the original prologue bytes */
        CopyMemory(code + 7, site, (SIZE_T)L);
        /* jmp rel32 -> site + L */
        code[7 + L] = 0xE9;
        *(int *)(code + 8 + L) = (int)((site + L) - (code + 7 + L + 5));

        if (!VirtualProtect(site, (SIZE_T)L, PAGE_EXECUTE_READWRITE, &old)) { failed++; continue; }
        site[0] = 0xE9;
        *(int *)(site + 1) = (int)(code - (site + 5));
        for (k = 5; k < L; k++) site[k] = 0x90;
        VirtualProtect(site, (SIZE_T)L, old, &old);
        FlushInstructionCache(GetCurrentProcess(), site, (SIZE_T)L);
        installed++;
    }
    FlushInstructionCache(GetCurrentProcess(), pool, (SIZE_T)EP_N * 40);

    wsprintfA(buf, "ENTRY installed=%d failed=%d targets=%d", installed, failed, EP_N);
    logline(buf);
    dump_counts();
    SetTimer(NULL, 0, period, dump_timer);
}

BOOL WINAPI DllMain(HINSTANCE inst, DWORD reason, LPVOID reserved) {
    (void)reserved;
    if (reason == DLL_PROCESS_ATTACH) DisableThreadLibraryCalls(inst);
    return TRUE;
}
