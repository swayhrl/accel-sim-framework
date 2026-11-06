from pathlib import Path
import tempfile,json,hashlib,types,shutil,copy,time
A=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_controlled_oracle_implementation_execution_20261106_v1/agents/P_resource_peer_adapter_v1/v5_cpu_draft_peer');path=A/'oracle_peer_disk_adapter_v5.py';m=types.ModuleType('p_cpu_draft_peer_fixture');m.__file__=str(path);exec(compile(path.read_bytes(),str(path),'exec'),m.__dict__)
source=Path('/root/data/dtc_controlled_oracle_20261106_v1');base=Path(tempfile.mkdtemp(prefix='dtc_oracle_cpu_mixed_actual_metadata_',dir='/root/data'));pins=[]
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2)+'\n')
def cp(sp,dp):
 b=sp.read_bytes();dp.parent.mkdir(parents=True,exist_ok=True);dp.write_bytes(b);pins.append({'source':str(sp),'source_sha256':hashlib.sha256(b).hexdigest(),'CPU_copy':str(dp),'bytes':len(b)})
def hold(f,needle):
 try:f();raise AssertionError('EXPECTED_HOLD_NOT_RAISED:'+needle)
 except RuntimeError as e:assert needle in str(e),(needle,str(e))
try:
 for stage in ['initial8','remaining24']:
  sr=source/stage;dr=base/stage
  for name in ['EXECUTION_PLAN.json','REGISTRY_REQUEST_CANDIDATE.json','REGISTRY_REQUEST_CANDIDATE.DRAFT.json','CPU_DRAFT_BUILD.json','SCIENCE_AUTHORIZATION.json','SCIENCE_AUTHORIZATION.DRAFT.json']:
   if(sr/'control'/name).exists():cp(sr/'control'/name,dr/'control'/name)
  for sp in (sr/'control/specs').glob('*.json'):cp(sp,dr/'control/specs'/sp.name)
  write(dr/'control/POOL_DISPATCH_RESERVATIONS.json',{'claims':{}})
 r1=base/'initial8';r2=base/'remaining24';p1=m.read(r1/'control/EXECUTION_PLAN.json');p2=m.read(r2/'control/EXECUTION_PLAN.json');requests=[p1['request'],p2['request']];roots=dict(zip(requests,map(str,[r1,r2])))
 for root,pl in [(r1,p1),(r2,p2)]:
  pl.update(execution_root=str(root),oracle_request_roots=roots,shared_pool_roots=list(roots.values()),shared_pool_dispatch_reservations_path=str(base/'control/SHARED_POOL_DISPATCH_RESERVATIONS.json'),archive_workers=1);write(root/'control/EXECUTION_PLAN.json',pl)
 (base/'control').mkdir();q1=m.read(r1/'control/REGISTRY_REQUEST_CANDIDATE.json');cohort=p1['initial_qualifiers']['OFF_MATCHED'];spec=m.read(r1/'control/specs'/(cohort+'.json'))
 assert not(r2/'control/REGISTRY_REQUEST_CANDIDATE.json').exists()and not(r2/'control/SCIENCE_AUTHORIZATION.json').exists()
 value=m.admission_disk_reservations(spec,p1);print('ACTUAL_MIXED_METADATA_REPLAY',value['status'],value.get('bounded_runtime_seconds'));assert value['status']=='PASS',value
 assert value['stage_resource_candidate_sources'][requests[1]]['kind']=='EXPLICIT_UNREGISTERED_CPU_DRAFT_PEER_RESOURCE_ONLY'
 assert value['stage_resource_candidate_sources'][requests[1]]['consumption_permitted']is False
 assert value['all_oracle_stage_dynamic_windows'][requests[1]]['live_actual_projection_bytes']==0
 write(A/'CPU_ACTUAL_MIXED_STAGES_PREFLIGHT_SAMPLE.json',value)
 # Negative controls apply only to isolated metadata copies, never production.
 write(r2/'control/SCIENCE_AUTHORIZATION.json',{'CPU_ONLY_NEGATIVE':True});hold(lambda:m._resource_candidate(r2,requests[1],True),'DRAFT_PEER_HAS_NORMAL_SCIENCE_AUTHORIZATION');(r2/'control/SCIENCE_AUTHORIZATION.json').unlink()
 dp=r2/'control/REGISTRY_REQUEST_CANDIDATE.DRAFT.json';original=dp.read_bytes();q=m.read(dp);q['ready_for_registration']=True;write(dp,q);hold(lambda:m._resource_candidate(r2,requests[1],True),'CPU_DRAFT_RESOURCE_METADATA_SHA_DRIFT');dp.write_bytes(original)
 manifest=r2/'control/CPU_DRAFT_BUILD.json';mb=manifest.read_bytes();manifest.unlink();hold(lambda:m._resource_candidate(r2,requests[1],True),'UNREGISTERED_PEER_MISSING_EXPLICIT_CPU_DRAFT_METADATA');manifest.write_bytes(mb)
 hold(lambda:m._resource_candidate(r2,requests[1],False),'CURRENT_REQUEST_REQUIRES_NORMAL_SCIENTIFIC_CANDIDATE')
 q=m.read(dp);c=next(iter(q['admitted_specs']));write(r2/'control/POOL_DISPATCH_RESERVATIONS.json',{'claims':{c:{'CPU_ONLY':True}}});hold(lambda:m._resource_candidate(r2,requests[1],True),'CPU_DRAFT_PEER_HAS_DISPATCH_CLAIMS');write(r2/'control/POOL_DISPATCH_RESERVATIONS.json',{'claims':{}})
 intent=r2/'control/qualification_ledger/CPU_ONLY_NEGATIVE.INTENT.json';write(intent,{'CPU_ONLY':True});hold(lambda:m._resource_candidate(r2,requests[1],True),'CPU_DRAFT_PEER_HAS_ACTUAL_LIFECYCLE_RECORDS');intent.unlink()
 result=r2/'DTC/run/results/CPU_ONLY_NEGATIVE_UUID';result.mkdir(parents=True);hold(lambda:m._resource_candidate(r2,requests[1],True),'CPU_DRAFT_PEER_HAS_ACTUAL_RESULT_UUID_OR_FILES');result.rmdir()
 # A normal finalized candidate retains the original normal path; no DRAFT
 # permission is inferred and no model or actual registry entry is created.
 cp(source/'initial8/control/REGISTRY_REQUEST_CANDIDATE.json',r2/'control/REGISTRY_REQUEST_CANDIDATE.json');normal,kind=m._resource_candidate(r2,requests[1],True);assert kind['kind']=='NORMAL_UNREGISTERED_CANDIDATE';hold(lambda:m._worker(spec,p1),'ORACLE_STAGE_REQUEST_MISMATCH');(r2/'control/REGISTRY_REQUEST_CANDIDATE.json').unlink()
 # This checks source selection only: mismatched normal request is rejected
 # by the unchanged downstream worker q/request and stage-plan checks.
 evidence={'schema':'DTC_ORACLE_CPU_DRAFT_PEER_QUALIFICATION_V5','status':'PASS','checks':{'real_current_initial_final_remaining_draft_metadata_replay':True,'inactive_draft_peer_resource_projection_zero':True,'draft_peer_not_scientific_authority_or_consumption':True,'normal_auth_blocks_draft_fallback':True,'draft_metadata_SHA_drift_blocks_fallback':True,'missing_CPU_DRAFT_manifest_blocks_fallback':True,'current_scientific_request_requires_normal_candidate':True,'draft_peer_claims_block_fallback':True,'draft_peer_actual_INTENT_blocks_fallback':True,'draft_peer_result_UUID_directory_blocks_fallback':True,'normal_candidate_path_remains_original':True,'normal_request_mismatch_rejected_by_worker':True},'real_sample_seconds':value['bounded_runtime_seconds'],'relocated_CPU_only_plan_fields':['execution_root','oracle_request_roots','shared_pool_roots','shared_pool_dispatch_reservations_path'],'copied_actual_metadata_pins':pins,'registry_mutations':0,'science_registration_calls':0,'model_invocations':0,'signals_to_models':0,'CPU_fixture_root_removed':str(base),'module_sha256':m.sha(path)};write(A/'CPU_QUALIFICATION_V5.json',evidence)
 print('DRAFT_SCOPE_SHA_AUTH_CLAIM_NORMAL_PATH_NEGATIVE_CONTROLS_PASS')
finally:
 assert str(base).startswith('/root/data/dtc_oracle_cpu_mixed_actual_metadata_');shutil.rmtree(base)
