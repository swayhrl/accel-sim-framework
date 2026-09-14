# CODEX 174-new — Analysis After Pipeline V1

Ownership: ChatGPT
Execution node: 174-new / port 2239
Status: do not execute until `C16_DATA_PLANE_V1_QUALIFIED`

## Objective

As soon as formal runs arrive from node109, verify/admit/catalog them and immediately perform CPU-side parsing and memory characterization. Do not wait for all models before analyzing the first valid run.

## Analysis role

174-new is not a replacement GPU runtime. It does not need CUDA/NCU/NVBit execution capability for this stage.

Its role is:

```text
raw verification
catalog
CPU parser
semantic/object join
page/cache-line fingerprint
NCU normalization
Sampling V2 preparation
cross-model datasets
```

## Source selection

Consume only cataloged runs with explicit scientific status.

Never select raw files by filename alone.

## Stage 1 — parser foundation

For each newly admitted run, bind parser outputs to:

```text
source RUN_ID
source raw manifest SHA
parser git commit
parser CLI/config
output artifact hashes
```

Preferred parsed outputs where data permits:

```text
launches.parquet
memory_access.parquet
object_ranges.parquet
ncu_metrics.parquet
semantic_join.parquet
```

Do not manufacture unavailable fields.

## Stage 2 — memory fingerprints

Generate per-run/per-window summaries:

```text
unique 4K pages
unique 64K pages
page occupancy/distribution
contiguous-range summary
128B cache-line footprint
sector/width utilization where trace supports it
read/write/atomic composition
active-mask statistics
object attribution
set overlap / same-object revisit
```

Do not claim a true global shared-L2 reuse/MRC when trace ordering does not support it.

## Stage 3 — object attribution

At minimum preserve classes:

```text
WEIGHT
QUANT_METADATA
KV_CACHE
ACTIVATION when evidenced
UNKNOWN_RUNTIME
```

UNKNOWN is valid and must not be force-classified.

## Stage 4 — NCU normalization

Normalize only metrics actually captured and tool-version-bound.

Store:

```text
metric name
value
unit
NCU version
capture RUN_ID
kernel/target identity
```

Do not compare semantically different counters as if identical.

## Stage 5 — incremental datasets

Maintain versioned datasets under 164, for example:

```text
derived/datasets/native_catalog/
derived/datasets/memory_fingerprint/
derived/datasets/ncu_counter/
derived/datasets/sampling_v2/
```

Every rebuild gets a receipt binding source catalog snapshot + code commit.

## Stage 6 — Sampling V2 support

Build the cheap-native feature table needed for strata:

```text
Phase
Operator/semantic class where evidenced
Implementation
Shape bucket
DType
quantization mode
KV representation when evidenced
```

Keep certainty/heavy-tail candidates separate from probabilistic strata.

Do not label a medoid/representative selector as unbiased.

## Parallel execution policy

As soon as one model/scenario is cataloged:

```text
verify -> parse -> fingerprint -> publish derived receipt
```

while node109 continues capturing the next scenario/model.

This is the default pipeline; do not wait for a campaign-wide batch.

## Required outputs

At minimum:

```text
PARSE_INDEX.tsv
FEATURE_INDEX.tsv
OBJECT_ATTRIBUTION_SUMMARY.tsv
PAGE_FINGERPRINT_SUMMARY.tsv
CACHELINE_FINGERPRINT_SUMMARY.tsv
NCU_NORMALIZED_INDEX.tsv
DATASET_BUILD_RECEIPTS/
OPEN_ISSUES.md
```

## Acceptance

A run is `ANALYSIS_READY_PASS` only when:

```text
raw source hash-bound
parser commit/config bound
parsed outputs hash-closed
feature outputs hash-closed
unknowns explicitly retained
scientific status propagated
no source raw mutation
```

A dataset version is PASS only when its source catalog snapshot and all included RUN_IDs are reproducibly enumerated.

## STOP boundary

For Wave 1, STOP after all currently available Qwen2.5 admitted runs have been parsed/fingerprinted and the initial Sampling-V2-ready dataset is built.

Do not make final universal cross-model claims until ChatGPT reviews coverage.
Do not create new Qwen3/DeepSeek input authority in this stage.