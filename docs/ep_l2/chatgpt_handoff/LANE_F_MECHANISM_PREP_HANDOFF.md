# EP-L2 Lane F — Mechanism Source Audit / Implementation Prep

Status: **AUTHORIZED IN PARALLEL WITH LANE D**.

This lane is source/design analysis only. It exists to reduce the delay between final calibration review and the first functional EP-L2 implementation.

## Objective

Translate `project_spec/MECHANISM_IMPLEMENTATION_PLAN.md` into a concrete source-level build plan for M0/M1/M2, while also mapping M3/M4 dependencies.

Do not choose the final primary baseline or implement a functional mechanism in this lane.

## Required source anchors

Read and audit both semantic families:

Formal C7e:

```text
Core      ece1a3a77c5628763e0a4605bfd1c639ee6a1495
Framework f08d2ce857972fad73c4e1ab7162ba94c6336507
```

D512 generalized candidate:

```text
Core      878f80869ce212e779df20b6421e4dc7f987825d
Framework aae62b66685f15437cecf0193934f628e6fac6ae
```

Use the D512 source family when it provides behavior-preserving telemetry/cardinality generalization, but do not silently choose D512 as the new primary baseline.

## Audit tasks

### F1 — payload source/state map

Identify exact files/classes/functions for:

```text
resident payload allocation/free
bypass/pending payload allocation/free
static resident/bypass role boundary
payload_id assignment
payload generation/version checks
payload owner metadata
bank mapping and arbitration
fill validation and stale-fill rejection
resident hit/read/write payload access
bypass/pending payload service
```

Produce state diagrams for allocation -> use -> release.

### F2 — M1 elastic substrate design

Specify the smallest behavior-preserving refactor needed to make payload role an explicit allocation attribute instead of a hidden/static index-range assumption.

The first mode must still reproduce 1024+128 static roles exactly.

Specify:

```text
new/changed data structures
allocator API
owner/role state
free-list representation
bank mapping preservation
release paths
assertions/invariants
config mode
migration strategy
```

### F3 — Unified Payload v1 design

Design, but do not implement, shared 1152-slot capacity allocation over the same 4x288 banks.

Audit forward-progress requirements and identify whether a protected reserve is needed for pending/bypass traffic. Do not invent a reserve amount without source/lifecycle justification.

Specify candidate allocation policies and their trade-offs:

```text
fully shared
shared + demand-aware reserve
shared + role watermark/hysteresis
```

Recommend the simplest safe v1.

### F4 — M0 opportunity telemetry delta

Compare existing C7e/Lane-D telemetry with the gaps in `MECHANISM_IMPLEMENTATION_PLAN.md`.

Produce exact proposed producer points/field semantics for only the telemetry needed before M2:

```text
cycle-based L2 admission blocked reasons
resident/bypass role occupancy/slack and complementarity
shadow shared-pool allocation opportunity
useful L2 throughput if practical
```

Keep RO/TVD-specific telemetry as a separate later subsection unless it is nearly free to expose.

### F5 — RO pending-state source map

Map:

```text
Line-MSHR allocation/merge/full/release
request descriptor lifetime
pending sector masks
tag state transitions around miss/fill
fill ownership validation
read/write/atomic request typing
requester response enqueue completion
```

Identify the exact safe point(s) where a certified read-only transaction could theoretically stop consuming the traditional Line-MSHR while retaining sufficient pending state.

Do not claim eligibility until request semantics prove it.

### F6 — WAD/TVD source map

Map:

```text
victim selection
resident dirty payload ownership
writeback creation
WAD allocation
lower-path writeback lifetime
memory_partition_unit::set_done()
WAD release
resident payload release timing
```

Identify what data storage would be required for TVD and how it can remain within a comparable total L2 storage budget.

## Deliverables

Create:

```text
docs/ep_l2/review_packs/MECHANISM_IMPLEMENTATION_PREP_r1/
  README.md
  SOURCE_MAP.md
  PAYLOAD_LIFECYCLE.md
  M1_ELASTIC_SUBSTRATE_DESIGN.md
  M2_UNIFIED_PAYLOAD_V1_DESIGN.md
  M0_TELEMETRY_DELTA.md
  M3_RO_PENDING_SOURCE_MAP.md
  M4_TVD_WAD_SOURCE_MAP.md
  MODIFICATION_SEQUENCE.md
  RISK_AND_INVARIANT_MATRIX.md
  CHANGED_FILES_EXPECTED.md
```

Update:

```text
docs/ep_l2/codex_handoff/LANE_F_LATEST.md
```

## Hard boundary

No functional simulator source modification is authorized in this lane.

Do not:

```text
implement shared payload allocation
change baseline capacities
change MSHR lifetime
add TVD storage
change WAD semantics
run mechanism experiments
```

Small throwaway local source inspection patches are not evidence and must not be pushed as functional changes.

Status on success:

```text
MECHANISM_IMPLEMENTATION_PREP_REVIEW_READY
```

Then STOP for ChatGPT review / baseline-decision integration.
