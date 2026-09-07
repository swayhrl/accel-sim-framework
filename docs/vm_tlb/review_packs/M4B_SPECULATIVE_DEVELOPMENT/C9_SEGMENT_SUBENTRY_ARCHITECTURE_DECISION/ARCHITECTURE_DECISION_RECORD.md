# C9 architecture decision record

## Decision summary

| ID | Decision | Source label | Rationale and closure |
| --- | --- | --- | --- |
| AD-01 | Segment descriptor translates a pinned 64KiB-granular contiguous physical extent using `PA = PA_base + (VA - VA_base)`. | `PAPER_SPEC` + `USER_APPROVED_DIRECTION` + `C9_MODEL_DECISION` | Paper specifies base/limit/offset and physical contiguity; C9 fixes the page-granular v1 form and forbids identity `ppn=vpn`. |
| AD-02 | A non-contiguous Weight allocation is decomposed into non-overlapping physically contiguous descriptors. | `USER_APPROVED_DIRECTION` + `C9_MODEL_DECISION` | No hidden indirect mapping or fabricated hit; failure to fit all extents is an atomic conventional-paging fallback. |
| AD-03 | A privileged runtime/driver, not `OBJECT_WEIGHT`, verifies and installs context-bound descriptors. | `USER_APPROVED_DIRECTION` + `C9_MODEL_DECISION` | Resolves provenance/tenant risk; object map remains telemetry only. |
| AD-04 | v1 table is a replicated local 8-descriptor table per translation cluster for exactly one provisioned ASID. | `PAPER_SPEC` + `USER_APPROVED_DIRECTION` + `C9_MODEL_DECISION` | Paper discusses a small 2--8 model count; local replica matches C4's one local L1 ingress/cycle without a central queue. |
| AD-05 | v1 completion policy is `HIT_FIRST / MISS_JOIN`. | `USER_APPROVED_DIRECTION` + `C9_MODEL_DECISION` | Removes unapproved wait-both L1-hit penalty while preserving a Segment opportunity after L1 miss. |
| AD-06 | `Lseg` is parameterized; 10 cycles is nominal and 5/10/20 are mandatory sensitivity points. | `USER_APPROVED_DIRECTION` + `C9_MODEL_DECISION` | C8 established 10 cycles was only a model point. |
| AD-07 | v1 uses a pinned immutable inference epoch, context ASID and 16-bit descriptor epoch; driver acknowledgements surround install/revoke. | `USER_APPROVED_DIRECTION` + `C9_MODEL_DECISION` | Correctly bounds migration/UVM/remap rather than pretending arbitrary dynamic support. |
| AD-08 | C9 hardware-accounting ABI uses 49-bit VA/PA byte address space, 64KiB base pages, 33-bit VPN/PPN, 16-bit ASID, two leaf PTE attribute bits, and 16-way PLRU. | `C9_MODEL_DECISION` | Explicit parameterized model widths, not paper-exact physical widths or PPA inputs; they make equal-bit comparison reproducible. |
| AD-09 | v1 sub-entry is 64KiB-only, 16 leaves/group, 16-way; standalone `G_equal_bit=96` groups. | `EXISTING_MODEL_FACT` + `C9_MODEL_DECISION` | Retains frozen C1 semantic factor while correcting the historical 768-group budget error. |
| AD-10 | Segment replica bits are charged at GPU scope. Under the base 66,000-bit shared L2 translation-state budget, combined candidate is 32 groups, not 96/768 groups. | `C9_MODEL_DECISION` | Prevents local replica state from being silently free. |
| AD-11 | 2MiB is retained as an explicit homogeneous-page diagnostic/alternative, not silently supported in sub-entry v1. | `EXISTING_MODEL_FACT` + `C9_MODEL_DECISION` | C1 is 64KiB-only; page allocation/promotion caveats stay visible. |

## Rejected alternatives

| Alternative | Status | Reason |
| --- | --- | --- |
| identity `ppn=vpn` Segment hit | Rejected | `EXISTING_MODEL_FACT` shortcut fails real VA→PA and lifecycle requirements. |
| simulator object map decides eligibility | Rejected | telemetry metadata is not a trusted hardware/driver authority. |
| single shared 1-port Segment vector | Rejected for v1 | cannot match 35 local L1 ingress opportunities without queue/backpressure. |
| wait-both L1+Segment | Rejected for v1 | slow/queued Segment serializes otherwise valid L1 hits. |
| nominal `N=1` | Rejected for v1 | contradicts multi-model use and fails requested capacity decision; paper context supports small multi-model count. |
| current 768 groups equals 768 exact entries | Rejected | maximum leaf capacity differs by 16x and state cost differs materially. |
| free Segment descriptor storage in combined comparison | Rejected | makes candidate capacity/state uncharged. |
| 2MiB silently omitted | Rejected | it is a material allocation/page-policy alternative. |

## Explicit unknowns that do not block v1 model implementation

| Unknown | Label | C9 handling |
| --- | --- | --- |
| target paper's exact Segment port/latency/descriptor bit layout | `UNKNOWN` | use documented C9 parameterized model; never call it paper-exact. |
| target physical PA/ASID/permission width | `UNKNOWN` | v1 ABI widths are explicit config defaults and must be reported by C10. |
| paper-exact sub-entry fill/replacement/timing | `UNKNOWN` | retain `REFERENCE_APPROX_SUBENTRY_16`; model C9's concrete 16-way semantics. |
| actual 2MiB allocator/promotion behavior for future workload | `UNKNOWN` | diagnostic has an explicit caveat and requires a separate OS/allocation contract. |
| arbitrary dynamic migration during inference | `UNKNOWN` | not supported in v1; pinned epoch requires revoke before it occurs. |

None of these unknowns changes the selected v1 mapping, registration, topology, completion, lifecycle or
same-budget policy. They must remain labeled if a later result is presented.
