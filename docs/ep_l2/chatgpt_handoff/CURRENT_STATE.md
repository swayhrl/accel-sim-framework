# EP-L2 ChatGPT Handoff — Current State

Updated: 2026-08-30

This file is the authoritative **current coordination snapshot**. Long-lived research goals, architecture intent, evidence standards, workload classification, implementation roadmap, and headroom policy live in:

```text
docs/ep_l2/project_spec/
```

Read `project_spec/README.md` before treating a lane-specific target as the overall project objective.

## 1. Long-lived research objective

> Under comparable L2 storage budget and basic L2 timing, improve the L2's ability to sustain concurrent misses, pending transactions, and payload state while reducing structural blocking caused by static resource/lifetime coupling.

End-to-end speedup is a stronger evidence tier, but a structurally/service-wise better L2 remains meaningful when the removed L2 ceiling exposes a later system bottleneck.

## 2. Frozen target geometry / formal semantic base

Current formal target geometry remains:

```text
64 L2 slices
128 B line, 4 x 32 B sectors
Resident Tag: 64 sets x 16 ways = 1024 / slice
Resident payload: 1024 / slice
Bypass payload: 128 / slice
B0-Legacy: separate resident/bypass organization
B0-Banked: 4 x 288 payload banks, bank=payload_id%4, static 1024+128 roles
Line MSHR: 128 until BASELINE-DECISION
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

Formal C7e source/config:

```text
Core      ece1a3a77c5628763e0a4605bfd1c639ee6a1495
Framework f08d2ce857972fad73c4e1ab7162ba94c6336507
runtime   85562fce759876616806d32791ea3b7d1b13ee68cf20a84e48c63c96f67b8c0d
```

No functional Unified borrowing, RO pending/no-MSHR, TVD, or primary 1GHz change is authorized before reviewed convergence and a mechanism-stage handoff.

## 3. Lane A — formal D256 baseline

Complete and frozen:

```text
13 workloads x {B0-Legacy, B0-Banked} @850 MHz
26/26 COMPLETE_VALID
```

The two duplicate-write 3mm diagnostic paths are quarantined; clean direct replacements are the only formal rows.

Evidence:

```text
docs/ep_l2/review_packs/TARGET_BASELINE_FINAL_26OF26_C7E_REVIEW_READY_r1/
docs/ep_l2/chatgpt_handoff/LANE_A_FINAL_26OF26_CHATGPT_REVIEW.md
```

Formal worktrees/results are read-only anchors.

## 4. Lane B — Descriptor 256->512 calibration

Complete:

```text
Core      878f80869ce212e779df20b6421e4dc7f987825d
Framework aae62b66685f15437cecf0193934f628e6fac6ae
runtime   a7dc3ce28f5e54ca966d08a7e3548a844533a9bee08b63ea4d964cd9ec2c9416

D256 backward equivalence PASS
D512 natural preflight PASS
D512_READY PASS
26/26 D512 COMPLETE_VALID
26/26 PROMOTED_VALID_CALIBRATION
D512_MIRROR_COMPLETE PASS
```

`D512_BASE.json` is published under `docs/ep_l2/calibration/contracts/` with exact source/config/equivalence/config-delta provenance.

Key conclusion: Descriptor256 is a real structural admission ceiling in several workloads. D512 removes it but generally does not improve application cycles, exposing later Line-MSHR/lower-path pressure.

## 5. Lane C — L1 causality

Complete:

```text
L1_CAUSALITY_SCREEN_COMPLETE
```

All D256/D512 META-HR/BANK-HR cells are complete and promoted. Four `EP_L2_CALIBRATION_CONTRACT_V2` contracts are published.

Broad L1 headroom has small performance sensitivity; the tested data do not justify changing the primary L1 baseline or mandatory one-at-a-time decomposition.

## 6. Lane E — Line-MSHR causal probe

Complete:

```text
LINE_MSHR_CAUSALITY_PROBE_COMPLETE
```

Controlled convolution result:

```text
D256 M128 = 290,308
D256 M256 = 290,308
D512 M128 = 292,211 with 931,416 Line-MSHR-full blocks
D512 M256 = 291,108 with 0 Line-MSHR-full blocks
```

Removing exact Line-MSHR-full pressure yields only ~0.38% speedup while pressure moves elsewhere. Accepted classification:

```text
MSHR_ADMISSION_THROTTLE_DOWNSTREAM_LIMITED
```

D512 spmv M128->M256 is unchanged and acts as a negative control. MSHR256 is not a primary-baseline recommendation.

## 7. Lane D — final calibration convergence

Lane-D V3 analysis/provenance infrastructure is independently accepted:

```text
TEMPORAL_ANALYSIS_READY
CALIBRATION_ANALYZER_READY
D512_COST_READY
```

All required promoted B/C/E inputs now exist. Final convergence is **authorized now** under:

```text
docs/ep_l2/chatgpt_handoff/FINAL_CALIBRATION_CONVERGENCE_HANDOFF.md
docs/ep_l2/chatgpt_handoff/FINAL_CALIBRATION_CONVERGENCE_ACCEPTANCE_CRITERIA.md
docs/ep_l2/chatgpt_handoff/LANE_D_FINAL_CONVERGENCE_TARGET_GOAL.md
```

Lane D must first produce an all-13 workload archetype checkpoint, then the six-cell final calibration matrix, baseline-decision evidence, mechanism-priority recommendation, and headroom candidates. No simulator run is authorized in this convergence stage.

## 8. Lane F — mechanism implementation preparation

A new source/design-analysis lane is authorized in parallel with Lane D:

```text
docs/ep_l2/chatgpt_handoff/LANE_F_MECHANISM_PREP_HANDOFF.md
docs/ep_l2/chatgpt_handoff/LANE_F_MECHANISM_PREP_ACCEPTANCE_CRITERIA.md
docs/ep_l2/chatgpt_handoff/LANE_F_TARGET_GOAL.md
```

Lane F must map the exact source/state/lifecycle implementation for:

```text
M0 mechanism-readiness telemetry/shadow opportunity
M1 behavior-preserving elastic payload/resource substrate
M2 Unified Payload Pool v1
M3 RO pending-state source dependencies
M4 WAD/TVD source dependencies
```

It may not push a functional mechanism change. The goal is to make the first implementation stage ready to start immediately after baseline-decision review.

## 9. Preliminary workload archetypes

Current evidence-backed preliminary map is in:

```text
docs/ep_l2/project_spec/WORKLOAD_ARCHETYPES_PRELIMINARY.md
```

Current high-level groups include:

```text
scan/vectorAdd: sustained descriptor + lower/scheduler + high-BW
convolution: controlled Descriptor -> Line-MSHR -> downstream substitution
spmv: Descriptor -> per-address / near-MSHR + lower path
FWTs: bursty/phase-local descriptor pressure
cfd: true payload-bank service contention
dwt2d: WAD/victim-lifetime candidate
btree: address-local / weak L1 sensitivity
gemm/3mm/sad/sgemm: low-L2-pressure/control families
```

Lane D must validate/revise this across the full promoted matrix before it becomes final characterization.

## 10. Performance-headroom policy

No broad new telemetry is required before the first headroom sensitivity screen. Existing C7e/Lane-D V3 telemetry is sufficient for an initial controlled scheduler/L2->DRAM/bandwidth headroom matrix.

If a meaningful L2-mechanism x downstream-headroom interaction appears, prioritize observation-only additions:

```text
P1 native per-channel physical DRAM bus utilization per 5K window
P2 cycle-based L2 admission blocking by exact reason
P3 selected request/transaction lifetime distributions
P4 useful per-window L2 admission/completion throughput
```

See `docs/ep_l2/project_spec/PERFORMANCE_HEADROOM_PLAN.md`.

## 11. Staged implementation roadmap

See:

```text
docs/ep_l2/project_spec/MECHANISM_IMPLEMENTATION_PLAN.md
```

Current intended sequence:

```text
Final calibration convergence
        -> BASELINE-DECISION
        -> M0 targeted opportunity/shadow telemetry
        -> M1 behavior-preserving elastic substrate
        -> first measured-opportunity functional mechanism
        -> remaining mechanism families
        -> integrated EP-L2
        -> performance headroom / full-suite evaluation
```

The default first functional candidate is Unified Payload Pool v1 because it directly targets static payload-role coupling and the 4x288 physical substrate already exists, **but only if M0 establishes real role-complementarity/residency opportunity**. If M0 does not, implementation priority must follow the evidence rather than force Unified Payload.

## 12. Shared update protocol

Codex updates execution/progress/evidence in:

```text
docs/ep_l2/coordination/PARALLEL_WORKBOARD.md
```

ChatGPT updates review/conclusion/next-action after inspecting pushed evidence.

Lane-specific reports stay under `docs/ep_l2/codex_handoff/LANE_*_LATEST.md`.
