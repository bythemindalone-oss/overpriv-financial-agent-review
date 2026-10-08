# Supplement S3: retained serving provenance and unresolved limitations

## Coverage
Four provenance records cover Qwen2.5-7B and32B under configured FP16/INT8. The result logs cover18 original configurations and13 trap remeasurements. The original15-cell planning YAML does not fully specify the measured18 cells or verify runtime precision.

## Source records
results/provenance/*.json retain checkpoint IDs/revisions,reported GPU/software settings,serving flags,and input/output hashes. Host identifiers are redacted. The original retained note about FP16 weights and INT8 identifiers is internally inconsistent; it has not been rewritten to invent verification.

## Hash and schema results
The four recorded base corpus hashes and output hashes match their files. The four recorded trap-corpus hashes do not match the canonical released trap JSON. All18 canonical trap rows omit domain_desc;the current generator supplies it. A rendering-only derivative with this field is documented in revisions/rendering_inputs/;original records remain unchanged. No historical timing or input substitution is asserted.

## Harness version
The copied core identifies package version0.1.0,while the source archive is v1.2.0. No explicit per-run harness-version field was retained. The source baseline commit is recorded privately;absence of per-run version evidence is stated rather than filled in.

## Quantization
The planning YAML labels INT8 with FP8 flags;some provenance identifies GPTQ-Int8 checkpoints. Actual loaded tensor dtype is not supplied for all cells. Treat labels as configured conditions,not verified precision. Quantization-specific causal inference is not retained.

## Later probes
results/provenance_logits/ contains later generic prompt probes. They are not original task logits,nor proof of original run dtype or date.

## Missing records
Original three repeated responses,per-call before/after snapshots,typed exception logs,and demonstrated network isolation are absent. Refusal rows conflate error/no-call/refusal/unknown tool cases. No surrogate observations have been generated.

## Correction
Before/after outcome files remain available,but the consolidated source history has no identifiable historical rendering-fix commit. The new schema derivative is a current repair,not a replacement for that missing historical evidence.
