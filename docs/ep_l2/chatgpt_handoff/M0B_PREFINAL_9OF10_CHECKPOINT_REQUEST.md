# EP-L2 M0b Pre-Final 9-of-10 Checkpoint Request

Status: **PUBLISH NOW; KEEP LIVE SCAN UNDISTURBED**.

## Purpose

M0b has completed all required units except the long `scan` ON observation. Publish a pre-final review pack now so ChatGPT can review source/producer correctness, the nine completed units, OFF/ON neutrality already available, and mechanism-opportunity conclusions before the final scan completes.

The remaining `scan` row is a late breadth/temporal validation gate, not a blocker for source/semantics review.

## Live-job rule

Do not stop, restart, duplicate, move, rebuild under, or otherwise disturb the currently running M0b `scan` ON process/result directory.

After publishing this checkpoint, allow the existing scan to continue naturally.

## Freeze exact source/config

Record exact full immutable:

```text
integrated parent Core / Framework SHAs
M0b Core / Framework implementation SHAs
runtime/effective config hashes
M0b OFF/ON delta
trace identities
```

If any semantic source change has occurred since the currently running scan was launched, report it explicitly and do not mix rows from different producer semantics.

## Required pre-final pack

Create/update:

```text
docs/ep_l2/review_packs/M0B_OPPORTUNITY_PREFINAL_9OF10_r1/
```

Include at minimum:

```text
README.md
SOURCE_ANCHORS.md
CHANGED_FILES.md
TELEMETRY_CONTRACT.md
VALIDATION_SUMMARY.md
COMPLETED_UNIT_STATUS.csv
TIMING_NEUTRALITY_AVAILABLE.csv
RO_OPPORTUNITY_9OF10.csv
RO_LIFETIME_SEMANTICS.md
DIRTY_VICTIM_TVD_PREMISE_9OF10.csv
NONRESIDENT_PAYLOAD_9OF10.csv
MECHANISM_OPPORTUNITY_PREFINAL.md
RUNNING_SCAN_SNAPSHOT.csv
RAW_LOG_INDEX.tsv
SHA256SUMS
```

## Required review questions

The pack must allow independent review of:

1. whether M0b remains observation-only and uses one frozen producer;
2. which nine required units are `COMPLETE_VALID`;
3. which OFF/ON pairs are already exact in cycles, instructions and existing deterministic B0/L1/DRAM artifacts;
4. RO candidate/exclusion counts and available Line-MSHR milestone distributions for completed RO workloads;
5. whether any source-proven safe RO eligibility exists, versus only `candidate_uncertified`;
6. dirty-victim event count and the exact fraction/count where the prior resident payload handle is still live after reassignment;
7. production resident and non-resident payload allocations across the completed workloads;
8. whether the current evidence supports narrowing TVD/shared-payload priority before scan;
9. the exact current scan PID/result/source/config health and progress.

## Interpretation discipline

Use only evidence-supported labels.

For RO:

```text
UNCERTIFIED_CANDIDATE_ONLY
```

unless an actual source-proven conservative eligibility predicate exists.

For TVD, if every observed dirty victim invalidates/reassigns the old resident payload handle before `set_done`, use a narrow current-model label such as:

```text
NO_OLD_RESIDENT_PAYLOAD_HANDLE_HOLD_TO_SET_DONE_OBSERVED
```

Do not generalize beyond the modeled payload identity/lifetime.

For shared payload, if production non-resident allocation remains zero across completed workloads, use:

```text
NO_REAL_NONRESIDENT_CONSUMER_OBSERVED_9OF10
```

and keep final breadth status pending `scan`.

## Maturity

Status must be:

```text
M0B_PREFINAL_9OF10_REVIEW_READY
```

This is not `M0B_OPPORTUNITY_LOCAL_COMPLETE` until scan completes and the final analyzer/pack is refreshed.

## After scan completes

Do not rerun completed rows. Parse only the existing final scan, append its evidence, rerun the read-only final aggregate/equivalence checks, and publish the final M0b pack for a small delta review.
