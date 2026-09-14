# START Lane A — Llama to Completion V12.3

You are the sole GPU/scientific execution owner.

Read first:

```text
docs/vm_tlb/codex_handoff/c16/retry570/v12/V12_3_PRIMARY_MODEL_COMPLETION_MODE.md
```

## P0 — Q1 now

Current reviewed active HEAD:

```text
6b32ddd7a7670ae8b2caab0d3125309c8aac3ff8
```

Current clean Q1 integration commit:

```text
ac36cbdcfaee44354a42ed952b010dcc7070475a
```

`ac36cbd...` is a one-commit direct descendant of reviewed active HEAD. Fast-forward the active scientific worktree to this commit after verifying the branch relation and clean worktree. Do not merge the broader producer branch.

Immediately execute the Q1 tiny-CUDA qualification from:

```text
docs/vm_tlb/review_packs/C16_H_MEMORY_FINGERPRINT/ROUTE_B_CAPTURE_CONTRACT_V1/ROUTE_B_Q1_INTEGRATION_READY.md
```

Q1 acceptance requires all of:

- exact Q1 kernel observed for two launches;
- direct GLOBAL load/store whitelisted;
- nontrivial predicate exercised;
- nonzero GPU VAs;
- explicit `(static_index,mref_ordinal)` identity;
- stream-global monotonic `OBSERVED_CALLBACK_ORDER` sequence;
- instance grouping by `(kernel_launch_id,warp_instruction_instance_id)`;
- exactly one COMPLETE terminal;
- overflow=0;
- drop=0;
- terminal event_count equals decoded LANE_EVENT count;
- actual JSONL bytes <=1 MiB;
- fixture checksum PASS.

On ordinary build/runtime/tool problems: diagnose, fix minimally, rerun smallest affected gate. Do not stop Goal.

## P1 — Q2 immediately after Q1 PASS

After Q1 PASS, do not wait for ChatGPT review.

Fetch Q2 preparation commit:

```text
606a8d6414236362cf1b6e751956f6d794db9704
```

Do not merge its branch wholesale. Recreate/cherry-pick only the minimal Q2 files onto the new post-Q1 active HEAD, resolve conflicts conservatively, rerun CPU tests, then execute GPU Q2.

Q2 anchors:

```text
PREFILL: indexSelectLargeIndex exact function
DECODE:  indexSelectSmallIndex exact function
```

For each anchor:

1. generate a fresh actual-owner V2 exact-function static map;
2. freeze ALL `GLOBAL && has_mref` rows and every MREF ordinal;
3. run dynamic LANE_EVENT capture with the qualified producer;
4. parse fail-closed;
5. compare structural Route-A bridge quantities without absolute-VA equality;
6. remote SHA/manifest close raw evidence.

Q2 Prefill and Decode are separate checkpoints.

## P2 — CUTLASS owner only after Q1/Q2

Two V2 exact functions remain owner-unresolved and block final selection. Continue bounded owner work only after Q1/Q2 unless Q2 itself needs that code.

The latest owner logic binds CUlibrary module ownership by the same actual library handle. Preserve this fail-closed rule.

Do not rerun identical owner probes indefinitely. Each retry must add new direct ownership evidence or a new bounded observer.

## P3 — final Llama Route-B

Once selection is admissible:

```text
final selection
-> bounded canary
-> formal Prefill partitions
-> formal Decode partitions
```

Capture all selected representative-kernel `GLOBAL && has_mref` events. Partition only deterministically by frozen static-index/MREF sets when volume requires it. Never partition by observed address/locality outcome.

## P4 — Route C and closeout

After Route B formal capture, run Route-C coverage reference sufficient to measure representative-kernel coverage of whole Prefill/Decode memory activity.

Then produce `MODEL_TRACE_COMPLETE` compact closeout.

## Fallback rule

Do not start or expand another model while Llama has legal GPU work.

Only if Llama is CPU-blocked >120s may you run exactly one already-frozen fallback GPU row. Return to Llama immediately when ready.

## Transfer

GPU artifacts require remote size/SHA/manifest closure only. Do not wait for copyback before next Llama GPU job while remote free space is safe.

## Report after every GPU boundary

```text
CHECKPOINT_COMMIT=
PRIMARY_MODEL=Llama-3.2-1B
PRIMARY_STAGE=
Q1_STATUS=
Q2_PREFILL_STATUS=
Q2_DECODE_STATUS=
ROUTEB_SELECTION_STATUS=
ROUTEB_FORMAL_STATUS=
ROUTEC_STATUS=
GPU_ACTIVE_JOB=
NEXT_GPU_JOB=
GPU_IDLE_SECONDS=
REMOTE_DATA_FREE_BYTES=
REMOTE_SHA_CLOSED=
BLOCKER_IF_ANY=
```
