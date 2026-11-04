from pathlib import Path
import hashlib,json,ast
A=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_perf_first_parallel_exploration_20261104_v1');O=A/'agents/A_runtime_resource_policy_v1';O.mkdir(parents=True,exist_ok=True)
p=Path('/root/data/dtc_stage_iia_remaining48_20261104_v1/tools/stage2_resources.py');source=p.read_text();parentsha=hashlib.sha256(p.read_bytes()).hexdigest()
source=source.replace('Remaining48-only resource admission.','Performance-first phys768 first4-only resource admission.')
source=source.replace("R=P('/root/data/dtc_stage_iia_remaining48_20261104_v1');REQ='DTC_STAGE_IIA_REMAINING48_CH_MATCH_20261104_V1'","R=P('/root/data/dtc_perf_first_parallel_exploration_20261104_v1');REQ='DTC_PERF_FIRST_PHYS768_FIRST4_20261104_V1'\nREMAINING48=P('/root/data/dtc_stage_iia_remaining48_20261104_v1');REMAINING48_REQ='DTC_STAGE_IIA_REMAINING48_CH_MATCH_20261104_V1'")
source=source.replace("ARCHIVE=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_stage_iia_remaining48_execution_20261104_v1')","ARCHIVE=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_perf_first_parallel_exploration_20261104_v1')\nOLD_PROVIDER=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_stage_iia_remaining48_execution_20261104_v1/agents/B_runtime_analysis_v1/snapshot_runner_v1/PUBLICATION_PROVIDER.json')\nPROTECTED_CPUS=set([2,258])|set(range(32,64))|set(range(288,320))")
source=source.replace('DTC_STAGE_IIA_REMAINING48_DYNAMIC_RESOURCE_POLICY_V1','DTC_PERF_FIRST_PHYS768_FIRST4_DYNAMIC_RESOURCE_POLICY_V1').replace('DTC_STAGE_IIA_REMAINING48_DYNAMIC_RESOURCES_V1','DTC_PERF_FIRST_PHYS768_FIRST4_DYNAMIC_RESOURCES_V1')
source=source.replace('remaining48_private_pure_resource','perf_first_private_pure_resource').replace('remaining48_readonly_r20_peer','perf_first_readonly_r20_peer')
source=source.replace('def sample_system():','def _base_sample_system():',1)
source=source.replace('math.ceil(recent*1.20)+128*M','math.ceil(recent*1.20)+384*M').replace('math.ceil(peak*1.20)+128*M','math.ceil(peak*1.20)+384*M')
source=source.replace("for request in [STAGE1_REQ,FIRST16_REQ,REQ]","for request in [STAGE1_REQ,FIRST16_REQ,REMAINING48_REQ,REQ]")
source=source.replace("peer.resources({'request':peer.ORIG,'cohort':'REMAINING48_READONLY_PEER_ACCOUNTING'}","peer.resources({'request':peer.ORIG,'cohort':'PERF_FIRST_READONLY_PEER_ACCOUNTING'}")
source=source.replace("q['budget']==len(q['admitted_specs'])==48","q['budget']==len(q['admitted_specs'])==4")
source=source.replace("and spec['cohort'].startswith('E2-DTC2A48-')","and sha(R/'control/specs'/(spec['cohort']+'.json'))==q['admitted_specs'][spec['cohort']]")
source=source.replace("FIRST16_REQ:_closed_first16(peer,reg)}","FIRST16_REQ:_closed_first16(peer,reg),REMAINING48_REQ:_closed_remaining48(peer,reg)}")
# Scientific pause is admission-only; actual-runtime RAM/disk remains safe for already started models.
needle="decision=_pure().memory_admission(s,total,prev,p)"
source=source.replace(needle,needle+"\n old_gate=old_completion_gate(s,p)\n if old_gate['pause_new']:decision=dict(decision,pass_admission=False,pressure_pause_new=True,pressure_reasons=decision['pressure_reasons']+old_gate['reasons'])")
source=source.replace("runtime_pressure_does_not_terminate_healthy_model=True,","runtime_pressure_does_not_terminate_healthy_model=True,old_remaining48_completion_gate=old_gate,protected_cpu_policy=s.get('protected_cpu_policy'),")
source+='''

def _closed_remaining48(peer,reg):
 q=reg['registered_future_requests'][REMAINING48_REQ];claims=peer.claims(REMAINING48)
 d=_dynamic(peer,REMAINING48,q,claims,256*M)
 exact=(q['budget']==len(q['consumed'])==48 and q['remaining']==0 and set(claims)<=set(q['consumed']) and d['exact_archived_nonlive_count']==48 and not d['writes'])
 if exact:
  d=dict(d,projected_write_bytes=0,actual_unarchived_output_bytes=0,additional_RAM_bytes=0,projection_within_registered_ceiling=True,closed_remaining48_zero_future_metadata=True,closed_join_basis='48exactDONE_EXIT_INTENT_registry_archive_joins_and_nonlive_generation;existing_files_remain_in_df')
 return d

def _old_completion_status():
 """Official publication metadata only, no simulator/raw input or final-analysis chain."""
 try:
  data=OLD_PROVIDER.read_bytes();v=json.loads(data)
  assert v['request']==REMAINING48_REQ and v['source_qualified'] is True
  assert sha(v['manifest']['path'])==v['manifest']['sha256']
  terminal=v['all_registered48_terminal_verified']
  assert type(terminal)is bool and terminal==v['summary']['all_registered48_terminal_verified']
  return dict(verified=True,all_terminal=terminal,provider_sha256=hashlib.sha256(data).hexdigest(),manifest_sha256=v['manifest']['sha256'],observed_utc=v['observed_utc'])
 except(OSError,ValueError,KeyError,AssertionError,TypeError)as e:
  return dict(verified=False,all_terminal=None,error=type(e).__name__+':'+str(e))

def old_completion_gate(s,p):
 old=s.get('old_remaining48_completion',{})
 if not old.get('verified'):return dict(pause_new=True,reasons=['OLD_FINAL_COMPLETION_STATUS_UNVERIFIED'],old=old)
 if not old['all_terminal']:return dict(pause_new=False,reasons=[],old=old)
 release=p.get('old_final_review_release')
 allowed=isinstance(release,dict)and release.get('approved')is True and release.get('request')==REQ and release.get('old_request')==REMAINING48_REQ and release.get('old_terminal_manifest_sha256')==old['manifest_sha256']
 return dict(pause_new=not allowed,reasons=[]if allowed else['OLD_REMAINING48_ALL_TERMINAL_FINAL_REVIEW_PAUSE_NEW'],old=old,explicit_Root_review_release_matched=allowed)

def _siblings(c):
 try:
  out=set()
  for part in (P('/sys/devices/system/cpu')/('cpu'+str(c))/'topology/thread_siblings_list').read_text().strip().split(','):
   if '-'in part:a,b=map(int,part.split('-'));out.update(range(a,b+1))
   else:out.add(int(part))
  return out
 except(OSError,ValueError):return {c}

def sample_system():
 s=_base_sample_system();excluded=set(PROTECTED_CPUS)
 for row in s.get('observed_models',[]):
  for c in row.get('cpus',[]):excluded.update(_siblings(c))
 s['cpu_allowed']=[c for c in s['cpu_allowed']if c not in excluded]
 s['protected_cpu_policy']=dict(always_excluded=sorted(PROTECTED_CPUS),actual_model_and_SMT_excluded=sorted(excluded-PROTECTED_CPUS),remaining_allowed_n=len(s['cpu_allowed']),signals_or_affinity_changes=0)
 s['old_remaining48_completion']=_old_completion_status()
 return s
'''
ast.parse(source);q=O/'perf_first_resources.py';q.write_text(source)
(O/'SOURCE_DERIVATION.json').write_text(json.dumps(dict(parent_path=str(p),parent_sha256=parentsha,own_path=str(q),own_sha256=hashlib.sha256(q.read_bytes()).hexdigest(),method='private copy plus explicit newREQ/newR/newArchive/newbudget4/oldR2peer/protectedCPU/admissiononlyoldcompletiongate; pinned PURE and PEER source privately imported, old files/globals not mutated'),indent=2)+'\n')
print('SOURCE',q,hashlib.sha256(q.read_bytes()).hexdigest())
