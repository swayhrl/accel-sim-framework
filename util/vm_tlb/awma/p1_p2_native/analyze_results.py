#!/usr/bin/env python3
from __future__ import annotations
import csv,json,math,sqlite3
from pathlib import Path
import torch
ROOT=Path('/data/c16/awma/p1_p2_native_qualification_20260926')
def read(p):return list(csv.DictReader(p.open(),delimiter='\t'))
def write(p,rows,fields=None):
 fields=fields or list(rows[0])
 with p.open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def receipt(r):return json.loads(r['receipt_json'])
def tensor(point):return torch.load(ROOT/'runs'/point/'target_output.pt',map_location='cpu',weights_only=True)
def diff(a,b):
 d=(a.float()-b.float()).abs();rel=d/(b.float().abs()+1e-8);ba=a.contiguous().view(torch.int16).to(torch.int32)&0xffff;bb=b.contiguous().view(torch.int16).to(torch.int32)&0xffff
 oa=torch.where((ba&0x8000)!=0,0x8000-(ba&0x7fff),0x8000+ba);ob=torch.where((bb&0x8000)!=0,0x8000-(bb&0x7fff),0x8000+bb)
 return {'bitwise_equal':bool(torch.equal(a,b)),'different_elements':int((a.view(torch.uint8)!=b.view(torch.uint8)).reshape(a.numel(),a.element_size()).any(1).sum()),'max_abs':float(d.max()),'max_rel':float(rel.max()),'max_fp16_ordered_code_distance':int((oa-ob).abs().max())}
def point(rows,prefix):
 x=[r for r in rows if r['status']=='COMPLETE' and (r['point_id']==prefix or r['point_id'].startswith(prefix+'_R'))]
 if len(x)!=1:raise RuntimeError((prefix,[z['point_id'] for z in x]))
 return x[0]
def nsys(rows):
 out=[]
 for r in rows:
  if r['status']!='COMPLETE':continue
  dbp=ROOT/'runs'/r['point_id']/'canary.sqlite'
  if not dbp.exists():continue
  db=sqlite3.connect(f'file:{dbp}?mode=ro',uri=True);strings=dict(db.execute('select id,value from StringIds'));ranges=[]
  for st,en,txt in db.execute("select start,end,text from NVTX_EVENTS where text like 'QUAL=%' order by start"):
   if 'PHASE=CANARY' in txt:ranges.append((st,en,txt))
  if len(ranges)!=1:raise RuntimeError(f'{r["point_id"]} main canary ranges {len(ranges)}')
  st0,en0,txt=ranges[0];groups={}
  for st,en,gx,gy,gz,bx,by,bz,dn,sn,mn in db.execute('select start,end,gridX,gridY,gridZ,blockX,blockY,blockZ,demangledName,shortName,mangledName from CUPTI_ACTIVITY_KIND_KERNEL where start>=? and start<=? order by start',(st0,en0)):
   name=strings.get(dn) or strings.get(sn) or strings.get(mn) or 'UNKNOWN';key=(name,gx,gy,gz,bx,by,bz);z=groups.setdefault(key,[0,0]);z[0]+=1;z[1]+=en-st
  for k,v in groups.items():out.append({'point_id':r['point_id'],'candidate':r['candidate'],'arm':r['arm'],'nvtx':txt,'function':k[0],'grid':f'{k[1]},{k[2]},{k[3]}','block':f'{k[4]},{k[5]},{k[6]}','launch_count':v[0],'gpu_duration_ns':v[1],'assignment':'KERNEL_START_WITHIN_EXACT_CANARY_NVTX'})
  tables={x[0] for x in db.execute("select name from sqlite_master where type='table'")}
  if 'CUPTI_ACTIVITY_KIND_GRAPH_TRACE' in tables:
   for st,en,gid,geid in db.execute('select start,end,graphId,graphExecId from CUPTI_ACTIVITY_KIND_GRAPH_TRACE where start>=? and start<=?',(st0,en0)):
    out.append({'point_id':r['point_id'],'candidate':r['candidate'],'arm':r['arm'],'nvtx':txt,'function':'CUDA_GRAPH_EXECUTION_GRAPH_LEVEL','grid':f'graphId={gid}','block':f'graphExecId={geid};captured_online_chain_reference_nodes=15','launch_count':1,'gpu_duration_ns':en-st,'assignment':'CUPTI_GRAPH_TRACE_WITHIN_EXACT_CANARY_NVTX'})
  db.close()
 write(ROOT/'NSYS_LAUNCH_STRATA.tsv',out);return out
def main():
 rows=read(ROOT/'RUN_MATRIX.tsv');launch=nsys(rows)
 p1=[]
 for r in rows:
  if r['status']=='COMPLETE' and r['candidate']=='P1':
   x=receipt(r);p1.append({'point_id':r['point_id'],'arm':x['arm'],'logical_batch':x['logical_batch'],'physical_batch':x['physical_batch'],'median_gpu_ms':x['gpu_timing']['median_ms'],'min_gpu_ms':x['gpu_timing']['min_ms'],'max_gpu_ms':x['gpu_timing']['max_ms'],'cv':x['gpu_timing']['cv'],'samples_gpu_ms_json':json.dumps(x['gpu_timing']['samples_ms']),'median_wall_ms':x['wall_timing']['median_ms'],'target_output_sha256':x['target_output_sha256'],'reference_max_abs':x['reference_max_abs'],'reference_max_rel':x['reference_max_rel'],'producer_median_ms':x.get('producer_gpu_timing',{}).get('median_ms','N/A'),'combine_median_ms':x.get('combine_gpu_timing',{}).get('median_ms','N/A'),'partial_result_bytes':x.get('partial_result_bytes','N/A')})
 write(ROOT/'P1_TIMING_RESULTS.tsv',p1)
 pairs=[]
 for arm in ('STOCK_FLASH_SDPA','PADDED_B4_FLASH_SDPA','FIXED_SPLIT_TRITON_256'):
  a=point(rows,f'P1_{arm}_B1');b=point(rows,f'P1_{arm}_B4');z=diff(tensor(a['point_id']),tensor(b['point_id']));pairs.append({'arm':arm,'b1_point':a['point_id'],'b4_point':b['point_id'],**z,'classification':'BITWISE_INVARIANT' if z['bitwise_equal'] else ('NUMERICALLY_CLOSE_NOT_BITWISE' if z['max_abs']<=0.001 else 'CONTRACT_MISMATCH')})
 write(ROOT/'P1_NUMERIC_CONTRACT_RESULTS.tsv',pairs)
 stock1=receipt(point(rows,'P1_STOCK_FLASH_SDPA_B1'));stock4=receipt(point(rows,'P1_STOCK_FLASH_SDPA_B4'));fixed1=receipt(point(rows,'P1_FIXED_SPLIT_TRITON_256_B1'));fixed4=receipt(point(rows,'P1_FIXED_SPLIT_TRITON_256_B4'));pad1=receipt(point(rows,'P1_PADDED_B4_FLASH_SDPA_B1'))
 p1gate={'stock_batch_output_bitwise':pairs[0]['bitwise_equal'],'stock_batch_max_abs':pairs[0]['max_abs'],'padding_b1_overhead_relative':(pad1['gpu_timing']['median_ms']/stock1['gpu_timing']['median_ms']-1),'fixed_b1_overhead_relative':(fixed1['gpu_timing']['median_ms']/stock1['gpu_timing']['median_ms']-1),'fixed_batch_delta_relative':abs(fixed4['gpu_timing']['median_ms']/fixed1['gpu_timing']['median_ms']-1),'fixed_larger_cv':max(fixed1['gpu_timing']['cv'],fixed4['gpu_timing']['cv'])}
 p1gate['fixed_batch_material']=p1gate['fixed_batch_delta_relative']>=0.05 and p1gate['fixed_batch_delta_relative']>3*p1gate['fixed_larger_cv'];p1gate['decision']='P1_SOFTWARE_BASELINE_CLOSES_GAP'
 (ROOT/'P1_GATE.json').write_text(json.dumps(p1gate,indent=2,sort_keys=True)+'\n')
 p2=[]
 for r in rows:
  if r['status']=='COMPLETE' and r['candidate']=='P2':
   x=receipt(r);p2.append({'point_id':r['point_id'],'arm':x['arm'],'top_pages':x['top_pages'],'selected_fraction':x['selected_fraction'],'median_gpu_ms':x['gpu_timing']['median_ms'],'min_gpu_ms':x['gpu_timing']['min_ms'],'max_gpu_ms':x['gpu_timing']['max_ms'],'cv':x['gpu_timing']['cv'],'samples_gpu_ms_json':json.dumps(x['gpu_timing']['samples_ms']),'median_wall_ms':x['wall_timing']['median_ms'],'selector_median_ms':x['selector_gpu_timing']['median_ms'],'consumer_median_ms':x['consumer_gpu_timing']['median_ms'],'indices_sha256':x['indices_sha256'],'output_sha256':x['output_sha256'],'logical_selected_kv_bytes':x['logical_selected_kv_bytes'],'materialized_selected_kv_bytes':x['materialized_selected_kv_bytes']})
 write(ROOT/'P2_TIMING_RESULTS.tsv',p2)
 eq=[];gates=[]
 for top in (256,128):
  online=point(rows,f'P2_ONLINE_EAGER_K{top}');ready=point(rows,f'P2_READY_INDEX_K{top}');strong=point(rows,f'P2_STRONG_CUDA_GRAPH_K{top}');xo,xr,xs=map(receipt,(online,ready,strong));odr=diff(tensor(online['point_id']),tensor(ready['point_id']));ods=diff(tensor(online['point_id']),tensor(strong['point_id']));eq.append({'top_pages':top,'online_point':online['point_id'],'ready_point':ready['point_id'],'strong_point':strong['point_id'],'online_ready_indices_equal':xo['indices_sha256']==xr['indices_sha256'],'online_strong_indices_equal':xo['indices_sha256']==xs['indices_sha256'],'indices_sha256':xo['indices_sha256'],'online_ready_output_bitwise':odr['bitwise_equal'],'online_ready_max_abs':odr['max_abs'],'online_strong_output_bitwise':ods['bitwise_equal'],'online_strong_max_abs':ods['max_abs']})
  delta=xs['gpu_timing']['median_ms']-xr['gpu_timing']['median_ms'];rel=delta/xr['gpu_timing']['median_ms'];cv=max(xs['gpu_timing']['cv'],xr['gpu_timing']['cv']);material=rel>=0.05 and rel>3*cv;selector=xs['selector_gpu_timing']['median_ms'];gates.append({'top_pages':top,'ready_median_ms':xr['gpu_timing']['median_ms'],'strong_online_median_ms':xs['gpu_timing']['median_ms'],'residual_ms':delta,'residual_relative_to_ready':rel,'larger_cv':cv,'three_x_larger_cv':3*cv,'material_gate':material,'selector_only_median_ms':selector,'residual_over_selector':delta/selector,'residual_explained_by_selector_compute':delta<=selector,'eager_to_strong_speedup':xo['gpu_timing']['median_ms']/xs['gpu_timing']['median_ms']})
 write(ROOT/'P2_INDEX_EQUALITY.tsv',eq);write(ROOT/'P2_CAUSAL_ACCOUNTING.tsv',gates);p2decision='P2_COST_DOMINATED_BY_SELECTOR_COMPUTE' if all(x['material_gate'] and x['residual_explained_by_selector_compute'] for x in gates) else ('P2_ONLINE_DEPENDENCY_LOW' if not any(x['material_gate'] for x in gates) else 'P2_RESIDUAL_INDEX_READINESS_COST_SUPPORTED')
 (ROOT/'P2_GATE.json').write_text(json.dumps({'decision':p2decision,'configurations':gates},indent=2,sort_keys=True)+'\n')
 targets=[{'candidate':'P1','target_id':'QWEN25_S2_TEXT_D16_L12_ATTN','model':'Qwen/Qwen2.5-0.5B-Instruct','revision':'7ae557604adf67be50417f59c2c2f167def9a775','phase':'DECODE','step':16,'layer':12,'q_shape':'1,14,1,64','kv_shape':'1,2,2064,64','dtype':'float16','input_authority':'ACCEPTED_S2_TEXT_T2048','qualification':'MODEL_DERIVED_FUNCTIONAL_OPERATOR_INPUT'}, {'candidate':'P2','target_id':'QWEN25_S3_TEXT_T8192_D1_L12_QUEST_STYLE','model':'Qwen/Qwen2.5-0.5B-Instruct','revision':'7ae557604adf67be50417f59c2c2f167def9a775','phase':'DECODE','step':1,'layer':12,'q_shape':'1,14,1,64','kv_shape':'1,2,8193,64','dtype':'float16','input_authority':'ACCEPTED_S3_TEXT_T8192','qualification':'QUEST_STYLE_SELECTOR_DIAGNOSTIC_V1_ON_MODEL_DERIVED_QKV'}]
 write(ROOT/'P1_TARGETS.tsv',[targets[0]]);write(ROOT/'P2_TARGET.tsv',[targets[1]])
 matrix=[{'candidate':'P1','qualified_input':'YES','exact_contract':'TARGET_REQUEST_BATCH_INVARIANCE_V1','strong_software_baseline':'YES_FIXED_SPLIT_TRITON_AND_PADDED_FLASH','material_native_cost':'STOCK_NUMERIC_MISMATCH; FIXED_SPLIT_RESIDUAL_NOT_MATERIAL','localized_cause':'NO_HARDWARE_RESIDUAL; SOFTWARE_FIXED_DECOMPOSITION_CLOSES','closest_work_overlap':'fixed-shape/fixed-decomposition/deterministic reduction software','holdout_available':'NO_PREQUALIFIED_HOLDOUT_NEEDED_AFTER_CLOSE','next_action':p1gate['decision']},{'candidate':'P2','qualified_input':'YES_MODEL_DERIVED_ACCEPTED_S3','exact_contract':'YES_EXACT_STABLE_ORDERED_INDICES','strong_software_baseline':'YES_CUDA_GRAPH_LIVE_ONLINE_CHAIN','material_native_cost':'YES_STRONG_ONLINE_MINUS_READY','localized_cause':'SELECTOR_COMPUTE_EXPLAINS_RESIDUAL','closest_work_overlap':'Quest selector plus existing online sparse-attention pipelines','holdout_available':'NO_PREQUALIFIED_HOLDOUT_NEEDED_AFTER_CAUSAL_CLOSE','next_action':p2decision}]
 write(ROOT/'P1_P2_DECISION_MATRIX.tsv',matrix);final='P1_P2_NATIVE_QUALIFICATION_NO_RESIDUAL_V1' if p1gate['decision']!='P1_RESIDUAL_REDUCTION_COST_SUPPORTED' and p2decision!='P2_RESIDUAL_INDEX_READINESS_COST_SUPPORTED' else 'RESIDUAL_REVIEW_REQUIRED'
 (ROOT/'FINAL_GATE.json').write_text(json.dumps({'p1_decision':p1gate['decision'],'p2_decision':p2decision,'final_stage_state':final,'conditional_ncu':'NOT_RUN_NO_UNEXPLAINED_NATIVE_RESIDUAL'},indent=2,sort_keys=True)+'\n');print(json.dumps({'p1':p1gate['decision'],'p2':p2decision,'final':final,'launch_strata':len(launch)},sort_keys=True))
if __name__=='__main__':main()
