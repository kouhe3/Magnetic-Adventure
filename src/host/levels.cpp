#include "levels.h"

#include <cstring>

#include "game_files.h"

namespace host {

namespace {

// 去掉行首尾空白
std::string Trim(const std::string& s) {
  size_t b = s.find_first_not_of(" \t\r");
  if (b == std::string::npos) return std::string();
  size_t e = s.find_last_not_of(" \t\r");
  return s.substr(b, e - b + 1);
}

// Value 可能带引号
std::string Unquote(const std::string& s) {
  if (s.size() >= 2 && s.front() == '"' && s.back() == '"') return s.substr(1, s.size() - 2);
  return s;
}

}  // namespace

std::string Utf16LeToUtf8(const unsigned char* data, size_t size) {
  std::string out;
  out.reserve(size / 2);
  size_t i = 0;
  if (size >= 2 && data[0] == 0xFF && data[1] == 0xFE) i = 2;  // BOM
  for (; i + 1 < size; i += 2) {
    unsigned cp = data[i] | (static_cast<unsigned>(data[i + 1]) << 8);
    if (cp >= 0xD800 && cp <= 0xDBFF && i + 3 < size) {
      unsigned lo = data[i + 2] | (static_cast<unsigned>(data[i + 3]) << 8);
      if (lo >= 0xDC00 && lo <= 0xDFFF) {
        cp = 0x10000 + ((cp - 0xD800) << 10) + (lo - 0xDC00);
        i += 2;
      }
    }
    if (cp < 0x80) {
      out.push_back(static_cast<char>(cp));
    } else if (cp < 0x800) {
      out.push_back(static_cast<char>(0xC0 | (cp >> 6)));
      out.push_back(static_cast<char>(0x80 | (cp & 0x3F)));
    } else if (cp < 0x10000) {
      out.push_back(static_cast<char>(0xE0 | (cp >> 12)));
      out.push_back(static_cast<char>(0x80 | ((cp >> 6) & 0x3F)));
      out.push_back(static_cast<char>(0x80 | (cp & 0x3F)));
    } else {
      out.push_back(static_cast<char>(0xF0 | (cp >> 18)));
      out.push_back(static_cast<char>(0x80 | ((cp >> 12) & 0x3F)));
      out.push_back(static_cast<char>(0x80 | ((cp >> 6) & 0x3F)));
      out.push_back(static_cast<char>(0x80 | (cp & 0x3F)));
    }
  }
  return out;
}

bool ParseLevelList(const unsigned char* data, size_t size, std::vector<LevelDef>* out) {
  out->clear();
  const std::string text = Utf16LeToUtf8(data, size);
  LevelDef cur;
  bool in_block = false;
  size_t pos = 0;
  while (pos <= text.size()) {
    size_t nl = text.find('\n', pos);
    if (nl == std::string::npos) nl = text.size();
    const std::string line = Trim(text.substr(pos, nl - pos));
    pos = nl + 1;
    if (line.empty()) continue;
    if (line == "<Level>") {
      cur = LevelDef();
      in_block = true;
      continue;
    }
    if (line == "</Level>") {
      if (in_block) out->push_back(cur);
      in_block = false;
      continue;
    }
    if (!in_block) continue;
    const size_t eq = line.find('=');
    if (eq == std::string::npos) continue;
    const std::string key = Trim(line.substr(0, eq));
    const std::string val = Unquote(Trim(line.substr(eq + 1)));
    if (key == "Caption") cur.caption = val;
    else if (key == "LevelFiles") cur.files = val;
    else if (key == "LevelGroup") cur.group = val;
  }
  return !out->empty();
}

bool LoadLevelList(std::vector<LevelDef>* out) {
  const Pak& pak = GamePak();
  const PakEntry* e = pak.Find("lvl_info.lvl");
  if (!e) return false;
  return ParseLevelList(pak.Data(*e), e->size, out);
}

}  // namespace host
