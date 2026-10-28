"""Inactive V3 private consumer candidate; exact historical nonselected delegation.
No installation, registration, simulation or process control occurs on import.
"""
import copy,hashlib,importlib.util,json,pathlib,sys,threading,time,types
P=pathlib.Path
PRODUCTION_ROOT=P('/root/data/dtc_l2_mlp_exploration_20261027_v1')
ORIGINAL_CONSUMER_SHA='6cc6cc30a71740df951327414d094953effb73a406e7036358ad0b702ebb0403'
CPU2_OWNER_SHA='4945156fe11db69f75a6f1dc39e08a0f5c7b28ef43244525f570bebbf33cf080'
V2_CONSUMER_SHA='2e548a181f28535043bdd5ed885ab2d554ca6462a2e8e690f6e400a36d8fc1c7'
ID='DTC_STRACE_BROAD_SHARED_CPU_V1'
FIELD='additional_strace_bpf_observation_binding';EXTRA='additional_strace_bpf_observation_strict'
MARKER='DTC_STRACE_BROAD_SHARED_PRIVATE_CONSUMER_V1';B_OWNER_MARKER='DTC_STRACE_BROAD_SHARED_DISPATCH_V1'
class ObservationHold(RuntimeError):pass
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def read(p):return json.loads(P(p).read_bytes())
def require(v,m):
 if not v:raise ObservationHold(m)
def load(n,path):
 sp=importlib.util.spec_from_file_location(n,path);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
def mandatory_old(proof):
 require(proof.get('performance_accepted')is True and type(proof.get('cycles'))is int and proof['cycles']>0,'Original full performance strict')
 require('additional_cpu_spare_memory_admission_strict'not in proof,'Dynamic Shared cannot claim CPU2 strict PASS')
 require(proof.get('additional_cpu_shared_timeslice_strict',{}).get('schema')=='CPU_SHARED_DYNAMIC_FUTURE_MEMORY_095_V1'and proof['additional_cpu_shared_timeslice_strict'].get('status')=='PASS_CPU_SHARED_DYNAMIC_IO_AND_ORIGINAL_PERFORMANCE','Dynamic Shared strict mandatory')
 require('additional_shared_json_io_strict'in proof or'additional_future_memory_io_strict'in proof,'IO strict mandatory')
 return proof
def make_private_consumer(consumer,scope_contract,observation,authority_provider):
 contract=copy.deepcopy(scope_contract);root=P(contract['root']);cfg=contract['cfg']
 require(sha(consumer.__file__)==ORIGINAL_CONSUMER_SHA,'Original consumer source drift')
 oldfinish=consumer.finish_evidence;oldsafe=consumer.safe_finish;oldload=consumer.load;oldput=consumer.put;oldarchive=consumer.archive_closed
 require(P(oldfinish.__code__.co_filename)==P(consumer.__file__),'Unknown original finisher')
 q=authority_provider();qualification=contract.get('qualification_only')is True and q.get('qualification_only')is True and root!=PRODUCTION_ROOT
 require(root==PRODUCTION_ROOT or qualification,'Private root needs both qualification flags')
 loader_sha=sha(oldload.__code__.co_filename)
 require(loader_sha==CPU2_OWNER_SHA or(qualification and loader_sha==contract.get('qualification_loader_sha256')),'Historical CPU2 loader required')
 if not qualification:require(sha(oldsafe.__code__.co_filename)==V2_CONSUMER_SHA,'Current Stage2 outer safe route must be preserved')
 if qualification:physics_load=oldload
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
 def result_path(c):return root/'analysis'/(c+'.RESULT.json')
 def recovery_path(c):return root/'analysis/incident_recovery_results'/(c+'.RESULT.json')
 def route_claim(c):return root/'control/broad_shared_cpu_route_claims'/(c+'.json')
 def selected(c):
  # Binding belongs to INTENT history, never today's cfg role alone. Exact V2
  # engineer4 and all jobs born before V3 continue through saved current safe.
  ip=root/'control/qualification_ledger'/(c+'.INTENT.json')
  if route_claim(c).exists():
   claim=read(route_claim(c));require(claim['cohort']==c and claim['schema']=='BROAD_SHARED_CPU_FUTURE_ROUTE_CLAIM_V1'and claim['overlay_id']==ID,'Wrong V3 route claim')
   return True
  if not ip.exists():return False
  intent=read(ip);binding=intent.get(FIELD)
  if binding is not None:
   if binding.get('schema')==ID:return True
   if binding.get('schema')in ['DTC_STRACE_FUTURE_ENTRY_V2','DTC_STRACE_FUTURE_ENTRY_V3','DTC_STRACE_SHARED_CPU_OBSERVATION_V1']:return False
   raise ObservationHold('Unknown observation generation; never fall back')
  snap=P(intent['output'])/'STRACE_BPF_OBSERVATION_SNAPSHOT.json'
  if snap.exists():
   snapshot=read(snap)
   if snapshot.get('schema')==ID:return True
   if snapshot.get('schema')not in ['DTC_STRACE_FUTURE_ENTRY_V2','DTC_STRACE_FUTURE_ENTRY_V3','DTC_STRACE_SHARED_CPU_OBSERVATION_V1']:raise ObservationHold('Unknown snapshot generation')
  return False
 def history(c):
  intent=read(root/'control/qualification_ledger'/(c+'.INTENT.json'));out=P(intent['output'])
  require(FIELD in intent and intent[FIELD]['schema']==ID,'New selected identity missing V3 INTENT binding')
  require(sha(out/'STRACE_BPF_OBSERVATION_SNAPSHOT.json')==intent[FIELD]['snapshot_sha256'],'Historical snapshot SHA')
  snap=read(out/'STRACE_BPF_OBSERVATION_SNAPSHOT.json');captured=snap['config']
  require(captured['qualified_sources']['extra_strict']==sha(observation.__file__),'New strict source generation mismatch')
  require(captured['qualified_sources']['consumer']==sha(__file__),'Consumer source generation mismatch')
  require(captured['root']==str(root),'Wrong captured root')
  return intent,out,snap,observation.normalize_contract(captured,root,qualification_only=captured['qualification_only'])
 def replay(c):
  require(selected(c),'Not a V3 replay identity')
  intent,out,snap,historical=history(c);value=read(result_path(c))
  require(value['cohort']==c and value['state']==consumer.PASS and consumer.accepted(value),'No canonical accepted V3 result')
  rule=snap['scope_policy']
  require(value['scientific_role']==rule['scientific_role']and value['primary_statistics_excluded']==rule['primary_statistics_excluded']and value['validated_union_authorized']is False,'Result role/union drift')
  if rule['primary_statistics_excluded']:require(read(recovery_path(c))==value,'IR mirror missing/changed')
  for key in ['additional_cpu_shared_timeslice_strict',EXTRA]:
   side=value['proof'][key];p=P(side['sidecar_path']);require(p.parent==out and p.exists()and sha(p)==side['sidecar_sha256'],'Readonly strict sidecar')
  io=value['proof'].get('additional_shared_json_io_strict')or value['proof'].get('additional_future_memory_io_strict')
  require(io is not None and P(io['sidecar_path']).parent==out and sha(io['sidecar_path'])==io['sidecar_sha256'],'Readonly IO sidecar')
  proof=whole_proof(c,readonly=True)
  observed=observation.terminal(c,proof,root,historical,authority_provider(),readonly=True)
  require(observed==value['proof'],'Readonly complete strict changed')
  archived=oldload('v3_original_readonly_outbox','l2_outbox.py').verify(c)
  require(archived=={k:v for k,v in value['archive'].items()if k!='additional_strace_bpf_archive_verification'},'Readonly original full archive changed')
  require(observation.verify_archive(c,archived,root,historical)==value['archive']['additional_strace_bpf_archive_verification'],'Readonly observation archive/native restore changed')
  return value
 def finish(c):
  if not selected(c):return oldsafe(c)
  intent,out,snap,historical=history(c)
  if result_path(c).exists():return replay(c)
  rule=snap['scope_policy'];state={'strict':False,'archive':False}
  def newload(name,file):
   module=physics_load(name,file)if P(file).name=='l2_strict.py'else oldload(name,file)
   if P(file).name=='l2_strict.py':
    previous=module.terminal
    def terminal(candidate):
     require(candidate==c,'Cross-cohort strict')
     value=observation.terminal(c,whole_proof(c,readonly=False),root,historical,authority_provider(),readonly=False)
     require(value[EXTRA]['schema']==ID,'V3 strict missing');state['strict']=True;return value
    module.terminal=terminal
   return module
  def archive_closed(candidate):
   require(candidate==c and state['strict'],'No archive promotion before all strict layers')
   archived=oldarchive(c);new=observation.verify_archive(c,archived,root,historical)
   state['archive']=True;return dict(archived,additional_strace_bpf_archive_verification=new)
  def put(path,value,exclusive=False):
   path=P(path)
   if path==result_path(c):
    require(state['strict']and state['archive'],'Accepted write before complete strict/archive')
    require(value['state']==consumer.PASS and EXTRA in mandatory_old(value['proof']),'Cannot publish weak accepted result')
    value.update(scientific_role=rule['scientific_role'],primary_statistics_excluded=rule['primary_statistics_excluded'],validated_union_authorized=False,observation_generation=ID)
    require(not result_path(c).exists(),'Cannot overwrite existing canonical RESULT')
    if rule['primary_statistics_excluded']:
     require(rule['scientific_role']=='INCIDENT_RECOVERY_PERFORMANCE_TRIAL','Unknown excluded V3 role')
     if recovery_path(c).exists():require(read(recovery_path(c))==value,'IR mirror conflict')
     else:oldput(recovery_path(c),value,True)
    return oldput(result_path(c),value,True)
   return oldput(path,value,exclusive)
  namespace=dict(oldfinish.__globals__,R=root,load=newload,archive_closed=archive_closed,put=put)
  cloned=types.FunctionType(oldfinish.__code__,namespace,oldfinish.__name__,oldfinish.__defaults__,oldfinish.__closure__)
  return cloned(c)
 def safe_finish(c):
  try:
   if not selected(c):return oldsafe(c)
   return finish(c)
  except Exception as error:
   value=dict(state='BROAD_SHARED_OBSERVATION_HOLD_PRESERVE',cohort=c,error=repr(error),accepted_cycles=None,model_retries=0,validated_union_authorized=False)
   try:oldput(root/'analysis/broad_shared_observation_holds'/(c+'.'+str(time.time_ns())+'.json'),value,True)
   except Exception as evidence_error:value['HOLD_evidence_write_error']=repr(evidence_error)
   return value
 return dict(safe_finish=safe_finish,finish_evidence=finish,readonly_replay=replay,selected=selected,
  result_path=result_path,recovery_path=recovery_path,original_safe=oldsafe,original_finish=oldfinish,
  original_refs=(oldload,oldfinish,oldput,oldarchive),scope_contract=contract,production_installed=False)
def install_on_frame(frame,cfg_path,owner_assert,main=None,qualification_loader_sha256=None):
 require(threading.current_thread()is threading.main_thread(),'Main owner thread required');owner_assert()
 main=main or sys.modules['__main__'];require(not hasattr(main,MARKER),'V3 route already installed')
 cfg=read(cfg_path);require(cfg['status']=='ACTIVE_FUTURE_SCOPED','Inactive configuration')
 require(cfg['source_paths']['consumer']==str(P(__file__).resolve())and cfg['qualified_sources']['consumer']==sha(__file__),'Consumer source mismatch')
 consumer=frame.f_locals['consumer'];engine=frame.f_locals['engine'];aging=frame.f_locals['res'].DTC_LARGE_JOB_AGING_INSTALLED
 require(all(m is not consumer for m in sys.modules.values()),'Actual frame-private consumer required')
 observation=load('v3_pinned_observation_strict',cfg['source_paths']['extra_strict'])
 require(sha(observation.__file__)==cfg['qualified_sources']['extra_strict'],'Strict source mismatch')
 q=engine.registered()[2];gate=observation.verify_release_prerequisite(cfg,q)
 contract=observation.normalize_contract(cfg,cfg['root'],qualification_only=cfg['qualification_only'])
 if qualification_loader_sha256 is not None:
  require(cfg['qualification_only']is True and q.get('qualification_only')is True and P(cfg['root'])!=PRODUCTION_ROOT,'Fixture loader cannot enter production')
  contract['qualification_loader_sha256']=qualification_loader_sha256
 bridge=make_private_consumer(consumer,contract,observation,lambda:engine.registered()[2])
 with aging.lock:
  owner_assert();before=(consumer.load,consumer.finish_evidence,consumer.put,consumer.archive_closed)
  require(consumer.safe_finish is bridge['original_safe'],'Previous V2 route changed')
  consumer.safe_finish=bridge['safe_finish']
  require(before==(consumer.load,consumer.finish_evidence,consumer.put,consumer.archive_closed),'Old callback changed')
  setattr(main,MARKER,dict(frame=frame,consumer=consumer,engine=engine,aging=aging,bridge=bridge,cfg=cfg,cfg_path=str(cfg_path),cfg_sha256=sha(cfg_path),wrapper=bridge['safe_finish'],original_refs=before,source_sha256=sha(__file__),gate=gate))
 return dict(status='BROAD_SHARED_PRIVATE_CONSUMER_SAFE_ROUTE_INSTALLED',models_started=0,new_grants=0,gate=gate)
def consumer_check(frame,cfg):
 m=getattr(sys.modules['__main__'],MARKER)
 require(m['frame']is frame and frame.f_locals['consumer']is m['consumer']and m['consumer'].safe_finish is m['wrapper'],'Actual scheduler post path not V3 routed')
 require(m['original_refs']==(m['consumer'].load,m['consumer'].finish_evidence,m['consumer'].put,m['consumer'].archive_closed),'Original callbacks changed')
 require(cfg==m['cfg']==read(m['cfg_path'])and sha(m['cfg_path'])==m['cfg_sha256']and sha(__file__)==m['source_sha256'],'Active config/source drift')
 observation=load('v3_readiness_observation',cfg['source_paths']['extra_strict']);require(sha(observation.__file__)==cfg['qualified_sources']['extra_strict'],'Readiness source')
 observation.verify_release_prerequisite(cfg,m['engine'].registered()[2]);return True
def restore_in_owner(owner_assert,main=None):
 require(threading.current_thread()is threading.main_thread(),'Main owner required');owner_assert()
 main=main or sys.modules['__main__'];m=getattr(main,MARKER)
 with m['aging'].lock:
  require(not hasattr(main,B_OWNER_MARKER),'Restore V3 dispatcher first; keep V2 underneath')
  require(m['consumer'].safe_finish is m['wrapper'],'Newer outer route present')
  q=m['engine'].registered()[2]
  for path in (P(m['cfg']['root'])/'control/broad_shared_cpu_route_claims').glob('*.json'):
   c=path.stem
   if c in q.get('admitted_specs',{}):
    claim=read(path);require(claim['schema']=='BROAD_SHARED_CPU_FUTURE_ROUTE_CLAIM_V1'and claim['overlay_id']==ID and claim['cohort']==c,'Unknown registered route claim')
    rp=m['bridge']['result_path'](c)
    require(c in q['consumed']and rp.exists()and m['consumer'].accepted(read(rp))and read(rp)['proof'].get(EXTRA,{}).get('schema')==ID,'Preserve mandatory V3 route for admitted unused/unresolved claim; Main disposition required')
  for c in q['consumed']:
   if not m['bridge']['selected'](c):continue
   rp=m['bridge']['result_path'](c);require(rp.exists(),'Preserve mandatory broad route from unresolved spent identity')
   value=read(rp);proof=value['proof'];intent=read(P(m['cfg']['root'])/'control/qualification_ledger'/(c+'.INTENT.json'));out=P(intent['output'])
   require(m['consumer'].accepted(value)and value['uuid']==proof['uuid']==intent['uuid']==q['consumed'][c]['uuid'],'Restore requires accepted same-UUID performance')
   require(proof.get(EXTRA,{}).get('schema')==ID and proof[EXTRA]['status']=='PASS_BROAD_SHARED_BPF_AND_ORIGINAL_IO','Restore observation generation')
   require(proof.get('additional_cpu_shared_timeslice_strict',{}).get('schema')=='CPU_SHARED_DYNAMIC_FUTURE_MEMORY_095_V1','Restore resource generation')
   require(intent[FIELD]['qualified_sources']==m['cfg']['qualified_sources'],'Restore captured source generation differs')
   for key in [EXTRA,'additional_cpu_shared_timeslice_strict']:
    side=proof[key];require(P(side['sidecar_path']).parent==out and sha(side['sidecar_path'])==side['sidecar_sha256'],'Restore strict sidecar missing/changed')
   require(value['archive'].get('additional_strace_bpf_archive_verification',{}).get('status')=='PASS_NEW_OBSERVATION_ARCHIVED_AND_NATIVE_RESTORED','Restore full archive/native closure')
  m['consumer'].safe_finish=m['bridge']['original_safe'];delattr(main,MARKER)
 return dict(status='EXACT_PREVIOUS_V2_OUTER_SAFE_RESTORED',models_started=0,new_grants=0)
