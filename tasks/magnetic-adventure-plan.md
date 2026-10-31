# 计划 — Magnetic Adventure C/C++ 复刻

依据：`docs/facts.md`；需求：`docs/requirements.md`。
规则：任务必须有 `依据：`；依据缺失或指向不存在的事实 → 不开工。

## M0 事实闭环（探针，不进主干）

- [x] T0.1 用调试器跟踪 `game.exe` 的 pak 读取循环，写出记录字段规格（消除第 33 条起的 1 字节漂移） 依据：F05、F13
- [x] T0.2 两版对照运行，归因 177/160 张图像差异与中文落点 依据：F08
- [ ] T0.3 IDA 载入 `b2Physics.dll` + `game.exe`，导出导出表/函数表/字符串引用 依据：F01、F02、F07
- [ ] T0.4 采集 oracle：启动→菜单→前 3 关，APITrace/RenderDoc 帧序列、PCM、存档、窗口/输入参数 依据：F03、F06

## M1 资源工具（可独立交付）

- [x] T1.1 `tools/pak` 只读解析 + 解包 依据：F05
- [x] T1.2 Lua 源码导出为文件树 + 两版 diff 依据：F04
- [x] T1.3 资产索引（像素 hash / PCM hash / 尺寸 / 类型） 依据：F06、F08

## M2 DLL 源码化（L2-A）

- [x] T2.1 `b2Physics` 导出表 → ABI 契约（函数签名、结构体布局、调用约定） 依据：F07
- [x] T2.2 C++ 实现（Box2D 2.x + C 包装），导出逐项一致 依据：F07
- [x] T2.3 差分：原 `game.exe` 加载新 DLL，逐帧物理状态比对 依据：F07（验收物：53 份录制全量重放，F99；逐关人工试玩，F71）
- [x] T2.4 `Squall` 导出表 + DSound 行为契约 依据：F06、F131–F152（T2.4a–d 全完成）
- [ ] T2.5 C++ 实现 Squall（已完成）与输出对拍（已完成，F149/F150）；剩 PCM 逐位（F147 已证明三条直取路线不可行） 依据：F06、F137、F144、F147、F149、F150
- [ ] T2.6 原 exe + 新双 DLL 整机回归 依据：F06、F07
- [x] T2.6a 整机冒烟：原 exe + 自建双 DLL 进 tutorial 关到结局页、模块 md5 核对、~90 s 不崩 依据：F141（细化 T2.6）
- [ ] T2.6b 长时/多关整机回归（含正常退出路径，触发 `SQUALL_Free`） 依据：F141

- [x] T2.4a 上游 `vendor/squall`（MIT，HEAD `20988426`）入库 + Win32 构建 + 导出表 99/99（`tools/check_exports.py`） 依据：F131、F132、F137（已完成；`squall` target 在 VS18 x86 上干净构建）
- [x] T2.4b 补 `libogg`/`libvorbis` 静态库并使 `SQUALL_Sample_LoadFromMemory` 能解 pak 内 OGG 依据：F133、F134、F137（PCM 逐位比留 T2.5）
- [x] T2.4c Squall 代理 DLL 抓包（17 个宿主导入函数的实参/返回值）→ 契约 依据：F131、F139（启动路径 5 个函数 / 44 次调用已抓并与自建 DLL 零差异；剩余 12 个见 T2.4d）
- [x] T2.4d 剩余宿主导入抓包：`Channel_Pause/SetVolume/Start/Status`、`Sample_LoadFile/Pause/Stop/UnloadAll`、`Free`（优雅退出才调） 依据：F139、F140、F143、F144（17 个导入全部覆盖：游戏内 12 个 + 探针 20 步全对齐）

## M3 宿主复刻（L0 + L1）

> **2026-10-30 起本里程碑降为对照物**：宿主主线走 M6（FPC/LCL + GLScene 重建，F213/F214）。
> 下面任务里的像素差值（如 T3.2 的 1.088/255）是 **C++ 宿主**的实测，不是最终口径；
> 换成 M6 后渲染由同一份 GLScene 库产出，判据改为逐调用（GL 序列）+ 逐指令（库层 sim）。

- [ ] T3.1 Win32 窗口/消息/输入（参数对照原 exe） 依据：F153–F159、F164、F166、F167（**脚手架已落地并通过窗口门禁**：`src/host/main.cpp` + CMake target `host`→`build/Release/magnethost.exe`，`tools/wincompare.py` 报 `fields=15 diffs=0`，外框/边框厚度也逐字相同（F166：PE 子系统版本 5.01）；全屏分支参数已实测（F167：`bsNone`+`wsMaximized`+`WS_EX_TOPMOST`，整屏无边框，实现留给 T3.6 接配置）；剩余：输入分发只做了消息日志，接场景属 T3.4）
- [ ] T3.2 OpenGL 上下文 + GLScene 等价渲染层 依据：F03、F158、F177、F178、F184、F187、F190（**里程碑 A + 纹理 + 布局全部落地**：WGL 上下文（F183）、纹理直读 pak（F187）、菜单布局宿主现算 + 二态悬停（F190）；原版 vs 宿主截屏 mean\|Δ\| **1.088/255**、p99 20、>16 1.346%（鼠标停同一设计像素，A/A 地板 0.00）。**剩**：关卡渲染（26–27 draw/帧的场景模型））
- [x] T3.2c 纹理直接读 pak（PNG/JPG 解码进宿主，替掉预烘焙的 `menu_tex.bin`） 依据：F183、F185、F187（**已落地**：`src/host/pak.{h,cpp}` + `src/host/wic_decode.{h,cpp}`（WIC，系统自带，不必 vendor）+ 生成物 `src/host/texture_table.h`（源 `mapping/textures.csv`）。判据：`HOST_TEX_CRC` 的 37 条 vs 原版上传 CRC **diffs=0/37**（含 5 张 JPG，F185），截图 mean|Δ| **1.375/255**、>16 2.105%（删掉 `menu_tex.bin` 仍能画）。边界：level 0 一致 ≠ mipmap 一致；800×600 的 `logo_1.JPG` 被 glu 扩到 1024×512）
- [x] T3.2d 菜单布局参数化：把 21 个 draw 的 bbox/UV 反推成宿主侧布局，替掉预烘焙的 `menu_draw.bin` 依据：F161、F182、F184、F188、F189、F190（**已落地**：`src/host/menu_layout.{h,cpp}` 按「设计空间 1018×739 逻辑像素」写死矩形/UV/纹理（F188：原版把固定设计空间缩放出去，不随客户区重排），鼠标命中切换二态按钮（F189）。判据：`tools/draw_ab.py` 比宿主现算列表 vs 原版抓包 → 13 个可见 draw **dx=dy=duv=0**；截图对拍（`shot_window.py --mouse` 两侧停同一设计像素）空闲 **1.088/255**、悬停 Play **1.085/255**；`menu_draw.bin` 已删）
- [x] T3.2a GL 调用面侦察：`opengl32.dll` 代理（368 导出全转发）记录名称/QPC 时间戳/栈上 6 个实参 依据：F03、F158、F175、F176（**已落地**：`src/glproxy/`（368/368 导出）+ `tools/gl_ffi.py`（`stats`/`frames`/`frame`/`init`/`names`）；透明性已证：无代理锚点判 `menu` 于 16.7 s（F169 无代理 16.5 s）、40 s 无崩溃、截图菜单/关卡正常（F176）；产出 F177/F178）
- [x] T3.2b GL payload 解码 + 绘制列表 依据：F178、F179、F181（**全部落地**：`GLFFI02` payload + 时间窗（F179）；`tools/gl_drawlist.py` 把一帧还原成 26–27 个 draw（纹理 id + 世界坐标 + UV + 颜色），JSON 可导出。坑：顶点永远乘 MODELVIEW（P·M·v），GLScene 的 HUD 会在帧中途把投影换成单位阵用像素空间画横幅，乘错"当前 mode"会让 bbox 飞到 ±509。**这就是渲染器的对拍基准**：逐 draw 比 bbox/UV/纹理 id）
- [ ] T3.3 pak 加载 + Lua 状态机 + 绑定 API 依据：F04、F180（**关卡数据面已摊开**：`lvl_info.lvl` 是 UTF-16LE 文本清单（`Caption`/`LevelFiles`/`LevelGroup`），零件与行为全在 Lua——116 个 `Add*` 工厂、144 个绑定、事件走 `Attach_ScriptToObject`（`OnMove`/`OnAddContact`/`OnPersistContact`/`OnRotate`）。⇒ **关卡编辑器的可行形态 = 产出「清单 + Lua」**，不改引擎；判据用原版加载（能过门禁/推进存档）；缺 pak 回写（`tools/pak.py` 只读）；**第一切片已落地（F191）**：vendor Lua 5.1.5（未改动）→ `lua51` 静态库 + `luac`，pak 里 111 个脚本 `luac -p` **111/111 通过**；`lvl_info.lvl`（pak 尾部记录）解析出 **52 关**，宿主 `host_data.log` 记录 `levels=52 / lua_ok=111`。**剩**：144 个绑定（`mapping/lua-bindings.csv`）+ 执行语义（状态机、事件回调））
- [ ] T3.4 场景/实体/物理/音频接线 依据：F03、F06、F07、F169、F171、F177、F179（**初始化顺序是契约**：loading/intro/menu 三段的内容与循环节奏都不同（F169、F177），37 张纹理在启动期一次性上传（F179），`Play` 落点还依赖存档 `LastCompleteLevel`（F171）⇒ 宿主不能"直接构造关卡场景"冷启动，必须按原顺序跑；状态判定用 `uistate` 像素锚点，不用定时点击（F172 的教训：intro 占 12.5 s，定时点击必落空））
- [ ] T3.5 文本渲染路径 依据：F11、F192（**路线已定**：文字 = pak 内 `*.dat` 32 B/字记录表（`u32 字符码; f32 u0,v0,u1,v1; u32 w,h,flag`，UV 以 512 归一化），抓包 'o' quad 与表内字符 111 记录**逐位相同**、`advance==w`、行高 `==h` ⇒ 解析 `.dat` 即可，不需要反推字宽；剩：行距/换行/左右对齐、关卡字体 `pt_sans*.dat`（3176 B，非 32 B 对齐，格式未解）与 `gulim2.dat`（32 条））
- [ ] T3.6 配置/存档写入（`cfg.ini` 等） 依据：F01
- [x] T3.8 复原原版对 GLScene 的本地补丁（库层收口） 依据：F211、F212、F213（**完成：12 个残差函数 → 0**。补丁入库 `patches/glscene-v11-game.patch`（5 文件 / 6.4 KB）：`SetHSpace`/`SetVSpace` 钳位到 ≥1、文本 API 改 `WideString`、`CalcStringWidth`/`RenderString` 声明 `virtual`、`TGLHUDText.FText: WideString`、`DestroyRC` 去掉 `RemoveBuffer`、`Assign` 加 `TGLPNGImage` 分支（+`uses GLFilePNG`）、`LMEraseBkgnd` 恒 1、`LMPaint` 去掉 `WM_SIZE` workaround。判据：pristine v1.1 + `patch -p1` + `tools/glskel_build.py` → `code_match funcs` 扫 12 个单元 = **1,054 个函数 / 0 个 sim<0.95**（构建两次复现）。副产品：原版**链接了 `GLFilePNG`**（推翻 F208 的"编不了"）。边界：只覆盖骨架链接的 12 个单元）
- [ ] T3.9 宿主实现路线拍板：C++ 仿写 vs FPC/LCL + GLScene 重建 依据：F202、F211、F213（**待拍板**。C++ 路线现状：`src/host` 已过窗口 15/15、菜单 mean|Δ| **1.088/255**（F190）——那是**仿写的残差**，且 `verify.py` 里没有像素门禁。FPC 路线现状：库层已 100% 复原（F213），宿主可以就是"LCL 窗体 + GLScene 视口 + 144 个 Lua 绑定"，渲染/文本/视口行为由同一份库产出，判据从"像素 diff"换成"逐调用 + 逐指令 + 像素验收"。**决策点 = HANDOFF §11**；两边的差别不是"能不能"，是"要不要把已有 C++ 代码扔掉"）
- [x] T3.7 用同版工具链测出宿主的"库/应用"分界 + 库层版本（L2-B 度量前置） 依据：F202–F211（**已完成**：① 尺寸分界 `.text` `0x521000`，应用 ≤389,815 B（F204）；② 工具链开关全对——LCL 逐指令 99.9–100%（F210）；③ **版本夹逼（F211）**：`tools/ver_bisect.py` 扫 r4700→r5025，跳变点 r4850/r4900/r4980/r5002 ⇒ GLScene = **v1.1 / trunk r5000 一带**（v1.1 发布包与 r5002–r5025 数字完全相同：100/100/98.8/84.9/84.6/99.7）；④ 残余：11 个单元 1,043 个函数里 **只有 12 个（2,448 B）sim<0.95**，全在文本/HUD/视口（`RenderTextAtPosition`、`RenderString` 助手、`DoRender`、`CalcStringWidth`、`SetHSpace/SetVSpace`、`LMPaint`、`LMEraseBkgnd`、`TGLPictureImage.Assign`、`DestroyRC`）；`SetHSpace` 的下限钳位在 trunk r4600–r6150 **不存在** ⇒ 这 12 个是**原版本地补丁**；⑤ F208 的"r4700 最 fit"被 F211 取代（glX 名字在 Win32 下被编掉，指纹假差异）。**下一步**：把 12 个补丁函数从反汇编复原（2.4 KB），再评估应用代码的复原形态）

## M4 行为对齐验收

- [ ] T4.1 确定性输入回放 harness 依据：F03、F169、F172、F174（**自动化驱动已可用**：`uistate` 状态机 + `uitemplate` 模板定位 + `e2e_tutorial` 无人值守跑关（38 s）+ `e2e_record` 自走录制并直接过门禁（40 s）。剩余：输入**回放**（按键/鼠标事件逐帧记录再重放）尚未做——现在是脚本化操作，同一脚本两次运行日志字节数相同（F174），但还没到「录一次输入、任意次重放」）
- [ ] T4.2 GL 调用序列 diff + 像素 diff 依据：F03、F194（**口径**：同状态对 + 16×16 窗口最大计数 + A/A 地板；`orig_menu` vs `host_menu` 这类跨状态对作废。已定位两个紧凑差异区：悬停 Play（205/256）与光标（120/256），归因见 F196）
- [x] T4.3 音频 diff（输出层）：环回 A/B 已跑通，逐秒 corr 0.9998–0.9999；PCM 逐位不可达见 T4.9 依据：F06、F149、F150
- [ ] T4.4 存档字节 diff 依据：F01
- [ ] T4.5 映射覆盖率报告 依据：F01
- [ ] T4.10 宿主 exe 的 A/B（exe 不能像 DLL 那样替换，改为"同脚本串行跑 + 在边界对拍"） 依据：F154、F166、F172、F174（四层判据，从便宜到贵：① 窗口层已可用——`tools/wincompare.py` 本身就是 exe-vs-exe，15 字段 diffs=0；② **DLL 调用层**：代理 DLL 与宿主无关，同一份 b2Physics/Squall 代理分别装进原版目录与自建宿主目录，两边跑同一脚本，用 `squall_ab` 的结构对拍比"调用序列/返回值"；③ 状态层：跑完 diff 存档（`tools/profile.py` 解码后逐键比）；④ 输出层：固定尺寸/DPI 的像素 diff 与环回音频 diff（只能给输出等价）。三个约束：单实例→串行且跑前 kill 干净；存档共享→每次备份复原；输入一致性→复用 `e2e_tutorial` 的脚本（F174 已证两次运行日志字节数相同））
- [x] T4.6 重录 `Get the Map` / `The First Totem`（现只剩 v01 日志，不可作判据） 依据：F99、F100（已完成，F101）
- [ ] T4.7 （路线已作废）用 `tools/dist_probe.py` 沿法线平移 B 扫出原版 `b2Distance` 误判为 0 的边界，并调两边内部 `Support`(`0x100144C0`)/`ProcessTwo`(`0x10009160`)/`ProcessThree`(`0x100092F0`) 定位误判发生在哪一步；反汇编锚点：poly-poly 泛型 `0x1000AB00`/`0x1000A5E0`、`b2TimeOfImpact=0x10018B20`、`b2_World_Step=0x10001490` 依据：F102、F107、F108（dist_probe 的 cdecl 调用约定错误见 F112；真实根因是 b2Distance 早退阈值，F122 已修）
- [ ] T4.8 残余 1 ULP：`Good Shot!` 的 `lvy`（首发 4847、bad 4,825，该录制 A/A 地板 0） 依据：F128
- [ ] T4.9 PCM 逐位（阻塞：dsound 文件代理 / 代理内 IAT / 日志重放三条路线均否） 依据：F134、F147、F195（**F195 追加**：环回 A/A 自身就不逐位（52.5% 样本差、`max|Δ|` 433，与 A/B 同量级）⇒ loopback 只作波形等价证据；逐位改抓 DLL 写进 DSound 缓冲区的字节，vtable hook 只替换返回对象的方法、不拦 `CoCreateInstance`）


## M5 汉化目标

- [ ] T5.1 汉化版资源作为交付资产（不改原 pak） 依据：F08
- [ ] T5.2 中文文本/字形核对 依据：F08、F11
- [ ] T5.3 交付包形态（`cfg.ini`、`images/`、`Uninstall/`） 依据：F09


## M6 宿主重建（L2-B 路线，2026-10-30 拍板）

> 决策依据：库层已 100% 复原（F213），原版就是 FPC/LCL + GLScene（F202）。C++ 宿主（M3）**保留作对照物**，不再作为交付主线。
> 判据变化：渲染不再靠像素 diff 逼近——同一份库 ⇒ 逐调用（GL 序列 diff）+ 逐指令（库层 sim）+ 像素只作验收。

- [x] T6.1 窗口层：LCL 复刻原版 15 个窗口字段 依据：F214、F154、F155、F157、F158、F166（**完成**：`src/host_lcl/magnet.pas` 40 行 —— bsNone 建窗 + 手工补 caption 位 + `SWP_FRAMECHANGED` + 按外框居中 + 视口用真实客户区；`wincompare --ours build/host_lcl --ours-exe magnet.exe` **fields=15 diffs=0**。坑：原版 style 带 `WS_POPUP`（切 BorderStyle 会丢）、LCL 的 `ClientWidth` 缓存改 style 后是旧的、`uses GLFilePNG` 需要 `libpng13.dll`/`zlib1.dll`）
- [x] T6.2 场景/渲染接入：TGLScene + 相机（±26.862 正交，F179）+ 纹理直读 pak （复用 F187 的 37 张表与 WIC/或改用 GLFilePNG） 依据：F179、F181、F182、F187、F225–F230（**完成（菜单层）**：`src/host_lcl/menuscene.pas` 把主菜单重建为 19 个 `TGLHUDSprite`（设计空间 1018×739，顺序=原版 draw 顺序），纹理走 GLFilePNG + 自持 32 位 RGBA（LCL 的 TPicture 丢 alpha，F226）。判据：新仪器 `tools/menu_draw_ab.py`（按素材名对齐）比原版 `glidle.bin` frame 10 vs 宿主 frame 2 ⇒ **19/19 draw 零差（dbbox=0/duv=0/dα=0）**，未配对的只有文本层；像素 `HOST_DUMP_FRAME` 自读帧 mean|Δ| 2.46/255（缺文本 + 光标不旋转为主，F230）。三个库级坑已记账：TextureMode 默认 decal（F227）、ObjectsSorting 默认重排（F228）、GLScene 不发 glBlendFunc（F229）。**剩**：关卡场景模型（归 T6.4 应用层））
- [ ] T6.3 Lua 144 绑定 + 状态机（T3.3 的内容迁到本路线） 依据：F180、F191、F201
- [ ] T6.4 应用层复原（菜单/关卡/存档/输入；≤390 KB，本就没有源）：先按"窗口层→菜单→关卡→存档"分块，用 GL 调用序列与窗口消息做判据；单元判据与工作台见 M7 依据：F204、F213
- [ ] T6.5 整机 A/B：`tools/gl_ffi.py` 抓新宿主的 GL 序列 vs 原版（F181），存档 diff（profile），像素作验收 依据：F181、F194、F196


## M7 函数级测量与替换（应用层单元判据，2026-10-30 新增）

> 目的：在黑盒输入输出之外建**逐函数判据**——记录未导出函数每次调用的 pre/post 状态，再用同工具链编出的实现顶替原函数入口，按 `(rva, call_seq)` 比对。
> 判据：**逐 call 的 post-state 摘要逐位相等 + 不崩溃 + 零调用函数清零**。「不崩溃」只是 harness 的运行条件，不是判据。
> 与 M6 的关系：M7 是 T6.4 的工作台与判据；T7.0/T7.1 可立即并行，不改变 M6 的 T6.3→T6.4→T6.5 顺序，T7.6 并入 T6.5 整机门禁。

- [x] T7.0 跨模块 RTL 实测：双向分配/释放 10 万次、`ReallocMem`、异常跨模块 unwind 依据：F235、F233（**完成（F244–F248）**：默认 RTL 的双向交叉 10 万次都在首 5000 次内崩/挂，交叉 `ReAllocMem` 挂死；装宿主 `TMemoryManager`+`TMemoryMutexManager` 后在真宿主主线程上 A/B 10 万 + 交叉 realloc 2 万 PASS；跨模块异常两向都不可捕获。工作台 `tools/rtlprobe/` + `tools/rtlprobe_build.py`；F235 的"进程堆直通"推论已证伪）
- [x] T7.1 应用层清单减法：用 patch 后 GLScene+LCL 骨架（F213）对 `game.exe` 跑 `code_match.py funcs`，sim≥0.95 标为「库，继承」、其余为待复原；输出 RVA/大小/sim/调用点数 依据：F236、F237、F238（**完成**：`tools/app_inventory.py` + `tools/glskel9.pas`（48 单元）⇒ 待复原 **1,012 函数 / 196,597 B / 60,868 指令**；清单 `mapping/app-functions.csv`，1,030 行含 18 个导入桩）
- [ ] T7.2 `hosttrace`：`hostrun.exe`（CREATE_SUSPENDED + 注入）+ `hosttrace.dll`（读 `HT_CFG`、5 字节 jmp trampoline、`HTFFI01` 日志、VEH 兜底回落原函数） 依据：F232、F233、F234、F235（**F244–F247 约束**：注入函数必须跑在宿主自己的线程上；模块内 try/except 全包，异常不跨模块；要么共享宿主 `TMemoryManager`+`TMemoryMutexManager`，要么零分配/只用 `GetProcessHeap` 自有块，绝不能用自身 RTL free 宿主分配）
- [ ] T7.3 双跑 A/B：R（原函数）与 S（我们的实现）同场景同输入，按 `(rva, call_seq)` 比 post-state（寄存器/栈出参/`fpu_cw`/ST0/watch CRC）；先量 A/A 地板 依据：F233、F234（**F246**：只在宿主线程上跑；工作线程会与宿主单线程堆竞争，2 万次内崩）
- [ ] T7.4 纯函数输入空间扫描：内嵌 A/B（快照→调我们的→比→恢复→返回原值），随机 + 边界 + 位模式 依据：F233
- [ ] T7.5 按调用频次批量替换 + 覆盖率台账（每函数命中次数）→ 自动生成 `mapping/functions.csv`（L1 函数映射） 依据：F204、F232
- [ ] T7.6 全替换混合产物（原版 LCL/GLScene + 我方应用层）整机回归，并入 T6.5 门禁 依据：F181、F194、F196、F213


## 变更记录

- 2026-10-31 依据 F258/F259（**b1 前置：每关新进程 + 人工 Play；合成点击不可依赖**）：① Play=resume，暂停菜单回主菜单不销毁关卡 ⇒ 每关采集必须新起进程。② 合成点击点 Play 多数会话让游戏 exit(0)（点背景安全；等 10 s/悬停 2 s 无效），只有一次外部进程点击成功进关并命中 3 个断点 ⇒ 自动点击不可依赖。③ hostprobe 固定 `--no-play`，Play 由人点；断点命中/寄存器/内存采集已验证。
- 2026-10-31 依据 F256/F257（**b1 采集链路定型：人工进关 + 脚本 attach 读内存；自动点击暂不可用**）：① attach + 手动 Play 不崩，断点可正常命中（3 次，eax=对象指针、edx=名字串记录）。② 合成点击（mouse_event/PostMessage/回车）在 attach 后不进关，无调试器时同一代码可用 ⇒ hostprobe 改 `--no-play` + 人工点 Play，采集改为「人工进关 → 脚本 attach → 按管理器偏移（`dword_665334` +0x1C/+0x20/+0x24）RPM dump 对象表/内联串」。③ 不再用"点 Play 后退出"推断崩溃（那是探针 finally 的 taskkill）。
- 2026-10-31 依据 F254/F255（**T6.3/b1 起步：运行时句柄/工厂快照已拿到；无头探针环境收口**）：① 存档设 0 → Play 进 Introduction，断点 0x59915A 两次命中，eax=对象指针（`magnet_hero_1`/`lvl_decor_4` 内联串可读）；0x5982FF 命中后单步 `push eax`，`[esp]`=eax ⇒ Lua 句柄=对象指针。② 切微软拼音 + `headless.ini [Events]` 全 0 后，无头 attach 点 Play 只停在自设断点（3.1 s），无注入 DLL 入口暂停；原生 `pause` 亦可用。⇒ 探针可直接用 x32dbg 交互断点做宿主内验证；T7.2 仍按计划做注入（不依赖调试器）。
- 2026-10-31 依据 F253（**MCP `PauseDebug` 不可靠；暂停改用原生 `pause`**）：GUI 会话里 `mcp__x32dbg_pausedebug` 连续三次后 `GetDebugState` 仍 RUNNING，状态栏「设置断点于 7775A1CC 失败！(SetBPX)」（插件在过期 IP 上 SetBPX）；同会话 `ExecuteDebuggerCommand("pause")` 立即 PAUSED，F12 亦正常。⇒ 探针脚本暂停统一用原生 `pause`；F251/F252 的暂停残留项关闭，T7.2 的注入/日志实现不受影响。
- 2026-10-31 依据 F252（**F251 勘误：入口暂停 = 搜狗输入法注入，不是 x64dbg 关不掉**）：① 现场确认 `biz_bundle`/`game_center`/`isgpet_bundle`/`picface`/`systembeautify_bundle`/`ichat_bundle` 来自搜狗 IME，切系统 IME 到微软拼音后不再加载；`groupy_32.dll`（Stardock Groupy）仍会注入。② 我把 `DllEntry=0` 写进了 `headless.ini` 的 `[Symbols]` 段（该文件无 `[Events]` 段）⇒ 未生效；已改为独立 `[Events]`（全 0、`EntryBreakpoint=0`）。③ 仍待对照：MCP `PauseDebug` 后 `GetDebugState` 报 RUNNING 但画面冻结（用 GUI F12 复核）。⇒ 探针环境要求：跑原版前切微软拼音；无头事件页默认全 0。
- 2026-10-31 依据 F249–F251（**T6.3/b0 完成：句柄 = 不透明对象指针**）：① 静态（`work/lua_bindings_asm.json`）：`Add_WoodWall`/`Add_GraphSprite`/`Add_JointNail` 都是 `call 工厂 → push eax → lua_pushinteger`，工厂返回 `sub_583300`/`sub_58C500` 分配的对象 ⇒ Lua 拿到的是对象指针，不是序号。② 运行时（`work/probe_objtable.py`，原版跑进 Introduction 后外部 `ReadProcessMemory`）：`dword_665334` 的对象管理器 `+0x1C/+0x20/+0x24` = WoodWall/GraphSprite/JointNail 子管理器，`+0x20` 内部是连续堆指针；句柄校验 `sub_40AB90` 会解引用 `[handle]` 并比对类链 ⇒ 句柄按指针解引用。③ 111 个脚本无 `io.`/`os.execute`、无句柄算术 ⇒ 任意稳定 id 语义等价，唯一硬要求是无效句柄回退（`Add_JointNail` 失败返回 0.0）。④ 工具教训（F251）：x32dbg 交互断点在本机被腾讯注入模块拖住且 `PauseDebug` 失效，宿主内验证改用「外部读内存」/T7.2 进程内注入。⑤ 下一步 T6.3/b1：对象表 + 工厂真实语义，判据用我方 JSONL 与原版 hook 序列（先由 hosttrace 提供）。
- 2026-10-31 依据 F244–F248（**T7.0 完成：跨模块 RTL 实测**）：① **F235 的推论被否**：FPC 2.2.4 的 `GetMem/FreeMem` 走 `heap.inc` 通用堆（每模块私有 freelist + 32K chunk、`MaxKeptOSChunks=4`），`sysheap.inc` 只给 OS 层；异常链 `ExceptAddrStack`/`ExceptObjectStack` 是每模块 ThreadVar。② 新仪器 `tools/rtlprobe/`（`rplib.lpr` FPC DLL + `rphost.lpr` 同工具链 harness）+ `tools/rtlprobe_build.py`（`--build`/`--same`/`--host`）；b2 代理加 env 门控 `B2RTLPROBE_DLL`（主线程 `SetTimer` 调 `rp_host_entry`，导出表仍 87/87）。③ 判据：默认 RTL 下 `host GetMem→DLL FreeMem` 与反向各 10 万次都在首 5000 次内崩/挂；交叉 `ReAllocMem` 挂死；强制 chunk 归还时宿主 120 个空闲块悬垂（对照 0）。装宿主 `.data 0x5D5C50` 的 `TMemoryManager` + `0x5D5C80` 的 `TMemoryMutexManager` 后，真宿主主线程 A/B 10 万 + 交叉 realloc 2 万 PASS（同一份代码在工作线程 1–2 万次内崩）。④ 异常：同工具链 exe→DLL 未捕获（exit 217）、DLL→exe 只捕获到 `EAccessViolation`（AV 退出）、真宿主 DLL 内调 `fpc_raiseexception` 进程死；共享 MM 不改变。⑤ 对下游的硬约束：T7.2/T7.3 的替换函数必须跑宿主线程、模块内 try/except、共享 MM 或零分配。

- 2026-10-31 依据 F243（**T6.3/a2 全量：52/52 关 call+args 与 `lua_probe` 相同**）：① `magnet.pas` 加 `LoadLevelScripts`（UTF-16LE `lvl_info.lvl`，`LevelFiles = "..."` 带空格）+ `LuaBindRunAll`（52 关独立 JSONL）+ `HOST_LUA_SELFTEST=4`。② `luabind.pas` 加 `ResetIds`（每关 id 从 1000 起）。③ 两侧固定 `math.randomseed(1)`（`AddFireWorks` 的随机尺寸）。④ 修 `tools/lua_probe_all.py` 的 `defined_entries` 拼接补换行（`BaseFsBeforeCreate` 被漏）。⑤ 判据：`levels=52 ok=52 fail=0` + 逐关 `lua_bind_ab.py` **52/52 `mismatches=0`**。下一步 T6.3-b：工厂语义（274 pending / 65 KB）+ b2 建体序对拍。

- 2026-10-31 依据 F242（**T6.3/a2 第一刀：e0 关 call+args 与 `lua_probe` 逐条相同**）：① 新增 `src/host_lcl/lualog.pas`（JSONL 序列化，对齐 `lua_probe`；NaN/Inf→null），生成器插入 `LuaLogBegin/End`。② `HOST_LUA_SELFTEST=3` 按 `lvl_o0,lvl_e0,basefs` 加载并调用三个入口，写 `HOST_LUA_LOG`。③ 新仪器 `tools/lua_bind_ab.py`：比 `call+args`（数值容差 1e-6，`ret` 不参与）。④ 判据：**55/55 行 mismatches=0**。下一步：52 关全量（Pascal 解析 `lvl_info.lvl`）+ 对象表/工厂语义。

- 2026-10-31 依据 F241（**T6.3/a1：144 绑定壳生成 + 宿主注册**）：① 新增 `tools/gen_lua_bindings.py` → `src/host_lcl/luabind.pas`（144 个 `cdecl` 壳 + `RegisterBindings`，桩语义对齐 `lua_probe`）。② 新增 `src/host_lcl/luadll.pas` 共享 lua51.dll 动态加载。③ 坑：`lua_setfield` 不要预压 key（否则栈残留 144 → 随机崩溃）。④ 判据：`bindings=144 loaded=3/3`（3/3 次）、独立程序 5/5 `top=0`、a0 与 `wincompare` 未回归。下一步 a2：52 关全量 + JSONL 与 C++ `lua_probe` 的 `call+args` 对拍（`ret` 因桩实现不同不参与）。

- 2026-10-31 依据 F240（**T6.3/a0：宿主接通 Lua**）：① CMake 新增 `lua51_dll`（`LUA_BUILD_AS_DLL`，产物 `lua51.dll`，导入库 `lua51_dll.lib` 避免与静态库同名）。② `src/host_lcl/magnet.pas` 动态加载 `lua51.dll`，`HOST_LUA_SELFTEST=1` 自检 `return 2+3` ⇒ `ok=TRUE result=5 top=1`。③ 两个 FPC 坑入账：无参函数指针必须写 `()`（否则取到函数地址）；自检退出用 `ExitProcess` 而非 `Halt`（LCL/GLScene finalization 崩 217）。④ `wincompare` 仍 15/15。下一步 a1：按 `mapping/lua-binding-args.csv` 生成 `luabind.pas`（144 个 `cdecl` 壳 + `RegisterBindings`），判据 52 关 JSONL 与 C++ `lua_probe` 逐条相同。

- 2026-10-31 依据 F239（**T6.3 参数表完成：144/144**）：① 新增 `tools/ida_lua_asm.py`（IDA MCP 导出 144 个函数的完整反汇编到 `work/lua_bindings_asm.json`）与 `tools/lua_binding_args.py`（解析五个读取器 → `mapping/lua-binding-args.csv`，144 行：args DSL / ret / factories）。② 复核 helper 语义：`sub_596C50`（4 槽）、`sub_596BA0`（3 槽，缺省不写）、`sub_596900`（optnumber）、`sub_5969F0`（optint）、`sub_596940`（optstring）；另有 `sub_598990`（对象属性，Lua 参数固定为对象 id）与 `sub_595D20`（lua_tolstring）。③ 分布：固定参数 131 / 无参数 10 / 动态 3（`Do_Command`、`Attach_ShapePolygon`、`Add_Rope` 变参）；86 个绑定有直接工厂调用；返回 int 58 / float 21 / none 56 / mixed 9。④ 判据：`rows=144 conflicts=0`；52 关语料 **12,593 调用** `kind_mismatch=0 arity_gt=0`（3 个 known_extra 是脚本多传、函数不读）。⑤ 顺带修复 `tools/lua_probe.cpp`：NaN/Inf 实参写成 `null`（`-nan(ind)` 不是合法 JSON）。T6.3 下一步：按参数表生成绑定外壳 + 接 `lua51`。

- 2026-10-31 依据 F236–F238（**T7.1 完成：待复原 1,012 函数 / 60,868 指令**）：① 清单：`0x521000` 之上 1,931 函数 / 389,815 B，GLScene 骨架（48 单元）按 sim≥0.95 认领 901 / 193,128 B；剩 1,030 / 196,687 B / 60,886 指令，其中 18 个单 `jmp` 桩 ⇒ 待复原 **1,012 / 196,597 B / 60,868 指令**（F236）。产物：`tools/app_inventory.py`（仪器）、`tools/glskel9.pas`（48 单元骨架）、`mapping/app-functions.csv`（1,030 行，`status=shim/pending`）。② 链接布局是**交错**不是纯尾块（F237）：`0x581000–0x5A1000` 集中 491 个 / 30,219 指令；应用自定义 `TGL*` 类 44 个。③ 导入是**两级桩**（F238）：`call 本地桩 → jmp 全局桩 → jmp [IAT]`；leftover 中 109 个碰 lua51、46 个 b2Physics、18 个 Squall，842 个不碰导入。④ 工作量（人时，按函数粒度估算，非实测）：≤32 B 116 个 0.2–0.5、33–64 190 个 0.35–0.8、65–128 204 个 0.6–1.3、129–256 280 个 1.0–2.2、257–512 160 个 2–4.5、513–1024 45 个 4–9、>1024 17 个 8–24 ⇒ **1,128–2,624 h（约 0.56–1.31 FTE 年）**；若 LLM 起草 + 指令判据 + 替换 harness 把验证开销压到 0.4–0.7 倍，约 **450–1,850 h**。⑤ 下一步：T7.0 跨模块 RTL 实测 → T7.2 `hosttrace` → T7.3 双跑 A/B。

- 2026-10-30 依据 F232–F235（**新增 M7：函数级测量与替换，作为 T6.4 的单元判据**）：① 判据定为「逐 call post-state 摘要逐位相等 + 不崩溃 + 零调用函数清零」；「不崩溃」只是 harness 运行条件。② 已量：`0x521000` 上方 **1,931 函数 / 389,815 B**（F232）；样本 `sub_521990` 的签名与调用约定（Self@EAX、float 在栈、`retn 8`）可从反编译 + 调用点恢复（F233）；exe **无 ASLR/DEP**（F234）；FPC 2.2.4 的堆是 `GetProcessHeap`（F235，跨模块实测见 T7.0）。③ 任务链：T7.0 跨模块 RTL → T7.1 清单减法（glskel `funcs` 减出应用层）→ T7.2 `hosttrace` → T7.3 双跑 A/B → T7.4 纯函数扫描 → T7.5 批量替换 + `mapping/functions.csv` → T7.6 并入 T6.5。④ 边界：这是单元判据，不替代组合层门禁（GL 序列/像素/存档/52 关）；差分测试不等于证明，覆盖不到的路径仍未证。

- 2026-10-30 依据 F231（**补上用户名文本层，菜单 21/21 draw 零差**）：`src/host_lcl/menuscene.pas` 新增 `TFontTable`（`gulim1.dat` 258 条 32 B 记录）与 `TMagTextSprite`（继承 `TGLHUDSprite`，重写 `DoRender`：一次 `glBegin(GL_QUADS)` 画 N 个字模 quad，色 `(0.8984,0.7852,0.5195)`）。原版同一串画两遍（alpha=1 + alpha=0），两遍都补。判据：`tools/menu_draw_ab.py` ⇒ **pairs=21 mismatches=0**，不再有未配对项；像素 2.464→2.448/255（文本只占 0.2% 面积）。

- 2026-10-30 依据 F225–F230（**T6.2 菜单层完成：逐 draw 19/19 零差**）：① `src/host_lcl/menuscene.pas`（19 个 TGLHUDSprite，设计空间 1018×739）+ `src/host_lcl/frameshot.pas`（`HOST_DUMP_FRAME` 自读帧缓冲写 BMP）；`magnet.pas` 接场景并加 `BeforeRender` 启动态。② 新仪器 `tools/menu_draw_ab.py`：按**素材名**（id 用像素 CRC 反查）逐 draw 比设计空间 bbox/UV/alpha，判据 `mismatches=0`。③ 三个库级坑入账：`TextureMode` 默认 `tmDecal`（透明区画白，32.75%→0，F227）、`ObjectsSorting` 默认 `osRenderBlendedLast`（重排绘制顺序，F228）、GLScene 不发 `glBlendFunc`（F229）；另 LCL `TPicture` 读 PNG 丢 alpha（F226）。④ 门禁 `verify.py` 仍 6/6 PASS。

- 2026-10-30 依据 F224（**T6.3 桩 harness：52/52 关能初始化**）：新增 `tools/lua_probe.cpp`（CMake target `lua_probe`，链 vendor `lua51`）——从 `mapping/lua-bindings.csv` 注册 144 个桩，`Add_*` 返回递增 id、其余返回 0，返回个数按脚本里的单行多值赋值推断；每次绑定调用写一行 JSONL（名字 / 实参 / 桩返回）。新增 `tools/lua_probe_all.py` 解析 `lvl_info.lvl` 批量跑 52 关，判据 `rc=0`，产物 `work/lua_probe_all.json`。结果：**52/52 rc=0**（调用 34–768、对象 17–177），单关两次运行逐字节相同。边界：桩返回值是约定不是语义；下一步把 `Add_*` 的 id/参数序列与原版 b2 代理的建体调用序对拍（T6.3 验收）。

- 2026-10-30 依据 F222/F223（**勘误 F215：GL 代理没有覆盖缺口，丢的是缓冲尾巴**）：`src/glproxy` 三处改动——① 新增 `<log>.wglproc`，逐条记录 `wglGetProcAddress` 的解析结果（name / ret / 模块基名），把"函数指针是否绕过代理"变成可读一行（实测 1,756 次 NULL = 1.1 核心名走静态导入、1,402 次 `igxelpicd32.dll` = 扩展名直连）；② 新增 `GLPROXY_FLUSH=1` 每条立即落盘——单帧宿主画完首帧后不再调 GL，默认 200 ms flush 永远等不到下一次调用，`shot_window.py` 的 `p.kill()` 又把 4 MB 缓冲整段丢掉，这正是"宿主一条绘制调用都没有"的来源；③ 删除 F215 那次无效的 `GLPROXY_WRAP`（核心名 `wglGetProcAddress` 返回 0、扩展名不在代理的 368 个导出里，wrap 永远不适用）。判据：同一次启动日志 `glBegin=2 / glEnd=2 / glVertex3f=48 / glClear=2 / glMultMatrixf=8`，抓屏仍有 702 个纯红像素；同一 exe 两次启动各 3,526 条、名字序列逐条相同。⇒ T6.2 的「调用序」判据**恢复可用**（固定管线立即模式全覆盖）；下一步给 `gl_seq_ab.py` 加「宿主日志无 `wglSwapBuffers`」的整段比较模式。

- 2026-10-30 依据 F221（**37 条启动纹理全部可解码**）：`magnet.pas` 增加 `kTextureAssets`（`mapping/textures.csv` 37 条）+ `HOST_TEX_SELFTEST=1` 自检；`PakFile` 逐条读出、按扩展名临时落盘、LCL `TPicture` 解码，日志 `loaded=37/37`（PNG+JPG 两条路径）。这只覆盖 pak→像素，不含 GL 上传格式（F183/F187）。

- 2026-10-30 依据 F220（**T6.2 纹理直读 pak 打通**）：① 新增 `src/host_lcl/pakfile.pas`（Pascal 版 v0.2 解析，按名字大小写不敏感读取，支持尾部记录）；`magnet.pas` 用 `HOST_DATA` 打开 pak，把 `mm_cent2.png` 解出为 `TGLPersistentImage` 上到立方体，抓屏中心出现木纹 (146,125,101)。② 实测坑：`TGLTextureImage.Create` 的 owner 必须是 `TGLTexture`（传 `TGLScene` 抛 Invalid type cast）；`TGLPictureImage.Assign` 会落到 inherited 再抛；改用 `TGLPersistentImage` + owner=`Cube.Material.Texture`。③ 临时文件必须 `.png` 后缀，否则 `TPicture.LoadFromFile` 报 Unknown picture extension。④ 判据见 F220；下一步把 37 张纹理表与场景模型接上。

- 2026-10-30 依据 F219（**T6.2 正交相机接通**）：`src/host_lcl/magnet.pas` 用 `Cam.CameraStyle := csCustom` + `OnCustomPerspective` 调 `glOrtho(-26.862,26.862,-19.5,19.5,-100,100)`；1 单位红色立方体在 1527×1108 抓图里占 **28×29 物理像素**（≈18.95 px/unit ×1.5 DPI），与 F179 一致。判据用像素几何（代理仍看不到 `glOrtho`，F215）。下一步：纹理直读 pak（37 张表）/场景模型。

- 2026-10-30 依据 F218（**勘误 F217：视口/呈现已证通**）：① `src/host_lcl/magnet.pas` 设 `V.Buffer.BackgroundColor := clBlack`、`V.Buffer.Lighting := False`，并加一个 `TGLCube`（Diffuse/Emission 红色）；`tools/shot_window.py --wait 2` 抓屏得到 **3,306 个纯红 (255,0,0)** 像素、其余 (0,0,0) ⇒ GLScene 的 clear + draw + present 都工作。② 之前的 240 灰是 `TGLSceneBuffer.FBackgroundColor` 默认 `clBtnFace`（`GLScene.pas:7986`），不是 DC/上下文失效；上一条变更记录里"视口/呈现未打通"作废。③ 代理无 swap/glClear 仍是 F215 的覆盖边界，不影响像素判据。T6.2 下一步：相机改 ±26.862 正交、接纹理直读 pak 与场景模型。

- 2026-10-30 依据 F215/F216/F217（**T6.2 判据先落地：调用序仪器 + A/A 地板；GLScene 内部调用不在代理覆盖内**）：① 新增仪器 `tools/gl_seq_ab.py`（GLFFI02 双日志逐帧对拍，名字 + 已知签名参数，首个分歧；`--names-only` 只看结构；默认忽略 wgl 上下文函数与 `glGetError`）；`tools/gl_ffi.py` 加 `iter_records()` 复用唯一日志解析。② A/A（原版、菜单、17–19 s，两份 62 帧/110,559 条）：`--names-only` 1–13 帧 **0 bad_frames**，1–60 帧 **2 bad_frames**（frame14 上下文事件）⇒ 有效窗口 13 帧或扣 2 帧地板；参数 `--float-tol 1e-3` 1–13 帧 **0 bad**（逐位时 glRotatef 有 1e-4 差、GLboolean 高字节是栈残渣）。③ 新宿主接相机并 `V.Render`（`src/host_lcl/magnet.pas`），窗口门禁仍 **15/15**；但 `work/host_gl_final.bin` 只有 3,273 条初始化记录、**无 swap/glClear**，抓屏主体是 LCL 灰 ⇒ **T6.2 还没打通视口/呈现**。④ **T6.2 验收改为三层**：库层 `code_match funcs`（已过）+ 场景参数（相机/对象/变换）+ **直接 import 的 GL 调用序**（`gl_seq_ab.py`，用 13 帧 A/A 口径）；GLScene 内部渲染由库层 sim 保证，代理看不见（F215），像素只作验收。⑤ 代理侧试过把 `wglGetProcAddress` 返回值换成代理桩（名字取 pre 桩 args[0]），未取得可见调用，改动已回滚、未入库；后续二选一：泛型扩展 thunk 或坚持三层判据。⑥ `tools/glskel_build.py` 修掉硬编码 `glskel5.exe` 的 exe 检查（现在按 `pas` basename 报 `exe=True`）。

- 2026-10-30 依据 F213/F214（**路线拍板：宿主改走 FPC/LCL + GLScene 重建**）：① `requirements.md` 的 L2-B 从"明确不做"改为**目标**——原否决理由（跨语言不可达）已被 F153/F202 证伪，库层 100% 复原（F213），只剩应用层（≤390 KB）。② 新增 M6（T6.1–T6.5）；M3 的 C++ 宿主**保留作对照物**，不再是交付主线。③ **T6.1 当天完成**：`src/host_lcl/magnet.pas` 40 行让 `wincompare` 的 15 个字段 `diffs=0`（F214）。配方要点：原版 style 带 `WS_POPUP` ⇒ 必须"无边框建窗 + 事后补 caption 位"，切 `BorderStyle` 会丢 popup 位；定位要按**外框**居中（LCL 的 poDesktopCenter 按客户区，差 3/14 px）；视口要用 `GetClientRect` 的真实客户区（LCL 缓存是改 style 前的 1024）。④ 判据随之改变：渲染不再靠像素 diff 逼近，改成逐调用（GL 序列）+ 逐指令（库层 sim），像素只作验收。⑤ 运行时依赖：新宿主 `uses GLFilePNG` ⇒ 需要 `libpng13.dll`/`zlib1.dll`（原版目录自带；缺失时进程不退出但无窗口）。

- 2026-10-30 依据 F213/F190（澄清，不改判据）：**把"宿主像素 1%"标清归属，并解开宿主实现的硬编码**。① `tools/verify.py` 的 6 项门禁里**没有像素判据**（docstring 明写"不含人眼看画面"），所以"像素差 1%"不是门禁在卡，而是 `src/host`（C++ 仿写路线）的历史测量（F190）。② 唯一耦合是 `window` 门禁把 `--ours` 写死成 `build/Release/magnethost.exe`——已改成 `HOST_DIR`/`HOST_EXE` 可覆盖，换实现零改脚本，判据（15 个窗口字段）不变。③ README/HANDOFF 给该数字加了"属于 C++ 仿写路线"的限定：若转 FPC/LCL + GLScene 重建，渲染由同一份库产出，判据应换成逐调用/逐指令，像素只作验收。④ 新增 T3.9 记录这个岔路（待拍板，决策点 HANDOFF §11）。

- 2026-10-30 依据 F213：**T3.8 收口——GLScene 库层 100% 复原，12 个单元 1,054 个函数残差归零**。① 剩余 6 个逐个攻掉：`LMPaint` 去掉 `WM_SIZE` 黑边 workaround、`LMEraseBkgnd` 恒 `Result:=1`、`DestroyRC` 去掉 `RemoveBuffer`、`CalcStringWidth`/`RenderString` 需声明 **`virtual`**（原版经 vtable 调用；改成直接调用会让 `AlignmentAdjustement` 与 `TGLFlatText.DoRender` 对不上）、`TGLPictureImage.Assign` 的第 4 个分支是 **`TGLPNGImage`**。② 认出那个分支的办法：直接读目标端的 VMT（类名在 VMT+12 的 ShortString，父类在 VMT+8）⇒ `TGLPNGImage = class(TGLBaseImage)`，与 v1.1 的 `GLFilePNG.pas` 一致。③ 因此原版**链接了 GLFilePNG**：把它加进骨架 `uses` 后它在本工具链下编得过（`GLFilePNG.o` 存活 98.9%），F208「GLFilePNG 编不了」作废。④ 交付物：`patches/glscene-v11-game.patch` + 骨架 `tools/glskel6.pas`（`glskel_build.py` 默认值）；判据 `patch -p1` → 重编 → `code_match funcs` 全绿。⑤ 至此 §11 的 B 选项只剩**应用层**（≤390 KB）。

- 2026-10-30 依据 F212：**库层残差 12→6，补丁主体是"Unicode 文本路径 + 空格钳位"**。① `SetHSpace`/`SetVSpace`：目标端有 `cmp eax,1; jle` → 下限钳位到 1（trunk r4600–r6150 无此改动）⇒ 复原后 sim 0.74→**1.00**（函数体 48→64 B，与原版同尺寸）。② `CalcStringWidth` 的目标端读 16 位字符并有 `shr eax,1` ⇒ 参数是 `WideString`；连同 `RenderString(aString)` 一起改宽字符后 0.66→**0.99**、0.97→**1.00**，嵌套的 `LayoutAdjustement` →**1.00**。③ `TGLHUDText.FText` 改 `WideString` 后 `GLHUDObjects.o` 从 82.8% 到 **100.0%**。④ 反例：`TGLFlatText.FText` 同样改宽会让 `DoRender` 0.90→0.84 ⇒ 保持 `string`（"同族类"不能照抄）。⑤ 新增任务 T3.8（库层收口），工作树 `work/glscene_patch`（gitignore），重编与判据全在 `tools/glskel_build.py` + `code_match.py funcs`。⑥ 至此 §11 的选项 B 只剩两件事：**6 个函数 + 应用层（≤390 KB）**。

- 2026-10-30 依据 F211：**版本夹逼收口——原版 GLScene = v1.1 / trunk r5000 一带，库层 1,043 个函数只剩 12 个对不上**。① 新增仪器 `tools/ver_bisect.py`（svn 按修订 update → `tools/glskel_build.py` 重编骨架 → `code_match.py funcs` 逐单元 sim，30 s/修订），`tools/glskel_build.py` 从 `work/bisect/build.py` 提升（可重跑，写得动手）。② 跳变点：`OpenGL1x` 27.7(r4700)→96.8(r4900)→99.7(r5010)、`GLObjects` 100(r4850)、`GLScene` 98.2(r4980)→99.7、`GLTexture` 98.8、`GLBitmapFont`/`GLLCLViewer` 84.9/84.6(r5002)；**r5002–r5025 与 v1.1 发布包逐单元数字完全相同** ⇒ 原版就在这一带。③ 残余 12 个函数（2,448 B）全在文本/HUD/视口，`SetHSpace` 的下限钳位在 trunk r4600–r6150 的源码里**一版都没有** ⇒ 判定为**原版本地补丁**，与 F192（`gulim1.dat` 自绘字模）一致。④ 推断勘误：F208 用"源码里的 `GLGetProcAddress` 清单"当指纹，r4704+ 的 116 个"树多"全是 `glX*`（Win32 不编）⇒ 那个指纹把条件编译当差异，"r4700 最 fit"是假象。⑤ T3.7 标完成；L2-B 从"未测量"推进到"库层已复原（差 12 个函数）"，`requirements.md` 那行仍留给人拍板。

- 2026-10-30 依据 F209/F210：**T3.7 的"逐单元"数字作废，换成指令级逐函数归因；结论 = 同代 + 局部函数漂移**。① 查 `tools/code_match.py units` 时发现坐标系混用：`attribute()` 的 `cov` 是**目标侧偏移**，`cmd_units` 却拿**候选侧偏移**去查 ⇒ 对位移 ≠ 0 的单元（GLScene 族全在 +0xD8xxx–+0x116xxx，LCL 也有 +0x2a20/+0x91be0 的整段偏移），百分比实际是"该单元在我们布局里的地址窗被目标覆盖了多少"。F208 的 `GLLCLViewer.o` 95.6% 由此而来。② 修 `units`（新增 `candidate_coverage()`/`coverage_map()`，候选坐标系；`dmap` 用 `NO_D` 哨兵，负数位移合法）；`cover` 的 72.8%/59.0%/尾部 19.9% 不变（全局量/目标侧窗口）。③ 新增 `code_match.py funcs`（capstone：操作数归一成寄存器/立即数/内存形状后比指令序，`difflib`；位移候选 = 覆盖图采样 ∪ 单元内见过的位移，先按 4 B 字率预排再算 sim）⇒ 只有 call 目标地址不同不扣分。自证：A/A=100%、四个 LCL 对照单元 **99.9–100%**（顺带否掉 F206/F208 的"LCL 单元集差异"推断）。④ 实测：GLScene 族 47–94% 的函数 ≥0.95（`OpenGL1x` 27.7%），缺口聚集在 `GenerateSilhouette` 0.12、`ApplyMappingMode` 0.24、`RenderString` 0.66、`CalcStringWidth` 0.19 这批 ⇒ **r4700 是同一代但不是同一修订**，逐字节路线剩下的活是版本夹逼，不是重写。⑤ 决定：**不动 `requirements.md` 的 L2-B 状态**（仍等版本夹逼结论）；T3.7 的任务描述改成"分界已量完，剩版本夹逼 + 抽样复核"。

- 2026-10-30 依据 F208：**GLScene 世系夹到 trunk r4700（2010-03-15）附近，编译开关三条收敛，比对仪器落地**。① 指纹法：拿 exe 里的 1,043 个 `gl*` 串当版本标尺，对 trunk 各日期的 `OpenGL1x.pas` 逐个比 loader 清单 —— 829(2009-06)→860(2010-01)→**981(r4700)**→1,070(r4708)→1,103(r4724)→1,226(2011-03 起)，r4700 的"树多 30"最小（v1.1 是 122）。② trunk@2011-09 被排除：泛型 `GThreadList<T>` 在 FPC 2.2.4 下是语法错误。③ 开关实验定死三条：**LCL 无优化**（-O1 重编让整体 72.8%→38.6%）、**GLScene/应用 -O1**（-O2/-O3 尾部 0.5%）、**无 -Cr/-Co**（2.7–6.6%）。④ r4700 逐单元：`GLLCLViewer.o` **95.6%**、GLScene 84.2%、GLMaterial 86.5%、GLTexture 86.1%、GLObjects 63.7%。⑤ 新增仪器 `tools/code_match.py`（`cover`/`units`），已自证。⑥ 结论：库层（LCL+GLScene）已经是"同代 + 小差"，**剩下的差距是应用代码本身（0%）+ 少数单元的内部漂移**，不再是"找不到源"。T3.7 从"定位 GLScene"改为"逐单元收敛 GLScene 残余 + 评估应用代码的复原形态"。

- 2026-10-30 依据 F205/F206：**LCL 0.9.28.3 已能自己编，逐字节路线的最关键前提成立；GLScene 反而成了新的缺口**。① SourceForge SVN 里找到 GLScene 的 LCL 分支（`branches/GLSceneLCL`，`Source/Platform/GLLCLViewer.pas`，2009/2010/2011 三个日期对应的修订 r4493/r5290/r5953 都有该单元）——本机 `svn.exe`（TortoiseSVN）直连可用，不必过 Cloudflare。② `svn.freepascal.org` 服务端 down，改走 GitLab 镜像：`fixes_0_9_28` 分支里 `lcl_version = '0.9.28.3'`（**没有 0.9.28.3 的标签**，只有 0.9.28 与 0.9.28.2），取 2009-12-01 的 f2e1062e，用 MSYS2 的 make + FPC 2.2.4 编通（26,693 行，5 s）。③ 用这套单元重测骨架：精确串 51.9% → **59.6%**、容忍重定位 73.5% → **79.5%**、`game.exe` 侧覆盖 23.4% → **51.0%**，局部 32 KB 桶达 **98.9% 逐位相同**；`0x521000` 的断崖边界一字不动 ⇒ **库代码可复现，剩余差异是单元集，不是 codegen 漂移**。④ GLScene 的 LCL 分支**用哪套 LCL 都编不过**：缺 `LCLType`（→`TCreateParams` 找不到）、补上后 `tagPAINTSTRUCT` vs `PAINTSTRUCT` 冲突、绕开 viewer 则 `GLCadencer` 的 published 字段报错 ⇒ 原版那棵树是打过补丁的变体，这是逐字节路线现在唯一的硬缺口。⑤ T3.7 更新：尺寸问题已由 F204 收口（应用 ≤390 KB / GLScene ≥195 KB），剩下的不是"量尺寸"而是"定位 GLScene 的变体"。

- 2026-10-30 依据 F202/F203：**L2-B 的前提勘误，并落地第一个可判真假的测量**。① F202 钉死工具链（`FPC 2.2.4 [2009/12/27]` + LCL 0.9.28.3 + GLScene 的 LCL 分支）；`requirements.md` 划掉 L2-B 的唯一理由"跨语言不可达（F01）"已被 F153 自己勘误 ⇒ **L2-B 由"明确不做"改为"未测量"**，需在 requirements 里改状态（等一个显式决定，不擅自改定稿文档）。② 实装工具链：用户装到 `C:\lazarus`（FPC **2009/10/25**、LCL **0.9.28.2**，与目标的 12/27 / 0.9.28.3 差两个月）。③ 用它对 `game.exe` 做首个测量（F203）：同包骨架 `.text` 1,124,176 B，其中 **73.5% 能按同一位移在原版里逐字节/容忍重定位地找回**（精确串 583,976 B，最长 7,799 B）⇒ **"构建日期不同 ⇒ 代码不可比"这个担心被实测否掉**，逐字节路线少了一个可能致命的前提风险。④ 仍缺的正是拆分项：`game.exe` 比 LCL-only 骨架多 640,400 B = **GLScene 族 + 应用代码**，需 GLScene 的 LCL 分支 2009 快照才能拆。⑤ 新增任务 T3.7（见下），并把 T3 的"C++ 仿写 vs FPC/LCL 继承"从无判据的 Open Question 改为由 T3.7 的残差数字驱动。⑥ 纪律：原版无 `.stab`（关调试编译），我们的构建默认带调试段，逐字节阶段必须 `-g- -Xs`。

- 2026-10-30 依据 F201：**T3.3 的规格提取开工——144 个绑定全部反编译，形态机械可生成**。新增 `tools/ida_lua_bindings.py`（在 ida MCP 的 `execute_python` 里跑）：按 `mapping/lua-bindings.csv` 的 `cfunc` 批量反编译，输出 `work/lua_bindings_decomp.json(.txt)`；判据 `rows=144 ok=144 fail=0`。结论：绑定 = `optnumber` 取参（`sub_596900`，返回 float）或 4 槽读取器（`sub_596C50`）→ 工厂（1..12 次）→ `lua_pushinteger`（67）/`lua_pushnumber`（30）；`return` 常量 1（65）/0（38）/变量（其余）⇒ **返回个数不能一律写 1**。**下一步**：逐函数参数表（索引在寄存器里，要读反汇编）→ 生成绑定注册表 + 144/144 自检；再按 b2 代理调用序做绑定语义的对拍。

- 2026-10-30 依据 F192/F200：**T3.5 菜单路径落地——宿主自己排版（查表），不再回放抓包的字形 quad**。新增 `src/host/font_table.{h,cpp}`：32 B/条（`u32 ch; f32 u0,v0,u1,v1; u32 w,h,flag`）+ `MismatchCount` 自检；`menu_layout` 的 `kGlyphU0..V1` 常量删除，改为 `PushText`（逐字查表、`advance==w`、整串仍一个 `MenuDraw` = 原版一个 `glBegin`）。判据：`draw_ab` 可见 **13/13 dx=dy=duv=0**（含 12 顶点文本）；`gl_init.log` 的 `font=258 font_mismatch=0` 把"表真的读了"写进日志。同状态像素对（两侧 `--mouse 900,700`）：mean 1.452 / >16 1.404% / 16×16 最大 195（= 光标）；文本区剩余 2.327 是采样级（draw 与纹理上传都逐位相同）。**剩**：名字来源接存档（T3.6）、空格/换行/对齐、关卡字体 `pt_sans.dat`。

- 2026-10-30 依据 F198/F199：**draw_ab 补覆盖 + 残差归因收敛（工具改动，无渲染代码改动）**。① `tools/draw_ab.py` 现在保留 alpha=0 的 draw 并逐 draw 比 caps/prim/blend/rgba：可见组判 PASS/FAIL，隐藏组默认只报（`--strict` 才判）。实测 `menu_draw.bin` vs `host_draws.bin`：可见 **13/13 全同（state-diffs=0）**、隐藏 **7/0** ⇒ 宿主**从不发 alpha=0 的 draw**（6 个悬停备用态 + 第二条用户名），像素上被 `SRC_ALPHA` 吞掉所以无差，但绘制列表不等价、旧门禁看不见；光标 caps 原版 29 / 宿主 31（多 `DEPTH_TEST`）。② 像素残差归因：F194② 报的"悬停 Play 区 205/256"实为**光标**（鼠标就停在按钮中心），掩掉后 maxwin 205→120、总面积只掉 0.04 个百分点；剩余紧凑块在设计 (827,645)/(658,530) 的**齿轮/常春藤贴花**，几何与状态全同 ⇒ 采样差异，与 F184 的过滤级结论一致 ⇒ T4.2 的像素判据必须单列光标区，不再把光标几何差异算进渲染残差。

- 2026-10-30 依据 F192–F195（探针轮，**无生产代码改动**）：把上一轮"剩余任务最佳实践"里三条只有 L1/文档级依据的建议先做成探针，两条被实测改写。① **T3.5 路线换掉**：菜单文字不是 GLScene 定宽渲染，而是 `gulim1.dat` 的 32 B/字记录表（字符码 + UV 矩形 + w/h + flag）驱动——抓到的 'o' quad 与表内字符 111 那条记录**逐位相同**（`advance==w==17`、行高 `==h==31`、UV 以 512 归一化），所以不存在"从 UV 间距反推步进"这回事，改成解析 `.dat`（F192）。② **T3.3 绑定纪律收紧、C++ 编译路线降级**：当前 `lua51` 是 C 编译（`ldo.obj` 引 `_longjmp`），Lua 错误不展开 C++ 栈；而 `lua.h` 没有 `extern "C"` 守卫，改 C++ 编译会改符号修饰，宿主与 `luac` 现有的 include 包装会链接失败 ⇒ 默认走"绑定体 POD-only + `lua_pcall`/`lua_gettop` 边界"，C++ 路只有当同步去掉 include 包装时才可选（F193）。③ **T4.2 判据换口径**：`orig_menu` vs `host_menu` 这一对不是同状态（原版悬停 Exit + 光标位置不同），其 mean/百分比不可当渲染证据；同状态对的差异是**紧凑块**（悬停 Play 的 16×16 窗口 205/256、光标区 120/256），不是散点滤波噪声 ⇒ 判据改成「同状态对 + 16×16 窗口最大计数」，并把悬停区/光标区列为待归因缺口（F194、F196）。④ **T4.9 仪器降级**：环回 A/A 自身 52.5% 样本不同（`max|Δ|=433`，与 A/B 同量级）⇒ loopback 只能证明波形等价，PCM 逐位必须抓 DLL 写进缓冲区的字节（`IDirectSoundBuffer8` 的 Lock/Unlock vtable hook，不拦 `CoCreateInstance`）（F195）。

- 2026-10-30 依据 F197（同一探针轮）：**F196 的 H2 被否**——悬停/空闲两帧 draw 集合完全相同（21 draw、纹理序一致），唯一差异是 tex 23/24 的 alpha 互斥翻转 ⇒ 悬停区的紧凑差异来自"同一批 draw 的合成/采样"，不是"多一层 glow"。顺带发现**门禁盲区**：`tools/draw_ab.py` 丢掉 alpha=0 的 draw 且不比 caps/prim/颜色（文件头明写），F190 的 13/13 因此不含这类差异 ⇒ T4.2 的下一刀是给 `draw_ab.py` 加 caps/blend 与 alpha 双份 draw 的分组比对（alpha=0 的 draw 保留但单独成组），再用 `HOST_DRAW_DUMP` 对同一帧核。

- 2026-10-30 依据 F191：**T3.3 第一切片落地——Lua 跑得起来、关卡清单读得出来**。vendor 官方 Lua 5.1.5（tar.gz md5 `2e115fe26e435e33b0d5c022e4490567`，未改动）→ `lua51` 静态库 + `luac`；`luac -p` 全量编译 pak 里的 **111 个脚本：111/111 通过**（证明方言就是 5.1，且宿主可自给自足，不依赖游戏目录 `lua51.dll`——两版该 DLL md5 不同，F12）。顺带修正 pak 解析：`lvl_info.lvl` 是**尾部附加记录**，`Pak::Find` 现在同查条目与尾部；宿主解析出 **52 关**（首关 Introduction、末关 The End），启动写 `host_data.log`（`entries=707 levels=52 lua_ok=111`）。**剩**：144 个绑定与执行语义（状态机/事件），另加 `tools/check_lua.py` 作为可重跑判据。

- 2026-10-30 依据 F188/F189/F190：**T3.2d 收口——菜单不再是抓包回放，是宿主代码现算**。① 先做了一条判据探测：带 GL 代理跑原版、intro 期间把客户区从 1018×739 改成 800×600，18–19 s 的菜单帧里 **21 个 draw 的 NDC bbox/UV 与基线逐字段相同**（只有跟随鼠标的光标变了）⇒ 布局是「固定设计空间 1018×739 逻辑像素」缩放出去，**不是**按客户区比例重排；元素在空间里还是纹理原始尺寸 1:1。这条直接决定实现形态（写设计像素常量即可，不用比例推导）。② `src/host/menu_layout.{h,cpp}`：矩形/UV/纹理 id/caps 表 + 鼠标 NDC 命中测试；悬停实测是**互斥**（基础项 alpha→0、hover→1，F189），按此实现；光标 32×32 居中（原版磁铁还会转，未归因）。③ 判据：新增 `tools/draw_ab.py` 比「宿主现算列表 vs 原版抓包」→ 13 个可见 draw **dx=dy=duv=0.000000**；`shot_window.py --mouse` 让两侧鼠标停同一设计像素后截屏对拍：空闲 **1.088/255**（>16 1.346%）、悬停 Play **1.085/255**，Play 区「悬停 vs 空闲」宿主差 6.66、原版 vs 宿主差 0.958 ⇒ 状态确实切了。`menu_draw.bin` 退役。**坑**：`--mouse` 必须在窗口摆位**之后**设置（窗口一挪，悬停位置就失效，第一版就因此测出「hover 没生效」的假阴性）。

- 2026-10-30 依据 F185/F186/F187：**T3.2c 收口 + 一个会毁文本的 primitive 错标**。① 纹理直读 pak：WIC 解码与原版 37 次 `glTexImage2D` 整块 CRC **37/37 逐字节相同**（含 5 张 JPG）⇒ 不 vendor libpng/libjpeg；宿主上传格式照抄 `GL_RGB8/GL_RGB`（JPG）与 `GL_RGBA8/GL_RGBA`，`menu_tex.bin` 退役，截屏 1.403→**1.375**。② 用户实测"主菜单 Welcome, ooo 渲染不同"⇒ 定位到 `tools/gl_drawlist.py` 的 `PRIMS` 表从 0x0004 起错位一格：原版 `glBegin` 实参是 **0x0007 = GL_QUADS**，被标成 TRIANGLE_FAN；用户名是一个 `glBegin/glEnd` 里的 **12 顶点 = 三连字**，按 fan 回放把三块连成蝴蝶结（`o>>`）。修 `PRIMS` + 绘制包升 `GLDRW02`（带 prim 原样回放）后名字区域 mean|Δ| **4.46→1.22**。③ 顺带修两个仪器坑：`shot_window.py` 抓屏前把窗口挪到 (0,0) 并置前（否则底部会拍到前台终端，曾误判成"渲染回归"）；`verify.py` 的 window 门禁失败时把完整字段表写 `work/gate_window_last.log`，`winprobe.py` 采样前等子窗口尺寸稳定（一次偶发 `diffs=2`，随后 20+ 次不复现）。**新增工具**：`tools/shotdiff.py`（逐像素 A/B：mean/p99/>16/分区域/平移扫描）、`tools/host_tex_ab.py`（宿主上传 CRC vs 原版日志）、`tools/gen_texture_table.py`。

- 2026-10-30 依据 F183/F184：**T3.2 里程碑 A 落地——宿主画出了主菜单，与原版逐像素基本一致**。新增 `src/host/gl_render.cpp`（WGL 上下文 + 两个二进制包加载器）与 `tools/gl_texpack.py`（37 张纹理 id ↔ pak 素材，CRC32 精确匹配，37/37）；`tools/gl_drawlist.py` 增加 `--pack` 与状态位。判据：原版两次截图差 **0.00**（菜单静止，A/A 地板），原版 vs 宿主 mean\|Δ\| **1.40/255**、p99 24、>16 像素 2.01%，九个平移里 (0,0) 最优 ⇒ 无整体偏移。两个坑：BLEND 在启动期常开（帧内没有 glEnable）⇒ caps 要从启动态继承，否则白屏；`GL_GENERATE_MIPMAP` 在本驱动兼容 profile 不生效 ⇒ 纹理不完整采样成白，改用 `gluBuild2DMipmaps`。**边界**：宿主吃预烘焙包，还没直接读 pak、也没自己算菜单布局 ⇒ 新增 T3.2c/T3.2d。

- 2026-10-30 依据 F181：**T3.2b 收口，渲染器对拍基准有了**。`tools/gl_drawlist.py` 把 `GLFFI02` 的一帧还原成 26–27 个 draw（纹理 id + 世界坐标 bbox + UV + 颜色），JSON 可导出；第 0/30/64 帧同构。过程中踩到 GLScene 的 HUD 细节：帧中途 `glMatrixMode(GL_PROJECTION)`+`PushMatrix`+`LoadIdentity` 换成单位投影、用像素空间画横幅 ⇒ **顶点永远乘 MODELVIEW（P·M·v）**，按"当前 mode"取矩阵会让 bbox 飞到 ±509。T3.2a/T3.2b 均完成，下一步是 T3.2 渲染器本体与 T3.3（pak+Lua）。

- 2026-10-30 依据 F180：**关卡数据面摊开了，顺带回答"能不能做关卡编辑器"**。关卡 = `lvl_info.lvl`（UTF-16LE 文本，`Caption`/`LevelFiles`/`LevelGroup`）+ 一组 Lua；零件是 Lua 工厂（116 个 `Add*`，内部只用 `Add_SimplePhysicObject`/`Attach_Shape*`/`Attach_SimpleGraphObject`/`Add_Joint*`/`Set_Phys*` 这些宿主原语，绑定共 144 个），行为是 `Attach_ScriptToObject` 注册的 Lua 事件回调（`OnMove`/`OnAddContact`/`OnPersistContact`/`OnRotate`）。⇒ 编辑器只需产出「清单 + Lua」，不动引擎；判据是原版能加载并推进存档；唯一缺口是 pak 回写（`tools/pak.py` 现在只有 parse/verify/extract）。这同时收敛了 T3.3 的范围：宿主必须提供的不是"零件逻辑"，而是那 144 个绑定 + 每步物理。

- 2026-10-30 依据 F179：**GL 代理升到 `GLFFI02`（payload + 时间窗），相机与变换读出来了**。每调用多记 12 个 dword + `args[0]/args[1]/args[8]` 三块 192 B，`GLPROXY_T0/T1` 只记 27–28 s 那一段（58,600 条 / 38.2 MB，比全量 8 MB/s 便宜两个数量级）。实测：`glOrtho(-26.862,26.862,-19.5,19.5,0.371,100.371)`（视野 53.72×39.0，比例 = 客户区 1018/739）、相机 `glTranslated(3,-3,-5)`、逐 sprite 的变换走 `glMultMatrixf`（含 (510,185,0) 这类局部平移）、纹理 id 1..37。`tools/gl_ffi.py` 兼容 v01/v02 并新增 `window` 子命令（按时间窗看调用序、解矩阵/颜色/UV/`glTexImage2D`）。T3.2b 只剩「sprite 列表抽取」。

- 2026-10-30 依据 F175–F178：**T3.2a（GL 调用面侦察）落地，并顺手推翻了一条既定结论**。仪器：`src/glproxy/`（`opengl32.dll` 代理，368 个 naked 桩全转发给改名的 `opengl32_orig.dll`，生成器 `tools/gen_proxy.py --library opengl32 --prefix ""`）+ `tools/gl_ffi.py`（`stats`/`frames`/`frame`/`init`/`names`）。透明性（F176）：用**无代理**画面建的状态锚点判 `menu` 于 16.7 s（F169 无代理 16.5 s），菜单/关卡截图正常，40 s 无崩溃。三条结论：① **渲染节奏**（F177）——加载/intro 是 2,100–3,100 swap/s 的忙循环，主菜单与关卡内恒 61–65 swap/s ≈ 15.6 ms/帧；静止画面只是像素不变，循环一直在跑 ⇒ **F168 的"按需重绘、有失效才画"作废**，T3.2 改成固定 ~15.6 ms 循环；② **调用面**（F178）——368 个导出只用 65–67 个，逐 sprite 立即模式（一帧 896 次调用：25 个 `glBegin`、100 顶点、61 次 `glMultMatrixf`、24 次 `glBindTexture`），纹理只在启动期上传 37 张；③ **覆盖边界**——每调用只存 6 个 dword（`glOrtho` 的 6 个 double 只覆盖 3 个），矩阵/纹素指针内容看不到，经 `wglGetProcAddress` 拿到的 ARB 指针直连驱动（`.names` 256 个名字只证明被请求过）。新增 T3.2b 补 payload 解码；`docs/facts.md` 的 F168 行按规则划掉改状态，勘误写进 F177。

- 2026-10-30 依据 F175：**M3 的下一步是 T3.2a（GL 调用面侦察），不是先写渲染器**。理由：T3.2/T3.4/T3.5 都要先知道原版"画一帧到底调了什么"，而现在只有 F03 的静态导入项列表（53+33），没有频率、顺序、参数与是否用扩展。前置探测已做完：`opengl32` 不在 KnownDLLs（与 F147 的 dsound 情形相反），所以文件代理这条路可用；`SwapBuffers`/`ChoosePixelFormat`/`SetPixelFormat` 在 `gdi32`（KnownDLL），帧边界只能由 `gl*` 的 QPC 时间戳聚簇或 `glClear` 推断。新增 F176（待证：代理透明度与可记录性），探针一次给出可证伪的结论：游戏能否照常到 menu、日志是否成帧、`wglGetProcAddress` 请求了哪些名字。

- 2026-10-30 依据 F169–F174：**"测试速度"这条线落地了一整套无人值守能力**。新增仪器与驱动：`tools/uistate.py`（界面状态机，loading/intro/menu 三个锚点，过渡帧返回 unknown，16.5 s 判出 menu）、`tools/uitemplate.py`（无 OpenCV 的 NCC 模板定位，`--selftest` 自证）、`tools/e2e_tutorial.py`（等 menu → 真实输入点 Play → 循环点气泡 X 直到**存档推进** → 默认杀进程退出）、`tools/e2e_record.py`（自走跑关同时挂 b2 代理录制，40.75 s 出 8.39 MB 日志并 `gate.py` PASS）。`tools/verify.py` 增加 `--e2e` 门禁（自动备份/还原存档）。三条硬结论：① `Play` 落点由存档 `LastCompleteLevel` 决定（=51 直接进结局页，F171）；② 点击坐标必须按**抓图的物理像素**算，游戏是 DPI-unaware 逻辑像素（F172，踩过一次）；③ 游戏内正常退出会 `ShellExecuteA` 弹网页，**默认改杀进程**（F173）。次要修复：`replay.py`/`record.py` 的 Pillow 改延迟导入，headless 门禁不再因缺 PIL 起不来（F174）。

- 2026-10-30 依据 F168：**"tick 间隔"这个问题有了结论，且结论是"没有固定 tick"**。新仪器 `tools/frame_probe.py`（屏幕小块 100 Hz 采样 + 逐帧字节比对）实测：主菜单 17 次/秒画面变化（间隔成簇 ⇒ 局部失效重绘）、静止关卡 0 次/秒，与 F156 的空闲 CPU 0.0% 一致 ⇒ **渲染是按需重绘**，宿主不能实现成固定 60 fps 循环。x32dbg 路线放弃：`SetTimer` 断点被 Sogou/Intel 驱动的 DLL 入口事件反复打断（每次新模块加载都停一次），成本高于收益。剩下未测的只有"运动中（拖拽/物理未静止）的重绘率"，交给 T3.2 的 GL 代理或人工拖拽时采样。

- 2026-10-30 依据 F167：**全屏分支参数实测完毕**（`FullScreen="1"` → `style=0x970A0000` 无边框最大化、`exstyle=0x8` 置顶、窗口=整屏 1707×960、`showCmd=3`、`normal_rect` 恰好等于 DFM 的 1072×539），切回窗口化后参数与 F154 逐字相同、无残留。F157 的"矛盾点"同时关闭：**DFM 本身就是全屏形态**，窗口化是启动期按配置改写的结果。全屏的宿主实现并入 T3.6（配置），T3.1 只剩输入日志→场景接线（属 T3.4）。

- 2026-10-30 依据 F166（勘误 F163）：**10px 边框偏差的根因是 PE 头 `MajorSubsystemVersion`**。Windows 对 subsystem<6.0 的映像用旧式非客户区度量（3/侧 + 23 标题、无 DWM padding），原版 `game.exe` 是 4.0、我们的默认构建是 6.0。A/B（同一二进制只改 PE 头）确认 5.01 即可复现原版度量；MSVC 拒收 4.0（LNK4010）。修法：`set_target_properties(host PROPERTIES LINK_FLAGS "/SUBSYSTEM:WINDOWS,5.01")`，并把 `main.cpp` 的尺寸逻辑还原成 LCL 语义（客户区 1018×739 → `AdjustWindowRectEx` → 外框 1024×768 → 居中），删掉为绕开偏差而写的 `kRef*` 常量。门禁 `tools/wincompare.py` 由 14 项判定升到 **15 项（含 `window_rect`）`diffs=0`**；T3.1 剩余只有"输入接场景"与"全屏分支参数"。

- 2026-10-30 依据 F162/F163：**T3.1 宿主脚手架落地**。`src/host/main.cpp` 按 F154/F155/F156/F158 复刻窗口：类名 `Window`（CS_DBLCLKS、hbrBackground=NULL、IDC_ARROW、MAINICON）、`style=0x96CA0000`、`exstyle=0x100`、DPI unaware、同一类名建视口子窗口（靠 `CREATESTRUCTW.hwndParent` 区分窗体/视口，否则 WM_CREATE 递归建子窗）、主循环 `PeekMessage` + `MsgWaitForMultipleObjects`。**验收 14/14 字段一致**（`tools/wincompare.py`：title/class/style/exstyle/client/viewer 全部相同）。两处已知偏差与结论：① 外框比原版厚 10px（原版边框 3/26，我们 8/31，OS 给我们加了 DWM padding），按**客户区**对齐后视口逐像素相同（F163）；② 菜单/按钮只能靠真实输入驱动，`PostMessage` 合成消息无效（F162）。新增仪器：`tools/winprobe.py`（窗口参数探针）、`tools/wincompare.py`（原版 vs 自建对拍门禁）。

- 2026-10-30 依据 F153–F160：**T3.1 的前置探测做完了，依据从 F01（PE 解剖）换成实测值**。新增 8 条台账：宿主框架是 **Lazarus/LCL 而非 Delphi/VCL**（F153，勘误 F01）；窗口化主窗口 1024×768 外框 / 1018×739 客户区 / `style=0x96CA0000` / **DPI unaware** / 桌面居中（F154）；窗口类由 LCL 通用注册函数建：类名 `Window`、`CS_DBLCLKS`、`hbrBackground=0`、`IDC_ARROW`、`MAINICON`（F155）；主循环 PeekMessage + `MsgWaitForMultipleObjects`（导入无 `GetMessage`），空闲 CPU 0.0%（F156）；Form1 的 DFM 是 `bsNone`+`wsMaximized` 且无子组件，与运行时工具窗矛盾（F157，全屏分支待证）；窗体下只有一个填满客户区的 GL 子窗口（F158）；输入无 DirectInput，鼠标走消息 + 键盘轮询，Lua 只有 `Get_MousePosition`（F159）；`game.exe` 疑似单实例（F160 待证，自动化前提）。**由此新增 M3 的 Open Question：宿主用 C++ 仿写 LCL 语义，还是用 Free Pascal + LCL 直接继承**——T3.1 开工前需要拍板。另：自动化驱动脚本的点击时机按用户实测改为"启动期 CPU 降到 <5% 后再等 6 s"，早点点到的是 intro/splash 而非主菜单。

- 2026-10-30 依据 F131–F152：**plan/todo 任务状态同步**。T2.4（含 a–d）标完成；T2.5 改为「实现与输出对拍已完成，只剩 PCM 逐位」；T4.3 改为「音频 diff 输出层」并标完成；T4.7（dist_probe 路线）标为作废并注明 F112/F122；新增 T4.8（Good Shot 残余 1 ULP）与 T4.9（PCM 逐位，阻塞）。todo 按里程碑重排，`[x]` 只增不减。

- 2026-10-30 依据 F152：**第二批九关实录**——1951 次调用，`Sample_Pause`（1032 次，集中在 sample `0x10019` 的暂停/恢复）与 `Channel_Status`（8 次）首次在游戏内出现 ⇒ 游戏内覆盖 16/17，唯一没用到的 `Sample_LoadFile` 由探针覆盖。9 关没有引入任何新接口，17 个导入的实机覆盖基本到顶。

- 2026-10-30 依据 F151：**多关实录并入契约**——四关同进程 906 次调用，接口仍是 17 个导入的子集（`Channel_Pause` 首次出现），关卡音乐用 `loop=1, group=1` 的 4 个 sample id 可对上 4 个关卡。游戏内累计覆盖 14/17，剩余 3 个（`Channel_Status`/`Sample_LoadFile`/`Sample_Pause`）由探针覆盖。

- 2026-10-30 依据 F150：**整段关卡音频对拍通过**。代理加 `SQUALL_FORCE_DEVICE=<n>`（Init 后强制切设备，宿主不调这个导出，仅测量用），把游戏音频路由到 VB-Cable 录制：原版 vs 自建 55 s 录音逐秒 corr 0.9998–0.9999，恒定 9 ms 启动偏移，RMS 差 <1%。⇒ Squall 侧除了 PCM 逐位（F134）之外，行为等价已有三层证据：导出/契约、调用序、输出波形。

- 2026-10-30 依据 F148/F149：**抓到并修掉第三处源码漂移（音量曲线）**。原版 2006 是每点 1 dB 的线性映射（99→-0.9 dB、80→-19.9、60→-39.9），上游 v1.48 是 log10 曲线 ⇒ 我们在非满音量下最多响 29 dB。修后同法复测四个点全在 0.1 dB 内，20 步契约与 35 个 OGG 元数据回归仍 0 分歧。同时把 VB-Cable 环回 A/B 跑通（`tools/audio_capture.py` + `tools/audio_diff.py`）：正弦 `corr=0.9999996`、OGG `corr=0.99992`/RMS 差 -90 dB。**仪器要求**：录制时不能有别的进程占设备（游戏开着录那次原版自己只有 0.60）。

- 2026-10-30 依据 F146/F147：**通关音效段已录到；PCM 三条路线全部否掉**。用户手动通关 Good Shot 并正常退出，代理录到 311 次调用（`Sample_PlayEx` 69 / `Channel_Start` 61 / `Channel_SetVolume` 61 / 其余见 F146），接口集合仍是 17 个导入的子集 ⇒ 通关音效无新增 API 面。想拿原版 PCM 的三条路都失败：换 `dsound.dll`（原版走 `CoCreateInstance`，ole32 是 KnownDLL）、在代理里钩 `CoCreateInstance`（`PlayEx` 变 -13）、日志重放（原版自检就有 174/311 差异，声道分配依赖实时状态）。已有仪器与结论按「地板过大」处理，相关文件已删；F134（PCM 逐位）状态仍是 `待证`，下一步要上进程内 hook（Detours 级）或改用 WASAPI 环回。

- 2026-10-30 依据 F144/F145：**T2.4d 收口**——新增 `tools/squall_contract.py`（固定 20 步脚本覆盖 17 个宿主导入），原版 vs 自建 `diffs=0`；顺带确认两个「反直觉但一致」的上游行为（PREPARED 通道 `Channel_Pause` 返回 -13；先内存样本再 `LoadFile` 会因 `strcmp(NULL)` 让两个 DLL 都崩）。整机 3 分钟静置不崩（F145）。至此 Squall 侧：导出 99/99、17 个导入的调用序与返回值全对齐、优雅退出路径对齐；唯一未闭合的是 **PCM 逐位一致（F134）**，需要 DirectSound 层抓包才能验。

- 2026-10-30 依据 F143：**优雅退出路径闭合**——脚本走 Main menu → Exit → Yes，原版与自建各 127 次调用、254 条事件 0 分歧，`game.exe` 自行退出（非 TerminateProcess）。这条覆盖了 T2.4d 里的 `SQUALL_Free`、`Sample_Stop`、`Sample_Unload`、`UnloadAll`；剩下未触发的是 `Channel_Pause/SetVolume/Start/Status` 与 `Sample_LoadFile/Pause`。同时修 `tools/squall_ab.py`：`void` 导出（Free/Unload/UnloadAll/SetWorker）不再比较 EAX，否则会产生假差异。

- 2026-10-30 依据 F141/F142：**整机冒烟通过 + 全量 OGG 元数据一致**。把自建 `b2Physics.dll` 与 `Squall.dll` 同时装进游戏：进 tutorial 关、跑 ~90 s、推进到 Congratulations 结局页，进程存活且模块表确认加载的是 `work/integration` 下与 `build/Release` 逐字节相同的两个 DLL（md5 核对）。新增 `tools/squall_decode_ab.py`：35 个 pak 内 OGG 的 `length/ms/hz/sid` 两侧 `diffs=0`（覆盖边界：不比 PCM，F134 仍未闭合）。新增 T2.6a（已完成）/T2.6b（长时+优雅退出）。

- 2026-10-30 依据 F140：**T2.4d 的接口集合更正**——脚本化进关（菜单→Play→18 s）后原版与自建各 51 次调用、102 条事件 **0 分歧**；实际用到 7 个接口，`Sample_Play3D*`/`Channel_Set3DPosition`/`Listener_*` 根本不在宿主导入表里（F131），那 82 个导出对本游戏是死码。T2.4d 缩到剩余未触发的 10 个（含只有优雅退出才调的 `SQUALL_Free`）。

- 2026-10-30 依据 F138/F139：**T2.4c 仪器落地 + 两处漂移修完**。`src/squallproxy/`（99 个 naked 桩，`Squall_orig.dll` 尾跳，日志 `SQFFI01`）+ `tools/squall_ffi.py`（解析）+ `tools/squall_ab.py`（结构对拍）+ `tools/gen_proxy.py` 参数化（b2/Squall 共用）。实抓宿主启动路径：44 次调用（`Init` → 35×`LoadFromMemory` → 4×`ChannelGroup_SetVolume` → 2×`Sample_PlayEx` → 2×`ChannelGroup_Pause`）；自建 DLL 复原后 88 条事件 **0 分歧**。期间修掉第二处源码漂移：`volume_table[100]` 越界（原版读到 0 dB、我们读到垃圾 → `PlayEx=-13`），已按 `altered (F138)` 扩到 101。**教训：代理日志必须逐条 WriteFile**，TerminateProcess 会吞掉用户态缓冲（首轮 25 秒日志 0 字节）。新增 T2.4d（关卡内剩余 12 个导入）。
- 2026-10-30 依据 F136/F137：**T2.4a 完成**——`cmake --build build --config Release --target squall` 产出 `build/Release/Squall.dll`（VS18 x86、静态 CRT），导出 `99/99` 序号全中，导入集合与原版相同；`SQUALL_Init`/`GetNumDevice`/`GetDeviceName`/`Sample_LoadFromMemory`/`GetFileLength(Ms)`/`GetFileFrequency` 在两份 pak 内 OGG 上与 oracle 逐项相同。同时抓到**第一处源码漂移**：上游 `SQUALL_GetNumDevice` 是空指针虚调用，自建 DLL 崩、原版返回 4，已按 `altered (F136)` 修好 ⇒ T2.4 纪律：上游源码只是起点，宿主用到的 17 个导出必须逐个对拍。构建适配：SDK `dsound.h`（不用 `ext/` 那份精简头）、`DIRECTSOUND_VERSION=0x0800`、链 `dxguid`；ogg/vorbis 源码直编（`squall_codec`），无外部解码 DLL。
- 2026-10-30 依据 F131/F132/F133/F134：**T2.4/T2.5 路线更换**——从"逆向 Squall.dll"改为"上游 MIT 源码 + A/B 对拍"。依据：导出名 99/99 与上游 `DLL_API` 定义逐一致、`SquallHiddenWindow` 字面同在、二进制只有 5 个系统 DLL 依赖。`vendor/squall` 已按 pin 入库（HEAD `20988426`），`mapping/squall-exports.csv`（99 行）成为导出契约单一事实源，`tools/check_exports.py` 改为表头驱动（默认仍 b2，`DllEntryPoint` 行跳过）。新增 T2.4a/b/c；风险单列为 F134（libvorbis 版本未知，待证）。物理侧不重开：`Good Shot!` 的 4,825 已是 1 ULP 级、`Looking for Keys` 5,297 = A/A 地板（F125/F128）。

- 2026-10-29 依据 F122：**B1 根因确定并修**——`b2Distance` 的早退缺绝对阈值 `vSqr < FLT_EPSILON²`；补上后 On a Leash `bad 19,614/首发 420` → `bad 0/首发 681`（A/A 地板），three coins（0/1009）与 looking for keys（5,297/1,996）逐项不变。vendor 已改并加 altered 注释，正在全量复跑。

- 2026-10-29 依据 F121：`DistanceGeneric` 逐迭代 trace 就绪（早退 14,065 / 三角形包含 284 / 跑满 0）；缺 TOI→距离的调用号关联，下一步把 `g_gjkCall` 外置并在 TOI 的 `b0` 行打印。

- 2026-10-29 依据 F120：几何真值是"包含"（真实距离 0），我们与原始都因早退给出非零/无碰撞，差异是**早退条件不同**而非精度。下一步：`DistanceGeneric` 逐迭代 trace + Python 枚举变体复现原版行为。

- 2026-10-29 依据 F119：探针打印 iter0 后，差异落到 `b2Distance` 给出的 `normal`（我们 `(-0.973,0.231)`、bound=+0.051 → 推进；原版必须 ≤0 才能返回 1.0，反推 normal ≈ `(0.59,0.81)`）。TOI 只是放大器。下一步：用可靠几何实现（或我们 DLL 的 `b2Distance` 返回的 p1/p2）确认哪侧 normal 是真实最近特征。

- 2026-10-29 依据 F117/F118：**隔离复现成功**——用第 420 步 TOI 的入口 sweep 直调两边，原版 `1.0`、我们 `0.674`；按 k 缩放位移时原版恒 `1.0`、我们与 k 成反比（固定碰撞点）。`Support` 换世界空间无效（F118）。下一步：在我们的探针构建里打印 iter0 的 `normal / approachVelocityBound / r1,r2`，判定是 `normal` 还是 `GetSweepRadius` 让 bound 反号。

- 2026-10-29 依据 F115/F116：新建接触的 `m_toi` 是未初始化垃圾 ⇒ 用 `m_toi` 判 TOI 的 F108 口径作废；改用只由真实推进写过的 `sweep.t0`（及 c0/c/a0/a）重扫，首个分歧确认为 **step 420**（body 0x2efd5284，0.0 vs 0.67421）。T4.7 下一步：在我们的探针构建里把"返回 0.674 的那次 TOI 调用"的 sweep 原始字节打出来，与接触转储的同名字段对齐比较。

- 2026-10-29 依据 F114：新增 `tools/toi_call.py`（直接调两边 `b2TimeOfImpact`）；用记录到的 419 步 sweep 对调，**两边都给 1.0**，与"原版 m_toi=0"矛盾 ⇒ 原版的 0 不能由 TOI 计算解释，怀疑点转向接触 `m_flags` 的未初始化/跳过路径。T4.7 下一步：造"刚创建未步进"的接触读两边 `m_flags/m_toi` 初值。

- 2026-10-29 依据 F112/F113：F111 的"原版误判相交"作废（`0x1000A040` 是自定义寄存器约定，cdecl 调用拿到垃圾）；改做端到端观测（`work/toi_scan.py`：受控 2-body + step + 读 `m_toi`），结论是**两边在相同输入下完全一致**（切换点同为 0.009），⇒ 419 步的分歧来自尚未复现的上下文状态（sweep/t0 或热启动历史），不是距离代码。T4.7 改为：把 419 步的 `sweep c0/a0/c/a` 直接写进受控 world 再 step。

- 2026-10-29 依据 F111：新增 `tools/dist_probe.py`（直接 ctypes 调 DLL 内部未导出函数，不需要调试器）；最小复现证明**原版** `b2Distance` 对实际分离 ~0.09 的两盒返回 0，我们返回 0.0924 ⇒ 目标是复刻原版的误判，而不是修我们的 GJK；F108 的表述由 F111 纠正。T4.7 改为：扫位姿找原版误判边界 + 调两边内部 `Support`/`ProcessThree` 定位误判步骤。

- 2026-10-29 依据 F109/F110：IDA 侧把原版距离分派读通（circle 情形 `0x10009980`/`0x10009B90` 读半径减 `toiSlop`；poly-poly 泛型 `0x1000AB00` 与我们源码逐句同构，差别只在 `Support`）；但探针的 `iter=0 d=0.008012` 与独立计算的首顶点距离 6.717 矛盾 → **归因未闭合，暂不改代码**，T4.7 增加一条前置：在 TOI 内打印 `GetXForm(0)` 与 `x1/x2/w1/w2`，把日志行与调用钉死。

- 2026-10-29 依据 F108：B1 收到一个具体缺陷——我们的 GJK 对"重叠 0.110259"的一对盒子返回 0.008（原版判 0），`m_toi` 全量对照显示前 418 步逐对相同、第 419 步首次不同；接触顺序/几何/位姿/编译器/常量均已排除。T4.7 改成对读原版 `ProcessTwo/ProcessThree` 与 `Support`，并记下四个反汇编锚点。

- 2026-10-29 依据 F107：B1 再收敛一层——插桩（独立 vendor 副本 `work/vendor_probe` + 独立构建 `work/build_probe`）拿到触发 TOI 的接触对与数值（我们 t=0 `b2Distance=0.0080` → 5 次推进 → `alpha=0.674`；原版同一步 `m_toi=0`），形状几何与位姿逐位相同、VC9 与 VS18 同结论 ⇒ 差异被限定在 `b2TimeOfImpact`/`b2Distance`；T4.7 改成带锚点（RVA + map 符号）的指令级比对。

- 2026-10-29 依据 F102/F103/F104：B1 的因果链由"broadphase 提前销毁接触"更正为"**多跑了一次 TOI 子步**"（F94 勘误）——接触集合、manifold、关节冲量在分叉前逐位相同，第 420 步我方 `sweep.t0=0.674` 而原版为 0；`B2_NO_TOI` 开关证明原版确实在用 TOI（关掉后首发分歧回到第 1 步）。新增仪器：replay 的内存级 contact/body/joint 转储（F103 含全部实测偏移）。新增 T4.7（TOI 函数级反汇编比对）。

- 2026-10-29 依据 F101：`Get the Map`（`rec_20261029_183833`）与 `The First Totem`（`rec_20261029_183942`）v02 重录完成，两关 `bodies_bad = 0`；T4.6 勾选，覆盖率缺口关闭 → **52 关全部有可判定语料**。

- 2026-10-29 依据 F98/F99/F100：批量重放改由 `tools/sweep.py` 承担（`gate_all.py` 依赖已删除的 `events.jsonl`，F70 之后不再用于批量）；判据产物必须自带构建指纹，v01 日志由工具层拒收（F87 从纪律变成代码）；`docs/levels.md` 的表格改为 `tools/report_sweep.py --write` 生成的标记块，录制↔关卡映射移到 `mapping/levels.csv`。T2.3 勾选完成；新增 T4.6（2 关需重录）。

- 2026-10-28 依据 F05/F17/F20：Pak v0.2 记录布局闭环（24 B 定长 + trailer），T0.1/T1.1/T1.2 完成；`tools/pak.py` 已可 verify/extract 两版。

- 2026-10-28 初版：对齐=行为等价+函数映射；基准=GameTop；范围=宿主 + 两个自有 DLL。
- 2026-10-29 依据 F130：仓库追踪的文本换行统一到 **CRLF**（38 个 LF/混合文件改写 + 新增 `.gitattributes` 的 `* -text`，禁止 git 做换行归一化，blob 字节即工作树字节）。验收：`b2World.cpp` 纯 LF / 纯 CRLF 两版在 `/Brepro` 下 `.obj` 逐位相同；重建后 `rec_20261029_183942` 仍 `bodies_bad=0 mismatches=0`；导出表 87/87。仓库保养，不涉及行为对齐口径。
- 2026-10-31 依据 F260/F261/F262（**T6.3/b1 采集链路定型**）：headless 的 MCP 插件写操作全静默失效（挂断点/暂停/日志命令），改走**离线模块库注入**——`tools/moduledb.py` 读写 `headless/db/<module>.dd32`（LZ4 legacy 帧 + JSON；RVA、oldbytes、`logText`、`"commandText":"run"`），采集期间不加载插件，命中即写 stdout 并自动继续。Introduction 已采 25/25 对象（`work/hostcapture_intro2.*`：tag/句柄/vtable/父指针/名字）。下一步：同一断点库保持挂载，进关卡即记录，按关卡切分后与 `work/lua_probe/lvlNN.jsonl` 对拍。
- 2026-10-31 依据 F263（**自动点击可用，F257/F259 勘误**）：点 Play 的真因是坐标按 **1.5×** 缩放（游戏把鼠标逻辑坐标算成 客户区/1.5）＋按下需保持 **~150 ms**（瞬时 down/up 被按帧轮询漏掉），与调试器 attach 无关。`tools/click_play.py` 在 headless attach + 62 断点会话下点一次即 25/25 `Add_*` 命中（`work/logtext6.log`）。⇒ b1 采集不再需要人工 Play。
