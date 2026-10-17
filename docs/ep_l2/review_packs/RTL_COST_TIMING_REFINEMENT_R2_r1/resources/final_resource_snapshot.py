from pathlib import Path
import importlib.util,json,datetime,subprocess,hashlib,socket,os
b=Path('/workspace/ep_l2_rtl_cost_timing_r2');art=Path('/workspace/ep_l2_potential20261017_lane5_results/EPL2_RTL_COST_TIMING_REFINEMENT_R2_lane2_v3');pack=art/'PUBLIC_REVIEW_PACK_R2';repo=Path('/workspace/worktrees/accel-sim-ep-l2-rtl-cost-r2-fanout-v3')
s=importlib.util.spec_from_file_location('reg',b/'registry_pinned.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);r=m.Registry(Path('/workspace/ep_l2_ft20261016_shared'))
with r.locked() as st:
 actual=sum(m.retained_tree_bytes(x) for x in {m.RESULT_WORKSPACE.resolve(),m.RESULT_LEGACY.resolve()});res=m.local_resources();pol=st['hosts'][socket.gethostname()];pending=sum(max(0,x.get('output_budget',{}).get('predicted_growth_bytes',pol['default_run_output_limit_bytes']+128*2**20)-m.retained_tree_bytes(Path(x['result_directory']))) for x in st['runs'].values() if x['status'] in m.ACTIVE)
 own=[]
 for f in b.glob('admission-*.json'):
  ad=json.loads(f.read_text());lease=st['resource_leases'][ad['lease_id']];own.append({'lease_id':ad['lease_id'],'status':lease['status'],'memory_bytes':ad['memory_bytes'],'cpu':ad['cpu_units']})
 active=[x for x in own if x['status']=='RESERVED'];key=Path(os.environ['LANE2_LEASE_FILE']).read_text().strip();assert all(x['lease_id']==key for x in active),'nonpublication own lease still reserved'
 target=repo/'docs/ep_l2/review_packs/RTL_COST_TIMING_REFINEMENT_R2_r1';assert not target.exists(),'calculate before new immutable copy'
 packbytes=sum(p.stat().st_size for p in pack.rglob('*') if p.is_file());publication_growth=2*packbytes+32*2**20
 assert actual+pending+publication_growth<=12*2**30
 assert res['disk_free_bytes']-pending-publication_growth>=48*2**30 and res['share_disk_free_bytes']>=40*2**30 and res['available_memory_bytes']>=64*2**30
 cores={}
 for label,path,want in [('TVD','gpgpu-sim-ep-l2-ft20261016-lane2-repair-r3','be5dcbe1fa5b9a501e81a77a6c399e6f6530e536'),('common','gpgpu-sim-ep-l2-ft20261017-lane2-common-r16','099aeb5ac002ddc03ab8dc295caa1333d9aa50e1'),('structural','gpgpu-sim-ep-l2-potential20261017-lane2-v1','26ed1da60249727870802c84f52fabe72274c541')]:
  cwd=Path('/workspace/worktrees')/path;head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=cwd,text=True).strip();dirty=subprocess.check_output(['git','status','--porcelain'],cwd=cwd,text=True);assert head==want and not dirty;(cores.update({label:{'HEAD':head,'clean':True}}))
 r1=Path('/workspace/worktrees/accel-sim-ep-l2-rtl-cost-v1');assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=r1,text=True).strip()=='09de19579c0708f6542dfd65e1f3aae8a9a8b841';assert not subprocess.check_output(['git','status','--porcelain'],cwd=r1,text=True)
 result={'UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'phase':'all EDA complete; publication copy/mapping object forecast; own publication lease still active and will release by guard finally','resources':res,'actual_central_retained_including_EDA_bytes':actual,'pending_existing_app_forecast_bytes':pending,'new_pack_bytes_before_snapshot':packbytes,'publication_additional_copy_and_git_object_allowance_bytes':publication_growth,'conservative_forecast_aggregate_bytes':actual+pending+publication_growth,'own_ceiling_bytes':12*2**30,'workspace_floor_bytes':48*2**30,'Share_floor_bytes':40*2**30,'availableRAM_floor_bytes':64*2**30,'own_leases':own,'only_active_own_lease':key,'Core_candidates':cores,'R1_worktree_clean_frozen':True,'formal_SIM_or_apps_launched':False,'other_project_process_or_data_mutations':False,'new_waiters':0,'no_R1_retests':True}
 (pack/'resources/FINAL_RESOURCE_SNAPSHOT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ('own_leases','Core_candidates')}))
