# C2P core validation results

These are trace-driven functional/model checks, run with the C2P GPGPU-Sim
commit recorded in each run's `provenance.txt`.  They establish mechanism
behavior and directional trends; they are not a claim to reproduce the
manuscript's absolute IPC because its traces, exact hashes, topology, and
several queue/refresh parameters are unavailable.

| Trace and purpose | Baseline cycles | Ideal cycles | C2P cycles | C2P remote hits / L1 misses | Candidates/query | Result |
|---|---:|---:|---:|---:|---:|---|
| Rodinia BFS, full retained trace, broad-sharing stress | 122,048 | 120,321 | 121,106 | 974 / 14,474 | 0.82 | Exact sharing is stronger (1.42%); Snapshot filtering retains 6.7% of misses as real remote hits and still exposes target-port timeout/fallback behavior. |
| Rodinia DWT2D, full retained trace | 72,232 | 71,883 | 71,725 | 4,877 / 28,908 | 0.34 | R1S1-style positive case: 16.9% of all L1 misses are completed remotely and C2P improves cycles by 0.70%. |
| DWT2D, legacy 64-SM overlay | 71,844 | 71,448 | 71,431 | 4,890 / 28,908 | 0.33 | Superseded configuration record; do not compare this row with the paper. It left adaptive L1 resizing enabled and set L1 latency to 4 cycles. |
| Rodinia NN, full retained trace | 6,259 | 6,297 | 6,297 | 0 / 10,691 | 0.00 | No-sharing control: C2P's query-only cost is 0.61%; it does not inject remote probes. |
| Rodinia Gaussian-16, full retained trace | 170,928 | 171,108 | 171,108 | 0 / 513 | 0.00 | Second no-sharing control: no Snapshot candidate or peer probe is produced; the 0.11% cost is strictly miss-path query overhead. |
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

The current result bundles additionally report query-time Snapshot TP/TN/FP/FN
and separate no-candidate, candidate-exhaustion, probe-timeout, and queue
fallbacks.  The C2P model now compares Snapshot candidates against an exact
peer probe at the later metadata-query instant; this keeps ordinary peer
fills/evictions between miss acceptance and query completion out of the
metadata-accuracy counter.  Earlier archived TP/TN/FP/FN totals used the
accept-time oracle and are retained only as historical diagnostics, not as
cross-run accuracy data.
