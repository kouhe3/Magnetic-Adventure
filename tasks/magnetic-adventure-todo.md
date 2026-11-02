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
- [ ] T6.4b 输入/拖拽：录轨迹 → 重放 → `b2_sites compare` 依据：F159、F189、F263（判据：`TOTAL mismatches=0`）
- [x] T6.4b-0 逐关采关（52 关，47 PASS / 2 SHARED / 3 RNG） 依据：F347–F349
- [x] T6.4b-0a 采集默认 WM_CLOSE + NOP 广告（level 1 PASS） 依据：F352–F355
- [ ] T6.4c 存档/配置写入（`profile.py diff` → `diffs=0`） 依据：F01、F171
- [ ] T6.4d 游戏循环/状态机（`uistate` 状态序列 + 切换时刻） 依据：F169、F171、F172、F177
- [ ] T6.4e 关卡文本（`pt_sans*.dat` / `gulim2.dat`，判据同 T6.4a 的 draw 列表） 依据：F11、F192、F231
- [ ] T6.5 整机 A/B（GL 序列 + 存档 + 像素验收） 依据：F181、F194、F196

## M7 函数级测量与替换

- [x] T7.0 跨模块 RTL 实测 依据：F244–F248
- [x] T7.1 应用层清单减法（1,012 函数 / 60,868 指令） 依据：F236–F238
- [ ] T7.2 `hosttrace` 注入记录器 依据：F232–F235
- [x] T7.2a 竖切：一个纯函数的 注入→pre/post→A/B（A/A + 负例；裁决应用层形态） 依据：F233、F234、F244–F248
- [x] T7.2b 崩溃捕获：first-chance VEH + minidump + `#32770` 弹窗正文（默认零成本；`CRASHLOG_DIR` 开启） 依据：F315、F316、F317
- [ ] T7.2c 补齐剩余 472 个 direct_method 的 `Self` 类（运行时入口 EAX/VMT 采样 + 更深数据流；静态已到 540/1,012） 依据：F319、F320
- [ ] T7.3 双跑 A/B 依据：F233、F234
- [ ] T7.4 纯函数输入空间扫描 依据：F233
- [ ] T7.5 批量替换 + 覆盖率台账 依据：F204、F232
- [ ] T7.5a 覆盖普查：1,012 函数的语料命中分布（`mapping/fn-hits.csv`；verified/covered/uncovered 三类分开报） 依据：F292、F236、F291
- [ ] T7.6 混合产物整机回归 依据：F181、F213

## 暂缓（不在队列里）

- 见 `tasks/backlog.md`：PCM 逐位、残余 1 ULP、T0.3/T0.4、M3 遗留。回流时先补 oracle + 二值判据，再进上面的队列。
