# -*- coding: utf-8 -*-
"""
Regenerate Figures 1-5 and 7 in the canonical palette that Figures 6 and 8 use,
so the whole figure set is stylistically consistent. Figures 6 and 8 are produced
by build_full_fig6_fig8_from_table6.py (same palette) and are not touched here.

Data provenance (nothing invented):
  Fig 1  schematic (dual-measurement pipeline)               -- diagram
  Fig 2  reference-policy intent vs impact (Table 3)         -- Table 3
  Fig 3  reference-policy III-Gap, bidirectional (Table 3)   -- Table 3
  Fig 4  per-domain intent vs impact under P_confused        -- computed live from the released corpus
  Fig 5  gold-label reliability, 3 panels                    -- released reliability table (Table 5 / a18)
  Fig 7  primary-endpoint MEagent dumbbell (n=12)            -- results/masked + results/leaked_traps

Run from the reproduction-bundle root:  python make_all_figures_unified.py
Outputs 300-dpi PNG + LZW TIF to OUT.
"""
from __future__ import annotations
import os, json, csv
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Patch
from matplotlib.lines import Line2D

# ----- canonical palette (identical to build_full_fig6_fig8_from_table6.py) -----
BLUE, ORANGE, GREEN = "#1f6fb2", "#d2601a", "#1f8a4c"
GRID, INK, MUTED = "#d8dce2", "#1a1d23", "#5a6270"
BLUE_T, ORANGE_T, VIOLET_T, GREY_T = "#dbe8f3", "#f6e0d0", "#e4def0", "#e9ecef"

# Repo-self-contained: write into the bundle's figures/ so a fresh clone reproduces
# the manuscript figures with `python make_all_figures_unified.py`.
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figures")
os.makedirs(OUT, exist_ok=True)

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 11,
    "axes.edgecolor": INK, "axes.linewidth": 1.1, "text.color": INK,
})


def _save(fig, stem):
    fig.savefig(os.path.join(OUT, stem + ".png"), dpi=300, bbox_inches="tight")
    fig.savefig(os.path.join(OUT, stem + ".tif"), dpi=300, bbox_inches="tight",
                pil_kwargs={"compression": "tiff_lzw"})
    plt.close(fig)


def _clean(ax, ygrid=True):
    ax.set_axisbelow(True)
    if ygrid:
        ax.yaxis.grid(True, color=GRID, linewidth=1.0)
    ax.xaxis.grid(False)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.tick_params(colors=MUTED, labelsize=10)
    for lbl in ax.get_yticklabels() + ax.get_xticklabels():
        lbl.set_color(MUTED)


# =========================================================== FIGURE 1 (schematic)
def figure1():
    fig, ax = plt.subplots(figsize=(13.8, 5.6), dpi=300)
    ax.set_xlim(0, 120); ax.set_ylim(0, 62); ax.axis("off")

    def box(x, y, w, h, text, face, fs=11):
        ax.add_patch(FancyBboxPatch((x, y), w, h,
                     boxstyle="round,pad=0.6,rounding_size=1.6",
                     facecolor=face, edgecolor=INK, linewidth=1.3))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
                fontsize=fs, color=INK)

    def arrow(x1, y1, x2, y2):
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2),
                     arrowstyle="-|>", mutation_scale=18, lw=1.8, color=INK))

    # air-gapped boundary
    ax.add_patch(FancyBboxPatch((1.5, 2), 116, 58,
                 boxstyle="round,pad=0.2,rounding_size=1.5",
                 facecolor="none", edgecolor=MUTED, linewidth=1.6, linestyle=(0, (7, 5))))
    ax.text(3.5, 57, "Air-gapped boundary  (no external Internet · full audit-log retention)",
            fontsize=11, style="italic", color=MUTED)

    box(4, 24, 17, 13, "Shared request\n(users of\ndiffering roles)", GREY_T)
    box(26, 24, 15, 13, "Gateway\n(prompt filter,\nrole verify)", GREY_T)
    box(46, 24, 15, 13, "vLLM serving\n(tool-calling)", "#d6d9dd")
    box(68, 39, 26, 13, "Selection log  (INTENT)\nΔtier ≥ 1\n→ over-privilege rate", BLUE_T, fs=10.5)
    box(68, 9, 26, 13, "Deterministic sandbox (IMPACT)\nMock IAM/DB snapshot diff\n→ escalation rate", ORANGE_T, fs=10)
    box(101, 24, 13, 13, "III-Gap\n= intent\n− impact", VIOLET_T, fs=11)

    arrow(21, 30.5, 26, 30.5)
    arrow(41, 30.5, 46, 30.5)
    arrow(61, 30.5, 68, 44)
    arrow(61, 30.5, 68, 17)
    arrow(94, 44, 101, 32)
    arrow(94, 17, 101, 29)
    ax.add_patch(FancyArrowPatch((81, 39), (81, 22), arrowstyle="<->",
                 mutation_scale=13, lw=1.2, color=MUTED, linestyle=(0, (3, 3))))
    ax.text(81, 30.5, "dual-confirmed\n(both axes agree)", fontsize=9, color=MUTED,
            va="center", ha="center",
            bbox=dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor="none"))
    _save(fig, "Figure1_full")


# =========================================================== FIGURE 2
def figure2():
    # Table 3: (policy, intent %, impact %)
    P = [("P_gold\n(least priv.)", 0.0, 18.2), ("P_greedy\n(moderate)", 90.9, 72.7),
         ("P_naive\n(maximum)", 90.9, 100.0), ("P_confused\n(conf. deputy)", 36.4, 53.0)]
    fig, ax = plt.subplots(figsize=(7.6, 4.8), dpi=300)
    w = 0.38
    for i, (lab, it, im) in enumerate(P):
        ax.bar(i - w / 2, it, width=w, color=BLUE, zorder=3)
        ax.bar(i + w / 2, im, width=w, color=ORANGE, hatch="//",
               edgecolor="white", linewidth=0, zorder=3)
        ax.text(i - w / 2, it + 1.5, f"{it:.1f}", ha="center", fontsize=9, color=MUTED)
        ax.text(i + w / 2, im + 1.5, f"{im:.1f}", ha="center", fontsize=9, color=MUTED)
    _clean(ax)
    ax.set_ylim(0, 136); ax.set_yticks(range(0, 101, 20)); ax.set_ylabel("Rate (%)")
    ax.set_xticks(range(len(P))); ax.set_xticklabels([p[0] for p in P], fontsize=9)
    ax.annotate("MEdef signature:  0% intent vs 18.2% impact",
                xy=(0 + w / 2, 19), xytext=(-0.36, 122),
                fontsize=9, color=MUTED, ha="left", va="center",
                arrowprops=dict(arrowstyle="->", color=MUTED, lw=1.0,
                                connectionstyle="arc3,rad=0.0"))
    ax.legend(handles=[Patch(facecolor=BLUE, label="Intent over-privilege (behavioral)"),
                       Patch(facecolor=ORANGE, hatch="//", edgecolor="white",
                             label="Impact escalation (executed)")],
              loc="upper right", frameon=False, fontsize=9)
    _save(fig, "Figure2_full")


# =========================================================== FIGURE 3
def figure3():
    # Table 3 III-Gap by policy
    P = [("P_gold", -18.2), ("P_greedy", +18.2), ("P_naive", -9.1), ("P_confused", -16.7)]
    fig, ax = plt.subplots(figsize=(7.2, 4.4), dpi=300)
    for i, (lab, g) in enumerate(P):
        c = ORANGE if g > 0 else BLUE
        ax.bar(i, g, width=0.56, color=c, zorder=3)
        va = "bottom" if g > 0 else "top"
        off = 0.6 if g > 0 else -0.6
        ax.text(i, g + off, f"{g:+.1f}", ha="center", va=va, fontsize=9.5, color=MUTED)
    _clean(ax)
    ax.axhline(0, color=INK, linewidth=1.1)
    ax.set_ylim(-24, 24); ax.set_yticks(range(-20, 21, 10))
    ax.set_ylabel("III-Gap (pp)")
    ax.set_xticks(range(len(P))); ax.set_xticklabels([p[0] for p in P])
    ax.text(0.02, 0.95, "over-counting  (intent > impact)", transform=ax.transAxes,
            fontsize=8.5, color=ORANGE, va="top")
    ax.text(0.02, 0.06, "under-counting  (impact > intent)", transform=ax.transAxes,
            fontsize=8.5, color=BLUE, va="bottom")
    _save(fig, "Figure3_full")


# =========================================================== FIGURE 4
def figure4():
    from overpriv.corpus_gen import build_corpus
    from overpriv.sandbox import execute
    from overpriv.policies import REFERENCE_POLICIES
    pol = next(v for k, v in REFERENCE_POLICIES.items() if "confused" in k.lower())
    tasks = build_corpus()
    ms = [execute(t, pol(t)) for t in tasks]
    agg = {}
    for t, m in zip(tasks, ms):
        d = m.domain
        a = agg.setdefault(d, [0, 0, 0])
        a[0] += 1
        a[1] += 1 if m.intent_overpriv else 0
        a[2] += 1 if m.impact else 0
    DNAME = {"D1": "D1 Server\naccess", "D2": "D2 Database\noperations",
             "D3": "D3 Networking", "D4": "D4 Service/\nprocess",
             "D5": "D5 Secrets/\ncredentials", "D6": "D6 Audit/\nlogging"}
    doms = sorted(agg)
    intent = [100 * agg[d][1] / agg[d][0] for d in doms]
    impact = [100 * agg[d][2] / agg[d][0] for d in doms]
    fig, ax = plt.subplots(figsize=(8.6, 4.6), dpi=300)
    w = 0.38
    for i, d in enumerate(doms):
        ax.bar(i - w / 2, intent[i], width=w, color=BLUE, zorder=3)
        ax.bar(i + w / 2, impact[i], width=w, color=ORANGE, hatch="//",
               edgecolor="white", linewidth=0, zorder=3)
        ax.text(i - w / 2, intent[i] + 1.2, f"{intent[i]:.1f}", ha="center", fontsize=8.5, color=MUTED)
        ax.text(i + w / 2, impact[i] + 1.2, f"{impact[i]:.1f}", ha="center", fontsize=8.5, color=MUTED)
    _clean(ax)
    ax.set_ylim(0, 68); ax.set_yticks(range(0, 61, 20)); ax.set_ylabel("Rate (%)")
    ax.set_xticks(range(len(doms))); ax.set_xticklabels([DNAME[d] for d in doms], fontsize=8.5)
    ax.set_title("Under P_confused, impact escalation exceeds intent over-privilege in all six domains",
                 fontsize=10.5, color=MUTED, loc="left")
    ax.legend(handles=[Patch(facecolor=BLUE, label="Intent over-privilege"),
                       Patch(facecolor=ORANGE, hatch="//", edgecolor="white",
                             label="Impact escalation")],
              loc="upper right", frameon=False, fontsize=9)
    _save(fig, "Figure4_full")
    return {d: (round(100 * agg[d][1] / agg[d][0], 1), round(100 * agg[d][2] / agg[d][0], 1),
                round(100 * (agg[d][1] - agg[d][2]) / agg[d][0], 1)) for d in doms}


# =========================================================== FIGURE 5
PAIRS = ["E1-E2", "E1-E3", "E1-E4", "E2-E3", "E2-E4", "E3-E4"]
TIER_K = [0.840, 0.905, 0.857, 0.843, 0.781, 0.852]
BEH_K = [0.902, 0.873, 0.914, 0.860, 0.900, 0.872]
UNANIM = {"5-level\nexact": 64.1, "≥T2": 87.4, "≥T3": 85.9, "≥T4": 92.9}
MEDEF = {"E1": 16.2, "E2": 17.6, "E3": 14.4, "E4": 17.6, "Consensus": 16.2}


def figure5():
    fig, ax = plt.subplots(1, 3, figsize=(13.0, 4.0), dpi=300)
    x = range(len(PAIRS)); w = 0.38
    ax[0].bar([i - w / 2 for i in x], TIER_K, w, color=BLUE, zorder=3, label="Minimum required tier")
    ax[0].bar([i + w / 2 for i in x], BEH_K, w, color=ORANGE, hatch="//", edgecolor="white",
              linewidth=0, zorder=3, label="Required behavior")
    ax[0].axhline(0.70, ls="--", lw=1.1, color=MUTED)
    ax[0].text(len(PAIRS) - 0.5, 0.71, "target 0.70", color=MUTED, fontsize=7.5, ha="right")
    ax[0].set_xticks(list(x)); ax[0].set_xticklabels(PAIRS, fontsize=8); ax[0].set_ylim(0.6, 1.0)
    ax[0].set_ylabel("Weighted kappa (linear)", fontsize=9)
    ax[0].set_title("(A)  Pairwise agreement", fontsize=11, fontweight="bold", loc="left")
    ax[0].legend(fontsize=8, frameon=False, loc="upper center",
                 bbox_to_anchor=(0.5, -0.14), ncol=2)
    labs = list(UNANIM); vals = list(UNANIM.values()); cols = [MUTED, BLUE, BLUE, GREEN]
    ax[1].bar(labs, vals, color=cols, width=0.62, zorder=3)
    for i, v in enumerate(vals):
        ax[1].text(i, v + 1, f"{v:.1f}", ha="center", fontsize=8.5, color=MUTED)
    ax[1].set_ylim(0, 105); ax[1].set_ylabel("Four-way unanimity (%)", fontsize=9)
    ax[1].set_title("(B)  Unanimity by dichotomy", fontsize=11, fontweight="bold", loc="left")
    who = list(MEDEF); me = list(MEDEF.values())
    ax[2].bar(who, me, color=[BLUE] * 4 + [ORANGE], width=0.6, zorder=3)
    ax[2].axhline(16.7, ls="--", lw=1.2, color=MUTED)
    ax[2].text(4.4, 17.0, "released 16.7%", color=MUTED, fontsize=7.5, ha="right")
    for i, v in enumerate(me):
        ax[2].text(i, v + 0.25, f"{v:.1f}", ha="center", fontsize=8.5, color=MUTED)
    ax[2].set_ylim(0, 20); ax[2].set_ylabel("MEdef (% of 216 tasks)", fontsize=9)
    ax[2].set_title("(C)  MEdef sensitivity to labeler", fontsize=11, fontweight="bold", loc="left")
    for a in ax:
        _clean(a)
    _save(fig, "Figure5_full")


# =========================================================== FIGURE 7
def _gold_tasks():
    g = set()
    with open("results/a08/trap_outcomes.csv", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            if r["declared==gold"].strip().lower() == "true":
                g.add(r["task_id"])
    return g


def _me12(path, gold):
    d = json.load(open(path, encoding="utf-8"))
    rows = [t for t in d["per_task"] if t["task_id"] in gold]
    hit = sum(1 for t in rows if t["impact"] == 1 and t["intent_overpriv"] == 0)
    return 100.0 * hit / len(rows)


def figure7():
    gold = _gold_tasks()
    order = ["qwen2.5-7b_fp16", "qwen2.5-7b_int8", "qwen2.5-7b_int4",
             "qwen2.5-32b_fp16", "qwen2.5-32b_int8", "qwen2.5-32b_int4",
             "qwen2.5-72b_int4", "qwen3-8b_fp16", "qwen3-8b_int4",
             "qwen3-14b_fp16", "qwen3-14b_int4", "qwen3-32b_fp16", "qwen3-32b_int4"]

    def lab(c):
        base, q = c.rsplit("_", 1)
        base = base.replace("qwen2.5-", "Qwen2.5-").replace("qwen3-", "Qwen3-")
        return f"{base[:-1] + base[-1].upper()}  {q.upper()}"

    conc = [_me12(f"results/masked/{c}.json", gold) for c in order]
    disc = [_me12(f"results/leaked_traps/{c}.json", gold) for c in order]
    mc, md = sum(conc) / len(conc), sum(disc) / len(disc)
    n = len(order); y = list(range(n))
    fig, ax = plt.subplots(figsize=(7.6, 5.6), dpi=300)
    for i in range(n):
        ax.plot([disc[i], conc[i]], [y[i], y[i]], color="#b6bcc4", lw=1.8, zorder=1)
    ax.scatter(disc, y, s=48, color=BLUE, zorder=3)
    ax.scatter(conc, y, s=48, color=ORANGE, zorder=3)
    ax.axvline(16.7, ls="--", lw=1.1, color=MUTED)
    ax.text(16.7, n - 0.3, " chance 16.7%", color=MUTED, fontsize=8, va="center")
    ax.axvline(mc, ls=":", lw=1.0, color=ORANGE, alpha=0.8)
    ax.axvline(md, ls=":", lw=1.0, color=BLUE, alpha=0.8)
    ax.text(mc, -1.15, f"mean {mc:.1f}%", color=ORANGE, fontsize=8, ha="center")
    ax.text(md, -1.15, f"mean {md:.1f}%", color=BLUE, fontsize=8, ha="center")
    ax.set_yticks(y); ax.set_yticklabels([lab(c) for c in order], fontsize=8.5); ax.invert_yaxis()
    ax.set_xlim(0, 105); ax.set_xticks(range(0, 101, 20))
    ax.set_xlabel("MEagent (%)  —  trap tasks with declared tier = gold (n = 12)", fontsize=9.5)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.grid(axis="x", ls=":", alpha=0.35, color=GRID)
    ax.tick_params(colors=MUTED)
    ax.legend(handles=[Line2D([0], [0], marker="o", color="w", markerfacecolor=ORANGE, markersize=9, label="Concealed"),
                       Line2D([0], [0], marker="o", color="w", markerfacecolor=BLUE, markersize=9, label="Disclosed")],
              loc="lower right", fontsize=9, frameon=False)
    _save(fig, "Figure7_full")
    return mc, md


if __name__ == "__main__":
    figure1(); print("Figure1_full  written (schematic)")
    figure2(); print("Figure2_full  written (Table 3 intent/impact)")
    figure3(); print("Figure3_full  written (Table 3 III-Gap)")
    g4 = figure4(); print("Figure4_full  written (P_confused per-domain):", g4)
    figure5(); print("Figure5_full  written (reliability 3-panel)")
    mc, md = figure7(); print(f"Figure7_full  written (MEagent concealed {mc:.1f} / disclosed {md:.1f})")
    print("OUT:", OUT)
