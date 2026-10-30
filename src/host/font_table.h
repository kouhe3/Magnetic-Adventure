// 位图字模表：pak 里的 `*.dat`，32 B/字。T3.5 的排版数据源。
//
// 依据（docs/facts.md）：
//   F192  `gulim1.dat` 258 条 × 32 B：{u32 ch; f32 u0,v0,u1,v1; u32 w,h,flag}；UV 以
//         512 归一化。抓包里 'o'（ch=111）的 quad 与表内那条记录**逐位相同**，
//         advance == w、行高 == h ⇒ 原版是"查表 + 按 w 步进"，不是 GLScene 定宽渲染。
//   F200  258 条全部满足 u1-u0 == w/512、v1-v0 == h/512（精确相等），h 恒 31，
//         ASCII 32..126 全覆盖 ⇒ 字段语义可用自检守住。
//
// 覆盖边界：只解 gulim1/gulim2 这类 32 B 记录表；`pt_sans.dat`（3176 B、不按 32 对齐）格式未解。
#pragma once

#include <cstddef>
#include <string>
#include <vector>

namespace host {

class Pak;

struct Glyph {
  unsigned ch = 0;
  float u0 = 0.0f, v0 = 0.0f, u1 = 0.0f, v1 = 0.0f;
  unsigned w = 0, h = 0, flag = 0;
};

class FontTable {
 public:
  // name 例 "gulim1.dat"；uv_size 是该表 UV 的归一化基准（gulim1/gulim2 都是 512）
  bool Load(const Pak& pak, const char* name, float uv_size = 512.0f);
  const Glyph* Find(unsigned ch) const;  // 线性表（≤ 数百条），够用
  std::size_t size() const { return glyphs_.size(); }
  // 结构自检（F200）：返回不满足 u1-u0==w/uv 或 v1-v0==h/uv 的条数
  int MismatchCount(float* max_du, float* max_dv) const;
  const char* name() const { return name_.c_str(); }
  float uv_size() const { return uv_; }

 private:
  std::vector<Glyph> glyphs_;
  std::string name_;
  float uv_ = 512.0f;
};

}  // namespace host
