# Repository Guidelines

复刻 *Magnetic Adventure*（Delphi 宿主 `game.exe` + `b2Physics.dll` + `Squall.dll`）：用 C++17 重写物理 DLL，使**导出 ABI 与浮点行为**与原版逐位一致；之后再轮到音频 DLL 与宿主 exe。所有结论必须落到 `docs/facts.md`（编号 F##），所有任务必须引用 F## 才能开工。

## Project Overview

- 目标不是"跑通"，是**行为等价**：同一份真实调用序列重放到两个 DLL，逐调用、逐 step 比对。
- 验收口径（`docs/requirements.md`）：L2-A = 导出名/序号/调用约定 + 原版 `game.exe` 直接加载新 DLL 跑通；整 exe 字节级复刻明确**不做**。
- 文档三件套：`docs/requirements.md`（口径）、`docs/facts.md`（事实台账，只增不减）、`tasks/magnetic-adventure-plan.md`（任务树 + 变更记录）。
- 交接：`tasks/HANDOFF.MD`（自包含的接手说明：现状/命令/排队/坑），每轮收尾更新。

## Architecture & Data Flow

两个同名 DLL，输出目录不同，职责相反：

| 层 | 源码 | 产物 | 职责 |
|---|---|---|---|
| 兼容层（真实现） | `src/b2physics/` | `build/Release/b2Physics.dll` | 87 个 `cdecl` 导出，直接转调 `vendor/box2d-2.0.2` 或直读写其内部字段 |
| 抓包代理（只记录） | `src/proxydll/` | `build/proxy/Release/b2Physics.dll` | 占住 `b2Physics.dll` 名字，加载改名的 `b2Physics_orig.dll`，naked 桩记录 pre/post 后尾跳真身 |

**兼容层的三种手写 shim**（其余都是薄转调）：
1. 宿主 def 布局重解释：`PolyDefC`（+20 顶点数、+24 起每点 8B）、`BoxDef`（+28/+32 半宽高）、`CircleDef`（+28 radius）——`src/b2physics/b2physics.cpp:452-496`。
2. 裸函数指针回调：宿主传的是 `void (*)(...)`，不能当 `b2ContactListener*`，用 `HostListenerC`/`HostFilterC` 适配成 9 个 dword 的扁平事件（`b2physics.cpp:324-378`）。
3. FFI 实测出的签名差异：`b2_World_DestroyJoint` 是两参、`b2_World_DestroyBody` 忽略 world 走 `body->m_world`、`b2_Body_SetXForm` 必须走 `b2Body::SetXForm`（`b2physics.cpp:392-403,635-641`）。

**数据流（唯一验收链）**：

```
game.exe + 代理 DLL ──B2PROXY_LOG──> work/rec_<ts>/ffi.bin (B2FFI02)
        │                                   │
        └── 宿主真实调用序列 ────────────────┤
                                            ▼
                        tools/ffi.py（唯一解析器）
                                            ▼
        tools/replay_ffi.py（32 位 CPython + ctypes）重放到目标 DLL
                                            ▼
       逐 call / 逐 step 比对 → tools/instr.py:bounded
                                            ▼
                work/sweep.jsonl → tools/report_sweep.py --write → docs/levels.md
```

代理日志格式以 `src/proxydll/proxy_core.c` 顶部与 `tools/ffi.py` 的 struct **双份真相**定义：改一侧必须同步另一侧并升级 magic（`B2FFI02` → 03），否则 v01/v02 兼容读取全乱。

## Key Directories

| 路径 | 用途 | 进 git |
|---|---|---|
| `src/b2physics/` | 兼容 DLL 实现（`b2physics.cpp` 933 行 + `.h` + `.def`） | ✓ |
| `src/proxydll/` | 代理 DLL；`proxy_stubs.c` / `proxy.def` 是**生成物** | ✓ |
| `src/squallproxy/` | Squall 代理 DLL（`SQFFI01` 日志）；`proxy_stubs.c` / `proxy.def` 由 `tools/gen_proxy.py --csv mapping/squall-exports.csv --library Squall --prefix SQUALL_` 生成 | ✓ |
| `vendor/box2d-2.0.2/` | **已按原版修正过的快照，不要当上游** | ✓ |
| `vendor/squall/` | 上游 Squall v1.48（MIT，HEAD `20988426`）源码：原 `Squall.dll` 与它导出名 99/99 一致；与 2006 二进制**行为不等价**，改动处标 `// altered (Fxxx)` | ✓ |
| `vendor/libogg-1.3.5/` `vendor/libvorbis-1.3.7/` | Ogg Vorbis 解码源码，直编进 `Squall.dll`（不生成独立 DLL） | ✓ |
| `tools/` | 可复用仪器与工具（`instr/gate/sweep/replay_ffi/ffi/gen_proxy/...`） | ✓ |
| `probe/` | 早期静态分析脚本（PE/Pak/资源差分），只读分析用 | ✓ |
| `mapping/*.csv` | 单一事实源：导出表、参数形态、Lua 绑定、录制↔关卡、资源差分 | ✓ |
| `docs/` | `requirements.md` / `facts.md` / `levels.md` / `b2physics-abi.md` | ✓ |
| `tasks/` | plan（任务树 + 变更记录）与 todo | ✓ |
| `build/` | CMake 产物 + `build_info.json` | ✗ |
| `work/` | 录制、一次性探针、`sweep.jsonl`（**权威结果**） | ✗ |
| `bin/` `baseline/` `gametop/` `msi/` | 只读 oracle / 原始二进制（`bin/gametop` 含 `game.exe`、原版 DLL、IDA i64）。**永不写入** | ✗ |

新克隆必须自行恢复 `bin/`（`bin/gametop`、`bin/baseline`、`bin/masque`），否则门禁与 IDA 全部不可用。

## Development Commands

```bash
# 构建（必须 Win32；/arch:IA32 只对 x86 有效）
cmake -S . -B build -G "Visual Studio 18 2026" -A Win32 -DB2_ARCH=IA32 -DB2_FP=default
cmake --build build --config Release            # → build/Release/b2Physics.dll + .map
cmake --build build --config Release --target b2physics_proxy   # → build/proxy/Release/b2Physics.dll

# 改过 mapping/b2physics-exports.csv 之后必须重新生成代理桩
python tools/gen_proxy.py

# 导出契约自检（期望 exports=87，missing/extra/ordinal_mismatch 全 0）
python tools/check_exports.py build/Release/b2Physics.dll

# Squall 音频 DLL（上游源码；ogg/vorbis 源码直编，无外部解码 DLL）
cmake --build build --config Release --target squall            # → build/Release/Squall.dll
python tools/check_exports.py build/Release/Squall.dll mapping/squall-exports.csv   # 99/99

# Squall 转发 DLL（占住 Squall.dll，加载 Squall_orig.dll，写 SQFFI01 日志）
cmake --build build --config Release --target squall_proxy      # → build/proxy_squall/Release/Squall.dll
#   装法：游戏目录里 Squall.dll = 代理、Squall_orig.dll = 真身；SQUALL_LOG=<path> 指定日志
python tools/squall_ffi.py <log> [--show N]      # 解析（pre/post 1:1 自检）
python tools/squall_ab.py <a.bin> <b.bin>        # 两份日志结构对拍（指针不参与比对）

# 诊断变体：SQUALL_DEBUG=1 时 api_Startup 在进程 CWD 写 Squall.log（每个导出记参数与结果）
cmake -S . -B build -DSQUALL_DEBUG_LOG=ON && cmake --build build --config Release --target squall_dbg

# 指纹（确认 build_info.json 与产物一致）
python -c "import sys;sys.path.insert(0,'tools');import instr;print(instr.fingerprint('build/Release/b2Physics.dll')['match'])"

# 单关（目录内有 ffi.bin 时自动跳过抓包；退出码 0 = PASS）
python tools/gate.py work/rec_20261029_134434 --name three_coins

# 裸重放（排查用，最后一行 JSON 是判据输入）
"C:/Users/K/.local/bin/python3.12.exe" tools/replay_ffi.py work/rec_20261029_134434/ffi.bin --json --dll build/Release/b2Physics.dll

# 全量回归 + 出表
python tools/sweep.py --jobs 8
python tools/report_sweep.py --write
```

## Code Conventions & Common Patterns

**导出与 ABI**
- 命名：`b2_<Family>_<Action>`（`b2_Body_GetXForm`、`b2_World_Joint_Revolute`），源文件按 `// ---- World / Body / Shapes / Joints` 分节。
- 全部 `extern "C" __declspec(dllexport)`（宏 `B2API`），全部 `cdecl`；序号以 `src/b2physics/b2physics.def` 为准。
- 出参约定：函数把结果写进 `out` 并**返回同一个 `out` 指针**；bool 用 `int` 0/1；类型不符的 getter 返回 `0`/`-1`。
- **不抛异常、不 assert、不做空指针检查**（与原版一致）；排查靠 `B2PHYSICS_LOG` + VEH。
- 新增导出必须同时改三处：`b2physics.cpp` 实现、`b2physics.def` 一行、`python tools/gen_proxy.py` 重新生成；且保持 `B2API <ret> b2_xxx(...) {` 的写法——`tools/replay_ffi.py` 用这个形态做正则提取原型。

**诊断开关（默认零成本）**
- `B2PHYSICS_LOG=<path>`：每个导出入口 `TRACE("b2_Xxx")` 打一行；`TraceDetail()` 打可疑参数。
- `B2DBG_STEP` / `B2DBG_FILE` / `B2DBG_CONTACTS` / `B2DBG_FROM..TO`：步窗内 dump body 与接触表。
- 重放侧：`B2_TRACE=<body hex>`、`B2_STEP_VI/PI`、`B2DUMP_CONTACTS=path,lo,hi`、`DIGEST_ALL`、`DUMP_FIRST`、`PROGRESS_EVERY`。
- 代理侧：`B2PROXY_LOG`、`B2PROXY_HOT=1`（记录只读 getter）。

**改 vendor 的规矩**
- `vendor/box2d-2.0.2` 是"已修正快照"：`b2_maxPolygonVertices` 16→8（F28）、`b2_angularSleepTolerance * b2_pi`（F97）、GJK 早退补 `B2_FLT_EPSILON²`（F122）、速度钳位改"每步最大平移/旋转"（F124）。
- 任何 vendor 改动**必须**写成 `// altered (Fxxx): 理由 + 实测依据`（许可证要求），并先在独立副本里验证：`-DB2_ROOT=work/vendor_probe -B work/build_probe`，别动主干。

**脚本分层**
- 一次性探针放 `work/`（已 gitignore）；**可重跑的仪器进 `tools/`**，docstring 写清用法、输入、判据或期望输出（例：`tools/av_clamp.py` 钳位映射、`tools/dumpdiff.py` 双 DLL 内部状态转储比对）。

## Important Files

| 文件 | 为什么重要 |
|---|---|
| `CMakeLists.txt` | 三个 target、`/arch:IA32`、静态 CRT、`B2_ROOT`、POST_BUILD 指纹 |
| `cmake/build_info.cmake` | 写 `build/build_info.json`（dll/box2d md5、arch/fp/msvc/flags） |
| `src/b2physics/b2physics.cpp` | 全部 87 个导出的实现与 shim |
| `src/b2physics/b2physics.def` | 导出名 + 序号契约 |
| `src/proxydll/proxy_core.c` | 日志二进制格式、热点 getter 过滤、pre/post 配对 |
| `src/proxydll/proxy_stubs.c` | 87 个 naked 桩（**生成物，勿手改**） |
| `tools/instr.py` | 指纹、`log_usable`、`bounded`/`deciles` 判据（纯函数） |
| `tools/replay_ffi.py` | 重放器：指针映射、scratch 缓冲区、逐 call/逐 step 比对 |
| `tools/gate.py` / `tools/sweep.py` | 单关 / 全量门禁 |
| `tools/ffi.py` | 日志唯一解析器（`stats/show/rets/sites`） |
| `docs/facts.md` | 事实台账（L1–L4 分级，出处必须可重放） |
| `docs/levels.md` | 52 关结果表，**只能由 `report_sweep.py --write` 生成** |
| `mapping/b2physics-exports.csv` | 导出表单一事实源（88 行，序号 1–87） |
| `mapping/levels.csv` | 录制 ↔ 关卡映射 |

## Runtime/Tooling Preferences

- **必须 x86（Win32）**：`/arch:IA32`（x87）才能逐位贴合原版；SSE2 会立刻产生 1e-4 级差异。静态 CRT（`/MT`）是 ABI 要求：原版只依赖 `KERNEL32`。
- 工具链实测：VS18 Insiders，`msvc=19.52` / `toolset=145`（`docs/requirements.md` 里写的 v143 已过时）。
- **加载 DLL 的脚本必须用 32 位 CPython**（否则 `WinError 193`）：优先 `PY32` 环境变量，默认 `C:/Users/K/.local/bin/python3.12.exe`。涉及脚本：`replay_ffi.py`、`gate.py`、`sweep.py`、`dist_probe.py`、`toi_call.py`、`toi_scan.py`、`av_clamp.py`。
- 纯解析类脚本（`ffi.py`、`pak.py`、`assetindex.py`、`profile.py`、`tmatch.py`）任意 Python 3。
- 本机是 Windows：统一用 `pwsh` + `python`；不要用 `bash`（裸 `bash` 可能解析到 WSL）、不要用 `du`（PATH 上是 Sysinternals DU）。
- 视觉/窗口自动化先 `SetProcessDpiAwarenessContext(-4)`；按标题含 `Magnetic` 且宽度 > 100 找窗口。
- git：不提交到 `main`；提交前 `git status` + `git diff --stat`；不自行 push；不改写 author/committer 身份。

## Testing & QA

**没有传统单测、没有 CI**。唯一验收 = FFI 录制 → 离线重放门禁。

| 判据 | 含义 | 阈值 |
|---|---|---|
| `no_crash` | 重放跑完且 `calls > 0` | — |
| `bounded` | 末两个十分位的中位数 ≤ 前段（70–90%）中位数 × 1.25 + 2 | 硬判据 |
| `bodies_bad` | 逐 `(step, body)` 超差计数 | **只报告，无阈值** |
| `first_exact` | 第一个**逐位**不等的 step | 严格口径，PASS 也可非空 |
| `deciles` | 每步最坏 `|Δ|/容差` 的十分位中位数 | 看幅度而非个数 |

容差（`tools/replay_ffi.py:315`，带 `max(1,|a|,|b|)` 相对化）：`sleepTime 1e-3`、`vx/vy/w 1e-4`、`px/py/angle 1e-5`、`mass/invMass/I/invI 1e-4`。flags 按位分组：`sleep/island` 视为管线噪声，`bullet/frozen/fixedRot/allowSleep` 记为语义差异（只 warn，不判 FAIL）。

- 四态：`PASS`（`no_crash` + `bounded`）/ `FAIL` / `UNUSABLE`（日志 magic < `B2FFI02`，工具层直接拒收）/ `SKIP`（日志 < 1 MiB，停在菜单）。
- **A/A 地板必须按录制量**：把同一份日志重放到**原版 DLL**（`--dll bin/gametop/b2Physics.dll`）。不同录制的天花板差很多（实测 `Slipgate` 0、`Looking for Keys` 5,297）。"bad 非零"本身不是缺陷证据，要与该录制的地板比。
- `mismatches` 计数有 25 条的地板（指针返回值不可比），`≤ 25` 不构成证据。
- 权威结果只认 `work/sweep.jsonl`；`work/gate_*.json` 是单次快照，可能过时。
- `tools/gate_all.py` 已与面板录制脱节（要求 `meta.json` 里的旧字段），**不要用**；批量一律 `sweep.py` + `report_sweep.py`。
- 录制：`python tools/recorder_gui.py`（装代理、起游戏、人工玩、STOP 杀进程），产物 `work/rec_<ts>/{ffi.bin,meta.json,shots/}`。
