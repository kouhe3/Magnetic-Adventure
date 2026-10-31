unit LuaDll;
{$mode objfpc}{$H+}
// Lua 5.1.5 动态加载（产物 build/Release/lua51.dll，CMake target lua51_dll，F240）。
// 全部 API 是 cdecl；FPC 2.2.4 的无参函数指针必须写 ()（F240）。
interface

uses Windows;

type
  TLuaState = Pointer;

  TLuaNewState = function: TLuaState; cdecl;
  TLuaOpenLibs = procedure(L: TLuaState); cdecl;
  TLuaLoadString = function(L: TLuaState; const S: PChar): Integer; cdecl;
  TLuaLoadFile = function(L: TLuaState; const FileName: PChar): Integer; cdecl;
  TLuaPCall = function(L: TLuaState; NArgs, NResults, ErrFunc: Integer): Integer; cdecl;
  TLuaToInteger = function(L: TLuaState; Idx: Integer): Integer; cdecl;
  TLuaToNumber = function(L: TLuaState; Idx: Integer): Double; cdecl;
  TLuaToString = function(L: TLuaState; Idx: Integer; Len: PInteger): PChar; cdecl;
  TLuaClose = procedure(L: TLuaState); cdecl;
  TLuaGetTop = function(L: TLuaState): Integer; cdecl;
  TLuaType = function(L: TLuaState; Idx: Integer): Integer; cdecl;
  TLuaPushInteger = procedure(L: TLuaState; N: Integer); cdecl;
  TLuaPushNumber = procedure(L: TLuaState; N: Double); cdecl;
  TLuaPushCClosure = procedure(L: TLuaState; Fn: Pointer; N: Integer); cdecl;
  TLuaCreateTable = procedure(L: TLuaState; NArr, NRec: Integer); cdecl;
  TLuaSetField = procedure(L: TLuaState; Idx: Integer; const K: PChar); cdecl;
  TLuaGetField = function(L: TLuaState; Idx: Integer; const K: PChar): Integer; cdecl;
  TLuaPushString = procedure(L: TLuaState; const S: PChar); cdecl;
  TLuaSetTop = procedure(L: TLuaState; Idx: Integer); cdecl;

  TLuaDll = record
    Handle: HMODULE;
    NewState: TLuaNewState;
    OpenLibs: TLuaOpenLibs;
    LoadString: TLuaLoadString;
    LoadFile: TLuaLoadFile;
    PCall: TLuaPCall;
    ToInteger: TLuaToInteger;
    ToNumber: TLuaToNumber;
    ToString: TLuaToString;
    Close: TLuaClose;
    GetTop: TLuaGetTop;
    LType: TLuaType;
    PushInteger: TLuaPushInteger;
    PushNumber: TLuaPushNumber;
    PushCClosure: TLuaPushCClosure;
    CreateTable: TLuaCreateTable;
    SetField: TLuaSetField;
    GetField: TLuaGetField;
    PushString: TLuaPushString;
    SetTop: TLuaSetTop;
  end;

const
  LUA_TNIL = 0;
  LUA_TNUMBER = 3;
  LUA_TSTRING = 4;
  LUA_GLOBALSINDEX = -10002;

var
  Lua: TLuaDll;

// 加载 lua51.dll 并解析全部 API；失败返回 False（宿主仍可启动）。
function LuaLoad: Boolean;
// 读栈顶错误对象并清栈。
function LuaLastError(L: TLuaState): string;
// F201 的 optnumber/optint：lua_type==LUA_TNUMBER 才取值，否则默认。
function LuaOptNumber(L: TLuaState; Idx: Integer; Default: Double): Double;
function LuaOptInt(L: TLuaState; Idx: Integer; Default: Integer): Integer;
function LuaOptStr(L: TLuaState; Idx: Integer): PChar;

implementation

function LuaLoad: Boolean;
begin
  FillChar(Lua, SizeOf(Lua), 0);
  Lua.Handle := LoadLibrary(PChar('lua51.dll'));
  if Lua.Handle = 0 then
    Exit(False);
  Lua.NewState := TLuaNewState(GetProcAddress(Lua.Handle, PChar('luaL_newstate')));
  Lua.OpenLibs := TLuaOpenLibs(GetProcAddress(Lua.Handle, PChar('luaL_openlibs')));
  Lua.LoadString := TLuaLoadString(GetProcAddress(Lua.Handle, PChar('luaL_loadstring')));
  Lua.LoadFile := TLuaLoadFile(GetProcAddress(Lua.Handle, PChar('luaL_loadfile')));
  Lua.PCall := TLuaPCall(GetProcAddress(Lua.Handle, PChar('lua_pcall')));
  Lua.ToInteger := TLuaToInteger(GetProcAddress(Lua.Handle, PChar('lua_tointeger')));
  Lua.ToNumber := TLuaToNumber(GetProcAddress(Lua.Handle, PChar('lua_tonumber')));
  Lua.ToString := TLuaToString(GetProcAddress(Lua.Handle, PChar('lua_tolstring')));
  Lua.Close := TLuaClose(GetProcAddress(Lua.Handle, PChar('lua_close')));
  Lua.GetTop := TLuaGetTop(GetProcAddress(Lua.Handle, PChar('lua_gettop')));
  Lua.LType := TLuaType(GetProcAddress(Lua.Handle, PChar('lua_type')));
  Lua.PushInteger := TLuaPushInteger(GetProcAddress(Lua.Handle, PChar('lua_pushinteger')));
  Lua.PushNumber := TLuaPushNumber(GetProcAddress(Lua.Handle, PChar('lua_pushnumber')));
  Lua.PushCClosure := TLuaPushCClosure(GetProcAddress(Lua.Handle, PChar('lua_pushcclosure')));
  Lua.CreateTable := TLuaCreateTable(GetProcAddress(Lua.Handle, PChar('lua_createtable')));
  Lua.SetField := TLuaSetField(GetProcAddress(Lua.Handle, PChar('lua_setfield')));
  Lua.GetField := TLuaGetField(GetProcAddress(Lua.Handle, PChar('lua_getfield')));
  Lua.PushString := TLuaPushString(GetProcAddress(Lua.Handle, PChar('lua_pushstring')));
  Lua.SetTop := TLuaSetTop(GetProcAddress(Lua.Handle, PChar('lua_settop')));
  Result := Assigned(Lua.NewState) and Assigned(Lua.OpenLibs) and
    Assigned(Lua.LoadString) and Assigned(Lua.LoadFile) and Assigned(Lua.PCall) and
    Assigned(Lua.ToInteger) and Assigned(Lua.ToNumber) and Assigned(Lua.ToString) and
    Assigned(Lua.Close) and Assigned(Lua.GetTop) and Assigned(Lua.LType) and
    Assigned(Lua.PushInteger) and Assigned(Lua.PushNumber) and Assigned(Lua.PushCClosure) and
    Assigned(Lua.CreateTable) and Assigned(Lua.SetField) and Assigned(Lua.GetField) and
    Assigned(Lua.PushString) and Assigned(Lua.SetTop);
end;

function LuaLastError(L: TLuaState): string;
begin
  Result := string(Lua.ToString(L, -1, nil));
  Lua.SetTop(L, 0);
end;

function LuaOptNumber(L: TLuaState; Idx: Integer; Default: Double): Double;
begin
  if Lua.LType(L, Idx) = LUA_TNUMBER then
    Result := Lua.ToNumber(L, Idx)
  else
    Result := Default;
end;

function LuaOptInt(L: TLuaState; Idx: Integer; Default: Integer): Integer;
begin
  if Lua.LType(L, Idx) = LUA_TNUMBER then
    Result := Trunc(Lua.ToNumber(L, Idx))
  else
    Result := Default;
end;

function LuaOptStr(L: TLuaState; Idx: Integer): PChar;
begin
  if Lua.LType(L, Idx) = LUA_TSTRING then
    Result := Lua.ToString(L, Idx, nil)
  else
    Result := nil;
end;

end.
