# 事实台账 — Magnetic Adventure 反编译

只增不减。状态：`待证` / `已证` / `已证伪` / `过期`。
证据等级：L1 反编译产物（只给探测方向）；L2 类型/符号/自有解析器 dump（授权该数据范围内的实施）；L3 日志/断点/断言（授权技术验收）；L4 实机观察或第二实现一致（授权验收与回归基准）。

基准包解包位置（不入库）：`bin/baseline/`（来自 `~/Downloads/Compressed/cilidamaoxian.zip`）。

## 工作副本（`bin/`，已 gitignore）

| 目录 | 来源 | 关键文件 md5 |
|---|---|---|
| `bin/gametop/` | `C:\Program Files (x86)\GameTop.com\Magnetic Adventure\` 安装目录 | `game.exe` `059fd8f39cfd2f763e5ba1a32d22fa73`；`data` `c516a2cd162b9616e25b36651ade3563` |
| `bin/baseline/` | `~/Downloads/Compressed/cilidamaoxian.zip` 解包（汉化版） | `AMagneticAdventure.exe` `7efb069e06bfa523078dacab8cb5f93b`；`data` `bda4b63eee90f767dfbe9ad3f86aba7a` |
| `bin/masque/` | `C:\Users\K\Downloads\Programs\AMagneticAdventure_dl_setup-1.exe` | `45c619b417812436d032ccbba31d3e29` |

所有探针与 IDA 分析一律引用 `bin/` 内副本，不再依赖仓库外路径。

| id | claim | 等级 | 出处 | 状态 | 影响 |
|---|---|---|---|---|---|
| F01 | 基线主程序 `AMagneticAdventure.exe` 是 Delphi/VCL 原生 PE32：2,668,814 B、md5 `7efb069e06bfa523078dacab8cb5f93b`、machine 0x014c、ImageBase 0x400000、时间戳 2010-10-28 15:00:27Z、5 节（`.text/.data/.bss/.rsrc/.TEDATA`，导入表落在 `.TEDATA`）；10 处 `TForm`、`TApplication`/`TImage`/`TBitmap` RTTI 字符串 | L2 | `python probe/peinfo.py "bin/baseline/AMagneticAdventure.exe"` | 已证 | 对齐定义、基准选择 |
| F02 | GameTop 版主程序 `game.exe` 是同一程序的另一次构建：2,583,968 B、md5 `059fd8f39cfd2f763e5ba1a32d22fa73`、时间戳 2011-09-21 14:17:28Z、导入在 `.idata`、比基线多 `ShellExecuteA`、`DragQueryFileA`（基线为 `DragQueryFileW`） | L2 | `python probe/peinfo.py "bin/gametop/game.exe"` | 已证 | 基准选择 |
| F03 | 渲染层是 GLScene（Delphi OpenGL 库）+ OpenGL 固定管线：RTTI 字符串 `TGLDirectOpenGL`/`TGLTextureImage`/`TAffineVectorList`、字符串 `[Cadencer, Viewer, GlScene, Dummy`、导入 opengl32 53 项 + glu32 33 项 | L2 | `probe/peinfo.py` 的 GLScene 标记 + 字符串扫描 | 已证 | 渲染复刻范围 |
| F04 | 游戏逻辑是 pak 内**明文 Lua 5.1 源码**，不需要反编译：基线 641 KB 文本、986 处 `function`、749 处 `\nfunction Name(`、308 个不同函数名；两版脚本正文几乎相同（641,431 B vs 641,074 B） | L2 | `python probe/pakscan.py <pak>` | 已证 | 范围：逻辑=提取而非反编译 |
| F05 | `data` 是 Pak v0.2，已完全解析：`u32 toc_size`（=24×(count+1)）+ `[Pak Header Info Ver 0.2]`（25 B）+ count×24 B 记录 + 1×24 B trailer 记录；记录尾部 8 字节为 `u32 off` + `u32 size`，前缀为 `u8 namelen` + 名字 + 填充；载荷起点 = 29+toc_size，偏移相对载荷起点；count = toc_size/24−1（基线 722 / GameTop 707） | L2 | `python tools/pak.py verify bin/baseline/data`（累计偏移 + 文件尾 + PNG/OGG/Lua 完整性全通过） | 已证 | M1 工具 |
| F06 | 音频走 `Squall.dll`（导出 `SQUALL_*`：Channel/Sample/ChannelGroup，导入 DSOUND `ord#2`=DirectSoundCreate8 与 waveOut）；OGG 资源 2451 个页，两版前 4 KB 页 hash 有 2430 个相同 | L2 | `probe/peinfo.py`、`python probe/assetdiff.py <a.data> <b.data>` | 已证 | DLL 复刻/替代 |
| F07 | 物理走 `b2Physics.dll`，导出 `b2_*` C API（`b2_Body_CreateShape_Box/Circle/Polygon` 等），主程序导入其中 62 项；该 DLL 时间戳 2010-04-05、linker 9.39（MSVC） | L2 | `probe/peinfo.py bin/baseline/b2Physics.dll` | 已证 | DLL 复刻 |
| F08 | 汉化 = **图片烘焙**：基线 `help_1.png` 显示"帮助"，GameTop 同名图显示"Help"（目视）；两版 111 个 `.lua` **字节完全相同**；差异集中在 158 个 PNG + 1 JPG + 1 DAT + 1 LVL，基线另有 19 张 PNG、GameTop 另有 Gulim 字体 4 件 | L4 | `python tools/pak.py extract` 后逐文件 md5 对比 + 目视 `work/pak_baseline/help_1.png` / `work/pak_gametop/help_1.png` | 已证 | 汉化=资源替换，不涉代码 |
| F09 | 基线 exe 的 Authenticode 目录（RVA 0x3E0000、size 0x1558）超出文件尾（0x28BA8E），签名不可校验 → 该 exe 在签名后被改动过 | L2 | `probe/peinfo.py` 输出的 security 目录 + 文件长度 | 已证 | 基线可信度 |
| F10 | `AMagneticAdventure_dl_setup-1.exe` 不是 MSI：PE32 `setup.exe`、52,839,512 B、资源段 52.7 MB、CompanyName `Powered by Masque Publishing`、ProductVersion 1.0.0.3、创建于 2012-04-19、`GameShield` | L2 | `7z l "bin/masque/AMagneticAdventure_dl_setup-1.exe"` | 已证 | 第三参照版本 |
| F11 | pak 内没有字体文件：`.ttf`/`.fnt` 文件名字符串 0 处、OTTO/TTC 签名 0 处 → 文本只能来自系统字体渲染或预烘焙位图 | L2 | `probe/pakscan.py` + 字节签名扫描 | 待证 | 文本渲染路径复刻 |
| F12 | 两版发行的 `b2Physics.dll`（md5 `5b1d145b774fb60165dbd185691532e9`）与 `Squall.dll`（md5 `73a950e4a10e714d6d4f0ff3886b6a93`）**字节相同**；`lua51.dll` **不同**（基线 `80a7660c4abf30212f37139ec93e1dfb` vs GameTop `9dd71b50331760748669b5c83ab670eb`） | L2 | `md5sum` 两目录同名 DLL | 已证 | 保留原 DLL 时须绑定对应版本 |
| F13 | Pak 前 32 条在 `[u8 namelen][name][stamp 0xF399B000][u32 off][u32 size]` 下自洽且偏移连续；第 33 条（`baloon_1.png`）起边界差 1 字节，静态推断不足 | L2 | `probe/pakscan.py` 变体 + `data` 0x342 处 hexdump | 待证 | T0.1 改动态断点 |
| F14 | `b2Physics.dll` 导出 **87 个 `b2_*` 函数（序号 1–87，全 `__cdecl`）** + `DllEntryPoint`；内部静态链接 **Box2D 2.0.x**（`b2PolygonDef`/`b2CircleDef` 带 vftable，`b2_GetMaxPolygonVertices()` 硬编码 8）与静态 CRT（只导入 KERNEL32） | L2 | IDA：`survey_binary` + `b2_Body_CreateShape_Box`/`b2_Body_CreateShape_Circle`/`b2_GetMaxPolygonVertices` 反编译；清单 `mapping/b2physics-exports.csv` | 已证 | T2.1/T2.2 |
| F15 | 包装层收的是**扁平 C 结构**而非 C++ 对象：形状描述 +4=density、+8=friction、+12=restitution、+16=isSensor；Box 用 +20/+24=center、+28/+32=halfExtent；Circle 用 +20/+24=localPos、+28=radius；Polygon 用 +20=顶点数、+28=顶点数组（步长 8） | L2 | IDA 反编译 `b2_Body_CreateShape_{Box,Circle,Polygon}` | 已证 | Lua 绑定结构体兼容 |
| F16 | `b2World` 分配 0x19288 字节；`b2_World_CreateBody` 栈上构造 0x3C 字节 body def；`b2Filter` 6 字节写在 `shape+34`；变换输入为 `{b2Vec2 position; float angle}`（`b2_Shape_TestPoint` 展开 cos/sin） | L2 | IDA 反编译 @0x100013B0、0x10001400、0x10001620、0x10001660 | 已证 | ABI 契约 |
| F17 | pak 末尾有 **trailer 文件**（由最后一条 24 B 记录的 `u8 len`+名字描述）：基线 `yes_2.png` 10800 B（PNG），GameTop `lvl_info.lvl` 13416 B（UTF-16LE `<Level>` 文本）；trailer 的偏移字段基线 = `sum(sizes)+0x8000`、GameTop = `sum(sizes)` | L2 | `python tools/pak.py verify ...` 输出 `field=0x2c7261f` / `0x2bc0808`；`bin/baseline/data` 末 10800 B 以 `\x89PNG` 开头 | 已证 | M1 提取完整性 |
| F18 | 111 个 `.lua` 在两版中**逐字节相同**；脚本注释是 **CP1251 俄文**（如 `-- первые слова`、`-- хинт "отлично! пойдем дальше?"`）→ 此前"Lua 内含 GBK 中文"是编码误判 | L2 | `work/pak_baseline/lvl_e0.lua` 按 cp1251 解码 | 已证 | 逻辑层一致 |
| F19 | Gulim 字体资源（`gulim1.png`/`gulim2.png`/`gulim1.dat`/`gulim2.dat`）只存在于 GameTop 版；基线版无此 4 件，另有 19 张 PNG 为其独有（`hint_41/44/49/54-58/70/78-86`、`logo_1.png`、`mm_pgm1.png`、`mm_pgm2.png`） | L2 | 两版解包目录逐名 diff（`onlyA`/`onlyB`） | 已证 | 交付资源选择 |
| F20 | `tools/pak.py verify` 对两版均通过：基线 722 条（550 PNG / 35 OGG / 111 Lua）+ trailer，GameTop 707 条（534/35/111）+ trailer；PNG 首尾签名、OGG 首签名、Lua 无 NUL 全部校验通过 | L2 | `python tools/pak.py verify bin/baseline/data; python tools/pak.py verify bin/gametop/data` | 已证 | M1 完成 |
| F21 | 宿主在 `sub_595E00` 里通过 `sub_595CA0(L, "名字", 函数)` 注册 **144 个 Lua 全局函数**（名字是 ASCII C 字符串：`Do_Command`、`Add_WoodBox`、`Set_PhysParams`…），每个绑定对应 137–1400 B 的 Delphi 函数；其中 122 个能在提取出的 Lua 脚本里找到调用 | L2 | IDA：`sub_595E00` 反编译 + `mapping/lua-bindings.csv`；Lua 侧 `work/pak_baseline/*.lua` 交叉比对 | 已证 | M3 Lua 绑定面 |
| F22 | 两版资源索引共 727 个条目：`same` 543、`diff` 161、`only_a` 19、`only_b` 4；每个 PNG 记录尺寸与像素 hash，每个 OGG 记录页数与流数 | L2 | `python tools/assetindex.py bin/baseline/data bin/gametop/data mapping/assets.csv` | 已证 | T4 帧/PCM 比对基准 |
| F23 | pak 装载链：`sub_52E750`（游戏初始化）→ `sub_563980`（建 pak 对象，含两个内存流）→ `sub_563D00`（打开 `"data"`：读 4 B 头长、25 B magic，把 TOC 复制进内存流）→ 打日志 `"[Pak] - done"`；与 F05 的格式一致 | L2 | IDA 反编译 + 0x52E8B2 处调用点 | 已证 | M3 pak 读取复刻 |
| F24 | 原 `b2Physics.dll` 的包装层**直接读写 Box2D 内部字段**（不是纯 API 封装）：body+8/+12 = `m_xf.position`、+60 = `m_sweep.a`、+68/+72 = `m_linearVelocity`、+76 = `m_angularVelocity`、+152 = `m_userData`；world+103004 = `m_gravity`；`SetVelocity/SetOmega` 还会清 `m_flags & ~8` 并把 +148 置 0（唤醒语义） | L2 | `work/b2physics-decomp/{001,003,015,016,019,031,032,033,034,086}_*.c` | 已证 | 必须用同代 Box2D 布局复刻 |
| F25 | 曾用 `vendor/box2d-2.0.1`（Google Code 存档）在 VS18 x86 下编译通过；`tools/check_exports.py` 对原 DLL 校验 87 个名字与序号完全一致（导出校验结论仍有效）。**该 vendor 已删除**，被 2.0.2 取代（F26/F27） | L3 | `python tools/check_exports.py bin/baseline/b2Physics.dll` | 过期 | 导出校验工具仍有效 |
| F26 | 游戏用的就是 **Box2D 2.0.2**：pybox2d 2.0.2b1 源码包内捆绑的快照含 `b2Version b2_version = {2, 0, 2};`，其编译布局与原 DLL **逐项一致**（`sizeof(b2World)`=0x19288、`position`=+8、`sweep.a`=+60、`linearVelocity`=+68、`angularVelocity`=+76、`shapeList`=+104、`sleepTime`=+148、`userData`=+152、`m_gravity`=+103004） | L3 | `work/b2_py202/Box2D-2.0.2b1/Box2D/Common/b2Settings.cpp:22`；`tools/layout_probe.cpp` 编译运行结果，对照 `work/b2physics-decomp/*` | 已证 | T2.2 基线 |
| F27 | Box2D **2.0.1 已排除**：同一探针在 2.0.1 上得 `sizeof(b2World)`=0x19278、`position`=+4、`sweep.a`=+56、`lv`=+64、`av`=+72、`shapeList`=+100、`userData`=+144、`m_gravity`=+102984，与原 DLL 差 16/4 字节 | L3 | `tools/layout_probe.cpp` 编译运行结果（2.0.1 版） | 已证 | 版本判定 |
| F28 | `vendor/box2d-2.0.2` 取自 pybox2d 2.0.2b1 捆绑快照，唯一改动：`b2_maxPolygonVertices` 16→8（原 DLL 的 `b2_GetMaxPolygonVertices()` 返回 8，`CreateShape_Polygon` 顶点数组 64 B = 8 个）；改动处已加注释标记 | L2/L3 | `vendor/box2d-2.0.2/Box2D/Common/b2Settings.h`；`work/b2physics-decomp/007_b2_Body_CreateShape_Polygon.c` | 已证 | T2.2 构建 |
| F29 | 原 DLL 的 ABI 已用「加载真 DLL + 调用」探针实测：`b2_CreateWorld(void* ctx, const b2Vec2* gravity)`（gravity 在 arg1，写入 world+103004；arg0 必须是非空可写指针）、`b2_World_Step(world, dt, vi, pi)`、`b2_Body_GetPosition(out, body)`、`b2_Body_GetAngle(body)->float`、`b2_GetMaxPolygonVertices()->8`。`b2_World_CreateBody(def*)` 的 def 是**对象在前的记录结构**：`+0` world、`+4` **angularDamping**（实测 slot=1 → GetAngularDamping=1.0）、`+8` linearDamping（假设）、`+12` allowSleep（宿主置 1）、`+13` fixedRotation（待证）、`+14` **isBullet**（实测置 1 → IsBullet=1）；def 里没有 position，位置由 `SetXForm` 后续设置 | L3 | `tools/probe_b2physics.c`（pair/slot/torque 模式）对 `bin/baseline/b2Physics.dll` 实测；宿主构造点 `game.exe` 0x58eaf0、0x59cfb0 | 已证 | T2.2 def 结构 |

## 影响对齐方案的硬约束

- 原程序是 **Delphi/VCL 编译产物**。C++ 编译器（MSVC/Clang）无法产出与原 PE 同字节流，因此"C++ 编译输出与原 exe 字节级一致"不可达；字节级一致只在**同语言同版本重编译**或**DLL 导出表/ABI** 两个尺度上有意义。
- 原程序 **32 位**。要与原 `Squall.dll`/`b2Physics.dll`/`lua51.dll` 保持 ABI 兼容，新 exe 必须 x86。
- 逻辑层已是源码。重写的实际范围是 **Delphi 宿主 + Lua 绑定 + GLScene 渲染路径 + pak 读取 + Win32/GL/DirectSound 调用**。
