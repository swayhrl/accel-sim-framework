import pathlib,sys,hashlib,json,time,shutil
_p=pathlib.Path(__file__).with_name('ordinary33_common_v1.py');_b=_p.read_bytes()
if hashlib.sha256(_b).hexdigest()!='673152596e7afb688925679b68ad7247c59231064c7ea2e207e8fe6d6a52ef55':raise RuntimeError('COMMON_PIN')
C=type(sys)('o33common');C.__file__=str(_p);exec(compile(_b,str(_p),'exec'),C.__dict__)
G=C.G;need=C.need;readref=C.readref;pinned_module=C.rawmodule;digest=C.sha;save=C.save
def native_light_verdict(old,v,policy):
 need(v['unknown_active_cohort_count']==0,'UNKNOWN_FOREIGN')
 need(old['host_MemAvailable']>=policy['host_floor_bytes'],'NATIVE_HOST67G_FLOOR')
 for r in old['rows']:
  need(r['effective_headroom'] is None or r['effective_headroom']>=policy['cgroup_floor_bytes'],'NATIVE_CGROUP51G_FLOOR')
  need(r['pressure_full_avg10']<=5 and r['pressure_some_avg10']<=20,'NATIVE_PSI')
  need(all(r['events_delta'].get(k,0)==0 for k in ['high','max','oom','oom_kill','oom_group_kill']),'NATIVE_OOM_EVENT')
 for r in v['current_RAM_planning_rows']:
  cap=(r.get('local_registered_SPEC_planning_proof')or{}).get('max_process_tree_rss_bytes')
  if cap is None:cap=r['registered_memory_fields'].get('max_process_tree_rss_bytes')
  if cap is None:cap=r['actual_RLIMIT_AS_bytes']
  need(type(cap)is int and cap>0 and r['actual_current_tree_Rss_bytes']<=cap,'REGISTERED_FOREIGN_CURRENT_TREE_OVER_CAP')
 return dict(schema='SC_EXACT61_NATIVE_LIGHT_BRIDGE_VERDICT_V1',status='PASS',role=policy['role'],own_control_bytes=2*G,host_MemAvailable=old['host_MemAvailable'],cgroup_min_headroom=min((r['effective_headroom']for r in old['rows']if r['effective_headroom']is not None),default=None),original_R4_full_aggregate_status=old['status'],original_R4_foreign_additional_bytes=v['additional_active_RAM_commitments_bytes'],foreign_forecasts_fully_disclosed_control_role_uses_physical_floor_policy=True,Native_CPU_POST_allowed=False,remote_heavy_POST_gate_bypassed=False,current_foreign_rows_checked=len(v['current_RAM_planning_rows']))
def native_gate(a,root):
 # Native2GiB is ONLY this control tree. Heavy POST uses the independent109 10GiB+32GiB gate.
 r=a['native_resource_code_manifest_ref'];need(r['sha256']=='952f859b6818109d8fe4b83f4f3a8ffc3eddfe54f792b257c88010beb473b8ee','FROZEN_R4_MF');mf=readref(r);base=pathlib.Path(r['path']).parent
 for n,v in mf['files'].items():need((base/n).stat().st_size==v['bytes']and digest(base/n)==v['sha256'],'NATIVE_OBSERVER_MF_PIN')
 old=list(sys.path);sys.path.insert(0,str(base));previous_helpers={}
 helpers=['hash18_registered_spec_planning_v1','dtc_l2_mlp_registered_spec_planning_v1','dtc_recovery12_registered_r20_spec_planning_v1']
 for name in helpers:
  previous_helpers[name]=sys.modules.get(name);sys.modules[name]=pinned_module(base/(name+'.py'),mf['files'][name+'.py']['sha256'],name)
 try:
  o=pinned_module(base/'current_foreign_observer_v1.py',mf['files']['current_foreign_observer_v1.py']['sha256'],'SC61_foreign')
  def raw_existing(name,path):
   need(path==o.V/'resources.py','ONLY_PINNED_EXISTING_RESOURCE_MODULE');return pinned_module(path,'ce77a7748e8beb0ff4eb71571e4a24858e0e2c905d1bf15a0c642d07b18d84bd',name)
  o.load=raw_existing
  for name,h in [('PROFILE.json','a3d8362d8c06e563cb74d55f92762d2f58d18943f0061fa5a87256335df9f8ce'),('legacy_foreign_binding.json','e069be66ddd0e7d9e7000c2edc93d0dcc12436e830c6f685a08e8c0960ce2c34')]:need(digest(o.V/name)==h,'FIXED_R5_DATA')
  v=o.observe();need(v['unknown_active_cohort_count']==0,'NATIVE_UNKNOWN_FOREIGN')
  mr=a['memory_module_ref'];need(mr['sha256']=='ccde5eb672a38448b834b8339cbbaf1ceeab1b9e8d4ac101253965eab7dd1238','FIXED_MEMORY_MODULE');m=pinned_module(mr['path'],mr['sha256'],'SC61_memory');snap=m.collect();verdict=m.evaluate(snap,v['additional_active_RAM_commitments_bytes'],2*G,'native174')
 finally:
  sys.path[:]=old
  for name,value in previous_helpers.items():
   if value is None:sys.modules.pop(name,None)
   else:sys.modules[name]=value
 light=native_light_verdict(verdict,v,a['Native_bridge_policy'])
 need(shutil.disk_usage('/root/data').free>=5*G+64*2**20,'NATIVE_FLOOR')
 save(root/('NATIVE_RESOURCE_'+str(time.time_ns())+'.json'),dict(light_bridge_verdict=light,original_full_R4_aggregate_verdict=verdict,additional_foreign=v['additional_active_RAM_commitments_bytes'],own_control=2*G,heavy_POST_budget_checked_separately_109=True))
