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
// T6.4c-2：只改 active 玩家的 LastCompleteLevel，其余字节/行不变。
function WriteLastCompleteLevel(const Path: string; Level: Integer): Boolean;
// T6.4d-8：改 active 玩家的任意键（音量/全屏）；键不存在时插在 </Player> 前。
function WriteProfileSetting(const Path, Key, Value: string): Boolean;

implementation

uses
  SysUtils, Classes, Windows;

type
  TByteArray = array of Byte;
  TBlockSpan = record
    StartLine, StopLine: Integer;
    Active: Boolean;
    UserName: string;
  end;

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


function EncodeProfile(const Text: string): TByteArray;
var
  i: Integer;
  b: Byte;
begin
  SetLength(Result, 2 + Length(Text) * 2);
  Result[0] := $FF;
  Result[1] := $FE;
  for i := 1 to Length(Text) do
  begin
    b := Byte(Ord(Text[i]) xor $B8);
    Result[2 + (i - 1) * 2] := b;
    Result[2 + (i - 1) * 2 + 1] := 0;
  end;
end;

// 按 #10 切行，第 LineIndex 行（0 基）替换为 NewLine；保留行尾 #13。
function ReplaceLineLF(const Text: string; LineIndex: Integer;
  const NewLine: string): string;
var
  i, line, p: Integer;
  hasCR: Boolean;
begin
  Result := Text;
  line := 0;
  p := 1;
  for i := 1 to Length(Text) do
    if Text[i] = #10 then
    begin
      if line = LineIndex then
      begin
        hasCR := (i > p) and (Text[i - 1] = #13);
        Result := Copy(Text, 1, p - 1) + NewLine;
        if hasCR then Result := Result + #13;
        Result := Result + Copy(Text, i, MaxInt);
        Exit;
      end;
      Inc(line);
      p := i + 1;
    end;
  if line = LineIndex then
  begin
    hasCR := (Length(Text) >= p) and (Text[Length(Text)] = #13);
    Result := Copy(Text, 1, p - 1) + NewLine;
    if hasCR then Result := Result + #13;
  end;
end;

// 原版保存时把 CompletedLevels 过滤到 <= LastCompleteLevel（F466：15-16-17-18 + level 1 → 空）。
function FilterCompleted(const S: string; Level: Integer): string;
var
  p, n, code: Integer;
  part: string;
begin
  Result := '';
  p := 1;
  while p <= Length(S) do
  begin
    while (p <= Length(S)) and (S[p] = '-') do Inc(p);
    part := '';
    while (p <= Length(S)) and (S[p] <> '-') do
    begin
      part := part + S[p];
      Inc(p);
    end;
    if part <> '' then
    begin
      Val(part, n, code);
      if (code = 0) and (n <= Level) then
        Result := Result + '-' + IntToStr(n);
    end;
  end;
end;

// T6.4c：选出 active 玩家的 <Player> 块（单块直取；多块取唯一 Active=1）。
function SelectActiveBlockSpan(sl: TStringList; out StartLine, StopLine: Integer): Boolean;
var
  i, count, activeCount, activeIndex, blockStart: Integer;
  val, key, blockName: string;
  inBlock, blockActive: Boolean;
  blocks: array of TBlockSpan;
begin
  Result := False;
  SetLength(blocks, 0);
  count := 0;
  inBlock := False;
  blockActive := False;
  blockStart := 0;
  blockName := '';
  for i := 0 to sl.Count - 1 do
  begin
    val := Trim(sl[i]);
    if CompareText(val, '<Player>') = 0 then
    begin
      inBlock := True;
      blockActive := False;
      blockStart := i;
      blockName := '';
      Continue;
    end;
    if CompareText(val, '</Player>') = 0 then
    begin
      if inBlock then
      begin
        SetLength(blocks, count + 1);
        blocks[count].StartLine := blockStart;
        blocks[count].StopLine := i;
        blocks[count].Active := blockActive;
        blocks[count].UserName := blockName;
        Inc(count);
      end;
      inBlock := False;
      Continue;
    end;
    if (not inBlock) or (Pos('=', val) = 0) then Continue;
    key := Trim(Copy(val, 1, Pos('=', val) - 1));
    val := StripQuotes(Copy(val, Pos('=', val) + 1, MaxInt));
    if CompareText(key, 'Active') = 0 then
      blockActive := val = '1'
    else if CompareText(key, 'UserName') = 0 then
      blockName := val;
  end;
  if count = 0 then Exit;
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
    if activeCount <> 1 then Exit;
  end;
  StartLine := blocks[activeIndex].StartLine;
  StopLine := blocks[activeIndex].StopLine;
  Result := True;
end;

function WriteLastCompleteLevel(const Path: string; Level: Integer): Boolean;
var
  fs: TFileStream;
  raw, enc: TByteArray;
  size, i, keyLine, compLine, blockStartLine, blockStopLine: Integer;
  oldLevel: Integer;
  oldList, text, err, key, val, newLine: string;
  sl: TStringList;
begin
  Result := False;
  if not FileExists(Path) then Exit;
  fs := TFileStream.Create(Path, fmOpenRead or fmShareDenyWrite);
  try
    size := fs.Size;
    SetLength(raw, size);
    if size > 0 then
      fs.ReadBuffer(raw[0], size);
  finally
    fs.Free;
  end;
  if not DecodeProfile(raw, text, err) then Exit;
  sl := TStringList.Create;
  try
    sl.Text := text;
    if not SelectActiveBlockSpan(sl, blockStartLine, blockStopLine) then Exit;

    keyLine := -1;
    compLine := -1;
    oldLevel := 0;
    oldList := '';
    for i := blockStartLine + 1 to blockStopLine - 1 do
      if Pos('=', sl[i]) > 0 then
      begin
        key := Trim(Copy(sl[i], 1, Pos('=', sl[i]) - 1));
        val := StripQuotes(Copy(sl[i], Pos('=', sl[i]) + 1, MaxInt));
        if CompareText(key, 'LastCompleteLevel') = 0 then
        begin
          keyLine := i;
          oldLevel := StrToIntDef(val, 0);
        end
        else if CompareText(key, 'CompletedLevels') = 0 then
        begin
          compLine := i;
          oldList := val;
        end;
      end;
    if keyLine < 0 then Exit;
    // 原版不回退进度：写 max(old, Level)（F466）。
    if oldLevel > Level then Level := oldLevel;
    newLine := 'LastCompleteLevel = "' + IntToStr(Level) + '"';
    text := ReplaceLineLF(text, keyLine, newLine);
    if compLine >= 0 then
      text := ReplaceLineLF(text, compLine,
        'CompletedLevels = "' + FilterCompleted(oldList, Level) + '"');
    enc := EncodeProfile(text);
    fs := TFileStream.Create(Path, fmCreate);
    try
      if Length(enc) > 0 then
        fs.WriteBuffer(enc[0], Length(enc));
    finally
      fs.Free;
    end;
    Result := True;
  finally
    sl.Free;
  end;
end;


// 返回第 LineIndex 行（0 基）的起始字符偏移；越界返回 0。
function LineStartOffset(const Text: string; LineIndex: Integer): Integer;
var
  i, line, p: Integer;
begin
  line := 0;
  p := 1;
  for i := 1 to Length(Text) do
    if Text[i] = #10 then
    begin
      if line = LineIndex then Exit(p);
      Inc(line);
      p := i + 1;
    end;
  if line = LineIndex then Exit(p);
  Result := 0;
end;

function WriteProfileSetting(const Path, Key, Value: string): Boolean;
var
  fs: TFileStream;
  raw, enc: TByteArray;
  size, i, keyLine, blockStartLine, blockStopLine, off: Integer;
  text, err, newLine: string;
  sl: TStringList;
begin
  Result := False;
  if (Key = '') or not FileExists(Path) then Exit;
  fs := TFileStream.Create(Path, fmOpenRead or fmShareDenyWrite);
  try
    size := fs.Size;
    SetLength(raw, size);
    if size > 0 then
      fs.ReadBuffer(raw[0], size);
  finally
    fs.Free;
  end;
  if not DecodeProfile(raw, text, err) then Exit;
  sl := TStringList.Create;
  try
    sl.Text := text;
    if not SelectActiveBlockSpan(sl, blockStartLine, blockStopLine) then Exit;
    keyLine := -1;
    for i := blockStartLine + 1 to blockStopLine - 1 do
      if (Pos('=', sl[i]) > 0) and
         (CompareText(Trim(Copy(sl[i], 1, Pos('=', sl[i]) - 1)), Key) = 0) then
      begin
        keyLine := i;
        Break;
      end;
    newLine := Key + ' = "' + Value + '"';
    if keyLine >= 0 then
      text := ReplaceLineLF(text, keyLine, newLine)
    else
    begin
      off := LineStartOffset(text, blockStopLine);
      if off = 0 then Exit;
      text := Copy(text, 1, off - 1) + newLine + #13#10 + Copy(text, off, MaxInt);
    end;
    enc := EncodeProfile(text);
    fs := TFileStream.Create(Path, fmCreate);
    try
      if Length(enc) > 0 then
        fs.WriteBuffer(enc[0], Length(enc));
    finally
      fs.Free;
    end;
    Result := True;
  finally
    sl.Free;
  end;
end;

end.
