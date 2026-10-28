// 对 b2Physics.dll 做 ABI 行为探针：加载真实 DLL，按候选签名调用，打印状态。
// 用法: probe_b2physics.exe <dll> <variant>
//   variant=ptr  : b2_CreateWorld(b2Vec2* gravity, int doSleep)
//   variant=flt  : b2_CreateWorld(float gx, float gy)
#include <windows.h>
#include <stdio.h>
#include <string.h>

typedef struct { float x, y; } Vec2;

typedef void* (*fnCreateWorld)(const void*, int);
typedef void* (*fnCreateWorldF)(float, float);
typedef int (*fnStep)(void*, float, int, int);
typedef void* (*fnCreateBody)(const void*);
typedef void* (*fnCreateShapeBox)(const void*);
typedef void* (*fnGetPosition)(void*, void*);
typedef float (*fnGetAngle)(void*);
typedef void (*fnGetVelocity)(void*, void*);

static void* must(HMODULE m, const char* n) {
    void* p = (void*)GetProcAddress(m, n);
    if (!p) printf("MISSING %s\n", n);
    return p;
}

int main(int argc, char** argv) {
    if (argc < 3) { printf("usage: %s <dll> <ptr|flt>\n", argv[0]); return 2; }
    setvbuf(stdout, NULL, _IONBF, 0);
    HMODULE m = LoadLibraryA(argv[1]);
    if (!m) { printf("LoadLibrary failed %lu\n", GetLastError()); return 3; }
    printf("loaded %s\n", argv[1]);
    { typedef int (*fnMax)(void); fnMax fm=(fnMax)GetProcAddress(m,"b2_GetMaxPolygonVertices"); printf("maxpoly=%d\n", fm?fm():-1); }

    void* w = 0;
    if (strcmp(argv[2], "ptr") == 0) {
        Vec2 g = {0.0f, -10.0f};
        fnCreateWorld f = (fnCreateWorld)must(m, "b2_CreateWorld");
        if (f) w = f(&g, 1);
    } else if (strcmp(argv[2], "out") == 0) {
        Vec2 g = {0.0f, -10.0f}; void* slot = 0;
        fnCreateWorld f = (fnCreateWorld)must(m, "b2_CreateWorld");
        if (f) { w = f(&slot, &g); printf("slot=%p\n", slot); }
    } else if (strcmp(argv[2], "null") == 0) {
        Vec2 g = {0.0f, -10.0f};
        fnCreateWorld f = (fnCreateWorld)must(m, "b2_CreateWorld");
        if (f) w = f(0, &g);
    } else if (strcmp(argv[2], "one") == 0) {
        Vec2 g = {0.0f, -10.0f};
        fnCreateWorld f = (fnCreateWorld)must(m, "b2_CreateWorld");
        if (f) w = f((void*)1, &g);
    } else {
        Vec2 g = {0.0f, -10.0f};
        fnCreateWorldF f = (fnCreateWorldF)must(m, "b2_CreateWorld");
        if (f) w = f(g.x, g.y);
    }
    printf("world=%p\n", w);
    if (!w) return 4;

    if (strcmp(argv[2], "pair") == 0) {
        int c = argc > 3 ? atoi(argv[3]) : 0;
        struct { void* world; float x, y; unsigned char a, b, cc; } d;
        memset(&d, 0, sizeof(d));
        d.world = w;
        if (c != 1 && c != 3) { d.x = 1.0f; d.y = 2.0f; }
        if (c != 2 && c != 3) d.a = 1;
        fnCreateBody cb0 = (fnCreateBody)must(m, "b2_World_CreateBody");
        void* b = cb0 ? cb0(&d) : 0;
        printf("pair%d body=%p", c, b);
        if (b) {
            fnGetPosition g0 = (fnGetPosition)must(m, "b2_Body_GetPosition");
            Vec2 p0 = {0, 0}; g0(&p0, b);
            printf(" pos=(%.3f,%.3f)", p0.x, p0.y);
        }
        printf("\n");
        return 0;
    }

    if (strcmp(argv[2], "bdef") == 0) {
        // 假设: def = { b2World* world; b2BodyDef def; }
        struct { void* world; float mass; float cx, cy; float I; void* user; float px, py; float angle;
                 float ldamp, adamp; unsigned char allowSleep, isSleeping, fixedRot, isBullet; } d;
        memset(&d, 0, sizeof(d));
        d.world = w; d.px = 3.0f; d.py = 4.0f; d.angle = 0.5f; d.allowSleep = 1;
        fnCreateBody cb0 = (fnCreateBody)must(m, "b2_World_CreateBody");
        void* b = cb0 ? cb0(&d) : 0;
        printf("bdef body=%p", b);
        if (b) {
            fnGetPosition g0 = (fnGetPosition)must(m, "b2_Body_GetPosition");
            Vec2 p0 = {0, 0}; g0(&p0, b);
            fnGetAngle a0 = (fnGetAngle)must(m, "b2_Body_GetAngle");
            printf(" pos=(%.2f,%.2f) angle=%.3f", p0.x, p0.y, a0(b));
        }
        printf("\n");
        return 0;
    }

    if (strcmp(argv[2], "slot") == 0) {
        // { b2World* world; float f[5]; } 全零，仅第 argv[3] 个 float 置 1.0
        int idx = argc > 3 ? atoi(argv[3]) : 0;
        struct { void* world; float f[13]; } d;
        memset(&d, 0, sizeof(d));
        d.world = w;
        if (idx >= 0 && idx < 13) d.f[idx] = 1.0f;
        ((unsigned char*)&d.f[2])[0] = 1;  // 试：allowSleep 槽位为 1
        fnCreateBody cb0 = (fnCreateBody)must(m, "b2_World_CreateBody");
        void* b = cb0 ? cb0(&d) : 0;
        printf("slot%d body=%p", idx, b);
        if (b) {
            fnGetPosition g0 = (fnGetPosition)must(m, "b2_Body_GetPosition");
            Vec2 p0 = {0, 0};
            g0(&p0, b);
            fnGetVelocity v0 = (fnGetVelocity)must(m, "b2_Body_GetVelocity");
            Vec2 ve = {0, 0};
            v0(&ve, b);
            fnGetAngle a0 = (fnGetAngle)must(m, "b2_Body_GetAngle");
            printf(" pos=(%.2f,%.2f) vel=(%.2f,%.2f) angle=%.2f", p0.x, p0.y, ve.x, ve.y, a0(b));
        }
        printf("\n");
        return 0;
    }

    // 宿主侧构造的 body def: { b2World* world; float x, y; u8 allowSleep, fixedRotation, isBullet; }
    struct { void* world; float x, y; unsigned char a, b, c; } def;
    memset(&def, 0, sizeof(def));
    def.world = w;
    def.x = 1.0f; def.y = 2.0f; def.a = 1; def.b = 0; def.c = 0;

    fnCreateBody cb = (fnCreateBody)must(m, "b2_World_CreateBody");
    void* body = cb ? cb(&def) : 0;
    printf("body=%p\n", body);

    fnGetPosition gp = (fnGetPosition)must(m, "b2_Body_GetPosition");
    Vec2 pos = {0, 0}, pos2 = {-1, -1};
    if (gp && body) gp(&pos, body);
    if (gp && body) gp(body, &pos2);
    printf("pos_before out-first=(%.4f, %.4f) body-first=(%.4f, %.4f)\n", pos.x, pos.y, pos2.x, pos2.y);

    fnStep st = (fnStep)must(m, "b2_World_Step");
    for (int i = 0; i < 10; ++i) st(w, 1.0f / 60.0f, 10, 10);

    pos.x = pos.y = 0;
    if (gp && body) gp(&pos, body);
    printf("pos_after=(%.4f, %.4f)\n", pos.x, pos.y);

    fnGetAngle ga = (fnGetAngle)must(m, "b2_Body_GetAngle");
    if (ga && body) printf("angle=%.6f\n", ga(body));

    fnGetVelocity gv = (fnGetVelocity)must(m, "b2_Body_GetVelocity");
    Vec2 vel = {0, 0};
    if (gv && body) gv(&vel, body);
    printf("vel=(%.4f, %.4f)\n", vel.x, vel.y);
    return 0;
}
