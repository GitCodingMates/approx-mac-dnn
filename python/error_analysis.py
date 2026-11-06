"""Exhaustive error characterization of every multiplier over all
65,536 signed 8-bit input pairs. Writes results/error_metrics.csv
and results/error_heatmaps.png."""
import csv
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from approx_mult import MULTIPLIERS, build_lut

OUT = os.path.join(os.path.dirname(__file__), "..", "results")
os.makedirs(OUT, exist_ok=True)

exact = build_lut("exact").astype(np.int64)
MAX_P = 128 * 128
rows = []
for name in MULTIPLIERS:
    approx = build_lut(name).astype(np.int64)
    ed = np.abs(approx - exact)
    nz = exact != 0
    rows.append({
        "multiplier": name,
        "error_rate_%": 100 * np.mean(ed != 0),
        "MED": ed.mean(),
        "NMED_%": 100 * ed.mean() / MAX_P,
        "MRED_%": 100 * np.mean(ed[nz] / np.abs(exact[nz])),
        "max_abs_err": int(ed.max()),
        "bias": float((approx - exact).mean()),
    })

with open(os.path.join(OUT, "error_metrics.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys())
    w.writeheader()
    for r in rows:
        w.writerow({k: (f"{v:.4f}" if isinstance(v, float) else v) for k, v in r.items()})

print(f"{'multiplier':10s} {'ER%':>7s} {'MED':>9s} {'NMED%':>7s} {'MRED%':>7s} {'maxErr':>7s}")
for r in rows:
    print(f"{r['multiplier']:10s} {r['error_rate_%']:7.2f} {r['MED']:9.2f} "
          f"{r['NMED_%']:7.3f} {r['MRED_%']:7.3f} {r['max_abs_err']:7d}")

# relative-error heatmaps for the approximate designs
names = [n for n in MULTIPLIERS if n != "exact"]
fig, axs = plt.subplots(1, len(names), figsize=(4 * len(names), 3.6))
for ax, n in zip(axs, names):
    approx = build_lut(n).astype(np.int64)
    rel = np.where(exact != 0, np.abs(approx - exact) / np.maximum(np.abs(exact), 1), 0)
    im = ax.imshow(100 * rel, extent=[-128, 127, 127, -128], cmap="magma", vmax=20)
    ax.set_title(n)
    ax.set_xlabel("b")
    ax.set_ylabel("a")
fig.colorbar(im, ax=axs, label="relative error % (clipped at 20)")
fig.savefig(os.path.join(OUT, "error_heatmaps.png"), dpi=130, bbox_inches="tight")
print("saved results/error_metrics.csv, results/error_heatmaps.png")
