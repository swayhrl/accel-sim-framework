"""Finite original-four-cell Cutcp followup after reviewed R5 phase closure."""
import pathlib,json,hashlib,subprocess,importlib.util,os,fcntl,time,datetime,copy,concurrent.futures
P=pathlib.Path;T=P('/root/data/dtc_main_v100_sweep_20261025_v1');N=P('/root/data/ep_l2_dtc_l1_native_v2');REQ='DTC_AE_V100_FULL_SWEEP_20261025_V1';KEY='af7320f9d9dc662971b1856cac87f29f9b8e4b2a65a7f9d4223bb7a74803fef8';CELLS=['E2-AEV100-'+KEY[:16]+'-'+c for c in ['DM','DH','CM','CH']]
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def write(p,x):p=P(p);tmp=p.with_name(p.name+'.writing');tmp.write_text(json.dumps(x,indent=2)+chr(10));os.replace(tmp,p)
def exclusive(p,x):
 p=P(p);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x') as f:json.dump(x,f,indent=2);f.write(chr(10));f.flush();os.fsync(f.fileno())
def module(name,file):s=importlib.util.spec_from_file_location(name,T/'tools'/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def event(x):
 x=dict(x,utc=datetime.datetime.now(datetime.timezone.utc).isoformat());print(json.dumps(x),flush=True)
 with (T/'logs/CONTROLLER_R6_EVENTS.jsonl').open('a') as f:f.write(json.dumps(x)+chr(10))
def generation_gone(row):
 p=P('/proc')/str(row['pid'])
 if p.exists():s=(p/'stat').read_text().rsplit(')',1)[1].split();return int(s[19])!=row['start_ticks'] or s[0]=='Z'
 return True
def boundary_ready(native):
 if not (T/'analysis/BATCH_NATIVE_CLOSED.json').exists():return False
 q=native.read_current_authority()[0]['registered_future_requests'][REQ]
 return q['state']=='ALL_STARTS_CLOSED_PENDING_COMPLETE_SCIENTIFIC_DELIVERY' and q['remaining']==0 and generation_gone(read(T/'control/CONTROLLER_LAUNCH_R5.json'))
def activate(native,lease):
 pub=read(T/'control/CONTINUATION_R6_PUBLICATION_READBACK.json');qual=read(T/'control/CONTINUATION_R6_ZERO_MODEL_QUALIFICATION.json');approval=read(T/'control/CUTCP_FORMAT_ADMISSION_CANDIDATE.json');formatpub=read(T/'control/CUTCP_FORMAT_ADJUDICATION_PUBLICATION_READBACK.json')
 assert pub['verified'] and pub['controller_sha256']==qual['controller_sha256']==sha(__file__) and qual['status']=='PASS' and pub['admission_candidate_sha256']==sha(T/'control/CUTCP_FORMAT_ADMISSION_CANDIDATE.json')
 assert formatpub['verified'] and formatpub['adjudication_sha256']==approval['adjudication_sha256'] and formatpub['producer_sha256']==approval['producer_sha256'] and sha(approval['producer_path'])==approval['producer_sha256']
 for name in ['review','adjudication','qualified_input']:assert sha(approval[name+'_path'])==approval[name+'_sha256']
 assert sha(T/'qualification'/KEY/'QUALIFICATION.json')==approval['original_qualification_sha256']
 assert generation_gone(read(T/'control/CONTROLLER_LAUNCH_R5.json')),'R5 generation still live'
 reg,epoch=native.read_current_authority();before=copy.deepcopy(reg['registered_future_requests'][REQ]);assert before['state']=='ALL_STARTS_CLOSED_PENDING_COMPLETE_SCIENTIFIC_DELIVERY' and before['remaining']==0 and before['budget']==356
 assert set(CELLS)==set(approval['original_never_spent_cells']) and set(CELLS)<=set(before['candidate_cohorts']) and set(CELLS)<=set(before['sealed']) and not set(CELLS)&set(before['consumed'])
 auth=read(T/'control/SCIENCE_AUTHORIZATION.json');assert all(auth['budgets'][c]==1 for c in CELLS) and all(not (T/'control/qualification_ledger'/(c+'.INTENT.json')).exists() for c in CELLS)
 assert KEY in before['input_holds'] and KEY not in before['admitted_inputs'] and all('execution_receipt' in row for row in before['consumed'].values()) and not read(T/'control/POOL_DISPATCH_RESERVATIONS.json')['claims']
 phase=read(T/'analysis/BATCH_NATIVE_CLOSED.json');assert phase['state']=='ALL_APPLICABLE_NATIVE_ATTEMPTS_CLOSED_ARCHIVED_RESTORED_WITH_CLASSIFIED_FAILURES'
 expected_old_cells={c for row in before['admitted_inputs'].values() for c in row['specs']};assert set(before['consumed'])==expected_old_cells and set(before['sealed'])==set(before['candidate_cohorts'])-expected_old_cells and len(expected_old_cells)+len(before['sealed'])==356,'prior phase matrix coverage incomplete'
 assert phase['closed_point_results']==len(before['consumed']) and phase['input_holds']==before['input_holds'],'prior phase closure coverage mismatch'
 body=read(T/'analysis/BODY_QUALIFICATION_PROGRESS.json');assert body['state']=='ALL_FINITE_BODY_QUALIFICATIONS_CLOSED' and body['closed']==body['total_unique']==89
 for c,row in before['consumed'].items():assert read(T/'analysis'/(c+'.RESULT.json'))['state'] in ['PASS_STRICT_ARCHIVE_NATIVE_RESTORE','FAIL_CLOSED_UNACCEPTED_ARCHIVED_NO_RETRY']
 phase_dir=T/'control/phase_closures';phase_dir.mkdir(exist_ok=True);phase_path=phase_dir/'R5_NATIVE_CLOSED_BEFORE_CUTCP.json';row_path=phase_dir/'R5_AUTHORITY_BEFORE_CUTCP.json';exclusive(phase_path,phase);exclusive(row_path,before)
 record={'phase':'R5_BEFORE_EXPLICIT_CUTCP_FORMAT_ADMISSION','native_closed_snapshot_path':str(phase_path),'native_closed_snapshot_sha256':sha(phase_path),'authority_snapshot_path':str(row_path),'authority_snapshot_sha256':sha(row_path),'old_sealed_cells':before['sealed'],'old_input_holds':before['input_holds'],'released_never_spent_cells':CELLS,'released_never_consumed_slots':4,'consumed_rows_unchanged':len(before['consumed']),'reason':'Separate full11membercurrent-source genericGLOBALstore format adjudication;originalHOLDretained,notperformancepromotion','format_publication_commit':formatpub['commit']}
 def amend(current):
  q=current['registered_future_requests'][REQ];assert q==before
  q['sealing_history']=q.get('sealing_history',[])+[record];q['sealed']=[c for c in q['sealed'] if c not in CELLS];q['sealed_unused']=len(q['sealed']);q['remaining']=4;q['state']='RUNNING';q['reserved_write_bytes']=12*1024**3
  q['format_adjudications']=dict(q.get('format_adjudications',{}),**{KEY:dict(approval,status='EXPLICIT_CURRENT_SOURCE_FORMAT_ADMISSION_REGISTERED',publication_commit=formatpub['commit'],publication_receipt_sha256=sha(T/'control/CUTCP_FORMAT_ADJUDICATION_PUBLICATION_READBACK.json'),continuation_commit=pub['commit'])})
  q['input_holds']=dict(q['input_holds']);del q['input_holds'][KEY]
  q['operational_continuations']=q.get('operational_continuations',[])+[{'revision':'R6_CUTCP_FORMAT_FOLLOWUP','controller_sha256':sha(__file__),'publication_commit':pub['commit'],'qualification_sha256':sha(T/'control/CONTINUATION_R6_ZERO_MODEL_QUALIFICATION.json'),'original_canonical_cells':CELLS,'maximum_starts':4,'budget_unchanged':356,'consumed_before':len(before['consumed']),'model_retries':0}];q['orchestrator_sha256']=sha(__file__)
 native.update_authority(amend);after=native.read_current_authority()[0]['registered_future_requests'][REQ]
 allowed={'state','remaining','reserved_write_bytes','sealed','sealed_unused','sealing_history','format_adjudications','input_holds','operational_continuations','orchestrator_sha256'}
 assert all(after[k]==v for k,v in before.items() if k not in allowed) and after['consumed']==before['consumed'] and len(after['consumed'])+after['remaining']+len(after['sealed'])==356
 producer=module('explicit_cutcp_only_spec_producer','sweep_admission_cutcp_reviewed.py');result=producer.admit(KEY,native);assert result['state']=='ADMITTED_FULL_INPUT' and set(result['cells'])==set(CELLS)
 effective=module('unchanged_cap1m_runtime_spec_derivation','sweep_cap1m_specs.py');effective.register_input(result,native)
 exclusive(T/'control/CONTINUATION_R6_ADOPTED.json',{'state':'ONLY_FOUR_ORIGINAL_NEVER_SPENT_CUTCP_CELLS_ADMITTED','prior_phase_consumed':len(before['consumed']),'new_available_slots':4,'same_original_maximum':356,'old_spent_rows_and_HOLD_snapshot_preserved':True,'phase_history':record,'lease':lease})
 return before,record
def main():
 assert not (T/'control/CONTROLLER_START_R6.json').exists(),'one finite continuation generation already activated;inspect/adopt journals,never blind restart'
 native=module('existing_qualified_R5_runtime','sweep_native_cap1m.py');base=module('unchanged_R5_cell_execution','revision5/sweep_controller.py');owner=(T/'control/FINITE_CONTROLLER.lock').open('a+b');global_lock=(N/'control/qualification_ledger/NATIVE_QUALIFICATION.lock').open('rb')
 while True:
  have_owner=False;have_global=False
  try:
   fcntl.flock(owner,fcntl.LOCK_EX|fcntl.LOCK_NB);have_owner=True;fcntl.flock(global_lock,fcntl.LOCK_EX|fcntl.LOCK_NB);have_global=True
   if boundary_ready(native):break
  except BlockingIOError:pass
  if have_global:fcntl.flock(global_lock,fcntl.LOCK_UN)
  if have_owner:fcntl.flock(owner,fcntl.LOCK_UN)
  event({'state':'WAIT_R5_REVIEWED_CLOSED_PHASE_BOUNDARY','new_model_starts':0});time.sleep(30)
 lease={'pid':os.getpid(),'start_ticks':int(P('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19]),'fd':global_lock.fileno(),'request':REQ,'controller_sha256':sha(__file__),'scope':'Four original never-spentCutcpcells only after explicitcurrent-sourceformatreview;oldR5history preserved'}
 before,history=activate(native,lease);write(T/'control/BATCH_LEASE.json',lease);exclusive(T/'control/CONTROLLER_START_R6.json',lease);claims={};write(T/'control/POOL_DISPATCH_RESERVATIONS.json',{'claims':claims});pending=list(CELLS);running={};results={};issues=False;ceiling=min(4,read(T/'control/HOST_CALIBRATION.json')['measured_N_safe_ceiling'])
 with concurrent.futures.ThreadPoolExecutor(max_workers=ceiling) as pool:
  while pending or running:
   for future,cell in list(running.items()):
    if not future.done():continue
    result=future.result();results[cell]=result;claims.pop(cell);write(T/'control/POOL_DISPATCH_RESERVATIONS.json',{'claims':claims});del running[future];write(T/'analysis'/(cell+'.RESULT.json'),result);event({k:v for k,v in result.items() if k not in ['archive','failure_classification']})
    if result['state'] not in ['PASS_STRICT_ARCHIVE_NATIVE_RESTORE','FAIL_CLOSED_UNACCEPTED_ARCHIVED_NO_RETRY']:issues=True
   if not issues:
    for cell in list(pending):
     if len(running)>=ceiling:break
     spec=native.spec_for(cell);resources=native.resources(spec,True)
     if not(resources['physical_RAM_pass'] and resources['physical_disk_pass']):continue
     claims[cell]={'result_cap_bytes':spec['limits']['max_result_directory_bytes'],'RAM_cap_bytes':spec['limits']['max_process_tree_rss_bytes'],'host_cpu':spec['host_cpu']};write(T/'control/POOL_DISPATCH_RESERVATIONS.json',{'claims':claims});running[pool.submit(base.run_cell,cell)]=cell;pending.remove(cell);event({'state':'DISPATCH_ORIGINAL_NEVER_SPENT_CUTCP_CELL','cohort':cell,'CPU':spec['host_cpu']})
   write(T/'analysis/BATCH_STATE_R6.json',{'state':'RESOLVING_UNREVIEWED_ISSUE_NO_RETRY' if issues else 'RUNNING_ORIGINAL_FOUR_CUTCP_CELLS','running':list(running.values()),'pending_original_cells':pending,'closed_results':list(results),'maximum_new_starts':4,'model_retries':0})
   if issues and not running:event({'state':'R6_ISSUE_CHECKPOINT_NO_NEW_STARTS','never_refund_or_retry':True});return
   time.sleep(10)
 q=native.read_current_authority()[0]['registered_future_requests'][REQ];assert set(results)==set(CELLS) and q['remaining']==0 and all(c in q['consumed'] for c in CELLS)
 all_results={c:read(T/'analysis'/(c+'.RESULT.json')) for c in q['consumed']};assert all(r['state'] in ['PASS_STRICT_ARCHIVE_NATIVE_RESTORE','FAIL_CLOSED_UNACCEPTED_ARCHIVED_NO_RETRY'] for r in all_results.values())
 def close(reg):reg['registered_future_requests'][REQ]['state']='ALL_STARTS_CLOSED_PENDING_COMPLETE_SCIENTIFIC_DELIVERY'
 native.update_authority(close)
 aggregate={'state':'ALL_APPLICABLE_NATIVE_ATTEMPTS_CLOSED_ARCHIVED_RESTORED_WITH_CLASSIFIED_FAILURES','input_candidates':89,'admitted_inputs':len(q['admitted_inputs']),'input_holds':q['input_holds'],'running':[],'closed_point_results':len(all_results),'accepted_archived_points':sum(r['state']=='PASS_STRICT_ARCHIVE_NATIVE_RESTORE' for r in all_results.values()),'closed_unaccepted_points':{c:r for c,r in all_results.items() if r['state']=='FAIL_CLOSED_UNACCEPTED_ARCHIVED_NO_RETRY'},'consumed_starts':len(q['consumed']),'remaining_registered_budget':0,'model_budget':356,'model_retries':0,'phase_history':history,'current_source_format_adjudication':read(T/'control/CUTCP_FORMAT_ADMISSION_CANDIDATE.json'),'observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 exclusive(T/'analysis/BATCH_NATIVE_CLOSED_R6.json',aggregate);write(T/'analysis/BATCH_NATIVE_CLOSED.json',aggregate);event({'state':'WHOLE_ORIGINAL_FINITE_MATRIX_PLUS_REVIEWED_CUTCP_CLOSED_FINAL_DELIVERY_REQUIRED','new_cutcp_results':4,'all_consumed':len(q['consumed'])})
if __name__=='__main__':
 try:main()
 except BaseException as e:event({'state':'R6_ERROR_PRESERVE_ALL_HISTORY_NO_RETRY','error':repr(e)});raise
