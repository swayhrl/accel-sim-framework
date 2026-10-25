"""Single epoch2 parent: original40 plus independently authorized repair23.
Original spent ledgers/failed identities remain immutable. No automatic model retry.
"""
import pathlib,json,hashlib,importlib.util,os,fcntl,time,datetime,subprocess,concurrent.futures,copy
P=pathlib.Path;T=P('/root/data/dtc_main_v100_sweep_20261025_v1');N=P('/root/data/ep_l2_dtc_l1_native_v2');F=P('/root/data/dtc_failure_repair_20261025_v1');R=F/'validation_lava_memory_v2';L=F/'validation_late_failure_v1';O=F/'ops';ORIGINAL='DTC_AE_V100_FULL_SWEEP_20261025_V1';OLD_REPAIR='DTC_AE_FAILURE_REPAIR_VALIDATION_20261025_V1';OLD_ROOT=F/'validation';REPAIR='DTC_AE_LAVAMEM_REPAIR_20261026_V2';LATE='DTC_AE_LATE_FAILURE_REPAIR_20261026_V1';G=1024**3
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
 with (R/'logs/CONTROLLER_R16_EVENTS.jsonl').open('a') as f:f.write(json.dumps(r)+'\n')
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
def main():
 assert not (L/'control/CONTROLLER_START_R16.json').exists(),'One-shot;explicit qualified continuation after exit'
 qual=read(O/'R16_ZERO_MODEL_QUALIFICATION_V1.json');pub=read(O/'R16_PUBLICATION_READBACK_V1.json');assert qual['status']=='PASS' and pub['verified'] and qual['controller_sha256']==pub['controller_sha256']==sha(__file__) and pub['qualification_sha256']==sha(O/'R16_ZERO_MODEL_QUALIFICATION_V1.json')
 for pin in qual['source_pins']:assert sha(pin['path'])==pin['sha256']
 old=load('r16_original_ops',T/'tools/revision12b/sweep_controller.py');n=load('r16_authority',T/'tools/sweep_native_cap1m.py');lava=load('r16_lava',R/'tools/lavamem_native_v2.py');late=load('r16_late',L/'tools/late_native_v1.py');lop=load('r16_lava_ops',R/'tools/lavamem_ops_v2.py');xop=load('r16_late_ops',L/'tools/late_ops_v1.py')
 owner=(T/'control/FINITE_CONTROLLER.lock').open('a+b');fcntl.flock(owner,fcntl.LOCK_EX);held=(N/'control/qualification_ledger/NATIVE_QUALIFICATION.lock').open('rb');fcntl.flock(held,fcntl.LOCK_EX)
 prior=read(T/'control/BATCH_LEASE.json');assert not live(prior) and prior['controller_sha256']==qual['prior_controller_sha256']=='e33951d0d53677681e422a4e28005327e0b33c4492a1eb7fc02121daa492e413'
 assert not any((root/'control/ABORT').exists() for root in [T,R,L])
 reg,epoch=n.read_current_authority();before=copy.deepcopy(reg['registered_future_requests'][ORIGINAL]);previous=copy.deepcopy(reg['registered_future_requests'][OLD_REPAIR]);assert len(previous['consumed'])==23 and previous['remaining']==0
 barrier=before['operational_repair_admission_barrier'];assert barrier['status']=='NEW_ORIGINAL_ADMISSION_PAUSED_FOR_QUALIFIED_REPAIR_SUPPLEMENT';assert set(before['sealed'])==set(barrier['original_sealed'])|set(barrier['added_cells']);assert not set(barrier['added_cells'])&set(before['consumed'])
 roots={ORIGINAL:T,REPAIR:R,LATE:L};engines={REPAIR:lava,LATE:late};ops={REPAIR:lop,LATE:xop};budgets={REPAIR:2,LATE:4};candidates={}
 for k in [REPAIR,LATE]:
  root=roots[k];candidate=read(root/'control/REGISTRY_REQUEST_CANDIDATE_V1.json');assert k not in reg['registered_future_requests'] and candidate['budget']==candidate['remaining']==budgets[k] and candidate['consumed']=={} and candidate['orchestrator_sha256']==sha(__file__);assert not list((root/'control/qualification_ledger').glob('*.INTENT.json'));auth=read(root/'control/SCIENCE_AUTHORIZATION.json');assert auth['explicit_user_approval'] and auth['approval_request_sha256']==sha(root/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json') and set(auth['budgets'])==set(candidate['admitted_specs']) and set(auth['budgets'].values())=={1}
  for c,digest in candidate['admitted_specs'].items():assert sha(root/'control/specs'/(c+'.json'))==sha(root/'control'/(c+'_SPEC.json'))==digest
  candidates[k]=candidate
 assert candidates[REPAIR]['reserved_write_bytes']==3*G//2 and candidates[LATE]['reserved_write_bytes']==3*G
 exceptions=set(qual['reviewed_original_engineering_issues']);assert exceptions=={'E2-AEV100-85700545918390d7-DM','E2-AEV100-e7c791ce2e4b09ee-DM'}
 for c in exceptions:assert c in before['consumed'] and 'execution_receipt' not in before['consumed'][c] and not model_live(T,before['consumed'][c]) and not (T/'control/qualification_ledger'/(c+'.DONE.json')).exists()
 for c,row in previous['consumed'].items():assert (OLD_ROOT/'DTC/run/results'/row['uuid']/'NATIVE_LAUNCH.json').exists()
 base=n.resources({'cohort':'R16_REGISTER6_METADATA'},False);assert base['physical_disk_pass'] and base['native_free_bytes']>base['required_free_bytes']+sum(x['reserved_write_bytes'] for x in candidates.values())
 write(L/'control/ORIGINAL_REQUEST_BEFORE_R16.json',before,True);write(L/'control/OLD_REPAIR_REQUEST_BEFORE_R16.json',previous,True)
 def activate(registry):
  q=registry['registered_future_requests'][ORIGINAL];assert set(q['consumed'])==set(before['consumed']) and q['orchestrator_sha256']==before['orchestrator_sha256'];assert q['operational_repair_admission_barrier']==barrier and set(q['sealed'])==set(before['sealed'])
  assert all({a:b for a,b in row.items() if a!='execution_receipt'}=={a:b for a,b in before['consumed'][c].items() if a!='execution_receipt'} for c,row in q['consumed'].items())
  q['sealed']=sorted(set(q['sealed'])-set(barrier['added_cells']));assert set(q['sealed'])==set(barrier['original_sealed']);q['operational_repair_admission_barrier']=dict(barrier,status='RELEASED_BY_QUALIFIED_R16',release_controller_sha256=sha(__file__),release_publication_commit=pub['commit']);q['orchestrator_sha256']=sha(__file__);q.setdefault('operational_continuations',[]).append(dict(revision='R16_ORIGINAL40_OLD23_CONTINUE_NEW_LAVA2_LATE4',controller_sha256=sha(__file__),publication_commit=pub['commit'],original_spent_prefix=len(before['consumed']),new_finite_budgets=budgets,old_receipt_issues_preserved=sorted(exceptions)))
  for k,candidate in candidates.items():assert k not in registry['registered_future_requests'];registry['registered_future_requests'][k]=copy.deepcopy(candidate)
 n.update_authority(activate)
 lease=dict(pid=os.getpid(),start_ticks=int(P('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19]),fd=held.fileno(),request=ORIGINAL,additional_requests=[OLD_REPAIR,REPAIR,LATE],controller_sha256=sha(__file__),scope='Original40 unchanged;old23 models continue and metadata V2 closes;new finite lava2 and late4;no spent retries')
 write(T/'control/BATCH_LEASE.json',lease);write(L/'control/CONTROLLER_START_R16.json',lease,True)
 entry=N/'bin/native';prior_bytes=entry.read_bytes();assert sha(entry)==qual['prior_entry_sha256'];write(L/'control/NATIVE_ENTRY_BEFORE_R16.json',dict(text=prior_bytes.decode(),sha256=sha(entry)),True);a=str(OLD_ROOT/'tools/repair_frontend_v1.py').encode();b=str(L/'tools/late_frontend_v1.py').encode();assert prior_bytes.count(a)==1;temp=entry.with_name('.native.R16writing');temp.write_bytes(prior_bytes.replace(a,b));temp.chmod(entry.stat().st_mode&0o777);temp.replace(entry)
 n=load('r16_host',T/'tools/sweep_host_execution_v4.py').install(n)
 for e in engines.values():e.registered()
 pools={ORIGINAL:read(T/'control/HOST_EXECUTION_PLAN_V4.json')['model_CPUs'],REPAIR:lava.plan()['allowed_model_CPUs'],LATE:late.plan()['allowed_model_CPUs']};old_plan=read(OLD_ROOT/'control/EXECUTION_PLAN_V1.json');assert sha(OLD_ROOT/'control/EXECUTION_PLAN_V1.json')==previous['execution_plan_sha256'];old_cpus=set(old_plan['allowed_model_CPUs'])|{x['host_cpu'] for x in read(OLD_ROOT/'control/POOL_DISPATCH_RESERVATIONS.json')['claims'].values()}
 for k in [REPAIR,LATE]:assert not set(pools[k])&old_cpus and not set(pools[k])&set(pools[ORIGINAL])
 assert not set(pools[REPAIR])&set(pools[LATE]);limits={ORIGINAL:40,REPAIR:2,LATE:4};claims={k:read(root/'control/POOL_DISPATCH_RESERVATIONS.json')['claims'] for k,root in roots.items()};running={};results={k:{} for k in roots};blocked={k:set() for k in roots};cooldown={};good=old.OK|{'PASS_REPAIR_CORRECTNESS_STRICT_ARCHIVE_RESTORE','FAIL_REPAIR_VALIDATION_ARCHIVED_NO_RETRY'}
 def save(k):write(roots[k]/'control/POOL_DISPATCH_RESERVATIONS.json',{'claims':claims[k]})
 def finish(k,c):return old.finish_evidence(c) if k==ORIGINAL else ops[k].finish_evidence(c)
 def guard(k,c):
  while True:
   row=n.read_current_authority()[0]['registered_future_requests'][k]['consumed'][c]
   if 'execution_receipt' in row:return finish(k,c)
   pidfile=roots[k]/'DTC/run/results'/row['uuid']/'NATIVE_SIMULATOR_PID_AND_MAPS.json'
   if pidfile.exists() and not live(read(pidfile)):
    time.sleep(30);row=n.read_current_authority()[0]['registered_future_requests'][k]['consumed'][c]
    if 'execution_receipt' not in row:return dict(state='ENGINEERING_MODEL_GONE_RECEIPT_MISSING_PRESERVED',cohort=c,accepted_cycles=None,model_retries=0)
   time.sleep(5)
 with concurrent.futures.ThreadPoolExecutor(max_workers=72) as pool:
  for c,row in before['consumed'].items():
   rp=T/'analysis'/(c+'.RESULT.json')
   if rp.exists() and read(rp)['state'] in old.OK:results[ORIGINAL][c]=read(rp);claims[ORIGINAL].pop(c,None);continue
   if c in exceptions:results[ORIGINAL][c]=dict(state='REVIEWED_OLD_OBSERVER_ENGINEERING_ISSUE_UNACCEPTED',cohort=c,accepted_cycles=None);claims[ORIGINAL].pop(c,None);continue
   assert 'execution_receipt' in row or c in claims[ORIGINAL];running[pool.submit(safe_call,lambda cell:guard(ORIGINAL,cell),c)]=dict(request=ORIGINAL,cell=c,cpu=claims[ORIGINAL].get(c,{}).get('host_cpu'),active='execution_receipt' not in row,adopted=True)
  save(ORIGINAL)
  while True:
   assert not any((root/'control/ABORT').exists() for root in roots.values())
   for future,meta in list(running.items()):
    if not future.done():continue
    result=future.result();k=meta['request'];c=meta['cell'];running.pop(future);latest=n.read_current_authority()[0]['registered_future_requests'][k];row=latest['consumed'].get(c);pidfile=roots[k]/'DTC/run/results'/row['uuid']/'NATIVE_SIMULATOR_PID_AND_MAPS.json' if row else None
    if row is not None and 'execution_receipt' not in row and (not pidfile.exists() or live(read(pidfile))):
     assert c in claims[k];running[pool.submit(safe_call,lambda cell,request=k:guard(request,cell),c)]=dict(meta,active=True,engineering_guard=True);write(roots[k]/'analysis'/(c+'.ENGINEERING_ACTIVE_GUARD.json'),result);continue
    claims[k].pop(c,None);save(k)
    if result['state'] in ['ADMISSION_DEFERRED_ZERO_START','REPAIR_ADMISSION_DEFERRED_ZERO_START']:
     assert c not in latest['consumed'];cooldown[c]=time.monotonic()+30;event('ADMISSION_DEFERRED_ZERO_START',request=k,cohort=c);continue
    results[k][c]=result
    if result['state'] not in good:blocked[k].add(c)
    write(roots[k]/'analysis'/(c+'.RESULT.json'),result);event(result['state'],request=k,cohort=c)
   launched=0
   for k in [LATE,REPAIR,ORIGINAL]:
    reg,epoch=n.read_current_authority();q=reg['registered_future_requests'][k];active=sum(m['request']==k and m['active'] for m in running.values());used={m['cpu'] for m in running.values() if m['cpu'] is not None}
    if k==ORIGINAL:
     bigq=reg['registered_future_requests'][REPAIR];big_pending=set(bigq['admitted_specs'])-set(bigq['consumed'])-blocked[REPAIR];big_active=any(m['request']==REPAIR and m['active'] for m in running.values())
     if big_pending and not big_active:continue
    for c in admit_order(q,roots[k],claims[k],cooldown,time.monotonic(),blocked[k]):
     if active>=limits[k]:break
     slots=[cpu for cpu in pools[k] if cpu not in used]
     if not slots:break
     s=n.spec_for(c) if k==ORIGINAL else engines[k].spec_for(c);sample=late.resources(s,True)
     if not(sample['physical_RAM_pass'] and sample['physical_disk_pass']):continue
     if k==ORIGINAL:
      original_sample=n.resources(s,True)
      if not(original_sample['physical_RAM_pass'] and original_sample['physical_disk_pass']):continue
     # Any old pre-fork failure record is preserved before a genuinely unused start.
     rp=roots[k]/'analysis'/(c+'.RESULT.json')
     if rp.exists():
      assert c not in q['consumed'] and not (roots[k]/'control/qualification_ledger'/(c+'.INTENT.json')).exists() and read(rp)['state'] not in good;target=roots[k]/'analysis/zero_start_preimages_R16'/rp.name;target.parent.mkdir(exist_ok=True);assert not target.exists();digest=sha(rp);rp.replace(target);assert sha(target)==digest
     cpu=slots[0];cap=s['limits']['max_result_directory_bytes'] if k==ORIGINAL else engines[k].output_cap(s);claims[k][c]=dict(host_cpu=cpu,result_cap_bytes=cap,RAM_cap_bytes=s['limits']['max_process_tree_rss_bytes']);save(k);fn=old.run_cell if k==ORIGINAL else ops[k].run_cell;running[pool.submit(safe_call,fn,c)]=dict(request=k,cell=c,cpu=cpu,active=True,adopted=False);active+=1;used.add(cpu);launched+=1;event('DISPATCH_FRESH_EXACT_ATTEMPT',request=k,cohort=c,CPU=cpu)
   reg,epoch=n.read_current_authority();state=dict(state='R16_ORIGINAL40_OLD23_CONTINUE_LAVA2_LATE4',observed_unix=time.time(),running=list(running.values()),consumed={k:len(reg['registered_future_requests'][k]['consumed']) for k in roots},closed_results={k:len(v) for k,v in results.items()},blocked={k:sorted(v) for k,v in blocked.items()},old_repair_closed_by_independent_postprocess_v2=True,original_matrix_complete=False,old_missing_receipts=sorted(exceptions),automatic_model_retries=0);write(L/'analysis/BATCH_STATE_R16.json',state);write(T/'analysis/BATCH_STATE.json',state)
   for k in [REPAIR,LATE]:
    q=reg['registered_future_requests'][k];marker=roots[k]/'analysis/VALIDATION_CLOSED_R16.json'
    if len(results[k])==budgets[k] and len(q['consumed'])==budgets[k] and all((roots[k]/'control/qualification_ledger'/(c+'.DONE.json')).exists() for c in q['consumed']) and all(r['state'] in good for r in results[k].values()) and not marker.exists():
     status='ALL_FINITE_CORRECTNESS_VALIDATION_PASS' if all(r['state']=='PASS_REPAIR_CORRECTNESS_STRICT_ARCHIVE_RESTORE' for r in results[k].values()) else 'CLOSED_WITH_ARCHIVED_NATIVE_FAILURES';write(marker,dict(status=status,results=results[k],accepted_cycles=None,original288_unmodified=True),True)
     def close(registry,request=k,validation_status=status):
      row=registry['registered_future_requests'][request];assert len(row['consumed'])==budgets[request] and row['remaining']==0;row.update(state='CLOSED',reserved_write_bytes=G,validation_status=validation_status,all_archived_and_native_restored=True)
     engines[k].update_authority(close)
   pending=any(set(reg['registered_future_requests'][k]['admitted_specs'])-set(reg['registered_future_requests'][k]['consumed'])-set(reg['registered_future_requests'][k].get('sealed',[])) for k in roots)
   if not running and not pending:event('R16_ALL_FINITE_STARTS_CLOSED_OLD_RECEIPT_ISSUES_PRESERVED');return
   time.sleep(1 if launched else 10)
if __name__=='__main__':
 try:main()
 except BaseException as e:event('R16_CONTROLLER_ERROR_PRESERVE_MODELS_NO_RETRY',error=repr(e));raise
