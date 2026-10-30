"""Squall 单 DLL 探针：Init / 设备枚举 / OGG 加载与解码长度。

用法: <32位 CPython> tools/squall_probe.py <dll> <ogg>
判据: 对同一份 ogg 分别跑 bin/gametop/Squall.dll 与 build/Release/Squall.dll，
      两行 JSON 的 init/num_device/dev0/sample_id/file_length/file_length_ms/file_freq 应逐项相同。
      输出一行 JSON；崩溃（如 access violation）即判 FAIL。
覆盖边界: 只到"解析 + 元数据"，不比对 PCM 样本（那需要抓 DirectSound 缓冲，见 T2.4c）。
"""
import ctypes
import json
import sys

path, ogg = sys.argv[1], sys.argv[2]
api = ctypes.WinDLL(path)
api.SQUALL_Init.restype = ctypes.c_int
api.SQUALL_Init.argtypes = [ctypes.c_void_p]
api.SQUALL_Free.restype = None
api.SQUALL_GetNumDevice.restype = ctypes.c_int
api.SQUALL_GetDeviceName.restype = ctypes.c_int
api.SQUALL_GetDeviceName.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int]
api.SQUALL_Sample_LoadFromMemory.restype = ctypes.c_int
api.SQUALL_Sample_LoadFromMemory.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_int, ctypes.c_void_p]
api.SQUALL_Sample_GetFileLength.restype = ctypes.c_int
api.SQUALL_Sample_GetFileLength.argtypes = [ctypes.c_int]
api.SQUALL_Sample_GetFileLengthMs.restype = ctypes.c_int
api.SQUALL_Sample_GetFileLengthMs.argtypes = [ctypes.c_int]
api.SQUALL_Sample_GetFileFrequency.restype = ctypes.c_int
api.SQUALL_Sample_GetFileFrequency.argtypes = [ctypes.c_int]
api.SQUALL_Sample_Unload.restype = None
api.SQUALL_Sample_Unload.argtypes = [ctypes.c_int]

out = {'dll': path}
out['init'] = api.SQUALL_Init(None)
out['num_device'] = api.SQUALL_GetNumDevice()
if out['num_device'] > 0:
    buf = ctypes.create_string_buffer(256)
    out['dev0_rc'] = api.SQUALL_GetDeviceName(0, buf, 256)
    out['dev0'] = buf.value.decode('latin1')
data = open(ogg, 'rb').read()
mem = ctypes.create_string_buffer(data, len(data))
sid = api.SQUALL_Sample_LoadFromMemory(mem, len(data), 1, None)
out['sample_id'] = sid
if sid >= 0:
    out['file_length'] = api.SQUALL_Sample_GetFileLength(sid)
    out['file_length_ms'] = api.SQUALL_Sample_GetFileLengthMs(sid)
    out['file_freq'] = api.SQUALL_Sample_GetFileFrequency(sid)
    api.SQUALL_Sample_Unload(sid)
api.SQUALL_Free()
print(json.dumps(out, ensure_ascii=False))
