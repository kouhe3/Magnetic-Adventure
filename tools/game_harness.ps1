# 游戏自动化测试台：启动 game.exe（替换 b2Physics.dll），点 Play 进入关卡并截图。
# 用法: pwsh -File tools/game_harness.ps1 -Dll build/Release/b2Physics.dll -Tag ours
param(
  [string]$Dll = "build/Release/b2Physics.dll",
  [string]$Tag = "run",
  [int]$MenuWaitSec = 22,
  [int]$PlayWaitSec = 12
)
$ErrorActionPreference = "Stop"
Add-Type @"
using System;
using System.Text;
using System.Runtime.InteropServices;
public class H {
  public delegate bool EnumProc(IntPtr h, IntPtr l);
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc cb, IntPtr l);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
  [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("kernel32.dll")] public static extern uint GetCurrentThreadId();
  [DllImport("user32.dll")] public static extern bool AttachThreadInput(uint a, uint b, bool f);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern bool BringWindowToTop(IntPtr h);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int c);
  [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
  [DllImport("user32.dll")] public static extern void mouse_event(uint f, uint dx, uint dy, uint d, UIntPtr e);
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int Left, Top, Right, Bottom; }
  public static IntPtr Find(uint pid) {
    IntPtr found = IntPtr.Zero;
    EnumWindows((h, l) => {
      uint p; GetWindowThreadProcessId(h, out p);
      if (p == pid && IsWindowVisible(h)) {
        var sb = new StringBuilder(256); GetWindowText(h, sb, 256);
        RECT r; GetWindowRect(h, out r);
        if (sb.ToString().Contains("Magnetic") && r.Right - r.Left > 100) found = h;
      }
      return true;
    }, IntPtr.Zero);
    return found;
  }
  public static void Focus(IntPtr h) {
    uint tid = GetWindowThreadProcessId(h, out _);
    uint cur = GetCurrentThreadId();
    AttachThreadInput(cur, tid, true);
    ShowWindow(h, 9); BringWindowToTop(h); SetForegroundWindow(h);
    System.Threading.Thread.Sleep(200);
    AttachThreadInput(cur, tid, false);
  }
  public static void Click(int x, int y) {
    SetCursorPos(x, y); System.Threading.Thread.Sleep(250);
    mouse_event(0x0002,0,0,0,UIntPtr.Zero); System.Threading.Thread.Sleep(120);
    mouse_event(0x0004,0,0,0,UIntPtr.Zero);
  }
}
"@
$root = "C:/tmp/Magnetic Adventure"
$dst = "$root/work/integration"
$src = if ([System.IO.Path]::IsPathRooted($Dll)) { $Dll } else { "$root/$Dll" }

# 等旧进程退出，避免 DLL 被占用
Get-Process game -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Milliseconds 500
Copy-Item $src "$dst/b2Physics.dll" -Force

$p = Start-Process -FilePath "$dst/game.exe" -WorkingDirectory $dst -PassThru
Start-Sleep -Seconds $MenuWaitSec
$h = [H]::Find([uint32]$p.Id)
"hwnd=$h pid=$($p.Id)"
if ($h -eq [IntPtr]::Zero) { "window not found"; exit 3 }

[H]::Focus($h)
$r = New-Object H+RECT
[H]::GetWindowRect($h, [ref]$r) | Out-Null
$w = $r.Right - $r.Left; $ht = $r.Bottom - $r.Top
"rect=$($r.Left),$($r.Top),$($w)x$($ht)"
$px = $r.Left + [int]($w * 0.267); $py = $r.Top + [int]($ht * 0.278)
[H]::Click($px, $py); Start-Sleep -Milliseconds 700; [H]::Click($px, $py)
"clicked play at $px,$py"
Start-Sleep -Seconds $PlayWaitSec
$p.Refresh()
"alive=$(-not $p.HasExited) exit=$($p.ExitCode)"
& ffmpeg -hide_banner -loglevel error -f gdigrab -i title="A Magnetic Adventure" -frames:v 1 -y "$root/work/shot_$Tag.png" 2>&1 | Select-Object -Last 1
if (-not $p.HasExited) { Stop-Process -Id $p.Id -Force }
Get-ChildItem "$root/work/shot_$Tag.png" -ErrorAction SilentlyContinue | Select-Object Name, Length
