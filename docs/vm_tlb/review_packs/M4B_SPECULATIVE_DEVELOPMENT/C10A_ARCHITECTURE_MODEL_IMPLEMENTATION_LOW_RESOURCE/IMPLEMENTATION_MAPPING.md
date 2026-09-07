# C9 requirement to C10-A implementation mapping

| C9/C10-A requirement | C10-A realization | Status |
| --- | --- | --- |
| real VA-to-PA Segment mapping | V2 `pa_base_ppn + (vpn-va_base_vpn)` and test VPN 16 -> PPN 256 | IMPLEMENTED_STATIC_UNRUN |
| object map telemetry only | `service_lookups()` uses descriptor registration, never `OBJECT_WEIGHT`, for eligibility | IMPLEMENTED_STATIC_UNRUN |
| ordinary paging agrees for registered page | `complete_translation()` calls `registered_ppn()` before the generic backend | IMPLEMENTED_STATIC_UNRUN |
| one immutable N=8 table per cluster | canonical V2 map copied to every existing L1/SID cluster; V2 parser caps eight descriptors | IMPLEMENTED_STATIC_UNRUN |
| one local acceptance per cycle | Segment acceptance locksteps with existing one-port L1 admission; denial is counted on L1-port denial | IMPLEMENTED_STATIC_UNRUN |
| HIT_FIRST / MISS_JOIN | explicit terminal owner branches precede L2 launch; neither lone miss proceeds lower | IMPLEMENTED_STATIC_UNRUN |
| no Weight TLB fill after Segment hit | Segment winner sets `LOOKUP_READY`; lower fill path is not entered | IMPLEMENTED_STATIC_UNRUN |
| 5/10/20 points | generic `segment_config.lookup_latency` remains parameterized; F7/F8 manifest contract lists `5|10|20` | CONTRACT_ONLY |
| G96/F1 and G32/F8 | `tlb_config(96,16)` derives 6 sets; `(32,16)` derives 2; test asserts both | IMPLEMENTED_STATIC_UNRUN |
| leaf invalidation / empty group release | `invalidate`, `flush_asid`, `flush_all`; test covers sibling and empty-group release | IMPLEMENTED_STATIC_UNRUN |
| generation-race stale fill | no captured generation in in-flight sub-entry fill | DEFERRED_C10B |
| privileged install/revoke acknowledgement | V2 artifact is driver-owned in schema, but no runtime install/revoke state machine | DEFERRED_C10B |
| F0--F9 executable metadata | immutable TSV plus static validator | CONTRACT_ONLY |
| physical F5 PWC | deliberately not represented by legacy PWC | DEFERRED_C10B_BLOCKER |

`IMPLEMENTED_STATIC_UNRUN` means source and focused test cases were added and
static-checked, but post-delta binary build/link/execution was prohibited by
the low-resource gate. It is not a runtime validation result.
