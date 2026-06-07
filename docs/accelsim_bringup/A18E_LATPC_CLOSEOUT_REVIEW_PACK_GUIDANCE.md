# A18E LATPC closeout and review pack guidance

## Goal

Close the A17 plus A18 large round with a final summary, readiness checklist, review pack, explicit git status, and a clean commit.

## Required script

Create:

scripts/accelsim/a18_latpc_closeout.py

## Inputs

Latest reports from:

A17A:
.local_reports/A17A_latpc_*

A17B:
.local_reports/A17B_latpc_*

A17C:
.local_reports/A17C_latpc_*

A17D:
.local_reports/A17D_latpc_*

A18A:
.local_reports/A18A_latpc_*

A18B:
.local_reports/A18B_latpc_*

A18C:
.local_reports/A18C_latpc_*

A18D:
.local_reports/A18D_latpc_*

Tracked guidance docs:

docs/accelsim_bringup/A17*
docs/accelsim_bringup/A18*
docs/accelsim_bringup/A17_A18_LATPC_DESIGN_AND_STATS_MASTER_GUIDANCE.md

Scripts:

scripts/accelsim/a17_latpc_*.py
scripts/accelsim/a18_latpc_*.py

Modified simulator source files, if any, listed by A18B.

## Required output files

.local_reports/A18E_latpc_final_summary_<timestamp>.md
.local_reports/A18E_latpc_readiness_checklist_<timestamp>.csv
.local_reports/A18E_latpc_git_status_<timestamp>.txt
.local_reports/A18E_latpc_git_diffstat_<timestamp>.txt
review_packs/A17_A18_LATPC_DESIGN_STATS_review_pack_<timestamp>.tar.gz

## Final summary required sections

1. Round identity.
2. Starting point from A16.
3. A17A paper requirements result.
4. A17B code localization result.
5. A17C minimal design result.
6. A17D readiness gate result and mode.
7. A18A stats field spec result.
8. A18B instrumentation result.
9. A18C build and run result.
10. A18D validation result.
11. Stats implemented.
12. Stats approximated.
13. Stats unavailable or deferred.
14. Modified tracked files.
15. Modified simulator source files.
16. Review pack path.
17. Final limitations.
18. Recommendation for A19/A20.
19. Clear statement that LATPC mechanisms were not implemented.

## Required limitation statements

Include these statements clearly:

- A17 plus A18 does not implement functional LATPC.
- A17 plus A18 does not reproduce LATPC speedup.
- Any A18 source changes are stats-only and must not alter timing or behavior.
- If only partial instrumentation was possible, list unavailable metrics.
- If no source instrumentation was possible, state that this round is design-only.
- Full paper reproduction still requires A19 plus mechanism implementation rounds.
- No full 24-workload campaign was attempted.
- No NVBit tracing was attempted without GPU.

## Readiness checklist CSV columns

Include:

- item
- status
- evidence_path
- notes

Checklist items:

- paper_pdf_exists
- a16_context_found
- selected_workload_found
- paper_requirements_created
- code_localization_created
- mechanism_design_created
- readiness_gate_created
- stats_field_spec_created
- stats_instrumentation_completed_or_blocked
- build_completed_if_needed
- selected_workload_probe_completed_if_needed
- latpc_stats_extracted_or_unavailable_documented
- behavior_validation_completed
- behavior_unchanged
- final_summary_created
- review_pack_created
- no_runtime_outputs_committed
- git_status_clean_or_explained

## Review pack contents

Include:

- docs/accelsim_bringup/A17*.md
- docs/accelsim_bringup/A18*.md
- docs/accelsim_bringup/A17_A18_LATPC_DESIGN_AND_STATS_MASTER_GUIDANCE.md
- scripts/accelsim/a17_latpc_*.py
- scripts/accelsim/a18_latpc_*.py
- latest .local_reports/A17A*
- latest .local_reports/A17B*
- latest .local_reports/A17C*
- latest .local_reports/A17D*
- latest .local_reports/A18A*
- latest .local_reports/A18B*
- latest .local_reports/A18C*
- latest .local_reports/A18D*
- latest .local_reports/A18E*
- relevant .local_logs/A18C*
- git status and diffstat reports
- a text file listing modified simulator source files

Do not include:

- full trace directories
- build directories
- unrelated old reports
- paper PDF unless already tracked and intentionally included
- review pack inside review pack

## Git handling

After A18E report and review pack are generated, inspect:

git status --short

Then add explicit tracked paths only.

Potential add commands:

git add docs/accelsim_bringup/A17_A18_LATPC_DESIGN_AND_STATS_MASTER_GUIDANCE.md
git add docs/accelsim_bringup/A17A_LATPC_PAPER_REQUIREMENTS_GUIDANCE.md
git add docs/accelsim_bringup/A17B_LATPC_CODE_LOCALIZATION_GUIDANCE.md
git add docs/accelsim_bringup/A17C_LATPC_MINIMAL_MECHANISM_DESIGN_GUIDANCE.md
git add docs/accelsim_bringup/A17D_LATPC_READINESS_GATE_GUIDANCE.md
git add docs/accelsim_bringup/A18A_LATPC_STATS_FIELD_SPEC_GUIDANCE.md
git add docs/accelsim_bringup/A18B_LATPC_STATS_ONLY_INSTRUMENTATION_GUIDANCE.md
git add docs/accelsim_bringup/A18C_LATPC_BUILD_AND_STATS_PROBE_GUIDANCE.md
git add docs/accelsim_bringup/A18D_LATPC_STATS_ONLY_VALIDATION_GUIDANCE.md
git add docs/accelsim_bringup/A18E_LATPC_CLOSEOUT_REVIEW_PACK_GUIDANCE.md
git add scripts/accelsim/a17_latpc_paper_requirements.py
git add scripts/accelsim/a17_latpc_code_locator.py
git add scripts/accelsim/a17_latpc_design_synthesizer.py
git add scripts/accelsim/a17_latpc_readiness_gate.py
git add scripts/accelsim/a18_latpc_stats_field_spec.py
git add scripts/accelsim/a18_latpc_stats_probe_runner.py
git add scripts/accelsim/a18_latpc_validate_stats_only.py
git add scripts/accelsim/a18_latpc_closeout.py

Add modified simulator source files explicitly, based on A18B modified files CSV.

Do not add runtime outputs.

Do not use git add . or git add -A.

Commit message:

scripts: add LATPC localization and stats instrumentation

## Final Codex response requirements

Report:

1. Final status.
2. Commit hash.
3. Review pack path.
4. A17D readiness mode.
5. Selected workload.
6. Whether simulator source was modified.
7. Modified source files.
8. Stats implemented, approximated, unavailable, deferred.
9. Behavior validation result.
10. Key report paths for A17A through A18E.
11. Final git status --short.
12. Clear statement that A17 plus A18 did not implement LATPC functional mechanisms.
