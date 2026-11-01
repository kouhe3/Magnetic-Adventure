# 覆盖清单 — 复刻到什么程度（decomp 口径）

> 这张表回答三个问题：**哪些函数算「已匹配」**（判据是什么）、**进展到哪**（T7 路径）、**哪些明确不做**（不参与等价）。
> 只增不减的结论在 `docs/facts.md`；任务树在 `tasks/magnetic-adventure-plan.md`；本文件是两者之上的**对外可读汇总**。
> 更新纪律：数字由命令生成，不手写；改了判据先改这一节再改表。

## 0. 「匹配」的定义（三层，互不替代）

| 层 | 判据 | 命令 | 通过条件 |
|---|---|---|---|
| 库函数（LCL / GLScene） | 指令序列归一后的相似度 | `python tools/code_match.py funcs <game.exe> <ours.exe>` | `sim >= 0.95`（自证 A/A = 100%） |
| 应用函数（我们重写的） | 同一输入、同一进程内 pre/post 摘要逐位相同 | `python work/ht/run.py`（T7.2a 形态） | `finite_diff=0 r_aa=0 s_aa=0` |
| 行为（整机） | GL 调用序列 / 存档 / 物理 FFI / 音频 | `python tools/verify.py`、`tools/phys_sweep.py`、`tools/gl_seq_ab.py` | 见各工具 docstring |

三条判据**不互相替代**：库层过不能推出应用层过；应用层过不能推出行为过。表里的「已匹配」只说明它所在那一层。

## 1. 总量与现状

| 层 | 总量 | 判据 | 已匹配 | 依据 |
|---|---|---|---|---|
| LCL 0.9.28.3（自编） | 抽样 4 个单元 | funcs sim | `win32int`/`stdctrls` **100%**、`controls`/`forms` **99.9%** | F210 |
| GLScene v1.1 + `patches/glscene-v11-game.patch` | 骨架链接的 **12 单元 / 1,054 函数** | funcs sim | **1,054 / 1,054**（`sim<0.95` 的 0 个） | F213 |
| 应用层（宿主自有代码） | **1,012 函数 / 60,868 指令 / 196,597 B** | T7.5（未建） | **1 个见证函数**：`sub_5ADF60`（竖切，F291）；**0 个进入交付代码** | F236、F291 |
| 应用层导入桩 | 18 个单 `jmp` | — | 计入上面的 1,030 行清单，不算「重写」 | F236 |
| Lua 绑定 | 144 个 | 逐调用 `call+args` | **144 / 144**（52 关 `mismatches=0`） | F239–F243 |
| b2Physics | 87 导出 | FFI 录制重放 | **87 / 87**，52 关 `bounded` PASS | F99、F130 |
| Squall | 99 导出 + 17 个宿主导入 | 调用序/返回值 | **99 / 99**、**17 / 17** 0 分歧 | F144 |

**覆盖边界（必须一起读）**：
- 库层的 1,054 只覆盖**骨架实际链接的 12 个单元**；没链接的单元不在统计里。
- 应用层的 1,012 是 `0x521000` 之上扣掉库层认领后的残差（F236）；它不含 144 个绑定（已单独统计）。
- 「1 个见证函数」= 竖切证明**方法可行**，不是覆盖率；T7.5 之前应用层覆盖率按 **0%** 计。

### 1.1 构建确定性（F292，影响判据形态）

- **代码段可复现**：同一源 + FPC 2.2.4 + 同 flags，完整宿主两次构建的 `.text`/`.data` **逐位相同**。
- **资源段不可复现**：`.rsrc` 的版本信息带构建时间（两次构建差 6 字节，2026-11-01 06:56:04 vs 06:56:10）。
- **原版不是纯编译器产物**：`game.exe` 的 PE 时间戳非 0（2011-09-21 14:17:28）；汉化版多 `.TEDATA`（加壳）。
- ⇒ 整文件 md5 不能当验收判据；**段级**（`.text` 逐函数 sim）+ **函数级**（T7.5 pre/post）才是判据。构建门禁要么排除 `.rsrc`，要么把构建时间钉死（未做）。
- 已知结构差：我们的 `magnet.exe` 带 `.stab/.stabstr`，原版没有 ⇒ 段级对拍前先抹平。

## 2. T7 路径的进展

| 任务 | 状态 | 判据/产物 |
|---|---|---|
| T7.0 跨模块 RTL | ✅ | 默认 RTL 交叉 10 万次首 5000 次内崩/挂；装宿主 MM 后 PASS（F244–F248） |
| T7.1 清单减法 | ✅ | `mapping/app-functions.csv` 1,030 行；`tools/app_inventory.py`（F236–F238） |
| **T7.2a 竖切** | ✅ | `python work/ht/run.py --runs 2000` ⇒ `finite_diff=0 r_aa=0 s_aa=0`，跨进程 A/A 相同，负例通过；NaN 层 `nan_diff=0`（F291） |
| T7.2 `hosttrace`（真实调用点记录） | ⏳ | 未做；竖切只调函数，没hook 调用点 |
| T7.3 双跑 A/B | ⏳ | 依赖 T7.2 |
| T7.4 纯函数输入空间扫描 | ⏳ | 竖切已给出形态（进程内、随机+边界、2000 条 ≈1.7 s），未推广到多函数 |
| T7.5 批量替换 + `mapping/functions.csv` | ⏳ | 文件尚不存在；这是 L1 验收项（requirements §2） |
| T7.6 混合产物整机回归 | ⏳ | 并入 T6.5 |

**T7.2a 给出的两条形态结论**（对后续路径有约束力）：
1. **不要用 MSVC 写注入侧**：FPC 的 `register` 约定（eax/edx/ecx）直接由编译器给出，源码级重写与目标**逐指令同构**（同 4 组 `fcompp` + 同极性 `jae/jbe`），不必写内联汇编。
2. **控制字是控制面**：宿主 raw CW = `0x137F`；FPC DLL 单独加载会留下 `0x1372`。把 MSVC 规范化的 `_controlfp` 值（`0x001F` 形态）直接 `fldcw` 会解除精度异常屏蔽 ⇒ 首个不精确运算抛 EInvalidOp（表现为游戏弹「无效浮点数操作」）。

## 3. 明确不做（不参与等价，也不进交付物）

| 项 | 为什么不做 | 依据 |
|---|---|---|
| GameTop 广告弹出（退出时 `ShellExecuteA` 打开网页） | 外部副作用，是 GameTop 包装行为，不是游戏本身；复刻它没有验收判据 | F02（导入表差异）、F173 |
| DRM / 安装器（GameShield、`setup.exe`） | 需求 §4 明确排除 | `docs/requirements.md` |
| 写原安装目录 / 回写原 pak | `bin/` 是只读 oracle；pak 只读解析 | requirements、F05 |
| `lua51.dll` 源码化 | 两版 md5 不同（F12），保留原 DLL；脚本本身是明文（F04） | requirements |
| PCM 逐位（T2.5 剩余 / T4.9） | L2-A 只要求「音频 PCM 差分」，F150 已给 corr 0.9998–0.9999；三条逐位路线均否 | `tasks/backlog.md` A |
| 残余 1 ULP（T4.8） | `no_crash` + `bounded` 均过，属噪声地板 | `tasks/backlog.md` A |
| M3 的 C++ 宿主实现 | 对照物；F213 拍板转 M6 | `tasks/backlog.md` C |
| IDA 全量导出 / oracle 全量采集（T0.3/T0.4） | 已被按需 IDA + 各代理覆盖 | `tasks/backlog.md` B |

## 4. 探针专用（我们的代码，默认关闭，不计入等价）

| 探针 | 作用 | 开关 |
|---|---|---|
| 无头模式 | 不建窗/不建 GL，只跑 pak+Lua+物理 | `HOST_HEADLESS=1`（F290） |
| 物理自检/诊断输入 | 建体、步进、瞬移驱动接触 | `HOST_PHYS`、`HOST_PHYS_STEPS`、`HOST_PHYS_MOVE`（F276–F281） |
| Lua 自检/事件注入 | 52 关绑定回归、`OnAddContact` 派发 | `HOST_LUA_SELFTEST`、`HOST_LUA_LEVEL`、`HOST_LUA_FIRE`、`HOST_LUA_LOG`（F242、F273） |
| 渲染/纹理判据 | 自读帧、上传 CRC、绘制 dump | `HOST_DUMP_FRAME`、`HOST_TEX_SELFTEST`、`HOST_TEX_CRC`、`HOST_DRAW_DUMP`（F185、F230） |
| `src/objlog` | 进程内记录 65 个工厂调用点 | 注入（F270） |
| `b2Physics` / `opengl32` / `Squall` 代理 | 调用序列抓包 | 文件替换 + `B2PROXY_LOG`/`GLPROXY_LOG`/`SQUALL_LOG`（F138、F176） |
| `work/ht`（T7.2a） | 进程内逐函数 A/B | `B2RTLPROBE_DLL` + `HT_*`（F291） |
| `tools/rtlprobe` | 跨模块堆/异常 | `B2RTLPROBE_DLL`（F244–F248） |

纪律：探针必须**默认零成本**（不设环境变量不建线程、不打开文件），且**不得出现在交付目录**的启动路径上。

## 5. 判定入口汇总（改判据先改这里）

```bash
python tools/verify.py                     # 6 门禁（exports×2 / window / squall×2 / physics 抽样）
python tools/verify.py --full              # 追加 52 关全量重放并重生成 docs/levels.md
python tools/phys_sweep.py                 # 52 关物理 init（无头，9.6 s）
python tools/code_match.py funcs bin/gametop/game.exe build/host_lcl/magnet.exe
python work/ht/run.py --runs 2000          # T7.2a 形态：进程内逐函数 A/B
```
