// 在隐藏 Windows 桌面上运行游戏，后台点击 + 截图（不移动用户鼠标、不抢前台）。
// 原理：CreateDesktop + CreateProcess(lpDesktop) + 该桌面内的 SetCursorPos/PostMessage + BitBlt 截图。
using System;
using System.IO;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading;
using System.Threading.Tasks;

static class Program {
    [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Unicode)]
    struct STARTUPINFO {
        public int cb; public string lpReserved; public string lpDesktop; public string lpTitle;
        public int dwX, dwY, dwXSize, dwYSize, dwXCountChars, dwYCountChars, dwFillAttribute, dwFlags;
        public short wShowWindow, cbReserved2; public IntPtr lpReserved2, hStdInput, hStdOutput, hStdError;
    }
    [StructLayout(LayoutKind.Sequential)]
    struct PROCESS_INFORMATION { public IntPtr hProcess, hThread; public int dwProcessId, dwThreadId; }
    [StructLayout(LayoutKind.Sequential)]
    struct RECT { public int Left, Top, Right, Bottom; }
    [StructLayout(LayoutKind.Sequential)]
    struct POINT { public int X, Y; }
    [StructLayout(LayoutKind.Sequential)]
    struct BITMAPINFOHEADER {
        public uint biSize; public int biWidth, biHeight; public ushort biPlanes, biBitCount;
        public uint biCompression, biSizeImage; public int biXPelsPerMeter, biYPelsPerMeter;
        public uint biClrUsed, biClrImportant;
    }

    delegate bool EnumProc(IntPtr h, IntPtr l);

    [DllImport("user32.dll", CharSet = CharSet.Unicode)] static extern IntPtr CreateDesktopW(string name, IntPtr dev, IntPtr dm, int flags, uint access, IntPtr sa);
    [DllImport("user32.dll")] static extern bool SetThreadDesktop(IntPtr desk);
    [DllImport("kernel32.dll", CharSet = CharSet.Unicode)] static extern bool CreateProcessW(string app, string cmd, IntPtr pa, IntPtr ta, bool inherit, uint flags, IntPtr env, string cwd, ref STARTUPINFO si, out PROCESS_INFORMATION pi);
    [DllImport("kernel32.dll")] static extern bool TerminateProcess(IntPtr h, uint code);
    [DllImport("user32.dll")] static extern bool EnumDesktopWindows(IntPtr desk, EnumProc cb, IntPtr l);
    [DllImport("user32.dll")] static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
    [DllImport("user32.dll", CharSet = CharSet.Unicode)] static extern int GetWindowTextW(IntPtr h, StringBuilder s, int n);
    [DllImport("user32.dll")] static extern bool IsWindowVisible(IntPtr h);
    [DllImport("user32.dll")] static extern bool SetWindowPos(IntPtr h, IntPtr after, int x, int y, int cx, int cy, uint flags);
    [DllImport("user32.dll")] static extern bool GetClientRect(IntPtr h, out RECT r);
    [DllImport("user32.dll")] static extern bool ClientToScreen(IntPtr h, ref POINT p);
    [DllImport("user32.dll")] static extern bool SetCursorPos(int x, int y);
    [DllImport("user32.dll")] static extern bool PostMessageW(IntPtr h, uint msg, IntPtr w, IntPtr l);
    [DllImport("user32.dll")] static extern IntPtr GetDC(IntPtr h);
    [DllImport("gdi32.dll", CharSet = CharSet.Unicode)] static extern IntPtr CreateDCW(string driver, string device, string port, IntPtr dm);
    [DllImport("user32.dll")] static extern int ReleaseDC(IntPtr h, IntPtr dc);
    [DllImport("gdi32.dll")] static extern IntPtr CreateCompatibleDC(IntPtr dc);
    [DllImport("gdi32.dll")] static extern IntPtr CreateCompatibleBitmap(IntPtr dc, int w, int h);
    [DllImport("gdi32.dll")] static extern IntPtr SelectObject(IntPtr dc, IntPtr obj);
    [DllImport("gdi32.dll")] static extern bool BitBlt(IntPtr dst, int x, int y, int w, int h, IntPtr src, int sx, int sy, uint rop);
    [DllImport("gdi32.dll")] static extern bool DeleteDC(IntPtr dc);
    [DllImport("gdi32.dll")] static extern bool DeleteObject(IntPtr o);
    [DllImport("user32.dll")] static extern bool PrintWindow(IntPtr h, IntPtr dc, uint flags);
    [DllImport("user32.dll")] static extern IntPtr GetWindowDC(IntPtr h);
    [DllImport("gdi32.dll")] static extern int GetDIBits(IntPtr dc, IntPtr bmp, uint start, uint lines, byte[] bits, ref BITMAPINFOHEADER bi, uint usage);

    static IntPtr desk;
    static int pid;
    static bool forceBitBlt;

    static async Task<int> Main(string[] args) {
        string exe = null, workdir = null, outDir = null, script = "wait:20000;shot:menu", desktopName = "MagVDesk";
        forceBitBlt = Array.IndexOf(args, "--bitblt") >= 0;
        for (int i = 0; i < args.Length - 1; ++i) {
            switch (args[i]) {
                case "--exe": exe = args[++i]; break;
                case "--workdir": workdir = args[++i]; break;
                case "--out": outDir = args[++i]; break;
                case "--script": script = args[++i]; break;
                case "--desktop": desktopName = args[++i]; break;
            }
        }
        if (exe == null || workdir == null || outDir == null) {
            Console.WriteLine("usage: vdesk --exe <game.exe> --workdir <dir> --out <dir> [--script ...]");
            return 2;
        }
        Directory.CreateDirectory(outDir);

        desk = CreateDesktopW(desktopName, IntPtr.Zero, IntPtr.Zero, 0, 0x10000000, IntPtr.Zero);
        if (desk == IntPtr.Zero) { Console.WriteLine("CreateDesktop failed " + Marshal.GetLastWin32Error()); return 3; }
        if (!SetThreadDesktop(desk)) { Console.WriteLine("SetThreadDesktop failed " + Marshal.GetLastWin32Error()); return 4; }

        var si = new STARTUPINFO();
        si.cb = Marshal.SizeOf(si);
        si.lpDesktop = desktopName;
        if (!CreateProcessW(exe, "\"" + exe + "\"", IntPtr.Zero, IntPtr.Zero, false, 0, IntPtr.Zero, workdir, ref si, out var pi)) {
            Console.WriteLine("CreateProcess failed " + Marshal.GetLastWin32Error());
            return 5;
        }
        pid = pi.dwProcessId;
        Console.WriteLine($"pid={pid} desktop={desktopName}");

        IntPtr h = IntPtr.Zero;
        for (int waited = 0; waited < 40000 && h == IntPtr.Zero; waited += 500) {
            EnumDesktopWindows(desk, (w, l) => {
                GetWindowThreadProcessId(w, out uint p);
                if (p == (uint)pid && IsWindowVisible(w)) {
                    var sb = new StringBuilder(256); GetWindowTextW(w, sb, 256);
                    GetClientRect(w, out RECT r);
                    if (sb.ToString().Contains("Magnetic", StringComparison.Ordinal) && r.Right > 100) h = w;
                }
                return true;
            }, IntPtr.Zero);
            if (h == IntPtr.Zero) await Task.Delay(500);
        }
        Console.WriteLine("hwnd=" + h);
        if (h == IntPtr.Zero) { TerminateProcess(pi.hProcess, 0); return 6; }
        SetWindowPos(h, IntPtr.Zero, 0, 0, 1024, 768, 0x0040);

        foreach (var cmd in script.Split(';')) {
            var parts = cmd.Split(':');
            switch (parts[0]) {
                case "wait": await Task.Delay(int.Parse(parts[1])); break;
                case "shot": Shot(h, Path.Combine(outDir, parts[1] + ".bmp")); Console.WriteLine("shot " + parts[1]); break;
                case "click": {
                    var xy = parts[1].Split(',');
                    await ClickAsync(h, double.Parse(xy[0]), double.Parse(xy[1]));
                    Console.WriteLine("click " + parts[1]);
                    break;
                }
                case "kill": TerminateProcess(pi.hProcess, 0); Console.WriteLine("killed"); break;
            }
        }
        TerminateProcess(pi.hProcess, 0);
        Console.WriteLine("done");
        return 0;
    }

    static async Task ClickAsync(IntPtr h, double fx, double fy) {
        GetClientRect(h, out RECT r);
        int cx = (int)(r.Right * fx), cy = (int)(r.Bottom * fy);
        POINT p = new POINT { X = cx, Y = cy };
        ClientToScreen(h, ref p);
        SetCursorPos(p.X, p.Y);
        await Task.Delay(250);
        IntPtr lp = (IntPtr)((cy << 16) | (cx & 0xFFFF));
        PostMessageW(h, 0x0200, IntPtr.Zero, lp);
        await Task.Delay(80);
        PostMessageW(h, 0x0201, (IntPtr)1, lp);
        await Task.Delay(80);
        PostMessageW(h, 0x0202, IntPtr.Zero, lp);
    }

    static void Shot(IntPtr h, string path) {
        GetClientRect(h, out RECT r);
        int w = r.Right, ht = r.Bottom;
        IntPtr screen = CreateDCW("DISPLAY", null, null, IntPtr.Zero);
        if (screen == IntPtr.Zero) screen = GetDC(IntPtr.Zero);
        IntPtr mem = CreateCompatibleDC(screen);
        IntPtr bmp = CreateCompatibleBitmap(screen, w, ht);
        IntPtr old = SelectObject(mem, bmp);
        bool ok = !forceBitBlt && PrintWindow(h, mem, 2);
        if (!ok) {
            POINT origin = new POINT { X = 0, Y = 0 };
            ClientToScreen(h, ref origin);
            BitBlt(mem, 0, 0, w, ht, screen, origin.X, origin.Y, 0x00CC0020);
        }
        var bi = new BITMAPINFOHEADER {
            biSize = (uint)Marshal.SizeOf<BITMAPINFOHEADER>(), biWidth = w, biHeight = ht,
            biPlanes = 1, biBitCount = 32
        };
        var bits = new byte[w * ht * 4];
        GetDIBits(mem, bmp, 0, (uint)ht, bits, ref bi, 0);
        SelectObject(mem, old); DeleteObject(bmp); DeleteDC(mem); ReleaseDC(IntPtr.Zero, screen);
        using var fs = new FileStream(path, FileMode.Create);
        using var bw = new BinaryWriter(fs);
        bw.Write((byte)'B'); bw.Write((byte)'M'); bw.Write(54 + bits.Length); bw.Write(0); bw.Write(54);
        bw.Write(40); bw.Write(w); bw.Write(ht); bw.Write((short)1); bw.Write((short)32);
        bw.Write(0); bw.Write(bits.Length); bw.Write(2835); bw.Write(2835); bw.Write(0); bw.Write(0);
        bw.Write(bits);
    }
}
