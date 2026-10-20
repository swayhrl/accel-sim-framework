# DTC-L1 / ISCAS 2027 — Lane RD: AG6 I/O Resource Diagnosis V1

Status: USER_AUTHORIZED_DIAGNOSIS_ONLY; NON-EXECUTABLE RESOURCE-POLICY REVIEW.
Date: 2026-10-20. Owner: independent Codex session on the **original huangrulin-174 account/container** (not 174-new, 109, or another execution node).
Goal publisher branch: `hrl/iscas2027-dtc-ag6-io-diagnosis-174-v1`.
Frozen source anchor: `d9c192544622579a93d3efad98f56f82536c2fbe` in `swayhrl/accel-sim-framework`. This Goal is a newly published independent document, **not** a revision of BA/AG contracts.

## 0. Requested outcome and hard boundaries

Determine, from existing **closed** data and bounded read-only diagnostics, what made the first AG6 `AE_GEMM` full simulation trip the cgroup I/O full PSI runtime rule. Separate what is observed from hypotheses. Draft evidence-based protection alternatives for a separately authorized future cohort. Publish immutable, reviewable evidence and stop. Do **not** run/retry any simulator, canary, trace capture, benchmark, old Goal, or workload.

Current anchored science:
- AG6 original four-start authorization remains consumed 1/4: `AE_GEMM` UUID `77cbc367-150c-418d-85e0-3be23d952498` was actually launched and stopped by resource policy after ~277.34 seconds; **0 accepted performance results**, cycles unavailable, other 3 UUIDs sealed. Never refund, reuse or resume those identities.
- BA has used 0/32 fullsim starts. BA `/root` remains sole authorized fullsim dispatcher; this RD window is **not** a dispatcher and receives no budget.
- `SELECTION_V2` is `PROVISIONAL_O_WITH_INCOMPLETE_OPT_SCREEN`; final F is null. No AE/AD promotion and no performance estimates from partial outputs. Old selection and original 44/GM12/T/U/independent inputs remain untouched.
- User-approved actual output-disk floor is **strictly >5GiB**, with expected-write headroom. This was not the cause of this stop. No implied change to other resource gates or historical refusals.
- Historical runtime I/O stop: three qualified samples more than 30 s apart, cgroup full avg10 **26.50%, 60.09%, 56.22%**, simultaneous host full avg10 **3.87%, 6.27%, 6.23%**. Primary cause category recorded `cgroup:IO_FULL_PSI_GT25_THREE_GE30S_SAMPLES_AG_EXPLICIT_EXTENSION`. A later `PROVEN_INSTANCE_EXIT_RETIREMENT_JOIN` / `KeyError:'point'` on stopped or incomplete receipts is **not** a second completed performance measurement.

HARD NO:
1. No reset/restart/continue of terminated AG6, AG3/AG4/AG5, BA Goal, or other Goals. No touching live/active raw, outside-project payloads, source Core or model binaries. Do not change `io.max`/`io.weight`, kernel controls, sysctl, mounts, cgroups, host policy, or filesystem quotas.
2. No new GPU/CPU simulator or test program, compiler, trace processing workload, calibration, `fio`/`dd`/`stress`/`ioping`, benchmark, process signals, ptrace/strace attachment, process-group adoption, polling daemon, or background loop. Only targeted existing-file reads and cheap, read-only local OS metadata probes as specified. No privilege escalation.
3. Do not spend AG6/BA budgets; do not create a new executable preregistration, UUID, RUN_START, lease/dispatcher, or modified runtime guard. Do not bypass or relax the 25% host/cgroup I/O threshold in code.
4. Keep original BA worktree/branch and immutable records strictly read-only. Use a **separate worktree/branch/output root**. Do not force checkout, reset, move or overwrite existing refs. No movement to 174-new/109.
5. No continuous watching of processes or raw logs; no repeated full scans of large trace payloads. Do not read or rehash multigiagbyte original trace bodies. Respect current disk and source provenance. No data deletion or cleanup.

## 1. Exact starting evidence

Read the pinned published reports and immutable indexes first (not historical text at the bottom of CURRENT_STATE as a current verdict).

- `docs/dtc_l1/iscas2027/evidence_closure_20261019_v1/CURRENT_STATE.md` (top/current snapshot at `d9c19254`).
- `.../execution/ag6_actual_cohort_stop_v2/STOP_SUMMARY.json`.
- `.../execution/ag6_actual_cohort_stop_v2/AE_GEMM/{RUN_START.json,RUN_TERMINAL.json,WRAPPER_EXCEPTION.json,STRICT.json,RESOURCE_FINAL.json,FINAL_PRE_FORK.json}`.
- `.../execution/ag6_actual_cohort_stop_v2/AE_GEMM/RESOURCE_MONITOR.jsonl` (published file/index and/or immutable closed local copy; bounded streaming pass if needed).
- `.../execution/AG6_BUDGET_LEDGER.json`, `.../execution/SELECTION_V2.json`, `.../execution/CURRENT_ROLE_STATUS_AFTER_DISK_AUTHORIZATION_20261020.json`, `.../execution/AG6_SINGLE_WORKER_RELEASE_REVIEW_V2.json`.
- Only if necessary, the **closed, AG6-owned** `ENGINE/stdout` and maps/event receipts identified by STOP_SUMMARY, with exact size/SHA from the published manifest. Avoid raw trace contents; preserve old raw and locks untouched.
- Existing CPU fixture resource receipts for SEM1/ROB1 may provide context, but they are **different workloads**; never call them a controlled simulator A/B comparison.
- Follow the actual canonical monitor/guard implementation used by the launched AG6 executable; audit the pinned source and SHA through RUN_START/registration. Do not presume the current tip or similarly named old source is the executed version.

If a source is missing, unreadable, untrusted or active, record `UNAVAILABLE` with the exact reason; do not reconstruct an event from an expected source path or rerun the workload.

## 2. Work plan (solve ordinary analysis problems and continue)

### D0: Isolation, authority and publication baseline
Use original174 only. Establish an independent worktree without disturbing BA, based on the Goal branch from pinned `d9c19254`. Verify GitHub exact Goal SHA/branch ancestor and output path. Suggested result root `docs/dtc_l1/review_packs/DTC_AG6_IO_DIAG_20261020_V1/` on this independent branch. Read-only existing file analyses need no new run authority. Do not touch active processes. Check whether other DTC jobs/leases exist only via already published state and ordinary minimally scoped read-only authority metadata; never signal them.

### D1: Reconstruct the closed stop time series
Using the exact stored source and complete closed monitor receipts, independently join timestamps (UTC and monotonic), host/cgroup `io.full.avg10`, sample spacing/threshold windows, memory PSI, OOM and swap deltas, remaining disk and per-process/project scope when present. Recompute the qualification of 3 samples >=30 seconds apart and identify earlier warnings/recovery windows. Distinguish `RUN_START`, simulator fork, policy trip, controlled kill/exit and post-stop wrapper/strict parsing. Confirm what was **not** observed, especially natural exit0 and final cycles. State whether completed progress counters are recorded; partial stdout must never be used as an accepted speedup.

Extract the needed JSONL fields in one bounded streaming pass, with output tables capped to informative rows. No wholesale copy of maps/raw/trace into Git.

### D2: Investigate sources of I/O waiting without an active experiment
Trace what the recorded host and cgroup PSI actually measure and their hierarchy/sampling path. PSI `full.avg10` is *time spent with all non-idle tasks in that scope stalled*, **not** disk utilization and **not** proof of cgroup throttling. Identify the cgroup path, sampled devices, controller settings and counter keys **only when supported by the historical receipts**. Examine which `io.stat`/`io.max`/`io.weight`, read/write bytes/IOPS, `/proc/PID/io`/fault counters, filesystem mount/device and output growth data were saved. The stopped PIDs are gone; do not reconstruct their historical /proc state using new PIDs.

If useful and cheap, collect a **single contemporaneous, read-only metadata snapshot** of the original174 host/cgroup's accessible `/proc/pressure/io`, `/sys/fs/cgroup/.../io.pressure`, `io.max`, `io.weight`, `io.stat`, `mountinfo`, mount free/inodes and IO control identity. Mark it `CURRENT_ONLY_NOT_HISTORICAL`, and do not claim it proves what was configured at AG6 runtime unless history establishes persistence. Do not query arbitrary foreign process command lines or scan unrelated projects.

Evaluate candidate mechanisms separately: simulator trace read/page faults, shared-storage latency, output/event logging small writes/fsync, cgroup device controls, writeback, and artifact filesystem effects. For each: direct evidence, plausible causal path, counter-evidence, missing distinguishing metric. Small stdout/MAP_EVENTS size alone cannot rule in or rule out pathological I/O latency. Compare coarse old CPU fixture conditions **only as contextual controls**, not mechanistic proof.

### D3: Conservative root-cause and policy sensitivity analysis
Produce one root-cause matrix with explicit confidence (`OBSERVED`, `SUPPORTED_HYPOTHESIS`, `UNRESOLVED`, `DISFAVORED`). Answer if the old stop was a correctly applied *frozen* rule (yes, if recomputation matches) separately from whether that rule was an appropriate protection signal for this GPU simulation (requires evidence). Evaluate effects of the metric `cgroup full avg10`, sampling cadence and consecutive-window logic, without inventing missing throughput/progress telemetry.

Form 2–3 **draft-only, non-executable** protection options:
- A: unchanged runtime stop rule;
- B: preserve strict prelaunch full paired host+cgroup R2 and 5GiB disk/memory/OOM/identity protections, while distinguishing runtime warning, sustained no-progress and actual safety conditions; define precisely what *measurable* progress evidence would be needed, with `UNAVAILABLE` where absent;
- C: another measured, bounded runtime threshold/hysteresis alternative if justified by the closed data.
For each give benefit, failure mode, minimum extra telemetry, consequences for fairness and full-run acceptance, and the exact changes that require user approval. **Do not** silently authorize changes, choose an invented numeric threshold, imply host PSI is interchangeable with cgroup PSI, or convert runtime resource STOP to scientific PASS.

If existing evidence cannot distinguish I/O throttling from naturally high I/O wait, say `ROOT_CAUSE_UNRESOLVED`; propose the *minimum future instrumentation* as a draft requiring separate new-experiment authorization, not as a probe to execute now.

### D4: Publish and stop
Publish a small evidence pack:
1. `LATEST_REPORT.md` (short conclusion, blockers and user decision requested);
2. `STOP_RECONSTRUCTION.tsv` (timestamp/scopes/PSI/other recorded metrics and provenance fields);
3. `IO_SOURCE_PROVENANCE.md` (exact executed monitor/guard sources, snapshots and limits);
4. `ROOT_CAUSE_MATRIX.md` (observations vs hypotheses);
5. `RESOURCE_POLICY_OPTIONS.md` (A/B/C proposals; change-control boundary);
6. `BUDGET_AND_SCIENCE_BOUNDARY.json` (AG6=1/4, 0 valid, three sealed, BA=0/32, O provisional, no permission);
7. `FILES_SHA256.tsv` and `PUBLICATION_READBACK.json` where feasible, excluding any self-referential hashes. Publish only small reports/proofs, not raw traces, ELF, large JSONL, maps or other payloads.

Commit/push to this new diagnostic branch, fetch exact HEAD/tree/relevant blob SHA back independently and verify clean. Do not alter BA/GitHub default or old selection. At completion report: final branch, exact commit, artifact paths, root cause with uncertainty, recommended next **authorization decision**, and confirmation of zero simulation/test/fixture starts, zero old/raw changes, zero process signals.

## 3. Fail/continue policy

Continue through minor report/parser/format engineering issues in this *isolated analysis* only, without changing the contracts or executing tests. STOP and report without launching anything if original174 identity/authority cannot be established, primary immutable receipts do not join, or a proposed step would require live raw, privileged controls, a new benchmark, Core/guard changes or a new simulator start. Missing historical counters are a scoped result, not permission to generate them retroactively. A new independent AG6 cohort, threshold relaxation and BA fullsim execution all require a **separate explicit user authorization** after this diagnosis.

No background/polling work. This Goal terminates after immutable publication.