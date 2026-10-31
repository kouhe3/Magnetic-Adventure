unit LuaLog;
{$mode objfpc}{$H+}
// 绑定调用 JSONL（格式对齐 tools/lua_probe.cpp）：
//   {"call":"Name","args":[...],"ret":N}
// 用途：T6.3/a2 把 FPC 宿主跑关的 call+args 与 C++ lua_probe 的语料逐条对拍。
interface

uses SysUtils, Math, LuaDll;

procedure LuaLogInit(const Path: string);
procedure LuaLogClose;
procedure LuaLogBegin(L: TLuaState; const Name: string);
procedure LuaLogEnd(Ret: Integer);

implementation

var
  gLog: TextFile;
  gOpen: Boolean = False;

procedure LuaLogInit(const Path: string);
begin
  if (Path = '') or gOpen then
    Exit;
  AssignFile(gLog, Path);
  Rewrite(gLog);
  gOpen := True;
end;

procedure LuaLogClose;
begin
  if gOpen then
  begin
    CloseFile(gLog);
    gOpen := False;
  end;
end;

procedure WriteJsonString(const S: string);
var
  i: Integer;
  c: Char;
begin
  Write(gLog, '"');
  for i := 1 to Length(S) do
  begin
    c := S[i];
    if (c = '"') or (c = '\') then
      Write(gLog, '\', c)
    else if c = #10 then
      Write(gLog, '\n')
    else if c = #13 then
      Write(gLog, '\r')
    else if c = #9 then
      Write(gLog, '\t')
    else if Ord(c) < 32 then
      Write(gLog, '\u', IntToHex(Ord(c), 4))
    else
      Write(gLog, c);
  end;
  Write(gLog, '"');
end;

procedure LuaLogBegin(L: TLuaState; const Name: string);
var
  i, n, t: Integer;
  d: Double;
  s: PChar;
begin
  if not gOpen then
    Exit;
  n := Lua.GetTop(L);
  Write(gLog, '{"call":"', Name, '","args":[');
  for i := 1 to n do
  begin
    if i > 1 then
      Write(gLog, ',');
    t := Lua.LType(L, i);
    case t of
      LUA_TNUMBER:
        begin
          d := Lua.ToNumber(L, i);
          if IsNan(d) or IsInfinite(d) then
            Write(gLog, 'null')
          else if (d = Int(d)) and (Abs(d) < 1e15) then
            Write(gLog, Trunc(d))
          else
            Write(gLog, FormatFloat('0.############', d));
        end;
      LUA_TSTRING:
        begin
          s := Lua.ToString(L, i, nil);
          if s = nil then
            Write(gLog, 'null')
          else
            WriteJsonString(string(s));
        end;
      LUA_TNIL:
        Write(gLog, 'null');
    else
      Write(gLog, '"<type', t, '>"');
    end;
  end;
end;

procedure LuaLogEnd(Ret: Integer);
begin
  if gOpen then
    WriteLn(gLog, '],"ret":', Ret, '}');
end;

end.
