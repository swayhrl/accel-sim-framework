# Codex prompt for Accel-Sim A0-A5 bringup

You are working in:

    /workspace/repos/accel-sim-framework

Complete the Accel-Sim bringup as one large round, but execute it strictly in order:

    A0 -> A1 -> A2 -> A3 -> A4 -> A5

Read these guidance files before editing or running commands:

    docs/accelsim_bringup/A0_A5_MASTER.md
    docs/accelsim_bringup/A0_ENV_AND_LOCAL_DIRS.md
    docs/accelsim_bringup/A1_BUILD_AND_BINARY_SMOKE.md
    docs/accelsim_bringup/A2_PRETRACE_MINIMAL_SIM.md
    docs/accelsim_bringup/A3_TRACER_FLOW.md
    docs/accelsim_bringup/A4_BENCHMARK_PIPELINE.md
    docs/accelsim_bringup/A5_RESULTS_AND_DOCS.md

Main objective:

Bring up Accel-Sim enough that we have a reproducible environment, build smoke, minimal simulation smoke, optional tracer smoke, reusable scripts, final docs, and a review pack.

Important constraints:

1. Do not push.
2. Do not use git add . or git add -A.
3. Do not commit generated logs, traces, build dirs, downloaded apps, or review packs.
4. Put local outputs only under ignored local paths:
   - .local_reports/
   - .local_logs/
   - .local_runs/
   - .local_traces/
   - hw_run/
   - review_packs/
5. Add those paths to .git/info/exclude, not .gitignore.
6. Create tracked reusable scripts under scripts/accelsim/.
7. Create tracked final docs under docs/accelsim_bringup/.
8. For every phase, write a phase report into .local_reports/.
9. Record start time, end time, and wall clock seconds for every phase.
10. If a phase is blocked, document the exact reason and continue where possible.
11. A3 is conditional. If no GPU is visible or tracer prerequisites fail, mark A3 blocked rather than treating the whole round as failed.
12. Avoid large uncontrolled downloads. For pre-traces, inspect help/options first and only use a small target if available.
13. Do not run large all-app benchmark campaigns.

Expected tracked scripts:

    scripts/accelsim/accelsim_env.sh
    scripts/accelsim/a0_env_check.sh
    scripts/accelsim/a1_build_smoke.sh
    scripts/accelsim/a2_pretrace_smoke.sh
    scripts/accelsim/a3_trace_rodinia_smoke.sh
    scripts/accelsim/a4_run_smoke_suite.sh
    scripts/accelsim/a5_collect_results.sh
    scripts/accelsim/README.md

Expected tracked docs:

    docs/accelsim_bringup/RESULTS_SUMMARY.md
    docs/accelsim_bringup/KNOWN_ISSUES.md
    docs/accelsim_bringup/RUNBOOK.md

Execution plan:

A0:
- Create local ignored dirs and update .git/info/exclude.
- Implement accelsim_env.sh and a0_env_check.sh.
- Run a0_env_check.sh.
- Save logs and report.

A1:
- Implement a1_build_smoke.sh.
- Run build smoke.
- Prefer make build, fallback to cmake if needed.
- Verify gpu-simulator/bin/release/accel-sim.out.
- Save logs and report.

A2:
- Implement a2_pretrace_smoke.sh.
- Discover existing traces first.
- If trace root is available, run rodinia_2.0-ft with QV100-SASS and collect stats.
- If no trace exists, inspect get-accel-sim-traces.py help. Avoid huge downloads. Mark blocked if no small safe trace can be acquired.
- Save logs, report, and stats if available.

A3:
- Implement a3_trace_rodinia_smoke.sh.
- Check GPU visibility.
- If GPU exists, build tracer, clone/reuse gpu-app-collection in .local_runs, build rodinia_2.0-ft, generate traces, then run simulation and stats.
- If no GPU or other blocker, write blocked report.
- Save logs, report, and stats if available.

A4:
- Implement a4_run_smoke_suite.sh and scripts/accelsim/README.md.
- Provide dry-run mode.
- Run dry-run always.
- Run real smoke if a valid trace root exists from A2 or A3.
- Save logs, report, and stats if available.

A5:
- Implement a5_collect_results.sh.
- Create RESULTS_SUMMARY.md, KNOWN_ISSUES.md, RUNBOOK.md.
- Create review pack under review_packs/.
- Commit tracked scripts/docs using explicit git add paths only.
- Final git status --short should be clean except ignored local outputs.

Suggested final commands after implementation:

    git add \
      docs/accelsim_bringup/A0_A5_MASTER.md \
      docs/accelsim_bringup/A0_ENV_AND_LOCAL_DIRS.md \
      docs/accelsim_bringup/A1_BUILD_AND_BINARY_SMOKE.md \
      docs/accelsim_bringup/A2_PRETRACE_MINIMAL_SIM.md \
      docs/accelsim_bringup/A3_TRACER_FLOW.md \
      docs/accelsim_bringup/A4_BENCHMARK_PIPELINE.md \
      docs/accelsim_bringup/A5_RESULTS_AND_DOCS.md \
      docs/accelsim_bringup/CODEX_PROMPT_A0_A5.md \
      docs/accelsim_bringup/RESULTS_SUMMARY.md \
      docs/accelsim_bringup/KNOWN_ISSUES.md \
      docs/accelsim_bringup/RUNBOOK.md \
      scripts/accelsim/README.md \
      scripts/accelsim/accelsim_env.sh \
      scripts/accelsim/a0_env_check.sh \
      scripts/accelsim/a1_build_smoke.sh \
      scripts/accelsim/a2_pretrace_smoke.sh \
      scripts/accelsim/a3_trace_rodinia_smoke.sh \
      scripts/accelsim/a4_run_smoke_suite.sh \
      scripts/accelsim/a5_collect_results.sh

    git commit -m "scripts: add accel-sim bringup smoke pipeline"

End-of-round response must include:

- Per-phase status table.
- Commands executed.
- Important logs/reports paths.
- Stats CSV paths if any.
- Review pack path.
- Final commit hash.
- Final git status --short.
