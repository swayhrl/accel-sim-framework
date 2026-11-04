# Victim quota CPU and hardware-cost qualification

**CPU correctness: PASS within recorded directed scope. Hardware cost/timing: PARTIAL. Host/native/application: NOT_QUALIFIED.**

## Verified production code

Anchors below refer to exact bf4 Core, not accepted Source78.

|Location|Meaning / protected boundary|
|---|---|
|ep-l2-tvd-directory.h:115-128|Maintained m_clean_count, configured limit and finite128 capacity; constant-time count accessor. Host C++ fields are unsigned, not a physical8-bit area measurement.|
|same:153-185|Preview is const; quota0 disables CLEAN; at quota only reclaimable CLEAN may replace CLEAN. Dirty installs are not quota-gated. Mandatory/inflight and readers cannot be selected.|
|same:207-216,327-334,405-414|Count update on install, CLEAN replacement, promotion and erase. No preview update. Generation bumps remain.|
|same:228-280|Sector/read lease checks, generation/payload matching, pinning until actual bank+response enqueue; quota does not override these.|
|same:338-382|Mandatory reclaim refused; lower data-transfer proof, bound WB UID, completion transition and epoch reader/mandatory drain retained.|
|ep-l2-tvd-cache.inc:39-55|Mandatory allocation reclaims unpinned CLEAN then completed WB in the required bank color; pending/inflight never reclaimed. Quota does not add/free ports.|
|same:81-93|Existing paid one-cycle lookup and one frontend CAM query/tick remain.|
|gpu-cache.h:3340-3354|Custom quota0..127 requires both CLEAN+DIRTY and RO disabled.129/partial/RO custom modes rejected. Default128 follows original mode guards; RO/F default128 application qualification is not inherited.|
|same:2354-2407|1168 physicalPayload slots remain; four P1 banks and generation-aware handles unchanged.|
|gpu-sim.cc:345|Production registered quota option default128; actual six parser echoes have283 options.|

Default128 code proof: count can reach128 only when every directory row is CLEAN. There is then no free/non-CLEAN row for the new quota predicate to exclude. Below128 the original candidate set is unchanged. All mutations of the CLEAN state update the count. This establishes the intended quota-neutral algorithm at128; full application acceptance still requires newSource qualification.

## Evidence and executed tests

Reused, SHA-indexed V2 evidence: full144-TU build/asserts enabled; directory UBSan and mandatory128 across0/32/64/96/128; readers/generation/preview/promotion count; production32x8 all five caps,91 version-checked replies, delayed dirtyWB, exact drain; cap128 vs Source78 and cap0 vs legacy dirty-only directed semantic golden; sector/promotion/WAD128/lower-full/bank-color tests. These are previous passes, not new runs.

New V3 execution:

- Actual six production-parser config echoes:283 distinct options, all exact expected values, original282 preserved. Parser helper never constructs a GPU or opens Trace.
- Missing cap0/64 production dirty-forward read/write/atomic, missing-sector wait and WAD128/lower-full:PASS.
- cap64 bank-local full and partial-dirty victim protections:PASS.
- Custom quota64 with RO requested:expected production rejection PASS.
- Implicit newSource default128 semantic trace equals explicit new128 and recorded Source78 fixture golden:PASS (DEFAULT128_STRICT_CPU_GOLDEN.json). Not application NI.
- Candidate Host schema:6 positives and5 negatives PASS. Official HostQ/native not exercised.

**Retained unsuccessful attempt:** the existing combined dirty-boundaries fixture at cap0 aborted on its assertion that a formerly evicted CLEAN line must reuse its old handle. That fixture requires CLEAN retention and is inapplicable at quota0. The raw failing result remains in MISSING_PRODUCTION_CPU_RECEIPT.json and stderr. No production assertion or protection changed. A private fixture now explicitly requires quota0 old directory alias absent, old generation handle not live and replacement identity distinct; data reply version, partial-sector no-false-forward, mandatory ownership, bank pressure and full drain still assert. Adapted fixture PASS in CAP0_CONTRACT_CPU_RECEIPT.json. This is a fixture assumption correction, not a discovered simulator Bug or performance repair.

## Hardware cost boundary

The quota decision reads maintained count, not a new O128 occupancy scan. Existing entry selection/priority loops are the simulator representation of the preexisting directory selector. No new address CAM lookup, Tag probe, data-bank operation, queue or Payload SRAM was added. This is a code fact, not physical timing closure.

At minimum, a finite implementation needs count0..128 (8 bits) + quota0..128 (8 bits) per slice, one threshold comparator/admission gate, and correct increment/decrement or combined-delta update logic. Across64 slices this is1024 logical state bits; configuration may alternatively be shared, so this is a conservative per-slice organization, not SRAM/area measurement. Existing metadata reports3 indexed update lanes. Multiple same-cycle changes may require merged deltas/multiple-input arithmetic; the software increments are not proof of physical update-port throughput. Comparator placement, update serialization, critical path, energy and PPA are UNKNOWN. The Core currently charges no separate quota compare cycle. Performance would therefore evaluate this abstract comparator contract, not prove its area/timing feasibility. **Hardware qualification remains PARTIAL.** A costed pipeline alternative must be a separate source/spec; do not silently add latency after freezing.

For mandatory progress, optional cap never blocks dirty insertion; readers can still temporarily pin reclaimable data, and all128 mandatory rows or a color-local full pool can correctly backpressure. Existing lower/response queues and bank service still limit progress. Correctness under eventual resource release is directed-tested, not a claim of zero waits.

No full application was launched; no app NI or quota performance gain is claimed. Current ELF/source SHA recheck PASS, source tracked tree clean, previous source/ELF archive and two restore receipts reused; newSource is not merged into accepted Main.
