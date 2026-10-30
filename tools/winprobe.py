"""窗口/消息参数探针（T3.1 的验收仪器）：起一个 exe、等主窗口、把窗口与类参数逐行打出来。

用法（任意位数 Python 3）：
    python tools/winprobe.py [game_dir] [--keep]      # 默认 game_dir = <repo>/bin/gametop
    python tools/winprobe.py work/integration         # 跑自建宿主/双自建 DLL 的版本

判据（原版 vs 自建，逐字段 diff，允许忽略的只有 hwnd/pid/类句柄等运行期值）：
    main_class / main_style / main_exstyle / window_rect / client_size / border_x,y /
    dpi / dpi_awareness / placement_showcmd / is_zoomed / has_menu / child 行
    参考值见 docs/facts.md 的 F154/F155/F158。

探针进程是 **DPI-unaware**（与游戏本体一致），所以坐标是游戏的逻辑坐标；本机 150% 缩放下
物理尺寸 = 逻辑 × 1.5（1024×768 → 1536×1152）。换桌面缩放时先确认这条再对数字。

覆盖边界：只从进程外部观测（user32 查询 + GetProcessTimes）。不注入、不挂钩 ⇒
「主循环是 PeekMessage 还是 GetMessage」只能由导入表 + CPU 占比 + WM_NULL 响应推断；
**tick 间隔（SetTimer 的 uElapse）不在覆盖范围内**，要另外用 opengl32 代理或调试器拿。
"""
import ctypes
import ctypes.wintypes as wt
import os
import subprocess
import sys
import time

ROOT = r"C:\tmp\Magnetic Adventure"
u = ctypes.windll.user32
k = ctypes.windll.kernel32


class MONITORINFOEXW(ctypes.Structure):
    _fields_ = [("cbSize", wt.DWORD), ("rcMonitor", wt.RECT),
                ("rcWork", wt.RECT), ("dwFlags", wt.DWORD),
                ("szDevice", wt.WCHAR * 32)]


class WINDOWPLACEMENT(ctypes.Structure):
    _fields_ = [("length", wt.UINT), ("flags", wt.UINT), ("showCmd", wt.UINT),
                ("ptMinPosition", wt.POINT), ("ptMaxPosition", wt.POINT),
                ("rcNormalPosition", wt.RECT), ("rcDevice", wt.RECT)]


class WINDOWINFO(ctypes.Structure):
    _fields_ = [("cbSize", wt.DWORD), ("rcWindow", wt.RECT), ("rcClient", wt.RECT),
                ("dwStyle", wt.DWORD), ("dwExStyle", wt.DWORD),
                ("dwWindowStatus", wt.UINT), ("cxWindowBorders", wt.UINT),
                ("cyWindowBorders", wt.UINT), ("atomWindowType", wt.ATOM),
                ("wCreatorVersion", wt.WORD)]


class PROCESS_TIMES(ctypes.Structure):
    _fields_ = [("creation", wt.FILETIME), ("exit", wt.FILETIME),
                ("kernel", wt.FILETIME), ("user", wt.FILETIME)]


STYLE_FLAGS = [
    (0x80000000, "WS_POPUP"), (0x40000000, "WS_CHILD"), (0x20000000, "WS_MINIMIZE"),
    (0x10000000, "WS_VISIBLE"), (0x08000000, "WS_DISABLED"), (0x04000000, "WS_CLIPSIBLINGS"),
    (0x02000000, "WS_CLIPCHILDREN"), (0x01000000, "WS_MAXIMIZE"), (0x00800000, "WS_BORDER"),
    (0x00400000, "WS_DLGFRAME"), (0x00200000, "WS_VSCROLL"), (0x00100000, "WS_HSCROLL"),
    (0x00080000, "WS_SYSMENU"), (0x00040000, "WS_THICKFRAME"),
    (0x00020000, "WS_MINIMIZEBOX"), (0x00010000, "WS_MAXIMIZEBOX"),
]
EX_FLAGS = [
    (0x00000001, "WS_EX_DLGMODALFRAME"), (0x00000008, "WS_EX_TOPMOST"),
    (0x00000040, "WS_EX_WINDOWEDGE"), (0x00000100, "WS_EX_WINDOWEDGE"),
    (0x00000200, "WS_EX_CLIENTEDGE"), (0x00010000, "WS_EX_CONTROLPARENT"),
    (0x00040000, "WS_EX_APPWINDOW"), (0x00080000, "WS_EX_LAYERED"),
    (0x00400000, "WS_EX_TOOLWINDOW"),
]


def decode(v, table):
    return "|".join(n for bit, n in table if v & bit) or "none"


def main():
    argv = sys.argv[1:]
    game_dir = next((a for a in argv if not a.startswith("--")), None) or \
        os.path.join(ROOT, "bin", "gametop")
    exe = "game.exe"
    if "--exe" in argv:
        exe = argv[argv.index("--exe") + 1]
    p = subprocess.Popen([os.path.join(game_dir, exe)], cwd=game_dir)
    os.makedirs(os.path.join(ROOT, "work"), exist_ok=True)
    open(os.path.join(ROOT, "work", "winprobe_pid.txt"), "w").write(str(p.pid))
    print("pid=%d exe=%s dir=%s" % (p.pid, exe, game_dir))
    try:
        return _probe(p, game_dir)
    finally:
        if "--keep" not in sys.argv:
            subprocess.run(["taskkill", "/PID", str(p.pid), "/F"], capture_output=True)
            print("killed=1")


def _probe(p, game_dir):

    WNDENUMPROC = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
    hwnd_main = None
    for _ in range(120):
        time.sleep(0.5)
        top = []

        def cb(h, l):
            pid = wt.DWORD()
            u.GetWindowThreadProcessId(h, ctypes.byref(pid))
            if pid.value == p.pid:
                top.append(h)
            return True

        u.EnumWindows(WNDENUMPROC(cb), 0)
        for h in top:
            n = ctypes.create_unicode_buffer(512)
            u.GetWindowTextW(h, n, 512)
            r = wt.RECT()
            u.GetWindowRect(h, ctypes.byref(r))
            if u.IsWindowVisible(h) and (r.right - r.left) > 200:
                hwnd_main = h
                break
        if hwnd_main:
            break

    if not hwnd_main:
        print("error=no_main_window")
        p.kill()
        return 1

    # 窗口刚可见时子窗口（GL 视口）可能还没被 MoveWindow 到最终尺寸，直接采样会拿到
    # 瞬时值（2026-10-30 门禁偶发 diffs=2 的最可能来源）。等两次采样一致再读字段。
    prev = None
    for _ in range(20):
        sizes = []

        def cs(h, l):
            r = wt.RECT()
            u.GetClientRect(h, ctypes.byref(r))
            sizes.append((r.right, r.bottom))
            return True

        u.EnumChildWindows(hwnd_main, WNDENUMPROC(cs), 0)
        cur = tuple(sizes)
        if cur and cur == prev:
            break
        prev = cur
        time.sleep(0.1)

    def qt(h):
        buf = ctypes.create_unicode_buffer(512)
        u.GetWindowTextW(h, buf, 512)
        return buf.value

    print("main_hwnd=0x%08x" % hwnd_main)
    print("main_title=%s" % qt(hwnd_main))
    cls = ctypes.create_unicode_buffer(256)
    u.GetClassNameW(hwnd_main, cls, 256)
    print("main_class=%s" % cls.value)

    style = u.GetWindowLongW(hwnd_main, -16) & 0xFFFFFFFF
    exstyle = u.GetWindowLongW(hwnd_main, -20) & 0xFFFFFFFF
    print("main_style=0x%08x %s" % (style, decode(style, STYLE_FLAGS)))
    print("main_exstyle=0x%08x %s" % (exstyle, decode(exstyle, EX_FLAGS)))

    wr, cr = wt.RECT(), wt.RECT()
    u.GetWindowRect(hwnd_main, ctypes.byref(wr))
    u.GetClientRect(hwnd_main, ctypes.byref(cr))
    print("window_rect=%d,%d,%d,%d size=%dx%d" % (wr.left, wr.top, wr.right, wr.bottom,
                                                  wr.right - wr.left, wr.bottom - wr.top))
    print("client_size=%dx%d" % (cr.right - cr.left, cr.bottom - cr.top))
    print("border_x=%d border_y=%d" % ((wr.right - wr.left) - cr.right,
                                       (wr.bottom - wr.top) - cr.bottom))
    wi = WINDOWINFO()
    wi.cbSize = ctypes.sizeof(wi)
    if u.GetWindowInfo(hwnd_main, ctypes.byref(wi)):
        print("wininfo_borders=%d/%d (OS 认为的每边边框/标题栏总高)" %
              (wi.cxWindowBorders, wi.cyWindowBorders))

    # 类属性
    for name, idx in (("hbrBackground", -10), ("hCursor", -12), ("hIcon", -14),
                      ("hInstance", -16), ("hModule", -16), ("wndproc", -24),
                      ("hIconSm", -34)):
        try:
            if ctypes.sizeof(ctypes.c_void_p) == 8:
                v = u.GetClassLongPtrW(hwnd_main, idx)
            else:
                v = u.GetClassLongW(hwnd_main, idx)
            print("class_%s=0x%08x" % (name, v & 0xFFFFFFFFFFFFFFFF))
        except Exception as e:  # noqa
            print("class_%s=err(%s)" % (name, e))

    # DPI
    try:
        u.GetDpiForWindow.restype = wt.UINT
        print("dpi=%d" % u.GetDpiForWindow(hwnd_main))
        # 必须声明 restype：上下文是 64 位句柄，默认 c_int 会截断成无效值，
        # GetAwarenessFromDpiAwarenessContext 于是恒返回 0（假"unaware"）
        u.GetWindowDpiAwarenessContext.restype = ctypes.c_void_p
        u.GetWindowDpiAwarenessContext.argtypes = (wt.HWND,)
        ctx = u.GetWindowDpiAwarenessContext(hwnd_main)
        u.GetAwarenessFromDpiAwarenessContext.restype = ctypes.c_int
        u.GetAwarenessFromDpiAwarenessContext.argtypes = (ctypes.c_void_p,)
        aware = u.GetAwarenessFromDpiAwarenessContext(ctypes.c_void_p(ctx))
        print("dpi_awareness=%d (0=unaware 1=system 2=permonitor, -1=invalid ctx=0x%x)" %
              (aware, ctx or 0))
    except Exception as e:  # noqa
        print("dpi=err(%s)" % e)

    # 显示器
    mon = u.MonitorFromWindow(hwnd_main, 2)  # MONITOR_DEFAULTTONEAREST
    mi = MONITORINFOEXW()
    mi.cbSize = ctypes.sizeof(mi)
    if u.GetMonitorInfoW(mon, ctypes.byref(mi)):
        print("monitor=%s rect=%d,%d,%d,%d work=%d,%d,%d,%d" % (
            mi.szDevice, mi.rcMonitor.left, mi.rcMonitor.top, mi.rcMonitor.right,
            mi.rcMonitor.bottom, mi.rcWork.left, mi.rcWork.top, mi.rcWork.right, mi.rcWork.bottom))

    # 窗口放置状态
    wp = WINDOWPLACEMENT()
    wp.length = ctypes.sizeof(wp)
    if u.GetWindowPlacement(hwnd_main, ctypes.byref(wp)):
        print("placement_showcmd=%d flags=0x%x normal_rect=%d,%d,%d,%d" % (
            wp.showCmd, wp.flags, wp.rcNormalPosition.left, wp.rcNormalPosition.top,
            wp.rcNormalPosition.right, wp.rcNormalPosition.bottom))

    print("is_zoomed=%d is_iconic=%d has_menu=%d" % (
        u.IsZoomed(hwnd_main), u.IsIconic(hwnd_main), 1 if u.GetMenu(hwnd_main) else 0))

    # 响应性
    res = ctypes.c_size_t()
    ok = u.SendMessageTimeoutW(hwnd_main, 0, 0, 0, 0x0002, 1000, ctypes.byref(res))
    print("wm_null_ok=%d" % ok)

    # 全部顶层窗口（含不可见）
    def cb2(h, l):
        pid = wt.DWORD()
        u.GetWindowThreadProcessId(h, ctypes.byref(pid))
        if pid.value == p.pid:
            c = ctypes.create_unicode_buffer(256)
            u.GetClassNameW(h, c, 256)
            n = ctypes.create_unicode_buffer(256)
            u.GetWindowTextW(h, n, 256)
            r = wt.RECT()
            u.GetWindowRect(h, ctypes.byref(r))
            s = u.GetWindowLongW(h, -16) & 0xFFFFFFFF
            print("top=0x%08x class=%s title=%r vis=%d style=0x%08x rect=%d,%d,%d,%d" % (
                h, c.value, n.value, u.IsWindowVisible(h), s, r.left, r.top, r.right, r.bottom))
        return True

    u.EnumWindows(WNDENUMPROC(cb2), 0)

    # 子窗口：GL 视图/控件都在这一层，视口尺寸以子窗口 client 为准
    def cb3(h, l):
        c = ctypes.create_unicode_buffer(256)
        u.GetClassNameW(h, c, 256)
        n = ctypes.create_unicode_buffer(256)
        u.GetWindowTextW(h, n, 256)
        r, cr2 = wt.RECT(), wt.RECT()
        u.GetWindowRect(h, ctypes.byref(r))
        u.GetClientRect(h, ctypes.byref(cr2))
        s = u.GetWindowLongW(h, -16) & 0xFFFFFFFF
        print("child class=%s title=%r vis=%d style=0x%08x rect=%d,%d,%d,%d client=%dx%d" % (
            c.value, n.value, u.IsWindowVisible(h), s, r.left, r.top, r.right, r.bottom,
            cr2.right, cr2.bottom))
        return True

    u.EnumChildWindows(hwnd_main, WNDENUMPROC(cb3), 0)

    # 线程数只作参考；CPU 占比故意不做（ctypes 下 GetProcessTimes 会静默给出 0，
    # 见 work/tickprobe.py 的教训）——要 CPU 数据用 pwsh 的 $p.CPU 两次采样：
    #   Start-Process game.exe -PassThru; 等 6 s; $c0=$p.CPU; 等 4 s; ($p.CPU-$c0)/4
    print("threads=%d" % _thread_count(p.pid))

    print("foreground=%d" % (u.GetForegroundWindow() == hwnd_main))

    k.CloseHandle(hproc)
    return 0


def _thread_count(pid):
    """用 CreateToolhelp32Snapshot 数线程。"""
    TH32CS_SNAPTHREAD = 0x4

    class THREADENTRY32(ctypes.Structure):
        _fields_ = [("dwSize", wt.DWORD), ("cntUsage", wt.DWORD), ("th32ThreadID", wt.DWORD),
                    ("th32OwnerProcessID", wt.DWORD), ("tpBasePri", wt.LONG),
                    ("tpDeltaPri", wt.LONG), ("dwFlags", wt.DWORD)]

    snap = k.CreateToolhelp32Snapshot(TH32CS_SNAPTHREAD, 0)
    if snap in (0, -1):
        return -1
    te = THREADENTRY32()
    te.dwSize = ctypes.sizeof(te)
    n = 0
    if k.Thread32First(snap, ctypes.byref(te)):
        while True:
            if te.th32OwnerProcessID == pid:
                n += 1
            if not k.Thread32Next(snap, ctypes.byref(te)):
                break
    k.CloseHandle(snap)
    return n


if __name__ == "__main__":
    sys.exit(main())
