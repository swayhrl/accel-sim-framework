"""Inert by default. Administrative file control only; never dispatches a model."""
from pathlib import Path
import argparse,copy,fcntl,hashlib,json,os,time,types
ROOT=Path('/root/data/dtc_oracle_clean_successor_20261107_v1/remaining24');BASE=ROOT.parent
REQUEST='DTC_ORACLE_REMAINING24_20261106_V1';OWNER=525725;START=1077052887
OBSERVER_SHA='d31c09c23f8f66af80dd940fdae92f3af8e9810524b3a29e6bffbf2353862e0b'
FIXED_DEPENDENCIES={'owner_observer':OBSERVER_SHA,'engine':'a69dfd8e19dc5d7852232c0147f35a4d2a4164e69b67f039d9f0c08742aef783',
 'resources':'3f20a6bb18d401825a84eb5445c00d0771c449fa5766ddd434d9f284b7ff4b7f',
 'RSS_history':'d10e7691ccd0b87b223cfd32a4651a256ec8c0bf1caf377ae360edbfaaed3d64'}
class Hold(RuntimeError):pass
def need(x,why):
 if not x:raise Hold(why)
def encoded(v):return(json.dumps(v,sort_keys=True,indent=2)+'\n').encode()
def digest(v):return hashlib.sha256(encoded(v)).hexdigest()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def put(p,v):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('xb')as h:h.write(encoded(v));h.flush();os.fsync(h.fileno())
def load(ref,name):
 p=Path(ref['path']);need(sha(p)==ref['sha256'],'DEPENDENCY_PIN_DRIFT')
 m=types.ModuleType(name);m.__file__=str(p);exec(compile(p.read_bytes(),str(p),'exec'),m.__dict__);return m
def inspect_unused(snapshot,cohort,binding_sha):
 q=snapshot['q'];need(q['request']==REQUEST and(q['owner_pid'],q['owner_start_ticks'])==(OWNER,START),'FIXED_REQUEST_OWNER_GENERATION')
 need(q['budget']==96 and q['remaining']==96-len(q['consumed']),'FIXED_ONCE_ONLY_BUDGET')
 need(cohort in q['admitted_specs']and cohort not in q['consumed'],'TARGET_ALREADY_CONSUMED_OR_FOREIGN')
 need(cohort not in snapshot['intents'],'TARGET_INTENT_EXISTS')
 need(not any(v['cohort']==cohort for v in snapshot['stage_claims'].values()),'TARGET_STAGE_CLAIM_EXISTS')
 need(not any(v['cohort']==cohort for v in snapshot['claims'].values()),'TARGET_SHARED_CLAIM_EXISTS')
 need(cohort not in snapshot['running']and cohort not in snapshot['preparing'],'TARGET_FUTURE_RUNNING_OR_PREPARING')
 need(snapshot['binding_sha256']==binding_sha,'TARGET_BINDING_CHANGED')
 return True
def no_hidden_errors(before,after):
 need(before['errors']==after['errors']and before['cycle_fingerprints']==after['cycle_fingerprints'],
      'NEW_ENGINEERING_ERROR_DURING_SELF_PAUSE_KEEP_HOLD')
def acknowledge(before,after,created_ns,cohort,binding_sha):
 inspect_unused(after,cohort,binding_sha);no_hidden_errors(before,after)
 need(after['batch_mtime_ns']>created_ns and after['pool_mtime_ns']>created_ns,
      'WAIT_NEW_OWNER_CYCLE_ACK')
 need(after['gates']=={},'WAIT_OWNER_SAW_PAUSE_EMPTY_GATES')
 need(after['pool_owner']==(OWNER,START),'ACK_FROM_FOREIGN_OWNER')
 return True
def target_from_picker(decision,binding,snapshot,resource):
 need(all(resource.get(k)is True for k in['physical_RAM_pass','physical_disk_pass','admission_disk_pass','admission_pressure_pass']),
      'RESOURCE_BUSY_NOT_A_BINDING_REPAIR')
 need(binding is not None and binding['cohort']==decision['cohort'],'NO_EXISTING_TARGET_BINDING')
 cohort=decision['cohort'];inspect_unused(snapshot,cohort,snapshot['binding_sha256'])
 cpu=binding['host_cpu'];occupiers=[x for x in snapshot['claims'].values()if x['host_cpu']==cpu and x['cohort']!=cohort]
 need(occupiers and decision['host_cpu']!=cpu,'NO_ACTUAL_OTHER_CLAIM_BINDING_CONFLICT')
 need(any(x['cohort']in snapshot['mapped_live_cohorts']for x in occupiers),'OCCUPIER_NOT_PROVEN_MAPPED_LIVE')
 return dict(cohort=cohort,binding_sha256=snapshot['binding_sha256'],binding_cpu=cpu,
             picker_free_cpu=decision['host_cpu'],occupiers=occupiers)
def still_blocked(snapshot,target):
 return any(v['cohort']!=target['cohort']and v['host_cpu']==target['binding_cpu']
            and v['cohort']in snapshot['mapped_live_cohorts']for v in snapshot['claims'].values())
def verify_self_pause(path,token):
 need(Path(path).exists()and Path(path).read_bytes()==encoded(token),'PAUSE_CHANGED_OR_FOREIGN_KEEP_HOLD')
def preserve_unused_binding(path,audit,expected_sha):
 need(sha(path)==expected_sha,'BINDING_CHANGED_AT_RENAME');destination=Path(audit)/'ORIGINAL_UNUSED_BINDING.json'
 need(not destination.exists(),'NO_REPEAT_BINDING_RETIREMENT');os.rename(path,destination)
 need(sha(destination)==expected_sha,'PRESERVED_BINDING_SHA');return destination
class LiveReadOnly:
 def __init__(self,release):
  self.release=release;self.plan=read(ROOT/'control/EXECUTION_PLAN.json');self.plan_sha=sha(ROOT/'control/EXECUTION_PLAN.json')
  need(all(release[k]['sha256']==v for k,v in FIXED_DEPENDENCIES.items()),'ONLY_REVIEWED_FIXED_READONLY_DEPENDENCIES')
  need(release['owner_observer']['sha256']==OBSERVER_SHA,'ONLY_REVIEWED_EXTERNAL_OBSERVER')
  self.observer=load(release['owner_observer'],'BINDING_ADMIN_OWNER_OBSERVATION_ONLY')
  self.engine=load(release['engine'],'BINDING_ADMIN_AUTHORITY_READ_ONLY')
  self.res=load(release['resources'],'BINDING_ADMIN_PICKER_READ_ONLY')
  self.history=load(release['RSS_history'],'BINDING_ADMIN_RSS_READ_ONLY')
  self.points=read(ROOT/'control/MATRIX.fixed.json')['points'];need(len(self.points)==96,'FIXED96_ONLY')
  self.pause=BASE/'control/ENGINEERING_PAUSE_NEW.json'
 def snapshot(self,cohort=None):
  need(sha(ROOT/'control/EXECUTION_PLAN.json')==self.plan_sha,'LIVE_PLAN_CHANGED')
  self.observer.observe_owner(self.plan) # true PID/start/source/four held locks; not model ancestry
  q=self.engine.authority()[0]['registered_future_requests'][REQUEST]
  poolpath=BASE/'control/SHARED_POOL_STATUS.json';batchpath=ROOT/'analysis/BATCH_STATE.json'
  pool=read(poolpath);batch=read(batchpath);claims=read(BASE/'control/SHARED_POOL_DISPATCH_RESERVATIONS.json')['claims'];stage=read(ROOT/'control/POOL_DISPATCH_RESERVATIONS.json')['claims']
  need(all(v['request']==REQUEST for v in claims.values()),'FOREIGN_SHARED_CONTEXT')
  need({k.split(':',1)[1]:v for k,v in claims.items()}==stage,'STAGE_SHARED_CLAIMS_DIFFER')
  mapped=[]
  for c,row in q['consumed'].items():
   if row.get('execution_receipt'):continue
   p=ROOT/'DTC/run/results'/row['uuid']/'NATIVE_SIMULATOR_PID_AND_MAPS.json'
   if not p.exists():continue
   m=read(p)
   try:
    values=(Path('/proc')/str(m['pid'])/'stat').read_text().rsplit(')',1)[1].split()
    claim=claims.get(REQUEST+':'+c);spec=read(ROOT/'control/specs'/(c+'.json'))
    if(int(values[19])==m['start_ticks']and values[0]!='Z'and claim
       and claim.get('uuid')==row['uuid']and spec['native_simulator_argv'][0]in m.get('maps','')
       and os.sched_getaffinity(m['pid'])=={claim['host_cpu']}):mapped.append(c)
   except FileNotFoundError:pass
  binding=ROOT/'control/dispatch_bindings'/(cohort+'.json')if cohort else None
  return dict(q=q,claims=claims,stage_claims=stage,intents=[p.name.removesuffix('.INTENT.json')for p in(ROOT/'control/qualification_ledger').glob('*.INTENT.json')],
    running=list(batch.get('running',[])),preparing=[x['cohort']for x in pool.get('running',[])],
    mapped_live_cohorts=mapped,binding_sha256=sha(binding)if binding and binding.exists()else None,
    errors=batch.get('errors',{}),cycle_fingerprints={p.name:sha(p)for p in(ROOT/'control/CLEAN_OPERATIONAL_GENERATION').glob('*.CYCLE_ERROR.json')},
    gates=batch.get('gates',{}),batch_mtime_ns=batchpath.stat().st_mtime_ns,pool_mtime_ns=poolpath.stat().st_mtime_ns,
    pool_owner=(pool['owner_pid'],pool['owner_start_ticks']))
 def diagnose(self):
  need(not self.pause.exists()and not(BASE/'control/POOL_STOP_NEW.json').exists(),'FOREIGN_OR_EXISTING_PAUSE_HOLD')
  snap=self.snapshot();need(not snap['cycle_fingerprints'],'CYCLE_ERROR_HOLD')
  if snap['q']['remaining']==0:return None
  pending=[]
  for row in self.points:
   c=row['cohort'];gate=snap['gates'].get(c,{})
   if c in snap['q']['consumed']or REQUEST+':'+c in snap['claims']or not isinstance(gate,dict)or gate.get('state')!='EXTENSION_MODE_GATE2_RELEASED':continue
   p=ROOT/'control/specs'/(c+'.json');need(sha(p)==snap['q']['admitted_specs'][c],'CANONICAL_SPEC_PIN');pending.append(read(p))
  hp=max((ROOT/'control/CLEAN_OPERATIONAL_GENERATION/RSS_history_snapshots').glob('*.json'),key=lambda p:p.stat().st_mtime)
  self.RSS=read(hp);self.history.verify_snapshot(self.RSS);self.history.bind_forecast(self.res,lambda:self.RSS)
  sample=self.res.sample_system();sample['cpu_allowed']=self.plan['new_dispatcher_cpu_allowance']
  index=len(list((ROOT/'events').glob('*DISPATCH_AUTHORIZED_UNUSED_IDENTITY.json')))
  decision=self.history.choose(self.res,self.RSS,pending,sample,snap['claims'],policy=read(ROOT/'control/RESOURCE_POLICY.json'),dispatch_index=index)
  if decision is None:return None
  c=decision['cohort'];p=ROOT/'control/dispatch_bindings'/(c+'.json')
  if not p.exists():return None
  binding=read(p);snap=self.snapshot(c);spec=next(s for s in pending if s['cohort']==c)
  need(binding['canonical_spec_sha256']==snap['q']['admitted_specs'][c]
       and binding['resolved_spec_sha256']==digest(dict(spec,host_cpu=binding['host_cpu'])),'BINDING_CANONICAL_RESOLVED_PIN')
  occupied=[v for v in snap['claims'].values()if v['host_cpu']==binding['host_cpu']and v['cohort']!=c]
  if not occupied:return None
  resource=self.res.resources(spec,True)
  target=target_from_picker(decision,binding,snap,resource);return dict(target=target,snapshot=snap,index=index,resource_decision=resource['resource_decision'])
def repair(io,observation,audit,ack_timeout=45):
 target=observation['target'];c=target['cohort'];bs=target['binding_sha256'];audit=Path(audit);audit.mkdir(exist_ok=False)
 before=io.snapshot(c);inspect_unused(before,c,bs);no_hidden_errors(observation['snapshot'],before)
 token=dict(schema='DTC_UNUSED_BINDING_ADMIN_SELF_PAUSE_V1',actor_pid=os.getpid(),cohort=c,binding_sha256=bs,audit=str(audit),nonce=time.time_ns(),new_admission_only=True,model_or_registry_operations=0)
 put(audit/'BEFORE.fixed.json',observation);put(io.pause,token);created=io.pause.stat().st_mtime_ns;put(audit/'SELF_PAUSE.fixed.json',token)
 deadline=time.monotonic()+ack_timeout
 while True:
  verify_self_pause(io.pause,token);after=io.snapshot(c)
  try:acknowledge(before,after,created,c,bs);break
  except Hold as error:
   if not str(error).startswith('WAIT_'):raise
  need(time.monotonic()<deadline,'OWNER_ACK_TIMEOUT_KEEP_PAUSE_HOLD');time.sleep(.5)
 put(audit/'ACTUAL_OWNER_ACK.fixed.json',after)
 verify_self_pause(io.pause,token);final=io.snapshot(c);acknowledge(before,final,created,c,bs)
 verify_self_pause(io.pause,token)
 if not still_blocked(final,target):
  # Natural completion may have solved the collision while we waited. Only a
  # proved-safe no-op (same unused target, no hidden errors, exact own pause)
  # releases this pause without retiring the binding.
  os.rename(io.pause,audit/'ORIGINAL_SELF_PAUSE.json')
  put(audit/'AFTER.fixed.json',dict(status='SKIP_NO_LONGER_BLOCKED',cohort=c,binding_preserved=True,registry_writes=0,models=0))
  return dict(target,status='SKIP_NO_LONGER_BLOCKED')
 destination=preserve_unused_binding(ROOT/'control/dispatch_bindings'/(c+'.json'),audit,bs)
 # A newly returned unexpected worker error can be hidden by our pause file;
 # never clear it based only on unchanged target identity.
 last=io.snapshot(c);inspect_unused(last,c,None);no_hidden_errors(before,last);verify_self_pause(io.pause,token)
 archived=audit/'ORIGINAL_SELF_PAUSE.json';os.rename(io.pause,archived)
 put(audit/'AFTER.fixed.json',dict(status='UNCONSUMED_BINDING_PRESERVED_SAME_OWNER_MAY_CONTINUE',cohort=c,binding_archive=str(destination),binding_sha256=bs,self_pause_archive=str(archived),models_started_by_helper=0,registry_writes=0,owner_changed=False))
 return target
def run(release):
 need(release['actual_administrative_helper_authorized']is True and release['subject_source_sha256']==sha(__file__),'MAIN_EXACT_ADMIN_HELPER_RELEASE_REQUIRED')
 need(release['request']==REQUEST and release['models_allowed']==release['registry_writes_allowed']==0,'ADMIN_ONLY_FIXED96')
 folder=ROOT/'control/UNUSED_BINDING_ADMIN';folder.mkdir(exist_ok=True)
 with(folder/'HELPER.lock').open('a+b')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);io=LiveReadOnly(release);stable=None;seen=set()
  while True:
   try:
    value=io.diagnose()
    if value is None:stable=None
    else:
     key=(value['target']['cohort'],value['target']['binding_sha256'])
     need(key not in seen,'SAME_BINDING_ALREADY_RETIRED_NO_BLIND_REPEAT')
     if stable and stable['key']==key and stable['batch_mtime_ns']!=value['snapshot']['batch_mtime_ns']:
      result=repair(io,value,folder/(str(time.time_ns())+'_'+key[0]))
      if result.get('status')!='SKIP_NO_LONGER_BLOCKED':seen.add(key)
      stable=None
     else:stable=dict(key=key,batch_mtime_ns=value['snapshot']['batch_mtime_ns'])
   except Exception as error:
    put(folder/(str(time.time_ns())+'.HOLD.json'),dict(reason=str(error),new_dispatcher=False,healthy_models_untouched=True));return dict(status='ADMIN_HELPER_HOLD',reason=str(error))
   time.sleep(release.get('poll_seconds',15))
def main(argv=None):
 p=argparse.ArgumentParser();p.add_argument('--release',type=Path);a=p.parse_args(argv)
 if a.release is None:return dict(status='INERT_CPU_PREPARATION_ONLY',models=0,registry_writes=0,source_changes=0)
 return run(read(a.release))
if __name__=='__main__':print(json.dumps(main(),sort_keys=True))
