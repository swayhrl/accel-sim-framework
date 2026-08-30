# EP-L2 M0a — Generic Structural/Service Observability Handoff

Status: **AUTHORIZED AFTER BASELINE_DECISION_PASS**

## Objective

Add observation-only, timing-neutral telemetry that measures how many simulated cycles the L2 frontend is structurally unable to admit useful work and how much useful work is actually admitted/completed, without creating any functional EP-L2 mechanism or synthetic bypass traffic.

M0a exists to strengthen the paper's Level-1/Level-2 evidence and to guide M0b mechanism-specific opportunity studies.

## Semantic parent

Use the accepted calibrated D512 research baseline:

```text
Core      878f80869ce212e779df20b6421e4dc7f987825d
Framework aae62b66685f15437cecf0193934f628e6fac6ae
Descriptor 512
Line MSHR 128
L1 BASE
WAD 128
L2->DRAM 128
scheduler 128
ReturnQ 192
DRAM 850 MHz
```

Do not start from Lane-D analysis source or Lane-F documentation branch.

## Isolation

Recommended:

```text
Framework /workspace/worktrees/accel-sim-ep-l2-m0a/
Core      /workspace/worktrees/gpgpu-sim-ep-l2-m0a/
branch    hrl/ep-l2-m0a-observability-v0
results   /workspace/results/ep_l2_m0a/
```

Other lane worktrees/results are read-only.

## Required new telemetry

Use a new observation family/version rather than changing existing C7e field semantics.

### 1. Frontend observation denominator

Per L2 slice:

```text
m0_frontend_head_observed_cycles
```

Increment once per simulated cycle when exact preview/admission is evaluated for the current frontend head.

### 2. Any-blocked cycles

```text
m0_frontend_head_any_blocked_cycles
```

Increment at most once per observed cycle if the exact frontend head cannot be admitted.

### 3. Independent blocked-cycle reason bits

At the exact non-mutating preview/admission decision, increment each independently true reason at most once/cycle:

```text
m0_frontend_head_blocked_cycles_tag_way
m0_frontend_head_blocked_cycles_wad_full
m0_frontend_head_blocked_cycles_wad_hazard
m0_frontend_head_blocked_cycles_line_mshr
m0_frontend_head_blocked_cycles_descriptor
m0_frontend_head_blocked_cycles_per_address
m0_frontend_head_blocked_cycles_missq
m0_frontend_head_blocked_cycles_payload_service
m0_frontend_head_blocked_cycles_payload_capacity
m0_frontend_head_blocked_cycles_lowerq
m0_frontend_head_blocked_cycles_responseq
```

Reasons may overlap; `any_blocked` may not double count. Do not derive any field from retry-event counts.

### 4. Resident payload occupancy/slack

Use actual production resident state only:

```text
m0_resident_payload_occupied
m0_resident_payload_free
```

Sample consistently at the existing B0 sampling point. Do not call dormant bypass slots workload opportunity.

### 5. Useful L2 service counts

Count unique useful events, not re-presented blocked heads:

```text
m0_useful_frontend_admit
m0_useful_response_enqueue
```

`useful_frontend_admit`: immediately after a frontend request is successfully admitted/mutated.

`useful_response_enqueue`: when a requester response is actually accepted into L2->ICNT immediately before the existing retirement/commit point.

If UID dedup is required for correctness, implement it explicitly or narrow the field semantics; do not assume retries are unique requests.

## Temporal output

Provide cumulative/application totals plus 5K-window deltas/distributions for:

```text
observed cycles
any blocked cycles
blocked cycles by reason
resident occupancy/free
useful admits
useful response enqueues
```

All denominators and overlap semantics must be documented.

## Explicitly forbidden

Do not:

```text
change admission/arbitration decisions
change descriptor/MSHR/L1/WAD/payload capacities
create a production bypass consumer
fabricate bypass traffic
change payload allocation
change bank mapping
change lower queues or DRAM
implement Unified/RO/TVD
use M0 values to control runtime behavior
```

## Representative validation workloads

At minimum:

```text
convolutionSeparable
scan
vectorAdd_4M
spmv
cfd_097k
sad
```

Parallel simulation is allowed after source/config freeze.

## Deliverables

```text
docs/ep_l2/codex_handoff/LANE_M0A_LATEST.md
docs/ep_l2/review_packs/M0A_OBSERVABILITY_r1/
```

The pack must include source anchors/diff, field contracts, directed tests, OFF/ON timing-neutrality, representative results, parser outputs, terminal invariants, raw-log index and SHA256SUMS.

## STOP

STOP at:

```text
M0A_OBSERVABILITY_REVIEW_READY
```

Do not use M0a findings to start a functional mechanism before ChatGPT review.
