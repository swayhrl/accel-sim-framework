# A24D LATPC behavior equivalence and sensitivity hardening

## Round name

A24D_LATPC_BEHAVIOR_EQUIV_AND_SENSITIVITY

## Purpose

A24D validates that A24A-A24C hardening did not change the original simulator behavior.

Shadow VM, hook exactness metadata, detector-ready stats, and sample dump must remain behavior-neutral.

A24D should also rerun a bounded sensitivity sanity check similar to A22B if the existing scripts support it.

Do not run full benchmark campaign.
Do not claim speedup reproduction.
Do not implement LATPC mechanisms.

## Required behavior equivalence

Compare at least:
- baseline or shadow disabled
- shadow/hardened enabled
- shadow/hardened with sample dump enabled if A24B sample dump exists

Metrics must match:
- cycles
- instructions
- IPC
- L2 accesses
- L2 misses

If any metric differs, status is FAIL unless the source change is reverted or the difference is explained as a parser/reporting bug and fixed.

## Recommended environment modes

Mode 1 baseline:
  ACCELSIM_LATPC_SHADOW_VM unset or 0
  ACCELSIM_LATPC_SAMPLE_DUMP unset or 0

Mode 2 shadow hardened:
  ACCELSIM_LATPC_SHADOW_VM=1
  ACCELSIM_LATPC_SAMPLE_DUMP unset or 0

Mode 3 shadow hardened sample:
  ACCELSIM_LATPC_SHADOW_VM=1
  ACCELSIM_LATPC_SAMPLE_DUMP=1
  ACCELSIM_LATPC_SAMPLE_LIMIT=64

If the existing runner uses variant names rather than env only, adapt to the existing A16-A23 pattern.

## Required output CSV

Write:
  .local_reports/A24D_behavior_equivalence_<timestamp>.csv

Columns:
- workload
- mode
- command
- status
- log_path
- stats_path
- cycles
- instructions
- IPC
- L2_accesses
- L2_misses
- cycles_match_baseline
- instructions_match_baseline
- IPC_match_baseline
- L2_accesses_match_baseline
- L2_misses_match_baseline
- equivalence_status
- limitation

## Required report

Write:
  .local_reports/A24D_behavior_equivalence_report_<timestamp>.md

Include:
- exact commands
- start time
- end time
- wall seconds
- status
- comparison table
- whether sample dump changed behavior
- whether hook sm_id/cycle exactness changed behavior
- blocker
- limitations

## Sensitivity sanity check

If the A22B sensitivity runner or configs are available, rerun a bounded version:
- default TLB
- small TLB
- large TLB

Expected trend from A22B:
- small TLB should generally increase L1 TLB misses or MSHR reservation fails or shadow PTW stalls
- large TLB should not be worse than small TLB
- exact numbers may differ after A24 stats additions, but behavior metrics must stay neutral for baseline vs shadow within each config

Write:
  .local_reports/A24D_sensitivity_sanity_<timestamp>.csv
  .local_reports/A24D_sensitivity_sanity_report_<timestamp>.md

If sensitivity scripts are not safely available, record SKIPPED_NO_SAFE_RUNNER.

## Derived stats validation

Run the A24B derived stats script on at least one A24D shadow stats log.

Validate:
- CSV exists.
- multi_translation_fraction is present.
- avg_unique_stride_count is present.
- same_l4_fraction is present.
- L1 and L2 miss rates are present.
- MSHR fail rate is present.
- PTW request and stall rates are present.
- page divergence fractions are present.
- hook exactness modes are present.

Write:
  .local_reports/A24D_derived_stats_validation_<timestamp>.md

## Build validation

If simulator source changed in A24A or A24B:
- run the smallest build command used successfully in A20-A23
- record build command and result

Do not spend more than 60 minutes in one stage without useful output. If build fails and cannot be fixed with clear local changes, stop that stage and write a blocker report.

## Git rules

A24D should usually not modify source. If it only produces .local_reports and .local_logs, do not commit.

If it fixes scripts, commit explicit script paths only.

Never use git add . or git add -A.
Never push.
Do not commit .local_reports, .local_logs, .local_runs, .local_traces, review_packs, traces, or build outputs.

## A24D completion checklist

- Baseline vs shadow/hardened equivalence CSV exists.
- Metrics cycles, instructions, IPC, L2 accesses, L2 misses match.
- Sample dump behavior neutrality is checked if sample dump exists.
- Derived stats script is validated on real output.
- Sensitivity sanity is run or explicitly skipped with reason.
- No full campaign is run.
- No speedup or faithful LATPC claim is made.
