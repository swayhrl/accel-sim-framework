# EP-L2 ChatGPT Handoff — Current State

Updated: 2026-08-30

This file is the authoritative **current coordination snapshot**. Long-lived research goals, architecture intent, evidence standards, implementation sequence, experiment-mode contract and headroom policy live under:

```text
docs/ep_l2/project_spec/
```

## 1. Research objective

> Under comparable L2 storage budget and basic L2 timing, improve the L2's ability to sustain concurrent misses, pending transactions, and payload state while reducing structural blocking caused by static resource/lifetime coupling.

End-to-end speedup is stronger evidence, but a structurally/service-wise better L2 remains meaningful when the removed L2 ceiling exposes a later system bottleneck.

## 2. Historical formal anchor — frozen

C7e D256 formal source/config:

```text
Core      ece1a3a77c5628763e0a4605bfd1c639ee6a1495
Framework f08d2ce857972fad73c4e1ab7162ba94c6336507
runtime   85562fce759876616806d32791ea3b7d1b13ee68cf20a84e48c63c96f67b8c0d
```

Lane A is frozen at 26/26 `COMPLETE_VALID`. Historical D256 data remain immutable calibration provenance.

## 3. Calibration closeout

Lane B:

```text
D512_READY PASS
D512_MIRROR_COMPLETE PASS
26/26 PROMOTED_VALID_CALIBRATION
Core      878f80869ce212e779df20b6421e4dc7f987825d
Framework aae62b66685f15437cecf0193934f628e6fac6ae
runtime   a7dc3ce28f5e54ca966d08a7e3548a844533a9bee08b63ea4d964cd9ec2c9416
```

Lane C:

```text
L1_CAUSALITY_SCREEN_COMPLETE
D256/D512 META-HR/BANK-HR promoted
no broad material L1 response
```

Lane E:

```text
LINE_MSHR_CAUSALITY_PROBE_COMPLETE
convolution D512 MSHR128->256:
  Line-MSHR-full 931,416 -> 0
  cycles 292,211 -> 291,108 (~0.38%)
classification: MSHR_ADMISSION_THROTTLE_DOWNSTREAM_LIMITED
```

Lane D final convergence is independently reviewed PASS in:

```text
docs/ep_l2/chatgpt_handoff/LANE_D_FINAL_CONVERGENCE_CHATGPT_REVIEW.md
```

## 4. BASELINE_DECISION — PASS

Accepted calibrated **mechanism-development research baseline**:

```text
Descriptor pool        512
Line MSHR              128
per-address cap         32
L1D                    64 KiB/core, 4 sets x 128 ways x 128 B
L1 banks               4
L1 latency             20 cycles
L1 MSHR                512
L1 merge cap           8
L1 MissQ               16
WAD                     128
payload storage        1152 x 128 B / slice
payload banks          4 x 288
bank service           one arbitrary op/bank/cycle
L2->DRAM queue          128
FR-FCFS scheduler      128/channel
ReturnQ                 192/channel
DRAM                    850 MHz primary
```

D512 is selected to remove a bounded-cost descriptor metadata throttle from the research baseline, **not because it is faster and not because it creates an MSHR bottleneck**.

Decision record:

```text
docs/ep_l2/project_spec/decisions/ADR-005-calibrated-research-baseline.md
```

## 5. Final workload characterization

Lane-D final 13-workload evidence is under:

```text
docs/ep_l2/review_packs/FINAL_CALIBRATION_CONVERGENCE_r1/
  WORKLOAD_ARCHETYPES.csv
  WORKLOAD_ARCHETYPES.md
  MECHANISM_TARGET_MAP.md
```

Representative development set:

```text
convolutionSeparable  structural bottleneck substitution
scan                  sustained descriptor/lower/high-BW
vectorAdd_4M          sustained throughput/high-BW
spmv                  per-address / near-MSHR
FWT_7_21              bursty descriptor/WAD/lower
cfd_097k              true bank-service contention
dwt2d                 dirty-victim/WAD lifetime candidate
sad                   low-pressure negative control
```

Unified/RO/TVD opportunity remains `UNKNOWN_NEEDS_TELEMETRY` where the required lifetime/eligibility/role evidence is not yet measured.

## 6. Lane F implementation-prep review

Lane-F source/design preparation is accepted in:

```text
docs/ep_l2/chatgpt_handoff/LANE_F_MECHANISM_PREP_CHATGPT_REVIEW.md
```

Critical source fact:

```text
1024 resident payload slots
128 bypass-model slots
but no production caller allocates the bypass model
```

Therefore dormant bypass occupancy/slack is not workload evidence.

M1 global-ID/sidecar/static-equivalent substrate is implementation-ready after a dedicated handoff.

M2 Unified Payload is **not** automatically the first functional mechanism. With 1024 resident tags == 1024 resident payload quota, the extra 128 physical slots cannot by themselves add resident cache-line capacity. A real non-resident consumer/lifetime and measured opportunity are required first.

Decision record:

```text
docs/ep_l2/project_spec/decisions/ADR-006-unified-payload-opportunity-precondition.md
```

## 7. Current mechanism sequence

Authoritative sequence:

```text
docs/ep_l2/project_spec/MECHANISM_SEQUENCE_CURRENT.md
```

Near-term:

```text
M0a generic observation  ||  M1 behavior-preserving elastic substrate
                 \              /
                  -> M0b mechanism-specific opportunity shadows
                          |
                          -> choose first functional mechanism from evidence
                          |
                          -> compose validated mechanisms
                          |
                          -> performance-headroom/full-suite evaluation
```

M0a must not fabricate bypass traffic. M0b should measure real RO/TVD/non-resident role opportunity.

## 8. Experiment-mode contract

All future functional implementations must follow:

```text
docs/ep_l2/project_spec/EXPERIMENT_MODE_SWITCH_CONTRACT.md
```

Base resource configuration is orthogonal to default-OFF mechanism feature bits. Formal comparisons should use the same source/SHA/binary and differ only through explicit audited feature overlays.

## 9. M2-specific guardrails

Before any shared/unified payload functional implementation:

```text
real non-resident consumer defined
measured demand/slack overlap
resident bank class preserved or bank placement separately ablated
resident + non-resident forward progress proved
reserve derived from lifecycle safety rather than dormant 128-slot tuning
```

Capacity-only resident experiments should preserve, where practical:

```text
payload_id % 4 == tag_index % 4
```

to avoid confounding capacity elasticity with bank remapping.

## 10. Performance-headroom policy

Do not launch headroom merely because calibration shows downstream pressure. First obtain an L2-local functional mechanism effect at H0. Then test mechanism × headroom interaction using single-axis candidates:

```text
H-SCHED 128->256
H-L2D   128->256
H-BW    850MHz->1GHz sensitivity
```

See `project_spec/PERFORMANCE_HEADROOM_PLAN.md`.

## 11. Immediate next stage

Authorized planning direction:

```text
M0a observation-only structural/service telemetry
+
M1 static-equivalent elastic/global-ID substrate
```

No functional Unified, RO pending-state, TVD or adaptive policy is authorized until the next implementation handoff and its acceptance criteria are published/reviewed.

## 12. Archival follow-ups

Lane D: add exact final analysis source SHA and explicit `git diff --check` evidence to the convergence pack.

Lane F: mirror `LANE_F_LATEST.md` and `MECHANISM_IMPLEMENTATION_PREP_r1/` from `hrl/ep-l2-mechanism-prep-v0` to the permanent coordination branch before archival.
