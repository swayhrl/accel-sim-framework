# CODEX_NEXT_STAGE

## Status

**ACTIVE — B07 RECOVERY AUTHORIZED; RESUME M1 -> M4 ONLY AFTER M1 HARD PASS**

The previous continuous goal correctly stopped at M1 HARD gate B07. Resume work only on the dedicated goal branches and execute the recovery specification below.

## Active branches

Core implementation:

- `swayhrl/gpgpu-sim:hrl/decoupled-l1-m1m4-v0`

Framework / experiments / evidence:

- `swayhrl/accel-sim-framework:hrl/decoupled-l1-exp-m1m4-v0`

Frozen M0 branches remain read-only anchors:

- `swayhrl/gpgpu-sim:hrl/decoupled-l1-v0`
- `swayhrl/accel-sim-framework:hrl/decoupled-l1-exp-v0`

## Required reading before recovery

Framework:

1. `AGENTS.md`
2. `docs/dtc_l1/chatgpt_handoff/CURRENT_STATE.md`
3. `docs/dtc_l1/codex_handoff/LATEST_REPORT.md`
4. this file
5. `docs/dtc_l1/goal/B07_RECOVERY_SPEC.md`
6. `docs/dtc_l1/goal/M1_M4_GOAL_PLAN.md`
7. `docs/dtc_l1/goal/COUNTER_INVARIANT_SPEC.md`
8. `docs/dtc_l1/goal/VALIDATION_ACCEPTANCE_MATRIX.md`

Core:

9. `AGENTS.md`
10. `docs/dtc_l1/DTC_L1_SPEC.md`

## Immediate objective

Resolve the M1 B07 traditional-MSHR merge-full deadlock without changing the frozen architecture or conventional cache/MSHR semantics.

ChatGPT source review found a concrete high-priority defect to verify first: the current `ldst_unit::L1_latency_queue_cycle()` L1-hit completion path calls `warp_inst_complete(...)` but does not pair that true completion event with `dtc_l1_retire(...)`. Other tracked memory completion paths already pair the two. This can leak Paper-Base PIB entries after the first same-line miss fills and younger requests become hits.

Follow `docs/dtc_l1/goal/B07_RECOVERY_SPEC.md` exactly. Do not apply a broad workaround before bounded pre-fix localization confirms or disproves this cause.

## Recovery progression

Execute in order:

- `R07.1` reproduce/localize the pre-fix failure with bounded diagnostics;
- `R07.2` minimal completion-lifecycle fix if confirmed;
- `R07.3` permanent hit-completion PIB-leak regression/invariant;
- `R07.4` re-run B07 with reproducible source-supported MSHR entry/max-merge configuration;
- `R07.5` frozen clean-upstream differential check;
- `R07.6` full M1 HARD revalidation.

If any recovery HARD item fails or the proposed cause is disproved without another source-backed root cause, STOP and report.

## Resume authorization after recovery

If and only if **all** M1 HARD gates pass after R07.6:

1. create and push `docs/dtc_l1/review_packs/M1_FOUNDATION/`;
2. update `docs/dtc_l1/codex_handoff/LATEST_REPORT.md` with M1 PASS evidence;
3. make semantic commits with explicit-path staging only;
4. push both affected branches;
5. resume the existing continuous goal automatically:
   - `M2_IO_READ`
   - `M3_OO_SECTOR`
   - `M4_COMPUTE_BRINGUP`

No new human re-authorization is required between M1 PASS and M4 as long as every subsequent HARD gate passes.

## Explicitly forbidden

Do NOT:

- modify M0 anchor branches;
- weaken/skip B07 to continue;
- special-case this workload or deadlock;
- add a PIB timeout/forced release;
- release a PIB entry before the simulator's true memory-instruction completion point;
- change conventional MSHR merge semantics merely to make B07 finish;
- tune target speedups;
- alter L2/NoC/DRAM;
- begin M2 before full M1 revalidation passes;
- modify ChatGPT-owned handoff/spec files;
- begin M5.

## Result/evidence requirements

The B07 recovery evidence must record pre-fix and post-fix source SHAs, effective MSHR entry/max-merge settings, workload identity, compact pre-fix localization, clean-upstream differential behavior, PIB admits/retires/drain state, merge-full count, and application completion/self-check.

Pre-fix evidence: `PRE_FIX`.
Recovery/directed tests: `DIAGNOSTIC`.
LEGACY neutrality: `FORMAL_VALIDATION` only as implementation validation, never as paper performance evidence.

## Final STOP condition

If M4 eventually passes, update `LATEST_REPORT.md` with `READY_FOR_M5_REVIEW`, push all source/evidence, and STOP. Do not begin M5.