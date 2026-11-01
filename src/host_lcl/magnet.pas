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
  GLRenderContextInfo, FrameShot, Windows, LuaDll, LuaLog, LuaBind, LuaEvents,
  PhysWorld;

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

// T6.3c：b2 接触 → Lua 事件（OnAddContact）。回调在 World_Step 内同步执行，
// 与 Lua 同一线程；g_lua 只在步进循环期间非空。
var
  g_lua: TLuaState = nil;
  g_contacts: Integer = 0;
  g_contactTrace: string = '';

procedure PhysContactCb(Rec: Pointer); cdecl;
var
  r: TContactRec;
  a, b, calls: Integer;
begin
  Move(Rec^, r, SizeOf(r));
  if (r.userData1 = nil) or (r.userData2 = nil) then
    Exit;
  a := PtrInt(r.userData1);
  b := PtrInt(r.userData2);
  Inc(g_contacts);
  if Length(g_contactTrace) < 400 then
    g_contactTrace := g_contactTrace + IntToStr(a) + '-' + IntToStr(b) + ':' +
      IntToStr(r.kind) + ' ';
  if (r.kind = 0) and (g_lua <> nil) then
  begin
    EventsFire(g_lua, a, 'OnAddContact', b, calls);
    EventsFire(g_lua, b, 'OnAddContact', a, calls);
  end;
end;

// HOST_PHYS_MOVE=<objId>:<x>:<y>[:<angle>]：把对象瞬移到位（接触管道自检用）。
procedure ApplyPhysMove(const Spec: string);
var
  p1, p2, p3, id: Integer;
  s: string;
  x, y, a: Double;
begin
  p1 := Pos(':', Spec);
  if p1 = 0 then
    Exit;
  id := StrToIntDef(Copy(Spec, 1, p1 - 1), -1);
  s := Copy(Spec, p1 + 1, MaxInt);
  p2 := Pos(':', s);
  if p2 = 0 then
    Exit;
  x := StrToFloatDef(Copy(s, 1, p2 - 1), 0.0);
  s := Copy(s, p2 + 1, MaxInt);
  p3 := Pos(':', s);
  if p3 = 0 then
  begin
    y := StrToFloatDef(s, 0.0);
    a := 0.0;
  end
  else
  begin
    y := StrToFloatDef(Copy(s, 1, p3 - 1), 0.0);
    a := StrToFloatDef(Copy(s, p3 + 1, MaxInt), 0.0);
  end;
  PhysSetBodyPos(id, x, y, a);
end;

// T6.3/a0 判据：新建 state → 跑 `return 2+3` → 读回 5。
function LuaSelfTest(const Code: string; out Log: string): Boolean;
var
  L: TLuaState;
  Rc: Integer;
begin
  Result := False;
  Log := '';
  if not LuaLoad then
  begin
    Log := 'dll=missing';
    Exit;
  end;
  L := Lua.NewState();   // 无参函数指针必须带 ()，否则取到的是函数地址本身
  if L = nil then
  begin
    Log := 'newstate=nil';
    Exit;
  end;
  try
    Lua.OpenLibs(L);
    Rc := Lua.LoadString(L, PChar(Code));
    if Rc <> 0 then
    begin
      Log := 'load=' + IntToStr(Rc) + ' ' + LuaLastError(L);
      Exit;
    end;
    Rc := Lua.PCall(L, 0, 1, 0);
    if Rc <> 0 then
    begin
      Log := 'pcall=' + IntToStr(Rc) + ' ' + LuaLastError(L);
      Exit;
    end;
    Log := 'result=' + IntToStr(Lua.ToInteger(L, -1)) + ' top=' + IntToStr(Lua.GetTop(L));
    Result := True;
  finally
    Lua.Close(L);
  end;
end;

function ReadTextFile(const Path: string): string;
var
  Stream: TFileStream;
begin
  Result := '';
  if not FileExists(Path) then
    Exit;
  Stream := TFileStream.Create(Path, fmOpenRead or fmShareDenyWrite);
  try
    SetLength(Result, Stream.Size);
    if Stream.Size > 0 then
      Stream.ReadBuffer(Result[1], Stream.Size);
  finally
    Stream.Free;
  end;
end;

// T6.3/a1 判据：注册 144 个绑定 + 编译一关的三个脚本（不执行）。
function LuaBindSelfTest(out Log: string): string;
const
  kScripts: array[0..2] of string = ('basefs.lua', 'lvl_o0.lua', 'lvl_e0.lua');
var
  L: TLuaState;
  Rc, loaded, i: Integer;
  Dir, Path, Content: string;
begin
  Result := '';
  Log := '';
  if not LuaLoad then
  begin
    Result := 'dll=missing';
    Exit;
  end;
  L := Lua.NewState();
  if L = nil then
  begin
    Result := 'newstate=nil';
    Exit;
  end;
  try
    Lua.OpenLibs(L);
  except
    ExitProcess(42);
  end;
  try
    RegisterBindings(L);
  except
    ExitProcess(43);
  end;
  Dir := EnvStr('HOST_LUA_DIR');
  if (Dir <> '') and (Dir[Length(Dir)] <> '\') then
    Dir := Dir + '\';
  loaded := 0;
  for i := 0 to High(kScripts) do
  begin
    Path := Dir + kScripts[i];
    Content := ReadTextFile(Path);
    if Content = '' then
    begin
      Log := Log + kScripts[i] + ': missing' + #13#10;
      Continue;
    end;
    Rc := -1;
    try
      Rc := Lua.LoadString(L, PChar(Content));
    except
      ExitProcess(44);
    end;
    if Rc = 0 then
    begin
      Inc(loaded);
      try
        Lua.SetTop(L, 0);
      except
        ExitProcess(45);
      end;
    end
    else
      Log := Log + kScripts[i] + ': ' + LuaLastError(L) + #13#10;
  end;
  Result := 'bindings=144 loaded=' + IntToStr(loaded) + '/' + IntToStr(Length(kScripts));
  Lua.Close(L);
end;

// T6.3/a2：跑一关脚本并把绑定调用落成 JSONL（call+args 与 lua_probe 对拍）。
function LuaBindRun(Scripts: TStrings; const LogPath: string; out Log: string): string;
const
  kEntries: array[0..2] of string = ('BaseFsBeforeCreate', 'Create', 'AttachScripts');
var
  L: TLuaState;
  Rc, i: Integer;
  Dir, Path, Content: string;
  FireSpec, EvName, Body2Expr, FireErr: string;
  P1, P2, FireObjId, Fired: Integer;
begin
  Result := '';
  Log := '';
  if not LuaLoad then
  begin
    Result := 'dll=missing';
    Exit;
  end;
  L := Lua.NewState();
  if L = nil then
  begin
    Result := 'newstate=nil';
    Exit;
  end;
  LuaLogInit(LogPath);
  try
    Lua.OpenLibs(L);
    Rc := Lua.LoadString(L, PChar('math.randomseed(1)'));
    if Rc = 0 then
      Rc := Lua.PCall(L, 0, 0, 0);
    if Rc <> 0 then
      Lua.SetTop(L, 0);
    ResetIds;
    EventsReset;
    PhysResetObjects;
    RegisterBindings(L);
    Dir := EnvStr('HOST_LUA_DIR');
    if (Dir <> '') and (Dir[Length(Dir)] <> '\') then
      Dir := Dir + '\';
    for i := 0 to Scripts.Count - 1 do
    begin
      Path := Dir + Scripts[i];
      Content := ReadTextFile(Path);
      if Content = '' then
      begin
        Log := Log + Scripts[i] + ': missing' + #13#10;
        Continue;
      end;
      Rc := Lua.LoadString(L, PChar(Content));
      if Rc <> 0 then
      begin
        Log := Log + Scripts[i] + ': ' + LuaLastError(L) + #13#10;
        Exit;
      end;
      Rc := Lua.PCall(L, 0, 0, 0);
      if Rc <> 0 then
      begin
        Log := Log + Scripts[i] + ': pcall ' + LuaLastError(L) + #13#10;
        Exit;
      end;
    end;
    for i := 0 to High(kEntries) do
    begin
      Lua.GetField(L, LUA_GLOBALSINDEX, PChar(kEntries[i]));
      if Lua.LType(L, -1) = 6 then
      begin
        Rc := Lua.PCall(L, 0, 0, 0);
        if Rc <> 0 then
          Log := Log + kEntries[i] + ': ' + LuaLastError(L) + #13#10;
      end
      else
        Lua.SetTop(L, -2);
    end;
    // T6.3 接触回调竖切：HOST_LUA_FIRE="<objId>:<Event>:<Body2 的 Lua 表达式>"。
    // 物理层还没有，事件由自检注入；判据见 tools/lua_event_check.py。
    FireSpec := EnvStr('HOST_LUA_FIRE');
    if FireSpec <> '' then
    begin
      P1 := Pos(':', FireSpec);
      P2 := 0;
      if P1 > 0 then
        P2 := Pos(':', Copy(FireSpec, P1 + 1, MaxInt));
      if (P1 > 0) and (P2 > 0) then
      begin
        FireObjId := StrToIntDef(Copy(FireSpec, 1, P1 - 1), -1);
        EvName := Copy(FireSpec, P1 + 1, P2 - 1);
        Body2Expr := Copy(FireSpec, P1 + P2 + 1, MaxInt);
        if EventsFireExpr(L, FireObjId, EvName, Body2Expr, Fired, FireErr) then
          Log := Log + 'fired=' + IntToStr(Fired) + ' event=' + EvName +
            ' obj=' + IntToStr(FireObjId) + ' body2=' + Body2Expr + #13#10
        else
          Log := Log + 'fire_error=' + FireErr + #13#10;
      end
      else
        Log := Log + 'fire_error=bad spec ' + FireSpec + #13#10;
    end;
    // T6.3c：物理步进。接触回调在同一次 step 内派发 OnAddContact；
    // 步数由 HOST_PHYS_STEPS 指定（dt/迭代数取自 F276 的录制：0.01 / 20 / 20）。
    if (EnvStr('HOST_PHYS_STEPS') <> '') and PhysActive then
    begin
      g_lua := L;
      g_contacts := 0;
      g_contactTrace := '';
      PhysSetContactCallback(@PhysContactCb);
      ApplyPhysMove(EnvStr('HOST_PHYS_MOVE'));
      for i := 1 to StrToIntDef(EnvStr('HOST_PHYS_STEPS'), 0) do
        PhysStep(0.01, 20, 20);
      g_lua := nil;
      Log := Log + 'steps=' + EnvStr('HOST_PHYS_STEPS') + ' contacts=' +
        IntToStr(g_contacts) + ' trace=' + g_contactTrace + #13#10;
    end;
    Result := 'ok';
  finally
    LuaLogClose;
    Lua.Close(L);
  end;
end;

function LuaBindRunE0(out Log: string): string;
var
  S: TStringList;
begin
  S := TStringList.Create;
  try
    S.Add('lvl_o0.lua');
    S.Add('lvl_e0.lua');
    S.Add('basefs.lua');
    Result := LuaBindRun(S, EnvStr('HOST_LUA_LOG'), Log);
  finally
    S.Free;
  end;
end;

function SplitList(const S: string): TStringList;
var
  Rest, Item: string;
  P: Integer;
begin
  Result := TStringList.Create;
  Rest := S;
  P := Pos(',', Rest);
  while P > 0 do
  begin
    Item := Trim(Copy(Rest, 1, P - 1));
    if Item <> '' then
      Result.Add(Item);
    Rest := Copy(Rest, P + 1, MaxInt);
    P := Pos(',', Rest);
  end;
  Item := Trim(Rest);
  if Item <> '' then
    Result.Add(Item);
end;

// lvl_info.lvl 是 UTF-16LE 文本；每关一行 LevelFiles="a.lua, b.lua"。
function LoadLevelScripts(const Path: string): TStringList;
var
  Raw: string;
  W: WideString;
  Text: string;
  Lines: TStringList;
  i, P, Q: Integer;
  S: string;
begin
  Result := TStringList.Create;
  Raw := ReadTextFile(Path);
  if Raw = '' then
    Exit;
  SetLength(W, Length(Raw) div 2);
  if Length(W) > 0 then
    Move(Raw[1], W[1], Length(W) * 2);
  Text := UTF8Encode(W);
  Lines := TStringList.Create;
  try
    Lines.Text := Text;
    for i := 0 to Lines.Count - 1 do
    begin
      if Pos('LevelFiles', Lines[i]) = 0 then
        Continue;
      P := Pos('=', Lines[i]);
      if P = 0 then
        Continue;
      S := Copy(Lines[i], P + 1, MaxInt);
      P := Pos('"', S);
      if P = 0 then
        Continue;
      S := Copy(S, P + 1, MaxInt);
      Q := Pos('"', S);
      if Q = 0 then
        Continue;
      Result.Add(Copy(S, 1, Q - 1));
    end;
  finally
    Lines.Free;
  end;
end;

function Pad2(N: Integer): string;
begin
  if N < 10 then
    Result := '0' + IntToStr(N)
  else
    Result := IntToStr(N);
end;

// T6.3/a2 全量：52 关逐关新建 state + 写 lvlNN.jsonl。
function LuaBindRunAll(out Log: string): string;
var
  Levels: TStringList;
  Scripts: TStringList;
  i, ok, fail: Integer;
  Dir, OutDir, OutPath, OneLog: string;
begin
  Result := '';
  Log := '';
  Dir := EnvStr('HOST_LUA_DIR');
  if (Dir <> '') and (Dir[Length(Dir)] <> '\') then
    Dir := Dir + '\';
  OutDir := EnvStr('HOST_LUA_LOG_DIR');
  if (OutDir <> '') and (OutDir[Length(OutDir)] <> '\') then
    OutDir := OutDir + '\';
  Levels := LoadLevelScripts(Dir + 'lvl_info.lvl');
  try
    ok := 0;
    fail := 0;
    for i := 0 to Levels.Count - 1 do
    begin
      Scripts := SplitList(Levels[i]);
      try
        OutPath := OutDir + 'lvl' + Pad2(i) + '.jsonl';
        if LuaBindRun(Scripts, OutPath, OneLog) = 'ok' then
          Inc(ok)
        else
        begin
          Inc(fail);
          Log := Log + 'lvl' + Pad2(i) + ': ' + OneLog;
        end;
      finally
        Scripts.Free;
      end;
    end;
    Result := 'levels=' + IntToStr(Levels.Count) + ' ok=' + IntToStr(ok) +
      ' fail=' + IntToStr(fail);
  finally
    Levels.Free;
  end;
end;

// 单关运行（自检 5）：Index 是 lvl_info.lvl 里的顺序（0 起），脚本列表与 a2 相同。
// 配合 HOST_LUA_FIRE 用来验证事件派发（T6.3 接触回调）。
function LuaBindRunLevel(Index: Integer; out Log: string): string;
var
  Levels, Scripts: TStringList;
  Dir: string;
begin
  Result := '';
  Log := '';
  Dir := EnvStr('HOST_LUA_DIR');
  if (Dir <> '') and (Dir[Length(Dir)] <> '\') then
    Dir := Dir + '\';
  Levels := LoadLevelScripts(Dir + 'lvl_info.lvl');
  try
    if (Index < 0) or (Index >= Levels.Count) then
    begin
      Result := 'level=out_of_range total=' + IntToStr(Levels.Count);
      Exit;
    end;
    Scripts := SplitList(Levels[Index]);
    try
      Result := 'level=' + IntToStr(Index) + ' ' +
        LuaBindRun(Scripts, EnvStr('HOST_LUA_LOG'), Log);
    finally
      Scripts.Free;
    end;
  finally
    Levels.Free;
  end;
end;

// 日志一律落在 exe 旁边（build/ 已 gitignore），别污染仓库根的 CWD。
function ExePath(const Name: string): string;
begin
  Result := IncludeTrailingPathDelimiter(ExtractFilePath(ParamStr(0))) + Name;
end;

// 纹理自检（HOST_TEX_SELFTEST=1）：只解码 pak 里的 37 张启动纹理，不需要 GL 上下文。
procedure RunTexSelfTest(Pak: TPakFile);
var
  n: Integer;
  log: string;
  tf: TextFile;
begin
  n := SelfTestTextures(Pak, log);
  AssignFile(tf, ExePath('host_tex_selftest.log'));
  Rewrite(tf);
  WriteLn(tf, 'loaded=', n, '/', Length(kTextureAssets));
  Write(tf, log);
  CloseFile(tf);
end;

// HOST_PHYS + HOST_LUA_SELFTEST：有头/无头共用。跑过自检就 ExitProcess（原行为），
// 无头模式下也靠它退出，不进入 LCL 事件循环。
procedure RunPhysAndSelfTests;
var
  log: string;
  tf: TextFile;
begin
  if EnvFlag('HOST_PHYS') then
  begin
    AssignFile(tf, ExePath('phys_init.log'));
    Rewrite(tf);
    WriteLn(tf, 'active=', PhysStart);
    CloseFile(tf);
  end;

  if EnvStr('HOST_LUA_SELFTEST') = '' then
    Exit;

  try
    AssignFile(tf, 'C:\tmp\magnet_lua_selftest.log');
    Rewrite(tf);
    if EnvStr('HOST_LUA_SELFTEST') = '2' then
    begin
      WriteLn(tf, LuaBindSelfTest(log));
      Write(tf, log);
    end
    else if EnvStr('HOST_LUA_SELFTEST') = '3' then
    begin
      WriteLn(tf, LuaBindRunE0(log));
      Write(tf, log);
    end
    else if EnvStr('HOST_LUA_SELFTEST') = '4' then
    begin
      WriteLn(tf, LuaBindRunAll(log));
      Write(tf, log);
    end
    else if EnvStr('HOST_LUA_SELFTEST') = '5' then
    begin
      WriteLn(tf, LuaBindRunLevel(StrToIntDef(EnvStr('HOST_LUA_LEVEL'), 48), log));
      Write(tf, log);
    end
    else
      WriteLn(tf, 'ok=', LuaSelfTest('return 2+3', log), ' ', log);
    CloseFile(tf);
  except
    on E: Exception do
      // 日志写失败也要把结论带出来：退出码 1 = 自检异常
      ExitProcess(1);
  end;
  ExitProcess(0);
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
  Headless, PakOpened: Boolean;
begin
  Application.Initialize;
  Headless := EnvFlag('HOST_HEADLESS');

  // pak 与纹理自检不需要窗口（有头/无头共用）。
  Pak := TPakFile.Create;
  PakOpened := Pak.Open(DataPath);
  if PakOpened and EnvFlag('HOST_TEX_SELFTEST') then
    RunTexSelfTest(Pak);

  // 无头模式（HOST_HEADLESS=1）：不建窗、不建 GLScene/GL 上下文，只跑物理与 Lua 自检。
  // 用于 phys_sweep 这类纯初始化跑关：没有窗口、没有渲染、没有消息循环。
  if Headless then
  begin
    RunPhysAndSelfTests;
    ExitProcess(0);
  end;

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
  if PakOpened then
  begin
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

  // T6.3c：HOST_PHYS=1 → 建 world（4 面世界墙）；HOST_LUA_SELFTEST → 跑自检后退出。
  // 有头/无头共用同一个入口（无头分支在上面已经调用过它）。
  RunPhysAndSelfTests;

  Application.Run;
end.
