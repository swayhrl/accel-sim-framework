"""Independent CPU-only V8 performance/numeric/cache/observer recheck."""
from pathlib import Path
import json,hashlib,math,statistics,csv,time
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/"docs/ai_workload_research/runs/QWEN_BF16_BATCH_PERFORMANCE_NUMERIC_STUDY_109_V8"
def H(v):return hashlib.sha256(v).hexdigest()
def D(v):return H(json.dumps(v,sort_keys=True,separators=(',',':')).encode())
def save(n,v):(OUT/n).write_text(json.dumps(v,indent=2)+"\n")
def stats(vals):
 m=statistics.median(vals)
 return dict(n=len(vals),median=m,MAD=statistics.median(abs(x-m) for x in vals),minimum=min(vals),maximum=max(vals),values=vals,MAD_over_median=statistics.median(abs(x-m) for x in vals)/abs(m) if m else None)
def compare(a,b):
 n=min(len(a['tokens']),len(b['tokens']));prefix=next((i for i in range(n) if a['tokens'][i]!=b['tokens'][i]),n)
 rows=[]
 for j in range(min(n,len(a['logprobs']),len(b['logprobs']))):
  ta,tb=a['tokens'][j],b['tokens'][j];pa,pb=a['logprobs'][j][str(ta)],b['logprobs'][j][str(tb)]
  common=set(a['logprobs'][j])&set(b['logprobs'][j])
  rows.append(dict(step=j,token_same=ta==tb,same_history=j<=prefix,B1=pa,B2=pb,abs_error=abs(pb-pa),allowed=.05+.01*abs(pa),old_gate_pass=abs(pb-pa)<=.05+.01*abs(pa),common_top20_count=len(common),
     common_top20_delta_min=min((b['logprobs'][j][k]-a['logprobs'][j][k] for k in common),default=None),common_top20_delta_max=max((b['logprobs'][j][k]-a['logprobs'][j][k] for k in common),default=None)))
 return dict(tokens_exact=a['tokens']==b['tokens'],common_prefix_tokens=prefix,first_divergence=None if a['tokens']==b['tokens'] else prefix,rows=rows,
   sampled_same_token_fail_steps=[x['step'] for x in rows if x['token_same'] and not x['old_gate_pass']],same_history_fail_steps=[x['step'] for x in rows if x['same_history'] and x['token_same'] and not x['old_gate_pass']])
def main():
 c=json.loads((OUT/'SCIENCE_CONTRACT.json').read_text());allrows=[];runtime={};private={};refs={};receipt=json.loads((OUT/'RESOURCE_RECEIPT.json').read_text())
 if 'samples_archive' in receipt:
  import gzip
  payload=gzip.decompress((OUT/receipt['samples_archive']['path']).read_bytes());assert H(payload)==receipt['samples_archive']['uncompressed_sha256'];receipt=json.loads(payload)
 inp=json.loads((OUT/'.private/inputs.json').read_text());source_map={D(v):k.removesuffix('_512') for k,v in inp.items()}
 completion_count=0;checks=[]
 for task in ['BASE','PREFIX']:
  master=json.loads((OUT/'raw'/(task+'.json')).read_text());runtime[task]=master.get('runtime');secret=json.loads((OUT/'.private'/(task+'_private_outputs.json')).read_text());private[task]=secret
  assert len(master['samples'])==len(secret['samples'])
  for index,pr in zip(master['samples'],secret['samples']):
   path=OUT/index['file'];assert H(path.read_bytes())==index['sha256'];s=json.loads(path.read_text())
   assert s['index']==pr['index']==index['index'];assert s['config']==pr['config'];assert s['capture_complete_before_numeric_gate']
   assert s['status']=='PASS_RUNTIME_VALID' and s['active_compiled_Qwen2Model']
   assert math.isfinite(s['request_gpu_elapsed_ms']) and s['request_gpu_elapsed_ms']>0
   assert len(pr['outputs'])==len(s['outputs'])==s['batch_size']
   for pu,pv in zip(s['outputs'],pr['outputs']):
    source=source_map[D(pv['returned_prompt_token_ids'])];assert source==pv['source']==pu['source']
    assert D(pv['returned_prompt_token_ids'])==pu['prompt_token_sha256'];assert len(pv['completions'])==1
    out=pv['completions'][0];assert out['tokens']==pv['tokens'] and out['logprobs']==pv['logprobs']
    assert len(out['tokens'])==s['output_tokens_each'];assert D(out['tokens'])==pu['token_sha256'];assert D(out['logprobs'])==pu['logprob_sha256']
    assert all(math.isfinite(v) for step in out['logprobs'] for v in step.values())
    if s['sampling']['logprobs'] is not None:
     selected=[out['logprobs'][j][str(tok)] for j,tok in enumerate(out['tokens'])]
     assert selected==out['sampled_token_logprobs'];assert D(selected)==pu['sampled_logprob_sha256']
    else:assert out['logprobs']==[]
    completion_count+=1
   allrows.append(s);refs[(task,s['index'])]=pr
  checks.append(dict(task=task,requests=len(master['samples']),all_samples_and_sources_verified=True,sha=H((OUT/'.private'/(task+'_private_outputs.json')).read_bytes())))
 configurations={}
 for config in ['MAIN','LP20_CONTROL','LP_NONE','APC_COLD','APC_WARM']:
  rows=[s for s in allrows if s['config']==config and s['role']=='FORMAL'];ps={}
  for point in ['P1','P2','P3','P4','P5','P6']:
   group=[s for s in rows if s['point']==point];assert len(group)>=5
   ps[point]=dict(GPU_ms=stats([s['request_gpu_elapsed_ms'] for s in group]),host_generate_ms=stats([s['host_generate_call_ms'] for s in group]),host_sync_ms=stats([s['host_synchronized_request_ms'] for s in group]),
      formal_compile_capture=sum(s['formal_compile_or_capture'] for s in group),fullgraph_replays=sorted(set(len(s['graph_replays']) for s in group)),
      cached_tokens=[o['num_cached_tokens'] for s in group for o in s['outputs']],
      drift_first2_last2_ms=statistics.median([s['request_gpu_elapsed_ms'] for s in group[-2:]])-statistics.median([s['request_gpu_elapsed_ms'] for s in group[:2]]))
  med=lambda p:ps[p]['GPU_ms']['median']
  da,db,dc=med('P4')-med('P1'),med('P5')-med('P2'),med('P6')-med('P3');den=(da+db)/2
  envelope=(ps['P4']['GPU_ms']['MAD']+ps['P1']['GPU_ms']['MAD']+ps['P5']['GPU_ms']['MAD']+ps['P2']['GPU_ms']['MAD'])/2
  configurations[config]=dict(points=ps,delta_A00_ms=da,delta_A01_ms=db,delta_B2_ms=dc,denominator_ms=den,R=dc/den if den else None,
     denominator_positive=den>0,denominator_over_MAD_envelope=den/envelope if envelope else None,
     all_point_MAD_over_median_le_0p05=all(v['GPU_ms']['MAD_over_median']<=.05 for v in ps.values()),
     full32_aggregate_tokens_per_second_B1_A00=32/(med('P4')/1000),full32_aggregate_tokens_per_second_B2=64/(med('P6')/1000),
     two_separate_B1_total_over_B2=(med('P4')+med('P5'))/med('P6'),incremental_amortization_factor=2*den/dc,
     first_token_B2_over_meanB1=med('P3')/((med('P1')+med('P2'))/2),
     full32_B2_over_meanB1=med('P6')/((med('P4')+med('P5'))/2))
 controls={}
 for name,left,right in [('logprobs','LP20_CONTROL','LP_NONE'),('prefix_cold_minus_warm','APC_COLD','APC_WARM')]:
  paired={}
  for point in ['P1','P2','P3','P4','P5','P6']:
   a={s['round']:s for s in allrows if s['config']==left and s['role']=='FORMAL' and s['point']==point}
   b={s['round']:s for s in allrows if s['config']==right and s['role']=='FORMAL' and s['point']==point};assert set(a)==set(b)
   paired[point]=stats([a[k]['request_gpu_elapsed_ms']-b[k]['request_gpu_elapsed_ms'] for k in a])
  controls[name]=dict(left=left,right=right,paired_ms=paired,delta_A00_effect_ms=configurations[left]['delta_A00_ms']-configurations[right]['delta_A00_ms'],
    delta_A01_effect_ms=configurations[left]['delta_A01_ms']-configurations[right]['delta_A01_ms'],delta_B2_effect_ms=configurations[left]['delta_B2_ms']-configurations[right]['delta_B2_ms'],
    interpretation='End-to-end controlled software bundle,not isolated kernel cost;separatepools')
 # Numeric comparisons: same round formalpair,all samples preserved.
 numeric={}
 for config in configurations:
  task='BASE' if config in ['MAIN','LP20_CONTROL','LP_NONE'] else 'PREFIX';cross=[];repeats=[]
  for ri in sorted(set(s['round'] for s in allrows if s['config']==config and s['role']=='FORMAL')):
   selection={s['point']:refs[(task,s['index'])] for s in allrows if s['config']==config and s['role']=='FORMAL' and s['round']==ri}
   for source,p1,p32 in [('TRAIN_A_DISCOVERY_00','P1','P4'),('TRAIN_A_DISCOVERY_01','P2','P5')]:
    for p,q in [(p1,'P3'),(p32,'P6')]:
     a=next(x for x in selection[p]['outputs'] if x['source']==source);b=next(x for x in selection[q]['outputs'] if x['source']==source)
     result=compare(a,b);cross.append(dict(round=ri,source=source,B1_point=p,B2_point=q,**result))
  for point in ['P1','P2','P3','P4','P5','P6']:
   selection=[refs[(task,s['index'])] for s in allrows if s['config']==config and s['role']=='FORMAL' and s['point']==point]
   for j,pr in enumerate(selection[1:],1):
    for a,b in zip(selection[0]['outputs'],pr['outputs']):repeats.append(dict(point=point,source=a['source'],sample=j,**compare(a,b)))
  item=dict(config=config,logprobs_observed=config!='LP_NONE',B1_B2_pairs=cross,repetition=repeats,
    token_exact_all_B1_B2=all(x['tokens_exact'] for x in cross),old_sampled_gate_failures_same_token=sum(len(x['sampled_same_token_fail_steps']) for x in cross),
    note='Old gate FAIL remains FAIL;it is an observation,not V8 performance admission. Different-token probabilities are not strict same-token comparisons.')
  numeric[config]=item;save('NUMERIC_'+config+'.json',item)
 # Exact software cross-config token comparisons.
 crossconfig=[]
 for a,b,task in [('MAIN','LP_NONE','BASE'),('LP20_CONTROL','LP_NONE','BASE'),('APC_COLD','APC_WARM','PREFIX')]:
  for point in ['P1','P2','P3','P4','P5','P6']:
   ar=[refs[(task,s['index'])] for s in allrows if s['config']==a and s['point']==point and s['role']=='FORMAL']
   br=[refs[(task,s['index'])] for s in allrows if s['config']==b and s['point']==point and s['role']=='FORMAL']
   for pa,pb in zip(ar,br):
    for aa,bb in zip(pa['outputs'],pb['outputs']):crossconfig.append(dict(left=a,right=b,point=point,source=aa['source'],tokens_exact=aa['tokens']==bb['tokens'],common_prefix_tokens=compare(aa,bb)['common_prefix_tokens'],first_divergence=compare(aa,bb)['first_divergence']))
 cache_valid=dict(cold_all_observed_zero=all(x==0 for p in configurations['APC_COLD']['points'].values() for x in p['cached_tokens']),
   warm_values=sorted(set(x for p in configurations['APC_WARM']['points'].values() for x in p['cached_tokens'])),
   warm_all_positive=all(isinstance(x,int) and x>0 for p in configurations['APC_WARM']['points'].values() for x in p['cached_tokens']),
   primer_requests=sum(s['role']=='CACHE_PRIME' for s in allrows),primer_in_formal=False,reset_and_prime_outside_timing=True)
 save('PERFORMANCE.json',dict(status='COMPLETE_NATIVE_SHARED_CONDITION',configurations=configurations,controls=controls,cache_validity=cache_valid))
 save('NUMERIC_SUMMARY.json',dict(configurations={k:{f:v[f] for f in ['logprobs_observed','token_exact_all_B1_B2','old_sampled_gate_failures_same_token']} for k,v in numeric.items()},cross_configuration_tokens=crossconfig,old_threshold_changed=False))
 for filename,roles in [('FORMAL_SAMPLES.tsv',['FORMAL']),('NONFORMAL_SAMPLES.tsv',['WARMUP','CACHE_PRIME','OBSERVER'])]:
  with (OUT/filename).open('w',newline='') as f:
   fields=['task','config','index','point','role','round','block','batch_size','output_tokens_each','request_gpu_elapsed_ms','host_generate_call_ms','host_synchronized_request_ms','status']
   writer=csv.DictWriter(f,fieldnames=fields,delimiter='\t',lineterminator='\n');writer.writeheader()
   for s in allrows:
    if s['role'] in roles:writer.writerow({k:('BASE' if s['config'] in ['MAIN','LP20_CONTROL','LP_NONE','LOCAL_OBSERVER'] else 'PREFIX') if k=='task' else s.get(k) for k in fields})
 bounds=json.loads((OUT/'MODEL_AND_BANDWIDTH_BOUND.json').read_text());main=configurations['MAIN']
 conditional=dict(bytes=bounds['no_retention_streaming_bytes'],nominal_ideal_ms=bounds['no_retention_ideal_ms'],L2_credit_ideal_ms=bounds['L2_credit_ideal_ms'],
  inferred_model_bytes_over_single_delta_GB_s=bounds['no_retention_streaming_bytes']/(main['denominator_ms']/1000)/1e9,
  ratio_to_nominal=(bounds['no_retention_streaming_bytes']/(main['denominator_ms']/1000))/bounds['nominal_bandwidth_B_s'],
  status='MEMORY_SUPPLY_CONSISTENT_NOT_CAUSALLY_PROVEN',not_DRAM_measured=True,
  alternatives=['Launch/control overhead can be shared','GEMM shape/occupancy/padding','Scheduler/sampler/graph overhead','No independent memory versus compute hardwareaxis'])
 resource=dict(status=receipt['status'],GPU_lock_held_seconds=receipt['GPU_lock_held_seconds'],GPU_model_initializations=receipt['GPU_model_initializations'],snapshots=len(receipt['samples']),
   own_NVML_MiB_peak=max(s['own_NVML_MiB'] for s in receipt['samples']),live_tree_RSS_subtotal_peak=max(s['own_tree_RSS_bytes'] for s in receipt['samples']),
   kernel_session_charged_memory_peak=max(s['session_memory']['kernel_charged_peak_bytes'] for s in receipt['samples']),root_disk_bytes_peak=max(s['own_new_disk_bytes'] for s in receipt['samples']),
   censored_races=[dict(snapshot=i,record=x) for i,s in enumerate(receipt['samples']) for x in s.get('rss_censored_observations',[])],
   mandatory_gaps=[dict(snapshot=i,gaps=s['monitor_gaps']) for i,s in enumerate(receipt['samples']) if s['monitor_gaps']],
   ImageLab_completed_scopes=sorted(set(s['shared_gate']['completed_scopes'] for s in receipt['samples'])),ImageLab_inflight=sorted(set(s['shared_gate']['in_flight_scopes'] for s in receipt['samples'])),
   desktop_perprocess_gap=receipt.get('performance_comparability_gap'),condition=receipt['measurement_condition'],own_contexts_cleared=receipt['own_GPU_contexts_cleared'],lock_released=receipt['lock_released'],reservation_cleanup=receipt['shared_reservation_cleanup'])
 save('RESOURCE_SUMMARY.json',resource)
 summary=dict(status='V8_COMPLETE',requests=len(allrows),completions=completion_count,formal_samples=sum(s['role']=='FORMAL' for s in allrows),configurations=list(configurations),checks=checks,runtime=runtime,
    input_runtime_validity='PASS',performance_measurement_validity='VALID_DESCRIPTIVE_NATIVE_SHARED_CONDITION',token_sequence_identity='Seeperconfigandcrossconfigurationresults',
    logprob_numeric_sensitivity='OldthresholdstillFAILinmultiplecomparisons;retainedseparately',architectural_causal_evidence='INSUFFICIENT_FOR_MEMORY_BOUND_OR_HARDWARE_INNOVATION',
    conditional_weight_model=conditional,all_formal_compile_capture_flags=sum(s['formal_compile_or_capture'] for s in allrows if s['role']=='FORMAL'),
    prior_monitor_interpretation='V7 retained INCONCLUSIVE text for missing desktop perprocess telemetry. V8 separates valid recorded timings from strictexclusive/causal interpretation;the gap remains,with no claim of no interference.')
 save('ANALYSIS.json',summary)
 print(json.dumps(dict(formals=summary['formal_samples'],requests=len(allrows),completions=completion_count,perf={k:{f:v[f] for f in ['delta_A00_ms','delta_A01_ms','delta_B2_ms','R']} for k,v in configurations.items()},cache=cache_valid,numeric={k:v['token_exact_all_B1_B2'] for k,v in numeric.items()},resource=resource)))
if __name__=='__main__':main()
