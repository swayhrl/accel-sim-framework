# Window C validation contract

Status: **MANDATORY**.

This contract supplements the existing M4B specification for the speculative Window-C lineage. Passing it does not promote results to formal M4B evidence.

## 1. Standard-mode preservation

Before enabling any candidate mode and after each major mechanism change:

- build cleanly;
- pass the accepted M1-M3 directed regression set available in the branch;
- pass object-map/telemetry regression needed by M4C;
- standard L2-TLB mode must remain behavior/counter compatible with the accepted baseline on fixed directed traces;
- no new repeated lookup polling/port consumption;
- no request loss, duplicate waiter wakeup, duplicate store/atomic/data side effect, recursive PTE traffic, or response misassociation.

Any standard-mode regression is a mechanism correctness failure: debug and fix before proceeding.

## 2. Sub-entry directed tests

At minimum:

1. 16 consecutive 64KB VPNs within one aligned 1MB region share one candidate group and all hit after fill under `REFERENCE_APPROX_SUBENTRY_16` or equivalent evidence-backed semantics.
2. VPN 16 crosses to a new group.
3. Base-tag hit + invalid selected subentry is a miss, not a false hit.
4. Filling one subentry preserves valid siblings.
5. Group replacement invalidates all old valid subentries.
6. Any subentry hit updates group recency according to frozen replacement semantics.
7. Candidate capacity/associativity realizes the configured group-entry count/ways.
8. ASID/page-size class remain part of identity.
9. Standard mode remains regression-compatible.
10. One requester launch consumes lookup ports exactly once; retry/pending polling does not reconsume.
11. Fill/eviction/subentry-valid counters conserve.
12. Object metadata does not influence hit match/victim selection/timing.
13. 2MB behavior is either explicitly supported/tested or rejected/kept on standard path according to the frozen candidate contract; never silently mis-handle it.

## 3. Segment descriptor tests

At minimum:

1. first byte/page of descriptor hits;
2. last valid byte/page hits;
3. immediately below base misses;
4. immediately above limit misses;
5. lower page-offset bits preserved;
6. safe non-zero page offset mapping produces expected PA;
7. full-byte-interval boundary crossing falls back to paging;
8. two non-overlapping descriptors match correctly;
9. overlapping descriptors are rejected;
10. table capacity is enforced;
11. descriptor persists across ordinary kernel boundaries.

## 4. Parallel Segment + L1 state-machine tests

At minimum:

1. Segment + L1 launch exactly once for a new requester.
2. Segment hit masks the raw L1 result.
3. Segment hit launches zero L2 TLB lookups.
4. Segment hit allocates/merges zero translation MSHRs.
5. Segment hit launches zero PWQ/walker/PWC/PTE work.
6. Segment hit fills neither conventional L1 nor L2 TLB with the Weight translation.
7. Segment miss reuses the completed L1 result without re-probing L1.
8. Segment miss + L1 hit returns normally without extra serial relookup.
9. Segment miss + L1 miss launches L2 exactly once.
10. Pending/in-flight retries consume neither Segment nor TLB resources again.
11. A new waiter UID gets its own normal one-shot frontend admission.
12. Store/atomic/data side effects remain exact-once.
13. Segmentation disabled is regression-identical to the selected paging candidate.
14. Non-weight-only directed input is behavior-equivalent to paging candidate except explicit segment-miss observability.
15. Segment result and conventional identity-like mapping agree for formal Weight traces under the current resident map.

## 5. Bounded real-trace admission

Before any full speculative candidate run, bounded prefill/decode1 must prove:

- exact trace/list/object-map/segment-map hashes;
- normal exit and intended kernel consumption;
- expected nonzero Weight segment hits;
- zero downstream conventional translation work after Weight segment hits;
- KV/UNKNOWN remain on paging;
- no unexpected Weight range expansion;
- PTE request/response conservation;
- waiter registration/wakeup conservation;
- zero response misassociation;
- object/telemetry conservation;
- translation state quiescence when required;
- standard/paging comparison uses the same platform/trace inputs.

If a real Weight access falls outside the frozen segment, investigate the metadata/range. Do not silently enlarge the segment to catch accesses.

## 6. Full speculative candidate acceptance

A full candidate arm becomes `SPECULATIVE_CANDIDATE` only when:

- all directed/bounded tests remain PASS at the exact Core SHA used;
- normal simulator exit;
- started-kernel markers = intended list count;
- telemetry records = intended list count;
- all VM/segment conservation assertions PASS;
- config/source/binary/runtime/list/object/segment-map hashes are bound;
- no parameter was tuned from desired paper performance numbers.

## 7. Telemetry continuity

M4B candidate runs must preserve the M4C hierarchy observability wherever semantically applicable:

- TLB/MSHR/PWQ/walker/PWC/PTE;
- L1D/L2/DRAM;
- PTE/data L2 contention;
- L2 cache and L2-TLB replacement attribution;
- cross-layer translation × L1D × L2 matrices;
- per-kernel and bounded window summaries.

New segment/subentry counters should be additive or explicitly versioned. Do not remove existing fields merely because a mechanism suppresses conventional traffic; zero/suppressed traffic is itself evidence.

## 8. Hard-stop conditions

Stop C immediately only when continuing would require materially inventing mechanism semantics without authorization, when source/artifact provenance cannot be recovered, when standard-mode correctness cannot be restored, or when there is cross-window contamination / request loss / duplicate side effect / recursive PTE / response misassociation / trace corruption.

Ordinary test failures, build errors, dead code, wrong counters, and first-pass implementation bugs must be debugged and fixed rather than treated as a reason to stop the Goal.
