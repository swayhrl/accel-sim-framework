# Classification methodology and evidence V1

This taxonomy supports architecture selection; it is not an application-performance model trained on the final EP speedup. It classifies exact input/configuration observations and preserves uncertainty.

## Population and identity

The frozen observation-guided population has 103 rows: 96 input/content groups plus seven unresolved slots. The original representative main35 and target main42 membership flags remain independent populations. These are not 103 independent workloads. A new accepted execution is linked only through exact input SHA, full Source5 (Core/framework/vendor/ELF/static library), literal ordered commandlist and kernel identities, mode, geometry, clocks, full effective configuration, observer scope and complete-application acceptance. A program name is display metadata, never a join key.

A row may retain several conflicting-looking observations when Source, clock, geometry or mode differs. These are separate strata. Source78, Core862, Core812 and Core7b4 are never pooled as one performance baseline. Historical Motivation/Streaming summaries without exact input and ordered commandlist binding remain a separate, identity-unresolved historical appendix.

## Three independent axes

1. **Memory-service sensitivity** uses a same-Source, same-input, same-mode pair with only a declared memory-service perturbation. Report both cycles and the exact clock/latency change; classify a positive/negative/no cycle response, without inventing a universal high/low threshold. A DRAM-frequency response conflates several modeled service effects; it is not completed physical bandwidth. EP S/F speedup is a validation outcome, never an input to this axis. Absent a legal service pair: UNKNOWN. A high request count or DRAM ingress byte count alone is not measured sensitivity.
2. **Temporal reuse and retention opportunity** separates an exact-input sector temporal reuse census, realized EP retained-sector service and capacity response. Exact-input reuse-distance or eviction/revisit evidence is needed to classify the full program opportunity distribution. A positive Victim read-response count proves that some retained sectors were actually revisited and served by the production mechanism; it is a lower bound, not the full opportunity census and not avoided DRAM requests. Line spatial reuse is not sector temporal reuse. Tag-capacity S/S and WV/WV contrasts remain validation outcomes and do not erase a Victim-positive label when larger Tag substitutes for EP retention.
3. **W/V/M/T pressure and applicability** is multi-label. WB activity, WB data-space blocking, WAD hazards, Victim actual service, directory/bank cost, ordinary Line-MSHR blocking, descriptor blocking, per-address cap, RO eligibility, actual RO admission, merge, detach and Tag-reserved pressure are separate. A large merge ratio does not imply pressure or useful performance.

## Thresholds, scope and confidence

Presence thresholds are hardware/semantic boundaries: a valid count greater than zero means the event occurred in that measured scope; zero means none was observed in that scope. Peaks reaching the frozen resource capacity mean the boundary was reached, not that a request blocked. A peak is max-over-slices, not a simultaneous GPU occupancy. Hardware capacities come from that point's full configuration; do not import a cap from another Source/configuration.

No empirical percentile or speedup threshold is used to declare a workload intrinsically friendly. Optional ranking by measured event intensity is within a single denominator and stratum only. Do not divide head-block observations by ingress, admissions or independent UID populations. Missing or disabled observations are UNKNOWN, represented as null plus a status, never numerical zero.

Confidence levels: EXACT_MEASURED means complete accepted-application statistics bound to exact Source/input/configuration. EXACT_DERIVED means arithmetic from compatible measured operands, with formula and refs. CANDIDATE_INFERENCE means a causal prediction supported by a different Source/configuration and explicitly not yet measured. HISTORICAL_IDENTITY_UNRESOLVED and UNKNOWN prohibit matched-performance claims.

Runtime waiting counts are overlapping event/service observations. They are not summed into critical-path application cycles. Lower-level admitted payload bytes are not completed DRAM bandwidth. Cumulative summaries are selected once per final slice, never summed over repeated kernel snapshots.

## Evidence examples that test rather than define the labels

- Stencil and 3MM retain observed Victim service after G64x8 shrinks the incremental WV gain. Capacity and retention can substitute. Their same-mode capacity response and same-background S/WV response must both be shown.
- FWT has realized retained-sector service and WB resource pressure. Core7b4 cold filtering reduced observed total frontend queries by 1.076% but slowed the application by 0.628%. This rejects the tested cold-filter performance direction; it does not remove the input's reuse evidence.
- Scan has large WB activity but little realized Victim service in the measured Source78 F run. It is a useful low-realized-V contrast, not proof of absent program reuse.
- Vector4M at Core812/1700 is a measured no-activation overhead negative control. Fbaseline55925 -> Fpressure45425 cycles was achieved with pressure activations0 and optimized RO admissions0. It is not evidence that active RO performs better.
- Conv and Scan reached ordinary Line-MSHR128 and blocked on Source78. They are better pressure-policy candidates than SGEMM's high merge fraction or Vector6M's sub-cap peak. The Core812 activation condition also needs a certified candidate, non-HIT probe and ready frontend, so activation remains a hypothesis until a new complete matched application is accepted.

## Engineering and reporting boundary

taxonomy_rules.py encodes the non-circular/null-safe rules; check_taxonomy_rules.py covers missing identities, counter domains, denominator/semantic separation and a hidden configuration change. These CPU checks are not new scientific application measurements or Source protocol qualification.

Classification coverage (a traceable row exists) and effective measurement coverage (the corresponding exact observable exists) are counted separately. Only missing measurements that change the next experiment choice are requested. No new model, Trace/raw body scan, GPU action, budget registration or historical ledger edit is performed by this task.

## Reproducible deliverables

Agent A UPDATED_EVIDENCE_ROWS.json retains the103frozen rows and all newly joined exact endpoints; Agent C WV_REUSE_EVIDENCE_BY_INPUT.json supplies actual service strata and19strict source-matched contrasts. MULTIDIMENSIONAL_DECISION_SUMMARY.json pins their current byte SHAs. The finite request includes four complete283maps, exact ordered input metadata and the Agent B production-loader/parser receipt. check_request_v1.py independently checks all four maps against actual production-parser output, unchanged old282options, Source5, ordered input, fullCTA/instruction population, policy-only differences and zero execution authority. No model is run by these checks.

The current bounded evidence has only three input rows with legal matched DRAM-clock response: Vector4M andConv show positive response andBlackScholes none at850-to-1020 onSource78. This is3/103classification rows, not all measured inputs. Other service sensitivity staysUNKNOWN; do not infer compute-bound from missing perturbation. The accepted W_ONLY-to-WV controls forStencil/FWT/GEMM differ only in Victim CLEAN/DIRTY enables and can be reused as conditional V validation, not as class-definition speedups.
