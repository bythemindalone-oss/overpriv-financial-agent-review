# Dataset datasheet for the curated evaluation package

## Purpose and composition
Synthetic declared-tool authority versus realized mock-execution benchmark. Six financial domains, ordinal tiers T1–T5. Base: 90 normal, 36 legitimate high-tier, 72 attack tasks. Traps: 18 tasks from six tools; primary subset four tools /12 tasks. Not representative institutional production traffic.

## Canonical inputs
Original data/corpus.json (198), corpus_traps.json (18) and CSV derivative are preserved. Generator variants must not silently replace source evidence. Document schema differences before live replication.

## Annotation
Four sources cover 198 non-trap tasks only. Exports retain task_id, min_tier, correct_behavior. Stable random filenames preserve pairwise/cross-task pairing. Source/role identity map and office metadata remain outside this repository. Consensus uses existing A18 upper median; modal ties are retained.
No survey XLSX, recruitment/contacts, identity mapping or collection form is distributed. Anonymous pairing plus category-count marginals support reproducibility. Published role-specific statistics may permit deductive reidentification; final author review is required.

## Limitations
Recorded votes and calculations do not establish participant recruitment, blinding or independence. This package alone does not prove institutional deployment, loaded weight dtype or preregistration. Missing observations are not synthesized.

## Maintenance
Data CC-BY-4.0, code MIT. Remains private pending review. Original versus export hashes recorded separately. Checksums protect distribution integrity, not historical authorship or empirical truth.
