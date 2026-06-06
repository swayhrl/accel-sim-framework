# A5 results validation and documentation

## Purpose

Produce final documentation and a review pack so the Accel-Sim bringup state is auditable and reusable.

## Required tracked files

Create or update:

    scripts/accelsim/a5_collect_results.sh
    docs/accelsim_bringup/RESULTS_SUMMARY.md
    docs/accelsim_bringup/KNOWN_ISSUES.md
    docs/accelsim_bringup/RUNBOOK.md

## Required behavior of a5_collect_results.sh

- cd to repo root.
- Source scripts/accelsim/accelsim_env.sh.
- Gather:
  - git branch
  - git commit
  - git status --short
  - CUDA version
  - gcc/g++ versions
  - cmake version
  - python version
  - binary path and file info
  - ldd missing libs, if any
  - A0-A4 phase reports list
  - stats CSV list
  - trace list, if present
  - run directories matching A2, A3, A4 run names
- Write:
    .local_reports/A5_final_summary_TIMESTAMP.md
- Create review pack:
    review_packs/A0_A5_ACCELSIM_BRINGUP_review_pack_TIMESTAMP.tar.gz
- Include in review pack:
  - docs/accelsim_bringup/*.md
  - scripts/accelsim/*.sh
  - scripts/accelsim/README.md
  - .local_reports/A0*.md
  - .local_reports/A1*.md
  - .local_reports/A2*.md
  - .local_reports/A3*.md
  - .local_reports/A4*.md
  - .local_reports/A5*.md
  - .local_reports/*_stats.csv
  - selected small logs from .local_logs, not huge logs
- Do not include traces, build directories, gpu-app-collection, or huge logs.
- Print review pack path at the end.

## RESULTS_SUMMARY.md content

Include:

- Overall result:
  - PASS
  - PARTIAL_PASS
  - BLOCKED
  - FAIL
- Per phase status:
  - A0
  - A1
  - A2
  - A3
  - A4
  - A5
- Exact commit/branch.
- Exact commands for reproducing the successful path.
- Trace root used, if any.
- Run names used.
- Stats CSV files.
- Known limitations.

## KNOWN_ISSUES.md content

List only issues actually observed, plus likely future risks clearly marked as not yet observed.

Typical categories:

- CUDA/NVBit mismatch
- no GPU visible
- pre-trace downloader requires interactive choice
- no small trace downloaded
- run_simulations.py trace root layout mismatch
- long simulation timeout
- build warning but binary usable

## RUNBOOK.md content

Make it concise and operational:

1. Environment setup.
2. Build.
3. Pre-trace smoke.
4. Tracer smoke.
5. Benchmark suite.
6. Stats collection.
7. Where logs/results live.
8. How to clean local outputs.
9. What not to commit.

## Commit and review pack policy

At end:

- Use git add with explicit paths only.
- Commit tracked docs/scripts if not already committed.
- Do not commit review_packs.
- Final git status should be clean except ignored local outputs.

Recommended final commit message:

    scripts: add accel-sim bringup smoke pipeline

## A5 pass criteria

- Final summary exists.
- Known issues exists.
- Runbook exists.
- Review pack exists.
- Tracked docs/scripts committed.
- git status --short is clean after commit.
