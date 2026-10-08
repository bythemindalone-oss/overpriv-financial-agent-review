# Rendering-fault correction evidence

The manuscript reports a missing task field that prevented trap prompts from reaching the model, followed by a one-line correction. The preserved `results/runs/` files are the pre-correction stage; `results/masked/` and `results/leaked_traps/` hold the later trap-stage outcomes. Replay checks compare these records without editing the observations.

The present `overpriv/corpus_gen.py` and `overpriv/llm_runner.py` contain the corrected rendering inputs and `_user_msg` template. However, the inspected repository starts with a consolidated reproduction-package commit, and its visible six-commit history does not include a separately identifiable historical rendering-fix commit or the original pre-fix source. No original fix patch or date has been fabricated.

Before claiming that the historical fixing commit itself is publicly released, the authors must provide the original pre-fix/fixed source pair or actual fixing commit. A reconstructed illustration is not historical evidence. Preserving before/after outcome files establishes an inspectable contrast, not the exact historical timing or execution provenance.
