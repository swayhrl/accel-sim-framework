#!/usr/bin/env python3
"""Formal paired Q1 timing of the two frozen recall-qualified CAGRA arms."""
import csv
import hashlib
import json
import math
import os
import statistics
import struct
import time
from pathlib import Path

import numpy as np

OLD=Path('/data/c16/awma/r17_graph_search_20260930')
NEW=Path('/data/c16/awma/r17r1_quality_requalification_20260930')
WT=Path('/home/huangrulin/workspace/worktrees/accel-sim-awma-r17r1-quality-requalification-109-v1')
PACK=WT/'docs/vm_tlb/review_packs/AWMA_R17R1_GRAPH_SEARCH_109_V2'
INDEX=OLD/'index/cagra_glove100_g64_ig128_sqeuclidean.bin'
ARMS=(('Q1_SINGLE_512_1','single_cta'),('Q1_MULTI_512_1','multi_cta'))

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

def write(path,rows):
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n')
        w.writeheader();w.writerows(rows)

def main():
    assert os.environ.get('R17R1_GPU_LOCK_HELD')=='1'
    parent=json.loads((PACK/'PARENT_AUTHORITY.json').read_text())
    assert sha(INDEX)==parent['parent_index_serialized_sha256']
    stage_a=json.loads((NEW/'raw/stage_a_summary.json').read_text())
    assert stage_a['stage_A_pass'] and not stage_a['a2_triggered'] and not stage_a['new_index_built']
    qualified={(r['mode'],int(r['itopk']),int(r['search_width'])) for r in stage_a['qualified_points']}
    assert qualified=={('single_cta',512,1),('multi_cta',512,1)}
    import cupy as cp
    from cuvs.neighbors import cagra
    from cuvs.common import Resources
    index=cagra.Index();dataset=cagra.Dataset();cagra.load(index,str(INDEX),out_dataset=dataset)
    assert len(index)==1183514 and index.graph_degree==64
    query=cp.asarray(mmap(OLD/'dataset/glove-100-inner/query.fbin','<f4')[:256].copy())
    gt=mmap(OLD/'dataset/glove-100-inner/groundtruth.neighbors.ibin','<i4')[:256,:10].copy()
    cp.cuda.runtime.deviceSynchronize()
    resources=Resources()
    params={label:cagra.SearchParams(algo=mode,itopk_size=512,search_width=1) for label,mode in ARMS}
    outputs={label:(cp.empty((256,10),dtype=cp.uint32),cp.empty((256,10),dtype=cp.float32)) for label,_ in ARMS}
    raw=[];compact=[];last_neighbors={}
    for group in range(3):
        order=ARMS if group%2==0 else tuple(reversed(ARMS))
        for arm_ordinal,(label,mode) in enumerate(order):
            neighbor,distance=outputs[label]
            for rep in range(7):
                status='WARMUP' if rep<2 else 'FORMAL'
                samples=[]
                for query_id in range(256):
                    begin=time.perf_counter_ns()
                    cagra.search(params[label],index,query[query_id:query_id+1],10,
                        neighbors=neighbor[query_id:query_id+1],
                        distances=distance[query_id:query_id+1],resources=resources)
                    resources.sync()
                    ms=(time.perf_counter_ns()-begin)/1e6
                    samples.append(ms)
                    raw.append({'group':group,'arm_order_in_group':arm_ordinal,'arm':label,
                        'mode':mode,'repeat':rep,'status':status,'query_id':query_id,
                        'complete_query_ready_to_GPU_result_ready_host_ms':f'{ms:.9f}'})
                ans=cp.asnumpy(neighbor);d=cp.asnumpy(distance)
                assert (ans<len(index)).all() and np.isfinite(d).all()
                recall=float(np.mean([len(set(map(int,ans[i])).intersection(map(int,gt[i])))/10 for i in range(256)]))
                assert recall>=0.95,(label,group,rep,recall)
                if status=='FORMAL':last_neighbors[label]=ans.copy()
                ordered=sorted(samples)
                compact.append({'group':group,'arm_order_in_group':arm_ordinal,
                    'arm':label,'mode':mode,'itopk':512,'search_width':1,'repeat':rep,'status':status,
                    'queries':256,'complete_256_Q1_host_ms':f'{sum(samples):.9f}',
                    'per_query_median_ms':f'{statistics.median(samples):.9f}',
                    'per_query_p95_ms':f'{ordered[math.ceil(0.95*len(ordered))-1]:.9f}',
                    'recall_at_10':f'{recall:.9f}','output_preallocated':True,
                    'device_resident_query_and_index':True,'Resources_reused':True})
            write(PACK/'FORMAL_Q1_TIMING.tsv',compact)
            print('FORMAL_GROUP_ARM_COMPLETE',group,label,flush=True)
    rawfile=NEW/'raw/formal_q1_per_query.tsv';write(rawfile,raw)
    for label,ans in last_neighbors.items():
        np.save(NEW/'raw'/f'{label}_last_formal_neighbors.npy',ans,allow_pickle=False)
    assert len(raw)==3*2*7*256 and len(compact)==42
    summary={}
    for label,mode in ARMS:
        arm=[float(x['complete_256_Q1_host_ms']) for x in compact if x['arm']==label and x['status']=='FORMAL']
        summary[label]={'mode':mode,'itopk':512,'search_width':1,
            'formal_repeat_count':len(arm),'median_complete_256_Q1_host_ms':statistics.median(arm),
            'MAD_complete_256_Q1_host_ms':statistics.median(abs(x-statistics.median(arm)) for x in arm),
            'recall_at_10':float(next(x['recall_at_10'] for x in compact if x['arm']==label and x['status']=='FORMAL')),
            'last_neighbor_output_sha256':sha(NEW/'raw'/f'{label}_last_formal_neighbors.npy')}
    eligible={k:v for k,v in summary.items() if v['recall_at_10']>=0.95}
    assert eligible
    strong=min(eligible,key=lambda k:(eligible[k]['median_complete_256_Q1_host_ms'],k))
    outcome={'Q1_STRONG_V2':strong,'candidate_summary':summary,
        'candidate_count':2,'formal_groups':3,'warmups_per_arm_group':2,
        'formal_repeats_per_arm_group':5,'queries_per_repeat':256,
        'arm_order_by_group':[['Q1_SINGLE_512_1','Q1_MULTI_512_1'],
                              ['Q1_MULTI_512_1','Q1_SINGLE_512_1'],
                              ['Q1_SINGLE_512_1','Q1_MULTI_512_1']],
        'index_sha256':sha(INDEX),'holdout_queries_inspected':False,
        'Resources_reused_per_process':True,
        'per_query_raw':str(rawfile),'per_query_raw_sha256':sha(rawfile)}
    (NEW/'raw/stage_c_summary.json').write_text(json.dumps(outcome,indent=2,sort_keys=True)+'\n')
    (PACK/'Q1_STRONG_V2.md').write_text(
        '# Formal Q1 strong candidate\n\n'
        f"`{strong}` was selected only after the preregistered 3×(2 warmup+5 formal) paired schedule. "
        f"Its discovery recall@10 is {summary[strong]['recall_at_10']:.9f}; median 256-query Q1 "
        f"complete host time is {summary[strong]['median_complete_256_Q1_host_ms']:.6f} ms. "
        'This is a quality-qualified mature software arm, not a hardware-performance conclusion. '
        'All per-query samples remain in node164 raw; sealed holdout was not opened.\n')
    print('STAGE_C_COMPLETE',json.dumps(outcome,sort_keys=True),flush=True)

if __name__=='__main__':main()
