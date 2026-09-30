#!/usr/bin/env python3
"""Close R17 quality-gated raw/index/dataset authority on node164."""
import csv
import hashlib
import json
import subprocess
from pathlib import Path

ROOT=Path('/data/c16/awma/r17_graph_search_20260930')
WT=Path('/home/huangrulin/workspace/worktrees/accel-sim-awma-r17-graph-search-native-109-v1')
PACK=WT/'docs/vm_tlb/review_packs/AWMA_R17_GRAPH_SEARCH_109_V1'
REPORT=WT/'docs/vm_tlb/codex_handoff/awma/AWMA_R17_GRAPH_SEARCH_109_V1.md'
TOOLS=WT/'util/vm_tlb/awma/r17_graph_search'
DEST='/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/r17_graph_search_109_v1_20260930'
HOST='hrl174new'  # accepted storage gateway only, no simulator activity

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):
            h.update(b)
    return h.hexdigest()

def run(*args):
    print('RUN',' '.join(args),flush=True)
    subprocess.run(args,check=True)

def main():
    dataset=json.loads((PACK/'DATASET_RECEIPT.json').read_text())
    index=json.loads((PACK/'INDEX_RECEIPT.json').read_text())
    runtime=json.loads((PACK/'SOURCE_RUNTIME_RECEIPT.json').read_text())
    screen=json.loads((ROOT/'raw/f2_f3_screen_summary.json').read_text())
    assert runtime['source_commit']=='25b1be43a8c127e5ab6d2f29f20c62dbfd3351ab'
    assert index['graph_degree']==64 and index['intermediate_graph_degree']==128
    assert screen['eligible_Q1_grid_count']==0 and screen['Q1_STRONG']=='NONE_RECALL_GATE_FAIL'
    assert len(screen['quality_summary'])==11 and screen['Q1_grid_count']==6
    assert dataset['holdout_query_values_inspected'] is False
    assert sha(ROOT/'index/cagra_glove100_g64_ig128_sqeuclidean.bin')==index['index_serialized_sha256']
    for relative,identity in dataset['files'].items():
        assert sha(ROOT/relative)==identity['sha256']
    with (PACK/'DISCOVERY_TIMING.tsv').open(newline='') as f:
        assert len(list(csv.DictReader(f,delimiter='\t')))==55
    with (ROOT/'raw/f2_f3_discovery_timing_per_batch.tsv').open(newline='') as f:
        assert len(list(csv.DictReader(f,delimiter='\t')))==9050
    tools={p.name:sha(p) for p in sorted(TOOLS.glob('*.py'))}
    receipt={'stage':'AWMA_R17_GRAPH_SEARCH_109_V1',
      'starting_head':'3e5041f8a04275270fe39032252ea318a368a773',
      'execution_branch':'hrl/awma-r17-graph-search-native-109-v1',
      'node':'109','GPU':'RTX4080 SM89','GPU_lock':'/data/c16/locks/c16_gpu_campaign.lock',
      'GPU_lock_scope':'all actual CUDA index-build and search commands used outer flock; subprocesses exited and released the lock',
      'runtime':'cuvs-cu12==26.8.1','source_commit':runtime['source_commit'],
      'runtime_wheel_sha256':runtime['stable_runtime_wheel_sha256'],
      'dataset_source_sha256':dataset['files']['dataset/glove-100-angular.hdf5']['sha256'],
      'normalized_base_sha256':dataset['files']['dataset/glove-100-inner/base.fbin']['sha256'],
      'groundtruth_sha256':dataset['files']['dataset/glove-100-inner/groundtruth.neighbors.ibin']['sha256'],
      'graph_sha256':index['graph_sha256'],'serialized_index_sha256':index['index_serialized_sha256'],
      'actual_index_builds':1,'prebuild_assertion_attempts':1,
      'screen_distinct_jobs':11,'quality_gate':0.95,
      'best_Q1_grid_recall_at_10':max(float(x['recall_at_10']) for x in screen['quality_summary'] if x['arm']=='F2_Q1_AUTO' or x['arm'].startswith('F3_Q1_')),
      'Q1_STRONG':'NONE_RECALL_GATE_FAIL','formal_timing_arms':0,'persistent_jobs':0,
      'C_or_CPP_fallback_jobs':0,'NSYS_jobs':0,'NCU_jobs':0,'NVBit_jobs':0,'AccelSim_jobs':0,
      'holdout_queries_examined':0,'decision':'R17_RECALL_GATE_NOT_QUALIFIED',
      'tool_sha256':tools,'node164_path':DEST,'node164_gateway':'hrl174new storage-only SSH'}
    (PACK/'RUN_RECEIPTS.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    rows=[]
    for kind in ('dataset','index','raw','wheels'):
        for p in sorted((ROOT/kind).rglob('*')):
            if p.is_file():
                rows.append({'node164_relative_path':str(p.relative_to(ROOT)),
                    'size_bytes':p.stat().st_size,'sha256':sha(p),'kind':kind})
    with (PACK/'RAW_DATA_INDEX.tsv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n')
        w.writeheader();w.writerows(rows)
    pack_lines=[]
    for p in sorted(PACK.iterdir()):
        if p.is_file() and p.name!='SHA256SUMS':pack_lines.append(f'{sha(p)}  {p.name}\n')
    (PACK/'SHA256SUMS').write_text(''.join(pack_lines))
    manifest=[f"{x['sha256']}  {x['node164_relative_path']}\n" for x in rows]
    for p in sorted(PACK.iterdir()):
        if p.is_file():manifest.append(f'{sha(p)}  review_pack/{p.name}\n')
    manifest.append(f'{sha(REPORT)}  codex_handoff/{REPORT.name}\n')
    (ROOT/'NODE164_SHA256SUMS').write_text(''.join(manifest))
    run('ssh',HOST,'mkdir','-p',DEST+'/dataset',DEST+'/index',DEST+'/raw',DEST+'/wheels',DEST+'/review_pack',DEST+'/codex_handoff')
    for kind in ('dataset','index','raw','wheels'):
        run('rsync','-rt','--partial',str(ROOT/kind)+'/',f'{HOST}:{DEST}/{kind}/')
    run('rsync','-rt',str(PACK)+'/',f'{HOST}:{DEST}/review_pack/')
    run('rsync','-t',str(REPORT),f'{HOST}:{DEST}/codex_handoff/{REPORT.name}')
    run('rsync','-t',str(ROOT/'NODE164_SHA256SUMS'),f'{HOST}:{DEST}/NODE164_SHA256SUMS')
    check=subprocess.run(['ssh',HOST,f'cd {DEST} && sha256sum -c NODE164_SHA256SUMS'],check=True,capture_output=True,text=True)
    lines=check.stdout.splitlines()
    assert len(lines)==len(manifest) and all(x.endswith(': OK') for x in lines)
    print(f'NODE164_VERIFIED={len(lines)} RAW_ASSET_FILES={len(rows)} DEST={DEST}',flush=True)

if __name__=='__main__':main()
