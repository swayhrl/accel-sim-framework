#!/usr/bin/env python3
"""Hash-close R17R1 quality/formal raw and publish without duplicating V1 assets."""
import csv
import hashlib
import json
import subprocess
from pathlib import Path

OLD=Path('/data/c16/awma/r17_graph_search_20260930')
NEW=Path('/data/c16/awma/r17r1_quality_requalification_20260930')
WT=Path('/home/huangrulin/workspace/worktrees/accel-sim-awma-r17r1-quality-requalification-109-v1')
PACK=WT/'docs/vm_tlb/review_packs/AWMA_R17R1_GRAPH_SEARCH_109_V2'
REPORT=WT/'docs/vm_tlb/codex_handoff/awma/AWMA_R17R1_GRAPH_SEARCH_109_V2.md'
TOOLS=WT/'util/vm_tlb/awma/r17r1_quality'
PARENT_DEST='/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/r17_graph_search_109_v1_20260930'
DEST='/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/r17r1_quality_requalification_109_v1_20261001'
HOST='hrl174new'  # accepted node164 storage gateway only

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
    parent=json.loads((PACK/'PARENT_AUTHORITY.json').read_text())
    a=json.loads((NEW/'raw/stage_a_summary.json').read_text())
    c=json.loads((NEW/'raw/stage_c_summary.json').read_text())
    d=json.loads((NEW/'raw/stage_d_summary.json').read_text())
    analysis=json.loads((PACK/'MATCHED_ANALYSIS.json').read_text())
    assert parent['accepted_assets_verified'] and a['stage_A_pass']
    assert a['a1_qualified'] and not a['a2_triggered'] and not a['new_index_built']
    assert c['Q1_STRONG_V2']=='Q1_MULTI_512_1' and c['Resources_reused_per_process']
    assert d['holdout_inspected'] is False
    assert analysis['decision']=='R17_CAGRA_EXISTING_SOFTWARE_SUFFICIENT'
    assert sha(OLD/'index/cagra_glove100_g64_ig128_sqeuclidean.bin')==parent['parent_index_serialized_sha256']
    for relative,identity in parent['parent_data_files'].items():
        assert sha(OLD/relative)==identity['sha256']
    with (PACK/'FORMAL_Q1_TIMING.tsv').open(newline='') as f:
        assert sum(x['status']=='FORMAL' for x in csv.DictReader(f,delimiter='\t'))==30
    with (PACK/'MATCHED_Q1_Q32.tsv').open(newline='') as f:
        assert sum(x['status']=='FORMAL' for x in csv.DictReader(f,delimiter='\t'))==30
    assert not any((NEW/'index').rglob('*')),'No NN_DESCENT index should exist'
    tool_hashes={p.name:sha(p) for p in sorted(TOOLS.glob('*.py'))}
    receipt={'stage':'AWMA_R17R1_QUALITY_REQUALIFICATION_109_V1',
        'starting_head':'35ae51220bdde8adccfddde847356a65578d465d',
        'scientific_parent':'78874fbfd767ec1321d41a04e4c51589a3c07298',
        'execution_branch':'hrl/awma-r17r1-quality-requalification-109-v1',
        'node':'109','GPU':'RTX4080 SM89',
        'GPU_lock':'/data/c16/locks/c16_gpu_campaign.lock',
        'GPU_lock_scope':'every actual CUDA quality/formal/matched job used outer flock; all subprocesses exited and released lock',
        'runtime':'cuvs-cu12==26.8.1','source_commit':parent['source_commit'],
        'dataset_reused':True,'IVF_PQ_index_reused':True,
        'IVF_PQ_index_sha256':parent['parent_index_serialized_sha256'],
        'new_index_builds':0,'A1_quality_new_points':4,'A2_quality_points':0,
        'NN_DESCENT_quality_points':0,'recall_gate':0.95,
        'quality_qualified_SINGLE_512_1':0.959765625,
        'quality_qualified_MULTI_512_1':0.961328125,
        'formal_Q1_candidates':2,'formal_Q1_groups':3,
        'formal_repeats_per_arm':15,'Q1_STRONG_V2':c['Q1_STRONG_V2'],
        'stage_C_attempt0_retained_not_authoritative':True,
        'stage_C_attempt1_reused_Resources':True,
        'matched_Q1_Q32_groups':3,'matched_Q32_batches_per_repeat':8,
        'custom_stream_GPU_event_probe':'UNQUALIFIED_PROCESS_EXIT_BEFORE_VALID_SAMPLE',
        'wrapper_gate':'NOT_TRIGGERED_STAGE_D_SOFTWARE_SUFFICIENT; submit interval not pure host',
        'C_API_fallback_jobs':0,'persistent_jobs':0,'NSYS_jobs':0,'NCU_jobs':0,
        'NVBit_jobs':0,'AccelSim_jobs':0,'holdout_queries_inspected':0,
        'decision':'R17_CAGRA_EXISTING_SOFTWARE_SUFFICIENT',
        'tool_sha256':tool_hashes,'node164_parent_authority':PARENT_DEST,
        'node164_new_raw_path':DEST,'node164_gateway':'hrl174new storage-only SSH'}
    (PACK/'RUN_RECEIPTS.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    rows=[]
    for p in sorted((NEW/'raw').rglob('*')):
        if p.is_file():rows.append({'node164_relative_path':str(p.relative_to(NEW)),
                                    'size_bytes':p.stat().st_size,'sha256':sha(p),'kind':'new_raw'})
    with (PACK/'RAW_DATA_INDEX.tsv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n')
        w.writeheader();w.writerows(rows)
    parents=[
      {'node164_path':PARENT_DEST+'/dataset/glove-100-inner/base.fbin',
       'sha256':parent['parent_data_files']['dataset/glove-100-inner/base.fbin']['sha256']},
      {'node164_path':PARENT_DEST+'/dataset/glove-100-inner/query.fbin',
       'sha256':parent['parent_data_files']['dataset/glove-100-inner/query.fbin']['sha256']},
      {'node164_path':PARENT_DEST+'/dataset/glove-100-inner/groundtruth.neighbors.ibin',
       'sha256':parent['parent_data_files']['dataset/glove-100-inner/groundtruth.neighbors.ibin']['sha256']},
      {'node164_path':PARENT_DEST+'/index/cagra_glove100_g64_ig128_sqeuclidean.bin',
       'sha256':parent['parent_index_serialized_sha256']},
    ]
    (PACK/'PARENT_NODE164_JOIN.json').write_text(json.dumps(parents,indent=2,sort_keys=True)+'\n')
    pack_lines=[]
    for p in sorted(PACK.iterdir()):
        if p.is_file() and p.name!='SHA256SUMS':pack_lines.append(f'{sha(p)}  {p.name}\n')
    (PACK/'SHA256SUMS').write_text(''.join(pack_lines))
    manifest=[f"{r['sha256']}  {r['node164_relative_path']}\n" for r in rows]
    for p in sorted(PACK.iterdir()):
        if p.is_file():manifest.append(f'{sha(p)}  review_pack/{p.name}\n')
    manifest.append(f'{sha(REPORT)}  codex_handoff/{REPORT.name}\n')
    (NEW/'NODE164_SHA256SUMS').write_text(''.join(manifest))
    run('ssh',HOST,'mkdir','-p',DEST+'/raw',DEST+'/review_pack',DEST+'/codex_handoff')
    run('rsync','-rt','--partial',str(NEW/'raw')+'/',f'{HOST}:{DEST}/raw/')
    run('rsync','-rt',str(PACK)+'/',f'{HOST}:{DEST}/review_pack/')
    run('rsync','-t',str(REPORT),f'{HOST}:{DEST}/codex_handoff/{REPORT.name}')
    run('rsync','-t',str(NEW/'NODE164_SHA256SUMS'),f'{HOST}:{DEST}/NODE164_SHA256SUMS')
    check=subprocess.run(['ssh',HOST,f'cd {DEST} && sha256sum -c NODE164_SHA256SUMS'],check=True,capture_output=True,text=True)
    lines=check.stdout.splitlines()
    assert len(lines)==len(manifest) and all(x.endswith(': OK') for x in lines)
    # Read-only verification of the accepted parent assets on node164.
    for identity in parents:
        remote=subprocess.check_output(['ssh',HOST,'sha256sum',identity['node164_path']],text=True).split()[0]
        assert remote==identity['sha256'],identity['node164_path']
    print(f'NODE164_NEW_VERIFIED={len(lines)} PARENT_ASSETS_VERIFIED={len(parents)} NEW_RAW_FILES={len(rows)} DEST={DEST}',flush=True)

if __name__=='__main__':main()
