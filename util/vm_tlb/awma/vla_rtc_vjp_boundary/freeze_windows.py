#!/usr/bin/env python3
"""Freeze two public LIBERO episodes/windows before any model timing."""
import csv
import hashlib
import json
from pathlib import Path

import pyarrow.parquet as pq

ROOT=Path('/data/c16/awma/vla_rtc_vjp_boundary_20260930')
PACK=Path('/home/huangrulin/workspace/worktrees/accel-sim-awma-vla-rtc-vjp-boundary-109-v1/docs/vm_tlb/review_packs/AWMA_VLA_RTC_VJP_BOUNDARY_109_V1')
DATASET_SHA='a1aaacb7f6cd6ee5fb43120f673cebb0cfea7dd4'
MODEL_SHA='31d453f7edd78c839a8bbc39744a292686daf0de'

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):
            h.update(b)
    return h.hexdigest()

def main():
    meta=pq.read_table(ROOT/'assets/dataset/meta/episodes/chunk-000/file-000.parquet').to_pylist()
    info=json.loads((ROOT/'assets/dataset/meta/info.json').read_text())
    assert info['total_episodes']==1693 and info['fps']==10.0
    episode={int(r['episode_index']):r for r in meta}
    assert episode[0]['length']==214 and episode[1]['length']==284
    chosen=[(0,'A_DISCOVERY'),(1,'B_SEALED_VALIDATION')]
    rows=[]
    for idx,role in chosen:
        r=episode[idx]
        assert r['length']>=40
        assert r['data/file_index']==0
        assert r['videos/observation.images.image/file_index']==0
        assert r['videos/observation.images.image2/file_index']==0
        for frame in (0,10,20,30):
            seed_src=f'AWMA_VLA_RTC_VJP_BOUNDARY_109_V1|{DATASET_SHA}|{MODEL_SHA}|episode={idx}|frame={frame}|noise'
            seed=int.from_bytes(hashlib.sha256(seed_src.encode()).digest()[:8],'big')%(2**63)
            rows.append({'role':role,'episode_index':idx,'window_ordinal':frame//10,
                'episode_frame_index':frame,'global_dataset_frame_index':r['dataset_from_index']+frame,
                'video_frame_index':round(r['videos/observation.images.image/from_timestamp']*10)+frame,
                'dataset_revision':DATASET_SHA,'model_revision':MODEL_SHA,
                'noise_seed':seed,'batch':1,'chunk_size':50,'num_denoise_steps':10,
                'execution_horizon':10,'video_payload':'file-000.mp4 for both exact camera streams',
                'data_payload':'data/chunk-000/file-000.parquet',
                'validation_content_status':'SEALED' if idx==1 else 'DISCOVERY'})
    with (PACK/'TARGET_WINDOWS.tsv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n')
        w.writeheader();w.writerows(rows)
    files=[
        ROOT/'assets/dataset/data/chunk-000/file-000.parquet',
        ROOT/'assets/dataset/videos/observation.images.image/chunk-000/file-000.mp4',
        ROOT/'assets/dataset/videos/observation.images.image2/chunk-000/file-000.mp4',
    ]
    receipt={'dataset_revision':DATASET_SHA,'model_revision':MODEL_SHA,
        'selection_rule':'first two metadata-eligible episodes with >=40 frames; 4 starts 10 frames apart',
        'discovery_episode':0,'sealed_validation_episode':1,'window_count_per_episode':4,
        'video_fps':10.0,'file_sha256':{str(p.relative_to(ROOT)):sha(p) for p in files},
        'validation_observation_not_decoded':True}
    (ROOT/'raw/f1/window_freeze.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'rows':len(rows),'discovery':0,'validation':1,'file_sha256':receipt['file_sha256']},sort_keys=True))

if __name__=='__main__':main()
