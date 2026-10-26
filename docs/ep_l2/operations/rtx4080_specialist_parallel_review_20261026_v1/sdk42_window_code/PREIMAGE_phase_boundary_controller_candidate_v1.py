#!/usr/bin/env python3
"""Private phase-boundary candidate. Import is inert; execution requires Root approval bytes."""
import argparse,ast,contextlib,fcntl,hashlib,json,os,pathlib,secrets,shlex,subprocess,time,traceback
D=pathlib.Path(__file__).resolve().parent
C=pathlib.Path('/root/data/shared_rtx4080_trace_library_20261024_v1/control')
B=pathlib.Path('/root/share/mnt164/huangrulin/traces/rtx4080_sm89/bulk_20261024_v1')
OLD_RUN=pathlib.Path('/root/share/mnt164/huangrulin/traces/receipts/rtx4080_pending_resume_20261025_v1/code/ab47640139120439c97282e130a133a924e72256478d0611360c95ea748d5f8e/run_1792921868613986155')
BEFORE_SHA='6813a27cde9afe0c4bd2f157309a62bc1905668b8252dfafdac503b336700daa'
AFTER_SHA='8c0af4fa9cf7a6f2a742a2c003f658bc89750437dc96cfcb6f7c087c75da8259'
WATCHDOG_SHA='06be838b97c255bbb299a9fb641556455e8f34267c73c1da94d60a2db0ddfde5'
WORKER_SHA='a546e0cfdf47e463bed63740289f44737f503b7cd6b822510c5845a6ec80b183'
SCHEDULER_SHA='9308c508d85c84db7e9b8d49e465ffaffc426fef638a92d05eec4c6dc7cae423'
OWN_STOP_SHA='117eccfb381e181188e5f6c47236be3ee49e0e0bbaad1803eeb60f6cc53079d5'
WORKER_REMOTE='/data/c16/rtx4080_suite_fill_20261024_v1/nas_rtx4080/private_candidates/cpu_post_parallel_20261026_v1/capture_ordinary_parallel2_nas_candidate_v2.py'
SCHED_REMOTE='/data/c16/rtx4080_suite_fill_20261024_v1/nas_rtx4080/private_candidates/cpu_post_parallel_20261026_v1/post_app_parallel_109_candidate_v1.py'
def digest(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def canon(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def load(p):return json.loads(pathlib.Path(p).read_text())
def durable(p,x,exclusive=False):
 p=pathlib.Path(p);raw=(json.dumps(x,indent=2)+'\n').encode()
 if exclusive:
  with p.open('xb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
 else:
  tmp=p.with_name(p.name+'.tmp')
  with tmp.open('wb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
  os.replace(tmp,p)
 # Directory fsync is best-effort only on SSHFS; durable-file readback is mandatory.
 assert p.read_bytes()==raw
 return hashlib.sha256(raw).hexdigest()
def identity(pid):
 try:
  x=pathlib.Path('/proc',str(pid),'stat').read_text().split(') ',1)[1].split()
  return {'pid':int(pid),'start_ticks':x[19],'state':x[0]}
 except (FileNotFoundError,ProcessLookupError):return None
def same_alive(expected):
 x=identity(expected['pid'])
 return bool(x and x['start_ticks']==expected['start_ticks'] and x['state']!='Z')
def validate_queue(queue,before,require_boundary_commit):
 ids=[x['id'] for x in queue];baseline=before['queue_baseline']
 assert ids==[x['id'] for x in baseline],'queue ID/order delta'
 assert len(ids)==len(set(ids)),'duplicate queue IDs'
 selected={x['queue_entry']['id']:x for x in before['jobs']};assert len(selected)==36
 assert {x['id'] for x in queue if x['status']=='PENDING'}==set(selected),'exact36 PENDING boundary changed'
 boundary=before['boundary_job']['id'];current=None
 for live,frozen in zip(queue,baseline):
  if live['id']==boundary:
   fixed={k:v for k,v in live.items() if k not in {'status','commit','end_unix'}}
   assert canon(fixed)==before['boundary_fixed_sha256'],'current job identity changed'
   assert live['status'] in ('RUNNING','COMMITTED_VERIFIED'),'boundary failure/hold'
   if require_boundary_commit:assert live['status']=='COMMITTED_VERIFIED','publication not closed'
   current=live
  else:assert canon(live)==frozen['canonical_sha256'],'queue row delta '+live['id']
 assert current is not None
 for id,x in selected.items():
  assert next(j for j in queue if j['id']==id)==x['queue_entry'],'selected queue identity changed'
 return current
def plan_queue(queue,before,after):
 validate_queue(queue,before,True)
 frozen={x['id']:x for x in after['jobs']};assert len(frozen)==36
 original={x['queue_entry']['id']:x for x in before['jobs']};assert set(frozen)==set(original)
 out=[]
 for item in queue:
  row=dict(item)
  if row['id'] in frozen:
   new=frozen[row['id']]
   assert new['job_path']==row['job_path'] and new['type']==row['type']=='CAPTURE_ORDINARY'
   assert new['job_sha256']==original[row['id']]['job_sha256']
   check={k:v for k,v in new.items() if k not in {'worker_script','worker_sha256','job_sha256'}}
   old={k:v for k,v in row.items() if k not in {'worker_script','worker_sha256'}}
   assert check==old,'nonworker field change'
   assert new['worker_script']==WORKER_REMOTE and new['worker_sha256']==WORKER_SHA
   row.update(worker_script=new['worker_script'],worker_sha256=new['worker_sha256'])
  out.append(row)
 assert sum(a!=b for a,b in zip(out,queue))==36
 return out
def publication_closed(boundary,base=B):
 id=boundary['id'];commit=boundary.get('commit');assert commit and commit['asset_id']==id
 receipt=load(base/'receipts'/(id+'_RECEIVER_READBACK.json'));assert receipt==commit
 obj=base/'objects'/id
 assert commit['status']=='COMMITTED_VERIFIED' and commit['object_path']==str(obj)
 assert digest(obj/'MANIFEST.json')==commit['manifest_sha256'],'manifest not receiver identity'
 on_disk=load(obj/'COMMIT.json')
 assert all(on_disk.get(k)==v for k,v in commit.items() if k!='object_path')
 entries=[x for x in load(base/'catalog/ASSETS.json')['objects'] if x['asset_id']==id]
 assert entries==[commit],'catalog receipt not closed'
 return {'asset_id':id,'manifest_sha256':commit['manifest_sha256'],'receiver_readback_sha256':digest(base/'receipts'/(id+'_RECEIVER_READBACK.json'))}
def stop_matches(path,expected_bytes):
 path=pathlib.Path(path)
 assert not path.is_symlink() and path.is_file(),'STOP absent or foreign type'
 assert path.read_bytes()==expected_bytes,'STOP replaced/modified by another owner'
 return path.stat()
def retire_stop(path,retired,expected_bytes):
 path=pathlib.Path(path);retired=pathlib.Path(retired)
 st=stop_matches(path,expected_bytes);assert not retired.exists(),'own retired STOP path already exists'
 assert path.stat().st_ino==st.st_ino and path.stat().st_dev==st.st_dev
 path.rename(retired)
 assert retired.read_bytes()==expected_bytes and retired.stat().st_ino==st.st_ino,'STOP retirement race; preserve evidence'
 return str(retired)
@contextlib.contextmanager
def leases():
 handles=[]
 try:
  for name in ['RTX4080_DISPATCHER.lock','RTX4080_SOURCE.lock','RTX4080_TARGET.lock','RTX4080_QUEUE.lock']:
   f=(C/name).open('r+')
   try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
   except BaseException:f.close();raise
   handles.append(f)
  yield
 finally:
  for f in reversed(handles):fcntl.flock(f,fcntl.LOCK_UN);f.close()
def verify_remote(before):
 expected={WORKER_REMOTE:WORKER_SHA,SCHED_REMOTE:SCHEDULER_SHA}
 expected.update({x['queue_entry']['job_path']:x['job_sha256'] for x in before['jobs']})
 code=("import pathlib,hashlib,json,fcntl;expected="+repr(expected)+";hs=[];\ntry:\n"
       " for n in ['/data/c16/rtx4080_suite_fill_20261024_v1/control/RTX4080_LOCAL_IO.lock','/data/c16/locks/c16_gpu_campaign.lock']:\n"
       "  f=open(n,'r+');fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);hs.append(f)\n"
       " for p,h in expected.items():\n"
       "  assert hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()==h,p\n"
       " print(json.dumps({'status':'REMOTE_FILES_EXACT_AND_LOCAL_LEASES_IDLE','files':len(expected)}))\n"
       "finally:\n"
       " for f in reversed(hs):fcntl.flock(f,fcntl.LOCK_UN);f.close()")
 result=subprocess.run(['ssh','-n','-o','BatchMode=yes','-o','ConnectTimeout=12','gpu109','python3 -B -c '+shlex.quote(code)],capture_output=True,text=True,timeout=40)
 assert result.returncode==0,('remote file/lease preflight failed; no switch',result.stderr[-2000:])
 x=json.loads(result.stdout);assert x['status']=='REMOTE_FILES_EXACT_AND_LOCAL_LEASES_IDLE';return x
def function_text(source,name):
 return ast.get_source_segment(source,next(x for x in ast.parse(source).body if isinstance(x,(ast.FunctionDef,ast.AsyncFunctionDef)) and x.name==name))
def verify_sources():
 old=(D/'dispatch_finite_original.py').read_text();new=(D/'dispatch_finite_cpu2_36_candidate.py').read_text()
 for name in ['save','sha','publish','update_job','run_remote']:
  assert function_text(old,name)==function_text(new,name),'function source changed '+name
  assert ast.dump(ast.parse(function_text(old,name)))==ast.dump(ast.parse(function_text(new,name)))
 assert digest(D/'remote_watchdog_candidate.py')==WATCHDOG_SHA
 assert digest(D/'capture_ordinary_parallel2_nas_candidate_v2.py')==WORKER_SHA
 assert digest(D/'post_app_parallel_109_candidate_v1.py')==SCHEDULER_SHA
def approval_gate(path,expected_sha):
 assert digest(path)==expected_sha,'approval bytes changed'
 a=load(path);assert a['approved'] is True and a['action']=='EXACT36_CPU2_PHASE_BOUNDARY_ONCE'
 expected={'controller_sha256':digest(__file__),'before_sha256':BEFORE_SHA,'after_sha256':AFTER_SHA,'dispatcher_sha256':digest(D/'dispatch_finite_cpu2_36_candidate.py'),'watchdog_sha256':WATCHDOG_SHA,'worker_sha256':WORKER_SHA,'scheduler_sha256':SCHEDULER_SHA,'own_stop_sha256':OWN_STOP_SHA}
 assert all(a.get(k)==v for k,v in expected.items()),'Root approval scope/hash mismatch'
 assert a.get('bandwidth_limit_enforced') is False and a.get('gpu_concurrency')==1 and a.get('post_concurrency')==2
 return a
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--execute',action='store_true',required=True);ap.add_argument('--approval',required=True);ap.add_argument('--approval-sha',required=True);a=ap.parse_args()
 verify_sources();approval_gate(pathlib.Path(a.approval),a.approval_sha)
 assert digest(D/'FROZEN_PENDING_36_BEFORE.json')==BEFORE_SHA
 assert digest(D/'FROZEN_PENDING_36_AFTER.json')==AFTER_SHA
 before=load(D/'FROZEN_PENDING_36_BEFORE.json');after=load(D/'FROZEN_PENDING_36_AFTER.json')
 run=D/'phase_run';run.mkdir(exist_ok=False)
 me=identity(os.getpid());deadline=time.time()+72*3600
 ident=dict(me,start_unix=time.time(),deadline_unix=deadline,approval_sha256=a.approval_sha)
 durable(run/'IDENTITY.json',ident,True)
 def state(status,**kw):durable(run/'STATE.json',dict(ident,status=status,unix=time.time(),**kw))
 stop=C/'STOP_AFTER_CURRENT';own=(D/'OWN_STOP_AFTER_CURRENT.json').read_bytes()
 assert hashlib.sha256(own).hexdigest()==OWN_STOP_SHA,'owned STOP payload changed'
 assert load(D/'OWN_STOP_AFTER_CURRENT.json')['snapshot_before_sha256']==BEFORE_SHA
 old=before['old_dispatcher'];old_run_id=load(OLD_RUN/'IDENTITY.json')
 assert all(old_run_id[k]==old[k] for k in ['pid','start_ticks'])
 validate_queue(load(C/'QUEUE.json'),before,False)
 # Writes only this controller's exact STOP and never overwrites a preexisting foreign file.
 if stop.exists():stop_matches(stop,own)
 else:
  with stop.open('xb') as f:f.write(own);f.flush();os.fsync(f.fileno())
  stop_matches(stop,own)
 durable(run/'OWN_STOP_CREATED.json',{'path':str(stop),'sha256':hashlib.sha256(own).hexdigest(),'old_dispatcher':old},True)
 state('WAIT_BOUNDARY_NO_RUNNING_JOB_CHANGE')
 try:
  while time.time()<deadline-120:
   stop_matches(stop,own)
   queue=load(C/'QUEUE.json');boundary=validate_queue(queue,before,False)
   if same_alive(old) or boundary['status']!='COMMITTED_VERIFIED':
    state('WAIT_CURRENT_OR_OLD_DISPATCHER',boundary_status=boundary['status']);time.sleep(10);continue
   old_state=load(OLD_RUN/'STATE.json')
   assert all(old_state[k]==old[k] for k in ['pid','start_ticks']) and old_state['status']=='STOP_AFTER_CURRENT','old dispatcher did not naturally STOP'
   closed=publication_closed(boundary)
   try:
    with leases():
     stop_matches(stop,own);assert not same_alive(old),'old identity unexpectedly active'
     queue=load(C/'QUEUE.json');boundary=validate_queue(queue,before,True)
     closed=publication_closed(boundary);remote=verify_remote(before)
     new_queue=plan_queue(queue,before,after)
     assert not (D/'NEW_BATCH_STARTED.json').exists() and not (D/'BATCH_LAUNCH_GATE.json').exists()
     intent=run/'LAUNCH_INTENT.json';assert not intent.exists(),'launch intent already exists; manual reconciliation required'
     durable(run/'QUEUE_BEFORE.json',queue,True)
     durable(run/'QUEUE_AFTER_PLANNED.json',new_queue,True)
     durable(C/'QUEUE.json',new_queue)
     assert load(C/'QUEUE.json')==new_queue
     retired=retire_stop(stop,C/'STOP_AFTER_CURRENT.RETIRED_CPU2_EXACT36_20261026_V1',own)
     durable(run/'SWITCH_CLOSED.json',{'publication':closed,'remote':remote,'retired_own_stop':retired,'changed_queue_rows':36,'old_dispatcher':old,'source_KEEP':True,'bandwidth_limit_enforced':False},True)
     token=secrets.token_hex(24)
     durable(intent,{'token':token,'dispatcher_sha256':digest(D/'dispatch_finite_cpu2_36_candidate.py'),'selected_count':36,'one_shot':True},True)
     env=os.environ.copy();env['RTX_CPU2_GATE_TOKEN']=token;env['PYTHONDONTWRITEBYTECODE']='1'
     with (run/'dispatcher.stdout.log').open('xb') as out,(run/'dispatcher.stderr.log').open('xb') as err:
      child=subprocess.Popen(['/usr/bin/python3','-B',str(D/'dispatch_finite_cpu2_36_candidate.py'),'--frozen36'],stdin=subprocess.DEVNULL,stdout=out,stderr=err,env=env,start_new_session=True)
     ci=identity(child.pid);assert ci and ci['state']!='Z'
     durable(run/'LAUNCHED_WAITING_GATE.json',dict(ci,token=token),True)
    # All controller leases have now been released; the child must acquire its own lease.
    durable(D/'BATCH_LAUNCH_GATE.json',{'token':token,'pid':ci['pid'],'start_ticks':ci['start_ticks']},True)
    until=time.monotonic()+60
    while time.monotonic()<until:
     if (D/'NEW_BATCH_STARTED.json').exists():
      ack=load(D/'NEW_BATCH_STARTED.json')
      assert ack['pid']==ci['pid'] and ack['start_ticks']==ci['start_ticks'] and ack['launch_token']==token
      state('EXACT36_BATCH_STARTED_CONTROLLER_COMPLETE',new_batch=ack);return
     assert same_alive(ci),'new dispatcher exited before durable startup acknowledgement'
     time.sleep(.2)
    raise TimeoutError('new batch startup acknowledgement missing; no relaunch')
   except BlockingIOError:
    state('WAIT_NATIVE_RTX_LEASES');time.sleep(10);continue
  raise TimeoutError('72h phase-boundary deadline; own STOP and all diagnostics retained')
 except BaseException as error:
  state('FAILED_RETAINED_NO_RELAUNCH',error=repr(error),traceback=traceback.format_exc());raise
if __name__=='__main__':main()
