#!/usr/bin/env python3
"""Close VLA RTC Lane F raw/asset authority and publish through node164 gateway."""
import csv
import hashlib
import json
import subprocess
from pathlib import Path

ROOT=Path('/data/c16/awma/vla_rtc_vjp_boundary_20260930')
WT=Path('/home/huangrulin/workspace/worktrees/accel-sim-awma-vla-rtc-vjp-boundary-109-v1')
PACK=WT/'docs/vm_tlb/review_packs/AWMA_VLA_RTC_VJP_BOUNDARY_109_V1'
REPORT=WT/'docs/vm_tlb/codex_handoff/awma/AWMA_VLA_RTC_VJP_BOUNDARY_109_V1.md'
TOOLS=WT/'util/vm_tlb/awma/vla_rtc_vjp_boundary'
DEST='/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/vla_rtc_vjp_boundary_109_v1_20260930'
HOST='hrl174new'  # accepted storage gateway only; never run simulator

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
    assert sha(ROOT/'assets/model/model.safetensors')=='9a9f6413e42c0f332fccbce9a0dc796af2790f82cf002f791cdbf7e01e1afca8'
    graph=json.loads((ROOT/'raw/f0/real_model_graph_canary.json').read_text())
    a0=json.loads((ROOT/'raw/f2/a0_timing_summary.json').read_text())
    a1=json.loads((ROOT/'raw/f4/a1_static_timing_summary.json').read_text())
    numeric=json.loads((ROOT/'raw/f4/a1_static_numeric_receipt.json').read_text())
    freeze=json.loads((ROOT/'raw/f1/window_freeze.json').read_text())
    assert graph['vjp_calls']==10 and graph['expert_backward_hook_fires']==10
    assert numeric['status']=='A1_FULL_VJP_NUMERIC_QUALIFIED'
    assert numeric['trajectory_and_graph_gate']['vjp_calls']==30
    assert numeric['trajectory_and_graph_gate']['trajectory_pass']
    assert a0['formal_rows']==a1['formal_rows']==60
    assert freeze['sealed_validation_episode']==1 and freeze['validation_observation_not_decoded']
    assert not list((ROOT/'raw').rglob('*validation_observation*'))
    assert not list((ROOT/'raw/f5').glob('*.nsys-rep'))
    with (PACK/'A0_TIMING.tsv').open(newline='') as f:
        assert sum(r['status']=='FORMAL' for r in csv.DictReader(f,delimiter='\t'))==60
    with (PACK/'A1_TIMING.tsv').open(newline='') as f:
        assert sum(r['status']=='FORMAL' for r in csv.DictReader(f,delimiter='\t'))==60
    tool_hashes={p.name:sha(p) for p in sorted(TOOLS.iterdir()) if p.is_file() and p.suffix in ('.py','.diff')}
    receipt={
      'stage':'AWMA_VLA_RTC_VJP_BOUNDARY_109_V1',
      'execution_branch':'hrl/awma-vla-rtc-vjp-boundary-109-v1',
      'starting_head':'6586b2530c38ccd3e7aa620e14990f0c1274bbef',
      'node':'109','gpu':'NVIDIA GeForce RTX 4080 SM89',
      'gpu_lock':'/data/c16/locks/c16_gpu_campaign.lock',
      'gpu_lock_scope':'every actual CUDA and NSYS target command used outer flock; all subprocesses exited, releasing lock',
      'torch':'2.11.0+cu130','transformers':'5.5.4','lerobot':'0.6.2',
      'source_identity_file_sha256':sha(PACK/'SOURCE_IDENTITY.json'),
      'input_identity_file_sha256':sha(PACK/'INPUT_RECEIPT.json'),
      'checkpoint_sha256':sha(ROOT/'assets/model/model.safetensors'),
      'dataset_revision':'a1aaacb7f6cd6ee5fb43120f673cebb0cfea7dd4',
      'episode_A':0,'episode_B_sealed':1,'delay_frames':4,
      'full_vjp_graph_canary':{'vjp_calls':graph['vjp_calls'],
          'expert_backward_hook_fires':graph['expert_backward_hook_fires'],
          'parameter_grad_count':graph['parameter_grad_count']},
      'A0_timing':{'formal_samples':60,'guided_median_ms':a0['guided_chunk_median_ms'],
                   'guided_MAD_ms':a0['guided_chunk_MAD_ms']},
      'A1_timing':{'formal_samples':60,'guided_median_ms':a1['guided_chunk_median_ms'],
                   'guided_MAD_ms':a1['guided_chunk_MAD_ms'],
                   'trajectory_comparisons':numeric['trajectory_and_graph_gate']['trajectory_comparisons'],
                   'max_abs_vs_A0':a1['max_abs_vs_A0_reference']},
      'compiler_canary':'one author max-autotune attempt failed CUDA misaligned address before qualified output; no mode search',
      'nsys_capture_attempts':1,'nsys_version':'2024.6.2','nsys_report_status':'NO_REPORT_GENERATED',
      'ncu_jobs':0,'nvbit_jobs':0,'accel_sim_jobs':0,'node174_sim_jobs':0,
      'validation_episodes_opened':0,
      'decision':'VLA_VJP_RESULT_MIXED_NEEDS_REVIEW',
      'tool_sha256':tool_hashes,
      'node164_path':DEST,'node164_gateway':'hrl174new storage-only SSH',
    }
    (PACK/'RUN_RECEIPTS.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    rows=[]
    for kind in ('assets','raw'):
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
    manifest=[f"{r['sha256']}  {r['node164_relative_path']}\n" for r in rows]
    for p in sorted(PACK.iterdir()):
        if p.is_file():manifest.append(f'{sha(p)}  review_pack/{p.name}\n')
    manifest.append(f'{sha(REPORT)}  codex_handoff/{REPORT.name}\n')
    (ROOT/'NODE164_SHA256SUMS').write_text(''.join(manifest))
    run('ssh',HOST,'mkdir','-p',DEST+'/assets',DEST+'/raw',DEST+'/review_pack',DEST+'/codex_handoff')
    for kind in ('assets','raw'):
        run('rsync','-rt','--partial',str(ROOT/kind)+'/',f'{HOST}:{DEST}/{kind}/')
    run('rsync','-rt',str(PACK)+'/',f'{HOST}:{DEST}/review_pack/')
    run('rsync','-t',str(REPORT),f'{HOST}:{DEST}/codex_handoff/{REPORT.name}')
    run('rsync','-t',str(ROOT/'NODE164_SHA256SUMS'),f'{HOST}:{DEST}/NODE164_SHA256SUMS')
    check=subprocess.run(['ssh',HOST,f'cd {DEST} && sha256sum -c NODE164_SHA256SUMS'],check=True,capture_output=True,text=True)
    lines=check.stdout.splitlines()
    assert len(lines)==len(manifest) and all(x.endswith(': OK') for x in lines)
    print(f'NODE164_VERIFIED={len(lines)} ASSET_RAW_FILES={len(rows)} DEST={DEST}',flush=True)

if __name__=='__main__':main()
