// 游戏目录资源入口：pak 只打开一次，纹理/关卡/Lua 共用。
//
// 路径规则：HOST_DATA 指向 pak 文件本身或含 `data` 的目录；否则用 exe 同级的 `data`。
// 依据：docs/facts.md F05（pak v0.2 格式）、F187（纹理直读 pak）。
#pragma once

#include <string>

#include "pak.h"

namespace host {

// 打开 pak（幂等）。失败返回 false，后续 GamePak() 不可用。
bool OpenGamePak();
const Pak& GamePak();
std::string GamePakPath();

}  // namespace host
