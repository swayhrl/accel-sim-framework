# EP-L2 M0a Interim Checkpoint Request

Status: **PUBLISH NOW WITHOUT DISTURBING LIVE SCAN**

## Purpose

M0a is locally near completion, with the long `scan` validation still running. Publish a reviewable source/evidence checkpoint now so ChatGPT can review the frozen implementation candidate while the live scan continues normally.

This checkpoint does **not** declare `M0A_OBSERVABILITY_REVIEW_READY` or final PASS.

## Hard runtime rule

Do not stop, restart, duplicate, move, rebuild under, or otherwise disturb the currently running M0a `scan` simulator process/result directory.

After publishing this checkpoint, continue the existing scan normally.

## Freeze and publish the implementation candidate

Push the exact current M0a implementation source branches used by the completed rows. Record full immutable:

```text
Core SHA
Framework SHA
parent D512 Core/Framework SHAs
runtime/effective config hashes
trace identities
```

If the source is still changing for reasons other than a proven packaging/parser-only fix, say so and do not call the candidate frozen.

## Required interim evidence

Create:

```text
docs/ep_l2/review_packs/M0A_OBSERVABILITY_INTERIM_r1/
```

Include at minimum:

```text
README.md
SOURCE_ANCHORS.md
CHANGED_FILES.md or source diff summary
TELEMETRY_CONTRACT.md
DIRECTED_TESTS.md
COMPLETED_WORKLOAD_STATUS.csv
OFF_ON_EQUIVALENCE.csv
M0A_INTERIM_METRICS.csv
RUNNING_JOBS_SNAPSHOT.csv
RAW_LOG_INDEX.tsv
VALIDATION_SUMMARY.md
SHA256SUMS
```

The pack must make it possible to independently answer:

1. Are the new M0a fields observation-only and absent from admission/arbitration decisions?
2. Are exact production points, cycle/event semantics, overlap policy and denominators correct?
3. Does M0a OFF reproduce the accepted D512 parent exactly?
4. For completed natural workloads, does M0a ON preserve cycles/existing deterministic telemetry while emitting only new observation fields?
5. Which representative workloads are complete and what generic blocked-cycle/useful-service signals are already visible?
6. What exact command/process/result path remains live for scan and is it healthy?

## Maturity

Use status:

```text
M0A_INTERIM_REVIEW_READY
```

Completed rows may be locally valid, but the M0a stage itself remains pending final scan and final ChatGPT review.

Do not authorize M0b or a functional mechanism from this checkpoint by yourself.

## Return path

Update/create:

```text
docs/ep_l2/codex_handoff/LANE_M0A_LATEST.md
```

Clearly state:

```text
INTERIM checkpoint only
exact frozen candidate SHAs
completed workload count
scan still RUNNING
no duplicate/restart
```

Push source branches and documentation/review material, then continue the existing scan.
