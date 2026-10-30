// pak v0.2 只读解析（宿主侧）：格式见 tools/pak.py 的 docstring（F05/F17）。
//
//   偏移 0   : u32 toc_size = 24 * (count + 1)
//   偏移 4   : char magic[25] = "[Pak Header Info Ver 0.2]"
//   偏移 29  : count × rec{ u8 namelen; char name[namelen]; pad; u32 off; u32 size }（24 B）
//              最后一条 rec 是尾部附加文件，不算条目
//   偏移 29 + toc_size : payload，条目偏移相对这里
//
// 依据：docs/facts.md F05（格式实测）、F17（偏移校验）。
#pragma once

#include <string>
#include <vector>

namespace host {

struct PakEntry {
  std::string name;
  unsigned off = 0;
  unsigned size = 0;
};

class Pak {
 public:
  bool Open(const std::string& path);
  // 名字大小写不敏感（pak 里混有大写扩展名，如 logo_1.JPG）
  const PakEntry* Find(const char* name) const;
  const unsigned char* Data(const PakEntry& e) const { return base_ + e.off; }
  const std::vector<PakEntry>& entries() const { return entries_; }
  const std::string& path() const { return path_; }

 private:
  std::string path_;
  std::vector<unsigned char> blob_;
  const unsigned char* base_ = nullptr;
  std::vector<PakEntry> entries_;
};

}  // namespace host
