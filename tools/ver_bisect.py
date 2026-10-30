"""版本夹逼：对一批 GLScene 修订重编骨架，用 code_match funcs 的 sim 打分。

用法: python tools/ver_bisect.py 4690 4704 4710 ...
前置: bin/gametop/game.exe；LCL 0.9.28.3 自编树 C:/tmp/laz9283。
输出: 每个修订一行 —— 各单元 sim>=0.95 的字节占比 + 加权总分。
"""
import os
import re
import subprocess
import sys

SVN = r"C:\Program Files\TortoiseSVN\bin\svn.exe"
URL = "https://svn.code.sf.net/p/glscene/code/trunk/Source"
WC = "work/bisect/src"
UNITS = ["OpenGL1x.o", "GLObjects.o", "GLTexture.o", "GLBitmapFont.o",
         "GLLCLViewer.o", "GLScene.o"]


def sh(args, **kw):
    return subprocess.run(args, capture_output=True, text=True, errors="replace", **kw)


def main():
    revs = sys.argv[1:]
    if not revs:
        print(__doc__)
        return 1
    if not os.path.isdir(WC + "/.svn"):
        print("checkout", URL)
        r = sh([SVN, "checkout", "-q", "-r", revs[0], URL, WC])
        if r.returncode:
            print(r.stderr[:400])
            return 1
    print("%-6s %s" % ("rev", "  ".join(u.replace(".o", "") for u in UNITS)))
    for rev in revs:
        r = sh([SVN, "update", "-q", "-r", rev, WC])
        if r.returncode:
            print("%-6s SVNUPDATE-FAIL %s" % (rev, r.stderr[:120]))
            continue
        out = "work/bisect/out_r%s" % rev
        r = sh([sys.executable, "tools/glskel_build.py", WC, out])
        if "rc=0 exe=True" not in (r.stdout + r.stderr):
            print("%-6s BUILD-FAIL %s" % (rev, (r.stdout or "").strip().splitlines()[-1:]))
            continue
        vals = []
        for u in UNITS:
            r = sh([sys.executable, "tools/code_match.py", "funcs", "bin/gametop/game.exe",
                    out + "/glskel5.exe", "--unit", u, "--top", "0"])
            m = re.search(r"sim 0\.95-1\.00:\s+(\d+) B\s+([\d.]+)%", r.stdout)
            vals.append(float(m.group(2)) if m else -1.0)
        total = sum(vals) / len(vals)
        print("%-6s %s   avg=%.1f" % (rev, "  ".join("%6.1f" % v for v in vals), total),
              flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
