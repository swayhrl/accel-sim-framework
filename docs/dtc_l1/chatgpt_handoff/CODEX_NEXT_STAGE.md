# CODEX_NEXT_STAGE

## Status

**ACTIVE — EXPLICIT GOAL MODE: COMPLETE M2 -> M3 -> M4**

M1 is closed PASS. M2 response/retirement recovery has already crossed the original conventional-fill blocker and is in validation/closeout. Run the remaining work as one persistent Codex Goal, not as a sequence of ordinary one-turn tasks.

Primary Goal contract:

`docs/dtc_l1/chatgpt_handoff/GOAL_START.md`

## Active branches

Core:

- `swayhrl/gpgpu-sim:hrl/decoupled-l1-m1m4-v0`

Framework:

- `swayhrl/accel-sim-framework:hrl/decoupled-l1-exp-m1m4-v0`

M0 branches remain read-only anchors.

## Current validated state

M1 `FOUNDATION` is PASS and must remain closed:

- Core M1 closeout anchor: `48b0be73833fc89fcf833349e82886ddc6d883b0`;
- M1 review pack: `docs/dtc_l1/review_packs/M1_FOUNDATION/`;
- B01-B09, B07 recovery, parser/accounting, CTests, and LEGACY exact differential validation passed.

M2 recovery has already established and smoke-tested a dedicated Paper-IO read request/response/PIB-writeback path. The latest mutable execution checkpoint is Codex-owned:

`docs/dtc_l1/codex_handoff/LATEST_REPORT.md`

Do not repeat already-passed recovery work solely because an older planning file describes the original failure.

## Required read order before launching/resuming Goal

Framework:

1. `AGENTS.md`
2. `docs/dtc_l1/chatgpt_handoff/CURRENT_STATE.md`
3. `docs/dtc_l1/codex_handoff/LATEST_REPORT.md`
4. this file
5. `docs/dtc_l1/chatgpt_handoff/GOAL_START.md`
6. `docs/dtc_l1/goal/M2_IO_RESPONSE_RECOVERY_SPEC.md`
7. `docs/dtc_l1/goal/M1_M4_GOAL_PLAN.md`
8. `docs/dtc_l1/goal/COUNTER_INVARIANT_SPEC.md`
9. `docs/dtc_l1/goal/VALIDATION_ACCEPTANCE_MATRIX.md`

Core:

10. `AGENTS.md`
11. `docs/dtc_l1/DTC_L1_SPEC.md`

If these conflict, STOP and report rather than guessing.

## Immediate execution objective

Finish M2 completely:

1. close remaining I06-I15 HARD validation;
2. perform the explicit high-MLP no-traditional-L1-MSHR proof;
3. close counters/parser/inflight/PIB/dependency/lower-credit invariants;
4. close release build/CTest/git hygiene;
5. create/push `review_packs/M2_IO_READ/` only on full PASS.

Then, without waiting for human confirmation:

- execute `M3_OO_SECTOR`, with PAPER_OO whole-line HARD closeout before sector extension;
- execute `M4_COMPUTE_BRINGUP`, beginning with the source-backed Store/Atomic/Fence/bypass semantics audit;
- stop at `READY_FOR_M5_REVIEW`.

## Explicit Goal behavior

Ordinary checkpoints are **not stop conditions**.

Codex may make semantic checkpoint commits, push safe evidence, and update `LATEST_REPORT.md`, but should continue automatically after:

- individual directed-test PASS;
- successful builds;
- M2 PASS;
- M3 PASS;
- successful diagnostic workload runs.

A major-stage PASS requires its review pack before progression, but does not require new human authorization.

Use the 20/40/60-minute no-progress policy for long commands. Do not terminate a job merely because it is long if measurable progress is present.

## HARD stop conditions

STOP only when:

- a HARD gate fails reproducibly;
- a correctness/architecture ambiguity cannot be source-resolved without guessing;
- a fix would require changing frozen M0 semantics;
- LEGACY/M1 closed behavior regresses;
- progress would require a forbidden shortcut such as hidden conventional L1D MSHR/fill dependence for PAPER_IO reads;
- unauthorized L2/NoC/DRAM redesign is required;
- M4 reaches `READY_FOR_M5_REVIEW`.

On HARD stop: preserve compact evidence, make only safe semantic commits, push, update Codex-owned `LATEST_REPORT.md`, and stop.

## Forbidden scope

Do NOT:

- modify M0 anchors;
- weaken/skip HARD gates;
- fabricate conventional L1D MSHR or `m_extra_mf_fields` state for Paper-IO reads;
- route IO-owned read responses through conventional `baseline_cache::fill()`;
- keep DTC and conventional L1D read backends active for the same Paper-IO request;
- create a second lane-level coalescing algorithm;
- tune implementation toward thesis speedup values;
- special-case expected deadlock/performance outcomes;
- redesign L2/NoC/DRAM;
- start sector extension before whole-line OO passes;
- begin M5.

## Final completion condition

The persistent Goal completes only when:

- M2 PASS review pack exists;
- M3 PASS review pack exists;
- M4 PASS review pack exists;
- required Base/IO/OO compute bring-up has matching dynamic operation counts and closed invariants;
- both active branches are pushed and clean;
- `LATEST_REPORT.md` is `READY_FOR_M5_REVIEW`;
- M5 has not started.
