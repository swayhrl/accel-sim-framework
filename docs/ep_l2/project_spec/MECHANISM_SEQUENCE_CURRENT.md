# EP-L2 Current Mechanism Sequence

Status: **canonical near-term sequence after Lane-D/F review**.

This file refines `MECHANISM_IMPLEMENTATION_PLAN.md` using accepted ADR-005 and ADR-006. Where the older plan says M2 Unified Payload is the default first functional mechanism, this file is authoritative.

## Accepted calibrated baseline

```text
Descriptor pool        512
Line MSHR              128
per-address cap         32
L1                     BASE
WAD                     128
payload storage        1152 x 128 B / slice
payload banks          4 x 288
L2->DRAM               128
FR-FCFS scheduler      128/channel
ReturnQ                192/channel
DRAM                    850 MHz primary
```

Mechanism features sit above this resource baseline through the default-OFF feature-vector contract.

## Near-term sequence

```text
M0a generic structural/service telemetry
        ||
M1 behavior-preserving elastic/global-ID substrate
        |
        v
M0b mechanism-specific opportunity shadows
        |
        +--> RO pending-state opportunity
        +--> dirty-victim/TVD opportunity
        +--> real non-resident payload-role opportunity
        |
        v
choose first functional mechanism from measured opportunity
        |
        +--> M3 RO pending-state v1 if safe eligibility/lifetime opportunity is strong
        +--> M4 TVD v1 if dirty-victim payload-lifetime opportunity is strong
        +--> M2 shared/unified payload only when a real non-resident consumer exists
        |
        v
compose validated mechanisms into integrated EP-L2
        |
        v
performance-headroom + full-suite evaluation
```

## M0a — implement now

Generic observation only:

```text
cycle-based frontend admission blocking by exact reason
any-blocked/observed-cycle denominators
resident payload occupancy/slack
useful frontend admits
useful requester responses enqueued
5K + cumulative distributions
```

M0a must not create or infer a fake bypass consumer.

## M1 — implement now

Behavior-preserving substrate:

```text
global 1152-entry payload-ID namespace
explicit role/status/owner/generation
payload handle {id,generation}
tag-index -> payload-ID sidecar
bank = payload_id % 4
static-compatible policy
feature-vector / mode-switch plumbing
```

All-OFF and M1 static-compatible modes must reproduce the accepted D512 research baseline.

M1 should preserve resident bank class under static operation. Future capacity-sharing modes should preserve `payload_id % 4 == tag_index % 4` for resident allocations unless bank placement is explicitly studied as a separate mechanism.

## M0b — opportunity shadows before any functional mechanism

### RO pending-state

Measure conservative eligibility/exclusion reasons, current Line-MSHR lifetime and the portion a safe pending object could avoid while preserving descriptors/sector/order state.

### TVD / dirty victim

Measure dirty-victim selection count, payload hold time to true `set_done`, WAD lifetime, and overlap with resident allocation/admission pressure.

### Non-resident payload role / Unified

Do not use dormant 128 bypass slots as workload evidence. Define a real production candidate role first. Once it exists, measure live demand, time-aligned resident slack, shadow shared-pool grants/denials, and two-sided forward-progress requirements.

## M2 Unified Payload — revised precondition

M2 is **not** the default first functional stage.

With 1024 resident tags and 1024 resident payload quota, letting a resident use one of the extra 128 physical IDs does not increase resident cache-line capacity. Standalone M2 capacity value therefore depends on a real non-resident role borrowing unused resident capacity or later composition with mechanisms that change tag/pending/payload lifetime.

Before M2:

```text
real non-resident consumer defined
measured demand/slack overlap
bank-remapping confound controlled
resident and non-resident forward progress proved
reserve derived from lifecycle safety, not dormant 128-slot tuning
```

## Performance-headroom timing

Do not run headroom merely because calibration shows lower-path pressure. First obtain an L2-local functional mechanism effect at H0. Then use the already-defined H-SCHED/H-L2D/H-BW matrix to test whether downstream masking changes conversion to end-to-end speedup.
