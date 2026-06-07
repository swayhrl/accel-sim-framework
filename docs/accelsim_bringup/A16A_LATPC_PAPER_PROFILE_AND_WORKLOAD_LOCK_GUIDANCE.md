# A16A LATPC paper profile and workload lock guidance

## Goal

Create a LATPC paper profile and select one existing trace-available workload for A16.

A16A must not run a large benchmark campaign. It should only inspect the paper, existing traces, existing A11-A15 outputs, and lockfiles.

## Inputs

Paper:

docs/accelsim_bringup/paper/2025_MICRO_LATPC_TLB_Prefetch_MSHR.pdf

Useful prior outputs, if present:

.local_reports/A12_workload_config_lock_*.csv
.local_reports/A13_experiment_matrix_*.csv
.local_reports/A13_experiment_results_*.csv
.local_reports/A14_mini_result_table_*.csv
.local_reports/A11_stats_equivalence_matrix_*.csv

Trace candidates may exist under:

.local_traces/
hw_run/
any existing Accel-Sim trace location referenced by prior matrix or lockfiles

## Paper facts to encode

From the LATPC paper, encode at least these facts manually in a small table or dict in the script. Do not depend entirely on PDF parsing.

Important workload candidates:

paper_workload, abbreviation, class, suite_hint, priority
nw, NW, Regular+High, Rodinia, 1
lud, LUD, Regular+High, Rodinia, 2
backprop, BP, Regular+Low, Rodinia, 3
rodinia-bfs, BFR, Irregular, Rodinia, 4
bfs, BFR, Irregular, Rodinia alias, 5

Other LATPC paper workload names may be recorded as non-primary candidates, but do not select them unless their traces already exist.

Important configuration facts to record:

- 4 KB pages are the default evaluation mode except large-page sensitivity.
- Baseline has no TLB prefetching.
- LATPC consists of LATP and LATC.
- A16 does not implement LATP or LATC.

## Required implementation

Create or update a script under scripts/accelsim, recommended name:

scripts/accelsim/a16_latpc_paper_profile.py

The script should:

1. Record start time, end time, and wall seconds.
2. Check that the paper PDF exists.
3. Try to extract paper text into .local_reports, using pdftotext if available.
4. If pdftotext is unavailable, continue with the manual paper facts above and mark pdf_text_extract=skipped.
5. Discover prior A12/A13/A14 files.
6. Discover candidate trace or kernelslist paths by inspecting:
   - prior lockfiles
   - prior experiment matrix
   - prior smoke scripts or reports
   - existing trace directories
7. Normalize workload names using simple aliases:
   - nw, needle, needleman-wunsch -> nw
   - lud -> lud
   - backprop, bp -> backprop
   - bfs, rodinia-bfs, bfr -> bfs
8. Select the first available workload using this priority:
   - nw
   - lud
   - backprop
   - bfs
9. Write a candidate CSV with all candidates and evidence.
10. Write a selected workload JSON.
11. Write a paper profile MD.

## Required output files

Use timestamp format YYYYMMDD_HHMMSS.

Required outputs:

.local_reports/A16A_latpc_paper_profile_<timestamp>.md
.local_reports/A16A_latpc_workload_candidates_<timestamp>.csv
.local_reports/A16A_latpc_selected_workload_<timestamp>.json

Optional output:

.local_reports/A16A_latpc_paper_text_<timestamp>.txt

## Candidate CSV columns

Include at least:

- paper
- paper_workload
- normalized_workload
- abbreviation
- workload_class
- suite_hint
- priority
- trace_available
- kernelslist_path
- config_path
- evidence_source
- evidence_count
- selected
- notes

## Selected workload JSON fields

Include at least:

- paper
- round
- selected_workload
- paper_workload
- abbreviation
- workload_class
- suite_hint
- kernelslist_path
- config_path
- selection_reason
- fallback_used
- timestamp
- status

## A16A status rules

PASS:

- paper PDF exists
- at least one preferred candidate has trace or kernelslist evidence
- selected workload JSON exists and status is PASS

BLOCKED_NO_PDF:

- paper PDF missing

BLOCKED_NO_TRACE:

- paper PDF exists, but no candidate trace or kernelslist path can be found

PASS_WITH_WARNINGS:

- paper PDF exists
- trace exists
- text extraction failed or partial, but manual facts are encoded and reports are complete

## Validation commands

Run:

python3 scripts/accelsim/a16_latpc_paper_profile.py

Then inspect:

ls -lh .local_reports/A16A_latpc_* | tail
cat latest A16A paper profile summary
cat latest selected workload JSON

## Important notes

Do not invent trace availability.

Do not select ATX just because it is prominent in the paper. Select only trace-available workloads.

Do not claim that A16 selected workload reproduces a LATPC result. It only gives a trace-available paper-specific anchor for the no-op variant pipeline.
