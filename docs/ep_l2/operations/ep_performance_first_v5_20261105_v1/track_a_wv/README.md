# V5 Agent A: costed W/V candidates and matched request

Research engineering only: no application model, scientific start, budget registration, Native route, old Source, old Spec/raw or public registry was changed.

## Decision and evidence

Two independent candidates remain, at different readiness.

A-COLD is a one-bit lifetime-never-installed TVD negative proof gate. A private production Core and application ELF are built and bounded real partition CPU witnesses pass. It is a secondary query-service optimization, not a solution to Stencil's long-lived Victim retention problem.

A-RETENTION is the primary structural research direction but not application-ready: unified recency across optional CLEAN and WB_COMPLETE, respecting mandatory/pinned ownership and same-bank allocation. A precise serial-lane C++ engineering schedule is tested against the actual production directory API. At128 rows it pays128 scan cycles plus a distinct commit cycle. This conservative implementation is too expensive to promote to a long application experiment without further evidence. The old one-cycle128-row selection model was withdrawn; a127-comparator parallel selector needs its own explicit cost/timing contract.

The accepted low-Tag Stencil WV small metrics contain875,480 clean installs,1,501,832 dirty installs,4,930,426 read responses,6,497 promotions,7,310,059 directory query/wait observations,20,750 bank-wait and2,841 same-address-WB wait observations. End rows sum8192 (128 per64 slices), mandatory end0. WB extra retention36,159,115,085 slot-cycles versus clean2,559,882,593. These support studying useful CLEAN versus completed-WB retention, but do not identify a falsely evicted row or prove speedup. Bank-compatible-landing/WB-space blocked observations are0. Automatic same-bank reclaim already exists in Source78, so another simple bank-aware chooser would duplicate it.

V3 FWT WV G32x16 and G64x8 have zero clean/dirty installs and Victim responses, but16,320 directory queries and lookup waits. GEMM has zero installs and queries. Thus FWT is a useful short negative-query-cost witness; GEMM is not a useful first test. These are overlapping slice/request observations, not16,320 disjoint GPU cycles. G32x8 behavior cannot be inferred from G32x16. References and raw sums are in STENCIL_EXISTING_EVIDENCE_SUMMARY.json and EXISTING_SHORT_EVIDENCE_SUMMARY.json.

## A-COLD production implementation and actual cost

Private independent Core commit:7b4c06678923153006b0aa7d6b8ca9db4770cda9, parent Source78. Framework/vendor stay pinned. SOURCE5_CANDIDATE.json binds the complete identity, application ELF and library.

Flag -gpgpu_ep_l2_tvd_cold_filter defaults0. Effective option tables now have283 fields; old282-field contracts/consumers are preserved, never silently widened.

One physical sticky bit per slice is SET before any successful installation publishes a CLEAN/WB_STAGED row. Failed commits do not SET it. Dirty promotion requires an already existing row, so the bit must already be set. Reset occurs only at cache/directory construction. Reclaim, rollback, WB completion, epoch cleanup and flush never reset it, deliberately giving up later-empty-directory optimizations.

The bit is read alongside the existing Tag-miss stage, through the single serialized frontend (at most one check/request per physical cache cycle). No address CAM, data array, readiness oracle, extra ticket, completion port, Payload, Bank or buffering is added. The small gate/wire is folded into the Tag stage in this engineering model; it is not claimed free, zero-time or physically closed. If it cannot fit the existing clock, add a paid stage, which can erase benefit versus the old one-cycle query. First installation permanently restores original lookup/ticket/reader/WB/completion behavior.

Same-cycle producer ordering is SET-before-row visibility. A miss authorized by the cold proof cannot alias an older row; the single frontend cannot start a second request halfway through that producer commit. Future concurrent producers must explicitly preserve this ordering.

Bounded CPU evidence:
- Real G32x8 partition default-off:11 queries/0 bypass.
- Cold-on CLEAN and dirty-WB:2 queries/9 bypass each.
- Exact external response versions, bankP1, WAD identity, pending-WB wait, lower completion, flush/drain and no flag reset are asserted.
- Actual directory proofs cover failed commit, SET-before-visible, reader pin, mandatory WB, absent lower-data backing, stale ticket and rollback.
- Production parser/cache-constructor proof uses exact proposed application configs, zero commands/kernels. All three modes have exactly283 registered options, zero value mismatches, and successful cache construction. No application acceptance is inferred.

## A-RETENTION exact boundary

retention_cycle_model/reclaim_scheduler.h is a C++ schedule around the production directory, not a cache frontend implementation. It reuses the existing64-bit age per128 rows (8192 logical metadata bits), inspects one row per cycle using one row-read lane and64-bit comparator. Selected index/incarnation/age, cursor, bank and phase need about148 additional logical pending bits. Physical timestamp encoding and clock-domain crossing remain unproved.

A distinct shared update-lane cycle follows the complete scan, with generation/readers/status/bank/age rechecks. Busy read/update lanes wait; mandatory WB is never selected. The model has no allocator/lower-credit reservation or atomic cache producer integration. No hidden128-way comparator tree is assumed.

Three bounded C++ cases prove clean-priority versus unified-oldest choice, same-bank filtering, full scan latency, update backpressure, reader pin, stale generation and mandatory-WB exclusion. The earlier one-cycle selection result is explicitly withdrawn history. No scientific budget is requested for this incomplete policy. Avoiding completion's age refresh remains an unimplemented hypothesis.

## Exact independent request

request/EXACT_MATCHED3_REQUEST.json prepares3 starts, without authorization: FWT input fc3a90622744ba1f63bec264284983747a372e3a34543249c3977d4bd285fe2e; G32x8; DRAM850/L100/FR-FCFS128; new sameSource/sameELF S, WV-off and WV-on. The WV pair differs only in the cold-filter flag. S is a new matching control; old-ELF accepted S is context only. Ordered configs,283-field dictionaries, exact cohorts and input refs are frozen.

Each point: one start, wall3600s/RSS2GiB/AS10GiB/result128MiB. Estimates1200s/RAM1GiB/hot64MiB require dynamic admission. No retry/refund; SourceKEEP/floor5GiB/EPcap10/Main-owner/true164/fullSHA/two independent Native restores apply.

Remaining: Main Source review and mode/input rebind; new exact283-option consumer and Host43 contract; Native22+Host5 pins/boot/mount/resource mapping; explicit user scope and new independent budget. These are concrete gates, not grounds to repeat old large tests or add NI models.

Stop A-COLD after a zero/negative full-command absolute-cycle result or excessive cost. Do not claim Stencil gain after first install. Stop duplicate same-bank policies and uncosted broad empty-directory filters. Do not spend long Stencil starts on128-cycle on-demand scan without evidence that retention wins amortize the cost.

DELIVERY_MANIFEST.json binds code/patch/CPU/contracts/request. True164 private output holds the verified Git bundle and all builds/bulk logs. Accepted sources remain clean. Agent A did not publish Git or mutate shared scientific systems.
