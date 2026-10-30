/* 生成文件，勿手改：python tools/gen_proxy.py
 * 依据：docs/facts.md F175（opengl32 368 导出/序号）、F176（透明性待证） */
#include <windows.h>
#include <stdint.h>

extern FARPROC g_slot[];
void __cdecl log_call(unsigned id, uint32_t esp0, uint32_t edx, uint32_t ecx);
void __cdecl save_ret(unsigned id, uint32_t orig_ret);
uint32_t __cdecl finish_call(unsigned id, uint32_t retval, uint32_t args_ptr);
uint32_t __cdecl get_ret(void);

const int g_n_exports = 369;
const char* const g_names[] = {
    "",  /* 0 号占位 */
    "GlmfBeginGlsBlock",
    "GlmfCloseMetaFile",
    "GlmfEndGlsBlock",
    "GlmfEndPlayback",
    "GlmfInitPlayback",
    "GlmfPlayGlsRecord",
    "glAccum",
    "glAlphaFunc",
    "glAreTexturesResident",
    "glArrayElement",
    "glBegin",
    "glBindTexture",
    "glBitmap",
    "glBlendFunc",
    "glCallList",
    "glCallLists",
    "glClear",
    "glClearAccum",
    "glClearColor",
    "glClearDepth",
    "glClearIndex",
    "glClearStencil",
    "glClipPlane",
    "glColor3b",
    "glColor3bv",
    "glColor3d",
    "glColor3dv",
    "glColor3f",
    "glColor3fv",
    "glColor3i",
    "glColor3iv",
    "glColor3s",
    "glColor3sv",
    "glColor3ub",
    "glColor3ubv",
    "glColor3ui",
    "glColor3uiv",
    "glColor3us",
    "glColor3usv",
    "glColor4b",
    "glColor4bv",
    "glColor4d",
    "glColor4dv",
    "glColor4f",
    "glColor4fv",
    "glColor4i",
    "glColor4iv",
    "glColor4s",
    "glColor4sv",
    "glColor4ub",
    "glColor4ubv",
    "glColor4ui",
    "glColor4uiv",
    "glColor4us",
    "glColor4usv",
    "glColorMask",
    "glColorMaterial",
    "glColorPointer",
    "glCopyPixels",
    "glCopyTexImage1D",
    "glCopyTexImage2D",
    "glCopyTexSubImage1D",
    "glCopyTexSubImage2D",
    "glCullFace",
    "glDebugEntry",
    "glDeleteLists",
    "glDeleteTextures",
    "glDepthFunc",
    "glDepthMask",
    "glDepthRange",
    "glDisable",
    "glDisableClientState",
    "glDrawArrays",
    "glDrawBuffer",
    "glDrawElements",
    "glDrawPixels",
    "glEdgeFlag",
    "glEdgeFlagPointer",
    "glEdgeFlagv",
    "glEnable",
    "glEnableClientState",
    "glEnd",
    "glEndList",
    "glEvalCoord1d",
    "glEvalCoord1dv",
    "glEvalCoord1f",
    "glEvalCoord1fv",
    "glEvalCoord2d",
    "glEvalCoord2dv",
    "glEvalCoord2f",
    "glEvalCoord2fv",
    "glEvalMesh1",
    "glEvalMesh2",
    "glEvalPoint1",
    "glEvalPoint2",
    "glFeedbackBuffer",
    "glFinish",
    "glFlush",
    "glFogf",
    "glFogfv",
    "glFogi",
    "glFogiv",
    "glFrontFace",
    "glFrustum",
    "glGenLists",
    "glGenTextures",
    "glGetBooleanv",
    "glGetClipPlane",
    "glGetDoublev",
    "glGetError",
    "glGetFloatv",
    "glGetIntegerv",
    "glGetLightfv",
    "glGetLightiv",
    "glGetMapdv",
    "glGetMapfv",
    "glGetMapiv",
    "glGetMaterialfv",
    "glGetMaterialiv",
    "glGetPixelMapfv",
    "glGetPixelMapuiv",
    "glGetPixelMapusv",
    "glGetPointerv",
    "glGetPolygonStipple",
    "glGetString",
    "glGetTexEnvfv",
    "glGetTexEnviv",
    "glGetTexGendv",
    "glGetTexGenfv",
    "glGetTexGeniv",
    "glGetTexImage",
    "glGetTexLevelParameterfv",
    "glGetTexLevelParameteriv",
    "glGetTexParameterfv",
    "glGetTexParameteriv",
    "glHint",
    "glIndexMask",
    "glIndexPointer",
    "glIndexd",
    "glIndexdv",
    "glIndexf",
    "glIndexfv",
    "glIndexi",
    "glIndexiv",
    "glIndexs",
    "glIndexsv",
    "glIndexub",
    "glIndexubv",
    "glInitNames",
    "glInterleavedArrays",
    "glIsEnabled",
    "glIsList",
    "glIsTexture",
    "glLightModelf",
    "glLightModelfv",
    "glLightModeli",
    "glLightModeliv",
    "glLightf",
    "glLightfv",
    "glLighti",
    "glLightiv",
    "glLineStipple",
    "glLineWidth",
    "glListBase",
    "glLoadIdentity",
    "glLoadMatrixd",
    "glLoadMatrixf",
    "glLoadName",
    "glLogicOp",
    "glMap1d",
    "glMap1f",
    "glMap2d",
    "glMap2f",
    "glMapGrid1d",
    "glMapGrid1f",
    "glMapGrid2d",
    "glMapGrid2f",
    "glMaterialf",
    "glMaterialfv",
    "glMateriali",
    "glMaterialiv",
    "glMatrixMode",
    "glMultMatrixd",
    "glMultMatrixf",
    "glNewList",
    "glNormal3b",
    "glNormal3bv",
    "glNormal3d",
    "glNormal3dv",
    "glNormal3f",
    "glNormal3fv",
    "glNormal3i",
    "glNormal3iv",
    "glNormal3s",
    "glNormal3sv",
    "glNormalPointer",
    "glOrtho",
    "glPassThrough",
    "glPixelMapfv",
    "glPixelMapuiv",
    "glPixelMapusv",
    "glPixelStoref",
    "glPixelStorei",
    "glPixelTransferf",
    "glPixelTransferi",
    "glPixelZoom",
    "glPointSize",
    "glPolygonMode",
    "glPolygonOffset",
    "glPolygonStipple",
    "glPopAttrib",
    "glPopClientAttrib",
    "glPopMatrix",
    "glPopName",
    "glPrioritizeTextures",
    "glPushAttrib",
    "glPushClientAttrib",
    "glPushMatrix",
    "glPushName",
    "glRasterPos2d",
    "glRasterPos2dv",
    "glRasterPos2f",
    "glRasterPos2fv",
    "glRasterPos2i",
    "glRasterPos2iv",
    "glRasterPos2s",
    "glRasterPos2sv",
    "glRasterPos3d",
    "glRasterPos3dv",
    "glRasterPos3f",
    "glRasterPos3fv",
    "glRasterPos3i",
    "glRasterPos3iv",
    "glRasterPos3s",
    "glRasterPos3sv",
    "glRasterPos4d",
    "glRasterPos4dv",
    "glRasterPos4f",
    "glRasterPos4fv",
    "glRasterPos4i",
    "glRasterPos4iv",
    "glRasterPos4s",
    "glRasterPos4sv",
    "glReadBuffer",
    "glReadPixels",
    "glRectd",
    "glRectdv",
    "glRectf",
    "glRectfv",
    "glRecti",
    "glRectiv",
    "glRects",
    "glRectsv",
    "glRenderMode",
    "glRotated",
    "glRotatef",
    "glScaled",
    "glScalef",
    "glScissor",
    "glSelectBuffer",
    "glShadeModel",
    "glStencilFunc",
    "glStencilMask",
    "glStencilOp",
    "glTexCoord1d",
    "glTexCoord1dv",
    "glTexCoord1f",
    "glTexCoord1fv",
    "glTexCoord1i",
    "glTexCoord1iv",
    "glTexCoord1s",
    "glTexCoord1sv",
    "glTexCoord2d",
    "glTexCoord2dv",
    "glTexCoord2f",
    "glTexCoord2fv",
    "glTexCoord2i",
    "glTexCoord2iv",
    "glTexCoord2s",
    "glTexCoord2sv",
    "glTexCoord3d",
    "glTexCoord3dv",
    "glTexCoord3f",
    "glTexCoord3fv",
    "glTexCoord3i",
    "glTexCoord3iv",
    "glTexCoord3s",
    "glTexCoord3sv",
    "glTexCoord4d",
    "glTexCoord4dv",
    "glTexCoord4f",
    "glTexCoord4fv",
    "glTexCoord4i",
    "glTexCoord4iv",
    "glTexCoord4s",
    "glTexCoord4sv",
    "glTexCoordPointer",
    "glTexEnvf",
    "glTexEnvfv",
    "glTexEnvi",
    "glTexEnviv",
    "glTexGend",
    "glTexGendv",
    "glTexGenf",
    "glTexGenfv",
    "glTexGeni",
    "glTexGeniv",
    "glTexImage1D",
    "glTexImage2D",
    "glTexParameterf",
    "glTexParameterfv",
    "glTexParameteri",
    "glTexParameteriv",
    "glTexSubImage1D",
    "glTexSubImage2D",
    "glTranslated",
    "glTranslatef",
    "glVertex2d",
    "glVertex2dv",
    "glVertex2f",
    "glVertex2fv",
    "glVertex2i",
    "glVertex2iv",
    "glVertex2s",
    "glVertex2sv",
    "glVertex3d",
    "glVertex3dv",
    "glVertex3f",
    "glVertex3fv",
    "glVertex3i",
    "glVertex3iv",
    "glVertex3s",
    "glVertex3sv",
    "glVertex4d",
    "glVertex4dv",
    "glVertex4f",
    "glVertex4fv",
    "glVertex4i",
    "glVertex4iv",
    "glVertex4s",
    "glVertex4sv",
    "glVertexPointer",
    "glViewport",
    "wglChoosePixelFormat",
    "wglCopyContext",
    "wglCreateContext",
    "wglCreateLayerContext",
    "wglDeleteContext",
    "wglDescribeLayerPlane",
    "wglDescribePixelFormat",
    "wglGetCurrentContext",
    "wglGetCurrentDC",
    "wglGetDefaultProcAddress",
    "wglGetLayerPaletteEntries",
    "wglGetPixelFormat",
    "wglGetProcAddress",
    "wglMakeCurrent",
    "wglRealizeLayerPalette",
    "wglSetLayerPaletteEntries",
    "wglSetPixelFormat",
    "wglShareLists",
    "wglSwapBuffers",
    "wglSwapLayerBuffers",
    "wglSwapMultipleBuffers",
    "wglUseFontBitmapsA",
    "wglUseFontBitmapsW",
    "wglUseFontOutlinesA",
    "wglUseFontOutlinesW",
    0,
};

FARPROC g_slot[370] = {0};

__declspec(naked) void proxy_post_1(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 1
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_2(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 2
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_3(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 3
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_4(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 4
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_5(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 5
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_6(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 6
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_7(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 7
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_8(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 8
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_9(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 9
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_10(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 10
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_11(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 11
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_12(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 12
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_13(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 13
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_14(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 14
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_15(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 15
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_16(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 16
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_17(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 17
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_18(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 18
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_19(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 19
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_20(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 20
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_21(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 21
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_22(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 22
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_23(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 23
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_24(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 24
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_25(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 25
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_26(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 26
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_27(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 27
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_28(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 28
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_29(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 29
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_30(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 30
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_31(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 31
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_32(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 32
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_33(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 33
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_34(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 34
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_35(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 35
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_36(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 36
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_37(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 37
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_38(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 38
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_39(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 39
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_40(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 40
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_41(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 41
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_42(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 42
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_43(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 43
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_44(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 44
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_45(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 45
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_46(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 46
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_47(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 47
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_48(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 48
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_49(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 49
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_50(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 50
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_51(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 51
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_52(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 52
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_53(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 53
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_54(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 54
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_55(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 55
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_56(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 56
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_57(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 57
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_58(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 58
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_59(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 59
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_60(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 60
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_61(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 61
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_62(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 62
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_63(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 63
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_64(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 64
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_65(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 65
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_66(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 66
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_67(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 67
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_68(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 68
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_69(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 69
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_70(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 70
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_71(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 71
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_72(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 72
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_73(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 73
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_74(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 74
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_75(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 75
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_76(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 76
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_77(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 77
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_78(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 78
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_79(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 79
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_80(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 80
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_81(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 81
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_82(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 82
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_83(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 83
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_84(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 84
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_85(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 85
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_86(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 86
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_87(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 87
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_88(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 88
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_89(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 89
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_90(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 90
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_91(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 91
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_92(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 92
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_93(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 93
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_94(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 94
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_95(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 95
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_96(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 96
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_97(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 97
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_98(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 98
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_99(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 99
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_100(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 100
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_101(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 101
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_102(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 102
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_103(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 103
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_104(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 104
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_105(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 105
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_106(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 106
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_107(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 107
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_108(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 108
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_109(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 109
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_110(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 110
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_111(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 111
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_112(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 112
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_113(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 113
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_114(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 114
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_115(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 115
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_116(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 116
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_117(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 117
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_118(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 118
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_119(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 119
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_120(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 120
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_121(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 121
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_122(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 122
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_123(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 123
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_124(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 124
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_125(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 125
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_126(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 126
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_127(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 127
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_128(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 128
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_129(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 129
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_130(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 130
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_131(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 131
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_132(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 132
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_133(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 133
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_134(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 134
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_135(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 135
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_136(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 136
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_137(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 137
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_138(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 138
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_139(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 139
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_140(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 140
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_141(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 141
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_142(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 142
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_143(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 143
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_144(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 144
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_145(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 145
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_146(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 146
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_147(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 147
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_148(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 148
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_149(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 149
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_150(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 150
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_151(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 151
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_152(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 152
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_153(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 153
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_154(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 154
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_155(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 155
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_156(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 156
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_157(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 157
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_158(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 158
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_159(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 159
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_160(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 160
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_161(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 161
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_162(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 162
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_163(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 163
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_164(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 164
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_165(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 165
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_166(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 166
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_167(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 167
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_168(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 168
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_169(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 169
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_170(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 170
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_171(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 171
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_172(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 172
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_173(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 173
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_174(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 174
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_175(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 175
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_176(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 176
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_177(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 177
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_178(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 178
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_179(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 179
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_180(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 180
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_181(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 181
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_182(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 182
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_183(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 183
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_184(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 184
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_185(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 185
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_186(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 186
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_187(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 187
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_188(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 188
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_189(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 189
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_190(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 190
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_191(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 191
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_192(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 192
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_193(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 193
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_194(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 194
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_195(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 195
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_196(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 196
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_197(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 197
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_198(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 198
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_199(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 199
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_200(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 200
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_201(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 201
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_202(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 202
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_203(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 203
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_204(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 204
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_205(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 205
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_206(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 206
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_207(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 207
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_208(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 208
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_209(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 209
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_210(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 210
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_211(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 211
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_212(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 212
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_213(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 213
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_214(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 214
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_215(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 215
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_216(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 216
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_217(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 217
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_218(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 218
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_219(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 219
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_220(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 220
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_221(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 221
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_222(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 222
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_223(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 223
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_224(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 224
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_225(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 225
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_226(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 226
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_227(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 227
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_228(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 228
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_229(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 229
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_230(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 230
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_231(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 231
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_232(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 232
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_233(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 233
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_234(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 234
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_235(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 235
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_236(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 236
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_237(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 237
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_238(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 238
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_239(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 239
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_240(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 240
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_241(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 241
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_242(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 242
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_243(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 243
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_244(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 244
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_245(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 245
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_246(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 246
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_247(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 247
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_248(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 248
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_249(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 249
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_250(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 250
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_251(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 251
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_252(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 252
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_253(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 253
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_254(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 254
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_255(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 255
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_256(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 256
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_257(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 257
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_258(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 258
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_259(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 259
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_260(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 260
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_261(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 261
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_262(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 262
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_263(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 263
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_264(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 264
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_265(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 265
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_266(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 266
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_267(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 267
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_268(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 268
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_269(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 269
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_270(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 270
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_271(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 271
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_272(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 272
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_273(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 273
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_274(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 274
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_275(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 275
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_276(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 276
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_277(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 277
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_278(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 278
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_279(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 279
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_280(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 280
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_281(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 281
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_282(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 282
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_283(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 283
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_284(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 284
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_285(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 285
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_286(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 286
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_287(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 287
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_288(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 288
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_289(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 289
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_290(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 290
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_291(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 291
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_292(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 292
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_293(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 293
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_294(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 294
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_295(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 295
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_296(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 296
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_297(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 297
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_298(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 298
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_299(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 299
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_300(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 300
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_301(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 301
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_302(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 302
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_303(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 303
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_304(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 304
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_305(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 305
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_306(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 306
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_307(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 307
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_308(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 308
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_309(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 309
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_310(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 310
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_311(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 311
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_312(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 312
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_313(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 313
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_314(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 314
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_315(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 315
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_316(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 316
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_317(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 317
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_318(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 318
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_319(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 319
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_320(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 320
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_321(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 321
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_322(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 322
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_323(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 323
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_324(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 324
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_325(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 325
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_326(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 326
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_327(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 327
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_328(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 328
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_329(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 329
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_330(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 330
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_331(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 331
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_332(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 332
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_333(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 333
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_334(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 334
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_335(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 335
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_336(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 336
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_337(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 337
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_338(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 338
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_339(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 339
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_340(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 340
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_341(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 341
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_342(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 342
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_343(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 343
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_344(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 344
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_345(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 345
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_346(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 346
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_347(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 347
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_348(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 348
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_349(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 349
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_350(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 350
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_351(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 351
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_352(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 352
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_353(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 353
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_354(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 354
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_355(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 355
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_356(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 356
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_357(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 357
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_358(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 358
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_359(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 359
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_360(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 360
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_361(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 361
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_362(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 362
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_363(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 363
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_364(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 364
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_365(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 365
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_366(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 366
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_367(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 367
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_post_368(void) {
    /* 真实函数返回到这里：eax=返回值，esp 指向第一个实参 */
    __asm {
        lea  edx, [esp]
        push edx                        /* args_ptr */
        push eax                        /* retval */
        push 368
        call finish_call                /* -> eax = 原返回地址 */
        add  esp, 12
        push eax                        /* 暂存原返回地址（esp 之下，安全） */
        call get_ret                    /* -> eax = 返回值 */
        pop  edx
        jmp  edx                        /* 回到宿主：esp 仍指向第一个实参 */
    }
}

__declspec(naked) void proxy_stub_1(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 1
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 1
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_1
        jmp  dword ptr [g_slot+4]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_2(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 2
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 2
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_2
        jmp  dword ptr [g_slot+8]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_3(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 3
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 3
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_3
        jmp  dword ptr [g_slot+12]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_4(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 4
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 4
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_4
        jmp  dword ptr [g_slot+16]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_5(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 5
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 5
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_5
        jmp  dword ptr [g_slot+20]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_6(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 6
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 6
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_6
        jmp  dword ptr [g_slot+24]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_7(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 7
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 7
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_7
        jmp  dword ptr [g_slot+28]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_8(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 8
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 8
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_8
        jmp  dword ptr [g_slot+32]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_9(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 9
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 9
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_9
        jmp  dword ptr [g_slot+36]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_10(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 10
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 10
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_10
        jmp  dword ptr [g_slot+40]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_11(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 11
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 11
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_11
        jmp  dword ptr [g_slot+44]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_12(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 12
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 12
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_12
        jmp  dword ptr [g_slot+48]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_13(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 13
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 13
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_13
        jmp  dword ptr [g_slot+52]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_14(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 14
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 14
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_14
        jmp  dword ptr [g_slot+56]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_15(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 15
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 15
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_15
        jmp  dword ptr [g_slot+60]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_16(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 16
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 16
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_16
        jmp  dword ptr [g_slot+64]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_17(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 17
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 17
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_17
        jmp  dword ptr [g_slot+68]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_18(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 18
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 18
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_18
        jmp  dword ptr [g_slot+72]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_19(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 19
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 19
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_19
        jmp  dword ptr [g_slot+76]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_20(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 20
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 20
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_20
        jmp  dword ptr [g_slot+80]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_21(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 21
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 21
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_21
        jmp  dword ptr [g_slot+84]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_22(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 22
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 22
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_22
        jmp  dword ptr [g_slot+88]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_23(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 23
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 23
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_23
        jmp  dword ptr [g_slot+92]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_24(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 24
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 24
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_24
        jmp  dword ptr [g_slot+96]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_25(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 25
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 25
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_25
        jmp  dword ptr [g_slot+100]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_26(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 26
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 26
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_26
        jmp  dword ptr [g_slot+104]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_27(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 27
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 27
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_27
        jmp  dword ptr [g_slot+108]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_28(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 28
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 28
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_28
        jmp  dword ptr [g_slot+112]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_29(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 29
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 29
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_29
        jmp  dword ptr [g_slot+116]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_30(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 30
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 30
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_30
        jmp  dword ptr [g_slot+120]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_31(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 31
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 31
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_31
        jmp  dword ptr [g_slot+124]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_32(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 32
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 32
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_32
        jmp  dword ptr [g_slot+128]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_33(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 33
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 33
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_33
        jmp  dword ptr [g_slot+132]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_34(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 34
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 34
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_34
        jmp  dword ptr [g_slot+136]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_35(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 35
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 35
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_35
        jmp  dword ptr [g_slot+140]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_36(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 36
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 36
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_36
        jmp  dword ptr [g_slot+144]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_37(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 37
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 37
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_37
        jmp  dword ptr [g_slot+148]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_38(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 38
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 38
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_38
        jmp  dword ptr [g_slot+152]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_39(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 39
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 39
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_39
        jmp  dword ptr [g_slot+156]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_40(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 40
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 40
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_40
        jmp  dword ptr [g_slot+160]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_41(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 41
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 41
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_41
        jmp  dword ptr [g_slot+164]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_42(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 42
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 42
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_42
        jmp  dword ptr [g_slot+168]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_43(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 43
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 43
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_43
        jmp  dword ptr [g_slot+172]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_44(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 44
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 44
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_44
        jmp  dword ptr [g_slot+176]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_45(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 45
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 45
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_45
        jmp  dword ptr [g_slot+180]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_46(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 46
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 46
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_46
        jmp  dword ptr [g_slot+184]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_47(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 47
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 47
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_47
        jmp  dword ptr [g_slot+188]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_48(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 48
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 48
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_48
        jmp  dword ptr [g_slot+192]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_49(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 49
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 49
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_49
        jmp  dword ptr [g_slot+196]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_50(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 50
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 50
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_50
        jmp  dword ptr [g_slot+200]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_51(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 51
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 51
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_51
        jmp  dword ptr [g_slot+204]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_52(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 52
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 52
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_52
        jmp  dword ptr [g_slot+208]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_53(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 53
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 53
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_53
        jmp  dword ptr [g_slot+212]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_54(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 54
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 54
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_54
        jmp  dword ptr [g_slot+216]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_55(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 55
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 55
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_55
        jmp  dword ptr [g_slot+220]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_56(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 56
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 56
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_56
        jmp  dword ptr [g_slot+224]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_57(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 57
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 57
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_57
        jmp  dword ptr [g_slot+228]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_58(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 58
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 58
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_58
        jmp  dword ptr [g_slot+232]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_59(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 59
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 59
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_59
        jmp  dword ptr [g_slot+236]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_60(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 60
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 60
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_60
        jmp  dword ptr [g_slot+240]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_61(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 61
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 61
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_61
        jmp  dword ptr [g_slot+244]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_62(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 62
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 62
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_62
        jmp  dword ptr [g_slot+248]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_63(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 63
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 63
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_63
        jmp  dword ptr [g_slot+252]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_64(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 64
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 64
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_64
        jmp  dword ptr [g_slot+256]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_65(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 65
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 65
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_65
        jmp  dword ptr [g_slot+260]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_66(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 66
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 66
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_66
        jmp  dword ptr [g_slot+264]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_67(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 67
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 67
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_67
        jmp  dword ptr [g_slot+268]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_68(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 68
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 68
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_68
        jmp  dword ptr [g_slot+272]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_69(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 69
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 69
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_69
        jmp  dword ptr [g_slot+276]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_70(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 70
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 70
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_70
        jmp  dword ptr [g_slot+280]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_71(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 71
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 71
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_71
        jmp  dword ptr [g_slot+284]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_72(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 72
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 72
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_72
        jmp  dword ptr [g_slot+288]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_73(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 73
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 73
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_73
        jmp  dword ptr [g_slot+292]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_74(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 74
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 74
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_74
        jmp  dword ptr [g_slot+296]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_75(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 75
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 75
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_75
        jmp  dword ptr [g_slot+300]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_76(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 76
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 76
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_76
        jmp  dword ptr [g_slot+304]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_77(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 77
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 77
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_77
        jmp  dword ptr [g_slot+308]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_78(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 78
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 78
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_78
        jmp  dword ptr [g_slot+312]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_79(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 79
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 79
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_79
        jmp  dword ptr [g_slot+316]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_80(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 80
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 80
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_80
        jmp  dword ptr [g_slot+320]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_81(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 81
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 81
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_81
        jmp  dword ptr [g_slot+324]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_82(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 82
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 82
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_82
        jmp  dword ptr [g_slot+328]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_83(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 83
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 83
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_83
        jmp  dword ptr [g_slot+332]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_84(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 84
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 84
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_84
        jmp  dword ptr [g_slot+336]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_85(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 85
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 85
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_85
        jmp  dword ptr [g_slot+340]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_86(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 86
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 86
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_86
        jmp  dword ptr [g_slot+344]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_87(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 87
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 87
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_87
        jmp  dword ptr [g_slot+348]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_88(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 88
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 88
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_88
        jmp  dword ptr [g_slot+352]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_89(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 89
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 89
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_89
        jmp  dword ptr [g_slot+356]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_90(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 90
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 90
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_90
        jmp  dword ptr [g_slot+360]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_91(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 91
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 91
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_91
        jmp  dword ptr [g_slot+364]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_92(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 92
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 92
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_92
        jmp  dword ptr [g_slot+368]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_93(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 93
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 93
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_93
        jmp  dword ptr [g_slot+372]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_94(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 94
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 94
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_94
        jmp  dword ptr [g_slot+376]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_95(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 95
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 95
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_95
        jmp  dword ptr [g_slot+380]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_96(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 96
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 96
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_96
        jmp  dword ptr [g_slot+384]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_97(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 97
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 97
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_97
        jmp  dword ptr [g_slot+388]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_98(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 98
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 98
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_98
        jmp  dword ptr [g_slot+392]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_99(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 99
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 99
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_99
        jmp  dword ptr [g_slot+396]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_100(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 100
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 100
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_100
        jmp  dword ptr [g_slot+400]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_101(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 101
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 101
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_101
        jmp  dword ptr [g_slot+404]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_102(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 102
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 102
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_102
        jmp  dword ptr [g_slot+408]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_103(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 103
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 103
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_103
        jmp  dword ptr [g_slot+412]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_104(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 104
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 104
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_104
        jmp  dword ptr [g_slot+416]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_105(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 105
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 105
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_105
        jmp  dword ptr [g_slot+420]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_106(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 106
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 106
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_106
        jmp  dword ptr [g_slot+424]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_107(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 107
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 107
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_107
        jmp  dword ptr [g_slot+428]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_108(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 108
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 108
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_108
        jmp  dword ptr [g_slot+432]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_109(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 109
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 109
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_109
        jmp  dword ptr [g_slot+436]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_110(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 110
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 110
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_110
        jmp  dword ptr [g_slot+440]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_111(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 111
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 111
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_111
        jmp  dword ptr [g_slot+444]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_112(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 112
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 112
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_112
        jmp  dword ptr [g_slot+448]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_113(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 113
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 113
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_113
        jmp  dword ptr [g_slot+452]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_114(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 114
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 114
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_114
        jmp  dword ptr [g_slot+456]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_115(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 115
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 115
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_115
        jmp  dword ptr [g_slot+460]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_116(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 116
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 116
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_116
        jmp  dword ptr [g_slot+464]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_117(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 117
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 117
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_117
        jmp  dword ptr [g_slot+468]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_118(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 118
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 118
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_118
        jmp  dword ptr [g_slot+472]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_119(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 119
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 119
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_119
        jmp  dword ptr [g_slot+476]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_120(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 120
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 120
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_120
        jmp  dword ptr [g_slot+480]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_121(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 121
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 121
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_121
        jmp  dword ptr [g_slot+484]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_122(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 122
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 122
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_122
        jmp  dword ptr [g_slot+488]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_123(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 123
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 123
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_123
        jmp  dword ptr [g_slot+492]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_124(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 124
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 124
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_124
        jmp  dword ptr [g_slot+496]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_125(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 125
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 125
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_125
        jmp  dword ptr [g_slot+500]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_126(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 126
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 126
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_126
        jmp  dword ptr [g_slot+504]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_127(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 127
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 127
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_127
        jmp  dword ptr [g_slot+508]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_128(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 128
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 128
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_128
        jmp  dword ptr [g_slot+512]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_129(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 129
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 129
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_129
        jmp  dword ptr [g_slot+516]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_130(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 130
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 130
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_130
        jmp  dword ptr [g_slot+520]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_131(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 131
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 131
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_131
        jmp  dword ptr [g_slot+524]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_132(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 132
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 132
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_132
        jmp  dword ptr [g_slot+528]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_133(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 133
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 133
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_133
        jmp  dword ptr [g_slot+532]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_134(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 134
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 134
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_134
        jmp  dword ptr [g_slot+536]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_135(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 135
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 135
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_135
        jmp  dword ptr [g_slot+540]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_136(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 136
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 136
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_136
        jmp  dword ptr [g_slot+544]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_137(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 137
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 137
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_137
        jmp  dword ptr [g_slot+548]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_138(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 138
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 138
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_138
        jmp  dword ptr [g_slot+552]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_139(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 139
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 139
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_139
        jmp  dword ptr [g_slot+556]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_140(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 140
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 140
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_140
        jmp  dword ptr [g_slot+560]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_141(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 141
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 141
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_141
        jmp  dword ptr [g_slot+564]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_142(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 142
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 142
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_142
        jmp  dword ptr [g_slot+568]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_143(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 143
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 143
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_143
        jmp  dword ptr [g_slot+572]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_144(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 144
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 144
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_144
        jmp  dword ptr [g_slot+576]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_145(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 145
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 145
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_145
        jmp  dword ptr [g_slot+580]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_146(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 146
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 146
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_146
        jmp  dword ptr [g_slot+584]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_147(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 147
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 147
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_147
        jmp  dword ptr [g_slot+588]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_148(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 148
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 148
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_148
        jmp  dword ptr [g_slot+592]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_149(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 149
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 149
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_149
        jmp  dword ptr [g_slot+596]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_150(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 150
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 150
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_150
        jmp  dword ptr [g_slot+600]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_151(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 151
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 151
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_151
        jmp  dword ptr [g_slot+604]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_152(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 152
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 152
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_152
        jmp  dword ptr [g_slot+608]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_153(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 153
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 153
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_153
        jmp  dword ptr [g_slot+612]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_154(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 154
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 154
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_154
        jmp  dword ptr [g_slot+616]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_155(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 155
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 155
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_155
        jmp  dword ptr [g_slot+620]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_156(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 156
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 156
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_156
        jmp  dword ptr [g_slot+624]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_157(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 157
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 157
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_157
        jmp  dword ptr [g_slot+628]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_158(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 158
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 158
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_158
        jmp  dword ptr [g_slot+632]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_159(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 159
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 159
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_159
        jmp  dword ptr [g_slot+636]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_160(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 160
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 160
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_160
        jmp  dword ptr [g_slot+640]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_161(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 161
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 161
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_161
        jmp  dword ptr [g_slot+644]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_162(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 162
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 162
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_162
        jmp  dword ptr [g_slot+648]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_163(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 163
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 163
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_163
        jmp  dword ptr [g_slot+652]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_164(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 164
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 164
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_164
        jmp  dword ptr [g_slot+656]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_165(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 165
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 165
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_165
        jmp  dword ptr [g_slot+660]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_166(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 166
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 166
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_166
        jmp  dword ptr [g_slot+664]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_167(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 167
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 167
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_167
        jmp  dword ptr [g_slot+668]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_168(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 168
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 168
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_168
        jmp  dword ptr [g_slot+672]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_169(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 169
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 169
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_169
        jmp  dword ptr [g_slot+676]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_170(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 170
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 170
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_170
        jmp  dword ptr [g_slot+680]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_171(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 171
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 171
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_171
        jmp  dword ptr [g_slot+684]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_172(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 172
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 172
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_172
        jmp  dword ptr [g_slot+688]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_173(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 173
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 173
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_173
        jmp  dword ptr [g_slot+692]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_174(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 174
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 174
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_174
        jmp  dword ptr [g_slot+696]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_175(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 175
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 175
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_175
        jmp  dword ptr [g_slot+700]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_176(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 176
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 176
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_176
        jmp  dword ptr [g_slot+704]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_177(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 177
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 177
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_177
        jmp  dword ptr [g_slot+708]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_178(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 178
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 178
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_178
        jmp  dword ptr [g_slot+712]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_179(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 179
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 179
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_179
        jmp  dword ptr [g_slot+716]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_180(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 180
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 180
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_180
        jmp  dword ptr [g_slot+720]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_181(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 181
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 181
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_181
        jmp  dword ptr [g_slot+724]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_182(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 182
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 182
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_182
        jmp  dword ptr [g_slot+728]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_183(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 183
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 183
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_183
        jmp  dword ptr [g_slot+732]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_184(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 184
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 184
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_184
        jmp  dword ptr [g_slot+736]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_185(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 185
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 185
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_185
        jmp  dword ptr [g_slot+740]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_186(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 186
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 186
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_186
        jmp  dword ptr [g_slot+744]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_187(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 187
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 187
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_187
        jmp  dword ptr [g_slot+748]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_188(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 188
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 188
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_188
        jmp  dword ptr [g_slot+752]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_189(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 189
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 189
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_189
        jmp  dword ptr [g_slot+756]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_190(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 190
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 190
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_190
        jmp  dword ptr [g_slot+760]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_191(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 191
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 191
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_191
        jmp  dword ptr [g_slot+764]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_192(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 192
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 192
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_192
        jmp  dword ptr [g_slot+768]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_193(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 193
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 193
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_193
        jmp  dword ptr [g_slot+772]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_194(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 194
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 194
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_194
        jmp  dword ptr [g_slot+776]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_195(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 195
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 195
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_195
        jmp  dword ptr [g_slot+780]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_196(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 196
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 196
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_196
        jmp  dword ptr [g_slot+784]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_197(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 197
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 197
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_197
        jmp  dword ptr [g_slot+788]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_198(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 198
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 198
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_198
        jmp  dword ptr [g_slot+792]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_199(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 199
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 199
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_199
        jmp  dword ptr [g_slot+796]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_200(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 200
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 200
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_200
        jmp  dword ptr [g_slot+800]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_201(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 201
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 201
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_201
        jmp  dword ptr [g_slot+804]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_202(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 202
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 202
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_202
        jmp  dword ptr [g_slot+808]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_203(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 203
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 203
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_203
        jmp  dword ptr [g_slot+812]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_204(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 204
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 204
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_204
        jmp  dword ptr [g_slot+816]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_205(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 205
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 205
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_205
        jmp  dword ptr [g_slot+820]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_206(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 206
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 206
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_206
        jmp  dword ptr [g_slot+824]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_207(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 207
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 207
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_207
        jmp  dword ptr [g_slot+828]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_208(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 208
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 208
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_208
        jmp  dword ptr [g_slot+832]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_209(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 209
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 209
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_209
        jmp  dword ptr [g_slot+836]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_210(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 210
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 210
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_210
        jmp  dword ptr [g_slot+840]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_211(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 211
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 211
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_211
        jmp  dword ptr [g_slot+844]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_212(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 212
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 212
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_212
        jmp  dword ptr [g_slot+848]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_213(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 213
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 213
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_213
        jmp  dword ptr [g_slot+852]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_214(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 214
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 214
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_214
        jmp  dword ptr [g_slot+856]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_215(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 215
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 215
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_215
        jmp  dword ptr [g_slot+860]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_216(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 216
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 216
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_216
        jmp  dword ptr [g_slot+864]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_217(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 217
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 217
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_217
        jmp  dword ptr [g_slot+868]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_218(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 218
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 218
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_218
        jmp  dword ptr [g_slot+872]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_219(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 219
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 219
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_219
        jmp  dword ptr [g_slot+876]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_220(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 220
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 220
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_220
        jmp  dword ptr [g_slot+880]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_221(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 221
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 221
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_221
        jmp  dword ptr [g_slot+884]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_222(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 222
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 222
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_222
        jmp  dword ptr [g_slot+888]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_223(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 223
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 223
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_223
        jmp  dword ptr [g_slot+892]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_224(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 224
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 224
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_224
        jmp  dword ptr [g_slot+896]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_225(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 225
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 225
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_225
        jmp  dword ptr [g_slot+900]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_226(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 226
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 226
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_226
        jmp  dword ptr [g_slot+904]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_227(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 227
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 227
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_227
        jmp  dword ptr [g_slot+908]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_228(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 228
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 228
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_228
        jmp  dword ptr [g_slot+912]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_229(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 229
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 229
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_229
        jmp  dword ptr [g_slot+916]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_230(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 230
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 230
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_230
        jmp  dword ptr [g_slot+920]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_231(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 231
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 231
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_231
        jmp  dword ptr [g_slot+924]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_232(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 232
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 232
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_232
        jmp  dword ptr [g_slot+928]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_233(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 233
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 233
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_233
        jmp  dword ptr [g_slot+932]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_234(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 234
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 234
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_234
        jmp  dword ptr [g_slot+936]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_235(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 235
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 235
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_235
        jmp  dword ptr [g_slot+940]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_236(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 236
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 236
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_236
        jmp  dword ptr [g_slot+944]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_237(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 237
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 237
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_237
        jmp  dword ptr [g_slot+948]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_238(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 238
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 238
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_238
        jmp  dword ptr [g_slot+952]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_239(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 239
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 239
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_239
        jmp  dword ptr [g_slot+956]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_240(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 240
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 240
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_240
        jmp  dword ptr [g_slot+960]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_241(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 241
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 241
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_241
        jmp  dword ptr [g_slot+964]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_242(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 242
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 242
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_242
        jmp  dword ptr [g_slot+968]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_243(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 243
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 243
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_243
        jmp  dword ptr [g_slot+972]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_244(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 244
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 244
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_244
        jmp  dword ptr [g_slot+976]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_245(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 245
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 245
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_245
        jmp  dword ptr [g_slot+980]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_246(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 246
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 246
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_246
        jmp  dword ptr [g_slot+984]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_247(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 247
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 247
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_247
        jmp  dword ptr [g_slot+988]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_248(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 248
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 248
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_248
        jmp  dword ptr [g_slot+992]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_249(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 249
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 249
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_249
        jmp  dword ptr [g_slot+996]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_250(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 250
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 250
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_250
        jmp  dword ptr [g_slot+1000]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_251(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 251
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 251
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_251
        jmp  dword ptr [g_slot+1004]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_252(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 252
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 252
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_252
        jmp  dword ptr [g_slot+1008]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_253(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 253
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 253
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_253
        jmp  dword ptr [g_slot+1012]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_254(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 254
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 254
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_254
        jmp  dword ptr [g_slot+1016]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_255(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 255
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 255
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_255
        jmp  dword ptr [g_slot+1020]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_256(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 256
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 256
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_256
        jmp  dword ptr [g_slot+1024]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_257(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 257
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 257
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_257
        jmp  dword ptr [g_slot+1028]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_258(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 258
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 258
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_258
        jmp  dword ptr [g_slot+1032]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_259(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 259
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 259
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_259
        jmp  dword ptr [g_slot+1036]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_260(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 260
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 260
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_260
        jmp  dword ptr [g_slot+1040]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_261(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 261
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 261
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_261
        jmp  dword ptr [g_slot+1044]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_262(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 262
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 262
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_262
        jmp  dword ptr [g_slot+1048]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_263(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 263
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 263
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_263
        jmp  dword ptr [g_slot+1052]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_264(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 264
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 264
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_264
        jmp  dword ptr [g_slot+1056]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_265(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 265
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 265
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_265
        jmp  dword ptr [g_slot+1060]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_266(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 266
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 266
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_266
        jmp  dword ptr [g_slot+1064]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_267(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 267
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 267
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_267
        jmp  dword ptr [g_slot+1068]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_268(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 268
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 268
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_268
        jmp  dword ptr [g_slot+1072]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_269(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 269
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 269
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_269
        jmp  dword ptr [g_slot+1076]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_270(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 270
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 270
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_270
        jmp  dword ptr [g_slot+1080]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_271(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 271
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 271
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_271
        jmp  dword ptr [g_slot+1084]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_272(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 272
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 272
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_272
        jmp  dword ptr [g_slot+1088]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_273(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 273
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 273
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_273
        jmp  dword ptr [g_slot+1092]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_274(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 274
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 274
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_274
        jmp  dword ptr [g_slot+1096]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_275(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 275
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 275
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_275
        jmp  dword ptr [g_slot+1100]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_276(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 276
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 276
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_276
        jmp  dword ptr [g_slot+1104]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_277(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 277
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 277
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_277
        jmp  dword ptr [g_slot+1108]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_278(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 278
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 278
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_278
        jmp  dword ptr [g_slot+1112]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_279(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 279
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 279
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_279
        jmp  dword ptr [g_slot+1116]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_280(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 280
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 280
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_280
        jmp  dword ptr [g_slot+1120]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_281(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 281
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 281
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_281
        jmp  dword ptr [g_slot+1124]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_282(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 282
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 282
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_282
        jmp  dword ptr [g_slot+1128]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_283(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 283
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 283
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_283
        jmp  dword ptr [g_slot+1132]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_284(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 284
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 284
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_284
        jmp  dword ptr [g_slot+1136]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_285(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 285
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 285
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_285
        jmp  dword ptr [g_slot+1140]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_286(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 286
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 286
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_286
        jmp  dword ptr [g_slot+1144]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_287(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 287
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 287
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_287
        jmp  dword ptr [g_slot+1148]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_288(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 288
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 288
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_288
        jmp  dword ptr [g_slot+1152]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_289(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 289
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 289
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_289
        jmp  dword ptr [g_slot+1156]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_290(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 290
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 290
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_290
        jmp  dword ptr [g_slot+1160]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_291(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 291
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 291
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_291
        jmp  dword ptr [g_slot+1164]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_292(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 292
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 292
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_292
        jmp  dword ptr [g_slot+1168]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_293(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 293
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 293
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_293
        jmp  dword ptr [g_slot+1172]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_294(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 294
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 294
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_294
        jmp  dword ptr [g_slot+1176]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_295(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 295
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 295
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_295
        jmp  dword ptr [g_slot+1180]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_296(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 296
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 296
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_296
        jmp  dword ptr [g_slot+1184]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_297(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 297
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 297
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_297
        jmp  dword ptr [g_slot+1188]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_298(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 298
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 298
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_298
        jmp  dword ptr [g_slot+1192]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_299(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 299
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 299
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_299
        jmp  dword ptr [g_slot+1196]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_300(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 300
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 300
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_300
        jmp  dword ptr [g_slot+1200]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_301(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 301
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 301
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_301
        jmp  dword ptr [g_slot+1204]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_302(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 302
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 302
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_302
        jmp  dword ptr [g_slot+1208]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_303(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 303
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 303
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_303
        jmp  dword ptr [g_slot+1212]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_304(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 304
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 304
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_304
        jmp  dword ptr [g_slot+1216]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_305(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 305
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 305
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_305
        jmp  dword ptr [g_slot+1220]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_306(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 306
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 306
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_306
        jmp  dword ptr [g_slot+1224]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_307(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 307
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 307
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_307
        jmp  dword ptr [g_slot+1228]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_308(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 308
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 308
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_308
        jmp  dword ptr [g_slot+1232]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_309(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 309
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 309
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_309
        jmp  dword ptr [g_slot+1236]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_310(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 310
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 310
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_310
        jmp  dword ptr [g_slot+1240]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_311(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 311
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 311
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_311
        jmp  dword ptr [g_slot+1244]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_312(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 312
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 312
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_312
        jmp  dword ptr [g_slot+1248]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_313(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 313
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 313
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_313
        jmp  dword ptr [g_slot+1252]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_314(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 314
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 314
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_314
        jmp  dword ptr [g_slot+1256]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_315(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 315
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 315
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_315
        jmp  dword ptr [g_slot+1260]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_316(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 316
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 316
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_316
        jmp  dword ptr [g_slot+1264]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_317(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 317
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 317
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_317
        jmp  dword ptr [g_slot+1268]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_318(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 318
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 318
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_318
        jmp  dword ptr [g_slot+1272]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_319(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 319
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 319
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_319
        jmp  dword ptr [g_slot+1276]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_320(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 320
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 320
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_320
        jmp  dword ptr [g_slot+1280]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_321(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 321
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 321
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_321
        jmp  dword ptr [g_slot+1284]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_322(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 322
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 322
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_322
        jmp  dword ptr [g_slot+1288]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_323(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 323
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 323
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_323
        jmp  dword ptr [g_slot+1292]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_324(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 324
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 324
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_324
        jmp  dword ptr [g_slot+1296]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_325(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 325
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 325
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_325
        jmp  dword ptr [g_slot+1300]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_326(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 326
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 326
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_326
        jmp  dword ptr [g_slot+1304]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_327(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 327
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 327
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_327
        jmp  dword ptr [g_slot+1308]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_328(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 328
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 328
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_328
        jmp  dword ptr [g_slot+1312]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_329(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 329
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 329
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_329
        jmp  dword ptr [g_slot+1316]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_330(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 330
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 330
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_330
        jmp  dword ptr [g_slot+1320]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_331(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 331
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 331
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_331
        jmp  dword ptr [g_slot+1324]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_332(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 332
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 332
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_332
        jmp  dword ptr [g_slot+1328]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_333(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 333
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 333
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_333
        jmp  dword ptr [g_slot+1332]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_334(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 334
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 334
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_334
        jmp  dword ptr [g_slot+1336]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_335(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 335
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 335
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_335
        jmp  dword ptr [g_slot+1340]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_336(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 336
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 336
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_336
        jmp  dword ptr [g_slot+1344]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_337(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 337
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 337
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_337
        jmp  dword ptr [g_slot+1348]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_338(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 338
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 338
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_338
        jmp  dword ptr [g_slot+1352]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_339(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 339
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 339
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_339
        jmp  dword ptr [g_slot+1356]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_340(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 340
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 340
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_340
        jmp  dword ptr [g_slot+1360]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_341(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 341
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 341
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_341
        jmp  dword ptr [g_slot+1364]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_342(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 342
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 342
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_342
        jmp  dword ptr [g_slot+1368]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_343(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 343
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 343
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_343
        jmp  dword ptr [g_slot+1372]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_344(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 344
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 344
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_344
        jmp  dword ptr [g_slot+1376]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_345(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 345
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 345
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_345
        jmp  dword ptr [g_slot+1380]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_346(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 346
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 346
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_346
        jmp  dword ptr [g_slot+1384]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_347(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 347
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 347
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_347
        jmp  dword ptr [g_slot+1388]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_348(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 348
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 348
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_348
        jmp  dword ptr [g_slot+1392]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_349(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 349
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 349
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_349
        jmp  dword ptr [g_slot+1396]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_350(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 350
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 350
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_350
        jmp  dword ptr [g_slot+1400]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_351(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 351
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 351
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_351
        jmp  dword ptr [g_slot+1404]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_352(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 352
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 352
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_352
        jmp  dword ptr [g_slot+1408]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_353(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 353
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 353
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_353
        jmp  dword ptr [g_slot+1412]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_354(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 354
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 354
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_354
        jmp  dword ptr [g_slot+1416]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_355(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 355
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 355
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_355
        jmp  dword ptr [g_slot+1420]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_356(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 356
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 356
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_356
        jmp  dword ptr [g_slot+1424]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_357(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 357
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 357
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_357
        jmp  dword ptr [g_slot+1428]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_358(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 358
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 358
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_358
        jmp  dword ptr [g_slot+1432]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_359(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 359
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 359
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_359
        jmp  dword ptr [g_slot+1436]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_360(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 360
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 360
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_360
        jmp  dword ptr [g_slot+1440]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_361(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 361
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 361
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_361
        jmp  dword ptr [g_slot+1444]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_362(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 362
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 362
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_362
        jmp  dword ptr [g_slot+1448]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_363(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 363
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 363
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_363
        jmp  dword ptr [g_slot+1452]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_364(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 364
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 364
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_364
        jmp  dword ptr [g_slot+1456]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_365(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 365
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 365
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_365
        jmp  dword ptr [g_slot+1460]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_366(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 366
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 366
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_366
        jmp  dword ptr [g_slot+1464]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_367(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 367
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 367
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_367
        jmp  dword ptr [g_slot+1468]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}

__declspec(naked) void proxy_stub_368(void) {
    __asm {
        pushfd
        pushad
        mov  eax, dword ptr [esp+12]   /* pushad 保存的 esp（指向 flags） */
        lea  eax, [eax+4]              /* -> 返回地址，实参紧随其后 */
        mov  edx, dword ptr [esp+20]   /* saved edx */
        mov  ecx, dword ptr [esp+24]   /* saved ecx */
        push ecx
        push edx
        push eax
        push 368
        call log_call
        add  esp, 16
        popad
        popfd
        mov  eax, dword ptr [esp]      /* 原返回地址 */
        push eax
        push 368
        call save_ret
        add  esp, 8
        mov  dword ptr [esp], offset proxy_post_368
        jmp  dword ptr [g_slot+1472]  /* 尾跳到真实函数：栈布局与直接调用一致 */
    }
}
