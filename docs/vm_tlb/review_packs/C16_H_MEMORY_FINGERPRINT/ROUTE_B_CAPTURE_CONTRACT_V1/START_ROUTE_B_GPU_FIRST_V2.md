# START — Route B GPU-first V2

Use Goal mode.

Read, without checking out or merging the H branch into the active G worktree:

- `docs/vm_tlb/review_packs/C16_H_MEMORY_FINGERPRINT/ROUTE_B_CAPTURE_CONTRACT_V1/ROUTE_B_GPU_EXECUTION_HANDOFF_V2.md`
- `ROUTE_A_LIMITATION_AUDIT.md`
- `ROUTE_B_TRACE_SCHEMA.md`
- `ROUTE_B_CANARY_ACCEPTANCE.md`
- `ROUTE_C_COVERAGE_VALIDATION_PLAN.md`

Methodology branch minimum:
`hrl/vm-c16-h-memory-fingerprint-v0@0901c0c48ab77c7a9c357d50995eb13fa8fa1d44`

Active execution authority remains:
`hrl/vm-c16-g-retry570-v0`

Do not reset/merge the active G worktree to H. Fetch/read H with `git show` only.

## Goal

Maximize useful RTX3090 GPU-dependent evidence before rental ends, while upgrading memory traces from Route A's single-PC evidence to representative-kernel all-GLOBAL-MREF traces suitable for memory/TLB/cache fingerprint analysis and later replay-sensitivity work.

## Immediate actions

1. Fetch current G and H heads and record them.
2. Continue any currently GPU-ready G work immediately; do not leave the GPU idle for H-side CPU work.
3. In parallel, adapt/use the proven Recovery-V3 campaign-scoped G1 parent path to run exact Llama-3.2-1B S0/B1/T128/Decode4 G1 on RTX3090.
4. Export/validate the S0 catalog and freeze Route B V2 representative selection before address tracing.
5. Selection must be pre-outcome and use the union of:
   - >=70% phase duration-mass prefix;
   - >=80% static memory-opportunity proxy prefix using launch count × CTA count × warps/CTA × static GLOBAL-MREF count;
   - actually observed semantic-class diversity anchors.
6. Build a new NVBit 1.7.5 Route B memory-event producer; do not misuse the single-record targeted-memory tool.
7. Producer must support exact full-mangled function + code-object SHA + map SHA + sorted static-index whitelist, all active-lane GPU VAs, masks, access kind, width, CTA/warp identity, static index, MREF ordinal, observed event sequence, zero-drop/overflow terminal closeout.
8. Run Q0 CPU/parser fixture, Q1 tiny CUDA memory fixture, Q2 Llama one-index bridge qualification.
9. After Q0/Q1/Q2 PASS, run one bounded Llama Route B canary, then formal deterministic partitions under <=4GiB and <=20min/window.
10. If GPU time remains, collect bounded Route C Llama phase reference and Qwen0 S3 exploratory Route B data using its lawful campaign G1 catalog.

## GPU-first scheduling

Remote SHA + manifest closure is enough to continue GPU work. Copyback is deferred unless storage safety requires it.

If `GPU_READY_QUEUE_COUNT > 0` and `GPU_ACTIVE_JOB=none` for >120s, treat it as a scheduling error unless there is a real measurement/process/identity/storage gate.

Do not let any of the following block a ready GPU job:

- markdown/publication
- Git status cleanup
- local copyback
- bulk SHA of already-staged model packages
- CPU-only audit
- parser formatting

## Scientific prohibitions

Do not:

- reuse S1/S2 catalog rows to select Llama S0 kernels;
- reuse static indices/maps across model, scenario, GPU, or code object;
- select kernels/partitions based on observed addresses/locality/TLB/cache results;
- claim Route B represents a whole phase without Route C coverage evidence;
- call observed callback sequence hardware global order;
- delete the sole remote raw copy before local size+SHA closure;
- write to the historical ledger.

## Checkpoint reporting

After each independently reviewable milestone, commit+push compact evidence and report:

`CHECKPOINT_COMMIT=`
`GPU_ACTIVE_JOB=`
`GPU_READY_QUEUE_COUNT=`
`NEXT_GPU_JOB=`
`LLAMA_S0_G1_STATUS=`
`ROUTE_B_SELECTED_KERNEL_COUNT=`
`ROUTE_B_PRODUCER_STATUS=`
`ROUTE_B_CANARY_STATUS=`
`ROUTE_B_FORMAL_PARTITIONS_COMPLETE=`
`ROUTE_C_STATUS=`
`REMOTE_SHA_CLOSED_COPYBACK_DEFERRED_COUNT=`
`REMOTE_DATA_FREE_BYTES=`

Solve ordinary engineering failures rather than stopping for review. Stop only on a true scientific/identity/resource gate, preserve evidence, and continue independent GPU-ready work.
