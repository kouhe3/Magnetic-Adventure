library rplib;
{ T7.0 探针 DLL：暴露 FPC 2.2.4 的一份独立 RTL（自己的 heap / 自己的异常链）。
  所有导出 stdcall，供 exe harness 或（经 b2 代理加载时）C 侧调用。
  判据与用法见 tools/rtlprobe_build.py 头部。 }
{$mode delphi}

uses
  SysUtils, Windows;

type
  TNoArg = procedure; stdcall;

function rp_alloc(n: LongInt): Pointer; stdcall;
begin
  GetMem(Result, n);
end;

procedure rp_free(p: Pointer); stdcall;
begin
  FreeMem(p);
end;

function rp_realloc(p: Pointer; n: LongInt): Pointer; stdcall;
begin
  ReAllocMem(p, n);
  Result := p;
end;

function rp_memsize(p: Pointer): LongInt; stdcall;
begin
  Result := MemSize(p);
end;

procedure rp_fill(p: Pointer; n: LongInt; b: Byte); stdcall;
begin
  FillChar(p^, n, b);
end;

function rp_check(p: Pointer; n: LongInt; b: Byte): LongInt; stdcall;
var
  i: LongInt;
  q: PByteArray;
begin
  Result := -1;
  q := PByteArray(p);
  for i := 0 to n - 1 do
    if q[i] <> b then
    begin
      Result := i;
      Exit;
    end;
end;

{ 对照：DLL 自己的 try/except 在同一模块内必须成立 }
function rp_internal_raise_catch: LongInt; stdcall;
begin
  Result := 0;
  try
    raise Exception.Create('rp-internal');
  except
    Result := 1;
  end;
end;

{ 跨模块 A 方向：DLL 抛，宿主 catch }
procedure rp_raise(msg: PChar); stdcall;
begin
  raise Exception.Create(msg);
end;

{ 跨模块 B 方向：宿主回调里抛，DLL catch }
function rp_try_callback(cb: TNoArg): LongInt; stdcall;
begin
  Result := 0;
  try
    cb();
  except
    Result := 1;
  end;
end;


{ 装宿主的内存管理器（T7.2 候选方案）：之后 DLL 的 GetMem/FreeMem 都走宿主 heap }
function rp_set_mm(mm: Pointer): LongInt; stdcall;
begin
  SetMemoryManager(PMemoryManager(mm)^);
  Result := 1;
end;

function rp_get_mm(mm: Pointer): LongInt; stdcall;
begin
  GetMemoryManager(PMemoryManager(mm)^);
  Result := 1;
end;

{ ================= 真宿主探针（game.exe 内运行） =================
  在 b2 代理的线程里调用；game.exe 无 ASLR，RVA 固定（F234）。
  RVA 来自 code_match funcs：system.o 对 game.exe 的逐函数 sim 0.96-1.00。 }
const
  RVA_SYSGETMEM        = $de30;
  RVA_SYSFREEMEM       = $df70;
  RVA_SYSFREEMEMSIZE   = $dfc0;
  RVA_SYSMEMSIZE       = $e000;
  RVA_SYSALLOCMEM      = $e020;
  RVA_SYSREALLOCMEM    = $e150;
  RVA_SYSGETHEAPSTATUS = $d5b0;
  RVA_RAISEEXCEPTION   = $b7c0;
  RVA_MEMMGR           = $1d5c50;  { host .data: TMemoryManager 记录 }
  RVA_MUTEXMGR         = $1d5c80;  { host .data: TMemoryMutexManager 记录 }

type
  THostGetMem = function(size: PtrInt): Pointer;
  THostFreeMem = function(p: Pointer): PtrInt;
  THostFreeMemSize = function(p: Pointer; size: PtrInt): PtrInt;
  THostAllocMem = function(size: PtrInt): Pointer;
  THostReAllocMem = function(var p: Pointer; size: PtrInt): Pointer;
  THostMemSize = function(p: Pointer): PtrInt;
  THostGetHeapStatus = function: THeapStatus;
  THostRaise = function(obj: TObject; anaddr, aframe: Pointer): TObject;

var
  g_log: THandle = THandle(-1);
  h_getmem: THostGetMem;
  h_freemem: THostFreeMem;
  h_freememsize: THostFreeMemSize;
  h_allocmem: THostAllocMem;
  h_reallocmem: THostReAllocMem;
  h_memsize: THostMemSize;
  h_getheapstatus: THostGetHeapStatus;
  h_raise: THostRaise;

procedure HLog(const s: string);
var
  n: DWORD;
begin
  if g_log = THandle(-1) then Exit;
  if Length(s) = 0 then Exit;
  WriteFile(g_log, s[1], Length(s), n, nil);
  FlushFileBuffers(g_log);
end;

function SizeAt2(i: LongInt): LongInt;
begin
  case i mod 6 of
    0: Result := 8;
    1: Result := 64;
    2: Result := 300;
    3: Result := 520;
    4: Result := 4096;
  else
    Result := 65536;
  end;
end;

{ A: 宿主 SysGetMem 分配 -> 我们的 FreeMem 释放 }
function HostAllocOurFree(n: LongInt): Boolean;
var
  i, sz: LongInt;
  p: Pointer;
begin
  Result := True;
  for i := 0 to n - 1 do
  begin
    if (i mod 5000) = 0 then HLog('A iter=' + IntToStr(i) + #13#10);
    sz := SizeAt2(i);
    p := h_getmem(sz);
    if p = nil then
    begin
      HLog('A nil at ' + IntToStr(i) + #13#10);
      Result := False;
      Exit;
    end;
    FillChar(p^, sz, Byte(i));
    FreeMem(p);
  end;
end;

{ B: 我们 GetMem 分配 -> 宿主 SysFreeMem 释放 }
function OurAllocHostFree(n: LongInt): Boolean;
var
  i, sz: LongInt;
  p: Pointer;
begin
  Result := True;
  for i := 0 to n - 1 do
  begin
    if (i mod 5000) = 0 then HLog('B iter=' + IntToStr(i) + #13#10);
    sz := SizeAt2(i);
    GetMem(p, sz);
    FillChar(p^, sz, Byte(i));
    h_freemem(p);
  end;
end;

{ C: 宿主分配 -> 我们 ReAllocMem -> 宿主释放（内容必须保住） }
function CrossRealloc(n: LongInt): Boolean;
var
  i, a, b: LongInt;
  p, q: Pointer;
  bad: LongInt;
begin
  Result := True;
  for i := 0 to n - 1 do
  begin
    if (i mod 1000) = 0 then HLog('C iter=' + IntToStr(i) + #13#10);
    a := 16 + (i mod 97);
    b := 1000 + (i mod 397);
    p := h_getmem(a);
    FillChar(p^, a, $A5);
    q := p;
    ReAllocMem(q, b);
    bad := -1;
    if q <> nil then
      bad := rp_check(q, a, $A5);
    if bad <> -1 then
    begin
      HLog('C content lost i=' + IntToStr(i) + #13#10);
      Result := False;
      Exit;
    end;
    h_freemem(q);
  end;
end;

{ D: chunk 立即归还 + 宿主 freelist 悬垂（与同工具链 harness 同一设计）。
  真宿主里同类 chunk 可能已有别的块：从块头的 offset 高位反推 chunk 基址，
  按基址分组，只对"块最多"的那个 chunk 做 偶数(宿主释放)/奇数(我们释放) 的交叉。 }
function ChunkBaseOf(p: Pointer): Pointer;
var
  hdr: PtrUInt;
begin
  hdr := PtrUInt(PLongInt(PtrUInt(p) - 4)^);
  Result := Pointer((PtrUInt(p) - 4) - (hdr shr 16));
end;

function ReleaseTest(control: Boolean): Boolean;
const
  GROOM: array[0..5] of LongInt = (20, 33, 49, 65, 81, 97);
  SHARED = 113;
  K = 240;
var
  blocks: array[0..K - 1] of Pointer;
  grp: array[0..5, 0..399] of Pointer;
  bases: array[0..K - 1] of Pointer;
  counts: array[0..K - 1] of LongInt;
  base: Pointer;
  hp: THandle;
  i, c, j, nbase, idx, chosen, kk, inside: LongInt;
  hs_before, hs_after: PtrUInt;
begin
  hp := GetProcessHeap();
  for c := 0 to 5 do
    for i := 0 to 399 do
      grp[c, i] := rp_alloc(GROOM[c]);
  for c := 0 to 5 do
    for i := 0 to 399 do
      rp_free(grp[c, i]);
  for i := 0 to K - 1 do
    blocks[i] := h_getmem(SHARED);
  nbase := 0;
  for i := 0 to K - 1 do
  begin
    base := ChunkBaseOf(blocks[i]);
    idx := -1;
    for j := 0 to nbase - 1 do
      if bases[j] = base then
      begin
        idx := j;
        Break;
      end;
    if idx < 0 then
    begin
      bases[nbase] := base;
      counts[nbase] := 0;
      idx := nbase;
      Inc(nbase);
    end;
    Inc(counts[idx]);
  end;
  chosen := 0;
  for j := 1 to nbase - 1 do
    if counts[j] > counts[chosen] then chosen := j;
  base := bases[chosen];
  hs_before := HeapSize(hp, 0, base);
  kk := 0;
  for i := 0 to K - 1 do
    if ChunkBaseOf(blocks[i]) = base then
    begin
      if control then
        rp_free(blocks[i])
      else if (kk mod 2) = 0 then
        h_freemem(blocks[i])
      else
        rp_free(blocks[i]);
      Inc(kk);
    end;
  hs_after := HeapSize(hp, 0, base);
  inside := 0;
  if not control then
  begin
    kk := 0;
    for i := 0 to K - 1 do
      if ChunkBaseOf(blocks[i]) = base then
      begin
        if (kk mod 2) = 0 then
          if (PtrUInt(blocks[i]) >= PtrUInt(base)) and
             (PtrUInt(blocks[i]) < PtrUInt(base) + 32768) then
            Inc(inside);
        Inc(kk);
      end;
  end;
  HLog('D control=' + BoolToStr(control, True) +
       ' chunks=' + IntToStr(nbase) +
       ' chosen_blocks=' + IntToStr(counts[chosen]) +
       ' base=' + IntToHex(PtrUInt(base), 8) +
       ' before=' + IntToHex(hs_before, 8) +
       ' after=' + IntToHex(hs_after, 8) +
       ' host_free_in_chunk=' + IntToStr(inside) + #13#10);
  if control then
    Result := (hs_before = 32768) and (hs_after = PtrUInt(-1))
  else
    Result := (hs_after <> PtrUInt(-1)) or (inside = 0);
end;


procedure InstallHostMMRecord(base: Pointer);
var
  mm: TMemoryManager;
  mmu: TMemoryMutexManager;
begin
  { 同一把锁：否则我们的 SysGetMem 调用与宿主主线程的 GetMem 互不排斥 }
  Move(Pointer(PtrUInt(base) + RVA_MUTEXMGR)^, mmu, SizeOf(mmu));
  SetMemoryMutexManager(mmu);
  IsMultiThread := True;
  Move(Pointer(PtrUInt(base) + RVA_MEMMGR)^, mm, SizeOf(mm));
  HLog('MM record needlock=' + IntToStr(Ord(mm.NeedLock)) +
       ' getmem=' + IntToHex(PDWord(PtrUInt(base) + RVA_MEMMGR + 4)^, 8) +
       ' freemem=' + IntToHex(PDWord(PtrUInt(base) + RVA_MEMMGR + 8)^, 8) +
       ' realloc=' + IntToHex(PDWord(PtrUInt(base) + RVA_MEMMGR + 20)^, 8) + #13#10);
  SetMemoryManager(mm);
end;

procedure InstallHostMM;
var
  mm: TMemoryManager;
begin
  FillChar(mm, SizeOf(mm), 0);
  mm.NeedLock := False;
  mm.GetMem := h_getmem;
  mm.FreeMem := h_freemem;
  mm.FreeMemSize := h_freememsize;
  mm.AllocMem := h_allocmem;
  mm.ReAllocMem := h_reallocmem;
  mm.MemSize := h_memsize;
  mm.GetHeapStatus := h_getheapstatus;
  mm.GetFPCHeapStatus := nil;
  SetMemoryManager(mm);
  HLog('MM=host installed'#13#10);
end;

procedure ExceptionTest(withmm: Boolean);
var
  e: TObject;
begin
  if withmm then InstallHostMM;
  HLog('exc internal=' + IntToStr(rp_internal_raise_catch) + #13#10);
  HLog('exc before host raise'#13#10);
  try
    e := Exception.Create('from-dll');
    h_raise(e, nil, nil);
    HLog('exc host raise returned'#13#10);
  except
    HLog('exc CAUGHT by dll'#13#10);
  end;
end;


{ 纯宿主分配/释放（不跨模块）：用来区分"共享 MM 失败"与"两个线程抢堆" }
function HostOnly(n: LongInt): Boolean;
var
  i, sz: LongInt;
  p: Pointer;
begin
  Result := True;
  for i := 0 to n - 1 do
  begin
    if (i mod 5000) = 0 then HLog('H iter=' + IntToStr(i) + #13#10);
    sz := SizeAt2(i);
    p := h_getmem(sz);
    if p = nil then
    begin
      Result := False;
      Exit;
    end;
    FillChar(p^, sz, Byte(i));
    h_freemem(p);
  end;
end;

procedure rp_host_entry; stdcall;
var
  base: Pointer;
  mode: array[0..63] of Char;
  path: array[0..1023] of Char;
  ok: Boolean;
begin
  GetEnvironmentVariableA('B2RTLPROBE_MODE', mode, SizeOf(mode));
  path[0] := #0;
  GetEnvironmentVariableA('B2RTLPROBE_LOG', path, SizeOf(path));
  if path[0] <> #0 then
    g_log := CreateFileA(path, GENERIC_WRITE, FILE_SHARE_READ, nil,
                         CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, 0);
  HLog('rp_host_entry mode=' + string(PChar(@mode[0])) + #13#10);
  base := Pointer(PtrUInt(GetModuleHandleA(nil)));
  HLog('base=' + IntToHex(PtrUInt(base), 8) + #13#10);
  h_getmem := THostGetMem(PtrUInt(base) + RVA_SYSGETMEM);
  h_freemem := THostFreeMem(PtrUInt(base) + RVA_SYSFREEMEM);
  h_freememsize := THostFreeMemSize(PtrUInt(base) + RVA_SYSFREEMEMSIZE);
  h_allocmem := THostAllocMem(PtrUInt(base) + RVA_SYSALLOCMEM);
  h_reallocmem := THostReAllocMem(PtrUInt(base) + RVA_SYSREALLOCMEM);
  h_memsize := THostMemSize(PtrUInt(base) + RVA_SYSMEMSIZE);
  h_getheapstatus := THostGetHeapStatus(PtrUInt(base) + RVA_SYSGETHEAPSTATUS);
  h_raise := THostRaise(PtrUInt(base) + RVA_RAISEEXCEPTION);
  if string(PChar(@mode[0])) = 'verify' then
  begin
    ok := True;
    HLog('verify getmem64=' + IntToHex(PtrUInt(h_getmem(64)), 8) + #13#10);
    HLog('done'#13#10);
  end
  else if string(PChar(@mode[0])) = 'heap' then
  begin
    HLog('A start'#13#10);
    ok := HostAllocOurFree(100000);
    HLog('A ok=' + BoolToStr(ok, True) + #13#10);
    HLog('B start'#13#10);
    ok := OurAllocHostFree(100000) and ok;
    HLog('B ok=' + BoolToStr(ok, True) + #13#10);
  end
  else if string(PChar(@mode[0])) = 'hostonly' then
  begin
    ok := HostOnly(100000);
    HLog('H ok=' + BoolToStr(ok, True) + #13#10);
  end
  else if string(PChar(@mode[0])) = 'heapa' then
  begin
    HLog('A start'#13#10);
    ok := HostAllocOurFree(100000);
    HLog('A ok=' + BoolToStr(ok, True) + #13#10);
  end
  else if string(PChar(@mode[0])) = 'heapb' then
  begin
    HLog('B start'#13#10);
    ok := OurAllocHostFree(100000);
    HLog('B ok=' + BoolToStr(ok, True) + #13#10);
  end
  else if string(PChar(@mode[0])) = 'realloc' then
  begin
    ok := CrossRealloc(20000);
    HLog('C ok=' + BoolToStr(ok, True) + #13#10);
  end
  else if string(PChar(@mode[0])) = 'release' then
  begin
    ok := ReleaseTest(False);
    HLog('D ok=' + BoolToStr(ok, True) + #13#10);
  end
  else if string(PChar(@mode[0])) = 'exc' then
    ExceptionTest(False)
  else if (string(PChar(@mode[0])) = 'mmrec') or (string(PChar(@mode[0])) = 'mm') then
  begin
    if string(PChar(@mode[0])) = 'mmrec' then
      InstallHostMMRecord(base)
    else
      InstallHostMM;
    ok := HostAllocOurFree(100000);
    HLog('A(mm) ok=' + BoolToStr(ok, True) + #13#10);
    ok := OurAllocHostFree(100000) and ok;
    HLog('B(mm) ok=' + BoolToStr(ok, True) + #13#10);
    ok := CrossRealloc(20000) and ok;
    HLog('C(mm) ok=' + BoolToStr(ok, True) + #13#10);
    ok := ReleaseTest(False) and ok;
    HLog('D(mm) ok=' + BoolToStr(ok, True) + #13#10);
  end
  else if string(PChar(@mode[0])) = 'mmexc' then
    ExceptionTest(True);
  HLog('ENTRY DONE'#13#10);
end;

exports
  rp_alloc, rp_free, rp_realloc, rp_memsize, rp_fill, rp_check,
  rp_internal_raise_catch, rp_raise, rp_try_callback,
  rp_set_mm, rp_get_mm, rp_host_entry;

begin
end.
