# C2P core experiment plan

The primary point is a credible directional reproduction, not an absolute
comparison to the paper.  Run each selected trace with `baseline`, `oracle`,
`ideal`, and `c2p` from `scripts/run_c2p_cache_cases.sh`.

The default trace configuration is the pinned Accel-Sim QV100 configuration.
For paper-shaped sensitivity runs, use both `paper-64sm-l1-16sets.config` and
`paper-64sm-l1-4sets.config`.  The manuscript's L1 table simultaneously says
64KiB, four sets, 32 ways, and 128B lines; those numbers cannot all be true.
The two configurations make that ambiguity explicit rather than silently
choosing one.

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
