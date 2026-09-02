# CODEX_NEXT_STAGE

## Status

**ACTIVE — CONTINUOUS GOAL AUTHORIZED FOR M1 THROUGH M4**

Execute M1 -> M2 -> M3 -> M4 on the dedicated goal branches. Human re-authorization is not required between passing major stages. Every HARD gate remains mandatory.

## Active branches

Core implementation:

- `swayhrl/gpgpu-sim:hrl/decoupled-l1-m1m4-v0`

Framework / experiments / evidence:

- `swayhrl/accel-sim-framework:hrl/decoupled-l1-exp-m1m4-v0`

Frozen M0 branches are read-only anchors:

- `swayhrl/gpgpu-sim:hrl/decoupled-l1-v0`
- `swayhrl/accel-sim-framework:hrl/decoupled-l1-exp-v0`

## Required reading before implementation

Framework:

1. `AGENTS.md`
2. `docs/dtc_l1/chatgpt_handoff/CURRENT_STATE.md`
3. `docs/dtc_l1/chatgpt_handoff/DISCUSSION_REFERENCE.md`
4. this file
5. `docs/dtc_l1/goal/M1_M4_GOAL_PLAN.md`
6. `docs/dtc_l1/goal/COUNTER_INVARIANT_SPEC.md`
7. `docs/dtc_l1/goal/VALIDATION_ACCEPTANCE_MATRIX.md`

Core:

8. `AGENTS.md`
9. `docs/dtc_l1/DTC_L1_SPEC.md`

## Goal objective

Deliver a validated, parameterized Accel-Sim/GPGPU-Sim implementation that:

1. preserves an exactly neutral LEGACY path;
2. implements the paper Baseline with explicit PIB and MSHR limits;
3. implements IO-DTC read semantics;
4. implements OO-DTC read semantics, Ref Count, Merge wakeup, and active reclamation;
5. implements and validates the modern sector readiness extension after whole-line OO passes;
6. attaches Store/Atomic/Fence and architectural bypass to the correct DTC lifecycle without changing their underlying memory semantics;
7. runs a representative available Chapter-4 compute workload set under Paper Base / IO / OO;
8. emits enough counters, invariants, parsers, and compact evidence to diagnose the mechanism and bottlenecks without rerunning solely to discover why a result moved.

## Stage progression

Run the following in order:

- `M1_FOUNDATION`
- `M2_IO_READ`
- `M3_OO_SECTOR`
- `M4_COMPUTE_BRINGUP`

At each major stage:

1. complete every required substage;
2. run every HARD acceptance item in `VALIDATION_ACCEPTANCE_MATRIX.md`;
3. close counter/accounting checks;
4. create `docs/dtc_l1/review_packs/<STAGE>/`;
5. update `docs/dtc_l1/codex_handoff/LATEST_REPORT.md`;
6. commit using explicit-path staging only;
7. push both affected branches;
8. continue automatically only if the stage is PASS.

If a HARD gate fails, STOP. If the current official source reveals an architecture-semantic ambiguity that cannot be resolved from source + frozen spec, classify it `UNKNOWN`, document it, and STOP rather than guessing.

## Required persistent Codex-owned implementation documents

Create/update under `docs/dtc_l1/implementation/` as execution proceeds:

- `SOURCE_INTEGRATION_MAP.md` in M1.0;
- `CONFIG_KNOB_MAP.md` by M1 closeout;
- `COUNTER_OUTPUT_MAP.md` by M1 closeout;
- `M4_MEMORY_OP_SEMANTICS.md` before M4 functional changes;
- `WORKLOAD_MANIFEST.md` before M4 workload runs.

## Explicitly forbidden during this goal

Do NOT:

- modify the M0 anchor branches;
- alter the frozen M0 architecture choices without a STOP/report;
- tune code/configs to target thesis speedup numbers;
- add all-or-nothing physical allocation or rollback;
- special-case small physical-cache deadlock;
- let DTC use the traditional L1 MSHR as its own capacity/merge mechanism;
- make OO retire more than the configured width;
- merge Atomic side effects as if they were read misses;
- redesign L2/NoC/DRAM;
- implement thesis DTC policy bypass;
- run or claim final paper-reproduction experiments;
- call M4 workload speedups FORMAL;
- modify ChatGPT-owned `chatgpt_handoff/` files.

## Required result labels

- Directed/unit and workload bring-up runs in M1-M4: `DIAGNOSTIC` unless explicitly used for exact neutrality.
- Clean-baseline neutrality evidence may be labeled `FORMAL_VALIDATION` inside the review pack, but not as a paper performance result.
- Pre-fix runs: `PRE_FIX`.
- Superseded runs: `OBSOLETE`.

## Final M4 closeout

The continuous goal is complete only when all M1-M4 HARD gates pass and Base/IO/OO complete the required available compute workload bring-up set with matching dynamic-operation counts and clean invariants.

Then:

- update `LATEST_REPORT.md` with `READY_FOR_M5_REVIEW`;
- push all source/evidence;
- STOP.

Do not begin M5.
