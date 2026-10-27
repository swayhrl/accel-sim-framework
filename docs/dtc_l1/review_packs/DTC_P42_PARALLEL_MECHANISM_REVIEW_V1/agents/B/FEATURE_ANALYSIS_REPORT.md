# Independent memory features and observed DTC response

The complete-original-result panel contains 23 frozen trace identities out of 42 target ordinary programs. Classification uses qualified trace instruction/address properties and original accepted CH telemetry before joining DH outcomes. It does not classify an application as memory-bound from a speedup, and it does not certify full application capture or numerical correctness beyond existing admission evidence.

## Results that follow from independent observations

* ATAX K1, MVT K1 and BICG K2 each have 16 CTAs on the modeled 64-SM GPU: at most 25% of SMs can host one of these CTAs concurrently. These kernels account for more than 93% of original CH application cycles. This restricts potential latency hiding, but it is shared by CH and DH and **does not by itself explain their difference**.
* Those same three complete strided kernels show roughly 16.5 distinct 128-byte lines per cacheable global-load warp record: alternating lane-broadcast/vector loads and 32-line matrix loads. Full address scans confirm adjacent active-lane matrix address differences of 16,384 bytes. ATAX/MVT each touch 524,544 distinct 128-byte load lines; BICG touches 524,416. Static global-load line-event revisit factors are 32.984/32.984/32.992. Most within-warp repeated-line event-index gaps lie in [32,63]. These are strong coalescing/locality features, not proof of L2 conflict replacement or duplicate outstanding requests.
* CH L2-ready-hit dominated request streams (>=80% of accepted global read sectors) occur in 17/23 programs. Their observed CH/DH GM is 1.099928 with 15 positive and 2 negative cases. This describes where accepted CH reads are served, not the critical path; the groups overlap with other classes.
* The independent large-line-count mapping candidate rule selects ATAX/MVT/BICG; their CH/DH GM is 0.855661. They are all negative cases even though they have substantial static line revisit. Revisit alone therefore does not predict DTC advantage. The rule describes lane coalescing amplification; it intentionally does not detect every possible cache-set conflict pattern in 3MM/GEMM.
* SFU-dense qualified traces are BlackScholes, heartwall and MRI-Q (MUFU >=1% of warp records); CH/DH GM is 1.011680. Opcode density is not a measured execution-time share or a causal explanation by itself.

## Positive cases and address coverage

2DCONV's first 16 MiB prefix contains 155,787 global-load line events and 10,683 distinct 128-byte lines (14.583 revisit factor). Active neighboring lane addresses differ by 4 bytes. In the complete qualified body, global-load warp records are exactly nine times global-store warp records, consistent with its neighborhood-load kernel; most loads touch one or two lines per warp. The prefix within-warp repeated-line event gaps are 1 to 3. These observations support strong short-range serialized reuse in the observed prefix; they neither prove full-grid global reuse nor establish the exact simulator service mechanism responsible for its large benefit.

3MM K1 and GEMM K1 each received the same bounded 16 MiB prefix budget: 8,590/8,444 distinct lines and revisit factors 16.859/15.021. Their qualified global-load coalescing is predominantly one line per warp record, despite known observed Hash response. This is why static lane-coalescing metrics and actual Hash response must stay separate. Prefix addresses are not a random or complete sample, and no whole-application unique-line count is claimed.

All six scanned cases pass the predeclared >=4 revisit factor threshold; their CH/DH GM is 1.354589, with 3 positive and 3 negative. **This is a diagnostic, deliberately selected six-case group with mixed full/prefix address coverage; its GM is not a general high-reuse population claim.** The other 17 programs were not address scanned and are missing, not low-reuse negatives. 3DCONV does not pass the available candidate thresholds and remains insufficiently classified; its positive performance is retained.

## Scope and missing evidence

Application traffic uses existing strict aggregate counters. This report does not assign application L2/DRAM bytes to a kernel by dividing proportional to cycles or instructions. Per-kernel accepted read/miss counters, simulator request identities, L2 replacement events, timestamped traffic bursts, achieved SM occupancy, and true LRU stack reuse distances are absent from this product. DRAM read atoms include all modeled read types while the available L2 denominator is global-read sectors; this domain difference is explicitly marked. Min/max address span includes gaps between allocations and is not allocation footprint. Arithmetic fractions include integer address/control arithmetic and do not mean compute time dominance.

Every matrix row retains full input SHA, original CH cohort/UUID/accepted receipt state, original raw and strict paths/hashes, actual Core/Framework/binary, configuration hash, qualified per-kernel trace path/SHA and denominator. Four-cell original accepted cycle identities are joined separately after feature freezing. CM/CH and DM/DH are observational Hash responses, not classification inputs. Repair verification, failure, HOLD and pending cells never fill missing original results.

## Scan execution and receipt correction

One sequential producer read 405,199,005 trace bytes in 173.63 seconds, with peak RSS 75,444 KiB, nice 19 and a 1 GiB address-space hard cap. Limits were 1 GiB total trace bytes, 15 minutes and 8 MiB/s cumulative trace read rate. No event stream was retained. Three strided kernels were fully scanned and their whole-file SHA rechecked; three positive-case scans intentionally stopped at a 16 MiB prefix. Metadata-only completed-warp count correction preserves original 127 receipts and corrects the full-kernel count to 128 with an explicit audit trail; no trace was rescanned. See ADDRESS_METRIC_NOTES.md and shared_address_index/RECEIPT_CORRECTION.json.

## Most valuable next evidence

1. Read-only source counter-semantics comparison and existing per-kernel closed-raw extraction can refine which request population actually reaches L2; no new simulation is needed.
2. Exact distinction among L2 replacement, separately outstanding duplicate requests and request timing requires matching line/request/generation identities plus accepted enqueue/service/return events. If existing logs lack them, a minimal instrumentation-only experiment needs NEW_SCIENTIFIC_EXECUTION_APPROVAL_REQUIRED. Do not infer it from static repetition.
3. Complete, strictly accepted current P0/PQ/PS results should be joined by the coordinator when available; early phases cannot replace whole-application final cycles. This producer never accesses their active raw files or control plane.

Reference science packet commit: 71584878be0c80375f9d25bcd80e171b7bf4478d, docs/dtc_l1/review_packs/DTC_PAPER42_HASH_REVIEW_20261027_V1/. English v0.23 remains unchanged.
