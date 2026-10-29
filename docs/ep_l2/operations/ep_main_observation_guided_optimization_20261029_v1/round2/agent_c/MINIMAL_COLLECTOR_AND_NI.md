# Minimal collector engineering and NI boundaries

## Implemented candidate

`mt_sector_counter_candidate.h` is an88-byte scalar-only C++ candidate. A null pointer means OFF. It has NO production hook, allocator, map, queue, address table or added Tag lookup. The module test uses real Source78 transactions/shared MSHR with a reference payload port. Its test adapter calls the existing diagnostic snapshot before merge, then counts only after `merge==ACCEPTED`; that test lookup is NOT proposed for production.

Proposed production location: `ep-l2-ro-transactions.h:197-201`, after real descriptor reservation succeeds and before waiter/required/reuse mutation. Forward the already-available scalar mask, pre_required, pre_issued, pre_ready and pre_reuse. Do not add another `get`, Tag probe or directory lookup. Rejected/oracle-failed/duplicate requesters do not join the accepted denominator.

Definitions (successful live-merge requester events, never sectors or unique lines):

- previously_required_not_ready: `(mask & pre_required & ~pre_ready)!=0`; strict revisit to a sector already demanded by this transaction.
- newly_required_not_ready: `(mask & ~pre_required & ~pre_ready)!=0`; a new sector, not prior demanded-sector reuse.
- requested_issued_not_ready: `(mask & pre_issued & ~pre_ready)!=0`.
- all_requested_ready: `(mask & ~pre_ready)==0`, split exclusively into other-required-pending vs all-required-ready/response-drain.
- first reuse transition, and first reuse without strict pending revisit.

Strict and new-sector events can overlap for a multi-sector requester; do not add them as exclusive categories. Every fraction uses accepted_live_merge denominator. These statistics observe successful RO merges, not ingress or requests blocked at preview.

Actual sizeof88; 64-slice scalar state5632 bytes. Fixed-output design contract64KiB/application, no per-event dump. The production outputter is unimplemented; actual application output and host overhead are NOT measured. Overflow or invalid mask marks exact=false. No new simulator Core/ELF was built; CPU executables and object hashes are recorded independently.

## T joint hook: design only

D's P1 touches preview/backend semantics. Main must integrate any correction and measurement in one reviewed Source; this agent did not edit that production file or import D's patch.

At the actual first-head/preview event, consume ALREADY-COMPUTED raw probe, UID, epoch/generation, target slice/set, R and final decision. Record raw Tag status separately from virtual RO/relief-adjusted status, actual frontend denial/admission, backend probe, relieve/detach and subsequent accept. Preserve ordinary/RO classification.

Structural eligibility must remove only the T enable bit while preserving attached state, reuse_seen, required-not-ready, owner/line/generation binding, and actual pin/protocol guards. `can_detach` includes T, so it cannot serve as a T-independent observer predicate. No added set scan, probe, bank operation or directory lookup is permitted.

One bounded design maintains observer-only per-set eligibility shadows at already-existing admit/merge/fill/detach/retire and Tag bind/unbind mutations. A shadow may be exact only after all predicate-changing mutations and same-tick ordering are verified. Missing hook, generation mismatch or overflow invalidates exactness; it must never affect admission or mechanism resources. State sizing and implementation are still UNKNOWN.

Current-head-only dedup cannot claim lifetime-unique NEW if a UID can leave and reappear. Retain epoch/child identity and explicit overflow/right-censor policy for any bounded UID table. Keep true parent push, sector-child arrival, queue_enter, first_head and admission separate; never recover arrivals by FIFO scans. T0 must still report structural opportunity, not a forced zero because execution is disabled.

Minimal joint output: independent NEW R0..Rways, ever-full, raw-full and structurally-eligible for the same UID/set/tick, ordinary/RO, T enable, actual frontier result. Synchronize D's diagnostic consulted/intermediate fields before qualifying any corrected Source.

## Normal+RO address union: conditional design only

Current RO peak_independent_lower_lines is distinct `issued & ~ready` line population. Normal-MSHR peak is another population; do not sum separate maxima. An exact simultaneous union would maintain event-driven per-slice normal and RO pending line refcounts with generation and overflow-invalid handling, distinguish unissued and ready/draining states, and collapse multiple RO instances of one line. This is NOT implemented or needed to first test T causality.

## NI matrix

| Path | Actual evidence this round | Remaining |
|---|---|---|
| RO module M1T0/M1T1 + scalar counter | four runs/two OFF-ON semantic pairs; real D512, reference payload | production hook/full rebuild, partition OFF/ON, application OFF/ON |
| Source78 16x8 T0/M1 | real partition legal block/progress/drain CPU | formal mode Host, input eligibility and native scope |
| Source78 16x8 T1/M1 | identity, reordered sectors, ReturnQ backpressure CPU | new observer NI and any new Source qualification |
| S | no RO runtime; RO-only counter N/A | if common NEW/ingress hooks enabled, S-specific CPU/application NI |
| WV | RO merge hook should be dormant, not blanket NI | common hooks require WV NI; FWT remains WV, not RO-F |
| new-Source F-minus-T/F | no scientific ELF built | affected-path correctness, exact same-ELF mode controls, fresh scoped budget |

Old Vector4M ET NI covers only old ET, not this candidate, Vector6M, S or WV. Module NI is not application NI. Full application starts=0. Each enabled new mode needs its own same-new-ELF OFF/ON controls; no old-binary inheritance.
