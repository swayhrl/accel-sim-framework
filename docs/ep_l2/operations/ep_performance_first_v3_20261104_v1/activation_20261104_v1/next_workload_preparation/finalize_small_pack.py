from pathlib import Path as P
import json,hashlib,csv
O=P('/root/data/ep_l2_full_workload_performance_20261027_v1/research/performance_first_v3_20261104_v1/activation_20261104_v1/next_workload_preparation')
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def ref(p):return dict(path=str(p),sha256=sha(p),bytes=P(p).stat().st_size)
def read(p):return json.loads(P(p).read_text())
def put(p,d):P(p).write_text(json.dumps(d,indent=2,sort_keys=True)+'\n');return ref(p)
resources=dict(Payload_slots_per_slice=1168,Resident_nominal=1024,Bypass_slots=128,static_WB_slots=16,banks=4,bank_ops_per_CORE_cycle=1,descriptors=512,WAD_entries=128,Line_MSHR_entries=128)
for p in list((O/'point_candidates').glob('*.json'))+[O/'OPTIONAL_3MM_WV_REF32W8_CANDIDATE.json']:
 d=read(p);d['physical_resources']=resources;put(p,d)
p=O/'OPTIONAL_3MM_WV_REF32W8_CANDIDATE.json';d=read(p);d['same_background_peer_cohort']='EP_PERF_3MM_F9F80028_S_REF_V1';d['existing_S_peer_usage']='EXACT_SOURCE_INPUT_OBSERVER_REF_REUSE_REQUIRES_FUTURE_MAIN_REVIEW';put(p,d)
index=read(O/'CONDITIONAL_FOUR_POINT_INDEX.json');checks=[]
cases={}
for r in index['points']:
 p=P(r['proposal_ref']['path']);d=read(p);r['proposal_ref']=ref(p);cases[d['cohort']]=d
 assert len(d['expected_effective_options'])==282 and d['approved_launches']==d['application_budget']==0 and not d['scientific_launch_permission']
 assert d['M']is False and d['T']is False and d['ro_qualification_ref']is None
 assert len(d['native_dependency_pin_population'])==22
 checks.append(dict(cohort=d['cohort'],complete282_dictionary=True,Source5_unmodified=True,RO_disabled=True,Native22_preserved=True,actual_new_option_parser_execution='NOT_EXECUTED_PROPOSAL_ONLY'))
for d in cases.values():
 peer=cases[d['same_background_peer_cohort']];diff={k for k,v in d['expected_effective_options'].items()if v!=peer['expected_effective_options'][k]}
 assert diff=={'-gpgpu_ep_l2_ft_mode','-gpgpu_ep_l2_tvd_clean','-gpgpu_ep_l2_tvd_dirty'}
 assert d['source_identity']==peer['source_identity']and d['input_identity_sha256']==peer['input_identity_sha256']and d['observer_env']==peer['observer_env']and d['geometry']==peer['geometry']
index['optional_extra_anchor_ref']=ref(O/'OPTIONAL_3MM_WV_REF32W8_CANDIDATE.json');put(O/'CONDITIONAL_FOUR_POINT_INDEX.json',index)
put(O/'PASSIVE_PROPOSAL_CHECKS.json',dict(status='PASS_ONLY_FOUR_POINT_PROPOSAL_IDENTITIES_OPTIONS_AND_FAIR_PAIRS',checks=checks,pairs=2,new_Source_or_ELF_builds=0,CPU_geometry_tests=0,actual_new_option_parser_execution=False,new_models=0,new_budget=0,registry_or_current_runtime_write=False))
(O/'NEXT_WORKLOAD_CONDITIONAL_PROPOSAL.md').write_text("""# Next real-workload four-point proposal

**PROPOSAL READY; scientific launch HOLD. Approved/registered starts:0.** No active V3 Source/runtime/Native/ledger or dispatcher changes.

Exactly four candidate points: Source78/accepted ELF, Stencil and3MM, G64x8, S/WV_ZERO_RO. Keep64 slices,32 DRAM channels, DRAM850/Core-L2-ICNT1132MHz,L100,FR-FCFS128, Payload1168/four-bank P1, queues/MSHR/WAD/descriptor and observer111 unchanged. RO/M/T OFF; no certificates or extra NI models. Scientific selection waits for Main's current GEMM4 result review and a separate exact authorization.

| Input | Accepted Source78 REF S | Accepted REF WV | Kernels | Prior S host time | Prior WV host time |
|---|---:|---:|---:|---:|---:|
| Stencil bd0309df... |5242939 cycles|4768893 cycles|100|4.83h|3.71h|
|3MM f9f80028...|1696618 cycles|UNKNOWN, absent|3|7.11h|UNKNOWN|

Both are **long-tail candidates** under historical conditions.3MM's three kernels do not establish a short job; observed host time was longer. Prior load/IO differ, so these are recorded costs, not controlled cross-workload throughput predictions or a promised ETA. Prior RSS:Stencil0.49-0.50GiB,3MM S3.53GiB. Preparation forecasts1GiB/5GiB respectively; hot/output growth64MiB/16MiB, with future real dynamic admission. Large inputs remain true164; no Trace scan/hash/copy.

Three references close exact Source5, input identity, original full282, ordered kernel/commandlist identity, official CLOSED_ACCEPTED population, archive SHA reference and two independent restore receipts. Archive bytes were not rehashed/re-restored in this small preparation. Details: EXACT_ACCEPTED_REFERENCE_IDENTITY_INDEX.json.

The3MM WV_REF is absent from both D254 and the bounded current registry check. **Its new G64x8 matched S/WV pair is still scientifically possible**; no old WV absolute anchor means the WV parameter improvement versus REF remains UNKNOWN. The3MM S input eligibility does not automatically qualify WV; future per-input/mode eligibility is pending. Old F is not substituted.

OPTIONAL_3MM_WV_REF32W8_CANDIDATE.json proposes one separately authorized new WV_REF anchor, paired with exact reusable accepted S_REF. It is outside the four, approved0 and not automatically released. No expansion of the current10 starts.

## Future registration safeguards

FUTURE_NATIVE_MONITOR_AND_CLOSURE_REQUIREMENTS.json requires the incident-derived43-key checklist plus an AST audit of the actually selected Source78 engine/helper. Fresh boot ID/mount, actual dispatch CPU, limits and full Native dependency closure must pass before consume and after CPU binding. SOURCE78_NATIVE_DEPENDENCY_CLOSURE.json preserves17 Source78 library and5 tool pins from accepted Source78 references. Do not reuse the incident's unchanged Source862-hardcoded validator or replace this population wholesale with Host pins.

This is a proposal schema, not a runnable FROZEN_SPEC. Full Host/parser/native qualification and current resource/Source/input admission remain pending. No source rebuild or repeated geometry CPU tests were done. Passive checks confirm four282-option dictionaries, exact typed RO OFF,22 Native pins and two fair S/WV pairs differing only by the three existing mode flags. New actual option-parser/appNI execution was not performed.

Main can submit these bounded choices after GEMM completes: Stencil pair,3MM pair with explicit unknown WV absolute anchor, or separately add the optional anchor under fresh authorization. No additional workload search or automatic launches are part of this handoff.
""")
files=[dict(member=str(p.relative_to(O)),**ref(p))for p in sorted(O.rglob('*'))if p.is_file()and p.name!='DELIVERY_MANIFEST.json']
manifest=dict(schema='EP_PFV3_NEXT_WORKLOAD_READONLY_PREPARATION_DELIVERY_V1',status='PROPOSAL_READY_NOT_AUTHORIZED_NO_EXECUTION',files=files,exact_accepted_references=3,missing_exact_WV_reference_count=1,planned_conditional_Tag_points=4,optional_separate_anchor_points=1,approved_starts=0,registered_starts=0,actual_new_models=0,CPU_geometry_retests=0,active_Source_runtime_graph_changed=False,huge_Trace_or_raw_scans=False,Main_scientific_choice_pending_GEMM4=True)
r=put(O/'DELIVERY_MANIFEST.json',manifest);print(json.dumps(dict(delivery_ref=r,file_count=len(files),bytes=sum(f['bytes']for f in files))))

