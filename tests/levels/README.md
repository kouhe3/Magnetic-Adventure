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

## 障碍夹具（wall）

| 文件 | 说明 |
|---|---|
| `wall_o.lua` | 替换 `lvl_o14.lua`：自由金属螺丝 `(0,0)`（`Set_PhysParams(bScrew,5,0,0)` 提高密度防穿墙）+ chalk `(9,0)` + 3 段静态 `Add_WoodFormWall(…,4)`（x≈2.16..5.41，y≈-3.31..3.38） |
| `wall_e.lua` | 替换 `lvl_e14.lua`：到 `(9,0)` 半径 0.6 后写 `(99,99)` 标记 + `DoLevelComplete()` |

这一关验证「磁铁输入能不能绕开碰撞体到达目标」：直线拖会被墙挡住，必须经 waypoint
（`--waypoint STAGE:x,y`，可重复）逐段引导。

```bash
python tools/ci_fake_magnet.py build --out work/fakemag_wall \
  --o tests/levels/wall_o.lua --e tests/levels/wall_e.lua
"%PY32%" tools/ci_fake_magnet.py run --dir work/fakemag_wall --level 1 \
  --stage=0,0:9,0 \
  --waypoint 0:0,6 --waypoint 0:6.5,6 --waypoint 0:6.5,2 \
  --waypoint 0:7.5,1 --waypoint 0:8.4,0.4 \
  --marker 99,99 --done-dist 0.65 --hold 3.0 \
  --waypoint-hold 1.5 --waypoint-tol 2.0 --json work/fakemag_wall.json
```

实测（F408）：

| 运行 | 路径 | 结果 |
|---|---|---|
| 负例 | 无 `--waypoint`，直线到 `(9,0)` | body 停在墙前 x≈2.117，`d_min=6.8912`，markers=0 ⇒ **FAIL** |
| 正例 1 | 上表 5 个 waypoint | `d_min=0.5733`、`pos_min≈(9.28,0.50)`、markers=2 ⇒ **PASS** |
| 正例 2 | 同上（第二次独立启动） | `d_min=0.5900`、`pos_min≈(9.26,0.53)`、markers=2 ⇒ **PASS** |

两次正例的 live 50 ms 最小只有 0.6206/0.7875，again 只能靠逐 step digest 判定。

边界：磁铁无阻尼，光标直达目标时 body 会绕目标转圈（per-step min 停在 2–4）；
最后一段 waypoint 必须靠近目标（`8.4,0.4`）且逐段小步，否则到不了 0.65。

## 齿轮力矩夹具（gear）

| 文件 | 说明 |
|---|---|
| `gear_o.lua` | 两个 `Add_MetallGear` (0,0)/(5,0)；`bStatic = AddStaticWall(0,-25,0)` 后各 `Add_JointNail(0,bStatic,…)`；`Add_JointSimpleGear(g1,g2,j1,j2,0.8)`；`Set_JointMotors(j1,1,1.0,100)` |
| `gear_e.lua` | 空 `AttachScripts`（电机/关节都在 Create 里启动） |
| `gear_nomotor_o.lua` | 负例：`Set_JointMotors(...,1.0,0)`（扭矩 0） |
| `gear_nolink_o.lua` | 负例：删掉 `Add_JointSimpleGear` |

这一关验证 `Add_JointNail` / `Add_JointSimpleGear` / `Set_JointMotors` 的绑定语义：
电机 1.0 rad/s 经 ratio 0.8 的齿轮关节，从动轮应为 **-1.25 rad/s**（F368 的
`w2 = -w1/ratio`）。

```bash
python tools/ci_fake_magnet.py build --out work/fakemag_gear \
  --o tests/levels/gear_o.lua --e tests/levels/gear_e.lua
"%PY32%" tools/ci_fake_magnet.py run --dir work/fakemag_gear --level 1 \
  --observe 2.5 --angle 0,0 --angle 5,0 --gear-ratio 1.25 --min-angle 0.5 \
  --json work/fakemag_gear.json --require-fg
```

判据（`--observe` 模式不按鼠标）：每只被观察 body 的 `|Δangle| >= --min-angle`；
两只时还要求 `Δ1·Δ2 < 0` 且 `|(-Δ2/Δ1) - --gear-ratio| <= --ratio-tol`。

实测（F409）：

| 运行 | 结果 |
|---|---|
| 正例 | `Δ1=2.5500`、`Δ2=-3.1875`、`w1=1.0`、`w2=-1.25`、`ratio_measured=1.25000007` ⇒ **PASS** |
| 负例 no-motor | `Δ1=Δ2=0`（扭矩 0）⇒ **FAIL** |
| 负例 no-link | `Δ1=2.53`、`Δ2=0`、`sign_ok=False`、`ratio_measured≈-0.0` ⇒ **FAIL** |

机制：b2 日志里 `b2_World_Joint_Revolute`×2、`b2_World_Joint_Gear`×1、
`b2_Joint_EnableMotor`/`SetMaxMotorTorque`/`SetMotorSpeed` 各 1。

边界：`bStatic` 必须在 `Create()` 里显式赋值（`AddStaticWall`）；不赋值时
`Add_JointNail` 静默失败——b2 日志 0 个 joint 调用，两轮都不动（本次实测）。

## 开关旋转夹具（switch）

| 文件 | 说明 |
|---|---|
| `switch_o.lua` | 静态锚点 + `AddSimpleSwitchArm(0,0,0,1,bStatic)`（枢轴 `(0,-1.6)`、限位 ±0.5）+ 自由标记螺丝 `(10,10)` |
| `switch_e.lua` | 注册 `OnRotate`；`\|Get_JointAngle(jSwitch)\| > 0.2` 时把标记螺丝传到 `(99,99)` |

这一关验证「磁铁拖拽 → 钉住物体的力矩 → 关节旋转 → `OnRotate` 回调」整条链：
横向拖拽产生力矩，拖拽方向经过枢轴则不产生力矩。

```bash
python tools/ci_fake_magnet.py build --out work/fakemag_switch \
  --o tests/levels/switch_o.lua --e tests/levels/switch_e.lua
"%PY32%" tools/ci_fake_magnet.py run --dir work/fakemag_switch --level 1 \
  --stage=0,0:5,0 --stage-angle 0:0,0 --stage-min-angle 0.2 --ignore-distance \
  --marker 99,99 --hold 2.5 --json work/fakemag_switch.json --require-fg
```

判据：target 锁定；`--stage-angle` 指定的 body 的 `|Δangle| >= --stage-min-angle`；
`--ignore-distance` 关闭「到 goal 的距离」判据（开关被钉住，不会平移）；marker 命中。

实测（F410）：

| 运行 | 结果 |
|---|---|
| 正例（横拖到 `(5,0)`） | `d_min=4.2036`（钉住）、`Δangle=-0.5250`、markers=2 ⇒ **PASS** |
| 负例（拖到 `(0,-2)`，力线过枢轴） | locked=True、`Δangle≈-1.34e-19`、markers=0 ⇒ **FAIL** |

机制：磁铁力作用在 body 中心，枢轴在其下方 1.6；横向力产生力矩，关节转到限位，
`OnRotate` 回调触发。

宿主 OnRotate 验证（F473）：`python tools/ci_fake_magnet.py build --out work/fakemag_switch --o tests/levels/switch_o.lua --e tests/levels/switch_e.lua`，
`python tools/pak.py extract work/fakemag_switch/data work/pak_switch_lua`；
`python work/run_vdesk_host.py rotpos work/profile_test.prf 1 0 200 0 1004 HOST_PHYS_STEPS=200 HOST_MAG_BUTTON=1 HOST_MAG_X=5 HOST_MAG_Y=0 HOST_STEP_LOG=<abs>/host_rot_pos.log HOST_LUA_DIR=work/pak_switch_lua HOST_PAK_DIR=work/pak_switch_lua`
⇒ marker body 在 step 7 起为 (99,99)；负例 `HOST_MAG_X=0 HOST_MAG_Y=-2`（力线过枢轴）⇒ 无 marker、臂角恒 0。

## 接触事件夹具（persist）

`persist_o.lua` / `persist_e.lua`：自由螺丝嵌在静态 WoodWall 内，b2 每步产生
Persist 接触；`OnPersistContact` 计到 5 次就把 marker 移到 (99,99)。负例
`persist_none_o/e.lua` 把螺丝放到 (15,15)，两侧都不应出现 marker。

- 构建/解包：`python tools/ci_fake_magnet.py build --out work/fakemag_persist --o tests/levels/persist_o.lua --e tests/levels/persist_e.lua`；`python tools/pak.py extract work/fakemag_persist/data work/pak_persist_lua`。
- 原版：`B2PROXY_LOG=<abs>/persist_orig.bin <PY32> tools/direct_drive.py --dir work/fakemag_persist --levels 1 --gap 4 --exit-mode wmclose`，从 b2 日志找 marker 的 SetXForm 步号。
- 宿主：`python work/run_vdesk_host.py persistpos work/profile_test.prf 1 0 150 0 1004 HOST_PHYS_STEPS=200 HOST_STEP_LOG=<abs>/host_persist_pos.log HOST_LUA_DIR=work/pak_persist_lua HOST_PAK_DIR=work/pak_persist_lua`。
- 判据（F474）：两侧 marker 都在 **step 7** 生效；负例两侧都无 marker。

## 计时器夹具（timer）

`timer_o.lua` / `timer_e.lua`：静态墙 + 自由螺丝 (10,10) + `Add_SimpleTimer`；
`Start_Timer(tTimer, 1.5)`，`OnTimer` 把螺丝 `Set_ScrObjPos(99,99,0)`。

- 构建：`python tools/ci_fake_magnet.py build --out work/fakemag_timer --o tests/levels/timer_o.lua --e tests/levels/timer_e.lua`
- 原版：`B2PROXY_LOG=<abs>/timer_orig_ffi.bin <PY32> tools/direct_drive.py --dir work/fakemag_timer --levels 1 --gap 5 --exit-mode wmclose`
- 宿主：`python work/run_vdesk_host.py timer2 work/profile_test.prf 1 0 200 0 1004 HOST_PHYS_STEPS=300 HOST_STEP_LOG=<abs>/host_timer_step.log HOST_LUA_DIR=work/pak_timer_lua HOST_PAK_DIR=work/pak_timer_lua`
- 判据（F472）：两侧 `Set_ScrObjPos` 生效的物理步都是 **150**（1.5 s / dt=0.01）；原版从 b2 日志的 `b2_Body_SetXForm` 取步号，宿主从 `HOST_STEP_LOG` 的 marker body 位置取。

边界：只覆盖 1.5 s 的一次性计时器；`Do_Command(cm_StartTimer)` 与 `Start_Timer`
两条路径同实现，但夹具只走 `Start_Timer`；`cm_*` 数值来自 IDA 常量表
（cm_StartTimer=10、cm_StopTimer=11）。

## 边界

- 私有桌面上 `PrintWindow` 返回 1 但客户端为黑；像素不是私有桌面的判据，完成用 Lua 标记。
- `--done-dist` 必须大于夹具自己的完成阈值（chain 用 0.6，命令用 0.65）；
  否则第二段的逐 step min 会被完成时的传送截断在阈值处，判据变成同义反复。
- 假磁铁对轻螺丝施 315 会把 body 甩到穿墙（实测终值 ~`(31,23)`，在关墙外）；
  夹具不依赖 body 留在墙内，只依赖它经过目标点。
- 障碍/齿轮/开关已加（wall/gear/switch）；`work/test_fakemag.py` 是单段原型，已被
  `tools/ci_fake_magnet.py`（build/run、多段、逐 step 判据）取代。
