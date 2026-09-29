# Source anchors

The exact accepted path and R101R4 insertion boundaries are recorded in
`SOURCE_PATH_MAP.md`.  The reproducible source deltas are the generated
`P0_CORE.patch` and `P1_CORE.patch`; applying each patch to its stated frozen
runtime parent reconstructs the corresponding simulator core source.

## P0 anchors

- `src/gpgpu-sim/shader.cc`: post-translation/pre-L1 admission, scheduled and
  ready transitions, response arbitration, terminal drain and counters.
- `src/gpgpu-sim/shader.h`: per-LD/ST finite queues and service state.
- `src/gpgpu-sim/awma_r101r4_local_service.h`: fixed 1/16 policy/accounting
  definitions used by directed tests and the simulator integration.

## P1 anchors

- `src/gpgpu-sim/gpu-cache.cc`: lower-request dequeue interception only after
  normal L1 miss/MSHR state exists and only when the cache level is exactly
  `L1_GPU_CACHE`.
- `src/gpgpu-sim/shader.cc`: bounded local scheduling and re-entry through
  `ldst_unit::fill`, followed by the unchanged L1 fill/MSHR-ready path.
- `src/gpgpu-sim/shader.h`: P1 per-LD/ST state and global cache-to-LDST routing.
- `src/abstract_hardware_model.h` and `src/cuda-sim/memory.cc`: opt-in request
  identity markers carried on the original access and `mem_fetch` objects.

Neither patch changes the committed scientific parent directly.  Both arms
were built in isolated runtimes, are default OFF, and are selected only by
`AWMA_R101R4_SERVICE_MODE` with diagnostics independently controlled by
`AWMA_R101R4_DIAGNOSTICS`.
