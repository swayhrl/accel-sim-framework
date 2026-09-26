#!/usr/bin/env python3
import csv,hashlib,json
from pathlib import Path
ROOT=Path('/data/c16/awma/ai_translation_native_atlas_capture_20260926')
OUT=ROOT/'KERNEL_SELECTION_PREREG.tsv'
def read(p):return list(csv.DictReader(open(p),delimiter='\t'))
ll=read(ROOT/'llama_native/analysis/NATIVE_CENSUS.tsv'); om=read(ROOT/'olmoe_native/analysis/NATIVE_CENSUS.tsv')
choices=[
 ('L1',next(r for r in ll if r['phase']=='DECODE' and r['family']=='GEMV'),'DENSE_OTHER_FAMILY','NATIVE_TOP_TIME_GEMV'),
 ('L2',next(r for r in ll if r['phase']=='DECODE' and r['family']=='ATTENTION_LIKE'),'DENSE_OTHER_FAMILY','ATTENTION_LIKE_DIVERSITY'),
 ('M1',next(r for r in om if r['phase']=='DECODE' and r['family']=='GEMV'),'MOE_FAMILY','NATIVE_TOP_TIME_GEMV'),
 ('M2',next(r for r in om if r['phase']=='DECODE' and 'DeviceReduceSingleTileKernel' in r['function']),'MOE_FAMILY','MOE_ROUTING_REDUCTION_DIVERSITY')]
rows=[]
for tid,r,dim,why in choices:
 rows.append({'target_id':tid,'dimension':dim,'scenario':r['scenario'],'phase':r['phase'],'family':r['family'],'function':r['function'],'function_sha256':hashlib.sha256(r['function'].encode()).hexdigest(),'grid':r['grid'],'block':r['block'],'source_launch_count':r['launch_count'],'native_gpu_duration_ns':r['gpu_duration_ns'],'native_gpu_time_share':r['gpu_time_share'],'selection_reason':why,'address_behavior_observed_before_selection':'NO','simulator_result_observed_before_selection':'NO'})
with OUT.open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t');w.writeheader();w.writerows(rows)
h=hashlib.sha256(OUT.read_bytes()).hexdigest();(ROOT/'SELECTION_FREEZE_RECEIPT.json').write_text(json.dumps({'status':'KERNEL_SELECTION_FROZEN_BEFORE_ADDRESS_BEHAVIOR','sha256':h,'targets':[r['target_id'] for r in rows]},indent=2,sort_keys=True)+'\n')
print(json.dumps({'sha256':h,'targets':[r['target_id'] for r in rows]},sort_keys=True))
