"""Finite16 physical x PIB dispatch under the existing DTC lease PID. No extension/reset/model retry."""
from pathlib import Path
import json,os,time,hashlib,importlib.util,concurrent.futures,fcntl,datetime,zlib,threading
P=Path;R=P('/root/data/dtc_perf_first_v2_codesign16_layout_r1_20261105_v1');N=P('/root/data/ep_l2_dtc_l1_native_v2');A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_perf_first_v2_codesign16_layout_r1_execution_20261105_v1')
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
TERMINAL=('PASS_PERFV2_CODESIGN16_LAYOUT_R1_DH_STRICT_ARCHIVE_NATIVE_RESTORE','FAIL_PERFV2_CODESIGN16_LAYOUT_R1_DH_ARCHIVED_NO_RETRY')
def validate_profile_hold_decision(path,points,resources):
 decision=rd(path);profile=decision['profile']
 assert decision['schema']=='DTC_PERFV2_CODESIGN16_LAYOUT_R1_PROFILE_HOLD_DECISION_V1'
 assert decision['request']==resources.REQ and decision['authority_commit']==resources.AUTHORITY_COMMIT
 assert profile in resources.VARIANT_TOKENS and decision['classification']=='CONFIGURATION_OR_LIFECYCLE_SAFETY_HOLD'
 assert decision['decided_by']=='DTC_MAIN'and decision['reason']and decision['created_utc']
 expected={x['cohort']for x in points if x['profile']==profile}
 assert len(expected)==8 and len(decision['approval_scope']['candidate_cohorts'])==8 and set(decision['approval_scope']['candidate_cohorts'])==expected
 assert decision['approval_scope']['request']==resources.REQ and decision['approval_scope']['profile']==profile
 assert sha(decision['evidence_path'])==decision['evidence_sha256'],'ROOT_HOLD_EVIDENCE_DRIFT'
 return dict(profile=profile,request=resources.REQ,classification=decision['classification'],reason=decision['reason'],evidence_path=decision['evidence_path'],evidence_sha256=decision['evidence_sha256'],decided_by=decision['decided_by'],created_utc=decision['created_utc'],decision_path=str(path),decision_sha256=sha(path),source_ops_sha256=sha(__file__))

def consume_profile_hold_decisions(engine,points,resources):
 directory=R/'control/PROFILE_HOLD_DECISIONS'
 if not directory.exists():return
 for path in sorted(directory.glob('*.json')):
  value=validate_profile_hold_decision(path,points,resources);current=engine.registered()[2];existing=current.get('admission_holds',{}).get(value['profile'])
  if existing is not None:
   assert existing==value,'EXISTING_PROFILE_HOLD_IS_IMMUTABLE';continue
  def append_only(reg,value=value):
   own=reg['registered_future_requests'][engine.REQ];assert own['budget']==16 and own['remaining']==16-len(own['consumed'])
   assert value['profile']not in own.get('admission_holds',{}),'PROFILE_HOLD_CONCURRENT_CHANGE'
   own.setdefault('admission_holds',{})[value['profile']]=value
  engine.update_authority(append_only)

def unused_hold_status(q,points,resources):
 holds={}
 for point in points:
  if point['cohort']not in q['consumed']:
   value=resources.admission_hold(q,point)
   if value is not None:holds[point['cohort']]=value
 return holds

def terminal_unused_ready(q,states,cohorts,unused_holds,running_n,post_n):
 assert q['budget']==16 and q['remaining']==16-len(q['consumed'])
 assert len(set(cohorts))==16 and set(q['consumed'])<=set(cohorts)
 return q['remaining']>0 and running_n==post_n==0 and all(states[c]in TERMINAL for c in q['consumed'])and all(c in unused_holds for c in cohorts if c not in q['consumed'])

def run_scheduler():
 import subprocess
 assert __import__('sys').dont_write_bytecode,'CALLER_MUST_DISABLE_BYTECODE_WRITES_BEFORE_SCHEDULER'
 assert os.getpid()==1498278 and int(P('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19])==977758783
 plan=rd(R/'control/EXECUTION_PLAN.json');mask=plan['new_dispatcher_cpu_allowance'];assert mask and len(set(mask))==len(mask)and threading.current_thread()is not threading.main_thread()
 assert not(set(mask)&({2,258}|set(range(32,64))|set(range(288,320)))),'PROTECTED_GES_MAIN_CPU_OVERLAP'
 os.sched_setaffinity(0,set(mask));assert set(os.sched_getaffinity(0))==set(mask)
 e=load('perf16r1_owner_engine',R/'tools/perf16r1_native.py');res=load('perf16r1_owner_resources',R/'tools/perf16r1_resources.py');consumer=load('perf16r1_owner_results',R/'tools/perf16r1_results.py');e.assert_parent_lease();points=rd(R/'control/MATRIX.fixed.json')['points'];cohorts=[x['cohort']for x in points];assert len(cohorts)==len(set(cohorts))==16 and set(cohorts)==set(EXPECTED16_COHORTS)
 assert {x['program']for x in points}=={'2DCONV','GEMM','convolutionSeparable','scan','ATAX','MVT','BICG','vectorAdd'}
 assert all(x['cohort'].startswith('E2-DTCPFV2R1-')for x in points)
 sample=res.sample_system();max_workers=min(16,max(1,len(sample['cpu_allowed'])-2));claims={};running={};post={};cool={};errors={};lock=threading.RLock();previous=None;dispatch_index=0
 def saveclaims():put(R/'control/POOL_DISPATCH_RESERVATIONS.json',dict(claims=claims))
 def event(kind,**data):put(A/'events'/(str(time.time_ns())+'_'+kind+'.json'),dict(UTC=stamp(),kind=kind,**data),True)
 def pause_unknown(cohort,result):
  path=R/'control/ENGINEERING_PAUSE_NEW.json'
  if not path.exists():put(path,dict(schema='DTC_PERFV2_CODESIGN16_LAYOUT_R1_UNKNOWN_ENGINEERING_PAUSE_NEW_V1',request=e.REQ,UTC=stamp(),cohort=cohort,result=result,classification='UNKNOWN_ENGINEERING_DIAGNOSTIC_REQUIRED',source_ops_sha256=sha(__file__),no_scientific_safety_inference=True,no_healthy_model_signals=True),True)
 def work(c):
  try:
   cmd=[str(N/'bin/experiment'),'prepare',c,'--project','DTC_L1'];x=subprocess.run(cmd,capture_output=True,text=True);put(R/'logs'/(c+'.PREPARE.'+str(time.time_ns())+'.json'),dict(returncode=x.returncode,stdout=x.stdout,stderr=x.stderr),True)
   if x.returncode:
    current=e.registered()[2]
    if c not in current['consumed']and res.admission_hold(current,e.canonical(c))is not None:return dict(state='UNUSED_SAFETY_HOLD',cohort=c,uuid=None,cycles=None,scientific_model_starts=0)
    return dict(state='ZERO_START_HOLD',error=x.stderr[-3000:])
   cmd[1]='run-native';x=subprocess.run(cmd,capture_output=True,text=True);put(R/'logs'/(c+'.NATIVE_COMMAND.'+str(time.time_ns())+'.json'),dict(returncode=x.returncode,stdout=x.stdout,stderr=x.stderr),True)
   dp=R/'control/qualification_ledger'/(c+'.DONE.json')
   if dp.exists():return dict(state='EXECUTION_CLOSED',cohort=c)
   q=e.registered()[2];return dict(state='SPENT_ENGINEERING_HOLD'if c in q['consumed']else'ZERO_START_HOLD',cohort=c,error=(x.stderr or x.stdout)[-3000:])
  except BaseException as error:
   try:spent=c in e.registered()[2]['consumed']
   except BaseException:spent=True
   return dict(state='SPENT_ENGINEERING_HOLD'if spent else'ZERO_START_HOLD',cohort=c,error=repr(error))
 with(R/'control/DISPATCH_OWNER.lock').open('a+b')as held:
  fcntl.flock(held,fcntl.LOCK_EX|fcntl.LOCK_NB);put(R/'control/DISPATCH_STARTED.json',dict(UTC=stamp(),pid=os.getpid(),start_ticks=977758783,thread_ident=threading.get_ident(),finite16_only=True,max_workers=max_workers,owner_allowed_cpus=sample['cpu_allowed'],no_second_OS_controller=True),True)
  with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers,thread_name_prefix='DTCPFV216_MODEL')as pool,concurrent.futures.ThreadPoolExecutor(max_workers=2,thread_name_prefix='DTCPFV216_ARCHIVE')as archives:
   while True:
    e.assert_parent_lease();q=e.registered()[2]
    with lock:
     for f,c in list(running.items()):
      if not f.done():continue
      v=f.result();running.pop(f);claims.pop(c,None);saveclaims();event('WORKER_RETURN',cohort=c,result=v)
      if v['state']=='EXECUTION_CLOSED':post[archives.submit(consumer.safe_finish,c)]=c
      elif v['state']=='UNUSED_SAFETY_HOLD':event('TYPED_UNUSED_HOLD_NO_MODEL_NO_GLOBAL_PAUSE',cohort=c)
      elif v['state']=='ZERO_START_HOLD':cool[c]=time.monotonic()+60;errors[c]=v;pause_unknown(c,v)
      else:errors[c]=v;put(R/'analysis'/(c+'.ENGINEERING_HOLD.json'),v);pause_unknown(c,v)
     for f,c in list(post.items()):
      if not f.done():continue
      v=f.result();post.pop(f);event('POSTPROCESS_RETURN',cohort=c,state=v['state'])
      if v['state']not in['PASS_PERFV2_CODESIGN16_LAYOUT_R1_DH_STRICT_ARCHIVE_NATIVE_RESTORE','FAIL_PERFV2_CODESIGN16_LAYOUT_R1_DH_ARCHIVED_NO_RETRY']:errors[c]=v;pause_unknown(c,v)
     # Only same-UUID evidence work can be reconsumed; never retry a model.
     busy=set(post.values())
     for c,row in q['consumed'].items():
      if row.get('execution_receipt')and c not in busy and c not in running.values()and not(R/'analysis'/(c+'.RESULT.json')).exists()and time.monotonic()>=cool.get('post:'+c,0):post[archives.submit(consumer.safe_finish,c)]=c;cool['post:'+c]=time.monotonic()+60
     try:
      consume_profile_hold_decisions(e,points,res);q=e.registered()[2];unused_holds=unused_hold_status(q,points,res)
     except(AssertionError,KeyError,OSError,ValueError,TypeError)as error:
      pause_unknown(None,dict(reason='ROOT_PROFILE_DECISION_NOT_YET_QUALIFIED',error=repr(error)));q=e.registered()[2];unused_holds={}
     sample=res.sample_system();put(R/'control/RESOURCE_OBSERVER.json',sample);pending=[]
     if not(R/'control/ENGINEERING_PAUSE_NEW.json').exists():
      try:pending=[e.canonical(c)for c in cohorts if c not in q['consumed']and c not in unused_holds and c not in claims and time.monotonic()>=cool.get(c,0)]
      except(AssertionError,KeyError,OSError,ValueError,TypeError)as error:pause_unknown(None,dict(reason='CANDIDATE_IDENTITY_OR_CONFIGURATION_UNRESOLVED',error=repr(error)));pending=[]
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
     states={c:rd(R/'analysis'/(c+'.RESULT.json'))['state']if(R/'analysis'/(c+'.RESULT.json')).exists()else('UNUSED_SAFETY_HOLD'if c in unused_holds else'PENDING')for c in cohorts}
     current=e.registered()[2];status=dict(UTC=stamp(),request=e.REQ,budget=16,consumed=len(current['consumed']),remaining=current['remaining'],running=list(running.values()),postprocess=list(post.values()),preclaim_resource_holds=res.preclaim_diagnostics(),claims=len(claims),states=states,unused_safety_HOLD=unused_holds,engineering_pause_new=(R/'control/ENGINEERING_PAUSE_NEW.json').exists(),errors=errors,source_scope='EXACT_AUTHORIZED_V2_PHYSICAL_PIB_COMBO16_ONLY',Tag_never_started=True,no_new_Core_or_trace=True,additional_experiments_released=False)
     put(R/'analysis/BATCH_STATE.json',status);put(A/'LATEST_EXECUTION_STATUS.json',status)
     if terminal_unused_ready(current,states,cohorts,unused_holds,len(running),len(post)):
      def stop_unused_future(reg):
       own=reg['registered_future_requests'][e.REQ];assert own['budget']==16 and own['remaining']==16-len(own['consumed'])and set(own['consumed'])==set(current['consumed'])
       fresh=unused_hold_status(own,points,res);assert all(c in fresh for c in cohorts if c not in own['consumed'])
       own['state']='STOP_UNACCEPTED_WITH_UNUSED_CREDITS';own['terminal_unused_safety_HOLD']=dict(UTC=stamp(),cohorts=list(fresh),remaining_credits_preserved=own['remaining'],no_budget_refund=True,no_spec_removal=True,no_model_retries=True)
      e.update_authority(stop_unused_future);event('TERMINAL_WITH_TYPED_UNUSED_SAFETY_HOLD',states=states,remaining_credits_preserved=current['remaining']);put(R/'analysis/EXECUTION_TERMINAL.json',dict(status='ALL_ACTUAL_MODELS_TERMINAL_WITH_UNUSED_SAFETY_HOLD',UTC=stamp(),states=states,remaining_credits_preserved=current['remaining'],budget=16,new_prepare_disabled=True,unused_safety_HOLD=unused_holds),True);return
     if current['remaining']==0 and not running and not post and all(x in['PASS_PERFV2_CODESIGN16_LAYOUT_R1_DH_STRICT_ARCHIVE_NATIVE_RESTORE','FAIL_PERFV2_CODESIGN16_LAYOUT_R1_DH_ARCHIVED_NO_RETRY']for x in states.values()):
      event('ALL16_SCIENTIFIC_IDENTITIES_TERMINAL',states=states);put(R/'analysis/EXECUTION_TERMINAL.json',dict(status='ALL16_STRICT_OR_ARCHIVED_NEGATIVE_TERMINAL',UTC=stamp(),states=states,analysis_and_publication_pending=True),True);return
     previous=sample
    time.sleep(2)

EXPECTED16_COHORTS=['E2-DTCPFV2R1-d984ea5475a581ad-DH-PHYS768-OOPIB192-V1', 'E2-DTCPFV2R1-d984ea5475a581ad-DH-PHYS1024-OOPIB192-V1', 'E2-DTCPFV2R1-fc0705ae3721e999-DH-PHYS768-OOPIB192-V1', 'E2-DTCPFV2R1-fc0705ae3721e999-DH-PHYS1024-OOPIB192-V1', 'E2-DTCPFV2R1-4114a3dc0d06b55b-DH-PHYS768-OOPIB192-V1', 'E2-DTCPFV2R1-4114a3dc0d06b55b-DH-PHYS1024-OOPIB192-V1', 'E2-DTCPFV2R1-6df3a84b612086e8-DH-PHYS768-OOPIB192-V1', 'E2-DTCPFV2R1-6df3a84b612086e8-DH-PHYS1024-OOPIB192-V1', 'E2-DTCPFV2R1-eededb785179fc04-DH-PHYS768-OOPIB192-V1', 'E2-DTCPFV2R1-eededb785179fc04-DH-PHYS1024-OOPIB192-V1', 'E2-DTCPFV2R1-f437190767aaed49-DH-PHYS768-OOPIB192-V1', 'E2-DTCPFV2R1-f437190767aaed49-DH-PHYS1024-OOPIB192-V1', 'E2-DTCPFV2R1-ae34174fbbdf83b2-DH-PHYS768-OOPIB192-V1', 'E2-DTCPFV2R1-ae34174fbbdf83b2-DH-PHYS1024-OOPIB192-V1', 'E2-DTCPFV2R1-e7bb67e63e3c3847-DH-PHYS768-OOPIB192-V1', 'E2-DTCPFV2R1-e7bb67e63e3c3847-DH-PHYS1024-OOPIB192-V1']
