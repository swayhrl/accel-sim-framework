# C16 Analysis Output Contract V1

Ownership: ChatGPT
Execution node: 174-new / CPU analysis
Long-term data root: `/root/share/mnt164/huangrulin/c16_ai_workload`

## 1. Source authority

Analysis consumes only:

- cataloged Pipeline V1 runs; or
- explicitly cataloged legacy imports with a frozen source authority.

Never promote a file based on filename alone.

Each derived product must bind:

```text
source RUN_ID or legacy object ID
source raw manifest / source artifact SHA
parser git commit
parser CLI/config
output path
output size
output SHA256
created_at_utc
```

Raw source data are read-only.

## 2. Derived layers

```text
derived/parsed/<source-id>/
derived/features/<source-id>/
derived/datasets/<dataset-version>/
```

No parser writes into `raw/` or `legacy/`.

## 3. Memory access normalized record

When source data support it, normalize to fields such as:

```text
source_id
launch_id
phase / decode_step when evidenced
function / code-object identity when evidenced
static instruction identity / PC-offset when evidenced
opcode
memory_space
is_load
is_store
is_atomic
width_bytes
active_mask or active_lane_count
lane/address
object_class
```

Unavailable values remain UNKNOWN/null. Never synthesize them.

## 4. Memory fingerprints

At minimum, where data support them:

```text
unique 4K pages
unique 64K pages
unique 128B cache lines
unique exact VA count
access width distribution
read/write/atomic distribution
active-lane distribution
page occupancy
contiguous-range summary
per-launch footprint
same-object revisit
set overlap
```

Callback/order-derived reuse must be labeled as observed trace order, not global hardware L2 order.

Do not claim true shared-L2 global MRC from per-callback/per-file ordering.

## 5. Object attribution

Preserve classes:

```text
WEIGHT
QUANT_METADATA
KV_CACHE
ACTIVATION (only with evidence)
UNKNOWN_RUNTIME
```

UNKNOWN is a valid scientific result.

## 6. NCU normalization

Store only actually captured metrics, bound to:

```text
NCU version
raw report SHA
kernel/launch identity
metric name
value
unit
```

Never equate counters whose names/semantics differ across versions or target kernels.

## 7. Regression anchors from archived RTX3090 Q2

Use the archived formal Q2 raw only as parser/fingerprint regression evidence, not as phase-wide representativeness.

Expected full-anchor values from frozen historical analysis:

### Q2 Prefill

```text
lane events: 786432
READ: 524288
WRITE: 262144
width 2B: 524288
width 4B: 262144
unique exact VA: 333952
unique 128B lines: 5224
unique 4K pages: 164
unique 2M pages: 20
```

### Q2 Decode

```text
lane events: 18432
READ: 12288
WRITE: 6144
width 2B: 12288
width 4B: 6144
unique exact VA: 12291
unique 128B lines: 195
unique 4K pages: 9
unique 2M pages: 7
```

The parser must reproduce these values exactly from the archived source before it is trusted on new formal NVBit data, unless a documented schema difference makes the comparison inapplicable.

## 8. Dataset build contract

Each dataset version must have a receipt containing:

```text
dataset_version
source catalog snapshot SHA
included source IDs
code commit
build argv/config
output files + SHA256
scientific-status filter
```

No campaign-wide claim is authorized merely because a dataset was built.
