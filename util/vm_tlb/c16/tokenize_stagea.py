#!/usr/bin/env python3
"""Pinned CPU-only chat-template tokenization of frozen natural input bytes."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from pathlib import Path

os.environ['HF_HUB_OFFLINE']='1'
os.environ['TRANSFORMERS_OFFLINE']='1'

import jinja2
import tokenizers
import transformers
from transformers import AutoTokenizer


MODELS={
    'QWEN_BF16':('qwen2.5-3b-instruct','aa8e72537993ba99e69dfaafa59ed015b17504d1'),
    'QWEN_AWQ':('qwen2.5-3b-instruct-awq','3559b226e8ce77211e2c1bd7ddfb7686fec4d6dd'),
    'OLMOE':('olmoe-1b-7b-0125-instruct','b89a7c4bc24fb9e55ce2543c9458ce0ca5c4650e'),
    'GRANITE':('granite-3.1-1b-a400m-instruct','0da7a48b0276d500ce5922fd2b33944091fc6c09'),
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_ids(ids: list[int]) -> bytes:
    return json.dumps(ids,separators=(',',':')).encode('utf-8')


def tokenize_prefix(tok,text: str,target: int) -> tuple[list[int],int,int,str]:
    def encode(prefix: str) -> list[int]:
        ids=tok.apply_chat_template([{'role':'user','content':prefix}],tokenize=True,
                                    add_generation_prompt=True)
        if not isinstance(ids,list) or any(not isinstance(x,int) for x in ids):
            raise AssertionError('unexpected chat template token type')
        return ids
    full=encode(text)
    if len(full)<=target:
        return full,len(text),len(full),'SOURCE_EXHAUSTED_BELOW_TARGET' if len(full)<target else 'EXACT_TARGET'
    lo=0;hi=len(text)
    best_ids=encode('')
    if len(best_ids)>target:
        raise AssertionError('chat template exceeds target')
    while lo<hi:
        mid=(lo+hi+1)//2
        current=encode(text[:mid])
        if len(current)<=target:
            lo=mid;best_ids=current
        else:
            hi=mid-1
    if lo<len(text) and len(encode(text[:lo+1]))<=target:
        raise AssertionError('nonmonotone adjacent tokenization; stop instead of guessing prefix')
    return best_ids,lo,len(full),'PREFIX_BISECTION_AT_OR_BELOW_TARGET'


def write_tsv(path: Path,rows: list[dict]) -> None:
    with path.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n')
        w.writeheader();w.writerows(rows)


def build(args) -> None:
    frozen=json.loads(args.input_manifest.read_bytes())
    metadata=json.loads(args.model_metadata.read_bytes())['models']
    out=args.out;out.mkdir(parents=True,exist_ok=True)
    receipt_rows=[]
    selected=MODELS if args.only is None else {key:MODELS[key] for key in args.only}
    for key,(slug,revision) in selected.items():
        directory=(args.olmoe_tokenizer if key=='OLMOE' else
                   args.granite_tokenizer if key=='GRANITE' else
                   args.download_root/slug/revision)
        info=metadata[key]
        if info['revision']!=revision:
            raise AssertionError('revision mismatch')
        for name in ('tokenizer.json','tokenizer_config.json','config.json'):
            if sha((directory/name).read_bytes())!=info['small_files'][name]['sha256']:
                raise AssertionError(f'tokenizer/config SHA mismatch {key}/{name}')
        tok=AutoTokenizer.from_pretrained(str(directory),local_files_only=True,use_fast=True,trust_remote_code=False)
        template=getattr(tok,'chat_template',None)
        if not template:
            raise AssertionError('missing pinned chat template '+key)
        template_sha=sha(template.encode('utf-8'))
        for source in frozen['entries']:
            input_bytes=(args.input_root/source['relative_path']).read_bytes()
            if sha(input_bytes)!=source['utf8_sha256'] or len(input_bytes)!=source['byte_count']:
                raise AssertionError('frozen source SHA mismatch '+source['source_text_id'])
            text=input_bytes.decode('utf-8')
            target=16384 if source['source']=='PG-19' else 512
            ids,prefix_chars,full_count,status=tokenize_prefix(tok,text,target)
            prefix_bytes=len(text[:prefix_chars].encode('utf-8'))
            encoded=canonical_ids(ids)
            rel=Path('token_ids')/key/(source['source_text_id']+'.json')
            path=out/rel;path.parent.mkdir(parents=True,exist_ok=True)
            path.write_bytes(encoded+b'\n')
            receipt_rows.append(dict(model_key=key,model_revision=revision,tokenizer_revision=revision,
                                     tokenizer_class=type(tok).__name__,
                                     tokenizer_json_sha256=info['small_files']['tokenizer.json']['sha256'],
                                     tokenizer_config_sha256=info['small_files']['tokenizer_config.json']['sha256'],
                                     chat_template_sha256=template_sha,
                                     transformers_version=transformers.__version__,
                                     tokenizers_version=tokenizers.__version__,jinja2_version=jinja2.__version__,
                                     source_text_id=source['source_text_id'],source_utf8_sha256=source['utf8_sha256'],
                                     source_byte_count=len(input_bytes),target_context_tokens=target,
                                     full_source_templated_token_count=full_count,
                                     prefix_utf8_byte_count=prefix_bytes,prompt_token_count=len(ids),
                                     truncate_rule_result=status,token_ids_sha256=sha(encoded),
                                     token_id_file_sha256=sha(encoded+b'\n'),
                                     token_ids_relative_path=str(rel).replace('\\','/'),
                                     model_max_position_embeddings=info['config'].get('max_position_embeddings','UNKNOWN'),
                                     model_output_generated='false'))
        print('TOKENIZER_PASS',key,len(frozen['entries']),flush=True)
    write_tsv(out/'TOKENIZATION_RECEIPTS.tsv',receipt_rows)
    qwen_bf16={r['source_text_id']:r for r in receipt_rows if r['model_key']=='QWEN_BF16'}
    qwen_awq={r['source_text_id']:r for r in receipt_rows if r['model_key']=='QWEN_AWQ'}
    if qwen_bf16 and qwen_awq:
        for source_id,bf16 in qwen_bf16.items():
            awq=qwen_awq[source_id]
            if (bf16['token_ids_sha256'],bf16['prompt_token_count'])!=(awq['token_ids_sha256'],awq['prompt_token_count']):
                raise AssertionError('Qwen BF16/AWQ tokenizer identity mismatch '+source_id)
    batch_specs=[('MP03_B4',['TRAIN_A_DISCOVERY_00','TRAIN_A_DISCOVERY_01','TRAIN_A_DISCOVERY_02','TRAIN_A_DISCOVERY_03']),
                 ('MP04_B16',['TRAIN_A_DISCOVERY_00']+[f'TRAIN_B_SEALED_{i:02}' for i in range(1,16)])]
    audit=[]
    for batch,ids in batch_specs if qwen_bf16 else []:
        counts=[int(qwen_bf16[source_id]['prompt_token_count']) for source_id in ids]
        full=[int(qwen_bf16[source_id]['full_source_templated_token_count']) for source_id in ids]
        gap=max(counts)-min(counts)
        flag='BATCH_SHAPE_CONTROL_HAS_CONTEXT_MIX' if gap>32 or min(counts)<480 else 'BATCH_CONTEXT_LENGTHS_NEAR_UNIFORM'
        for pos,source_id in enumerate(ids):
            row=qwen_bf16[source_id]
            audit.append(dict(batch_id=batch,position=pos,source_text_id=source_id,
                              source_utf8_sha256=row['source_utf8_sha256'],
                              source_byte_count=row['source_byte_count'],
                              full_source_templated_token_count=row['full_source_templated_token_count'],
                              prompt_token_count=row['prompt_token_count'],
                              batch_min_prompt_tokens=min(counts),batch_max_prompt_tokens=max(counts),
                              batch_prompt_token_range=gap,
                              batch_full_source_token_range=max(full)-min(full),
                              context_mix_flag=flag,
                              rule='flag if prompt range >32 or min <480;no prompt substitution'))
    if audit:
        write_tsv(out/'BATCH_INPUT_LENGTH_AUDIT.tsv',audit)
    print('COMPLETE',len(receipt_rows),'tokenization rows',len(audit),'batch rows',flush=True)


def main() -> None:
    p=argparse.ArgumentParser()
    p.add_argument('--download-root',type=Path,required=True)
    p.add_argument('--olmoe-tokenizer',type=Path,required=True)
    p.add_argument('--granite-tokenizer',type=Path,required=True)
    p.add_argument('--input-root',type=Path,required=True)
    p.add_argument('--input-manifest',type=Path,required=True)
    p.add_argument('--model-metadata',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--only',nargs='+',choices=list(MODELS))
    build(p.parse_args())


if __name__=='__main__':
    main()
