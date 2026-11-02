"""Drive the retail game through dispatcher indices without mouse/focus.

Runs the game on a private desktop (default), waits for MENU via memory
(F337), then calls the real command dispatcher sub_560880(appObj, 299+index)
on the window thread. The first call loads a level; later calls switch levels
in the same process (F344). No SetCursorPos / mouse_event / PostMessage.

Usage (32-bit Python):
  python tools/direct_drive.py --dir work/e2e_game --levels 0,1,2
  python tools/direct_drive.py --dir work/e2e_game --levels 0-51 --out work/drive.jsonl
  python tools/direct_drive.py --dir work/e2e_game --levels 0 --no-desktop   # debug

Criterion: for every requested index, within --timeout seconds the game reaches
  [lm+0x30]==1, [lm+4]==index, [lm+0x50]!=0, [lm+8]==1, and the process stays alive.
Exit code 0 iff all requested indices pass; JSONL records every step.

Coverage boundary:
  * indices are dispatcher order 0..51 (0 = Introduction, 1 = Let's Get
    Acquainted, ...), not the 1-based names in mapping/levels.csv;
  * the game must be at MENU on start (mgr/lm/state=2/idx=-1);
  * no pixels/audio are checked; the private desktop is not captured;
  * B2PROXY_LOG is inherited if the caller installed the b2 proxy in --dir.

Failure conditions:
  * size of c_void_p != 4 (32-bit Python required for the thread CONTEXT);
  * window/MENU not reached within 60 s;
  * appObj not found by the [app+0x2C]=lm/[app+0x30]=menu/[menu+0x58]=list/
    [list+0x58]=count signature;
  * SuspendThread/SetThreadContext fails (thread exited or access denied);
  * a level does not reach the expected state within --timeout.

Silent by default: expects the active profile's SoundsVolume/MusicVolume = 0
(the game persists them in hg_lmpgl.prf) and also runs
`nircmd muteappvolume game.exe 1` as a per-process fallback. The profile is not
written; --no-silent leaves audio untouched.
"""
import argparse
import ctypes
import ctypes.wintypes as wt
import json
import os
import shutil
import struct
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DIR = os.path.join(ROOT, "work", "e2e_game")

k32 = ctypes.windll.kernel32
user32 = ctypes.windll.user32
k32.OpenProcess.restype = ctypes.c_void_p
k32.OpenThread.restype = ctypes.c_void_p
k32.VirtualAllocEx.restype = ctypes.c_void_p
k32.VirtualAllocEx.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t,
                               wt.DWORD, wt.DWORD]
k32.WriteProcessMemory.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p,
                                   ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t)]
k32.ReadProcessMemory.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p,
                                  ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t)]
k32.VirtualQueryEx.restype = ctypes.c_size_t
k32.VirtualQueryEx.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p,
                               ctypes.c_size_t]
user32.CreateDesktopW.restype = ctypes.c_void_p
user32.CreateDesktopW.argtypes = [wt.LPCWSTR, ctypes.c_void_p, ctypes.c_void_p,
                                  wt.DWORD, wt.DWORD, ctypes.c_void_p]
user32.CloseDesktop.argtypes = [ctypes.c_void_p]
user32.GetWindowThreadProcessId.argtypes = [wt.HWND, ctypes.POINTER(wt.DWORD)]

PROCESS_VM_READ = 0x0010
PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_VM_OPERATION = 0x0008
PROCESS_VM_WRITE = 0x0020
THREAD_SUSPEND_RESUME = 0x0002
THREAD_GET_CONTEXT = 0x0008
THREAD_SET_CONTEXT = 0x0010
MEM_COMMIT = 0x1000
MEM_RESERVE = 0x2000
PAGE_EXECUTE_READWRITE = 0x40
CONTEXT_FULL = 0x00100007
READABLE = {0x02, 0x04, 0x08, 0x20, 0x40, 0x80}
DESKTOP_ALL = 0x000F01FF
PROCESS_CREATE_THREAD = 0x0002


class MBI(ctypes.Structure):
    _fields_ = [("BaseAddress", ctypes.c_void_p), ("AllocationBase", ctypes.c_void_p),
                ("AllocationProtect", wt.DWORD), ("RegionSize", ctypes.c_size_t),
                ("State", wt.DWORD), ("Protect", wt.DWORD), ("Type", wt.DWORD)]


class FSA(ctypes.Structure):
    _fields_ = [("ControlWord", wt.DWORD), ("StatusWord", wt.DWORD), ("TagWord", wt.DWORD),
                ("ErrorOffset", wt.DWORD), ("ErrorSelector", wt.DWORD),
                ("DataOffset", wt.DWORD), ("DataSelector", wt.DWORD),
                ("RegisterArea", ctypes.c_ubyte * 80), ("Cr0NpxState", wt.DWORD)]


class CONTEXT(ctypes.Structure):
    _fields_ = [("ContextFlags", wt.DWORD),
                ("Dr0", wt.DWORD), ("Dr1", wt.DWORD), ("Dr2", wt.DWORD),
                ("Dr3", wt.DWORD), ("Dr6", wt.DWORD), ("Dr7", wt.DWORD),
                ("FloatSave", FSA),
                ("SegGs", wt.DWORD), ("SegFs", wt.DWORD), ("SegEs", wt.DWORD),
                ("SegDs", wt.DWORD),
                ("Edi", wt.DWORD), ("Esi", wt.DWORD), ("Ebx", wt.DWORD),
                ("Edx", wt.DWORD), ("Ecx", wt.DWORD), ("Eax", wt.DWORD),
                ("Ebp", wt.DWORD), ("Eip", wt.DWORD), ("SegCs", wt.DWORD),
                ("EFlags", wt.DWORD), ("Esp", wt.DWORD), ("SegSs", wt.DWORD),
                ("ExtendedRegisters", ctypes.c_ubyte * 512)]


class STARTUPINFOW(ctypes.Structure):
    _fields_ = [("cb", wt.DWORD), ("lpReserved", wt.LPWSTR),
                ("lpDesktop", wt.LPWSTR), ("lpTitle", wt.LPWSTR),
                ("dwX", wt.DWORD), ("dwY", wt.DWORD), ("dwXSize", wt.DWORD),
                ("dwYSize", wt.DWORD), ("dwXCountChars", wt.DWORD),
                ("dwYCountChars", wt.DWORD), ("dwFillAttribute", wt.DWORD),
                ("dwFlags", wt.DWORD), ("wShowWindow", wt.WORD),
                ("cbReserved2", wt.WORD), ("lpReserved2", ctypes.c_void_p),
                ("hStdInput", wt.HANDLE), ("hStdOutput", wt.HANDLE),
                ("hStdError", wt.HANDLE)]


class PROCESS_INFORMATION(ctypes.Structure):
    _fields_ = [("hProcess", wt.HANDLE), ("hThread", wt.HANDLE),
                ("dwProcessId", wt.DWORD), ("dwThreadId", wt.DWORD)]


ENUMPROC = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
k32.CreateProcessW.argtypes = [wt.LPCWSTR, wt.LPWSTR, ctypes.c_void_p,
                               ctypes.c_void_p, wt.BOOL, wt.DWORD, ctypes.c_void_p,
                               wt.LPCWSTR, ctypes.POINTER(STARTUPINFOW),
                               ctypes.POINTER(PROCESS_INFORMATION)]
k32.CreateProcessW.restype = wt.BOOL
user32.EnumDesktopWindows.argtypes = [ctypes.c_void_p, ENUMPROC, wt.LPARAM]
user32.EnumWindows.argtypes = [ENUMPROC, wt.LPARAM]


def rpm(hp, addr, size):
    buf = ctypes.create_string_buffer(size)
    got = ctypes.c_size_t(0)
    ok = k32.ReadProcessMemory(hp, ctypes.c_void_p(addr), buf, size, ctypes.byref(got))
    return buf.raw[: got.value] if ok else None


def u32(hp, addr):
    b = rpm(hp, addr, 4)
    return int.from_bytes(b, "little") if b and len(b) == 4 else None


def u8(hp, addr):
    b = rpm(hp, addr, 1)
    return b[0] if b else None


def state(hp, app=None):
    mgr = u32(hp, 0x665334)
    lm = u32(hp, mgr + 0xA0) if mgr else None
    if not lm:
        return (mgr, lm, None, None, None, None, None)
    return (mgr, lm, u32(hp, lm + 0x30), u32(hp, lm + 4), u32(hp, lm + 0x50),
            u32(hp, lm + 0x54), u8(hp, app + 0x10) if app else None)


def scan_appobj(hp, lm):
    needle = struct.pack("<I", lm)
    addr = 0
    while addr < 0x7FFF0000:
        mbi = MBI()
        if not k32.VirtualQueryEx(ctypes.c_void_p(hp), ctypes.c_void_p(addr),
                                  ctypes.byref(mbi), ctypes.sizeof(mbi)):
            break
        base = mbi.BaseAddress or 0
        size = mbi.RegionSize
        if (mbi.State == MEM_COMMIT and (mbi.Protect & 0xFF) in READABLE
                and not (mbi.Protect & 0x100)):
            off = 0
            while off < size:
                n = min(0x100000, size - off)
                b = rpm(hp, base + off, n)
                if b:
                    i = b.find(needle)
                    while i >= 0:
                        app = base + off + i - 0x2C
                        if u32(hp, app + 0x2C) == lm:
                            menu = u32(hp, app + 0x30)
                            lst = u32(hp, menu + 0x58) if menu else None
                            cnt = u32(hp, lst + 0x58) if lst else None
                            if menu and lst and cnt and 0 < cnt <= 4096:
                                return app
                        i = b.find(needle, i + 1)
                off += n
        addr = base + size
        if size == 0:
            addr += 0x1000
    return None


def find_window(pid, desk=None):
    found = []

    def cb(hwnd, lparam):
        p = wt.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(p))
        if p.value == pid and user32.IsWindowVisible(hwnd):
            r = wt.RECT()
            user32.GetWindowRect(hwnd, ctypes.byref(r))
            if (r.right - r.left) > 200:
                found.append((hwnd, r.left, r.top, r.right, r.bottom))
        return True

    cbk = ENUMPROC(cb)
    if desk:
        user32.EnumDesktopWindows(desk, cbk, 0)
    else:
        user32.EnumWindows(cbk, 0)
    return found[0] if found else None


def build_stub(base, app, index, orig_eip, call_va=0x560880):
    b = bytearray(b"\x60\x9C")
    b += b"\xB8" + struct.pack("<I", app)
    b += b"\xBA" + struct.pack("<I", 299 + index)
    b += b"\x31\xDB\x31\xFF\x31\xF6"
    rel = (call_va - (base + len(b) + 5)) & 0xFFFFFFFF
    b += b"\xE8" + struct.pack("<I", rel)
    b += b"\x9D\x61"
    b += b"\x68" + struct.pack("<I", orig_eip) + b"\xC3"
    return bytes(b)


def remote_exit(hp, pi, timeout=10.0):
    """Call kernel32!ExitProcess(0) in the target so DLL_PROCESS_DETACH flushes logs.

    Returns (process_exited, elapsed_ms, reason).  Fallback is TerminateProcess by
    the caller; that loses the proxy's 8 MB user-space buffer (F349).
    """
    hp_val = hp.value if hasattr(hp, "value") else hp
    if not hp_val:
        return False, 0, "no process handle"
    psapi = ctypes.WinDLL("psapi")
    psapi.EnumProcessModules.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p),
                                         wt.DWORD, ctypes.POINTER(wt.DWORD)]
    psapi.EnumProcessModules.restype = wt.BOOL
    psapi.GetModuleBaseNameA.argtypes = [ctypes.c_void_p, ctypes.c_void_p,
                                         ctypes.c_char_p, wt.DWORD]
    psapi.GetModuleBaseNameA.restype = wt.DWORD

    mods = (ctypes.c_void_p * 1024)()
    need = wt.DWORD()
    if not psapi.EnumProcessModules(ctypes.c_void_p(hp_val), mods,
                                    ctypes.sizeof(mods), ctypes.byref(need)):
        return False, 0, "EnumProcessModules"

    k32.GetModuleHandleA.restype = ctypes.c_void_p
    k32.GetProcAddress.restype = ctypes.c_void_p
    local_base = k32.GetModuleHandleA(b"kernel32.dll")
    local_exit = k32.GetProcAddress(ctypes.c_void_p(local_base), b"ExitProcess")
    if not local_base or not local_exit:
        return False, 0, "local kernel32!ExitProcess"
    local_base = int(local_base)
    local_exit = int(local_exit)

    remote_base = None
    for i in range(need.value // ctypes.sizeof(ctypes.c_void_p)):
        name = ctypes.create_string_buffer(260)
        n = psapi.GetModuleBaseNameA(ctypes.c_void_p(hp_val), mods[i], name, 260)
        if n and name.value.lower() == b"kernel32.dll":
            remote_base = mods[i].value if hasattr(mods[i], "value") else int(mods[i])
            break
    if not remote_base:
        return False, 0, "remote kernel32 not found"

    addr = remote_base + (local_exit - local_base)
    k32.CreateRemoteThread.restype = wt.HANDLE
    k32.CreateRemoteThread.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t,
                                       ctypes.c_void_p, ctypes.c_void_p, wt.DWORD,
                                       ctypes.POINTER(wt.DWORD)]
    k32.WaitForSingleObject.argtypes = [ctypes.c_void_p, wt.DWORD]
    th = k32.CreateRemoteThread(ctypes.c_void_p(hp_val), None, 0,
                                ctypes.c_void_p(addr), None, 0, None)
    if not th:
        return False, 0, "CreateRemoteThread"
    t0 = time.time()
    k32.WaitForSingleObject(ctypes.c_void_p(pi.hProcess), int(timeout * 1000))
    k32.CloseHandle(th)
    alive = k32.WaitForSingleObject(ctypes.c_void_p(pi.hProcess), 0)
    ms = int((time.time() - t0) * 1000)
    return alive == 0, ms, "ok" if alive == 0 else "still alive"


def parse_levels(spec):
    out = []
    for part in spec.split(","):
        if "-" in part:
            a, b = part.split("-", 1)
            out.extend(range(int(a), int(b) + 1))
        else:
            out.append(int(part))
    return out


NIRCMD = shutil.which("nircmd") or r"C:\Users\K\scoop\apps\nircmd\current\nircmd.exe"


def mute_game():
    if not NIRCMD or not os.path.exists(NIRCMD):
        return False
    ok = True
    for args in (["muteappvolume", "game.exe", "1"],
                 ["setappvolume", "game.exe", "0"]):
        try:
            r = subprocess.run([NIRCMD] + args, capture_output=True, timeout=5)
            ok = ok and (r.returncode == 0)
        except Exception:
            return False
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=DEFAULT_DIR)
    ap.add_argument("--levels", required=True, help="dispatcher indices 0..51, e.g. 0,1,2 or 0-3")
    ap.add_argument("--timeout", type=float, default=20.0)
    ap.add_argument("--gap", type=float, default=1.5)
    ap.add_argument("--out", default=None, help="JSONL output path")
    ap.add_argument("--no-desktop", action="store_true", help="run on the default desktop (debug)")
    ap.add_argument("--no-silent", action="store_true", help="skip the nircmd mute")
    ap.add_argument("--kill", action="store_true",
                    help="TerminateProcess instead of a clean ExitProcess (negative control)")
    ap.add_argument("--exit-mode", choices=("clean", "wmclose", "kill"), default="clean",
                    help="clean=remote ExitProcess; wmclose=PostMessage(WM_CLOSE) then clean fallback")
    ap.add_argument("--exit-timeout", type=float, default=15.0,
                    help="seconds to wait for WM_CLOSE to end the process")
    a = ap.parse_args()

    if ctypes.sizeof(ctypes.c_void_p) != 4:
        raise SystemExit("32-bit Python required (CONTEXT is x86)")
    levels = parse_levels(a.levels)
    bad = [x for x in levels if not (0 <= x < 52)]
    if bad:
        print("bad indices (expect 0..51):", bad)
        return 2
    game_dir = os.path.abspath(a.dir)
    desk = None
    desk_name = "MagDrive_%d" % os.getpid()
    if not a.no_desktop:
        desk = user32.CreateDesktopW(desk_name, None, None, 0, DESKTOP_ALL, None)
        if not desk:
            print("CreateDesktop failed", ctypes.get_last_error())
            return 2

    si = STARTUPINFOW()
    si.cb = ctypes.sizeof(si)
    si.lpDesktop = desk_name if desk else None
    pi = PROCESS_INFORMATION()
    exe = os.path.join(game_dir, "game.exe")
    ok = k32.CreateProcessW(exe, exe, None, None, False, 0, None, game_dir,
                            ctypes.byref(si), ctypes.byref(pi))
    if not ok:
        print("CreateProcess failed", ctypes.get_last_error())
        return 2
    pid = pi.dwProcessId
    print("pid", pid, "desktop", desk_name if desk else "default", flush=True)
    if not a.no_silent:
        muted = False
        for _ in range(10):
            if mute_game():
                muted = True
                break
            time.sleep(0.5)
        print("muted game.exe", muted, flush=True)
    hp = k32.OpenProcess(PROCESS_VM_READ | PROCESS_QUERY_INFORMATION |
                         PROCESS_VM_OPERATION | PROCESS_VM_WRITE |
                         PROCESS_CREATE_THREAD, False, pid)
    out = open(a.out, "w", encoding="utf-8") if a.out else None

    def emit(obj):
        line = json.dumps(obj, ensure_ascii=False)
        print(line, flush=True)
        if out:
            out.write(line + "\n")
            out.flush()

    fails = 0
    try:
        menu = None
        for _ in range(150):
            s = state(hp)
            if s[0] and s[1] and s[2] == 2 and s[3] == 0xFFFFFFFF:
                menu = s
                break
            if k32.WaitForSingleObject(pi.hProcess, 0) == 0:
                print("process exited before MENU")
                return 3
            time.sleep(0.4)
        if not menu:
            print("MENU not reached")
            return 3
        lm = menu[1]
        app = scan_appobj(hp, lm)
        emit({"event": "menu", "lm": lm, "app": app})
        if not app:
            print("appObj not found")
            return 3
        win = find_window(pid, desk)
        if not win:
            print("window not found")
            return 3
        tid = user32.GetWindowThreadProcessId(win[0], None)
        ht = k32.OpenThread(THREAD_SUSPEND_RESUME | THREAD_GET_CONTEXT |
                            THREAD_SET_CONTEXT, False, tid)
        if not ht:
            print("OpenThread failed")
            return 3
        psapi = ctypes.WinDLL("psapi")
        mods = (ctypes.c_void_p * 64)()
        need = wt.DWORD()
        psapi.EnumProcessModules(ctypes.c_void_p(hp), mods, ctypes.sizeof(mods),
                                 ctypes.byref(need))
        base = mods[0] or 0x400000
        stub_addr = k32.VirtualAllocEx(hp, None, 0x1000, MEM_COMMIT | MEM_RESERVE,
                                       PAGE_EXECUTE_READWRITE)
        emit({"event": "window", "tid": tid, "base": base, "stub": stub_addr})

        for idx in levels:
            if not a.no_silent:
                mute_game()
            t0 = time.time()
            n = k32.SuspendThread(ctypes.c_void_p(ht))
            ctx = CONTEXT()
            ctx.ContextFlags = CONTEXT_FULL
            if not k32.GetThreadContext(ctypes.c_void_p(ht), ctypes.byref(ctx)):
                emit({"index": idx, "ok": False, "why": "GetThreadContext"})
                fails += 1
                break
            stub = build_stub(stub_addr, app, idx, ctx.Eip,
                              base + (0x560880 - 0x400000))
            buf = ctypes.create_string_buffer(stub, len(stub))
            wr = ctypes.c_size_t(0)
            if not k32.WriteProcessMemory(hp, ctypes.c_void_p(stub_addr), buf,
                                          len(stub), ctypes.byref(wr)):
                emit({"index": idx, "ok": False, "why": "WriteProcessMemory"})
                fails += 1
                break
            ctx.Eip = stub_addr
            ctx.ContextFlags = CONTEXT_FULL
            if not k32.SetThreadContext(ctypes.c_void_p(ht), ctypes.byref(ctx)):
                emit({"index": idx, "ok": False, "why": "SetThreadContext"})
                fails += 1
                break
            k32.ResumeThread(ctypes.c_void_p(ht))

            ok = False
            last = None
            while time.time() - t0 < a.timeout:
                time.sleep(0.2)
                s = state(hp, app)
                last = s
                if (s[2] == 1 and s[3] == idx and s[4]
                        and u8(hp, lm + 8) == 1):
                    ok = True
                    break
                if k32.WaitForSingleObject(pi.hProcess, 0) == 0:
                    break
            emit({"index": idx, "ok": ok, "ms": int((time.time() - t0) * 1000),
                  "state": last, "lm8": u8(hp, lm + 8)})
            if not ok:
                fails += 1
                if k32.WaitForSingleObject(pi.hProcess, 0) == 0:
                    emit({"event": "exited", "after": idx})
                    break
            time.sleep(a.gap)
        exit_ok = True
        if a.exit_mode == "wmclose" and not a.kill:
            win = find_window(pid, desk)
            if not win:
                exit_info = {"event": "exit", "mode": "wmclose", "ok": False,
                             "why": "no window"}
            else:
                user32.PostMessageW(win[0], 0x0010, 0, 0)
                t0 = time.time()
                while time.time() - t0 < a.exit_timeout:
                    if k32.WaitForSingleObject(pi.hProcess, 0) == 0:
                        code = ctypes.c_ulong()
                        k32.GetExitCodeProcess(pi.hProcess, ctypes.byref(code))
                        exit_info = {"event": "exit", "mode": "wmclose", "ok": code.value == 0,
                                     "code": code.value,
                                     "ms": int((time.time() - t0) * 1000)}
                        break
                    time.sleep(0.1)
                else:
                    exit_info = {"event": "exit", "mode": "wmclose", "ok": False,
                                 "why": "timeout"}
            if not exit_info["ok"]:
                clean_ok, ms, why = remote_exit(hp, pi)
                exit_info["fallback"] = {"mode": "clean", "ok": clean_ok,
                                         "ms": ms, "why": why}
                exit_ok = False
            emit(exit_info)
        emit({"event": "summary", "levels": len(levels), "fail": fails,
              "exit_mode": a.exit_mode})
        return 0 if fails == 0 and exit_ok else 1
    finally:
        if a.kill:
            a.exit_mode = "kill"
        alive = k32.WaitForSingleObject(pi.hProcess, 0) != 0
        if a.exit_mode == "kill":
            try:
                k32.TerminateProcess(ctypes.c_void_p(pi.hProcess), 0)
            except Exception:
                pass
            if out:
                emit({"event": "exit", "mode": "kill", "ok": True, "why": "kill"})
        elif alive:
            clean_ok, ms, why = remote_exit(hp, pi)
            if out:
                emit({"event": "exit", "mode": "clean", "ok": clean_ok,
                      "ms": ms, "why": why})
            if not clean_ok:
                try:
                    k32.TerminateProcess(ctypes.c_void_p(pi.hProcess), 0)
                except Exception:
                    pass
        if out:
            out.close()
        try:
            k32.CloseHandle(ctypes.c_void_p(pi.hThread))
            hp_val = hp.value if hasattr(hp, "value") else hp
            if hp_val:
                k32.CloseHandle(ctypes.c_void_p(hp_val))
        except Exception:
            pass
        if desk:
            try:
                user32.CloseDesktop(ctypes.c_void_p(desk))
            except Exception:
                pass
        print("exit", a.exit_mode, pid, flush=True)


if __name__ == "__main__":
    sys.exit(main())
