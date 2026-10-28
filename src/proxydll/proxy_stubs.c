/* 生成文件，勿手改：python tools/gen_proxy.py
 * 依据：docs/facts.md F35（87 个导出/序号）、F31（check_exports 零差异） */
#include <windows.h>
#include <stdint.h>

extern FARPROC g_slot[];
void __cdecl log_call(unsigned id, uint32_t esp0, uint32_t edx, uint32_t ecx);

const int g_n_exports = 88;
const char* const g_names[] = {
    "",  /* 0 号占位 */
    "b2_Body_ApplyForce",
    "b2_Body_ApplyImpulse",
    "b2_Body_ApplyTorque",
    "b2_Body_ClearShapes",
    "b2_Body_CreateShape_Box",
    "b2_Body_CreateShape_Circle",
    "b2_Body_CreateShape_Polygon",
    "b2_Body_DestroyShape",
    "b2_Body_GetAngle",
    "b2_Body_GetAngularDamping",
    "b2_Body_GetIsSleeping",
    "b2_Body_GetLocalPoint",
    "b2_Body_GetLocalVector",
    "b2_Body_GetMass",
    "b2_Body_GetOmega",
    "b2_Body_GetPosition",
    "b2_Body_GetShapeList",
    "b2_Body_GetUserData",
    "b2_Body_GetVelocity",
    "b2_Body_GetWorld",
    "b2_Body_GetWorldPoint",
    "b2_Body_GetWorldVector",
    "b2_Body_GetXForm",
    "b2_Body_IsBullet",
    "b2_Body_IsFrozen",
    "b2_Body_PutToSleep",
    "b2_Body_SetAngularDamping",
    "b2_Body_SetBullet",
    "b2_Body_SetMass",
    "b2_Body_SetMassFromShapes",
    "b2_Body_SetOmega",
    "b2_Body_SetUserData",
    "b2_Body_SetVelocity",
    "b2_Body_SetXForm",
    "b2_Body_WakeUp",
    "b2_CreateWorld",
    "b2_DestroyWorld",
    "b2_GetMaxPolygonVertices",
    "b2_Joint_EnableLimit",
    "b2_Joint_EnableMotor",
    "b2_Joint_GetAnchor1",
    "b2_Joint_GetAnchor2",
    "b2_Joint_GetBody1",
    "b2_Joint_GetBody2",
    "b2_Joint_GetJointAngle",
    "b2_Joint_GetJointTranslation",
    "b2_Joint_GetJointType",
    "b2_Joint_GetLimits",
    "b2_Joint_GetMotorSpeed",
    "b2_Joint_GetReactionImpulse",
    "b2_Joint_GetReactionTorqImpulse",
    "b2_Joint_IsLimitEnabled",
    "b2_Joint_IsMotorEnabled",
    "b2_Joint_SetLimits",
    "b2_Joint_SetMaxMotorForce",
    "b2_Joint_SetMaxMotorTorque",
    "b2_Joint_SetMotorSpeed",
    "b2_Shape_GetBody",
    "b2_Shape_GetCirclePos",
    "b2_Shape_GetCircleRadius",
    "b2_Shape_GetDensity",
    "b2_Shape_GetFilter",
    "b2_Shape_GetFriction",
    "b2_Shape_GetNext",
    "b2_Shape_GetRestitution",
    "b2_Shape_GetSensor",
    "b2_Shape_GetShapeType",
    "b2_Shape_SetDensity",
    "b2_Shape_SetFilter",
    "b2_Shape_SetFriction",
    "b2_Shape_SetRestitution",
    "b2_Shape_SetSensor",
    "b2_Shape_TestPoint",
    "b2_World_ClearJoints",
    "b2_World_CreateBody",
    "b2_World_DestroyBody",
    "b2_World_DestroyJoint",
    "b2_World_Joint_Distance",
    "b2_World_Joint_Gear",
    "b2_World_Joint_Prismatic",
    "b2_World_Joint_Pulley",
    "b2_World_Joint_Revolute",
    "b2_World_ReFilter",
    "b2_World_SetContactFilterCallBack",
    "b2_World_SetContactListenerCallBack",
    "b2_World_SetGravity",
    "b2_World_Step",
    0,
};

FARPROC g_slot[89] = {0};

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
        jmp  dword ptr [g_slot+4]
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
        jmp  dword ptr [g_slot+8]
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
        jmp  dword ptr [g_slot+12]
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
        jmp  dword ptr [g_slot+16]
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
        jmp  dword ptr [g_slot+20]
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
        jmp  dword ptr [g_slot+24]
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
        jmp  dword ptr [g_slot+28]
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
        jmp  dword ptr [g_slot+32]
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
        jmp  dword ptr [g_slot+36]
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
        jmp  dword ptr [g_slot+40]
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
        jmp  dword ptr [g_slot+44]
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
        jmp  dword ptr [g_slot+48]
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
        jmp  dword ptr [g_slot+52]
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
        jmp  dword ptr [g_slot+56]
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
        jmp  dword ptr [g_slot+60]
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
        jmp  dword ptr [g_slot+64]
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
        jmp  dword ptr [g_slot+68]
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
        jmp  dword ptr [g_slot+72]
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
        jmp  dword ptr [g_slot+76]
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
        jmp  dword ptr [g_slot+80]
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
        jmp  dword ptr [g_slot+84]
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
        jmp  dword ptr [g_slot+88]
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
        jmp  dword ptr [g_slot+92]
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
        jmp  dword ptr [g_slot+96]
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
        jmp  dword ptr [g_slot+100]
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
        jmp  dword ptr [g_slot+104]
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
        jmp  dword ptr [g_slot+108]
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
        jmp  dword ptr [g_slot+112]
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
        jmp  dword ptr [g_slot+116]
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
        jmp  dword ptr [g_slot+120]
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
        jmp  dword ptr [g_slot+124]
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
        jmp  dword ptr [g_slot+128]
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
        jmp  dword ptr [g_slot+132]
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
        jmp  dword ptr [g_slot+136]
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
        jmp  dword ptr [g_slot+140]
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
        jmp  dword ptr [g_slot+144]
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
        jmp  dword ptr [g_slot+148]
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
        jmp  dword ptr [g_slot+152]
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
        jmp  dword ptr [g_slot+156]
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
        jmp  dword ptr [g_slot+160]
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
        jmp  dword ptr [g_slot+164]
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
        jmp  dword ptr [g_slot+168]
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
        jmp  dword ptr [g_slot+172]
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
        jmp  dword ptr [g_slot+176]
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
        jmp  dword ptr [g_slot+180]
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
        jmp  dword ptr [g_slot+184]
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
        jmp  dword ptr [g_slot+188]
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
        jmp  dword ptr [g_slot+192]
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
        jmp  dword ptr [g_slot+196]
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
        jmp  dword ptr [g_slot+200]
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
        jmp  dword ptr [g_slot+204]
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
        jmp  dword ptr [g_slot+208]
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
        jmp  dword ptr [g_slot+212]
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
        jmp  dword ptr [g_slot+216]
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
        jmp  dword ptr [g_slot+220]
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
        jmp  dword ptr [g_slot+224]
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
        jmp  dword ptr [g_slot+228]
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
        jmp  dword ptr [g_slot+232]
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
        jmp  dword ptr [g_slot+236]
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
        jmp  dword ptr [g_slot+240]
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
        jmp  dword ptr [g_slot+244]
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
        jmp  dword ptr [g_slot+248]
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
        jmp  dword ptr [g_slot+252]
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
        jmp  dword ptr [g_slot+256]
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
        jmp  dword ptr [g_slot+260]
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
        jmp  dword ptr [g_slot+264]
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
        jmp  dword ptr [g_slot+268]
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
        jmp  dword ptr [g_slot+272]
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
        jmp  dword ptr [g_slot+276]
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
        jmp  dword ptr [g_slot+280]
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
        jmp  dword ptr [g_slot+284]
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
        jmp  dword ptr [g_slot+288]
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
        jmp  dword ptr [g_slot+292]
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
        jmp  dword ptr [g_slot+296]
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
        jmp  dword ptr [g_slot+300]
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
        jmp  dword ptr [g_slot+304]
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
        jmp  dword ptr [g_slot+308]
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
        jmp  dword ptr [g_slot+312]
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
        jmp  dword ptr [g_slot+316]
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
        jmp  dword ptr [g_slot+320]
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
        jmp  dword ptr [g_slot+324]
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
        jmp  dword ptr [g_slot+328]
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
        jmp  dword ptr [g_slot+332]
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
        jmp  dword ptr [g_slot+336]
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
        jmp  dword ptr [g_slot+340]
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
        jmp  dword ptr [g_slot+344]
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
        jmp  dword ptr [g_slot+348]
    }
}
