/* 生成文件，勿手改：python tools/gen_proxy.py
 * 依据：docs/facts.md F35/F131（导出清单与序号） */
#include <windows.h>
#include <stdint.h>

extern FARPROC g_slot[];
void __cdecl log_call(unsigned id, uint32_t esp0, uint32_t edx, uint32_t ecx);
void __cdecl save_ret(unsigned id, uint32_t orig_ret);
uint32_t __cdecl finish_call(unsigned id, uint32_t retval, uint32_t args_ptr);
uint32_t __cdecl get_ret(void);

const int g_n_exports = 100;
const char* const g_names[] = {
    "",  /* 0 号占位 */
    "SQUALL_ChannelGroup_Pause",
    "SQUALL_ChannelGroup_SetFrequency",
    "SQUALL_ChannelGroup_SetVolume",
    "SQUALL_ChannelGroup_Stop",
    "SQUALL_Channel_EAX_GetProperties",
    "SQUALL_Channel_EAX_SetProperties",
    "SQUALL_Channel_Get3DPosition",
    "SQUALL_Channel_GetConeParameters",
    "SQUALL_Channel_GetFragment",
    "SQUALL_Channel_GetFragmentMs",
    "SQUALL_Channel_GetFrequency",
    "SQUALL_Channel_GetLength",
    "SQUALL_Channel_GetLengthMs",
    "SQUALL_Channel_GetLoop",
    "SQUALL_Channel_GetMinMaxDistance",
    "SQUALL_Channel_GetPan",
    "SQUALL_Channel_GetPlayPosition",
    "SQUALL_Channel_GetPlayPositionMs",
    "SQUALL_Channel_GetPriority",
    "SQUALL_Channel_GetVelocity",
    "SQUALL_Channel_GetVolume",
    "SQUALL_Channel_Pause",
    "SQUALL_Channel_Set3DPosition",
    "SQUALL_Channel_SetConeParameters",
    "SQUALL_Channel_SetEndWorker",
    "SQUALL_Channel_SetFragment",
    "SQUALL_Channel_SetFragmentMs",
    "SQUALL_Channel_SetFrequency",
    "SQUALL_Channel_SetLoop",
    "SQUALL_Channel_SetMinMaxDistance",
    "SQUALL_Channel_SetPan",
    "SQUALL_Channel_SetPlayPosition",
    "SQUALL_Channel_SetPlayPositionMs",
    "SQUALL_Channel_SetPriority",
    "SQUALL_Channel_SetVelocity",
    "SQUALL_Channel_SetVolume",
    "SQUALL_Channel_SetWorker",
    "SQUALL_Channel_Start",
    "SQUALL_Channel_Status",
    "SQUALL_Channel_Stop",
    "SQUALL_Channel_ZOOMFX_GetProperties",
    "SQUALL_Channel_ZOOMFX_SetProperties",
    "SQUALL_Free",
    "SQUALL_Get3DAlgorithm",
    "SQUALL_GetBufferSize",
    "SQUALL_GetChannelsInfo",
    "SQUALL_GetDevice",
    "SQUALL_GetDeviceCaps",
    "SQUALL_GetDeviceName",
    "SQUALL_GetEAXVersion",
    "SQUALL_GetHardwareAcceleration",
    "SQUALL_GetNumDevice",
    "SQUALL_GetSpeakerMode",
    "SQUALL_Init",
    "SQUALL_Listener_EAX_GetProperties",
    "SQUALL_Listener_EAX_SetPreset",
    "SQUALL_Listener_EAX_SetProperties",
    "SQUALL_Listener_GetDistanceFactor",
    "SQUALL_Listener_GetDopplerFactor",
    "SQUALL_Listener_GetParameters",
    "SQUALL_Listener_GetPosition",
    "SQUALL_Listener_GetRolloffFactor",
    "SQUALL_Listener_GetVelocity",
    "SQUALL_Listener_SetDistanceFactor",
    "SQUALL_Listener_SetDopplerFactor",
    "SQUALL_Listener_SetParameters",
    "SQUALL_Listener_SetPosition",
    "SQUALL_Listener_SetRolloffFactor",
    "SQUALL_Listener_SetVelocity",
    "SQUALL_Listener_SetWorker",
    "SQUALL_Listener_Update",
    "SQUALL_Pause",
    "SQUALL_SampleGroup_Play",
    "SQUALL_SampleGroup_Play3D",
    "SQUALL_SampleGroup_Play3DEx",
    "SQUALL_SampleGroup_PlayEx",
    "SQUALL_Sample_GetDefault",
    "SQUALL_Sample_GetFileFrequency",
    "SQUALL_Sample_GetFileLength",
    "SQUALL_Sample_GetFileLengthMs",
    "SQUALL_Sample_LoadFile",
    "SQUALL_Sample_LoadFromMemory",
    "SQUALL_Sample_Pause",
    "SQUALL_Sample_Play",
    "SQUALL_Sample_Play3D",
    "SQUALL_Sample_Play3DEx",
    "SQUALL_Sample_PlayEx",
    "SQUALL_Sample_SetDefault",
    "SQUALL_Sample_Stop",
    "SQUALL_Sample_Unload",
    "SQUALL_Sample_UnloadAll",
    "SQUALL_Set3DAlgorithm",
    "SQUALL_SetBufferSize",
    "SQUALL_SetDevice",
    "SQUALL_SetFileCallbacks",
    "SQUALL_SetHardwareAcceleration",
    "SQUALL_SetMemoryCallbacks",
    "SQUALL_SetSpeakerMode",
    "SQUALL_Stop",
    0,
};

FARPROC g_slot[101] = {0};

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
