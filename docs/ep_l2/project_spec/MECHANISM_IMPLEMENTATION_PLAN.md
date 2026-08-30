# EP-L2 Mechanism Implementation Plan

Status: **pre-implementation architecture plan**. Exact implementation starts only after `BASELINE-DECISION` review, but source audit/specification may proceed earlier.

## Design objective

Build EP-L2 as a sequence of independently verifiable resource-decoupling mechanisms rather than one monolithic patch.

The target property is:

> Under comparable total L2 storage and basic L2 timing, reduce structural admission/service blocking caused by static coupling among tag residency, pending transaction state, requester metadata, and physical payload ownership.

Every phase must preserve a fallback mode that exactly reproduces the previous accepted stage.

## Phase M0 — mechanism-readiness characterization and shadow opportunity

### Purpose

Close the evidence gaps that determine which mechanism is worth implementing first.

### Build

Observation-only / timing-neutral telemetry and shadow models, selected from:

```text
P1 physical per-channel 5K DRAM bus utilization, if headroom analysis needs it
P2 true cycle-based L2 admission-blocked accounting by independent reason
P3 selected transaction/resource lifetime distributions
P4 useful L2 throughput per 5K window
```

Mechanism-specific shadow observations:

```text
Unified payload:
  resident-role occupancy/slack
  bypass/pending-role occupancy/slack
  simultaneous role slack/complementarity
  shadow shared-pool allocation success
  counterfactual resident eviction/save opportunity

RO pending-tag:
  requests provably eligible for read-only treatment
  traditional Line-MSHR lifetime that would be avoidable/releasable
  descriptor/pending-tag occupancy required by the alternative
  overlap with lower-path bottleneck phases

TVD/WAD:
  dirty-victim count
  time from destructive victim selection to true writeback completion
  resident payload slot lifetime attributable to dirty victim data
  WAD occupancy/lifetime overlap
```

### Correctness requirement

Default OFF/observation-only behavior must reproduce the calibrated baseline exactly in simulated cycles and existing telemetry on representative workloads.

### Output

```text
MECHANISM_OPPORTUNITY_MATRIX
selected first functional mechanism
representative workload subset
```

### Why M0 comes first

Current data establish structural pressure, but do not yet prove time-aligned resident/bypass slack, RO eligibility, or TVD-releasable payload lifetime. Implementing those mechanisms before measuring the opportunity would risk optimizing an unmeasured condition.

## Phase M1 — common elastic-resource substrate, behavior-preserving

### Purpose

Create the plumbing needed by later mechanisms without changing architectural behavior.

### Build

Audit and, only where required, generalize:

```text
payload slot allocator interface
payload role/owner metadata
payload_id + generation ownership checks
free/release path
resident-vs-pending role accounting
explicit pending-state handles
resource-lifetime hooks
configuration modes
```

The current 4x288 physical bank layout and one-op/bank/cycle model remain unchanged.

### Key rule

First implementation mode must still enforce the current static roles:

```text
resident quota 1024
bypass quota   128
```

and reproduce the chosen calibrated baseline exactly.

### Output

```text
ELASTIC_SUBSTRATE_READY
```

No performance claim.

## Phase M2 — Unified Payload Pool v1

### Purpose

Remove the static 1024-resident / 128-bypass capacity partition while preserving the same total 1152 x 128-B physical payload storage and the same 4-bank service model.

### Build

Functional shared-pool capacity allocation:

```text
one 1152-slot physical pool
4 x 288 banks unchanged
payload_id + generation unchanged
role recorded per live allocation rather than encoded by a static quota
same bank mapping and service timing
safe allocation/release invariants
```

The exact deadlock/safety reservation policy must be chosen from source audit and M0 evidence. Do not simply allow one role to consume all slots if that can prevent required forward progress. Prefer a demand-aware protected-reserve rule over silently reintroducing a permanent 1024/128 partition.

### Keep fixed

```text
resident tag count 1024
Descriptor baseline chosen at BASELINE-DECISION
Line-MSHR baseline chosen at BASELINE-DECISION
per-address cap 32
WAD 128
L1
lower queues / scheduler / DRAM clock
bank count / bank service rate
```

### First success metrics

Primary:

```text
role-specific allocation denial / blocked cycles
shared-pool occupancy / free-space utilization
resident evictions avoided or useful residency gained, if shadow model supports it
```

Secondary:

```text
L2 miss/admission/service throughput
bank conflict/wait change
lower-path pressure movement
```

System:

```text
cycles / speedup
```

### Representative workloads

Choose only workloads with M0 evidence of resident/bypass complementarity plus one control. Do not use the whole suite by default.

### Output

```text
UNIFIED_PAYLOAD_V1_READY
```

## Phase M3 — pending-state / read-only decoupling v1

### Purpose

Reduce the amount of traditional Line-MSHR lifetime needed for requests that can be **provably** handled by cheaper pending-tag/transaction metadata.

This is not justified merely by a nonzero MSHR-full counter. Lane-E already shows that removing Line-MSHR-full can have low end-to-end sensitivity.

### Build concept

For a strictly certified class of requests, investigate:

```text
resident/pending tag state survives without a traditional Line-MSHR for the entire miss lifetime
requester descriptors remain explicit
sector/pending masks remain explicit
fill/response ownership remains protected by generation/version state
writes/atomics/non-certified accesses use the normal path
```

Start with a shadow-eligibility oracle and then a functional conservative eligibility rule.

### Required source invariants

```text
no duplicate live owner for one payload generation
no stale fill can validate a replaced/reused tag
all requesters receive exactly one response
per-address ordering/merge semantics preserved
writes/atomics never enter an unsafe RO path
terminal pending state drains to zero
```

### Primary success metrics

```text
traditional Line-MSHR allocation/lifetime reduction
MSHR admission-blocked cycles
pending-tag occupancy/lifetime
requester descriptor pressure
useful admitted concurrency
```

Performance is secondary and should be interpreted with lower-path headroom.

### Output

```text
RO_PENDING_STATE_V1_READY
```

## Phase M4 — WAD-backed TVD / victim-payload decoupling v1

### Purpose

Release a resident cache payload slot earlier when dirty victim data must remain live for writeback, so resident-way/payload lifetime is not forced to match no-return writeback lifetime.

### Build concept

Source audit must define the actual storage accounting. The mechanism may associate a temporary victim-data object with WAD state, but total L2 storage must remain comparable; do not create an unaccounted extra victim data cache.

Required conceptual state:

```text
victim address identity in WAD
victim data ownership / payload_id or explicitly budgeted TVD slot
dirty sector mask
writeback-issued / completion state
generation/owner validation
```

Release only at the true modeled lifecycle point; current WAD semantics release at `memory_partition_unit::set_done()` for no-return writeback.

### Primary success metrics

```text
resident payload/way lifetime shortened by dirty victim handling
victim-related structural blocked cycles
WAD/TVD occupancy and lifetime
resident allocation opportunity gained
```

### Target workloads

Use M0 dirty-victim lifetime evidence; `dwt2d`, `scan`, `FWT_7_21`, and other WAD-active workloads are candidates, not automatic targets.

### Output

```text
TVD_V1_READY
```

## Phase M5 — combined EP-L2 v1

### Purpose

Combine only individually validated mechanisms whose state machines and storage budgets compose cleanly.

Potential composition:

```text
elastic/shared payload allocation
+
pending-tag / reduced-MSHR-lifetime path
+
TVD/victim payload decoupling
```

### Rules

- Preserve per-mechanism enable bits for ablation.
- Do not change total storage to obtain the combined result.
- Re-run cross-product directed tests for ownership/generation/replacement/writeback interactions.
- Use the representative workload set first, then full suite only after correctness/performance sanity.

### Output

```text
EP_L2_V1_INTEGRATED
```

## Phase M6 — performance-headroom and robustness

### Purpose

Measure how much L2-local structural improvement converts to application performance under the primary system and under independently relaxed downstream constraints.

Use `PERFORMANCE_HEADROOM_PLAN.md`.

Start with single-axis headroom:

```text
scheduler 128 -> 256
L2->DRAM 128 -> 256
DRAM 850 MHz -> 1 GHz as sensitivity only
```

Only use combined headroom after single-axis evidence.

### Output

```text
PRIMARY_SYSTEM_RESULT
HEADROOM_INTERACTION_RESULT
```

Keep them explicitly separate in paper claims.

## Phase M7 — policy/adaptation only if justified

Do not begin with adaptive policy.

Only after static mechanism behavior is understood should EP-L2 consider phase-aware allocation/reservation across resource roles.

Possible later policy inputs:

```text
role occupancy
blocked-cycle reason
pending lifetime
bank pressure
lower-path pressure
```

The policy must improve on a simple static/shared mechanism rather than compensate for an incorrect substrate.

## Recommended near-term engineering order

```text
Final calibration convergence
        -> BASELINE-DECISION
        -> M0 targeted opportunity/shadow telemetry
        -> M1 behavior-preserving elastic substrate
        -> choose first functional mechanism from measured opportunity
        -> M2 Unified Payload v1 OR M3/M4 if M0 shows stronger evidence
        -> remaining mechanisms
        -> integrated EP-L2
        -> headroom / full-suite / paper evaluation
```

The default expectation is to try **M2 Unified Payload v1 first** because it is closest to the central EP-L2 storage-decoupling idea and the physical 4x288 payload substrate already exists, but this is conditional on M0 demonstrating real role-complementarity or residency opportunity. If M0 does not, the implementation priority must change rather than force the mechanism.

## Review rule for every phase

Each functional phase requires:

```text
HANDOFF
ACCEPTANCE_CRITERIA
TARGET_GOAL
source branch/worktree isolation
directed lifecycle tests
old-mode exact equivalence
natural-workload smoke
review pack
ChatGPT independent review
```

No phase inherits scientific validity merely because the previous phase passed.
