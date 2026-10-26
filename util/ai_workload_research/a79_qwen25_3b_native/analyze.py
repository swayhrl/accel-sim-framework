"""CPU analysis: preserve request boundaries and separate G1 from G2."""
import pathlib,json,statistics,csv,math
ROOT=pathlib.Path(__file__).resolve().parents[3];OUT=ROOT/'docs/ai_workload_research/runs/AI_ARCH_A79_QWEN25_3B_NATIVE_WORKLOAD_SENSITIVITY_109_V1'
def summarize(values):
 m=statistics.median(values);return {'formal_n':len(values),'median_ms':m,'MAD_ms':statistics.median(abs(v-m) for v in values),'raw_ms':values}
def analyze():
 resource=json.loads((OUT/'GPU_RESOURCE_RECEIPT.json').read_text());points=[];samples=[]
 for stage in ['G1','G2']:
  path=OUT/'raw'/(stage+'.json')
  if not path.exists():continue
  raw=json.loads(path.read_text())
  for p in raw['points']:
   for s in p['formal_samples']:samples.append({'stage':stage,'point':p['point'],'source':p['source'],'prompt_tokens':p['prompt_tokens'],'output_tokens':p['output_tokens'],'index':s['index'],'request_gpu_elapsed_ms':s['request_gpu_elapsed_ms'],'host_generate_wall_ms':s['host_generate_wall_ms'],'output_token_ids_sha256':s['output_token_ids_sha256'],'sampled_logprobs_sha256':s['sampled_logprobs_sha256'],'numeric_scope':p.get('numeric_scope','INCOMPLETE'),'point_status':p['status']})
   if p['status']=='PASS' and len(p['formal_samples'])==5:
    points.append({'stage':stage,**{k:p[k] for k in ['point','source','prompt_tokens','output_tokens']},'max_model_len':544 if stage=='G1' else 2080,'GPU_event':summarize([s['request_gpu_elapsed_ms'] for s in p['formal_samples']]),'host_generate_wall_diagnostic':summarize([s['host_generate_wall_ms'] for s in p['formal_samples']]),'numeric_scope':p['numeric_scope']})
 contrasts=[]
 for source in ['TRAIN_A_DISCOVERY_00','TRAIN_A_DISCOVERY_01']:
  grid={(p['prompt_tokens'],p['output_tokens']):p for p in points if p['stage']=='G2' and p['source']==source}
  if set(grid)!={(512,1),(512,32),(2048,1),(2048,32)}:continue
  T=lambda L,O:grid[L,O]['GPU_event']['median_ms'];MAD=lambda L,O:grid[L,O]['GPU_event']['MAD_ms']
  values={'Delta_prompt_1_ms':T(2048,1)-T(512,1),'Delta_prompt_32_ms':T(2048,32)-T(512,32),'Delta_generation_512_ms':T(512,32)-T(512,1),'Delta_generation_2048_ms':T(2048,32)-T(2048,1)};values['Interaction_ms']=values['Delta_prompt_32_ms']-values['Delta_prompt_1_ms']
  tests=[]
  for a,b in [((2048,1),(512,1)),((2048,32),(512,32)),((512,32),(512,1)),((2048,32),(2048,1))]:
   delta=T(*a)-T(*b);envelope=max(.05*min(T(*a),T(*b)),3*(MAD(*a)+MAD(*b)));tests.append({'a':a,'b':b,'delta_ms':delta,'descriptive_envelope_ms':envelope,'exceeds_envelope':abs(delta)>envelope})
  contrasts.append({'source':source,**values,'descriptive_difference_checks':tests})
 directions='NOT_ASSESSABLE'
 if len(contrasts)==2:
  keys=['Delta_prompt_1_ms','Delta_prompt_32_ms','Delta_generation_512_ms','Delta_generation_2048_ms','Interaction_ms'];directions='INPUT_DEPENDENT' if any((contrasts[0][k]>0)!=(contrasts[1][k]>0) for k in keys) else 'SAME_RECORDED_DIRECTIONS'
 if resource['status']=='GPU_PHASES_COMPLETE' and len(contrasts)==2:status='NATIVE_WORKLOAD_SENSITIVITY_COMPLETE' if any(t['exceeds_envelope'] for c in contrasts for t in c['descriptive_difference_checks']) else 'NO_STABLE_DIFFERENCE'
 elif resource['status']=='GPU_RESOURCE_DEFERRED':status='GPU_RESOURCE_DEFERRED'
 elif resource['status'] in ['BUDGET_STOP','ENGINEERING_STOP','IDENTITY_OR_INPUT_NO_GO']:status=resource['status']
 else:status='NATIVE_ONLY_SCOPED_PARTIAL'
 result={'status':status,'interpretation':'NATIVE_ONLY_WORKLOAD_CHARACTERIZATION','points':points,'G2_same_capacity_contrasts':contrasts,'cross_text_direction':directions,'phenomenon_classification':'SCIENTIFIC_POSITIVE_WORKLOAD_SENSITIVITY' if contrasts and any(t['exceeds_envelope'] for c in contrasts for t in c['descriptive_difference_checks']) else 'NO_STABLE_DIFFERENCE' if contrasts else 'NOT_MEASURED','hardware_headroom_or_projection_claims':0,'pure_prefill_or_decode_ITL_claims':0,'G1_used_as_G2_short_point':False,'limitations':['Natural workload amounts, KV sizes and graph dispatch all change; no hardware resource-only interpretation','G2 numerical scope is self-repeatability, no independent long-prompt mathematical oracle','A01 is discovery text validation, not sealed holdout','Graph manager dispatch counter has no semantic family mapping or profiler information']}
 (OUT/'ANALYSIS.json').write_text(json.dumps(result,indent=2)+'\n')
 fields=['stage','point','source','prompt_tokens','output_tokens','index','request_gpu_elapsed_ms','host_generate_wall_ms','output_token_ids_sha256','sampled_logprobs_sha256','numeric_scope','point_status']
 with (OUT/'FORMAL_SAMPLES.tsv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(samples)
 (OUT/'NUMERIC_AND_IDENTITY.json').write_text(json.dumps({'status':status,'G1':'See raw/G1.json if admitted; frozen reference exact-token/logprob checks','G2':'SCOPED_SELF_REPEATABILITY only if admitted and passed; no long-prompt external oracle','model_initializations':resource['GPU_model_initializations'],'formal_samples':len(samples),'completed_points':len(points),'input_receipt':'INPUT_RECEIPT.json','runtime_receipt':'SOURCE_AND_RUNTIME.json','all_completed_points_have5_formal':all(p['GPU_event']['formal_n']==5 for p in points)},indent=2)+'\n')
 print(json.dumps({'status':status,'formal_samples':len(samples),'contrasts':contrasts}))
 return result
if __name__=='__main__':analyze()
