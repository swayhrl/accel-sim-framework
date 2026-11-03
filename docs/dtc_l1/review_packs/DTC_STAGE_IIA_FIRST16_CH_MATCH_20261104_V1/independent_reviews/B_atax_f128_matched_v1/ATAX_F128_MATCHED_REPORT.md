# ATAX F128: four-source matched diagnosis

**Main result:** CH regresses materially; DH is nearly unchanged but slightly slower, not exact zero. Almost all cycle change is in K1, while K2 has small positive changes. I>1 here reflects CH regressing more, not an absolute DH win or a speedup of DH.

## Identity and fixed comparison

Full input digest: `eededb785179fc0488c5a01d95154f6748ea45a2ea7bb18ecdbc316cf5166950`. Three original Phase-I sources are selected exactly by full digest/cell/profile from ORIGINAL_REFERENCE_INDEX; the new CH-F128 has STAGEII_AUTHORIZED_CH identity. Ratified P0 reference aliases stay disclosed. All four closed raw SHA/native-exit identities are checked; the new strict/true164/native-restore path was independently revalidated. Same Core 9eed/FW 02775/binary 02a28936,145666048 instructions,32 CTAs and two ordered kernels. No IR/R2/EP/PQ/PS replacement.

Within each design only FR-FCFS 64->128 changes. Shared partition credits also increase 255->319; DRAM 850MHz, L2 10MiB,40 subpartitions, MSHR192 entries per subpartition x merge4, miss queue 32 and all design-specific L1 parameters stay fixed. The nominal 7680 MSHR entries are partitioned resources, not a freely shared pool. No equal-area or equivalent CH/DH L1-service claim.

## Cycles and dependency

| Design/profile | K1 row-strided cycles | K2 lane-coalesced cycles | Total |
|---|---:|---:|---:|
| CH P0 | 26,677,630 | 1,751,212 | 28,428,842 |
| CH F128 | 28,130,567 | 1,751,543 | 29,882,110 |
| DH P0 | 30,226,439 | 1,653,781 | 31,880,220 |
| DH F128 | 30,240,733 | 1,653,904 | 31,894,637 |

S_CH=0.951367; S_DH=0.999548; R_P0=0.891739; R_F128=0.936901; I=1.050644. At F128 DH still has 6.73% more cycles than CH. CH cycles increase 5.11%; DH cycles increase 0.0452%. These are one-input results, not suite statistics.

CH adds 1453268 cycles: K1+1452937 and K2+331. DH adds 14417 cycles: K1+14294 and K2+123. It would be wrong to call DH an exact zero-response control or K2 exactly unchanged.

Unlike MVT/BICG, ATAX has a true source-level data dependency: K1 computes tmp=A*x; K2 consumes tmp to form y=A^T*tmp. Stream/synchronize order also serializes them. K1 has 16KiB adjacent-lane A stride with 4B loop stride, K2 has 4B lane stride with 16KiB loop stride,16 CTAs per kernel and serial per-output accumulation. These formulas motivate phase interpretation but do not prove dynamic cache-hit, merge or critical-path behavior.

Scope limit: the full frozen eededb input retains two full declared grids; the known dd8955 prefix-trim identity is excluded. The inspected candidate source/producer ELF and original numeric input/state are not linked by this analysis. In particular, recovered candidate tmp/y initialization concerns are not repaired or certified by strict trace termination. Dependency and address facts remain candidate-source/trace-defined claims, not a new complete-application numerical certificate.

## Cumulative common downstream counters

| Counter | CH P0 | CH F128 | DH P0 | DH F128 |
|---|---:|---:|---:|---:|
| L2 accepted GLOBAL reads,32B sectors | 65,889,456 | 65,185,968 | 49,155,352 | 50,320,284 |
| L2 GLOBAL read misses,32B sectors | 16,720,180 | 18,006,712 | 19,387,556 | 19,331,416 |
| DRAM issued reads,32B atoms | 16,720,180 | 18,006,712 | 19,387,556 | 19,331,416 |
| DRAM issued writes,32B atoms | 4,924 | 5,430 | 5,808 | 5,802 |
| All-L2 reservation-fail attempts | 39,327,664 | 36,585,050 | 158,818,027 | 162,551,103 |
| ICNT admission-blockage events | 31,062,137 | 28,953,175 | 158,348,591 | 162,334,002 |

CH sends 1.07% fewer accepted L2 read sectors but suffers 7.69% more L2 misses/DRAM-read atoms. Retry attempts fall 6.97% and ICNT admission-blockage counts fall 6.79% while cycles increase. Thus these proxy-event reductions do not establish shorter critical-path execution.

DH sends 2.37% more accepted L2 sectors while DRAM reads fall 0.29%; reservation-fail attempts rise 2.35% and ICNT blockage rises 2.52%, but cycles change only+0.0452%. Near-zero total response hides substantial internal traffic/retry changes rather than proving that no mechanism changed.

K1 contains all accepted-read differences and all measured retry/blockage differences. K2 accepted reads stay identical within each design; read-miss/DRAM atoms change+7036in CH and -2080 in DH. Additive deltas are between completed-kernel print snapshots, not automatic origin-kernel labels if tails cross boundaries. Only first constructor-zero state permits an initial 0; later fields require explicit endpoints, otherwise null. Means, gauges and peaks are never differenced.

## Retry reasons

| Explicit L2 GLOBAL_R reason | CH P0 | CH F128 | DH P0 | DH F128 |
|---|---:|---:|---:|---:|
| LINE_ALLOC_FAIL | 3,213,805 | 2,934,740 | 335,494 | 312,763 |
| MISS_QUEUE_FULL | 7,111,605 | 12,524 | 18,806,950 | 106,080 |
| MSHR_ENRTY_FAIL | 26,793,345 | 30,902,794 | 139,657,561 | 162,115,286 |
| MSHR_MERGE_ENRTY_FAIL | 2,206,900 | 2,730,603 | 17,636 | 15,807 |

MISS_QUEUE_FULL nearly disappears in both designs; entry-capacity retries instead increase. CH entry and merge-limit failure classes both grow, while its total failures shrink. DH entry failures become dominant. Entry capacity and merge saturation are separate source checks; retry count is neither MSHR occupancy-time nor critical-path stall time. Counting retries alone cannot show that expanding either resource improves performance. Positive-only omitted reasons remain missing, not 0.

## Typed OO, PIB/Tag and finite-service evidence

| DH-only cumulative counter | P0 | F128 |
|---|---:|---:|
| OO valid line hits | 5,997,156 | 5,695,060 |
| OO pending line hits | 64,342 | 75,205 |
| OO new misses/lower-created | 12,288,838 | 12,580,071 |
| OO tag-mapping evictions | 12,272,454 | 12,563,687 |
| PIB integral,entry x SM-cycle | 3,419,022,729 | 3,468,770,454 |
| Fully-ready-to-retire sum,entry-cycle | 8,863,818 | 8,964,149 |
| Ready-to-collect sum,entry-cycle | 3,001,940 | 3,101,937 |
| Collection-cycle sum | 5,825,195 | 5,827,373 |
| Writeback-wait sum | 36,683 | 34,839 |
| Recorded map-loss-to-free sum | 61,254,611,518 | 61,591,965,204 |
| Recorded map-loss-to-free event count | 12,272,454 | 12,563,687 |

DH OO line probes are conserved at18350336. Valid hits fall 302096, pending hits rise 10863 and new misses/lower-created/tag evictions rise 291233. In both runs L2 accepted 32B sectors equal 4x full128B lower-created requests. More upstream misses coexist with slightly fewer DRAM-read atoms: upstream request count and downstream miss work are different domains, not a single monotonic chain.

Across all 64 SM samples mean PIB occupancy is1.6757->1.6993, physical-line occupancy152.614->152.770, and fully-ready-to-retire mean4.2261->4.2739core cycles per retired service entry. Recorded map-loss-to-free mean4991.2->4902.4cycles/event. Finite-service retired entries are unchanged. These integrals/means are not critical-path time or active-SM-only peaks; they cannot prove an offsetting-latency budget.

**Active paths:** CH PAPER_BASE/common PIB capacity 256; DH PAPER_OO PIB capacity 128 through oo_pib_entries. DH generic pib_entries=8 is not the OO admission limit. CH_common_frontend and DH_PAPER_OO_frontend are separate machine-readable domains. CH explicit common PIB-full0 and tag conflicts20972288 are not OO counters. OO PIB-full/tag-bank-conflict fields remain null because this active print path does not expose them.

CH finite_service0 is DTC-extension state, not free/unbounded conventional cache service. Different L1 organizations, metadata/queue record sizes and ordinary-MSHR options are not equal-area/equal-mechanism. Terminal0 PIB/outstanding/reference gauges show drain, not absence of pressure; retained physical allocation is cache state rather than live-request leakage.

## Means and causal limits

| Last printed diagnostic | CH P0 | CH F128 | DH P0 | DH F128 |
|---|---:|---:|---:|---:|
| avg_mrq_latency | 412 | 553 | 745 | 1,389 |
| averagemflatency | 620 | 628 | 2,369 | 2,391 |
| avg_icnt2mem_latency | 152 | 158 | 428 | 413 |
| avg_icnt2sh_latency | 39 | 40 | 226 | 257 |

MRQ ages grow in both designs. They condition on DRAM requests up to bank assignment and are not full L2->DRAM/return or critical-path latency. Other means retain the known 500000-cycle fold/tail and packet-population limitations. They are not differenced or summed into per-kernel latency.

**Facts:** CH regression is almost entirely K1 and accompanies more DRAM-read work despite fewer accepted upstream reads and fewer retry/blockage events. DH is slightly slower but nearly unchanged, with more OO misses and fewer DRAM atoms. K2 has a real tmp dependency but changes very little in cycles.

**Association:** CH higher K1 L2-miss/DRAM work is consistent with its regression. DH shows mixed internal changes with small net execution change; aggregate totals do not assign compensating critical-path effects.

**Hypotheses, not proved:** window/credit changes affect filtering, ordering, overlap and the residence of requests/data. For CH, the remaining L2 read stream may have worse useful reuse/timing, creating more memory work despite fewer failed attempts. For DH, changed upstream reuse, request admission and downstream service may partly offset in elapsed cycles. Exact address-ordered L2 reuse, per-bank MSHR occupancy-time and dependency ages are absent, so neither a single bottleneck nor a cancellation budget is established.

**Cannot conclude:** that I>1 means DH gets faster or beats CH; that fewer retries mean lower latency; that Tag/PIB or finite completion is absent as a limiter; that MSHR expansion will improve ATAX; or that this one point selects a uniform configuration. No simulation,48-point design, original-result/service mutation or v0.23 edit occurred. The all16 final review remains a separate Root task.

## Reproduction

MATCHED_FOUR_SOURCE_DATA.json binds four full identities, roles, reference aliases, closed native-exit/raw SHA, cycles, additive print intervals and explicit buckets/reasons. NEW_CH_INDEPENDENT_QUALIFICATION.json verifies new strict/archive/native restore. TYPED_ACTIVE_PATH_COUNTERS and DERIVED_TYPED_DIAGNOSTICS keep CH common/DH OO separated. ACTIVE_PATH_SOURCE_EVIDENCE, ATAX_SOURCE_DEPENDENCY_EVIDENCE and the frozen counter catalog preserve source/trace limitations. Scripts/reports exist only in this new true164 directory.
