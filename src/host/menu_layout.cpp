#include "menu_layout.h"

#include "font_table.h"

namespace host {

namespace {

const unsigned CAP_TEXTURE_2D = 1u << 0;
const unsigned CAP_DEPTH_TEST = 1u << 1;
const unsigned CAP_BLEND = 1u << 2;
const unsigned CAP_ALPHA_TEST = 1u << 3;
const unsigned CAP_CULL_FACE = 1u << 4;
const unsigned kCaps = CAP_TEXTURE_2D | CAP_BLEND | CAP_ALPHA_TEST | CAP_CULL_FACE;   // 29
const unsigned kCapsDepth = kCaps | CAP_DEPTH_TEST;                                  // 31
const unsigned kBlendSrc = 0x0302;  // GL_SRC_ALPHA
const unsigned kBlendDst = 0x0303;  // GL_ONE_MINUS_SRC_ALPHA

// 设计像素（1018×739，左上原点）→ NDC
float Nx(float x) { return 2.0f * x / kDesignW - 1.0f; }
float Ny(float y) { return 1.0f - 2.0f * y / kDesignH; }

// 展开成两个三角形（GL_QUADS 的 4 顶点顺序与原版一致：主色在左下）
void Quad(MenuDraw* d, float x, float y, float w, float h, float u0, float v0, float u1,
          float v1) {
  if (d->n + 4 > MenuDraw::kMaxVerts) return;
  const float xs[4] = {x, x + w, x + w, x};
  const float ys[4] = {y + h, y + h, y, y};
  const float us[4] = {u0, u1, u1, u0};
  const float vs[4] = {v0, v0, v1, v1};
  for (int i = 0; i < 4; ++i) {
    float* p = &d->v[(d->n++) * 5];
    p[0] = Nx(xs[i]);
    p[1] = Ny(ys[i]);
    p[2] = 0.0f;
    p[3] = us[i];
    p[4] = vs[i];
  }
}

MenuDraw MakeDraw(unsigned tex, const float rgba[4], unsigned caps) {
  MenuDraw d;
  d.tex = tex;
  d.caps = caps;
  d.blend_src = kBlendSrc;
  d.blend_dst = kBlendDst;
  for (int i = 0; i < 4; ++i) d.rgba[i] = rgba[i];
  return d;
}

void PushFull(std::vector<MenuDraw>* out, unsigned tex, float x, float y, float w, float h,
              unsigned caps) {
  const float white[4] = {1, 1, 1, 1};
  MenuDraw d = MakeDraw(tex, white, caps);
  Quad(&d, x, y, w, h, 0, 0, 1, 1);
  out->push_back(d);
}

// 用户名文本：原点与内容取自抓包那一帧（F192），字形/步进全部来自 gulim1.dat。
// 名字的**来源**（存档/配置里的玩家名）属 T3.6，这里先用抓包时那串。
const float kNickX = 509.0f;   // 首个字形左上（设计像素），F192 实测
const float kNickY = 204.5f;
const char kNickName[] = "ooo";

// 文本：逐字查表出 quad，整串留在同一个 MenuDraw（= 原版一个 glBegin，F186）。
// advance == w，没有额外字距（F192）；空格只推进不出 quad（空白记录 w=10）。
void PushText(MenuDraw* d, float x, float y, const char* s, const FontTable& font) {
  for (const char* p = s; p && *p; ++p) {
    const Glyph* g = font.Find(static_cast<unsigned char>(*p));
    if (!g) continue;
    if (*p != ' ') {
      Quad(d, x, y, static_cast<float>(g->w), static_cast<float>(g->h), g->u0, g->v0, g->u1,
           g->v1);
    }
    x += static_cast<float>(g->w);
  }
}

const MenuButton kButtons[] = {
    // 基础纹理 / 悬停纹理 / 设计像素矩形（都等于纹理原始尺寸）
    {23, 24, 223.0f, 224.0f, 256.0f, 128.0f},  // Play
    {25, 26, 557.0f, 510.0f, 256.0f, 128.0f},  // Exit
    {27, 28, 301.0f, 490.0f, 128.0f, 128.0f},  // Help
    {29, 30, 221.0f, 350.0f, 128.0f, 128.0f},  // Levels/Map
    {31, 32, 615.0f, 356.0f, 256.0f, 128.0f},  // Options
    {33, 34, 579.0f, 226.0f, 256.0f, 128.0f},  // Profile
};

}  // namespace

const MenuButton* MenuButtons(int* count) {
  *count = static_cast<int>(sizeof(kButtons) / sizeof(kButtons[0]));
  return kButtons;
}

void BuildMenuDraws(std::vector<MenuDraw>* out, float mx, float my, bool cursor,
                    const FontTable* font) {
  out->clear();
  out->reserve(16);
  const float white[4] = {1, 1, 1, 1};

  // 1) 木纹背景：上下各半屏，左右/上下各外扩 0.5 设计像素（原版就是这样，避免接缝）
  PushFull(out, 19, -0.5f, -0.25f, 1019.0f, 370.0f, kCaps);
  PushFull(out, 20, -0.5f, 369.25f, 1019.0f, 370.0f, kCaps);
  // 2) 黑板（mm_cent2 1024×512，水平居中、纵向中心 419）
  PushFull(out, 21, -3.0f, 163.0f, 1024.0f, 512.0f, kCaps);
  // 3) "Welcome," 标签（m_label1 256×64，1:1）
  PushFull(out, 22, 277.0f, 186.0f, 256.0f, 64.0f, kCaps);

  // 4) 六个按钮：悬停时基础项 alpha=0、hover 项 alpha=1（F189）
  const float btn_x = (mx + 1.0f) * 0.5f * kDesignW;
  const float btn_y = (1.0f - my) * 0.5f * kDesignH;
  for (int i = 0; i < static_cast<int>(sizeof(kButtons) / sizeof(kButtons[0])); ++i) {
    const MenuButton& b = kButtons[i];
    const bool hot = cursor && btn_x >= b.x && btn_x <= b.x + b.w && btn_y >= b.y &&
                     btn_y <= b.y + b.h;
    const float base_rgba[4] = {1, 1, 1, hot ? 0.0f : 1.0f};
    const float hover_rgba[4] = {1, 1, 1, hot ? 1.0f : 0.0f};
    if (!hot) {
      MenuDraw d = MakeDraw(b.base_tex, base_rgba, kCaps);
      Quad(&d, b.x, b.y, b.w, b.h, 0, 0, 1, 1);
      out->push_back(d);
    } else {
      MenuDraw d = MakeDraw(b.hover_tex, hover_rgba, kCaps);
      Quad(&d, b.x, b.y, b.w, b.h, 0, 0, 1, 1);
      out->push_back(d);
    }
  }

  // 5) 用户名：按 gulim1.dat 现算（T3.5/F192），整串仍是一个 GL_QUADS（F186）
  if (font) {
    const float text_rgba[4] = {0.8984375f, 0.78515625f, 0.51953125f, 1.0f};
    MenuDraw d = MakeDraw(35, text_rgba, kCapsDepth);
    PushText(&d, kNickX, kNickY, kNickName, *font);
    if (d.n) out->push_back(d);
  }

  // 6) 中央微光（mm_cent1 放大到 1205×602）+ 标题（gamename 512×128）
  PushFull(out, 36, -65.5f, 140.0f, 1205.0f, 602.0f, kCaps);
  PushFull(out, 37, 253.0f, 60.0f, 512.0f, 128.0f, kCaps);

  // 7) GL 光标：32×32 设计像素、以鼠标为中心（静止态实测，F188）。
  //    原版的磁铁光标还会**旋转**（glffi4 的帧里是 45°、静止抓包里是 0°），旋转规则未归因。
  if (cursor) {
    const float half = 16.0f;
    MenuDraw d = MakeDraw(1, white, kCapsDepth);
    Quad(&d, btn_x - half, btn_y - half, 32.0f, 32.0f, 0, 0, 1, 1);
    out->push_back(d);
  }
}

}  // namespace host
