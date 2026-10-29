# Workload observations: round 2 deepening

Status: READ_ONLY_ANALYSIS_COMPLETE. Zero new full-application starts, Trace/body scans, Core changes, CPU protocol tests or application NI. This is additional analysis of frozen compact evidence, not a repeat of the round-1 workload catalogue.

## What is new

1. Two exact historical publication heads and their small machine-readable evidence were recovered from GitHub, rather than treating missing local files as missing science. Motivation now has all 10 exact rows plus raw-log checksum index; Streaming has 12 sector rows and 12 trace-root locators. No raw-log target or Trace was read. Full content/ordered-command identity against Source78 remains unproven.
2. Six exact Source78 inputs now have a common positive/negative comparison including bank-operation and wait changes, WB lifecycle, same-address first-reason wait population, ordinary MSHR and descriptor pressure. These arithmetic contrasts expose why aggregate pressure relief cannot predict application cycles.
3. The follow-up gaps are ordered by decisions they can change. Existing unprojected small fields, genuinely absent measurements and missing historical identity are different cases.

## Frozen current comparison

Core `78f4b59e865b136eede74df74c44c210f5b4ca04`; Framework `9dd1ee57a83d83b56b7874bc7c716185ab52c8f7`; ELF `78d4e96bb79c776e27146bcf168d7c70cf3897ef9cb84d837d8974fec4c91b8a`. REF32x8_L100: 64 slices, 32 sets x 8 ways, same clocks, physical1168 Payload slots/slice, line-MSHR128, descriptor512, WAD128, P1. MS/B0/M0a=111; four heavy observers OFF. FWT is legal WV_ZERO_RO, not RO-F. Full input SHAs and accepted spec/validation/archive references are in ACCEPTED_ENDPOINT_PROVENANCE.json.

|Exact input prefix|Treatment|S cycles|Treatment cycles|Cycle change|Actual V read responses|Ordinary line-MSHR peak S/treatment|
|---|---|---:|---:|---:|---:|---:|
|Stencil bd0309df|F|5,242,939|4,769,712|-9.026%|4,930,616|16/5|
|3MM f9f80028|F|1,696,618|1,669,413|-1.603%|1,147,507|79/82|
|GEMM 140f6ed3|F|558,588|552,065|-1.168%|586,844|9/0|
|FWT fc3a9062|WV_ZERO_RO|181,827|178,951|-1.582%|88,069|99/103|
|Scan cf8d1c4d|F|2,162,540|2,224,142|+2.849%|5,584|128/128|
|Conv 438eefd6|F|331,234|335,088|+1.164%|44,974|128/128|

GEMM also has accepted WV550,642 cycles, S/WV=1.014430; it is a distinct input from SGEMM. V responses are actual services, not a hit rate, avoided-DRAM-request count or an independent V speedup. Maxima above are maxima over individual slices, not simultaneous GPU-wide outstanding counts. FWT treatment bank/WAD fields absent from the existing cached W projection remain null; this analysis does not refill them with zero.

## The discriminating Stencil/Scan result

**PROVEN package behavior:** Stencil eliminates 3,008,272 copy operations, decreases total logical bank operations 22.516%, and speeds up 1.099215x. It has 4.93M actual V read responses and no WB-data-space, WAD-full, descriptor-full or ordinary line-MSHR-full observations. WAD peaks7/10 are far below128. This supports W/V decomposition as a useful next question; it does not support increasing WAD or ordinary MSHR for Stencil.

**PROVEN counterexample to a cumulative-wait explanation:** Stencil cumulative bank_wait rises 800,516 -> 1,047,656 (+30.873%) while application cycles fall. Scan cumulative bank_wait falls 11,713,774 -> 7,634,131 (-34.828%), total logical bank operations fall13.261%, and WB_DATA_SPACE distinct first-block UIDs fall1,737,618 ->0; application cycles nevertheless rise61,602 (+2.849%). Conv likewise reduces bank_wait24.156% but slows1.164%. Bank-wait aggregates and slice-head observations are not exclusive application critical-path cycles. Adding their deltas cannot reconstruct the cycle delta.

**PROVEN pressure redistribution, not its critical-path cause:** Scan same-address WB first-block population increases390 ->1,913 (4.905x). Its per-reason cleared-request mean is nearly unchanged: 215,979/390=553.792 ->1,059,421/1,913=553.801 in the MS observer's request wait units; unresolved=0 for both. The increase comes from more requests encountering this reason, rather than a longer mean for that reason. WAD-full first-block UIDs increase35 ->257 and ordinary MSHR-full head observations911 ->4,677 (distinct66 ->145); descriptor peak remains402/512 with no full events. WB mean over sampled slice ticks increases10.661 ->12.895 even though WAD slice-mean range decreases54-55 ->51-52. A pooled WB-role peak72 is not an overflow of S's static WBUF16: they are different role organizations within equal physical1168.

**LIKELY useful distinction:** Stencil has substantial actual optional-data service with little metadata/WB pressure; Scan has little V service and visible pressure in resources not removed by copy elimination. That makes Stencil a positive-service control and Scan a pressure negative control. **UNKNOWN:** which retained objects, admission ordering, downstream queues or memory dependencies dominate Scan's extra cycles; whether W-only avoids that loss; how much of Stencil's gain belongs to W versus V versus M/T. Neither cumulative counts nor the unpaired S/F package settles this.

## Feature -> resource -> opportunity -> performance

- Stencil: many dirty-copy operations and actual V services -> bank operations plus retained data usefulness -> W/WV decomposition; observed F benefit, no evidence for more WAD/MSHR. Missing independent W/V contribution.
- 3MM: only39,174 S copy operations but1,147,507 V read services -> optional reuse can matter more than copy count -> V preservation candidate; modest observed F benefit. Ordinary MSHR82/128 never full; extra line-MSHRs lack direct support.
- GEMM140f6ed3: S copy6,482, ordinary peak9 and actual V service586,844F/609,858WV -> optional reuse with low ordinary miss concurrency -> cheap W-only check separates W from V; WV already slightly outperforms F. This is not proof that RO itself is harmful.
- FWT: S copy91,406, WB-space8,736 first-block UIDs, WV88,069 V read plus3,312 dirty-forward services -> mixed W pressure and optional-data reuse -> low-cost W-only against accepted S/WV. No RO-F substitution or RO inference.
- Scan: copy10,620,662 and severe S WB-space pressure removed, but same-address/WAD/MSHR populations rise and V service is small -> coupled allocation/service ordering -> W-only/WV negative control before tuning capacity. Do not call the negative F result a bug.
- Conv: S copy1,441,668, ordinary MSHR and WAD reach capacity; F still has both and modest V service44,974 -> mixed resource constraints -> isolate W/V and separately examine legal T causal witness geometry. Do not combine those geometries or infer T contribution from S/F.

## Historical evidence recovered and its boundary

Motivation publication `11cbd5a79127ad2fedf9801969a656be73fead96` exposes exact10-row CSVs, old Core2a6a315/Framework02f368, all10 raw-log hashes, and packaging-closeout evidence. The existing independent review accepted data/semantics but did not grant final packaging promotion; this analysis does not invent a later review.

Streaming publication `cdab5765b65f6e1575d9c185de127a1c1c49dd70` still identifies PREFINAL, Coreca3e7bc/Frameworkdb1c901. Its manifest binds12 completed rows to trace-root paths, config6412ba93 and raw-log SHA; Scan is absent, not zero. The original9 completed sector-event totals equal their separate old Motivation eligible-reference totals, consistent with the previously noted single-sector-total check, but not proof of same run or current input identity.

**New exact historical illustration:** FWT_7_21 has line reuse8,912,896/10,223,616=87.1795%, yet true sector temporal reuse4,980,736/10,223,616=48.7179%; 61.4450% of those temporal reuses lie beyond1024 sectors. Conv historical line reuse is77.3810%, sector temporal reuse9.5240%, and39.2745% of temporal reuses are beyond1024. Vector4M line reuse75% is entirely spatial with0temporal-sector reuse. Therefore line short-reuse bins cannot be treated as V hit-rate predictions, and far temporal reuse must not be declared absent. Historical post-eviction rereference fractions are Scan15.1967%, FWT24.7541%, Conv3.7265% over recorded evictions; these are not post-eviction distinct-distance distributions or a capacity-K capture curve.

The recovered manifests provide paths, old source/config and raw-log hashes, **not** the historical input content root plus complete ordered command/kernel identity needed to join current Source78 rows. No name-only merge is performed. Exact historical results can support their own scoped paper observation and motivate questions, but not current workload quantitative attribution.

## Minimal next work

First close B's W-only engineering qualification and D's confirmed P1 scope review. For performance decomposition, retain the proposed Stencil/Scan W-only/WV controls and cheap FWT/GEMM W-only candidates as separate not-yet-authorized science. Do not first build a universal observer.

For Scan attribution, project already-accepted compact B0/C7E/lower/DRAM fields before asking for new measurement; the present cached table lacks a synchronized critical-path attribution. If V-independent results justify policy work, bounded first-service/reclaim age by object kind is more decision-relevant than another full trace or indiscriminate capacity sweep. Historical content identity is a metadata recovery task, not a reason to simulate again.

D's reported engineering P1 (ordinary non-RO preview cannot exploit legal same-set RO detach) is a separate CPU witness under Main review. This Agent did not independently execute that test. Its effect on these accepted applications and on Stencil/Scan divergence is UNKNOWN; no causal claim here relies on it.

All ratios retain their own population. Per-reason MS waits end at known reason-clear; ANY alone ends at admission. Distinct first-block heads cannot use FT unique_requesters as an unproven demand denominator. Slice peaks are not added, retention area is not lifetime, and differing source/clock populations remain separate. Host runtime and GPU cycles are different quantities.
