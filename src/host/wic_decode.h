// PNG/JPG 解码（Windows Imaging Component，系统自带，无需 vendor 第三方库）。
//
// 选型依据（2026-10-30 探测）：WIC 解码 pak 里的 37 张素材后，按原版上传顺序
// （自下而上）与上传格式（RGB / RGBA）算 CRC32，与 GL 代理抓到的 37 次
// glTexImage2D 整块像素 CRC **37/37 逐字节相同**（含 5 张 JPG）⇒ 不必 vendor
// libpng/libjpeg。出处见 docs/facts.md F185。
#pragma once

#include <cstddef>
#include <vector>

namespace host {

bool WicInit();
void WicShutdown();

// 解码为 **自下而上** 的像素（GL 上传顺序）：rgb=true 时 3 字节/像素，否则 4 字节并补 alpha=255。
bool DecodeImage(const unsigned char* bytes, size_t n, bool rgb, int* w, int* h,
                 std::vector<unsigned char>* out);

}  // namespace host
