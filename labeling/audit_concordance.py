# -*- coding: utf-8 -*-
"""Single-expert audit concordance: compare an independent expert's blind labels
(audit_sheet_36.csv, filled) against the released gold. Reports exact agreement,
weighted Cohen's kappa (min_tier, linear) of expert-vs-gold, and correct_behavior
agreement. This is the *validity* audit for §4.1 (lighter than a full 2-annotator
kappa): one qualified expert re-derives labels from codebook v2, blind to gold.

Run:  python labeling/audit_concordance.py --audit annotation_audit_36.csv
"""
from __future__ import annotations
import argparse
import csv
import sys

sys.path.insert(0, ".")
from overpriv.corpus_gen import build_corpus


def cohen_kappa(pairs, weighted=True, cats=(1, 2, 3, 4, 5)):
    K = len(cats); idx = {c: i for i, c in enumerate(cats)}
    n = len(pairs)
    if n == 0:
        return None
    O = [[0] * K for _ in range(K)]
    for a, b in pairs:
        O[idx[a]][idx[b]] += 1
    r = [sum(O[i]) for i in range(K)]
    c = [sum(O[i][j] for i in range(K)) for j in range(K)]

    def w(i, j):
        return abs(cats[i] - cats[j]) / (K - 1) if weighted else (0 if i == j else 1)
    num = sum(w(i, j) * O[i][j] for i in range(K) for j in range(K))
    den = sum(w(i, j) * r[i] * c[j] / n for i in range(K) for j in range(K))
    return round(1 - num / den, 4) if den else None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--audit", required=True, help="filled audit_sheet_36.csv")
    a = ap.parse_args()
    gold = {t["task_id"]: t for t in build_corpus()}
    rows = list(csv.DictReader(open(a.audit, encoding="utf-8-sig")))
    mt_pairs, cb_ok, cb_n, miss = [], 0, 0, []
    for r in rows:
        tid = r["id"]; g = gold.get(tid)
        if not g:
            continue
        try:
            et = int(str(r.get("min_tier", "")).strip())
        except ValueError:
            miss.append(tid); continue
        mt_pairs.append((g["gold_tier"], et))
        # correct_behavior: attack -> refuse/escalate ; else select_tool
        exp = "refuse" if g["label"] == "attack" else "select_tool"
        cb = str(r.get("correct_behavior", "")).strip().lower()
        if cb:
            cb_n += 1
            if (g["label"] == "attack" and cb in ("refuse", "escalate")) or \
               (g["label"] != "attack" and cb == "select_tool"):
                cb_ok += 1
    exact = sum(1 for x, y in mt_pairs if x == y) / len(mt_pairs) if mt_pairs else None
    kw = cohen_kappa(mt_pairs, weighted=True)
    print(f"audited: {len(mt_pairs)} (unfilled/skipped: {len(miss)})")
    print(f"min_tier exact agreement (expert vs gold): {round(exact,4) if exact is not None else None}")
    print(f"min_tier weighted kappa (linear):          {kw}   (target >= 0.70)")
    print(f"correct_behavior agreement:                {round(cb_ok/cb_n,4) if cb_n else None} ({cb_ok}/{cb_n})")
    if miss:
        print("unfilled ids:", ", ".join(miss[:10]), ("..." if len(miss) > 10 else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
