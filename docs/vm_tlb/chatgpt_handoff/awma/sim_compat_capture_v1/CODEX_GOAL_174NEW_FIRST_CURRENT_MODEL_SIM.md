# CODEX GOAL — 174-new First Current-Model Simulation Integration

Run on **174-new / port 2239** in a fresh worktree/branch.

Suggested branch:

```text
hrl/awma-first-current-model-sim-174new-v1
```

This Goal may start before node109 finishes capture. Complete all CPU/runtime/control-plane preparation first, then consume the producer bundle only after it is READY and independently verified.

## Goal

Close the consumer half of `SIM_COMPAT_CAPTURE_V1` and, if admission passes, execute the first current-model bounded baseline simulation on `NEW_SIM_BASELINE_V1`.

Preferred final state:

```text
SIM_COMPAT_CAPTURE_V1_QUALIFIED
FIRST_CURRENT_MODEL_BASELINE_SIM_PASS
```

## Phase 0 — Repair stale baseline review summaries inline

Do not rerun C12 merely for documentation cleanup.

Audit `docs/vm_tlb/review_packs/AWMA_NEW_SIM_BASELINE_174NEW_V1/` and reconcile stale pre-recovery summaries such as:

```text
C12_PREFILL_CALIBRATION.tsv
C12_DECODE_CALIBRATION.tsv
SMOKE_LADDER_RESULTS.tsv
OPEN_ISSUES.md
EXTERNAL_BLOCKER.md
```

with the accepted successful evidence:

```text
HISTORICAL_TRACE_RECOVERY_ADDENDUM.md
BASELINE_QUALIFICATION_DECISION.json
NEW_SIM_BASELINE_174NEW_REPORT.md
```

Update only control-plane summaries/receipts justified by existing evidence. Preserve:

```text
NEW_SIM_BASELINE_V1_QUALIFIED
scope = HASH_BOUND_FIXED_WINDOW_10000
```

Regenerate review-pack `SHA256SUMS` and note the repair in this stage's review pack.

## Phase A — Freeze consumer baseline identity

Re-read and hash-bind:

- Framework/Core source commits;
- qualified simulator binary;
- toolchain/build receipt;
- base/F0 or selected current config and VM overlay;
- telemetry exporter/normalizer source;
- fixed-window policy.

Create/reuse a deterministic `SIM_BASELINE_ID`. If any semantic baseline field changed, issue a new ID and explain why.

## Phase B — Consumer/parser preparation before producer arrival

Strengthen admission so a formal producer bundle is checked by an **actual traceg parser/grammar smoke**, not merely xz non-emptiness.

Reuse the historical recovered trace bundle as a regression fixture where useful.

Required negative tests:

```text
missing sync_control
bad kernelslist member
hash mismatch
malformed traceg record
missing width/access semantics
nonzero drop/overflow
partial terminal
C16WARP1/MREF input
```

All must fail closed without `SIM_INPUT_ID`.

## Phase C — Wait/ingest through accepted pipeline

Do not poll aggressively or mutate producer directories.

When node109 publishes the READY bundle:

1. verify transfer receipt;
2. independently hash all files;
3. verify producer manifest identity;
4. verify model/input/target binding against accepted authority;
5. move/admit according to existing immutable raw pipeline rules;
6. never repair producer trace bytes in place.

If a recoverable packaging/path issue exists but bytes are valid, create a derived compatibility view/manifest rather than mutating raw.

## Phase D — Formal SIM_INPUT admission

Run the AWMA consumer contract.

PASS requires:

- required semantics including sync/control;
- actual parser/grammar smoke;
- list/payload/sidecar closure;
- COMPLETE terminal;
- drop/overflow zero;
- stable `SIM_INPUT_ID` on repeated admission.

Write immutable catalog entry and snapshot.

## Phase E — Structural trace sanity before simulation

Produce bounded structural statistics from the admitted trace:

```text
kernel count / selected target scope
instruction/warp record counts
memory instruction counts by access kind/memory space/width
active-mask sanity
address/page/cache-line footprint where derivable without changing semantics
control/sync marker counts
```

These are simulator-input structural diagnostics, not replacements for Native evidence.

If exact WORKLOAD/TARGET identity matches an accepted Native target, record relation:

```text
EXACT_WORKLOAD_TARGET_DIFFERENT_CAPTURE
```

Do not numerically calibrate Native vs Simulation yet.

## Phase F — First current-model bounded baseline replay

Run only the admitted formal current-model target on `NEW_SIM_BASELINE_V1`.

Start with the frozen fixed-window policy:

```text
10000 cycles
```

Record:

```text
SIM_INPUT_ID
SIM_BASELINE_ID
config/overlay SHA
command/environment receipt
raw log SHA
execution status
simulated instruction/cycle counters
VM/TLB/PTW/PWC telemetry
L1/L2/cache/memory/DRAM telemetry
performance/stall telemetry available within scope
```

A fixed-window timeout is acceptable only when it is the expected wrapper boundary and no simulator assert/fatal/parser abort occurred.

## Phase G — Determinism/repeat

Repeat the bounded current-model replay at least once when practical.

Check deterministic or expected-stable invariants:

```text
input/baseline/config identities
completion/window boundary
normalized telemetry SHA or field-wise equality
critical VM/TLB/PTW/cache counters
```

Any nondeterminism must be characterized before FORMAL acceptance.

## Phase H — Normalize and catalog

Generate canonical Simulation Evidence rows. Write immutable entries/snapshots for:

```text
SIM_INPUT
SIM_BASELINE
SIM_RUN
SIM_EVIDENCE
```

Store large raw logs/traces outside Git; Git contains manifests, hashes, summaries and source code only.

## Phase I — Optional second target

Only if node109 supplies a second already-qualified formal bundle and the first target has closed completely, repeat admission + bounded baseline replay. Do not delay stage closure merely to increase target count.

## Required review pack

```text
docs/vm_tlb/review_packs/AWMA_FIRST_CURRENT_MODEL_SIM_174NEW_V1/
```

Minimum:

```text
README.md
SOURCE_ANCHORS.md
BASELINE_CONTROL_PLANE_REPAIR.md
BASELINE_IDENTITY.json
CONSUMER_VALIDATOR_CHANGES.md
SIM_INPUT_ADMISSION.tsv
TRACE_STRUCTURE_SUMMARY.tsv
CROSSVIEW_IDENTITY_RELATION.tsv
BASELINE_REPLAY_RESULTS.tsv
REPEAT_DETERMINISM.tsv
SIMULATION_EVIDENCE_SUMMARY.tsv
CATALOG_RECEIPTS.md
TEST_AND_REGRESSION_SUMMARY.md
CLAIM_BOUNDARY.md
OPEN_ISSUES.md
SHA256SUMS
```

Codex report:

```text
docs/vm_tlb/codex_handoff/awma/FIRST_CURRENT_MODEL_SIM_174NEW_REPORT.md
```

## Solve-and-continue rule

Recoverable engineering issues — parser portability, stale paths, runtime wrapper details, catalog formatting, transfer packaging, obvious review-pack inconsistencies — must be solved inline, regression-tested and documented. Do not STOP simply to ask for a cleanup round.

STOP early only for a genuine scientific-semantic mismatch, corrupt/unrecoverable producer bytes, or externally unavailable input after the producer has explicitly failed.

## Forbidden

- no 109 GPU control from this Goal beyond consuming READY output;
- no C16WARP1→traceg fabrication;
- no mechanism/Segment/cache-variant sweep;
- no full-ROI claim from the fixed-window baseline;
- no mutation of accepted Native raw.
