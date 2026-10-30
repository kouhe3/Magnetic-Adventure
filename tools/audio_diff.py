"""比较两份环回录音（tools/audio_capture.py 的产物）。

用法: python tools/audio_diff.py <a.wav> <b.wav>
判据: 两侧都从首个超过阈值的样本开始对齐，取共同长度，报告
      最大绝对差、RMS 差、以及归一化互相关（1.0 = 波形完全一致）。
      A/A（同一 DLL 两次录制）给出的数就是这套环回的口径地板；
      只有显著高于地板才好说"两个 DLL 输出不同"。
"""
import sys
import wave

import numpy as np


def load(path):
    with wave.open(path, "rb") as w:
        n = w.getnframes()
        raw = w.readframes(n)
        return np.frombuffer(raw, dtype="<i2"), w.getframerate(), w.getnchannels()


def trim(x, thresh=200):
    idx = np.nonzero(np.abs(x) > thresh)[0]
    if not len(idx):
        return x[:0]
    return x[idx[0]:]


def main(a_path, b_path):
    a, ra, ca = load(a_path)
    b, rb, cb = load(b_path)
    if (ra, ca) != (rb, cb):
        print(f"format mismatch: {ra}/{ca} vs {rb}/{cb}")
    a, b = trim(a), trim(b)
    n = min(len(a), len(b))
    if n == 0:
        print("both silent")
        return 2
    a, b = a[:n].astype(np.int64), b[:n].astype(np.int64)
    diff = a - b
    denom = float(np.sqrt(np.mean(a.astype(np.float64) ** 2)) * np.sqrt(np.mean(b.astype(np.float64) ** 2)))
    corr = float(np.mean(a * b) / denom) if denom else 0.0
    print(f"samples={n} max|d|={int(np.max(np.abs(diff)))} "
          f"rms_d={float(np.sqrt(np.mean(diff.astype(np.float64) ** 2))):.2f} corr={corr:.6f}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(sys.argv[1], sys.argv[2]))
