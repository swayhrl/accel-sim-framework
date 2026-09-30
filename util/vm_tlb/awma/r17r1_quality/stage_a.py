#!/usr/bin/env python3
"""Bounded quality extension on the accepted IVF-PQ index, no latency claim."""
import csv
import hashlib
import json
import os
import struct
import time
from pathlib import Path

import numpy as np

OLD=Path('/data/c16/awma/r17_graph_search_20260930')
NEW=Path('/data/c16/awma/r17r1_quality_requalification_20260930')
WT=Path('/home/huangrulin/workspace/worktrees/accel-sim-awma-r17r1-quality-requalification-109-v1')
PARENT=Path('/home/huangrulin/workspace/worktrees/accel-sim-awma-r17-graph-search-native-109-v1/docs/vm_tlb/review_packs/AWMA_R17_GRAPH_SEARCH_109_V1')
PACK=WT/'docs/vm_tlb/review_packs/AWMA_R17R1_GRAPH_SEARCH_109_V2'
INDEX=OLD/'index/cagra_glove100_g64_ig128_sqeuclidean.bin'
GATE=0.95

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):
            h.update(b)
    return h.hexdigest()

def mmap(path,dtype):
    with path.open('rb') as f:n,d=struct.unpack('<ii',f.read(8))
    assert path.stat().st_size==8+n*d*np.dtype(dtype).itemsize
    return np.memmap(path,dtype=dtype,mode='r',offset=8,shape=(n,d))

def write(rows):
    with (PACK/'QUALITY_EXTENSION_IVFPQ.tsv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n')
        w.writeheader();w.writerows(rows)

def main():
    assert os.environ.get('R17R1_GPU_LOCK_HELD')=='1'
    parent=json.loads((PACK/'PARENT_AUTHORITY.json').read_text())
    assert sha(INDEX)==parent['parent_index_serialized_sha256']
    import cupy as cp
    from cuvs.neighbors import cagra
    index=cagra.Index();dataset=cagra.Dataset()
    cagra.load(index,str(INDEX),out_dataset=dataset)
    assert index.trained and len(index)==1183514 and index.graph_degree==64
    queries=cp.asarray(mmap(OLD/'dataset/glove-100-inner/query.fbin','<f4')[:256].copy())
    gt=mmap(OLD/'dataset/glove-100-inner/groundtruth.neighbors.ibin','<i4')[:256,:10].copy()
    cp.cuda.runtime.deviceSynchronize()
    raw=NEW/'raw/quality_ivfpq';raw.mkdir(parents=True,exist_ok=True)
    old=[]
    with (PARENT/'QUALITY_CALIBRATION.tsv').open(newline='') as f:
        for r in csv.DictReader(f,delimiter='\t'):
            if r['query_batch']=='1' and r['identity_note']=='MEASURED':
                old.append({'index':'IVF_PQ_PARENT','stage':'PARENT_REUSED','arm':r['arm'],
                  'mode':'multi_cta' if r['mode']=='auto' else r['mode'],
                  'itopk':r['itopk'],'search_width':r['search_width'],
                  'cta_per_query':r['expected_cta_per_query'],'recall_at_10':r['recall_at_10'],
                  'qualified':str(float(r['recall_at_10'])>=GATE),
                  'status':'ACCEPTED_V1_REUSED','neighbor_output_sha256':'NOT_RECORDED_IN_PARENT',
                  'reason':'accepted parent Q1 quality; no GPU rerun'})
    assert len(old)==7,len(old)
    rows=old.copy();write(rows)
    phase1=[('A1_SINGLE_128_1','single_cta',128,1),
            ('A1_SINGLE_256_1','single_cta',256,1),
            ('A1_SINGLE_512_1','single_cta',512,1),
            ('A1_MULTI_512_1','multi_cta',512,1)]
    phase2=[('A2_SINGLE_512_2','single_cta',512,2),
            ('A2_SINGLE_512_4','single_cta',512,4),
            ('A2_SINGLE_512_8','single_cta',512,8),
            ('A2_MULTI_512_32','multi_cta',512,32),
            ('A2_MULTI_512_64','multi_cta',512,64)]
    def evaluate(points,stage):
        for label,mode,itopk,width in points:
            out=cp.empty((256,10),dtype=cp.uint32)
            dist=cp.empty((256,10),dtype=cp.float32)
            params=cagra.SearchParams(algo=mode,itopk_size=itopk,search_width=width)
            begin=time.perf_counter();error=''
            try:
                for i in range(256):
                    cagra.search(params,index,queries[i:i+1],10,
                        neighbors=out[i:i+1],distances=dist[i:i+1])
                cp.cuda.runtime.deviceSynchronize()
                ans=cp.asnumpy(out);d=cp.asnumpy(dist)
                assert np.isfinite(d).all() and (ans<len(index)).all()
                recall=float(np.mean([len(set(map(int,ans[i])).intersection(map(int,gt[i])))/10 for i in range(256)]))
                dest=raw/f'{label}.npy';np.save(dest,ans,allow_pickle=False)
                status='VALID';digest=sha(dest)
            except Exception as exc:
                recall=float('nan');status='INVALID_SOURCE_SUPPORTED_POINT'
                error=f'{type(exc).__name__}: {exc}';digest='NO_OUTPUT'
            row={'index':'IVF_PQ_PARENT','stage':stage,'arm':label,'mode':mode,
                'itopk':itopk,'search_width':width,
                'cta_per_query':1 if mode=='single_cta' else max(width,(itopk+31)//32),
                'recall_at_10':f'{recall:.9f}' if status=='VALID' else 'INVALID',
                'qualified':str(status=='VALID' and recall>=GATE),
                'status':status,'neighbor_output_sha256':digest,
                'reason':error if error else f'quality_only_elapsed_seconds={time.perf_counter()-begin:.6f}'}
            rows.append(row);write(rows)
            print(json.dumps(row,sort_keys=True),flush=True)
    evaluate(phase1,'A1_HIGH_ITOPK')
    a1_qualified=any(r['stage']=='A1_HIGH_ITOPK' and r['qualified']=='True' for r in rows)
    if not a1_qualified:evaluate(phase2,'A2_WIDTH_ONLY_IF_A1_FAIL')
    qualified=[r for r in rows if r['qualified']=='True']
    summary={'parent_index_sha256':sha(INDEX),'a1_all_four_run':True,
        'a1_qualified':a1_qualified,'a2_triggered':not a1_qualified,
        'qualified_points':qualified,'quality_gate':GATE,'stage_A_pass':bool(qualified),
        'holdout_inspected':False,'new_index_built':False}
    (NEW/'raw/stage_a_summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
    print('STAGE_A_COMPLETE',json.dumps({'passed':bool(qualified),'a2':not a1_qualified,
        'qualified':qualified},sort_keys=True),flush=True)

if __name__=='__main__':main()
