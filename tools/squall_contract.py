"""Squall 17 个宿主导入的接口契约探针（不依赖游戏路径）。

用法: <32位 CPython> tools/squall_contract.py <dllA> <dllB>
判据: 固定脚本（Init → LoadFromMemory/LoadFile → PlayEx(prepared) → Status/Pause/SetVolume/
      SetPriority/Start → Sample_Pause/Stop → ChannelGroup_* → Unload/UnloadAll → Free）
      两侧每步返回值逐项相同；退出码 0 = 一致。
单侧调试: <32位 CPython> tools/squall_contract.py --one <dll>
覆盖边界: 只比返回值，不比播放出来的 PCM；`Channel_Status` 依赖播放时序，两侧脚本相同即可比。
已知坑: 先 LoadFromMemory 再 LoadFile 会让 `api_SampleLoadFile` 的 strcmp 读到 NULL（内存样本无
        文件名）→ 两个 DLL 都崩；本脚本因此先 LoadFile。宿主的真实顺序是只走 LoadFromMemory。
"""
import ctypes
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OGG_MEM = os.path.join(ROOT, "work", "pak_baseline", "ac_mw_1.ogg")
OGG_FILE = os.path.join(ROOT, "work", "pak_baseline", "birds_1.ogg")


def one(dll):
    api = ctypes.WinDLL(dll)
    a = api
    a.SQUALL_Init.restype = ctypes.c_int; a.SQUALL_Init.argtypes = [ctypes.c_void_p]
    a.SQUALL_Free.restype = None
    a.SQUALL_Sample_LoadFromMemory.restype = ctypes.c_int
    a.SQUALL_Sample_LoadFromMemory.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_int, ctypes.c_void_p]
    a.SQUALL_Sample_LoadFile.restype = ctypes.c_int
    a.SQUALL_Sample_LoadFile.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.c_void_p]
    a.SQUALL_Sample_PlayEx.restype = ctypes.c_int; a.SQUALL_Sample_PlayEx.argtypes = [ctypes.c_int] * 8
    a.SQUALL_Sample_Pause.restype = ctypes.c_int; a.SQUALL_Sample_Pause.argtypes = [ctypes.c_int] * 2
    a.SQUALL_Sample_Stop.restype = ctypes.c_int; a.SQUALL_Sample_Stop.argtypes = [ctypes.c_int]
    a.SQUALL_Sample_Unload.restype = None; a.SQUALL_Sample_Unload.argtypes = [ctypes.c_int]
    a.SQUALL_Sample_UnloadAll.restype = None
    a.SQUALL_Channel_Start.restype = ctypes.c_int; a.SQUALL_Channel_Start.argtypes = [ctypes.c_int]
    a.SQUALL_Channel_Pause.restype = ctypes.c_int; a.SQUALL_Channel_Pause.argtypes = [ctypes.c_int] * 2
    a.SQUALL_Channel_Status.restype = ctypes.c_int; a.SQUALL_Channel_Status.argtypes = [ctypes.c_int]
    a.SQUALL_Channel_SetVolume.restype = ctypes.c_int; a.SQUALL_Channel_SetVolume.argtypes = [ctypes.c_int] * 2
    a.SQUALL_Channel_SetPriority.restype = ctypes.c_int; a.SQUALL_Channel_SetPriority.argtypes = [ctypes.c_int] * 2
    a.SQUALL_ChannelGroup_Pause.restype = ctypes.c_int; a.SQUALL_ChannelGroup_Pause.argtypes = [ctypes.c_int] * 2
    a.SQUALL_ChannelGroup_SetVolume.restype = ctypes.c_int
    a.SQUALL_ChannelGroup_SetVolume.argtypes = [ctypes.c_int] * 2
    a.SQUALL_ChannelGroup_Stop.restype = ctypes.c_int; a.SQUALL_ChannelGroup_Stop.argtypes = [ctypes.c_int]

    steps = []

    def rec(tag, v):
        steps.append([tag, v])

    rec("init", a.SQUALL_Init(None))
    # 先 LoadFile 再 LoadFromMemory：反过来会在 api_SampleLoadFile 的
    # strcmp(filename, GetFileName()) 上读到 NULL（内存样本没有文件名）→ 两个 DLL 都崩。
    sid2 = a.SQUALL_Sample_LoadFile(OGG_FILE.encode(), 1, None)
    rec("load_file", sid2)
    data = open(OGG_MEM, "rb").read()
    buf = ctypes.create_string_buffer(data, len(data))
    sid = a.SQUALL_Sample_LoadFromMemory(buf, len(data), 1, None)
    rec("load_mem", sid)
    ch = a.SQUALL_Sample_PlayEx(sid, 0, 1, 0, 0, 100, 0, 50)   # start=0 → prepared
    rec("play_prepared", ch)
    rec("status_prepared", a.SQUALL_Channel_Status(ch))
    rec("channel_pause1", a.SQUALL_Channel_Pause(ch, 1))
    rec("status_paused", a.SQUALL_Channel_Status(ch))
    rec("channel_pause0", a.SQUALL_Channel_Pause(ch, 0))
    rec("status_unpaused", a.SQUALL_Channel_Status(ch))
    rec("set_volume", a.SQUALL_Channel_SetVolume(ch, 50))
    rec("set_priority", a.SQUALL_Channel_SetPriority(ch, 7))
    rec("channel_start", a.SQUALL_Channel_Start(ch))
    rec("status_playing", a.SQUALL_Channel_Status(ch))
    rec("sample_pause1", a.SQUALL_Sample_Pause(sid, 1))
    rec("sample_pause0", a.SQUALL_Sample_Pause(sid, 0))
    rec("sample_stop", a.SQUALL_Sample_Stop(sid))
    rec("group_pause1", a.SQUALL_ChannelGroup_Pause(1, 1))
    rec("group_pause0", a.SQUALL_ChannelGroup_Pause(1, 0))
    rec("group_volume", a.SQUALL_ChannelGroup_SetVolume(1, 80))
    rec("group_stop", a.SQUALL_ChannelGroup_Stop(1))
    a.SQUALL_Sample_Unload(sid)
    a.SQUALL_Sample_Unload(sid2)
    a.SQUALL_Sample_UnloadAll()
    a.SQUALL_Free()
    print(json.dumps({"dll": dll, "steps": steps}))


def main(a_dll, b_dll):
    outs = []
    for dll in (a_dll, b_dll):
        r = subprocess.run([sys.executable, __file__, "--one", dll], capture_output=True, text=True)
        if r.returncode != 0 or not r.stdout.strip():
            print(r.stdout, r.stderr)
            return 2
        outs.append(json.loads(r.stdout)["steps"])
    diffs = [(x, y) for x, y in zip(*outs) if x != y]
    print(f"steps={len(outs[0])}/{len(outs[1])} diffs={len(diffs)}")
    for x, y in diffs[:10]:
        print(f"  A {x}\n  B {y}")
    return 0 if not diffs and len(outs[0]) == len(outs[1]) else 1


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--one":
        one(sys.argv[2])
        sys.exit(0)
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(sys.argv[1], sys.argv[2]))
