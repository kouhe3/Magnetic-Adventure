# 交接文档 — Magnetic Adventure 复刻

> 写给下一个接手的 agent，自包含：读这一份 + 三份文档就能开工。
> 写于 2026-10-30，`work` 分支，工作树干净（本文随附的那个提交）。

## 0. 一句话现状

两个 DLL 已复刻并验证完毕（**b2Physics 87/87 + 52 关全 PASS**；**Squall 99/99 + 17 个宿主导入 0 分歧**）；宿主 exe 过了窗口门禁，**主菜单已经画出**，纹理**直接读 pak**（37 张上传像素与原版逐字节相同，F187），与原版逐像素 mean|Δ| **1.375/255**、A/A 地板 0.00。
卡点很明确：渲染器仍**按抓包得到的绘制列表回放**，还没自己算菜单布局（T3.2d）；文本靠回放原版的字形 quad，**宿主自己不会排版/渲染字符串**（T3.5）；Squall 的 **PCM 逐位**仍阻塞。

台账 **187 条**（F01–F187，只增不减），计划 19/42 完成。

## 1. 先读这几份（按顺序）

1. `AGENTS.md` —— 构建/工具/纪律（x86、32 位 CPython、pwsh、bin 只读）。
2. `docs/requirements.md` —— 验收口径：**L2-A**（导出名/序号/调用约定 + 原版 exe 直接加载新 DLL），字节级复刻**明确不做**。
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
- 换行：仓库追踪文件统一 **CRLF**，`.gitattributes` 是 `* -text`（blob 字节 == 工作树字节，F130）。新文件写完转 CRLF。

## 3. 常用命令

```bash
# 构建（首次要带 -A Win32 -DB2_ARCH=IA32，之后增量即可）
cmake -S . -B build -G "Visual Studio 18 2026" -A Win32 -DB2_ARCH=IA32 -DB2_FP=default
cmake --build build --config Release                 # b2Physics + box2d
cmake --build build --config Release --target squall # Squall.dll（ogg/vorbis 直编）
cmake --build build --config Release --target host   # magnethost.exe（窗口 + 菜单渲染）
cmake --build build --config Release --target gl_proxy   # build/proxy_gl/Release/opengl32.dll

# 门禁（快集 6 项，~25 s；--full 追加 52 关全量重放并重生成 docs/levels.md）
python tools/verify.py
python tools/verify.py --full

# 导出契约
python tools/check_exports.py build/Release/b2Physics.dll                     # 87/87
python tools/check_exports.py build/Release/Squall.dll mapping/squall-exports.csv   # 99/99
python tools/check_exports.py build/proxy_gl/Release/opengl32.dll mapping/opengl32-exports.csv  # 368/368

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
# 绘制列表（宿主仍吃这份，T3.2d 才会替掉）；纹理已经改成宿主直读 pak
python tools/gl_drawlist.py work/glprobe/glffi4.bin --frame 20 --pack build/Release/menu_draw.bin

# 纹理 id↔素材映射（改 pak/启动顺序时重跑；产物已入库，一般不用动）
python tools/gl_texpack.py work/glprobe/glffi8.bin --pak work/pak_gametop \
  --out work/menu_tex.bin --manifest work/menu_tex.json --csv mapping/textures.csv
python tools/gen_texture_table.py          # mapping/textures.csv → src/host/texture_table.h

# 宿主直读 pak：HOST_DATA 指向 pak 文件或含 data 的目录；跑完对拍上传像素
HOST_DATA=bin/gametop/data HOST_TEX_CRC=work/host_tex_crc.txt \
  python tools/shot_window.py build/Release/magnethost.exe work/host_menu.png --wait 2
python tools/host_tex_ab.py work/glprobe/glffi8.bin work/host_tex_crc.txt   # 期望 diffs=0 / 37
python tools/shotdiff.py work/orig_menu.png work/host_menu.png --regions    # mean/p99/>16/分区域

# 宿主/原版截图（同一个工具；--wait 控制等窗口出现后再等多久）
python tools/shot_window.py build/Release/magnethost.exe work/host_menu.png --wait 2
python tools/shot_window.py work/glprobe/game.exe work/orig_menu.png --wait 19
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

## 4. 当前状态（按里程碑）

| 阶段 | 状态 |
|---|---|
| M0/M1 资源与规格 | pak 格式闭环、Lua 导出、资产索引 ✅；T0.3（IDA 全量导出）/T0.4（oracle 采集）仍是历史遗留项，按需再补 |
| M2 两个 DLL | b2：87/87、52 关全量 PASS、A/A 地板内；Squall：99/99、17 个宿主导入调用序 0 分歧（含优雅退出）、环回音频逐秒 corr 0.9998；**剩 PCM 逐位（F134，三条路线均否，F147）** 与长时回归（T2.6b） |
| M3 宿主 | 窗口层门禁 15/15 ✅（F166 子系统 5.01）；GL 上下文 + **主菜单渲染** ✅（F184）、**纹理直读 pak** ✅（T3.2c：WIC 解码，上传像素 37/37 逐字节相同，F185/F187）；剩：菜单布局参数化（T3.2d）、pak+Lua（T3.3）、场景接线（T3.4）、文本排版（T3.5）、配置（T3.6） |
| M4 验收 | 音频 diff ✅（F150）、e2e 自动化 ✅（F172/F174）、GL 绘制列表 ✅（F181/F182）；剩输入回放（T4.1）、帧 diff（T4.2）、存档 diff（T4.4）、映射覆盖（T4.5）、exe A/B 四层（T4.10）、1 ULP（T4.8） |
| M5 汉化 | 未开始（资源替换路线已定，F08） |

**本轮之前的硬数字**（写报告时直接引用）：
- b2：`calls=118558` / `steps=2018` / `bodies_bad=0`（F130 验收录制）。
- Squall：35 个 OGG 元数据 `diffs=0`（F142）；17 导入 20 步契约 `diffs=0`（F144）；环回逐秒 corr 0.9998–0.9999（F150）。
- 渲染：`glOrtho(±26.862, ±19.5)` ⇒ **18.95 px/unit**（F179）；菜单 **21 draw**、关卡 **26–27 draw**（F181/F182）；主菜单/关卡恒 **61–65 swap/s ≈ 15.6 ms/帧**（F177）。
- 宿主菜单 vs 原版：mean|Δ| **1.375/255**、p99 30、>16 像素 **2.105%**、A/A 地板 **0.00**（纹理直读 pak 后；口径见 `tools/shotdiff.py`，F187）。
- 纹理：37 张上传像素与原版 `glTexImage2D` 整块 CRC **37/37 逐字节相同**（F185/F187）；WIC 解码即可，不 vendor 任何图像库。

## 5. 本轮（GL 侦察 + 渲染里程碑 A + T3.2c）做了什么

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

## 6. 排队（建议顺序）

1. **T3.2d 菜单布局参数化**：把 21 个 draw 的 NDC bbox/UV 反推成「按客户区比例 + 纹理」的宿主侧布局（菜单在宿主代码里，F161），替掉 `menu_draw.bin`。顺带把悬停/点击（`mbtn_1/2`、`play_1/2` 这类二态纹理 + 用户名文本）接上——**文本排版本身是 T3.5**，T3.2d 只需把已抓到的字形 quad 参数化。
2. **T3.3 pak 加载 + Lua 状态机 + 144 个绑定**（F180 已把数据面摊开：`lvl_info.lvl` 文本清单、116 个 `Add*` 工厂、事件 `Attach_ScriptToObject`）。
3. **T3.4 场景接线**。铁律：**初始化顺序是契约**——loading→intro→menu→关卡，纹理在启动期上传（F179），不能冷启动造场景（F169/F171/F177）。
4. **T3.5 文本排版**（字模表 + 步进；见 §7）。菜单以外还有关卡 HUD/提示框。
5. **T4.1 输入回放**（现在是脚本化操作，还不是"录一次任意次重放"）。
6. **T4.10 宿主 exe A/B** 的四层判据里，②（DLL 调用层）要等 T3.4 之后才可用。
7. 收尾：T2.6b 长时回归、T4.4 存档 diff、T4.5 映射覆盖。
8. 已知阻塞：T4.9 PCM 逐位（F147 三条路线否，需要进程内 hook 或 WASAPI 环回）、T4.8 `Good Shot!` 残余 1 ULP。

## 7. 开放问题 / 风险

- **菜单布局在宿主代码里**（F161），Lua/pak 里没有；T3.2d 得从绘制列表反推（21 个 quad 的比例/UV/纹理已经全部拿到）。
- **渲染残差 2% 像素 >16 未归因**：不是几何偏移（9 个平移里 (0,0) 最优），mipmap 开/关几乎无差；怀疑是纹理过滤/取整与 DWM 1.5× 缩放的交互，暂按"过滤级残差"记录。
- **动态文本宿主自己不会画**：主菜单的 `Welcome, <玩家名>` 是"烘焙纹理（`m_label1.png` = `Welcome,`）+ 字形 quad（`gulim1.png` 字模，UV 指向单格）"。现在能对上是因为**原样回放了抓到的字形 quad**；换用户名/换文案就不行，需要 T3.5 的字模排版（字模格里只有字形，没有字宽表 ⇒ 得从 UV 间距反推步进）。
- **关卡渲染**只有单帧画像（26–27 draw/帧、逐 sprite `glMultMatrixf`），变换链/场景图还没系统化；要做关卡渲染得先把"矩阵栈 → 世界坐标"的参数化做完（`gl_drawlist.py` 已能给世界坐标，但还没归纳成宿主侧的场景模型）。
- **PCM 逐位**与 **1 ULP** 是两条长期尾巴，别让它们阻塞主线。
- 外部参考：`C:/tmp/bpsim`（群友的 Unity DOTS 复刻，2022.2.23f1c1 + Entities 1.0.0-pre.44）里有现成的**内容管线**（274 关 / 526 contraption XML / prefabs.json）和 **QA harness**（`Bpsim/QA` + `DshBridge invoke_static`），思路可借鉴，但与本仓库无代码依赖。

## 8. 踩过的坑（复用清单）

- **KnownDLL 决定能不能文件代理**：`dsound` 拦不住（F147，`ole32` 在 KnownDLLs），`opengl32` 能拦（F175）。动手前先查 `HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\KnownDLLs`。
- **代理日志必须逐条 WriteFile**（F139）：录制用 TerminateProcess 结束，用户态缓冲会整段丢。GL 代理额外做了 200 ms 周期 flush。
- **代理里的 payload 要防越界**：`IsBadReadPtr` + 长度上限；`glTexImage2D` 的像素按 `w*h*bpp` 算整块 CRC32 才够精确（192 B 前缀对均匀边界的图会多图同分）。
- **GL 的变换链是 P·M·v**：顶点永远乘 MODELVIEW，和当前 `glMatrixMode` 无关（F181）。GLScene 的 HUD 会在帧中途把投影换成单位阵、用像素空间画东西，乘错就飞出屏幕。
- **固定管线状态要继承启动态**：`GL_BLEND` 在启动期就常开、帧内不再 `glEnable`，只按帧内调用推状态会漏掉它 → 白屏（F184）。
- **`GL_GENERATE_MIPMAP(0x8191)` 在部分驱动兼容 profile 下不生效** → 纹理不完整、采样成白；用 `gluBuild2DMipmaps`（F184）。
- **prim 枚举不能凭印象写**：GL 的 `0x0004..0x0009` 是 TRIANGLES/STRIP/FAN/QUADS/QUAD_STRIP/POLYGON，错一位就把 `GL_QUADS` 当 fan。4 顶点的 draw 看不出差别，**文本串是 12 顶点**，一错就成蝴蝶结（`Welcome, ooo`→`o>>`，F186）。回放时**按记录里的 prim 原样画**，别统一画 fan。
- **抓屏工具必须先摆窗口再拍**：`ImageGrab` 抓的是屏幕像素，窗口被终端/任务栏盖住时会把别人的像素拍进来，看起来像"渲染回归"（踩过：底部 108 px 是前台终端，误判 2.6 vs 1.37）。`shot_window.py` 现在先 `SetWindowPos(0,0)` + `SetForegroundWindow`。
- **UI 自动化只能走真实输入**：`PostMessage` 合成鼠标消息不触发按钮（F162）；点击坐标按**抓图的物理像素**算（F172，踩过 1.5×）；`Play` 落点由存档 `LastCompleteLevel` 决定（F171）；游戏内正常退出会 `ShellExecuteA` 弹网页 → 默认杀进程（F173）。
- **FPC/LCL 不适合逐函数 patch**：内部 `register` 约定（EAX/EDX/ECX，Self 在 EAX）+ LCL 对象布局，替换不复合；值得做的只有输入输出自包含的纯函数（in-process trampoline A/B）。
- **双后端/双实现互相比不算验证**：判据必须对"原版"，容差写进语料。

## 9. 关键文件索引

| 区域 | 文件 |
|---|---|
| 物理 DLL | `src/b2physics/b2physics.cpp`（87 导出）、`b2physics.def`、`vendor/box2d-2.0.2`（带 `altered (F###)` 注释） |
| 音频 DLL | `vendor/squall`（上游 1.48，3 处 `altered (F136/F138/F148)`）、`vendor/libogg-1.3.5`、`vendor/libvorbis-1.3.7` |
| 宿主 | `src/host/main.cpp`（窗口/消息）、`src/host/gl_render.cpp`（WGL + 菜单渲染）、`src/host/pak.{h,cpp}`（pak 只读）、`src/host/wic_decode.{h,cpp}`（WIC 解码）、`src/host/texture_table.h`（生成物） |
| 代理 | `src/proxydll/`（b2，`B2FFI02`）、`src/squallproxy/`（`SQFFI01`）、`src/glproxy/`（`GLFFI02`）；桩由 `tools/gen_proxy.py` 生成 |
| 仪器 | `tools/instr.py`、`gate.py`、`sweep.py`、`report_sweep.py`、`replay_ffi.py`、`ffi.py`、`verify.py`、`shotdiff.py`（截图像素 A/B）、`host_tex_ab.py`（上传纹理 CRC 对拍）、`gen_texture_table.py` |
| UI/自动化 | `tools/uistate.py`、`uitemplate.py`、`e2e_tutorial.py`、`e2e_record.py`、`driver.py`、`winprobe.py`、`wincompare.py`、`shot_window.py`（窗口客户区截图） |
| GL | `tools/gl_ffi.py`、`gl_drawlist.py`、`gl_texpack.py`；抓包目录 `work/glprobe/` |
| 数据 | `mapping/*.csv`（导出表、绑定、关卡映射、纹理 id↔素材 `textures.csv`）、`docs/levels.md`（只能由 `report_sweep.py --write` 生成） |
| 文档 | `docs/requirements.md`、`docs/facts.md`、`docs/b2physics-abi.md`、`tasks/magnetic-adventure-plan.md`、`tasks/magnetic-adventure-todo.md`、本文 |

## 10. 接手第一小时

1. `python tools/verify.py` → 期望 `gates=6 fail=0`（~25 s）。挂了先修门禁，别看别的。
2. `cmake --build build --config Release --target host` + `HOST_DATA=bin/gametop/data python tools/shot_window.py build/Release/magnethost.exe work/host_menu.png --wait 2` → 应看到主菜单（若红底：`gl_init.log` 里 `ok=0`，查 `bin/gametop/data` 路径与 `build/Release/menu_draw.bin`；若白屏，查 `GL_GENERATE_MIPMAP` 那条坑）。
3. 读 `docs/facts.md` 的 F175–F187（GL 结论 + WIC 解码 + prim 勘误），再读计划 §变更记录 最近三条。
4. 按 §6 第 1 条（T3.2d 菜单布局参数化）开工；改计划记得追加变更记录并写 `依据：F##`。
