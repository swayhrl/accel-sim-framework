# Post-Llama multimodel master handoff

## Entry condition

Consume this handoff only after the active Lane G branch publishes a Llama S6 closeout showing that the current NVBit 1.7.5 path is usable at model level.

The Llama closeout becomes the **reference implementation pattern**, not a source of static ordinals for other models.

Before doing anything else, record:

```text
LLAMA_CLOSEOUT_COMMIT=
LLAMA_PUBLICATION_MANIFEST=
LLAMA_PREFILL_TARGETS=
LLAMA_DECODE_TARGETS=
LLAMA_PREFILL_RECORDS=
LLAMA_DECODE_RECORDS=
LLAMA_STRUCTURAL_ZERO_NOTES=
```

If Llama decode uses a different kernel path than prefill, preserve that lesson: phase-specific targets are allowed and often expected.

## Goal

Complete all remaining required AI-trace models:

1. Qwen 0.5-class campaign target
2. Qwen 7B AWQ campaign target
3. DeepSeek campaign target
4. GLM campaign target

Then build one cross-model, analysis-ready trace dataset with consistent provenance and validation.

## Core policy change learned from Llama

Do **not** impose one target kernel/range across prefill and decode.

For every model build a phase-target manifest:

```text
PREFILL_TARGETS = one or more requalified memory targets
DECODE_TARGETS  = one or more requalified memory targets
```

A target that is absent in a phase is a valid `STRUCTURAL_ZERO_TARGET_NOT_LAUNCHED` only after an independent kernel census proves that the target function is not launched in that phase.

Never interpret zero records as zero memory traffic.

## Runtime lock

Keep the proven infrastructure fixed:

```text
GPU                  RTX3090 / SM86
Driver               570.124.04
CUDA                 12.4
PyTorch              2.5.1+cu124
NVBit                 1.7.5
effective loading     EAGER
Lane G tracer         qualified lineage from Llama closeout
```

No NVBit 1.8 work in this campaign.

## Overall phases

```text
A. identity + asset recovery
B. Qwen 0.5 S0-S6
C. Qwen 7B AWQ S0-S6
D. DeepSeek S0-S6
E. GLM S0-S6
F. cross-model normalization + integrity + dataset closeout
```

Each model uses a fresh recovery deployment/budget namespace. Historical ledgers remain immutable.

## Per-model S0-S6

### S0 exact identity freeze

Freeze exact model ID, revision/content hash, quantization, dtype, deterministic input, batch/sequence/decode contract, backend/offload/device-map behavior, and local asset hashes.

### S1 full-model no-trace runtime gate

Run the complete frozen workload with capture disabled/no-match. Require normal completion, stable checksum/terminal evidence, prewarm trace count 0, clean process state.

### S2 phase-aware target discovery

Obtain separate prefill/decode kernel census. Select scientifically relevant address-bearing memory target(s) for each phase.

For every selected target bind:

- full mangled identity;
- phase/step launch count;
- NVBit 1.7.5 static ordinal/range;
- opcode;
- global/local/shared memory space as applicable;
- address-bearing proof.

Never reuse another model's static range.

### S3 narrow capture canary

Capture one bounded target occurrence per phase-target class. Require nonzero records for launched targets, parser/schema pass, no prewarm contamination.

### S4 reproducibility

Repeat in an independent process. Raw addresses may differ; identity/range/schema/phase and structural record contract must agree.

### S5 full frozen workload capture

Capture all required occurrences over the complete frozen workload. Preserve phase attribution, and decode-step attribution where the workload exposes steps separately.

### S6 model publication

Remote SHA -> local copy -> local SHA closure; raw traces stay out of Git. Publish exact identity, target manifest, phase counts, bytes, parser results, storage accounting, cleanup proof.

## Downstream-consumer check before each S5

Before final S5 for the first non-Llama model, inspect the actual downstream trace consumer/converter in this repository and answer:

```text
Does the scientific consumer require:
A) selected phase-specific target memory streams, or
B) all address-bearing global-memory records inside the ROI?
```

If B is required, do not mistake target canaries for the final scientific dataset. Use S3/S4 only to qualify the path, estimate storage, then perform a bounded ROI-wide memory capture if the tracer supports it and storage safety passes.

Do not broaden capture blindly; document the exact downstream requirement and the selected final contract.

## Model failure policy

A failure in one model must not terminate later models unless it reveals a global infrastructure invariant failure.

Allowed terminal blockers include:

```text
BLOCKED_IDENTITY_UNRESOLVED_REQUIRES_USER
BLOCKED_ASSET_FETCH_AUTH_REQUIRED
BLOCKED_ASSET_UNAVAILABLE_AFTER_AUTHORITATIVE_SEARCH
BLOCKED_MODEL_DOES_NOT_FIT_FROZEN_RUNTIME
BLOCKED_TARGET_REQUALIFICATION
BLOCKED_STORAGE_SAFETY
```

Never silently substitute a different model/quantization/size.

## Final success

The post-Llama campaign is complete only when each remaining model is either COMPLETE with validated traces or has a precise evidence-backed blocker, and the cross-model dataset audit is published.
