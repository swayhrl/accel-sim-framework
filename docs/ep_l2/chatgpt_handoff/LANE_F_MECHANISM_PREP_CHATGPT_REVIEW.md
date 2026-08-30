# EP-L2 Lane F Mechanism Implementation Prep — ChatGPT Review

Date: 2026-08-30

Review status: **PASS — SOURCE/DESIGN PREPARATION ACCEPTED**

This PASS applies to the source audit, M0/M1 preparation, mode-switch design, and M3/M4 dependency maps. It does **not** authorize M2 Unified Payload as the first functional mechanism without the additional opportunity/safety conditions below.

Reviewed evidence lives on:

```text
Framework branch hrl/ep-l2-mechanism-prep-v0
review pack docs/ep_l2/review_packs/MECHANISM_IMPLEMENTATION_PREP_r1/
branch tip during review: d3f0e0e38617b0b6407ec2c1df81f382c99a9c8f
```

No functional simulator source change was found in Lane F; its pushed commits are documentation/design-only.

## 1. Source/state map — PASS

The source map identifies the exact current payload assumptions:

```text
resident payload slots  1024
bypass-model slots       128
resident ID              tag/cache index in current production path
bypass global ID         1024 + role-local ID
bank                     global payload ID % 4
fill identity            payload_id + generation + owner/pending-sector checks
```

The current production L2 path allocates/fills resident slots. `reserve_bypass`, `complete_bypass`, and `release_bypass` have no production caller; they are exercised only by directed tests.

This is a major design fact and must remain explicit in all subsequent opportunity claims.

## 2. Payload lifecycle / stale-fill protection — PASS

Resident allocation, rollback, replacement, fill, response completion, WAD and dirty-victim paths are mapped with exact source anchors. The proposed substrate preserves the current `payload_id + generation` ownership contract and tag-array authority.

The risk matrix correctly treats stale fill, double free/leak, bank timing drift, hidden storage, mode/provenance ambiguity and retry-vs-cycle telemetry as independent correctness risks.

## 3. M0 telemetry design — PASS with one sequencing refinement

The generic M0 producer design is good and can be implemented next:

```text
frontend head blocked cycles by exact reason
any-blocked cycle denominator
resident occupancy/slack
useful L2 admit / response enqueue throughput
5K + cumulative scope
```

Crucially, the proposed bypass-candidate fields already say **do not emit until a real semantic producer/consumer contract exists** and must not use dormant `bypass_used()` as a proxy. That is correct.

For the next implementation stage, split M0 conceptually into:

```text
M0a generic, mechanism-neutral observation
M0b mechanism-specific opportunity shadows (RO/TVD/non-resident payload role)
```

Do not delay M0a/M1 while inventing a synthetic bypass workload.

## 4. M1 elastic substrate — PASS / implementation-ready after new handoff

The M1 design is the strongest part of the prep and is accepted as the common behavior-preserving substrate:

```text
one 1152-entry global physical slot array
explicit role/status/owner/generation per slot
tag-index -> payload-id sidecar
payload handle = {payload_id,generation}
global-ID bank mapping payload_id % 4
static-compatible policy
```

M1 must preserve tag policy, descriptor/MSHR/WAD/MissQ/lower behavior and exact bank arbitration. Static/all-OFF equivalence is mandatory before any functional feature is enabled.

The mode-switch design is also accepted: base resource configuration is orthogonal to default-OFF mechanism feature bits; the same source/binary must run baseline and ablations with deterministic config overlays/result roots/provenance.

## 5. MATERIAL DESIGN CORRECTION: Unified Payload opportunity is asymmetric

The source audit creates a stronger constraint than the current M2 document states.

The calibrated structure has:

```text
resident tags          1024 / slice
resident payload quota 1024 / slice
bypass payload quota    128 / slice
```

Under M2 alone, resident tags remain fixed at 1024. Therefore the extra 128 physical payload slots cannot by themselves increase the number of simultaneously resident cache lines:

- if fewer than 1024 resident tags are occupied, the original 1024-resident pool already contains free resident slots;
- if all 1024 resident tags are occupied, there is no additional resident tag to bind a 1025th resident cache line.

So **“resident borrows bypass payload and gains extra resident capacity / avoids eviction” is not a valid standalone M2 capacity claim under the fixed 1024-tag design.** A resident may use a different physical ID, but that is relocation, not added residency.

The realistic standalone shared-pool opportunity is the opposite direction: a real non-resident/pending/TVD payload role may borrow unused resident payload capacity. If no such production role exceeds its protected capacity, M2 has little or no capacity benefit.

This correction must be reflected before M2 functional implementation.

## 6. MATERIAL DESIGN CORRECTION: avoid bank-remapping confounding

Current resident bank identity is effectively tied to `cache_index % 4`. A shared allocator that gives a resident tag an arbitrary global payload ID can change its bank and therefore change conflict/service behavior independently of capacity sharing.

A capacity-elasticity experiment must not accidentally become a bank-remapping experiment.

Recommended M2/M1 rule for resident allocations:

```text
payload_id % 4 == tag_index % 4
```

where practical, using per-bank free lists. If a later policy intentionally changes bank placement, that must be a separate feature/ablation with its own claim.

M1 static mode must preserve the exact old bank class and grant sequence.

## 7. MATERIAL DESIGN CORRECTION: forward-progress reserve must be two-sided/consumer-specific

The proposed `protected_bypass_reserve` correctly recognizes that unrestricted sharing can starve a pending role, but a one-sided reserve is not sufficient as a general proof once bypass/pending traffic can borrow resident slots.

After a real non-resident consumer is defined, the design must prove both:

```text
pending/non-resident forward progress
resident/fill forward progress
```

and rule out circular dependency between slot release and a transaction that itself needs a slot to complete.

Do not freeze a reserve number from the dormant 128-slot model as a performance parameter. Start from a safety bound derived from the actual lifecycle/maximum simultaneously indispensable payload objects, then measure whether a smaller dynamic reserve is safe/useful.

## 8. M3 RO pending-state map — PASS as dependency map

The source map correctly identifies that MSHR currently holds more than just a capacity token: line identity, sector issued/pending/ready state, requester descriptors and response retirement interact with it.

`is_write()==false` / `isatomic()==false` are correctly treated as insufficient to prove read-only safety. A future M0 shadow classification must report exclusion reasons before a functional M3 rule is allowed.

## 9. M4 TVD/WAD map — PASS as dependency map

The WAD is metadata, not a data store. A storage-neutral TVD must transfer an existing resident payload handle into a victim/TVD role or explicitly account an equivalent fixed-budget slot; it cannot silently add a victim data cache.

The preferred transferred-handle direction is consistent with the EP-L2 lifetime-decoupling objective and the fixed-storage rule.

## 10. Mode-switch / experiment plumbing — PASS

Accepted requirements:

```text
base resource configuration separate from feature vector
all feature bits default OFF
same source/SHA/binary baseline and mechanism comparisons
unsupported combinations fail closed
minimal deterministic config overlays
runtime effective-config hash
explicit mode + feature vector in manifest
collision-free result roots
OFF-path parent equivalence for every functional stage
```

## 11. Documentation-mirroring follow-up

Lane-F evidence is currently reviewable on `hrl/ep-l2-mechanism-prep-v0`, but `LANE_F_LATEST.md` / `MECHANISM_IMPLEMENTATION_PREP_r1/` were not mirrored into the permanent coordination branch during this review.

Before archiving Lane F, mirror the documentation-only report/review pack to `hrl/ep-l2-exp-v0` per the project workflow. No source or simulation change is requested.

## Final disposition

```text
MECHANISM_IMPLEMENTATION_PREP           PASS
M0a generic observation design          PASS / ready for implementation handoff
M1 elastic static-equivalent substrate  PASS / ready for implementation handoff
M2 Unified Payload functional start     NOT YET — requires real non-resident consumer/opportunity + corrected bank/reserve contract
M3 RO pending-state                     dependency map accepted; opportunity unknown
M4 TVD/WAD                              dependency map accepted; opportunity unknown
MODE SWITCH                             PASS
```

The recommended next code stage is **M0a + M1**, on the newly accepted D512/L1-BASE/Line-MSHR128 research baseline, with separate commits/checkpoints and no functional Unified/RO/TVD behavior yet.
