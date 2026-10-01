#!/usr/bin/env python3
"""CPU-only pinned metadata/source audit; never fetches model weight bytes."""
from __future__ import annotations

import argparse
import hashlib
import json
import urllib.parse
import urllib.request
from pathlib import Path


MODELS={
    'QWEN_BF16':('Qwen/Qwen2.5-3B-Instruct','aa8e72537993ba99e69dfaafa59ed015b17504d1'),
    'QWEN_AWQ':('Qwen/Qwen2.5-3B-Instruct-AWQ','3559b226e8ce77211e2c1bd7ddfb7686fec4d6dd'),
    'OLMOE':('allenai/OLMoE-1B-7B-0125-Instruct','b89a7c4bc24fb9e55ce2543c9458ce0ca5c4650e'),
    'GRANITE':('ibm-granite/granite-3.1-1b-a400m-instruct','0da7a48b0276d500ce5922fd2b33944091fc6c09'),
}
VLLM_COMMIT='ced6857afa0ea7b2e3f0846a62e1394e90f15607'
VLLM_TAG='v0.30.0'
SOURCE_PATHS={
    'qwen2':'vllm/model_executor/models/qwen2.py',
    'olmoe':'vllm/model_executor/models/olmoe.py',
    'granitemoe':'vllm/model_executor/models/granitemoe.py',
    'auto_awq':'vllm/model_executor/layers/quantization/auto_awq.py',
    'marlin_utils':'vllm/model_executor/layers/quantization/utils/marlin_utils.py',
    'flash_attn':'vllm/v1/attention/backends/flash_attn.py',
    'cmake':'CMakeLists.txt',
}
MARKERS={
    'qwen2':['MergedColumnParallelLinear','SiluAndMul','QKVParallelLinear'],
    'olmoe':['FusedMoE','OlmoeForCausalLM'],
    'granitemoe':['FusedMoE','GraniteMoeForCausalLM'],
    'auto_awq':['AWQ','zero_point','group_size'],
    'marlin_utils':['SM89','awq'],
    'flash_attn':['FlashAttention'],
    'cmake':['8.9','MARLIN'],
}


def get(url: str) -> bytes:
    request=urllib.request.Request(url,headers={'User-Agent':'C16-CPU-metadata-preflight/1.0'})
    with urllib.request.urlopen(request,timeout=40) as response:
        return response.read()


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def dump(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,indent=2,sort_keys=True,ensure_ascii=False)+'\n',encoding='utf-8')


def audit_models() -> dict:
    result={}
    for key,(repo,revision) in MODELS.items():
        api=f'https://huggingface.co/api/models/{repo}/revision/{revision}?blobs=true'
        model=json.loads(get(api))
        if model.get('sha')!=revision:
            raise AssertionError((repo,model.get('sha'),revision))
        siblings=model.get('siblings',[])
        weights=[]
        for entry in siblings:
            name=entry['rfilename']
            if name.endswith('.safetensors'):
                weights.append(dict(path=name,size_bytes=entry.get('size'),sha256=entry.get('lfs',{}).get('sha256')))
        if not weights or any(not x['size_bytes'] or not x['sha256'] for x in weights):
            raise AssertionError(f'missing pinned weight metadata: {repo}')
        base=f'https://huggingface.co/{repo}/resolve/{revision}'
        small={}
        names={x['rfilename'] for x in siblings}
        for name in ('config.json','tokenizer_config.json','tokenizer.json','model.safetensors.index.json'):
            if name in names:
                payload=get(f'{base}/{name}')
                small[name]=dict(sha256=sha(payload),size_bytes=len(payload))
                if name=='config.json':
                    config=json.loads(payload)
        result[key]=dict(repository=repo,revision=revision,tokenizer_revision=revision,
                         api_url=api,private=model.get('private'),gated=model.get('gated'),
                         license=model.get('cardData',{}).get('license','UNKNOWN'),
                         license_name=model.get('cardData',{}).get('license_name','UNKNOWN'),
                         weight_shards=weights,weight_total_bytes=sum(x['size_bytes'] for x in weights),
                         small_files=small,config=config,
                         all_sibling_paths=sorted(names),
                         inventory_status='REMOTE_PINNED_METADATA_ONLY_NO_WEIGHT_DOWNLOAD')
    return dict(schema='C16_REMOTE_MODEL_METADATA_V1',models=result)


def audit_runtime() -> dict:
    result={}
    for key,path in SOURCE_PATHS.items():
        url=f'https://raw.githubusercontent.com/vllm-project/vllm/{VLLM_COMMIT}/{path}'
        body=get(url)
        code=body.decode('utf-8')
        result[key]=dict(path=path,url=url,sha256=sha(body),bytes=len(body),
                         markers={marker:marker in code for marker in MARKERS[key]})
    return dict(schema='C16_RUNTIME_SOURCE_AUDIT_V1',candidate='vllm-project/vllm',tag=VLLM_TAG,
                commit=VLLM_COMMIT,source_files=result,
                installed_109_binary='UNKNOWN_NOT_AUDITED',
                SM89_compilation='TO_BE_CONFIRMED_BY_109_CANARY',
                exact_attention_backend='TO_BE_CONFIRMED_BY_109_CANARY',
                exact_AWQ_linear_backend='TO_BE_CONFIRMED_BY_109_CANARY',
                exact_MoE_expert_backend='TO_BE_CONFIRMED_BY_109_CANARY')


def main() -> None:
    p=argparse.ArgumentParser()
    p.add_argument('--out',type=Path,required=True)
    args=p.parse_args()
    dump(args.out/'REMOTE_MODEL_METADATA.json',audit_models())
    dump(args.out/'RUNTIME_SOURCE_AUDIT.json',audit_runtime())
    print('pinned model metadata and runtime source audited without weight download')


if __name__=='__main__':
    main()
