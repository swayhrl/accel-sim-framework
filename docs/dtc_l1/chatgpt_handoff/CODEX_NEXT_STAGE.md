# CODEX_NEXT_STAGE

## Status

**ACTIVE — M2 IO RESPONSE/RETIREMENT RECOVERY AUTHORIZED**

M1 is closed PASS. The continuous goal correctly stopped on the first real `PAPER_IO` integration HARD failure. Resume only on the dedicated M1-M4 goal branches and recover M2 according to the specification below.

## Active branches

Core implementation:

- `swayhrl/gpgpu-sim:hrl/decoupled-l1-m1m4-v0`

Framework / experiments / evidence:

- `swayhrl/accel-sim-framework:hrl/decoupled-l1-exp-m1m4-v0`

Frozen M0 branches remain read-only anchors.

## Current validated state

M1 `FOUNDATION` is PASS and must remain closed:

- Core M1 closeout anchor: `48b0be73833fc89fcf833349e82886ddc6d883b0`;
- M1 review pack: `docs/dtc_l1/review_packs/M1_FOUNDATION/`;
- B07, B06, B08, strict parser/accounting, all M1 CTests, and LEGACY exact differential validation passed.

M2 committed directed-model/scaffolding work currently exists on the active Core branch. The first real PAPER_IO request/response experiment was discarded after the HARD failure, leaving the committed Core worktree clean at the reported stop SHA.

## Required reading before recovery

Framework:

1. `AGENTS.md`
2. `docs/dtc_l1/chatgpt_handoff/CURRENT_STATE.md`
3. `docs/dtc_l1/codex_handoff/LATEST_REPORT.md`
4. `docs/dtc_l1/implementation/M2_IO_INTEGRATION_FAILURE.md`
5. this file
6. `docs/dtc_l1/goal/M2_IO_RESPONSE_RECOVERY_SPEC.md`
7. `docs/dtc_l1/goal/M1_M4_GOAL_PLAN.md`
8. `docs/dtc_l1/goal/COUNTER_INVARIANT_SPEC.md`
9. `docs/dtc_l1/goal/VALIDATION_ACCEPTANCE_MATRIX.md`

Core:

10. `AGENTS.md`
11. `docs/dtc_l1/DTC_L1_SPEC.md`

## Immediate objective

Build a source-safe, fully DTC-owned Paper IO **read** request/response/retirement path.

The observed failure is not permission to reintroduce the conventional L1D MSHR. An IO-owned lower request must be recognized on return and completed directly against its immutable DTC physical allocation identity; it must never be sent to conventional `baseline_cache::fill()` merely to reuse `m_extra_mf_fields`/MSHR completion machinery.

Follow `M2_IO_RESPONSE_RECOVERY_SPEC.md` in order:

- `R2.0` prove request identity survives the lower-memory round trip;
- `R2.1` implement dedicated IO request ownership, bounded queue/issue, and response dispatch;
- `R2.2` implement dedicated IO PIB payload plus finite writeback/retirement;
- `R2.3` align completion/pending-write cardinality to unique 128B paper line references;
- `R2.4` remove/prove-safe the current sticky allocation-block state;
- `R2.5` prove Paper IO read-path isolation from conventional L1D MSHR/fill;
- `R2.6` rerun real VecAdd smoke;
- `R2.7` rerun every M2 HARD gate I01-I15 plus no-MSHR/accounting closeout.

## Progression authorization

If and only if all M2 HARD gates pass:

1. create/push `docs/dtc_l1/review_packs/M2_IO_READ/`;
2. update Codex-owned `docs/dtc_l1/codex_handoff/LATEST_REPORT.md`;
3. make semantic commits using explicit-path staging only;
4. push both affected branches;
5. continue automatically to the already-authorized:
   - `M3_OO_SECTOR`;
   - `M4_COMPUTE_BRINGUP`.

No new human authorization is required between M2 PASS and M4 as long as all HARD gates pass.

## Explicitly forbidden

Do NOT:

- modify M0 anchors;
- weaken or skip any M2 HARD gate;
- fabricate `m_extra_mf_fields` or a hidden traditional L1 MSHR entry for IO reads;
- route an IO-owned read response through conventional `baseline_cache::fill()`;
- use the conventional L1D MSHR as DTC merge/capacity state;
- silently keep both DTC and conventional L1D read accesses active for the same Paper IO request;
- create a second lane-level coalescing algorithm;
- let completion cardinality depend accidentally on 32B sector transactions in whole-line paper mode;
- make allocation-block state sticky after the blocking condition has cleared;
- bypass operand-collector/writeback resource availability at IO retirement;
- tune speedups;
- redesign L2/NoC/DRAM;
- begin M3 before M2 fully passes;
- begin M5.

## STOP condition

On any HARD failure or unresolved source-semantic ambiguity, push compact evidence, update `LATEST_REPORT.md`, and STOP.

If M4 eventually passes, update `LATEST_REPORT.md` to `READY_FOR_M5_REVIEW`, push, and STOP. Do not begin M5.