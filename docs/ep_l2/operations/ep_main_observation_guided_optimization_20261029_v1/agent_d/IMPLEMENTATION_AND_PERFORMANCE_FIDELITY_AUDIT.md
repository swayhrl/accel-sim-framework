# EP-L2 Implementation and Performance Fidelity Audit

**One P1 implementation path omission is confirmed by production-class CPU tests.** An ordinary non-RO request facing a fully reserved set is rejected by frontend preview, although the backend can legally detach a same-set old certified RO transaction. Both ordinary global reads and writes reproduce the omission. A private minimal preview candidate admits them, detaches once, and correctly drains old returns. **No new P0 was confirmed. Accepted-application incidence and cycles impact remain UNKNOWN.** This does not explain all F slowdowns.

## Frozen identity and audit scope

Core `78f4b59e865b136eede74df74c44c210f5b4ca04`; Framework `9dd1ee57a83d83b56b7874bc7c716185ab52c8f7`; model ELF SHA256 `78d4e96bb79c776e27146bcf168d7c70cf3897ef9cb84d837d8974fec4c91b8a`. Core HEAD and thirteen production source hashes were checked; tracked diff remains empty. The actual linked static archive SHA agrees with accepted Source5. See SOURCE_AND_SCOPE.json. Existing exact accepted point/config identity was reused; no redundant large raw/Trace/ELF scan.

The current accepted finite model, exact options and modeled-resource overlay govern actual identity. The historical architecture roadmap has different 1152-slot/D256/64x16 targets and unresolved choices; it is not the actual 1168-slot/D512/32x8 model specification. The explicit overlay already discloses physical versus reachable static capacity.

No accepted Core, archive, model ELF, registry, controller, old budget, longtail process, or shared Trace was modified. No application model or GPU collection was started. New files and private CPU build artifacts are confined to this independent engineering directory; bulk retention belongs on true164. The candidate is NOT accepted science.

## Actual W/V/M/T paths and modes

MODE_AND_QUALIFICATION_MATRIX.csv and REQUEST_PATH_MATRIX.csv give the path map and source references.

- S: FT1, V0/M0/T0. Finite WB16 staging, copy service and common bank model remain.
- W_ONLY: FT2, Vclean0/Vdirty0/M0/T0. In-place WB role transfer, native MSHRs; no TVD object or paid V query. Engineering configuration semantics exist, but formal mode qualification is separate.
- WV: FT2, clean/dirty V enabled, M0/T0. It includes retention, forwarding, lookup latency, pinning and promotion; FWT retains this legal mode.
- F-minus-T: WV plus certified RO M1, T0. It is not WV, which has M0.
- F: certified RO M1/T1 with W/V. Current conservative eligibility still requires attached, no reuse_seen history, and required-not-ready sectors.

A Tag miss entering TVD pays a serialized cached-ticket query. A V response must also receive an actual Payload bank grant and real ICNT enqueue. A normal resident hit skips TVD. The ticket avoids charging a CAM query on every retry. A certified RO candidate then pays its own one-GPU-cycle, one-port query before miss/merge admission. Those are explicitly modeled costs, not evidence that V/M are accidentally off. Repeated host C++ probe/capacity calls do not independently advance GPU time.

RO admission uses the same D512 descriptor allocator and per-address32 cap. M1 bypasses ordinary line-MSHR128, not shared descriptors, data banks, request queues or response credits. Accepted Vector6M line-MSHR peak0 with RO independent pending-line peak70 is consistent with this implementation, not zero memory concurrency. Live merge includes ready/draining overlap; it is not strictly requested-sector-before-fill reuse.

FT1 dirty replacement pays source read, one-cycle copy latch, and staging write. FT2 changes the old Payload to WB in place and reserves another landing; it removes copy but still pays lower WB readout. WAD protects the address through real WB completion, independently of a staging Payload's release after lower acceptance. Dirty forward keeps a valid pinned Payload and cannot permit writes/atomics through a mandatory owner.

RO lower packets carry Payload/generation. Attached fills validate the current Tag identity before changing its sector state; detached fills update the old Payload only. Response bank grants are cycle-local, with real enqueue/backpressure rather than an uncharged per-transaction data buffer. Retirement requires no waiter and no issued/required-not-ready obligation; attached Payload becomes resident, detached Payload releases. Current CPU coverage tests a bounded subset of these invariants.

## Findings by severity

### P0: no new issue confirmed within this bounded audit

This is an audit negative result, not exhaustive protocol verification. Existing unsupported host-write technical failures and the independent V3 repair keep their original eligibility boundaries. They were not reclassified or silently merged.

### P1 D01: ordinary requests cannot reach generic Tag relief

`gpu-cache.cc:2798` dispatches only RO new_request preview to the RO adapter. For an ordinary request, lines2821-2823 immediately return RESERVATION_FAIL. `l2cache.cc:1432-1443` then refuses the head, so `access()` is never invoked. However `ep-l2-ft-cache.inc:338` implements generic `m_ro->relieve(addr)` after raw TagFAIL for any incoming request. RO preview alone virtualizes this opportunity at `ep-l2-ro-runtime.inc:277-280`.

The Source78 CPU fixture fills a real 8-way target set with eight actual never-merged pending certified RO reads. An ordinary read or write to a new same-set address then stays head for64 fixture ticks despite eligible8, D8/512, and available MissQ capacity. Old returns eventually allow progress; this is unnecessary blocking, not a permanent deadlock or demonstrated corrupt response.

A private seven-line candidate asks the unchanged read-only detachable predicate, virtualizes MISS and retains the ordinary downstream resource gates. Repeated32 previews preserve old Tag identity and bank-grant total. Real partition admission then detaches exactly once for both read and write, validates returned versions and generation, and completely drains resources. T0, reuse_seen and line128-full controls still block. Details and precise logs are in CPU_EXECUTION_SUMMARY.md and the final execution JSONs.

The backend-only DIRECT witness separately establishes previewFAIL/backendaccept in the corresponding state. It intentionally does not complete through the subpartition, because it bypasses that admission ledger. Its first exploratory version incorrectly called finish and aborted in the test harness response ledger; the -6 receipt and original log are preserved. Corrected candidate read/write witnesses use real partition admission and full drain.

This establishes an implementation opportunity loss. It does NOT establish application speedup, the proportion of Conv/Scan losses, or that every full set has a legal RO victim. Commit-only production TagFAIL=0 cannot exclude this precommit omission. Existing results describe actual Source78, but a claim that current T serves generic native full-set demand must be narrowed.

The CPU candidate is not ready for scientific execution. Main identified that diagnostic preview `consulted/intermediate` is not updated by the seven-line change; raw must stay immutable while the decision path is separately reflected. Without that correction, future diagnostic classifications can still report relief-not-consulted/kept-fail. This gap is explicitly pending. No protection was relaxed, no assertion removed, and no accepted source was changed.

### P2: implemented finite costs and organization constraints

D02: TVD and RO queries are serialized, finite and paid. They may outweigh infrequent useful V service or M relief, especially when a new head reaches an already ready/draining transaction. Their physical one-cycle/one-port circuit realization is not proven, but deleting the modeled payment is not a safe bug fix.

D03: Payload allocation/reclaim follows Tag-index bank color; free entries in another bank do not automatically help. A single pending replacement can hold landing/control reservations while retrying. P1 provides one bank operation per physical GPU cycle. Sticky pending/grant identity prevents lost retries; whether non-ready ownership causes avoidable idle-bank time on accepted apps remains unmeasured. A redesigned allocator/arbiter needs real hardware costs and protocol checks.

D04: W removes copy, not all WB service, WAD ordering, mandatory lifetime, landing requirements or lower traffic. Scan eliminating copy/WB-space events while slowing down is compatible with costs elsewhere or noncritical eliminated waits; it is not proof that W was off.

D05: any accepted live merge sets reuse_seen permanently for that transaction, including a merge whose requested sectors are already ready. Retiring that waiter does not clear history. Current candidate REUSE_GUARD intentionally keeps all8 merged old RO ineligible and drains17 responses correctly. The necessity/value of every conservative exclusion is not proven; changing policy requires a separate correctness and traffic proof. High merge fractions cannot be multiplied by unrelated full-set counts.

D09: same physical capacity is not equal usable capacity. In32x8 S, resident landing=index reaches only0..255 of nominal1024. Another768 nominal resident slots and128 bypass slots have no regular production allocation path; source reachable resident+WB upper bound is272, not a joint-achievability proof. F can borrow physical IDs from1168 subject to color, roles and finite metadata. This is already declared static-stranding versus pooling, not a newly discovered hidden baseline change. S/F includes that organization advantage; there is no basis to claim equal usable capacity or smaller hardware SRAM/area from the Tag sensitivity.

### P3: unproven optimizations, model closure and observation gaps

D06: directory-full `preview_install` favors CLEAN over WB_COMPLETE only for a dirty install; a clean install picks oldest eligible across those states. Bank-compatible `tvd_reclaim_one` always tries CLEAN then WB_COMPLETE. Real response_commit refreshes age. Neither fact proves valuable data is prematurely lost on an accepted application. B's service_seen proposal must update both selectors, retain revision consistency, reset on install and dirty-promotion reincarnation, set only on actual service, and preserve pins/mandatory/bank constraints. The1024B logical bit estimate omits comparators, ports and timing. It remains HYPOTHESIS.

D07: software bounded scans and invariant assertions are not a circuit implementation. Paid frontend/completion CAMs and declared indexed control views/update lanes exist, but free-list, ready-response selection, reclaim and cleanup timing/PPA are not closed. The code explicitly prints metadata_PPA and metadata_clock_closure UNKNOWN. Extra host work is not GPU stall time. Conversely, abstract single-call selection may under-model hardware cost; no evidence supports labeling this as an F-only pessimistic bug.

D08: `l2cache.cc:1617-1624` increments coarse payload_block for any access RESERVATION_FAIL in payload mode. It is not physical-pool-full. Bank/port subcategories use the recorded service result; other causes need their own populations. M1 RO does not set conventional MSHR-need flags, so C7e descriptor-need fields gated by those flags are not all RO descriptor demand. FT tracked requester excludes L1WB while generic MS head checks need not. Without matching type/population, derived rates remain UNKNOWN. Arrival, queue-enter, first-head, admission and backend TagFAIL remain distinct.

D10: W-only parsing is not Host/native/app qualification. Its earlier exact3 attempt was RAM HOLD before build/fixture, not an observed protocol failure. Source92 P2, host-writeV3, MSHR64 and RO candidates are separate implementations; none was folded into Source78. V3's existing800 pure checks/10 production CPU tests cover a restricted noRO complete-sector host-write domain; native application qualification is still pending. No old failed input was rerun here.

FINDINGS.json gives all ten findings with trigger, intended and actual behavior, precise locations, evidence, impact, workload boundary and minimal control. PROVEN is always scoped to source fact or actual CPU trigger; accepted-application causal impact is not inferred.

## What explains present performance, and what cannot yet be attributed

Stencil approximately1.0992x and4,930,616 actual V responses, 3MM approximately1.0163x and1,147,507 V responses, and positive GEMM/WV/FWT/WV demonstrate working mechanism paths. Removing WB-space and copy does not ensure critical-path improvement: Scan still slows, and Conv retains ordinary MSHR/WAD/bank/lower interactions. Paid V queries, metadata sharing, bank conflicts, required reservations, safe old-return lifetimes and RO per-request query costs are real modeled expenses.

D01 is the strongest concrete implementation restriction identified. Its actual joint occurrence is not measured in the accepted compact REF summaries, so the share of existing losses attributable to it is UNKNOWN. It cannot affect WV/W-only with no RO runtime. W/V mode qualification and decomposition can therefore prepare in parallel; expanded T science should first review the minimal correction and its instrumentation.

Existing true detach witnesses do not isolate T benefit. S/F or WV/F cannot substitute for same-background F-minus-T/F. NewSource performance must use its own controls; old ELF cycles cannot fill a newSource counterfactual. Synthetic CPU cycle differences are not workload speedup or realistic DRAM timing.

## Executed work and recommended next decision

Selected final evidence has13 bounded CPU controls:12 complete-drain cases and one backend-only DIRECT. Prior exploratory failure remains preserved. No production collector, full newSource rebuild, modelELF, native qualification, app NI or new scientific performance result was produced.

Prioritize review of D01's minimal correction, diagnostic consistency and remaining CPU/resource guards before broadening T claims. Keep conservative protocol protections. Continue W-only/WV engineering separately. MINIMAL_NEW_SOURCE_VALIDATION_PLAN.md proposes exact kinds of sameSource controls for later Main/user review, with no fresh budget and zero authorized application starts. Do not expand parameter scans to compensate for an uncorrected implementation path.
