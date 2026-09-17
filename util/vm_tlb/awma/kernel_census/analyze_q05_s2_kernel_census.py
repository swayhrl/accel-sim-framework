#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, json, math, re, sqlite3, statistics
from collections import Counter, defaultdict
from pathlib import Path

SQLITE=Path('/data/c16/awma/qwen25_s2_kernel_census_20260917T101100Z/qwen25_s2_census.sqlite')
OUT=Path('/data/c16/awma/qwen25_s2_kernel_census_20260917T101100Z/analysis')

def sha(p: Path) -> str:
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''): h.update(b)
 return h.hexdigest()

def percentile(xs, q):
 if not xs: return 0
 xs=sorted(xs); pos=(len(xs)-1)*q; lo=int(math.floor(pos)); hi=int(math.ceil(pos))
 return xs[lo] if lo==hi else xs[lo]+(xs[hi]-xs[lo])*(pos-lo)

def family(name: str) -> str:
 n=name.lower()
 if 'pytorch_flash::flash_fwd' in n: return 'PYTORCH_FLASH_FWD'
 if 'pytorch_flash::flash' in n: return 'PYTORCH_FLASH_OTHER'
 if 'internal::gemm' in n or 'gemm' in n: return 'CUBLAS_GEMM'
 if 'internal::gemvx' in n or 'gemv' in n: return 'CUBLAS_GEMV'
 if 'vectorized_elementwise_kernel' in n: return 'AT_NATIVE_VECTORIZED_ELEMENTWISE'
 if 'unrolled_elementwise_kernel' in n: return 'AT_NATIVE_UNROLLED_ELEMENTWISE'
 if 'elementwise_kernel' in n: return 'AT_NATIVE_ELEMENTWISE'
 if 'reduce_kernel' in n: return 'AT_NATIVE_REDUCE'
 if 'layer_norm' in n or 'rms_norm' in n: return 'NORM_KERNEL'
 if 'rotary' in n or 'rope' in n: return 'ROPE_KERNEL'
 if 'copy' in n or 'memcpy' in n: return 'COPY_KERNEL'
 return 'OTHER_EXACT_IMPLEMENTATION'

def semantic(name: str) -> str:
 n=name.lower()
 if 'pytorch_flash::flash' in n: return 'ATTENTION_CORE'
 if 'rotary' in n or 'rope' in n: return 'ROPE'
 if 'layer_norm' in n or 'rms_norm' in n: return 'NORM'
 if 'direct_copy' in n or 'copy_kernel' in n: return 'COPY_LAYOUT'
 if 'elementwise' in n or 'reduce_kernel' in n: return 'ELEMENTWISE'
 # GEMM/GEMV may be attention projection, MLP, or output; exact role is unproven.
 return 'UNKNOWN'

def main():
 OUT.mkdir(parents=True,exist_ok=True)
 c=sqlite3.connect(SQLITE)
 ids={i:v for i,v in c.execute('select id,value from StringIds')}
 ranges=[]
 for st,en,text in c.execute("select start,end,text from NVTX_EVENTS where text like 'C16_PHASE=%' order by start"):
  fields=dict(x.split('=',1) for x in text.split(';') if '=' in x)
  ranges.append({'start':st,'end':en,'phase':fields['C16_PHASE'],'step':fields.get('STEP',''),'label':text})
 assert len(ranges)==33 and ranges[0]['phase']=='PREFILL' and sum(x['phase']=='DECODE' for x in ranges)==32
 rows=[]
 query='select start,end,streamId,gridX,gridY,gridZ,blockX,blockY,blockZ,demangledName,shortName,mangledName from CUPTI_ACTIVITY_KIND_KERNEL order by start,end'
 for idx,r in enumerate(c.execute(query)):
  st,en,stream,gx,gy,gz,bx,by,bz,dem,short,mangled=r
  name=ids.get(dem) or ids.get(short) or ids.get(mangled) or 'UNKNOWN'
  overlaps=[(max(0,min(en,x['end'])-max(st,x['start'])),x) for x in ranges]
  overlap,rg=max(overlaps,key=lambda x:x[0])
  if overlap==0: phase='UNKNOWN'; step=''
  else: phase=rg['phase']; step=rg['step']
  rows.append({'global_launch_index':idx,'phase':phase,'decode_step':step,'start_ns':st,'end_ns':en,'duration_ns':en-st,'stream':stream,'grid':f'{gx},{gy},{gz}','block':f'{bx},{by},{bz}','exact_kernel_name':name,'demangled_kernel_name':name,'normalized_kernel_family':family(name),'semantic_category':semantic(name),'nvtx_overlap_ns':overlap})
 fields=list(rows[0])
 all_tsv=OUT/'ALL_KERNEL_LAUNCHES.tsv'
 with all_tsv.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields,delimiter='\t');w.writeheader();w.writerows(rows)
 inference=[r for r in rows if r['phase']!='UNKNOWN']
 def summarize(sub,scope,by,output):
  total_count=len(sub); total_dur=sum(r['duration_ns'] for r in sub)
  groups=defaultdict(list)
  for r in sub: groups[tuple(r[x] for x in by)].append(r)
  with output.open('w',newline='') as f:
   w=csv.writer(f,delimiter='\t');w.writerow(['scope',*by,'launch_count','launch_count_share','total_gpu_duration_ns','gpu_time_share','mean_ns','median_ns','min_ns','p25_ns','p75_ns','max_ns'])
   for k,vals in sorted(groups.items()):
    ds=[r['duration_ns'] for r in vals]
    w.writerow([scope,*k,len(vals),len(vals)/total_count if total_count else 0,sum(ds),sum(ds)/total_dur if total_dur else 0,statistics.mean(ds),statistics.median(ds),min(ds),percentile(ds,.25),percentile(ds,.75),max(ds)])
 scopes={'WHOLE_FROZEN_INFERENCE':inference,'PREFILL':[r for r in inference if r['phase']=='PREFILL'],'DECODE_TOTAL':[r for r in inference if r['phase']=='DECODE']}
 for step in range(1,33): scopes[f'DECODE_STEP_{step}']=[r for r in inference if r['decode_step']==str(step)]
 for scope,sub in scopes.items():
  summarize(sub,scope,['phase','decode_step'],OUT/f'_phase_{scope}.tsv')
  summarize(sub,scope,['semantic_category','normalized_kernel_family'],OUT/f'_family_{scope}.tsv')
  summarize(sub,scope,['semantic_category'],OUT/f'_semantic_{scope}.tsv')
 # combine all per-scope summaries after each was written independently
 for root,name in [('phase','PHASE_SUMMARY.tsv'),('family','KERNEL_FAMILY_SUMMARY.tsv'),('semantic','SEMANTIC_KERNEL_SUMMARY.tsv')]:
  target=OUT/name; chunks=[OUT/f'_{root}_{s}.tsv' for s in scopes]
  with target.open('w') as out:
   for i,p in enumerate(chunks):
    lines=p.read_text().splitlines()
    if i==0: out.write('\n'.join(lines)+'\n')
    else: out.write('\n'.join(lines[1:])+'\n')
    p.unlink()
 attention=[r for r in inference if r['semantic_category'].startswith('ATTENTION')]
 summarize(attention,'ATTENTION_RELATED',['phase','semantic_category','normalized_kernel_family'],OUT/'ATTENTION_KERNEL_SUMMARY.tsv')
 flashes=[r for r in inference if r['normalized_kernel_family']=='PYTORCH_FLASH_FWD']
 q05=next(r for r in flashes if r['phase']=='PREFILL')
 with (OUT/'FLASH_ATTENTION_OCCURRENCES.tsv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields,delimiter='\t');w.writeheader();w.writerows(flashes)
 same_prefill=[r for r in flashes if r['phase']=='PREFILL']
 ds=[r['duration_ns'] for r in same_prefill]
 q05_report={
  'q05_global_launch_index':q05['global_launch_index'],'q05_duration_ns':q05['duration_ns'],'q05_grid':q05['grid'],'q05_block':q05['block'],
  'exact_flash_fwd_launch_count':len(flashes),'prefill_flash_fwd_launch_count':len(same_prefill),'prefill_flash_duration_stats_ns':{'mean':statistics.mean(ds),'median':statistics.median(ds),'min':min(ds),'p25':percentile(ds,.25),'p75':percentile(ds,.75),'max':max(ds)},
  'same_grid_block_count':sum(r['grid']==q05['grid'] and r['block']==q05['block'] for r in same_prefill),
  'other_grid_block_variants':sorted({f"{r['grid']}|{r['block']}" for r in same_prefill if (r['grid'],r['block']) != (q05['grid'],q05['block'])}),
  'q05_single_launch_gpu_time_share_prefill':q05['duration_ns']/sum(r['duration_ns'] for r in scopes['PREFILL']),
  'flash_family_gpu_time_share_prefill':sum(r['duration_ns'] for r in same_prefill)/sum(r['duration_ns'] for r in scopes['PREFILL']),
  'attention_related_gpu_time_share_prefill':sum(r['duration_ns'] for r in attention if r['phase']=='PREFILL')/sum(r['duration_ns'] for r in scopes['PREFILL']),
  'layer_mapping':'LAYER_MAPPING_NOT_PROVEN',
 }
 j=(OUT/'Q05_REPRESENTATIVENESS.json'); j.write_text(json.dumps(q05_report,indent=2,sort_keys=True)+'\n')
 receipt={'sqlite':str(SQLITE),'sqlite_sha256':sha(SQLITE),'kernel_launches_total':len(rows),'inference_kernel_launches':len(inference),'unknown_phase_launches':len(rows)-len(inference),'nvtx_ranges':ranges,'driver_stdout_sha256':sha(SQLITE.parent/'driver.stdout'),'q05_reference':q05_report}
 (OUT/'RUN_RECEIPT.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
 (OUT/'SEMANTIC_RULES.md').write_text('ATTENTION_CORE: pytorch_flash::flash substring. ROPE/NORM/COPY_LAYOUT/ELEMENTWISE only for explicit implementation-name substrings. GEMM/GEMV and any uncertain operator are UNKNOWN. No transformer layer or Q/K/V/operator role is inferred from launch order.\n')
 idx={'all_kernel_launches_path':str(all_tsv),'sha256':sha(all_tsv),'size_bytes':all_tsv.stat().st_size,'rows':len(rows),'durable_destination':'PENDING_NODE164_TRANSFER'}
 (OUT/'ALL_KERNEL_LAUNCHES_INDEX.json').write_text(json.dumps(idx,indent=2,sort_keys=True)+'\n')
 for p in OUT.iterdir():
  if p.is_file() and p.name!='SHA256SUMS': pass
 with (OUT/'SHA256SUMS').open('w') as f:
  for p in sorted(x for x in OUT.iterdir() if x.is_file() and x.name!='SHA256SUMS'):
   f.write(f'{sha(p)}  {p.name}\n')
 print(json.dumps({'out':str(OUT),'q05':q05_report,'launches':len(rows),'inference':len(inference)},sort_keys=True))

if __name__=='__main__': main()
