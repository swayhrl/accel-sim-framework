# CODEX SIDE GOAL OVERRIDE — 109 V2.1 Post-Checkpoint Priority Refinement

Date: 2026-09-19

Status: ACTIVE AFTER CHECKPOINT 1.

This does not start a new campaign. It refines only the remaining queue of the same V2.1 campaign.

## 0. Preserve current work

Finish the currently selected native timing-stability phase normally.

Do not interrupt an active NSYS run.

Checkpoint 1 is already remote-verified at:

`34760124c894fd23175b9961d46f2e8ca2e5a0c7`

Do not rewrite it.

## 1. High-value optional native follow-up before lower-priority cross-model work

After timing stability, check remaining time against:

`no_new_gpu_target_after_utc`

If at least **45 minutes** remain, run a bounded cache-controlled native reconnaissance extension before cross-model census.

Classification remains:

`RECONNAISSANCE_ONLY`

### 1A. Motivation

Checkpoint 1 shows:

- default-load single-chain median is 52 cycles/load through 512 touched locations;
- a strong default-load knee appears at 512->1024 locations across all tested strides;
- `cg` at 512/1024 locations is already around ~293-303 cycles/load and largely removes the 52-cycle plateau;
- warm-repeat versus intervening-thrash medians are close at the sampled points.

Therefore the largest default-load knee is strongly confounded by data-cache behavior and must not be assigned to a TLB level.

### 1B. Targeted `cg` matrix

Use the already qualified same dependent-chain harness and the existing explicit `cg` load-policy path.

Sweep:

```text
stride:
  4 KiB
  64 KiB
  256 KiB
  2 MiB

locations:
  256
  512
  768
  1024
  1536
  2048
```

Use one dependent chain / one active warp.

For every point:

- same dependent-load count;
- pre-touch;
- warmup;
- >=50 samples when practical;
- median/p10/p90/min/max;
- exact allocation span;
- touched-line count;
- source/binary SHA unchanged from accepted harness.

Keep one touched cache line per chain node.

The purpose is to hold touched-line count comparable across strides while changing virtual-address span / likely translation footprint.

Do not allocate >50% of device memory at one point.

### 1C. Small repeatability subset

If >=20 minutes remain after 1B, repeat in two extra process launches:

```text
stride 4 KiB: 512, 1024, 2048
stride 64 KiB: 512, 1024, 2048
stride 2 MiB: 512, 1024, 2048
```

Report cross-process CV.

### 1D. Interpretation boundary

Allowed:

- `cg` cache-controlled latency surface;
- stride-sensitive or location-sensitive candidate knees;
- comparison against default-load surface.

Forbidden:

- pure L1/L2 TLB latency assignment;
- changing simulator 10/80;
- claiming `cg` perfectly isolates translation;
- treating an allocation stride as a proven hardware page size.

If the `cg` surface remains dominated by broad latency plateaus without clean stride-dependent separation, record:

`CACHE_CONTROLLED_NATIVE_TLB_RECON_STILL_AMBIGUOUS`

That is a useful result.

## 2. Decode Flash structural interpretation to carry into final report

Checkpoint 1 already covers all requested Primary-1/Primary-2 temporal and 2D cells.

The final campaign report should explicitly quantify:

### Primary-1

- memory-instruction count is invariant across all sampled step/occurrence cells;
- lane-address count is occurrence-invariant at a fixed step and grows gradually with decode step;
- 4KiB page footprint grows modestly with step;
- 64KiB page footprint is essentially flat;
- dynamic non-memory record count varies slightly by occurrence.

### Primary-2

- dynamic records, memory instructions and lane addresses are effectively invariant across all sampled step/occurrence cells;
- page footprint remains tiny and nearly invariant.

Do not equate occurrence with transformer layer.

Do not infer simulator-performance equivalence from structural invariance.

## 3. Final-pack packaging correction

Checkpoint 1 has a correctness-neutral packaging duplication:

```text
DECODE_FLASH_TEMPORAL_MATRIX.tsv
DECODE_FLASH_TIME_DEPTH_PARTIAL_MATRIX.tsv
RAW_DATA_INDEX.tsv
```

resolve to the same content/blob in the checkpoint pack.

Do not rewrite Checkpoint 1 history.

For the **final campaign review pack**:

- build a true `DECODE_FLASH_TEMPORAL_MATRIX.tsv` containing only temporal rows;
- build a true `DECODE_FLASH_TIME_DEPTH_MATRIX.tsv` containing the full 2D cells;
- build a true `RAW_DATA_INDEX.tsv` with artifact/run/path/hash indexing;
- give each its own semantic schema and independently verified SHA.

This is packaging repair only; do not alter accepted run evidence.

## 4. Remaining queue

After timing stability and optional targeted `cg` follow-up:

- only then consider cross-model census if time remains;
- do not sacrifice finalization reserve;
- no new large simulator-native target after the existing no-new-target deadline.

Final campaign closeout rules remain unchanged.
