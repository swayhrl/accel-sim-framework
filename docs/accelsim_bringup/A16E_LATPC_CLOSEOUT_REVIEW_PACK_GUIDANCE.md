# A16E LATPC closeout and review pack guidance

## Goal

Close A16 with a final summary, readiness checklist, review pack, and clean git state.

A16E should make it easy for GPT and the user to review whether the LATPC paper variant slot full chain is ready.

## Inputs

A16A reports:

.local_reports/A16A_latpc_*

A16B reports:

.local_reports/A16B_latpc_*

A16C reports:

.local_reports/A16C_latpc_*

A16D reports:

.local_reports/A16D_latpc_*

Tracked scripts and docs:

docs/accelsim_bringup/A16*
scripts/accelsim/a16*
scripts/accelsim/run_a16*

## Required tracked script

Create or update:

scripts/accelsim/a16_latpc_closeout.py

## Closeout behavior

The closeout script should:

1. Record start time, end time, and wall seconds.
2. Locate latest A16A, A16B, A16C, and A16D reports.
3. Determine final A16 status.
4. Write final summary MD.
5. Write readiness checklist CSV.
6. Capture git diff summary and git status into .local_reports.
7. Create review pack tar.gz under review_packs.
8. Print key output paths.

## Required output files

.local_reports/A16E_latpc_final_summary_<timestamp>.md
.local_reports/A16E_latpc_readiness_checklist_<timestamp>.csv
.local_reports/A16E_latpc_git_status_<timestamp>.txt
.local_reports/A16E_latpc_git_diffstat_<timestamp>.txt
review_packs/A16_LATPC_PAPER_VARIANT_SLOT_review_pack_<timestamp>.tar.gz

## Final summary required sections

Include:

1. Round identity
2. Paper identity and PDF path
3. A16 scope
4. Selected workload
5. Variant definitions
6. Matrix commands and run status
7. Baseline vs no-op comparison result
8. What passed
9. What did not attempt
10. Limitations
11. Review pack path
12. Git commit or pending changes
13. Recommended next round

## Required limitation statements

Include these statements clearly:

- A16 does not implement LATPC.
- A16 does not reproduce LATPC speedup.
- A16 validates only baseline-vs-no-op variant infrastructure.
- A16 uses existing traces only.
- A16 does not validate NVBit tracing if no GPU is visible.
- A16 does not validate full 24-workload paper campaign.
- A17 or later must add a paper-specific mechanism design before simulator changes.

## Readiness checklist CSV columns

Include:

- item
- status
- evidence_path
- notes

Checklist items:

- paper_pdf_exists
- paper_profile_created
- trace_available_for_selected_workload
- selected_workload_is_in_paper
- noop_variant_manifest_created
- baseline_and_noop_inputs_identical
- variant_matrix_created
- baseline_run_passed
- noop_run_passed
- stats_parsed
- noop_comparison_passed
- final_summary_created
- review_pack_created
- no_runtime_outputs_committed
- git_status_clean_or_explained

## Review pack contents

Include:

- docs/accelsim_bringup/A16*.md
- scripts/accelsim/a16*.py
- scripts/accelsim/run_a16*.py
- latest .local_reports/A16A*
- latest .local_reports/A16B*
- latest .local_reports/A16C*
- latest .local_reports/A16D*
- latest .local_reports/A16E*
- relevant .local_logs/A16C* logs
- git status and diffstat text files

Do not include:

- large trace directories
- build products
- hw_run dumps
- unrelated .local_reports from older rounds unless specifically needed
- the paper PDF unless it is already tracked and small enough; by default do not pack the PDF

## Final git handling

After scripts and docs are complete, inspect:

git status --short

Then add only explicit source paths. Example:

git add docs/accelsim_bringup/A16_LATPC_PAPER_VARIANT_SLOT_MASTER_GUIDANCE.md
git add docs/accelsim_bringup/A16A_LATPC_PAPER_PROFILE_AND_WORKLOAD_LOCK_GUIDANCE.md
git add docs/accelsim_bringup/A16B_LATPC_NOOP_VARIANT_SLOT_GUIDANCE.md
git add docs/accelsim_bringup/A16C_LATPC_VARIANT_MATRIX_RUNNER_GUIDANCE.md
git add docs/accelsim_bringup/A16D_LATPC_BASELINE_VS_NOOP_VALIDATION_GUIDANCE.md
git add docs/accelsim_bringup/A16E_LATPC_CLOSEOUT_REVIEW_PACK_GUIDANCE.md
git add scripts/accelsim/a16_latpc_paper_profile.py
git add scripts/accelsim/a16_latpc_variant_lib.py
git add scripts/accelsim/a16_latpc_variant_slot.py
git add scripts/accelsim/run_a16_latpc_variant_matrix.py
git add scripts/accelsim/a16_latpc_validate_noop.py
git add scripts/accelsim/a16_latpc_closeout.py

Some script paths may not exist if implementation merged helpers differently. Add only existing explicit paths.

Commit message:

scripts: add LATPC paper variant slot pipeline

Never use git add . or git add -A.

Do not commit runtime reports or review packs.

## Final response requirements

Report:

- final commit hash
- review pack path
- selected workload
- final A16 status
- key report paths
- final git status --short
- any blocker or warning
- explicit statement that A16 is not LATPC mechanism reproduction
