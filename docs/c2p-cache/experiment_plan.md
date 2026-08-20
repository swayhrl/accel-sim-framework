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
- `ideal` converts eligible redundant L2 accesses into remote hits and avoids
  the same number of L2 requests.
- finite C2P retains a substantial, but no larger than ideal, fraction of
  those remote hits; its candidate count and snapshot false-positive counters
  explain the difference.
- R1S1-like inputs show a measurable benefit, while R0S1-like inputs expose
  only bounded query/update overhead rather than a fabricated benefit.

Consequently, when a result differs materially from the paper, investigate
first the configuration geometry, partition/set mapping, input/trace size,
and remote-hit eligibility.  Do not tune incidental pipeline timing merely to
force a matching cycle count.

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

The existing trace inventory is grouped by the paper's reuse taxonomy where
provenance permits it.  The first core dataset is the locally retained
Rodinia/Parboil/PolyBench trace set; R1S1 is prioritized because C2P predicts
benefit there, while R0S1 establishes query overhead.  Pannotia and ISPASS,
ATA/CCD/RING comparisons, and PPA remain deferred by scope.
