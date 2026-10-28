# 事实台账 — Magnetic Adventure 反编译

只增不减。状态：`待证` / `已证` / `已证伪` / `过期`。
证据等级：L1 反编译产物（只给探测方向）；L2 类型/符号/自有解析器 dump（授权该数据范围内的实施）；L3 日志/断点/断言（授权技术验收）；L4 实机观察或第二实现一致（授权验收与回归基准）。

基准包解包位置（不入库）：`baseline/磁力大冒险/`（来自 `~/Downloads/Compressed/cilidamaoxian.zip`）。

| id | claim | 等级 | 出处 | 状态 | 影响 |
|---|---|---|---|---|---|
| F01 | 基线主程序 `AMagneticAdventure.exe` 是 Delphi/VCL 原生 PE32：2,668,814 B、md5 `7efb069e06bfa523078dacab8cb5f93b`、machine 0x014c、ImageBase 0x400000、时间戳 2010-10-28 15:00:27Z、5 节（`.text/.data/.bss/.rsrc/.TEDATA`，导入表落在 `.TEDATA`）；10 处 `TForm`、`TApplication`/`TImage`/`TBitmap` RTTI 字符串 | L2 | `python probe/peinfo.py "baseline/磁力大冒险/AMagneticAdventure.exe"` | 已证 | 对齐定义、基准选择 |
| F02 | GameTop 版主程序 `game.exe` 是同一程序的另一次构建：2,583,968 B、md5 `059fd8f39cfd2f763e5ba1a32d22fa73`、时间戳 2011-09-21 14:17:28Z、导入在 `.idata`、比基线多 `ShellExecuteA`、`DragQueryFileA`（基线为 `DragQueryFileW`） | L2 | `python probe/peinfo.py "C:/Program Files (x86)/GameTop.com/Magnetic Adventure/game.exe"` | 已证 | 基准选择 |
| F03 | 渲染层是 GLScene（Delphi OpenGL 库）+ OpenGL 固定管线：RTTI 字符串 `TGLDirectOpenGL`/`TGLTextureImage`/`TAffineVectorList`、字符串 `[Cadencer, Viewer, GlScene, Dummy`、导入 opengl32 53 项 + glu32 33 项 | L2 | `probe/peinfo.py` 的 GLScene 标记 + 字符串扫描 | 已证 | 渲染复刻范围 |
| F04 | 游戏逻辑是 pak 内**明文 Lua 5.1 源码**，不需要反编译：基线 641 KB 文本、986 处 `function`、749 处 `\nfunction Name(`、308 个不同函数名；两版脚本正文几乎相同（641,431 B vs 641,074 B） | L2 | `python probe/pakscan.py <pak>` | 已证 | 范围：逻辑=提取而非反编译 |
| F05 | `data` 是自定义 Pak v0.2：`u32 toc_size` + `[Pak Header Info Ver 0.2]` + 条目表（`u8 namelen`、名字、4 B 标记 `0xF399B000`、`u32 offset`、`u32 size`），载荷从 TOC 末尾起连续存放；条目数基线 722 / GameTop 707。第 33 条后记录边界差 1 字节，字段语义未闭环 | L2 | `probe/pakscan.py` + `data` 0x0–0x140、0x43C0–0x4480 hexdump | 待证 | 资源工具（M1） |
| F06 | 音频走 `Squall.dll`（导出 `SQUALL_*`：Channel/Sample/ChannelGroup，导入 DSOUND `ord#2`=DirectSoundCreate8 与 waveOut）；OGG 资源 2451 个页，两版前 4 KB 页 hash 有 2430 个相同 | L2 | `probe/peinfo.py`、`python probe/assetdiff.py <a.data> <b.data>` | 已证 | DLL 复刻/替代 |
| F07 | 物理走 `b2Physics.dll`，导出 `b2_*` C API（`b2_Body_CreateShape_Box/Circle/Polygon` 等），主程序导入其中 62 项；该 DLL 时间戳 2010-04-05、linker 9.39（MSVC） | L2 | `probe/peinfo.py baseline/磁力大冒险/b2Physics.dll` | 已证 | DLL 复刻 |
| F08 | 汉化落点不在 Lua：两版 pak 的 Lua 文本无 CJK 字符；PNG 签名 551 vs 534、内容 hash 交集 373；exe ASCII 字符串集 7312 相同、基线独有 332 / GameTop 独有 351 | L2 | `probe/pakscan.py`（utf8-cjk/gbk 统计）、`probe/assetdiff.py` | 待证 | 汉化范围（是否仅图片/字模） |
| F09 | 基线 exe 的 Authenticode 目录（RVA 0x3E0000、size 0x1558）超出文件尾（0x28BA8E），签名不可校验 → 该 exe 在签名后被改动过 | L2 | `probe/peinfo.py` 输出的 security 目录 + 文件长度 | 已证 | 基线可信度 |
| F10 | `AMagneticAdventure_dl_setup-1.exe` 不是 MSI：PE32 `setup.exe`、52,839,512 B、资源段 52.7 MB、CompanyName `Powered by Masque Publishing`、ProductVersion 1.0.0.3、创建于 2012-04-19、`GameShield` | L2 | `7z l "C:/Users/K/Downloads/Programs/AMagneticAdventure_dl_setup-1.exe"` | 已证 | 第三参照版本 |

## 影响对齐方案的硬约束

- 原程序是 **Delphi/VCL 编译产物**。C++ 编译器（MSVC/Clang）无法产出与原 PE 同字节流，因此"C++ 编译输出与原 exe 字节级一致"不可达；字节级一致只在**同语言同版本重编译**或**DLL 导出表/ABI** 两个尺度上有意义。
- 原程序 **32 位**。要与原 `Squall.dll`/`b2Physics.dll`/`lua51.dll` 保持 ABI 兼容，新 exe 必须 x86。
- 逻辑层已是源码。重写的实际范围是 **Delphi 宿主 + Lua 绑定 + GLScene 渲染路径 + pak 读取 + Win32/GL/DirectSound 调用**。
