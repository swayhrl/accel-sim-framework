# A23B LATPC VM substrate closeout guidance

## Goal

Close A20-A23 with a final report, review pack, source patch, readiness checklist, and clean git state.

## Required script

Create:

scripts/accelsim/a23b_latpc_vm_substrate_closeout.py

## Inputs

All A20-A23 reports and logs.

Tracked guidance docs:

docs/accelsim_bringup/A20*.md
docs/accelsim_bringup/A21*.md
docs/accelsim_bringup/A22*.md
docs/accelsim_bringup/A23*.md
docs/accelsim_bringup/A20_A23_LATPC_VM_SUBSTRATE_MASTER_GUIDANCE.md
docs/accelsim_bringup/A20_A37_UPDATED_LATPC_REPRODUCTION_PLAN.md

Scripts:

scripts/accelsim/a20*.py
scripts/accelsim/a21*.py
scripts/accelsim/a22*.py
scripts/accelsim/a23*.py

Nested source files modified in gpu-simulator/gpgpu-sim.

## Required tasks

1. Collect latest reports.
2. Capture top-level git status.
3. Capture nested git status.
4. Capture nested source diff or patch.
5. Write final summary MD.
6. Write checklist CSV.
7. Create review pack.
8. Commit nested source changes if any.
9. Commit top-level docs/scripts after nested commit.
10. Report final status and hashes.

## Final summary sections

1. Round identity.
2. Starting point from A19.
3. A20 design result.
4. A21 implementation result.
5. A22 validation result.
6. A23 timing decision.
7. Source files changed.
8. Shadow VM stats observed.
9. Behavior validation result.
10. Readiness classification.
11. Limitations.
12. Next recommended round.
13. Review pack path.
14. Git hashes.
15. Clear statement that LATPC mechanisms were not implemented.

## Required limitation statements

Include:

- A20-A23 did not implement Regularity Detector as a functional prefetch generator.
- A20-A23 did not implement LATC compressed real TLB MSHR behavior.
- A20-A23 did not implement LATP real PTW batching or prefetching.
- A20-A23 did not reproduce LATPC speedup.
- The substrate is shadow stats unless explicitly documented otherwise.
- Any timing integration must be a future round.
- Shadow VM stats can support mechanism analysis but not faithful IPC speedup claims.

## Checklist CSV columns

- item
- status
- evidence_path
- notes

Checklist items:

- a19_context_found
- a20_requirements_complete
- architecture_complete
- implementation_gate_complete
- source_implementation_done_or_blocked
- address_hook_integrated
- stats_print_integrated
- runner_integrated
- build_passed
- baseline_run_passed
- shadow_vm_run_passed
- behavior_unchanged
- shadow_stats_nontrivial
- sanity_checks_passed
- sensitivity_checks_done
- foundation_report_done
- timing_decision_done
- source_patch_captured
- review_pack_created
- nested_git_clean
- top_level_git_clean

## Review pack contents

Include:

- docs/accelsim_bringup/A20*.md
- docs/accelsim_bringup/A21*.md
- docs/accelsim_bringup/A22*.md
- docs/accelsim_bringup/A23*.md
- docs/accelsim_bringup/A20_A23_LATPC_VM_SUBSTRATE_MASTER_GUIDANCE.md
- docs/accelsim_bringup/A20_A37_UPDATED_LATPC_REPRODUCTION_PLAN.md
- scripts/accelsim/a20*.py
- scripts/accelsim/a21*.py
- scripts/accelsim/a22*.py
- scripts/accelsim/a23*.py
- latest .local_reports/A20*
- latest .local_reports/A21*
- latest .local_reports/A22*
- latest .local_reports/A23*
- latest .local_logs/A22*
- source patch diff
- git status and diffstat reports

Do not include:

- trace directories
- build outputs
- unrelated old reports
- review packs inside review pack
- paper PDF unless already tracked

## Required output files

.local_reports/A23B_latpc_vm_substrate_closeout_<timestamp>.md
.local_reports/A23B_latpc_vm_substrate_checklist_<timestamp>.csv
.local_reports/A23B_latpc_git_status_<timestamp>.txt
.local_reports/A23B_latpc_git_diffstat_<timestamp>.txt
.local_reports/A23B_latpc_source_patch_<timestamp>.diff
review_packs/A20_A23_LATPC_VM_SUBSTRATE_review_pack_<timestamp>.tar.gz

## Git commands policy

Do not use git add . or git add -A.

Nested repo example:

cd /workspace/repos/accel-sim-framework/gpu-simulator/gpgpu-sim
git status --short
git add explicit_modified_source_paths
git commit -m "sim: add LATPC shadow VM stats substrate"

Top-level example:

cd /workspace/repos/accel-sim-framework
git add explicit_docs_and_scripts
git commit -m "scripts: add LATPC VM substrate pipeline"

Only add existing files.

Do not commit runtime outputs.

## Status rules

PASS:
Implementation and validation passed, review pack created, git clean.

PASS_WITH_WARNINGS:
Substrate works but has approximations or partial PWC/PTW support.

PASS_DESIGN_ONLY:
No source implementation, but design and closeout complete.

FAIL_BEHAVIOR_CHANGED:
Shadow VM changed real simulator stats.

FAIL_STATS_EMPTY:
Substrate did not produce meaningful stats.

FAIL_DIRTY_TREE:
Final git status dirty for unexpected files.

## Final Codex response requirements

Report:

1. final status
2. top-level commit hash
3. nested simulator commit hash if any
4. review pack path
5. selected workload
6. implementation mode
7. modified source files
8. shadow VM key stats
9. behavior validation result
10. A22C readiness classification
11. A23A timing decision
12. key report paths A20A through A23B
13. final git status --short for both repos
14. clear statement that A20-A23 are shadow VM substrate only, not LATPC mechanism implementation
