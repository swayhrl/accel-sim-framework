# Mid-Tag matched performance family V1

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
