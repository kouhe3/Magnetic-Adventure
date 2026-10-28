# b2Physics.dll ABI 契约（恢复中）

来源：`bin/baseline/b2Physics.dll`（md5 `5b1d145b774fb60165dbd185691532e9`，与 GameTop 安装目录同文件，F12）。
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

## 4. 导出参数表（机器生成，原始证据）

argc 分布：{0: 1, 1: 42, 2: 34, 3: 9, 4: 1}。表内 `argN=助记符` 是反汇编中该参数被哪些指令引用；**类型未标注**，需在 T2.2 逐个按语义确认（依据 F14）。

| # | 导出 | RVA | 大小 | argc | 参数引用（助记符） |
|---|---|---|---|---|---|
| 1 | `b2_Body_ApplyForce` | 0x10001B20 | 20 | 3 | arg0=mov arg1=mov arg2=mov |
| 2 | `b2_Body_ApplyImpulse` | 0x10001AB0 | 20 | 3 | arg0=mov arg1=mov arg2=mov |
| 3 | `b2_Body_ApplyTorque` | 0x10001B70 | 38 | 2 | arg0=mov arg1=fadd |
| 4 | `b2_Body_ClearShapes` | 0x100019E0 | 35 | 1 | arg0=mov |
| 5 | `b2_Body_CreateShape_Box` | 0x10001870 | 193 | 1 | arg0=fld+fstp+mov |
| 6 | `b2_Body_CreateShape_Circle` | 0x10001940 | 122 | 1 | arg0=mov |
| 7 | `b2_Body_CreateShape_Polygon` | 0x10001700 | 354 | 1 | arg0=mov |
| 8 | `b2_Body_DestroyShape` | 0x10001A10 | 13 | 2 | arg0=mov arg1=mov |
| 9 | `b2_Body_GetAngle` | 0x10001AA0 | 8 | 1 | arg0=mov |
| 10 | `b2_Body_GetAngularDamping` | 0x10001A30 | 11 | 1 | arg0=mov |
| 11 | `b2_Body_GetIsSleeping` | 0x10001C10 | 18 | 1 | arg0=mov |
| 12 | `b2_Body_GetLocalPoint` | 0x10001D90 | 77 | 3 | arg0=mov arg1=mov arg2=mov |
| 13 | `b2_Body_GetLocalVector` | 0x10001D10 | 44 | 3 | arg0=mov arg1=mov arg2=mov |
| 14 | `b2_Body_GetMass` | 0x10001BE0 | 35 | 2 | arg0=mov arg1=mov |
| 15 | `b2_Body_GetOmega` | 0x10001B40 | 8 | 1 | arg0=mov |
| 16 | `b2_Body_GetPosition` | 0x10001A80 | 20 | 2 | arg0=mov arg1=mov |
| 17 | `b2_Body_GetShapeList` | 0x100019D0 | 8 | 1 | arg0=mov |
| 18 | `b2_Body_GetUserData` | 0x10001BA0 | 11 | 1 | arg0=mov |
| 19 | `b2_Body_GetVelocity` | 0x10001AD0 | 20 | 2 | arg0=mov arg1=mov |
| 20 | `b2_Body_GetWorld` | 0x100019C0 | 8 | 1 | arg0=mov |
| 21 | `b2_Body_GetWorldPoint` | 0x10001D40 | 70 | 3 | arg0=mov arg1=mov arg2=mov |
| 22 | `b2_Body_GetWorldVector` | 0x10001CE0 | 44 | 3 | arg0=mov arg1=mov arg2=mov |
| 23 | `b2_Body_GetXForm` | 0x10001A60 | 26 | 2 | arg0=mov arg1=mov |
| 24 | `b2_Body_IsBullet` | 0x10001CC0 | 18 | 1 | arg0=mov |
| 25 | `b2_Body_IsFrozen` | 0x10001C80 | 18 | 1 | arg0=mov |
| 26 | `b2_Body_PutToSleep` | 0x10001C30 | 35 | 1 | arg0=mov |
| 27 | `b2_Body_SetAngularDamping` | 0x10001A20 | 15 | 2 | arg0=mov arg1=fld |
| 28 | `b2_Body_SetBullet` | 0x10001CA0 | 25 | 2 | arg0=mov arg1=cmp |
| 29 | `b2_Body_SetMass` | 0x10001BD0 | 16 | 2 | arg0=mov arg1=mov |
| 30 | `b2_Body_SetMassFromShapes` | 0x10001BC0 | 12 | 1 | arg0=mov |
| 31 | `b2_Body_SetOmega` | 0x10001B50 | 28 | 2 | arg0=mov arg1=fld |
| 32 | `b2_Body_SetUserData` | 0x10001BB0 | 15 | 2 | arg0=mov arg1=mov |
| 33 | `b2_Body_SetVelocity` | 0x10001AF0 | 36 | 2 | arg0=mov arg1=mov |
| 34 | `b2_Body_SetXForm` | 0x10001A40 | 21 | 2 | arg0=mov arg1=mov |
| 35 | `b2_Body_WakeUp` | 0x10001C60 | 21 | 1 | arg0=mov |
| 36 | `b2_CreateWorld` | 0x100013B0 | 40 | 2 | arg0=mov arg1=mov |
| 37 | `b2_DestroyWorld` | 0x100013E0 | 26 | 1 | arg0=mov |
| 38 | `b2_GetMaxPolygonVertices` | 0x100011C0 | 6 | 0 | — |
| 39 | `b2_Joint_EnableLimit` | 0x100023D0 | 155 | 2 | arg0=mov arg1=mov |
| 40 | `b2_Joint_EnableMotor` | 0x10002650 | 155 | 2 | arg0=mov arg1=mov |
| 41 | `b2_Joint_GetAnchor1` | 0x100021B0 | 20 | 2 | arg0=mov arg1=mov |
| 42 | `b2_Joint_GetAnchor2` | 0x100021D0 | 21 | 2 | arg0=mov arg1=mov |
| 43 | `b2_Joint_GetBody1` | 0x10002190 | 8 | 1 | arg0=mov |
| 44 | `b2_Joint_GetBody2` | 0x100021A0 | 8 | 1 | arg0=mov |
| 45 | `b2_Joint_GetJointAngle` | 0x10002230 | 63 | 1 | arg0=fld+fstp+mov |
| 46 | `b2_Joint_GetJointTranslation` | 0x10002270 | 41 | 1 | arg0=mov |
| 47 | `b2_Joint_GetJointType` | 0x10002130 | 53 | 1 | arg0=mov |
| 48 | `b2_Joint_GetLimits` | 0x10002350 | 113 | 3 | arg0=mov arg1=mov arg2=mov |
| 49 | `b2_Joint_GetMotorSpeed` | 0x10002560 | 80 | 1 | arg0=mov |
| 50 | `b2_Joint_GetReactionImpulse` | 0x100021F0 | 27 | 2 | arg0=mov arg1=mov |
| 51 | `b2_Joint_GetReactionTorqImpulse` | 0x10002210 | 18 | 1 | arg0=mov |
| 52 | `b2_Joint_IsLimitEnabled` | 0x10002470 | 80 | 1 | arg0=mov |
| 53 | `b2_Joint_IsMotorEnabled` | 0x100026F0 | 80 | 1 | arg0=mov |
| 54 | `b2_Joint_SetLimits` | 0x100022A0 | 175 | 3 | arg0=mov arg1=fld arg2=fld |
| 55 | `b2_Joint_SetMaxMotorForce` | 0x10002600 | 75 | 2 | arg0=mov arg1=fld |
| 56 | `b2_Joint_SetMaxMotorTorque` | 0x100025B0 | 75 | 2 | arg0=mov arg1=fld |
| 57 | `b2_Joint_SetMotorSpeed` | 0x100024C0 | 155 | 2 | arg0=mov arg1=fld |
| 58 | `b2_Shape_GetBody` | 0x100014D0 | 8 | 1 | arg0=mov |
| 59 | `b2_Shape_GetCirclePos` | 0x10001590 | 63 | 2 | arg0=mov arg1=mov |
| 60 | `b2_Shape_GetCircleRadius` | 0x100015D0 | 40 | 1 | arg0=mov |
| 61 | `b2_Shape_GetDensity` | 0x10001530 | 8 | 1 | arg0=mov |
| 62 | `b2_Shape_GetFilter` | 0x10001640 | 22 | 2 | arg0=mov arg1=mov |
| 63 | `b2_Shape_GetFriction` | 0x10001540 | 8 | 1 | arg0=mov |
| 64 | `b2_Shape_GetNext` | 0x100014E0 | 8 | 1 | arg0=mov |
| 65 | `b2_Shape_GetRestitution` | 0x10001550 | 8 | 1 | arg0=mov |
| 66 | `b2_Shape_GetSensor` | 0x10001610 | 8 | 1 | arg0=mov |
| 67 | `b2_Shape_GetShapeType` | 0x100014F0 | 42 | 1 | arg0=mov |
| 68 | `b2_Shape_SetDensity` | 0x10001560 | 12 | 2 | arg0=mov arg1=fld |
| 69 | `b2_Shape_SetFilter` | 0x10001620 | 22 | 2 | arg0=mov arg1=mov |
| 70 | `b2_Shape_SetFriction` | 0x10001570 | 12 | 2 | arg0=mov arg1=fld |
| 71 | `b2_Shape_SetRestitution` | 0x10001580 | 12 | 2 | arg0=mov arg1=fld |
| 72 | `b2_Shape_SetSensor` | 0x10001600 | 12 | 2 | arg0=mov arg1=mov |
| 73 | `b2_Shape_TestPoint` | 0x10001660 | 156 | 3 | arg0=mov arg1=mov arg2=mov |
| 74 | `b2_World_ClearJoints` | 0x10001DF0 | 34 | 1 | arg0=mov |
| 75 | `b2_World_CreateBody` | 0x10001400 | 119 | 1 | arg0=mov |
| 76 | `b2_World_DestroyBody` | 0x10001480 | 15 | 2 | arg0=mov arg1=mov |
| 77 | `b2_World_DestroyJoint` | 0x10001DE0 | 15 | 2 | arg0=mov arg1=mov |
| 78 | `b2_World_Joint_Distance` | 0x10001E20 | 119 | 1 | arg0=mov |
| 79 | `b2_World_Joint_Gear` | 0x100020D0 | 81 | 1 | arg0=mov |
| 80 | `b2_World_Joint_Prismatic` | 0x10001F50 | 184 | 1 | arg0=mov |
| 81 | `b2_World_Joint_Pulley` | 0x10002010 | 183 | 1 | arg0=mov |
| 82 | `b2_World_Joint_Revolute` | 0x10001EA0 | 170 | 1 | arg0=mov |
| 83 | `b2_World_ReFilter` | 0x10001350 | 30 | 1 | arg0=mov |
| 84 | `b2_World_SetContactFilterCallBack` | 0x10001390 | 24 | 2 | arg0=mov arg1=mov |
| 85 | `b2_World_SetContactListenerCallBack` | 0x10001370 | 24 | 2 | arg0=mov arg1=mov |
| 86 | `b2_World_SetGravity` | 0x100014B0 | 26 | 2 | arg0=mov arg1=mov |
| 87 | `b2_World_Step` | 0x10001490 | 28 | 4 | arg0=mov arg1=fld arg2=mov arg3=mov |

## 4. 待证

| 项 | 状态 | 下一步 |
|---|---|---|
| Box2D 精确小版本（2.0.1 vs 2.0.2） | 待证 | 用上游源码编译同函数，比对常量与指令序列 |
| 每个导出的参数顺序/返回值 | 待证 | 逐条按反汇编确认（IDA 推断的 prototype 有误） |
| `b2_Shape_GetShapeType` case 0 返回全局 `dword_100398D4` | 待证 | 查该全局初值与写入点 |
| `b2_Body_SetXForm`/`GetXForm` 的方向（out vs body） | 待证 | 反汇编确认第一个参数是 out 还是 body |
| 静态 CRT 版本（决定异常/堆行为） | 待证 | 比对 CRT 特征串；实现侧用 /MT 即可 |
