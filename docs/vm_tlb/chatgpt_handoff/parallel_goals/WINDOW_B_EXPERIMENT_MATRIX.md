# Window B experiment matrix

Status: **AUTHORIZED SPECULATIVE MATRIX**.

All sweeps are one-factor-at-a-time around the accepted generic-M3 real-PTW baseline unless the row explicitly names the paper-platform shell. Each `ROI × config` is one continuous simulator process.

## Baseline reference

- page size: 64KB
- L1 TLB: 32 entries, fully associative
- L2 TLB: 768 entries, 16-way
- translation MSHR: 32
- PWQ: 32
- walkers: 16
- PWC: FINITE-128
- L1/L2 TLB service: 10/80 cycles
- real PTE L2/DRAM path
- 49-bit VA for the accepted formal traces

## B2 VM sweep

| Family | Values | Baseline value |
| --- | --- | --- |
| L1 TLB entries | 16, 32, 64, 128 | 32 |
| L2 TLB entries | 128, 256, 512, 768, 1536, 3072 | 768 |
| Translation MSHR entries | 8, 16, 32, 64, 128 | 32 |
| PWQ entries | 8, 16, 32, 64 | 32 |
| Walkers | 1, 4, 8, 16, 32 | 16 |
| PWC | OFF, FINITE-32, FINITE-128, FINITE-512, IDEAL | FINITE-128 |
| Page size | 64KB, 2MB diagnostic where valid | 64KB |
| Translation control | VM disabled, ideal identity, real-PTW baseline | real-PTW |

Generate deduplicated configs: the baseline should not be rerun once per family unless a fresh provenance/check is intentionally desired.

For each config:

1. config validator;
2. bounded smoke on decode1 and prefill representative traces;
3. if valid, full decode1 continuous ROI;
4. if valid and slots permit, full prefill continuous ROI;
5. terminal invariant/telemetry summary.

The user has accepted that these full speculative runs may need rerun after C4 review.

## B3 cache sweep

Use the paper-platform shell for the primary cache-capacity family so the 3MB baseline has a clear reference, while retaining standard/non-subentry translation semantics.

### L1D capacity

Target capacities:

- 32KB
- 64KB
- 128KB baseline
- 256KB

For every config, compute and assert realized capacity from cache geometry. Do not assume `-gpgpu_unified_l1d_size` alone changes effective geometry.

### Data L2 capacity

Target total capacities:

- 1.5MB
- 3MB baseline
- 6MB
- 12MB

Keep line size and associativity fixed when practical; vary sets/partition geometry in a valid way. Record exact realized total and per-subpartition capacity.

### L2 associativity

- 8-way
- 16-way baseline
- 32-way

Hold total capacity as close to 3MB as the simulator configuration permits; if exact capacity cannot remain fixed, report the realized geometry and do not claim pure associativity isolation.

### L1D bypass

- normal L1D
- global-memory L1D bypass control

## B5 TLB × L2 grid

After the single-factor rows are available:

| L2 TLB entries \ L2 capacity | 1.5MB | 3MB | 6MB |
| --- | --- | --- | --- |
| 256 | run | run | run |
| 768 | run | baseline | run |
| 1536 | run | run | run |

Run prefill and decode1 separately.

## B4 non-LLM matrix

For every compatible selected workload:

- VM ideal identity;
- generic real-PTW / L2 TLB 256;
- generic real-PTW / L2 TLB 768;
- generic real-PTW / L2 TLB 1536.

Candidate applications are not hard-coded as valid. Inventory and prove trace/config compatibility first. Prefer diversity across graph, dense linear algebra, sparse, stencil/convolution, and irregular memory access.

## Required metrics for simulator sweeps

At minimum:

- cycles, instructions, IPC;
- L1/L2 TLB hit/miss/port stalls;
- MSHR alloc/merge/full/high-water;
- PWQ full/wait;
- walker starts/high-water;
- PWC hit/miss;
- PTE requests/L2-only/DRAM;
- requester translation latency/wait;
- Weight/KV/UNKNOWN split when object maps exist;
- L2-TLB replacement matrix;
- L1D/L2 cache outcomes;
- PTE/data L2 request class and replacement;
- DRAM and native memory-system stats;
- cross-layer translation × L1D × L2 matrices;
- wall time/RSS/host throughput for farm scheduling.

## Interpretation rule

A sensitivity curve is informative even when it contradicts the current hypothesis. Do not tune away unexpected results. Flag non-monotonic or surprising results for replay/diagnostic validation, then retain them if reproducible.
