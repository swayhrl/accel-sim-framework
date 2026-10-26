"""Actual frontend/bridge/frozen-native path to Popen, with private fake authority.

One disposable CPU Python parent is used solely so the unchanged native lease
predicate can inspect real PID/start, ancestry and a real private flock FD.
No scientific subprocess, preexec callback, production ledger or entry is used.
"""
import pathlib,json,hashlib,importlib.util,copy,tempfile,types,os,subprocess,datetime,sys,fcntl,io,contextlib
P=pathlib.Path;F=P('/root/data/dtc_failure_repair_20261025_v1');D=F/'ops/revision17';T=P('/root/data/dtc_main_v100_sweep_20261025_v1');N=P('/root/data/ep_l2_dtc_l1_native_v2');REAL=F/'validation_lava_memory_v2';L=F/'validation_late_failure_v1';REQ='DTC_AE_LAVAMEM_REPAIR_20261026_V2';LATE='DTC_AE_LATE_FAILURE_REPAIR_20261026_V1';ORIG='DTC_AE_V100_FULL_SWEEP_20261025_V1'
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def put(p,x):p=P(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x))
def load(name,p):s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
if not os.environ.get('R17_CPU_LEASE_FIXTURE'):
 root=P(tempfile.mkdtemp(prefix='R17_BRIDGE_LEASE_CPU_',dir=F/'control'));wrapper=root/'sweep_controller.py';wrapper.write_text('import runpy\nrunpy.run_path('+repr(str(P(__file__).resolve()))+",run_name='__main__')\n");env=dict(os.environ,R17_CPU_LEASE_FIXTURE=str(root));p=subprocess.run([sys.executable,str(wrapper)],env=env,text=True,capture_output=True);print(p.stdout,end='');print(p.stderr,end='',file=sys.stderr);raise SystemExit(p.returncode)
FIX=P(os.environ['R17_CPU_LEASE_FIXTURE']);assert FIX.resolve().is_relative_to((F/'control').resolve()) and FIX.name.startswith('R17_BRIDGE_LEASE_CPU_');MANIFEST=D/'OPERATIONAL_PARENT_BRIDGE_MANIFEST_V1.json';mapping=read(MANIFEST);assert mapping['actual_parent_sha256']==sha(D/'sweep_controller.py');BRIDGESHA=sha(D/'operational_parent_bridge_v1.py');FRONTSHA=sha(D/'frontend_v1.py');assert BRIDGESHA=='01ad5280d71daa9763b209e2fb22759b9f33604c8e401952299b84eafe524e2b';checks=[];scenarios=[]
def check(name,fn):fn();checks.append(dict(name=name,status='PASS'))
def reject(name,fn):
 try:fn()
 except (RuntimeError,AssertionError,KeyError,FileNotFoundError):checks.append(dict(name=name,status='PASS'));return
 raise RuntimeError('negative accepted: '+name)
class ReachedPopen(BaseException):pass
class PopenProxy:
 def __init__(self,real,fn):self.real=real;self.fn=fn
 def Popen(self,*a,**k):return self.fn(*a,**k)
 def __getattr__(self,k):return getattr(self.real,k)
baseline_native=load('r17_baseline_readonly_authority',T/'tools/sweep_native_cap1m.py');realreg,realepoch=baseline_native.read_current_authority();realq=realreg['registered_future_requests'][REQ];future=sorted(set(realq['admitted_specs'])-set(realq['consumed'])-set(realq.get('sealed',[])));assert len(future)==1;CELL=future[0];ticks=int(P('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19]);frozenfiles=[REAL/'control/EXECUTION_PLAN_V2.json',REAL/'control/LAVAMEM_BUILD_PROFILE_V2.json',REAL/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json',REAL/'control/SCIENCE_AUTHORIZATION.json',REAL/'control/specs'/(CELL+'.json'),REAL/'tools/lavamem_native_v2.py',REAL/'tools/lavamem_strict_v2.py',L/'control/EXECUTION_PLAN_V1.json',N/'bin/native'];frozen_before={str(p):sha(p)for p in frozenfiles}
for index,kind in enumerate(['fresh_positive','missing_binding','wrong_parent_SHA','wrong_lease_birth','wrong_epoch','missing_alias','already_consumed']):
 root=FIX/(str(index)+'_'+kind);r=root/'lava';orig=root/'original';fakeN=root/'native';fakeD=root/'bridge';engine=load('r17_private_engine_'+str(index),REAL/'tools/lavamem_native_v2.py');engine.R=r;engine.N=fakeN
 for sub in ['control/specs','control/qualification_ledger','DTC/run/results','DTC/run/recovery','DTC/control','logs','analysis','DTC/env']:(r/sub).mkdir(parents=True,exist_ok=True)
 for p in (REAL/'control').glob('*.json'):
  if not p.name.endswith('_SPEC.json'):(r/'control'/p.name).write_bytes(p.read_bytes())
 for p in (REAL/'control/specs').glob('*.json'):(r/'control/specs'/p.name).write_bytes(p.read_bytes());(r/'control'/(p.stem+'_SPEC.json')).symlink_to('specs/'+p.name)
 for name,target in [('common-lib',REAL/'common-lib'),('DTC/env/lib',REAL/'DTC/env/lib'),('tools',REAL/'tools')]:(r/name).symlink_to(target,target_is_directory=True)
 for c in realq['consumed']:(r/'control/qualification_ledger'/(c+'.INTENT.json')).write_bytes((REAL/'control/qualification_ledger'/(c+'.INTENT.json')).read_bytes())
 fakeD.mkdir(parents=True);(fakeD/MANIFEST.name).write_bytes(MANIFEST.read_bytes());heldpath=fakeN/'control/qualification_ledger/NATIVE_QUALIFICATION.lock';heldpath.parent.mkdir(parents=True);held=heldpath.open('a+b');fcntl.flock(held,fcntl.LOCK_EX)
 lease=dict(pid=os.getpid(),start_ticks=ticks,fd=held.fileno(),request=ORIG,controller_sha256=mapping['actual_parent_sha256'],additional_requests=['DTC_AE_FAILURE_REPAIR_VALIDATION_20261025_V1',REQ,LATE]);put(orig/'control/BATCH_LEASE.json',lease)
 registry=copy.deepcopy(realreg)
 for k in [ORIG,REQ,LATE]:registry['registered_future_requests'][k]['orchestrator_sha256']=mapping['actual_parent_sha256']
 records={}
 for k in [REQ,LATE]:
  q=registry['registered_future_requests'][k];record=dict(manifest_path=str(fakeD/MANIFEST.name),manifest_sha256=sha(MANIFEST),bridge_sha256=BRIDGESHA,actual_parent_sha256=mapping['actual_parent_sha256'],actual_parent_pid=os.getpid(),actual_parent_start_ticks=ticks,actual_parent_qualification_fd=held.fileno(),effective_future_cohorts=sorted(set(q['admitted_specs'])-set(q['consumed'])-set(q.get('sealed',[]))),consumed_prefix_UUIDs={c:v['uuid']for c,v in q['consumed'].items()});q.setdefault('operational_parent_continuations',[]).append(record);records[k]=record
 spec=read(r/'control/specs'/(CELL+'.json'));cap=read(r/'control'/('OPERATIONAL_OUTPUT_CAP_'+CELL+'.json'))['effective_result_cap_bytes'];put(r/'control/POOL_DISPATCH_RESERVATIONS.json',{'claims':{CELL:{'host_cpu':225,'result_cap_bytes':cap,'RAM_cap_bytes':128*2**30}}})
 rp=fakeN/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json';ep=fakeN/'control/CURRENT_SCIENCE_EPOCH.json';put(rp,registry);epoch=copy.deepcopy(realepoch);epoch['native_registry_sha256']=sha(rp);put(ep,epoch);put(fakeN/'EP/control/SCIENCE_QUALIFICATION.json',read(N/'EP/control/SCIENCE_QUALIFICATION.json'))
 if kind=='missing_binding':registry['registered_future_requests'][REQ]['operational_parent_continuations']=[]
 if kind=='wrong_parent_SHA':lease['controller_sha256']='0'*64;put(orig/'control/BATCH_LEASE.json',lease)
 if kind=='wrong_lease_birth':records[REQ]['actual_parent_start_ticks']+=1
 if kind=='wrong_epoch':epoch['epoch']=1
 if kind=='already_consumed':registry['registered_future_requests'][REQ]['consumed'][CELL]={'uuid':'CPU_ALREADY_CONSUMED'};registry['registered_future_requests'][REQ]['remaining']=0
 if kind=='missing_alias':(r/'control'/(CELL+'_SPEC.json')).unlink()
 put(rp,registry);epoch['native_registry_sha256']=sha(rp);put(ep,epoch);engine.authority=lambda:(read(rp),read(ep));resources=[]
 engine.resources=lambda s,fresh_source=False:(resources.append(dict(cohort=s['cohort'],fresh_source=fresh_source)) or dict(physical_RAM_pass=True,physical_disk_pass=True,CPU_ONLY_PRIVATE_RESOURCE_FIXTURE=True))
 def check_input(s):
  path=P(s.get('input_binding_path',str(T/'control/input_bindings'/(s['input_digest']+'.json'))));assert sha(path)==s['input_binding_sha256'];return dict(status='CPU_INPUT_BINDING_SHA_REUSES_PRIOR_FINAL_CURRENTSTAT_PROOF',binding_sha256=sha(path))
 engine.check_input=check_input;barrier=[];native_instances=[]
 def original_native():
  n=load('r17_fixture_native_'+str(index)+'_'+str(len(native_instances)),T/'tools/sweep_native_cap1m.py');n.ROOT=orig;n.NATIVE=fakeN;n.read_current_authority=engine.authority;n.authority_consistent=lambda:True;native_instances.append(n);return n
 engine.original_native=original_native;real_engine=engine.engine
 def native_engine():
  n=real_engine();n.NATIVE=fakeN;n.read_current_authority=engine.authority;n.authority_consistent=lambda:True
  def reached(argv,**kwargs):
   ip=r/'control/qualification_ledger'/(CELL+'.INTENT.json');i=read(ip);q=read(rp)['registered_future_requests'][REQ];assert q['consumed'][CELL]['intent_sha256']==sha(ip) and q['consumed'][CELL]['uuid']==i['uuid'];b=i['operational_parent_continuation_binding'];assert (b['actual_lease_pid'],b['actual_lease_start_ticks'],b['actual_lease_fd'])==(os.getpid(),ticks,held.fileno());assert b['actual_controller_sha256']==mapping['actual_parent_sha256'] and b['scientific_plan_parent_sha256']==mapping['scientific_parent_lineage_sha256'] and b['lease_returned_unchanged']is True;assert i['repair_execution_overlay']['engine_sha256']==sha(REAL/'tools/lavamem_native_v2.py') and i['observer_exit_race_binding']['profile']=='OBSERVER_PROC_EXIT_RACE_V1'
   assert argv[-len(spec['native_simulator_argv']):]==spec['native_simulator_argv'] and str(r/'tools/bin/strace')in argv and kwargs['env']['DTC_AG7_GENERATION']==i['uuid'] and kwargs['pass_fds']and callable(kwargs['preexec_fn']);assert len(resources)>=3;assert not list((r/'control/qualification_ledger').glob('*.DONE.json'));assert q['remaining']==0 and len(q['consumed'])==2
   barrier.append(dict(status='REAL_FRONT_BRIDGE_OBSERVER_NATIVE_POPEN_BARRIER',intent_sha256=sha(ip),new_binding=b,real_native_lease_PID_start_FD_validated=True,real_model_Popen_or_preexec=False,source_spec_argv_unchanged=True,fake_remaining=q['remaining'],resource_fixture_calls=len(resources)));raise ReachedPopen()
  n.subprocess=PopenProxy(subprocess,reached);return n
 engine.engine=native_engine;bridge=load('r17_bridge_'+str(index),D/'operational_parent_bridge_v1.py');bridge.MANIFEST=fakeD/MANIFEST.name;bridge.ROOTS=dict(bridge.ROOTS,**{REQ:r});oldload=bridge.load;bridge.load=lambda name,path:engine if P(path).name=='lavamem_native_v2.py'else oldload(name,path)
 front=load('r17_front_'+str(index),D/'frontend_v1.py');front.load=lambda name,path:bridge
 if kind=='fresh_positive':
  prep=front.main(['experiment','prepare',CELL,'--project','DTC_L1']);assert prep['operational_parent_continuation_binding']['actual_controller_sha256']==mapping['actual_parent_sha256'];assert engine.assert_parent_lease()==lease
  try:front.main(['experiment','run-native',CELL,'--project','DTC_L1']);raise RuntimeError('missed Popen barrier')
  except ReachedPopen:assert len(barrier)==1
  check('actual frontend prepare/run bridge to frozen observer-native Popen barrier; exact actual INTENT SHA consumed once',lambda:None)
 else:reject(kind+' rejects actual front route with0 Popen',lambda:front.main(['experiment','run-native',CELL,'--project','DTC_L1']));assert not barrier and not(r/'control/qualification_ledger'/(CELL+'.INTENT.json')).exists()
 scenarios.append(dict(scenario=kind,status='PASS',Popen_barrier_count=len(barrier),barrier=barrier,real_models_started=0));held.close()
check('frozen science specs plans profiles requests authorization entry bytes unchanged',lambda:all(sha(p)==h for p,h in frozen_before.items())or(_ for _ in()).throw(RuntimeError('frozen bytes drift')))
assert sha(D/'operational_parent_bridge_v1.py')==BRIDGESHA and sha(D/'frontend_v1.py')==FRONTSHA and sha(MANIFEST)==sha(FIX/'0_fresh_positive/bridge'/MANIFEST.name)
report=dict(schema='R17_INDEPENDENT_FRONT_BRIDGE_REAL_NATIVE_PRE_POPEN_CPU_V1',status='PASS',observed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),controller_sha256=mapping['actual_parent_sha256'],bridge_sha256=BRIDGESHA,frontend_sha256=FRONTSHA,manifest_sha256=sha(MANIFEST),driver_sha256=sha(__file__),check_count=len(checks),checks=checks,scenarios=scenarios,fixture_root=str(FIX),real_scientific_Popen_calls=0,real_preexec_calls=0,production_entry_or_authority_or_epoch_writes=0,real_scientific_INTENTs_written=0,CPU_only_python_launcher_processes=1,source_spec_plan_pins=[{'path':p,'sha256':h}for p,h in frozen_before.items()],input_fixture_scope='Only resource availability and expensive input currentstat/body actions mocked in private engine; binding SHA, all original source/runtime/approval/native identity/actual lease FD+flock+birth/ancestry/storage BA/argv/env and real native write/consume path executed on fake authority before nonreturning Popen sentinel. No native p.wait status or model identity fabricated.')
dest=D/'BRIDGE_FRONT_REAL_NATIVE_PRE_POPEN_CPU_QUALIFICATION_V1.json'
with dest.open('x')as f:json.dump(report,f,indent=2);f.write('\n')
print(json.dumps(dict(status='PASS',checks=len(checks),scenarios=len(scenarios),path=str(dest),sha256=sha(dest),driver_sha256=sha(__file__),real_models_started=0)))
