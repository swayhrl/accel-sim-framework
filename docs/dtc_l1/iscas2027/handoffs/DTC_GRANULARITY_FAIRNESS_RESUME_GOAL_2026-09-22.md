# Codex Goal Prompt — Resume DTC Granularity/Fairness Campaign

Goal name:

`RESUME_DTC_GRANULARITY_FAIRNESS_AND_DOWNSTREAM_LOCALIZATION`

Repository:

`swayhrl/accel-sim-framework`

Master coordination branch:

`hrl/iscas2027-dtc-granularity-fairness-v0`

Required master ancestry before execution:

- storage relocation: `1bae8f55b71ee71e2081dbab8baf1a1960b67e27`
- efficiency policy: `a1c8f0de69b0a920a33c805758cf79caaab2f664`
- updated resume handoff: `8e57f1a419a270e0265e08c28fcf3ba86ad1714b`

The actual remote HEAD may be newer. Verify and use it; do not reset it.

Before doing any work:

1. `git fetch origin`.
2. Verify actual heads of master, SG0, SG1, SG3, SG4A and SG5.
3. Do not reset or overwrite a branch that has advanced.
4. Use one isolated worktree per lane.
5. Read completely:

`docs/dtc_l1/iscas2027/handoffs/DTC_GRANULARITY_FAIRNESS_RESUME_HANDOFF_2026-09-22.md`

and:

`docs/dtc_l1/iscas2027/handoffs/DTC_EXPERIMENTAL_EFFICIENCY_POLICY_2026-09-22.md`

Treat both as authoritative. The first defines scientific/operational state; the second defines how to minimize elapsed time and unnecessary runs without weakening evidence.

The previous Codex checkpoint ended with **zero live Wave-A simulators**. Disk remediation is now complete: the user reports ~54.1 GB (~50.4 GiB) free on `/workspace`, and the common Git object store has been relocated to `/root/share/accel-sim-framework-object-store/objects` as recorded by commit `1bae8f55...`. Do not launch simulations until a fresh resource snapshot and Git-object-store accessibility check satisfy the resume policy.

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
- SG3 observer-ON G4 downstream localization using the **deduplicated staged V2 design** from the efficiency policy: one shared 1x/default baseline, decisive coarse capacity/MSHR/cap screen, then only predeclared conditional refinements;
- SG4A bounded G4 32/64 logical-Tag characterization first; handle logical80 only according to its source-qualified boundary; expand to FAST12 only if the efficiency-policy triggers require it;
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


## Execution-efficiency requirement

Do not treat the previously enumerated matrices as mandatory dense sweeps when the same scientific question can be answered with exact reuse, shared baselines, or a predeclared staged design.

Before each major launch batch:

1. produce a run-necessity/reuse table;
2. identify exact reusable rows and terminal rows needing validation;
3. estimate projected disk growth from comparable completed attempts;
4. launch the largest scientifically justified batch that fits the common resource ceiling;
5. use a rolling queue and validate as rows finish;
6. stop conditional refinement once the claim is resolved.

In particular:

- SG3 must not blindly launch the old 96-row plan; create the pre-result deduplicated V2 plan described in the efficiency policy and start with the 56-row decisive coarse screen;
- SG4A must not blindly launch 72 FAST12 missing points; close the fixed G4 characterization first and expand only under predeclared triggers;
- SG1 canonical FAST12 remains primary and should be completed efficiently with exact reuse;
- SG5 canonical G6 remains a compact diagnostic matrix and may run as one rolling campaign after its gate closes.

Elapsed time and compute/storage cost are first-class execution constraints, but never justify weaker validation or result-driven cherry-picking.
