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

## 覆盖边界

- 只覆盖 `targets.csv` 里的 363 个目标（F299 快照）；不是全 exe。
- 不覆盖：函数体中间的间接入口（只扫描了直接 call/jmp 到 `(target,target+L)` 的情况）、
  通过计算跳转进入序言的代码、2 个 1 字节 nullsub（`0x5afc70`/`0x5afcd6`，长度 < 5 跳过）。
- 计数是“进入函数的次数”，不是调用点次数；同一函数的所有调用来源合并。
- 探针在主线程 `SetTimer(1500ms)` 安装（b2 代理的 `B2RTLPROBE_DLL`，F246）；安装前已执行的调用不计数。
- 依赖 **无 ASLR** 的 `game.exe`（F234，ImageBase `0x400000`，md5 `059fd8f39cfd2f763e5ba1a32d22fa73`）。
  换版本/加壳/VAs 变化后必须重跑 `bin/gametop/game.exe.i64` 的清单并更新 `targets.csv`。

## 失效条件

- `game.exe` 换版（md5 变）→ 所有 VA 失效，禁止使用旧 `targets.inc`。
- 目标函数序言含相对跳转 / 首指令跨 24 字节 / 有内部直接入口 → 生成器已跳过并写进 `targets.json.skipped`。
- 游戏启用 ASLR 或加载基址非 `0x400000` → `base+(va-0x400000)` 会写错地址。
- 探针安装后崩溃 = patch 破坏了对齐/序言；先用 `ENTRY_LOG` 对照 installed 数，再二分 targets。
