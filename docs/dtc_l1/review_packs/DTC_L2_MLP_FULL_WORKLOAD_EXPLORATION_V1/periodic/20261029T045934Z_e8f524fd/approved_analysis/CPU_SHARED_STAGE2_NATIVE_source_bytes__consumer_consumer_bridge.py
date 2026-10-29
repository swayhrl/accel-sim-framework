"""Private per-cohort finisher clone. Import never installs, registers or dispatches."""
import copy,hashlib,importlib.util,json,pathlib,sys,threading,time,types
P=pathlib.Path
PRODUCTION_ROOT=P('/root/data/dtc_l2_mlp_exploration_20261027_v1')
ORIGINAL_CONSUMER_SHA='6cc6cc30a71740df951327414d094953effb73a406e7036358ad0b702ebb0403'
CPU2_OWNER_SHA='4945156fe11db69f75a6f1dc39e08a0f5c7b28ef43244525f570bebbf33cf080'
FIELD='additional_strace_bpf_observation_binding'
EXTRA='additional_strace_bpf_observation_strict'
MARKER='DTC_STRACE_CPU_SHARED_PRIVATE_CONSUMER_V1'
B_OWNER_MARKER='DTC_STRACE_CPU_SHARED_DISPATCH_V1'
class ObservationHold(RuntimeError):pass
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def read(p):return json.loads(P(p).read_bytes())
def require(v,message):
 if not v:raise ObservationHold(message)
def mandatory_old(proof):
 require(proof.get('performance_accepted')is True and type(proof.get('cycles'))is int and proof['cycles']>0,'Original complete performance strict mandatory')
 cpu=proof.get('additional_cpu_spare_memory_admission_strict',{})
 require('additional_cpu_spare_memory_admission_strict'not in proof,'Shared branch cannot claim old CPU2 strict PASS')
 require(proof.get('additional_cpu_shared_timeslice_strict',{}).get('status')=='PASS_CPU_SHARED_TIMESLICE_IO_AND_ORIGINAL_PERFORMANCE','Actual SharedCPU strict mandatory')
 require('additional_shared_json_io_strict'in proof or'additional_future_memory_io_strict'in proof,'Original IO strict mandatory')
 return proof
def make_private_consumer(consumer,scope_contract,observation,authority_provider):
 """Return new functions; never assign to consumer or its load/put globals.

 scope_contract.cohorts is Main's registered exact engineer exclusion contract,
 not a fallback role. Only these entries produce engineering_results records.
 """
 contract=copy.deepcopy(scope_contract);root=P(contract['root']);cohorts=contract['cohorts']
 require(sha(consumer.__file__)==ORIGINAL_CONSUMER_SHA,'Original consumer source drift')
 require(cohorts and contract['primary_statistics_excluded']is True and contract['validated_union_authorized']is False,'Explicit Main exclusion contract required')
 oldfinish=consumer.finish_evidence;oldsafe=consumer.safe_finish;oldload=consumer.load;oldput=consumer.put;oldarchive=consumer.archive_closed
 require(P(oldfinish.__code__.co_filename)==P(consumer.__file__),'Unknown consumer finisher')
 loader_sha=sha(oldload.__code__.co_filename)
 q=authority_provider()
 qualification=contract.get('qualification_only')is True and q.get('qualification_only')is True
 require(root==PRODUCTION_ROOT or qualification,'Private fixture root requires both qualification flags')
 require(loader_sha==CPU2_OWNER_SHA or(qualification and loader_sha==contract.get('qualification_loader_sha256')),'Current qualified CPU2 loader mandatory')
 # Shared INTENT is not a CPU2 generation. The new selected branch loads the
 # pristine original physics verifier; only nonselected delegates oldload.
 if qualification:physics_load=oldload
 else:
  pristine=_load('shared_pristine_original_consumer',consumer.__file__);require(sha(pristine.__file__)==ORIGINAL_CONSUMER_SHA,'Original physics loader source');physics_load=pristine.load
 def historical_shared(c):
  intent=read(root/'control/qualification_ledger'/(c+'.INTENT.json'));out=P(intent['output']);b=intent['additional_cpu_shared_timeslice_binding']
  path=out/'CPU_SHARED_TIMESLICE_SNAPSHOT.json';require(sha(path)==b['snapshot_sha256'],'Shared captured snapshot')
  captured=read(path)['config'];source=captured['source_paths']['extra_strict'];require(sha(source)==captured['qualified_sources']['extra_strict'],'Shared resource extra source')
  return _load('shared_captured_resource_extra',source)
 def whole_proof(c,readonly=False):
  base=physics_load('shared_original_whole_input_physics','l2_strict.py').terminal(c)
  require(base.get('performance_accepted')is True,'Original physics mandatory')
  intent=read(root/'control/qualification_ledger'/(c+'.INTENT.json'))
  if 'additional_cpu_shared_timeslice_binding'in intent:return historical_shared(c).terminal(c,base,root=root,authority=authority_provider(),readonly=readonly)
  require('additional_cpu_spare_memory_admission_binding'in intent,'Unknown historical resource generation')
  return oldload('stage2_old_CPU2_whole_input','l2_strict.py').terminal(c)
 def policy(c):
  rule=cohorts[c];require(rule['primary_statistics_excluded']is True and rule['validated_union_authorized']is False,'Canary exclusion missing')
  require(sha(root/'control/SCOPE.json')==contract['original_primary_SCOPE_sha256'],'Frozen original primary scope drift')
  for name in ['SCOPE.json','MATRIX_CURRENT.json']:
   matrix=read(root/'control'/name);require(not any(p['cohort']==c for p in matrix['points']),'Engineer cohort leaked into primary '+name)
  spec=read(root/'control/specs'/(c+'.json'))
  observation.verify_science_rule(spec,rule,contract)
  require(spec.get('scientific_role')==rule['scientific_role'] and rule['scientific_role'],'Explicit engineer role mismatch')
  return rule
 def historical_observation(c):
  intent=read(root/'control/qualification_ledger'/(c+'.INTENT.json'));out=P(intent['output']);binding=intent['additional_strace_bpf_observation_binding'];path=out/'STRACE_BPF_OBSERVATION_SNAPSHOT.json'
  require(sha(path)==binding['snapshot_sha256'],'Historical observation snapshot')
  captured=read(path)['config'];pin=captured['qualified_sources']['extra_strict']
  allowed={'cbbddba1fe954a1e7dd411c89f9feff2480d5314781204b75fc8364159586711','1766aefbaf4710b876e0ed97a46bcfb91434a9f333e0a985b01864f592d1437b',sha(observation.__file__)}
  require(pin in allowed and sha(captured['source_paths']['extra_strict'])==pin,'Unreviewed historical observation source')
  oldextra=_load('stage2_INTENT_bound_observation',captured['source_paths']['extra_strict']);document=read(captured['exclusion_contract_path'])
  if pin==sha(observation.__file__):oldcontract=oldextra.normalize_contract(document,root,captured['exclusion_contract_sha256'],captured['qualification_only'],cfg=captured)
  else:oldcontract=oldextra.normalize_contract(document,root,captured['exclusion_contract_sha256'],captured['qualification_only'])
  return oldextra,oldcontract
 def result_path(c):return root/'analysis'/(c+'.RESULT.json')
 def engineering_path(c):return root/'analysis/engineering_results'/(c+'.RESULT.json')
 def replay(c):
  require(c in cohorts,'Unknown engineer replay scope');policy(c)
  rp=result_path(c);value=read(rp);require(value['cohort']==c and value['scientific_role']==cohorts[c]['scientific_role']and value['primary_statistics_excluded']is True and value['validated_union_authorized']is False and value['state']==consumer.PASS and consumer.accepted(value),'Engineer RESULT identity')
  require(engineering_path(c).exists()and read(engineering_path(c))==value,'Engineering mirror missing/changed')
  intent=read(root/'control/qualification_ledger'/(c+'.INTENT.json'));out=P(intent['output'])
  resource_key='additional_cpu_shared_timeslice_strict'if 'additional_cpu_shared_timeslice_binding'in intent else'additional_cpu_spare_memory_admission_strict'
  for key in [resource_key,EXTRA]:
   saved=value['proof'][key];side=P(saved['sidecar_path'])
   require(side.parent==out and side.exists()and sha(side)==saved['sidecar_sha256'],'Readonly replay requires existing strict sidecar')
  io=value['proof'].get('additional_shared_json_io_strict')or value['proof'].get('additional_future_memory_io_strict')
  require(io is not None and P(io['sidecar_path']).parent==out and sha(io['sidecar_path'])==io['sidecar_sha256'],'Readonly IO sidecar missing/changed')
  # Original replay remains source-bound and mandatory. Observation layer writes0.
  proof=whole_proof(c,readonly=True)
  oldextra,oldcontract=historical_observation(c)
  observed=oldextra.terminal(c,proof,root=root,contract=oldcontract,authority=authority_provider(),readonly=True)
  require(observed==value['proof'],'Readonly strict proof changed')
  original_archive=oldload('engineer_original_readonly_archive','l2_outbox.py').verify(c)
  require(original_archive=={k:v for k,v in value['archive'].items()if k!='additional_strace_bpf_archive_verification'},'Original full archive replay changed')
  archive=oldextra.verify_archive(c,original_archive,root=root,contract=oldcontract)
  require(archive==value['archive']['additional_strace_bpf_archive_verification'],'Readonly archive proof changed')
  return value
 def finish(c):
  if c not in cohorts:return oldfinish(c) # exact old call, no new reads/rewrites
  policy(c)
  if result_path(c).exists():return replay(c)
  state={'strict':False,'archive':False}
  def load(name,file):
   module=physics_load(name,file)if P(file).name=='l2_strict.py'else oldload(name,file)
   if P(file).name=='l2_strict.py':
    previous=module.terminal
    def terminal(candidate):
     require(candidate==c,'Cross-cohort strict invocation')
     intent=read(root/'control/qualification_ledger'/(c+'.INTENT.json'))
     require(FIELD in intent,'New scope cannot omit observation binding')
     proof=whole_proof(c,readonly=False);oldextra,oldcontract=historical_observation(c)
     value=oldextra.terminal(c,proof,root=root,contract=oldcontract,authority=authority_provider(),readonly=False)
     require(EXTRA in value,'Observation strict proof missing');state['strict']=True;return value
    module.terminal=terminal
   return module
  def archive_closed(candidate):
   require(candidate==c and state['strict'],'No accepted/fallback archive without all strict layers')
   archived=oldarchive(c)
   oldextra,oldcontract=historical_observation(c);proof=oldextra.verify_archive(c,archived,root=root,contract=oldcontract)
   state['archive']=True;return dict(archived,additional_strace_bpf_archive_verification=proof)
  def put(path,value,exclusive=False):
   path=P(path)
   if path==root/'analysis'/(c+'.RESULT.json'):
    require(state['strict']and state['archive'],'Accepted write before complete strict/archive verification')
    require(value.get('state')==consumer.PASS and value['proof'].get('performance_accepted')is True and EXTRA in value['proof'],'No weak accepted result')
    value.update(scientific_role=cohorts[c]['scientific_role'],primary_statistics_excluded=True,validated_union_authorized=False)
    require(not result_path(c).exists(),'Cannot overwrite existing canonical RESULT')
    if engineering_path(c).exists():require(read(engineering_path(c))==value,'Engineering mirror immutable conflict')
    else:oldput(engineering_path(c),value,True)
    # Canonical new-C result commits last. Real MATRIX/SCOPE stay untouched;
    # RuntimeFrames can then observe genuine strict/archived natural release.
    return oldput(result_path(c),value,True)
   return oldput(path,value,exclusive)
  namespace=dict(oldfinish.__globals__,R=root,load=load,archive_closed=archive_closed,put=put)
  cloned=types.FunctionType(oldfinish.__code__,namespace,oldfinish.__name__,oldfinish.__defaults__,oldfinish.__closure__)
  return cloned(c)
 def safe_finish(c):
  if c not in cohorts:return oldsafe(c)
  try:return finish(c)
  except Exception as error:
   value=dict(state='CPU_SHARED_OBSERVATION_HOLD_PRESERVE',cohort=c,error=repr(error),model_retries=0,accepted_cycles=None,primary_statistics_excluded=True)
   try:oldput(root/'analysis/engineering_results'/(c+'.HOLD.'+str(time.time_ns())+'.json'),value,True)
   except Exception as evidence_error:value['HOLD_evidence_write_error']=repr(evidence_error)
   return value
 return dict(finish_evidence=finish,safe_finish=safe_finish,readonly_replay=replay,result_path=result_path,engineering_path=engineering_path,
  original_finish=oldfinish,original_load=oldload,original_put=oldput,scope_contract=contract,
  original_safe=oldsafe,original_archive=oldarchive,original_consumer_sha256=ORIGINAL_CONSUMER_SHA,original_loader_source_sha256=loader_sha,production_installed=False)
def _load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def install_on_frame(frame,cfg_path,contract_path,contract_sha256,owner_assert,main=None,qualification_loader_sha256=None):
 """Main-only candidate API. Changes ONE frame-private module attribute only."""
 require(threading.current_thread()is threading.main_thread(),'Main owner thread required');owner_assert()
 main=main or sys.modules['__main__'];require(not hasattr(main,MARKER),'Consumer route already present')
 cfg=read(cfg_path);require(sha(contract_path)==contract_sha256,'Exclusion contract SHA');document=read(contract_path)
 require(cfg['future_primary_policy']=='NONE','This engineer qualification does not authorize broad primary rollout')
 require(P(cfg['source_paths']['consumer']).resolve()==P(__file__).resolve()and cfg['qualified_sources']['consumer']==sha(__file__),'Wrong consumer source')
 consumer=frame.f_locals['consumer'];engine=frame.f_locals['engine'];aging=frame.f_locals['res'].DTC_LARGE_JOB_AGING_INSTALLED
 require(all(module is not consumer for module in sys.modules.values()),'Consumer must be actual frame-private module, not shared module')
 extra=_load('bound_strace_observation_strict',cfg['source_paths']['extra_strict']);require(sha(extra.__file__)==cfg['qualified_sources']['extra_strict'],'Wrong strict source')
 contract=extra.normalize_contract(document,cfg['root'],contract_sha256,cfg['qualification_only'],cfg=cfg)
 if qualification_loader_sha256 is not None:
  require(cfg['qualification_only']is True and engine.registered()[2].get('qualification_only')is True,'Synthetic loader cannot enter production')
  contract['qualification_loader_sha256']=qualification_loader_sha256
 require(set(cfg['modes'])==set(contract['cohorts'])and all(contract['cohorts'][c]['mode']==mode for c,mode in cfg['modes'].items()),'Original engineering four modes only')
 bridge=make_private_consumer(consumer,contract,extra,lambda:engine.registered()[2])
 with aging.lock:
  owner_assert();before=(consumer.load,consumer.finish_evidence,consumer.put,consumer.archive_closed)
  require(consumer.safe_finish is bridge['original_safe'],'Consumer changed while preparing route')
  consumer.safe_finish=bridge['safe_finish']
  require(before==(consumer.load,consumer.finish_evidence,consumer.put,consumer.archive_closed),'Old consumer source callbacks changed')
  setattr(main,MARKER,dict(frame=frame,consumer=consumer,engine=engine,aging=aging,bridge=bridge,cfg=cfg,cfg_path=str(cfg_path),cfg_sha256=sha(cfg_path),
   contract_path=str(contract_path),contract_sha256=contract_sha256,original_refs=before,wrapper=bridge['safe_finish'],source_sha256=sha(__file__)))
 return dict(status='CPU_SHARED_EXACT_ONE_PRIVATE_SAFE_ROUTE_INSTALLED',only_changed='actual_frame_private_consumer.safe_finish',models_started=0,new_grants=0)
def consumer_check(frame,cfg):
 """Exact API used by B before future entry selection; no proof-shaped callback."""
 main=sys.modules['__main__'];m=getattr(main,MARKER)
 require(m['frame']is frame and frame.f_locals['consumer']is m['consumer'],'Wrong actual scheduler consumer')
 require(m['consumer'].safe_finish is m['wrapper'],'Actual ops.post path is not routed')
 require(m['original_refs']==(m['consumer'].load,m['consumer'].finish_evidence,m['consumer'].put,m['consumer'].archive_closed),'Original callback drift')
 require(cfg==m['cfg']==read(m['cfg_path'])and sha(m['cfg_path'])==m['cfg_sha256'],'Active observation config drift')
 require(cfg['future_primary_policy']=='NONE'and sha(m['contract_path'])==m['contract_sha256']and sha(__file__)==m['source_sha256'],'Consumer scope/source drift')
 for c in m['bridge']['scope_contract']['cohorts']:
  for name in ['SCOPE.json','MATRIX_CURRENT.json']:
   require(not any(p['cohort']==c for p in read(P(cfg['root'])/'control'/name)['points']),'Engineer present in primary matrix')
 return True
def restore_in_owner(owner_assert,main=None):
 require(threading.current_thread()is threading.main_thread(),'Main owner thread required');owner_assert();main=main or sys.modules['__main__'];m=getattr(main,MARKER)
 with m['aging'].lock:
  require(not hasattr(main,B_OWNER_MARKER),'Restore future dispatcher before consumer')
  consumer=m['consumer'];require(consumer.safe_finish is m['wrapper']and m['frame'].f_locals['consumer']is consumer,'Restore newer consumers first')
  require(m['original_refs']==(consumer.load,consumer.finish_evidence,consumer.put,consumer.archive_closed),'Original callback drift')
  q=m['engine'].registered()[2]
  for c in m['bridge']['scope_contract']['cohorts']:
   if c in q['consumed']:
    rp=m['bridge']['result_path'](c);require(rp.exists(),'Consumed shared result missing; preserve strict route')
    result=read(rp);proof=result.get('proof',{});shared=proof.get('additional_cpu_shared_timeslice_strict',{});observed=proof.get(EXTRA,{});archive=result.get('archive',{})
    require(m['consumer'].accepted(result)and result['uuid']==proof['uuid']==q['consumed'][c]['uuid'],'Shared restore requires same-UUID accepted performance')
    require(shared.get('schema')=='CPU_SHARED_TIMESLICE_FUTURE_MEMORY_095_V1'and shared.get('status')=='PASS_CPU_SHARED_TIMESLICE_IO_AND_ORIGINAL_PERFORMANCE','Shared restore resource generation')
    require(observed.get('schema')=='DTC_STRACE_SHARED_CPU_OBSERVATION_V1'and observed.get('status')=='PASS_CPU_SHARED_OBSERVATION_AND_ORIGINAL_IO','Shared restore observation generation')
    require(archive.get('additional_strace_bpf_archive_verification',{}).get('status')=='PASS_NEW_OBSERVATION_ARCHIVED_AND_NATIVE_RESTORED','Shared restore complete archive/native verification')
  consumer.safe_finish=m['bridge']['original_safe'];delattr(main,MARKER)
 return dict(status='EXACT_OLD_PRIVATE_CONSUMER_SAFE_RESTORED',models_started=0,new_grants=0)
