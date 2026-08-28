# C2P-Cache redundant-L2 locality diagnostic — audited result

Date: 2026-08-29  
Scope: the 16 locally compatible paper workloads, plus the requested six-case
L1 geometry study.  This is a diagnosis of redundant L2 opportunity, not a
claim of cycle-for-cycle reproduction of the C2P-Cache paper.

## Qualification and provenance

The final link-only audit root is:

```text
hw_run/c2p-peer-locality-audit-20260829-v2/
```

Its generated result files are:

```text
analysis/stage_totals.csv
analysis/all_workloads.csv
analysis/geometry_comparison.csv
analysis/current64_vs_paper_fig3_inferred.csv
current64-assembled/analysis/{invariant_report.md,diagnostic_summary.csv,
  event_semantics.csv,cluster_locality.csv,peer_count_hist.csv,
  peer_distance_hist.csv,run_audit.csv}
```

| Stage | Workloads | Qualification |
|---|---:|---|
| current64 (`16 x 32 x 128 B = 64 KiB`) | 16 | 16 PASS / 0 FAIL / 0 missing |
| literal16k (`4 x 32 x 128 B = 16 KiB`) | 5 | 5 PASS / 0 FAIL / 0 missing |
| fourset64k (`4 x 128 x 128 B = 64 KiB`) | 6 | 6 PASS / 0 FAIL / 0 missing |

`literal16k/Gaussian` is deliberately absent from the five valid geometry
cells.  It is the separately reproduced and documented literal-configuration
baseline deadlock, therefore it is an **invalid geometry point**, not zero
redundancy and not an architectural result.

Every selected run exited normally and passed all of the following:

- 64 L1 instances were registered;
- accepted L1 misses split exactly into new lower requests and MSHR merges;
- each new lower request has exactly one detect and one physical-issue record;
- no detect record remains pending and none is missing at issue;
- sector/line histograms, peer-count bins, cluster classes, signed-distance
  bins and nearest/all-distance bins each satisfy their conservation equations.

The 16-cell provenance manifest records a common GPGPU-Sim commit
`f0724ce9`, resolved configuration SHA-256, copied simulator SHA-256 and
CUDART SHA-256; only the trace SHA differs by workload as intended.  Framework
commits vary only between known ancestors carrying campaign/documentation
changes; they are retained per cell and are *not* used as an executable
equivalence key.  The compiled simulator and resolved configuration are
identical.  This distinction is enforced by
`scripts/assemble_c2p_peer_locality_stage.sh`.

## Pure-observation control

The switch defaults to zero.  The detect and issue hooks return before peer
scanning unless `-c2p_cache_peer_locality_diagnostic 1` is explicitly set.

An additional NN oracle replay compared the same configuration with the switch
off and on.  It is stored in:

```text
hw_run/c2p-peer-locality-audit-20260829-v2/purity-control-nn/{off,on}/oracle/
```

| Metric | off | on |
|---|---:|---:|
| `gpu_tot_sim_cycle` | 7,206 | 7,206 |
| `gpu_sim_insn` | 1,284,872 | 1,284,872 |
| L2 total accesses | 16,037 | 16,037 |
| L2 global reads | 10,691 | 10,691 |
| `c2p_l1_misses` | 10,691 | 10,691 |
| `c2p_oracle_peer_hits` | 0 | 0 |

Thus this dynamic control, in addition to the default-off code path, supports
the intended claim that locality collection does not change cache state,
routing, timing, or completion behavior.

## Current 64 KiB result: denominator and timing

The actionable denominator is physical lower-read issue, rather than all L1
miss accepts:

| Current64 aggregate | Count / rate |
|---|---:|
| accepted eligible L1 misses | 184,751,903 |
| MSHR merges excluded from physical lower demand | 65,317,417 |
| physical lower issues | 119,434,486 |
| issue-time exact-sector redundant requests | 17,023,535 (14.253%) |
| issue-time resident-line redundant requests | 20,848,324 (17.456%) |
| mean detect-to-issue wait | 3.682 cycles |
| maximum detect-to-issue wait | 51 cycles |

The resident-line view is the closer proxy for the paper's tag-residency
definition.  Its 3.202 percentage-point aggregate gap above the exact-sector
view measures the effect of this Accel-Sim L1 sector model: a peer can retain
the line tag while not owning the requested sector.

Across the 16 workloads, 104,204 requests transitioned from no exact peer at
detect to an exact peer at issue, while 95,004 went in the reverse direction.
This directly demonstrates why the issue-time sample must not be replaced by
an earlier cache-access sample.

The legacy `c2p_oracle_peer_hits` counter is sampled in `accept_miss()`, not at
physical lower issue.  It is now reported separately as
`issue_sector_minus_oracle_accept_hits`, rather than used as an invalid equality
gate.  The aggregate delta is -36 and comes solely from 3mm; this is a small
accept-versus-issue timing difference, not an accounting failure.

## Comparison with the conditionally inferred Fig. 3 reference

The paper plot does not publish a keyed numeric workload table.  The reference
used below is the previously archived vector-position inference; all identity
assignments are conditional, and GESUMMV is explicitly a synthetic placement.
Therefore this table identifies discrepancies worth explaining; it does not
assert that the inferred coordinate is a ground-truth paper measurement.

| Workload | issue exact % | issue line % | inferred paper R % | exact − paper (pp) | line − paper (pp) |
|---|---:|---:|---:|---:|---:|
| MRI-q | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| Nearest Neighbor | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| DWT2D | 9.06 | 11.30 | 15.38 | -6.32 | -4.08 |
| CUTCP | 91.29 | 91.66 | 97.33 | -6.04 | -5.67 |
| Hotspot | 30.04 | 75.29 | 63.77 | -33.73 | +11.52 |
| Gaussian | 7.94 | 64.14 | 89.08 | -81.14 | -24.94 |
| ATAX | 0.19 | 0.64 | 1.18 | -0.99 | -0.54 |
| BICG | 0.17 | 0.62 | 1.59 | -1.42 | -0.97 |
| GESUMMV* | 0.17 | 0.58 | 0.66 | -0.49 | -0.08 |
| LUD | 25.20 | 56.17 | 93.17 | -67.97 | -37.00 |
| SGEMM | 41.01 | 45.60 | 82.99 | -41.98 | -37.39 |
| 3mm | 35.65 | 38.35 | 89.12 | -53.47 | -50.77 |
| GEMM | 36.85 | 40.20 | 89.66 | -52.81 | -49.46 |
| B+tree | 43.40 | 48.34 | 49.27 | -5.87 | -0.93 |
| 2DConvolution | 33.90 | 67.60 | 47.10 | -13.20 | +20.50 |
| Stencil | 33.18 | 33.18 | 36.28 | -3.10 | -3.10 |

`*` GESUMMV's inferred paper position is intentionally non-evidentiary.

The sector-versus-line distinction resolves a substantial part of the mismatch
for Gaussian (+56.00 pp), Hotspot (+45.26 pp), 2DConvolution (+33.70 pp) and
LUD (+30.97 pp), but it does **not** close the large 3mm, GEMM or SGEMM gaps.
It is therefore a necessary explanation, not a sufficient one.

## L1 geometry sensitivity

All entries are issue-time exact-sector redundant rates.  Parentheses are
percentage-point differences from the current 16-set 64 KiB configuration.

| Workload | current64 | literal 16 KiB | four-set 64 KiB |
|---|---:|---:|---:|
| Hotspot | 30.04% | 19.47% (-10.57) | 31.44% (+1.40) |
| Gaussian | 7.94% | invalid baseline deadlock | 7.90% (-0.04) |
| LUD | 25.20% | 27.00% (+1.81) | 11.85% (-13.34) |
| SGEMM | 41.01% | 35.22% (-5.80) | 40.55% (-0.46) |
| 3mm | 35.65% | 25.26% (-10.39) | 55.36% (+19.70) |
| GEMM | 36.85% | 26.48% (-10.36) | 50.84% (+14.00) |

The literal 16 KiB experiment usually *reduces* opportunity and therefore does
not reconcile the large paper gaps.  Holding capacity at 64 KiB but changing
the set/way geometry has a material, workload-dependent effect: especially
3mm and GEMM increase by 19.70/14.00 pp, while LUD decreases by 13.34 pp.
This proves that conflict/indexing geometry is a major contributor for some
workloads.  It cannot be reduced to a single L1-capacity explanation, and it
does not make the current configuration equivalent to the paper.

## Locality and copy multiplicity

The requested eight-SM groups are **logical statistics only**:
`cluster(sid) = floor(sid / 8)`.  They are not a physical far-L1 latency
measurement in the current one-endpoint-per-SM topology.

For the 17,023,535 issue-time exact-sector redundant requests:

| Class | Requests | Fraction conditional on redundancy |
|---|---:|---:|
| copies only in requester's logical cluster | 4,123,884 | 24.22% |
| copies only outside it | 8,088,112 | 47.51% |
| copies in both regions | 4,811,539 | 28.26% |

There are 16,907,216 local peer copies and 52,220,857 outer peer copies; only
24.46% of all observed copies are local-cluster copies.  Nearest-peer logical
SID distance is 1 for 22.67% of redundant requests and 2–7 for 43.06%; its
mean is 8.95.  Hence 65.74% have a nearest copy within absolute SID distance
seven, while a large fraction still has outer-only availability.  This is
useful evidence that request placement/SM mapping matters, but it is not yet
proof of a physical network cause.

Peer-count distribution across all lower issues is 85.75% no exact peer,
6.29% exactly one peer, 3.06% two to three peers, 2.71% four to seven peers,
1.64% eight to fifteen peers, and 0.55% at least sixteen peers.

## Attribution conclusion

The evidence supports the following ordered conclusion.

1. **No locality-accounting implementation defect is currently indicated.**
   The default-off control is behaviorally identical on NN; all 27 valid
   stage/workload cells pass detect/issue and every histogram conservation
   gate; executable provenance is common.  The one 3mm legacy-oracle delta was
   traced to deliberately different sampling times and is now reported rather
   than misclassified as a failure.
2. **Statistical semantics are a demonstrated contributor.**  Paper-like line
   residency can be far above immediately usable requested-sector availability.
   Any claim based only on the old L1-miss or accept-time oracle counters would
   conflate MSHR coalescing and queue timing with physical lower-read demand.
3. **L1 set geometry is a demonstrated contributor.**  Same-capacity geometry
   moves 3mm, GEMM and LUD by double-digit percentage points in different
   directions.  The paper's stated L1 capacity/geometry ambiguity must remain
   explicit; neither tested interpretation makes all workloads match.
4. **Trace placement/topology/scheduling remains a plausible but unproven
   residual cause.**  The logical local/outer and distance measurements show
   substantial non-local availability.  A topology/scheduler sensitivity is
   required before attributing the remaining gap to the far-L1 network rather
   than to trace mapping.
5. **The inferred paper plot bounds the comparison.**  Its workload identity
   is conditional and its GESUMMV point is synthetic.  The audited local
   numeric data are definitive for this campaign; the inferred paper numbers
   are diagnostic context only.

## Reproduction commands

The finalizer is intentionally strict and may be run on a fresh audit root
whose `current64`, `current64-extra`, `literal16k`, and `fourset64k` entries
are link-only references to completed stage roots:

```bash
scripts/finalize_c2p_peer_locality_campaign.sh \
  --root hw_run/c2p-peer-locality-audit-20260829-v2 --poll-sec 1
```

The command is non-destructive for source stages and refuses partial/failed
cells.  Re-running in the same output root is intentionally rejected; create
a fresh link-only audit root for another audit pass.
