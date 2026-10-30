// 宿主渲染层 v0（T3.2 里程碑 A）：建 WGL 上下文 + 按抓到的二进制绘制列表画菜单。
//
// 纹理：**直接读游戏 pak**（`data`）里的 37 张素材，WIC 解码后按原版顺序/格式上传
// （F183 的 id↔素材映射、F185 的逐字节解码一致性）。pak 路径：HOST_DATA 指向 pak 文件
// 或含 `data` 的目录，否则用 exe 同级的 `data`。
// 菜单布局：`src/host/menu_layout.cpp` 按「设计空间 1018×739 逻辑像素」现算（F188），
// 不再是抓包回放；二态按钮按鼠标命中切换（F189）。需要逐 draw 对拍时设
// HOST_DRAW_DUMP=<path> 落 GLDRW02，再用 tools/draw_ab.py 与原版抓包比。
//
// 状态复刻（F184）：PFD 24 色 / 24 深度 / 双缓冲 / 无 alpha；纹理用
// WRAP=REPEAT、MIN=LINEAR_MIPMAP_LINEAR、MAG=LINEAR、GL_GENERATE_MIPMAP=1（与启动期实测一致），
// 混合 SRC_ALPHA / ONE_MINUS_SRC_ALPHA；顶点坐标已是 NDC（projection=identity）。
//
// 依据：docs/facts.md F177（64 fps）、F181/F182（绘制列表）、F183（纹理映射）。
#include "gl_render.h"

#include <windows.h>
#include <GL/gl.h>
#include <GL/glu.h>

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>

#include "game_files.h"
#include "menu_layout.h"
#include "pak.h"
#include "texture_table.h"
#include "wic_decode.h"

namespace {

using namespace host;  // pak / WIC / 纹理表都在 host 命名空间

#ifndef GL_GENERATE_MIPMAP
#define GL_GENERATE_MIPMAP 0x8191
#endif
#ifndef GL_CLAMP_TO_EDGE
#define GL_CLAMP_TO_EDGE 0x812F
#endif

const unsigned CAP_TEXTURE_2D = 1u << 0;
const unsigned CAP_DEPTH_TEST = 1u << 1;
const unsigned CAP_BLEND = 1u << 2;
const unsigned CAP_ALPHA_TEST = 1u << 3;
const unsigned CAP_CULL_FACE = 1u << 4;

struct Tex {
  unsigned id;
  GLuint gl;
};

struct Menu {
  std::vector<Tex> tex;
  bool ok = false;
};

Menu g_menu;
HDC g_dc = nullptr;
HGLRC g_rc = nullptr;
HWND g_viewer = nullptr;
int g_w = 0, g_h = 0;

std::string ExeDir() {
  char buf[MAX_PATH];
  DWORD n = GetModuleFileNameA(nullptr, buf, MAX_PATH);
  std::string s(buf, n);
  size_t p = s.find_last_of("\\/");
  return p == std::string::npos ? std::string(".") : s.substr(0, p + 1);
}

unsigned Crc32(const unsigned char* p, size_t n) {
  static unsigned table[256];
  static bool init = false;
  if (!init) {
    for (unsigned i = 0; i < 256; ++i) {
      unsigned c = i;
      for (int k = 0; k < 8; ++k) c = (c & 1) ? 0xEDB88320u ^ (c >> 1) : c >> 1;
      table[i] = c;
    }
    init = true;
  }
  unsigned c = 0xFFFFFFFFu;
  for (size_t i = 0; i < n; ++i) c = table[(c ^ p[i]) & 0xFF] ^ (c >> 8);
  return c ^ 0xFFFFFFFFu;
}

// 与启动期实测一致（F183）：内/外部格式配对 GL_RGB8/GL_RGB 与 GL_RGBA8/GL_RGBA，
// WRAP=REPEAT、MIN=LINEAR_MIPMAP_LINEAR、MAG=LINEAR。mipmap 用 gluBuild2DMipmaps 显式生成
// ——GL_GENERATE_MIPMAP(0x8191) 在部分驱动的兼容 profile 里不生效，会让纹理不完整
// 而采样成白色（第一版就踩了这个）。
GLuint UploadTexture(const unsigned char* px, int w, int h, bool rgb) {
  GLuint id = 0;
  glGenTextures(1, &id);
  glBindTexture(GL_TEXTURE_2D, id);
  glPixelStorei(GL_UNPACK_ALIGNMENT, rgb ? 1 : 4);
  glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT);
  glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT);
  glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR);
  glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
  const GLint internal = rgb ? GL_RGB8 : GL_RGBA8;
  const GLenum format = rgb ? GL_RGB : GL_RGBA;
  if (std::getenv("HOST_GL_NOMIP")) {
    glTexImage2D(GL_TEXTURE_2D, 0, internal, w, h, 0, format, GL_UNSIGNED_BYTE, px);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
  } else {
    GLint gluerr = gluBuild2DMipmaps(GL_TEXTURE_2D, internal, w, h, format, GL_UNSIGNED_BYTE, px);
    if (const char* dp = std::getenv("HOST_TEX_DIAG")) {
      // 诊断：glu 的返回值 + level 0/1 的实际尺寸（非 2 的幂会被 glu 缩放，800x600→1024x512）
      GLint l0w = 0, l0h = 0, l1w = 0, l1h = 0;
      glGetTexLevelParameteriv(GL_TEXTURE_2D, 0, GL_TEXTURE_WIDTH, &l0w);
      glGetTexLevelParameteriv(GL_TEXTURE_2D, 0, GL_TEXTURE_HEIGHT, &l0h);
      glGetTexLevelParameteriv(GL_TEXTURE_2D, 1, GL_TEXTURE_WIDTH, &l1w);
      glGetTexLevelParameteriv(GL_TEXTURE_2D, 1, GL_TEXTURE_HEIGHT, &l1h);
      if (FILE* f = std::fopen(dp, "a")) {
        std::fprintf(f, "tex=%u %s %dx%d internal=%#x fmt=%#x gluerr=%d l0=%dx%d l1=%dx%d glerr=%#x\n",
                     id, rgb ? "RGB" : "RGBA", w, h, internal, format, gluerr, l0w, l0h, l1w,
                     l1h, glGetError());
        std::fclose(f);
      }
    }
  }
  return id;
}

// 直接读 pak：按 mapping/textures.csv（F183）的 id→素材映射逐张解码上传。
// HOST_TEX_CRC=<path> 时把每张上传像素的 CRC32 落盘，供 tools 与原版日志对拍（F185）。
bool LoadTexturesFromPak() {
  if (!OpenGamePak()) return false;
  const Pak& pak = GamePak();
  const char* crc_env = std::getenv("HOST_TEX_CRC");
  FILE* crc = crc_env ? std::fopen(crc_env, "w") : nullptr;
  bool ok = true;
  const size_t want = sizeof(kTextures) / sizeof(kTextures[0]);
  for (size_t i = 0; i < want && ok; ++i) {
    const TextureDef& def = kTextures[i];
    const PakEntry* e = pak.Find(def.asset);
    const bool rgb = def.rgb;
    std::vector<unsigned char> px;
    int w = 0, h = 0;
    ok = e && DecodeImage(pak.Data(*e), e->size, rgb, &w, &h, &px);
    if (!ok) break;
    Tex t = {};
    t.id = def.id;
    t.gl = UploadTexture(px.data(), w, h, rgb);
    g_menu.tex.push_back(t);
    if (crc)
      std::fprintf(crc, "%u %s %d %d %08x\n", def.id, def.asset, w, h,
                   Crc32(px.data(), px.size()));
  }
  if (crc) std::fclose(crc);
  if (g_menu.tex.size() != want) return false;
  return ok;
}

GLuint FindTex(unsigned id) {
  for (auto& t : g_menu.tex)
    if (t.id == id) return t.gl;
  return 0;
}

}  // namespace

bool GlInit(HWND viewer) {
  g_viewer = viewer;
  g_dc = GetDC(viewer);
  if (!g_dc) return false;

  PIXELFORMATDESCRIPTOR pfd = {};
  pfd.nSize = sizeof(pfd);
  pfd.nVersion = 1;
  // 与原版一致（F183 实测 PFD）：窗口 + 双缓冲 + OpenGL，24 色 / 24 深度，无 alpha
  pfd.dwFlags = PFD_DRAW_TO_WINDOW | PFD_SUPPORT_OPENGL | PFD_DOUBLEBUFFER;
  pfd.iPixelType = PFD_TYPE_RGBA;
  pfd.cColorBits = 24;
  pfd.cDepthBits = 24;
  pfd.iLayerType = PFD_MAIN_PLANE;
  int fmt = ChoosePixelFormat(g_dc, &pfd);
  if (!fmt || !SetPixelFormat(g_dc, fmt, &pfd)) return false;
  g_rc = wglCreateContext(g_dc);
  if (!g_rc || !wglMakeCurrent(g_dc, g_rc)) return false;

  if (!WicInit()) return false;
  g_menu.ok = LoadTexturesFromPak();
  if (FILE* f = std::fopen(std::string(ExeDir() + "gl_init.log").c_str(), "w")) {
    std::fprintf(f, "dc=%p rc=%p ok=%d tex=%zu pak=%s err=%#x\n",
                 static_cast<void*>(g_dc), static_cast<void*>(g_rc), g_menu.ok ? 1 : 0,
                 g_menu.tex.size(), GamePakPath().c_str(), glGetError());
    std::fclose(f);
  }
  return g_menu.ok;
}

void GlResize(int w, int h) {
  g_w = w;
  g_h = h;
  if (g_rc) glViewport(0, 0, w, h);
}

namespace {

// 鼠标在视口客户区里的 NDC；不在窗口内返回 false
bool MouseNdc(float* mx, float* my) {
  if (!g_viewer || g_w <= 1 || g_h <= 1) return false;
  POINT p = {0, 0};
  if (!GetCursorPos(&p)) return false;
  if (!ScreenToClient(g_viewer, &p)) return false;
  if (p.x < 0 || p.y < 0 || p.x >= g_w || p.y >= g_h) return false;
  *mx = 2.0f * static_cast<float>(p.x) / g_w - 1.0f;
  *my = 1.0f - 2.0f * static_cast<float>(p.y) / g_h;
  return true;
}

// HOST_DRAW_DUMP=<path>：把宿主现算的 draw 列表按 GLDRW02 落盘，供 tools/draw_ab.py 与原版抓包逐 draw 比
void DumpDraws(const std::vector<MenuDraw>& draws) {
  const char* path = std::getenv("HOST_DRAW_DUMP");
  if (!path) return;
  FILE* f = std::fopen(path, "wb");
  if (!f) return;
  std::fwrite("GLDRW02\0", 1, 8, f);
  unsigned count = static_cast<unsigned>(draws.size());
  std::fwrite(&count, 4, 1, f);
  for (const auto& d : draws) {
    unsigned head[6] = {d.tex, static_cast<unsigned>(d.n), d.caps, 7u /*GL_QUADS*/,
                        d.blend_src, d.blend_dst};
    std::fwrite(head, 4, 6, f);
    std::fwrite(d.rgba, 4, 4, f);
    std::fwrite(d.v, 4, static_cast<size_t>(d.n) * 5, f);
  }
  std::fclose(f);
}

}  // namespace

void GlRenderMenu() {
  if (!g_rc || !g_menu.ok) {
    glClearColor(0.15f, 0.0f, 0.0f, 1.0f);  // 数据缺失时给个明显的底色
    glClear(GL_COLOR_BUFFER_BIT);
    SwapBuffers(g_dc);
    return;
  }
  float mx = 2.0f, my = 2.0f;
  const bool inside = MouseNdc(&mx, &my);
  std::vector<MenuDraw> draws;
  BuildMenuDraws(&draws, mx, my, inside);
  static bool dumped = false;
  if (!dumped) {
    dumped = true;
    DumpDraws(draws);
  }

  glViewport(0, 0, g_w, g_h);
  glClearColor(0.0f, 0.0f, 0.0f, 1.0f);
  glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

  glMatrixMode(GL_PROJECTION);
  glLoadIdentity();
  glMatrixMode(GL_MODELVIEW);
  glLoadIdentity();

  glEnable(GL_BLEND);
  glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
  glDisable(GL_DEPTH_TEST);
  glDisable(GL_CULL_FACE);
  glDisable(GL_LIGHTING);
  glDisable(GL_TEXTURE_2D);
  glColor4f(1, 1, 1, 1);

  for (const auto& d : draws) {
    glBlendFunc(d.blend_src, d.blend_dst);
    if (d.caps & CAP_BLEND) glEnable(GL_BLEND); else glDisable(GL_BLEND);
    if (d.caps & CAP_DEPTH_TEST) glEnable(GL_DEPTH_TEST); else glDisable(GL_DEPTH_TEST);
    if (d.caps & CAP_CULL_FACE) glEnable(GL_CULL_FACE); else glDisable(GL_CULL_FACE);
    if (d.caps & CAP_TEXTURE_2D) glEnable(GL_TEXTURE_2D); else glDisable(GL_TEXTURE_2D);
    GLuint tex = FindTex(d.tex);
    if (tex) glBindTexture(GL_TEXTURE_2D, tex);
    glColor4fv(d.rgba);
    glBegin(GL_QUADS);  // 原版就是 GL_QUADS；文本串的 12 顶点是三个连字（F186）
    for (int i = 0; i < d.n; ++i) {
      const float* p = &d.v[i * 5];
      glTexCoord2f(p[3], p[4]);
      glVertex3f(p[0], p[1], p[2]);
    }
    glEnd();
  }
  static int dbg = 0;
  if (!dbg && std::getenv("HOST_GL_DEBUG")) {
    dbg = 1;
    unsigned char px[5][4];
    const int xs[5] = {g_w / 2, 0, 0, g_w - 1, g_w - 1};
    const int ys[5] = {g_h / 2, 0, g_h - 1, 0, g_h - 1};
    for (int i = 0; i < 5; ++i) {
      glReadPixels(xs[i], ys[i], 1, 1, GL_RGBA, GL_UNSIGNED_BYTE, px[i]);
    }
    if (FILE* f = std::fopen(std::string(ExeDir() + "gl_frame.log").c_str(), "w")) {
      std::fprintf(f, "size=%dx%d center=%02x%02x%02x%02x tl=%02x%02x%02x%02x bl=%02x%02x%02x%02x err=%#x draws=%zu\n",
                   g_w, g_h, px[0][0], px[0][1], px[0][2], px[0][3],
                   px[1][0], px[1][1], px[1][2], px[1][3],
                   px[2][0], px[2][1], px[2][2], px[2][3], glGetError(), draws.size());
      std::fclose(f);
    }
  }
  SwapBuffers(g_dc);

}
