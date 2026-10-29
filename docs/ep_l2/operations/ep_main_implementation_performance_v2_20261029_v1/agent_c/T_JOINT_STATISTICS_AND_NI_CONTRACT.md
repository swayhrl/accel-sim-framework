# Minimal T opportunity statistics and NI contract

## What existing code really measures

Source78 `gpu-cache.cc:3047-3075` captures diagnostic rawprobe, targetSet, cache/slice/physicalcycle/requestUID and each target way's kind/live/attached/reuse/required/ready. Ways are read using `index=o.set*assoc+way`: this is an actual same-targetSet state. `ep-l2-tagpressure-diag.h:53-54,73-79,125` computes structural eligible as `live && attached && !reuse && (required & ~ready)` independently of T. Actual `runtime.detachable` and `tx.can_detach` remain T-gated. Therefore **do not conflate absent operational lookup with absent structural observer state**.

The once-callback `gpu-cache.cc:3088-3098` joins this actual snapshot to the same UID/tick's route/admit. TP route_joint retains slice/phase/raw/RESERVED/requester/eligibility/route/admit/early. It drops Set from the aggregated key, but still counts **true joint occurrences computed from the original sameSet snapshot**, not marginal products. Denominator is covered frontend head-cycles after the existing once guard. It is not actual ingress, independent NEW or a time-weighted full-set exposure denominator. Repeated waiting heads in later ticks remain repeated observations.

`NONRO_NATIVE_PATH` is the complement of candidate, not a demand-only access_type. Read/write/WB components are not in the aggregate key; cannot rename this ordinary demand requests or use unmatched FT demand denominator. T0 RO-runtime state is applicable because M1; no S runtime means NOT_APPLICABLE rather than zero.

Existing legacy detach_diag `gpu-cache.cc:3077-3082,3130-3142` only fills its selected predicate/eligible aggregate under T. T0structural data must come from qualified TP, never its zero eligible field. `ep-l2-detach-diag.h:287-298` stores up to64SAMPLEs with UID/Set/victimPayload/generation and immediate_commit_result. The wire explicitly says `trigger_later_linkage=NOT_MEASURED`. Real detach and accepted-after-detach counters exist, plus detached retire closure; they are not the full per-trigger request completion chain.

## Newly proven geometric limitation

Source78 TP observe60/basic_closure96/route_joint118/print307 accepts only32/64sets and8/16ways. `gpu-cache.cc:3066` additionally uses LIFE.supported_geometry, whose helper likewise accepts only those. Thus preferredConv16x8 and backupVector32x4 have **no qualified TP structuraljoint**, even though their model geometries run. HeavyOFF accepted results are not invalidated; turning TPON at these geometries yields invalid observation and must not be silently accepted.

`tagpressure_small_geometry_candidate.patch` adds an exact TP geometry helper with oldpairs plus16x8/32x4; switches the existing snapshot-loop gate to this helper, extends count/printvalidation, and binds a new geometry schemaJSON/hash/wireID. Base64x16 R5schema remains. No model predicate, queue, Tagprobe, lookup scheduling or protocol guard changes. It is not in DSource. Main application changes require a newCore/ELF and all3draft Source5 rebinding. The old emitted source_base_core is historical schema ancestry, not currentSource5 authority; capsule Source5 wins.

Actual header CPU controls and serialization PASS. Capture hook/fullTU, actual accepted raw/parser, and applicationOFF/ON NI remain NOT_QUALIFIED. The reducer keeps the original128MiBdesign bound (phase86032B,joint2097160B,registry186392B). This is **not** a proven <=8MiBnewcollector or <=5%hostoverhead. Existing two-kernel actual allocation and hostcost not measured here.

## Minimum observations and status

| Metric | Existing primary heavyOFF | Qualified TP/DIAG ON candidate |
|---|---|---|
| ordinary rawTagFAIL | MS TAG_SET_PENDING is stage-specific blockedpopulation, not exact demandraw joint | raw RF headcycle joint; NONRO may includeWB |
| sameUID/set/tick structural RO | NOT_COLLECTED | true joint occurrence count, after geometry qualification |
| frontend allow/deny | existing aggregate reasons, differing population | same snapshot route_joint admission |
| actual backend detach | RO aggregate detach | DIAG actualsuccess and commit outcome, no margin inference |
| independentNEW requester count | NOT_COLLECTED | NOT_INSTRUMENTED; TP is headcycle |
| later final acceptance/completion pertrigger | NOT_COLLECTED | NOT_INSTRUMENTED; bounded immediate sample only |
| resource/protocol correctness | existingfullapp invariants plusnewCPU required | same; cannot replace ownership/generation guards by observerpredicate |

## NI and authorization

Every enabled arm needs matching sameELF OFF/ON production CPU semantic comparison after the finalSource is frozen. D CPU pairs do not cover this separate geometry patch automatically. Then3applicationON counterparts to3OFF primary points are conditional minimum for each actual F_MINUS_T/LEGACY_F/CORRECTED_F path; Source, input, all283options and background identical, only two existing diag env switches differ. Require exact semantic outputs and complete request/kernel/drain populations, modeledcycles equal, hostwall/RSS/output measured and declared. Host overhead comparisons need account actual sharedhost load, not just a single noisy ratio.

No Source/ELF change after OFF points may be patched into their NI identity. Neither S NI, oldVector4M F NI nor syntheticC++counter checks grant this new16x8 app NI. On failure retainnegative and stopqualification, no autoretry/refund. This task executed0scientificstarts and asks no automaticbudgetgrant.
