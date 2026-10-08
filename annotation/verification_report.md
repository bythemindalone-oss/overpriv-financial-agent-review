# Annotation verification report

- 4 stable random pseudonymous annotators; 198 aligned tasks; 792 records.
- Source workbook roles, names, sheet names, comments, free text, and OOXML metadata are excluded from rating exports.
- Exact vote values and source row order were independently checked against all four sources; integrated labels matched; source hashes remained unchanged.
- A private-source-marker scan passed for exported files, including source filenames, sheet labels and workbook creator/last-modifier values.
- Rating files contain only task_id, min_tier, correct_behavior. Pairing is retained through anonymous file IDs.
- Per-task category counts, all six tier and behavior contingency tables, and exact input counts are exported.
- Tier linear-weighted kappa mean: 0.846257016568.
- Conventional ordinal alpha: 0.910482280434.
- Behavior nominal kappa mean: 0.886827302917.
- Tier consensus uses the exact existing A18 upper-median function, not an invented tie rule.
- Rounded-mean labels use Python ties-to-even. Modal ties are retained as candidate sets, not resolved from anonymous-ID order.
- No behavior consensus is fabricated.

## Unanimity
- exact_tier_unanimous: 127/198.
- impact_threshold_unanimous: 184/198.
- behavior_unanimous: 177/198.
- role_cap_threshold_unanimous: 144/198.

- Impact-boundary unanimity means all four min_tier votes lie on the same side of T4/T5 (tier >= 4). It is not exact-tier agreement or operational intent agreement.
- Operational execution impact remains measured from traces, not inferred from annotation votes.
- Source refusal rows without an impact field are retained as null in metric inputs; only A18 scoring maps null selected tier to (0,0).

## Metric limitations
- Paper pp11-12 definition supplied in review context: expert-reconstructed legitimate-high tasks satisfy min_tier >= 4 AND correct_behavior == select_tool; divide count by full216.
- MEdef under this supplied definition is a potential upper-bound/design-constant proxy, not observed realized per-config ME.
- The PDF definition was supplied by the coordinating review agent; this script directly validates the underlying votes, not the PDF passage.
- Exported missed_escalation uses the existing A18 intent-impact 2x2 definition, separately and explicitly named.
- Traps are not expert-labeled and retain author gold in full216 re-scoring.
- Human provenance and independence cannot be established from files alone.
- Alpha is independently implemented using conventional pooled ordinal distances; no source alpha implementation was identified.

## Reproduce
Run `python analysis/reliability.py` from the package root. The script reads the anonymized rating manifest and the whitelisted metric_inputs.json, then recomputes all derived outputs in annotation/.

## Grounded execution results
- Author intent re-scoring matches all 18 published run results to one decimal.
- Per-expert canonical missed_escalation ranges: base198 16.161616161616% to 17.676767676768%; full216 14.814814814815% to 16.203703703704%.
- These canonical missed_escalation values are distinct from the separately reconstructed MEdef design constant.
- Operational intent unanimity for each run is also listed in reliability_summary.json; it differs from the annotation T4/T5 boundary test.

## Expert reconstructed MEdef design constant
- Predicate: min_tier >= T4 AND correct_behavior == select_tool; only the 198 expert-labeled base tasks contribute to numerator. Full216 denominator is the supplied paper convention.
- No trap annotation votes, execution policies or realized impacts are fabricated.
- Counts sorted across anonymous experts: [31, 35, 38, 38].
- Exact percentage range: 14.351851851852% to 17.592592592593%, rounding to 14.4-17.6%.
- Paper count multiset matches: True; rounded range matches: True.
- Per-expert counts are in expert_design_constant.csv; all 792 task-level membership decisions are in expert_design_membership.csv.
