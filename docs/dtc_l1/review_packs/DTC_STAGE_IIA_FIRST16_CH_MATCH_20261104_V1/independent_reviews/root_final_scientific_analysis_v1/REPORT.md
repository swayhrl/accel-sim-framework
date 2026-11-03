# DTC-MAIN final scientific analysis: Stage II-A first16

The fixed first8 input subset is fully paired:16 newCH accepted,0 archivednegative,0 missing;32 exact original references retained. Root independently rehashed strict/true164 archive/full native recovery and all10 execution requirements are proven. This report does not turn8 into core32/full35 coverage.

## Fair matching changes the interpretation

| Profile | GM CH own-P0 speedup | GM DH own-P0 speedup | GM same-F CH/DH | GM relative interaction I | I positive/negative/exactzero |
|---|---:|---:|---:|---:|---|
| F128 | 1.053160710 | 1.045478946 | 1.170800616 | 0.992705991 | 3/4/1 |
| F256 | 1.079176069 | 1.076911812 | 1.176928647 | 0.997901865 | 4/3/1 |

All GM use the exact same8 full digests, equal program weighting and uniform F per column. Baseline GM CH0/DH0 is1.179403194. F128 andF256 improve DH itself, but CH improves slightly more in aggregate: I falls0.7294% and0.2098% below1. F256 is less unfavorable thanF128, with same-set GM I256/I128=1.005234052; that is not a relative gain overP0. This subset does not justify adopting either enlarged window as a DTC-specific advantage or selecting per-program best configurations. Positive absolute GM CH/DH and unfavorable incremental I answer different questions.

Same-F DH is faster in4/8 programs at each enlarged F, with4/8 slower. P0 had5 faster/3 slower. The accepted negative responses are not scientific run failures. Formal wider adoption requires the remaining fixed core matches under future approval; no workload may be removed based on these results. No repeatability interval is estimated from one accepted execution per identity.

Full six-cycle table, per-input ratios, suite GM, exact sign populations, directF comparisons and missing counts are in [quantitative report](quantitative/FINAL_FIRST16_REPORT.md). Exact source paths, all input members and32old/16new RESULT SHA are in quantitative/FULL_SHA_REFERENCES.json.

## Program-specific findings and evidence strength

| Program/input prefix | Established observation | Interpretation limit | Evidence packet |
|---|---|---|---|
| convolutionSeparable /4114a3dc | F256 CH1.370455x,DH1.422263x,I1.037804; Rows andColumns both improve;Columns supplies about59% of saved cycles. DRAM reads nearly constant. | Large shared-system benefit plus a smaller DTC-relative improvement;Rows retries/full observations can rise while faster. | A_convseparable_three_profiles_v1 |
| scan /6df3a84b | CH1.178254/1.272539x,DH1.156693/1.283635x;I0.981700/1.008719. | F128 favoursCH incrementally,F256 only modestly favoursDH;whole-run common benefit is not exclusively DTC. Actual33-kernel grouping must be consumed from this input, not11 assumed identical triplets. | B_scan_three_profiles_v1 |
| 2DCONV /d984ea54 | CH exact unchanged1548909 acrossP0/F;DH1.057515/1.078012x. | Existing F128 evidence has unchanged DRAM reads but fewer admission retries;this is association, not isolated queue-delay proof. F256 cycle effect is independently matched;do not silently extrapolate F128 counters. | B_gemm_2d_f128_controls_v1 plus quantitative32/16refs |
| ATAX /eededb78 | F256 DH1.017823x yet still0.7735% more cycles thanCH;I1.112797. Nearly all change isK1. | CH itself worsens9.331%;83.47% of log(I) is its arithmetic contribution,not causal runtime fraction. Printed DH MRQ rises. | B_atax_three_profiles_v1 |
| MVT /f4371907 | F256 CH1.091946x butDH0.988434x;DH44.1628% more cycles thanCH;I0.905203. K1 dominates. | Recovery versusF128 does not recoverP0 or relativeCH. OO lower requests can rise whileDRAM reads fall. | B_mvt_three_profiles_v1 |
| BICG /ae34174f | F256 DH0.993156x;DH17.1653% more cycles thanCH;I0.930967. K1 exact unchanged,all cycle differenceK2. | Miss-queue retries fall but entry retries remain high;counts do not prove a capacity fix or critical-path cause. | B_bicg_three_profiles_v1 |
| vectorAdd /e7bb67e6 | F256 DH cycles+8.703%,despite unchanged1.5M read sectors/DRAM atoms and retries more thanhalved. | Explicit OO0 valid/pending hits are real0;unprinted latency means aremissing. Larger maximum latency is a tail clue,not identified critical load. | B_vectoradd_three_profiles_v1 |
| GEMM /fc0705ae | Both designs have exactzero cycle response acrossF;DH826089 vsCH1395216. | Existing F128 raw evidence has explicit0 DRAM events and warm HtoD tagfill;do not call the whole application compute-bound or a cold-cache result. F256 cycles do not automatically prove every F256 counter unchanged. | B_gemm_2d_f128_controls_v1 plus quantitative32/16refs |

All packet paths and frozen manifest SHA are in EVIDENCE.json. The agent-packet manifest names resolve under ../ in the published independent_reviews directory, or under A/agents on true164. BICG prior report has a literal ?-delimited quote around miss-queue-pressure wording; this is typography only,not a scientific unknown marker or a change to the frozen numeric data.

## Resource and implementation evidence

The16 closed resource streams show periodic peak RSS from0.4805 to4.7383GiB. These are sampled observations,not continuous HWM or guarantees for other inputs. Longest elapsed run was5.5033h. No runtime RAM/disk failure or observed RSS/output-cap overrun occurred. Admission-only disk waits remain in the ledger and are not model failures. No asset was migrated by this Goal. Final trajectory source is pinned in EVIDENCE.json.

F64/128/256 couples FR-FCFS window64/128/256 with memory-partition sharedcredits255/319/447 across20controllers;it is not an isolated L2 queue intervention. Additional queue slots are64/192 percontroller and additional shared-credit capacity likewise64/192. 10MiB L2 data/sets/ways/address map,192MSHR entries,4merge limit,missQ32,850MHz DRAM and1410MHz core/ICNT/L2 stay fixed. Geometry/capacity counts are not physical area estimates.

CH PAPER_BASE uses conventional hash-L1D with active commonPIB256 andTag-bank arbitration;DH PAPER_OO uses activeOO PIB128,80KiB capacity-model physicalpool and its distinctTag/service structure. DH generic commonPIB8/dtcMSHR32 are not activeOO capacities. CH/DH L1 structures,queues,timing andphysical area are unequal. Source-pinned A_resource_cost_v1 documents actual active paths;matched downstream options do not make equal-area hardware.

gpgpu_perf_sim_memcpy1/flush_l2_cache0 directly fills L2 tags for HtoD,without issuing normal timed DRAM transfers. GEMM3MiB and2DCONV64MiB copies do not imply equal residency or that64MiB fits10MiB. Numerical values and capture-time ELF/source linkage remain uncertified;whole declared trace coverage does not newly certify native full-application semantics. v0.23 remains the last confirmed manuscript.

## What the counters do and do not establish

L2GLOBAL accepted/miss counters use32B sectors;OO lower requests are128B lines;DRAM reads/writes are issued32B atoms. Cumulative fields are differenced only at explicit additive print endpoints,not summed over kernels. End-of-kernel print intervals need not identify request-origin kernel. Per-kernel gpu_sim fields and cumulative gpu_tot/L2/DRAM/DTC fields remain distinct. Missing positive-only reasons,means,gauges orpeaks are never invented as0 or differenced like additive events.

MRQ measures request-construction-to-bank-assignment in corecycles,not full L2-to-DRAM latency or critical-load waiting. Other printed means have500k-cycle fold/print ordering and tail omissions. ATAX/MVT/BICG DH MRQ rises acrossF even when some total cycles improve. Therefore this experiment does not establish average DRAM waiting fell. Retry events are not occupancy,stall-cycle fractions or a causal decomposition. Candidate-source access direction/dependency is separated from actual trace shape and dynamic statistics;static repeated addresses are not observed hits/merges.

The plausible hypothesis is changed scheduling/admission/credits redistributing overlap,cache residency and request lifetime. Existing evidence locates sensitive kernels and associations;it does not isolate queues,banks,credits or dependent critical requests. A new instrumentation or parameter experiment would require separate authorization.

## Preserved engineering history and scope

Pre-registration owner attachment failed before any model or identity consumption;the qualified attachment retained the unique owner/locks. An initial result postprocess lacked RESULT_ENGINE_PIN;the established compatible pin was restored and the same UUID/raw result was reprocessed,without rerunning its model. Prior failures remain recorded. A same-owner disk-preclaim amendment only tightened earlier admission accounting;disk waits were allowed to resolve naturally. All62 frozen runtime/build/input/config pins still match,16 unique UUIDs were consumed exactlyonce,and old DTC records/budgets remain unchanged.

Original350 remains331 accepted,18archivednegative,1engineeringnegative;the separate336 named view is not merged into it. Original72,old350,repair-validation roles andoriginalP0 aliases remain distinct. No EP/PQPS/IR/R2 result is promoted into this first16 matrix. No next48 identity,combination,capture,109 task ormanuscript edit was authorized or dispatched. Remaining48 batching will be written only after this completed first16 analysis receives independent final review.
