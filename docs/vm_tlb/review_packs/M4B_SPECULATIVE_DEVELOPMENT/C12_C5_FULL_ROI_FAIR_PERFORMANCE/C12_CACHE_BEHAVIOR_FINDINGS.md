# C12 cache-behavior checkpoint — terminal F0 only

Scope: `MEASURED_FULL_ROI_FACT`. This checkpoint reads only the terminal-PASS C12 Prefill F0 and Decode1 F0 raw logs. It neither runs nor changes any simulator input.
The C5 F0 execution identity is the formal baseline; C4/Window-A values are not mixed.

## Provenance and formulas

- Prefill F0 raw-log SHA-256: `8f7bbc5a0e1263ca264c2b4f892d4bc4e02faf570cfd7df327b98a27ac326db7`.
- Decode1 F0 raw-log SHA-256: `96097ee02fff4b31219339bf673e53af826d8b9c98cb3dd1d3657767b8e0025d`.
- Locality counters sum the emitted full-ROI `m4c_telemetry` (L1D) or `m4c_telemetry_l2` (L2) records for each requested class/event.
- `hit/(hit+miss) = raw_hit / (raw_hit + raw_miss)`; `hit/(hit+miss+reservation_fail) = raw_hit / (raw_hit + raw_miss + raw_reservation_fail)`.
- Replacement counters sum `m4c_telemetry_l2_replacement`. `row_share = raw / incoming-row-total`; `total_share = raw / all-emitted-replacement-total`. `DATA_UNKNOWN` is kept verbatim and is **not** renamed Activation.

## MEASURED_FULL_ROI_FACT

### Weight locality

prefill L1D DATA_WEIGHT: hit=1980870, miss=247354, reservation_fail=0, hit/(hit+miss)=88.8991%, hit/(hit+miss+reservation_fail)=88.8991%.
decode1 L1D DATA_WEIGHT: hit=896, miss=7111808, reservation_fail=2253776, hit/(hit+miss)=0.0126%, hit/(hit+miss+reservation_fail)=0.0096%.
prefill L2 DATA_WEIGHT: hit=46410056, miss=47717680, reservation_fail=2893426, hit/(hit+miss)=49.3054%, hit/(hit+miss+reservation_fail)=47.8350%.
decode1 L2 DATA_WEIGHT: hit=19264, miss=16090942, reservation_fail=2307674, hit/(hit+miss)=0.1196%, hit/(hit+miss+reservation_fail)=0.1046%.

### KV-cache locality

prefill L1D DATA_KV_CACHE: hit=1762, miss=3289374, reservation_fail=0, hit/(hit+miss)=0.0535%, hit/(hit+miss+reservation_fail)=0.0535%.
decode1 L1D DATA_KV_CACHE: hit=129864, miss=1390616, reservation_fail=0, hit/(hit+miss)=8.5410%, hit/(hit+miss+reservation_fail)=8.5410%.
prefill L2 DATA_KV_CACHE: hit=2701396, miss=1392452, reservation_fail=805318, hit/(hit+miss)=65.9867%, hit/(hit+miss+reservation_fail)=55.1399%.
decode1 L2 DATA_KV_CACHE: hit=2797354, miss=611880, reservation_fail=139840, hit/(hit+miss)=82.0523%, hit/(hit+miss+reservation_fail)=78.8193%.

### L2 replacement rows relevant to Weight/KV/UNKNOWN

prefill incoming=DATA_WEIGHT -> victim=DATA_WEIGHT: raw=16270184, row_total=32638696, row_share=49.8494%, total=89736578, total_share=18.1311%.
prefill incoming=DATA_WEIGHT -> victim=DATA_UNKNOWN: raw=16365538, row_total=32638696, row_share=50.1415%, total=89736578, total_share=18.2373%.
prefill incoming=DATA_WEIGHT -> victim=DATA_KV_CACHE: raw=674, row_total=32638696, row_share=0.0021%, total=89736578, total_share=0.0008%.
decode1 incoming=DATA_WEIGHT -> victim=DATA_WEIGHT: raw=11469162, row_total=15551738, row_share=73.7484%, total=31599378, total_share=36.2955%.
decode1 incoming=DATA_WEIGHT -> victim=DATA_UNKNOWN: raw=4041936, row_total=15551738, row_share=25.9903%, total=31599378, total_share=12.7912%.
decode1 incoming=DATA_WEIGHT -> victim=DATA_KV_CACHE: raw=39312, row_total=15551738, row_share=0.2528%, total=31599378, total_share=0.1244%.
prefill incoming=DATA_UNKNOWN -> victim=DATA_WEIGHT: raw=14179598, row_total=57014926, row_share=24.8700%, total=89736578, total_share=15.8014%.
decode1 incoming=DATA_UNKNOWN -> victim=DATA_WEIGHT: raw=3758358, row_total=15937760, row_share=23.5815%, total=31599378, total_share=11.8938%.

## SUPPORTED_SIGNAL

- Weight has markedly higher measured F0 L1D locality in Prefill than Decode1; at L2, Prefill Weight is near 49.3% hit/(hit+miss), while Decode1 Weight is near 0.12%. This is a full-ROI F0 association, not an arm-level causal result.
- KV-cache L2 locality is higher in Decode1 than Prefill in this F0 checkpoint, while its L1D locality is also higher in Decode1. The raw counters and both denominator conventions are retained in the TSV.
- Replacement composition differs by ROI: Prefill incoming Weight replacements split almost evenly between DATA_UNKNOWN and DATA_WEIGHT; Decode1 incoming Weight replacements are predominantly DATA_WEIGHT. These are replacement correlations, not proof that one class causes the other class's eviction behavior.
- If these C5 F0 counters differ from Window-A/C4 characterization, no reconciliation or parameter tuning is applied: C5 uses the frozen C11 common-PA backend, binary/config/registration identity, and complete F0 ROI logs. C5 F0 is the formal baseline for this replay.

## UNRESOLVED

- `DATA_UNKNOWN` remains an instrumentation category; this checkpoint makes no Activation relabeling claim.
- Replacement rows do not establish causality, residency lifetime, or a counterfactual cache-policy outcome.
- F0-only evidence cannot determine whether candidate arms change the observed locality/replacement mix; those comparisons remain pending the 22-point C12 matrix.

The complete raw counters and all replacement rows (including PTE and OTHER classes) are in `C12_CACHE_BEHAVIOR_CHECKPOINT.tsv`.
