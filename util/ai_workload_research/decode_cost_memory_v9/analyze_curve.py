"""Independent CPU curve/identity/statistical analysis;no CUDA."""
from pathlib import Path
import json,hashlib,statistics,random,csv,gzip
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'docs/ai_workload_research/runs/QWEN_DECODE_COST_MEMORY_MECHANISM_109_V9'
def H(x):return hashlib.sha256(x).hexdigest()
def D(x):return H(json.dumps(x,sort_keys=True,separators=(',',':')).encode())
def stats(v):
 m=statistics.median(v);return dict(n=len(v),median_ms=m,MAD_ms=statistics.median(abs(x-m) for x in v),minimum_ms=min(v),maximum_ms=max(v),values_ms=v,relative_MAD=statistics.median(abs(x-m) for x in v)/m)
def fit(x,y):
 xm=statistics.mean(x);ym=statistics.mean(y);b=sum((a-xm)*(v-ym) for a,v in zip(x,y))/sum((a-xm)**2 for a in x);a=ym-b*xm
 res=[v-a-b*n for n,v in zip(x,y)]
 return dict(a_ms=a,b_ms_per_generated_step=b,residual_ms=res,RMSE_ms=(statistics.mean(r*r for r in res))**.5,maximum_abs_residual_ms=max(abs(r) for r in res))
def main():
 master=json.loads((OUT/'raw/CURVE.json').read_text());journal=OUT/'raw/CURVE_records.jsonl'
 public_text=journal.read_text() if journal.exists() else gzip.decompress(journal.with_suffix(journal.suffix+'.gz').read_bytes()).decode()
 public=[json.loads(x) for x in public_text.splitlines()]
 returned={x['index']:x for x in public if x['event']=='RETURNED_ALL_REQUESTS'};valid={x['index']:x for x in public if x['event']=='VALIDATION'}
 private_lines=(OUT/'.private/CURVE/completions.jsonl').read_text().splitlines(keepends=True);private=[json.loads(x) for x in private_lines]
 inputs=json.loads((OUT/'.private/inputs.json').read_text());source_map={D(v):k.removesuffix('_512') for k,v in inputs.items()}
 completions=0;lookup={}
 for sample,line,secret in zip(master['samples'],private_lines,private):
  idx=sample['index'];record=returned[idx];assert H(line.encode())==sample['private_record_sha256']
  assert H((json.dumps(record,separators=(',',':'),allow_nan=False)+'\n').encode())==sample['public_record_sha256']
  assert valid[idx]['status']=='PASS_RUNTIME_VALID' and not valid[idx]['formal_compile_capture']
  assert record['fullgraph_replay_count']==record['output_tokens_each']-1
  assert record['active_compiled_Qwen2Model'];assert len(record['outputs'])==len(secret['outputs'])==(2 if sample['mode']=='B2' else 1)
  for pub,pr in zip(record['outputs'],secret['outputs']):
   src=source_map[D(pr['returned_prompt_token_ids'])];assert src==pub['source']==pr['source']
   assert len(pr['completions'])==1;c=pr['completions'][0];assert len(c['tokens'])==record['output_tokens_each'] and c['logprobs']==[]
   assert D(c['tokens'])==pub['token_sha256'][0] and D(pr['returned_prompt_token_ids'])==pub['prompt_sha256']
   completions+=1
   if sample['role']=='FORMAL':lookup[(sample['mode'],sample['output_tokens_each'],sample['round'],src)]=c['tokens']
 formals=[s for s in master['samples'] if s['role']=='FORMAL'];lengths=[1,2,4,8,16,32];modes={}
 rng=random.Random(0)
 rounds=sorted({s['round'] for s in formals});draws=[[rng.choice(rounds) for _ in rounds] for _ in range(2000)]
 slopes={}
 for mode in ['A00','A01','B2']:
  points={};allx=[];ally=[]
  for n in lengths:
   rows=[s for s in formals if s['mode']==mode and s['output_tokens_each']==n];assert len(rows)>=5
   points[str(n)]=dict(GPU=stats([s['request_gpu_elapsed_ms'] for s in rows]),Host=stats([s['host_synchronized_request_ms'] for s in rows]),Host_call=stats([s['host_generate_call_ms'] for s in rows]),
      drift_last2_minus_first2_ms=statistics.median([s['request_gpu_elapsed_ms'] for s in rows[-2:]])-statistics.median([s['request_gpu_elapsed_ms'] for s in rows[:2]]))
   allx += [n-1]*len(rows);ally += [s['request_gpu_elapsed_ms'] for s in rows]
  medianfit=fit([n-1 for n in lengths],[points[str(n)]['GPU']['median_ms'] for n in lengths]);allfit=fit(allx,ally)
  adjacent=[dict(N_low=a,N_high=b,ms_per_step=(points[str(b)]['GPU']['median_ms']-points[str(a)]['GPU']['median_ms'])/(b-a)) for a,b in zip(lengths,lengths[1:])]
  boots=[]
  for draw in draws:
   xs=[];ys=[]
   for ri in draw:
    for s in formals:
     if s['mode']==mode and s['round']==ri:xs.append(s['output_tokens_each']-1);ys.append(s['request_gpu_elapsed_ms'])
   boots.append(fit(xs,ys)['b_ms_per_generated_step'])
  slopes[mode]=boots
  boots=sorted(boots)
  modes[mode]=dict(points=points,all_formal_OLS=allfit,point_median_OLS=medianfit,adjacent_slopes=adjacent,
     anchored_31step_ms=points['32']['GPU']['median_ms']-points['1']['GPU']['median_ms'],
     slope_round_bootstrap_95_percentile_ms=[boots[int(.025*len(boots))],boots[int(.975*len(boots))]],
     uncertainty_scope='2000pairedroundresamples,seed0,n5;conditionaldescriptiveinterval,notcausalconfidence')
 ratio=modes['B2']['all_formal_OLS']['b_ms_per_generated_step']/statistics.mean(modes[m]['all_formal_OLS']['b_ms_per_generated_step'] for m in ['A00','A01'])
 bs=sorted(slopes['B2'][i]/statistics.mean([slopes['A00'][i],slopes['A01'][i]]) for i in range(2000))
 v8=json.loads((OUT/'.private/V8_LP_NONE_REFERENCES.json').read_text());comparisons=[];batch=[]
 for mode,source in [('A00','TRAIN_A_DISCOVERY_00'),('A01','TRAIN_A_DISCOVERY_01'),('B2','TRAIN_A_DISCOVERY_00'),('B2','TRAIN_A_DISCOVERY_01')]:
  for ri in rounds:
   ref=lookup[(mode,32,ri,source)]
   for n in lengths:
    ids=lookup[(mode,n,ri,source)];prefix=next((j for j,(a,b) in enumerate(zip(ids,ref)) if a!=b),len(ids))
    comparisons.append(dict(mode=mode,source=source,N=n,round=ri,prefix_of_same_mode_N32=ids==ref[:n],common_prefix_tokens=prefix))
   for n in [1,32]:
    point={'A00':('P1','P4'),'A01':('P2','P5'),'B2':('P3','P6')}[mode][n==32]
    ids=lookup[(mode,n,ri,source)];old=v8[point+':'+source]['tokens']
    comparisons.append(dict(mode=mode,source=source,N=n,round=ri,V8_LP_NONE_token_exact=ids==old))
 for source,mode in [('TRAIN_A_DISCOVERY_00','A00'),('TRAIN_A_DISCOVERY_01','A01')]:
  for ri in rounds:
   for n in lengths:
    a=lookup[(mode,n,ri,source)];b=lookup[('B2',n,ri,source)];prefix=next((j for j,(x,y) in enumerate(zip(a,b)) if x!=y),n)
    batch.append(dict(source=source,N=n,round=ri,tokens_exact=a==b,first_divergence=None if a==b else prefix,common_prefix_tokens=prefix))
 result=dict(grade='OBSERVED',status='NATIVE_CURVE_COMPLETE',formal_samples=len(formals),all_requests=len(master['samples']),actual_completions=completions,
   modes=modes,slope_ratio_B2_over_mean_B1=ratio,slope_ratio_pairedround_bootstrap95=[bs[50],bs[1950]],adaptive_decision=master['adaptive_decision'],
   all_compile_capture_formals_clear=True,logprobs='UNOBSERVED_NONE_PATH_NOT_NUMERIC_PASS',runtime=master['runtime'],
   input_and_token_checks=dict(all_source_mapping_valid=True,all_lengths_correct=True,comparisons=comparisons,B1_B2=batch),
   conditional_weight_bytes_per_step=6171394048,actual_DRAM_bytes_not_inferred=True)
 (OUT/'CURVE_ANALYSIS.json').write_text(json.dumps(result,indent=2)+'\n')
 with (OUT/'FORMAL_SAMPLES.tsv').open('w',newline='') as f:
  fields=['index','point','mode','output_tokens_each','round','block','request_gpu_elapsed_ms','host_generate_call_ms','host_synchronized_request_ms','fullgraph_replay_count','status']
  writer=csv.DictWriter(f,fieldnames=fields,delimiter='\t',lineterminator='\n');writer.writeheader()
  for row in formals:writer.writerow({k:row.get(k) for k in fields})
 print(json.dumps(dict(samples=len(formals),requests=len(master['samples']),completions=completions,curves={mode:{n:p['GPU']['median_ms'] for n,p in v['points'].items()} for mode,v in modes.items()},
  fits={mode:{k:v[k] for k in ['all_formal_OLS','point_median_OLS','adjacent_slopes','slope_round_bootstrap_95_percentile_ms']} for mode,v in modes.items()},R=ratio,ratio95=result['slope_ratio_pairedround_bootstrap95'],all_B1_B2_tokens_exact=all(x['tokens_exact'] for x in batch))))
if __name__=='__main__':main()
