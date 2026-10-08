# -*- coding: utf-8 -*-
"""Machine verification that the released gold labels conform to the externally
anchored codebook rules (labeling/codebook.md v2). This provides the *validity*
(objectivity) evidence for §4.1: the gold is not free author judgment but a
rule-governed assignment, mechanically reproducible with zero rule violations.

Checked rules (mechanically decidable):
  R1  gold_tool's declared tier == gold_tier          (self-consistency)
  R2  legit_high  =>  gold_tier in {T4, T5}           (approved high-tier)
  R3  normal      =>  gold_tier <= role_cap            (within authority)
  R4  attack      =>  attack_implied_tier > role_cap   (genuinely over-cap)
  R5  every gold_tier in {1..5}; label in {normal, legit_high, attack}

NOTE: rule-conformance shows the tier assignment is consistent with the codebook
given the capability reading of each request; the request->capability reading
itself is validated by an independent single-expert audit (labeling/audit_*.csv).

Run:  python labeling/verify_gold_rules.py
Exit code 0 and "PASS" iff zero violations.
"""
from __future__ import annotations
import sys
from collections import Counter

sys.path.insert(0, ".")
from overpriv.corpus_gen import build_corpus


def main() -> int:
    tasks = build_corpus()
    viol = []
    lab_c = Counter()
    for t in tasks:
        tid, lab = t["task_id"], t["label"]
        cap, g = t.get("role_cap"), t.get("gold_tier")
        gtool = t.get("gold_tool")
        menu = {m["name"]: m["tier"] for m in t.get("candidate_menu", [])}
        lab_c[lab] += 1
        if lab not in ("normal", "legit_high", "attack"):
            viol.append((tid, f"R5 unknown label {lab}"))
        if g not in (1, 2, 3, 4, 5):
            viol.append((tid, f"R5 gold_tier {g} out of range"))
        if gtool in menu and menu[gtool] != g:
            viol.append((tid, f"R1 gold_tool tier {menu[gtool]} != gold_tier {g}"))
        if lab == "legit_high" and g not in (4, 5):
            viol.append((tid, f"R2 legit_high gold_tier {g} not in T4/T5"))
        if lab == "normal" and cap is not None and g is not None and g > cap:
            viol.append((tid, f"R3 normal gold_tier {g} > role_cap {cap}"))
        if lab == "attack":
            ai = t.get("attack_implied_tier")
            if ai is not None and cap is not None and ai <= cap:
                viol.append((tid, f"R4 attack implied {ai} <= role_cap {cap}"))

    print(f"tasks={len(tasks)}  labels={dict(lab_c)}")
    print(f"rule violations: {len(viol)}")
    for tid, msg in viol[:20]:
        print(f"  {tid}: {msg}")
    ok = not viol
    print("PASS — gold conforms to codebook rules (0 violations)" if ok
          else "FAIL — gold violates codebook rules")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
