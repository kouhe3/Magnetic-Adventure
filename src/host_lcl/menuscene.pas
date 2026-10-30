unit MenuScene;
{$mode objfpc}{$H+}
// 主菜单场景（M6/T6.2）：把原版的 19 条静态 draw + 光标还原成 GLScene HUD 图元。
//
// 依据（docs/facts.md）：
//   F216/F224 原版一帧菜单 21 个 draw：19..37 号纹理各一次，其中 tex=35（用户名文本）
//        是 12 顶点的字串、且**画两遍**（可见层 alpha=1 + 隐藏层 alpha=0）。
//   F188 设计空间 1018×739 固定：改客户区不重排。
//   F189 六个按钮各有 base/hover 两层，两层**都画**，用 alpha 互斥（不是画一层）。
//   F179/F219 相机 ±26.862×±19.5；菜单走 HUD 路径（每 draw 覆盖投影为 identity）。
//   F222 单帧抓包必须 GLPROXY_FLUSH=1。
//
// 坐标：设计像素、左上原点。位置 = 矩形中心（GLHUDObjects.DoRender 用
//   `vp.cy*0.5 - Position.Y` 反算，即 Position.Y 按自上而下解读），尺寸 = 矩形宽高。
//
// 覆盖边界：文本层（tex=35，gulim1.dat 字模）尚未实现（T3.5/T6.4）；
//   悬停状态本轮按"鼠标未命中任何按钮"（与 glidle 抓包同状态）。

interface

uses Classes, SysUtils, Graphics, GLScene, GLHUDObjects, GLTexture, GLMaterial,
  GLGraphics, GLFilePNG, GLTextureFormat, GLRenderContextInfo, GLState, OpenGL1x,
  PakFile;

type
  // gulim1.dat 的一条字模记录（32 B，F192）：u32 字符码; f32 u0,v0,u1,v1; u32 w,h,flag。
  // UV 以 512 归一化、v 自下而上（v0 对应 GL 的下边），advance == w。
  TGlyph = record
    Code: Cardinal;
    U0, V0, U1, V1: Single;
    W, H, Flags: Cardinal;
  end;

  TFontTable = class
  private
    FItems: array of TGlyph;
  public
    Loaded: Boolean;
    Count: Integer;
    function Load(Pak: TPakFile; const Asset: string): Boolean;
    function Find(Code: Cardinal): Integer;   // -1 = 表里没有这个字
    function GlyphAt(Index: Integer): TGlyph;
  end;

  // 一个字串 = 一次 glBegin(GL_QUADS) 里 N 个字模 quad（F186/F192：原版就是这样画的）。
  TMagTextSprite = class(TGLHUDSprite)
  private
    FFont: TFontTable;
    FText: string;
  public
    property Font: TFontTable read FFont write FFont;
    property Text: string read FText write FText;
    procedure DoRender(var rci: TRenderContextInfo; drawSelf,
      drawKids: Boolean); override;
  end;

  // 直接把 32 位 RGBA 交给 GLScene 上传的纹理图像。
  //
  // 为什么不直接用 TGLPersistentImage：它走 LCL 的 TPicture/TBitmap，0.9.28.3 的
  // TPicture 读 PNG 会丢掉 alpha ⇒ 透明背景整块变黑（实测：按钮 hover 层把 base 层
  // 盖死、黑板内部不透出木纹）。原版为此链接了 GLFilePNG 并给 GLTexture 打补丁
  // （F213），这里用等价但更直接的方式：GLFilePNG 解码 → 自己的 TGLBitmap32。
  TMagImage = class(TGLTextureImage)
  private
    FBitmap: TGLBitmap32;
  protected
    function GetTextureTarget: TGLTextureTarget; override;
    function GetHeight: Integer; override;
    function GetWidth: Integer; override;
    function GetDepth: Integer; override;
  public
    AlphaZero: Integer;   // 自检：alpha==0 的像素数（写进 gl_init.log）
    AlphaTotal: Integer;
    constructor Create(AOwner: TPersistent); override;
    destructor Destroy; override;
    procedure Assign(Source: TPersistent); override;
    procedure SaveToFile(const fileName: string); override;
    function GetBitmap32(target: TGLUInt = GL_TEXTURE_2D): TGLBitmap32; override;
    class function FriendlyName: string; override;
    // PNG：GLFilePNG 解码（RGBA），行序翻成 GL 的底在上。
    procedure LoadPng(const Path: string);
    // JPG：LCL TPicture 解码（原版没有链接 GLFileJPG，F202），不透明。
    procedure LoadJpeg(const Path: string);
  end;

type
  TMenuScene = class
  private
    FScene: TGLScene;
    FPak: TPakFile;
    FCursorX, FCursorY: Single;
    FLayers: Integer;
    FLog: string;
    FDumpDir: string;
    FOnly: Integer;    // HOST_MENU_ONLY=<index>：只建这一层（排查用）
    FIndex: Integer;
    FTint: Boolean;    // HOST_MENU_TINT=1：所有层染红（判 alpha 是"没画"还是"画成不透明"）
    FFont: TFontTable;
    function LoadTexture(const Asset: string; Tex: TGLTexture): Boolean;
    procedure AddLayer(const Asset: string; X, Y, W, H, Alpha: Single);
    procedure AddText(const S: string; X, Y, Alpha: Single);
  public
    constructor Create(Scene: TGLScene; Pak: TPakFile);
    destructor Destroy; override;
    // 建 19 条静态层；Cursor=false 时不建光标（原版鼠标离开窗口时不画）。
    function Build(Cursor: Boolean; CursorX, CursorY: Single): Boolean;
    property Log: string read FLog;
    property Layers: Integer read FLayers;
    property Font: TFontTable read FFont;
  end;

function TempFilePath(const Ext: string): string;

implementation

uses Windows;

constructor TMagImage.Create(AOwner: TPersistent);
begin
  inherited Create(AOwner);
  FBitmap := TGLBitmap32.Create;
end;

destructor TMagImage.Destroy;
begin
  FBitmap.Free;
  inherited Destroy;
end;

procedure TMagImage.Assign(Source: TPersistent);
begin
  // TGLTexture.SetImage 会把新图像 Assign 进纹理里已有的 FImage（同类实例），
  // 不覆盖 Assign 就会抛 "Cannot assign a TMagImage to a TMagImage"。
  if Source is TMagImage then
  begin
    FBitmap.Assign(TMagImage(Source).FBitmap);
    NotifyChange(Self);
  end
  else
    inherited Assign(Source);
end;

function TMagImage.GetBitmap32(target: TGLUInt): TGLBitmap32;
begin
  Result := FBitmap;
end;

function TMagImage.GetWidth: Integer;
begin
  Result := FBitmap.Width;
end;

function TMagImage.GetHeight: Integer;
begin
  Result := FBitmap.Height;
end;

function TMagImage.GetDepth: Integer;
begin
  Result := 1;
end;

function TMagImage.GetTextureTarget: TGLTextureTarget;
begin
  Result := ttTexture2D;
end;

class function TMagImage.FriendlyName: string;
begin
  Result := 'MagImage';
end;

procedure TMagImage.SaveToFile(const fileName: string);
var
  fs: TFileStream;
  hdr: AnsiString;
  line: PByte;
  y, x: Integer;
  p: PByte;
begin
  // 只用于排查：写 PPM(P6)，24 位、丢掉 alpha。
  fs := TFileStream.Create(fileName, fmCreate);
  try
    hdr := AnsiString('P6'#10 + IntToStr(GetWidth) + ' ' + IntToStr(GetHeight) +
      #10'255'#10);
    fs.WriteBuffer(hdr[1], Length(hdr));
    GetMem(line, GetWidth * 3);
    try
      for y := 0 to GetHeight - 1 do
      begin
        p := PByte(FBitmap.ScanLine[y]);
        for x := 0 to GetWidth - 1 do
        begin
          line[x * 3 + 0] := p[x * 4 + 0];
          line[x * 3 + 1] := p[x * 4 + 1];
          line[x * 3 + 2] := p[x * 4 + 2];
        end;
        fs.WriteBuffer(line^, GetWidth * 3);
      end;
    finally
      FreeMem(line);
    end;
  finally
    fs.Free;
  end;
end;

procedure TMagImage.LoadPng(const Path: string);
var
  Png: TGLPNGImage;
  w, h, y, i: Integer;
  src, dst: PByte;
begin
  // TGLBaseImage.Create 是无参的（覆盖了 TDataFile.Create(AOwner)）。
  Png := TGLPNGImage.Create;
  try
    Png.LoadFromFile(Path);
    w := Png.Width;
    h := Png.Height;
    if (w <= 0) or (h <= 0) or (Png.Data = nil) then
      raise Exception.Create('PNG 解码为空: ' + Path);
    // 顺序要紧：TGLBitmap32 按当前 ColorFormat/InternalFormat 分配缓冲，
    // 先设尺寸会按未初始化格式分配 ⇒ Data 为 nil（实测 Access violation）。
    FBitmap.ColorFormat := GL_RGBA;
    FBitmap.InternalFormat := tfRGBA8;
    FBitmap.DataType := GL_UNSIGNED_BYTE;
    FBitmap.Width := w;
    FBitmap.Height := h;
    // TGLBitmap32 默认 Blank=True（不分配像素缓冲），必须显式置 False 才真正分配。
    FBitmap.Blank := False;
    if FBitmap.Data = nil then
      raise Exception.Create('TGLBitmap32 缓冲分配失败: ' + Path);
    // 行序：GLFilePNG 交出来的就是 GL 需要的底在上（实测翻了一次反而上下颠倒）。
    src := PByte(Png.Data);
    dst := PByte(FBitmap.Data);
    for y := 0 to h - 1 do
      Move(src[y * w * 4], dst[y * w * 4], w * 4);
    AlphaTotal := w * h;
    AlphaZero := 0;
    for i := 0 to w * h - 1 do
      if dst[i * 4 + 3] = 0 then Inc(AlphaZero);
  finally
    Png.Free;
  end;
end;

procedure TMagImage.LoadJpeg(const Path: string);
var
  Pic: TPicture;
begin
  Pic := TPicture.Create;
  try
    Pic.LoadFromFile(Path);
    if (Pic.Width <= 0) or (Pic.Height <= 0) then
      raise Exception.Create('JPG 解码为空: ' + Path);
    FBitmap.Assign(Pic.Bitmap);
  finally
    Pic.Free;
  end;
end;

function TFontTable.Load(Pak: TPakFile; const Asset: string): Boolean;
var
  Stream: TMemoryStream;
  i, n: Integer;
  p: PByte;
begin
  Result := False;
  Loaded := False;
  Count := 0;
  if Pak = nil then Exit;
  if not Pak.Read(Asset, Stream) then Exit;
  try
    n := Stream.Size div 32;
    SetLength(FItems, n);
    p := PByte(Stream.Memory);
    for i := 0 to n - 1 do
    begin
      FItems[i].Code := PCardinal(p)^; Inc(p, 4);
      FItems[i].U0 := PSingle(p)^; Inc(p, 4);
      FItems[i].V0 := PSingle(p)^; Inc(p, 4);
      FItems[i].U1 := PSingle(p)^; Inc(p, 4);
      FItems[i].V1 := PSingle(p)^; Inc(p, 4);
      FItems[i].W := PCardinal(p)^; Inc(p, 4);
      FItems[i].H := PCardinal(p)^; Inc(p, 4);
      FItems[i].Flags := PCardinal(p)^; Inc(p, 4);
    end;
    Count := n;
    Loaded := n > 0;
    Result := Loaded;
  finally
    Stream.Free;
  end;
end;

function TFontTable.GlyphAt(Index: Integer): TGlyph;
begin
  Result := FItems[Index];
end;

function TFontTable.Find(Code: Cardinal): Integer;
var
  i: Integer;
begin
  for i := 0 to Count - 1 do
    if FItems[i].Code = Code then
      Exit(i);
  Result := -1;
end;

procedure TMagTextSprite.DoRender(var rci: TRenderContextInfo; drawSelf,
  drawKids: Boolean);
var
  f, vx, vy, vy1, x, gw: Single;
  i, gi: Integer;
  g: TGlyph;
begin
  if rci.ignoreMaterials then Exit;
  // 矩阵/状态与 TGLHUDSprite.DoRender 同形（F225 已证逐 draw 一致），
  // 差别只在一次 glBegin 里画 N 个 quad（F186：原版整串是一个 glBegin）。
  Material.Apply(rci);
  glMatrixMode(GL_MODELVIEW);
  glPushMatrix;
  glLoadMatrixf(@TGLSceneBuffer(rci.buffer).BaseProjectionMatrix);
  if rci.renderDPI = 96 then
    f := 1
  else
    f := rci.renderDPI / 96;
  glScalef(2 / rci.viewPortSize.cx, 2 / rci.viewPortSize.cy, 1);
  glTranslatef(f * Position.X - rci.viewPortSize.cx * 0.5,
    rci.viewPortSize.cy * 0.5 - f * Position.Y, Position.Z);
  glMatrixMode(GL_PROJECTION);
  glPushMatrix;
  glLoadIdentity;
  rci.GLStates.Disable(stDepthTest);
  rci.GLStates.DepthWriteMask := False;
  if (FFont <> nil) and FFont.Loaded and (FText <> '') then
  begin
    vx := -Width * 0.5 * f;
    vy := Height * 0.5 * f;
    vy1 := vy - Height * f;
    x := vx;
    glBegin(GL_QUADS);
    for i := 1 to Length(FText) do
    begin
      gi := FFont.Find(Cardinal(Ord(FText[i])));
      if gi < 0 then Continue;
      g := FFont.GlyphAt(gi);
      gw := g.W * f;
      glTexCoord2f(g.U0, g.V0); glVertex2f(x, vy1);
      glTexCoord2f(g.U1, g.V0); glVertex2f(x + gw, vy1);
      glTexCoord2f(g.U1, g.V1); glVertex2f(x + gw, vy);
      glTexCoord2f(g.U0, g.V1); glVertex2f(x, vy);
      x := x + gw;
    end;
    glEnd;
  end;
  glPopMatrix;
  glMatrixMode(GL_MODELVIEW);
  glPopMatrix;
  Material.UnApply(rci);
  if Count > 0 then
    Self.RenderChildren(0, Count - 1, rci);
end;

function TempFilePath(const Ext: string): string;
var
  dir, name: array[0..MAX_PATH - 1] of Char;
  tmp: string;
begin
  GetTempPath(MAX_PATH, @dir[0]);
  GetTempFileName(@dir[0], 'mgt', 0, @name[0]);
  tmp := name;
  Result := ChangeFileExt(tmp, Ext);
  DeleteFile(PChar(tmp));
end;

constructor TMenuScene.Create(Scene: TGLScene; Pak: TPakFile);
var
  buf: array[0..MAX_PATH - 1] of Char;
begin
  inherited Create;
  FScene := Scene;
  FPak := Pak;
  FLog := '';
  if Windows.GetEnvironmentVariable('HOST_TEX_DUMP', @buf[0], MAX_PATH) > 0 then
    FDumpDir := buf
  else
    FDumpDir := '';
  FOnly := -1;
  if Windows.GetEnvironmentVariable('HOST_MENU_ONLY', @buf[0], MAX_PATH) > 0 then
    FOnly := StrToIntDef(buf, -1);
  FTint := Windows.GetEnvironmentVariable('HOST_MENU_TINT', @buf[0], MAX_PATH) > 0;
  FIndex := 0;
  FFont := TFontTable.Create;
  FFont.Load(Pak, 'gulim1.dat');
  FLog := FLog + 'font=' + IntToStr(FFont.Count) + #13#10;
end;

destructor TMenuScene.Destroy;
begin
  FFont.Free;
  inherited Destroy;
end;

procedure TMenuScene.AddText(const S: string; X, Y, Alpha: Single);
var
  Sprite: TMagTextSprite;
  i, gi, w, h: Integer;
begin
  Inc(FIndex);
  if (FOnly >= 0) and (FIndex <> FOnly) then Exit;
  if not FFont.Loaded then Exit;
  w := 0;
  h := 0;
  for i := 1 to Length(S) do
  begin
    gi := FFont.Find(Cardinal(Ord(S[i])));
    if gi < 0 then Continue;
    Inc(w, FFont.GlyphAt(gi).W);
    if Integer(FFont.GlyphAt(gi).H) > h then h := FFont.GlyphAt(gi).H;
  end;
  if (w = 0) or (h = 0) then Exit;
  Sprite := TMagTextSprite.Create(FScene);
  Sprite.Font := FFont;
  Sprite.Text := S;
  Sprite.Position.SetPoint(X + w * 0.5, Y + h * 0.5, 0);
  Sprite.Width := w;
  Sprite.Height := h;
  if FTint then
    Sprite.Material.FrontProperties.Diffuse.SetColor(1, 0, 0, Alpha)
  else
    Sprite.Material.FrontProperties.Diffuse.SetColor(0.8984375, 0.78515625,
      0.51953125, Alpha);
  Sprite.Material.BlendingMode := bmTransparency;
  Sprite.Material.Texture.TextureMode := tmModulate;
  if not LoadTexture('gulim1.png', Sprite.Material.Texture) then
  begin
    Sprite.Free;
    Exit;
  end;
  FScene.Objects.AddChild(Sprite);
  Inc(FLayers);
end;

function TMenuScene.LoadTexture(const Asset: string; Tex: TGLTexture): Boolean;
var
  Stream: TMemoryStream;
  Path, Ext: string;
  Img: TMagImage;
begin
  Result := False;
  if FPak = nil then Exit;
  if not FPak.Read(Asset, Stream) then
  begin
    FLog := FLog + 'missing ' + Asset + #13#10;
    Exit;
  end;
  try
    Ext := ExtractFileExt(Asset);
    if Ext = '' then Ext := '.png';
    Path := TempFilePath(Ext);
    try
      Stream.SaveToFile(Path);
      try
        Img := TMagImage.Create(Tex);
        try
          if CompareText(Ext, '.png') = 0 then
            Img.LoadPng(Path)
          else
            Img.LoadJpeg(Path);
        except
          on E: Exception do
          begin
            Img.Free;
            FLog := FLog + 'decode ' + Asset + ': ' + E.Message + #13#10;
            Exit;
          end;
        end;
        Tex.Image := Img;
      except
        on E: Exception do
        begin
          FLog := FLog + 'assign ' + Asset + ': ' + E.Message + #13#10;
          Exit;
        end;
      end;
      if FDumpDir <> '' then
        try
          Tex.Image.SaveToFile(IncludeTrailingPathDelimiter(FDumpDir) +
            ChangeFileExt(ExtractFileName(Asset), '.png'));
        except
          on E: Exception do
            FLog := FLog + 'dump ' + Asset + ': ' + E.Message + #13#10;
        end;
      FLog := FLog + 'tex ' + Asset + ' ' + IntToStr(Tex.Image.Width) + 'x' +
        IntToStr(Tex.Image.Height) + ' a0=' + IntToStr(Img.AlphaZero) + '/' +
        IntToStr(Img.AlphaTotal);
      if Tex.Image is TMagImage then
        FLog := FLog + ' copy=' + IntToStr(TMagImage(Tex.Image).AlphaZero) + '/' +
          IntToStr(TMagImage(Tex.Image).AlphaTotal);
      FLog := FLog + #13#10;
      Tex.Disabled := False;
      Result := True;
    finally
      DeleteFile(PChar(Path));
    end;
  finally
    Stream.Free;
  end;
end;

procedure TMenuScene.AddLayer(const Asset: string; X, Y, W, H, Alpha: Single);
var
  Sprite: TGLHUDSprite;
begin
  Inc(FIndex);
  if (FOnly >= 0) and (FIndex <> FOnly) then Exit;
  Sprite := TGLHUDSprite.Create(FScene);
  Sprite.Position.SetPoint(X + W * 0.5, Y + H * 0.5, 0);
  Sprite.Width := W;
  Sprite.Height := H;
  // 层透明度走材质的 diffuse alpha（原版每个 draw 都有 glColor4fv (1,1,1,α)），
  // 不是 AlphaChannel：后者在 lightingDisabledCounter=0 时走 SetGLMaterialAlphaChannel，
  // 被材质的 diffuse alpha=1 覆盖掉，隐藏层会变成不透明（实测按钮被 hover 层盖死）。
  if FTint then
    Sprite.Material.FrontProperties.Diffuse.SetColor(1, 0, 0, Alpha)
  else
    Sprite.Material.FrontProperties.Diffuse.SetColor(1, 1, 1, Alpha);
  // 原版启动期就把 BLEND/ALPHA_TEST 打开并把 blendFunc 设为 SRC_ALPHA/ONE_MINUS_SRC_ALPHA
  // 并保持（帧内没有 glBlendFunc、glEnable(GL_BLEND) 记录）；bmTransparency 走 GLStates
  // 状态缓存，第一帧之后不再重复发调用，与原版一致（F184）。
  Sprite.Material.BlendingMode := bmTransparency;
  // GLScene 的 TextureMode 默认是 tmDecal ⇒ glTexEnvi(GL_DECAL)，DECAL 模式下
  // **片元 alpha 取的是着色器颜色而不是纹理 alpha**（透明处露出白色底色）。
  // 菜单要的是常规 alpha 混合，用 tmModulate（C=tex*frag, A=tex.a*frag.a）。
  Sprite.Material.Texture.TextureMode := tmModulate;
  if not LoadTexture(Asset, Sprite.Material.Texture) then
  begin
    Sprite.Free;
    Exit;
  end;
  // JPG 没有 alpha 通道：原版按 RGB8 上传（F185），这里别让 GLScene 升成 RGBA。
  if CompareText(ExtractFileExt(Asset), '.jpg') = 0 then
    Sprite.Material.Texture.ImageAlpha := tiaOpaque;
  FScene.Objects.AddChild(Sprite);
  Inc(FLayers);
end;

function TMenuScene.Build(Cursor: Boolean; CursorX, CursorY: Single): Boolean;
var
  only: Integer;
begin
  // 顺序 = 原版 draw 顺序（gl_drawlist 实测）：背景两半 → 黑板 → 标签 →
  // 六个按钮（base 后 hover）→ 中央微光 → 标题 → 光标。
  AddLayer('menubk_1.jpg', -0.5, -0.25, 1019, 370, 1);
  AddLayer('menubk_2.jpg', -0.5, 369.25, 1019, 370, 1);
  AddLayer('mm_cent2.png', -3, 163, 1024, 512, 1);
  AddLayer('m_label1.png', 277, 186, 256, 64, 1);
  AddLayer('play_1.png', 223, 224, 256, 128, 1);
  AddLayer('play_2.png', 223, 224, 256, 128, 0);
  AddLayer('exit_1.png', 557, 510, 256, 128, 1);
  AddLayer('exit_2.png', 557, 510, 256, 128, 0);
  AddLayer('help_1.png', 301, 490, 128, 128, 1);
  AddLayer('help_2.png', 301, 490, 128, 128, 0);
  AddLayer('levels_1.png', 221, 350, 128, 128, 1);
  AddLayer('levels_2.png', 221, 350, 128, 128, 0);
  AddLayer('option_1.png', 615, 356, 256, 128, 1);
  AddLayer('option_2.png', 615, 356, 256, 128, 0);
  AddLayer('profil_1.png', 579, 226, 256, 128, 1);
  AddLayer('profil_2.png', 579, 226, 256, 128, 0);
  // 用户名文本（F192）：原版整串一个 glBegin、画**两遍**（可见层 alpha=1 + 隐藏层 alpha=0），
  // 位置/字串取自抓包那一帧；字串来源（存档/配置）属 T6.4。
  AddText('ooo', 509, 204.5, 1);
  AddText('ooo', 509, 204.5, 0);
  AddLayer('mm_cent1.png', -65.5, 140, 1205, 602, 1);
  AddLayer('gamename.png', 253, 60, 512, 128, 1);
  if Cursor then
    AddLayer('mcur_1.png', CursorX - 16, CursorY - 16, 32, 32, 1);
  Result := FLayers = 21 + Ord(Cursor);
  FCursorX := CursorX;
  FCursorY := CursorY;
end;

end.
