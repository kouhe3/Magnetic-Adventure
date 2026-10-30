// 关卡清单 lvl_info.lvl：pak 内的 **UTF-16LE 文本**，INI 式块：
//   <Level>
//   Caption = "Introduction"
//   LevelFiles = "lvl_o0.lua, lvl_e0.lua, basefs.lua"
//   LevelGroup = "Tutorial"
//   </Level>
// 依据：docs/facts.md F180（格式实测：13,416 B / 52 关）。
#pragma once

#include <cstddef>
#include <string>
#include <vector>

namespace host {

struct LevelDef {
  std::string caption;
  std::string files;  // 逗号分隔的 .lua 名
  std::string group;
};

bool ParseLevelList(const unsigned char* data, size_t size, std::vector<LevelDef>* out);

// 从已打开的 pak 读 `lvl_info.lvl` 并解析
bool LoadLevelList(std::vector<LevelDef>* out);

// UTF-16LE → UTF-8（BOM 可选）
std::string Utf16LeToUtf8(const unsigned char* data, size_t size);

}  // namespace host
