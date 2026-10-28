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
| F05 | `data` 是自定义 Pak v0.2：`u32 toc_size` + `[Pak Header Info Ver 0.2]` + 条目表（`u8 namelen`、名字、4 B 标记 `0xF399B000`、`u32 offset`、`u32 size`），载荷从 TOC 末尾起连续存放；条目数基线 722 / GameTop 707。第 33 条后记录边界差 1 字节，字段语义未闭环 | L2 | `probe/pakscan.py` + `data` 0x0–0x140、0x43C0–0x4480 hexdump | 待证 | 资源工具（M1） |
| F06 | 音频走 `Squall.dll`（导出 `SQUALL_*`：Channel/Sample/ChannelGroup，导入 DSOUND `ord#2`=DirectSoundCreate8 与 waveOut）；OGG 资源 2451 个页，两版前 4 KB 页 hash 有 2430 个相同 | L2 | `probe/peinfo.py`、`python probe/assetdiff.py <a.data> <b.data>` | 已证 | DLL 复刻/替代 |
| F07 | 物理走 `b2Physics.dll`，导出 `b2_*` C API（`b2_Body_CreateShape_Box/Circle/Polygon` 等），主程序导入其中 62 项；该 DLL 时间戳 2010-04-05、linker 9.39（MSVC） | L2 | `probe/peinfo.py bin/baseline/b2Physics.dll` | 已证 | DLL 复刻 |
| F08 | 汉化落点**不在明文文本层**：22 个常用 UI 词（开始/退出/设置/…）在 pak 与 exe 中按 GBK、UTF-8、UTF-16LE 检索均为 0 命中；两版 pak 的 Lua 文本几乎相同（539,200 B vs 539,747 B）；两版图像按像素 hash 有 373 张完全相同、177/160 张互不相同。差异来自"本地化"还是"版本差异"未定 | L2 | `python probe/cjk_search.py <pak|exe>`、`probe/pakscan.py`、`probe/assetdiff.py` | 待证 | 汉化范围；需一次对照运行定位 |
| F09 | 基线 exe 的 Authenticode 目录（RVA 0x3E0000、size 0x1558）超出文件尾（0x28BA8E），签名不可校验 → 该 exe 在签名后被改动过 | L2 | `probe/peinfo.py` 输出的 security 目录 + 文件长度 | 已证 | 基线可信度 |
| F10 | `AMagneticAdventure_dl_setup-1.exe` 不是 MSI：PE32 `setup.exe`、52,839,512 B、资源段 52.7 MB、CompanyName `Powered by Masque Publishing`、ProductVersion 1.0.0.3、创建于 2012-04-19、`GameShield` | L2 | `7z l "bin/masque/AMagneticAdventure_dl_setup-1.exe"` | 已证 | 第三参照版本 |
| F11 | pak 内没有字体文件：`.ttf`/`.fnt` 文件名字符串 0 处、OTTO/TTC 签名 0 处 → 文本只能来自系统字体渲染或预烘焙位图 | L2 | `probe/pakscan.py` + 字节签名扫描 | 待证 | 文本渲染路径复刻 |
| F12 | 两版发行的 `b2Physics.dll`（md5 `5b1d145b774fb60165dbd185691532e9`）与 `Squall.dll`（md5 `73a950e4a10e714d6d4f0ff3886b6a93`）**字节相同**；`lua51.dll` **不同**（基线 `80a7660c4abf30212f37139ec93e1dfb` vs GameTop `9dd71b50331760748669b5c83ab670eb`） | L2 | `md5sum` 两目录同名 DLL | 已证 | 保留原 DLL 时须绑定对应版本 |
| F13 | Pak 前 32 条在 `[u8 namelen][name][stamp 0xF399B000][u32 off][u32 size]` 下自洽且偏移连续；第 33 条（`baloon_1.png`）起边界差 1 字节，静态推断不足 | L2 | `probe/pakscan.py` 变体 + `data` 0x342 处 hexdump | 待证 | T0.1 改动态断点 |
| F14 | `b2Physics.dll` 导出 **87 个 `b2_*` 函数（序号 1–87，全 `__cdecl`）** + `DllEntryPoint`；内部静态链接 **Box2D 2.0.x**（`b2PolygonDef`/`b2CircleDef` 带 vftable，`b2_GetMaxPolygonVertices()` 硬编码 8）与静态 CRT（只导入 KERNEL32） | L2 | IDA：`survey_binary` + `b2_Body_CreateShape_Box`/`b2_Body_CreateShape_Circle`/`b2_GetMaxPolygonVertices` 反编译；清单 `mapping/b2physics-exports.csv` | 已证 | T2.1/T2.2 |
| F15 | 包装层收的是**扁平 C 结构**而非 C++ 对象：形状描述 +4=density、+8=friction、+12=restitution、+16=isSensor；Box 用 +20/+24=center、+28/+32=halfExtent；Circle 用 +20/+24=localPos、+28=radius；Polygon 用 +20=顶点数、+28=顶点数组（步长 8） | L2 | IDA 反编译 `b2_Body_CreateShape_{Box,Circle,Polygon}` | 已证 | Lua 绑定结构体兼容 |
| F16 | `b2World` 分配 0x19288 字节；`b2_World_CreateBody` 栈上构造 0x3C 字节 body def；`b2Filter` 6 字节写在 `shape+34`；变换输入为 `{b2Vec2 position; float angle}`（`b2_Shape_TestPoint` 展开 cos/sin） | L2 | IDA 反编译 @0x100013B0、0x10001400、0x10001620、0x10001660 | 已证 | ABI 契约 |

## 影响对齐方案的硬约束

- 原程序是 **Delphi/VCL 编译产物**。C++ 编译器（MSVC/Clang）无法产出与原 PE 同字节流，因此"C++ 编译输出与原 exe 字节级一致"不可达；字节级一致只在**同语言同版本重编译**或**DLL 导出表/ABI** 两个尺度上有意义。
- 原程序 **32 位**。要与原 `Squall.dll`/`b2Physics.dll`/`lua51.dll` 保持 ABI 兼容，新 exe 必须 x86。
- 逻辑层已是源码。重写的实际范围是 **Delphi 宿主 + Lua 绑定 + GLScene 渲染路径 + pak 读取 + Win32/GL/DirectSound 调用**。
