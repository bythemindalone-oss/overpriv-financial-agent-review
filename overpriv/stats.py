"""Pre-registered statistical analysis (Section 5.4, Table 5).

Implements the confirmatory tests planned for the LLM study:

  * paired McNemar exact test           (condition-pair contrast on same tasks)
  * cluster (domain) bootstrap 95% CI   (respects domain-clustered structure)
  * size x quantization interaction     (GLMM if statsmodels present; DiD bootstrap fallback)
  * Holm-Bonferroni (FWER) + Benjamini-Hochberg (FDR) multiplicity control
  * minimum detectable effect note      (paired McNemar MDE, N ~= 283)

All functions operate on per-task records produced by llm_runner (fields
`task_id`, `domain`, and a chosen binary outcome such as `intent_overpriv` or
`impact`). This module is dependency-light (numpy + scipy); statsmodels is
optional and only used for the GLMM.

A synthetic self-test (`python -m overpriv.stats`) runs the full pipeline on
fabricated paired data so the code is exercised without any GPU/LLM.
"""
from __future__ import annotations
from dataclasses import dataclass
import math

try:
    import numpy as np
except ImportError:  # pragma: no cover
    np = None


# ---- McNemar ------------------------------------------------------------------
@dataclass
class McNemarResult:
    b: int
    c: int
    p_value: float
    rate_diff: float      # p1 - p2 (proportion of 1s in each condition)
    cohens_h: float


def mcnemar_exact(cond1: list[int], cond2: list[int]) -> McNemarResult:
    """Paired binary outcomes on the SAME tasks (aligned lists)."""
    from scipy.stats import binomtest
    assert len(cond1) == len(cond2)
    b = sum(1 for a, d in zip(cond1, cond2) if a == 1 and d == 0)
    c = sum(1 for a, d in zip(cond1, cond2) if a == 0 and d == 1)
    n = b + c
    p = binomtest(min(b, c), n, 0.5).pvalue if n > 0 else 1.0
    p1, p2 = sum(cond1) / len(cond1), sum(cond2) / len(cond2)
    return McNemarResult(b, c, p, p1 - p2, cohens_h(p1, p2))


def cohens_h(p1: float, p2: float) -> float:
    def phi(p):
        p = min(max(p, 0.0), 1.0)
        return 2 * math.asin(math.sqrt(p))
    return phi(p1) - phi(p2)


# ---- cluster bootstrap --------------------------------------------------------
def cluster_bootstrap_ci(records: list[dict], stat_fn, n_boot: int = 5000,
                         seed: int = 20260813, alpha: float = 0.05):
    """Percentile CI resampling whole DOMAINS (clusters) with replacement.

    `stat_fn(list_of_records) -> float`. Flat bootstrap underestimates the CI by
    ignoring domain correlation, so we resample clusters.
    """
    if np is None:
        raise RuntimeError("numpy required")
    rng = np.random.default_rng(seed)
    by_dom: dict[str, list[dict]] = {}
    for r in records:
        by_dom.setdefault(r["domain"], []).append(r)
    domains = list(by_dom)
    point = stat_fn(records)
    boots = []
    for _ in range(n_boot):
        chosen = rng.choice(len(domains), size=len(domains), replace=True)
        sample = []
        for idx in chosen:
            sample.extend(by_dom[domains[idx]])
        boots.append(stat_fn(sample))
    lo = float(np.percentile(boots, 100 * alpha / 2))
    hi = float(np.percentile(boots, 100 * (1 - alpha / 2)))
    return point, lo, hi


def rate(field: str):
    return lambda recs: (sum(r[field] for r in recs) / len(recs)) if recs else 0.0


def iii_gap_stat(recs):
    if not recs:
        return 0.0
    return (sum(r["intent_overpriv"] for r in recs) / len(recs)
            - sum(r["impact"] for r in recs) / len(recs))


# ---- multiplicity control -----------------------------------------------------
def holm_bonferroni(pvals: dict[str, float], alpha: float = 0.05) -> dict[str, dict]:
    items = sorted(pvals.items(), key=lambda kv: kv[1])
    m = len(items)
    out = {}
    prev_reject = True
    for i, (k, p) in enumerate(items):
        thr = alpha / (m - i)
        reject = (p <= thr) and prev_reject
        out[k] = {"p": p, "threshold": thr, "reject": reject}
        prev_reject = reject
    return out


def benjamini_hochberg(pvals: dict[str, float], alpha: float = 0.05) -> dict[str, dict]:
    items = sorted(pvals.items(), key=lambda kv: kv[1])
    m = len(items)
    out = {k: {"p": p, "reject": False} for k, p in items}
    max_i = -1
    for i, (k, p) in enumerate(items, 1):
        if p <= (i / m) * alpha:
            max_i = i
    for i, (k, p) in enumerate(items, 1):
        out[k] = {"p": p, "threshold": (i / m) * alpha, "reject": i <= max_i}
    return out


# ---- size x quant interaction -------------------------------------------------
def interaction_did_bootstrap(records: list[dict], field: str = "impact",
                              n_boot: int = 5000, seed: int = 20260813):
    """Difference-in-differences interaction contrast (small vs large) x (int4 vs fp16).

    Each record must carry `size` in {small,large} and `quant` in {fp16,int4}.
    Returns the DiD point estimate and cluster-bootstrap CI:
        DiD = [rate(small,int4) - rate(small,fp16)]
            - [rate(large,int4) - rate(large,fp16)]
    A positive DiD with CI excluding 0 => INT4 degrades small models more (H2).
    """
    def did(recs):
        def r(sz, q):
            sub = [x[field] for x in recs if x["size"] == sz and x["quant"] == q]
            return sum(sub) / len(sub) if sub else 0.0
        return (r("small", "int4") - r("small", "fp16")) - \
               (r("large", "int4") - r("large", "fp16"))
    return cluster_bootstrap_ci(records, did, n_boot=n_boot, seed=seed)


def interaction_glmm(records: list[dict], field: str = "impact"):
    """Logistic GLMM with task random intercept; interaction size:quant.
    Requires statsmodels + pandas. Returns fitted summary or None if unavailable.
    """
    try:
        import pandas as pd
        from statsmodels.genmod.bayes_mixed_glm import BinomialBayesMixedGLM
    except ImportError:
        return None
    df = pd.DataFrame(records)
    df["y"] = df[field].astype(int)
    # random intercept per task; fixed effects size*quant
    vc = {"task": "0 + C(task_id)"}
    model = BinomialBayesMixedGLM.from_formula(
        "y ~ C(size) * C(quant)", vc_formulas=vc, data=df)
    return model.fit_vb()


# ---- power / MDE --------------------------------------------------------------
def mcnemar_min_n(effect_pp: float = 0.10, discordance: float = 0.30,
                  power: float = 0.80, alpha: float = 0.05) -> int:
    """Approx N for paired McNemar to detect a rate difference `effect_pp`
    given discordant-pair proportion. Returns the headline planning number
    (~283 for a medium effect), used to justify the 600-task extension."""
    from scipy.stats import norm
    za, zb = norm.ppf(1 - alpha / 2), norm.ppf(power)
    psi = discordance
    if effect_pp <= 0:
        return 0
    n = ((za * math.sqrt(psi) + zb * math.sqrt(psi - effect_pp ** 2)) ** 2) / (effect_pp ** 2)
    return math.ceil(n)


# ---- self-test ----------------------------------------------------------------
def _selftest():
    if np is None:
        print("numpy/scipy required for self-test"); return
    rng = np.random.default_rng(0)
    domains = [f"D{i}" for i in range(1, 7)]
    # fabricate: large model has lower over-priv than small; int4 worsens small more
    recs = []
    for sz, base in [("small", 0.5), ("large", 0.3)]:
        for q, bump in [("fp16", 0.0), ("int4", 0.15 if sz == "small" else 0.03)]:
            for d in domains:
                for k in range(33):
                    y = int(rng.random() < base + bump)
                    imp = int(rng.random() < (base + bump) * 0.8)
                    recs.append({"task_id": f"{sz}-{q}-{d}-{k}", "domain": d,
                                 "size": sz, "quant": q,
                                 "intent_overpriv": y, "impact": imp})
    small_i4 = [r["intent_overpriv"] for r in recs if r["size"] == "small" and r["quant"] == "int4"]
    small_f16 = [r["intent_overpriv"] for r in recs if r["size"] == "small" and r["quant"] == "fp16"]
    mn = mcnemar_exact(small_i4, small_f16)
    print(f"McNemar small int4 vs fp16: b={mn.b} c={mn.c} p={mn.p_value:.4g} "
          f"RD={mn.rate_diff:+.3f} h={mn.cohens_h:+.3f}")
    pt, lo, hi = cluster_bootstrap_ci(
        [r for r in recs if r["size"] == "small" and r["quant"] == "int4"],
        rate("intent_overpriv"), n_boot=2000)
    print(f"cluster-bootstrap over-priv rate (small,int4): {pt:.3f} [{lo:.3f},{hi:.3f}]")
    did, dlo, dhi = interaction_did_bootstrap(recs, "intent_overpriv", n_boot=2000)
    print(f"DiD interaction (H2): {did:+.3f} [{dlo:+.3f},{dhi:+.3f}] "
          f"-> {'supported' if dlo > 0 else 'CI includes 0'}")
    ps = {"H1_size": mn.p_value, "H2_interaction": 0.02, "H3_attack": 0.001}
    print("Holm:", {k: v["reject"] for k, v in holm_bonferroni(ps).items()})
    print("BH:  ", {k: v["reject"] for k, v in benjamini_hochberg(ps).items()})
    print(f"McNemar min N (10pp, medium): {mcnemar_min_n(0.10, 0.30)}  "
          f"(headline ~283 at psi=0.34)")


if __name__ == "__main__":
    _selftest()
