# 测试关卡（Pak v0.2 同名替换）

用途：用原版加载**自选 b2d 物件**的关卡，不再依赖真实关卡的谜题。当前最小版：
自由金属螺丝 `(0,0)` + chalk `(5,0)`；螺丝进入 `(5,0)` 半径 0.3 后
`Set_ScrObjPos(bScrew,99,99,0)`（完成标记）+ `DoLevelComplete()`。

## 文件

| 文件 | 说明 |
|---|---|
| `test_lvl_o.lua` | 替换关卡记录里的 `lvl_o14.lua`（Create：相机/背景/螺丝/chalk） |
| `test_lvl_e.lua` | 替换 `lvl_e14.lua`（AttachScripts + OnMove 完成逻辑 + 99,99 标记） |

关卡记录（`lvl_info.lvl`）仍指向 `lvl_o14.lua` / `lvl_e14.lua`，所以**不新增 entry、不改地图/关卡列表**；
dispatch index 仍是 1（Let's Get Acquainted 的 slot）。

## 构建（副本，`bin/gametop` 只读）

```bash
cp -r work/e2e_game work/pak_test_game
python tools/pak_write.py rebuild work/e2e_game/data work/pak_test_game/data \
  lvl_o14.lua=tests/levels/test_lvl_o.lua \
  lvl_e14.lua=tests/levels/test_lvl_e.lua
python tools/pak_write.py verify work/pak_test_game/data
```

## 判据

1. **原版加载**：`tools/direct_drive.py --dir work/pak_test_game --levels 1` 进关；
   B2 digest 恰好 5 bodies = 4 面墙 + 螺丝 `(0.000,0.000)`（F388）。
2. **fake magnet**：`B2CI_FAKE_MAGNET=1` + 32 位 `work/test_fakemag.py`：
   target 锁定 → 螺丝到 `(5,0)` → b2 全量日志出现 `b2_Body_SetXForm`（id=34）的 `(99,99)` 标记
   （`completion_marker` 非空）→ `fg_same True`。
3. **默认零行为**：不设 `B2CI_FAKE_MAGNET` 时关卡照常加载/step。

## 运行时生成夹具（chain）

| 文件 | 说明 |
|---|---|
| `chain_o.lua` | 替换 `lvl_o14.lua`：自由金属螺丝 `(0,0)` + chalk `(3,0)`；`bScrew2/bChalk2` 先置 0 |
| `chain_e.lua` | 替换 `lvl_e14.lua`：第一颗到 `(3,0)` 半径 0.6 后，**在 `OnMove` 回调里**创建第二颗螺丝 `(-3,3)` + chalk `(0,6)` 并注册 `OnMove`；第二颗到 `(0,6)` 后写 `Set_ScrObjPos(99,99)` + `DoLevelComplete()` |

这一关验证的是「磁铁把 body 拖到目标 → Lua 回调在关卡运行中创建新 body → 磁铁再拖新 body」，
即按需生成的对象也能被 CI 找到并驱动（不依赖关卡初始对象表）。

构建与运行（32 位 Python）：

```bash
python tools/ci_fake_magnet.py build --out work/fakemag_chain \
  --o tests/levels/chain_o.lua --e tests/levels/chain_e.lua
"%PY32%" tools/ci_fake_magnet.py run --dir work/fakemag_chain --level 1 \
  --stage=0,0:3,0 --stage=-3,3:0,6 --marker 99,99 --done-dist 0.65 \
  --hold 2.5 --runtime-stage 1 --require-fg --json work/fakemag_chain.json
```

判据（退出码 0 = PASS，逐项写在 `work/fakemag_chain.json`）：

1. 每段按下时 `player+0x14` 锁定 target；每段 body 的**逐 step** 最小距离
   （`b2_World_Step` 的 digest，不是 50 ms 轮询）< `--done-dist`；
2. `--marker 99,99` 在 `b2_Body_SetXForm` 的 pre 记录里出现；
3. 磁铁 `ApplyForce` 行满足 F386：方向 = mouse−target、`|F|<=315`、远场 315、
   近场 30·d（容差 2.5）、body = 该段 target 的 body；
4. `--runtime-stage 1` 的 body 不在进关时的初始 digest 里（运行时生成）；
5. 游戏窗口从未成为用户前台（`--require-fg`）且 `ExitProcess` 干净退出。

负例（每条只改一个变量）：

```bash
# 距离判据：第二段完成时夹具把 body 传送到 (99,99)，逐 step min 被夹具阈值截断在 ~0.597
"%PY32%" tools/ci_fake_magnet.py run --dir work/fakemag_chain --level 1 \
  --stage=0,0:3,0 --stage=-3,3:0,6 --marker 99,99 --done-dist 0.1 \
  --runtime-stage 1                      # FAIL
# marker 判据：换一个不存在的完成位置
"%PY32%" tools/ci_fake_magnet.py run ... --marker 77,77   # FAIL（marker_ok=False）
# runtime 判据：把第一段（初始就存在的 body）标成 runtime
"%PY32%" tools/ci_fake_magnet.py run ... --runtime-stage 0  # FAIL
```

实测（F407，pid 10048）：两段 `d_min=0.2868/0.5974`、markers=2、磁铁 ApplyForce
315 行（方向 ≤0.0097 rad、力律误差 ≤0.0048）、`fg_game_events=[]`、`exit_clean=True`。
live 50 ms 轮询在同样两段上只看到 0.57–0.71，所以判据必须读逐 step digest。

## 边界

- 私有桌面上 `PrintWindow` 返回 1 但客户端为黑；像素不是私有桌面的判据，完成用 Lua 标记。
- `--done-dist` 必须大于夹具自己的完成阈值（chain 用 0.6，命令用 0.65）；
  否则第二段的逐 step min 会被完成时的传送截断在阈值处，判据变成同义反复。
- 假磁铁对轻螺丝施 315 会把 body 甩到穿墙（实测终值 ~`(31,23)`，在关墙外）；
  夹具不依赖 body 留在墙内，只依赖它经过目标点。
- 齿轮力矩/障碍/开关尚未加入；`work/test_fakemag.py` 是单段原型，已被
  `tools/ci_fake_magnet.py`（build/run、多段、逐 step 判据）取代。
