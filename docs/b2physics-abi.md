# b2Physics.dll ABI 契约（恢复中）

来源：`baseline/磁力大冒险/b2Physics.dll`（md5 `5b1d145b774fb60165dbd185691532e9`，与 GameTop 安装目录同文件，F12）。
IDA 基址 `0x10000000`；导出清单 `mapping/b2physics-exports.csv`（88 条 = 87 个 `b2_*` + `DllEntryPoint`）。

## 1. 构建指纹（L2，已证）

| 项 | 实测 | 出处 |
|---|---|---|
| Box2D 版本族 | **2.0.x**：`b2PolygonDef`/`b2CircleDef` 带 vftable（`0x1002CD0C`/`0x1002CD04`），`b2_GetMaxPolygonVertices()` 直接 `return 8` | IDA 反编译 |
| CRT | 静态链接（只导入 KERNEL32，无 MSVCRT `*.dll` 依赖） | imports |
| 调用约定 | 全部 `__cdecl`，32 位栈参数 | 反汇编 |
| 世界对象 | `b2_CreateWorld` → `operator new(0x19288)` | @0x100013B0 |
| body def | `b2_World_CreateBody` 栈上构造 0x3C(60) 字节结构 | @0x10001400 |

## 2. 调用方可见结构（实测偏移）

### 2.1 形状描述公共头（三种形状共用前 20 字节）

| 偏移 | 类型 | 含义 |
|---|---|---|
| +4 | float | density |
| +8 | float | friction |
| +12 | float | restitution |
| +16 | u8 | isSensor |

### 2.2 Box 扩展（`b2_Body_CreateShape_Box` @0x10001870）

| 偏移 | 类型 | 含义 |
|---|---|---|
| +20 | float | center.x |
| +24 | float | center.y |
| +28 | float | halfWidth |
| +32 | float | halfHeight |

顶点按 `center ± halfExtent` 生成（`v11 = x20 - x28`、`v13 = x28 + x20`）。

### 2.3 Circle 扩展（@0x10001940）

| 偏移 | 类型 | 含义 |
|---|---|---|
| +20 | float | localPosition.x |
| +24 | float | localPosition.y |
| +28 | float | radius |

### 2.4 Polygon 扩展（@0x10001700）

| 偏移 | 类型 | 含义 |
|---|---|---|
| +20 | int | vertexCount |
| +28 | b2Vec2[] | 顶点数组，步长 8 |

### 2.5 变换 XForm（`b2_Shape_TestPoint` 输入）

| 偏移 | 类型 | 含义 |
|---|---|---|
| 0 | b2Vec2 | position |
| 8 | float | angle |

`b2_Shape_TestPoint` 用它展开成 `b2XForm`（cos/sin 计算 R）。

### 2.6 滤镜 Filter（6 字节）

| 偏移 | 类型 | 含义 |
|---|---|---|
| 0 | u16 | categoryBits |
| 2 | u16 | maskBits |
| 4 | i16 | groupIndex |

`b2_Shape_SetFilter` 写入 `shape+34` 起 6 字节；`b2_Shape_GetFilter` 反向读。

## 3. 导出族清单

| 族 | 数量 | 成员 |
|---|---|---|
| World | 12 | `b2_CreateWorld`/`DestroyWorld`/`World_Step`/`World_SetGravity`/`World_ReFilter`/`World_SetContactListenerCallBack`/`World_SetContactFilterCallBack`/`World_CreateBody`/`World_DestroyBody`/`World_ClearJoints`/`World_DestroyJoint`/`World_Joint_{Distance,Revolute,Prismatic,Pulley,Gear}` |
| Body | 35 | `CreateShape_{Box,Circle,Polygon}`、`Get/Set{XForm,Position,Angle,Velocity,Omega,Mass,...}`、`Apply{Force,Impulse,Torque}`、`Get/SetUserData`、`Sleep/Wake/PutToSleep/GetIsSleeping/IsFrozen/SetBullet/IsBullet`、`Get{World,Local}{Point,Vector}` |
| Shape | 14 | `GetBody/Next/ShapeType/Density/Friction/Restitution/CirclePos/CircleRadius/Sensor/Filter`、对应 Set、`TestPoint` |
| Joint | 13 | `GetBody1/2`、`Get/SetLimits`、`Enable/IsLimit`、`Motor{Speed,MaxForce,MaxTorque,Enable,IsEnabled}`、`GetAnchor1/2`、`GetJoint{Angle,Translation,Type}`、`GetReaction{Impulse,TorqImpulse}` |
| 杂项 | 1 | `GetMaxPolygonVertices` |

## 4. 待证

| 项 | 状态 | 下一步 |
|---|---|---|
| Box2D 精确小版本（2.0.1 vs 2.0.2） | 待证 | 用上游源码编译同函数，比对常量与指令序列 |
| 每个导出的参数顺序/返回值 | 待证 | 逐条按反汇编确认（IDA 推断的 prototype 有误） |
| `b2_Shape_GetShapeType` case 0 返回全局 `dword_100398D4` | 待证 | 查该全局初值与写入点 |
| `b2_Body_SetXForm`/`GetXForm` 的方向（out vs body） | 待证 | 反汇编确认第一个参数是 out 还是 body |
| 静态 CRT 版本（决定异常/堆行为） | 待证 | 比对 CRT 特征串；实现侧用 /MT 即可 |
