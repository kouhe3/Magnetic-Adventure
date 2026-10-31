# 交接文档 — Magnetic Adventure 复刻

> 写给下一个接手的 agent，自包含：读这一份 + 三份文档就能开工。
> 写于 2026-10-30（**L2-B 工具链考古那一轮之后**），`work` 分支。行文时工作树里只有本文这一处未提交改动；台账到 F208。

## 0. 一句话现状

**2026-10-31 更新**：T6.3/b0 完成（F249/F250）——Lua 的 `Add_*` 句柄是**堆对象指针**（工厂返回 `sub_583300`/`sub_58C500` 对象，`push eax; lua_pushinteger`），句柄校验 `sub_40AB90` 会解引用 `[handle]`；111 个脚本对句柄无算术、无 `io.` ⇒ 我方可用任意稳定 id，唯一硬要求是无效句柄回退（`Add_JointNail` → 0.0）。运行时证据用 `work/probe_objtable.py`（外部 `ReadProcessMemory` 读 `dword_665334` 对象管理器）。

**2026-10-30 决策：宿主改走 FPC/LCL + GLScene 重建（计划 M6），C++ 宿主保留作对照物。** 当天 T6.1 窗口层就完成：`src/host_lcl/magnet.pas`（40 行）让 `tools/wincompare.py` 的 15 个窗口字段 `diffs=0`（F214）。下面几段描述的是 **C++ 路线**（F184–F200）的成果，仍可作对照基准，但不再是交付主线。

两个 DLL 已复刻并验证完毕（**b2Physics 87/87 + 52 关全 PASS**；**Squall 99/99 + 17 个宿主导入 0 分歧**）；宿主 exe 过了窗口门禁，**主菜单由宿主代码现算**：纹理直读 pak（上传像素 37/37 与原版逐字节相同，F187）、布局按固定设计空间 1018×739 与二态悬停（F190），与原版逐像素 mean|Δ| **1.088/255**、A/A 地板 0.00。
Lua 侧已经起步：vendor Lua 5.1.5（未改动），pak 里 **111 个脚本 111/111 编译通过**、`lvl_info.lvl` 解析出 **52 关**（F191）。
卡点很明确：**关卡渲染**还没做（只有菜单 + 单帧画像）；Lua 的 **144 个绑定与执行语义**未接（T3.3 剩余）；文本仍是「同一字模格 ×3」的固定串，**宿主自己不会排版字符串**（T3.5）；Squall 的 **PCM 逐位**仍阻塞。

**本轮新增一条主线（2026-10-30 晚，L2-B 工具链考古）**：`requirements.md` 里「整 exe 字节级 = 明确不做」的否决理由（F01 说是 Delphi/VCL ⇒ 跨语言不可达）**前提已被证伪**——原版是 **FPC 2.2.4 [2009/12/27] + LCL 0.9.28.3 + GLScene(LCL 分支)**（F202），同语言同编译器，工具链公开可得。现在已经量到的：LCL 可自编且局部 **98.9% 逐位相同**（F206）、`.text` 在 **`0x521000`** 有断崖分界（F204）、GLScene 世系夹到 **trunk r4700** 且 `GLLCLViewer.o` **95.6%**（F208）、宿主自有代码 **≤390 KB / 约 400–700 个函数**。**但 `requirements.md` 那行还没改**（要一个显式决定，见 §11）。

台账 **248 条**（F01–F248，只增不减）。**T7.0 已完成（F244–F248）**：FPC 2.2.4 的 `GetMem/FreeMem` 不是进程堆直通（F235 的"进程堆直通/无私有块头"推论已证伪）；默认 RTL 下跨模块双向 10 万次交叉分配/释放都在首 5000 次内崩/挂；装宿主 `TMemoryManager`+`TMemoryMutexManager` 后在真宿主主线程上 A/B 10 万 + 交叉 realloc 2 万 PASS；跨模块异常两向都不可捕获。

## 0.1 勘误（F209/F210，2026-10-30，**优先于下文所有 L2-B 数字**）

下文凡是「逐单元百分比」（`GLLCLViewer.o` 95.6%、`GLObjects` 63.7%、`GLBitmapFont` 22.6%…）**全部作废**：`tools/code_match.py units` 当时把候选侧偏移拿去查目标侧偏移集合，量到的是"该单元地址窗在目标里被覆盖多少"，与单元内容无关（F209）。修好后的口径与结果：

- `units` 已改为候选坐标系（`candidate_coverage()`）：LCL 单元 78–89%、GLScene 族 28–68%。
- 新增 `code_match.py funcs`（capstone，操作数归一 → 指令序 `difflib`）才是"是不是同一份源码"的判据：自证 A/A = **100%**；**四个 LCL 单元 `win32int`/`stdctrls` 100%、`controls`/`forms` 99.9%**（⇒ "LCL 单元集差异"那条旧结论被否）；GLScene 族 **47–94%** ≥0.95，缺口聚集在 `GenerateSilhouette` 0.12 / `ApplyMappingMode` 0.24 / `RenderString` 0.66 / `CalcStringWidth` 0.19 这批函数（F210）。
- 结论：工具链与开关已经"对"（LCL 99.9% 是硬证据），r4700 与目标**同代但不是同一修订**；逐字节路线剩下的活是**版本夹逼**，不是重写或找源。
- **版本夹逼已完成（F211）**：`tools/ver_bisect.py` 扫 r4700→r5025，跳变点 r4850/r4900/r4980/r5002 ⇒ 原版 GLScene = **v1.1 / trunk r5000 一带**（v1.1 发布包与 r5002–r5025 的逐单元数字完全相同）。**11 个单元 1,043 个函数里只剩 12 个（2,448 B）sim<0.95**，全在文本/HUD/视口（`RenderTextAtPosition`/`RenderString` 助手/`DoRender`/`CalcStringWidth`/`SetHSpace`/`SetVSpace`/`LMPaint`/`LMEraseBkgnd`/`TGLPictureImage.Assign`/`DestroyRC`）。`SetHSpace` 的下限钳位在 trunk r4600–r6150 **一版都没有** ⇒ 这 12 个是**原版本地补丁**（与 F192 的 `gulim1.dat` 自绘字模吻合）。**库层到此算复原完成**。
- **补丁复原已完成（T3.8，F212/F213）**：残差 **12 → 0**。补丁入库 `patches/glscene-v11-game.patch`（5 个文件 / 6.4 KB），骨架 `tools/glskel6.pas`（`glskel_build.py` 默认）。内容：`SetHSpace`/`SetVSpace` 钳位到 ≥1、文本 API 改 `WideString`、`CalcStringWidth`/`RenderString` 声明 **`virtual`**、`TGLHUDText.FText: WideString`、`DestroyRC` 去掉 `RemoveBuffer`、`Assign` 加 `TGLPNGImage` 分支（`uses GLFilePNG`）、`LMEraseBkgnd` 恒 1、`LMPaint` 去掉 `WM_SIZE` workaround。判据：pristine v1.1 → `patch -p1` → `glskel_build.py` → `code_match.py funcs` 扫 12 单元 = **1,054 个函数 / 0 个 sim<0.95**。**反例**：`TGLFlatText.FText` 必须保持 `string`。副产品：原版链接了 `GLFilePNG`（F208 的"编不了"作废）。
- `cover` 的 72.8% / 59.0% / 尾部 19.9% **不受影响**（全局量与目标侧窗口，口径本来就对）。
- **像素数字属于 C++ 仿写宿主（`src/host`），不是最终判据**：主菜单 mean|Δ| **1.088/255**（F190）是 `src/host` 与原版的差。`tools/verify.py` 里**没有像素门禁**（docstring 明写"不含人眼看画面"，6 项门禁一张表在跑）；`window` 门禁只比 15 个窗口字段，且宿主目录/可执行名可用 `HOST_DIR`/`HOST_EXE` 覆盖（换实现不改判据）。若改走 FPC/LCL + GLScene 重建（F213 之后可行），渲染由同一份库产出，判据应换成逐调用/逐指令，像素只作验收。

## 0.2 T6.2 种子与判据（2026-10-30 晚，优先于 §6 的旧队列）

**已完成**：`tools/gl_seq_ab.py`（GLFFI02 双日志逐帧对拍；名字 + 已知签名参数；首个分歧；`--names-only` 只看结构；默认忽略 wgl 上下文函数/`glGetError`）。A/A 地板（原版菜单 17–19 s，两份 62 帧/110,559 条）：结构 1–13 帧 **0 bad_frames**、1–60 帧 **2**（frame14 上下文事件）；参数 `--float-tol 1e-3` 1–13 帧 **0**。逐位时 `glRotatef` 有 1e-4 差、`glColorMask` 的 GLboolean 高字节是栈残渣（工具已按低字节比）。命令：

```bash
python tools/gl_seq_ab.py work/aa_gl_a.bin work/aa_gl_b.bin --a-skip 1 --b-skip 1 --frames 13 --names-only
python tools/gl_seq_ab.py work/aa_gl_a.bin work/aa_gl_b.bin --a-skip 1 --b-skip 1 --frames 13 --float-tol 1e-3
```

**新宿主**：`src/host_lcl/magnet.pas` 已接相机（`TGLCamera.Create(S)` + `S.Objects.AddChild(Cam)` + `V.Camera := Cam`）并在 `Application.Run` 前 `V.Render`；`wincompare` 仍 **15/15**。**视口/呈现已证通**（F218）：设 `V.Buffer.BackgroundColor := clBlack` 后抓屏主体 `(0,0,0)`；加一个红色 `TGLCube`（`Diffuse/Emission` 红、`Lighting := False`）后 `work/host_cube2.png` 有 **3,306 个纯红 (255,0,0)** 像素。**正交相机也已接通**（F219）：`csCustom` + `glOrtho(±26.862, ±19.5)`，1 单位立方体在 1527×1108 抓图里占 **28×29 物理像素**（≈18.95 px/unit ×1.5 DPI）。**纹理直读 pak 也已打通**（F220）：`src/host_lcl/pakfile.pas` 解析 v0.2，`mm_cent2.png` 上到立方体，抓屏中心 (146,125,101) 木纹。**37 条启动纹理全部可解码**（F221）：`HOST_TEX_SELFTEST=1` 日志 `loaded=37/37`（PNG+JPG）。之前的 240 灰是 GLScene 默认背景 `clBtnFace`，不是 DC 失效（F217 已勘误）。`work/host_gl_final.bin` 的"无 swap/glClear"是缓冲尾巴（F222 勘误 F215），加 `GLPROXY_FLUSH=1` 即可抓到。**T6.2 菜单层已完成（F225–F230）**：`src/host_lcl/menuscene.pas` 把主菜单重建为 **19 个 `TGLHUDSprite`**（设计空间 1018×739，创建顺序=原版 draw 顺序）；新仪器 `tools/menu_draw_ab.py` 按**素材名**逐 draw 比 ⇒ **21/21 零差**（dbbox=0/duv=0/dα=0，含用户名文本层的两条 `gulim1.png`）。文本层：`TFontTable` 解析 `gulim1.dat`（258 条 32 B，`advance==w`、`v0` 落在四边形下边）+ `TMagTextSprite`（`TGLHUDSprite` 子类，一次 `glBegin` 画 N 个字模 quad；原版同一串画两遍 alpha=1/0，F231）。像素自读帧 `HOST_DUMP_FRAME`（`src/host_lcl/frameshot.pas`）mean|Δ| **2.45/255**，残差主要是光标不旋转与下采样。**T6.3 进行中：参数表 144/144（F239）+ a0（F240）+ a1（F241）+ a2 全量 **52/52** 关 call+args 与 `lua_probe` 相同（F242/F243）；下一步 T6.3-b：工厂语义（274 pending / 65 KB）+ b2 建体序对拍**；关卡场景模型归 T6.4。

**关键覆盖边界（F222/F223，勘误 F215）**：GL 代理**能**看见宿主的绘制调用——之前"没有 glClear/glBegin"是缓冲尾巴被 `p.kill()` 丢掉的假象（默认每 200 ms 或下一条调用才 flush）。单帧/短命进程抓包**必须** `GLPROXY_FLUSH=1`；同一次启动可抓到 `glBegin=2 / glVertex3f=48 / glClear=2`，两次启动 3,526 条名字序列逐条相同（A/A = 0）。仍看不见的只有扩展函数：`wglGetProcAddress` 的 3,158 次解析里 1,756 次返回 NULL（1.1 核心名，走静态导入 = 代理），1,402 次返回 `igxelpicd32.dll`（扩展名直连；渲染路径按 F178 不用扩展）。因此 T6.2 验收仍按三层：① 库层 `code_match funcs`（已过）② 场景参数（相机/对象/变换）③ 直接 GL 调用序（`gl_seq_ab.py`；宿主日志没有 `wglSwapBuffers`，需要"整段/无帧边界"模式）——像素只作验收。

## 1. 先读这几份（按顺序）

1. `AGENTS.md` —— 构建/工具/纪律（x86、32 位 CPython、pwsh、bin 只读）。
2. `docs/requirements.md` —— 验收口径：**L2-A**（导出名/序号/调用约定 + 原版 exe 直接加载新 DLL）。⚠️ 其中「~~L2-B 整 exe 字节级~~ **明确不做**：跨语言不可达（F01）」**已过期**：F153 勘误了 F01 的框架判定，F202/F206/F208 又把可行性量了出来 ⇒ 该行状态应改成「未测量」，等 §11 的显式决定。
3. `docs/facts.md` —— 事实台账。规则：**只增不减**；每条必须有可重放的出处（路径+行号/命令/观察步骤）；证伪要划掉改状态并另起勘误行。
4. `tasks/magnetic-adventure-plan.md` —— 任务树 + **变更记录**（按日期倒序，改计划必须追加一条，依据写 `F##`）。
5. 本文。

任务开工的硬规则：**计划里每个任务都要有 `依据：F##`**；依据缺失或指向不存在的事实 → 先修台账，不要开工。

## 2. 环境与硬约束

- 必须 **Win32/x86**：`/arch:IA32`（x87）才能逐位贴合原版，SSE2 会立刻产生 1e-4 级差异；静态 CRT（`/MT`）是 ABI 要求。
- 加载 DLL 的脚本必须用 **32 位 CPython**（`PY32`，默认 `C:/Users/K/.local/bin/python3.12.exe`），否则 `WinError 193`。
- 本机 Windows：用 `pwsh` 或 omp 的 bash（brush）。**不要裸 `bash`**（可能命中 WSL stub）、**不要 `du`**（PATH 上是 Sysinternals DU）。
- `bin/`（`gametop`/`baseline`/`masque` + IDA i64）是**只读 oracle，永不写入**；`work/` 放一次性产物（已 gitignore）。
- git：不提交 `main`；提交前 `git status`；不自行 push；不改写 author/committer 身份。提交前缀沿用 `feat(...)`/`docs(facts)`/`docs(plan)`/`fix(...)`。
- 换行：仓库追踪文件统一 **CRLF**，`.gitattributes` 是 `* -text`（blob 字节 == 工作树字节，F130）。新文件写完转 CRLF。
- **L2-B 工具链（本轮新增，都在 `work/` 与 `C:\tmp`，gitignore）**：
  - FPC 2.2.4：`C:\lazarus\fpc\2.2.4\bin\i386-win32\fpc.exe`（用户装的 Lazarus 0.9.28.2 附带，构建日期 **2009/10/25**，与目标的 12/27 差两个月但**实测不阻碍逐位对应**，F206）。
  - LCL 0.9.28.3（自编）：源码树 `C:\tmp\laz9283`（**必须无空格路径**），单元在 `lcl\units\i386-win32{,/win32}`。用 MSYS2 的 make（`pacman -S make` → `C:\msys64\usr\bin\make.exe`）。
  - GLScene 候选树：`work\glscene_r4700`（最 fit）、`work\glscene_v11`（发布包）、`work\glscene_lcl` / `work\glscene_4493`（SVN 分支）、`work\glscene_trunk`（trunk@2011，编不了）。
  - `svn.exe` 用 TortoiseSVN 自带的（`C:\Program Files\TortoiseSVN\bin\svn.exe`），直连 SourceForge 可用；Lazarus 走 `gitlab.com/freepascal.org/lazarus/lazarus`（`svn.freepascal.org` 服务端 down）。

## 3. 常用命令

```bash
# 构建（首次要带 -A Win32 -DB2_ARCH=IA32，之后增量即可）
cmake -S . -B build -G "Visual Studio 18 2026" -A Win32 -DB2_ARCH=IA32 -DB2_FP=default
cmake --build build --config Release                 # b2Physics + box2d
cmake --build build --config Release --target squall # Squall.dll（ogg/vorbis 直编）
cmake --build build --config Release --target host   # magnethost.exe（窗口 + 菜单渲染）
cmake --build build --config Release --target gl_proxy   # build/proxy_gl/Release/opengl32.dll

# 新宿主（FPC/LCL 路线，M6）：先建打过补丁的 GLScene 树，再编 magnet.exe
python tools/glskel_build.py work/glscene_patch build/host_lcl src/host_lcl/magnet.pas
cp bin/gametop/libpng13.dll bin/gametop/zlib1.dll build/host_lcl/   # GLFilePNG 运行时依赖
python tools/wincompare.py --orig work/winprobe_game --ours build/host_lcl --ours-exe magnet.exe

# 门禁（快集 6 项，~25 s；--full 追加 52 关全量重放并重生成 docs/levels.md）
python tools/verify.py
python tools/verify.py --full

# 导出契约
python tools/check_exports.py build/Release/b2Physics.dll                     # 87/87
python tools/check_exports.py build/Release/Squall.dll mapping/squall-exports.csv   # 99/99
python tools/check_exports.py build/proxy_gl/Release/opengl32.dll mapping/opengl32-exports.csv  # 368/368

# Lua：vendor 5.1.5 的 luac 全量编译 pak 脚本（期望 111/111）
cmake --build build --config Release --target luac
python tools/check_lua.py

# 窗口门禁（原版 vs 宿主，15 字段）
python tools/wincompare.py --orig work/winprobe_game --ours build/Release

# 物理单关 / 全量
python tools/gate.py work/rec_<ts> --name three_coins
python tools/sweep.py --jobs 8 && python tools/report_sweep.py --write

# 自动化（无人值守跑关，默认杀进程退出）
python tools/e2e_tutorial.py --dir work/winprobe_game --anchors work/uianchors.npz --clicks 40
python tools/e2e_record.py --dir work/e2e_game --name auto

# 存档（改完必须还原）
python tools/profile.py backup
python tools/profile.py set LastCompleteLevel 0
python tools/profile.py show

# GL 抓包（代理装进 work/glprobe：opengl32.dll=代理、opengl32_orig.dll=原版）
GLPROXY_LOG=C:/tmp/Magnetic\ Adventure/work/glprobe/glffi.bin \
  GLPROXY_T0=18000 GLPROXY_T1=19000 \
  GLPROXY_ONLY='glTexImage2D,glBindTexture,wglChoosePixelFormat,glBlendFunc' \
  python tools/uistate.py capture --dir work/glprobe --out work/glprobe_states --seconds 22

# GL 日志分析
python tools/gl_ffi.py stats  work/glprobe/glffi.bin
python tools/gl_ffi.py frames work/glprobe/glffi.bin --lo 14 --hi 28
python tools/gl_ffi.py frame  work/glprobe/glffi.bin --index 41629
# 原版抓包绘制列表（只作对拍基准；宿主已经不吃它了）
python tools/gl_drawlist.py work/glprobe/glffi4.bin --frame 20 --pack work/menu_draw.bin

# 纹理 id↔素材映射（改 pak/启动顺序时重跑；产物已入库，一般不用动）
python tools/gl_texpack.py work/glprobe/glffi8.bin --pak work/pak_gametop \
  --out work/menu_tex.bin --manifest work/menu_tex.json --csv mapping/textures.csv
python tools/gen_texture_table.py          # mapping/textures.csv → src/host/texture_table.h

# 宿主直读 pak：HOST_DATA 指向 pak 文件或含 data 的目录；顺便对拍上传像素与现算布局
HOST_DATA=bin/gametop/data HOST_TEX_CRC=work/host_tex_crc.txt \
  HOST_DRAW_DUMP=work/host_draws.bin \
  python tools/shot_window.py build/Release/magnethost.exe work/host_menu.png --wait 2 --mouse 900,700
python tools/host_tex_ab.py work/glprobe/glffi8.bin work/host_tex_crc.txt   # 期望 diffs=0 / 37
python tools/draw_ab.py work/menu_draw.bin work/host_draws.bin              # 期望 13/13 零偏差
python tools/shotdiff.py work/orig_menu.png work/host_menu.png --regions    # mean/p99/>16/分区域

# 宿主/原版截图（同一个工具；--wait 控制等窗口出现后再等多久，--mouse 按设计像素停鼠标）
python tools/shot_window.py build/Release/magnethost.exe work/host_menu.png --wait 2 --mouse 900,700
python tools/shot_window.py work/glprobe/game.exe work/orig_menu.png --wait 19 --mouse 900,700
```

### 3.1 重建 `work/` 目录（新克隆必做）

`work/` 全部 gitignore，新环境要自己造。四类目录：

```bash
# 1) pak 解包（Lua/PNG/JPG/OGG 都从这里来）
python tools/pak.py extract bin/gametop/data work/pak_gametop
python tools/pak.py list bin/gametop/data | head

# 2) 原版运行目录（= bin/gametop 的副本 + data 硬链接，bin/ 只读不能直接跑）
#    pwsh: $d='work/winprobe_game'; New-Item -ItemType Directory $d; Copy-Item bin/gametop/* $d -Exclude *.i64; New-Item -ItemType HardLink -Path "$d/data" -Target (Resolve-Path bin/gametop/data)
#    这份是 wincompare / uistate / frame_probe 的默认 --dir

# 3) GL 抓包目录：上面那份 + 代理
cp build/proxy_gl/Release/opengl32.dll work/glprobe/opengl32.dll
cp C:/Windows/SysWOW64/opengl32.dll work/glprobe/opengl32_orig.dll

# 4) b2 代理录制目录（e2e_record / gate 用）
cp build/proxy/Release/b2Physics.dll work/e2e_game/b2Physics.dll
cp bin/gametop/b2Physics.dll      work/e2e_game/b2Physics_orig.dll

# 5) 界面锚点（uistate 的门禁依赖它）
python tools/uistate.py capture --dir work/winprobe_game --out work/states --seconds 40 --every 0.4
python tools/uistate.py label   --frames work/states --state loading:0-4 intro:4-16 menu:17-40
python tools/uistate.py build   --frames work/states --out work/uianchors.npz
```

### 3.2 L2-B（逐字节）测量链

```bash
# 0) 一次性：编 LCL 0.9.28.3。源码来自 GitLab 镜像（svn.freepascal.org 已 down）
#    https://gitlab.com/api/v4/projects/freepascal.org%2Flazarus%2Flazarus/repository/archive.tar.gz?sha=f2e1062e
#    fixes_0_9_28 的 tip(2010-10-18) 里 lcl/lclversion.pas 就是 lcl_version = '0.9.28.3'
#    ⚠️ 源码树必须放无空格路径（放仓库里会被 "Magnetic Adventure" 的空格炸）
cp -r work/lazarus_09283 /c/tmp/laz9283
PATH="/c/msys64/usr/bin:/c/lazarus/fpc/2.2.4/bin/i386-win32:$PATH" \
  /c/msys64/usr/bin/make.exe -C /c/tmp/laz9283/lcl LCL_PLATFORM=win32
#    ⚠️ 不要加 OPT=-O1：安装器的 LCL 是**无优化**编的，加 -O1 会让对应率从 72.8% 掉到 38.6%

# 1) 编"同包骨架"（work/toolchain_probe/glskel5.pas：LCL 窗体 + TGLSceneViewer + 原版链接的 GLScene 单元）
fpc -n -Mdelphi -O1 -g- -Xs- -Xm -dLCL -dLCLwin32 \
    -Fu<LCL 0.9.28.3 单元> -Fu<glscene/Source 全树> -Fu<FPC units\i386-win32 的全部子目录> \
    -Fi<同上> -FE<out> -FU<out> work/toolchain_probe/glskel5.pas
#    -n 必须有（否则命中装机的 0.9.28.2 单元，数字立刻变差）

# 2) 对拍
python tools/code_match.py cover bin/gametop/game.exe <out>/glskel5.exe --tail 0x521000
python tools/code_match.py units bin/gametop/game.exe <out>/glskel5.exe
```

判据读法：`cover` 看"归因 %"与"目标侧覆盖 %"（全局量，口径正确）；`units` 是**候选坐标系的字节覆盖**（要连续 ≥64 B 相同），只回答"这个单元的字节有多少在目标里出现过"，**不回答**"是不是同一份源码"——后者一律用 `funcs` 的 `sim`（≥0.95 同码 / <0.80 不同，见 §0.1）。当前基准（r4700 + 正确开关）：归因 72.8%、目标侧 59.0%、尾部 19.9%；`funcs`：`win32int`/`stdctrls` **100%**、`controls`/`forms` **99.9%**、`GLObjects` 76.7%、`GLBitmapFont` 47.4%、`GLTexture` 53.6%。

## 4. 当前状态（按里程碑）

| 阶段 | 状态 |
|---|---|
| **M6 宿主重建（新主线）** | 窗口层 ✅ 15/15 `diffs=0`（F214）；T6.2 菜单层 ✅ 21/21（F225–F231）；T6.3 参数表 ✅ 144/144（F239）、a0 ✅（F240）、a1 ✅（F241）、a2 52/52 关 ✅（F242/F243），剩工厂语义 + 状态机；T6.4 应用层、T6.5 整机 A/B 排队 |
| **M7 函数级（T6.4 的工作台）** | T7.0 ✅ 跨模块 RTL 实测（F244–F248）：默认 RTL 双向 10 万次首 5000 次内崩/挂、交叉 realloc 挂死、chunk 归还时宿主 120 个空闲块悬垂；共享宿主 `TMemoryManager`+`TMemoryMutexManager` 后真宿主主线程 A/B 10 万 + 2 万 PASS；异常跨模块两向不可捕获。剩 T7.2 注入/日志、T7.3 双跑、T7.4 扫描、T7.5 台账、T7.6 整机 |
| M0/M1 资源与规格 | pak 格式闭环、Lua 导出、资产索引 ✅；T0.3（IDA 全量导出）/T0.4（oracle 采集）仍是历史遗留项，按需再补 |
| M2 两个 DLL | b2：87/87、52 关全量 PASS、A/A 地板内；Squall：99/99、17 个宿主导入调用序 0 分歧（含优雅退出）、环回音频逐秒 corr 0.9998；**剩 PCM 逐位（F134，三条路线均否，F147）** 与长时回归（T2.6b） |
| M3 宿主（C++ 仿写，**对照物**） | 路线切换后**不再是交付口径**：窗口层 15/15（F166）、主菜单渲染（F184）、纹理直读 pak（F187）、布局现算 + 二态悬停（F190，draw A/B 零偏差、**C++ 宿主截屏 mean\|Δ\| 1.088/255**）、Lua 5.1.5 + 52 关清单（F191）。这些能力在 M6 里用 GLScene 原库重做，判据换成逐调用/逐指令 |
| M4 验收 | 音频 diff ✅（F150）、e2e 自动化 ✅（F172/F174）、GL 绘制列表 ✅（F181/F182）；剩输入回放（T4.1）、帧 diff（T4.2）、存档 diff（T4.4）、映射覆盖（T4.5）、exe A/B 四层（T4.10）、1 ULP（T4.8） |
| M5 汉化 | 未开始（资源替换路线已定，F08） |
| **L2-B 库层** | **已复原（F213）**：GLScene = v1.1 + `patches/glscene-v11-game.patch`（5 文件 / 6.4 KB），12 个单元 **1,054 个函数 sim<0.95 的 0 个**；LCL 单元逐指令 99.9–100%（F210）；尺寸分界 `0x521000`、应用 ≤389,815 B（F204）。**剩**：应用层（≤390 KB，本没有源）—— 这正是 M6 的 T6.4 |

**本轮之前的硬数字**（写报告时直接引用）：
- b2：`calls=118558` / `steps=2018` / `bodies_bad=0`（F130 验收录制）。
- Squall：35 个 OGG 元数据 `diffs=0`（F142）；17 导入 20 步契约 `diffs=0`（F144）；环回逐秒 corr 0.9998–0.9999（F150）。
- 渲染：`glOrtho(±26.862, ±19.5)` ⇒ **18.95 px/unit**（F179）；菜单 **21 draw**、关卡 **26–27 draw**（F181/F182）；主菜单/关卡恒 **61–65 swap/s ≈ 15.6 ms/帧**（F177）。
- **C++ 宿主**菜单 vs 原版（两侧鼠标停同一设计像素，仅供对照，非最终口径）：空闲 mean|Δ| **1.088/255**、p99 20、>16 **1.346%**；悬停 Play **1.085/255**、>16 1.335%；A/A 地板 **0.00**（F190）。
- 主菜单绘制列表：宿主现算 vs 原版抓包 **13/13 零偏差**（`tools/draw_ab.py`，只忽略跟随鼠标的光标，F190）。
- 纹理：37 张上传像素与原版 `glTexImage2D` 整块 CRC **37/37 逐字节相同**（F185/F187）；WIC 解码即可，不 vendor 任何图像库。

## 5. 本轮（L2-B 工具链考古，2026-10-30 晚）做了什么

一句话：**把「整 exe 字节级」从"文档否决"推到"有数字的测量"**，并且没动任何生产代码（`src/` 一行未改）。

1. **工具链钉死（F202）**：`game.exe` 偏移 `0x24D120`（`.data` 尾部、紧邻 `.idata`）有 FPC 自带的版本串 `FPC 2.2.4 [2009/12/27] for i386 - Win32`，汉化版同串一字不差 ⇒ 两版同工具链。配套：LCL 0.9.28.3（DFM 的 `LCLVersion` 属性，两处）、GLScene 的 **LCL 分支**（`GLLCLViewer`/`GLFilePNG` 在，`GLFileJPG` 不在）。这直接推翻 `requirements.md` 里 L2-B 的否决理由（前提是 F01 的"Delphi/VCL"，而 F153 已勘误成 Lazarus/LCL）。
2. **LCL 可复现（F206）**：GitLab 镜像的 `fixes_0_9_28` 就是 0.9.28.3（**没有同名标签**），用 MSYS2 的 make + FPC 2.2.4 编通。同包骨架 `.text` = 1,133,264 B，其中 **79.5%** 能按同一位移在原版里找回（精确 59.6%），**局部 32 KB 桶 98.9% 逐位相同** ⇒ "编译器构建日期差两个月"不阻碍对应。
3. **尺寸分界（F204）**：`.text` 在 **`0x521000`** 处**断崖归零**（上方 584,928 B 一个字节都找不回）= GLScene + 应用代码。IDA 侧：全库 6,960 函数 / 1,184,338 B，边界上方 1,931 个 / 389,815 B；**144 个 Lua 绑定 23,378 B + 注册函数 2,603 B 是精确下界**；`lua_*` 调用者全落在 `0x581000–0x5A1000`。⇒ 宿主自有代码 **≤390 KB、约 400–700 个函数**（与 SM64 decomp 同量级）。
4. **GLScene 世系（F205/F207/F208）**：
   - `branches/GLSceneLCL`（`Source/Platform/GLLCLViewer.pas`，r4493/r5290/r5953 都有）**编不过**：缺 `LCLType`→`TCreateParams` 找不到；补上后 `tagPAINTSTRUCT` vs `PAINTSTRUCT`；绕开 viewer 则 `GLCadencer` 的 published 字段报错。
   - **trunk@2011-09 排除**：`GLContext.pas:153` 用泛型 `GThreadList<T>`，FPC 2.2.4 直接语法错误 ⇒ 原版不可能来自 2011 年的 trunk。
   - v1.1 发布包（2010-08）：Lazarus 树能编（修 `XCollection.pas` 一处 FPC 守卫；`GLFilePNG` 要摘掉，它拉进 FPC 编不了的 `LIBPNG.pas`），GLScene 贡献 325 KB，但尾部只对 19.7%。
   - **r4700（2010-03-15）最 fit**：用 exe 里 1,043 个 `gl*` 串当尺子比 `OpenGL1x.pas` 的 loader 清单（829→860→**981**→1070→1103→1108→1226），r4700 的"树有 exe 无"只有 30（v1.1 是 122）。逐单元：`GLLCLViewer.o` **95.6%**、`GLSilhouette` 88.8、`GLMaterial` 86.5、`GLTexture` 86.1、`GLScene` 84.2、`GLObjects` 63.7、`GLBitmapFont` 22.6。
5. **开关收敛（F208）**：LCL 必须**无优化**（改 `-O1` 重编 → 整体 72.8%→38.6%）；GLScene/应用必须 **`-O1`**（`-O2/-O3` 尾部掉到 0.5%）；**必须关 `-Cr/-Co`**（掉到 2.7–6.6%）。
6. **新仪器 `tools/code_match.py`**：`cover`（精确串 + 同位空隙 + 目标侧覆盖）与 `units`（读 `fpc -Xm` 的 `.map`，逐 `.o` 给命中率）。已用已知结果自证（复现 75.0% 与逐单元数字）。
7. **副作用**：`SourceForge` 的下载姿势也摸清了（目录页无 WAF，但 Edge 会拦下载；取浏览器 cookie + `postdownload` 页 meta-refresh 里的 `ts=` 令牌可直取）。

## 5.1 上一轮（GL 侦察 + 渲染里程碑 A + T3.2c）做了什么

1. **`src/glproxy/`**：`opengl32.dll` 转发 DLL（368 个 naked 桩，真身改名 `opengl32_orig.dll` 尾跳）。透明性已证：无代理锚点判 `menu` 于 16.7 s（无代理 16.5 s）、40 s 不崩（F176）。
   - 记录格式 `GLFFI02`：`id, tick, QPC, ret, ecx, edx, args[12], mem0/1/2 各 192 B`（`args[0]/[1]/[8]`；`glTexImage2D` 额外算整块 CRC32 写进 mem2 前 8 字节）。
   - 时间窗 `GLPROXY_T0/T1`（毫秒）、函数过滤 `GLPROXY_ONLY=a,b,...`、日志路径 `GLPROXY_LOG`。
2. **`tools/gl_ffi.py`**：v01/v02 解析 + `stats/frames/frame/init/window/names`。
3. **`tools/gl_drawlist.py`**：单遍模拟矩阵栈/纹理/颜色 + `glBegin` 顶点 → 世界坐标 draw 列表；`--pack` 输出 `GLDRW01`。
4. **`tools/gl_texpack.py`**：37 张纹理 id ↔ pak 素材（CRC32 + 翻转/通道序枚举，37/37 命中，F183）。
5. **`src/host/gl_render.cpp`**：WGL 上下文（PFD 24/24 双缓冲，同 F183）+ 两个二进制包 + ~15 ms 定时重绘；主菜单渲染对拍通过（F184）。
6. **T3.2c 纹理直读 pak**：`src/host/pak.{h,cpp}`（只读解析）+ `src/host/wic_decode.{h,cpp}`（WIC）+ `src/host/texture_table.h`（`tools/gen_texture_table.py` 从 `mapping/textures.csv` 生成）；`menu_tex.bin` 退役。上传格式照抄原版（RGB8/RGB 给 5 张 JPG、RGBA8/RGBA 给其余）。判据：`tools/host_tex_ab.py` 报 `diffs=0 / 37`（F185/F187）。
7. **文本 primitive 修复**（用户实测触发）：`gl_drawlist.py` 的 `PRIMS` 表从 0x0004 起错位一格，把原版的 `GL_QUADS`（0x0007）标成 TRIANGLE_FAN ⇒ 12 顶点的三连字按 fan 回放连成蝴蝶结，主菜单用户名渲染成 `o>>`。修表 + 绘制包升 `GLDRW02`（带 prim 原样回放）后该区域 mean|Δ| 4.46→1.22（F186）。
8. **仪器**：`tools/shotdiff.py`（逐像素 A/B）、`tools/host_tex_ab.py`（上传 CRC 对拍）、`tools/gen_texture_table.py`；`shot_window.py` 抓屏前把窗口挪到 (0,0) 并置前（否则底部拍到前台终端，曾误判成渲染回归）。
9. **T3.2d 菜单布局参数化**：`src/host/menu_layout.{h,cpp}`（设计空间 1018×739 的矩形/UV/纹理表 + 鼠标命中切换二态按钮 + 32×32 光标）；`menu_draw.bin` 退役。先做了判据探测（改客户区尺寸后 NDC 不变 ⇒ 固定设计空间，F188），悬停互斥规则由 `work/hover_probe.py` 实测（F189）。
10. **仪器**：`tools/draw_ab.py`（两个 GLDRW02 逐 draw 比 tex/bbox/UV）、`shot_window.py --mouse`（两侧鼠标停同一设计像素，悬停对拍必需）。
11. **T3.3 第一切片**：`vendor/lua-5.1.5`（官方，未改）编译成 `lua51` + `luac`，`tools/check_lua.py` 全量编译 pak 脚本 **111/111**；`src/host/levels.{h,cpp}` 解析 `lvl_info.lvl`（**pak 尾部记录**）得到 **52 关**；宿主启动写 `host_data.log`（`entries=707 levels=52 lua_ok=111`）。

## 6. 排队（建议顺序）

**当前主线是 M6（宿主重建）**：~~T6.2~~（菜单层已完成，F225）→ **T6.3 Lua 144 绑定 + 状态机（进行中：参数表 144/144（F239）+ a0（F240）+ a1（F241）+ a2 全量 52/52（F242/F243）；下一步工厂语义 + 对象表）** → T6.4 应用层复原（含关卡场景模型） → T6.5 整机 A/B。下面 1–7 是 **C++ 路线/对照物** 的队列，路线切换后降级为参考。

**M7 已开工**：T7.0 ✅（F244–F248）。下一步 T7.2 `hosttrace`，硬约束：注入函数跑宿主自己的线程（F246：主线程 PASS / 工作线程 1–2 万次内崩）、模块内 try/except 全包（F247）、共享宿主 `TMemoryManager`（`.data 0x5D5C50`）+ `TMemoryMutexManager`（`0x5D5C80`）或零分配，绝不能用自身 RTL free 宿主分配（F244/F245）。

> 主交付线仍是下面 1–7。**L2-B 的版本夹逼已经做完**（F211，见 §0.1）：GLScene = **v1.1 / trunk r5000 一带**，1,043 个函数只剩 **12 个**（2,448 B）对不上，且已确证是原版本地补丁（`SetHSpace` 的钳位在 trunk r4600–r6150 里不存在）。**下一步**（若继续 L2-B）：把这 12 个补丁函数按反汇编复原（2.4 KB，`tools/code_match.py funcs --unit <U> --top 400` 能给出逐个 sim 与位移，配合 IDA 反编译），然后剩下的就只有应用代码（≤390 KB）。⚠️ 旧的逐单元百分比已作废（F209）。

1. **T3.3 续：144 个绑定 + Lua 状态机**（F180/F191：清单与脚本加载已通，`mapping/lua-bindings.csv` 是绑定表；执行期需要 `Add_SimplePhysicObject`/`Attach_Shape*`/`Attach_SimpleGraphObject`/`Add_Joint*`/`Set_Phys*`，事件走 `Attach_ScriptToObject`）。**桩 harness 已落地（F224）**：`tools/lua_probe.cpp`（144 个桩 + JSONL）+ `tools/lua_probe_all.py`，**52/52 关脚本初始化 rc=0**。竖切已完成，下一步是把 `Add_*` 的实参/id 序列与**原版 b2 代理的建体调用序**对拍，再逐个把桩换成真实语义。
2. **T3.4 场景/关卡接线**。铁律：**初始化顺序是契约**——loading→intro→menu→关卡，纹理在启动期上传（F179），不能冷启动造场景（F169/F171/F177）。做关卡渲染前先把 `gl_drawlist` 的世界坐标归纳成宿主侧场景模型（±26.86 正交相机、逐 sprite `glMultMatrixf`）。
3. **T3.5 文本排版**（字模表 + 步进；见 §7）。菜单以外还有关卡 HUD/提示框。
4. **T4.1 输入回放**（现在是脚本化操作，还不是"录一次任意次重放"）。
5. **T4.10 宿主 exe A/B** 的四层判据里，②（DLL 调用层）要等 T3.4 之后才可用。
6. 收尾：T2.6b 长时回归、T4.4 存档 diff、T4.5 映射覆盖。
7. 已知阻塞：T4.9 PCM 逐位（F147 三条路线否，需要进程内 hook 或 WASAPI 环回）、T4.8 `Good Shot!` 残余 1 ULP。

## 7. 开放问题 / 风险

- **菜单布局已参数化**（F188/F190）：固定设计空间 1018×739、元素 1:1 纹理尺寸；改客户区尺寸原版不重排。剩下的是**关卡**的场景模型（26–27 draw/帧、±26.86 正交相机、逐 sprite `glMultMatrixf`），还没归纳。
- **渲染残差 1.3% 像素 >16 未归因**：不是几何偏移（9 个平移里 (0,0) 最优），mipmap 开/关几乎无差；怀疑是纹理过滤/取整与 DWM 1.5× 缩放的交互，暂按"过滤级残差"记录。**勘误（F194/F197，2026-10-30 探针）**：① 这一对 `orig_menu`/`host_menu` **不是同状态**（原版悬停 Exit + 光标位置不同），其 mean/百分比不能当渲染证据；② 同状态对的差异是**紧凑块**而非散点：悬停 Play 的 16×16 窗口 205/256、光标区 120/256；③ 悬停/空闲两帧 **draw 集合完全相同**（21 draw、纹理序一致），唯一差异是 tex 23/24 的 alpha 互斥翻转 ⇒ 悬停区的差异在"同一批 draw 的合成/采样"，不是"多一层 glow"；④ `tools/draw_ab.py` 丢掉 alpha=0 的 draw、不比 caps/prim/颜色，所以这类差异**当前门禁看不见**（F190 的 13/13 只覆盖可见 draw 的几何/UV）。
- **像素残差的两块已归因（F198/F199，2026-10-30）**：① 那个 16×16 窗口 205/256 的"悬停 Play 区块"其实是**光标**（鼠标就停在按钮中心，光标 32×32 居中）；掩掉光标后 maxwin 205→120，而整幅 >16 只从 1.335% 降到 1.295%。② 剩余紧凑块在设计 (827,645)/(658,530)，落在**齿轮/常春藤贴花**上，几何/状态全同 ⇒ 采样（mip/过滤）差异，与 F184 的过滤级结论一致。③ 顺带发现**结构漂移**：宿主从不发 alpha=0 的 draw（原版 21 条里 7 条），像素上被 `SRC_ALPHA` 吞掉所以看不见；`tools/draw_ab.py` 已升级为保留隐藏组并逐 draw 比 caps/prim/blend/rgba（可见组判 PASS/FAIL，`--strict` 才判隐藏组）。

- **磁铁光标会旋转**（F188）：静止 32×32 轴对齐，但 glffi4 的帧里顶点是转了约 45° 的正方形；驱动它的是鼠标速度、指向还是别的，未归因 ⇒ 宿主目前只画不转的光标。
- **动态文本宿主自己不会画**：主菜单的 `Welcome, <玩家名>` 是"烘焙纹理（`m_label1.png` = `Welcome,`）+ 字形 quad（`gulim1.png` 字模，UV 指向单格）"。现在能对上是因为**原样回放了抓到的字形 quad**；换用户名/换文案就不行，需要 T3.5 的字模排版。**勘误（F192，2026-10-30 探针）**：字宽表**是存在的** —— 就是 pak 里的 `gulim1.dat`（32 B/字：`u32 字符码; f32 u0,v0,u1,v1; u32 w,h,flag`，UV 以 512 归一化，`gulim1` 258 条、`h` 恒 31、`w` 8..29）；抓包 'o' 的 quad 与表内字符 111 那条记录**逐位相同**（`advance==w==17`）⇒ 直接解析 `.dat` 即可，不必反推步进。
- **关卡渲染**只有单帧画像（26–27 draw/帧、逐 sprite `glMultMatrixf`），变换链/场景图还没系统化；要做关卡渲染得先把"矩阵栈 → 世界坐标"的参数化做完（`gl_drawlist.py` 已能给世界坐标，但还没归纳成宿主侧的场景模型）。
- **PCM 逐位**与 **1 ULP** 是两条长期尾巴，别让它们阻塞主线。
- 外部参考：`C:/tmp/bpsim`（群友的 Unity DOTS 复刻，2022.2.23f1c1 + Entities 1.0.0-pre.44）里有现成的**内容管线**（274 关 / 526 contraption XML / prefabs.json）和 **QA harness**（`Bpsim/QA` + `DshBridge invoke_static`），思路可借鉴，但与本仓库无代码依赖。

- **T3.5 菜单路径已落地（F192/F200）**：宿主不再回放抓包的字形 quad，改为查 `gulim1.dat`（32 B/字：字符码 + UV 矩形 + w/h，`advance==w`）现算，整串仍是一个 `MenuDraw`（= 原版一个 `glBegin`）；`gl_init.log` 记 `font=258 font_mismatch=0`，`tools/draw_ab.py` 可见 13/13 零差。名字内容仍是抓包那串 `"ooo"`（来源=存档/配置，属 T3.6）；`pt_sans.dat`/`gulim2.dat`、换行与左右对齐还没做。

- **L2-B 的剩余差距清单（F208，按重要性）**：
  1. **应用代码 = 0%**：本来就没有源（144 个绑定之外，菜单/关卡/存档/输入这些逻辑都在宿主里）。量已定：≤299,696 B（尺寸残差）、≥25,981 B（绑定+注册精确值）。**形态未定**：是"按 F201 那种机械模板从反编译重写"还是"逐函数语义复原"——这是 §11 要定的事。
  2. **GLScene 少数函数漂移（已归因，F210）**：逐指令 ≥0.95 的字节占比 `GLExtrusion` 93.8%、`GLMaterial` 82.7%、`GLObjects` 76.7%、`GLLCLViewer` 73.9%、`GLScene` 60.6%、`GLTexture` 53.6%、`GLBitmapFont` 47.4%、`OpenGL1x` 27.7%；缺口固定落在 `GenerateSilhouette`/`RayCastIntersect`/`Apply*`/`PrepareParams`/`RenderString`/`CalcStringWidth` 这些函数上（不是散点）⇒ **同代 + 局部函数属于另一个修订**。旧的 63.7%/22.6%/95.6% 是坐标系混用（F209）。
  3. ~~**LCL 单元集差异**：`win32int` 61.5%、`forms` 65.4%、`stdctrls` 51.9%~~ **已否（F210）**：逐指令口径下 `win32int` **100%**、`stdctrls` **100%**、`controls`/`forms` **99.9%** ⇒ LCL 侧没有差距，之前那些低分全是 F209 的坐标 bug。
  4. **`OpenGL1x` 逐指令只有 27.7% ≥0.95**（r4700；v1.1 那次的 15% 是旧坐标口径）：这个单元是扩展绑定表，对版本极敏感，是"原版到底哪一版 GLScene"的最强指纹 ⇒ 版本夹逼的第一指纹就是它。
- **`requirements.md` 的 L2-B 行是过期文档**：它写着"明确不做：跨语言不可达（F01）"，而 F153 已把 F01 的框架判定勘误成 Lazarus/LCL、F202/F206/F208 又把可行性量了出来。**未擅自改定稿文档**，等 §11 的决定。

## 8. 踩过的坑（复用清单）

- **x32dbg 交互断点在本机不可用**（F251）：attach 原版后点一次 Play 会依次停在 6 个腾讯注入模块的入口（`biz_bundle`/`game_center`/`isgpet_bundle`/`picface`/`systembeautify_bundle`/`ichat_bundle`；`DllEntry`/`TlsCallbacks` 关不掉），此后 `PauseDebug` 不生效——`GetDebugState` 报 RUNNING、窗口应答 `WM_NULL`，但软件光标/悬停不刷新、点 Play 进不去关卡。宿主内验证用**外部 `ReadProcessMemory`**（`work/probe_objtable.py`：起游戏→等 menu→点 Play→读 `0x665334` 管理器），长期用 T7.2 进程内注入。
- **FPC 2.2.4 的 `GetMem/FreeMem` 不是进程堆直通**（F244）：`sysheap.inc` 只提供 `SysOSAlloc/SysOSFree`；`heap.inc` 是**每模块私有 freelist + 32K chunk + 共享 chunk 头**（`used`/`ocRecycleFlag`，`MaxKeptOSChunks=4`）。跨模块 free 只靠块头布局恰好相同，chunk 归还时另一侧 freelist 悬垂——实测 `host GetMem→DLL FreeMem` 与反向都在首 5000 次内崩/挂（F245/F246）。要么装宿主 `TMemoryManager`+`TMemoryMutexManager`（真宿主 `.data 0x5D5C50`/`0x5D5C80`），要么绝不交换堆所有权。
- **异常不能跨模块**（F247）：`ExceptAddrStack`/`ExceptObjectStack` 是每模块 ThreadVar。exe 回调里 raise 用 DLL `try` 包住 → exit 217；DLL raise 被 exe 包住 → DLL 先走 unhandled，exe 只捕到 `EAccessViolation`。注入函数必须模块内 try/except 全包，异常对象也不跨模块。
- **注入代码跑宿主线程**（F246）：同一份"共享 MM"代码在主线程 PASS，在工作线程 1–2 万次内崩——[推断] 宿主堆按单线程使用。b2 代理的 `B2RTLPROBE_DLL` 用主线程 `SetTimer` 进入，不要用 `CreateThread`。
- **KnownDLL 决定能不能文件代理**：`dsound` 拦不住（F147，`ole32` 在 KnownDLLs），`opengl32` 能拦（F175）。动手前先查 `HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\KnownDLLs`。
- **代理日志必须逐条 WriteFile**（F139）：录制用 TerminateProcess 结束，用户态缓冲会整段丢。GL 代理额外做了 200 ms 周期 flush。
- **单帧宿主抓 GL 必须 `GLPROXY_FLUSH=1`**（F222）：默认 flush 要等「下一条调用」，单帧进程画完就静默，`p.kill()` 再把 4 MB 缓冲整段丢掉 ⇒ 日志里"一条绘制调用都没有"，看起来像代理覆盖缺口（F215 就是这样误判的）。`<log>.wglproc` 另记 `wglGetProcAddress` 的解析归属：ret=0 是 1.1 核心名（静态导入，日志可见），落在驱动模块（`igxelpicd32.dll`）的是扩展名（直连，看不见）。
- **GLScene 三个默认值会静默毁掉画面**（M6/T6.2 实测，各一条）：① `TGLTexture.TextureMode` 默认 `tmDecal` ⇒ 透明区画成**白块**（白占比 32.75%→0，F227）；② `TGLScene.ObjectsSorting` 默认 `osRenderBlendedLast` ⇒ 绘制顺序被重排（背景盖住黑板，F228），要设 `osNone`；③ 库**不发 `glBlendFunc`**（GLStates 缓存假设已就位），必须在 `TGLSceneViewer.BeforeRender` 里显式设一次（F229）。
- **LCL 0.9.28.3 的 `TPicture` 读 PNG 丢 alpha**：透明区变黑/白。走 `GLFilePNG` 的 `TGLPNGImage` 解码后自己搬 32 位 RGBA（F226）；`TGLBitmap32` 要 `Blank := False` 才分配像素，且**先设格式再设尺寸**；`TGLPNGImage.Create` 无参。
- **像素判据用宿主自读帧**（`HOST_DUMP_FRAME`）：GLScene `Render` 后上下文被解绑（`glGetIntegerv` 全 0），读回前要 `RenderingContext.Activate`；`shot_window.py` 抓屏幕会被前台窗口污染（本次被微信盖住半屏，F230）。
- **代理里的 payload 要防越界**：`IsBadReadPtr` + 长度上限；`glTexImage2D` 的像素按 `w*h*bpp` 算整块 CRC32 才够精确（192 B 前缀对均匀边界的图会多图同分）。
- **GL 的变换链是 P·M·v**：顶点永远乘 MODELVIEW，和当前 `glMatrixMode` 无关（F181）。GLScene 的 HUD 会在帧中途把投影换成单位阵、用像素空间画东西，乘错就飞出屏幕。
- **固定管线状态要继承启动态**：`GL_BLEND` 在启动期就常开、帧内不再 `glEnable`，只按帧内调用推状态会漏掉它 → 白屏（F184）。
- **`GL_GENERATE_MIPMAP(0x8191)` 在部分驱动兼容 profile 下不生效** → 纹理不完整、采样成白；用 `gluBuild2DMipmaps`（F184）。
- **UI 布局可能是"固定设计空间"而不是"按客户区比例"**：改一次窗口尺寸抓一帧就能区分（`work/resize_probe.py`）。本次实测原版 21 个 draw 的 NDC 一字不差 ⇒ 设计空间写死即可，不必推导比例。
- **抓屏前先摆窗口、再放鼠标**：`shot_window.py --mouse` 必须在 `SetWindowPos` 之后（窗口一挪悬停位置就失效）。第一版顺序反了，测出「hover 没生效」的假阴性。
- **prim 枚举不能凭印象写**：GL 的 `0x0004..0x0009` 是 TRIANGLES/STRIP/FAN/QUADS/QUAD_STRIP/POLYGON，错一位就把 `GL_QUADS` 当 fan。4 顶点的 draw 看不出差别，**文本串是 12 顶点**，一错就成蝴蝶结（`Welcome, ooo`→`o>>`，F186）。回放时**按记录里的 prim 原样画**，别统一画 fan。
- **抓屏工具必须先摆窗口再拍**：`ImageGrab` 抓的是屏幕像素，窗口被终端/任务栏盖住时会把别人的像素拍进来，看起来像"渲染回归"（踩过：底部 108 px 是前台终端，误判 2.6 vs 1.37）。`shot_window.py` 现在先 `SetWindowPos(0,0)` + `SetForegroundWindow`。
- **UI 自动化只能走真实输入**：`PostMessage` 合成鼠标消息不触发按钮（F162）；点击坐标按**抓图的物理像素**算（F172，踩过 1.5×）；`Play` 落点由存档 `LastCompleteLevel` 决定（F171）；游戏内正常退出会 `ShellExecuteA` 弹网页 → 默认杀进程（F173）。
- **FPC/LCL 不适合逐函数 patch**：内部 `register` 约定（EAX/EDX/ECX，Self 在 EAX）+ LCL 对象布局，替换不复合；值得做的只有输入输出自包含的纯函数（in-process trampoline A/B）。
- **双后端/双实现互相比不算验证**：判据必须对"原版"，容差写进语料。
- **`svn cat` 必须带 peg 修订**：`svn cat -r 4700 URL@4700`。只给 `-r` 会按 HEAD 解析路径，文件移动过就报 `path not found`（GLScene 的 `Source/Base/OpenGL1x.pas` 后来搬过家，踩过一次）。
- **Lazarus/GLScene 源码树不能放含空格路径**：放 `work/`（`C:\tmp\Magnetic Adventure`）会让 `make` 与 fpc 的 `-Fu` 全炸；统一放 `C:\tmp\laz9283`、`C:\tmp\...`。
- **跨版本编骨架必须 `-n`**：不读 Lazarus 的 `fpc.cfg`，否则 `-Fu` 顺序里会先命中装机的 0.9.28.2 单元，数字立刻失真。同时要显式带上 FPC 全部 `units\i386-win32\*` 子目录（`-n` 后不会自动找 `fcl-process` 之类）。
- **LCL 用 `-O1` 编会毁掉对应率**（72.8%→38.6%）：Lazarus 安装器发的 LCL 是**无优化**编的。这条反直觉，别"顺手优化"。
- **GLScene 的 `.lpk` 里写着 `RangeChecks/OverflowChecks = True`，但原版没开**：照抄 lpk 会让尾部覆盖从 19.9% 掉到 2.7–6.6% ⇒ lpk 选项不能当"原版用的选项"。
- **trunk 2011+ 用了泛型**（`GThreadList<T>`）：FPC 2.2.4 直接语法错误 ⇒ 原版不可能来自 2011 年的 trunk，别往那个方向找。
- **老 GLScene 的 `GLFilePNG` 会拉进 `LIBPNG.pas`**，后者在 FPC 下 `FORWARD not allowed in interface section`；量体量时把该单元摘掉即可。
- **FPC 2.2.4 下 `Pointer` → 过程变量赋值是硬错误**：编 GLScene 必须 `-Mdelphi`（objfpc 会在 `OpenGL1x.pas` 报几十条 "Incompatible types: got Pointer"）。
- **FPC 2.2.4 无参函数指针必须写 `()`**：`L := A.NewState;` 取到的是函数地址本身（实测 = DLL 基址+0x13520），不是调用；症状是 `lua_gettop` 返回垃圾、`luaL_openlibs` 在 DLL 内访问冲突（F240）。
- **`lua_setfield` 不要预压 key**：它直接接收 C 字符串 key；先 `lua_pushstring` 会让每次注册残留一个栈值（实测 top=144），随后 `lua_close`/GC 随机访问冲突（F241）。
- **`lvl_info.lvl` 的字段是 `LevelFiles = "..."`（带空格）**：按 `LevelFiles=` 找会得到 0 关（F243）。
- **`lua_probe_all.py` 拼接多脚本必须补 `\n`**：上一个文件末尾无换行时，下一个文件首行的 `function BaseFsBeforeCreate` 不在行首，`^` 正则漏掉（lvl01 的入口被漏调用，F243）。
- **随机值对拍要在两侧固定种子**：`basefs.lua` 的 `AddFireWorks` 用 `math.random()` 算尺寸；C++ exe 与 FPC 加载的 lua51.dll 的 `rand()` 序列不同 ⇒ 两侧加载前都 `math.randomseed(1)`（F243）。
- **批量跑关每关要重置桩 id**：`luabind.pas` 的 `ResetIds` 把 `g_nextId` 归 1000（C++ 是每关新进程）；否则 id 跨关累积（F243）。
- **LCL/GLScene 程序里 `Halt` 会触发 finalization 崩溃**（退出码 217）：自检/一次性模式用 `ExitProcess` 直接收尾（F240）。

## 9. 关键文件索引

| 区域 | 文件 |
|---|---|
| 物理 DLL | `src/b2physics/b2physics.cpp`（87 导出）、`b2physics.def`、`vendor/box2d-2.0.2`（带 `altered (F###)` 注释） |
| 音频 DLL | `vendor/squall`（上游 1.48，3 处 `altered (F136/F138/F148)`）、`vendor/libogg-1.3.5`、`vendor/libvorbis-1.3.7` |
| 跨模块 RTL 探针 | `tools/rtlprobe/rplib.lpr`（FPC DLL：`rp_*` + `rp_host_entry`，宿主 RVA 常量）、`tools/rtlprobe/rphost.lpr`（同工具链 harness）、`tools/rtlprobe_build.py`（`--build`/`--same`/`--host`）；代理 env `B2RTLPROBE_DLL` 用主线程 `SetTimer` 进入 |
| Lua | `vendor/lua-5.1.5`（官方 tar.gz md5 `2e115fe26e435e33b0d5c022e4490567`，**未改动**）→ CMake target `lua51` + `luac` |
| 宿主（M6 主线） | `src/host_lcl/magnet.pas`（窗口+场景装配+Lua 自检）、`src/host_lcl/menuscene.pas`（菜单 19 层 HUD 精灵 + GLFilePNG 纹理）、`src/host_lcl/pakfile.pas`（pak 只读）、`src/host_lcl/frameshot.pas`（自读帧写 BMP）、`src/host_lcl/luadll.pas`（lua51.dll 动态加载）、`src/host_lcl/luabind.pas`（生成物：144 绑定壳）、`src/host_lcl/lualog.pas`（绑定 JSONL） |
| 宿主 | `src/host/main.cpp`（窗口/消息）、`src/host/gl_render.cpp`（WGL + 菜单渲染）、`src/host/pak.{h,cpp}`（pak 只读）、`src/host/wic_decode.{h,cpp}`（WIC 解码）、`src/host/texture_table.h`（生成物） |
| 代理 | `src/proxydll/`（b2，`B2FFI02`）、`src/squallproxy/`（`SQFFI01`）、`src/glproxy/`（`GLFFI02`）；桩由 `tools/gen_proxy.py` 生成 |
| 仪器 | `tools/instr.py`、`gate.py`、`sweep.py`、`report_sweep.py`、`replay_ffi.py`、`ffi.py`、`verify.py`、`shotdiff.py`（截图像素 A/B）、`host_tex_ab.py`（上传纹理 CRC 对拍）、`draw_ab.py`（绘制列表逐 draw 比）、`gl_seq_ab.py`（GL 调用序逐帧 A/B，F216）、`lua_bind_ab.py`（绑定 JSONL call+args 对拍）、`gen_texture_table.py` |
| UI/自动化 | `tools/uistate.py`、`uitemplate.py`、`e2e_tutorial.py`、`e2e_record.py`、`driver.py`、`winprobe.py`、`wincompare.py`、`shot_window.py`（窗口客户区截图） |
| GL | `tools/gl_ffi.py`、`gl_drawlist.py`、`gl_texpack.py`、`menu_draw_ab.py`（菜单逐 draw A/B，按素材名对齐）；抓包目录 `work/glprobe/` |
| 数据 | `mapping/*.csv`（导出表、绑定、关卡映射、纹理 id↔素材 `textures.csv`）、`docs/levels.md`（只能由 `report_sweep.py --write` 生成） |
| L2-B 侧 | `tools/code_match.py`（`cover`/`units`，本轮新增，已自证）；`work/toolchain_probe/`（`skel.pas` LCL-only / `glskel5.pas` 含 GLScene 的骨架）；`work/glscene_r4700`（最 fit 的候选树）、`work/glscene_v11`、`work/glscene_lcl`、`work/glscene_4493`、`work/glscene_trunk`（编不了）；`C:\tmp\laz9283`（自编 LCL 0.9.28.3 的构建树，不在仓库） |
| 文档 | `docs/requirements.md`、`docs/facts.md`、`docs/b2physics-abi.md`、`tasks/magnetic-adventure-plan.md`、`tasks/magnetic-adventure-todo.md`、本文 |

## 10. 接手第一小时

1. `python tools/verify.py` → 期望 `gates=6 fail=0`（~25 s）。挂了先修门禁，别看别的。
2. `cmake --build build --config Release --target host` + `HOST_DATA=bin/gametop/data python tools/shot_window.py build/Release/magnethost.exe work/host_menu.png --wait 2` → 应看到主菜单（若红底：`gl_init.log` 里 `ok=0`，查 `bin/gametop/data` 路径；若白屏，查 `GL_GENERATE_MIPMAP` 那条坑）。悬停/光标对拍记得两边都带 `--mouse 同一设计像素`。
3. `python tools/code_match.py cover bin/gametop/game.exe work/toolchain_probe/o_r4700final/glskel5.exe --tail 0x521000` → 应复现 **归因 72.8% / 目标侧 59.0% / 尾部 19.9%**；再跑 `funcs --unit controls.o` 应得 **99.9% ≥0.95**（`--unit GLObjects.o` 应得 76.7%）。数字对不上说明工具链被换过（多半是 LCL 被加了 `-O1` 或用错了 `-Fu`）。
4. 读 `docs/facts.md` 的 F175–F187（GL 结论 + WIC 解码 + prim 勘误）与 **F202–F208**（L2-B 工具链考古），再读计划 §变更记录 最近三条。
5. **新宿主先跑一遍**：`python tools/glskel_build.py work/glscene_patch build/host_lcl src/host_lcl/magnet.pas` → `wincompare --ours build/host_lcl --ours-exe magnet.exe` 应得 `fields=15 diffs=0`（F214）。
6. 按 §6 的 **M6** 队列开工（T6.3 绑定外壳）；先跑 `python tools/lua_binding_args.py --check-probe work/lua_probe/*.jsonl`，应得 `rows=144 ok=131 noargs=10 dynamic=3 partial=0 conflicts=0 factories=86` 与 `probe_calls=12593 kind_mismatch=0 arity_gt=0 known_extra=3`（F239）。Lua 接线自检：`HOST_LUA_SELFTEST=1 build/host_lcl/magnet.exe` ⇒ exit=0、`C:\tmp\magnet_lua_selftest.log` 为 `ok=TRUE result=5 top=1`（F240；运行目录需 `lua51.dll`）；绑定注册：`HOST_LUA_SELFTEST=2 HOST_LUA_DIR=work/pak_gametop` ⇒ `bindings=144 loaded=3/3`（F241）；52 关对拍：`HOST_LUA_SELFTEST=4 HOST_LUA_DIR=work/pak_gametop HOST_LUA_LOG_DIR=C:\tmp\magnet_bind` ⇒ `levels=52 ok=52 fail=0`；逐关 `python tools/lua_bind_ab.py work/lua_probe/lvlNN.jsonl C:/tmp/magnet_bind/lvlNN.jsonl` 应得 52/52 `mismatches=0`（F242/F243）。改计划记得追加变更记录并写 `依据：F##`。
7. **T7.0 工作台**：`python tools/rtlprobe_build.py --build --same splitctl release mm-heapa` ⇒ `splitctl PASS`、`release FAIL`（`dups=0`、`host_free_in_chunk=120`）、`mm-heapa PASS`（F244–F248）；真宿主：`python tools/rtlprobe_build.py --host work/e2e_game --mode mmrec --log work/rtl_mmrec.log` ⇒ `A/B 10 万 + C 2 万 ok=True`（`.data 0x5D5C50`/`0x5D5C80`，主线程）。

## 11. 已拍板：宿主走 FPC/LCL + GLScene 重建（原"要不要转正"）

**2026-10-30 决定：选 B。** 依据 F213（库层 100% 复原）+ F214（窗口层当天 15/15）。落地在新里程碑 **M6**：`src/host_lcl/magnet.pas` 是种子实现（窗口层已过门禁），`build/host_lcl/magnet.exe` 可用 `wincompare --ours build/host_lcl --ours-exe magnet.exe` 复验。M3 的 C++ 宿主保留作对照物，不再是交付主线。下面这张表保留为当时的决策依据。

现状：**前置条件成立，版本也夹到了**（F211）⇒ 库层（LCL + GLScene v1.1/r5000）**已复原**：LCL 逐指令 99.9–100%，GLScene 11 个单元 1,043 个函数只剩 **12 个（2,448 B）**，且已证是原版本地补丁（文本/HUD/视口）。剩下的是**应用代码**（≤390 KB，本就没有源）。⇒ 选项 B 的形态从"未知工程量"变成"**补 12 个函数 + 复原应用层**"。

| 选项 | 含义 | 代价 |
|---|---|---|
| A 维持现状（默认） | L2-B 只作"研究线"，主线继续 T3.3/T3.4 的语义等价 | 天花板停在 ~99%（像素采样级残差、1 ULP、PCM 逐位） |
| B 把 L2-B 转正 | 改 `requirements.md` 的 L2-B 行为"未测量/进行中"，主线切成"库层收敛 + 应用代码复原" | 主机工作量从"写 C++ 宿主"变成"复原 Pascal 源码"，前期还要先把 GLScene/LCL 的残余漂移收敛到 >99% |

**建议**：先做 §6 那条"函数级归因"的单单元竖切（半个到一个会话），拿到"是几个函数还是另一代"的答案再决定。那个答案直接决定 B 的工程量，也避免在没有数据的情况下改定稿文档。
