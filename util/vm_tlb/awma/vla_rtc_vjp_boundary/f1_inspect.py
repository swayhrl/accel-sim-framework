#!/usr/bin/env python3
"""CPU-only inspection of pinned public VLA asset metadata and downloaded files."""
import hashlib
import json
from pathlib import Path

import pyarrow.parquet as pq
from safetensors import safe_open

ROOT=Path('/data/c16/awma/vla_rtc_vjp_boundary_20260930')

def git_blob_sha1(path):
    b=path.read_bytes()
    return hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()

def sha256(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):
            h.update(b)
    return h.hexdigest()

def inspect_repo(name,tree):
    root=ROOT/'assets'/name
    rows=[]
    for item in json.loads((ROOT/'raw/f1'/tree).read_text()):
        if item.get('type')!='file': continue
        path=root/item['path']
        if not path.exists():continue
        observed=sha256(path) if 'lfs' in item else git_blob_sha1(path)
        expected=item['lfs']['oid'] if 'lfs' in item else item['oid']
        assert path.stat().st_size==item['size'] and observed==expected,(path,observed,expected)
        rows.append({'path':str(path),'size':path.stat().st_size,'sha256':sha256(path),'repo_oid':expected})
    return rows

def main():
    verification=[]
    verification+=inspect_repo('model','model_tree.json')
    verification+=inspect_repo('base_vlm','base_vlm_tree.json')
    verification+=inspect_repo('dataset','dataset_tree.json')
    model=json.loads((ROOT/'assets/model/config.json').read_text())
    dataset=json.loads((ROOT/'assets/dataset/meta/info.json').read_text())
    ep=pq.read_table(ROOT/'assets/dataset/meta/episodes/chunk-000/file-000.parquet')
    task=pq.read_table(ROOT/'assets/dataset/meta/tasks.parquet')
    normalizer={}
    for filename in ('policy_preprocessor_step_5_normalizer_processor.safetensors',
                     'policy_postprocessor_step_0_unnormalizer_processor.safetensors'):
        with safe_open(ROOT/'assets/model'/filename,framework='pt',device='cpu') as f:
            normalizer[filename]={k:list(f.get_tensor(k).shape) for k in f.keys()}
    result={
        'verified_downloads':verification,
        'model':{'chunk_size':model['chunk_size'],'num_steps':model['num_steps'],
                 'use_amp':model['use_amp'],'use_cache':model['use_cache'],
                 'state_feature':model['input_features']['observation.state'],
                 'cameras':[k for k in model['input_features'] if 'images' in k],
                 'base_vlm':model['vlm_model_name']},
        'dataset':{'total_episodes':dataset['total_episodes'],'fps':dataset['fps'],
                   'state_feature':dataset['features']['observation.state'],
                   'video_keys':[k for k,v in dataset['features'].items() if v['dtype']=='video']},
        'episode_schema':str(ep.schema),
        'episode_first_rows':ep.slice(0,4).to_pylist(),
        'tasks_schema':str(task.schema),
        'task_first_rows':task.slice(0,4).to_pylist(),
        'normalizer_tensor_shapes':normalizer,
    }
    out=ROOT/'raw/f1/metadata_inspection.json'
    out.write_text(json.dumps(result,indent=2,sort_keys=True,default=str)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='verified_downloads'},indent=2,default=str))

if __name__=='__main__':main()
