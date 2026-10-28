// b2Physics 兼容层：宿主可见的 C ABI（原 DLL 的 87 个导出，见 mapping/b2physics-exports.csv）。
// 记录式调用约定：多数函数只收一个「对象在前的结构体指针」。
// 依据：docs/facts.md F14/F15/F24/F29 与 work/b2physics-decomp/ 的反编译。
#pragma once

#ifdef B2PHYSICS_EXPORTS
#define B2API extern "C" __declspec(dllexport)
#else
#define B2API extern "C" __declspec(dllimport)
#endif

struct b2World;
struct b2Body;
struct b2Shape;
struct b2Joint;

// 宿主可见的扁平静态结构
struct B2Vec2C { float x, y; };

struct B2BodyDefC {          // 原 DLL: { world, angularDamping, linearDamping, allowSleep, fixedRotation, isBullet }
    b2World* world;
    float angularDamping;
    float linearDamping;
    unsigned char allowSleep;
    unsigned char fixedRotation;
    unsigned char isBullet;
};

struct B2ShapeDefC {         // 形状描述公共头（F15）
    b2Body* body;            // +0  Box/Circle/Polygon 三者的 +0 都是 body
    float density;           // +4
    float friction;          // +8
    float restitution;       // +12
    unsigned char sensor;    // +16
    float a, b, c, d;        // +20 box:center / circle:localPos / polygon:vertexCount
};

struct B2XFormC { float x, y, angle; };     // GetXForm 输出 / SetXForm 输入
struct B2FilterC { unsigned short category, mask; short group; };
struct B2MassDataC { float mass; float cx, cy; float I; };
