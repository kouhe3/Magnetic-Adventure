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
function PhysAddSimplePhysCircle(Id: Integer; Fric, Dens, Rest, X, Y, Radius: Double): Pointer;
function PhysAddWoodGear(Id: Integer; X, Y, Angle, Size: Double): Pointer;
function PhysAddWoodWall(Id: Integer; X, Y, Angle: Double): Pointer;
function PhysAddSwitchArm(Id: Integer; X, Y, Angle: Double): Pointer;
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
// Set_PhysParams / Get_PhysParams / Set_PhysFilterData / Re_Filter。
procedure PhysSetPhysParams(Id: Integer; Density, Friction, Restitution: Double);
procedure PhysGetPhysParams(Id: Integer; out Density, Friction, Restitution: Double);
procedure PhysSetPhysFilter(Id: Integer; Category, Mask, Group: Integer);
procedure PhysReFilter(Id: Integer);
function PhysAddMetallScrew(Id: Integer; X, Y, Angle, Style: Double): Pointer;
function PhysAddMetallGear(Id: Integer; X, Y, Angle, Style: Double): Pointer;
procedure PhysAttachShapePolygon(Id: Integer; Fric, Rest, Dens: Double;
  Count: Integer; Verts: PDouble);

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
  TShapeFloatFn = procedure(Shape: Pointer; V: Single); cdecl;
  TSetFilterFn = function(Shape, Filter: Pointer): Pointer; cdecl;
  TReFilterFn = procedure(Shape: Pointer); cdecl;
  TPolyShapeFn = function(Def: Pointer): Pointer; cdecl;

type
  TPhysObj = record
    Id: Integer;
    Body: Pointer;
    ShapeCount: Integer;
    Shapes: array[0..7] of Pointer;
    Density, Friction, Restitution: Single;
  end;

  TPhysJoint = record
    Id: Integer;
    Joint: Pointer;
  end;

const
  MAX_OBJECTS = 2048;
  kGearRadius: array[1..6] of Single = (1.6, 1.8, 2.0, 2.2, 2.4, 4.33);
  kMetalGearRadius: array[1..6] of Single = (1.6, 1.8, 2.0, 2.2, 2.4, 4.33);
  // MetallScrew 的六边形（level 1 录制：r=1.4，顶点 = 1.4·cos30° = 1.212435565）。
  kScrewVerts: array[0..11] of Single =
    (-1.4, 0.0, -0.7, -1.2124355652982142, 0.7, -1.2124355652982142,
     1.4, 0.0, 0.7, 1.2124355652982142, -0.7, 1.2124355652982142);
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
  g_shapeSetDensity: TShapeFloatFn;
  g_shapeSetFriction: TShapeFloatFn;
  g_shapeSetRestitution: TShapeFloatFn;
  g_shapeSetFilter: TSetFilterFn;
  g_reFilter: TReFilterFn;
  g_objs: array[0..MAX_OBJECTS - 1] of TPhysObj;
  g_objCount: Integer;
  g_joints: array[0..MAX_OBJECTS - 1] of TPhysJoint;
  g_jointCount: Integer;

function PhysActive: Boolean;
begin
  Result := g_active;
end;

procedure PhysResetObjects;
begin
  g_objCount := 0;
  g_jointCount := 0;
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

procedure NoteShape(Body, Shape: Pointer; Dens, Fric, Rest: Single);
var
  i: Integer;
begin
  for i := 0 to g_objCount - 1 do
    if g_objs[i].Body = Body then
    begin
      if g_objs[i].ShapeCount < 8 then
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

function PhysAddSimplePhysicObject(Id: Integer; X, Y, Angle: Double): Pointer;
begin
  if not g_active then
    Exit(nil);
  Result := NewBody(Id, X, Y, Angle, True);
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

procedure PhysSetPhysParams(Id: Integer; Density, Friction, Restitution: Double);
var
  i, idx: Integer;
begin
  if not g_active then
    Exit;
  idx := ObjIndex(Id);
  if idx < 0 then
    Exit;
  for i := 0 to g_objs[idx].ShapeCount - 1 do
    g_shapeSetDensity(g_objs[idx].Shapes[i], Density);
  g_mass(g_objs[idx].Body);
  for i := 0 to g_objs[idx].ShapeCount - 1 do
    g_shapeSetFriction(g_objs[idx].Shapes[i], Friction);
  for i := 0 to g_objs[idx].ShapeCount - 1 do
    g_shapeSetRestitution(g_objs[idx].Shapes[i], Restitution);
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
  for i := 0 to g_objs[idx].ShapeCount - 1 do
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
  for i := 0 to g_objs[idx].ShapeCount - 1 do
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
    Assigned(g_jointSetMaxTorque) and Assigned(g_getXForm) and
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
