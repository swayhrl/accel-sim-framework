import pathlib,json,importlib.util,os,sys,copy,threading,datetime,hashlib,traceback
P=pathlib.Path;ROOT=P('/root/data/dtc_l2_mlp_exploration_20261027_v1');MARKER='DTC_INCIDENT11_RECOVERY_REGISTER_ONLY_V1'
read=lambda p:json.loads(P(p).read_bytes());sha=lambda p:hashlib.sha256(P(p).read_bytes()).hexdigest()
def put(p,v):
 with P(p).open('x')as f:json.dump(v,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def apply(directory):
 d=P(directory);assert threading.current_thread()is threading.main_thread()
 assert os.getpid()==1498278 and int(P('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19])==977758783
 main=sys.modules['__main__'];assert not hasattr(main,MARKER),'Observe/reconcile existing transaction; never requeue blindly'
 cfg=read(d/'CONFIGURATION.json');assert sha(d/'CONFIGURATION.json')=='79f788502efde5e8d791acf5470be1a5c9ba018b9d519e9121ea67db2507ef02'
 assert sha(d/'incident_registry.py')==cfg['source_sha256']=='9979d791175cd3c7545efa5fec9e89ef2c3278db4bcd4769ab149cdc6b8ec22a'
 frame=main.DTC_FUTURE_MEMORY_PRIMARY_SCOPE_SYNC_V1.frame;engine=frame.f_locals['engine'];engine.assert_parent_lease()
 sp=importlib.util.spec_from_file_location('actual_IR11_registry_main',d/'incident_registry.py');module=importlib.util.module_from_spec(sp);sp.loader.exec_module(module)
 state=dict(source_sha256=sha(module.__file__),phase='REGISTER_ONLY_PREPARING',frame=frame,module=module,store=None);setattr(main,MARKER,state)
 try:
  aging=frame.f_locals['res'].DTC_LARGE_JOB_AGING_INSTALLED
  with aging.lock:
   before=engine.registered()[2];matrixsha=sha(ROOT/'control/MATRIX_CURRENT.json');scopesha=sha(ROOT/'control/SCOPE.json')
   memory=main.DTC_FUTURE_MEMORY_ADMISSION_095_FLOOR10_V1;memorysha=sha(ROOT/'control/operational_amendments/future_memory_admission_v1/ACTIVE_MEMORY.json');memorycfg=copy.deepcopy(memory['context']['cfg'])
   refs=(frame.f_globals['read'],frame.f_globals['worker'],frame.f_globals['safe'],frame.f_locals['res'].choose_dispatch,frame.f_locals['consumer'].safe_finish,frame.f_locals['adaptive'].recommend)
   store=module.IncidentRecoveryRegistry(ROOT,engine,frame,cfg);state['store']=store
   authorization=store.expected_authorization();put(d/'MAIN_AUTHORIZATION.json',authorization)
   prepared=store.prepare(authorization);put(d/'PREPARED_RECEIPT.json',prepared)
   registered=store.register(authorization);state['registration']=registered
   after=engine.registered()[2];assert after['budget']==before['budget']+11 and after['remaining']==after['budget']-len(after['consumed'])
   cohorts=set(registered['cohorts']);assert len(cohorts)==11 and not(cohorts&set(after['consumed']))
   assert not(cohorts&set(memorycfg['allowed_cohorts']))and memory['context']['cfg']==memorycfg
   assert sha(ROOT/'control/MATRIX_CURRENT.json')==matrixsha and sha(ROOT/'control/SCOPE.json')==scopesha
   assert sha(ROOT/'control/operational_amendments/future_memory_admission_v1/ACTIVE_MEMORY.json')==memorysha
   assert refs==(frame.f_globals['read'],frame.f_globals['worker'],frame.f_globals['safe'],frame.f_locals['res'].choose_dispatch,frame.f_locals['consumer'].safe_finish,frame.f_locals['adaptive'].recommend)
   current_view=frame.f_globals['read'](ROOT/'control/MATRIX_CURRENT.json');assert not(cohorts&{p['cohort']for p in current_view['points']})
   for c,row in before['consumed'].items():
    assert all(after['consumed'][c].get(k)==v for k,v in row.items())and set(after['consumed'][c])-set(row)<= {'execution_receipt'}
   state['phase']='REGISTERED_INDEPENDENT_IR11_NO_RUNTIME_ACTIVATION'
   ack=dict(schema='MAIN_IR11_ACTUAL_REGISTER_ONLY_ACK_V1',UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),status=state['phase'],owner_pid=os.getpid(),owner_start_ticks=977758783,budget_before=before['budget'],budget_after=after['budget'],new_grants=11,refunds=0,cohorts=sorted(cohorts),consumed_new_trials=0,
    registration=registered,matrix_sha256=matrixsha,scope_sha256=scopesha,active_memory_sha256=memorysha,memory_allowed_count=len(memorycfg['allowed_cohorts']),actual_runtime_view_points=len(current_view['points']),source_sha256=sha(module.__file__),configuration_sha256=sha(d/'CONFIGURATION.json'),
    runtime_or_consumer_or_selector_or_CPU_policy_changed=False,original_failures_replaced=False,primary_statistics_excluded=True,validated_union_authorized=False,models_started_by_callback=0,old_consumed_UUIDs_preserved=True,
    next_required='Engineering4 real qualification, explicit IR runtime and memory eligibility; new trial performance remains separately reported until statistical disposition.')
   put(d/'ACK.json',ack);return ack
 except BaseException:
  error=traceback.format_exc()
  try:
   actual=engine.registered()[2];observed=dict(status='ACTUAL_AUTHORITY',IR11_records=len(actual.get('authorized_incident_recovery_trials',[])),IR11_consumed=[r['cohort']for r in actual.get('authorized_incident_recovery_trials',[])if r['cohort']in actual['consumed']])
  except BaseException as e:observed=dict(status='UNKNOWN_PRESERVE_PREPARED_NO_REFUND',error=repr(e))
  state.update(phase='REGISTER_ONLY_ENGINEERING_HOLD',error=error);put(d/'ERROR.json',dict(traceback=error,authority=observed,automatic_requeue=False,refunds=0,runtime_unchanged=True))
  raise
