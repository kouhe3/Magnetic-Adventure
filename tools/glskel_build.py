"""用 FPC 2.2.4 + LCL 0.9.28.3 编 glskel5 骨架（含 GLScene 视口）。

用途：版本夹逼时对同一份骨架换 GLScene 源码树重编；`ver_bisect.py` 会调用它。
用法: python tools/glskel_build.py <glscene-tree> <out-dir> [pas]
前置：C:/lazarus/fpc/2.2.4 + 自编 LCL 0.9.28.3 在 C:/tmp/laz9283（见 HANDOFF §3.2）。
"""
import glob
import os
import shutil
import subprocess
import sys

FPC = "C:/lazarus/fpc/2.2.4/bin/i386-win32/fpc.exe"
FPC_UNITS = "C:/lazarus/fpc/2.2.4/units/i386-win32"
LCL_UNITS = ["C:/tmp/laz9283/lcl/units/i386-win32",
             "C:/tmp/laz9283/lcl/units/i386-win32/win32"]


def dirs_with(root, ext):
    return sorted({os.path.dirname(p).replace("\\", "/")
                   for p in glob.glob(root + "/**/*." + ext, recursive=True)})


def main():
    tree = sys.argv[1].replace("\\", "/")
    out = sys.argv[2].replace("\\", "/")
    pas = sys.argv[3] if len(sys.argv) > 3 else "tools/glskel6.pas"
    src = tree + "/Source" if os.path.isdir(tree + "/Source") else tree
    args = [FPC, "-n", "-Mdelphi", "-O1", "-g-", "-Xs-", "-Xm", "-dLCL", "-dLCLwin32"]
    for d in dirs_with(src, "pas") + LCL_UNITS + dirs_with(FPC_UNITS, "ppu"):
        args.append("-Fu" + d)
    inc = dirs_with(src, "inc") + dirs_with(FPC_UNITS, "inc")
    for d in inc:
        args.append("-Fi" + d)
    os.makedirs(out, exist_ok=True)
    args += ["-FE" + out, "-FU" + out, pas]
    r = subprocess.run(args, capture_output=True, text=True, errors="replace")
    tail = (r.stdout or "").strip().splitlines()[-40:]
    print("\n".join(tail))
    if r.returncode != 0:
        print("STDERR:", (r.stderr or "")[-2000:])
    exe = os.path.splitext(os.path.basename(pas))[0] + ".exe"
    # 崩溃捕获（F315–F317）：CMake 的 crashlog.dll 若已构建，放到宿主旁边，
    # 这样 CRASHLOG_DIR/CRASHLOG_LOG 开启时 magnet.pas 能直接 LoadLibrary。
    if r.returncode == 0:
        dll = "build/Release/crashlog.dll"
        if os.path.exists(dll):
            shutil.copy2(dll, os.path.join(out, "crashlog.dll"))
    print("rc=%d exe=%s" % (r.returncode, os.path.exists(out + "/" + exe)))
    return r.returncode


if __name__ == "__main__":
    sys.exit(main())
