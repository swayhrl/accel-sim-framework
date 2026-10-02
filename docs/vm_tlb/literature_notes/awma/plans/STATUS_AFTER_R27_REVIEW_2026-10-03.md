# Status after R27 review

Date: 2026-10-03 (Asia/Shanghai)

This supersedes `STATUS_AFTER_R27_AUTHORIZATION_2026-10-03.md` for current AWMA activity. R26's accepted scientific result remains unchanged; R27 did not reach a new varied-input capacity observation.

## Current activity

- Lane G / node109 R27: **COMPLETE / STOP**.
- Accepted R27 classification: `R27_INPUT_OR_SOURCE_NOT_QUALIFIED`.
- Gate A: `R27_PARENT_RAW_QUALIFIED`.
- Gate B: STOP because the sole authorized pinned WikiText-2 train parquet was unavailable byte-for-byte.
- Gates C/D: NOT RUN.
- New R27 CUDA/JIT operations: 0.
- New R27 GPU-lock acquisitions: 0.
- No current AWMA GPU Goal is authorized by this review.
- R26 / R25 / R24 / R23G remain COMPLETE / STOP. Lane F and Lane E remain STOP; R20 remains CLOSED.
- No node174/Accel-Sim, profiler, hardware/PPA, production pilot, second corpus/model, all-parameter training or deployment authorization.

## Exact R27 result

Execution branch:
`hrl/awma-r27-varied-batch-capacity-109-v1`

Execution commit:
`4dca1cd713df8315b9e04f702d7f3b990c8f4b88`

Execution tree:
`03debf7395f51062c133ad4d534791f2b5fc1770`

Exact handoff parent:
`5144bde8f9d7b399a596395e0c88ee89025b3a6f`

Handoff tree:
`605f0360debb3f62a1923452c91552ca1f2acaa9`

The execution commit is the single direct child of the handoff, and the remote execution branch points to it.

Scientific review:
[`R27_VARIED_BATCH_CAPACITY_REVIEW_2026-10-03.md`](../empirical/R27_VARIED_BATCH_CAPACITY_REVIEW_2026-10-03.md)

Execution review pack:
https://github.com/swayhrl/accel-sim-framework/tree/4dca1cd713df8315b9e04f702d7f3b990c8f4b88/docs/vm_tlb/review_packs/AWMA_R27_TIED_WEIGHT_VARIED_BATCH_CAPACITY_STABILITY_109_V1

## What R27 establishes

R27 successfully closes the R26 raw-evidence gap on the execution side: the node164 R26 archive/manifest/common checkpoint and the 12 endpoint confirmations were read back and parsed under Gate A, with the expected C1 B70 PASS, C1 B71 OOM, S2 B71 PASS and S2 B72 OOM 3/3 pattern. The B71 C1 failure is recorded after two complete steps, on the third-step `BACKBONE_COMPACT_LOOKUP_BACKWARD`, with a 142.00 MiB failed allocation request.

R27 also establishes that the exact authorized new input was not available through the bounded execution paths at the time of the run. The runner correctly did not substitute another source, split, corpus or proxy.

## What R27 does not establish

There is no new evidence about whether varied text preserves, removes or reverses the R26 one-batch capacity distinction. There is no new B1 varied-stream numerical result, natural-capacity search, 32-step trajectory/resume result, timing result, production result or hardware result.

Therefore do not label R27 as a capacity negative or as partial support for `R27_VARIED_BATCH_CAPACITY_EXTENSION_32_STEP_SUPPORTED`.

## Current research boundary

R26 remains the latest accepted capacity result and retains its narrow repeated-sequence tied-W scope. R27 is an evidence/input-gate STOP, not a scientific falsification.

If the exact 6,357,543-byte parquet with SHA256 `e83889baabc497075506f91975be5fac0d45c5290b6b20582c8cd1e853d0c9f7` is later supplied and durably admitted, continuation requires a new reviewed handoff/contract. Do not implicitly resume the closed execution branch, and do not automatically open GPU work merely because the missing file later becomes available.

C16 Stage A and DTC-L1 remain separate project lines and contribute no authorization or conclusion to R27.
