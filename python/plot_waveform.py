"""Render a timing diagram of the exact MAC from the ModelSim VCD dump
(sim/modelsim/mac.vcd) to results/mac_waveform.png."""
import os
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.join(os.path.dirname(__file__), "..")
VCD = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "sim", "modelsim", "mac.vcd")
T0, T1 = 20, 200          # ns window to draw

SIGNALS = [("clk", 1, False), ("rst", 1, False), ("en", 1, False), ("clr", 1, False),
           ("a", 8, True), ("b", 8, True), ("p", 16, True), ("p_q", 16, True),
           ("acc", 32, True), ("r_exact", 32, True)]
LABEL = {"p": "p (mult)", "p_q": "p_q (stage 1)", "acc": "acc (stage 2)",
         "r_exact": "reference"}


def parse_vcd(path):
    """Minimal VCD reader. ModelSim dumps some buses as individual bits
    (e.g. 'p [15]'), so bit-level variables are reassembled into buses."""
    widths = {s[0]: s[1] for s in SIGNALS}
    ids = {}                      # vcd id -> (name, bit index or None)
    state = {n: ["x"] * w for n, w in widths.items()}
    changes, scale, t, last_t = {}, 1, 0, None
    dirty = set()

    def flush(at):
        for n in dirty:
            changes.setdefault(n, []).append((at, "".join(state[n])))
        dirty.clear()

    with open(path) as f:
        for line in f:
            tok = line.split()
            if not tok:
                continue
            if tok[0] == "$timescale":
                spec = tok[1] if len(tok) > 1 and tok[1] != "$end" else next(f).split()[0]
                num = int("".join(c for c in spec if c.isdigit()))
                unit = spec.lstrip("0123456789")
                scale = num * {"s": 1e9, "ms": 1e6, "us": 1e3, "ns": 1, "ps": 1e-3, "fs": 1e-6}[unit]
            elif tok[0] == "$var":
                name = tok[4]
                if name not in widths:
                    continue
                bit = None
                ref = " ".join(tok[5:-1])
                if int(tok[2]) == 1 and widths[name] > 1 and ref.startswith("["):
                    bit = int(ref.strip("[]").split(":")[0])
                ids[tok[3]] = (name, bit)
            elif tok[0].startswith("#"):
                flush(t)
                t = int(tok[0][1:]) * scale
            else:
                if tok[0][0] == "b" and len(tok) == 2:
                    vid, val = tok[1], tok[0][1:]
                elif tok[0][0] in "01xzXZ":
                    vid, val = tok[0][1:], tok[0][0].lower()
                else:
                    continue
                if vid not in ids:
                    continue
                name, bit = ids[vid]
                w = widths[name]
                if bit is None:
                    val = val.rjust(w, "0" if val[0] == "1" else val[0])[-w:]
                    state[name] = list(val)
                else:
                    state[name][w - 1 - bit] = val
                dirty.add(name)
        flush(t)
    # drop repeated values
    for n, ev in changes.items():
        changes[n] = [e for i, e in enumerate(ev) if i == 0 or e[1] != ev[i - 1][1]]
    return changes


def to_int(bits, width, signed):
    if any(c in "xz" for c in bits):
        return None
    v = int(bits, 2)
    if signed and len(bits) == width and bits[0] == "1":
        v -= 1 << width
    return v


ch = parse_vcd(VCD)
fig, ax = plt.subplots(figsize=(12, 0.55 * len(SIGNALS) + 0.6))
for row, (name, width, signed) in enumerate(SIGNALS):
    y = len(SIGNALS) - 1 - row
    ev = [(t, v) for t, v in ch.get(name, [])]
    # value at window start
    start = [v for t, v in ev if t <= T0]
    pts = [(T0, start[-1] if start else "x")] + [(t, v) for t, v in ev if T0 < t < T1]
    pts.append((T1, None))
    color = "#1f4e9c" if name != "r_exact" else "#2e7d32"
    for (t, v), (tn, _) in zip(pts[:-1], pts[1:]):
        if width == 1:
            lvl = 0.75 if v == "1" else 0.1
            ax.plot([t, tn], [y + lvl] * 2, color=color, lw=1.4)
            ax.plot([tn, tn], [y + 0.1, y + 0.75], color=color, lw=0.6, alpha=0.5)
        else:
            ax.fill([t + 0.6, tn - 0.6, tn, tn - 0.6, t + 0.6, t],
                    [y + 0.75, y + 0.75, y + 0.425, y + 0.1, y + 0.1, y + 0.425],
                    facecolor="#e8eef8" if name != "r_exact" else "#e6f2e6",
                    edgecolor=color, lw=0.9)
            val = to_int(v, width, signed) if isinstance(v, str) else None
            if tn - t >= 8:
                ax.text((t + tn) / 2, y + 0.425, "x" if val is None else str(val),
                        ha="center", va="center", fontsize=7)
    ax.text(T0 - 2, y + 0.425, LABEL.get(name, name), ha="right", va="center", fontsize=9)

ax.set_xlim(T0 - 22, T1)
ax.set_ylim(-0.2, len(SIGNALS))
ax.set_yticks([])
ax.set_xlabel("time (ns)")
for s in ("left", "right", "top"):
    ax.spines[s].set_visible(False)
ax.grid(axis="x", alpha=0.25)
ax.set_title("Exact MAC: two-stage pipeline (ModelSim VCD dump)", fontsize=10)
fig.tight_layout()
out = os.path.join(ROOT, "results", "mac_waveform.png")
fig.savefig(out, dpi=160)
print("saved", out)
