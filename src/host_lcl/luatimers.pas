unit LuaTimers;
{$mode objfpc}{$H+}
// T6.3：Lua 简单计时器（Add_SimpleTimer / Start_Timer / Do_Command(cm_StartTimer/StopTimer)）。
//
// 原版把 cm_* 常量以 double 注册给 Lua（game.exe 的 16 条记录表，VA 0x6457a0）；
// cm_StartTimer = 10.0、cm_StopTimer = 11.0（Do_Command 的第 2 参按 Integer 读）。
// 计时器用物理步的 dt 递减（宿主 loop 与 EnterLevel 回放都调用 TimerUpdate），
// 到期派发 OnTimer（EventsFire，args = timer id, 0），一次性；脚本自己重开。

interface

uses
  LuaDll;

const
  TimerMax = 64;

procedure TimerReset;
procedure TimerAdd(Id: Integer);
procedure TimerStart(Id: Integer; Seconds: Double);
procedure TimerStop(Id: Integer);
// Do_Command(id, cmd, argCount, value...)：只处理 cm_StartTimer(10) / cm_StopTimer(11)。
procedure TimerCommand(Id, Cmd: Integer; Seconds: Double);
// 递减所有活动计时器；到期的派发 OnTimer。返回派发次数。
function TimerUpdate(L: TLuaState; Dt: Double): Integer;
function TimerActiveCount: Integer;

implementation

uses
  LuaEvents;

type
  TTimerRec = record
    Id: Integer;
    Remaining: Double;
    Active: Boolean;
  end;

var
  gTimers: array[0..TimerMax - 1] of TTimerRec;
  gTimerCount: Integer = 0;

procedure TimerReset;
var
  i: Integer;
begin
  gTimerCount := 0;
  for i := 0 to TimerMax - 1 do
  begin
    gTimers[i].Id := 0;
    gTimers[i].Remaining := 0;
    gTimers[i].Active := False;
  end;
end;

function FindTimer(Id: Integer): Integer;
var
  i: Integer;
begin
  Result := -1;
  for i := 0 to gTimerCount - 1 do
    if gTimers[i].Id = Id then
      Exit(i);
end;

procedure TimerAdd(Id: Integer);
var
  i: Integer;
begin
  if (Id = 0) or (gTimerCount >= TimerMax) then Exit;
  i := FindTimer(Id);
  if i < 0 then
  begin
    i := gTimerCount;
    Inc(gTimerCount);
    gTimers[i].Id := Id;
  end;
  gTimers[i].Remaining := 0;
  gTimers[i].Active := False;
end;

procedure TimerStart(Id: Integer; Seconds: Double);
var
  i: Integer;
begin
  if Id = 0 then Exit;
  i := FindTimer(Id);
  if i < 0 then
  begin
    TimerAdd(Id);
    i := FindTimer(Id);
    if i < 0 then Exit;
  end;
  gTimers[i].Remaining := Seconds;
  gTimers[i].Active := Seconds > 0;
end;

procedure TimerStop(Id: Integer);
var
  i: Integer;
begin
  i := FindTimer(Id);
  if i >= 0 then
    gTimers[i].Active := False;
end;

procedure TimerCommand(Id, Cmd: Integer; Seconds: Double);
begin
  case Cmd of
    10: TimerStart(Id, Seconds);
    11: TimerStop(Id);
  end;
end;

function TimerUpdate(L: TLuaState; Dt: Double): Integer;
var
  i, calls: Integer;
begin
  Result := 0;
  if L = nil then Exit;
  for i := 0 to gTimerCount - 1 do
    if gTimers[i].Active then
    begin
      gTimers[i].Remaining := gTimers[i].Remaining - Dt;
      if gTimers[i].Remaining <= 1e-9 then
      begin
        gTimers[i].Active := False;
        EventsFire(L, gTimers[i].Id, 'OnTimer', 0, calls);
        Inc(Result);
      end;
    end;
end;

function TimerActiveCount: Integer;
var
  i: Integer;
begin
  Result := 0;
  for i := 0 to gTimerCount - 1 do
    if gTimers[i].Active then
      Inc(Result);
end;

initialization
  TimerReset;

end.
