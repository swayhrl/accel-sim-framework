# Remaining48 completion audit: existing evidence and minimal closure path

This read-only audit examines the fixed Remaining48 request and commit `b665d5ea77b5ae022a86cd03c6c464f5b11cb15e`. It does not complete a Goal, repeat the final consumer, validate numerical correctness or authorize another scientific start. Existing closed derived data and SHA-bound RESULT files were checked; no active raw was read. R1 and its services are outside this audit.

## Evidence that is complete

- New CH identities: 48 accepted, 0 archived negative, 0 pending/HOLD; consumed48/remaining0. Source-qualified final snapshot is `20261104T105114130127Z_c3570151`, manifest `7aa37a91d6506c4de5033cc72f3b0f4233bc43e64e5724128f308423a3809566`.
- CORE32: 32 fixed complete inputs, 192 accepted six-cell slots = original128 + first16CH16 + newCH48. All192 source RESULT SHA values were rechecked; the six inherited P0 aliases remain separately identified. This does not promote the original350 ledger or unresolved7.
- Final24 consumer: 144 accepted source rows, 43,524 kernel records and 7,254 matched six-cell kernel positions. Every source has contiguous ordinal1..N and a per-kernel cycle sum equal to its accepted whole replay. All144 explicitly report SINGLE_STREAM_ZERO_CUMULATIVE. Public manifest `55abe646060556421e53969451f8cf2b1b661378c44ef772720889d6daa3750b` passed all member SHA checks.
- First8: the original indexed frozen manifests and their members pass SHA checks. Existing convolutionSeparable six-source Rows/Columns authority is additionally identified below; the inherited index alone points only to the counter catalog. GEMM/2DCONV counter evidence remains F128-scoped; their six-cell performance is complete.
- C final48 already reports PASS_ALL48_INDEPENDENT_LIFECYCLE_AND_REVIEWED_INTEGER_STATISTICS. Root final integer audit already reports PASS, 192 accepted slots and48 raw terminal cycle endpoints. This audit reuses those lifecycle/archive judgments rather than repeating all archive streams.

## Complete fixed32 performance

Same32 denominator for both F settings. R=CH_cycles/DH_cycles; R>1 means DH faster. I=S_DH/S_CH compares relative advantage, not absolute speed. Positive/negative/exact-zero counts below use integer cross-products, not rounded ratios.

|F|GM S_CH|GM S_DH|GM R|GM I|CH +/=/-|DH +/=/-|I +/=/-|
|---|---:|---:|---:|---:|---|---|---|
|F128|1.015815817|1.012595183|1.096584425|0.996829509|9/21/2|7/19/6|5/19/8|
|F256|1.020645454|1.019138263|1.098447713|0.998523296|7/21/4|7/19/6|6/19/7|

Common P0 GM R is1.100072194. Both F settings improve both designs on average; neither increases aggregate DH relative advantage over P0 (I<1). DH remains faster in the aggregate (R>1); those statements are compatible. Same32 direct GM F128_cycles/F256_cycles is1.004754441 forCH and1.006461694 forDH. No bestF-per-program aggregate is constructed. Suite/distribution data remain in FULL32_STATISTICS and the source CORE32_RESULTS; the32-row CSV retains all inputs and six raw cycle values.

## Coverage of the new24

|Program|Kernel instances per cell|Six-cell detail records|
|---|---:|---:|
|BlackScholes|1|6|
|fastWalshTransform|16|96|
|histogram|8|48|
|mergeSort|13|78|
|scalarProd|1|6|
|transpose|24|144|
|bfs|11|66|
|cutcp|11|66|
|histo|80|480|
|mri-q|4|24|
|sad|3|18|
|sgemm|1|6|
|stencil|100|600|
|3DCONV|254|1524|
|3MM|3|18|
|GESUMMV|1|6|
|dwt2d|10|60|
|gaussian|126|756|
|heartwall|1|6|
|lud|46|276|
|myocyte|5993|35958|
|particlefilter_float|36|216|
|particlefilter_naive|9|54|
|srad_v1|502|3012|

The reused first8 are scan, ATAX, MVT, BICG, vectorAdd, GEMM, 2DCONV and convolutionSeparable. Their exact original report/profile limits remain authoritative; full quantitative six-cell coverage does not fill counter gaps. The forward convolution reference is first16/agents/A_convseparable_three_profiles_v1/MANIFEST.json; its full path/SHA is pinned in AUDIT.json.

## Controls, regressions and the final GES case

Examples are included as controls, not a rule for selecting workloads. Exact-zero cases such as3MM, myocyte, srad_v1, stencil and cutcp remain listed. FWT has CH slight gains and DH slight regressions under bothF. ATAX CH worsens while DH is near-zero/F256 modestly improves; MVT CH improves while DH worsens; BICG CH improves while DH worsens; scalarProd preserves a small CH-F256 regression. All are retained in the same32 denominator.

GESUMMV closes the prior missing pair: CH P0/F128/F256 =114860845/106901261/112286106; DH =89502220/86464623/90151547. S_CH=1.074457344/1.022930166, S_DH=1.035131096/0.992797384 and I=0.963398968/0.970542679. DH remains faster thanCH at each matchedF, while F256 is a DH own-design regression. One actual kernel per source, all six closed: no stage-order hypothesis is needed.

ForGES, final cumulative DRAM32B reads are CH70163098/65161203/68406632 and DH53120556/52528884/54970692. DH L2 reservation-fail attempts are288925236/293860392/276005118; ICNT admission-block events are271775567/283687590/265956790. F128 is faster despite more such events, whereas F256 is slower despite fewer. OO new misses decline30273725/30198629/29933505. These facts falsify any simple monotone claim that fewer retry/miss events necessarily means fewer execution cycles; they do not identify a unique critical path. Exact source SHA/counter detail is in final24 source_metadata and kernel parts.

## Mandatory scientific limits

- FWT K6 is a **read-active print interval**. The old frozen initial report phrase cold/read-active is not supported as a cold-start/compulsory-miss classification or request-origin attribution. Prefill exists. This forward wording preserves the old report SHA.
- MRQ latency is integer-truncated request-construction-to-bank-assignment age in core cycles, conditional on its print gate. It excludes post-assignment service; it is not full L2-to-DRAM latency or critical-path wait time. Request and32B-atom denominators differ. Do not subtract means or weight them by atoms. Other latency means retain their packet/response sampling/fold/tail limits and can be missing.
- Per-kernel cycles/instructions reset; selected L2/DTC/DRAM cumulative counters use explicit endpoint differences only. Missing endpoints remain null. Means, terminal gauges and running peaks are not differenced or summed as phase work. Reservation failures and gpu_stall_dramfull are retry/admission events, not time or occupancy history.
- L2 accepted GLOBAL reads and misses use32B sectors; DRAM issued read/write data use32B atoms across20controllers. L2 all-type misses may include writes. Lazy-fetch write misses need not imply DRAM reads. Bank READ-only distributions do not characterize all bank activity or short-time hotspots.
- CH common PAPER_BASE PIB256 and DH active OO PIB128 are different active mechanisms; generic DH frontend8 is inactive. No equal-resource/equal-area inference, and no missing DH OO conflict/full getter is replaced by aCH proxy.
- All32 have declared pre-first HtoD; actual prefill1/flushL1=1/flushL2=0/source-event OO invalidation0 remain disclosed. Zero timed DRAM traffic is replay/initial-state exposure, not compute-bound proof or a real-GPU conclusion. Interkernel-copy coherence and numerical freshness are not certified by accepted timing counters.
- myocyte5993=13x461 is compatible arithmetic, not accepted solver steps/attempts or full-application proof; phase_epoch is not kernelordinal. SRAD502 and450CTA/1CTA same-symbol phases remain distinct. 3DCONV254 ordinals are not scalar i. Source/ELF/macros/numerical binding remains candidate or UNKNOWN;3MM initialization and myocyte uploads retain their specific correctness questions.
- Fixed SM70/V100-derived64SM replay,10MiB L2 and850MHz DRAM is not a nativeV100 hardware measurement. FR capacity and shared-credit allowances change together. RSS/host time is not hardware PPA. English LaTeX v0.23 is unchanged.

## Minimal remaining closure work

No new simulation or final24 parser rerun is needed. Root can:

1. Publish final24 MANIFEST and exactly its public members, plus final C48/Root integer audit with their original source pins. Do not publish private staging or rerun the one-shot chain.
2. Add a final32 narrative and GES supplement using these closed tables; forward-link the existing convolution six-source report. Keep GEMM/2DCONV F256 counter-scope gaps explicit, or supplement only if claiming full six-profile mechanism coverage.
3. Visually inspect already-rendered final common32 PNGs, record final approval and promote that exact provider. The current published approved figures remain partial24/32, not final.
4. Include final48 measured resources and its independent review when ready; update bounded next-stage recommendations against final32. This oldGoal grants no new simulations, combinations, instrumentation/capture/109 work, unresolved inputs or manuscript edits. Later separately authorized Goals have their own authority.
5. Submit the final immutable package, verify remote/readback, record requirement-by-requirement Root scientific closure, then transition the oldGoal. b665 itself is terminal progress publication and explicitly final_scientific_closure=false; it must not be relabeled retroactively.

These are publication/signoff and explicit scope tasks. Observed905 checks passed; they do not replace Root final responsibility or a new independent review of this forward report.
