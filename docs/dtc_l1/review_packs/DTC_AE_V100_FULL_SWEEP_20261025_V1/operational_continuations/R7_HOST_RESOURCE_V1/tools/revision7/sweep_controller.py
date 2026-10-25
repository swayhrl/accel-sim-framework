"""Finite continuation: adopt all spent attempts; only original unused starts.

Retired parent control does not terminate/relaunch an existing native frontend
or simulator. A preserved live attempt is watched through its original DONE.
"""
import pathlib,json,hashlib,importlib.util,os,fcntl,time,datetime,subprocess,concurrent.futures,copy
P=pathlib.Path;T=P('/root/data/dtc_main_v100_sweep_20261025_v1');N=P('/root/data/ep_l2_dtc_l1_native_v2');REQ='DTC_AE_V100_FULL_SWEEP_20261025_V1'
OK={'PASS_STRICT_ARCHIVE_NATIVE_RESTORE','FAIL_CLOSED_UNACCEPTED_ARCHIVED_NO_RETRY'}
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def write(p,r,exclusive=False):
 p=P(p);p.parent.mkdir(parents=True,exist_ok=True)
 if exclusive:
  with p.open('x') as f:json.dump(r,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 else:
  tmp=p.with_name(p.name+'.writing');tmp.write_text(json.dumps(r,indent=2)+'\n');tmp.replace(p)
def module(name,file):
 s=importlib.util.spec_from_file_location(name,T/'tools'/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def live(pid,ticks):
 try:s=(P('/proc')/str(pid)/'stat').read_text().rsplit(')',1)[1].split();return int(s[19])==ticks and s[0] not in ['Z','X']
 except FileNotFoundError:return False
def event(state,**kw):
 row=dict(state=state,observed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),**kw);print(json.dumps(row),flush=True)
 with (T/'logs/CONTROLLER_R7_EVENTS.jsonl').open('a') as f:f.write(json.dumps(row)+'\n')
def finish_evidence(cell):
 n=module('R7_evidence_native_'+cell,'sweep_native_cap1m.py');intent=read(T/'control/qualification_ledger'/(cell+'.INTENT.json'));out=P(intent['output']);done=read(out/'NATIVE_EXIT.json')
 if done['stop_reason'] or done['launcher_wait_returncode']:
  proof=module('R7_failure_'+cell,'sweep_failure_review_host_v1.py').classify(cell);archive=module('R7_closed_copy_'+cell,'revision5/sweep_controller.py').archive_closed(cell)
  assert archive['scientific_status']=='STOP_UNACCEPTED';return {'state':'FAIL_CLOSED_UNACCEPTED_ARCHIVED_NO_RETRY','cohort':cell,'uuid':done['uuid'],'failure_classification':proof,'archive':archive,'accepted_cycles':None,'partial_cycles_accepted':False}
 science=module('R7_strict_'+cell,'sweep_strict_cap1m.py').terminal(cell);p=out/'AEFAIR_STRICT.json'
 if p.exists():assert read(p)==science
 else:write(p,science,True)
 qual={'status':'AEFAIR_SCIENCE_QUALIFIED','cohort':cell,'uuid':science['uuid'],'cycles':science['cycles'],'strict_sha256':sha(p),'SOURCE_KEEP':True};p=T/'DTC/control'/('SCIENCE_QUALIFICATION_'+cell+'.json')
 if p.exists():assert read(p)==qual
 else:write(p,qual,True)
 archive=module('R7_natural_copy_'+cell,'revision5/sweep_controller.py').archive_closed(cell)
 return {'state':'PASS_STRICT_ARCHIVE_NATIVE_RESTORE','cohort':cell,'uuid':done['uuid'],'cycles':science['cycles'],'archive':archive}
def run_cell(cell):
 try:
  assert not (T/'control/qualification_ledger'/(cell+'.INTENT.json')).exists()
  with (T/'logs'/(cell+'.PREPARE_R7.json')).open('x') as f:subprocess.run([str(N/'bin/experiment'),'prepare',cell,'--project','DTC_L1'],stdout=f,stderr=subprocess.STDOUT,check=True)
  with (T/'logs'/(cell+'.EXECUTION_R7.json')).open('x') as f:subprocess.run([str(N/'bin/experiment'),'run-native',cell,'--project','DTC_L1'],stdout=f,stderr=subprocess.STDOUT,check=True)
  return finish_evidence(cell)
 except BaseException as e:
  dp=T/'control/qualification_ledger'/(cell+'.DONE.json')
  if dp.exists():
   try:return finish_evidence(cell)
   except BaseException as diagnosis:e=RuntimeError(repr(e)+';evidence review:'+repr(diagnosis))
  return {'state':'RESOLVING_ISSUE_NO_MODEL_RETRY','cohort':cell,'error':repr(e),'partial_cycles_accepted':False}
def adopt_live(cell):
 n=module('R7_adopt_live_'+cell,'sweep_native_cap1m.py');began=time.monotonic()
 while True:
  q=n.read_current_authority()[0]['registered_future_requests'][REQ]
  if 'execution_receipt' in q['consumed'][cell]:return finish_evidence(cell)
  if time.monotonic()-began>90*86400:raise RuntimeError('preserved native attempt did not close within original outer wall bound')
  time.sleep(5)
def main():
 assert not (T/'control/CONTROLLER_START_R7.json').exists(),'No blind continuation restart'
 n=module('R7_authority_native','sweep_native_cap1m.py');owner=(T/'control/FINITE_CONTROLLER.lock').open('a+b');fcntl.flock(owner,fcntl.LOCK_EX)
 global_lock=(N/'control/qualification_ledger/NATIVE_QUALIFICATION.lock').open('rb');fcntl.flock(global_lock,fcntl.LOCK_EX)
 planpath=T/'control/HOST_EXECUTION_PLAN_V1.json';plan=read(planpath);qual=read(T/'control/CONTINUATION_R7_ZERO_MODEL_QUALIFICATION.json');pub=read(T/'control/CONTINUATION_R7_PUBLICATION_READBACK.json')
 assert qual['status']=='PASS' and qual['controller_sha256']==sha(__file__) and qual['plan_sha256']==sha(planpath) and pub['verified'] and pub['qualification_sha256']==sha(T/'control/CONTINUATION_R7_ZERO_MODEL_QUALIFICATION.json') and pub['controller_sha256']==sha(__file__)
 for r in plan['source_pins']:assert sha(r['path'])==r['sha256']
 prior=read(T/'control/CONTROLLER_LAUNCH_R5.json');assert not live(prior['pid'],prior['start_ticks'])
 before=copy.deepcopy(n.read_current_authority()[0]['registered_future_requests'][REQ]);assert set(before['consumed'])==set(plan['preserved_prefix_cells']) and before['state']=='RUNNING' and before['budget']==356
 write(T/'control/REQUEST_BEFORE_CONTINUATION_R7.json',before,True)
 def activate(reg):
  q=reg['registered_future_requests'][REQ];assert q==before
  q.setdefault('host_execution_profiles',{})['HOST_CPU_CACHE_AWARE_V1']=dict(plan,plan_sha256=sha(planpath),qualification_sha256=sha(T/'control/CONTINUATION_R7_ZERO_MODEL_QUALIFICATION.json'),publication_commit=pub['commit'])
  q['operational_continuations']=q.get('operational_continuations',[])+[{'revision':'R7_HOST_RESOURCE_CONTINUATION','controller_sha256':sha(__file__),'prefix_consumed':len(before['consumed']),'plan_sha256':sha(planpath),'publication_commit':pub['commit'],'model_retries':0,'adopt_live_without_restart':True}];q['orchestrator_sha256']=sha(__file__)
 n.update_authority(activate)
 lease={'pid':os.getpid(),'start_ticks':int(P('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19]),'fd':global_lock.fileno(),'request':REQ,'controller_sha256':sha(__file__),'scope':'Original finite matrix;qualified host resource adapter;all spent attempts preserved'};write(T/'control/BATCH_LEASE.json',lease);write(T/'control/CONTROLLER_START_R7.json',lease,True)
 prior_entry=(N/'bin/native').read_bytes();assert hashlib.sha256(prior_entry).hexdigest()==plan['prior_entry_sha256'];write(T/'control/NATIVE_ENTRY_BEFORE_HOST_ADAPTER_R7.json',{'sha256':plan['prior_entry_sha256'],'text':prior_entry.decode()},True)
 needle=str(T/'tools/sweep_frontend_cap1m.py').encode();assert prior_entry.count(needle)==1;new=prior_entry.replace(needle,str(T/'tools/sweep_frontend_host_v1.py').encode());tmp=N/'bin/.native.HOST_V1.writing';tmp.write_bytes(new);tmp.chmod((N/'bin/native').stat().st_mode&0o777);tmp.replace(N/'bin/native')
 n=module('R7_scheduler_native','sweep_native_cap1m.py');n=module('R7_explicit_host_adapter','sweep_host_execution_v1.py').install(n)
 claims=read(T/'control/POOL_DISPATCH_RESERVATIONS.json')['claims'];results={};running={};recovering={};issues=False
 with concurrent.futures.ThreadPoolExecutor(max_workers=plan['maximum_jobs']+4) as pool:
  for c,row in before['consumed'].items():
   p=T/'analysis'/(c+'.RESULT.json')
   if p.exists() and read(p)['state'] in OK:results[c]=read(p);continue
   if p.exists():write(T/'analysis/issue_preimages'/(c+'.BEFORE_R7.json'),read(p),True)
   if 'execution_receipt' in row:recovering[pool.submit(finish_evidence,c)]=c
   else:
    assert c in claims;running[pool.submit(adopt_live,c)]={'cell':c,'cpu':claims[c]['host_cpu'],'adopted_original_frontend':True}
  while True:
   assert not (T/'control/ABORT').exists(),'User ABORT;new dispatch stops'
   for collection in [running,recovering]:
    for future,meta in list(collection.items()):
     if not future.done():continue
     c=meta['cell'] if isinstance(meta,dict) else meta
     try:r=future.result()
     except BaseException as e:r={'state':'RESOLVING_ISSUE_NO_MODEL_RETRY','cohort':c,'error':repr(e)}
     results[c]=r;write(T/'analysis'/(c+'.RESULT.json'),r);collection.pop(future);claims.pop(c,None);write(T/'control/POOL_DISPATCH_RESERVATIONS.json',{'claims':claims});event(r['state'],cohort=c)
     if r['state'] not in OK:issues=True
   q=n.read_current_authority()[0]['registered_future_requests'][REQ];pending=[c for c in q['admitted_specs'] if c not in q['consumed'] and c not in q.get('sealed',[])];pending.sort(key=lambda c:(read(T/'control'/(c+'_SPEC.json'))['expected']['instructions'],c))
   used={r['cpu'] for r in running.values()};started=0
   if not issues:
    for c in pending:
     if len(running)>=plan['maximum_jobs']:break
     slots=[cpu for cpu in plan['model_CPUs'] if cpu not in used]
     if not slots:break
     s=n.spec_for(c);res=n.resources(s,True)
     if not(res['physical_RAM_pass'] and res['physical_disk_pass']):continue
     cpu=slots[0];claims[c]={'result_cap_bytes':s['limits']['max_result_directory_bytes'],'RAM_cap_bytes':s['limits']['max_process_tree_rss_bytes'],'host_cpu':cpu};write(T/'control/POOL_DISPATCH_RESERVATIONS.json',{'claims':claims});running[pool.submit(run_cell,c)]={'cell':c,'cpu':cpu,'adopted_original_frontend':False};used.add(cpu);started+=1;event('DISPATCH_ORIGINAL_UNUSED_HOST_BOUND_CELL',cohort=c,CPU=cpu)
   state={'state':'R7_ISSUE_CHECKPOINT_NO_NEW_STARTS' if issues else 'R7_RESOURCE_AWARE_FINITE_MATRIX','running':[r['cell'] for r in running.values()],'recovering_closed_attempts':list(recovering.values()),'closed_results':len(results),'consumed_starts':len(q['consumed']),'remaining_registered_budget':q['remaining'],'maximum_jobs':plan['maximum_jobs'],'actual_running_future_count':len(running),'observed_unix':time.time(),'model_retries':0};write(T/'analysis/BATCH_STATE_R7.json',state);write(T/'analysis/BATCH_STATE.json',state)
   if issues and not running and not recovering:event('R7_NATIVE_OR_STRICT_ISSUE_ALL_ACTIVE_CLOSED');return
   if not running and not recovering and not pending:
    assert set(results)==set(q['consumed']) and all(r['state'] in OK for r in results.values());prior_phase=read(T/'analysis/BODY_QUALIFICATION_PROGRESS.json');assert prior_phase['closed']==89
    holds=read(T/'analysis/BATCH_STATE_BEFORE_R7.json')['input_holds']
    def close(reg):
     a=reg['registered_future_requests'][REQ];a['sealed']=sorted(set(a['candidate_cohorts'])-set(a['consumed']));a['sealed_unused']=len(a['sealed']);a['remaining']=0;a['state']='ALL_STARTS_CLOSED_PENDING_COMPLETE_SCIENTIFIC_DELIVERY';a['input_holds']=holds
    n.update_authority(close)
    phase=dict(state,state='ALL_APPLICABLE_NATIVE_ATTEMPTS_CLOSED_ARCHIVED_RESTORED_WITH_CLASSIFIED_FAILURES',closed_point_results=len(results),input_holds=holds,closed_unaccepted_points={c:r for c,r in results.items() if r['state']=='FAIL_CLOSED_UNACCEPTED_ARCHIVED_NO_RETRY'},phase_revision='R7_HOST_RESOURCE_CONTINUATION_COMPLETED_ORIGINAL_R5_MATRIX')
    write(T/'analysis/BATCH_NATIVE_CLOSED_R7.json',phase,True);write(T/'analysis/BATCH_NATIVE_CLOSED.json',phase);event('R7_NATIVE_PHASE_CLOSED_ORIGINAL_R6_CUTCP_STILL_REQUIRED');return
   time.sleep(1 if started else 10)
if __name__=='__main__':
 try:main()
 except BaseException as e:event('R7_CONTROLLER_ERROR_PRESERVE_ALL_HISTORY_NO_RETRY',error=repr(e));raise
