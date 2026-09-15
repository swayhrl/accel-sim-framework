# Simulation Metrics and Data Model

## Principle

Simulation Evidence is a separate evidence plane from Native Evidence. It may be joined for comparison, but it must never overwrite or masquerade as real-GPU measurement.

Every normalized simulation metric must carry:

```text
WORKLOAD_ID / TARGET_ID when aligned
SIM_INPUT_ID or historical input lineage
SIM_BASELINE_ID or historical baseline lineage
SIM_RUN_ID for current runs
evidence_origin
scientific_status
metric_name
metric_value
unit
raw log SHA256
analyzer identity
claim_scope
```

## Evidence origins

Use at least:

```text
SIMULATOR
HISTORICAL_RECORD
CROSSVIEW_DERIVED
```

`HISTORICAL_RECORD` is used for inherited C12–C15 results that were not freshly replayed under the new baseline.

## Metric domains

### Translation

Canonical families should cover, where the simulator exposes them:

```text
L1 TLB access/hit/miss
L2 TLB access/hit/miss
translation request count
PTW request count
PTW latency
walker occupancy/utilization
PWC hit/miss
page-size class
translation-related stalls/queues
```

### Cache/memory hierarchy

```text
L1D access/hit/miss
L2 access/hit/miss
reservation/fill/replacement events
cache queue occupancy/stall where supported
DRAM transactions/bytes
memory latency/throughput proxies
```

### Performance

```text
cycles
instructions
IPC
kernel/runtime cycles
stall cycles/categories when valid
```

### Mechanism-specific

Mechanism counters remain namespaced rather than flattened into generic baseline metrics.

Examples:

```text
segment.*
selective.*
subentry.*
cache_variant.*
```

## Units and aggregation

Every metric must state its unit and aggregation level:

```text
count
bytes
cycles
ratio
percent
requests/cycle
cycles/request
```

and scope:

```text
RUN
KERNEL
WINDOW
SM
TLB_LEVEL
CACHE_LEVEL
OBJECT_CLASS
```

Do not compare ratios derived from different denominators without an explicit transformation.

## Raw vs derived evidence

Separate:

```text
raw telemetry
→ normalized telemetry
→ derived metrics
→ research summary
```

For every derived metric, retain the formula/version and upstream normalized metric identities.

Example:

```text
TLB miss rate
= misses / accesses
```

must not be stored without preserving source misses/accesses.

## Scientific status

The source run and the normalized row both preserve status.

Typical values:

```text
FORMAL
DIAGNOSTIC
PRE_FIX
OBSOLETE
UNKNOWN
```

A parser cannot promote evidence status.

## Baseline vs mechanism comparison

Mechanism speedup is always bound to an explicit baseline:

```text
speedup = baseline_cycles / mechanism_cycles
```

Store:

```text
baseline SIM_RUN_ID
mechanism SIM_RUN_ID
metric formula
value
```

Do not report “+X%” without the baseline identity.

## Cross-view fields

When Simulation Evidence is aligned with Native Evidence, preserve both raw origins, for example:

```text
native.unique_4k_pages
sim.translation.l1_tlb_miss_rate
native.ncu_l2_bytes
sim.l2.bytes
sim_vs_native_delta
join_relation
```

A difference between simulated and measured counters is not an error by definition; it is calibration/fidelity evidence that must remain visible.

## Initial dataset outputs

Recommended normalized datasets:

```text
AWMA_SIM_RUNS.tsv/parquet
AWMA_SIM_TELEMETRY.tsv/parquet
AWMA_SIM_TRANSLATION.tsv/parquet
AWMA_SIM_CACHE.tsv/parquet
AWMA_SIM_PERFORMANCE.tsv/parquet
AWMA_SIM_COMPARISONS.tsv/parquet
```

Human-reviewable TSV/JSON summaries should accompany any Parquet authority snapshot.
