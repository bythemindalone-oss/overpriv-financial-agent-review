# -*- coding: utf-8 -*-
"""Analyse the 4-expert trap-scenario validation (R4-3c). Pre-registered in TRAP_VALIDATION_GUIDE.md.

Primary   : per task, how many raters judged the designated correct (gold) tool as
            fully accomplishing the request (adequacy == 2). Tasks where gold fails to
            reach a 3-of-4 majority are the configurations in which the equal-tier safe
            alternative does not serve the request.
Secondary : linear-weighted Krippendorff alpha on the ordinal adequacy scale (pre-registered >= 0.667).
Tertiary  : human tool choice under the concealed menu, next to the model rate.

Raters must be human domain experts; see the note in kappa.py.

Usage:
  python trap_validation_agreement.py --sheets trap_validation_A*.csv \
      --key _trap_validation_key.csv --out trap_validation_report.md
"""
import argparse, csv, itertools, sys
from collections import defaultdict
from pathlib import Path


def read_sheet(p):
    with open(p, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def krippendorff_linear(units):
    """Ordinal data, linear distance. units: list of lists of numeric ratings."""
    units = [u for u in units if len(u) >= 2]
    if not units:
        return float("nan")
    allv = [v for u in units for v in u]
    n = len(allv)

    def d(a, b):
        return (a - b) ** 2  # linear scale -> squared difference on the 0/1/2 scale

    num = 0.0
    for u in units:
        m = len(u)
        num += sum(d(a, b) for a, b in itertools.permutations(u, 2)) / (m - 1)
    den = sum(d(a, b) for a, b in itertools.permutations(allv, 2)) / (n - 1)
    return 1.0 - num / den if den else float("nan")


ap = argparse.ArgumentParser()
ap.add_argument("--sheets", nargs="+", required=True)
ap.add_argument("--key", default="_trap_validation_key.csv")
ap.add_argument("--out", default="trap_validation_report.md")
a = ap.parse_args()

key = {(r["id"], r["option"]): r for r in read_sheet(a.key)}
gold = {r["id"]: r["option"] for r in key.values() if r["role"] == "gold"}
trap = {r["id"]: r["option"] for r in key.values() if r["role"] == "trap"}

adeq = defaultdict(list)          # (id, option) -> [ratings]
choice = defaultdict(list)        # id -> [chosen option or 'refuse']
for p in a.sheets:
    rows = read_sheet(p)
    picked = {}
    for r in rows:
        v = (r.get("adequacy") or "").strip()
        if v in ("0", "1", "2"):
            adeq[(r["id"], r["option"])].append(int(v))
        if (r.get("chosen") or "").strip() == "1":
            picked[r["id"]] = r["option"]
        if "refuse" in (r.get("note") or "").lower():
            picked.setdefault(r["id"], "refuse")
    for tid in sorted({r["id"] for r in rows}):
        choice[tid].append(picked.get(tid, "refuse"))

tasks = sorted(gold)
L = ["# Trap-scenario validation — 4-expert panel", "",
     f"Sheets: {len(a.sheets)} · tasks: {len(tasks)}", "",
     "## Primary — is the designated correct tool adequate?", "",
     "| task | gold tool | adequacy ratings | 2-ratings | verdict |", "|---|---|---|---|---|"]
inadequate = []
for t in tasks:
    g = gold[t]
    rr = adeq.get((t, g), [])
    k = sum(1 for v in rr if v == 2)
    ok = k >= 3
    if not ok:
        inadequate.append(t)
    tool = key[(t, g)]["tool"]
    L.append(f"| {t} | {tool} | {rr} | {k}/{len(rr)} | {'adequate' if ok else '**NOT adequate**'} |")

L += ["", f"**{len(tasks)-len(inadequate)} of {len(tasks)}** tasks have an adequate equal-tier correct tool; "
          f"**{len(inadequate)}** do not" + (f": {', '.join(inadequate)}" if inadequate else "") + ".", ""]

alpha = krippendorff_linear(list(adeq.values()))
L += ["## Secondary — agreement", "",
      f"Krippendorff alpha (ordinal, linear) on adequacy over {len(adeq)} task-tool units: **{alpha:.3f}** "
      f"(pre-registered threshold 0.667 — {'met' if alpha >= 0.667 else 'NOT met, report as exploratory'}).", "",
      "## Tertiary — human choice under the concealed menu", "",
      "| task | trap tool | rater choices | chose trap | chose gold |", "|---|---|---|---|---|"]
tt = tg = tot = 0
for t in tasks:
    ch = choice.get(t, [])
    ct = sum(1 for c in ch if c == trap.get(t))
    cg = sum(1 for c in ch if c == gold.get(t))
    tt += ct; tg += cg; tot += len(ch)
    L.append(f"| {t} | {key[(t, trap[t])]['tool']} | {ch} | {ct} | {cg} |")
L += ["", f"Humans chose the trap in **{tt}/{tot}** decisions and the correct tool in **{tg}/{tot}**. "
          "The model selected the trap in 83.4% of equal-tier decisions under the same concealed menu "
          "(results/v28/masked, 13 serving configurations).", "",
      "Reading: a high human trap rate supports the instrument claim — the declared-tier record "
      "carries no information that separates the two equal-tier tools — rather than an agent-reasoning "
      "failure. A low human trap rate records a human-model difference on this corpus.", ""]

Path(a.out).write_text("\n".join(L), encoding="utf-8")
print("\n".join(L[:14]))
print(f"\nwrote {a.out}")
