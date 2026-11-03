# convolutionSeparable: six closed matched sources

Frozen input `4114a3dc0d06b55bc11aac0d0e4e209d5b640e8ec90fd84d8b4615871033f449`. Four original references are SHA-matched to the32-reference index; both new CH sources were independently verified through strict, true164 archive and native restore. Core9eed/FW02775/binary02a289 remain fixed. This is one input, not a suite result.

**Most of the large improvement is shared downstream-system benefit.** DH retains a modest extra relative improvement; the whole DH speedup must not be credited exclusively to DTC.

| Design/config | Rows cycles | Columns cycles | Whole cycles | OwnP0 speedup |
|---|---:|---:|---:|---:|
| CH-P0 | 379655 | 445496 | 825151 | 1.000000 |
| CH-F128 | 328720 | 374220 | 702940 | 1.173857 |
| CH-F256 | 288224 | 313876 | 602100 | 1.370455 |
| DH-P0 | 365625 | 434947 | 800572 | 1.000000 |
| DH-F128 | 311113 | 363251 | 674364 | 1.187151 |
| DH-F256 | 269306 | 293580 | 562886 | 1.422263 |

| F | S_CH | S_DH | CH/DH atP0 | CH/DH atF | I=S_DH/S_CH |
|---|---:|---:|---:|---:|---:|
| F128 | 1.173857 | 1.187151 | 1.030702 | 1.042375 | 1.011325 |
| F256 | 1.370455 | 1.422263 | 1.030702 | 1.069666 | 1.037804 |

F128 cuts cycles14.81% forCH and15.76% forDH; F256 cuts27.03% and29.69%. Relative interaction is only+1.13%/+3.78%, not the entire17.4–42.2% self-speedup. AtF256 DH uses6.51% fewer cycles thanCH, under the disclosed different L1 designs.

## Both directions improve

| Design/F | Rows reduction | Columns reduction | Columns share of total saved cycles |
|---|---:|---:|---:|
| CH-F128 | 13.42% | 16.00% | 58.32% |
| CH-F256 | 24.08% | 29.54% | 59.01% |
| DH-F128 | 14.91% | 16.48% | 56.81% |
| DH-F256 | 26.34% | 32.50% | 59.48% |

Rows/Columns are actual closed trace-kernel names with matching instruction/CTA scope; the two printed cycle intervals sum to each accepted whole replay. Larger absolute savings inColumns explain about59% ofF256 total savings. This localizes where benefit occurs; it does not identify a unique queue mechanism.

## Traffic is nearly unchanged

All counts below use32B L2 sectors or DRAM atoms; bytes=count×32. L2 accepted reads include HIT/HIT_RESERVED/MISS/SECTOR_MISS, whereas readmisses include MISS+SECTOR_MISS.

| Design/F | L2 accepted reads | L2 readmisses | DRAM read atoms | DRAM write atoms |
|---|---:|---:|---:|---:|
| CH-P0 | 4604248 | 2360500 | 2360500 | 2166185 |
| CH-F128 | 4608244 | 2359392 | 2359392 | 2168285 |
| CH-F256 | 4612044 | 2359296 | 2359296 | 2168384 |
| DH-P0 | 4645512 | 2359408 | 2359408 | 2170788 |
| DH-F128 | 4647964 | 2359296 | 2359296 | 2171576 |
| DH-F256 | 4649940 | 2359296 | 2359296 | 2170825 |

FromP0 toF256, CH readmiss/DRAM reads fall only0.0510%; DH only0.00475%. Accepted L2 reads increase about0.17%/0.095%, and write atoms stay near-constant. The27–30% cycle reduction therefore does not coincide with a large traffic-volume reduction. F256 issued reads equal72MiB for both designs; this is model traffic, not native-GPU DRAM measurement.

## Retry and service associations, with limits

| Design/F | L2 reservation-fail attempts | ICNT→subpartition full observations | CHcommon PIB-full events | CHcommon Tag conflicts |
|---|---:|---:|---:|---:|
| CH-P0 | 17940250 | 18970630 | 3247700 | 3967488 |
| CH-F128 | 15425984 | 18034419 | 3243650 | 3967488 |
| CH-F256 | 13553108 | 17461703 | 3518122 | 3967488 |
| DH-P0 | 17783805 | 20420241 | not an active CH counter | not an active CH counter |
| DH-F128 | 14756434 | 18028711 | not an active CH counter | not an active CH counter |
| DH-F256 | 12199317 | 16218216 | not an active CH counter | not an active CH counter |

Aggregate reservation failures decline, especially inColumns. ButRows atF256 becomes faster while L2 reservation failures rise12.3% forCH/6.1% forDH and gpu_stall_dramfull observations rise44.5%/30.3%. These are rejected/retried or per-L2-tick/subpartition observations, not unique requests, queue occupancy, isolatedFR-FCFS waiting cycles or additive critical-path losses. Fewer such events cannot by itself be the full explanation.

CH Tag-conflict totals stay exactly3,967,488; ordinary MSHR entry-full andmerge-full events are explicitly0 inall3CH logs. CHcommonPIB-full events do not monotonically fall. DH OO-full/conflict counters unavailable in this print path remainUNKNOWN; inactive CHcommon counters are not substituted. Real DH OO pending-hit/new-miss/eviction counts and typed per-interval details are retained inJSON.

| DH config | PIB integral/sample mean | Physical-line integral/sample mean | Fully-ready→retire cycles/entry | Map-loss→free cycles/event |
|---|---:|---:|---:|---:|
| P0 | 112.030 | 515.240 | 2.735 | 753.078 |
| F128 | 109.824 | 512.548 | 2.732 | 631.362 |
| F256 | 106.754 | 509.237 | 2.748 | 516.939 |

These are matched aggregate sample/entry/event means across the64SM domain, not critical-path delay. DH retired finite-service entries732,672 andcollected sectors2,930,688 are identical inall3cases. Fully-ready→retire mean remains near2.73cycles, while map-loss→free mean shortens and average physical/PIB occupancy modestly decreases. That is compatible with changed upstream lifetime/overlap; it does not isolate DRAM queue waiting, cachehit causality or MSHR merging. Means/gauges/peaks are never differenced.

## Interpretation boundary

The factor expands FR-FCFS64→128/256 **and** sharedcredits255→319/447; L2 data10MiB, MSHR192×4, missQ32 and850MHz remain fixed. Evidence supports a sizeable shared response to this coupled downstream contract plus a smaller relativeDH improvement. Scheduling, overlap and credit pressure are plausible associations; the present aggregate counters do not separate them into an isolated queue-delay cause.

Interval additive counters are constructor-zero first snapshots and explicit later endpoint differences. They are print-boundary intervals, not automatically request-origin attribution; missing positive-only reason fields remainnull, never0. Existing HtoD tag-fill initial-state and captured-ELF/numerical-state limits remain unchanged. Source overlap is not runtime cachehit/merge proof. CHcommonPIB256 versusDHOO128 and other L1 resource differences remain non-equal-area. No simulation, newinput, source/owner mutation, manuscript edit or remaining48 plan is produced.

Read MATCHED_SUMMARY.json and TYPED_ACTIVE_PATH_COUNTERS.json for compact derivations; SIX_CLOSED_SOURCE_DATA.json preserves complete source/raw SHA, kernel endpoints, counters and missingness. NEW_CH_F128/F256_INDEPENDENT_QUALIFICATION.json preserve actual strict/archive/native restore witnesses.
