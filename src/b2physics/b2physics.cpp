// b2Physics 兼容层实现（World / Body / Shape 族）。
// 依据：docs/facts.md F14/F15/F24/F29；反编译语料 work/b2physics-decomp/。
// 原 DLL 的包装层直接读写 Box2D 内部字段，这里同样按字段语义实现，保持副作用一致。
#include <cassert>
#include <cmath>
#include <cstddef>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <new>

#define private public
#define protected public
#include "Box2D.h"
#undef private
#undef protected

#include "b2physics.h"

namespace {

b2Vec2 V(const B2Vec2C& v) { return b2Vec2(v.x, v.y); }
b2Vec2 V(const float* p) { return b2Vec2(p[0], p[1]); }
void Out(B2Vec2C* out, const b2Vec2& v) { out->x = v.x; out->y = v.y; }

// 唤醒 body 并把 sleepTime 归零（原 DLL: m_flags &= ~8; body+148 = 0）
void Wake(b2Body* b) {
    b->m_flags &= ~b2Body::e_sleepFlag;
    b->m_sleepTime = 0.0f;
}

}  // namespace

// ---------------------------------------------------------------- World

// 实测（F29）：arg0 必须是非空可写指针 —— 它是 b2World 构造所需的 world AABB
B2API void* b2_CreateWorld(const b2AABB* aabb, const B2Vec2C* gravity) {
    b2Vec2 g = gravity ? V(*gravity) : b2Vec2(0.0f, -10.0f);
    b2AABB box = aabb ? *aabb : b2AABB();
    return new b2World(box, g, true);
}

B2API void b2_DestroyWorld(b2World* world) {
    if (!world) return;
    world->~b2World();
    ::operator delete(world);
}

B2API void b2_World_Step(b2World* world, float dt, int velocityIterations, int positionIterations) {
    world->Step(dt, velocityIterations, positionIterations);
}

B2API void b2_World_SetGravity(b2World* world, const B2Vec2C* gravity) {
    world->m_gravity = V(*gravity);
}

B2API void b2_World_ReFilter(b2World* world) {
    for (b2Body* b = world->m_bodyList; b; b = b->m_next) {
        for (b2Shape* s = b->m_shapeList; s; s = s->m_next) {
            world->Refilter(s);
        }
    }
}

namespace {
class CallbackHolder {
public:
    static b2ContactFilter g_filter;
    static b2ContactListener g_listener;
};
b2ContactFilter CallbackHolder::g_filter;
b2ContactListener CallbackHolder::g_listener;
}  // namespace

B2API void b2_World_SetContactFilterCallBack(b2World* world, b2ContactFilter* filter) {
    world->SetContactFilter(filter);
}

B2API void b2_World_SetContactListenerCallBack(b2World* world, b2ContactListener* listener) {
    world->SetContactListener(listener);
}

B2API void* b2_World_CreateBody(const B2BodyDefC* d) {
    b2BodyDef def;  // 默认构造：massData 0、position 0、allowSleep=true
    def.angularDamping = d->angularDamping;
    def.linearDamping = d->linearDamping;
    def.allowSleep = d->allowSleep != 0;
    def.fixedRotation = d->fixedRotation != 0;
    def.isBullet = d->isBullet != 0;
    return d->world->CreateBody(&def);
}

B2API void b2_World_DestroyBody(b2World* world, b2Body* body) {
    (void)world;  // 原 DLL 只用 body 自身
    body->m_world->DestroyBody(body);
}

B2API void b2_World_DestroyJoint(b2Joint* joint) {
    joint->m_body1->m_world->DestroyJoint(joint);
}

B2API void b2_World_ClearJoints(b2World* world) {
    while (world->m_jointList) {
        world->DestroyJoint(world->m_jointList);
    }
}

B2API int b2_GetMaxPolygonVertices(void) { return 8; }

// ---------------------------------------------------------------- Body

B2API void b2_Body_ApplyForce(b2Body* body, const float* force, const float* point) {
    body->ApplyForce(V(force), V(point));
}

B2API void b2_Body_ApplyImpulse(b2Body* body, const float* impulse, const float* point) {
    body->ApplyImpulse(V(impulse), V(point));
}

B2API void b2_Body_ApplyTorque(b2Body* body, float torque) {
    if (body->m_flags & b2Body::e_sleepFlag) Wake(body);
    body->m_force.y += 0.0f;  // 保持与原实现相同的分支形状
    body->m_torque += torque;
}

B2API void b2_Body_ClearShapes(b2Body* body) {
    while (body->m_shapeList) {
        body->DestroyShape(body->m_shapeList);
    }
}

namespace {

void FillShapeCommon(b2ShapeDef* def, const B2ShapeDefC* d) {
    def->friction = d->friction;
    def->restitution = d->restitution;
    def->density = d->density;
    def->isSensor = d->sensor != 0;
}

}  // namespace

B2API void* b2_Body_CreateShape_Box(const B2ShapeDefC* d) {
    b2PolygonDef def;
    FillShapeCommon(&def, d);
    def.SetAsBox(d->c, d->d, b2Vec2(d->a, d->b), 0.0f);  // +28/+32 半宽高，+20/+24 中心
    return d->body->CreateShape(&def);
}

B2API void* b2_Body_CreateShape_Circle(const B2ShapeDefC* d) {
    b2CircleDef def;
    FillShapeCommon(&def, d);
    def.localPosition.Set(d->a, d->b);  // +20/+24
    def.radius = d->c;                 // +28
    return d->body->CreateShape(&def);
}

B2API void* b2_Body_CreateShape_Polygon(const B2ShapeDefC* d) {
    b2PolygonDef def;
    FillShapeCommon(&def, d);
    int count = (int)d->a;  // +20 顶点数
    if (count < 3) return nullptr;
    if (count > b2_maxPolygonVertices) count = b2_maxPolygonVertices;
    def.vertexCount = count;
    const float* p = &d->b;  // +24 起是顶点数组
    for (int i = 0; i < count; ++i) {
        def.vertices[i].Set(p[2 * i], p[2 * i + 1]);
    }
    return d->body->CreateShape(&def);
}

B2API void b2_Body_DestroyShape(b2Shape* shape) { shape->m_body->DestroyShape(shape); }

B2API float b2_Body_GetAngle(b2Body* body) { return body->m_sweep.a; }

B2API float b2_Body_GetAngularDamping(b2Body* body) { return body->m_angularDamping; }

B2API int b2_Body_GetIsSleeping(b2Body* body) {
    return (body->m_flags & b2Body::e_sleepFlag) ? 1 : 0;
}

B2API void* b2_Body_GetLocalPoint(void* out, b2Body* body, const float* p) {
    *(b2Vec2*)out = body->GetLocalPoint(V(p));
    return out;
}

B2API void* b2_Body_GetLocalVector(void* out, b2Body* body, const float* v) {
    *(b2Vec2*)out = body->GetLocalVector(V(v));
    return out;
}

B2API void b2_Body_GetMass(b2Body* body, B2MassDataC* out) {
    out->mass = body->m_mass;
    out->cx = body->m_sweep.c.x;
    out->cy = body->m_sweep.c.y;
    out->I = body->m_I;
}

B2API float b2_Body_GetOmega(b2Body* body) { return body->m_angularVelocity; }

B2API void* b2_Body_GetPosition(void* out, b2Body* body) {
    Out((B2Vec2C*)out, body->m_xf.position);
    return out;
}

B2API void* b2_Body_GetShapeList(b2Body* body) { return body->m_shapeList; }

B2API void* b2_Body_GetUserData(b2Body* body) { return body->m_userData; }

B2API void* b2_Body_GetVelocity(void* out, b2Body* body) {
    Out((B2Vec2C*)out, body->m_linearVelocity);
    return out;
}

B2API void* b2_Body_GetWorld(b2Body* body) { return body->m_world; }

B2API void* b2_Body_GetWorldPoint(void* out, b2Body* body, const float* p) {
    *(b2Vec2*)out = body->GetWorldPoint(V(p));
    return out;
}

B2API void* b2_Body_GetWorldVector(void* out, b2Body* body, const float* v) {
    *(b2Vec2*)out = body->GetWorldVector(V(v));
    return out;
}

B2API void* b2_Body_GetXForm(b2Body* body, B2XFormC* out) {
    out->x = body->m_xf.position.x;
    out->y = body->m_xf.position.y;
    out->angle = body->m_sweep.a;
    return body;
}

B2API int b2_Body_IsBullet(b2Body* body) {
    return (body->m_flags & b2Body::e_bulletFlag) ? 1 : 0;
}

B2API int b2_Body_IsFrozen(b2Body* body) {
    return (body->m_flags & b2Body::e_frozenFlag) ? 1 : 0;
}

B2API void b2_Body_PutToSleep(b2Body* body) {
    body->m_flags |= b2Body::e_sleepFlag;
    body->m_sleepTime = 0.0f;
    body->m_linearVelocity.SetZero();
    body->m_angularVelocity = 0.0f;
    body->m_force.SetZero();
    body->m_torque = 0.0f;
}

B2API void b2_Body_SetAngularDamping(b2Body* body, float d) { body->m_angularDamping = d; }

B2API void b2_Body_SetBullet(b2Body* body, int flag) {
    if (flag)
        body->m_flags |= b2Body::e_bulletFlag;
    else
        body->m_flags &= ~b2Body::e_bulletFlag;
}

B2API void b2_Body_SetMass(b2Body* body, const B2MassDataC* md) { body->SetMass((const b2MassData*)md); }

B2API void b2_Body_SetMassFromShapes(b2Body* body) { body->SetMassFromShapes(); }

B2API void b2_Body_SetOmega(b2Body* body, float omega) {
    body->m_flags &= ~b2Body::e_sleepFlag;
    body->m_sleepTime = 0.0f;
    body->m_angularVelocity = omega;
}

B2API void* b2_Body_SetUserData(b2Body* body, void* data) {
    body->m_userData = data;
    return data;
}

B2API void b2_Body_SetVelocity(b2Body* body, const float* v) {
    body->m_flags &= ~b2Body::e_sleepFlag;
    body->m_sleepTime = 0.0f;
    body->m_linearVelocity = V(v);
}

B2API void b2_Body_SetXForm(b2Body* body, const B2XFormC* xf) {
    body->m_xf.position.Set(xf->x, xf->y);
    body->m_xf.R.Set(xf->angle);
    body->m_sweep.c = body->m_xf.position;
    body->m_sweep.a = xf->angle;
    body->SynchronizeTransform();
}

B2API void b2_Body_WakeUp(b2Body* body) {
    body->m_sleepTime = 0.0f;
    body->m_flags &= ~b2Body::e_sleepFlag;
}

// ---------------------------------------------------------------- Shape

B2API void* b2_Shape_GetBody(b2Shape* shape) { return shape->m_body; }

B2API void* b2_Shape_GetNext(b2Shape* shape) { return shape->m_next; }

B2API int b2_Shape_GetShapeType(b2Shape* shape) {
    switch (shape->m_type) {
        case e_unknownShape: return 0;
        case e_circleShape: return 1;
        case e_polygonShape: return 2;
        default: return -1;
    }
}

B2API float b2_Shape_GetDensity(b2Shape* shape) { return shape->m_density; }
B2API float b2_Shape_GetFriction(b2Shape* shape) { return shape->m_friction; }
B2API float b2_Shape_GetRestitution(b2Shape* shape) { return shape->m_restitution; }
B2API int b2_Shape_GetSensor(b2Shape* shape) { return shape->m_isSensor ? 1 : 0; }

B2API void b2_Shape_SetDensity(b2Shape* shape, float v) { shape->m_density = v; }
B2API void b2_Shape_SetFriction(b2Shape* shape, float v) { shape->m_friction = v; }
B2API void b2_Shape_SetRestitution(b2Shape* shape, float v) { shape->m_restitution = v; }
B2API int b2_Shape_SetSensor(b2Shape* shape, int v) { shape->m_isSensor = v != 0; return v; }

B2API void* b2_Shape_GetFilter(b2Shape* shape, B2FilterC* out) {
    out->category = shape->m_filter.categoryBits;
    out->mask = shape->m_filter.maskBits;
    out->group = shape->m_filter.groupIndex;
    return out;
}

B2API void* b2_Shape_SetFilter(b2Shape* shape, const B2FilterC* f) {
    shape->m_filter.categoryBits = f->category;
    shape->m_filter.maskBits = f->mask;
    shape->m_filter.groupIndex = f->group;
    return shape;
}

B2API void* b2_Shape_GetCirclePos(void* out, b2Shape* shape) {
    if (shape->m_type != e_circleShape) {
        ((float*)out)[0] = ((float*)out)[1] = 0.0f;
        return out;
    }
    Out((B2Vec2C*)out, ((b2CircleShape*)shape)->m_localPosition);
    return out;
}

B2API float b2_Shape_GetCircleRadius(b2Shape* shape) {
    if (shape->m_type != e_circleShape) return 0.0f;
    return ((b2CircleShape*)shape)->m_radius;
}

B2API int b2_Shape_TestPoint(b2Shape* shape, const B2XFormC* xf, const float* p) {
    b2XForm f;
    f.position.Set(xf->x, xf->y);
    f.R.Set(xf->angle);
    return shape->TestPoint(f, V(p)) ? 1 : 0;
}

// ---------------------------------------------------------------- Joints

// 工厂：输入布局见 docs/facts.md F34
B2API void* b2_World_Joint_Distance(const B2DistanceJointC* d) {
    b2DistanceJointDef def;
    def.Initialize(d->body1, d->body2, V(d->anchor1), V(d->anchor2));
    def.collideConnected = d->collide != 0;
    return d->world->CreateJoint(&def);
}

B2API void* b2_World_Joint_Revolute(const B2RevoluteJointC* d) {
    b2RevoluteJointDef def;
    def.Initialize(d->body1, d->body2, V(d->anchor));
    def.enableLimit = d->enableLimit != 0;
    def.lowerAngle = d->lower;
    def.upperAngle = d->upper;
    def.enableMotor = d->enableMotor != 0;
    def.motorSpeed = d->motorSpeed;
    def.maxMotorTorque = d->maxMotorTorque;
    def.collideConnected = d->collide != 0;
    return d->world->CreateJoint(&def);
}

B2API void* b2_World_Joint_Prismatic(const B2PrismaticJointC* d) {
    b2PrismaticJointDef def;
    def.Initialize(d->body1, d->body2, V(d->anchor), V(d->axis));
    def.enableLimit = d->enableLimit != 0;
    def.lowerTranslation = d->lower;
    def.upperTranslation = d->upper;
    def.enableMotor = d->enableMotor != 0;
    def.motorSpeed = d->motorSpeed;
    def.maxMotorForce = d->maxMotorForce;
    def.collideConnected = d->collide != 0;
    return d->world->CreateJoint(&def);
}

B2API void* b2_World_Joint_Gear(const B2GearJointC* d) {
    b2GearJointDef def;
    def.body1 = d->body1;
    def.body2 = d->body2;
    def.joint1 = d->joint1;
    def.joint2 = d->joint2;
    def.ratio = d->ratio;
    def.collideConnected = false;
    return d->world->CreateJoint(&def);
}

B2API void* b2_World_Joint_Pulley(const B2PulleyJointC* d) {
    b2PulleyJointDef def;
    def.Initialize(d->body1, d->body2, V(d->groundAnchor1), V(d->groundAnchor2),
                   V(d->localAnchor1), V(d->localAnchor2), d->ratio);
    def.collideConnected = d->collide != 0;
    return d->world->CreateJoint(&def);
}

namespace {

template <class T>
T* As(b2Joint* j) {
    return static_cast<T*>(j);
}

}  // namespace

B2API void b2_Joint_EnableLimit(b2Joint* j, int enable) {
    switch (j->m_type) {
        case e_revoluteJoint: As<b2RevoluteJoint>(j)->EnableLimit(enable != 0); break;
        case e_prismaticJoint: As<b2PrismaticJoint>(j)->EnableLimit(enable != 0); break;
        default: break;
    }
}

B2API void b2_Joint_EnableMotor(b2Joint* j, int enable) {
    switch (j->m_type) {
        case e_revoluteJoint: As<b2RevoluteJoint>(j)->EnableMotor(enable != 0); break;
        case e_prismaticJoint: As<b2PrismaticJoint>(j)->EnableMotor(enable != 0); break;
        default: break;
    }
}

B2API void* b2_Joint_GetAnchor1(void* out, b2Joint* j) {
    *(b2Vec2*)out = j->GetAnchor1();
    return out;
}

B2API void* b2_Joint_GetAnchor2(void* out, b2Joint* j) {
    *(b2Vec2*)out = j->GetAnchor2();
    return out;
}

B2API void* b2_Joint_GetBody1(b2Joint* j) { return j->m_body1; }
B2API void* b2_Joint_GetBody2(b2Joint* j) { return j->m_body2; }

B2API float b2_Joint_GetJointAngle(b2Joint* j) {
    if (j->m_type != e_revoluteJoint) return 0.0f;
    return As<b2RevoluteJoint>(j)->GetJointAngle();
}

B2API float b2_Joint_GetJointTranslation(b2Joint* j) {
    if (j->m_type != e_prismaticJoint) return 0.0f;
    return As<b2PrismaticJoint>(j)->GetJointTranslation();
}

B2API int b2_Joint_GetJointType(b2Joint* j) {
    switch (j->m_type) {
        case e_revoluteJoint: return 0;
        case e_prismaticJoint: return 1;
        case e_distanceJoint: return 2;
        case e_pulleyJoint: return 3;
        case e_gearJoint: return 4;
        default: return -1;
    }
}

B2API void* b2_Joint_GetLimits(b2Joint* j, float* lower, float* upper) {
    switch (j->m_type) {
        case e_revoluteJoint:
            *lower = As<b2RevoluteJoint>(j)->GetLowerLimit();
            *upper = As<b2RevoluteJoint>(j)->GetUpperLimit();
            break;
        case e_prismaticJoint:
            *lower = As<b2PrismaticJoint>(j)->GetLowerLimit();
            *upper = As<b2PrismaticJoint>(j)->GetUpperLimit();
            break;
        default:
            *lower = *upper = 0.0f;
            break;
    }
    return j;
}

B2API float b2_Joint_GetMotorSpeed(b2Joint* j) {
    switch (j->m_type) {
        case e_revoluteJoint: return As<b2RevoluteJoint>(j)->GetMotorSpeed();
        case e_prismaticJoint: return As<b2PrismaticJoint>(j)->GetMotorSpeed();
        default: return 0.0f;
    }
}

B2API void* b2_Joint_GetReactionImpulse(void* out, b2Joint* j) {
    *(b2Vec2*)out = j->GetReactionForce(1.0f);
    return out;
}

B2API float b2_Joint_GetReactionTorqImpulse(b2Joint* j) { return j->GetReactionTorque(1.0f); }

B2API int b2_Joint_IsLimitEnabled(b2Joint* j) {
    switch (j->m_type) {
        case e_revoluteJoint: return As<b2RevoluteJoint>(j)->IsLimitEnabled() ? 1 : 0;
        case e_prismaticJoint: return As<b2PrismaticJoint>(j)->IsLimitEnabled() ? 1 : 0;
        default: return 0;
    }
}

B2API int b2_Joint_IsMotorEnabled(b2Joint* j) {
    switch (j->m_type) {
        case e_revoluteJoint: return As<b2RevoluteJoint>(j)->IsMotorEnabled() ? 1 : 0;
        case e_prismaticJoint: return As<b2PrismaticJoint>(j)->IsMotorEnabled() ? 1 : 0;
        default: return 0;
    }
}

B2API void b2_Joint_SetLimits(b2Joint* j, float lower, float upper) {
    switch (j->m_type) {
        case e_revoluteJoint: As<b2RevoluteJoint>(j)->SetLimits(lower, upper); break;
        case e_prismaticJoint: As<b2PrismaticJoint>(j)->SetLimits(lower, upper); break;
        default: break;
    }
}

B2API void b2_Joint_SetMaxMotorForce(b2Joint* j, float force) {
    if (j->m_type == e_prismaticJoint) As<b2PrismaticJoint>(j)->SetMaxMotorForce(force);
}

B2API void b2_Joint_SetMaxMotorTorque(b2Joint* j, float torque) {
    if (j->m_type == e_revoluteJoint) As<b2RevoluteJoint>(j)->SetMaxMotorTorque(torque);
}

B2API void b2_Joint_SetMotorSpeed(b2Joint* j, float speed) {
    switch (j->m_type) {
        case e_revoluteJoint: As<b2RevoluteJoint>(j)->SetMotorSpeed(speed); break;
        case e_prismaticJoint: As<b2PrismaticJoint>(j)->SetMotorSpeed(speed); break;
        default: break;
    }
}
