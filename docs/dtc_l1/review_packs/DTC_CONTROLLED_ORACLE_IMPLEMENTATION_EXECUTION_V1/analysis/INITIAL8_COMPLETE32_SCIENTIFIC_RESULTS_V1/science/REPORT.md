# Initial8: complete32-cell controlled-Oracle scientific analysis

**All8 predeclared inputs now have accepted same-build OFF/M/L2/L1:32/32 initial cells,24 program pairs and132 kernel pairs. This is8/32 programs and32/128 cells of the fixed CORE32 goal, not a completed CORE32 suite.**

Tail1 naturally completed under its original UUID and passed strict, true164 archive and native restoration. The frozen32 snapshot is from 2026-11-06T17:15:47Z. This new package preserves the prior31-cell package unchanged (manifest059db88c206c20b9c6bfb660508a81b112db728a235bfb53fd932a3f08c9795c). The original D0619-reviewed analyzer passes identity/kernel-work checks on32/32 rows with0 raw-log reads and0 model/owner/tracer/dataworker/watcher/Git operations.

## Uniform eight-input comparison

S=actual matched OFF/Oracle; H=1-Oracle/OFF. Every mode GM below uses the same eight accepted inputs, with no best-mode selection.

| Mode | GM S, same8 | Faster/equal/slower vs OFF | Initial coverage | CORE32 coverage |
|---|---:|---:|---:|---:|
|M_DATAREAD|3.446285318|8/0/0|8/8|8/32|
|L2_DATAREAD|2.103432831|7/1/0|8/8|8/32|
|L1_DATAREADY|5.106115891|8/0/0|8/8|8/32|

| Program | OFF cycles | M cycles / S / H | L2 cycles / S / H | L1 cycles / S / H |
|---|---:|---:|---:|---:|
|2DCONV|462,740|227,406 / 2.034863 / 50.8566%|387,960 / 1.192752 / 16.1603%|227,373 / 2.035158 / 50.8638%|
|GEMM|826,089|697,878 / 1.183715 / 15.5202%|826,089 / 1.000000 / 0.0000%|742,072 / 1.113219 / 10.1705%|
|convolutionSeparable|800,572|321,480 / 2.490270 / 59.8437%|364,110 / 2.198709 / 54.5188%|320,659 / 2.496646 / 59.9463%|
|scan|6,648,993|2,090,347 / 3.180808 / 68.5614%|2,164,410 / 3.071966 / 67.4476%|2,075,101 / 3.204178 / 68.7907%|
|ATAX|31,880,220|4,862,254 / 6.556675 / 84.7484%|11,628,526 / 2.741553 / 63.5243%|1,714,624 / 18.593126 / 94.6217%|
|MVT|34,687,540|4,862,254 / 7.134045 / 85.9827%|12,184,082 / 2.846956 / 64.8748%|1,714,624 / 20.230406 / 95.0569%|
|BICG|28,685,812|4,861,661 / 5.900414 / 83.0520%|11,242,893 / 2.551462 / 60.8068%|1,715,343 / 16.723076 / 94.0202%|
|vectorAdd|217,305|57,508 / 3.778692 / 73.5358%|90,979 / 2.388518 / 58.1330%|53,613 / 4.053215 / 75.3282%|

| Initial8 suite | Paired/population | M GM | L2 GM | L1 GM |
|---|---:|---:|---:|---:|
|CUDA Samples|3/3|3.104858368|2.526800173|3.188778864|
|PolyBench/GPU|5/5|3.668908588|1.884270714|6.772833923|

The full CORE32 denominators remain CUDA Samples9, PolyBench/GPU8, Parboil7 and Rodinia8. This snapshot supplies3/9,5/8,0/7 and0/8 respectively; it supplies no Rodinia/Parboil Oracle conclusion. Remaining24/96 cells are still unregistered CPU drafts.

## New accepted scan data and actual kernel phases

Scan OFF is now **6,648,993 accepted cycles**, UUID b1e1d2b8-4359-46d2-af61-65844b889b70, RESULT SHA15c4aa5cc3e985ab63bd74e75eb6f081f980f1d99b96c5999875d01715947f0a. No historical OFF was used. M/L2/L1 are2,090,347/2,164,410/2,075,101 cycles: S3.180808/3.071966/3.204178 and H68.56145%/67.44755%/68.79075%.

All four scan rows cover the frozen33-kernel ordinal/name/work sequence,1,963,460,720 active instructions and166,608CTA. Actual kernel-cycle group sums follow; all individual ordinals and counters remain in MATCHED_KERNEL_COMPARISONS.json.gz.

| Scan kernel family | Instances | OFF cycles | M cycles | L2 cycles | L1 cycles |
|---|---:|---:|---:|---:|---:|
|_Z19scanExclusiveSharedP5uint4S0_j|17|4526869|1375672|1401337|1373708|
|_Z20scanExclusiveShared2PjS_S_jj|8|248231|62190|89525|50697|
|_Z13uniformUpdateP5uint4Pj|8|1873893|652485|673548|650696|

Earlier live progress.completed was cumulative instructions (gpu_tot_sim_insn+gpu_sim_insn), not accepted cycles; phase_epoch was phase transitions, not kernel ordinal. It was not used for S/H, an ETA or a progress ratio. These32-cell results come only from accepted complete input records.

## Key response controls and mechanism evidence

- Across132 matched kernel pairs there are no slowdowns versus OFF, and one exact-zero pair:GEMM/L2. This absence of negative OFF-relative results is retained honestly. GEMM/L1 is nevertheless slower than GEMM/M by44,194 cycles (742,072 versus697,878), despite both beating OFF. More aggressive data readiness is not assumed monotone.
- GEMM OFF andL2 both826,089 cycles. OFF already has0 DRAM atoms and1,716,504 physical L2 read hits; L2 virtual exposure is positive at1,716,504. Zero response is therefore not an inactive-switch claim. L1 new allocation events rise to2,004,120 versus M438,108/OFF429,126, with zero pending hits. Changed allocation/reuse/overlap is an observed association, not a proven unique cause of the M-to-L1 reversal.
- ATAX/MVT/BICG retain strong L1 responses18.5931x/20.2304x/16.7231x. Their dominant first/second GEMV phases and exact work remain separate despite some equal Oracle cycles. OFF average PIB occupancy near1.6 does not establish PIB128 saturation; M gains despite higher parent-request counts. No request-count-only causal explanation is asserted.
- convolutionSeparable still distinguishes horizontal/vertical phases;2DCONV and convolution show only33/821 cycles further improvement from M toL1. VectorAdd still has0 effective/pending OO hits and375,000 new misses. The unchanged31 report contains these detailed counter associations; this32 package retains all current per-cell and per-kernel evidence without altering that history.

Prior31 mechanism report: /root/share/mnt164/huangrulin/host174_storage_recovery/dtc_controlled_oracle_implementation_execution_20261106_v1/agents/M_initial8_closed31_scientific_analysis_v1/REPORT.md, pinned by its immutable manifest059db88c206c20b9c6bfb660508a81b112db728a235bfb53fd932a3f08c9795c and scope reviewe2a4bd097d030c13295daeda62edb3faa3af1b5c90b640428404804b45d362c7.

## Scientific readiness versus engineering dispatch

All three actual ModeGate2 receipts now PASS, each reviewing its8 Oracle rows plus the same shared8 OFF controls (not48 unique models). SOURCE_AND_GATE2_PINS.json and actual_mode_gate2_receipts retain the full exact SHA-bound receipts. Scientific extension conditions are met. The remaining24/96 request is nonetheless not registered because the sole-owner engineering dispatch boundary remains unresolved; this analysis does not bypass lease/Main identity, create a dispatcher or release science.

D full-package true164/native I/O review and final independent analysis scope review remain separate statuses; the present runtime/ModeGate2 receipts are not presented as an already completed broader audit. The old31 and new32 packages remain distinct.

## Structural implications and limits

1. First finish the already-authorized uniform CORE32 extension after Main resolves legitimate execution identity. Existing8 deliberately cover controls and opportunities; they do not establish all32-program rankings.
2. For ATAX/MVT/BICG, use closed request/phase evidence to investigate lower-service dependency and lifetime behavior rather than equating the low average PIB occupancy with capacity pressure. A feasible architecture must preserve dependencies and pay real traffic/latency costs; it cannot claim the Oracle gain for free.
3. For GEMM, prioritize preserving useful pending reuse and safe Tag/physical lifetime behavior under changed fill pacing. The allocation/churn reversal is a testable hypothesis. CPU/source studies are possible from present evidence; a new mechanism/Core or model experiment needs separate scientific scope, and historical1024-Tag safety-HOLD is not reopened.
4. For2DCONV/convolution/scan, examine finite notification, collection/WB and transport overlap with existing counters first. Missing Tag-bank/full-pressure or matched latency counters remainnull. New observation hooks or combinations require isolated qualification and separate execution authority; they are not auto-launched here.

M retains original ICNT-full local admission and one32B return/cluster/core-tick limit. L2 retains real routing/bank/port/return timing, and virtual service is distinct from physical cache stats; source-derived physical read0 does not mean no L2 request. L1 uses next-tick generation events after actual Tag/physical admission and retains finite reference/notify/collect/WB/retire. Queue/event/port and storage changes are counterfactual resources, not free or equal-area hardware.

C1 historical real structural results stay separate from C2 Oracle data and never replace current OFF. Reportednull remainsnull; separately source-proven derived0 retains proof. Per-kernel counters are as printed, without invented reset/delta semantics. Oracle cycle differences are not independent additive time budgets, mathematical upper bounds or guaranteed implementable DTC gains. Capture ELF/HtoD/numerical limits remain. EnglishLaTeX v0.23 is unchanged.
