# Same-version P0: ATAX / MVT / BICG CH versus DH

Source: the **same 129-log closed-only scan**, UTC 2026-10-27T11:48:59.998479+00:00; SHA `16d8116967884d021151964fd8590f88ffccdb1ee8ee553b1b01571263bb0d1e`. This table performs **zero raw rescans and zero model starts**. Six result byte snapshots were re-read and matched to the scan’s immutable result SHA.

All six are legal downstream18 P0 references with exact Core `9eedb3131937748f0492fa83aad37d3691118d70`, Framework `02775fd795cde5aae1480d81cee6eb481d0a08f4`, binary `02a289360b42a573832698c978f21ad2125182a453067a35be60410f1eb8888d`. DRAM is 850MHz and L2 is the common baseline. CH/DH retain their disclosed different L1 designs; this is not an equal-area claim.

## Raw counters

| Program | Design | Cycles | L2 accepted read sectors | L2 read miss sectors | DRAM read atoms | Entry fail | Merge fail | Miss-queue fail | Line-alloc fail |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| ATAX | CH | 28,428,842 | 65,889,456 | 16,720,180 | 16,720,180 | 26,793,345 | 2,206,900 | 7,111,605 | 3,213,805 |
| ATAX | DH | 31,880,220 | 49,155,352 | 19,387,556 | 19,387,556 | 139,657,561 | 17,636 | 18,806,950 | 335,494 |
| BICG | CH | 26,298,698 | 64,586,544 | 15,513,224 | 15,513,224 | 39,160,496 | 1,717,571 | 10,086,344 | 6,064,345 |
| BICG | DH | 28,685,812 | 44,804,596 | 17,688,864 | 17,688,864 | 142,533,205 | 15,401 | 15,514,452 | 347,238 |
| MVT | CH | 26,581,175 | 65,311,172 | 15,617,216 | 15,617,216 | 29,115,010 | 880,332 | 5,560,281 | 3,262,847 |
| MVT | DH | 34,687,540 | 48,510,772 | 20,574,896 | 20,574,896 | 108,621,212 | 18,837 | 52,360,071 | 529,671 |

Read sectors and DRAM atoms are 32B. Reasons above are **GLOBAL_ACC_R** only, with literal labels `MSHR_ENRTY_FAIL`, `MSHR_MERGE_ENRTY_FAIL`, `MISS_QUEUE_FULL`, `LINE_ALLOC_FAIL`. Write-side reasons are not silently folded into this read table. Unprinted reasons would remain None.

## Attempt intensity

| Program | Design | Entry / accepted read | Merge / accepted read | Miss queue / accepted read | Entry / core cycle | Merge / core cycle | Miss queue / core cycle |
|---|---|---:|---:|---:|---:|---:|---:|
| ATAX | CH | 0.406641 | 0.033494 | 0.107932 | 0.942471 | 0.077629 | 0.250155 |
| ATAX | DH | 2.841147 | 0.000359 | 0.382602 | 4.380696 | 0.000553 | 0.589925 |
| BICG | CH | 0.606326 | 0.026593 | 0.156168 | 1.489066 | 0.065310 | 0.383530 |
| BICG | DH | 3.181218 | 0.000344 | 0.346269 | 4.968770 | 0.000537 | 0.540841 |
| MVT | CH | 0.445789 | 0.013479 | 0.085135 | 1.095324 | 0.033119 | 0.209181 |
| MVT | DH | 2.239115 | 0.000388 | 1.079349 | 3.131419 | 0.000543 | 1.509478 |

These are repeated rejection/retry attempts aggregated across subpartitions. They are **not** unique transactions, a miss probability, a queue waiting time or a fraction of application cycles. More than one attempt per accepted sector/cycle is possible.

## Descriptive association only

| Program | DH/CH cycles | DH/CH accepted reads | DH/CH DRAM reads | DH/CH entry fails | DH/CH miss-queue fails |
|---|---:|---:|---:|---:|---:|
| ATAX | 1.121404 | 0.746028 | 1.159530 | 5.212397 | 2.644544 |
| MVT | 1.304966 | 0.742764 | 1.317450 | 3.730763 | 9.416803 |
| BICG | 1.090769 | 0.693714 | 1.140244 | 3.639719 | 1.538164 |

DH has fewer accepted L2 read sectors but more DRAM reads and considerably more observed MSHR-entry retry attempts in these P0 inputs. This localizes visible pressure to entry admission and miss-queue paths rather than merely assuming merge capacity is limiting. It does **not** prove that expansion speeds up DH, that the attempts cause the full CH/DH cycle gap, or that queue populations/order match across the two L1 designs. No missing or unfinished L2 variant is substituted.

## Complete provenance

| Program | Design | Full frozen input SHA | UUID | Result SHA |
|---|---|---|---|---|
| ATAX | CH | `eededb785179fc0488c5a01d95154f6748ea45a2ea7bb18ecdbc316cf5166950` | `681b81cd-4add-4802-a5f0-1994b9156847` | `5364ea570de11a9929d5107c259a2cdbd9d440ea0b71ed178a75b34a04944be2` |
| ATAX | DH | `eededb785179fc0488c5a01d95154f6748ea45a2ea7bb18ecdbc316cf5166950` | `37325f35-2eb7-4a2b-bba9-5dc5d00e497f` | `7a0df4d27305dab8ae9da64a2cbfe51c0c01d6d0c8cf2e91243a7ce471ef3ab2` |
| BICG | CH | `ae34174fbbdf83b20a72f44492665cf4b99ed35563f482f7d14763e89f398aef` | `f93c0c73-fc16-496b-9021-87ba236f60c2` | `dded01863187729a3a7d98f74418f2602eedd0490c11c3faeeef9adfaa8f47a8` |
| BICG | DH | `ae34174fbbdf83b20a72f44492665cf4b99ed35563f482f7d14763e89f398aef` | `fbb45ea4-716d-46f5-abfb-2842f03a8e99` | `78f79fa1898c45e4769ee10e0043bf2840507023da46882bd168d914b6584216` |
| MVT | CH | `f437190767aaed4921e11e6b85f80fb3348da90ec0f18fa8fa1bdfcd76ae3079` | `bde2fff3-0d42-4920-a97c-1ed7a5be1df1` | `12718f4e83f007d846e10bcb0778b29f62cbe5af2797b932024945601f3860a8` |
| MVT | DH | `f437190767aaed4921e11e6b85f80fb3348da90ec0f18fa8fa1bdfcd76ae3079` | `93cd6c4f-02cf-4e47-9a73-cba755167f47` | `198efde39a9f29222f80e6bda521aa1a28dd281a6e649999505af60cbe06d162` |

The JSON companion contains source result paths, full cohort names, original natural-DONE/strict/archive ancestry, compressed and uncompressed raw SHA, and exact final per-stream reason lines/kernel UID. Nothing was inferred from the name of the workload or an absent field.
