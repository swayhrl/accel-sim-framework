# EP-L2 M3A — Target Goal

Status: **authorized in parallel with M0b final scan delta**.

## Goal

Reach:

```text
M3A_RO_CERTIFICATION_REVIEW_READY
```

with a source-proven decision about whether and where a traditional Line-MSHR can be replaced/released while preserving all required pending/requester/order state.

## Required end-state

M3A must leave the project with one of four explicit outcomes:

```text
FUNCTIONAL_M3A_CANDIDATE_A_READY_FOR_HANDOFF
FUNCTIONAL_M3B_CANDIDATE_B_READY_FOR_HANDOFF
NEEDS_NARROW_LIFETIME_MEASUREMENT_FIRST
NO_SAFE_M3_DIRECTION_CURRENTLY
```

and enough source/state/test/cost detail for ChatGPT to issue the next functional handoff immediately if one candidate is accepted.

## Priority

Prefer the simplest correct lifetime decoupling that removes a real structural ceiling. Do not maximize the amount of state/lifetime bypassed merely for a stronger story.

## Parallelism

M0b `scan` may finish independently. M3A source/design work must not wait for it. If scan later changes candidate prevalence but not source semantics, update quantitative motivation without restarting the certification audit.
