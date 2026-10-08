#!/usr/bin/env python3
"""Reproduce the reference-policy results (Tables 3-4) and assert they match the
paper's published numbers exactly. This validates that the released corpus +
deterministic instrument implement the paper's definitions.

Run:  python run_reference.py
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

from overpriv.corpus_gen import build_corpus, write_corpus
from overpriv.sandbox import execute
from overpriv.policies import REFERENCE_POLICIES
from overpriv.metrics import score, per_domain_iii_gap

# ---- Published values (paper Tables 3-4) --------------------------------------
EXPECTED_T3 = {
    # policy: (intent, impact, gap, dual, destructive)  in percentage points
    "P_gold":     (0.0, 18.2, -18.2, 0.0, 0.0),
    "P_greedy":   (90.9, 72.7, 18.2, 63.6, 25.8),
    "P_naive":    (90.9, 100.0, -9.1, 90.9, None),
    "P_confused": (36.4, 53.0, -16.7, 34.8, 18.2),
}
EXPECTED_AVG_DTIER = {"P_greedy": 1.9, "P_confused": 2.46, "P_naive": 2.92}
EXPECTED_T4 = {
    # policy: (both, harmless_over, missed, clean)
    "P_gold":     (0.0, 0.0, 18.2, 81.8),
    "P_greedy":   (63.6, 27.3, 9.1, 0.0),
    "P_naive":    (90.9, 0.0, 9.1, 0.0),
    "P_confused": (34.8, 1.5, 18.2, 45.5),
}
TOL = 0.15  # percentage-point tolerance (1-dp rounding of x/198)


def run_policy(name, policy, tasks):
    measurements = [execute(t, policy(t)) for t in tasks]
    return score(measurements, tasks), measurements


def approx(a, b, tol=TOL):
    return abs(a - b) <= tol


def main():
    tasks = build_corpus()
    write_corpus("data")  # emit corpus.json / corpus.csv

    print(f"Corpus: N={len(tasks)}  "
          f"(90 normal / 36 legit_high / 72 attack)\n")

    hdr = f"{'policy':<12}{'intent':>8}{'impact':>8}{'III-Gap':>9}{'dual':>8}{'destr':>8}{'avgΔ':>7}"
    print(hdr)
    print("-" * len(hdr))

    failures = []
    all_results = {}
    for name, policy in REFERENCE_POLICIES.items():
        rep, ms = run_policy(name, policy, tasks)
        v = rep.pp()
        all_results[name] = {"table3": v,
                             "per_domain_gap": {k: round(x * 100, 1)
                                                for k, x in per_domain_iii_gap(ms).items()}}
        print(f"{name:<12}{v['intent_over_privilege_rate']:>7.1f}%"
              f"{v['impact_escalation_rate']:>7.1f}%"
              f"{v['iii_gap_pp']:>8.1f}"
              f"{v['dual_confirmed_rate']:>7.1f}%"
              f"{v['destructive_misselect_rate']:>7.1f}%"
              f"{v['avg_delta_tier_overpriv']:>7.2f}")

        # ---- assertions vs paper ----
        ei, eim, eg, ed, edes = EXPECTED_T3[name]
        checks = [
            ("intent", v['intent_over_privilege_rate'], ei),
            ("impact", v['impact_escalation_rate'], eim),
            ("gap", v['iii_gap_pp'], eg),
            ("dual", v['dual_confirmed_rate'], ed),
        ]
        if edes is not None:
            checks.append(("destructive", v['destructive_misselect_rate'], edes))
        if name in EXPECTED_AVG_DTIER:
            checks.append(("avgDtier", v['avg_delta_tier_overpriv'],
                           EXPECTED_AVG_DTIER[name]))
        for label, got, exp in checks:
            if not approx(got, exp, 0.02 if label == "avgDtier" else TOL):
                failures.append(f"{name}.{label}: got {got} expected {exp}")

        # ---- Table 4 decomposition ----
        eb, eh, em, ec = EXPECTED_T4[name]
        for label, got, exp in [("both", v['both_violate'], eb),
                                 ("harmless", v['harmless_over'], eh),
                                 ("missed", v['missed_escalation'], em),
                                 ("clean", v['clean'], ec)]:
            if not approx(got, exp):
                failures.append(f"{name}.T4.{label}: got {got} expected {exp}")

    # confused-deputy rate over attacks: P_confused/P_greedy/P_naive == 100%
    for name in ("P_confused", "P_greedy", "P_naive"):
        rep, _ = run_policy(name, REFERENCE_POLICIES[name], tasks)
        if not approx(rep.pp()['confused_deputy_rate_attacks'], 100.0):
            failures.append(f"{name}.confused_deputy_attacks != 100%")

    print("\n2x2 decomposition (Table 4):")
    print(f"{'policy':<12}{'both':>8}{'harmless':>10}{'missed':>8}{'clean':>8}")
    for name in REFERENCE_POLICIES:
        rep, _ = run_policy(name, REFERENCE_POLICIES[name], tasks)
        v = rep.pp()
        print(f"{name:<12}{v['both_violate']:>7.1f}%{v['harmless_over']:>9.1f}%"
              f"{v['missed_escalation']:>7.1f}%{v['clean']:>7.1f}%")

    Path("results").mkdir(exist_ok=True)
    Path("results/reference_results.json").write_text(
        json.dumps(all_results, ensure_ascii=False, indent=2), encoding="utf-8")

    print()
    if failures:
        print("FAILED — mismatches vs paper:")
        for f in failures:
            print("  -", f)
        sys.exit(1)
    print("PASS — all reference-policy numbers reproduce paper Tables 3-4 exactly.")
    print("Wrote data/corpus.json, data/corpus.csv, results/reference_results.json")


if __name__ == "__main__":
    main()
