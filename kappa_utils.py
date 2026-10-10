# -*- coding: utf-8 -*-
"""Weighted-kappa helpers used by the labeler-sensitivity re-scoring.
Extracted verbatim from the survey aggregation script of the original package; it contains no
participant data, only the kappa computation and the Landis-Koch band labels."""

def linear_weighted_kappa(a, b, kmin=1, kmax=5):
    """a,b: 동일 순서의 정수 라벨 리스트(1~5). 반환: (kappa, raw_agreement, n)."""
    pairs = [(x, y) for x, y in zip(a, b) if x is not None and y is not None]
    n = len(pairs)
    if n == 0:
        return None, None, 0
    cats = list(range(kmin, kmax + 1)); K = len(cats)
    idx = {c: i for i, c in enumerate(cats)}
    O = [[0] * K for _ in range(K)]
    ca = [0] * K; cb = [0] * K
    for x, y in pairs:
        O[idx[x]][idx[y]] += 1; ca[idx[x]] += 1; cb[idx[y]] += 1
    denom = (K - 1) if K > 1 else 1
    def w(i, j): return abs(cats[i] - cats[j]) / denom   # linear weights
    num = den = 0.0
    for i in range(K):
        for j in range(K):
            e = ca[i] * cb[j] / n
            num += w(i, j) * O[i][j]
            den += w(i, j) * e
    kappa = 1 - num / den if den > 0 else 1.0
    raw = sum(O[i][i] for i in range(K)) / n
    return kappa, raw, n


def landis_koch(k):
    if k is None: return "n/a"
    if k < 0:    return "poor(<0)"
    if k < .20:  return "slight(0.00–0.20)"
    if k < .40:  return "fair(0.21–0.40)"
    if k < .60:  return "moderate(0.41–0.60)"
    if k < .80:  return "substantial(0.61–0.80)"
    return "almost perfect(0.81–1.00)"

# ---------- 파일 파싱 ----------

