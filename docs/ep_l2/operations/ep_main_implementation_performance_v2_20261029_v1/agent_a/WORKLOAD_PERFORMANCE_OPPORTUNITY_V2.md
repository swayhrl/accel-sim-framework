# WORKLOAD_PERFORMANCE_OPPORTUNITY_V2

Status: **PASS for bounded evidence derivation; UNKNOWN for individual mechanism causality and historical/current input equality.** No new application, GPU, protocol fixture or NI run. This report adds downstream/L1 measurements and decision descriptors to Round2; it does not repeat its catalogue as a new result.

## Frozen population and execution

Accepted Source78: Core `78f4b59e865b136eede74df74c44c210f5b4ca04`, Framework `9dd1ee57a83d83b56b7874bc7c716185ab52c8f7`, ELF `78d4e96bb79c776e27146bcf168d7c70cf3897ef9cb84d837d8974fec4c91b8a`; full five-part identities, accepted outer-join references and frozen config digests are in `EXISTING_MEMORY_PATH_PROJECTION_V2.json`. Thirteen existing accepted endpoints cover six exact inputs (GEMM has S/F/WV). REF64slices/32sets/8ways, fixed1168 Payload slots per slice, ordinaryMSHR128, descriptor512, WAD128, P1, dram_latency100; MS/B0/M0a111 and four heavy observersOFF. FWT treatment is **WV_ZERO_RO**, never RO-F. No Source92, host-writeV3, MSHR64 or new P1 implementation is included.

A single bounded pass over13 named validated compact JSONs read6,349,410bytes. SHA, Source5, exact input, accepted endpoint cycles,282config count, snapshot scopes and hardware drain were checked. Existing accepted endpoint outer joins are reused, not inferred from the intermediate bundle's pending-acceptance status. Thirty-nine additional B0/DRAM byte-population and64-slice sample closure checks PASS. This is offline metadata/arithmetic verification, not CPU protocol, NI, application acceptance or a new experiment. No raw/Trace bodies, models or old controllers were opened or changed. Initial schema inspection reread one563,699byte Stencil compact bundle; execution records distinguish those reads from the final13-endpoint pass.

## Newly established memory-path contrasts

|Input/treatment|S/treatment cycles ratio|Successful DRAM read bytes S?treatment|Read change|Write change|Lower FIFO full observations S?treatment|MissQ full observations S?treatment|
|---|---:|---:|---:|---:|---:|---:|
|Stencil/F|1.099215|209,495,744?111,164,576|-46.94%|-0.15%|0?0|0?0|
|3MM/F|1.016296|12,161,920?8,984,704|-26.12%|-17.05%|0?0|0?0|
|GEMM/F|1.011816|3,160,704?1,080,704|-65.81%|-99.69%|0?0|0?0|
|FWT/WV|1.016071|7,414,144?4,614,016|-37.77%|+30.11%|1?188,426|1?190,082|
|Scan/F|0.972303|685,009,088?684,928,896|-0.0117%|+0.00023%|3,344,063?24,681,903|3,441,878?26,489,672|
|Conv/F|0.988499|82,699,456?81,382,112|-1.59%|+0.00885%|394,681?891,687|395,168?936,658|

These are successful transfer byte counts within the declared commandlist plus hardware drain, not automatically all program stores flushed to DRAM. Resident dirty state need not be flushed by the accepted contract; in particular GEMM's dramatic completed-write reduction is not proof those stores disappear. Causal avoided traffic from V alone is UNKNOWN. Actual V sector bytes and DRAM byte reduction differ in population and must not be equated.

**Stencil versus Scan, beyond the prior bank-wait paradox.** Stencil's read traffic falls98,331,168bytes while write traffic is nearly constant. Sampled lowerQ peak falls40?17; MissQ peak stays4. Credit, scheduler causal/full, ReturnQ full, lowerFIFO full and MissQ full observations are all0. Actual V reads are4,930,616;3,008,272 logical copy ops disappear. The package both serves substantial data locally and lowers successful lower-memory demand, without evidence for enlarged WAD/MSHR/lower queues. Its bank_wait increase is not contradictory: those accumulated slice events are not exclusive application stalls.

Scan's completed DRAM traffic is effectively unchanged. Its reported transfer utilization remains high,82.073%?79.795%, with scheduler occupancy reaching128 in both modes. Scheduler full channel-cycles actually fall18,437,167?17,526,115; causal scheduler-block observations fall36,468,083?34,147,325. Nevertheless lowerFIFO-full observations rise7.38?, MissQ-full7.70? and L1 MissQ-full reports50,009,599?70,515,328. Ordinary L2 line-MSHR peak stays128, descriptor peak402/512. The package removes10,620,662 copy ops and the S WB-data-space first-block population, but that relief does not remove lower-memory service demand or all admission/queue pressure. These are **PROVEN pressure redistribution observations**; **LIKELY** upstream relief allows pressure to accumulate elsewhere. Whether that redistribution is the cause of+61,602application cycles remains UNKNOWN. Scheduler/full/credit counters are not exclusive waits and cannot be added to explain the cycle delta.

The new evidence rejects a useful but overbroad hypothesis: Scan is not merely missing enough WB-copy relief. It also rejects the converse shortcut that more observed queue blocking must always cause a slowdown: FWT WV speeds up1.607% despite new lowerFIFO/MissQ blocking and30.11% more completed write bytes. The order, population and dependency position of service matter.

## Resource constraints and opportunity descriptors

1. **Actual optional-data usefulness together with preserved service headroom** is a supported retrospective discriminator. Stencil has4.93M V read responses with no sampled lower-resource full events. Scan has5,584 V read responses despite16,316,924,436retention slot-ticks; its V read-response density is approximately372? lower than Stencil's. This is service count per retention area, not hit rate, average lifetime or port throughput. It suggests prioritizing W-only/WV decomposition and object usefulness before expanding retention or queues.
2. **Avoided successful DRAM demand matters only when it has application leverage.** 3MM and GEMM reduce read bytes26.12%/65.81%, but improve only1.63%/1.18%. Their reported aggregate transfer utilization is low (S1.124%/0.832%; treatment0.862%/0.255%). This rules out aggregate bandwidth saturation as their universal explanation;3MM nevertheless has bursty scheduler-full observations, so low average bandwidth does not prove no local congestion. Core issue, scoreboard and critical-path evidence is insufficient to label either compute-only limited. GEMM W-only remains a cheap, useful discriminator, not a predicted large win.
3. **Capacity maxima alone poorly predict W/V value.** Scan and Conv have lowerQ/MissQ/MSHR and WAD reaching capacities and small traffic reduction. FWT also reaches lowerQ/MissQ/scheduler capacity yet benefits. Stencil does not require any of those maxima for its largest measured package gain. Do not turn these maxima into a parameter scan.
4. **Copy count and aggregate bank wait alone fail as predictors.** Round2 established Stencil speeds up while bank_wait rises, Scan/Conv slow while bank_wait falls, and3MM has little copy volume yet V service. The new downstream byte counts supply a concrete demand distinction rather than a claim that every unmeasured negative result is a bug.

These six cases were selected after observing outcomes. Their V service and traffic changes are post-treatment data, not independently validated pre-run predictors. No regression, cutoff or35/96-population speedup is claimed. For a prospective predictor, require an independently frozen input set and either exact same-input historical locality identity or measured per-kind optional first-service/reclaim usefulness, then validate it out of sample.

## What did not saturate, and what remains unknown

**PROVEN within these reported sampling populations:** all13endpoints have0c7d credit-block and0DRAM ReturnQ-full channel-cycles. Stencil/GEMM have0scheduler-full, lowerFIFO-full and MissQ-full events; no ordinary line-MSHR or WAD expansion has direct evidence there.3MM lowerQ peak reaches128 yet its full-denial counter is0, illustrating that sampled max and actual denial differ. None of this proves all resource stalls were instrumented or no unsampled microburst existed.

Tag allocation-refusal observations exist for Scan(S551/F1090) and Conv(S42717/F37279), with sampled per-set RESERVED peaks8/8. These are repeated production precheck/allocation observations, **not** independent NEW requests, joint eligibleRO opportunities, actual detach or speedup. Stencil/3MM/GEMM/FWT show0such observations and lower peaks2/5/2/6. Heavy exact joint observers areOFF; do not fill missing joint data with0. D's ordinary-request preview P1 has CPU evidence but its incidence/cycles contribution here is UNKNOWN. Conv's separate16?8three-arm experiment must use one newELF; none of the current32?8 S/F numbers can fill those arms.

The compact scopes are application-final64L2-slice B0/M0 and32DRAM-channel records; B0 sample sums equal64?application cycles. DRAM full cycles/transfer denominators are in the DRAM domain; B0 head/stage observations use their own CORE/L2 event scopes. L1 counters include failure/retry event reports that can exceed accesses; they are not unique request counts or exclusive stall cycles. Integer occupancy averages are preserved as per-resource ranges, not falsely precise weighted means. Per-kernel critical-path windows and exact fixed-delay residence decomposition are not available in this projection; an ordered kernel catalog alone cannot provide them.

## Historical locality identity: incremental review, no invented join

The previous round already recovered Motivation10 and Streaming12smallCSV rows at `11cbd5a79127ad2fedf9801969a656be73fead96` and `cdab5765b65f6e1575d9c185de127a1c1c49dd70`. V2 inventories the manifest fields explicitly: trace paths, historical Core/Framework/config, rawlog SHA and observer snapshot policy exist; input content-root and complete ordered commandlist/kernel-content binding do not. Current exact input SHA/catalog digest cannot establish the missing historical half. Same path, name, event total or size is insufficient. **Status remains UNKNOWN**. Historical-only line/sector reuse observations remain usable under their original source/PREFINAL bounds and are not inserted into currentSource78feature rows. No new GitHub traversal or Trace scan was performed to rediscover known files. The minimum next step is custodian metadata recovery; if unavailable preserve UNKNOWN.

## Minimal next decisions

First B closesW-only formal engineering qualification; request the cheap **FWT W-only and GEMM W-only2points**, conditional on separate exact scientific approval. They reuse acceptedS/WV only if allSource5/input/geometry/observer/config/mode contracts match. Conditional Stencil/Scan W-only/WV4points then distinguish the strongest useful-service example from the strongest pressure negative control. A universal new collector is not a prerequisite for these cycles comparisons.

C/D's same-newELF Conv16?8F?T/Legacy-F/Corrected-F is independent and must not share oldELF arms or budgets. If D qualifies a correction, no numerical performance improvement is assumed beforehand. Service-aware reclaim remains a candidate, not a fix or merged policy; first prove independentV benefit. Only if subsequent results leave a policy decision unresolved should a minimal served-at-reclaim or bounded service chronology collector be prepared with separateS/WV/F NI and newSource identity.

All actions proposed above have0launch authorization in this Agent's task. This delivery is completed read-only research plus small derived evidence. Full exact values and evidenceSHA are in the adjacentJSON/CSV/manifest.
