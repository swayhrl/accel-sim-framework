# EP-L2 ChatGPT Review — Final Target Baseline Interim 22/26

Status: **CONDITIONAL PASS FOR CONTINUING THE FOUR LIVE RUNS.**

Do not stop, rebuild, restart, or otherwise disturb the four currently running formal jobs (`gemm` Legacy/Banked and `3mm` Legacy/Banked).

This review is based on the coordination-branch interim pack:

```text
docs/ep_l2/review_packs/TARGET_BASELINE_FINAL_INTERIM_22OF26_r1/
```

The completed 22 runs are internally consistent enough to continue the campaign. The items below must be resolved before final `TARGET_BASELINE_26RUN_PASS`, but none currently requires invalidating or rerunning the completed 22 runs unless the requested source/cardinality audit discovers an actual producer defect.

## 1. Interim provenance / run validity

PASS at artifact level:

```text
22/26 COMPLETE_VALID
normal exits
terminal_clean = 1
payload consistency = 1
one declared Core SHA
one declared Framework SHA
one runtime-config composite hash
required parsed artifacts present
```

Declared formal source pair:

```text
Core      ece1a3a77c5628763e0a4605bfd1c639ee6a1495
Framework f08d2ce857972fad73c4e1ab7162ba94c6336507
```

## 2. Blocking reviewability issue: push the exact final source commits/branches

The two declared final C7e SHAs are not currently resolvable from the GitHub remotes available to ChatGPT. The coordination branch contains the result/review documentation, but not the exact source commits used by the formal runs.

This does **not** invalidate the already-running local campaign, but final independent review requires the exact source objects.

Without rebuilding or touching runtime directories, push the exact existing commits used by the campaign to stable remote branches, e.g.:

```text
Core      hrl/ep-l2-c7e-final-char-v0
Framework hrl/ep-l2-c7e-final-char-v0
```

The pushed branch tips must equal exactly the declared formal SHAs. Do not create new source commits merely to publish the branches.

Also publish/link the retained C7e readiness evidence (build/regressions, OFF/ON timing neutrality, host overhead, runner SHA fail-fast) so ChatGPT can verify why target mode crossed `READY_FOR_FINAL_26_RUN`.

## 3. Interim research result: shared 256-descriptor pool is a major target pressure point

The current data strongly supports the following **pressure** observation, not yet a performance-causality claim:

```text
vectorAdd_4M   descriptor block/need ~= 68.5%
scan           descriptor block/need ~= 72.3%
spmv           descriptor block/need ~= 47.9%
convolution    descriptor block/need ~= 57.5%
FWT_7_21       descriptor block/need ~= 49.4%
FWT_11_19      descriptor block/need ~= 47.7%
```

For these workloads Line-MSHR-full remains zero while descriptor occupancy reaches 256 (Line-MSHR maxima remain below 128). This is exactly the structural distinction C7e was intended to expose.

Important: do **not** yet claim the 256-descriptor pool is the dominant performance cause. After final baseline closeout we should run a small 256->512 descriptor sensitivity on representative descriptor-heavy workloads before building an EP-L2 benefit claim on this pressure point.

### Small correction to interim text

`cfd_097k` Legacy also reaches descriptor max 256 and records 64 descriptor-pool-full blocks, while Banked reaches 251 and records zero. This is weak/transient, not one of the six strong descriptor-pressure cases. Update the wording so it distinguishes:

```text
strong/sustained descriptor-pressure workloads
```

from:

```text
any variant with a nonzero descriptor-full observation
```

## 4. Old btree/sgemm fixed-merge story is behaving as expected under the new shared pool

Current evidence:

```text
btree:
  descriptor max = 253
  descriptor-pool-full = 0
  32/address-cap block = 674

sgemm:
  descriptor max = 120
  descriptor-pool-full = 0
  32/address-cap block = 1,409

spmv:
  32/address-cap block = 8,598
```

So the old fixed 4-target fragmentation has largely disappeared. The 32/address cap is measurable but much weaker than the global descriptor pressure in the descriptor-heavy workloads.

## 5. Tag/set is not a broad primary target bottleneck

Only `scan` shows material nonzero Tag-way all-reserved blocking:

```text
tag-way alloc block = 222,849
tag-way alloc need  = 24,712,819
ratio ~= 0.90%
```

This is real but weak relative to its demand. The other completed workloads report zero Tag-way block.

## 6. WAD pressure is real and heterogeneous

Notable examples:

```text
scan:
  WAD full    = 2,318,944
  WAD hazard  =   585,398

dwt2d:
  WAD full    = 74,044
  WAD hazard  = 19,521

FWT_7_21:
  WAD hazard  = 286,123

convolutionSeparable:
  WAD full    = 8,266

cfd_097k:
  WAD hazard ~= 9.4K
```

This is worth retaining as a later WAD/TVD motivation candidate, but requires sensitivity/shadow evidence before a causal performance claim.

## 7. Correct the payload-service statement

The current `INTERIM_RESEARCH_FINDINGS.md` says all completed pairs have zero payload capacity **and service-port** denials. The comparison CSV shows this is not exactly true.

Correct statement:

```text
Payload-capacity allocation denials are zero in all completed runs.

B0-Banked payload service-port denials are zero in all completed runs.

B0-Legacy has small nonzero service-port denials in at least:
  cfd_097k = 488
  sad      = 2
```

This is useful attribution: in `cfd_097k`, Banked removes the Legacy service-port denial but introduces 16,166 true bank-conflict ops/wait cycles and is ~2.37% slower overall.

Do not change simulator results; fix only the interim/final analysis wording.

## 8. C6d B0-Banked result is strong

Among the 11 completed pairs:

```text
10/11 completed workloads:
  Banked cycles == Legacy cycles
  measured true bank conflict = 0

cfd_097k:
  Legacy = 79,555 cycles
  Banked = 81,443 cycles
  slowdown ~= 2.37%
  true conflict ops = 16,166
  wait cycles       = 16,166
  true-conflict rate ~= 1.478%
```

This is good evidence that the old artificial Banked penalty is gone and that the bank-matched static baseline is generally timing-equivalent when no true conflict occurs.

Also note interacting pressure in `cfd_097k`: the slower Banked execution slightly relieves other resources (e.g. Legacy has a tiny descriptor-pool-full observation while Banked does not). Blocker counts are therefore not additive causal cycle decompositions.

## 9. L1D is a major competing pressure and must be treated explicitly in final analysis

Examples from the completed runs include:

```text
scan:
  MSHR-entry fail        = 124,523,721
  MissQ-full             = 38,533,635
  bank/latency conflict  = 55,242,027
  line-allocation fail   =    471,629

convolutionSeparable:
  line-allocation fail   = 5,179,994
  MSHR-entry fail        = 2,242,333
  MissQ-full             = 1,460,359

FWT_7_21:
  MissQ-full             = 19,940,958
  MSHR-entry fail        =  4,709,556
  bank/latency conflict  =  8,909,207
```

These native counters are retry/pressure observations, not unique-request counts, so do not divide them naively by accesses and call the result a miss probability. They nevertheless show that upper-level pressure is substantial and may throttle traffic presented to L2.

After the final 26-run, a small L1 headroom sensitivity may be needed before claiming that an L2 mechanism is fundamentally throughput-limited by L2 rather than hidden by L1.

## 10. Lower path: scheduler/queue pressure is heterogeneous

Current exact telemetry supports:

```text
vectorAdd_4M:
  L2->DRAM full block     = 2,176,661
  scheduler causal block =   989,094
  DRAM BW util            = 0.7958

scan:
  MissQ full block        = 2,053,094
  L2->DRAM full block     = 62,160,071
  scheduler causal block = 37,119,745
  DRAM BW util            = 0.8187

convolutionSeparable:
  L2->DRAM full block     = 3,133,633
  scheduler causal block = 2,510,412
  DRAM BW util            = 0.6511

FWT_7_21:
  L2->DRAM full block     = 1,190,064
  scheduler causal block =   888,688
  DRAM BW util            = 0.1629
```

Low aggregate BW with nonzero scheduler blocking (`cfd`, `dwt2d`, `FWT_7`) suggests burst/channel-local pressure rather than simple chip-wide bandwidth saturation. This is exactly where the 5K channel windows should be used.

Internal DRAM ReturnQ full cycles and DRAM->L2 return-path blocks are measured zero in the completed subset. ReturnQ occupancy max is typically 1, so the configured 192-entry internal ReturnQ is not currently implicated.

## 11. Final pack needs an actual temporal analysis, not only window-row counts

The interim `target_baseline_interim_windows_summary.csv` currently reports record counts only. Before final closeout, derive analysis-ready temporal metrics from the already-produced L2/DRAM 5K window CSVs; no rerun is needed.

At minimum report per workload/variant:

```text
descriptor occupancy/window p50/p95/max
fraction of windows near/full descriptor capacity
L2->DRAM occupancy/window p50/p95/max
scheduler occupancy/window p50/p95/max
fraction of channel windows with scheduler-full activity
window bandwidth-util p50/p95/max
max/mean channel pressure or another explicit channel-imbalance indicator
```

This is needed to distinguish sustained pressure from short bursts, especially for `cfd`, `dwt2d`, `FWT_7_21`, and `FWT_11_19`.

## 12. Audit temporal-stream cardinality

The interim summary reports identical L2-window and DRAM-channel-window row counts (e.g. 448 for vectorAdd and 13,792 for scan). Before final closeout, explicitly report:

```text
configured L2 slice count
configured DRAM channel count
unique L2 window slice IDs observed
unique DRAM window channel IDs observed
expected vs actual window-row cardinality
```

If the equality is only a post-processing aggregation choice, document it. If raw L2 window telemetry unexpectedly covers only one subpartition per channel, that is a producer defect and must be treated as a hard blocker before final campaign acceptance. Do not assume either interpretation without checking the raw parsed files.

## 13. Final closeout requirements added by this review

Before writing `TARGET_BASELINE_26RUN_PASS`:

```text
1. finish the four currently running jobs without disturbance
2. reach 26/26 COMPLETE_VALID
3. push exact final Core/Framework source commits/branches used by all runs
4. publish/link C7e readiness validation evidence
5. correct the payload-service and descriptor-summary wording
6. add temporal distribution/channel-imbalance postprocessing
7. complete temporal-stream cardinality audit
8. rerun only parser/analyzer/postprocessing if those are documentation/analysis fixes
9. do not rerun simulator jobs unless an actual producer/source defect is proven
10. push final analysis pack to hrl/ep-l2-exp-v0 and STOP before 1GHz/Opportunity Study
```
