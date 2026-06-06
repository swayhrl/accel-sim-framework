# A6 clean baseline rerun

## Goal

Rerun the Accel-Sim build and minimal smoke tests from a clean committed tree, so the reported Accel-Sim/GPGPU-Sim build strings no longer contain dirty or modified markers.

This is a validation round, not a feature round.

## Background

A0-A5 completed successfully enough to bring up Accel-Sim:

- A0 PASS: environment wrapper and local ignored directories
- A1 PASS: simulator build, accel-sim.out executable, ldd no missing libs
- A2 PASS: minimal pre-trace SASS smoke with tesla-v100 rodinia_2.0-ft trace
- A3 BLOCKED_NO_GPU: nvidia-smi and /dev/nvidia* unavailable, tracer not verified
- A4 PASS: dry-run and real direct smoke suite
- A5 PASS: final summary and review pack generated

However, previous stats showed a build string like:

    d1d9aa0_modified

The likely reason is that A1/A2/A4 ran before tracked docs/scripts were committed. A6 must remove this ambiguity.

## Non-goals

Do not implement new simulator behavior.

Do not change Accel-Sim source logic.

Do not run large benchmark suites.

Do not try to force tracer bringup when no GPU is visible.

Do not commit logs, traces, downloaded apps, build directories, hw_run, or review packs.

## Required new tracked script

Create:

    scripts/accelsim/a6_clean_baseline_rerun.sh

The script must be executable.

## Required local output paths

Use only ignored local paths for outputs:

    .local_reports/
    .local_logs/
    review_packs/

Do not write A6 runtime output into /workspace/tmp.

## Critical sequencing rule

This rule is mandatory.

1. Create or update the A6 tracked script and any tracked docs.
2. Commit those tracked changes.
3. Confirm:

       git status --short

   prints nothing.
4. Only then run:

       bash scripts/accelsim/a6_clean_baseline_rerun.sh

5. After the baseline rerun starts, do not edit tracked files. If a tracked-file fix is needed, fix it, commit it, return to step 3, and rerun A6 from the beginning.

This is required because any tracked modification before build may cause the build string to contain modified.

## Required behavior of a6_clean_baseline_rerun.sh

The script must:

1. cd to the repo root.
2. Source:

       scripts/accelsim/accelsim_env.sh

3. Record start time and wall clock seconds.
4. Check and record:

       git branch --show-current
       git rev-parse HEAD
       git status --short
       nvcc --version
       gcc --version
       g++ --version
       cmake --version
       python3 --version

5. If git status is not clean at script start, stop before build and write a FAILED_DIRTY_TREE report.
6. Save baseline commit:

       BASELINE_COMMIT=$(git rev-parse HEAD)
       BASELINE_SHORT=$(git rev-parse --short=12 HEAD)

7. Force a rebuild enough to refresh the build string.

Preferred command:

       make -B -j$(nproc) -C ./gpu-simulator/

If this fails, try normal make:

       make -j$(nproc) -C ./gpu-simulator/

If both fail but the binary exists, record PARTIAL_BUILD_BINARY_EXISTS and continue only if the binary is executable and ldd has no missing libraries.

8. Verify:

       test -x ./gpu-simulator/bin/release/accel-sim.out
       file ./gpu-simulator/bin/release/accel-sim.out
       ldd ./gpu-simulator/bin/release/accel-sim.out

Fail if ldd contains:

       not found

9. Determine trace root.

Priority:

- Use ACCELSIM_TRACE_ROOT if set.
- Otherwise inspect previous reports under .local_reports/A2*.md and .local_reports/A4*.md for trace root hints.
- Otherwise discover from kernelslist.g under:
    - .local_traces
    - hw_run
    - current repo tree

The script should print candidate trace roots.

If no usable trace root is found, mark BLOCKED_NO_TRACE. Do not download large traces in A6.

10. Run minimal pre-trace smoke.

Use existing script if it is available:

       ACCELSIM_TRACE_ROOT="$TRACE_ROOT" \
       ACCELSIM_RUN_NAME="$RUN_NAME_A2" \
       bash scripts/accelsim/a2_pretrace_smoke.sh

where RUN_NAME_A2 should include A6 and timestamp, for example:

       A6_pretrace_clean_YYYYMMDD_HHMMSS

11. Run A4 smoke suite.

Use existing script if available:

       ACCELSIM_TRACE_ROOT="$TRACE_ROOT" \
       ACCELSIM_RUN_NAME="$RUN_NAME_A4" \
       bash scripts/accelsim/a4_run_smoke_suite.sh

where RUN_NAME_A4 should include A6 and timestamp, for example:

       A6_suite_clean_YYYYMMDD_HHMMSS

12. Collect stats CSV paths.

Expected local files may look like:

       .local_reports/A6_pretrace_clean_*_stats.csv
       .local_reports/A6_suite_clean_*_stats.csv

If existing scripts produce slightly different names, locate them and record the exact paths.

13. Validate build string cleanliness.

The script must scan A6 logs and stats for:

       _modified
       modified
       dirty

Case-insensitive is acceptable.

If any of these appear in Accel-Sim or GPGPU-Sim build string context, mark A6 FAILED_DIRTY_BUILD_STRING.

If these words appear only in unrelated explanatory docs, do not fail; record the grep context and judge carefully.

Also try to find the baseline short commit in logs/stats. If the exact short commit is not present but no dirty marker appears, mark PASS_NO_DIRTY_MARKER_COMMIT_NOT_FOUND rather than failing.

14. Write final A6 markdown report:

       .local_reports/A6_clean_baseline_summary_TIMESTAMP.md

The report must include:

- status
- baseline commit
- branch
- git status at start
- git status at end
- build command used
- binary path
- ldd result summary
- trace root used
- A2 rerun name
- A4 rerun name
- stats CSV paths
- whether dirty or modified markers were found
- grep excerpts for build strings
- limitations

15. Create review pack:

       review_packs/A6_CLEAN_BASELINE_RERUN_review_pack_TIMESTAMP.tar.gz

Include:

- docs/accelsim_bringup/A6_CLEAN_BASELINE_RERUN.md
- docs/accelsim_bringup/A6_BASELINE_REPORT_TEMPLATE.md if present
- docs/accelsim_bringup/CODEX_PROMPT_A6.md
- scripts/accelsim/a6_clean_baseline_rerun.sh
- scripts/accelsim/accelsim_env.sh
- scripts/accelsim/a2_pretrace_smoke.sh
- scripts/accelsim/a4_run_smoke_suite.sh
- .local_reports/A6*.md
- .local_reports/A6*_stats.csv
- small A6 logs from .local_logs

Do not include:

- traces
- hw_run directories
- gpu-app-collection
- build directories
- large logs
- review_packs inside review_packs

16. Final output should print:

- A6 status
- baseline commit
- stats CSV paths
- review pack path
- final git status --short

## Expected final state

After A6 execution:

- git status --short should be empty.
- A6 report should exist under .local_reports.
- A6 review pack should exist under review_packs.
- A6 stats should not show a dirty or modified build string.
- A6 should clearly state that this is still a minimal smoke, not full Rodinia.

## Commit policy

Codex should make one tracked commit before running the clean baseline:

    scripts: add accel-sim A6 clean baseline rerun

This commit should include:

    scripts/accelsim/a6_clean_baseline_rerun.sh
    docs/accelsim_bringup/A6_CLEAN_BASELINE_RERUN.md
    docs/accelsim_bringup/A6_BASELINE_REPORT_TEMPLATE.md
    docs/accelsim_bringup/CODEX_PROMPT_A6.md

After that commit, Codex should run A6.

Do not make another tracked commit after the baseline rerun unless a script bug must be fixed. If a bug fix is needed, commit it first, then rerun A6 from a clean tree.

## A6 pass criteria

PASS requires all of:

- clean git status at A6 script start
- rebuild attempted from clean tree
- accel-sim.out executable
- ldd no missing libraries
- A2 or equivalent minimal pre-trace smoke rerun completed
- A4 or equivalent smoke suite rerun completed
- stats CSV produced
- no dirty or modified marker in relevant build string context
- final git status clean
- review pack generated

PARTIAL_PASS is acceptable if:

- rebuild fails but clean existing binary works, and this is clearly recorded
- build strings are clean
- smoke tests pass

BLOCKED is acceptable only for:

- missing trace root
- missing previously downloaded pre-trace
- environment no longer has required CUDA/toolchain

A3 tracer is not part of A6. Do not fail A6 because no GPU exists.
