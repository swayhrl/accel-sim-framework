"""One finite metadata correction, after DM exit, with the existing CPU launcher held.

No model launch, no retry/refund and no Core/Framework/binary change. Only the
two never-started PAPER_BASE specs are corrected to the supported mode contract.
"""
import pathlib,json,hashlib,os,signal,fcntl,time,importlib.util,datetime,copy,sys
T=pathlib.Path('/root/data/dtc_main_20261023_v1/ae_fair_v1');N=pathlib.Path('/root/data/ep_l2_dtc_l1_native_v2');D=T/'prepared_revision2';REQ='DTC_AEFAIR_EPOCH2_V1'
def read(p):return json.loads(pathlib.Path(p).read_text())
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def atomic(p,x):
 p=pathlib.Path(p);tmp=p.with_name(p.name+'.revision2.writing');raw=(json.dumps(x,sort_keys=True,indent=2)+'\n').encode() if not isinstance(x,bytes) else x
 with tmp.open('wb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
 os.replace(tmp,p);fd=os.open(p.parent,os.O_RDONLY);os.fsync(fd);os.close(fd)
def load_native():
 s=importlib.util.spec_from_file_location('existing_exact_native_for_revision',T/'tools/aefair_native.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def launcher(resume=False):
 q=read(T/'control/UNUSED_CPLUS_CORRECTION_HOLD.json');p=pathlib.Path('/proc')/str(q['controller_pid']);a=(p/'stat').read_text().rsplit(')',1)[1].split()
 assert int(a[19])==q['controller_start_ticks'],'launcher generation changed'
 assert str(T/'tools/aefair_controller.py').encode() in (p/'cmdline').read_bytes().split(b'\0'),'launcher argv changed'
 if resume:
  fd=os.pidfd_open(q['controller_pid']);assert int((p/'stat').read_text().rsplit(')',1)[1].split()[19])==q['controller_start_ticks'];signal.pidfd_send_signal(fd,signal.SIGCONT);os.close(fd)
 else:assert a[0]=='T','launcher must remain held during unused-spec transaction'
 return q
def revise_row(reg,candidate):
 row=reg['registered_future_requests'][REQ];assert set(row['consumed'])=={'E2-AEFAIR-DM'} and row['remaining']==3 and row['budget']==4
 assert row['spec_request_sha256']==candidate['old_request_sha256'],'request already changed'
 before=copy.deepcopy(row['consumed']);row['spec_request_sha256']=candidate['new_request_sha256'];row['spec_revision']=2
 row['unused_spec_amendment']={'operation':'AMEND_NEVER_STARTED_CPLUS_FINITE_FLAG','old_request_sha256':candidate['old_request_sha256'],'new_request_sha256':candidate['new_request_sha256'],'old_execution_authorization_sha256':candidate['old_authorization_sha256'],'new_execution_authorization_sha256':candidate['new_authorization_sha256'],'changed_cells':['E2-AEFAIR-CM','E2-AEFAIR-CH'],'consumed_unchanged':True,'budget_or_refund_change':False,'reason':'PAPER_BASE must use its existing standard-cache timing; DTC-only finiteV1 flag is unsupported and set0 only in the two unstarted conventional cells.'}
 assert row['consumed']==before
def apply():
 marker=T/'control/UNUSED_CPLUS_AMENDMENT_APPLIED.json'
 if marker.exists():return read(marker)
 proof=read(D/'PUBLICATION_READBACK.json');assert proof['verified'],'revision source/specs not published and read back'
 assert proof['helper_sha256']==sha(__file__),'published amendment helper changed'
 for file,digest in proof['private_file_pins'].items():assert sha(file)==digest,'published candidate/qualification changed:'+file
 assert read(D/'CPU_QUALIFICATION.json')['status']=='PASS_UNUSED_BASELINE_MODE_CPU_QUALIFICATION_ONLY'
 launcher();donefile=T/'control/qualification_ledger/E2-AEFAIR-DM.DONE.json';assert donefile.exists(),'DM not terminal'
 done=read(donefile);assert done['launcher_wait_returncode']==0 and done['stop_reason'] is None and done['native_simulator_observed'],'DM not a successful natural native exit'
 intent=read(T/'control/qualification_ledger/E2-AEFAIR-DM.INTENT.json');out=pathlib.Path(intent['output']);assert read(out/'NATIVE_EXIT.json')==done
 meta=read(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json');p=pathlib.Path('/proc')/str(meta['pid'])
 if p.exists():assert int((p/'stat').read_text().rsplit(')',1)[1].split()[19])!=meta['start_ticks'],'DM process still live'
 last=[json.loads(l) for l in (out/'progress.jsonl').read_text().splitlines()][-1];assert last['end']=='NATURAL' and last['completed']==739246080
 held=(N/'control/qualification_ledger/NATIVE_QUALIFICATION.lock').open('rb');fcntl.flock(held,fcntl.LOCK_EX|fcntl.LOCK_NB)
 regpath=N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json';reg=read(regpath);row=reg['registered_future_requests'][REQ]
 assert 'execution_receipt' in row['consumed']['E2-AEFAIR-DM'],'native guard final registry join pending'
 assert set(row['consumed'])=={'E2-AEFAIR-DM'} and row['remaining']==3 and row['state']=='RUNNING'
 for cell in ['DH','CM','CH']:assert not (T/'control/qualification_ledger'/('E2-AEFAIR-'+cell+'.INTENT.json')).exists(),'unused cell already started'
 c=read(D/'AMENDMENT_CANDIDATE.json');assert sha(T/'control/E2-AEFAIR-DM_SPEC.json')==c['active_DM_spec_sha256']
 for name,key in [('SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json','old_request_sha256'),('SCIENCE_AUTHORIZATION.json','old_authorization_sha256')]:assert sha(T/'control'/name)==c[key]
 history=T/'control/freeze_history/revision1';history.mkdir(parents=True,exist_ok=True);saved={}
 targets=['SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json','SCIENCE_AUTHORIZATION.json','E2-AEFAIR-CM_SPEC.json','E2-AEFAIR-CH_SPEC.json']
 for name in targets:
  src=T/'control'/name;h=sha(src);dst=history/(src.stem+'.'+h+'.json')
  if not dst.exists():
   with dst.open('xb') as f:f.write(src.read_bytes());f.flush();os.fsync(f.fileno())
  saved[name]={'path':str(dst),'sha256':h}
 before=copy.deepcopy(reg);oldregsha=sha(regpath);old_dm_auth=read(T/'control/qualification_ledger/E2-AEFAIR-DM.INTENT.json')['authorization_sha256'];assert old_dm_auth==c['old_authorization_sha256']
 for name in ['E2-AEFAIR-CM_SPEC.json','E2-AEFAIR-CH_SPEC.json','SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json','SCIENCE_AUTHORIZATION.json']:
  atomic(T/'control'/name,(D/name).read_bytes())
 m=load_native();m.update_authority(lambda r:revise_row(r,c));after=read(regpath)
 assert after['old_source_history']==before['old_source_history'] and after['qualification_history']==before['qualification_history']
 assert after['registered_future_requests'][REQ]['consumed']==before['registered_future_requests'][REQ]['consumed']
 assert after['registered_future_requests'][REQ]['remaining']==3 and after['new_scientific_budget_remaining']==before['new_scientific_budget_remaining']
 for k,v in before['registered_future_requests'].items():
  if k!=REQ:assert after['registered_future_requests'][k]==v,'foreign request changed'
 receipt={'status':'UNSTARTED_CPLUS_SPEC_REVISION2_APPLIED_AFTER_DM_NATIVE_EXIT','operation':'AMEND_NEVER_STARTED_CPLUS_FINITE_FLAG','request_id':REQ,'source_release':proof,'active_DM_spec_unchanged':True,'DM_attempt_uuid':intent['uuid'],'DM_native_exit_sha256':sha(out/'NATIVE_EXIT.json'),'DM_performance_acceptance':'Pending original strict consumer; not granted by this amendment','old_DM_authorization_preimage':saved['SCIENCE_AUTHORIZATION.json'],'changed_cells':['E2-AEFAIR-CM','E2-AEFAIR-CH'],'old_files_preserved':saved,'request_sha256':sha(T/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json'),'execution_authorization_sha256':sha(T/'control/SCIENCE_AUTHORIZATION.json'),'native_registry_sha256_before':oldregsha,'native_registry_sha256_after':sha(regpath),'starts_consumed_before':1,'starts_consumed_after':1,'remaining_before':3,'remaining_after':3,'extra_model_starts':0,'refunds':0,'Core_Framework_binary_changes':0,'utc':now()}
 atomic(marker,receipt);launcher(resume=True);return receipt
def main(wait=False):
 own=(D/'FINITE_AMENDMENT_WORKER.lock').open('a+b');fcntl.flock(own,fcntl.LOCK_EX|fcntl.LOCK_NB);start=time.monotonic();last=0
 while True:
  done=T/'control/qualification_ledger/E2-AEFAIR-DM.DONE.json'
  if done.exists():
   d=read(done)
   if d['launcher_wait_returncode']!=0 or d['stop_reason'] is not None:
    atomic(D/'AMENDMENT_WORKER_STATE.json',{'state':'NO_AMENDMENT_DM_FAILED_RESUME_FAILURE_CLOSEOUT','utc':now()});launcher(resume=True);return
   current=read(N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json')['registered_future_requests'][REQ]
   if 'execution_receipt' not in current['consumed']['E2-AEFAIR-DM']:
    time.sleep(.2);continue
   try:
    r=apply();atomic(D/'AMENDMENT_WORKER_STATE.json',r);print(json.dumps(r,indent=2),flush=True);return
   except BlockingIOError:pass
  if not wait:return {'state':'PREPARED_WAITING_DM_NATIVE_TERMINAL','apply_performed':False}
  if time.monotonic()-start>21660:raise RuntimeError('finite amendment wait bound; keep launcher held for review')
  if time.monotonic()-last>=300:
   x={'state':'WAIT_CURRENT_DM_NATIVE_TERMINAL_LAUNCHER_HELD','current_model_not_signaled':True,'new_model_starts':0,'elapsed_seconds':time.monotonic()-start,'utc':now()};atomic(D/'AMENDMENT_WORKER_STATE.json',x);print(json.dumps(x),flush=True);last=time.monotonic()
  time.sleep(5)
if __name__=='__main__':
 try:print(json.dumps(main('--wait' in sys.argv),indent=2))
 except BaseException as e:atomic(D/'AMENDMENT_WORKER_STATE.json',{'state':'HOLD_AMENDMENT_ERROR_LAUNCHER_REMAINS_HELD','error':repr(e),'utc':now()});raise
