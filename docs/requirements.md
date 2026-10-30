# 需求规格 — Magnetic Adventure C/C++ 复刻

状态：2026-10-28 定稿。决策：对齐=行为等价+函数映射；基准=GameTop 版；范围=宿主 + b2Physics/Squall 源码化。
依据：`docs/facts.md`（F01–F13）。

## 1. 目标

产出 32 位 Windows 的 C/C++ 源码工程（宿主 exe + b2Physics.dll + Squall.dll），行为与基准二进制一致，且每个自写函数可追溯到原二进制地址。

## 2. 对齐合同（验收口径）

| 级别 | 适用对象 | 判定方式 |
|---|---|---|
| **L0 行为等价** | 宿主 exe | 场景矩阵回放：GL 调用序列 diff、帧缓冲像素 diff、音频 PCM diff、存档字节 diff |
| **L1 函数映射** | 自写单元 | `mapping/functions.csv`：原 RVA / 大小 / C++ 符号 / 伪代码 hash / 状态；自写单元覆盖率 100%（RTL/GLScene/Box2D/Lua 白名单排除） |
| **L2-A DLL ABI** | b2Physics、Squall | 导出名+序号+调用约定逐项相等；原 `game.exe` 直接加载新 DLL 可运行；物理状态/音频 PCM 差分 |
| **L2-B 整 exe 字节级** | 宿主 exe | **改为目标（2026-10-30 拍板；原"明确不做"的唯一理由"跨语言不可达（F01）"已被 F153/F202 证伪）**：原版是 FPC 2.2.4 + LCL 0.9.28.3 + GLScene（F202），**库层已 100% 复原**——GLScene v1.1 + `patches/glscene-v11-game.patch`，12 个单元 1,054 个函数残差 0（F213）；LCL 单元逐指令 99.9–100%（F210）。⇒ 宿主改走 **FPC/LCL + GLScene 重建**，判据从"像素 diff"转为**逐调用（GL 序列）+ 逐指令（库层）+ 像素验收**。剩余未知只有应用层（≤390 KB，本就没有源） |

## 3. 基准与目标

- **oracle（对齐基准）**：`bin/gametop/`（`game.exe` + 原三 DLL + `data`），更接近原厂构建（F02）。
- **交付目标**：汉化版（`bin/baseline/`）的资源与可执行形态（F08 待证：汉化落点）。
- **第三参照**：Masque `setup.exe`（F10），仅在需要交叉验证时解包，不作为基准。
- `b2Physics.dll`、`Squall.dll` 两版字节相同（F12）；`lua51.dll` 两版不同（F12）——保留原 DLL，不源码化。

## 4. 范围

包含：
1. 宿主 exe：Win32 窗口/消息/输入、OpenGL 上下文与 GLScene 等价渲染层、pak 读取、Lua 状态机与绑定 API、场景/实体/物理/音频接线、配置与存档。
2. `b2Physics.dll`：Box2D 2.x + C 包装，源码化，导出表级对齐。
3. `Squall.dll`：DirectSound8 音频后端，源码化，导出表级对齐。
4. `tools/pak`：只读解析 + 解包（不改原文件）。
5. `tests/`：确定性回放与差分 harness；`mapping/functions.csv`。

保留二进制：`lua51.dll`、pak 内 Lua 脚本（F04）。

不包含：Delphi RTL/GLScene 内部实现、DRM/GameShield 安装器、原安装目录写入。

## 5. 技术约束

- x86（Win32）；CMake + MSVC v143；C++17。
- 渲染走 OpenGL 固定管线，调用序列与基线一致（F03）。
- 音频走 DirectSound8，语义对齐 Squall（F06）。
- 所有原始二进制只读；产物写 `build/`。

## 6. 验收矩阵

| 场景 | L0 判据 | 覆盖 |
|---|---|---|
| 启动 → 主菜单 | GL 调用序列一致；像素 diff ≤ 阈值；窗口类名/尺寸/像素格式一致 | 渲染、Win32 |
| 主菜单 → 第 1 关 | 同左 + 输入响应时序（固定 tick） | 输入、Lua 绑定 |
| 前 3 关 → 失败/重开 | 同左 + 存档字节一致 | 物理、存档 |
| 通关/退出 | 同左 + 退出码与资源释放顺序 | 关闭路径 |
| 双 DLL 替换 | 原 `game.exe` + 新 DLL 跑通全矩阵 | L2-A |

## 7. 风险与待证

| 项 | 现状 | 处理 |
|---|---|---|
| Pak v0.2 记录字段 | 已闭环：24 B 定长记录 + trailer（F05/F17） | 已关闭 |
| 汉化落点 | 已确证：图片烘焙（`help_1.png` 帮助 vs Help）；111 个 Lua 两版字节相同（F08） | 已关闭 |
| 文本渲染 | pak 内无字体文件（F11） | 跟踪 exe 的 GDI/纹理字体路径 |
| 原版可运行性 | 未验证 | 先跑 GameTop 版确认 oracle 可用 |
