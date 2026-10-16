"""One accepted R1 reverse restore batch. Read-only unless --stage is explicit.

Writes only the dedicated shared bridge. Never imports or releases old174 data.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import fcntl
from archive_receiver import ARCHIVE, BRIDGE, LIMIT, SHARE_FLOOR, require, sha, beneath, mkdirs, atomic_json, check_resources, now
from cold_project_restore import read_zstd_jsonl, read_zstd_rows, join_file_metadata

NAME = 'R1_NATIVE_RESTORE_B001'

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--acceptance-proof', required=True)
    ap.add_argument('--full-restore-proof', required=True)
    ap.add_argument('--stage', action='store_true')
    args = ap.parse_args()
    owner = json.loads(Path(args.acceptance_proof).read_text())
    full_proof = json.loads(Path(args.full_restore_proof).read_text())
    for proof in [owner, full_proof]:
        require(re.fullmatch('[0-9a-f]{40}', proof['commit']) is not None, 'missing pinned Git publication')
        require(proof['github_readback_verified'] is True, 'missing GitHub readback')
    raw = (BRIDGE / 'V7_R1_NATIVE_RESTORE_ACCEPTED.json').read_bytes()
    require(hashlib.sha256(raw).hexdigest() == owner['receipt_sha256'], 'source acceptance changed')
    acceptance = json.loads(raw)
    request = (BRIDGE / 'V7_R1_NATIVE_RESTORE_WINDOW_REQUEST.json').read_bytes()
    require(hashlib.sha256(request).hexdigest() == acceptance['target_request_sha256'], 'accepted request mismatch')
    require(acceptance['source_action'] == 'SOURCE_KEEP' and acceptance['source_release_authorized'] is False,
            'restore cannot authorize source release')
    full_raw = (ARCHIVE / 'infrastructure/project_receipts/R1_FULL_CONTENT_RESTORE_8556dd125ac2.json').read_bytes()
    require(hashlib.sha256(full_raw).hexdigest() == full_proof['receipt_sha256'], 'full restore proof mismatch')
    full = json.loads(full_raw)
    require(full['all_files_dest_verified'] and full['verified_restore_bytes'] == 4737658722 and full['missing_files'] == 0,
            'full project content proof incomplete')
    receipt = json.loads((ARCHIVE / 'receipts/R1_B001_DEST_VERIFIED.json').read_text())
    ready_raw = (BRIDGE / 'R1_B001_READY.json').read_bytes()
    require(hashlib.sha256(ready_raw).hexdigest() == acceptance['sample_ready_sha256'] == receipt['source_ready_sha256'],
            'wrong accepted sample')
    rows = receipt['files']
    require(len(rows) == acceptance['sample_regular_files'] == 1269 and
            sum(f['size_bytes'] for f in rows) == acceptance['sample_logical_bytes'] == 483509895 <= LIMIT,
            'restore sample scope/byte limit mismatch')
    require(sum(f['source_allocated_bytes'] for f in rows) == acceptance['sample_source_allocated_bytes'] <= LIMIT,
            'restore sample allocation limit')
    meta = ARCHIVE / 'infrastructure/project_manifests'
    frozen = read_zstd_jsonl(meta / 'R1_8556dd125ac2.jsonl.zst', acceptance['source_manifest_sha256'])
    joined = join_file_metadata(frozen, read_zstd_rows(meta / 'R1_FILE_METADATA.jsonl.zst',
                                acceptance['source_file_metadata_manifest_sha256']))
    known = {r['source_path']: r for r in joined}
    source_base = ARCHIVE / 'EP-L2/old174/workspace/repos/gpu-l2-cache-verilog-v3r1-clean/build'
    for f in rows:
        original = known[f['source_path']]
        require((f['source_sha256'], f['size_bytes'], f['source_uid'], f['source_gid'], f['source_mode']) ==
                (original['sha256'], original['size_bytes'], original['uid'], original['gid'], original['mode']),
                'frozen recovery metadata mismatch')
        require(Path(f['destination_path']) == source_base / f['relative_path'], 'archive source mapping mismatch')
    closed = json.loads((BRIDGE / 'R1_B014_BRIDGE_CLEANED.json').read_text())
    require(closed['status'] == 'BRIDGE_CLEANED' and closed['source_action'] == 'SOURCE_KEEP' and
            closed['bridge_remaining_data_bytes'] == 0, 'last forward batch not closed')
    resources = check_resources()
    require(resources['share_available_bytes'] >= SHARE_FLOOR + acceptance['sample_source_allocated_bytes'] + 32 * 1024**2,
            'Share lacks reverse batch reserve')
    lock = os.open(BRIDGE / '.TARGET_RECEIVER.lock', os.O_RDWR | os.O_NOFOLLOW)
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        require(not any(BRIDGE.glob('*/files')), 'another active bridge batch')
        require(subprocess.run(['pgrep','-x','rsync'],capture_output=True).returncode == 1, 'another rsync is active')
        stage = BRIDGE / NAME / 'files'
        marker = BRIDGE / (NAME + '_READY.json')
        require(not os.path.lexists(stage.parent) and not os.path.lexists(marker), 'reverse batch already exists; do not restart')
        for f in rows:
            h, s = sha(beneath(ARCHIVE, f['destination_path']))
            require(h == f['source_sha256'] and s['size'] == f['size_bytes'], '164 reverse source hash mismatch')
        if not args.stage:
            print(json.dumps(dict(mode='READ_ONLY_REVERSE_PLAN', files=len(rows), logical_bytes=483509895,
                native_staging=acceptance['approved_absent_native_staging_path'], source_action='SOURCE_KEEP', data_written=0)))
            return
        mkdirs(BRIDGE, stage)
        names = b''.join(f['relative_path'].encode() + b'\0' for f in rows)
        command = ['nice','-n','19','ionice','-c','3','rsync','-aH','--no-owner','--no-group',
                   '--partial','--fsync','--bwlimit=30m','--from0','--files-from=-']
        dry = subprocess.run(command + ['--dry-run','--',str(source_base)+'/',str(stage)+'/'],input=names,capture_output=True,timeout=60)
        require(dry.returncode == 0, 'reverse rsync dry-run failed')
        check_resources()
        copy = subprocess.run(command + ['--',str(source_base)+'/',str(stage)+'/'],input=names,capture_output=True,timeout=1800)
        require(copy.returncode == 0, 'reverse copy failed; keep owned partial stage and originals')
        files = []
        allocated = 0
        for f in rows:
            path = beneath(BRIDGE, stage / f['relative_path'])
            digest, snap = sha(path)
            require(digest == f['source_sha256'] and snap['size'] == f['size_bytes'], 'reverse bridge hash mismatch')
            allocated += path.lstat().st_blocks * 512
            files.append(dict(relative_path=f['relative_path'], source_original_path=f['source_path'],
                archive_path=f['destination_path'], bridge_path=str(path), size_bytes=f['size_bytes'],
                source_sha256=f['source_sha256'], archive_sha256=f['destination_sha256'], bridge_sha256=digest,
                original_uid=f['source_uid'],original_gid=f['source_gid'],original_mode=f['source_mode'],
                original_mtime_ns=f['source_mtime_ns'],bridge_identity=snap))
        require(allocated <= LIMIT, 'reverse actual bridge allocation exceeds batch budget')
        result = dict(schema='STORAGE_OPS_V7_TARGET_REVERSE_RESTORE_READY',status='REVERSE_READY',batch_id=NAME,
            created_at_utc=now(),project='R1',file_count=len(files),total_size_bytes=483509895,
            bridge_allocated_bytes=allocated,bridge_root=str(BRIDGE),bridge_files_root=str(stage),
            native_restore_staging_path=acceptance['approved_absent_native_staging_path'],
            original_sample_ready_sha256=acceptance['sample_ready_sha256'],source_acceptance_publication=owner,
            full_target_restore_publication=full_proof,source_manifest_sha256=acceptance['source_manifest_sha256'],
            source_file_metadata_sha256=acceptance['source_file_metadata_manifest_sha256'],
            source_directory_metadata_sha256=acceptance['source_directory_metadata_manifest_sha256'],
            native_mode_owner_must_be_applied_from_trusted_sidecars=True,files=files,
            source_action='SOURCE_KEEP',original_source_released_bytes=0,source_release_authorized=False,
            native_import_owner='existing independent old174 Source Ops',resources=check_resources())
        atomic_json(marker,result)
        folder=ARCHIVE/'infrastructure/project_receipts';mkdirs(ARCHIVE,folder)
        atomic_json(folder/(NAME+'_READY.json'),result)
        print(json.dumps(result))
    finally:
        os.close(lock)

if __name__ == '__main__':
    main()
