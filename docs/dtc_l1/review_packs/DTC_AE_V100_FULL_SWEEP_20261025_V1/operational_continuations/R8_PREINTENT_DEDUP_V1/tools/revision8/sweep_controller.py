"""Deduplicated finite scheduler; no second model fork for a spent cell."""
import pathlib,json,hashlib,importlib.util,os,fcntl,time,datetime,subprocess,concurrent.futures,copy,uuid
P=pathlib.Path;T=P('/root/data/dtc_main_v100_sweep_20261025_v1');N=P('/root/data/ep_l2_dtc_l1_native_v2');REQ='DTC_AE_V100_FULL_SWEEP_20261025_V1';OK={'PASS_STRICT_ARCHIVE_NATIVE_RESTORE','FAIL_CLOSED_UNACCEPTED_ARCHIVED_NO_RETRY'}
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
def live(r):
 try:s=(P('/proc')/str(r['pid'])/'stat').read_text().rsplit(')',1)[1].split();return int(s[19])==r['start_ticks'] and s[0] not in ['Z','X']
 except FileNotFoundError:return False
def event(state,**fields):
 r=dict(state=state,observed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),**fields);print(json.dumps(r),flush=True)
 with (T/'logs/CONTROLLER_R8_EVENTS.jsonl').open('a') as f:f.write(json.dumps(r)+'\n')
def pending_cells(q,running,claims,cooldown,now):
 occupied={r['cell'] for r in running.values()}|set(claims)
 return [c for c in q['admitted_specs'] if c not in q['consumed'] and c not in q.get('sealed',[]) and c not in occupied and cooldown.get(c,0)<=now]
def prefork_resource_defer(cell,native,detail):
 ip=T/'control/qualification_ledger'/(cell+'.INTENT.json');q=native.read_current_authority()[0]['registered_future_requests'][REQ]
 return not ip.exists() and cell not in q['consumed'] and any(token in detail for token in ["'RESOURCE_HOLD'","'RESOURCE_HOLD_NO_START'","'RESOURCE_HOLD_AFTER_DTC_PAIR'"])
def archive_closed(cell):
 outbox=module('R8_outbox_'+cell,'sweep_outbox.py');p=T/'control'/(cell+'_ARCHIVE_RECEIPT.json');began=time.monotonic()
 while True:
  if p.exists():
   r=read(p);assert r['status']=='ARCHIVE_VERIFIED_AND_RESTORE_VERIFIED_NATIVE_TARGET';bundle=P(r['target_mount_path']);manifest=outbox.manifest_for(cell);assert manifest==read(bundle/'SOURCE_MANIFEST.json') and manifest['scientific_status']==r['scientific_status'];f,v=outbox.libraries(bundle);idx=f.verify_archive(bundle,manifest);proof=f.check_native(P(r['native_restore']),manifest);assert idx['archive_sha256']==r['archive_sha256'] and len(proof)==len(manifest['entries']);return r
  cmd=subprocess.run([str(N/'bin/result'),'archive',cell],capture_output=True,text=True,timeout=3600);write(T/'logs'/(cell+'.ARCHIVE_R8.'+uuid.uuid4().hex+'.json'),{'stdout':cmd.stdout,'stderr':cmd.stderr,'returncode':cmd.returncode,'models_started':0},True)
  if cmd.returncode==0:continue
  if '[Errno 11]' not in cmd.stderr or time.monotonic()-began>21600:cmd.check_returncode()
  time.sleep(30)
def finish_evidence(cell):
 intent=read(T/'control/qualification_ledger'/(cell+'.INTENT.json'));out=P(intent['output']);done=read(out/'NATIVE_EXIT.json')
 if done['stop_reason'] or done['launcher_wait_returncode']:
  proof=module('R8_failure_'+cell,'sweep_failure_review_host_v1.py').classify(cell);archive=archive_closed(cell);assert archive['scientific_status']=='STOP_UNACCEPTED'
  return {'state':'FAIL_CLOSED_UNACCEPTED_ARCHIVED_NO_RETRY','cohort':cell,'uuid':done['uuid'],'failure_classification':proof,'archive':archive,'accepted_cycles':None,'partial_cycles_accepted':False}
 science=module('R8_strict_'+cell,'sweep_strict_cap1m.py').terminal(cell);p=out/'AEFAIR_STRICT.json'
 if p.exists():assert read(p)==science
 else:write(p,science,True)
 qual={'status':'AEFAIR_SCIENCE_QUALIFIED','cohort':cell,'uuid':science['uuid'],'cycles':science['cycles'],'strict_sha256':sha(p),'SOURCE_KEEP':True};p=T/'DTC/control'/('SCIENCE_QUALIFICATION_'+cell+'.json')
 if p.exists():assert read(p)==qual
 else:write(p,qual,True)
 archive=archive_closed(cell);assert archive['scientific_status']=='AEFAIR_SCIENCE_QUALIFIED';return {'state':'PASS_STRICT_ARCHIVE_NATIVE_RESTORE','cohort':cell,'uuid':done['uuid'],'cycles':science['cycles'],'archive':archive}
def run_cell(cell):
 native=module('R8_worker_identity_'+cell,'sweep_native_cap1m.py');roundid=uuid.uuid4().hex
 try:
  assert not (T/'control/qualification_ledger'/(cell+'.INTENT.json')).exists() and cell not in native.read_current_authority()[0]['registered_future_requests'][REQ]['consumed']
  for stage in ['prepare','run-native']:
   cmd=subprocess.run([str(N/'bin/experiment'),stage,cell,'--project','DTC_L1'],capture_output=True,text=True);write(T/'logs'/(cell+'.'+stage+'.R8.'+roundid+'.json'),{'stdout':cmd.stdout,'stderr':cmd.stderr,'returncode':cmd.returncode,'stage':stage},True)
   if cmd.returncode:
    if prefork_resource_defer(cell,native,cmd.stderr):return {'state':'ADMISSION_DEFERRED_ZERO_START','cohort':cell,'stage':stage,'roundid':roundid,'model_starts':0,'reason':cmd.stderr}
    cmd.check_returncode()
  return finish_evidence(cell)
 except BaseException as e:
  if (T/'control/qualification_ledger'/(cell+'.DONE.json')).exists():
   try:return finish_evidence(cell)
   except BaseException as diagnosis:e=RuntimeError(repr(e)+';closed review:'+repr(diagnosis))
  return {'state':'RESOLVING_ISSUE_NO_MODEL_RETRY','cohort':cell,'error':repr(e),'partial_cycles_accepted':False}
def adopt_live(cell):
 n=module('R8_watched_native_'+cell,'sweep_native_cap1m.py');began=time.monotonic()
 while True:
  if 'execution_receipt' in n.read_current_authority()[0]['registered_future_requests'][REQ]['consumed'][cell]:return finish_evidence(cell)
  assert time.monotonic()-began<90*86400;time.sleep(5)
def main():
 assert not (T/'control/CONTROLLER_START_R8.json').exists(),'Never blindly restart a continuation'
 n=module('R8_authority','sweep_native_cap1m.py');owner=(T/'control/FINITE_CONTROLLER.lock').open('a+b');fcntl.flock(owner,fcntl.LOCK_EX);held=(N/'control/qualification_ledger/NATIVE_QUALIFICATION.lock').open('rb');fcntl.flock(held,fcntl.LOCK_EX)
 qual=read(T/'control/CONTINUATION_R8_ZERO_MODEL_QUALIFICATION.json');pub=read(T/'control/CONTINUATION_R8_PUBLICATION_READBACK.json');assert qual['status']=='PASS' and pub['verified'] and pub['controller_sha256']==qual['controller_sha256']==sha(__file__) and pub['qualification_sha256']==sha(T/'control/CONTINUATION_R8_ZERO_MODEL_QUALIFICATION.json')
 assert not live(read(T/'control/CONTROLLER_LAUNCH_R7.json')) and not (T/'control/ABORT').exists();before=copy.deepcopy(n.read_current_authority()[0]['registered_future_requests'][REQ]);assert before['budget']==356 and before['state']=='RUNNING' and before['host_execution_profiles']['HOST_CPU_CACHE_AWARE_V1']['plan_sha256']==sha(T/'control/HOST_EXECUTION_PLAN_V1.json');write(T/'control/REQUEST_BEFORE_CONTINUATION_R8.json',before,True)
 def activate(reg):
  q=reg['registered_future_requests'][REQ];assert q==before;q['orchestrator_sha256']=sha(__file__);q.setdefault('operational_continuations',[]).append({'revision':'R8_DEDUPLICATED_PREINTENT_QUEUE','controller_sha256':sha(__file__),'publication_commit':pub['commit'],'qualification_sha256':sha(T/'control/CONTINUATION_R8_ZERO_MODEL_QUALIFICATION.json'),'spent_prefix':len(before['consumed']),'model_retries':0,'adopts_all_live_original_generations':True})
 n.update_authority(activate);lease={'pid':os.getpid(),'start_ticks':int(P('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19]),'fd':held.fileno(),'request':REQ,'controller_sha256':sha(__file__),'scope':'Same original finite matrix;pre-INTENT running/claimed exclusion;host adapter unchanged'};write(T/'control/BATCH_LEASE.json',lease);write(T/'control/CONTROLLER_START_R8.json',lease,True)
 n=module('R8_scheduler_native','sweep_native_cap1m.py');n=module('R8_unchanged_host_adapter','sweep_host_execution_v1.py').install(n);plan=read(T/'control/HOST_EXECUTION_PLAN_V1.json');claims=read(T/'control/POOL_DISPATCH_RESERVATIONS.json')['claims'];results={};running={};recovering={};cooldown={};issues=False
 for p in (T/'analysis').glob('E2-AEV100-*.RESULT.json'):
  cell=p.name.removesuffix('.RESULT.json')
  if cell not in before['consumed']:
   assert not (T/'control/qualification_ledger'/(cell+'.INTENT.json')).exists();dest=T/'analysis/issue_preimages'/(p.stem+'.UNSPENT_BEFORE_R8.json');assert not dest.exists();p.rename(dest)
 with concurrent.futures.ThreadPoolExecutor(max_workers=plan['maximum_jobs']+4) as pool:
  for c,row in before['consumed'].items():
   p=T/'analysis'/(c+'.RESULT.json')
   if p.exists() and read(p)['state'] in OK:results[c]=read(p);continue
   if 'execution_receipt' in row:recovering[pool.submit(finish_evidence,c)]=c
   else:assert c in claims;running[pool.submit(adopt_live,c)]={'cell':c,'cpu':claims[c]['host_cpu'],'adopted_original_frontend':True}
  while True:
   assert not (T/'control/ABORT').exists()
   for collection in [running,recovering]:
    for future,meta in list(collection.items()):
     if not future.done():continue
     c=meta['cell'] if isinstance(meta,dict) else meta
     try:r=future.result()
     except BaseException as e:r={'state':'RESOLVING_ISSUE_NO_MODEL_RETRY','cohort':c,'error':repr(e)}
     collection.pop(future);claims.pop(c,None);write(T/'control/POOL_DISPATCH_RESERVATIONS.json',{'claims':claims})
     if r['state']=='ADMISSION_DEFERRED_ZERO_START':
      assert c not in n.read_current_authority()[0]['registered_future_requests'][REQ]['consumed'] and not (T/'control/qualification_ledger'/(c+'.INTENT.json')).exists();cooldown[c]=time.monotonic()+30;write(T/'analysis/prefork_admission'/(c+'.'+r['roundid']+'.json'),r,True);event('ADMISSION_DEFERRED_ZERO_START',cohort=c);continue
     results[c]=r;write(T/'analysis'/(c+'.RESULT.json'),r);event(r['state'],cohort=c)
     if r['state'] not in OK:issues=True
   q=n.read_current_authority()[0]['registered_future_requests'][REQ];pending=pending_cells(q,running,claims,cooldown,time.monotonic());pending.sort(key=lambda c:(read(T/'control'/(c+'_SPEC.json'))['expected']['instructions'],c));started=0;used={r['cpu'] for r in running.values()}
   if not issues:
    for c in pending:
     if len(running)>=plan['maximum_jobs']:break
     slots=[cpu for cpu in plan['model_CPUs'] if cpu not in used]
     if not slots:break
     s=n.spec_for(c);res=n.resources(s,True)
     if not(res['physical_RAM_pass'] and res['physical_disk_pass']):continue
     assert c not in {r['cell'] for r in running.values()} and c not in claims
     cpu=slots[0];claims[c]={'result_cap_bytes':s['limits']['max_result_directory_bytes'],'RAM_cap_bytes':s['limits']['max_process_tree_rss_bytes'],'host_cpu':cpu};write(T/'control/POOL_DISPATCH_RESERVATIONS.json',{'claims':claims});running[pool.submit(run_cell,c)]={'cell':c,'cpu':cpu,'adopted_original_frontend':False};used.add(cpu);started+=1;event('DISPATCH_ORIGINAL_UNUSED_CELL',cohort=c,CPU=cpu)
   state={'state':'R8_ISSUE_CHECKPOINT_NO_NEW_STARTS' if issues else 'R8_RESOURCE_AWARE_DEDUPLICATED_FINITE_MATRIX','running':[r['cell'] for r in running.values()],'recovering_closed_attempts':list(recovering.values()),'closed_results':len(results),'consumed_starts':len(q['consumed']),'remaining_registered_budget':q['remaining'],'maximum_jobs':plan['maximum_jobs'],'observed_unix':time.time(),'model_retries':0};write(T/'analysis/BATCH_STATE_R8.json',state);write(T/'analysis/BATCH_STATE.json',state)
   if issues and not running and not recovering:event('R8_ISSUE_ALL_ACTIVE_CLOSED');return
   # Cooling-down unstarted cells are still pending original work.
   all_pending=set(q['admitted_specs'])-set(q['consumed'])-set(q.get('sealed',[]))
   if not running and not recovering and not all_pending:
    assert set(results)==set(q['consumed']) and all(r['state'] in OK for r in results.values());holds=read(T/'analysis/BATCH_STATE_BEFORE_R7.json')['input_holds']
    def close(reg):
     a=reg['registered_future_requests'][REQ];a['sealed']=sorted(set(a['candidate_cohorts'])-set(a['consumed']));a['sealed_unused']=len(a['sealed']);a['remaining']=0;a['state']='ALL_STARTS_CLOSED_PENDING_COMPLETE_SCIENTIFIC_DELIVERY';a['input_holds']=holds
    n.update_authority(close);phase=dict(state,state='ALL_APPLICABLE_NATIVE_ATTEMPTS_CLOSED_ARCHIVED_RESTORED_WITH_CLASSIFIED_FAILURES',closed_point_results=len(results),input_holds=holds,closed_unaccepted_points={c:r for c,r in results.items() if r['state']=='FAIL_CLOSED_UNACCEPTED_ARCHIVED_NO_RETRY'},phase_revision='R8_COMPLETED_ORIGINAL_R5_R7_MATRIX')
    write(T/'analysis/BATCH_NATIVE_CLOSED_R8.json',phase,True);write(T/'analysis/BATCH_NATIVE_CLOSED.json',phase);event('R8_NATIVE_PHASE_CLOSED_REQUIRES_R6_CUTCP_AND_FINAL_DELIVERY');return
   time.sleep(1 if started else 10)
if __name__=='__main__':
 try:main()
 except BaseException as e:event('R8_CONTROLLER_ERROR_PRESERVE_ALL_HISTORY_NO_RETRY',error=repr(e));raise
