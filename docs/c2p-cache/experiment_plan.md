# C2P core experiment plan

The primary point is a credible directional reproduction, not an absolute
comparison to the paper.  Run each selected trace with `baseline`, `oracle`,
`ideal`, and `c2p` from `scripts/run_c2p_cache_cases.sh`.

## Reproduction criterion

This is intentionally **not** a cycle-by-cycle co-simulation of the original
RTL, nor can it establish the paper's exact numerical points without the
authors' trace inputs and address hashes.  A case is a useful reproduction
point when the following mechanism-level relationships are simultaneously
true and of a comparable order of magnitude to the paper's reported trends:

- `oracle` leaves the baseline timing unchanged; it measures opportunity only.
- `ideal` is an exact-discovery reference: every completed remote hit avoids
  exactly one L2 request.  It is an opportunity reference, not a strict
  performance upper bound, because it can create more peer-port pressure than
  a pruned C2P candidate set.
- finite C2P retains a substantial fraction of those remote hits; its
  candidate count and snapshot false-positive counters explain the difference
  from exact discovery.
- R1S1-like inputs show a measurable benefit, while R0S1-like inputs expose
  only bounded query/update overhead rather than a fabricated benefit.

The paper-level comparison targets are therefore recorded explicitly rather
than inferred after a workload finishes: it reports C2P R1S1 speedup of about
23.5% on average (up to 49.7%), and R0S1 changes of about -2.0% for C2P,
-31.7% for ATA, -19.3% for RING, and +0.4% for CCD.  Local retained traces
are not claimed to be the authors' inputs, so exact equality is not an
acceptance condition.  The required evidence is a consistent direction,
relative ordering, and explainable magnitude.  A material mismatch triggers
an investigation of trace/input class, L1/L2 geometry, partition/set mapping,
cluster scope, and remote-hit timing before any cycle-level tuning.

Consequently, when a result differs materially from the paper, investigate
first the configuration geometry, partition/set mapping, input/trace size,
and remote-hit eligibility.  Do not tune incidental pipeline timing merely to
force a matching cycle count.

The primary C2P configuration leaves no idle gap between per-SM Snapshot
column rebuilds. The paper describes continuously rebuilding one selected
column and then moving to the next; `100000` idle cycles per column would make
a 64-SM snapshot effectively insertion-only over typical traces and is not a
valid substitute for that background path.

The default trace configuration is the pinned Accel-Sim QV100 configuration.
Paper-table runs append `configs/c2p-cache/paper-table.config` and pass
`--strip-mem-addr-mapping` to the runner. The manuscript's L1 table
simultaneously says 64KiB, four sets, 32 ways, and 128B lines; those numbers
cannot all be true. We use the capacity-preserving interpretation, 16 sets by
32 ways by 128B, as the single primary point. Adaptive L1 resizing is disabled
so trace kernels cannot silently change this geometry.

Record for each mode:

- simulated cycles and IPC;
- `c2p_oracle_peer_hits / c2p_l1_misses` (redundant-L2 opportunity);
- `c2p_remote_hits / c2p_l1_misses` (realized remote hit rate);
- `c2p_candidate_total / c2p_candidate_queries`;
- C2P false-positive/false-negative and fallback counters.
- peer-L1 access-count P90/P95/P99/max split by completed remote-hit and
  fallback requests that actually consulted at least one peer L1. This is the
  direct local counterpart of the paper's Figure 14; average candidate bitmap
  width alone is not a substitute.

The existing trace inventory is grouped by the paper's reuse taxonomy where
provenance permits it.  The first core dataset is the locally retained
Rodinia/Parboil/PolyBench trace set; R1S1 is prioritized because C2P predicts
benefit while R0S1 establishes query overhead.  ATA/CCD/RING are run after a
core bundle completes; Pannotia and ISPASS remain unavailable without
compatible replay traces, and PPA remains outside this functional study.
