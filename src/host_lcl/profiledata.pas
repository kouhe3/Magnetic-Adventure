unit ProfileData;
{$mode objfpc}{$H+}
// 玩家档案（%APPDATA%\Magnet's Story\hg_lmpgl.prf）只读解析（T6.4c-1）。
//
// 格式（F41）：UTF-16LE BOM + 每个 code unit 的低字节 XOR 0xB8，高字节恒 0；
// 正文是若干 <Player> 块，每块 `key = "value"`。
//
// 选择规则与 tools/profile.py:pick 对齐（F434 的 oracle）：
//   1. 只有一个 <Player> 块 -> 直接用；
//   2. 多个块 -> 取唯一 Active="1" 的块；
//   3. 多个块且没有唯一 Active -> 失败（不猜第一个）。
//
// 只读：本单元不写档案。HOST_PROFILE 未设时宿主不调用它（零行为）。

interface

type
  TProfileInfo = record
    Ok: Boolean;
    Error: string;
    Players: Integer;
    UserName: string;
    LastCompleteLevel: Integer;
    CompletedLevels: string;
    SoundsVolume: Integer;
    MusicVolume: Integer;
    FullScreen: Integer;
  end;

function DefaultProfilePath: string;
function ReadProfileFile(const Path: string; out Info: TProfileInfo): Boolean;

implementation

uses
  SysUtils, Classes, Windows;

type
  TPlayerBlock = record
    UserName: string;
    Active: Boolean;
    LastCompleteLevel: Integer;
    CompletedLevels: string;
    SoundsVolume: Integer;
    MusicVolume: Integer;
    FullScreen: Integer;
  end;

function DefaultProfilePath: string;
var
  buf: array[0..MAX_PATH - 1] of Char;
  n: DWORD;
begin
  n := GetEnvironmentVariable('APPDATA', @buf[0], MAX_PATH);
  if n > 0 then
    Result := IncludeTrailingPathDelimiter(buf) + 'Magnet''s Story' +
      PathDelim + 'hg_lmpgl.prf'
  else
    Result := '';
end;

function StripQuotes(const S: string): string;
var
  v: string;
begin
  v := Trim(S);
  if (Length(v) >= 2) and (v[1] = '"') and (v[Length(v)] = '"') then
    v := Copy(v, 2, Length(v) - 2);
  Result := v;
end;

// profile.py 的 decode()：BOM + 低字节 XOR 0xB8。
function DecodeProfile(const Raw: array of Byte; out Text: string;
  out Err: string): Boolean;
var
  i, n: Integer;
  u: Word;
begin
  Result := False;
  Text := '';
  Err := '';
  n := Length(Raw);
  if (n < 2) or (Raw[0] <> $FF) or (Raw[1] <> $FE) then
  begin
    Err := 'not UTF-16LE BOM';
    Exit;
  end;
  i := 2;
  while i + 1 < n do
  begin
    u := Raw[i] or (Raw[i + 1] shl 8);
    Text := Text + Chr((u and $FF) xor $B8);
    Inc(i, 2);
  end;
  Result := True;
end;

function ReadProfileFile(const Path: string; out Info: TProfileInfo): Boolean;
var
  fs: TFileStream;
  raw: array of Byte;
  size: Integer;
  text, err: string;
  sl: TStringList;
  i, j: Integer;
  line, key, val: string;
  inBlock: Boolean;
  blocks: array of TPlayerBlock;
  count, activeCount, activeIndex: Integer;
  cur: TPlayerBlock;
begin
  Result := False;
  Info.Ok := False;
  Info.Error := '';
  Info.Players := 0;
  Info.UserName := '';
  Info.LastCompleteLevel := -1;
  Info.CompletedLevels := '';
  Info.SoundsVolume := -1;
  Info.MusicVolume := -1;
  Info.FullScreen := -1;

  if not FileExists(Path) then
  begin
    Info.Error := 'missing file';
    Exit;
  end;

  fs := TFileStream.Create(Path, fmOpenRead or fmShareDenyWrite);
  try
    size := fs.Size;
    SetLength(raw, size);
    if size > 0 then
      fs.ReadBuffer(raw[0], size);
  finally
    fs.Free;
  end;

  if not DecodeProfile(raw, text, err) then
  begin
    Info.Error := err;
    Exit;
  end;

  sl := TStringList.Create;
  try
    sl.Text := text;
    SetLength(blocks, 0);
    count := 0;
    inBlock := False;
    for i := 0 to sl.Count - 1 do
    begin
      line := Trim(sl[i]);
      if CompareText(line, '<Player>') = 0 then
      begin
        inBlock := True;
        cur.UserName := '';
        cur.Active := False;
        cur.LastCompleteLevel := -1;
        cur.CompletedLevels := '';
        cur.SoundsVolume := -1;
        cur.MusicVolume := -1;
        cur.FullScreen := -1;
        Continue;
      end;
      if CompareText(line, '</Player>') = 0 then
      begin
        if inBlock then
        begin
          SetLength(blocks, count + 1);
          blocks[count] := cur;
          Inc(count);
        end;
        inBlock := False;
        Continue;
      end;
      if (not inBlock) or (Pos('=', line) = 0) then
        Continue;
      j := Pos('=', line);
      key := Trim(Copy(line, 1, j - 1));
      val := StripQuotes(Copy(line, j + 1, Length(line) - j));
      if CompareText(key, 'UserName') = 0 then
        cur.UserName := val
      else if CompareText(key, 'Active') = 0 then
        cur.Active := val = '1'
      else if CompareText(key, 'LastCompleteLevel') = 0 then
        cur.LastCompleteLevel := StrToIntDef(val, -1)
      else if CompareText(key, 'CompletedLevels') = 0 then
        cur.CompletedLevels := val
      else if CompareText(key, 'SoundsVolume') = 0 then
        cur.SoundsVolume := StrToIntDef(val, -1)
      else if CompareText(key, 'MusicVolume') = 0 then
        cur.MusicVolume := StrToIntDef(val, -1)
      else if CompareText(key, 'FullScreen') = 0 then
        cur.FullScreen := StrToIntDef(val, -1);
    end;

    Info.Players := count;
    if count = 0 then
    begin
      Info.Error := 'no player block';
      Exit;
    end;

    if count = 1 then
      activeIndex := 0
    else
    begin
      activeCount := 0;
      activeIndex := -1;
      for i := 0 to count - 1 do
        if blocks[i].Active then
        begin
          Inc(activeCount);
          activeIndex := i;
        end;
      if activeCount <> 1 then
      begin
        Info.Error := 'multiple players and no unique Active';
        Exit;
      end;
    end;

    Info.UserName := blocks[activeIndex].UserName;
    Info.LastCompleteLevel := blocks[activeIndex].LastCompleteLevel;
    Info.CompletedLevels := blocks[activeIndex].CompletedLevels;
    Info.SoundsVolume := blocks[activeIndex].SoundsVolume;
    Info.MusicVolume := blocks[activeIndex].MusicVolume;
    Info.FullScreen := blocks[activeIndex].FullScreen;
    Info.Ok := True;
    Result := True;
  finally
    sl.Free;
  end;
end;

end.
