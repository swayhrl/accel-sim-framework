# Oracle source and semantic qualification — CPU only

The fixed source supports no immediately admissible matched CH/DH Oracle result among the three stock names. This is a source/CPU eligibility finding; no simulator, simulator --help, GPU, native experiment, capture or service was executed. Existing accepted results are not reclassified.

| Candidate | Source finding | Current qualification | Permissible interpretation |
|---|---|---|---|
| Oracle-M: -gpgpu_perfect_mem1 | Replaces shader lower transport by a finite cluster response FIFO; leaves local frontends and completion paths | HOLD_RESPONSE_GRANULARITY_FOR_PAPER_OO | Not a paired performance reference with current whole-line OO. A separately implemented/qualified return protocol could become a controlled lower-transport counterfactual. |
| Oracle-L2: -l2_ideal1 | Registration/declaration only; no consumer in fixed tracked source | HOLD_INERT_REGISTERED_OPTION | Parser acceptance is not an active all-hit treatment. |
| Oracle-L1 | No matched ordinaryL1D/OO all-hit oracle identified | HOLD_NO_IMPLEMENTED_MATCHED_L1D_ORACLE | New local-availability mechanism/contract needed; not silently replaceable by bypass/zero latency. |

No strict lower cycle bound or upper speedup bound is established. Finite response ports, dependency timing, issue/WB arbitration and changed ordering can affect observed performance; names and optimistic intent are not a monotonicity theorem. No new scientific execution is authorized by this packet.

## What perfect memory actually changes

GPU source registers the flag at gpu-sim.cc477–479. shader.cc165–185 selects the perfect interface only after the higher-priority SST branch and passes the selected interface to both L1I and LDST. shader.h3727–3745 implements full() as response_queue_full(); push() invokes the existing atomic callback, records traffic and enqueues the exact same mem_fetch pointer. It neither performs Tag hits nor changes DRAM timing parameters, splits responses or calls set_reply(). L1I misses also use this interface, so this treatment is not confined to global-load DRAM service.

The response FIFO still has a finite ejection bound (shader.h3592–3598), and cluster icnt_cycle delivers its front response to I-fetch/LDST only when the recipient can receive it (shader.cc7895–7933). The flag does not promise all memory instruction completion in zero cycles. Normal shader requests through this port bypass L2/DRAM transport; possible zero DRAM traffic would be a route consequence to measure under an eligible implementation, not proof of zero memory stalls, free L1 hits or numerical correctness. Other state/source events and generic timestamp counters are not globally reset. Do not reinterpret memlatstat counters as measured isolated DRAM service.

## Concrete whole-line OO counterexample

The actual whole-line OO path creates a128B read with expected sector mask0xF (shader.cc3437–3441,3474–3500). The ordinary sectorL2 push decomposes it into four32B children with original-parent identity (l2cache.cc828–904). OO consume_response records only the one32B sector selected by each returned address, and completes the physical identity/releases the global lower credit/removes inflight state only after all expected bits arrive (shader.cc3521–3553).

The perfect interface skips the decomposition and returns the original128B request at the aligned line address. The exact production response method therefore accepts sector0 only: received mask1, expected15, inflight remains1, frontend completion0 and lower-credit release0. It deletes that returned carrier without manufacturing the other three replies. A64-iteration empty-FIFO observation cannot generate them. This is a concrete conditional lifecycle counterexample for a whole-line cacheable OO NEW_MISS, not a claim that every workload reaches its first miss at the same time or an integrated model replay. CPU control with four proper32B children closes exactly once. Wrong address and duplicate-sector cases hit original assertions; an unknown UID is not consumed. Atomic callback and FIFO-backpressure subcases also pass.

Four isolated executable cases were run using three copied production methods and minimal carrier/FIFO/frontend-callback stubs. Real scheduler, Scoreboard, physical generations/refcounts, numeric values and DRAM/cache timing are not instantiated by that fixture. It establishes the return-mask mismatch and controls, not general liveness or full CH/OO correctness. Existing whole-line IO has the same0xF receive requirement at shader.cc3209–3244; only OO was executed in this CPU fixture.

## Resources and lifecycle that remain real

- CH PAPER_BASE keeps common admission/Tag checks and conventional L1/cache/MSHR path. DH PAPER_OO keeps PIB admission, next_reference registration, Tag-bank grants, physical allocation/ref ownership and lower-create reservation before m_icnt (shader.cc3349–3518,3663–3689,3970–4081). Matching lower flags does not make these local designs equal area or equal service.
- Finite DH create/inject/refill/retire quotas remain1 per absolute corecycle, collection width4, Tag commit and collection/WB edges remain nonzero. Generic local cache data/fill ports and miss queues are retained (shader.h2156–2160; dtc-l1-common.h59–118; gpu-cache.cc1196–1272). Enlarging Tag or pool is not what the perfect flag does.
- Original response ownership/parent UID/sector mask and physical/PIB-slot generations must remain valid. Pending returns, waiter notifications, all references registered, operand-collector WB and exact pending-write closure precede retirement. A fabricated ready bit or Scoreboard release is not a lawful memory completion (shader.cc3521–3655; dtc-l1-common.h709–772).
- Stores retain outstanding-store acknowledgements; perfect writes are accepted by the explicit store_ack branch. Global atomic side effects occur on perfect push and outstanding atomic lanes close on global response/WB; shared atomics are a separate path. The CPU callback subcase does not certify trace numerical atomic values or every operation class (shader.h3736–3740; shader.cc4657–4719,5241–5249,7128–7143).
- Warp Scoreboard reservation/RAW/WAW, memory barrier waiting and hardware completion still apply. DTC pending_work and GPU active() include live PIB/inflight state; a timeout/deadlock/maxcycle exit cannot be promoted to natural accepted completion (scoreboard.cc82–152; shader.cc2726–2742,7066–7081,7200–7226; gpu-sim.cc1480–1503).
- Framework trace issue delegates to the base issue_warp and generates real source memory-access queues; no oracle establishes source input values, complete native application capture or numerical correctness (trace_driven.cc1130–1174).

## Why common shortcuts do not define Oracle-L1

With an enabled ordinaryL1D, shader.cc4414–4429 asserts l1_latency>0; the zero branch in a helper does not make -gpgpu_l1_latency0 an eligible configuration. gmem_skip_L1D/dl1none changes bypass identity before OO dispatch; it does not represent all hits while retaining the original DTC path. perfect_inst_const_cache applies to instruction/constant handling, not an all-L1D oracle. finite_service0 removes modeled local service constraints and is a different architecture treatment, not an innocuous implementation convenience.

A possible future L1 read-data-availability design must specify whether original Tag/physical/PIB admission is retained. Retaining it leaves a residual local-service reference; bypassing it changes the mechanism and must be named accordingly. Preserve original instruction issue/coalescing, all-reference dependency cardinality, Scoreboard, generation/ref/waiters, WB and retire paths; keep store/atomic/bypass/fence rules explicit. Such a design needs a new version/binary and independent CPU/integrated qualification before separately authorized scientific use. No source patch or implementation was produced here.

For a future M design, four32B return units with exact parent/generation binding, bounded FIFO/service and once-only credit release are minimum protocol requirements. L2 all-hit design must be actually implemented and retain operation-specific ownership/events/acks, routing/ports and coherent return granularity. Neither protocol sketch is a strict performance-bound proof or production qualification.

## Preserved boundaries and reproduction

The old Tag1024/physical640 forward-progress HOLD remains unchanged; a transport oracle cannot create a safe reclaim victim or extra physical slot. LaneX invalidation is not a substitute for reclaim. Existing HtoD/source-event-invalidation and numerical/coherence boundaries remain unresolved; neither absence of an interkernel upload nor a cache-hit counter proves correct values. This task changes no production source, input identity, prior scientific status, owner/ledger/budget or v0.23 manuscript.

SOURCE_INDEX.json binds fourteen exact Core/FW Git blobs and actual source bytes. SOURCE_CALLGRAPH.json has32 file/line/SHA/excerpt anchors; the two grep witnesses expose the entire fixed tracked-tree option occurrences. ORACLE_SEMANTICS_MATRIX.json gives each stock/design route explicit status and uncertainty. Source excerpts and CPU stubs are not additional simulation evidence.

To reproduce only the isolated fixture, compile cpu_fixture/perfect_interface_oo_lifecycle.cpp with g++ -std=c++17 -O0 in a fresh private output directory, then run that private executable with no argument, wrong_address, duplicate_sector, unknown_uid. Disable core dumps for the intentional assertion cases; expected returns are0,-SIGABRT,-SIGABRT,0. No accel-sim binary is called. The executed source and CPU_RESULT.json pin the precise production method extraction, compiler command and limits; fixture executables and temporary logs are not production simulator binaries and are excluded from the public manifest.
