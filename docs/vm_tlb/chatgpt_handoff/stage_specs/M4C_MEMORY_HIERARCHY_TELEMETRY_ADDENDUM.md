# M4C memory-hierarchy telemetry addendum

Status: **AUTHORIZED CONTRACT ADDENDUM — MANDATORY BEFORE M4C FORMAL RUNS**.

This addendum extends `M4C_LLM_BASELINE_CHARACTERIZATION.md` so that the expensive real Llama replay is useful not only for the immediate TLB/Segmentation reproduction, but also for later L1/L2/cache–TLB/DRAM research. It is observability-only and must not change simulated behavior.

It does **not** invalidate or require rerunning completed M4I or M4R admission/feasibility gates. It must be integrated before M4C C2/C3 characterization runs and the same telemetry must remain available for M4B paging/Segmentation comparisons.

## 1. Design principle: collect once, analyze many times

The formal traces are large and expensive to replay. Therefore M4C must capture a reusable cross-memory-hierarchy dataset in the same run.

Do not solve this by dumping every memory event. Formal runs must use structured aggregate/kernel/window statistics, not an unbounded per-access log.

Separate two categories:

1. **Offline trace-derived metrics** — compute from the immutable trace/sidecars without simulator rerun whenever possible.
2. **Simulator-state metrics** — collect only where runtime cache/TLB/MSHR/queue/replacement state is required.

Any optional detailed event sampling must be bounded, explicitly sampled, and diagnostic-only.

## 2. Telemetry levels

Implement a configurable telemetry level or equivalent clean separation.

### Level 0 — off

No new memory-hierarchy telemetry. Used only for behavior-neutral differential validation.

### Level 1 — mandatory formal aggregate

ROI totals plus per-object totals. Required for every M4C/M4B formal run.

### Level 2 — mandatory reusable characterization

Level 1 plus per-kernel records and bounded fixed-window aggregate records. This is the default for real Llama characterization once host-side overhead is validated.

Window identity must be deterministic and provenance-bound. Prefer an instruction- or memory-transaction-count window rather than wall-clock host time. The exact window size may be selected during the bounded pilot based on output/host-runtime overhead, but must then be frozen before formal runs.

### Level 3 — optional diagnostic sampling

Bounded sampled event records for a small set of representative kernels/windows only. Never enable an unbounded access-by-access stream for full formal prefill/decode1.

## 3. Common dimensions

Where meaningful, records must be separable by:

- ROI: prefill / decode1;
- trace policy: `COMPUTE_ONLY_TP_PARTITION` / `FULL_RANK0`;
- semantic kernel index and kernel name/family;
- object class: `WEIGHT`, `KV_CACHE`, `UNKNOWN`;
- request class: application data vs PTE, with PTE level when available;
- load / store / atomic where the simulator distinguishes them;
- page size;
- SM for L1-side data, and L2 subpartition/bank/channel where practical.

Do not infer additional object classes from behavior. Unknown application data remains `UNKNOWN`.

## 4. Front-end / coalescing observability

Collect enough information to relate tensor/object traffic to actual cache traffic:

- memory instructions;
- active-lane references;
- coalesced memory transactions;
- requested application bytes;
- transaction bytes sent toward the memory hierarchy;
- 32B-sector utilization / sector-mask population where applicable;
- transactions per memory instruction;
- load/store/atomic transaction counts.

Report aggregate and per-object values. Per-kernel values are required at Level 2.

Offline from immutable traces, also produce reusable locality/footprint tables including at least:

- unique 128B cache lines;
- unique 32B sectors where relevant;
- unique 64KB and 2MB pages;
- access-frequency/hotness distribution summaries;
- per-object and per-kernel footprints;
- cross-kernel footprint overlap for Weight/KV/UNKNOWN when exact range attribution is available.

If reuse-distance or stride summaries are added, compute them offline rather than expanding formal simulator logs.

## 5. L1D telemetry

For application data entering L1D, collect at minimum:

### 5.1 Outcomes

- accesses;
- hits;
- misses;
- sector misses;
- hit-reserved;
- data-cache MSHR hits/merges where exposed;
- reservation failures.

Reservation failures must be split by the existing simulator reason when available, including:

- line allocation failure;
- miss queue full;
- MSHR entry full;
- MSHR merge-entry full;
- read/write pending conflict.

### 5.2 Resource pressure

Where available without protocol changes:

- L1 data-cache MSHR occupancy high-water and histogram/window average;
- merge depth / merged-request count;
- miss-queue occupancy high-water and window average;
- L1 bank/latency-queue or equivalent port/backpressure events;
- fill count;
- eviction count;
- dirty writeback count/bytes.

### 5.3 Object attribution

Break down L1 outcomes by `WEIGHT`, `KV_CACHE`, `UNKNOWN`.

If observational cache-line metadata can be added behavior-neutrally, record an L1 incoming-object -> victim-object eviction matrix. The observational tag must not participate in hit matching, replacement, coherence, timing, or arbitration.

If exact L1 victim attribution would require invasive changes, document it as optional and do not delay mandatory M4C metrics.

## 6. L2 telemetry

L2 is mandatory because application data and PTE traffic share it in the accepted real-PTW baseline.

### 6.1 Outcomes by request class

Collect L2 access/hit/miss/sector-miss/MSHR-hit/reservation-fail counts separately for:

- data WEIGHT;
- data KV_CACHE;
- data UNKNOWN;
- PTE level 0/1/2/3 (or the simulator's exact level numbering);
- writeback/other traffic where required for conservation.

Never fold PTE traffic into ordinary application-data hit-rate tables.

### 6.2 L2 resource pressure

Collect, where exposed:

- L2 MSHR allocation/merge/full pressure;
- miss-queue / request-queue occupancy average/high-water and full events;
- per-subpartition/bank request distribution;
- input/output queue pressure around L2 and DRAM;
- fill and eviction counts;
- writeback count/bytes;
- bytes served by L2 vs bytes sent to DRAM.

Use existing simulator queue-length/stat hooks when possible rather than adding a parallel shadow timing model.

### 6.3 L2 replacement/pollution matrix

Add behavior-neutral fill/victim attribution for L2 with classes:

- `DATA_WEIGHT`;
- `DATA_KV_CACHE`;
- `DATA_UNKNOWN`;
- `PTE_L0` / `PTE_L1` / `PTE_L2` / `PTE_L3`;
- `OTHER` where unavoidable.

Produce `incoming_class -> victim_class` counts.

The following cells are especially important for later cache–TLB research:

- PTE -> Weight/KV/Unknown data victim;
- Weight/KV/Unknown data -> PTE victim;
- KV/Unknown -> Weight data victim;
- Weight -> KV data victim.

Observational class tags must never affect replacement victim selection.

## 7. DRAM and interconnect telemetry

Collect a reusable memory-system view, split between application data and PTE traffic where practical:

- DRAM read/write requests and bytes;
- PTE DRAM requests/bytes;
- memory-fetch latency average/max/histogram using existing latency hooks;
- request-queue / DRAM-queue latency where exposed;
- channel/bank distribution and imbalance;
- row-buffer/row-locality statistics already exposed by the simulator;
- NoC/interconnect request/byte counts for data vs PTE if obtainable without invasive event logging.

Per-object DRAM data traffic is desirable for `WEIGHT`, `KV_CACHE`, `UNKNOWN` and should be collected when the object identity survives to the memory request. If not, preserve enough immutable request metadata to add this attribution behavior-neutrally.

## 8. Stall / backpressure attribution

In addition to the M4C translation stalls, preserve memory-side stall causes useful for future work:

- translation/TLB/MSHR/PWQ/walker-caused blocked cycles;
- L1D reservation-fail/backpressure cycles/events;
- L2/ICNT/DRAM queue-full or memory-stage stall causes exposed by current GPGPU-Sim statistics;
- scheduler memory-stall aggregate where available.

Do not invent a new cycle attribution if current pipeline semantics cannot uniquely assign a cause. Distinguish exact event counts from derived/inferred stall attribution.

## 9. Cross-layer correlation

Create aggregate matrices that can be computed without raw event logs.

At minimum:

### 9.1 Translation outcome × data-cache outcome

Per object class, count translated application transactions by categories such as:

- L1-TLB hit / L2-TLB hit / PTW;
- followed by L1D hit / L1D miss;
- for L1D miss, followed by L2 hit / L2 miss.

The implementation may use request UID/context carried through the existing path, but must not alter timing or request ordering.

### 9.2 PTE/data contention view

Report, at aggregate/kernel/window level:

- PTE share of L2 accesses and DRAM accesses;
- PTE-induced L2 data evictions from the replacement matrix;
- L2 queue pressure during windows with high PTW activity;
- data-cache pressure during windows with high TLB-miss/PTW activity.

This is correlation evidence, not proof of causal interference unless supported by later controlled experiments.

## 10. Temporal granularity

Formal output must include:

1. ROI aggregate;
2. per-kernel aggregate;
3. bounded fixed-window aggregate for long/high-traffic kernels.

The window file should contain only compact counters/histograms, not addresses or one row per memory access.

This temporal view is required to support later questions such as:

- prefill vs decode behavior;
- layer/kernel phase changes;
- bursts of KV translation pressure;
- simultaneous TLB and cache pressure;
- whether a global average hides short critical bottlenecks.

## 11. Behavior-neutrality and overhead gate

Before enabling Level 2 on full formal runs:

- run the same bounded trace with new telemetry OFF and ON;
- cycles, IPC, architectural cache/TLB/memory counters and request ordering/conservation must be identical;
- only observational outputs may differ;
- M1-M3 and M4I invariants remain PASS.

Measure host wall-clock and output size overhead. If Level 2 is too expensive, reduce window frequency/record width, not the mandatory ROI/per-kernel counters.

Do not drop mandatory L1/L2/PTE/data aggregate counters merely to save host time.

## 12. Required reusable artifacts

Extend M4C closeout with machine-readable files (names may be adjusted only if the manifest maps them exactly):

- `KERNEL_MEMORY_STATS.tsv`;
- `WINDOW_MEMORY_STATS.tsv`;
- `L1D_OBJECT_STATS.tsv`;
- `L1D_FAIL_PRESSURE.tsv`;
- `L2_REQUEST_CLASS_STATS.tsv`;
- `L2_QUEUE_PRESSURE.tsv`;
- `L2_CLASS_REPLACEMENT_MATRIX.tsv`;
- `DRAM_REQUEST_CLASS_STATS.tsv`;
- `CROSS_LAYER_OUTCOME_MATRIX.tsv`;
- `TRACE_LOCALITY_OFFLINE.tsv`;
- `TELEMETRY_SCHEMA.md`;
- `TELEMETRY_OVERHEAD_VALIDATION.md`.

All files must include enough provenance to bind Core/Framework/config/trace/object-map identities.

## 13. M4B continuity

M4B-P and M4B-S must retain the same memory-hierarchy telemetry schema so that paging/sub-entry/Segmentation comparisons can answer not only TLB questions but also whether translation changes alter:

- L1D/L2 traffic;
- L2 PTE/data contention;
- cache occupancy/eviction behavior;
- DRAM/PTE traffic;
- memory-side stall pressure.

Do not introduce a new mechanism-dependent telemetry format after M4C unless it is backward-compatible or explicitly versioned.

## 14. Acceptance boundary

This addendum expands observability only. It does not authorize:

- synthetic 12K KV pressure;
- KV segmentation;
- new cache/TLB optimization mechanisms;
- page faults/migration/UVM;
- MCM/chiplet behavior.

M4C may proceed only after the mandatory behavior-neutral telemetry gate passes. Completed M4I/M4R work does not need to be repeated solely because of this addendum.
