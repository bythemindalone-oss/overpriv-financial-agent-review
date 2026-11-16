# Verification checklist (reviewer-facing)

| manuscript item | command | expected |
|---|---|---|
| Tables 3, 4 | `python run_reference.py` | reference-policy rates reproduce exactly |
| Table 6 (13 corrected rows) | `python a20_fill_table6.py --all` | OPUR / impact / gap / MEagent per configuration |
| Table 6A (base 198, 18 cells), H1, H2, H3 | `python a22_revision_analysis.py` | +12.1 pp and +18.2 pp within-family contrasts; H3 +10.5 / +10.6 pp |
| Two-way (equal-tier) baseline, §5.2 | `python a26_reviewer_response.py` | concealed 125/151 = 82.8%; disclosed 100/150 = 66.7% |
| Merged-cell sign tests, §5.2 | same script | 13 labels p = 0.0020; 10 merged cells p = 0.016; 6 checkpoints p = 0.0625; 4 tools 2/4 |
| Lexical cueing, §5.2 and §5.7 | same script | normal 83/90 unique best match; trap 13/18 trap-favoured, 0/18 gold-favoured |
| Graded severity, §6 | same script | w(T4)=0.5: 17/18 negative; T5 only: 11/18 non-negative |
| Table 11 (request-wording controls) | `bash run_a23_controls.sh a` then `b` (GPU), then `python a25_v28_aggregate.py` | neutral 38.7%, gold-cued 0/156, concealed re-run 83.4%; aggregate as deposited in `results/v28/A25_summary.md` |
| Labeler sensitivity, §4.3 | `python a18_rescore_expert_gold.py` | mean pairwise weighted kappa 0.846; 7/198 gold labels change; ≤ 0.5 pp movement |

Run every command from the repository root. `a06_h1_glmm.py` and `a22_revision_analysis.py` need `statsmodels` and `pandas`; the others need only the standard library and `numpy`.

> **Table 11 provenance.** The control conditions were executed after the archived deposit, on vLLM 0.33.0. The per-task records of those runs were not retained; the deposited artefact is the aggregate in `results/v28/A25_summary.md`, and the row above reproduces it by re-executing the harness. The concealed condition was re-run on the same stack as an internal control (83.4% against the archived 82.8%).
