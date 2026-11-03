# BICG: matched CH/DH P0 versus F128, four closed sources

All performance-response differences are localized to K2: K1 is exactly unchanged within each design. CH improves while DH regresses despite fewer DH L1 line misses/tag evictions. The strongest existing association is the remaining L2 miss stream and the composition of L2 admission retries; the counters do not yet prove a single critical-path cause.

## Identity and comparison contract

Input digest: `ae34174fbbdf83b20a72f44492665cf4b99ed35563f482f7d14763e89f398aef`. Source roles: three exact original Phase-I references selected by full digest/cell/profile from ORIGINAL_REFERENCE_INDEX; one new STAGEII_AUTHORIZED_CH result. Ratified CH/DH P0 aliases retain their original identities. No IR/R2/EP/PQ/PS substitution. All four raw streams are closed, naturally exited, SHA-verified, share Core 9eed/FW 02775/binary 02a28936 and the same ordered 145666048 instructions,32 CTAs and two kernels. The new CH strict/archive/native-restore path was independently revalidated.

Within CH and within DH, the only effective-option difference is FR-FCFS 64->128. Source shared-credit coupling simultaneously changes 255->319 per memory controller (return queue 192,2 subpartitions); L2 remains 10MiB, MSHR192 entries per L2 cache/subpartition x merge4 (40subpartitions; nominal7680 entries, not a freely shared global pool), miss queue 32, clocks/DRAM 850MHz and all design-specific L1 options fixed. This is not an isolated queue-capacity or equal-area experiment. The seven deliberate CH/DH L1/configuration differences are preserved in MATCHED_FOUR_SOURCE_DATA.json.

## Performance and phase localization

| Design/profile | K1 coalesced cycles | K2 row-strided cycles | Total cycles |
|---|---:|---:|---:|
| CH P0 | 1,749,396 | 24,549,302 | 26,298,698 |
| CH F128 | 1,749,396 | 22,715,495 | 24,464,891 |
| DH P0 | 1,655,347 | 27,030,465 | 28,685,812 |
| DH F128 | 1,655,347 | 27,555,133 | 29,210,480 |

S_CH=1.074957; S_DH=0.982038; R_P0=CH0/DH0=0.916784; R_F128=CHF/DHF=0.837538; I=0.913561. DH has 19.40% more cycles than CH at matched F128. This is one workload, no suite-GM or uniform-config adoption claim.

CH saves 1833807 cycles, all in K2 (-7.47% of K2). DH adds 524668 cycles, all in K2 (+1.94% of K2). Source/trace mapping: K1 forms s=A^T*r with lane-contiguous A; K2 forms q=A*p with 16KiB adjacent-lane stride and 4B same-thread loop stride. The fixed candidate source has 16CTAs per phase and serial output accumulation; captured source/ELF linkage remains unresolved. These formulas explain phase contrast, not measured cache-hit/MSHR causality.

## Common downstream totals

| Counter | CH P0 | CH F128 | DH P0 | DH F128 |
|---|---:|---:|---:|---:|
| L2 accepted GLOBAL reads (32B sectors) | 64,586,544 | 63,678,800 | 44,804,596 | 42,483,856 |
| L2 GLOBAL read misses (32B sectors) | 15,513,224 | 14,425,788 | 17,688,864 | 17,956,084 |
| DRAM issued reads (32B atoms) | 15,513,224 | 14,425,788 | 17,688,864 | 17,956,084 |
| DRAM issued writes (32B atoms) | 4,772 | 4,316 | 5,892 | 5,836 |
| All-L2 reservation-fail attempts | 57,034,297 | 46,315,523 | 158,410,296 | 159,762,760 |
| ICNT admission blockage events | 42,823,201 | 34,414,850 | 157,588,835 | 159,723,396 |

The counters are persistent cumulative snapshots. K1 counters are identical P0/F128 within each design, so the changes above occur in the K2 print interval. Full per-kernel interval counts and raw explicit buckets/reasons are retained in MATCHED_FOUR_SOURCE_DATA.json. These intervals are not automatically request-origin labels if outstanding tails cross a boundary.

CH: accepted reads -1.41%, L2 misses/DRAM reads -7.01%, L2 reservation failures -18.79%, ICNT admission blockage -19.64%. DH: accepted reads -5.18% but L2 misses/DRAM reads +1.51%, reservation failures +0.85%, ICNT blockage +1.35%. GLOBAL write sectors stay 4195328 in all four; small DRAM-write totals do not account for the changed read volume. ACT totals fall 3387972->3116011 in CH and rise 3932072->3998719 in DH, consistent with the direction of DRAM read work, not proof of a unique row-buffer mechanism.

## Retry composition: relief is not removal of all pressure

| Explicit L2 GLOBAL-read reason | CH P0 | CH F128 | DH P0 | DH F128 |
|---|---:|---:|---:|---:|
| LINE_ALLOC_FAIL | 6,064,345 | 5,007,714 | 347,238 | 405,108 |
| MISS_QUEUE_FULL | 10,086,344 | 6,746 | 15,514,452 | 137,002 |
| MSHR_ENRTY_FAIL | 39,160,496 | 39,747,955 | 142,533,205 | 159,204,818 |
| MSHR_MERGE_ENRTY_FAIL | 1,717,571 | 1,547,340 | 15,401 | 15,832 |

Both designs almost eliminate MISS_QUEUE_FULL attempts. CH MSHR-entry failures rise 1.50%, but DH rises 11.70%(142533205->159204818). In DH-F128 this reason is 99.65% of all L2 reservation failures, versus about 90.0% at P0. This establishes a change in the mix of failed admission attempts at the still-fixed192-entry-per-L2-subpartition MSHR structure; it is not an occupancy histogram or a measurement of critical-path stall time. Repeated retries can count the same logical request many times.

Source mshr_table::full distinguishes existing-address merge-list saturation from new-address entry-capacity saturation; send_read_request increments the corresponding reason. Increasing F also expands shared partition credits, so changed admission/interleaving is a viable explanation for the mix. MISS_QUEUE_FULL falling does not mean downstream limitations disappeared. Entry-capacity shortage and per-address merge-limit shortage are different conditions. These retry counts alone cannot establish that increasing either resource will improve performance; per-bank occupancy/time and dependency evidence are missing. No exclusive timing attribution follows from event counts. Positive-only raw omissions remain missing; per-kernel reason differences are emitted only where both boundaries explicitly print the reason.

## Design-specific L1/PIB/Tag/completion evidence

| DH-only cumulative counter | DH P0 | DH F128 |
|---|---:|---:|
| OO valid line hits | 7,087,138 | 7,667,198 |
| OO pending line hits | 61,793 | 61,918 |
| OO new line misses / lower-created | 11,201,149 | 10,620,964 |
| OO tag-mapping evictions | 11,184,765 | 10,604,580 |
| Finite-service PIB integral (entry x SM-cycle) | 3,024,944,589 | 2,956,048,834 |
| Fully-ready-to-retire sum (entry-cycle) | 9,069,203 | 9,125,347 |
| Ready-to-collect sum (entry-cycle) | 3,188,930 | 3,240,224 |
| Collection-cycle sum | 5,847,447 | 5,850,729 |
| Writeback-wait sum | 32,826 | 34,394 |

DH line probes remain 18350080. Valid hits rise 580060, pending hits 125, and new misses/lower-created/tag evictions fall 580185. In both runs L2 accepted sectors equal exactly 4x lower-created. Source constructs full 128B OO lower reads with four 32B sectors; this is real upstream request reduction, not a changed input. Yet L2 HIT sectors fall 27113296->24525132 and absolute read misses rise 267220. The filtered L2 stream and its cache/service timing have changed; less L1 traffic does not guarantee less DRAM traffic.

DH global-read L2 miss fraction rises39.48%->42.27%; CH falls24.02%->22.65%. This conditions on different upstream streams; it is not a same-request locality experiment.

DH finite-service retired entries remain 2097152. Mean PIB occupancy across all 64 SMs is1.6477->1.5812; physical-line mean264.982->264.346. Post-fully-ready-to-retire mean changes4.3245->4.3513core cycles per retired service entry. These averages do not expose peaks/tails or active-SM-only behavior and cannot exclude a local completion/PIB bottleneck.

Terminal PIB/outstanding/active-reference gauges drain to 0. Physical allocated 16384 at termination is retained cache-state occupancy, not proof of live leaked requests. OO PIB-full and tag-bank-conflict event counters are not printed here and stay MISSING; CH-specific full events are explicitly 0 and cannot be imported into DH. CH baseline L1 MSHR entry/merge failures are explicitly 0; its L1 LINE_ALLOC_FAIL reasons remain large. CH tag_requests 338407901->323889774and tag_conflicts 20972288 unchanged are source-defined attempt/arbitration counters, not the same event domain as DH OO line-probe hits/evictions.

CH finite_service=0 versus DH=1, mode1 versus3, MSHR option512 versus32 (different frontend paths, not asserted to be equivalent effective structures), PIB parameter256 versus8, different cache/Tag layouts and unified L1 size96 versus128 remain deliberate architectural differences. The DTC finite_service flag is an extension-specific contract; CH ordinary cache/MSHR service is still finite. Missing DTC service instrumentation does not mean missing conventional latency. No finite-service absence-as-zero, equal-capacity, equal-area, timing or hardware-cost claim is made. Same-source L2/DRAM event units are comparable, while their upstream request populations intentionally differ.

## Latency and causal boundary

| Last printed diagnostic | CH P0 | CH F128 | DH P0 | DH F128 |
|---|---:|---:|---:|---:|
| avg_mrq_latency | 526 | 807 | 791 | 1,477 |
| averagemflatency | 736 | 684 | 2,548 | 2,649 |
| avg_icnt2mem_latency | 153 | 137 | 462 | 484 |
| avg_icnt2sh_latency | 72 | 84 | 221 | 202 |

MRQ age rises in both designs although CH gets faster. Its cumulative request-conditioned mean runs from DRAM-request construction to bank assignment, not complete L2->DRAM or critical-path latency. Other printed means have the known 500000-cycle fold/tail limitation and distinct packet populations. None is differenced into a per-kernel mean or summed into an end-to-end decomposition.

**Facts:** opposite performance changes are entirely K2; shared-credit/window expansion removes most miss-queue retry attempts; DH retains dominant MSHR-entry retry pressure and issues more DRAM read work despite fewer upstream line requests.

**Association:** CH lower miss/read work and admission blockage accompany its gain; DH higher miss/read work, MSHR failures and admission blockage accompany its regression. Tag-eviction reduction and slightly changed post-ready service averages do not track execution improvement.

**Leading hypothesis, not proved:** expanded credits/window changes request/response overlap and filtering/interleaving. For DH, useful upstream reuse improves but the remaining L2 stream has more misses and the fixed L2 MSHR entry resource remains heavily contested; the new concurrency does not translate into lower K2 cycles. CH enjoys a larger reduction of downstream work/queue blocking. Timing/order, replacement, merging, DRAM scheduling and request-age/return dependencies are not separated by current totals.

**Cannot conclude:** that MSHR192 alone is the critical cause; that PIB/Tag/finite completion is absent as a bottleneck; that larger F makes DH intrinsically worse; that CH/DH are equal-area; or that this one program selects a suite configuration.

Remaining high-value read-only checks are per-L2-bank/per-DRAM-controller load imbalance and already-recorded request distributions in these same four closed files. Exact MSHR occupancy-time, address/order-dependent L2 reuse and critical dependency-age attribution are missing; if needed later, they require separately authorized observability work, not invented zero counters or any new simulation in this task. No 48-point batch or manuscript change is proposed.

## Evidence files

MATCHED_FOUR_SOURCE_DATA.json binds full input identity, roles, exact RESULT/native-exit/raw SHA, ordered kernel counts, all printed reasons/buckets and lawful additive intervals. NEW_CH_INDEPENDENT_QUALIFICATION.json records the new actual strict/archive/native-restore verification. DERIVED_DIAGNOSTICS.json records typed means and missingness. MECHANISM_SOURCE_EVIDENCE.json binds fixed Core9eed source excerpts, and CONSUMED_COUNTER_CATALOG.json is a byte-exact copy of the already frozen catalog. Scripts/reports remain solely in this new 164 directory; no raw logs/traces are copied or committed.
