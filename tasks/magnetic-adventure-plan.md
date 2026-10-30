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

- [ ] T3.1 Win32 窗口/消息/输入（参数对照原 exe） 依据：F153–F159、F164、F166、F167（**脚手架已落地并通过窗口门禁**：`src/host/main.cpp` + CMake target `host`→`build/Release/magnethost.exe`，`tools/wincompare.py` 报 `fields=15 diffs=0`，外框/边框厚度也逐字相同（F166：PE 子系统版本 5.01）；全屏分支参数已实测（F167：`bsNone`+`wsMaximized`+`WS_EX_TOPMOST`，整屏无边框，实现留给 T3.6 接配置）；剩余：输入分发只做了消息日志，接场景属 T3.4）
- [ ] T3.2 OpenGL 上下文 + GLScene 等价渲染层 依据：F03、F158、F177、F178（**渲染循环已实测**：加载/intro 是 2,100–3,100 swap/s 的忙循环，主菜单与关卡内恒 61–65 swap/s ≈ **15.6 ms/帧**（F177，勘误 F168 的"按需重绘"）；一帧 ≈ 870–900 次调用、逐 sprite 立即模式（25 个 quad、100 顶点、61 次 `glMultMatrixf`、24 次 `glBindTexture`，F178）⇒ 宿主实现成固定 ~15.6 ms 循环，不是"有失效才画"）
- [x] T3.2a GL 调用面侦察：`opengl32.dll` 代理（368 导出全转发）记录名称/QPC 时间戳/栈上 6 个实参 依据：F03、F158、F175、F176（**已落地**：`src/glproxy/`（368/368 导出）+ `tools/gl_ffi.py`（`stats`/`frames`/`frame`/`init`/`names`）；透明性已证：无代理锚点判 `menu` 于 16.7 s（F169 无代理 16.5 s）、40 s 无崩溃、截图菜单/关卡正常（F176）；产出 F177/F178）
- [x] T3.2b GL payload 解码 + 绘制列表 依据：F178、F179、F181（**全部落地**：`GLFFI02` payload + 时间窗（F179）；`tools/gl_drawlist.py` 把一帧还原成 26–27 个 draw（纹理 id + 世界坐标 + UV + 颜色），JSON 可导出。坑：顶点永远乘 MODELVIEW（P·M·v），GLScene 的 HUD 会在帧中途把投影换成单位阵用像素空间画横幅，乘错"当前 mode"会让 bbox 飞到 ±509。**这就是渲染器的对拍基准**：逐 draw 比 bbox/UV/纹理 id）
- [ ] T3.3 pak 加载 + Lua 状态机 + 绑定 API 依据：F04、F180（**关卡数据面已摊开**：`lvl_info.lvl` 是 UTF-16LE 文本清单（`Caption`/`LevelFiles`/`LevelGroup`），零件与行为全在 Lua——116 个 `Add*` 工厂、144 个绑定、事件走 `Attach_ScriptToObject`（`OnMove`/`OnAddContact`/`OnPersistContact`/`OnRotate`）。⇒ **关卡编辑器的可行形态 = 产出「清单 + Lua」**，不改引擎；判据用原版加载（能过门禁/推进存档）；缺 pak 回写（`tools/pak.py` 只读））
- [ ] T3.4 场景/实体/物理/音频接线 依据：F03、F06、F07、F169、F171、F177、F179（**初始化顺序是契约**：loading/intro/menu 三段的内容与循环节奏都不同（F169、F177），37 张纹理在启动期一次性上传（F179），`Play` 落点还依赖存档 `LastCompleteLevel`（F171）⇒ 宿主不能"直接构造关卡场景"冷启动，必须按原顺序跑；状态判定用 `uistate` 像素锚点，不用定时点击（F172 的教训：intro 占 12.5 s，定时点击必落空））
- [ ] T3.5 文本渲染路径 依据：F11
- [ ] T3.6 配置/存档写入（`cfg.ini` 等） 依据：F01

## M4 行为对齐验收

- [ ] T4.1 确定性输入回放 harness 依据：F03、F169、F172、F174（**自动化驱动已可用**：`uistate` 状态机 + `uitemplate` 模板定位 + `e2e_tutorial` 无人值守跑关（38 s）+ `e2e_record` 自走录制并直接过门禁（40 s）。剩余：输入**回放**（按键/鼠标事件逐帧记录再重放）尚未做——现在是脚本化操作，同一脚本两次运行日志字节数相同（F174），但还没到「录一次输入、任意次重放」）
- [ ] T4.2 GL 调用序列 diff + 像素 diff 依据：F03
- [x] T4.3 音频 diff（输出层）：环回 A/B 已跑通，逐秒 corr 0.9998–0.9999；PCM 逐位不可达见 T4.9 依据：F06、F149、F150
- [ ] T4.4 存档字节 diff 依据：F01
- [ ] T4.5 映射覆盖率报告 依据：F01
- [ ] T4.10 宿主 exe 的 A/B（exe 不能像 DLL 那样替换，改为"同脚本串行跑 + 在边界对拍"） 依据：F154、F166、F172、F174（四层判据，从便宜到贵：① 窗口层已可用——`tools/wincompare.py` 本身就是 exe-vs-exe，15 字段 diffs=0；② **DLL 调用层**：代理 DLL 与宿主无关，同一份 b2Physics/Squall 代理分别装进原版目录与自建宿主目录，两边跑同一脚本，用 `squall_ab` 的结构对拍比"调用序列/返回值"；③ 状态层：跑完 diff 存档（`tools/profile.py` 解码后逐键比）；④ 输出层：固定尺寸/DPI 的像素 diff 与环回音频 diff（只能给输出等价）。三个约束：单实例→串行且跑前 kill 干净；存档共享→每次备份复原；输入一致性→复用 `e2e_tutorial` 的脚本（F174 已证两次运行日志字节数相同））
- [x] T4.6 重录 `Get the Map` / `The First Totem`（现只剩 v01 日志，不可作判据） 依据：F99、F100（已完成，F101）
- [ ] T4.7 （路线已作废）用 `tools/dist_probe.py` 沿法线平移 B 扫出原版 `b2Distance` 误判为 0 的边界，并调两边内部 `Support`(`0x100144C0`)/`ProcessTwo`(`0x10009160`)/`ProcessThree`(`0x100092F0`) 定位误判发生在哪一步；反汇编锚点：poly-poly 泛型 `0x1000AB00`/`0x1000A5E0`、`b2TimeOfImpact=0x10018B20`、`b2_World_Step=0x10001490` 依据：F102、F107、F108（dist_probe 的 cdecl 调用约定错误见 F112；真实根因是 b2Distance 早退阈值，F122 已修）
- [ ] T4.8 残余 1 ULP：`Good Shot!` 的 `lvy`（首发 4847、bad 4,825，该录制 A/A 地板 0） 依据：F128
- [ ] T4.9 PCM 逐位（阻塞：dsound 文件代理 / 代理内 IAT / 日志重放三条路线均否） 依据：F134、F147

## M5 汉化目标

- [ ] T5.1 汉化版资源作为交付资产（不改原 pak） 依据：F08
- [ ] T5.2 中文文本/字形核对 依据：F08、F11
- [ ] T5.3 交付包形态（`cfg.ini`、`images/`、`Uninstall/`） 依据：F09

## 变更记录

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
