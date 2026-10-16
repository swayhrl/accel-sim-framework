"""Stage one frozen R1 197-file reverse batch using the existing receiver lock.

Derived from the already exercised R1 B001 reverse helper. No source import,
promotion or deletion exists here. Default is read-only; --stage is explicit.
"""
import argparse
import csv
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys

PLAN_SHA = '32563312cb2adfff5965c89cc23aa50cc8ac95994eec4de903f3fee714c18c2c'
MANIFEST_SHA = '7080a4a01940b85a8166e7bceab7705f0bdd2c5ea2195f9417e4e109deae3dcd'
CANONICAL_SHA = 'af1bf73951ab44258591afd625043c855e3a76bca67fb378abe8b226ee271c84'
DECISION_SHA = '96c3736e50c01d2c7390c712f9963bad05e700452cbd529051bae07fdff4901a'
FULL_RESTORE_SHA = 'f71dbc6eba23b0219674efde3473046877efdc958a3a3aacfdcfad0834f338b7'
SOURCE = '/workspace/repos/gpu-l2-cache-verilog-v3r1-clean/build'
NATIVE = SOURCE + '.restore.r1_197'
ARCHIVE_REL = 'EP-L2/old174' + SOURCE
PAYLOAD_LIMIT = 524288000


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def validate_membership(plan, rows):
    require(len(rows) == 197 and len(plan['batches']) == 10 and
            plan['source_manifest_sha256'] == MANIFEST_SHA and
            plan['source_root_old174'] == SOURCE, 'wrong exact 197 scope')
    require(sum(r['size_bytes'] for r in rows.values()) == 4464202341 and
            sum(r['allocated_bytes'] for r in rows.values()) == 4464783360,
            'exact manifest byte totals changed')
    seen = set()
    for i, batch in enumerate(plan['batches']):
        require(batch['index'] == i and batch['logical_bytes'] <= PAYLOAD_LIMIT,
                'batch ordinal/size mismatch')
        logical = allocated = 0
        for f in batch['files']:
            relative = PurePosixPath(f['relative_path'])
            require(not relative.is_absolute() and '..' not in relative.parts and
                    relative.suffix == '.vvp', 'unsafe or non-vvp restore path')
            name = str(relative)
            require(name in rows and name not in seen, 'unexpected or duplicate restore file')
            r = rows[name]
            require((f['sha256'], f['size_bytes'], f['uid'], f['gid'],
                     int(f['mode_octal'], 8), f['mtime_ns']) ==
                    (r['sha256'], r['size_bytes'], r['uid'], r['gid'],
                     r['mode'], r['mtime_ns']), 'frozen hash/metadata substitution')
            seen.add(name)
            logical += r['size_bytes']
            allocated += r['allocated_bytes']
        require(logical == batch['logical_bytes'] and allocated <= 512 * 1024**2,
                'batch byte/allocation coverage mismatch')
    require(seen == set(rows), 'reverse plan misses exact manifest members')


def load_scope(plan_raw, manifest_raw):
    require(hashlib.sha256(plan_raw).hexdigest() == PLAN_SHA, 'frozen reverse plan SHA mismatch')
    require(hashlib.sha256(manifest_raw).hexdigest() == MANIFEST_SHA, 'frozen exact manifest SHA mismatch')
    records = list(csv.DictReader(io.StringIO(manifest_raw.decode()), delimiter='\t'))
    rows = {}
    for raw in records:
        source = PurePosixPath(raw['source_path'])
        require(source.is_relative_to(PurePosixPath(SOURCE)), 'source outside frozen R1 root')
        relative = str(source.relative_to(PurePosixPath(SOURCE)))
        require(relative not in rows, 'duplicate exact manifest source')
        rows[relative] = dict(sha256=raw['sha256'], size_bytes=int(raw['size_bytes']),
            allocated_bytes=int(raw['allocated_bytes']), uid=int(raw['uid']), gid=int(raw['gid']),
            mode=int(raw['mode_octal'], 8), mtime_ns=int(raw['mtime_ns']), archive_path=raw['archive_path'])
    canonical = ''.join('\t'.join(map(str, (name, r['sha256'], r['size_bytes'], r['allocated_bytes']))) + '\n'
                        for name, r in sorted(rows.items())).encode()
    require(hashlib.sha256(canonical).hexdigest() == CANONICAL_SHA, 'canonical exact197 scope changed')
    plan = json.loads(plan_raw)
    validate_membership(plan, rows)
    return plan, rows


def validate_acceptance(ack, decision_sha):
    require(decision_sha == DECISION_SHA, 'wrong target window decision')
    require(ack.get('source_action') == 'SOURCE_KEEP' and
            ack.get('source_release_authorized') is False and ack.get('source_released_bytes') == 0,
            'reverse window cannot authorize source release')
    require(ack.get('target_window_decision_sha256', ack.get('target_decision_sha256')) == decision_sha,
            'source did not accept exact target decision')
    require(ack['reverse_plan_sha256'] == PLAN_SHA and
            ack['exact_scope_manifest_sha256'] == MANIFEST_SHA and
            ack['canonical_four_column_manifest_sha256'] == CANONICAL_SHA and
            ack['native_staging_root'] == NATIVE, 'source acceptance scope/native root mismatch')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--plan', required=True)
    p.add_argument('--exact-manifest', required=True)
    p.add_argument('--index', type=int, required=True)
    p.add_argument('--receiver-bundle')
    p.add_argument('--source-acceptance-proof')
    p.add_argument('--stage', action='store_true')
    p.add_argument('--scope-only', action='store_true')
    args = p.parse_args()
    require(0 <= args.index < 10 and not (args.scope_only and args.stage), 'invalid batch/options')
    plan, known = load_scope(Path(args.plan).read_bytes(), Path(args.exact_manifest).read_bytes())
    batch_plan = plan['batches'][args.index]
    name = f'R1_197_NATIVE_RESTORE_B{args.index + 1:03d}'
    if args.scope_only:
        print(json.dumps(dict(mode='FROZEN_SCOPE_ONLY_PASS', batch_id=name,
            files=len(batch_plan['files']), logical_bytes=batch_plan['logical_bytes'],
            source_action='SOURCE_KEEP', data_written_bytes=0)))
        return
    require(args.receiver_bundle and args.source_acceptance_proof, 'explicit existing bundle/source ACK proof required')
    import fcntl
    sys.path.insert(0, args.receiver_bundle)
    from archive_receiver import ARCHIVE, BRIDGE, LIMIT, SHARE_FLOOR, sha, beneath, mkdirs, atomic_json, check_resources, now
    proof = json.loads(Path(args.source_acceptance_proof).read_bytes())
    require(re.fullmatch('[0-9a-f]{40}', proof['commit']) is not None and
            proof['github_readback_verified'] is True, 'source ACK not GitHub-pinned')
    ack_raw = (BRIDGE/'R1_197_REVERSE_WINDOW_SOURCE_ACCEPTED_R10_V1.json').read_bytes()
    require(hashlib.sha256(ack_raw).hexdigest() == proof['receipt_sha256'], 'source window ACK changed')
    decision_raw = (BRIDGE/'TARGET_NEXT_SOLE_WINDOW_DECISION_R10_V1.json').read_bytes()
    validate_acceptance(json.loads(ack_raw), hashlib.sha256(decision_raw).hexdigest())
    full_raw = (ARCHIVE/'infrastructure/project_receipts/R1_FULL_CONTENT_RESTORE_8556dd125ac2.json').read_bytes()
    require(hashlib.sha256(full_raw).hexdigest() == FULL_RESTORE_SHA, 'full R1 restore proof changed')
    full = json.loads(full_raw)
    require(full['all_files_dest_verified'] and full['verified_restore_bytes'] == 4737658722 and
            full['missing_files'] == 0, 'full R1 content protection incomplete')
    resource = check_resources()
    allocated = sum(known[f['relative_path']]['allocated_bytes'] for f in batch_plan['files'])
    require(resource['share_available_bytes'] >= SHARE_FLOOR + allocated + 32 * 1024**2,
            'Share lacks reverse batch reserve')
    lock = os.open(BRIDGE/'.TARGET_RECEIVER.lock', os.O_RDWR | os.O_NOFOLLOW)
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        require(not any(BRIDGE.glob('*/files')), 'another bridge data batch is active')
        require(subprocess.run(['pgrep', '-x', 'rsync'], capture_output=True).returncode == 1,
                'another rsync is active; do not stop it')
        if args.index:
            previous = f'R1_197_NATIVE_RESTORE_B{args.index:03d}'
            closed = json.loads((BRIDGE/(previous+'_BRIDGE_CLEANED.json')).read_bytes())
            require(closed['status'] == 'BRIDGE_CLEANED' and closed['bridge_remaining_data_bytes'] == 0 and
                    closed['source_original_released_bytes'] == 0 and closed['source_github_readback_verified'] is True,
                    'previous reverse batch lacks independent verified closeout')
        else:
            require((BRIDGE/'TARGET_POLYBENCH_RESTORE_PHASE_CLOSED_R10_V1.json').is_file() and
                    (BRIDGE/'POLYBENCH_TARGET_RESTORE_PHASE_SOURCE_ACCEPTED_R10_V1.json').is_file(),
                    'PolyBench target/source phase closure absent')
        stage = BRIDGE/name/'files'
        marker = BRIDGE/(name+'_READY.json')
        require(not os.path.lexists(stage.parent) and not os.path.lexists(marker),
                'reverse batch already exists: inspect/reuse verified receipt; never restart or overwrite')
        source_base = ARCHIVE/ARCHIVE_REL
        for f in batch_plan['files']:
            path = beneath(ARCHIVE, source_base/f['relative_path'])
            require(str(path) == known[f['relative_path']]['archive_path'], 'frozen archive mapping changed')
            digest, snap = sha(path)
            require(digest == f['sha256'] and snap['size'] == f['size_bytes'], '164 reverse source hash mismatch')
        if not args.stage:
            print(json.dumps(dict(mode='READ_ONLY_REVERSE_PLAN_PASS', batch_id=name,
                files=len(batch_plan['files']), logical_bytes=batch_plan['logical_bytes'], data_written_bytes=0)))
            return
        mkdirs(BRIDGE, stage)
        names = b''.join(f['relative_path'].encode()+b'\0' for f in batch_plan['files'])
        command = ['nice', '-n', '19', 'ionice', '-c', '3', 'rsync', '-aH', '--no-owner', '--no-group',
                   '--partial', '--fsync', '--bwlimit=30m', '--from0', '--files-from=-']
        dry = subprocess.run(command+['--dry-run', '--', str(source_base)+'/', str(stage)+'/'],
                             input=names, capture_output=True, timeout=60)
        require(dry.returncode == 0, 'reverse rsync dry-run failed')
        check_resources()
        copy = subprocess.run(command+['--', str(source_base)+'/', str(stage)+'/'],
                              input=names, capture_output=True, timeout=1800)
        require(copy.returncode == 0, 'reverse rsync failed: retain owned partial for bounded inspection')
        files, physical = [], 0
        for f in batch_plan['files']:
            path = beneath(BRIDGE, stage/f['relative_path'])
            digest, snap = sha(path)
            require(digest == f['sha256'] and snap['size'] == f['size_bytes'] and snap['nlink'] == 1,
                    'closed/reopened bridge content/link mismatch')
            physical += path.lstat().st_blocks * 512
            files.append(dict(relative_path=f['relative_path'], source_original_path=SOURCE+'/'+f['relative_path'],
                archive_path=str(source_base/f['relative_path']), bridge_path=str(path), size_bytes=f['size_bytes'],
                source_sha256=f['sha256'], archive_sha256=f['sha256'], bridge_sha256=digest,
                original_uid=f['uid'], original_gid=f['gid'], original_mode=int(f['mode_octal'], 8),
                original_mtime_ns=f['mtime_ns'], bridge_identity=snap))
        physical += stage.parent.lstat().st_blocks*512 + stage.lstat().st_blocks*512
        physical += sum(d.lstat().st_blocks*512 for d in stage.rglob('*') if d.is_dir())
        require(physical <= LIMIT, 'actual bridge files/directories exceed <=512MiB batch budget')
        result = dict(schema='STORAGE_OPS_V7_TARGET_REVERSE_RESTORE_READY', status='REVERSE_READY',
            batch_id=name, plan_index=args.index, created_at_utc=now(), project='R1_197', file_count=len(files),
            total_size_bytes=batch_plan['logical_bytes'], bridge_allocated_bytes=physical,
            bridge_root=str(BRIDGE), bridge_files_root=str(stage), native_restore_staging_path=NATIVE,
            reverse_plan_sha256=PLAN_SHA, exact_scope_manifest_sha256=MANIFEST_SHA,
            canonical_four_column_manifest_sha256=CANONICAL_SHA, source_acceptance_publication=proof,
            target_window_decision_sha256=DECISION_SHA,
            full_target_restore_publication=dict(commit='be3cdc8cdf21dd858df8a603a00bded8dd88a747',
                receipt_sha256=FULL_RESTORE_SHA, github_readback_verified=True),
            source_manifest_sha256='8556dd125ac2147ccd035419a905093a20d56be989890f70a3193813ab3791e5',
            source_file_metadata_sha256='9226c1f5e457a8ab716afd08dc126201f94a827afde1e4312b4a1f8bf936d22f',
            source_directory_metadata_sha256='88b1e989d79a95762a77228593c6e19501cf5ae903d3d5a496ee7d6f4c5dec4b',
            native_mode_owner_must_be_applied_from_trusted_sidecars=True, files=files,
            source_action='SOURCE_KEEP', original_source_released_bytes=0, source_release_authorized=False,
            native_import_owner='existing independent old174 Source Ops', resources=check_resources())
        atomic_json(marker, result)
        atomic_json(ARCHIVE/'infrastructure/project_receipts'/(name+'_READY.json'), result)
        print(json.dumps(result))
    finally:
        os.close(lock)


if __name__ == '__main__':
    main()
