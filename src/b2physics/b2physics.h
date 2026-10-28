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

struct B2ShapeDefC {         // 形状描述公共头（F32 实测：+4 摩擦、+8 弹性、+12 密度、+16 传感器）
    b2Body* body;            // +0
    float friction;          // +4
    float restitution;       // +8
    float density;           // +12
    unsigned char sensor;    // +16
    float a, b, c, d;        // +20/+24 center 或 localPos；+28/+32 半宽高 或 radius / 顶点
};

// 关节工厂输入（F34：world/body1/body2 公共头）
struct B2JointCommonC { b2World* world; b2Body* body1; b2Body* body2; };
struct B2DistanceJointC : B2JointCommonC { B2Vec2C anchor1, anchor2; unsigned char collide; };
struct B2RevoluteJointC : B2JointCommonC {
    B2Vec2C anchor; unsigned char enableLimit; float lower, upper;
    unsigned char enableMotor; float motorSpeed, maxMotorTorque; unsigned char collide;
};
struct B2PrismaticJointC : B2JointCommonC {
    B2Vec2C anchor, axis; unsigned char enableLimit; float lower, upper;
    unsigned char enableMotor; float motorSpeed, maxMotorForce; unsigned char collide;
};
struct B2GearJointC : B2JointCommonC { b2Joint* joint1; b2Joint* joint2; float ratio; };
struct B2PulleyJointC : B2JointCommonC {
    B2Vec2C groundAnchor1, groundAnchor2, localAnchor1, localAnchor2;
    float length1, length2, ratio; unsigned char collide;
};

struct B2XFormC { float x, y, angle; };     // GetXForm 输出 / SetXForm 输入
struct B2FilterC { unsigned short category, mask; short group; };
struct B2MassDataC { float mass; float cx, cy; float I; };
