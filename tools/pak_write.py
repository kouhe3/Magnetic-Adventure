#!/usr/bin/env python3
"""Pak v0.2 写回：round-trip、同名替换、条目导出、校验。

格式（tools/pak.py + F05/F17/F387）：
  u32 toc_size            = 24 * (count + 1)
  char magic[25]          = "[Pak Header Info Ver 0.2]"
  rec entries[count]      = { u8 namelen; name[n]; pad[15-n]; u32 off; u32 size }
  rec trailer             = 同上；off 字段是 payload 总长（可带 0x80000000 标志）
  u8 payload[...]         = entries 顺序拼接 + trailer 数据
无压缩。重建时保留每条记录的 name/pad，只重算 off/size；同名替换不改变 TOC 条目数。

用法:
  python tools/pak_write.py roundtrip <pak> <out>
  python tools/pak_write.py rebuild   <pak> <out> name1=file1 [name2=file2 ...]
  python tools/pak_write.py extract   <pak> <name> <out>
  python tools/pak_write.py verify    <pak>

判据:
  * roundtrip: 输出与输入**逐字节相同**（exit 0），否则 exit 1；
  * rebuild: 输出能被 `tools/pak.py verify` 接受（entries/base/sum 不变，png/ogg/lua 计数不变），
    且目标条目内容等于给定文件；
  * extract: 输出字节等于 pak 中该条目的 size 字节。

覆盖边界:
  * 只支持**同名替换**（不新增/删除 entry、不改 `lvl_info.lvl` 或地图节点）；
  * 不做 Lua 语义校验、不检查游戏能否加载；加载验证用 `tools/direct_drive.py` + B2 代理；
  * 测试 pak 必须写到副本目录（如 `work/pak_test_game/data`），`bin/gametop` 只读。

失效条件:
  * 记录 namelen 与 pad 长度不是 15，或 name 含无法用 latin1 表示的字符；
  * trailer 的 off 字段不是 payload 总长（低 31 位）——格式升级时本工具拒绝；
  * 输入 pak 的 entry off 不连续（按 `tools/pak.py verify` 会报 PROBLEMS）。
"""
import os
import struct
import sys

MAGIC = b"[Pak Header Info Ver 0.2]"
HEAD = 4 + len(MAGIC)
REC = 24


def parse(path):
    d = open(path, "rb").read()
    toc_size = struct.unpack_from("<I", d, 0)[0]
    if d[4:4 + len(MAGIC)] != MAGIC:
        raise ValueError("bad magic")
    if toc_size % REC:
        raise ValueError("bad toc_size")
    count = toc_size // REC - 1
    base = HEAD + toc_size
    entries = []
    pos = HEAD
    for _ in range(count + 1):
        n = d[pos]
        name = d[pos + 1:pos + 1 + n].decode("latin1")
        pad = d[pos + 1 + n:pos + 16]
        off, size = struct.unpack_from("<II", d, pos + 16)
        entries.append({"name": name, "off": off, "size": size, "pad": pad})
        pos += REC
    trailer = entries.pop()
    for e in entries:
        e["data"] = d[base + e["off"]:base + e["off"] + e["size"]]
    toff = trailer["off"] & 0x7FFFFFFF
    trailer["data"] = d[base + toff:base + toff + trailer["size"]]
    return entries, trailer


def build(entries, trailer):
    toc_size = REC * (len(entries) + 1)
    payload = bytearray()
    recs = bytearray()
    for e in entries:
        name = e["name"].encode("latin1")
        if len(name) + len(e["pad"]) != 15:
            raise ValueError("bad name/pad for %r" % e["name"])
        recs += bytes([len(name)]) + name + e["pad"]
        recs += struct.pack("<II", len(payload), len(e["data"]))
        payload += e["data"]
    flag = trailer["off"] & 0x80000000
    name = trailer["name"].encode("latin1")
    recs += bytes([len(name)]) + name + trailer["pad"]
    recs += struct.pack("<II", len(payload) | flag, len(trailer["data"]))
    payload += trailer["data"]
    return struct.pack("<I", toc_size) + MAGIC + bytes(recs) + bytes(payload)


def find(entries, name):
    for e in entries:
        if e["name"] == name:
            return e
    raise KeyError(name)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    cmd = sys.argv[1]
    if cmd == "roundtrip":
        src, out = sys.argv[2], sys.argv[3]
        entries, trailer = parse(src)
        blob = build(entries, trailer)
        open(out, "wb").write(blob)
        same = open(src, "rb").read() == blob
        print("wrote", out, "bytes", len(blob), "byte_identical", same)
        return 0 if same else 1
    if cmd == "rebuild":
        src, out = sys.argv[2], sys.argv[3]
        pairs = [a.split("=", 1) for a in sys.argv[4:]]
        if not pairs:
            raise SystemExit("rebuild needs name=file pairs")
        entries, trailer = parse(src)
        for name, path in pairs:
            e = find(entries, name)
            e["data"] = open(path, "rb").read()
            print("replace", name, len(e["data"]))
        blob = build(entries, trailer)
        open(out, "wb").write(blob)
        print("wrote", out, "bytes", len(blob), "replaced", len(pairs))
        return 0
    if cmd == "extract":
        src, name, out = sys.argv[2], sys.argv[3], sys.argv[4]
        entries, _ = parse(src)
        e = find(entries, name)
        open(out, "wb").write(e["data"])
        print("extracted", name, len(e["data"]), "->", out)
        return 0
    if cmd == "verify":
        from pak import verify
        return 0 if verify(sys.argv[2]) else 1
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
