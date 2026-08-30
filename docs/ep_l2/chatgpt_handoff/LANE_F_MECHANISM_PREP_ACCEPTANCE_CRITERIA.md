# EP-L2 Lane F — Mechanism Prep Acceptance Criteria

## A. Source anchoring

Every source claim must cite exact repository path/function/state and exact reviewed source SHA.

If C7e and D512 generalized sources differ, state whether the difference is semantic or observation-only.

## B. No functional modification

PASS only if Lane F does not push functional simulator behavior changes.

The review pack may contain design pseudocode/state tables, but no mechanism result may be presented as implemented.

## C. Payload lifecycle completeness

The source map must cover all payload ownership transitions for resident and bypass/pending roles, including failure/retry/release paths and stale-fill protection.

It must identify every place that currently relies on static role partitioning or payload-ID range assumptions.

## D. M1 behavior-preserving substrate

The proposed substrate must have a static-compatibility mode that can reproduce the accepted baseline exactly.

Required invariant plan:

```text
one live owner per payload_id+generation
no double free
no leaked payload at terminal drain
bank mapping unchanged
static mode role counts remain 1024/128
no change to cache/tag/MSHR/descriptor semantics
```

## E. M2 total-storage discipline

Unified Payload v1 must use the same total 1152 x 128-B payload storage and same 4x288 bank service organization.

Any reserve/watermark must be justified by forward progress/lifecycle semantics, not performance tuning.

## F. M0 telemetry semantics

For every proposed new counter define:

```text
exact production point
event vs cycle semantics
scope/reset/delta semantics
overlap policy
denominator where relevant
expected parser field
```

Cycle-based admission blocking must not be derived by relabeling retry events.

## G. RO source-map safety

The design map must identify request classes that cannot safely use a read-only pending path and the exact state required after Line-MSHR release/avoidance.

If read-only certification cannot currently be proven from simulator request semantics, mark it unresolved.

## H. TVD storage accounting

The TVD design map must explicitly account for data bytes and metadata bits. It must not create a hidden extra data cache outside the comparable L2 storage budget.

## I. Modification sequence

Provide a concrete staged file/function modification order with independent build/test checkpoints:

```text
M0 telemetry
M1 static-equivalent substrate
M2 functional unified payload
later M3/M4
```

Each checkpoint must state rollback boundary and directed-test family.

## J. Completion

Required status:

```text
MECHANISM_IMPLEMENTATION_PREP_REVIEW_READY
```

No `*_READY` functional mechanism status may be declared.
