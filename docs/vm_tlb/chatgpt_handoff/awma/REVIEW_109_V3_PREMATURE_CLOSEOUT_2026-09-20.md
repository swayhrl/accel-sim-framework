# ChatGPT Review — 109 V3 20h Premature Closeout

Date: 2026-09-20

Reviewed execution:

`hrl/awma-109-20h-unattended-e1-e3-v3 @ baa3da1593b237cf3791c39d446588da4e3e02e4`

Accepted scientific result:
- M1 threshold characterization is accepted.
- AWQ M1023 = QUANT_GEMM.
- AWQ M1024 = DEQUANT_MATMUL.
- raw controls are stable across the boundary.

However, the campaign-level completion marker is reclassified as:

`INTERIM_CHECKPOINT_PREMATURE_CLOSEOUT`

not as exhaustion of the authorized 20h campaign.

## Why

The campaign clock was:

- START = 2026-09-19T17:03:38Z
- NO_NEW_GPU = 2026-09-20T11:03:38Z
- DEADLINE = 2026-09-20T13:03:38Z

The branch closed only minutes after START.

Several tasks were marked SKIPPED_GATE for conditions that the handoff explicitly authorized Codex to solve as engineering work:

- M2: no isolated selector canary materialized;
- M3: no frozen decomposition boundary;
- M4/E3: harness not materialized;
- G1: no new input authority;
- G4: no frozen input authority.

Those are not valid campaign-exhaustion conditions.

## Corrected interpretation

Accepted:
- M0/M1 results.

Not accepted as final disposition:
- M2/M3/M4/G1/G4 were not meaningfully attempted under the solve-and-continue policy.

The continuation must use the ORIGINAL campaign deadline, not restart a new 20h clock.

## Hard rule for resume

A task may not be marked SKIPPED_GATE merely because an engineering artifact does not already exist when the scientific contract explicitly authorizes materializing it.

Before marking such a task unresolved, produce an ENGINEERING_ATTEMPT_RECEIPT containing:
- what was attempted;
- source/runtime authority;
- exact failure;
- bounded alternatives tried;
- why further work would require a scientific contract change.

## Remaining priorities

1. M2 isolated module-level NCU selector + resource profiling.
2. M3 same-quantized-weight decomposition.
3. M4/M5 Q30 exact experts harness + N/P/U-active if qualified.
4. G1 Qwen0.5B scenario extension with newly materialized but honestly labeled input authority.
5. G4 Llama raw shape holdout with newly materialized activation authority.
6. G3 profiler protocol sensitivity if M2 works.
7. M9 optional M1023/M1024 detailed capture if gates pass.

No architecture mechanism or new model download.
