# C14 changed-files and provenance receipt

## Framework branch

Branch: `hrl/vm-m4b-c14-dual-path-explore-v0`.

- `configs/vm_tlb/c14_dual_path/C14_P_EXACT320_SEGMENT_N8_L10.config`
- `configs/vm_tlb/c14_dual_path/C14_N_F0_EXACT768_NO_SEGMENT.config`
- `configs/vm_tlb/c14_dual_path/C14_N_F7_L5_EXACT320_SEGMENT_N8.config`
- `util/vm_tlb/run_c14_microdiagnostic.sh`
- `docs/vm_tlb/review_packs/M4B_SPECULATIVE_DEVELOPMENT/C14_DUAL_PATH_EXPLORATION/*`
- `docs/vm_tlb/codex_handoff/c14_dual_path/LATEST_REPORT.md` (final handoff)

Framework commits before final synthesis:
`4922618a`, `825e33be`, `d625bcab`, `89be98b1`, and `8bc99ec2`.
The branch began at the required Framework baseline
`c534fbd4fd33f0a4f6c0e128ca569bc309f85cee`.

## Path P Core branch

Branch: `hrl/vm-m4b-c14-segment-positive-v0`, based at the required C12 Core
`57bb71ecd015b6ec0ab32e45b0815e5beaf69172`; C14 commit `ce05732b`.

- `src/gpgpu-sim/gpu-sim.cc`
- `src/gpgpu-sim/shader.h`
- `src/gpgpu-sim/vm_translation.cc`
- `src/gpgpu-sim/vm_translation.h`
- `tests/vm_c14_segment_race_telemetry_test.cc`

## Path N Core branch

Branch: `hrl/vm-m4b-c14-criticality-v0`, based at the required C12 Core
`57bb71ecd015b6ec0ab32e45b0815e5beaf69172`; C14 commit `290bf7b7`.

- `src/abstract_hardware_model.cc`, `src/abstract_hardware_model.h`
- `src/gpgpu-sim/gpu-sim.cc`
- `src/gpgpu-sim/memory_telemetry.cc`, `src/gpgpu-sim/memory_telemetry.h`
- `src/gpgpu-sim/shader.cc`, `src/gpgpu-sim/shader.h`
- `src/gpgpu-sim/vm_translation.cc`, `src/gpgpu-sim/vm_translation.h`
- `tests/vm_c14_criticality_telemetry_test.cc`

Both Core branches passed their direct telemetry unit test and
`make -j4 gpgpu-sim_uarch`; the Framework simulator build and the exercised
runtime receipts also passed.  `git diff --check` passed before their Core
commits.

## Deliberately unchanged

C13's worktree, branch, raw outputs, and review pack were never modified.
C14 only ran read-only `git fetch` on its remote branch at permitted phase
boundaries.  No new full-ROI matrix was started.
