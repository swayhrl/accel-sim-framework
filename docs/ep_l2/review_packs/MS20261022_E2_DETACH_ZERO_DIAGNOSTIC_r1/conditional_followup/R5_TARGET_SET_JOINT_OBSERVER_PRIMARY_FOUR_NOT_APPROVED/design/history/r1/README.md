# PASSIVE_OBSERVER r5: target-set pressure/eligibility joint design

Status: design/code draft only. No build, native test or application is authorized or run here. No production tree, binary, registry, qualification, source pin or resource policy was changed. Base is frozen Core9243. Files are an isolated reducer header, integration patch text and explicit schema proposal. They are not a producer release or executable qualification.

The missing measurement is the distribution of reserved ways in the target set **at each actually covered frontend head probe**, including same-line hits. Existing r4 only examines RO victim predicates after raw RESERVATION_FAIL; it cannot say whether reserved occupancy was low, or reached16 while request traffic only hit an existing Tag. r5 must not retrospectively claim it explains any old application.

## Measurement unit and joint structure

One observation is one physical slice frontend head `(cycle,request_uid)` that passes the old r4 deduplication and actually receives its old status-only raw Tag probe. A request that waits100 cycles supplies100 head-cycle observations, not100 unique requests. Read only that snapshot's target set16ways, before preview/admission modifies state. No random sampling or global-cache scan.

All raw statuses are retained, not only FAIL. Derive identity demand with explicit wire labels:

- NEW_TAG_IDENTITY: MISS or RESERVATION_FAIL.
- SAME_LINE_IDENTITY: HIT, HIT_RESERVED or SECTOR_MISS.
- OTHER_NA: MSHR_HIT, WRITE_ALLOCATED, UNKNOWN; never coerce these to new-tag demand.

Wire histograms keep raw status × reservedWays0..16 × eligibleCount0..16. A second exact head histogram keeps raw × reservedWays × five-bit **joint presence** mask: eligible, notAttached, reuseSeen, noMissing, noLive. Bits coexist; reuse and noMissing are not forced into exclusive priority categories. This is an actual same-snapshot joint, never a product of marginal frequencies. Predicate mask `(attached,reuse,missing)` is additionally retained for each live RO way, jointly with raw and reservedWays. Eligibility count is structural (`attached&&!reuse&&missing`); T is explicit per slice so operational eligibility also requires T. Runtime absent makes RO predicates NA.

The presence mask supplies exact head-level eligible/reuse/noMissing overlap. It does not claim the exact **counts** of every reason are mutually joined with eligibleCount; those counts are way observations grouped by raw/reservedWays. This is sufficient to distinguish the requested mechanism cases without storing a combinatorial full set-state signature.

For each snapshot classify all16ways exclusively: any sector RESERVED; otherwise all sectors INVALID; otherwise any MODIFIED (replaceable dirty); otherwise replaceable clean. Reserved includes mixed VALID/RESERVED lines. “Replaceable” describes Tag probe availability, not FT pin, WAD or writeback acceptance. Keep both way-class counts and invalid-way-count distribution at raw/reservedWays. Thus nonreserved16-r is exactly invalid+clean+dirty; no Tag availability category disappears into a generic occupied count.

An exact same-head route/admission histogram adds raw × reservedWays × eligiblePresent × actual production route × actual admit. The routes are production probe not reached, reached/not consulted, consulted/rewrite MISS, consulted/kept FAIL, existing target rewritten HIT_RESERVED, other. A parallel early-reason joint retains owner/directory/query/WAD/TVD outcomes. This prevents a final analysis from discovering eligible candidates but being unable to tell whether the production gate consulted them. These route results are attached at the real frontend callback, not recomputed by the observer.

## Scope and NA

Use the existing r4 `once`, slice binding and phase mapping. TVD/ideal/disabled/other skips retain an explicit skipped reason and NA for raw/set/eligibility. Absent head is an absent-cycle counter only. Runtime-off still permits physical Tag occupancy, but RO eligibility is NA, not zero. T-off permits structural predicate inspection but marks operational relief disabled. No candidate-owner kernel linkage is invented; phase retains UNASSIGNED/OVERLAP_UNKNOWN/SINGLE_ACTIVE_INTERVAL exactly as r4.

Counter reductions must close PHASE→SLICE→GLOBAL across all64 slices. PHASE is the base stored ledger; SLICE/GLOBAL reduce it without an independent counter update path. Empty bins within a covered explicit dimension are zeros; skipped dimensions are NA. Serialization emits independent `EPL2TAGPRESSUREV1|` records. All212 r4 field names, ordering, value semantics, bytes and existing decoder remain unchanged. New consumer is additive and separately source/schema-bound. Same-cycle final snapshots must support an identical cumulative snapshot or false→true epoch closure; no repeat conflict bug.

## Passive code hooks and costs

See `isolated_hooks.patch.txt` for exact current function locations. Main hook is `gpu-cache.cc:2978` detach_diag_snapshot, immediately after its existing raw observer probe, before its rawFAIL/T-only return. That is the only place both the raw result and pre-preview physical state are coherent. Add a pure const sector accessor, then read only the target16 ways and already-readable live transaction diagnostic state. Do not call probe again, invoke capacity predicates, select a victim, modify preview, reserve/model a port, schedule work or charge model cycles.

Doing a global1024-Tag scan per slice/cycle (or all64×1024) answers a different denominator, adds high host overhead and cannot explain the requester target-set decision. It is unnecessary. Cost is ≤16way×4sector reads per already observed head and ≤16read-only RO state checks. The existing r4 probe already walks at most16ways but can return early on matching Tags. Therefore a complete target-set const read is simpler and necessary for those early-return cases; do not instrument only the probe's partial walk.

Current conservative dense arrays in the draft require144,138,240 bytes (~137.46MiB) for64slices×18phases, plus small ledger metadata. Allocate lazily; reserve at least160MiB host RAM in producer resource accounting without reducing existing application RAM/5GiB+2GiB disk guards. No transaction-address log is needed. Additional frame output has64MiB hard ceiling; existing r4 has its separate64MiB ceiling. Combined actual endpoint total remains384MiB. Hitting an observer ceiling marks r5 OUTPUT_INVALID and prevents r5 acceptance; never truncate and call it zero. Sparse nonzero tuple output can reduce actual bytes but must retain explicit dimensions/NA, closure and checked arithmetic. Producer must estimate final text size and avoid assuming first epoch closure is commandlist final. Repeated final printing can be bounded by emitting unchanged r5 snapshots only once, or by a proved existing commandlist-END final hook; never suppress required final64slice closure.

## Required closure equations

Use arbitrary-precision decoder arithmetic and checked uint64 producer addition/reduction. Overflow invalidates qualification/terminal acceptance.

1. observedHeads = coveredProbeHeads + skippedTVD + skippedIdeal + skippedDisabled + skippedOther. Absent cycles are separate.
2. Sum(raw,reserved) heads = coveredProbeHeads. Sum over runtime-present eligibility-count joint = sum over reason-mask joint = roObserved. roObserved+roNA=coveredProbeHeads.
3. For every raw,r: sum over invalidCount histogram = heads(raw,r); reserved way observations=r×heads; four way classes sum16×heads; nonreserved counts=(16-r)×heads.
4. Weighted invalidCount histogram exactly equals INVALID class way observations. Raw FAIL requires r=16; raw MISS requires r<16. The converse “r16 implies FAIL” is forbidden because same-line hits can coexist with r16.
5. For every raw,r: runtime-present reason-mask head sums equal eligible-count head sums. Head HAS_ELIGIBLE count equals sum eligibleCount>0; sum weighted eligibleCount equals live predicate mask5 way count. Reason-presence/way predicates cannot be independently inferred by marginal multiplication.
6. Route/admit and early joint sums equal roObserved; eligiblePresent projection equals the actual eligible histogram. Every frame's scope is stable, phase sum equals slice, all64slice sum equals GLOBAL; old raw status hist/skips/observedHeads equal new raw/skips/covered projection for the exact same snapshot.
7. Phase kernel UID mapping matches r4; final epoch_closed/all resource drain remain mandatory. r5 is additional evidence, never a replacement for old native exit0/full instructions/64slice/scientific terminal gates.

## Minimal new tests before producer release

No tests in this list were run by this design task.

- Const capture unit: 0,1,15,16 reserved ways; mixed VALID/RESERVED; clean, allINVALID, MODIFIED fallback. Every query leaves model state/hash and original return value unchanged.
- Joint fixtures: same r16 set with same-line HIT_RESERVED versus17th newTag FAIL; same r15 with MISS; preserve raw category and identity demand. r16 HIT is not rejected as inconsistent.
- Exact predicate overlap: attached+reuse+missing, attached+reuse+ready, detached, noLive, eligible in the same set; verify head masks and way masks, eligible counts and no marginal multiplication.
- Existing native PRESSURE_ELIGIBLE and NATIVE_REQUESTER_RO_VICTIM scope controls with observer on/off: no original cycle/event/state/old RO or212counter changes. Ordinary native requester frontend-not-consulted/direct-access-positive asymmetry must remain explicit, not “fixed.”
- First r5 fixture with16pending same-set ways: capture full histogram for matching HIT_RESERVED and new identityFAIL; verify exact route/admit joins under early gate/consulted/notconsulted. Add READY-pinned MISS control; don't assert raw allreserved.
- Skip/runtime-off/T-off/unknown phase/overflow/output-cap controls prove NA and fail-closed behavior. Two-slice+multiple-phase reductions, then all64closed frame; repeated same-cycle final epoch-close and cumulative snapshots accepted only when exact/monotonic.
- Byte compare old212 frame formatting and legacy decoder; new parser cannot bypass old parser/full terminal acceptance. Build command/source/flags/noNDEBUG/native execution receipts independently checked before new full application qualification.

## Producer and application gates; finite user proposal

A2 work is not presumed necessary: E2 can own an isolated source candidate, targeted native review and formal producer handoff if separately authorized. Source/base/diff/observer schema/native/build/main/archive hashes must be exact; the new binary must be independently qualified. No main61/r4 binary qualification is inherited wholesale. Existing applicable source/native/input evidence can be reused with an explicit applicability matrix, while modified observer hooks, output parser and all mandatory new gates require fresh exact evidence. No production mechanism/admission/priority change belongs in r5.

If user later approves, propose at most **four r5 F diagnostic endpoints**, in CFD→DWT→Vector→Conv priority, each once with the currently accepted exact positive RO input/certificate/config identities. No S runs or new S/F pair are implied. Each endpoint ≤384MiB, all four ≤1.5GiB, all existing result-generation/resource controls remain. Start only after exact producer/input/schema/profile/source/native/resource qualification and original single central controller adoption; failures charged, no automatic retry. A new observer binary means previous r4 F is context, not an identical-binary scientific anchor. The user has not yet authorized this build or any additional startup.

Admit→firstmerge/firstready delay histograms are useful secondary lifecycle context but **not necessary** to answer the four requested pressure cases once the target-set joint is present. Current admit/merge APIs do not take physical cycle; fill does. Deriving admit time from the last frontend sample would be wrong when non-head/return processing occurs. Defer these optional histograms rather than touch transaction call signatures or invent ages in minimal r5. If later separately included, use immutable generation-bound observer timestamps supplied by the existing runtime's exact physical clock at actual ACCEPTED transitions, bounded by live slots, with right-censored/no-merge/initial-ready counts and no model scheduling; never infer them from present marginals.

## Decision outcomes now measurable

- Reserved-way distribution low for NEW_TAG traffic: no physical all-way-reserved opportunity in the observed request domain.
- r16 exists but confined to SAME_LINE traffic: full target sets existed; replacement demand did not coincide.
- NEW_TAG/r16 with eligible state and route not-consulted: production scope/gate limitation, with requester and early reason preserved.
- NEW_TAG/r16 with no eligible state: actual reuse/attached/missing reason joint explains why safe detach cannot proceed.
- r5/r4 raw or reduction mismatch: evidence invalid, investigate observer/decoder; do not force an explanation or change mechanism.
