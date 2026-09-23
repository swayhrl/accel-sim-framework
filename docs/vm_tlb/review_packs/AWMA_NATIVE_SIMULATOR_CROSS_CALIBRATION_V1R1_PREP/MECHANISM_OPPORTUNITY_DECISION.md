# Mechanism opportunity decision

| Trace | Active dependent LDGs | Min | Mean | Max | Cardinality >1 | Histogram |
|---|---:|---:|---:|---:|---:|---|
| M0 | 1024 | 1 | 1.0 | 1 | 0 | `{"1": 1024}` |
| M1 | 1024 | 1 | 1.0 | 1 | 0 | `{"1": 1024}` |
| M2 | 16384 | 1 | 1.0 | 1 | 0 | `{"1": 16384}` |
| M3 | 1024 | 1 | 1.0 | 1 | 0 | `{"1": 1024}` |

Every active dependent `LDG.E` has one active lane and exactly one coalesced accessq entry. The event counts close exactly as `warps × 2 warmup brackets × 512 steps`.

Final classification: `M0_M3_MECHANISM_INACTIVE_CONTROL_SUITE`.

Legacy/V1/V2R1 equality is therefore expected by construction: these traces provide no multi-entry accessq opportunity for pipelined launch or READY consume-and-apply. They cannot validate or invalidate V1/V2R1 Native alignment.
