program rphost;
{ T7.0 同工具链 harness：一份 FPC 2.2.4 exe 对一份 FPC 2.2.4 DLL，
   测跨模块 GetMem/FreeMem、ReAllocMem、异常 unwind、共享 MemoryManager。
   判据：PASS=无崩溃且不变量成立；FAIL 打印反例；异常模式若进程直接退出即"未捕获"。 }
{$mode delphi}

uses
  SysUtils, Windows;

type
  TNoArg = procedure; stdcall;
  TAlloc = function(n: LongInt): Pointer; stdcall;
  TFree = procedure(p: Pointer); stdcall;
  TRealloc = function(p: Pointer; n: LongInt): Pointer; stdcall;
  TMemSize = function(p: Pointer): LongInt; stdcall;
  TFill = procedure(p: Pointer; n: LongInt; b: Byte); stdcall;
  TCheck = function(p: Pointer; n: LongInt; b: Byte): LongInt; stdcall;
  TIntNoArg = function: LongInt; stdcall;
  TRaise = procedure(msg: PChar); stdcall;
  TTryCb = function(cb: TNoArg): LongInt; stdcall;
  TPtrFn = function(p: Pointer): LongInt; stdcall;

var
  Dll: HMODULE;
  rp_alloc: TAlloc;
  rp_free: TFree;
  rp_realloc: TRealloc;
  rp_memsize: TMemSize;
  rp_fill: TFill;
  rp_check: TCheck;
  rp_internal_raise_catch: TIntNoArg;
  rp_raise: TRaise;
  rp_try_callback: TTryCb;
  rp_set_mm: TPtrFn;
  rp_get_mm: TPtrFn;

  Fails: LongInt;

procedure Need(ok: Boolean; const what: string);
begin
  if not ok then
  begin
    Writeln('FAIL load ', what);
    Halt(3);
  end;
end;

function P(const n: PChar): Pointer;
begin
  Result := GetProcAddress(Dll, n);
end;

procedure LoadProbe;
begin
  Dll := LoadLibrary('rplib.dll');
  Need(Dll <> 0, 'rplib.dll');
  @rp_alloc := P('rp_alloc');
  @rp_free := P('rp_free');
  @rp_realloc := P('rp_realloc');
  @rp_memsize := P('rp_memsize');
  @rp_fill := P('rp_fill');
  @rp_check := P('rp_check');
  @rp_internal_raise_catch := P('rp_internal_raise_catch');
  @rp_raise := P('rp_raise');
  @rp_try_callback := P('rp_try_callback');
  @rp_set_mm := P('rp_set_mm');
  @rp_get_mm := P('rp_get_mm');

  Need(Assigned(rp_alloc) and Assigned(rp_free) and Assigned(rp_realloc) and
       Assigned(rp_memsize) and Assigned(rp_fill) and Assigned(rp_check) and
       Assigned(rp_internal_raise_catch) and Assigned(rp_raise) and
       Assigned(rp_try_callback) and Assigned(rp_set_mm) and Assigned(rp_get_mm) and
       True,
       'exports');
end;

function SizeAt(i: LongInt): LongInt;
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

{ A: 宿主分配 -> DLL 释放（双方都是默认 RTL） }
function TestHostAllocDllFree(n: LongInt): Boolean;
var
  i: LongInt;
  p: Pointer;
  sz: LongInt;
begin
  Result := True;
  for i := 0 to n - 1 do
  begin
    if (i mod 5000) = 0 then
    begin
      Writeln('  A iter=', i);
      Flush(Output);
    end;
    sz := SizeAt(i);
    GetMem(p, sz);
    rp_fill(p, sz, Byte(i));
    if rp_check(p, sz, Byte(i)) <> -1 then
    begin
      Writeln('  mismatch before free i=', i);
      Result := False;
      Exit;
    end;
    rp_free(p);
  end;
end;

{ B: DLL 分配 -> 宿主释放 }
function TestDllAllocHostFree(n: LongInt): Boolean;
var
  i: LongInt;
  p: Pointer;
  sz: LongInt;
begin
  Result := True;
  for i := 0 to n - 1 do
  begin
    if (i mod 5000) = 0 then
    begin
      Writeln('  B iter=', i);
      Flush(Output);
    end;
    sz := SizeAt(i);
    p := rp_alloc(sz);
    rp_fill(p, sz, Byte(i));
    if rp_check(p, sz, Byte(i)) <> -1 then
    begin
      Writeln('  mismatch before free i=', i);
      Result := False;
      Exit;
    end;
    FreeMem(p);
  end;
end;

{ C: 交叉 ReAllocMem：宿主分配 -> DLL 改大小 -> 宿主释放，内容必须逐字节保住 }
function TestCrossRealloc(n: LongInt): Boolean;
var
  i: LongInt;
  p: Pointer;
  q: Pointer;
  a, b: LongInt;
begin
  Result := True;
  for i := 0 to n - 1 do
  begin
    a := 16 + (i mod 97);
    b := 1000 + (i mod 397);
    GetMem(p, a);
    rp_fill(p, a, $A5);
    q := rp_realloc(p, b);
    if rp_check(q, a, $A5) <> -1 then
    begin
      Writeln('  content lost after dll realloc i=', i, ' a=', a, ' b=', b);
      Result := False;
      Exit;
    end;
    FreeMem(q);
  end;
  { 反向：DLL 分配 -> 宿主 ReAllocMem -> DLL 释放 }
  for i := 0 to n - 1 do
  begin
    a := 16 + (i mod 89);
    b := 800 + (i mod 233);
    p := rp_alloc(a);
    rp_fill(p, a, $5A);
    ReAllocMem(p, b);
    if rp_check(p, a, $5A) <> -1 then
    begin
      Writeln('  content lost after host realloc i=', i);
      Result := False;
      Exit;
    end;
    rp_free(p);
  end;
end;

type
  PPointerArr = ^TPointerArr;
  TPointerArr = array[0..8191] of Pointer;

function Eq(a, b: Pointer): Boolean;
begin
  Result := a = b;
end;

function Contains(arr: PPointerArr; n: LongInt; p: Pointer): Boolean;
var
  i: LongInt;
begin
  Result := False;
  for i := 0 to n - 1 do
    if arr^[i] = p then
    begin
      Result := True;
      Exit;
    end;
end;

{ 分块释放不变量：一个 32KB 固定块 chunk 装 409 个 64B 块。
   control=true：全部释放/再分配都在宿主一侧（对照，必须 0 重复）。
   control=false：偶数块在宿主释放、奇数块在 DLL 释放，然后两侧同时再分配。
   判据：两侧同时持有的指针集合交集必须为空（重复地址 = 同一块内存双所有权）。 }
function TestSplit(control: Boolean): Boolean;
const
  K = 409;
  NH = 200;
  ND = 210;
var
  blocks: array[0..K - 1] of Pointer;
  hostLive: array[0..NH - 1] of Pointer;
  dllLive: array[0..ND - 1] of Pointer;
  i: LongInt;
  dups: LongInt;
begin
  Result := True;
  for i := 0 to K - 1 do
    GetMem(blocks[i], 64);
  for i := 0 to K - 1 do
    rp_fill(blocks[i], 64, Byte(i));
  for i := 0 to K - 1 do
    if (i mod 2) = 0 then
      FreeMem(blocks[i])
    else if control then
      FreeMem(blocks[i])
    else
      rp_free(blocks[i]);
  { control: 两侧都从宿主 heap 取；cross: DLL 先耗尽自己的 freelist 并复用 chunk }
  if control then
  begin
    for i := 0 to ND - 1 do
      GetMem(dllLive[i], 64);   { 名字沿用作"第二组"，其实仍是宿主 }
  end
  else
  begin
    for i := 0 to ND - 1 do
      dllLive[i] := rp_alloc(64);
  end;
  for i := 0 to NH - 1 do
    GetMem(hostLive[i], 64);
  { 写标记：DLL 侧写 0xD1，宿主侧写 0xE1 }
  for i := 0 to ND - 1 do
    rp_fill(dllLive[i], 64, $D1);
  for i := 0 to NH - 1 do
    rp_fill(hostLive[i], 64, $E1);
  dups := 0;
  for i := 0 to ND - 1 do
    if Contains(PPointerArr(@hostLive), NH, dllLive[i]) then
    begin
      Inc(dups);
      if dups <= 5 then
        Writeln('  DUP addr=', PtrUInt(dllLive[i]));
    end;
  Writeln('  split control=', control, ' dll_live=', ND, ' host_live=', NH,
          ' dups=', dups);
  Result := dups = 0;
  { 收尾（可能已经在重复块上，保持顺序：先宿主后 DLL） }
  for i := 0 to NH - 1 do
    FreeMem(hostLive[i]);
  for i := 0 to ND - 1 do
    rp_free(dllLive[i]);
end;

{ chunk 立即归还测试：MaxKeptOSChunks=4。
  1) 先让 DLL 同时持有 6 个尺寸类的整块 chunk，再逐个整块释放：
     count 到 4 后，后两个走 append_to_oslist 的 "count>=4 => SysOSFree" 分支
     => 之后 DLL 的 freeoslist 恒为 4。
  2) 共享 chunk 由宿主（A）分配一个尺寸类（不进 DLL 的 oslist），DLL（B）释放奇数块、
     宿主保留偶数块在宿主 freelist。used 归零时由 B 调 append_to_oslist，
     count>=4 => 立即 SysOSFree，宿主的 freelist 指针悬垂。
  判据：HeapSize(base) 释放前=32768、释放后=$FFFFFFFF（chunk 确实还给进程堆）；
       control=TRUE（全由 DLL 释放）时宿主无悬垂块；control=FALSE 时宿主
       140 个空闲块仍落在已释放的 chunk 内 => FAIL = 双所有权悬垂。 }
function TestRelease(control: Boolean): Boolean;
const
  GROOM: array[0..5] of LongInt = (20, 33, 49, 65, 81, 97);
  SHARED = 113;   { chunksize 128：32676/128 => 256 块/chunk }
  K = 240;
var
  blocks: array[0..K - 1] of Pointer;
  grp: array[0..5, 0..399] of Pointer;
  base: Pointer;
  i, c, j, groomed: LongInt;
  inside: LongInt;
  hp: THandle;
  hs_before, hs_after: PtrUInt;
begin
  hp := GetProcessHeap();
  { 1) 6 个类同时持有，再逐个整块释放 }
  groomed := 0;
  for c := 0 to 5 do
    for i := 0 to 399 do
      grp[c, i] := rp_alloc(GROOM[c]);
  for c := 0 to 5 do
  begin
    for i := 0 to 399 do
      rp_free(grp[c, i]);
    Inc(groomed);
  end;
  { 2) 共享 chunk：宿主分配，偶数块留宿主 freelist，奇数块由 DLL 释放 }
  for i := 0 to K - 1 do
    GetMem(blocks[i], SHARED);
  base := Pointer(PtrUInt(blocks[0]) - 16);
  hs_before := HeapSize(hp, 0, base);
  for i := 0 to K - 1 do
    if control then
      rp_free(blocks[i])
    else if (i mod 2) = 0 then
      FreeMem(blocks[i])
    else
      rp_free(blocks[i]);
  hs_after := HeapSize(hp, 0, base);
  { 3) 悬垂检查：宿主释放、未再分配的偶数块仍指向这个 chunk 的范围 }
  inside := 0;
  if not control then
    for i := 0 to (K div 2) - 1 do
      if (PtrUInt(blocks[i * 2]) >= PtrUInt(base)) and
         (PtrUInt(blocks[i * 2]) < PtrUInt(base) + 32768) then
        Inc(inside);
  Writeln('  release control=', control, ' chunk=', PtrUInt(base),
          ' heapsize_before=', hs_before, ' heapsize_after=', hs_after,
          ' groomed=', groomed, ' host_free_in_chunk=', inside);
  if control then
    Result := (hs_before = 32768) and (hs_after = PtrUInt(-1))
  else
    Result := (hs_after <> PtrUInt(-1)) or (inside = 0);
end;

procedure ExeRaise; stdcall;
begin
  raise Exception.Create('exe-callback');
end;

function ExeRaiseCatch: LongInt;
begin
  Result := 0;
  try
    raise Exception.Create('exe-internal');
  except
    Result := 1;
  end;
end;

procedure UseHostMM;
var
  mm: TMemoryManager;
begin
  GetMemoryManager(mm);
  rp_set_mm(@mm);
end;

var
  mode: string;
  ok: Boolean;
begin
  if ParamCount < 1 then
  begin
    Writeln('usage: rphost <heap|realloc|split|splitctl|exc-internal|exc-dll-raise|exc-dll-catch|exe-internal|mm-heap|mm-realloc|mm-split>');
    Halt(2);
  end;
  mode := ParamStr(1);
  LoadProbe;
  if Copy(mode, 1, 3) = 'mm-' then
  begin
    UseHostMM;
    mode := Copy(mode, 4, Length(mode));
    Writeln('MM=host');
  end
  else
    Writeln('MM=dll-default');
  ok := True;
  if mode = 'heap' then
  begin
    ok := TestHostAllocDllFree(100000);
    Writeln('  A host->dll 100k: ', ok);
    ok := TestDllAllocHostFree(100000) and ok;
    Writeln('  B dll->host 100k: ', ok);
  end
  else if mode = 'heapa' then
  begin
    ok := TestHostAllocDllFree(100000);
    Writeln('  A host->dll 100k: ', ok);
  end
  else if mode = 'heapb' then
  begin
    ok := TestDllAllocHostFree(100000);
    Writeln('  B dll->host 100k: ', ok);
  end
  else if mode = 'realloc' then
  begin
    ok := TestCrossRealloc(20000);
    Writeln('  cross realloc 2x20k: ', ok);
  end
  else if mode = 'split' then
    ok := TestSplit(False)
  else if mode = 'splitctl' then
    ok := TestSplit(True)
  else if mode = 'release' then
    ok := TestRelease(False)
  else if mode = 'releasectl' then
    ok := TestRelease(True)
  else if mode = 'exc-dll-raise-nocatch' then
  begin
    rp_raise('from-dll-nocatch');
    Writeln('  rp_raise returned (no catch)');
    ok := False;
  end
  else if mode = 'exc-internal' then
  begin
    Writeln('  dll internal catch=', rp_internal_raise_catch);
    Writeln('  exe internal catch=', ExeRaiseCatch);
    ok := (rp_internal_raise_catch = 1) and (ExeRaiseCatch = 1);
  end
  else if mode = 'exc-dll-raise' then
  begin
    try
      rp_raise('from-dll');
      Writeln('  CAUGHT by exe');
    except
      Writeln('  CAUGHT by exe (except)');
    end;
    { 到得了这里才是被宿主捕获 }
    Writeln('  dll raise returned normally');
    ok := False;
  end
  else if mode = 'exc-dll-raise-on' then
  begin
    try
      rp_raise('from-dll-on');
      Writeln('  no exception');
    except
      on E: Exception do
        Writeln('  on Exception:', E.Message);
    end;
    Writeln('  after on-handler');
    ok := False;
  end
  else if mode = 'exc-dll-raise-nested' then
  begin
    try
      try
        rp_raise('from-dll-nested');
      except
        Writeln('  INNER except ran');
      end;
    except
      Writeln('  OUTER except ran');
    end;
    Writeln('  after nested');
    ok := False;
  end
  else if mode = 'exc-dll-catch' then
  begin
    Writeln('  dll try around exe callback => ', rp_try_callback(@ExeRaise));
    Writeln('  dll callback catch returned normally');
    ok := False;
  end
  else if mode = 'exe-internal' then
  begin
    Writeln('  exe internal catch=', ExeRaiseCatch);
    ok := ExeRaiseCatch = 1;
  end
  else
  begin
    Writeln('unknown mode ', mode);
    Halt(2);
  end;
  if ok then
  begin
    Writeln('RESULT PASS');
    Halt(0);
  end
  else
  begin
    Writeln('RESULT FAIL');
    Halt(1);
  end;
end.
