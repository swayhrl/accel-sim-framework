"""V6 target-only receiver. Default is a read-only plan; never releases source.

Explicit --receive copies one already staged/hashed batch. --restore-sample
checks one archived file at an independent path and reports only sample bytes.
"""
import argparse
import csv
import datetime
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess

ARCHIVE = Path('/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02')
BRIDGE = Path('/root/share/host174_storage_recovery_bridge/20261016_storageops_02')
LIMIT = 512 * 1024**2
SHARE_FLOOR = 40 * 1024**3
FROZEN_INVENTORY_SHA = 'd34a952f7dfa5fcd0a2a965fc82623a6ff5fb9666f007b7626269e295a8505d7'

def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def require(ok, message):
    if not ok:
        raise ValueError(message)

def relative(value):
    require(isinstance(value, str) and value and not value.startswith('/'), 'absolute/empty relative path')
    require(all(p not in ['', '.', '..'] for p in value.split('/')), 'unsafe path components')
    require('\\' not in value and '\0' not in value, 'unsafe path encoding')
    return PurePosixPath(value)

def beneath(root, path, must_exist=True):
    p = Path(path)
    p.relative_to(root)
    require(p.resolve(strict=must_exist) == p, 'symlink or noncanonical path: ' + str(p))
    return p

def identity(path):
    s = path.lstat()
    require(stat.S_ISREG(s.st_mode), 'not a regular file: ' + str(path))
    return dict(dev=s.st_dev, inode=s.st_ino, nlink=s.st_nlink,
                size=s.st_size, mtime_ns=s.st_mtime_ns, ctime_ns=s.st_ctime_ns)

def sha(path):
    before = identity(path)
    h = hashlib.sha256()
    with os.fdopen(os.open(path, os.O_RDONLY | os.O_NOFOLLOW), 'rb') as f:
        s = os.fstat(f.fileno())
        require((s.st_dev, s.st_ino) == (before['dev'], before['inode']), 'open identity changed')
        for block in iter(lambda: f.read(4 * 1024**2), b''):
            h.update(block)
    require(identity(path) == before, 'file changed while hashing: ' + str(path))
    return h.hexdigest(), before

def mkdirs(root, destination):
    relative_name = destination.relative_to(root)
    p = root
    for component in relative_name.parts:
        p = p / component
        if not os.path.lexists(p):
            p.mkdir(mode=0o700)
        require(p.is_dir() and not p.is_symlink(), 'unsafe directory: ' + str(p))

def atomic_json(path, data):
    require(not os.path.lexists(path), 'refuse to overwrite receipt: ' + str(path))
    tmp = path.with_name(path.name + '.tmp-' + str(os.getpid()))
    with tmp.open('x', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
        f.write('\n')
        f.flush()
        os.fsync(f.fileno())
    require(not os.path.lexists(path), 'receipt appeared during write')
    os.rename(tmp, path)

def check_resources():
    m = json.loads(subprocess.check_output(['findmnt', '-J', '-T', str(ARCHIVE),
        '-o', 'TARGET,SOURCE,FSTYPE'], text=True))['filesystems'][0]
    require(m['source'] == 'admin-wcx@10.208.130.164:/home/shared' and
            m['fstype'] == 'fuse.sshfs', 'archive mount identity mismatch')
    require(ARCHIVE.resolve() == ARCHIVE and BRIDGE.resolve() == BRIDGE, 'root symlink')
    bridge_mount = json.loads(subprocess.check_output(['findmnt', '-J', '-T', str(BRIDGE),
        '-o', 'TARGET,SOURCE,FSTYPE'], text=True))['filesystems'][0]
    require(bridge_mount['target'] == '/root/share' and bridge_mount['source'] == '/dev/md127'
            and bridge_mount['fstype'] == 'ext4', 'bridge mount identity mismatch')
    v = os.statvfs(BRIDGE)
    require(v.f_bavail * v.f_frsize >= SHARE_FLOOR, 'BRIDGE_RESOURCE_HOLD: Share <40GiB')
    return dict(mount=m, bridge_mount=bridge_mount, share_available_bytes=v.f_bavail * v.f_frsize,
                archive_available_bytes=os.statvfs(ARCHIVE).f_bavail * os.statvfs(ARCHIVE).f_frsize)

def validate(data, inventory=None):
    require(data.get('schema') in ['STORAGE_OPS_V6_SOURCE_BATCH_READY',
            'STORAGE_OPS_V7_COLD_PROJECT_BATCH_READY'], 'unsupported source READY schema')
    batch = data.get('batch_id', '')
    project = data.get('project', '')
    require(re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,63}', batch) is not None, 'unsafe batch id')
    require(re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,63}', project) is not None, 'unsafe project id')
    require(data.get('bridge_root') == str(BRIDGE), 'wrong bridge root')
    require(data.get('destination_archive_root') == str(ARCHIVE), 'wrong archive root')
    require(data.get('source_identity_nlink_and_hash_rechecked_before_and_after_stage') is True,
            'source stability qualification missing')
    require(data.get('stage_reopened_per_file_sha256_verified') is True, 'stage qualification missing')
    require(re.fullmatch('[0-9a-f]{40}', data.get('source_receipt_commit', '')) is not None,
            'pinned source receipt commit missing')
    if batch in ['S01', 'S02']:
        require(data.get('source_inventory_sha256') == FROZEN_INVENTORY_SHA, 'wrong frozen inventory')
        require(data.get('probe_absence_independently_confirmed') is True, 'source probe absence missing')
        require(data.get('only_vvp_compiled_outputs') is True and
                data.get('retain_verilog_filelists_and_other_source_evidence') is True, 'wrong V5 source class')
        require(inventory is not None, 'S01/S02 frozen inventory required')
    else:
        require(data.get('owner_authorization') == 'COLD_COPY_OK' and data.get('owner'), 'owner scope missing')
        require(data.get('retention') == 'SOURCE_KEEP', 'general cold archives default SOURCE_KEEP')
        require(data.get('source_status') == 'STAGED_READY', 'cold batch not STAGED_READY')
        require(data.get('asset_state') == 'COLD', 'active assets are outside cold acceptance')
        if data.get('schema') == 'STORAGE_OPS_V7_COLD_PROJECT_BATCH_READY':
            require(data.get('source_action') == 'COPY_OK_ONLY' and
                    data.get('release_requires_user_approval') is True,
                    'V7 scientific offload remains copy-only pending source/user approval')
            for key in ['project_manifest_sha256', 'owner_scope_receipt_sha256']:
                require(re.fullmatch('[0-9a-f]{64}', data.get(key, '')) is not None,
                        'V7 project/owner evidence missing: ' + key)
            require(data.get('dependencies_complete') is True and data.get('no_active_consumers') is True,
                    'V7 dependency or consumer closure missing')
        else:
            require(data.get('contains_unique_original_inputs') is False,
                    'V6 unique-original inputs need a reviewed V7 copy-only scope')
        for key in ['source_mount_namespace', 'source_mount', 'source_commit', 'source_config',
                    'producer', 'run_key', 'rehydration_recipe']:
            require(data.get(key), 'missing multi-project provenance: ' + key)
    files = data.get('files', [])
    require(files and len(files) == data.get('file_count'), 'file count mismatch')
    require(sum(f['size_bytes'] for f in files) == data.get('total_size_bytes') <= LIMIT, 'batch >512MiB or size mismatch')
    known = {(r['batch_id'], r['exact_source']): r for r in inventory or []}
    paths, destinations = set(), set()
    for f in files:
        require(isinstance(f['size_bytes'], int) and 0 <= f['size_bytes'] <= LIMIT, 'invalid file size')
        require(f['source_sha256'] == f['bridge_sha256'] and
                re.fullmatch('[0-9a-f]{64}', f['source_sha256']) is not None, 'hash mismatch/format')
        require(f['source_path'] not in paths, 'duplicate source')
        require(not any(x in ['.git', '.ssh'] or x.startswith('tmp_pack_') for x in Path(f['source_path']).parts), 'excluded source class')
        paths.add(f['source_path'])
        rel = relative(f['relative_path'])
        require(Path(f['source_path']) == Path(data['source_root']) / rel,
                'source root/relative mapping mismatch')
        require(f['bridge_path'] == str(BRIDGE / batch / 'files' / rel), 'noncanonical bridge mapping')
        dest = relative(f['destination_relative_path'])
        require(dest.parts[0] == project, 'destination project isolation mismatch')
        require(str(dest) not in destinations, 'duplicate destination')
        destinations.add(str(dest))
        require(f['source_nlink'] == 1 and f['source_allocated_bytes'] >= 0, 'source link/allocation qualification')
        if batch not in ['S01', 'S02']:
            require(f['source_allocated_bytes'] >= f['size_bytes'], 'sparse input needs an explicit restore-capable adapter')
            for key in ['source_mtime_ns', 'source_ctime_ns', 'source_uid', 'source_gid',
                        'source_mode', 'readers_and_inflight_references']:
                require(key in f, 'missing cold-source metadata: ' + key)
            require(f['readers_and_inflight_references'] == [], 'active/unknown source reader scope')
        if inventory:
            r = known.get((batch, f['source_path']))
            require(r is not None, 'source not in frozen inventory')
            require((int(r['size_bytes']), r['sha256'], int(r['device']), int(r['inode'])) ==
                    (f['size_bytes'], f['source_sha256'], f['source_dev'], f['source_inode']), 'frozen identity/hash mismatch')
    if inventory:
        require(paths == {r['exact_source'] for r in inventory if r['batch_id'] == batch}, 'frozen file set mismatch')
    return files

def validate_project_membership(data, files, project_rows, digest):
    require(data.get('project_manifest_sha256', data.get('source_inventory_sha256')) == digest,
            'wrong frozen full-project manifest')
    known = {r['source_path']: r for r in project_rows}
    for f in files:
        r = known.get(f['source_path'])
        require(r is not None, 'batch source is outside full-project scope')
        require((f['size_bytes'], f['source_sha256'], f['source_dev'], f['source_inode'], f['source_nlink']) ==
                (r['size_bytes'], r['sha256'], r['device'], r['inode'], r['nlink']),
                'full-project identity/hash mismatch')

def receive(data, manifest_sha, files, manifest_path, restore_sample=False, resume=False):
    import fcntl
    resources_before = check_resources()
    require(resources_before['archive_available_bytes'] >= data['total_size_bytes'] +
            (files[0]['size_bytes'] if restore_sample else 0), 'archive capacity below batch and restore needs')
    lock = os.open(BRIDGE / '.TARGET_RECEIVER.lock', os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        batch = data['batch_id']
        receipt_path = ARCHIVE / 'receipts' / (batch + '_DEST_VERIFIED.json')
        if receipt_path.exists():
            existing = json.loads(receipt_path.read_text())
            require(existing['source_ready_sha256'] == manifest_sha and existing['project'] == data['project'],
                    'existing receipt belongs to another manifest')
            old_files = {f['source_path']: f for f in existing['files']}
            require(set(old_files) == {f['source_path'] for f in files}, 'existing receipt file set mismatch')
            for f in files:
                old = old_files[f['source_path']]
                require(old['destination_relative_path'] == f['destination_relative_path'], 'existing path mapping mismatch')
                digest, snap = sha(beneath(ARCHIVE, old['destination_path']))
                require(digest == f['source_sha256'] and snap['size'] == f['size_bytes'],
                        'verified archive changed; stop, never overwrite')
            marker = BRIDGE / (batch + '_DEST_VERIFIED.json')
            if not marker.exists():
                atomic_json(marker, existing)
            else:
                require(json.loads(marker.read_text()) == existing, 'bridge receipt conflict')
            return dict(existing, idempotent_existing_archive_verified=True,
                        new_archived_bytes=0, new_data_transfer=False)
        staged = {}
        for f in files:
            p = beneath(BRIDGE, f['bridge_path'])
            digest, snapshot = sha(p)
            require(digest == f['source_sha256'] and snapshot['size'] == f['size_bytes'], 'stage hash mismatch')
            staged[f['source_path']] = snapshot
        results = []
        destination_bases = set()
        journal_path = ARCHIVE / 'infrastructure' / 'transfer_journals' / (batch + '_' + manifest_sha + '.json')
        journal_files = [dict(source_path=f['source_path'], destination_relative_path=f['destination_relative_path'],
                              size_bytes=f['size_bytes'], sha256=f['source_sha256']) for f in files]
        sample_path = (ARCHIVE / 'infrastructure' / 'restore_tests' / data['project'] / batch /
                       relative(files[0]['relative_path'])) if restore_sample else None
        if journal_path.exists():
            require(resume, 'unfinished batch requires explicit --resume')
            journal = json.loads(journal_path.read_text())
            require(journal['source_ready_sha256'] == manifest_sha and journal['files'] == journal_files
                    and journal['owner'] == 'Storage-Ops' and journal['all_destinations_absent_before_start'] is True,
                    'resume journal scope mismatch')
            require(journal.get('restore_sample_path') == (str(sample_path) if sample_path else None),
                    'resume restore-sample scope mismatch')
        else:
            require(not resume, 'no owned journal: cannot resume or overwrite')
            require(all(not os.path.lexists(ARCHIVE / relative(f['destination_relative_path'])) for f in files),
                    'preexisting archive destination has no owned journal')
            require(sample_path is None or not os.path.lexists(sample_path), 'preexisting restore sample')
            mkdirs(ARCHIVE, journal_path.parent)
            atomic_json(journal_path, dict(owner='Storage-Ops', created_at_utc=now(), batch_id=batch,
                source_ready_sha256=manifest_sha, all_destinations_absent_before_start=True, files=journal_files,
                restore_sample_path=str(sample_path) if sample_path else None))
        pending = []
        for f in files:
            p = beneath(BRIDGE, f['bridge_path'])
            require(identity(p) == staged[f['source_path']], 'stage changed before copy')
            dest = ARCHIVE / relative(f['destination_relative_path'])
            mkdirs(ARCHIVE, dest.parent)
            if os.path.lexists(dest):
                require(resume and not dest.is_symlink(), 'refuse existing destination: ' + str(dest))
                digest, snap = sha(dest)
                if digest == f['source_sha256'] and snap['size'] == f['size_bytes']:
                    continue
            pending.append(f)
        for f in files:
            rp = relative(f['relative_path']).parts
            dp = relative(f['destination_relative_path']).parts
            require(dp[-len(rp):] == rp, 'destination does not preserve relative structure')
            destination_bases.add(str(ARCHIVE.joinpath(*dp[:-len(rp)])))
        require(len(destination_bases) == 1, 'one batch needs one common destination prefix')
        destination_base = next(iter(destination_bases))
        source_base = str(BRIDGE / batch / 'files')
        names = b''.join(f['relative_path'].encode() + b'\0' for f in pending)
        args = ['nice', '-n', '19', 'ionice', '-c', '3', 'rsync', '-aH',
                '--no-owner', '--no-group', '--partial', '--fsync', '--bwlimit=30m',
                '--from0', '--files-from=-']
        dry = subprocess.run(args + ['--dry-run', '--itemize-changes', '--', source_base + '/', destination_base + '/'],
                             input=names, capture_output=True, timeout=30)
        require(dry.returncode == 0, 'rsync dry-run failed: ' + dry.stderr.decode(errors='replace'))
        check_resources()
        cp = subprocess.run(args + ['--', source_base + '/', destination_base + '/'],
                            input=names, capture_output=True, timeout=1800)
        require(cp.returncode == 0, 'rsync failed: ' + cp.stderr.decode(errors='replace'))
        for f in files:
            check_resources()
            p = beneath(BRIDGE, f['bridge_path'])
            dest = ARCHIVE / relative(f['destination_relative_path'])
            digest, target_stat = sha(dest)  # rsync exited/closed; reopen via SSHFS.
            require(digest == f['source_sha256'] and target_stat['size'] == f['size_bytes'], 'destination mismatch')
            require(identity(p) == staged[f['source_path']], 'stage changed during copy')
            results.append(dict(f, destination_path=str(dest), destination_sha256=digest,
                                bridge_identity_before_after=staged[f['source_path']], destination_stat=target_stat))
        restore = dict(status='NOT_RUN', verified_restore_bytes=0)
        if restore_sample:
            f = results[0]
            dest = ARCHIVE / 'infrastructure' / 'restore_tests' / data['project'] / batch / relative(f['relative_path'])
            mkdirs(ARCHIVE, dest.parent)
            if os.path.lexists(dest):
                require(resume and not dest.is_symlink(), 'restore sample exists')
            else:
                restored_copy = subprocess.run(['nice', '-n', '19', 'ionice', '-c', '3', 'rsync', '-aH',
                    '--no-owner', '--no-group', '--fsync', '--bwlimit=30m', '--', f['destination_path'], str(dest)], capture_output=True, text=True, timeout=120)
                require(restored_copy.returncode == 0, 'restore sample copy failed')
            digest, snap = sha(dest)
            require(digest == f['source_sha256'], 'restore sample mismatch')
            restore = dict(status='SAMPLE_RESTORE_VERIFIED_NOT_FULL_BATCH', path=str(dest),
                sha256=digest, verified_restore_bytes=snap['size'], sampled_files=1, batch_files=len(files))
        require(hashlib.sha256(Path(manifest_path).read_bytes()).hexdigest() == manifest_sha,
                'READY changed during receive; no DEST_VERIFIED')
        receipt = dict(schema='STORAGE_OPS_V6_DEST_VERIFIED', status='DEST_VERIFIED', batch_id=batch,
            project=data['project'], verified_at_utc=now(), destination_archive_root=str(ARCHIVE),
            source_ready_sha256=manifest_sha, source_inventory_sha256=data.get('source_inventory_sha256'),
            project_manifest_sha256=data.get('project_manifest_sha256'),
            owner_scope_receipt_sha256=data.get('owner_scope_receipt_sha256'),
            source_receipt_commit=data.get('source_receipt_commit'), file_count=len(results),
            total_size_bytes=data['total_size_bytes'], archived_bytes=data['total_size_bytes'],
            source_allocated_bytes=data.get('source_allocated_bytes'), files=results,
            verification_level='SSHFS_READBACK_VERIFIED', server_side_native_verified=False,
            source_action='SOURCE_KEEP_PENDING_INDEPENDENT_SOURCE_RELEASE_RECHECK',
            source_release_authorized_by_target=False, source_confirmed_released_allocated_bytes=0,
            source_df_free_before_after=None, restore=restore, resources_before=resources_before,
            resources_after=check_resources(), bridge_stage_cleanup='AWAIT_SOURCE_ACTION_RECEIPT')
        receipt['new_archived_bytes'] = sum(f['size_bytes'] for f in pending)
        receipt['resumed_from_owned_journal'] = resume
        receipt['rsync'] = dict(dry_run_exit=dry.returncode, copy_exit=cp.returncode,
            argv=args + ['--', source_base + '/', destination_base + '/'], exact_files_from=[f['relative_path'] for f in files])
        mkdirs(ARCHIVE, ARCHIVE / 'receipts')
        atomic_json(ARCHIVE / 'receipts' / (batch + '_DEST_VERIFIED.json'), receipt)
        atomic_json(BRIDGE / (batch + '_DEST_VERIFIED.json'), receipt)
        return receipt
    finally:
        os.close(lock)

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--manifest', required=True)
    ap.add_argument('--inventory')
    ap.add_argument('--project-inventory', help='pinned .jsonl.zst full-project source manifest for V7')
    ap.add_argument('--expected-project-inventory-sha256')
    ap.add_argument('--expected-ready-sha256', required=True)
    ap.add_argument('--receive', action='store_true', help='explicitly execute one target-only copy batch')
    ap.add_argument('--restore-sample', action='store_true')
    ap.add_argument('--resume', action='store_true', help='resume only an incomplete batch with matching owned journal')
    args = ap.parse_args()
    raw = Path(args.manifest).read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    require(digest == args.expected_ready_sha256, 'READY manifest changed')
    data = json.loads(raw)
    inventory = None
    if args.inventory:
        frozen = Path(args.inventory).read_bytes()
        require(hashlib.sha256(frozen).hexdigest() == FROZEN_INVENTORY_SHA, 'inventory SHA256 mismatch')
        inventory = list(csv.DictReader(frozen.decode().splitlines()))
    files = validate(data, inventory)
    if data.get('schema') == 'STORAGE_OPS_V7_COLD_PROJECT_BATCH_READY' or args.project_inventory:
        require(args.project_inventory and args.expected_project_inventory_sha256,
                'V7 full-project source manifest is required even for a read-only plan')
        from cold_project_restore import read_zstd_jsonl
        project_rows = read_zstd_jsonl(args.project_inventory, args.expected_project_inventory_sha256)
        validate_project_membership(data, files, project_rows, args.expected_project_inventory_sha256)
    if args.receive:
        receipt = receive(data, digest, files, args.manifest, args.restore_sample, args.resume)
        require(hashlib.sha256(Path(args.manifest).read_bytes()).hexdigest() == digest, 'READY changed during receive')
        print(json.dumps(receipt, indent=2))
    else:
        print(json.dumps(dict(mode='READ_ONLY_DRY_RUN', batch_id=data['batch_id'], project=data['project'],
            manifest_sha256=digest, files=files, total_size_bytes=data['total_size_bytes'],
            source_action='SOURCE_KEEP', data_written=0), indent=2))

if __name__ == '__main__':
    main()
