# Magnetic Adventure 复刻

目标不是"能跑"，是**行为等价**：同一份真实调用序列重放到原版与新实现，逐调用、逐 step 比对。
验收口径见 `docs/requirements.md`（当前主口径 **L2-A**：导出名/序号/调用约定 + 原版 `game.exe` 直接加载新 DLL）。

原版构成：Lazarus/LCL 宿主 `game.exe`（FPC 2.2.4 + LCL 0.9.28.3 + GLScene）+ `b2Physics.dll`（Box2D 2.0.2）+ `Squall.dll`（Ogg Vorbis）+ Lua 5.1.5 关卡脚本。

## 现状

| 层 | 状态 |
|---|---|
| `b2Physics.dll` | 87/87 导出；53 份真实录制全量重放，**52/52 关 PASS**（F130） |
| `Squall.dll` | 99/99 导出；17 个宿主导入 0 分歧；环回逐秒 corr 0.9998–0.9999。**PCM 逐位未解**（F147/F195） |
| 宿主窗口 | 15 个字段 `diffs=0`（类名/样式/客户区/子窗口/外框，F166） |
| 宿主渲染（C++ 仿写路线） | GL 上下文 + 主菜单宿主现算：与原版逐像素 mean\|Δ\| **1.088/255**，A/A 地板 0.00；纹理直读 pak，上传像素 **37/37** 逐字节相同（F187/F190）。⚠️ 这是 `src/host` 的残差；若改走 FPC/LCL + GLScene 重建（F213 后可行），渲染由同一份库产出，应改用逐调用/逐指令判据，像素只作验收 |
| Lua | vendor Lua 5.1.5；pak 里 111 个脚本 111/111 编译；`lvl_info.lvl` 解析出 52 关（F191） |
| 宿主（FPC/LCL 路线，M6） | **2026-10-30 拍板转此路线**；窗口层已复刻：`src/host_lcl/magnet.pas` 让 `wincompare` **15 字段 diffs=0**（F214）。渲染/场景/Lua 待接 |
| 库层复原（L2-B） | GLScene = **v1.1 + `patches/glscene-v11-game.patch`**；12 个单元 **1,054 个函数残差 0**（F211–F213） |
| 关卡渲染 / Lua 绑定 | 未做（T3.3/T3.4） |

## 目录

| 路径 | 用途 |
|---|---|
| `src/b2physics/` | 兼容 DLL：87 个 `cdecl` 导出，转调 `vendor/box2d-2.0.2` |
| `src/squallproxy/` `src/proxydll/` `src/glproxy/` | 三个转发代理 DLL（b2 / Squall / opengl32），只记录调用 |
| `src/host/` | C++ 宿主（窗口、WGL、pak 直读、WIC 解码、菜单布局、字模表）——**路线切换后保留作对照物** |
| `src/host_lcl/` | FPC/LCL + GLScene 新宿主（M6）；`magnet.pas` 已过窗口门禁 |
| `vendor/` | box2d-2.0.2（已按原版修正）、squall、libogg、libvorbis、lua-5.1.5 |
| `patches/` | 原版对 GLScene v1.1 的本地补丁（`patch -p1` 到 v1.1 的 `Source/` 树） |
| `tools/` | 全部可重跑仪器（门禁、重放、GL 抓包、代码对应率、版本夹逼） |
| `mapping/` | 单一事实源：导出表、Lua 绑定、关卡映射、纹理 id↔素材 |
| `docs/` | `requirements.md`（口径）、`facts.md`（台账 F01–F212）、`levels.md`（52 关结果，只能由工具生成） |
| `tasks/` | `magnetic-adventure-plan.md`（任务树 + 变更记录）、`HANDOFF.MD`（接手必读） |
| `bin/` `baseline/` `gametop/` | 只读 oracle（原版 exe/DLL/IDA 库），**永不写入**，不入 git |

## 快速开始

```bash
# 构建（必须 Win32；/arch:IA32 才能逐位贴合原版 x87）
cmake -S . -B build -G "Visual Studio 18 2026" -A Win32 -DB2_ARCH=IA32 -DB2_FP=default
cmake --build build --config Release

# 门禁（6 项，~10 s）：导出契约 / 窗口 / Squall 契约与解码 / 物理抽样
python tools/verify.py
python tools/verify.py --full        # 追加 52 关全量重放并重生成 docs/levels.md

# 单关重放（退出码 0 = PASS）
python tools/gate.py work/rec_20261029_134434 --name three_coins

# 新宿主（FPC/LCL 路线）：需要打过补丁的 GLScene v1.1 树，见 patches/
python tools/glskel_build.py work/glscene_patch build/host_lcl src/host_lcl/magnet.pas
cp bin/gametop/libpng13.dll bin/gametop/zlib1.dll build/host_lcl/   # GLFilePNG 的运行时依赖
python tools/wincompare.py --orig work/winprobe_game --ours build/host_lcl --ours-exe magnet.exe

# 库层对应率（指令级，重定位无关）
python tools/code_match.py cover bin/gametop/game.exe <候选.exe> --tail 0x521000
python tools/code_match.py funcs bin/gametop/game.exe <候选.exe> --unit GLObjects.o
```

细节（重建 `work/`、GL 抓包、UI 自动化、L2-B 工具链）见 `tasks/HANDOFF.MD` §3。

## 判据口径（别混）

- **物理/DLL**：FFI 录制 → 离线重放；权威结果是 `work/sweep.jsonl`，判据 `no_crash` + `bounded`，`mismatches ≤ 25` 是地板。
- **库层源码对应**：`code_match.py funcs` 的 `sim`（指令序，操作数归一）；**不是** `units` 的字节覆盖率（判"是否同一份源码"会误判）。
- **渲染**：同状态对 + 16×16 窗口最大计数；A/A 地板必须先量（原版两次截图差 0.00）。

## 纪律

- x86/Win32 + 静态 CRT；加载 DLL 的脚本必须用 **32 位 CPython**（`PY32`）。
- `bin/`、`baseline/`、`gametop/`、`msi/` 只读，`work/` 放一次性产物（已 gitignore）。
- 不提交 `main`；提交前 `git status`；不改写 author/committer 身份。
- 文本文件统一 **CRLF**（`.gitattributes` 是 `* -text`）。
- 台账只增不减：结论必须带可重放的出处；证伪走划掉 + 勘误行（见 `docs/facts.md`）。
