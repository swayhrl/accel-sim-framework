from pathlib import Path
import json,hashlib,datetime
O=Path(__file__).parent
A=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1')
B=A/'agents/B/cpu_shared_timeslice_entry_v1';R=Path('/root/data/dtc_l2_mlp_exploration_20261027_v1')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def put(n,v):
 b=(json.dumps(v,indent=2,sort_keys=True)+'\n').encode()
 with(O/n).open('xb')as f:f.write(b)
 return hashlib.sha256(b).hexdigest()
expected={'resource_extra':'b89910928efdd77f4686700362913fd241e12ab2256e517f1887fc8986b8fa47','observation_extra':'1766aefbaf4710b876e0ed97a46bcfb91434a9f333e0a985b01864f592d1437b','consumer':'c24cfaa663348ea98a5f1f8cd179ef8fcb0845031ba1a0651b4e3eac29d7ea1f','resource_library':'cb6f6d4c6d49e1ad944fead5fd02034ec8b159c59793540dcd9ae16ebc6394e7','producer':'6d3d72e132d7c7fa65b103b4e90e685665bd4bcc2dc0ccc405878a0495ce55c6','frontend':'f043a21f4e087f921bb23e1cb26181acde31d85f2bb8bc496dbac3474c07f45b','entry':'3c40691efc8057fa6da13f9d7cb881cf89a3ad0b146b33c024b4aa462af73f3a'}
paths={'resource_extra':O/'resource_extra_strict.py','observation_extra':O/'bpf_extra_strict.py','consumer':O/'consumer_bridge.py','resource_library':A/'agents/A/cpu_shared_timeslice_v1/cpu_shared.py','producer':B/'strace_entry.py','frontend':B/'bpf_frontend.py','entry':B/'native-entry/bin/experiment'}
for k,p in paths.items():assert sha(p)==expected[k],(k,sha(p))
qa=read(O/'CPU_PREFIX_CONSUMER_QUALIFICATION.json');assert qa['status']=='PASS'and qa['count']==24
for k in paths:assert qa['sources'][k]==expected[k]
assert qa['driver_sha256']==sha(O/'qualify_shared_consumer.py')
put('INTERFACE.json',{'schema':'CPU_SHARED_EXACT1_STRICT_CONSUMER_INTERFACE_V1','status':'FROZEN_CPU_QUALIFIED_NOT_ACTUAL_CANARY_ACCEPTANCE','source_sha256':expected,
 'initial_cohort':'E2-DTCL2MLP-731af5428c4b8155-DH-P0-OBSCTRL-V1','observation_mode':'DEFAULT_CONTROL','reference_cycles':8551,
 'resource_ID':'CPU_SHARED_TIMESLICE_FUTURE_MEMORY_095_V1','resource_binding':'additional_cpu_shared_timeslice_binding','resource_snapshot':'CPU_SHARED_TIMESLICE_SNAPSHOT.json','resource_strict_field':'additional_cpu_shared_timeslice_strict','resource_status':'PASS_CPU_SHARED_TIMESLICE_IO_AND_ORIGINAL_PERFORMANCE','observation_ID':'DTC_STRACE_SHARED_CPU_OBSERVATION_V1',
 'APIs':{'resource.terminal':'(c,base_proof,root=None,authority=None,readonly=False)','observation.normalize_contract':'(document4d7,root,source_sha256,qualification_only=False)','observation.terminal':'(c,physics_plus_shared_IO_proof,root,contract,authority,readonly=False)','observation.verify_archive':'(c,original_full_archive,root,contract)','consumer.install_on_frame':'(frame,observation_cfg_path,exclusion_contract_path,exclusion_contract_SHA,owner_assert,main=None,qualification_loader_sha256=None)','consumer.consumer_check':'(frame,cfg)','consumer.restore_in_owner':'(owner_assert,main=None)'},
 'markers':{'consumer':'DTC_STRACE_CPU_SHARED_PRIVATE_CONSUMER_V1','Bdispatcher':'DTC_STRACE_CPU_SHARED_DISPATCH_V1'},
 'actual_first_point_required':'Natural full original physics/progress/resource-cadence+new Shared/IO/observation/reference8551 strict+true164/native restoration. CPU fixtures cannot qualify these real outcomes.',
 'known_nonselected_V2_engineer_readiness_limit':'Exact old safe/worker delegation retained, but oldV2 consumer_check wrapper-identity may HOLD the remaining3 while Shared outer is installed. InitialC new checker is unaffected; no old guard silently changed.',
 'future_four_gate':'Requires explicit versioned captured-generation dispatch and four actual accepted points; oldV3 gate unchanged and initial1 cannot self-promote.',
 'new_grants':0,'models_started':0,'production_changes':0,'statistics_union_authorized':False})
C='E2-DTCL2MLP-731af5428c4b8155-DH-P0-OBSCTRL-V1'
put('ACTUAL_CANARY_STATUS_READONLY.json',{'UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'cohort':C,'actual_INTENT_file_exists':(R/'control/qualification_ledger'/(C+'.INTENT.json')).exists(),'actual_RESULT_file_exists':(R/'analysis'/(C+'.RESULT.json')).exists(),'actual_canary_qualified_by_this_package':False,'evidence_scope':'File-existence read only, not authoritative unused proof. Main must freshly check current authority/claims before installation.'})
names=['resource_extra_strict.py','bpf_extra_strict.py','consumer_bridge.py','build_observation_extra.py','build_consumer.py','qualify_shared_consumer.py','CPU_PREFIX_CONSUMER_QUALIFICATION.json','README.md','INTERFACE.json','ACTUAL_CANARY_STATUS_READONLY.json','freeze_package.py']
h=put('MANIFEST.json',{'schema':'CPU_SHARED_EXACT1_E_STRICT_CONSUMER_MANIFEST_V1','status':'FROZEN_CPU_QUALIFIED_NO_ACTUAL_CANARY_PASS','files':[{'path':n,'sha256':sha(O/n),'bytes':(O/n).stat().st_size}for n in names],'QA_sha256':sha(O/'CPU_PREFIX_CONSUMER_QUALIFICATION.json'),'actual_models_qualified':False,'production_changes':0,'models_started':0,'new_grants':0})
print(json.dumps({'manifest_sha256':h,'QA_sha256':sha(O/'CPU_PREFIX_CONSUMER_QUALIFICATION.json'),'sources':expected}))
