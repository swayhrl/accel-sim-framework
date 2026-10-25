"""Single epoch2 parent: original40 plus independently authorized repair23.
Original spent ledgers/failed identities remain immutable. No automatic model retry.
"""
import pathlib,json,hashlib,importlib.util,os,fcntl,time,datetime,subprocess,concurrent.futures,copy
P=pathlib.Path;T=P('/root/data/dtc_main_v100_sweep_20261025_v1');N=P('/root/data/ep_l2_dtc_l1_native_v2');F=P('/root/data/dtc_failure_repair_20261025_v1');R=F/'validation';O=F/'ops';ORIGINAL='DTC_AE_V100_FULL_SWEEP_20261025_V1';REPAIR='DTC_AE_FAILURE_REPAIR_VALIDATION_20261025_V1';G=1024**3
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def write(p,r,exclusive=False):
 p=P(p);p.parent.mkdir(parents=True,exist_ok=True)
 if exclusive:
  with p.open('x') as f:json.dump(r,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 else:
  tmp=p.with_name(p.name+'.r13writing');tmp.write_text(json.dumps(r,indent=2)+'\n');tmp.replace(p)
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def event(state,**kw):
 r=dict(state=state,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),**kw);print(json.dumps(r),flush=True)
 with (R/'logs/CONTROLLER_R14_EVENTS.jsonl').open('a') as f:f.write(json.dumps(r)+'\n')
def live(b):
 try:s=(P('/proc')/str(b['pid'])/'stat').read_text().rsplit(')',1)[1].split();return int(s[19])==b['start_ticks'] and s[0] not in ['Z','X']
 except (FileNotFoundError,ProcessLookupError):return False
def model_live(root,row):
 p=root/'DTC/run/results'/row['uuid']/'NATIVE_SIMULATOR_PID_AND_MAPS.json';return p.exists() and live(read(p))
def admit_order(q,root,claims,cooldown,now,blocked=()):
 return sorted([c for c in q['admitted_specs'] if c not in blocked and c not in q['consumed'] and c not in q.get('sealed',[]) and c not in claims and cooldown.get(c,0)<=now],key=lambda c:(read(root/'control'/((c+'_SPEC.json') if root==T else ('specs/'+c+'.json')))['expected']['instructions'],c))
def safe_call(fn,c):
 try:return fn(c)
 except BaseException as e:return dict(state='ENGINEERING_ISSUE_PRESERVE_ACTUAL_ARTIFACTS',cohort=c,error=repr(e),model_retries=0)
def assert_zero_start_compatibility(prior,candidate):
 assert prior['budget']==prior['remaining']==23 and prior['consumed']=={},'R14 may only continue the exact never-started repair request'
 assert set(prior['admitted_specs'])==set(candidate['admitted_specs']) and len(candidate['admitted_specs'])==23
 assert not list((R/'control/qualification_ledger').glob('E2-AEREPAIR-*.INTENT.json'))
 assert not list((N/'control/science_authority/requests'/REPAIR).glob('*.INTENT.json'))
 for cell,expected in candidate['admitted_specs'].items():
  assert cell.startswith('E2-AEREPAIR-')
  canonical=R/'control/specs'/(cell+'.json');alias=R/'control'/(cell+'_SPEC.json')
  assert canonical.is_file() and alias.is_file() and canonical.read_bytes()==alias.read_bytes()
  assert sha(canonical)==sha(alias)==expected,'native spec compatibility alias must equal frozen canonical bytes'
  assert not (R/'control/qualification_ledger'/(cell+'.DONE.json')).exists()

def preserve_zero_start_engineering_results(candidate):
 # Only never-started NEW repair metadata is moved. Original288 and all
 # historical INTENT/DONE/source assets remain untouched, without refund.
 target=R/'analysis/prelaunch_engineering_preimages/R13_zero_start'
 assert not target.exists();target.mkdir(parents=True)
 rows=[]
 for cell in candidate['admitted_specs']:
  source=R/'analysis'/(cell+'.RESULT.json');result=read(source)
  assert result['cohort']==cell and result['state']=='REPAIR_ENGINEERING_ISSUE_PRESERVE_ACTUAL_ARTIFACTS'
  assert result['model_retries']==0 and result['original_models_or_ledgers_touched'] is False
  assert str(R/'control'/(cell+'_SPEC.json')) in result['error'] and 'No such file or directory' in result['error']
  destination=target/source.name;assert not destination.exists()
  original=source.read_bytes();digest=sha(source);source.replace(destination)
  assert not source.exists() and destination.read_bytes()==original and sha(destination)==digest
  rows.append(dict(cohort=cell,source=str(source),preserved_at=str(destination),sha256=digest,bytes=len(original),scientific_starts=0))
 write(R/'control/R13_ZERO_START_RESULT_PREIMAGES_R14.json',dict(schema='R14_PRESERVED_R13_PREINTENT_ENGINEERING_METADATA_V1',rows=rows,count=len(rows),original288_touched=False,budget_refund=0,scientific_starts=0),True)

def main():
 assert not (R/'control/CONTROLLER_START_R14.json').exists(),'one-shot controller; explicit continuation required after any exit'
 qual=read(O/'R14_ZERO_MODEL_QUALIFICATION_V1.json');pub=read(O/'R14_PUBLICATION_READBACK_V1.json');assert qual['status']=='PASS' and pub['verified'] and pub['controller_sha256']==qual['controller_sha256']==sha(__file__)
 assert pub['qualification_sha256']==sha(O/'R14_ZERO_MODEL_QUALIFICATION_V1.json')
 for pin in qual['source_pins']:assert sha(pin['path'])==pin['sha256']
 old=load('r13_old_ops',T/'tools/revision12b/sweep_controller.py');n=load('r13_original_authority',T/'tools/sweep_native_cap1m.py');rn=load('r13_repair_authority',R/'tools/repair_native_v1.py');ops=load('r13_repair_ops',R/'tools/repair_ops_v1.py')
 owner=(T/'control/FINITE_CONTROLLER.lock').open('a+b');fcntl.flock(owner,fcntl.LOCK_EX);held=(N/'control/qualification_ledger/NATIVE_QUALIFICATION.lock').open('rb');fcntl.flock(held,fcntl.LOCK_EX)
 prior=read(T/'control/BATCH_LEASE.json');assert not live(prior),'prior metadata parent must have exited without signaling models'
 assert not (T/'control/ABORT').exists() and not (R/'control/ABORT').exists()
 reg,epoch=n.read_current_authority();before=copy.deepcopy(reg['registered_future_requests'][ORIGINAL]);repair_before=copy.deepcopy(reg['registered_future_requests'][REPAIR]);candidate=read(R/'control/REGISTRY_REQUEST_CANDIDATE_V1.json');assert candidate['budget']==23 and candidate['remaining']==23 and candidate['consumed']=={} and candidate['orchestrator_sha256']==sha(__file__)
 assert_zero_start_compatibility(repair_before,candidate)
 assert prior['controller_sha256']==qual['prior_controller_sha256']=='3c75d688788076bcb9f9cbd66ce6478a198d1569f8b7779b2a7c043c09555e96'
 auth=read(R/'control/SCIENCE_AUTHORIZATION.json');assert auth['explicit_user_approval'] and auth['approval_request_sha256']==sha(R/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json') and set(auth['budgets'])==set(candidate['admitted_specs']) and set(auth['budgets'].values())=={1}
 forensic=read(O/'OBSERVER_OLD_ATTEMPTS_FORENSIC_V1.json');exceptions=set(qual['reviewed_original_engineering_issues']);assert exceptions=={'E2-AEV100-85700545918390d7-DM','E2-AEV100-e7c791ce2e4b09ee-DM'}
 for c in exceptions:assert c in before['consumed'] and 'execution_receipt' not in before['consumed'][c] and not model_live(T,before['consumed'][c]) and not (T/'control/qualification_ledger'/(c+'.DONE.json')).exists()
 # Registration itself must be safe for unchanged original runtime peer-reservation checks.
 base=n.resources({'cohort':'R14_REGISTRATION_METADATA'},False);extra=max(0,candidate['reserved_write_bytes']-repair_before['reserved_write_bytes']);assert base['physical_disk_pass'] and base['native_free_bytes']>base['required_free_bytes']+extra
 write(R/'control/ORIGINAL_REQUEST_BEFORE_R14.json',before,True)
 write(R/'control/REPAIR_ZERO_START_REQUEST_BEFORE_R14.json',repair_before,True)
 preserve_zero_start_engineering_results(candidate)
 def activate(registry):
  q=registry['registered_future_requests'][ORIGINAL];assert q==before and registry['registered_future_requests'][REPAIR]==repair_before;q['orchestrator_sha256']=sha(__file__);q.setdefault('operational_continuations',[]).append(dict(revision='R14_ZERO_START_COMPATIBILITY_ORIGINAL40_PLUS_REPAIR23',controller_sha256=sha(__file__),publication_commit=pub['commit'],qualification_sha256=sha(O/'R14_ZERO_MODEL_QUALIFICATION_V1.json'),spent_prefix=len(before['consumed']),original_model_retries=0,known_unaccepted_receipt_issues=sorted(exceptions),original_matrix_completion_blocked_by_missing_receipts=True));registry['registered_future_requests'][REPAIR]=copy.deepcopy(candidate);registry['registered_future_requests'][REPAIR].setdefault('operational_continuations',[]).append(dict(revision='R14_ZERO_START_COMPATIBILITY_METADATA_ONLY',prior_request_snapshot_sha256=sha(R/'control/REPAIR_ZERO_START_REQUEST_BEFORE_R14.json'),prior_consumed=0,prior_remaining=23,budget_added=0,model_retries=0))
 n.update_authority(activate)
 lease=dict(pid=os.getpid(),start_ticks=int(P('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19]),fd=held.fileno(),request=ORIGINAL,additional_requests=[REPAIR],controller_sha256=sha(__file__),scope='Original40 unchanged source+separate repair23 correctness;old observer receipts remain unaccepted')
 write(T/'control/BATCH_LEASE.json',lease);write(R/'control/CONTROLLER_START_R14.json',lease,True)
 entry=N/'bin/native';prior_bytes=entry.read_bytes();assert sha(entry)==qual['prior_entry_sha256'];write(R/'control/NATIVE_ENTRY_BEFORE_R14.json',dict(text=prior_bytes.decode(),sha256=sha(entry),entry_byte_action='KEEP_ALREADY_INSTALLED_REPAIR_ROUTE'),True);assert prior_bytes.count(str(R/'tools/repair_frontend_v1.py').encode())==1 and str(T/'tools/sweep_frontend_host_v4.py').encode() not in prior_bytes;assert entry.read_bytes()==prior_bytes
 n=load('r13_scheduler_original_host',T/'tools/sweep_host_execution_v4.py').install(n);rn.registered();plan=rn.plan();cpu_pools={ORIGINAL:read(T/'control/HOST_EXECUTION_PLAN_V4.json')['model_CPUs'],REPAIR:plan['allowed_model_CPUs']};assert not set(cpu_pools[ORIGINAL])&set(cpu_pools[REPAIR]);limits={ORIGINAL:40,REPAIR:23};roots={ORIGINAL:T,REPAIR:R};claims={k:read(v/'control/POOL_DISPATCH_RESERVATIONS.json')['claims'] for k,v in roots.items()};running={};results={k:{} for k in roots};cooldown={};blocked={ORIGINAL:set(),REPAIR:set()};last_state=0
 good=old.OK|{'PASS_REPAIR_CORRECTNESS_STRICT_ARCHIVE_RESTORE','FAIL_REPAIR_VALIDATION_ARCHIVED_NO_RETRY'}
 def save_claims(k):write(roots[k]/'control/POOL_DISPATCH_RESERVATIONS.json',{'claims':claims[k]})
 def guard_actual_attempt(k,c):
  root=roots[k]
  while True:
   q=n.read_current_authority()[0]['registered_future_requests'][k];row=q['consumed'][c]
   if 'execution_receipt' in row:return old.finish_evidence(c) if k==ORIGINAL else ops.finish_evidence(c)
   pidfile=root/'DTC/run/results'/row['uuid']/'NATIVE_SIMULATOR_PID_AND_MAPS.json'
   if pidfile.exists() and not live(read(pidfile)):
    time.sleep(30);row=n.read_current_authority()[0]['registered_future_requests'][k]['consumed'][c]
    if 'execution_receipt' in row:continue
    return dict(state='ENGINEERING_MODEL_GONE_RECEIPT_MISSING_PRESERVED',cohort=c,accepted_cycles=None,model_retries=0)
   # A missing identity after INTENT is unknown, never proof of no model.
   time.sleep(5)
 def adopt(c):
  while True:
   q=n.read_current_authority()[0]['registered_future_requests'][ORIGINAL];row=q['consumed'][c]
   if 'execution_receipt' in row:return old.finish_evidence(c)
   if not model_live(T,row):
    # A frontend may be closing; only classify absent model after finite drain wait.
    time.sleep(30);q=n.read_current_authority()[0]['registered_future_requests'][ORIGINAL]
    if 'execution_receipt' in q['consumed'][c]:return old.finish_evidence(c)
    return dict(state='ORIGINAL_ENGINEERING_MISSING_RECEIPT_PRESERVED',cohort=c,accepted_cycles=None,model_retries=0)
   time.sleep(5)
 with concurrent.futures.ThreadPoolExecutor(max_workers=72) as pool:
  for c,row in before['consumed'].items():
   rp=T/'analysis'/(c+'.RESULT.json')
   if rp.exists() and read(rp)['state'] in old.OK:results[ORIGINAL][c]=read(rp);claims[ORIGINAL].pop(c,None);continue
   if c in exceptions:results[ORIGINAL][c]=dict(state='REVIEWED_OLD_OBSERVER_ENGINEERING_ISSUE_UNACCEPTED',cohort=c,accepted_cycles=None,forensic_path=str(O/'OBSERVER_OLD_ATTEMPTS_FORENSIC_V1.json'));claims[ORIGINAL].pop(c,None);continue
   assert 'execution_receipt' in row or c in claims[ORIGINAL]
   fn=old.finish_evidence if 'execution_receipt' in row else adopt;running[pool.submit(safe_call,fn,c)]=dict(request=ORIGINAL,cell=c,cpu=claims[ORIGINAL].get(c,{}).get('host_cpu'),active='execution_receipt' not in row,adopted=True)
  save_claims(ORIGINAL)
  while True:
   assert not (T/'control/ABORT').exists() and not (R/'control/ABORT').exists()
   for future,meta in list(running.items()):
    if not future.done():continue
    result=future.result();k=meta['request'];c=meta['cell'];running.pop(future);latest=n.read_current_authority()[0]['registered_future_requests'][k];row=latest['consumed'].get(c);pidfile=roots[k]/'DTC/run/results'/row['uuid']/'NATIVE_SIMULATOR_PID_AND_MAPS.json' if row else None
    uncertain_live=row is not None and 'execution_receipt' not in row and (not pidfile.exists() or live(read(pidfile)))
    if uncertain_live:
     assert c in claims[k];running[pool.submit(safe_call,lambda cell,request=k:guard_actual_attempt(request,cell),c)]=dict(meta,active=True,engineering_guard=True);write(roots[k]/'analysis'/(c+'.ENGINEERING_ACTIVE_GUARD.json'),result);event('ENGINEERING_GUARD_RETAIN_CLAIM_AND_SLOT',request=k,cohort=c);continue
    claims[k].pop(c,None);save_claims(k)
    if result['state'] in ['ADMISSION_DEFERRED_ZERO_START','REPAIR_ADMISSION_DEFERRED_ZERO_START']:
     assert c not in n.read_current_authority()[0]['registered_future_requests'][k]['consumed'];cooldown[c]=time.monotonic()+30;event('ADMISSION_DEFERRED_ZERO_START',request=k,cohort=c);continue
    results[k][c]=result
    if result['state'] not in good:blocked[k].add(c)
    write(roots[k]/'analysis'/(c+'.RESULT.json'),result);event(result['state'],request=k,cohort=c)
   # Repair is prioritized; its slots are independent of original40. Claims serialize resources.
   launched=0
   for k in [REPAIR,ORIGINAL]:
    reg,epoch=n.read_current_authority();q=reg['registered_future_requests'][k];active=sum(1 for m in running.values() if m['request']==k and m['active']);used={m['cpu'] for m in running.values() if m['cpu'] is not None}
    for c in admit_order(q,roots[k],claims[k],cooldown,time.monotonic(),blocked[k]):
     if active>=limits[k]:break
     slots=[cpu for cpu in cpu_pools[k] if cpu not in used]
     if not slots:break
     s=rn.spec_for(c) if k==REPAIR else n.spec_for(c);r=rn.resources(s,True)
     if not (r['physical_RAM_pass'] and r['physical_disk_pass']):continue
     if k==ORIGINAL:
      legacy=n.resources(s,True)
      if not (legacy['physical_RAM_pass'] and legacy['physical_disk_pass']):continue
     cpu=slots[0];cap=rn.output_cap(s) if k==REPAIR else s['limits']['max_result_directory_bytes'];claims[k][c]=dict(host_cpu=cpu,result_cap_bytes=cap,RAM_cap_bytes=s['limits']['max_process_tree_rss_bytes']);save_claims(k);fn=ops.run_cell if k==REPAIR else old.run_cell;running[pool.submit(safe_call,fn,c)]=dict(request=k,cell=c,cpu=cpu,active=True,adopted=False);used.add(cpu);active+=1;launched+=1;event('DISPATCH_FRESH_EXACT_ATTEMPT',request=k,cohort=c,CPU=cpu)
   reg,epoch=n.read_current_authority();state=dict(state='R14_ORIGINAL40_PLUS_REPAIR23_BACKGROUND',observed_unix=time.time(),running=list(running.values()),original_consumed=len(reg['registered_future_requests'][ORIGINAL]['consumed']),repair_consumed=len(reg['registered_future_requests'][REPAIR]['consumed']),closed_result_counts={k:len(v) for k,v in results.items()},original_reviewed_missing_receipts=sorted(exceptions),original_matrix_complete=False,repair_maximum=23,original_maximum=40,automatic_model_retries=0,blocked_engineering_cells={k:sorted(v) for k,v in blocked.items()});write(R/'analysis/BATCH_STATE_R14.json',state);write(T/'analysis/BATCH_STATE.json',state)
   rq=reg['registered_future_requests'][REPAIR]
   if len(results[REPAIR])==23 and len(rq['consumed'])==23 and all((R/'control/qualification_ledger'/(c+'.DONE.json')).exists() for c in rq['consumed']) and all(x['state'] in good for x in results[REPAIR].values()) and not (R/'analysis/REPAIR_VALIDATION_CLOSED_V1.json').exists():
    status='ALL23_CORRECTNESS_VALIDATION_PASS' if all(x['state']=='PASS_REPAIR_CORRECTNESS_STRICT_ARCHIVE_RESTORE' for x in results[REPAIR].values()) else 'VALIDATION_CLOSED_WITH_ARCHIVED_FAILURES'
    write(R/'analysis/REPAIR_VALIDATION_CLOSED_V1.json',dict(status=status,results=results[REPAIR],accepted_cycles=None,original_matrix_unmodified=True),True)
    def close_repair(registry):
     q=registry['registered_future_requests'][REPAIR];assert len(q['consumed'])==23 and q['remaining']==0;q.update(state='CLOSED',validation_status=status,reserved_write_bytes=G,all23_archived_and_native_restored=True,original_performance_points_added=0)
    rn.update_authority(close_repair);event('REPAIR23_CLOSED_SOURCE_KEEP_FOREIGN_WRITE_CAPACITY_RELEASED',validation_status=status,remaining_metadata_reservation_bytes=G)
   pending_any=any(set(reg['registered_future_requests'][k]['admitted_specs'])-set(reg['registered_future_requests'][k]['consumed'])-set(reg['registered_future_requests'][k].get('sealed',[])) for k in roots)
   if not running and not pending_any:event('R14_ALL_ADMITTED_DISPATCH_CLOSED_OLD_RECEIPT_ISSUES_PRESERVED');return
   time.sleep(1 if launched else 10)
if __name__=='__main__':
 try:main()
 except BaseException as e:event('R14_CONTROLLER_ERROR_NO_RETRY_PRESERVE_CHILDREN',error=repr(e));raise
