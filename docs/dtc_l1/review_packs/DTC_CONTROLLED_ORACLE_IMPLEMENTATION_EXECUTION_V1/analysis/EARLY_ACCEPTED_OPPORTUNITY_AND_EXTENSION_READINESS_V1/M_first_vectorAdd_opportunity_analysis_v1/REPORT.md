# vectorAdd: first three accepted controlled-Oracle rows

This is a read-only analysis of **three completed raw logs for one frozen input**, not a suite result. All three SourceRows are `PASS_CONTROLLED_ORACLE_DH_STRICT_ARCHIVE_NATIVE_RESTORE`, with natural completion, accepted strict evidence, SOURCE_KEEP, true164 archive and native restoration receipts. The analysis checked each restored raw gzip and uncompressed SHA against its accepted proof; it did not rerun a model, re-register an identity, edit a ledger, modify Core or commit Git.

## Matched identity and measured opportunity

Input `e7bb67e63e3c38478ff50db4dcc25dee9262fe195b30589547b1ac5e2bc3d799` is the frozen vectorAdd_6000000 capture. Its recorded A/B buffers are24MB each, grid23438x256 with tail predication. Exact capture executable linkage and full numerical correctness remain uncertified. Each accepted row runs the single kernel `_Z6VecAddPKfS0_Pfi`, ordinal1,84,000,768 active instructions and23,438CTA. The original270 options are identical; only enum0/1/3 differs.

| Mode | GPU cycles | S=OFF/mode | H=(OFF-mode)/OFF | UUID |
|---|---:|---:|---:|---|
| OFF_MATCHED |217,305|1.000000|0.0000%|c5dda178-aa29-45b7-9fc1-1638d67c14b8|
| M_DATAREAD |57,508|3.778692|73.5358%|54d2c391-2daa-434b-9def-4723a5bef90c|
| L1_DATAREADY |53,613|4.053215|75.3282%|231c2aef-80c7-4d95-859c-2bacfadf488c|

L1 uses3,895 fewer cycles than M: M/L1=1.072650, or6.7730% fewer cycles relative to M. This difference is **not** an independent/additive refill-latency budget. L2 Oracle is not included in this three-cell analysis.

All rows use Core `e6b41ab8992e7d41651501c4d34cfe24195c4f96`, Framework `02775fd795cde5aae1480d81cee6eb481d0a08f4`, executable SHA `3f8e547d87893aaf7319e337883a2bcc1f5717138296e3e6d1425cc75d055283`, and libcudart SHA `174f53a02223ae69e4a549e60a310f7e69a9334748e719fd48c40640c2a0af43`. Historical DH-P0 was not substituted for matched OFF.

## Runtime facts

| Counter / unit | OFF | M | L1 |
|---|---:|---:|---:|
| OO valid / pending hits |0 /0|0 /0|0 /0|
| OO new line misses |375,000|375,000|375,000|
| Tag evictions |342,232|342,232|342,232|
| Real lower parents created/issued/closed |375,000 each|375,000 each|0 each|
| M virtual parents /32B sectors closed |0 /0|375,000 /1,500,000|0 /0|
| L1 virtual events enqueued/delivered |0 /0|0 /0|375,000 each|
| DRAM read atoms (32B) |1,500,000|0|0|
| L2 read TOTAL_ACCESS, actually printed |1,500,000|null|null|
| Separate source-proven derived L2 read count |not needed|0|0|
| L2 accepted write sectors |750,000|750,000|750,000|
| DRAM issued write atoms (32B) |633,008|403,846|404,578|
| Load/store warp-operation counts |375,000 /187,500|same|same|
| Finite collected sectors / retired loads |1,500,000 /375,000|same|same|

M emits64 cluster counter rows. All375,000 parents close once with1,500,000 required/enqueued/received sectors, zero pending parents and zero recorded M return-FIFO-full stalls. Per-cluster pending-parent peaks range94–107. **This does not prove original ICNT admission never blocked:** that count is not exposed here. M retains original ICNT-full admission and local lower-create/inject quotas, then a finite RR sequencer returns at most one32B sector per cluster/core tick, earliest next tick. L1 instead creates one next-tick generation-bound full-line availability event after normal Tag/physical admission, skips real lower/refill work, and retains finite frontend notification/collection/WB/retirement. These are different controlled mechanisms.

No measured valid/pending OO reuse appears even under either Oracle. The speedup therefore does not demonstrate a newly created Tag-hit or merge benefit. It accompanies removal of the eligible downstream read service and reduced outstanding instruction occupancy. OFF's1.5M L2 read sectors all miss and1.5M DRAM read atoms are issued. The experiment changes transport/L2/DRAM and overlap together; it does not isolate DRAM latency from all queues.

Logical stores remain187,500 warp operations/6,000,000 lane stores;750,000 L2 write sectors remain in every row. DRAM write totals nevertheless differ. These are observed cache/order/combining/drain-sensitive outcomes, not proof that store semantics were removed or that a write optimization was separately measured. Do not compare the leftover real-traffic maximum latency in M/L1 with OFF as a matched eligible-read latency distribution.

## Finite service and resource observations

| Derived quantity | OFF | M | L1 |
|---|---:|---:|---:|
| Average PIB entries per SM |59.4348|21.1737|0.7440|
| Average allocated physical lines per SM |483.2908|450.9253|448.8682|
| Ready-to-complete interval per retired load |2.16164|3.06217|2.25165|
| Ready-to-collect interval per retired load |1.08978|2.03862|1.22737|
| Collection interval per retired load |1|1|1|
| Post-collection wait sum |26,947|8,830|9,108|

Occupancy means divide the printed integrals by printed SM-cycle samples; every sample total equals64xGPUcycles. They do not reveal peak saturation. Allocated physical lines include retained valid, Ref-free data, so occupancy is not a physical-full stall measurement. At termination activeRefs, PIB occupancy, inflight and lower outstanding are0;32768 retained allocated lines are not liveRef leaks. All375,000 completion dependencies close.

Finite collection work remains1.5M sectors. Its printed interval decomposition satisfies ready-to-complete=ready-to-collect+collection+post-collection wait, but these are summed per-entry service intervals, not disjoint global critical-path cycles. M's interval grows despite its large total speedup; this is compatible with changed overlap and does not establish completion service as the new dominant bottleneck.

OO Tag-bank requests/conflicts, no-free-physical events, PIB-full stalls, activeRef time integral/peak, pereligible-read latency and original M ICNT-full admission stall counts are unavailable and remainnull. Raw DRAM refresh data also retains its inherited uninitialized-field limitation. None is interpreted as0.

## Missing versus derived-zero policy

M/L1 genuinely omit GLOBAL_ACC_R:TOTAL_ACCESS. The installed postprocessing source is **V3 `dc00fb7a0435c85dd0b377ead470df58ce9127d6bc1ef32b7ec69ad5a5885c6d`**, not the rejected UNVERIFIED nullable candidate. The reported totals and payload bytes remainnull. A separate proof derives0 from all13x7 printed access states,40 bank totals, aggregates and exact source identities, with overflow/partition guards. Both cases have750,000 total accepted L2 accesses, all attributable to writes, zero read-state sum and printed zero DRAM reads. No raw line or generic missing-to-zero replacement is fabricated.

## Interpretation and next-use boundary

This is genuine observed **controlled-model read-service opportunity** for this input:3.78x/4.05x under two precise counterfactuals. It suggests prioritizing downstream read-path latency/concurrency and physical/PIB lifetime overlap hypotheses rather than claiming a Tag-reuse gain for vectorAdd. It neither proves an implementable DTC can attain this gain nor establishes a mathematical upper bound, free hardware benefit, compute-only residual or CORE32 result. Retained stores, instruction issue, finite service and dependencies all remain. Missing bottleneck counters constrain finer attribution; first consume the remaining already-authorized matched results before proposing any new experiment.

`VECTORADD_THREE_CELL_ANALYSIS.json` contains exact ratios, original metrics, explicitnulls and raw line evidence. `SOURCE_ROWS_AND_SELECTED_RAW.json` retains only derived selected excerpts and accepted SourceRows; full raw logs remain at their original/native-restored locations. `SOURCE_AND_RECEIPT_PINS.json` gives paths, archive receipts, input identity and source SHAs; `CLAIMS_AND_EVIDENCE_LEVELS.json` separates facts, associations and unknowns. EnglishLaTeX v0.23 is unchanged.
