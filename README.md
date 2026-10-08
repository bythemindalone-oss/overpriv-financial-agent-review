# Measuring What Selection Logs Miss: artifact-evaluation preparation

**PRIVATE PREPARATION. Not approved for public release or journal submission.**

Curated evidence for the manuscript Measuring What Selection Logs Miss: A Deterministic Benchmark for Execution-Level Auditing of Air-Gapped Financial-Operations LLM Agents, by Hyung-Chul Lee and Bo-Young Kim. Original private development history remains unchanged. This new distribution history is not a claim that all historical work was manually authored.

## Scope
- 198 synthetic base tasks plus 18 trap tasks (216 total).
- 18 base-stage configurations; 13 corrected trap-stage configurations under concealed, disclosed, and placebo conditions.
- Four label sets exported as stable pseudonymous CSVs, preserving 792 tier/behavior votes. Files alone do not establish independence.
- Core deterministic mock execution/scoring, no production systems or model weights.
- Original result records preserved; four provenance files have documented host redaction.

## Offline evaluation
Use Python 3.10+ from package root:
1. `python -X utf8 analysis/reliability.py` recomputes annotation results.
2. `python -X utf8 analysis/replay.py` replays selections and compares explicit paper expectations, without model calls.

The legacy `a20_fill_table6.py --validate` is NOT a real validation gate. Figure scripts use some paper-derived constants; successful redraw is not independent statistic reproduction. NumPy/SciPy/statsmodels/matplotlib were unavailable in this preparation environment; full inference and graphics reruns are not claimed.

## Reading guide
- data/, overpriv/: corpus, taxonomy, mock execution, scoring.
- results/runs/: original base-stage files, including faulty trap outcomes.
- results/masked/, leaked_traps/, placebo/: concealed, disclosed, placebo.
- annotation/: anonymous paired votes, consensus, reliability inputs/results.
- figures/: supplied figures, not yet visually certified against PDF.
- verification/: measured comparisons and unresolved limitations.
- documentation/: redaction, correction/provenance caveats and manuscript-update checklist.

## Public release gate
Resolve discrepancies, obtain human-author approval, align manuscript URLs/AI disclosures, complete license/privacy review, and freeze an archived version. No new DOI is claimed.

Code MIT; synthetic data CC-BY-4.0. Existing notices retained. Package preparation was AI-assisted at the author’s request; final responsibility and approval remain with human authors.

Saved a06/a07 inferential outputs are historical comparisons only; inference has not been rerun here. Figure scripts need matplotlib and a08/trap_outcomes.csv.
