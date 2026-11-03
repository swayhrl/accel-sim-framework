# Preliminary accepted-primary analysis and next decision

This is a fixed pre-NI analysis of five CLOSED_ACCEPTED primary points plus four already accepted exact Source78 S/WV reference points. The three authorized diagnostic ON runs continue unchanged in the existing finite Main controller. No new model start, budget registration, Source change, CPU protocol test or collector is performed by this analysis. The application-level NI results are still pending at this snapshot. This report does not replace the final run/NI closeout.

## Decision

Prioritize W/V mechanism decomposition on the strongest useful-service workload, Stencil. Propose two fresh Source78 points, W_ONLY and WV_ZERO_RO, with the exact existing S anchor; reserve Scan W_ONLY/WV as a separately approved two-point negative-control followup. Do not start these points from the current eight-point allowance. Finish the existing three T diagnostic pairs first. Keep the P1 correction as an independent correctness/implementation candidate, without making Corrected-F the performance default for Conv or merging it into accepted Source78.

The new two-point W result establishes that the V-enabled package provides additional performance on FWT/GEMM, while W_ONLY alone is approximately neutral there. It does not establish that every V access is profitable or that the same policy helps all workloads. The T result establishes a real correction benefit over legacy T, but not net T acceleration over F_MINUS_T.

## Proven primary performance

|Conv16x8, same new ELF|Full cycles|Detach counter, sum64 final RO slice summaries|Rows kernel|Columns kernel|Residual after last kernel statistics|
|---|---:|---:|---:|---:|---:|
|F_MINUS_T|362791|0|174205|188456|130|
|LEGACY_F|367152|237|176424|190570|158|
|CORRECTED_F|364463|360|177078|187262|123|

B versus A increases cycles1.2021%. C versus B reduces cycles0.7324%, while C versus A still increases cycles0.4609%. All3 points are accepted with714547200 instructions,27648CTA,2 real kernels, requester/identity checks, complete hardware drain, true164 archive and two independent native restores. Source is Core1e07b263ca0879798387d2a712914a914f298775 / ELF54c3fbba9bb152d1a26539cccb617ac4a3368547a06509f427a202eeda6d8505; no old-ELF point fills any arm.

The new kernel split is material: C versus B worsens Rows by654 cycles, improves Columns by3308, and reduces the final residual by35, summing to2689fewer cycles. C versus A worsens Rows by2873 but improves Columns by1194, with7fewer residual cycles, summing to1672more cycles. This is PROVEN timing localization, not a proof that the query or an individual detach caused a particular kernel delta. Cache state and request ordering can carry between kernels. The residual is not asserted to be pure DRAM or hardware-drain time. The final zero-instruction/zero-cycle empty-name print is not a third real kernel; its -nan IPC is an empty-statistic artifact, not an application performance measurement.

## What the counters do and do not explain about T

All3 arms have a sampled per-set RESERVED maximum8/8. B0 all-way-reserved refusal observations are310081/321244/317937 for A/B/C. These are repeated production/head observations, not unique NEW demands or the rawTagFAIL/eligible/relieve/accepted joint funnel. Heavy diagnostic observers are OFF for these primary performance points; their missing joint fields remain UNKNOWN until accepted same-arm ON data and NI are available.

Corrected-F issues2954 explicitly paid set-eligibility queries, with2954 cumulative one-cycle slice-exposures and0port-wait attempts. Those are real modeled costs. They are not2954exclusive end-to-end critical-path cycles and cannot be subtracted from application cycle differences. Total detached RO transactions increase237 to360; the net123 difference is not a UID-level count of newly corrected ordinary-request relief events.

|Observed population|A F_MINUS_T|B LEGACY_F|C CORRECTED_F|
|---|---:|---:|---:|
|Same-address WB request wait exposure|4220963|4243639|4441624|
|Tag-set-pending request wait exposure|310081|321244|317937|
|MissQ-full request wait exposure|9145|11666|12357|
|RO lookup one-cycle request exposure|1354339|1354822|1355375|
|Victim lookup one-cycle request exposure|1786078|1792427|1799733|
|Successful lower read bytes|85509184|85614976|85683136|
|Victim read responses|64741|63634|62169|
|Ordinary line-MSHR peak /128|107|109|111|
|Shared descriptor peak /512|356|349|350|

LIKELY: local Tag progress competes with existing writeback serialization, lookup costs and altered downstream/replacement ordering; the mechanism is too infrequent or poorly placed to produce a net gain here. HYPOTHESIS: changed Tag ownership/replacement order contributes to additional traffic or different cache state in Columns. UNKNOWN: the precise UID-level critical path and contribution of each counter change. In fact C improves over B while its aggregate same-address WB wait increases, demonstrating why summed slice wait counts cannot explain the GPU cycle difference.

Across these three arms, observed ordinary line-MSHR-full, shared-descriptor-full, DRAM-credit-block and ReturnQ-full counts are0. This supports no expansion of those resources on this evidence; it does not establish that they can never constrain another workload. WAD, lower/MissQ and scheduler sometimes reach capacity, but peak occupancy alone does not prove a causal throughput limit. No further Tag shrinking or DRAM latency inflation is justified by these results.

## W/S/WV matched decomposition

|Source78 input|S cycles|W_ONLY cycles|WV cycles|W versus S cycle change|WV versus W cycle change|
|---|---:|---:|---:|---:|---:|
|GEMM|558588|558957|550642|+0.0661%|-1.4876%|
|FWT|181827|181635|178951|-0.1056%|-1.4777%|

These comparisons reuse only the reviewed exact Source78/input/geometry/observer/config references. W_ONLY includes pooled FT allocation and in-place WB; it is not a free-copy oracle. Adding V includes retention, allocation, lookup cost, actual victim service and dirty forwarding. The observed cycles difference identifies that package in this background, not a single instruction or comparator.

GEMM: W halves WB-readout bank operations6482 to3241, but these are small relative to18.55M bank grants. Lower read/write bytes barely change and performance is nearly neutral. WV reduces successful lower read bytes from3160192 to1080320, serves609858 victim reads, and lowers cycles relative to W. Ordinary MSHR peak9/128, descriptor35/512, scheduler peak19/128 in S/W and no recorded lower/MissQ/scheduler refusal show no evidence for a queue-capacity optimization here. Compute-only limitation remains UNKNOWN; low DRAM volume is insufficient to establish it.

FWT: W eliminates the S WB_DATA_SPACE request-wait exposure (193143 to0) and copy-pipeline waits (45703 to0), with bank grants falling2531489 to2440075. However MissQ-full exposure rises1 to201212 and same-address WB exposure remains about214139; successful lower read/write demand stays essentially unchanged. PROVEN: the local work reduction and observed pressure redistribution coexist with only0.106%cycle improvement. LIKELY: the relieved stage is not the dominant dependency/service constraint. The two kinds of wait use different request populations; their counts must not be treated as migrated one-for-one or added as an exclusive cycle budget.

FWT WV serves88069 victim reads and3312dirty-forward responses. Relative to W, successful lower read bytes drop37.7578%, successful write bytes rise30.0305%, total successful bytes drop7.8477%, and cycles fall1.4777%. Thus neither less WB traffic nor fewer cumulative frontend waits is a necessary description of this benefit. The package improves useful local service despite added lookup cost and changed writeback scheduling.

Final resident/Victim dirty data need not be flushed by the existing commandlist+hardware-drain contract. GEMM's completed write-byte reduction, particularly414848 to1152, cannot be claimed as permanent elimination of stores or full-flush bandwidth savings. Exact final dirty-line counts are not supplied by this compact projection and remain UNKNOWN.

## Ranked next work

1. Now, without new starts: finish all3 already-authorized ON runs, validate each against its same-arm OFF point, and analyze rawTagFAIL/eligible/preview/paid query/detach joint evidence only after the pair is accepted. Use per-kernel or existing bounded window records if present; do not equate globally increased detach with the Columns timing gain. Preserve any NI mismatch as a negative without retry. Strict demand-unique NEW and later UID completion chain remain uninstrumented.
2. First proposed performance batch: Stencil W_ONLY and WV_ZERO_RO,2fresh starts, same Source78 ELF,64slice32set8way, dram_latency100,1168physical Payload slots per slice, same ports/queues/clocks and existing SUMMARY_STAGE observer profile. Both modes have M=T=OFF and require no RO certificate. Reuse the exact current S anchor after admission review. Existing Stencil F is evidence of a positive package result, not the W or V control. Historical wall anchors are4.8-8.0hours per point, about0.58GiB planning RSS; these are planning ranges, not predicted model performance or new static reservations.
3. Conditional followup, not automatically authorized: Scan W_ONLY/WV,2fresh starts. Its historical8.1-8.9hours per point makes a staged decision sensible. A harmful WV/W delta would support investigating optional Victim retention/lookup cost; W already slow versus S would instead require investigating W-related pressure redistribution before blaming V. The first and followup scopes must not consume the remaining current conditional T allowance or reopen spent W2.
4. Engineering candidate only after decomposition: service-aware optional-Victim reclaim or occupancy-responsive optional retention. Preserve mandatory dirty/WAD ownership, readers/pins, generation, bank colors and pending return protection. Account comparator/metadata/port/timing costs; update frontend preview and backend reclaim together. Do not merge C1, relax RO/T safety, or assume a free negative filter. Then freeze one unified policy and validate on held-out qualified inputs; these outcome-selected Stencil/Scan cases are not an independent generalization set.

If Stencil WV captures most of the existing F improvement while W is near S, prioritize V usefulness and retention. If W alone captures it, prioritize W throughput/resource policy. If neither approaches F, investigate qualified RO/M contributions before attributing F's9.9%gain to V. Scan provides the corresponding negative-control decision. Avoid a new large collector or parameter grid until a concrete policy question remains unanswered.

## Evidence and execution boundary

ACCEPTED_PRIMARY_AND_MATCHED_REFERENCE_METRICS.json binds all9 exact accepted point/spec/source identities and compact metrics. T_PRIMARY_KERNEL_RECORDS.json records one bounded pass through the three accepted primary local gzip logs (about36.6MB uncompressed total, each capped64MiB); no Trace body was read. T_KERNEL_CYCLE_DECOMPOSITION.json checks printed per-kernel cycles against accepted totals. MATCHED_WV_COMPARISONS.json records explicit arithmetic. NEXT_MINIMUM_EXPERIMENT_PLAN.json binds four prior draft specs with exact input/S identities and first2/conditional2 status.

No new application, GPU collection, protocol fixture, registered budget or runtime/source modification occurred. Existing Main dispatcher, live NI runs, accepted assets, foreign owner guarantees and Source KEEP are preserved. The proposed future modes require their own exact input qualification, Host/native scope and fresh user authorization. The currently running scoped native file must remain unchanged. Large inputs/results remain genuine164; SSD/RAM admission uses actual increments and one sequential restore window, not repeated hard-cap or historical pool reservations.
