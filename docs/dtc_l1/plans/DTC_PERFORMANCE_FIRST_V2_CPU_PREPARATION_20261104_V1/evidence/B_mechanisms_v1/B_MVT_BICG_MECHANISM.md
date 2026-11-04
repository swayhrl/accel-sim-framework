# MVT/BICG: performance mechanism and counterevidence (CPU-only V2)

Frozen capture: V3 `20261104T155603_725e5ee5`,11/32 structural points accepted,21 not yet closed;16 Tag safety HOLD remain separate. Provider SHA `ebf0e09f8304bd03fa37ea875a59370095321eb0af7f931eadd8ad4298cfd81f`. This report does not wait for V1 or claim a completed32-point experiment. It uses strictly closed outputs only, starts no model/service and changes no V1 source, owner, identity, result or paper.

## Measured outcome and kernel localization

|Program|DH-P0 cycles|DH-PHYS768 cycles|S_DH = I|CH-P0 / candidate|
|---|---:|---:|---:|---:|
|MVT|34,687,540|30,609,855|1.133214777|0.868386178|
|BICG|28,685,812|30,892,841|0.928558562|0.851287779|

MVT reduces cycles11.7555%; BICG increases cycles7.6938%. Both candidates still take more cycles than their matched traditional CH-P0 references. All270 effective options differ only in physical640->768, retaining512 Tags, OO PIB128, Hash, finite widths,10MiB L2 and850MHz DRAM.

|Actual kernel|Instructions|P0 cycles|768 cycles|Delta|
|---|---:|---:|---:|---:|
|MVT K1 `_Z11mvt_kernel1PfS_S_`|71,380,992|33,032,429|28,955,953|-4,076,476|
|MVT K2 `_Z11mvt_kernel2PfS_S_`|74,285,056|1,655,111|1,653,902|-1,209|
|BICG K1 `_Z12bicg_kernel1PfS_S_`|74,285,056|1,655,347|1,655,347|0|
|BICG K2 `_Z12bicg_kernel2PfS_S_`|71,380,992|27,030,465|29,237,494|+2,207,029|

The input identities are MVT `f437190767aaed4921e11e6b85f80fb3348da90ec0f18fa8fa1bdfcd76ae3079` and BICG `ae34174fbbdf83b20a72f44492665cf4b99ed35563f482f7d14763e89f398aef`; each has2 stream0 kernels,16 CTAs/kernel,145,666,048 total instructions. These are actual trace contracts, not a claim of numeric/full-application validity.

## Requests, mapping and physical lifetime

|Whole replay counter|MVT P0->768|BICG P0->768|
|---|---:|---:|
|OO valid hits|6,155,579->11,524,013|7,087,138->11,263,033|
|OO pending hits|67,064->32,598|61,793->41,390|
|OO new misses = lower created/issued/responses|12,127,693->6,793,725|11,201,149->7,045,657|
|Tag mapping evictions|12,111,309->6,777,341|11,184,765->7,029,273|
|Deferred / final-Ref reclaims (equal)|10,989,092->5,528,257|9,975,153->5,862,970|
|DRAM read32B atoms|20,574,896->19,993,536|17,688,864->20,596,672|
|L2 GLOBAL read conditional miss fraction|42.4130%->73.5735%|39.4800%->73.0829%|

MVT lower requests fall43.9817% and DRAM reads fall2.8256%; BICG lower requests fall37.0988% but DRAM reads rise16.4386%. Selected reference populations are unchanged, and GLOBAL L2 accepted32B sectors equal4 times lower128B requests in these runs. A higher conditional L2 miss fraction can partly reflect filtering of former L2 hits; it is not alone evidence of worse cache behavior. BICG's absolute DRAM increase is additional evidence of a changed downstream demand/cache-history interaction, whose address/order/latency cause remains unmeasured.

Source rejects two tempting explanations. `find_tag` searches only512 logical mappings; an unmapped physical generation protected by live Refs is not address-searchable. More physical slots are not more lookup capacity or direct reuse of an evicted unmapped line. Physical availability can change when a miss is admitted and a victim replaced, thereby changing timing/interleaving; current counters do not identify this as the critical cause. A valid hit means the mapped physical line is ready in this model, and still passes Tag/collection/WB service; it does not imply zero instruction latency.

Map-loss release sums/counts are preserved in JSON. Their per-recorded-release quotient rises in both programs while the release population shrinks; this does not establish longer lifetime for each reference or critical blocking. Terminal Ref/PIB/inflight0 establishes drain. Retained mapped physical gauge is not a pressure total.

## New existing-CSV evidence: exact cumulative endpoints

The archived per-bank CSV explicitly prints zero values omitted by stdout. Fixed Core registers absolute references to constructor-zero `m_tot_stats/m_tot_fail_stats`; `cache_stats::clear()` does not clear these total arrays. Framework prints CSV at each kernel end. All four closed CSV hashes match their accepted archive manifests; exact kernel-end cycle/instruction/CTA and read/miss totals reconcile with raw/strict. K2 counts below are **same-run K2-end minus K1-end**, never a final cumulative snapshot relabeled K2.

|GLOBAL read retry events|MVT K1 P0->768|BICG K2 P0->768|
|---|---:|---:|
|MSHR entry limit|108,621,212->98,532,676|142,533,205->179,225,930|
|Miss queue full|52,360,071->51,947,551|15,514,452->34,133,834|
|MSHR merge limit|17,573->48,297|14,509->59,229|

BICG K1 CSV explicitly has entry/missqueue0; its merge events remain892. This fills a prior stdout-only missing endpoint without altering the old packet or imputing zero. These are retries, not occupancy or queue time. BICG whole replay all-type L2 reservation failures rise34.8021%, and ICNT-to-subpartition admission blocked events rise30.1094%. Neither count is GPU critical-path cycles.

For40 L2 subpartitions, population CV of exact K2 miss-sector delta counts, including every zero, decreases in BICG0.946292->0.924976. Thus a claim of increased overall relative L2-bank-count imbalance is unsupported. This does not exclude higher absolute load, DRAM-bank contention or short-time hotspots. The metric is not a DRAM-bank CV or service-latency distribution. Compact sampled cumulative CSV rows are retained for further read-only checks; cycle samples across designs are not automatically equal-work intervals.

## PIB and completion timing: counterevidence

OO lower-create-queue-full and lower-cap-full are explicitly0 in these runs. OO no-free-physical and PIB-full events, Tag-bank failed grants, per-SM occupancy histograms and critical queue/wait times are unavailable in consumed outputs. A source getter is not a measured counter.

MVT app post-ready sum grows8,982,782->8,984,215 despite faster execution; BICG grows9,069,203->9,135,438. WB-wait sums decline45,586->20,662 and32,826->17,024, respectively. This does not support a simple uniformly faster/slower aggregate completion explanation. It also cannot exclude a different small critical subset: these are overlapping retired-item sums, not critical-path time.

Exact64SM clock-window means rise in the responsive phases: MVT K1 PIB1.5700->1.9072 and physical147.5333->155.2579; BICG K2 PIB1.6271->1.9412 and physical273.4550->282.5452. They are not active-SM averages or peaks;16 CTAs do not establish residency. Higher mean does not prove saturation or predict a combination. PIB192 also increases the bounded lower-create queue128->192; create/inject/retire widths remain fixed.

## Controls and source/phase context

At this frozen capture,2DCONV physical768/1024 remain462,740 cycles; GEMM physical768/1024 and TagSvc2/8 remain826,089; vectorAdd all4 families remain217,305. All known additive endpoint fields are unchanged versus DH-P0. VectorAdd has0 OO valid/pending hits and375,000 new misses under this captured read path. GEMM has0 timed DRAM read/write while2DCONV does not; neither zero response nor memcpy-prefilled L2 proves compute-bound execution or general real-GPU behavior.

`ATAX_SCAN_CONV_P0_CONTEXT.json` reuses frozen exact-authority P0 evidence only. ATAX has many deferred reclaim events; scan has few valid hits; convolutionSeparable has a high whole-replay all64SM mean PIB. These constrain future observations but are not physical/PIB response predictions: their V1 structural cells were unclosed at capture.

Candidate source at dad09c maps MVT's slow strided matrix phase first and BICG's analogous strided phase second. Source-derived lane stride and phase order motivate a retention/history hypothesis; distinct programs, input identities, initial state and unresolved capture/ELF binding prevent treating them as a controlled phase-order experiment. Static reuse is not a measured cache hit or MSHR merge.

## Testable next observations and boundary

The detailed hypothesis/contradiction matrix is `HYPOTHESES_AND_COUNTEREVIDENCE.json`. Four useful next steps are:

1. Read-only: consume already-authorized V1 physical1024/PIB192 results when closed, preserving this11-point capture and every negative/zero. Test whether lower-volume versus downstream-miss tradeoffs persist; no per-program best-GM or missing-term combination prediction.
2. Read-only: compare existing CSV phase endpoints/temporal counts at explicit cycle and instruction positions. Retain denominator filtering, cumulative/reset boundaries and unknown causal direction.
3. Separately authorized observation/replay: link per-SM physical-full/PIB-full reasons, live generations/Refs and lower address/arrival/return to instruction UID. This can distinguish a physical-lifetime admission bottleneck from changed lower filtering/cache order. No such instrumentation or simulation is executed here.
4. Separately authorized validation: readiness/collection/WB/dependent-use timestamps and numerical/coherence checks before critical-path or complete-application correctness claims. Current CPU/source checks do not provide those validations.

Physical768 adds20% nominal lifetime slots;512 lookup Tags remain fixed.128B accounting is not measured data-array payload, area/PPA or free timing. No V2 scientific simulation, GPU/capture, new request, production Core edit, V1 restart or manuscript edit is authorized by this package.

## Reproduction and evidence

All files are rooted at this B package. `CPU_REPRODUCTION.json` records the byte-identical8051 parser invocation into `snapshots/capture11_v1` (21 closed sources,27 kernel rows). Its manifest is `47bff0cdf7290fa3b9822c7ccb6b187b66e506d8140903edb081da0a3182b437`. Run `python3 -B consume_closed_csv_resources.py` then `python3 -B derive_v2_evidence.py` only in an isolated copy to reproduce derivatives; they write this package's own directory and read closed pinned sources only.43 derivation/source assertions plus4 CSV/resource source gates pass. No full archive tar re-audit is claimed; member hashes are checked against existing accepted manifests.

`MVT_BICG_KERNEL_EVIDENCE.json` contains all typed endpoints, kernel changes, canonical/bottom RESULT/UUID/raw/input SHA and unavailable observations; `KERNEL_EVIDENCE.csv` is the compact phase table. `CLOSED_CSV_RESOURCE_EVIDENCE.json` pins4 CSV/resource archive members and exact cumulative boundaries. Resource samples show no new host/cgroup OOM/throttle/swapout in the two PHYS768 observation windows; older P0 fields not exported remain null. RSS and host wall time are host diagnostics, not hardware cost or simulated-cycle causation.

Core `9eedb3131937748f0492fa83aad37d3691118d70`; Framework `02775fd795cde5aae1480d81cee6eb481d0a08f4`; binary `02a289360b42a573832698c978f21ad2125182a453067a35be60410f1eb8888d`. `SOURCE_PINS_V2.json` and22 literal source excerpts pin actual bytes equal to those Git blobs: Tag/physical access637-698, retirement801-832 and lookup1093-1113; shader finite export5918-5927 and OO print6103-6169; cache registration2323-2354 and total-array initialization657-684; absolute CSV serializer1293-1354; Framework kernel-end print180-183. Candidate source mappings retain dad09c/Atlas47a SHA and explicitly unbound capture/ELF status. Existing host-upload/source-invalidation/numerical limitations remain unresolved.
