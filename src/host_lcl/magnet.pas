program magnet;
{$mode objfpc}{$H+}
// Magnetic Adventure 宿主（FPC/LCL + GLScene 重建路线）—— 种子实现。
//
// 现状：窗口层（F214）+ T6.2 场景种子（相机 + 红色测试立方体；F217/F218）。
// 视口/呈现已证通（黑底 + 3306 个红像素）；GLScene 内部调用不进 GL 代理（F215）。
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
  Interfaces, Forms, Controls, Graphics, GLScene, GLObjects, GLLCLViewer,
  OpenGL1x, VectorGeometry, Windows;

type
  TCameraEvents = class
    procedure Ortho(const viewport: TRectangle; width, height, DPI: Integer;
      var viewPortRadius: Single);
  end;

procedure TCameraEvents.Ortho(const viewport: TRectangle; width, height,
  DPI: Integer; var viewPortRadius: Single);
begin
  // 原版菜单/关卡的正交相机：glOrtho(±26.862, ±19.5) ⇒ 18.95 px/unit（F179）。
  glOrtho(-26.862, 26.862, -19.5, 19.5, -100, 100);
  viewPortRadius := 33.2;
end;

var
  F: TForm;
  S: TGLScene;
  Cam: TGLCamera;
  Cube: TGLCube;
  CamEvents: TCameraEvents;
  V: TGLSceneViewer;
  r: TRect;
begin
  Application.Initialize;

  F := TForm.CreateNew(nil, 0);
  F.Caption := 'A Magnetic Adventure';
  F.BorderStyle := bsNone;

  S := TGLScene.Create(F);
  CamEvents := TCameraEvents.Create;
  Cam := TGLCamera.Create(S);
  Cam.Position.SetPoint(0, 0, 10);
  Cam.CameraStyle := csCustom;
  Cam.OnCustomPerspective := @CamEvents.Ortho;
  S.Objects.AddChild(Cam);
  Cube := TGLCube.Create(S);
  Cube.Material.FrontProperties.Diffuse.SetColor(1, 0, 0, 1);
  Cube.Material.FrontProperties.Emission.SetColor(1, 0, 0, 1);
  S.Objects.AddChild(Cube);
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
  V.Render;

  Application.Run;
end.
