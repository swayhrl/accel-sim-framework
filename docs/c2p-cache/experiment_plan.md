# C2P core experiment plan

The primary point is a credible, auditable **mechanism-and-trend**
reproduction, not merely a set of completed replay jobs or an absolute
cycle-by-cycle comparison to the paper.  The canonical campaign is the 16 complete local
traces listed in `configs/c2p-cache/paper16_workloads.tsv`; run each with
`baseline`, `oracle`, `ideal`, `c2p`, `ata`, `ccd`, and `ring` through
`scripts/run_c2p_paper16.sh`.  A second baseline-only replay at 50-cycle L2
latency supplies the independent S0/S1 classification input.

## Reproduction criterion and completion gates

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
- CCD and C2P miss-time TP/FN/FP/TN, each measured against its own exact
  tag-time candidate snapshot; this is the local counterpart of Figure 12.
- Figure 13 is a distinct C2P-only sweep: vary Snapshot BF rows per bank and
  BF-hash count, bin the *measured* system FP ratio, and plot median IPC with
  its 25th--75th percentile band.  A single default C2P point is not Figure
  13 evidence.
- peer-L1 access-count P90/P95/P99/max split by completed remote-hit and
  fallback requests that actually consulted at least one peer L1. This is the
  direct local counterpart of the paper's Figure 14; average candidate bitmap
  width alone is not a substitute.

The campaign is not complete until all four gates below have passed.  This
prevents a successful workload exit, or a visually plausible plot, from being
mistaken for a reproduction result.

1. **Complete and provenance-pinned evidence.**  Every retained case has all
   seven performance modes, its independent 50-cycle baseline, and a
   same-config CCD classification replay.  Each result retains the resolved
   configuration, trace/config/binary hashes, simulator log, and summary.
2. **Mechanism invariants.**  Oracle remains timing-observational; every
   realized remote hit avoids exactly one lower-L2 request; C2P/CCD TP, FN, FP,
   and TN use their own exact miss-time reference; and the default parameterized
   Snapshot implementation is regression-equivalent to the original default.
3. **Trend and magnitude review.**  The R0/R1 and S0/S1 grouping comes only
   from the independent replay.  For every Figure-10--14 observation, compare
   direction, relative ordering, and order of magnitude with the paper.  A
   material disagreement is a failed investigation item: identify whether it
   arises from the local trace/input, geometry/mapping, remote-hit timing,
   comparator model, or an implementation defect.  Do not tune incidental
   cycle timing merely to manufacture agreement.
4. **Figure fidelity and auditability.**  Publish both vector (PDF/SVG) and
   raster (PNG) figures using the paper's panel organization, group order,
   axis semantics, palette, hatch/marker/line conventions, legend order,
   separator treatment, and percentile-band presentation.  Keep a concise
   per-figure style-and-data mapping beside the plots.  A plot with different
   colors or an arbitrary layout is a diagnostic chart, not the paper-style
   reproduction figure.

The primary objective is therefore revised to: **complete these four gates on
the 16 compatible traces, then issue a final report that distinguishes
confirmed paper-consistent trends, explainable model/input differences, and
unresolved discrepancies.**  The unavailable ISPASS and Pannotia eight
workloads remain explicit missing evidence, rather than being silently
replaced by similar local applications.

The existing trace inventory is grouped by the paper's reuse taxonomy after
the 50-cycle replay completes.  The local core dataset is the retained
Rodinia/Parboil/PolyBench trace set; R1S1 is prioritized because C2P predicts
benefit while R0S1 establishes query overhead.  The unavailable ISPASS and
Pannotia eight workloads are recorded as explicit missing evidence, never
replaced by merely similarly named traces.  PPA and the broader Figure 16--21
parameter study remain outside this functional study.
