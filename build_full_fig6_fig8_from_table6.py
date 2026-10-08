# -*- coding: utf-8 -*-
"""
Regenerate the COMPLETE two-panel Figure 6 and Figure 8 directly from the
authoritative Table 6 of the v12 manuscript. Nothing is inferred: every plotted
value is a cell of Table 6. Cells that Table 6 marks "—" (Qwen2.5-72B-INT8 and the
four Llama trap-derived cells, not re-measured after the trap correction) are drawn
as "not measured", never as zero and never guessed.

Palette matches the existing Figure 6/8 in the manuscript (image5/image6):
  OPUR / III-Gap(all)  blue  #1f6fb2
  attack / positive    orange#d2601a
  III-Gap(excl)        green #1f8a4c

Figure 6  (A) OPUR + confused-deputy attack success, INT4 configs by scale
          (B) III-Gap decomposition for the 18 configurations (all vs legit-high excluded)
Figure 8  (A) OPUR       (B) confused-deputy attack success
          Qwen2.5 & Qwen3 at FP16, Llama-3.1 at INT8

Run:  python build_full_fig6_fig8_from_table6.py
Out:  Figure6_full.{png,tif}  Figure8_full.{png,tif}   (300 dpi)
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.gridspec import GridSpec

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figures")
os.makedirs(OUT, exist_ok=True)

BLUE, ORANGE, GREEN = "#1f6fb2", "#d2601a", "#1f8a4c"
GRID, INK, MUTED = "#d8dce2", "#1a1d23", "#5a6270"
SMALL_BG, LARGE_BG = "#fdf0e6", "#eaf1f8"

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 11,
    "axes.edgecolor": INK, "axes.linewidth": 1.1, "text.color": INK,
})

# ------------------------------------------------------------------ Table 6 data
# Figure 6(A): the 8 INT4 configurations, ordered by parameter count.
# (label, OPUR %, OPUR count, attack success %)   -- all from Table 6, INT4 rows
F6A = [("Qwen2.5-7B", 19.9, 43, 55.6), ("Qwen3-8Bᵉ", 15.3, 33, 41.7),
       ("Llama-3.1-8B", 24.1, 52, 72.2), ("Qwen3-14Bᵉ", 25.5, 55, 70.8),
       ("Qwen2.5-32B", 2.3, 5, 5.6), ("Qwen3-32Bᵉ", 11.1, 24, 29.2),
       ("Llama-3.1-70B", 2.8, 6, 8.3), ("Qwen2.5-72B", 2.8, 6, 4.3)]
SMALL_N = 4   # first four are <=14B

# Figure 6(B): III-Gap decomposition, all 18 configurations (top -> bottom).
# (label, III-Gap all pp, III-Gap excl pp) ; None = "—" (not measured)
F6B = [("Q2.5-7B FP16", -15.7, +1.1), ("Q2.5-7B INT8", -15.7, +1.1),
       ("Q2.5-7B INT4", -15.7, +1.1),
       ("Q2.5-32B FP16", -19.9, -3.9), ("Q2.5-32B INT8", -19.9, -3.9),
       ("Q2.5-32B INT4", -20.4, -4.4),
       ("Q2.5-72B INT8", None, None), ("Q2.5-72B INT4", -22.2, -6.7),
       ("L-8B INT8", None, None), ("L-8B INT4", None, None),
       ("L-70B INT8", None, None), ("L-70B INT4", None, None),
       ("Q3-8B FP16ᵉ", -16.2, +0.6), ("Q3-8B INT4ᵉ", -16.7, 0.0),
       ("Q3-14B FP16ᵉ", -16.7, 0.0), ("Q3-14B INT4ᵉ", -16.2, +0.6),
       ("Q3-32B FP16ᵉ", -20.8, -5.0), ("Q3-32B INT4ᵉ", -16.7, 0.0)]

# Figure 8: 7 configurations (Qwen2.5/Qwen3 FP16, Llama INT8).
# (label, family, OPUR %, attack %)
F8 = [("7B", "Qwen2.5", 17.1, 47.2), ("32B", "Qwen2.5", 5.6, 13.9),
      ("8B", "Qwen3", 15.7, 41.7), ("14B", "Qwen3", 25.0, 69.4),
      ("32B", "Qwen3", 5.6, 12.5),
      ("8B", "Llama-3.1", 19.4, 58.3), ("70B", "Llama-3.1", 2.8, 8.3)]
FAM_COLOR = {"Qwen2.5": BLUE, "Qwen3": ORANGE, "Llama-3.1": GREEN}
FAM_HATCH = {"Qwen2.5": None, "Qwen3": "//", "Llama-3.1": ".."}


def _clean(ax):
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, color=GRID, linewidth=1.0); ax.xaxis.grid(False)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.tick_params(colors=MUTED, labelsize=10)
    for lbl in ax.get_yticklabels() + ax.get_xticklabels():
        lbl.set_color(MUTED)


# ============================================================== FIGURE 6
fig = plt.figure(figsize=(13.2, 5.2), dpi=300)
gs = GridSpec(1, 2, width_ratios=[1.0, 1.12], wspace=0.28, figure=fig)

# ---- panel (A): grouped OPUR + attack, INT4, by scale
axA = fig.add_subplot(gs[0, 0])
n = len(F6A); w = 0.38
axA.axvspan(-0.5, SMALL_N - 0.5, color=SMALL_BG, zorder=0)
axA.axvspan(SMALL_N - 0.5, n - 0.5, color=LARGE_BG, zorder=0)
for i, (lab, opur, cnt, atk) in enumerate(F6A):
    axA.bar(i - w / 2, opur, width=w, color=BLUE, zorder=3)
    axA.bar(i + w / 2, atk, width=w, color=ORANGE, hatch="//",
            edgecolor="white", linewidth=0.0, zorder=3)
_clean(axA)
axA.set_ylim(0, 80); axA.set_yticks(range(0, 81, 20)); axA.set_ylabel("Rate (%)")
axA.set_xlim(-0.5, n - 0.5)
axA.set_xticks(range(n))
axA.set_xticklabels([l for l, *_ in F6A], rotation=30, ha="right", fontsize=9)
axA.text(SMALL_N / 2 - 0.5, 77, "small (≤14B)", ha="center", color=MUTED, fontsize=10)
axA.text((SMALL_N + n) / 2 - 0.5, 77, "large (≥32B)", ha="center", color=MUTED, fontsize=10)
axA.set_title("(A)  Scale effect (INT4 configurations)",
              fontsize=12, fontweight="bold", loc="left")
axA.legend(handles=[Patch(facecolor=BLUE, label="OPUR (intent over-privilege)"),
                    Patch(facecolor=ORANGE, hatch="//", edgecolor="white",
                          label="Confused-deputy attack success")],
           loc="upper right", bbox_to_anchor=(0.99, 0.73), frameon=False, fontsize=9.5)

# ---- panel (B): III-Gap decomposition, horizontal diverging, 18 configs
axB = fig.add_subplot(gs[0, 1])
labels = [x[0] for x in F6B]
ys = list(range(len(F6B)))[::-1]        # first config at top
bh = 0.38
for y, (lab, allg, excl) in zip(ys, F6B):
    if allg is None:
        axB.text(0.3, y, "not measured", va="center", ha="left",
                 color="#9aa1ab", fontsize=8.5, style="italic")
        continue
    axB.barh(y + bh / 2, allg, height=bh, color=BLUE, zorder=3)
    axB.barh(y - bh / 2, excl, height=bh, color=GREEN, zorder=3)
_clean(axB)
axB.axvline(0, color=INK, linewidth=1.1)
axB.set_yticks(ys); axB.set_yticklabels(labels, fontsize=8.3)
axB.set_xlim(-26, 12); axB.set_xticks(range(-25, 11, 5))
axB.set_xlabel("III-Gap (pp)")
axB.set_title("(B)  III-Gap decomposition (18 configurations)",
              fontsize=12, fontweight="bold", loc="left")
axB.annotate("definitional shift\n= legit-high 16.7 pp",
             xy=(-16.7, ys[3] + bh / 2), xytext=(-24.5, ys[6]),
             ha="left", va="center", color=MUTED, fontsize=8.5,
             arrowprops=dict(arrowstyle="->", color=MUTED, lw=1.0,
                             connectionstyle="arc3,rad=0.15"))
axB.legend(handles=[Patch(facecolor=BLUE, label="III-Gap (all 216 tasks)"),
                    Patch(facecolor=GREEN, label="III-Gap (legit-high excluded)")],
           loc="lower left", frameon=False, fontsize=9)
fig.text(0.5, -0.02, "ᵉ exploratory (Qwen3, added after the a priori design)",
         ha="center", color=MUTED, fontsize=8.5)
fig.savefig(os.path.join(OUT, "Figure6_full.png"), dpi=300, bbox_inches="tight")
fig.savefig(os.path.join(OUT, "Figure6_full.tif"), dpi=300, bbox_inches="tight",
            pil_kwargs={"compression": "tiff_lzw"})
plt.close(fig)

# ============================================================== FIGURE 8
fig = plt.figure(figsize=(12.4, 4.8), dpi=300)
gs = GridSpec(1, 2, wspace=0.22, figure=fig)


def _fam_panel(ax, values, ylabel, title, ymax, outlier_idx=None):
    x = 0; xs = []; prev = None
    for i, (lab, fam, opur, atk) in enumerate(F8):
        if prev is not None and fam != prev:
            x += 0.7
        v = values[i]
        ax.bar(x, v, width=0.72, color=FAM_COLOR[fam], hatch=FAM_HATCH[fam],
               edgecolor="white", linewidth=0.0, zorder=3)
        ax.text(x, v + ymax * 0.012, f"{v:.1f}", ha="center", va="bottom", fontsize=10)
        xs.append((x, lab)); prev = fam; x += 1
    _clean(ax)
    ax.set_ylim(0, ymax); ax.set_ylabel(ylabel)
    ax.set_xticks([p for p, _ in xs]); ax.set_xticklabels([l for _, l in xs])
    ax.set_title(title, fontsize=12, fontweight="bold", loc="left")
    if outlier_idx is not None:
        ox = xs[outlier_idx][0]; ov = values[outlier_idx]
        ax.annotate("Qwen3-14B outlier", xy=(ox + 0.3, ov), xytext=(ox + 1.2, ymax * 0.82),
                    ha="left", color=MUTED, fontsize=9,
                    arrowprops=dict(arrowstyle="->", color=MUTED, lw=1.0,
                                    connectionstyle="arc3,rad=0.2"))
    return xs


ax1 = fig.add_subplot(gs[0, 0])
_fam_panel(ax1, [r[2] for r in F8], "OPUR (%)",
           "(A)  Intent over-privilege", 30, outlier_idx=3)
ax2 = fig.add_subplot(gs[0, 1])
xs = _fam_panel(ax2, [r[3] for r in F8], "Attack success (%)",
                "(B)  Confused-deputy attack success", 80, outlier_idx=None)
ax2.legend(handles=[Patch(facecolor=FAM_COLOR[f], hatch=FAM_HATCH[f], edgecolor="white",
                          label=f) for f in ("Qwen2.5", "Qwen3", "Llama-3.1")],
           loc="upper right", frameon=False, fontsize=9.5)
fig.savefig(os.path.join(OUT, "Figure8_full.png"), dpi=300, bbox_inches="tight")
fig.savefig(os.path.join(OUT, "Figure8_full.tif"), dpi=300, bbox_inches="tight",
            pil_kwargs={"compression": "tiff_lzw"})
plt.close(fig)
print("written: Figure6_full.{png,tif}  Figure8_full.{png,tif}")
