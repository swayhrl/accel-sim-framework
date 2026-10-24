"""One finite request, measured-safe worker pool, immutable one-start cells."""
import pathlib,json,subprocess,time,sys,os,fcntl,importlib.util,hashlib,datetime,concurrent.futures,threading
P=pathlib.Path;T=P('/root/data/dtc_main_v100_sweep_20261025_v1');N=P('/root/data/ep_l2_dtc_l1_native_v2');REQ='DTC_AE_V100_FULL_SWEEP_20261025_V1'
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def module(name,file):
 s=importlib.util.spec_from_file_location(name,T/'tools'/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def write(p,x):
 p=P(p);temp=p.with_name(p.name+'.writing');temp.write_text(json.dumps(x,indent=2)+'\n');os.replace(temp,p)
def event(x):
 x=dict(x,utc=datetime.datetime.now(datetime.timezone.utc).isoformat());print(json.dumps(x),flush=True)
 with (T/'logs/CONTROLLER_EVENTS.jsonl').open('a') as f:f.write(json.dumps(x)+'\n')
COPY_LOCK=threading.Lock()
def archive_closed(cell):
 started=time.monotonic();attempt=0
 while True:
  attempt+=1
  with COPY_LOCK:
   p=subprocess.run([str(N/'bin/result'),'archive',cell],capture_output=True,text=True,timeout=3600)
   with (T/'logs'/(cell+'.ARCHIVE.'+str(attempt)+'.json')).open('x') as f:json.dump({'stdout':p.stdout,'stderr':p.stderr,'returncode':p.returncode,'model_starts':0},f,indent=2)
  if p.returncode==0:
   r=json.loads(p.stdout);assert r['receipt']['status']=='ARCHIVE_VERIFIED_AND_RESTORE_VERIFIED_NATIVE_TARGET';return r['receipt']
  if '[Errno 11]' not in p.stderr or time.monotonic()-started>21600:p.check_returncode()
  event({'state':'WAIT_COPYONLY_SHARED_RECEIVER','cohort':cell,'seconds':time.monotonic()-started});time.sleep(30)
def run_cell(cell):
 native=module('worker_'+cell.replace('-','_'),'sweep_native.py');strict=module('strict_'+cell.replace('-','_'),'sweep_strict.py')
 try:
  prep=subprocess.run([str(N/'bin/experiment'),'prepare',cell,'--project','DTC_L1'],capture_output=True,text=True,timeout=3600)
  with (T/'logs'/(cell+'.PREPARE.json')).open('x') as f:json.dump({'stdout':prep.stdout,'stderr':prep.stderr,'returncode':prep.returncode},f,indent=2)
  prep.check_returncode()
  assert not (T/'control/qualification_ledger'/(cell+'.INTENT.json')).exists(),'spent cell cannot be restarted'
  with (T/'logs'/(cell+'.EXECUTION.json')).open('x') as f:p=subprocess.run([str(N/'bin/experiment'),'run-native',cell,'--project','DTC_L1'],stdout=f,stderr=subprocess.STDOUT)
  if p.returncode:raise RuntimeError('native operation closed or refused;inspect exact INTENT/DONE,never blind model retry')
  science=strict.terminal(cell);intent=read(T/'control/qualification_ledger'/(cell+'.INTENT.json'));out=P(intent['output'])
  with (out/'AEFAIR_STRICT.json').open('x') as f:json.dump(science,f,indent=2);f.write('\n')
  qual={'status':'AEFAIR_SCIENCE_QUALIFIED','cohort':cell,'uuid':science['uuid'],'cycles':science['cycles'],'strict_sha256':sha(out/'AEFAIR_STRICT.json'),'SOURCE_KEEP':True}
  with (T/'DTC/control'/('SCIENCE_QUALIFICATION_'+cell+'.json')).open('x') as f:json.dump(qual,f,indent=2);f.write('\n')
  event({'state':'POINT_STRICT_ACCEPTED','cohort':cell,'cycles':science['cycles'],'uuid':science['uuid']})
  archive=archive_closed(cell)
  return {'state':'PASS_STRICT_ARCHIVE_NATIVE_RESTORE','cohort':cell,'uuid':science['uuid'],'cycles':science['cycles'],'archive':archive}
 except BaseException as e:
  try:
   failure=module('closed_failure_'+cell.replace('-','_'),'sweep_failure_review.py');proof=failure.classify(cell);archive=archive_closed(cell);assert archive['scientific_status']=='STOP_UNACCEPTED'
   result={'state':'FAIL_CLOSED_NATIVE_DEADLOCK_ARCHIVED_NO_RETRY','cohort':cell,'uuid':proof['uuid'],'failure_classification':proof,'archive':archive,'accepted_cycles':None,'partial_cycles_accepted':False};event(result);return result
  except BaseException as diagnosis_error:event({'state':'FAILURE_CLASS_NOT_REVIEWED_CHECKPOINT','cohort':cell,'error':repr(diagnosis_error)})
  intent=T/'control/qualification_ledger'/(cell+'.INTENT.json');done=T/'control/qualification_ledger'/(cell+'.DONE.json')
  result={'state':'RESOLVING_ISSUE_NO_MODEL_RETRY','cohort':cell,'error':repr(e),'intent_exists':intent.exists(),'done_exists':done.exists(),'partial_cycles_accepted':False}
  if done.exists():result['native_done']=read(done)
  event(result);return result
def unused_original_install(native,lease):
 assert read(T/'control/PUBLICATION_READBACK.json')['verified'] and read(T/'control/ZERO_MODEL_QUALIFICATION.json')['status']=='PASS'
 q=read(T/'control/REGISTRATION_CANDIDATE.json');assert q['controller_sha256']==sha(T/'tools/sweep_native.py') and q['orchestrator_sha256']==sha(__file__)
 reg,epoch=native.read_current_authority();assert epoch['epoch']==2 and epoch['state']=='NATIVE_SCIENCE_ACTIVE' and REQ not in reg['registered_future_requests']
 for name,row in reg['registered_future_requests'].items():
  assert row['state'] in native.TERMINAL_PEER_STATES and row.get('reserved_write_bytes',0)==0 or row['state'] in ['COMPLETE','CLOSED','STOP_UNACCEPTED'],'unresolved peer request:'+name
 prior=(N/'bin/native').read_bytes();needle=b'/root/data/dtc_main_short3_20261024_v1/tools/short3_frontend_floor5_v3.py';assert prior.count(needle)==1
 (T/'control/NATIVE_ENTRY_AT_INSTALL.sh').write_bytes(prior)
 replacement=prior.replace(needle,str(T/'tools/sweep_frontend.py').encode());tmp=N/'bin/.native.DTC_SWEEP.writing'
 with tmp.open('xb') as f:f.write(replacement);f.flush();os.fsync(f.fileno())
 tmp.chmod((N/'bin/native').stat().st_mode&0o777);assert (N/'bin/native').read_bytes()==prior;os.replace(tmp,N/'bin/native')
 before=reg['registered_future_requests'];write(T/'control/REGISTRY_AT_INSTALL.json',reg)
 def add(r):
  assert r['registered_future_requests']==before;r['registered_future_requests'][REQ]=q
 native.update_authority(add)
 write(T/'control/REQUEST_INSTALLED.json',{'request':REQ,'max_budget':q['budget'],'actual_starts':0,'prior_requests_unchanged':True,'asset_router_and_all_prior_science_routes_preserved':True,'current_entry_sha256':sha(N/'bin/native'),'lease':lease})
def adopt(native,lease):
 pub=read(T/'control/CONTINUATION_R3_PUBLICATION_READBACK.json');qual=read(T/'control/CONTINUATION_R3_ZERO_MODEL_QUALIFICATION.json')
 assert pub['verified'] and pub['controller_sha256']==sha(__file__) and pub['failure_review_sha256']==sha(T/'tools/sweep_failure_review.py') and qual['status']=='PASS'
 old=read(T/'control/CONTROLLER_LAUNCH_R2.json');p=P('/proc')/str(old['pid'])
 if p.exists():assert int((p/'stat').read_text().rsplit(')',1)[1].split()[19])!=old['start_ticks'],'old controller generation still live'
 reg,epoch=native.read_current_authority();q=reg['registered_future_requests'][REQ];assert q['state']=='RUNNING' and q['budget']==356
 assert not read(T/'control/POOL_DISPATCH_RESERVATIONS.json')['claims']
 failure=module('closed_failure_adoption','sweep_failure_review.py');recovered={}
 for cell,row in q['consumed'].items():
  assert 'execution_receipt' in row,'active or unclosed prior model cannot be adopted'
  resultfile=T/'analysis'/(cell+'.RESULT.json');result=read(resultfile)
  if result['state']=='PASS_STRICT_ARCHIVE_NATIVE_RESTORE':recovered[cell]=result;continue
  proof=failure.classify(cell);receipt=read(T/'control'/(cell+'_ARCHIVE_RECEIPT.json'));assert receipt['scientific_status']=='STOP_UNACCEPTED' and receipt['status']=='ARCHIVE_VERIFIED_AND_RESTORE_VERIFIED_NATIVE_TARGET'
  outbox=module('closed_failure_archive_adoption','sweep_outbox.py');bundle=P(receipt['target_mount_path']);f,v=outbox.libraries(bundle);manifest=read(bundle/'SOURCE_MANIFEST.json');idx=f.verify_archive(bundle,manifest);assert idx['archive_sha256']==receipt['archive_sha256'];f.check_native(P(receipt['native_restore']),manifest)
  pre=T/'analysis/issue_preimages';pre.mkdir(exist_ok=True);saved=pre/(cell+'.RESULT_R2.json');assert not saved.exists();saved.write_bytes(resultfile.read_bytes())
  recovered[cell]={'state':'FAIL_CLOSED_NATIVE_DEADLOCK_ARCHIVED_NO_RETRY','cohort':cell,'uuid':row['uuid'],'failure_classification':proof,'archive':receipt,'accepted_cycles':None,'partial_cycles_accepted':False};write(resultfile,recovered[cell])
 before=dict(q);write(T/'control/REQUEST_BEFORE_CONTINUATION_R3.json',q)
 def amend(r):
  actual=r['registered_future_requests'][REQ];assert actual==before
  actual['operational_continuations']=actual.get('operational_continuations',[])+[{'revision':'R3','prior_orchestrator_sha256':actual['orchestrator_sha256'],'new_orchestrator_sha256':sha(__file__),'failure_classifier_sha256':sha(T/'tools/sweep_failure_review.py'),'publication_commit':pub['commit'],'qualification_sha256':sha(T/'control/CONTINUATION_R3_ZERO_MODEL_QUALIFICATION.json'),'prior_consumed':len(actual['consumed']),'same_finite_budget':356,'model_retries':0}]
  actual['orchestrator_sha256']=sha(__file__)
 native.update_authority(amend)
 after=native.read_current_authority()[0]['registered_future_requests'][REQ];assert all(after[k]==v for k,v in before.items() if k not in ['orchestrator_sha256','operational_continuations'])
 write(T/'control/CONTINUATION_R3_ADOPTED.json',{'state':'ALL_PRIOR_SPENT_CELLS_ADOPTED_NO_RERUN','consumed':len(before['consumed']),'remaining':before['remaining'],'accepted':sum(x['state']=='PASS_STRICT_ARCHIVE_NATIVE_RESTORE' for x in recovered.values()),'closed_unaccepted':sum(x['state'].startswith('FAIL_CLOSED') for x in recovered.values()),'lease':lease})
 return recovered

def main():
 owner=(T/'control/FINITE_CONTROLLER.lock').open('a+b')
 while True:
  try:fcntl.flock(owner,fcntl.LOCK_EX|fcntl.LOCK_NB);break
  except BlockingIOError:event({'state':'WAIT_PREVIOUS_OWNED_CONTROLLER_NATURAL_CLOSE','new_model_starts':0});time.sleep(30)
 assert not (T/'control/CONTROLLER_START_R3.json').exists(),'one finite controller already started;inspect/adopt journals,never restart spent cells'
 native=module('main_native','sweep_native.py');admission=module('input_admission','sweep_admission.py')
 global_lock=(N/'control/qualification_ledger/NATIVE_QUALIFICATION.lock').open('rb');started=time.monotonic()
 while True:
  try:fcntl.flock(global_lock,fcntl.LOCK_EX|fcntl.LOCK_NB);break
  except BlockingIOError:
   if time.monotonic()-started>21600:raise
   event({'state':'WAIT_GLOBAL_NATIVE_SCIENCE_RELEASE','new_model_starts':0});time.sleep(30)
 lease={'pid':os.getpid(),'start_ticks':int(P('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19]),'fd':global_lock.fileno(),'request':REQ,'controller_sha256':sha(__file__),'scope':'One finite request owns global epoch2 admission lease;internal independent jobs have per-cell journals/locks and one sole164 receiver'}
 recovered=adopt(native,lease);write(T/'control/BATCH_LEASE.json',lease);write(T/'control/CONTROLLER_START_R3.json',lease)
 cal=read(T/'control/HOST_CALIBRATION.json');ceiling=cal['measured_N_safe_ceiling'];target=cal['startup_model_concurrency'];claims={};write(T/'control/POOL_DISPATCH_RESERVATIONS.json',{'claims':claims})
 grouped=admission.grouped_candidates();admitted={};holds={};results=recovered;running={};issues=False;start_count=0
 with concurrent.futures.ThreadPoolExecutor(max_workers=ceiling) as pool:
  while True:
   if (T/'control/ABORT').exists():raise RuntimeError('USER_ABORT;running native guards observe same abort file')
   for key in grouped:
    if key in admitted or key in holds:continue
    result=admission.admit(key,native)
    if result['state']=='ADMITTED_FULL_INPUT':admitted[key]=result;event(result)
    elif result['state']=='INPUT_HOLD':holds[key]=result;event({'state':'INPUT_HOLD','input_digest':key,'reason':result['reason'],'issue_count':len(result.get('issues',[]))})
   for future,meta in list(running.items()):
    if not future.done():continue
    result=future.result();results[meta['cell']]=result;claims.pop(meta['cell']);write(T/'control/POOL_DISPATCH_RESERVATIONS.json',{'claims':claims});del running[future]
    write(T/'analysis'/(meta['cell']+'.RESULT.json'),result);event({k:v for k,v in result.items() if k!='archive'})
    if result['state'] not in ['PASS_STRICT_ARCHIVE_NATIVE_RESTORE','FAIL_CLOSED_NATIVE_DEADLOCK_ARCHIVED_NO_RETRY']:issues=True
   passed=sum(r['state']=='PASS_STRICT_ARCHIVE_NATIVE_RESTORE' for r in results.values())
   if passed>=cal['ramp_after_complete_accepted_points']:target=ceiling
   reg,_=native.read_current_authority();q=reg['registered_future_requests'][REQ];usedcpus={m['cpu'] for m in running.values()};active_heavy=sum(m['heavy'] for m in running.values())
   pending=[]
   for key,r in admitted.items():
    for cell in r['cells']:
     if cell in results or cell in q['consumed'] or any(m['cell']==cell for m in running.values()):continue
     s=native.spec_for(cell);heavy=s['expected']['instructions']>100_000_000
     pending.append((key,cell,s,heavy))
   # Firstfour actual Goal points reproduceNN with fresh UUIDs to qualify the
   # entire concurrent execution pipeline;these are not extra canaries.
   pending.sort(key=lambda z:(0 if grouped[z[0]][0]['program']=='nn' and z[2]['expected']['instructions']==1284872 else 1,z[2]['expected']['instructions'],z[1]))
   launched=False
   if not issues:
    for key,cell,s,heavy in pending:
     if len(running)>=target:break
     if s['host_cpu'] in usedcpus:continue
     if heavy and active_heavy>=max(1,target//3) and any(not x[3] for x in pending):continue
     res=native.resources(s,True)
     if not(res['physical_RAM_pass'] and res['physical_disk_pass']):continue
     claims[cell]={'result_cap_bytes':s['limits']['max_result_directory_bytes'],'RAM_cap_bytes':s['limits']['max_process_tree_rss_bytes'],'host_cpu':s['host_cpu']};write(T/'control/POOL_DISPATCH_RESERVATIONS.json',{'claims':claims})
     f=pool.submit(run_cell,cell);running[f]={'cell':cell,'cpu':s['host_cpu'],'heavy':heavy};usedcpus.add(s['host_cpu']);active_heavy+=heavy;start_count+=1;launched=True
     event({'state':'DISPATCH_FULL_INPUT_CELL','cohort':cell,'CPU':s['host_cpu'],'pool_target':target,'max_per_point_wall':s['limits']['timeout_seconds']})
   body_done=read(T/'analysis/BODY_QUALIFICATION_PROGRESS.json')['state']=='ALL_FINITE_BODY_QUALIFICATIONS_CLOSED'
   state={'state':'RESOLVING_NATIVE_OR_STRICT_ISSUE' if issues else 'RUNNING_FINITE_MATRIX','body_closed':len(admitted)+len(holds),'input_candidates':len(grouped),'admitted_inputs':len(admitted),'input_holds':holds,'running':[m['cell'] for m in running.values()],'accepted_archived_points':passed,'closed_point_results':len(results),'closed_unaccepted_points':sum(x['state'].startswith('FAIL_CLOSED') for x in results.values()),'admitted_pending_points':len(pending),'pool_target':target,'qualified_ceiling':ceiling,'model_budget':q['budget'],'consumed_starts':len(q['consumed']),'remaining_registered_budget':q['remaining'],'model_retries':0,'observed_unix':time.time()}
   write(T/'analysis/BATCH_STATE.json',state)
   if issues and not running:event({'state':'ISSUE_CHECKPOINT_ALL_ACTIVE_MODELS_CLOSED_NO_NEW_STARTS'});return
   if body_done and not running and not pending:
    def close(r):
     row=r['registered_future_requests'][REQ];row['sealed']=list(set(row['candidate_cohorts'])-set(row['consumed']));row['sealed_unused']=row['remaining'];row['remaining']=0;row['state']='ALL_STARTS_CLOSED_PENDING_COMPLETE_SCIENTIFIC_DELIVERY';row['input_holds']=holds
    native.update_authority(close);write(T/'analysis/BATCH_NATIVE_CLOSED.json',dict(state,state='ALL_APPLICABLE_NATIVE_ATTEMPTS_CLOSED_ARCHIVED_RESTORED_WITH_CLASSIFIED_FAILURES',input_holds=holds,closed_unaccepted_points={k:v for k,v in results.items() if v['state'].startswith('FAIL_CLOSED')}));event({'state':'NATIVE_MATRIX_CLOSED_REQUIRES_FINAL_SCIENTIFIC_DELIVERY','accepted':passed,'input_holds':len(holds)});return
   time.sleep(1 if launched else 10)
if __name__=='__main__':
 try:main()
 except BaseException as e:event({'state':'CONTROLLER_ERROR_PRESERVE_ALL_INTENTS_NO_RETRY','error':repr(e)});raise
