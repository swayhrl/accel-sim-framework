# Codex prompt for A6B-A9 Accel-Sim pipeline hardening

You are working in:

    /workspace/repos/accel-sim-framework

Complete one large round:

    A6B -> A7A -> A7B -> A8 -> A9

Read these first:

    docs/accelsim_bringup/A6B_A9_MASTER.md
    docs/accelsim_bringup/A6B_VERSION_STRING_AUDIT.md
    docs/accelsim_bringup/A7A_CLEAN_BASELINE_PIPELINE_HARDENING.md
    docs/accelsim_bringup/A7B_N_APP_SMOKE_RUNNER.md
    docs/accelsim_bringup/A8_SMALL_BENCHMARK_BASELINE.md
    docs/accelsim_bringup/A9_MASCAR_MEDIC_ALIGNMENT.md

Main objective:

Fix the A6 false dirty-build result, harden the clean baseline rerun, add a controlled N-app smoke runner, generate a small benchmark baseline, and align the workflow style with the previous Mascar and MeDiC GPGPU-Sim reproduction infrastructure.

Critical context:

A6 was run from a clean tree. Build and A2/A4 smoke passed. But it was marked FAILED_DIRTY_BUILD_STRING because the build string contained:

    accelsim-commit-2586635_modified_0.0_26-06-07-00-06-49
    gpgpu-sim_git-commit-6c3cf4ff_modified_0.0

This is a false negative. In this repo, _modified_0.0 or _modified_0 should be treated as clean diff zero when git status at build start and end is clean. Nonzero modified values or dirty should still fail.

Hard rules:

1. Do not push.
2. Do not use git add . or git add -A.
3. Do not commit generated logs, traces, build directories, hw_run, downloaded apps, or review packs.
4. Use ignored local output paths only:
   - .local_reports/
   - .local_logs/
   - .local_runs/
   - .local_traces/
   - hw_run/
   - review_packs/
5. Do not run a large benchmark campaign.
6. Do not try to validate NVBit tracer in this round.
7. Do not modify simulator architectural behavior.
8. For all rebuild or baseline-quality runs, tracked changes must be committed first and git status --short must be empty before running.

Required tracked scripts:

    scripts/accelsim/a6b_version_string_audit.sh
    scripts/accelsim/a7a_clean_baseline_hardened.sh
    scripts/accelsim/a7b_n_app_smoke.sh
    scripts/accelsim/a8_small_benchmark_baseline.sh
    scripts/accelsim/a9_mascar_medic_alignment.sh

Also update as needed:

    scripts/accelsim/a6_clean_baseline_rerun.sh
    scripts/accelsim/README.md

Required tracked docs:

    docs/accelsim_bringup/VERSION_STRING_AUDIT.md
    docs/accelsim_bringup/CLEAN_BASELINE_PIPELINE.md
    docs/accelsim_bringup/N_APP_SMOKE_RUNNER.md
    docs/accelsim_bringup/SMALL_BENCHMARK_BASELINE.md
    docs/accelsim_bringup/MASCAR_MEDIC_ALIGNMENT.md
    docs/accelsim_bringup/RUNBOOK.md
    docs/accelsim_bringup/KNOWN_ISSUES.md

Recommended execution:

Step 1: Implement all tracked scripts/docs for A6B-A9.

Step 2: Commit tracked changes explicitly. Example:

    git add \
      scripts/accelsim/a6b_version_string_audit.sh \
      scripts/accelsim/a7a_clean_baseline_hardened.sh \
      scripts/accelsim/a7b_n_app_smoke.sh \
      scripts/accelsim/a8_small_benchmark_baseline.sh \
      scripts/accelsim/a9_mascar_medic_alignment.sh \
      scripts/accelsim/a6_clean_baseline_rerun.sh \
      scripts/accelsim/README.md \
      docs/accelsim_bringup/VERSION_STRING_AUDIT.md \
      docs/accelsim_bringup/CLEAN_BASELINE_PIPELINE.md \
      docs/accelsim_bringup/N_APP_SMOKE_RUNNER.md \
      docs/accelsim_bringup/SMALL_BENCHMARK_BASELINE.md \
      docs/accelsim_bringup/MASCAR_MEDIC_ALIGNMENT.md \
      docs/accelsim_bringup/RUNBOOK.md \
      docs/accelsim_bringup/KNOWN_ISSUES.md

    git commit -m "scripts: harden accel-sim baseline pipeline"

Step 3: Confirm clean tree:

    git status --short

Step 4: Run phases in order:

    bash scripts/accelsim/a6b_version_string_audit.sh
    bash scripts/accelsim/a7a_clean_baseline_hardened.sh
    ACCELSIM_A7B_DRY_RUN=1 bash scripts/accelsim/a7b_n_app_smoke.sh
    bash scripts/accelsim/a7b_n_app_smoke.sh
    ACCELSIM_A8_DRY_RUN=1 bash scripts/accelsim/a8_small_benchmark_baseline.sh
    bash scripts/accelsim/a8_small_benchmark_baseline.sh
    ACCELSIM_A9_DRY_RUN=1 bash scripts/accelsim/a9_mascar_medic_alignment.sh
    bash scripts/accelsim/a9_mascar_medic_alignment.sh

If a phase is blocked, write the report and continue where possible.

A6B requirements:

- Audit gpu-simulator/version_detection.mk and gpu-simulator/gpgpu-sim/version_detection.mk.
- Update a6_clean_baseline_rerun.sh to classify _modified_0.0 as clean.
- Create VERSION_STRING_AUDIT.md.
- Write .local_reports/A6B_version_string_audit_*.md.

A7A requirements:

- Run updated clean baseline pipeline from clean tree.
- Confirm A2 and A4 smoke still pass.
- Confirm build string classification no longer false-fails.
- Write .local_reports/A7A_clean_baseline_hardened_*.md.

A7B requirements:

- Add controlled N-app direct smoke runner.
- Support dry run.
- Default max apps is 3.
- Use direct accel-sim.out with kernelslist.g and SM7_QV100 configs.
- Enforce timeout per app.
- Write per-app CSV and report.
- Do not run full suite.

A8 requirements:

- Add bounded small benchmark baseline script.
- Use A7B logic.
- Default max apps is 5.
- Include only traces already present.
- Produce aggregate CSV and report.
- Mark not baseline-quality if A7A did not pass.

A9 requirements:

- Search cautiously for previous Mascar and MeDiC GPGPU-Sim workflow artifacts under /workspace/repos.
- Produce mapping CSV.
- Run at most 3 aligned smoke runs if matching traces exist.
- Produce final review pack:
      review_packs/A6B_A9_ACCELSIM_PIPELINE_review_pack_*.tar.gz

Final response must include:

- phase status table for A6B, A7A, A7B, A8, A9
- baseline commit
- whether _modified_0.0 is now accepted as clean
- A7B stats CSV path
- A8 stats CSV path
- A9 mapping CSV path
- final review pack path
- final commit hash
- final git status --short
