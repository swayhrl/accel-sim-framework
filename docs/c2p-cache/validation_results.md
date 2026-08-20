# C2P core validation results

These are trace-driven functional/model checks, run with the C2P GPGPU-Sim
commit recorded in each run's `provenance.txt`.  They establish mechanism
behavior and directional trends; they are not a claim to reproduce the
manuscript's absolute IPC because its traces, exact hashes, topology, and
several queue/refresh parameters are unavailable.

| Trace and purpose | Baseline cycles | Ideal cycles | C2P cycles | C2P remote hits / L1 misses | Candidates/query | Result |
|---|---:|---:|---:|---:|---:|---|
| Rodinia BFS, full retained trace, broad-sharing stress | 122,048 | 120,321 | 123,018 | 936 / 14,474 | 6.50 | Exact peer sharing helps; deliberately high false-positive pressure makes Snapshot C2P slower, exercising probe-timeout and L2-fallback paths. |
| Rodinia DWT2D, full retained trace | 72,232 | 71,883 | 71,920 | 4,567 / 28,908 | 0.80 | R1S1-style positive case: 15.8% of eligible misses become remote hits and C2P improves cycles by 0.43%. |
| DWT2D, 64 SM / 64KiB 16-set interpretation | 71,844 | 71,448 | 71,678 | 4,520 / 28,908 | 0.79 | Paper-shaped sensitivity point: 15.6% L2 requests avoided and 0.23% cycle improvement. |
| Rodinia NN, full retained trace | 6,259 | 6,297 | 6,297 | 0 / 10,691 | 0.00 | No-sharing control: C2P's query-only cost is 0.61%; it does not inject remote probes. |
| Pathfinder, 1/40 CTA plus instruction-trim functional view | 75,165 | 75,561 | 75,517 | 0 / 36,229 | 0.79 | R0S1-style no-reuse functional proxy: zero oracle/remote hits; C2P cost is 0.47%. Not a performance result because the trace is intentionally trimmed. |
| Rodinia LUD, full retained trace | 457,133 | 457,270 | 457,931 | 819 / 130,432 | 0.30 | Full multi-kernel R1S1-style linear-algebra check. Snapshot pruning reduces ideal's 1,083 hits but bounds its overhead to 0.17%. |

`oracle_only` preserves the baseline cycle count in every listed run and
measures accept-time peer availability.  For example, DWT2D recorded 6,452
oracle peer hits (22.3% of eligible misses) on the QV100 configuration.  The
ideal and C2P modes can differ from that number because target-port contention,
late peer fills, and candidate pruning determine whether a request is actually
redirected.

For every completed remote hit, `c2p_l2_requests_avoided` equals
`c2p_remote_hits`: the original request is completed through its existing L1
MSHR/fill path and is never issued to the baseline L2 port.  This is the
model's redundant-L2-reduction measure.

The LUD run also caught and closed a lifecycle bug during validation: the
simulator flushes L1s between kernels, so C2P now clears that L1's Snapshot
column and discards queued updates for it.  Before the fix, stale bits from
earlier kernels inflated LUD candidates to about nine/query; after it, the
full retained run measures 27,969 candidates across 94,771 candidate queries.
