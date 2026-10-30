// 宿主脚手架（T3.1）：把原版 game.exe 的窗口/消息参数按实测值复刻出来，
// 供 tools/winprobe.py 与原版逐字段对拍。
//
// 依据（docs/facts.md）：
//   F153 宿主是 Lazarus/LCL；F154 窗口化主窗口 1024×768 / 客户区 1018×739 /
//        style 0x96CA0000 / exstyle 0x100 / 桌面居中 / DPI unaware；
//   F155 窗口类：CS_DBLCLKS、hbrBackground=NULL、IDC_ARROW、MAINICON、类名 "Window"；
//   F156 主循环 PeekMessage + MsgWaitForMultipleObjects（无消息时真阻塞）；
//   F158 唯一的子窗口 = 填满客户区的 GL 视口（style 0x56000000）。
//
#include <windows.h>

#include <cstdarg>
#include <cstdio>
#include <cstdlib>

#include "gl_render.h"

namespace {

const wchar_t kClassName[] = L"Window";
const wchar_t kHintClassName[] = L"HintWindow";
const wchar_t kTitle[] = L"A Magnetic Adventure";

// 原版窗口化尺寸：客户区 1018×739、外框 1024×768（F154）。
// LCL 的语义是「TForm.Width/Height = 客户区，外框由 AdjustWindowRectEx 补」（F164），
// 这里照抄；外框能正好 1024×768 靠的是 PE 子系统版本 5.01（F166）。
const int kClientW = 1018;
const int kClientH = 739;

// T3.2 里程碑 A：建 GL 上下文、按抓到的绘制列表画菜单（F181/F182/F183/F184）。
const UINT_PTR kRenderTimer = 1;
const UINT kRenderIntervalMs = 15;  // F177：菜单/关卡实测恒 61–65 swap/s ≈ 15.6 ms

HWND g_viewer = nullptr;
FILE* g_log = nullptr;

void Log(const char* fmt, ...) {
  if (!g_log) return;
  va_list ap;
  va_start(ap, fmt);
  vfprintf(g_log, fmt, ap);
  va_end(ap);
  fputc('\n', g_log);
  fflush(g_log);
}

// 子窗口就是 GL 视口的位置：原版 style = WS_CHILD|WS_VISIBLE|WS_CLIPSIBLINGS|WS_CLIPCHILDREN
const DWORD kViewerStyle = WS_CHILD | WS_VISIBLE | WS_CLIPSIBLINGS | WS_CLIPCHILDREN;

LRESULT CALLBACK ViewerProc(HWND hwnd, UINT msg, WPARAM wp, LPARAM lp) {
  switch (msg) {
    case WM_ERASEBKGND:
      return 1;  // 原版 hbrBackground = NULL，且 GL 会覆盖整幅
    default:
      break;
  }
  return DefWindowProcW(hwnd, msg, wp, lp);
}

LRESULT CALLBACK FormProc(HWND hwnd, UINT msg, WPARAM wp, LPARAM lp) {
  switch (msg) {
    case WM_CREATE: {
      // 窗体与视口共用同一个窗口类（原版两层的类名都是 "Window"，F155/F158），
      // 所以只能靠 parent 区分：只有顶层窗（hWndParent == NULL）才建视口，
      // 否则子窗口的 WM_CREATE 会再建一个子窗口，无限递归。
      auto* cs = reinterpret_cast<CREATESTRUCTW*>(lp);
      if (!cs || cs->hwndParent != nullptr) return 0;
      g_viewer = CreateWindowExW(0, kClassName, L"", kViewerStyle, 0, 0, 1, 1,
                                 hwnd, nullptr, GetModuleHandleW(nullptr), nullptr);
      Log("WM_CREATE viewer=%p", static_cast<void*>(g_viewer));
      return 0;
    }
    case WM_SIZE:
      if (g_viewer) {
        MoveWindow(g_viewer, 0, 0, LOWORD(lp), HIWORD(lp), TRUE);
        GlResize(LOWORD(lp), HIWORD(lp));
        GlRenderMenu();
        Log("WM_SIZE %dx%d", LOWORD(lp), HIWORD(lp));
      }
      return 0;
    case WM_TIMER:
      if (wp == kRenderTimer) {
        GlRenderMenu();
        return 0;
      }
      break;
    case WM_PAINT: {
      // 有失效就重画：内容来自绘制列表，不需要 BeginPaint 的返回值
      GlRenderMenu();
      PAINTSTRUCT ps;
      BeginPaint(hwnd, &ps);
      EndPaint(hwnd, &ps);
      return 0;
    }
    case WM_ERASEBKGND:
      return 1;
    case WM_LBUTTONDOWN:
    case WM_LBUTTONUP:
    case WM_MOUSEMOVE:
    case WM_KEYDOWN:
    case WM_KEYUP:
      // T3.1 只验证消息能到：有 HOST_LOG 时落盘，后续 T3.4 才接场景
      Log("msg=0x%04X wp=0x%08X lp=0x%08X", msg, static_cast<unsigned>(wp),
          static_cast<unsigned>(lp));
      break;
    case WM_CLOSE:
      DestroyWindow(hwnd);
      return 0;
    case WM_DESTROY:
      PostQuitMessage(0);
      return 0;
    default:
      break;
  }
  return DefWindowProcW(hwnd, msg, wp, lp);
}

// 复刻 F155：类名 "Window"，style=CS_DBLCLKS，hIcon=MAINICON（失败退 IDI_APPLICATION），
// hCursor=IDC_ARROW，hbrBackground=NULL，无菜单。
bool RegisterClasses(HINSTANCE inst) {
  const char* log_path = std::getenv("HOST_LOG");
  if (log_path) g_log = std::fopen(log_path, "w");

  WNDCLASSEXW wc = {};
  wc.cbSize = sizeof(wc);
  wc.style = CS_DBLCLKS;
  wc.lpfnWndProc = FormProc;
  wc.hInstance = inst;
  wc.hIcon = LoadIconW(inst, L"MAINICON");
  if (!wc.hIcon) wc.hIcon = LoadIconW(nullptr, IDI_APPLICATION);
  wc.hIconSm = wc.hIcon;
  wc.hCursor = LoadCursorW(nullptr, IDC_ARROW);
  wc.hbrBackground = nullptr;
  wc.lpszMenuName = nullptr;
  wc.lpszClassName = kClassName;
  if (!RegisterClassExW(&wc)) return false;

  // LCL 同时注册提示窗类：CS_DBLCLKS|CS_SAVEBITS，Vista+ 再加 CS_DROPSHADOW，hIcon=0
  wc.style = CS_DBLCLKS | CS_SAVEBITS | CS_DROPSHADOW;
  wc.lpfnWndProc = DefWindowProcW;
  wc.hIcon = nullptr;
  wc.hIconSm = nullptr;
  wc.lpszClassName = kHintClassName;
  RegisterClassExW(&wc);  // 失败不影响主窗体
  return true;
}

}  // namespace

int WINAPI wWinMain(HINSTANCE inst, HINSTANCE, PWSTR, int) {
  if (!RegisterClasses(inst)) {
    MessageBoxW(nullptr, L"RegisterClass failed", kTitle, MB_ICONERROR);
    return 1;
  }

  // F154：WS_POPUP|WS_CLIPSIBLINGS|WS_CLIPCHILDREN|WS_CAPTION|WS_SYSMENU|WS_MINIMIZEBOX，
  // exstyle WS_EX_WINDOWEDGE；外框 1024×768，屏幕居中（LCL poScreenCenter）
  const DWORD style = WS_POPUP | WS_CLIPSIBLINGS | WS_CLIPCHILDREN | WS_CAPTION | WS_SYSMENU |
                      WS_MINIMIZEBOX;
  // 客户区 → 外框（LCL AdjustFormBounds 的同款做法），外框居中（poScreenCenter）
  RECT rc = {0, 0, kClientW, kClientH};
  AdjustWindowRectEx(&rc, style, FALSE, WS_EX_WINDOWEDGE);
  const int outer_w = rc.right - rc.left;
  const int outer_h = rc.bottom - rc.top;
  const int win_x = (GetSystemMetrics(SM_CXSCREEN) - outer_w) / 2;
  const int win_y = (GetSystemMetrics(SM_CYSCREEN) - outer_h) / 2;
  HWND hwnd = CreateWindowExW(WS_EX_WINDOWEDGE, kClassName, kTitle, style, win_x, win_y,
                              outer_w, outer_h, nullptr, nullptr, inst, nullptr);
  if (!hwnd) {
    MessageBoxW(nullptr, L"CreateWindowEx failed", kTitle, MB_ICONERROR);
    return 1;
  }
  ShowWindow(hwnd, SW_SHOW);
  UpdateWindow(hwnd);
  Log("form=%p at %d,%d %dx%d (client %dx%d)", static_cast<void*>(hwnd), win_x, win_y,
      outer_w, outer_h, kClientW, kClientH);

  HWND gl_target = g_viewer;
  if (gl_target) {
    if (GlInit(gl_target)) {
      RECT rc_viewer;
      GetClientRect(gl_target, &rc_viewer);
      GlResize(rc_viewer.right - rc_viewer.left, rc_viewer.bottom - rc_viewer.top);
      Log("gl=ok viewer_client=%dx%d", rc_viewer.right, rc_viewer.bottom);
    } else {
      Log("gl=fail");
    }
    // 固定 ~15.6 ms 渲染循环（F177），不是"有失效才画"
    SetTimer(hwnd, kRenderTimer, kRenderIntervalMs, nullptr);
    GlRenderMenu();
  }

  // F156：PeekMessage 抽干 + MsgWaitForMultipleObjects 阻塞等待（不 Sleep 轮询）
  MSG msg;
  for (;;) {
    while (PeekMessageW(&msg, nullptr, 0, 0, PM_REMOVE)) {
      if (msg.message == WM_QUIT) return static_cast<int>(msg.wParam);
      TranslateMessage(&msg);
      DispatchMessageW(&msg);
    }
    MsgWaitForMultipleObjects(0, nullptr, FALSE, INFINITE, QS_ALLINPUT);
  }
}
