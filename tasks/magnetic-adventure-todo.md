# TODO — Magnetic Adventure 复刻

> 当前队列（2026-11-02 裁决）：T6.4a ✅ → T6.4b/c/d/e/f → T6.5；T6.4a-r（通用化/动画/其他关卡）与 b/d 并行；T7.2 作工作台并行，T7.3/T7.5 等 T6.4b/d 就绪。依据：`tasks/magnetic-adventure-plan.md` 变更记录 2026-11-02。

## M0/M1 资源与规格

- [x] T0.1 pak 记录字段规格（动态断点） 依据：F05、F13
- [x] T0.2 汉化落点归因（两版对照运行） 依据：F08
- [ ] T0.3 IDA：b2Physics.dll + game.exe 导出 依据：F01、F02、F07
- [ ] T0.4 oracle 采集（帧/PCM/存档/窗口参数） 依据：F03、F06
- [x] T1.1 tools/pak 只读解析 依据：F05
- [x] T1.2 Lua 源码导出 + diff 依据：F04
- [x] T1.3 资产索引 依据：F06、F08

## M2 DLL 源码化

- [x] T2.1 b2Physics ABI 契约 依据：F07
- [x] T2.2 b2Physics C++ 实现 依据：F07
- [x] T2.3 物理差分（53 份录制全量重放） 依据：F07、F99
- [x] T2.4 Squall 行为契约（T2.4a–d 全完成） 依据：F06、F131–F152
- [x] T2.4a `vendor/squall` 入库 + Win32 构建 + 导出 99/99 依据：F131、F132、F137
- [x] T2.4b 补 libogg/libvorbis，解 pak 内 OGG 依据：F133、F134、F137
- [x] T2.4c Squall 代理 DLL 抓包（启动/关卡/退出路径） 依据：F131、F139、F140、F143
- [x] T2.4d 游戏内覆盖 16/17（剩 `Sample_LoadFile` 由探针补） 依据：F144、F151、F152
- [ ] T2.5 Squall 实现（已完成）与输出对拍（已完成 F149/F150）；剩 PCM 逐位（F147 三条路线均否） 依据：F06、F137、F147
- [ ] T2.6 原 exe + 新双 DLL 整机回归 依据：F06、F07
- [x] T2.6a 整机冒烟（tutorial 到结局页、模块 md5 核对） 依据：F141
- [ ] T2.6b 多关/长时回归（优雅退出路径已由 F143 覆盖） 依据：F141、F143

## M3 宿主复刻

> 冻结（2026-11-01）：T3.1/T3.2/T3.3/T3.4 已被 M6 逐项取代，不再执行；T3.5/T3.6 改挂 T6.4e/T6.4c。见 plan 的 M3 冻结说明。

- [ ] T3.1 Win32 窗口/输入 依据：F153–F159、F164、F166（脚手架 + 门禁 `fields=15 diffs=0`，外框/边框逐字相同；剩输入接场景、全屏分支）
- [ ] T3.2 渲染层（里程碑 A：宿主画出主菜单，mean 1.40/255） 依据：F03、F177、F178、F183、F184
- [x] T3.2c 纹理直接读 pak（WIC 解码，上传像素 37/37 与原版逐字节一致） 依据：F135、F183、F185、F187
- [x] T3.2d 菜单布局参数化（宿主现算设计空间布局 + 二态悬停，draw A/B 13/13 零偏差） 依据：F161、F182、F184、F188、F189、F190
- [x] T3.2a GL 代理侦察（368 导出转发 + 名称/QPC/实参记录） 依据：F03、F158、F175、F176
- [x] T3.2b GL payload 解码 + 绘制列表（`tools/gl_drawlist.py`，26–27 draw/帧） 依据：F176、F178、F179、F181、F186（prim 勘误：是 GL_QUADS；12 顶点文本串按 fan 画会连成蝴蝶结）
- [ ] T3.3 pak + Lua 绑定 依据：F04、F191（第一切片：vendor Lua 5.1.5，111/111 脚本编译通过、52 关清单已解析；剩 144 绑定与执行语义）
- [ ] T3.4 场景接线 依据：F03、F06、F07
- [ ] T3.5 文本渲染 依据：F11
- [ ] T3.6 配置/存档 依据：F01

## M4 行为对齐验收

- [ ] T4.1 输入回放 harness 依据：F03
- [ ] T4.2 帧 diff 依据：F03
- [x] T4.3 音频 diff（输出层，环回 A/B 逐秒 corr 0.9998–0.9999） 依据：F06、F149、F150
- [ ] T4.4 存档 diff 依据：F01
- [ ] T4.5 映射覆盖率 依据：F01
- [x] T4.6 重录 `Get the Map` / `The First Totem` 依据：F99、F100、F101
- [x] T4.7 （路线已作废）`dist_probe` 边界扫描（cdecl 约定错误见 F112，根因见 F122） 依据：F102、F107、F108
- [ ] T4.8 残余 1 ULP：`Good Shot!` 的 `lvy`（首发 4847、bad 4,825，该录制 A/A 地板 0） 依据：F128
- [ ] T4.9 PCM 逐位（阻塞：dsound 文件代理 / 代理内 IAT / 日志重放三条路线均否） 依据：F134、F147

## M5 汉化目标

- [ ] T5.1 汉化资产 依据：F08
- [ ] T5.2 中文核对 依据：F08、F11
- [ ] T5.3 交付包 依据：F09

## M6 宿主重建（主线：FPC/LCL + GLScene，F213/F214 拍板）

- [x] T6.1 窗口层：LCL 复刻原版 15 个窗口字段 依据：F214
- [x] T6.2 场景/渲染 + 菜单层（21/21 draw 零差） 依据：F225–F231
- [ ] T6.3 Lua 144 绑定 + 事件 + 真实物理（a0–a2/b1/b2 已完成） 依据：F239–F243、F273、F274、F276
- [x] T6.3c 真实物理接触：world + 14 个对象 body/shape → joint → `OnAddContact` 依据：F276、F277（oracle：The Teleport 14/14 建体逐项对齐，20 个 shape 常量已读出；剩项（真实玩法输入/力驱动）已归 T6.4）
- [x] T6.3d 工厂覆盖扩展（52 关扫描：**50 PASS / 2 SKIP / 0 MISMATCH**，F336） 依据：F283–F290、F333–F336（`tools/phys_sweep.py` 已默认无头 `HOST_HEADLESS=1`，52 关 12.5 s；`Add_Rope` 10 关 + HammerParts 双 body 已接；`Good Shot!` 重录 + `Add_Ball` 已接；13/51 为 shared SKIP）
- [ ] T6.4 应用层复原（菜单/关卡/存档/输入） 依据：F204、F213
- [x] T6.4a 关卡渲染：Introduction frame 9600 逐 draw **25/25 mismatches=0**；仪器 `level_draw_ab` 自证 A/A/负例；内存判 MENU 依据：F337–F340（菜单回归 21/21，`verify` 7/7，`phys_sweep` 50/2/0）
- [ ] T6.4a-r 关卡场景通用化：Lua→场景生成、齿轮/提示动画、其他关卡 依据：F339、F340（第一关瞬时态已过；先做生成器）
- [x] T6.4a-r-0 逐关 GL 绘制 oracle 探测（level 1 A/A：静态 29/29 零差；动态=alpha 淡入/光标；负例 loading 帧 `unmatched_ref=29`） 依据：F356
- [x] T6.4a-r-1 升仪器 `tools/capture_gl_levels.py`（逐关窗口 + settled 帧 + 静态/动态分列；纹理解析缓存；level 2 A/A 47/47） 依据：F357
- [ ] T6.4a-r-2 通用场景生成器（52 关 50 个 `Add_*` 工厂；先 level 0/1，判据静态 draw 零差） 依据：F356、F340
- [x] T6.4a-r-2a 工厂→draw 配对（graph 层 = 参数 − 有效相机、world 层 = 参数；层归属未归因） 依据：F358
- [x] T6.4a-r-2b 归因层规则（半视图偏移 ±28.24/±20.5；front/hints=屏幕层、medium/back=世界层） 依据：F359
- [x] T6.4a-r-2b2 给四个 graph root 赋稳定 id（1..4），probe + host 记录 parent（2,339 次调用 0 差；宿主 52/52） 依据：F360
- [x] T6.4a-r-2c `tools/scene_from_lua.py` Python 场景模型（已实现子集：level 0 19/19、level 1 18/18 零差；负例 shift=5） 依据：F361
- [x] T6.4a-r-2c2 补齐齿轮/钉/螺丝/SimplePhysicObject/HudButton（level 0 25/25、level 1 29/29 静态 draw 零差） 依据：F362
- [ ] T6.4a-r-2c3 HUD 烟雾/level_end_box（level 1 该帧隐藏；其他帧可见时再接） 依据：F362
- [x] T6.4a-r-2c4 level 2 扩关探针（gear_1/gear_11、世界层 (0,-4)、45/5；剩 SwitchArm/圆/时钟箭头/层划分） 依据：F363
- [x] T6.4a-r-2c5 `Get_RealViewRect` 语义（相机 ± 半视图）+ 相机偏移/`Set_ScrObjPos` 回放：level 2 46/46、level 0/1 无回归 依据：F364、F365
- [x] T6.4a-r-2c6 `Add_SwitchArm`（`sw_arm1.png` 4×2、锚点半径 1.6、动态摆角拟合；level 2 47/47） 依据：F366
- [x] T6.4a-r-2c7 扩关 level 3/4：WoodBox/PushButton+平台/BarDoor/SwitchArm style 2（静态 53/53、37/37；动态项单列） 依据：F367
- [x] T6.4a-r-2c8 齿轮动画机制：`w_child=-w_parent/ratio`（level 0 实测 1.699/-1.275/1.530；level 1/2 静态） 依据：F368
- [x] T6.4a-r-2d0 Pascal 场景模型（`src/host_lcl/scenemodel.pas` + CLI）：5 关与 Python 逐对象一致（15/21/37/45/33） 依据：F369
- [x] T6.4a-r-2d 移植到 `levelscene.pas` 通用生成器（`HOST_LEVEL_MODEL`；level 1 逐 draw 29/29 零差） 依据：F369、F370
- [x] T6.4a-r-2e0 宿主自产 Lua 日志驱动渲染（level 1：149/149 绑定、29/29 draw） 依据：F371
- [x] T6.4a-r-2e1 齿轮速度移植（SceneModel 传播 `w_child=-w_parent/ratio`；1.7000/−1.2750/1.5300） 依据：F372
- [x] T6.4a-r-2e 齿轮绝对相位：π sprite 偏移 + `HOST_LEVEL_TIME`（level 0 25/25） 依据：F373
- [x] T6.4a-r-2f0 摆臂 settle 规则（init+0.5 + 锚点半径 1.6；level 2 47/47、level 4 arm2 PASS） 依据：F374
- [x] T6.4a-r-2f1 level 4 齿轮相位（t=0.689，37/37 零差） 依据：F375
- [x] T6.4a-r-2g 5 关静态渲染覆盖（25/29/47/53/37 全零差；宿主自身日志） 依据：F376
- [x] T6.4a-r-2f2 level 3 train/smoke：`DoProgress` 第一段圆弧 + smoke 相位（Python/宿主 frame 357 `mismatches=0`；`--time 1.52` 负例 2） 依据：F427、F428
- [x] T6.4a-r-2f level 4 plunger/shank（曲柄滑块解析位姿）与 smoke 静态 sprite（F378/F379；宿主/Python 44/44，2a+2b 双采集） 依据：F376
- [x] T6.4b-1 宿主磁铁力：`PhysApplyForce`（`b2_Body_ApplyForce`）+ `NearestBody` + `HOST_MAG_BUTTON/X/Y`；level 1 `target=1001 moved=2.511224`，负例 `target=0 moved=0` 依据：F440
- [x] T6.4b-2a `OnMove` 派发：`EventsFireMove` + `Tick` 磁铁施力/位移检测；level 1 私有桌面 `onmove_calls=38`，负例 `HOST_MAG_BUTTON=0` → 0 依据：F444
- [x] T6.4b-2b-0 `Get_ScrObjPos` graph 回退：`ScrPosLookup` + `TLevelScene.GetSpritePos`；level 1 `id=1004 x=-9 y=10.19`，负例 id=0 无日志 依据：F445
- [x] T6.4b-2b 测试关真实完成链：`test_lvl_o/e` + `Tick` 检测 `LevelComplete` → 存档 `1→2` → 回菜单；正例 trace `boot,menu,level,menu,exit`，负例 mag=0 无完成 依据：F446
- [x] T6.4b-3a 运行时 gear 图形：`Spawn` 队列 + `TLevelScene.AddRuntimeGear`；`spawn.log calls=1 created=1`、`scrpos_get id=1004` 可读；负例 mag=0 无日志 依据：F447
- [ ] T6.4b 输入/拖拽：**行为级已通过**（level 1 两段拖拽 + “Level completed”，F380/F381；`work/drag_lvl1.py`/`drag_shot.py`）；剩：宿主重放 + `b2_sites compare` 力/step + 绕障寻路 依据：F159、F189、F263（判据：`TOTAL mismatches=0`）
- [x] T6.4b-0 逐关采关（52 关，47 PASS / 2 SHARED / 3 RNG） 依据：F347–F349
- [x] T6.4b-0a 采集默认 WM_CLOSE + NOP 广告（level 1 PASS） 依据：F352–F355
- [x] T6.4b-x IAT 假磁铁：`GetCursorPos` 槽 `0x667330` / `GetAsyncKeyState` 槽 `0x66730C` 伪造按下+光标 ⇒ 命中测试、target 锁定与力律全走游戏自己（无真鼠标 ⇒ 采样源无竞争，不会被清零）。**已收口**：实现 `src/proxydll/proxy_core.c`（`B2CI_FAKE_MAGNET`/`B2CI_MAG_CONFIG`/`B2CI_MAG_TRACE`），驱动 `work/fake_magnet_drive.py run`；判据 ① 的力幅按 F386 修正为 `min(315,30·d)`（d>10.5 时 315±4.6e-5；244 行，方向 ≤0.065 rad）；② level 1 两段 d<0.548 + 完成面板（5/5）；③ 负例 A `target_events=0`/磁铁 ApplyForce=0/body 位移 0.000；④ 负例 B 空点按住 target/flag=0。依据：F341、F346、F381、F382、F385、F386
- [x] T6.4b-x-y 假磁铁 CI 仪器 + 运行时生成夹具：`tools/ci_fake_magnet.py`（build/run、多 stage、私有桌面、逐 step digest 最小距离、marker/force/runtime 三类判据）+ `tests/levels/chain_o.lua`/`chain_e.lua`（`OnMove` 回调在关卡运行中生成第二颗螺丝与目标）。正例 pid 10048：两段 `d_min=0.2868/0.5974`、markers=2、ApplyForce 315 行、`fg_game_events=[]`、PASS；负例 `--done-dist 0.1` / `--marker 77,77` / `--runtime-stage 0` 全 FAIL。依据：F407
- [x] T6.4b-x-z 障碍夹具 wall + waypoint 绕行：`tests/levels/wall_o.lua`/`wall_e.lua` + 仪器 `--waypoint`。直线负例 `d_min=6.8912` 无 marker ⇒ FAIL；两次正例 `d_min=0.5733/0.5900`、markers=2 ⇒ PASS。依据：F408
- [x] T6.4b-x-g 齿轮力矩夹具 + observe 模式：`tests/levels/gear_o.lua`/`gear_e.lua`/`gear_nomotor_o.lua`/`gear_nolink_o.lua` + 仪器 `--observe/--angle/--gear-ratio`。正例 Δ1=2.55、Δ2=-3.1875、ratio=1.25000007 ⇒ PASS；no-motor/no-link 均 FAIL。依据：F409
- [x] T6.4b-x-s 开关旋转夹具 + 阶段角度判据：`tests/levels/switch_o.lua`/`switch_e.lua` + 仪器 `--stage-angle/--stage-min-angle/--ignore-distance`。正例 Δangle=-0.5250、markers=2 ⇒ PASS；过枢轴负例 Δ≈0、markers=0 ⇒ FAIL。依据：F410
- [x] T6.4c-0 存档工具多玩家感知：`tools/profile.py` `players/get/set/diff` + `--player/--file`。A/A=0；`set SoundsVolume 7 --player KKK` 后 diff=1 且 `ooo` 不变；默认 Active 选择正确。依据：F411
- [x] T6.4c-1 宿主读 Active 玩家档案（只读）：`HOST_PROFILE` + `profiledata.pas`；正例 user=KKK/level=20、三条负例、两次启动 cmp=0 依据：F434
- [x] T6.4d-0 状态轨迹 + 地板：`direct_drive.py --trace` + `tools/trace_diff.py`。两次运行序列相同，dt=-62/-407/-411 ms，tol 600 PASS；exit+1000 负例 FAIL；level→exit 1765/1769。依据：F412、F413
- [x] T6.4d-0b win/complete 状态：`lm`/`app`/`mgr` dword 无翻转；图元 +1 是烟花；`+0x1F0` 可见性无翻转；F416 的 `+0x30`/`+0x2f0` 候选**已证伪**（F425：未完成 4 关 nonzero=98/99/99/99，通用滑动倒计时）。**完成锚点 = `TGraphObjectList` 里的 `TGlAlphaHudSpriteObject`（bEndLevelBox，size 0x30）的 `+0x2C` 0→1.0**（F426：`Do_ShowCommand` 0x59A0B0 → vmt[0x50] 0x5937C0 case 0x17 写 +0x2C；原版完成 timing2 +5.01 s 0→1.0），已并入 `direct_drive --trace` 的 `complete`（正例写字段 1.0 后 1.0 s 记录、1.5 s 复位回 level；负例未完成 6 s 无）。依据：F414、F415、F416、F425、F426
- [x] T6.4d-0b2 完成链 CI 驱动稳定性：完成信号修正为任一 size-0x30 HUD sprite 的 `+0x2C` 相对基线 0→1（`bHintComplete`；`bEndLevelBox` 恒 0）；no-nudge 3/3 + nudge 3/3 PASS，检测 2.91–2.97 s。依据：F430、F431
- [x] T6.4c-2 宿主完成写副本档案：`WriteLastCompleteLevel`（UTF-16LE+XOR 0xB8/逐行替换）；level 3 完成 → 副本 `3 -> 4`、`profile.py diff` 仅一行；负例 `HOST_SAVE_PROFILE=0` diff 0 依据：F441
- [ ] T6.4c 存档/配置写入（`profile.py diff` → `diffs=0`） 依据：F01、F171
- [x] T6.4d-1 宿主 `HOST_CLICK` → 按档案 LastCompleteLevel 进关 + `HOST_TRACE`（进程内命令入口）：正例 index=20/3、lua_bind_ab 0 差、两次序列相同；点空白/无档案/坏档案/51 四条负例无 level 依据：F435
- [x] T6.4d-2 LCL 真实点击 + 运行时场景切换：`THostMouseHandler` 命中 Play → `TMenuScene.Clear`/`Free` → `BuildFromModel`；正例 index=20/3、sprites=21/60、lua_bind_ab 0 差；点空白/坏档案无 level 依据：F436
- [x] T6.4d-3 宿主进关后物理步进 + 图形同步：`PhysStart` → `HOST_PHYS_STEPS` → `SyncPhysics` → `phys.log`；level 0 bodies=3/objects=15 angle_moved=3 sync_after=0，负例无 phys.log 依据：F437
- [x] T6.4d-4 持久 Lua state + `DoProgress`：`HOST_KEEP_LUA=1` 保留 state，`EnterLevel` 每步 `PCall('DoProgress',0.01)`；level 3 calls=100 rc=0、lua_bind_ab 187/187、sync_after=0；负例 `HOST_LUA_PROGRESS=0` 无日志、`HOST_KEEP_LUA=0` calls=0 依据：F438
- [x] T6.4d-5 完成信号 + 返回菜单：`bind_Do_LevelComplete` 置 `LevelComplete`，`ExitLevel` 清关卡/重建菜单；trace `boot,menu,level,menu,exit`、`menu_after layers=21`；负例 `HOST_FIRE_COMPLETE=0` 无第二个 menu 依据：F439
- [x] T6.4d-6 持续帧循环：`THostLoop` + 16 ms `TTimer`，`HOST_LOOP_MS` 到时写 `loop.log`；level 3 `steps=39 calls=39 ms=1016`；负例 `HOST_LOOP=0` 无日志 依据：F442
- [x] T6.4d-7 `Set_ScrObjPos` 接 sprite：`ScrPos` 队列 + `TLevelScene.SetSpritePos` + `Tick` 应用；level 3 `scrpos_calls=74 scrpos_moved=37`，负例 `--progress 0` → 0/0 依据：F443
- [ ] T6.4d 游戏循环/状态机（`uistate` 状态序列 + 切换时刻） 依据：F169、F171、F172、F177
- [x] T6.4e 关卡文本：范围核实（GameTop 不引用 `pt_sans`；关卡名/完成文本是烘焙图；动态文本只剩用户名；gulim2 无消费者） 依据：F432、F433
- [ ] T6.5 整机 A/B（GL 序列 + 存档 + 像素验收） 依据：F181、F194、F196

## M7 函数级测量与替换

- [x] T7.0 跨模块 RTL 实测 依据：F244–F248
- [x] T7.1 应用层清单减法（1,012 函数 / 60,868 指令） 依据：F236–F238
- [ ] T7.2 `hosttrace` 注入记录器 依据：F232–F235
- [x] T7.2a 竖切：一个纯函数的 注入→pre/post→A/B（A/A + 负例；裁决应用层形态） 依据：F233、F234、F244–F248
- [x] T7.2b 崩溃捕获：first-chance VEH + minidump + `#32770` 弹窗正文（默认零成本；`CRASHLOG_DIR` 开启） 依据：F315、F316、F317
- [x] T7.2c-0 布局交叉验证仪器：`tools/app_layout.py`（1 条错分 0x552CA0→TLogSession；真实布局重建 3/3；字节冲撞普查） 依据：F389–F393
- [x] T7.2c-0b 调试 HUD 抵达：`TDebugInfo` 主线程调用 `0x564760`（5 个可见位 0→1；MENU `65.17 FPS`，Level 1 `Start`） 依据：F403、F404
- [ ] T7.2c 补齐剩余 472 个 direct_method 的 `Self` 类（运行时入口 EAX/VMT 采样 + 更深数据流；静态已到 540/1,012） 依据：F319、F320
- [ ] T7.3 双跑 A/B 依据：F233、F234
- [ ] T7.4 纯函数输入空间扫描 依据：F233
- [ ] T7.5 批量替换 + 覆盖率台账 依据：F204、F232
- [ ] T7.5a 覆盖普查：1,012 函数的语料命中分布（`mapping/fn-hits.csv`；verified/covered/uncovered 三类分开报）。**入口探针并集 875/1,010（F419；52 关自动批次 +82）**；剩 209：direct 64、unreferenced 64、lua 36、address 21、state_dispatch 12、event 11、state_loop 1 依据：F292、F236、F291、F417
- [ ] T7.6 混合产物整机回归 依据：F181、F213

## 暂缓（不在队列里）

- 见 `tasks/backlog.md`：PCM 逐位、残余 1 ULP、T0.3/T0.4、M3 遗留。回流时先补 oracle + 二值判据，再进上面的队列。
