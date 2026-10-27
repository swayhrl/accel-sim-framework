"""Independent epoch2 request, original qualified model loop and explicit resource overlays."""
import pathlib,json,hashlib,importlib.util,os,fcntl,copy,datetime,subprocess,sys,types,resource
P=pathlib.Path;R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1');T=P('/root/data/dtc_main_v100_sweep_20261025_v1');N=P('/root/data/ep_l2_dtc_l1_native_v2');REQ='DTC_L2_MLP_FULL_WORKLOAD_EXPLORATION_20261027_V1'
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def jsonsha(v):return hashlib.sha256((json.dumps(v,sort_keys=True,indent=2)+'\n').encode()).hexdigest()
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def base():return load('l2_original_native',T/'tools/sweep_native_cap1m.py')
def authority():return base().read_current_authority()
def registered():
 reg,ep=authority();q=reg['registered_future_requests'][REQ];plan=read(R/'control/EXECUTION_PLAN.json')
 assert q['request']==REQ and q['engine_sha256']==sha(__file__)and q['execution_plan_sha256']==sha(R/'control/EXECUTION_PLAN.json')
 assert q['spec_request_sha256']==sha(R/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json')and q['model_automatic_retries']==0
 assert q['budget']==len(q['admitted_specs'])and q['remaining']==q['budget']-len(q['consumed'])
 for x in plan['source_pins']:assert sha(x['path'])==x['sha256'],x['path']
 return reg,ep,q,plan
def canonical(c):
 reg,ep,q,plan=registered();p=R/'control/specs'/(c+'.json');s=read(p)
 assert q['admitted_specs'][c]==sha(p)==sha(R/'control'/(c+'_SPEC.json'))and s['cohort']==c and s['request']==REQ
 assert c.startswith('E2-DTCL2MLP-')and s['cell']in['CH','DH']and s['host_cpu']is None
 assert s['input_digest']in read(R/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json')['input_digests']
 assert s['core_commit']==read(R/'control/BUILD_PROFILE.json')['core_commit']and s['framework_commit']==read(R/'control/BUILD_PROFILE.json')['framework_commit']
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
 with(N/'control/science_authority/REGISTRY_UPDATE.lock').open('a+b')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);rp=N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json';ep=N/'control/CURRENT_SCIENCE_EPOCH.json';reg=read(rp);epoch=read(ep);assert sha(rp)==epoch['native_registry_sha256']
  peers={k:copy.deepcopy(v)for k,v in reg['registered_future_requests'].items()if k!=REQ};hist=copy.deepcopy((reg['old_source_history'],reg['qualification_history']));old=(sha(rp),sha(ep));folder=N/'control/science_authority/request_history'
  for p in [rp,ep]:
   dst=folder/(p.stem+'.'+sha(p)+'.json')
   if not dst.exists():dst.write_bytes(p.read_bytes())
  fn(reg);assert all(reg['registered_future_requests'][k]==v for k,v in peers.items())and hist==(reg['old_source_history'],reg['qualification_history'])
  reg['new_scientific_budget_remaining']=sum(v.get('remaining',max(0,v.get('budget',0)-(v.get('consumed',0)if isinstance(v.get('consumed',0),int)else len(v.get('consumed',{})))))for v in reg['registered_future_requests'].values())
  def save(p,v):
   tmp=p.with_name('.'+p.name+'.L2MLPwriting')
   with tmp.open('w')as h:json.dump(v,h,sort_keys=True,indent=2);h.write('\n');h.flush();os.fsync(h.fileno())
   tmp.replace(p)
  save(rp,reg);epoch['native_registry_sha256']=sha(rp);epoch['new_budget_remaining']=reg['new_scientific_budget_remaining'];epoch['request_revision']=dict(request_id=REQ,operation='AUTHORIZED_L2_MLP_MATRIX_UPDATE',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),prior_registry_sha256=old[0],prior_current_epoch_sha256=old[1]);save(ep,epoch)
  for d in [rp.parent,ep.parent]:fd=os.open(d,os.O_RDONLY);os.fsync(fd);os.close(fd)
def output_cap(s):return s['limits']['max_result_directory_bytes']
def check_input(s):
 n=base();n.ROOT=R;return n.check_input(s)
def resources(s,fresh_source=False):return load('l2_resources_runtime',R/'tools/l2_resources.py').resources(s,fresh_source)
def binding():
 return dict(request=REQ,engine_sha256=sha(__file__),plan_sha256=sha(R/'control/EXECUTION_PLAN.json'),profile_sha256=sha(R/'control/BUILD_PROFILE.json'),resource_source_sha256=sha(R/'tools/l2_resources.py'),original_native_source_sha256=sha(T/'tools/sweep_native_cap1m.py'),performance_scope='NEW_L2_MLP_ONLY_NEVER_ORIGINAL_OR_REPAIR',resource_contract='dynamic CPU dispatch,RSS and AS separated;pressure pauses only admission',authorization_contract='immutable explicit factor-family authorization plus current exact registry one-start grants')
def prepare(c):
 reg,ep,q,plan=registered();assert ep['epoch']==2 and ep['state']=='NATIVE_SCIENCE_ACTIVE'and ep['holder']==os.uname().nodename
 assert q['state']in['ARMED','RUNNING']and q['remaining']>0 and c not in q['consumed'];assert_parent_lease();s=spec_for(c)
 assert R.stat().st_dev==2128 and not(R/'control/ABORT').exists()and not(R/'control/qualification_ledger'/(c+'.INTENT.json')).exists()
 claims=read(R/'control/POOL_DISPATCH_RESERVATIONS.json')['claims'];assert c in claims and claims[c]['host_cpu']==s['host_cpu']and len({v['host_cpu']for v in claims.values()})==len(claims)
 assert s['host_cpu']in os.sched_getaffinity(0)and s['limits']['max_process_tree_vms_bytes']>=s['limits']['max_process_tree_rss_bytes']
 for x in s['runtime_files']:assert (R/x['target']).resolve()==P(x['actual_realpath']).resolve()and sha(x['actual_realpath'])==x['sha256']
 for x in s['configs']:assert sha(x['path'])==x['sha256']
 for k in ['core','framework']:
  repo=s['source_worktrees'][k];assert subprocess.check_output(['git','-C',repo,'rev-parse','HEAD'],text=True).strip()==s[k+'_commit'];assert not subprocess.check_output(['git','-C',repo,'status','--porcelain'],text=True).strip()
 asset=check_input(s);sample=resources(s,True)
 if not(sample['physical_RAM_pass']and sample['physical_disk_pass']):raise RuntimeError('RESOURCE_HOLD_NO_START')
 return dict(status='L2MLP_PREPARE_PASS_NO_START',cohort=c,request=REQ,selected_host_cpu=s['host_cpu'],identity=base().identity(),asset=asset,resources=sample,operational_resource_profile=binding(),scientific_starts=0)
class ResourceOverlay:
 """A per-module proxy: never changes Python's shared resource module."""
 def __getattr__(self,k):return getattr(resource,k)
 def setrlimit(self,kind,pair):
  if kind==resource.RLIMIT_AS:
   s=sys._getframe(1).f_locals['s'];limit=s['limits']['max_process_tree_vms_bytes'];assert limit>=s['limits']['max_process_tree_rss_bytes']>0;pair=(limit,limit)
  return resource.setrlimit(kind,pair)
def engine():
 reg,ep,q,plan=registered();n=base();n.ROOT=R;n.REQUEST=REQ;n.COHORTS={c:'DTC'for c in q['admitted_specs']};n.spec_for=spec_for;n.prepare=prepare;n.resources=resources;n.output_cap=output_cap;n.check_input=check_input;n.assert_batch_lease=assert_parent_lease;n.update_authority=update_authority;n.resource=ResourceOverlay()
 # Only this new frontend process imports the proxy. Existing controller/worker
 # module dictionaries and source files are never changed.
 original_guard=load('l2_original_storage_guard',T/'tools/sweep_storage_guard.py');proxy=types.ModuleType('sweep_storage_guard');proxy.__dict__.update(original_guard.__dict__)
 def native_admission(path):
  assert P(path).resolve()==(R/'DTC/run').resolve();b=base().identity();assert b['native_device']==2128
  v=resources({'cohort':'L2_MLP_ADMISSION_ALREADY_CLAIMED'},False)
  return dict(status='PASS'if v['physical_RAM_pass']and v['physical_disk_pass']else'HOLD',resource_contract=binding(),resources=v,old_namespace_guard_preserved=True)
 proxy.native_admission=native_admission;sys.modules['sweep_storage_guard']=proxy
 original_read=n.read
 def qualified_read(path):
  v=original_read(path)
  if P(path)==R/'control/SCIENCE_AUTHORIZATION.json':
   assert v['factor_family_grants_resolve_from_current_registry']is True
   current=registered()[2];v=dict(v,budgets={c:1 for c in current['admitted_specs']})
  return v
 n.read=qualified_read
 oldchild=n.child_info
 def child(pid):
  v=oldchild(pid);v['host_cpu_affinity_actual']=sorted(os.sched_getaffinity(pid));v['actual_process_limits_text']=(P('/proc')/str(pid)/'limits').read_text();return v
 n.child_info=child;old=n.exclusive;bind=binding()
 def exclusive(path,obj):
  path=P(path)
  if path.name.endswith('.INTENT.json')or path.name in ['NATIVE_LAUNCH.json','NATIVE_SIMULATOR_PID_AND_MAPS.json']:
   c=obj.get('cohort')
   if c is None:
    if path.name=='NATIVE_LAUNCH.json':uid=obj['scientific_qualification_uuid']
    else:uid=read(path.parent/'NATIVE_LAUNCH.json')['scientific_qualification_uuid']
    c=next(c for c,row in registered()[2]['consumed'].items()if row['uuid']==uid)
   db=R/'control/dispatch_bindings'/(c+'.json');obj=dict(obj,l2_mlp_execution_binding=bind,dispatch_binding_sha256=sha(db))
   if path.name=='NATIVE_LAUNCH.json':
    obj['effective_RLIMIT_AS_bytes']=spec_for(c)['limits']['max_process_tree_vms_bytes']
    for name,src in [('DOWNSTREAM_FROZEN_SPEC.json',R/'control/specs'/(c+'.json')),('DISPATCH_BINDING.json',db),('DOWNSTREAM_INTENT.json',R/'control/qualification_ledger'/(c+'.INTENT.json')),('DOWNSTREAM_PLAN.json',R/'control/EXECUTION_PLAN.json'),('DOWNSTREAM_REQUEST.json',R/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json'),('DOWNSTREAM_PROFILE.json',R/'control/BUILD_PROFILE.json')]:
     with(path.parent/name).open('xb')as h:h.write(src.read_bytes());h.flush();os.fsync(h.fileno())
  return old(path,obj)
 n.exclusive=exclusive;obs=plan['observer_overlay'];assert sha(obs['path'])==obs['sha256'];return load('l2_qualified_exit_observer',obs['path']).install(n)
def run_native(c):return engine().finish_cell(c)
