#!/usr/bin/env python3
"""无 cv2 依赖的模板匹配（归一化互相关，FFT 实现）。

用法: python tools/tmatch.py <scene.png> <template.png> [--threshold 0.8]
输出 JSON: {"score":..., "at":[x,y], "passed":bool}
"""
import json
import sys

import numpy as np
from PIL import Image


def gray(path):
    return np.asarray(Image.open(path).convert("L"), dtype=np.float64)


def match(scene_path, tpl_path):
    I = gray(scene_path)
    T = gray(tpl_path)
    th, tw = T.shape
    H, W = I.shape
    if th > H or tw > W:
        return {"error": "template larger than scene"}
    n = th * tw
    T0 = T - T.mean()
    tstd = np.sqrt((T0 * T0).mean())

    # 积分图：局部和、局部平方和
    S = np.zeros((H + 1, W + 1))
    S2 = np.zeros((H + 1, W + 1))
    S[1:, 1:] = np.cumsum(np.cumsum(I, 0), 1)
    S2[1:, 1:] = np.cumsum(np.cumsum(I * I, 0), 1)

    def box(A):
        return (A[th:, tw:] - A[:-th, tw:] - A[th:, :-tw] + A[:-th, :-tw])

    sum_i = box(S)
    sum_i2 = box(S2)
    mean_i = sum_i / n
    var_i = sum_i2 / n - mean_i * mean_i
    std_i = np.sqrt(np.maximum(var_i, 1e-9))

    # 互相关（FFT）
    fh, fw = H + th, W + tw
    FI = np.fft.rfft2(I, (fh, fw))
    FT = np.fft.rfft2(T0[::-1, ::-1], (fh, fw))
    corr = np.fft.irfft2(FI * FT, (fh, fw))
    corr = corr[th - 1:th - 1 + (H - th + 1), tw - 1:tw - 1 + (W - tw + 1)]

    score = corr / (n * std_i * tstd + 1e-9)
    idx = np.unravel_index(np.argmax(score), score.shape)
    return {"score": float(score[idx]), "at": [int(idx[1]), int(idx[0])]}


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(2)
    threshold = 0.8
    if "--threshold" in sys.argv:
        threshold = float(sys.argv[sys.argv.index("--threshold") + 1])
    r = match(sys.argv[1], sys.argv[2])
    r["passed"] = r.get("score", 0) >= threshold
    print(json.dumps(r))
