# Revision evidence package — *Measuring What Selection Logs Miss*

Public evidence package for the revised manuscript *Measuring What Selection Logs Miss: A Deterministic
Benchmark for Execution-Level Auditing of Air-Gapped Financial-Operations LLM Agents* (Frontiers in
Computer Science, Computer Security).

It contains the records and scripts a reader needs to recompute every number in the manuscript. It is
separate from the original measurement archive and contains no personal data.

* Original measurement archive (unchanged, historical): https://doi.org/10.5281/zenodo.22757475 (v1.2.0),
  resolved by the concept DOI https://doi.org/10.5281/zenodo.22178240
* Mirror of the original package: https://github.com/bythemindalone-oss/overpriv-financial-agent

## No personal data

The four practitioners who labeled the corpus appear only as rater identifiers in a stable random order;
the mapping to job roles, the source survey workbooks and all office metadata are excluded. Serving
provenance records are released with the host name redacted. Every task in the corpus is synthetic.

## Start here

```bash
python -X utf8 -I -B analysis/replay.py        # replay of the saved observations
python -X utf8 -I -B analysis/reliability.py   # anonymous paired labels
python -X utf8 -I -B analysis/reanalysis.py    # revised statistics and cohorts
python run_reference.py                        # Tables 3 and 4
python a20_fill_table6.py --all                # Table 6, the 13 corrected rows
python a22_revision_analysis.py                # Table 6A (base 198), H1-H3
python a26_reviewer_response.py                # two-way baseline, merged sign tests, lexical overlap, graded severity
python a18_rescore_expert_gold.py              # labeler sensitivity from the anonymous labels
```

`VERIFY.md` maps each manuscript item to the command that reproduces it. Scripts run from the repository
root. `a06_h1_glmm.py` and `a22_revision_analysis.py` need `statsmodels` and `pandas`; the rest need only the
standard library and `numpy`.

## Layout

| path | contents |
|---|---|
| `data/` | the 216-task synthetic corpus (198 base + 18 trap), JSON and CSV |
| `overpriv/` | the deterministic mock-execution instrument, scoring, metrics and the serving runner |
| `analysis/`, `a*.py` | replay, reliability, and every revision analysis |
| `annotation/`, `labeling/` | codebook, gold-rule verifier, consensus tables, anonymous rater labels |
| `results/` | raw per-task run records and the output of each analysis script |
| `supplements/` | working copies of the supplementary material; `supplements/as_submitted/` holds the four files uploaded to the journal (S1–S4) |
| `revisions/`, `documentation/`, `verification/` | the revision log, scope and disclosure notes, and integrity check reports |
| `figures/` | figure sources |

`supplements/as_submitted/Supplementary_S4_TwoWay_Baseline_and_Controls.xlsx` is new in this revision: it
holds the two-way (equal-tier) baseline per configuration and per tool, the sign tests after merging
duplicate cells, the request-to-tool lexical overlap for all 216 tasks, and the graded-severity re-scoring.

## What this package does and does not establish

It establishes that the reported counts, rates, intervals and tests follow from the retained records. It does
not establish the numerical precision actually loaded during the original serving runs (see
`supplements/as_submitted/Supplementary_S3_Serving_Provenance.xlsx`), network isolation, or any property of
production systems.

## Licence

Code: MIT (`LICENSE`). Synthetic data and labels: CC-BY-4.0 (`data/LICENSE`).
