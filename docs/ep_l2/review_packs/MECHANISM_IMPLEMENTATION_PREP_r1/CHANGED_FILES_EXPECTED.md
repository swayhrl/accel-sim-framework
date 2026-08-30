# Expected Changed Files

These are planned scopes, not current source modifications.

| phase | core files | framework/docs/tests |
|---|---|---|
| M0 | `src/gpgpu-sim/l2cache.h`, `l2cache.cc`; possibly read-only accessors in `gpu-cache.h` | target config switch, parser/schema, focused telemetry tests |
| M1 | `src/gpgpu-sim/gpu-cache.h`, `gpu-cache.cc`, `mem_fetch.h` only if handle naming needs extension, `gpu-sim.cc` for mode/policy parsing | `tests/ep_l2/test_payload_store.cc`, `test_payload_banked.cc`, new lifecycle/equivalence test, config/docs |
| M2 | same M1 core files; `l2cache.cc` only for observation/reporting | shared-pool forward-progress test and review pack parser/docs |
| M3 | `gpu-cache.h/.cc`, potentially `l2cache.cc` and `mem_fetch.h/.cc` only after certified design | RO semantic directed tests and configs |
| M4 | `gpu-cache.h/.cc`, `l2cache.cc`; `mem_fetch.h/.cc` if writeback carries handle | dirty-victim/WAD/TVD tests and storage-accounting docs |

No functional source file is changed by Lane F r1. Documentation-only output resides in this review pack and `docs/ep_l2/codex_handoff/LANE_F_LATEST.md`.
