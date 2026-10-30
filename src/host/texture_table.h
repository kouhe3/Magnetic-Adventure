// 生成物，勿手改 —— python tools/gen_texture_table.py mapping/textures.csv
// 依据 docs/facts.md F183：启动期 37 次 glTexImage2D 的 id 与 pak 素材一一对应；
// rgb=true 表示原版按 GL_RGB/GL_RGB8 上传（5 张 JPG），其余是 GL_RGBA/GL_RGBA8。
#pragma once

namespace host {

struct TextureDef {
  unsigned id;
  const char* asset;
  bool rgb;
};

static const TextureDef kTextures[] = {
    {1, "mcur_1.png", false},
    {2, "logo_1.JPG", true},
    {3, "logo_2.JPG", true},
    {4, "logo_3.jpg", true},
    {5, "logo_3.png", false},
    {6, "hint_atl.png", false},
    {7, "dot_1.png", false},
    {8, "dot_1.png", false},
    {9, "dot_1.png", false},
    {10, "dot_1.png", false},
    {11, "dot_1.png", false},
    {12, "dot_1.png", false},
    {13, "dot_1.png", false},
    {14, "dot_1.png", false},
    {15, "dot_1.png", false},
    {16, "dot_1.png", false},
    {17, "mbtn_1.png", false},
    {18, "mbtn_2.png", false},
    {19, "menubk_1.jpg", true},
    {20, "menubk_2.jpg", true},
    {21, "mm_cent2.png", false},
    {22, "m_label1.png", false},
    {23, "play_1.png", false},
    {24, "play_2.png", false},
    {25, "exit_1.png", false},
    {26, "exit_2.png", false},
    {27, "help_1.png", false},
    {28, "help_2.png", false},
    {29, "levels_1.png", false},
    {30, "levels_2.png", false},
    {31, "option_1.png", false},
    {32, "option_2.png", false},
    {33, "profil_1.png", false},
    {34, "profil_2.png", false},
    {35, "gulim1.png", false},
    {36, "mm_cent1.png", false},
    {37, "gamename.png", false},
};

}  // namespace host
