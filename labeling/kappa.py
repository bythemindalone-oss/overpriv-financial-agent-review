# -*- coding: utf-8 -*-
"""Compute inter-annotator agreement (weighted Cohen's kappa) for the gold labels.

Two qualified HUMAN annotators (A1, A2) each fill a copy of annotation_blank.csv
(columns min_tier / allowed_tools / correct_behavior). This script:
  - weighted Cohen's kappa on `min_tier` (ordinal, linear weights)  -> primary
  - Cohen's kappa (nominal) + % agreement on `correct_behavior`     -> secondary
  - writes disagreements.csv for A3 adjudication
Target (pre-registered): weighted kappa >= 0.70 (substantial).

NOTE: annotators MUST be human domain experts (SRE/DBA/security-ops). An LLM
cannot substitute here — kappa's purpose is to show independent HUMAN experts
converge, which an LLM annotator cannot establish (and would undermine, given
this paper studies LLM misjudgment of tool privilege).

Usage:
  python kappa.py --a1 annotation_A1.csv --a2 annotation_A2.csv --out labeling_report.md
"""
import argparse, csv
from collections import Counter
from pathlib import Path

def read(path, col):
    out = {}
    with open(path, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            v = (row.get(col) or "").strip()
            if v != "":
                out[row["id"]] = v
    return out

def cohen_kappa(pairs, weighted=False, cats=None):
    """pairs: list of (a1, a2). weighted=linear ordinal weights (ints expected)."""
    if not pairs:
        return None, 0
    if cats is None:
        cats = sorted({p for pr in pairs for p in pr})
    idx = {c: i for i, c in enumerate(cats)}
    K = len(cats)
    n = len(pairs)
    O = [[0] * K for _ in range(K)]
    for a, b in pairs:
        O[idx[a]][idx[b]] += 1
    r = [sum(O[i]) for i in range(K)]
    c = [sum(O[i][j] for i in range(K)) for j in range(K)]
    def w(i, j):
        if not weighted:
            return 0 if i == j else 1
        return abs(i - j) / (K - 1) if K > 1 else 0
    num = sum(w(i, j) * O[i][j] for i in range(K) for j in range(K))
    den = sum(w(i, j) * r[i] * c[j] / n for i in range(K) for j in range(K))
    if den == 0:
        return 1.0, n
    return round(1 - num / den, 4), n

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--a1", required=True); ap.add_argument("--a2", required=True)
    ap.add_argument("--out", default="labeling_report.md")
    a = ap.parse_args()

    mt1, mt2 = read(a.a1, "min_tier"), read(a.a2, "min_tier")
    cb1, cb2 = read(a.a1, "correct_behavior"), read(a.a2, "correct_behavior")
    ids = sorted(set(mt1) & set(mt2))
    if not ids:
        raise SystemExit("[error] no overlapping labeled ids — are both sheets filled?")

    mt_pairs = [(int(mt1[i]), int(mt2[i])) for i in ids]
    kw, n = cohen_kappa(mt_pairs, weighted=True, cats=[1, 2, 3, 4, 5])
    ku, _ = cohen_kappa(mt_pairs, weighted=False, cats=[1, 2, 3, 4, 5])
    agree = sum(1 for x, y in mt_pairs if x == y) / n

    cb_ids = sorted(set(cb1) & set(cb2))
    cb_pairs = [(cb1[i], cb2[i]) for i in cb_ids]
    cbk, _ = cohen_kappa(cb_pairs) if cb_pairs else (None, 0)
    cb_agree = (sum(1 for x, y in cb_pairs if x == y) / len(cb_pairs)) if cb_pairs else None

    dis = [i for i in ids if mt1[i] != mt2[i]]
    with open("disagreements.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f); w.writerow(["id", "A1_min_tier", "A2_min_tier", "A3_adjudicated"])
        for i in dis:
            w.writerow([i, mt1[i], mt2[i], ""])

    verdict = "PASS (>=0.70)" if (kw is not None and kw >= 0.70) else "BELOW TARGET (<0.70) -> recalibrate (protocol §4.3)"
    lines = [
        "# Labeling Report — inter-annotator agreement", "",
        f"- N labeled (both annotators): **{n}**",
        f"- **Weighted Cohen's kappa (min_tier, linear)**: **{kw}**  -> {verdict}",
        f"- Unweighted kappa (min_tier): {ku}",
        f"- Exact agreement (min_tier): {round(agree,4)}",
        f"- correct_behavior: kappa={cbk}, agreement={None if cb_agree is None else round(cb_agree,4)}",
        f"- Disagreements written to `disagreements.csv`: **{len(dis)}** (route to A3)", "",
        "> 논문 §4.1/부록에 이 표와 codebook 요약을 수록한다. 목표 미달 시 protocol §4.3(재캘리브레이션).",
    ]
    text = "\n".join(lines)
    Path(a.out).write_text(text + "\n", encoding="utf-8")
    try:
        print(text)
    except UnicodeEncodeError:  # Windows cp949 console can't encode em-dash/Korean
        import sys
        sys.stdout.buffer.write((text + "\n").encode("utf-8"))

if __name__ == "__main__":
    main()
