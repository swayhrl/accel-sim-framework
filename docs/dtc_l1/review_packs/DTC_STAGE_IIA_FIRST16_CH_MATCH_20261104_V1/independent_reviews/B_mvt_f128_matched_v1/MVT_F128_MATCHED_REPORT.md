# MVT F128: four-source matched diagnosis

**Main result:** opposite CH/DH responses are overwhelmingly in K1, but not exactly confined to it. CH improves despite more accepted L2 reads, reservation-failure attempts and ICNT-admission blockage. DH creates fewer OO line requests and tag evictions, yet issues more DRAM reads and runs slower. Thus aggregate retry or upstream-miss reduction alone is not a performance explanation.

## Identity and fixed contract

Full input digest: `f437190767aaed4921e11e6b85f80fb3348da90ec0f18fa8fa1bdfcd76ae3079`. Three original references are selected exactly by digest/cell/profile from ORIGINAL_REFERENCE_INDEX; the new CH-F128 is STAGEII_AUTHORIZED_CH. Original P0 aliases remain disclosed. Four closed raw streams and the new strict/true164/native-restore path are SHA-verified. Core 9eed/FW 02775/binary 02a28936,145666048 ordered instructions,32 CTAs and two kernels match. No IR/R2/EP/PQ/PS data enters.

Within each design only FR-FCFS 64->128 changes; the shared-credit limit also changes 255->319, so this is a coupled window/credit probe. DRAM 850MHz, L2 10MiB,40 subpartitions, per-subpartition MSHR192 x merge4 and miss queue 32 remain fixed. These are not freely shared global7680 MSHR entries. CH/DH have deliberate different L1 paths and no equal-area/capacity/timing claim.

## Cycles and kernels

| Design/profile | K1 row-strided cycles | K2 lane-coalesced cycles | Total |
|---|---:|---:|---:|
| CH P0 | 24,828,424 | 1,752,751 | 26,581,175 |
| CH F128 | 23,819,947 | 1,753,055 | 25,573,002 |
| DH P0 | 33,032,429 | 1,655,111 | 34,687,540 |
| DH F128 | 33,678,264 | 1,654,356 | 35,332,620 |

S_CH=1.039423; S_DH=0.981743; R_P0=0.766303; R_F128=0.723779; I=0.944507. DH has38.16% more cycles than matched CH-F128. This is one input/profile, no suite/configuration-selection claim.

CH K1 saves 1008477 cycles while K2 adds 304; net saving 1008173. DH K1 adds 645835 while K2 saves 755; net increase 645080. It would be inaccurate to say K2 is exactly unchanged.

The frozen trace/source map has K1 x1+=A*y1 with 16KiB adjacent-lane A stride and 4B loop stride; K2 x2+=A^T*y2 has 4B lane stride and 16KiB loop stride. Both have 16CTAs and serial accumulation. The two output chains are algebraically independent but launched serially; K2 is not an ATAX-like consumer of K1 output. Source is a fixed inspected candidate; capture-source/ELF and original numeric-byte certification remain unresolved.

## Whole-replay cumulative downstream counters

| Counter | CH P0 | CH F128 | DH P0 | DH F128 |
|---|---:|---:|---:|---:|
| GLOBAL L2 accepted reads,32B sectors | 65,311,172 | 67,381,220 | 48,510,772 | 43,887,104 |
| GLOBAL L2 read misses,32B sectors | 15,617,216 | 15,559,856 | 20,574,896 | 21,306,908 |
| DRAM issued reads,32B atoms | 15,617,216 | 15,559,856 | 20,574,896 | 21,306,908 |
| All-L2 reservation-fail attempts | 38,829,217 | 41,003,118 | 161,531,923 | 173,604,363 |
| ICNT->L2 admission-blockage events | 32,670,735 | 34,946,868 | 152,064,800 | 161,662,150 |

CH: L2 accepted reads +3.17%, misses/DRAM reads -0.37%, retry attempts +5.60%, ICNT blockage +6.97%, while cycles improve. DH: L2 accepted reads -9.53%, misses/DRAM reads +3.56%, retry attempts +7.47%, ICNT blockage +6.31%, while cycles regress. MVT directly refutes a simple rule that fewer aggregate retry/stall proxy events must accompany a gain.

K1 accounts for all accepted-read change and nearly all retry change. K2 accepted reads are identical within each design; its DRAM-read atoms still change by +11284 in CH and +73720 in DH, while K2 cycles change only +304 and -755. Printed-boundary deltas do not automatically assign every request to its origin kernel; state/tails can cross boundaries. The exact intervals and cumulative buckets are in MATCHED_FOUR_SOURCE_DATA.json. After the first source-proven constructor-zero snapshot, a field must be explicit at both endpoints to yield a delta; a late/disappearing field remains null, never default0.

## Retry-reason composition

| Explicit L2 GLOBAL_R failure | CH P0 | CH F128 | DH P0 | DH F128 |
|---|---:|---:|---:|---:|
| LINE_ALLOC_FAIL | 3,262,847 | 3,822,607 | 529,671 | 595,326 |
| MISS_QUEUE_FULL | 5,560,281 | 30,644 | 52,360,071 | 56,276 |
| MSHR_ENRTY_FAIL | 29,115,010 | 35,964,383 | 108,621,212 | 172,934,579 |
| MSHR_MERGE_ENRTY_FAIL | 880,332 | 1,175,494 | 18,837 | 17,853 |

MISS_QUEUE_FULL collapses in both designs. Entry-capacity retry attempts increase from 29115010 to35964383 in CH and108621212 to172934579 in DH. The DH increase is about 59.2%, and entry failures are 99.61% of its F128 all-L2 reservation failures. This shows a changed admission-retry composition at the still-fixed per-bank MSHR resource, not its occupancy-time or critical-path delay. Entry capacity and per-address merge limit are different checks. These event counts cannot prove that expanding either will speed the application.

CH common L1 MSHR entry/merge full events and common PIB-full events are explicitly 0; they are not DH OO observations. Raw bracketed omissions stay missing, not 0. gpu_stall_dramfull counts full-subpartition ticks only when an ICNT packet waits, summed over subpartitions; it is not isolated FR-FCFS queue latency or wall-clock stall time.

## OO request conservation, active PIB and completion service

| DH-only whole-replay counter | P0 | F128 |
|---|---:|---:|
| OO valid line hits | 6,155,579 | 7,321,884 |
| OO pending line hits | 67,064 | 56,676 |
| OO new misses/lower-created | 12,127,693 | 10,971,776 |
| OO tag-mapping evictions | 12,111,309 | 10,955,392 |
| PIB integral,entry x SM-cycle | 3,524,478,877 | 3,570,366,544 |
| Fully-ready-to-retire sum,entry-cycle | 8,982,782 | 9,142,276 |
| Ready-to-collect sum,entry-cycle | 3,103,802 | 3,274,915 |
| Collection-cycle sum | 5,833,394 | 5,836,408 |
| Writeback-wait sum | 45,586 | 30,953 |
| Recorded map-loss-to-free sum | 65,791,323,051 | 66,159,534,874 |
| Recorded map-loss-to-free event count | 12,111,309 | 10,955,392 |

DH total OO line probes remain18350336; valid hits rise 1166305, pending hits fall 10388, and new misses/lower-created/tag evictions fall 1155917. L2 accepted 32B sectors equal 4x full128B OO lower requests in both runs. This is a genuine upstream request reduction with fixed instructions, not evidence that downstream miss work must also fall.

Mean PIB occupancy across all 64 SMs is 1.5876->1.5789; mean physical-line occupancy152.644->152.354. Fully-ready-to-retire mean is4.2828->4.3588core cycles per service-retired entry. Recorded map-loss-to-free mean changes 5432.2->6039.0 cycles per recorded event; it is not critical-path time. Ready-to-collect sum grows, while aggregate writeback-wait falls 32.10%; neither is a critical-path time decomposition. Mean/terminal gauges do not exclude burst/tail bottlenecks.

**Active-path correction:** CH PAPER_BASE/common admission uses PIB256 through generic pib_entries. DH PAPER_OO admission uses oo_pib_entries128. DH generic pib_entries8 is not its OO capacity. The source constructor/guards and literal option values are pinned in ACTIVE_PATH_SOURCE_EVIDENCE.json. CH_common_frontend and DH_PAPER_OO_frontend are separate JSON domains; CH common values never appear as OO measurements. OO PIB-full and tag-bank-conflict event counters are not printed in this active path and stay null.

Terminal PIB/active-reference/lower-outstanding gauges drain to 0; retained physical cache allocation is not a leaked-request count. CH finite_service0 describes absence of the DTC extension, not infinite/free conventional service. The ordinary-MSHR512 and generic32 options have different frontend paths and are not asserted to be equivalent active OO structures. Capacity counts alone do not establish equal record size, service or physical area.

## Means and evidence levels

| Last printed diagnostic | CH P0 | CH F128 | DH P0 | DH F128 |
|---|---:|---:|---:|---:|
| avg_mrq_latency | 455 | 696 | 738 | 1,366 |
| averagemflatency | 620 | 614 | 2,230 | 2,463 |
| avg_icnt2mem_latency | 153 | 140 | 349 | 391 |
| avg_icnt2sh_latency | 44 | 46 | 220 | 166 |

MRQ mean increases in both designs although CH improves. It is a cumulative request-conditioned age to bank assignment, not complete L2->DRAM service or critical-path latency. Other printed means have the known 500000-cycle fold/tail and population limitations. Means are never differenced or summed into per-kernel latency.

**Facts:** K1 dominates both opposite responses; DH improves OO line-hit/eviction counts but increases L2/DRAM miss work; both remove most miss-queue retry attempts; MSHR-entry retries become more dominant. CH improves even while its retry/blockage counters increase.

**Association:** DH higher DRAM-read work and downstream admission retries accompany its K1 regression. For CH, almost unchanged DRAM-read work and more retry events coexist with a K1 gain, so event totals alone cannot identify useful concurrency, overlap, waiting age or dependency-critical delay.

**Hypothesis, not proved:** coupled window/credit expansion changes filtering/interleaving and overlap. DH eliminates many upstream hits-to-be-served, but its remaining L2 stream has worse conditional miss fraction and more absolute misses; fixed MSHR entry admission remains a strong retry site. CH may benefit from overlap or dependency ordering not visible in aggregate failures. Address/timestamp, occupancy-time and critical-dependency evidence are missing; no single bottleneck or promised expansion gain is established.

**Missing/limits:** no measured OO full/conflict counter, no per-bank MSHR occupancy-time or address-ordered L2 reuse trace, no exact per-kernel mean latency, no equal-area comparison. Static source direction and 16CTA supply do not prove dynamic cache hits or MLP. No new simulation, runtime/source/service mutation,48-point design or manuscript edit was made.

## Reproduction

MATCHED_FOUR_SOURCE_DATA.json binds exact full identities, reference aliases, RESULT/native-exit/raw SHA, cycles, per-kernel additive print intervals and all printed reasons/buckets. NEW_CH_INDEPENDENT_QUALIFICATION.json binds new strict/archive/native restore. TYPED_ACTIVE_PATH_COUNTERS.json and DERIVED_TYPED_DIAGNOSTICS.json preserve mode namespaces. Source/catalog evidence and two scripts are local to this new 164 directory.
