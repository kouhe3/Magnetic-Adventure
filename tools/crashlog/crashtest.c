#include <windows.h>
#include <stdint.h>

/* 测试夹具：b2 代理的 B2RTLPROBE_DLL 定时器在主线程调用本入口。
 * 故意解引用空指针且不吞掉异常，模拟“异常逃逸到 LCL 主循环”的宿主崩溃；
 * crashlog 的 VEH 应先记录，随后 LCL 弹 MB_OKCANCEL（F315）并可 Cancel 退出 0。
 * 依据：docs/facts.md F315、F316。 */
void __stdcall rp_host_entry(void) {
    *(volatile int*)(uintptr_t)0 = 1;
}

BOOL WINAPI DllMain(HINSTANCE inst, DWORD reason, LPVOID reserved) {
    (void)inst;
    (void)reason;
    (void)reserved;
    return TRUE;
}
