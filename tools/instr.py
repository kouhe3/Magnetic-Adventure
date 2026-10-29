"""判据共用的仪器：日志格式、构建指纹、序列判据。

为什么必须存在（docs/facts.md F82、F87）：
- 同一份录制在 SSE2 与 x87 构建下数字差三个数量级，产物里没有 DLL md5 就无法事后
  判断一条结论出自哪个构建——「仪器修好后重跑历史」这条规则也就无法执行；
- v01 日志（`B2FFI01`）缺返回值/出参、dump 只有 64B，不能作为保真度判据。

用法：
  import instr
  instr.log_magic("work/rec_x/ffi.bin")      -> 'B2FFI02'
  instr.log_usable('B2FFI01')                -> False
  instr.fingerprint("build/Release/b2Physics.dll") -> {...'match': True}
  instr.bounded(step_bad)                    -> (ok, prev_decile, last_decile, peak)
"""
import hashlib
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD_INFO = os.path.join(ROOT, "build", "build_info.json")

# 可用于保真度判定的日志格式：v02 起才有完整返回值/出参（F46）与 128B dump（F59）。
MIN_LOG_VERSION = 2


def md5_file(path):
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def log_magic(path):
    """日志头 8 字节里的格式魔数；读不到返回 '?'。"""
    try:
        with open(path, "rb") as fh:
            return fh.read(8).rstrip(b"\0").decode("ascii", "replace")
    except OSError:
        return "?"


def log_usable(magic):
    """只有 ≥ v02 的日志能作保真度判据（F87）。"""
    if not magic.startswith("B2FFI"):
        return False
    try:
        return int(magic[5:]) >= MIN_LOG_VERSION
    except ValueError:
        return False


def build_info():
    """CMake 在构建末尾写出的指纹；不存在返回 {}。"""
    try:
        with open(BUILD_INFO, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError):
        return {}


def fingerprint(dll_path):
    """被测 DLL 的指纹。`match` 为假表示指纹文件不是这个二进制的产物。

    没有 match 时 arch/fp 一律写 unknown——宁可不给，不给错的。
    """
    p = dll_path if os.path.isabs(dll_path) else os.path.join(ROOT, dll_path)
    out = {"dll": os.path.relpath(p, ROOT).replace("\\", "/")}
    try:
        out["md5"] = md5_file(p)
        out["bytes"] = os.path.getsize(p)
    except OSError:
        out.update({"md5": None, "bytes": None, "match": False, "arch": "unknown", "fp": "unknown"})
        return out
    info = build_info()
    match = bool(info) and info.get("dll_md5") == out["md5"]
    out["match"] = match
    if match:
        out["arch"] = info.get("arch")
        out["fp"] = info.get("fp")
        out["config"] = info.get("config")
        out["msvc"] = info.get("msvc")
        out["cxx"] = info.get("cxx")
        out["flags"] = info.get("flags")
        out["built"] = info.get("built")
        out["box2d_md5"] = info.get("box2d_md5")
    else:
        out["arch"] = "unknown"
        out["fp"] = "unknown"
        out["info_md5"] = info.get("dll_md5")
    return out


def deciles(series):
    """按步序号分十个十分位，返回每段的中位数（跳过前 10% 热身）。"""
    if not series:
        return []
    ks = sorted(series, key=int)
    warm = ks[len(ks) // 10:] or ks
    out = []
    n = len(warm)
    for i in range(10):
        seg = warm[int(n * i / 10):int(n * (i + 1) / 10)]
        if seg:
            out.append(sorted(series[k] for k in seg)[len(seg) // 2])
    return out


def bounded(step_bad):
    """判「是否还在增长」，而不是「比开头高多少」。

    典型曲线是 1 → 4 → 5 → 11 → 11：前段扩散、后段饱和，这是容差内的数值传播，
    不是发散。所以比较**最后两个十分位**的中位数（近端斜率），并额外报出饱和水位。

    跳过前 10%：关卡加载阶段 body 还没建全，超差数天然低。
    """
    if not step_bad:
        return True, 0.0, 0.0, 0.0
    ks = sorted(step_bad, key=int)
    warm = ks[len(ks) // 10:] or ks
    n = len(warm)
    prev = warm[max(0, int(n * 0.7)):max(1, int(n * 0.9))]
    last = warm[max(1, int(n * 0.9)):]
    a = sorted(step_bad[k] for k in prev)[len(prev) // 2] if prev else 0
    b = sorted(step_bad[k] for k in last)[len(last) // 2] if last else 0
    peak = max(step_bad[k] for k in warm) if warm else 0
    return b <= a * 1.25 + 2, float(a), float(b), float(peak)
