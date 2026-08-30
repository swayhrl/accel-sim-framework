# EP-L2 M3A — RO Certification / Pending-State Minimality Handoff

Status: **AUTHORIZED IN PARALLEL WITH M0b FINAL SCAN**.

M3A is a source/design + narrowly observation-only stage. It does not implement functional MSHR bypass/release.

## Objective

Convert M0b's large `UNCERTIFIED_CANDIDATE_ONLY` population into a defensible architectural decision.

Answer:

```text
1. Does a conservative source-proven safe request class exist?
2. If yes, what exact state must remain live after leaving the traditional Line-MSHR?
3. Is that state materially smaller/different than the current Line-MSHR entry?
4. What is the safest useful release boundary?
5. Is more observation needed before functional M3 v1?
```

## Source anchors

Use the reviewed M0b source family as the audit parent:

```text
Integrated parent Core  1fc248aa89abefbd1b417f7f4053cd2bf56d7a1e
M0b Core                9907b7e617ea0ee6580fb8156e985838720f08fa
M0b runtime Framework   8a0299cab19a658d34b7a2dc0b6d91e8373c121b
```

M3A runtime evidence, if any, remains dependent on final M0b source/config confirmation. Source/design work may proceed immediately.

Create isolated worktrees:

```text
Framework /workspace/worktrees/accel-sim-ep-l2-m3a-ro-cert/
Core      /workspace/worktrees/gpgpu-sim-ep-l2-m3a-ro-cert/
branch    hrl/ep-l2-m3a-ro-cert-v0
results   /workspace/results/ep_l2_m3a_ro_cert/
```

## A. Certification audit

Audit every production request class entering the target L2 miss/MSHR path.

A `SAFE_RO_ELIGIBLE` predicate must be based on source-proven semantics, not merely:

```text
!is_write()
!isatomic()
```

Explicitly audit at minimum:

```text
memory access type / read-write-atomic class
write-allocate synthetic reads
pending writers to the same line
read-after-write / write-after-read ordering rules
sector merges
same-address descriptor/per-line cap semantics
L1/L2 writeback traffic
cache-policy-specific local write absorption
fill ownership / generation validation
late merge after first fill/all-ready
response ordering and response-queue backpressure
```

If a conservative safe subset cannot be proven, return `NO_SOURCE_PROVEN_SAFE_CLASS` rather than weakening the predicate.

## B. Traditional Line-MSHR state inventory

Produce a field/state-level inventory of what one Line-MSHR instance currently owns:

```text
line key / identity
issued sectors
pending sectors
ready sectors
requester descriptor references
per-request sector masks
ready-response ordering
write/order state
any timestamps/debug-only state
```

Separate:

```text
state that must survive for correctness
state already represented elsewhere (descriptor/tag/payload)
state needed only until lower issue
state needed only until all-ready
state needed only for response retirement
```

Do not claim a metadata saving until duplicated/moved state is explicitly accounted.

## C. Compare two M3 boundaries

### Candidate A — pre-fill pending-state replacement

After all required lower requests are safely issued, replace the traditional Line-MSHR with a smaller pending object while fills remain outstanding.

This is the more aggressive option and requires proof that all merge/order/fill state survives.

### Candidate B — all-ready / response-tail decoupling

After all required sectors are ready, move response-ready requester state out of the Line-MSHR and free the line entry while L2->ICNT enqueue/backpressure continues.

This is potentially safer because fill completion has already occurred.

For each boundary specify:

```text
exact transition event
state copied/moved
state retained in tag/payload/descriptor
new lookup key
late-request behavior
ordering behavior
release/terminal conditions
failure/rollback behavior
```

Recommend the simplest boundary whose correctness can be proven and whose measured opportunity is nontrivial.

## D. Close missing lifetime evidence if needed

M0b does not emit:

```text
allocation -> final retirement
all-ready -> final retirement
last lower issue -> final retirement
```

If response-tail length is needed to choose Candidate B, add a **default-OFF observation-only callback** at the exact final requester/Line-MSHR retirement point and an epoch-safe measurement.

If a safe exact last-lower-issue boundary can be proven and observed without changing behavior, instrument it as well.

Any new telemetry must:

```text
be default OFF
not affect MSHR/cache behavior
preserve exact OFF/ON timing neutrality
use epoch-safe instance identity
use NOT_EMITTED for unsupported milestones
```

Do not add telemetry merely to fill a table; add only what changes the M3 design choice.

## E. Metadata / storage cost

For current Line-MSHR and each proposed pending object, give transparent hardware-oriented state estimates per line and per slice for a reasonable bit-width range where exact hardware width is not represented by the simulator.

Keep requester descriptors separately accounted; do not hide them inside the pending-object saving.

## F. Directed correctness plan

Before any future functional M3 implementation, define directed tests for:

```text
single-sector read miss
multi-sector read miss
same-line merged readers
late merge before first fill
late merge after partial fill
read/write same-line exclusion
atomic exclusion
writeback exclusion
stale/late fill generation
response queue backpressure
address reuse / new epoch
terminal drain
```

## Deliverables

Create:

```text
docs/ep_l2/review_packs/M3A_RO_CERTIFICATION_r1/
  README.md
  REQUEST_CLASS_CERTIFICATION.md
  SAFE_ELIGIBILITY_PREDICATE.md
  LINE_MSHR_STATE_INVENTORY.md
  CANDIDATE_A_PREFILL_PENDING_DESIGN.md
  CANDIDATE_B_ALL_READY_TAIL_DESIGN.md
  LIFETIME_GAP_MEASUREMENT.md
  METADATA_COST.md
  DIRECTED_TEST_PLAN.md
  SOURCE_MAP.md
  DECISION_MATRIX.md
  VALIDATION_SUMMARY.md
  RAW_LOG_INDEX.tsv          # only if new runtime observations are executed
  SHA256SUMS
```

Update:

```text
docs/ep_l2/codex_handoff/LANE_M3A_LATEST.md
```

## STOP

Required completion state:

```text
M3A_RO_CERTIFICATION_REVIEW_READY
```

STOP for ChatGPT review before implementing a functional M3 transition.
