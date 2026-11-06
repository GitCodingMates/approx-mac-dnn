"""Export golden products from the bit-accurate models for RTL verification.

Writes tb/vectors/<name>.hex with 65,536 lines. Line index i = {a, b},
where a = i[15:8] and b = i[7:0] are raw two's-complement bytes; each
line is the expected 16-bit two's-complement product.
"""
import os
import numpy as np
from approx_mult import MULTIPLIERS

OUT = os.path.join(os.path.dirname(__file__), "..", "tb", "vectors")
os.makedirs(OUT, exist_ok=True)

idx = np.arange(1 << 16)
a = ((idx >> 8) & 0xFF).astype(np.int64)
b = (idx & 0xFF).astype(np.int64)
a = np.where(a >= 128, a - 256, a)
b = np.where(b >= 128, b - 256, b)

for name, fn in MULTIPLIERS.items():
    p = np.asarray(fn(a, b), dtype=np.int64) & 0xFFFF
    path = os.path.join(OUT, f"{name}.hex")
    with open(path, "w") as f:
        f.write("\n".join(f"{v:04x}" for v in p) + "\n")
    print(f"wrote {path}")
