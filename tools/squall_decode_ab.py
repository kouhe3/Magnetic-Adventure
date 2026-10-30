"""对拍两个 Squall.dll 对整目录 OGG 的解析/解码元数据。

用法: <32位 CPython> tools/squall_decode_ab.py <dllA> <dllB> <ogg-dir>
判据: 每个文件的 (sample_id, file_length, file_length_ms, file_freq) 两侧逐项相同；
      退出码 0 = 全一致，1 = 有差异（打印前 10 条）。
覆盖边界: 只比元数据，不比 PCM 样本（解码样本需抓 DirectSound 缓冲，见 T4.3）。
"""
import ctypes
import json
import os
import subprocess
import sys


def one(dll, files):
    api = ctypes.WinDLL(dll)
    api.SQUALL_Init.restype = ctypes.c_int
    api.SQUALL_Init.argtypes = [ctypes.c_void_p]
    api.SQUALL_Free.restype = None
    api.SQUALL_Sample_LoadFromMemory.restype = ctypes.c_int
    api.SQUALL_Sample_LoadFromMemory.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_int, ctypes.c_void_p]
    for f in ("GetFileLength", "GetFileLengthMs", "GetFileFrequency"):
        fn = getattr(api, "SQUALL_Sample_" + f)
        fn.restype = ctypes.c_int
        fn.argtypes = [ctypes.c_int]
    api.SQUALL_Sample_UnloadAll.restype = None

    rows = []
    rc = api.SQUALL_Init(None)
    for path in files:
        data = open(path, "rb").read()
        buf = ctypes.create_string_buffer(data, len(data))
        sid = api.SQUALL_Sample_LoadFromMemory(buf, len(data), 1, None)
        rec = {"file": os.path.basename(path), "sid": sid}
        if sid >= 0:
            rec["len"] = api.SQUALL_Sample_GetFileLength(sid)
            rec["ms"] = api.SQUALL_Sample_GetFileLengthMs(sid)
            rec["hz"] = api.SQUALL_Sample_GetFileFrequency(sid)
        rows.append(rec)
        api.SQUALL_Sample_UnloadAll()
    api.SQUALL_Free()
    print(json.dumps({"init": rc, "rows": rows}))


def main(a, b, d):
    files = sorted(os.path.join(d, f) for f in os.listdir(d) if f.lower().endswith(".ogg"))
    if not files:
        print(f"no .ogg under {d}")
        return 2
    outs = []
    for dll in (a, b):
        r = subprocess.run([sys.executable, __file__, "--one", dll, *files],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print(r.stdout, r.stderr)
            return 2
        outs.append(json.loads(r.stdout))
    ra, rb = outs[0]["rows"], outs[1]["rows"]
    diffs = [(x, y) for x, y in zip(ra, rb) if x != y]
    print(f"files={len(ra)} init={outs[0]['init']}/{outs[1]['init']} diffs={len(diffs)}")
    for x, y in diffs[:10]:
        print(f"  A {x}\n  B {y}")
    return 0 if not diffs and len(ra) == len(rb) else 1


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--one":
        one(sys.argv[2], sys.argv[3:])
        sys.exit(0)
    if len(sys.argv) < 4:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(sys.argv[1], sys.argv[2], sys.argv[3]))
