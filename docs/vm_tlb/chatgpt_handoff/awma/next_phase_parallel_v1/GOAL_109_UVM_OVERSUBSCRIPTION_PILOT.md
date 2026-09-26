# Goal 109 — AI UVM/Oversubscription Feasibility Pilot V1

Stage:
`AWMA_AI_UVM_OVERSUBSCRIPTION_FEASIBILITY_PILOT_V1`

Execution branch:
`hrl/awma-ai-uvm-oversubscription-feasibility-pilot-v1`

Node:
109 / RTX4080

## 0. Goal

Determine whether the current RTX4080/Linux environment can provide stable,
observable and reproducible UVM page-fault/migration behavior under controlled
AI-shaped memory-access patterns.

This is a feasibility + problem-discovery pilot.
It is NOT:
- a new UVM mechanism;
- a claim about real LLM inference;
- a translation-TLB experiment unless an exact TLB metric exists;
- a reason to download or modify models.

## 1. Safety and GPU lock

All GPU execution must hold:
`/data/c16/locks/c16_gpu_campaign.lock`

Before allocation record:
- GPU model/driver/CUDA;
- `cudaMemGetInfo`;
- `nvidia-smi` memory state;
- host MemAvailable;
- swap state;
- other GPU processes.

No experiment may intentionally exhaust host memory or invoke host OOM.

Define a safe allocation cap before any oversubscription run:
- never exceed 1.30 × physical VRAM;
- never exceed a fixed byte cap of 20 GiB;
- require host MemAvailable >= managed_allocation + 8 GiB at launch;
- if this cannot be met, reduce all oversubscription levels proportionally and
  record the actual ratios.

Any persistent driver reset/Xid/OOM -> stop immediately and preserve evidence.

Cleanup every managed allocation and verify GPU memory returns to pre-run state.

## 2. Platform capability audit

Build and run a minimal CUDA Managed Memory probe.

Audit availability of:
- `cudaMallocManaged`;
- `cudaMemPrefetchAsync`;
- `cudaMemAdvise` calls needed only for controls;
- Nsight Systems UVM/page-fault/migration events;
- CUPTI Unified Memory activity/counters if supported by this driver.

Do not invent metrics when tools do not expose them.

Create:
`UVM_PLATFORM_CAPABILITY.tsv`

Each metric/tool:
- AVAILABLE
- AVAILABLE_WITH_LIMITATION
- UNAVAILABLE.

If managed oversubscription itself is unsupported/stable execution impossible:
final status `UVM_PLATFORM_BLOCKED` and STOP.

## 3. Build one deterministic CUDA harness

Create an isolated harness under:
`util/vm_tlb/awma/uvm_pilot/`

Three AI-shaped access patterns:

### P1 DENSE_WEIGHT_STREAM
Represents repeated dense-model weight streaming at token granularity.

- one large managed allocation;
- deterministic sequential/coalesced GPU reads;
- each "token step" scans the entire active weight pool;
- small output/checksum prevents optimization;
- repeated steps expose whether the same pages remain resident or thrash.

This is AI-shaped, not real model execution.

### P2 KV_GROWTH
Represents a growing KV-like active region.

- managed pool larger than the initial active prefix;
- each step appends/touches a new tail region;
- then reads the entire currently-active prefix or a deterministic sampled
  prefix if full scanning exceeds the run-time safety cap;
- active set increases monotonically.

Record exact access law; do not call it real attention.

### P3 MOE_EXPERT_ROTATION
Represents sparse selection from a larger expert pool.

- divide one managed allocation into fixed-size expert regions;
- each step touches exactly K expert regions;
- use one deterministic route sequence with locality and periodic rotation so
  active experts change over time;
- record route sequence hash.

Do not claim the route distribution matches OLMoE unless directly derived and
proved.

All patterns must have CPU-reference checksum validation.

## 4. Fixed residency/oversubscription matrix

Determine physical VRAM `V` at runtime.

Target allocation ratios:
- R0 = 0.75V (comfortably resident)
- R1 = 0.95V (near capacity)
- R2 = 1.10V (mild oversubscription)
- R3 = 1.30V (moderate oversubscription)

Apply the safety cap from Phase 1.
Record actual allocated bytes and actual ratio.

No finer ratio sweep.

For each pattern × ratio:
- 1 untimed setup/first-touch control where required;
- 1 authoritative cold run;
- 1 immediate repeat run to expose residency/history.

If runtime exceeds 180 seconds for one measured run, abort that point safely
and mark `RUNTIME_CAP_REACHED`; continue lower ratios.

Do not add more repetitions merely to obtain smoother numbers.

## 5. Two access-management modes

### M0 DEMAND
Normal demand migration; no prefetch before the measured kernel sequence.

### M1 PREFETCH_CONTROL
Use `cudaMemPrefetchAsync` only when the requested working set fits in the
reported GPU memory at that point.

For oversubscribed allocations where prefetching the full working set is not a
valid operation, do not fake a full-prefetch comparison.
Use `NOT_APPLICABLE_OVERSUBSCRIBED`.

M1 is a control for migration placement, not a proposed mechanism.

Do not add preferred-location/read-mostly knobs in this Goal unless needed to
make basic UVM function correctly; if needed, record and stop for scientific
review rather than silently changing policy.

## 6. Metrics

For every measured run capture:

### Execution
- GPU kernel/sequence time with CUDA events;
- wall time;
- first iteration vs subsequent step times;
- checksum.

### UVM / migration where available
- GPU page-fault events or fault groups;
- HtoD migration bytes/count;
- DtoH eviction/migration bytes/count;
- migration time;
- CPU page faults if exposed;
- prefetch bytes/control events.

### Residency / system
- GPU memory before/peak/after where observable;
- host memory before/after;
- allocation size;
- working-set size per step.

### Temporal behavior
For step-based P2/P3:
- per-step latency;
- per-step migrated bytes/fault events if tool supports correlation;
- active working-set bytes;
- expert/prefix identifier.

Do not infer TLB miss rate, PPN continuity, page size, or shootdown counts from
UVM transfer events unless the exact source reports them.

## 7. Stability / reproducibility gate

The pilot is useful only if:
- all checksums PASS;
- no driver/Xid/reset;
- cleanup returns memory to expected state;
- UVM events correspond directionally to residency ratio changes;
- repeated identical points do not exhibit unexplained order-of-magnitude
  variation.

Do not require an arbitrary percentage variance threshold.
Report raw cold/repeat values.

If UVM counters are unavailable but timing and migration bytes are reliable:
classify `FEASIBLE_WITH_LIMITED_OBSERVABILITY`, not failure.

## 8. AI-specific problem-discovery analysis

Do NOT ask only "is oversubscription slower?"

For each pattern identify:
- onset of migration/fault activity versus allocation ratio;
- whether repeated steps stabilize or repeatedly migrate the same working set;
- whether active-set growth causes a phase transition;
- whether sparse expert rotation avoids migration or causes periodic thrash;
- whether migration traffic dominates wall time or remains hidden;
- whether P1/P2/P3 differ qualitatively under the same residency pressure.

Create:
`AI_SHAPED_UVM_BEHAVIOR.md`

Claims must be:
- about these synthetic patterns and this platform;
- not about all LLMs/MoE models.

## 9. Optional existing-model feasibility bridge

Only if there is already a working local code path that can place a tensor or
buffer in CUDA Managed Memory without replacing PyTorch's allocator globally
and without substantial framework surgery:

run ONE small existing Llama or OLMoE tensor-level experiment to prove bridge
feasibility.

This is optional.
Do not spend more than one bounded engineering attempt.
Do not download anything.

If unavailable:
`REAL_MODEL_UVM_BRIDGE_NOT_AVAILABLE_IN_PILOT`.

## 10. Literature/novelty boundary

Compare observed phenomena with closest existing UVM work:
- GPU UVM runtime analyses;
- oversubscription frameworks;
- batch-aware unified memory;
- Avatar's oversubscription sensitivity;
- migration/prefetch/page eviction literature.

This Goal does not propose a mechanism.

Output at most TWO future research questions, each requiring:
1. an observed reproducible phenomenon;
2. a specific AI-shaped access property;
3. a closest-work gap;
4. a measurable future real-model validation path.

## 11. Decision

Final status exactly one:

### `UVM_PLATFORM_BLOCKED`
Basic managed oversubscription is not safely runnable/observable.

### `UVM_FEASIBLE_NO_DISTINCT_AI_SHAPED_SIGNAL`
UVM works, but P1/P2/P3 only show generic capacity/thrashing behavior with no
useful differentiated problem.

### `UVM_FEASIBLE_WITH_LIMITED_OBSERVABILITY`
Behavior is stable but critical UVM event telemetry is unavailable.

### `READY_FOR_AI_UVM_CHARACTERIZATION_V1`
At least one stable, differentiated AI-shaped behavior is observed and merits
a real-model / broader characterization stage.

Do not output a mechanism name.

## 12. Durable evidence

Publish raw authority to node164 under a new directory:
`/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/uvm_oversubscription_pilot_20260926/`

Include:
- source/binary hashes;
- capability audit;
- system/GPU receipts;
- profiler exports;
- per-run metrics;
- checksums;
- logs;
- SHA256SUMS.

## 13. Deliverables

- README.md
- UVM_PLATFORM_CAPABILITY.tsv
- SYSTEM_SAFETY_RECEIPT.tsv
- PATTERN_CONTRACT.md
- MATRIX_PREREG.tsv
- RUN_MATRIX.tsv
- UVM_EVENT_MATRIX.tsv
- STEPWISE_BEHAVIOR.tsv
- STABILITY_CHECKS.tsv
- AI_SHAPED_UVM_BEHAVIOR.md
- CLOSEST_WORK_SCREEN.md
- FUTURE_RESEARCH_QUESTIONS.md
- REAL_MODEL_BRIDGE_STATUS.md
- RAW_DATA_INDEX.tsv
- SHA256SUMS
- REPORT.md

Commit/push/fetch-back/remote HEAD+tree/hash/clean and STOP.

