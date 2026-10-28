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

- [ ] T2.1 `b2Physics` 导出表 → ABI 契约（函数签名、结构体布局、调用约定） 依据：F07
- [ ] T2.2 C++ 实现（Box2D 2.x + C 包装），导出逐项一致 依据：F07
- [ ] T2.3 差分：原 `game.exe` 加载新 DLL，逐帧物理状态比对 依据：F07
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

## M5 汉化目标

- [ ] T5.1 汉化版资源作为交付资产（不改原 pak） 依据：F08
- [ ] T5.2 中文文本/字形核对 依据：F08、F11
- [ ] T5.3 交付包形态（`cfg.ini`、`images/`、`Uninstall/`） 依据：F09

## 变更记录

- 2026-10-28 依据 F05/F17/F20：Pak v0.2 记录布局闭环（24 B 定长 + trailer），T0.1/T1.1/T1.2 完成；`tools/pak.py` 已可 verify/extract 两版。

- 2026-10-28 初版：对齐=行为等价+函数映射；基准=GameTop；范围=宿主 + 两个自有 DLL。
