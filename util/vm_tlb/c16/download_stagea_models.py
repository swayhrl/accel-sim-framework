#!/usr/bin/env python3
"""Download only two pinned Qwen repositories, resume safely, verify every blob."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
import urllib.request
from pathlib import Path


ALLOWED={
    'QWEN_BF16':('Qwen/Qwen2.5-3B-Instruct','aa8e72537993ba99e69dfaafa59ed015b17504d1','qwen2.5-3b-instruct'),
    'QWEN_AWQ':('Qwen/Qwen2.5-3B-Instruct-AWQ','3559b226e8ce77211e2c1bd7ddfb7686fec4d6dd','qwen2.5-3b-instruct-awq'),
}


def request(url: str, headers: dict | None=None):
    return urllib.request.Request(url,headers={'User-Agent':'C16-pinned-asset-closure/1.0',**(headers or {})})


def sha_file(path: Path) -> str:
    digest=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(8*1024*1024),b''):
            digest.update(chunk)
    return digest.hexdigest()


def fetch(url: str,path: Path,expected_size: int,expected_sha: str | None) -> dict:
    path.parent.mkdir(parents=True,exist_ok=True)
    partial=path.with_name(path.name+'.part')
    if path.is_file():
        size=path.stat().st_size
        digest=sha_file(path)
        if size==expected_size and (expected_sha is None or digest==expected_sha):
            print('REUSE',path.name,size,flush=True)
            return dict(size_bytes=size,sha256=digest)
        raise AssertionError(f'existing final file mismatch; refusing overwrite: {path}')
    for attempt in range(8):
        offset=partial.stat().st_size if partial.exists() else 0
        if offset>expected_size:
            raise AssertionError('partial file exceeds expected size')
        headers={'Range':f'bytes={offset}-'} if offset else {}
        try:
            with urllib.request.urlopen(request(url,headers),timeout=90) as response:
                if offset:
                    expected_prefix=f'bytes {offset}-'
                    actual_range=response.headers.get('Content-Range','')
                    if response.status!=206 or not actual_range.startswith(expected_prefix):
                        raise AssertionError(f'Range resume not honored: {response.status} {actual_range}')
                else:
                    if response.status not in (200,206):
                        raise AssertionError(f'unexpected HTTP {response.status}')
                with partial.open('ab' if offset else 'wb') as out:
                    last_print=offset
                    while True:
                        chunk=response.read(8*1024*1024)
                        if not chunk:break
                        out.write(chunk)
                        if out.tell()-last_print>=256*1024*1024:
                            print('PROGRESS',path.name,out.tell(),'/',expected_size,flush=True)
                            last_print=out.tell()
            if partial.stat().st_size==expected_size:
                digest=sha_file(partial)
                if expected_sha is not None and digest!=expected_sha:
                    raise AssertionError(f'SHA mismatch {path.name}: {digest}')
                os.replace(partial,path)
                print('PASS',path.name,expected_size,digest,flush=True)
                return dict(size_bytes=expected_size,sha256=digest)
            print('RETRY_SHORT',path.name,partial.stat().st_size,expected_size,flush=True)
        except (TimeoutError,ConnectionError,OSError) as exc:
            print('RETRY_NET',path.name,attempt,type(exc).__name__,str(exc)[:120],flush=True)
        if attempt<7:time.sleep(min(4*(attempt+1),20))
    raise RuntimeError(f'download incomplete: {path}')


def main() -> None:
    p=argparse.ArgumentParser()
    p.add_argument('--model-key',choices=ALLOWED,required=True)
    p.add_argument('--metadata',type=Path,required=True)
    p.add_argument('--out-root',type=Path,required=True)
    args=p.parse_args()
    key=args.model_key;repo,revision,slug=ALLOWED[key]
    metadata=json.loads(args.metadata.read_bytes())['models'][key]
    if (metadata['repository'],metadata['revision'])!=(repo,revision):
        raise AssertionError('pinned model metadata mismatch')
    api=f'https://huggingface.co/api/models/{repo}/revision/{revision}?blobs=true'
    with urllib.request.urlopen(request(api),timeout=30) as response:
        actual=json.load(response)
    if actual['sha']!=revision:
        raise AssertionError('HF resolved revision mismatch')
    siblings={x['rfilename']:x for x in actual['siblings']}
    if set(siblings)!=set(metadata['all_sibling_paths']):
        raise AssertionError('pinned sibling inventory changed')
    directory=args.out_root/slug/revision
    directory.mkdir(parents=True,exist_ok=True)
    finished=[]
    for name in sorted(siblings):
        if name.startswith('/') or '..' in Path(name).parts:
            raise AssertionError('unsafe model path')
        info=siblings[name];size=info.get('size')
        if not isinstance(size,int):
            raise AssertionError('missing pinned size '+name)
        expected=info.get('lfs',{}).get('sha256')
        if name.endswith('.safetensors'):
            match=next((x for x in metadata['weight_shards'] if x['path']==name),None)
            if match is None or (size,expected)!=(match['size_bytes'],match['sha256']):
                raise AssertionError('weight size/SHA authority mismatch '+name)
        elif name in metadata['small_files']:
            expected=metadata['small_files'][name]['sha256']
        url=f'https://huggingface.co/{repo}/resolve/{revision}/{name}'
        result=fetch(url,directory/name,size,expected)
        finished.append(dict(path=name,**result))
    manifest=dict(schema='C16_STAGEA_LOCAL_DOWNLOAD_RECEIPT_V1',repository=repo,revision=revision,
                  model_key=key,files=finished,file_count=len(finished),
                  total_bytes=sum(x['size_bytes'] for x in finished),
                  config_sha256=metadata['small_files']['config.json']['sha256'],
                  tokenizer_revision=revision,weights_downloaded=True,model_inference_executed=False)
    receipt=directory/'DOWNLOAD_RECEIPT.json'
    receipt.write_bytes((json.dumps(manifest,indent=2,sort_keys=True)+'\n').encode('utf-8'))
    print('COMPLETE',key,len(finished),manifest['total_bytes'],flush=True)


if __name__=='__main__':
    main()
