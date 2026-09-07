# C9 acceptance matrix

Goal: `C9_SEGMENT_SUBENTRY_ARCHITECTURE_DECISION`

C9 is design-only. Any functional Core modification, simulator run, C5 replay, build or full-trace scan is an automatic scope violation.

| ID | Requirement | Mandatory evidence |
|---|---|---|
| C9-A | Input provenance bound | C8 `468fe62d...`, frozen Core `c21137bc...`, paper spec, A checkpoint `73d25ebb...` recorded |
| C9-B | Evidence labels explicit | PAPER_SPEC / EXISTING_MODEL_FACT / USER_APPROVED_DIRECTION / C9_MODEL_DECISION / UNKNOWN used consistently |
| C9-C | Real Segment PA mapping closed | No identity `ppn=vpn`; descriptor supports real contiguous extent mapping or justified equivalent |
| C9-D | Trusted registration closed | Privileged runtime/driver installation, context/permission and overflow/fallback semantics defined |
| C9-E | Segment topology/capacity selected | Placement and nominal descriptor count chosen after N=1/4/8/16/64 analysis |
| C9-F | Parallel ordering selected | Exact L1/Segment hit/miss completion policy defined; ordinary L1 hits not unjustifiably serialized |
| C9-G | Throughput/latency contract selected | Accept rate, queue/backpressure semantics, parameterized latency and sensitivity points defined |
| C9-H | Lifecycle closed | Install/invalidate, pinned epoch or alternative, migration/remap/free/context/ASID reuse semantics defined |
| C9-I | Sub-entry equal-bit accounting | Hardware-relevant state formula complete; old 768-group comparison explicitly not equal-cost |
| C9-J | `G_equal_bit` determined | Concrete G when widths permit, otherwise bounded formula with only explicit unresolved widths |
| C9-K | Fair baseline policy frozen | exact equal-bit, PWC, 2MiB, leaf-capacity diagnostic, Segment and combined candidate rules defined |
| C9-L | Sub-entry lookup/lifecycle closed | tag/leaf hit, fill, replacement, invalidation, ASID/context and superpage scope defined |
| C9-M | A checkpoint used only as motivation | no A/C numeric pooling or parameter tuning; queue/stall implication recorded |
| C9-N | C10 delta bounded | Future implementation requirements and regression/test obligations listed without implementing them |
| C9-O | No heavy work | Core unchanged; no build/sim/C5/trace/PPA; Window A/B untouched |
| C9-P | Unique final decision | exactly READY_FOR_MODEL_IMPLEMENTATION or DECISION_STILL_OPEN |
| C9-Q | Stop boundary | commit/push then STOP; no automatic C10/C5 |

## Hard failure conditions for READY

`ARCHITECTURE_READY_FOR_MODEL_IMPLEMENTATION` is forbidden if any of the following remains open in a way that can materially change performance/correctness:
- Weight VA->PA mapping;
- eligibility/registration authority;
- descriptor table topology/port/queue model;
- L1/Segment completion ordering;
- migration/context/stale-descriptor protocol;
- sub-entry same-budget sizing;
- comparison policy that gives candidate uncharged capacity/state.

UNKNOWN paper details may remain UNKNOWN if C9 makes an explicit project architecture decision rather than mislabeling it as paper-exact.
