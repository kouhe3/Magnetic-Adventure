#include "wic_decode.h"

#include <windows.h>
#include <wincodec.h>

namespace host {

namespace {

IWICImagingFactory* g_factory = nullptr;

}  // namespace

bool WicInit() {
  if (g_factory) return true;
  HRESULT hr = CoInitializeEx(nullptr, COINIT_APARTMENTTHREADED);
  if (FAILED(hr) && hr != RPC_E_CHANGED_MODE) return false;
  return SUCCEEDED(CoCreateInstance(CLSID_WICImagingFactory, nullptr, CLSCTX_INPROC_SERVER,
                                    IID_PPV_ARGS(&g_factory)));
}

void WicShutdown() {
  if (g_factory) {
    g_factory->Release();
    g_factory = nullptr;
  }
}

bool DecodeImage(const unsigned char* bytes, size_t n, bool rgb, int* w, int* h,
                 std::vector<unsigned char>* out) {
  if (!g_factory || !bytes || n == 0) return false;
  IWICStream* stream = nullptr;
  IWICBitmapDecoder* dec = nullptr;
  IWICBitmapFrameDecode* frame = nullptr;
  IWICFormatConverter* conv = nullptr;
  bool ok = false;
  UINT width = 0, height = 0;
  std::vector<unsigned char> bgra;
  do {
    if (FAILED(g_factory->CreateStream(&stream))) break;
    if (FAILED(stream->InitializeFromMemory(const_cast<BYTE*>(bytes), static_cast<DWORD>(n))))
      break;
    if (FAILED(g_factory->CreateDecoderFromStream(stream, nullptr, WICDecodeMetadataCacheOnLoad,
                                                  &dec)))
      break;
    if (FAILED(dec->GetFrame(0, &frame))) break;
    if (FAILED(g_factory->CreateFormatConverter(&conv))) break;
    if (FAILED(conv->Initialize(frame, GUID_WICPixelFormat32bppBGRA, WICBitmapDitherTypeNone,
                                nullptr, 0.0, WICBitmapPaletteTypeCustom)))
      break;
    if (FAILED(conv->GetSize(&width, &height)) || width == 0 || height == 0) break;
    bgra.resize(static_cast<size_t>(width) * height * 4);
    if (FAILED(conv->CopyPixels(nullptr, width * 4, static_cast<UINT>(bgra.size()),
                                bgra.data())))
      break;
    ok = true;
  } while (false);
  if (conv) conv->Release();
  if (frame) frame->Release();
  if (dec) dec->Release();
  if (stream) stream->Release();
  if (!ok) return false;

  const size_t bpp = rgb ? 3 : 4;
  out->resize(static_cast<size_t>(width) * height * bpp);
  for (UINT y = 0; y < height; ++y) {
    // GL 的上传顺序是自下而上：源图最后一行先出
    const unsigned char* src = &bgra[static_cast<size_t>(height - 1 - y) * width * 4];
    unsigned char* dst = &(*out)[static_cast<size_t>(y) * width * bpp];
    for (UINT x = 0; x < width; ++x) {
      dst[x * bpp + 0] = src[x * 4 + 2];
      dst[x * bpp + 1] = src[x * 4 + 1];
      dst[x * bpp + 2] = src[x * 4 + 0];
      if (!rgb) dst[x * bpp + 3] = src[x * 4 + 3];
    }
  }
  *w = static_cast<int>(width);
  *h = static_cast<int>(height);
  return true;
}

}  // namespace host
