"""把启动期 GL 日志里的 37 次 `glTexImage2D` 映射回 pak 素材，打成宿主能直接吃的纹理包。

原理：代理在 `glTexImage2D` 时对**整个像素缓冲**算 CRC32（连同字节数写进记录的 mem2）。
本工具对 pak 里的 PNG/JPG 解码成 RGBA，按「上传格式（RGB/RGBA）+ 是否上下翻转（GL 是
自下而上）+ 通道序」生成候选字节串，用 `zlib.crc32` 精确匹配 —— 比「192 B 前缀」可靠
（前缀对边界均匀的图会多图同分，见 F183）。

用法:
  python tools/gl_texpack.py <startup_log> --pak work/pak_gametop \
      --out work/menu_tex.bin --manifest work/menu_tex.json

输出:
  <out>       "GLTEX01\\0" + u32 count + count × {u32 id, u32 w, u32 h, RGBA 像素}
              像素按**自下而上**存放（与 GL 上传顺序一致），宿主直接 glTexImage2D 即可。
  <manifest>  {"textures":[{"id":1,"asset":"mcur_1.png","w":64,"h":64,"fmt":"RGBA"}…]}

覆盖边界：只处理 `GLFFI02` 且需要在抓取时打开 `GLPROXY_ONLY` 里的 `glTexImage2D`；
匹配失败（运行时生成/合成的纹理）会在 manifest 里标 `"asset": null` 并跳过像素。

依据：docs/facts.md F183。
"""
import argparse
import glob
import json
import os
import struct
import sys
import zlib

import gl_ffi


def load_uploads(log):
    """返回 [(id, w, h, fmt, crc, nbytes)]，按日志顺序（id 来自前一条 glBindTexture）。"""
    nm = gl_ffi.names()
    s = gl_ffi.load(log)
    s["path"] = log
    blob = open(log, "rb").read()
    bind = [k for k, v in nm.items() if v == "glBindTexture"][0]
    te = [k for k, v in nm.items() if v == "glTexImage2D"][0]
    cur = None
    out = []
    for i, rid in enumerate(s["ids"]):
        r = s["rec"].unpack_from(blob, gl_ffi.HDR_SIZE + i * s["rec"].size)
        if rid == bind:
            cur = r[7]
        elif rid == te:
            a = r[6:18]
            m = r[18][384:576]
            crc, n = struct.unpack("<II", m[:8])
            out.append((cur, a[3], a[4], a[6], crc, n))
    return out


def variants(im, fmt):
    """按上传格式生成候选字节串：(名称, bytes)。GL 的贴图数据是自下而上的。"""
    raw = im.tobytes()
    w, h = im.size
    rows = [raw[i * w * 4:(i + 1) * w * 4] for i in range(h)]
    for flip in (0, 1):
        rs = rows[::-1] if flip else rows
        tag = "_flip" if flip else ""
        if fmt == 0x1907:                 # GL_RGB
            b = bytearray()
            for row in rs:
                for k in range(0, len(row), 4):
                    b += row[k:k + 3]
            yield "rgb" + tag, bytes(b)
            yield "bgr" + tag, bytes(bytearray(
                [x for k in range(0, len(b), 3) for x in (b[k + 2], b[k + 1], b[k])]))
        else:                             # GL_RGBA
            yield "rgba" + tag, b"".join(rs)
            b2 = bytearray()
            for row in rs:
                for k in range(0, len(row), 4):
                    b2 += bytes((row[k + 2], row[k + 1], row[k], row[k + 3]))
            yield "bgra" + tag, bytes(b2)


def index_assets(pak_dir):
    """(w,h) -> [(name, PIL.Image)]，只索引 pak 里的 png/jpg。"""
    from PIL import Image
    lab = {}
    for p in glob.glob(os.path.join(pak_dir, "*.png")) + glob.glob(os.path.join(pak_dir, "*.jpg")):
        try:
            im = Image.open(p).convert("RGBA")
        except Exception:
            continue
        lab.setdefault((im.width, im.height), []).append((os.path.basename(p), im))
    return lab


def pak_fingerprint(pak_dir):
    """pak 目录的廉价指纹：文件名 + size + mtime_ns，用于缓存失效。"""
    import hashlib
    h = hashlib.md5()
    files = sorted(glob.glob(os.path.join(pak_dir, "*.png")) +
                   glob.glob(os.path.join(pak_dir, "*.jpg")))
    for p in files:
        st = os.stat(p)
        h.update(os.path.basename(p).encode("utf-8", "replace"))
        h.update(b"|%d|%d\n" % (st.st_size, getattr(st, "st_mtime_ns", 0)))
    return h.hexdigest()


def crc_table(pak_dir, cache_path=None):
    """(w,h,fmt,nbytes,crc) -> 素材名；按 pak 指纹缓存在 work/ 下。

    与 `index_assets` + `variants` 的直查逐条等价：同一 (w,h) 的候选顺序、
    同一 variants 顺序、`setdefault` 取首个命中（CRC 冲突时的旧行为）。
    缓存文件损坏或指纹不符 ⇒ 重建，不静默返回错误表。
    """
    cache_path = cache_path or os.path.join("work", "pak_crc_index.json")
    fp = pak_fingerprint(pak_dir)
    try:
        with open(cache_path, encoding="utf-8") as f:
            d = json.load(f)
        if d.get("fingerprint") == fp and isinstance(d.get("entries"), list):
            return {(int(e[0]), int(e[1]), int(e[2]), int(e[3]), int(e[4])): e[5]
                    for e in d["entries"]}
    except Exception:
        pass
    lab = index_assets(pak_dir)
    tab = {}
    entries = []
    for (w, h), items in lab.items():
        for name, im in items:
            for fmt in (0x1907, 0x1908):
                for _tag, b in variants(im, fmt):
                    crc = zlib.crc32(b) & 0xFFFFFFFF
                    key = (w, h, fmt, len(b), crc)
                    if key not in tab:
                        tab[key] = name
                        entries.append([w, h, fmt, len(b), crc, name])
    os.makedirs(os.path.dirname(os.path.abspath(cache_path)), exist_ok=True)
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump({"fingerprint": fp, "entries": entries}, f)
    return tab


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("log")
    ap.add_argument("--pak", default="work/pak_gametop")
    ap.add_argument("--out", default="work/menu_tex.bin")
    ap.add_argument("--manifest", default="work/menu_tex.json")
    ap.add_argument("--csv", default="", help="可选：把 id↔素材映射写成 CRLF 的 mapping/textures.csv")
    a = ap.parse_args()

    ups = load_uploads(a.log)
    if not ups:
        raise SystemExit("日志里没有 glTexImage2D（抓取时要设 GLPROXY_ONLY 含它）")
    lab = index_assets(a.pak)

    entries = []
    for tid, w, h, fmt, crc, n in ups:
        hit = None
        for name, im in lab.get((w, h), []):
            for tag, b in variants(im, fmt):
                if len(b) == n and (zlib.crc32(b) & 0xFFFFFFFF) == crc:
                    hit = (name, tag, b)
                    break
            if hit:
                break
        if not hit:
            entries.append({"id": tid, "w": w, "h": h, "fmt": "RGB" if fmt == 0x1907 else "RGBA",
                            "asset": None, "pixels": None})
            continue
        name, tag, b = hit
        # 统一转成 RGBA 像素（宿主按 RGBA 上传；alpha=255 与 GL 的 RGB 采样等价）
        if fmt == 0x1907:
            if tag.startswith("bgr"):
                rgb = bytearray(len(b))
                for k in range(0, len(b), 3):
                    rgb[k] = b[k + 2]; rgb[k + 1] = b[k + 1]; rgb[k + 2] = b[k]
                b = bytes(rgb)
            px = bytearray(len(b) // 3 * 4)
            for k in range(0, len(b), 3):
                d = k // 3 * 4
                px[d] = b[k]; px[d + 1] = b[k + 1]; px[d + 2] = b[k + 2]; px[d + 3] = 255
            px = bytes(px)
        else:
            if tag.startswith("bgra"):
                px = bytearray(len(b))
                for k in range(0, len(b), 4):
                    px[k] = b[k + 2]; px[k + 1] = b[k + 1]; px[k + 2] = b[k]; px[k + 3] = b[k + 3]
                px = bytes(px)
            else:
                px = b
        entries.append({"id": tid, "w": w, "h": h,
                        "fmt": "RGB" if fmt == 0x1907 else "RGBA",
                        "asset": name, "pixels": px})

    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(a.out, "wb") as f:
        f.write(b"GLTEX01\0")
        f.write(struct.pack("<I", len(entries)))
        for e in entries:
            f.write(struct.pack("<III", e["id"], e["w"], e["h"]))
            if e["pixels"] is not None:
                f.write(e["pixels"])
    with open(a.manifest, "w", encoding="utf-8") as f:
        json.dump({"textures": [{k: e[k] for k in ("id", "w", "h", "fmt", "asset")}
                                for e in entries]}, f, ensure_ascii=False, indent=1)
    if a.csv:
        # 仓库约定：git 追踪的文本用 CRLF（.gitattributes 是 * -text）
        with open(a.csv, "w", encoding="ascii", newline="") as f:
            f.write("id,asset,w,h,fmt\r\n")
            for e in entries:
                f.write("%d,%s,%d,%d,%s\r\n" % (e["id"], e["asset"] or "", e["w"], e["h"],
                                                e["fmt"]))
    ok = sum(1 for e in entries if e["asset"])
    print("textures=%d matched=%d bytes=%d" % (len(entries), ok, os.path.getsize(a.out)))
    for e in entries:
        if not e["asset"]:
            print("  unmatched id=%d %dx%d %s" % (e["id"], e["w"], e["h"], e["fmt"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
