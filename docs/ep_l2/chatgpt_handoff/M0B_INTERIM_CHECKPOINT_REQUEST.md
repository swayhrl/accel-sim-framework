# EP-L2 M0b Interim Checkpoint Request

Status: **PUBLISH NOW WITHOUT DISTURBING LIVE OFF CONTROL**.

## Purpose

M0b already has a parser-valid ON smoke and preliminary observation-only evidence while the exact OFF timing-neutrality control is still running. Publish a source/evidence checkpoint now so ChatGPT can review the producer, epoch/lifetime semantics, and preliminary premise-audit findings without waiting for the OFF control to finish.

This checkpoint is not M0b final PASS.

## Hard runtime rule

Do not stop, restart, duplicate, move, rebuild under, or otherwise disturb the currently running M0b OFF control process/result directory. Continue it normally after publishing this checkpoint.

## Parent maturity

The exact M0a+M1 integration parent has now been promoted by ChatGPT after `M0A_FINAL_PASS` and `M1_FINAL_PASS`. Record the exact runtime parent and the exact M0b candidate Core/Framework SHAs. Any semantic source change after the ON evidence requires a new candidate and invalidates mismatched descendants.

## Required interim review pack

Create:

```text
docs/ep_l2/review_packs/M0B_OPPORTUNITY_INTERIM_r1/
```

Include at minimum:

```text
README.md
SOURCE_ANCHORS.md
CHANGED_FILES.md
M0B_TELEMETRY_CONTRACT.md
EPOCH_AND_LIFETIME_SEMANTICS.md
RO_CLASSIFICATION_PRELIMINARY.md
DIRTY_VICTIM_PREMISE_AUDIT.md
NONRESIDENT_PAYLOAD_PRECONDITION.md
ON_SMOKE_STATUS.csv
OFF_CONTROL_RUNNING_SNAPSHOT.csv
PRELIMINARY_METRICS.csv
RAW_LOG_INDEX.tsv
VALIDATION_SUMMARY.md
SHA256SUMS
```

## Questions the checkpoint must answer

### 1. Source / timing contract

State exact:

```text
integrated parent Core/Framework
M0b Core/Framework candidate
runtime config hash for ON
runtime config hash / expected one-bit delta for OFF
```

Prove M0b fields are observation-only and are not read by admission, allocation, replacement, bank arbitration, MSHR state transition, WAD state transition, lower routing, scheduler, or DRAM behavior.

### 2. Epoch-safe lifetime tracking

Explain the exact identity used for one Line-MSHR instance/epoch so address reuse cannot merge independent lifetimes.

For every milestone state which is:

```text
EXACT_SOURCE_EVENT
DERIVED_FROM_EXACT_EVENTS
NOT_EMITTED
```

Do not fabricate a milestone from an unavailable source event.

### 3. RO candidate semantics

Show the current conservative classification and exclusion reasons. Do not claim that `!is_write()` alone proves safe RO semantics.

Any lifetime after lower issue / all-ready may be described as candidate transferable pending-state lifetime only. Do not call it proven avoidable MSHR lifetime before a functional replacement state is designed and validated.

### 4. Dirty-victim/TVD premise audit

For the ON smoke, provide event counts and direct evidence for:

```text
victim selection
WAD allocation
writeback creation
old resident payload-handle liveness after replacement/reassignment
payload slot reuse/reassignment if observed
writeback issue
set_done / WAD release if emitted
```

If every observed old dirty-victim handle is already non-live after static slot reassignment, state the narrow preliminary conclusion:

```text
CURRENT_MODEL_DOES_NOT_RETAIN_OLD_RESIDENT_PAYLOAD_HANDLE_TO_SET_DONE
```

Do not yet promote this to final mechanism-priority conclusion until OFF neutrality and representative WAD workloads complete.

### 5. Non-resident payload premise

Report actual production payload allocation counts by role. If non-resident production allocation is zero in observed workloads, state:

```text
PRELIMINARY_NO_REAL_NONRESIDENT_CONSUMER_OBSERVED
```

Do not create synthetic bypass traffic or use dormant bypass capacity as opportunity evidence.

### 6. OFF control state

Record the exact process/result path, source/config identity, trace identity, start state and health of the currently running OFF control. It must differ from ON only by the authorized `-gpgpu_ep_l2_m0b_stats 0/1` setting.

## Maturity

Use:

```text
M0B_INTERIM_REVIEW_READY
```

Do not declare final opportunity classifications or start a functional mechanism from this checkpoint without ChatGPT review.

## Return path

Update/create:

```text
docs/ep_l2/codex_handoff/LANE_M0B_LATEST.md
```

Push the frozen source candidate and interim review material, then continue the existing OFF control normally.
