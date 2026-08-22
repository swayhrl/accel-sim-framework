# C2P performance diagnosis and C2P+ plan

Status: analysis and experiment plan only.  It does not change the canonical
paper16 result or the currently running V100 baselines.

## Scope and evidence

The canonical result is the strict paper16 closeout under
`hw_run/c2p-paper16-analysis-final-v7-20260821/`.  The active C2P source
worktree is `/workspace/worktrees/gpgpu-sim-c2p-cache` at
`eff4467972ed7b3918b441c17dd258444ee3481f`; the qualified paper16 result
records the exact older backend/front-end binary hashes used for each replay in
`paper16_provenance.csv`.  No new conclusion below is merged into paper16.

The V100 extension is separately held in
`hw_run/c2p-v100-extension-execution-hold-20260822.md`.  It must never be
combined with paper16 because it has independently generated V100 traces and
candidate inputs.

## Observed facts

### Canonical paper16

| Observation | Evidence | Interpretation boundary |
|---|---|---|
| C2P produces 9.97M remote hits vs Ideal's 11.55M | `paper16_modes.csv` | It retains about 86% of realized Ideal opportunities; this does not prove equal latency behavior. |
| C2P IPC/L2-access geomean is 1.019/0.899; Ideal is 1.033/0.885 | same CSV | There is a real, but incomplete, C2P benefit overall. |
| R1S1 C2P IPC is 1.218 in the paper-style report | `c2p-paper16-report-final-v7-20260821.md` | This is directionally close to the paper's +23.5% target. |
| R0S1 C2P IPC is 0.954 and ATA/RING are 0.906/0.629 | report | The expected sharing-overhead direction exists locally. |
| R1S0/R1S1 C2P L2 access is 0.831/0.840 vs paper target 0.534/0.698 | report | Direction matches, magnitude remains weaker. |
| C2P records 14.66M miss-time Snapshot FPs and 0.105M FNs | `paper16_modes.csv` | Candidate over-inclusion dominates metadata classification; counts must not be read as a common-denominator error rate without the TP/TN table. |
| R1S0/R1S1 C2P probe-timeout rates are 0.320/0.187 | report Fig.12 table | Target-side contention or serial probing is material in the groups with opportunity. |
| SGEMM and 2DConvolution reduce L2 accesses but slow down | report outlier table | Performance is not explained by traffic reduction alone. |

The four-group IPC and L2 trends are therefore useful C2P mechanism evidence.
They do **not** establish a quantitative reproduction for every comparator:
RING's all-workload IPC geomean is 0.227 despite normalized L2 access 0.906.

### Existing V100 extension points

Completed V100 points are only evidence for their own candidate inputs:

| Case | C2P IPC | C2P L2/base | Ideal IPC | C2P / Ideal remote hit | Main implication |
|---|---:|---:|---:|---:|---|
| ISPASS BFS | 1.024 | 0.918 | 1.095 | 87,877 / 226,203 | Opportunity exists; current C2P discards many Ideal opportunities. |
| ISPASS LPS | 0.972 | 0.847 | 0.998 | 62,919 / 64,515 | C2P finds nearly all peers but protocol cost exceeds benefit. |
| ISPASS RAY | 1.015 | 1.000 | 1.011 | 0 / 0 | No sharing opportunity; IPC difference is not a C2P benefit claim. |
| ISPASS LIB | 1.000 | 1.000 | 1.000 | 0 / 0 | Compatibility-only negative control. |
| Pannotia fw_block | 1.005 | 0.991 | 1.006 | 9,134 / 9,478 | Very little opportunity; near-neutral result is expected. |

RING is likewise slow on these completed points (BFS/LPS/fw_block IPC
0.117/0.173/0.406).  That repeats the model concern; it is not evidence that
the C2P core is wrong.

## Code-path diagnosis

### C2P candidate/probe path

1. A global read L1 miss creates a transaction in
   `c2p_cache::accept_miss` (`src/gpgpu-sim/c2p-cache.cc:370-456`).
2. C2P intersects the tag-mask and Bloom rows for **every** peer endpoint,
   then sorts candidates nearest-first (`ordered_candidates`, lines 634-657).
3. One candidate at a time advances through `WAIT_TARGET_PROBE`, `WAIT_PROBE`,
   and either `WAIT_RETURN` or the next candidate (`advance_probes`, lines
   773-893).  This is a deliberate serial-pruning model, so false-positive
   tails multiply tag/queue latency.
4. A target probe enters a finite per-L1 FIFO and reserves the target's
   **data port** for the modeled remote-tag latency (`service_target_probe_queues`,
   lines 745-770; `l1_cache::c2p_reserve_probe_port` in `gpu-cache.h:1745-1747`).
   The paper states a remote tag latency, but does not state whether it shares
   an L1 data port.  This is a simulator assumption, not a proven paper fact.
5. A 32-cycle timeout sends the original request through L2, preserving
   forward progress but losing a possible remote hit (lines 805-887).

This makes the following diagnosis well supported, rather than speculative:

- **Candidate quality and protocol cost interact.** More candidates are not
  merely a filter-quality statistic; every false candidate can consume a
  serial probe slot and target-FIFO/data-port time.
- **Target data-port contention is a measured contributor, but not the whole
  cause.** In the existing diagnostic matrix, removing only target-port/FIFO
  contention improves Btree C2P IPC from 1.026 to 1.040 and SGEMM from 0.987
  to 0.998.  It cannot explain the full Ideal-to-C2P gap.
- **Increasing headroom alone is not a fix.** Btree's 256-entry/4096-cycle
  headroom experiment realizes 3.57x remote hits but takes 1.48x the default
  cycles.  It converts fallback into excessive waiting.
- **Bloom FP alone is not a monotonic optimization knob.** In the measured
  Btree Figure-13 sweep, m2048-k2 has FP ratio 0.503 and IPC 1.124, whereas
  default m5120-k4 is 0.245/1.026 and m9216-k5 is 0.053/1.007.  Changing
  row/hash shape also changes Snapshot query resource use and candidate timing.

### RING-like comparator

RING is intentionally modeled as a comparator rather than a reproduction of
unpublished RING RTL.  Two explicit model choices make its extreme slowdown
locatable:

- A full RING returns `MISS_STALL`, holding the L1 miss head rather than taking
  C2P's normal lower-L2 bypass (`accept_miss`, lines 378-384; documented in
  `c2p-cache.h:118-123`).
- All requests share `m_ring_next_issue_cycle`; traversal starts at the later
  of this global serialization point and the current cycle, then pays
  hop-distance times hop latency plus tag latency (`complete_matches`, lines
  717-735).

Thus the current RING result is evidence for this explicit serialized-ring
assumption, not a localized C2P bug.  It should stay out of claims that compare
absolute RING performance with the paper until its topology, injection width,
and full-queue policy are independently justified.

## Recommended C2P+ sequence

All variants below must be separate named modes or config overlays; the
canonical default C2P configuration and paper16 artifacts remain immutable.

### Stage A — observation only (first)

Add no behavior change.  Record, per transaction and aggregate:

- first successful probe ordinal and successful distance;
- probes spent before fallback, split by no-candidate, exhausted candidates,
  full FIFO, timeout, target-port busy, requester-fill wait;
- C2P transaction residence by state;
- RING admission-stall cycles, injection wait, hop distance, and traversal
  delay.

Directed check: default-off must be binary-equivalent to baseline; default C2P
must retain remote-hit == L2-requests-avoided and existing paper16 counters.

### Stage B — C2P+ bounded probe budget

Add an optional `c2p_cache_max_candidate_probes` (default `0` = current
unbounded behavior).  After the configured number of failed exact probes,
forward the original request to L2 and count a distinct `candidate_budget`
fallback.  This attacks long false-positive tails without pretending to make
the Snapshot more accurate.

Small validation set: Btree, SGEMM, 2DConvolution, LPS, plus NN as a
no-op control; budgets 1, 2, and 4.  Expected trade-off is lower probe/timeout
cost but potentially fewer remote hits.  Reject a point that violates request
ownership, lower-path single-send, or remote-hit/L2-avoid conservation.

### Stage C — separate remote-tag resource (counterfactual then model)

The existing `diagnostic_target_port_bypass` is an upper-bound diagnostic, not
an architectural result.  If Stage A confirms target data-port domination,
introduce an optional single remote-tag port per target L1: it has the existing
seven-cycle tag latency but does not reserve the data port.  Remote data return
and requester-fill contention remain unchanged.  This is plausible, but the
paper leaves it unspecified; label it `C2P+ separate-tag-port`, never replace
default C2P with it.

### Stage D — metadata choices only after A-C

Use the existing measured m/k sweep to choose a *candidate* point, but do not
select it from FP alone.  Score IPC, L2 reduction, candidates/query, probe
ordinal, timeouts, and update pressure together.  Any new Snapshot encoding or
adaptive candidate score must include its storage, bandwidth, and lookup
latency cost.

### Separate RING work

First add RING observability only.  A pipelined ring or lower-path fallback on
full injection is a new comparator (`RING+`), not a correction to C2P or a
paper-faithful RING claim.  It requires a separately stated topology contract
before performance comparisons.

## Decision rules

- Do not change the qualified paper16 aggregate for any C2P+ point.
- Do not interpret fewer L2 accesses as success without equal-or-better IPC,
  bounded waiting, and correct conservation counters.
- Do not claim a RING fix before the model's own backpressure and traversal
  costs are reported.
- Prefer Stage A, then the small Stage-B matrix, before a full workload sweep.
