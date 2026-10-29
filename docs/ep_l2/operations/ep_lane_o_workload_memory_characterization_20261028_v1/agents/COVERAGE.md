# Lane O evidence coverage audit

Read-only audit of existing evidence; no simulation, build, Trace body scan or Main mutation. New files only in Lane O.

## Snapshot and evidence levels

Four live projections were copied once at UTC 2026-10-28 10:31:56. All have source mtime UTC 10:30:57, report utc=10:30:57.004363: **2026-10-28 18:30:57 Asia/Shanghai**. This is an interim snapshot, not a final campaign result. See coverage_snapshot/SNAPSHOT_RECEIPT.json.

| Population / stage | Count | Boundary |
|---|---:|---|
| Authoritative42 |42|35 frozen exact inputs +7 unresolved programs|
| Registered exact points |227|Not equivalent to started/completed/accepted|
| Consumed starts |218|Includes consumed-before-fork, not a live-process count|
| CLOSED_ACCEPTED |214|Current Main acceptance projection; status says all scientific results genuine164|
| CLOSED_UNACCEPTED |2|particlefilter_naive S/WV, retained failures|
| CONSUMED_BEFORE_FORK |2|lavamd S and SYRK S, not scientific completion|
| NOT_STARTED |9|Preparation/readiness is not a result|
| Accepted profile pairs |106|Exact matched input/Source/ELF/observer/background|
| Accepted REF S/F input pairs |22|21 programs; Vector4M and Vector6M are distinct inputs|
| Accepted input IDs |26|25 selected primary35 inputs plus auxiliary Vector4M|
| Accepted program names |25|Not the matched primary35 completion count|

214 accepted points:210 Core78/ELF78d4 plus4 Core92/ELF67315. Do not pool across ELF. Full source identity includes Core, Framework, pybind commit, binary SHA, source archive SHA.
Core78=78f4b59e865b136eede74df74c44c210f5b4ca04, ELF=78d4e96bb79c776e27146bcf168d7c70cf3897ef9cb84d837d8974fec4c91b8a.
Core92=92ed2c4c1c2d682b33f2f7ce4d6b56571a889480, ELF=67315b875a0fa80d2886cb142f3fc4a5b044325ce2b5f901eca675a9abb0e53f.

CPU preparation, process exit, validated bundle, application acceptance and archive closure are separate stages. The inspected 2DCONV F historical bundle still says PENDING_MAIN and ACCEPTED_POINT says PENDING_MANDATORY_ARCHIVE_CLOSURE. Current RUN_STATUS=CLOSED_ACCEPTED and separate ARCHIVE_RECEIPT says TRUE164_RESULT_SHA_AND_TWO_NATIVE_TARGET_RESTORES_PASS. Join current state and archive receipt; do not use old staged fields alone. Producer PASS is not application acceptance.

## Workload identity and full population

Identity source: review/docs/ep_l2/operations/ep_full_workload_performance_20261027_v1/MAIN42_QUALIFICATION_AND_HOLD.csv; Authoritative42 freeze71584878be0c80375f9d25bcd80e171b7bf4478d (CONTEXT).
Full ordered commandlist CONTENT is identity; program names are insufficient.
Unresolved7:backprop,cfd,kmeans,nn,nw,pathfinder,streamcluster. CFD5kernel lacks time_step relative to standard full timestep, diagnostic only. Other unresolved programs mix source versions/input semantics.
GaussianN64 is distinct from old tinyGaussian; primary Vector6M is distinct from auxiliary Vector4M.
Account asset53 suite-program families,100 ordinary records,25 fraction records,96 deduplicated ordinary inputs,42 programs,35 primary inputs and accepted runs are different denominators. Existing SM70 headers establish assets, not EP qualification. Reuse existing inventory, no rescan.

| Primary42 program | Identity | Accepted points | Accepted REF modes |
|---|---|---:|---|
|2DCONV|IDENTITY_FROZEN|3|F,S,WV_ZERO_RO|
|3DCONV|IDENTITY_FROZEN|3|F,S,WV_ZERO_RO|
|3MM|IDENTITY_FROZEN|2|F,S|
|ATAX|IDENTITY_FROZEN|2|F,S|
|backprop|UNRESOLVED|0||
|bfs|IDENTITY_FROZEN|0||
|BICG|IDENTITY_FROZEN|3|F,S,WV_ZERO_RO|
|BlackScholes|IDENTITY_FROZEN|39|F,S|
|cfd|UNRESOLVED|0||
|convolutionSeparable|IDENTITY_FROZEN|41|F,S|
|cutcp|IDENTITY_FROZEN|0||
|dwt2d|IDENTITY_FROZEN|8|F,S|
|fastWalshTransform|IDENTITY_FROZEN|2|S,WV_ZERO_RO|
|gaussian|IDENTITY_FROZEN|8|F,S|
|GEMM|IDENTITY_FROZEN|3|F,S,WV_ZERO_RO|
|GESUMMV|IDENTITY_FROZEN|2|F,S|
|heartwall|IDENTITY_FROZEN|8|F,S|
|histo|IDENTITY_FROZEN|0||
|histogram|IDENTITY_FROZEN|8|F,S|
|hybridsort|IDENTITY_FROZEN|0||
|kmeans|UNRESOLVED|0||
|lavamd|IDENTITY_FROZEN|0||
|lud|IDENTITY_FROZEN|8|F,S|
|mergeSort|IDENTITY_FROZEN|8|F,S|
|mri-q|IDENTITY_FROZEN|0||
|MVT|IDENTITY_FROZEN|2|F,S|
|myocyte|IDENTITY_FROZEN|0||
|nn|UNRESOLVED|0||
|nw|UNRESOLVED|0||
|particlefilter_float|IDENTITY_FROZEN|2|S,WV_ZERO_RO|
|particlefilter_naive|IDENTITY_FROZEN|0||
|pathfinder|UNRESOLVED|0||
|sad|IDENTITY_FROZEN|0||
|scalarProd|IDENTITY_FROZEN|1|F|
|scan|IDENTITY_FROZEN|2|F,S|
|sgemm|IDENTITY_FROZEN|2|F,S|
|srad_v1|IDENTITY_FROZEN|1|S|
|stencil|IDENTITY_FROZEN|2|F,S|
|streamcluster|UNRESOLVED|0||
|SYRK|IDENTITY_FROZEN|0||
|transpose|IDENTITY_FROZEN|3|F,S,WV_ZERO_RO|
|vectorAdd|IDENTITY_FROZEN|8|F,S|

Primary35 with no accepted result at this snapshot: bfs,cutcp,histo,hybridsort,lavamd,mri-q,myocyte,particlefilter_naive,sad,SYRK.
No accepted result does not mean absent Trace or absent readiness/running work. Lane O must wait for Main status updates, not launch gap-fill simulations.
coverage.csv/json stores full SHA identity, suite, expected kernels, scope, registered/accepted counts, modes, Source, prior RO qualifications, body bytes and capture/numeric boundaries.

## Mandatory versus optional observers

All106 matched pairs have identical observer_env:
EPL2_DETACH_DIAG=0; EPL2_TAGPRESSURE_DIAG=0; EPL2_TAG_LIFETIME=0; EP_L2_EVENT_TIMELINE=0; EPL2_LIFE_WIRE=SUMMARY_STAGE.
CURRENT_STATUS explicitly says optional_pressure_lifetime_counters=NOT_OBSERVED_NOT_MEASURED_ZERO.
Optional counters OFF does NOT imply all mandatory W/V/M/T counters absent, and does NOT mean the phenomena are measured zero.

Existing ACCEPTED_REFERENCE_MSHR_SUMMARY.json covers44 accepted Source78 REF endpoints,21 input IDs and2816 slice rows (64 slices/endpoint). Registry snapshot=cdce3596f5e82cde70325f1062666969d7b7ab0bee5999c263286b6c50778f4d. This summary predates the frozen214 population. It is a bounded reusable subset, not complete214-point coverage.

Parent-integrated finite audits have separate populations:48 REF endpoints for W,44 endpoint subset for M,30 F/WV endpoints for V,22 matched REF S/F input pairs. These are not contradictory counts; they answer different questions. Do not replace one denominator with another.

Actual mandatory B0 fields were directly inspected at:
cases/EP_PERF_2DCONV_0AE13552_F_REF_V1/run/df62f0de-9be2-42fb-a2b6-ebf8e14d608b/VALIDATED_APPLICATION_BUNDLE.json.
model.mechanism_metrics.bottleneck contains:
distinct_requests_first_block, blocked_observations_over_slices, request_wait_cycle_sum, request_wait_max, hist_log2[65], resolved_first_waits, unknown_while_unresolved.
Reasons include ANY_FIRST_BLOCK_TO_ADMISSION,BANK_COMPATIBLE_LANDING,COPY_PIPELINE,DATA_SERVICE,DESCRIPTOR_FULL,FRONTEND_TRANSACTION,LINE_MSHR_FULL,MISS_QUEUE_FULL,PER_LINE_CAP,PINNED_PAYLOAD,READONLY_LOOKUP,RESPONSE_QUEUE_FULL.
Therefore **distinct blocked requests and wait duration are not universally missing**. Reuse these accepted-bundle summaries before designing new counters or rerunning. This direct check verifies one actual cohort/schema, not uniform field coverage/definition across214 points; detailed W/V/M/T audits establish those contracts.

| Dimension | Verified existing evidence | Claim boundary / gaps |
|---|---|---|
| W |44 endpoint WAD peak/full; inspected bundle wb_created/lower_accepted/completed and B0 wait aggregates|Resource/queue facts, not same-address reaccess or complete WB lifetime distribution|
| V |Inspected bundle payload roles/TVD structure fields|Not a substitute for access interval, distinct reuse distance or evict-to-next-access|
| M |44 endpoint line-MSHR/descriptor/WAD peak/full; inspected B0 distinct first-block and wait histogram|Mechanism pressure, not intrinsic workload MLP|
| T |Mandatory B0 exists; optional tag pressure/lifetime off|Cannot infer per-set Reserved pressure zero or old-RO/new-address overlap from absent optional records|

Prior MAIN35_LATEST_QUALIFICATION.csv has16 positive,18 unknown,1 proven-zero RO inputs. Current live status has25 positive-RO input IDs with exact registered F specs. Different times/qualification scopes; prior unknown must not be turned into current RO=0. Certified RO LINE count is static, not dynamic request fraction.
Current capture completeness and numerical output are UNKNOWN. Claims remain TRACE_DEFINED_COMPLETE_DECLARED_COMMANDLIST, not newly certified whole original application or numeric output correctness.

## Retain positive and negative findings without speedup attribution

These values are from existing44 endpoint aggregation. Peaks are max over slices; counts are sums over slices.

| S REF endpoint | Line peak | WAD peak | Line-full head observations | WAD-full events |
|---|---:|---:|---:|---:|
|EP_PERF_2DCONV_0AE13552_S_REF_V1|27|19|0|0|
|EP_PERF_3DCONV_8F268365_S_REF_V1|51|16|0|0|
|EP_PERF_ATAX_S_REF_V1|32|2|0|0|
|EP_PERF_BICG_192C29C0_S_REF_V1|32|2|0|0|
|EP_PERF_BLACKSCHOLES_09EFF62B_S_REF_V1|0|0|0|0|
|EP_PERF_CONV_S_REF_V1|128|128|6499|14876|
|EP_PERF_DWT2D_8E07074A_S_REF_V1|0|0|0|0|
|EP_PERF_FASTWALSHTRANSFORM_FC3A9062_S_REF_V1|99|100|0|0|
|EP_PERF_GAUSSIAN_B5FC8DF0_S_REF_V1|0|0|0|0|
|EP_PERF_GEMM_140F6ED3_S_REF_V1|9|3|0|0|
|EP_PERF_GESUMMV_A953FB7D_S_REF_V1|32|0|0|0|
|EP_PERF_HEARTWALL_81949DE8_S_REF_V1|3|0|0|0|
|EP_PERF_HISTOGRAM_85ECC480_S_REF_V1|0|0|0|0|
|EP_PERF_LUD_28B97CD0_S_REF_V1|0|0|0|0|
|EP_PERF_MERGESORT_ADD5C722_S_REF_V1|0|0|0|0|
|EP_PERF_MVT_39D1748B_S_REF_V1|32|2|0|0|
|EP_PERF_PARTICLEFILTERFLOAT_3904B55B_S_REF_V1|1|0|0|0|
|EP_PERF_SGEMM_S_REF_V1|34|29|0|0|
|EP_PERF_TRANSPOSE_DA6CAAE1_S_REF_V1|0|0|0|0|
|EP_PERF_VECTOR4M_S_REF_V1|110|99|0|0|
|EP_PERF_VECTOR6M_S_REF_V1|110|98|0|0|

Confirmed bounded observation: Conv S reaches line-MSHR128 with6499 line-full head observations and WAD128/full14876. Vector4M/Vector6M S peak110 but line-full0; FWT S peak99/full0. Pressure is workload-dependent within this reference sample; negative cases remain.
This does not establish a universal MSHR bottleneck,6499 distinct blocked requests,6499 global GPU cycles, or a causal explanation of any speedup. Repeated head observations must be distinguished from B0 first-block distinct counts and wait histogram. Sum over slice observations cannot be divided by GPU cycles and called single-resource utilization.

## Minimal collection population and cost boundaries

1. First reuse accepted aggregate evidence for all35 fixed identities. Keep10 accepted-result gaps and7 unresolved programs visible; do not replace with a successful alternative input. Main alone updates formal closure.
2. Future missing-feature collection:one fixed S baseline per eligible input, same Source/ELF, geometry and complete commandlist. Add only counters actually missing. Do not recollect all214 profile points or repeat performance exploration.
3. Only after baseline features reveal actual positives and retained negatives should Main choose a few W/V/M/T controls. Controls cannot define the original workload feature after seeing speedup.
4. If Main already plans an unfinished input run, after review it can attach lightweight counters; if essential missing features cannot be recovered from completed results, Main can schedule one baseline supplement. No starts now.
5. Prior metadata body_bytes sum across primary35=114575222092 bytes (~114.6GB). This is a sum of existing lengths, not a new scan, compressed IO estimate or unique storage claim. Exact offline reuse scans can be expensive. Prefer bounded online counters, fixed/log2 histograms, sampled address histories and limited eviction watches; emit sampling, overflow and censored counts.
6. Bind feature output to full input SHA, ordered commandlist/epoch, Source5/ELF, baseline parameters/geometry, RO certificate/domain, observer mask/schema, kernel/instruction/CTA closure, clock unit, dedup key and sampling/censor semantics.
7. Per metric status:AVAILABLE / NOT_COLLECTED / NOT_APPLICABLE / FAILED / UNKNOWN. Use numeric zero only when actually measured and applicable.
8. Any implementation goes to isolated candidate branch. Main owns later native admission, budgets, resource scheduling and archive acceptance. This audit requires no source changes.

## Sources

- /root/data/ep_l2_full_workload_performance_20261027_v1/CONTEXT.md and review/AGENTS.md.
- analysis/live/{CURRENT_STATUS.json,MATCHED_PERFORMANCE.csv,MATCHED_RESULT_DETAILS.json,RUN_STATUS.csv}, frozen in coverage_snapshot.
- review/docs/ep_l2/operations/ep_full_workload_performance_20261027_v1/{MAIN42_QUALIFICATION_AND_HOLD.csv,MAIN35_LATEST_QUALIFICATION.csv,ACCEPTED_REFERENCE_MSHR_SUMMARY.json}, copied in coverage_snapshot.
- Same directory ACCEPTED_RESULT_REFS_CURRENT.json:current accepted point/archive/spec refs; raw not copied.
- review/docs/ep_l2/operations/ep_main_sm70_trace_statistics_20261024_v3/SM70_TRACE_STATISTICS.md:existing header inventory.
- cases/EP_PERF_2DCONV_0AE13552_F_REF_V1/run/df62f0de-9be2-42fb-a2b6-ebf8e14d608b/{ACCEPTED_POINT.json,VALIDATED_APPLICATION_BUNDLE.json}, plus cohort/control/ARCHIVE_RECEIPT.json:bounded direct inspection.
