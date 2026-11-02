unit SceneModel;
{$mode objfpc}{$H+}
// 场景模型（T6.4a-r-2d 的 Pascal 移植）：把绑定 JSONL 还原成图元列表。
//
// 语义与 tools/scene_from_lua.py 的 build() 一一对应（F364/F366/F367）：
//   - 世界坐标 = 参数 − 相机；不按父图做层偏移（F364）
//   - Set_ScrObjPos 按句柄回放（OnResizeForm/动画的最终位置）
//   - 摆臂：4×2、sprite 角 = body−π/2、锚点 = 紧随的 Add_JointNail（半径 1.6）
//   - HUD 按钮用设计空间；Do_HideCommand 只改 HUD 的 alpha
// 边界：只产出静态场景数据；齿轮/摆臂的动画相位由调用方（宿主时钟/物理）决定。
interface

uses
  SysUtils, Classes, Math;

const
  MAX_ARGS = 16;
  ARM_RADIUS = 1.6;
  HUD_HALF_W = 509.0;
  HUD_HALF_H = 369.5;

type
  TArgKind = (akNone, akNum, akStr, akBool);
  TArg = record
    Kind: TArgKind;
    Num: Double;
    Str: string;
    Bool: Boolean;
  end;
  TArgs = array[0..MAX_ARGS - 1] of TArg;

  TSceneObj = record
    Kind, Asset: string;
    X, Y, Angle, W, H, Alpha: Double;
    Space: Integer;  // 0=world, 1=ndc
    Root: Integer;
    Handle: Integer;
    HasPivot: Boolean;
    PivotX, PivotY: Double;
    InitAngle: Double;
    Speed: Double;
    HasSpeed: Boolean;
  end;

  TSceneModel = class
  private
    FObjects: array of TSceneObj;
    FBacks: array of record Top, Bottom: string; end;
    FCamX, FCamY: Double;
    function AddObject(const O: TSceneObj): Integer;
    function FindHandle(H: Integer): Integer;
  public
    procedure Clear;
    function BuildFromJsonl(const FileName, PakDir: string): Boolean;
    function SaveJsonl(const FileName: string): Boolean;
    function Count: Integer;
    function ObjectAt(Index: Integer): TSceneObj;
    // 齿轮链动画：angle = InitAngle + w*t（w 由 Set_JointMotors/Add_JointSimpleGear 推出）。
    procedure ApplyTime(t: Double);
    function BackCount: Integer;
    procedure BackAt(Index: Integer; out Top, Bottom: string);
    property CamX: Double read FCamX;
    property CamY: Double read FCamY;
  end;

function ParseCallLine(const Line: string; out Name: string;
  var Args: TArgs; out ArgCount, Ret: Integer): Boolean;

implementation

type
  THud = record
    Handle: Integer;
    W, H: Double;
    Tex: string;
    X, Y, Alpha: Double;
  end;
  TBody = record
    Handle: Integer;
    X, Y, Angle: Double;
  end;

const
  // 齿轮/螺丝/钉/方块/按钮/门：边长由零售 draw 的对边量出（F362/F363/F367）。
  WOOD_GEAR_ASSET: array[1..5] of string =
    ('gear_1.png', 'gear_2.png', 'gear_3.png', '', 'gear_7.png');
  WOOD_GEAR_SIDE: array[1..5] of Double =
    (3.6896, 7.3141, 7.3668, 0, 7.5408);
  METAL_GEAR_ASSET: array[1..3] of string =
    ('gear_10.png', 'gear_11.png', 'gear_12.png');
  METAL_GEAR_SIDE: array[1..3] of Double = (3.6896, 7.3141, 7.3668);
  WOOD_BOX_ASSET: array[1..3] of string =
    ('wbox_1.png', 'wbox_2.png', 'wbox_3.png');
  WOOD_BOX_SIDE = 4.702;
  NAIL_SIZE = 1.6;

function NumArg(const Args: TArgs; Idx: Integer): Double;
begin
  if (Idx >= 0) and (Idx < MAX_ARGS) and (Args[Idx].Kind = akNum) then
    Result := Args[Idx].Num
  else
    Result := 0.0;
end;

function StrArg(const Args: TArgs; Idx: Integer): string;
begin
  if (Idx >= 0) and (Idx < MAX_ARGS) and (Args[Idx].Kind = akStr) then
    Result := Args[Idx].Str
  else
    Result := '';
end;

function IntArg(const Args: TArgs; Idx: Integer): Integer;
begin
  Result := Trunc(NumArg(Args, Idx));
end;

{ ---------- JSONL 解析（只覆盖探针/宿主日志的形态） ---------- }

function ReadJsonString(const S: string; var P: Integer): string;
var
  c: Char;
begin
  Result := '';
  if (P > Length(S)) or (S[P] <> '"') then Exit;
  Inc(P);
  while P <= Length(S) do
  begin
    c := S[P];
    if c = '"' then
    begin
      Inc(P);
      Exit;
    end;
    if c = '\' then
    begin
      Inc(P);
      if P > Length(S) then Exit;
      case S[P] of
        'n': Result := Result + #10;
        'r': Result := Result + #13;
        't': Result := Result + #9;
        else Result := Result + S[P];
      end;
      Inc(P);
    end
    else
    begin
      Result := Result + c;
      Inc(P);
    end;
  end;
end;

function ParseCallLine(const Line: string; out Name: string;
  var Args: TArgs; out ArgCount, Ret: Integer): Boolean;
var
  P, Q: Integer;
  s: string;
  c: Char;
begin
  Result := False;
  Name := '';
  ArgCount := 0;
  Ret := 0;
  P := Pos('"call":"', Line);
  if P = 0 then Exit;
  Inc(P, Length('"call":"'));
  Q := P;
  while (Q <= Length(Line)) and (Line[Q] <> '"') do Inc(Q);
  Name := Copy(Line, P, Q - P);

  P := Pos('"args":[', Line);
  if P = 0 then Exit;
  Inc(P, Length('"args":['));
  while (P <= Length(Line)) and (ArgCount < MAX_ARGS) do
  begin
    while (P <= Length(Line)) and ((Line[P] = ' ') or (Line[P] = ',') or
      (Line[P] = #9)) do Inc(P);
    if (P > Length(Line)) or (Line[P] = ']') then
    begin
      if (P <= Length(Line)) and (Line[P] = ']') then Inc(P);
      Break;
    end;
    FillChar(Args[ArgCount], SizeOf(Args[ArgCount]), 0);
    c := Line[P];
    if c = '"' then
    begin
      Args[ArgCount].Kind := akStr;
      Args[ArgCount].Str := ReadJsonString(Line, P);
    end
    else if c = 't' then
    begin
      Args[ArgCount].Kind := akBool;
      Args[ArgCount].Bool := True;
      Inc(P, 4);
    end
    else if c = 'f' then
    begin
      Args[ArgCount].Kind := akBool;
      Args[ArgCount].Bool := False;
      Inc(P, 5);
    end
    else if c = 'n' then
    begin
      Args[ArgCount].Kind := akNone;
      Inc(P, 4);
    end
    else
    begin
      Q := P;
      while (Q <= Length(Line)) and (Line[Q] <> ',') and (Line[Q] <> ']') do
        Inc(Q);
      s := Trim(Copy(Line, P, Q - P));
      Args[ArgCount].Kind := akNum;
      Args[ArgCount].Num := StrToFloat(s);
      P := Q;
    end;
    Inc(ArgCount);
  end;

  P := Pos('"ret":', Line);
  if P > 0 then
  begin
    Inc(P, Length('"ret":'));
    Q := P;
    while (Q <= Length(Line)) and (Line[Q] >= '0') and (Line[Q] <= '9') do
      Inc(Q);
    s := Copy(Line, P, Q - P);
    if s <> '' then Ret := StrToInt(s);
  end;
  Result := True;
end;

{ ---------- TSceneModel ---------- }
function TSceneModel.BackCount: Integer;
begin
  Result := Length(FBacks);
end;

procedure TSceneModel.BackAt(Index: Integer; out Top, Bottom: string);
begin
  Top := '';
  Bottom := '';
  if (Index >= 0) and (Index < Length(FBacks)) then
  begin
    Top := FBacks[Index].Top;
    Bottom := FBacks[Index].Bottom;
  end;
end;

procedure InitObj(out O: TSceneObj);
begin
  O.Kind := '';
  O.Asset := '';
  O.X := 0.0;
  O.Y := 0.0;
  O.Angle := 0.0;
  O.W := 0.0;
  O.H := 0.0;
  O.Alpha := 1.0;
  O.Space := 0;
  O.Root := 0;
  O.Handle := 0;
  O.HasPivot := False;
  O.PivotX := 0.0;
  O.PivotY := 0.0;
  O.InitAngle := 0.0;
  O.Speed := 0.0;
  O.HasSpeed := False;
end;

procedure TSceneModel.Clear;
begin
  SetLength(FObjects, 0);
  SetLength(FBacks, 0);
  FCamX := 0.0;
  FCamY := 0.0;
end;

function TSceneModel.Count: Integer;
begin
  Result := Length(FObjects);
end;

function TSceneModel.ObjectAt(Index: Integer): TSceneObj;
begin
  if (Index >= 0) and (Index < Length(FObjects)) then
    Result := FObjects[Index]
  else
    InitObj(Result);
end;

procedure TSceneModel.ApplyTime(t: Double);
var
  i: Integer;
begin
  for i := 0 to High(FObjects) do
    if FObjects[i].HasSpeed and
      ((FObjects[i].Kind = 'Add_WoodGear') or
       (FObjects[i].Kind = 'Add_MetallGear')) then
      FObjects[i].Angle := FObjects[i].InitAngle + FObjects[i].Speed * t;
end;

function TSceneModel.AddObject(const O: TSceneObj): Integer;
begin
  Result := Length(FObjects);
  SetLength(FObjects, Result + 1);
  FObjects[Result] := O;
  FObjects[Result].Handle := 0;
end;

function TSceneModel.FindHandle(H: Integer): Integer;
var
  i: Integer;
begin
  Result := -1;
  if H <= 0 then Exit;
  for i := 0 to High(FObjects) do
    if FObjects[i].Handle = H then
      Exit(i);
end;



function TSceneModel.BuildFromJsonl(const FileName, PakDir: string): Boolean;
var
  F: TextFile;
  Line, Name, Alias, Asset: string;
  Args: TArgs;
  ArgCount, Ret, i, j, k, m, n: Integer;
  O: TSceneObj;
  Materials: TStringList;
  Huds: array of THud;
  Bodies: array of TBody;
  PendingArm: Integer;
  Style: Integer;
  Joints: array of record Handle, BodyA, BodyB: Integer; end;
  Links: array of record B1, B2: Integer; Factor: Double; end;
  Motors: array of record Joint: Integer; Speed: Double; end;
  Side: Double;
  X, Y, Ang: Double;

  function AssetOf(const N: string): string;
  begin
    if N = 'magnet_hero_1' then begin Result := 'magneth.png'; Exit; end;
    if N = 'button_platform_1' then begin Result := 'bplatf_1.png'; Exit; end;
    Result := Materials.Values[N];
    if Result <> '' then Exit;
    if (PakDir <> '') and FileExists(IncludeTrailingPathDelimiter(PakDir) +
      N + '.png') then Exit(N + '.png');
    if (PakDir <> '') and FileExists(IncludeTrailingPathDelimiter(PakDir) +
      N + '.jpg') then Exit(N + '.jpg');
    Result := N;
  end;

  procedure AddHandle(H: Integer; ObjIdx: Integer);
  begin
    if (H > 1000) and (ObjIdx >= 0) then
      FObjects[ObjIdx].Handle := H;
  end;

  function FindBody(H: Integer): Integer;
  var
    k: Integer;
  begin
    Result := -1;
    for k := 0 to High(Bodies) do
      if Bodies[k].Handle = H then
        Exit(k);
  end;

  function FindHud(H: Integer): Integer;
  var
    k: Integer;
  begin
    Result := -1;
    for k := 0 to High(Huds) do
      if Huds[k].Handle = H then
        Exit(k);
  end;

begin
  Result := False;
  Clear;
  Materials := TStringList.Create;
  try
    Materials.NameValueSeparator := '=';
    Materials.CaseSensitive := True;
    SetLength(Huds, 0);
    SetLength(Bodies, 0);
    SetLength(Joints, 0);
    SetLength(Links, 0);
    SetLength(Motors, 0);
    PendingArm := -1;

    AssignFile(F, FileName);
    {$I-}
    Reset(F);
    {$I+}
    if IOResult <> 0 then Exit;
    while not Eof(F) do
    begin
      ReadLn(F, Line);
      if not ParseCallLine(Line, Name, Args, ArgCount, Ret) then Continue;

      if Name = 'Set_CameraPosition' then
      begin
        FCamX := NumArg(Args, 0);
        FCamY := NumArg(Args, 1);
      end
      else if Name = 'Add_LevelMaterial' then
      begin
        Alias := StrArg(Args, 1);
        Asset := StrArg(Args, 0);
        if (Alias <> '') and (Asset <> '') then
          Materials.Values[Alias] := Asset;
      end
      else if Name = 'Set_BackMaterial' then
      begin
        i := Length(FBacks);
        SetLength(FBacks, i + 1);
        FBacks[i].Top := StrArg(Args, 0) + '1.jpg';
        FBacks[i].Bottom := StrArg(Args, 0) + '2.jpg';
      end
      else if Name = 'Add_GraphSprite' then
      begin
        InitObj(O);
        O.Kind := Name;
        O.Asset := AssetOf(StrArg(Args, 6));
        O.X := NumArg(Args, 1);
        O.Y := NumArg(Args, 2);
        O.Angle := NumArg(Args, 3);
        O.W := 2.0 * NumArg(Args, 4);
        O.H := 2.0 * NumArg(Args, 5);
        O.Alpha := 1.0;
        O.Root := IntArg(Args, 0);
        AddHandle(Ret, AddObject(O));
      end
      else if Name = 'Add_AlphaHint' then
      begin
        InitObj(O);
        O.Kind := Name;
        O.Asset := AssetOf(StrArg(Args, 6));
        O.X := NumArg(Args, 1);
        O.Y := NumArg(Args, 2);
        O.Angle := NumArg(Args, 3);
        O.W := 2.0 * NumArg(Args, 4);
        O.H := 2.0 * NumArg(Args, 5);
        O.Alpha := 1.0;
        O.Root := IntArg(Args, 0);
        AddHandle(Ret, AddObject(O));
      end
      else if (Name = 'Add_CloseButton') or (Name = 'Add_NextButton') then
      begin
        InitObj(O);
        O.Kind := Name;
        if Name = 'Add_CloseButton' then O.Asset := 'close_1.png'
        else O.Asset := 'next_1.png';
        O.X := NumArg(Args, 1);
        O.Y := NumArg(Args, 2);
        O.W := 3.0;
        O.H := 3.0;
        O.Alpha := 1.0;
        O.Root := IntArg(Args, 0);
        AddHandle(Ret, AddObject(O));
      end
      else if Name = 'Add_SimplePhysicObject' then
      begin
        i := Length(Bodies);
        SetLength(Bodies, i + 1);
        Bodies[i].Handle := Ret;
        Bodies[i].X := NumArg(Args, 0);
        Bodies[i].Y := NumArg(Args, 1);
        Bodies[i].Angle := NumArg(Args, 2);
      end
      else if Name = 'Attach_SimpleGraphObject' then
      begin
        i := FindBody(IntArg(Args, 0));
        if i >= 0 then
        begin
          InitObj(O);
          O.Kind := Name;
          O.Asset := AssetOf(StrArg(Args, 4));
          O.X := Bodies[i].X;
          O.Y := Bodies[i].Y;
          O.Angle := Bodies[i].Angle;
          O.W := 2.0 * NumArg(Args, 2);
          O.H := 2.0 * NumArg(Args, 3);
          O.Alpha := 1.0;
          O.Root := IntArg(Args, 1);
          AddHandle(Ret, AddObject(O));
        end;
      end
      else if (Name = 'Add_MetallScrew') or (Name = 'Add_MetallGear') then
      begin
        Style := IntArg(Args, 4);
        if (Name = 'Add_MetallGear') and (Style >= 1) and (Style <= 3) then
        begin
          InitObj(O);
          O.Kind := Name;
          O.Asset := METAL_GEAR_ASSET[Style];
          O.X := NumArg(Args, 1);
          O.Y := NumArg(Args, 2);
          O.Angle := NumArg(Args, 3) + Pi;
          O.W := METAL_GEAR_SIDE[Style];
          O.H := METAL_GEAR_SIDE[Style];
          O.Alpha := 1.0;
          O.Root := IntArg(Args, 0);
          AddHandle(Ret, AddObject(O));
        end
        else if (Name = 'Add_MetallScrew') and (Style = 1) then
        begin
          InitObj(O);
          O.Kind := Name;
          O.Asset := 'screw_1.png';
          O.X := NumArg(Args, 1);
          O.Y := NumArg(Args, 2);
          O.Angle := NumArg(Args, 3);
          O.W := 3.248;
          O.H := 3.248;
          O.Alpha := 1.0;
          O.Root := IntArg(Args, 0);
          AddHandle(Ret, AddObject(O));
        end;
      end
      else if Name = 'Add_WoodGear' then
      begin
        Style := IntArg(Args, 4);
        if (Style >= 1) and (Style <= 5) and (WOOD_GEAR_ASSET[Style] <> '') then
        begin
          InitObj(O);
          O.Kind := Name;
          O.Asset := WOOD_GEAR_ASSET[Style];
          O.X := NumArg(Args, 1);
          O.Y := NumArg(Args, 2);
          O.Angle := NumArg(Args, 3) + Pi;
          O.W := WOOD_GEAR_SIDE[Style];
          O.H := WOOD_GEAR_SIDE[Style];
          O.Alpha := 1.0;
          O.Root := IntArg(Args, 0);
          AddHandle(Ret, AddObject(O));
        end;
      end
      else if Name = 'Add_JointNail' then
      begin
        InitObj(O);
        O.Kind := Name;
        O.Asset := 'nail_2.png';
        O.X := NumArg(Args, 3);
        O.Y := NumArg(Args, 4);
        O.W := NAIL_SIZE;
        O.H := NAIL_SIZE;
        O.Alpha := 1.0;
        AddHandle(Ret, AddObject(O));
        i := Length(Joints);
        SetLength(Joints, i + 1);
        Joints[i].Handle := Ret;
        Joints[i].BodyA := IntArg(Args, 1);
        Joints[i].BodyB := IntArg(Args, 2);
        if PendingArm >= 0 then
        begin
          FObjects[PendingArm].HasPivot := True;
          FObjects[PendingArm].PivotX := O.X;
          FObjects[PendingArm].PivotY := O.Y;
          PendingArm := -1;
        end;
      end
      else if Name = 'Add_SwitchArm' then
      begin
        Style := IntArg(Args, 4);
        if (Style = 1) or (Style = 2) then
        begin
          InitObj(O);
          O.Kind := Name;
          if Style = 1 then O.Asset := 'sw_arm1.png'
          else O.Asset := 'sw_arm2.png';
          O.X := NumArg(Args, 1);
          O.Y := NumArg(Args, 2);
          O.Angle := NumArg(Args, 3) - Pi * 0.5;
          O.InitAngle := NumArg(Args, 3);
          O.W := 4.0;
          O.H := 2.0;
          O.Alpha := 1.0;
          O.Root := IntArg(Args, 0);
          i := AddObject(O);
          AddHandle(Ret, i);
          PendingArm := i;
        end;
      end
      else if Name = 'Add_WoodBox' then
      begin
        Style := IntArg(Args, 4);
        if (Style >= 1) and (Style <= 3) then
        begin
          InitObj(O);
          O.Kind := Name;
          O.Asset := WOOD_BOX_ASSET[Style];
          O.X := NumArg(Args, 1);
          O.Y := NumArg(Args, 2);
          O.Angle := NumArg(Args, 3);
          O.W := WOOD_BOX_SIDE;
          O.H := WOOD_BOX_SIDE;
          O.Alpha := 1.0;
          O.Root := IntArg(Args, 0);
          AddHandle(Ret, AddObject(O));
        end;
      end
      else if Name = 'Add_PushButton' then
      begin
        Style := IntArg(Args, 4);
        if Style = 1 then
        begin
          InitObj(O);
          O.Kind := Name;
          O.Asset := 'pbut_1.png';
          O.X := NumArg(Args, 1);
          O.Y := NumArg(Args, 2);
          O.Angle := NumArg(Args, 3);
          O.W := 3.0;
          O.H := 1.5;
          O.Alpha := 1.0;
          O.Root := IntArg(Args, 0);
          AddHandle(Ret, AddObject(O));
        end;
      end
      else if Name = 'Add_BarDoor' then
      begin
        Style := IntArg(Args, 4);
        if Style = 1 then
        begin
          InitObj(O);
          O.Kind := Name;
          O.Asset := 'bar_1.png';
          O.X := NumArg(Args, 1);
          O.Y := NumArg(Args, 2);
          O.Angle := NumArg(Args, 3);
          O.W := 7.0;
          O.H := 3.5;
          O.Alpha := 1.0;
          O.Root := IntArg(Args, 0);
          AddHandle(Ret, AddObject(O));
        end;
      end
      else if Name = 'Add_JointSimpleGear' then
      begin
        if NumArg(Args, 4) <> 0.0 then
        begin
          i := Length(Links);
          SetLength(Links, i + 1);
          Links[i].B1 := IntArg(Args, 0);
          Links[i].B2 := IntArg(Args, 1);
          Links[i].Factor := -1.0 / NumArg(Args, 4);
        end;
      end
      else if Name = 'Set_JointMotors' then
      begin
        i := Length(Motors);
        SetLength(Motors, i + 1);
        Motors[i].Joint := IntArg(Args, 0);
        Motors[i].Speed := NumArg(Args, 2);
      end
      else if Name = 'Add_HudButton' then
      begin
        i := Length(Huds);
        SetLength(Huds, i + 1);
        Huds[i].Handle := Ret;
        Huds[i].W := NumArg(Args, 4);
        Huds[i].H := NumArg(Args, 5);
        Huds[i].Tex := StrArg(Args, 6);
        Huds[i].X := 0.0;
        Huds[i].Y := 0.0;
        Huds[i].Alpha := 1.0;
      end
      else if Name = 'Set_ScrObjPos' then
      begin
        j := FindHud(IntArg(Args, 0));
        if j >= 0 then
        begin
          Huds[j].X := NumArg(Args, 1);
          Huds[j].Y := NumArg(Args, 2);
        end
        else
        begin
          j := FindHandle(IntArg(Args, 0));
          if j >= 0 then
          begin
            FObjects[j].X := NumArg(Args, 1);
            FObjects[j].Y := NumArg(Args, 2);
            if ArgCount >= 4 then
              FObjects[j].Angle := NumArg(Args, 3);
          end;
        end;
      end
      else if Name = 'Do_HideCommand' then
      begin
        j := FindHud(IntArg(Args, 0));
        if j >= 0 then
          Huds[j].Alpha := 0.0;
      end;
    end;
    CloseFile(F);

    // 齿轮：保留 init 角，供 ApplyTime 叠加 w*t；速度由电机 + 传动比推出。
    for i := 0 to High(FObjects) do
      if (FObjects[i].Kind = 'Add_WoodGear') or
        (FObjects[i].Kind = 'Add_MetallGear') then
        FObjects[i].InitAngle := FObjects[i].Angle;
    for i := 0 to High(Motors) do
      for j := 0 to High(Joints) do
        if Joints[j].Handle = Motors[i].Joint then
        begin
          k := FindHandle(Joints[j].BodyA);
          if (k >= 0) and ((FObjects[k].Kind = 'Add_WoodGear') or
            (FObjects[k].Kind = 'Add_MetallGear')) then
          begin
            FObjects[k].Speed := Motors[i].Speed;
            FObjects[k].HasSpeed := True;
          end;
          k := FindHandle(Joints[j].BodyB);
          if (k >= 0) and ((FObjects[k].Kind = 'Add_WoodGear') or
            (FObjects[k].Kind = 'Add_MetallGear')) then
          begin
            FObjects[k].Speed := Motors[i].Speed;
            FObjects[k].HasSpeed := True;
          end;
        end;
    for k := 1 to High(Links) + 1 do
      for i := 0 to High(Links) do
      begin
        n := FindHandle(Links[i].B1);
        m := FindHandle(Links[i].B2);
        if (n >= 0) and (m >= 0) and FObjects[n].HasSpeed and
          (not FObjects[m].HasSpeed) then
        begin
          FObjects[m].Speed := FObjects[n].Speed * Links[i].Factor;
          FObjects[m].HasSpeed := True;
        end;
      end;

    // 摆臂静止位姿（F374）：body = init + 0.5（关节限位），位置由锚点 + 1.6。
    for i := 0 to High(FObjects) do
      if (FObjects[i].Kind = 'Add_SwitchArm') and FObjects[i].HasPivot then
      begin
        Ang := FObjects[i].InitAngle + 0.5;
        FObjects[i].X := FObjects[i].PivotX - ARM_RADIUS * Sin(Ang);
        FObjects[i].Y := FObjects[i].PivotY + ARM_RADIUS * Cos(Ang);
        FObjects[i].Angle := Ang - Pi * 0.5;
      end;

    // HUD 按钮在全部调用之后按插入序追加（与 scene_from_lua.build 一致）。
    for i := 0 to High(Huds) do
    begin
      Asset := '';
      if Huds[i].Tex = 'btn_restart_2' then Asset := 'restart2.png'
      else if Huds[i].Tex = 'btn_next_4' then Asset := 'next_4.png';
      if Asset <> '' then
      begin
        InitObj(O);
        O.Kind := 'Add_HudButton';
        O.Asset := Asset;
        O.X := Huds[i].X;
        O.Y := Huds[i].Y;
        O.W := 2.0 * Huds[i].W;
        O.H := 2.0 * Huds[i].H;
        O.Alpha := Huds[i].Alpha;
        O.Space := 1;
        AddObject(O);
      end;
    end;
    Result := True;
  finally
    Materials.Free;
  end;
end;

function TSceneModel.SaveJsonl(const FileName: string): Boolean;
var
  F: TextFile;
  i: Integer;
  Sp: string;
begin
  Result := False;
  AssignFile(F, FileName);
  {$I-}
  Rewrite(F);
  {$I+}
  if IOResult <> 0 then Exit;
  WriteLn(F, '{"kind":"_camera","x":' + FloatToStrF(FCamX, ffGeneral, 9, 0) +
    ',"y":' + FloatToStrF(FCamY, ffGeneral, 9, 0) + '}');
  for i := 0 to High(FObjects) do
  begin
    if FObjects[i].Space = 1 then Sp := 'ndc' else Sp := 'world';
    WriteLn(F, '{"kind":"' + FObjects[i].Kind + '","asset":"' +
      FObjects[i].Asset + '","x":' + FloatToStrF(FObjects[i].X, ffGeneral, 9, 0) +
      ',"y":' + FloatToStrF(FObjects[i].Y, ffGeneral, 9, 0) +
      ',"angle":' + FloatToStrF(FObjects[i].Angle, ffGeneral, 9, 0) +
      ',"w":' + FloatToStrF(FObjects[i].W, ffGeneral, 9, 0) +
      ',"h":' + FloatToStrF(FObjects[i].H, ffGeneral, 9, 0) +
      ',"alpha":' + FloatToStrF(FObjects[i].Alpha, ffGeneral, 9, 0) +
      ',"space":"' + Sp + '","root":' + IntToStr(FObjects[i].Root) + '}');
  end;
  CloseFile(F);
  Result := True;
end;

end.
