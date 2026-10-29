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
#include <cstdarg>

#define private public
#define protected public
#include "Box2D.h"
#undef private
#undef protected

#include "b2physics.h"

// ---- 诊断：把访问违例的地址/模块/调用栈写进 B2PHYSICS_LOG ----
#ifndef B2_NO_VEH
#include <windows.h>
#endif
#ifndef B2_NO_VEH
static LONG CALLBACK VexHandler(PEXCEPTION_POINTERS p) {
    const char* path = std::getenv("B2PHYSICS_LOG");
    if (!path) return EXCEPTION_CONTINUE_SEARCH;
    if (p->ExceptionRecord->ExceptionCode != EXCEPTION_ACCESS_VIOLATION) return EXCEPTION_CONTINUE_SEARCH;
    if (FILE* f = std::fopen(path, "a")) {
        void* addr = p->ExceptionRecord->ExceptionAddress;
        HMODULE mod = nullptr;
        char name[MAX_PATH] = "?";
        if (GetModuleHandleExA(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS | GET_MODULE_HANDLE_EX_FLAG_UNCHANGED_REFCOUNT,
                               (LPCSTR)addr, &mod) && mod) {
            GetModuleFileNameA(mod, name, MAX_PATH);
        }
        std::fprintf(f, "AV at %p %s+0x%llx", addr, name,
                     (unsigned long long)(mod ? (char*)addr - (char*)mod : 0));
        if (p->ExceptionRecord->NumberParameters >= 2) {
            std::fprintf(f, " op=%llu target=%p",
                         (unsigned long long)p->ExceptionRecord->ExceptionInformation[0],
                         (void*)p->ExceptionRecord->ExceptionInformation[1]);
        }
        std::fprintf(f, "\n  stack:");
        DWORD* esp = (DWORD*)p->ContextRecord->Esp;
        for (int i = 0; i < 28; ++i) {
            void* ra = (void*)esp[i];
            HMODULE m2 = nullptr;
            char n2[MAX_PATH] = "?";
            if (GetModuleHandleExA(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS | GET_MODULE_HANDLE_EX_FLAG_UNCHANGED_REFCOUNT,
                                   (LPCSTR)ra, &m2) && m2) {
                GetModuleFileNameA(m2, n2, MAX_PATH);
                std::fprintf(f, " %s+0x%llx", n2, (unsigned long long)((char*)ra - (char*)m2));
            }
        }
        std::fputc('\n', f);
        std::fclose(f);
    }
    return EXCEPTION_CONTINUE_SEARCH;
}

BOOL WINAPI DllMain(HINSTANCE, DWORD reason, LPVOID) {
    if (reason == DLL_PROCESS_ATTACH && std::getenv("B2PHYSICS_LOG")) {
        AddVectoredExceptionHandler(1, VexHandler);
    }
    return TRUE;
}


#endif

namespace {

void TraceDetail(const char* fmt, ...) {
    const char* path = std::getenv("B2PHYSICS_LOG");
    if (!path) return;
    if (FILE* f = std::fopen(path, "a")) {
        va_list ap;
        va_start(ap, fmt);
        std::vfprintf(f, fmt, ap);
        va_end(ap);
        std::fputc('\n', f);
        std::fclose(f);
    }
}

void Trace(const char* n) {
    const char* path = std::getenv("B2PHYSICS_LOG");
    if (!path) return;
    if (FILE* f = std::fopen(path, "a")) {
        std::fprintf(f, "%s\n", n);
        std::fclose(f);
    }
}
#define TRACE(n) Trace(n)

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
    TRACE("b2_CreateWorld");
    b2Vec2 g = gravity ? V(*gravity) : b2Vec2(0.0f, -10.0f);
    b2AABB box = aabb ? *aabb : b2AABB();
    return new b2World(box, g, true);
}

B2API void b2_DestroyWorld(b2World* world) {
    TRACE("b2_DestroyWorld");
    if (!world) return;
    world->~b2World();
    ::operator delete(world);
}

// 调试：B2DBG_STEP=<body 指针 hex> 时，每步后打印该 body 的接触与冲量（定位"无外力却获得速度"用）
static const char* DbgEnv(const char* name) {
    static const char* cache[4] = {NULL, NULL, NULL, NULL};
    static const char* names[4] = {NULL, NULL, NULL, NULL};
    for (int i = 0; i < 4; ++i) {
        if (names[i] == name) return cache[i];
        if (!names[i]) { names[i] = name; cache[i] = getenv(name); return cache[i]; }
    }
    return getenv(name);
}

static void DbgPrint(const char* fmt, ...) {
    const char* path = DbgEnv("B2DBG_FILE");
    if (!path) path = "C:/tmp/Magnetic Adventure/work/b2dbg.txt";
    FILE* f = fopen(path, "a");
    if (!f) return;
    va_list ap;
    va_start(ap, fmt);
    vfprintf(f, fmt, ap);
    va_end(ap);
    fclose(f);
}

static bool DbgInWindow(int step) {
    static const int lo = DbgEnv("B2DBG_FROM") ? atoi(DbgEnv("B2DBG_FROM")) : 1;
    static const int hi = DbgEnv("B2DBG_TO") ? atoi(DbgEnv("B2DBG_TO")) : 5;
    return step >= lo && step <= hi;
}

static bool DbgAlive(b2World* world, b2Body* b) {
    for (b2Body* it = world->m_bodyList; it; it = it->m_next) if (it == b) return true;
    return false;
}

static void DbgJoints(b2Body* target, int stepNo, const char* when) {
    for (b2JointEdge* e = target->m_jointList; e; e = e->next) {
        b2Joint* j = e->joint;
        if (j->m_type == e_prismaticJoint) {
            b2PrismaticJoint* pj = static_cast<b2PrismaticJoint*>(j);
            DbgPrint("[dbg] step %d %s prismatic: trans=%.9f limits=[%.4f,%.4f] limitOn=%d "
                     "motorOn=%d speed=%.3f ax=(%.4f,%.4f)\n",
                     stepNo, when, pj->GetJointTranslation(), pj->GetLowerLimit(),
                     pj->GetUpperLimit(), (int)pj->IsLimitEnabled(), (int)pj->IsMotorEnabled(),
                     pj->GetMotorSpeed(), 0.0f, 0.0f);
        } else {
            DbgPrint("[dbg] step %d %s joint type=%d\n", stepNo, when, (int)j->m_type);
        }
    }
}

static void DbgOffsets() {
    static bool done = false;
    if (done) return;
    done = true;
    DbgPrint("[off] world.m_contactList=%d contact.next=%d contact.shape1=%d contact.shape2=%d "
             "contact.manifolds=%d shape.m_body=%d body.next=%d\n",
             (int)((char*)&((b2World*)0)->m_contactList - (char*)0),
             (int)((char*)&((b2Contact*)0)->m_next - (char*)0),
             (int)((char*)&((b2Contact*)0)->m_shape1 - (char*)0),
             (int)((char*)&((b2Contact*)0)->m_shape2 - (char*)0),
             (int)((char*)&((b2Contact*)0)->m_manifoldCount - (char*)0),
             (int)((char*)&((b2Shape*)0)->m_body - (char*)0),
             (int)((char*)&((b2Body*)0)->m_next - (char*)0));
}

// 导出整张接触表，供"接触拓扑对比"使用（F78）
static void DbgDumpContacts(b2World* world, int stepNo) {
    const char* path = DbgEnv("B2DBG_CONTACTS");
    if (!path || !*path) return;
    FILE* f = fopen(path, "a");
    if (!f) return;
    for (b2Contact* c = world->m_contactList; c; c = c->m_next)
        fprintf(f, "%d %u %u %d\n", stepNo,
                (unsigned)(uintptr_t)c->m_shape1, (unsigned)(uintptr_t)c->m_shape2,
                c->m_manifoldCount);
    fclose(f);
}

static void DbgContacts(b2World* world, b2Body* target, int stepNo) {
    int n = 0;
    DbgOffsets();
    for (b2Contact* c = world->m_contactList; c; c = c->m_next) {
        b2Body* b1 = c->m_shape1 ? c->m_shape1->m_body : NULL;
        b2Body* b2_ = c->m_shape2 ? c->m_shape2->m_body : NULL;
        if (b1 != target && b2_ != target) continue;
        b2Body* other = (b1 == target) ? b2_ : b1;
        ++n;
        DbgPrint("[dbg] step %d contact shapes(%p,%p) other=%p manifolds=%d\n",
               stepNo, (void*)c->m_shape1, (void*)c->m_shape2, (void*)other, c->m_manifoldCount);
        b2Manifold* mf = c->GetManifolds();
        for (int k = 0; k < c->m_manifoldCount; ++k) {
            DbgPrint("[dbg]   mf%d normal=(%.4f,%.4f) points=%d\n", k,
                   mf[k].normal.x, mf[k].normal.y, mf[k].pointCount);
            for (int i = 0; i < mf[k].pointCount; ++i)
                DbgPrint("[dbg]     p%d sep=%.6f nImp=%.6f tImp=%.6f\n", i,
                       mf[k].points[i].separation, mf[k].points[i].normalImpulse,
                       mf[k].points[i].tangentImpulse);
        }
    }
    if (!n) DbgPrint("[dbg] step %d no contacts for %p\n", stepNo, (void*)target);
}

#ifndef B2_NO_VEH
#include <float.h>
#include <xmmintrin.h>
#endif

// 实验：B2_FPU=ftz|dbl|ext 强制设置浮点环境（对齐游戏进程的 FPU/MXCSR 状态）
static void ApplyFpuEnv() {
    static bool done = false;
    if (done) return;
    done = true;
    const char* m = getenv("B2_FPU");
    if (!m) return;
    unsigned int mx = _mm_getcsr();
    if (!strcmp(m, "ftz")) {          // 打开 FTZ+DAZ，x87 精度=double
        mx |= 0x8040;
        _controlfp(_PC_53, _MCW_PC);
    } else if (!strcmp(m, "dbl")) {   // 只改 x87 精度
        _controlfp(_PC_53, _MCW_PC);
    } else if (!strcmp(m, "ext")) {
        _controlfp(_PC_64, _MCW_PC);
    }
    _mm_setcsr(mx);
}

B2API void b2_World_Step(b2World* world, float dt, int velocityIterations, int positionIterations) {
    TRACE("b2_World_Step");
    ApplyFpuEnv();

    static int s_step = 0;
    ++s_step;
    const char* dbg = DbgEnv("B2DBG_STEP");
    if (dbg && !*dbg) dbg = NULL;
    // B2DBG_POS="x,y" 按坐标找 body（重放里原版指针与我们的地址不同）
    static b2Body* s_dbg_target = NULL;   // 按坐标锁定一次，之后黏住（body 会移动）
    b2Body* target = s_dbg_target;
    if (dbg && !target) {
        float tx = 0.0f, ty = 0.0f;
        if (sscanf(dbg, "%f,%f", &tx, &ty) == 2) {
            for (b2Body* b = world->m_bodyList; b; b = b->m_next) {
                float dx = b->m_xf.position.x - tx, dy = b->m_xf.position.y - ty;
                if (dx * dx + dy * dy < 1e-4f) { target = b; s_dbg_target = b; break; }
            }
        } else {
            target = (b2Body*)(uintptr_t)strtoul(dbg, NULL, 16);
        }
    }
    if (target && !DbgAlive(world, target)) target = NULL;   // 已销毁的 body 不能解引用
    if (target && DbgInWindow(s_step)) {
        DbgPrint("[dbg] step %d before: type=%d flags=%#x shapes=%p v=(%.4f,%.4f) w=%.4f grav=(%.4f,%.4f) mass=%.4f lc=(%.9f,%.9f) p=(%.9f,%.9f)\n",
               s_step, (int)target->m_type, (unsigned)target->m_flags, (void*)target->m_shapeList,
               target->m_linearVelocity.x, target->m_linearVelocity.y, target->m_angularVelocity,
               world->m_gravity.x, world->m_gravity.y, target->m_mass,
               target->m_sweep.localCenter.x, target->m_sweep.localCenter.y,
               target->m_xf.position.x, target->m_xf.position.y);
        DbgJoints(target, s_step, "before");
    }
    world->Step(dt, velocityIterations, positionIterations);
    DbgDumpContacts(world, s_step);
    if (target && DbgInWindow(s_step) && DbgAlive(world, target)) {
        DbgJoints(target, s_step, "after");
        DbgContacts(world, target, s_step);
        DbgPrint("[dbg] step %d after: v=(%.4f,%.4f) w=%.4f\n", s_step,
               target->m_linearVelocity.x, target->m_linearVelocity.y, target->m_angularVelocity);
    }
}

B2API void b2_World_SetGravity(b2World* world, const B2Vec2C* gravity) {
    TRACE("b2_World_SetGravity");
    world->m_gravity = V(*gravity);
}

B2API void b2_World_ReFilter(b2Shape* shape) {
    TRACE("b2_World_ReFilter");
    // 名字有误导：宿主传的是 shape（game.exe: for (s=GetShapeList(obj)); s; s=Shape_GetNext(s)) World_ReFilter(s)
    if (!shape || !shape->m_body) return;
    b2World* world = shape->m_body->m_world;
    if (world) world->Refilter(shape);
}

// ---------------------------------------------------------------- 宿主回调适配
// 原 DLL（0x10001370/0x10001390）收到的是**裸函数指针**：存进全局，并往 world 上挂一个
// 自带的静态适配对象。适配对象把 b2ContactPoint 翻译成宿主认识的 9 个 dword：
//   { shape1, shape2, pos.x, pos.y, normal.x, normal.y, ud1, ud2, type }
// type: 0=Add 1=Persist 2=Remove（Result 不转发，原 DLL 的 vtable 第 5 项是空函数）。
// 直接把函数指针当 b2ContactListener* 交给 Box2D，Box2D 会按 vtable 取 [0] 当函数调，
// 那里是函数首字节 → 跳飞（lvl_o20 的 Access violation 就是这个）。
struct B2ContactRecC {
    b2Shape* shape1;
    b2Shape* shape2;
    float posX, posY;
    float normalX, normalY;
    void* userData1;
    void* userData2;
    int type;
};

static void* g_contactCb = nullptr;
static void* g_filterCb = nullptr;

class HostListenerC : public b2ContactListener {
public:
    void Add(const b2ContactPoint* p) override { Dispatch(p, 0); }
    void Persist(const b2ContactPoint* p) override { Dispatch(p, 1); }
    void Remove(const b2ContactPoint* p) override { Dispatch(p, 2); }

private:
    static void Dispatch(const b2ContactPoint* p, int type) {
        if (!g_contactCb) return;
        const float* f = (const float*)p;
        B2ContactRecC rec;
        rec.shape1 = p->shape1;
        rec.shape2 = p->shape2;
        rec.posX = f[2];
        rec.posY = f[3];
        rec.normalX = f[6];
        rec.normalY = f[7];
        rec.userData1 = p->shape1->m_body->m_userData;
        rec.userData2 = p->shape2->m_body->m_userData;
        rec.type = type;
        ((void(__cdecl*)(B2ContactRecC*))g_contactCb)(&rec);
    }
};
static HostListenerC g_hostListener;

class HostFilterC : public b2ContactFilter {
public:
    bool ShouldCollide(b2Shape* s1, b2Shape* s2) override {
        if (!g_filterCb) return b2ContactFilter::ShouldCollide(s1, s2);
        void* rec[4] = {s1, s2, s1->m_body->m_userData, s2->m_body->m_userData};
        return ((bool(__cdecl*)(void**))g_filterCb)(rec);
    }
};
static HostFilterC g_hostFilter;

B2API void b2_World_SetContactFilterCallBack(b2World* world, void* cb) {
    TRACE("b2_World_SetContactFilterCallBack");
    g_filterCb = cb;
    world->SetContactFilter(&g_hostFilter);
}


B2API void b2_World_SetContactListenerCallBack(b2World* world, void* cb) {
    TRACE("b2_World_SetContactListenerCallBack");
    g_contactCb = cb;
    world->SetContactListener(&g_hostListener);   // 原 DLL 无条件挂适配对象
}

B2API void* b2_World_CreateBody(const B2BodyDefC* d) {
    TRACE("b2_World_CreateBody");
    b2BodyDef def;  // 默认构造：massData 0、position 0、allowSleep=true
    def.angularDamping = d->angularDamping;
    def.linearDamping = d->linearDamping;
    def.allowSleep = d->allowSleep != 0;
    def.fixedRotation = d->fixedRotation != 0;
    def.isBullet = d->isBullet != 0;
    return d->world->CreateBody(&def);
}

B2API void b2_World_DestroyBody(b2World* world, b2Body* body) {
    TRACE("b2_World_DestroyBody");
    (void)world;  // 原 DLL 只用 body 自身
    body->m_world->DestroyBody(body);
}

// 实测（FFI 抓包）：宿主传的是 (world, joint) —— arg0 与 CreateBody def 里的 world 相同。
// 之前按 (joint) 实现，从未被调用过；totem 关第一次销毁关节就崩在 world 当 joint 解引用。
B2API void b2_World_DestroyJoint(b2World* world, b2Joint* joint) {
    TRACE("b2_World_DestroyJoint");
    world->DestroyJoint(joint);
}

B2API void b2_World_ClearJoints(b2World* world) {
    TRACE("b2_World_ClearJoints");
    while (world->m_jointList) {
        world->DestroyJoint(world->m_jointList);
    }
}

B2API int b2_GetMaxPolygonVertices(void) {
    TRACE("b2_GetMaxPolygonVertices"); return 8; }

// ---------------------------------------------------------------- Body

B2API void b2_Body_ApplyForce(b2Body* body, const float* force, const float* point) {
    TRACE("b2_Body_ApplyForce");
    body->ApplyForce(V(force), V(point));
}

B2API void b2_Body_ApplyImpulse(b2Body* body, const float* impulse, const float* point) {
    TRACE("b2_Body_ApplyImpulse");
    body->ApplyImpulse(V(impulse), V(point));
}

B2API void b2_Body_ApplyTorque(b2Body* body, float torque) {
    TRACE("b2_Body_ApplyTorque");
    if (body->m_flags & b2Body::e_sleepFlag) Wake(body);
    body->m_force.y += 0.0f;  // 保持与原实现相同的分支形状
    body->m_torque += torque;
}

B2API void b2_Body_ClearShapes(b2Body* body) {
    TRACE("b2_Body_ClearShapes");
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
    TRACE("b2_Body_CreateShape_Box");
    b2PolygonDef def;
    FillShapeCommon(&def, d);
    def.SetAsBox(d->c, d->d, b2Vec2(d->a, d->b), 0.0f);  // +28/+32 半宽高，+20/+24 中心
    return d->body->CreateShape(&def);
}

B2API void* b2_Body_CreateShape_Circle(const B2ShapeDefC* d) {
    TRACE("b2_Body_CreateShape_Circle");
    b2CircleDef def;
    FillShapeCommon(&def, d);
    def.localPosition.Set(d->a, d->b);  // +20/+24
    def.radius = d->c;                 // +28
    TraceDetail("circle r=%.4f pos=(%.3f,%.3f) dens=%.3f", def.radius, d->a, d->b, d->density);
    return d->body->CreateShape(&def);
}

B2API void* b2_Body_CreateShape_Polygon(const B2ShapeDefC* dp) {
    TRACE("b2_Body_CreateShape_Polygon");
    // 多边形专用布局：+16 之后是 int32 vertexCount(+20)，顶点从 +24 开始（每点 8 字节）
    struct PolyDefC {
        b2Body* body;
        float friction, restitution, density;
        void* userData;
        int vertexCount;
        float vertices[2 * 8];
    };
    const PolyDefC* d = (const PolyDefC*)dp;
    b2PolygonDef def;
    FillShapeCommon(&def, dp);
    int count = d->vertexCount;
    if (count < 3) {
        TraceDetail("poly count=%d <3", count);
        return nullptr;
    }
    if (count > b2_maxPolygonVertices) count = b2_maxPolygonVertices;
    def.vertexCount = count;
    for (int i = 0; i < count; ++i) {
        def.vertices[i].Set(d->vertices[2 * i], d->vertices[2 * i + 1]);
    }
    TraceDetail("poly n=%d v0=(%.3f,%.3f) v1=(%.3f,%.3f) dens=%.3f", count,
                d->vertices[0], d->vertices[1], d->vertices[2], d->vertices[3], dp->density);
    b2Shape* sh = d->body->CreateShape(&def);
    TraceDetail("poly -> %p", (void*)sh);
    return sh;
}

B2API void b2_Body_DestroyShape(b2Shape* shape) {
    TRACE("b2_Body_DestroyShape"); shape->m_body->DestroyShape(shape); }

B2API float b2_Body_GetAngle(b2Body* body) {
    TRACE("b2_Body_GetAngle"); return body->m_sweep.a; }

B2API float b2_Body_GetAngularDamping(b2Body* body) {
    TRACE("b2_Body_GetAngularDamping"); return body->m_angularDamping; }

B2API int b2_Body_GetIsSleeping(b2Body* body) {
    TRACE("b2_Body_GetIsSleeping");
    return (body->m_flags & b2Body::e_sleepFlag) ? 1 : 0;
}

B2API void* b2_Body_GetLocalPoint(void* out, b2Body* body, const float* p) {
    TRACE("b2_Body_GetLocalPoint");
    *(b2Vec2*)out = body->GetLocalPoint(V(p));
    return out;
}

B2API void* b2_Body_GetLocalVector(void* out, b2Body* body, const float* v) {
    TRACE("b2_Body_GetLocalVector");
    *(b2Vec2*)out = body->GetLocalVector(V(v));
    return out;
}

B2API void b2_Body_GetMass(b2Body* body, B2MassDataC* out) {
    TRACE("b2_Body_GetMass");
    out->mass = body->m_mass;
    out->cx = body->m_sweep.c.x;
    out->cy = body->m_sweep.c.y;
    out->I = body->m_I;
}

B2API float b2_Body_GetOmega(b2Body* body) {
    TRACE("b2_Body_GetOmega"); return body->m_angularVelocity; }

B2API void* b2_Body_GetPosition(void* out, b2Body* body) {
    TRACE("b2_Body_GetPosition");
    Out((B2Vec2C*)out, body->m_xf.position);
    return out;
}

B2API void* b2_Body_GetShapeList(b2Body* body) {
    TRACE("b2_Body_GetShapeList"); return body->m_shapeList; }

B2API void* b2_Body_GetUserData(b2Body* body) {
    TRACE("b2_Body_GetUserData"); return body->m_userData; }

B2API void* b2_Body_GetVelocity(void* out, b2Body* body) {
    TRACE("b2_Body_GetVelocity");
    Out((B2Vec2C*)out, body->m_linearVelocity);
    return out;
}

B2API void* b2_Body_GetWorld(b2Body* body) {
    TRACE("b2_Body_GetWorld"); return body->m_world; }

B2API void* b2_Body_GetWorldPoint(void* out, b2Body* body, const float* p) {
    TRACE("b2_Body_GetWorldPoint");
    *(b2Vec2*)out = body->GetWorldPoint(V(p));
    return out;
}

B2API void* b2_Body_GetWorldVector(void* out, b2Body* body, const float* v) {
    TRACE("b2_Body_GetWorldVector");
    *(b2Vec2*)out = body->GetWorldVector(V(v));
    return out;
}

B2API void* b2_Body_GetXForm(b2Body* body, B2XFormC* out) {
    TRACE("b2_Body_GetXForm");
    out->x = body->m_xf.position.x;
    out->y = body->m_xf.position.y;
    out->angle = body->m_sweep.a;
    return body;
}

B2API int b2_Body_IsBullet(b2Body* body) {
    TRACE("b2_Body_IsBullet");
    return (body->m_flags & b2Body::e_bulletFlag) ? 1 : 0;
}

B2API int b2_Body_IsFrozen(b2Body* body) {
    TRACE("b2_Body_IsFrozen");
    return (body->m_flags & b2Body::e_frozenFlag) ? 1 : 0;
}

B2API void b2_Body_PutToSleep(b2Body* body) {
    TRACE("b2_Body_PutToSleep");
    body->m_flags |= b2Body::e_sleepFlag;
    body->m_sleepTime = 0.0f;
    body->m_linearVelocity.SetZero();
    body->m_angularVelocity = 0.0f;
    body->m_force.SetZero();
    body->m_torque = 0.0f;
}

B2API void b2_Body_SetAngularDamping(b2Body* body, float d) {
    TRACE("b2_Body_SetAngularDamping"); body->m_angularDamping = d; }

B2API void b2_Body_SetBullet(b2Body* body, int flag) {
    TRACE("b2_Body_SetBullet");
    if (flag)
        body->m_flags |= b2Body::e_bulletFlag;
    else
        body->m_flags &= ~b2Body::e_bulletFlag;
}

B2API void b2_Body_SetMass(b2Body* body, const B2MassDataC* md) {
    TRACE("b2_Body_SetMass"); body->SetMass((const b2MassData*)md); }

B2API void b2_Body_SetMassFromShapes(b2Body* body) {
    TRACE("b2_Body_SetMassFromShapes"); body->SetMassFromShapes(); }

B2API void b2_Body_SetOmega(b2Body* body, float omega) {
    TRACE("b2_Body_SetOmega");
    body->m_flags &= ~b2Body::e_sleepFlag;
    body->m_sleepTime = 0.0f;
    body->m_angularVelocity = omega;
}

B2API void* b2_Body_SetUserData(b2Body* body, void* data) {
    TRACE("b2_Body_SetUserData");
    body->m_userData = data;
    return data;
}

B2API void b2_Body_SetVelocity(b2Body* body, const float* v) {
    TRACE("b2_Body_SetVelocity");
    body->m_flags &= ~b2Body::e_sleepFlag;
    body->m_sleepTime = 0.0f;
    body->m_linearVelocity = V(v);
}

// 原 DLL 直接转调 b2Body::SetXForm（反编译 0x10003560）：除了 m_xf/m_sweep 还要
// 重算 sweep.c(=pos+R*localCenter)、c0/a0、同步 broadphase proxy 并 Commit，
// 越界时置 frozen 并销毁 proxy。手写字段会漏掉这些，导致出参与速度漂移。
B2API void b2_Body_SetXForm(b2Body* body, const B2XFormC* xf) {
    TRACE("b2_Body_SetXForm");
    body->SetXForm(b2Vec2(xf->x, xf->y), xf->angle);
}

B2API void b2_Body_WakeUp(b2Body* body) {
    TRACE("b2_Body_WakeUp");
    body->m_sleepTime = 0.0f;
    body->m_flags &= ~b2Body::e_sleepFlag;
}

// ---------------------------------------------------------------- Shape

B2API void* b2_Shape_GetBody(b2Shape* shape) {
    TRACE("b2_Shape_GetBody"); return shape->m_body; }

B2API void* b2_Shape_GetNext(b2Shape* shape) {
    TRACE("b2_Shape_GetNext"); return shape->m_next; }

B2API int b2_Shape_GetShapeType(b2Shape* shape) {
    TRACE("b2_Shape_GetShapeType");
    switch (shape->m_type) {
        case e_unknownShape: return 0;
        case e_circleShape: return 1;
        case e_polygonShape: return 2;
        default: return -1;
    }
}

B2API float b2_Shape_GetDensity(b2Shape* shape) {
    TRACE("b2_Shape_GetDensity"); return shape->m_density; }
B2API float b2_Shape_GetFriction(b2Shape* shape) {
    TRACE("b2_Shape_GetFriction"); return shape->m_friction; }
B2API float b2_Shape_GetRestitution(b2Shape* shape) {
    TRACE("b2_Shape_GetRestitution"); return shape->m_restitution; }
B2API int b2_Shape_GetSensor(b2Shape* shape) {
    TRACE("b2_Shape_GetSensor"); return shape->m_isSensor ? 1 : 0; }

B2API void b2_Shape_SetDensity(b2Shape* shape, float v) {
    TRACE("b2_Shape_SetDensity"); shape->m_density = v; }
B2API void b2_Shape_SetFriction(b2Shape* shape, float v) {
    TRACE("b2_Shape_SetFriction"); shape->m_friction = v; }
B2API void b2_Shape_SetRestitution(b2Shape* shape, float v) {
    TRACE("b2_Shape_SetRestitution"); shape->m_restitution = v; }
B2API int b2_Shape_SetSensor(b2Shape* shape, int v) {
    TRACE("b2_Shape_SetSensor"); shape->m_isSensor = v != 0; return v; }

B2API void* b2_Shape_GetFilter(b2Shape* shape, B2FilterC* out) {
    TRACE("b2_Shape_GetFilter");
    out->category = shape->m_filter.categoryBits;
    out->mask = shape->m_filter.maskBits;
    out->group = shape->m_filter.groupIndex;
    return out;
}

B2API void* b2_Shape_SetFilter(b2Shape* shape, const B2FilterC* f) {
    TRACE("b2_Shape_SetFilter");
    shape->m_filter.categoryBits = f->category;
    shape->m_filter.maskBits = f->mask;
    shape->m_filter.groupIndex = f->group;
    return shape;
}

B2API void* b2_Shape_GetCirclePos(void* out, b2Shape* shape) {
    TRACE("b2_Shape_GetCirclePos");
    if (shape->m_type != e_circleShape) {
        ((float*)out)[0] = ((float*)out)[1] = 0.0f;
        return out;
    }
    Out((B2Vec2C*)out, ((b2CircleShape*)shape)->m_localPosition);
    return out;
}

B2API float b2_Shape_GetCircleRadius(b2Shape* shape) {
    TRACE("b2_Shape_GetCircleRadius");
    if (shape->m_type != e_circleShape) return 0.0f;
    return ((b2CircleShape*)shape)->m_radius;
}

B2API int b2_Shape_TestPoint(b2Shape* shape, const B2XFormC* xf, const float* p) {
    TRACE("b2_Shape_TestPoint");
    b2XForm f;
    f.position.Set(xf->x, xf->y);
    f.R.Set(xf->angle);
    return shape->TestPoint(f, V(p)) ? 1 : 0;
}

// ---------------------------------------------------------------- Joints

// 工厂：输入布局见 docs/facts.md F34
B2API void* b2_World_Joint_Distance(const B2DistanceJointC* d) {
    TRACE("b2_World_Joint_Distance");
    b2DistanceJointDef def;
    def.Initialize(d->body1, d->body2, V(d->anchor1), V(d->anchor2));
    def.collideConnected = d->collide != 0;
    return d->world->CreateJoint(&def);
}

B2API void* b2_World_Joint_Revolute(const B2RevoluteJointC* d) {
    TRACE("b2_World_Joint_Revolute");
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
    TRACE("b2_World_Joint_Prismatic");
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
    TRACE("b2_World_Joint_Gear");
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
    TRACE("b2_World_Joint_Pulley");
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
    TRACE("b2_Joint_EnableLimit");
    switch (j->m_type) {
        case e_revoluteJoint: As<b2RevoluteJoint>(j)->EnableLimit(enable != 0); break;
        case e_prismaticJoint: As<b2PrismaticJoint>(j)->EnableLimit(enable != 0); break;
        default: break;
    }
}

B2API void b2_Joint_EnableMotor(b2Joint* j, int enable) {
    TRACE("b2_Joint_EnableMotor");
    switch (j->m_type) {
        case e_revoluteJoint: As<b2RevoluteJoint>(j)->EnableMotor(enable != 0); break;
        case e_prismaticJoint: As<b2PrismaticJoint>(j)->EnableMotor(enable != 0); break;
        default: break;
    }
}

B2API void* b2_Joint_GetAnchor1(void* out, b2Joint* j) {
    TRACE("b2_Joint_GetAnchor1");
    *(b2Vec2*)out = j->GetAnchor1();
    return out;
}

B2API void* b2_Joint_GetAnchor2(void* out, b2Joint* j) {
    TRACE("b2_Joint_GetAnchor2");
    *(b2Vec2*)out = j->GetAnchor2();
    return out;
}

B2API void* b2_Joint_GetBody1(b2Joint* j) {
    TRACE("b2_Joint_GetBody1"); return j->m_body1; }
B2API void* b2_Joint_GetBody2(b2Joint* j) {
    TRACE("b2_Joint_GetBody2"); return j->m_body2; }

B2API float b2_Joint_GetJointAngle(b2Joint* j) {
    TRACE("b2_Joint_GetJointAngle");
    if (j->m_type != e_revoluteJoint) return 0.0f;
    return As<b2RevoluteJoint>(j)->GetJointAngle();
}

B2API float b2_Joint_GetJointTranslation(b2Joint* j) {
    TRACE("b2_Joint_GetJointTranslation");
    if (j->m_type != e_prismaticJoint) return 0.0f;
    return As<b2PrismaticJoint>(j)->GetJointTranslation();
}

B2API int b2_Joint_GetJointType(b2Joint* j) {
    TRACE("b2_Joint_GetJointType");
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
    TRACE("b2_Joint_GetLimits");
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
    TRACE("b2_Joint_GetMotorSpeed");
    switch (j->m_type) {
        case e_revoluteJoint: return As<b2RevoluteJoint>(j)->GetMotorSpeed();
        case e_prismaticJoint: return As<b2PrismaticJoint>(j)->GetMotorSpeed();
        default: return 0.0f;
    }
}

B2API void* b2_Joint_GetReactionImpulse(void* out, b2Joint* j) {
    TRACE("b2_Joint_GetReactionImpulse");
    *(b2Vec2*)out = j->GetReactionForce(1.0f);
    return out;
}

B2API float b2_Joint_GetReactionTorqImpulse(b2Joint* j) {
    TRACE("b2_Joint_GetReactionTorqImpulse"); return j->GetReactionTorque(1.0f); }

B2API int b2_Joint_IsLimitEnabled(b2Joint* j) {
    TRACE("b2_Joint_IsLimitEnabled");
    switch (j->m_type) {
        case e_revoluteJoint: return As<b2RevoluteJoint>(j)->IsLimitEnabled() ? 1 : 0;
        case e_prismaticJoint: return As<b2PrismaticJoint>(j)->IsLimitEnabled() ? 1 : 0;
        default: return 0;
    }
}

B2API int b2_Joint_IsMotorEnabled(b2Joint* j) {
    TRACE("b2_Joint_IsMotorEnabled");
    switch (j->m_type) {
        case e_revoluteJoint: return As<b2RevoluteJoint>(j)->IsMotorEnabled() ? 1 : 0;
        case e_prismaticJoint: return As<b2PrismaticJoint>(j)->IsMotorEnabled() ? 1 : 0;
        default: return 0;
    }
}

B2API void b2_Joint_SetLimits(b2Joint* j, float lower, float upper) {
    TRACE("b2_Joint_SetLimits");
    switch (j->m_type) {
        case e_revoluteJoint: As<b2RevoluteJoint>(j)->SetLimits(lower, upper); break;
        case e_prismaticJoint: As<b2PrismaticJoint>(j)->SetLimits(lower, upper); break;
        default: break;
    }
}

B2API void b2_Joint_SetMaxMotorForce(b2Joint* j, float force) {
    TRACE("b2_Joint_SetMaxMotorForce");
    if (j->m_type == e_prismaticJoint) As<b2PrismaticJoint>(j)->SetMaxMotorForce(force);
}

B2API void b2_Joint_SetMaxMotorTorque(b2Joint* j, float torque) {
    TRACE("b2_Joint_SetMaxMotorTorque");
    if (j->m_type == e_revoluteJoint) As<b2RevoluteJoint>(j)->SetMaxMotorTorque(torque);
}

B2API void b2_Joint_SetMotorSpeed(b2Joint* j, float speed) {
    TRACE("b2_Joint_SetMotorSpeed");
    switch (j->m_type) {
        case e_revoluteJoint: As<b2RevoluteJoint>(j)->SetMotorSpeed(speed); break;
        case e_prismaticJoint: As<b2PrismaticJoint>(j)->SetMotorSpeed(speed); break;
        default: break;
    }
}
