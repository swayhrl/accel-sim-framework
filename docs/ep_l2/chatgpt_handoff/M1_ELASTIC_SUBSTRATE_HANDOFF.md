# EP-L2 M1 — Behavior-Preserving Elastic Payload Substrate Handoff

Status: **AUTHORIZED AFTER BASELINE_DECISION_PASS**

## Objective

Refactor the current static resident/bypass payload representation into a global physical payload-handle substrate that can support later non-resident roles, while preserving the accepted D512 research baseline **exactly** under the default static policy.

M1 is infrastructure. It must not create capacity borrowing, RO pending-state, TVD, adaptive policy, bank-placement optimization or any functional performance mechanism.

## Semantic parent / base resources

Use:

```text
Core      878f80869ce212e779df20b6421e4dc7f987825d
Framework aae62b66685f15437cecf0193934f628e6fac6ae
```

Accepted calibrated resources are fixed by ADR-005:

```text
Descriptor 512
Line MSHR 128
per-address cap 32
L1 BASE
WAD 128
payload 1152 x 128 B / slice
4 x 288 banks, payload_id % 4
L2->DRAM 128
scheduler 128
ReturnQ 192
DRAM 850 MHz
```

## Isolation

Prefer:

```text
Framework /workspace/worktrees/accel-sim-ep-l2-m1/
Core      /workspace/worktrees/gpgpu-sim-ep-l2-m1/
branch    hrl/ep-l2-m1-elastic-substrate-v0
results   /workspace/results/ep_l2_m1_equivalence/
```

M0a worktrees/results are read-only to M1.

## Accepted source-design parent

Read Lane-F accepted design evidence:

```text
docs/ep_l2/chatgpt_handoff/LANE_F_MECHANISM_PREP_CHATGPT_REVIEW.md
```

and the original detailed pack on `hrl/ep-l2-mechanism-prep-v0`:

```text
docs/ep_l2/review_packs/MECHANISM_IMPLEMENTATION_PREP_r1/
  SOURCE_MAP.md
  PAYLOAD_LIFECYCLE.md
  M1_ELASTIC_SUBSTRATE_DESIGN.md
  RISK_AND_INVARIANT_MATRIX.md
  EXPERIMENT_MODE_SWITCH_DESIGN.md
```

Also read ADR-007: M1 becomes infrastructure, not a long-term functional feature bit.

## Required implementation shape

### 1. One physical payload-ID namespace

Replace role-local physical identity with a global physical ID:

```text
0 <= payload_id < 1152
bank = payload_id % 4
```

Represent each physical slot with explicit state sufficient for the current lifecycle:

```text
role
status
owner line address / invalid
current generation
pending sector mask
other existing dirty/valid state required by current store
```

Do not remove existing owner/generation/stale-fill checks.

### 2. Payload handle

Use one canonical handle concept:

```text
{payload_id, generation}
```

The existing `mem_fetch` fields already carry this identity. Avoid introducing a second independent payload identity unless source correctness proves it necessary.

### 3. Tag-to-payload sidecar

Add a mapping indexed by the 1024 tag-array cache indices:

```text
tag_payload_id[tag_index]
```

or an equivalent handle mapping.

The tag array remains authoritative for tag/sector residency validity. The sidecar only decouples physical payload ID from tag-array index.

### 4. Static policy — baseline behavior

The post-M1 **default/all-functional-features-OFF** path uses static policy and must reproduce current semantics:

```text
resident tag_index i -> payload_id i
bypass-model local id j -> payload_id 1024+j
```

No production bypass consumer is added.

This exact mapping preserves the existing resident bank class and avoids a capacity/bank-remapping change.

### 5. Common allocator/lifecycle API

Refactor allocation/release/rollback/fill/request paths into one global-handle-capable substrate, but static policy chooses the old IDs.

Required lifecycle operations conceptually include:

```text
reserve
rollback reserve
owner/generation validation
note lower-read sectors
complete fill
request bank service
release
```

Exact C++ API names are implementation decisions; avoid unnecessary surface-area churn.

### 6. Generation / reuse

Before a released physical ID becomes a new live incarnation, old `{id,generation}` handles must be invalidated so late fills cannot bind to the new owner.

No double free, no release while a pending sector/fill still owns the incarnation, no stale sidecar.

### 7. Bank service

M1 must not alter:

```text
bank count
bank mapping
immediate idle grant
oldest-ready pending priority
one arbitrary operation/bank/cycle
```

For every static-mode resident stream, payload ID and bank must be the same as the accepted parent.

## Baseline / feature switching

Follow:

```text
docs/ep_l2/project_spec/EXPERIMENT_MODE_SWITCH_CONTRACT.md
docs/ep_l2/project_spec/decisions/ADR-007-m1-substrate-is-infrastructure.md
```

After M1, the new substrate is the implementation infrastructure. Do **not** keep two long-lived competing payload stores solely to provide an `elastic_substrate` experiment bit.

The formal post-M1 baseline is:

```text
all functional mechanism bits OFF
payload policy static
```

Future functional bits are Unified/RO/TVD/etc., not M1 itself.

A temporary local bring-up selector is allowed only if removed or made non-semantic before M1 closeout.

## Explicitly forbidden

Do not:

```text
allow resident to allocate an arbitrary/free payload ID in the accepted static mode
allow bypass/nonresident borrowing
create production bypass traffic
change resident tag count
change replacement policy
change tag selection
change MSHR/descriptor semantics
change WAD
change bank placement/arbitration
implement Unified/RO/TVD
change total physical storage
```

## Required directed test families

At minimum:

1. empty/init mapping and invalid sidecar.
2. resident MISS reserve -> lower -> fill -> hit -> release/replacement.
3. sector merge/pending-sector identity.
4. rollback after WAD hazard/full and base admission failure restores both slot and sidecar.
5. late/stale fill rejected after release/reuse generation change.
6. replacement of old resident on same static payload ID.
7. full-sector locally absorbed write path.
8. dormant bypass unit-test lifecycle still maps 1024..1151 exactly; no production caller is introduced.
9. same-bank arbitration replay gives identical bank/grant order.
10. terminal drain: no live slot/sidecar/pending bank retry/resource leak.

## Natural equivalence

After directed correctness, prove post-M1 static baseline vs accepted D512 parent on at least:

```text
vectorAdd_4M
convolutionSeparable
cfd_097k
sad
FWT_7_21
```

Compare:

```text
cycles/instructions
existing target summary/slice/kernel/bank/window/L1/DRAM parsed artifacts where deterministic
DRAM read/write traffic
bank logical/conflict/wait behavior
payload occupancy/terminal consistency
MSHR/descriptor/WAD blockers
terminal invariants
```

Prefer byte-identical parsed artifacts where source/output schema is unchanged. Any mismatch must be explained and reviewed; do not normalize it away.

## Deliverables

```text
docs/ep_l2/codex_handoff/LANE_M1_LATEST.md
docs/ep_l2/review_packs/M1_ELASTIC_SUBSTRATE_r1/
```

Required pack files include:

```text
README.md
SOURCE_ANCHORS.md
SOURCE_SEMANTIC_MAP.md
CHANGED_FILES.md
PAYLOAD_HANDLE_CONTRACT.md
SIDECAR_LIFECYCLE.md
MODE_SWITCH_EFFECTIVE_CONFIG.md
VALIDATION_SUMMARY.md
DIRECTED_TEST_MATRIX.md
BASELINE_EQUIVALENCE.csv
RAW_LOG_INDEX.tsv
SHA256SUMS
validation/
```

## STOP

STOP at:

```text
M1_ELASTIC_SUBSTRATE_REVIEW_READY
```

Do not enable a functional shared policy or run a mechanism performance campaign.
