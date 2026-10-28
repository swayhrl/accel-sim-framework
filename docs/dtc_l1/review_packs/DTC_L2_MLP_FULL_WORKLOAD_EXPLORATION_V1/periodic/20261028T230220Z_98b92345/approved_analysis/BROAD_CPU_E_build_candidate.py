"""Build separate broad SharedCPU candidates from frozen qualified preimages."""
import pathlib,hashlib
P=pathlib.Path;D=P(__file__).parent;E=D.parent
def replace(text,old,new):
 assert old in text,old[:120]
 return text.replace(old,new)
s=(E/'cpu_shared_timeslice_stage2_v1/resource_extra_strict.py').read_text()
s=replace(s,"ID='CPU_SHARED_TIMESLICE_FUTURE_MEMORY_095_V1'","ID='CPU_SHARED_DYNAMIC_FUTURE_MEMORY_095_V1'")
s=replace(s,"STATUS='PASS_CPU_SHARED_TIMESLICE_IO_AND_ORIGINAL_PERFORMANCE'","STATUS='PASS_CPU_SHARED_DYNAMIC_IO_AND_ORIGINAL_PERFORMANCE'")
s=replace(s,"DESIGN_SHA='02e9050b76f695c21d72a73bff636a415f8fe45c6a7f543874108241ae22905d'","DESIGN_SHA='a8c7446a0edaeb166402400f6a8efbf558e54aac690d26dccfda5bbc63a3edc9'")
s=replace(s,"assert b['mode']==snap['mode']=='CPU_SHARED_TIMESLICE_PER_COHORT'and cfg['max_shared_running']==1,'Explicit single shared slot'","assert b['mode']==snap['mode']=='CPU_SHARED_DYNAMIC_PER_COHORT'and cfg['max_shared_running']is None,'Explicit dynamic shared reservation generation'")
start=s.index(" design=json.loads(snap['design_contract_utf8'])")
end=s.index(" canonical_path=",start)
s=s[:start]+''' design=json.loads(snap['design_contract_utf8']);assert design['resource_id']==ID and design['schema']=='CPU_SHARED_DYNAMIC_RESOURCE_CONTRACT_V1'
 assert cfg['qualification_stage']=='AFTER_REAL_ENGINEERING4_GATE'and cfg['max_shared_running']is None,'Broad dynamic scope only'
 first=snap['fresh_preflights'][0]
 fields=['broad_approval_utf8','broad_gate_utf8','broad_source_artifacts_utf8','scope_contract_utf8']
 for field in fields:assert snap[field]==first[field],'Resource top/proof broad prerequisite mismatch'
 certificate=lib.validate_broad_approval(cfg,authority,first['broad_approval_utf8'],first['broad_gate_utf8'],first['broad_source_artifacts_utf8'],first['scope_contract_utf8'])
 assert c in cfg['allowed_cohorts']
 for p in snap['fresh_preflights']:
  for field in fields:assert p[field]==first[field],'Broad prerequisite witnesses differ'
''' +s[end:]
s=replace(s,"'single_slot_qualified'","'dynamic_concurrency_qualified'")
(D/'resource_extra_strict.py').write_text(s)

s=(E/'strace_bpf_future_strict_consumer_v3/bpf_extra_strict.py').read_text()
s=s[:s.index('# Included verbatim into new bpf_extra_strict.py')]
s=replace(s,"ID='DTC_STRACE_FUTURE_ENTRY_V3'","ID='DTC_STRACE_BROAD_SHARED_CPU_V1'")
s=replace(s,"canary4_prerequisite_sha256=cfg['canary4_prerequisite_sha256'])","canary4_prerequisite_sha256=cfg['canary4_prerequisite_sha256'],resource_configuration_sha256=cfg['resource_configuration_sha256'])")
s=replace(s,"expected_status='PASS_BPF_REQUIRED_ACTIVE'if mode=='BPF_REQUIRED'else'PASS_DEFAULT_CONTROL_NO_BPF'","require(mode=='BPF_REQUIRED','Broad scope is BPF only')\n expected_status='PASS_BROAD_SHARED_BPF_REQUIRED_ACTIVE'")
s=replace(s," verify_release_prerequisite(cfg,authority)"," verify_release_prerequisite(cfg,authority,resource_configuration_utf8=snap['resource_configuration_utf8'],resource_snapshot=read(out/'CPU_SHARED_TIMESLICE_SNAPSHOT.json'))")
start=s.index(" memory=json.loads(snap['memory_configuration_utf8'])")
end=s.index(" if rule['scientific_role']",start)
s=s[:start]+''' memory=json.loads(snap['memory_configuration_utf8']);captured_memory=read(out/'CPU_SHARED_TIMESLICE_SNAPSHOT.json')['config']
 require(snap['memory_configuration_utf8']==snap['resource_configuration_utf8'],'Broad typed memory/resource scope differs')
 require(memory==captured_memory and c in memory['allowed_cohorts'],'Captured broad resource generation differs')
 require(utfsha(snap['resource_configuration_utf8'])==cfg['resource_configuration_sha256'],'Broad resource configuration binding')
''' +s[end:]
s=replace(s,"require(base_proof.get('additional_cpu_spare_memory_admission_strict',{}).get('status')=='PASS_CPU_SPARE_MEMORY_IO_AND_ORIGINAL_PERFORMANCE','CPU2 strict mandatory')","require('additional_cpu_spare_memory_admission_strict'not in base_proof,'Broad Shared cannot claim CPU2 PASS')\n require(base_proof.get('additional_cpu_shared_timeslice_strict',{}).get('schema')=='CPU_SHARED_DYNAMIC_FUTURE_MEMORY_095_V1'and base_proof['additional_cpu_shared_timeslice_strict'].get('status')=='PASS_CPU_SHARED_DYNAMIC_IO_AND_ORIGINAL_PERFORMANCE','Dynamic Shared strict mandatory')")
s=replace(s,"status='PASS_STRACE_V3_AND_ORIGINAL_CPU2_IO'","status='PASS_BROAD_SHARED_BPF_AND_ORIGINAL_IO'")
s=replace(s,"CPU2_strict_required=True,IO_strict_required=True","CPU2_strict_required=False,old_CPU2_PASS_claimed=False,dynamic_shared_strict_required=True,IO_strict_required=True")
s=replace(s,"'NATIVE_EXIT.json','L2_STRICT.json']","'NATIVE_EXIT.json','L2_STRICT.json','CPU_SHARED_TIMESLICE_SNAPSHOT.json','CPU_SHARED_TIMESLICE_EXTRA_STRICT.json','SHARED_JSON_IO_SNAPSHOT.json','SHARED_JSON_IO_EXTRA_STRICT.json']")
s+='\n'+(D/'release_prerequisite.py').read_text()
(D/'bpf_extra_strict.py').write_text(s)

s=(E/'strace_bpf_future_strict_consumer_v3/consumer_bridge.py').read_text()
s=replace(s,"ID='DTC_STRACE_FUTURE_ENTRY_V3'","ID='DTC_STRACE_BROAD_SHARED_CPU_V1'")
s=replace(s,"V2_CONSUMER_SHA='5c4ded4df0dee860015208b0af46d967e91a0bb2a2fc98e6830ed7b54db6ae9f'","V2_CONSUMER_SHA='2e548a181f28535043bdd5ed885ab2d554ca6462a2e8e690f6e400a36d8fc1c7'")
s=replace(s,"MARKER='DTC_STRACE_BPF_PRIVATE_CONSUMER_V3';B_OWNER_MARKER='DTC_STRACE_FUTURE_DISPATCH_V3'","MARKER='DTC_STRACE_BROAD_SHARED_PRIVATE_CONSUMER_V1';B_OWNER_MARKER='DTC_STRACE_BROAD_SHARED_DISPATCH_V1'")
s=replace(s,"require(proof.get('additional_cpu_spare_memory_admission_strict',{}).get('status')=='PASS_CPU_SPARE_MEMORY_IO_AND_ORIGINAL_PERFORMANCE','CPU2 strict mandatory')","require('additional_cpu_spare_memory_admission_strict'not in proof,'Dynamic Shared cannot claim CPU2 strict PASS')\n require(proof.get('additional_cpu_shared_timeslice_strict',{}).get('schema')=='CPU_SHARED_DYNAMIC_FUTURE_MEMORY_095_V1'and proof['additional_cpu_shared_timeslice_strict'].get('status')=='PASS_CPU_SHARED_DYNAMIC_IO_AND_ORIGINAL_PERFORMANCE','Dynamic Shared strict mandatory')")
s=replace(s,"Current V2 outer safe route must be preserved","Current Stage2 outer safe route must be preserved")
needle=" def result_path(c):"
at=s.index(needle)
s=s[:at]+''' if qualification:physics_load=oldload
 else:
  pristine=load('broad_pristine_original_consumer',consumer.__file__);require(sha(pristine.__file__)==ORIGINAL_CONSUMER_SHA,'Original physics source');physics_load=pristine.load
 def whole_proof(c,readonly=False):
  base=physics_load('broad_original_whole_physics','l2_strict.py').terminal(c)
  require(base.get('performance_accepted')is True,'Original physics mandatory')
  intent=read(root/'control/qualification_ledger'/(c+'.INTENT.json'));out=P(intent['output']);binding=intent['additional_cpu_shared_timeslice_binding'];snapshot=out/'CPU_SHARED_TIMESLICE_SNAPSHOT.json'
  require(binding['schema']=='CPU_SHARED_DYNAMIC_FUTURE_MEMORY_095_V1'and sha(snapshot)==binding['snapshot_sha256'],'Dynamic resource snapshot binding')
  captured=read(snapshot)['config'];source=captured['source_paths']['extra_strict']
  require(captured['qualified_sources']['consumer']==sha(__file__)and sha(source)==captured['qualified_sources']['extra_strict'],'Captured broad resource source')
  return mandatory_old(load('broad_INTENT_bound_resource_extra',source).terminal(c,base,root=root,authority=authority_provider(),readonly=readonly))
''' +s[at:]
s=replace(s,'control/strace_bpf_v3_route_claims','control/broad_shared_cpu_route_claims')
s=replace(s,'STRACE_BPF_V3_FUTURE_ROUTE_CLAIM_V1','BROAD_SHARED_CPU_FUTURE_ROUTE_CLAIM_V1')
s=replace(s,"if binding.get('schema')=='DTC_STRACE_FUTURE_ENTRY_V2':return False","if binding.get('schema')in ['DTC_STRACE_FUTURE_ENTRY_V2','DTC_STRACE_FUTURE_ENTRY_V3','DTC_STRACE_SHARED_CPU_OBSERVATION_V1']:return False")
s=replace(s,"if snapshot.get('schema')!='DTC_STRACE_FUTURE_ENTRY_V2':raise ObservationHold('Unknown snapshot generation')","if snapshot.get('schema')not in ['DTC_STRACE_FUTURE_ENTRY_V2','DTC_STRACE_FUTURE_ENTRY_V3','DTC_STRACE_SHARED_CPU_OBSERVATION_V1']:raise ObservationHold('Unknown snapshot generation')")
s=replace(s,"for key in ['additional_cpu_spare_memory_admission_strict',EXTRA]:","for key in ['additional_cpu_shared_timeslice_strict',EXTRA]:")
s=replace(s,"proof=mandatory_old(oldload('v3_original_readonly_strict','l2_strict.py').terminal(c))","proof=whole_proof(c,readonly=True)")
s=replace(s,"module=oldload(name,file)","module=physics_load(name,file)if P(file).name=='l2_strict.py'else oldload(name,file)")
s=replace(s,"value=observation.terminal(c,mandatory_old(previous(c)),root,historical,authority_provider(),readonly=False)","value=observation.terminal(c,whole_proof(c,readonly=False),root,historical,authority_provider(),readonly=False)")
s=replace(s,'STRACE_V3_OBSERVATION_HOLD_PRESERVE','BROAD_SHARED_OBSERVATION_HOLD_PRESERVE')
s=replace(s,'analysis/observation_v3_holds','analysis/broad_shared_observation_holds')
s=replace(s,'V3_PRIVATE_CONSUMER_SAFE_ROUTE_INSTALLED','BROAD_SHARED_PRIVATE_CONSUMER_SAFE_ROUTE_INSTALLED')
s=replace(s,"  for c in q['consumed']:\n   rp=m['bridge']['result_path'](c)\n   require(not m['bridge']['selected'](c)or(rp.exists()and m['consumer'].accepted(read(rp))and read(rp)['proof'].get(EXTRA,{}).get('schema')==ID),'Cannot remove mandatory route from unresolved spent identity')",'''  for c in q['consumed']:
   if not m['bridge']['selected'](c):continue
   rp=m['bridge']['result_path'](c);require(rp.exists(),'Preserve mandatory broad route from unresolved spent identity')
   value=read(rp);proof=value['proof'];intent=read(P(m['cfg']['root'])/'control/qualification_ledger'/(c+'.INTENT.json'));out=P(intent['output'])
   require(m['consumer'].accepted(value)and value['uuid']==proof['uuid']==intent['uuid']==q['consumed'][c]['uuid'],'Restore requires accepted same-UUID performance')
   require(proof.get(EXTRA,{}).get('schema')==ID and proof[EXTRA]['status']=='PASS_BROAD_SHARED_BPF_AND_ORIGINAL_IO','Restore observation generation')
   require(proof.get('additional_cpu_shared_timeslice_strict',{}).get('schema')=='CPU_SHARED_DYNAMIC_FUTURE_MEMORY_095_V1','Restore resource generation')
   require(intent[FIELD]['qualified_sources']==m['cfg']['qualified_sources'],'Restore captured source generation differs')
   for key in [EXTRA,'additional_cpu_shared_timeslice_strict']:
    side=proof[key];require(P(side['sidecar_path']).parent==out and sha(side['sidecar_path'])==side['sidecar_sha256'],'Restore strict sidecar missing/changed')
   require(value['archive'].get('additional_strace_bpf_archive_verification',{}).get('status')=='PASS_NEW_OBSERVATION_ARCHIVED_AND_NATIVE_RESTORED','Restore full archive/native closure')''')
(D/'consumer_bridge.py').write_text(s)
print('Built three isolated broad candidates')
