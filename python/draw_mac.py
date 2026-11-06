"""Block diagram of the pipelined MAC unit (rtl/mac.v).
Writes results/mac_block_diagram.pdf (vector, used by the report) and .png."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle, Polygon

OUT = os.path.join(os.path.dirname(__file__), "..", "results")
INK = "#1d2b3a"
BLUE = "#e8eef8"
REG = "#fff3d6"
GREEN = "#e6f2e6"

fig, ax = plt.subplots(figsize=(14, 6.4))
ax.set_xlim(-0.2, 14.0)
ax.set_ylim(-1.5, 5.4)
ax.axis("off")


def box(x0, y0, x1, y1, fc=BLUE, lw=1.4, round_=True):
    if round_:
        p = FancyBboxPatch((x0, y0), x1 - x0, y1 - y0, boxstyle="round,pad=0.02,rounding_size=0.08",
                           fc=fc, ec=INK, lw=lw, zorder=2)
    else:
        p = Rectangle((x0, y0), x1 - x0, y1 - y0, fc=fc, ec=INK, lw=lw, zorder=2)
    ax.add_patch(p)


def reg(x0, y0, x1, y1, name, width):
    box(x0, y0, x1, y1, fc=REG, round_=False)
    ax.add_patch(Polygon([[x0 + 0.25, y0], [x0 + 0.4, y0 + 0.17], [x0 + 0.55, y0]],
                         closed=False, fill=False, ec=INK, lw=1.1, zorder=3))
    ax.text((x0 + x1) / 2, (y0 + y1) / 2 + 0.12, name, ha="center", va="center",
            fontsize=10, family="monospace", weight="bold", zorder=4)
    ax.text((x0 + x1) / 2, (y0 + y1) / 2 - 0.2, width, ha="center", va="center",
            fontsize=8, color="#555", zorder=4)


def arrow(pts, label=None, lpos=None, bus=None):
    xs, ys = zip(*pts)
    ax.plot(xs[:-1] + (xs[-1],), ys, color=INK, lw=1.4, zorder=1, solid_capstyle="round")
    ax.annotate("", xy=pts[-1], xytext=pts[-2],
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.4, mutation_scale=13), zorder=1)
    if label:
        ax.text(*lpos, label, fontsize=9, ha="center", va="bottom", family="monospace")
    if bus:
        # bus-width slash
        mx, my = (pts[0][0] + pts[1][0]) / 2, (pts[0][1] + pts[1][1]) / 2
        ax.plot([mx - 0.07, mx + 0.07], [my - 0.12, my + 0.12], color=INK, lw=1.1)
        ax.text(mx, my - 0.32, bus, fontsize=7.5, ha="center", color="#555")


# pipeline stage shading
ax.add_patch(Rectangle((0.95, -1.35), 6.95, 6.35, fc="#f4f7fb", ec="none", zorder=0))
ax.add_patch(Rectangle((7.9, -1.35), 4.3, 6.35, fc="#f6faf4", ec="none", zorder=0))
ax.text(4.4, 4.75, "Stage 1: multiply", ha="center", fontsize=11, weight="bold", color="#3a5a8c")
ax.text(10.05, 4.75, "Stage 2: accumulate", ha="center", fontsize=11, weight="bold", color="#3f7a3f")

# inputs
ax.text(0.0, 3.55, "a", fontsize=12, family="monospace", weight="bold", va="center")
ax.text(0.0, 2.65, "b", fontsize=12, family="monospace", weight="bold", va="center")
arrow([(0.25, 3.55), (1.2, 3.55)], bus="8")
arrow([(0.25, 2.65), (1.2, 2.65)], bus="8")

# sign_mag
box(1.2, 2.2, 2.75, 4.0)
ax.text(1.975, 3.65, "sign_mag", ha="center", fontsize=10, family="monospace", weight="bold")
ax.text(1.975, 3.25, "|a|, |b|", ha="center", fontsize=9)
ax.text(1.975, 2.85, "neg = a7 ^ b7", ha="center", fontsize=8.5)
ax.text(1.975, 2.45, "two's compl. ->\nsign-magnitude", ha="center", va="center", fontsize=7, color="#555")
arrow([(2.75, 3.4), (3.45, 3.4)], bus="8+8")
arrow([(2.75, 2.5), (3.45, 2.5)])
ax.text(3.1, 2.58, "neg", fontsize=8, family="monospace", ha="center")

# multiplier
box(3.45, 1.55, 6.35, 4.35)
ax.text(4.9, 4.05, "Multiplier", ha="center", fontsize=11, weight="bold")
ax.text(4.9, 3.75, "selected by parameter MUL", ha="center", fontsize=8, color="#555")
for i, (k, t) in enumerate([("MUL=0", "exact array (64 PP bits)"),
                            ("MUL=1", "truncated: drop cols < K"),
                            ("MUL=2", "Mitchell: LOD + shift + add")]):
    y = 3.3 - i * 0.55
    box(3.65, y - 0.22, 6.15, y + 0.22, fc="white", lw=0.9)
    ax.text(3.75, y, k, fontsize=8, family="monospace", va="center", weight="bold")
    ax.text(4.45, y, t, fontsize=8, va="center")
ax.text(4.9, 1.7, "apply sign -> p", ha="center", fontsize=8, color="#555")

# p -> p_q
arrow([(6.35, 3.1), (7.05, 3.1)], bus="16")
ax.text(6.7, 3.42, "p", fontsize=9, family="monospace", ha="center")
reg(7.05, 2.6, 7.85, 3.6, "p_q", "16 b")

# sign extend
arrow([(7.85, 3.1), (8.35, 3.1)])
box(8.35, 2.75, 9.3, 3.45, fc="white")
ax.text(8.825, 3.1, "sign\next.", ha="center", va="center", fontsize=8.5)
arrow([(9.3, 3.1), (9.85, 3.1)], bus="32")

# adder
ax.add_patch(Circle((10.2, 3.1), 0.35, fc=GREEN, ec=INK, lw=1.4, zorder=2))
ax.text(10.2, 3.1, "+", ha="center", va="center", fontsize=18, weight="bold", zorder=3)
arrow([(10.55, 3.1), (11.05, 3.1)], bus="32")

# accumulator
reg(11.05, 2.6, 11.85, 3.6, "acc", "32 b")
arrow([(11.85, 3.1), (13.2, 3.1)])
ax.text(13.25, 3.1, "acc\n[31:0]", fontsize=10, family="monospace", va="center", weight="bold")

# feedback through clear mux
ax.plot([12.4, 12.4, 10.45], [3.1, 1.25, 1.25], color=INK, lw=1.4, zorder=1)
ax.add_patch(Circle((12.4, 3.1), 0.05, color=INK, zorder=3))
ax.add_patch(Polygon([[9.95, 0.85], [10.45, 1.0], [10.45, 1.7], [9.95, 1.85]],
                     fc="white", ec=INK, lw=1.3, zorder=2))
ax.text(10.38, 1.25, "0", fontsize=7, va="center", ha="right")
ax.text(10.38, 1.5, "1", fontsize=7, va="center", ha="right")
ax.plot([10.75, 10.45], [1.5, 1.5], color=INK, lw=1.2)
ax.text(10.8, 1.5, "0", fontsize=9, va="center", family="monospace")
ax.text(11.95, 1.15, "feedback", fontsize=8, color="#555", ha="center", va="top")
arrow([(9.95, 1.35), (9.6, 1.35), (9.6, 2.35), (10.2, 2.35), (10.2, 2.75)])

# control path
ax.text(0.0, 0.3, "en", fontsize=11, family="monospace", weight="bold", va="center")
ax.text(0.0, -0.75, "clr", fontsize=11, family="monospace", weight="bold", va="center")
arrow([(0.45, 0.3), (7.05, 0.3)])
arrow([(0.55, -0.75), (7.05, -0.75)])
reg(7.05, -0.05, 7.85, 0.65, "v_q", "")
reg(7.05, -1.1, 7.85, -0.4, "clr_q", "")
# v_q -> acc enable
arrow([(7.85, 0.3), (11.45, 0.3), (11.45, 2.6)])
ax.text(11.55, 0.45, "enable", fontsize=8, color="#555")
# clr_q -> mux select
arrow([(7.85, -0.75), (10.2, -0.75), (10.2, 0.92)])
ax.text(10.3, -0.6, "select", fontsize=8, color="#555")

ax.text(0.0, -1.3, "All registers: posedge clk, synchronous rst.  Latency: 2 cycles.  "
        "Throughput: 1 MAC / cycle.", fontsize=8.5, color="#444")

ax.set_title("Pipelined MAC unit  (rtl/mac.v)", fontsize=13, weight="bold", pad=4)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "mac_block_diagram.pdf"))
fig.savefig(os.path.join(OUT, "mac_block_diagram.png"), dpi=200)
print("saved results/mac_block_diagram.pdf/.png")
