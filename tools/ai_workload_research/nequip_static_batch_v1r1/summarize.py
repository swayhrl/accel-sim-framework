"""CPU-only post-observation statistics from all raw paired blocks; no sample filtering."""
import os,pathlib,json,csv,statistics,hashlib
import numpy as np
root=pathlib.Path(os.environ['TASK_DATA']);raw=root/'raw';pack=pathlib.Path('docs/ai_workload_research/review_packs/AI_ARCH_NEQUIP_STATIC_BATCH_DISCOVERY_109_V1R1');pack.mkdir(parents=True,exist_ok=True)
conditions=['N-C2','N-G2','N-G4','N-G8'];samples=[]
for proc in range(3):
 checks=json.loads((raw/f'formal_{proc}_checks.json').read_text());assert checks['status']=='PASS' and checks['timing_samples']==48;assert all(x['exact_multiset_equal'] for x in checks['edge_checks']);assert all(x['pass'] for x in checks['numeric_checks']);assert checks['cache_before_timing']==checks['cache_after_timing']
 with (raw/f'timing_process_{proc}.tsv').open() as f:
  delimiter=',' if ',' in f.readline() else '\t';f.seek(0)
  for row in csv.DictReader(f,delimiter=delimiter):samples.append({k:(int(v) if k not in ['condition'] else v) for k,v in row.items()})
assert len(samples)==144 and len({(r['process'],r['block'],r['condition']) for r in samples})==144
for proc in range(3):
 for block in range(12):
  rows=sorted([r for r in samples if r['process']==proc and r['block']==block],key=lambda r:r['order']);shift=(proc+block)%4;assert [r['condition'] for r in rows]==conditions[shift:]+conditions[:shift]
  for r in rows:assert r['frames']==32 and r['atoms']==2048 and r['batches']==(16 if r['condition'] in ['N-C2','N-G2'] else 8 if r['condition']=='N-G4' else 4) and r['wall_ns']>0
samples.sort(key=lambda r:(r['process'],r['block'],r['order']))
with (pack/'TIMING_SAMPLES.tsv').open('w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=list(samples[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(samples)
medians=[]
for proc in range(3):
 for cond in conditions:
  v=np.array([r['wall_ns'] for r in samples if r['process']==proc and r['condition']==cond],dtype=np.float64);assert len(v)==12;median=float(np.median(v));mad=float(np.median(np.abs(v-median)));medians.append({'process':proc,'condition':cond,'samples':12,'median_group_wall_ns':median,'MAD_group_wall_ns':mad,'median_per_structure_ns':median/32,'median_throughput_structures_s':32e9/median,'min_group_wall_ns':float(v.min()),'max_group_wall_ns':float(v.max())})
with (pack/'PROCESS_SUMMARY.tsv').open('w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=list(medians[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(medians)
paired_rows=[];comparisons=[];rng=np.random.default_rng(20261013)
for base,candidate in [('N-C2','N-G2'),('N-G2','N-G4'),('N-G2','N-G8')]:
 ratios=np.zeros((3,12));reductions=np.zeros((3,12));label=base+'/'+candidate
 for proc in range(3):
  for block in range(12):
   a=next(r['wall_ns'] for r in samples if r['process']==proc and r['block']==block and r['condition']==base);b=next(r['wall_ns'] for r in samples if r['process']==proc and r['block']==block and r['condition']==candidate);ratios[proc,block]=a/b;reductions[proc,block]=1-b/a;paired_rows.append({'comparison':label,'process':proc,'block':block,'base_wall_ns':a,'candidate_wall_ns':b,'speed_ratio_Tbase_over_Tcandidate':a/b,'time_reduction_1_minus_Tcandidate_over_Tbase':1-b/a})
 boots=np.empty(10000)
 for i in range(10000):boots[i]=np.median(np.concatenate([ratios[p,rng.integers(0,12,12)] for p in range(3)]))
 lo,hi=np.quantile(boots,[.025,.975]);process_ratios=np.median(ratios,axis=1);consistent=bool(np.all(process_ratios>1) or np.all(process_ratios<1));resolved=consistent and (lo>1 or hi<1)
 comparisons.append({'comparison':label,'paired_blocks':36,'median_paired_speed_ratio':float(np.median(ratios)),'median_paired_time_reduction':float(np.median(reductions)),'paired_ratio_MAD':float(np.median(np.abs(ratios-np.median(ratios)))),'process_median_ratios':process_ratios.tolist(),'bootstrap_ratio_95pct_low':float(lo),'bootstrap_ratio_95pct_high':float(hi),'bootstrap_seed':20261013,'bootstrap_replicates':10000,'bootstrap_method':'Resample12 complete paired blocks with replacement within each fixed process stratum; median of36 ratios. Describes observed run fluctuations, no population inference.','stable_direction_all_processes':consistent,'resolved_response_for_this_workload':bool(resolved)})
with (pack/'PAIRED_SAMPLES.tsv').open('w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=list(paired_rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(paired_rows)
with (pack/'PAIRED_SUMMARY.tsv').open('w',newline='',encoding='utf-8') as f:
 keys=[k for k in comparisons[0] if k not in ['process_median_ratios','bootstrap_method']];w=csv.DictWriter(f,fieldnames=keys,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows({k:r[k] for k in keys} for r in comparisons)
all_diagnostics=[]
for proc in range(3):all_diagnostics+=json.loads((raw/f'diagnostics_{proc}.json').read_text())
assert len(all_diagnostics)==132 and all(r['process']==2 for r in all_diagnostics)
for c in conditions:assert {r['sweep'] for r in all_diagnostics if r['condition']==c}=={0,1,2}
with (pack/'DIAGNOSTIC_STAGES.tsv').open('w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=list(all_diagnostics[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(all_diagnostics)
summary={'status':'PASS_ALL_RAW_SAMPLES_AND_GATES_CLOSED','samples':144,'per_condition_samples':36,'fresh_processes':3,'blocks_per_process':12,'sample_filtering':False,'raw_timing_format':'Comma-separated raw files retain historical .tsv suffix; review-pack TIMING_SAMPLES.tsv is normalized TSV, raw bytes unchanged','per_process':medians,'paired_comparisons':comparisons,'overall_condition_median_wall_ns':{c:float(np.median([r['wall_ns'] for r in samples if r['condition']==c])) for c in conditions},'diagnostic_rows':132,'diagnostic_total_sweeps_per_condition':3,'diagnostic_stream_basis':'Fixed ALCHEMI scoped_torch_warp_stream uses current Torch CUDA stream; same-stream events surround neighbor/model only in diagnostic sweeps, outside main timing.','diagnostic_interpretation':'Intervals are instrumented auxiliary observations, not additive critical-path weights or hardware attribution.'}
(pack/'STATISTICAL_SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8');(raw/'POST_OBSERVATION_STATISTICAL_SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps({k:v for k,v in summary.items() if k!='per_process'},indent=2))
