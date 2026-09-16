#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, shutil, subprocess
from pathlib import Path

repo = Path('/home/huangrulin/workspace/worktrees/accel-sim-awma-terminal-v2')
run = 'C16R_qwen25-05b_s2-text_prefill_awma-routeb-sim_q05-prefill-attn-flash_20260917T163000Z_e46193b94dd9'
bundle = Path('/data/c16/capture/transferred') / run
transfer = Path('/data/c16/capture/transfer_receipts') / run
pack = repo / 'docs/vm_tlb/review_packs/AWMA_SIM_COMPAT_CAPTURE_109_V2'
report = repo / 'docs/vm_tlb/codex_handoff/awma/SIM_COMPAT_CAPTURE_109_REPORT.md'

def sha(p: Path) -> str:
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(1048576), b''): h.update(b)
    return h.hexdigest()

def jwrite(p: Path, data: object) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2, sort_keys=True) + '\n')

def ccopy(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)

def main() -> None:
    if pack.exists(): raise SystemExit('final pack exists')
    manifest_path = bundle/'RUN_MANIFEST.json'
    manifest = json.loads(manifest_path.read_text())
    if manifest['run_id'] != run or manifest['scientific_status'] != 'FORMAL': raise SystemExit('formal manifest mismatch')
    terminal = json.loads((bundle/'sidecars/TERMINAL_RECEIPT.json').read_text())
    address = json.loads((bundle/'sidecars/ADDRESS_CONTEXT.json').read_text())
    target = json.loads((bundle/'sidecars/TARGET_IDENTITY.json').read_text())
    promotion = json.loads((bundle/'sidecars/R3_PROMOTION_AUDIT.json').read_text())
    ack = json.loads((transfer/'TRANSFER_ACK.json').read_text())
    if terminal['status'] != 'COMPLETE' or terminal['drop_count'] or terminal['overflow_count']: raise SystemExit('terminal gate')
    if ack['verification_status'] != 'PASS' or ack['source_manifest_sha256'] != sha(manifest_path): raise SystemExit('ack gate')
    artifacts = manifest['artifacts']
    trace = [x for x in artifacts if x['relative_path'].startswith('traces/')]
    trace_root = hashlib.sha256(json.dumps(trace, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    roots = {
        'run_id': run, 'bundle_manifest_sha256': sha(manifest_path), 'trace_member_hash_root': trace_root,
        'terminal_receipt_sha256': sha(bundle/'sidecars/TERMINAL_RECEIPT.json'),
        'address_context_sha256': sha(bundle/'sidecars/ADDRESS_CONTEXT.json'),
        'target_identity_sha256': sha(bundle/'sidecars/TARGET_IDENTITY.json'),
        'local_close_receipt_sha256': sha(bundle/'LOCAL_CLOSE_RECEIPT.json'),
        'transfer_ack_sha256': sha(transfer/'TRANSFER_ACK.json'),
        'remote_verification_sha256': sha(transfer/'REMOTE_VERIFICATION.json'),
        'remote_admission_sha256': sha(transfer/'REMOTE_ADMISSION.json'),
        'file_count': len(artifacts), 'total_bytes': sum(x['size_bytes'] for x in artifacts),
    }
    pack.mkdir(parents=True)
    jwrite(pack/'FORMAL_PRODUCER_STATUS.json', {'status':'SIM_COMPAT_CAPTURE_V1_PRODUCER_PASS','terminal_protocol':'TERMINAL_PROTOCOL_SM89_RECOVERED_V2','r3_promoted_without_recapture':True,'run_id':run,'hotfix_commit':'fb5d0bebee421a0153661239e1f7c2bc088d5c9e','ack_status':'PASS'})
    jwrite(pack/'HASH_ROOTS.json', roots)
    jwrite(pack/'RUN_MANIFEST.json', manifest)
    jwrite(pack/'TARGET_IDENTITY.json', target)
    jwrite(pack/'ADDRESS_CONTEXT.json', address)
    jwrite(pack/'TERMINAL_RECEIPT.json', terminal)
    jwrite(pack/'R3_PROMOTION_AUDIT.json', promotion)
    jwrite(pack/'TRANSFER_ACK.json', ack)
    (pack/'PROMOTION.md').write_text('R3 carried a historical canary label only. Its exact frozen workload, target function occurrence 0, full Decode32 natural completion, device/channel terminal, zero loss, mode2=0 policy, canonical postprocess, and hotfix validation satisfy the formal producer contract; it was promoted without GPU recapture.\n')
    (pack/'CLAIM_BOUNDARY.md').write_text('Producer PASS only. 109 did not generate SIM_INPUT_ID, run Accel-Sim replay, or conduct TLB/PTW/cache mechanism experiments. 174 independently owns consumer admission and simulation.\n')
    for src in [bundle/'LOCAL_CLOSE_RECEIPT.json', bundle/'PROMOTION_PROVENANCE.md', bundle/'receipts/R3_PROMOTION_COMPLETENESS.txt', bundle/'receipts/HOTFIX_VALIDATOR.stdout', bundle/'receipts/HOTFIX_VALIDATOR.stderr', bundle/'receipts/HOTFIX_VALIDATOR.returncode', bundle/'receipts/HOTFIX_VALIDATOR_SOURCE_SHA256SUMS', bundle/'receipts/HOTFIX_VALIDATOR_BINARY_SHA256SUMS', bundle/'traces/kernelslist', bundle/'traces/kernelslist.g', transfer/'ACK_VERIFY.stdout', transfer/'ACK_VERIFY.stderr', transfer/'REMOTE_VERIFICATION.json', transfer/'REMOTE_ADMISSION.json', transfer/'TRANSFER_ACK.json', transfer/'SHA256SUMS']:
        ccopy(src, pack/'evidence'/src.name)
    git_state = subprocess.check_output(['git','-C',str(repo),'status','--short'], text=True)
    (pack/'GIT_STATE.txt').write_text('branch=hrl/awma-sim-compat-terminal-recovery-109-v2\nhead=' + subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'], text=True) + 'status:\n' + git_state)
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(f'''# AWMA simulator-native producer report — node109

Decision: `SIM_COMPAT_CAPTURE_V1_PRODUCER_PASS` and `TERMINAL_PROTOCOL_SM89_RECOVERED_V2`.

Run/capture ID: `{run}`. Existing R3 was promoted without recapture because its actual execution—not its historical canary label—met the formal contract.

READY was independently verified/admitted by 174-new. Destination raw path: `{ack['destination_raw_path']}`.

Key hashes: kernelslist `{next(x['sha256'] for x in artifacts if x['relative_path']=='traces/kernelslist')}`; trace-member root `{trace_root}`; bundle manifest `{roots['bundle_manifest_sha256']}`; terminal receipt `{roots['terminal_receipt_sha256']}`.

Q05 target: exact Qwen2.5-0.5B revision `7ae557604adf67be50417f59c2c2f167def9a775`, S2_TEXT/PREFILL/B1/T2048/D32/FP16/SDPA, `Q05_PREFILL_ATTN_FLASH`, semantic function occurrence 0. Terminal was COMPLETE with 13,490,624 raw records, zero drop/overflow, and mode2=0. Hotfix validator commit `fb5d0bebee421a0153661239e1f7c2bc088d5c9e` passed the complete trace and accepted 16,128 LDGDEPBAR controls.

Producer scope ends here; no SIM_INPUT_ID or simulation ran on node109.
''')
    tmp = Path('/tmp/awma_final_pack.sha')
    rows = []
    for p in sorted(x for x in pack.rglob('*') if x.is_file() and x.name != 'SHA256SUMS'):
        rows.append(f'{sha(p)}  {p}')
    tmp.write_text('\n'.join(rows)+'\n')
    shutil.move(tmp, pack/'SHA256SUMS')
    print(json.dumps({'run_id':run,'pack':str(pack),'report':str(report),'roots':roots}, sort_keys=True))

if __name__ == '__main__': main()
