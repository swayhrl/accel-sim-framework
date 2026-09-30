#!/usr/bin/env python3
"""Offline official GloVe-100-angular identity and metric-admission audit."""
import csv
import hashlib
import json
import struct
from pathlib import Path

import h5py
import numpy as np

ROOT=Path('/data/c16/awma/r17_graph_search_20260930')
WT=Path('/home/huangrulin/workspace/worktrees/accel-sim-awma-r17-graph-search-native-109-v1')
PACK=WT/'docs/vm_tlb/review_packs/AWMA_R17_GRAPH_SEARCH_109_V1'
HDF=ROOT/'dataset/glove-100-angular.hdf5'
BIN=ROOT/'dataset/glove-100-inner'

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):
            h.update(b)
    return h.hexdigest()

def memmap(path,dtype):
    with path.open('rb') as f: n,d=struct.unpack('<ii',f.read(8))
    assert path.stat().st_size==8+n*d*np.dtype(dtype).itemsize
    return np.memmap(path,dtype=dtype,mode='r',offset=8,shape=(n,d)),(n,d)

def main():
    PACK.mkdir(parents=True,exist_ok=True)
    with h5py.File(HDF,'r') as h:
        assert h.attrs['distance']=='angular'
        shape={k:list(h[k].shape) for k in ('train','test','neighbors','distances')}
        dtype={k:str(h[k].dtype) for k in ('train','test','neighbors','distances')}
        assert shape['train']==[1183514,100] and shape['test']==[10000,100]
        assert shape['neighbors']==shape['distances']==[10000,100]
        assert dtype=={'train':'float32','test':'float32','neighbors':'int32','distances':'float32'}
        original_base=h['train'][:10]
        original_query=h['test'][:256]
        original_gt=h['neighbors'][:256]
    base,bs=memmap(BIN/'base.fbin','<f4')
    query,qs=memmap(BIN/'query.fbin','<f4')
    gt,gs=memmap(BIN/'groundtruth.neighbors.ibin','<i4')
    gd,gds=memmap(BIN/'groundtruth.distances.fbin','<f4')
    assert bs==(1183514,100) and qs==(10000,100) and gs==gds==(10000,100)
    assert np.array_equal(gt[:256],original_gt)
    expected_base=original_base/np.linalg.norm(original_base,axis=1,keepdims=True)
    expected_query=original_query/np.linalg.norm(original_query,axis=1,keepdims=True)
    assert np.array_equal(base[:10],expected_base)
    assert np.array_equal(query[:256],expected_query)
    assert np.isfinite(base[:]).all() and np.isfinite(query[:256]).all()
    norm_max=0.0
    for off in range(0,len(base),65536):
        norms=np.linalg.norm(base[off:off+65536],axis=1)
        norm_max=max(norm_max,float(np.abs(norms-1).max()))
    assert norm_max<1e-5
    assert int(gt[:256].min())>=0 and int(gt[:256].max())<len(base)
    exact=[]
    for i in (0,1,2):
        scores=base@query[i]
        top=np.argpartition(-scores,10)[:10]
        top=top[np.argsort(-scores[top])]
        recall=len(set(map(int,top)).intersection(map(int,gt[i,:10])))/10
        exact.append({'query':i,'cosine_top10_vs_official_GT_recall':recall})
    assert all(x['cosine_top10_vs_official_GT_recall']==1.0 for x in exact)
    paths=[HDF]+[BIN/f for f in ('base.fbin','query.fbin','groundtruth.neighbors.ibin','groundtruth.distances.fbin')]
    file_records={str(p.relative_to(ROOT)):dict(size_bytes=p.stat().st_size,sha256=sha(p)) for p in paths}
    descriptor=ROOT/'source/cuvs_v26_08_01/python/cuvs_bench/cuvs_bench/config/datasets/datasets.yaml'
    converter=ROOT/'source/cuvs_v26_08_01/python/cuvs_bench/cuvs_bench/get_dataset/hdf5_to_fbin.py'
    helper=ROOT/'source/cuvs_v26_08_01/python/cuvs_bench/cuvs_bench/get_dataset/__main__.py'
    receipt={'scientific_dataset':'glove-100-angular','source_url':'https://ann-benchmarks.com/glove-100-angular.hdf5',
        'source_content_length':485413888,'source_etag':'9ef1a69a639809d4ae43efd5e6707fa1-58',
        'HDF5_attr_distance':'angular','shapes':shape,'dtypes':dtype,
        'official_converter_invocation':'python -m cuvs_bench.get_dataset --dataset glove-100-angular --normalize --dataset-path <root>',
        'official_converter_output_dir':'glove-100-inner (the helper renames angular to inner after normalization)',
        'official_descriptor_name':'glove-100-angular','official_descriptor_distance':'euclidean',
        'scientific_metric':'sqeuclidean on L2-unit-normalized vectors; rank-equivalent to cosine/angular',
        'redistribution_license_status':'NOT_STATED_IN_OFFICIAL_CUVS_DESCRIPTOR_OR_HDF5; retained as private research authority',
        'max_base_norm_abs_error':norm_max,'first_256_GT_exact_binary_match':True,
        'independent_cosine_top10_sanity':exact,'source_commit':'25b1be43a8c127e5ab6d2f29f20c62dbfd3351ab',
        'descriptor_sha256':sha(descriptor),'converter_sha256':sha(converter),'helper_sha256':sha(helper),
        'files':file_records,'holdout_query_values_inspected':False,
        'holdout_performance_inspected':False}
    (PACK/'DATASET_RECEIPT.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    split=[]
    for i in range(512):
        split.append({'query_id':i,'role':'DISCOVERY' if i<256 else 'SEALED_HOLDOUT',
            'dataset_sha256':file_records['dataset/glove-100-inner/query.fbin']['sha256'],
            'groundtruth_sha256':file_records['dataset/glove-100-inner/groundtruth.neighbors.ibin']['sha256']})
    with (PACK/'QUERY_SPLIT.tsv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(split[0]),delimiter='\t',lineterminator='\n')
        w.writeheader();w.writerows(split)
    print(json.dumps({'shapes':shape,'file_sha256':{k:v['sha256'] for k,v in file_records.items()},
        'norm_max_error':norm_max,'exact_sanity':exact},sort_keys=True))

if __name__=='__main__':main()
