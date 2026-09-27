# Future B16 Result Interpretation Template

Status: `TEMPLATE_ONLY_NO_TIMING_RESULT`.

Do not select a branch until the future timing run and this characterization
both have exact provenance/SHA closure. Multiple branches may apply to
different layers or scopes; report that explicitly instead of forcing one
global label.

## Evidence binding

- Timing run ID/receipt: `PENDING`
- Framework/Core/config/trace/sidecar SHA closure: `PENDING`
- Target protection/admission counters: `PENDING`
- Trace-pressure characterization outputs/SHA: `PENDING`
- Scope of “local” and “whole decode”: `PENDING`

## Branch 1 — timing local positive + pressure low

Compatible interpretation: useful target retention under modest conflicting
reference pressure. Check realized protection, denial/quota saturation,
whole-decode coverage, and D1→D2 versus D2→D3 consistency.

Do not claim that low proxy pressure proves no actual L2 conflict or eviction.

## Branch 2 — timing local positive + collateral high

Compatible interpretation: a real target-local benefit may be offset by
collateral cache/admission cost or limited protected coverage. Separate local
and whole-decode timing; inspect non-target timing, denial, hot sets,
per-subpartition pressure, and global-capacity-versus-local-placement evidence.

Do not turn a local positive result into an application-wide benefit claim.

## Branch 3 — target protection low + denial high

Compatible interpretation: the budget/admission path may not realize intended
protection, so timing is not a clean test of retained-target usefulness. Check
quota accounting, per-subpartition distribution, set-local population,
eligibility, and fill realization.

Do not interpret weak timing as evidence that the underlying reuse has no
value.

## Branch 4 — target protection high + timing no benefit

Compatible interpretation: retention may be realized but not timing-critical,
may occur too far before reuse, may be hidden by another bottleneck, or may be
offset by collateral effects. Check reuse distance, actual next-reuse target
footprint, future hit/service evidence, critical-path coverage, and non-target
timing.

Do not claim that the mapper or pressure proxy is invalid solely because high
protection produces no speedup.

## Result section — leave empty until future timing closure

- Selected branch(es): `UNSELECTED`
- Timing evidence: `PENDING`
- Pressure evidence: `PENDING`
- Mechanism-counter evidence: `PENDING`
- Interpretation: `PENDING`
- Unresolved alternatives: `PENDING`
