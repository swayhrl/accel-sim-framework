#!/usr/bin/env python3
"""Decode only preregistered discovery episode A observations, CPU only."""
import hashlib
import json
import subprocess
from pathlib import Path

import numpy as np
import pyarrow.parquet as pq

ROOT=Path('/data/c16/awma/vla_rtc_vjp_boundary_20260930')
FRAMES=(0,10,20,30)

def digest(b): return hashlib.sha256(b).hexdigest()

def read_frames(path):
    # Force the system's software dav1d decoder; OpenCV's AV1 backend on this
    # host erroneously attempts unavailable hardware acceleration.
    cmd=['/usr/bin/ffmpeg','-hide_banner','-loglevel','error','-hwaccel','none',
         '-c:v','libdav1d','-i',str(path),'-an','-frames:v',str(max(FRAMES)+1),
         '-f','rawvideo','-pix_fmt','rgb24','pipe:1']
    p=subprocess.run(cmd,capture_output=True,check=True)
    expected=(max(FRAMES)+1)*256*256*3
    assert len(p.stdout)==expected,(path,len(p.stdout),expected,p.stderr.decode())
    array=np.frombuffer(p.stdout,dtype=np.uint8).reshape(max(FRAMES)+1,256,256,3)
    return {idx:array[idx].copy() for idx in FRAMES}

def main():
    # The minimum shared Parquet shard also stores episode B. Materialize only
    # episode A rows; never select B observation values before its gate.
    data=pq.read_table(ROOT/'assets/dataset/data/chunk-000/file-000.parquet',
                       filters=[('episode_index','=',0)])
    meta=pq.read_table(ROOT/'assets/dataset/meta/episodes/chunk-000/file-000.parquet').to_pylist()
    ep0=next(x for x in meta if x['episode_index']==0)
    assert ep0['dataset_from_index']==0 and ep0['length']==214
    rows=data.to_pylist()
    assert len(rows)==ep0['length']
    selected={int(x['frame_index']):x for x in rows if int(x['frame_index']) in FRAMES}
    assert set(selected)==set(FRAMES) and all(x['episode_index']==0 for x in selected.values())
    tasks=pq.read_table(ROOT/'assets/dataset/meta/tasks.parquet').to_pylist()
    taskmap={int(x['task_index']):x['__index_level_0__'] for x in tasks}
    files=[ROOT/'assets/dataset/videos/observation.images.image/chunk-000/file-000.mp4',
           ROOT/'assets/dataset/videos/observation.images.image2/chunk-000/file-000.mp4']
    cameras=[read_frames(p) for p in files]
    states=np.stack([np.asarray(selected[f]['observation.state'],dtype=np.float32) for f in FRAMES])
    image1=np.stack([cameras[0][f] for f in FRAMES])
    image2=np.stack([cameras[1][f] for f in FRAMES])
    taskids=np.array([int(selected[f]['task_index']) for f in FRAMES],dtype=np.int64)
    tasktexts=np.array([taskmap[int(i)] for i in taskids])
    assert states.shape==(4,8) and image1.shape==(4,256,256,3)
    output=ROOT/'raw/f1/discovery_observations.npz'
    np.savez_compressed(output,frame_index=np.array(FRAMES,dtype=np.int64),
        state=states,image1_rgb=image1,image2_rgb=image2,
        task_index=taskids,task_text=tasktexts)
    ffmpeg_version=subprocess.check_output(['/usr/bin/ffmpeg','-version'],text=True).splitlines()[0]
    receipt={'episode_index':0,'frame_indices':FRAMES,'decoder':'ffmpeg -hwaccel none -c:v libdav1d',
        'ffmpeg_version':ffmpeg_version,
        'state_shape':list(states.shape),'image_shape':list(image1.shape),
        'state_sha256':digest(states.tobytes()),
        'image1_sha256':digest(image1.tobytes()),
        'image2_sha256':digest(image2.tobytes()),
        'task_index':taskids.tolist(),'task_text':tasktexts.tolist(),
        'npz_sha256':digest(output.read_bytes()),
        'validation_episode_values_selected_or_inspected':False,
        'shared_parquet_shard_contains_B_but_filter_selects_only_A':True}
    (ROOT/'raw/f1/discovery_observations_receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(json.dumps(receipt,sort_keys=True))

if __name__=='__main__':main()
