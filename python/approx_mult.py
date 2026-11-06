"""
Bit-accurate models of 8-bit signed multipliers (exact and approximate).

All models use sign-magnitude internally:
    |a|, |b| in [0, 128]  (8-bit unsigned magnitudes)
    result sign = sign(a) XOR sign(b)
These models are the golden reference for the Verilog RTL in ../rtl.
Every function works element-wise on NumPy integer arrays.
"""
import numpy as np

N_BITS = 8  # magnitude width (covers |-128| = 128)


def _sign_mag(a, b):
    a = np.asarray(a, dtype=np.int64)
    b = np.asarray(b, dtype=np.int64)
    sign = np.where((a < 0) ^ (b < 0), -1, 1)
    return np.abs(a), np.abs(b), sign


# ---------------------------------------------------------------- exact
def mul_exact(a, b):
    return np.asarray(a, dtype=np.int64) * np.asarray(b, dtype=np.int64)


# ------------------------------------------------------------ truncated
def mul_truncated(a, b, k):
    """Array multiplier with all partial-product bits in result
    columns < k removed (column truncation, no compensation).
    Hardware saving: those AND gates and their adder cells disappear."""
    ma, mb, sign = _sign_mag(a, b)
    acc = np.zeros_like(ma)
    for i in range(N_BITS):
        ai = (ma >> i) & 1
        for j in range(N_BITS):
            if i + j >= k:
                acc += (ai & ((mb >> j) & 1)) << (i + j)
    return sign * acc


# ------------------------------------------------------------- mitchell
def _lod(x):
    """Leading-one detector: floor(log2(x)) for x > 0 (0 for x == 0)."""
    k = np.zeros_like(x)
    for p in range(N_BITS):
        k = np.where((x >> p) & 1 == 1, p, k)
    return k


def mul_mitchell(a, b):
    """Mitchell's logarithmic multiplier (1962), exact-integer form.

    a = 2^k1 (1 + f1),  b = 2^k2 (1 + f2),  x_i = a_i - 2^k_i
    log2(a*b) ~= k1 + k2 + f1 + f2
      if f1 + f2 < 1:  P = 2^(k1+k2) + x1*2^k2 + x2*2^k1
      else:            P = 2*(x1*2^k2 + x2*2^k1)
    Needs only LODs, shifters and one adder -> no partial-product array.
    Always under-estimates (max relative error ~11.1%)."""
    ma, mb, sign = _sign_mag(a, b)
    k1, k2 = _lod(ma), _lod(mb)
    x1 = ma - (1 << k1)
    x2 = mb - (1 << k2)
    s = (x1 << k2) + (x2 << k1)          # = 2^(k1+k2) * (f1 + f2)
    base = 1 << (k1 + k2)
    p = np.where(s < base, base + s, s << 1)
    p = np.where((ma == 0) | (mb == 0), 0, p)
    return sign * p


# -------------------------------------------------------------- registry
MULTIPLIERS = {
    "exact": mul_exact,
    "trunc_k4": lambda a, b: mul_truncated(a, b, 4),
    "trunc_k6": lambda a, b: mul_truncated(a, b, 6),
    "trunc_k8": lambda a, b: mul_truncated(a, b, 8),
    "mitchell": mul_mitchell,
}

_VALS = np.arange(-128, 128)


def build_lut(name):
    """256x256 product table, index [a+128, b+128]. Used for fast inference."""
    A, B = np.meshgrid(_VALS, _VALS, indexing="ij")
    return MULTIPLIERS[name](A, B).astype(np.int32)


if __name__ == "__main__":
    for n in MULTIPLIERS:
        print(f"{n:9s}  13*-11 = {int(MULTIPLIERS[n](13, -11)):6d}   "
              f"127*127 = {int(MULTIPLIERS[n](127, 127))}")
