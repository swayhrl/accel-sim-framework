#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import torch
from transformers import AutoModelForCausalLM,AutoTokenizer
from heads import HeadArms
from reference import MODEL,ROOT,load_rows
from full_generation import generation,compare_to_reference

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--arm',choices=['A0_DENSE_VENDOR','A1_DENSE_FUSED','A2_INDEXED_UNION','A3_RAGGED_DIRECT'],required=True)
    args=p.parse_args()
    cohort='C1_HETEROGENEOUS_DISCOVERY'
    rows=load_rows(cohort)
    tok=AutoTokenizer.from_pretrained(MODEL,local_files_only=True,padding_side='left')
    model=AutoModelForCausalLM.from_pretrained(MODEL,local_files_only=True,
      torch_dtype=torch.bfloat16,attn_implementation='sdpa').eval().to('cuda:0')
    head=HeadArms(model.get_output_embeddings().weight)
    with ThreadPoolExecutor(max_workers=1) as executor:
        torch.cuda.nvtx.range_push(f'R81_FULL_GENERATION_C1_{args.arm}')
        try:result=generation(model,head,tok,rows,args.arm,executor)
        finally:torch.cuda.nvtx.range_pop()
    passed,divergence=compare_to_reference(cohort,result)
    result['semantic_exact']=passed;result['first_divergence']=divergence
    out=ROOT/'raw/nsys'/cohort/args.arm
    out.mkdir(parents=True,exist_ok=True)
    (out/'PROFILE_CANARY_RECEIPT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'arm':args.arm,'semantic_exact':passed,'wall_ms_canary':result['wall_ms']}))
    if not passed:raise SystemExit(2)

if __name__=='__main__':main()
