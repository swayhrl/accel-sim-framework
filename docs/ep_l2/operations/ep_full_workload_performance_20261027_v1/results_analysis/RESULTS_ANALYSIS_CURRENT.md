# Accepted experiment results: bounded current analysis

Analysis UTC: 2026-10-30T14:17:57.395547+00:00. Registry: 227 registered; 227 consumed; states {'CLOSED_ACCEPTED': 224, 'CLOSED_UNACCEPTED': 2, 'CONSUMED_BEFORE_FORK': 1}. Independently joined CLOSED_ACCEPTED endpoints: 224. Joins cover frozen spec, natural DONE, point, canonical Source5, validation SHA and genuine164/two-native-restore receipts. No raw or Trace rereads; Main remains the acceptance authority.

Each row is an endpoint, not a distinct workload. This is a bounded snapshot; live counts may advance. There is no full35/full96 geometric mean or global-optimum claim.

Incremental refresh reuses 223 prior closed endpoints with unchanged frozen-spec SHA and exact current registry point/DONE/archive references. 1 new or changed endpoints were freshly joined. Old artifact SHA references remain the sealed prior evidence; they were not all rehashed.

## Newly closed endpoints and newly matched comparisons

This refresh reuses 223 closed endpoint references and freshly joins 1 new/changed endpoints. New fully matched pairs: 0. REF S/F coverage is 24 inputs / 23 programs. This is not completed35/96 coverage.

|new endpoint|mode|cycles|instructions|CTA|kernels|
|---|---|---:|---:|---:|---:|
|SYRK (90b0cc9d)|S|22589807|5626658816|4096|1|

|new matched input|S cycles|F cycles|S/F|F cycle change vs S|
|---|---:|---:|---:|---:|

Per-candidate fixed8 closure:
- COMBO_G64W16_UD2: 8/8; full-population GM=0.996987; missing=NONE.
- N_ICNT_BUFFERS1024: 8/8; full-population GM=0.999064; missing=NONE.
- U_L2MQ256: 8/8; full-population GM=0.999977; missing=NONE.

Only complete fixed populations receive a full GM. Actual detach occurrence remains separate from an independently attributable T speedup; same-Core/ELF/geometry/input/F WVM background T-OFF(M1) is still required.

## What the completed comparisons show

On the predeclared development3 inputs, G16x8 raises S/F GM to 1.010887 but slows F in absolute terms (REF/F GM 0.968467) and slows S still more (0.951736). It is a relative EP advantage under smaller Tags, not an absolute performance winner. The G64x16+UD2 combination improves absolute F GM to 1.078870 and S to 1.084268, while S/F remains 0.988478: most benefit is common hardware headroom. DRAM850-to1020 similarly improves absolute F GM to 1.080864 and S to 1.079279, with S/F 0.994883. These are fixed3 observations, not global conclusions.

Per-candidate fixed8 completeness is reported in the refresh section above; incomplete groups retain GM UNKNOWN. Source92 bank-ops2 evidence remains one Vector input only. The separately pinned coverage ledger carries its own older as-of; its main35/ordinary96 classifications are historical evidence, not substituted for the current joined REF coverage.

## Fixed populations and matched comparisons

S/F compares S and F on the same hardware. REF/S and REF/F compare absolute cycles within the same mode, Source, input and observer profile. A larger S/F alone does not prove a faster F endpoint. Complete-population GM is UNKNOWN until all preselected inputs close.

|profile|population|closed/required|complete S/F GM|positive/negative/equal|S absolute REF GM|F absolute REF GM|
|---|---|---:|---:|---:|---:|---:|
|COMBO_G32W16_L2MQ2|DEVELOPMENT_FIXED3|3/3|0.992405|0/3/0|1.029694|1.028639|
|COMBO_G64W16_UD2|DEVELOPMENT_FIXED3|3/3|0.988478|0/3/0|1.084268|1.078870|
|COMBO_G64W16_UD2|PRESELECTED_VALIDATION8|8/8|0.996987|1/5/2|1.017513|1.015552|
|COMBO_G64W8_L1L2MQ2|DEVELOPMENT_FIXED3|3/3|0.993775|0/3/0|1.027835|1.028199|
|COMBO_ICNT_LOWER2|DEVELOPMENT_FIXED3|3/3|0.993258|0/3/0|1.002071|1.001904|
|D_DRAM_MHZ1020|DEVELOPMENT_FIXED3|3/3|0.994883|0/3/0|1.079279|1.080864|
|D_LOWERFIFO256|DEVELOPMENT_FIXED3|3/3|0.992212|0/3/0|1.002027|1.000806|
|G16_W8|DEVELOPMENT_FIXED3|3/3|1.010887|2/1/0|0.951736|0.968467|
|G32_W16|DEVELOPMENT_FIXED3|3/3|0.995385|1/2/0|1.026835|1.028863|
|G32_W4|DEVELOPMENT_FIXED3|3/3|0.991861|1/2/0|0.928849|0.927388|
|G64_W16|DEVELOPMENT_FIXED3|3/3|0.993159|1/2/0|1.057995|1.057714|
|G64_W8|DEVELOPMENT_FIXED3|3/3|0.991854|0/3/0|1.031510|1.029881|
|N_ICNT_BUFFERS1024|DEVELOPMENT_FIXED3|3/3|0.997662|1/2/0|0.999250|1.003513|
|N_ICNT_BUFFERS1024|PRESELECTED_VALIDATION8|8/8|0.999064|1/5/2|0.999799|0.999950|
|REF32x8_L100|DEVELOPMENT_FIXED3|3/3|0.993424|0/3/0|1.000000|1.000000|
|REF32x8_L100|PRESELECTED_VALIDATION8|8/8|0.998913|1/5/2|1.000000|1.000000|
|REF_G_P1168_MSOFF|DEVELOPMENT_FIXED3|3/3|0.993424|0/3/0|1.000000|1.000000|
|SOURCE92_P1_APPLICATION_NI|SOURCE92_VECTOR_ONLY|1/1|0.999314|0/1/0|1.000000|1.000000|
|SOURCE92_P2_G32W8_L100|SOURCE92_VECTOR_ONLY|1/1|0.999741|0/1/0|0.999896|1.000324|
|UD_REQUEST_HEADROOM2|DEVELOPMENT_FIXED3|3/3|0.995954|0/3/0|1.015310|1.017896|
|U_FRFCFS256|DEVELOPMENT_FIXED3|3/3|0.992457|0/3/0|1.013638|1.012652|
|U_L1MQ32|DEVELOPMENT_FIXED3|3/3|0.997912|1/2/0|0.998848|1.003361|
|U_L2MQ256|DEVELOPMENT_FIXED3|3/3|0.993759|1/2/0|1.002772|1.003110|
|U_L2MQ256|PRESELECTED_VALIDATION8|8/8|0.999977|2/4/2|0.999457|1.000522|
|U_RETURN384|DEVELOPMENT_FIXED3|3/3|0.993424|0/3/0|1.000000|1.000000|

## Per-input changes: all signs retained

|profile|input|S cycles|F cycles|S/F|F REF/F|
|---|---|---:|---:|---:|---:|
|COMBO_G64W16_UD2|vectorAdd:ddf26d4f|69756|70956|0.983088|1.088520|
|N_ICNT_BUFFERS1024|vectorAdd:ddf26d4f|77042|77237|0.997475|1.000000|
|D_LOWERFIFO256|convolutionSeparable:438eefd6|330749|335130|0.986927|0.999875|
|N_ICNT_BUFFERS1024|VECTOR6M|112453|112662|0.998145|0.999601|
|COMBO_G64W16_UD2|HEARTWALL_81949DE8|8281|8304|0.997230|0.999639|
|G32_W16|convolutionSeparable:438eefd6|315591|313781|1.005768|1.067904|
|COMBO_G64W16_UD2|HISTOGRAM_85ECC480|74000|73987|1.000176|1.001662|
|U_L2MQ256|convolutionSeparable:438eefd6|328265|333687|0.983751|1.004199|
|COMBO_G32W16_L2MQ2|vectorAdd:ddf26d4f|75068|76052|0.987061|1.015581|
|U_L2MQ256|VECTOR6M|112761|112148|1.005466|1.004182|
|SOURCE92_P1_APPLICATION_NI|vectorAdd:ddf26d4f|77184|77237|0.999314|1.000000|
|N_ICNT_BUFFERS1024|LUD_28B97CD0|456406|456406|1.000000|1.000000|
|COMBO_ICNT_LOWER2|vectorAdd:ddf26d4f|76829|77041|0.997248|1.002544|
|G64_W16|convolutionSeparable:438eefd6|292932|291469|1.005019|1.149652|
|COMBO_G64W16_UD2|BlackScholes:09eff62b|8440|8489|0.994228|1.003652|
|N_ICNT_BUFFERS1024|DWT2D_8E07074A|72052|72078|0.999639|1.000000|
|G16_W8|vectorAdd:ddf26d4f|76585|76156|1.005633|1.014195|
|D_DRAM_MHZ1020|convolutionSeparable:438eefd6|310366|311505|0.996344|1.075707|
|U_RETURN384|vectorAdd:ddf26d4f|77184|77237|0.999314|1.000000|
|N_ICNT_BUFFERS1024|convolutionSeparable:438eefd6|332592|331581|1.003049|1.010577|
|U_FRFCFS256|vectorAdd:ddf26d4f|73895|74098|0.997260|1.042363|
|D_LOWERFIFO256|vectorAdd:ddf26d4f|76829|77041|0.997248|1.002544|
|COMBO_G64W16_UD2|VECTOR6M|101713|103820|0.979705|1.084733|
|N_ICNT_BUFFERS1024|SGEMM|353921|357466|0.990083|1.000000|
|COMBO_G64W8_L1L2MQ2|convolutionSeparable:438eefd6|312250|313616|0.995644|1.068466|
|G32_W4|BlackScholes:09eff62b|9029|8605|1.049274|0.990122|
|U_L1MQ32|BlackScholes:09eff62b|8440|8489|0.994228|1.003652|
|UD_REQUEST_HEADROOM2|BlackScholes:09eff62b|8440|8489|0.994228|1.003652|
|D_DRAM_MHZ1020|vectorAdd:ddf26d4f|65522|65797|0.995820|1.173868|
|COMBO_ICNT_LOWER2|convolutionSeparable:438eefd6|330706|334029|0.990052|1.003170|
|U_RETURN384|BlackScholes:09eff62b|8456|8520|0.992488|1.000000|
|U_L2MQ256|HISTOGRAM_85ECC480|73975|74110|0.998178|1.000000|
|N_ICNT_BUFFERS1024|GAUSSIAN_B5FC8DF0|727673|727673|1.000000|1.000000|
|U_L2MQ256|DWT2D_8E07074A|72052|72078|0.999639|1.000000|
|U_L2MQ256|GAUSSIAN_B5FC8DF0|727673|727673|1.000000|1.000000|
|N_ICNT_BUFFERS1024|HISTOGRAM_85ECC480|73975|74110|0.998178|1.000000|
|D_DRAM_MHZ1020|BlackScholes:09eff62b|8456|8520|0.992488|1.000000|
|U_L2MQ256|BlackScholes:09eff62b|8456|8520|0.992488|1.000000|
|U_L1MQ32|vectorAdd:ddf26d4f|77135|77387|0.996744|0.998062|
|U_RETURN384|convolutionSeparable:438eefd6|331234|335088|0.988499|1.000000|
|COMBO_G64W16_UD2|MERGESORT_ADD5C722|112651|112659|0.999929|1.000923|
|G32_W4|vectorAdd:ddf26d4f|75484|75583|0.998690|1.021883|
|COMBO_G32W16_L2MQ2|convolutionSeparable:438eefd6|311948|312669|0.997694|1.071702|
|U_L2MQ256|HEARTWALL_81949DE8|8356|8301|1.006626|1.000000|
|COMBO_G64W16_UD2|DWT2D_8E07074A|72042|72065|0.999681|1.000180|
|SOURCE92_P2_G32W8_L100|vectorAdd:ddf26d4f|77192|77212|0.999741|1.000324|
|UD_REQUEST_HEADROOM2|convolutionSeparable:438eefd6|332551|332711|0.999519|1.007144|
|G32_W16|vectorAdd:ddf26d4f|74823|75733|0.987984|1.019859|
|COMBO_G32W16_L2MQ2|BlackScholes:09eff62b|8456|8520|0.992488|1.000000|
|U_L2MQ256|vectorAdd:ddf26d4f|77238|76842|1.005153|1.005140|
|COMBO_ICNT_LOWER2|BlackScholes:09eff62b|8456|8520|0.992488|1.000000|
|N_ICNT_BUFFERS1024|MERGESORT_ADD5C722|112753|112763|0.999911|1.000000|
|G64_W8|convolutionSeparable:438eefd6|309924|312637|0.991322|1.071812|
|U_L2MQ256|LUD_28B97CD0|456406|456406|1.000000|1.000000|
|COMBO_G64W8_L1L2MQ2|BlackScholes:09eff62b|8440|8489|0.994228|1.003652|
|U_FRFCFS256|BlackScholes:09eff62b|8456|8520|0.992488|1.000000|
|U_L2MQ256|MERGESORT_ADD5C722|112753|112763|0.999911|1.000000|
|COMBO_G64W16_UD2|SGEMM|343063|343286|0.999350|1.041307|
|COMBO_G64W16_UD2|convolutionSeparable:438eefd6|288067|291522|0.988148|1.149443|
|COMBO_G64W16_UD2|GAUSSIAN_B5FC8DF0|728027|728027|1.000000|0.999514|
|UD_REQUEST_HEADROOM2|vectorAdd:ddf26d4f|73592|74027|0.994124|1.043363|
|G64_W16|BlackScholes:09eff62b|8456|8520|0.992488|1.000000|
|N_ICNT_BUFFERS1024|HEARTWALL_81949DE8|8356|8301|1.006626|1.000000|
|N_ICNT_BUFFERS1024|BlackScholes:09eff62b|8456|8520|0.992488|1.000000|
|G16_W8|convolutionSeparable:438eefd6|360380|367152|0.981555|0.912668|
|COMBO_G64W16_UD2|LUD_28B97CD0|456530|456530|1.000000|0.999728|
|G64_W8|BlackScholes:09eff62b|8456|8520|0.992488|1.000000|
|U_L1MQ32|convolutionSeparable:438eefd6|333223|332298|1.002784|1.008396|
|D_LOWERFIFO256|BlackScholes:09eff62b|8456|8520|0.992488|1.000000|
|U_L2MQ256|SGEMM|353921|357466|0.990083|1.000000|
|G32_W16|BlackScholes:09eff62b|8456|8520|0.992488|1.000000|
|G32_W4|convolutionSeparable:438eefd6|395820|425074|0.931179|0.788305|
|U_FRFCFS256|convolutionSeparable:438eefd6|332199|336354|0.987647|0.996236|
|G64_W16|vectorAdd:ddf26d4f|73696|75039|0.982103|1.029291|
|G64_W8|vectorAdd:ddf26d4f|75160|75785|0.991753|1.019159|
|COMBO_G64W8_L1L2MQ2|vectorAdd:ddf26d4f|75546|76197|0.991456|1.013649|
|G16_W8|BlackScholes:09eff62b|9086|8682|1.046533|0.981341|

## Detach, static layout, Source92 and diagnostic boundaries

- EP_PERF_BLACKSCHOLES_09EFF62B_F_G16_W8_V1: final64 RO detached=0; accepted/responses=4732/4732. End-to-end T benefit remains UNKNOWN; B0 pending is not a real TagFAIL counter.
- EP_PERF_BLACKSCHOLES_09EFF62B_F_G32_W4_V1: final64 RO detached=0; accepted/responses=4744/4744. End-to-end T benefit remains UNKNOWN; B0 pending is not a real TagFAIL counter.
- EP_PERF_CONV_F_G16_W8_V1: final64 RO detached=237; accepted/responses=1354746/1354746. End-to-end T benefit remains UNKNOWN; B0 pending is not a real TagFAIL counter.
- EP_PERF_CONV_F_G32_W4_V1: final64 RO detached=1141; accepted/responses=1348728/1348728. End-to-end T benefit remains UNKNOWN; B0 pending is not a real TagFAIL counter.
- EP_PERF_VECTOR4M_F_G16_W8_V1: final64 RO detached=0; accepted/responses=1000000/1000000. End-to-end T benefit remains UNKNOWN; B0 pending is not a real TagFAIL counter.
- EP_PERF_VECTOR4M_F_G32_W4_V1: final64 RO detached=27; accepted/responses=1000000/1000000. End-to-end T benefit remains UNKNOWN; B0 pending is not a real TagFAIL counter.

Vector G32x4 has 27 actual detaches but F=75583 is 99 cycles slower than matched S=75484. Detach occurrence therefore does not establish T benefit. G16x8 requires both same-mode absolute comparisons and independent validation before a wider claim.

S64 comparisons below explicitly reuse the frozen F endpoint by alias. Only the declared mode-layout static_s64 difference is permitted: S resident/bypass/WB=1024/80/64; F unified1168. No generic hardware-key exclusion is used.

- S64 BlackScholes:09eff62b S=8456, reused F=8520, S/F=0.992488; S64-default S=0 cycles, same MS0 profile.
- S64 convolutionSeparable:438eefd6 S=331550, reused F=335088, S/F=0.989442; S64-default S=316 cycles, same MS0 profile.
- S64 vectorAdd:ddf26d4f S=77016, reused F=77237, S/F=0.997139; S64-default S=-168 cycles, same MS0 profile.

Source92 P2 is compared with Source92 P1 only. It includes the conservative native identity/arbitration organization and serializes same-slot RR/RAW/WAW; it is not a pure ideal two-port bandwidth intervention. COPY_FREE/DATA_FREE endpoints are idealized diagnostics and are excluded from deployable modeled-cost Pareto claims.

- EP_PERF_CONV_F_DIAG_L2_DATA_FREE_V1: 335720 cycles; same-mode REF=335088; REF/actual=0.9981174788514238.
- EP_PERF_CONV_S_DIAG_COPY_FREE_V1: 329781 cycles; same-mode REF=331234; REF/actual=1.00440595425449.
- EP_PERF_VECTOR4M_F_SOURCE92_P1_NI_V1: 77237 cycles; same-mode REF=77237; REF/actual=1.0.
- EP_PERF_VECTOR4M_F_SOURCE92_P2_G32W8_V1: 77212 cycles; same-mode REF=77237; REF/actual=1.0003237838677925.
- EP_PERF_VECTOR4M_S_SOURCE92_P1_NI_V1: 77184 cycles; same-mode REF=77184; REF/actual=1.0.
- EP_PERF_VECTOR4M_S_SOURCE92_P2_G32W8_V1: 77192 cycles; same-mode REF=77184; REF/actual=0.9998963623173386.

## Evidence-ranked next mechanisms (proposals, not launch authority)

1. **W/V and RO/T attribution.** Use same-Source matched W-only/WV/F/F-minus-T(M1) endpoints to separate write/victim reuse from T. Require latency and extra descriptor-read costs for native/merge candidates. The 27-detach case justifies a bounded causal comparison, not a T speedup claim.
2. **Bounded geometry attribution, not a smaller-Tag speedup search.** G16x8 improves relative S/F while absolute F gets slower on fixed3. It is informative for W/V/T causality; prioritize independently better absolute endpoints and retain negative cases. Do not shrink Tags indefinitely to manufacture detach.
3. **L2MissQ256 / ICNT1024 / combined geometry-headroom.** Finish the preselected fixed8 validation population before any complete-population GM. Keep per-input exceptions and absolute F gains separate from same-hardware EP gains; resource increases improve both modes.
4. **Payload/bank organization.** S64 tests equal physical1168 data budget with different role reachability. Physical0.5x/2x requires a new qualified Source. Source92 P2 currently has Vector-only performance evidence; no multiworkload claim follows. Future lean/native/merge candidates remain separate engineering qualifications.

## Technical failures: actual evidence and boundary

Metadata-only annotation UTC: 2026-10-28T10:11:16.550678+00:00; Main failure audit UTC: 2026-10-28T10:09:22.329206+00:00. This technical-failure evidence was first attached to the210-endpoint snapshot at07:55:32 UTC; the accepted population above is newer, and the failure evidence is reused unchanged.

The two spent CLOSED_UNACCEPTED points are the same ParticlefilterNaive input in S and WV_ZERO_RO, both T=0/M=0, same Source78/ELF. **PROVEN:** kernel1 completed at91440 cycles/8 CTA; command ordinal9, the third subsequent HtoD to0x7ff9f3504000 for8000 B, reaches the explicit host-prefill refusal and SIGABRT. Peak RSS is336 MiB and the resource stop reason is null. These are first-kernel-only / partial-application measurements: kernel1 completed, but the nine-kernel application did not. They are never whole-application performance endpoints.

At the last printed boundary all64 slices have pending-resource fields0 and terminal_clean1. That establishes no inflight work; it does not establish a cache without dirty resident data. The first kernel records500 resident-bank write operations,0 DRAM read/write issues and0 production Tag-way allocation blocks. Historical per-slice dirty maxima are not final occupancy or a simultaneous GPU count.

**LIKELY:** the selected owner is dirty due to kernel1 stores, supported by exact address overlap and dirty history. **UNKNOWN:** the rejected sector, selected way, owner snapshot and precise failing Boolean subpredicate were not logged. The generic refusal must not be promoted to a logged proof of that one predicate.

The shared FT interkernel host-overwrite path lacks the required dirty-overwrite compatibility protocol. The existing CPU dirty-host-prefill test intentionally expects refusal/SIGABRT; it does not prove successful dirty overwrite. This is neither a T failure nor a performance negative, resource-stop result or evidence of a bad Trace. A repair requires a new Source, protocol CPU proof and matched application NI; none is executed or qualified by this annotation. No retry or refund follows.

Pinned Main audit: `/root/data/ep_l2_full_workload_performance_20261027_v1/control/TECHNICAL_FAILURE_ROOTCAUSE_20261028_V1/EVIDENCE.json`, SHA `4a42772a59fa2d04b45f6437bc3d3c23c2fdbbf9b08e42ddc50abbe138fd0956`. Its exact Source excerpts, prior first-kernel store-population join, actual raw/archive checks and both native restores are retained by reference; this updater did not reread raw or Trace bodies. JSON and both CSV failure rows carry this evidence reference.

Original detailed Main report (read-only source): `/root/data/ep_l2_full_workload_performance_20261027_v1/control/TECHNICAL_FAILURE_ROOTCAUSE_20261028_V1/TECHNICAL_FAILURE_ROOTCAUSE.md`, SHA `f4ce23bde393007c3f02fc0dec5c54ebdec7134bd8a12d563b851f4c81ccea8a`. The original failure annotation and Main audit times are separate from the current accepted-results snapshot above.

## Units, costs and unavailable observations

Physical payload data RAM is 1168 x 128 B x 64 = 9,568,256 B (9.125 MiB). Tag address coverage is not Tag RAM storage or area. Pareto results use only explicit modeled capacity proxies within the same input/mode/Source/observer profile; they omit technology area, energy and metadata PPA. F also has RO/TVD metadata and is not claimed to have identical total area.

Unclosed endpoints: 1. Technical negatives retained: 2. Metadata join HOLDs: 0; live pair exclusions: 0. Exact refs, 282-option deltas, pending cases and population membership are in JSON/CSV.

Disabled R4/R5/LIFE/ET observations are NOT_OBSERVED, not measured zero. TagFAIL/reuse/timing populations cannot be reconstructed from unrelated marginal counters. Original-capture completeness and numeric SASS correctness remain UNKNOWN.
