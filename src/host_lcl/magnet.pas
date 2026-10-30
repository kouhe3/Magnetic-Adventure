program magnet;
{$mode objfpc}{$H+}
// Magnetic Adventure 宿主（FPC/LCL + GLScene 重建路线）—— 种子实现。
//
// 现状：窗口层（F214）+ T6.2 场景种子（正交相机 + 测试立方体 + pak 纹理；
// F217–F220）。视口/呈现/纹理直读 pak 已证通；GLScene 内部调用不进 GL 代理（F215）。
// 构建（需要 FPC 2.2.4 + 自编 LCL 0.9.28.3，见 HANDOFF §3.2）：
//   python tools/glskel_build.py work/glscene_patch build/host_lcl src/host_lcl/magnet.pas
// 运行前置：与 exe 同目录需要 libpng13.dll + zlib1.dll（GLFilePNG 的运行时依赖，
//   原版目录 bin/gametop 里就有）。
// 验收：python tools/wincompare.py --orig work/winprobe_game \
//         --ours build/host_lcl --ours-exe magnet.exe  → fields=15 diffs=0
//
// 窗口配方（F154/F155/F157/F158/F166，逐条都有实测出处）：
//   1. TForm.CreateNew + Caption，BorderStyle := bsNone —— 原版 style 里带 WS_POPUP，
//      说明它是"无边框建窗、之后手工补 caption 位"，不是运行时切 BorderStyle
//      （LCL 切 BorderStyle 会 RecreateWnd，WS_POPUP 会丢）。
//   2. Show 之后 SetWindowLong 补 WS_CAPTION|WS_SYSMENU|WS_MINIMIZEBOX，
//      再 SetWindowPos(FRAMECHANGED) 让 Windows 重算非客户区。
//   3. 外框 1024x768、按**外框**在屏幕上居中（原版 341,96 = (1707-1024)/2, (960-768)/2；
//      LCL 的 poDesktopCenter 按客户区算，会给 344,110）。
//   4. GL 视口用 GetClientRect 的真实客户区重排：原生改 style 后 LCL 缓存的 ClientWidth
//      还是旧值，直接 alClient 会得到 1024x768。
uses
  Classes, Interfaces, Forms, Controls, Graphics, GLScene, GLObjects, GLLCLViewer,
  GLFilePNG, GLTexture, OpenGL1x, PakFile, MenuScene, SysUtils, VectorGeometry,
  GLRenderContextInfo, FrameShot, Windows;

type
  TCameraEvents = class
    procedure Ortho(const viewport: TRectangle; width, height, DPI: Integer;
      var viewPortRadius: Single);
  end;

  TGLStateInit = class
    procedure BeforeRender(Sender: TObject);
  end;

procedure TGLStateInit.BeforeRender(Sender: TObject);
begin
  // 每帧开画前设一次：此刻上下文一定 current（BeforeRender 在 Buffer.Render 内部触发）。
  // 原版启动期就是这个状态（F184：帧内没有 glBlendFunc / glEnable(GL_BLEND) 记录），
  // GLScene 的 GLStates 认为 blendFunc 已是 SRC_ALPHA/ONE_MINUS 而不再发调用，
  // 但驱动默认是 (ONE, ZERO) ⇒ alpha 被忽略、透明区画成白块。
  glEnable(GL_BLEND);
  glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
  glEnable(GL_ALPHA_TEST);
  glAlphaFunc(GL_GREATER, 0);
end;

const
  // mapping/textures.csv 的 37 条启动纹理（重复项保留，按原版上传次数）。
  kTextureAssets: array[0..36] of string = (
    'mcur_1.png', 'logo_1.JPG', 'logo_2.JPG', 'logo_3.jpg', 'logo_3.png',
    'hint_atl.png', 'dot_1.png', 'dot_1.png', 'dot_1.png', 'dot_1.png',
    'dot_1.png', 'dot_1.png', 'dot_1.png', 'dot_1.png', 'dot_1.png',
    'dot_1.png', 'mbtn_1.png', 'mbtn_2.png', 'menubk_1.jpg', 'menubk_2.jpg',
    'mm_cent2.png', 'm_label1.png', 'play_1.png', 'play_2.png', 'exit_1.png',
    'exit_2.png', 'help_1.png', 'help_2.png', 'levels_1.png', 'levels_2.png',
    'option_1.png', 'option_2.png', 'profil_1.png', 'profil_2.png',
    'gulim1.png', 'mm_cent1.png', 'gamename.png');

procedure TCameraEvents.Ortho(const viewport: TRectangle; width, height,
  DPI: Integer; var viewPortRadius: Single);
begin
  // 原版菜单/关卡的正交相机：glOrtho(±26.862, ±19.5) ⇒ 18.95 px/unit（F179）。
  glOrtho(-26.862, 26.862, -19.5, 19.5, -100, 100);
  viewPortRadius := 33.2;
end;

function DataPath: string;
var
  n: DWORD;
  buf: array[0..MAX_PATH - 1] of Char;
begin
  n := GetEnvironmentVariable('HOST_DATA', @buf[0], MAX_PATH);
  if n > 0 then
    Result := buf
  else
    Result := 'data';
  if DirectoryExists(Result) then
    Result := IncludeTrailingPathDelimiter(Result) + 'data';
end;

function TempFileName(const Ext: string): string;
var
  dir, name: array[0..MAX_PATH - 1] of Char;
  tmp: string;
begin
  GetTempPath(MAX_PATH, @dir[0]);
  GetTempFileName(@dir[0], 'mag', 0, @name[0]);
  tmp := name;
  Result := ChangeFileExt(tmp, Ext);
  DeleteFile(PChar(tmp));
end;

function SelfTestTextures(Pak: TPakFile; out Log: string): Integer;
var
  i: Integer;
  Stream: TMemoryStream;
  Pic: TPicture;
  Path, Ext: string;
begin
  Result := 0;
  Log := '';
  for i := 0 to High(kTextureAssets) do
  begin
    Stream := nil;
    if not Pak.Read(kTextureAssets[i], Stream) then
    begin
      Log := Log + 'missing ' + kTextureAssets[i] + #13#10;
      Continue;
    end;
    Ext := ExtractFileExt(kTextureAssets[i]);
    if Ext = '' then Ext := '.png';
    Path := TempFileName(Ext);
    try
      try
        Stream.SaveToFile(Path);
        Pic := TPicture.Create;
        try
          Pic.LoadFromFile(Path);
          if (Pic.Width > 0) and (Pic.Height > 0) then
            Inc(Result)
          else
            Log := Log + 'empty ' + kTextureAssets[i] + #13#10;
        finally
          Pic.Free;
        end;
      except
        on E: Exception do
          Log := Log + 'fail ' + kTextureAssets[i] + ': ' + E.Message + #13#10;
      end;
    finally
      DeleteFile(PChar(Path));
      Stream.Free;
    end;
  end;
end;

function EnvFlag(const Name: string): Boolean;
var
  buf: array[0..7] of Char;
begin
  Result := (GetEnvironmentVariable(PChar(Name), @buf[0], 8) > 0) and
    (buf[0] = '1');
end;

function EnvStr(const Name: string): string;
var
  buf: array[0..MAX_PATH - 1] of Char;
begin
  if GetEnvironmentVariable(PChar(Name), @buf[0], MAX_PATH) > 0 then
    Result := buf
  else
    Result := '';
end;

// 日志一律落在 exe 旁边（build/ 已 gitignore），别污染仓库根的 CWD。
function ExePath(const Name: string): string;
begin
  Result := IncludeTrailingPathDelimiter(ExtractFilePath(ParamStr(0))) + Name;
end;

var
  F: TForm;
  S: TGLScene;
  Cam: TGLCamera;
  Menu: TMenuScene;
  CamEvents: TCameraEvents;
  Pak: TPakFile;
  n: Integer;
  log: string;
  tf: TextFile;
  V: TGLSceneViewer;
  r: TRect;
  MouseX, MouseY: Single;
  DumpVp: array[0..3] of Integer;
  StateInit: TGLStateInit;
begin
  Application.Initialize;

  F := TForm.CreateNew(nil, 0);
  F.Caption := 'A Magnetic Adventure';
  F.BorderStyle := bsNone;

  S := TGLScene.Create(F);
  // GLScene 默认 ObjectsSorting=osRenderBlendedLast：会把"混合对象"排到最后重排
  // 绘制顺序，菜单的 painter 顺序（背景→黑板→按钮→标题→光标）就乱了——
  // 实测背景被排到黑板之后，把黑板上半截盖掉。原版是严格按对象顺序画的。
  S.ObjectsSorting := osNone;
  CamEvents := TCameraEvents.Create;
  Cam := TGLCamera.Create(S);
  Cam.Position.SetPoint(0, 0, 10);
  Cam.CameraStyle := csCustom;
  Cam.OnCustomPerspective := @CamEvents.Ortho;
  S.Objects.AddChild(Cam);
  Pak := TPakFile.Create;
  if Pak.Open(DataPath) then
  begin
    if EnvFlag('HOST_TEX_SELFTEST') then
    begin
      n := SelfTestTextures(Pak, log);
      AssignFile(tf, ExePath('host_tex_selftest.log'));
      Rewrite(tf);
      WriteLn(tf, 'loaded=', n, '/', Length(kTextureAssets));
      Write(tf, log);
      CloseFile(tf);
    end;
    // 鼠标位置（设计像素，左上原点）：默认停在 glidle 抓包那一帧的位置
    // (884,684)-(916,716) 的中心 (900,700)，这样 A/B 是同状态（F188/F189）。
    MouseX := 900;
    MouseY := 700;
    Menu := TMenuScene.Create(S, Pak);
    Menu.Build(True, MouseX, MouseY);
    AssignFile(tf, ExePath('gl_init.log'));
    Rewrite(tf);
    WriteLn(tf, 'layers=', Menu.Layers, ' font=', Menu.Font.Count, ' text=ooo');
    Write(tf, Menu.Log);
    CloseFile(tf);
  end;
  V := TGLSceneViewer.Create(F);
  V.Parent := F;
  V.Align := alClient;
  V.Camera := Cam;
  V.Buffer.BackgroundColor := clBlack;
  V.Buffer.Lighting := False;

  F.Show;

  SetWindowLong(F.Handle, GWL_STYLE,
    GetWindowLong(F.Handle, GWL_STYLE) or WS_CAPTION or WS_SYSMENU or WS_MINIMIZEBOX);
  SetWindowPos(F.Handle, 0, 0, 0, 0, 0,
    SWP_NOMOVE or SWP_NOSIZE or SWP_NOZORDER or SWP_FRAMECHANGED);

  F.Width := 1024;
  F.Height := 768;
  F.Left := (Screen.Width - 1024) div 2;
  F.Top := (Screen.Height - 768) div 2;

  GetClientRect(F.Handle, r);
  V.Align := alNone;
  V.SetBounds(0, 0, r.Right, r.Bottom);
  V.Show;
  V.BringToFront;

  V.Invalidate;
  Application.ProcessMessages;
  // 上下文在第一帧渲染时才建立，且 PostRender 是唯一"上下文一定 current"的钩子。
  StateInit := TGLStateInit.Create;
  V.BeforeRender := @StateInit.BeforeRender;
  V.Render;
  V.Render;
  // 像素验收走自读帧缓冲（HOST_DUMP_FRAME），不受窗口层叠影响。
  if EnvStr('HOST_DUMP_FRAME') <> '' then
  begin
    AssignFile(tf, ExePath('gl_dump.log'));
    Rewrite(tf);
    WriteLn(tf, 'path=', EnvStr('HOST_DUMP_FRAME'));
    try
      // GLScene 在 Render 后会把上下文解绑（此时 glGetIntegerv 全 0），
      // 读回前必须自己 Activate。
      if V.Buffer.RenderingContext.IsValid then
        V.Buffer.RenderingContext.Activate;
      try
        WriteLn(tf, 'size=', V.ClientWidth, 'x', V.ClientHeight,
          ' ok=', DumpFramebufferBmp(EnvStr('HOST_DUMP_FRAME'), V.ClientWidth,
          V.ClientHeight));
      finally
        V.Buffer.RenderingContext.Deactivate;
      end;
    except
      on E: Exception do
        WriteLn(tf, 'exc=', E.ClassName, ': ', E.Message);
    end;
    CloseFile(tf);
  end;

  Application.Run;
end.
