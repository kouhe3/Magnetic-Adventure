// 宿主渲染层 v0（T3.2 里程碑 A）：建 WGL 上下文 + 按抓到的二进制绘制列表画菜单。
//
// 输入是两份数据文件（同 exe 目录，可用 MENU_TEX / MENU_DRAW 覆盖）：
//   menu_tex.bin  "GLTEX01\0" + u32 count + count × {u32 id,w,h, RGBA 像素（自下而上）}
//                 由 tools/gl_texpack.py 从启动期 GL 日志 + pak 素材生成（F183）
//   menu_draw.bin "GLDRW01\0" + u32 count + 每个 draw{u32 tex,n,caps,src,dst; f32 rgba[4];
//                 n × f32 (x,y,z,u,v)}，由 tools/gl_drawlist.py --pack 生成（F181/F182）
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

namespace {

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
  unsigned id, w, h;
  GLuint gl;
};

struct Draw {
  unsigned tex, n, caps, src, dst;
  float rgba[4];
  std::vector<float> v;  // n × (x,y,z,u,v)
};

struct Menu {
  std::vector<Tex> tex;
  std::vector<Draw> draws;
  bool ok = false;
};

Menu g_menu;
HDC g_dc = nullptr;
HGLRC g_rc = nullptr;
int g_w = 0, g_h = 0;

std::string ExeDir() {
  char buf[MAX_PATH];
  DWORD n = GetModuleFileNameA(nullptr, buf, MAX_PATH);
  std::string s(buf, n);
  size_t p = s.find_last_of("\\/");
  return p == std::string::npos ? std::string(".") : s.substr(0, p + 1);
}

bool ReadFileBytes(const std::string& path, std::vector<unsigned char>* out) {
  FILE* f = std::fopen(path.c_str(), "rb");
  if (!f) return false;
  std::fseek(f, 0, SEEK_END);
  long n = std::ftell(f);
  std::fseek(f, 0, SEEK_SET);
  out->resize(n > 0 ? static_cast<size_t>(n) : 0);
  size_t got = n > 0 ? std::fread(out->data(), 1, out->size(), f) : 0;
  std::fclose(f);
  return got == out->size();
}

// 从目录读，可用环境变量覆盖
std::string DataPath(const char* env, const char* leaf) {
  char buf[MAX_PATH];
  DWORD n = GetEnvironmentVariableA(env, buf, MAX_PATH);
  if (n > 0 && n < MAX_PATH) return std::string(buf);
  return ExeDir() + leaf;
}

bool LoadTex(const std::string& path) {
  std::vector<unsigned char> b;
  if (!ReadFileBytes(path, &b)) return false;
  if (b.size() < 12 || std::memcmp(b.data(), "GLTEX01", 7) != 0) return false;
  unsigned count = 0;
  std::memcpy(&count, b.data() + 8, 4);
  size_t off = 12;
  for (unsigned i = 0; i < count; ++i) {
    Tex t = {};
    if (off + 12 > b.size()) return false;
    std::memcpy(&t.id, b.data() + off, 4);
    std::memcpy(&t.w, b.data() + off + 4, 4);
    std::memcpy(&t.h, b.data() + off + 8, 4);
    off += 12;
    size_t bytes = static_cast<size_t>(t.w) * t.h * 4;
    if (off + bytes > b.size()) return false;
    glGenTextures(1, &t.gl);
    glBindTexture(GL_TEXTURE_2D, t.gl);
    glPixelStorei(GL_UNPACK_ALIGNMENT, 4);
    // 与启动期实测一致（F183）：REPEAT + 三线性。mipmap 用 gluBuild2DMipmaps 显式生成
    // ——GL_GENERATE_MIPMAP(0x8191) 在部分驱动的兼容 profile 里不生效，会让纹理不完整
    // 而采样成白色（第一版就踩了这个）。
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
    if (std::getenv("HOST_GL_NOMIP")) {
      glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, t.w, t.h, 0, GL_RGBA, GL_UNSIGNED_BYTE,
                   b.data() + off);
      glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
    } else {
      gluBuild2DMipmaps(GL_TEXTURE_2D, GL_RGBA8, t.w, t.h, GL_RGBA, GL_UNSIGNED_BYTE,
                        b.data() + off);
    }
    off += bytes;
    g_menu.tex.push_back(t);
  }
  return true;
}

bool LoadDraw(const std::string& path) {
  std::vector<unsigned char> b;
  if (!ReadFileBytes(path, &b)) return false;
  if (b.size() < 12 || std::memcmp(b.data(), "GLDRW01", 7) != 0) return false;
  unsigned count = 0;
  std::memcpy(&count, b.data() + 8, 4);
  size_t off = 12;
  for (unsigned i = 0; i < count; ++i) {
    Draw d = {};
    if (off + 28 > b.size()) return false;
    std::memcpy(&d.tex, b.data() + off, 4);
    std::memcpy(&d.n, b.data() + off + 4, 4);
    std::memcpy(&d.caps, b.data() + off + 8, 4);
    std::memcpy(&d.src, b.data() + off + 12, 4);
    std::memcpy(&d.dst, b.data() + off + 16, 4);
    std::memcpy(d.rgba, b.data() + off + 20, 16);
    off += 36;
    d.v.resize(static_cast<size_t>(d.n) * 5);
    if (off + d.v.size() * 4 > b.size()) return false;
    std::memcpy(d.v.data(), b.data() + off, d.v.size() * 4);
    off += d.v.size() * 4;
    g_menu.draws.push_back(std::move(d));
  }
  return true;
}

GLuint FindTex(unsigned id) {
  for (auto& t : g_menu.tex)
    if (t.id == id) return t.gl;
  return 0;
}

}  // namespace

bool GlInit(HWND viewer) {
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

  g_menu.ok = LoadTex(DataPath("MENU_TEX", "menu_tex.bin")) &&
              LoadDraw(DataPath("MENU_DRAW", "menu_draw.bin"));
  if (FILE* f = std::fopen(std::string(ExeDir() + "gl_init.log").c_str(), "w")) {
    std::fprintf(f, "dc=%p rc=%p ok=%d tex=%zu draws=%zu err=%#x\n",
                 static_cast<void*>(g_dc), static_cast<void*>(g_rc), g_menu.ok ? 1 : 0,
                 g_menu.tex.size(), g_menu.draws.size(), glGetError());
    std::fclose(f);
  }
  return g_menu.ok;
}

void GlResize(int w, int h) {
  g_w = w;
  g_h = h;
  if (g_rc) glViewport(0, 0, w, h);
}

void GlRenderMenu() {
  if (!g_rc || !g_menu.ok) {
    glClearColor(0.15f, 0.0f, 0.0f, 1.0f);  // 数据缺失时给个明显的底色
    glClear(GL_COLOR_BUFFER_BIT);
    SwapBuffers(g_dc);
    return;
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

  for (auto& d : g_menu.draws) {
    glBlendFunc(d.src, d.dst);
    if (d.caps & CAP_BLEND) glEnable(GL_BLEND); else glDisable(GL_BLEND);
    if (d.caps & CAP_DEPTH_TEST) glEnable(GL_DEPTH_TEST); else glDisable(GL_DEPTH_TEST);
    if (d.caps & CAP_CULL_FACE) glEnable(GL_CULL_FACE); else glDisable(GL_CULL_FACE);
    if (d.caps & CAP_TEXTURE_2D) glEnable(GL_TEXTURE_2D); else glDisable(GL_TEXTURE_2D);
    GLuint tex = FindTex(d.tex);
    if (tex) glBindTexture(GL_TEXTURE_2D, tex);
    glColor4fv(d.rgba);
    glBegin(GL_TRIANGLE_FAN);
    for (unsigned i = 0; i < d.n; ++i) {
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
                   px[2][0], px[2][1], px[2][2], px[2][3], glGetError(), g_menu.draws.size());
      std::fclose(f);
    }
  }
  SwapBuffers(g_dc);

}
