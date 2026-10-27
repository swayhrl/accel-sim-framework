"""One parent-owner dispatcher; dynamic throughput, exact starts, additive authorized search."""
import pathlib,json,hashlib,importlib.util,subprocess,time,concurrent.futures,os,uuid,threading
P=pathlib.Path;R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1');N=P('/root/data/ep_l2_dtc_l1_native_v2');G=1024**3
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def load(n,f):
 s=importlib.util.spec_from_file_location(n,R/'tools'/f);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def put(p,x,exclusive=False):
 p=P(p);p.parent.mkdir(parents=True,exist_ok=True)
 if exclusive:
  with p.open('x')as h:json.dump(x,h,indent=2);h.write('\n');h.flush();os.fsync(h.fileno())
 else:
  tmp=p.with_name('.'+p.name+'.'+str(os.getpid())+'.L2OPS');tmp.write_text(json.dumps(x,indent=2)+'\n');tmp.replace(p)
def event(state,**kw):
 with(R/'logs/EVENTS.jsonl').open('a')as h:h.write(json.dumps(dict(state=state,monotonic=time.monotonic(),**kw))+'\n')
def worker(c):
 engine=load('l2_worker_engine','l2_native.py');engine.assert_parent_lease();ip=R/'control/qualification_ledger'/(c+'.INTENT.json');assert not ip.exists();token=uuid.uuid4().hex
 for stage in ['prepare','run-native']:
  r=subprocess.run([str(N/'bin/experiment'),stage,c,'--project','DTC_L1'],capture_output=True,text=True);put(R/'logs'/(c+'.'+stage+'.'+token+'.json'),dict(returncode=r.returncode,stdout=r.stdout,stderr=r.stderr),True)
  if r.returncode:
   if not ip.exists()and c not in engine.registered()[2]['consumed']:
    reason=r.stderr
    return dict(state='ZERO_START_DEFERRED'if 'RESOURCE_HOLD'in reason else'ZERO_START_ENGINEERING',cohort=c,error=reason,model_starts=0)
   return dict(state='SPENT_ENGINEERING_PRESERVE',cohort=c,error=r.stderr,model_retries=0)
 return dict(state='EXECUTION_CLOSED',cohort=c)
def safe(c):
 try:return worker(c)
 except BaseException as x:return dict(state='ENGINEERING_PRESERVE',cohort=c,error=repr(x),model_retries=0)
def run_scheduler():
 engine=load('l2_schedule_engine','l2_native.py');res=load('l2_schedule_resources','l2_resources.py');consumer=load('l2_schedule_results','l2_results.py');adaptive=load('l2_schedule_adaptive','l2_adaptive.py');registry=load('l2_schedule_registry','l2_registry.py')
 claims={};running={};post={};cool={};errors={};previous=None;dispatch_index=0;last_summary=last_adaptive=last_history=0
 sample=res.sample_system();max_workers=max(1,min(len(sample['cpu_allowed']),int(sample.get('cpu_quota_equivalent')or len(sample['cpu_allowed']))));pool=concurrent.futures.ThreadPoolExecutor(max_workers=max_workers,thread_name_prefix='L2MLP');archive_pool=concurrent.futures.ThreadPoolExecutor(max_workers=4,thread_name_prefix='L2MLP_ARCHIVE');canaries=read(R/'control/CANARY_PLAN.json')['cohorts'];broad=False
 put(R/'control/SCHEDULER_STARTED.json',dict(parent_pid=os.getpid(),worker_capacity_from_actual_CPU_quota=max_workers,canaries=canaries,no_model_total_cap=True),True)
 def saveclaims():put(R/'control/POOL_DISPATCH_RESERVATIONS.json',dict(claims=claims))
 try:
  while True:
   assert not(R/'control/ABORT').exists()
   for future,c in list(post.items()):
    if not future.done():continue
    value=future.result();post.pop(future);event(value['state'],cohort=c)
    if value['state']not in ['PASS_L2MLP_STRICT_ARCHIVE_NATIVE_RESTORE','FAIL_L2MLP_ARCHIVED_NO_RETRY']:
     errors[c]=value;put(R/'analysis'/(c+'.POSTPROCESS_PENDING.json'),value)
   for future,c in list(running.items()):
    if not future.done():continue
    value=future.result();running.pop(future);row=engine.registered()[2]['consumed'].get(c)
    if row and 'execution_receipt'not in row:
     errors[c]=value;put(R/'analysis'/(c+'.ENGINEERING_GUARD.json'),value);continue
    claims.pop(c,None);saveclaims();event(value['state'],cohort=c)
    if value['state']=='EXECUTION_CLOSED':post[archive_pool.submit(consumer.safe_finish,c)]=c
    elif value['state']=='ZERO_START_DEFERRED':cool[c]=time.monotonic()+30
    elif value['state']=='ZERO_START_ENGINEERING':errors[c]=value;cool[c]=time.monotonic()+300;put(R/'analysis'/(c+'.ZERO_START_ENGINEERING.json'),value)
    elif value['state']not in ['PASS_L2MLP_STRICT_ARCHIVE_NATIVE_RESTORE','FAIL_L2MLP_ARCHIVED_NO_RETRY']:
     errors[c]=value;put(R/'analysis'/(c+'.POSTPROCESS_PENDING.json'),value)
   sample=res.sample_system();sample['previous_sample']={k:previous[k]for k in ['monotonic','host_pswpout_pages','cgroup_memory_events','cgroup_cpu_stat']if previous and k in previous}if previous else None;put(R/'control/RESOURCE_OBSERVER.json',sample)
   actual_cpus={cpu for p in sample['observed_models']for cpu in p['cpus']}
   for v in claims.values():v['observed_model']=v['host_cpu']in actual_cpus
   now=time.monotonic();matrix=read(R/'control/MATRIX_CURRENT.json');reg,ep,q,plan=engine.registered();history=read(R/'control/HISTORICAL_RSS.json')
   if now-last_history>30:
    known={x.get('receipt_path')for x in history['records']}
    for c,row in q['consumed'].items():
     dp=R/'control/qualification_ledger'/(c+'.DONE.json')
     if not dp.exists()or str(dp)in known:continue
     d=read(dp);s=read(R/'control/specs'/(c+'.json'));history['records'].append(dict(receipt_path=str(dp),receipt_sha256=sha(dp),cohort=c,workload=s['workload'],program=s['program'],cell=s['cell'],rss=d['peak_observed_rss_bytes'],elapsed=d['elapsed_seconds'],success=d['launcher_wait_returncode']==0 and d['stop_reason']is None,core_commit=s['core_commit']))
    put(R/'control/HISTORICAL_RSS.json',history);last_history=now
   if not broad:
    state={c:read(R/'analysis'/(c+'.RESULT.json'))['state']if(R/'analysis'/(c+'.RESULT.json')).exists()else None for c in canaries}
    if all(v=='PASS_L2MLP_STRICT_ARCHIVE_NATIVE_RESTORE'for v in state.values()):
     broad=True;put(R/'control/ACTUAL_CANARY_QUALIFICATION.json',dict(status='PASS_ALL_CANARY_NATIVE_STRICT_ARCHIVE_RESTORE',cohorts=canaries,result_sha256={c:sha(R/'analysis'/(c+'.RESULT.json'))for c in canaries},automatic_broad_admission=True),True)
   pending=[]
   for p in matrix['points']:
    c=p['cohort']
    if c not in q['admitted_specs']or c in q['consumed']or c in claims or cool.get(c,0)>now:continue
    if not broad and c not in canaries:continue
    if p['program']=='cutcp':
     cut=[(pp,rr)for pp,rr in q['consumed'].items()if 'E2-DTCL2MLP-'+p['input_digest'][:16]+'-'in pp]
     measured=any('execution_receipt'in rr for _,rr in cut)
     if not measured and(p['cell']!='DH'or p['profile']!='P0'or cut):continue
    spec=engine.canonical(c);pending.append(spec)
   # Multiple fits use serialized in-memory claims; every actual native prepare
   # independently rechecks registry, source and physical admission.
   for _ in range(max_workers-len(claims)):
    decision=res.choose_dispatch(pending,sample,claims,history,previous,read(R/'control/RESOURCE_POLICY.json'),dispatch_index)
    if decision is None:break
    c=decision['cohort'];registry.refresh_pending_resource_spec(c,history);spec=engine.canonical(c)
    db=R/'control/dispatch_bindings'/(c+'.json')
    if db.exists():
     binding=read(db)
     if binding['host_cpu']not in res.cpu_candidates(sample,claims,previous):pending=[s for s in pending if s['cohort']!=c];continue
    else:
     resolved=dict(spec,host_cpu=decision['host_cpu']);binding=dict(cohort=c,canonical_spec_sha256=sha(R/'control/specs'/(c+'.json')),host_cpu=decision['host_cpu'],resolved_spec_sha256=engine.jsonsha(resolved));put(db,binding,True)
    claims[c]=dict(host_cpu=binding['host_cpu'],workload=spec['workload'],predicted_peak_RAM_bytes=spec['estimated_peak_model_RAM_bytes'],result_cap_bytes=spec['limits']['max_result_directory_bytes'],RAM_cap_bytes=spec['limits']['max_process_tree_rss_bytes'],observed_model=False);saveclaims();running[pool.submit(safe,c)]=c;dispatch_index+=1;event('DISPATCH_NEW_AUTHORIZED_IDENTITY',cohort=c,cpu=binding['host_cpu'],canary=not broad);pending=[s for s in pending if s['cohort']!=c]
   if now-last_summary>20:
    summary=consumer.summary();last_summary=now
    put(R/'analysis/BATCH_STATE.json',dict(spent=len(q['consumed']),registered_finite_budget=q['budget'],remaining=q['remaining'],running=list(running.values()),postprocess=list(post.values()),canary_phase=not broad,active_claims=len(claims),errors=errors,dynamic_memory_budget_fraction=.88,sole_owner_pid=os.getpid()))
   if broad and not running and not post and not pending and now-last_adaptive>60:
    summary=consumer.summary();search=adaptive.recommend(summary,matrix,read(R/'control/SEARCH_HISTORY.json'));put(R/'analysis/ADAPTIVE_DECISIONS.json',search);last_adaptive=now
    for proposal in search['proposals']:registry.extend(proposal)
    if search.get('scientific_stage_complete')and search.get('adoption_ready'):
     put(R/'analysis/FINAL_STATUS.json',dict(status='AUTHORIZED_L2_MLP_SEARCH_COMPLETE',decisions=search,source_hashes=engine.binding()),True);return
   previous=sample;time.sleep(2)
 finally:pool.shutdown(wait=True);archive_pool.shutdown(wait=True)
