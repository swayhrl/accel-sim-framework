# A7A clean baseline pipeline hardening

## Goal

After A6B fixes version string classification, rerun the clean baseline pipeline from a committed clean tree and confirm the baseline is usable.

This phase should turn A6 from a false negative into a clean baseline result.

## Required tracked script

Create:

    scripts/accelsim/a7a_clean_baseline_hardened.sh

The script should be a coordinator around the updated A6 runner.

Required behavior:

1. cd to repo root.
2. Source scripts/accelsim/accelsim_env.sh.
3. Record start time, end time, and wall seconds.
4. Refuse to run if git status --short is not empty.
5. Record baseline commit:
       git rev-parse HEAD
6. Run:
       bash scripts/accelsim/a6_clean_baseline_rerun.sh
7. Locate the newest A6 summary:
       .local_reports/A6_clean_baseline_summary_*.md
8. Determine final A7A status:
   - PASS if A6 summary is PASS, PASS_CLEAN_DIFF_ZERO, or PASS_NO_DIRTY_MARKER.
   - FAIL if A6 summary reports FAILED_DIRTY_TREE or FAILED_DIRTY_BUILD_STRING.
   - BLOCKED if A6 summary reports missing trace/toolchain.
   - NEEDS_REVIEW if status cannot be parsed.
9. Write:
       .local_reports/A7A_clean_baseline_hardened_TIMESTAMP.md
10. Include:
   - baseline commit
   - A6 summary path
   - A2 stats path from A6 rerun
   - A4 stats path from A6 rerun
   - trace root used
   - build string excerpts
   - final status
11. Do not edit tracked docs after the clean rerun starts.

## Required tracked doc

Create or update:

    docs/accelsim_bringup/CLEAN_BASELINE_PIPELINE.md

It must explain:

- clean-tree sequencing rule.
- why build-string validation requires committed tracked files first.
- status names and meanings.
- how to rerun:
      bash scripts/accelsim/a7a_clean_baseline_hardened.sh
- how to interpret:
      PASS_CLEAN_DIFF_ZERO
- where reports and stats live.

## Required README update

Update scripts/accelsim/README.md with A6B and A7A usage.

## A7A run sequence

Codex should not run A7A until all tracked script/doc changes for A6B-A9 are committed.

After commit and clean tree:

    git status --short
    bash scripts/accelsim/a7a_clean_baseline_hardened.sh

## A7A pass criteria

- clean tree at start.
- updated A6 rerun completes.
- A2 style smoke passes.
- A4 style smoke passes.
- version string classification is PASS_CLEAN_DIFF_ZERO or equivalent.
- A7A report exists.
