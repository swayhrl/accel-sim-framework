#!/usr/bin/env python3
from __future__ import annotations
import csv,json,math,statistics,sys
from collections import defaultdict
from pathlib import Path

src=Path(sys.argv[1]);out=Path(sys.argv[2]);out.mkdir(parents=True,exist_ok=True)
rows=list(csv.DictReader(src.open(),delimiter='\t'))
for r in rows:
 r['global_launch_index']=int(r['global_launch_index']);r['duration_ns']=int(r['duration_ns'])

def pct(xs,q):
 xs=sorted(xs);p=(len(xs)-1)*q;lo=int(p);hi=math.ceil(p);return xs[lo] if lo==hi else xs[lo]+(xs[hi]-xs[lo])*(p-lo)
def key(r):return (r['phase'],r['normalized_kernel_family'],r['exact_kernel_name'],r['grid'],r['block'])
def occurrence(records):
 d=defaultdict(int)
 for r in sorted(records,key=lambda x:x['global_launch_index']):
  k=key(r);r['occurrence_index_within_phase_function_shape']=d[k];d[k]+=1
def subfamilies(records,phase,family):
 x=[dict(r) for r in records if r['phase']==phase and r['normalized_kernel_family']==family]
 occurrence(x);g=defaultdict(list)
 for r in x:g[key(r)].append(r)
 total=sum(r['duration_ns'] for r in x)
 phase_total=sum(r['duration_ns'] for r in records if r['phase']==phase)
 outrows=[]
 for k,v in sorted(g.items(),key=lambda kv:(-sum(r['duration_ns'] for r in kv[1]),kv[0])):
  ds=[r['duration_ns'] for r in v];steps=sorted({r['decode_step'] for r in v if r['decode_step']})
  outrows.append({'phase':k[0],'normalized_family':k[1],'exact_kernel_name':k[2],'grid':k[3],'block':k[4], 'launch_count':len(v),'launch_count_share_within_family':len(v)/len(x),'total_gpu_duration_ns':sum(ds),'gpu_time_share_within_family':sum(ds)/total,'gpu_time_share_within_phase':sum(ds)/phase_total,'mean_ns':statistics.mean(ds),'median_ns':statistics.median(ds),'p25_ns':pct(ds,.25),'p75_ns':pct(ds,.75),'min_ns':min(ds),'max_ns':max(ds),'decode_step_count':len(steps),'decode_steps':','.join(steps)})
 return x,outrows
def write_tsv(path,items):
 if not items: path.write_text('');return
 with path.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(items[0]),delimiter='\t');w.writeheader();w.writerows(items)
def choose(items,allrecords,idprefix,threshold=0):
 selected=[]
 for n,g in enumerate([x for x in items if x['gpu_time_share_within_family']>=threshold],1):
  candidates=[r for r in allrecords if key(r)==(g['phase'],g['normalized_family'],g['exact_kernel_name'],g['grid'],g['block'])]
  med=g['median_ns']; ref=min(candidates,key=lambda r:(abs(r['duration_ns']-med),r['global_launch_index']))
  selected.append({'candidate_id':f'{idprefix}_{n}','phase':g['phase'],'decode_step':ref['decode_step'] or 'NOT_APPLICABLE','exact_kernel_function':g['exact_kernel_name'],'normalized_family':g['normalized_family'],'grid':g['grid'],'block':g['block'],'reference_launch_index':ref['global_launch_index'],'occurrence_index_within_phase_function_shape':ref['occurrence_index_within_phase_function_shape'],'reference_duration_ns':ref['duration_ns'],'subfamily_launch_count':g['launch_count'],'subfamily_gpu_time_share_within_family':g['gpu_time_share_within_family'],'subfamily_gpu_time_share_within_phase':g['gpu_time_share_within_phase'],'decode_step_count':g['decode_step_count'],'operator_role':'UNKNOWN','layer':'UNKNOWN','status':'CANDIDATE_ONLY_NOT_CAPTURED'})
 return selected

prefill_gemm,pg=subfamilies(rows,'PREFILL','CUBLAS_GEMM')
decode_gemv,dg=subfamilies(rows,'DECODE','CUBLAS_GEMV')
decode_flash,df=subfamilies(rows,'DECODE','PYTORCH_FLASH_FWD')
prefill_flash=[dict(r) for r in rows if r['phase']=='PREFILL' and r['normalized_kernel_family']=='PYTORCH_FLASH_FWD'];occurrence(prefill_flash)
write_tsv(out/'PREFILL_GEMM_SUBFAMILIES.tsv',pg);write_tsv(out/'DECODE_GEMV_SUBFAMILIES.tsv',dg);write_tsv(out/'DECODE_FLASH_SUBFAMILIES.tsv',df)
pf=[]
for r in prefill_flash:
 pf.append({k:r[k] for k in ['phase','decode_step','global_launch_index','exact_kernel_name','normalized_kernel_family','grid','block','duration_ns','occurrence_index_within_phase_function_shape']})
write_tsv(out/'PREFILL_FLASH_10_OCCURRENCES.tsv',pf)
candidates=[]
candidates+=choose(pg,prefill_gemm,'PREFILL_GEMM_PRIMARY',threshold=max(x['gpu_time_share_within_family'] for x in pg))
candidates+=choose(dg,decode_gemv,'DECODE_GEMV_PRIMARY',threshold=max(x['gpu_time_share_within_family'] for x in dg))
# Keep each materially significant Decode Flash shape (>=10% family time); fallback top one.
sig=[x for x in df if x['gpu_time_share_within_family']>=.10]
candidates+=choose(sig or df[:1],decode_flash,'DECODE_FLASH_PRIMARY',threshold=0)
write_tsv(out/'TARGET_CANDIDATES.tsv',candidates)
cdir=out/'candidate_targets';cdir.mkdir(exist_ok=True)
for c in candidates:
 (cdir/(c['candidate_id']+'.json')).write_text(json.dumps({'model':'Qwen/Qwen2.5-0.5B-Instruct','revision':'7ae557604adf67be50417f59c2c2f167def9a775','scenario':'S2_TEXT','candidate_only_not_captured':True,**c},indent=2,sort_keys=True)+'\n')
(out/'NATIVE_TARGET_ALIGNMENT.md').write_text('NATIVE_TARGET_MATCH_NOT_PROVEN: this offline stage found no accepted Native PREFILL_HEAVY_GEMM manifest with exact function + grid + block + phase occurrence fields that can be joined to the selected census candidate. Duration or family similarity alone is not treated as proof.\n')
(out/'TARGET_SELECTION_RATIONALE.md').write_text('Candidates are selected by exact implementation+shape recurrence and GPU-time contribution, then representative duration (nearest median, earliest deterministic tie). No high-level operator role or layer is inferred from symbol/launch order.\n')
print(json.dumps({'prefill_gemm_subfamilies':len(pg),'decode_gemv_subfamilies':len(dg),'decode_flash_subfamilies':len(df),'candidates':candidates},sort_keys=True))
