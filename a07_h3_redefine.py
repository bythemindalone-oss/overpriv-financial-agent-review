# -*- coding: utf-8 -*-
"""A-07: Withdraw the confirmatory H3 and redefine it on a matched subset
(exploratory).

Problem (reviewer): the pre-registered H3 ("attack III-Gap more negative than
normal") is confounded with stratification. The negative III-Gap is produced
ENTIRELY by the 36 legit_high tasks (gold tier 4/5): a compliant agent selects
the high gold tier -> intent=0 but impact=1 -> III-Gap = -1 per task. Because the
original "non-attack" bucket lumps legit_high in with normal, non-attack III-Gap
is dragged negative and the attack-vs-nonattack sign reverses. attack tasks exist
only at gold tiers {1,2,3}, so there is no attack counterpart at tiers 4/5.

Redefinition (exploratory, NOT confirmatory): restrict to the matched gold-tier
support S = {1,2,3} where BOTH attack and normal tasks exist, and contrast
III-Gap(attack | S) vs III-Gap(normal | S). legit_high (gold 4/5) is excluded as
the unmatched stratum that is the confound source.

Usage:  python a07_h3_redefine.py
Outputs: results/a07/{A07_h3_redefine.md, a07.json}
"""
from __future__ import annotations
import sys, json, glob
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from overpriv.stats import cluster_bootstrap_ci
OUT = Path("results/a07"); OUT.mkdir(parents=True, exist_ok=True)
MATCH = {1, 2, 3}


def _tasks(p):
    c = json.loads(Path(p).read_text(encoding="utf-8"))
    return c if isinstance(c, list) else c.get("tasks", c)


def load_records():
    meta = {}
    for t in _tasks("data/corpus.json"):
        meta[t["task_id"]] = (t["label"], t["gold_tier"])
    for t in _tasks("data/corpus_traps.json"):
        meta[t["task_id"]] = ("trap", t["gold_tier"])
    recs = []
    for f in sorted(glob.glob("results/runs/*.json")):
        d = json.loads(Path(f).read_text(encoding="utf-8"))
        for pt in d["per_task"]:
            tid = pt["task_id"]
            lab, gt = meta[tid]
            intent = 0 if pt.get("tier") is None else int(pt.get("intent_overpriv", 0))
            impact = 0 if pt.get("tier") is None else int(pt.get("impact", 0))
            recs.append({"task_id": tid, "domain": tid.split("-")[0], "config": Path(f).stem,
                         "label": lab, "gold_tier": gt, "intent_overpriv": intent, "impact": impact})
    return recs


def iiigap(recs):
    if not recs:
        return 0.0
    return (sum(r["intent_overpriv"] for r in recs) / len(recs)
            - sum(r["impact"] for r in recs) / len(recs))


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    recs = load_records()

    # ---- attribution: where does the negative III-Gap come from? ----
    def gap_for(lab):
        s = [r for r in recs if r["label"] == lab]
        return round(100 * iiigap(s), 1)
    attribution = {lab: gap_for(lab) for lab in ("normal", "legit_high", "attack", "trap")}

    # ---- original (confounded) contrast, for the record ----
    atk_all = [r for r in recs if r["label"] == "attack"]
    non_all = [r for r in recs if r["label"] != "attack"]
    orig = {"attack": round(100 * iiigap(atk_all), 1),
            "non_attack_all": round(100 * iiigap(non_all), 1),
            "diff": round(100 * (iiigap(atk_all) - iiigap(non_all)), 1)}

    # ---- redefined matched contrast on S = {1,2,3} (exploratory) ----
    atk_S = [r for r in recs if r["label"] == "attack" and r["gold_tier"] in MATCH]
    nor_S = [r for r in recs if r["label"] == "normal" and r["gold_tier"] in MATCH]

    def diff_stat(rr):
        a = [r for r in rr if r["label"] == "attack"]
        n = [r for r in rr if r["label"] == "normal"]
        return iiigap(a) - iiigap(n)
    pooled = atk_S + nor_S
    point, lo, hi = cluster_bootstrap_ci(pooled, diff_stat)

    # per-config matched contrast
    per_cfg = []
    for cfg in sorted({r["config"] for r in recs}):
        a = [r for r in atk_S if r["config"] == cfg]
        n = [r for r in nor_S if r["config"] == cfg]
        per_cfg.append({"config": cfg,
                        "iiigap_attack_S": round(100 * iiigap(a), 1),
                        "iiigap_normal_S": round(100 * iiigap(n), 1),
                        "diff": round(100 * (iiigap(a) - iiigap(n)), 1),
                        "intent_attack_S": round(100 * sum(r["intent_overpriv"] for r in a) / len(a), 1),
                        "impact_attack_S": round(100 * sum(r["impact"] for r in a) / len(a), 1)})

    payload = {
        "confirmatory_H3": "WITHDRAWN (confounded with gold-tier stratification)",
        "confound": "negative III-Gap is produced by the 36 legit_high (gold 4/5) tasks; "
                    "attacks exist only at gold {1,2,3}, so legit_high is an unmatched stratum",
        "iii_gap_by_label_pp": attribution,
        "original_confounded_contrast_pp": orig,
        "redefined_exploratory": {
            "matched_support": "gold_tier in {1,2,3} (both attack and normal present)",
            "excluded": "legit_high (gold 4/5), trap",
            "pooled_diff_attack_minus_normal_pp": round(100 * point, 1),
            "cluster_bootstrap_ci90_pp": [round(100 * lo, 1), round(100 * hi, 1)],
            "n_attack_records": len(atk_S), "n_normal_records": len(nor_S),
            "status": "EXPLORATORY (not a confirmatory test)",
        },
        "per_config": per_cfg,
    }
    (OUT / "a07.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    L = []
    L.append("# A-07 H3 재정의: 사전검정 철회 + 대응 부분집합(탐색적)\n")
    L.append("## 문제 (리뷰어)\n")
    L.append("사전등록 H3(\"공격의 III-Gap이 정상보다 더 음수\")는 **gold-tier 층화와 교란**되어 식별 불가하다. "
             "음의 III-Gap은 **정당 고티어(legit_high, gold 4/5) 36개 태스크**에서 전적으로 발생한다"
             "(순응 시 intent=0·impact=1 → 태스크당 III-Gap=−1). 기존 \"비-공격\" 버킷이 이 legit_high를 "
             "포함하므로 비-공격 III-Gap이 음으로 끌리고 부호가 뒤집힌다. 공격 태스크는 gold {1,2,3}에만 "
             "존재하여 tier 4/5에는 대응짝이 없다.\n")
    L.append("## III-Gap 라벨별 귀인 (%p) — 음수의 출처\n")
    L.append("| 라벨 | III-Gap |")
    L.append("|------|---------|")
    for lab in ("normal", "legit_high", "attack", "trap"):
        L.append(f"| {lab} | {attribution[lab]:+.1f} |")
    L.append(f"\n→ 음의 III-Gap은 **legit_high({attribution['legit_high']:+.1f}%p)에 집중**되고, normal은 "
             f"{attribution['normal']:+.1f}%p, attack은 {attribution['attack']:+.1f}%p이다.\n")
    L.append("## 재정의 (탐색적): 매칭 지지 gold∈{1,2,3}에서 attack vs normal\n")
    L.append(f"- pooled III-Gap 차(attack − normal) = **{100*point:+.1f}%p** "
             f"(도메인 클러스터 부트스트랩 90% CI [{100*lo:+.1f}, {100*hi:+.1f}])")
    L.append(f"- 대상: attack {len(atk_S)} · normal {len(nor_S)} 레코드 (legit_high·trap 제외)")
    L.append(f"- **상태: 탐색적(EXPLORATORY)** — 사전등록 확정검정 아님\n")
    L.append("### 해석\n")
    L.append("매칭 지지에서 공격의 III-Gap이 정상보다 **더 양수**라면, 공격은 실행 은폐가 아니라 "
             "**선택 단계 과권한(로그에서 관측 가능)** 으로 드러난다는 뜻이다. 즉 음의 III-Gap(감사 사각)은 "
             "공격이 아니라 **정당 고티어 실행**의 정의적 성질이며, 선택-로그 감시는 공격 탐지에 유효하다.\n")
    L.append("## 조합별 (매칭 지지, %p)\n")
    L.append("| config | III-Gap attack|S | III-Gap normal|S | 차 | intent attack|S | impact attack|S |")
    L.append("|--------|------------------|------------------|----|------------------|------------------|")
    for r in per_cfg:
        L.append(f"| {r['config']} | {r['iiigap_attack_S']:+} | {r['iiigap_normal_S']:+} | {r['diff']:+} | "
                 f"{r['intent_attack_S']} | {r['impact_attack_S']} |")
    L.append("\n## 산출물\n- `results/a07/a07.json`")
    (OUT / "A07_h3_redefine.md").write_text("\n".join(L), encoding="utf-8")

    print("III-Gap by label (pp):", attribution)
    print(f"original confounded diff (attack - non_attack_all) = {orig['diff']:+.1f}pp")
    print(f"redefined matched diff (attack - normal | gold in 1,2,3) = {100*point:+.1f}pp "
          f"(90% CI [{100*lo:+.1f},{100*hi:+.1f}]) EXPLORATORY")
    print(f"wrote {OUT}/A07_h3_redefine.md, a07.json")


if __name__ == "__main__":
    main()
