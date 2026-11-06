"""Train a 784-128-10 MLP on MNIST in pure NumPy, then quantize to
int8 weights/activations with int32 accumulation (accelerator-style).
Saves results/model_int8.npz."""
import os
import numpy as np
from sklearn.datasets import fetch_openml

ROOT = os.path.join(os.path.dirname(__file__), "..")
rng = np.random.default_rng(0)

X, y = fetch_openml("mnist_784", version=1, return_X_y=True, as_frame=False,
                    data_home=os.path.join(ROOT, "data"), parser="liac-arff")
X = (X / 255.0).astype(np.float32)
y = y.astype(np.int64)
Xtr, ytr, Xte, yte = X[:60000], y[:60000], X[60000:], y[60000:]

# ---------------------------------------------------------------- train
H = 128
W1 = rng.normal(0, np.sqrt(2 / 784), (784, H)).astype(np.float32)
b1 = np.zeros(H, np.float32)
W2 = rng.normal(0, np.sqrt(2 / H), (H, 10)).astype(np.float32)
b2 = np.zeros(10, np.float32)
lr, bs = 0.1, 128
for ep in range(8):
    perm = rng.permutation(60000)
    for s in range(0, 60000, bs):
        idx = perm[s:s + bs]
        x, t = Xtr[idx], ytr[idx]
        h = np.maximum(x @ W1 + b1, 0)
        z = h @ W2 + b2
        p = np.exp(z - z.max(1, keepdims=True))
        p /= p.sum(1, keepdims=True)
        p[np.arange(len(t)), t] -= 1
        g = p / len(t)
        gW2, gb2 = h.T @ g, g.sum(0)
        gh = (g @ W2.T) * (h > 0)
        gW1, gb1 = x.T @ gh, gh.sum(0)
        W1 -= lr * gW1; b1 -= lr * gb1; W2 -= lr * gW2; b2 -= lr * gb2
    acc = np.mean(np.argmax(np.maximum(Xte @ W1 + b1, 0) @ W2 + b2, 1) == yte)
    print(f"epoch {ep + 1}: float test acc = {acc * 100:.2f}%")

# ------------------------------------------------------------- quantize
def q(w, scale):
    return np.clip(np.round(w / scale), -127, 127).astype(np.int8)

s_x = 1 / 127                                  # input pixels in [0,1]
s_w1 = np.abs(W1).max() / 127
s_w2 = np.abs(W2).max() / 127
h_cal = np.maximum(Xtr[:5000] @ W1 + b1, 0)   # calibration for activations
s_h = np.percentile(h_cal, 99.99) / 127

np.savez(os.path.join(ROOT, "results", "model_int8.npz"),
         W1=q(W1, s_w1), W2=q(W2, s_w2),
         b1=np.round(b1 / (s_x * s_w1)).astype(np.int32),
         b2=np.round(b2 / (s_h * s_w2)).astype(np.int32),
         # requantization: h_q = round(acc1 * M1), M1 = s_x*s_w1/s_h
         M1=np.float64(s_x * s_w1 / s_h),
         float_acc=np.float64(acc))
print("saved results/model_int8.npz")
