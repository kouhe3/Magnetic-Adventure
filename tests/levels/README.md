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

## 边界

- 私有桌面上 `PrintWindow` 返回 1 但客户端为黑；像素不是私有桌面的判据，完成用 Lua 标记。
- 当前只有一只自由螺丝；齿轮力矩/障碍/运行时生成/开关尚未加入（按需扩展本文件）。
- `work/test_fakemag.py` 是原型；`tools/ci_fake_magnet.py` 落地后替换它。
