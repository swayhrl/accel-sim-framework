"""Run the REAL native loop to a Popen barrier inside a disposable fake root.

No model subprocess is forked. Real spec/runtime/auth/INTENT/loader/env/storage-BA
paths are exercised. Expensive input stat/body checks reuse their prior receipt,
after independently verifying the exact input-binding bytes.
"""
import pathlib,json,hashlib,importlib.util,copy,tempfile,types,os,subprocess,datetime
P=pathlib.Path;REAL=P('/root/data/dtc_failure_repair_20261025_v1/validation_remaining_failure_v1');T=P('/root/data/dtc_main_v100_sweep_20261025_v1');N=P('/root/data/ep_l2_dtc_l1_native_v2');REQ='DTC_AE_REMAINING_FAILURE_REPAIR_20261026_V1'
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
class ReachedPopen(BaseException):pass
class PopenProxy:
 def __init__(self,real,callback):self.real=real;self.callback=callback
 def Popen(self,*args,**kwargs):return self.callback(*args,**kwargs)
 def __getattr__(self,key):return getattr(self.real,key)
real_reg=read(N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json');assert REQ not in real_reg['registered_future_requests'];actual_q=read(REAL/'control/REGISTRY_REQUEST_CANDIDATE_V1.json');assert actual_q['remaining']==4 and not actual_q['consumed'] and not list((REAL/'control/qualification_ledger').glob('*.INTENT.json'));entry_sha=sha(N/'bin/native');source=REAL/'tools/remaining_native_v1.py';scope=read(REAL/'control/REMAINING_SCOPE_CANDIDATE_V1.json');results=[];negative=None
for index,point in enumerate(scope['points']+[dict(scope['points'][0],negative_missing_alias=True)]):
 engine=load('native_pre_popen_private_'+str(index),source)
 with tempfile.TemporaryDirectory(prefix='CPU_PRE_POPEN_',dir=REAL/'analysis') as folder:
  root=P(folder);assert root.resolve().is_relative_to((REAL/'analysis').resolve());engine.R=root;fakeN=root/'FAKE_NATIVE_AUTHORITY';engine.N=fakeN
  for name in ['control/specs','control/qualification_ledger','DTC/run/results','DTC/run/recovery','DTC/control','logs','analysis','DTC/env']:(root/name).mkdir(parents=True,exist_ok=True)
  for p in (REAL/'control').glob('*.json'):
   if not p.name.endswith('_SPEC.json'):(root/'control'/p.name).write_bytes(p.read_bytes())
  for p in (REAL/'control/specs').glob('*.json'):(root/'control/specs'/p.name).write_bytes(p.read_bytes());(root/'control'/(p.stem+'_SPEC.json')).symlink_to('specs/'+p.name)
  for name,target in [('common-lib',REAL/'common-lib'),('DTC/env/lib',REAL/'DTC/env/lib'),('tools',REAL/'tools')]:(root/name).symlink_to(target,target_is_directory=True)
  cell=point['cohort'];spec=read(root/'control/specs'/(cell+'.json'));cap=read(root/'control'/('OPERATIONAL_OUTPUT_CAP_'+cell+'.json'))['effective_result_cap_bytes'];cpu=192+(index%4);(root/'control/POOL_DISPATCH_RESERVATIONS.json').write_text(json.dumps({'claims':{cell:{'host_cpu':cpu,'result_cap_bytes':cap,'RAM_cap_bytes':spec['limits']['max_process_tree_rss_bytes']}}}))
  (fakeN/'control/science_authority').mkdir(parents=True);registry=copy.deepcopy(real_reg);registry['registered_future_requests'][REQ]=copy.deepcopy(actual_q);rp=fakeN/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json';ep=fakeN/'control/CURRENT_SCIENCE_EPOCH.json';rp.write_text(json.dumps(registry));epoch=read(N/'control/CURRENT_SCIENCE_EPOCH.json');epoch['native_registry_sha256']=sha(rp);ep.write_text(json.dumps(epoch));engine.authority=lambda:(read(rp),read(ep));engine.assert_parent_lease=lambda:{'pid':os.getpid(),'start_ticks':0,'request':engine.ORIGINAL,'additional_requests':[REQ],'CPU_FIXTURE_NOT_SCIENTIFIC_OWNER':True};resource_calls=[]
  def fixture_resources(s,fresh_source=False):
   resource_calls.append({'cohort':s['cohort'],'fresh_source':fresh_source});return {'physical_RAM_pass':True,'physical_disk_pass':True,'CPU_ONLY_FAKE_RESOURCE_LEDGER':True}
  engine.resources=fixture_resources
  def prior_input_proof(s):
   binding=P(s.get('input_binding_path',str(T/'control/input_bindings'/(s['input_digest']+'.json'))));assert sha(binding)==s['input_binding_sha256'];return {'status':'CPU_FIXTURE_INPUT_BINDING_SHA_MATCH_REUSES_POSTFREEZE_CURRENTSTAT_NO_REPEAT_BODY_IO','binding_sha256':sha(binding),'prior_currentstat_receipt_sha256':sha(REAL/'control/REMAINING_BUILD_PROFILE_V1.json')}
  engine.check_input=prior_input_proof;n=engine.engine();n.NATIVE=fakeN;n.read_current_authority=engine.authority;n.authority_consistent=lambda:True;n.resources=fixture_resources
  # Only the native loop's Popen attribute is replaced; Git/findmnt/storage BA
  # continue to use the real standard-library subprocess module.
  barrier=[]
  def reached(argv,**kwargs):
   intent=root/'control/qualification_ledger'/(cell+'.INTENT.json');assert intent.exists();current=read(rp)['registered_future_requests'][REQ];assert len(current['consumed'])==1 and current['remaining']==3 and current['consumed'][cell]['uuid']==read(intent)['uuid'];assert read(intent)['spec_sha256']==sha(root/'control'/(cell+'_SPEC.json'))==sha(root/'control/specs'/(cell+'.json'))
   assert argv[0]==str(root/'common-lib/ld-linux-x86-64.so.2') and str(root/'tools/bin/strace') in argv and argv[-len(spec['native_simulator_argv']):]==spec['native_simulator_argv'];assert kwargs['env']['LD_LIBRARY_PATH']==str(root/'DTC/env/lib') and kwargs['env']['DTC_AG7_GENERATION']==read(intent)['uuid'] and kwargs['env']['DTC_AG7_INPUT_SHA']==spec['original_environment']['DTC_AG7_INPUT_SHA'] and callable(kwargs['preexec_fn']) and kwargs['pass_fds'];assert read(intent)['observer_exit_race_binding']['profile']=='OBSERVER_PROC_EXIT_RACE_V1' and read(intent)['repair_execution_overlay']['request']==REQ;assert len(resource_calls)>=3;assert spec['estimated_peak_model_RAM_bytes']==read(REAL/'control/REMAINING_BUILD_PROFILE_V1.json')['per_cohort_memory'][cell]['estimated_peak_model_RAM_bytes'];assert dict(zip(kwargs['preexec_fn'].__code__.co_freevars,[x.cell_contents for x in kwargs['preexec_fn'].__closure__]))['s']['limits']['max_process_tree_rss_bytes']==spec['limits']['max_process_tree_rss_bytes']
   actual_intent=read(intent);assert actual_intent['resource_accounting_binding_R19']==n._R19_FUTURE_RESOURCE_BINDING
   # Exercise the installed exclusive callbacks on private synthetic metadata.
   # These are explicitly not model PID/launcher observations or real DONEs.
   output=P(actual_intent['output']);n.exclusive(output/'NATIVE_LAUNCH.json',{'scientific_qualification_uuid':actual_intent['uuid'],'CPU_ONLY_SYNTHETIC_BINDING_CALLBACK':True});n.exclusive(output/'NATIVE_SIMULATOR_PID_AND_MAPS.json',{'CPU_ONLY_SYNTHETIC_BINDING_CALLBACK_NO_MODEL_PID':True})
   bindings=[actual_intent['resource_accounting_binding_R19'],read(output/'NATIVE_LAUNCH.json')['resource_accounting_binding_R19'],read(output/'NATIVE_SIMULATOR_PID_AND_MAPS.json')['resource_accounting_binding_R19']];assert bindings[0]==bindings[1]==bindings[2]==n._R19_FUTURE_RESOURCE_BINDING;assert sha(intent)==read(rp)['registered_future_requests'][REQ]['consumed'][cell]['intent_sha256']
   barrier.append({'R19_resource_binding_three_callbacks_identical':True,'actual_INTENT_file_SHA_matches_consumed_row':True,'other_two_callback_snapshots_are_private_synthetic_NOT_native_observations':True,'resource_binding':bindings[0],'argv':argv,'exact_spec_alias_sha256':read(intent)['spec_sha256'],'fake_remaining':current['remaining'],'resource_calls':len(resource_calls),'storage_BA_completed_before_Popen':True,'real_Popen_or_preexec_executed':False,'production_model_PID_or_wait_status_created':False});raise ReachedPopen()
  n.subprocess=PopenProxy(subprocess,reached)
  if point.get('negative_missing_alias'):(root/'control'/(cell+'_SPEC.json')).unlink()
  try:n.run_native(cell)
  except ReachedPopen:
   assert not point.get('negative_missing_alias') and len(barrier)==1 and not list((root/'control/qualification_ledger').glob('*.DONE.json'));results.append({'cohort':cell,'validation_kind':'REMAINING_FAILED_FULL_INPUT_CORRECTNESS_NOT_FORMAL','hard_AS_RSS_bytes':spec['limits']['max_process_tree_rss_bytes'],'estimated_peak_model_RAM_bytes':spec['estimated_peak_model_RAM_bytes'],'status':'REAL_NATIVE_PRE_POPEN_BARRIER_REACHED_FAKE_LEDGER_ONLY','barrier':barrier[0]})
  except FileNotFoundError as error:
   assert point.get('negative_missing_alias') and error.filename==str(root/'control'/(cell+'_SPEC.json')) and not barrier and not list((root/'control/qualification_ledger').glob('*.INTENT.json')) and read(rp)['registered_future_requests'][REQ]['remaining']==4;negative={'status':'PASS_MISSING_ALIAS_FAILS_AT_REAL_NATIVE_LINE_BEFORE_INTENT_OR_POPEN','missing_suffix':P(error.filename).name,'fake_credit_unchanged':4}
  else:raise AssertionError('Native loop returned before Popen barrier without diagnosis')
assert len(results)==4 and negative and sha(N/'bin/native')==entry_sha and REQ not in read(N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json')['registered_future_requests']
receipt={'schema':'REMAIN4_REAL_NATIVE_PRE_POPEN_FAKE_ROOT_INTEGRATION_QUALIFICATION_V1','status':'PASS','positive_cases':results,'positive_count':4,'negative_alias_case':negative,'source_sha256':sha(source),'inherited_native_source_sha256':sha(T/'tools/sweep_native_cap1m.py'),'observer_sha256':sha(REAL.parent/'ops/observer_exit_race_v1.py'),'input_check_fixture_scope':'Private resource availability mocked in engine and installed native.resources (after validating frozen shared module/launch-binding source). Only input body/currentstat mocked after checking binding SHA and prior fixed postfreeze proof; all real model prepares retain real currentstat checks. Source/spec/runtime/auth/INTENT/global-update on fake root, actual storage native-admission and exact argv/env were executed before mockPopen marker. No Popen return value or process wait status invented.','actual_registry_mutated':False,'actual_entry_mutated':False,'actual_scientific_INTENTs_written':0,'real_model_or_component_processes_forked':0,'preexec_callbacks_executed':0,'observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()};dest=REAL/'control/REAL_NATIVE_PRE_POPEN_CPU_QUALIFICATION_V1.json';assert not dest.exists();dest.write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({'status':'PASS','positive_count':4,'negative_alias_case':negative,'receipt':str(dest),'sha256':sha(dest),'actual_models_started':0},indent=2))
