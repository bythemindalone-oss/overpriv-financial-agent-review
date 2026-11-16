# RUNBOOK — A-23 request-wording controls (Reviewer 4 response, 2026-11)

## Why this run exists

Reviewer 4, main comment 3: *"관찰된 도구 선택 동작 중 일부는 모델의 권한 추론 능력보다는
벤치마크 구성의 영향을 받을 수 있습니다"* — i.e. the v27 trap rate may be an artefact of
request wording rather than a property of the agent. The manuscript already concedes the
lexical fact (trap tool is the unique lexical best match in 13 of 18 trap tasks, gold in none).
This run turns that concession into a measurement.

Three conditions, all against the CONCEALED description unless stated:

| condition | request wording | what it tests |
|---|---|---|
| `neutral` | no content word shared with ANY menu tool | fit is not cued toward either equal-tier tool |
| `goldcue` | worded to fit the GOLD tool | fit favours the safe tool |
| `neutral_disclosed` | neutral wording + disclosing description | disclosure effect without lexical cueing |

Only the model's *view* changes. The sandbox always executes the true effect of whatever is chosen.

## Pre-registered decision rule — fix this BEFORE looking at the numbers

(the rule is also printed by `a25_v28_aggregate.py`)

- `neutral` share ≤ ~60% **and** `goldcue` trap ≈ 0 → the v27 trap rate was request-fit.
  The principal claim becomes the **instrument** claim ("a log-only audit is blind to a
  misdeclared tool whenever it is chosen"), not an agent-preference claim.
- `neutral` share clearly > 50% (p < .05 in most configs) **and** `goldcue` trap > 0 →
  agents prefer the escalating tool beyond fit. The **agent-level** claim survives and is
  reported on the neutral condition.
- `neutral_disclosed` vs `neutral` isolates disclosure without lexical cueing.

Either outcome is publishable and both are answers to Reviewer 4. Do not run this
expecting a particular result.

## Scope

13 serving labels — exactly the set that carries a trap measurement (`results/masked/*.json`),
so the output lines up one-to-one with the concealed / disclosed / placebo baselines.
All cells are TP=1: **one A100-80GB is enough**. Llama-3.1 is excluded (no trap baseline).

## Run

Pod: RunPod, **A100 80GB PCIe** (~$1.19/hr, community cloud), template `RunPod PyTorch 2.x`,
network volume on `/workspace` **>= 300 GB**, Expose TCP 22. Transfer the repo as in
`RUNPOD_LAUNCH.md` section 2.

```bash
# PASS A — Qwen2.5 (7 cells)
bash bootstrap_fp16.sh && bash run_a23_controls.sh a

# PASS B — Qwen3 (6 cells); Qwen3 needs the pinned stack
pip install "vllm==0.8.5" "transformers==4.51.3" "numpy<2"
bash run_a23_controls.sh b
```

If the volume is smaller than 300 GB, add `CLEAR_CACHE=1` to drop each model after its cell:
`CLEAR_CACHE=1 bash run_a23_controls.sh a`

The script is idempotent: a cell whose three condition files already exist is skipped, so a
pod that dies mid-run can simply be restarted with the same command.

## Retrieve, then aggregate with no GPU

```bash
# on the pod
tar czf a23_controls.tgz results/v28/controls results/v28_recipe logs
runpodctl send a23_controls.tgz

# stop billing
~/runpodctl.exe stop pod <id>

# locally, in the repo root
python a25_v28_aggregate.py        # -> results/v28/A25_summary.md , results/v28/a25.json
```

`a25` Part 2 prints the controls side by side with concealed (v27), disclosed (v27) and
placebo (v27): trap/gold counts on the declared==gold trap subset (n=12 per config), trap
share of the two equal-tier tools, Wilson 95%, exact test vs 50%, and the per-tool breakdown
for D1/D2/D4/D6.

## Cost and time — estimate, not a quote

Inference here is trivial (12 trap tasks x 3 repeats x 3 conditions = 108 generations per cell).
**Weight download and vLLM warm-up dominate.** `run_v28_session.sh` measured ~4-6 GPU-h for its
Qwen2.5 pass and ~1.5 GPU-h for Qwen3, including the full 216-task runs this script omits.
Expect roughly **4-7 GPU-h total, about $5-9**, plus volume storage. Budget a working day.

## Where the result goes in the manuscript

- Methods: one paragraph defining the three controls (the harness already releases them).
- Results: the `a25` Part 2 table as a new table, next to the trap-selection diagnostics.
- Discussion / Table 10: the claim grade for the agent-level reading moves up or down
  according to the decision rule above.
