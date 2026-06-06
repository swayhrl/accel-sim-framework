# Codex prompt for A10 real workload alignment

You are working in:

    /workspace/repos/accel-sim-framework

Complete one large round:

    A10_REAL_WORKLOAD_ALIGNMENT

Execute subphases strictly in order:

    A10A -> A10B -> A10C -> A10D -> A10E

Read these first:

    docs/accelsim_bringup/A10_MASTER.md
    docs/accelsim_bringup/A10A_PRIOR_ARTIFACT_DISCOVERY.md
    docs/accelsim_bringup/A10B_WORKLOAD_INVENTORY_EXTRACTION.md
    docs/accelsim_bringup/A10C_ACCELSIM_TRACE_MAPPING.md
    docs/accelsim_bringup/A10D_ALIGNED_SMOKE_AND_STATS.md
    docs/accelsim_bringup/A10E_CLOSEOUT_AND_REVIEW_PACK.md

Main objective:

A9 produced an alignment template. A10 must make the alignment real by reading prior Mascar and MeDiC GPGPU-Sim reproduction artifacts under /workspace/repos, extracting actual workload/config/stats evidence, mapping those workloads to currently available Accel-Sim traces, and running a bounded aligned smoke for trace-available workloads.

Hard rules:

1. Do not push.
2. Do not use git add . or git add -A.
3. Do not modify prior GPGPU-Sim repos.
4. Do not commit generated logs, traces, build dirs, hw_run, downloaded apps, or review packs.
5. Runtime outputs only under:
   .local_reports/
   .local_logs/
   .local_runs/
   .local_traces/
   hw_run/
   review_packs/
6. Do not run a full benchmark campaign.
7. Do not validate NVBit tracer in A10.
8. Do not modify Accel-Sim architectural behavior.
9. Search prior artifacts cautiously. Avoid huge recursive scans.
10. If prior artifacts are missing, report BLOCKED or PARTIAL clearly. Do not fabricate mappings.
11. Strip CR from parsed paths and CSV fields.
12. Avoid transient file named 0. If created and untracked/tiny, delete it and report it.

Required tracked scripts:

    scripts/accelsim/a10a_discover_prior_workflows.sh
    scripts/accelsim/a10b_extract_prior_inventory.py
    scripts/accelsim/a10c_build_trace_mapping.py
    scripts/accelsim/a10d_run_aligned_smoke.sh
    scripts/accelsim/a10e_collect_alignment_pack.sh
    scripts/accelsim/a10_run_all.sh

Update if needed:

    scripts/accelsim/README.md
    scripts/accelsim/a7b_n_app_smoke.sh
    scripts/accelsim/a8_small_benchmark_baseline.sh
    scripts/accelsim/a9_mascar_medic_alignment.sh

Required tracked docs:

    docs/accelsim_bringup/A10_REAL_WORKLOAD_ALIGNMENT.md
    docs/accelsim_bringup/A10_PRIOR_ARTIFACT_DISCOVERY.md
    docs/accelsim_bringup/A10_WORKLOAD_INVENTORY_SCHEMA.md
    docs/accelsim_bringup/A10_TRACE_MAPPING_SCHEMA.md
    docs/accelsim_bringup/A10_ALIGNED_SMOKE.md
    docs/accelsim_bringup/A10_MASCAR_MEDIC_GAPS.md
    docs/accelsim_bringup/RUNBOOK.md
    docs/accelsim_bringup/KNOWN_ISSUES.md

Recommended workflow:

Step 1:
Implement all tracked A10 scripts and docs.

Step 2:
Commit tracked changes explicitly. Use explicit paths only. Example:

    git add \
      scripts/accelsim/a10a_discover_prior_workflows.sh \
      scripts/accelsim/a10b_extract_prior_inventory.py \
      scripts/accelsim/a10c_build_trace_mapping.py \
      scripts/accelsim/a10d_run_aligned_smoke.sh \
      scripts/accelsim/a10e_collect_alignment_pack.sh \
      scripts/accelsim/a10_run_all.sh \
      scripts/accelsim/README.md \
      docs/accelsim_bringup/A10_REAL_WORKLOAD_ALIGNMENT.md \
      docs/accelsim_bringup/A10_PRIOR_ARTIFACT_DISCOVERY.md \
      docs/accelsim_bringup/A10_WORKLOAD_INVENTORY_SCHEMA.md \
      docs/accelsim_bringup/A10_TRACE_MAPPING_SCHEMA.md \
      docs/accelsim_bringup/A10_ALIGNED_SMOKE.md \
      docs/accelsim_bringup/A10_MASCAR_MEDIC_GAPS.md \
      docs/accelsim_bringup/RUNBOOK.md \
      docs/accelsim_bringup/KNOWN_ISSUES.md

    git commit -m "scripts: add accel-sim real workload alignment"

Step 3:
Confirm clean tree:

    git status --short

Step 4:
Run A10 in order:

    bash scripts/accelsim/a10a_discover_prior_workflows.sh
    python3 scripts/accelsim/a10b_extract_prior_inventory.py
    python3 scripts/accelsim/a10c_build_trace_mapping.py
    ACCELSIM_A10D_DRY_RUN=1 bash scripts/accelsim/a10d_run_aligned_smoke.sh
    bash scripts/accelsim/a10d_run_aligned_smoke.sh
    bash scripts/accelsim/a10e_collect_alignment_pack.sh

Alternatively, after testing individual scripts:

    bash scripts/accelsim/a10_run_all.sh

A10A requirements:
- Search /workspace/repos for real Mascar/MeDiC/GPGPU-Sim artifacts.
- Search is bounded.
- Review packs are listed and only small relevant text files extracted.
- Write A10A inventory CSV and report.

A10B requirements:
- Parse A10A artifacts.
- Extract real prior workloads with source evidence.
- Extract prior stats fields.
- Write workload inventory CSV and stats field inventory CSV.

A10C requirements:
- Discover Accel-Sim kernelslist.g traces.
- Normalize names.
- Map prior workloads to available traces.
- Write trace mapping CSV and summary.

A10D requirements:
- Select only runnable mapped workloads.
- Run at most 3 by default.
- Use direct accel-sim.out with SM7_QV100 configs.
- Enforce timeout.
- Write aligned smoke stats CSV and report.

A10E requirements:
- Write final alignment summary.
- Write A10 gaps doc if not already done.
- Generate review_packs/A10_REAL_WORKLOAD_ALIGNMENT_review_pack_*.tar.gz.
- Final git status must be clean.

Final response must include:

- A10A/A10B/A10C/A10D/A10E status table
- prior artifact inventory CSV path
- prior workload inventory CSV path
- trace mapping CSV path
- aligned smoke stats CSV path if any
- final summary path
- review pack path
- final commit hash
- final git status --short
