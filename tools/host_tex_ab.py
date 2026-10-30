"""宿主上传的纹理像素 vs 原版 glTexImage2D 整块像素 CRC —— T3.2c 的逐字节判据。

用法:
  HOST_TEX_CRC=work/host_tex_crc.txt python tools/shot_window.py build/Release/magnethost.exe ...
  python tools/host_tex_ab.py work/glprobe/glffi8.bin work/host_tex_crc.txt

输入:
  <gl_log>        GLFFI02 启动期日志（抓取时 GLPROXY_ONLY 要含 glTexImage2D，见 F183）
  <crc_file>      宿主写的每张纹理 CRC：`id asset w h crc32`（HOST_TEX_CRC 环境变量）
判据:
  逐 id 比 (w, h, crc32)；任何一个不等即 DIFF。CRC 覆盖的字节串与原版上传格式一致
  （GL_RGB 纹理 = RGB 3 字节/像素，GL_RGBA = 4 字节，均为自下而上）。
覆盖边界:
  只比 level 0 的像素；mipmap 链由宿主用 gluBuild2DMipmaps 生成，原版是 GL_GENERATE_MIPMAP，
  两边都没有被记录。⇒ 这条判据过了**不等于** mipmap 也一致。
依据: docs/facts.md F183（37 次上传的格式与 CRC）、F185（WIC 解码 37/37 一致）。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gl_texpack  # noqa: E402


def main():
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    ups = {u[0]: u for u in gl_texpack.load_uploads(sys.argv[1])}
    if not ups:
        raise SystemExit("日志里没有 glTexImage2D")
    seen = set()
    bad = 0
    for line in open(sys.argv[2], encoding="utf-8"):
        f = line.split()
        if len(f) < 5:
            continue
        tid, asset, w, h, crc = int(f[0]), f[1], int(f[2]), int(f[3]), int(f[4], 16)
        u = ups.get(tid)
        seen.add(tid)
        ok = u and (w, h, crc) == (u[1], u[2], u[4])
        if not ok:
            bad += 1
            print("id=%-2d %-12s DIFF host=(%d,%d,%08x) oracle=%s" %
                  (tid, asset, w, h, crc, None if not u else "(%d,%d,%08x)" % (u[1], u[2], u[4])))
    missing = sorted(set(ups) - seen)
    for tid in missing:
        bad += 1
        print("id=%-2d 缺宿主记录（原版 %dx%d fmt=%#x）" % (tid, ups[tid][1], ups[tid][2], ups[tid][3]))
    print("host_tex diffs=%d / %d" % (bad, len(ups)))
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
