# Audit-corrected standard-library reanalysis

Finite saved-artifact reanalysis only. No GLMM rerun. Old +2.519 (about +2.52) archived as legacy16config, not original12 confirmation. No historical prespecification claims invented.

## Cohorts

Original12: no Qwen3, five checkpoints. Full18: expanded, eight checkpoints. Binary16: exclude two14B configs, seven checkpoints, distinct from original12. Each has198 base tasks or216 original tasks/config.

## H1: audit-revised decision family

Exact paired McNemar base198; b=small1/large0, c=small0/large1. Holm2 at alpha.05 is audit-revised now, not historically prespecified. Qwen3 separate exploratory.
- qwen2.5-7b_fp16 vs qwen2.5-32b_fp16: n198; small/large intent 34/10; b/c 24/0; RD 12.121212121 pp; exact p=1/8388608 (1.19209289551e-07). Holm2 p=14196869/70368744177664, reject at.05.
- llama3.1-8b_int8 vs llama3.1-70b_int8: n198; small/large intent 42/6; b/c 42/6; RD 18.181818182 pp; exact p=14196869/140737488355328 (1.00874821385e-07). Holm2 p=14196869/70368744177664, reject at.05.
- qwen3-8b_fp16 vs qwen3-32b_fp16: n198; small/large intent 30/9; b/c 21/0; RD 10.606060606 pp; exact p=1/1048576 (9.53674316406e-07). Exploratory, not in Holm2.

Independent task-pair assumption is not established by exact arithmetic. These are finite synthetic templates sharing domains, not generalizable model-population tests.

## H3: labels and denominators

### original12
- normal90: n1080, intent0, impact0, gap 0.000000000 pp.
- nonattack144_legacy_diagnostic: n1728, intent0, impact432, gap -25.000000000 pp.
- attack72: n864, intent259, impact168, gap 10.532407407 pp.
- Matched base gold1-3: attack n864, normal n1080; attack-normal 10.532407407 pp; approximate95% percentile [2.893518519, 20.254629630] pp. Exact6^6=46656 ordered six-domain bootstrap samples, linear percentile interpolation.
- Attack minus legacy nonattack144 35.532407407 pp. Nonattack144=normal90+legit_high36+pre-correction refused traps18. Base nonattack126 is separate in JSON.

### full18
- normal90: n1620, intent0, impact0, gap 0.000000000 pp.
- nonattack144_legacy_diagnostic: n2592, intent0, impact648, gap -25.000000000 pp.
- attack72: n1296, intent450, impact313, gap 10.570987654 pp.
- Matched base gold1-3: attack n1296, normal n1620; attack-normal 10.570987654 pp; approximate95% percentile [1.929012346, 24.151234568] pp. Exact6^6=46656 ordered six-domain bootstrap samples, linear percentile interpolation.
- Attack minus legacy nonattack144 35.570987654 pp. Nonattack144=normal90+legit_high36+pre-correction refused traps18. Base nonattack126 is separate in JSON.

Only six discrete clusters: descriptive/exploratory, not exact95% coverage, no implicit old90%. Original H3 empirical inference withdrawn. Saved a07 mislabeled90% despite alpha=.05 default; archived only.

## H2: withdrawn/nonidentified

Legacy original-family pooled impact DiD 0.0841049382716 (8.410493827 pp, rounds .084), arithmetic only. Unequal checkpoint/family composition across FP16/INT4 cells and unreconstructible execution dtype/quantization prevent an identified empirical quantization effect. No inferential p/CI or surrogate0/1 p.

## Main primary unchanged

Concealed125/156=80.1%, disclosed100/156=64.1%, placebo123/156=78.8%. Thirteen configurations,12 primary traps/config in D1/D2/D4/D6.
- concealed_minus_disclosed: checkpoint6 positive/negative/tie 5/0/1, exact illustrative p=1/16; config13 10/0/3, p=1/512. Checkpoint counts/denominators in JSON.
- concealed_minus_placebo: checkpoint6 positive/negative/tie 2/1/3, exact illustrative p=1; config13 3/1/9, p=5/8. Checkpoint counts/denominators in JSON.
- placebo_minus_disclosed: checkpoint6 positive/negative/tie 4/0/2, exact illustrative p=1/8; config13 8/0/5, p=1/128. Checkpoint counts/denominators in JSON.

Checkpoint grouping is illustrative dependence sensitivity, not a validity substitute.

## III-Gap_excl

Co-primary DESCRIPTIVE, not inferential; this revision label only, no historical prespecification. Corrected base198+concealed18 minus legit_high36: n180/config,13 available,5 missing not imputed. Pooled gap -35/2340 = -1.495726496 pp.

## Integrity

All 84 data/results files byte/semantic identical before/after. Canonical semantic SHA256 4373e44966138d67026d955306d2a48f26b20a343673299c8b4c7cb5bfdf3a6e. Checks include corpus/paired IDs, deterministic per-task raw score agreement, denominators, enumeration/mean identities, exact binomial/interpolation edges, Holm, legacy rates/DiD arithmetic and primary/gap-excl replay agreement.

## Limitations
- No GLMM refit. Old +2.519 archived as legacy16config, not confirmation on original12.
- H1 Holm2 decision family is explicitly audit-revised now, not historically prespecified. Qwen3 remains separate exploratory.
- McNemar conditions on discordant pairs and assumes independent task-level pairs. Shared synthetic templates and six domains mean exact arithmetic cannot establish that assumption. Finite corpus results do not generalize to new tasks, model populations, real finance or production.
- Exact6^6 enumeration describes a discrete six-domain bootstrap distribution; coverage is approximate95%, exploratory/descriptive only, not an implicit legacy90% interval.
- Normal90 differs from legacy nonattack144, which includes legit_high36 and pre-correction refused traps18. No corrected traps for all18 are imputed.
- H2 withdrawn/nonidentified as empirical inference. True quantization/dtype not reconstructible; unequal pooled cell compositions. Legacy .084 arithmetic only.
- Checkpoint6 sign sensitivities are illustrative, not validity substitutes. Shared tasks, related families/checkpoints and unequal serving counts remain dependence/weighting limits.
- III-Gap_excl is co-primary descriptive only in this revision, not inferential or historical prespecification. Corrected concealed data available13, missing5.
- Saved modal choices and deterministic mock scoring only. No network, GPU, real asset/model execution, serving validation, repeat-trace reconstruction or historical preregistration verification.
