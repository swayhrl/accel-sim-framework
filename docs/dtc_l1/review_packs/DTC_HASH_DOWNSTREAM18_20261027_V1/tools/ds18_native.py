"""Finite new-contract downstream experiment; original native loop stays pinned."""
import pathlib,json,hashlib,importlib.util,os,fcntl,copy,datetime,subprocess
P=pathlib.Path;R=P('/root/data/dtc_hash_downstream18_20261027_v1');T=P('/root/data/dtc_main_v100_sweep_20261025_v1');N=P('/root/data/ep_l2_dtc_l1_native_v2');F=P('/root/data/dtc_failure_repair_20261025_v1');REQ='DTC_HASH_DOWNSTREAM18_20261027_V1';ORIG='DTC_AE_V100_FULL_SWEEP_20261025_V1';G=1024**3;M=1024**2
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def base():return load('ds18_original_native',T/'tools/sweep_native_cap1m.py')
def authority():return base().read_current_authority()
def plan():return read(R/'control/EXECUTION_PLAN.json')
def registered():
 reg,ep=authority();q=reg['registered_future_requests'][REQ];p=plan();assert q['budget']==18 and q['model_automatic_retries']==0 and q['performance_contract']=='NEW_DOWNSTREAM_MATCHED_HASH18' and q['engine_sha256']==sha(__file__) and q['execution_plan_sha256']==sha(R/'control/EXECUTION_PLAN.json') and q['spec_request_sha256']==sha(R/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json')
 assert p['build_profile_sha256']==sha(R/'control/BUILD_PROFILE.json') and p['scope_sha256']==sha(R/'control/SCOPE.json')
 for x in p['source_pins']:assert sha(x['path'])==x['sha256'],x['path']
 return reg,ep,q,p
def spec_for(c):
 reg,ep,q,p=registered();path=R/'control/specs'/(c+'.json');s=read(path);assert sha(path)==q['admitted_specs'][c]==sha(R/'control'/(c+'_SPEC.json')) and s['request']==REQ and s['cohort']==c and s['project']=='DTC'
 assert c.startswith('E2-DTCHASH18-') and s['cell']in['CH','DH'] and s['downstream_profile']in['PQ','P0','PS']and s['program']in['ATAX','MVT','BICG']and not s['correctness_validation_only']
 assert s['core_commit']=='9eedb3131937748f0492fa83aad37d3691118d70'and s['framework_commit']=='02775fd795cde5aae1480d81cee6eb481d0a08f4'and len(s['expected_options'])==270
 claim=read(R/'control/POOL_DISPATCH_RESERVATIONS.json')['claims'].get(c)
 if claim is not None:assert claim['host_cpu']==s['host_cpu'] and claim['host_cpu']in p['allowed_model_CPUs']
 return s
def assert_parent_lease():
 lease=base().assert_batch_lease();p=plan();assert lease['pid']==p['parent_pid']and lease['start_ticks']==p['parent_start_ticks']and lease['controller_sha256']==p['parent_controller_sha256']and REQ in lease.get('additional_requests',[])
 assert sha(p['parent_controller_path'])==lease['controller_sha256'];ack=read(R/'control/PARENT_ADDON_ACK.json');assert ack['parent_pid']==lease['pid']and ack['addon_sha256']==sha(R/'tools/ds18_parent_addon.py')and ack['status']=='REGISTERED_ADDON_READY_NO_START'
 return lease
def update_authority(fn):
 lock=(N/'control/science_authority/REGISTRY_UPDATE.lock').open('a+b');fcntl.flock(lock,fcntl.LOCK_EX);rp=N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json';ep=N/'control/CURRENT_SCIENCE_EPOCH.json';reg=read(rp);epoch=read(ep);assert sha(rp)==epoch['native_registry_sha256'];peers={k:copy.deepcopy(v)for k,v in reg['registered_future_requests'].items()if k!=REQ};hist=copy.deepcopy((reg['old_source_history'],reg['qualification_history']));old=(sha(rp),sha(ep));history=N/'control/science_authority/request_history'
 for p in [rp,ep]:
  dst=history/(p.stem+'.'+sha(p)+'.json')
  if not dst.exists():dst.write_bytes(p.read_bytes())
 fn(reg);assert all(reg['registered_future_requests'][k]==v for k,v in peers.items())and hist==(reg['old_source_history'],reg['qualification_history'])
 reg['new_scientific_budget_remaining']=sum(v.get('remaining',max(0,v.get('budget',0)-(v.get('consumed',0)if isinstance(v.get('consumed',0),int)else len(v.get('consumed',{})))))for v in reg['registered_future_requests'].values());tmp=rp.with_name('.DS18_REGISTRY.writing')
 with tmp.open('w')as h:json.dump(reg,h,sort_keys=True,indent=2);h.write('\n');h.flush();os.fsync(h.fileno())
 tmp.replace(rp);epoch['native_registry_sha256']=sha(rp);epoch['new_budget_remaining']=reg['new_scientific_budget_remaining'];epoch['request_revision']=dict(request_id=REQ,operation='NEW_DOWNSTREAM18_EXACT_UPDATE',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),prior_registry_sha256=old[0],prior_current_epoch_sha256=old[1]);tmp=ep.with_name('.DS18_EPOCH.writing')
 with tmp.open('w')as h:json.dump(epoch,h,sort_keys=True,indent=2);h.write('\n');h.flush();os.fsync(h.fileno())
 tmp.replace(ep)
 for folder in [rp.parent,ep.parent]:fd=os.open(folder,os.O_RDONLY);os.fsync(fd);os.close(fd)
def output_cap(s):return s['limits']['max_result_directory_bytes']
def check_input(s):
 n=base();return n.check_input(s)
def resources(s,fresh_source=False):return load('ds18_resources',R/'tools/ds18_resources.py').resources(s,fresh_source)
def binding():return dict(request=REQ,engine_sha256=sha(__file__),plan_sha256=sha(R/'control/EXECUTION_PLAN.json'),profile_sha256=sha(R/'control/BUILD_PROFILE.json'),resource_source_sha256=sha(R/'tools/ds18_resources.py'),original_native_source_sha256=sha(T/'tools/sweep_native_cap1m.py'),performance_scope='NEW_DOWNSTREAM18_ONLY_NEVER_ORIGINAL288_OR_REPAIR')
def prepare(c):
 reg,ep,q,p=registered();assert ep['epoch']==2 and ep['state']=='NATIVE_SCIENCE_ACTIVE'and ep['holder']==os.uname().nodename and q['state']in['ARMED','RUNNING']and q['remaining']>0 and c not in q['consumed'];assert_parent_lease();s=spec_for(c);host=base().identity();assert R.stat().st_dev==2128 and not(R/'control/ABORT').exists()and not(R/'control/qualification_ledger'/(c+'.INTENT.json')).exists()
 claims=read(R/'control/POOL_DISPATCH_RESERVATIONS.json')['claims'];assert c in claims and claims[c]['host_cpu']==s['host_cpu']and claims[c]['result_cap_bytes']==output_cap(s);assert len({v['host_cpu']for v in claims.values()})==len(claims)
 roots=[T,F/'validation',F/'validation_lava_memory_v2',F/'validation_late_failure_v1',F/'validation_remaining_failure_v1',F/'validation_storage_recovery12_v1']
 for root in roots:assert s['host_cpu']not in {v['host_cpu']for v in read(root/'control/POOL_DISPATCH_RESERVATIONS.json')['claims'].values()}
 for x in s['runtime_files']:assert sha(x['actual_realpath'])==x['sha256']and (R/x['target']).resolve()==P(x['actual_realpath']).resolve()
 for x in s['configs']:assert sha(x['path'])==x['sha256']
 for k in ['core','framework']:
  repo=s['source_worktrees'][k];assert subprocess.check_output(['git','-C',repo,'rev-parse','HEAD'],text=True).strip()==s[k+'_commit']and not subprocess.check_output(['git','-C',repo,'status','--porcelain'],text=True).strip()
 asset=check_input(s);sample=resources(s,True)
 if not(sample['physical_RAM_pass']and sample['physical_disk_pass']):raise RuntimeError('RESOURCE_HOLD_NO_START')
 return dict(status='DOWNSTREAM18_EXACT_PREPARE_PASS_NO_START',cohort=c,request=REQ,selected_host_cpu=s['host_cpu'],identity=host,asset=asset,resources=sample,operational_resource_profile=binding(),scientific_starts=0)
def engine():
 reg,ep,q,p=registered();n=base();n.ROOT=R;n.REQUEST=REQ;n.COHORTS={c:'DTC'for c in q['admitted_specs']};n.spec_for=spec_for;n.prepare=prepare;n.resources=resources;n.output_cap=output_cap;n.check_input=check_input;n.assert_batch_lease=assert_parent_lease;n.update_authority=update_authority
 oldchild=n.child_info
 def child(pid):
  v=oldchild(pid);v['host_cpu_affinity_actual']=sorted(os.sched_getaffinity(pid));return v
 n.child_info=child;old=n.exclusive;bind=binding()
 def exclusive(path,obj):
  path=P(path)
  if path.name.endswith('.INTENT.json')or path.name in ['NATIVE_LAUNCH.json','NATIVE_SIMULATOR_PID_AND_MAPS.json']:obj=dict(obj,downstream_execution_binding=bind)
  if path.name=='NATIVE_LAUNCH.json':
   uid=obj['scientific_qualification_uuid'];cells=[c for c,v in registered()[2]['consumed'].items()if v['uuid']==uid];assert len(cells)==1;c=cells[0]
   for name,source in [('DOWNSTREAM_FROZEN_SPEC.json',R/'control/specs'/(c+'.json')),('DOWNSTREAM_INTENT.json',R/'control/qualification_ledger'/(c+'.INTENT.json')),('DOWNSTREAM_PLAN.json',R/'control/EXECUTION_PLAN.json'),('DOWNSTREAM_REQUEST.json',R/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json'),('DOWNSTREAM_PROFILE.json',R/'control/BUILD_PROFILE.json')]:
    with(path.parent/name).open('xb')as h:h.write(source.read_bytes());h.flush();os.fsync(h.fileno())
  return old(path,obj)
 n.exclusive=exclusive;observer=p['observer_overlay'];assert sha(observer['path'])==observer['sha256'];return load('ds18_qualified_exit_observer',P(observer['path'])).install(n)
def run_native(c):return engine().finish_cell(c)
