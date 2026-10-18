from resource_accounting_r3 import *
import sys,hashlib
r=reg.Registry(SHARED);lease_file=Path(os.environ.get('LANE2_LEASE_FILE',str(BASE/'lease.txt')))
if len(sys.argv)>1 and sys.argv[1]=='release':r.release_build(lease_file.read_text().strip(),'lane2');sys.exit()
authority=json.loads((SHARED/'CLIENT_CONTRACT.json').read_text())['output_budget_authorization'];assert authority['max_result_bytes']>=20*2**30
with r.locked() as state:
 snap=snapshot(state);growth=int(os.environ.get('LANE2_OUTPUT_MIB','16'))*2**20;extra=snap['publication_future_reserve_bytes'];other=snap['other_own_EDA_reserved_growth_bytes'];pending=snap['pending_apps_predicted_growth_bytes'];resources=snap['resources'];policy=state['hosts'][socket.gethostname()]
 assert snap['shared_result_actual_bytes']+snap['Lane2_outside_shared_results_plus_Git_bytes']+pending+other+growth+extra<=snap['shared_limit_bytes'],'shared20GiB forecast ceiling'
 assert snap['Lane2_owned_actual_plus_conservative_Git_reserve_bytes']+other+growth+extra<=snap['own_limit_bytes'],'independent Lane2 own12GiB forecast ceiling'
 maintenance=os.environ.get('LANE2_NET_NEGATIVE_MAINTENANCE')=='1'
 if maintenance:
  assert resources['disk_free_bytes']-growth>=policy['min_disk_free_bytes'],'net-negative maintenance actual free minus temporary compressed output floor'
  snap['maintenance_scope']='lossless archive only own new R3 files; bounded temporary output; no formal build; no reduction of physical floor or changes to existing app forecast/lease'
 else:assert resources['disk_free_bytes']-snap['physical_reserved_unwaived_app_growth_bytes']-other-growth>=policy['min_disk_free_bytes'],'physical safety floor after own EDA and non-waived app growth; exact existing Lane5 forecast exceptions retained'
 assert resources['share_disk_free_bytes']>=40*2**30
 snap['EDA_cap_bytes']=growth
cpu=1;memory=int(os.environ.get('LANE2_MEM_GIB','2'))*2**30;key=r.build_lease('lane2',cpu=cpu,memory=memory)
try:
 with r.locked() as state:
  row=state['resource_leases'][key];row['output_forecast_bytes']=growth;row['output_phase_root']=os.environ.get('LANE2_MONITOR_ROOT','/workspace/ep_l2_potential20261017_lane5_results/EPL2_RTL_R3_METADATA_AND_COST_OPT_lane2');row['output_phase_initial_bytes']=reg.retained_tree_bytes(Path(row['output_phase_root']))
 lease_file.write_text(key+'\n');snap.update(lease_id=key,cpu_units=cpu,memory_bytes=memory);(BASE/('admission-'+key+'.json')).write_text(json.dumps(snap,indent=2)+'\n');print(json.dumps(snap),flush=True)
except BaseException:
 r.release_build(key,'lane2');raise
