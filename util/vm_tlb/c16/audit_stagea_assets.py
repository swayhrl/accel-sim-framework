#!/usr/bin/env python3
"""Independent CPU-only durable model asset and safetensors metadata closure."""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from collections import Counter
from pathlib import Path

from audit_local_assets import audit as audit_existing_assets


STAGEA={
    'QWEN_BF16':('qwen2.5-3b-instruct','aa8e72537993ba99e69dfaafa59ed015b17504d1','QWEN_BF16_ASSET_RECEIPT.json'),
    'QWEN_AWQ':('qwen2.5-3b-instruct-awq','3559b226e8ce77211e2c1bd7ddfb7686fec4d6dd','QWEN_AWQ_ASSET_RECEIPT.json'),
}


def sha_file(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(8*1024*1024),b''):
            h.update(chunk)
    return h.hexdigest()


def tensor_header(path: Path) -> dict:
    with path.open('rb') as f:
        head=f.read(8)
        if len(head)!=8:
            raise AssertionError('short safetensors header')
        length=struct.unpack('<Q',head)[0]
        if length<=0 or length>32*1024*1024:
            raise AssertionError('invalid safetensors header length')
        body=f.read(length)
    value=json.loads(body)
    tensor={name:info for name,info in value.items() if name!='__metadata__'}
    payload_size=path.stat().st_size-8-length
    if not tensor or max(x['data_offsets'][1] for x in tensor.values())>payload_size:
        raise AssertionError('invalid safetensors offsets')
    for info in tensor.values():
        a,b=info['data_offsets']
        if not 0<=a<b<=payload_size:
            raise AssertionError('invalid tensor byte range')
    return dict(tensors=tensor,payload_bytes=payload_size,header_bytes=length)


def audit_qwen(key: str,root: Path,remote: dict) -> dict:
    slug,revision,_=STAGEA[key]
    target=root/slug/revision
    if not target.is_dir():
        raise AssertionError(f'missing durable target {target}')
    receipt_path=target/'DOWNLOAD_RECEIPT.json'
    download=json.loads(receipt_path.read_bytes())
    model=remote['models'][key]
    if download['repository']!=model['repository'] or download['revision']!=revision:
        raise AssertionError('download revision mismatch')
    expected=set(model['all_sibling_paths'])
    if {x['path'] for x in download['files']}!=expected:
        raise AssertionError('download sibling inventory mismatch')
    actual={p.relative_to(target).as_posix() for p in target.rglob('*') if p.is_file()}
    if actual!=expected|{'DOWNLOAD_RECEIPT.json'}:
        raise AssertionError(f'unexpected/missing durable files {actual^expected}')
    verified=[]
    for entry in download['files']:
        file=target/entry['path']
        if file.stat().st_size!=entry['size_bytes'] or sha_file(file)!=entry['sha256']:
            raise AssertionError('durable file not byte-exact '+entry['path'])
        weight=next((x for x in model['weight_shards'] if x['path']==entry['path']),None)
        if weight and (entry['size_bytes'],entry['sha256'])!=(weight['size_bytes'],weight['sha256']):
            raise AssertionError('weight LFS authority mismatch')
        if entry['path'] in model['small_files'] and entry['sha256']!=model['small_files'][entry['path']]['sha256']:
            raise AssertionError('small-file pinned SHA mismatch')
        verified.append(entry)
    headers={x['path']:tensor_header(target/x['path']) for x in model['weight_shards']}
    tensor_sets={name:set(info['tensors']) for name,info in headers.items()}
    if key=='QWEN_BF16':
        index=json.loads((target/'model.safetensors.index.json').read_bytes())['weight_map']
        if set(index)!=set().union(*tensor_sets.values()):
            raise AssertionError('BF16 weight map tensor closure')
        if any(name not in tensor_sets[shard] for name,shard in index.items()):
            raise AssertionError('BF16 weight map shard closure')
        index_status='PINNED_SAFETENSORS_INDEX_EXACT'
    else:
        if len(headers)!=1 or (target/'model.safetensors.index.json').exists():
            raise AssertionError('AWQ expected single-file safetensors')
        index_status='SINGLE_FILE_HEADER_INDEX_NO_SEPARATE_INDEX'
    all_tensors={name:info for h in headers.values() for name,info in h['tensors'].items()}
    if len(all_tensors)!=sum(len(h['tensors']) for h in headers.values()):
        raise AssertionError('duplicate tensor name across shards')
    dtype=dict(sorted(Counter(x['dtype'] for x in all_tensors.values()).items()))
    quant=model['config'].get('quantization_config')
    awq={}
    if key=='QWEN_AWQ':
        if not quant or (quant['bits'],quant['group_size'],quant['zero_point'],quant['version'])!=(4,128,True,'gemm'):
            raise AssertionError('AWQ quantization identity changed')
        for role in ('qweight','qzeros','scales'):
            selected={n:x for n,x in all_tensors.items() if n.split('.')[-1]==role}
            if not selected:
                raise AssertionError('missing AWQ '+role)
            awq[role]=dict(tensor_count=len(selected),dtype_histogram=dict(sorted(Counter(x['dtype'] for x in selected.values()).items())),
                           exemplar_name=sorted(selected)[0],exemplar_shape=selected[sorted(selected)[0]]['shape'])
    return dict(schema='C16_STAGEA_DURABLE_MODEL_ASSET_RECEIPT_V1',status='PASS',model_key=key,
                repository=model['repository'],revision=revision,durable_root=str(target),
                download_receipt_sha256=sha_file(receipt_path),file_count=len(verified),
                total_bytes=sum(x['size_bytes'] for x in verified),
                weight_total_bytes=sum(x['size_bytes'] for x in verified if x['path'].endswith('.safetensors')),
                files=verified,config_sha256=model['small_files']['config.json']['sha256'],
                tokenizer_revision=revision,
                tokenizer_json_sha256=model['small_files'].get('tokenizer.json',{}).get('sha256','NOT_PRESENT'),
                safetensors_index_status=index_status,tensor_count=len(all_tensors),dtype_histogram=dtype,
                tensor_header_bytes={name:h['header_bytes'] for name,h in headers.items()},
                quantization_config=quant or 'NONE',awq_tensor_metadata=awq,
                no_requantization=True,gpu_or_model_inference_executed=False)


def main() -> None:
    p=argparse.ArgumentParser()
    p.add_argument('--root',type=Path,default=Path('/root/share/mnt164/huangrulin/c16_ai_workload/assets/models'))
    p.add_argument('--preflight-metadata',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--models',nargs='+',choices=['QWEN_BF16','QWEN_AWQ','OLMOE'],required=True)
    args=p.parse_args()
    remote=json.loads(args.preflight_metadata.read_bytes())
    args.out.mkdir(parents=True,exist_ok=True)
    for key in args.models:
        if key=='OLMOE':
            observed=audit_existing_assets(args.root)['models']['OLMOE']
            if observed['status']!='ASSET_READY' or observed['verified_file_count']!=11 or observed['weight_total_bytes']!=13838721960:
                raise AssertionError('OLMoE frozen asset mismatch')
            result=dict(schema='C16_STAGEA_OLMOE_REVERIFY_V1',status='PASS',model_key='OLMOE',
                        repository='allenai/OLMoE-1B-7B-0125-Instruct',revision=observed['expected_revision'],
                        asset=observed,expected_weight_total_bytes=13838721960,
                        gpu_or_model_inference_executed=False)
            filename='OLMOE_ASSET_REVERIFY.json'
        else:
            result=audit_qwen(key,args.root,remote)
            filename=STAGEA[key][2]
        (args.out/filename).write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8')
        print('PASS',key,filename,flush=True)


if __name__=='__main__':
    main()
