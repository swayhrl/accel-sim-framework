# Codex prompt for A11-A15 paper reproduction infrastructure

You are working in:

    /workspace/repos/accel-sim-framework

Complete one large round:

    A11_A15_PAPER_REPRODUCTION_PIPELINE

Execute strictly in order:

    A11 -> A12 -> A13 -> A14 -> A15

Read these first:

    docs/accelsim_bringup/A11_A15_MASTER.md
    docs/accelsim_bringup/A11_STATS_EQUIVALENCE_NARROW.md
    docs/accelsim_bringup/A12_WORKLOAD_CONFIG_LOCKDOWN.md
    docs/accelsim_bringup/A13_EXPERIMENT_MATRIX_RUNNER.md
    docs/accelsim_bringup/A14_PAPER_REPRODUCTION_READY.md
    docs/accelsim_bringup/A15_TRACE_GPU_GAP_PLAN.md

Main objective:

Move Accel-Sim from A10 real workload alignment to paper reproduction infrastructure readiness.

A11:
- Build comparison-grade stats parser for narrow workloads.
- Use Mascar/hotspot and MeDiC/srad if available.
- Distinguish first, last, aggregate_sum, and per_kernel stats modes.
- Produce normalized stats CSV and stats equivalence matrix.

A12:
- Deduplicate A10 evidence rows into unique workload/config/run-level lockfile.
- Preserve evidence sources.
- Mark stats readiness and config equivalence.
- Define smoke, pilot, and paper-candidate sets.

A13:
- Build experiment matrix runner from the A12 lockfile.
- Support baseline/variant labels, dry-run, max-runs, timeout, resume, rerun-failed, and stats mode.
- Run only bounded baseline smoke by default.
- Produce matrix CSV and results CSV.

A14:
- Demonstrate the minimal paper-reproduction loop.
- Produce mini result table, readiness checklist, and PAPER_REPRODUCTION_READY.md.
- Clearly state what is ready and what remains missing.

A15:
- Check GPU/tracer availability.
- Produce trace gap matrix and trace acquisition plan.
- Do not fail solely because no GPU is visible.
- Generate final A11-A15 review pack.

Hard rules:

1. Do not push.
2. Do not use git add . or git add -A.
3. Do not modify prior GPGPU-Sim repos.
4. Do not commit .local_reports, .local_logs, .local_runs, .local_traces, hw_run, review_packs, traces, build products, or downloaded apps.
5. Do not run a full benchmark campaign.
6. Do not validate NVBit tracer or generate new traces unless GPU is visible and ACCELSIM_A15_ALLOW_TRACE_GENERATION=1.
7. Do not implement paper mechanisms or Accel-Sim architecture changes.
8. Every phase must write a local report with start/end/wall seconds, status, inputs, outputs, commands, blockers, and limitations.
9. Strip CR from parsed paths and CSV fields.
10. Avoid transient file named 0. If it appears and is untracked/tiny/generated, remove it and report it.
11. Tracked script/doc changes must be committed before baseline-quality runs.
12. Final git status --short must be empty.

Required tracked scripts:

    scripts/accelsim/a11_stats_equivalence_narrow.py
    scripts/accelsim/a12_workload_config_lockdown.py
    scripts/accelsim/a13_experiment_matrix_runner.py
    scripts/accelsim/a14_reproduction_readiness_closeout.sh
    scripts/accelsim/a15_trace_gpu_gap_plan.sh
    scripts/accelsim/a11_a15_run_all.sh

Optional helper scripts are allowed:

    scripts/accelsim/accelsim_stats_parser.py
    scripts/accelsim/accelsim_csv_utils.py
    scripts/accelsim/accelsim_trace_utils.py

Required tracked docs:

    docs/accelsim_bringup/STATS_EQUIVALENCE_SCHEMA.md
    docs/accelsim_bringup/WORKLOAD_CONFIG_LOCKDOWN.md
    docs/accelsim_bringup/EXPERIMENT_MATRIX_SCHEMA.md
    docs/accelsim_bringup/PAPER_REPRODUCTION_READY.md
    docs/accelsim_bringup/TRACE_ACQUISITION_PLAN.md
    docs/accelsim_bringup/RUNBOOK.md
    docs/accelsim_bringup/KNOWN_ISSUES.md

Recommended implementation workflow:

Step 1:
Implement tracked scripts and docs.

Step 2:
Commit tracked changes with explicit paths only. Example:

    git add \
      scripts/accelsim/a11_stats_equivalence_narrow.py \
      scripts/accelsim/a12_workload_config_lockdown.py \
      scripts/accelsim/a13_experiment_matrix_runner.py \
      scripts/accelsim/a14_reproduction_readiness_closeout.sh \
      scripts/accelsim/a15_trace_gpu_gap_plan.sh \
      scripts/accelsim/a11_a15_run_all.sh \
      scripts/accelsim/README.md \
      docs/accelsim_bringup/STATS_EQUIVALENCE_SCHEMA.md \
      docs/accelsim_bringup/WORKLOAD_CONFIG_LOCKDOWN.md \
      docs/accelsim_bringup/EXPERIMENT_MATRIX_SCHEMA.md \
      docs/accelsim_bringup/PAPER_REPRODUCTION_READY.md \
      docs/accelsim_bringup/TRACE_ACQUISITION_PLAN.md \
      docs/accelsim_bringup/RUNBOOK.md \
      docs/accelsim_bringup/KNOWN_ISSUES.md

    git commit -m "scripts: add accel-sim paper reproduction pipeline"

Step 3:
Confirm clean tree:

    git status --short

Step 4:
Run in order:

    python3 scripts/accelsim/a11_stats_equivalence_narrow.py
    python3 scripts/accelsim/a12_workload_config_lockdown.py
    ACCELSIM_A13_DRY_RUN=1 python3 scripts/accelsim/a13_experiment_matrix_runner.py
    python3 scripts/accelsim/a13_experiment_matrix_runner.py
    bash scripts/accelsim/a14_reproduction_readiness_closeout.sh
    bash scripts/accelsim/a15_trace_gpu_gap_plan.sh

Alternatively, after individual scripts are verified:

    bash scripts/accelsim/a11_a15_run_all.sh

Final response must include:

- A11/A12/A13/A14/A15 status table
- baseline commit
- A11 equivalence matrix CSV path
- A11 normalized stats CSV path
- A12 lockfile path
- A13 experiment matrix CSV path
- A13 results CSV path
- A14 mini result table path
- A14 readiness checklist path
- A15 trace gap matrix path
- final review pack path
- final commit hash
- final git status --short
