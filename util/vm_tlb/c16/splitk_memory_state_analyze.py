#!/usr/bin/env python3
"""CPU-only analysis and review-pack emission for split-K memory-state interaction V1."""
import argparse
import csv
import hashlib
import json
import math
import shutil
import statistics
from pathlib import Path

import numpy as np

ROOT=Path('/data/c16/splitk_memory_state_interaction_v1')
REPO=Path('/home/huangrulin/workspace/worktrees/accel-sim-c16-splitk-memory-state-interaction-109-v1')
PACK=REPO/'docs/vm_tlb/review_packs/C16_SPLITK_MEMORY_STATE_INTERACTION_109_V1'
OPS=('up_proj','down_proj'); CELLS=('A_W','B_W','A_E','B_E')
EXPECTED={'up_proj':{'A':18944,'B':2368,'reduction':9472},'down_proj':{'A':3584,'B':448,'reduction':1792}}


def sha(path):
 h=hashlib.sha256()
 with open(path,'rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
 return h.hexdigest()


def load(path): return json.loads(Path(path).read_text())
def write_json(name,value): (PACK/name).write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
def write_tsv(name,fields,rows):
 with (PACK/name).open('w',newline='') as f:
  w=csv.DictWriter(f,delimiter='\t',fieldnames=fields,extrasaction='ignore',lineterminator='\n'); w.writeheader()
  for r in rows: w.writerow({k:('NA' if r.get(k) in (None,'') else r.get(k)) for k in fields})


def parse_ncu(path,operator,cell):
 rows=list(csv.reader(open(path,newline=''))); header,units=rows[0],rows[1]; out=[]
 for values in rows[2:]:
  if not values or not values[0] or len(values)!=len(header): continue
  d,u=dict(zip(header,values)),dict(zip(header,units))
  if not d.get('Kernel Name'): continue
  def number(key):
   s=d[key].replace(',',''); return float(s) if '.' in s else int(s)
  arm,state=cell.split('_'); name=d['Kernel Name']; kind='GEMM' if 'gemm_forward' in name else 'REDUCTION' if 'reduce_kernel' in name else 'OTHER'
  out.append({'operator':operator,'cell':cell,'arm':arm,'state':'WARM_SAME_ARM' if state=='W' else 'EVICT_CONDITIONED','kernel_order':len(out),'kernel_kind':kind,'kernel_name':name,'block_size':d['Block Size'],'grid_size':d['Grid Size'],'l1tex_bytes':int(number('l1tex__t_bytes.sum')),'lts_bytes':int(number('lts__t_bytes.sum')),'dram_bytes':int(number('dram__bytes.sum')),'duration_ns':int(number('gpu__time_duration.sum')),'registers_per_thread':int(number('launch__registers_per_thread')),'static_shared_bytes':int(number('launch__shared_mem_per_block_static')),'dynamic_shared_bytes':int(number('launch__shared_mem_per_block_dynamic')),'l1tex_unit':u['l1tex__t_bytes.sum'],'lts_unit':u['lts__t_bytes.sum'],'dram_unit':u['dram__bytes.sum'],'duration_unit':u['gpu__time_duration.sum']})
 return out


def validate_ncu(rows):
 for op in OPS:
  for cell in CELLS:
   rs=[r for r in rows if r['operator']==op and r['cell']==cell]; arm=cell[0]
   expected_count=2 if arm=='A' else 1
   if len(rs)!=expected_count or rs[0]['kernel_kind']!='GEMM': raise RuntimeError(f'NCU_KERNEL_COUNT_FAIL {op} {cell}')
   grid=int(rs[0]['grid_size'].strip('()').split(',')[0])
   if grid!=EXPECTED[op][arm]: raise RuntimeError(f'NCU_GRID_FAIL {op} {cell} {grid}')
   if arm=='A':
    red=int(rs[1]['grid_size'].strip('()').split(',')[0])
    if rs[1]['kernel_kind']!='REDUCTION' or red!=EXPECTED[op]['reduction']: raise RuntimeError(f'NCU_REDUCTION_FAIL {op} {cell}')
 return True


def stats(vals):
 return {'n':len(vals),'min_ms':min(vals),'median_ms':statistics.median(vals),'max_ms':max(vals),'mean_ms':statistics.mean(vals),'cv':statistics.pstdev(vals)/statistics.mean(vals)}


def bootstrap(samples,operator):
 by={(b,c):[r['ms'] for r in samples if r['operator']==operator and r['block']==b and r['cell']==c] for b in range(25) for c in CELLS}
 rng=np.random.default_rng(20260928); out=[]
 for _ in range(1000):
  chosen=rng.integers(0,25,size=25); meds={}
  for c in CELLS:
   vals=[v for b in chosen for v in by[(int(b),c)]]; meds[c]=float(np.median(vals))
  gain_w=1-meds['B_W']/meds['A_W']; gain_e=1-meds['B_E']/meds['A_E']
  out.append((gain_w,gain_e,gain_w-gain_e))
 arr=np.asarray(out)
 q=lambda col:[float(x) for x in np.quantile(arr[:,col],[.05,.5,.95])]
 return {'seed':20260928,'permutations':1000,'unit':'complete mirror block','gain_W_q05_q50_q95':q(0),'gain_E_q05_q50_q95':q(1),'state_interaction_q05_q50_q95':q(2)}


def profile_receipt(log):
 found=[]
 for line in Path(log).read_text(errors='replace').splitlines():
  line=line.strip()
  if line.startswith('{'):
   try:
    x=json.loads(line)
    if x.get('status')=='PASS_PROFILE': found.append(x)
   except json.JSONDecodeError: pass
 if not found: raise RuntimeError(f'PROFILE_RECEIPT_MISSING {log}')
 return found[-1]


def main():
 p=argparse.ArgumentParser(); p.add_argument('--pre-execution-commit',required=True); a=p.parse_args()
 run_id=(ROOT/'ACTIVE_RUN_ID').read_text().strip(); run=ROOT/run_id; raw=run/'raw'
 if not (raw/'LOCKED_CAMPAIGN_COMPLETE').is_file(): raise RuntimeError('LOCKED_CAMPAIGN_INCOMPLETE')
 qualification=load(raw/'correctness.json'); timing_recheck=load(raw/'timing_correctness_recheck.json'); launch=load(raw/'launch_audit.json')
 if not all(r['pass'] for r in qualification+timing_recheck) or launch['status']!='PASS': raise RuntimeError('QUALIFICATION_FAIL')
 samples=load(raw/'timing_samples.json')
 if len(samples)!=400: raise RuntimeError(f'TIMING_SAMPLE_COUNT_FAIL {len(samples)}')
 for op in OPS:
  for cell in CELLS:
   if sum(r['operator']==op and r['cell']==cell for r in samples)!=50: raise RuntimeError(f'CELL_SAMPLE_COUNT_FAIL {op} {cell}')
 ncu=[]; profile_receipts=[]
 for op in OPS:
  for cell in CELLS:
   ncu+=parse_ncu(raw/f'ncu_{op}_{cell}.csv',op,cell)
   pr=profile_receipt(raw/f'ncu_{op}_{cell}.log'); expected_calls=1 if cell.endswith('_E') else 0
   if pr['conditioner']['calls']!=expected_calls: raise RuntimeError(f'PROFILE_CONDITIONER_FAIL {op} {cell}')
   profile_receipts.append(pr)
 validate_ncu(ncu)

 cell_stats=[]; block_rows=[]; derived={}
 for op in OPS:
  stats_by={}
  for cell in CELLS:
   vals=[r['ms'] for r in samples if r['operator']==op and r['cell']==cell]; s=stats(vals); stats_by[cell]=s
   cell_stats.append({'record_type':'CELL','operator':op,'cell':cell,'arm':cell[0],'state':'WARM_SAME_ARM' if cell.endswith('_W') else 'EVICT_CONDITIONED',**s})
  gain_w=1-stats_by['B_W']['median_ms']/stats_by['A_W']['median_ms']; gain_e=1-stats_by['B_E']['median_ms']/stats_by['A_E']['median_ms']; interaction=gain_w-gain_e
  boot=bootstrap(samples,op); q=boot['state_interaction_q05_q50_q95']; resolved=(q[0]>0 and q[2]>0) or (q[0]<0 and q[2]<0)
  derived[op]={'gain_W':gain_w,'gain_E':gain_e,'state_interaction':interaction,'bootstrap':boot,'interaction_descriptively_resolved':resolved,'direction_persists':(gain_w>=0)==(gain_e>=0),'old_direction_expected':'B_FASTER' if op=='up_proj' else 'B_SLIGHTLY_FASTER'}
  cell_stats.append({'record_type':'DERIVED','operator':op,'cell':'GAINS','gain_W':gain_w,'gain_E':gain_e,'state_interaction':interaction,'bootstrap_interaction_p05':q[0],'bootstrap_interaction_median':q[1],'bootstrap_interaction_p95':q[2],'interaction_descriptively_resolved':resolved,'direction_persists':derived[op]['direction_persists']})
  for block in range(25):
   means={c:statistics.mean([r['ms'] for r in samples if r['operator']==op and r['block']==block and r['cell']==c]) for c in CELLS}
   gw=1-means['B_W']/means['A_W']; ge=1-means['B_E']/means['A_E']
   block_rows.append({'operator':op,'block':block,**{f'{c}_mean_ms':means[c] for c in CELLS},'gain_W':gw,'gain_E':ge,'state_interaction':gw-ge})

 ncu_summary={}
 for op in OPS:
  ncu_summary[op]={}
  for cell in CELLS:
   rs=[r for r in ncu if r['operator']==op and r['cell']==cell]
   ncu_summary[op][cell]={'kernel_count':len(rs),'reduction_present':any(r['kernel_kind']=='REDUCTION' for r in rs),'l1tex_bytes_total':sum(r['l1tex_bytes'] for r in rs),'lts_bytes_total':sum(r['lts_bytes'] for r in rs),'dram_bytes_total':sum(r['dram_bytes'] for r in rs),'duration_ns_total':sum(r['duration_ns'] for r in rs),'gemm':next({k:r[k] for k in ('l1tex_bytes','lts_bytes','dram_bytes','duration_ns')} for r in rs if r['kernel_kind']=='GEMM'),'reduction':next(({k:r[k] for k in ('l1tex_bytes','lts_bytes','dram_bytes','duration_ns')} for r in rs if r['kernel_kind']=='REDUCTION'),None)}
  ncu_summary[op]['state_deltas']={arm:{metric:ncu_summary[op][f'{arm}_E'][metric]-ncu_summary[op][f'{arm}_W'][metric] for metric in ('l1tex_bytes_total','lts_bytes_total','dram_bytes_total','duration_ns_total')} for arm in ('A','B')}

 resolved=[op for op in OPS if derived[op]['interaction_descriptively_resolved']]
 if resolved: primary='SPLIT_POLICY_BENEFIT_STATE_CONDITIONED_SCOPED'
 elif all(derived[op]['direction_persists'] for op in OPS): primary='SPLIT_POLICY_DIRECTION_PERSISTS_ACROSS_TESTED_STATES'
 else: primary='MEMORY_STATE_INTERACTION_UNRESOLVED'
 labels=[primary]
 if all(derived[op]['direction_persists'] for op in OPS) and 'SPLIT_POLICY_DIRECTION_PERSISTS_ACROSS_TESTED_STATES' not in labels: labels.append('SPLIT_POLICY_DIRECTION_PERSISTS_ACROSS_TESTED_STATES')
 if not resolved and 'MEMORY_STATE_INTERACTION_UNRESOLVED' not in labels: labels.append('MEMORY_STATE_INTERACTION_UNRESOLVED')

 PACK.mkdir(parents=True,exist_ok=True)
 manifest=load(raw/'SOURCE_AND_RUN_MANIFEST.pre_gpu.json'); manifest['status']='PASS_COMPLETED'; manifest['pre_execution_source_commit']=a.pre_execution_commit; manifest['gpu_identity']=(raw/'GPU_IDENTITY.txt').read_text().strip(); manifest['qualification_pass']=True; manifest['timing_samples']=len(samples); manifest['ncu_profiles']=8
 write_json('SOURCE_AND_RUN_MANIFEST.json',manifest)
 combined=[]
 for r in qualification: combined.append({'record_type':'CORRECTNESS',**r})
 for r in launch['rows']: combined.append({'record_type':'LAUNCH',**r,'grid':json.dumps(r['grid']),'block':json.dumps(r['block'])})
 write_tsv('CORRECTNESS_AND_LAUNCH.tsv',['record_type','operator','arm','order','kernel_kind','kernel_name','grid','block','registers_per_thread','static_shared_bytes','dynamic_shared_bytes','input_sha256','a_expected_sha256','a_observed_sha256','b_prior_sha256','b_observed_sha256','a_shape','b_shape','a_dtype','b_dtype','a_finite','b_finite','max_abs','mean_abs','relative_l2','changed_element_count','element_count','rtol','atol','a_exact_pass','b_tolerance_pass','pass'],combined)
 write_tsv('TIMING_SAMPLES.tsv',['operator','cell','arm','state','block','position','ms','conditioner_calls_before','conditioner_calls_after'],samples)
 write_tsv('TIMING_SUMMARY.tsv',['record_type','operator','cell','arm','state','n','min_ms','median_ms','max_ms','mean_ms','cv','gain_W','gain_E','state_interaction','bootstrap_interaction_p05','bootstrap_interaction_median','bootstrap_interaction_p95','interaction_descriptively_resolved','direction_persists'],cell_stats)
 write_tsv('TIMING_BLOCK_DELTAS.tsv',['operator','block','A_W_mean_ms','B_W_mean_ms','A_E_mean_ms','B_E_mean_ms','gain_W','gain_E','state_interaction'],block_rows)
 write_tsv('NCU_KERNEL_ROWS.tsv',['operator','cell','arm','state','kernel_order','kernel_kind','kernel_name','block_size','grid_size','l1tex_bytes','lts_bytes','dram_bytes','duration_ns','registers_per_thread','static_shared_bytes','dynamic_shared_bytes','l1tex_unit','lts_unit','dram_unit','duration_unit'],ncu)
 write_json('NCU_SUMMARY.json',{'contract':{'replay_mode':'application','cache_control':'none','metrics':['l1tex__t_bytes.sum','lts__t_bytes.sum','dram__bytes.sum'],'profiles':8,'tensor_attribution':'NOT_INFERRED'},'operators':ncu_summary,'profile_receipts':profile_receipts})
 final={'decision':primary,'allowed_labels':labels,'operator_results':derived,'ncu_state_summary':ncu_summary,'conditioner_qualified':True,'conditioner_timing_calls':load(raw/'timing_conditioner_receipt.json')['calls'],'warm_direction_consistent_with_old_observation':{'up_proj':derived['up_proj']['gain_W']>0,'down_proj':derived['down_proj']['gain_W']>0},'automatic_expansion':False,'claim_boundary':'Layer0 up/down M256 accepted split8/split1 under WARM_SAME_ARM versus one fixed 4xL2 EVICT_CONDITIONED preparation; not unique cache/L2/TLB/frequency causality, tensor attribution, full-model speedup, or Lane4 interpretation'}
 write_json('FINAL_DECISION.json',final)
 lock={'status':'PASS','lock_path':'/data/c16/locks/c16_gpu_campaign.lock','acquisition':'ONE_OUTER_GPU_CAMPAIGN','release':'RELEASED_AFTER_QUALIFICATION_TIMING_AND_8_NCU','start_utc':(raw/'GPU_LOCK_START_UTC.txt').read_text().strip(),'end_utc':(raw/'GPU_LOCK_END_UTC.txt').read_text().strip(),'gpu_identity':(raw/'GPU_IDENTITY.txt').read_text().strip(),'nvidia_smi_pre':{'path':str(raw/'NVIDIA_SMI_PRE.txt'),'sha256':sha(raw/'NVIDIA_SMI_PRE.txt')},'nvidia_smi_post':{'path':str(raw/'NVIDIA_SMI_POST.txt'),'sha256':sha(raw/'NVIDIA_SMI_POST.txt')},'clocks_power_persistence_driver_modified':False}
 write_json('GPU_LOCK_RECEIPT.json',lock)

 lines=['# Split-K memory-state interaction interpretation','',f'Primary bounded label: `{primary}`.','']
 for op in OPS:
  d=derived[op]; lines.append(f"- `{op}`: gain_W={100*d['gain_W']:.3f}%, gain_E={100*d['gain_E']:.3f}%, state_interaction={100*d['state_interaction']:.3f} percentage points; bootstrap interaction q05/q50/q95={[round(100*x,3) for x in d['bootstrap']['state_interaction_q05_q50_q95']]} pp.")
 lines += ['', 'WARM_SAME_ARM directions are compared only qualitatively with the prior ABBA protocol; medians are not spliced across protocols. EVICT_CONDITIONED changes target traffic/timing descriptively as listed in NCU_SUMMARY and TIMING_SUMMARY, but the conditioner may also affect TLB, clocks, scheduling or other execution state. GEMM and reduction rows remain separate. No counter is assigned to a specific tensor, and no unique L2/cache cause is claimed.','']
 (PACK/'INTERPRETATION.md').write_text('\n'.join(lines))
 (PACK/'README.md').write_text(f"# C16 split-K memory-state interaction V1\n\nRUN_ID: `{run_id}`\n\nDecision: `{primary}`. Accepted split8/split1 binaries, Layer0 up/down M256 only, eight preregistered cells, 50 CUDA-event samples per cell and eight bounded NCU profiles. The result is execution-state-conditioned and does not modify the frozen `OPERATOR_SPECIFIC_SPLIT_POLICY_ONLY` conclusion.\n")

 for op in OPS:
  for cell in CELLS:
   src=raw/f'ncu_{op}_{cell}.csv'; shutil.copy2(src,PACK/f'RAW_NCU_{op}_{cell}.csv')
 raw_rows=[]
 for q in sorted(raw.iterdir()):
  if q.is_file(): raw_rows.append({'artifact':q.name,'path':str(q),'bytes':q.stat().st_size,'sha256':sha(q),'committed_copy':f'RAW_NCU_{q.stem.removeprefix("ncu_")}.csv' if q.name.startswith('ncu_') and q.suffix=='.csv' else 'INDEX_ONLY'})
 write_tsv('RAW_INDEX.tsv',['artifact','path','bytes','sha256','committed_copy'],raw_rows)
 (PACK/'SHA256SUMS').unlink(missing_ok=True)
 (PACK/'SHA256SUMS').write_text('\n'.join(f'{sha(q)}  {q.name}' for q in sorted(PACK.iterdir()) if q.is_file() and q.name!='SHA256SUMS')+'\n')
 print(json.dumps({'status':'PASS_ANALYSIS','run_id':run_id,'decision':primary,'operator_results':derived},sort_keys=True))


if __name__=='__main__': main()
