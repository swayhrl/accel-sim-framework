# DTC-L1 Current State

Last coordination update: 2026-09-03

Status: **M1 PASS; M2 RECOVERY IN PROGRESS; EXPLICIT GOAL MODE AUTHORIZED THROUGH M4**

## Source anchors

Frozen M0 framework anchor:

- official: `accel-sim/accel-sim-framework:dev`;
- official base SHA: `d930ad6d02c09bb56867132583735aba0389cff4`;
- M0 branch: `swayhrl/accel-sim-framework:hrl/decoupled-l1-exp-v0`.

Frozen M0 core anchor:

- official: `accel-sim/gpgpu-sim_distribution:dev`;
- official base SHA: `91880c53383d5a6a6742bfb1be2c5f34e39c7871`;
- M0 branch: `swayhrl/gpgpu-sim:hrl/decoupled-l1-v0`.

Active goal branches:

- Core: `swayhrl/gpgpu-sim:hrl/decoupled-l1-m1m4-v0`;
- Framework: `swayhrl/accel-sim-framework:hrl/decoupled-l1-exp-m1m4-v0`.

M0 branches are read-only design anchors.

## M1 closeout — PASS

M1 Foundation is independently reviewable at:

`docs/dtc_l1/review_packs/M1_FOUNDATION/README.md`

Validated Core M1 closeout anchor:

`48b0be73833fc89fcf833349e82886ddc6d883b0`

M1 established:

- exact-neutral `LEGACY` boundary against frozen upstream;
- explicit Paper-Base PIB/backpressure;
- paper Tag-bank arbitration;
- conventional Paper-Base MSHR capacity/merge behavior;
- lower outstanding-cap accounting;
- common counters/parser plumbing;
- B07 L1-hit completion PIB-retirement recovery;
- all B01-B09 and M1 accounting/hygiene HARD gates PASS.

M1 is closed and must not be weakened to solve later DTC issues.

## M2 recovery — current verified progress

The original Paper-IO integration failure was that an IO-owned lower read bypassed conventional L1D MSHR allocation but its return still entered conventional `baseline_cache::fill()`, which requires `m_extra_mf_fields`. That failure is preserved in:

`docs/dtc_l1/implementation/M2_IO_INTEGRATION_FAILURE.md`

The recovery has now crossed that blocker.

Current pushed Core recovery state includes at least checkpoint:

`f6ce41c610ab27e886f86c1cd98d52d4548c39c5`

Current detailed evidence:

`docs/dtc_l1/implementation/M2_IO_RESPONSE_RECOVERY_EVIDENCE.md`

Verified recovery behavior includes:

- DTC-owned whole-line lower request identity using root request UID plus source-backed sector-child/original mapping;
- response dispatch recognizes IO ownership before conventional L1D fill;
- no IO-owned read response is routed through conventional `baseline_cache::fill()` in the validated smoke;
- physical `{id,generation}` completion identity is checked;
- IO PIB retains completion payload and retires FIFO head through finite operand-collector/writeback availability;
- whole-line Paper IO completion cardinality uses unique coalesced 128B line references;
- allocation blocking is transient rather than a sticky historical retirement dependency;
- real `PAPER_IO` VecAdd self-check PASS;
- VecAdd IO request/response, PIB, dependency, inflight, and lower-credit state drain to zero;
- lower-outstanding cap=2 pressure run completes and observes cap blocking instead of creating untracked requests.

Latest mutable execution status is always Codex-owned:

`docs/dtc_l1/codex_handoff/LATEST_REPORT.md`

Do not redo already-passed recovery work solely because a planning document predates the latest checkpoint.

## M2 remaining HARD work

M2 is **not** yet accepted and no M2 review pack should exist until all HARD items pass.

Remaining priority is:

1. close directed state/resource cases I06-I15 that are not already formally evidenced;
2. formalize/reuse valid I14 cap=2 evidence rather than rerun it without purpose;
3. perform an explicit high-MLP no-traditional-L1-MSHR proof that exceeds Baseline PIB=8 / MSHR=32 concurrency and demonstrates Paper-IO reads do not depend on conventional L1D MSHR capacity/merge state;
4. close all IO request/response/PIB/dependency/physical/lower-credit counters and strict parser checks;
5. close release build/CTest/`git diff --check`/clean-worktree gates;
6. create/push `review_packs/M2_IO_READ/` only after complete M2 HARD PASS.

## M3 progression after M2 PASS

M3 is authorized automatically after full M2 PASS and review-pack creation.

Required order:

1. PAPER_OO whole-line random-access PIB and deterministic oldest-ready retirement;
2. line-level Ref Count and independent Shadow Ref checker;
3. pending-hit Merge/wakeup;
4. active reclamation using `tag_valid==0 && ref_count==0`;
5. O01-O13 and IO-vs-OO causal HOL test;
6. **only after all whole-line OO HARD gates pass**, implement/validate the 4x32B sector-readiness extension;
7. create/push M3 review pack and continue to M4 on PASS.

## M4 progression after M3 PASS

M4 is authorized automatically after full M3 PASS.

Before functional edits, perform the source-backed Store/Atomic/Fence/architectural-bypass semantics audit. Preserve existing underlying memory semantics and attach them to the DTC lifecycle. Atomic side effects must never be collapsed by read pending-hit merge logic.

M4 closes only after mixed-operation regressions and the required representative Base/IO/OO compute bring-up complete with matching dynamic operation counts, closed invariants, provenance, and a review pack.

## Explicit Goal-mode execution authority

Primary short Goal contract:

`docs/dtc_l1/chatgpt_handoff/GOAL_START.md`

Executable stage authority:

`docs/dtc_l1/chatgpt_handoff/CODEX_NEXT_STAGE.md`

Detailed specifications:

- `docs/dtc_l1/goal/M2_IO_RESPONSE_RECOVERY_SPEC.md`;
- `docs/dtc_l1/goal/M1_M4_GOAL_PLAN.md`;
- `docs/dtc_l1/goal/COUNTER_INVARIANT_SPEC.md`;
- `docs/dtc_l1/goal/VALIDATION_ACCEPTANCE_MATRIX.md`;
- Core `docs/dtc_l1/DTC_L1_SPEC.md`.

Codex should run this as one persistent Goal through M2 -> M3 -> M4. Ordinary checkpoint commits/test passes are not stop conditions. Major-stage PASS requires a review pack but does not require new human authorization.

Any reproducible HARD failure or source-semantic ambiguity requiring a guess still requires evidence + STOP.

Final authorized end state is `READY_FOR_M5_REVIEW`. M5 remains forbidden.
