#!/usr/bin/env python3
"""Matched Q1/Q32 strong CAGRA characterization with reusable Resources."""
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

def medmad(values):
    m=statistics.median(values)
    return {'median':m,'MAD':statistics.median(abs(v-m) for v in values)}

def main():
    print('STAGE_D_BOOT',flush=True)
    assert os.environ.get('R17R1_GPU_LOCK_HELD')=='1'
    c=json.loads((NEW/'raw/stage_c_summary.json').read_text())
    assert c['Q1_STRONG_V2']=='Q1_MULTI_512_1' and c['Resources_reused_per_process']
    assert sha(INDEX)==c['index_sha256']
    import cupy as cp
    from cuvs.neighbors import cagra
    from cuvs.common import Resources
    print('STAGE_D_IMPORTED',flush=True)
    index=cagra.Index();dataset=cagra.Dataset();cagra.load(index,str(INDEX),out_dataset=dataset)
    print('STAGE_D_INDEX_LOADED',flush=True)
    query=cp.asarray(mmap(OLD/'dataset/glove-100-inner/query.fbin','<f4')[:256].copy())
    gt=mmap(OLD/'dataset/glove-100-inner/groundtruth.neighbors.ibin','<i4')[:256,:10].copy()
    cp.cuda.runtime.deviceSynchronize()
    print('STAGE_D_QUERY_LOADED',flush=True)
    # Reuse the same stable default Resources path that qualified Stage C.
    # A custom nonblocking stream caused a no-report cuVS process exit during
    # admission; do not force a different stream for a profiler convenience.
    resources=Resources()
    print('STAGE_D_RESOURCES_READY',flush=True)
    params=cagra.SearchParams(algo='multi_cta',itopk_size=512,search_width=1)
    outputs={q:(cp.empty((256,10),dtype=cp.uint32),cp.empty((256,10),dtype=cp.float32)) for q in (1,32)}
    raw=[];compact=[]
    def one_repeat(q,group,arm_ordinal,rep):
        neighbor,distance=outputs[q]
        status='WARMUP' if rep<2 else 'FORMAL'
        times=[];submits=[];waits=[]
        for batch,off in enumerate(range(0,256,q)):
            t0=time.perf_counter_ns()
            cagra.search(params,index,query[off:off+q],10,
                neighbors=neighbor[off:off+q],distances=distance[off:off+q],resources=resources)
            t1=time.perf_counter_ns()
            resources.sync()
            t2=time.perf_counter_ns()
            host=(t2-t0)/1e6;submit=(t1-t0)/1e6;wait=(t2-t1)/1e6
            times.append(host);submits.append(submit);waits.append(wait)
            raw.append({'group':group,'arm_order_in_group':arm_ordinal,'query_batch':q,
                'repeat':rep,'status':status,'batch_ordinal':batch,'query_begin':off,
                'query_end_exclusive':off+q,'complete_host_ms':f'{host:.9f}',
                'host_submit_interval_ms':f'{submit:.9f}','sync_wait_interval_ms':f'{wait:.9f}'})
        ans=cp.asnumpy(neighbor);d=cp.asnumpy(distance)
        assert np.isfinite(d).all() and (ans<len(index)).all()
        recall=float(np.mean([len(set(map(int,ans[i])).intersection(map(int,gt[i])))/10 for i in range(256)]))
        assert recall>=0.95,(q,group,rep,recall)
        ordered=sorted(times)
        compact.append({'group':group,'arm_order_in_group':arm_ordinal,
            'query_batch':q,'mode':'multi_cta','itopk':512,'search_width':1,
            'repeat':rep,'status':status,'search_calls':len(times),
            'complete_256_query_set_host_ms':f'{sum(times):.9f}',
            'batch_median_host_ms':f'{statistics.median(times):.9f}',
            'batch_p95_host_ms':f'{ordered[math.ceil(0.95*len(ordered))-1]:.9f}',
            'host_submit_sum_ms':f'{sum(submits):.9f}',
            'sync_wait_sum_ms':f'{sum(waits):.9f}',
            'submit_fraction_of_complete_host':f'{sum(submits)/sum(times):.9f}',
            'recall_at_10':f'{recall:.9f}',
            'output_preallocated':True,'Resources_reused':True,
            'query_and_index_GPU_resident':True,
            'Q32_div32_not_single_query_latency':True})
    for group in range(3):
        order=(1,32) if group%2==0 else (32,1)
        for ordinal,q in enumerate(order):
            for rep in range(7):one_repeat(q,group,ordinal,rep)
            write(PACK/'MATCHED_Q1_Q32.tsv',compact)
            print('MATCHED_GROUP_ARM_COMPLETE',group,q,flush=True)
    assert len(compact)==42 and len(raw)==3*7*(256+8)
    rawfile=NEW/'raw/stage_d_per_batch.tsv';write(rawfile,raw)
    formal={q:[r for r in compact if r['status']=='FORMAL' and r['query_batch']==q] for q in (1,32)}
    summary={}
    for q in (1,32):
        xs=formal[q]
        summary[str(q)]={'complete_256_set_host_ms':medmad([float(r['complete_256_query_set_host_ms']) for r in xs]),
            'per_search_batch_host_ms':medmad([float(r['batch_median_host_ms']) for r in xs]),
            'submit_fraction':medmad([float(r['submit_fraction_of_complete_host']) for r in xs]),
            'recall_at_10_min':min(float(r['recall_at_10']) for r in xs),
            'recall_at_10_max':max(float(r['recall_at_10']) for r in xs),
            'search_calls_per_repeat':256//q}
    summary['GPU_event_time_status']='UNAVAILABLE_CUSTOM_STREAM_NOT_QUALIFIED; host submit and synchronized completion retained'
    summary['Q32_amortized_throughput_only_ms_per_query']=summary['32']['complete_256_set_host_ms']['median']/256
    summary['Q32_div32_is_not_Q1_latency_bound']=True
    summary['index_sha256']=sha(INDEX)
    summary['raw_per_batch_sha256']=sha(rawfile)
    summary['holdout_inspected']=False
    (NEW/'raw/stage_d_summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
    print('STAGE_D_COMPLETE',json.dumps(summary,sort_keys=True),flush=True)

if __name__=='__main__':main()
