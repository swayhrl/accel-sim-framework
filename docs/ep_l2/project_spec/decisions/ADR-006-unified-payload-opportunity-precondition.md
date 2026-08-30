# ADR-006 — Unified Payload Requires a Real Non-Resident Consumer

Status: **ACCEPTED**

Date: 2026-08-30

## Context

Lane-F source audit found that the current C7e `ep_l2_payload_store` models:

```text
1024 resident payload slots
128 bypass payload slots
```

but the production L2 request path allocates/fills resident payload only. `reserve_bypass`, `complete_bypass`, and `release_bypass` have no production caller; current bypass occupancy/slack is therefore a dormant-model fact, not workload evidence.

The design also has exactly 1024 resident tags. Under a standalone shared-payload mechanism with tag count fixed at 1024, the extra 128 physical payload slots cannot increase the number of simultaneously resident cache lines.

## Decision

Do **not** implement or evaluate Unified Payload v1 as a performance/capacity mechanism until M0 establishes a real non-resident payload consumer/lifecycle and time-aligned opportunity.

The next implementation order is:

```text
M0a generic structural/service observation
M1 behavior-preserving elastic/global-ID substrate
M0b real mechanism-specific opportunity shadows
        -> choose first functional mechanism
```

A real non-resident consumer may later be a conservative RO/pending object, a transferred dirty-victim/TVD object, or another explicitly defined production lifecycle. Do not fabricate bypass traffic solely to populate the dormant 128 slots.

## Capacity asymmetry

With 1024 resident tags and 1024 resident payload quota:

```text
resident borrowing a bypass-range physical ID
```

is relocation, not additional resident-line capacity. A standalone M2 capacity claim must therefore not count "resident can borrow the extra 128" as extra residency or avoided eviction unless another reviewed mechanism changes logical tag/pending lifetime such that additional physical payload demand really exists.

The likely capacity-sharing opportunity is the reverse direction: a real non-resident role can borrow unused resident payload capacity when resident occupancy is below its logical maximum.

## Bank-confounding rule

Current resident service bank is effectively tied to the current payload/tag index modulo 4. A shared allocator that changes payload IDs may change bank placement and confound a capacity-elasticity experiment with bank remapping.

For capacity-only experiments, preserve resident bank class wherever practical:

```text
payload_id % 4 == tag_index % 4
```

using per-bank free lists. Intentional bank-placement optimization must be a separate feature/ablation.

## Forward-progress rule

After a real non-resident consumer exists, allocation/reserve design must prove forward progress for **both** resident/fill and non-resident/pending roles. A one-sided protected reserve is insufficient without lifecycle proof.

Reserve size must be derived from the number of simultaneously indispensable live payload objects / circular-dependency analysis, not inherited from the dormant 128-slot model as a performance tuning knob.

## Consequences

- M1 remains high priority because a global handle/sidecar substrate is useful for M3/M4 and later sharing.
- M2 is no longer assumed to be the first functional mechanism.
- M0 opportunity telemetry must not use dormant `bypass_used()` as workload evidence.
- The first functional mechanism after M1 is selected from measured RO/TVD/non-resident opportunity, then shared-pool composition can be evaluated with a real consumer.
