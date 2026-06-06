# A6B version string audit

## Goal

Fix the false dirty-build failure observed in A6.

A6 showed strings like:

    accelsim-commit-2586635_modified_0.0_26-06-07-00-06-49
    gpgpu-sim_git-commit-6c3cf4ff_modified_0.0

The tree was clean, rebuild passed, and smoke tests passed. The problem is the classification rule, not the build itself.

## Files to inspect

Codex must inspect:

    gpu-simulator/version_detection.mk
    gpu-simulator/gpgpu-sim/version_detection.mk

Also inspect the existing A6 runner:

    scripts/accelsim/a6_clean_baseline_rerun.sh

And relevant A6 local reports if present:

    .local_reports/A6_clean_baseline_summary_*.md
    .local_reports/A6_dirty_marker_scan_*.log

## Required tracked script

Create:

    scripts/accelsim/a6b_version_string_audit.sh

This script should:

1. cd to repo root.
2. Source scripts/accelsim/accelsim_env.sh.
3. Record:
   - git branch
   - git commit
   - git status --short
   - relevant version_detection.mk excerpts
   - previous A6 build string excerpts if present
4. Explain how _modified_0.0 should be interpreted.
5. Test the classification logic using sample strings:
   - accelsim-commit-2586635_modified_0.0_26-06-07-00-06-49 should be CLEAN
   - gpgpu-sim_git-commit-6c3cf4ff_modified_0.0 should be CLEAN
   - accelsim-commit-abc_modified_0 should be CLEAN
   - accelsim-commit-abc_modified_1.0 should be DIRTY
   - gpgpu-sim_git-commit-abc_modified_2 should be DIRTY
   - accelsim-commit-abc_dirty should be DIRTY
6. Write report:
   - .local_reports/A6B_version_string_audit_TIMESTAMP.md

## Required tracked doc

Create or update:

    docs/accelsim_bringup/VERSION_STRING_AUDIT.md

It must include:

- version string examples.
- why _modified_0.0 is not dirty in this repo.
- accepted clean forms:
    _modified_0
    _modified_0.0
    _modified_0.00
- rejected dirty forms:
    dirty
    _modified_1
    _modified_1.0
    _modified_2
    _modified_nonzero
- the rule that git status at build start must still be clean.
- the rule that _modified_0.0 is only acceptable when git status start and end are clean.

## Required update to A6 runner

Update:

    scripts/accelsim/a6_clean_baseline_rerun.sh

The old behavior likely greps for modified or dirty. Replace it with a real classifier.

Recommended classifier behavior:

- If git status at script start is not empty, fail before build.
- If any relevant build string contains dirty, fail.
- If a relevant build string contains _modified_NUMBER:
  - parse NUMBER
  - if NUMBER numeric value is 0, accept as clean diff zero
  - if NUMBER numeric value is greater than 0, fail
- If no modified token is found and no dirty token is found, accept as clean.
- If parsing fails for a suspicious modified token, mark NEEDS_REVIEW rather than silent pass.
- Store grep context in the A6 report.

Implementation can be shell, awk, sed, or python3. Prefer readability over clever one-liners.

A simple robust approach is to add a small python3 block inside the shell script to parse relevant strings.

Suggested status names:

    PASS_CLEAN_DIFF_ZERO
    PASS_NO_DIRTY_MARKER
    FAILED_DIRTY_TREE
    FAILED_DIRTY_BUILD_STRING
    NEEDS_REVIEW_VERSION_STRING

## Important caution

Do not modify version_detection.mk unless there is a clear bug. The safer fix is to adjust our classification logic.

## Commands to run for A6B

After implementing and committing tracked changes, from a clean tree run:

    bash scripts/accelsim/a6b_version_string_audit.sh

Then check:

    git status --short

## A6B pass criteria

- a6b_version_string_audit.sh exists and passes sample classification tests.
- VERSION_STRING_AUDIT.md exists.
- a6_clean_baseline_rerun.sh no longer fails on _modified_0.0.
- A6B report exists.
