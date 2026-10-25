"""One finite metadata waiter for the existing final consumer; never starts models."""
import pathlib,json,hashlib,datetime,time,os,fcntl,importlib.util,subprocess,shutil
P=pathlib.Path;T=P('/root/data/dtc_main_v100_sweep_20261025_v1');REQ='DTC_AE_V100_FULL_SWEEP_20261025_V1'
CLOSED='ALL_APPLICABLE_NATIVE_ATTEMPTS_CLOSED_ARCHIVED_RESTORED_WITH_CLASSIFIED_FAILURES'
ACCEPT={'PASS_STRICT_ARCHIVE_NATIVE_RESTORE','FAIL_CLOSED_UNACCEPTED_ARCHIVED_NO_RETRY'}
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def write(p,r,exclusive=False):
 p=P(p)
 if exclusive:
  with p.open('x') as f:json.dump(r,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 else:
  tmp=p.with_name(p.name+'.writing');tmp.write_text(json.dumps(r,indent=2)+'\n');tmp.replace(p)
def generation_present(r):
 try:return int((P('/proc')/str(r['pid'])/'stat').read_text().rsplit(')',1)[1].split()[19])==r['start_ticks']
 except FileNotFoundError:return False
def eligibility(q,closed,r6,body,claims,controllers_present,complete_exists):
 assert not complete_exists,'Existing COMPLETE_RESULT must be reviewed;never overwrite or auto-replay'
 if q['state']!='ALL_STARTS_CLOSED_PENDING_COMPLETE_SCIENTIFIC_DELIVERY' or q['remaining']!=0:return 'WAIT_NATIVE_MATRIX'
 if not closed or not r6:return 'WAIT_EXPLICIT_R6_AGGREGATE'
 if controllers_present:return 'WAIT_ALL_CONTROLLER_GENERATIONS_GONE'
 assert closed==r6 and closed['state']==CLOSED and not closed['running']
 assert q['budget']==356 and len(q['consumed'])==288 and len(q['admitted_inputs'])==72
 assert len(q['sealed'])==68 and not set(q['sealed'])&set(q['consumed']) and len(q['input_holds'])==17
 assert closed['closed_point_results']==288 and closed['admitted_inputs']==72 and len(closed['input_holds'])==17
 assert body['state']=='ALL_FINITE_BODY_QUALIFICATIONS_CLOSED' and body['closed']==body['total_unique']==89
 assert not claims and all('execution_receipt' in r for r in q['consumed'].values())
 assert all(set(r['specs'])<=set(q['consumed']) and len(r['specs'])==4 for r in q['admitted_inputs'].values())
 return 'READY_FULL_MATRIX_NO_MODELS'
def verify_pins(pins):
 for row in pins:assert sha(row['path'])==row['sha256'],('pinned source changed',row['path'])
def state(value,**fields):
 r=dict(state=value,observed_utc=utc(),actual_pid=os.getpid(),scientific_model_starts=0,scientific_authority_writes=0,**fields);write(T/'control/FINAL_CONSUMER_WAITER_STATE_V6.json',r);return r
def final_disk_floor(native):
 r=native.resources({'cohort':'FINAL_CONSUMER_METADATA_ONLY'},False)
 assert r['local_safety_floor_bytes']==5*1024**3
 return r['required_free_bytes']+256*1024**2,r
def main():
 lock=(T/'control/FINAL_CONSUMER_WAITER_V1.lock').open('a+b');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 config=read(T/'control/FINAL_CONSUMER_WAITER_CONFIG_V6.json');verify_pins(config['source_pins']);assert config['request']==REQ and config['waiter_sha256']==sha(__file__)
 qp=T/'control/FINAL_CONSUMER_WAITER_QUALIFICATION_V6.json';qual=read(qp)
 assert config['qualification_sha256']==sha(qp) and qual['status']=='PASS' and qual['waiter_sha256']==sha(__file__) and qual['source_pins']==config['source_pins'],'Qualification binding changed'
 assert not (T/'control/FINAL_CONSUMER_START_V1.json').exists(),'Prior consumer launch is one-shot;inspect its actual process/receipts'
 spec=importlib.util.spec_from_file_location('final_waiter_existing_native',T/'tools/sweep_native_cap1m.py');native=importlib.util.module_from_spec(spec);spec.loader.exec_module(native)
 began=time.monotonic();last_pin_check=0
 while True:
  assert not (T/'control/ABORT').exists(),'ABORT requested;no consumer launched'
  assert time.monotonic()-began<90*86400,'Finite metadata wait expired;review required'
  if time.monotonic()-last_pin_check>900:verify_pins(config['source_pins']);last_pin_check=time.monotonic()
  q=native.read_current_authority()[0]['registered_future_requests'][REQ]
  cp=T/'analysis/BATCH_NATIVE_CLOSED.json';rp=T/'analysis/BATCH_NATIVE_CLOSED_R6.json'
  closed=read(cp) if cp.exists() else None;r6=read(rp) if rp.exists() else None
  live=[read(p) for p in (T/'control').glob('CONTROLLER_LAUNCH_R*.json') if generation_present(read(p))]
  ready=eligibility(q,closed,r6,read(T/'analysis/BODY_QUALIFICATION_PROGRESS.json'),read(T/'control/POOL_DISPATCH_RESERVATIONS.json')['claims'],live,(T/'analysis/COMPLETE_RESULT.json').exists())
  if ready=='READY_FULL_MATRIX_NO_MODELS':break
  state(ready,consumed=len(q['consumed']),remaining_registered=q['remaining'],actual_controller_pids=[r['pid'] for r in live]);time.sleep(60)
 verify_pins(config['source_pins'])
 for c in q['consumed']:assert read(T/'analysis'/(c+'.RESULT.json'))['state'] in ACCEPT
 floor,disk_admission=final_disk_floor(native)
 assert disk_admission['physical_disk_pass'],'Fresh known final-consumer writes require disk review'
 assert shutil.disk_usage(T).free>floor,'Final consumer disk margin requires review'
 consumer=T/'tools/sweep_final_consumer_v9.py'
 # No prior final consumer may be active, including an independently launched one.
 for proc in P('/proc').iterdir():
  if not proc.name.isdigit():continue
  try:cmd=(proc/'cmdline').read_bytes().split(b'\0')
  except (FileNotFoundError,PermissionError,ProcessLookupError):continue
  assert os.fsencode(consumer) not in cmd,('Existing final consumer generation',proc.name)
 start={'state':'ONE_SHOT_FINAL_CONSUMER_START_INTENT','request':REQ,'waiter_sha256':sha(__file__),'consumer_sha256':sha(consumer),'consumer_path':str(consumer),'final_consumer_disk_admission':disk_admission,'source_pins':config['source_pins'],'native_closed_sha256':sha(cp),'r6_aggregate_sha256':sha(rp),'observed_utc':utc(),'models_started':0,'automatic_consumer_retries':0}
 write(T/'control/FINAL_CONSUMER_START_V1.json',start,True)
 logpath=T/'logs/FINAL_CONSUMER_V9_BACKGROUND.log'
 with logpath.open('xb') as log:
  child=subprocess.Popen(['/usr/bin/python3','-B','-u',str(consumer)],stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True,cwd=T,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'))
  ticks=int((P('/proc')/str(child.pid)/'stat').read_text().rsplit(')',1)[1].split()[19])
  launch=dict(start,state='FINAL_CONSUMER_CHILD_ACTUALLY_STARTED',pid=child.pid,start_ticks=ticks,log=str(logpath))
  write(T/'control/FINAL_CONSUMER_LAUNCH_V1.json',launch,True);state('FINAL_CONSUMER_RUNNING',child_pid=child.pid,child_start_ticks=ticks)
  code=child.wait()
 result=T/'analysis/COMPLETE_RESULT.json'
 if code==0:
  r=read(result);assert r['status']=='ALL_APPLICABLE_ATTEMPTS_AND_HOLDS_ARCHIVE_NATIVE_RESTORE_REPLAYED' and r['new_native_attempts']==288 and r['applicable_four_attempt_inputs']==72 and r['preserved_input_holds']==17
  assert r['each_unique_applicable_input_current_full_SHA_rechecked_once']==72 and r['model_automatic_retries']==0
  state('FINAL_CONSUMER_FINISHED_REVIEW_PUBLICATION_AND_AUTHORITY_STILL_REQUIRED',child_pid=child.pid,returncode=code,result_sha256=sha(result),goal_complete=False)
 else:state('FINAL_CONSUMER_FAILED_NO_AUTOMATIC_RETRY_REVIEW_REQUIRED',child_pid=child.pid,returncode=code,partial_sessions_preserved=True,goal_complete=False)
if __name__=='__main__':
 try:main()
 except BaseException as e:state('FINAL_CONSUMER_WAITER_CHECKPOINT_NO_RETRY',error=repr(e),goal_complete=False);raise
