from pathlib import Path
import json,hashlib,subprocess,os,fcntl,datetime,sys
P=Path;R=P('/root/data/dtc_perf_first_remaining28_20261104_v1');N=P('/root/data/ep_l2_dtc_l1_native_v2');REQ='DTC_PERF_FIRST_NON_TAG_REMAINING28_20261104_V1';D=R/'control/actual_owner_attach_v1';Q=D/'execution_queue_v1'
def rd(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def put(p,v):
 p=P(p);p.parent.mkdir(parents=True,exist_ok=True);b=v if isinstance(v,bytes)else(json.dumps(v,indent=2)+'\n').encode()
 if p.exists():assert p.read_bytes()==b,'PREEXISTING_CONFLICT '+str(p);return
 with p.open('xb')as f:f.write(b);f.flush();os.fsync(f.fileno())
ref=rd(R/'control/QUALIFICATION_REVIEW_REFERENCE.json');src=P(ref['path']);assert sha(src)==ref['sha256'];qual=rd(src)
assert qual['status']=='PASS'and qual['execution_plan_sha256']==sha(R/'control/EXECUTION_PLAN.json')and qual['registry_candidate_sha256']==sha(R/'control/REGISTRY_REQUEST_CANDIDATE.json')
put(R/'control/CPU_QUALIFICATION.json',src.read_bytes())
plan=rd(R/'control/EXECUTION_PLAN.json')
for x in plan['source_pins']:assert sha(x['path'])==x['sha256']
import types
def _private(path,name):
 m=types.ModuleType(name);m.__file__=str(path);exec(compile(path.read_bytes(),str(path),'exec'),m.__dict__);return m
sys.dont_write_bytecode=True
_engine=_private(R/'tools/perf28_native.py','perf28_queue_engine_readonly')
_receipt=_private(R/'tools/perf28_terminal_gate_receipt.py','perf28_queue_actual_first4_closure')
_registry,_epoch=_engine.authority();_release=_receipt.verify(plan,_registry)
assert _release['validator_source_sha256']=='06996cc8f27ddbe67eb73e8979c98bcceb63e8993d98edfb3d7485076070d516'

stat=P('/proc/1498278/stat').read_text().rsplit(')',1)[1].split();assert int(stat[19])==977758783 and stat[0]not in['Z','X']
assert set(os.sched_getaffinity(1498278))==set(range(32,64))
for fd,path in [(3,'/root/data/dtc_main_v100_sweep_20261025_v1/control/FINITE_CONTROLLER.lock'),(4,str(N/'control/qualification_ledger/NATIVE_QUALIFICATION.lock'))]:
 assert'FLOCK'in P('/proc/1498278/fdinfo/'+str(fd)).read_text()and os.readlink('/proc/1498278/fd/'+str(fd))==path
reg=rd(N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json');assert REQ not in reg['registered_future_requests'];assert not(R/'control/PARENT_ADDON_ACK.json').exists()
Q.mkdir(parents=True,exist_ok=True);source=R/'tools/perf28_parent_addon.py';pin=sha(source)
body='''import pathlib,json,hashlib,types,traceback,datetime,os,sys
try:
 assert sys.dont_write_bytecode
 _pf28_path=pathlib.Path('__SOURCE__')
 assert hashlib.sha256(_pf28_path.read_bytes()).hexdigest()=='__SHA__'
 _pf28_module=types.ModuleType('dtc_perffirst_remaining28_main_callback_v1');_pf28_module.__file__=str(_pf28_path)
 exec(compile(_pf28_path.read_bytes(),str(_pf28_path),'exec'),_pf28_module.__dict__)
 _pf28_module.apply('__DIRECTORY__')
except BaseException:
 try:
  with (pathlib.Path('__DIRECTORY__')/'CALLBACK_ERROR.json').open('x')as _pf28_f:
   json.dump(dict(schema='DTC_PERFFIRST28_MAIN_CALLBACK_ERROR_V1',UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),traceback=traceback.format_exc(),automatic_requeue=False,owner_exception_contained=True),_pf28_f,indent=2);_pf28_f.write(chr(10));_pf28_f.flush();os.fsync(_pf28_f.fileno())
 except BaseException:pass
'''.replace('__SOURCE__',str(source)).replace('__SHA__',pin).replace('__DIRECTORY__',str(D))
compile(body,'perf_remaining28_owner_BODY','exec');payload=body.encode()+b'\0';assert len(payload)<4096
put(Q/'BODY.py',body.encode());put(Q/'PENDING.bin',payload)
gdb='''set pagination off
set confirm off
set auto-load python-scripts off
set scheduler-locking off
set $pf28buf=(void*)mmap((void*)0,4096,3,34,-1,0)
restore __PENDING__ binary $pf28buf
set $pf28queued=(int)Py_AddPendingCall((int(*)(void*))PyRun_SimpleString,$pf28buf)
printf "QUEUED=%d\\n",$pf28queued
detach
quit
'''.replace('__PENDING__',str(Q/'PENDING.bin'))
put(Q/'APPLY.gdb',gdb.encode())
if '--enqueue'not in sys.argv:
 print(json.dumps(dict(status='CALLBACK_PAYLOAD_PREPARED_ONLY',owner_pid=1498278,source_sha256=pin,model_starts=0)));sys.exit(0)
with(R/'control/OWNER_CALLBACK_QUEUER.lock').open('a+b')as lock:
 fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);assert not(Q/'QUEUE_INVOKED.json').exists(),'OBSERVE_SAME_CALLBACK_NEVER_BLIND_REQUEUE'
 put(Q/'QUEUE_INVOKED.json',dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),invoke_once=True,target_pid=1498278,target_start_ticks=977758783,source_sha256=pin,plan_sha256=sha(R/'control/EXECUTION_PLAN.json'),qualification_sha256=sha(R/'control/CPU_QUALIFICATION.json'),model_starts_by_queuer=0))
 x=subprocess.run(['gdb','-q','-n','-batch','-p','1498278','-x',str(Q/'APPLY.gdb')],capture_output=True,text=True,timeout=45)
 put(Q/'GDB.stdout',x.stdout.encode());put(Q/'GDB.stderr',x.stderr.encode());print(json.dumps(dict(returncode=x.returncode,stdout=x.stdout[-2500:],stderr=x.stderr[-2000:])))
 assert x.returncode==0 and'QUEUED=0'in x.stdout,'OBSERVE_ACTUAL_OWNER_STATE_NO_BLIND_REQUEUE'
 put(Q/'QUEUED.json',dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),queued_once=True,no_blind_requeue=True))
 print(json.dumps(dict(status='EXACT28_SAME_OWNER_CALLBACK_QUEUED_ONCE',owner_pid=1498278,start_ticks=977758783,no_second_dispatcher=True)))
