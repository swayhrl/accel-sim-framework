"""One finite four-cell Goal worker; never restarts a consumed cell."""
import pathlib,json,subprocess,time,sys,os,fcntl,importlib.util,datetime,hashlib
T=pathlib.Path('/root/data/dtc_main_short3_20261024_v1');N=pathlib.Path('/root/data/ep_l2_dtc_l1_native_v2')
def read(p):return json.loads(pathlib.Path(p).read_text())
def module(name,file):
 s=importlib.util.spec_from_file_location(name,T/'tools'/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def state(x):
 x['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();p=T/'control/CONTROLLER_STATE.json';tmp=p.with_suffix('.writing');tmp.write_text(json.dumps(x,indent=2)+'\n');os.replace(tmp,p);print(json.dumps(x),flush=True)
def main():
 own=(T/'control/FINITE_GOAL_CONTROLLER.lock').open('a+b');fcntl.flock(own,fcntl.LOCK_EX|fcntl.LOCK_NB)
 assert not (T/'control/CONTROLLER_START_R3.json').exists(),'finite worker already started'
 (T/'control/CONTROLLER_START_R3.json').write_text(json.dumps({'pid':os.getpid(),'start_ticks':int(pathlib.Path('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19]),'scope':'one finite exact12-cell short3 cohort','no_retry':True,'max_shared_wait_seconds':21600},indent=2)+'\n')
 start=time.monotonic();installer=module('exact_goal_installer','short3_install.py')
 while not (T/'control/NATIVE_REQUEST_INSTALL_RECEIPT.json').exists():
  if time.monotonic()-start>21600:state({'state':'HOLD_SHARED_RELEASE_WAIT_BOUND','actual_starts':0});return
  if (T/'control/ABORT').exists():state({'state':'USER_ABORT_BEFORE_REGISTER','actual_starts':0});return
  try:proof=installer.install();state(proof)
  except (BlockingIOError,AssertionError) as error:
   state({'state':'WAIT_SHARED_NATIVE_RELEASE','reason':str(error),'actual_starts':0,'elapsed_seconds':time.monotonic()-start});time.sleep(30)
 native=module('current_goal_native','short3_native.py');strict=module('current_goal_strict','short3_strict_r2.py')
 matrix=read(T/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json')['matrix_order'];completed=[]
 for cell in matrix:
  existing=T/'control/qualification_ledger'/(cell+'.INTENT.json')
  if existing.exists():
   assert cell=='E2-AEF3-NN-DM','only the one closed original point may be consumed before this continuation'
   science=strict.terminal(cell);archive=read(T/'control'/(cell+'_ARCHIVE_RECEIPT.json'))
   assert archive['status']=='ARCHIVE_VERIFIED_AND_RESTORE_VERIFIED_NATIVE_TARGET'
   completed.append({'cell':cell,'cycles':science['cycles'],'uuid':science['uuid'],'archive':archive,'original_spent_run_postprocess_only':True})
   state({'state':'PRESERVED_CONSUMED_CELL_ALREADY_ACCEPTED_ARCHIVED','cell':cell,'completed':completed})
   continue
  assert not existing.exists(),'consumed cell never restarted'
  if (T/'control/ABORT').exists():raise RuntimeError('USER_ABORT')
  state({'state':'PREPARING_FRESH_CELL','cell':cell,'completed':completed})
  r=subprocess.run([str(N/'bin/experiment'),'prepare',cell,'--project','DTC_L1'],capture_output=True,text=True,timeout=90)
  (T/'control'/(cell+'.R3.PREPARE.json')).write_text(r.stdout);r.check_returncode()
  state({'state':'RUNNING_FRESH_CELL','cell':cell,'completed':completed})
  with (T/'control'/(cell+'.R3.CLI_EXECUTION.json')).open('x') as log:
   r=subprocess.run([str(N/'bin/experiment'),'run-native',cell,'--project','DTC_L1'],stdout=log,stderr=subprocess.STDOUT)
  r.check_returncode()
  science=strict.terminal(cell)
  intent=read(T/'control/qualification_ledger'/(cell+'.INTENT.json'));out=pathlib.Path(intent['output'])
  with (out/'AEFAIR_STRICT.json').open('x') as f:json.dump(science,f,indent=2);f.write('\n')
  qual={'status':'AEFAIR_SCIENCE_QUALIFIED','uuid':science['uuid'],'cohort':cell,'strict_sha256':hashlib.sha256((out/'AEFAIR_STRICT.json').read_bytes()).hexdigest(),'cycles':science['cycles'],'SOURCE_KEEP':True}
  (T/'DTC/control'/('SCIENCE_QUALIFICATION_'+cell+'.json')).write_text(json.dumps(qual,indent=2)+'\n')
  state({'state':'ARCHIVING_ACCEPTED_CELL','cell':cell,'cycles':science['cycles'],'completed':completed})
  r=subprocess.run([str(N/'bin/result'),'archive',cell],capture_output=True,text=True,timeout=300)
  (T/'control'/(cell+'.R3.ARCHIVE_CLI.json')).write_text(r.stdout+r.stderr);r.check_returncode()
  archive=json.loads(r.stdout);assert archive['receipt']['status']=='ARCHIVE_VERIFIED_AND_RESTORE_VERIFIED_NATIVE_TARGET'
  completed.append({'cell':cell,'cycles':science['cycles'],'uuid':science['uuid'],'archive':archive['receipt']})
  state({'state':'CELL_SCIENCE_ARCHIVE_RESTORE_COMPLETE','cell':cell,'completed':completed})
 def close(r):r['registered_future_requests'][native.REQUEST]['state']='COMPLETE'
 native.update_authority(close);state({'state':'ALL_TWELVE_SCIENCE_ARCHIVE_RESTORE_COMPLETE','completed':completed,'remaining':'scientific interpretation and publication'})
if __name__=='__main__':
 try:main()
 except BaseException as error:
  try:
   n=module('goal_fail_close','short3_native.py')
   if n.REQUEST in read(N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json')['registered_future_requests']:
    def seal(r):
     q=r['registered_future_requests'][n.REQUEST];q['sealed_unused']=q['remaining'];q['remaining']=0;q['state']='STOP_UNACCEPTED';q['failure']=repr(error)
    n.update_authority(seal)
  except BaseException as secondary:print('SEAL_EXCEPTION',repr(secondary),flush=True)
  state({'state':'STOP_OR_HOLD_NO_AUTOMATIC_RETRY','error':repr(error)});raise
