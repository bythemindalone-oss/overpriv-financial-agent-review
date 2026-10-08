# Serving provenance and replication limits

`results/runs/` preserves 18 base-stage result files (including pre-correction trap outcomes). `results/masked/`, `results/leaked_traps/`, and `results/placebo/` preserve 13 configurations each. Folder names are historical: masked=concealed, leaked_traps=disclosed.

`configs/models.yaml` is an ORIGINAL planning configuration for 15 cells, not proof that its flags were applied to all measured cells. It uses FP8 for a condition labeled INT8; do not infer an integer checkpoint implementation from that label. Source provenance files for four cells record model ids, version information, flags, and hashes, but cannot establish loaded numerical dtype or original experiment execution in all 18 cells.

`results/provenance_logits/` contains later probe artifacts. Do not interpret them as first-token logits saved during the original selection experiment or as proof resolving identical-selection cells. Host identifiers have been redacted from provenance while numerical fields have been preserved.

The per-task records retain modal selections and reproducibility rates, not the full three repeated responses or all before/after state snapshots. No original full response trace, independent registry timestamp, or append-only production log is supplied here. Absence must not be filled with generated observations.

The optional LLM runner makes requests to a vLLM endpoint; it is not invoked by offline verification. Model weights, private credentials, endpoint addresses, and deployment-account operations are excluded.
