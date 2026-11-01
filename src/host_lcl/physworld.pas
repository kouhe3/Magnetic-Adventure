unit PhysWorld;
{$mode objfpc}{$H+}
// 宿主侧 b2 物理桥（T6.3c）：动态加载 b2Physics.dll，按原版工厂语义建 world/body/shape。
//
// 依据：F276（The Teleport 18 个 CreateBody = 4 墙 + 14 对象；body 顺序/坐标/角度 14/14）、
//       F277（20 个 shape 的半径/密度/摩擦/弹性）、F273/F274（接触事件派发给 Lua）。
//
// 覆盖边界：
//   * 只实现 The Teleport 用到的 5 个建体绑定 + Attach_ShapeCircle；关节/接触回调接口已留。
//   * WoodWall 的盒半宽高 (0.687, 3) 与 SwitchArm 的 (圆 0.57@(0,0.9) + 盒 0.42x0.976@(0,-0.54))
//     是从该关录制定出的常量；别的关卡若形状不同，需要按同一方法补测。
//   * WoodGear 半径表 1..6 = 1.6/1.8/2.0/2.2/2.4/4.33：1 与 5 由录制验证，其余取自
//     IDA 常量 dword_6468A4/645D68/6468D8/646910（L1，待录制复核）。
//
// 失效条件：b2Physics 的 def 布局（src/b2physics/b2physics.h）改动、或工厂参数表变化。
interface

uses Windows;

type
  TPhysVec2 = packed record x, y: Single; end;
  TPhysAABB = packed record lo, hi: TPhysVec2; end;
  TPhysBodyDef = packed record
    world: Pointer;
    angularDamping, linearDamping: Single;
    allowSleep, fixedRotation, isBullet: Byte;
    pad: Byte;
  end;
  TPhysShapeDef = packed record
    body: Pointer;
    friction, restitution, density: Single;
    sensor: Byte;
    pad: array[0..2] of Byte;
    a, b, c, d: Single;
  end;
  TPhysXForm = packed record x, y, angle: Single; end;
  TPhysFilter = packed record category, mask: Word; group: SmallInt; end;
  TContactRec = packed record
    shape1, shape2: Pointer;
    posX, posY, normalX, normalY: Single;
    userData1, userData2: Pointer;
    kind: Integer;
  end;

// 加载 DLL、建 world（AABB ±100，重力 0）与 4 面世界墙；失败返回 False。
function PhysStart: Boolean;
function PhysActive: Boolean;
// 每关重开时清 id→body 映射（b2 世界与已有 body 不销毁）。
procedure PhysResetObjects;
procedure PhysStep(Dt: Single; Vi, Pi: Integer);
procedure PhysSetContactCallback(Cb: Pointer);
function PhysBodyOf(Id: Integer): Pointer;

// 工厂语义（参数与原版 Lua 绑定实参一致；F276/F277）。
function PhysAddSimplePhysicObject(Id: Integer; X, Y, Angle: Double): Pointer;
function PhysAddSimplePhysCircle(Id: Integer; Dens, Angle, X, Y, Radius: Double): Pointer;
function PhysAddWoodGear(Id: Integer; X, Y, Angle, Size: Double): Pointer;
function PhysAddWoodWall(Id: Integer; X, Y, Angle: Double): Pointer;
function PhysAddSwitchArm(Id: Integer; X, Y, Angle: Double): Pointer;
function PhysAttachShapeCircle(Id: Integer; Fric, Rest, Dens, LX, LY, Radius: Double): Pointer;

implementation

type
  TCreateWorldFn = function(Aabb, Gravity: Pointer): Pointer; cdecl;
  TCreateBodyFn = function(Def: Pointer): Pointer; cdecl;
  TSetXFormFn = procedure(Body, Xf: Pointer); cdecl;
  TShapeFn = function(Def: Pointer): Pointer; cdecl;
  TMassFn = procedure(Body: Pointer); cdecl;
  TUserDataFn = function(Body, Data: Pointer): Pointer; cdecl;
  TStepFn = procedure(World: Pointer; Dt: Single; Vi, Pi: Integer); cdecl;
  TContactCbFn = procedure(World, Cb: Pointer); cdecl;

type
  TPhysObj = record
    Id: Integer;
    Body: Pointer;
  end;

const
  MAX_OBJECTS = 2048;
  kGearRadius: array[1..6] of Single = (1.6, 1.8, 2.0, 2.2, 2.4, 4.33);
  kWallX = 31.305818557739258;  // 原版 float32 = 0xC1FA7251（F276 的录制值）
  kWallY = 23.0;

var
  g_dll: HMODULE;
  g_world: Pointer;
  g_active: Boolean;
  g_createWorld: TCreateWorldFn;
  g_createBody: TCreateBodyFn;
  g_setXForm: TSetXFormFn;
  g_shapeCircle: TShapeFn;
  g_shapeBox: TShapeFn;
  g_mass: TMassFn;
  g_setUserData: TUserDataFn;
  g_step: TStepFn;
  g_contactCb: TContactCbFn;
  g_objs: array[0..MAX_OBJECTS - 1] of TPhysObj;
  g_objCount: Integer;

function PhysActive: Boolean;
begin
  Result := g_active;
end;

procedure PhysResetObjects;
begin
  g_objCount := 0;
end;

function PhysBodyOf(Id: Integer): Pointer;
var
  i: Integer;
begin
  for i := 0 to g_objCount - 1 do
    if g_objs[i].Id = Id then
      Exit(g_objs[i].Body);
  Result := nil;
end;

procedure RegBody(Id: Integer; Body: Pointer);
begin
  if g_objCount < MAX_OBJECTS then
  begin
    g_objs[g_objCount].Id := Id;
    g_objs[g_objCount].Body := Body;
    Inc(g_objCount);
  end;
end;

procedure SetXForm(Body: Pointer; X, Y, Angle: Single);
var
  xf: TPhysXForm;
begin
  xf.x := X;
  xf.y := Y;
  xf.angle := Angle;
  g_setXForm(Body, @xf);
end;

// 原版每个 body 都发两条 SetXForm：先 (x,y,0)，再 (x,y,angle)（F276）。
function NewBody(Id: Integer; X, Y, Angle: Single; AllowSleep: Boolean): Pointer;
var
  def: TPhysBodyDef;
begin
  FillChar(def, SizeOf(def), 0);
  def.world := g_world;
  if AllowSleep then
    def.allowSleep := 1
  else
    def.allowSleep := 0;
  Result := g_createBody(@def);
  if Result = nil then
    Exit;
  SetXForm(Result, X, Y, 0.0);
  SetXForm(Result, X, Y, Angle);
  if Assigned(g_setUserData) then
    g_setUserData(Result, Pointer(Id));
  RegBody(Id, Result);
end;

function AttachCircle(Body: Pointer; Fric, Rest, Dens, LX, LY, Radius: Single): Pointer;
var
  sd: TPhysShapeDef;
begin
  FillChar(sd, SizeOf(sd), 0);
  sd.body := Body;
  sd.friction := Fric;
  sd.restitution := Rest;
  sd.density := Dens;
  sd.a := LX;
  sd.b := LY;
  sd.c := Radius;
  Result := g_shapeCircle(@sd);
  if Assigned(g_mass) then
    g_mass(Body);
end;

function AttachBox(Body: Pointer; Fric, Rest, Dens, LX, LY, HalfW, HalfH: Single): Pointer;
var
  sd: TPhysShapeDef;
begin
  FillChar(sd, SizeOf(sd), 0);
  sd.body := Body;
  sd.friction := Fric;
  sd.restitution := Rest;
  sd.density := Dens;
  sd.a := LX;
  sd.b := LY;
  sd.c := HalfW;
  sd.d := HalfH;
  Result := g_shapeBox(@sd);
  if Assigned(g_mass) then
    g_mass(Body);
end;

function GearRadius(Size: Integer): Single;
begin
  if (Size >= 1) and (Size <= 6) then
    Result := kGearRadius[Size]
  else
    Result := kGearRadius[1];
end;

function PhysAddSimplePhysicObject(Id: Integer; X, Y, Angle: Double): Pointer;
begin
  if not g_active then
    Exit(nil);
  Result := NewBody(Id, X, Y, Angle, True);
end;

function PhysAddSimplePhysCircle(Id: Integer; Dens, Angle, X, Y, Radius: Double): Pointer;
var
  b: Pointer;
begin
  if not g_active then
    Exit(nil);
  b := NewBody(Id, X, Y, Angle, True);
  if b <> nil then
    AttachCircle(b, 0.0, 0.0, Dens, 0.0, 0.0, Radius);
  Result := b;
end;

function PhysAddWoodGear(Id: Integer; X, Y, Angle, Size: Double): Pointer;
var
  b: Pointer;
begin
  if not g_active then
    Exit(nil);
  b := NewBody(Id, X, Y, Angle, True);
  if b <> nil then
    AttachCircle(b, 0.3, 0.1, 0.3, 0.0, 0.0, GearRadius(Round(Size)));
  Result := b;
end;

function PhysAddWoodWall(Id: Integer; X, Y, Angle: Double): Pointer;
var
  b: Pointer;
begin
  if not g_active then
    Exit(nil);
  b := NewBody(Id, X, Y, Angle, True);
  if b <> nil then
    AttachBox(b, 0.7, 0.4, 0.3, 0.0, 0.0, 0.687, 3.0);
  Result := b;
end;

function PhysAddSwitchArm(Id: Integer; X, Y, Angle: Double): Pointer;
var
  b: Pointer;
begin
  if not g_active then
    Exit(nil);
  b := NewBody(Id, X, Y, Angle, True);
  if b <> nil then
  begin
    AttachCircle(b, 0.7, 0.4, 0.3, 0.0, 0.9, 0.57);
    AttachBox(b, 0.7, 0.4, 0.3, 0.0, -0.54, 0.42, 0.976);
  end;
  Result := b;
end;

function PhysAttachShapeCircle(Id: Integer; Fric, Rest, Dens, LX, LY, Radius: Double): Pointer;
var
  b: Pointer;
begin
  if not g_active then
    Exit(nil);
  b := PhysBodyOf(Id);
  if b = nil then
    Exit(nil);
  Result := AttachCircle(b, Fric, Rest, Dens, LX, LY, Radius);
end;

procedure PhysStep(Dt: Single; Vi, Pi: Integer);
begin
  if g_active and (g_world <> nil) then
    g_step(g_world, Dt, Vi, Pi);
end;

procedure PhysSetContactCallback(Cb: Pointer);
begin
  if g_active and (g_world <> nil) then
    g_contactCb(g_world, Cb);
end;

// 4 面世界墙：body(allowSleep=0) + box(半宽高 1x100 / 100x1, fric=0 rest=0.5 dens=0)，
// 先全部建完再设位（与录制顺序一致）。
procedure CreateWalls;
var
  def: TPhysBodyDef;
  sd: TPhysShapeDef;
  bodies: array[0..3] of Pointer;
  i: Integer;
begin
  for i := 0 to 3 do
  begin
    FillChar(def, SizeOf(def), 0);
    def.world := g_world;
    def.allowSleep := 0;
    bodies[i] := g_createBody(@def);
    FillChar(sd, SizeOf(sd), 0);
    sd.body := bodies[i];
    sd.friction := 0.0;
    sd.restitution := 0.5;
    sd.density := 0.0;
    if Odd(i) then
    begin
      sd.c := 100.0;
      sd.d := 1.0;
    end
    else
    begin
      sd.c := 1.0;
      sd.d := 100.0;
    end;
    g_shapeBox(@sd);
  end;
  SetXForm(bodies[0], -kWallX, 0.0, 0.0);
  SetXForm(bodies[1], 0.0, -kWallY, 0.0);
  SetXForm(bodies[2], kWallX, 0.0, 0.0);
  SetXForm(bodies[3], 0.0, kWallY, 0.0);
end;

function PhysStart: Boolean;
var
  buf: array[0..MAX_PATH - 1] of Char;
  aabb: TPhysAABB;
  gravity: TPhysVec2;
begin
  if g_active then
    Exit(True);
  FillChar(buf, SizeOf(buf), 0);
  if GetEnvironmentVariable('HOST_B2DLL', @buf, MAX_PATH) = 0 then
    lstrcpyn(@buf, 'b2Physics.dll', MAX_PATH);
  g_dll := LoadLibrary(PChar(@buf));
  if g_dll = 0 then
    Exit(False);
  g_createWorld := TCreateWorldFn(GetProcAddress(g_dll, 'b2_CreateWorld'));
  g_createBody := TCreateBodyFn(GetProcAddress(g_dll, 'b2_World_CreateBody'));
  g_setXForm := TSetXFormFn(GetProcAddress(g_dll, 'b2_Body_SetXForm'));
  g_shapeCircle := TShapeFn(GetProcAddress(g_dll, 'b2_Body_CreateShape_Circle'));
  g_shapeBox := TShapeFn(GetProcAddress(g_dll, 'b2_Body_CreateShape_Box'));
  g_mass := TMassFn(GetProcAddress(g_dll, 'b2_Body_SetMassFromShapes'));
  g_setUserData := TUserDataFn(GetProcAddress(g_dll, 'b2_Body_SetUserData'));
  g_step := TStepFn(GetProcAddress(g_dll, 'b2_World_Step'));
  g_contactCb := TContactCbFn(GetProcAddress(g_dll, 'b2_World_SetContactListenerCallBack'));
  if not (Assigned(g_createWorld) and Assigned(g_createBody) and Assigned(g_setXForm) and
    Assigned(g_shapeCircle) and Assigned(g_shapeBox) and Assigned(g_mass) and
    Assigned(g_setUserData) and Assigned(g_step) and Assigned(g_contactCb)) then
    Exit(False);
  aabb.lo.x := -100.0;
  aabb.lo.y := -100.0;
  aabb.hi.x := 100.0;
  aabb.hi.y := 100.0;
  gravity.x := 0.0;
  gravity.y := 0.0;
  g_world := g_createWorld(@aabb, @gravity);
  if g_world = nil then
    Exit(False);
  g_objCount := 0;
  g_active := True;
  CreateWalls;
  Result := True;
end;

end.
