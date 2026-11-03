# Conv three-arm kernel and resource attribution V1

Status: PASS for bounded offline extraction, identity checks and arithmetic. PARTIAL for causal resource attribution. New simulation starts: 0. New collector/source/binary changes: 0.

## Frozen comparison and evidence

All arms use Core `1e07b263ca0879798387d2a712914a914f298775`, Framework `9dd1ee57a83d83b56b7874bc7c716185ab52c8f7`, ELF SHA256 `54c3fbba9bb152d1a26539cccb617ac4a3368547a06509f427a202eeda6d8505`, the same Conv input `438eefd67b073f1ca0e2c08be6aa99b3b9b9619d7832cc6cad9cc4467e63654e`, 283 effective options, 64 slices x 16 sets x 8 ways, dram_latency=100. A=F_MINUS_T; B=LEGACY_F; C=CORRECTED_F. Same-arm OFF/ON NI results report all application/model equality fields true. NI does not prove strict demand-unique NEW or complete UID-to-event ordering.

Existing small sources: E/analysis/primary_v1/{ACCEPTED_PRIMARY_AND_MATCHED_REFERENCE_METRICS,T_KERNEL_CYCLE_DECOMPOSITION,T_PRIMARY_KERNEL_RECORDS}.json, E/control/MECHANISM_METRICS/*CONV*ON*.json, E/control/NI_RESULTS/*.json. E is /root/data/ep_l2_full_workload_performance_20261027_v1/execution_v2_20261103_v1. Exact evidence SHA/byte counts are in DELIVERY_MANIFEST.json and T_KERNEL_TAG_JOINT_AND_RO_BOUNDARY.json.

Main specifically approved a bounded missing-kernel-resource read: one streaming pass through each of the three accepted OFF compressed raw files, retaining only existing EPL2B0V1/EPL2M0AV1 scope=kernel records. Actual decompressed bytes: 36,572,994; hard cap: 67,108,864. Both compressed and decompressed raw SHA were matched to each accepted point; point/spec SHA, Source5, input and 283-option count checked. Retained per arm: 128 B0 and 128 M0 records (64 slices x 2 kernels). No Trace read. No ON raw reread. Reusable summary: T_ACCEPTED_OFF_KERNEL_RESOURCE_RECORDS.json. This avoids a second scan by Main/D.

## Kernel result: the improvement is in the successor kernel

| Actual GPU cycles | A | B | C | B-A | C-B | C-A |
|---|---:|---:|---:|---:|---:|---:|
| Rows |174205|176424|177078|2219|654|2873|
| Columns |188456|190570|187262|2114|-3308|-1194|
| Remaining total minus printed kernels |130|158|123|28|-35|-7|
| Complete application |362791|367152|364463|4361|-2689|1672|

PROVEN: B/A cycles rise 1.2021%; C/B fall 0.7324%; C/A rise 0.4609%. Identical 714,547,200 instructions and complete application acceptance bound the comparison. The final residual is arithmetic, not asserted pure hardware drain or any particular queue's latency.

PROVEN: all observed successful relief outcomes occur in Rows, while the C/B performance gain occurs in Columns. The final GLOBAL TP `route_joint` already retains phase: ep-l2-detach-diag.h:248 maps phase 2/3 to the sole active kernel UID 1/2; ep-l2-tagpressure-diag.h:110-136 and :266-290 encode/print slice, phase, raw, reserved count, requester, structural eligibility, production route, admission, early reason and multiplicity. The frozen kernel_catalog=[1,2]. This is a joint head-cycle population; repeated visits by one waiting request remain repeated observations.

| Rows TP head-cycle observations | A | B | C |
|---|---:|---:|---:|
| Raw RESERVATION_FAIL and R=8 |136627|148539|146882|
| Structural eligible RO present at that same head/set/tick |27333|13012|724|
| Structural-eligible head admitted |3|237|360|
| Production route CONSULTED_MISS |0|237|360|
| Of those: certified RO requester / non-RO requester |0 / 0|237 / 0|297 / 63|

| Columns TP head-cycle observations | A | B | C |
|---|---:|---:|---:|
| Raw RESERVATION_FAIL and R=8 |174918|174399|173721|
| Structural-eligible same-head opportunities |0|0|0|
| Production route CONSULTED_MISS |0|0|0|

The per-phase CONSULTED_MISS totals equal the whole-application detach_success counts 0/237/360 exactly. Corrected-F demonstrates a real ordinary-request path (63 observed ordinary successful relief outcomes), alongside 297 RO-candidate outcomes. These are production event closures; they are not a complete later UID completion chain or strict demand-unique population. The 12,536 ordinary eligible B head-cycle observations versus 126 C observations do not mean 12,410 independent requests were recovered; successful early progress changes subsequent retries/populations. A structural eligibility can be present with T disabled; it is not an executed T success. Raw preview TagFAIL is not the same population as backend TagFAIL commits or final frontend TAG_SET_PENDING.

## Cross-kernel state: strong evidence, limited attribution

PROVEN: the maximum last successful RO response commit across all 64 slices is A=172596, B=174632, C=175007 physical GPU cycles, preceding Rows end by 1609/1792/2071 cycles. ep-l2-ro-runtime.inc:396-400 sets last_response_cycle only on successful runtime response commit; ep-l2-ro-transactions.h:300-313 performs descriptor release/waiter erase/retirement check. It is not a DRAM fill timestamp and not a direct live-transaction census at kernel boundary. Do not infer Columns P1 query=0: an ordinary full-tag head may still pay a query that finds no eligible RO.

PROVEN: L1 flush=1, L2 flush=0, concurrent_kernel_sm=0. gpu-sim.cc:840-845 declares the flush controls; :2306-2339 guards L2 flush on that option. `set_kernel_done` (:1077-1095) snapshots B0/L1 rather than rebuilding the L2. l2cache.cc:2299-2323 records/erases observer baselines; it does not flush Tag/Payload/TVD/WAD/queues. RO begin/end is whole-commandlist, not an automatic per-kernel epoch reset (ep-l2-ro-runtime.inc:414-426). Therefore earlier policy decisions can affect successor cache/replacement/TVD and memory scheduling state.

LIKELY: the Columns cycle difference is mediated by state/schedule changes inherited from the earlier stage, plus any continuing ordinary-query costs; it is not direct Columns detach acceleration. UNKNOWN: which cache/TVD lines, queue ordering, dirty victims, or arrival schedule carry the benefit. The current evidence contains no boundary state diff or request critical-path graph. Last RO response and zero Columns eligible/relief jointly narrow the path, but are not a standalone proof that every kind of RO state was zero at Rows boundary.

## Per-kernel resource evidence

All below are sums of the same counter across 64 slice kernel_shared_delta records. They are not exclusive global GPU stall cycles. Scheduler events occur in the DRAM admission/probe domain; frontend heads in L2 domain; bank waits use physical service cycles. Neither domain conversion nor division by 64 yields critical-path cycles.

| Resource counter | Rows B | Rows C | C-B | Columns B | Columns C | C-B |
|---|---:|---:|---:|---:|---:|---:|
| Final-plan tag-set pending block |147483|145487|-1996|173761|172450|-1311|
| Payload bank wait |405626|403988|-1638|381958|386033|4075|
| L2 MissQ full observations |1327|1999|672|10339|10358|19|
| L2-to-DRAM FIFO full observations |1146|1811|665|10278|10304|26|
| Scheduler causal block observations |978400|962620|-15780|92663|90151|-2512|
| DRAM successful read bytes |41765536|41684160|-81376|43849440|43998976|149536|
| DRAM successful write bytes |36761344|36750848|-10496|37998048|38022368|24320|
| M0 any-blocked head observations |1503882|1500212|-3670|184100|182808|-1292|
| M0 observed heads |4245255|4239677|-5578|2870313|2875557|5244|

PROVEN: Rows gets fewer tag/bank/scheduler block observations and fewer DRAM bytes yet is 654 cycles slower. Columns gets more bank/MissQ/FIFO exposure and more transferred bytes yet is 3308 cycles faster. This rules out deriving kernel cycles by summing or subtracting these counters, and rules out describing Columns improvement as a measured traffic-reduction effect. M0 tag-block/observed-head ratios can be computed using each arm/kernel's own M0 denominator; do not divide TP counts by M0 population (handled/exempt paths differ). Scheduler blocked observations may be normalized only by that same kernel's c7e_dram_issue_attempt, not by request count or GPU cycles as an exclusive stall fraction.

PROVEN: source delta semantics are explicit: l2cache.cc:1965-2036 subtracts kernel baseline counters/histograms; :2037-2055 reconstructs interval maxima; :2366-2387 selects kernel_shared_delta and bank snapshot delta. All retained B0 records report overlap_detected=0. Kernel intervals are timing intervals, not an ownership classifier for every downstream response; in-flight work across a boundary can be charged to the interval where it executes. Source producer semantics are retained rather than treating snapshots as reset model state.

## Application-level tradeoffs and nonsaturation

PROVEN: C/B V read responses fall 63634 -> 62169 (-1465), directory queries rise 1792427 -> 1799733 (+7306), clean installs rise 878519 -> 886624 (+8105), and same-address WB waiting exposure rises 4243639 -> 4441624 (+197985). RO merged requesters fall 948150 -> 945536 (-2614), while RO transactions rise 406596 -> 406811 (+215). Lower read bytes rise 68160 and successful write bytes rise 13824. These are real policy-induced workload/path changes, not proof that a specific one causes the cycle result. Per-kernel V/RO lookup and same-address WB waiting decomposition remains UNKNOWN in the reused summaries.

PROVEN: aggregate P1 cost is 2954 issued / 2954 paid_wait_gpu_cycles / 0 port-wait attempts in C. It is a sum of slice/query exposure, overlaps other work, shares the RO frontend query resource, and cannot be deducted from 364463 to construct a free-query GPU counterfactual. A/B P1 counters are zero by mode. Physical 1-cycle timing and PPA remain UNKNOWN.

PROVEN within measured populations: application descriptor max A/B/C=356/349/350 <512; ordinary Line-MSHR max=107/109/111 <128, with zero recorded full-block events. Descriptor/per-address full, Bank-compatible landing, WB_DATA_SPACE, frontend transaction and response queue block counters do not identify a saturation problem here. Credit/return-queue block events are zero in B0's recorded issue population. WAD reaches128; MissQ and lower FIFO reach128; scheduler reaches128; set RESERVED reaches8. These are observed pressure sources. Max reaching capacity is not duration at capacity and no global bottleneck ranking follows just from maxima.

Important population check: B0 c7d_wad_hazard_wait_cycles=0 coexists with nonzero SAME_ADDRESS_WB request waiting. The handled TVD/WB path and the ordinary B0 precheck sample different populations. A zero B0 subcounter must not erase the positive same-address wait evidence or imply WAD never delays a request. Payload capacity/landing counters are zero where sampled, but no claim of all-path free payload service is made; physical bank contention is observed.

## Scientific decision and minimal next step

PROVEN result: corrected ordinary-request T functionality now executes safely in accepted Conv and raises observed detach, but it does not beat matched F_MINUS_T for this input/configuration. Keep the repair as an engineering candidate with its explicit cost/guard contract; do not sell increased detach as acceleration or make T universally default on performance grounds.

Next, no new full simulation is necessary for this attribution pass. Reuse the exported kernel resource summary and phase joint table in the Main report. If a later exact new-Source collection is independently authorized, the smallest useful missing instrumentation is per-kernel P1 issued/wait and per-kernel V query/service/same-address-WB interval counters plus a compact Rows-end Tag/TVD/WAD/queue census. Preserve existing paid resource semantics and same-mode OFF/ON NI. A CPU two-stage fixture can test persistent Tag/TVD identity and query reset across a kernel observer boundary without claiming application performance. No Stage-C/D experiment, tag shrink, queue expansion, delay scan, or new collector has been executed here.

The specific hypothesis to distinguish is indirect carryover versus direct local relief cost/benefit, not whether one can manufacture more detach. Any later application intervention must retain the same ELF/background resources and explicitly scope query/relief behavior; resetting caches or forcing kernel drain changes the model and is not a free attribution control.
