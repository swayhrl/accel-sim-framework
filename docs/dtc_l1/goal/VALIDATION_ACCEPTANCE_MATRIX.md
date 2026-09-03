# DTC-L1 M1-M4 Validation and Acceptance Matrix

All items marked **HARD** must pass before automatic progression. No performance-speedup threshold is a correctness gate.

Use deterministic request-level/unit tests when they provide clearer cycle/state expectations, plus simulator integration tests to prove the real pipeline path.

---

# M1 — Foundation

## M1.0 Source audit — HARD

- [ ] Actual built Core source tree and SHA identified.
- [ ] Framework/Core source relationship documented.
- [ ] Load request, L1, lower issue, fill, and completion functions mapped.
- [ ] Store, Atomic, Fence, architectural bypass paths mapped at navigation level.
- [ ] Config/stat plumbing mapped.
- [ ] Safe dynamic/lower request identity strategy established or documented as needing a new UID.
- [ ] No architecture guess used to close an UNKNOWN.

Deliverable: `implementation/SOURCE_INTEGRATION_MAP.md`.

## M1.1 Coalesced-line representation — HARD

Directed tests:

- `B01A`: 32 lanes -> 1 distinct 128B line.
- `B01B`: 32 lanes -> 2 distinct 128B lines.
- `B01C`: 32 lanes -> 4 distinct 128B lines.
- `B01D`: fully divergent -> 32 distinct 128B lines.
- `B01E`: sector masks preserved when multiple 32B sectors belong to one 128B line.

Pass: exact expected line-reference count/masks; no new coalescing algorithm changes upstream behavior.

## M1.2 PIB/backpressure — HARD

- `B02`: configure PIB=2; third live instruction cannot admit until a slot releases.
- `B03`: PIB entry releases only at real completion; no early release on miss issue/fill if completion is later.
- Backpressure must propagate to the established entrance; no drop/bypass.

Accounting: admitted-retired == live PIB entries during execution and closes at drain.

## M1.3 Tag-bank timing — HARD

- `B04`: multiple same-bank refs require multiple cycles.
- `B05`: four refs mapping to four banks can be served in one cycle.
- Per-bank service never exceeds 1/cycle.
- Total service never exceeds 4/cycle at defaults.

## M1.4 Baseline resource limits — HARD

- `B06`: MSHR capacity configured small; entry-full condition occurs exactly when expected.
- `B07`: if current source distinguishes merge limit, directed merge-full behavior matches source semantics.
- `B08`: lower outstanding cap configured small; next new request blocks exactly at cap.
- `B09`: architectural bypass path matches clean baseline behavior when DTC disabled.

## M1.5 LEGACY neutrality — HARD

Compare frozen clean upstream build against project code in `LEGACY` on at least:

1. deterministic L1 hit microbenchmark;
2. deterministic miss/merge microbenchmark;
3. one small representative kernel that completes quickly.

Require exact equality for the agreed deterministic outputs, including at minimum:

- dynamic instruction count;
- kernel cycles;
- L1 accesses;
- L1 misses;
- L2/lower read request count;
- DRAM request count when deterministically exposed.

If any differs, M1 FAIL.

## M1 counter/invariant closeout — HARD

- Primary stall reasons close to total defined frontend stall cycles.
- Non-exclusive resource counters are independent.
- PIB accounting closes.
- Lower outstanding never exceeds cap and token accounting closes.
- `git diff --check` clean.
- Required parsers produce machine-readable summaries.

M1 PASS -> create/push `review_packs/M1_FOUNDATION/` and continue to M2.

---

# M2 — IO-DTC Whole-Line Reads

## IO functional tests — HARD

- `I01 ColdMiss`: one new 128B miss -> one physical allocation + one lower request.
- `I02 ValidHit`: valid hit -> no new lower request.
- `I03 PendingHit`: two+ readers before fill -> total lower read requests remains exactly one while Tag remains pending/visible.
- `I04 AllocWidth4`: four independent misses may allocate in one cycle at width=4.
- `I05 AllocWidth8`: eight independent misses require at least two allocation cycles.
- `I06 PartialAlloc`: instruction allocates some lines, then stalls for lack of free lines; allocated lines remain held, no rollback.
- `I07 LRU`: controlled accesses select the exact 4-way LRU victim.
- `I08 EvictWhileFill`: logical Tag eviction while request is in flight; response reaches original physical allocation only.
- `I09 DuplicateAfterEvict`: re-access same address after pending Tag eviction may create a second lower request and increments duplicate-after-eviction counter.
- `I10 IOHOL`: younger ready entry cannot retire before unready FIFO head.
- `I11 SameCycleRelease`: release at retirement is visible to allocator in same cycle according to event ordering model.
- `I12 TinyPoolDeadlock`: directed undersized pool naturally reaches detected `EXPECTED_RESOURCE_DEADLOCK`; no special-case code.
- `I13 Default80KProgress`: same stress class at default 80KB makes progress and finishes; unexpected watchdog event is failure.
- `I14 OutstandingCap`: cap=2; third committed lower request waits until credit returns.
- `I15 IssueWidth`: each SM issues <= configured lower request width per cycle.

## IO no-MSHR proof — HARD

For DTC read path:

- traditional L1 MSHR capacity is not consulted as DTC merge/capacity gate;
- directed high-MLP test can exceed Baseline PIB=8 occupancy and Baseline MSHR=32 outstanding dependencies when configured resources allow;
- Pending hit still suppresses duplicate lower read requests.

## IO fill/release invariants — HARD

- all valid Tags map to allocated physical lines;
- no stale generation/UID fill;
- no invalid free-line Tag mapping;
- only FIFO head retires;
- all required data ready at head retirement;
- no lower token leak/double-release.

## IO counter sanity — HARD

Directed cases must produce expected values for:

- new miss / valid hit / pending hit;
- physical allocations/releases;
- partial allocation events/lines held;
- pending-hit lower requests avoided;
- duplicate-after-eviction;
- IO HOL cycles/ready-younger count;
- outstanding request histogram/cap.

M2 PASS -> create/push `review_packs/M2_IO_READ/` and continue to M3.

---

# M3 — OO-DTC and Sector

## M3.1 Whole-line OO retirement — HARD

- `O01 YoungerReady`: I0 pending, I1 ready -> I1 may retire first.
- `O02 RetireWidth`: multiple ready entries -> no more than configured 1 retirement/cycle.
- Default ready selection deterministic oldest-ready.

## M3.2 Ref Count — HARD

- `O03 ValidHitRef`: Valid hit creates exactly one Ref for one coalesced 128B line and releases exactly once.
- `O04 PendingHitRef`: Pending hit adds one Ref and pending merge dependency.
- `O05 DivergentRefs`: fully divergent instruction can create multiple line refs; counts correspond to coalesced lines, not threads per se.
- `O06 ShadowRef`: modeled Ref Count equals independently reconstructed Shadow Ref for every physical line throughout directed test.
- `O07 EvictRefNonzero`: Tag eviction with ref>0 clears `tag_valid` but does not free physical line.
- `O08 FinalRefFree`: final ref decrement with `tag_valid=0` reclaims line with same-cycle allocator visibility.
- `O09 EvictRefZero`: Tag eviction with zero refs permits immediate reclaim under modeled event ordering.

## M3.3 Merge/wakeup — HARD

- `O10 ManyWaiters`: multiple PIB entries wait on one pending read; one lower request.
- `O11 FillWakeAll`: one fill wakes every registered waiter exactly once.
- `O12 SlotReuse`: delayed fill cannot wake a new instruction that reused an old PIB slot.
- `O13 InjectBadGeneration`: intentional debug mismatch triggers invariant failure.

## M3.4 IO-vs-OO causal test — HARD

Construct e.g. older long-latency + younger short-latency requests:

- IO: younger-ready entries accumulate HOL and cannot retire first.
- OO: younger-ready entries retire before older unready entry while retire width remains 1.
- Same dynamic operation count and request/data semantics.

Expected counters: IO HOL > 0 and OO out-of-order-retire count > 0.

## M3.5 Whole-line gate before sector — HARD

All O01-O13 and whole-line invariants pass before sector implementation starts.

## M3.6 Sector extension — HARD

- `S01 ValidSectorHit`: existing valid sector resolves immediately.
- `S02 PendingSectorHit`: pending sector registers dependency without duplicate lower request for that sector.
- `S03 InvalidSectorExistingTag`: missing sector under existing Tag becomes Pending without allocating a second 128B physical line.
- `S04 MultiSectorOneRef`: one instruction references three sectors of one line -> line Ref Count contribution +1.
- `S05 TwoPendingSectors`: two unresolved sectors -> wait count +2.
- `S06 IndependentFills`: two sector fills independently decrement wait count to zero.
- `S07 EvictWithPendingSector`: Tag may be evicted while old physical sector request is pending; fill still targets original allocation.
- `S08 RefProtectsLine`: line not reclaimed while Ref Count >0 regardless of sector readiness.
- `S09 SectorMask`: requested/ready/pending masks preserved exactly.

M3 PASS -> create/push `review_packs/M3_OO_SECTOR/` and continue to M4.

---

# M4 — Full source-reachable memory-operation lifecycle + workload bring-up

## M4.0 Semantics audit — HARD

`implementation/M4_MEMORY_OP_SEMANTICS.md` must source-map current Load/Store/Atomic/Fence/bypass behavior before functional M4 edits.

A verified source limitation is an acceptable audit result when it is documented rather than silently replaced. For the frozen current source, the PTX frontend cannot generate the existing dynamic proxy-fence path; apply `goal/M4_FENCE_REACHABILITY_RESOLUTION.md`.

## M4.1 Store tests — HARD

- `W01 StoreHit`: audited hit behavior preserved.
- `W02 StoreMiss`: audited miss/write-allocate/no-write-allocate behavior preserved.
- `W03 StorePolicyParity`: LEGACY vs paper variants differ only where DTC lifecycle requires; underlying write policy matches audited baseline semantics.
- `W04 StorePIBLifetime`: Store occupies/releases pending-instruction state at the correct completion point.

## M4.2 Atomic tests — HARD

- `A01 SingleAtomic`: executes exactly one architectural atomic operation.
- `A02 SameAddressTwoAtomics`: two executed atomics to same address remain two side effects/lower operations according to audited semantics; never merged into one read dependency.
- `A03 AtomicHOLIO`: long Atomic at IO head can block a younger ready load when ordering permits the younger load to become ready.
- `A04 AtomicHOLOO`: OO may retire the younger eligible load early without violating source-reachable architectural ordering.

## M4.3 Fence reachability / ordering boundary — HARD

For the frozen current source, end-to-end PTX F01-F03 are classified `SOURCE_UNREACHABLE_NA`, not failed, only after all replacement gates below pass:

- `F00A FenceReachabilityAudit`: prove PTX lexer/parser/static decode cannot generate `FENCE_OP` / proxy-fence state and distinguish `membar` from fence.
- `F00B NoSilentSubstitution`: no parser/decode fence semantics, `membar -> FENCE_OP`, forced proxy bits, or regular-fence bypass is introduced by this project.
- `F00C CurrentDomainFenceAccounting`: accepted workload triplets have identical source-reachable `FENCE_OP` counts; under the frozen source expected count is zero. If a real source-backed `FENCE_OP` producer appears, STOP and reactivate end-to-end fence validation.
- `F00D DynamicProxyPathPreserved`: M4 changes do not semantically alter the existing unreachable dynamic proxy-fence path.

Optional synthetic direct-object testing may exercise the already-existing dynamic proxy-fence path as DIAGNOSTIC evidence, but must not be described as PTX frontend support.

Do not substitute PTX `membar` for proxy fence. See `goal/M4_FENCE_REACHABILITY_RESOLUTION.md`.

## M4.4 Architectural bypass tests — HARD

- `BP01` bypass load follows baseline architectural bypass path without DTC Tag/physical allocation.
- `BP02` bypass store follows audited baseline behavior.

Do not implement DTC policy bypass.

## M4.5 Mixed regression — HARD

For the frozen current source, `MIX01` is a deterministic mixed **source-reachable** Load/Store/Atomic/architectural-bypass sequence under LEGACY/Paper Base/IO/OO. Do not insert `membar` as a fence substitute.

Require:

- identical dynamic operation counts where architecture dictates;
- identical source-reachable `FENCE_OP` count (expected zero for current source);
- Atomic side-effect counts preserved;
- no stale fills/ref/merge violations;
- no unexpected deadlock;
- correct drain/accounting.

## M4.6 Workload manifest — HARD

Before running workload set, document mapping/status/input/provenance in `implementation/WORKLOAD_MANIFEST.md`.

No silent benchmark substitution. A workload requiring unsupported PTX `fence` syntax cannot count toward the accepted bring-up set.

## M4.7 Diagnostic workload bring-up — HARD

Run available provenance-resolved representative Chapter-4 compute workloads under `PAPER_BASE`, `PAPER_IO`, `PAPER_OO` with identical trace/input/unrelated GPU config.

Minimum required bring-up set should include at least five successfully resolved workloads spanning multiple behaviors, and should attempt the available set documented in the Goal Plan (bicg, atax, mvt, syrk, syr2k, 2mm, conv2d-equivalent if confirmed, Parboil spmv, and resolved gesummv/gesu/gemv mappings).

For every accepted triplet require:

- same dynamic instruction count;
- same Load count;
- same Store count;
- same Atomic count;
- same source-reachable `FENCE_OP` count (current frozen source expected zero);
- no HARD invariant failure;
- no unexpected watchdog/deadlock;
- valid Core/Framework/config/trace provenance;
- counter accounting closure.

A workload with unresolved provenance may be executed only as explicitly labeled diagnostic exploration and must not count toward the provenance-resolved minimum.

## M4.8 Output/parser closeout — HARD

Machine-readable outputs exist and parse correctly:

- `summary.csv`;
- `stall_breakdown.csv`;
- `occupancy.csv`;
- `latency.csv`;
- `traffic.csv`;
- `io_hol.csv`;
- `oo_ref_merge.csv`;
- `mechanism_sanity.csv`.

Causal consistency warnings are generated but are non-fatal review signals.

## M4 final repository/evidence gate — HARD

- all M1-M4 review packs independently navigable;
- source anchors/final SHAs recorded;
- semantic commit history recorded;
- M4 review pack explicitly records the current-source proxy-fence frontend limitation and `F01-F03 SOURCE_UNREACHABLE_NA` disposition;
- `git diff --check` clean;
- expected working-tree status documented;
- no raw traces/huge logs/build trees committed;
- `codex_handoff/LATEST_REPORT.md` points to M4 review pack and says `READY_FOR_M5_REVIEW` only if all active HARD gates pass.

Then STOP. M5 is not authorized.
