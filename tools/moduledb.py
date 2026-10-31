"""Read/write x64dbg module database (LZ4 legacy frame + JSON).

Format (release/x32/headless/db/<module>.dd32):
  4 bytes magic 0x184C2102 (LE)  = LZ4 legacy frame
  4 bytes compressed block size
  block: LZ4 raw block of UTF-8 JSON

Usage:
  python tools/moduledb.py show <db>            # dump json
  python tools/moduledb.py inject <db> <exe> <bps.txt>
      bps.txt lines "0xADDR<TAB>tag"; entries get logText "#HB <tag> {x:eax} {x:edx}",
      fastResume=true, silent=false, and real oldbytes read from the exe by RVA.
"""
import json
import struct
import sys

import lz4.block

MAGIC = 0x184C2102


def load(path):
    b = open(path, "rb").read()
    magic, = struct.unpack("<I", b[:4])
    if magic != MAGIC:
        raise SystemExit("bad magic %08X" % magic)
    size, = struct.unpack("<I", b[4:8])
    d = lz4.block.decompress(b[8:8 + size], uncompressed_size=1 << 22)
    return json.loads(d)


def save(path, obj):
    data = json.dumps(obj, indent=1).encode("utf-8")
    blk = lz4.block.compress(data, store_size=False)
    out = struct.pack("<II", MAGIC, len(blk)) + blk
    open(path, "wb").write(out)


def rva_bytes(exe, rva, n):
    b = open(exe, "rb").read()
    e_lfanew, = struct.unpack("<I", b[0x3C:0x40])
    nsec, = struct.unpack("<H", b[e_lfanew + 6:e_lfanew + 8])
    opt = e_lfanew + 24
    for i in range(nsec):
        s = opt + struct.unpack("<H", b[e_lfanew + 20:e_lfanew + 22])[0] + i * 40
        va, vsz, rs, _ = struct.unpack("<IIII", b[s + 12:s + 28])
        if va <= rva < va + max(vsz, rs):
            off = rs + (rva - va)
            return b[off:off + n]
    raise SystemExit("rva %X outside sections" % rva)


def oldbytes(exe, rva):
    bb = rva_bytes(exe, rva, 2)
    v = bb[0] | (bb[1] << 8)
    return "0x%04X" % v


def main():
    cmd, db = sys.argv[1], sys.argv[2]
    obj = load(db)
    if cmd == "show":
        print(json.dumps(obj, indent=1))
        return
    exe, bplist = sys.argv[3], sys.argv[4]
    bps = []
    for line in open(bplist, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        a, _, tag = line.partition("\t")
        bps.append((int(a, 0), tag))
    obj["breakpoints"] = []
    for addr, tag in bps:
        rva = addr - 0x400000
        obj["breakpoints"].append({
            "address": "0x%X" % rva,
            "enabled": True,
            "oldbytes": oldbytes(exe, rva),
            "type": 0,
            "titantype": "0x0",
            "name": tag,
            "module": "game.exe",
            "breakCondition": "",
            "logText": "#HB %s {x:eax} {x:edx} {x:[eax]} {x:[eax+8]} {x:[eax+0xC]}%s" % (tag, " {s:edx+8}" if tag in ("Add_GraphSprite","Add_LevelMaterial","Add_AlphaHint","Add_NextButton","Add_CloseButton","Add_WoodGear") else ""),
            "logCondition": "",
            "commandText": "run",
            "commandCondition": "",
            "logFile": "",
            "fastResume": True,
            "silent": False,
        })
    save(db, obj)
    print("wrote", len(bps), "bps ->", db)


if __name__ == "__main__":
    main()
