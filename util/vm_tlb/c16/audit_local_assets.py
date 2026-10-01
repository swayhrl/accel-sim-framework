#!/usr/bin/env python3
"""Read-only CPU inventory and full hash closure for four fixed 164 candidates."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ASSETS={
    'QWEN_BF16':('qwen2.5-3b-instruct','aa8e72537993ba99e69dfaafa59ed015b17504d1'),
    'QWEN_AWQ':('qwen2.5-3b-instruct-awq','3559b226e8ce77211e2c1bd7ddfb7686fec4d6dd'),
    'OLMOE':('olmoe-1b-7b-0125-instruct','b89a7c4bc24fb9e55ce2543c9458ce0ca5c4650e'),
    'GRANITE':('granite-3.1-1b-a400m-instruct','0da7a48b0276d500ce5922fd2b33944091fc6c09'),
}


def sha_file(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(8*1024*1024),b''):
            h.update(chunk)
    return h.hexdigest()


def audit(root: Path) -> dict:
    result={}
    for key,(slug,revision) in ASSETS.items():
        parent=root/slug
        target=parent/revision
        revision_dirs=sorted(p.name for p in parent.iterdir() if p.is_dir()) if parent.is_dir() else []
        if not target.is_dir():
            result[key]=dict(status='NEW_ASSET_REQUIRED' if not revision_dirs else 'ASSET_IDENTITY_MISMATCH',
                             expected_revision=revision,expected_path=str(target),other_revisions=revision_dirs,
                             full_weight_hash_checked=False)
            continue
        receipt_path=target/'MODEL_ASSET_RECEIPT.json'
        if not receipt_path.is_file():
            result[key]=dict(status='ASSET_INCOMPLETE',expected_revision=revision,
                             expected_path=str(target),reason='missing MODEL_ASSET_RECEIPT.json',
                             full_weight_hash_checked=False)
            continue
        receipt_bytes=receipt_path.read_bytes()
        receipt=json.loads(receipt_bytes)
        if receipt.get('revision')!=revision or receipt.get('tokenizer_revision')!=revision:
            result[key]=dict(status='ASSET_IDENTITY_MISMATCH',expected_revision=revision,
                             expected_path=str(target),receipt_sha256=hashlib.sha256(receipt_bytes).hexdigest(),
                             reason='revision or tokenizer revision mismatch',full_weight_hash_checked=False)
            continue
        verified=[]; errors=[]
        for item in receipt['files']:
            path=target/item['path']
            if not path.is_file():
                errors.append(f'missing:{item["path"]}')
                continue
            size=path.stat().st_size
            if size!=item['size']:
                errors.append(f'size:{item["path"]}:{size}')
                continue
            digest=sha_file(path)
            if digest!=item['sha256']:
                errors.append(f'sha:{item["path"]}:{digest}')
            else:
                verified.append(dict(path=item['path'],size_bytes=size,sha256=digest))
        index=target/'model.safetensors.index.json'
        index_names=sorted(set(json.loads(index.read_bytes())['weight_map'].values())) if index.is_file() else []
        weight_names=sorted(x['path'] for x in receipt['files'] if x['path'].endswith('.safetensors'))
        if index_names!=weight_names:
            errors.append('index_weight_shards_mismatch')
        total=sum(x['size_bytes'] for x in verified)
        if total!=receipt['total_bytes']:
            errors.append('total_bytes_mismatch')
        result[key]=dict(status='ASSET_READY' if not errors else 'ASSET_INCOMPLETE',
                         expected_revision=revision,expected_path=str(target),
                         receipt_sha256=hashlib.sha256(receipt_bytes).hexdigest(),
                         config_sha256=receipt.get('config_sha256'),
                         tokenizer_revision=receipt.get('tokenizer_revision'),
                         weight_total_bytes=sum(x['size_bytes'] for x in verified if x['path'].endswith('.safetensors')),
                         weight_shard_names=weight_names,verified_file_count=len(verified),
                         receipt_file_count=receipt['file_count'],verified_total_bytes=total,
                         errors=errors,full_weight_hash_checked=True)
    return dict(schema='C16_LOCAL_164_ASSET_AUDIT_V1',root=str(root),models=result)


def main() -> None:
    p=argparse.ArgumentParser()
    p.add_argument('--root',type=Path,default=Path('/root/share/mnt164/huangrulin/c16_ai_workload/assets/models'))
    p.add_argument('--out',type=Path,required=True)
    args=p.parse_args()
    result=audit(args.root)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print({k:v['status'] for k,v in result['models'].items()})


if __name__=='__main__':
    main()
