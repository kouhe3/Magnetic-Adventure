# 交接文档 — Magnetic Adventure 复刻

> 写给下一个接手的 agent，自包含：读这一份 + 三份文档就能开工。
> 写于 2026-10-30（**L2-B 工具链考古那一轮之后**），最后更新 **2026-11-03**（§0 追加 **T6.4b-x `B2CI_FAKE_MAGNET`**、力律勘误 F386 与 **测试关卡/私有桌面 F387/F388**；此前 T6.4a-r-2f level 4 动态项、T6.4b 鼠标拖拽首段与 CI mover 两段通关、10-function matching pilot、五批叶子/带 call 对拍、T6.3d 收口 50/2/0 仍在下方）。`work` 分支；台账到 **F388**。

## 0. 一句话现状

**2026-10-31 更新**：T6.3/b0 完成（F249/F250）——Lua 的 `Add_*` 句柄是**堆对象指针**（工厂返回 `sub_583300`/`sub_58C500` 对象，`push eax; lua_pushinteger`），句柄校验 `sub_40AB90` 会解引用 `[handle]`；111 个脚本对句柄无算术、无 `io.` ⇒ 我方可用任意稳定 id，唯一硬要求是无效句柄回退（`Add_JointNail` → 0.0）。运行时证据用 `work/probe_objtable.py`（外部 `ReadProcessMemory` 读 `dword_665334` 对象管理器）。

**2026-10-31 追加：T6.3/b1 采集链路已定型（F260–F264）。** 不要再走「MCP 插件挂断点」：headless 下插件的写操作全静默失效（`SetBreakpoint` 报成功但不进 `ListBreakpoints`、`bp`/`pause` 无效、`log` 命令被拼成 `log{x:eax}`）。可用链路是**离线写模块库**：`tools/moduledb.py inject <x64dbg>/x32/headless/db/game.exe.dd32 <game.exe> <bps.txt>` 注入断点（RVA、oldbytes、`logText`、`"commandText":"run"`），把 `plugins/x64dbg-MCP-Server.dp32` 改名 `.off`，headless `-pid` attach 后命中即写 stdout 并自动继续；MCP 仅用于读（`GetDebugState`/`ReadMemory`/`Disassemble`/`ListBreakpoints`）。**点击**：`python tools/click_play.py <pid> --x <design_x> --y <design_y>`（客户区 1.5× 缩放、按下 150 ms；F263）。地图节点坐标来自 pak `GuiLvl.txt`（Command 299–350 = 52 关，`design=(PosX,PosY)+(506.15,355.5)`；`tools/map_nodes.py` 生成表，F264），开图点 (285,414)。已端到端验证：Map → 1 号节点 → 25/25 `Add_*`（`work/hostcapture_lvl1_via_map.*`）。

**2026-10-30 决策：宿主改走 FPC/LCL + GLScene 重建（计划 M6），C++ 宿主保留作对照物。** 当天 T6.1 窗口层就完成：`src/host_lcl/magnet.pas`（40 行）让 `tools/wincompare.py` 的 15 个窗口字段 `diffs=0`（F214）。下面几段描述的是 **C++ 路线**（F184–F200）的成果，仍可作对照基准，但不再是交付主线。

两个 DLL 已复刻并验证完毕（**b2Physics 87/87 + 52 关全 PASS**；**Squall 99/99 + 17 个宿主导入 0 分歧**）；宿主 exe 过了窗口门禁，**主菜单由宿主代码现算**：纹理直读 pak（上传像素 37/37 与原版逐字节相同，F187）、布局按固定设计空间 1018×739 与二态悬停（F190），与原版逐像素 mean|Δ| **1.088/255**、A/A 地板 0.00。
Lua 侧已经起步：vendor Lua 5.1.5（未改动），pak 里 **111 个脚本 111/111 编译通过**、`lvl_info.lvl` 解析出 **52 关**（F191）。
卡点很明确：**关卡渲染**还没做（只有菜单 + 单帧画像）；Lua 的 **144 个绑定与执行语义**未接（T3.3 剩余）；文本仍是「同一字模格 ×3」的固定串，**宿主自己不会排版字符串**（T3.5）；Squall 的 **PCM 逐位**仍阻塞。

**本轮新增一条主线（2026-10-30 晚，L2-B 工具链考古）**：`requirements.md` 里「整 exe 字节级 = 明确不做」的否决理由（F01 说是 Delphi/VCL ⇒ 跨语言不可达）**前提已被证伪**——原版是 **FPC 2.2.4 [2009/12/27] + LCL 0.9.28.3 + GLScene(LCL 分支)**（F202），同语言同编译器，工具链公开可得。现在已经量到的：LCL 可自编且局部 **98.9% 逐位相同**（F206）、`.text` 在 **`0x521000`** 有断崖分界（F204）、GLScene 世系夹到 **v1.1 / trunk r5000**、11 个单元 1,043 个函数只剩 **12 个（2,448 B）sim<0.95** 且已证是原版本地补丁（F211–F213，逐单元百分比以 §0.1 为准）、宿主自有代码 **≤390 KB / 约 400–700 个函数**。**但 `requirements.md` 那行还没改**（要一个显式决定，见 §11）。

台账 **349 条**（F001–F349，无缺号，只增不减）。**T7.0 已完成（F244–F248）**：FPC 2.2.4 的 `GetMem/FreeMem` 不是进程堆直通（F235 的"进程堆直通/无私有块头"推论已证伪）；默认 RTL 下跨模块双向 10 万次交叉分配/释放都在首 5000 次内崩/挂；装宿主 `TMemoryManager`+`TMemoryMutexManager` 后在真宿主主线程上 A/B 10 万 + 交叉 realloc 2 万 PASS；跨模块异常两向都不可捕获。

- **2026-11-01 T6.3d 起点（F283/F284）**：新仪器 `tools/phys_sweep.py` 把 52 关物理 init 一次扫完（46.9 s）⇒ **5 PASS / 45 MISMATCH / 2 SKIP**（PASS = Introduction、Let's Get Acquainted、The Old Clock、Oscilloscope、The Teleport；SKIP = 两个与 Introduction 共用录制的对话关）；`b2_sites.py compare` 增 `--stop-at-step`（只比首次 `b2_World_Step` 之前的调用）。首修 `Add_SimplePhysCircle` 的 arg2/arg3 语义——是密度/弹性，不是角度（F283）⇒ The Old Clock 归零。下一步队列按「录制 body 数量差」排：`Add_GraphSprite`(49 关) → `Add_Key`/`Add_Lock`/`Add_BarDoor`(24–26 关) → `Add_WoodFormWall`(17) → `Add_Rope`(10，单次 ~12 body)。

- **2026-11-01 T6.3d 覆盖图收口（F285/F286）**：`tools/phys_sweep.py` 打 52 关物理 init 覆盖，从 **5 PASS 提到 34 PASS**（46 s）。新增 `tools/gen_phys_shapes.py`：从录制按 style 生成形状常量表（`phys_shapes_gen.inc` / `wfw_table.inc`），`physworld.pas` 用 `BuildFromStyle` 统一建体，共接 18 个工厂。关键语义：`SetFriction/Restitution` 只写最后一个形状、filter/density 形状号从大到小、Rack 半径是 π 的倍数、Key 常量是 1/128 倍数、`Add_PhysicObjectWithAdvGraph` 只建 body。剩 16 关：绳索 10、父图局部坐标/视觉角度 4、`Set_PhysFilterData` 按 body 形状链 1、录制不可用 2。

- **2026-11-01 T6.3d 收口（F285–F288）**：52 关物理 init 覆盖 **5 → 35 PASS**（`tools/phys_sweep.py`，46 s）。新增 `tools/gen_phys_shapes.py` 从录制按 style 生成形状常量表（`phys_shapes_gen.inc`/`wfw_table.inc`），`physworld.pas` 用 `BuildFromStyle` 统一建体，共 18 个工厂；`SetFriction/Restitution` 只写最后一个形状，`SetFilter`/`SetDensity` 形状号从大到小，`TPhysObj.Shapes` 上限 8→64（lvl38 的 body 8 有 10 个形状）。剩 15 关：绳索 10（kind=1 的链节规律已读出）、父图局部坐标/视觉角度 4、录制不可用 2。

- **2026-11-01 T6.3d 绳索 + 无头模式（F289/F290）**：`Add_Rope` 按「锚点链式」实现（`anchor_i = p_i + h·u(a_i)`、`p_{i+1} = anchor_i + h·u(a_{i+1})`，两步都落 Single；style 表 0/1:(0.77,0.2) dens .5、2:(0.275,0.2) dens 3、3:(0.77,0.5) dens .2；相邻链节无 id Revolute），`Get_RopePhysItem` 0 基、rope id 的 `Set_PhysParams` 逐链节；`Add_HammerParts` 补第二个 body（锤头）。⇒ 52 关物理 init **35 → 45 PASS**，终局 **45 PASS / 5 MISMATCH / 2 SKIP**（MISMATCH = 5/36/42 视觉角度、9 录制不可用、28 待归因；SKIP = 13/51 共用录制；`work/phys_sweep_headless.json`）。**新增 `HOST_HEADLESS=1`**：不建窗、不建 GLScene/GL 上下文，只跑 pak/Lua/物理自检；有头 vs 无头 b2 日志 `compare` 0 差异，单关 0.92 s → 0.12 s、52 关 sweep 36.7 s → **9.6 s**（`tools/phys_sweep.py` 已默认无头）。**无头用法**：`HOST_HEADLESS=1 HOST_PHYS=1 HOST_LUA_SELFTEST=5 HOST_LUA_LEVEL=8 B2PROXY_LOG=... build/host_lcl/magnet.exe`（`HOST_DUMP_FRAME` 仍必须有头）。

- **2026-11-01 T8 oracle 自动化（F308–F314，详见 §14）**：`sweep.py --floors` 把每份录制的 A/A 地板缓存到 `work/floors.json`（**唯一非零** `rec_20261028_231623`=5,297，与 F125 逐项相同），`report_sweep` 出 `地板` 列、`verify physics:sample` 输出 `bad/floor`（判定口径不变）；`gen_rec_exports` + `rec_pick` 让「改一个导出」只跑 **1–3 份**录制（`rec_pick --exports b2_Body_SetBullet` → 1 份，现 4.4 s；`verify --changed` 0.3 s）；**14 路并行被证伪**（34.7 min vs 8 路 17 min，总重放量 3.6×）⇒ 默认 `min(8, cpu//2)`；**D4 重放器 5.0×**（真凶是每 8 条调用写一次进度文件）⇒ 全量 57 份 **15–17 min → 3.7 min**、总重放量 7,109→1,421 s（F312/F313）；**D5 合成契约** 87/87 导出 0 差异（`verify --only b2:contract` 0.3 s，F314），顺带修掉 5 处只有契约探针能抓到的 ABI 错误。

- **2026-11-02 T7.2b 崩溃捕获（F315–F317）**：宿主崩溃的 OK/CANCEL 来自 LCL `TApplication.ShowException`（Cancel → `Halt(0)`，F315）；`src/crashlog/crashlog.c` 在进程内装 first-chance VEH，`CRASHLOG_DIR` 开启后把 code/地址/模块+RVA/CONTEXT/栈写进 `crash_<owner>_<pid>.log`，`CRASHLOG_DUMP=1` 写 minidump（默认只写 seq=1），`CRASHLOG_DIALOG=1` 记 `#32770` 正文（覆盖 FPC `raise`）。代理（b2/Squall/GL）与 `magnet.exe` 都带；判据 `python tools/crashlog_test.py` 16/16、`python tools/crashlog_host_test.py` PASS、`verify.py` gates=7。符号化：`python tools/crashlog_symbolize.py <log>`。

- **2026-11-02 旧 FP 场景复核（F318）**：`HT_CW=0x1332`（解除 invalid 屏蔽）+ `HT_SPECIAL=1`（NaN/denormal）时，crashlog 在 `game.exe+0x001ADFAB`（原版 `sub_5ADF60` 的 `fcompp`）记录 `0xC0000090`（`note=float-invalid-operation`），栈 `htab!ht_entry → htcw → b2Physics 代理 → USER32 → game.exe`，并写 74 KB MDMP；正确宿主 CW `0x137F` 下同一 800 条语料 `HT DONE runs=800 nan_diff=0`、crashlog 0 条 EXC。⇒ 旧的“Invalid floating point operation”弹窗根因是 FPC DLL 解除 x87 invalid 屏蔽后对 NaN 比较。

- **2026-11-02 Self 类型首过（F319）**：1,012 个 pending 函数的 `Self` **不是单一结构体**。FPC 对象头 `[Self]=VMT`、`VMT+0xC` 类名短字符串、`VMT+0x30+4*i` 虚方法槽；`dword_665334` 是 `TLevelObjects`（VMT `0x6431D0`，大小 `0xB8`）。`python tools/app_self.py` → `work/app_self.csv`：39 个 virtual_method（21 个定义类）、144 个 Lua 绑定（`lua_State*`，不是 Pascal Self；102 个内部用 TLevelObjects）、802 个 direct_method（类未定，T7.2c）、27 个 static/helper。

- **2026-11-02 Self 深层映射（F320）**：修掉抽象解释的 `mov [ebp+var], eax` Self 槽 bug 后，静态覆盖 **183 → 540/1,012**（153 Lua + 387 方法）。运行时字段表 66 类（`TLevelObjects` 字段到 TDebugInfo/TSoundManager/TPhysicObjectList/TGraphObjectList/TJointObjectList/TTimerObjectList/TScriptManager 等）+ live 回调 46 条（30/30 的 Self 偏移更匹配 context）参与传播。剩 472 = 324 只有未知调用者 + 101 已知调用者未解析 + 47 无直接调用者；下一层用运行时入口 EAX/VMT 采样。产物 `work/app_self_deep.csv`、`work/live_fields.json`、`work/live_callbacks.json`。

- **2026-11-02 10-function matching pilot（F321–F323）**：从 540 个有类名函数选 10 个跨类叶子，用 FPC 2.2.4 `-Mdelphi -O1 -g- -Xs- -Xm` 重建源码；`work/pilot/compare.py` 逐字节比对 retail `.text` ⇒ **10/10 exact**（无 call/全局引用，故无重定位）。负例：`TLevelObjects.SetFlag` 的 `True→False` 第 15 字节 `01→00`，判据拒绝。关键形态：`0x52DDA0` 是带两参、未显式赋 Result 的 function + `with`；`0x576290` 是 procedure 不是 function；`0x5625F0` 匹配 standalone procedure(Obj, A)，不是方法。边界：候选源用合成类/填充字段，只证 codegen/ABI，不是真实类布局；带 call/绝对地址的函数还需重定位归一化或整链接。产物 `work/pilot/pilot10.pas`、`work/pilot/pilot10_results.json`、`work/pilot/README.md`。

- **2026-11-02 带 call 的 10 函数（F324/F325）**：`work/pilot/callers.pas` 用同 flags 编译；`work/pilot/reloc_compare.py` 只屏蔽候选 COFF 的 REL32/DIR32 字段 ⇒ **9/10 masked_equal**。关键：`TProfileManager.Get` 是 procedure；`TCameraManager.Update`/`TScriptManager.Get`/`TUIContainer.Count` 调用嵌套对象的**方法**（对象进 EBX，standalone 显式 Obj 桩形态不对）；`TMainMenuManager.LoadGui` 是全局 `PChar` 的 `mov edx,[0x64162C]`，不是 `mov edx,offset`。唯一失败 `TSoundManager.Stop`：target `mov al/test` vs FPC `cmp`，其余字节相同，是源码形态/开关问题，不是重定位。wrong-target 负例 `callers_neg.pas` 把 `sub_5795D0` 改成 `sub_571960`：`masked_equal=True` 但映射不符 ⇒ R3 拒绝；规则 R1–R6 见 F325。

- **2026-11-02 第二批 10 个叶子（F326）**：`work/pilot/leaves2.pas` ⇒ **9/10 exact**；累计叶子 **19/20**。新增 exact：TMouseCur 三个字节 getter、三个空方法、TLevelObjects 字节 setter、TBaseScreenObject 带一个未用参数的 Char getter、TLevelMenu 嵌套 Boolean setter。唯一失败 `0x57B330`：target Self 在 EAX + 一个栈参数、callee `retn 4`；FPC 2.2.4 的 2 参/3 参/stdcall 方法形态都产生更大帧或 `retn 8`，暂归为调用约定/源码形态未复现。

- **2026-11-02 两个例外闭环（F327/F328）**：`0x57B330` 的 `[ebp+8]` 不是 Integer，是 **Single**；`procedure SetValue(A: Single); FValue: Single at +0x2C` 逐字节相同 ⇒ 第二批叶子 **10/10**，累计叶子 **20/20**。`TSoundManager.Stop` 的 +4 是 **Char**，`if FChar <> #0 then ...` 复现 `mov al,[eax+4]; test al,al` ⇒ 带 call 批次 **10/10 masked-equal**。先前 F326 的 9/10 与 F324 的 9/10 是历史状态。

- **2026-11-02 第三批 9 个叶子（F329）**：`work/pilot/leaves3.pas` ⇒ **7/9 exact**，累计叶子 **27/29 attempted**。新增 exact：0x57B290 早退 reset、0x57B660/0x58E660 standalone `GetData(Obj, Dest)` + `rep movsd`、0x567DC0 const-record copy、0x58F100 三参 Boolean True、0x58F120 单 Single 空方法、0x561EE0 `FFlag1 and FFlag2`。残差：0x57B160 只差对齐 NOP（`89 f6` vs `90 90`，指令级相同）；0x58F620 只差栈槽序（Self -8/Src -4/Dst -C vs 方法 Self -C/Src -4/Dst -8）。0x583270 140 B 浮点循环延后。

- **2026-11-02 第四批带 call 10 个（F330）**：`work/pilot/callers2.pas` ⇒ **10/10 masked-equal**，累计带 call **20/20**。覆盖 Single/LongInt/Char 参数、零参 getter、四参 setter（`retn 8`）；方法调用形态（对象进 EBX、Self 在 EAX）全部成立。

- **2026-11-02 第五批带 call 10 个（F331）**：`work/pilot/callers3.pas` ⇒ **5/10 masked-equal**，累计带 call **25/30**。exact = 4 个 TSoundManager Stop/Pause（Char 守卫 + cdecl）+ TLevelMenu 四参 setter。TJointObjectList 五个同形函数只差参数求值顺序（target 先取 FField 到 ECX 再装全局到 EDX；FPC 2.2.4 反过来），重定位目标全匹配。
- **2026-11-02 第五批残差闭环（F332）**：`work/pilot/callers4.pas` 把五个 TJointObjectList 包装的第二实参写成 retail 数值地址常量（`Pointer($647AC4)` 等）⇒ **5/5 masked-equal，累计带 call 30/30**。机制：同一编译器下数值常量的装载顺序与 retail 一致，`@G` 符号地址则相反；`$647AC4→$647AC8` 负例在 offset 0x10 被拒。⇒ 残差不要求 2009/12/27 编译器；retail 源码 token 仍未定。
- **2026-11-02 T6.3d 收口（F333–F335）**：① `Local_ToWorld`/`World_ToLocal` 由 `(id,0)` 桩改为 body 平移+旋转；Burned Out（5）PASS。② 28/36/42 的 xform/joint 残差是 **RNG 状态**，不是视觉角度/父图局部坐标：`HOST_LUA_RANDOM` 回放录制反推的 `math.random` 返回值 + `mapping/phys_random.csv`，36/42 在 1e-6、28 在 5e-6 下三关 0 差。③ `Good Shot!`（9）的 `rec_20261029_134716` 从关卡中途开始（首 step 前 4 bodies vs 宿主 15）⇒ `mapping/phys_skip.csv` SKIP，新增 T6.3d-r 重录。④ 判据：`python tools/phys_sweep.py` ⇒ **49 PASS / 3 SKIP / 0 MISMATCH**（11.3 s）；`python tools/verify.py` ⇒ **gates=7 fail=0**。目标 50/2 只差第 9 关重录。
- **2026-11-02 T6.3d 最终（F336）**：重录 `Good Shot!`（`work/rec_20261102_155327`，293,593,804 B，B2FFI02，首 step 前 23 bodies）后，新录制暴露 `Add_Ball` 未接：8 个球体 = Circle fric .7 / rest .4 / dens .3 / r .6；`PhysAddBall` + 生成器 HOOKS 接上 ⇒ 第 9 关 **23/23/33/8/82** 全 0。`python tools/phys_sweep.py` ⇒ **50 PASS / 2 SKIP / 0 MISMATCH**（12.5 s），`verify.py` ⇒ gates=7 fail=0。F335（49/3/0）置过期；13/51 仍为 shared SKIP。
- **2026-11-02 T6.4a 第一关（F337–F340）**：内存判 MENU（`[0x665334]`/`TLevelManager+0x30`）→ 内存门控 Play 录 `work/level0_gl.bin`；新仪器 `tools/level_draw_ab.py`（自证 A/A/负例）；宿主 `src/host_lcl/levelscene.pas` 的 Introduction 场景 **25/25 逐 draw 零差**（frame 9600，`mismatches=0`）；菜单 `LoadPakTexture` 重构后 21/21；`verify.py` 7/7、`phys_sweep` 50/2/0。边界：瞬时态（hint alpha 0.8255/齿轮角 0）、手工场景表；通用 Lua→场景/动画/其他关卡归 T6.4a-r。

- **2026-11-02 C 路线：绕过菜单直接进关（F342）**：`sub_560880` 的 command 299–350 分支 = `sub_571610(lm,index)` → `sub_572160(lm,rec)` → `sub_5721B0(lm)`；`work/probe_direct_level.py` 用窗口线程 hijack（`SuspendThread`+`SetThreadContext`）实测 `[lm+0x30]` 2→1、`[lm+4]=index`，负例 no-op 保持 2；index 0/1 的 b2 init 与真实点击录制 `b2_sites compare --stop-at-step` **TOTAL mismatches=0**；边界：未调 `sub_560720(appObj,1)`，渲染/退出未验证。

- **2026-11-02 菜单管理器状态切换（F343）**：`sub_560880(appObj, 299+index)` 端到端实测 ⇒ `[app+0x10]` 2→1、`[lm+0x30]` 2→1、b2 首步前 init 与真实点击录制 **TOTAL mismatches=0**、截图确认 Introduction（菜单消失）；负例 `cmd=298` 保持 2。appObj 由 `[app+0x2C]=lm`+`[app+0x30]=menu`+`[menu+0x58]`+`[list+0x58]=52` 扫描定位。F342 的「未调 `sub_560720`」边界已闭合。

- **2026-11-02 同进程 LVL→LVL（F344）**：`sub_5721B0` 建关末尾把 `[lm+0x54]` 清零，所以关卡运行时再调一次 `sub_560880(appObj, 299+newIndex)` 即可切到另一关（`sub_572160` 接受新记录）；`--index 0 --index2 1` 实测 `[lm+4]` 0→1、第二段 init 对 `rec_20261029_135715` **0 mismatches**（bodies 9 / shapes 15 / setters 39 / joints 0），截图 `work/level_switch.png` 是第 2 关。边界：xform 因 `collect_seq` 按 body 指针分组、指针复用而暂不可比；Lua/HUD 对象表未 diff。

- **2026-11-02 Play=resume 的静态守卫（F345）**：`sub_560880` case 106 只在 `[lm+8]==0` 时走 `sub_575490`→`sub_571610`→`sub_572160`→`sub_5721B0`；`[lm+8]!=0` 时只执行 `sub_560720(app,1)`。`sub_5721B0` 写 `[lm+8]=1`，只有 `sub_560E80`（菜单回调 cmd 1/3）清零，主菜单切换不清。地图 299–350 无此守卫 ⇒ 强制重载。`work/probe_play_resume.py` 实测：menu 后 `lm8=1`、`[lm+4]`/`[lm+0x50]` 不变；Play 后仍不变、`app16` 2→1。

- **2026-11-02 私有桌面隔离（F346）**：`work/probe_vdesk.py` 用 `CreateDesktop`+`CreateProcess(lpDesktop)` 在 `MagVDesk_<pid>` 上跑 `game.exe`；t≈16 s 到 MENU，窗口线程直接 `sub_560880(app,299)` ⇒ `[lm+0x30]` 2→1、`[lm+8]=1`。两次独立运行都是 b2 日志 8,388,548 B / `CreateWorld 1 / CreateBody 8 / DestroyBody 0 / 1,266 steps`；用户前台窗口不变，用户光标移动 5 次期间隐藏光标 0 次变化。⇒ 批量采关可以跑在私有桌面，不抢前台、不需要鼠标。边界：无像素/音频验收，游戏仍占 CPU/GPU。

- **2026-11-02 `tools/direct_drive.py` + 静音（F347/F348）**：私有桌面 + 连续 `sub_560880(app,299+index)`，判据 `[lm+0x30]=1/[lm+4]=index/[lm+0x50]!=0/[lm+8]=1`；`--levels 0,1,2` 各 200 ms、fail=0，负例 `99` 启动前 exit 2。游戏把 SOUND/MUSIC 音量持久化在 active `<Player>`（用户改成 0/0，624→616 B；`KKK` 100/100 不变）；工具只读不写存档，并用 `nircmd muteappvolume game.exe 1` 兜底。CABLE 留给音频验收。
- **2026-11-02 采集默认 WM_CLOSE + NOP 广告（F354/F355）**：`direct_drive.py` 新增 `--exit-mode wmclose`（`PostMessage(WM_CLOSE)`，失败回落 clean）；`capture_levels.py` 默认 wmclose + `--noad`（work 副本 file 0x12E16A 写 `90×5`，`--keep-ad` 关闭）。level 1 实测 PASS mism=0、log 2,371,720 B、exit 0/702 ms；clean 仍 PASS。全量 52 关未重跑。
- **2026-11-02 T6.4b-0 采关补全（F349）**：`direct_drive.py` 默认远端 `ExitProcess` 干净退出，b2 代理在 `DLL_PROCESS_DETACH` 写完 8 MB 缓冲（同一关 clean 2,345,172 B vs `--kill` 0 B）；新增 `tools/capture_levels.py` 逐关独立进程采集并 `b2_sites compare --stop-at-step`。52 关 15m28s ⇒ PASS=47 / SHARED=2（13、51，共用 Introduction 录制）/ RNG=3（28/36/42）；0 MISMATCH、0 ERROR，52/52 `exit.clean=True`。产物 `work/capture/lvl*_ffi.bin`、`summary.jsonl`、`run52.log`。

- **2026-11-02 T6.4a-r-2c5 `Get_RealViewRect`（F364/F365）**：反汇编 `0x59be10 → 0x57B430 → 0x562510` / `0x562410` 定出矩形 = 相机中心 ± 适配半视图（`hx=max(a,b·W/H)`，`W/H`=1018/739）；探针/宿主的 0 桩是 F359「父图=屏幕层」的误归因。探针实现后 52 关重生成（只有 20 关的 left/top 派生实参变化；`LUA_PROBE_VIEWRECT=0` 与改造前逐字节相同），`scene_from_lua` 改成相机偏移 + `Set_ScrObjPos` 回放 ⇒ level 2 静态 draw **46/46 零差**（level 0/1 25/25、29/29；负例 0 桩语料 `mismatches=3`）。宿主同语义（`gen_lua_bindings.py`），`lua_bind_ab` 只剩 lvl05/09/28 的 `Local_ToWorld` 派生实参差（已知口径）；`phys_sweep` 50/2/0、`verify` gates=7。

- **2026-11-02 T6.4a-r-2c6 `Add_SwitchArm`（F366）**：图元 = 中心在 body 的 4×2 quad、sprite 角 = body−π/2，锚点半径 1.6；level 2 frame 904 的摆角是 init+0.506（关节限位）。`fit_arm_pose` 从 ref 长边拟合动态角并用 `pivot+R(body)·(0,1.6)` 预测位置（`center_err=0.0000`，`--arm-tol 0.02` 硬判据）⇒ level 2 **47/47 零差**；负例 `--no-arm-fit` 退出码 1；level 0/1 无回归。下一刀：r-2d 移植 Pascal。

- **2026-11-02 T6.4a-r-2c7 扩关 level 3/4（F367）**：两份独立 GL 采集 `work/gl_levels2a`/`2b`，A/A 只余动态项（`train_1` d=0.630、smoke 动画帧）。新增 `Add_WoodBox`（1/2/3→`wbox_N` 4.702 正方形）、`Add_PushButton`（`pbut_1` 3×1.5）、`Add_BarDoor`（`bar_1` 7×3.5）、`Add_SwitchArm` style 2（`sw_arm2` 4×2）与引擎材质名回退（`button_platform_1`→`bplatf_1.png`）。静态判据 level 3 `pairs=53 mismatches=0`、level 4 `pairs=37 mismatches=0`；level 0/1/2 无回归。plunger/shank/train/smoke 是动态项，归宿主的物理/动画。

- **2026-11-02 T6.4a-r-2c8 齿轮动画机制（F368）**：短间隔（Δt<0.92 s）测角速度 ⇒ level 0 的 gear_2/7/3 = **1.699/-1.275/1.530 rad/s**，与 `Set_JointMotors(...,1.7,...)` + `Add_JointSimpleGear` 的 ratio（1.3333/-1.1111）按 `w_child=-w_parent/ratio` 吻合；level 1/2 的齿轮 **0.000**（静态；`fit_gear_angles` 的 ±π 是对称四边形歧义，已改为差 0/π 时保留 init 角）。5 关静态判据不变：25/29/47/53/37。宿主可按 `w·t` 出齿轮动画；level 0 的帧内绝对时间仍待定。

- **2026-11-02 T6.4a-r-2d0 Pascal 场景模型（F369）**：新增 `src/host_lcl/scenemodel.pas`（绑定 JSONL→图元列表，语义照 `tools/scene_from_lua.py` 的 `build()`：相机偏移、`Set_ScrObjPos` 句柄回放、HUD 设计空间、摆臂锚点、WoodBox/PushButton/BarDoor/SwitchArm style 2、引擎材质名回退）+ `scenemodel_cli.pas`（FPC 2.2.4 控制台）+ `tools/scenemodel_ab.py`。5 关 objects=15/21/37/45/33、相机一致、`mismatches=0`；负例跨关 16 处。宿主**尚未**把它接进渲染路径（仍走硬编码 `levelscene.pas`）。

- **2026-11-02 T6.4a-r-2d 接渲染路径（F370）**：宿主 `HOST_LEVEL_RENDER=1 HOST_LEVEL_MODEL=<binding.jsonl>` 用 `SceneModel` 建关卡场景（世界/HUD sprite、背景 `back_N1/2`、mbtn/dot 常量、相机取模型；HUD 映射 `X=x+509−w/2, Y=y+369.5−h/2`）。level 1 与零售 frame 1060 `pairs=29 mismatches=0`；负例（level 2 模型）`mismatches=4`；无 MODEL 的硬编码 Introduction 仍 `sprites=25`。数据源仍是探针 JSONL；下一刀接宿主自身 Lua 日志 + 动画相位。

- **2026-11-02 T6.4a-r-2e0 宿主自产 Lua 日志（F371）**：`HOST_LUA_SELFTEST=5 HOST_LUA_LEVEL=1` 产出的 JSONL 与探针 `lua_bind_ab` **149/149**；以它为 `HOST_LEVEL_MODEL` 渲染 level 1 仍 **29/29 零差**（`sprites=35`）。数据源不再依赖探针；剩动画相位（`HOST_LEVEL_TIME` + 齿轮 `w·t`、摆臂、level 3/4 动态项）。

- **2026-11-02 T6.4a-r-2e1 齿轮速度移植（F372）**：`scenemodel.pas` 解析 `Add_JointNail`/`Set_JointMotors`/`Add_JointSimpleGear`，按 `w_child=-w_parent/ratio` 传播并暴露 `ApplyTime(t)`；CLI `[time]` 选项打印速度。level 0 得 `1.7000/−1.2750/1.5300`（=F368）。**绝对相位未归因**：由驱动轮反推 t 后 gear_7/gear_3 的 sprite 角差 0.785/0.314 rad，存在 per-style sprite 偏移或电机前沉降，需单独测。

- **2026-11-02 T6.4a-r-2e 齿轮相位（F373）**：齿轮 sprite 相对 body 的局部旋转是 **π**（螺丝为 0）；加 π 后 level 0 的驱动轮 `t=1.490`，gear_7/gear_3 的预测与零售逐位吻合。`HOST_LEVEL_TIME` 接进 `BuildFromModel`→`ApplyTime`，宿主 level 0（自身 Lua 日志 55/55）`pairs=25 mismatches=0`；负例 t=1.952/0.5 失配。方形齿轮 bbox 对 90° 倍数不敏感，负例取 ~45° 偏移。下一刀：摆臂 settle 与 level 3/4 动态项。

- **2026-11-02 T6.4a-r-2f0 摆臂 settle（F374）**：摆臂静止位姿是确定规则——body = init + 0.5（关节限位）、位置 = 锚点 + R(body)·(0,1.6)、sprite = body−π/2；level 2 整帧 **47/47**（宿主自身日志 193/193），level 4 的 `sw_arm2` dbbox=0.016 PASS（整帧只剩 `gear_7` 的电机相位差 0.829）。`scene_from_lua.build` 与 `scenemodel.pas` 都在构建末尾应用；`--no-arm-settle` 是工具负例。下一刀：level 4 齿轮相位（电机 9/5）与 level 3/4 的 plunger/shank/train/smoke。
- **2026-11-02 T6.4b 拖拽首段（F380/F381）**：`work/drag_lvl1.py`（分阶段 CLI）+ `work/drag_shot.py`（截图标注刚体/目标/轨迹）用实时 b2 digest 做闭环；level 1 螺母→左箱 d=0.166、刷新 gear→右箱 d=0.197，出现 **“Level completed!”**。关键标定：客户区 1527×1108 @ (516,183)（1.5× DPI）、视口 ±28.2395/±20.5、**屏幕 y 与 GL y 反向**；磁铁需按住左键。b2 代理新增 `B2PROXY_LIVE`/`B2PROXY_LIGHT`。下一步：宿主重放 + `b2_sites compare`。
- **2026-11-02 磁铁机制 + CI mover 首跑（F382–F384）**：按下金属体 → `TPlayerObject+0x14`=目标、`+0x10`=1、`TMouseCur+0x40/+0x44`=光标世界；每帧 0x57A000→0x58E5A0→0x58E4A0，力 `min(315/d,30)` 沿 mouse−target（常数 10.5/315/30），经 target VMT +0xD4。`Add_Magnet` 是 TPhysicObject 工厂，不是玩家磁铁。CI 代理 `B2CI_*` 力伺服能推动 body #4，但直线路径被箱体挡住（22.34→17.11），未到目标；下一步 waypoint/施力点。
- **2026-11-02 CI mover 两段通关（F384）**：`B2CI_CONFIG` 热切换 + `B2CI_MODE=velocity`（max 20）在 level 1 两段到达目标（螺母 d=0.073、齿轮 d=0.176），出现 **“Excellent! Level completed!”** 对话；`start` 在 level state 后等 0.8 s 并复查 `[lm+0x30]/[lm+4]/[lm+8]/app16` 再 arm。负例：不等待时完成态退回主菜单。全程无鼠标。

- **2026-11-02 下一步探索方向：IAT 假磁铁（让游戏自己施磁铁力，替掉代理直施力/写速度）**。依据：F341（输入采样唯一入口）、F346（私有桌面隔离）、F381（世界↔屏幕标定）、F382/F383（磁铁字段与力律）、F384（现行 CI 路径）。**关键前提（用户 2026-11-02 提出）**：CI 里没有真鼠标，`GetCursorPos`/`GetAsyncKeyState` 的返回值本来就没有语义（`GetAsyncKeyState(VK_LBUTTON)` 恒 0、光标位置与玩家意图无关），所以伪造这两个采样源**不会与真实输入竞争**——之前"写 `player+0x14/+0x10`/`mouse+0x1F` 每帧被清零"只在有真鼠标采样时成立。做法：改 `GetCursorPos` IAT 槽 `0x667330`、`GetAsyncKeyState` 槽 `0x66730C`（F341：应用层唯一引用，wrapper `0x401ED0`/`0x401BD0`，采样点 `sub_561C70`），每帧返回 `VK_LBUTTON=0x8000` + 目标方向的屏幕点（F381 反算 `screen_y=(20.5−world_y)/41·h`，客户区 1527×1108 @ (516,183)，视口 ±28.2395/±20.5）；命中测试、target 锁定、`min(315/d,30)` 力律与 `target VMT +0xD4` 施力全走游戏自己。建议配 F346 的 `MagVDesk_<pid>` 私有桌面跑，彻底隔离用户前台输入。**判据**：① `B2CI_FAKE_MAGNET=1` 时 trace 里出现 `b2_Body_ApplyForce`，且合力模长 ≤30、方向 = mouse−target（力来自游戏而非代理）；② level 1 两段 d<0.548 ⇒ gear 刷新 + 完成对话；③ 负例 A：`B2CI_FAKE_MAGNET=0` 同一脚本 body 不动；④ 负例 B：光标不落在金属体上 ⇒ `player+0x14` 保持 0、零 `ApplyForce`。**边界**：磁铁只有 30 N 上限、方向朝鼠标而非朝目标、远处按 `315/d` 衰减 ⇒ 仍需 waypoint（F382 的力伺服即因直线被箱体挡住停在 17.11）；私有桌面里 `GetCursorPos` 是桌面坐标，客户区换算要重标定。

- **2026-11-02 T6.4a-r-2f1 level 4 齿轮相位（F375）**：模型速度 gear_7/gear_1/gear_3 = 3.0/9.0/5.0；三只齿轮反推的 `t (mod π/w)` 唯一公共解 **0.689 s**。`HOST_LEVEL_TIME=0.689` 的宿主整帧（忽略 plunger/shank/smoke 与隐藏提示）**37/37 零差**；负例 t=0.4 ⇒ gear_7 失配 1.219。下一刀：level 3 的 train/smoke 与 level 4 的 plunger/shank/smoke。

- **2026-11-02 T6.4a-r-2g 静态覆盖里程碑（F376）**：5 个已采集关卡的静态场景全部通过宿主渲染路径（宿主自身 Lua 日志 → SceneModel → GL）：level 0 **25/25**（t=1.49）、1 **29/29**、2 **47/47**、3 **53/53**、4 **37/37**（t=0.689），`lua_bind_ab` 55/149/193/187/285 行 0 差，`level_draw_ab` 全部 `missing=0 unmatched_ref=0`。只排除各关动态项（level 3 train/smoke、level 4 plunger/shank/smoke）与隐藏提示。

- **2026-11-02 F377 level 3 train/smoke = 逐帧 `DoProgress`**：`lvl_o20.lua:1-67` 的 `DoProgress(DeltaTime)` 用 TrainTime + 三段圆弧算 `ang`，再 `Set_ScrObjPos(bTrain/bSmoke, ...)`；探针不跑 Update，记录的是 init 位姿。⇒ 这两项需要宿主逐帧 Lua 回调（T6.4d），不是静态工厂。下一刀：level 4 plunger/shank（几何连杆/物理位姿）与 smoke 动画帧。
- **2026-11-02 T6.4a-r-2f 动态项（F378/F379）**：level 4 的 plunger/shank 是曲柄滑块（`P=G+R(ωt)·(P0−G)`，`body_y=P_y+sign·sqrt(L²−(A_x−P_x)²)−off`），smoke 是 `smoke_5.png` 4×8 at (10.19,9.70)；宿主/Python vs 2a frame 827 **44/44**（含动态项），第二份采集 2b 反推 t≈0.1887 仍 **44/44**，负例 t=0.4 ⇒ 7 失配；`verify` 7/7、`phys_sweep` 50/2/0。**下一步已被上方 T6.4b 拖拽首段（F380/F381）取代：实际关卡是 level 1 / `lvl_o14`，已两段拖拽过关；旧的 level 2 / 先商量作废。**

- **2026-11-03 T6.4b-x 收口（F385/F386）：`B2CI_FAKE_MAGNET` 让游戏自己走磁铁路径**：`src/proxydll/proxy_core.c` 在 b2 代理 DllMain 按 env `B2CI_FAKE_MAGNET` 解析 game.exe 导入表替换 IAT 槽 `0x667330`/`0x66730C`，每帧返回 `B2CI_MAG_CONFIG` 的 `world_x,world_y,button`（世界→屏幕用 F381 视口 + 运行时控件原点；`B2CI_MAG_VIEW` 可覆盖），`B2CI_MAG_TRACE` 记 10 Hz；env 未设零行为。`work/fake_magnet_drive.py run` 用游戏自己的 `mouse+0x40` 两点标定（ax=0.9986467/ay=1.0041948），按下/移动/松开全走 `sub_561C70`→`sub_561F10`→`sub_58E8DD`→`sub_58E810`→`sub_58E690`；5 次独立启动均两段 d<0.548 + 完成面板，负例 A/B 通过。**力律勘误**：trace 244 行证明实际 `|F|=min(315,30·d)`（d>10.5 时 315±4.6e-5；d≤10.5 时与 30d 差 ≤1.79，位置差一帧），F383 的 `min(315/d,30)` 置已证伪，另立 F386。边界：只跑 level 1；普通桌面 + bring_front（未接 F346 私有桌面）；`player+0x14` 对象→b2 body 偏移未定（trace 直接给 body）。

- **2026-11-03 测试关卡 + 私有桌面（F387/F388）**：`tools/pak_write.py` 让 Pak v0.2 可重建/同名替换（roundtrip 逐字节相同）；`tests/levels/test_lvl_o.lua`/`test_lvl_e.lua` 用自由金属螺丝 (0,0)+chalk (5,0) 替换 level 1 的 `lvl_o14.lua`/`lvl_e14.lua`（不新增 entry/不改地图）。原版加载 5 bodies（4 墙+螺丝 (0,0)），`B2CI_FAKE_MAGNET` 在 `MagTest_<pid>` 私有桌面抓取→(5,0)，Lua 回调的 `Set_ScrObjPos(99,99,0)` 在 b2 日志出现（完成标记），`fg_same=True`；`PrintWindow` 私有桌面客户端全黑，像素不作判据。下一步：`tests/levels` 扩齿轮/障碍/运行时生成/开关，`work/test_fakemag.py` 升 `tools/ci_fake_magnet.py`。
- **2026-11-03 T6.4b-x-y（F407）：假磁铁 CI 升仪器 + 运行时生成夹具**：`tools/ci_fake_magnet.py` 支持 `build`（`bin/gametop` 副本 + `tools/pak_write.py` 同名替换）和 `run`（私有桌面、`sub_560880` 进关失败重试、两点标定、多 `--stage`、**逐 step digest 最小距离**而非 50 ms 轮询、`b2_Body_SetXForm` marker、F386 力律、runtime witness、前台隔离）。夹具 `tests/levels/chain_o.lua`/`chain_e.lua`：第一颗螺丝→(3,0) 后 `OnMove` 回调在关卡运行中创建第二颗 (-3,3)+chalk (0,6)，第二颗→(0,6) 写 (99,99) 标记并过关。正例 pid 10048：`d_min 0.2868/0.5974`、markers=2、ApplyForce 315 行（方向 ≤0.0097 rad、力律误差 ≤0.0048）、`fg_game_events=[]`、PASS；负例 `--done-dist 0.1` / `--marker 77,77` / `--runtime-stage 0` 全 FAIL。边界：live 轮询会漏（0.57–0.71 vs 逐 step 0.29–0.60）；`--done-dist` 必须大于夹具完成阈值；假磁铁会甩轻 body 穿墙。命令见 `tests/levels/README.md`。
- **2026-11-03 T6.4b-x-z（F408）：障碍夹具 + waypoint 绕行**：`tests/levels/wall_o.lua`/`wall_e.lua` 用自由螺丝 (0,0)（`Set_PhysParams(...,5,0,0)` 防穿墙）→ chalk (9,0)，中间 3 段静态 `Add_WoodFormWall(...,4)`+`SetStaticMass`（合并 x≈2.16..5.41、y≈-3.31..3.38）。仪器新增 `--waypoint STAGE:x,y`（可重复）/`--waypoint-hold`/`--waypoint-tol`，逐点移动光标。负例（无 waypoint，直线）：body 停在 x≈2.117、`d_min=6.8912`、无 marker ⇒ FAIL；正例两次独立启动（waypoints 0,6 → 6.5,6 → 6.5,2 → 7.5,1 → 8.4,0.4）：`d_min=0.5733/0.5900`、markers=2、PASS。边界：磁铁无阻尼，光标直达目标会绕圈（per-step min 2–4），最后一段 waypoint 必须靠近目标且逐段小步。命令见 `tests/levels/README.md`。
- **2026-11-03 T6.4b-x-g（F409）：齿轮力矩夹具 + observe 模式**：`tests/levels/gear_o.lua`/`gear_e.lua`：`bStatic=AddStaticWall(0,-25,0)`（**必须先赋值**，否则 `Add_JointNail` 静默失败、b2 日志 0 个 joint 调用）+ 两轮 `Add_MetallGear` (0,0)/(5,0) + `Add_JointNail`×2 + `Add_JointSimpleGear(0.8)` + `Set_JointMotors(j1,1,1.0,100)`。仪器新增 `--observe SEC --angle x,y --min-angle --gear-ratio --ratio-tol`（不按鼠标，读 angle/w）。正例：Δ1=2.5500、Δ2=-3.1875、w1=1.0、w2=-1.25、`ratio_measured=1.25000007` ⇒ PASS；负例 no-motor（torque 0）Δ=0、no-link Δ1=2.53/Δ2=0 均 FAIL。机制：b2 日志 `b2_World_Joint_Revolute`×2、`b2_World_Joint_Gear`×1、EnableMotor/SetMaxMotorTorque/SetMotorSpeed 各 1。命令见 `tests/levels/README.md`。
- **2026-11-03 T6.4b-x-s（F410）：开关旋转夹具 + 阶段角度判据**：`tests/levels/switch_o.lua`/`switch_e.lua`：`bStatic=AddStaticWall(0,-25,0)` + `AddSimpleSwitchArm(0,0,0,1,bStatic)`（枢轴 (0,-1.6)、限位 ±0.5）+ 标记螺丝；OnRotate 在 |Get_JointAngle|>0.2 时写 (99,99)。仪器新增 `--stage-angle STAGE:x,y`/`--stage-min-angle`/`--ignore-distance`。正例（横拖到 (5,0)）：Δangle=-0.5250、markers=2 ⇒ PASS；负例（拖到 (0,-2)，力线过枢轴）：locked=True、Δ≈-1.34e-19、markers=0 ⇒ FAIL。机制：磁铁力在 body 中心、枢轴下方 1.6 → 力矩。命令见 `tests/levels/README.md`。
- **2026-11-03 T6.4c-0（F411）：存档工具多玩家感知**：`tools/profile.py` 旧 `set` 在多 `<Player>` 档案里命中第一个同名键（实测会改 `ooo` 而不是 Active 的 `KKK`）。新 CLI：`players`、`get/set --player`（省略时单玩家直接用、多玩家用 `Active="1"`）、`diff A B [--player]`（逐键 `UserName.Key: old -> new`，相同退出 0）、`--file` 指向副本；新键插在目标块内。实测副本：A/A=0；`set SoundsVolume 7 --player KKK` ⇒ diff=1 且 `ooo` 不变；默认 Active 选择正确；缺失玩家报错。真实档案本轮已按用户要求把 `KKK` 的 `SoundsVolume/MusicVolume` 改为 0（备份 `hg_lmpgl.prf.bak`）。

- **2026-11-03 T7.2c 布局交叉验证 / 字节冲撞（F389–F393）**：新仪器 `tools/app_layout.py`（VMT 590 类、Self/字段 taint、`--check/--dups/--report/--show`）从 `mapping/app-self-map.csv` + `mapping/live-fields.json` 推出 399 个 `(class,off)`：pinned 180 / ambiguous 163；`--check` 用 `off < VMT+0` 抓到 0x552CA0 错分（TLevelObjects→TLogSession，F392），修正后 contradictions=0（负例 1）；`--dups`：exact 10 簇/34 成员、masked 62 簇/184 成员、7 跨类簇，30 个 pilot 命中 17 个在 masked 簇内（F390）。`tools/app_layout_rebuild.py` 用真实类型重建 3 函数 `masked_equal=3/3`，偏移 +4 负例 2/2，`LongInt`↔`TList` 与 typed↔Pointer+cast 两组声明字节逐位相同（F391）。下一步：运行时 EAX/VMT 采样补 T7.2c 剩 471；T7.5 身份判据加 R3。
- **2026-11-03 T7.2c 调用图 + Level 1 覆盖（F395–F397）**：`tools/app_graph.py` 建 3,901 条 app 调用边、209 个未解析间接；分类 state_loop 20 / state_dispatch 159 / event_virtual 37 / lua 144 / address_taken 40 / direct 487 / unreferenced 125。实机（私有桌面前台 + 真鼠标两段拖拽过 Level 1）入口探针 1,010/1,010：**547/1,010 会话命中、212 关卡窗口**；463 未调用中 428 不在已执行子图、35 可达；前沿无全局 flag、状态门无纯 setter ⇒ 不在前沿写内存。下一步：event 分支先定位实例再 idle 调用；state 分支驱动菜单/下一关；content 用 52 关语料。
- **2026-11-03 手动会话覆盖（F398）**：同一 1,010 入口探针，用户点遍主菜单 + NEXT ⇒ **597/1,010**（拖拽局 547），新增 51；剩余 413 中 state_dispatch 只剩关卡加载/地图 10 个 ⇒ 下一杠杆是 Level map 选普通关（毕业关捷径绕过 0x571B80），或写 [TLevelMap+0xb4]=1..5 触发纯 helper 0x579740。
- **2026-11-03 新 Profile + 前 2 关（F400）**：641/1,010（两局并集 **663**）。`0x571B80` 只在 `LevelGroup ∈ Circle-1..5` 时走；Tutorial/End-levels 不走 ⇒ 剩余 9 个 LevelMap/加载链要 `direct_drive --levels 15` 直接进 Circle 组。
- **2026-11-03 Circle-1 实入（F401）**：`LastCompleteLevel` 2→15 进 `lvl_o1`，LevelGroup 门确认；链路 `0x571B80/0x571A20/0x579100/0x5794B0/0x579740/0x57A930/0x582A60` 全命中；三局并集 **702/1,010**，剩 308（direct 142、lua 83、unreferenced 64、address 10、event 9、state_dispatch 2）。
- **2026-11-03 Circle-1 过关（F402）**：本局 706，跨局并集 **736/1,010**，剩 274（direct 121、lua 73、unreferenced 62、address 10、event 8、state_dispatch 2）。剩余 2 个 state_dispatch 是 state=1 分支与 debug HUD 分支，正常游玩不触发。
- **2026-11-03 调试 HUD 主线程调用（F403/F404）**：`TDebugInfo=[TGameManager+0x4C]`（2×TGLSphere + font + 3×TGLHUDText，`FText` 在 `+0x230`，WideString），默认因 `byte_622510=0` 隐藏；`work/hud_probe.py`（32 位）扫 VMT `0x6224A0` 找 manager，挂起窗口线程改 EIP 调 `0x564760(dbg,1)`，5 个 `+0x1F0` 0→1；MENU 截图 `65.17 FPS`，`--level 1` 后读回 `Start` 并截图 `85.17 FPS`+`Start`（`work/hud_after.png`）。勘误：`0x57A860` 是 `LoadLevelFile` 的 `scripts\\` 兜底，不是 HUD。注意 `[0x665334]` 是 `TLevelObjects`，不是 manager。
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
- 换行：工作树里追踪的文本统一 **CRLF**。`.gitattributes` 仍是 `* -text`（脚本/二进制/vendor 快照逐字节保真，F130），另给**本仓库文档**（`AGENTS.md`、`README.md`、`docs/*.md`、`tasks/*.md`、`tasks/*.MD`）加 `text eol=crlf`：提交归一为 LF、检出为 CRLF ⇒ 工具把文档误写成裸 LF 不会再造成整文件重写（F275）。vendor/ 快照不走归一；新文件写完仍转 CRLF。
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
| **M6 宿主重建（新主线）** | 窗口层 ✅ 15/15 `diffs=0`（F214）；T6.2 菜单层 ✅ 21/21（F225–F231）；T6.3 参数表 ✅ 144/144（F239）、a0 ✅（F240）、a1 ✅（F241）、a2 52/52 关 ✅（F242/F243）、b0 句柄语义 ✅（F249/F250）、b1 采集链路 ✅（F260–F264）、b2 事件派发 ✅（F273/F274）；T6.3d 物理工厂 52 关 init **45 PASS / 5 MISMATCH / 2 SKIP**（F283–F290，`tools/phys_sweep.py` 无头 9.6 s）；整机字节覆盖 **71.0%**（精确 795,218 B，§13）；T6.4 应用层、T6.5 整机 A/B 排队 |
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

> **2026-11-01 队列（当前，按 premise-gate 重排；判据见 plan 头部「路线图闸门」）**：① T6.3d 收口（9.6 s 判据，目标 `PASS=50 / SKIP=2 / MISMATCH=0`，9 关先重录）；② **T7.2a 竖切**（一个纯函数的 注入→pre/post→A/B，A/A + 负例）——它裁决应用层走逐函数替换还是行为切片，且不依赖宿主完成度，可与 ① 并行；③ 按 ② 的结论进 T6.4a–e（关卡渲染 / 输入拖拽 / 存档配置 / 循环状态机 / 关卡文本）；④ T6.5 整机 A/B。暂缓项（PCM 逐位、1 ULP、T0.3/T0.4、M3 遗留）见 `tasks/backlog.md`。

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

- **调试器探针环境**（F252/F253/F257–F259）：`biz_bundle`/`game_center`/`isgpet_bundle`/`picface`/`systembeautify_bundle`/`ichat_bundle` 是**搜狗输入法**注入，切系统 IME 到**微软拼音**后不再加载；`groupy_32.dll`（Stardock Groupy 壳扩展）仍会注入。无头实例的事件断点配置在 `x32\headless\headless.ini` 的 **`[Events]` 段**（写成 `[Symbols]` 不生效）。暂停不要用 MCP 工具 `PauseDebug`（在过期 IP 上 SetBPX，失败且状态不变），一律用 `ExecuteDebuggerCommand("pause")` 或 GUI F12。**合成点击点 Play 不可依赖**（多数会话让游戏 exit 0；点背景安全；手动点击有效，F259）⇒ 探针 `tools/hostprobe.py --no-play`，Play 由人点；每关必须新起进程（Play=resume，F258）。批量采集走 attach + `ReadProcessMemory` 读对象管理器（`dword_665334` +0x1C/+0x20/+0x24）。
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
| 崩溃捕获 | `src/crashlog/crashlog.c`（VEH + minidump + `#32770` 正文，编进三个代理 + 独立 `crashlog.dll`）、`tools/crashlog_test.py`（32 位单元探针）、`tools/crashlog_host_test.py`（game.exe 主线程 AV）、`tools/crashlog_symbolize.py`（RVA→函数名） |
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
## 12. 最近一轮（2026-10-31 晚，T6.3/b2 事件派发竖切）

**一句话**：`Attach_ScriptToObject` 不再只是桩——登记进 `src/host_lcl/luaevents.pas`，`HOST_LUA_FIRE` 可注入 `OnAddContact`，lvl49 的回调会真正执行并产出与原版 objlog 同名同序的 2 个工厂调用（F273/F274）。

```bash
# 单关 + 注入事件（index 49 = lvl_o7,lvl_e7,basefs；1016 = gLSystem.bBigDial）
HOST_LUA_SELFTEST=5 HOST_LUA_LEVEL=49 HOST_LUA_DIR=work/pak_gametop \
  HOST_LUA_LOG='C:\tmp\magnet_evt\lvl49.jsonl' \
  HOST_LUA_FIRE='1016:OnAddContact:gLSystem.bGearB' build/host_lcl/magnet.exe
python tools/lua_event_check.py work/lua_probe/lvl49.jsonl C:/tmp/magnet_evt/lvl49.jsonl \
  --objlog work/objlog_lvl49.jsonl        # 期望 PASS 1/1

# 负例（派发成功但 Lua 守卫不成立 ⇒ 与 init 逐条相同、无追加）
HOST_LUA_FIRE='1016:OnAddContact:1012'   # Body2 不是 gear
HOST_LUA_FIRE='1020:OnRotate:0'          # State=3，两个分支都不进
python tools/lua_event_check.py work/lua_probe/lvl49.jsonl <该次日志> --no-tail   # 期望 PASS 1/1

# 52 关回归（改生成器/绑定后必跑）
HOST_LUA_SELFTEST=4 HOST_LUA_DIR=work/pak_gametop HOST_LUA_LOG_DIR='C:\tmp\magnet_bind2' \
  build/host_lcl/magnet.exe               # 期望 levels=52 ok=52 fail=0
```

**下一步（T6.3c 已完成；T6.3d 工厂覆盖已扩到 level 1，见 F278–F282）**：宿主对 lvl49 init 的 bodies 18/18、xforms 18/18、shapes 20/20、init 关节 16/16、一次 init 的 56 个 setter 与原版录制逐项相同；level 1 的 13 bodies/13 设位组/19 shapes/39 setters 也全 0（`--body-limit/--shape-limit/--setter-limit`）。真实接触（`HOST_PHYS_MOVE=1022:8.04:3.16` 诊断输入）触发 `OnAddContact`，JSONL 尾段 5 条与 objlog 同名同序（`tools/lua_event_check.py --init <init-only>` PASS，ratio 0.417959183673）。**剩**：真实玩法输入/力驱动接触（T6.4）；其它建体绑定（CloseButton/AnimateSmoke…）与 style 表；其余事件（`OnMove`/`OnPersistContact`/`OnRotate`/`OnTimer`/`OnClick`）走同一派发接口。

**坑**：生成器里登记调用必须写在参数读取**之后**（放在前面会读到 0，`EventsFire` 报 `no binding for 1016/...`）；`luaevents.pas` 是新增文件，记得 CRLF。

## 13. 本轮（2026-11-01，整机字节覆盖测量 + 暂停菜单命令通道）

**一句话**：`code_match cover` 第一次拿**当前宿主**量了整机字节覆盖（逐字节 795,218 B，含重定位空隙 71.0%），并逐单元定位到缺口；暂停菜单的四个 `Command` **不是** `.text` 里的字面量 switch，下一步应走 `Do_Command`（签名零风险），不要先去猜 UI 函数。

### 13.1 整机字节覆盖（对 `bin/gametop/game.exe`）

```bash
python tools/code_match.py cover bin/gametop/game.exe build/host_lcl/magnet.exe --tail 0x521000
# 精确串 4280 段 / 792206 B (52.6%)
# + 同位空隙 275470 B
# 归因 1067652/1507136 = 70.8%   目标侧 1067652/1764864 = 60.5%
# --tail 0x521000 之后：149934/585216 = 25.6%

python tools/code_match.py units bin/gametop/game.exe build/host_lcl/magnet.exe
# 精确 795218 + 空隙 275470 = 归因 1070688/1507136 = 71.0%
```

两次跑的口径差 3,012 B（792,206 vs 795,218），来自精确串合并方式，不是测量误差方向的问题；引用时写清是哪一条命令。

逐单元（`units`，只列判断用得上的）：

| unit | size | hit | % |
|---|---|---|---|
| translations.o | 22320 | 21213 | **95.0%** |
| extctrls.o | 20640 | 19036 | 92.2% |
| intfgraphics.o | 51552 | 46080 | 89.4% |
| wsfactory.o | 16480 | 14682 | 89.1% |
| controls.o | 127744 | 113347 | **88.7%** |
| stdctrls.o | 34768 | 30451 | 87.6% |
| GLScene.o | 44192 | 36459 | 82.5% |
| forms.o | 55712 | 41479 | 74.5% |
| system.o | 54256 | 38329 | 70.6% |
| classes.o | 62416 | 41392 | 66.3% |
| **sysutils.o** | 40512 | 19199 | **47.4%** |
| OpenGLAdapter.o | 33840 | 2086 | 6.2% |
| OpenGL1x.o | 21776 | 482 | 2.2% |
| luabind.o / magnet.o | — | 0 | 0.0%（我方代码，应然） |

**读法**：

1. **没有一个单元到 100%**，但也没有一个单元接近 0（除 GL 后端与自有代码）⇒ 尺子已经对到"同一代"，差的是每单元都有的小量。
2. `sysutils.o` 47.4% 相对 `controls.o` 88.7% 低 41 个点，**不像全局 flag 差异**（那会全体一起掉），更像这个单元单独用了另一组选项或另一个 patch 级。若要把缺口收敛，先查它。
3. `OpenGLAdapter` / `OpenGL1x` 2–6%：先确认原版到底链没链这两个单元（也可能命中的只是巧合字节），不要当缺口追。
4. 边界：`cover` 的"同位空隙"带重定位容忍（每 4 B 字不同率 ≤30%），只有"精确串"部分才是逐字节；引用 71.0% 时必须同时写"其中精确 795,218 B"。

### 13.2 暂停菜单：`lmenugui.txt` 的四个 Command

`work/pak_gametop/lmenugui.txt`（`pak_baseline` 同）把暂停面板的按钮写成**数据**：

| Command | PosX | PosY | 备注 |
|---|---|---|---|
| 101 | —（默认） | — | 位置默认 ⇒ 最上，候选 Continue |
| 104 | -160 | 46 | ActionRegionHeightPercent=0.6 |
| 105 | -150 | 130 | 同上 |
| 103 | -153 | 216 | 同上 |

PosY 46 / 130 / 216 等距 84 ⇒ 纵向按钮列，与 F294 的 `(0.80,0.092)` Continue 命中一致。

**新发现（否定）**：在 `game.exe` 的 `.text` 里按 8/16/32 位比较编码扫 101/103/104/105（`3C`、`3D`、`66 3D`、`81 F8`、`83 F8`、`81 FA`、`83 FA`、`81 F9`、`83 F9`、`81 FB`、`83 FB`），四个立即数**没有任何 2 KB / 4 KB 窗口内聚在一起**（2 KB 与 4 KB 都试过，簇数 0；各值单独命中 4–7 次，多数应是无关常量）。

⇒ 暂停菜单的命令分派**不是字面量 `switch`**。剩下的可能：字符串 `"101"` → atoi/哈希 → 表索引，或 `.rdata` 跳转表。**别再按"找 cmp 某个数"的思路找下去。**

脚本是一次性的，未入库；要复现就重写这段扫描（十几行）。

### 13.3 建议下一步（按代价排序）

1. **先试 `Do_Command`。** F239 已恢复它的参数形态（`4..3+arg3`），签名零风险。宿主侧：载入任一关 → Lua 里调 `Do_Command(101)` → 用 `tools/draw_ab.py` 或 `uistate` 的暂停判据（F294，`lmenu_1.png` 资产级 NCC）跟暂停帧比。成 ⇒ 结束；不成 ⇒ 第 2 条。
2. **找 `lmenugui.txt` 的解析点**：谁读 `Command` 字段、怎么转成数、交给谁。这是数据驱动入口，找到等于拿到一张命令表，比猜函数安全。
3. **真要直调 UI 函数**：签名必须机械恢复（prologue 里 eax/edx/ecx 谁在被写之前被读、结尾 `ret` vs `ret N`、有无 `[esp+N]`），并且**从游戏自己的线程调用**（`CreateRemoteThread` 的新线程里 GL 上下文与当前关卡对象都不对），调用前后各存一次状态摘要。
   - 理由：约定错**不必然崩**。`ret N` / `ret` 弹栈量不同会让栈歪，或写进错误对象，然后还能跑十几秒 —— 录下来就是一份错基线。F111→F112 就是这么作废的（cdecl 调 `__usercall` 拿到"合理垃圾"）。

### 13.4 输入驱动（备查，暂不施工）

- **Syringe 本体不做输入**：`CreateProcess` 挂起 → 注入 DLL → 打补丁 → 恢复线程。这三步 `tools/inject_dll.py` 已经是同一套（`VirtualAllocEx` → `WriteProcessMemory` → `CreateRemoteThread(LoadLibraryA)`）。
- 若要走"进程内替换输入源"：游戏只用 user32 的 `GetCursorPos`/`GetAsyncKeyState`/`GetKeyState`/`GetKeyboardState`/`SetCapture`（F159），可 IAT hook，`SetCapture` 要一并接管。**user32 是 KnownDLL，代理同名 DLL 抢不到**（F147 的 ole32 同款坑）⇒ 只能 IAT/inline hook。
- 现状 `tools/uistate.py:363` 是 `SetCursorPos` + `mouse_event`：受前台窗口、DPI 缩放（F307 的 1.5×）与时序抖动影响，且会抢用户的鼠标。

### 13.5 边界

- 13.1 的数字绑定 `build/host_lcl/magnet.exe`（2026-11-01 14:20 构建）与 `bin/gametop/game.exe`；任一侧重编都要重测。
- 13.2 的否定结论只覆盖 `.text` 内的立即数比较；字符串比较、表索引、别的段都未排除。
- 本节未改动任何 `bin/`、`work/` 下的既有产物。

## 14. 本轮（2026-11-01，T8 oracle 自动化 D1–D5）

**一句话**：A/A 地板落盘、覆盖选样入口化、重放器 5.0×、**87 个导出的合成契约 0 差异**；并行度提升被证伪（14 路比 8 路慢一倍）。

```bash
# 地板：原版 DLL 重放 57 份，键含原版 md5（不变就不重算）；一次性 ~22 min
python tools/sweep.py --floors && python tools/report_sweep.py --write
# 之后普通 sweep 自动把 floor 标注进 work/sweep.jsonl（判定口径不变）

# 覆盖表 + 选样：改 b2physics 后先跑这个，不要直接全量
python tools/gen_rec_exports.py --from-probe work/oracle_cost_probe.json   # 或全量解析 ~2 min
python tools/rec_pick.py --changed HEAD~1 --budget 90     # diff 抓 b2_*，按「净增覆盖/秒」贪心
python tools/verify.py --changed HEAD~1 --only physics:changed

# 合成契约：87 个导出各点一次（不启动游戏/代理），<1 s
python tools/verify.py --only b2:contract
PY32="C:/Users/K/.local/bin/python3.12.exe" "$PY32" tools/b2_contract.py build/Release/b2Physics.dll bin/gametop/b2Physics.dll
```

判据（已跑通）：`work/floors.json` 57 条（54 可判定，**唯一非零** `rec_20261028_231623`=5,297，与 F125 逐项相同）；`rec_pick --exports b2_Body_SetBullet` → 1 份 `rec_20261028_231336`（现 4.4 s）；`verify --changed ca58de5^ --only physics:changed` → PASS（0.3 s）；**D4**：全量 57 份 **220.7 s**（原 15–17 min）、单份 135534 5.5→1.5 s、231623 535.7→61.1 s，57 行除 `secs`/`build`/`floor` 逐字段不变（F312）。

**D5 抓到 5 处 ABI 错误（F314）**：契约探针第一次给「宿主从未调用」的 15 个导出上判据，当场暴露 `b2_Shape_GetFilter` 实为 **(out, shape)**（原实现会把 6 字节写进 shape 头部）、`b2_Body_DestroyShape` 实为 **(body, shape)**、`b2_Body_GetMass` 的 cx/cy 是**局部**质心、`b2_Shape_GetShapeType` 是 0/1、Revolute/Prismatic 的 def 是「几何 → collide → limit → motor」。负例：把 `b2_GetMaxPolygonVertices` 入口改成返回 `0xDEADBEEF`，探针报 1 差、rc=1。

坑：
- **契约探针能抓 ABI，但只能靠「原版行为」当规格**（F314）：这些导出从没被宿主调用过，签名/布局没有第二来源；`b2_Shape_GetFilter` 的参数顺序、`b2_Body_DestroyShape` 的 (body, shape)、两个关节 def 的 byte 偏移，全是拿 IDA 反汇编 + 逐字节置 1 探测出来的。改这类导出前先跑 `b2:contract`。
- **原版不少导出的返回值是 `bool`（只写 AL）**：`IsBullet`/`IsFrozen`/`GetIsSleeping`/`GetSensor`/`SetSensor`/`IsLimitEnabled`/`IsMotorEnabled`。按 int 读会把 EAX 高位垃圾当值；探针对这些只比低字节。
- **热路径里别写文件、别查环境变量**（F312）：原先每 8 条调用 `PROGRESS.write_text`（97k 调用 → 1.2 万次 `open`，占 28%），外加每条调用查 3 个 `os.environ`（29 万次）。`PROGRESS_EVERY` 默认已改 5,000；要精确定位崩溃点用 `PROGRESS_EVERY=8 --start N` 重跑一小段。
- **并行不是越大越快**（F309）：14 路 wall **2,080 s**，8 路 15–17 min；总重放量 7,109 → 25,718 s（3.6×）。瓶颈是磁盘/内存带宽（10 核/16 线程/16 GiB）。默认 `min(8, cpu//2)`。
- 「大日志限 2 并发」用**阻塞信号量**会饿死 worker（14 个 worker 全抢巨日志、12 个阻塞在 `Semaphore(2)`，2m19s 0 行完成）——要限流请用独立 executor。
- `rec_pick` 的成本取 `sweep.jsonl` 的 `secs`（8 路并发实测；单跑快 2–4×）⇒ 预算偏保守。
- **覆盖 ≠ 区分**：选样只保证「该导出在这份日志里出现过」，不保证能暴露你的 bug。
- 29 个导出目前没有判据（14 个 getter 被 `kHotGetters` 过滤、15 个从未被调用，F308）⇒ 下一步 D5 合成契约探针，或 `B2PROXY_HOT=1` 录一份 getter 会话。
