# C2P core validation results

These are trace-driven functional/model checks, run with the C2P GPGPU-Sim
commit recorded in each run's `provenance.txt`.  They establish mechanism
behavior and directional trends; they are not a claim to reproduce the
manuscript's absolute IPC because its traces, exact hashes, topology, and
several queue/refresh parameters are unavailable.

## Current formal bundle

The current mechanism revision uses continuous per-column Snapshot rebuilds,
matching the paper's background operation. The completed Btree bundle is the
first full seven-mode result with this revision.

| Mode | Cycles | Speedup vs baseline | Remote hits | C2P-specific observation |
|---|---:|---:|---:|---|
| baseline | 252,592 | 0.00% | 0 | reference |
| oracle | 252,592 | 0.00% | 0 | 699,085 accept-time peer opportunities; timing invariant passes |
| ideal | 229,027 | 9.33% | 205,707 | exact peer discovery reference |
| C2P | 237,809 | 5.85% | 154,748 | 6.07 bitmap candidates/query; actual-probe hit P90/P95/P99 = 2/3/6 |
| ATA-like | 243,092 | 3.76% | 75,407 | 9,809,152 aggregate tag/data accesses |
| CCD-like | 252,861 | -0.11% | 0 | no effective predicted sharing |
| RING-like | 262,862 | -4.07% | 33,691 | serialized ring path loses to baseline |

This establishes the key Btree ordering `ideal > C2P > ATA > baseline ≈ CCD
> RING`, the same qualitative mechanism trend sought from the paper. It is
not a numerical match claim: the retained Btree input and simplified far-L1
network are not the authors' experimental setup.

## Current cross-workload campaign

All rows below are complete seven-mode bundles from the same continuous-refresh
revision and passed the strict oracle/remote-ownership checks. `mri-q` is the
retained Parboil MRI-Q variant; the paper labels the workload only as `mri`,
so it is intentionally kept separate from any future MRI-gridding result.

| Case | Baseline cycles | C2P change | C2P remote hits | Interpretation |
|---|---:|---:|---:|---|
| Btree | 252,592 | -5.85% | 154,748 | strong R1 sharing; C2P is ahead of ATA and RING |
| DWT2D | 76,093 | -1.81% | 4,381 | positive R1 case; C2P's pruned peer traffic can outperform exact discovery |
| LUD | 484,010 | -0.01% | 1,628 | peer opportunity does not necessarily translate to a visible speedup |
| Gaussian-16 | 173,970 | +0.10% | 0 | clean zero-opportunity R0 control |
| NN | 7,892 | -0.53% | 0 | zero-opportunity diagnostic; query timing changes lower-memory phasing, not a claimed benefit |
| Parboil MRI-Q | 367,150 | +0.27% | 0 | provisional `mri` R0 point; C2P is below ATA (+0.41%) and CCD (+0.45%) overhead |

For MRI-Q, RING costs +0.31%, only slightly above C2P despite the paper's
much larger R0S1 group-average RING penalty. The current RING comparator has
the specified hop/tag timings and injection serialization, but not a complete
far-L1 network/queue topology; this is an explicit remaining source of
quantitative mismatch, not a parameter to tune against one workload.

## Earlier diagnostics

The rows below predate the continuous-refresh revision unless explicitly
rerun. They remain useful for directed model debugging, but are not included
in the formal cross-workload comparison until reproduced with the current
revision.

| Trace and purpose | Baseline cycles | Ideal cycles | C2P cycles | C2P remote hits / L1 misses | Candidates/query | Result |
|---|---:|---:|---:|---:|---:|---|
| Rodinia BFS, full retained trace, broad-sharing stress | 122,048 | 120,321 | 121,106 | 974 / 14,474 | 0.82 | Exact sharing is stronger (1.42%); Snapshot filtering retains 6.7% of misses as real remote hits and still exposes target-port timeout/fallback behavior. |
| Rodinia DWT2D, full retained trace | 72,232 | 71,883 | 71,725 | 4,877 / 28,908 | 0.34 | Pre-continuous-refresh diagnostic; rerun pending before cross-workload use. |
| DWT2D, legacy 64-SM overlay | 71,844 | 71,448 | 71,431 | 4,890 / 28,908 | 0.33 | Superseded configuration record; do not compare this row with the paper. It left adaptive L1 resizing enabled and set L1 latency to 4 cycles. |
| Rodinia NN, full retained trace | 6,259 | 6,297 | 6,297 | 0 / 10,691 | 0.00 | Pre-continuous-refresh no-sharing diagnostic; rerun pending. |
| Rodinia Gaussian-16, full retained trace | 170,928 | 171,108 | 171,108 | 0 / 513 | 0.00 | Pre-continuous-refresh no-sharing diagnostic; rerun pending. |
| Rodinia Hotspot-512, full retained trace | 21,573 | 21,790 | 21,456 | 3,511 / 173,193 | 1.05 | Mixed case: 24.9% of accepted queries are false positives and 89,114 misses bypass the finite query queue, yet the 2.0% realized remote-hit rate gives a 0.54% cycle improvement. |
| Rodinia LUD, full retained trace | 457,133 | 457,270 | 457,931 | 819 / 130,432 | 0.30 | Full multi-kernel R1S1-style linear-algebra check. Snapshot pruning reduces ideal's 1,083 hits but bounds its overhead to 0.17%. |

`oracle_only` preserves the baseline cycle count in every listed run and
measures accept-time peer availability. For example, current DWT2D records
6,452 oracle peer hits across the baseline/oracle timing point (22.3% of
eligible misses); C2P records 6,372 because its query timing changes the
accept-time observation point. The ideal and C2P modes can differ from either
number because target-port contention, late peer fills, and candidate pruning
determine whether a request is actually redirected.

For every completed remote hit, `c2p_l2_requests_avoided` equals
`c2p_remote_hits`: the original request is completed through its existing L1
MSHR/fill path and is never issued to the baseline L2 port.  This is the
model's redundant-L2-reduction measure.

The current paper-table baseline is `configs/c2p-cache/paper-table.config`.
It uses a fixed 64KiB 16-set/32-way/128B L1 at 20 cycles, 64 SMs arranged as
eight clusters of eight, GTO scheduling, 20 memory partitions, and a 128-set
16-way L2 slice at 200 cycles. The original manuscript's L1 entry also says
four sets, which is incompatible with its stated 64KiB capacity and 32-way
associativity; this repository deliberately uses the capacity-preserving
interpretation. The legacy DWT row above predates this correction.

The LUD run also caught and closed a lifecycle bug during validation: the
simulator flushes L1s between kernels, so C2P now clears that L1's Snapshot
column and discards queued updates for it. Before the fix, stale bits from
earlier kernels inflated LUD candidates to about nine/query; after it, the
full retained run measures 27,969 candidates across 94,771 candidate queries.

The primary result bundles report the paper's miss-time Snapshot TP/TN/FP/FN
and separate no-candidate, candidate-exhaustion, probe-timeout, and queue
fallbacks. They additionally report `snapshot_query_*` counters, which
classify the same candidate bitmap against exact peer residency when the
metadata query completes. This second truth table exposes fills/evictions
while a miss waits in C2P without changing the paper-comparable miss-time
classification.
