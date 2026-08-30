# EP-L2 M1 Interim Checkpoint Request

Status: **PUBLISH NOW WITHOUT DISTURBING LIVE CONVOLUTION/FWT RUNS**

## Purpose

M1 implementation is locally near completion, with long `convolutionSeparable` and `FWT_7_21` equivalence validations still running. Publish a reviewable source/evidence checkpoint now so ChatGPT can review the frozen substrate candidate while those jobs continue normally.

This checkpoint does **not** declare `M1_ELASTIC_SUBSTRATE_REVIEW_READY` or final PASS.

## Hard runtime rule

Do not stop, restart, duplicate, move, rebuild under, or otherwise disturb either live M1 simulator process/result directory:

```text
convolutionSeparable
FWT_7_21
```

After publishing this checkpoint, continue both existing jobs normally.

## Freeze and publish the implementation candidate

Push the exact current M1 implementation source branches used by all completed equivalence rows. Record full immutable:

```text
Core SHA
Framework SHA
accepted D512 parent Core/Framework SHAs
runtime/effective config hashes
trace identities
```

The implementation candidate must be source-frozen while the two long validation jobs finish. Any later source change that affects payload identity/allocation/fill/bank/config semantics invalidates speculative descendants unless separately proven timing-neutral/packaging-only.

## Required interim evidence

Create:

```text
docs/ep_l2/review_packs/M1_ELASTIC_SUBSTRATE_INTERIM_r1/
```

Include at minimum:

```text
README.md
SOURCE_ANCHORS.md
CHANGED_FILES.md
SOURCE_DIFF_SUMMARY.md
PAYLOAD_HANDLE_AND_SIDECAR.md
MODE_SWITCH_EFFECTIVE_CONFIG.md
DIRECTED_LIFECYCLE_TESTS.md
COMPLETED_EQUIVALENCE_STATUS.csv
RUNNING_JOBS_SNAPSHOT.csv
RAW_LOG_INDEX.tsv
VALIDATION_SUMMARY.md
SHA256SUMS
```

The pack must independently prove on the completed evidence:

1. M1 is infrastructure only; no Unified/RO/TVD/adaptive functional behavior is enabled.
2. Static/default behavior preserves resident tag `i -> payload_id i` and the original bank class `payload_id % 4`.
3. Tag->payload sidecar, `{payload_id,generation}` ownership, rollback, replacement and stale-fill protection are coherent.
4. The accepted base-resource configuration is unchanged from the D512 research baseline.
5. Completed natural workloads reproduce accepted-parent cycles and deterministic existing telemetry exactly where required.
6. Omitted/zero functional mechanism features resolve to baseline semantics and invalid combinations fail closed.
7. The two remaining live jobs are healthy and use the exact same frozen implementation candidate.

## Maturity

Use status:

```text
M1_INTERIM_REVIEW_READY
```

The implementation stage remains pending the two long rows and final ChatGPT review.

Do not implement Unified, RO, TVD, M0b functional policy, or performance headroom from this checkpoint by yourself.

## Return path

Update/create:

```text
docs/ep_l2/codex_handoff/LANE_M1_LATEST.md
```

Clearly state:

```text
INTERIM checkpoint only
exact frozen candidate SHAs
completed equivalence count
convolution/FWT still RUNNING
no duplicate/restart
```

Push source branches and documentation/review material, then continue both existing jobs.
