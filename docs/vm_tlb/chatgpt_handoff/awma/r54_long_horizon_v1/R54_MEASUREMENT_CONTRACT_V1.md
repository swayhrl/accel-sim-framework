# R54 Exact Recurrent Checkpoint Measurement Contract V1

## A. Execution identity

Stage:
`AWMA_R54_EXACT_RECURRENT_CHECKPOINT_LIFECYCLE_V1`

Node:
109 / RTX4080 / SM89.

Formal GPU lock:
`/data/c16/locks/c16_gpu_campaign.lock`

Only model:
`Qwen/Qwen3.5-0.8B@c6046cd1f7e2763bf1abf5a5aef6ad7878e10ccb`

No node174, Accel-Sim, NVBit full trace, driver change, offload or second model.

## B. Environment and fast-path gate

Create an isolated runtime environment and record:
- Python;
- torch/CUDA;
- transformers;
- causal-conv1d;
- FLA or actual recurrent-kernel package;
- compiler/toolchain;
- driver/GPU;
- all package versions and hashes.

Run one bounded source/runtime audit of a short text prefill and decode.

The GDN path must dispatch to a credible optimized CUDA implementation. Record exact NSYS function/kernel identities for:
- at least one GDN prefill/update kernel;
- at least one full-attention kernel;
- model-level launch strata.

Two bounded dependency/build repairs maximum.

If only an obvious slow PyTorch/reference recurrent path remains:
`R54_RUNTIME_FASTPATH_NOT_QUALIFIED_V1`.

## C. Prefix fixture construction

Read accepted R53 `REQUEST_SELECTION.tsv`.

Use exact raw prompts in frozen order:
1. GSM8K DISCOVERY rank 0,1,2,3
2. GSM8K HOLDOUT rank 4,5,6,7
3. HumanEval DISCOVERY rank 0,1,2,3
4. HumanEval HOLDOUT rank 4,5,6,7

Join adjacent prompts with:
`\n\n---\n\n`

Repeat the 16-prompt list cyclically.

Tokenize with the pinned Qwen3.5 tokenizer:
- add_special_tokens = false;
- no chat template.

Freeze:
- `PREFIX_DISCOVERY_4096`: tokens [0:4096]
- `PREFIX_HOLDOUT_2048`: tokens [0:2048]
- `SUFFIX_A_512`: tokens [4096:4608]
- `SUFFIX_B_512`: tokenize a second cyclic text stream with the 16-prompt list left-rotated by 5; take [0:512]
- `HOLDOUT_SUFFIX_256`: tokens [2048:2304]

Hash all raw sources, combined text, tokenizer identity and token IDs.

## D. Exact state schema

After a qualified prefix canary, enumerate the actual runtime cache/state object.

For every layer/field emit:
- layer index
- layer type
- field name/path
- tensor shape
- dtype
- device
- logical bytes
- storage bytes if different
- mutable/in-place flag
- exact continuation required YES/NO/UNKNOWN
- state class:
  - FULL_ATTN_K
  - FULL_ATTN_V
  - GDN_CONV
  - GDN_RECURRENT
  - POSITION_OR_LENGTH
  - INIT_FLAG
  - OTHER
- snapshot inclusion
- evidence/source anchor

Create:
`R54_EXACT_STATE_SCHEMA.tsv`.

Recurrent checkpoint = every exact-continuation GDN recurrent/conv tensor plus required recurrent metadata.

Full-attention KV is kept as the ordinary token-addressable prefix cache and is not duplicated into every recurrent checkpoint.

If exact state ownership cannot be determined after source audit and two bounded instrumentation attempts:
`R54_STATE_AUTHORITY_NOT_QUALIFIED_V1`.

## E. Semantic contract

Define:
`R54_EXACT_CONTINUATION_SEMANTICS_V1`.

All checkpoint/restore paths must preserve:
- exact cache sequence length/position;
- GDN initialized/uninitialized flags;
- full-attention KV prefix identity;
- no NaN/Inf;
- exact greedy next-token ID at checkpoint canary;
- exact top-8 token-ID set;
- exact top1/top2 token ordering;
- exact generated token IDs for a fixed 16-token greedy continuation after restore.

Record numerical state/logit differences, but do not invent an absolute-error pass threshold.

Where the exact same copy path should be bitwise identical, require bitwise equality and fail closed if it is not.

## F. Prefix execution

Frozen model-prefill chunk:
`512 tokens`.

### M0_MONOLITHIC_IDENTITY

One-shot PREFIX_DISCOVERY_4096 if the runtime supports it.

Used for semantic/implementation reference only.

### P0_CHUNKED512_NO_CHECKPOINT

Eight 512-token chunks.
No recurrent checkpoint copy.

Primary checkpoint-production timing baseline.

P0 must satisfy the semantic contract relative to M0. If model/runtime arithmetic differs but discrete semantics match, retain the numerical difference and continue.

## G. Snapshot implementations

Frozen densities:
- D512: checkpoint after every 512-token chunk
- D2048: checkpoint after token 2048 and 4096

No other density.

Allocate all checkpoint buffers before timed regions.

### P1_SYNC_PREALLOC

At each checkpoint boundary:
- copy the exact recurrent checkpoint bundle to the preallocated slot;
- use D2D copies;
- no allocator/clone in the timed region;
- ensure snapshot complete before the next chunk updates source state.

### P2_ASYNC_LAYER_STAGGERED

Primary strong software arm.

Use:
- one dedicated CUDA snapshot stream;
- per-layer readiness events;
- preallocated checkpoint buffers;
- source-correct dependencies.

When a GDN layer finishes processing the checkpoint-boundary chunk:
1. record readiness on the compute stream;
2. snapshot stream waits for that event;
3. copy that layer's exact recurrent/conv state;
4. allow later model layers to continue on compute stream;
5. before the next chunk updates the same GDN layer, enforce completion of its checkpoint copy.

Do not overlap a copy with a mutation of its source state.

If model structure prevents layer-staggered overlap, use the strongest legal preallocated asynchronous boundary-copy implementation and record the dependency limitation.

Use comparable lightweight hook/wrapper infrastructure for P0/P1/P2 so Python hook overhead is not silently unique to P2.

## H. Snapshot production formal matrix

Discovery prefix:
PREFIX_DISCOVERY_4096.

Formal points:
1. P0
2. P1 D512
3. P2 D512
4. P1 D2048
5. P2 D2048

Each:
- one correctness/timeline canary;
- 2 warmups;
- 7 measured repetitions;
- paired/interleaved arm order where practical.

Primary interval:
first prefix-chunk GPU submission
to
both model prefix completion AND all required snapshot copies ready.

Also measure:
- model-compute-complete time;
- checkpoint-ready time;
- checkpoint bytes;
- total D2D copy GPU time;
- copy/compute overlap;
- snapshot orchestration host time;
- peak allocated/reserved memory.

One NSYS canary per arm.
No NCU yet.

## I. Production classification

For each P1/P2 density:

`overhead = (median(T_arm)-median(T_P0))/median(T_P0)`.

Stable material cost requires:
- overhead >=5%;
- effect >3x the larger relative run-to-run jitter/noise envelope;
- semantic contract passes.

Intermediate interpretations:

- P1 high, P2 <5% both densities:
  software overlap closes production cost.
- P2 <5% both densities:
  production lifecycle cost low for this scope.
- P2 >=5% stable:
  production residual exists, but do not promote until restore/holdout.

## J. Restore authority

Use the exact final token-4096 recurrent checkpoint produced by qualified P2.

Prepare an independent destination cache/state object with:
- correct full-attention KV for prefix4096 already resident;
- correct cache length/position metadata;
- preallocated GDN recurrent/conv destination storage.

The attention-KV prefix must not be regenerated inside the timed restore region.

No aliasing with a previous suffix run.

## K. Restore conditions

### R0_RESTORE_ONLY
Copy recurrent checkpoint bundle + required metadata into destination.
Measure direct restore latency/bytes.

### R1A_RESTORE_SUFFIX_A
Restore, then process SUFFIX_A_512.

### R1B_RESTORE_SUFFIX_B
Restore, then process SUFFIX_B_512.

### L1A_LIVE_SUFFIX_A
Start from an independently prepared live prefix4096 state; no timed restore; process SUFFIX_A_512.

### L1B_LIVE_SUFFIX_B
Same for suffix B.

### F1A_FULL_RECOMPUTE_SUFFIX_A
Compute prefix4096 from beginning, then suffix A.

### F1B_FULL_RECOMPUTE_SUFFIX_B
Compute prefix4096 from beginning, then suffix B.

The full recompute arms are amortization controls, not the restore-overhead denominator.

## L. Restore correctness

Before formal timing, for A and B:
- compare restored prefix-boundary greedy/top8/top1-top2;
- run a fixed 16 greedy decode tokens after suffix prefill;
- require exact generated token IDs;
- verify cache length/state schema;
- verify no cross-repetition contamination.

If failure persists after one surgical restore-implementation repair:
`R54_RESTORE_SEMANTICS_NOT_QUALIFIED_V1`.

## M. Restore timing

Each needed condition:
- 1 canary;
- 2 warmups;
- 7 repetitions.

Primary incremental restore cost:
`R1 - L1`.

Also report R0.

Restore is material only if:
- incremental restore >=5% of the measured prefix compute that reuse avoids;
- effect >3x jitter/noise;
- semantics pass.

Do not divide restore only by the short suffix and overstate the cost.

## N. Amortization

Using measured components only, derive N=1,2,4 suffix consumers.

No-cache:
`N × (prefix4096 + suffix)`.

Exact recurrent checkpoint reuse:
`prefix4096 materialization + selected checkpoint-production cost + N × (restore + suffix)`.

Use both:
- D512 storage/production
- D2048 storage/production

Report:
- measured terms;
- derived totals;
- break-even N;
- recurrent checkpoint bytes per boundary;
- total stored checkpoint bytes;
- attention-KV assumption.

No service-arrival claim.

## O. Conditional holdout

Only if qualified P2 production or restore has a stable >=5% residual.

Use:
- PREFIX_HOLDOUT_2048
- HOLDOUT_SUFFIX_256.

Select density by frozen rule:
larger qualified P2 production residual; tie -> D512.

Run only:
- P0
- P2 selected density
- restore+holdout suffix
- required live/recompute controls

Same semantic/materiality gates.

No tuning on holdout.

## P. Conditional NCU

Only if residual survives holdout.

Maximum 2 standalone profiles.

Pre-register metrics before collection.

Purpose:
- memory traffic;
- copy/memory engine behavior where visible;
- SM occupancy only if snapshot uses SM kernels;
- distinguish GPU-local copy cost from host orchestration.

No NCU replay timing as primary latency.

## Q. R55 side audit

No GPU timing.

Read and compare:
- Transformer Engine NVFP4 rowwise/columnwise storage and scales;
- Stable FP4 Training via Transposition-Invariant Block Quantization;
- NVIDIA NVFP4 pretraining;
- Quartet II;
- MOSS.

Output:
`R55_PLATFORM_AND_CLOSEST_WORK_AUDIT.md`.

No hardware claim from RTX4080 FP4 emulation.

## R. Final R54 states

Choose exactly one:

- R54_RUNTIME_FASTPATH_NOT_QUALIFIED_V1
- R54_STATE_AUTHORITY_NOT_QUALIFIED_V1
- R54_RESTORE_SEMANTICS_NOT_QUALIFIED_V1
- R54_SNAPSHOT_LIFECYCLE_COST_LOW_V1
- R54_SOFTWARE_BASELINE_SUFFICIENT_V1
- R54_HOST_RUNTIME_COST_NOT_ARCH_LOCALIZED_V1
- R54_RESIDUAL_READY_FOR_ARCH_REVIEW_V1

READY_FOR_ARCH_REVIEW requires:
- optimized real runtime;
- exact state schema;
- semantic restore;
- strong P2;
- stable >=5% GPU-local residual;
- holdout;
- not allocator/Python/host dominated;
- closest-work differentiation.
