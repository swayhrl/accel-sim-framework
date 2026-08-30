# Changed files

Core change relative to parent `878f80869ce212e779df20b6421e4dc7f987825d`: 11 files, 328 insertions, 97 deletions.

| Path | Purpose |
| --- | --- |
| `src/gpgpu-sim/gpu-cache.h` | Global payload store, handle, bank identity, sidecar, configuration gate. |
| `src/gpgpu-sim/gpu-cache.cc` | Access, rollback, and fill handle propagation. |
| `src/gpgpu-sim/gpu-sim.cc` | Parser registration. |
| `src/gpgpu-sim/l2cache.cc` | Terminal sidecar/leak invariant. |
| `src/gpgpu-sim/l2cache.h` | Supporting L2 declarations. |
| `tests/ep_l2/test_payload_store.cc` | Namespace, generation, and bypass lifecycle coverage. |
| `tests/ep_l2/test_descriptor_mshr_integrated.cc` | Sidecar lifetime coverage. |
| `tests/ep_l2/run_descriptor_mshr_integrated.sh` | Current CMake result-path support. |
| `tests/ep_l2/run_wad.sh` | Current CMake result-path support. |
| `tests/ep_l2/m1_unsupported_feature.config` | Unsupported functional-mode fixture. |
| `tests/ep_l2/run_m1_mode_switch.sh` | Fail-closed mode-switch test. |

No Framework implementation source file changed for M1. This review-pack publication is documentation only.
