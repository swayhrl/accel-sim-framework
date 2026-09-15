# C16 Trace Capture Architecture V2

## Problem statement

V1 proved that target identity is correct but the current all-GLOBAL-MREF implementation cannot terminal-close a complete model target launch. The recovery must reduce event pressure without returning to single-PC evidence.

## 1. Diagnostic split: volume vs lifecycle

Use one exact Qwen0 attention target with known-good MREF 4110 as a control.

Run the same exact target launch with:

1. single MREF / full launch — expected PASS control;
2. all GLOBAL MREF / CTA 0 only;
3. all GLOBAL MREF / CTA 0..1;
4. CTA count doubled geometrically until failure;
5. fixed CTA count with increasing static MREF count.

Record:

```text
callback/event count
bytes emitted
host drain rate
channel occupancy/overflow if measurable
GPU wall time
terminal status
last progress marker
```

This locates the pressure dimension.

## 2. Preferred formal method: CTA sharding

If one or more CTAs terminal-close with all GLOBAL MREFs, capture deterministic CTA shards.

### Shard identity

Each shard binds:

```text
model/input/scenario
exact target function
code object SHA
launch selector
static GLOBAL MREF set SHA
CTA selector/range
warp/lane semantics
tracer build SHA
```

### CTA selection

For a grid with many CTAs, use a deterministic spatial portfolio rather than only CTA 0:

- first CTA(s);
- center CTA(s);
- final CTA(s);
- evenly spaced quantile CTA IDs;
- when grid is multidimensional, cover edge/interior coordinates.

Prefer enough shards to demonstrate whether page/cache-line/object fingerprints stabilize.

If all CTAs can be covered within the campaign budget, classify `CTA_SHARDED_COMPLETE_GRID`; otherwise `CTA_SHARDED_REPRESENTATIVE_GRID`.

### Formal acceptance

A CTA shard is accepted only when:

- exact target launch identity matches;
- all selected static GLOBAL MREFs are instrumented;
- terminal marker is present;
- no overflow/drop;
- emitted record count is internally consistent where countable;
- nonzero addresses exist for executing memory references;
- raw is hash-closed and Pipeline ACKed.

## 3. Secondary method: MREF sharding

If even one CTA with all MREFs fails, partition the static GLOBAL MREF set into deterministic groups.

Group by contiguous static index ranges or balanced expected event mass, not cherry-picked PCs.

Require:

- exact same launch selector across replay;
- disjoint group membership;
- union equals the frozen selected GLOBAL MREF set;
- every group terminal-closes;
- group metadata records static MREF set SHA.

The merged product is `MREF_SHARDED_COMPLETE_SET` and explicitly lacks cross-group temporal order.

## 4. Compact binary tracer

If event count rather than callback lifecycle is the bottleneck, implement a compact record path before giving up.

Preferred record unit: one warp memory-instruction event, not one JSON line per lane.

Minimum record fields:

```text
launch_id
CTA id / coordinates
warp id
static instruction index or PC offset
opcode/access width metadata id
active mask
address representation
```

Address representation may be:

- 32 absolute 64-bit addresses for active lanes; or
- one 64-bit base plus per-lane signed deltas when lossless; or
- a tagged fallback to absolute addresses.

Requirements:

- binary, fixed/length-tagged records;
- no device-side string formatting;
- bounded ring/double buffer;
- asynchronous host drain;
- explicit dropped-record counter;
- terminal record after drain;
- offline decoder with round-trip unit tests.

Compression must be lossless for fields used by page/cache-line/object analysis.

## 5. Record-order claims

No V2 method may invent hardware global order.

- full single-run capture: `OBSERVED_CALLBACK_ORDER_ONLY`;
- CTA-sharded: order only within each shard;
- MREF-sharded: order only within each MREF group;
- merged cross-shard/global reuse-distance claims prohibited.

## 6. Quality gate before long capture

For every target method, first run a bounded canary and compute immediately:

```text
unique 4K pages
unique 64K pages
unique 128B lines
object mix
load/store mix
per-CTA diversity
```

Reject a shard/target as weak only when the evidence shows trivial footprint or redundant behavior. Do not reject merely because it is small if it represents a unique semantic stratum.

## 7. Capture budget

Per shard/group default:

```text
<= 20 min wall time
<= 4 GiB raw
```

However a complete formal shard is preferred over a hard byte cap. If a shard approaches the cap, reduce CTA count/group size and rerun from scratch; do not accept a truncated formal shard.

## 8. Minimum V2 success portfolio

At minimum attempt to obtain:

- Qwen0 S2 Prefill Attention — all-MREF CTA or MREF-sharded formal evidence;
- Qwen0 S2 Prefill heavy GEMM — same;
- one Qwen0 Decode early/late target if feasible;
- one AWQ fused or explicitly separate AWQ control target if backend recovery succeeds.

Raw7B and Llama are secondary to recovering these core data classes.
