# 在隐藏的 Windows 桌面上运行游戏并后台点击/截图（不移动用户鼠标）。
# 用法:
#   pwsh -File tools/vdesk.ps1 -Exe "work/integration/game.exe" -WorkDir "work/integration" -Out "work/vd" -Script "wait:20000;shot:menu;click:0.342,0.401;wait:1200;click:0.342,0.401;wait:10000;shot:play"
param(
  [Parameter(Mandatory=$true)][string]$Exe,
  [Parameter(Mandatory=$true)][string]$WorkDir,
  [Parameter(Mandatory=$true)][string]$Out,
  [string]$Script = "wait:20000;shot:menu",
  [string]$DesktopName = ""
)
$ErrorActionPreference = "Stop"
New-Item -ItemType Directory -Force -Path $Out | Out-Null
if (-not $DesktopName) { $DesktopName = "MagVDesk" }

Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
using System.Text;
using System.IO;

public class VD {
    [StructLayout(LayoutKind.Sequential, CharSet=CharSet.Unicode)]
    public struct STARTUPINFO {
        public int cb; public string lpReserved; public string lpDesktop; public string lpTitle;
        public int dwX, dwY, dwXSize, dwYSize, dwXCountChars, dwYCountChars, dwFillAttribute, dwFlags;
        public short wShowWindow, cbReserved2; public IntPtr lpReserved2, hStdInput, hStdOutput, hStdError;
    }
    [StructLayout(LayoutKind.Sequential)]
    public struct PROCESS_INFORMATION { public IntPtr hProcess, hThread; public int dwProcessId, dwThreadId; }
    [StructLayout(LayoutKind.Sequential)]
    public struct RECT { public int Left, Top, Right, Bottom; }
    [StructLayout(LayoutKind.Sequential)]
    public struct POINT { public int X, Y; }
    [StructLayout(LayoutKind.Sequential)]
    public struct BITMAPINFOHEADER {
        public uint biSize; public int biWidth, biHeight; public ushort biPlanes, biBitCount;
        public uint biCompression, biSizeImage; public int biXPelsPerMeter, biYPelsPerMeter;
        public uint biClrUsed, biClrImportant;
    }

    [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern IntPtr CreateDesktopW(string name, IntPtr dev, IntPtr dm, int flags, uint access, IntPtr sa);
    [DllImport("user32.dll")] public static extern bool SetThreadDesktop(IntPtr desk);
    [DllImport("user32.dll")] public static extern bool CloseDesktop(IntPtr desk);
    [DllImport("kernel32.dll", CharSet=CharSet.Unicode)] public static extern bool CreateProcessW(string app, string cmd, IntPtr pa, IntPtr ta, bool inherit, uint flags, IntPtr env, string cwd, ref STARTUPINFO si, out PROCESS_INFORMATION pi);
    [DllImport("kernel32.dll")] public static extern bool TerminateProcess(IntPtr h, uint code);
    [DllImport("user32.dll")] public static extern bool EnumDesktopWindows(IntPtr desk, EnumProc cb, IntPtr l);
    public delegate bool EnumProc(IntPtr h, IntPtr l);
    [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
    [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetWindowTextW(IntPtr h, StringBuilder s, int n);
    [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
    [DllImport("user32.dll")] public static extern bool SetWindowPos(IntPtr h, IntPtr after, int x, int y, int cx, int cy, uint flags);
    [DllImport("user32.dll")] public static extern bool GetClientRect(IntPtr h, out RECT r);
    [DllImport("user32.dll")] public static extern bool ClientToScreen(IntPtr h, ref POINT p);
    [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
    [DllImport("user32.dll")] public static extern bool PostMessageW(IntPtr h, uint msg, IntPtr w, IntPtr l);
    [DllImport("user32.dll")] public static extern IntPtr GetDC(IntPtr h);
    [DllImport("user32.dll")] public static extern int ReleaseDC(IntPtr h, IntPtr dc);
    [DllImport("gdi32.dll")] public static extern IntPtr CreateCompatibleDC(IntPtr dc);
    [DllImport("gdi32.dll")] public static extern IntPtr CreateCompatibleBitmap(IntPtr dc, int w, int h);
    [DllImport("gdi32.dll")] public static extern IntPtr SelectObject(IntPtr dc, IntPtr obj);
    [DllImport("gdi32.dll")] public static extern bool BitBlt(IntPtr dst, int x, int y, int w, int h, IntPtr src, int sx, int sy, uint rop);
    [DllImport("gdi32.dll")] public static extern bool DeleteDC(IntPtr dc);
    [DllImport("gdi32.dll")] public static extern bool DeleteObject(IntPtr o);
    [DllImport("gdi32.dll")] public static extern int GetDIBits(IntPtr dc, IntPtr bmp, uint start, uint lines, byte[] bits, ref BITMAPINFOHEADER bi, uint usage);

    public static IntPtr Desk;
    public static int Pid;

    public static IntPtr Create(string name) {
        Desk = CreateDesktopW(name, IntPtr.Zero, IntPtr.Zero, 0, 0x10000000, IntPtr.Zero); // GENERIC_ALL
        if (Desk == IntPtr.Zero) throw new Exception("CreateDesktop failed " + Marshal.GetLastWin32Error());
        if (!SetThreadDesktop(Desk)) throw new Exception("SetThreadDesktop failed " + Marshal.GetLastWin32Error());
        return Desk;
    }

    public static int Launch(string exe, string workdir, string desktopName) {
        var si = new STARTUPINFO();
        si.cb = Marshal.SizeOf(si);
        si.lpDesktop = desktopName;
        PROCESS_INFORMATION pi;
        bool ok = CreateProcessW(exe, "\"" + exe + "\"", IntPtr.Zero, IntPtr.Zero, false, 0, IntPtr.Zero, workdir, ref si, out pi);
        if (!ok) throw new Exception("CreateProcess failed " + Marshal.GetLastWin32Error());
        Pid = pi.dwProcessId;
        return Pid;
    }

    public static IntPtr WaitWindow(int pid, string titlePart, int timeoutMs) {
        int waited = 0;
        while (waited < timeoutMs) {
            IntPtr found = IntPtr.Zero;
            EnumDesktopWindows(Desk, (h, l) => {
                uint p; GetWindowThreadProcessId(h, out p);
                if (p == (uint)pid && IsWindowVisible(h)) {
                    var sb = new StringBuilder(256); GetWindowTextW(h, sb, 256);
                    RECT r; GetClientRect(h, out r);
                    if (sb.ToString().Contains(titlePart) && r.Right > 100) found = h;
                }
                return true;
            }, IntPtr.Zero);
            if (found != IntPtr.Zero) return found;
            System.Threading.Thread.Sleep(500);
            waited += 500;
        }
        return IntPtr.Zero;
    }

    public static void Click(IntPtr h, double fx, double fy) {
        RECT r; GetClientRect(h, out r);
        int cx = (int)(r.Right * fx), cy = (int)(r.Bottom * fy);
        POINT p = new POINT(); p.X = cx; p.Y = cy;
        ClientToScreen(h, ref p);
        SetCursorPos(p.X, p.Y);
        System.Threading.Thread.Sleep(200);
        IntPtr lp = (IntPtr)((cy << 16) | (cx & 0xFFFF));
        PostMessageW(h, 0x0200, IntPtr.Zero, lp);
        System.Threading.Thread.Sleep(80);
        PostMessageW(h, 0x0201, (IntPtr)1, lp);
        System.Threading.Thread.Sleep(80);
        PostMessageW(h, 0x0202, IntPtr.Zero, lp);
    }

    public static void Shot(IntPtr h, string path) {
        RECT r; GetClientRect(h, out r);
        int w = r.Right, ht = r.Bottom;
        IntPtr screen = GetDC(IntPtr.Zero);
        IntPtr mem = CreateCompatibleDC(screen);
        IntPtr bmp = CreateCompatibleBitmap(screen, w, ht);
        IntPtr old = SelectObject(mem, bmp);
        POINT origin = new POINT(); origin.X = 0; origin.Y = 0;
        ClientToScreen(h, ref origin);
        BitBlt(mem, 0, 0, w, ht, screen, origin.X, origin.Y, 0x00CC0020);
        var bi = new BITMAPINFOHEADER();
        bi.biSize = (uint)Marshal.SizeOf(bi); bi.biWidth = w; bi.biHeight = ht; bi.biPlanes = 1; bi.biBitCount = 32;
        byte[] bits = new byte[w * ht * 4];
        GetDIBits(mem, bmp, 0, (uint)ht, bits, ref bi, 0);
        SelectObject(mem, old); DeleteObject(bmp); DeleteDC(mem); ReleaseDC(IntPtr.Zero, screen);
        using (var fs = new FileStream(path, FileMode.Create)) {
            int size = 54 + bits.Length;
            var bw = new BinaryWriter(fs);
            bw.Write((byte)'B'); bw.Write((byte)'M'); bw.Write(size); bw.Write(0); bw.Write(54);
            bw.Write(40); bw.Write(w); bw.Write(ht); bw.Write((short)1); bw.Write((short)32);
            bw.Write(0); bw.Write(bits.Length); bw.Write(2835); bw.Write(2835); bw.Write(0); bw.Write(0);
            bw.Write(bits);
        }
    }
}
'@

[VD]::Create($DesktopName) | Out-Null
$pid2 = [VD]::Launch((Resolve-Path $Exe), (Resolve-Path $WorkDir), $DesktopName)
"pid=$pid2 desktop=$DesktopName"
$h = [VD]::WaitWindow($pid2, "Magnetic", 40000)
"hwnd=$h"
if ($h -eq [IntPtr]::Zero) { "no window"; exit 3 }
[VD]::SetWindowPos($h, [IntPtr]::Zero, 0, 0, 1024, 768, 0x0040) | Out-Null

foreach ($cmd in $Script.Split(";")) {
    $p = $cmd.Split(":")
    switch ($p[0]) {
        "wait" { Start-Sleep -Milliseconds ([int]$p[1]) }
        "shot" { [VD]::Shot($h, (Join-Path $Out ($p[1] + ".bmp"))); "shot $($p[1])" }
        "click" {
            $xy = $p[1].Split(",")
            [VD]::Click($h, [double]$xy[0], [double]$xy[1])
            "click $($p[1])"
        }
        "kill" { [VD]::TerminateProcess([IntPtr]$pid2, 0); "killed" }
    }
}
[VD]::TerminateProcess([IntPtr]$pid2, 0) | Out-Null
"done"
