# Eight accepted controls: T/M nonadditivity and CFD phase effects

This revision consumes E2's requested frozen closeout `5cffabab5588c22219a7271f92e98402d6f74e1b`, its complete final audit, and E025/E026/E029/E030 current accepted receipts using the existing D intake. The original ten authorized attempts ended **30/40, eight accepted, two RAM RESOURCE_LIMIT, controller STOPPED**. All old evidence remains immutable. No trace body, native test, build, simulator or notification adapter is run by D.

**Later-state correction:** E2 subsequently published explicit two-slot DWT retry approval at `55926adae…` and qualified admission at `f9233fcd9…`. The initial live registry check recorded **31/40, E031 running, controller ACTIVE, no accepted DWT retry**. This is a subsequent resource-recovery episode, not a change to E027/E028's failed scientific status. Its exact approval and separate live readback are retained; D neither authorizes nor starts a retry. By final readback the live count reached **32/40**, with E031 independently accepted by E and E032 active; that later pair is recorded in a separate scope-only receipt and is not included in this original-ten analysis. The original-ten table and scientific results below remain bound to the 30-start closeout.

## Conv: same cycles, different resource behavior

All corners retain W+V, the same full input/main61, fixed budgets/P1 and strict client/UID/generation retry matching.

| T/M corner | Configuration | Rows cycles | Columns cycles | Total cycles | RO line allocations / avoided |
|---|---|---:|---:|---:|---|
| C00 | F_MINUS_R | 160278 | 132154 | 292432 | OFF; native RO counters absent |
| C10 | WV_T | 160984 | 130485 | 291469 | 371495 / 0 |
| C01 | WV_M | 160984 | 130485 | 291469 | 0 / 371495 |
| C11 | F | 160984 | 130485 | 291469 | 0 / 371495 |

Turning on either feature with the other OFF changes **Rows +706, Columns −1669, total −963**. Adding it with the other already ON changes **0/0/0**. The signed interaction is:

`C11−C10−C01+C00 = −706 Rows +1669 Columns = +963 program cycles`.

Thus the joint saving is 963 cycles, not the 1926 obtained by adding both either-on savings. This is a configuration-level factorial observation; it does not assign exclusive causal stall cycles to T and M.

Allocation numbers are cumulative events, not simultaneously occupied entries or additional physical capacity.

WV_T/WV_M/F each admit **1251551 RO reads**, allocate **371495 transactions**, merge **880056 requests**, issue **1179774 RO lower sectors**, perform **1179774 RO bank fills and 1251551 RO bank response reads**, and record **zero successful Tag detach**. All have **8118075 physical bank services**, **75502720 lower-read bytes**, and **69826496 lower-WB bytes**. Their paid queries, captured per-kernel service/traffic counters and observed wait aggregates also match. RO admission/query increments occur in Rows; Columns has zero new RO admission/query increments.

A recursive comparison of the exact E-accepted WV_T/WV_M parsed mechanism records finds differences only in five per-slice fields: the two switch flags, normal/avoided line allocations, and sampled peak shared lines. Each differs on 64 slices; all other parsed mechanism fields match. This bounded comparison is recorded in `CONV_TM_NATIVE_COUNTER_DIFFERENCES.json`; it is not an all-UID execution-equivalence test.

The source explains why the experiment cannot identify a detached-Tag gain: `ro_requested()` and `ro_init()` activate the common RO runtime when **T OR M** is enabled. C00 lacks that runtime; all three other corners use it. T-only therefore includes common RO-path activation even when no Tag detach succeeds. M changes real line-MSHR allocation accounting: its absence in WV_T allocates 371495 normal RO lines. Recorded RO-sampled per-slice line peaks are **63–88/128** for WV_T versus 0 for WV_M/F; Rows has zero observed line-MSHR wait in all three. This is consistent with the additional line reservations not adding an observed bottleneck on this input. Those peaks are sampled by the RO transaction observer, not a continuous proof that every native capacity check was free. Allocation/index bookkeeping itself is not a separately charged data-bank service in the reviewed source.

**Do not infer functional equivalence.** Their actual line allocation and capacity exposure differ. Equal kernel durations and matching captured service totals do not prove identical UID schedules, equivalence on other inputs, or that M never helps. Zero successful detach also does not prove zero attempts/overhead. The observed T-only improvement is not application evidence of executed Tag-detach benefit. Exact source excerpts and sampled-peak scope are retained.

The current grid has no counterfactual that keeps the common RO runtime ON while T=M=0. Its signed interaction is valid for these four configurations, but does not independently identify common-path benefit versus the pure Tag-detach or MSHR-bypass effects. This is an identification limit, not a request to add a runtime feature or another run.

## CFD: conditional benefits concentrate in flux

| Left → F | K1 | K2 | K3 | K4 step | K5 flux | Net F−left |
|---|---:|---:|---:|---:|---:|---:|
| S | +14 | +1 | +34 | +29 | −14 | **+64** |
| F_MINUS_V | +14 | +1 | +34 | +81 | −1559 | **−1429** |
| F_MINUS_R | 0 | 0 | 0 | +35 | −1690 | **−1655** |

All residuals are zero. V-enabled conditional benefit is **1559 flux cycles offset by 130 earlier cycles**, net 1429. RO-enabled conditional benefit is **1690 flux cycles offset by 35 earlier cycles**, net 1655. However, relative to the traditional S, F gains only 14 cycles in flux and loses 78 earlier: **F=79157 versus S=79093**, still 64 cycles slower (speedup −0.08085%). The two remove-one backgrounds are not the traditional baseline; no same-input W-only CFD control is present. The observations are consistent, not contradictory, and **1429+1655 is not an additive contribution to the S→F result**. Algebraically, `−1429+1493=64` on the V-removal path and `−1655+1719=64` on the RO-removal path; these identities are not a causal cost breakdown.

**Actual V-path evidence.** F serves 49962 V responses (all flux), versus V OFF in F_MINUS_V. Lower-read packets fall **212308→206462**, bytes **6793856→6606784**, and WB bytes **3978880→3835136**. RO admissions/queries remain **206448**, RO lower sectors remain **206448**, and RO bank fills/responses remain **206448 each**; transactions change 51652→51678 while merges change 154796→154770. At the complete terminal boundary, subtracting the reported RO sector subset leaves 5860 lower reads without V versus 14 in F; the 5846-packet change is outside the unchanged reported RO subset. All five-kernel V/RO-enabled results keep strict retry matching. V retention/read handling and altered load/WB arrivals are compatible with the flux gain, but 49962 responses are not 49962 independently avoided lower reads or a measured 1429-cycle direct-hit contribution. V queries are paid even in the earlier zero-hit kernels, where F has no earlier service-count saving.

**Actual RO-path evidence.** Removing RO leaves 48524 V responses versus F's 49962, but has **five fewer** lower reads (206457 vs 206462), **160 fewer** lower-read bytes, **1920 fewer** WB bytes and **7329 fewer** physical bank services. It is nevertheless 1655 cycles slower. Consequently a reduction in aggregate traffic or physical service count does not explain this conditional RO gain. F admits 206448 RO reads in step/flux, allocates 51678 transactions and merges 154770 requests, avoiding 51678 line allocations and recording zero successful detach. Observed normal line-MSHR/MissQ waits are zero throughout these CFD conditions, so avoidance counts are not evidence of relieved measured saturation.

**Timing observations, not critical-path attribution.** In flux, same-address-WB wait sums are **22972 without V, 8868 without RO, 6103 in F**; data-service wait sums are **36322, 37668, 34287** respectively. F_MINUS_V additionally records 548 response-queue wait cycles (whole-program accepted counter); its existing stage cache omits that reason, so stage localization is UNKNOWN. These nonexclusive sums are compatible with altered request/response ordering, not additive GPU stalls. Exact first-UID, per-load dependence and bottleneck critical-path timing is unavailable in current logs. It remains a hypothesis that common RO handling and V/WB state improve relevant flux response timing; it is not a demonstrated independent T/M or bandwidth contribution.

## Preserved results and qualification boundaries

The complete ten-control table retains all eight accepted endpoints and E027/E028 as **RESOURCE_LIMIT / no complete performance value**. No partial DWT cycles, speedups or intermediate kernel timings are promoted into results. Later retries have separate authorization/attempt/pair identities; E031's subsequent acceptance is recorded separately and is not backfilled into E027/E028 or this original-ten table.

Conv W_ONLY still reproduces 1407/1463=96.172% of the main net gain, not a copy attribution share; S_COPY_FREE remains adversely **739 cycles slower than S** despite exempt copy service and fixed staging delay. F_MINUS_V remains 1994 cycles slower than F. The earlier six-condition results, reports and all raw evidence remain preserved.

The four main S/F pairs remain Conv +0.502%, CFD −0.081%, DWT −0.670%, SAD +0.928%; interim four-pair GM is **1.001679**, complete original-seven GM **UNKNOWN**. No control replaces main F. All four main-F successful Tag-detach totals remain zero, and SAD's zero-copy prefix remains unexplained. The EN-v20 mother is untouched. The accompanying English paragraphs and measured plots are insertion candidates only; E remains the sole qualification and acceptance owner.
