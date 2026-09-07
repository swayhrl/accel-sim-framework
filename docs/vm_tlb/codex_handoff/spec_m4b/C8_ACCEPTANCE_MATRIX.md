# C8 Acceptance Matrix

Goal：`C8_HARDWARE_COST_AND_MODEL_RISK_AUDIT`

| ID | Acceptance criterion | Required evidence |
| --- | --- | --- |
| C8-A1 | Analysis-only | No simulator, build, new trace, C5 replay, full large-trace scan |
| C8-A2 | Core frozen | `swayhrl/gpgpu-sim@c21137bc...` unchanged; no Core functional commit |
| C8-A3 | Isolation | Window A/B worktrees, processes and scratch untouched |
| C8-A4 | Provenance | C1/C3/C4/C7 docs and Core SHA bound explicitly |
| C8-A5 | Weight descriptor audit | Required fields, storage formula, missing ASID/PA/protection/lifecycle state identified |
| C8-A6 | Lookup topology audit | Comparator/table/placement/port/throughput/latency alternatives assessed |
| C8-A7 | Parallel-L1 contract | L1-hit penalty, Segment throughput, queue/backpressure/replication risks audited |
| C8-A8 | Mapping correctness | identity-like VA→PA shortcut explicitly assessed; migration/remap/UVM implications covered |
| C8-A9 | Context lifecycle | ASID, context switch, install/remove, invalidation, model load/unload addressed |
| C8-A10 | Classification provenance | Real hardware/software mechanism for Weight identification separated from simulator object map |
| C8-A11 | Scalability | Descriptor scaling at 1/4/16/64 entries analyzed symbolically |
| C8-A12 | Sub-entry storage | Exact-page vs group/leaf hardware state accounted fairly |
| C8-A13 | Sub-entry lookup | base-tag/leaf/fill/replacement/invalidation/superpage complexity audited |
| C8-A14 | Fair-budget comparison | Baseline, larger L2 TLB, larger PWC, 2MiB, Sub-entry, Segment, combined compared |
| C8-A15 | No fake PPA | No unsupported absolute area/power/timing claims |
| C8-A16 | Risk register | Every major assumption classified and tied to result impact/minimum fix |
| C8-A17 | C5 precondition | Exactly one allowed C5 gate conclusion selected |
| C8-A18 | No execution | C8 does not start C5 or modify candidate implementation |
| C8-A19 | Deliverables | Required review pack complete and internally consistent |
| C8-A20 | Closeout | Commit/push then STOP for independent review |

Hard FAIL conditions: violation of A1/A2/A3/A18, silently treating simulator-only identity mapping/object labels as hardware facts, or reporting unsupported PPA numbers.