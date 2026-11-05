# Included in the separate Stage2 observation source. No work on import.
APPROVAL_PATH=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1/coordinator/CPU_SHARED_ENGINEERING4_SCOPE_EXTENSION_V1/SCOPE_EXTENSION_APPROVAL.json')
APPROVAL_SHA='30bd502f7fe6653907b3e835c2b7aee78c780c65ecde758df473942158d1b895'
OLD_SHARED_RESOURCE_SHA='b89910928efdd77f4686700362913fd241e12ab2256e517f1887fc8986b8fa47'
OLD_SHARED_OBSERVATION_SHA='1766aefbaf4710b876e0ed97a46bcfb91434a9f333e0a985b01864f592d1437b'
OLD_V2_OBSERVATION_SHA='cbbddba1fe954a1e7dd411c89f9feff2480d5314781204b75fc8364159586711'
CPU2_OWNER_SHA='4945156fe11db69f75a6f1dc39e08a0f5c7b28ef43244525f570bebbf33cf080'
ORIGINAL_STRICT_SHA='f889b248adca6f466f8ee19fb2dc17986e355196132c716b7b6fc50ced333b59'
ORIGINAL_OUTBOX_SHA='d4b58b362a39c9d198a40e5c252f6eb07ba780e4707ffd79f6724569e349c4a5'
def pinned_load(path,pin,name):
 require(sha(path)==pin,'Captured source bytes changed '+str(path))
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def validate_stage2_approval(cfg):
 require(cfg['scope_extension_approval_sha256']==APPROVAL_SHA and sha(cfg['scope_extension_approval_path'])==APPROVAL_SHA,'Actual Stage2 approval SHA')
 approval=read(cfg['scope_extension_approval_path'])
 require(approval['schema']=='CPU_SHARED_ACTUAL_CANARY_ENGINEERING4_SCOPE_APPROVAL_V1'and approval['status']=='PASS_CPU_SHARED_NATURAL_STRICT_ARCHIVE_NATIVE_RESTORE','Wrong actual approval')
 require(not approval.get('qualification_only',False)and approval['Main_scope_extension_approved']is True and approval['max_shared_running']==1,'Not an actual finite scope approval')
 require(approval['production_release_scope']=='FINITE_ORIGINAL_FOUR_ENGINEERING_QUALIFICATION_ONLY'and approval['production_primary_rollout_eligible']is False and approval['IR_rollout_eligible']is False and approval['validated_union_authorized']is False,'No broad or union approval')
 artifacts={}
 for key,reference in approval['source_artifacts'].items():
  require(sha(reference['path'])==reference['sha256'],'Actual first source artifact '+key);artifacts[key]=read(reference['path'])
 result,done,full=artifacts['RESULT'],artifacts['DONE'],artifacts['FULL_REPLAY']
 require(result['state']=='PASS_L2MLP_STRICT_ARCHIVE_NATIVE_RESTORE'and result['proof']['performance_accepted']is True,'First actual RESULT not accepted')
 require(result['uuid']==done['uuid']==full['uuid']==approval['uuid']and result['cohort']==done['cohort']==full['cohort']==approval['cohort'],'Actual first UUID/cohort mismatch')
 require(done['stop_reason']is None and done['launcher_wait_returncode']==0,'Actual first not natural')
 require(result['cycles']==result['proof']['cycles']==full['cycles']==approval['cycles']==8551,'Actual first cycles changed')
 for key in ['CTA','instructions','kernel_count']:require(result['proof'][key]==full['counts'][key]==approval['counts'][key],'Actual first counts changed')
 require(full['status']==approval['status']and full['RESULT_sha256']==approval['source_artifacts']['RESULT']['sha256']==approval['first_RESULT_sha256'],'Full actual replay source mismatch')
 archive=result['archive']['receipt'];require(archive['archive_sha256']==approval['first_actual_archive_sha256']and archive['manifest_sha256']==approval['first_actual_archive_manifest_sha256'],'Actual first archive mismatch')
 require(sha(MAIN_EXCLUSION_PATH)==MAIN_EXCLUSION_SHA and set(approval['allowed_cohorts'])==set(read(MAIN_EXCLUSION_PATH)['scope_cohorts']),'Only original engineering four')
 require(approval['modes']=={c:r['mode']for c,r in read(MAIN_EXCLUSION_PATH)['scope_cohorts'].items()},'Original four modes changed')
 return approval
def _historical_contract(extra,cfg,root):
 document=read(MAIN_EXCLUSION_PATH)
 if sha(extra.__file__)==sha(__file__):return extra.normalize_contract(document,root,MAIN_EXCLUSION_SHA,cfg['qualification_only'],cfg=cfg)
 return extra.normalize_contract(document,root,MAIN_EXCLUSION_SHA,cfg['qualification_only'])
def replay_closed_generation(c,authority,root=PRODUCTION_ROOT):
 """Real readonly full-chain replay; choose by immutable INTENT generation.

 No simulator/model starts; CPU fixture roots are not accepted as a real gate.
 """
 root=P(root);require(root==PRODUCTION_ROOT and not authority.get('qualification_only',False),'Real gate needs actual production root/authority')
 require(c in read(MAIN_EXCLUSION_PATH)['scope_cohorts'],'Only four engineering identities')
 rp=root/'analysis'/(c+'.RESULT.json');value=read(rp);require(value['state']=='PASS_L2MLP_STRICT_ARCHIVE_NATIVE_RESTORE'and value['proof']['performance_accepted']is True,'Missing actual accepted performance')
 require(value['primary_statistics_excluded']is True and value['validated_union_authorized']is False and read(root/'analysis/engineering_results'/(c+'.RESULT.json'))==value,'Actual engineering exclusion/mirror')
 ip=root/'control/qualification_ledger'/(c+'.INTENT.json');intent=read(ip);out=P(intent['output']);require(sha(ip)==authority['consumed'][c]['intent_sha256']and intent['uuid']==authority['consumed'][c]['uuid']==value['uuid'],'Actual consumed identity')
 for key in ['additional_cpu_shared_timeslice_strict','additional_cpu_spare_memory_admission_strict','additional_shared_json_io_strict',KEY]:
  if key in value['proof']:
   side=value['proof'][key];require(P(side['sidecar_path']).parent==out and sha(side['sidecar_path'])==side['sidecar_sha256'],'Existing readonly sidecar '+key)
 base=pinned_load(root/'tools/l2_strict.py',ORIGINAL_STRICT_SHA,'mixed_gate_original_physics').terminal(c)
 shared='additional_cpu_shared_timeslice_binding'in intent
 if shared:
  require('additional_cpu_spare_memory_admission_binding'not in intent,'Mixed resource bindings')
  b=intent['additional_cpu_shared_timeslice_binding'];rs=out/'CPU_SHARED_TIMESLICE_SNAPSHOT.json';require(sha(rs)==b['snapshot_sha256'],'Resource snapshot SHA');rcfg=read(rs)['config'];pin=rcfg['qualified_sources']['extra_strict']
  require(pin in [OLD_SHARED_RESOURCE_SHA,STAGE2_RESOURCE_EXTRA_SHA],'Unreviewed Shared source generation')
  resource=pinned_load(rcfg['source_paths']['extra_strict'],pin,'mixed_gate_captured_Shared_extra');proof=resource.terminal(c,base,root=root,authority=authority,readonly=True)
 else:
  require('additional_cpu_spare_memory_admission_binding'in intent,'Only captured Shared or old CPU2 accepted')
  owner=pinned_load(root/'control/operational_amendments/cpu_spare_memory_v2/cpu_owner.py',CPU2_OWNER_SHA,'mixed_gate_old_CPU2_owner');resource=owner.historical_extra(intent,out);proof=resource.terminal(c,base)
 obs_binding=intent[FIELD];obs_path=out/SNAP;require(sha(obs_path)==obs_binding['snapshot_sha256'],'Observation snapshot SHA');ocfg=read(obs_path)['config'];pin=ocfg['qualified_sources']['extra_strict']
 require(pin in [OLD_V2_OBSERVATION_SHA,OLD_SHARED_OBSERVATION_SHA,sha(__file__)],'Unreviewed observation source generation')
 require((pin==OLD_V2_OBSERVATION_SHA)==(not shared),'Observation/resource generation family mismatch')
 observer=pinned_load(ocfg['source_paths']['extra_strict'],pin,'mixed_gate_captured_observation');contract=_historical_contract(observer,ocfg,root)
 observed=observer.terminal(c,proof,root,contract,authority,readonly=True);require(observed==value['proof'],'Historical full strict replay changed')
 original=pinned_load(root/'tools/l2_outbox.py',ORIGINAL_OUTBOX_SHA,'mixed_gate_original_full_archive').verify(c)
 require(original=={k:v for k,v in value['archive'].items()if k!='additional_strace_bpf_archive_verification'},'Original full archive/native replay changed')
 archive=observer.verify_archive(c,original,root,contract);require(archive==value['archive']['additional_strace_bpf_archive_verification'],'Captured observation/native restore changed')
 return dict(cohort=c,uuid=value['uuid'],RESULT_sha256=sha(rp),cycles=value['cycles'],counts={k:value['proof'][k]for k in ['CTA','instructions','kernel_count']},resource_source_sha256=sha(resource.__file__),observation_source_sha256=pin,mode=observed[KEY]['mode'],archive_manifest_sha256=archive['manifest_sha256'],archive_sha256=archive['archive_sha256'],actual_full_chain_replayed=True)
def replay_mixed_four_gate(authority,root=PRODUCTION_ROOT):
 """Return HOLD until all four real chains pass; never accepts fake quorum."""
 rows=[];missing=[]
 for c in sorted(read(MAIN_EXCLUSION_PATH)['scope_cohorts']):
  try:rows.append(replay_closed_generation(c,authority,root))
  except Exception as error:missing.append(dict(cohort=c,error=repr(error)))
 if missing:return dict(status='HOLD_REAL_ENGINEERING_FOUR_INCOMPLETE',accepted_real_count=len(rows),rows=rows,missing=missing,four_point_qualified=False,primary_rollout_eligible=False,models_started=0)
 return dict(status='PASS_REAL_MIXED_GENERATION_ENGINEERING_FOUR_FULL_CHAIN',rows=rows,accepted_real_count=4,four_point_qualified=True,primary_rollout_eligible=False,IR_rollout_eligible=False,validated_union_authorized=False,gate_source_sha256=sha(__file__),models_started=0)
def capture_mixed_four_gate(frame,main,path):
 import os,threading,datetime
 require(threading.current_thread()is threading.main_thread()and os.getpid()==1498278,'Actual Main required')
 require(int(P('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19])==977758783,'Main generation')
 require(frame.f_locals['res'].DTC_LARGE_JOB_AGING_INSTALLED is main.DTC_FUTURE_MEMORY_ADMISSION_095_FLOOR10_V1['aging'],'Actual existing frame')
 engine=frame.f_locals['engine'];engine.assert_parent_lease();value=replay_mixed_four_gate(engine.registered()[2]);require(value['four_point_qualified'],'All four actual full chains required')
 value.update(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),actual_owner_pid=os.getpid(),actual_owner_start_ticks=977758783)
 # Atomically publish a new independent derived gate, no overwrite/no grants.
 import uuid
 path=P(path);temporary=path.with_name('.'+path.name+'.'+uuid.uuid4().hex)
 try:
  with temporary.open('xb')as f:f.write(js(value));f.flush();os.fsync(f.fileno())
  os.link(temporary,path)
  fd=os.open(path.parent,os.O_RDONLY)
  try:os.fsync(fd)
  finally:os.close(fd)
 finally:
  if temporary.exists():temporary.unlink()
 return dict(path=str(path),sha256=sha(path),gate=value)
