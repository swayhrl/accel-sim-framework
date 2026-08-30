# EP-L2 Motivation — Final Preflight Finish Request

Status: **AUTHORIZED — finish preflight only**

## Frozen source candidate

Use exactly:

```text
Core      2f9d984cc25422353bdf0270c6c27c82502f77c9
Framework 549e3db7b87d2c51686e2ca2435994be770df88e
branch    hrl/ep-l2-motivation-v0
```

All paper-facing pilot/preflight evidence must use this exact pair. Earlier results produced before the demand-write scope correction are diagnostic only.

## Current accepted partial state

- Corrected WBUF release boundary is implemented.
- EPL2MOTV1 parser is streaming and selects the final cumulative application record per slice.
- Demand read + demand write miss classifier scope is implemented.
- Release build and directed regressions have passed locally according to the latest Codex report.
- Final corrected `vectorAdd_4M` OFF/ON control has passed on the frozen pair.

## Remaining final-provenance pilot runs

Launch in parallel where host resources permit; do not serialize them:

```text
convolutionSeparable  MOTIVATION_ON
convolutionSeparable  MOTIVATION_OFF
sad                   MOTIVATION_ON
sad                   MOTIVATION_OFF
spmv                  MOTIVATION_ON
```

`spmv` does not require an OFF twin for Gate B, but its paper-facing pilot row must be regenerated on the frozen pair because pre-scope-fix results are diagnostic.

The already-completed corrected `vectorAdd_4M` OFF/ON pair remains valid and must not be rerun unless provenance/invariant checks fail.

## Required checks after the five runs

1. All five new runs are `COMPLETE_VALID` with the exact frozen source/config provenance.
2. Gate-B exact OFF/ON neutrality closes for:
   - `vectorAdd_4M`
   - `convolutionSeparable`
   - `sad`
3. Pilot ON rows for:
   - `vectorAdd_4M`
   - `convolutionSeparable`
   - `spmv`
   - `sad`
   all pass the final EPL2MOTV1 parser and accounting gates.
4. For each final ON pilot and C={4,8,16}:
   - exclusive category counts sum exactly to projected blocked miss-admission cycles;
   - `OTHER` is reported explicitly;
   - no WBUF accepted count exceeds created count;
   - final terminal `wb_packets_terminally_outstanding` must be zero for a fully drained valid run, or the run must be held for review rather than silently accepted.
5. Reuse bins sum to 1.0 whenever reuse instances are nonzero.
6. Capture host wall time and peak RSS for at least the final `vectorAdd_4M` and `convolutionSeparable` OFF/ON controls to satisfy host-overhead sanity.
7. All directed regressions, parser tests, Release build, terminal invariants, `git diff --check`, and clean-status evidence are included in the review pack.

## Diagnostic boundary

Do not mix any pre-scope-fix `vectorAdd`, `spmv`, `sad`, or `convolutionSeparable` blocking/WBUF results into formal pilot tables. Preserve them only as `PRE_SCOPE_FIX_DIAGNOSTIC` evidence where useful.

## Deliverable

Publish:

```text
docs/ep_l2/review_packs/MOTIVATION_FIGURES_PREFLIGHT_r1/
docs/ep_l2/codex_handoff/LANE_MOTIVATION_LATEST.md
```

Required status:

```text
MOTIVATION_INSTRUMENTATION_PREFLIGHT_REVIEW_READY
```

Do not start the broad 10-workload motivation campaign before ChatGPT reviews this preflight pack.
