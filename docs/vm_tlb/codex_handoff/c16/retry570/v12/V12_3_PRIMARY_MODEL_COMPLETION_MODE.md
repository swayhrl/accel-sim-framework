# C16 Recovery-V3 V12.3 — Primary-Model Completion Mode

## Decision

Stop broad horizontal expansion. The primary objective is now to finish one model end-to-end before expanding the next model.

```text
PRIMARY_MODEL = meta-llama/Llama-3.2-1B
PRIMARY_SCENARIO = S0 / B1 / T128 / Decode4
PRIMARY_GPU = rented RTX3090 / SM86
```

Other models are fallback-only until Llama reaches `MODEL_TRACE_COMPLETE`.

## Current reviewed authority

Active scientific branch:

```text
hrl/vm-c16-g-retry570-v0
reviewed HEAD = 6b32ddd7a7670ae8b2caab0d3125309c8aac3ff8
```

Clean Q1 integration directly based on the reviewed active HEAD:

```text
hrl/vm-c16-g-routeb-q1-integration-local-v0
Q1 integration commit = ac36cbdcfaee44354a42ed952b010dcc7070475a
```

Q2 preparation branch:

```text
hrl/vm-c16-g-routeb-q1-integration-v0
Q2 preparation commit = 606a8d6414236362cf1b6e751956f6d794db9704
```

Q1 is GPU-ready. Q2 preparation exists. Llama V2 map status remains 34/36 exact maps with two CUTLASS owner gaps; those gaps block final representative selection but MUST NOT block Q1/Q2 producer qualification.

## Completion definition

Do not declare Llama complete until the following are closed:

1. exact S0 native/G1 census — already complete;
2. Route-B Q1 tiny-CUDA dynamic producer qualification;
3. Route-B Q2 Llama bridge for both Prefill and Decode using all mapped `GLOBAL && has_mref` rows of the exact anchor functions;
4. required CUTLASS owner closure, or an explicitly revised scientifically justified coverage contract approved after evidence review;
5. final representative-kernel selection frozen from pre-outcome evidence;
6. bounded Route-B canary on selected representative kernels;
7. formal Route-B dynamic address capture for Prefill and Decode, partitioned if needed;
8. Route-C phase coverage reference sufficient to quantify representative-kernel coverage;
9. remote SHA/manifest closure for every retained GPU artifact;
10. compact model-level closeout receipt stating what is complete, what is excluded, and why.

Only then set:

```text
MODEL_TRACE_COMPLETE = LLAMA_3P2_1B_S0_ROUTE_B_ROUTE_C_COMPLETE
```

Local copyback is NOT required before `MODEL_TRACE_COMPLETE` if every remote artifact has size/SHA/manifest closure and sufficient remote free space remains.

## Scheduling law

While `PRIMARY_MODEL=Llama-3.2-1B`:

```text
if Llama GPU-ready work exists:
    run Llama immediately
elif Llama CPU-blocked and expected unblock <=120s:
    wait only for that bounded unblock
elif Llama CPU-blocked >120s and an already-frozen fallback GPU row exists:
    run exactly one fallback row
    return immediately to Llama when it becomes ready
else:
    continue bounded Llama engineering work; do not open a new model campaign
```

No new model expansion merely to keep dashboards busy.

## GPU priority chain

Current chain:

```text
Q1 tiny CUDA
  -> Q2 Llama Prefill bridge
  -> Q2 Llama Decode bridge
  -> CUTLASS owner closure if still needed
  -> final representative selection
  -> Route-B canary
  -> Route-B formal partitions
  -> Route-C coverage capture
  -> Llama model closeout
```

Q1/Q2 must not wait for final representative selection.

## Branch ownership

Lane A remains the only GPU/scientific active-branch owner.

Lane C is CPU/code support only. It may prepare minimal commits but must never run GPU work or mutate Lane A's active worktree.

Lane B is storage/copyback only. It must not hold the remote I/O exclusion lock while idle.

Lane D is paused except when Lane A explicitly requests one already-frozen fallback row or missing authority needed to finish Llama.

## No broad merge

Do not merge divergent Route-B development branches wholesale.

Use minimal integration commits based directly on the latest active scientific HEAD. Q1 already has such a commit (`ac36cbd...`). Q2 must be rebased/recreated as a minimal direct child of the post-Q1 active HEAD before execution.

## GPU-idle rule

If a legal Llama GPU job is ready and GPU is idle for >120 seconds, classify as a scheduling error.

CPU work that is not a scientific gate does not justify GPU idle:

- markdown/status updates;
- publication cleanup;
- copyback/local SHA;
- unrelated model preparation;
- long remote package SHA;
- broad refactors.

## Evidence rules

Never weaken:

- exact model/revision/input/scenario identity;
- actual code-object owner closure;
- exact function identity;
- `(static_index,mref_ordinal)` whitelist identity;
- predicate-aware executing-lane semantics;
- overflow/drop fail-close;
- bounded <=4 GiB and <=20 min capture windows;
- no blind target scans;
- no cross-model/static-index reuse;
- no fake coverage denominator shrinkage.

## Checkpoint cadence

Checkpoint immediately after each of:

```text
Q1 PASS/FAIL
Q2 Prefill PASS/FAIL
Q2 Decode PASS/FAIL
CUTLASS owner disposition
final selection freeze
Route-B canary
formal partition completion
Route-C completion
Llama MODEL_TRACE_COMPLETE
```

Each checkpoint must report:

```text
CHECKPOINT_COMMIT=
PRIMARY_MODEL=
PRIMARY_STAGE=
GPU_ACTIVE_JOB=
NEXT_GPU_JOB=
GPU_IDLE_SECONDS=
REMOTE_DATA_FREE_BYTES=
DYNAMIC_ADDRESS_TRACE_AVAILABLE=
REMOTE_SHA_CLOSED=
BLOCKER_IF_ANY=
```
