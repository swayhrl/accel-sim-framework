from pathlib import Path
import json,os,importlib.util,socket,hashlib
BASE=Path('/workspace/ep_l2_rtl_r3_metadata_cost');SHARED=Path('/workspace/ep_l2_ft20261016_shared')
spec=importlib.util.spec_from_file_location('registry_r3',BASE/'registry_pinned.py');reg=importlib.util.module_from_spec(spec);spec.loader.exec_module(reg)
PUBLICATION_RESERVE=128*2**20
GIT_CONSERVATIVE_RESERVE=2**30

def inventory():
 roots=list(Path('/workspace').glob('ep_l2_rtl*'))
 roots+=list(Path('/workspace/worktrees').glob('*lane2*'))+list(Path('/workspace/worktrees').glob('*rtl*'))
 for parent in (reg.RESULT_WORKSPACE,reg.RESULT_LEGACY):
  roots += [p for p in parent.iterdir() if p.is_dir() and ('lane2' in p.name.lower() or 'rtl' in p.name.lower())]
 unique=[]
 for p in sorted({p.resolve() for p in roots},key=lambda p:len(p.parts)):
  if not any(p==q or q in p.parents for q in unique):unique.append(p)
 shared_roots={reg.RESULT_WORKSPACE.resolve(),reg.RESULT_LEGACY.resolve()}
 rows=[{'path':str(p),'bytes':reg.retained_tree_bytes(p),'already_in_shared_result_roots':any(p==q or q in p.parents for q in shared_roots)} for p in unique]
 return rows

def snapshot(state):
 policy=state['hosts'][socket.gethostname()];rows=inventory();actual=sum(reg.retained_tree_bytes(x) for x in {reg.RESULT_WORKSPACE.resolve(),reg.RESULT_LEGACY.resolve()})
 pending=sum(max(0,x.get('output_budget',{}).get('predicted_growth_bytes',policy['default_run_output_limit_bytes']+128*2**20)-reg.retained_tree_bytes(Path(x['result_directory']))) for x in state['runs'].values() if x['status'] in reg.ACTIVE)
 waived=0;waivers=[]
 for key,x in state['runs'].items():
  if x['status'] not in reg.ACTIVE:continue
  exception=x.get('output_budget',{}).get('disk_growth_reservation_exception')
  if exception:
   assert exception['run_key']==key
   evidence=exception['authorization_file'];assert hashlib.sha256(Path(evidence['path']).read_bytes()).hexdigest()==evidence['sha256']
   waived+=max(0,x['output_budget']['predicted_growth_bytes']-reg.retained_tree_bytes(Path(x['result_directory'])))
   waivers.append({'run_key':key,'exact_existing_authorization':exception})
 other=sum(max(0,x.get('output_forecast_bytes',json.loads((BASE/('admission-'+k+'.json')).read_text()).get('EDA_cap_bytes',0) if (BASE/('admission-'+k+'.json')).exists() else 0)-max(0,reg.retained_tree_bytes(Path(x['output_phase_root']))-x['output_phase_initial_bytes'])) if 'output_phase_root' in x else x.get('output_forecast_bytes',0) for k,x in state.get('resource_leases',{}).items() if x.get('owner')=='lane2' and x['status'] in reg.ACTIVE)
 own=sum(x['bytes'] for x in rows)+GIT_CONSERVATIVE_RESERVE
 outside=sum(x['bytes'] for x in rows if not x['already_in_shared_result_roots'])+GIT_CONSERVATIVE_RESERVE
 return {'shared_result_actual_bytes':actual,'Lane2_owned_inventory':rows,'Lane2_owned_actual_plus_conservative_Git_reserve_bytes':own,'Lane2_outside_shared_results_plus_Git_bytes':outside,'publication_future_reserve_bytes':PUBLICATION_RESERVE,'pending_apps_predicted_growth_bytes':pending,'physical_reserved_unwaived_app_growth_bytes':pending-waived,'existing_exact_app_forecast_waivers_retained':waivers,'other_own_EDA_reserved_growth_bytes':other,'shared_limit_bytes':policy['max_result_bytes'],'own_limit_bytes':12*2**30,'resources':reg.local_resources(),'ownership_rule':'deduplicated Lane2/RTL-only source worktrees, books and result roots; other Lane5 application assets never charged to own ceiling; incremental shared Git conservatively reserved at1GiB; all shared results plus Lane2 outside assets counted toward shared20GiB'}
