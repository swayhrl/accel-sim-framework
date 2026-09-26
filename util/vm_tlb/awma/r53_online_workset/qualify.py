#!/usr/bin/env python3
from __future__ import annotations
import csv,fcntl,gzip,hashlib,json,sys,types
from pathlib import Path
ROOT=Path('/data/c16/awma/r53_online_workset_qualification_20260927');MODEL=ROOT/'model/Fast_dLLM_v2_1.5B_25093b6f';SRC=ROOT/'source/Fast-dLLM/v2';sys.path[:0]=[str(SRC),str(Path(__file__).parent)]
import torch
from transformers import AutoModelForCausalLM,AutoTokenizer
import generation_functions
from engine import generate,tsha
def jsha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def prepare(rows):
 ids=[torch.tensor([json.loads(x['token_ids_json'])],device='cuda') for x in rows];lens=torch.tensor([x.shape[1] for x in ids],device='cuda');mx=max(x.shape[1] for x in ids);batch=torch.cat([torch.cat([x,torch.full((1,mx-x.shape[1]),151665,device='cuda',dtype=torch.long)],1) for x in ids]);return batch,lens
def outinfo(out,tok,rows):
 z=[]
 for i in range(len(rows)):
  t=out[i].cpu();text=tok.decode(t,skip_special_tokens=True);z.append({'request_id':rows[i]['canonical_id'],'token_sha256':tsha(t),'text_sha256':hashlib.sha256(text.encode()).hexdigest(),'tokens':t.tolist(),'text':text})
 return z
def main():
 req=json.loads((ROOT/'selected_requests.json').read_text());lock=open('/data/c16/locks/c16_gpu_campaign.lock','a+');fcntl.flock(lock,fcntl.LOCK_EX)
 try:
  torch.manual_seed(0);torch.cuda.set_device(0);tok=AutoTokenizer.from_pretrained(MODEL,trust_remote_code=True,local_files_only=True);model=AutoModelForCausalLM.from_pretrained(MODEL,trust_remote_code=True,local_files_only=True,torch_dtype=torch.bfloat16).eval().to('cuda:0');model.mdm_sample=types.MethodType(generation_functions.Fast_dLLM_QwenForCausalLM.batch_sample,model);all_ledger=[];summ=[];eq=[]
  for domain in ('GSM8K','HumanEval'):
   rows=req[domain][:4];ids,lens=prepare(rows);rids=[x['canonical_id'] for x in rows]
   official=model.mdm_sample(ids.clone(),tokenizer=tok,block_size=32,max_new_tokens=512,small_block_size=8,min_len=int(lens.min()),seq_len=lens.clone(),mask_id=151665,threshold=.9,stop_token=151645,use_block_cache=True,top_p=.95,temperature=0.0)
   results={};
   for arm in ('A0','A1_PACKED','A1_SAFE_BUCKET'):
    out,ledger,traj,stats,completion=generate(model,tok,ids.clone(),lens.clone(),rids,arm=arm,record=True)
    for x in ledger:x['domain']=domain;x['arm']=arm
    all_ledger+=ledger;info=outinfo(out,tok,rows);results[arm]={'outputs':info,'traj':traj,'stats':stats,'completion':completion};summ.append({'domain':domain,'arm':arm,**stats,'trajectory_events':len(traj),'trajectory_sha256':jsha(traj),'outputs_sha256':jsha(info)})
   oi=outinfo(official,tok,rows);official_match=all(a['token_sha256']==b['token_sha256'] for a,b in zip(oi,results['A0']['outputs']))
   for arm in ('A1_PACKED','A1_SAFE_BUCKET'):
    traj_match=results['A0']['traj']==results[arm]['traj'];out_match=all(a['token_sha256']==b['token_sha256'] and a['text_sha256']==b['text_sha256'] for a,b in zip(results['A0']['outputs'],results[arm]['outputs']));eq.append({'domain':domain,'a1_arm':arm,'official_a0_output_exact':official_match,'a0_a1_trajectory_exact':traj_match,'a0_a1_final_tokens_exact':out_match,'a0_trajectory_sha256':jsha(results['A0']['traj']),'a1_trajectory_sha256':jsha(results[arm]['traj']),'a0_outputs_sha256':jsha(results['A0']['outputs']),'a1_outputs_sha256':jsha(results[arm]['outputs']),'status':'PASS' if official_match and traj_match and out_match else 'FAIL'})
   (ROOT/f'qualification_{domain}.json').write_text(json.dumps({'official':oi,**results},indent=2,sort_keys=True,ensure_ascii=False)+'\n')
  fields=['domain','arm','request_id','logical_step','block_idx','subblock_idx','cohort_id','active_request_count','request_active','request_finished','mask_count_current_request','cohort_mask_count','cohort_full_refresh_decision','request_has_current_subblock_work','input_token_rows_executed','logits_rows_materialized','cache_epoch','cache_action','commit_positions','commit_token_ids','forced_commit_positions','stop_transition','graph_bucket_if_any','evidence_class','notes','next_block_seed_token']
  with gzip.open(ROOT/'LEGAL_WORK_LEDGER.tsv.gz','wt',newline='') as f:w=csv.DictWriter(f,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(all_ledger)
  with (ROOT/'LEGAL_WORK_SUMMARY.tsv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(summ[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(summ)
  with (ROOT/'A0_A1_SEMANTIC_EQUIVALENCE.tsv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(eq[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(eq)
  print(json.dumps({'semantic':eq,'summary':summ},sort_keys=True))
 finally:fcntl.flock(lock,fcntl.LOCK_UN);lock.close()
if __name__=='__main__':main()
