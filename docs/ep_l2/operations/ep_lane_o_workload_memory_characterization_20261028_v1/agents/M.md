# Lane O / M: Read-only requests and memory concurrency audit (2026-10-28)

## Scope and identity

Finite read-only audit. No Trace bodies, raw decompression, models, builds, production edits, controller/ledger mutations. Only this report is written.

Architecture source: `docs/ep_l2/ELASTIC_PAYLOAD_L2_ARCHITECTURE_AND_ROADMAP.md`, sections 3.7, 10-13, 21. The document includes earlier 192-line/4-merge designs and later 128/D512/address32 designs; these are not one executing configuration. Current Source78 enforces ordinary line-MSHR128/slice, shared descriptor512/slice, per-address32, Payload1168, line128B/sector32B. Source checkout `/root/data/ep_l2_multiworkload_event_timeline_20261027_v1/core`: Core `78f4b59e865b136eede74df74c44c210f5b4ca04`, Framework `9dd1ee57a83d83b56b7874bc7c716185ab52c8f7`, ELF `78d4e96bb79c776e27146bcf168d7c70cf3897ef9cb84d837d8974fec4c91b8a`.

Reused existing ACCEPTED_REFERENCE_MSHR_SUMMARY.json: 44 CLOSED_ACCEPTED Source78 REF endpoints, 2816 slice rows. Each has accepted point and validated compact bundle path/SHA. This is a bounded older snapshot, NOT all 214 accepted endpoints in Lane O frozen live projection. Newer accepted endpoints can be appended by compact-only projection and acceptance outer join; omission here does not mean not run. Different inputs/modes are not independent program samples.

- Summary: `/root/data/ep_l2_full_workload_performance_20261027_v1/review/docs/ep_l2/operations/ep_full_workload_performance_20261027_v1/ACCEPTED_REFERENCE_MSHR_SUMMARY.json`
- Summary SHA256 read now: `cb0787b3275dc46a01c2c8ce252786193819f10ed8825810d96304abda012683`
- Pinned registry SHA256: `cdce3596f5e82cde70325f1062666969d7b7ab0bee5999c263286b6c50778f4d`
- RO summaries applicable at 16 endpoints; absent RO runtime is NOT_APPLICABLE/NOT_OBSERVED, not semantic RO=0.

## Metric table and strict populations

|Metric|Definition and denominator|Reliable existing evidence|Gap / minimal extension|
|---|---|---|---|
|Certified RO fraction of global demand reads|Accepted GLOBAL_ACC_R, nonwrite/nonatom/non-RO-lower, line in exact whole-commandlist certificate / all accepted global demand reads|ROV1 accepted_oracle_candidates / accepted_global_reads|L2-visible accepted population, not lane references, all program loads or all-L2 traffic. Missing certificate is UNKNOWN. Zero-line safe fallback does not prove semantically writable|
|Certified RO fraction of all frontend requests|Candidate numerator / all unique first-arrival UID, separated read/write/atomic/internal|Candidate counts and model.unique_requesters exist, but class population of latter must be audited before naming all-L2 denominator|Add first-arrival class counters; do not divide by DRAM requests or repeated previews|
|RO-path usage|accepted_ro / accepted_oracle_candidates|ROV1 accepted counts|Mechanism outcome; resident hits may bypass RO transactions|
|Live RO merge request fraction|merges / (transactions+merges)|Exact accepted counts and requester closure|Not strictly before-fill reuse: transaction can be ready while responses drain|
|Transactions with any reuse|Transactions having first successful merge / created transactions|reuse_seen_first_transition exists in detach diagnostics; current full-perf observers OFF|Not derivable from merge total. One reuse flag and count per transaction|
|Same-line RO interarrival gap|Time between distinct UIDs FIRST arriving at L2 head; also global first-arrival sequence distance|Architecture planned; no full-population compact distribution located|Shared M/V bounded stable-address sample table, 64-bin log2 histogram and explicit censor/conflict counts. Never update on retry|
|Revisit before completion|New UID first arrival finds same line outstanding; split not-ready requested sectors versus ready-only response drain. Denominator all classified first-arrival RO requests|Live merge count is partial signal, not exact full numerator; no S shadow certificate population|Bounded pending-line refcounts; classify phase, accumulate request-level and transaction-level incidence separately|
|Independent outstanding lines|U_pending(t): distinct lines with issued-not-ready sectors; U_live(t): lines with unretired requesters|ROC1 lower-concurrency per-slice RO pending peak; B0 ordinary line-MSHR avg/p95/max excludes bypass RO|Need all normal+RO union distribution, event-maintained refcount and time integration. Sum of slice peaks is NOT simultaneous GPU peak|
|MSHR capacity pressure|Occupancy=128 time; distinct first-time new-line demand UIDs blocked / all distinct new-line-demand UIDs; separately repeated checks and per-reason first-block-to-first-known-clear wait (or admission if still blocked)|B0/C7d peaks and head checks, M0, MS independent UID wait hist/max already in compact bundles|C7d eligibility and semantic_need are repeated head observations, not independent request denominator. Exact time hist availability requires endpoint flag/output check|
|Merge/address/descriptor limits|Distinct UID refused by address32 or D512 / distinct matching eligible UIDs; repeat checks and nonexclusive waits separately|MS bottleneck counts unique first block, repeated observations, wait histogram/max|address32 is not old static merge4. full_reason has priority. Add first-UID eligibility counters if independent refusal rate needed|

Use exact u64 counts with explicit numerators/denominators. Gaps/waits: 64 log2 bins with separate zero/one/overflow, reuse count bins 0/1/2-3/4-7/8-15/16-31/32+, occupancy exact 0..512 or bounded grouped bins. Whole-program aggregation plus finite predefined phases, never unbounded kernel-count x slice x field output.

Code locations in Core78: `ep-l2-ro-runtime.inc:99-104` demand/candidate, `:136-158` unique UID wait and accepted counts, `:440-465` ROV1/ROC1 output; `ep-l2-ro-transactions.h:112-156` creation, `:180-207` merge/reuse, `:300-317` response retirement/pending, `:323-341` RO lower peaks. `gpu-cache.cc:716-733` full_reason includes normal+RO per-address descriptor limit and priority; `l2cache.cc:1395-1428` C7d/C7e repeated head checks, `:2095-2133` M0 one head observation per cycle. Original `l2-char-stats.cc` has normal MSHR pending/drain lifetimes and histograms, but code existence is not application coverage: verify endpoint enablement. LIFE wire SUMMARY_STAGE alone does not mean TAG_LIFETIME/TAGPRESSURE/ET enabled.

Per-reason MS observer wait terminates at first known-clear of that reason, or at admission if it remains blocked; only ANY_FIRST_BLOCK_TO_ADMISSION necessarily runs until admission. Durations cannot be described as admission latency. Source: `ep-l2-mechanism-observer.h:45-83`.

## Observation status

PROVEN, only for the named accepted Source78 reference population:

1. Certification, RO-path usage and live same-line merging are separate axes. Vector4M candidate/global-demand-read=100%, while about75% of RO requesters merge. SGEMM has a high certificate fraction and live-RO merge fraction92.82%. This rejects an unconditional claim that read-only requests inherently lack short-term repetition; exact pre-fill fraction remains UNKNOWN.
2. Realized independent pending RO line peaks differ: Vector4M/6M69/70 per slice, Conv102, ATAX/MVT32, GEMM5, SGEMM8. Peaks are mechanism/configuration-conditioned outcomes; they alone do not establish a bottleneck.
3. Within these44 accepted REF endpoints, only Conv S/F has line-MSHR capacity refusals. S:6499 repeated head observations,696 distinct UIDs,max per-reason first-block-to-first-known-clear wait151 cycles (or admission if still blocked). F:2986 observations,337 distinct UIDs,max per-reason wait124 with the same closure rule. D512 descriptor-full count is0 throughout44 endpoints. S/F all-mechanism change cannot isolate M causal benefit.
4. SGEMM S encounters the per-line32 limit:1738 head observations,55 distinct UIDs,max per-reason first-block-to-first-known-clear wait97 cycles (or admission if still blocked). F reports0. This is an actual same-address concurrency/merge-limit observation, distinct from global line-MSHR capacity.
5. Zero RO transactions does not mean no RO data. Current BlackScholes37500/37500 reads and Transpose786432/786432 are certified candidates, with0 RO transactions. Resident hits/prewarming are candidates for explanation, but no exclusive causal claim without controls.
6. Current Source78 SGEMM F has81582 RO transactions and1054333 merges. Old r4 SGEMM transaction0 remains valid only for that older lineage. Current tiny-DWT identity8e07074a is different from old DWT99b543b9; current Gaussian b5fc8df0 differs from early ET tinyGaussian.

PENDING: exact before-fill overlap fraction; same-line interarrival distribution; first revisits before lower issue, during lower pending, and ready-only drain; all-normal+RO outstanding union time distribution; unique-UID MSHR refusal rate with a matching new-line demand denominator; joint low-reuse and capacity-pressure occurrence. Do not infer these from speedup/slowdown.

UNSUPPORTED/INVALID: RO=load; every F0-transaction input lacks semantic RO;749913 merges means749913 distinct repeated addresses; all RO transactions are reused; ordinary MSHR max0 means no memory concurrency;6499 checks means6499 new requests; peak descriptor420 proves no other pressure; S/F cycle change is the isolated M effect.

## Minimal collection/experiment plan: design only, Main reviews and schedules

Stage0, no models: one compact projection of Main frozen accepted VALIDATED_APPLICATION_BUNDLE refs, certificate status and existing C statistics. Identity-stratify by input SHA/Core/ELF/config/mode; acceptance outer join required. No raw/Trace scan. Missing Source92/statsOFF observers remain NOT_OBSERVED, not inherited Source78 measurements.

Stage1 independent candidate branch, defaultOFF: common M/V first-arrival observer, not separate giant address tables. Mark L2 frontend first-visible UID once; separate arrival, acceptance, lower issue, sector ready, response enqueue and retire. Key epoch/address-domain+line, attach clock-domain labels and only subtract same-domain times.

- Exact first-arrival class counters: global read/write/atomic/internal, certified/uncertified/UNKNOWN, unique new-line/merge eligibility.
- Bounded pending-line refcount/state, first/last time and reuse count. Existing D512 bounds live waiter population per slice. Fixed512 entries x approximately32B x64 slices is approximately1MiB, plus histogram state approximately0.5MiB. Overflow must invalidate exactness, never silently drop. Event hooks through existing handle/line indexes avoid new per-cycle scans.
- Maintain U_pending/U_live normal,RO,union by event updates and delta-cycle time-integrated histograms. Union requires line refcounts, not sum of two populations.
- Cross-completion interarrival history cannot be exact at unbounded address cardinality for free. Optional model-global fixed16384-entry x32B approximately512KiB stable-line-hash sample table, shared with V. Report sampling rate, valid adjacent pairs, left censor, collisions/evictions; only valid sampled pairs enter gap hist. Never label sampled estimates exact full-population distributions.
- Output only aggregate plus bounded phases.12 histogram groups x64 bins x8B x64 slices is384KiB numeric payload before serialization. Compact output budget must include real serialization and many-kernel CPU stress (e.g.5993 kernels), preventing per-kernel field explosion.

These are design-size estimates; C++ alignment/container RSS and host overhead remain UNMEASURED. Check sizeof/fixed allocation upper bounds, same-stream OFF/ON protocol/cycle noninterference, and actual RSS/wall-time before release; no claim of measured<5%. New source needs its own qualification. Never patch the running Core.

Prefer piggybacking on Main already-planned all-workload reference collection. Preserve missing certification as UNKNOWN instead of immediately rescanning huge Trace. Only nominate discriminating representatives for any additional exact model request: Conv(line capacity), SGEMM(address cap/many merges), Vector4M/6M(many RO/no line-capacity refusal), ATAX/MVT(high certification/low pending concurrency), BlackScholes/Transpose(positive certificate/no transactions), and an UNKNOWN-certificate input. Lane O starts none of these.

## Accepted RO endpoint numbers

candidate/read denominator is accepted global demand reads. Peaks are max of per-slice peaks, not simultaneous GPU total. merge fraction denominator=accepted_ro=transactions+merges. Live transaction peak includes ready/draining; pending unique line peak means issued-not-returned only.

|cohort|candidate/read|RO requesters|transactions|merges|merges/RO|live tx peak|pending unique peak|duplicate sectors|
|---|---:|---:|---:|---:|---:|---:|---:|---:|
|EP_PERF_2DCONV_0AE13552_F_REF_V1|3813424/3813424|2533720|948357|1585363|0.625706|29|29|0|
|EP_PERF_ATAX_F_REF_V1|18972216/18981432|4191527|2618727|1572800|0.375233|32|32|0|
|EP_PERF_BLACKSCHOLES_09EFF62B_F_REF_V1|37500/37500|0|0|0|NA|0|0|0|
|EP_PERF_CONV_F_REF_V1|1420132/2886784|1322070|376204|945866|0.715443|123|102|1|
|EP_PERF_DWT2D_8E07074A_F_REF_V1|3456/28908|0|0|0|NA|0|0|0|
|EP_PERF_GAUSSIAN_B5FC8DF0_F_REF_V1|33/25485|0|0|0|NA|0|0|0|
|EP_PERF_GEMM_140F6ED3_F_REF_V1|1617346/1650114|49347|33019|16328|0.330881|5|5|0|
|EP_PERF_HEARTWALL_81949DE8_F_REF_V1|18819/18819|0|0|0|NA|0|0|0|
|EP_PERF_HISTOGRAM_85ECC480_F_REF_V1|8192/131712|0|0|0|NA|0|0|0|
|EP_PERF_LUD_28B97CD0_F_REF_V1|512/130432|0|0|0|NA|0|0|0|
|EP_PERF_MERGESORT_ADD5C722_F_REF_V1|2048/10045|0|0|0|NA|0|0|0|
|EP_PERF_MVT_39D1748B_F_REF_V1|18979107/18980131|4192092|2619386|1572706|0.375160|32|32|0|
|EP_PERF_SGEMM_F_REF_V1|2317312/2452480|1135915|81582|1054333|0.928179|8|8|0|
|EP_PERF_TRANSPOSE_DA6CAAE1_F_REF_V1|786432/786432|0|0|0|NA|0|0|0|
|EP_PERF_VECTOR4M_F_REF_V1|1000000/1000000|1000000|250087|749913|0.749913|99|69|0|
|EP_PERF_VECTOR6M_F_REF_V1|1500000/1500000|1500000|375109|1124891|0.749927|102|70|0|

## Exact compact bundle references

Paths include exact run UUID; SHAs are the already-accepted summary bindings, not new raw rehashes or reacceptance.

- `EP_PERF_2DCONV_0AE13552_F_REF_V1`: `/root/data/ep_l2_full_workload_performance_20261027_v1/cases/EP_PERF_2DCONV_0AE13552_F_REF_V1/run/df62f0de-9be2-42fb-a2b6-ebf8e14d608b/VALIDATED_APPLICATION_BUNDLE.json` SHA256 `6c8925c78fdc784aff91c5703fcdb8ce531b09f633b2b1e68a0821c0d91fe6bc`
- `EP_PERF_2DCONV_0AE13552_S_REF_V1`: `/root/data/ep_l2_full_workload_performance_20261027_v1/cases/EP_PERF_2DCONV_0AE13552_S_REF_V1/run/8469916d-09af-41a3-b285-467f5d95fe3f/VALIDATED_APPLICATION_BUNDLE.json` SHA256 `a7dfea645bc44dc77074b6c38252c20ad4b295e894c876c88fabb08fa40f7b80`
- `EP_PERF_2DCONV_0AE13552_WV_ZERO_RO_REF_V1`: `/root/data/ep_l2_full_workload_performance_20261027_v1/cases/EP_PERF_2DCONV_0AE13552_WV_ZERO_RO_REF_V1/run/bd1197ca-6d78-451d-92c9-ce9e1602cb2e/VALIDATED_APPLICATION_BUNDLE.json` SHA256 `223d69ef624aded5294dc45ea76c5197bc9ed6ad80c7e67f060cb65d4edf0247`
- `EP_PERF_3DCONV_8F268365_S_REF_V1`: `/root/data/ep_l2_full_workload_performance_20261027_v1/cases/EP_PERF_3DCONV_8F268365_S_REF_V1/run/d82187e5-6846-4529-bada-465625cb196d/VALIDATED_APPLICATION_BUNDLE.json` SHA256 `4e15c807af890dfbefce3ea39543afe4c03aa4b456b7020bd60c380c0b876e2b`
- `EP_PERF_3DCONV_8F268365_WV_ZERO_RO_REF_V1`: `/root/data/ep_l2_full_workload_performance_20261027_v1/cases/EP_PERF_3DCONV_8F268365_WV_ZERO_RO_REF_V1/run/cd7ae1cc-4cbd-4a92-9585-ca4f2d68515d/VALIDATED_APPLICATION_BUNDLE.json` SHA256 `36e041353edf942cd806d703ddb9e898ddc0a4c5e6482abd9545bdc75a9bf0ce`
- `EP_PERF_ATAX_F_REF_V1`: `/root/data/ep_l2_full_workload_performance_20261027_v1/cases/EP_PERF_ATAX_F_REF_V1/run/b72b9152-4051-4392-a763-e9e86485a904/VALIDATED_APPLICATION_BUNDLE.json` SHA256 `2f52c2511ed18957ff1efffb7956f5dc630d5dca0148f8a8453f57724f3986d7`
- `EP_PERF_ATAX_S_REF_V1`: `/root/data/ep_l2_full_workload_performance_20261027_v1/cases/EP_PERF_ATAX_S_REF_V1/run/474b7a0d-438d-4b8d-a860-9c8f4f2d2852/VALIDATED_APPLICATION_BUNDLE.json` SHA256 `50c1e8ef41e428f7629ea9cb9598ddd18fd7847b7f9a08b785977a73b16bba6d`
- `EP_PERF_BICG_192C29C0_S_REF_V1`: `/root/data/ep_l2_full_workload_performance_20261027_v1/cases/EP_PERF_BICG_192C29C0_S_REF_V1/run/37c6e138-54f0-49f0-b0cc-2b9bdab2f24f/VALIDATED_APPLICATION_BUNDLE.json` SHA256 `33746d598dfb7794f03253cc19a1daee436600b2dd9f56fc6204706cc751848c`
- `EP_PERF_BICG_192C29C0_WV_ZERO_RO_REF_V1`: `/root/data/ep_l2_full_workload_performance_20261027_v1/cases/EP_PERF_BICG_192C29C0_WV_ZERO_RO_REF_V1/run/72f27153-e6ca-4c3a-9d30-29c839687407/VALIDATED_APPLICATION_BUNDLE.json` SHA256 `06e3650c0cec97842e7ed84efcd936b1f1a10fd6b160cf9754b0846a1e0dcf43`
- `EP_PERF_BLACKSCHOLES_09EFF62B_F_REF_V1`: `/root/data/ep_l2_full_workload_performance_20261027_v1/cases/EP_PERF_BLACKSCHOLES_09EFF62B_F_REF_V1/run/3bb641f1-0276-481b-949b-3955718aade1/VALIDATED_APPLICATION_BUNDLE.json` SHA256 `d45a9f72236f6ca9f37c30f63e5abb8cd6a4a69e66edc56c9dbf265da2db8edc`
- `EP_PERF_BLACKSCHOLES_09EFF62B_S_REF_V1`: `/root/data/ep_l2_full_workload_performance_20261027_v1/cases/EP_PERF_BLACKSCHOLES_09EFF62B_S_REF_V1/run/da827081-3dad-4351-8fe3-b985d6132a85/VALIDATED_APPLICATION_BUNDLE.json` SHA256 `edb88890acfc3bf52d27d92cd9f1b5505b5eaf517a68068b71cd55fc5a250982`
- `EP_PERF_CONV_F_REF_V1`: `/root/data/ep_l2_full_workload_performance_20261027_v1/cases/EP_PERF_CONV_F_REF_V1/run/7ca3920a-c7c6-4b62-8266-d8c10eb886fd/VALIDATED_APPLICATION_BUNDLE.json` SHA256 `7da7d68c6036767185d727fa3b6baa5c5d3c525c5e0cb970bb18a686c51527a2`
- `EP_PERF_CONV_S_REF_V1`: `/root/data/ep_l2_full_workload_performance_20261027_v1/cases/EP_PERF_CONV_S_REF_V1/run/6b2ed072-bc0c-4cca-8cbd-5366535d892f/VALIDATED_APPLICATION_BUNDLE.json` SHA256 `435f88a8972779761cb99612e32da8f112ed07c3a51a2e2db60ff155499ad805`
- `EP_PERF_DWT2D_8E07074A_F_REF_V1`: `/root/data/ep_l2_full_workload_performance_20261027_v1/cases/EP_PERF_DWT2D_8E07074A_F_REF_V1/run/54960f5d-6cf0-4a9e-b6b2-966e11932675/VALIDATED_APPLICATION_BUNDLE.json` SHA256 `fa8e4a455aaa4fdbe9d3e19499e68fe11cf959440b2a2bd2571e5bcc4b22faa8`
- `EP_PERF_DWT2D_8E07074A_S_REF_V1`: `/root/data/ep_l2_full_workload_performance_20261027_v1/cases/EP_PERF_DWT2D_8E07074A_S_REF_V1/run/29b83fa1-b8da-4768-abd1-c7b300f447cc/VALIDATED_APPLICATION_BUNDLE.json` SHA256 `4c4f26d2faf556b49db4a60b9078df05a4d7e886a69a16e7298788dddd5bd562`
- `EP_PERF_FASTWALSHTRANSFORM_FC3A9062_S_REF_V1`: `/root/data/ep_l2_full_workload_performance_20261027_v1/cases/EP_PERF_FASTWALSHTRANSFORM_FC3A9062_S_REF_V1/run/1de868e7-e434-4ead-85b3-a2caf283695b/VALIDATED_APPLICATION_BUNDLE.json` SHA256 `3dd4102e63200837e509c1a8bda3fc179668fc584f1412bbc3a9c114d1608177`
- `EP_PERF_FASTWALSHTRANSFORM_FC3A9062_WV_ZERO_RO_REF_V1`: `/root/data/ep_l2_full_workload_performance_20261027_v1/cases/EP_PERF_FASTWALSHTRANSFORM_FC3A9062_WV_ZERO_RO_REF_V1/run/f7f6e8a3-18d4-4c30-be5e-2965f752eaa5/VALIDATED_APPLICATION_BUNDLE.json` SHA256 `901100fc30ee5606a2f7415f5ea83ed6d1c053f443c18017f83f8bc4b020f6ea`
- `EP_PERF_GAUSSIAN_B5FC8DF0_F_REF_V1`: `/root/data/ep_l2_full_workload_performance_20261027_v1/cases/EP_PERF_GAUSSIAN_B5FC8DF0_F_REF_V1/run/8985b930-0763-426f-bd50-93d2a2355101/VALIDATED_APPLICATION_BUNDLE.json` SHA256 `aac6a95d033a63b98d6845ecfc8a705016984dd20e929aa39f731d0423129c97`
- `EP_PERF_GAUSSIAN_B5FC8DF0_S_REF_V1`: `/root/data/ep_l2_full_workload_performance_20261027_v1/cases/EP_PERF_GAUSSIAN_B5FC8DF0_S_REF_V1/run/548fe8b4-bc08-4fb9-9724-6d73e19cf8d5/VALIDATED_APPLICATION_BUNDLE.json` SHA256 `7c55c66c7ed684399532acc9fe1b8f362b512c1ec7daa9229fe5c19e3bed39a8`
- `EP_PERF_GEMM_140F6ED3_F_REF_V1`: `/root/data/ep_l2_full_workload_performance_20261027_v1/cases/EP_PERF_GEMM_140F6ED3_F_REF_V1/run/28c05828-94ea-4213-996d-14be69b56064/VALIDATED_APPLICATION_BUNDLE.json` SHA256 `33a559ab5285024b7b4e9124d447c07b30fb3fc96ec084ec1e28f8844abd10fb`
- `EP_PERF_GEMM_140F6ED3_S_REF_V1`: `/root/data/ep_l2_full_workload_performance_20261027_v1/cases/EP_PERF_GEMM_140F6ED3_S_REF_V1/run/2f302196-d44d-4470-8335-2dfbb83d41c0/VALIDATED_APPLICATION_BUNDLE.json` SHA256 `d0cc0cf72ca1b488fc2d05e9a8a241bf3999a46f2f8d5a56eb97258f79684753`
- `EP_PERF_GEMM_140F6ED3_WV_ZERO_RO_REF_V1`: `/root/data/ep_l2_full_workload_performance_20261027_v1/cases/EP_PERF_GEMM_140F6ED3_WV_ZERO_RO_REF_V1/run/4d594974-6f7d-4675-a704-5218f3a0d1b4/VALIDATED_APPLICATION_BUNDLE.json` SHA256 `21069b7d215c485bd902436076bc8469d649c766bf1570c4a32c4d202d095593`
- `EP_PERF_GESUMMV_A953FB7D_S_REF_V1`: `/root/data/ep_l2_full_workload_performance_20261027_v1/cases/EP_PERF_GESUMMV_A953FB7D_S_REF_V1/run/a6e0884d-a8c7-4a1e-93d8-3c472a617ecc/VALIDATED_APPLICATION_BUNDLE.json` SHA256 `b61e5958b1be6052eb43325a6fe38d3e13615a2ca3fd0b7862a94a62d56c3fb2`
- `EP_PERF_HEARTWALL_81949DE8_F_REF_V1`: `/root/data/ep_l2_full_workload_performance_20261027_v1/cases/EP_PERF_HEARTWALL_81949DE8_F_REF_V1/run/3e6b0df8-dc5d-4050-99b3-29cd037a6831/VALIDATED_APPLICATION_BUNDLE.json` SHA256 `cc825795e9ad863294fee7eded79d03da9372676a6eb799bfb21c0264d427a3f`
- `EP_PERF_HEARTWALL_81949DE8_S_REF_V1`: `/root/data/ep_l2_full_workload_performance_20261027_v1/cases/EP_PERF_HEARTWALL_81949DE8_S_REF_V1/run/c716c641-797b-41f2-8e75-af2c8290a1fe/VALIDATED_APPLICATION_BUNDLE.json` SHA256 `d02192a8c73b5f88b355a47b9633f908416f296d50595b24b0bb4ed8c044a9a6`
- `EP_PERF_HISTOGRAM_85ECC480_F_REF_V1`: `/root/data/ep_l2_full_workload_performance_20261027_v1/cases/EP_PERF_HISTOGRAM_85ECC480_F_REF_V1/run/1b68cd01-be2e-4349-a951-3c7a11c68c97/VALIDATED_APPLICATION_BUNDLE.json` SHA256 `d33d38faec4bef47bae87d8bf1d368d5093ba34f854e011174f87d74c70f7767`
- `EP_PERF_HISTOGRAM_85ECC480_S_REF_V1`: `/root/data/ep_l2_full_workload_performance_20261027_v1/cases/EP_PERF_HISTOGRAM_85ECC480_S_REF_V1/run/6fe2bdd8-a590-4198-ae6e-a9e2c2bd1f60/VALIDATED_APPLICATION_BUNDLE.json` SHA256 `0ba114cd6c2f1e81767459eaf700a17e13613d2eb43086f828bda37e5e056ea4`
- `EP_PERF_LUD_28B97CD0_F_REF_V1`: `/root/data/ep_l2_full_workload_performance_20261027_v1/cases/EP_PERF_LUD_28B97CD0_F_REF_V1/run/dda5f472-5b18-49b8-8bdf-82a198531719/VALIDATED_APPLICATION_BUNDLE.json` SHA256 `c37ecd20402c9e30acb8b6e8cbd7da235febda4476cc16d730e653d1b5bf6fc5`
- `EP_PERF_LUD_28B97CD0_S_REF_V1`: `/root/data/ep_l2_full_workload_performance_20261027_v1/cases/EP_PERF_LUD_28B97CD0_S_REF_V1/run/9fd21da4-3304-4c09-844a-856c565e2a40/VALIDATED_APPLICATION_BUNDLE.json` SHA256 `4ea74430c6e246b0475252c42bfb01e7a3914445b2b19833587d9bbb986040cc`
- `EP_PERF_MERGESORT_ADD5C722_F_REF_V1`: `/root/data/ep_l2_full_workload_performance_20261027_v1/cases/EP_PERF_MERGESORT_ADD5C722_F_REF_V1/run/bdb52ebe-e9c1-4223-9e52-420f4987db72/VALIDATED_APPLICATION_BUNDLE.json` SHA256 `1802cac7015d567b90e998101817eb303a103790373eb77cde36e09c6d79f432`
- `EP_PERF_MERGESORT_ADD5C722_S_REF_V1`: `/root/data/ep_l2_full_workload_performance_20261027_v1/cases/EP_PERF_MERGESORT_ADD5C722_S_REF_V1/run/9a391dc2-6538-40a1-ab07-b82964ed53a8/VALIDATED_APPLICATION_BUNDLE.json` SHA256 `0625622550198353b360ddccec9842232e5b75ca6df552361f23290a2659e41e`
- `EP_PERF_MVT_39D1748B_F_REF_V1`: `/root/data/ep_l2_full_workload_performance_20261027_v1/cases/EP_PERF_MVT_39D1748B_F_REF_V1/run/28e0d3cb-ff46-43af-997e-5a335c2cbd3e/VALIDATED_APPLICATION_BUNDLE.json` SHA256 `6b2f7e41823b1dbda0cb1bed23b67c6251778e60f85e6ac71c88829042bfd3ce`
- `EP_PERF_MVT_39D1748B_S_REF_V1`: `/root/data/ep_l2_full_workload_performance_20261027_v1/cases/EP_PERF_MVT_39D1748B_S_REF_V1/run/90b835e8-3023-4e86-a48e-337d6dc0ba70/VALIDATED_APPLICATION_BUNDLE.json` SHA256 `c339d0e2dda3f43de63a1ab632e8e5b382ad1921b0e7c37ea5a0ff6a9ff609be`
- `EP_PERF_PARTICLEFILTERFLOAT_3904B55B_S_REF_V1`: `/root/data/ep_l2_full_workload_performance_20261027_v1/cases/EP_PERF_PARTICLEFILTERFLOAT_3904B55B_S_REF_V1/run/2aac88de-75fc-40c8-8fac-b3fb80ed3d1d/VALIDATED_APPLICATION_BUNDLE.json` SHA256 `22ad37237dbc5b0f633ad3d8ec7486dd0647f6cdf07e3db9c02b262a8fee5550`
- `EP_PERF_PARTICLEFILTERFLOAT_3904B55B_WV_ZERO_RO_REF_V1`: `/root/data/ep_l2_full_workload_performance_20261027_v1/cases/EP_PERF_PARTICLEFILTERFLOAT_3904B55B_WV_ZERO_RO_REF_V1/run/f628575e-d5a1-46f9-a859-e07c6d4ae261/VALIDATED_APPLICATION_BUNDLE.json` SHA256 `fa5d91b6bf4f04db69da6b747330758e9706ef692f440c01a5963546ba2b34ec`
- `EP_PERF_SGEMM_F_REF_V1`: `/root/data/ep_l2_full_workload_performance_20261027_v1/cases/EP_PERF_SGEMM_F_REF_V1/run/b3adef4b-c1a8-4f20-b341-2e85f40b0cb8/VALIDATED_APPLICATION_BUNDLE.json` SHA256 `b2b0131cef449f7ff68301d98ce62f75c384457da5ccc1ba52a6c3fc881fbcf2`
- `EP_PERF_SGEMM_S_REF_V1`: `/root/data/ep_l2_full_workload_performance_20261027_v1/cases/EP_PERF_SGEMM_S_REF_V1/run/b8b08029-4c0b-4a20-8bb2-774fd8e17181/VALIDATED_APPLICATION_BUNDLE.json` SHA256 `e2fa0437c2e38e6d3ecb4c1b36acb872ed9d512d6fed92558154ef5bb7acfe88`
- `EP_PERF_TRANSPOSE_DA6CAAE1_F_REF_V1`: `/root/data/ep_l2_full_workload_performance_20261027_v1/cases/EP_PERF_TRANSPOSE_DA6CAAE1_F_REF_V1/run/6738eaa8-644f-4fb1-af2e-b3130fa48919/VALIDATED_APPLICATION_BUNDLE.json` SHA256 `1b48b8e55dce3222b1d6949cfd38ec94ae678aa9f5c2057aed2539ce708ebf08`
- `EP_PERF_TRANSPOSE_DA6CAAE1_S_REF_V1`: `/root/data/ep_l2_full_workload_performance_20261027_v1/cases/EP_PERF_TRANSPOSE_DA6CAAE1_S_REF_V1/run/4ee41d56-bf45-4cf4-afc7-f8f27bf74313/VALIDATED_APPLICATION_BUNDLE.json` SHA256 `b9fb3eb16e3f851fa4d8361e12181bd60f60081679142a153f3efc2be309df04`
- `EP_PERF_TRANSPOSE_DA6CAAE1_WV_ZERO_RO_REF_V1`: `/root/data/ep_l2_full_workload_performance_20261027_v1/cases/EP_PERF_TRANSPOSE_DA6CAAE1_WV_ZERO_RO_REF_V1/run/f9a923af-d448-477b-86f7-0c8ccfbd20b9/VALIDATED_APPLICATION_BUNDLE.json` SHA256 `ee48559aa7a9e20f301983b6839efa5e0d065d3b549abcccb9e24477de44a9ec`
- `EP_PERF_VECTOR4M_F_REF_V1`: `/root/data/ep_l2_full_workload_performance_20261027_v1/cases/EP_PERF_VECTOR4M_F_REF_V1/run/aadf1736-04a2-4f3c-bb71-9a176d3dfc90/VALIDATED_APPLICATION_BUNDLE.json` SHA256 `193e478e32f6a2a87e5bc4c4c4cbe885c706bb2c2b2522cf363c500ed521f36e`
- `EP_PERF_VECTOR4M_S_REF_V1`: `/root/data/ep_l2_full_workload_performance_20261027_v1/cases/EP_PERF_VECTOR4M_S_REF_V1/run/f706489e-8088-4d3c-8d46-c12bab768b29/VALIDATED_APPLICATION_BUNDLE.json` SHA256 `867114818a29889eb932f3baf992c9a753437ed5356fe7463d0ea1ece015077c`
- `EP_PERF_VECTOR6M_F_REF_V1`: `/root/data/ep_l2_full_workload_performance_20261027_v1/cases/EP_PERF_VECTOR6M_F_REF_V1/run/38ec0afb-8560-43a2-a199-87cc7cba83ae/VALIDATED_APPLICATION_BUNDLE.json` SHA256 `713f52c5a999ee7755469d1615a5ea3db24e983c23dd6d256c62919547573960`
- `EP_PERF_VECTOR6M_S_REF_V1`: `/root/data/ep_l2_full_workload_performance_20261027_v1/cases/EP_PERF_VECTOR6M_S_REF_V1/run/2bf1c80b-d57d-4a07-9274-73d820978c04/VALIDATED_APPLICATION_BUNDLE.json` SHA256 `b7879dc58b2a3e703561eeaa59f1e3b5240afba2f05d0e5ba2361e574da6f133`
