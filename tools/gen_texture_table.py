"""把 mapping/textures.csv 生成宿主的纹理表头（生成物入库，同 proxy_stubs.c 的做法）。

用法:
  python tools/gen_texture_table.py [mapping/textures.csv] [src/host/texture_table.h]

输入 : id,asset,w,h,fmt —— 由 tools/gl_texpack.py --csv 从启动期 GL 日志（F183）产出
输出 : src/host/texture_table.h —— {id, 素材名, 上传格式} 的静态表
判据 : asset 为空的行（运行时合成的纹理）直接跳过并打印，生成结果必须与之 1:1 对上。

依据：docs/facts.md F183。
"""
import csv
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "mapping", "textures.csv")
    dst = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "src", "host",
                                                             "texture_table.h")
    rows = []
    skipped = []
    with open(src, encoding="ascii", newline="") as f:
        for r in csv.DictReader(f):
            if not r["asset"]:
                skipped.append(int(r["id"]))
                continue
            rows.append((int(r["id"]), r["asset"], r["fmt"] == "RGB"))
    lines = [
        "// 生成物，勿手改 —— python tools/gen_texture_table.py mapping/textures.csv",
        "// 依据 docs/facts.md F183：启动期 37 次 glTexImage2D 的 id 与 pak 素材一一对应；",
        "// rgb=true 表示原版按 GL_RGB/GL_RGB8 上传（5 张 JPG），其余是 GL_RGBA/GL_RGBA8。",
        "#pragma once",
        "",
        "namespace host {",
        "",
        "struct TextureDef {",
        "  unsigned id;",
        "  const char* asset;",
        "  bool rgb;",
        "};",
        "",
        "static const TextureDef kTextures[] = {",
    ]
    for tid, name, rgb in rows:
        lines.append('    {%d, "%s", %s},' % (tid, name, "true" if rgb else "false"))
    lines += ["};", "", "}  // namespace host", ""]
    with open(dst, "w", encoding="utf-8", newline="") as f:
        f.write("\r\n".join(lines))
    print("rows=%d skipped(no asset)=%d -> %s" % (len(rows), len(skipped), dst))
    if skipped:
        print("  skipped ids:", skipped)
    return 0


if __name__ == "__main__":
    sys.exit(main())
