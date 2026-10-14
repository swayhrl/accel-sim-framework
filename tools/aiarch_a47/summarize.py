"""CPU analysis of paired native measurements; never starts device work."""
import json,pathlib,statistics,math
from budget_io import ROOT
import numpy as np
rows=[]
for p in sorted((ROOT/'private_raw').glob('process_*_timing.jsonl')):
 for l in p.read_text().splitlines():rows.append(json.loads(l))
fields=['GPU_resident_sync_host_search_seconds','CPU_H2D_search_D2H_wall_seconds'];out={'status':'ACTUAL_NATIVE_PAIRED_MEASUREMENTS','processes':{},'batches':{},'raw_run_count':len(rows),'queries_per_run':2048,'not_a_pure_kernel_timer':True,'B256_amortized_not_single_request_latency':True}
for b in [1,256]:
 bout={}
 for field in fields:
  logs=[];proc=[]
  for process in [0,1,2]:
   r=[x for x in rows if x['B']==b and x['process']==process];assert len(r)==40
   pairs=[]
   for block in range(10):
    a=[x['values'][field] for x in r if x['block']==block and x['arm']=='A'];z=[x['values'][field] for x in r if x['block']==block and x['arm']=='B'];assert len(a)==len(z)==2
    av=statistics.mean(a);bv=statistics.mean(z);pairs.append({'block':block,'A_seconds_2048':av,'B_seconds_2048':bv,'B_over_A':bv/av,'B_minus_A_seconds':bv-av})
   la=np.array([math.log(x['B_over_A']) for x in pairs]);logs.append(la)
   points={}
   for arm in ['A','B']:
    vals=[x['values'][field] for x in r if x['arm']==arm];median=statistics.median(vals)
    points[arm]={'runs':len(vals),'median_seconds_2048':median,'median_batch_wall_seconds':median/(2048/b),'median_amortized_seconds_per_query':median/2048,'throughput_queries_per_second':2048/median,'min_seconds_2048':min(vals),'max_seconds_2048':max(vals),'sample_stdev_seconds_2048':statistics.stdev(vals)}
   proc.append({'process':process,'points':points,'paired_blocks':pairs,'paired_geomean_B_over_A':float(np.exp(la.mean()))})
  rng=np.random.default_rng(20261014);boot=[]
  for repeat in range(5000):
   chosen=rng.integers(0,3,3);draw=np.concatenate([logs[i][rng.integers(0,10,10)] for i in chosen]);boot.append(float(np.exp(draw.mean())))
  ratios=[p['paired_geomean_B_over_A'] for p in proc];ci=np.quantile(boot,[.025,.975]).tolist();ratio=float(np.exp(np.concatenate(logs).mean()))
  bout[field]={'per_process':proc,'paired_geomean_B_over_A':ratio,'hierarchical_process_then_paired_block_bootstrap_95pct':ci,'bootstrap_replicates':5000,'stable_B_faster_observed':all(x<1 for x in ratios) and ci[1]<1,'stable_A_faster_observed':all(x>1 for x in ratios) and ci[0]>1,'no_query_level_independence_assumed':True}
 out['batches'][str(b)]=bout
(ROOT/'timing_summary.json').write_text(json.dumps(out,indent=2)+'\n')
print('PAIRED_SUMMARY',json.dumps({b:{f:(v['paired_geomean_B_over_A'],v['hierarchical_process_then_paired_block_bootstrap_95pct']) for f,v in x.items()} for b,x in out['batches'].items()}))
