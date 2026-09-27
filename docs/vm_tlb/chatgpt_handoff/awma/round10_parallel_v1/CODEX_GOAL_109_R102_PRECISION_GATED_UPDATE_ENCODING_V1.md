# CODEX GOAL — AWMA R102 Precision-Gated Update Encoding V1

## Mission

Execute a source- and input-authority-gated exploration:

`AWMA_R102_PRECISION_GATED_UPDATE_ENCODING_V1`

Scientific question:

> When a real training update is projected into the exact low-precision model representation that must be synchronized, can the changed-element indices and values be discovered/compacted efficiently enough in software, or does a material GPU-local encoding residual remain?

This is not a generic sparse-mask microbenchmark and not a multi-GPU network experiment.

Repository:
`swayhrl/accel-sim-framework`

Coordination branch:
`hrl/awma-round10-parallel-exploration-handoff-v1`

Execution branch:
`hrl/awma-r102-precision-gated-update-encoding-v1`

Accepted base:
`d6ef29505de75985181afc74dffc3cf1b652afc2`

Literature:
`hrl/awma-chatgpt-literature-notes-v1 @ 1dcf2cc9e4409010ec7f49d8afbefe0194ba0a8f`

Read:
- `docs/vm_tlb/chatgpt_handoff/awma/round10_parallel_v1/START_HERE.md`
- `docs/vm_tlb/literature_notes/awma/rounds/2026-09-27_ROUND_10_HORIZONTAL_REVIEW_AND_NEXT.md`

Node109 is allowed, but GPU execution is forbidden until the input-authority gate passes.

Every CUDA operation must hold:
`/data/c16/locks/c16_gpu_campaign.lock`.

No node174 or Accel-Sim.

---

# 1. Pin the published SparseRL-Sync software authority

Fetch exactly:

- repo: `scitix/helix`
- commit: `867f76a82822dd87413da4fec617b7f8e7cf6414`

Hash/read at minimum:

- `sparse_update/common/compare.py`
- `sparse_update/common/convert.py`
- `sparse_update/megatron/updater.py`
- `sparse_update/megatron/gather_indices.py`
- `sparse_update/slime/sparse_bucket.py`
- statistics/offline input-format code required to understand dumps.

Verify the current reference path rather than assuming it:

- previous low-precision model weight is retained;
- change mask uses exact low-precision `curr != prev`;
- changed indices are found via `nonzero`;
- indices become int32;
- changed values are gathered;
- per-tensor sparse items are merged/bucketed;
- source contains the explicit Triton-implementation TODO if still present.

Create:
`R102_SOURCE_RECEIPT.json`.

Do not call this reference path a hardware limitation.

---

# 2. Input-authority gate — highest priority

A real before/after low-precision update authority is mandatory for scientific GPU timing.

Search in this order:

## A. Existing local/node164 project assets

Search metadata/path names first, without expensive whole-storage hashing:

- existing C16/AWMA assets;
- prior training/RL artifacts;
- SparseRL/Helix dumps;
- before/after model weight snapshots;
- accepted update-statistics packages that retain actual tensors.

Do not modify or move accepted assets.

## B. Pinned Helix public artifact

Inspect:
- repository data paths;
- README;
- release/assets;
- scripts/configs;
- documented external dump locations.

A statistics CSV or list of NNZ counts is **not** enough.

Required scientific payload is at least one exact pair:

`PREV_LOW_PRECISION_WEIGHT`
`CURR_LOW_PRECISION_WEIGHT`

or a source training dump from which the pair is deterministically reconstructible.

The dtype must be the representation whose exact equality defines changed/not-changed payload semantics.

## Gate result

If no actual tensor authority exists:

final state:
`R102_INPUT_AUTHORITY_NOT_QUALIFIED_V1`

Then:
- complete source audit;
- document exactly what artifact is missing;
- do not create random sparse masks;
- do not use Bernoulli masks or fabricated 1% sparsity as AI evidence;
- do not run GPU timing;
- publish and STOP.

This is a valid successful outcome.

---

# 3. Bind the real update authority

If an actual before/after update exists, create:

`R102_INPUT_AUTHORITY_RECEIPT.json`

Record:

- model/training source;
- step/update identity;
- tensor names;
- original/master dtype if available;
- synchronized/deployment dtype;
- shapes;
- element counts;
- exact hashes;
- how before/after tensors were created;
- whether the source is RL, SFT, pretraining or other;
- whether the current low-precision weights are direct casts/copies from a higher-precision master;
- any DP/TP/EP sharding.

Do not label non-RL data as SparseRL workload.

If only a subset of parameters is available, report that scope exactly.

---

# 4. Freeze selected tensors before performance

Do not choose tensors based on favorable sparsity or latency.

Selection rule:

1. enumerate all qualified tensor pairs in canonical name order;
2. exclude only tensors with incompatible/non-floating representation, documenting them;
3. take the first three tensors with >=1M elements;
4. if fewer than three exist, use all qualified tensors with >=1M elements;
5. separately aggregate all remaining qualified tensors as an `ALL_AVAILABLE` stream when memory permits.

Freeze names/hashes before timing.

Record exact change fraction:

`rho = count(curr != prev) / numel`.

Raw sparse payload lower bound for BF16 value + int32 index:
`6 * nnz bytes`.

Dense BF16 payload:
`2 * numel bytes`.

This arithmetic is diagnostic only; include actual metadata/alignment later.

If every selected tensor has `rho >= 1/3`, sparse indices+BF16 values are not even smaller than dense payload before metadata.

Classify:
`R102_DENSE_OR_LOW_SPARSITY_NO_OPPORTUNITY_V1`

No compaction architecture claim.
A bounded software timing can be skipped.

---

# 5. Exact encoding semantics

Define:

`R102_EXACT_LOW_PRECISION_UPDATE_ENCODING_V1`

Reference output for each tensor:

- indices = every flattened position where `curr != prev`;
- values = exact `curr` values at those indices;
- unchanged positions absent.

Required reconstruction:

1. clone/copy `prev`;
2. assign encoded `values` at encoded `indices`;
3. reconstructed tensor must be bitwise equal to `curr`.

The order of sparse records is canonical:
ascending flattened index.

Do not relax this after seeing performance.

No approximation, thresholding or top-k update selection is allowed.

---

# 6. Software arms

All arms begin with both `prev` and `curr` tensors resident on the same GPU.

Snapshot ownership cost is reported separately.

## E0 — HELIX_REFERENCE_COMPARE_COMPACT

Faithfully reproduce the pinned source path:

`curr != prev -> nonzero -> int32 indices -> index_select values`

Include all kernels and temporary allocations in the timed encode region.

## E0_FULL — REFERENCE_LIFECYCLE

Separately account the pinned `before_copy` previous-weight clone plus E0.

Do not use E0_FULL as the only compaction baseline; it mixes snapshot ownership with encoding.

## E1 — BOUNDED_TRITON_COMPARE_COMPACT

Implement one strong software baseline preserving ascending indices.

Recommended structure:

1. blockwise exact compare and changed-count;
2. prefix offsets using a legal GPU scan/cumsum primitive;
3. blockwise fill of int32 indices and exact current values into preallocated output.

Requirements:
- no CPU round-trip in the timed path;
- preallocate outputs/workspace after NNZ canary;
- no per-element atomics that produce nondeterministic ordering unless a deterministic reorder is included in timing;
- exact reconstruction contract.

One correctness repair is allowed.
One second substantive implementation strategy is allowed only if the first strategy is structurally unsuitable, not merely slower.

Do not add a hardware-specific primitive.

---

# 7. Correctness canary

For every selected tensor/stream:

- E0 exact reconstruction PASS;
- E1 exact reconstruction PASS;
- E0/E1 NNZ equal;
- index set equal;
- values bitwise equal at each canonical index.

Record:
- change fraction;
- output bytes;
- temporary bytes;
- allocation behavior.

If the reference itself cannot be reproduced:
`R102_REFERENCE_ENCODING_NOT_QUALIFIED_V1`.

If E1 cannot be made exact after bounded repair:
record software candidate not qualified; do not call it a hardware opportunity.

---

# 8. Formal timing

Only after real input and correctness gates pass.

Per selected tensor and `ALL_AVAILABLE` if admitted:

- 1 canary;
- 2 warmups;
- 7 formal repetitions;
- paired/interleaved E0/E1;
- stable resident inputs;
- preallocated E1 workspace;
- no profiler during primary timing.

Measure:

- encoding GPU time;
- host elapsed;
- NNZ;
- encoded bytes;
- temp/workspace peak;
- kernel count.

Also measure a dense BF16 D2D copy of the same input byte size as a **local transfer control**, not a network baseline.

Material software improvement:
- E1 vs E0 >=5%;
- >3x larger jitter/noise envelope;
- exact semantics.

---

# 9. Conditional profiler

NCU/NSYS diagnostic is allowed only if:

- E1 remains a material encoding cost after optimization, or
- E0/E1 decomposition is unclear.

Maximum:
- one NSYS canary;
- two NCU profiles.

Pre-register metrics before collection.

Questions:
- compare/scan/compact memory traffic;
- local memory/register pressure;
- atomics/scans if present;
- whether host launch or GPU memory/compaction dominates.

Do not convert single-GPU D2D data into network speedup.

---

# 10. System relevance boundary

This Goal does not reproduce distributed SparseRL synchronization.

Use source/paper measurements only as attributed external context.

Do not claim end-to-end RL speedup from local encoder timing.

For architecture review readiness, all must hold:

1. real low-precision update authority;
2. encoded payload is materially smaller than dense;
3. exact E1 strong software baseline;
4. E1 still has stable material GPU-local cost;
5. that cost is localized to compare/scan/compaction rather than Python/allocator;
6. the cost is large enough relative to the published/accepted synchronization context to plausibly matter, with measured and externally reported terms clearly separated;
7. closest-work does not already provide the same capability.

If step 6 cannot be established:
use `R102_SYSTEM_CONTEXT_REQUIRED_V1`, not architecture-ready.

---

# 11. Final states

Choose exactly one:

- `R102_INPUT_AUTHORITY_NOT_QUALIFIED_V1`
- `R102_DENSE_OR_LOW_SPARSITY_NO_OPPORTUNITY_V1`
- `R102_REFERENCE_ENCODING_NOT_QUALIFIED_V1`
- `R102_SOFTWARE_CANDIDATE_NOT_QUALIFIED_V1`
- `R102_SOFTWARE_BASELINE_SUFFICIENT_V1`
- `R102_HOST_RUNTIME_COST_NOT_ARCH_LOCALIZED_V1`
- `R102_SYSTEM_CONTEXT_REQUIRED_V1`
- `R102_COMPACTION_RESIDUAL_READY_FOR_REVIEW_V1`

READY authorizes only later ChatGPT review.
Do not start node174.

---

# 12. Publication

Durable root:

`/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/r102_precision_gated_update_encoding_20260927/`

Review pack:

`docs/vm_tlb/review_packs/AWMA_R102_PRECISION_GATED_UPDATE_ENCODING_V1/`

Required minimum:
- README.md
- SOURCE_AND_CLOSEST_WORK_AUDIT.md
- INPUT_AUTHORITY_AUDIT.md
- optional R102_INPUT_AUTHORITY_RECEIPT.json
- PREREGISTRATION.json
- optional TENSOR_SELECTION.tsv
- optional CHANGE_SPARSITY.tsv
- optional SEMANTIC_RESULTS.tsv
- optional TIMING_RESULTS.tsv
- optional PROFILER_DIAGNOSTIC.tsv
- R102_DECISION.md
- FINAL_DECISION.md
- RAW_DATA_INDEX.tsv
- SHA256SUMS

If stopped at input authority, absent downstream files must be marked NOT_RUN in README/decision rather than fabricated empty science.

Closure:
`source/science -> node164 -> review pack -> hashes -> commit -> push -> fetch-back -> exact remote SHA/tree -> clean -> GPU released -> STOP`.

No auto merge.
