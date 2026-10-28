// 布局探针：用 vendored Box2D 打印 b2Body/b2World 的成员偏移与大小，
// 与原 b2Physics.dll 里观察到的偏移对照（见 docs/facts.md F24/F26）。
#include <cstddef>
#include <cstdio>

#define private public
#include "Box2D.h"

int main() {
    printf("sizeof(b2World)=%zu (0x%zx)\n", sizeof(b2World), sizeof(b2World));
    printf("b2Body: xf=%zu position=%zu sweep=%zu sweep.a=%zu lv=%zu av=%zu force=%zu torque=%zu world=%zu shapeList=%zu mass=%zu damping=%zu sleepTime=%zu userData=%zu\n",
           offsetof(b2Body, m_xf),
           offsetof(b2Body, m_xf) + offsetof(b2XForm, position),
           offsetof(b2Body, m_sweep),
           offsetof(b2Body, m_sweep) + offsetof(b2Sweep, a),
           offsetof(b2Body, m_linearVelocity),
           offsetof(b2Body, m_angularVelocity),
           offsetof(b2Body, m_force),
           offsetof(b2Body, m_torque),
           offsetof(b2Body, m_world),
           offsetof(b2Body, m_shapeList),
           offsetof(b2Body, m_mass),
           offsetof(b2Body, m_linearDamping),
           offsetof(b2Body, m_sleepTime),
           offsetof(b2Body, m_userData));
    printf("b2World: gravity=%zu\n", offsetof(b2World, m_gravity));
    return 0;
}
