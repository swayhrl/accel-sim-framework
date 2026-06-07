# A24C LATPC trace availability and small stats probe

## Round name

A24C_LATPC_TRACE_AVAILABILITY_AND_SMALL_PROBE

## Purpose

A24C checks whether more LATPC-relevant workloads are already available in the current Accel-Sim environment.

NW remains the anchor workload, but A20-A23 showed NW has weak page divergence. A24C should find whether traces exist for workloads likely to provide stronger TLB/page divergence signals.

Do not run a full benchmark campaign.
Do not generate new traces.
Do not invoke NVBit tracer if there is no GPU.
Do not claim paper-level workload coverage.

## Candidate workloads

Always include:
- nw
- lud
- backprop
- bfs
- rodinia-bfs
- atax
- bicg
- mvt
- 2mm

Optional extra candidates if easy to scan:
- sssp
- pagerank
- cfd
- hotspot
- pathfinder
- gaussian
- streamcluster

The main priority after NW:
1. lud
2. backprop
3. bfs or rodinia-bfs
4. atax
5. bicg
6. mvt
7. 2mm

## Implementation task 1: trace availability scanner

Add a script, preferably:
  scripts/accelsim/a24_latpc_trace_availability_probe.py

The script should scan likely trace and run directories without assuming one fixed layout.

Likely roots:
- .local_traces
- .local_runs
- traces
- util/tracer_nvbit/traces
- gpu-simulator/gpgpu-sim/traces
- any existing paths referenced by A11-A16 scripts or lockfiles

Use bounded search. Avoid recursively scanning huge build directories without limits.

Output:
  .local_reports/A24C_latpc_trace_availability_<timestamp>.csv

Required CSV columns:
- workload
- aliases
- found
- candidate_path
- path_type
- size_bytes
- file_count
- has_config
- has_trace_files
- last_modified
- probe_eligible
- notes

The scanner should not fail if no traces are found. It should write found=false rows with notes.

## Implementation task 2: use existing A13/A16/A20 runner when possible

Inspect scripts/accelsim and docs/accelsim_bringup for existing runner scripts.

If an existing runner supports a workload and variant:
- run only a small stats probe
- use shadow VM enabled
- do not run full campaign
- write logs under .local_logs
- write summary under .local_reports

If no runner supports a workload:
- record probe_status=NO_RUNNER
- do not invent a fragile one-off full campaign

If trace exists but run fails:
- record probe_status=RUN_FAILED
- include short blocker
- keep going with other candidates

If trace does not exist:
- record probe_status=TRACE_MISSING

## Implementation task 3: small stats probe matrix

Create:
  .local_reports/A24C_latpc_small_probe_matrix_<timestamp>.csv

Columns:
- workload
- selected_path
- variant
- env_shadow_vm
- env_sample_dump
- run_command
- status
- log_path
- stats_path
- cycles
- instructions
- IPC
- L2_accesses
- L2_misses
- latpc_vm_warp_mem_inst_observed
- latpc_vm_translation_request_total
- latpc_tlb_l1_miss_total
- latpc_ptw_request_total
- page_div_bin_1
- page_div_bin_2_3
- page_div_bin_4_7
- page_div_bin_8_15
- page_div_bin_16_31
- page_div_bin_32
- limitation

At minimum, NW should be probed if the existing pipeline is still functional.

For non-NW workloads, it is acceptable for A24C to report availability only if run commands are not safely discoverable.

## Implementation task 4: workload readiness ranking

Write:
  .local_reports/A24C_latpc_workload_readiness_ranking_<timestamp>.md

Classify each candidate:
- READY_FOR_A25_PROBE
- TRACE_AVAILABLE_RUNNER_UNKNOWN
- TRACE_MISSING
- RUN_FAILED_NEEDS_DEBUG
- SKIPPED_NO_SAFE_COMMAND

Give a short recommendation:
- keep NW as pipeline anchor
- choose the best 1-3 candidates for A25 or A26 stats probes
- do not claim paper coverage if only a subset is available

## Validation

A24C is not required to modify simulator source.

If A24C modifies only top-level scripts:
- run python syntax check:
  python3 -m py_compile scripts/accelsim/a24_latpc_trace_availability_probe.py

If it uses the derived stats script from A24B:
- run it on at least one NW stats log.

## Reports to produce

Write:
- .local_reports/A24C_trace_scanner_report_<timestamp>.md
- .local_reports/A24C_latpc_trace_availability_<timestamp>.csv
- .local_reports/A24C_latpc_small_probe_matrix_<timestamp>.csv
- .local_reports/A24C_latpc_workload_readiness_ranking_<timestamp>.md

Each report must include:
- start time
- end time
- wall seconds
- status
- commands
- output summary
- blocker
- limitations

Long logs go to .local_logs.

## Git rules

If top-level scripts changed:
  git add scripts/accelsim/a24_latpc_trace_availability_probe.py
  git commit -m "tools(accelsim): add LATPC trace availability probe"

Never use git add . or git add -A.
Never push.
Do not commit .local_reports, .local_logs, .local_runs, .local_traces, review_packs, traces, or build outputs.

## A24C completion checklist

- Trace availability CSV exists.
- NW is retained as anchor.
- lud, backprop, bfs or rodinia-bfs, atax, bicg, mvt, and 2mm are checked.
- Small probe is attempted only when safe.
- Missing traces are reported as missing, not treated as failure.
- Workload readiness ranking exists.
- No full benchmark campaign is run.
- No paper-level coverage or speedup claim is made.
