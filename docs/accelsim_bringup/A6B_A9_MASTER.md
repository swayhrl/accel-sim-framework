# Accel-Sim A6B-A9 master guidance

## Overall goal

Complete one large Accel-Sim infrastructure round from A6B to A9.

This round should turn the current bringup state into a more reliable baseline pipeline:

- A6B: audit and fix version string dirty-marker classification.
- A7A: harden clean baseline rerun flow.
- A7B: add a controlled N-app smoke runner.
- A8: generate a small benchmark baseline.
- A9: align the Accel-Sim workflow with previous Mascar and MeDiC GPGPU-Sim reproduction workflow style.

This is still infrastructure work. Do not implement new Accel-Sim architectural behavior in this round.

## Current state before this round

A0-A5 completed:

- A0 PASS: environment wrapper and local ignored directories.
- A1 PASS: make build succeeded, accel-sim.out executable, ldd no missing libraries.
- A2 PASS: small pre-trace SASS smoke using tesla-v100 rodinia_2.0-ft trace.
- A3 BLOCKED_NO_GPU: no nvidia-smi and no /dev/nvidia*, tracer not validated.
- A4 PASS: dry-run and real direct smoke suite completed.
- A5 PASS: final summary and review pack generated.

A6 completed from a clean tree, but the script marked the result as FAILED_DIRTY_BUILD_STRING.

A6 important observation:

    accelsim-commit-2586635_modified_0.0_26-06-07-00-06-49
    gpgpu-sim_git-commit-6c3cf4ff_modified_0.0

The tree was clean at start and end. Rebuild passed. A2 and A4 smoke passed. The actual issue is that the version string format always includes a _modified token and uses the following numeric value as a diff-count-like field. The value 0.0 should be treated as clean.

## Required phase order

Execute phases strictly in this order:

    A6B -> A7A -> A7B -> A8 -> A9

If a phase is blocked, write a clear report and continue when possible.

A6B and A7A must be resolved before treating any later stats as baseline-quality.

## Critical clean-tree sequencing rule

For any phase that rebuilds the simulator or validates clean baseline build strings:

1. Make tracked script/doc changes first.
2. Commit those tracked changes with explicit git add paths.
3. Confirm:

       git status --short

   is empty.
4. Run the build or baseline command.
5. After the run starts, do not edit tracked files.
6. If a tracked-file fix is required, fix it, commit it, confirm clean tree, and rerun the affected phase from the beginning.

This rule prevents build strings from being produced from a dirty tree.

## Hard rules

1. Do not push.
2. Do not use git add . or git add -A.
3. Do not commit generated logs, traces, downloaded apps, build directories, hw_run, or review packs.
4. Runtime outputs must go only under ignored local paths:
   - .local_reports/
   - .local_logs/
   - .local_runs/
   - .local_traces/
   - hw_run/
   - review_packs/
5. Add ignored local paths to .git/info/exclude only. Do not change .gitignore unless explicitly needed and justified.
6. Do not run a large benchmark campaign.
7. Do not try to bring up NVBit tracer in this round. A3 remains blocked until a GPU is visible.
8. Do not modify Accel-Sim or GPGPU-Sim simulator behavior in this round unless a tiny script/config fix is required for the infrastructure.
9. Every phase must write:
   - start time
   - end time
   - wall clock seconds
   - commands run
   - status
   - important paths
   - blockers or limitations
10. Generated local reports should be markdown under .local_reports.
11. Long command output should go to .local_logs, not to chat.
12. Review packs must not include traces, build directories, gpu-app-collection, or huge logs.

## Expected tracked scripts

Codex should create or update these tracked scripts:

    scripts/accelsim/a6b_version_string_audit.sh
    scripts/accelsim/a7a_clean_baseline_hardened.sh
    scripts/accelsim/a7b_n_app_smoke.sh
    scripts/accelsim/a8_small_benchmark_baseline.sh
    scripts/accelsim/a9_mascar_medic_alignment.sh

Existing scripts may also be updated if needed:

    scripts/accelsim/a6_clean_baseline_rerun.sh
    scripts/accelsim/a2_pretrace_smoke.sh
    scripts/accelsim/a4_run_smoke_suite.sh
    scripts/accelsim/accelsim_env.sh
    scripts/accelsim/README.md

## Expected tracked docs

Codex should create or update:

    docs/accelsim_bringup/VERSION_STRING_AUDIT.md
    docs/accelsim_bringup/CLEAN_BASELINE_PIPELINE.md
    docs/accelsim_bringup/N_APP_SMOKE_RUNNER.md
    docs/accelsim_bringup/SMALL_BENCHMARK_BASELINE.md
    docs/accelsim_bringup/MASCAR_MEDIC_ALIGNMENT.md
    docs/accelsim_bringup/RUNBOOK.md
    docs/accelsim_bringup/KNOWN_ISSUES.md

Runtime results should be written to .local_reports, not hardcoded into tracked docs after clean rerun unless Codex commits and reruns from a clean tree.

## Expected local reports

Expected local report examples:

    .local_reports/A6B_version_string_audit_TIMESTAMP.md
    .local_reports/A7A_clean_baseline_hardened_TIMESTAMP.md
    .local_reports/A7B_n_app_smoke_TIMESTAMP.md
    .local_reports/A8_small_benchmark_baseline_TIMESTAMP.md
    .local_reports/A9_mascar_medic_alignment_TIMESTAMP.md
    .local_reports/A6B_A9_final_summary_TIMESTAMP.md

Expected review packs:

    review_packs/A6B_A9_ACCELSIM_PIPELINE_review_pack_TIMESTAMP.tar.gz

## Suggested commit structure

Preferred implementation commit sequence:

1. Implement all A6B-A9 tracked scripts and docs.
2. Commit with explicit paths:

       git commit -m "scripts: harden accel-sim baseline pipeline"

3. Confirm clean tree.
4. Run A6B-A9 local execution scripts.
5. If no tracked fixes are needed, do not make another commit.
6. If tracked fixes are needed, commit them explicitly and rerun affected phases from clean tree.

## Final pass criteria

A6B pass:
- version_detection.mk files audited.
- _modified_0.0 or _modified_0 is classified as clean.
- _modified_nonzero or dirty is classified as dirty.
- VERSION_STRING_AUDIT.md exists.
- a6_clean_baseline_rerun.sh no longer false-fails on _modified_0.0.

A7A pass:
- clean baseline hardened script runs from clean tree.
- rebuild succeeds or verified existing binary is clearly justified.
- A2 and A4 smoke rerun successfully.
- build string audit status is PASS_CLEAN_DIFF_ZERO or equivalent.

A7B pass:
- controlled N-app direct smoke runner exists.
- dry-run works.
- real run attempts a small bounded number of apps when traces exist.
- per-app CSV is produced.

A8 pass:
- small benchmark baseline script exists.
- bounded small suite runs or clearly reports unavailable traces.
- aggregate baseline CSV/report is produced.
- no full benchmark campaign is launched.

A9 pass:
- Mascar/MeDiC alignment inventory is generated.
- mapping from prior GPGPU-Sim workflow to Accel-Sim available traces/runners is documented.
- any runnable aligned smoke is executed in a bounded way.
- final review pack is generated.

Final round pass:
- final git status --short is empty.
- tracked scripts/docs are committed.
- local reports and review pack exist.
