# DRAFT — CODEX GOAL 109 20h Unattended Native/Experiment Pipeline V1

Date: 2026-09-19

Status: `PRE_REPAIR_DRAFT_NOT_EXECUTABLE`

Node: 109 / RTX4080

Execution mode: GOAL MODE, solve-and-continue.

This file is a draft. Do not execute it until a post-repair final coordination commit explicitly
promotes or replaces it.

## 0. Mission

Use the 20-hour unattended window to close the highest-value native characterization and
workload-design evidence without introducing new model downloads, new architecture mechanisms,
or redundant captures.

Mandatory scientific deliverables:

1. close missing native-resource characterization for selected existing AWMA families;
2. complete E1 shape × low-bit implementation diagnostics;
3. if gates pass, perform low-cost E3 natural-vs-controlled MoE routing diagnostics;
4. use remaining budget for pre-authorized opportunity work;
5. perform detailed capture only when a pre-frozen trigger selects a scientifically informative pair.

## 1. Frozen upstream

Accepted AWMA 109 V2.1 anchor:

`hrl/awma-109-ten-hour-capture-native-recon-v2`

`8a9d96ceb00e36ebdfa3d56cc277f965fffa649c`

Do not modify the accepted V2.1 branch/review pack.

Existing model / producer / state assets must be reused only after their exact receipts/hashes
are verified locally and against node164 authority.

Current Q05 / translation simulator results are not inputs for deciding whether E1/E3 native
measurements are valid. Do not use legacy translation timing conclusions to choose positive
native results.

## 2. Final-version placeholders

The post-repair final handoff will bind:

`<FINAL_109_EXECUTION_PARENT>`
`<FINAL_109_EXECUTION_BRANCH>`
`<CAMPAIGN_START_UTC>`
`<CAMPAIGN_DEADLINE_UTC>`
`<FINAL_109_REPORT_PATH>`
`<FINAL_109_REVIEW_PACK>`

## 3. Resource ownership

Before GPU work:

- inspect `nvidia-smi`;
- verify expected RTX4080 UUID;
- inspect `/data/c16/locks/c16_gpu_campaign.lock`;
- acquire it normally;
- never kill/bypass a legitimate owner.

If the lock is temporarily busy, perform CPU-only preparation/analysis and retry within the
bounded policy. Do not spin indefinitely.

Keep accepted model replicas on 109 if already present.
node164 remains durable authority.

## 4. Stage 109-M0 — Existing-family native resource closure

### 4.1 Targets

- Q05 Prefill Flash;
- Prefill GEMM Primary;
- Decode GEMV Primary;
- Decode Flash Primary-1.

Decode Flash Primary-2 remains a tiny control; do not perform a dense NCU sweep on it.

### 4.2 Reuse-first rule

Before any new profiler run, inspect accepted receipts/review packs.

For each target classify every required field:

`ACCEPTED_REUSE`
`MISSING_NEEDS_RUN`
`NOT_AVAILABLE`

Do not recollect evidence already accepted under the same identity, tool semantics, and metric
definition.

### 4.3 Required native fields

At minimum:

- exact semantic target identity;
- exact function / shape / occurrence;
- uninstrumented timing authority where already available or cheaply recoverable;
- kernel/census context;
- selected compute-pipeline utilization;
- achieved/issued warp activity where supported;
- L2 traffic;
- DRAM traffic;
- occupancy / launch resource information;
- selected stall metrics only if available and interpretable in the installed tool.

Resolve exact metric names with the installed `ncu --query-metrics`.

Do not hard-code unsupported metric names.

### 4.4 Measurement semantics

Record:

- NCU version;
- replay mode;
- cache-control mode;
- number of passes;
- clock / persistence settings if changed;
- target selection method;
- whether execution came from complete application, exact replay, or local operator replay.

Do not use NCU wall time as native timing.
Do not call NCU cache-control a TLB flush.

### 4.5 M0 acceptance

M0 passes if:

- all four targets have a complete resource-row with either accepted reuse or bounded new
  measurement;
- every row has exact provenance and target identity;
- no missing field is silently zero-filled;
- unsupported counters are marked `COUNTER_UNAVAILABLE`;
- comparisons distinguish native timing from profiler measurements.

Produce:

`EXISTING_FAMILY_NATIVE_RESOURCE_MATRIX.tsv`

and provenance receipts.

## 5. Stage 109-M1 — E1 shape × low-bit implementation diagnostics

### 5.1 Scientific question

For the same semantic linear operator, when token-row shape changes, do low-bit implementation
benefits and GPU resource limits remain the same?

Competing explanations:

A. reduced weight traffic dominates;
B. M changes reuse / parallel utilization / tensor-core utilization;
C. dequantization, layout, extra instructions, or kernel selection dominates.

### 5.2 Core matrix

Operators:

- FFN `down_proj`;
- Attention `q_proj`.

Shapes:

- `M=1`;
- `M=256`.

Implementations:

- raw;
- AWQ.

Core:

`2 operators × 2 M values × 2 implementations = 8 points`.

N/K must come from the real frozen weights.

M=1 is a shape diagnostic.
Do not relabel it as natural Decode.

### 5.3 Authority and semantic binding

For every operator:

- bind exact model ID/revision;
- bind exact raw/AWQ checkpoint authority;
- bind exact operator path/layer;
- bind exact weight tensor or AWQ qweight/qzeros/scales identities;
- bind activation-pool source and hash;
- bind runtime/backend source versions;
- record tensor rank, shape, stride, dtype, and storage layout;
- record timing-region semantics.

The existing down_proj anchor may be reused only after exact identity verification.
It does not automatically qualify q_proj.

### 5.4 Numeric correctness

Separate:

1. implementation correctness:
   AWQ execution versus a trustworthy reference using the same quantized representation;
2. deployment/quantization difference:
   AWQ deployment versus raw model semantics.

If absorbed scaling / input transformation prevents a clean same-function comparison, mark the
affected point:

`IMPLEMENTATION_LEVEL_ONLY`

and STOP the raw-vs-AWQ semantic claim for that operator.
Continue independent M1 work.

Do not fabricate an input transform.

### 5.5 Dtype bridge

Record actual input / output / accumulation behavior as far as the runtime exposes it.

If raw and AWQ differ in the execution dtype relevant to the comparison, add matching raw-FP16
bridge points for each affected operator at M=1 and M=256.

Thus the core matrix remains 8; bridge points are conditional and may increase the measured set.

Do not overwrite raw BF16 identities.

### 5.6 Native timing protocol

Default starting protocol for new points:

- 2 warmups;
- 5 uninstrumented measurements;
- save every sample;
- report median and dispersion;
- interleave comparison order when practical.

This count is a campaign protocol, not a literature-derived universal rule.

If noise prevents interpretation, perform a bounded repeat block after checking temperature,
clock, background processes, and synchronization.
Do not select the fastest result.

### 5.7 Implementation fingerprint

Each point must record:

- semantic operator;
- tensor shapes;
- backend implementation;
- kernel sequence;
- kernel names;
- grid/block;
- temporary dequantization/copy kernels;
- whether a path switch occurred relative to another M;
- output checksum/numeric error status.

A multi-kernel AWQ region must be timed and described as a semantic region if that is the
actual implementation. Do not select only the matmul kernel and call it the complete operator.

### 5.8 Resource diagnosis

Run bounded NCU only after native timing / implementation fingerprints are closed.

Collect only metrics needed to distinguish A/B/C.

At minimum where supported:

- L2 bytes/transactions;
- DRAM bytes/transactions;
- tensor/math utilization indicators;
- occupancy/warp activity;
- instruction / stall indicators relevant to observed changes.

### 5.9 M1 acceptance

E1 core passes if:

- all 8 core points have authoritative identity;
- all 8 have native timing samples;
- all 8 have implementation fingerprints;
- output correctness/status is explicit;
- every raw/AWQ pair has a declared semantic comparability class;
- dtype bridge status is resolved;
- NCU/resource rows exist for the points required by the pre-frozen diagnosis plan;
- no result is labeled pure bit-width causality unless the evidence actually supports it.

Produce:

- `E1_CORE_MATRIX.tsv`
- `E1_IMPLEMENTATION_FINGERPRINT.tsv`
- `E1_NUMERIC_VALIDATION.tsv`
- `E1_NATIVE_TIMING.tsv`
- `E1_RESOURCE_DIAGNOSIS.tsv`
- `E1_CLAIM_BOUNDARY.md`

## 6. Stage 109-C1 — Conditional E3 MoE routing diagnostic

Entry gates:

- M1 accepted or cleanly closed;
- Q30 accepted exact S2 state/replay authority verifies;
- target MoE FFN region can be replayed with the same expert execution backend;
- resident-weight/loading policy is identical across comparison cases;
- enough campaign budget remains.

If any gate fails, mark `SKIPPED_GATE` and continue to opportunities.

### 6.1 Required cases

N — natural routing.

P — histogram-preserving permutation:
jointly permute the relevant token/hidden ordering and corresponding route/gate information;
apply inverse permutation to output and verify equivalence.

U-active — balance assignments within the naturally active expert set.

Do not require H hotspot or U-all in this first campaign.

### 6.2 Controls

Hold:

- M=2048;
- actual model E/k;
- total assignments;
- expert precision;
- expert backend;
- expert-weight residency/loading policy;
- input pool;
- timing boundary.

Record:

- natural active expert set;
- per-expert token histogram;
- CV/dispersion;
- kernel counts/shapes;
- dispatch time;
- expert compute time;
- combine time;
- bytes/resource metrics where low-cost;
- numeric validation for P.

U-active is `SYNTHETIC_ROUTING`.
Do not report it as natural model speed.

### 6.3 E3 acceptance

Pass as a light diagnostic if:

- N authority is exact;
- P equivalence passes;
- U-active obeys the defined controls;
- execution region and weight residency are identical across cases;
- raw timing and route statistics are saved;
- result is scoped to this region/backend.

No detailed trace is required for E3 acceptance.

## 7. Opportunity queue

Run only when mandatory work is closed or when a required resource would otherwise be idle.

### G1 — Scenario extension

Priority:

1. Qwen2.5-0.5B B1 / T8192 / D32;
2. B4 / T2048 / D32.

Requirements:

- new run identity;
- frozen input/token IDs;
- no silent reuse of old S2 label;
- native timing + lightweight census;
- small resource sample only if needed.

If trustworthy input construction cannot be closed, skip.

### G2 — Same-quantized-weight execution decomposition

Use an already-qualified E1 operator.

Possible diagnostic paths only if the frozen runtime already provides trustworthy implementations:

A. actual AWQ;
B. one-time dequantized weight then FP16 matmul;
C. per-invocation dequantization plus FP16 matmul.

Do not implement a new backend to create this comparison.

Report these as implementation diagnostics, not deployment speedups.

### G3 — Profiling protocol sensitivity

Targets:

- Q05 Prefill Flash;
- Prefill GEMM Primary.

Compare supported cache/replay protocol variants under the installed NCU.

Record exact tool semantics.

Do not call the result a TLB warm/cold experiment.

### G4 — Llama raw shape holdout

Reuse accepted Llama-3.2-1B asset/binding.

At most:

`2 pre-frozen semantic linear roles × {M1,M256}`

This validates raw shape trend only.
It does not validate AWQ effect.

## 8. Conditional detailed capture

No detailed capture is mandatory.

A candidate pair may enter capture only if:

- native effect exceeds measured run-to-run noise;
- the pair distinguishes at least one competing explanation;
- exact semantic and kernel identity is closed;
- capture can complete before the no-new-work deadline;
- storage/transfer budget remains.

Before reading holdout results, freeze the selection rule.

Default total new detailed raw budget for this draft: 16 GiB.
Final handoff may reduce but must not silently increase it.

Use existing producer validation contracts.
Partial capture remains partial.

## 9. Data-plane rules

Use node164 durable authority.

For every new large artifact:

`staging → local closure → ready → .partial transfer → size/SHA verify → no-overwrite admit → ACK`

Once a task reaches local ready state, transfer may overlap later CPU-only work.
A later GPU task may start while prior data transfers only if local space and transfer pressure are
safe and each run has unique paths/receipts.

Never delete accepted V2.1 data.

## 10. Solve-and-continue / STOP

Engineering issues: solve and continue.

Scientific issue in one task:

- freeze that task;
- preserve evidence;
- write `STOP_SCIENTIFIC`;
- continue independent pre-authorized tasks.

Stop whole 109 Goal only if a shared defect invalidates multiple queued tasks, GPU identity/lock
is unsafe, or model/data authority is inconsistent globally.

## 11. Finalization

No new target in final 2 hours.

Required durable outputs in final review pack:

- `README.md`
- `SOURCE_ANCHORS.md`
- `PIPELINE_STATE.json`
- `EXISTING_FAMILY_NATIVE_RESOURCE_MATRIX.tsv`
- E1 files listed above
- E3 files if executed
- opportunity-task receipts if executed
- detailed-capture selector decision
- `RAW_DATA_INDEX.tsv`
- `RUN_RECEIPTS.json`
- `SHA256SUMS`

Final report must list:

- accepted;
- partial;
- skipped by gate;
- skipped by budget;
- scientific stops;
- opportunity tasks actually executed;
- node164 ACK status;
- GPU lock release / idle baseline.

Then commit → push → remote verify → clean worktree → release lock → STOP.
