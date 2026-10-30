// 主菜单的宿主侧布局（T3.2d）：不再回放抓包得到的 draw list，而是按「设计空间矩形」现算。
//
// 依据（docs/facts.md）：
//   F188 把客户区改成 800×600（物理 1200×900）后，21 个 draw 的 NDC bbox 与 1018×739
//        一字不差 ⇒ 原版用**固定设计空间 1018×739 逻辑像素**映射到 NDC，不随客户区重排。
//        菜单元素在这个空间里是 1:1 像素（256×128 的按钮纹理就是 256×128 设计像素），
//        所以下面写设计像素、由 Nd 换算成 NDC。
//   F189 二态按钮悬停时**互斥**：基础项 alpha→0、hover 项 alpha→1（悬停 Play 实测
//        tex=23 alpha 0、tex=24 alpha 1；不悬停时反之）。
//   F186 原版一次 draw 用 GL_QUADS；文本串是单个 glBegin/glEnd 里的 12 顶点（三连字）。
#pragma once

#include <vector>

namespace host {

struct MenuDraw {
  unsigned tex = 0;
  unsigned caps = 0;       // 位：1=TEXTURE_2D 2=DEPTH_TEST 4=BLEND 8=ALPHA_TEST 16=CULL_FACE
  unsigned blend_src = 0;
  unsigned blend_dst = 0;
  float rgba[4] = {1, 1, 1, 1};
  int n = 0;               // 顶点数（每个顶点 5 float：x,y,z,u,v）
  float v[5 * 16] = {};
};

// 设计空间（逻辑像素，左上原点）
const float kDesignW = 1018.0f;
const float kDesignH = 739.0f;

// 鼠标位置（NDC）→ 是否命中某个按钮（设计像素矩形）
struct MenuButton {
  unsigned base_tex;
  unsigned hover_tex;
  float x, y, w, h;
};

const MenuButton* MenuButtons(int* count);

// 生成一帧菜单的 draw 列表（按原版绘制顺序）。
//   mx, my  鼠标 NDC（-1..1）；传 2,2 表示"不在窗口里"（全部按未悬停画）
//   cursor  是否画 GL 光标（tex=1，鼠标未在窗口内时不画）
void BuildMenuDraws(std::vector<MenuDraw>* out, float mx, float my, bool cursor);

}  // namespace host
