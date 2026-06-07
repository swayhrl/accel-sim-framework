# A24E LATPC closeout review pack and handoff

## Round name

A24E_LATPC_CLOSEOUT_REVIEW_PACK_AND_HANDOFF

## Purpose

A24E closes A24 by producing a complete review pack, final reports, and a handoff for A25.

A24E must make A24 reviewable:
- Complete source patch material is included.
- Current full latpc_shadow_vm.h source is included.
- Hook exactness and limitations are explicit.
- Derived detector-ready stats and sample dump are included.
- Trace availability is summarized.
- Behavior equivalence is proven.

Do not implement Regularity Detector, LATC, LATP, prefetching, MSHR compression, or timing integration in A24E.

## Required final summary

Write:
  .local_reports/A24E_latpc_shadow_vm_hardening_final_summary_<timestamp>.md

Required sections:
1. Final status
2. Top-level commit
3. Nested simulator commit
4. Source files changed
5. Scripts changed
6. Reports produced
7. Review pack path
8. Hook exactness summary
   - address mode
   - sm_id mode
   - cycle mode
   - exact fields
   - approximate fields
   - deferred fields
9. Detector-ready stats summary
10. Sample dump summary
11. Trace availability summary
12. Behavior equivalence summary
13. Sensitivity sanity summary
14. Limitations
15. A25 readiness
16. Things not implemented

The final summary must explicitly say:
- A24 does not implement LATPC Regularity Detector.
- A24 does not implement LATC.
- A24 does not implement LATP.
- A24 does not integrate timing behavior.
- A24 does not reproduce IPC speedup.
- A24 output should be called detector-ready shadow analysis substrate, not faithful LATPC reproduction.

## Required review pack contents

Create:
  review_packs/A24_LATPC_SHADOW_VM_HARDENING_AND_DETECTOR_READINESS_review_pack_<timestamp>.tar.gz

The tarball must include, under a clean internal directory:
- A24A reports from .local_reports
- A24B reports and derived CSV from .local_reports
- A24C trace availability CSV and ranking from .local_reports
- A24D behavior equivalence CSV/report from .local_reports
- A24E final summary
- Current full source copy:
  gpu-simulator/gpgpu-sim/src/gpgpu-sim/latpc_shadow_vm.h
- Current relevant source snapshots if changed:
  gpu-simulator/gpgpu-sim/src/abstract_hardware_model.cc
  gpu-simulator/gpgpu-sim/src/gpgpu-sim/gpu-sim.cc
- Nested simulator patch:
  git -C gpu-simulator/gpgpu-sim show --stat --patch --find-renames HEAD
- Top-level patch:
  git show --stat --patch --find-renames HEAD
- A24 guidance docs:
  docs/accelsim_bringup/A24A_LATPC_SOURCE_PATCH_AND_HOOK_EXACTNESS.md
  docs/accelsim_bringup/A24B_LATPC_DETECTOR_READY_STATS_AND_SAMPLE_DUMP.md
  docs/accelsim_bringup/A24C_LATPC_TRACE_AVAILABILITY_AND_SMALL_PROBE.md
  docs/accelsim_bringup/A24D_LATPC_BEHAVIOR_EQUIV_AND_SENSITIVITY.md
  docs/accelsim_bringup/A24E_LATPC_CLOSEOUT_REVIEW_PACK_AND_HANDOFF.md
- A manifest:
  A24_review_pack_manifest.txt

If HEAD is not the relevant nested commit because source changes were split across multiple A24 commits, include:
  git -C gpu-simulator/gpgpu-sim log --oneline -n 10
  git -C gpu-simulator/gpgpu-sim diff <A23_nested_commit>..HEAD --stat --patch

A23 nested commit reference:
  bd1f1f0b3bf5994b93623114e8767473eedb8424

## Review pack completeness verification

After creating the tarball, run:
  tar -tzf review_packs/A24_LATPC_SHADOW_VM_HARDENING_AND_DETECTOR_READINESS_review_pack_<timestamp>.tar.gz > .local_reports/A24E_review_pack_contents_<timestamp>.txt

Verify the contents list includes:
- latpc_shadow_vm.h
- nested patch file
- top-level patch file
- final summary
- behavior equivalence CSV
- derived stats CSV
- trace availability CSV
- sample dump or sample dump manifest
- hook exactness audit

Write:
  .local_reports/A24E_review_pack_verification_<timestamp>.md

If any required item is missing, fix the pack before declaring PASS.

## Commit rules

Before final pack:
1. Check nested repo:
   git -C gpu-simulator/gpgpu-sim status --short

2. If simulator source has changes, commit in nested repo with explicit paths:
   cd gpu-simulator/gpgpu-sim
   git add src/gpgpu-sim/latpc_shadow_vm.h src/abstract_hardware_model.cc src/gpgpu-sim/gpu-sim.cc
   git commit -m "feat(latpc): harden shadow VM detector readiness"
   cd /workspace/repos/accel-sim-framework

3. Check top-level repo:
   git status --short

4. If top-level scripts/docs changed, commit explicit paths only. Example:
   git add docs/accelsim_bringup/A24A_LATPC_SOURCE_PATCH_AND_HOOK_EXACTNESS.md
   git add docs/accelsim_bringup/A24B_LATPC_DETECTOR_READY_STATS_AND_SAMPLE_DUMP.md
   git add docs/accelsim_bringup/A24C_LATPC_TRACE_AVAILABILITY_AND_SMALL_PROBE.md
   git add docs/accelsim_bringup/A24D_LATPC_BEHAVIOR_EQUIV_AND_SENSITIVITY.md
   git add docs/accelsim_bringup/A24E_LATPC_CLOSEOUT_REVIEW_PACK_AND_HANDOFF.md
   git add docs/accelsim_bringup/A24_LATPC_CODEX_SHORT_PROMPT.md
   git add scripts/accelsim/a24_latpc_derive_detector_ready_stats.py
   git add scripts/accelsim/a24_latpc_trace_availability_probe.py
   git commit -m "docs-tools(accelsim): close A24 LATPC shadow VM hardening"

Only add files that actually exist and are intended for git.

Never use git add . or git add -A.
Never push.
Do not commit .local_reports, .local_logs, .local_runs, .local_traces, review_packs, traces, or build outputs.

## Final response format to user

Use this structure:

A24 completed with status: PASS or PARTIAL or FAIL

Nested simulator commit:
  <hash or none>

Top-level commit:
  <hash or none>

Review pack:
  review_packs/<name>.tar.gz

What changed:
- hook exactness:
  - address:
  - sm_id:
  - cycle:
- detector-ready stats:
- sample dump:
- trace availability:
- behavior equivalence:

Key metrics:
- cycles:
- instructions:
- IPC:
- L2 accesses:
- L2 misses:

Limitations:
- still shadow model
- no Regularity Detector
- no LATC
- no LATP
- no timing integration
- no speedup reproduction
- PWC status if still deferred
- NW page divergence limitation if still true

A25 recommendation:
  Proceed to A25 Regularity Detector over shadow VM only after reviewing A24 pack.

## A24E completion checklist

- Final summary exists.
- Review pack exists.
- Review pack contents list exists.
- Review pack includes full latpc_shadow_vm.h.
- Review pack includes nested patch.
- Review pack includes top-level patch.
- Hook exactness report is included.
- Derived stats CSV is included.
- Sample dump or manifest is included.
- Trace availability CSV is included.
- Behavior equivalence report is included.
- Top-level and nested git status are clean except ignored runtime artifacts.
- Final response does not overclaim LATPC implementation or speedup.
