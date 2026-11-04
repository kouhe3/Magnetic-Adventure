unit LuaEvents;
{$mode objfpc}{$H+}
// 对象脚本事件：Attach_ScriptToObject 登记 + 事件派发（T6.3 接触回调竖切）。
//
// 原版语义（F272 实测）：Attach_ScriptToObject(obj, 'OnAddContact', 'gLSystembBigDialOnAddContact')
// 挂的是**全局函数名**；事件发生时引擎以 (self, 另一对象) 调用该函数。lvl49 的回调在
// State==3 / GearJoint1==0 / 接触对象是 gear 时追加 Add_JointSimpleRevolute +
// Add_JointSimpleGear（work/objlog_lvl49.jsonl burst1 末尾恰是这 2 条）。
//
// 本单元不含物理：登记与派发分离，何时 Fire 由调用方决定（自检 HOST_LUA_FIRE，
// 后续接物理层）。派发前把全局 self 设成目标对象，对齐原版事件里的 self 语义。
//
// 判据（tools/lua_event_check.py）：Fire(1016,'OnAddContact',gLSystem.bGearB) 后
// JSONL 末尾依次出现 Add_JointSimpleRevolute / Set_JointLimits / Add_JointSimpleGear。
interface

uses SysUtils, LuaDll;

procedure EventsReset;
procedure EventsAdd(ObjId: Integer; const Event, FuncName: string);
function EventsCount: Integer;
function EventsFire(L: TLuaState; ObjId: Integer; const Event: string;
  Body2: Integer; out Calls: Integer): Integer;
// T6.4b-2a：OnMove 回调签名是 (PosX, PosY)（Double），不能用 Integer 版。
function EventsFireMove(L: TLuaState; ObjId: Integer; X, Y: Double;
  out Calls: Integer): Integer;
function EvalIntExpr(L: TLuaState; const Expr: string; out Value: Integer;
  out Err: string): Boolean;
function EventsFireExpr(L: TLuaState; ObjId: Integer; const Event,
  Body2Expr: string; out Fired: Integer; out Err: string): Boolean;

implementation

const
  LUA_TFUNCTION = 6;

type
  TEventBinding = record
    ObjId: Integer;
    EventName: string;
    FuncName: string;
  end;

var
  gBindings: array of TEventBinding;

procedure EventsReset;
begin
  SetLength(gBindings, 0);
end;

procedure EventsAdd(ObjId: Integer; const Event, FuncName: string);
var
  n: Integer;
begin
  n := Length(gBindings);
  SetLength(gBindings, n + 1);
  gBindings[n].ObjId := ObjId;
  gBindings[n].EventName := Event;
  gBindings[n].FuncName := FuncName;
end;

function EventsCount: Integer;
begin
  Result := Length(gBindings);
end;

// 在 Lua 里求值 'return <Expr>' 并把结果读成 Integer；栈恢复到进入时的 top。
function EvalIntExpr(L: TLuaState; const Expr: string; out Value: Integer;
  out Err: string): Boolean;
var
  rc, top: Integer;
begin
  Value := 0;
  Err := '';
  top := Lua.GetTop(L);
  rc := Lua.LoadString(L, PChar('return ' + Expr));
  if rc <> 0 then
  begin
    Err := LuaLastError(L);
    Lua.SetTop(L, top);
    Result := False;
    Exit;
  end;
  rc := Lua.PCall(L, 0, 1, 0);
  if rc <> 0 then
  begin
    Err := LuaLastError(L);
    Lua.SetTop(L, top);
    Result := False;
    Exit;
  end;
  Value := Lua.ToInteger(L, -1);
  Lua.SetTop(L, top);
  Result := True;
end;

// 派发一个事件：命中登记的每个 (ObjId, Event) 各调一次。返回成功调用次数，
// Calls 记录命中登记的条数（两者不等 = 有函数缺失或执行出错）。
function EventsFire(L: TLuaState; ObjId: Integer; const Event: string;
  Body2: Integer; out Calls: Integer): Integer;
var
  i, rc: Integer;
begin
  Result := 0;
  Calls := 0;
  for i := 0 to High(gBindings) do
    if (gBindings[i].ObjId = ObjId) and (gBindings[i].EventName = Event) then
    begin
      Inc(Calls);
      Lua.GetField(L, LUA_GLOBALSINDEX, PChar(gBindings[i].FuncName));
      if Lua.LType(L, -1) = LUA_TFUNCTION then
      begin
        // 原版事件里 self = 触发对象（bSwitchOnRotate 等回调依赖它）。
        Lua.PushInteger(L, ObjId);
        Lua.SetField(L, LUA_GLOBALSINDEX, PChar('self'));
        Lua.PushInteger(L, ObjId);
        Lua.PushInteger(L, Body2);
        rc := Lua.PCall(L, 2, 0, 0);
        if rc = 0 then
          Inc(Result)
        else
          LuaLastError(L);
      end
      else
        Lua.SetTop(L, -2);
    end;
end;

// Body2 用 Lua 表达式给出（如 gLSystem.bGearB），避免把对象 id 写死。
function EventsFireMove(L: TLuaState; ObjId: Integer; X, Y: Double;
  out Calls: Integer): Integer;
var
  i, rc: Integer;
begin
  Result := 0;
  Calls := 0;
  for i := 0 to High(gBindings) do
    if (gBindings[i].ObjId = ObjId) and (gBindings[i].EventName = 'OnMove') then
    begin
      Inc(Calls);
      Lua.GetField(L, LUA_GLOBALSINDEX, PChar(gBindings[i].FuncName));
      if Lua.LType(L, -1) = LUA_TFUNCTION then
      begin
        Lua.PushInteger(L, ObjId);
        Lua.SetField(L, LUA_GLOBALSINDEX, PChar('self'));
        Lua.PushNumber(L, X);
        Lua.PushNumber(L, Y);
        rc := Lua.PCall(L, 2, 0, 0);
        if rc = 0 then
          Inc(Result)
        else
          LuaLastError(L);
      end
      else
        Lua.SetTop(L, -2);
    end;
end;

function EventsFireExpr(L: TLuaState; ObjId: Integer; const Event,
  Body2Expr: string; out Fired: Integer; out Err: string): Boolean;
var
  body2, calls: Integer;
begin
  Fired := 0;
  Err := '';
  if not EvalIntExpr(L, Body2Expr, body2, Err) then
  begin
    Result := False;
    Exit;
  end;
  Fired := EventsFire(L, ObjId, Event, body2, calls);
  if calls = 0 then
  begin
    Err := 'no binding for ' + IntToStr(ObjId) + '/' + Event;
    Result := False;
    Exit;
  end;
  Result := True;
end;

end.
