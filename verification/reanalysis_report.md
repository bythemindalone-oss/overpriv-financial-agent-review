# Reanalysis verification

16128 meaningful checks passed; zero failed.

All 84 data/results files preserved byte-for-byte and semantically. Before/after semantic SHA256 4373e44966138d67026d955306d2a48f26b20a343673299c8b4c7cb5bfdf3a6e.

Run from any cwd: python -X utf8 -I -B <absolute-package>/analysis/reanalysis.py. No model/GLMM, network, GPU, subprocess or installs. Legacy code inspected, not executed. Outputs restricted to six-file allowlist.

See reanalysis_checks.json and reanalysis_manifest.json for corpus IDs, task scores, denominators, numerical identities/edges, replay agreement and baseline before/after per-file hashes.
