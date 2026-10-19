# DTC-L1 AG4 / Lane BA scientific intake and resource decision (2026-10-19)

Status: **READ-ONLY SCIENTIFIC REVIEW / NON-EXECUTABLE**.
This note does not modify AG4, Lane BA's active branch, any historical raw/UUID, source/Core, science configuration, executor permission, R2 thresholds, paper, or the 32-new-start cap. It neither dispatches nor autoruns anything.

## Frozen evidence reviewed

- AG4 terminal Framework `d8d0401dab0a1d9cb949302bcc05148328421cc2`: `docs/dtc_l1/review_packs/DTC_LANE_AG4_AUTHORITY_AE_AD_V1/{LATEST_REPORT.md,ROOT_CAUSE_AND_FIX_TERMINAL_SUPPLEMENT.md,FINAL_CPU_QUALIFICATION_DECISION.json,FULL_MATRIX.tsv}`.
- Lane BA published execution snapshot `7cdc27a7f4d7f13e11f942d6afdc5529121e6c3c`: `docs/dtc_l1/iscas2027/evidence_closure_20261019_v1/execution/{NEXT_RESUME.md,MATRIX_READINESS.md,SCIENTIFIC_SCOPE_CURRENT.md,CONTINUATION_GLOBAL_RESOURCE_CURRENT.json,BLOCKED_AUDIT_RESOURCE_THREE_TURNS.json,SELECTION.json,BUDGET_LEDGER.json}`.
- Timestamps/samples in these files are historical observations, not live measurements after any subsequent storage cleanup.

## 1. AG4 scientific decision

AG4 is terminal STOP, 2/5 actual starts, 0 accepted optimization performance results. The imported AG3 GEMM BASE is an original 1,071,405-cycle complete observation with 91 reuse checks. The AG4 Gaussian BASE produced 3,278,356 cycles, 510 kernels/513 commands, and matching frozen common metrics, but the *cohort executor qualification* is incomplete; retain as an identified complete calibration observation, not an AG4 optimization/convergence PASS. AE_GEMM was stopped and AE_Gaussian/AD_GEMM/AD_Gaussian not started. Do not make AE/AD negative or positive performance claims.

The found defect is the production wait-dispatch temporal ownership gap after PID retirement and reuse. Retired PIDs remained in `owned`/`states`, allowing a synthetic fresh-generation stop to reach `resume` without fresh parent event/PID-start_ticks proof. The actual frozen AST negative reproduces this unsafe dispatch. There is **no evidence of actual PID reuse during the real Gaussian or AE attempt** and no Core/microarchitecture, ELF or resource mismatch proven. AG4's own-signal fail-closed STOP and historical receipt preservation are correct. No AG4 reset, retry, patch-resume, or reuse of failed UUIDs.

## 2. BA is the single continuation; no parallel AG5 repair

BA has already prepared a targeted retired-PID dispatch fix, six actual-dispatch AST tests and two real CPU-root/thread/dash/cat lifecycle tests. These *bounded* tests do not replace the pending shared-global observer / exact external-role / three-role qualification. Continue from the current BA checkpoint and `NEXT_RESUME.md`, rather than requesting a new AG5 Goal or replaying unaffected CPU qualification.

BA's candidate remains `PROVISIONAL_O_WITH_INCOMPLETE_OPT_SCREEN` (K0/OO128/Tag64x8/AE0/AD0). This is not a finding that AE or AD has no effect. The BA budget must not be used to secretly complete AG4's unfinished optimization screen. Keep old C+ and O controls as imported source-bound evidence until exact current-family comparison eligibility is established.

## 3. Two independent resource gates: keep fail-closed and focus on useful work

Last BA published samples show output disk free about 5 GiB (<10 GiB full-simulation gate), host IO-full PSI avg10 around 26-29% (>25% CPU/complete-sim gate), but abundant host/cgroup memory. These are checkpoints, not current host state. User is arranging storage migration in a separate window and reclaiming capacity independently. Do not touch unowned project data, other raw, shared stores, or running processes. Do not relax R2 or rename/whitelist roles to evade authorization.

Once space is reclaimed:
1. Verify free bytes at the **actual simulation output filesystem**, not an unrelated mount. Minimum is 10 GiB; retaining practical output headroom above that threshold is preferable for repeated map/trace artifacts.
2. Allow cleanup/migration IO pressure to settle. Require fresh >=10-second paired resource admissions covering **both host and cgroup** memory/IO PSI plus no new OOM; a single low sample or cgroup-only pass is insufficient.
3. Under the *same BA coordinator and sole dispatch authority*, resume only the previously registered CPU build and shared observer/external-role qualification in `NEXT_RESUME.md`. No unregistered CPU process or background restart.
4. After the shared qualification, freeze each exact simulation family (runtime/ELF, whole input, scope, comparator, UUIDs, budget, strict/timeout, source options) and perform a new full R2 admission before its first actual start.
5. If pressure remains over the accepted threshold or space is again below the minimum, remain resource-blocked; independently completed input inventories and source preparations may be reported as such. Do not fabricate a RUNNING/PASS state.

Both BA's existing `P<=16,N<=6,R<=6,reserve<=4,total<=32` caps and AG4's terminal no-retry boundary remain unchanged. Empty slots are not a run target; no mass replay of old controls.

## 4. Scientific emphasis after unblocking

Priority: fixed-O/C+ primary eight-input coverage and adverse cases; one selective collection-service 4->1 sensitivity pair; existing source-backed correctness limits and input variants only after their capture/ABI/source qualification. SEM1 conditional injected-byte routing does not prove application architectural values or general coherence. DC remains user-owned. Preserve BICG regressions and the alternative conventional expansion advantage; no favorable-subset GM, no paper result until complete bounded evidence. v0.18 is a pending-result manuscript, not an excuse to fill cells from prefixes.

## Decision boundary

No change to the active BA Goal is requested. The next useful communication is a **fresh verified disk + paired host/cgroup IO admission receipt** after cleanup, followed by resumption in the existing BA window. If the site cannot pass the actual R2 thresholds, report `RESOURCE_BLOCKED` rather than starting tests or demanding another generic audit round.
