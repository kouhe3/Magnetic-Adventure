"""把 DLL 注入运行中的进程（32 位 Python 必需，否则地址被截断）。

用法：
  python tools/inject_dll.py <pid> build/Release/objlog.dll

原理：VirtualAllocEx 写入路径 → CreateRemoteThread(LoadLibraryA)。打印目标进程里
DLL 的基址（= 远程线程的返回值），0 表示失败（LoadLibrary 返回 NULL）。
"""
import ctypes
import sys

k32 = ctypes.WinDLL("kernel32", use_last_error=True)
k32.OpenProcess.restype = ctypes.c_void_p
k32.VirtualAllocEx.restype = ctypes.c_void_p
k32.VirtualAllocEx.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t,
                               ctypes.c_uint32, ctypes.c_uint32]
k32.WriteProcessMemory.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p,
                                   ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t)]
k32.GetModuleHandleA.restype = ctypes.c_void_p
k32.GetProcAddress.restype = ctypes.c_void_p
k32.GetProcAddress.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
k32.CreateRemoteThread.restype = ctypes.c_void_p
k32.CreateRemoteThread.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t,
                                   ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint32,
                                   ctypes.c_void_p]
k32.WaitForSingleObject.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
k32.GetExitCodeThread.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_ulong)]

PROCESS_ALL_ACCESS = 0x1F0FFF


def inject(pid, dll_path):
    h = k32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
    if not h:
        raise OSError("OpenProcess failed: %d" % ctypes.get_last_error())
    buf = dll_path.encode("mbcs") + b"\0"
    remote = k32.VirtualAllocEx(h, None, len(buf), 0x3000, 0x04)
    if not remote:
        raise OSError("VirtualAllocEx failed: %d" % ctypes.get_last_error())
    wr = ctypes.c_size_t(0)
    k32.WriteProcessMemory(h, remote, buf, len(buf), ctypes.byref(wr))
    load = k32.GetProcAddress(k32.GetModuleHandleA(b"kernel32.dll"), b"LoadLibraryA")
    th = k32.CreateRemoteThread(h, None, 0, load, remote, 0, None)
    if not th:
        raise OSError("CreateRemoteThread failed: %d" % ctypes.get_last_error())
    k32.WaitForSingleObject(th, 5000)
    code = ctypes.c_ulong(0)
    k32.GetExitCodeThread(th, ctypes.byref(code))
    return code.value


if __name__ == "__main__":
    base = inject(int(sys.argv[1]), sys.argv[2])
    print("objlog base in target: 0x%08X" % base)
    sys.exit(0 if base else 1)
