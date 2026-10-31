"""生成 src/objlog/sites.h：把 work/add_bps_all.txt 的 65 个 call 点变成 (站点RVA, 目标RVA, tag, 是否取名字)。

用法：
  python tools/gen_objlog.py [--list work/add_bps_all.txt] [--exe work/winprobe_game/game.exe] [--out src/objlog/sites.h]

判据：列表里每个地址都是 `E8 rel32` 调用之后的返回地址；脚本自校验 65/65 全为 E8，否则报错退出。
"""
import argparse
import struct

NAMED = ("Add_GraphSprite", "Add_LevelMaterial", "Add_AlphaHint",
         "Add_NextButton", "Add_CloseButton", "Add_WoodGear")


def sections(exe):
    pe = struct.unpack_from("<I", exe, 0x3C)[0]
    nsec = struct.unpack_from("<H", exe, pe + 6)[0]
    optsz = struct.unpack_from("<H", exe, pe + 20)[0]
    opt = pe + 24
    base = struct.unpack_from("<I", exe, opt + 28)[0]
    sec = opt + optsz
    out = []
    for i in range(nsec):
        o = sec + 40 * i
        name = exe[o:o + 8].rstrip(b"\0").decode()
        vs, va, rs, ra = struct.unpack_from("<IIII", exe, o + 8)
        out.append((name, base + va, rs, ra))
    return out


def off(sects, rva):
    for n, va, rs, ra in sects:
        if va <= rva < va + rs:
            return ra + (rva - va)
    raise KeyError(hex(rva))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", default="work/add_bps_all.txt")
    ap.add_argument("--exe", default="work/winprobe_game/game.exe")
    ap.add_argument("--out", default="src/objlog/sites.h")
    a = ap.parse_args()

    exe = open(a.exe, "rb").read()
    sects = sections(exe)
    rows = []
    for line in open(a.list):
        line = line.strip()
        if not line:
            continue
        site = int(line.split("\t")[0], 16)
        tag = line.split("\t")[1].strip()
        o = off(sects, site - 5)
        b = exe[o:o + 5]
        if b[0] != 0xE8:
            raise SystemExit("site 0x%X 前 5 字节不是 E8 调用：%s" % (site, b.hex()))
        tgt = (site + struct.unpack_from("<i", b, 1)[0]) & 0xFFFFFFFF
        rows.append((site, tgt, tag, 1 if tag in NAMED else 0))

    with open(a.out, "w", newline="\n") as fh:
        fh.write("// 生成物：python tools/gen_objlog.py；勿手改。\n")
        fh.write("typedef struct { DWORD site; DWORD target; const char *tag; int named; } OBJLOG_SITE;\n")
        fh.write("static const OBJLOG_SITE kSites[%d] = {\n" % len(rows))
        for site, tgt, tag, named in rows:
            fh.write('    {0x%08X, 0x%08X, "%s", %d},\n' % (site, tgt, tag, named))
        fh.write("};\n")
    print("sites=%d -> %s" % (len(rows), a.out))


if __name__ == "__main__":
    main()
