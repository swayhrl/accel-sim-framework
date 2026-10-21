# Lane D: PRIMARY FOUR offline science for EN-v22

E authority is `ca2dbc456b061885b1c5e7503de91fc38a8e90c8`, review pack `MS20261021_E2_PRIMARY_FOUR_EXECUTION_r1`. D continues from `2789e3034493bb57a66948c77a67fdcb26bf6ef0` on its existing analysis branch. E remains the acceptance owner. This report consumes its frozen CURRENT_ACCEPTED declarations and exact endpoint hashes through the existing D readers; no E qualification gate is rerun. EN-v22 remains the sole manuscript; this pack contains proposed evidence and text only.

The decision-relevant result is a **five-MAIN subset GM of 0.9977331349× (−0.226687% speedup)**, including Vector's negative result. DWT's RO-enabled conditional regression occurs mainly after its RO-active kernel. Conv's service-exemption diagnostic changes stage timing in opposite directions and does not establish a hardware performance bound.

## Exact accepted deliveries and denominator

| New delivery | Attempt | Accepted cycles | Existing anchor | Pair ID suffix |
|---|---|---:|---|---|
| Vector F resource retry | E033_f01f6993 | 75,039 | E013_33cffb17 S, 73,696 | vectorAdd_4M_S_F_MAIN61_RESOURCE_RETRY |
| DWT WV = F_MINUS_R | E034_479739f1 | 166,718 | E018_67a874f4 F, 167,643 | dwt2d_F_VS_F_MINUS_R_MAIN61 |
| Conv S_L2_DATA_FREE | E035_d8a8279a | 293,531 | E010_1108e4d2 S, 292,932 | convolutionSeparable_S_VS_S_L2_DATA_FREE_MAIN61 |
| Conv F_L2_DATA_FREE | E036_6d4eee56 | 291,320 | E009_76e25c1e F, 291,469 | convolutionSeparable_F_VS_F_L2_DATA_FREE_MAIN61 |

Full pair IDs, acceptance publication SHAs, receipt/config/trace/qualification/run-key identities are in `FOUR_DELIVERY_IDENTITIES.json` and `ACCEPTED_ENDPOINT_IDENTITIES.json`. The four acceptance checkpoints and accepted-pair documents match E's final declarations; delivery receipt hashes match its published index. E's final state is 36/40 charged starts, four remaining, controller STOPPED; these are statements at the frozen authority, not a new live admission check. No execution or budget change is requested.

All five MAIN pairs use binary SHA256 `61aad385723ac97a76cb1f32c124b286a10bc8609c9c58b1a3ef8a87413f2dd5`, Core `d010911e3174a3764791183cd108fe4664ba8731`, Framework `9dd1ee57a83d83b56b7874bc7c716185ab52c8f7`, vendor `f90c430c3a1ce8f08c09942a5a1c3a797bb2295b`. Each pair retains its own complete input, selection, nonresearch invariants and exact configuration, not another application's certificate. Conv F uses E's revalidated accepted receipt, not the original failed E009 receipt.

| MAIN input | S cycles | F cycles | F−S cycles | S/F speedup | Instructions per endpoint |
|---|---:|---:|---:|---:|---:|
| Conv | 292,932 | 291,469 | −1,463 | +0.501940% | 714,547,200 |
| CFD | 79,093 | 79,157 | +64 | −0.080852% | 143,129,372 |
| DWT | 166,519 | 167,643 | +1,124 | −0.670472% | 148,684,429 |
| SAD | 110,773 | 109,754 | −1,019 | +0.928440% | 157,583,646 |
| Vector | 73,696 | 75,039 | +1,343 | −1.789736% | 56,000,000 |

Speedup is `100*(S/F−1)` and GM is `exp(mean(log(S/F)))`; neither averages percentages nor weights by cycles. Vector's **cycle increase** is +1.822351%, a different denominator. The five-subset GM is −0.226687% speedup. **Original seven-input GM is UNKNOWN**: FWT has no accepted complete MAIN pair; Btree remains HOLD. No missing input is assigned zero or 1×, and controls never replace MAIN F. Old four-subset GM remains historical, not the current five-subset headline.

## Vector: measured facts and localization limit

| Counter / observation | S | F |
|---|---:|---:|
| Logical copy reads / writes | 100,568 / 100,568 | 0 / 0 |
| Physical bank grants | 2,801,704 | 2,600,762 (−7.172135%) |
| V queries / actual V read responses | OFF / no V native records | 375,000 / **0** |
| V dirty-forward / promotion | OFF | 0 / 0 |
| V clean / dirty installs | OFF | 115,809 / 100,762 |
| V clean / dirty retention integrals | OFF | 161,907,096 / 363,176,659 slot-cycles |
| RO admitted requests / transactions / merges | OFF | 1,000,000 / 250,118 / 749,882 |
| RO line-MSHR allocations avoided | OFF | 250,118 |
| Successful Tag detach | OFF | **0** |
| RO lower sectors / concurrent duplicate sectors | OFF | 1,000,000 / 0 |
| RO real fill / response bank operations | OFF | 1,000,000 / 1,000,000 |
| All lower reads / read bytes | 1,000,000 / 32,000,000 | 1,000,000 / 32,000,000 |
| Lower WB bytes | 12,872,704 | 12,897,536 (+24,832) |
| WB created / lower accepted / completed | 100,568 each | 100,762 each |
| Final retained TVD payloads | 0 (disabled) | 8,192 |

OFF native V/RO fields remain UNKNOWN in machine-readable generic tables, rather than fabricated measured zeros. F's active zeros are actual counters. RO merges and allocation avoidance are exercised, but **do not reduce total lower read bytes** here; allocation avoidance is not measured saturation relief (line-MSHR-full waits are zero in both). Zero concurrent duplicate-sector events only describes the instrumented concurrent scope, not all temporal repeated reads. Retention without actual V reads is not a demonstrated reuse benefit; final retained occupancy is not a whole-run peak.

The existing complete snapshots give one named `_Z6VecAddPKfS0_Pfi` kernel: **73,557→74,928 (+1,371)**. Final accepted cycles minus named durations are **139→111 (−28)**. Thus +1,343 is localized to kernel execution, not an enlarged final residual; the residual is not asserted to be DRAM drain. There are no intra-kernel timing snapshots or request-dependency records in these observations. Exact warp/request/phase attribution within K1 remains **UNKNOWN**.

F's query wait observations are 375,000 V and 1,000,000 RO request-cycles (each maximum 1); bank-compatible landing has 14,508 first-blocked requests, 109,395 request-cycles, maximum 668. Conversely, data-service waits decrease 84,555→65,277, MissQ waits 1,131,061→818,741, and WB-data-space waits 460,461→0; copy waits 100,568→0. ANY-first-block-to-admission observations rise 1,762,049→2,275,296. These overlap across requests, slices and reasons and **are not an additive program-stall decomposition**.

**Source-derived interpretation**, retained from A2 review `04f255e4316d69eb773ca178b3349699958a1dde` and D's frozen source excerpts: V/RO query paths model latency, enabled V or RO activates stricter client/UID/generation retry matching, and a landing refusal bit can precede same-bank reclaim and a later service failure. Therefore S→F changes identity/state/control paths as well as copy service. A landing count alone does not prove a final slot shortage or extra physical port demand.

**Falsifiable hypotheses, not established causes:** paid queries and bank-compatible retention/admission timing may outweigh copy/WB-space relief when V yields no read reuse; the slightly higher WB count may alter downstream timing. The observed +24,832 WB bytes equal 194 additional 128B writes, and the bank-count decrease is 194 smaller than the 201,136 eliminated copy operations, but this arithmetic does not identify their criticality. Only an independently authorized exact-input control or existing request-order evidence could distinguish these explanations. This report requests no new run and does not claim all 1,343 cycles are lookup or landing stalls.

## DWT: accepted conditional chain and phase effects

WV means W+V with both RO controls OFF (`F_MINUS_R`). These are full-application endpoints, not chaining one run's state into another.

| Stage | S | W_ONLY | WV | F | F−WV |
|---|---:|---:|---:|---:|---:|
| K1 | 22,169 | 22,255 | 22,109 | 22,018 | −91 |
| K2 | 25,759 | 25,727 | 25,735 | 25,667 | −68 |
| K3 | 12,262 | 12,259 | 12,260 | 12,254 | −6 |
| K4 | 9,075 | 9,075 | 9,075 | 9,074 | −1 |
| K5 | 28,101 | 27,871 | 28,175 | 28,869 | **+694** |
| K6 | 12,260 | 12,263 | 12,244 | 12,252 | +8 |
| K7 | 9,074 | 9,074 | 9,075 | 9,075 | 0 |
| K8 | 26,496 | 26,938 | 26,711 | 27,095 | **+384** |
| K9 | 12,249 | 12,256 | 12,259 | 12,264 | +5 |
| K10 | 9,074 | 9,074 | 9,075 | 9,075 | 0 |
| Final residual | 0 | 0 | 0 | 0 | 0 |
| Total | **166,519** | **166,792** | **166,718** | **167,643** | **+925** |

The chain closes: S→W_ONLY **+273**, W_ONLY→WV **−74**, WV→F **+925**, total **+1,124**. K1 contributions are +86/−146/−91; K5 −230/+304/+694; K8 +442/−227/+384. For WV→F, K5+K8 cost **1,078**, K1 saves91 and other kernels save62: net925. K5/K8 are repeated `fdwt53Kernel<192,8>` launches; ordinals and matching launch UIDs prevent an incorrect name-only join.

Only K1 has F's 39,836 new RO admissions/queries, 9,965 transactions/allocations avoided and29,871 merges; successful detach is0. K1 becomes91 cycles faster, with landing-wait increments153,739→146,780. **No new RO admissions or queries occur in K5/K8.** At K5, WV→F changes V reads3,456→3,139, V queries68,375→68,107, bank grants470,170→470,467, lower reads128,583→128,788, WB bytes6,176,128→6,172,288. K8 V reads remain0 and queries65,536, lower reads remain131,072; grants457,723→457,729, WB bytes4,252,288→4,250,240. Landing-wait increments actually decrease724→718 and378→339. Direct query count or landing-wait growth in these stages therefore cannot by itself explain their regressions.

Whole-application WV→F has V reads24,216→23,305, lower read bytes11,737,696→11,749,312 (+11,616), bank grants2,172,767→2,173,230 (+463), identical WB bytes20,971,520. It changes transaction/retention/admission history before later kernels; earlier-state effects on later cache contents, WB ordering or memory scheduling are plausible. These data establish an **adverse conditional net effect of enabling the RO path in the W+V background**, including persistent state effects. They do not establish direct RO lookup stalls in K5/K8, a unique T versus M contribution, or an independently additive mechanism cost. W_ONLY→WV also activates strict retry matching; WV→F keeps that rule active on both sides. The original S/F bank-service and traffic reductions remain real despite negative total performance. Original E027/E028 RAM failures remain invalid; E031/E032 are separate accepted retries, not repaired historical observations.

## Conv: finite-residual service-exemption diagnostic

| Endpoint | Rows K1 | Columns K2 | Total | Diagnostic−P1 |
|---|---:|---:|---:|---:|
| S, normal P1 | 161,236 | 131,696 | 292,932 | — |
| S_L2_DATA_FREE | 162,221 | 131,310 | 293,531 | **+599 = +985−386** |
| F, normal P1 | 160,984 | 130,485 | 291,469 | — |
| F_L2_DATA_FREE | 160,198 | 131,122 | 291,320 | **−149 = −786+637** |

The diagnostic exempts data-service grants; physical bank grants and DATA_SERVICE wait observations become0. It retains finite payload/tags/descriptors/line-MSHRs/WAD/per-address limits, metadata queries, actual version/reference data, RO identity, dirty WB/ICNT/backpressure, real completion/response/ROP and **S's fixed copy latch**. It is distinct from S_COPY_FREE, whose separate +739-cycle adverse result remains preserved. The frozen E `FINITE_RESIDUAL_SERVICE_GATE` specifies the scope; D does not extend its native qualification or interpret exempt grants as physical zero-cost hardware.

For S, logical copy events persist: Rows252,901→252,479, Columns293,964→294,666; total+280. Rows lower reads are unchanged1,179,878, WB bytes fall54,016 and elapsed increases985. Columns WB bytes rise74,880, lower reads rise2, line-MSHR wait observations fall36,905→21,006 and same-WB waits638,854→615,035 while elapsed falls386. Whole-run WB-data-space waits rise848,913→1,063,566; the existing stage parser does not expose that reason per kernel, so its phase attribution remains **UNKNOWN** rather than inferred from the total.

For F, Rows saves786: RO admissions1,251,551→1,253,122, transactions371,495→369,609, merges880,056→883,513; V reads32→14; lower reads1,179,774→1,179,772. Columns adds637 despite no new RO admission/query: same-WB wait observations538,426→637,958, line-MSHR150,118→295,764, MissQ590,686→607,580, landing80,033→93,147; lower WB bytes37,438,400→37,530,624 and V queries591,187→591,759. V reads fall4→2. Whole-run lower reads change−24 and WB bytes+84,928. These are counter/phase correspondences, not exclusive causal stalls; finite resource contention and prior-state timing remain plausible explanations for the stage reversal.

The diagnostic net deltas are small compared with service-count removal and include adverse stages. **It is not a hardware performance upper bound, not a port-count projection, and not proof that physical banks can never matter.** Its S/F difference2,211 cycles is diagnostic only; MAIN remains1,463. Removing modeled services can retime resource acquisition and WB ordering rather than monotonically reduce elapsed time.

## Claim boundary and retained results

All five MAIN F runs report **zero successful Tag detach** in the final accepted 64-slice cumulative RO summary. This is an application-level counter boundary for these exact inputs/configurations, not proof of general unreachability or absence of benefit from the common RO path. Existing Conv T/M equal-cycle corners retain their different allocation/avoidance counts and nonadditive interaction; they do not establish functional equivalence or executed-detach performance benefit. CFD conditional gains and its slightly negative MAIN result both remain. SAD's zero-copy-prefix improvement remains unexplained; it is not assigned to copy elimination, V reuse or Tag detach.

Mechanism activation, service counts, request wait observations and elapsed GPU time are separate measurements. No causal stall shares, additive independent W/V/T/M benefits, workload-wide favorable generalization or hardware diagnostic bound is supported. All old failures, input HOLDs and negative controls are retained. No new workload is selected by its F performance.

## Evidence and reproduction

`MAIN_FIVE_PERFORMANCE.csv/.tex/.pdf/.png` is the paper MAIN input; `PRIMARY_FOUR_ELAPSED_STAGES.pdf/.png` and `VECTOR_MECHANISM_COUNTS.pdf/.png` expose conditional stage changes and active mechanism counts. Detailed inputs are `FOCUSED_STAGE_CYCLES.csv`, `KERNEL_TIMING_AND_MECHANISM_DELTAS.csv`, `ACCEPTED_STAGE_MECHANISMS.csv` and `ACCEPTED_PAIR_TERMINAL_MECHANISMS.csv`. English candidates and the claim audit are separate files.

Existing `sync_intake.analyze_pair`, `full_v2_analysis.mechanism_table`, `control_incremental.cached_observation` and `paper_four_pair_details.paired_timing` supply the projection. The existing analysis source is unchanged; no second acceptor is introduced. E's frozen final receipt supplies exact accepted pointers without registry access. E endpoint receipts are hash-bound, not freshly native-tested. E013/E033/E034/E035/E036 are the only five newly decoded **completed accepted** raw logs;18 prior observations are reused from their hash manifests. No trace body, failed raw or active raw is read. Matching kernel sequences and UIDs, every elapsed contrast including its explicit residual, five-main denominators, and GM by log/product methods are checked. All three figure PNGs were visually inspected for readable labels and correct negative signs. `DATA_VALIDATION.json` records the scientific projection checks; these are not production correctness qualification.
