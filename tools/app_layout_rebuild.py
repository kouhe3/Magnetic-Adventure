#!/usr/bin/env python3
"""真实布局重建 + 字节冲撞/偏移负例（T7.2c 判据）。

用法：
  python tools/app_layout_rebuild.py            # 生成源码 → FPC 2.2.4 编译 → 比对 → PASS
  python tools/app_layout_rebuild.py --keep     # 保留中间产物（默认保留在 work/pilot/rebuild/）
  FPC=<path> python tools/app_layout_rebuild.py # 换编译器

判据（打印 PASS=…）：
  real_masked=3/3   三个函数（0x57B4B0 / 0x5716A0 / 0x569BD0）的候选体与零售仅重定位字节不同
  reloc_class=3/3   重定位符号包含我们声明的类名（TPlayerObject / TList）
  retail_class=3/3  零售侧：0x58E8A0 的静态类=TPlayerObject（F320 映射）；
                    0x42B5E0 不在应用层清单，用 RTL 形状 `mov eax,[eax+4]; mov eax,[eax+8]; ret` 判 TList.GetCount
  neg_diff=2/2      字段偏移 +4 的负例在 disp 字节（+0x11）报差
  collision=2/2     LongInt↔TList 返回、typed↔Pointer+cast 两组声明字节逐位相同
  A_vs_retail       0x571EC0 的 23 字节与 "LongInt getter" 候选逐位相同
输出 PASS=all 时退出码 0；否则 1。

输入：bin/gametop/game.exe（只读）；mapping/app-self-fixes.csv（类归属证据）；
      FPC 2.2.4 i386-win32（本机 `C:/lazarus/fpc/2.2.4/bin/i386-win32/fpc.exe`，可用 FPC 覆盖）。
输出：work/pilot/rebuild/{real_layout,real_layout_neg,real_layout_amb}.pas/.o、verdict.json。

覆盖边界：只覆盖这 3 个重建目标与 3 组对照；类声明用最小填充把字段放到实测偏移，
  方法名/字段名不可从字节恢复（桩名），所以“真实布局”只指偏移 + 字段类型证据链。
失效条件：零售 exe 或 FPC 版本/标志（-Mdelphi -O1 -g- -Xs- -Xm）变化后重跑；
  偏移或类型证据（F389/F392）更新后同步改下面的源码常量。
"""
from __future__ import annotations

import argparse
import json
import os
import struct
import subprocess
import sys
from pathlib import Path

import capstone

ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / "bin" / "gametop" / "game.exe"
OUT = ROOT / "work" / "pilot" / "rebuild"
DEFAULT_FPC = "C:/lazarus/fpc/2.2.4/bin/i386-win32/fpc.exe"

SRC_REAL = """unit real_layout;
interface
uses Classes;
type
  TPlayerObject = class
  private
    FPad: array[0..$53] of Byte;
  public
    procedure ReleaseTarget;
  end;
  TLevelObjects = class
  private
    FPad: array[0..$43] of Byte;   // +4 .. +0x47
    FPlayer: TPlayerObject;        // +0x48
  public
    procedure DoRelease;
  end;
  TLevelManager = class
  private
    FPad: array[0..$33] of Byte;   // +4 .. +0x37
    FList: TList;                  // +0x38
  public
    function GetListCount: LongInt;
  end;
  TArrowLine = class
  private
    FPad: array[0..$43] of Byte;   // +4 .. +0x47
    FList: TList;                  // +0x48
  public
    function GetListCount: LongInt;
  end;
implementation
procedure TPlayerObject.ReleaseTarget;
begin
end;
procedure TLevelObjects.DoRelease;
begin
  FPlayer.ReleaseTarget;
end;
function TLevelManager.GetListCount: LongInt;
begin
  Result := FList.Count;
end;
function TArrowLine.GetListCount: LongInt;
begin
  Result := FList.Count;
end;
end.
"""

SRC_NEG = """unit real_layout_neg;
interface
uses Classes;
type
  TPlayerObject = class
  public
    procedure ReleaseTarget;
  end;
  TLevelObjectsNeg = class
  private
    FPad: array[0..$3F] of Byte;   // +4 .. +0x43
    FPlayer: TPlayerObject;        // +0x44（错 4）
  public
    procedure DoRelease;
  end;
  TLevelManagerNeg = class
  private
    FPad: array[0..$2F] of Byte;   // +4 .. +0x33
    FList: TList;                  // +0x34（错 4）
  public
    function GetListCount: LongInt;
  end;
implementation
procedure TPlayerObject.ReleaseTarget;
begin
end;
procedure TLevelObjectsNeg.DoRelease;
begin
  FPlayer.ReleaseTarget;
end;
function TLevelManagerNeg.GetListCount: LongInt;
begin
  Result := FList.Count;
end;
end.
"""

SRC_AMB = """unit real_layout_amb;
interface
uses Classes;
type
  TLevelManagerA = class
  private
    FPad: array[0..$33] of Byte;
    FValue: LongInt;
  public
    function GetValue: LongInt;
  end;
  TLevelManagerB = class
  private
    FPad: array[0..$33] of Byte;
    FList: TList;
  public
    function GetList: TList;
  end;
  TCallableObject = class
  public
    procedure ReleaseTarget;
  end;
  TLevelObjectsTyped = class
  private
    FPad: array[0..$43] of Byte;
    FPlayer: TCallableObject;
  public
    procedure DoRelease;
  end;
  TLevelObjectsPointer = class
  private
    FPad: array[0..$43] of Byte;
    FPlayer: Pointer;
  public
    procedure DoRelease;
  end;
implementation
function TLevelManagerA.GetValue: LongInt;
begin
  Result := FValue;
end;
function TLevelManagerB.GetList: TList;
begin
  Result := FList;
end;
procedure TCallableObject.ReleaseTarget;
begin
end;
procedure TLevelObjectsTyped.DoRelease;
begin
  FPlayer.ReleaseTarget;
end;
procedure TLevelObjectsPointer.DoRelease;
begin
  TCallableObject(FPlayer).ReleaseTarget;
end;
end.
"""

TARGETS = [
    # (object, section prefix, retail rva, size, expected class, retail call target)
    ("real_layout", ".text.n_real_layout_tlevelobjects_$__dorelease", 0x57B4B0, 30, "TPlayerObject", 0x58E8A0),
    ("real_layout", ".text.n_real_layout_tlevelmanager_$__getlistcount$$longint", 0x5716A0, 36, "TList", 0x42B5E0),
    ("real_layout", ".text.n_real_layout_tarrowline_$__getlistcount$$longint", 0x569BD0, 36, "TList", 0x42B5E0),
]
# FPC 2.2.4 RTL TList.GetCount: mov eax,[eax+4] (FList) ; mov eax,[eax+8] (FCount) ; ret
TLIST_GETCOUNT = bytes.fromhex("8b40048b4008c3")


def retail_class(rva: int) -> str | None:
    import csv
    path = ROOT / "mapping" / "app-self-map.csv"
    for r in csv.DictReader(path.open(newline="", encoding="utf-8")):
        if int(r["rva"], 16) == rva:
            return r["self_class"] or None
    return None


def pe_text() -> tuple[bytes, int]:
    b = GAME.read_bytes()
    lf = struct.unpack_from("<I", b, 0x3C)[0]
    n = struct.unpack_from("<H", b, lf + 6)[0]
    opt = lf + 24
    off = opt + struct.unpack_from("<H", b, lf + 20)[0]
    for i in range(n):
        s = b[off + i * 40: off + (i + 1) * 40]
        name = s[:8].rstrip(b"\0").decode("latin1")
        vs, va, rs, ra = struct.unpack_from("<IIII", s, 8)
        if name == ".text":
            return b[ra:ra + rs], va + 0x400000
    raise SystemExit("no .text")


def coff(path: Path):
    b = path.read_bytes()
    machine, nsec, tds, ptrsym, nsym, optsz, chars = struct.unpack_from("<HHIIIHH", b, 0)
    stroff = ptrsym + nsym * 18

    def cstr(o: int) -> str:
        e = b.index(b"\0", o)
        return b[o:e].decode("latin1")

    syms = []
    for i in range(nsym):
        s = b[ptrsym + i * 18: ptrsym + (i + 1) * 18]
        if s[:4] == b"\0\0\0\0":
            name = cstr(stroff + struct.unpack_from("<I", s, 4)[0])
        else:
            name = s[:8].rstrip(b"\0").decode("latin1")
        syms.append(name)
    sections = {}
    off = 20 + optsz
    for i in range(nsec):
        s = b[off + i * 40: off + (i + 1) * 40]
        name = s[:8]
        if name.startswith(b"/"):
            name = cstr(stroff + int(name[1:].split(b"\0")[0], 10))
        else:
            name = name.rstrip(b"\0").decode("latin1")
        vs, va, rs, ra = struct.unpack_from("<IIII", s, 8)
        rp, lp, nr, nl = struct.unpack_from("<IIHH", s, 24)
        relocs = []
        for j in range(nr):
            r = b[rp + j * 10: rp + (j + 1) * 10]
            if len(r) < 10:
                break
            voff, symidx, rtyp = struct.unpack_from("<IIH", r, 0)
            relocs.append((voff, symidx, rtyp))
        sections[name] = (b[ra:ra + rs], va, relocs)
    return sections, syms


def build(fpc: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for stem, src in (("real_layout", SRC_REAL), ("real_layout_neg", SRC_NEG), ("real_layout_amb", SRC_AMB)):
        p = OUT / f"{stem}.pas"
        p.write_text(src, encoding="utf-8", newline="\r\n")
        r = subprocess.run([fpc, "-Mdelphi", "-O1", "-g-", "-Xs-", "-Xm", "-al",
                            f"-FE{OUT}", str(p)], capture_output=True, text=True)
        if r.returncode != 0:
            print(r.stdout[-2000:], r.stderr[-2000:])
            raise SystemExit(f"fpc failed for {stem}")


def sec(path: Path, prefix: str):
    sections, syms = coff(path)
    for n, (d, va, rel) in sections.items():
        if n.startswith(prefix):
            return d, rel, syms
    raise SystemExit("no section " + prefix)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--fpc", default=os.environ.get("FPC", DEFAULT_FPC))
    ap.add_argument("--keep", action="store_true", help="保留中间产物（默认已保留）")
    args = ap.parse_args()
    build(args.fpc)
    tb, tva = pe_text()
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    md.detail = True
    out = {"targets": [], "neg": [], "collision": []}

    n_masked = n_cls = n_retail = 0
    for stem, prefix, rva, size, expect, call_tgt in TARGETS:
        d, rel, syms = sec(OUT / f"{stem}.o", prefix)
        t = tb[rva - tva: rva - tva + size]
        c = d[:size]
        masks = set()
        for voff, symidx, rtyp in rel:
            if voff + 4 <= size:
                masks.update(range(voff, voff + 4))
        diffs = [i for i in range(min(len(t), len(c))) if i not in masks and t[i] != c[i]]
        rel_syms = [syms[i] for o, i, _ in rel if o < size]
        cls_ok = any(expect.upper() in s.upper() for s in rel_syms)
        rc = retail_class(call_tgt)
        if rc:
            retail_ok = rc.upper() == expect.upper()
            retail_note = rc
        else:
            retail_ok = call_tgt == 0x42B5E0 and tb[call_tgt - tva: call_tgt - tva + 7] == TLIST_GETCOUNT
            retail_note = "RTL-shape" if retail_ok else "?"
        n_masked += not diffs
        n_cls += cls_ok
        n_retail += retail_ok
        out["targets"].append({"rva": hex(rva), "size": size, "masked_equal": not diffs,
                               "first_diff": diffs[0] if diffs else None,
                               "relocs": rel_syms, "reloc_class_ok": cls_ok,
                               "retail_target": hex(call_tgt), "retail_class": retail_note,
                               "retail_ok": retail_ok})
        print(f"REAL {hex(rva)} masked_equal={not diffs} relocs={','.join(rel_syms) or '-'} "
              f"cls={cls_ok} retail={hex(call_tgt)}/{retail_note}/{retail_ok}")

    negs = []
    for prefix, rva, size in (
            (".text.n_real_layout_neg_tlevelobjectsneg_$__dorelease", 0x57B4B0, 30),
            (".text.n_real_layout_neg_tlevelmanagerneg_$__getlistcount$$longint", 0x5716A0, 36)):
        d, _, _ = sec(OUT / "real_layout_neg.o", prefix)
        t = tb[rva - tva: rva - tva + size]
        diffs = [i for i in range(min(len(t), len(d))) if t[i] != d[i]]
        ok = bool(diffs) and diffs[0] == 0x11
        negs.append(ok)
        out["neg"].append({"section": prefix, "first_diff": diffs[0] if diffs else None,
                           "target_byte": hex(t[diffs[0]]) if diffs else None,
                           "cand_byte": hex(d[diffs[0]]) if diffs else None, "ok": ok})
        print(f"NEG  {prefix.split('_$__')[-1]} first_diff={diffs[0] if diffs else None} ok={ok}")

    a, _, _ = sec(OUT / "real_layout_amb.o", ".text.n_real_layout_amb_tlevelmanagera_$__getvalue$$longint")
    b, _, _ = sec(OUT / "real_layout_amb.o", ".text.n_real_layout_amb_tlevelmanagerb_$__getlist$$tlist")
    ty, _, _ = sec(OUT / "real_layout_amb.o", ".text.n_real_layout_amb_tlevelobjectstyped_$__dorelease")
    pt, _, _ = sec(OUT / "real_layout_amb.o", ".text.n_real_layout_amb_tlevelobjectspointer_$__dorelease")
    eq_ab = a == b
    eq_tp = ty == pt
    eq_retail = a[:23] == tb[0x571EC0 - tva: 0x571EC0 - tva + 23]
    for name, eq, la, lb in (("LongInt vs TList", eq_ab, len(a), len(b)),
                             ("typed vs Pointer+cast", eq_tp, len(ty), len(pt)),
                             ("A vs retail 0x571EC0[0:23]", eq_retail, 23, 23)):
        out["collision"].append({"pair": name, "equal": eq, "len_a": la, "len_b": lb})
        print(f"COLL {name:<28} equal={eq} ({la}/{lb})")

    (OUT / "verdict.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    ok = n_masked == 3 and n_cls == 3 and n_retail == 3 and sum(negs) == 2 and eq_ab and eq_tp and eq_retail
    print("real_masked=%d/3 reloc_class=%d/3 retail_class=%d/3 neg_diff=%d/2 collision=%d/2 A_vs_retail=%s" % (
        n_masked, n_cls, n_retail, sum(negs), sum([eq_ab, eq_tp]), eq_retail))
    print("PASS=%s" % ("all" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
