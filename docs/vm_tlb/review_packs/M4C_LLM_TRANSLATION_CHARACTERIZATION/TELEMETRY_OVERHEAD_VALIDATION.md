# M4C Level-2 telemetry behavior and overhead validation

Status: **PASS**.  This gate authorizes `M4C_MEMORY_TELEMETRY_V1` Level 2 for
M4C/M4B formal replays with a fixed window of 1,000,000 L1D transactions.

## Bound inputs

- Framework execution commit: `7125c85e3a48990d4b6317577ea1e43ae4d4a2c8`
- Core execution commit: `0d92e6aa8fd8bc885ffdf081a559bc616aaa85fd`
- ROI/profile: `decode1` / `GENERIC_M3_LLM_BASELINE`
- Trace policy: `COMPUTE_ONLY_TP_PARTITION`
- Immutable semantic list SHA256:
  `b6c42eb1932fcacefc2429b91a2015d38003a764a5319fe4bcbaf65b3d0cd0dc`
- Object-map SHA256:
  `b1dd8745d5a9fd418d03c4bab82627d820c161b6f990f913e6f90583e72e3340`
- Bound selected two-kernel list SHA256:
  `86af2adf62b8e3c05457fb05a4b1972e8ead3866da7a34f5584e2c4aef2f63e5`

The paired, isolated outputs are:

- `/workspace/m4c-telemetry-gate-decode1-v10-level-0`
- `/workspace/m4c-telemetry-gate-decode1-v10-level-2`
- `/workspace/m4c-telemetry-gate-decode1-v10-validation.txt`

## Behavior-neutrality result

Both simulator executions exited normally and consumed the same two immutable
traces.  The validation canonicalizes only telemetry records, the telemetry
configuration line, isolated scratch paths, and host-time-derived rate fields.
It retains execution order, cycles, instructions, IPC, cache/memory/TLB
counters, PTE conservation, and all M4I invariants.

Canonical behavioral-stat SHA256:

`7db7c9eed985b035ad94823f4ea740c7ed2dd77075d87759ab2be8f431fb5e92`

The OFF and ON canonical streams are byte-identical.  Therefore this telemetry
does not alter simulated behavior or request ordering.

## Host/output measurement and frozen choice

| Arm | Wall seconds | RSS KiB | `run.log` bytes |
| --- | ---: | ---: | ---: |
| Level 0 | 5.68 | 196,608 | 198,038 |
| Level 2 | 5.37 | 200,704 | 257,607 |

Level 2 added 59,569 log bytes (30.08%) on this bounded pair.  The small-pilot
wall-clock difference is within normal host noise and is not interpreted as a
speedup.  The bounded output and absence of a measured host-runtime regression
retain Level 2 as the formal default.

Formal runs use ROI/per-kernel/fixed-window aggregate records only.  Level 3
is not enabled, and no unbounded per-access logging is authorized.  The replay
launcher executes inside each run directory, so upstream auxiliary statistics
also remain isolated rather than modifying the Framework checkout.
