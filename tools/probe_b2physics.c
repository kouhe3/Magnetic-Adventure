// b2Physics.dll ABI 探针：加载真 DLL，按已验证的签名调用，打印可观测状态。
// 已验证（docs/facts.md F29）：b2_CreateWorld(void* ctx, const b2Vec2* gravity)。
// 用法: probe_b2physics.exe <dll> [pair <c>|slot <i>|step]
#include <windows.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct { float x, y; } Vec2;
typedef void* (*fnCreateWorld)(void* ctx, const void* gravity);
typedef int (*fnStep)(void* w, float dt, int vi, int pi);
typedef void* (*fnCreateBody)(const void* def);
typedef void* (*fnCreateShapeBox)(const void* def);
typedef void* (*fnGetPosition)(void* out, void* body);
typedef void* (*fnGetVelocity)(void* out, void* body);
typedef float (*fnGetAngle)(void* body);
typedef int (*fnIsSleeping)(void* body);
typedef int (*fnIsBullet)(void* body);
typedef void* (*fnSetMassFromShapes)(void* body);
typedef float (*fnGetAngularDamping)(void* body);
typedef void* (*fnSetXForm)(void* body, const void* xf);
typedef void* (*fnApplyTorque)(void* body, float t);

static void* sym(HMODULE m, const char* n) {
    void* p = (void*)GetProcAddress(m, n);
    if (!p) printf("MISSING %s\n", n);
    return p;
}

int main(int argc, char** argv) {
    setvbuf(stdout, NULL, _IONBF, 0);
    if (argc < 2) { printf("usage: %s <dll> [pair c|slot i|step]\n", argv[0]); return 2; }
    HMODULE m = LoadLibraryA(argv[1]);
    if (!m) { printf("LoadLibrary failed %lu\n", GetLastError()); return 3; }

    Vec2 g = {0.0f, -10.0f};
    struct { Vec2 lo, hi; } aabb = {{-100.0f, -100.0f}, {100.0f, 100.0f}};
    fnCreateWorld cw = (fnCreateWorld)sym(m, "b2_CreateWorld");
    if (!cw) return 4;
    void* w = cw(&aabb, &g);
    printf("world=%p\n", w);
    if (!w) return 5;

    // 宿主实测的 body def 形状: { b2World* world; float f4, f8; u8 b12, b13, b14; }
    struct Def { void* world; float f4, f8; unsigned char b12, b13, b14; };
    struct Def d;
    memset(&d, 0, sizeof(d));
    d.world = w;

    fnCreateBody cb = (fnCreateBody)sym(m, "b2_World_CreateBody");

    if (argc > 2 && strcmp(argv[2], "slot") == 0) {
        int idx = argc > 3 ? atoi(argv[3]) : 0;
        if (idx == 0) d.f4 = 1.0f;
        else if (idx == 1) d.f8 = 1.0f;
        else if (idx == 2) d.b12 = 2;
        else if (idx == 3) d.b13 = 1;
        else if (idx == 4) d.b14 = 1;
        else if (idx == 5) d.b12 = 1;
    } else if (argc > 2 && strcmp(argv[2], "pair") == 0) {
        int c = argc > 3 ? atoi(argv[3]) : 0;
        if (c == 0) { d.f4 = 1.0f; d.f8 = 2.0f; d.b12 = 1; }
        else if (c == 1) { d.b12 = 1; }
        else if (c == 2) { d.f4 = 1.0f; d.f8 = 2.0f; }
        else { d.b12 = 1; d.b13 = 1; d.b14 = 1; }
    } else {
        d.b12 = 1;   // 与宿主一致
    }

    void* body = cb ? cb(&d) : 0;
    printf("body=%p (f4=%.2f f8=%.2f b12=%u b13=%u b14=%u)\n", body, d.f4, d.f8, d.b12, d.b13, d.b14);
    if (!body) return 6;

    fnGetPosition gp = (fnGetPosition)sym(m, "b2_Body_GetPosition");
    fnGetAngle ga = (fnGetAngle)sym(m, "b2_Body_GetAngle");
    fnGetVelocity gv = (fnGetVelocity)sym(m, "b2_Body_GetVelocity");
    fnIsSleeping isl = (fnIsSleeping)sym(m, "b2_Body_GetIsSleeping");
    fnIsBullet isb = (fnIsBullet)sym(m, "b2_Body_IsBullet");

    Vec2 p = {0, 0}, v = {0, 0};
    gp(&p, body); gv(&v, body);
    fnGetAngularDamping gad = (fnGetAngularDamping)sym(m, "b2_Body_GetAngularDamping");
    printf("t0 pos=(%.4f,%.4f) vel=(%.4f,%.4f) angle=%.4f sleeping=%d bullet=%d adamp=%.3f\n",
           p.x, p.y, v.x, v.y, ga(body), isl(body), isb(body), gad ? gad(body) : -1.0f);

    if (argc > 2 && strcmp(argv[2], "box") == 0) {
        // 建体 + 0.5x0.5 方块 + 重力步进，用于与原 DLL 差分
        d.f4 = 0; d.f8 = 0; d.b12 = 1; d.b13 = 0; d.b14 = 0;
        void* b2 = cb(&d);
        struct { void* body; float density, friction, restitution; unsigned char sensor;
                 float cx, cy, hw, hh; } sd;
        memset(&sd, 0, sizeof(sd));
        sd.body = b2; sd.density = 1.0f; sd.friction = 0.3f; sd.hw = 0.5f; sd.hh = 0.5f;
        fnCreateShapeBox cs = (fnCreateShapeBox)sym(m, "b2_Body_CreateShape_Box");
        void* sh = cs ? cs(&sd) : 0;
        fnSetMassFromShapes ms = (fnSetMassFromShapes)sym(m, "b2_Body_SetMassFromShapes");
        if (ms) ms(b2);
        printf("box shape=%p\n", sh);
        fnStep st = (fnStep)sym(m, "b2_World_Step");
        for (int i = 0; i < 60; ++i) st(w, 1.0f / 60.0f, 10, 10);
        Vec2 p2 = {0, 0}, v2 = {0, 0};
        fnGetPosition gpx = (fnGetPosition)sym(m, "b2_Body_GetPosition");
        fnGetVelocity gvx = (fnGetVelocity)sym(m, "b2_Body_GetVelocity");
        fnGetAngle gax = (fnGetAngle)sym(m, "b2_Body_GetAngle");
        gpx(&p2, b2); gvx(&v2, b2);
        printf("box t60 pos=(%.6f,%.6f) vel=(%.6f,%.6f) angle=%.6f\n", p2.x, p2.y, v2.x, v2.y, gax(b2));
        return 0;
    }

    if (argc > 2 && strcmp(argv[2], "torque") == 0) {
        int b13 = argc > 3 ? atoi(argv[3]) : 0;
        d.f4 = 0; d.f8 = 0; d.b12 = 1; d.b13 = (unsigned char)b13; d.b14 = 0;
        void* b2 = cb(&d);
        fnApplyTorque at = (fnApplyTorque)sym(m, "b2_Body_ApplyTorque");
        fnStep st = (fnStep)sym(m, "b2_World_Step");
        at(b2, 100.0f);
        for (int i = 0; i < 60; ++i) st(w, 1.0f / 60.0f, 10, 10);
        printf("torque b13=%d angle=%.4f\n", b13, ga(b2));
        return 0;
    }

    if (argc > 2 && strcmp(argv[2], "step") == 0) {
        fnStep st = (fnStep)sym(m, "b2_World_Step");
        for (int i = 0; i < 60; ++i) st(w, 1.0f / 60.0f, 10, 10);
        gp(&p, body); gv(&v, body);
        printf("t60 pos=(%.4f,%.4f) vel=(%.4f,%.4f)\n", p.x, p.y, v.x, v.y);
    }
    return 0;
}
