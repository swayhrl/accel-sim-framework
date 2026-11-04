from pathlib import Path as P
A=P('/root/data/ep_l2_full_workload_performance_20261027_v1/research/performance_first_v3_20261104_v1/agent_a_mid_tag')
docs={
'MID_TAG_GEOMETRY_QUALIFICATION_V1.md':"""# Mid-Tag geometry qualification V1

**PASS: production geometry, CPU protocol and 282-option engineering qualification. HOLD: formal activation pending new scope authorization and Main installation.**

Accepted Source78 Core 78f4b59e865b136eede74df74c44c210f5b4ca04 and ELF 78d4e96bb79c776e27146bcf168d7c70cf3897ef9cb84d837d8974fec4c91b8a are unchanged. Framework/vendor/library identities are pinned in evidence/SOURCE78_READBACK.json. No Source92, P1 correction, host-write V3, CLEAN quota or high-clock repair is included.

| Geometry | Logical Tags/slice | Nominal addressability, 64 slices | Physical Payload/slice | Engineering status |
|---|---:|---:|---:|---|
| REF32x8 |256|2 MiB|1168 line slots|accepted reference reused|
| G32x16 |512|4 MiB|1168 line slots|PASS, not application accepted|
| G64x8 |512|4 MiB|1168 line slots|PASS, not application accepted|
| G64x16 |1024|8 MiB|1168 line slots|accepted reference reused|

Both candidates keep32 DRAM channels,64 subpartitions,128B lines/32B sectors, four Payload banks, one operation/bank/CORE cycle, nominal Resident1024/Bypass128/staticWB16, descriptor512, WAD128 and ordinary Line-MSHR128. Nominal Tag capacity is distinct from physical Payload capacity. Static S retains its declared fixed allocation partition; WV uses the already qualified unified allocation policy.

Actual production mapping is used. gpu-cache.cc:97-169 dispatches set_index to configured P/IPOLY;32 sets use the32-set polynomial rather than masking a64-set index. Existing Source78 actual constructor controls G32W16_S/G64W8_S cover all active sets and are reused. gpu-cache.h:3335-3431 retains finite-policy and geometry/resource guards. gpu-cache.h:3052-3079 binds dense logical Tag indices and checks Payload identity/bank color; physical Resident capacity remains fixed.

## Tests actually executed this round

The owned harness changes only the prior external protocol fixture's coupled sets/ways choice into two explicit geometry arguments. It links unchanged accepted production archives; no cache source or assertions are edited.

Four geometry/mode controls, each with MS111 and MS011: **eight runs PASS**. The fixture drives real memory_sub_partition frontend, Tag allocation, dirty replacement/WB, WAD retention/completion, reversed independent responses and complete drain. G32x16 produces17 replies/one dirtyWB/15 reverse returns; G64x8 produces9 replies/one dirtyWB/7 reverse returns. P1, ownership, physical capacities and drain assertions pass. S and WV are independently exercised with RO OFF and TVD disabled/enabled respectively.

Every MS011/111 pair has identical semantic markers including fixture cycles, replies, WB count and drain. This proves bounded MS-only CPU NI; B0/M0a remain ON. It is not application NI, timing calibration or application performance. No new observer is introduced.

All eight prospective workload/mode/geometry configurations passed the real Source78 plus trace option parser: exactly282 unique options, no conflicts; only -gpgpu_cache:dl2 differs from each exact original mode reference. Read evidence/ACTUAL282_CPU_RECEIPT.json, EXACT_282_DELTAS_BY_POINT.json and PRODUCTION_CPU_AND_MS_NI.json.

No full GPU application model, Trace-body scan/input copy, new scientific budget or production registry write occurred.
""",
'MID_TAG_MATCHED_PERFORMANCE_FAMILY_V1.md':"""# Mid-Tag matched performance family V1

**Preparation PASS; formal Native activation HOLD, not installed or budgeted.**

Request candidate: EP_L2_MID_TAG_850MHZ_V1_20261104. Intended execution root: /root/data/ep_l2_full_workload_performance_20261027_v1/execution_midtag_v3_20261104_v1/midtag.

Exactly eight proposed starts:

1. FWT G32x16 S/WV_ZERO_RO and G64x8 S/WV_ZERO_RO: four points.
2. GEMM at the same geometries/modes: four points, after all FWT points are CLOSED_ACCEPTED with true164 SHA and two independent restores.

The Native engine enforces this release order before GEMM consumption; preparation can overlap. No conditional combinations, FR-FCFS changes, other input, observer NI starts or retries. Each candidate declares a prospective one-start contract; **registered allowance and launches are zero**. No old authorization or approved-launch inheritance.

All points retain Source78, DRAM850MHz, CORE/L2/ICNT1132MHz, L100, FR-FCFS128, original input/complete commandlist/ordered kernels, observer111 and fixed hardware resources. S/WV changes only existing mode-defining FT/TVD flags. M/T are OFF; RO certificates are not applicable. FWT is not replaced with RO-F.

MID_TAG_FAMILY_SCOPE.json lists exact candidate spec SHAs. spec_candidates/ contains complete Source5, input/member identity, ordered configs, all282 options, peer controls, SourceKEEP and terminal requirements. Large inputs remain verified true164 paths. Their bodies were not rehashed or copied.

## Reuse

evidence/REF_AND_G64X16_REUSE_QUALIFICATION.json closes eight accepted anchors: FWT/GEMM x S/WV x REF32x8/G64x16. Exact Source78/ELF, input, observer111,850MHz/L100/FR128 and full drain. REF is an absolute capacity anchor, not the matched S of new geometry. Every new geometry has a new S/WV pair. G64x16 can be reused without new starts.

## Executable Host/Native candidate

runtime_candidate/ is an owned bounded clone of the V2 system engine, common utilities, parser adapter, postprocessor and archive. The new pure mode contract admits exact eight cells. Numeric parser body/suffix and geometry math are byte-preserved. Consume-before-fork, no retry/refund, SourceKEEP, current resource admission, global Main admission lock and shared restore-window lock remain.

native_midtag_v3.candidate is executable but **not installed**. Its frontend rejects foreign cohorts/operations and requires a valid registered request and immutable specs. Prepare additionally requires Main-installed NATIVE_ENTRY_ROUTE_V3.json, exact current shared Native SHA/scoped entry and activated scope. Future global route drift HOLDs. All eight run-native calls fail closed before consume/fork without that receipt.

evidence/DRY_HOST_NATIVE_QUALIFICATION.json:126 checks PASS, including eight exact specs, four fair pairs, Source/input/clock/FR-FCFS/observer/Payload/RO mutation negatives, four premature GEMM denials, parser math verification and noninstalled Native failure. Registry fixture is in memory; no real registry, epoch, budget or shared Native changed. This is dry engineering qualification, not formal installation or application acceptance.

Reproduce:
~~~sh
python3 /root/data/ep_l2_full_workload_performance_20261027_v1/research/performance_first_v3_20261104_v1/agent_a_mid_tag/test_runtime_candidate.py
~~~

Source/CPU preparation has prepare_and_cpu.py; no full application starts. Current finalized refs are in BUNDLE_MANIFEST.json.

## Main integration

After approval: freeze exact eight specs; review Host/mode CPU receipts; register fresh budget8/admitted SHAs; bind installed scoped entry/global exact route; seal dispatch/engine/parser/resource/archive refs; use sole Main dispatcher and shared consume/admission/restore serialization. Recheck current Source/input storage identity and resource obligations per launch. Prospective one-start declarations and dry fixtures are not authorization.

New geometry application NI remains NOT_MEASURED; B0/M0a application NI NOT_PROVEN. No extra NI starts are in this eight-point family. Main must state this boundary or separately HOLD/request NI if needed.

## Cost forecast

V2 logs: FWT RSS0.65-0.68GiB and9-11min; GEMM RSS3.75-3.78GiB and58-63min. Forecasts:1GiB FWT/5GiB GEMM,10-20min/45-90min,16MiB incremental hot/result growth per case. Inherited hard stops8GiB RSS/24GiB AS/256MiB output are not extra unoccupied resource reservations. One shared restore window. Compilation peaked about416MiB RSS. Admission stays dynamic; forecasts cannot overrun another owner's commitments.
""",
'TAG_PERFORMANCE_RESOURCE_FRONTIER_V1.md':"""# Tag performance/resource frontier V1

**Eight accepted reference points reused; eight intermediate geometry points prepared, performance UNKNOWN pending authorization/execution.**

| Input | Geometry | S cycles | WV cycles | Same-background S/WV |
|---|---|---:|---:|---:|
| FWT |REF32x8|181827|178951|1.01607x|
| FWT |G32x16|UNKNOWN|UNKNOWN|UNKNOWN|
| FWT |G64x8|UNKNOWN|UNKNOWN|UNKNOWN|
| FWT |G64x16|170266|170105|1.00095x|
| GEMM |REF32x8|558588|550642|1.01443x|
| GEMM |G32x16|UNKNOWN|UNKNOWN|UNKNOWN|
| GEMM |G64x8|UNKNOWN|UNKNOWN|UNKNOWN|
| GEMM |G64x16|548988|548988|1.00000x|

TAG_PERFORMANCE_RESOURCE_FRONTIER.csv/json uses null/UNKNOWN candidate values, never zero. Existing FWT WV G64x16 improves about4.94% versus own REF; GEMM about0.30%. S and WV both benefit; this is not all EP-specific acceleration.

The two512-Tag geometries have equal nominal4MiB addressability across64 slices but different associativity and decoder/address grouping. Their comparison distinguishes organization from count without changing DRAM or physical Payload. A middle point matching1024-Tag performance would bound excess for these inputs, not prove a universal optimum.

Resource proxies relative to REF32x8:

- G32x16:2x Tag entries,2x ways/comparisons per target set; same set count.
- G64x8:2x Tag entries, same8-way comparison width;2x sets and different real decoder.
- G64x16:4x Tag entries,2x ways and2x sets.
- Physical Payload remains9.125MiB aggregate (64x1168x128B), fixed four-bank P1, WB/Bypass/descriptor/WAD/MSHR/queues. More Tag addressability does not add Payload SRAM.

These are metadata/count proxies. Exact Tag bit widths, comparator/decoder area, wiring, access energy, timing and PPA remain UNKNOWN. Declared cache timing is fixed; extra16-way comparator delay is not automatically charged. No equal-area, calibrated hardware or new T contribution claim.

Next decision: execute bounded middle-geometry matched pairs only after authorization, select least-resource point retaining useful absolute performance, preserve regressions and zeros. No automatic finer geometry scan or FR-FCFS combination is released by this package.
"""
}
for name,text in docs.items():(A/name).write_text(text)
print('wrote three bounded handoff reports')

