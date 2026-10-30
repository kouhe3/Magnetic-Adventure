#pragma once

#include <windows.h>

// 见 gl_render.cpp 顶部注释；数据文件与 exe 同目录（MENU_TEX / MENU_DRAW 可覆盖）。
bool GlInit(HWND viewer);
void GlResize(int w, int h);
void GlRenderMenu();
