"""Root CPU waiter: one audited closure, one callback to existing owner, no model dispatcher."""
from pathlib import Path
import json,os,sys,time,hashlib,subprocess,fcntl,datetime,traceback,types
sys.dont_write_bytecode=True
A=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_perf_first_parallel_exploration_20261104_v1');S=A/'remaining28/gate_release_waiter_v1';R=Path('/root/data/dtc_perf_first_remaining28_20261104_v1');REQ='DTC_PERF_FIRST_NON_TAG_REMAINING28_20261104_V1'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rd(p):return json.loads(Path(p).read_bytes())
def put(p,v,once=False):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);b=(json.dumps(v,sort_keys=True,indent=2)+'\n').encode()
 if once:
  with p.open('xb')as f:f.write(b);f.flush();os.fsync(f.fileno())
 else:
  tmp=p.with_name('.'+p.name+'.'+str(os.getpid())+'.writing');tmp.write_bytes(b);tmp.replace(p)
def stamp():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def status(state,**data):put(S/'STATUS.json',dict(UTC=stamp(),state=state,model_starts_by_this_process=0,registry_writes_by_this_process=0,Goal_mutations=0,**data))
def private(path,name):
 m=types.ModuleType(name);m.__file__=str(path);exec(compile(path.read_bytes(),str(path),'exec'),m.__dict__);return m
def invariants(cfg):
 assert sha(R/'control/EXECUTION_PLAN.json')==cfg['execution_plan_sha256']and sha(R/'control/REGISTRY_REQUEST_CANDIDATE.json')==cfg['registry_candidate_sha256']
 ref=rd(R/'control/QUALIFICATION_REVIEW_REFERENCE.json');assert sha(ref['path'])==ref['sha256']==cfg['qualification_sha256'];q=rd(ref['path']);assert q['status']=='PASS'and q['execution_plan_sha256']==cfg['execution_plan_sha256']and q['registry_candidate_sha256']==cfg['registry_candidate_sha256']
 for row in cfg['source_pins']:assert sha(row['path'])==row['sha256'],'WAITER_SOURCE_PIN_DRIFT '+row['path']
 plan=rd(R/'control/EXECUTION_PLAN.json');contract=plan['first4_terminal_gate']
 assert cfg['first4_validator_path']==contract['source_path']and sha(cfg['first4_validator_path'])==contract['source_sha256']=='06996cc8f27ddbe67eb73e8979c98bcceb63e8993d98edfb3d7485076070d516'
 assert cfg['first4_gate_output']==contract['output_path']
 assert Path(cfg['same_owner_queuer_path']).resolve()==(A/'remaining28/control/queue_remaining28_owner_once.py').resolve()
 assert sha(cfg['same_owner_queuer_path'])==cfg['same_owner_queuer_sha256']
 assert sha(__file__)==cfg['waiter_source_sha256']
 return plan
def run():
 os.nice(10);S.mkdir(parents=True,exist_ok=True)
 with(S/'CPU_GATE_WAITER.lock').open('a+b')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);cfg=rd(S/'CONTRACT.fixed.json');plan=invariants(cfg)
  validator=Path(cfg['first4_validator_path']);output=Path(cfg['first4_gate_output']);queuer=Path(cfg['same_owner_queuer_path'])
  engine=private(R/'tools/perf28_native.py','root_waiter_readonly_perf28_engine');receipt=private(R/'tools/perf28_terminal_gate_receipt.py','root_waiter_actual_C_closure_receipt')
  while True:
   plan=invariants(cfg);reg,ep=engine.authority()
   callback_dir=R/'control/actual_owner_attach_v1';error=callback_dir/'CALLBACK_ERROR.json';marker=callback_dir/'execution_queue_v1/QUEUE_INVOKED.json'
   if error.exists():status('OWNER_CALLBACK_ERROR_FORWARD_RECONCILIATION_REQUIRED',error_path=str(error),automatic_requeue=False);return
   thread_error=R/'analysis/OWNER_THREAD_ERROR.json'
   if thread_error.exists():status('OWNER_THREAD_ERROR_FORWARD_RECONCILIATION_REQUIRED',error_path=str(thread_error),automatic_requeue=False);return
   if REQ in reg['registered_future_requests']:
    ack=R/'control/PARENT_ADDON_ACK.json'
    if ack.exists():status('SAME_OWNER_REMAINING28_ATTACHED',ACK=rd(ack),further_callbacks=0);return
    status('REQUEST_EXISTS_AWAIT_SAME_CALLBACK_ACK_NO_REQUEUE');time.sleep(10);continue
   if marker.exists():
    status('OWNER_CALLBACK_ALREADY_INVOKED_OBSERVE_ONLY_NO_REQUEUE');time.sleep(10);continue
   if not output.exists():
    if(S/'AUDIT_INVOKED.json').exists():status('ONE_SHOT_AUDIT_ALREADY_INVOKED_WITHOUT_PASS_FORWARD_RECONCILIATION_REQUIRED',audit_retry=False);return
    x=subprocess.run(['/usr/bin/python3','-B',str(validator),'--check-readiness'],text=True,capture_output=True,timeout=120)
    ready=json.loads(x.stdout);assert type(ready.get('ready'))is bool
    if not ready['ready']:
     status('WAIT_ALL4_NATURAL_STRICT_ARCHIVE_RESTORE_NO_NEW_SCIENTIFIC_START',readiness=ready);time.sleep(30);continue
    put(S/'AUDIT_INVOKED.json',dict(UTC=stamp(),source_sha256=sha(validator),one_shot=True,models_started=0),True)
    status('FIRST4_INDEPENDENT_FULL_CLOSURE_AUDIT_RUNNING_NO_MODELS')
    x=subprocess.run(['/usr/bin/python3','-B',str(validator),'--audit'],text=True,capture_output=True,timeout=1800)
    put(S/'AUDIT_COMMAND_RESULT.json',dict(UTC=stamp(),returncode=x.returncode,stdout=x.stdout[-5000:],stderr=x.stderr[-5000:]),True)
    assert x.returncode==0 and output.exists(),'FULL_FIRST4_AUDIT_HOLD_NO_AUTOMATIC_RETRY'
   reg,ep=engine.authority();release=receipt.verify(plan,reg);assert release['first4_terminal_gate_report_sha256']==sha(output)
   # Existing owner alone will reverify this same proof, then register and dispatch.
   put(S/'OWNER_QUEUE_INVOKED.json',dict(UTC=stamp(),exact_request=REQ,queue_source_sha256=sha(queuer),release_evidence=release,one_time=True,model_starts_by_waiter=0),True)
   status('C_FULL_FIRST4_GATE_PASS_QUEUING_ONE_EXISTING_OWNER_CALLBACK',release_evidence=release)
   x=subprocess.run(['/usr/bin/python3','-B',str(queuer),'--enqueue'],text=True,capture_output=True,timeout=90)
   put(S/'OWNER_QUEUE_COMMAND_RESULT.json',dict(UTC=stamp(),returncode=x.returncode,stdout=x.stdout[-5000:],stderr=x.stderr[-5000:]),True)
   assert x.returncode==0,'ONE_OWNER_QUEUE_HOLD_OBSERVE_DO_NOT_REQUEUE'
   status('ONE_EXISTING_OWNER_CALLBACK_QUEUED_AWAIT_ACK',automatic_requeue=False);time.sleep(10)
if __name__=='__main__':
 try:run()
 except BaseException:
  status('CPU_RELEASE_WAITER_HOLD_NO_MODEL_OR_QUEUE_RETRY',traceback=traceback.format_exc(),automatic_retry=False)
  raise
