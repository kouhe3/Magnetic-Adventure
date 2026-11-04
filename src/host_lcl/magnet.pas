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
  PhysWorld, LevelScene, ProfileData, ExtCtrls;

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
  g_levelLua: TLuaState = nil;  // T6.4d-4：HOST_KEEP_LUA=1 时保留的关卡 state
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
// F359：retail 的四个 graph root 是图对象；宿主原先让它们是 nil，Add_* 的
// parent 实参丢失层信息。固定 id：1=front、2=medium、3=hints、4=back。
procedure DefineLuaRoots(L: TLuaState);
const
  kRoots: array[0..3] of PChar = ('grFrontRoot', 'grMediumRoot',
                                  'grHintsRoot', 'grBackRoot');
var
  i: Integer;
begin
  for i := 0 to 3 do
  begin
    Lua.PushInteger(L, i + 1);
    // Lua 5.1 的 lua_setglobal 是宏，不是导出；用 lua_setfield(GLOBALSINDEX)。
    Lua.SetField(L, LUA_GLOBALSINDEX, kRoots[i]);
  end;
end;

function LuaBindRun(Scripts: TStrings; const LogPath: string; out Log: string): string;
const
  kEntries: array[0..2] of string = ('BaseFsBeforeCreate', 'Create', 'AttachScripts');
var
  L: TLuaState;
  Rc, i: Integer;
  Dir, Path, Content: string;
  RandPath, RandChunk: string;
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
    // 随机序列回放（只用于对拍带 math.random 的关卡）：HOST_LUA_RANDOM 指向逗号分隔的
    // 返回值列表；每次 math.random(...) 按顺序返回下一个值，耗尽后回落真实 RNG。
    RandPath := EnvStr('HOST_LUA_RANDOM');
    if RandPath <> '' then
    begin
      RandChunk := ReadTextFile(RandPath);
      if RandChunk <> '' then
      begin
        Rc := Lua.LoadString(L, PChar(
          'local seq={' + RandChunk + '}; local i=1; local real=math.random; ' +
          'math.random=function(...) if i<=#seq then local v=seq[i]; i=i+1; return v end; ' +
          'return real(...) end'));
        if Rc = 0 then
          Rc := Lua.PCall(L, 0, 0, 0);
        if Rc <> 0 then
          Lua.SetTop(L, 0);
      end;
    end;
    ResetIds;
    EventsReset;
    PhysResetObjects;
    RegisterBindings(L);
    DefineLuaRoots(L);
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
    if EnvFlag('HOST_KEEP_LUA') then
      g_levelLua := L
    else
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
  CrashLogDll: HMODULE;
  // T6.4d-1：宿主状态机切片的状态（只读，env 未设时零行为）。
  g_profile: TProfileInfo;
  g_profileRead: Boolean = False;
  g_tracePath: string = '';
  g_t0: DWORD = 0;
  g_Menu: TMenuScene = nil;
  g_Level: TLevelScene = nil;
  g_Scene: TGLScene = nil;
  g_Cam: TGLCamera = nil;
  g_Pak: TPakFile = nil;
  g_Viewer: TGLSceneViewer = nil;
  g_InLevel: Boolean = False;

// 崩溃捕获（F315–F317）：设 CRASHLOG_DIR/CRASHLOG_LOG 时加载 crashlog.dll，它在 DllMain 里装 VEH。
// 默认零成本；代理（HOST_PHYS）路径也会带同一份记录器，二者用进程级互斥量只装一个。
procedure MaybeLoadCrashLog;
var
  dir: array[0..MAX_PATH - 1] of Char;
begin
  if (GetEnvironmentVariable('CRASHLOG_DIR', @dir[0], SizeOf(dir)) > 0) or
     (GetEnvironmentVariable('CRASHLOG_LOG', @dir[0], SizeOf(dir)) > 0) then
    CrashLogDll := LoadLibrary('crashlog.dll');
end;

// T6.4c-1：HOST_PROFILE=<path> 时只读解析玩家档案（F434）。
// 日志固定写 exe 旁的 profile.log；未设 env 时不读、不写（旧行为）。
procedure MaybeReadProfile;
var
  path: string;
  tf: TextFile;
begin
  g_profileRead := False;
  path := EnvStr('HOST_PROFILE');
  if path = '' then Exit;
  g_profileRead := ReadProfileFile(path, g_profile);
  AssignFile(tf, ExePath('profile.log'));
  Rewrite(tf);
  if g_profile.Ok then
    WriteLn(tf, 'ok=1 players=', g_profile.Players, ' user=', g_profile.UserName,
      ' level=', g_profile.LastCompleteLevel, ' completed=', g_profile.CompletedLevels,
      ' sounds=', g_profile.SoundsVolume, ' music=', g_profile.MusicVolume,
      ' fullscreen=', g_profile.FullScreen)
  else
    WriteLn(tf, 'ok=0 players=', g_profile.Players, ' err=', g_profile.Error);
  CloseFile(tf);
end;

// T6.4d-1：状态轨迹（JSONL，字段与 tools/direct_drive.py --trace 同构）。
// 只有 HOST_TRACE 非空时写；每次追加一行。
procedure WriteTraceLine(const Line: string);
var
  tf: TextFile;
begin
  if g_tracePath = '' then Exit;
  AssignFile(tf, g_tracePath);
  if FileExists(g_tracePath) then
    Append(tf)
  else
    Rewrite(tf);
  WriteLn(tf, Line);
  CloseFile(tf);
end;

procedure WriteTrace(const State: string);
begin
  WriteTraceLine('{"t_ms": ' + IntToStr(Integer(GetTickCount - g_t0)) +
    ', "state": "' + State + '"}');
end;

procedure WriteTraceIndex(const State: string; Index: Integer);
begin
  WriteTraceLine('{"t_ms": ' + IntToStr(Integer(GetTickCount - g_t0)) +
    ', "state": "' + State + '", "index": ' + IntToStr(Index) + '}');
end;

// HOST_CLICK=<design_x>,<design_y>：设计像素（左上原点），与 menuscene 的矩形同一空间。
function ParseClickSpec(out X, Y: Integer): Boolean;
var
  s: string;
  p: Integer;
begin
  Result := False;
  X := -1;
  Y := -1;
  s := EnvStr('HOST_CLICK');
  if s = '' then Exit;
  p := Pos(',', s);
  if p = 0 then Exit;
  X := StrToIntDef(Trim(Copy(s, 1, p - 1)), -1);
  Y := StrToIntDef(Trim(Copy(s, p + 1, MaxInt)), -1);
  Result := (X >= 0) and (Y >= 0);
end;

// menuscene.pas:Build 里 play_1/play_2 的矩形（223,224,256,128）。
function HitPlay(X, Y: Integer): Boolean;
begin
  Result := (X >= 223) and (X < 223 + 256) and
    (Y >= 224) and (Y < 224 + 128);
end;

type
  TStepForce = record
    Step, Id: Integer;
    Fx, Fy, Px, Py: Double;
    HasPoint: Boolean;
  end;

  TStepTorque = record
    Step, Id: Integer;
    T: Double;
  end;

  TCursorPt = record
    Step: Integer;
    Cx, Cy: Double;
  end;

  THostLoop = class
    procedure Tick(Sender: TObject);
  end;

  THostMouseHandler = class
    procedure MouseDown(Sender: TObject; Button: TMouseButton;
      Shift: TShiftState; X, Y: Integer);
  end;

var
  g_Loop: THostLoop = nil;
  g_LoopTimer: TTimer = nil;
  g_LoopSteps, g_LoopCalls, g_LoopStartMs, g_LoopMs: Integer;
  g_LoopScrCalls, g_LoopScrMoved: Integer;
  g_LoopMoveCalls: Integer;
  g_LoopSpawnCalls, g_LoopSpawnCreated: Integer;
  g_MagOn: Boolean = False;
  // T6.4b-3b：真实鼠标磁铁（GetCursorPos/GetAsyncKeyState 轮询）。
  g_MagReal: Boolean = False;
  g_MagRealDown: Boolean = False;
  g_MagRealCalls: Integer = 0;
  // T6.4b-4c：原版全局角阻尼系数（每步 -Coeff*w）。
  g_DampCoeff: Double = 0.0;
  // T6.4b-4e：F454 模型的抓取点（body-local）与线性阻尼系数。
  g_MagLocalX: Double = 0.0;
  g_MagLocalY: Double = 0.0;
  g_LinDamp: Double = 0.0;
  g_MagX, g_MagY, g_MagLastX, g_MagLastY: Double;
  g_MagTargetId: Integer = 0;
  g_LevelIndex: Integer = -1;
  g_LuaProgressOn: Boolean = False;

procedure EnterStage(const S: string);
var
  f: TextFile;
begin
  if EnvStr('HOST_ENTER_LOG') = '' then Exit;
  AssignFile(f, EnvStr('HOST_ENTER_LOG'));
  if FileExists(EnvStr('HOST_ENTER_LOG')) then Append(f) else Rewrite(f);
  WriteLn(f, S);
  CloseFile(f);
end;

// T6.4b-3b：真实鼠标磁铁的事件日志（down/up/down-miss）。
procedure MagRealLog(const S: string);
var
  f: TextFile;
  p: string;
begin
  p := ExePath('mag_real.log');
  AssignFile(f, p);
  if FileExists(p) then Append(f) else Rewrite(f);
  WriteLn(f, S);
  CloseFile(f);
end;

procedure ExitLevel; forward;

// T6.4b-2b-0：Lua Get_ScrObjPos 对无物理体的 graph 对象回退到这里。
function LookupSpritePos(Id: Integer; out X, Y, Angle: Double): Boolean;
begin
  Result := False;
  X := 0;
  Y := 0;
  Angle := 0;
  if g_Level <> nil then
    Result := g_Level.GetSpritePos(Id, X, Y, Angle);
end;

// T6.4f：提示按钮 hitbox（F307 实测命中 (980,650)）与 DoShowHint 派发。
function HintHitTest(X, Y: Integer): Boolean;
begin
  Result := (X >= 950) and (X <= 1010) and (Y >= 620) and (Y <= 690);
end;

procedure DoShowHintNow;
var
  f: TextFile;
  p: string;
begin
  HintShown := True;
  if g_levelLua <> nil then
  begin
    Lua.GetField(g_levelLua, LUA_GLOBALSINDEX, PChar('DoShowHint'));
    if Lua.LType(g_levelLua, -1) = 6 then
    begin
      Lua.PCall(g_levelLua, 0, 0, 0);
      Lua.SetTop(g_levelLua, 0);
    end;
  end;
  p := ExePath('hint.log');
  AssignFile(f, p);
  if FileExists(p) then Append(f) else Rewrite(f);
  WriteLn(f, 'shown=1');
  CloseFile(f);
end;

procedure HintClickFromEnv;
var
  s: string;
  p, x, y: Integer;
  f: TextFile;
  fp: string;
begin
  s := EnvStr('HOST_HINT_CLICK');
  if s = '' then Exit;
  p := Pos(',', s);
  if p = 0 then Exit;
  x := StrToIntDef(Copy(s, 1, p - 1), 0);
  y := StrToIntDef(Copy(s, p + 1, Length(s)), 0);
  fp := ExePath('hint.log');
  AssignFile(f, fp);
  Rewrite(f);
  if HintVisible and HintHitTest(x, y) then
    WriteLn(f, 'hit=1')
  else
    WriteLn(f, 'hit=0');
  CloseFile(f);
  if HintVisible and HintHitTest(x, y) then
    DoShowHintNow;
end;

// T6.4d-2：运行时切到关卡（真实 LCL 点击路径）。菜单 sprite 先清掉，
// Cam 保留；关卡模型来自 LuaBindRunLevel 刚写的 HOST_LUA_LOG。
procedure EnterLevel(Index: Integer; out Err: string);
var
  runLog, rc: string;
  BuildOk: Boolean;
  i, Steps, SyncCount, TargetId: Integer;
  ProgressCalls, ProgressRc, rc2: Integer;
  StepsStr: string;
  SyncFirst, SyncAfter: Double;
  MagX, MagY, MagDX, MagDY, MagD, MagF, MagMoved, MagIX, MagIY, MagIA: Double;
  MagOn: Boolean;
  tf, ptf, ptf2, mtf, stepLog: TextFile;
  stepOn: Boolean;
  MagUntil: Integer;
  Forces: array of TStepForce;
  ForceCount, ForceIdx, fi, fcode: Integer;
  forceFile: TextFile;
  fline, ftok: string;
  Torques: array of TStepTorque;
  TorqueCount, TorqueIdx, ti, tcode: Integer;
  torqueFile: TextFile;
  tline, ttok: string;
  Cursors: array of TCursorPt;
  CursorCount, CursorIdx, ci, ccode: Integer;
  cursorFile: TextFile;
  cline, ctok: string;
  SelfMode: Boolean;
  LocalX, LocalY, LinDamp: Double;
  MagPX, MagPY: Double;
begin
  Err := '';
  if g_InLevel then Exit;
  runLog := '';
  // T6.4d-3：先建 b2 world（4 面世界墙），LuaBindRunLevel 的工厂再往里建关卡体。
  if EnvFlag('HOST_PHYS') and not PhysActive then
    if not PhysStart then
    begin
      Err := 'PhysStart failed';
      Exit;
    end;
  // T6.4d-4：LuaBindRun 自带的 HOST_PHYS_STEPS 步进是自检用；EnterLevel 在外面
  // 统一步进，调用期间临时清空，避免内外层各走一遍（T6.4d-3 的 100 步实际走了 200）。
  Steps := StrToIntDef(EnvStr('HOST_PHYS_STEPS'), 0);
  StepsStr := EnvStr('HOST_PHYS_STEPS');
  if Steps > 0 then
    SetEnvironmentVariable('HOST_PHYS_STEPS', nil);
  rc := LuaBindRunLevel(Index, runLog);
  if Steps > 0 then
    SetEnvironmentVariable('HOST_PHYS_STEPS', PChar(StepsStr));
  EnterStage('stage=lua rc=' + rc + ' menu_nil=' + BoolToStr(g_Menu = nil, True));
  if rc <> 'level=' + IntToStr(Index) + ' ok' then
  begin
    Err := runLog + ' rc=' + rc;
    Exit;
  end;
  if (g_Menu <> nil) and not EnvFlag('HOST_NO_MENU_CLEAR') then
  begin
    EnterStage('stage=pre_clear');
    g_Menu.Clear;
    EnterStage('stage=post_clear');
    g_Menu.Free;
    g_Menu := nil;
    EnterStage('stage=post_free');
  end;
  g_Level := TLevelScene.Create(g_Scene, g_Pak, g_Cam);
  ScrPosLookup := @LookupSpritePos;
  EnterStage('stage=pre_build');
  // 运行时 GL 上下文在消息循环里不是 current；纹理创建/上传要先激活，
  // 否则 TGLTexture.Image 赋值失败、AddHud/AddWorld 直接 Exit（启动分支
  // 没有这个问题：那时上下文还没创建，上传被延迟到首帧）。
  if (g_Viewer <> nil) and g_Viewer.Buffer.RenderingContext.IsValid then
    g_Viewer.Buffer.RenderingContext.Activate;
  BuildOk := False;
  try
    BuildOk := g_Level.BuildFromModel(EnvStr('HOST_LUA_LOG'), EnvStr('HOST_PAK_DIR'),
      StrToFloatDef(EnvStr('HOST_LEVEL_TIME'), 0.0));
    if EnvStr('HOST_HINT_VISUAL') <> '' then
      if not g_Level.BuildHintVisual(EnvStr('HOST_HINT_CELLS'),
        StrToFloatDef(EnvStr('HOST_LEVEL_TIME'), 0.0)) then
        WriteLn('hint_visual failed: ', g_Level.Log);
  finally
    if (g_Viewer <> nil) and g_Viewer.Buffer.RenderingContext.IsValid then
      g_Viewer.Buffer.RenderingContext.Deactivate;
  end;
  EnterStage('stage=post_build ok=' + BoolToStr(BuildOk, True) +
    ' sprites=' + IntToStr(g_Level.Sprites));
  // 已知缺失素材（level 20 的 symbol_back）会让 BuildFromModel 返回 False，
  // 但已建出的 sprite 是有效的；与启动分支的判据一致：sprites>0 就算进关。
  if g_Level.Sprites = 0 then
  begin
    EnterStage('level_log=' + g_Level.Log);
    Err := 'model produced 0 sprites: ' + EnvStr('HOST_LUA_LOG');
    Exit;
  end;
  AssignFile(tf, ExePath('level_init.log'));
  Rewrite(tf);
  WriteLn(tf, 'sprites=', g_Level.Sprites);
  Write(tf, g_Level.Log);
  CloseFile(tf);
  // 初始化阶段的 Set_ScrObjPos 已由 SceneModel 回放到 JSONL；清空队列，
  // 让 loop 里的 scrpos_calls 只统计运行期 DoProgress 的调用。
  ScrPosReset;
  SpawnReset;  // 清初始化阶段的 Spawn（运行时生成的才在 Tick 里消费）
  // T6.4b-2a：帧循环的磁铁 target 与 OnMove 派发用全局状态。
  g_MagOn := EnvFlag('HOST_MAG_BUTTON');
  g_MagX := StrToFloatDef(EnvStr('HOST_MAG_X'), 0.0);
  g_MagY := StrToFloatDef(EnvStr('HOST_MAG_Y'), 0.0);
  g_MagTargetId := 0;
  g_MagReal := EnvFlag('HOST_MAG_REAL');
  g_MagRealDown := False;
  g_MagRealCalls := 0;
  g_DampCoeff := StrToFloatDef(EnvStr('HOST_MAG_DAMPING'), 0.0);
  // T6.4b-4d：自驱磁铁模型（F454）——力律、body-local 抓取点、两类阻尼。
  SelfMode := EnvFlag('HOST_MAG_SELF');
  LocalX := StrToFloatDef(EnvStr('HOST_MAG_LOCALX'), 0.0);
  LocalY := StrToFloatDef(EnvStr('HOST_MAG_LOCALY'), 0.0);
  LinDamp := StrToFloatDef(EnvStr('HOST_MAG_LINDAMP'), 0.0);
  g_MagLocalX := LocalX;
  g_MagLocalY := LocalY;
  g_LinDamp := LinDamp;
  if g_MagReal then
    g_MagOn := False;
  if g_MagOn and g_Level.NearestBody(g_MagX, g_MagY, g_MagTargetId, MagD) then
    PhysGetBodyPos(g_MagTargetId, g_MagLastX, g_MagLastY, MagIA);
  g_LevelIndex := Index;
  g_InLevel := True;
  WriteTraceIndex('level', Index);
  HintClickFromEnv;
  if g_Viewer <> nil then
    g_Viewer.Invalidate;
  // T6.4d-3：HOST_PHYS_STEPS>0 时步进并把 world sprite 同步到物理体。
  // 第一次 SyncPhysics 记录"同步前 sprite 与 body 的位置差"（即物理位移），
  // 第二次记录同步后残差（应为 0），用于判据 sync_after。
  if EnvFlag('HOST_PHYS') and (Steps > 0) then
  begin
    ProgressCalls := 0;
    ProgressRc := 0;
    // T6.4b-1：磁铁 target 在第一步锁定，之后每步按 min(315,30d) 朝鼠标施力。
    MagOn := EnvFlag('HOST_MAG_BUTTON');
    if g_MagReal then
      MagOn := False;
    TargetId := 0;
    MagMoved := 0;
    MagX := StrToFloatDef(EnvStr('HOST_MAG_X'), 0.0);
    MagY := StrToFloatDef(EnvStr('HOST_MAG_Y'), 0.0);
    MagUntil := StrToIntDef(EnvStr('HOST_MAG_UNTIL'), 0);
    stepOn := EnvStr('HOST_STEP_LOG') <> '';
    if stepOn then
    begin
      AssignFile(stepLog, EnvStr('HOST_STEP_LOG'));
      Rewrite(stepLog);
    end;
    // T6.4b-4：逐 step 精确力回放（原版 ApplyForce 时间线，含阻尼力）。
    ForceCount := 0;
    ForceIdx := 0;
    if EnvStr('HOST_MAG_FORCE') <> '' then
    begin
      AssignFile(forceFile, EnvStr('HOST_MAG_FORCE'));
      Reset(forceFile);
      while not Eof(forceFile) do
      begin
        ReadLn(forceFile, fline);
        SetLength(Forces, ForceCount + 1);
        with Forces[ForceCount] do
        begin
          Step := 0; Id := 0; Fx := 0; Fy := 0;
          Px := 0; Py := 0; HasPoint := False;
          fi := 1;
          while (fi <= Length(fline)) and (fline[fi] = ' ') do Inc(fi);
          ftok := '';
          while (fi <= Length(fline)) and (fline[fi] <> ' ') do
          begin ftok := ftok + fline[fi]; Inc(fi); end;
          Val(ftok, Step, fcode);
          while (fi <= Length(fline)) and (fline[fi] = ' ') do Inc(fi);
          ftok := '';
          while (fi <= Length(fline)) and (fline[fi] <> ' ') do
          begin ftok := ftok + fline[fi]; Inc(fi); end;
          Val(ftok, Id, fcode);
          while (fi <= Length(fline)) and (fline[fi] = ' ') do Inc(fi);
          ftok := '';
          while (fi <= Length(fline)) and (fline[fi] <> ' ') do
          begin ftok := ftok + fline[fi]; Inc(fi); end;
          Val(ftok, Fx, fcode);
          while (fi <= Length(fline)) and (fline[fi] = ' ') do Inc(fi);
          ftok := '';
          while (fi <= Length(fline)) and (fline[fi] <> ' ') do
          begin ftok := ftok + fline[fi]; Inc(fi); end;
          Val(ftok, Fy, fcode);
          // T6.4b-4b：可选的第 5/6 列是原版施力点；缺省按 body 中心。
          while (fi <= Length(fline)) and (fline[fi] = ' ') do Inc(fi);
          if fi <= Length(fline) then
          begin
            ftok := '';
            while (fi <= Length(fline)) and (fline[fi] <> ' ') do
            begin ftok := ftok + fline[fi]; Inc(fi); end;
            Val(ftok, Px, fcode);
            while (fi <= Length(fline)) and (fline[fi] = ' ') do Inc(fi);
            if fi <= Length(fline) then
            begin
              ftok := '';
              while (fi <= Length(fline)) and (fline[fi] <> ' ') do
              begin ftok := ftok + fline[fi]; Inc(fi); end;
              Val(ftok, Py, fcode);
              HasPoint := True;
            end;
          end;
        end;
        Inc(ForceCount);
      end;
      CloseFile(forceFile);
    end;
    // 同一步还有 ApplyTorque（螺丝旋转），单独一份时间线。
    TorqueCount := 0;
    TorqueIdx := 0;
    if EnvStr('HOST_MAG_TORQUE') <> '' then
    begin
      AssignFile(torqueFile, EnvStr('HOST_MAG_TORQUE'));
      Reset(torqueFile);
      while not Eof(torqueFile) do
      begin
        ReadLn(torqueFile, tline);
        SetLength(Torques, TorqueCount + 1);
        with Torques[TorqueCount] do
        begin
          Step := 0; Id := 0; T := 0;
          ti := 1;
          while (ti <= Length(tline)) and (tline[ti] = ' ') do Inc(ti);
          ttok := '';
          while (ti <= Length(tline)) and (tline[ti] <> ' ') do
          begin ttok := ttok + tline[ti]; Inc(ti); end;
          Val(ttok, Step, tcode);
          while (ti <= Length(tline)) and (tline[ti] = ' ') do Inc(ti);
          ttok := '';
          while (ti <= Length(tline)) and (tline[ti] <> ' ') do
          begin ttok := ttok + tline[ti]; Inc(ti); end;
          Val(ttok, Id, tcode);
          while (ti <= Length(tline)) and (tline[ti] = ' ') do Inc(ti);
          ttok := '';
          while (ti <= Length(tline)) and (tline[ti] <> ' ') do
          begin ttok := ttok + tline[ti]; Inc(ti); end;
          Val(ttok, T, tcode);
        end;
        Inc(TorqueCount);
      end;
      CloseFile(torqueFile);
    end;
    // T6.4b-4d：自驱模式只用逐步光标时间线，力/点/阻尼由宿主按 F454 计算。
    CursorCount := 0;
    CursorIdx := 0;
    if SelfMode and (EnvStr('HOST_MAG_CURSOR') <> '') then
    begin
      AssignFile(cursorFile, EnvStr('HOST_MAG_CURSOR'));
      Reset(cursorFile);
      while not Eof(cursorFile) do
      begin
        ReadLn(cursorFile, cline);
        SetLength(Cursors, CursorCount + 1);
        with Cursors[CursorCount] do
        begin
          Step := 0; Cx := 0; Cy := 0;
          ci := 1;
          while (ci <= Length(cline)) and (cline[ci] = ' ') do Inc(ci);
          ctok := '';
          while (ci <= Length(cline)) and (cline[ci] <> ' ') do
          begin ctok := ctok + cline[ci]; Inc(ci); end;
          Val(ctok, Step, ccode);
          while (ci <= Length(cline)) and (cline[ci] = ' ') do Inc(ci);
          ctok := '';
          while (ci <= Length(cline)) and (cline[ci] <> ' ') do
          begin ctok := ctok + cline[ci]; Inc(ci); end;
          Val(ctok, Cx, ccode);
          while (ci <= Length(cline)) and (cline[ci] = ' ') do Inc(ci);
          ctok := '';
          while (ci <= Length(cline)) and (cline[ci] <> ' ') do
          begin ctok := ctok + cline[ci]; Inc(ci); end;
          Val(ctok, Cy, ccode);
        end;
        Inc(CursorCount);
      end;
      CloseFile(cursorFile);
    end;
    // T6.4b-4：原版是“按在螺丝上锁定 target，再把光标移到目标”，
    // 所以 target 与施力点分开：HOST_MAG_TARGET 是锁定体，HOST_MAG_X/Y 是光标。
    if EnvStr('HOST_MAG_TARGET') <> '' then
    begin
      TargetId := StrToIntDef(EnvStr('HOST_MAG_TARGET'), 0);
      if (TargetId = 0) or (PhysBodyOf(TargetId) = nil) then
        TargetId := 0
      else
        PhysGetBodyPos(TargetId, MagIX, MagIY, MagIA);
    end
    else if MagOn and g_Level.NearestBody(MagX, MagY, TargetId, MagD) then
      PhysGetBodyPos(TargetId, MagIX, MagIY, MagIA);
    for i := 1 to Steps do
    begin
      if SelfMode then
      begin
        while (CursorIdx < CursorCount) and (Cursors[CursorIdx].Step <= i) do
        begin
          if (Cursors[CursorIdx].Step = i) and (TargetId <> 0) then
          begin
            PhysGetBodyPos(TargetId, MagIX, MagIY, MagIA);
            MagDX := Cursors[CursorIdx].Cx - MagIX;
            MagDY := Cursors[CursorIdx].Cy - MagIY;
            MagD := Sqrt(MagDX * MagDX + MagDY * MagDY);
            if MagD > 1e-6 then
            begin
              MagF := 30.0 * MagD;
              if MagF > 315.0 then MagF := 315.0;
              MagPX := MagIX + Cos(MagIA) * LocalX - Sin(MagIA) * LocalY;
              MagPY := MagIY + Sin(MagIA) * LocalX + Cos(MagIA) * LocalY;
              PhysApplyForceAt(TargetId, MagF * MagDX / MagD,
                MagF * MagDY / MagD, MagPX, MagPY);
            end;
          end;
          Inc(CursorIdx);
        end;
      end
      else if ForceCount > 0 then
      begin
        while (ForceIdx < ForceCount) and (Forces[ForceIdx].Step <= i) do
        begin
          if Forces[ForceIdx].Step = i then
          begin
            if Forces[ForceIdx].HasPoint then
              PhysApplyForceAt(Forces[ForceIdx].Id, Forces[ForceIdx].Fx,
                Forces[ForceIdx].Fy, Forces[ForceIdx].Px, Forces[ForceIdx].Py)
            else
              PhysApplyForce(Forces[ForceIdx].Id, Forces[ForceIdx].Fx,
                Forces[ForceIdx].Fy);
          end;
          Inc(ForceIdx);
        end;
      end
      else if (TargetId <> 0) and MagOn and ((MagUntil = 0) or (i <= MagUntil)) then
      begin
        PhysGetBodyPos(TargetId, MagDX, MagDY, MagIA);
        MagDX := MagX - MagDX;
        MagDY := MagY - MagDY;
        MagD := Sqrt(MagDX * MagDX + MagDY * MagDY);
        if MagD > 1e-6 then
        begin
          MagF := 30.0 * MagD;
          if MagF > 315.0 then MagF := 315.0;
          PhysApplyForce(TargetId, MagF * MagDX / MagD, MagF * MagDY / MagD);
        end;
      end;
      while (TorqueIdx < TorqueCount) and (Torques[TorqueIdx].Step <= i) do
      begin
        if Torques[TorqueIdx].Step = i then
          PhysApplyTorque(Torques[TorqueIdx].Id, Torques[TorqueIdx].T);
        Inc(TorqueIdx);
      end;
      // T6.4b-4c：原版每步对全部动态体施加 -30*w（F451）；与扭矩时间线二选一。
      if LinDamp > 0 then
        PhysApplyLinearDamping(LinDamp);
      if g_DampCoeff > 0 then
        PhysApplyAngularDamping(g_DampCoeff);
      PhysStep(0.01, 20, 20);
      if stepOn then
        g_Level.WriteStepDigest(i, stepLog);
      // T6.4d-4：关卡运行期保留的 Lua state 里每步调 DoProgress(dt)。
      if EnvFlag('HOST_LUA_PROGRESS') and (g_levelLua <> nil) then
      begin
        Lua.GetField(g_levelLua, LUA_GLOBALSINDEX, PChar('DoProgress'));
        if Lua.LType(g_levelLua, -1) = 6 then
        begin
          Lua.PushNumber(g_levelLua, 0.01);
          rc2 := Lua.PCall(g_levelLua, 1, 0, 0);
          if rc2 <> 0 then Inc(ProgressRc);
          Inc(ProgressCalls);
        end;
        Lua.SetTop(g_levelLua, 0);
      end;
    end;
    if stepOn then
      CloseFile(stepLog);
    if EnvFlag('HOST_LUA_PROGRESS') then
    begin
      AssignFile(ptf2, ExePath('lua_progress.log'));
      Rewrite(ptf2);
      WriteLn(ptf2, 'calls=', ProgressCalls, ' rc=', ProgressRc);
      CloseFile(ptf2);
    end;
    if TargetId <> 0 then
    begin
      PhysGetBodyPos(TargetId, MagDX, MagDY, MagIA);
      MagMoved := Sqrt((MagDX - MagIX) * (MagDX - MagIX) +
        (MagDY - MagIY) * (MagDY - MagIY));
    end;
    AssignFile(mtf, ExePath('mag.log'));
    Rewrite(mtf);
    WriteLn(mtf, 'target=', TargetId, ' moved=', FormatFloat('0.000000', MagMoved));
    CloseFile(mtf);
    SyncCount := g_Level.SyncPhysics;
    SyncFirst := g_Level.SyncMaxErr;
    g_Level.SyncPhysics;
    SyncAfter := g_Level.SyncMaxErr;
    AssignFile(ptf, ExePath('phys.log'));
    Rewrite(ptf);
    WriteLn(ptf, 'bodies=', SyncCount, ' objects=', g_Level.SyncObjects,
      ' steps=', Steps, ' angle_moved=', g_Level.SyncAngleMoved,
      ' sync_first=', FormatFloat('0.000000000', SyncFirst),
      ' sync_after=', FormatFloat('0.000000000', SyncAfter));
    CloseFile(ptf);
    EnterStage('stage=phys bodies=' + IntToStr(SyncCount) +
      ' angle_moved=' + IntToStr(g_Level.SyncAngleMoved));
    // T6.4d-5：注入 Do_LevelComplete()（Lua 全局存在则调用；无论是否存在都置标志），
    // 然后走 menu→level→menu 的状态切换。
    if EnvFlag('HOST_FIRE_COMPLETE') then
    begin
      if g_levelLua <> nil then
      begin
        Lua.GetField(g_levelLua, LUA_GLOBALSINDEX, PChar('Do_LevelComplete'));
        if Lua.LType(g_levelLua, -1) = 6 then
        begin
          rc2 := Lua.PCall(g_levelLua, 0, 0, 0);
          EnterStage('stage=fire_complete rc=' + IntToStr(rc2));
        end;
        Lua.SetTop(g_levelLua, 0);
      end;
      LevelComplete := True;
    end;
    if LevelComplete then
    begin
      if EnvFlag('HOST_SAVE_PROFILE') and (EnvStr('HOST_PROFILE') <> '') then
      begin
        if WriteLastCompleteLevel(EnvStr('HOST_PROFILE'), Index + 1) then
          EnterStage('stage=save_profile level=' + IntToStr(Index + 1))
        else
          EnterStage('stage=save_profile failed');
      end;
      ExitLevel;
    end;
  end;
  // T6.4d-6：持续帧循环（16 ms TTimer）；HOST_LOOP_MS 到时写 loop.log。
  if EnvFlag('HOST_LOOP') then
  begin
    g_LoopMs := StrToIntDef(EnvStr('HOST_LOOP_MS'), 2000);
    g_LoopStartMs := Integer(GetTickCount);
    g_LoopSteps := 0;
    g_LoopCalls := 0;
    g_LoopScrCalls := 0;
    g_LoopScrMoved := 0;
    g_LoopMoveCalls := 0;
    g_LoopSpawnCalls := 0;
    g_LoopSpawnCreated := 0;
    g_LuaProgressOn := EnvFlag('HOST_LUA_PROGRESS');
    if g_Loop = nil then
      g_Loop := THostLoop.Create;
    if g_LoopTimer = nil then
    begin
      g_LoopTimer := TTimer.Create(nil);
      g_LoopTimer.Interval := 16;
      g_LoopTimer.OnTimer := @g_Loop.Tick;
    end;
    g_LoopTimer.Enabled := True;
  end;
end;

// T6.4d-5：清关卡 sprite、重建菜单、写 trace menu；HOST_EXIT_AFTER_COMPLETE 供测试退出。
procedure ExitLevel;
var
  menuOk: Boolean;
  tf: TextFile;
begin
  if g_Level <> nil then
  begin
    g_Level.Clear;
    g_Level.Free;
    g_Level := nil;
  end;
  if g_Menu = nil then
  begin
    g_Menu := TMenuScene.Create(g_Scene, g_Pak);
    if (g_Viewer <> nil) and g_Viewer.Buffer.RenderingContext.IsValid then
      g_Viewer.Buffer.RenderingContext.Activate;
    try
      menuOk := g_Menu.Build(True, 900, 700);
    finally
      if (g_Viewer <> nil) and g_Viewer.Buffer.RenderingContext.IsValid then
        g_Viewer.Buffer.RenderingContext.Deactivate;
    end;
    if menuOk then
      WriteLn(StdErr, 'menu rebuilt')
    else
      WriteLn(StdErr, 'menu rebuild failed');
    AssignFile(tf, ExePath('menu_after.log'));
    Rewrite(tf);
    WriteLn(tf, 'layers=', g_Menu.Layers);
    CloseFile(tf);
  end;
  g_InLevel := False;
  WriteTrace('menu');
  if g_Viewer <> nil then
    g_Viewer.Invalidate;
  if EnvFlag('HOST_EXIT_AFTER_COMPLETE') then
  begin
    WriteTrace('exit');
    ExitProcess(0);
  end;
end;

// 客户区坐标 = 设计像素（客户区 1018×739，F154/F188）。
procedure THostMouseHandler.MouseDown(Sender: TObject; Button: TMouseButton;
  Shift: TShiftState; X, Y: Integer);
var
  err: string;
  ctf: TextFile;
begin
  if EnvStr('HOST_CLICK_LOG') <> '' then
  begin
    AssignFile(ctf, EnvStr('HOST_CLICK_LOG'));
    if FileExists(EnvStr('HOST_CLICK_LOG')) then Append(ctf) else Rewrite(ctf);
    if g_Viewer <> nil then
      WriteLn(ctf, 'x=', X, ' y=', Y, ' cw=', g_Viewer.ClientWidth,
        ' ch=', g_Viewer.ClientHeight)
    else
      WriteLn(ctf, 'x=', X, ' y=', Y, ' viewer=nil');
    CloseFile(ctf);
  end;
  if Button <> mbLeft then Exit;
  if g_InLevel then
  begin
    if HintVisible and HintHitTest(X, Y) then
      DoShowHintNow;
    Exit;
  end;
  if not HitPlay(X, Y) then Exit;
  if not g_profile.Ok then Exit;
  if (g_profile.LastCompleteLevel < 0) or
     (g_profile.LastCompleteLevel >= 51) then Exit;
  EnterLevel(g_profile.LastCompleteLevel, err);
  if err <> '' then
    WriteLn(StdErr, 'enter level failed: ', err);
  if g_InLevel and EnvFlag('HOST_EXIT_AFTER_LEVEL') then
  begin
    WriteTrace('exit');
    ExitProcess(0);
  end;
end;


procedure THostLoop.Tick(Sender: TObject);
var
  rc2: Integer;
  tf: TextFile;
  elapsed: Integer;
  n, pid, moveCalls, sid, skind, sstyle: Integer;
  px, py, pa, dx, dy, d, f, sx, sy, sa: Double;
  pt: TPoint;
  down, hasPos: Boolean;
  wx, wy: Double;
begin
  if (not g_InLevel) or (g_Level = nil) then Exit;
  if EnvStr('HOST_SCRPOS_GET') <> '' then
  begin
    pid := StrToIntDef(EnvStr('HOST_SCRPOS_GET'), 0);
    hasPos := False;
    if PhysBodyOf(pid) <> nil then
    begin
      PhysGetBodyPos(pid, px, py, pa);
      hasPos := True;
    end
    else if g_Level.GetSpritePos(pid, px, py, pa) then
      hasPos := True;
    if hasPos then
    begin
      AssignFile(tf, ExePath('scrpos_get.log'));
      Rewrite(tf);
      WriteLn(tf, 'id=', pid, ' x=', FormatFloat('0.000000', px),
        ' y=', FormatFloat('0.000000', py), ' a=', FormatFloat('0.000000', pa));
      CloseFile(tf);
    end;
  end;
  // T6.4b-3b：真实鼠标磁铁。轮询与 F385 的原版输入采样一致；按下点用
  // b2_Shape_TestPoint 命中，只有落在金属体形状内才锁定（空点不吸引）。
  if g_MagReal and (g_Viewer <> nil) then
  begin
    GetCursorPos(pt);
    ScreenToClient(g_Viewer.Handle, pt);
    down := (GetAsyncKeyState(VK_LBUTTON) and $8000) <> 0;
    hasPos := g_Level.ClientToWorld(pt.X, pt.Y, g_Viewer.ClientWidth,
      g_Viewer.ClientHeight, wx, wy);
    if hasPos then
    begin
      g_MagX := wx;
      g_MagY := wy;
    end;
    if down and (not g_MagRealDown) and hasPos then
    begin
      g_MagTargetId := 0;
      if g_Level.PickBody(wx, wy, g_MagTargetId) then
      begin
        g_MagOn := True;
        PhysGetBodyPos(g_MagTargetId, g_MagLastX, g_MagLastY, pa);
        // T6.4b-4e：把世界命中点转成 body-local 抓取点（F454）。
        g_MagLocalX := Cos(-pa) * (wx - g_MagLastX) -
          Sin(-pa) * (wy - g_MagLastY);
        g_MagLocalY := Sin(-pa) * (wx - g_MagLastX) +
          Cos(-pa) * (wy - g_MagLastY);
        MagRealLog('down target=' + IntToStr(g_MagTargetId) +
          ' wx=' + FormatFloat('0.000000', wx) +
          ' wy=' + FormatFloat('0.000000', wy) +
          ' local=' + FormatFloat('0.000000', g_MagLocalX) + ',' +
          FormatFloat('0.000000', g_MagLocalY));
        Inc(g_MagRealCalls);
      end
      else
        MagRealLog('down-miss wx=' + FormatFloat('0.000000', wx) +
          ' wy=' + FormatFloat('0.000000', wy));
    end
    else if (not down) and g_MagRealDown then
    begin
      MagRealLog('up target=' + IntToStr(g_MagTargetId));
      g_MagOn := False;
      g_MagTargetId := 0;
    end;
    g_MagRealDown := down;
  end;
  if g_MagOn and (g_MagTargetId <> 0) then
  begin
    PhysGetBodyPos(g_MagTargetId, px, py, pa);
    dx := g_MagX - px;
    dy := g_MagY - py;
    d := Sqrt(dx * dx + dy * dy);
    if d > 1e-6 then
    begin
      f := 30.0 * d;
      if f > 315.0 then f := 315.0;
      sx := px + Cos(pa) * g_MagLocalX - Sin(pa) * g_MagLocalY;
      sy := py + Sin(pa) * g_MagLocalX + Cos(pa) * g_MagLocalY;
      PhysApplyForceAt(g_MagTargetId, f * dx / d, f * dy / d, sx, sy);
    end;
  end;
  if g_LinDamp > 0 then
    PhysApplyLinearDamping(g_LinDamp);
  if g_DampCoeff > 0 then
    PhysApplyAngularDamping(g_DampCoeff);
  PhysStep(0.01, 20, 20);
  Inc(g_LoopSteps);
  // T6.4b-2a：target 位移 >1e-3 时按 (PosX,PosY) 派发 OnMove。
  if g_MagOn and (g_MagTargetId <> 0) then
  begin
    PhysGetBodyPos(g_MagTargetId, px, py, pa);
    if (Abs(px - g_MagLastX) + Abs(py - g_MagLastY)) > 1e-3 then
    begin
      moveCalls := 0;
      if g_levelLua <> nil then
        EventsFireMove(g_levelLua, g_MagTargetId, px, py, moveCalls);
      Inc(g_LoopMoveCalls, moveCalls);
      g_MagLastX := px;
      g_MagLastY := py;
    end;
  end;
  // T6.4b-3a：运行时 Add_* 生成的对象补 sprite（GL 上下文需 current）。
  if SpawnCount > 0 then
  begin
    if (g_Viewer <> nil) and g_Viewer.Buffer.RenderingContext.IsValid then
      g_Viewer.Buffer.RenderingContext.Activate;
    try
      n := 0;
      while (n < SpawnCount) and SpawnAt(n, sid, skind, sstyle, sx, sy, sa) do
      begin
        Inc(g_LoopSpawnCalls);
        if (skind = 1) and (g_Level <> nil) then
          if g_Level.AddRuntimeGear(sid, sstyle, sx, sy, sa) then
            Inc(g_LoopSpawnCreated);
        Inc(n);
      end;
    finally
      if (g_Viewer <> nil) and g_Viewer.Buffer.RenderingContext.IsValid then
        g_Viewer.Buffer.RenderingContext.Deactivate;
    end;
    SpawnReset;
    AssignFile(tf, ExePath('spawn.log'));
    Rewrite(tf);
    WriteLn(tf, 'calls=', g_LoopSpawnCalls, ' created=', g_LoopSpawnCreated);
    CloseFile(tf);
  end;
  if g_LuaProgressOn and (g_levelLua <> nil) then
  begin
    Lua.GetField(g_levelLua, LUA_GLOBALSINDEX, PChar('DoProgress'));
    if Lua.LType(g_levelLua, -1) = 6 then
    begin
      Lua.PushNumber(g_levelLua, 0.01);
      rc2 := Lua.PCall(g_levelLua, 1, 0, 0);
      Inc(g_LoopCalls);
    end;
    Lua.SetTop(g_levelLua, 0);
  end;
  if g_Level <> nil then
  begin
    n := 0;
    while (n < ScrPosCount) and ScrPosAt(n, pid, px, py, pa) do
    begin
      Inc(g_LoopScrCalls);
      if g_Level.SetSpritePos(pid, px, py, pa) then
        Inc(g_LoopScrMoved);
      Inc(n);
    end;
    ScrPosReset;
  end;
  g_Level.SyncPhysics;
  // T6.4b-2b：Lua DoLevelComplete 置位后写副本存档并回菜单（真实完成链）。
  if LevelComplete then
  begin
    g_LoopTimer.Enabled := False;
    if EnvFlag('HOST_SAVE_PROFILE') and (EnvStr('HOST_PROFILE') <> '') then
      WriteLastCompleteLevel(EnvStr('HOST_PROFILE'), g_LevelIndex + 1);
    ExitLevel;
    Exit;
  end;
  elapsed := Integer(GetTickCount) - g_LoopStartMs;
  if (g_LoopMs > 0) and (elapsed >= g_LoopMs) then
  begin
    g_LoopTimer.Enabled := False;
    AssignFile(tf, ExePath('loop.log'));
    Rewrite(tf);
    WriteLn(tf, 'steps=', g_LoopSteps, ' calls=', g_LoopCalls,
      ' scrpos_calls=', g_LoopScrCalls, ' scrpos_moved=', g_LoopScrMoved,
      ' onmove_calls=', g_LoopMoveCalls,
      ' ms=', elapsed);
    CloseFile(tf);
    if EnvFlag('HOST_EXIT_AFTER_LOOP') then
    begin
      WriteTrace('exit');
      ExitProcess(0);
    end;
  end;
end;

var
  F: TForm;
  S: TGLScene;
  Cam: TGLCamera;
  Menu: TMenuScene;
  Level: TLevelScene;
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
  Headless, PakOpened, LevelMode: Boolean;
  ClickLevel, ClickOk, HasClick: Boolean;
  ClickX, ClickY: Integer;
  MouseHandler: THostMouseHandler;
begin
  MaybeLoadCrashLog;
  g_t0 := GetTickCount;
  g_tracePath := EnvStr('HOST_TRACE');
  Application.Initialize;
  MaybeReadProfile;
  WriteTrace('boot');
  Headless := EnvFlag('HOST_HEADLESS');
  LevelMode := EnvFlag('HOST_LEVEL_RENDER');

  // T6.4d-1：HOST_CLICK 命中菜单 Play 时，按档案 LastCompleteLevel 跑该关 Lua
  // （JSONL 由 HOST_LUA_LOG 指定）并建场景。点击是进程内命令入口，不是 LCL 消息。
  ClickLevel := False;
  HasClick := ParseClickSpec(ClickX, ClickY);
  ClickOk := HasClick and HitPlay(ClickX, ClickY) and g_profile.Ok and
    (g_profile.LastCompleteLevel >= 0) and (g_profile.LastCompleteLevel < 51);
  WriteTrace('menu');
  if ClickOk then
  begin
    log := '';
    ClickLevel := LuaBindRunLevel(g_profile.LastCompleteLevel, log) =
      'level=' + IntToStr(g_profile.LastCompleteLevel) + ' ok';
    if not ClickLevel then
      WriteLn(StdErr, 'click level failed: ', log);
  end;
  if ClickLevel then
    LevelMode := True;

  // pak 与纹理自检不需要窗口（有头/无头共用）。
  Pak := TPakFile.Create;
  PakOpened := Pak.Open(DataPath);
  g_Pak := Pak;
  if PakOpened and EnvFlag('HOST_TEX_SELFTEST') then
    RunTexSelfTest(Pak);

  // 无头模式（HOST_HEADLESS=1）：不建窗、不建 GLScene/GL 上下文，只跑物理与 Lua 自检。
  // 用于 phys_sweep 这类纯初始化跑关：没有窗口、没有渲染、没有消息循环。
  if Headless then
  begin
    RunPhysAndSelfTests;
    WriteTrace('exit');
    ExitProcess(0);
  end;

  F := TForm.CreateNew(nil, 0);
  F.Caption := 'A Magnetic Adventure';
  F.BorderStyle := bsNone;

  S := TGLScene.Create(F);
  g_Scene := S;
  // GLScene 默认 ObjectsSorting=osRenderBlendedLast：会把"混合对象"排到最后重排
  // 绘制顺序，菜单的 painter 顺序（背景→黑板→按钮→标题→光标）就乱了——
  // 实测背景被排到黑板之后，把黑板上半截盖掉。原版是严格按对象顺序画的。
  S.ObjectsSorting := osNone;
  CamEvents := TCameraEvents.Create;
  Cam := TGLCamera.Create(S);
  g_Cam := Cam;
  Cam.Position.SetPoint(0, 0, 10);
  Cam.CameraStyle := csCustom;
  Cam.OnCustomPerspective := @CamEvents.Ortho;
  S.Objects.AddChild(Cam);
  if PakOpened and LevelMode then
  begin
    Level := TLevelScene.Create(S, Pak, Cam);
    g_Level := Level;
    if EnvStr('HOST_LEVEL_MODEL') <> '' then
    begin
      // T6.4a-r-2d：从 SceneModel 的图元列表建场景（相机由模型里的
      // Set_CameraPosition 提供）；HOST_PAK_DIR 只用于素材名回退。
      if not Level.BuildFromModel(EnvStr('HOST_LEVEL_MODEL'),
        EnvStr('HOST_PAK_DIR'),
        StrToFloatDef(EnvStr('HOST_LEVEL_TIME'), 0.0)) then
        WriteLn(StdErr, 'level model failed: ', EnvStr('HOST_LEVEL_MODEL'));
    end
    else if ClickLevel then
    begin
      // T6.4d-1：点击进关的模型来自 HOST_LUA_LOG（LuaBindRunLevel 刚写的 JSONL）。
      if not Level.BuildFromModel(EnvStr('HOST_LUA_LOG'), EnvStr('HOST_PAK_DIR'),
        StrToFloatDef(EnvStr('HOST_LEVEL_TIME'), 0.0)) then
        WriteLn(StdErr, 'level model failed: ', EnvStr('HOST_LUA_LOG'));
    end
    else
    begin
      // T6.4a：Introduction 的相机与场景。draw 列表坐标是相机相对量；
      // 相机放在原版 Set_CameraPosition(-3,3) 的位置即可。
      Cam.Position.SetPoint(-3, 3, 10);
      Level.BuildIntroduction;
    end;
    AssignFile(tf, ExePath('level_init.log'));
    Rewrite(tf);
    WriteLn(tf, 'sprites=', Level.Sprites);
    Write(tf, Level.Log);
    CloseFile(tf);
    WriteTraceIndex('level', g_profile.LastCompleteLevel);
  end
  else if PakOpened then
  begin
    // 鼠标位置（设计像素，左上原点）：默认停在 glidle 抓包那一帧的位置
    // (884,684)-(916,716) 的中心 (900,700)，这样 A/B 是同状态（F188/F189）。
    MouseX := 900;
    MouseY := 700;
    Menu := TMenuScene.Create(S, Pak);
    g_Menu := Menu;
    Menu.Build(True, MouseX, MouseY);
    AssignFile(tf, ExePath('gl_init.log'));
    Rewrite(tf);
    WriteLn(tf, 'layers=', Menu.Layers, ' font=', Menu.Font.Count, ' text=ooo');
    Write(tf, Menu.Log);
    CloseFile(tf);
  end;
  V := TGLSceneViewer.Create(F);
  g_Viewer := V;
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
  MouseHandler := THostMouseHandler.Create;
  V.OnMouseDown := @MouseHandler.MouseDown;
  // T6.4d-7 私有桌面测试：进程内直接进关，不依赖鼠标/前台点击。
  if EnvFlag('HOST_AUTOCLICK') and not LevelMode then
  begin
    log := '';
    EnterLevel(StrToIntDef(EnvStr('HOST_LEVEL_INDEX'),
      g_profile.LastCompleteLevel), log);
    if log <> '' then
      WriteLn(StdErr, 'autoclick enter failed: ', log);
  end;

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

  // T6.4a 自检：建场景 + 渲染一帧后直接退，不进入玩法循环（T6.4d 再接）。
  if LevelMode then
  begin
    WriteTrace('exit');
    ExitProcess(0);
  end;
  // 菜单分支的自动退出（判据用）：渲染一帧后写 exit，不进入 LCL 事件循环。
  if EnvFlag('HOST_EXIT_AFTER_RENDER') then
  begin
    WriteTrace('exit');
    ExitProcess(0);
  end;

  // T6.3c：HOST_PHYS=1 → 建 world（4 面世界墙）；HOST_LUA_SELFTEST → 跑自检后退出。
  // 有头/无头共用同一个入口（无头分支在上面已经调用过它）。
  RunPhysAndSelfTests;

  Application.Run;
end.
