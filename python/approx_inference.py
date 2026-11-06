"""Run int8 MNIST inference where every multiplication goes through a
chosen (approximate) multiplier via its bit-accurate LUT.
Writes results/accuracy.csv."""
import csv
import os
import numpy as np
from sklearn.datasets import fetch_openml
from approx_mult import MULTIPLIERS, build_lut

ROOT = os.path.join(os.path.dirname(__file__), "..")
m = np.load(os.path.join(ROOT, "results", "model_int8.npz"))
X, y = fetch_openml("mnist_784", version=1, return_X_y=True, as_frame=False,
                    data_home=os.path.join(ROOT, "data"), parser="liac-arff")
Xte = np.round(X[60000:] / 255.0 * 127).astype(np.int64)   # int8 inputs
yte = y[60000:].astype(np.int64)


def matmul_lut(xq, wq, lut, chunk=50):
    """acc[n,j] = sum_i MUL(x[n,i], w[i,j]) with int32 accumulation."""
    wi = wq.astype(np.int64) + 128
    out = np.empty((xq.shape[0], wq.shape[1]), np.int64)
    for s in range(0, xq.shape[0], chunk):
        xi = xq[s:s + chunk, :, None] + 128
        out[s:s + chunk] = lut[xi, wi[None]].sum(1)
    return out


def infer(lut):
    acc1 = matmul_lut(Xte, m["W1"], lut) + m["b1"]
    h = np.clip(np.round(np.maximum(acc1, 0) * m["M1"]), 0, 127).astype(np.int64)
    acc2 = matmul_lut(h, m["W2"], lut) + m["b2"]
    return np.mean(np.argmax(acc2, 1) == yte) * 100


rows = []
print(f"float32 reference: {m['float_acc'] * 100:.2f}%")
for name in MULTIPLIERS:
    a = infer(build_lut(name))
    rows.append({"multiplier": name, "accuracy_%": f"{a:.2f}"})
    print(f"{name:9s}: {a:.2f}%")

with open(os.path.join(ROOT, "results", "accuracy.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["multiplier", "accuracy_%"])
    w.writeheader()
    w.writerows(rows)
print("saved results/accuracy.csv")
