"""Combine synthesis, error and accuracy results into the design-space
plot results/pareto.png and the summary table results/summary.csv."""
import csv
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.join(os.path.dirname(__file__), "..", "results")


def load(name, key):
    with open(os.path.join(ROOT, name)) as f:
        return {r[key]: r for r in csv.DictReader(f)}


syn = load("synth.csv", "design")
err = load("error_metrics.csv", "multiplier")
acc = load("accuracy.csv", "multiplier")

names = ["exact", "trunc_k4", "trunc_k6", "trunc_k8", "mitchell"]
base_acc = float(acc["exact"]["accuracy_%"])
rows = []
for n in names:
    rows.append({
        "multiplier": n,
        "area_GE": float(syn[n]["area_GE"]),
        "area_saving_%": float(syn[n]["area_saving_%"]),
        "logic_depth": int(syn[n]["logic_depth"]),
        "MRED_%": float(err[n]["MRED_%"]),
        "accuracy_%": float(acc[n]["accuracy_%"]),
        "accuracy_drop_%": round(base_acc - float(acc[n]["accuracy_%"]), 2),
    })

with open(os.path.join(ROOT, "summary.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys())
    w.writeheader()
    w.writerows(rows)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
colors = {"exact": "#444444", "mitchell": "#d62728"}
for r in rows:
    c = colors.get(r["multiplier"], "#1f77b4")
    ax1.scatter(r["area_GE"], r["accuracy_%"], s=60, color=c, zorder=3)
    ax1.annotate(r["multiplier"], (r["area_GE"], r["accuracy_%"]),
                 textcoords="offset points", xytext=(-20, -14) if r["multiplier"] == "mitchell" else (6, 4), fontsize=9)
    ax2.scatter(r["area_GE"], r["MRED_%"], s=60, color=c, zorder=3)
    ax2.annotate(r["multiplier"], (r["area_GE"], r["MRED_%"]),
                 textcoords="offset points", xytext=(-20, -14) if r["multiplier"] == "mitchell" else (6, 4), fontsize=9)

trunc = [r for r in rows if r["multiplier"].startswith("trunc") or r["multiplier"] == "exact"]
trunc.sort(key=lambda r: r["area_GE"])
ax1.plot([r["area_GE"] for r in trunc], [r["accuracy_%"] for r in trunc], "--", color="#1f77b4", lw=1)
ax2.plot([r["area_GE"] for r in trunc], [r["MRED_%"] for r in trunc], "--", color="#1f77b4", lw=1)

ax1.set_xlabel("multiplier area (NAND2 eq.)")
ax1.set_ylabel("MNIST accuracy (%)")
ax1.set_title("Application-level trade-off")
ax1.set_ylim(base_acc - 1.0, base_acc + 0.3)
ax2.set_xlabel("multiplier area (NAND2 eq.)")
ax2.set_ylabel("MRED (%)")
ax2.set_title("Arithmetic-level trade-off")
for ax in (ax1, ax2):
    ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(os.path.join(ROOT, "pareto.png"), dpi=150)

for r in rows:
    print(r)
print("saved results/pareto.png, results/summary.csv")
