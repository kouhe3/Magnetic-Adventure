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
  TPhysRevolute = packed record
    world, body1, body2: Pointer;
    anchor: TPhysVec2;
    enableLimit: Byte;
    pad1: array[0..2] of Byte;
    lower, upper: Single;
    enableMotor: Byte;
    pad2: array[0..2] of Byte;
    motorSpeed, maxMotorTorque: Single;
    collide: Byte;
    pad3: array[0..2] of Byte;
  end;
  TPhysPrismatic = packed record
    world, body1, body2: Pointer;
    anchor, axis: TPhysVec2;
    enableLimit: Byte;
    pad1: array[0..2] of Byte;
    lower, upper: Single;
    enableMotor: Byte;
    pad2: array[0..2] of Byte;
    motorSpeed, maxMotorForce: Single;
    collide: Byte;
    pad3: array[0..2] of Byte;
  end;
  TPhysGear = packed record
    world, body1, body2, joint1, joint2: Pointer;
    ratio: Single;
  end;
  TPhysPolyDef = packed record
    body: Pointer;
    friction, restitution, density: Single;
    userData: Pointer;
    vertexCount: Integer;
    vertices: array[0..15] of Single;
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
// Add_Ball(0,x,y,ang,style)：圆 body；style 5 的常量见 Burned Out 录制（F336）。
function PhysAddBall(Id: Integer; X, Y, Angle, Style: Double): Pointer;
function PhysAddSimplePhysCircle(Id: Integer; Fric, Dens, Rest, X, Y, Radius: Double): Pointer;
function PhysAddWoodGear(Id: Integer; X, Y, Angle, Size: Double): Pointer;
function PhysAddWoodWall(Id: Integer; X, Y, Angle: Double): Pointer;
function PhysAddSwitchArm(Id: Integer; X, Y, Angle: Double): Pointer;
function PhysAddBarDoor(Id: Integer; X, Y, Angle, Style: Double): Pointer;
function PhysAddLock(Id: Integer; X, Y, Angle, Style: Double): Pointer;
function PhysAddKey(Id: Integer; X, Y, Angle, Style: Double): Pointer;
function PhysAddWoodBox(Id: Integer; X, Y, Angle, Style: Double): Pointer;
function PhysAddWoodFormWall(Id: Integer; X, Y, Angle, Style: Double): Pointer;
function PhysAddPushButton(Id: Integer; X, Y, Angle, Style: Double): Pointer;
function PhysAddLaser(Id: Integer; X, Y, Angle, Style: Double): Pointer;
function PhysAddRack(Id: Integer; X, Y, Angle, Style: Double): Pointer;
function PhysAddMagnet(Id: Integer; X, Y, Angle, Style: Double): Pointer;
function PhysAddScrewDriver(Id: Integer; X, Y, Angle, Style: Double): Pointer;
function PhysAddShankBody(Id: Integer; X, Y, Angle, Style: Double): Pointer;
function PhysAddLamp(Id: Integer; X, Y, Angle, Style: Double): Pointer;
function PhysAddCork(Id: Integer; X, Y, Angle, Style: Double): Pointer;
function PhysAddTestTube(Id: Integer; X, Y, Angle, Style: Double): Pointer;
function PhysAddToothGear(Id: Integer; X, Y, Angle, Style: Double): Pointer;
function PhysAddWoodDetail(Id: Integer; X, Y, Angle, Style: Double): Pointer;
function PhysAddHammerParts(Id: Integer; X, Y, Angle, Style: Double): Pointer;
function PhysAddPhysicObjectWithAdvGraph(Id: Integer; X, Y, Angle: Double): Pointer;
function PhysAttachShapeCircle(Id: Integer; Fric, Rest, Dens, LX, LY, Radius: Double): Pointer;
function PhysAddJointNail(Id, B1, B2: Integer; X, Y: Double): Pointer;
function PhysAddJointSimpleRevolute(Id, B1, B2: Integer; X, Y: Double): Pointer;
function PhysAddJointSimpleGear(Id, B1, B2, J1, J2: Integer; Ratio: Double): Pointer;
function PhysAddJointSimplePrismatic(Id, B1, B2: Integer; AX, AY, VX, VY: Double): Pointer;
procedure PhysSetJointLimits(Id: Integer; Enable: Boolean; Lower, Upper: Double);
procedure PhysSetJointMotors(Id: Integer; Enable: Boolean; Speed, Torque: Double);
// 诊断用：把对象瞬移到指定位置（HOST_PHYS_MOVE 自检，不参与正式语义）。
procedure PhysSetBodyPos(Id: Integer; X, Y, Angle: Double);
// Get_ScrObjPos：对象的物理位置/角度（无效 id 返回 0,0,0）。
procedure PhysGetBodyPos(Id: Integer; out X, Y, Angle: Double);
// T6.4b-1：在 body 中心施加世界力（不产生力矩；原版磁铁力律见 F386）。
procedure PhysApplyForce(Id: Integer; Fx, Fy: Double);
// Local_ToWorld / World_ToLocal：按 body 的 (x,y,angle) 做平移+旋转（不含 graph scale）。
procedure PhysLocalToWorld(Id: Integer; LX, LY: Double; out X, Y: Double);
procedure PhysWorldToLocal(Id: Integer; WX, WY: Double; out X, Y: Double);
// Set_PhysParams / Get_PhysParams / Set_PhysFilterData / Re_Filter。
procedure PhysSetPhysParams(Id: Integer; Density, Friction, Restitution: Double);
procedure PhysGetPhysParams(Id: Integer; out Density, Friction, Restitution: Double);
procedure PhysSetPhysFilter(Id: Integer; Category, Mask, Group: Integer);
procedure PhysReFilter(Id: Integer);
function PhysAddMetallScrew(Id: Integer; X, Y, Angle, Style: Double): Pointer;
function PhysAddMetallGear(Id: Integer; X, Y, Angle, Style: Double): Pointer;
procedure PhysAttachShapePolygon(Id: Integer; Fric, Rest, Dens: Double;
  Count: Integer; Verts: PDouble);
// Add_Rope：N 个 Box 链节 + N-1 个 Revolute（几何与 style 表见 F289）。
function PhysAddRope(Id: Integer; X, Y, Style: Double; Count: Integer;
  Angles: PDouble): Pointer;
// Get_RopePhysItem 的句柄（0 基；越界返回 0；rope id 本身指向第 0 节）。
function PhysGetRopeItemId(RopeId, Index: Integer): Integer;

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
  TJointFn = function(Def: Pointer): Pointer; cdecl;
  TJointBoolFn = procedure(J: Pointer; Enable: Integer); cdecl;
  TJointLimitsFn = procedure(J: Pointer; Lower, Upper: Single); cdecl;
  TJointFloatFn = procedure(J: Pointer; V: Single); cdecl;
  TGetXFormFn = function(Body, OutXf: Pointer): Pointer; cdecl;
  TApplyForceFn = procedure(Body, Force, Point: Pointer); cdecl;
  TShapeFloatFn = procedure(Shape: Pointer; V: Single); cdecl;
  TSetFilterFn = function(Shape, Filter: Pointer): Pointer; cdecl;
  TReFilterFn = procedure(Shape: Pointer); cdecl;
  TPolyShapeFn = function(Def: Pointer): Pointer; cdecl;

type
  TPhysObj = record
    Id: Integer;
    Body: Pointer;
    ShapeCount: Integer;
    // 一个 body 可能挂很多形状（lvl38 的 body 8 有 10 个，ToothGear 单条 12 个）。
    Shapes: array[0..63] of Pointer;
    Density, Friction, Restitution: Single;
  end;

  TPhysJoint = record
    Id: Integer;
    Joint: Pointer;
  end;

  // 一根绳 = N 个链节对象；Set_PhysParams 对 rope id 要逐链节生效（F289 的录制序列：
  // 密度×N（每节 SetMass）→ 摩擦×N → 弹性×N，全按链节顺序）。
  TPhysRope = record
    Id: Integer;
    Count: Integer;
    Items: array[0..63] of Integer;
  end;

const
  MAX_OBJECTS = 2048;
  kGearRadius: array[1..6] of Single = (1.6, 1.8, 2.0, 2.2, 2.4, 4.33);
  kMetalGearRadius: array[1..6] of Single = (1.6, 1.8, 2.0, 2.2, 2.4, 4.33);
  // Add_Rope 的 style 表（10 个 rope 关的录制逐 style 读出，F289）：
  // 链节 Box 半宽/半高、密度；摩擦恒 0.3、弹性恒 0。
  kRopeHalfW: array[0..3] of Single = (0.77, 0.77, 0.275, 0.77);
  kRopeHalfH: array[0..3] of Single = (0.2, 0.2, 0.2, 0.5);
  kRopeDensity: array[0..3] of Single = (0.5, 0.5, 3.0, 0.2);
  // 链节 id 派生基数：rope id（1e3 量级）* 100 + 索引 ⇒ 与 Lua 的 Add_* id 不重叠。
  kRopeItemBase = 1000000;
  // MetallScrew 的六边形（level 1 录制：r=1.4，顶点 = 1.4·cos30° = 1.212435565）。
  kScrewVerts: array[0..11] of Single =
    (-1.4, 0.0, -0.7, -1.2124355652982142, 0.7, -1.2124355652982142,
     1.4, 0.0, 0.7, 1.2124355652982142, -0.7, 1.2124355652982142);
  kWallX = 31.305818557739258;  // 原版 float32 = 0xC1FA7251（F276 的录制值）
  kWallY = 23.0;

{$I wfw_table.inc}
{$I phys_shapes_gen.inc}

var
  g_dll: HMODULE;
  g_world: Pointer;
  g_active: Boolean;
  g_createWorld: TCreateWorldFn;
  g_createBody: TCreateBodyFn;
  g_setXForm: TSetXFormFn;
  g_shapeCircle: TShapeFn;
  g_shapeBox: TShapeFn;
  g_shapePoly: TPolyShapeFn;
  g_mass: TMassFn;
  g_setUserData: TUserDataFn;
  g_step: TStepFn;
  g_contactCb: TContactCbFn;
  g_jointRev: TJointFn;
  g_jointPri: TJointFn;
  g_jointGear: TJointFn;
  g_jointEnableLimit: TJointBoolFn;
  g_jointEnableMotor: TJointBoolFn;
  g_jointSetLimits: TJointLimitsFn;
  g_jointSetMotorSpeed: TJointFloatFn;
  g_jointSetMaxTorque: TJointFloatFn;
  g_getXForm: TGetXFormFn;
  g_applyForce: TApplyForceFn;
  g_shapeSetDensity: TShapeFloatFn;
  g_shapeSetFriction: TShapeFloatFn;
  g_shapeSetRestitution: TShapeFloatFn;
  g_shapeSetFilter: TSetFilterFn;
  g_reFilter: TReFilterFn;
  g_objs: array[0..MAX_OBJECTS - 1] of TPhysObj;
  g_objCount: Integer;
  g_joints: array[0..MAX_OBJECTS - 1] of TPhysJoint;
  g_jointCount: Integer;
  g_ropes: array[0..63] of TPhysRope;
  g_ropeCount: Integer;

function RopeIndex(Id: Integer): Integer; forward;

function PhysActive: Boolean;
begin
  Result := g_active;
end;

procedure PhysResetObjects;
begin
  g_objCount := 0;
  g_jointCount := 0;
  g_ropeCount := 0;
end;

function PhysBodyOf(Id: Integer): Pointer;
var
  i, r: Integer;
begin
  for i := 0 to g_objCount - 1 do
    if g_objs[i].Id = Id then
      Exit(g_objs[i].Body);
  // rope id 指向第 0 节（F289：录制里 `Add_JointNail(null, rope, …)` 连的是 link[0]）。
  r := RopeIndex(Id);
  if r >= 0 then
    Exit(PhysBodyOf(g_ropes[r].Items[0]));
  Result := nil;
end;

function RopeIndex(Id: Integer): Integer;
var
  i: Integer;
begin
  for i := 0 to g_ropeCount - 1 do
    if g_ropes[i].Id = Id then
      Exit(i);
  Result := -1;
end;

procedure RegBody(Id: Integer; Body: Pointer);
begin
  if g_objCount < MAX_OBJECTS then
  begin
    g_objs[g_objCount].Id := Id;
    g_objs[g_objCount].Body := Body;
    g_objs[g_objCount].ShapeCount := 0;
    g_objs[g_objCount].Density := 0.0;
    g_objs[g_objCount].Friction := 0.0;
    g_objs[g_objCount].Restitution := 0.0;
    Inc(g_objCount);
  end;
end;

function ObjIndex(Id: Integer): Integer;
var
  i: Integer;
begin
  for i := 0 to g_objCount - 1 do
    if g_objs[i].Id = Id then
      Exit(i);
  Result := -1;
end;

// 工厂内部子对象的 id（rope 链节、HammerParts 的锤头）：rope id*100 + 索引，
// 与 Lua 的 Add_* id（1e3 量级）不重叠（F289）。
function SubItemId(Id, Index: Integer): Integer;
begin
  Result := kRopeItemBase + Id * 100 + Index;
end;

procedure NoteShape(Body, Shape: Pointer; Dens, Fric, Rest: Single);
var
  i: Integer;
begin
  for i := 0 to g_objCount - 1 do
    if g_objs[i].Body = Body then
    begin
      if g_objs[i].ShapeCount < 64 then
      begin
        g_objs[i].Shapes[g_objs[i].ShapeCount] := Shape;
        Inc(g_objs[i].ShapeCount);
      end;
      g_objs[i].Density := Dens;
      g_objs[i].Friction := Fric;
      g_objs[i].Restitution := Rest;
      Exit;
    end;
end;

procedure RegJoint(Id: Integer; Joint: Pointer);
begin
  if g_jointCount < MAX_OBJECTS then
  begin
    g_joints[g_jointCount].Id := Id;
    g_joints[g_jointCount].Joint := Joint;
    Inc(g_jointCount);
  end;
end;

function JointOf(Id: Integer): Pointer;
var
  i: Integer;
begin
  for i := 0 to g_jointCount - 1 do
    if g_joints[i].Id = Id then
      Exit(g_joints[i].Joint);
  Result := nil;
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
  NoteShape(Body, Result, Dens, Fric, Rest);
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
  NoteShape(Body, Result, Dens, Fric, Rest);
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

function BuildFromStyle(Id: Integer; X, Y: Double; Angle: Double;
  const info: TGenStyleInfo): Pointer; forward;

function PhysAddSimplePhysicObject(Id: Integer; X, Y, Angle: Double): Pointer;
begin
  if not g_active then
    Exit(nil);
  Result := NewBody(Id, X, Y, Angle, True);
end;

function PhysAddBall(Id: Integer; X, Y, Angle, Style: Double): Pointer;
var
  b: Pointer;
begin
  if not g_active then
    Exit(nil);
  b := NewBody(Id, X, Y, Angle, True);
  if b <> nil then
    // Burned Out 录制：8 个 Add_Ball(style=5) 均为 Circle fric .7 / rest .4 / dens .3 / r .6。
    AttachCircle(b, 0.7, 0.4, 0.3, 0.0, 0.0, 0.6);
  Result := b;
end;

{ Add_SimplePhysCircle(fric, dens, rest, x, y, radius)：录制 F283 证明第 2/3 个实参是
  密度/弹性，不是角度——body angle 恒 0（The Old Clock 两个实例的 shape 与 xform 逐项相同）。 }
function PhysAddSimplePhysCircle(Id: Integer; Fric, Dens, Rest, X, Y, Radius: Double): Pointer;
var
  b: Pointer;
begin
  if not g_active then
    Exit(nil);
  b := NewBody(Id, X, Y, 0.0, True);
  if b <> nil then
    AttachCircle(b, Fric, Rest, Dens, 0.0, 0.0, Radius);
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

// 内联多边形（顶点顺序照抄原版 def；Key 的钥匙齿从录制读出，F285）。
function AttachPolyBody(Body: Pointer; Fric, Rest, Dens: Single;
  Count: Integer; const Verts: array of Double): Pointer;
var
  d: TPhysPolyDef;
  i: Integer;
begin
  FillChar(d, SizeOf(d), 0);
  d.body := Body;
  d.friction := Fric;
  d.restitution := Rest;
  d.density := Dens;
  d.vertexCount := Count;
  for i := 0 to Count - 1 do
  begin
    d.vertices[2 * i] := Verts[2 * i];
    d.vertices[2 * i + 1] := Verts[2 * i + 1];
  end;
  Result := g_shapePoly(@d);
  NoteShape(Body, Result, Dens, Fric, Rest);
  if Assigned(g_mass) then
    g_mass(Body);
end;

// 以下六个工厂的常量全部来自 52 关录制的 body def（F284 的聚合表）：
// 每个绑定在 16–26 个关卡里形状完全一致（Rack 按 style 两档）。
function PhysAddBarDoor(Id: Integer; X, Y, Angle, Style: Double): Pointer;
var
  st: Integer;
begin
  st := Round(Style);
  if (st < 1) or (st > 2) or (kBarDoor[st].n < 0) then
    st := 1;
  Result := BuildFromStyle(Id, X, Y, Angle, kBarDoor[st]);
end;

function PhysAddLock(Id: Integer; X, Y, Angle, Style: Double): Pointer;
var
  st: Integer;
begin
  st := Round(Style);
  if (st < 1) or (st > 5) or (kLock[st].n < 0) then
    st := 4;
  Result := BuildFromStyle(Id, X, Y, Angle, kLock[st]);
end;

function PhysAddKey(Id: Integer; X, Y, Angle, Style: Double): Pointer;
var
  st: Integer;
begin
  st := Round(Style);
  if (st < 2) or (st > 5) or (kKey[st].n < 0) then
    st := 2;
  Result := BuildFromStyle(Id, X, Y, Angle, kKey[st]);
end;

function PhysAddWoodBox(Id: Integer; X, Y, Angle, Style: Double): Pointer;
var
  b: Pointer;
begin
  if not g_active then
    Exit(nil);
  b := NewBody(Id, X, Y, Angle, True);
  if b <> nil then
    AttachBox(b, 0.7, 0.1, 0.3, 0.0, 0.0, 1.8, 1.8);
  Result := b;
end;

// WoodFormWall：11 个 style 的形状表在 wfw_table.inc（逐 style 从录制读出，F285）。
function PhysAddWoodFormWall(Id: Integer; X, Y, Angle, Style: Double): Pointer;
var
  b: Pointer;
  st, i, j: Integer;
  spec: TWFWShape;
  verts: array[0..9] of Double;
begin
  if not g_active then
    Exit(nil);
  b := NewBody(Id, X, Y, Angle, True);
  if b = nil then
    Exit(nil);
  st := Round(Style);
  if (st < 1) or (st > 11) then
    st := 1;
  for i := 0 to kWFW[st].n - 1 do
  begin
    spec := kWFW[st].sh[i];
    if spec.kind = 1 then
      AttachBox(b, 0.7, 0.4, 0.6, spec.d[0], spec.d[1], spec.d[2], spec.d[3])
    else if spec.n > 0 then
    begin
      for j := 0 to 2 * spec.n - 1 do
        verts[j] := spec.d[j];
      AttachPolyBody(b, 0.7, 0.4, 0.6, spec.n, verts);
    end;
  end;
  Result := b;
end;

function PhysAddPushButton(Id: Integer; X, Y, Angle, Style: Double): Pointer;
begin
  Result := BuildFromStyle(Id, X, Y, Angle, kPushButton[1]);
end;

function PhysAddLaser(Id: Integer; X, Y, Angle, Style: Double): Pointer;
begin
  Result := BuildFromStyle(Id, X, Y, Angle, kLaser[1]);
end;

function PhysAddRack(Id: Integer; X, Y, Angle, Style: Double): Pointer;
var
  st: Integer;
begin
  st := Round(Style);
  if (st < 1) or (st > 2) then
    st := 1;
  Result := BuildFromStyle(Id, X, Y, Angle, kRack[st]);
end;

// 通用建体：形状来自 physics_shapes_gen.inc（由 tools/gen_phys_shapes.py 从录制生成）。
function BuildFromStyle(Id: Integer; X, Y, Angle: Double;
  const info: TGenStyleInfo): Pointer;
var
  b: Pointer;
  i, j: Integer;
  spec: TGenShape;
  verts: array[0..15] of Double;
begin
  if not g_active then
    Exit(nil);
  b := NewBody(Id, X, Y, Angle, True);
  if b = nil then
    Exit(nil);
  for i := 0 to info.n - 1 do
  begin
    spec := kGenShapes[info.off + i];
    case spec.kind of
      1: AttachBox(b, spec.f, spec.r, spec.d, spec.v[0], spec.v[1], spec.v[2], spec.v[3]);
      2: AttachCircle(b, spec.f, spec.r, spec.d, spec.v[0], spec.v[1], spec.v[2]);
    else
      if spec.n > 0 then
      begin
        for j := 0 to 2 * spec.n - 1 do
          verts[j] := spec.v[j];
        AttachPolyBody(b, spec.f, spec.r, spec.d, spec.n, verts);
      end;
    end;
  end;
  Result := b;
end;

function PhysAddMagnet(Id: Integer; X, Y, Angle, Style: Double): Pointer;
var
  st: Integer;
begin
  st := Round(Style);
  if (st < 1) or (st > 3) then
    st := 1;
  Result := BuildFromStyle(Id, X, Y, Angle, kMagnet[st]);
end;

function PhysAddScrewDriver(Id: Integer; X, Y, Angle, Style: Double): Pointer;
begin
  Result := BuildFromStyle(Id, X, Y, Angle, kScrewDriver[1]);
end;

function PhysAddShankBody(Id: Integer; X, Y, Angle, Style: Double): Pointer;
var
  st: Integer;
begin
  st := Round(Style);
  if (st < 1) or (st > 2) then
    st := 1;
  Result := BuildFromStyle(Id, X, Y, Angle, kShankBody[st]);
end;

function PhysAddLamp(Id: Integer; X, Y, Angle, Style: Double): Pointer;
var
  st: Integer;
begin
  st := Round(Style);
  if (st < 3) or (st > 4) then
    st := 3;
  Result := BuildFromStyle(Id, X, Y, Angle, kLamp[st]);
end;

function PhysAddCork(Id: Integer; X, Y, Angle, Style: Double): Pointer;
var
  st: Integer;
begin
  st := Round(Style);
  if (st < 1) or (st > 4) or (kCork[st].n < 0) then
    st := 1;
  Result := BuildFromStyle(Id, X, Y, Angle, kCork[st]);
end;

function PhysAddTestTube(Id: Integer; X, Y, Angle, Style: Double): Pointer;
begin
  Result := BuildFromStyle(Id, X, Y, Angle, kTestTube[1]);
end;

function PhysAddToothGear(Id: Integer; X, Y, Angle, Style: Double): Pointer;
begin
  Result := BuildFromStyle(Id, X, Y, Angle, kToothGear[1]);
end;

function PhysAddWoodDetail(Id: Integer; X, Y, Angle, Style: Double): Pointer;
var
  st: Integer;
begin
  st := Round(Style);
  if (st < 1) or (st > 3) then
    st := 1;
  Result := BuildFromStyle(Id, X, Y, Angle, kWoodDetail[st]);
end;

// Add_HammerParts(x, y, angle, style)：**两个** body——手柄（style 表）+ 锤头，中间一个
// 0..0 限位的 Revolute（lvl29 录制 seq 569–597：手柄 Box 3.2/0.594，锤头在 +3.76 处
// Box 0.56/1.82（fric 0 / rest 0.7 / dens 1），锚点在 +3.2 处）。Set_PhysParams 只作用于
// 手柄（录制的 setter 只有一条链），锤头用派生 id 单独登记。
function PhysAddHammerParts(Id: Integer; X, Y, Angle, Style: Double): Pointer;
var
  head: Pointer;
  hx, hy, ax, ay: Single;
  d: TPhysRevolute;
  j: Pointer;
begin
  if not g_active then
    Exit(nil);
  Result := BuildFromStyle(Id, X, Y, Angle, kHammerParts[1]);
  hx := X + 3.76 * Cos(Angle);
  hy := Y + 3.76 * Sin(Angle);
  head := NewBody(SubItemId(Id, 1), hx, hy, Angle, True);
  if head <> nil then
    AttachBox(head, 0.0, 0.7, 1.0, 0.0, 0.0, 0.56, 1.82);
  if (Result = nil) or (head = nil) then
    Exit;
  ax := X + 3.2 * Cos(Angle);
  ay := Y + 3.2 * Sin(Angle);
  FillChar(d, SizeOf(d), 0);
  d.world := g_world;
  d.body1 := Result;
  d.body2 := head;
  d.anchor.x := ax;
  d.anchor.y := ay;
  j := g_jointRev(@d);
  if j <> nil then
  begin
    g_jointEnableLimit(j, 1);
    g_jointSetLimits(j, 0.0, 0.0);
  end;
end;

// Add_PhysicObjectWithAdvGraph(x, y, angle, …)：两个多边形（形状取自录制，F285）。
// Add_PhysicObjectWithAdvGraph(x, y, angle, …)：只建 body，两块多边形由随后的
// Attach_ShapePolygon 挂上（录制里那 2 个 shape 就来自这两条调用，F285）。
function PhysAddPhysicObjectWithAdvGraph(Id: Integer; X, Y, Angle: Double): Pointer;
begin
  if not g_active then
    Exit(nil);
  Result := NewBody(Id, X, Y, Angle, True);
end;

function MetalGearRadius(Style: Integer): Single;
begin
  if (Style >= 1) and (Style <= 6) then
    Result := kMetalGearRadius[Style]
  else
    Result := kMetalGearRadius[1];
end;

function PhysAddMetallScrew(Id: Integer; X, Y, Angle, Style: Double): Pointer;
var
  b: Pointer;
  d: TPhysPolyDef;
  i: Integer;
  sh: Pointer;
begin
  if not g_active then
    Exit(nil);
  b := NewBody(Id, X, Y, Angle, True);
  if b = nil then
    Exit(nil);
  FillChar(d, SizeOf(d), 0);
  d.body := b;
  d.friction := 1.0;
  d.restitution := 0.1;
  d.density := 0.3;
  d.vertexCount := 6;
  for i := 0 to 11 do
    d.vertices[i] := kScrewVerts[i];
  sh := g_shapePoly(@d);
  NoteShape(b, sh, 0.3, 1.0, 0.1);
  g_mass(b);
  Result := b;
end;

function PhysAddMetallGear(Id: Integer; X, Y, Angle, Style: Double): Pointer;
var
  b: Pointer;
begin
  if not g_active then
    Exit(nil);
  b := NewBody(Id, X, Y, Angle, True);
  if b <> nil then
    AttachCircle(b, 1.0, 0.1, 0.3, 0.0, 0.0, MetalGearRadius(Round(Style)));
  Result := b;
end;

procedure PhysAttachShapePolygon(Id: Integer; Fric, Rest, Dens: Double;
  Count: Integer; Verts: PDouble);
var
  b: Pointer;
  d: TPhysPolyDef;
  i, n: Integer;
  sh: Pointer;
begin
  if not g_active then
    Exit;
  b := PhysBodyOf(Id);
  if b = nil then
    Exit;
  n := Count;
  if n < 3 then
    Exit;
  if n > 8 then
    n := 8;
  FillChar(d, SizeOf(d), 0);
  d.body := b;
  d.friction := Fric;
  d.restitution := Rest;
  d.density := Dens;
  d.vertexCount := n;
  for i := 0 to n - 1 do
  begin
    d.vertices[2 * i] := Verts[2 * i];
    d.vertices[2 * i + 1] := Verts[2 * i + 1];
  end;
  sh := g_shapePoly(@d);
  NoteShape(b, sh, Dens, Fric, Rest);
  g_mass(b);
end;

// ---- Add_Rope（T6.3d / F289）--------------------------------------------
// 几何：首节在 (x,y)、angle_i = a_i；相邻两节共享锚点
//   anchor_i = p_i + h·u(a_i)，p_{i+1} = anchor_i + h·u(a_{i+1})，h = halfW/1.1。
// 每步都落 Single 才能与录制的 float32 位置对上（`work/probe_rope5.py` 复核：
// 47 个链节 + 64 步递推，误差 ≤1 float32 ulp）。相邻链节是一个无 id、
// 无 limit/motor、collide=0 的 Revolute。
function PhysAddRope(Id: Integer; X, Y, Style: Double; Count: Integer;
  Angles: PDouble): Pointer;
var
  i, st, n, itemId: Integer;
  hw, hh, dens, h: Single;
  px, py, ax, ay, a1, a2: Single;
  bodies: array[0..63] of Pointer;
  anchorX, anchorY: array[0..63] of Single;
  d: TPhysRevolute;
begin
  if not g_active then
    Exit(nil);
  n := Count;
  if n <= 0 then
    Exit(nil);
  if n > 64 then
    n := 64;
  st := Round(Style);
  if (st < 0) or (st > 3) then
    st := 0;
  hw := kRopeHalfW[st];
  hh := kRopeHalfH[st];
  dens := kRopeDensity[st];
  h := hw / 1.1;

  px := X;
  py := Y;
  for i := 0 to n - 1 do
  begin
    a1 := Angles[i];
    itemId := SubItemId(Id, i);
    bodies[i] := NewBody(itemId, px, py, a1, True);
    if bodies[i] <> nil then
      AttachBox(bodies[i], 0.3, 0.0, dens, 0.0, 0.0, hw, hh);
    if i < n - 1 then
    begin
      ax := px + h * Cos(a1);
      ay := py + h * Sin(a1);
      anchorX[i] := ax;
      anchorY[i] := ay;
      a2 := Angles[i + 1];
      px := ax + h * Cos(a2);
      py := ay + h * Sin(a2);
    end;
  end;

  for i := 0 to n - 2 do
  begin
    if (bodies[i] = nil) or (bodies[i + 1] = nil) then
      Continue;
    FillChar(d, SizeOf(d), 0);
    d.world := g_world;
    d.body1 := bodies[i];
    d.body2 := bodies[i + 1];
    d.anchor.x := anchorX[i];
    d.anchor.y := anchorY[i];
    g_jointRev(@d);
  end;

  if g_ropeCount < 64 then
  begin
    g_ropes[g_ropeCount].Id := Id;
    g_ropes[g_ropeCount].Count := n;
    for i := 0 to n - 1 do
      g_ropes[g_ropeCount].Items[i] := SubItemId(Id, i);
    Inc(g_ropeCount);
  end;
  Result := bodies[0];
end;

function PhysGetRopeItemId(RopeId, Index: Integer): Integer;
var
  r: Integer;
begin
  r := RopeIndex(RopeId);
  if (r < 0) or (Index < 0) or (Index >= g_ropes[r].Count) then
    Exit(0);
  Result := g_ropes[r].Items[Index];
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

function PhysAddJointNail(Id, B1, B2: Integer; X, Y: Double): Pointer;
var
  d: TPhysRevolute;
  pb1, pb2: Pointer;
begin
  if not g_active then
    Exit(nil);
  pb1 := PhysBodyOf(B1);
  pb2 := PhysBodyOf(B2);
  if (pb1 = nil) or (pb2 = nil) then
    Exit(nil);
  FillChar(d, SizeOf(d), 0);
  d.world := g_world;
  d.body1 := pb1;
  d.body2 := pb2;
  d.anchor.x := X;
  d.anchor.y := Y;
  Result := g_jointRev(@d);
  RegJoint(Id, Result);
end;

function PhysAddJointSimpleRevolute(Id, B1, B2: Integer; X, Y: Double): Pointer;
begin
  Result := PhysAddJointNail(Id, B1, B2, X, Y);
end;

function PhysAddJointSimpleGear(Id, B1, B2, J1, J2: Integer; Ratio: Double): Pointer;
var
  d: TPhysGear;
  pb1, pb2: Pointer;
begin
  if not g_active then
    Exit(nil);
  pb1 := PhysBodyOf(B1);
  pb2 := PhysBodyOf(B2);
  if (pb1 = nil) or (pb2 = nil) then
    Exit(nil);
  FillChar(d, SizeOf(d), 0);
  d.world := g_world;
  d.body1 := pb1;
  d.body2 := pb2;
  d.joint1 := JointOf(J1);
  d.joint2 := JointOf(J2);
  d.ratio := Ratio;
  Result := g_jointGear(@d);
  RegJoint(Id, Result);
end;

function PhysAddJointSimplePrismatic(Id, B1, B2: Integer; AX, AY, VX, VY: Double): Pointer;
var
  d: TPhysPrismatic;
  pb1, pb2: Pointer;
begin
  if not g_active then
    Exit(nil);
  pb1 := PhysBodyOf(B1);
  pb2 := PhysBodyOf(B2);
  if (pb1 = nil) or (pb2 = nil) then
    Exit(nil);
  FillChar(d, SizeOf(d), 0);
  d.world := g_world;
  d.body1 := pb1;
  d.body2 := pb2;
  d.anchor.x := AX;
  d.anchor.y := AY;
  d.axis.x := VX;
  d.axis.y := VY;
  // 原版 def 里 motorSpeed=100（enableMotor=0，无行为影响；F276 录制观测）。
  d.motorSpeed := 100.0;
  Result := g_jointPri(@d);
  RegJoint(Id, Result);
end;

procedure PhysSetJointLimits(Id: Integer; Enable: Boolean; Lower, Upper: Double);
var
  j: Pointer;
begin
  if not g_active then
    Exit;
  j := JointOf(Id);
  if j = nil then
    Exit;
  if Enable then
    g_jointEnableLimit(j, 1)
  else
    g_jointEnableLimit(j, 0);
  g_jointSetLimits(j, Lower, Upper);
end;

procedure PhysSetJointMotors(Id: Integer; Enable: Boolean; Speed, Torque: Double);
var
  j: Pointer;
begin
  if not g_active then
    Exit;
  j := JointOf(Id);
  if j = nil then
    Exit;
  if Enable then
    g_jointEnableMotor(j, 1)
  else
    g_jointEnableMotor(j, 0);
  g_jointSetMotorSpeed(j, Speed);
  g_jointSetMaxTorque(j, Torque);
end;

procedure PhysSetBodyPos(Id: Integer; X, Y, Angle: Double);
var
  b: Pointer;
begin
  if not g_active then
    Exit;
  b := PhysBodyOf(Id);
  if b <> nil then
    SetXForm(b, X, Y, Angle);
end;

procedure PhysGetBodyPos(Id: Integer; out X, Y, Angle: Double);
var
  b: Pointer;
  xf: TPhysXForm;
begin
  X := 0.0;
  Y := 0.0;
  Angle := 0.0;
  if not g_active then
    Exit;
  b := PhysBodyOf(Id);
  if b = nil then
    Exit;
  g_getXForm(b, @xf);
  X := xf.x;
  Y := xf.y;
  Angle := xf.angle;
end;

procedure PhysApplyForce(Id: Integer; Fx, Fy: Double);
var
  b: Pointer;
  f, p: TPhysVec2;
  x, y, a: Double;
begin
  if not g_active then Exit;
  b := PhysBodyOf(Id);
  if b = nil then Exit;
  PhysGetBodyPos(Id, x, y, a);
  f.x := Fx;
  f.y := Fy;
  p.x := x;
  p.y := y;
  g_applyForce(b, @f, @p);
end;

procedure PhysLocalToWorld(Id: Integer; LX, LY: Double; out X, Y: Double);
var
  bx, by, ba: Double;
  c, s: Double;
begin
  PhysGetBodyPos(Id, bx, by, ba);
  c := Cos(ba);
  s := Sin(ba);
  X := bx + LX * c - LY * s;
  Y := by + LX * s + LY * c;
end;

procedure PhysWorldToLocal(Id: Integer; WX, WY: Double; out X, Y: Double);
var
  bx, by, ba: Double;
  c, s, dx, dy: Double;
begin
  PhysGetBodyPos(Id, bx, by, ba);
  c := Cos(ba);
  s := Sin(ba);
  dx := WX - bx;
  dy := WY - by;
  X := dx * c + dy * s;
  Y := -dx * s + dy * c;
end;

// rope id 的 Set_PhysParams 逐链节生效：录制里是 密度×N（每节 SetMass）→ 摩擦×N →
// 弹性×N，全按链节顺序（lvl08 seq 339–417，F289）。不是"一个 body 多形状"那条路径。
function ApplyRopePhysParams(Id: Integer; Density, Friction, Restitution: Double): Boolean;
var
  r, i, idx: Integer;
begin
  Result := False;
  r := RopeIndex(Id);
  if r < 0 then
    Exit;
  Result := True;
  for i := 0 to g_ropes[r].Count - 1 do
  begin
    idx := ObjIndex(g_ropes[r].Items[i]);
    if idx < 0 then
      Continue;
    if g_objs[idx].ShapeCount > 0 then
      g_shapeSetDensity(g_objs[idx].Shapes[g_objs[idx].ShapeCount - 1], Density);
    g_mass(g_objs[idx].Body);
    g_objs[idx].Density := Density;
  end;
  for i := 0 to g_ropes[r].Count - 1 do
  begin
    idx := ObjIndex(g_ropes[r].Items[i]);
    if (idx >= 0) and (g_objs[idx].ShapeCount > 0) then
    begin
      g_shapeSetFriction(g_objs[idx].Shapes[g_objs[idx].ShapeCount - 1], Friction);
      g_objs[idx].Friction := Friction;
    end;
  end;
  for i := 0 to g_ropes[r].Count - 1 do
  begin
    idx := ObjIndex(g_ropes[r].Items[i]);
    if (idx >= 0) and (g_objs[idx].ShapeCount > 0) then
    begin
      g_shapeSetRestitution(g_objs[idx].Shapes[g_objs[idx].ShapeCount - 1], Restitution);
      g_objs[idx].Restitution := Restitution;
    end;
  end;
end;

procedure PhysSetPhysParams(Id: Integer; Density, Friction, Restitution: Double);
var
  i, idx: Integer;
begin
  if not g_active then
    Exit;
  if ApplyRopePhysParams(Id, Density, Friction, Restitution) then
    Exit;
  idx := ObjIndex(Id);
  if idx < 0 then
    Exit;
  // 形状遍历同样按 body 形状链头→尾（= 形状号从大到小，F285）。
  for i := g_objs[idx].ShapeCount - 1 downto 0 do
    g_shapeSetDensity(g_objs[idx].Shapes[i], Density);
  g_mass(g_objs[idx].Body);
  // 摩擦/弹性只写**最后一个**形状（原版取形状链头；52 关 69 个多形状 body 全部如此，F285）。
  if g_objs[idx].ShapeCount > 0 then
  begin
    g_shapeSetFriction(g_objs[idx].Shapes[g_objs[idx].ShapeCount - 1], Friction);
    g_shapeSetRestitution(g_objs[idx].Shapes[g_objs[idx].ShapeCount - 1], Restitution);
  end;
  g_objs[idx].Density := Density;
  g_objs[idx].Friction := Friction;
  g_objs[idx].Restitution := Restitution;
end;

procedure PhysGetPhysParams(Id: Integer; out Density, Friction, Restitution: Double);
var
  idx: Integer;
begin
  Density := 0.0;
  Friction := 0.0;
  Restitution := 0.0;
  if not g_active then
    Exit;
  idx := ObjIndex(Id);
  if idx < 0 then
    Exit;
  Density := g_objs[idx].Density;
  Friction := g_objs[idx].Friction;
  Restitution := g_objs[idx].Restitution;
end;

procedure PhysSetPhysFilter(Id: Integer; Category, Mask, Group: Integer);
var
  f: TPhysFilter;
  i, idx: Integer;
begin
  if not g_active then
    Exit;
  idx := ObjIndex(Id);
  if idx < 0 then
    Exit;
  f.category := Word(Category);
  f.mask := Word(Mask);
  f.group := SmallInt(Group);
  // 原版按 body 形状链的头部顺序（新形状前插）遍历 ⇒ 形状号从大到小（F285：录制里
  // `SetFilter` 的 slot 是 1,0 / 9,8,7…；正向会逐条对不上）。
  for i := g_objs[idx].ShapeCount - 1 downto 0 do
    g_shapeSetFilter(g_objs[idx].Shapes[i], @f);
end;

procedure PhysReFilter(Id: Integer);
var
  i, idx: Integer;
begin
  if not g_active then
    Exit;
  idx := ObjIndex(Id);
  if idx < 0 then
    Exit;
  for i := g_objs[idx].ShapeCount - 1 downto 0 do
    g_reFilter(g_objs[idx].Shapes[i]);
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
  g_shapePoly := TPolyShapeFn(GetProcAddress(g_dll, 'b2_Body_CreateShape_Polygon'));
  g_mass := TMassFn(GetProcAddress(g_dll, 'b2_Body_SetMassFromShapes'));
  g_setUserData := TUserDataFn(GetProcAddress(g_dll, 'b2_Body_SetUserData'));
  g_step := TStepFn(GetProcAddress(g_dll, 'b2_World_Step'));
  g_contactCb := TContactCbFn(GetProcAddress(g_dll, 'b2_World_SetContactListenerCallBack'));
  g_jointRev := TJointFn(GetProcAddress(g_dll, 'b2_World_Joint_Revolute'));
  g_jointPri := TJointFn(GetProcAddress(g_dll, 'b2_World_Joint_Prismatic'));
  g_jointGear := TJointFn(GetProcAddress(g_dll, 'b2_World_Joint_Gear'));
  g_jointEnableLimit := TJointBoolFn(GetProcAddress(g_dll, 'b2_Joint_EnableLimit'));
  g_jointEnableMotor := TJointBoolFn(GetProcAddress(g_dll, 'b2_Joint_EnableMotor'));
  g_jointSetLimits := TJointLimitsFn(GetProcAddress(g_dll, 'b2_Joint_SetLimits'));
  g_jointSetMotorSpeed := TJointFloatFn(GetProcAddress(g_dll, 'b2_Joint_SetMotorSpeed'));
  g_jointSetMaxTorque := TJointFloatFn(GetProcAddress(g_dll, 'b2_Joint_SetMaxMotorTorque'));
  g_getXForm := TGetXFormFn(GetProcAddress(g_dll, 'b2_Body_GetXForm'));
  g_applyForce := TApplyForceFn(GetProcAddress(g_dll, 'b2_Body_ApplyForce'));
  g_shapeSetDensity := TShapeFloatFn(GetProcAddress(g_dll, 'b2_Shape_SetDensity'));
  g_shapeSetFriction := TShapeFloatFn(GetProcAddress(g_dll, 'b2_Shape_SetFriction'));
  g_shapeSetRestitution := TShapeFloatFn(GetProcAddress(g_dll, 'b2_Shape_SetRestitution'));
  g_shapeSetFilter := TSetFilterFn(GetProcAddress(g_dll, 'b2_Shape_SetFilter'));
  g_reFilter := TReFilterFn(GetProcAddress(g_dll, 'b2_World_ReFilter'));
  if not (Assigned(g_createWorld) and Assigned(g_createBody) and Assigned(g_setXForm) and
    Assigned(g_shapeCircle) and Assigned(g_shapeBox) and Assigned(g_mass) and
    Assigned(g_shapePoly) and
    Assigned(g_setUserData) and Assigned(g_step) and Assigned(g_contactCb) and
    Assigned(g_jointRev) and Assigned(g_jointPri) and Assigned(g_jointGear) and
    Assigned(g_jointEnableLimit) and Assigned(g_jointEnableMotor) and
    Assigned(g_jointSetLimits) and Assigned(g_jointSetMotorSpeed) and
    Assigned(g_jointSetMaxTorque) and Assigned(g_getXForm) and Assigned(g_applyForce) and
    Assigned(g_shapeSetDensity) and Assigned(g_shapeSetFriction) and
    Assigned(g_shapeSetRestitution) and Assigned(g_shapeSetFilter) and
    Assigned(g_reFilter)) then
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
