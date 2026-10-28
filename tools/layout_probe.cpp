// 布局探针：打印 b2Body/b2World/b2BodyDef/形状与关节定义的成员偏移。
// 用途：把原 b2Physics.dll 反编译里看到的栈偏移映射回具体字段（docs/facts.md F24/F26）。
#include <cstddef>
#include <cstdio>

#define private public
#define protected public
#include "Box2D.h"

int main() {
    printf("sizeof(b2World)=%zu (0x%zx)\n", sizeof(b2World), sizeof(b2World));
    printf("b2Body: xf=%zu position=%zu sweep=%zu sweep.a=%zu lv=%zu av=%zu shapeList=%zu sleepTime=%zu userData=%zu\n",
           offsetof(b2Body, m_xf), offsetof(b2Body, m_xf) + offsetof(b2XForm, position),
           offsetof(b2Body, m_sweep), offsetof(b2Body, m_sweep) + offsetof(b2Sweep, a),
           offsetof(b2Body, m_linearVelocity), offsetof(b2Body, m_angularVelocity),
           offsetof(b2Body, m_shapeList), offsetof(b2Body, m_sleepTime), offsetof(b2Body, m_userData));
    printf("b2World: gravity=%zu\n", offsetof(b2World, m_gravity));

    printf("sizeof(b2BodyDef)=%zu\n", sizeof(b2BodyDef));
    printf("b2BodyDef: userData=%zu position=%zu angle=%zu linearVelocity=%zu angularVelocity=%zu "
           "linearDamping=%zu angularDamping=%zu allowSleep=%zu isSleeping=%zu fixedRotation=%zu isBullet=%zu\n",
           offsetof(b2BodyDef, userData), offsetof(b2BodyDef, position), offsetof(b2BodyDef, angle),
           offsetof(b2BodyDef, linearVelocity), offsetof(b2BodyDef, angularVelocity),
           offsetof(b2BodyDef, linearDamping), offsetof(b2BodyDef, angularDamping),
           offsetof(b2BodyDef, allowSleep), offsetof(b2BodyDef, isSleeping),
           offsetof(b2BodyDef, fixedRotation), offsetof(b2BodyDef, isBullet));

    printf("sizeof(b2PolygonDef)=%zu sizeof(b2CircleDef)=%zu sizeof(b2ShapeDef)=%zu\n",
           sizeof(b2PolygonDef), sizeof(b2CircleDef), sizeof(b2ShapeDef));
    printf("b2ShapeDef: type=%zu userData=%zu filter=%zu density=%zu friction=%zu restitution=%zu\n",
           offsetof(b2ShapeDef, type), offsetof(b2ShapeDef, userData), offsetof(b2ShapeDef, filter),
           offsetof(b2ShapeDef, density), offsetof(b2ShapeDef, friction), offsetof(b2ShapeDef, restitution));
    printf("b2CircleDef: radius=%zu localPosition=%zu | b2PolygonDef: vertexCount=%zu vertices=%zu\n",
           offsetof(b2CircleDef, radius), offsetof(b2CircleDef, localPosition),
           offsetof(b2PolygonDef, vertexCount), offsetof(b2PolygonDef, vertices));
    printf("sizeof(b2JointDef)=%zu type=%zu body1=%zu body2=%zu collideConnected=%zu\n",
           sizeof(b2JointDef), offsetof(b2JointDef, type), offsetof(b2JointDef, body1),
           offsetof(b2JointDef, body2), offsetof(b2JointDef, collideConnected));
    return 0;
}
