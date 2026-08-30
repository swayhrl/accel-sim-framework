# Changed files

## Core implementation

- `src/gpgpu-sim/gpu-cache.h` — global slot representation, handle API,
  static role mapping, sidecar, static-only configuration gate.
- `src/gpgpu-sim/gpu-cache.cc` — handle propagation through L2 access and fill.
- `src/gpgpu-sim/gpu-sim.cc` — parser entries for static policy and future
  functional mechanism bits.
- `src/gpgpu-sim/l2cache.h`, `src/gpgpu-sim/l2cache.cc` — sidecar observation
  and terminal consistency invariant.

## Test/support changes

- `tests/ep_l2/test_payload_store.cc` — namespace, handle invalidation and
  dormant bypass lifecycle assertions.
- `tests/ep_l2/test_descriptor_mshr_integrated.cc` — production sidecar
  consistency checks before/after drain.
- `tests/ep_l2/m1_unsupported_feature.config`, `run_m1_mode_switch.sh` —
  unsupported future feature configuration must fail closed.
- Existing WAD/integrated test launchers now target the repository's CMake
  release archive layout, without semantic test changes.

No production bypass caller, capacity allocator, cache policy, telemetry schema,
or experiment overlay was added.
