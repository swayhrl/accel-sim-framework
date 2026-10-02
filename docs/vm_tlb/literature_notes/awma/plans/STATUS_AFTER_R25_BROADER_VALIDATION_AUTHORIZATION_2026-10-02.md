# Status after R25 broader validation authorization

Date: 2026-10-02.

This supersedes `STATUS_AFTER_R24_REVIEW_2026-10-02.md` only for current execution authorization.
Historical R24/R23/R22 decisions and review packs are not rewritten.

## Accepted completed state

- R24 execution `41795817a5b86959c86cc36c6973f292be33c6a6`: COMPLETE / STOP.
- R24 empirical interpretation remains: large causal capacity benefit; S2>S1 stable; S2 vs B0 mixed/near-neutral; execution label has the documented post-formal decision-contract caveat.
- R23G remains COMPLETE / STOP.
- Lane F / R22F1 remains STOP.
- Lane E / R22E remains STOP.
- R20 remains CLOSED.
- No old C16/R101/OEQ line is reopened.

## Newly authorized task

Lane G / node109 is authorized for one bounded broader software validation:

`AWMA_R25_TIED_WEIGHT_BROADER_SOFTWARE_VALIDATION_109_V1`

Handoff branch:
`hrl/awma-r25-tied-weight-broader-validation-handoff-v1`

Handoff HEAD:
`9939291fbc0e890d703c6cfffe8d29e5435f9f0e`

Execution branch to create:
`hrl/awma-r25-tied-weight-broader-validation-109-v1`

Start:
`docs/vm_tlb/chatgpt_handoff/awma/r25_tied_weight_broader_validation_v1/START_HERE.md`

Goal:
`docs/vm_tlb/chatgpt_handoff/awma/r25_tied_weight_broader_validation_v1/LANE_G_R25_TIED_WEIGHT_BROADER_VALIDATION_109_GOAL.md`

## Purpose

R25 does not tune the R24 point.

It introduces:
- `C1_COMPACT_FULL`: compact lookup-side accumulation plus exactly one full classifier/total gradient, as the stronger primary software comparator;
- `S2_TILED`: no formal full VxH gradient, using the same fixed 32 MiB FP32 tile-budget rule;
- D0: exact R24 Qwen discovery/calibration point;
- H0: accepted `meta-llama/Llama-3.2-1B` asset plus the existing frozen `S0/B1/T128/Decode4/TEXT` input as an independent performance holdout.

H0 authority/identity and numerical qualification may be checked before freeze, but H0 performance must not be used to tune implementation.

A four-step repeated-batch optimizer trajectory qualification is required at both points before formal performance.

## Current scope

Node109 only.
All CUDA/JIT uses:
`/data/c16/locks/c16_gpu_campaign.lock`.

No new model/input download.
No re-tokenization of H0.
No tile/context/batch/optimizer sweep.
No convergence run.
No NCU/NVBit/SASS.
No node174/Accel-Sim.
No hardware/PPA.

Node164 remains durable large-data authority.

## Execution policy

Solve-and-continue for ordinary engineering issues.
Any candidate-code fix before implementation freeze requires rerunning numerical/trajectory qualification on both points.
After `IMPLEMENTATION_FREEZE.json`, no candidate behavior change is allowed.
No post-formal decision-classifier edits; R25 decision table is exhaustive.

Qualification failure is not a performance negative.

No R25 result automatically authorizes hardware.
