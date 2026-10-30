#include "pak.h"

#include <cstdio>
#include <cstring>

namespace host {

namespace {

const char kMagic[] = "[Pak Header Info Ver 0.2]";
const size_t kHead = 4 + sizeof(kMagic) - 1;  // 29
const size_t kRec = 24;

unsigned le32(const unsigned char* p) {
  return static_cast<unsigned>(p[0]) | (static_cast<unsigned>(p[1]) << 8) |
         (static_cast<unsigned>(p[2]) << 16) | (static_cast<unsigned>(p[3]) << 24);
}

char lower(char c) { return (c >= 'A' && c <= 'Z') ? static_cast<char>(c - 'A' + 'a') : c; }

bool NameEq(const std::string& a, const char* b) {
  size_t i = 0;
  for (; i < a.size(); ++i) {
    if (!b[i]) return false;
    if (lower(a[i]) != lower(b[i])) return false;
  }
  return b[i] == '\0';
}

}  // namespace

bool Pak::Open(const std::string& path) {
  path_ = path;
  blob_.clear();
  entries_.clear();
  base_ = nullptr;

  FILE* f = std::fopen(path.c_str(), "rb");
  if (!f) return false;
  std::fseek(f, 0, SEEK_END);
  long n = std::ftell(f);
  std::fseek(f, 0, SEEK_SET);
  if (n <= static_cast<long>(kHead)) {
    std::fclose(f);
    return false;
  }
  blob_.resize(static_cast<size_t>(n));
  size_t got = std::fread(blob_.data(), 1, blob_.size(), f);
  std::fclose(f);
  if (got != blob_.size()) return false;

  const unsigned char* d = blob_.data();
  if (std::memcmp(d + 4, kMagic, sizeof(kMagic) - 1) != 0) return false;
  unsigned toc = le32(d);
  if (toc % kRec != 0 || toc < kRec || kHead + toc > blob_.size()) return false;
  unsigned count = toc / kRec - 1;

  size_t pos = kHead;
  for (unsigned i = 0; i < count; ++i, pos += kRec) {
    unsigned namelen = d[pos];
    if (namelen == 0 || pos + kRec > kHead + toc) return false;
    PakEntry e;
    e.name.assign(reinterpret_cast<const char*>(d + pos + 1), namelen);
    e.off = le32(d + pos + 16);
    e.size = le32(d + pos + 20);
    if (static_cast<size_t>(e.off) + e.size > blob_.size() - (kHead + toc)) return false;
    entries_.push_back(std::move(e));
  }
  base_ = d + kHead + toc;
  return true;
}

const PakEntry* Pak::Find(const char* name) const {
  for (const auto& e : entries_)
    if (NameEq(e.name, name)) return &e;
  return nullptr;
}

}  // namespace host
