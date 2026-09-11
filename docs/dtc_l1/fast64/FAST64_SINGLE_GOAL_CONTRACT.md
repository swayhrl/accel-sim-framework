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
- `MECHANISM_BEHAVIOR_ANCHOR`:
  `hrl/decoupled-l1-m5-v0@15cfa76ed3b041fa5b78161dfba02bae1e6d7fe9`.
- `FAST64_HISTORICAL_TELEMETRY_CORE`:
  `hrl/decoupled-l1-m5-v0@bbcbb5e7565417102087bc80b14c349b4e568c05`, whose
  existing rows remain immutable historical evidence.
- `FAST64_FORMAL_REPAIRED_CORE`:
  `hrl/decoupled-l1-m5-v0@95ccdb7a056f2d53f740d90869785cac6d4ee0f5`, runtime
  `462d105cf28efe98a8a20131fd671f3d28ad374a3e4b5448a597df702cc4dbc9`.
  It guards only zero-effective-access IO/OO loads before DTC reference
  admission, preserves the nonempty assertion, and has a strict common
  Hotspot1 Base/IO/OO triplet plus exact Base differential.  Every new formal
  FAST64 row uses this identity, except the narrow 2DConvolution tag-identity
  repair mapping in `handoffs/FAST64_2D_TAG_IDENTITY_CORE_AUTHORITY_MAP.md`.
  Historical bbcbb reuse is governed solely by
  `handoffs/FAST64_ZERO_ACCESS_CORE_REPAIR_IDENTITY_MAP.md`; never silently
  mix or relabel identities.
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

## Logical-stage acceptance versus physical precomputed acquisition

`LOGICAL_STAGE_ACCEPTANCE` remains strictly ordered from FAST64.0 through
FAST64.7.  A PASS state, result promotion, causal conclusion, or stage advance
occurs only after that stage's HARD gates pass.

`PHYSICAL_PRECOMPUTED_ACQUISITION` is permitted before a later logical stage
opens only when the exact frozen Core, payload, platform, observer, config and
isolated namespace are recorded.  It never relaxes a HARD gate and must retain
one of these explicit pending classifications until the applicable gate passes:

- `PRECOMPUTED_FAST64_2_COUPLED_STRESS_PENDING_FAST64_1_ACCEPTANCE` for the
  source-reachable coupled lower-cap/create-queue positive stress; the
  preserved high-cap row is `FAST64_2_HIGH_CAP_NEGATIVE_CONTROL` only;
- `PRECOMPUTED_PENDING_FAST64_1_2_ACCEPTANCE` for FAST12 Base@8192 rows;
- `PRECOMPUTED_PENDING_FAST64_3_ACCEPTANCE` for main-matrix IO/OO rows acquired
  only after FAST64.2 repair PASS;
- `PRECOMPUTED_PENDING_FAST64_4_5_ACCEPTANCE` for frozen one-dimensional
  sensitivity points acquired after FAST64.2 PASS.

The entire historical FAST64.1 r1 wave is
`SUPERSEDED_NONFORMAL_EXECUTION_PATH_AT_RISK`.  It may remain as diagnostic or
supporting evidence only; no r1 row may close FAST64.1 or be reused as the
FAST64.2 normal triplet.  Those formal gates require the complete immutable
seven-row r2 qualification set.

Use measured dynamic `N_safe`, prefer one worker per physical core before SMT,
and refill only after a fresh CPU, memory, swap, I/O, and output-space audit.

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
