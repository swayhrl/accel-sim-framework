# START — NVBit 1.7.5 model-level Lane G capture

Read-only handoff branch:

```text
hrl/vm-c16-g-retry570-chatgpt-handoff-v3
```

Qualified active checkpoint:

```text
d001a349156c51aa6de15f30b9aedaa70f534442
```

Primary handoff:

```text
docs/vm_tlb/codex_handoff/c16/retry570/LANE_G_NVBIT175_MODEL_CAPTURE_HANDOFF.md
```

## Start procedure

Do not checkout/reset/merge the handoff branch into the active Lane G worktree.

```bash
git fetch origin hrl/vm-c16-g-retry570-chatgpt-handoff-v3

git show \
  origin/hrl/vm-c16-g-retry570-chatgpt-handoff-v3:docs/vm_tlb/codex_handoff/c16/retry570/LANE_G_NVBIT175_MODEL_CAPTURE_HANDOFF.md
```

Read it completely, then continue on the current `hrl/vm-c16-g-retry570-v0` worktree.

## Immediate order

```text
M0 freeze exact retained Llama/model/input/runtime identity
 -> M1 full frozen model no-trace runtime/prewarm canary
 -> M2 rebind exact indexSelectLargeIndex + derive NVBit-1.7.5 static ordinal
 -> M3 one narrow model capture canary
 -> M4 two independent reproducibility runs
 -> M5 complete frozen B1/T128/decode4 target capture
 -> M6 publication + STOP for review
```

Important: historical static ordinal 348 is a candidate requiring NVBit-1.7.5 requalification. Never reuse ordinal 34.

“Full capture” does not mean unbounded tracing of every model kernel. It means all occurrences of the requalified target instruction/range across the complete frozen model workload window.

## Hard rules

- NVBit fixed at 1.7.5.
- effective module loading fixed at EAGER.
- keep CUDA/driver/PyTorch/model/input fixed.
- no network model/tokenizer download.
- no model/input substitution.
- prewarm occurs before `MEASUREMENT_ACTIVE`.
- raw traces remain outside Git and must close remote SHA -> local copy -> local SHA.
- enforce storage/file-size safety limits.
- do not continue to Qwen/other models after Llama M6 without review.

## Required lead report

```text
MODEL_CAMPAIGN_IDENTITY_FROZEN=
INPUT_BINDING=
M1_NVBIT175_LLAMA_RUNTIME_READY=
M2_TARGET_FULL_MANGLED_IDENTITY=
M2_TARGET_LAUNCH_COUNT=
M2_NVBIT175_STATIC_ORDINAL=
M2_HISTORICAL_348_STATUS=
M3_SINGLE_WINDOW_CAPTURE=
M3_RECORD_COUNT=
M4_REPRO_RUN1_RECORD_COUNT=
M4_REPRO_RUN2_RECORD_COUNT=
M4_REPRODUCIBLE=
M5_FULL_FROZEN_WORKLOAD_CAPTURE=
M5_RECORD_COUNT=
M5_TRACE_BYTES=
TRACE_SCHEMA_VALIDATION=
MEASUREMENT_WINDOW_CLEAN=
ACTIVE_GPU_PROCESS_COUNT=
MEASUREMENT_ACTIVE_AFTER_RUN=
PUBLICATION_COMMIT=
PUBLISH_MANIFEST_SHA256=
```

Do not stop at the first minor implementation obstacle. Attempt bounded, evidence-preserving fixes within the frozen campaign contract. Stop early only if model identity, measurement isolation, storage safety, or the fixed software/runtime matrix would otherwise be violated.
