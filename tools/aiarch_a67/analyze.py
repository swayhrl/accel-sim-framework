"""CPU-only independent raw recomputation; no additional GPU or training calls."""
import collections,json,math,statistics,hashlib
from paths import R,save

def main():
 d=json.loads((R/'native_results.json').read_text());g=json.loads((R/'gpu_ledger.json').read_text());p=json.loads((R/'preregistration.json').read_text())
 assert d['status']=='PASS_ALL_6_EAGER_WINDOWS' and d['total_updates']==85 and d['formal_updates']==72
 assert g['reason'] is None and g['exclusivity_evidence_complete'] and g['final_NVML_empty'] and g['all_owned_processes_ended']
 assert json.loads((R/'G1_OFF_numeric.json').read_text())['status']=='PASS'
 snapshots=[json.loads(x) for x in (R/'raw/gpu_pid_snapshots.jsonl').read_text().splitlines()]
 by_query={x['query_start']:x for x in snapshots};classes=collections.Counter()
 for x in snapshots:
  assert x['stop_reason'] is None
  for decision in x['classification']:classes[decision['classification']]+=1
 identities=json.loads((R/'GPU_child_launch.json').read_text())['identity']
 for name in ['child_identity_start.json','child_identity_end.json']:
  actual=json.loads((R/name).read_text());assert actual['PID']==identities['pid'] and actual['PGID']==identities['pgid'] and actual['SID']==identities['sid']
 rows=[];initial={};orders={}
 for index,x in enumerate(d['windows']):
  assert [x['arm'],x['seed']]==p['schedule'][index]
  assert x['status']=='PASS' and x['completed_updates']==12 and len(x['losses'])==12 and len(x['sample_counts'])==12
  assert all(math.isfinite(y) for y in x['losses']) and x['finite']['actual_Adam_step_each_parameter']==14
  assert x['formal_node_order_actual_sha256']==x['formal_node_order_expected_sha256']
  for y in x['sample_counts']:
   assert y['feature_rows']==y['input_nodes'] and y['logical_feature_request_bytes']==y['input_nodes']*1024*4
   assert len(y['sampled_edges_each_layer'])==3
  seed=x['seed']
  if seed in initial:assert x['initial_model_sha256']==initial[seed] and x['formal_node_order_actual_sha256']==orders[seed]
  else:initial[seed]=x['initial_model_sha256'];orders[seed]=x['formal_node_order_actual_sha256']
  samples=[v for v in g['samples'] if v['phase'].get('arm')==x['arm'] and v['phase'].get('seed')==seed]
  for boundary in ['FORMAL_UNINSTRUMENTED','FORMAL_WALL_SAVED']:
   points=[v for v in samples if v['phase']['phase']==boundary];assert points,'MISSING_WINDOW_BOUNDARY_PID_EVIDENCE'
   for v in points:assert by_query[v['PID_snapshot_query_start']]['stop_reason'] is None
  wall=x['full_train_step_wall_seconds'];assert wall>0
  assert math.isclose(x['natural_seed_nodes_per_second'],12288/wall,rel_tol=1e-14)
  row={'arm':x['arm'],'seed':seed,'position':index,'formal_updates':12,'wall_seconds':wall,'mean_complete_batch_ms':wall/12*1000,'natural_seed_nodes_per_second':12288/wall,'losses':x['losses'],'loss_mean':statistics.mean(x['losses']),'loss_sample_stdev':statistics.stdev(x['losses']),'initial_model_SHA256':initial[seed],'formal_node_order_SHA256':orders[seed],'peak_sampled_window_RSS_bytes':max(v['RSS_bytes'] for v in samples),'peak_sampled_window_GPU_MiB':max(v['GPU_MiB'] for v in samples),'Torch_formal_peak_allocated_bytes':x['Torch_peak_allocated_bytes'],'Torch_formal_peak_reserved_bytes':x['Torch_peak_reserved_bytes'],'ctx_preparation_seconds':x['preparation_seconds'],'warmup_with_audits_seconds':x['warmup_seconds_including_qualification_audits'],'full_residency':x['residency'],'cache_before':x['cache_before'],'cache_after':x['cache_after']}
  rows.append(row)
 by={(x['seed'],x['arm']):x for x in rows};ratios=[]
 for seed in [20261015,20261016]:
  full=by[seed,'FULL_RESIDENT_GPU'];on=by[seed,'PINNED_CACHE_ON'];off=by[seed,'PINNED_CACHE_OFF']
  ratios.append({'seed':seed,'ON_wall_over_FULL':on['wall_seconds']/full['wall_seconds'],'OFF_wall_over_FULL':off['wall_seconds']/full['wall_seconds'],'ON_wall_over_OFF':on['wall_seconds']/off['wall_seconds'],'FULL_ctx_prep_plus_formal_seconds':full['ctx_preparation_seconds']+full['wall_seconds'],'ON_ctx_prep_plus_formal_seconds':on['ctx_preparation_seconds']+on['wall_seconds'],'scope':'distribution comparison, not bitwise paired; setup plus formal is arithmetic illustration excluding common pin and warmup/audit'})
 aggregate={}
 for arm in ['FULL_RESIDENT_GPU','PINNED_CACHE_ON','PINNED_CACHE_OFF']:
  vals=[x['wall_seconds'] for x in rows if x['arm']==arm];aggregate[arm]={'n_windows':2,'mean_wall_seconds':statistics.mean(vals),'sample_stdev_seconds':statistics.stdev(vals),'sample_CV':statistics.stdev(vals)/statistics.mean(vals),'min_wall_seconds':min(vals),'max_wall_seconds':max(vals),'not_independent_perstep_latencies':True}
 assert all(x['ON_wall_over_FULL']>1 and x['OFF_wall_over_FULL']>1 for x in ratios)
 save('analysis.json',{'scientific_status':'SCOPED_FULL_RESIDENT_SOFTWARE_ALTERNATIVE','scope':'EAGER_ONLY','windows':rows,'per_seed_ratios':ratios,'two_seed_dispersion':aggregate,'source_update_count':{'qualification':1,'warmup':12,'formal':72,'total':85},'PID_snapshots':len(snapshots),'PID_classification_counts':dict(classes),'full_exclusivity_evidence_complete':True,'limitations':['only2 short12step windows perarm','FULL has appreciable two-seed/order dispersion; ratios are observed, not precise general speedups','same node orders, independently sampled neighborhoods','no sync supply-wait decomposition or physical PCIe/DRAM byte measurement','full upload,pin,warmups excluded from steady-state wall and reported separately','compiled strong path remains unqualified; not all software backends exhausted','CONVERGENCE_NOT_EVALUATED'],'next_minimal_recommendation':{'action':'CPU-only independent review of this exact raw six-window pack and full-resident capacity/setup accounting, then close IGB-small eager hardware-supply hypothesis unless new evidence changes scope','GPU_seconds':0,'downloads_installs':0,'CPU_workers_max':2,'RAM_MiB_max':512,'new_disk_MiB_max':16,'stop_conditions':['any identity/wall-boundary/PID/raw mismatch'],'no_new_GPU_or_dataset_authorization':True}})
 print('CPU_RECOMPUTE_PASS',json.dumps({'classification':'SCOPED_FULL_RESIDENT_SOFTWARE_ALTERNATIVE','ratios':ratios,'PID_snapshots':len(snapshots),'PID_classes':dict(classes)}),flush=True)

if __name__=='__main__':main()
