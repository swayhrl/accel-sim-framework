# Source anchors

- `src/gpgpu-sim/shader.cc:2573` admits non-cacheable sidecars; `:2610` closes their existing-path dependency; `:3716-3749` classifies Atomic, Store, and `bypassL1D` before routing only cacheable loads into DTC.
- `shader.cc:3118,3388` retire sidecars; `:4333,4423,5060` use existing completion paths; `:5457-5469` asserts and prints M4 accounting.
- `src/cuda-sim/cuda-sim.cc:1123-1158` maps `.cg` to `CACHE_GLOBAL` and `.nc` to `CACHE_L1`; `abstract_hardware_model.h:1095-1108` defines the same distinction.
- `tests/dtc_l1_m1_common_test.cc:641-704` proves FIFO IO blocking, OO ready-younger retirement, external dependency closure, and no sidecar Tag/physical allocation.
- `src/cuda-sim/ptx.l:110` maps `membar` to `MEMBAR_OP`. No PTX lexer/parser/decode produces `FENCE_OP`; dynamic proxy-fence handling remains at `shader.cc:4463-4471,4958-4979` and rejects regular fences.
