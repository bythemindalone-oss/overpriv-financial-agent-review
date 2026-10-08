# Bounded offline artifact replay

Command: `python -X utf8 -I -B analysis/replay.py` from package root. Script also works from a clean cwd with its absolute path.

Checks 819; failed 0; raw intent/impact mismatches 0.
Corrected Table6: 13/18 configurations, base198 + concealed18.
Primary concealed/disclosed/placebo: 80.1/64.1/78.8 percent, n12 D1/D2/D4/D6.
Exact paired sign test: 10 positive, 0 negative, 3 ties, two-sided p=0.001953125.
All gaps negative at T3 w=0,.25,.5,.75,1: True. Linear gap endpoints bound the entire interval.

Table7 reports per-domain trap selections (n39), not primary n12 missed escalation. Table9 reports original normal/legit_high/attack base198 utility; invalid original trap refusals separated. Errors before/after are refusals/missing fields, not fabricated exception counts.

Field counts: base {12: 198}, released traps {11: 18}; datasheet enumerates11. All18 released trap rows lack domain_desc present in current generator. Task IDs unique216; base ID length8, trap length10. Source corpus retained unchanged.
Observable trap refusals before/after: {'after_concealed': {'configs_available': 13, 'trap_rows': 234, 'trap_refusals': 0, 'actual_exception_count': None}, 'after_disclosed': {'configs_available': 13, 'trap_rows': 234, 'trap_refusals': 0, 'actual_exception_count': None}, 'after_placebo': {'configs_available': 13, 'trap_rows': 234, 'trap_refusals': 0, 'actual_exception_count': None}, 'before_pre_correction': {'configs_available': 18, 'trap_rows': 324, 'trap_refusals': 324, 'actual_exception_count': None}}. These are not typed exception counts.

## Failed checks

None.

## Limitations

- Artifact replay only, not independent model inference, weights validation, real financial execution, or causal replication.
- Modal choices and claimed repeats/repro_rate retained, actual three replicate selections absent. Repeat reliability cannot be independently audited.
- Actual tensor dtype/quantization and serving-state snapshots absent. Four provenance records are partial claims/hash evidence, not dtype evidence for all18.
- Raw scores can agree with deterministic tier-based mock execution without proving real-world effects. Raw before/after sandbox snapshots not retained.
- Pre-correction trap refusals are observable; typed runtime-error counts unavailable. Caught exceptions/no calls/refusal/unknown tools conflated.
- Corrected Table6 combines temporally separate base198 and concealed18 files. Llama configurations and Qwen2.5-72B INT8 lack concealed18; corrected impact/gap not imputed.
- H1/H2/H3 numerical model-based inference UNVERIFIED: scipy/statsmodels unavailable and not executed. Exact sign test is not a substitute for those models.
- Saved full Table6 aggregate comparison is not independent authentication of manuscript rows; embedded paper constants are comparisons only.
- Datasheet enumeration lists11 fields but actual corpus/generator field counts differ. Canonical English corpus and trap input untouched.
- Legacy a20 --validate not run or claimed to validate paper. Inspected implementation has no expected-value assertion under that flag.

## Provenance hashes

- results/provenance/qwen2.5-32b_fp16.json: corpus_sha256 match, corpus_traps_sha256 MISMATCH, result_sha256 match
- results/provenance/qwen2.5-32b_int8.json: corpus_sha256 match, corpus_traps_sha256 MISMATCH, result_sha256 match
- results/provenance/qwen2.5-7b_fp16.json: corpus_sha256 match, corpus_traps_sha256 MISMATCH, result_sha256 match
- results/provenance/qwen2.5-7b_int8.json: corpus_sha256 match, corpus_traps_sha256 MISMATCH, result_sha256 match
