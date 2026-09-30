#!/usr/bin/env python3
"""F1/F2/F3 frozen CAGRA quality + bounded discovery screen under GPU lock."""
import csv
import hashlib
import json
import os
import statistics
import struct
import time
from pathlib import Path

import numpy as np

ROOT=Path('/data/c16/awma/r17_graph_search_20260930')
WT=Path('/home/huangrulin/workspace/worktrees/accel-sim-awma-r17-graph-search-native-109-v1')
PACK=WT/'docs/vm_tlb/review_packs/AWMA_R17_GRAPH_SEARCH_109_V1'
BIN=ROOT/'dataset/glove-100-inner'
INDEX=ROOT/'index/cagra_glove100_g64_ig128_sqeuclidean.bin'
K=10

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):
            h.update(b)
    return h.hexdigest()

def memmap(path,dtype):
    with path.open('rb') as f:n,d=struct.unpack('<ii',f.read(8))
    assert path.stat().st_size==8+n*d*np.dtype(dtype).itemsize
    return np.memmap(path,dtype=dtype,mode='r',offset=8,shape=(n,d))

def tsv(path,rows):
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n')
        w.writeheader();w.writerows(rows)

def main():
    assert os.environ.get('R17_GPU_LOCK_HELD')=='1'
    receipt=json.loads((PACK/'INDEX_RECEIPT.json').read_text())
    assert sha(INDEX)==receipt['index_serialized_sha256']
    import cupy as cp
    from cuvs.neighbors import cagra
    index=cagra.Index();dataset=cagra.Dataset()
    cagra.load(index,str(INDEX),out_dataset=dataset)
    assert len(index)==1183514 and index.graph_degree==64 and index.dim==100
    graph_shape=list(cp.asarray(index.graph).shape)
    dataset_shape=list(cp.asarray(index.dataset).shape)
    query_cpu=memmap(BIN/'query.fbin','<f4')[:256].copy()
    gt=memmap(BIN/'groundtruth.neighbors.ibin','<i4')[:256,:10].copy()
    query=cp.asarray(query_cpu)
    cp.cuda.runtime.deviceSynchronize()
    assert query.shape==(256,100) and gt.shape==(256,10)
    nsm=cp.cuda.runtime.getDeviceProperties(0)['multiProcessorCount']
    assert nsm==76
    # SOURCE: search_plan.cuh AUTO chooses SINGLE at >=2*SM for itopk<=512;
    # MULTI CTA/query=max(width,ceil(global_itopk/32)).
    plans=[]
    for q in (1,32,256):
        resolved='single_cta' if q>=nsm*2 else 'multi_cta'
        for mode in ('auto','multi_cta','single_cta'):
            plans.append({'query_batch':q,'requested_mode':mode,
                'resolved_mode':resolved if mode=='auto' else mode,
                'source_auto_alias':mode=='auto' and resolved,
                'itopk':64,'search_width':1,
                'expected_cta_per_query':1 if (resolved if mode=='auto' else mode)=='single_cta' else 2,
                'source_identity':'v26.08.01 search_plan.cuh threshold 2*76; search_multi_cta.cuh max(width,ceil(itopk/32))',
                'runtime_duplicate_full_arm_skipped':(mode=='multi_cta' and q in (1,32)) or (mode=='single_cta' and q==256)})
    tsv(PACK/'PLAN_IDENTITY.tsv',plans)
    jobs=[
      ('F2_Q1_AUTO',1,'auto',64,1,False),
      ('F2_Q1_SINGLE',1,'single_cta',64,1,False),
      ('F2_Q32_AUTO',32,'auto',64,1,False),
      ('F2_Q32_SINGLE',32,'single_cta',64,1,False),
      ('F2_Q256_AUTO',256,'auto',64,1,False),
      ('F2_Q256_MULTI',256,'multi_cta',64,1,False),
      ('F3_Q1_MULTI_64_2',1,'multi_cta',64,2,True),
      ('F3_Q1_MULTI_128_1',1,'multi_cta',128,1,True),
      ('F3_Q1_MULTI_128_2',1,'multi_cta',128,2,True),
      ('F3_Q1_MULTI_256_1',1,'multi_cta',256,1,True),
      ('F3_Q1_MULTI_256_2',1,'multi_cta',256,2,True),
    ]
    quality=[];timing=[];summary=[]
    for label,q,mode,itopk,width,is_grid in jobs:
        params=cagra.SearchParams(itopk_size=itopk,search_width=width,algo=mode)
        neighbor=cp.empty((256,K),dtype=cp.uint32)
        distance=cp.empty((256,K),dtype=cp.float32)
        def one_pass():
            per=[]
            for off in range(0,256,q):
                begin=time.perf_counter_ns()
                cagra.search(params,index,query[off:off+q],K,
                    neighbors=neighbor[off:off+q],distances=distance[off:off+q])
                cp.cuda.runtime.deviceSynchronize()
                per.append((time.perf_counter_ns()-begin)/1e6)
            return per
        for _ in range(2):one_pass()
        measured=[]
        for rep in range(5):
            per=one_pass();measured.append(sum(per))
            for batch,ms in enumerate(per):
                timing.append({'stage':'F3_GRID' if is_grid else 'F2_FIXED',
                    'arm':label,'query_batch':q,'mode':mode,'itopk':itopk,
                    'search_width':width,'repeat':rep,'batch_ordinal':batch,
                    'query_begin':batch*q,'query_end_exclusive':(batch+1)*q,
                    'complete_host_ms':f'{ms:.9f}',
                    'output_buffers_preallocated':True,'query_device_resident':True})
        ans=cp.asnumpy(neighbor)
        d=cp.asnumpy(distance)
        assert np.isfinite(d).all() and (ans<len(index)).all()
        recalls=[len(set(map(int,ans[i])).intersection(map(int,gt[i])))/K for i in range(256)]
        recall=float(np.mean(recalls))
        if len(set(map(tuple,ans.tolist())))==0:raise AssertionError('empty result')
        cta=max(width,(itopk+31)//32) if mode=='multi_cta' or (mode=='auto' and q<152) else 1
        item={'arm':label,'query_batch':q,'mode':mode,'itopk':itopk,'search_width':width,
            'resolved_mode':('multi_cta' if q<152 else 'single_cta') if mode=='auto' else mode,
            'expected_cta_per_query':cta,'recall_at_10':f'{recall:.9f}',
            'recall_gate_pass':recall>=0.95,'host_256_queries_median_ms':f'{statistics.median(measured):.9f}',
            'host_256_queries_MAD_ms':f'{statistics.median(abs(x-statistics.median(measured)) for x in measured):.9f}',
            'query_sha256':sha(BIN/'query.fbin'),'GT_sha256':sha(BIN/'groundtruth.neighbors.ibin'),
            'graph_sha256':receipt['graph_sha256'],'identity_note':'MEASURED'}
        quality.append(item)
        summary.append(item)
        tsv(PACK/'QUALITY_CALIBRATION.tsv',quality)
        tsv(PACK/'DISCOVERY_TIMING.tsv',timing)
        print(json.dumps(item,sort_keys=True),flush=True)
    # Aliases are the same runtime plan by stable-source rule. Do not issue a
    # second full timing arm just to rename AUTO as its forced equivalent.
    aliases=[]
    for q,forced,source_label in ((1,'multi_cta','F2_Q1_AUTO'),(32,'multi_cta','F2_Q32_AUTO'),(256,'single_cta','F2_Q256_AUTO')):
        item=next(x for x in quality if x['arm']==source_label).copy()
        item['arm']=f'F2_Q{q}_{forced.upper()}_SOURCE_ALIAS'
        item['mode']=forced;item['identity_note']='SOURCE_ALIAS_NO_DUPLICATE_PROFILE'
        aliases.append(item)
    quality.extend(aliases)
    tsv(PACK/'QUALITY_CALIBRATION.tsv',quality)
    # Six preregistered Q1 MULTI_CTA points, with 64/1 sourced from Q1_AUTO.
    grid=[next(x for x in quality if x['arm']=='F2_Q1_AUTO')]+[x for x in quality if x['arm'].startswith('F3_Q1_')]
    assert len(grid)==6
    eligible=[x for x in grid if x['recall_gate_pass']]
    result={'index_sha256':sha(INDEX),'graph_shape':graph_shape,'dataset_shape':dataset_shape,
      'F2_F3_jobs_run':len(jobs),'Q1_grid_count':6,'eligible_Q1_grid_count':len(eligible),
      'quality_summary':summary,'alias_count':len(aliases),'query_ids_used':[0,255],
      'sealed_holdout_values_inspected':False}
    if eligible:
        chosen=min(eligible,key=lambda x:float(x['host_256_queries_median_ms']))
        result['Q1_STRONG']=chosen
        (PACK/'STRONG_Q1_SELECTION.md').write_text(
            '# Frozen discovery Q1 strong selection\n\n'
            f"Selected `{chosen['arm']}`: MULTI_CTA, itopk={chosen['itopk']}, search_width={chosen['search_width']}, "
            f"recall@10={chosen['recall_at_10']}, median complete host time for all 256 individual queries="
            f"{chosen['host_256_queries_median_ms']} ms. Selection considered exactly the six preregistered "
            'Q1 MULTI_CTA points; 64/1 is the source-proven AUTO alias. No holdout result was read.\n')
    else:result['Q1_STRONG']='NONE_RECALL_GATE_FAIL'
    (ROOT/'raw/f2_f3_screen_summary.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('SCREEN_COMPLETE',json.dumps({'eligible':len(eligible),'strong':result['Q1_STRONG']},sort_keys=True),flush=True)

if __name__=='__main__':main()
