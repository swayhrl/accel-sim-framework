# Codex Goal Prompt — Resume DTC Granularity/Fairness Campaign

Goal name:

`RESUME_DTC_GRANULARITY_FAIRNESS_AND_DOWNSTREAM_LOCALIZATION`

Repository:

`swayhrl/accel-sim-framework`

Master coordination branch:

`hrl/iscas2027-dtc-granularity-fairness-v0`

Expected remote master HEAD at prompt creation:

`df5338ae205d98b86fd721be7bd86dbf24ce6d83`

Before doing any work:

1. `git fetch origin`.
2. Verify actual heads of master, SG0, SG1, SG3, SG4A and SG5.
3. Do not reset or overwrite a branch that has advanced.
4. Use one isolated worktree per lane.
5. Read completely:

`docs/dtc_l1/iscas2027/handoffs/DTC_GRANULARITY_FAIRNESS_RESUME_HANDOFF_2026-09-22.md`

Treat that file as the authoritative resume context and scientific/operational boundary.

The previous Codex checkpoint ended with **zero live Wave-A simulators** and a disk hard-stop because `/workspace` had only ~7.64 GiB free. The user is manually cleaning disk. Do not launch simulations until a fresh resource snapshot satisfies the resume policy in the handoff.

First perform **R0 only**, with no new simulation:

- strict-validate the terminal SG1 B16-N/BICG canonical D2B smoke row;
- strict-validate the terminal SG5 GESUMMV/B16-S canonical C2 retry;
- strict-validate all eight SG4A exit-0 terminal rows;
- complete SG4A failure registry for both GESUMMV logical80 exit-1 rows;
- source-audit the SG4A logical80 = 160 sets x 4 ways / 640 physical-line boundary before any further logical80 launch;
- optionally strict-validate the twelve SG3 V1 OFF controls as historical controls only;
- commit/push lane-local R0 evidence without promoting terminal-only rows.

If R0 closes and the resource gate passes, continue solve-and-continue through all remaining stages in the handoff:

- SG1 canonical G6 and canonical FAST12;
- bounded same-Core B16-S/TC80-S G6 control for a clean S-vs-N granularity comparison;
- SG5 complete canonical 36-row G6 lower-traffic observer campaign;
- SG3 observer-ON G4 downstream localization: 1x baseline first, then capacity, MSHR, DTC cap, conditional queue and service sweeps;
- SG4A complete 32/64 logical-Tag study and handle logical80 only according to its source-qualified boundary;
- final review package and bounded paper-safe conclusions.

Ordinary engineering/controller/parser/validator problems should be investigated and repaired within lane boundaries, preserving failed evidence and using fresh UUIDs when a simulator rerun is actually required.

Stop for researcher review only if continuing would require:

- changing frozen FAST12 membership or trace identity;
- modifying accepted FAST64/Lane-E/TC80 scientific evidence;
- selecting workloads/parameters based on favorable performance;
- replacing the predeclared SG4A logical80 point with another capacity;
- changing DTC scientific semantics beyond already authorized observer/sensitivity work;
- introducing a new optimization mechanism rather than diagnostic localization;
- destructive cleanup of accepted evidence.

Do not manufacture PASS.

Final target:

`DTC_GRANULARITY_FAIRNESS_AND_DOWNSTREAM_LOCALIZATION_READY_FOR_REVIEW`

The final report must include branch SHAs, Core/runtime identities, run counts, all strict-validation results, SG1 canonical S/N comparisons, SG5 lower traffic, SG4A logical-Tag boundary/results, SG3 bottleneck decision matrix, all superseded/historical evidence, and explicit claim boundaries.
