# Continue 109 — Model-Derived AI UVM Characterization V1

Date: 2026-09-26

Stage:
`AWMA_AI_UVM_MODEL_DERIVED_CHARACTERIZATION_V1`

Execution branch:
`hrl/awma-ai-uvm-model-derived-characterization-v1`

Node:
109 / RTX4080

## 0. Starting authority

Accepted pilot:
- branch `hrl/awma-ai-uvm-oversubscription-feasibility-pilot-v1`
- commit `368b7043c70c1274f29153b5d5a665d1742aeacb`
- status `READY_FOR_AI_UVM_CHARACTERIZATION_V1`

Accepted pilot observations:
- P1/P2 whole-pool/growing-prefix patterns cross into repeated migration under
  oversubscription;
- P3 sparse expert rotation keeps the immediate repeat resident-fast;
- migration memcpy telemetry is available and step-correlatable;
- dedicated GPU/CPU page-fault counters are unavailable;
- the synthetic patterns are not real-model evidence.

Important correction:
P3 R2/R3 total DtoH is about 2 MiB, but it is not large eviction traffic.
The exported migration-cause breakdown is coherence/prefetch dominated and
contains no P1/P2-like eviction volume. Preserve that distinction.

No UVM mechanism is authorized by this Goal.

## 1. Goal

Replace the synthetic access laws with model-derived sizes, tensor structure,
and routing where possible, and determine whether the qualitative UVM behavior
survives.

Questions:
1. Does a real dense-model parameter layout still behave like full-weight
   repeated streaming under memory pressure?
2. Does an exact model-derived KV layout exhibit a sharp residency/migration
   transition as active context/concurrency grows?
3. Does real MoE routing temporal locality preserve a sparse-residency
   advantage, and under what expert-pool pressure does that advantage break?

This is characterization, not a new offloading policy.

## 2. Safety

Retain pilot GPU lock and memory safety contract:
`/data/c16/locks/c16_gpu_campaign.lock`.

- no allocation >20 GiB;
- no allocation >1.30x physical VRAM;
- host MemAvailable >= requested managed allocation + 8 GiB;
- driver Xid/reset/OOM -> immediate STOP;
- cleanup and memory recovery receipt after every scenario.

Do not download model assets.

## 3. Model-asset metadata audit — offline first

Audit already-present local/node164 assets without loading full models.

Candidate sources, in priority order where actually present:

### Dense weights
Prefer an already-finalized dense model whose BF16/FP16 parameter footprint is
near or above RTX4080 capacity, e.g. an existing Gemma-3-12B-class asset.
Fallback to another already-present dense asset.

### KV configuration
Use the already-qualified Llama-3.2-1B model/revision from Native Atlas unless
a larger already-present dense model has cleaner fully specified attention
metadata.

### MoE
Prefer an already-present MoE model with:
- exact expert tensor metadata;
- runnable routing path on 109;
- preferably total model state near/above VRAM.

Audit OLMoE first because it is already runnable and accepted.
Audit an already-present larger MoE (e.g. DeepSeek-V2-Lite lineage) only if its
asset/runtime is already available; no download/repair campaign.

Produce:
`MODEL_ASSET_METADATA.tsv`

For every tensor group record:
- model/revision;
- tensor names/pattern;
- shapes/dtypes;
- byte count;
- layer/expert identity;
- total parameter bytes;
- expert-pool bytes;
- non-expert bytes;
- source file/hash provenance.

Do not infer runtime access frequency from file order alone.

## 4. Freeze three model-derived replay contracts before UVM results

Create:
`MODEL_DERIVED_PATTERN_PREREG.tsv`

### D1 DENSE_PARAMETER_STREAM_REPLAY
Use exact tensor byte sizes and layer/tensor ordering from one selected dense
model.

Access law:
- one decode-like step reads every selected weight tensor exactly once in
  frozen layer order;
- repeat 3 steps;
- preserve tensor boundaries;
- use deterministic coalesced reads and checksums.

If the full model exceeds the 20 GiB safety cap:
select a deterministic prefix of complete layers/tensors whose total is the
largest <=20 GiB and record the omitted fraction.
Do not resize individual tensors.

This is a parameter-layout replay, not actual GEMM execution.

### D2 KV_LAYOUT_GROWTH_REPLAY
Derive exact KV element layout from a real model config:
- layers;
- KV heads;
- head dimension;
- dtype bytes;
- K and V;
- token/block layout supported by the config/runtime.

Compute exact bytes/token/sequence.

Choose exactly THREE preregistered concurrency/context points:
- one clearly resident;
- one near capacity;
- one mildly oversubscribed,
subject to the same 20 GiB cap.

Vary one scientific variable at a time:
prefer fixed context with increasing concurrent sequences OR fixed concurrency
with increasing context. Select before runs based on feasibility, and document
why.

Each step appends the exact model-derived per-token KV bytes and accesses the
frozen active KV pattern. If an exact attention read law cannot be reproduced
without framework integration, use an explicitly defined sequential/block
replay and label it `LAYOUT_EXACT_ACCESS_APPROXIMATE`.

### D3 REAL_ROUTE_EXPERT_REPLAY
Obtain an actual expert route sequence from an already-runnable MoE inference.

Preferred:
- reuse an existing exact expert-ID trace if one is already authoritative;
- otherwise add ONE read-only routing capture to the accepted OLMoE scenario
  (or selected larger MoE scenario), recording token/layer/top-k expert IDs.

Freeze:
- route trace SHA;
- expert tensor sizes;
- layer count;
- top-k;
- expert-pool structure.

Replay exact selected-expert regions in the recorded temporal order.

If total model state is resident:
include the real non-expert/model-state footprint as a fixed managed resident
pressure allocation when source-supported by metadata so the experiment
reflects the model's total memory demand.
Do NOT add arbitrary pressure solely to force thrashing.

If the real selected model cannot cross memory pressure under the 20 GiB cap,
retain it as a resident control rather than scaling expert size artificially.

## 5. Routing characterization before UVM policy comparison

For D3 calculate:
- expert selection frequency;
- per-layer route entropy;
- expert reuse-distance distribution in token/layer events;
- working-set experts in fixed windows;
- fraction of consecutive steps reusing at least one expert;
- hot-expert concentration;
- exact bytes touched per route step.

No claim that these metrics imply optimal caching.

Create:
`REAL_ROUTING_BEHAVIOR.tsv`.

## 6. Minimal matrix

Do not repeat the pilot's 4-ratio sweep.

For each D1/D2/D3 use only the preregistered natural/model-derived points.

Modes:

### M0 DEMAND
Normal UVM demand migration.

### M1 CURRENT-STEP_PREFETCH_CONTROL — only where semantically valid
This is a known control, not a mechanism.

- D1: optional next-tensor prefetch only if tensor order is already known
  online by the replay; label as deterministic replay control.
- D2: prefetch only the newly appended KV region, not the whole future KV.
- D3: after the router output is known for the current step, prefetch only the
  selected experts required by that step.

Do not prefetch future route decisions.

If a control changes total work or has no clean source semantics, mark N/A.

For every applicable point:
- 1 cold run;
- 1 immediate repeat;
- no extra repetitions.

## 7. Metrics

Reuse pilot telemetry:
- CUDA-event time;
- wall time;
- per-step time;
- HtoD migration bytes/count/time;
- DtoH bytes/count/time split by migration cause;
- user-prefetch bytes/events;
- working-set bytes;
- allocation/residency receipts;
- checksum.

Keep:
GPU/CPU page-fault counters = UNAVAILABLE unless tool capability actually
changes and is re-audited.

Never infer:
- TLB miss rate;
- PPN continuity;
- migration page size;
- shootdown count.

## 8. Synthetic-to-model-derived comparison

Build:
`SYNTHETIC_VS_MODEL_DERIVED.tsv`

Compare qualitative hypotheses, not raw runtimes:

### H1 Dense
Full repeated parameter use under memory pressure causes recurring
eviction/remigration rather than one-time cold placement.

### H2 KV
A monotonically growing model-derived KV active set has a measurable transition
where repeat/late-step migration rises sharply near/exceeding residency.

### H3 MoE
Sparse real routing touches a smaller temporal expert working set than the
entire expert pool and can keep repeat migration low while that temporal set
fits.

For every hypothesis classify:
- `SUPPORTED_MODEL_DERIVED`
- `PARTIAL`
- `NOT_SUPPORTED`
- `NOT_TESTABLE`.

Do not call H3 novel: sparse expert activation is a known MoE property.

## 9. One bounded real PyTorch managed-tensor bridge attempt

Now that the standalone UVM platform is qualified, make ONE bounded engineering
attempt to create a CUDA Managed Memory-backed PyTorch tensor without replacing
the global allocator.

Permitted approach:
- a small CUDA/C++ extension using `cudaMallocManaged`;
- wrap the allocation in a CUDA-device tensor/storage with a custom deleter
  only if PyTorch APIs support it safely;
- validate simple read/write and one representative CUDA op;
- verify pointer/device attributes and cleanup.

Do not patch PyTorch globally.
Do not replace the CUDA caching allocator.
Do not spend the Goal debugging unsupported framework internals.

If this small bridge works:
run ONE representative tensor-level experiment:
- dense GEMV/linear weight tensor OR
- one expert weight tensor,
chosen before performance based on easiest semantic closure.

Record:
`MANAGED_TORCH_TENSOR_BRIDGE_PASS`.

If not:
`MANAGED_TORCH_TENSOR_BRIDGE_NOT_READY`.
This does not invalidate the replay characterization.

## 10. Closest-work screen before any research claim

Explicitly compare the observed behavior to:
- generic GPU UVM oversubscription characterization;
- UVM batching/eviction/migration work;
- explicit LLM KV offload/tiering;
- MoE expert offloading/prefetching.

Important known boundaries:
- ES-MoE (ICML 2024) already offloads expert parameters and overlaps
  CPU-GPU transfer with expert compute;
- recent MoE inference systems already exploit sparse expert activation and
  expert prefetch/offload;
- KV cache multi-tier/offload is an active systems area.

Therefore, "dense thrashes, sparse experts do not" is NOT sufficient novelty.

The potentially interesting research gap, if evidence supports it, must be
more specific, e.g.:
- unmanaged UVM migration decisions systematically mismatch real route reuse
  even when explicit current-step routing information is available;
- a repeatable phase transition tied to real KV growth that generic
  allocation-ratio policies do not capture;
- interaction between real model-state layout and migration granularity.

Do not invent a gap when closest work already covers it.

## 11. No mechanism in this Goal

This Goal produces characterization and at most TWO formal problem cards.

A problem card requires:
1. real/model-derived evidence;
2. a reproducible event-level phenomenon;
3. a closest-work limitation;
4. a measurable future real-model path;
5. no dependence on unavailable fault/TLB telemetry.

No UVM policy prototype is authorized yet.

## 12. Final decision

Exactly one:

- `MODEL_DERIVED_UVM_NO_DISTINCT_PROBLEM`
- `MODEL_DERIVED_UVM_CHARACTERIZATION_SUPPORTED`
- `AI_UVM_PROBLEM_IDENTIFIED_READY_FOR_FORMAL_DEVELOPMENT`

The third status requires a differentiated problem card; it does NOT authorize
a mechanism automatically.

## 13. Durable authority

Node164 root:
`/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/uvm_model_derived_characterization_20260926/`

Store:
- model metadata/index hashes;
- routing trace;
- replay contracts/source/binaries;
- raw NSYS;
- exported event tables;
- run receipts;
- bridge receipts;
- SHA256SUMS.

## 14. Deliverables

- README.md
- MODEL_ASSET_METADATA.tsv
- MODEL_DERIVED_PATTERN_PREREG.tsv
- REAL_ROUTING_BEHAVIOR.tsv
- MODEL_DERIVED_RUN_MATRIX.tsv
- MODEL_DERIVED_UVM_EVENTS.tsv
- MODEL_DERIVED_STEP_BEHAVIOR.tsv
- SYNTHETIC_VS_MODEL_DERIVED.tsv
- MANAGED_TORCH_BRIDGE_STATUS.md
- CLOSEST_WORK_SCREEN.md
- PROBLEM_CARD_1.md / PROBLEM_CARD_2.md if justified
- FINAL_DECISION.md
- RAW_DATA_INDEX.tsv
- SHA256SUMS
- REPORT.md

Commit/push/fetch-back/remote HEAD+tree/hash/clean and STOP.
