# EP-L2 Main: observation-guided optimization V1

**Decision:** prioritize a bounded W-only/WV decomposition on Stencil and Scan before new structures. Prepare service-aware optional Victim reclaim as a hypothesis, not a demonstrated optimization. Keep M/T causal tests separate. Stage A and necessary Stage B reference/design preparation are complete; production collector and W-only launch qualification remain unfinished. New formal starts: **0**.

## Evidence and mechanism opportunity

|Input, exact identity in feature table|Accepted same-REF comparison|Observed opportunity|Claim boundary|
|---|---|---|---|
|Stencil bd0309df|S/F1.099215|4,930,616 actual V responses;3,008,272 S copy bank ops; WAD peak7, noWB-space block|PROVEN service and performance association; independent V contribution UNKNOWN|
|3MM f9f80028|S/F1.016296|1,147,507 V responses; little copy cost|Prioritize V study over larger WAD|
|GEMM140f6ed3|S/WV1.014430;S/F1.011816|609,858 WV V responses|GEMM input, not SGEMM; M/T addition not automatically beneficial|
|FWTfc3a9062|S/WV1.016071|88,069 V responses,3,312 dirty-forward|Legal WV only; no default RO-F|
|Scancf8d1c4d|S/F0.972303|WB-space unique heads1,737,618 to0; ordinary MSHR peak128 both|Removing one constraint did not ensure speedup; useful negative control|
|Conv438eefd6|S/F0.988499|V44,974; residual same-WB/MSHR pressure|Multiple constraints; do not attribute all losses toTag or solve by moreWAD|
|Vector6Mefced2c|F live merge74.99%|RO issued-not-ready independent-line peak70/slice; ordinary peak0|PROVEN RO path concurrency; strict required-sector pre-fill reuse UNKNOWN|
|SGEMM, distinct exact input in C table|F live merge92.82%|Same-address merge and independent-line capacity differ|Live merge is not strict Fill-before repeat or independent performance gain|

T has real accepted witnesses: Conv16x8 detach237, Conv32x4 detach1141, Vector4M32x4 detach27. These F results do not establish T independent speedup. Vector4M and Vector6M are distinct. Same-UID/set/instant full+eligible joint opportunity is missing in heavy-OFF REF; no marginal-count multiplication.

## Delivery and coverage

- [Unified compact feature table](agent_a/WORKLOAD_FEATURE_COMPACT.csv), [full provenance/features](agent_a/WORKLOAD_FEATURE_AND_OPPORTUNITY.json), [measured/missing](agent_a/METRIC_GAPS_BY_INPUT.csv).103rows cover96ordinary plus7unresolved program slots; exact35representative and42program membership retained.
- [W/V candidates and fairness](agent_b/WV_CANDIDATES.md), [M/T opportunities](agent_c/MT_OPPORTUNITY_AND_GAPS.md). Candidates distinguish measured opportunity from unimplemented hypotheses.
- [Collector/NI qualification](COLLECTOR_AND_NI_QUALIFICATION.md), [LaneO receipt](LANE_O_MAIN_READBACK.json), [Source/NI exact refs](SOURCE_AND_NI_READBACK.json).
- [Minimal science review plan](NEXT_MINIMAL_SCIENTIFIC_PLAN.md), [exact drafts](NEXT_MINIMAL_SCIENTIFIC_PLAN.json).

The feature snapshot is explicitly as of2026-10-29T01:33:10Z accepted results and01:39:47Z coverage:222accepted,110pairs;57REF endpoints=S27/F23/WV7;23S/F inputs plus7WV inputs, overlap5. This does not replace live longtail results or imply35/42/96completion. Allmissing/HOLD/technical-failure/live rows remain visible.

Historical Motivation/Streaming authority documents were recovered, but exact smallCSV/manifest/ordered-input binding and Streaming final tie-fix evidence were not. Status IDENTITY_UNRESOLVED; do not repurpose old approximate values or rescan giantTrace.

## Source, execution and safety boundaries

Core78f4b59e865b136eede74df74c44c210f5b4ca04; Framework9dd1ee57a83d83b56b7874bc7c716185ab52c8f7; ELF78d4e96bb79c776e27146bcf168d7c70cf3897ef9cb84d837d8974fec4c91b8a. Full Source5 in readback. LaneO28c2c66 docs/measurement contract received; no whole-branch/source merge. Source92, host-writeV3, MSHR64 and native/merge candidates retain separate engineering eligibility. No acceptedCore, registry, controller or oldbudget changed.

Three bounded agents worked in parallel and completed. Actual new execution was13purePython metering-reference checks; A12/B114 metadata checks are not simulator protocol tests or NI. No application launches, GPU collection, largeTrace/raw scans, production code edits or accepted-source changes. New production hooks NOT_IMPLEMENTED; their NI and measured overhead UNKNOWN.

Original LavaMD-F and SYRK-S/F longtails, dispatcher, postprocessor and finite automatic publishing remain owned by the original controller. This independent review branch never writes their Git index or results. Largeinputs/raw/permanent assets remain genuine164; only bounded documents and reference scripts are new here.

PROVEN means an accepted same-identity observation or executed reference check, within that scope. LIKELY indicates supported but unisolated explanation; UNKNOWN missing evidence; HYPOTHESIS an untested mechanism proposal. No proposed configuration is claimed to provide speedup.
