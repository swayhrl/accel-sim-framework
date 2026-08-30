# Source anchors

The following anchors resolve against Core candidate `955a50cbb5e8d928b6c7b0c78e1af062b835df44`.

| Concern | Source anchor | Audit finding |
| --- | --- | --- |
| M1 configuration defaults | `src/gpgpu-sim/gpu-cache.h:577-583,929-941` | M1 policy defaults to static; functional Unified/RO/TVD/adaptive bits default off. |
| Payload namespace and handle | `src/gpgpu-sim/gpu-cache.h:2066-2160` | Defines 1,152-slot global namespace and `{payload_id,generation}` handle. |
| Allocation/free lifecycle | `src/gpgpu-sim/gpu-cache.h:2192-2263` | Static reservation and bypass release preserve generation discipline. |
| Bank identity | `src/gpgpu-sim/gpu-cache.h:2288-2390` | Bank class derives from global payload ID modulo four while legacy service/arbitration remains. |
| Owner/liveness validation | `src/gpgpu-sim/gpu-cache.h:2422-2442` | Valid handle requires matching generation and owner. |
| L2 sidecar and mode gate | `src/gpgpu-sim/gpu-cache.h:2518-2680` | A 1,024-entry tag sidecar tracks payload handle; unsupported modes reject before simulation. |
| Admission and rollback | `src/gpgpu-sim/gpu-cache.cc:2416-2554` | Access reserves the static handle and restores slot/sidecar on WAD/base admission failure. |
| Fill validation | `src/gpgpu-sim/gpu-cache.cc:2578-2596` | Completion requires the matching sidecar handle and owner. |
| Terminal invariant | `src/gpgpu-sim/l2cache.cc:2073-2081` | End-of-run check includes no-resource-leak / sidecar consistency. |
| Parser binding | `src/gpgpu-sim/gpu-sim.cc:272-286` | Registers substrate policy and feature configuration controls. |
