"""播放单个 OGG 到指定设备，同时用 ffmpeg 从 VB-Audio CABLE Output 录下来。

用法: <32位 CPython> tools/audio_capture.py <dll> <ogg> <out.wav> [--device 3] [--seconds 3]
判据: 同一条命令对两个 Squall.dll 各跑一次，然后用 tools/audio_diff.py 比波形。
      A/A（同一个 DLL 跑两次）的差值就是这套环回的口径地板，必须先量。
覆盖边界: 录到的是 Windows 混音后的输出（含共享模式重采样），不是解码原始样本；
      因此只能证明"输出等价"，不能证明 PCM 逐位（F134）。
"""
import ctypes
import subprocess
import sys
import time

CABLE = "CABLE Output (VB-Audio Virtual Cable)"


class Params(ctypes.Structure):
    _fields_ = [
        ("Window", ctypes.c_void_p),
        ("Device", ctypes.c_int),
        ("SampleRate", ctypes.c_int),
        ("BitPerSample", ctypes.c_int),
        ("Channels", ctypes.c_int),
        ("UseHW2D", ctypes.c_int),
        ("UseHW3D", ctypes.c_int),
        ("UseAlg", ctypes.c_int),
        ("BufferSize", ctypes.c_int),
        ("ListenerMode", ctypes.c_int),
        ("DistanceFactor", ctypes.c_float),
        ("RolloffFactor", ctypes.c_float),
        ("DopplerFactor", ctypes.c_float),
    ]


def main(argv):
    dll, ogg, out = argv[0], argv[1], argv[2]
    device = 3
    seconds = 3
    i = 3
    while i < len(argv):
        if argv[i] == "--device":
            device = int(argv[i + 1]); i += 2
        elif argv[i] == "--seconds":
            seconds = int(argv[i + 1]); i += 2
        else:
            i += 1

    api = ctypes.WinDLL(dll)
    api.SQUALL_Init.restype = ctypes.c_int
    api.SQUALL_Init.argtypes = [ctypes.POINTER(Params)]
    api.SQUALL_Sample_LoadFromMemory.restype = ctypes.c_int
    api.SQUALL_Sample_LoadFromMemory.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_int, ctypes.c_void_p]
    api.SQUALL_Sample_PlayEx.restype = ctypes.c_int
    api.SQUALL_Sample_PlayEx.argtypes = [ctypes.c_int] * 8
    api.SQUALL_Free.restype = None

    rec = subprocess.Popen(
        ["ffmpeg", "-hide_banner", "-loglevel", "error", "-f", "dshow",
         "-i", f"audio={CABLE}", "-t", str(seconds), "-ac", "2", "-ar", "44100",
         "-y", out])
    time.sleep(0.8)

    p = Params(None, device, 44100, 16, 16, 0, 0, 0, 200, 0, 1.0, 1.0, 1.0)
    rc_init = api.SQUALL_Init(ctypes.byref(p))
    data = open(ogg, "rb").read()
    buf = ctypes.create_string_buffer(data, len(data))
    sid = api.SQUALL_Sample_LoadFromMemory(buf, len(data), 1, None)
    ch = api.SQUALL_Sample_PlayEx(sid, 0, 1, 1, 0, 99, 0, 50) if sid >= 0 else -1
    print(f"init={rc_init} sid={sid} channel={ch}")
    time.sleep(seconds)
    api.SQUALL_Free()
    rec.wait()
    return 0 if (rc_init >= 0 and sid >= 0 and ch >= 0) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
