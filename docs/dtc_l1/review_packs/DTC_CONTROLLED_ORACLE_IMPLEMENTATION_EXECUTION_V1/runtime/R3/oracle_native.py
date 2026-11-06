import types
"""Independent epoch2 request, original qualified model loop and explicit resource overlays."""
import pathlib,json,hashlib,importlib.util,os,fcntl,copy,datetime,subprocess,sys,types,resource,time
P=pathlib.Path;R=P(__file__).resolve().parents[1];T=P('/root/data/dtc_main_v100_sweep_20261025_v1');N=P('/root/data/ep_l2_dtc_l1_native_v2');REQ=json.loads((R/'control/EXECUTION_PLAN.json').read_bytes())['request'] if (R/'control/EXECUTION_PLAN.json').exists() else None
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def jsonsha(v):return hashlib.sha256((json.dumps(v,sort_keys=True,indent=2)+'\n').encode()).hexdigest()
def load(n,p):
 m=types.ModuleType(n);m.__file__=str(p);exec(compile(P(p).read_bytes(),str(p),'exec'),m.__dict__);return m
def base():return load('l2_original_native',T/'tools/sweep_native_cap1m.py')
def authority():
 # New admission/control reads have a bounded wait. Never call this inside the
 # REGISTRY_UPDATE EX mutator; all lock-held checks consume its passed snapshot.
 with (N/'control/science_authority/REGISTRY_UPDATE.lock').open('rb')as lock:
  deadline=time.monotonic()+2.0
  while True:
   try:fcntl.flock(lock,fcntl.LOCK_SH|fcntl.LOCK_NB);break
   except BlockingIOError:
    if time.monotonic()>=deadline:raise RuntimeError('REGISTRY_SHARED_LOCK_BUSY_ADMISSION_HOLD_NO_START')
    time.sleep(.02)
  rp=N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json';ep=N/'control/CURRENT_SCIENCE_EPOCH.json';reg=read(rp);epoch=read(ep);assert sha(rp)==epoch['native_registry_sha256'];return reg,epoch
def registered():
 reg,ep=authority();plan=read(R/'control/EXECUTION_PLAN.json');assert REQ==plan['request'];q=reg['registered_future_requests'][REQ]
 assert q['request']==REQ and q['engine_sha256']==sha(__file__) and q['execution_plan_sha256']==sha(R/'control/EXECUTION_PLAN.json')
 assert q['spec_request_sha256']==sha(R/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json') and q['model_automatic_retries']==0
 assert q['budget']==len(q['admitted_specs'])==plan['expected_new_starts'] and q['remaining']==q['budget']-len(q['consumed'])
 for x in plan['source_pins']:assert sha(x['path'])==x['sha256'],x['path']
 assert set(q['admitted_specs'])=={p['cohort']for p in read(R/'control/MATRIX.fixed.json')['points']}
 resource_module().verify_frozen_release(plan,q);verify_launcher_layout(plan)
 return reg,ep,q,plan
def canonical(c):
 reg,ep,q,plan=registered();assert c in q['admitted_specs'],'EXACT_REGISTERED_ORACLE_ROW_REQUIRED';p=R/'control/specs'/(c+'.json');s=read(p)
 assert q['admitted_specs'][c]==sha(p)==sha(R/'control'/(c+'_SPEC.json')) and s['cohort']==c and s['request']==REQ
 assert c.startswith('E2-DTCORACLE-') and s['cell']=='DH' and s['downstream_profile']=='P0' and s['host_cpu'] is None
 adapter=load('oracle_spec_contract',R/'tools/oracle_population.py');adapter.validate_spec(s)
 row=next(x for x in read(R/'control/MATRIX.fixed.json')['points']if x['cohort']==c)
 assert row['program']==s['program'] and row['input_digest']==s['input_digest'] and row['mode']==s['oracle_mode'] and row['plan_id']==s['plan_id']
 assert s['input_digest'] in read(R/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json')['input_digests']
 build=read(R/'control/BUILD_PROFILE.json');assert s['core_commit']==build['core_commit'] and s['framework_commit']==build['framework_commit']
 assert s['binary_sha256']==build['binary_sha256'];verify_launcher_layout(plan,s)
 return s
def spec_for(c):
 s=canonical(c);p=R/'control/dispatch_bindings'/(c+'.json');b=read(p)
 assert b['cohort']==c and b['canonical_spec_sha256']==sha(R/'control/specs'/(c+'.json'))and type(b['host_cpu'])is int
 s['host_cpu']=b['host_cpu'];assert b['resolved_spec_sha256']==jsonsha(s)
 return s
def assert_parent_lease():
 lease=base().assert_batch_lease();plan=read(R/'control/EXECUTION_PLAN.json')
 assert lease['pid']==plan['parent_pid']and lease['start_ticks']==plan['parent_start_ticks']and REQ in lease.get('additional_requests',[])
 assert lease['controller_sha256']==plan['parent_controller_sha256']==sha(plan['parent_controller_path'])
 return lease
def update_authority(fn):
 # This is the only mutating registry interface. Callback callgraph must use
 # passed current only: no registered(), canonical(), authority(), resources().
 with (N/'control/science_authority/REGISTRY_UPDATE.lock').open('a+b') as lock:
  deadline=time.monotonic()+2.0
  while True:
   try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);break
   except BlockingIOError:
    if time.monotonic()>=deadline:raise RuntimeError('REGISTRY_EX_BUSY_HOLD_NO_MUTATION')
    time.sleep(.02)
  rp=N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json';ep=N/'control/CURRENT_SCIENCE_EPOCH.json'
  reg=read(rp);epoch=read(ep);assert sha(rp)==epoch['native_registry_sha256'] and epoch['epoch']==2
  peers={k:copy.deepcopy(v)for k,v in reg['registered_future_requests'].items()if k!=REQ};hist=copy.deepcopy({k:v for k,v in reg.items()if k not in ['registered_future_requests','new_scientific_budget_remaining']});old=(sha(rp),sha(ep))
  own_before=copy.deepcopy(reg['registered_future_requests'].get(REQ));folder=rp.parent/'request_history';folder.mkdir(exist_ok=True)
  for p in [rp,ep]:
   dst=folder/(p.stem+'.'+sha(p)+'.json')
   if not dst.exists():dst.write_bytes(p.read_bytes())
  fn(reg)
  assert all(reg['registered_future_requests'][k]==v for k,v in peers.items())
  assert set(reg['registered_future_requests'])==set(peers)|{REQ}
  assert hist=={k:v for k,v in reg.items()if k not in ['registered_future_requests','new_scientific_budget_remaining']}
  own=reg['registered_future_requests'][REQ];assert own['remaining']==own['budget']-len(own['consumed'])
  if own_before is not None:
   assert own['budget']==own_before['budget'] and own['admitted_specs']==own_before['admitted_specs'] and set(own_before['consumed'])<=set(own['consumed'])
   for c,row in own_before['consumed'].items():assert all(own['consumed'][c].get(k)==v for k,v in row.items())
  reg['new_scientific_budget_remaining']=sum(v.get('remaining',max(0,v.get('budget',0)-(v.get('consumed',0)if isinstance(v.get('consumed',0),int)else len(v.get('consumed',{})))))for v in reg['registered_future_requests'].values())
  def save(p,v):
   tmp=p.with_name('.'+p.name+'.ORACLE.'+str(os.getpid())+'.writing')
   with tmp.open('w')as h:json.dump(v,h,sort_keys=True,indent=2);h.write('\n');h.flush();os.fsync(h.fileno())
   tmp.replace(p)
  save(rp,reg);epoch['native_registry_sha256']=sha(rp);epoch['new_budget_remaining']=reg['new_scientific_budget_remaining']
  epoch['request_revision']=dict(request_id=REQ,operation='AUTHORIZED_CONTROLLED_ORACLE_STATE_UPDATE',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),prior_registry_sha256=old[0],prior_current_epoch_sha256=old[1]);save(ep,epoch)
  for d in [rp.parent,ep.parent]:fd=os.open(d,os.O_RDONLY);os.fsync(fd);os.close(fd)
def output_cap(s):return s['limits']['max_result_directory_bytes']
def check_input(s):
 n=base();n.ROOT=R;n.read_current_authority=authority;return n.check_input(s)
_RESOURCES_MODULE=None
def resource_module():
 global _RESOURCES_MODULE
 if _RESOURCES_MODULE is None:_RESOURCES_MODULE=load('oracle_resources_private_process',R/'tools/oracle_resources.py')
 return _RESOURCES_MODULE
def resources(s,fresh_source=False):return resource_module().resources(s,fresh_source)
def admission_hold(q,s):return resource_module().admission_hold(q,s)
def verify_direction_release(plan,q):return resource_module().verify_frozen_release(plan,q)
def verify_initial_runtime_gate(plan,cohort,q):return resource_module().verify_initial_runtime_gate(plan,cohort,q=q)
def verify_launcher_layout(plan,s=None):
 ref=plan['launcher_layout'];assert sha(ref['path'])==ref['sha256'];v=read(ref['path'])
 assert v['status']=='PASS' and v['request']==REQ and v['scientific_models_started']==v['scientific_UUIDs_allocated']==0 and v['final_binary_layout_qualified'] is True
 assert len(v['CPU_probes'])==plan['expected_new_starts'] and {r['cohort']for r in v['CPU_probes']}==set(plan['authorized_cohorts'])
 if s is not None:assert s['host_launcher_layout']==ref
 for row in v['files']:assert sha(row['path'])==row['sha256']
 for row in v['CPU_probes']:assert sha(row['receipt_path'])==row['receipt_sha256'] and sha(row['trace_path'])==row['trace_sha256']
 return dict(launcher_layout=ref,CPU_only_proof=True,actual_model_qualification_still_required=True)

def binding():
 reg,ep,q,plan=registered()
 return dict(request=REQ,engine_sha256=sha(__file__),plan_sha256=sha(R/'control/EXECUTION_PLAN.json'),profile_sha256=sha(R/'control/BUILD_PROFILE.json'),resource_source_sha256=sha(R/'tools/oracle_resources.py'),original_native_source_sha256=sha(T/'tools/sweep_native_cap1m.py'),performance_scope='CONTROLLED_ORACLE_DH_COUNTERFACTUAL_NOT_IMPLEMENTED_ARCHITECTURE',approved_contract_commit='18b1ee9d339902e555fc2e04ef51c84f77dfe1b1',project_authority_sha256=sha(R/'control/PROJECT_AUTHORITY.fixed.json'),launcher_layout=plan['launcher_layout'],runtime_guard_sha256=sha(R/'tools/oracle_guard.py'),runtime_guard_policy_sha256=sha(R/'tools/oracle_guard_policy.py'),authorization_contract='fixed matrix and same-build OFF, no CH or hidden canary, no reset/refund/model retry')
def prepare(c):
 reg,ep,q,plan=registered();assert os.environ.get('DTC_CONTROLLED_ORACLE_NATIVE_ENTRY')=='1','NATIVE_EPOCH2_EXACT_ROUTE_REQUIRED';assert ep['epoch']==2 and ep['state']=='NATIVE_SCIENCE_ACTIVE'and ep['holder']==os.uname().nodename
 assert q['state']in['ARMED','RUNNING']and q['remaining']>0 and c not in q['consumed'];assert_parent_lease();s=spec_for(c);assert admission_hold(q,s)is None,'TYPED_SAFETY_ADMISSION_HOLD_NO_START';verify_initial_runtime_gate(plan,c,q)
 assert R.stat().st_dev==2128 and not(R/'control/ABORT').exists()and not(R/'control/qualification_ledger'/(c+'.INTENT.json')).exists()
 claims=read(R/'control/POOL_DISPATCH_RESERVATIONS.json')['claims'];assert c in claims and claims[c]['host_cpu']==s['host_cpu']and len({v['host_cpu']for v in claims.values()})==len(claims)
 assert s['host_cpu']in os.sched_getaffinity(0)and s['limits']['max_process_tree_vms_bytes']>=s['limits']['max_process_tree_rss_bytes']
 for x in s['runtime_files']:assert (R/x['target']).resolve()==P(x['actual_realpath']).resolve()and sha(x['actual_realpath'])==x['sha256']
 for x in s['configs']:assert sha(x['path'])==x['sha256']
 for k in ['core','framework']:
  repo=s['source_worktrees'][k];assert subprocess.check_output(['git','-c','safe.directory='+repo,'-C',repo,'rev-parse','HEAD'],text=True).strip()==s[k+'_commit'];assert not subprocess.check_output(['git','-c','safe.directory='+repo,'-C',repo,'status','--porcelain'],text=True).strip()
 asset=check_input(s);sample=resources(s,True)
 if not(sample['physical_RAM_pass']and sample['physical_disk_pass']and sample.get('admission_disk_pass',False)and sample.get('admission_pressure_pass',False)):raise RuntimeError('RESOURCE_HOLD_NO_START')
 return dict(status='CONTROLLED_ORACLE_PREPARE_PASS_NO_START',cohort=c,request=REQ,selected_host_cpu=s['host_cpu'],identity=base().identity(),asset=asset,resources=sample,operational_resource_profile=binding(),scientific_starts=0)
def guard_model_mutation(current,cohort,mutator):
 # The registry lock is already held by update_authority. Check before the old
 # consume mutator writes INTENT, closing the prepare-to-consume HOLD race.
 own=current['registered_future_requests'][REQ]
 if cohort not in own['consumed']:
  assert own['state']in['ARMED','RUNNING']and cohort in own['admitted_specs'],'EXACT_ORACLE_UNCONSUMED_COHORT_REQUIRED'
  # Already under REGISTRY_UPDATE LOCK_EX: do not call registered/spec_for or
  # any authority reader here. Bind the immutable canonical spec to this exact
  # in-memory locked request snapshot, then apply the pure typed-HOLD helper.
  canonical=R/'control/specs'/(cohort+'.json')
  assert sha(canonical)==own['admitted_specs'][cohort]==sha(R/'control'/(cohort+'_SPEC.json')),'LOCKED_CANONICAL_SPEC_SHA_REQUIRED'
  spec=read(canonical);assert spec['request']==REQ and spec['cohort']==cohort and spec['host_cpu']is None,'LOCKED_CANONICAL_IDENTITY_REQUIRED'
  assert admission_hold(own,spec)is None,'TYPED_SAFETY_ADMISSION_HOLD_NO_CONSUME'
  verify_initial_runtime_gate(read(R/'control/EXECUTION_PLAN.json'),cohort,own)
 return mutator(current)
class ResourceOverlay:
 """A per-module proxy: never changes Python's shared resource module."""
 def __getattr__(self,k):return getattr(resource,k)
 def setrlimit(self,kind,pair):
  if kind==resource.RLIMIT_AS:
   s=sys._getframe(1).f_locals['s'];limit=s['limits']['max_process_tree_vms_bytes'];assert limit>=s['limits']['max_process_tree_rss_bytes']>0;pair=(limit,limit)
  return resource.setrlimit(kind,pair)
def engine(c):
 reg,ep,q,plan=registered();assert os.getpid()!=plan['parent_pid'],'MODEL_ENGINE_PRIVATE_FRONTEND_PROCESS_ONLY';identity_spec=spec_for(c);launcher_state={};n=base();n.ROOT=R;n.read_current_authority=authority;n.REQUEST=REQ;n.COHORTS={c:'DTC'for c in q['admitted_specs']};n.spec_for=spec_for;n.prepare=prepare;n.resources=resources;n.output_cap=output_cap;n.check_input=check_input;n.assert_batch_lease=assert_parent_lease;n.update_authority=lambda fn:update_authority(lambda current:guard_model_mutation(current,c,fn));n.resource=ResourceOverlay()
 # Only this new frontend process imports the proxy. Existing controller/worker
 # module dictionaries and source files are never changed.
 original_guard=load('l2_original_storage_guard',T/'tools/sweep_storage_guard.py');proxy=types.ModuleType('sweep_storage_guard');proxy.__dict__.update(original_guard.__dict__)
 def native_admission(path):
  assert P(path).resolve()==(R/'DTC/run').resolve();b=base().identity();assert b['native_device']==2128
  v=resources(spec_for(c),True)
  return dict(status='PASS'if v['physical_RAM_pass']and v['physical_disk_pass']and v.get('admission_disk_pass',False)and v.get('admission_pressure_pass',False)else'HOLD',resource_contract=binding(),resources=v,old_namespace_guard_preserved=True)
 proxy.native_admission=native_admission;sys.modules['sweep_storage_guard']=proxy
 original_read=n.read
 def qualified_read(path):
  v=original_read(path)
  if P(path)==R/'control/SCIENCE_AUTHORIZATION.json':
   current=registered()[2];assert len(v['budgets'])==len(current['admitted_specs']) and set(v['budgets'])==set(current['admitted_specs'])and all(x==1 for x in v['budgets'].values()),'EXACT_ORACLE_AUTHORIZATION_ONLY'
  return v
 n.read=qualified_read
 oldchild=n.child_info
 def child(pid):
  v=oldchild(pid);v['host_cpu_affinity_actual']=sorted(os.sched_getaffinity(pid));v['actual_process_limits_text']=(P('/proc')/str(pid)/'limits').read_text()
  cudart=next(x['actual_realpath']for x in identity_spec['runtime_files']if x['sha256']==read(R/'control/BUILD_PROFILE.json')['libcudart_sha256'])
  loader=str((R/'common-lib/ld-linux-x86-64.so.2').resolve())
  if launcher_state and all(x in v['maps']for x in [identity_spec['native_simulator_argv'][0],cudart,loader]):
   target=launcher_state['output']/'NATIVE_SIMULATOR_VERIFIED_LATE_MAPS.json'
   if not target.exists():
    snap=dict(v,cohort=c,uuid=launcher_state['uuid'],input=identity_spec['original_environment']['DTC_AG7_INPUT_SHA'],roi=identity_spec['original_environment']['DTC_AG7_ROI_SHA'],identity_tag_source='frozen_expected_tags;authenticated_progress_independently_joined',oracle_execution_binding=bind,snapshot_source='ACTUAL_CHILD_INFO_PROC_READ_NO_EXTRA_POLL_OR_AUTHORITY')
    try:
     with target.open('x')as f:json.dump(snap,f,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    except FileExistsError:pass
  return v
 n.child_info=child;old=n.exclusive;bind=binding()
 def exclusive(path,obj):
  path=P(path)
  if path.name.endswith('.INTENT.json')or path.name in ['NATIVE_LAUNCH.json','NATIVE_SIMULATOR_PID_AND_MAPS.json']:
   c=obj.get('cohort')
   if c is None:
    if path.name=='NATIVE_LAUNCH.json':uid=obj['scientific_qualification_uuid']
    else:uid=read(path.parent/'NATIVE_LAUNCH.json')['scientific_qualification_uuid']
    c=next(c for c,row in registered()[2]['consumed'].items()if row['uuid']==uid)
   db=R/'control/dispatch_bindings'/(c+'.json');obj=dict(obj,oracle_execution_binding=bind,dispatch_binding_sha256=sha(db))
   if path.name=='NATIVE_LAUNCH.json':
    obj['effective_RLIMIT_AS_bytes']=spec_for(c)['limits']['max_process_tree_vms_bytes']
    for name,src in [('DOWNSTREAM_FROZEN_SPEC.json',R/'control/specs'/(c+'.json')),('DISPATCH_BINDING.json',db),('DOWNSTREAM_INTENT.json',R/'control/qualification_ledger'/(c+'.INTENT.json')),('DOWNSTREAM_PLAN.json',R/'control/EXECUTION_PLAN.json'),('DOWNSTREAM_REQUEST.json',R/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json'),('DOWNSTREAM_PROFILE.json',R/'control/BUILD_PROFILE.json')]:
     with(path.parent/name).open('xb')as h:h.write(src.read_bytes());h.flush();os.fsync(h.fileno())
  result=old(path,obj)
  if path.name=='NATIVE_LAUNCH.json':launcher_state.update(output=path.parent,uuid=obj['scientific_qualification_uuid'])
  return result
 n.exclusive=exclusive;guard=R/'tools/oracle_guard.py';assert sha(guard)==plan['runtime_guard']['sha256'];sys.modules['sweep_guard_cap1m']=load('oracle_exact_guard_private',guard);obs=plan['observer_overlay'];assert sha(obs['path'])==obs['sha256'];return load('l2_qualified_exit_observer',obs['path']).install(n)
def run_native(c):return engine(c).finish_cell(c)
