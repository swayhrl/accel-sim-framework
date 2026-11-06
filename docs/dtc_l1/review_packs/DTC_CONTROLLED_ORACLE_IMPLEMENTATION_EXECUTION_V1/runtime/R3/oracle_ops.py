"""One same-owner dispatch pool across two independent Oracle requests.

Main registers initial8 and starts run_scheduler once. A later registered
remaining24 calls attach_registered_request, never a second scheduler thread.
"""
from pathlib import Path
import concurrent.futures,datetime,fcntl,hashlib,json,os,subprocess,sys,threading,time,types
P=Path;R=P(__file__).resolve().parents[1];BASE=P('/root/data/dtc_controlled_oracle_20261106_v1');N=P('/root/data/ep_l2_dtc_l1_native_v2')
MARKER='DTC_CONTROLLED_ORACLE_SHARED_POOL_V1';PASS='PASS_CONTROLLED_ORACLE_DH_STRICT_ARCHIVE_NATIVE_RESTORE';NEG='FAIL_CONTROLLED_ORACLE_DH_ARCHIVED_NO_RETRY'
def rd(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def load(n,p):
 m=types.ModuleType(n);m.__file__=str(p);exec(compile(P(p).read_bytes(),str(p),'exec'),m.__dict__);return m
def put(p,v,exclusive=False):
 p=P(p);p.parent.mkdir(parents=True,exist_ok=True);b=(json.dumps(v,sort_keys=True,indent=2)+'\n').encode()
 if exclusive:
  with p.open('xb')as f:f.write(b);f.flush();os.fsync(f.fileno())
 else:
  t=p.with_name('.'+p.name+'.'+str(os.getpid())+'.'+str(threading.get_ident())+'.writing');t.write_bytes(b);os.replace(t,p)
def stamp():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def owner():
 assert sys.dont_write_bytecode and os.getpid()==1498278 and int(P('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19])==977758783
def attach_registered_request(stage_root):
 """Attach already registered context only; this call never launches a model."""
 owner();root=P(stage_root).resolve();assert root in [BASE/'initial8',BASE/'remaining24']
 main=sys.modules['__main__'];state=getattr(main,MARKER,None)
 if state is None:
  assert root==BASE/'initial8','INITIAL_OWNER_POOL_REQUIRED'
  state=dict(lock=threading.RLock(),contexts={},thread_ident=None,claims={});setattr(main,MARKER,state)
 with state['lock']:
  assert str(root)not in state['contexts'],'ALREADY_ATTACHED_NO_REAPPLY'
  e=load('oracle_private_engine_'+root.name,root/'tools/oracle_native.py');reg,ep,q,plan=e.registered();e.assert_parent_lease()
  assert plan['execution_root']==str(root)and plan['preparation_phase']=='SCIENCE_FINAL_FROZEN'and not plan.get('mock',False)
  build=rd(root/'control/BUILD_PROFILE.json')
  for old in state['contexts'].values():
   assert old['request']!=q['request']and all(old['build'][k]==build[k]for k in ['binary_sha256','core_commit','libcudart_sha256'])
   assert old['plan']['qualified_modes']==plan['qualified_modes'],'IMMUTABLE_BINARY_Q_REQUIRED'
   assert old['plan']['new_dispatcher_cpu_allowance']==plan['new_dispatcher_cpu_allowance'],'SHARED_POOL_CPU_ALLOWANCE_MUST_MATCH'
  ctx=dict(root=root,request=q['request'],plan=plan,build=build,e=e,res=load('oracle_private_resources_'+root.name,root/'tools/oracle_resources.py'),consumer=load('oracle_private_results_'+root.name,root/'tools/oracle_results.py'),points=rd(root/'control/MATRIX.fixed.json')['points'],cool={},errors={})
  assert plan['archive_workers']==1,'ONE_ACTUAL_ARCHIVE_WORKER_REQUIRED'
  assert len(ctx['points'])==q['budget']==plan['expected_new_starts'];state['contexts'][str(root)]=ctx
  if state.get('saveclaims')is not None:state['saveclaims']()
 return dict(status='REGISTERED_REQUEST_ATTACHED_ONE_OWNER_POOL',request=q['request'],execution_root=str(root),requests=len(state['contexts']))
def install_extension_callback(callback):
 """Called exactly once by S's initial addon on the existing Main thread."""
 owner();assert threading.current_thread()is threading.main_thread()
 state=getattr(sys.modules['__main__'],MARKER)
 with state['lock']:
  assert set(state['contexts'])=={str(BASE/'initial8')}and 'extension_callback'not in state
  first=state['contexts'][str(BASE/'initial8')];m=load('oracle_private_pendingcall',first['root']/'tools/oracle_pendingcall.py')
  state['extension_callback']=m.OnceMainCallback(callback);state['pendingcall_source_module']=m
 return dict(status='ONCE_MAINTHREAD_EXTENSION_CALLBACK_ARMED_NO_NEW_REQUEST_REGISTERED')
def sync_stage_reservation(ctx,claims):
 # Local file/proc projection and bounded SH occur OUTSIDE the actual EX
 # callback. It receives only captured numbers/fingerprint; no nested SH/FUSE.
 if 'reservation_module'not in ctx:ctx['reservation_module']=load('oracle_private_reservations_'+ctx['root'].name,ctx['root']/'tools/oracle_reservations.py')
 q=ctx['e'].authority()[0]['registered_future_requests'][ctx['request']]
 value=ctx['reservation_module'].compute_stage_reservation(ctx['root'],q,claims)
 put(ctx['root']/'control/DYNAMIC_NATIVE_RESERVATION.latest.json',value)
 if q['reserved_write_bytes']==value['reserved_write_bytes']:return value
 captured=value['reserved_write_bytes'];budget=q['budget'];admitted=dict(q['admitted_specs']);technical=q['maximum_source_plus_restore_lifetime_bytes']
 def update(current):
  own=current['registered_future_requests'][ctx['request']]
  assert own['budget']==budget and own['admitted_specs']==admitted and own['maximum_source_plus_restore_lifetime_bytes']==technical
  assert 0<=captured<=technical
  own['reserved_write_bytes']=captured
 ctx['e'].update_authority(update)
 return value

def run_scheduler():
 owner();assert threading.current_thread()is not threading.main_thread()
 main=sys.modules['__main__'];state=getattr(main,MARKER,None)
 if state is None:attach_registered_request(str(R));state=getattr(main,MARKER)
 with state['lock']:
  assert state['thread_ident']is None,'SECOND_SCIENTIFIC_DISPATCH_POOL_FORBIDDEN';state['thread_ident']=threading.get_ident()
 first=state['contexts'][str(BASE/'initial8')];mask=set(first['plan']['new_dispatcher_cpu_allowance'])
 assert mask and not mask&set(first['plan']['protected_cpu_ids']);os.sched_setaffinity(0,mask)
 running={};post={};reviews={};dispatch_index=0
 def key(ctx,c):return ctx['request']+':'+c
 def event(ctx,kind,**data):put(ctx['root']/'events'/(str(time.time_ns())+'_'+kind+'.json'),dict(UTC=stamp(),kind=kind,request=ctx['request'],**data),True)
 def saveclaims():
  with state['lock']:
   for ctx in state['contexts'].values():put(ctx['root']/'control/POOL_DISPATCH_RESERVATIONS.json',dict(claims={v['cohort']:v for v in state['claims'].values()if v['request']==ctx['request']}))
   put(BASE/'control/SHARED_POOL_DISPATCH_RESERVATIONS.json',dict(schema='DTC_CONTROLLED_ORACLE_SHARED_POOL_CLAIMS_V1',owner_pid=1498278,owner_start_ticks=977758783,claims=state['claims'],requests={c['request']:str(c['root'])for c in state['contexts'].values()}))
   for ctx in state['contexts'].values():sync_stage_reservation(ctx,{v['cohort']:v for v in state['claims'].values()if v['request']==ctx['request']})
 state['saveclaims']=saveclaims
 def pause(ctx,c,value):
  p=BASE/'control/ENGINEERING_PAUSE_NEW.json'
  if not p.exists():
   try:put(p,dict(request=ctx['request'],cohort=c,UTC=stamp(),result=value,no_healthy_model_signals=True,model_retries=0),True)
   except FileExistsError:pass
 def work(ctx,c):
  command=[str(N/'bin/experiment'),'prepare',c,'--project','DTC_L1']
  try:
   v=subprocess.run(command,capture_output=True,text=True);put(ctx['root']/'logs'/(c+'.PREPARE.'+str(time.time_ns())+'.json'),dict(argv=command,returncode=v.returncode,stdout=v.stdout,stderr=v.stderr),True)
   if v.returncode:return dict(state='ZERO_START_HOLD',cohort=c,error=(v.stderr or v.stdout)[-3000:])
   command[1]='run-native';v=subprocess.run(command,capture_output=True,text=True);put(ctx['root']/'logs'/(c+'.NATIVE.'+str(time.time_ns())+'.json'),dict(argv=command,returncode=v.returncode,stdout=v.stdout,stderr=v.stderr),True)
   if(ctx['root']/'control/qualification_ledger'/(c+'.DONE.json')).exists():return dict(state='EXECUTION_CLOSED',cohort=c)
   return dict(state='UNRESOLVED_EXECUTION',cohort=c,error=(v.stderr or v.stdout)[-3000:])
  except BaseException as error:return dict(state='UNRESOLVED_EXECUTION',cohort=c,error=repr(error))
 def review(ctx,c):
  tail=['--mode',c[5:]]if c.startswith('MODE:')else[c]
  v=subprocess.run(['/usr/bin/python3','-B',str(ctx['root']/'tools/oracle_actual_review_runner.py'),str(ctx['root']),*tail],capture_output=True,text=True,timeout=1800)
  put(ctx['root']/'logs'/(c+'.INDEPENDENT_REVIEW.'+str(time.time_ns())+'.json'),dict(returncode=v.returncode,stdout=v.stdout,stderr=v.stderr),True)
  return dict(cohort=c,returncode=v.returncode,stdout=v.stdout[-2000:],stderr=v.stderr[-2000:])
 with(BASE/'control/SHARED_DISPATCH_OWNER.lock').open('a+b')as held:
  fcntl.flock(held,fcntl.LOCK_EX|fcntl.LOCK_NB);put(BASE/'control/SHARED_DISPATCH_STARTED.json',dict(UTC=stamp(),pid=os.getpid(),start_ticks=977758783,thread_ident=threading.get_ident(),CPU_allowance=sorted(mask),single_dispatcher=True),True);saveclaims()
  with concurrent.futures.ThreadPoolExecutor(max_workers=min(128,len(mask)),thread_name_prefix='DTC_ORACLE_SHARED_MODEL')as workers,concurrent.futures.ThreadPoolExecutor(max_workers=1,thread_name_prefix='DTC_ORACLE_ARCHIVE')as archives,concurrent.futures.ThreadPoolExecutor(max_workers=1,thread_name_prefix='DTC_ORACLE_INDEPENDENT_CPU_REVIEW')as review_pool:
   while True:
    with state['lock']:contexts=list(state['contexts'].values())
    for ctx in contexts:ctx['e'].assert_parent_lease()
    for future,(ctx,c)in list(running.items()):
     if not future.done():continue
     value=future.result();running.pop(future);event(ctx,'MODEL_WORKER_RETURN',cohort=c,result=value)
     if value['state']=='EXECUTION_CLOSED':
      with state['lock']:state['claims'].pop(key(ctx,c),None);saveclaims()
      post[archives.submit(ctx['consumer'].safe_finish,c)]=(ctx,c)
     elif c not in ctx['e'].registered()[2]['consumed']:
      with state['lock']:state['claims'].pop(key(ctx,c),None);saveclaims()
      ctx['cool'][c]=time.monotonic()+30;ctx['errors'][c]=value
      if any(reason in value.get('error','')for reason in ['RESOURCE_HOLD','REGISTRY_SHARED_LOCK_BUSY','REGISTRY_EX_BUSY','REGISTRY_BUSY','WAIT_MODE_GATE2','WAIT_INDEPENDENT_ACTUAL_QUALIFIER_REVIEW']):event(ctx,'EXPECTED_ADMISSION_DEFERRAL_ZERO_START',cohort=c,error=value.get('error'))
      else:pause(ctx,c,value)
     else:ctx['errors'][c]=value;pause(ctx,c,value) # spent uncertain generation retains claim
    for future,(ctx,c)in list(post.items()):
     if not future.done():continue
     value=future.result();post.pop(future);event(ctx,'RESULT_CONSUMED',cohort=c,state=value['state']);saveclaims()
     if value['state']==PASS and c in set(ctx['plan']['initial_qualifiers'].values()):reviews[review_pool.submit(review,ctx,c)]=(ctx,c);ctx['cool']['review:'+c]=time.monotonic()+60
     elif value['state']not in[PASS,NEG]:ctx['errors'][c]=value;pause(ctx,c,value)
    for future,(ctx,c)in list(reviews.items()):
     if not future.done():continue
     try:event(ctx,'INDEPENDENT_QUALIFIER_REVIEW_RETURN',**future.result())
     except BaseException as error:ctx['errors'][c]=dict(reason='INDEPENDENT_REVIEW_ENGINEERING',error=repr(error));event(ctx,'FAMILY_RELEASE_HELD',cohort=c,error=repr(error))
     reviews.pop(future)
    sample=first['res'].sample_system();all_pending=[];states_by_request={};snapshots={}
    for ctx in contexts:
     q=ctx['e'].registered()[2];snapshots[ctx['request']]=q;root=ctx['root'];busy={key(k,c)for k,c in list(running.values())+list(post.values())};reviewbusy={key(k,c)for k,c in reviews.values()}
     for c,row in q['consumed'].items():
      claim=state['claims'].get(key(ctx,c))
      if claim:claim['uuid']=row['uuid']
      if row.get('execution_receipt')and key(ctx,c)not in busy and not(root/'analysis'/(c+'.RESULT.json')).exists()and time.monotonic()>=ctx['cool'].get('post:'+c,0):post[archives.submit(ctx['consumer'].safe_finish,c)]=(ctx,c);ctx['cool']['post:'+c]=time.monotonic()+60
      if c in set(ctx['plan']['initial_qualifiers'].values())and key(ctx,c)not in reviewbusy and(root/'analysis'/(c+'.RESULT.json')).exists()and rd(root/'analysis'/(c+'.RESULT.json'))['state']==PASS and not(root/'control/actual_qualification_reviews'/(c+'.json')).exists()and time.monotonic()>=ctx['cool'].get('review:'+c,0):reviews[review_pool.submit(review,ctx,c)]=(ctx,c);ctx['cool']['review:'+c]=time.monotonic()+60
     if ctx['plan']['stage']=='initial8':
      for mode in ctx['plan']['qualified_modes']:
       subject='MODE:'+mode;members=[p for p in ctx['points']if p['mode']in[mode,'OFF_MATCHED']]
       if key(ctx,subject)in reviewbusy or P(ctx['plan']['mode_gate2_reviews'][mode]).exists()or time.monotonic()<ctx['cool'].get('review:'+subject,0):continue
       if len(members)==16 and all((root/'analysis'/(p['cohort']+'.RESULT.json')).exists()and rd(root/'analysis'/(p['cohort']+'.RESULT.json'))['state']==PASS for p in members)and all((root/'control/actual_qualification_reviews'/(ctx['plan']['initial_qualifiers'][m]+'.json')).exists()for m in[mode,'OFF_MATCHED']):
        reviews[review_pool.submit(review,ctx,subject)]=(ctx,subject);ctx['cool']['review:'+subject]=time.monotonic()+60
     gates={}
     if not(BASE/'control/ENGINEERING_PAUSE_NEW.json').exists()and not(BASE/'control/POOL_STOP_NEW.json').exists():
      for point in ctx['points']:
       c=point['cohort']
       if c in q['consumed']or key(ctx,c)in state['claims']or time.monotonic()<ctx['cool'].get(c,0):continue
       try:
        spec=ctx['e'].canonical(c)
        if ctx['res'].admission_hold(q,spec)is not None:gates[c]='TYPED_MODE_HOLD';continue
        gates[c]=ctx['res'].verify_initial_runtime_gate(ctx['plan'],c,q);all_pending.append((ctx,spec))
       except ctx['res'].WaitInitialRuntimeGate as wait:gates[c]=str(wait)
       except BaseException as error:gates[c]=repr(error);ctx['errors'][c]=dict(reason='MODE_QUALIFICATION_GATE_FAILED',error=repr(error))
     states={p['cohort']:rd(root/'analysis'/(p['cohort']+'.RESULT.json'))['state']if(root/'analysis'/(p['cohort']+'.RESULT.json')).exists()else'PENDING'for p in ctx['points']};states_by_request[ctx['request']]=states
     put(root/'analysis/BATCH_STATE.json',dict(UTC=stamp(),request=ctx['request'],budget=q['budget'],consumed=len(q['consumed']),remaining=q['remaining'],running=[c for k,c in running.values()if k is ctx],postprocess=[c for k,c in post.values()if k is ctx],independent_reviews=[c for k,c in reviews.values()if k is ctx],states=states,gates=gates,errors=ctx['errors'],same_owner_shared_pool=True,no_extra_model_retries=True))
    callback=state.get('extension_callback')
    if callback is not None:
     if callback.snapshot()['state']=='ARMED':
      for mode in first['plan']['qualified_modes']:
       try:
        evidence=first['res'].verify_mode_extension_receipt(first['plan'],mode)
        queue=callback.queue_once();event(first,'AUTHORIZED_GATE2_MAINTHREAD_HANDOFF_QUEUED',mode=mode,evidence=evidence,queue=queue);break
       except first['res'].WaitInitialRuntimeGate:pass
     put(BASE/'control/EXTENSION_CALLBACK_STATUS.json',callback.snapshot())
    # One global pending list and RAM/CPU claim dictionary across both requests.
    for _ in range(min(128,len(mask))-len(running)):
     if not all_pending or(BASE/'control/ENGINEERING_PAUSE_NEW.json').exists()or(BASE/'control/POOL_STOP_NEW.json').exists():break
     decision=first['res'].choose_dispatch([s for _,s in all_pending],sample,state['claims'],policy=rd(first['root']/'control/RESOURCE_POLICY.json'),dispatch_index=dispatch_index)
     if decision is None:break
     ctx,spec=next((k,s)for k,s in all_pending if s['cohort']==decision['cohort']);c=spec['cohort'];fresh=ctx['res'].resources(spec,True)
     if not all(fresh[k]for k in ['physical_RAM_pass','physical_disk_pass','admission_disk_pass','admission_pressure_pass']):event(ctx,'RESOURCE_HOLD_NO_START',cohort=c,sample=fresh);all_pending=[(k,s)for k,s in all_pending if s['cohort']!=c];continue
     cpu=decision['host_cpu'];db=ctx['root']/'control/dispatch_bindings'/(c+'.json')
     if db.exists():
      b=rd(db);assert b['canonical_spec_sha256']==sha(ctx['root']/'control/specs'/(c+'.json'))
      if b['host_cpu']not in mask or b['host_cpu']in({x['host_cpu']for x in state['claims'].values()}|{cpu for x in sample['observed_affinity_claims']for cpu in x['cpus']}):all_pending=[(k,s)for k,s in all_pending if s['cohort']!=c];continue
      cpu=b['host_cpu']
     else:put(db,dict(cohort=c,canonical_spec_sha256=sha(ctx['root']/'control/specs'/(c+'.json')),host_cpu=cpu,resolved_spec_sha256=ctx['e'].jsonsha(dict(spec,host_cpu=cpu))),True)
     with state['lock']:
      state['claims'][key(ctx,c)]=dict(request=ctx['request'],execution_root=str(ctx['root']),cohort=c,host_cpu=cpu,uuid=None,workload=spec['workload'],predicted_peak_RAM_bytes=decision['predicted_peak_RAM_bytes'],result_cap_bytes=spec['limits']['max_result_directory_bytes'],RAM_cap_bytes=spec['limits']['max_process_tree_rss_bytes'],observed_model=False);saveclaims()
     charged=ctx['res'].resources(spec,True)
     if not all(charged[k]for k in ['physical_RAM_pass','physical_disk_pass','admission_disk_pass','admission_pressure_pass']):
      with state['lock']:state['claims'].pop(key(ctx,c),None);saveclaims()
      event(ctx,'POSTCLAIM_RESOURCE_HOLD_ZERO_CONSUME',cohort=c,resource_sample=charged);all_pending=[(k,s)for k,s in all_pending if s['cohort']!=c];continue
     running[workers.submit(work,ctx,c)]=(ctx,c);dispatch_index+=1;event(ctx,'DISPATCH_AUTHORIZED_UNUSED_IDENTITY',cohort=c,cpu=cpu);all_pending=[(k,s)for k,s in all_pending if s['cohort']!=c];sample=first['res'].sample_system()
    put(BASE/'control/SHARED_POOL_STATUS.json',dict(UTC=stamp(),owner_pid=1498278,owner_start_ticks=977758783,requests={k:dict(budget=q['budget'],remaining=q['remaining'],consumed=len(q['consumed']))for k,q in snapshots.items()},running=[dict(request=k['request'],cohort=c)for k,c in running.values()],archive_jobs=len(post),independent_reviews=len(reviews),claims=len(state['claims']),single_dispatcher=True))
    terminal=not running and not post and not reviews and all(q['remaining']==0 and all(v in[PASS,NEG]for v in states_by_request[k].values())for k,q in snapshots.items())
    if terminal and(len(contexts)==2 or(BASE/'control/POOL_STOP_NEW.json').exists()):put(BASE/'control/SHARED_POOL_EXECUTION_TERMINAL.json',dict(status='ALL_ATTACHED_REGISTERED_ORACLE_IDENTITIES_TERMINAL',UTC=stamp(),states=states_by_request,independent_final_closeout_pending=True),True);return
    time.sleep(2) # wait for legal extension attach without resetting old request
