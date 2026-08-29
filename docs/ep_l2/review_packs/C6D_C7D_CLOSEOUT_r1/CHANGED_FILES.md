# Changed files and semantic purpose

## Core diffstat (`0cde3333..88e243e8`)

`5 files changed, 668 insertions(+), 49 deletions(-)`

| File | Semantic purpose |
| --- | --- |
| `src/gpgpu-sim/gpu-cache.cc` | Exact cache admission/WAD/payload observations and descriptor sampling. |
| `src/gpgpu-sim/gpu-cache.h` | C7d observation state, source-of-truth accessors, and L1 helper. |
| `src/gpgpu-sim/l2cache.cc` | EPL2B0V1 emission, lower-path samples, kernel deltas, 5K windows. |
| `src/gpgpu-sim/l2cache.h` | Accumulator and snapshot schemas. |
| `tests/ep_l2/test_epl2_schema.cc` | Schema regression coverage. |

## Framework diffstat (`0a0c0fc3..2aef9fad`)

`6 files changed, 153 insertions(+), 25 deletions(-)`

| File | Semantic purpose |
| --- | --- |
| `util/ep_l2/parse_epl2_b0.py` | Preserve new explicitly named fields and window records. |
| `util/ep_l2/analyze_target_baseline.py` | Analyze only measured meanings; preserve unavailable fields. |
| `util/ep_l2/run_target_baseline.py` | Isolated Core SHA pinning. |
| `util/ep_l2/tests/test_parse_epl2_b0.py` | Parser regression. |
| `docs/ep_l2/C7D_SCHEMA.md` | Producer/parser contract. |
| `docs/ep_l2/C7D_TELEMETRY_SOURCE_MAP.md` | Production-source navigation and availability caveats. |

No cache behavior, replacement policy, capacity, payload-banking timing, L1
configuration, queue capacity, DRAM timing/scheduler, Unified, RO, or TVD
mechanism is changed by the C7d diff. Full textual patches are intentionally
omitted: the GitHub commit views are smaller and more reviewable than a
duplicated patch, and this pack contains the exact commit sequence.
