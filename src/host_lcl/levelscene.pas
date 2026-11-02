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

uses Classes, SysUtils, Math, GLScene, GLObjects, GLHUDObjects, GLTexture,
  GLMaterial, GLGraphics, GLTextureFormat, GLRenderContextInfo, OpenGL1x,
  MenuScene, PakFile, SceneModel;

type
  TLevelScene = class
  private
    FScene: TGLScene;
    FPak: TPakFile;
    FCamera: TGLCamera;
    FLog: string;
    FSprites: Integer;
    function AddWorld(const Asset: string; X, Y, Angle, ScaleX, ScaleY,
      Alpha: Single): Boolean;
    function AddHud(const Asset: string; X, Y, W, H, Alpha: Single): Boolean;
    function AddHiddenDots(Count: Integer): Boolean;
  public
    constructor Create(Scene: TGLScene; Pak: TPakFile; Camera: TGLCamera);
    function BuildIntroduction: Boolean;
    // 从 SceneModel 的图元列表建场景（T6.4a-r-2d）：世界坐标 + 相机来自模型，
    // HUD 按钮走设计空间，末尾补 mbtn/dot 引擎常量（与 BuildIntroduction 一致）。
    function BuildFromModel(const JsonlPath, PakDir: string; Time: Double): Boolean;
    property Log: string read FLog;
    property Sprites: Integer read FSprites;
  end;

implementation

constructor TLevelScene.Create(Scene: TGLScene; Pak: TPakFile; Camera: TGLCamera);
begin
  inherited Create;
  FScene := Scene;
  FPak := Pak;
  FCamera := Camera;
  FLog := '';
  FSprites := 0;
end;

function TLevelScene.AddWorld(const Asset: string; X, Y, Angle, ScaleX, ScaleY,
  Alpha: Single): Boolean;
var
  Sprite: TGLSprite;
  Err: string;
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
  Inc(FSprites);
  FLog := FLog + 'world ' + Asset + ' ' + FormatFloat('0.###', X) + ',' +
    FormatFloat('0.###', Y) + ' a=' + FormatFloat('0.###', Alpha) + #13#10;
  Result := True;
end;

function TLevelScene.AddHud(const Asset: string; X, Y, W, H, Alpha: Single): Boolean;
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
  Inc(FSprites);
  Result := True;
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

function TLevelScene.BuildFromModel(const JsonlPath, PakDir: string; Time: Double): Boolean;
const
  HUD_W = 509.0;   // 设计空间半宽（F188）
  HUD_H = 369.5;   // 设计空间半高
var
  M: TSceneModel;
  i: Integer;
  O: TSceneObj;
  Top, Bot: string;
begin
  Result := False;
  M := TSceneModel.Create;
  try
    if not M.BuildFromJsonl(JsonlPath, PakDir) then Exit;
    if Time <> 0.0 then
      M.ApplyTime(Time);  // 齿轮：sprite 角 = init + w·t（F372/F373）
    FCamera.Position.SetPoint(M.CamX, M.CamY, 10);
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
      if O.Space = 1 then
      begin
        // SceneModel 的 HUD 坐标是**中心**（设计像素，y 向下）；AddHud 收左上角。
        if not AddHud(O.Asset, O.X + HUD_W - O.W * 0.5,
          O.Y + HUD_H - O.H * 0.5, O.W, O.H, O.Alpha) then Exit;
      end
      else if not AddWorld(O.Asset, O.X, O.Y, O.Angle, O.W * 0.5, O.H * 0.5,
        O.Alpha) then Exit;
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

end.
