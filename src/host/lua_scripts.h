// 用宿主自带的 Lua 5.1.5 编译 pak 里的脚本（**只编译不执行**）。
//
// 为什么只编译：执行关卡脚本会立刻调用宿主的 144 个绑定（`Add_SimplePhysicObject`、
// `Attach_ShapePolygon`…，F180），绑定层是 T3.3 的后续切片。编译这一层能单独证明
// 「VM 版本对、pak 文本能喂进 Lua、111 个脚本语法全过」，而且判据是机器可判的。
//
// 依据：docs/facts.md F04（逻辑是 pak 内明文 Lua 5.1）、F180（116 个 Add* 工厂/144 绑定）。
#pragma once

#include <string>

namespace host {

struct LuaCompileStat {
  int ok = 0;
  int failed = 0;
  std::string first_error;  // 第一条编译错误（含脚本名）
};

LuaCompileStat CompilePakLua();

}  // namespace host
