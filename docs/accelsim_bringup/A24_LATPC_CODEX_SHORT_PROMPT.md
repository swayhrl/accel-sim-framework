# A24 LATPC Codex short prompt

Use this prompt after the A24 guidance docs have been committed.

Prompt:

You are working in /workspace/repos/accel-sim-framework on A24_LATPC_SHADOW_VM_HARDENING_AND_DETECTOR_READINESS.

Read and follow these guidance documents in order:
1. docs/accelsim_bringup/A24A_LATPC_SOURCE_PATCH_AND_HOOK_EXACTNESS.md
2. docs/accelsim_bringup/A24B_LATPC_DETECTOR_READY_STATS_AND_SAMPLE_DUMP.md
3. docs/accelsim_bringup/A24C_LATPC_TRACE_AVAILABILITY_AND_SMALL_PROBE.md
4. docs/accelsim_bringup/A24D_LATPC_BEHAVIOR_EQUIV_AND_SENSITIVITY.md
5. docs/accelsim_bringup/A24E_LATPC_CLOSEOUT_REVIEW_PACK_AND_HANDOFF.md

Estimated effort: 120 to 240 minutes. If any single stage runs for more than 60 minutes without useful intermediate output, stop that stage and write a blocker report under .local_reports.

A24 scope:
- Harden the A20-A23 behavior-neutral LATPC shadow VM/TLB/MSHR/PTW substrate.
- Fix review pack/source patch completeness.
- Improve or explicitly report sm_id and cycle hook exactness.
- Add detector-ready derived stats and capped sampled VPN/stride dump.
- Probe trace availability for more LATPC workloads.
- Validate behavior equivalence.
- Produce a complete A24 review pack and A25 handoff.

A24 non-goals:
- Do not implement Regularity Detector.
- Do not implement LATC.
- Do not implement LATP.
- Do not inject prefetches.
- Do not compress MSHRs.
- Do not integrate timing behavior.
- Do not claim IPC speedup or paper reproduction.

Repository rules:
- Top-level repo: /workspace/repos/accel-sim-framework
- Nested simulator repo: /workspace/repos/accel-sim-framework/gpu-simulator/gpgpu-sim
- If simulator source is changed, commit inside nested repo first, then return to top-level.
- Never push.
- Never use git add . or git add -A.
- Do not commit .local_reports, .local_logs, .local_runs, .local_traces, review_packs, traces, build outputs, or generated benchmark outputs.
- Long logs go to .local_logs.
- Reports go to .local_reports.
- Each stage report must include start time, end time, wall seconds, status, commands, output summary, blocker, and limitations.

Required final checklist:
- A24A hook exactness audit exists.
- A24 review material includes full latpc_shadow_vm.h.
- sm_id exactness is exact or explicitly marked approximate.
- cycle exactness is exact or explicitly marked approximate.
- address source is explicitly marked WARP_EFFECTIVE_ADDRESS_APPROX.
- A24B detector-ready derived stats CSV exists.
- A24B sample dump exists or a clear sample dump blocker/manifest exists.
- A24C trace availability CSV checks nw, lud, backprop, bfs or rodinia-bfs, atax, bicg, mvt, and 2mm.
- A24D behavior equivalence confirms cycles, instructions, IPC, L2 accesses, and L2 misses match.
- A24E review pack exists and includes full source snapshots, nested patch, top-level patch, reports, CSVs, and manifest.
- Final response states clearly that A24 is still shadow substrate hardening, not LATPC implementation and not speedup reproduction.

Start by running git status --short in the top-level repo and nested simulator repo, then proceed with A24A.
