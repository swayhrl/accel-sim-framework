# Initial8 controlled-Oracle analysis: fixed31 accepted snapshot

**31 runtime strict/true164/native-restoration accepted cells; seven complete four-cell inputs. This is a preliminary initial8 result, not a completed CORE32 result. Independent full-archive I/O review remains a separate status.**

The external single pass naturally closed with31 completed rows and errors0. Its FINAL status is ALL_FIXED31_CLOSED_VERIFIED_PASS_COMPLETE_NO_SCIENCE_RELEASE. This analysis consumes the working S v2 snapshot at 2026-11-06T16:59:07Z and its SHA-named immutable kernel facts, using the unchanged D0619-reviewed M analyzer. It reads no raw logs and performs no model, owner, tracer, registration, ledger, Git or watcher action.

## Exact coverage

- Initial8:31/32 cells accepted;7/8 inputs have accepted OFF/M/L2/L1. All three Oracle modes have8 accepted inputs, but only7 can pair with accepted same-build OFF.
- Fixed CORE32 denominator remains32:7/32 complete inputs and31/128 cells. The remaining24 inputs/96 cells are unregistered CPU drafts. No31-cell or7-program GM is called a complete CORE32 result.
- Scan has three accepted Oracle rows and no accepted OFF in this frozen snapshot. No historical DH0 is substituted.

## Actual cycles

| Program | OFF | M_DATAREAD | L2_DATAREAD | L1_DATAREADY |
|---|---:|---:|---:|---:|
|2DCONV|462,740|227,406|387,960|227,373|
|GEMM|826,089|697,878|826,089|742,072|
|convolutionSeparable|800,572|321,480|364,110|320,659|
|scan|NOT ACCEPTED|2,090,347|2,164,410|2,075,101|
|ATAX|31,880,220|4,862,254|11,628,526|1,714,624|
|MVT|34,687,540|4,862,254|12,184,082|1,714,624|
|BICG|28,685,812|4,861,661|11,242,893|1,715,343|
|vectorAdd|217,305|57,508|90,979|53,613|

## Same-seven-input normalized comparison

S=actual matched OFF/Oracle; H=1-Oracle/OFF. Positive, zero and negative responses are retained. All three GMs below use the identical seven-input accepted intersection.

| Mode | GM S (n=7) | Faster/equal/slower vs OFF | Initial8 matched coverage | CORE32 matched coverage |
|---|---:|---:|---:|---:|
|M_DATAREAD|3.485977833|7/0/0|7/8|7/32|
|L2_DATAREAD|1.992647166|6/1/0|7/8|7/32|
|L1_DATAREADY|5.457594237|7/0/0|7/8|7/32|

| Program | M S / H | L2 S / H | L1 S / H |
|---|---:|---:|---:|
|2DCONV|2.034863 / 50.8566%|1.192752 / 16.1603%|2.035158 / 50.8638%|
|GEMM|1.183715 / 15.5202%|1.000000 / 0.0000%|1.113219 / 10.1705%|
|convolutionSeparable|2.490270 / 59.8437%|2.198709 / 54.5188%|2.496646 / 59.9463%|
|scan|UNKNOWN / UNKNOWN|UNKNOWN / UNKNOWN|UNKNOWN / UNKNOWN|
|ATAX|6.556675 / 84.7484%|2.741553 / 63.5243%|18.593126 / 94.6217%|
|MVT|7.134045 / 85.9827%|2.846956 / 64.8748%|20.230406 / 95.0569%|
|BICG|5.900414 / 83.0520%|2.551462 / 60.8068%|16.723076 / 94.0202%|
|vectorAdd|3.778692 / 73.5358%|2.388518 / 58.1330%|4.053215 / 75.3282%|

## Suite coverage and GMs

| Suite within initial8 | Matched/population | M GM | L2 GM | L1 GM |
|---|---:|---:|---:|---:|
|CUDA Samples|2/3|3.067566215|2.291649397|3.181107065|
|PolyBench/GPU|5/5|3.668908588|1.884270714|6.772833923|

These are CUDA Samples2/3 (scan unpaired) and PolyBench/GPU5/5 for initial8 only. In the fixed CORE32 suite populations the corresponding paired coverage is CUDA2/9, PolyBench5/8, Parboil0/7 and Rodinia0/8. No coverage gap is silently removed.

## Kernel evidence

There are33 actual OFF/Oracle kernel pairs across the seven inputs, preserving ordinal, repeated names, active instructions and CTA work. All33 are faster or equal to their matched OFF; GEMM/L2 is the sole exact-zero kernel pair. The complete per-kernel table and as-printed counters are in MATCHED_KERNEL_COMPARISONS.json.gz; counters are not automatically differenced or interpreted as reset.

- convolutionSeparable distinguishes horizontal Rows and vertical Columns. OFF365,625/434,947 becomes M192,666/128,814, L2193,483/170,627, L1192,649/128,010. The vertical phase responds more, while M andL1 end almost equal. This is phase-local association, not a uniquely proved queue bottleneck.
- ATAX/MVT first kernels dominate their OFF totals:30,226,439/33,032,429 cycles respectively. L1 first-kernel cycles are1,185,017 for each; second kernels are529,607. Their unique input SHA/UUID and complete work remain separate. BICG strong response occurs in its second kernel27,030,465 to1,185,651; first kernel1,655,347 to529,692.
- The same accepted input/work does not imply identical cross-warp global issue order. Changed overlap and cache history are part of these controlled scenarios.

## Positive, exact-zero and non-monotone observations

1. ATAX/MVT/BICG show the largest L1 controlled responses:18.5931x/20.2304x/16.7231x. OFF DRAM reads are19,387,556/20,574,896/17,688,864 atoms; the three Oracle modes show0. Yet OFF average PIB occupancy is only about1.59–1.68 entries/SM, so these facts do not establish PIB128 capacity saturation. M improves5.90–7.13x despite increasing real lower-parent counts to about17.31M; request count alone does not determine cycles.
2. GEMM is a useful exact-zero L2 control:OFF andL2 both826,089 cycles. OFF already has0 DRAM read/write atoms and all1,716,504 physical L2 read accesses HIT. L2 virtual exposure1,716,504 is positive, so zero response is not simply an inactive mode. It is consistent with retaining the original hit/port/transport service.
3. GEMM is also non-monotone across Oracles: M697,878 is faster than L1742,072 by44,194 cycles. L1 remains1.1132x faster than OFF, but is about6.33% slower than M. L1 records2,004,120 new physical allocations versus M438,108/OFF429,126; pending hits fall to0 and Tag evictions rise. These facts associate changed reuse/overlap/allocation history with the reversal; they do not isolate its cause or justify clipping the result.
4. 2DCONV and convolutionSeparable show little further M-to-L1 improvement (33 and821 cycles), despite much smaller L1 PIB averages. Their L2 responses are weaker than M/L1, particularly2DCONV1.1928x versus about2.035x. This distinguishes retained pipeline/transport effects from a claim that free PIB occupancy automatically yields more throughput.
5. vectorAdd retains0 valid/pending OO hits and375,000 new misses in all modes. Its3.7787x/2.3885x/4.0532x M/L2/L1 responses are controlled read-service effects, not a newly demonstrated Tag-reuse benefit. Logical stores remain; DRAM write counts vary with scheduling/cache behavior and are not independently attributed.

No whole-program Oracle is slower than OFF in these seven inputs; this absence is reported rather than manufacturing a negative. The GEMM M-to-L1 reversal and the exact-zero L2 case are retained as important controls.

## Mechanism and missing-data boundaries

- M retains original ICNT-full local admission and finite lower-create/inject, then returns at most one32B sector per cluster/core tick, earliest next tick, through the bounded original receiver. It is not an infinite-bandwidth memory system.
- L2 retains routing, sectorization, finite L2 bank/port/return service and reverse ICNT. Eligible virtual-hit service occurs before normal physical cache.access. Thus a source-derived physical L2 read-stat count0 does not mean no request traversed L2; its separate virtual_hit_served/exposure and real lower/network evidence must be kept.
- L1 creates generation-bound next-tick data-availability events after real Tag/physical admission, skipping eligible lower/refill work while preserving reference registration, finite notification/collect/WB/retire and dependencies. It is not literal all-Tag-hit hardware.
- Reported sparse TOTAL_ACCESS remainsnull and source-proven derived0 stays separate with its exact proof. Missing Tag-bank/physical-full/PIB-full/Ref-integral or matched-read-latency measurements are not assumed0. As-printed interval sums/occupancy correlations are not disjoint critical-path budgets.
- C1 historical real downstream/structural evidence remains in a separate field with old source/build identities. It neither fills OFF nor mixes into these Oracle GMs. No best-mode stitched GM, mathematical/monotone/additive upper bound, feasible equal-gain design or equal-area claim is made.

## Scan: accepted work, missing accepted OFF

Scan M/L2/L1 are accepted at2,090,347/2,164,410/2,075,101 cycles. Each covers all33 frozen kernels,1,963,460,720 active instructions and166,608CTA, with the same ordinal/name/instruction/CTA sequence as the historical frozen DH-P0 derived proof. This is an identity/work check only; historical cycles do not enter S/H.
The Main-supplied16:50UTC observation described OFF running with progress.completed1,931,680,721 and phase_epoch133. Fixed Framework027 proves completed is gpu_tot_sim_insn+gpu_sim_insn, a cumulative instruction count; phase_epoch counts phase transitions, not kernel ordinal. It cannot be compared with Oracle GPU cycles or used as an accepted cycle/ETA/progress-ratio claim. Main subsequently reported natural OFF DONE at17:02UTC, but strict/accepted RESULT/archival qualification was not part of the frozen31 snapshot. This package remains31; any accepted32nd row requires a new analysis version after its authorized checks.

## Evidence and review scope

EXTERNAL31_FINAL.fixed.json and FINAL_ANALYZER_RUN_RECEIPT.json pin the completed pass and its binding to all31 S result SHA/UUID/cycles. closed31_analyzer_output_v1/inputs contains the immutable S snapshot, frozen matrix/settings and SHA-named derived kernel facts. INITIAL8_FIXED31_SCIENTIFIC_SUMMARY.json retains all population/coverage/suite metrics; CELL_IDENTITIES_AND_MECHANISM_EVIDENCE.json links each cell and its counters. The D0619-reviewed analyzer is unchanged.

This is runtime strict/archive/native acceptance plus read-only analysis. D’s separate full true164/native I/O verification must not be presented as complete before its own receipt. No driver/model rerun, new source/binary, owner/tracer recovery, registration of96 rows or watcher change occurred. EnglishLaTeX v0.23 remains frozen.
