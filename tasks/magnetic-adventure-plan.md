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
- [ ] T2.4 `Squall` 导出表 + DSound 行为契约 依据：F06
- [ ] T2.5 C++ 实现 Squall，PCM 输出 diff 依据：F06
- [ ] T2.6 原 exe + 新双 DLL 整机回归 依据：F06、F07

## M3 宿主复刻（L0 + L1）

- [ ] T3.1 Win32 窗口/消息/输入（参数对照原 exe） 依据：F01
- [ ] T3.2 OpenGL 上下文 + GLScene 等价渲染层 依据：F03
- [ ] T3.3 pak 加载 + Lua 状态机 + 绑定 API 依据：F04
- [ ] T3.4 场景/实体/物理/音频接线 依据：F03、F06、F07
- [ ] T3.5 文本渲染路径 依据：F11
- [ ] T3.6 配置/存档写入（`cfg.ini` 等） 依据：F01

## M4 行为对齐验收

- [ ] T4.1 确定性输入回放 harness 依据：F03
- [ ] T4.2 GL 调用序列 diff + 像素 diff 依据：F03
- [ ] T4.3 音频 PCM diff 依据：F06
- [ ] T4.4 存档字节 diff 依据：F01
- [ ] T4.5 映射覆盖率报告 依据：F01
- [x] T4.6 重录 `Get the Map` / `The First Totem`（现只剩 v01 日志，不可作判据） 依据：F99、F100（已完成，F101）
- [ ] T4.7 用 `tools/dist_probe.py` 沿法线平移 B 扫出原版 `b2Distance` 误判为 0 的边界，并调两边内部 `Support`(`0x100144C0`)/`ProcessTwo`(`0x10009160`)/`ProcessThree`(`0x100092F0`) 定位误判发生在哪一步；反汇编锚点：poly-poly 泛型 `0x1000AB00`/`0x1000A5E0`、`b2TimeOfImpact=0x10018B20`、`b2_World_Step=0x10001490` 依据：F102、F107、F108

## M5 汉化目标

- [ ] T5.1 汉化版资源作为交付资产（不改原 pak） 依据：F08
- [ ] T5.2 中文文本/字形核对 依据：F08、F11
- [ ] T5.3 交付包形态（`cfg.ini`、`images/`、`Uninstall/`） 依据：F09

## 变更记录

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
