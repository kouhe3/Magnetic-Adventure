#include "font_table.h"

#include <cmath>
#include <cstring>

#include "pak.h"

namespace host {

namespace {
const std::size_t kRecordBytes = 32;
}

bool FontTable::Load(const Pak& pak, const char* name, float uv_size) {
  glyphs_.clear();
  name_.assign(name ? name : "");
  uv_ = uv_size > 0.0f ? uv_size : 512.0f;
  const PakEntry* e = pak.Find(name_.c_str());
  if (!e || e->size < kRecordBytes) return false;
  const unsigned char* p = pak.Data(*e);
  const std::size_t n = e->size / kRecordBytes;
  glyphs_.reserve(n);
  for (std::size_t i = 0; i < n; ++i, p += kRecordBytes) {
    Glyph g;
    std::memcpy(&g.ch, p + 0, 4);
    std::memcpy(&g.u0, p + 4, 4);
    std::memcpy(&g.v0, p + 8, 4);
    std::memcpy(&g.u1, p + 12, 4);
    std::memcpy(&g.v1, p + 16, 4);
    std::memcpy(&g.w, p + 20, 4);
    std::memcpy(&g.h, p + 24, 4);
    std::memcpy(&g.flag, p + 28, 4);
    glyphs_.push_back(g);
  }
  return !glyphs_.empty();
}

const Glyph* FontTable::Find(unsigned ch) const {
  for (const Glyph& g : glyphs_) {
    if (g.ch == ch) return &g;
  }
  return nullptr;
}

int FontTable::MismatchCount(float* max_du, float* max_dv) const {
  int bad = 0;
  float du_max = 0.0f, dv_max = 0.0f;
  for (const Glyph& g : glyphs_) {
    const float du = (g.u1 - g.u0) - static_cast<float>(g.w) / uv_;
    const float dv = (g.v1 - g.v0) - static_cast<float>(g.h) / uv_;
    const float au = std::fabs(du), av = std::fabs(dv);
    if (au > 1e-6f || av > 1e-6f) ++bad;
    if (au > du_max) du_max = au;
    if (av > dv_max) dv_max = av;
  }
  if (max_du) *max_du = du_max;
  if (max_dv) *max_dv = dv_max;
  return bad;
}

}  // namespace host
