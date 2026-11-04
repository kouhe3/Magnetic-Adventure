# Backlog — 暂缓项（premise-gate §7.3）

> 规则：暂缓 ≠ 取消。每条带「为什么暂缓」与「回流条件」；回流时先补 oracle 与二值判据，再进 `tasks/magnetic-adventure-plan.md` 的队列。
> 建立日期：2026-11-01（依据：路线图全线过闸，见 plan 头部「路线图闸门」与当天变更记录）。

## A. 超出当前验收口径

- **PCM 逐位（T2.5 剩余 / T4.9）**
  - 暂缓理由：`docs/requirements.md` L2-A 的字面是「音频 PCM 差分」，F150 已给环回 A/B 逐秒 `corr=0.9998–0.9999`、RMS 差 <1%；三条逐位路线（`dsound` 文件代理 / 代理内 IAT / 日志重放）均已否（F147），且环回自身 A/A 就不逐位（F195：52.5% 样本差、`max|Δ|` 433）。
  - 回流条件：进程内 vtable hook（Detours 级）落地，或 WASAPI 环回能给出逐位 A/A 地板；且主线无更便宜的判据可补。
- **残余 1 ULP（T4.8，`Good Shot!` 的 `lvy`）**
  - 暂缓理由：差异 1 ULP 级，`no_crash` 与 `bounded` 均 PASS，属验收口径内的噪声地板（F128）。
  - 回流条件：物理层其余项收口后，或用户明确要求逐位。

## B. 历史遗留（已被新链路取代）

- **T0.3 IDA 全量导出表 / 函数表 / 字符串引用**
  - 暂缓理由：实际工作已按需用 IDA MCP 逐函数取（F201、F239），全量导出没有消费者；T7.1 的清单减法已给出函数级台账（F236–F238）。
  - 回流条件：需要「未导出函数全集」做一次全局规划时。
- **T0.4 oracle 采集（APITrace/RenderDoc 帧序列、PCM、存档、窗口/输入参数）**
  - 暂缓理由：已被 B2FFI02 / GLFFI02 / `objlog`（F270）/ `uistate` / `e2e_record` 分项覆盖；缺的只是「跨层同一时间线」。
  - 回流条件：需要 GL + 物理 + 音频 + 输入落在同一条时间线上对拍时（例如 T6.4b/T6.4d 卡在时序归因）。

## C. 路线冻结（对照物，不再执行）

- **M3 的 T3.1 / T3.2 / T3.3 / T3.4**（C++ 宿主实现）
  - 暂缓理由：F213 拍板转 M6，四项已分别被 T6.1 / T6.2 / T6.3 / T6.4 取代；C++ 宿主保留作对照物（窗口 15/15、菜单 mean|Δ| 1.088/255，F190）。
  - 回流条件：M6 在某个判据上覆盖不到、而 C++ 实现能覆盖时，单独取用（不恢复为主线）。

## D. oracle 自动化候选（2026-11-01 测量，依据 F308）

> 状态：候选，未开工。每条开工前按 premise-gate 在台账预注册 `待证` 行（假设 + 二值判据）。
> 反馈预算：单次判据 >5 s 的一律先摘掉无关面（无头/离线/子阶段）。

- **D1 每份录制的 A/A 地板落盘，判据改为「与地板比」**
  - 现状：`verify.py:18` 声称比较地板，`check_physics_sample` 只判 `verdict==PASS`；F125 已证明地板按录制分别是 0 / 0 / 5,297。
  - 改法：`sweep.py --floors` 用 `bin/gametop/b2Physics.dll` 重放每份录制，写 `work/floors.json`（键含原版 md5，原版不变不重算）；`report_sweep.py` 出 `floor` 列并删掉"原版自放 0 差异"总括句；`verify.py` 打印 `bad/floor`（是否升级成阈值先预注册）。
  - 判据：`floors.json` 57 条；`--only physics:sample` 输出含 `bad=…/floor=…`；负例（改坏角速度钳位）在 Slipgate 上 `bad` 显著高于 0。
  - 成本：一次性多跑 ~118 min（可分批/过夜），之后命中缓存。
- **D2 覆盖选样的快闸（迭代收益最大）**
  - 现状：改一个导出要确认只能跑 57 份（15–17 min）；快集 3 份只覆盖 33/58 观测导出（F308）。
  - 改法：把 `work/oracle_cost_probe.py` 产物固化成 `mapping/rec_exports.csv`（rec、calls、导出集合）；新增 `tools/rec_pick.py --exports … [--budget 90s]`，按「净增覆盖 / 预计秒数」贪心；`verify.py --changed <git-ref>` 从 diff 抓 `b2_*` 名字喂它。
  - 判据：冷门导出（如 `b2_World_Joint_Gear`）挑出 ≤3 份、预计 ≤90 s；同一构建下选定集判定与全量一致（子集 FAIL ⊆ 全集 FAIL）；负例：改坏 Gear → 选定集 FAIL。
  - 成本：约半天。
- **D3 并行度与调度**：`--jobs` 默认 `min(cpu-2, 14)`，>1 GB 日志限 2 并发。
  - 判据：`sweep --force` wall ≤600 s（同构建），除 `secs` 外逐字段与改前相同。
  - 收益：15–17 min → ~9 min（下界是最大单任务 543 s）。
- **D4 重放器热路径两处**：① digest 改 `string_at`+`unpack_from`（实测 3.0×）；② 参数翻译预编译成 per-export 计划表（raw/obj/scratch/zero）。
  - 判据：同一录制 `--json` 除 `secs` 外逐字段相同；`secs` 降 ≥30%；改后连跑两次逐字段相同。
- **D5 `b2:contract` 合成契约探针（补 29 个盲区，<1 s）**
  - 现状：58/87 被观测；14 个 getter 被代理默认过滤；15 个从未被任何会话调用（F308）。
  - 改法：仿 `tools/squall_contract.py`，在 32 位进程内按固定序列建 world/body/shape/joint 并调用全部 87 个导出，记录返回值/出参/关键状态，两侧各跑一次。
  - 判据：A/A diffs=0；跨 DLL diffs=0；负例（改坏 `SetMass`）该步 FAIL；耗时 <1 s。
  - 边界：只覆盖 API 层，不覆盖真实时序；与录制互补。
- **D6 `B2PROXY_HOT=1` 的 getter 录制**：短会话（菜单→一关 ~20 s）单独成 `oracle_getters` 套件。
  - 判据：14 个被过滤 getter 各自 `calls>0`；该日志 `sweep` PASS；A/A 0 分歧。
- **D7 `oracle.py audit` 覆盖审计入口**：一条命令输出 52 关 ×（录制/对象日志/物理 PASS/地板/原因），计数与 `work/phys_sweep_headless.json` 对齐（45/5/2）。
  - 判据：表 52 行，状态 ∈ {ok, v01, small, shared, missing}。
- **D8 `level_capture --resume` 补齐 25→52**：逐关 attach + 两次真点击，29–50 s/关（mtime 实测）。
  - 判据：一次跑完 52 行 `status.csv`；已采 25 行不重跑；MISS 带归因标签。
- **D9 FAIL 行自动落盘定位**：`work/fail_<rec>.txt`（首个分歧 callsite/导出/两侧值/该导出直方图）。
  - 判据：任取 FAIL 行，只读该文件即可回答「哪个导出、第几次、两侧值」。

## E. baseline 变体的 pt_sans 文本（T6.4e 的 baseline 分支）

- **baseline `AMagneticAdventure.exe` 的 `pt_sans*.dat` 文本**
  - 暂缓理由：L2-A 目标 `bin/gametop/game.exe` 不引用 `pt_sans`（F432）；GameTop 的关卡名/完成面板文本是烘焙图，动态文本只剩用户名（gulim1，F231/F433）。
  - 回流条件：baseline 变体纳入交付，或需要 3DM 汉化版的文本渲染时；先补 baseline 的 GL 文本 oracle（字形 quad 的 UV/advance），再解 `pt_sans.dat`。
