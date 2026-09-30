#!/usr/bin/env python3
"""CPU-only exact verification of accepted R17 V1 scientific authority."""
import csv
import hashlib
import json
import subprocess
from pathlib import Path

OLD=Path('/data/c16/awma/r17_graph_search_20260930')
NEW=Path('/data/c16/awma/r17r1_quality_requalification_20260930')
WT=Path('/home/huangrulin/workspace/worktrees/accel-sim-awma-r17r1-quality-requalification-109-v1')
PARENT=Path('/home/huangrulin/workspace/worktrees/accel-sim-awma-r17-graph-search-native-109-v1/docs/vm_tlb/review_packs/AWMA_R17_GRAPH_SEARCH_109_V1')
PACK=WT/'docs/vm_tlb/review_packs/AWMA_R17R1_GRAPH_SEARCH_109_V2'

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):
            h.update(b)
    return h.hexdigest()

def git(repo,*args):
    return subprocess.check_output(['git','-C',str(repo),*args],text=True).strip()

def main():
    NEW.mkdir(parents=True,exist_ok=True)
    PACK.mkdir(parents=True,exist_ok=True)
    assert git(PARENT.parents[3],'rev-parse','HEAD')=='78874fbfd767ec1321d41a04e4c51589a3c07298'
    index=json.loads((PARENT/'INDEX_RECEIPT.json').read_text())
    data=json.loads((PARENT/'DATASET_RECEIPT.json').read_text())
    runtime=json.loads((PARENT/'SOURCE_RUNTIME_RECEIPT.json').read_text())
    assert runtime['source_commit']=='25b1be43a8c127e5ab6d2f29f20c62dbfd3351ab'
    assert runtime['cuvs']=='26.08.01'
    assert git(OLD/'source/cuvs_v26_08_01','rev-parse','HEAD')==runtime['source_commit']
    for relative,receipt in data['files'].items():
        path=OLD/relative
        assert path.stat().st_size==receipt['size_bytes'] and sha(path)==receipt['sha256']
    old_index=OLD/'index/cagra_glove100_g64_ig128_sqeuclidean.bin'
    assert sha(old_index)=='6cddddb35f63d31b1308d1411d76aabcef910b11caea1778ca823f4fb63e7151'
    assert index['graph_sha256']=='a68d4a2905fcab13a40872db73165fb4271a493f09b9fd61f5f1e9a401f073b8'
    assert index['graph_degree']==64 and index['intermediate_graph_degree']==128
    with (PARENT/'QUERY_SPLIT.tsv').open(newline='') as f:
        split=list(csv.DictReader(f,delimiter='\t'))
    assert len(split)==512
    assert [int(x['query_id']) for x in split if x['role']=='DISCOVERY']==list(range(256))
    assert [int(x['query_id']) for x in split if x['role']=='SEALED_HOLDOUT']==list(range(256,512))
    yaml=OLD/'source/cuvs_v26_08_01/python/cuvs_bench/cuvs_bench/config/algos/cuvs_cagra.yaml'
    content=yaml.read_text()
    assert 'graph_build_algo: ["NN_DESCENT"]' in content
    assert 'itopk: [32, 64, 128, 256, 512]' in content
    assert 'search_width: [1, 2, 4, 8, 16, 32, 64]' in content
    wheel=OLD/'wheels/cuvs_cu12-26.8.1-cp311-abi3-manylinux_2_24_x86_64.manylinux_2_28_x86_64.whl'
    assert sha(wheel)==runtime['stable_runtime_wheel_sha256']
    receipt={'stage':'AWMA_R17R1_QUALITY_REQUALIFICATION_109_V1',
      'starting_head':'35ae51220bdde8adccfddde847356a65578d465d',
      'scientific_parent_commit':'78874fbfd767ec1321d41a04e4c51589a3c07298',
      'parent_index_graph_sha256':index['graph_sha256'],
      'parent_index_serialized_sha256':sha(old_index),
      'parent_index_path':str(old_index),'parent_index_build_algo':'IVF_PQ Python default',
      'parent_data_files':{relative:receipt for relative,receipt in data['files'].items()},
      'source_commit':runtime['source_commit'],'source_tag':'v26.08.01',
      'runtime_wheel_sha256':sha(wheel),'runtime_env_path':str(OLD/'env'),
      'benchmark_base_yaml_sha256':sha(yaml),
      'benchmark_base_build_algo':'NN_DESCENT',
      'benchmark_base_itopk':[32,64,128,256,512],
      'benchmark_base_search_width':[1,2,4,8,16,32,64],
      'recall_at_10_gate':0.95,'discovery_queries':[0,255],
      'sealed_holdout_queries':[256,511],
      'accepted_assets_verified':True,'no_GPU_work_in_parent_audit':True}
    (PACK/'PARENT_AUTHORITY.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'index_sha256':receipt['parent_index_serialized_sha256'],
      'dataset_sha256':data['files']['dataset/glove-100-angular.hdf5']['sha256'],
      'benchmark_yaml_sha256':receipt['benchmark_base_yaml_sha256']},sort_keys=True))

if __name__=='__main__':main()
