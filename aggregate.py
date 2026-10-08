#!/usr/bin/env python3
"""Aggregate the 15 per-config run files into a tidy table and run the
pre-registered analyses (H1 size, H2 size x quant interaction, H3 attack gap).

Run after all runs exist in results/runs/*.json:
    python aggregate.py
"""
from __future__ import annotations
import json
from pathlib import Path

from overpriv.corpus_gen import build_corpus
from overpriv.stats import (
    mcnemar_exact, cluster_bootstrap_ci, rate, iii_gap_stat,
    interaction_did_bootstrap, holm_bonferroni, benjamini_hochberg, mcnemar_min_n,
)

# model id -> (size bucket, param label) for H1/H2 grouping
SIZE_BUCKET = {
    "meta-llama/Llama-3.1-8B-Instruct": ("small", "8B"),
    "Qwen/Qwen2.5-7B-Instruct": ("small", "7B"),
    "Qwen/Qwen2.5-32B-Instruct": ("large", "32B"),
    "meta-llama/Llama-3.1-70B-Instruct": ("large", "70B"),
    "Qwen/Qwen2.5-72B-Instruct": ("large", "72B"),
}
LABEL_BY_TASK = {t["task_id"]: t["label"] for t in build_corpus()}


def load_runs(runs_dir="results/runs"):
    recs = []       # tidy per-(config,task) records
    summaries = []
    for f in sorted(Path(runs_dir).glob("*.json")):
        r = json.loads(f.read_text(encoding="utf-8"))
        mid = r["model"]
        # quantized checkpoints carry suffixes (-AWQ, -GPTQ-Int4/8); map to base id
        base = mid.split("-AWQ")[0].split("-GPTQ")[0]
        size, plabel = (SIZE_BUCKET.get(mid) or SIZE_BUCKET.get(base)
                        or ("unknown", mid))
        summaries.append({"model": r["model"], "size": size, "param": plabel,
                          "quant": r["quant"], **r["metrics"]})
        for pt in r["per_task"]:
            if pt.get("tier") is None:
                intent = impact = 0
            else:
                intent, impact = pt["intent_overpriv"], pt["impact"]
            recs.append({
                "task_id": pt["task_id"],
                "domain": pt["task_id"].split("-")[0],
                "model": r["model"], "size": size, "param": plabel,
                "quant": r["quant"],
                "label": LABEL_BY_TASK.get(pt["task_id"], "?"),
                "intent_overpriv": intent, "impact": impact,
            })
    return recs, summaries


def paired(recs, sizeA, quantA, sizeB, quantB, field):
    """Align two configs on shared task_ids for a paired contrast."""
    A = {r["task_id"]: r[field] for r in recs if r["size"] == sizeA and r["quant"] == quantA}
    B = {r["task_id"]: r[field] for r in recs if r["size"] == sizeB and r["quant"] == quantB}
    keys = sorted(set(A) & set(B))
    return [A[k] for k in keys], [B[k] for k in keys]


def main():
    recs, summaries = load_runs()
    if not summaries:
        print("No run files in results/runs/. Run overpriv.llm_runner first.")
        print(f"(Planning) paired-McNemar min N for 10pp effect: {mcnemar_min_n(0.10,0.34)}")
        return

    print("=== Per-config summary (15 combinations) ===")
    for s in summaries:
        print(f"{s['param']:>5} {s['quant']:>5}  intent={s['intent_over_privilege_rate']:5.1f}%  "
              f"impact={s['impact_escalation_rate']:5.1f}%  gap={s['iii_gap_pp']:+5.1f}pp  "
              f"dual={s['dual_confirmed_rate']:5.1f}%")

    pvals = {}
    # H1: size effect (small vs large, fp16), over-priv
    a, b = paired(recs, "small", "fp16", "large", "fp16", "intent_overpriv")
    if a and b:
        mn = mcnemar_exact(a, b)
        pvals["H1_size"] = mn.p_value
        print(f"\nH1 size (small-large, fp16): RD={mn.rate_diff:+.3f} h={mn.cohens_h:+.3f} p={mn.p_value:.3g}")

    # H2: size x quant interaction (int4 vs fp16), impact
    inter = [r for r in recs if r["size"] in ("small", "large") and r["quant"] in ("fp16", "int4")]
    if inter:
        did, lo, hi = interaction_did_bootstrap(inter, "impact")
        print(f"H2 interaction DiD: {did:+.3f} [{lo:+.3f},{hi:+.3f}] "
              f"-> {'supported' if lo > 0 else 'CI includes 0'}")
        pvals["H2_interaction"] = 0.0 if lo > 0 else 1.0  # CI-based; p from GLMM if available

    # H3: attack gap more negative than normal
    atk = [r for r in recs if r["label"] == "attack"]
    nor = [r for r in recs if r["label"] != "attack"]
    if atk and nor:
        _, alo, ahi = cluster_bootstrap_ci(atk, iii_gap_stat)
        gap_atk = iii_gap_stat(atk)
        gap_nor = iii_gap_stat(nor)
        print(f"H3 III-Gap attack={gap_atk:+.3f} normal={gap_nor:+.3f}  (attack CI [{alo:+.3f},{ahi:+.3f}])")

    if pvals:
        print("\nMultiplicity control:")
        print("  Holm:", {k: v["reject"] for k, v in holm_bonferroni(pvals).items()})
        print("  BH:  ", {k: v["reject"] for k, v in benjamini_hochberg(pvals).items()})

    Path("results/aggregate.json").write_text(
        json.dumps({"summaries": summaries, "n_records": len(recs)},
                   ensure_ascii=False, indent=2), encoding="utf-8")
    print("\nwrote results/aggregate.json")


if __name__ == "__main__":
    main()
