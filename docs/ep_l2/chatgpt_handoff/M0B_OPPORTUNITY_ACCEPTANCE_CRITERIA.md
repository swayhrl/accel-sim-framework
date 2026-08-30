# EP-L2 M0b Opportunity — Acceptance Criteria

## A. Parent identity

Use exact speculative parent:

```text
Core      1fc248aa89abefbd1b417f7f4053cd2bf56d7a1e
Framework d61ffd23c926a25fa463a3e6e955c885b45f0f8a
```

All M0b rows remain `SPECULATIVE_PENDING_GATE` until parent promotion.

## B. Observation-only correctness

No M0b state may affect admission, replacement, payload allocation, MSHR/descriptor transitions, WAD semantics, bank arbitration, lower routing, or response retirement.

M0b OFF vs ON controls must match exactly in cycles/instructions and all pre-existing deterministic parsed artifacts.

## C. RO classification discipline

A safe-eligible label requires a source-proven conservative predicate. `!is_write()` alone is insufficient.

Every excluded or uncertified request class must retain an explicit reason. Unknown semantics remain unknown.

## D. MSHR lifetime semantics

Each measured lifetime must use an instance/epoch identity robust to address reuse.

Each milestone must correspond to an exact source event. Missing milestones use `NOT_EMITTED`.

Candidate transferable lifetime must not be relabeled as proven avoidable MSHR lifetime.

## E. WAD/TVD premise audit

PASS requires direct evidence about whether a dirty victim's old payload handle remains live after writeback creation and whether that identity blocks reuse before `set_done`.

If no such hold exists in the current model, the report must explicitly reject an early-payload-release TVD opportunity rather than force one.

## F. Shared-payload precondition

Do not create synthetic bypass/non-resident traffic. Audit production callers only.

If no real non-resident payload consumer exists, report `NO_REAL_CONSUMER_YET`.

## G. Correlation semantics

M0a `any_blocked_cycles` is the exact blocked total. M0a per-reason fields remain production-visible/stage-primary and are not an exhaustive independent bitset.

Do not sum reason fields or infer unavailable/available resources from unseen later stages.

## H. Validation

Required:

```text
Release build
relevant M1/M0a directed regressions
new RO classification tests
new lifetime instance/reuse tests
new WAD/victim timeline tests
parser/analyzer tests
M0b OFF/ON exact controls
git diff --check
terminal invariants
clean frozen worktrees
```

## I. Workload coverage

RO: convolutionSeparable, spmv, vectorAdd_4M, scan, sad.

WAD/TVD: dwt2d, FWT_7_21, scan, cfd_097k, sad.

Runs may execute in parallel in unique result roots.

## J. Completion

Local completion status:

```text
M0B_OPPORTUNITY_LOCAL_COMPLETE
```

Evidence maturity remains:

```text
SPECULATIVE_PENDING_GATE
```

Stop for ChatGPT review before any functional RO/TVD/shared-payload implementation.
