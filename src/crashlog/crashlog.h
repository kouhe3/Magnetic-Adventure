/* 进程内崩溃记录器（VEH + minidump）。
 *
 * 设计约束：
 *   - 默认零成本：只有设置 CRASHLOG_DIR / CRASHLOG_LOG 才注册 VEH、打开文件。
 *   - 只用 kernel32（minidump 时再动态加载 dbghelp），不依赖 CRT 的格式化/分配。
 *   - 记录在 VEH 里同步 WriteFile + FlushFileBuffers，宿主随后弹窗/退出/被杀都不丢。
 *
 * 依据：docs/facts.md F315（LCL 弹窗与 Halt(0)）、F316（VEH 捕获待证）。
 */
#ifndef CRASHLOG_H
#define CRASHLOG_H

#ifdef __cplusplus
extern "C" {
#endif

/* 幂等；未设置环境变量时直接返回（一次 GetEnvironmentVariable）。 */
void CrashLogInstallFromEnv(void);

/* 刷新并关闭日志、移除 VEH。 */
void CrashLogUninstall(void);

#ifdef __cplusplus
}
#endif

#endif /* CRASHLOG_H */
