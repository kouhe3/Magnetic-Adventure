# entryprobe — 入口级覆盖探针（F299 的 363 个未覆盖函数）

census（`work/census`）只 patch 直接 `call rel32` 点，因此对 **Lua VM 闭包、虚表、函数指针**调用的函数一律报 0。
本探针改 patch **函数入口**：`jmp stub` → `lock inc [count]` → 重放被覆盖的序言字节 → `jmp target+L`。
ESP/寄存器不动（不加 `pushfd`；序言不读入参 flags）。

## 命令

```bash
# 目标表（默认 tools/entryprobe/targets.csv = F299 uncovered 快照）
python tools/entryprobe/gen_targets.py            # 生成 targets.inc / targets.json（361 个可挂桩）

# 构建（Win32，静态 CRT）
cmake -S tools/entryprobe -B tools/entryprobe/build -G "Visual Studio 18 2026" -A Win32
cmake --build tools/entryprobe/build --config Release

# 跑：准备 work/entryprobe/game（data 硬链接 bin/gametop/data），装 b2 代理 + 原 DLL + 探针
python tools/entryprobe/run.py --seconds 120      # 启动，人工点，超时 kill 并出报告
python tools/entryprobe/run.py --keep             # 一直开着，之后 --report
python tools/entryprobe/run.py --report work/entryprobe/counts.bin
```

判据：`entry.log` 出现 `ENTRY installed=361 failed=0 targets=361`；`counts.bin` = 361×4 字节；
`--report` 给出 `nonzero=N/361` 与逐函数计数。

## 启动期挂载（F405）

默认挂载点在 b2 代理的 `SetTimer(1500 ms)`，因此 **exe 入口到计时器触发之间的调用一律记 0**。
要测启动期，设 `B2RTLPROBE_EARLY=1`：代理在 `DllMain` 里直接 `LoadLibrary` + `rp_host_entry()`，
探针在 `start` 之前完成打桩（`counts` 里 `005afcc0 start` 会变成 1）。

```bash
B2RTLPROBE_EARLY=1 python tools/entryprobe/run.py --seconds 25
```

实测（1,010 目标版）：晚挂载四局并集 736/1,010；早挂载新增 **39** 个启动期函数
（27 个 `0x52E750`/TDebugInfo 块 + 12 个回调/表项），即 **775/1,010**，未覆盖降到 235。
⇒ 晚挂载报 0 不等于没执行；`0x52E750` 及其 `0x564760` 已用 x32dbg 断点确认在启动期执行。

## 自制关卡覆盖 Lua 绑定（F406）

`tests/levels/cover_bindings_*.lua` 用同名替换 `lvl_o14/e14` 的方式调用未覆盖绑定；
主关覆盖 70 个，`cover_bindings_terminal_*.lua` 分别覆盖入口后会抛异常/重启的
`Set_VisibleRollMap`、`Add_LevelSound`、`Level_Restart`。

```bash
python tools/entryprobe/cover_build.py                 # 主关
python tools/entryprobe/cover_build.py --o tests/levels/cover_bindings_terminal_roll.lua
# 每次启动前设 B2RTLPROBE_EARLY=1 / ENTRY_OUT / ENTRY_LOG，然后：
"C:/Users/K/.local/bin/python3.12.exe" tools/direct_drive.py --dir work/cover_game --levels 1 --timeout 5
python tools/entryprobe/check_bindings.py --counts work/cover_game/counts_main.bin \
    work/cover_game/counts_term_roll.bin work/cover_game/counts_term_sound.bin \
    work/cover_game/counts_term_restart.bin
```

结果：`hit=73 miss=0 expected=73 helpers=73/73`；负例只给 `counts_term_roll.bin` 时
`hit=1 miss=72`。边界：只证明入口命中，不证明参数/行为等价。

## 覆盖边界

- 只覆盖 `targets.csv` 里的 361 个可挂桩目标（F299 的 363 个快照扣掉 2 个 1 字节 nullsub）；不是全 exe。
- 不覆盖：函数体中间的间接入口（只扫描了直接 call/jmp 到 `(target,target+L)` 的情况）、
  通过计算跳转进入序言的代码、2 个 1 字节 nullsub（`0x5afc70`/`0x5afcd6`，长度 < 5 跳过）。
- 计数是“进入函数的次数”，不是调用点次数；同一函数的所有调用来源合并。
- 探针在主线程 `SetTimer(1500ms)` 安装（b2 代理的 `B2RTLPROBE_DLL`，F246）；安装前已执行的调用不计数。
- 依赖 **无 ASLR** 的 `game.exe`（F234，ImageBase `0x400000`，md5 `059fd8f39cfd2f763e5ba1a32d22fa73`）。
  换版本/加壳/VAs 变化后必须重跑 `bin/gametop/game.exe.i64` 的清单并更新 `targets.csv`。
- `tools/entryprobe/targets.json` 是 F299 的 **361** 目标快照；1,010 目标版在
  `work/entryprobe_lvl1/targets.json`（同名 `targets.inc`，需用该目录的 build）。

## 失效条件

- `game.exe` 换版（md5 变）→ 所有 VA 失效，禁止使用旧 `targets.inc`。
- 目标函数序言含相对跳转 / 首指令跨 24 字节 / 有内部直接入口 → 生成器已跳过并写进 `targets.json.skipped`。
- 游戏启用 ASLR 或加载基址非 `0x400000` → `base+(va-0x400000)` 会写错地址。
- 探针安装后崩溃 = patch 破坏了对齐/序言；先用 `ENTRY_LOG` 对照 installed 数，再二分 targets。
