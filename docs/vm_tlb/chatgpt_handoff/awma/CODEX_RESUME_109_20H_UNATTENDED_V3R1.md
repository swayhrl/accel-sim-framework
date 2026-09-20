# CODEX CONTINUATION — Resume Original 109 20h Campaign V3R1

Date: 2026-09-20

Mode:
`GOAL MODE / UNATTENDED RESUME / solve-and-continue`

Node:
`109 / RTX4080`

Stage:
`AWMA_109_20H_UNATTENDED_E1_E3_CHARACTERIZATION_V3R1`

Coordination:
`hrl/awma-109-20h-resume-handoff-v3r1`

Parent execution:
`baa3da1593b237cf3791c39d446588da4e3e02e4`

Suggested execution branch:
`hrl/awma-109-20h-unattended-e1-e3-v3r1`

Read:
1. `REVIEW_109_V3_PREMATURE_CLOSEOUT_2026-09-20.md`
2. original `UNATTENDED_POLICY_109_20H_V3.md`
3. original `UNATTENDED_ACCEPTANCE_109_20H_V3.md`
4. original V3 Goal
5. this continuation

## 0. Resume the SAME campaign clock

Do not create a new 20h window.

Authoritative clock:

```text
START_UTC               = 2026-09-19T17:03:38Z
NO_NEW_GPU_SCIENCE_AFTER= 2026-09-20T11:03:38Z
DEADLINE_UTC            = 2026-09-20T13:03:38Z
```

Record current UTC at resume.

If current time is before NO_NEW_GPU:
continue scientific work.

If current time is between NO_NEW_GPU and DEADLINE:
perform closeout only.

## 1. Prior M1 is accepted; do not rerun it

Reuse:
- raw/AWQ q_proj/down_proj M1023/M1024;
- all 9 timing samples;
- fingerprints;
- threshold result.

## 2. Invalid skip states

The following statuses are NOT permitted without an ENGINEERING_ATTEMPT_RECEIPT:

- SKIPPED_GATE_NO_ISOLATED_SELECTOR_CANARY_MATERIALIZED
- SKIPPED_GATE_NO_FROZEN_DECOMPOSITION_BOUNDARY
- STOP_SCIENTIFIC_HARNESS_NOT_MATERIALIZED
- SKIPPED_GATE_NO_NEW_INPUT_AUTHORITY
- SKIPPED_GATE_NO_FROZEN_INPUT_AUTHORITY

These are engineering prerequisites explicitly authorized for materialization.

## 3. M2 — Build the isolated NCU path, do not skip it

Mandatory unless the installed NCU/runtime itself is unusable.

### Strategy A: isolated one-call replay

Build a standalone replay process from accepted shape-specific authority:
- load only exact target module/buffers;
- load exact input tensor;
- warmup;
- NVTX range around one measured semantic module call;
- exit.

No full-model execution required.

First profile the isolated process WITHOUT a fragile kernel-name selector if possible.

Use NVTX range or profile all kernels in the isolated process.

### Strategy B

If NVTX range selection is unsupported:
- run NCU on all isolated-process kernels;
- inspect output;
- derive exact kernel-name/launch selector from the canary itself;
- rerun with exact selector.

### Strategy C

If NCU cannot attach/profile:
- query installed NCU capabilities;
- run a minimal CUDA smoke profile;
- diagnose permissions/replay incompatibility.

Only after bounded engineering attempts may M2 be frozen.

Timebox:
up to 90 minutes of engineering before moving to another READY task.

Required mandatory contrast:
- down_proj raw M1
- down_proj AWQ M1
- down_proj raw M256
- down_proj AWQ M256

Do not use NCU wall time as native latency.

## 4. M3 — Same-quantized-weight decomposition is mandatory

The boundary is already frozen by the acceptance contract.

Do NOT skip for "no frozen boundary".

Role:
`down_proj`

Shapes:
- M1
- M256
- M1023
- M1024

Use exact accepted qweight/qzeros/scales.

A:
deployed AWQ path.

B:
exact AWQ dequantization once outside timed region -> FP16 matmul timed.

C:
exact AWQ dequantization inside each timed invocation -> FP16 matmul timed.

Use the frozen runtime's existing dequantization primitive and torch matmul path.
No new backend.

For each:
- output numerical validation;
- 3 warmups;
- 9 native timing samples;
- kernel fingerprint.

If implementation work fails, produce ENGINEERING_ATTEMPT_RECEIPT and continue.

Suggested engineering timebox:
60 minutes.

## 5. M4/M5 — Materialize Q30 harness, do not skip because it does not pre-exist

Authority:
`ee67225edc8fc5868de585d38e0391cbeb755d9f`

Inspect exact frozen local source.

If expert loop is inline, implement a TEST-ONLY wrapper by copying/extracting the exact grouping/expert/routing-weight/combine semantics.

Use same:
- expert module objects;
- weights;
- precision;
- backend;
- residency.

Do not optimize or restructure.

Try at least:
1. direct call to existing internal expert function if available;
2. exact extracted inline expert-loop wrapper if not.

Natural N canary:
real gate/routes -> wrapper -> compare same-boundary output.

Only if N passes:
P -> inverse-permutation equivalence -> U-active.

Suggested engineering timebox before freezing E3:
up to 2 hours.

If unresolved, continue G1/G4/M2/M3.

## 6. G1 — Materialize input authority rather than skip

Existing Qwen2.5-0.5B asset only.

### B4/T2048/D32

If only one accepted 2048-token S2 sequence exists:
replicate it across batch only as:

`CONTROLLED_BATCH_REPLICATION_DIAGNOSTIC`

Do not call it natural workload diversity.

This is authorized for batch-resource scaling.

### B1/T8192/D32

Priority:
1. use an existing local accepted long-text/token asset if available;
2. otherwise concatenate available distinct local accepted text sources deterministically;
3. if no such inputs exist, deterministic repetition may be used only as:
   `CONTROLLED_SYNTHETIC_LONG_CONTEXT_DIAGNOSTIC`

Never call repeated context natural.

Freeze token/text SHA and scenario ID before timing.

Measure native phase timing + lightweight census.

Input authority absence is engineering work, not an immediate skip.

Suggested timebox:
60 minutes.

## 7. G4 — Materialize Llama activation authority rather than skip

Existing:
`Llama3.2-1B @ 4e20de362430cd3b72f300e6b0f18e50e7166e08`

No download.

Use:
- an existing accepted Llama scenario/input if present;
- otherwise recover the accepted S2 source TEXT and tokenize it with the frozen Llama tokenizer.

Do not reuse Qwen token IDs directly across tokenizers.

Freeze:
- source text SHA;
- tokenizer identity;
- Llama token SHA;
- q_proj/down_proj live activation pools.

Then run raw M1/M256 for at most q_proj/down_proj.

Claim:
`RAW_CROSS_MODEL_SHAPE_HOLDOUT`.

Suggested timebox:
60 minutes.

## 8. G3

If M2 profiling works, run one bounded profiler protocol sensitivity test with same target/metrics.

No cache-control = TLB-flush claim.

## 9. M9 optional detailed capture

Candidate remains:
`AWQ down_proj M1023 vs M1024`

Only if:
- exact selector stable;
- M2/M3 show detailed trace adds value;
- >=3h remain before NO_NEW cutoff;
- projected raw <=16 GiB.

Otherwise mark skipped with reason.

## 10. Scheduler behavior

After every task:
- update PIPELINE_STATE;
- select next READY task.

A task-local stop must not end the campaign.

Before emitting final COMPLETE marker, run a scheduler audit.

Final COMPLETE is INVALID if:
- current time < NO_NEW_GPU_SCIENCE_AFTER;
- any authorized task is marked SKIPPED solely because an engineering artifact was absent;
- no ENGINEERING_ATTEMPT_RECEIPT exists for unresolved engineering gates;
- another READY task exists.

## 11. Closeout

At NO_NEW_GPU:
no new GPU science.

Finish safely closable work, transfer, hash, analyze, node164 ACK, report, commit/push, remote verify, clean, release lock.

Report:
`docs/vm_tlb/codex_handoff/awma/UNATTENDED_E1_E3_20H_109_V3R1_REPORT.md`

Review pack:
`docs/vm_tlb/review_packs/AWMA_109_20H_UNATTENDED_E1_E3_V3R1/`

Include:
- RESUME_TIME_AUTHORITY.json
- PIPELINE_STATE.json
- ENGINEERING_ATTEMPT_RECEIPTS.json
- M2/M3/E3/G1/G4 outputs or explicit bounded-failure receipts
- RUN_RECEIPTS.json
- RAW_DATA_INDEX.tsv
- SHA256SUMS

Success marker:
`AWMA_109_20H_UNATTENDED_E1_E3_CHARACTERIZATION_V3R1_COMPLETE_WITH_SCOPE`
