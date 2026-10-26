"""R20 sole metadata parent: adopt original science, run finite RECOVER12.
No original attempt is retried/refunded; repaired-source results are correctness
only. Old four repair scopes and their histories remain immutable.
"""
import pathlib,json,hashlib,importlib.util,os,fcntl,time,datetime,copy,subprocess,concurrent.futures,gzip
P=pathlib.Path;T=P('/root/data/dtc_main_v100_sweep_20261025_v1');N=P('/root/data/ep_l2_dtc_l1_native_v2');F=P('/root/data/dtc_failure_repair_20261025_v1');O=F/'ops';D=O/'revision20';R=F/'validation_storage_recovery12_v1';ORIGINAL='DTC_AE_V100_FULL_SWEEP_20261025_V1';REQ='DTC_AE_STORAGE_RECOVERY12_20261026_V1';OLD=['DTC_AE_FAILURE_REPAIR_VALIDATION_20261025_V1','DTC_AE_LAVAMEM_REPAIR_20261026_V2','DTC_AE_LATE_FAILURE_REPAIR_20261026_V1','DTC_AE_REMAINING_FAILURE_REPAIR_20261026_V1'];PRIOR='c4cc1f48e404f949afb5bfe942044031bfc6650fe6f4032b97757b370f82f532';G=1024**3
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def write(p,x,exclusive=False):
 p=P(p);p.parent.mkdir(parents=True,exist_ok=True)
 if exclusive:
  with p.open('x')as f:json.dump(x,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 else:
  tmp=p.with_name(p.name+'.R20writing');tmp.write_text(json.dumps(x,indent=2)+'\n');tmp.replace(p)
def load(name,p):s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def event(state,**kw):
 row=dict(state=state,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),**kw);print(json.dumps(row),flush=True)
 with(R/'logs/CONTROLLER_R20_EVENTS.jsonl').open('a')as f:f.write(json.dumps(row)+'\n')
def live(b):
 try:s=(P('/proc')/str(b['pid'])/'stat').read_text().rsplit(')',1)[1].split();return int(s[19])==b['start_ticks']and s[0]not in['Z','X']
 except(FileNotFoundError,ProcessLookupError):return False
def model_live(root,row):
 p=root/'DTC/run/results'/row['uuid']/'NATIVE_SIMULATOR_PID_AND_MAPS.json';return p.exists()and live(read(p))
def safe_call(fn,c):
 try:return fn(c)
 except BaseException as e:return dict(state='ENGINEERING_ISSUE_PRESERVE_ACTUAL_ARTIFACTS',cohort=c,error=repr(e),accepted_cycles=None,model_retries=0)
def ready(sample):return sample['physical_RAM_pass']and sample['physical_disk_pass']and sample['native_free_bytes']-sample['required_free_bytes']>=5*G
def admit_order(q,root,claims,cooldown,now):
 cells=set(q['admitted_specs'])-set(q['consumed'])-set(q.get('sealed',[]))-set(claims)
 def key(c):
  s=read(root/'control/specs'/(c+'.json'));return(s['estimated_peak_model_RAM_bytes']>=96*G,s['expected']['instructions'],c)
 return sorted((c for c in cells if cooldown.get(c,0)<=now),key=key)
def original_archive(cell,copygate):
 ob=load('r20_private_original_archive_'+cell,T/'tools/sweep_outbox.py');ob=copygate.install_private_outbox(ob,ORIGINAL,cohort=cell);ap=T/'control'/(cell+'_ARCHIVE_RECEIPT.json');began=time.monotonic()
 while True:
  if ap.exists():
   receipt=read(ap);manifest=ob.manifest_for(cell);bundle=P(receipt['target_mount_path']);assert read(bundle/'SOURCE_MANIFEST.json')==manifest;f,v=ob.libraries(bundle);idx=f.verify_archive(bundle,manifest);proof=f.check_native(P(receipt['native_restore']),manifest);assert idx['archive_sha256']==receipt['archive_sha256']and len(proof)==len(manifest['entries']);return receipt
  try:ob.archive(cell)
  except BlockingIOError:assert time.monotonic()-began<21600;time.sleep(10)
  except(RuntimeError,AssertionError)as e:
   if 'HOLD'not in str(e)or time.monotonic()-began>=21600:raise
   time.sleep(10)
def original_finish(cell,native,copygate):
 # The old full strict comparator is retained. Only its private archive API is
 # replaced with the qualified current six-scope COPY gate, never its science.
 old=load('r20_original_strict_worker_'+cell,T/'tools/revision12b/sweep_controller.py');old.archive_closed=lambda c:original_archive(c,copygate)
 row=native.read_current_authority()[0]['registered_future_requests'][ORIGINAL]['consumed'][cell];ip=T/'control/qualification_ledger'/(cell+'.INTENT.json');intent=read(ip);out=P(intent['output']);done=read(out/'NATIVE_EXIT.json');assert row['intent_sha256']==sha(ip)and row['uuid']==intent['uuid']==done['uuid']and row['execution_receipt']==done==read(ip.with_name(cell+'.DONE.json'))
 if not done['stop_reason']and not done['launcher_wait_returncode']:return old.finish_evidence(cell)
 try:return old.finish_evidence(cell)
 except BaseException as classifier_error:
  # COPY a genuine closed native negative even when an old classifier lacks its
  # signature. This is explicitly unaccepted and requires subsequent diagnosis.
  pid=read(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json');assert not live(pid)and done['native_simulator_observed']and done['new_attempt_consumed']==1;assert sha(out/'raw.log.gz')==done['raw_sha256'];h=hashlib.sha256();size=0
  with gzip.open(out/'raw.log.gz','rb')as f:
   for chunk in iter(lambda:f.read(1024**2),b''):h.update(chunk);size+=len(chunk)
  assert h.hexdigest()==done['raw_uncompressed_sha256']and size==done['raw_uncompressed_bytes'];archive=original_archive(cell,copygate);assert archive['scientific_status']=='STOP_UNACCEPTED';proof=dict(state='FAIL_CLOSED_UNACCEPTED_ARCHIVED_NO_RETRY',cohort=cell,uuid=done['uuid'],failure_classification=dict(status='REAL_NATIVE_NEGATIVE_ROOT_CAUSE_REVIEW_REQUIRED',recorded_stop_reason=done['stop_reason'],actual_wait_returncode=done['launcher_wait_returncode'],legacy_classifier_error=repr(classifier_error),raw_compressed_sha256=done['raw_sha256'],raw_uncompressed_sha256=h.hexdigest()),archive=archive,accepted_cycles=None,partial_cycles_accepted=False,model_retries=0);write(F/'analysis/r20_original_negative_reviews'/(cell+'.json'),proof,True);return proof
def guard(root,request,cell,native,finish):
 while True:
  row=native.read_current_authority()[0]['registered_future_requests'][request]['consumed'][cell]
  if 'execution_receipt'in row:return finish(cell)
  pp=root/'DTC/run/results'/row['uuid']/'NATIVE_SIMULATOR_PID_AND_MAPS.json'
  if pp.exists()and not live(read(pp)):
   time.sleep(30);row=native.read_current_authority()[0]['registered_future_requests'][request]['consumed'][cell]
   if 'execution_receipt'not in row:return dict(state='ENGINEERING_MODEL_GONE_RECEIPT_MISSING_PRESERVED',cohort=cell,uuid=row['uuid'],accepted_cycles=None,model_retries=0)
  time.sleep(5)
def main():
 assert not(R/'control/CONTROLLER_START_R20.json').exists(),'One-shot controller generation; no blind scientific restart'
 qual=read(O/'R20_ZERO_MODEL_QUALIFICATION_V1.json');pub=read(O/'R20_PUBLICATION_READBACK_V1.json');assert qual['status']=='PASS'and pub['verified']and qual['controller_sha256']==pub['controller_sha256']==sha(__file__)and pub['qualification_sha256']==sha(O/'R20_ZERO_MODEL_QUALIFICATION_V1.json')
 for pin in qual['source_pins']:assert sha(pin['path'])==pin['sha256'],pin['path']
 native=load('r20_original_authority',T/'tools/sweep_native_cap1m.py');engine=load('r20_recover12_engine',R/'tools/recovery12_native_v1.py');ops=load('r20_recover12_ops',R/'tools/recovery12_ops_v1.py');accounting=load('r20_six_scope_resources',D/'resource_accounting_v1.py');copygate=load('r20_private_copy_gate',D/'copy_gate_v1.py')
 owner=(T/'control/FINITE_CONTROLLER.lock').open('a+b');fcntl.flock(owner,fcntl.LOCK_EX);held=(N/'control/qualification_ledger/NATIVE_QUALIFICATION.lock').open('rb');fcntl.flock(held,fcntl.LOCK_EX);prior=read(T/'control/BATCH_LEASE.json');assert prior['controller_sha256']==PRIOR and not live(prior);reg,epoch=native.read_current_authority();assert epoch['epoch']==2 and epoch['state']=='NATIVE_SCIENCE_ACTIVE'and epoch['holder']==os.uname().nodename;assert not any((p/'control/ABORT').exists()for p in[T,R])
 before=copy.deepcopy(reg['registered_future_requests'][ORIGINAL]);oldqs={k:copy.deepcopy(reg['registered_future_requests'][k])for k in OLD};assert all(q['state']=='CLOSED'and q['remaining']==0 for q in oldqs.values());assert before['budget']==356 and before['orchestrator_sha256']==PRIOR and not(set(before['admitted_specs'])-set(before['consumed'])-set(before.get('sealed',[])))
 candidate=read(R/'control/REGISTRY_REQUEST_CANDIDATE_V1.json');auth=read(R/'control/SCIENCE_AUTHORIZATION.json');assert REQ not in reg['registered_future_requests']and candidate['budget']==candidate['remaining']==12 and candidate['consumed']=={}and candidate['orchestrator_sha256']==sha(__file__);assert auth['explicit_user_approval']and auth['approval_request_sha256']==sha(R/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json')and set(auth['budgets'])==set(candidate['admitted_specs'])and set(auth['budgets'].values())=={1}
 for c,digest in candidate['admitted_specs'].items():assert sha(R/'control/specs'/(c+'.json'))==sha(R/'control'/(c+'_SPEC.json'))==digest
 assert not list((R/'control/qualification_ledger').glob('*.INTENT.json'))and not read(R/'control/POOL_DISPATCH_RESERVATIONS.json')['claims'];claims={ORIGINAL:read(T/'control/POOL_DISPATCH_RESERVATIONS.json')['claims'],REQ:{}};assert set(claims[ORIGINAL])<=set(before['consumed']);engine.verify_cpu_reuse();holes=set(qual['reviewed_original_receipt_gaps']);assert len(holes)==3
 closed={};adopt=[]
 for c,row in before['consumed'].items():
  dp=T/'control/qualification_ledger'/(c+'.DONE.json');pp=T/'DTC/run/results'/row['uuid']/'NATIVE_SIMULATOR_PID_AND_MAPS.json';ap=T/'control'/(c+'_ARCHIVE_RECEIPT.json')
  if c in holes:
   assert 'execution_receipt'not in row and not dp.exists()and not model_live(T,row);closed[c]=dict(state='REVIEWED_OLD_RECEIPT_GAP_UNACCEPTED',cohort=c,uuid=row['uuid'],accepted_cycles=None);continue
  if 'execution_receipt'in row:
   assert read(dp)==row['execution_receipt']==read(T/'DTC/run/results'/row['uuid']/'NATIVE_EXIT.json')and pp.exists()and not live(read(pp))
   if ap.exists():closed[c]=dict(state='PRESERVED_PRE_R20_REAL_DONE_ARCHIVE_RECEIPT',cohort=c,uuid=row['uuid'],archive_receipt_sha256=sha(ap));continue
   adopt.append(c);continue
  assert c in claims[ORIGINAL]and pp.exists()and live(read(pp));adopt.append(c)
 write(R/'control/ORIGINAL_REQUEST_BEFORE_R20.json',before,True);write(R/'control/OLD_FOUR_REPAIR_REQUESTS_BEFORE_R20.json',oldqs,True)
 entry=N/'bin/native';prior_bytes=entry.read_bytes();assert sha(entry)==qual['prior_entry_sha256'];block=('''# Explicit finite RECOVER12 route; all prior DTC and EP routes remain byte-identical.
if [ "$#" -ge 3 ]; then
 case "$1:$3" in
  experiment:E2-AEREPAIR-RECOVER12-*|result:E2-AEREPAIR-RECOVER12-*)
   exec /usr/bin/python3 -B '''+str(R/'tools/recovery12_frontend_v1.py')+''' "$@"
   ;;
 esac
fi
''').encode();anchor=b'#!/bin/sh\nset -eu\n';assert prior_bytes.startswith(anchor)and block not in prior_bytes;next_bytes=anchor+block+prior_bytes[len(anchor):];assert next_bytes.replace(block,b'',1)==prior_bytes;tmp=entry.with_name('.native.R20writing');tmp.write_bytes(next_bytes);tmp.chmod(entry.stat().st_mode&0o777);assert entry.read_bytes()==prior_bytes,'shared entry changed concurrently; preserve other Lane';tmp.replace(entry);write(R/'control/NATIVE_ENTRY_TRANSITION_R20.json',dict(prior_text=prior_bytes.decode(),prior_sha256=hashlib.sha256(prior_bytes).hexdigest(),new_sha256=sha(entry),added_exact_prefix=block.decode(),other_routes_byte_preserved=True),True)
 def activate(r):
  q=r['registered_future_requests'][ORIGINAL];assert q['orchestrator_sha256']==PRIOR and set(q['consumed'])==set(before['consumed'])and q['budget']==before['budget']and q['remaining']==before['remaining']and q.get('sealed',[])==before.get('sealed',[])
  for c,row in q['consumed'].items():assert {k:v for k,v in row.items()if k!='execution_receipt'}=={k:v for k,v in before['consumed'][c].items()if k!='execution_receipt'}
  assert all(r['registered_future_requests'][k]==v for k,v in oldqs.items())and REQ not in r['registered_future_requests'];q['orchestrator_sha256']=sha(__file__);q.setdefault('operational_continuations',[]).append(dict(revision='R20_FINITE12_STORAGE_RECOVERY_VALIDATION',controller_sha256=sha(__file__),publication_commit=pub['commit'],old_spent_budget_unchanged=True,old_live_generations_adopted=True,new_original_starts=0));r['registered_future_requests'][REQ]=copy.deepcopy(candidate)
 native.update_authority(activate);lease=dict(pid=os.getpid(),start_ticks=int(P('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19]),fd=held.fileno(),request=ORIGINAL,additional_requests=[*OLD,REQ],controller_sha256=sha(__file__),scope='R20 exact original live continuation and separate finite12 corrected-source full validation; old four repair scopes unchanged');write(T/'control/BATCH_LEASE.json',lease);write(R/'control/CONTROLLER_START_R20.json',lease,True);engine.registered();plan=engine.plan();cpus=plan['allowed_model_CPUs'];assert len(set(cpus))==16 and not set(cpus)&{v['host_cpu']for v in claims[ORIGINAL].values()};limits={ORIGINAL:40,REQ:12};roots={ORIGINAL:T,REQ:R};results={ORIGINAL:closed,REQ:{}};running={};blocked={ORIGINAL:set(),REQ:set()};cooldown={};good={'PASS_STRICT_ARCHIVE_NATIVE_RESTORE','FAIL_CLOSED_UNACCEPTED_ARCHIVED_NO_RETRY','PASS_REPAIR_CORRECTNESS_STRICT_ARCHIVE_RESTORE','FAIL_REPAIR_VALIDATION_ARCHIVED_NO_RETRY'}
 def save(k):write(roots[k]/'control/POOL_DISPATCH_RESERVATIONS.json',dict(claims=claims[k]))
 def finish_original(c):return original_finish(c,native,copygate)
 with concurrent.futures.ThreadPoolExecutor(max_workers=64)as pool:
  for c in adopt:
   row=before['consumed'][c];running[pool.submit(safe_call,lambda cell:guard(T,ORIGINAL,cell,native,finish_original),c)]=dict(request=ORIGINAL,cell=c,cpu=claims[ORIGINAL].get(c,{}).get('host_cpu'),adopted=True,active='execution_receipt'not in row)
  for c in closed:claims[ORIGINAL].pop(c,None)
  save(ORIGINAL)
  while True:
   assert not any((root/'control/ABORT').exists()for root in roots.values())
   for future,meta in list(running.items()):
    if not future.done():continue
    result=future.result();k=meta['request'];c=meta['cell'];running.pop(future);row=native.read_current_authority()[0]['registered_future_requests'][k]['consumed'].get(c)
    pidfile=roots[k]/'DTC/run/results'/row['uuid']/'NATIVE_SIMULATOR_PID_AND_MAPS.json'if row is not None else None
    if row is not None and 'execution_receipt'not in row and(not pidfile.exists()or model_live(roots[k],row)):
     assert c in claims[k],'unknown spent generation must retain its serialized CPU claim'
     fn=finish_original if k==ORIGINAL else ops.finish_evidence;running[pool.submit(safe_call,lambda cell,root=roots[k],request=k,final=fn:guard(root,request,cell,native,final),c)]=dict(meta,engineering_guard=True);write(roots[k]/'analysis'/(c+'.R20_ACTIVE_ENGINEERING_GUARD.json'),result);continue
    claims[k].pop(c,None);save(k)
    if result['state']in['ADMISSION_DEFERRED_ZERO_START','REPAIR_ADMISSION_DEFERRED_ZERO_START']:
     assert row is None and not(roots[k]/'control/qualification_ledger'/(c+'.INTENT.json')).exists();cooldown[c]=time.monotonic()+30;write(roots[k]/'analysis/zero_start_deferrals_R20'/(c+'.'+str(time.monotonic_ns())+'.json'),result,True);event('ADMISSION_DEFERRED_ZERO_START',request=k,cohort=c);continue
    results[k][c]=result
    if result['state']not in good:blocked[k].add(c)
    write(roots[k]/'analysis'/(c+'.RESULT.json'),result);event(result['state'],request=k,cohort=c)
   reg,epoch=native.read_current_authority();q=reg['registered_future_requests'][REQ];launched=0;active=sum(x['request']==REQ for x in running.values());used={x['cpu']for x in running.values()if x['cpu']is not None}
   for c in admit_order(q,R,claims[REQ],cooldown,time.monotonic()):
    if c in blocked[REQ]:continue
    if active>=12:break
    slots=[cpu for cpu in cpus if cpu not in used]
    if not slots:break
    s=engine.spec_for(c);sample=accounting.resources(s,True)
    if not ready(sample):continue
    rp=R/'analysis'/(c+'.RESULT.json')
    if rp.exists():assert c not in q['consumed']and not(R/'control/qualification_ledger'/(c+'.INTENT.json')).exists();target=R/'analysis/zero_start_preimages_R20'/rp.name;target.parent.mkdir(exist_ok=True);assert not target.exists();rp.rename(target)
    cpu=slots[0];claims[REQ][c]=dict(host_cpu=cpu,result_cap_bytes=engine.output_cap(s),RAM_cap_bytes=s['limits']['max_process_tree_rss_bytes']);save(REQ);running[pool.submit(safe_call,ops.run_cell,c)]=dict(request=REQ,cell=c,cpu=cpu,adopted=False,active=True);active+=1;used.add(cpu);launched+=1;event('DISPATCH_FRESH_EXACT_RECOVER12_ATTEMPT',request=REQ,cohort=c,CPU=cpu)
   reg,epoch=native.read_current_authority();q=reg['registered_future_requests'][REQ];assert all(reg['registered_future_requests'][k]==v for k,v in oldqs.items()),'closed prior repair history changed';state=dict(state='R20_ORIGINAL_CONTINUATION_AND_FINITE12_FULL_VALIDATION',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),running=list(running.values()),new12_spent=len(q['consumed']),new12_remaining=q['remaining'],new12_results={c:x['state']for c,x in results[REQ].items()},blocked={k:sorted(v)for k,v in blocked.items()},original_consumed=len(reg['registered_future_requests'][ORIGINAL]['consumed']),original_receipt_gaps_preserved=sorted(holes),old_four_repair_requests_unchanged=True,original_full_matrix_complete=False,automatic_model_retries=0);write(R/'analysis/BATCH_STATE_R20.json',state);write(T/'analysis/BATCH_STATE.json',state)
   marker=R/'analysis/VALIDATION_CLOSED_R20.json'
   if len(q['consumed'])==12 and len(results[REQ])==12 and all((R/'control/qualification_ledger'/(c+'.DONE.json')).exists()for c in q['consumed'])and all(r['state']in good for r in results[REQ].values())and not marker.exists():
    status='ALL_FINITE_CORRECTNESS_VALIDATION_PASS'if all(r['state']=='PASS_REPAIR_CORRECTNESS_STRICT_ARCHIVE_RESTORE'for r in results[REQ].values())else'CLOSED_WITH_ARCHIVED_NATIVE_FAILURES';write(marker,dict(status=status,results=results[REQ],accepted_cycles=None,old_scientific_ledgers_preserved=True),True)
    def close(r):
     x=r['registered_future_requests'][REQ];assert x['remaining']==0 and len(x['consumed'])==12;x.update(state='CLOSED',reserved_write_bytes=G,validation_status=status,all_archived_and_native_restored=True)
    engine.update_authority(close)
   pending=set(q['admitted_specs'])-set(q['consumed'])-set(q.get('sealed',[]))
   if not running and not pending:event('R20_ALL_FINITE_SCIENTIFIC_STARTS_CLOSED_ORIGINAL_GAPS_AND_CUTCP_PRESERVED');return
   time.sleep(1 if launched else 10)
if __name__=='__main__':
 try:main()
 except BaseException as e:event('R20_CONTROLLER_ERROR_PRESERVE_ALL_SCIENCE_NO_RETRY',error=repr(e));raise
