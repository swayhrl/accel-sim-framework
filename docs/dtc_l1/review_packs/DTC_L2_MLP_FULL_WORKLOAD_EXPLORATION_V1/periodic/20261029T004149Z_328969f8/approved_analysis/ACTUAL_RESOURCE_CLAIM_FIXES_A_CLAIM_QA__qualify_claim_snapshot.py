"""Three focused bookkeeping cases with unchanged saveclaims AST and real put.
No run_scheduler loop, owner process, registry operation, thread pool or model.
"""
import pathlib as P,json,hashlib,ast,copy,types,threading,os,tempfile,importlib.util,traceback
A=P.Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1');R=P.Path('/root/data/dtc_l2_mlp_exploration_20261027_v1');D=A/'agents/A/owner_claim_snapshot_sync_v1';S=types.SimpleNamespace
def read(p):return json.loads(P.Path(p).read_bytes())
def sha(p):return hashlib.sha256(P.Path(p).read_bytes()).hexdigest()
def put(p,v):p=P.Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,sort_keys=True,indent=2)+'\n')
def load(n,p):s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
lib=load('actual_claim_snapshot_sync',D/'claim_snapshot_sync.py');ops_path=R/'tools/l2_ops.py';ops=load('actual_l2ops_put_readonly_import',ops_path);root=P.Path(tempfile.mkdtemp(prefix='PRIVATE_CLAIM_BOOKKEEPING_',dir=D));snapshot=R/'control/POOL_DISPATCH_RESERVATIONS.json';disk=read(snapshot);diag_path=R/'control/operational_amendments/broad_shared_cpu_v1/actual_install_v2/readonly_diagnostics_v8/ACK.json';diag=read(diag_path);claims=copy.deepcopy(diag['claims']);assert lib.observation_delta(disk,claims)
path=root/'control/POOL_DISPATCH_RESERVATIONS.json';put(path,disk);initial_disk_sha=sha(snapshot)
calls=[];writes=[]
def writer(p,v,exclusive=False):writes.append((str(p),copy.deepcopy(v)));return ops.put(p,v,exclusive)
tree=ast.parse(ops_path.read_text());run=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='run_scheduler');save=copy.deepcopy(next(n for n in run.body if isinstance(n,ast.FunctionDef)and n.name=='saveclaims'))
factory=ast.FunctionDef(name='run_scheduler',args=ast.arguments(posonlyargs=[],args=[ast.arg(arg='claims')],vararg=None,kwonlyargs=[],kw_defaults=[],kwarg=None,defaults=[]),body=[save,ast.Return(value=ast.Name(id='saveclaims',ctx=ast.Load()))],decorator_list=[]);mod=ast.fix_missing_locations(ast.Module(body=[factory],type_ignores=[]));namespace={'R':root,'put':writer};exec(compile(mod,str(ops_path),'exec'),namespace);saveclaims=namespace['run_scheduler'](claims)
assert lib.code_shape(saveclaims.__code__)==lib.code_shape(lib.expected_saveclaims_code(str(ops_path)))
prior_path=root/'prior_choose_fixture.py';prior_path.write_text('def choose(*args):\n return hook(*args)\n');prior=load('private_prior_choose',prior_path)
def original(*args):assert read(path)==dict(claims=claims);calls.append(args);return {'PRIVATE_PREVIOUS_DECISION':True}
prior.hook=original
aging=S(lock=threading.RLock(),original=object(),frame_provider=object(),state=S(advance=lambda frame:None));res=S(choose_dispatch=prior.choose,resources=object(),DTC_LARGE_JOB_AGING_INSTALLED=aging);q=dict(request='DTC_L2_MLP_FULL_WORKLOAD_EXPLORATION_20261027_V1',qualification_only=True,additional_operational_overlays={},budget=360,remaining=24,consumed={'KEEP_UUID':{'uuid':'UNCHANGED'}});engine=S(registered=lambda:(None,None,q,None),assert_parent_lease=lambda:None);worker=object();frame=S(f_locals=dict(engine=engine,res=res,claims=claims,saveclaims=saveclaims),f_globals={'worker':worker});main=S()
pins={str(p):sha(p)for p in [D/'claim_snapshot_sync.py',ops_path,prior_path]};qa=root/'CPU_ONLY_QA.json';rb=root/'CPU_ONLY_READBACK.json';put(qa,dict(status='PASS',saveclaims_real_serialization_qualified=True,observation_flags_only_qualified=True,source_sha256=sha(D/'claim_snapshot_sync.py'),dependency_pins=pins,qualification_only=True));put(rb,dict(verified=True,QA_sha256=sha(qa),source_sha256=sha(D/'claim_snapshot_sync.py'),dependency_pins=pins,qualification_only=True))
cfg=dict(schema=lib.ID,overlay_id=lib.ID,request=q['request'],root=str(root),status='ACTIVE_OPERATIONAL_BOOKKEEPING_ONLY',qualification_only=True,source_path=str(D/'claim_snapshot_sync.py'),source_sha256=sha(D/'claim_snapshot_sync.py'),ops_source_path=str(ops_path),ops_source_sha256=sha(ops_path),prior_choose_source_path=str(prior_path),prior_choose_source_sha256=sha(prior_path),dependency_pins=pins,owner={'pid':os.getpid(),'start_ticks':lib.birth()},scheduler_thread_ident=threading.get_ident(),QA_path=str(qa),QA_sha256=sha(qa),readback_path=str(rb),readback_sha256=sha(rb));q['additional_operational_overlays'][lib.ID]=lib.record(cfg);beforeq=copy.deepcopy(q);state=lib.install_on_frame(frame,cfg,lambda:None,main);checks=[]
def check(name,fn):
 try:r=fn();checks.append(dict(name=name,status='PASS',details=r))
 except BaseException as e:checks.append(dict(name=name,status='FAIL',error=repr(e),traceback=traceback.format_exc()))
args=([{'cohort':'CPU_ONLY_NO_DISPATCH'}],{'sample':1},claims,{'history':2},{'previous':3},{'policy':4},9)
def flags():
 before=copy.deepcopy(claims);value=res.choose_dispatch(*args);assert value=={'PRIVATE_PREVIOUS_DECISION':True}and len(calls)==len(writes)==1 and all(a is b for a,b in zip(calls[0],args))
 assert read(path)==dict(claims=claims)and claims==before and frame.f_locals['claims']is claims and q==beforeq and frame.f_globals['worker']is worker
 oldscan=next(c for c in claims if'6df3a84b612086e8'in c);assert claims[oldscan]['observed_model']is False
 assert lib.observation_delta(disk,claims)==state['last_sync']['changed_observation_cohorts']and len(state['last_sync']['changed_observation_cohorts'])==2
 return dict(real_saveclaims_AST_code_and_original_atomic_put=True,only_two_actual_observed_flags_persisted=True,oldscan_false_RAM_CPU_all_preserved=True,previous_exact_once_after_readback=True)
check('actual_live_vs_disk_flags_original_saveclaims_serialization_delegate',flags)
def same():
 old=path.read_bytes();count=len(writes);value=res.choose_dispatch(*args);assert value and len(writes)==count and path.read_bytes()==old and len(calls)==2 and not state['last_sync']['changed_observation_cohorts'];return dict(already_synced_no_redundant_write=True,previous_called_once=True)
check('already_equal_snapshot_no_write_and_exact_once_delegate',same)
def negative_and_restore():
 baseline=path.read_bytes();done=[];oldcalls=len(calls);oldwrites=len(writes)
 for kind in ['disk_key','RAM_cost','observed_not_bool','source_pin','closure_reference']:
  d=read(path);key=next(iter(d['claims']))
  if kind=='disk_key':d['claims'].pop(key);put(path,d)
  if kind=='RAM_cost':d['claims'][key]['RAM_cap_bytes']+=1;put(path,d)
  if kind=='observed_not_bool':d['claims'][key]['observed_model']=1;put(path,d)
  if kind=='source_pin':cfg['dependency_pins'][str(ops_path)]='WRONG'
  if kind=='closure_reference':frame.f_locals['claims']=copy.deepcopy(claims)
  current=path.read_bytes();assert res.choose_dispatch(*args)is None and path.read_bytes()==current and len(calls)==oldcalls and len(writes)==oldwrites
  path.write_bytes(baseline);cfg['dependency_pins'][str(ops_path)]=sha(ops_path);frame.f_locals['claims']=claims;done.append(kind)
 assert q==beforeq and frame.f_globals['worker']is worker
 previous=state['previous'];lib.restore_in_owner(lambda:None,main);assert res.choose_dispatch is previous and read(path)==dict(claims=claims)and claims==diag['claims']
 return dict(structural_cost_type_source_closure_reject_before_write_or_delegate=done,exact_restore=True,persisted_observations_not_rolled_back=True)
check('structural_source_closure_drift_HOLD_before_writes_exact_restore',negative_and_restore)
result=dict(schema='OWNER_CLAIM_SNAPSHOT_SYNC_FOCUSED_CPU_QUALIFICATION_V1',status='PASS'if all(x['status']=='PASS'for x in checks)else'FAIL',source_path=str(D/'claim_snapshot_sync.py'),source_sha256=sha(D/'claim_snapshot_sync.py'),driver_path=__file__,driver_sha256=sha(__file__),checks=checks,count=3,actual_disk_initial_sha256=initial_disk_sha,actual_live_diag_path=str(diag_path),actual_live_diag_sha256=sha(diag_path),saveclaims_AST_extracted_unchanged_from=str(ops_path),ops_sha256=sha(ops_path),original_atomic_put_executed_only_private_root=True,fixture_root=str(root),authority_owner_and_priorchooser='PRIVATE_STANDINS_NOT_MAIN',actual_models_started=0,production_mutations=0,new_grants=0,signals=0)
put(D/'CPU_QUALIFICATION.json',result);print(json.dumps(dict(status=result['status'],source_sha256=result['source_sha256'],QA_sha256=sha(D/'CPU_QUALIFICATION.json'),checks=[(x['name'],x['status'],x.get('error'))for x in checks]),indent=2))
