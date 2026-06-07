# A24A LATPC source patch completeness and hook exactness

## Round name

A24A_LATPC_SOURCE_PATCH_AND_HOOK_EXACTNESS

## Purpose

A24A is the first hardening step after A20-A23 shadow VM substrate.

A20-A23 created a behavior-neutral shadow VM/TLB/MSHR/PTW substrate, but there are known limitations:
- The previous review pack did not include a complete copy or complete patch for the newly added latpc_shadow_vm.h.
- The address hook is currently approximate.
- sm_id is currently passed as 0.
- cycle is currently passed as 0.
- The hook observes warp effective addresses, not a full virtual memory translation pipeline.

A24A must harden reviewability and exactness metadata before A25 Regularity Detector.

Do not implement Regularity Detector, LATC, LATP, prefetching, MSHR compression, or timing integration in A24A.

## Repository layout

Top-level repo:
  /workspace/repos/accel-sim-framework

Nested simulator repo:
  /workspace/repos/accel-sim-framework/gpu-simulator/gpgpu-sim

Important source files from A20-A23:
  gpu-simulator/gpgpu-sim/src/gpgpu-sim/latpc_shadow_vm.h
  gpu-simulator/gpgpu-sim/src/abstract_hardware_model.cc
  gpu-simulator/gpgpu-sim/src/gpgpu-sim/gpu-sim.cc

## Required precheck

Run and record in .local_reports/A24A_precheck_report_<timestamp>.md:

1. Top-level status:
   git status --short

2. Nested simulator status:
   git -C gpu-simulator/gpgpu-sim status --short

3. Confirm current commits:
   git rev-parse HEAD
   git -C gpu-simulator/gpgpu-sim rev-parse HEAD

4. Confirm the shadow VM source file exists:
   test -f gpu-simulator/gpgpu-sim/src/gpgpu-sim/latpc_shadow_vm.h

5. Generate a source review snapshot into .local_reports, not into git:
   mkdir -p .local_reports
   cp gpu-simulator/gpgpu-sim/src/gpgpu-sim/latpc_shadow_vm.h .local_reports/A24A_source_snapshot_latpc_shadow_vm.h
   git -C gpu-simulator/gpgpu-sim show --stat --patch --find-renames HEAD > .local_reports/A24A_nested_head_patch.patch || true
   git -C gpu-simulator/gpgpu-sim show --stat --patch --find-renames bd1f1f0b3bf5994b93623114e8767473eedb8424 > .local_reports/A24A_A20_A23_shadow_vm_commit_patch.patch || true

The previous A20-A23 nested commit is expected to be:
  bd1f1f0b3bf5994b93623114e8767473eedb8424

If the exact commit is unavailable locally, do not fail the whole round. Record the limitation and still include the current full source snapshot of latpc_shadow_vm.h.

## Implementation task 1: review pack/source patch completeness foundation

Add or update scripts/reports so that A24E can include complete reviewable source material.

Minimum requirement for A24 review pack:
- Include current full source copy of gpu-simulator/gpgpu-sim/src/gpgpu-sim/latpc_shadow_vm.h.
- Include git show --stat --patch output for the final nested simulator commit after A24 source changes.
- Include git diff or git show output for top-level scripts/docs changed in A24.
- Include a manifest that explicitly says whether latpc_shadow_vm.h is included.

Do not modify old review packs. Fix completeness in the new A24 review pack.

## Implementation task 2: hook exactness audit

Inspect the current call path around:
  warp_inst_t::generate_mem_accesses()
  latpc_shadow_vm_observe_warp_addresses(...)

Find where the hook currently passes:
  sm_id
  warp_id
  pc
  cycle
  address list
  address count

Write .local_reports/A24A_hook_exactness_audit_<timestamp>.md with:
- Exact source file and line/function where the hook is installed.
- Current source of PC.
- Current source of warp id.
- Current source of address list.
- Whether unique VPN sequence is based on lane/thread order or sorted.
- Current sm_id source.
- Current cycle source.
- Whether sm_id is exact, approximate, or unavailable.
- Whether cycle is exact, approximate, or unavailable.
- Whether the address stream is full virtual translation or warp effective address approximation.

## Implementation task 3: try to improve sm_id

Try to pass a real shader/SM id to latpc_shadow_vm_observe_warp_addresses.

Acceptable ways:
- If warp_inst_t already has a shader id or core id field, use it.
- If the generate_mem_accesses call site has access to shader_core_ctx or a similar object with an SM id, pass it safely.
- If there is an existing setter or metadata path for warp_inst_t, use it.
- If this requires invasive refactoring of simulator control flow, do not do it in A24A. Keep sm_id approximate and record the blocker.

Do not change timing or memory coalescing behavior.

Required stats or report fields:
- latpc_hook_sm_id_mode
  - 0 means approximate zero
  - 1 means exact shader id
  - 2 means partially exact or call-site dependent
- latpc_hook_sm_id_nonzero_sample_total
- latpc_hook_sm_id_distinct_observed

If numeric stats are not safe to add in A24A, at least write these values in .local_reports and add the numeric stats in A24B.

## Implementation task 4: try to improve cycle

Try to pass a real simulator cycle to latpc_shadow_vm_observe_warp_addresses.

Possible source, only if safe in the current tree:
  gpu_sim_cycle + gpu_tot_sim_cycle

Do not introduce brittle global dependencies if the source file cannot safely access cycle variables.

If exact cycle cannot be safely obtained:
- Keep the current event-index or zero based approximation.
- Record that latpc_ptw_queue_shadow_stall_cycle_total remains a proxy, not a true cycle stall.

Required stats or report fields:
- latpc_hook_cycle_mode
  - 0 means approximate event index or zero
  - 1 means exact simulator cycle
  - 2 means partially exact or call-site dependent
- latpc_hook_cycle_nonzero_sample_total

Do not use the cycle value to stall the simulator. It is only metadata for shadow stats in A24.

## Implementation task 5: hook source mode metadata

Add or report the address source mode:
- latpc_hook_address_mode = 1 for WARP_EFFECTIVE_ADDRESS_APPROX

Do not claim this is a full virtual address translation path.

## Validation for A24A

Run the minimal build or compile check used in A20-A23.

Then run a small NW baseline and shadow/hardened probe if an existing A16/A20-A23 runner is available.

Required equivalence metrics:
- cycles
- instructions
- IPC
- L2 accesses
- L2 misses

If any behavior metric differs between baseline and shadow/hardened, A24A status is FAIL until fixed or reverted.

## Reports to produce

Write these under .local_reports:
- A24A_precheck_report_<timestamp>.md
- A24A_hook_exactness_audit_<timestamp>.md
- A24A_build_probe_<timestamp>.md
- A24A_behavior_probe_<timestamp>.md
- A24A_source_review_material_manifest_<timestamp>.md

Each report must include:
- start time
- end time
- wall seconds
- status
- commands
- output summary
- blocker
- limitations

Long logs go under .local_logs.

## Git rules

If simulator source is changed:
1. Commit in nested repo first:
   cd gpu-simulator/gpgpu-sim
   git add src/gpgpu-sim/latpc_shadow_vm.h src/abstract_hardware_model.cc src/gpgpu-sim/gpu-sim.cc
   git commit -m "feat(latpc): harden shadow VM hook exactness metadata"

2. Then return to top-level repo.

If only reports are produced, do not commit reports.

Never use:
  git add .
  git add -A

Never push.

Do not commit:
  .local_reports
  .local_logs
  .local_runs
  .local_traces
  review_packs
  traces
  build outputs

## A24A completion checklist

- Current latpc_shadow_vm.h full source snapshot exists in .local_reports.
- Hook exactness audit exists.
- sm_id exactness mode is reported.
- cycle exactness mode is reported.
- address mode is explicitly reported as warp effective address approximation.
- If source changed, nested simulator commit exists.
- Behavior equivalence remains unchanged.
- No LATPC mechanism or speedup claim is made.
