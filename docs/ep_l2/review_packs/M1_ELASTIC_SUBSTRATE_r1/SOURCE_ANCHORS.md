# Source anchors

All line numbers refer to Core commit `955a50cbb5e8d928b6c7b0c78e1af062b835df44`.

| Concern | Anchor | M1 relevance |
|---|---|---|
| Static/default mode fields | `src/gpgpu-sim/gpu-cache.h:577-583, 929-941` | Functional bits default OFF and M1 policy defaults to static. |
| Global namespace + handle | `src/gpgpu-sim/gpu-cache.h:2066-2160` | 1152 slots; handle is `{payload_id,generation}`. |
| Static allocation/lifecycle | `src/gpgpu-sim/gpu-cache.h:2192-2263` | Resident `i`, bypass `1024+j`, pending-sector and generation rules. |
| Bank mapping/arbitration | `src/gpgpu-sim/gpu-cache.h:2288-2390` | Bank derives from global ID modulo 4; legacy arbiter algorithm retained. |
| Ownership invariant | `src/gpgpu-sim/gpu-cache.h:2422-2442` | Role/range/status and one resident owner checks. |
| Sidecar/config gate | `src/gpgpu-sim/gpu-cache.h:2518-2680` | 1024-handle sidecar plus static-only fail-closed gate. |
| Access reserve/rollback | `src/gpgpu-sim/gpu-cache.cc:2416-2554` | Sidecar is saved/restored with speculative resident reservation. |
| Fill validation | `src/gpgpu-sim/gpu-cache.cc:2578-2596` | Response validates ID, generation, sidecar and owner before completion. |
| Terminal invariant | `src/gpgpu-sim/l2cache.cc:2073-2081` | Drain/no-leak additionally requires sidecar consistency. |
| Option parsing | `src/gpgpu-sim/gpu-sim.cc:272-286` | Policy and future functional bits are parseable, default OFF. |
| Direct tests | `tests/ep_l2/test_payload_store.cc`, `test_payload_sector_lifetime.cc`, `test_payload_banked.cc`, `test_descriptor_mshr_integrated.cc` | Mapping, generations, bank replay, production lifecycle. |
