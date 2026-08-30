# EP-L2 ChatGPT Handoff — Current State

Updated: 2026-08-30

This file is the authoritative **current coordination snapshot**. Long-lived research goals, architecture intent, evidence standards, and roadmap now live in:

```text
docs/ep_l2/project_spec/
```

Read `project_spec/README.md` before treating a lane-specific target as the overall project objective.

## 1. Long-lived research objective

> Under comparable L2 storage budget and basic L2 timing, improve the L2's ability to sustain concurrent misses, pending transactions, and payload state while reducing structural blocking caused by static resource/lifetime coupling.

End-to-end speedup is a stronger evidence tier, but a structurally/service-wise better L2 remains meaningful when the removed L2 ceiling exposes a later system bottleneck. See `project_spec/RESEARCH_CHARTER.md` and `EVIDENCE_AND_CLAIM_MODEL.md`.

## 2. Frozen target geometry / formal semantic base

Primary formal target geometry remains:

```text
64 L2 slices
128 B line, 4 x 32 B sectors
Resident Tag: 64 sets x 16 ways = 1024 / slice
Resident payload: 1024 / slice
Bypass payload: 128 / slice
B0-Legacy: separate resident/bypass organization
B0-Banked: 4 x 288 payload banks, bank=payload_id%4, static 1024+128 roles
Line MSHR: 128 in the primary calibrated baseline until BASELINE-DECISION
Per-address descriptor cap: 32
WAD: 128
L2->DRAM queue: 128
FR-FCFS scheduler: 128/channel
internal DRAM ReturnQ: 192/channel
DRAM->L2: 64/slice
850 MHz primary DRAM clock
L1D: 64 KiB, 4 sets x 128 ways x 128 B, 4 banks, 20 cycles
L1 MSHR=512, merge cap=8, MissQ=16
```

Formal C7e runtime source pair:

```text
Core      ece1a3a77c5628763e0a4605bfd1c639ee6a1495
Framework f08d2ce857972fad73c4e1ab7162ba94c6336507
runtime config composite
          85562fce759876616806d32791ea3b7d1b13ee68cf20a84e48c63c96f67b8c0d
```

No Unified borrowing, functional RO no-MSHR, TVD, or primary 1GHz change is authorized before reviewed convergence/opportunity handoffs.

## 3. Lane A — formal D256 baseline

Lane A is complete and frozen:

```text
13 workloads x {B0-Legacy, B0-Banked} @850 MHz
26/26 COMPLETE_VALID
```

The two duplicate-write 3mm diagnostic paths are quarantined; clean direct 3mm replacements are the only formal rows.

Independent review-ready evidence:

```text
docs/ep_l2/review_packs/TARGET_BASELINE_FINAL_26OF26_C7E_REVIEW_READY_r1/
docs/ep_l2/chatgpt_handoff/LANE_A_FINAL_26OF26_CHATGPT_REVIEW.md
```

Formal worktrees/results are read-only anchors for all later lanes.

## 4. Lane B — Descriptor 256->512 calibration

Frozen D512 candidate:

```text
Core      878f80869ce212e779df20b6421e4dc7f987825d
Framework aae62b66685f15437cecf0193934f628e6fac6ae
runtime config composite
          a7dc3ce28f5e54ca966d08a7e3548a844533a9bee08b63ea4d964cd9ec2c9416
```

Scientific/runtime gates are complete:

```text
D256 backward equivalence: PASS
D512 natural preflight:    PASS
D512 mirror:               26/26 COMPLETE_VALID
promotion:                 26/26 PROMOTED_VALID_CALIBRATION
D512_READY:                PASS
D512_MIRROR_COMPLETE:      PASS
```

Key conclusion: descriptor-full blocking collapses in several heavy workloads but end-to-end speedup is near zero/slightly negative; pressure moves to Line-MSHR/lower-path resources. Lane B is completing documentation/contract semantic cleanup for Lane-D ingestion.

## 5. Lane C — L1 causality

D256 META-HR/BANK-HR and D512 META-HR/BANK-HR local execution is complete.

Observed performance sensitivity is small (mostly <2%, btree about 2%); the broad L1 META/BANK headroom screen does not currently justify changing the primary L1 baseline or mandatory one-at-a-time decomposition.

D512 descendants were launched speculatively from the exact Lane-B candidate. Since Lane B's promotion gate has now passed, Lane C should promote exact matching rows, publish compact machine-readable tables/contracts, and close out without rerun.

## 6. Lane D — analysis/provenance infrastructure

Lane-D V3 infrastructure has independent PASS:

```text
TEMPORAL_ANALYSIS_READY
CALIBRATION_ANALYZER_READY
D512_COST_READY
```

It provides corrected semantics for:

```text
lower_admission_byte_rate_norm (not physical BW)
final-complete 32-channel native DRAM physical utilization
64-slice / 32-channel exact time-group cardinality
scheduler/ReturnQ cycle fractions
traffic-conditioned channel imbalance
runtime-config <-> contract binding
cross-SHA reviewed equivalence
```

Do not start final CAL-ANALYSIS until Lane B/C/E final promoted contracts/packs are frozen and reviewed.

## 7. Lane E — Line-MSHR causal probe

Line-MSHR256 support/boundary audit and local causal execution are complete.

Key controlled result for convolutionSeparable / B0-Banked:

```text
D256 M128 = 290,308 cycles
D256 M256 = 290,308 cycles
D512 M128 = 292,211 cycles, 931,416 Line-MSHR-full blocks
D512 M256 = 291,108 cycles, 0 Line-MSHR-full blocks
```

Eliminating the exact MSHR-full ceiling yields only ~0.38% speedup while pressure moves to MissQ/WAD/lower path. Current classification:

```text
MSHR_ADMISSION_THROTTLE_DOWNSTREAM_LIMITED
```

D512 spmv M128->M256 is exactly unchanged and serves as a negative control.

Since the Lane-B preflight gate now passes, Lane E should promote exact matching descendants, finalize the review pack, and stop. MSHR256 is not a primary-baseline recommendation.

## 8. Scientific observations currently supported

- D256 descriptor capacity is a real structural pressure ceiling in several workloads, but is not generally the final performance ceiling.
- Descriptor relief exposes higher Line-MSHR/lower pressure; convolution develops exact MSHR-full blocking and scan a small amount.
- Removing convolution MSHR-full blocking produces very little speedup, demonstrating bottleneck substitution/downstream limitation.
- Large L1 retry/MissQ/bank-latency event counts do not imply a broad primary L1 performance bottleneck under the tested headroom points.
- cfd_097k remains the clear true B0-Banked contention case in the formal baseline; most other Banked pairs are timing-equal when true conflicts are absent.
- ReturnQ/DRAM->L2 return blocking is not a broad primary limit in the current target set.
- A better L2 must be evaluated using structural/service evidence in addition to application cycles; see `project_spec/EVIDENCE_AND_CLAIM_MODEL.md`.

## 9. Performance-headroom policy

No broad new telemetry is required before the first headroom sensitivity screen. Existing C7e/Lane-D V3 telemetry is sufficient for an initial controlled scheduler/L2->DRAM/bandwidth headroom matrix.

If a meaningful L2-mechanism x downstream-headroom interaction appears, prioritize observation-only additions:

```text
P1 native per-channel physical DRAM bus utilization per 5K window
P2 cycle-based L2 admission blocking by exact reason
P3 selected request/transaction lifetime distributions
P4 useful per-window L2 admission/completion throughput
```

See `docs/ep_l2/project_spec/PERFORMANCE_HEADROOM_PLAN.md`.

## 10. Next convergence gate

After Lane B/C/E closeout packages/contracts are pushed and independently reviewed:

```text
Lane A formal D256
+ Lane B promoted D512
+ Lane C L1 causality
+ Lane E Line-MSHR causality
+ Lane D V3 analyzer
        |
        v
CAL-ANALYSIS
        |
        v
BASELINE-DECISION
        |
        +--> performance-headroom sensitivity where needed
        |
        v
opportunity characterization
        |
        v
functional EP-L2 mechanisms
```

No lane independently declares the calibrated primary baseline or begins functional RO/TVD/Unified work.

## 11. Shared update protocol

Codex updates execution/progress/evidence columns in:

```text
docs/ep_l2/coordination/PARALLEL_WORKBOARD.md
```

ChatGPT updates review/conclusion/next-action fields after inspecting pushed evidence.

Lane-specific execution reports remain under `docs/ep_l2/codex_handoff/LANE_*_LATEST.md` to avoid cross-window collisions.
