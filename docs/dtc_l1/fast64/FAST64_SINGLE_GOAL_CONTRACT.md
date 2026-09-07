# DTC FAST64 Single Persistent Goal Contract

Status: **ACTIVE**

Terminal state:

`FAST64_COMPLETE_READY_FOR_REVIEW`

## Continuous state machine

`FAST64.0_PIVOT -> FAST64.1_PLATFORM_AND_PAYLOAD_LOCK ->
FAST64.2_REPAIR_QUALIFICATION -> FAST64.3_BASE_CHARACTERIZATION ->
FAST64.4_PRIMARY_MATRIX -> FAST64.5_CAUSAL_ANALYSIS ->
FAST64.6_SENSITIVITY -> FAST64.7_FINAL_SYNTHESIS ->
FAST64_COMPLETE_READY_FOR_REVIEW`

Each stage transition is automatic after HARD acceptance and compact
commit/push. The Goal must not stop at ordinary stage boundaries.

## Frozen top-level authority

- Framework branch: `hrl/decoupled-l1-fast64-v0`.
- Pivot parent: `a9cdb3328a346cbc9a76b7ffadae3725b4209ab5`.
- Core: `hrl/decoupled-l1-m5-v0@15cfa76ed3b041fa5b78161dfba02bae1e6d7fe9`.
- FAST12 membership: `FAST64_WORKLOAD_MANIFEST.tsv`.
- Platform/mechanism contract: `FAST64_PLATFORM_CONTRACT.md`.
- Stage work: `FAST64_EXPERIMENT_MATRIX.md`.
- Acceptance: `FAST64_ACCEPTANCE_CONTRACT.md`.
- Operational behavior: `FAST64_EXECUTION_RUNBOOK.md`.

## Goal behavior

Ordinary failures are work to solve, not reasons to stop.

For ordinary issues apply:

`OBSERVE -> REPRODUCE -> CLASSIFY -> INVESTIGATE -> REPAIR -> REGRESS ->
INVALIDATE AFFECTED DATA -> RESUME`.

The Goal should attempt source-correct fixes, alternative valid build/config
paths, parser repairs, workload-local reconstruction, safe scheduling changes,
and reproducible storage/trace handling before considering a human pause.

Pause only at the researcher-decision boundaries enumerated in
`FAST64_EXECUTION_RUNBOOK.md`, or after the terminal state is reached.

## Acquisition versus acceptance

Logical acceptance order must remain FAST64.0 through FAST64.7.
Physical acquisition inside an active stage should be parallel whenever rows
are independent and resource-safe.

Use measured dynamic `N_safe`; refill the pool as jobs finish.

## Checkpoint rule

Meaningful stage progress is committed/pushed. Ordinary polling is not.

Before every push:

- preserve untracked artifacts;
- `git diff --check`;
- explicitly stage intended paths only;
- never use `git add .` or `git add -A`.

## Scientific integrity rule

Do not tune membership, inputs, mechanism resources, or platform parameters to
target a desired speedup. Weak or negative results remain in the primary
aggregate when otherwise valid.
