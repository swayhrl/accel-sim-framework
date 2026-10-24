"""Approve two precise new native requests after independent pins/code review."""
from pathlib import Path
import hashlib,json,sys,time,subprocess,os
R=Path('/root/data/shared_sm70_trace_library_20261024_v1');sys.path.insert(0,str(R/'tools'));import library_copy_v8 as e
A=Path('/root/data/ada_native_extensions_stage4_20261024_v1')
assert subprocess.check_output(['git','-C',str(A/'core'),'rev-parse','HEAD'],text=True).strip()=='e5942d5bdeb9848327dbaaf63d155ca6970904f4'
assert not subprocess.check_output(['git','-C',str(A/'core'),'status','--porcelain=v1','--untracked-files=no'],text=True).strip()
assert e.hash_file(A/'native_maps_observer_v2.py')=='3f187edf034f0d6d9f79f410ed6bbcdc0572df9a13db0c8b87cf62307d4a7c21'
assert e.hash_file(A/'native_process_status_v1.py')=='22ad2df8b69fbee913f2b41abc03181bcd789f6194a9721966e21af2c45064e1'
maps=json.loads((A/'maps_cpu_qualification_A3/QUALIFICATION.json').read_text());assert maps['all_expected_reasons'] and maps['CPU_ONLY_NOT_SIMULATOR_APPLICATION']
status=json.loads((A/'PROCESS_STATUS_CPU_QUALIFICATION.json').read_text());assert status['CPU_ONLY_NOT_SIMULATOR_APPLICATION'] and len(status['results'])==7
tests=[('jit','030fd1fd7639878945bebbf8f3f10458dc7a2f31ed92f5ce8fbf98ebe0098489','4b82409bbfeee7497e86539b465b3add14c74977624753dd310cac7eb7bf842c',1121),('warpsync','43d967e3502952cf56e8f5a163e541ac35ded18d8fddcd0c1dcb83ec20832b0a','39e87b604cb00a4b3874b9dd73d2665c5e4200a314afd44fcc5121f8947360f4',5562)]
reg=e.read('/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json');before=e.Resources()(True);results=[]
for kind,specsha,qsha,total in tests:
 B=Path('/root/data')/('ep_l2_main_ada_'+kind+'_maps_r3_compat_20261024_v1');sp=B/'control/FROZEN_SPEC.json';qp=B/'control/NATIVE_PRELAUNCH_QUALIFICATION_R2.json'
 assert e.hash_file(sp)==specsha and e.hash_file(qp)==qsha
 s=json.loads(sp.read_text());q=json.loads(qp.read_text());assert q['spec_sha256']==specsha and q['status']=='PRELAUNCH_QUALIFIED_NOT_APPLICATION_ACCEPTED'
 assert s['maximum_application_attempts']==1 and not s['automatic_retry'] and len(s['cases'])==1 and s['request'] not in reg['registered_future_requests']
 assert s['limits']['memory_cap_bytes']==4*e.GIB and s['limits']['output_cap_bytes']==128*e.MIB and s['limits']['wall_seconds']==120
 assert len(s['pinned_files'])==95
 pins=[]
 for name,want in s['pinned_files'].items():
  p=Path(name);actual=e.hash_file(p,rate=0);assert actual==want,'pin drift '+name;pins.append({'path':name,'sha256':want,'bytes':p.stat().st_size})
 assert s['pinned_files'][s['binary']]=='d1566bbb07da7252b3924bbf436accc81b1ed8174eb73f614d0316907485393f'
 assert s['pinned_files'][str(A/'core/lib/gcc-11.4.0/cuda-12040/release/libcudart.so')]=='f4c0e5014fe601e624c9b7e7131ea4a65a4459c0d3987b26ee673f75e28d106c'
 case=next(iter(s['cases'].values()));assert case['expected_total_sim_active_lane_uop_instances']==total and case['ctas']==2 and case['warps']==4
 campaign=sum(reg['registered_future_requests'].get(k,{}).get('consumed',0) for k in s['campaign']['request_ids']);assert campaign==4 and s['campaign']['application_attempt_ceiling']==8
 helptext=(B/'control/ELF_HELP_R2.log').read_text();assert 'usage' in helptext.lower() or 'option' in helptext.lower();assert 'gpu_tot_sim_insn' not in helptext
 approval={'schema':'EP_MAIN_PARENT_NATIVE_R3_EXACT_REVIEW_V1','approved_for_registration':True,'request':s['request'],'spec_sha256':specsha,'native_qualification_sha256':qsha,'entry_sha256':e.hash_file(B/'ada_runtime.py',rate=0),'one_exact_application_attempt':True,'maximum_application_attempts':1,'automatic_retry':False,'campaign_consumed_before_registration':4,'campaign_ceiling':8,'failed_attempts_never_refunded':True,'resource_admission_before':before,'pins_checked_independently':pins,'reviewed_semantics':['Original full64 PC chain and old failed CALL candidate preserved','Explicit whole-warp older-issued-instruction and store-ack drain; zero-mask no drain and no CTA barrier alias; conservative serialization, no hardware timing equivalence','Actual compute70 PTX JIT loaded89 cubin bound by full SHA and actual instruction metadata; single measured module scope only','First actual issue and post-simulation explicit host SIGSTOP checkpoints; sampled maps/new path hash with exact PID/startticks; no all-transient-DSO claim','Only recursively observed main-thread children lists; not all TID/orphan coverage','Mapped-file read/hash disappearance fails closed; actual process exit resource-read races handled without inventing failed app','Native epoch2 shared authority lock/CAS and fresh exact budget before fork; no direct ELF execution and no original runtime or old scientific ledger modification'],'expected_total_active_lane_uops':total,'post_run_required':'Independent source trace/control/counter/actual maps join; exit0 alone grants no semantic PASS. Archive full SHA and independent native readback before retiring write reservation','scientific_or_hardware_performance_qualification':False,'observed_unix':time.time()}
 p=B/'control/PARENT_APPROVED_FOR_REGISTRATION.json';assert not p.exists()
 with p.open('x')as f:json.dump(approval,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 results.append({'request':s['request'],'root':str(B),'approval_sha256':e.hash_file(p,rate=0),'spec_sha256':specsha,'qualification_sha256':qsha,'case':next(iter(s['cases']))})
proof={'status':'PARENT_APPROVED_TWO_R3_EXACT_NATIVE_CASES_NOT_YET_REGISTERED_OR_CONSUMED','cases':results,'campaign_before':4,'maximum_after_two':6,'campaign_ceiling':8,'prior_V1_R2_unregistered_candidates_preserved':True,'observed_unix':time.time()}
(R/'control/ADA_STAGE4_R3_PARENT_PRELAUNCH_REVIEW.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof))
