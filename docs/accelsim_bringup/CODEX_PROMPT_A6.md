# Codex prompt for A6 clean baseline rerun

You are working in:

    /workspace/repos/accel-sim-framework

Task:

Complete A6 clean baseline rerun for Accel-Sim.

Read first:

    docs/accelsim_bringup/A6_CLEAN_BASELINE_RERUN.md
    docs/accelsim_bringup/A6_BASELINE_REPORT_TEMPLATE.md

Context:

A0-A5 already completed and were committed. A0/A1/A2/A4/A5 passed, A3 was BLOCKED_NO_GPU. The issue to fix now is not functionality. The issue is that previous stats showed a build string like d1d9aa0_modified because the simulator was built before tracked docs/scripts were committed. A6 must rerun build and smoke tests from a clean committed tree and prove that the build string is no longer dirty or modified.

Critical rule:

Create the A6 runner script and any tracked docs first, commit them, confirm git status --short is empty, and only then run the clean baseline. If you edit any tracked file after that, commit it and rerun A6 from the beginning.

Required new tracked script:

    scripts/accelsim/a6_clean_baseline_rerun.sh

The script must:

1. Source scripts/accelsim/accelsim_env.sh.
2. Check git status is clean at script start. If not clean, write FAILED_DIRTY_TREE report and stop before build.
3. Record baseline commit.
4. Force rebuild using make -B -j$(nproc) -C ./gpu-simulator/, with normal make fallback.
5. Verify gpu-simulator/bin/release/accel-sim.out is executable and ldd has no missing libraries.
6. Find trace root from ACCELSIM_TRACE_ROOT, prior A2/A4 reports, or kernelslist.g discovery.
7. Rerun A2 style minimal pre-trace smoke using scripts/accelsim/a2_pretrace_smoke.sh.
8. Rerun A4 style smoke suite using scripts/accelsim/a4_run_smoke_suite.sh.
9. Collect A6 stats CSV paths.
10. Scan relevant A6 logs and stats for dirty, modified, and _modified build-string markers.
11. Write .local_reports/A6_clean_baseline_summary_TIMESTAMP.md.
12. Create review_packs/A6_CLEAN_BASELINE_RERUN_review_pack_TIMESTAMP.tar.gz.
13. Print A6 status, baseline commit, stats paths, review pack path, and final git status.

Do not:

- push
- use git add . or git add -A
- commit logs, traces, hw_run, .local_reports, .local_logs, .local_runs, .local_traces, or review_packs
- run large benchmark suites
- try to validate NVBit tracer in A6
- modify Accel-Sim source logic

Expected commit before rerun:

    git add \
      docs/accelsim_bringup/A6_CLEAN_BASELINE_RERUN.md \
      docs/accelsim_bringup/A6_BASELINE_REPORT_TEMPLATE.md \
      docs/accelsim_bringup/CODEX_PROMPT_A6.md \
      scripts/accelsim/a6_clean_baseline_rerun.sh

    git commit -m "scripts: add accel-sim A6 clean baseline rerun"

Then run:

    git status --short
    bash scripts/accelsim/a6_clean_baseline_rerun.sh

End response must include:

- A6 status
- baseline commit used for clean build
- whether any dirty or modified build marker remains
- A2 stats CSV path
- A4 stats CSV path
- A6 final report path
- review pack path
- final git status --short
