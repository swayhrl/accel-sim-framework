# EP-L2 M0a + M1 Integration Interim — ChatGPT Review

Status: **CONDITIONAL PASS — authorized as speculative M0b parent**

Maturity remains:

```text
SPECULATIVE_PENDING_GATE
```

Promotion dependencies:

```text
M0A_FINAL_PASS
M1_FINAL_PASS
```

`M1_FINAL_PASS` is now satisfied independently. Final integration promotion still waits for M0a final closeout.

## Reviewed integrated source

```text
M1 Core input         955a50cbb5e8d928b6c7b0c78e1af062b835df44
M0a Core input        666f0ba2d7b6a027f395346e274a934c19fdd3c1
Integrated Core       1fc248aa89abefbd1b417f7f4053cd2bf56d7a1e
Runtime Framework     d61ffd23c926a25fa463a3e6e955c885b45f0f8a
Integration branch    hrl/ep-l2-m0a-m1-int-v0
```

Core lineage is clean: integrated Core is exact M1 plus the frozen M0a observation commit. No functional Unified/RO/TVD/adaptive change was introduced.

## Local integration gates

PASS on compact Banked controls:

```text
vectorAdd_4M
cfd_097k
sad
```

For `BASE_M1_STATIC` versus accepted M1:

- cycles exact;
- instructions exact;
- seven parsed artifact families byte-identical.

For `M0A_ON_M1_STATIC` versus integrated BASE:

- cycles exact;
- instructions exact;
- seven existing parsed artifact families byte-identical;
- only the M0a telemetry mode changes.

Release build, M1 directed lifecycle tests, M0a parser/cardinality tests, integrated mode/config tests, and `git diff --check` pass.

## M0a reason-semantics correction

`m0_frontend_head_any_blocked_cycles` is accepted as the exact once-per-observed-cycle blocked total.

Per-reason fields are **production-visible / stage-primary** reason accounting. They are not an exhaustive independent all-resource multi-cause bitset because `preview_access()` may return after earlier pipeline-stage blockers and MSHR `full_reason` is priority-encoded. Do not sum reason fields, and absence of a later reason does not prove that resource was available in an earlier-stopped cycle.

No producer rerun is required for this semantic narrowing.

## Accidental integration-scan launch

The pack records that an integration `scan` copy was accidentally launched and immediately terminated before status publication. It is not present in the accepted RAW_LOG_INDEX, which contains only the six compact control rows. No integration result or scientific claim uses that attempted scan. This does not invalidate the child.

## Decision

The integration source may be used **now** as the exact parent for speculative, observation-only M0b implementation and computation.

Any M0b descendant must remain `SPECULATIVE_PENDING_GATE` until the integrated parent is promoted after `M0A_FINAL_PASS`.

A real source/producer/timing defect discovered by M0a final review invalidates affected descendants. Packaging/parser-only corrections may be reprocessed without simulator rerun when runtime source/config identity is unchanged.
