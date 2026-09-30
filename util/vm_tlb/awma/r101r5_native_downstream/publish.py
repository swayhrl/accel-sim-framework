#!/usr/bin/env python3
"""Close and publish R101R5 raw/review authority through accepted node164 gateway."""
import csv
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path('/data/c16/awma/r101r5_native_post_l1_downstream_20260930')
RAW = ROOT / 'raw'
WT = Path('/home/huangrulin/workspace/worktrees/accel-sim-awma-r101r5-native-post-l1-downstream-109-v1')
PACK = WT / 'docs/vm_tlb/review_packs/AWMA_R101R5_NATIVE_POST_L1_DOWNSTREAM_109_V1'
REPORT = WT / 'docs/vm_tlb/codex_handoff/awma/AWMA_R101R5_NATIVE_POST_L1_DOWNSTREAM_109_V1.md'
DEST = '/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/r101r5_native_post_l1_downstream_109_v1_20260930'
HOST = 'hrl174new'  # historical node164 storage gateway; no 174 simulation

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):
            h.update(b)
    return h.hexdigest()

def run(*args):
    print('RUN', ' '.join(args), flush=True)
    subprocess.run(args, check=True)

def main():
    accepted = {'L512.ncu-rep':'a73f9db4638171b5236194d1541c1943c849714c9671a85e82e5700a1ae403d8',
                'L512.raw.csv':'fba83ccbc68a7b833a4d645a3d4f4044672337a68a403fe41a43478a712894d5',
                'PROFILE_TARGET_RECEIPT.json':'30e6226256c7d8bdc8e89d90e88493798e67f673ab14173c829890f000a5738d'}
    old = Path('/data/c16/awma/r101_fixed_ns_intermediate_lifecycle_20260927/raw/ncu/L512')
    for name, expected in accepted.items(): assert sha(old/name) == expected
    commands = json.loads((RAW/'phase_b/command_receipts.json').read_text())
    assert len(commands)==3 and all(x['returncode']==0 for x in commands)
    assert [x['target'] for x in commands] == ['XXT_kernel','ba_plus_cAA_kernel','bmm_add_kernel']
    assert [x['accepted_launch_id'] for x in commands] == [6,7,8]
    assert all(x['replayer_passes']=='11.000000' for x in commands)
    assert not (RAW/'phase_b/compute_apps_at_admission.txt').read_text().strip()
    for x in commands:
        assert sha(RAW/'phase_b'/f"{x['target']}.ncu-rep") == x['report_sha256']
        receipt = json.loads((RAW/'phase_b'/f"{x['target']}.numerical_receipt.json").read_text())
        assert receipt['same_numerical_output_with_author_tolerance']
    tools = WT/'util/vm_tlb/awma/r101r5_native_downstream'
    receipt = {
        'stage':'AWMA_R101R5_NATIVE_POST_L1_DOWNSTREAM_REALISM_CHECK_V1',
        'scientific_parent':'d96a64da8311c1bdee8f23f3d83ce665395060d1',
        'handoff_head':'ef01d870d90eae89f529bad31a882debd1139b2b',
        'host':'node109', 'gpu':'RTX4080 SM89',
        'accepted_input_sha256':'1b0496a115ddaa647f8896a20e5711a125e02ab8bb2f7d47dc5f2fbd7693a234',
        'accepted_himuon_commit':'af89eda9a0176effed99e1fe19cc1f8a1a2c9588',
        'accepted_existing_ncu_hashes':accepted,
        'accepted_cubin_sha256':'NOT_RECORDED_IN_ACCEPTED_RECEIPT',
        'gpu_lock':'/data/c16/locks/c16_gpu_campaign.lock',
        'gpu_lock_scope':'actual device metric/section capability query and all three serial bounded NCU jobs; subprocess exited and lock released',
        'ncu_version':'2025.1.1',
        'ncu_cache_control':'none', 'ncu_clock_control':'none',
        'ncu_pipeline_boost_state':'dynamic',
        'new_ncu_jobs':commands,
        'tools_sha256':{p.name:sha(p) for p in sorted(tools.glob('*.py'))},
        'phase_a_tool_sha256':sha(WT/'util/vm_tlb/awma/r101r5_phase_a_audit.py'),
        'decision':'NATIVE_POST_L1_DOWNSTREAM_SUPPORT_NOT_OBSERVED',
        'node164_path':DEST,
        'node164_gateway':'hrl174new storage-only SSH; no 174 simulation',
    }
    (PACK/'RUN_RECEIPTS.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    raw_rows=[]
    for p in sorted(RAW.rglob('*')):
        if p.is_file():
            raw_rows.append({'node164_relative_path':str(p.relative_to(ROOT)),
                             'size_bytes':p.stat().st_size,'sha256':sha(p),'kind':'raw'})
    with (PACK/'RAW_DATA_INDEX.tsv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(raw_rows[0]),delimiter='\t',lineterminator='\n')
        w.writeheader();w.writerows(raw_rows)
    lines=[]
    for p in sorted(PACK.iterdir()):
        if p.is_file() and p.name!='SHA256SUMS':lines.append(f'{sha(p)}  {p.name}\n')
    (PACK/'SHA256SUMS').write_text(''.join(lines))
    manifest_lines=[f"{x['sha256']}  {x['node164_relative_path']}\n" for x in raw_rows]
    for p in sorted(PACK.iterdir()):
        if p.is_file():manifest_lines.append(f'{sha(p)}  review_pack/{p.name}\n')
    manifest_lines.append(f'{sha(REPORT)}  codex_handoff/{REPORT.name}\n')
    manifest = ROOT/'NODE164_SHA256SUMS'
    manifest.write_text(''.join(manifest_lines))
    run('ssh',HOST,'mkdir','-p',DEST+'/raw',DEST+'/review_pack',DEST+'/codex_handoff')
    run('rsync','-rt','--partial',str(RAW)+'/',f'{HOST}:{DEST}/raw/')
    run('rsync','-rt',str(PACK)+'/',f'{HOST}:{DEST}/review_pack/')
    run('rsync','-t',str(REPORT),f'{HOST}:{DEST}/codex_handoff/{REPORT.name}')
    run('rsync','-t',str(manifest),f'{HOST}:{DEST}/NODE164_SHA256SUMS')
    result=subprocess.run(['ssh',HOST,f'cd {DEST} && sha256sum -c NODE164_SHA256SUMS'],check=True,capture_output=True,text=True)
    checks=result.stdout.splitlines()
    assert len(checks)==len(manifest_lines) and all(x.endswith(': OK') for x in checks)
    print(f'NODE164_VERIFIED={len(checks)} RAW_FILES={len(raw_rows)} DEST={DEST}',flush=True)

if __name__=='__main__':main()
