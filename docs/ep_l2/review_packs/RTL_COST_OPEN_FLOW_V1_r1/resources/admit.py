from pathlib import Path
import json,os,sys,importlib.util,hashlib
base=Path('/workspace/ep_l2_rtl_cost_open_flow_v1/r1');shared=Path('/workspace/ep_l2_ft20261016_shared');c=json.loads((base/'CLIENT_CONTRACT_SNAPSHOT.json').read_text());p=base/'registry_pinned.py';assert hashlib.sha256(p.read_bytes()).hexdigest()==c['registry_client_sha256']
spec=importlib.util.spec_from_file_location('reg',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);r=m.Registry(shared);lease_file=Path(os.environ.get('LANE2_LEASE_FILE',str(base/'lease.txt')))
if len(sys.argv)>1 and sys.argv[1]=='release':r.release_build(lease_file.read_text().strip(),'lane2');sys.exit()
artifact=Path('/workspace/ep_l2_potential20261017_lane5_results/EPL2_RTL_COST_OPEN_FLOW_V1_lane2_r1');artifact.mkdir(exist_ok=True)
with r.locked() as state:
 policy=state['hosts'][__import__('socket').gethostname()];actual=sum(m.retained_tree_bytes(x) for x in {m.RESULT_WORKSPACE.resolve(),m.RESULT_LEGACY.resolve()});pending=sum(max(0,x.get('output_budget',{}).get('predicted_growth_bytes',policy['default_run_output_limit_bytes']+128*2**20)-m.retained_tree_bytes(Path(x['result_directory']))) for x in state['runs'].values() if x['status'] in m.ACTIVE);resources=m.local_resources();growth=int(os.environ.get("LANE2_OUTPUT_MIB","16"))*2**20
 assert actual+pending+growth<=policy['max_result_bytes'],'aggregate12GiB including EDA forecast'
 assert resources['disk_free_bytes']-pending-growth>=policy['min_disk_free_bytes'],'physical safety floor after growth'
 assert resources['share_disk_free_bytes']>=40*2**30
 snapshot={'actual_including_EDA_root_bytes':actual,'pending_apps_predicted_growth_bytes':pending,'EDA_cap_bytes':growth,'resources':resources,'central_max_bytes':policy['max_result_bytes'],'EDA_root':str(artifact)}
cpu=1;memory=int(os.environ.get('LANE2_MEM_GIB','2'))*2**30;key=r.build_lease('lane2',cpu=cpu,memory=memory);lease_file.write_text(key+'\n');snapshot.update(lease_id=key,cpu_units=cpu,memory_bytes=memory);(base/('admission-'+key+'.json')).write_text(json.dumps(snapshot,indent=2)+'\n');print(json.dumps(snapshot))
