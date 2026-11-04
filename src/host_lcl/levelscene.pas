unit LevelScene;
{$mode objfpc}{$H+}
// 关卡场景（T6.4a 第一关）：把 Introduction 的 Lua 对象还原成 GLScene 图元。
//
// 数据来源（不是回放 draw 调用）：
//   - `work/lua_probe/lvl00.jsonl`：Add_GraphSprite / Add_AlphaHint / Add_CloseButton /
//     Add_NextButton / Add_WoodGear / Set_CameraPosition / Set_BackMaterial 的实参。
//   - `work/level0_gl.bin` frame 9600 的 GLFFI02 绘制列表 + `work/level0_tex.json`
//     的纹理 id→素材映射：用于补出工厂内部生成的齿轮/钉/隐藏 dot 的尺寸与 alpha。
//   - 世界坐标 = draw bbox + 相机(-3,3)；draw 列表里的坐标已经是相机相对量。
//
// 覆盖边界：只实现 Introduction 这一关的这一帧；其余关卡/状态不在本单元。
// 原版 `Set_CameraViewArea(20,19.5)` 的投影差异不影响 draw 列表 bbox 判据；
// 像素验收另算（T6.5）。文本层在本帧不可见（3 个 tex=45 是钉，不是字）。

interface

uses Classes, SysUtils, Math, Windows, GLScene, GLObjects, GLHUDObjects, GLTexture,
  GLMaterial, GLGraphics, GLTextureFormat, GLRenderContextInfo, OpenGL1x,
  MenuScene, PakFile, SceneModel;

type
  // T6.3：可点击 HUD sprite 的设计像素矩形（Add_HudButton 等）。
  THudClick = record
    Handle: Integer;
    X, Y, W, H: Single;
  end;

  // T6.4d-3：world sprite ↔ b2 body 的同步项（Handle = Lua 工厂返回的 id）。
  TLevelSync = record
    Handle: Integer;
    Sprite: TGLSprite;
    InitAngle: Double;
  end;

  TLevelScene = class
  private
    FScene: TGLScene;
    FPak: TPakFile;
    FCamera: TGLCamera;
    FLog: string;
    FSprites: Integer;
    FObjects: TList;   // T6.4d-5：AddWorld/AddHud 新建的 sprite（Clear 时释放）
    FSync: array of TLevelSync;
    FSyncCount: Integer;
    FSyncMaxErr: Double;
    FSyncAngleMoved: Integer;
    // T6.4b-3b：Set_CameraViewArea(a,b) 的实参（F364）；由 BuildFromModel 填。
    FViewA, FViewB: Double;
    // T6.4f-visual：提示按钮（hintwood/helptime/numsatl）与数字图集材质库。
    // F469：原版把同一组 sprite 逐帧画两遍（见 BuildHintVisual），这里存两套实例。
    FHintLib: TGLMaterialLibrary;
    FHintSprites: array[0..9] of TGLBaseSceneObject;
    FHintDigits: array[0..5] of TGLHUDSprite;
    FHudClicks: array of THudClick;
    FHudClickCount: Integer;
    function AddWorld(const Asset: string; X, Y, Angle, ScaleX, ScaleY,
      Alpha: Single; Handle: Integer = 0): Boolean;
    function AddHud(const Asset: string; X, Y, W, H, Alpha: Single;
      Handle: Integer = 0): Boolean;
    function AddHiddenDots(Count: Integer): Boolean;
  public
    constructor Create(Scene: TGLScene; Pak: TPakFile; Camera: TGLCamera);
    destructor Destroy; override;
    // 释放本单元建的 sprite（Cam 不在其中），供 menu→level→menu 状态切换用。
    procedure Clear;
    function BuildIntroduction: Boolean;
    // 从 SceneModel 的图元列表建场景（T6.4a-r-2d）：世界坐标 + 相机来自模型，
    // HUD 按钮走设计空间，末尾补 mbtn/dot 引擎常量（与 BuildIntroduction 一致）。
    function BuildFromModel(const JsonlPath, PakDir: string; Time: Double): Boolean;
    // 把 world sprite 的位置同步到物理体；返回有效 body 数。
    // FSyncMaxErr = 同步前 sprite 与 body 的最大位置差；FSyncAngleMoved = 角度变化数。
    function SyncPhysics: Integer;
    // T6.4b-1：按世界距离找最近的、有物理 body 的 world sprite（磁铁 target 选择）。
    function NearestBody(X, Y: Double; out Handle: Integer;
      out Dist: Double): Boolean;
    // T6.4b-3b：只有光标落在形状内才锁定（b2_Shape_TestPoint，F385）。
    function PickBody(X, Y: Double; out Handle: Integer): Boolean;
    // T6.4b-3b：客户区设计像素 → 世界坐标（F364 的 view rect：hx=max(a,b·W/H)）。
    function ClientToWorld(X, Y, ClientW, ClientH: Integer;
      out WX, WY: Double): Boolean;
    // T6.4d-7：按句柄更新 sprite（DoProgress 的 Set_ScrObjPos）；返回是否发生位移。
    function SetSpritePos(Handle: Integer; X, Y, Angle: Double): Boolean;
    // T6.4b-2b-0：按句柄读 sprite 位置/角度（graph 对象的 Get_ScrObjPos 回退）。
    function GetSpritePos(Handle: Integer; out X, Y, Angle: Double): Boolean;
    // T6.3：设计像素命中可点击 HUD sprite（OnClick 派发用）。
    function HudHit(X, Y: Integer; out Handle: Integer): Boolean;
    // T6.4b-3a：运行时 Add_MetallGear 生成了新物理体；这里补 sprite 并记入 FSync。
    function AddRuntimeGear(Id, Style: Integer; X, Y, Angle: Double): Boolean;
    // T6.4b-4：把当前全部物理体写到 step digest（step handle x y angle）。
    procedure WriteStepDigest(Step: Integer; var F: TextFile);
    // T6.4f-visual：建 5 个提示按钮 sprite（世界木牌 + HUD 底板 + 3 数字）；
    // Cells='a,b,c' 指定 numsatl 图集格（0..9）；数字材质用 TextureOffset/Scale
    // 生成与原版同形状的 TEXTURE 矩阵（F461/F463）。
    function BuildHintVisual(const Cells: string; Time: Double): Boolean;
    procedure SetHintCells(const Cells: string; Time: Double);
    property Log: string read FLog;
    property Sprites: Integer read FSprites;
    property SyncObjects: Integer read FSyncCount;
    property SyncMaxErr: Double read FSyncMaxErr;
    property SyncAngleMoved: Integer read FSyncAngleMoved;
  end;

implementation

uses PhysWorld;

constructor TLevelScene.Create(Scene: TGLScene; Pak: TPakFile; Camera: TGLCamera);
begin
  inherited Create;
  FScene := Scene;
  FPak := Pak;
  FCamera := Camera;
  FLog := '';
  FSprites := 0;
  FObjects := TList.Create;
  FSyncCount := 0;
  FSyncMaxErr := 0;
  FSyncAngleMoved := 0;
  FViewA := 0;
  FViewB := 0;
  SetLength(FSync, 0);
end;

destructor TLevelScene.Destroy;
begin
  Clear;
  FObjects.Free;
  inherited Destroy;
end;

procedure TLevelScene.Clear;
var
  i: Integer;
begin
  if FObjects = nil then Exit;
  for i := FObjects.Count - 1 downto 0 do
    TObject(FObjects[i]).Free;
  FObjects.Clear;
  if FHintLib <> nil then
  begin
    FHintLib.Free;
    FHintLib := nil;
  end;
  for i := 0 to 9 do FHintSprites[i] := nil;
  for i := 0 to 5 do FHintDigits[i] := nil;
  SetLength(FHudClicks, 0);
  FHudClickCount := 0;
  SetLength(FSync, 0);
  FSyncCount := 0;
  FSprites := 0;
end;

function TLevelScene.AddWorld(const Asset: string; X, Y, Angle, ScaleX, ScaleY,
  Alpha: Single; Handle: Integer): Boolean;
var
  Sprite: TGLSprite;
  Err: string;
  k: Integer;
  bx, by, ba: Double;
begin
  Result := False;
  Sprite := TGLSprite.Create(FScene);
  Sprite.Position.SetPoint(X, Y, 0);
  Sprite.Width := ScaleX * 2;
  Sprite.Height := ScaleY * 2;
  Sprite.Rotation := Angle * 180 / Pi;
  Sprite.Material.FrontProperties.Diffuse.SetColor(1, 1, 1, Alpha);
  Sprite.Material.BlendingMode := bmTransparency;
  Sprite.Material.Texture.TextureMode := tmModulate;
  Err := '';
  if not LoadPakTexture(FPak, Asset, Sprite.Material.Texture, '', Err) then
  begin
    FLog := FLog + Err + 'world ' + Asset + #13#10;
    Sprite.Free;
    Exit;
  end;
  if CompareText(ExtractFileExt(Asset), '.jpg') = 0 then
    Sprite.Material.Texture.ImageAlpha := tiaOpaque;
  FScene.Objects.AddChild(Sprite);
  FObjects.Add(Sprite);
  Inc(FSprites);
  if Handle > 0 then
  begin
    k := Length(FSync);
    SetLength(FSync, k + 1);
    FSync[k].Handle := Handle;
    FSync[k].Sprite := Sprite;
    PhysGetBodyPos(Handle, bx, by, ba);
    FSync[k].InitAngle := ba;
    Inc(FSyncCount);
  end;
  FLog := FLog + 'world ' + Asset + ' ' + FormatFloat('0.###', X) + ',' +
    FormatFloat('0.###', Y) + ' a=' + FormatFloat('0.###', Alpha) + #13#10;
  Result := True;
end;

function TLevelScene.AddHud(const Asset: string; X, Y, W, H, Alpha: Single;
  Handle: Integer): Boolean;
var
  Sprite: TGLHUDSprite;
  Err: string;
begin
  Result := False;
  Sprite := TGLHUDSprite.Create(FScene);
  Sprite.Position.SetPoint(X + W * 0.5, Y + H * 0.5, 0);
  Sprite.Width := W;
  Sprite.Height := H;
  Sprite.Material.FrontProperties.Diffuse.SetColor(1, 1, 1, Alpha);
  Sprite.Material.BlendingMode := bmTransparency;
  Sprite.Material.Texture.TextureMode := tmModulate;
  Err := '';
  if not LoadPakTexture(FPak, Asset, Sprite.Material.Texture, '', Err) then
  begin
    FLog := FLog + Err + 'hud ' + Asset + #13#10;
    Sprite.Free;
    Exit;
  end;
  if CompareText(ExtractFileExt(Asset), '.jpg') = 0 then
    Sprite.Material.Texture.ImageAlpha := tiaOpaque;
  FScene.Objects.AddChild(Sprite);
  FObjects.Add(Sprite);
  Inc(FSprites);
  if Handle <> 0 then
  begin
    SetLength(FHudClicks, FHudClickCount + 1);
    FHudClicks[FHudClickCount].Handle := Handle;
    FHudClicks[FHudClickCount].X := X;
    FHudClicks[FHudClickCount].Y := Y;
    FHudClicks[FHudClickCount].W := W;
    FHudClicks[FHudClickCount].H := H;
    Inc(FHudClickCount);
  end;
  Result := True;
end;

// T6.3：按设计像素命中可点击 HUD sprite（后建的在上层，优先）。
function TLevelScene.HudHit(X, Y: Integer; out Handle: Integer): Boolean;
var
  i: Integer;
begin
  Result := False;
  Handle := 0;
  for i := FHudClickCount - 1 downto 0 do
    if (X >= FHudClicks[i].X) and (X <= FHudClicks[i].X + FHudClicks[i].W) and
       (Y >= FHudClicks[i].Y) and (Y <= FHudClicks[i].Y + FHudClicks[i].H) then
    begin
      Handle := FHudClicks[i].Handle;
      Exit(True);
    end;
end;

function TLevelScene.AddHiddenDots(Count: Integer): Boolean;
var
  i: Integer;
begin
  // 原版这一帧有 10 个 dot_1 的零尺寸、alpha=0 draw；它们来自工厂创建后
  // Do_HideCommand 的隐藏层。用 HUD 零尺寸 sprite 复现：Position=(0,0) 时
  // TGLHUDSprite 的平移落到 NDC(-1,1)，与 draw bbox 一致。
  Result := True;
  for i := 1 to Count do
    if not AddHud('dot_1.png', 0, 0, 0, 0, 0) then
      Result := False;
end;

function TLevelScene.BuildIntroduction: Boolean;
begin
  Result := False;
  // draw 顺序 = 原版 frame 9600：背景两层 → 磁铁 → 旗 → 3 齿轮 → 提示 →
  // 3 钉 → close/next → mbtn 两层 → 10 个隐藏 dot。
  if not AddHud('back_21.jpg', -0.5, -0.25, 1019, 370, 1) then Exit;
  if not AddHud('back_22.jpg', -0.5, 369.25, 1019, 370, 1) then Exit;
  if not AddWorld('magneth.png', -1.4, -7, 0, 3.4, 3.4, 1) then Exit;
  if not AddWorld('wel_flag.png', -3, 17, 0, 20, 5, 1) then Exit;
  if not AddWorld('gear_2.png', -20.35, -11.65, 0, 5, 5, 1) then Exit;
  if not AddWorld('gear_7.png', -23.97, -10.2, 0, 5, 5, 1) then Exit;
  if not AddWorld('gear_3.png', -23.8, -6.15, 0, 5, 5, 1) then Exit;
  if not AddWorld('hint_71.png', -1.95, -1.7, 0, 10, 5, 0.8255) then Exit;
  if not AddWorld('nail_2.png', -20.35, -11.65, 0, 0.8, 0.8, 1) then Exit;
  if not AddWorld('nail_2.png', -23.97, -10.2, 0, 0.8, 0.8, 1) then Exit;
  if not AddWorld('nail_2.png', -23.8, -6.15, 0, 0.8, 0.8, 1) then Exit;
  if not AddWorld('close_1.png', 2.65, 1.0, 0, 1.5, 1.5, 1) then Exit;
  if not AddWorld('next_1.png', 2.7, 0.85, 0, 1.5, 1.5, 0) then Exit;
  // mbtn 两层是 HUD 小按钮（draw bbox 0.81..1.06,0.76..1.11 ≈ 设计 921..1049,-40..89）。
  if not AddHud('mbtn_1.png', 921.5, -40.5, 127, 129, 1) then Exit;
  if not AddHud('mbtn_2.png', 921.5, -40.5, 127, 129, 0) then Exit;
  if not AddHiddenDots(10) then Exit;
  Result := True;
  FLog := FLog + 'sprites=' + IntToStr(FSprites) + #13#10;
end;

function TLevelScene.SyncPhysics: Integer;
var
  i: Integer;
  x, y, a, d: Double;
begin
  Result := 0;
  FSyncMaxErr := 0;
  FSyncAngleMoved := 0;
  for i := 0 to High(FSync) do
  begin
    if PhysBodyOf(FSync[i].Handle) = nil then Continue;
    PhysGetBodyPos(FSync[i].Handle, x, y, a);
    d := Abs(FSync[i].Sprite.Position.X - x) +
      Abs(FSync[i].Sprite.Position.Y - y);
    if d > FSyncMaxErr then FSyncMaxErr := d;
    if Abs(a - FSync[i].InitAngle) > 1e-3 then Inc(FSyncAngleMoved);
    FSync[i].Sprite.Position.SetPoint(x, y, 0);
    Inc(Result);
  end;
end;

function TLevelScene.NearestBody(X, Y: Double; out Handle: Integer;
  out Dist: Double): Boolean;
var
  i: Integer;
  bx, by, ba, d: Double;
begin
  Result := False;
  Handle := 0;
  Dist := 1e30;
  for i := 0 to High(FSync) do
  begin
    if PhysBodyOf(FSync[i].Handle) = nil then Continue;
    PhysGetBodyPos(FSync[i].Handle, bx, by, ba);
    d := Sqrt((bx - X) * (bx - X) + (by - Y) * (by - Y));
    if d < Dist then
    begin
      Dist := d;
      Handle := FSync[i].Handle;
      Result := True;
    end;
  end;
end;

function TLevelScene.PickBody(X, Y: Double; out Handle: Integer): Boolean;
var
  i: Integer;
  bx, by, ba, d, best: Double;
begin
  Result := False;
  Handle := 0;
  best := 1e30;
  for i := 0 to High(FSync) do
  begin
    if PhysBodyOf(FSync[i].Handle) = nil then Continue;
    if not PhysTestPoint(FSync[i].Handle, X, Y) then Continue;
    PhysGetBodyPos(FSync[i].Handle, bx, by, ba);
    d := Sqrt((bx - X) * (bx - X) + (by - Y) * (by - Y));
    if d < best then
    begin
      best := d;
      Handle := FSync[i].Handle;
      Result := True;
    end;
  end;
end;

// F364：view rect = 相机中心 ± 适配后的半视图（hx=max(a,b·W/H)、hy=hx/(W/H)）。
// 设计像素左上原点、y 向下；世界坐标 y 向上。
function TLevelScene.ClientToWorld(X, Y, ClientW, ClientH: Integer;
  out WX, WY: Double): Boolean;
var
  aspect, hx, hy: Double;
begin
  Result := False;
  WX := 0;
  WY := 0;
  if (ClientW <= 0) or (ClientH <= 0) or (FViewA <= 0) or (FViewB <= 0) then Exit;
  aspect := ClientW / ClientH;
  hx := FViewA;
  if FViewB * aspect > hx then hx := FViewB * aspect;
  hy := hx / aspect;
  WX := FCamera.Position.X - hx + (X / ClientW) * (2 * hx);
  WY := FCamera.Position.Y + hy - (Y / ClientH) * (2 * hy);
  Result := True;
end;

function TLevelScene.SetSpritePos(Handle: Integer; X, Y, Angle: Double): Boolean;
var
  i: Integer;
  ox, oy: Double;
begin
  Result := False;
  for i := 0 to High(FSync) do
    if FSync[i].Handle = Handle then
    begin
      ox := FSync[i].Sprite.Position.X;
      oy := FSync[i].Sprite.Position.Y;
      FSync[i].Sprite.Position.SetPoint(X, Y, 0);
      FSync[i].Sprite.Rotation := Angle * 180 / Pi;
      Result := (Abs(ox - X) + Abs(oy - Y)) > 1e-6;
      Exit;
    end;
end;

function TLevelScene.GetSpritePos(Handle: Integer; out X, Y, Angle: Double): Boolean;
var
  i: Integer;
begin
  Result := False;
  X := 0;
  Y := 0;
  Angle := 0;
  for i := 0 to High(FSync) do
    if FSync[i].Handle = Handle then
    begin
      X := FSync[i].Sprite.Position.X;
      Y := FSync[i].Sprite.Position.Y;
      Angle := FSync[i].Sprite.Rotation * Pi / 180;
      Result := True;
      Exit;
    end;
end;

procedure TLevelScene.WriteStepDigest(Step: Integer; var F: TextFile);
begin
  PhysDumpBodies(Step, F);
end;

function TLevelScene.AddRuntimeGear(Id, Style: Integer; X, Y, Angle: Double): Boolean;
var
  asset: string;
  side: Double;
begin
  asset := MetalGearAsset(Style);
  side := MetalGearSide(Style);
  if (asset = '') or (side <= 0) then
  begin
    Result := False;
    Exit;
  end;
  Result := AddWorld(asset, X, Y, Angle, side * 0.5, side * 0.5, 1, Id);
end;

function TLevelScene.BuildFromModel(const JsonlPath, PakDir: string; Time: Double): Boolean;
const
  HUD_W = 509.0;   // 设计空间半宽（F188）
  HUD_H = 369.5;   // 设计空间半高
var
  M: TSceneModel;
  i: Integer;
  O: TSceneObj;
  Top, Bot: string;
  EnvBuf: array[0..15] of Char;
  ForceEndBox: Boolean;
begin
  Result := False;
  M := TSceneModel.Create;
  try
    if not M.BuildFromJsonl(JsonlPath, PakDir) then Exit;
    ForceEndBox := GetEnvironmentVariable('HOST_FORCE_ENDBOX',
      @EnvBuf[0], 16) > 0;
    if Time <> 0.0 then
      M.ApplyTime(Time);  // 齿轮：sprite 角 = init + w·t（F372/F373）
    FCamera.Position.SetPoint(M.CamX, M.CamY, 10);
    FViewA := M.ViewA;
    FViewB := M.ViewB;
    // 背景 = 两个半屏 NDC quad（back_N1 上、back_N2 下），与 Python
    // scene_draws 的常量一致：中心 (0,±0.5)、size 2×1。
    for i := 0 to M.BackCount - 1 do
    begin
      M.BackAt(i, Top, Bot);
      if not AddHud(Top, 0, 0, 1018, 369.5, 1) then Exit;
      if not AddHud(Bot, 0, 369.5, 1018, 369.5, 1) then Exit;
    end;
    for i := 0 to M.Count - 1 do
    begin
      O := M.ObjectAt(i);
      if (O.Kind = 'Add_AlphaHudSprite') and (O.Alpha <= 0.0) then
      begin
        if not ForceEndBox then
          Continue;
        O.Alpha := 1.0;
      end;
      if O.Space = 1 then
      begin
        // SceneModel 的 HUD 坐标是**中心**（设计像素，y 向下）；AddHud 收左上角。
        if not AddHud(O.Asset, O.X + HUD_W - O.W * 0.5,
          O.Y + HUD_H - O.H * 0.5, O.W, O.H, O.Alpha, O.Handle) then Exit;
      end
      else if not AddWorld(O.Asset, O.X, O.Y, O.Angle, O.W * 0.5, O.H * 0.5,
        O.Alpha, O.Handle) then Exit;
    end;
    if not AddHud('mbtn_1.png', 921.5, -40.5, 127, 129, 1) then Exit;
    if not AddHud('mbtn_2.png', 921.5, -40.5, 127, 129, 0) then Exit;
    if not AddHiddenDots(10) then Exit;
    Result := True;
    FLog := FLog + 'model=' + JsonlPath + ' sprites=' + IntToStr(FSprites) + #13#10;
  finally
    M.Free;
  end;
end;

function ParseHintCell(const S: string; Index, Default: Integer): Integer;
var
  p, i: Integer;
  Part: string;
begin
  Result := Default;
  p := 1;
  for i := 0 to Index do
  begin
    Part := '';
    while (p <= Length(S)) and (S[p] <> ',') do
    begin
      Part := Part + S[p];
      Inc(p);
    end;
    if p <= Length(S) then Inc(p);
    if Part <> '' then Result := StrToIntDef(Trim(Part), Default);
  end;
end;

function TLevelScene.BuildHintVisual(const Cells: string; Time: Double): Boolean;
const
  // 原版 draw 列表（work/gl_hint_l4show，F457/F461）：世界木牌 bbox (-3,2.5)-(7,7.5)；
  // HUD 底板 NDC (0.52,-0.83)-(1.03,-0.48)；数字 NDC x 0.710/0.749/0.788，宽 0.050，
  // y -0.719..-0.632（设计空间 1018x739）。数字 3 的右边界实测 0.839（宽 0.051）。
  DIGIT_L: array[0..2] of Double = (870.39, 890.24, 910.09);
  DIGIT_W: array[0..2] of Double = (25.45, 25.45, 25.96);
var
  Err: string;
  k, Pass: Integer;
  LM: TGLLibMaterial;
  W: TGLSprite;
  H: TGLHUDSprite;
begin
  Result := False;
  if FHintLib <> nil then
  begin
    SetHintCells(Cells, Time);
    Exit(True);
  end;
  FHintLib := TGLMaterialLibrary.Create(nil);
  for k := 0 to 9 do
  begin
    LM := FHintLib.Materials.Add;
    LM.Name := 'hint_digit_' + IntToStr(k);
    Err := '';
    if not LoadPakTexture(FPak, 'numsatl.png', LM.Material.Texture, '', Err) then
    begin
      FLog := FLog + Err;
      Exit;
    end;
    LM.Material.Texture.TextureMode := tmModulate;
    LM.Material.FrontProperties.Diffuse.SetColor(1, 1, 1, 1);
    LM.Material.BlendingMode := bmTransparency;
    LM.TextureScale.SetPoint(0.1, 1, 1);
    LM.TextureOffset.SetPoint(k * 0.1, 0, 0);
  end;
  // 木牌/底板的纹理也进库，两套 sprite 共享同一份纹理（只上传一次）。
  LM := FHintLib.Materials.Add;
  LM.Name := 'hint_wood';
  Err := '';
  if not LoadPakTexture(FPak, 'hintwood.png', LM.Material.Texture, '', Err) then
  begin
    FLog := FLog + Err;
    Exit;
  end;
  LM.Material.Texture.TextureMode := tmModulate;
  LM.Material.FrontProperties.Diffuse.SetColor(1, 1, 1, 1);
  LM.Material.BlendingMode := bmTransparency;
  LM := FHintLib.Materials.Add;
  LM.Name := 'hint_btn';
  Err := '';
  if not LoadPakTexture(FPak, 'helptime.png', LM.Material.Texture, '', Err) then
  begin
    FLog := FLog + Err;
    Exit;
  end;
  LM.Material.Texture.TextureMode := tmModulate;
  LM.Material.FrontProperties.Diffuse.SetColor(1, 1, 1, 1);
  LM.Material.BlendingMode := bmTransparency;
  // F469：原版一帧内把可见的这组 sprite 画两遍（两遍 tex/bbox/tm/rgba/caps/blend
  // 逐字段相同）；宿主用两个独立实例复现同样的 10 条 draw。
  for Pass := 0 to 1 do
  begin
    // 世界木牌；原版 draw bbox 是相机相对量，相机 (-2,-5) ⇒ 场景中心 = (0,0)。
    W := TGLSprite.Create(FScene);
    W.Position.SetPoint(0, 0, 0);
    W.Width := 10;
    W.Height := 5;
    W.Material.MaterialLibrary := FHintLib;
    W.Material.LibMaterialName := 'hint_wood';
    FScene.Objects.AddChild(W);
    FObjects.Add(W);
    Inc(FSprites);
    FHintSprites[Pass * 5] := W;
    // HUD 底板
    H := TGLHUDSprite.Create(FScene);
    H.Position.SetPoint(773.68 + 259.59 * 0.5, 546.86 + 129.33 * 0.5, 0);
    H.Width := 259.59;
    H.Height := 129.33;
    H.Material.MaterialLibrary := FHintLib;
    H.Material.LibMaterialName := 'hint_btn';
    FScene.Objects.AddChild(H);
    FObjects.Add(H);
    Inc(FSprites);
    FHintSprites[Pass * 5 + 1] := H;
    // 三个数字 sprite（材质库选格）
    for k := 0 to 2 do
    begin
      H := TGLHUDSprite.Create(FScene);
      H.Position.SetPoint(DIGIT_L[k] + DIGIT_W[k] * 0.5, 603.02 + 32.16 * 0.5, 0);
      H.Width := DIGIT_W[k];
      H.Height := 32.16;
      H.Material.MaterialLibrary := FHintLib;
      H.Material.LibMaterialName := 'hint_digit_0';
      FScene.Objects.AddChild(H);
      FObjects.Add(H);
      Inc(FSprites);
      FHintDigits[Pass * 3 + k] := H;
      FHintSprites[Pass * 5 + 2 + k] := H;
    end;
  end;
  SetHintCells(Cells, Time);
  Result := True;
end;

procedure TLevelScene.SetHintCells(const Cells: string; Time: Double);
var
  a, b, c, n, Pass: Integer;
  S: string;
begin
  if FHintLib = nil then Exit;
  // F468：三位数字是同一个 180 秒倒计时 N = 180 - floor(t+0.38) 的百/十/个位；
  // 'auto'、空串或 '?' 从关卡时间算，显式数字保持原样（t>=180 未观测，钳到 0）。
  n := 180 - Trunc(Time + 0.38);
  if n < 0 then n := 0;
  S := Trim(Cells);
  if (S = '') or SameText(S, 'auto') then
  begin
    a := n div 100 mod 10;
    b := n div 10 mod 10;
    c := n mod 10;
  end
  else
  begin
    a := ParseHintCell(S, 0, -1);
    b := ParseHintCell(S, 1, -1);
    c := ParseHintCell(S, 2, -1);
    if a < 0 then a := n div 100 mod 10;
    if b < 0 then b := n div 10 mod 10;
    if c < 0 then c := n mod 10;
  end;
  for Pass := 0 to 1 do
  begin
    FHintDigits[Pass * 3 + 0].Material.LibMaterialName := 'hint_digit_' + IntToStr(a);
    FHintDigits[Pass * 3 + 1].Material.LibMaterialName := 'hint_digit_' + IntToStr(b);
    FHintDigits[Pass * 3 + 2].Material.LibMaterialName := 'hint_digit_' + IntToStr(c);
  end;
end;

end.
