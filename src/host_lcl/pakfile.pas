unit PakFile;
{$mode objfpc}{$H+}
// pak v0.2 只读解析（宿主侧 Pascal 实现）：格式与 src/host/pak.cpp、
// tools/pak.py 同源（F05/F17）。
//   偏移 0   : u32 toc_size = 24 * (count + 1)
//   偏移 4   : char magic[25] = "[Pak Header Info Ver 0.2]"
//   偏移 29  : count × rec{ u8 namelen; char name[namelen]; pad; u32 off; u32 size }
//   最后一条 rec 是尾部附加文件（lvl_info.lvl）
//   偏移 29 + toc_size : payload，条目偏移相对这里
interface
uses Classes, SysUtils;

type
  TPakEntry = record
    Name: string;
    Offset: Cardinal;
    Size: Cardinal;
  end;

  TPakFile = class
  private
    FData: TMemoryStream;
    FBase: Cardinal;
    FEntries: array of TPakEntry;
    FTrailer: TPakEntry;
    function Find(const Name: string): Integer;
  public
    constructor Create;
    destructor Destroy; override;
    function Open(const Path: string): Boolean;
    function Read(const Name: string; out Stream: TMemoryStream): Boolean;
    property Trailer: TPakEntry read FTrailer;
  end;

implementation

const
  kMagic = '[Pak Header Info Ver 0.2]';
  kHead = 4 + 25;   // 29
  kRec = 24;

function LE32(p: PByte; off: Cardinal): Cardinal;
begin
  Result := Cardinal(p[off]) or (Cardinal(p[off + 1]) shl 8) or
    (Cardinal(p[off + 2]) shl 16) or (Cardinal(p[off + 3]) shl 24);
end;

constructor TPakFile.Create;
begin
  inherited Create;
  FData := nil;
end;

destructor TPakFile.Destroy;
begin
  FData.Free;
  inherited Destroy;
end;

function TPakFile.Find(const Name: string): Integer;
var
  i: Integer;
begin
  for i := 0 to High(FEntries) do
    if CompareText(FEntries[i].Name, Name) = 0 then
      Exit(i);
  if (FTrailer.Name <> '') and (CompareText(FTrailer.Name, Name) = 0) then
    Exit(Length(FEntries));
  Result := -1;
end;

function TPakFile.Open(const Path: string): Boolean;
var
  p: PByte;
  toc, cnt, i, namelen: Cardinal;
  q: PByte;
  e: TPakEntry;
  total: Cardinal;
begin
  Result := False;
  FreeAndNil(FData);
  SetLength(FEntries, 0);
  FTrailer.Name := '';
  if not FileExists(Path) then Exit;
  FData := TMemoryStream.Create;
  try
    FData.LoadFromFile(Path);
  except
    FreeAndNil(FData);
    Exit;
  end;
  if FData.Size < kHead + kRec then Exit;
  p := PByte(FData.Memory);
  if not CompareMem(p + 4, @kMagic[1], Length(kMagic)) then Exit;
  toc := LE32(p, 0);
  if (toc < kRec) or ((toc mod kRec) <> 0) then Exit;
  if Cardinal(kHead) + toc > Cardinal(FData.Size) then Exit;
  cnt := toc div kRec - 1;
  SetLength(FEntries, cnt);
  for i := 0 to cnt - 1 do
  begin
    q := p + kHead + i * kRec;
    namelen := q^;
    if (namelen = 0) or (namelen > 200) then Exit;
    SetLength(e.Name, namelen);
    Move((q + 1)^, e.Name[1], namelen);
    e.Offset := LE32(q, 16);
    e.Size := LE32(q, 20);
    FEntries[i] := e;
  end;
  // 尾部附加文件（lvl_info.lvl）：紧随最后一条普通记录
  q := p + kHead + cnt * kRec;
  namelen := q^;
  if namelen > 0 then
  begin
    SetLength(FTrailer.Name, namelen);
    Move((q + 1)^, FTrailer.Name[1], namelen);
    FTrailer.Offset := LE32(q, 16);
    FTrailer.Size := LE32(q, 20);
  end;
  FBase := kHead + toc;
  total := FBase;
  for i := 0 to High(FEntries) do
    if Cardinal(FEntries[i].Offset) + FEntries[i].Size > Cardinal(FData.Size) - total then
      Exit;
  if (FTrailer.Name <> '') and
     (Cardinal(FTrailer.Offset) + FTrailer.Size > Cardinal(FData.Size) - total) then
    Exit;
  Result := True;
end;

function TPakFile.Read(const Name: string; out Stream: TMemoryStream): Boolean;
var
  i: Integer;
  e: TPakEntry;
  p: PByte;
begin
  Stream := nil;
  i := Find(Name);
  if i < 0 then Exit(False);
  if i = Length(FEntries) then e := FTrailer else e := FEntries[i];
  p := PByte(FData.Memory) + FBase + e.Offset;
  Stream := TMemoryStream.Create;
  if e.Size > 0 then
    Stream.WriteBuffer(p^, e.Size);
  Stream.Position := 0;
  Result := True;
end;

end.
