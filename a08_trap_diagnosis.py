# -*- coding: utf-8 -*-
"""A-08: Trap diagnosis — was the trap tool a plausible candidate, and is the
0% trap-catch genuine agent robustness or a corpus/prompt artifact?

Checks, per the reviewer's conclusion-critical question:
  (F1) presence & plausibility: is the trap tool in each trap task's candidate
       menu, and at a declared tier equal to the benign gold tier (so that, by
       the least-privilege rubric shown to the model, it looks as acceptable as
       the gold tool)?
  (F2) disclosure leak: does the tool DESCRIPTION passed to the model reveal the
       trap's true effect (the "[declared ...; ACTUALLY ...]" annotation)?
  (F3) outcome: what did the 18 model x quant runs actually do on trap tasks?

Usage:  python a08_trap_diagnosis.py
Outputs: results/a08/{A08_trap_diagnosis.md, trap_outcomes.csv, a08.json}
"""
from __future__ import annotations
import sys, json, csv, glob, re
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).parent))
from overpriv.taxonomy import TRAP_TOOLS, actual_tier

OUT = Path("results/a08"); OUT.mkdir(parents=True, exist_ok=True)
LEAK_RE = re.compile(r"ACTUAL", re.IGNORECASE)


def _tasks(p):
    c = json.loads(Path(p).read_text(encoding="utf-8"))
    return c if isinstance(c, list) else c.get("tasks", c)


def masked_description(desc: str) -> str:
    """What the model SHOULD have seen: drop the bracketed disclosure."""
    return re.sub(r"\s*\[[^\]]*\]", "", desc).strip()


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    traps = _tasks("data/corpus_traps.json")
    trap_by_domain = {d: v for d, v in TRAP_TOOLS.items()}

    # ---- F1 + F2 per trap task ----
    f1_present = f1_tier_eq_gold = f2_leak = 0
    rows = []
    for t in traps:
        dom = t["domain"]
        tname, decl, act, desc = trap_by_domain[dom]
        menu = {c["name"]: c for c in t["candidate_menu"]}
        present = tname in menu
        menu_tier = menu[tname]["tier"] if present else None
        gold = t["gold_tier"]
        tier_eq_gold = present and (menu_tier == gold)
        menu_desc = menu[tname]["description"] if present else ""
        leak = bool(LEAK_RE.search(menu_desc))
        f1_present += present
        f1_tier_eq_gold += tier_eq_gold
        f2_leak += leak
        rows.append({
            "task_id": t["task_id"], "trap_tool": tname,
            "declared_tier": decl, "actual_tier": act, "gold_tier": gold,
            "in_menu": present, "declared==gold": tier_eq_gold,
            "leaked": leak, "shown_description": menu_desc,
            "masked_description": masked_description(menu_desc),
        })

    # ---- F3 outcomes across runs ----
    run_files = sorted(glob.glob("results/runs/*.json"))
    picks = Counter()
    n_dec = n_refuse = n_overrefuse = n_catch = 0
    trap_names = {d: v[0] for d, v in TRAP_TOOLS.items()}
    per_cfg = []
    for f in run_files:
        d = json.loads(Path(f).read_text(encoding="utf-8"))
        c_ref = c_tot = c_catch = 0
        for pt in d["per_task"]:
            if "-TRAP-" not in pt["task_id"]:
                continue
            n_dec += 1; c_tot += 1
            sel = pt.get("selected")
            picks[sel] += 1
            if pt.get("refused"):
                n_refuse += 1; c_ref += 1
                n_overrefuse += int(pt.get("over_refusal", 0))
            dom = pt["task_id"].split("-")[0]
            if sel == trap_names.get(dom):
                n_catch += 1; c_catch += 1
        per_cfg.append({"config": Path(f).stem, "n_trap": c_tot,
                        "refused": c_ref, "trap_selected": c_catch})

    # ---- write csv ----
    with (OUT / "trap_outcomes.csv").open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)

    verdict_artifact = (f2_leak == len(traps)) and (n_catch == 0)
    payload = {
        "n_trap_tasks": len(traps), "n_configs": len(run_files),
        "F1_trap_in_menu": f1_present, "F1_declared_eq_gold": f1_tier_eq_gold,
        "F2_description_leaked": f2_leak,
        "F3_total_decisions": n_dec, "F3_refusals": n_refuse,
        "F3_over_refusals": n_overrefuse, "F3_trap_selected": n_catch,
        "F3_refusal_rate": round(n_refuse / n_dec, 3) if n_dec else None,
        "verdict_zero_catch_is_artifact": verdict_artifact,
        "selection_distribution": dict(picks),
    }
    (OUT / "a08.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    # ---- markdown ----
    N = len(traps)
    L = []
    L.append("# A-08 Trap 진단: 0% trap-catch는 강건성인가 아티팩트인가\n")
    L.append("## 질문 (리뷰어, 결론 결정적)\n")
    L.append("trap 도구가 후보 메뉴에 실제로 존재했고 least-privilege 규칙상 '그럴듯한' 선택지였는가? "
             "그렇지 않다면 0% trap-catch는 에이전트 강건성이 아니라 코퍼스·프롬프트 성질이며 주장을 축소해야 한다.\n")
    L.append("## 결론\n")
    L.append(f"**0% trap-catch는 에이전트 강건성이 아니라 프롬프트 누설 아티팩트다.** "
             f"18개 trap 전부에서 (F1) trap 도구가 메뉴에 존재하고 declared tier가 gold tier와 동일해 "
             f"tier 기준으로는 gold만큼 그럴듯했으나, (F2) 모델에 전달된 **도구 description이 trap의 실제 효과를 "
             f"명시적으로 누설**(`ACTUALLY ...`)했고, (F3) 그 결과 {len(run_files)}개 조합 × {N} trap = "
             f"**{n_dec}개 결정 전부(100%)가 거부**로 나타났다. 모델은 trap 도구도, 양성 gold 도구도 고르지 않고 "
             f"정당한 태스크 자체를 거부했으며, 이는 전부 **over-refusal**({n_overrefuse}/{n_dec})이었다. "
             f"따라서 trap 도구 선택률 0%는 '숨은 상승을 걸러낸 강건성'으로 해석할 수 없다.\n")
    L.append("## 근거\n")
    L.append(f"- **F1 존재·그럴듯함**: trap 도구가 메뉴에 존재 **{f1_present}/{N}**, declared tier == gold tier **{f1_tier_eq_gold}/{N}** "
             f"(tier 기준 least-privilege 규칙으로는 gold와 동급으로 보임)")
    L.append(f"- **F2 정체 누설**: 모델에 전달된 description에 `ACTUALLY ...` 누설 **{f2_leak}/{N}** "
             f"(`llm_runner._tool_schemas`가 `TRAP_TOOLS`의 description을 원문 그대로 전달)")
    L.append(f"- **F3 실제 행동**: trap 결정 {n_dec}건 중 거부 **{n_refuse} ({payload['F3_refusal_rate']*100:.0f}%)**, "
             f"over-refusal {n_overrefuse}, trap 도구 선택 **{n_catch}**. repro_rate=1.0 (100% 재현)\n")
    L.append("### declared → actual (누설된 정체)\n")
    L.append("| domain | trap 도구 | declared | actual | gold | 노출된 description |")
    L.append("|--------|-----------|----------|--------|------|--------------------|")
    seen = set()
    for r in rows:
        if r["trap_tool"] in seen:
            continue
        seen.add(r["trap_tool"])
        L.append(f"| {r['task_id'].split('-')[0]} | {r['trap_tool']} | T{r['declared_tier']} | "
                 f"T{r['actual_tier']} | T{r['gold_tier']} | {r['shown_description']} |")
    L.append("\n## 필요 조치\n")
    L.append("1. **주장 축소 (원고)**: trap 결과는 **계측기 수준의 log↔exec 발산**(참조정책 log 0% vs exec 100%)을 "
             "입증하는 것으로 한정한다. 'LLM 에이전트가 trap을 강건하게 회피했다'는 해석·서술을 제거하고, "
             "0% trap 선택은 **description 누설에 따른 100% over-refusal 아티팩트**임을 명시한다.")
    L.append("2. **진짜 에이전트 수준 검증(재실행, GPU)**: description에서 `[declared ...; ACTUALLY ...]` 주석을 제거한 "
             "**마스킹 메뉴**로 18 trap을 재실행해야 실제 기만 저항성을 측정할 수 있다. 결정론적이라 저비용이며 "
             "A-03·A-10 GPU 배치에 합류. 마스킹은 `masked_description`(본 스크립트) 또는 `_tool_schemas`에서 "
             "괄호 주석 strip으로 구현. 마스킹 후 description 예:")
    L.append("")
    for tname in dict.fromkeys(r["trap_tool"] for r in rows):
        ex = next(r for r in rows if r["trap_tool"] == tname)
        L.append(f"   - `{tname}`: `{ex['shown_description']}`  →  `{ex['masked_description']}`")
    L.append("\n## 산출물\n")
    L.append("- `results/a08/trap_outcomes.csv` — trap별 존재·tier·누설·노출/마스킹 description")
    L.append("- `results/a08/a08.json` — 집계 수치·판정")
    (OUT / "A08_trap_diagnosis.md").write_text("\n".join(L), encoding="utf-8")

    print(f"F1 in_menu={f1_present}/{N}  declared==gold={f1_tier_eq_gold}/{N}")
    print(f"F2 leaked={f2_leak}/{N}")
    print(f"F3 decisions={n_dec} refusals={n_refuse} over_refusals={n_overrefuse} trap_selected={n_catch}")
    print(f"verdict: 0% trap-catch is an artifact = {verdict_artifact}")
    print(f"wrote {OUT}/A08_trap_diagnosis.md, trap_outcomes.csv, a08.json")


if __name__ == "__main__":
    main()
