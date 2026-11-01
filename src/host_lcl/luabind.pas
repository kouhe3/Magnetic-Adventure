unit LuaBind;
{$mode objfpc}{$H+}
// 由 tools/gen_lua_bindings.py 从 mapping/lua-binding-args.csv 生成，勿手改。
// 144 个 Lua 绑定壳：按参数表读参 + 桩返回值（T6.3/a1，F239/F201）。
// 桩语义：Add_* 返回递增 id（1001 起，对齐 tools/lua_probe.cpp），其余 0。
interface

uses LuaDll, LuaLog, LuaEvents, PhysWorld;

function NextId(const Name: string): Integer;
procedure ResetIds;
procedure RegisterBindings(L: TLuaState);

implementation

var
  g_nextId: Integer = 1000;

function NextId(const Name: string): Integer;
begin
  if (Length(Name) >= 4) and (Copy(Name, 1, 4) = 'Add_') then
  begin
    Inc(g_nextId);
    Result := g_nextId;
  end
  else
    Result := 0;
end;

procedure ResetIds;
begin
  g_nextId := 1000;
end;

function bind_Do_Command(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: Integer;
  v3: Integer;
  n, i: Integer;
  d: Double;
begin
  LuaLogBegin(L, 'Do_Command');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptInt(L, 2, 0);
  v3 := LuaOptInt(L, 3, 0);
  n := v3;
  for i := 0 to n - 1 do
    d := LuaOptNumber(L, 4 + i, 0.0);
  id := NextId('Do_Command');
  Result := 0;
  LuaLogEnd(id);
end;

function bind_Add_WoodBox(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: Double;
  v3: Double;
  v4: Double;
  v5: Double;
begin
  LuaLogBegin(L, 'Add_WoodBox');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptNumber(L, 2, 0.0);
  v3 := LuaOptNumber(L, 3, 0.0);
  v4 := LuaOptNumber(L, 4, 0.0);
  v5 := LuaOptNumber(L, 5, 0.0);
  id := NextId('Add_WoodBox');
  PhysAddWoodBox(id, v2, v3, v4, v5);
  Lua.PushInteger(L, id);
  Result := 1;
  LuaLogEnd(id);
end;

function bind_Add_MetallScrew(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: Double;
  v3: Double;
  v4: Double;
  v5: Double;
begin
  LuaLogBegin(L, 'Add_MetallScrew');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptNumber(L, 2, 0.0);
  v3 := LuaOptNumber(L, 3, 0.0);
  v4 := LuaOptNumber(L, 4, 0.0);
  v5 := LuaOptNumber(L, 5, 0.0);
  id := NextId('Add_MetallScrew');
  PhysAddMetallScrew(id, v2, v3, v4, v5);
  Lua.PushInteger(L, id);
  Result := 1;
  LuaLogEnd(id);
end;

function bind_Add_MetallGear(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: Double;
  v3: Double;
  v4: Double;
  v5: Double;
begin
  LuaLogBegin(L, 'Add_MetallGear');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptNumber(L, 2, 0.0);
  v3 := LuaOptNumber(L, 3, 0.0);
  v4 := LuaOptNumber(L, 4, 0.0);
  v5 := LuaOptNumber(L, 5, 0.0);
  id := NextId('Add_MetallGear');
  PhysAddMetallGear(id, v2, v3, v4, v5);
  Lua.PushInteger(L, id);
  Result := 1;
  LuaLogEnd(id);
end;

function bind_Add_WoodGear(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: Double;
  v3: Double;
  v4: Double;
  v5: Double;
begin
  LuaLogBegin(L, 'Add_WoodGear');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptNumber(L, 2, 0.0);
  v3 := LuaOptNumber(L, 3, 0.0);
  v4 := LuaOptNumber(L, 4, 0.0);
  v5 := LuaOptNumber(L, 5, 0.0);
  id := NextId('Add_WoodGear');
  PhysAddWoodGear(id, v2, v3, v4, v5);
  Lua.PushInteger(L, id);
  Result := 1;
  LuaLogEnd(id);
end;

function bind_Add_WoodWall(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: Double;
  v3: Double;
  v4: Double;
  v5: Double;
begin
  LuaLogBegin(L, 'Add_WoodWall');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptNumber(L, 2, 0.0);
  v3 := LuaOptNumber(L, 3, 0.0);
  v4 := LuaOptNumber(L, 4, 0.0);
  v5 := LuaOptNumber(L, 5, 0.0);
  id := NextId('Add_WoodWall');
  PhysAddWoodWall(id, v2, v3, v4);
  Lua.PushInteger(L, id);
  Result := 1;
  LuaLogEnd(id);
end;

function bind_Add_WoodFormWall(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: Double;
  v3: Double;
  v4: Double;
  v5: Double;
begin
  LuaLogBegin(L, 'Add_WoodFormWall');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptNumber(L, 2, 0.0);
  v3 := LuaOptNumber(L, 3, 0.0);
  v4 := LuaOptNumber(L, 4, 0.0);
  v5 := LuaOptNumber(L, 5, 0.0);
  id := NextId('Add_WoodFormWall');
  PhysAddWoodFormWall(id, v2, v3, v4, v5);
  Lua.PushInteger(L, id);
  Result := 1;
  LuaLogEnd(id);
end;

function bind_Add_SwitchArm(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: Double;
  v3: Double;
  v4: Double;
  v5: Double;
begin
  LuaLogBegin(L, 'Add_SwitchArm');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptNumber(L, 2, 0.0);
  v3 := LuaOptNumber(L, 3, 0.0);
  v4 := LuaOptNumber(L, 4, 0.0);
  v5 := LuaOptNumber(L, 5, 0.0);
  id := NextId('Add_SwitchArm');
  PhysAddSwitchArm(id, v2, v3, v4);
  Lua.PushInteger(L, id);
  Result := 1;
  LuaLogEnd(id);
end;

function bind_Add_Lock(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: Double;
  v3: Double;
  v4: Double;
  v5: Double;
begin
  LuaLogBegin(L, 'Add_Lock');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptNumber(L, 2, 0.0);
  v3 := LuaOptNumber(L, 3, 0.0);
  v4 := LuaOptNumber(L, 4, 0.0);
  v5 := LuaOptNumber(L, 5, 0.0);
  id := NextId('Add_Lock');
  PhysAddLock(id, v2, v3, v4, v5);
  Lua.PushInteger(L, id);
  Result := 1;
  LuaLogEnd(id);
end;

function bind_Add_Key(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: Double;
  v3: Double;
  v4: Double;
  v5: Double;
begin
  LuaLogBegin(L, 'Add_Key');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptNumber(L, 2, 0.0);
  v3 := LuaOptNumber(L, 3, 0.0);
  v4 := LuaOptNumber(L, 4, 0.0);
  v5 := LuaOptNumber(L, 5, 0.0);
  id := NextId('Add_Key');
  PhysAddKey(id, v2, v3, v4, v5);
  Lua.PushInteger(L, id);
  Result := 1;
  LuaLogEnd(id);
end;

function bind_Add_Symbol(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: Double;
  v3: Double;
  v4: Double;
  v5: Double;
begin
  LuaLogBegin(L, 'Add_Symbol');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptNumber(L, 2, 0.0);
  v3 := LuaOptNumber(L, 3, 0.0);
  v4 := LuaOptNumber(L, 4, 0.0);
  v5 := LuaOptNumber(L, 5, 0.0);
  id := NextId('Add_Symbol');
  Lua.PushInteger(L, id);
  Result := 1;
  LuaLogEnd(id);
end;

function bind_Add_HammerParts(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: Double;
  v3: Double;
  v4: Double;
  v5: Double;
begin
  LuaLogBegin(L, 'Add_HammerParts');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptNumber(L, 2, 0.0);
  v3 := LuaOptNumber(L, 3, 0.0);
  v4 := LuaOptNumber(L, 4, 0.0);
  v5 := LuaOptNumber(L, 5, 0.0);
  id := NextId('Add_HammerParts');
  PhysAddHammerParts(id, v2, v3, v4, v5);
  Lua.PushInteger(L, id);
  Result := 1;
  LuaLogEnd(id);
end;

function bind_Add_BarDoor(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: Double;
  v3: Double;
  v4: Double;
  v5: Double;
begin
  LuaLogBegin(L, 'Add_BarDoor');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptNumber(L, 2, 0.0);
  v3 := LuaOptNumber(L, 3, 0.0);
  v4 := LuaOptNumber(L, 4, 0.0);
  v5 := LuaOptNumber(L, 5, 0.0);
  id := NextId('Add_BarDoor');
  PhysAddBarDoor(id, v2, v3, v4, v5);
  Lua.PushInteger(L, id);
  Result := 1;
  LuaLogEnd(id);
end;

function bind_Add_Ball(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: Double;
  v3: Double;
  v4: Double;
  v5: Double;
begin
  LuaLogBegin(L, 'Add_Ball');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptNumber(L, 2, 0.0);
  v3 := LuaOptNumber(L, 3, 0.0);
  v4 := LuaOptNumber(L, 4, 0.0);
  v5 := LuaOptNumber(L, 5, 0.0);
  id := NextId('Add_Ball');
  Lua.PushInteger(L, id);
  Result := 1;
  LuaLogEnd(id);
end;

function bind_Add_ControlArm(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: Double;
  v3: Double;
  v4: Double;
  v5: Double;
begin
  LuaLogBegin(L, 'Add_ControlArm');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptNumber(L, 2, 0.0);
  v3 := LuaOptNumber(L, 3, 0.0);
  v4 := LuaOptNumber(L, 4, 0.0);
  v5 := LuaOptNumber(L, 5, 0.0);
  id := NextId('Add_ControlArm');
  Lua.PushInteger(L, id);
  Result := 1;
  LuaLogEnd(id);
end;

function bind_Add_DoorHandle(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: Double;
  v3: Double;
  v4: Double;
  v5: Double;
begin
  LuaLogBegin(L, 'Add_DoorHandle');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptNumber(L, 2, 0.0);
  v3 := LuaOptNumber(L, 3, 0.0);
  v4 := LuaOptNumber(L, 4, 0.0);
  v5 := LuaOptNumber(L, 5, 0.0);
  id := NextId('Add_DoorHandle');
  Lua.PushInteger(L, id);
  Result := 1;
  LuaLogEnd(id);
end;

function bind_Add_ScrewDriver(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: Double;
  v3: Double;
  v4: Double;
  v5: Double;
begin
  LuaLogBegin(L, 'Add_ScrewDriver');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptNumber(L, 2, 0.0);
  v3 := LuaOptNumber(L, 3, 0.0);
  v4 := LuaOptNumber(L, 4, 0.0);
  v5 := LuaOptNumber(L, 5, 0.0);
  id := NextId('Add_ScrewDriver');
  PhysAddScrewDriver(id, v2, v3, v4, v5);
  Lua.PushInteger(L, id);
  Result := 1;
  LuaLogEnd(id);
end;

function bind_Add_Rope(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: Double;
  v3: Double;
  v4: Double;
  n, i: Integer;
  d: Double;
  ang: array[0..63] of Double;
begin
  LuaLogBegin(L, 'Add_Rope');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptNumber(L, 2, 0.0);
  v3 := LuaOptNumber(L, 3, 0.0);
  v4 := LuaOptNumber(L, 4, 0.0);
  n := 0;
  i := 5;
  while (Lua.LType(L, i) = LUA_TNUMBER) and (n < 64) do
  begin
    ang[n] := Lua.ToNumber(L, i);
    Inc(n);
    Inc(i);
  end;
  id := NextId('Add_Rope');
  PhysAddRope(id, v2, v3, v4, n, @ang[0]);
  Lua.PushInteger(L, id);
  Result := 1;
  LuaLogEnd(id);
end;

function bind_Add_Cork(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: Double;
  v3: Double;
  v4: Double;
  v5: Double;
begin
  LuaLogBegin(L, 'Add_Cork');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptNumber(L, 2, 0.0);
  v3 := LuaOptNumber(L, 3, 0.0);
  v4 := LuaOptNumber(L, 4, 0.0);
  v5 := LuaOptNumber(L, 5, 0.0);
  id := NextId('Add_Cork');
  PhysAddCork(id, v2, v3, v4, v5);
  Lua.PushInteger(L, id);
  Result := 1;
  LuaLogEnd(id);
end;

function bind_Add_TestTube(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: Double;
  v3: Double;
  v4: Double;
  v5: Double;
begin
  LuaLogBegin(L, 'Add_TestTube');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptNumber(L, 2, 0.0);
  v3 := LuaOptNumber(L, 3, 0.0);
  v4 := LuaOptNumber(L, 4, 0.0);
  v5 := LuaOptNumber(L, 5, 0.0);
  id := NextId('Add_TestTube');
  PhysAddTestTube(id, v2, v3, v4, v5);
  Lua.PushInteger(L, id);
  Result := 1;
  LuaLogEnd(id);
end;

function bind_Add_Rack(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: Double;
  v3: Double;
  v4: Double;
  v5: Double;
begin
  LuaLogBegin(L, 'Add_Rack');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptNumber(L, 2, 0.0);
  v3 := LuaOptNumber(L, 3, 0.0);
  v4 := LuaOptNumber(L, 4, 0.0);
  v5 := LuaOptNumber(L, 5, 0.0);
  id := NextId('Add_Rack');
  PhysAddRack(id, v2, v3, v4, v5);
  Lua.PushInteger(L, id);
  Result := 1;
  LuaLogEnd(id);
end;

function bind_Add_Battery(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: Double;
  v3: Double;
  v4: Double;
  v5: Double;
begin
  LuaLogBegin(L, 'Add_Battery');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptNumber(L, 2, 0.0);
  v3 := LuaOptNumber(L, 3, 0.0);
  v4 := LuaOptNumber(L, 4, 0.0);
  v5 := LuaOptNumber(L, 5, 0.0);
  id := NextId('Add_Battery');
  Lua.PushInteger(L, id);
  Result := 1;
  LuaLogEnd(id);
end;

function bind_Add_ElectricPlug(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: Double;
  v3: Double;
  v4: Double;
  v5: Double;
begin
  LuaLogBegin(L, 'Add_ElectricPlug');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptNumber(L, 2, 0.0);
  v3 := LuaOptNumber(L, 3, 0.0);
  v4 := LuaOptNumber(L, 4, 0.0);
  v5 := LuaOptNumber(L, 5, 0.0);
  id := NextId('Add_ElectricPlug');
  Lua.PushInteger(L, id);
  Result := 1;
  LuaLogEnd(id);
end;

function bind_Add_Spanner(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: Double;
  v3: Double;
  v4: Double;
  v5: Double;
begin
  LuaLogBegin(L, 'Add_Spanner');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptNumber(L, 2, 0.0);
  v3 := LuaOptNumber(L, 3, 0.0);
  v4 := LuaOptNumber(L, 4, 0.0);
  v5 := LuaOptNumber(L, 5, 0.0);
  id := NextId('Add_Spanner');
  Lua.PushInteger(L, id);
  Result := 1;
  LuaLogEnd(id);
end;

function bind_Add_Laser(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: Double;
  v3: Double;
  v4: Double;
  v5: Double;
begin
  LuaLogBegin(L, 'Add_Laser');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptNumber(L, 2, 0.0);
  v3 := LuaOptNumber(L, 3, 0.0);
  v4 := LuaOptNumber(L, 4, 0.0);
  v5 := LuaOptNumber(L, 5, 0.0);
  id := NextId('Add_Laser');
  PhysAddLaser(id, v2, v3, v4, v5);
  Lua.PushInteger(L, id);
  Result := 1;
  LuaLogEnd(id);
end;

function bind_Add_StaticCan(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: Double;
  v3: Double;
  v4: Double;
  v5: Double;
begin
  LuaLogBegin(L, 'Add_StaticCan');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptNumber(L, 2, 0.0);
  v3 := LuaOptNumber(L, 3, 0.0);
  v4 := LuaOptNumber(L, 4, 0.0);
  v5 := LuaOptNumber(L, 5, 0.0);
  id := NextId('Add_StaticCan');
  Lua.PushInteger(L, id);
  Result := 1;
  LuaLogEnd(id);
end;

function bind_Add_Lamp(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: Double;
  v3: Double;
  v4: Double;
  v5: Double;
begin
  LuaLogBegin(L, 'Add_Lamp');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptNumber(L, 2, 0.0);
  v3 := LuaOptNumber(L, 3, 0.0);
  v4 := LuaOptNumber(L, 4, 0.0);
  v5 := LuaOptNumber(L, 5, 0.0);
  id := NextId('Add_Lamp');
  PhysAddLamp(id, v2, v3, v4, v5);
  Lua.PushInteger(L, id);
  Result := 1;
  LuaLogEnd(id);
end;

function bind_Add_PropellerFan(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: Double;
  v3: Double;
  v4: Double;
  v5: Double;
begin
  LuaLogBegin(L, 'Add_PropellerFan');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptNumber(L, 2, 0.0);
  v3 := LuaOptNumber(L, 3, 0.0);
  v4 := LuaOptNumber(L, 4, 0.0);
  v5 := LuaOptNumber(L, 5, 0.0);
  id := NextId('Add_PropellerFan');
  Lua.PushInteger(L, id);
  Result := 1;
  LuaLogEnd(id);
end;

function bind_Add_Magnet(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: Double;
  v3: Double;
  v4: Double;
  v5: Double;
begin
  LuaLogBegin(L, 'Add_Magnet');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptNumber(L, 2, 0.0);
  v3 := LuaOptNumber(L, 3, 0.0);
  v4 := LuaOptNumber(L, 4, 0.0);
  v5 := LuaOptNumber(L, 5, 0.0);
  id := NextId('Add_Magnet');
  PhysAddMagnet(id, v2, v3, v4, v5);
  Lua.PushInteger(L, id);
  Result := 1;
  LuaLogEnd(id);
end;

function bind_Add_WoodDetail(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: Double;
  v3: Double;
  v4: Double;
  v5: Double;
begin
  LuaLogBegin(L, 'Add_WoodDetail');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptNumber(L, 2, 0.0);
  v3 := LuaOptNumber(L, 3, 0.0);
  v4 := LuaOptNumber(L, 4, 0.0);
  v5 := LuaOptNumber(L, 5, 0.0);
  id := NextId('Add_WoodDetail');
  PhysAddWoodDetail(id, v2, v3, v4, v5);
  Lua.PushInteger(L, id);
  Result := 1;
  LuaLogEnd(id);
end;

function bind_Add_ToothGear(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: Double;
  v3: Double;
  v4: Double;
  v5: Double;
begin
  LuaLogBegin(L, 'Add_ToothGear');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptNumber(L, 2, 0.0);
  v3 := LuaOptNumber(L, 3, 0.0);
  v4 := LuaOptNumber(L, 4, 0.0);
  v5 := LuaOptNumber(L, 5, 0.0);
  id := NextId('Add_ToothGear');
  PhysAddToothGear(id, v2, v3, v4, v5);
  Lua.PushInteger(L, id);
  Result := 1;
  LuaLogEnd(id);
end;

function bind_Add_ShankBody(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: Double;
  v3: Double;
  v4: Double;
  v5: Double;
begin
  LuaLogBegin(L, 'Add_ShankBody');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptNumber(L, 2, 0.0);
  v3 := LuaOptNumber(L, 3, 0.0);
  v4 := LuaOptNumber(L, 4, 0.0);
  v5 := LuaOptNumber(L, 5, 0.0);
  id := NextId('Add_ShankBody');
  PhysAddShankBody(id, v2, v3, v4, v5);
  Lua.PushInteger(L, id);
  Result := 1;
  LuaLogEnd(id);
end;

function bind_Add_Barrel(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: Double;
  v3: Double;
  v4: Double;
  v5: Double;
begin
  LuaLogBegin(L, 'Add_Barrel');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptNumber(L, 2, 0.0);
  v3 := LuaOptNumber(L, 3, 0.0);
  v4 := LuaOptNumber(L, 4, 0.0);
  v5 := LuaOptNumber(L, 5, 0.0);
  id := NextId('Add_Barrel');
  Lua.PushInteger(L, id);
  Result := 1;
  LuaLogEnd(id);
end;

function bind_Add_PushButton(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: Double;
  v3: Double;
  v4: Double;
  v5: Double;
begin
  LuaLogBegin(L, 'Add_PushButton');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptNumber(L, 2, 0.0);
  v3 := LuaOptNumber(L, 3, 0.0);
  v4 := LuaOptNumber(L, 4, 0.0);
  v5 := LuaOptNumber(L, 5, 0.0);
  id := NextId('Add_PushButton');
  PhysAddPushButton(id, v2, v3, v4, v5);
  Lua.PushInteger(L, id);
  Result := 1;
  LuaLogEnd(id);
end;

function bind_Add_FlyAwayLockIcon(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: Double;
  v3: Double;
  v4: Double;
  v5: Double;
begin
  LuaLogBegin(L, 'Add_FlyAwayLockIcon');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptNumber(L, 2, 0.0);
  v3 := LuaOptNumber(L, 3, 0.0);
  v4 := LuaOptNumber(L, 4, 0.0);
  v5 := LuaOptNumber(L, 5, 0.0);
  id := NextId('Add_FlyAwayLockIcon');
  Lua.PushInteger(L, id);
  Result := 1;
  LuaLogEnd(id);
end;

function bind_Add_SpiderWeb(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: Double;
  v3: Double;
  v4: Double;
  v5: Double;
begin
  LuaLogBegin(L, 'Add_SpiderWeb');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptNumber(L, 2, 0.0);
  v3 := LuaOptNumber(L, 3, 0.0);
  v4 := LuaOptNumber(L, 4, 0.0);
  v5 := LuaOptNumber(L, 5, 0.0);
  id := NextId('Add_SpiderWeb');
  Lua.PushInteger(L, id);
  Result := 1;
  LuaLogEnd(id);
end;

function bind_Get_PhysObjByIndex(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Double;
begin
  LuaLogBegin(L, 'Get_PhysObjByIndex');
  v1 := LuaOptNumber(L, 1, 0.0);
  id := NextId('Get_PhysObjByIndex');
  Lua.PushInteger(L, id);
  Result := 1;
  LuaLogEnd(id);
end;

function bind_Add_JointNail(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: Integer;
  v3: Integer;
  v4: Double;
  v5: Double;
begin
  LuaLogBegin(L, 'Add_JointNail');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptInt(L, 2, 0);
  v3 := LuaOptInt(L, 3, 0);
  v4 := LuaOptNumber(L, 4, 0.0);
  v5 := LuaOptNumber(L, 5, 0.0);
  id := NextId('Add_JointNail');
  PhysAddJointNail(id, v2, v3, v4, v5);
  Lua.PushInteger(L, id);
  Result := 1;
  LuaLogEnd(id);
end;

function bind_Add_JointNailToStatic(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: Integer;
  v3: Double;
  v4: Double;
begin
  LuaLogBegin(L, 'Add_JointNailToStatic');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptInt(L, 2, 0);
  v3 := LuaOptNumber(L, 3, 0.0);
  v4 := LuaOptNumber(L, 4, 0.0);
  id := NextId('Add_JointNailToStatic');
  Lua.PushInteger(L, id);
  Result := 1;
  LuaLogEnd(id);
end;

function bind_Add_JointSkid(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: Integer;
  v3: Integer;
  v4: Double;
  v5: Double;
  v6: Double;
  v7: Double;
begin
  LuaLogBegin(L, 'Add_JointSkid');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptInt(L, 2, 0);
  v3 := LuaOptInt(L, 3, 0);
  v4 := LuaOptNumber(L, 4, 0.0);
  v5 := LuaOptNumber(L, 5, 0.0);
  v6 := LuaOptNumber(L, 6, 0.0);
  v7 := LuaOptNumber(L, 7, 0.0);
  id := NextId('Add_JointSkid');
  Lua.PushInteger(L, id);
  Result := 1;
  LuaLogEnd(id);
end;

function bind_Add_JointShank(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: Integer;
  v3: Integer;
  v4: Double;
  v5: Double;
  v6: Double;
  v7: Double;
begin
  LuaLogBegin(L, 'Add_JointShank');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptInt(L, 2, 0);
  v3 := LuaOptInt(L, 3, 0);
  v4 := LuaOptNumber(L, 4, 0.0);
  v5 := LuaOptNumber(L, 5, 0.0);
  v6 := LuaOptNumber(L, 6, 0.0);
  v7 := LuaOptNumber(L, 7, 0.0);
  id := NextId('Add_JointShank');
  Lua.PushInteger(L, id);
  Result := 1;
  LuaLogEnd(id);
end;

function bind_Add_JointDistance(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: Integer;
  v3: Integer;
  v4: Double;
  v5: Double;
  v6: Double;
  v7: Double;
  v8: Double;
begin
  LuaLogBegin(L, 'Add_JointDistance');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptInt(L, 2, 0);
  v3 := LuaOptInt(L, 3, 0);
  v4 := LuaOptNumber(L, 4, 0.0);
  v5 := LuaOptNumber(L, 5, 0.0);
  v6 := LuaOptNumber(L, 6, 0.0);
  v7 := LuaOptNumber(L, 7, 0.0);
  v8 := LuaOptNumber(L, 8, 0.0);
  id := NextId('Add_JointDistance');
  Lua.PushInteger(L, id);
  Result := 1;
  LuaLogEnd(id);
end;

function bind_Flip_GraphObjectX(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
begin
  LuaLogBegin(L, 'Flip_GraphObjectX');
  v1 := LuaOptInt(L, 1, 0);
  id := NextId('Flip_GraphObjectX');
  Lua.PushNumber(L, id);
  Result := 1;
  LuaLogEnd(id);
end;

function bind_Flip_GraphObjectY(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
begin
  LuaLogBegin(L, 'Flip_GraphObjectY');
  v1 := LuaOptInt(L, 1, 0);
  id := NextId('Flip_GraphObjectY');
  Lua.PushNumber(L, id);
  Result := 1;
  LuaLogEnd(id);
end;

function bind_Set_FlipGraphObject(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v2: Double;
  v3: Double;
begin
  LuaLogBegin(L, 'Set_FlipGraphObject');
  v2 := LuaOptNumber(L, 2, 0.0);
  v3 := LuaOptNumber(L, 3, 0.0);
  id := NextId('Set_FlipGraphObject');
  Lua.PushNumber(L, id);
  Result := 1;
  LuaLogEnd(id);
end;

function bind_Add_JointSimpleGear(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: Integer;
  v3: Integer;
  v4: Integer;
  v5: Double;
begin
  LuaLogBegin(L, 'Add_JointSimpleGear');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptInt(L, 2, 0);
  v3 := LuaOptInt(L, 3, 0);
  v4 := LuaOptInt(L, 4, 0);
  v5 := LuaOptNumber(L, 5, 0.0);
  id := NextId('Add_JointSimpleGear');
  PhysAddJointSimpleGear(id, v1, v2, v3, v4, v5);
  Lua.PushInteger(L, id);
  Result := 1;
  LuaLogEnd(id);
end;

function bind_Add_JointSimplePulley(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: Integer;
  v3: Double;
  v4: Double;
  v5: Double;
  v6: Double;
  v7: Double;
  v8: Double;
  v9: Double;
  v10: Double;
  v11: Double;
  v12: Double;
  v13: Double;
begin
  LuaLogBegin(L, 'Add_JointSimplePulley');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptInt(L, 2, 0);
  v3 := LuaOptNumber(L, 3, 0.0);
  v4 := LuaOptNumber(L, 4, 0.0);
  v5 := LuaOptNumber(L, 5, 0.0);
  v6 := LuaOptNumber(L, 6, 0.0);
  v7 := LuaOptNumber(L, 7, 0.0);
  v8 := LuaOptNumber(L, 8, 0.0);
  v9 := LuaOptNumber(L, 9, 0.0);
  v10 := LuaOptNumber(L, 10, 0.0);
  v11 := LuaOptNumber(L, 11, 0.0);
  v12 := LuaOptNumber(L, 12, 0.0);
  v13 := LuaOptNumber(L, 13, 0.0);
  id := NextId('Add_JointSimplePulley');
  Lua.PushInteger(L, id);
  Result := 1;
  LuaLogEnd(id);
end;

function bind_Add_JointSimplePrismatic(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: Integer;
  v3: Double;
  v4: Double;
  v5: Double;
  v6: Double;
begin
  LuaLogBegin(L, 'Add_JointSimplePrismatic');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptInt(L, 2, 0);
  v3 := LuaOptNumber(L, 3, 0.0);
  v4 := LuaOptNumber(L, 4, 0.0);
  v5 := LuaOptNumber(L, 5, 0.0);
  v6 := LuaOptNumber(L, 6, 0.0);
  id := NextId('Add_JointSimplePrismatic');
  PhysAddJointSimplePrismatic(id, v1, v2, v3, v4, v5, v6);
  Lua.PushInteger(L, id);
  Result := 1;
  LuaLogEnd(id);
end;

function bind_Add_JointSimpleRevolute(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: Integer;
  v3: Double;
  v4: Double;
begin
  LuaLogBegin(L, 'Add_JointSimpleRevolute');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptInt(L, 2, 0);
  v3 := LuaOptNumber(L, 3, 0.0);
  v4 := LuaOptNumber(L, 4, 0.0);
  id := NextId('Add_JointSimpleRevolute');
  PhysAddJointSimpleRevolute(id, v1, v2, v3, v4);
  Lua.PushInteger(L, id);
  Result := 1;
  LuaLogEnd(id);
end;

function bind_Add_GraphSprite(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: Double;
  v3: Double;
  v4: Double;
  v5: Double;
  v6: Double;
  v7: PChar;
begin
  LuaLogBegin(L, 'Add_GraphSprite');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptNumber(L, 2, 0.0);
  v3 := LuaOptNumber(L, 3, 0.0);
  v4 := LuaOptNumber(L, 4, 0.0);
  v5 := LuaOptNumber(L, 5, 0.0);
  v6 := LuaOptNumber(L, 6, 0.0);
  v7 := LuaOptStr(L, 7);
  id := NextId('Add_GraphSprite');
  Lua.PushInteger(L, id);
  Result := 1;
  LuaLogEnd(id);
end;

function bind_Add_HudGraphSprite(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: Double;
  v3: Double;
  v4: Double;
  v5: Double;
  v6: Double;
  v7: PChar;
begin
  LuaLogBegin(L, 'Add_HudGraphSprite');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptNumber(L, 2, 0.0);
  v3 := LuaOptNumber(L, 3, 0.0);
  v4 := LuaOptNumber(L, 4, 0.0);
  v5 := LuaOptNumber(L, 5, 0.0);
  v6 := LuaOptNumber(L, 6, 0.0);
  v7 := LuaOptStr(L, 7);
  id := NextId('Add_HudGraphSprite');
  Lua.PushInteger(L, id);
  Result := 1;
  LuaLogEnd(id);
end;

function bind_Add_AlphaDoubleSprite(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: Double;
  v3: Double;
  v4: Double;
  v5: Double;
  v6: Double;
  v7: PChar;
  v8: PChar;
begin
  LuaLogBegin(L, 'Add_AlphaDoubleSprite');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptNumber(L, 2, 0.0);
  v3 := LuaOptNumber(L, 3, 0.0);
  v4 := LuaOptNumber(L, 4, 0.0);
  v5 := LuaOptNumber(L, 5, 0.0);
  v6 := LuaOptNumber(L, 6, 0.0);
  v7 := LuaOptStr(L, 7);
  v8 := LuaOptStr(L, 8);
  id := NextId('Add_AlphaDoubleSprite');
  Lua.PushInteger(L, id);
  Result := 1;
  LuaLogEnd(id);
end;

function bind_Add_ExtAlphaDoubleSprite(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: Double;
  v3: Double;
  v4: Double;
  v5: Double;
  v6: Double;
  v7: Double;
  v8: Double;
  v9: PChar;
  v10: PChar;
begin
  LuaLogBegin(L, 'Add_ExtAlphaDoubleSprite');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptNumber(L, 2, 0.0);
  v3 := LuaOptNumber(L, 3, 0.0);
  v4 := LuaOptNumber(L, 4, 0.0);
  v5 := LuaOptNumber(L, 5, 0.0);
  v6 := LuaOptNumber(L, 6, 0.0);
  v7 := LuaOptNumber(L, 7, 0.0);
  v8 := LuaOptNumber(L, 8, 0.0);
  v9 := LuaOptStr(L, 9);
  v10 := LuaOptStr(L, 10);
  id := NextId('Add_ExtAlphaDoubleSprite');
  Lua.PushInteger(L, id);
  Result := 1;
  LuaLogEnd(id);
end;

function bind_Add_SpringSprite(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: Double;
  v3: Double;
  v4: Double;
  v5: Double;
  v6: Double;
begin
  LuaLogBegin(L, 'Add_SpringSprite');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptNumber(L, 2, 0.0);
  v3 := LuaOptNumber(L, 3, 0.0);
  v4 := LuaOptNumber(L, 4, 0.0);
  v5 := LuaOptNumber(L, 5, 0.0);
  v6 := LuaOptNumber(L, 6, 0.0);
  id := NextId('Add_SpringSprite');
  Lua.PushInteger(L, id);
  Result := 1;
  LuaLogEnd(id);
end;

function bind_Add_GearChalkSprite(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: Double;
  v3: Double;
  v4: Double;
  v5: Double;
begin
  LuaLogBegin(L, 'Add_GearChalkSprite');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptNumber(L, 2, 0.0);
  v3 := LuaOptNumber(L, 3, 0.0);
  v4 := LuaOptNumber(L, 4, 0.0);
  v5 := LuaOptNumber(L, 5, 0.0);
  id := NextId('Add_GearChalkSprite');
  Lua.PushInteger(L, id);
  Result := 1;
  LuaLogEnd(id);
end;

function bind_Add_AnimateSmoke(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: Double;
  v3: Double;
  v4: Double;
  v5: Double;
  v6: Integer;
begin
  LuaLogBegin(L, 'Add_AnimateSmoke');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptNumber(L, 2, 0.0);
  v3 := LuaOptNumber(L, 3, 0.0);
  v4 := LuaOptNumber(L, 4, 0.0);
  v5 := LuaOptNumber(L, 5, 0.0);
  v6 := LuaOptInt(L, 6, 0);
  id := NextId('Add_AnimateSmoke');
  Lua.PushInteger(L, id);
  Result := 1;
  LuaLogEnd(id);
end;

function bind_Add_AnimateHUDSmoke(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: Double;
  v3: Double;
  v4: Double;
  v5: Double;
  v6: Integer;
begin
  LuaLogBegin(L, 'Add_AnimateHUDSmoke');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptNumber(L, 2, 0.0);
  v3 := LuaOptNumber(L, 3, 0.0);
  v4 := LuaOptNumber(L, 4, 0.0);
  v5 := LuaOptNumber(L, 5, 0.0);
  v6 := LuaOptInt(L, 6, 0);
  id := NextId('Add_AnimateHUDSmoke');
  Lua.PushInteger(L, id);
  Result := 1;
  LuaLogEnd(id);
end;

function bind_Add_AlphaHint(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: Double;
  v3: Double;
  v4: Double;
  v5: Double;
  v6: Double;
  v7: PChar;
begin
  LuaLogBegin(L, 'Add_AlphaHint');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptNumber(L, 2, 0.0);
  v3 := LuaOptNumber(L, 3, 0.0);
  v4 := LuaOptNumber(L, 4, 0.0);
  v5 := LuaOptNumber(L, 5, 0.0);
  v6 := LuaOptNumber(L, 6, 0.0);
  v7 := LuaOptStr(L, 7);
  id := NextId('Add_AlphaHint');
  Lua.PushInteger(L, id);
  Result := 1;
  LuaLogEnd(id);
end;

function bind_Add_AlphaHudSprite(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: Double;
  v3: Double;
  v4: Double;
  v5: Double;
  v6: Double;
  v7: PChar;
begin
  LuaLogBegin(L, 'Add_AlphaHudSprite');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptNumber(L, 2, 0.0);
  v3 := LuaOptNumber(L, 3, 0.0);
  v4 := LuaOptNumber(L, 4, 0.0);
  v5 := LuaOptNumber(L, 5, 0.0);
  v6 := LuaOptNumber(L, 6, 0.0);
  v7 := LuaOptStr(L, 7);
  id := NextId('Add_AlphaHudSprite');
  Lua.PushInteger(L, id);
  Result := 1;
  LuaLogEnd(id);
end;

function bind_Add_MovingPipe(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: Double;
  v3: Double;
  v4: Double;
  v5: Double;
begin
  LuaLogBegin(L, 'Add_MovingPipe');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptNumber(L, 2, 0.0);
  v3 := LuaOptNumber(L, 3, 0.0);
  v4 := LuaOptNumber(L, 4, 0.0);
  v5 := LuaOptNumber(L, 5, 0.0);
  id := NextId('Add_MovingPipe');
  Lua.PushInteger(L, id);
  Result := 1;
  LuaLogEnd(id);
end;

function bind_Destroy_Joint(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
begin
  LuaLogBegin(L, 'Destroy_Joint');
  v1 := LuaOptInt(L, 1, 0);
  id := NextId('Destroy_Joint');
  Result := 0;
  LuaLogEnd(id);
end;

function bind_Destroy_Body(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
begin
  LuaLogBegin(L, 'Destroy_Body');
  v1 := LuaOptInt(L, 1, 0);
  id := NextId('Destroy_Body');
  Result := 0;
  LuaLogEnd(id);
end;

function bind_Add_SimplePhysicObject(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Double;
  v2: Double;
  v3: Double;
begin
  LuaLogBegin(L, 'Add_SimplePhysicObject');
  v1 := LuaOptNumber(L, 1, 0.0);
  v2 := LuaOptNumber(L, 2, 0.0);
  v3 := LuaOptNumber(L, 3, 0.0);
  id := NextId('Add_SimplePhysicObject');
  PhysAddSimplePhysicObject(id, v1, v2, v3);
  Lua.PushInteger(L, id);
  Result := 1;
  LuaLogEnd(id);
end;

function bind_Add_SimplePhysCircle(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Double;
  v2: Double;
  v3: Double;
  v4: Double;
  v5: Double;
  v6: Double;
begin
  LuaLogBegin(L, 'Add_SimplePhysCircle');
  v1 := LuaOptNumber(L, 1, 0.0);
  v2 := LuaOptNumber(L, 2, 0.0);
  v3 := LuaOptNumber(L, 3, 0.0);
  v4 := LuaOptNumber(L, 4, 0.0);
  v5 := LuaOptNumber(L, 5, 0.0);
  v6 := LuaOptNumber(L, 6, 0.0);
  id := NextId('Add_SimplePhysCircle');
  PhysAddSimplePhysCircle(id, v1, v2, v3, v4, v5, v6);
  Lua.PushInteger(L, id);
  Result := 1;
  LuaLogEnd(id);
end;

function bind_Add_SimpleButton(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: Double;
  v3: Double;
  v4: Double;
  v5: Double;
  v6: Double;
  v7: PChar;
  v8: PChar;
begin
  LuaLogBegin(L, 'Add_SimpleButton');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptNumber(L, 2, 0.0);
  v3 := LuaOptNumber(L, 3, 0.0);
  v4 := LuaOptNumber(L, 4, 0.0);
  v5 := LuaOptNumber(L, 5, 0.0);
  v6 := LuaOptNumber(L, 6, 0.0);
  v7 := LuaOptStr(L, 7);
  v8 := LuaOptStr(L, 8);
  id := NextId('Add_SimpleButton');
  Lua.PushInteger(L, id);
  Result := 1;
  LuaLogEnd(id);
end;

function bind_Add_HudButton(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: Double;
  v3: Double;
  v4: Double;
  v5: Double;
  v6: Double;
  v7: PChar;
  v8: PChar;
begin
  LuaLogBegin(L, 'Add_HudButton');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptNumber(L, 2, 0.0);
  v3 := LuaOptNumber(L, 3, 0.0);
  v4 := LuaOptNumber(L, 4, 0.0);
  v5 := LuaOptNumber(L, 5, 0.0);
  v6 := LuaOptNumber(L, 6, 0.0);
  v7 := LuaOptStr(L, 7);
  v8 := LuaOptStr(L, 8);
  id := NextId('Add_HudButton');
  Lua.PushInteger(L, id);
  Result := 1;
  LuaLogEnd(id);
end;

function bind_Add_NextButton(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: Double;
  v3: Double;
  v4: Double;
  v5: Double;
begin
  LuaLogBegin(L, 'Add_NextButton');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptNumber(L, 2, 0.0);
  v3 := LuaOptNumber(L, 3, 0.0);
  v4 := LuaOptNumber(L, 4, 0.0);
  v5 := LuaOptNumber(L, 5, 0.0);
  id := NextId('Add_NextButton');
  Lua.PushInteger(L, id);
  Result := 1;
  LuaLogEnd(id);
end;

function bind_Add_CloseButton(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: Double;
  v3: Double;
  v4: Double;
  v5: Double;
begin
  LuaLogBegin(L, 'Add_CloseButton');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptNumber(L, 2, 0.0);
  v3 := LuaOptNumber(L, 3, 0.0);
  v4 := LuaOptNumber(L, 4, 0.0);
  v5 := LuaOptNumber(L, 5, 0.0);
  id := NextId('Add_CloseButton');
  Lua.PushInteger(L, id);
  Result := 1;
  LuaLogEnd(id);
end;

function bind_Do_ShowCommand(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
begin
  LuaLogBegin(L, 'Do_ShowCommand');
  v1 := LuaOptInt(L, 1, 0);
  id := NextId('Do_ShowCommand');
  Result := 0;
  LuaLogEnd(id);
end;

function bind_Do_HideCommand(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
begin
  LuaLogBegin(L, 'Do_HideCommand');
  v1 := LuaOptInt(L, 1, 0);
  id := NextId('Do_HideCommand');
  Result := 0;
  LuaLogEnd(id);
end;

function bind_Add_SimpleTimer(L: TLuaState): Integer; cdecl;
var
  id: Integer;
begin
  LuaLogBegin(L, 'Add_SimpleTimer');
  id := NextId('Add_SimpleTimer');
  Lua.PushInteger(L, id);
  Result := 1;
  LuaLogEnd(id);
end;

function bind_Start_Timer(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: Double;
begin
  LuaLogBegin(L, 'Start_Timer');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptNumber(L, 2, 0.0);
  id := NextId('Start_Timer');
  Result := 0;
  LuaLogEnd(id);
end;

function bind_Set_GlobalVar(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: PChar;
  v2: Double;
begin
  LuaLogBegin(L, 'Set_GlobalVar');
  v1 := LuaOptStr(L, 1);
  v2 := LuaOptNumber(L, 2, 0.0);
  id := NextId('Set_GlobalVar');
  Result := 0;
  LuaLogEnd(id);
end;

function bind_Set_ScrObjPos(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: Double;
  v3: Double;
  v4: Double;
begin
  LuaLogBegin(L, 'Set_ScrObjPos');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptNumber(L, 2, 0.0);
  v3 := LuaOptNumber(L, 3, 0.0);
  v4 := LuaOptNumber(L, 4, 0.0);
  id := NextId('Set_ScrObjPos');
  PhysSetBodyPos(v1, v2, v3, v4);
  Result := 0;
  LuaLogEnd(id);
end;

function bind_Get_ScrObjPos(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  gx, gy, ga: Double;
begin
  LuaLogBegin(L, 'Get_ScrObjPos');
  v1 := LuaOptInt(L, 1, 0);
  id := NextId('Get_ScrObjPos');
  PhysGetBodyPos(v1, gx, gy, ga);
  Lua.PushNumber(L, gx);
  Lua.PushNumber(L, gy);
  Lua.PushNumber(L, ga);
  Result := 3;
  LuaLogEnd(id);
end;

function bind_Local_ToWorld(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: Double;
  v3: Double;
begin
  LuaLogBegin(L, 'Local_ToWorld');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptNumber(L, 2, 0.0);
  v3 := LuaOptNumber(L, 3, 0.0);
  id := NextId('Local_ToWorld');
  Lua.PushNumber(L, id);
  Lua.PushNumber(L, 0);
  Result := 2;
  LuaLogEnd(id);
end;

function bind_World_ToLocal(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: Double;
  v3: Double;
begin
  LuaLogBegin(L, 'World_ToLocal');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptNumber(L, 2, 0.0);
  v3 := LuaOptNumber(L, 3, 0.0);
  id := NextId('World_ToLocal');
  Lua.PushNumber(L, id);
  Lua.PushNumber(L, 0);
  Result := 2;
  LuaLogEnd(id);
end;

function bind_Set_PhysSensor(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: Integer;
begin
  LuaLogBegin(L, 'Set_PhysSensor');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptInt(L, 2, 0);
  id := NextId('Set_PhysSensor');
  Result := 0;
  LuaLogEnd(id);
end;

function bind_Set_PhysBullet(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: Integer;
begin
  LuaLogBegin(L, 'Set_PhysBullet');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptInt(L, 2, 0);
  id := NextId('Set_PhysBullet');
  Result := 0;
  LuaLogEnd(id);
end;

function bind_Set_PhysFilterData(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: Integer;
  v3: Integer;
  v4: Integer;
begin
  LuaLogBegin(L, 'Set_PhysFilterData');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptInt(L, 2, 0);
  v3 := LuaOptInt(L, 3, 0);
  v4 := LuaOptInt(L, 4, 0);
  id := NextId('Set_PhysFilterData');
  PhysSetPhysFilter(v1, v2, v3, v4);
  Result := 0;
  LuaLogEnd(id);
end;

function bind_Re_Filter(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
begin
  LuaLogBegin(L, 'Re_Filter');
  v1 := LuaOptInt(L, 1, 0);
  id := NextId('Re_Filter');
  PhysReFilter(v1);
  Result := 0;
  LuaLogEnd(id);
end;

function bind_Set_PhysThresholdPlayerForce(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: Double;
begin
  LuaLogBegin(L, 'Set_PhysThresholdPlayerForce');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptNumber(L, 2, 0.0);
  id := NextId('Set_PhysThresholdPlayerForce');
  Result := 0;
  LuaLogEnd(id);
end;

function bind_Set_PhysParams(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: Double;
  v3: Double;
  v4: Double;
begin
  LuaLogBegin(L, 'Set_PhysParams');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptNumber(L, 2, 0.0);
  v3 := LuaOptNumber(L, 3, 0.0);
  v4 := LuaOptNumber(L, 4, 0.0);
  id := NextId('Set_PhysParams');
  PhysSetPhysParams(v1, v2, v3, v4);
  Result := 0;
  LuaLogEnd(id);
end;

function bind_Get_PhysParams(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  gx, gy, ga: Double;
begin
  LuaLogBegin(L, 'Get_PhysParams');
  v1 := LuaOptInt(L, 1, 0);
  id := NextId('Get_PhysParams');
  PhysGetPhysParams(v1, gx, gy, ga);
  Lua.PushNumber(L, gx);
  Lua.PushNumber(L, gy);
  Lua.PushNumber(L, ga);
  Result := 3;
  LuaLogEnd(id);
end;

function bind_Set_ExtPhysParams(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: Double;
  v3: Double;
  v4: Double;
begin
  LuaLogBegin(L, 'Set_ExtPhysParams');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptNumber(L, 2, 0.0);
  v3 := LuaOptNumber(L, 3, 0.0);
  v4 := LuaOptNumber(L, 4, 0.0);
  id := NextId('Set_ExtPhysParams');
  Result := 0;
  LuaLogEnd(id);
end;

function bind_Set_PhysDamping(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: Double;
  v3: Double;
begin
  LuaLogBegin(L, 'Set_PhysDamping');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptNumber(L, 2, 0.0);
  v3 := LuaOptNumber(L, 3, 0.0);
  id := NextId('Set_PhysDamping');
  Result := 0;
  LuaLogEnd(id);
end;

function bind_Set_DebugPosition(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Double;
  v2: Double;
begin
  LuaLogBegin(L, 'Set_DebugPosition');
  v1 := LuaOptNumber(L, 1, 0.0);
  v2 := LuaOptNumber(L, 2, 0.0);
  id := NextId('Set_DebugPosition');
  Result := 0;
  LuaLogEnd(id);
end;

function bind_Set_DebugText(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Double;
begin
  LuaLogBegin(L, 'Set_DebugText');
  v1 := LuaOptNumber(L, 1, 0.0);
  id := NextId('Set_DebugText');
  Result := 0;
  LuaLogEnd(id);
end;

function bind_Set_JointLimits(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: Double;
  v3: Double;
  v4: Double;
begin
  LuaLogBegin(L, 'Set_JointLimits');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptNumber(L, 2, 0.0);
  v3 := LuaOptNumber(L, 3, 0.0);
  v4 := LuaOptNumber(L, 4, 0.0);
  id := NextId('Set_JointLimits');
  PhysSetJointLimits(v1, v2 <> 0.0, v3, v4);
  Result := 0;
  LuaLogEnd(id);
end;

function bind_Get_JointLimits(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
begin
  LuaLogBegin(L, 'Get_JointLimits');
  v1 := LuaOptInt(L, 1, 0);
  id := NextId('Get_JointLimits');
  Lua.PushNumber(L, id);
  Lua.PushNumber(L, 0);
  Lua.PushNumber(L, 0);
  Result := 3;
  LuaLogEnd(id);
end;

function bind_Set_JointMotors(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: Double;
  v3: Double;
  v4: Double;
begin
  LuaLogBegin(L, 'Set_JointMotors');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptNumber(L, 2, 0.0);
  v3 := LuaOptNumber(L, 3, 0.0);
  v4 := LuaOptNumber(L, 4, 0.0);
  id := NextId('Set_JointMotors');
  PhysSetJointMotors(v1, v2 <> 0.0, v3, v4);
  Result := 0;
  LuaLogEnd(id);
end;

function bind_Get_JointMotors(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
begin
  LuaLogBegin(L, 'Get_JointMotors');
  v1 := LuaOptInt(L, 1, 0);
  id := NextId('Get_JointMotors');
  Lua.PushNumber(L, id);
  Lua.PushNumber(L, 0);
  Lua.PushNumber(L, 0);
  Result := 3;
  LuaLogEnd(id);
end;

function bind_Get_JointAngle(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
begin
  LuaLogBegin(L, 'Get_JointAngle');
  v1 := LuaOptInt(L, 1, 0);
  id := NextId('Get_JointAngle');
  Lua.PushNumber(L, id);
  Result := 1;
  LuaLogEnd(id);
end;

function bind_Get_JointTranslation(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
begin
  LuaLogBegin(L, 'Get_JointTranslation');
  v1 := LuaOptInt(L, 1, 0);
  id := NextId('Get_JointTranslation');
  Lua.PushNumber(L, id);
  Result := 1;
  LuaLogEnd(id);
end;

function bind_Clear_JustCreationFlag(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
begin
  LuaLogBegin(L, 'Clear_JustCreationFlag');
  v1 := LuaOptInt(L, 1, 0);
  id := NextId('Clear_JustCreationFlag');
  Result := 0;
  LuaLogEnd(id);
end;

function bind_Apply_PhysImpulse(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: Double;
  v3: Double;
begin
  LuaLogBegin(L, 'Apply_PhysImpulse');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptNumber(L, 2, 0.0);
  v3 := LuaOptNumber(L, 3, 0.0);
  id := NextId('Apply_PhysImpulse');
  Result := 0;
  LuaLogEnd(id);
end;

function bind_Set_PhysVelocity(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: Double;
  v3: Double;
begin
  LuaLogBegin(L, 'Set_PhysVelocity');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptNumber(L, 2, 0.0);
  v3 := LuaOptNumber(L, 3, 0.0);
  id := NextId('Set_PhysVelocity');
  Result := 0;
  LuaLogEnd(id);
end;

function bind_Get_PhysVelocity(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
begin
  LuaLogBegin(L, 'Get_PhysVelocity');
  v1 := LuaOptInt(L, 1, 0);
  id := NextId('Get_PhysVelocity');
  Lua.PushNumber(L, id);
  Lua.PushNumber(L, 0);
  Result := 2;
  LuaLogEnd(id);
end;

function bind_Apply_PhysForce(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: Double;
  v3: Double;
begin
  LuaLogBegin(L, 'Apply_PhysForce');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptNumber(L, 2, 0.0);
  v3 := LuaOptNumber(L, 3, 0.0);
  id := NextId('Apply_PhysForce');
  Result := 0;
  LuaLogEnd(id);
end;

function bind_Apply_PhysForceAtPos(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: Double;
  v3: Double;
  v4: Double;
  v5: Double;
begin
  LuaLogBegin(L, 'Apply_PhysForceAtPos');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptNumber(L, 2, 0.0);
  v3 := LuaOptNumber(L, 3, 0.0);
  v4 := LuaOptNumber(L, 4, 0.0);
  v5 := LuaOptNumber(L, 5, 0.0);
  id := NextId('Apply_PhysForceAtPos');
  Result := 0;
  LuaLogEnd(id);
end;

function bind_Attach_ShapeCircle(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: Double;
  v3: Double;
  v4: Double;
  v5: Double;
  v6: Double;
  v7: Double;
begin
  LuaLogBegin(L, 'Attach_ShapeCircle');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptNumber(L, 2, 0.0);
  v3 := LuaOptNumber(L, 3, 0.0);
  v4 := LuaOptNumber(L, 4, 0.0);
  v5 := LuaOptNumber(L, 5, 0.0);
  v6 := LuaOptNumber(L, 6, 0.0);
  v7 := LuaOptNumber(L, 7, 0.0);
  id := NextId('Attach_ShapeCircle');
  PhysAttachShapeCircle(v1, v2, v3, v4, v5, v6, v7);
  Result := 0;
  LuaLogEnd(id);
end;

function bind_Attach_ShapePolygon(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: Double;
  v3: Double;
  v4: Double;
  v5: Integer;
  n, i: Integer;
  d: Double;
  pts: array[0..15] of Double;
begin
  LuaLogBegin(L, 'Attach_ShapePolygon');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptNumber(L, 2, 0.0);
  v3 := LuaOptNumber(L, 3, 0.0);
  v4 := LuaOptNumber(L, 4, 0.0);
  v5 := LuaOptInt(L, 5, 0);
  n := v5;
  for i := 0 to n - 1 do
  begin
    d := LuaOptNumber(L, 6 + 2 * i, 0.0);
    pts[2 * i] := d;
    d := LuaOptNumber(L, 7 + 2 * i, 0.0);
    pts[2 * i + 1] := d;
  end;
  id := NextId('Attach_ShapePolygon');
  PhysAttachShapePolygon(v1, v2, v3, v4, v5, @pts[0]);
  Result := 0;
  LuaLogEnd(id);
end;

function bind_Attach_SimpleGraphObject(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: Integer;
  v3: Double;
  v4: Double;
  v5: PChar;
begin
  LuaLogBegin(L, 'Attach_SimpleGraphObject');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptInt(L, 2, 0);
  v3 := LuaOptNumber(L, 3, 0.0);
  v4 := LuaOptNumber(L, 4, 0.0);
  v5 := LuaOptStr(L, 5);
  id := NextId('Attach_SimpleGraphObject');
  Result := 0;
  LuaLogEnd(id);
end;

function bind_Add_PhysicObjectWithAdvGraph(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Double;
  v2: Double;
  v3: Double;
  v4: Double;
  v5: Double;
begin
  LuaLogBegin(L, 'Add_PhysicObjectWithAdvGraph');
  v1 := LuaOptNumber(L, 1, 0.0);
  v2 := LuaOptNumber(L, 2, 0.0);
  v3 := LuaOptNumber(L, 3, 0.0);
  v4 := LuaOptNumber(L, 4, 0.0);
  v5 := LuaOptNumber(L, 5, 0.0);
  id := NextId('Add_PhysicObjectWithAdvGraph');
  PhysAddPhysicObjectWithAdvGraph(id, v1, v2, v3);
  Lua.PushInteger(L, id);
  Result := 1;
  LuaLogEnd(id);
end;

function bind_Get_GraphObject(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
begin
  LuaLogBegin(L, 'Get_GraphObject');
  v1 := LuaOptInt(L, 1, 0);
  id := NextId('Get_GraphObject');
  Lua.PushInteger(L, id);
  Result := 1;
  LuaLogEnd(id);
end;

function bind_Attach_AlphaHintGraphObject(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: Integer;
  v3: Double;
  v4: Double;
  v5: PChar;
  v6: PChar;
begin
  LuaLogBegin(L, 'Attach_AlphaHintGraphObject');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptInt(L, 2, 0);
  v3 := LuaOptNumber(L, 3, 0.0);
  v4 := LuaOptNumber(L, 4, 0.0);
  v5 := LuaOptStr(L, 5);
  v6 := LuaOptStr(L, 6);
  id := NextId('Attach_AlphaHintGraphObject');
  Result := 0;
  LuaLogEnd(id);
end;

function bind_Attach_AlphaHintExGraphObject(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: Integer;
  v3: Double;
  v4: Double;
  v5: Double;
  v6: Double;
  v7: PChar;
  v8: PChar;
begin
  LuaLogBegin(L, 'Attach_AlphaHintExGraphObject');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptInt(L, 2, 0);
  v3 := LuaOptNumber(L, 3, 0.0);
  v4 := LuaOptNumber(L, 4, 0.0);
  v5 := LuaOptNumber(L, 5, 0.0);
  v6 := LuaOptNumber(L, 6, 0.0);
  v7 := LuaOptStr(L, 7);
  v8 := LuaOptStr(L, 8);
  id := NextId('Attach_AlphaHintExGraphObject');
  Result := 0;
  LuaLogEnd(id);
end;

function bind_Set_GraphObjectParent(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: Integer;
begin
  LuaLogBegin(L, 'Set_GraphObjectParent');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptInt(L, 2, 0);
  id := NextId('Set_GraphObjectParent');
  Result := 0;
  LuaLogEnd(id);
end;

function bind_Set_MaterialEmission(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: PChar;
  v2: Double;
  v3: Double;
  v4: Double;
begin
  LuaLogBegin(L, 'Set_MaterialEmission');
  v1 := LuaOptStr(L, 1);
  v2 := LuaOptNumber(L, 2, 0.0);
  v3 := LuaOptNumber(L, 3, 0.0);
  v4 := LuaOptNumber(L, 4, 0.0);
  id := NextId('Set_MaterialEmission');
  Result := 0;
  LuaLogEnd(id);
end;

function bind_Set_JointThresholdForce(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v4: Double;
begin
  LuaLogBegin(L, 'Set_JointThresholdForce');
  v1 := LuaOptInt(L, 1, 0);
  v4 := LuaOptNumber(L, 4, 0.0);
  id := NextId('Set_JointThresholdForce');
  Result := 0;
  LuaLogEnd(id);
end;

function bind_Get_RopePhysItem(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: Integer;
begin
  LuaLogBegin(L, 'Get_RopePhysItem');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptInt(L, 2, 0);
  id := NextId('Get_RopePhysItem');
  id := PhysGetRopeItemId(v1, v2);
  Lua.PushInteger(L, id);
  Result := 1;
  LuaLogEnd(id);
end;

function bind_Get_RopeJointItem(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: Integer;
begin
  LuaLogBegin(L, 'Get_RopeJointItem');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptInt(L, 2, 0);
  id := NextId('Get_RopeJointItem');
  Lua.PushInteger(L, id);
  Result := 1;
  LuaLogEnd(id);
end;

function bind_Attach_ScriptToObject(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: PChar;
  v3: PChar;
  s2, s3: string;
begin
  LuaLogBegin(L, 'Attach_ScriptToObject');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptStr(L, 2);
  v3 := LuaOptStr(L, 3);
  if v2 <> nil then s2 := v2;
  if v3 <> nil then s3 := v3;
  EventsAdd(v1, s2, s3);
  id := NextId('Attach_ScriptToObject');
  Result := 0;
  LuaLogEnd(id);
end;

function bind_Set_PlayerMagnetOff(L: TLuaState): Integer; cdecl;
var
  id: Integer;
begin
  LuaLogBegin(L, 'Set_PlayerMagnetOff');
  id := NextId('Set_PlayerMagnetOff');
  Result := 0;
  LuaLogEnd(id);
end;

function bind_Set_CameraPosition(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Double;
  v2: Double;
begin
  LuaLogBegin(L, 'Set_CameraPosition');
  v1 := LuaOptNumber(L, 1, 0.0);
  v2 := LuaOptNumber(L, 2, 0.0);
  id := NextId('Set_CameraPosition');
  Result := 0;
  LuaLogEnd(id);
end;

function bind_Set_CameraRotation(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Double;
begin
  LuaLogBegin(L, 'Set_CameraRotation');
  v1 := LuaOptNumber(L, 1, 0.0);
  id := NextId('Set_CameraRotation');
  Result := 0;
  LuaLogEnd(id);
end;

function bind_Set_CameraViewArea(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Double;
  v2: Double;
begin
  LuaLogBegin(L, 'Set_CameraViewArea');
  v1 := LuaOptNumber(L, 1, 0.0);
  v2 := LuaOptNumber(L, 2, 0.0);
  id := NextId('Set_CameraViewArea');
  Result := 0;
  LuaLogEnd(id);
end;

function bind_Get_RealViewRect(L: TLuaState): Integer; cdecl;
var
  id: Integer;
begin
  LuaLogBegin(L, 'Get_RealViewRect');
  id := NextId('Get_RealViewRect');
  Lua.PushNumber(L, id);
  Lua.PushNumber(L, 0);
  Lua.PushNumber(L, 0);
  Lua.PushNumber(L, 0);
  Result := 4;
  LuaLogEnd(id);
end;

function bind_Get_ScreenViewerRect(L: TLuaState): Integer; cdecl;
var
  id: Integer;
begin
  LuaLogBegin(L, 'Get_ScreenViewerRect');
  id := NextId('Get_ScreenViewerRect');
  Lua.PushNumber(L, id);
  Lua.PushNumber(L, 0);
  Lua.PushNumber(L, 0);
  Lua.PushNumber(L, 0);
  Result := 4;
  LuaLogEnd(id);
end;

function bind_Get_PhysicTime(L: TLuaState): Integer; cdecl;
var
  id: Integer;
begin
  LuaLogBegin(L, 'Get_PhysicTime');
  id := NextId('Get_PhysicTime');
  Lua.PushNumber(L, id);
  Result := 1;
  LuaLogEnd(id);
end;

function bind_Play_SoundSample(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: PChar;
begin
  LuaLogBegin(L, 'Play_SoundSample');
  v1 := LuaOptStr(L, 1);
  id := NextId('Play_SoundSample');
  Lua.PushNumber(L, id);
  Result := 1;
  LuaLogEnd(id);
end;

function bind_Play_LoopSoundSample(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: PChar;
begin
  LuaLogBegin(L, 'Play_LoopSoundSample');
  v1 := LuaOptStr(L, 1);
  id := NextId('Play_LoopSoundSample');
  Lua.PushNumber(L, id);
  Result := 1;
  LuaLogEnd(id);
end;

function bind_Stop_SoundSample(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: PChar;
begin
  LuaLogBegin(L, 'Stop_SoundSample');
  v1 := LuaOptStr(L, 1);
  id := NextId('Stop_SoundSample');
  Result := 0;
  LuaLogEnd(id);
end;

function bind_Pause_SoundSample(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: PChar;
  v2: Integer;
begin
  LuaLogBegin(L, 'Pause_SoundSample');
  v1 := LuaOptStr(L, 1);
  v2 := LuaOptInt(L, 2, 0);
  id := NextId('Pause_SoundSample');
  Result := 0;
  LuaLogEnd(id);
end;

function bind_Set_PhysicMaxHitSoundValue(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: Double;
begin
  LuaLogBegin(L, 'Set_PhysicMaxHitSoundValue');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptNumber(L, 2, 0.0);
  id := NextId('Set_PhysicMaxHitSoundValue');
  Result := 0;
  LuaLogEnd(id);
end;

function bind_Play_MusicSample(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: PChar;
begin
  LuaLogBegin(L, 'Play_MusicSample');
  v1 := LuaOptStr(L, 1);
  id := NextId('Play_MusicSample');
  Lua.PushNumber(L, id);
  Result := 1;
  LuaLogEnd(id);
end;

function bind_Start_MusicSample(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: PChar;
begin
  LuaLogBegin(L, 'Start_MusicSample');
  v1 := LuaOptStr(L, 1);
  id := NextId('Start_MusicSample');
  Lua.PushNumber(L, id);
  Result := 1;
  LuaLogEnd(id);
end;

function bind_Pause_AllMusic(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
begin
  LuaLogBegin(L, 'Pause_AllMusic');
  v1 := LuaOptInt(L, 1, 0);
  id := NextId('Pause_AllMusic');
  Result := 0;
  LuaLogEnd(id);
end;

function bind_Stop_AllMusic(L: TLuaState): Integer; cdecl;
var
  id: Integer;
begin
  LuaLogBegin(L, 'Stop_AllMusic');
  id := NextId('Stop_AllMusic');
  Result := 0;
  LuaLogEnd(id);
end;

function bind_Add_LevelMaterial(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: PChar;
  v2: PChar;
begin
  LuaLogBegin(L, 'Add_LevelMaterial');
  v1 := LuaOptStr(L, 1);
  v2 := LuaOptStr(L, 2);
  id := NextId('Add_LevelMaterial');
  Result := 0;
  LuaLogEnd(id);
end;

function bind_Add_LevelSound(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: PChar;
  v2: PChar;
begin
  LuaLogBegin(L, 'Add_LevelSound');
  v1 := LuaOptStr(L, 1);
  v2 := LuaOptStr(L, 2);
  id := NextId('Add_LevelSound');
  Result := 0;
  LuaLogEnd(id);
end;

function bind_Clear_LevelMaterial(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: PChar;
begin
  LuaLogBegin(L, 'Clear_LevelMaterial');
  v1 := LuaOptStr(L, 1);
  id := NextId('Clear_LevelMaterial');
  Result := 0;
  LuaLogEnd(id);
end;

function bind_Set_BackMaterial(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: PChar;
begin
  LuaLogBegin(L, 'Set_BackMaterial');
  v1 := LuaOptStr(L, 1);
  id := NextId('Set_BackMaterial');
  Result := 0;
  LuaLogEnd(id);
end;

function bind_Set_GraphMaterial(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
  v2: PChar;
  v3: PChar;
begin
  LuaLogBegin(L, 'Set_GraphMaterial');
  v1 := LuaOptInt(L, 1, 0);
  v2 := LuaOptStr(L, 2);
  v3 := LuaOptStr(L, 3);
  id := NextId('Set_GraphMaterial');
  Result := 0;
  LuaLogEnd(id);
end;

function bind_Level_Complete(L: TLuaState): Integer; cdecl;
var
  id: Integer;
begin
  LuaLogBegin(L, 'Level_Complete');
  id := NextId('Level_Complete');
  Result := 0;
  LuaLogEnd(id);
end;

function bind_Level_Restart(L: TLuaState): Integer; cdecl;
var
  id: Integer;
begin
  LuaLogBegin(L, 'Level_Restart');
  id := NextId('Level_Restart');
  Result := 0;
  LuaLogEnd(id);
end;

function bind_Go_NextLevel(L: TLuaState): Integer; cdecl;
var
  id: Integer;
begin
  LuaLogBegin(L, 'Go_NextLevel');
  id := NextId('Go_NextLevel');
  Result := 0;
  LuaLogEnd(id);
end;

function bind_Do_LevelComplete(L: TLuaState): Integer; cdecl;
var
  id: Integer;
begin
  LuaLogBegin(L, 'Do_LevelComplete');
  id := NextId('Do_LevelComplete');
  Result := 0;
  LuaLogEnd(id);
end;

function bind_Set_VisibleHintButton(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Double;
begin
  LuaLogBegin(L, 'Set_VisibleHintButton');
  v1 := LuaOptNumber(L, 1, 0.0);
  id := NextId('Set_VisibleHintButton');
  Result := 0;
  LuaLogEnd(id);
end;

function bind_Set_VisibleRollMap(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Double;
begin
  LuaLogBegin(L, 'Set_VisibleRollMap');
  v1 := LuaOptNumber(L, 1, 0.0);
  id := NextId('Set_VisibleRollMap');
  Result := 0;
  LuaLogEnd(id);
end;

function bind_Set_HideTimeHint(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Double;
begin
  LuaLogBegin(L, 'Set_HideTimeHint');
  v1 := LuaOptNumber(L, 1, 0.0);
  id := NextId('Set_HideTimeHint');
  Result := 0;
  LuaLogEnd(id);
end;

function bind_Drop_ToLog(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Double;
begin
  LuaLogBegin(L, 'Drop_ToLog');
  v1 := LuaOptNumber(L, 1, 0.0);
  id := NextId('Drop_ToLog');
  Result := 0;
  LuaLogEnd(id);
end;

function bind_Get_MousePosition(L: TLuaState): Integer; cdecl;
var
  id: Integer;
begin
  LuaLogBegin(L, 'Get_MousePosition');
  id := NextId('Get_MousePosition');
  Lua.PushNumber(L, id);
  Lua.PushNumber(L, 0);
  Result := 2;
  LuaLogEnd(id);
end;

function bind_Get_JointReactionForce(L: TLuaState): Integer; cdecl;
var
  id: Integer;
  v1: Integer;
begin
  LuaLogBegin(L, 'Get_JointReactionForce');
  v1 := LuaOptInt(L, 1, 0);
  id := NextId('Get_JointReactionForce');
  Lua.PushNumber(L, id);
  Lua.PushNumber(L, 0);
  Result := 2;
  LuaLogEnd(id);
end;

procedure RegisterBindings(L: TLuaState);
begin
  Lua.PushCClosure(L, Pointer(@bind_Do_Command), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Do_Command'));
  Lua.PushCClosure(L, Pointer(@bind_Add_WoodBox), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Add_WoodBox'));
  Lua.PushCClosure(L, Pointer(@bind_Add_MetallScrew), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Add_MetallScrew'));
  Lua.PushCClosure(L, Pointer(@bind_Add_MetallGear), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Add_MetallGear'));
  Lua.PushCClosure(L, Pointer(@bind_Add_WoodGear), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Add_WoodGear'));
  Lua.PushCClosure(L, Pointer(@bind_Add_WoodWall), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Add_WoodWall'));
  Lua.PushCClosure(L, Pointer(@bind_Add_WoodFormWall), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Add_WoodFormWall'));
  Lua.PushCClosure(L, Pointer(@bind_Add_SwitchArm), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Add_SwitchArm'));
  Lua.PushCClosure(L, Pointer(@bind_Add_Lock), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Add_Lock'));
  Lua.PushCClosure(L, Pointer(@bind_Add_Key), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Add_Key'));
  Lua.PushCClosure(L, Pointer(@bind_Add_Symbol), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Add_Symbol'));
  Lua.PushCClosure(L, Pointer(@bind_Add_HammerParts), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Add_HammerParts'));
  Lua.PushCClosure(L, Pointer(@bind_Add_BarDoor), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Add_BarDoor'));
  Lua.PushCClosure(L, Pointer(@bind_Add_Ball), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Add_Ball'));
  Lua.PushCClosure(L, Pointer(@bind_Add_ControlArm), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Add_ControlArm'));
  Lua.PushCClosure(L, Pointer(@bind_Add_DoorHandle), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Add_DoorHandle'));
  Lua.PushCClosure(L, Pointer(@bind_Add_ScrewDriver), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Add_ScrewDriver'));
  Lua.PushCClosure(L, Pointer(@bind_Add_Rope), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Add_Rope'));
  Lua.PushCClosure(L, Pointer(@bind_Add_Cork), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Add_Cork'));
  Lua.PushCClosure(L, Pointer(@bind_Add_TestTube), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Add_TestTube'));
  Lua.PushCClosure(L, Pointer(@bind_Add_Rack), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Add_Rack'));
  Lua.PushCClosure(L, Pointer(@bind_Add_Battery), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Add_Battery'));
  Lua.PushCClosure(L, Pointer(@bind_Add_ElectricPlug), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Add_ElectricPlug'));
  Lua.PushCClosure(L, Pointer(@bind_Add_Spanner), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Add_Spanner'));
  Lua.PushCClosure(L, Pointer(@bind_Add_Laser), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Add_Laser'));
  Lua.PushCClosure(L, Pointer(@bind_Add_StaticCan), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Add_StaticCan'));
  Lua.PushCClosure(L, Pointer(@bind_Add_Lamp), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Add_Lamp'));
  Lua.PushCClosure(L, Pointer(@bind_Add_PropellerFan), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Add_PropellerFan'));
  Lua.PushCClosure(L, Pointer(@bind_Add_Magnet), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Add_Magnet'));
  Lua.PushCClosure(L, Pointer(@bind_Add_WoodDetail), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Add_WoodDetail'));
  Lua.PushCClosure(L, Pointer(@bind_Add_ToothGear), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Add_ToothGear'));
  Lua.PushCClosure(L, Pointer(@bind_Add_ShankBody), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Add_ShankBody'));
  Lua.PushCClosure(L, Pointer(@bind_Add_Barrel), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Add_Barrel'));
  Lua.PushCClosure(L, Pointer(@bind_Add_PushButton), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Add_PushButton'));
  Lua.PushCClosure(L, Pointer(@bind_Add_FlyAwayLockIcon), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Add_FlyAwayLockIcon'));
  Lua.PushCClosure(L, Pointer(@bind_Add_SpiderWeb), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Add_SpiderWeb'));
  Lua.PushCClosure(L, Pointer(@bind_Get_PhysObjByIndex), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Get_PhysObjByIndex'));
  Lua.PushCClosure(L, Pointer(@bind_Add_JointNail), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Add_JointNail'));
  Lua.PushCClosure(L, Pointer(@bind_Add_JointNailToStatic), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Add_JointNailToStatic'));
  Lua.PushCClosure(L, Pointer(@bind_Add_JointSkid), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Add_JointSkid'));
  Lua.PushCClosure(L, Pointer(@bind_Add_JointShank), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Add_JointShank'));
  Lua.PushCClosure(L, Pointer(@bind_Add_JointDistance), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Add_JointDistance'));
  Lua.PushCClosure(L, Pointer(@bind_Flip_GraphObjectX), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Flip_GraphObjectX'));
  Lua.PushCClosure(L, Pointer(@bind_Flip_GraphObjectY), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Flip_GraphObjectY'));
  Lua.PushCClosure(L, Pointer(@bind_Set_FlipGraphObject), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Set_FlipGraphObject'));
  Lua.PushCClosure(L, Pointer(@bind_Add_JointSimpleGear), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Add_JointSimpleGear'));
  Lua.PushCClosure(L, Pointer(@bind_Add_JointSimplePulley), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Add_JointSimplePulley'));
  Lua.PushCClosure(L, Pointer(@bind_Add_JointSimplePrismatic), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Add_JointSimplePrismatic'));
  Lua.PushCClosure(L, Pointer(@bind_Add_JointSimpleRevolute), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Add_JointSimpleRevolute'));
  Lua.PushCClosure(L, Pointer(@bind_Add_GraphSprite), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Add_GraphSprite'));
  Lua.PushCClosure(L, Pointer(@bind_Add_HudGraphSprite), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Add_HudGraphSprite'));
  Lua.PushCClosure(L, Pointer(@bind_Add_AlphaDoubleSprite), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Add_AlphaDoubleSprite'));
  Lua.PushCClosure(L, Pointer(@bind_Add_ExtAlphaDoubleSprite), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Add_ExtAlphaDoubleSprite'));
  Lua.PushCClosure(L, Pointer(@bind_Add_SpringSprite), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Add_SpringSprite'));
  Lua.PushCClosure(L, Pointer(@bind_Add_GearChalkSprite), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Add_GearChalkSprite'));
  Lua.PushCClosure(L, Pointer(@bind_Add_AnimateSmoke), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Add_AnimateSmoke'));
  Lua.PushCClosure(L, Pointer(@bind_Add_AnimateHUDSmoke), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Add_AnimateHUDSmoke'));
  Lua.PushCClosure(L, Pointer(@bind_Add_AlphaHint), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Add_AlphaHint'));
  Lua.PushCClosure(L, Pointer(@bind_Add_AlphaHudSprite), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Add_AlphaHudSprite'));
  Lua.PushCClosure(L, Pointer(@bind_Add_MovingPipe), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Add_MovingPipe'));
  Lua.PushCClosure(L, Pointer(@bind_Destroy_Joint), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Destroy_Joint'));
  Lua.PushCClosure(L, Pointer(@bind_Destroy_Body), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Destroy_Body'));
  Lua.PushCClosure(L, Pointer(@bind_Add_SimplePhysicObject), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Add_SimplePhysicObject'));
  Lua.PushCClosure(L, Pointer(@bind_Add_SimplePhysCircle), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Add_SimplePhysCircle'));
  Lua.PushCClosure(L, Pointer(@bind_Add_SimpleButton), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Add_SimpleButton'));
  Lua.PushCClosure(L, Pointer(@bind_Add_HudButton), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Add_HudButton'));
  Lua.PushCClosure(L, Pointer(@bind_Add_NextButton), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Add_NextButton'));
  Lua.PushCClosure(L, Pointer(@bind_Add_CloseButton), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Add_CloseButton'));
  Lua.PushCClosure(L, Pointer(@bind_Do_ShowCommand), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Do_ShowCommand'));
  Lua.PushCClosure(L, Pointer(@bind_Do_HideCommand), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Do_HideCommand'));
  Lua.PushCClosure(L, Pointer(@bind_Add_SimpleTimer), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Add_SimpleTimer'));
  Lua.PushCClosure(L, Pointer(@bind_Start_Timer), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Start_Timer'));
  Lua.PushCClosure(L, Pointer(@bind_Set_GlobalVar), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Set_GlobalVar'));
  Lua.PushCClosure(L, Pointer(@bind_Set_ScrObjPos), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Set_ScrObjPos'));
  Lua.PushCClosure(L, Pointer(@bind_Get_ScrObjPos), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Get_ScrObjPos'));
  Lua.PushCClosure(L, Pointer(@bind_Local_ToWorld), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Local_ToWorld'));
  Lua.PushCClosure(L, Pointer(@bind_World_ToLocal), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('World_ToLocal'));
  Lua.PushCClosure(L, Pointer(@bind_Set_PhysSensor), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Set_PhysSensor'));
  Lua.PushCClosure(L, Pointer(@bind_Set_PhysBullet), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Set_PhysBullet'));
  Lua.PushCClosure(L, Pointer(@bind_Set_PhysFilterData), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Set_PhysFilterData'));
  Lua.PushCClosure(L, Pointer(@bind_Re_Filter), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Re_Filter'));
  Lua.PushCClosure(L, Pointer(@bind_Set_PhysThresholdPlayerForce), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Set_PhysThresholdPlayerForce'));
  Lua.PushCClosure(L, Pointer(@bind_Set_PhysParams), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Set_PhysParams'));
  Lua.PushCClosure(L, Pointer(@bind_Get_PhysParams), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Get_PhysParams'));
  Lua.PushCClosure(L, Pointer(@bind_Set_ExtPhysParams), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Set_ExtPhysParams'));
  Lua.PushCClosure(L, Pointer(@bind_Set_PhysDamping), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Set_PhysDamping'));
  Lua.PushCClosure(L, Pointer(@bind_Set_DebugPosition), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Set_DebugPosition'));
  Lua.PushCClosure(L, Pointer(@bind_Set_DebugText), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Set_DebugText'));
  Lua.PushCClosure(L, Pointer(@bind_Set_JointLimits), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Set_JointLimits'));
  Lua.PushCClosure(L, Pointer(@bind_Get_JointLimits), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Get_JointLimits'));
  Lua.PushCClosure(L, Pointer(@bind_Set_JointMotors), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Set_JointMotors'));
  Lua.PushCClosure(L, Pointer(@bind_Get_JointMotors), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Get_JointMotors'));
  Lua.PushCClosure(L, Pointer(@bind_Get_JointAngle), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Get_JointAngle'));
  Lua.PushCClosure(L, Pointer(@bind_Get_JointTranslation), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Get_JointTranslation'));
  Lua.PushCClosure(L, Pointer(@bind_Clear_JustCreationFlag), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Clear_JustCreationFlag'));
  Lua.PushCClosure(L, Pointer(@bind_Apply_PhysImpulse), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Apply_PhysImpulse'));
  Lua.PushCClosure(L, Pointer(@bind_Set_PhysVelocity), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Set_PhysVelocity'));
  Lua.PushCClosure(L, Pointer(@bind_Get_PhysVelocity), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Get_PhysVelocity'));
  Lua.PushCClosure(L, Pointer(@bind_Apply_PhysForce), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Apply_PhysForce'));
  Lua.PushCClosure(L, Pointer(@bind_Apply_PhysForceAtPos), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Apply_PhysForceAtPos'));
  Lua.PushCClosure(L, Pointer(@bind_Attach_ShapeCircle), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Attach_ShapeCircle'));
  Lua.PushCClosure(L, Pointer(@bind_Attach_ShapePolygon), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Attach_ShapePolygon'));
  Lua.PushCClosure(L, Pointer(@bind_Attach_SimpleGraphObject), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Attach_SimpleGraphObject'));
  Lua.PushCClosure(L, Pointer(@bind_Add_PhysicObjectWithAdvGraph), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Add_PhysicObjectWithAdvGraph'));
  Lua.PushCClosure(L, Pointer(@bind_Get_GraphObject), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Get_GraphObject'));
  Lua.PushCClosure(L, Pointer(@bind_Attach_AlphaHintGraphObject), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Attach_AlphaHintGraphObject'));
  Lua.PushCClosure(L, Pointer(@bind_Attach_AlphaHintExGraphObject), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Attach_AlphaHintExGraphObject'));
  Lua.PushCClosure(L, Pointer(@bind_Set_GraphObjectParent), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Set_GraphObjectParent'));
  Lua.PushCClosure(L, Pointer(@bind_Set_MaterialEmission), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Set_MaterialEmission'));
  Lua.PushCClosure(L, Pointer(@bind_Set_JointThresholdForce), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Set_JointThresholdForce'));
  Lua.PushCClosure(L, Pointer(@bind_Get_RopePhysItem), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Get_RopePhysItem'));
  Lua.PushCClosure(L, Pointer(@bind_Get_RopeJointItem), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Get_RopeJointItem'));
  Lua.PushCClosure(L, Pointer(@bind_Attach_ScriptToObject), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Attach_ScriptToObject'));
  Lua.PushCClosure(L, Pointer(@bind_Set_PlayerMagnetOff), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Set_PlayerMagnetOff'));
  Lua.PushCClosure(L, Pointer(@bind_Set_CameraPosition), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Set_CameraPosition'));
  Lua.PushCClosure(L, Pointer(@bind_Set_CameraRotation), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Set_CameraRotation'));
  Lua.PushCClosure(L, Pointer(@bind_Set_CameraViewArea), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Set_CameraViewArea'));
  Lua.PushCClosure(L, Pointer(@bind_Get_RealViewRect), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Get_RealViewRect'));
  Lua.PushCClosure(L, Pointer(@bind_Get_ScreenViewerRect), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Get_ScreenViewerRect'));
  Lua.PushCClosure(L, Pointer(@bind_Get_PhysicTime), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Get_PhysicTime'));
  Lua.PushCClosure(L, Pointer(@bind_Play_SoundSample), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Play_SoundSample'));
  Lua.PushCClosure(L, Pointer(@bind_Play_LoopSoundSample), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Play_LoopSoundSample'));
  Lua.PushCClosure(L, Pointer(@bind_Stop_SoundSample), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Stop_SoundSample'));
  Lua.PushCClosure(L, Pointer(@bind_Pause_SoundSample), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Pause_SoundSample'));
  Lua.PushCClosure(L, Pointer(@bind_Set_PhysicMaxHitSoundValue), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Set_PhysicMaxHitSoundValue'));
  Lua.PushCClosure(L, Pointer(@bind_Play_MusicSample), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Play_MusicSample'));
  Lua.PushCClosure(L, Pointer(@bind_Start_MusicSample), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Start_MusicSample'));
  Lua.PushCClosure(L, Pointer(@bind_Pause_AllMusic), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Pause_AllMusic'));
  Lua.PushCClosure(L, Pointer(@bind_Stop_AllMusic), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Stop_AllMusic'));
  Lua.PushCClosure(L, Pointer(@bind_Add_LevelMaterial), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Add_LevelMaterial'));
  Lua.PushCClosure(L, Pointer(@bind_Add_LevelSound), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Add_LevelSound'));
  Lua.PushCClosure(L, Pointer(@bind_Clear_LevelMaterial), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Clear_LevelMaterial'));
  Lua.PushCClosure(L, Pointer(@bind_Set_BackMaterial), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Set_BackMaterial'));
  Lua.PushCClosure(L, Pointer(@bind_Set_GraphMaterial), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Set_GraphMaterial'));
  Lua.PushCClosure(L, Pointer(@bind_Level_Complete), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Level_Complete'));
  Lua.PushCClosure(L, Pointer(@bind_Level_Restart), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Level_Restart'));
  Lua.PushCClosure(L, Pointer(@bind_Go_NextLevel), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Go_NextLevel'));
  Lua.PushCClosure(L, Pointer(@bind_Do_LevelComplete), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Do_LevelComplete'));
  Lua.PushCClosure(L, Pointer(@bind_Set_VisibleHintButton), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Set_VisibleHintButton'));
  Lua.PushCClosure(L, Pointer(@bind_Set_VisibleRollMap), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Set_VisibleRollMap'));
  Lua.PushCClosure(L, Pointer(@bind_Set_HideTimeHint), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Set_HideTimeHint'));
  Lua.PushCClosure(L, Pointer(@bind_Drop_ToLog), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Drop_ToLog'));
  Lua.PushCClosure(L, Pointer(@bind_Get_MousePosition), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Get_MousePosition'));
  Lua.PushCClosure(L, Pointer(@bind_Get_JointReactionForce), 0);
  Lua.SetField(L, LUA_GLOBALSINDEX, PChar('Get_JointReactionForce'));
end;

end.