"""DRAFT finite28 dispatch under the existing DTC lease PID. No extension/reset/model retry."""
from pathlib import Path
import json,os,time,hashlib,importlib.util,concurrent.futures,fcntl,datetime,zlib,threading
P=Path;R=P('/root/data/dtc_perf_first_remaining28_20261104_v1');N=P('/root/data/ep_l2_dtc_l1_native_v2');A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_perf_first_parallel_exploration_20261104_v1/remaining28')
def rd(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def load(n,p):
 m=__import__('types').ModuleType(n);m.__file__=str(p);exec(compile(P(p).read_bytes(),str(p),'exec'),m.__dict__);return m
def put(p,v,exclusive=False):
 p=P(p);p.parent.mkdir(parents=True,exist_ok=True);b=(json.dumps(v,sort_keys=True,indent=2)+'\n').encode()
 if exclusive:
  with p.open('xb')as f:f.write(b);f.flush();os.fsync(f.fileno())
 else:
  t=p.with_name('.'+p.name+'.'+str(os.getpid())+'.writing');t.write_bytes(b);os.replace(t,p)
def stamp():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def native_live(p):
 try:
  v=rd(p);f=P('/proc',str(v['pid']),'stat').read_text().rsplit(')',1)[1].split();return int(f[19])==v['start_ticks']and f[0]not in['Z','X']
 except(OSError,ValueError,KeyError):return False
FAMILY_VARIANTS=('PHYS768_TAG64x8','PHYS1024_TAG64x8','OO_PIB192','TAG4BANK_PERBANK2_TOTAL8')
NEW_FAMILY_VARIANTS=FAMILY_VARIANTS[1:]
TERMINAL=('PASS_PERFFIRST28_DH_STRICT_ARCHIVE_NATIVE_RESTORE','FAIL_PERFFIRST28_DH_ARCHIVED_NO_RETRY')
def family_seeds(points):
 seeds={profile:next(x['cohort']for x in points if x['program']=='vectorAdd'and x['structure_variant']==profile)for profile in NEW_FAMILY_VARIANTS}
 assert len(set(seeds.values()))==3;return seeds

def eligible_for_family(spec,states,seeds):
 profile=spec['structure_variant'];state=states[profile]['state']
 return state=='QUALIFIED'or(state=='PENDING'and spec['cohort']==seeds.get(profile))

def seed_runtime_witness(c,e):
 """Read bounded current seed metadata/guard; full270 echo remains final strict.
 A measured speedup or regression is never a qualification criterion.
 """
 try:
  q=e.registered()[2]
  if c not in q['consumed']:return dict(state='PENDING',reason='UNUSED_LEGAL_SEED')
  row=q['consumed'][c];out=R/'DTC/run/results'/row['uuid'];rp=R/'analysis'/(c+'.RESULT.json')
  if rp.exists():
   result=rd(rp)
   if result['state']==TERMINAL[1]:return dict(state='FAILED',reason='ACTUAL_NATIVE_NEGATIVE',uuid=row['uuid'])
   if result['state']==TERMINAL[0]:
    assert result['uuid']==row['uuid']and result['proof']['performance_accepted']is True
    return dict(state='QUALIFIED',reason='NATURAL_STRICT_ARCHIVE_NATIVE_RESTORE',uuid=row['uuid'],actual270_echo_final_strict=True)
  done=R/'control/qualification_ledger'/(c+'.DONE.json')
  if done.exists():
   receipt=rd(done)
   if receipt['stop_reason']or receipt['launcher_wait_returncode']:return dict(state='FAILED',reason='ACTUAL_MODEL_STOP_OR_NONZERO_EXIT',uuid=row['uuid'])
   return dict(state='PENDING',reason='NATURAL_DONE_AWAIT_STRICT_ARCHIVE',uuid=row['uuid'])
  pm=out/'NATIVE_SIMULATOR_PID_AND_MAPS.json'
  if not pm.exists()or not native_live(pm):return dict(state='PENDING',reason='AWAIT_OBSERVED_NATIVE_GENERATION',uuid=row['uuid'])
  s=e.spec_for(c);i=rd(R/'control/qualification_ledger'/(c+'.INTENT.json'));launch=rd(out/'NATIVE_LAUNCH.json');pid=rd(pm);bind=e.binding()
  assert i['uuid']==row['uuid']and sha(R/'control/qualification_ledger'/(c+'.INTENT.json'))==row['intent_sha256']
  assert sha(out/'DOWNSTREAM_FROZEN_SPEC.json')==sha(R/'control/specs'/(c+'.json'))
  assert launch['argv'][-len(s['native_simulator_argv']):]==s['native_simulator_argv']and launch['host']['native_device']==2128
  assert s['native_simulator_argv'][0]in pid['maps']and pid['mnt_namespace']==s['execution_mnt_namespace']and pid['host_cpu_affinity_actual']==[s['host_cpu']]
  for packet in[i,launch,pid]:assert packet['l2_mlp_execution_binding']==bind
  for cfg in s['configs']:assert sha(cfg['path'])==cfg['sha256']
  resource=out/'RESOURCE_SAMPLES.jsonl.gz'
  if not resource.exists():return dict(state='PENDING',reason='AWAIT_AUTHENTICATED_RUNTIME_GUARD',uuid=row['uuid'])
  assert resource.stat().st_size<=s['limits']['max_result_directory_bytes']
  text=zlib.decompressobj(31).decompress(resource.read_bytes()).decode(errors='replace');rows=[json.loads(x)for x in text.splitlines()if x.strip().endswith('}')];guards=[x['DTC_exact_original_policy']for x in rows if'DTC_exact_original_policy'in x]
  if not guards:return dict(state='PENDING',reason='AWAIT_AUTHENTICATED_RUNTIME_GUARD',uuid=row['uuid'])
  guard=guards[-1]
  if guard['decision']['decision']=='STOP':return dict(state='FAILED',reason='ACTUAL_AUTHENTICATED_GUARD_STOP',uuid=row['uuid'])
  assert guard['runtime_policy_binding']['schema']=='DTC_PERFFIRST_REMAINING28_ADMISSION_PRESSURE_ONLY_RUNTIME_V1'
  assert guard['runtime_policy_binding']['guard_sha256']==bind['runtime_guard_sha256']and guard['runtime_policy_binding']['policy_sha256']==bind['runtime_guard_policy_sha256']
  return dict(state='QUALIFIED',reason='ACTUAL_PINNED_ARGV_CONFIG_IDENTITY_AND_GUARD',uuid=row['uuid'],actual270_echo_final_strict=False,performance_acceptance=False)
 except(AssertionError,TypeError)as error:return dict(state='FAILED',reason='OBSERVED_IDENTITY_CONFIG_OR_RUNTIME_BINDING_FAILURE',error=repr(error))
 except(OSError,ValueError,KeyError,zlib.error)as error:return dict(state='PENDING',reason='INCOMPLETE_OR_NOT_YET_READABLE_EVIDENCE',error=repr(error))

def update_family_state(old,witness):
 if old['state']=='FAILED':return old
 if witness['state']=='FAILED':return dict(state='FAILED',witness=witness)
 if witness['state']=='QUALIFIED':return dict(state='QUALIFIED',witness=witness)
 return old  # Awaiting final postprocess does not undo prior healthy runtime evidence.

def mark_family_admission_holds(reg,request,points,profile,witness,utc):
 """Only new own unused identities are held. Budget/specs/qstate stay unchanged."""
 own=reg['registered_future_requests'][request];assert own['budget']==28 and own['remaining']==28-len(own['consumed'])
 holds=own.setdefault('admission_holds',{});added=[]
 for point in points:
  c=point['cohort']
  if point['structure_variant']==profile and c not in own['consumed']:
   assert point['input_digest']and point['structure_variant']==profile
   holds[c]=dict(request=request,cohort=c,input_digest=point['input_digest'],full_input_digest=point['input_digest'],program=point['program'],suite=point['suite'],profile=profile,structure_variant=profile,cell='DH',downstream_profile='P0',state='UNUSED_FAMILY_HOLD',reason=witness,UTC=utc,cycles=None,uuid=None,consumed=False,scientific_model_starts=0,canonical_spec_sha256=own['admitted_specs'][c],source_ops_sha256=sha(__file__),no_budget_refund=True,no_model_retry=True);added.append(c)
 return added

def run_scheduler():
 import subprocess
 assert __import__('sys').dont_write_bytecode,'CALLER_MUST_DISABLE_BYTECODE_WRITES_BEFORE_SCHEDULER'
 assert os.getpid()==1498278 and int(P('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19])==977758783
 plan=rd(R/'control/EXECUTION_PLAN.json');mask=plan['new_dispatcher_cpu_allowance'];assert mask and len(set(mask))==len(mask)and threading.current_thread()is not threading.main_thread()
 assert not(set(mask)&({2,258}|set(range(32,64))|set(range(288,320)))),'PROTECTED_GES_MAIN_CPU_OVERLAP'
 os.sched_setaffinity(0,set(mask));assert set(os.sched_getaffinity(0))==set(mask)
 e=load('perf28_owner_engine',R/'tools/perf28_native.py');res=load('perf28_owner_resources',R/'tools/perf28_resources.py');consumer=load('perf28_owner_results',R/'tools/perf28_results.py');e.assert_parent_lease();points=rd(R/'control/MATRIX.json')['points'];cohorts=[x['cohort']for x in points];assert len(cohorts)==len(set(cohorts))==28 and set(cohorts)==set(EXPECTED28_COHORTS)
 assert {x['program']for x in points}=={'2DCONV','GEMM','convolutionSeparable','scan','ATAX','MVT','BICG','vectorAdd'}
 assert all(x['cohort'].startswith('E2-DTCPF28-')for x in points)
 predecessor=res.first4_completion_gate();assert predecessor['pass'],'FIRST4_PREDECESSOR_GATE_HOLD'
 seeds=family_seeds(points);family_states={p:dict(state='QUALIFIED'if p=='PHYS768_TAG64x8'else'PENDING',basis='C_FIRST4_FULL_CLOSURE'if p=='PHYS768_TAG64x8'else'AWAIT_OWN_VECTORADD_ORIGINAL_POINT')for p in FAMILY_VARIANTS}
 sample=res.sample_system();max_workers=min(28,max(1,len(sample['cpu_allowed'])-2));claims={};running={};post={};cool={};errors={};lock=threading.RLock();previous=None;dispatch_index=0
 def saveclaims():put(R/'control/POOL_DISPATCH_RESERVATIONS.json',dict(claims=claims))
 def event(kind,**data):put(A/'events'/(str(time.time_ns())+'_'+kind+'.json'),dict(UTC=stamp(),kind=kind,**data),True)
 def work(c):
  try:
   cmd=[str(N/'bin/experiment'),'prepare',c,'--project','DTC_L1'];x=subprocess.run(cmd,capture_output=True,text=True);put(R/'logs'/(c+'.PREPARE.'+str(time.time_ns())+'.json'),dict(returncode=x.returncode,stdout=x.stdout,stderr=x.stderr),True)
   if x.returncode:return dict(state='ZERO_START_HOLD',error=x.stderr[-3000:])
   cmd[1]='run-native';x=subprocess.run(cmd,capture_output=True,text=True);put(R/'logs'/(c+'.NATIVE_COMMAND.'+str(time.time_ns())+'.json'),dict(returncode=x.returncode,stdout=x.stdout,stderr=x.stderr),True)
   dp=R/'control/qualification_ledger'/(c+'.DONE.json')
   if dp.exists():return dict(state='EXECUTION_CLOSED',cohort=c)
   q=e.registered()[2];return dict(state='SPENT_ENGINEERING_HOLD'if c in q['consumed']else'ZERO_START_HOLD',cohort=c,error=(x.stderr or x.stdout)[-3000:])
  except BaseException as error:
   try:spent=c in e.registered()[2]['consumed']
   except BaseException:spent=True
   return dict(state='SPENT_ENGINEERING_HOLD'if spent else'ZERO_START_HOLD',cohort=c,error=repr(error))
 with(R/'control/DISPATCH_OWNER.lock').open('a+b')as held:
  fcntl.flock(held,fcntl.LOCK_EX|fcntl.LOCK_NB);put(R/'control/DISPATCH_STARTED.json',dict(UTC=stamp(),pid=os.getpid(),start_ticks=977758783,thread_ident=threading.get_ident(),finite28_only=True,max_workers=max_workers,owner_allowed_cpus=sample['cpu_allowed'],no_second_OS_controller=True),True)
  with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers,thread_name_prefix='DTCPF28_MODEL')as pool,concurrent.futures.ThreadPoolExecutor(max_workers=2,thread_name_prefix='DTCPF28_ARCHIVE')as archives:
   while True:
    e.assert_parent_lease();q=e.registered()[2]
    with lock:
     for f,c in list(running.items()):
      if not f.done():continue
      v=f.result();running.pop(f);claims.pop(c,None);saveclaims();event('WORKER_RETURN',cohort=c,result=v)
      if v['state']=='EXECUTION_CLOSED':post[archives.submit(consumer.safe_finish,c)]=c
      elif v['state']=='ZERO_START_HOLD':cool[c]=time.monotonic()+60;errors[c]=v
      else:errors[c]=v;put(R/'analysis'/(c+'.ENGINEERING_HOLD.json'),v)
     for f,c in list(post.items()):
      if not f.done():continue
      v=f.result();post.pop(f);event('POSTPROCESS_RETURN',cohort=c,state=v['state'])
      if v['state']not in['PASS_PERFFIRST28_DH_STRICT_ARCHIVE_NATIVE_RESTORE','FAIL_PERFFIRST28_DH_ARCHIVED_NO_RETRY']:errors[c]=v
     # Only same-UUID evidence work can be reconsumed; never retry a model.
     busy=set(post.values())
     for c,row in q['consumed'].items():
      if row.get('execution_receipt')and c not in busy and c not in running.values()and not(R/'analysis'/(c+'.RESULT.json')).exists()and time.monotonic()>=cool.get('post:'+c,0):post[archives.submit(consumer.safe_finish,c)]=c;cool['post:'+c]=time.monotonic()+60
     for profile,seed in seeds.items():
      old_state=family_states[profile]['state'];family_states[profile]=update_family_state(family_states[profile],seed_runtime_witness(seed,e))
      if old_state!='FAILED'and family_states[profile]['state']=='FAILED':
       def preserve_family_hold(reg,profile=profile,witness=family_states[profile]['witness']):mark_family_admission_holds(reg,e.REQ,points,profile,witness,stamp())
       e.update_authority(preserve_family_hold);event('FAMILY_FAILED_UNUSED_IDENTITIES_HELD_ONLY',profile=profile,witness=family_states[profile]['witness'],no_healthy_model_signal=True)
     q=e.registered()[2]
     sample=res.sample_system();put(R/'control/RESOURCE_OBSERVER.json',sample);pending=[e.canonical(c)for c in cohorts if c not in q['consumed']and c not in q.get('admission_holds',{})and c not in claims and time.monotonic()>=cool.get(c,0)]
     pending=[spec for spec in pending if eligible_for_family(spec,family_states,seeds)]
     for _ in range(max_workers-len(running)):
      if not pending:break
      decision=res.choose_dispatch(pending,sample,claims,previous=previous,policy=rd(R/'control/RESOURCE_POLICY.json'),dispatch_index=dispatch_index)
      if decision is None:break
      c=decision['cohort'];spec=e.canonical(c);cpu=decision['host_cpu'];db=R/'control/dispatch_bindings'/(c+'.json')
      fresh=res.resources(spec,True)
      if not(fresh['physical_RAM_pass']and fresh['physical_disk_pass']and fresh.get('admission_disk_pass',False)):
       event('PRECLAIM_RESOURCE_HOLD_NO_BINDING_NO_START',cohort=c,resource_sample=fresh);pending=[x for x in pending if x['cohort']!=c];continue
      if db.exists():
       binding=rd(db)
       if binding['host_cpu']not in sample['cpu_allowed']or binding['host_cpu']in({v['host_cpu']for v in claims.values()}|{cpu for row in sample.get('observed_affinity_claims',sample.get('observed_models',[]))for cpu in row['cpus']}):pending=[s for s in pending if s['cohort']!=c];continue
       cpu=binding['host_cpu']
      else:
       binding=dict(cohort=c,canonical_spec_sha256=sha(R/'control/specs'/(c+'.json')),host_cpu=cpu,resolved_spec_sha256=e.jsonsha(dict(spec,host_cpu=cpu)));put(db,binding,True)
      claims[c]=dict(host_cpu=cpu,workload=spec['workload'],predicted_peak_RAM_bytes=spec['estimated_peak_model_RAM_bytes'],result_cap_bytes=spec['limits']['max_result_directory_bytes'],RAM_cap_bytes=spec['limits']['max_process_tree_rss_bytes'],observed_model=False);saveclaims();running[pool.submit(work,c)]=c;dispatch_index+=1;event('DISPATCH_AUTHORIZED_UNUSED_IDENTITY',cohort=c,cpu=cpu);pending=[s for s in pending if s['cohort']!=c];sample=res.sample_system()
     states={c:rd(R/'analysis'/(c+'.RESULT.json'))['state']if(R/'analysis'/(c+'.RESULT.json')).exists()else('UNUSED_FAMILY_HOLD'if c not in q['consumed']and(c in q.get('admission_holds',{})or family_states[next(x['structure_variant']for x in points if x['cohort']==c)]['state']=='FAILED')else'PENDING')for c in cohorts};current=e.registered()[2];status=dict(UTC=stamp(),request=e.REQ,budget=28,consumed=len(current['consumed']),remaining=current['remaining'],running=list(running.values()),postprocess=list(post.values()),first4_predecessor_gate_passed=True,family_seeds=seeds,family_qualification_states=family_states,unused_family_HOLD=[c for c,state in states.items()if state=='UNUSED_FAMILY_HOLD'],performance_never_used_for_family_gate=True,preclaim_resource_holds=res.preclaim_diagnostics(),claims=len(claims),states=states,errors=errors,source_scope='EXACT_PRIOR_PLAN_NON_TAG_REMAINING28_ONLY',conditional_remaining28_scope_authorized=True,Tag16_never_started=True,additional_experiments_released=False)
     put(R/'analysis/BATCH_STATE.json',status);put(A/'LATEST_EXECUTION_STATUS.json',status)
     if current['remaining']>0 and not running and not post and all(states[c]in TERMINAL for c in current['consumed'])and all(states[c]=='UNUSED_FAMILY_HOLD'for c in cohorts if c not in current['consumed']):
      def stop_unused_future(reg):
       own=reg['registered_future_requests'][e.REQ];assert own['budget']==28 and own['remaining']==28-len(own['consumed'])and set(own['consumed'])==set(current['consumed'])
       own['state']='STOP_UNACCEPTED';own['terminal_unused_family_HOLD']=dict(UTC=stamp(),cohorts=[c for c in cohorts if c not in own['consumed']],family_states=family_states,no_budget_refund=True,no_spec_removal=True,no_model_retries=True)
      e.update_authority(stop_unused_future);event('PARTIAL_TERMINAL_UNUSED_FAMILY_HOLD',states=states,remaining_credits_preserved=current['remaining']);put(R/'analysis/EXECUTION_TERMINAL.json',dict(status='ALL_ACTUAL_MODELS_TERMINAL_WITH_UNUSED_FAMILY_HOLD',UTC=stamp(),states=states,remaining_credits_preserved=current['remaining'],budget=28,new_prepare_disabled=True,accepted_or_negative_only_from_actual_UUIDs=True),True);return
     if current['remaining']==0 and not running and not post and all(x in['PASS_PERFFIRST28_DH_STRICT_ARCHIVE_NATIVE_RESTORE','FAIL_PERFFIRST28_DH_ARCHIVED_NO_RETRY']for x in states.values()):
      event('ALL28_SCIENTIFIC_IDENTITIES_TERMINAL',states=states);put(R/'analysis/EXECUTION_TERMINAL.json',dict(status='ALL28_STRICT_OR_ARCHIVED_NEGATIVE_TERMINAL',UTC=stamp(),states=states,analysis_and_publication_pending=True),True);return
     previous=sample
    time.sleep(2)

EXPECTED28_COHORTS=['E2-DTCPF28-d984ea5475a581ad-DH-PHYS1024-V1', 'E2-DTCPF28-d984ea5475a581ad-DH-PIB192-V1', 'E2-DTCPF28-d984ea5475a581ad-DH-TAGSVC8-V1', 'E2-DTCPF28-fc0705ae3721e999-DH-PHYS1024-V1', 'E2-DTCPF28-fc0705ae3721e999-DH-PIB192-V1', 'E2-DTCPF28-fc0705ae3721e999-DH-TAGSVC8-V1', 'E2-DTCPF28-4114a3dc0d06b55b-DH-PHYS768-V1', 'E2-DTCPF28-4114a3dc0d06b55b-DH-PHYS1024-V1', 'E2-DTCPF28-4114a3dc0d06b55b-DH-PIB192-V1', 'E2-DTCPF28-4114a3dc0d06b55b-DH-TAGSVC8-V1', 'E2-DTCPF28-6df3a84b612086e8-DH-PHYS768-V1', 'E2-DTCPF28-6df3a84b612086e8-DH-PHYS1024-V1', 'E2-DTCPF28-6df3a84b612086e8-DH-PIB192-V1', 'E2-DTCPF28-6df3a84b612086e8-DH-TAGSVC8-V1', 'E2-DTCPF28-eededb785179fc04-DH-PHYS768-V1', 'E2-DTCPF28-eededb785179fc04-DH-PHYS1024-V1', 'E2-DTCPF28-eededb785179fc04-DH-PIB192-V1', 'E2-DTCPF28-eededb785179fc04-DH-TAGSVC8-V1', 'E2-DTCPF28-f437190767aaed49-DH-PHYS1024-V1', 'E2-DTCPF28-f437190767aaed49-DH-PIB192-V1', 'E2-DTCPF28-f437190767aaed49-DH-TAGSVC8-V1', 'E2-DTCPF28-ae34174fbbdf83b2-DH-PHYS1024-V1', 'E2-DTCPF28-ae34174fbbdf83b2-DH-PIB192-V1', 'E2-DTCPF28-ae34174fbbdf83b2-DH-TAGSVC8-V1', 'E2-DTCPF28-e7bb67e63e3c3847-DH-PHYS768-V1', 'E2-DTCPF28-e7bb67e63e3c3847-DH-PHYS1024-V1', 'E2-DTCPF28-e7bb67e63e3c3847-DH-PIB192-V1', 'E2-DTCPF28-e7bb67e63e3c3847-DH-TAGSVC8-V1']
