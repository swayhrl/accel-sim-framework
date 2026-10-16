"""Bounded target receipt index. Read-only stdout unless --write is explicit."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import stat

from archive_receiver import ARCHIVE, BRIDGE, atomic_json, mkdirs, check_resources

def inventory(source_actions=None):
    check_resources()
    records = []
    paths = sorted((ARCHIVE / 'receipts').glob('*.json'))
    if len(paths) > 2048:
        raise ValueError('bounded inventory exceeded; select an explicit project receipt subset')
    for p in paths:
        data = json.loads(p.read_text())
        if data.get('status') == 'DEST_VERIFIED':
            files = data['files']
            for f in files:
                dest = Path(f['destination_path'])
                dest.relative_to(ARCHIVE)
                s = dest.lstat()
                if not stat.S_ISREG(s.st_mode) or s.st_size != f['size_bytes']:
                    raise ValueError('archive metadata mismatch: ' + str(dest))
                if f['source_sha256'] != f['bridge_sha256'] or f['source_sha256'] != f['destination_sha256']:
                    raise ValueError('stored hash triple mismatch')
            records.append(dict(project=data['project'], batch_id=data['batch_id'],
                archived_bytes=data['archived_bytes'], verification_level=data['verification_level'],
                hash_authority='stored complete SSHFS readback receipt; not a new data rehash',
                manifest_path=str(p), manifest_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),
                files=[dict(source_path=f['source_path'], destination_path=f['destination_path'],
                            size_bytes=f['size_bytes'], sha256=f['destination_sha256']) for f in files],
                source_confirmed_released_allocated_bytes=0, source_df_free_before_after=None,
                source_action='SOURCE_KEEP_UNTIL_INDEPENDENT_ACTION_RECEIPT',
                verified_restore_bytes=data.get('restore', {}).get('verified_restore_bytes', 0)))
        elif re.fullmatch(r'batch[0-9]{3}', data.get('batch', '')):
            dest = ARCHIVE / data['destination_relative_path']
            if dest.lstat().st_size != data['size'] or not (
                    data['source_sha256'] == data['stage_sha256'] == data['sshfs_reopened_sha256']):
                raise ValueError('legacy backup receipt mismatch')
            records.append(dict(project='legacy-git-pack-backup', batch_id=data['batch'],
                archived_bytes=data['size'], verification_level='SSHFS_READBACK_VERIFIED',
                route_compliance='LEGACY_ROUTE_NOT_V4_COMPLIANT',
                hash_authority='existing verified receipt; historical data not rehashed',
                manifest_path=str(p), manifest_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),
                files=[dict(source_path=data['source'], destination_path=str(dest),
                            size_bytes=data['size'], sha256=data['source_sha256'])],
                source_action='SOURCE_KEEP', source_confirmed_released_allocated_bytes=0,
                source_df_free_before_after=None, verified_restore_bytes=0))
    for proof in source_actions or []:
        if not re.fullmatch('[0-9a-f]{40}', proof['source_commit']):
            raise ValueError('source action must name an exact source commit')
        p = Path(proof['receipt_path'])
        p.relative_to(ARCHIVE / 'infrastructure' / 'source_receipts')
        if p.resolve() != p:
            raise ValueError('source receipt symlink')
        raw = p.read_bytes()
        if hashlib.sha256(raw).hexdigest() != proof['receipt_sha256']:
            raise ValueError('independent source receipt hash mismatch')
        action = json.loads(raw)
        matches = [r for r in records if r['batch_id'] == action['batch_id']]
        if len(matches) != 1:
            raise ValueError('source action lacks unique destination batch')
        row = matches[0]
        if action['source_namespace'] != 'mnt:[4026534768]' or action['source_action'] != 'SOURCE_RELEASED_EXACT_VVP':
            raise ValueError('unreviewed source release class; keep separate for owner review')
        source = {f['source_path']: f for f in action['files']}
        if set(source) != {f['source_path'] for f in row['files']}:
            raise ValueError('source action exact file set mismatch')
        for f in row['files']:
            if source[f['source_path']]['sha256'] != f['sha256'] or source[f['source_path']]['size_bytes'] != f['size_bytes']:
                raise ValueError('source action file digest mismatch')
        if action['target_receipt_sha256'] != row['manifest_sha256']:
            raise ValueError('source action references a different destination receipt')
        row.update(source_action=action['source_action'], source_commit=proof['source_commit'],
            source_receipt_sha256=proof['receipt_sha256'],
            source_confirmed_released_allocated_bytes=action['source_released_allocated_bytes'],
            source_df_free_before_after=dict(before=action['df_free_before_bytes'], after=action['df_free_after_bytes'],
                delta=action['df_free_delta_bytes'], source_namespace=action['source_namespace']))
    projects = {}
    for row in records:
        group = projects.setdefault(row['project'], dict(batches=0, archived_bytes=0,
            verified_restore_bytes=0, source_confirmed_released_allocated_bytes=0,
            source_df_free_delta_bytes=0))
        group['batches'] += 1
        group['archived_bytes'] += row['archived_bytes']
        group['verified_restore_bytes'] += row['verified_restore_bytes']
        group['source_confirmed_released_allocated_bytes'] += row['source_confirmed_released_allocated_bytes']
        group['source_df_free_delta_bytes'] += (row['source_df_free_before_after'] or {}).get('delta', 0)
    return dict(schema='STORAGE_OPS_V6_PROJECT_ARCHIVE_INDEX',
        created_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        archive_root=str(ARCHIVE), projects=projects, batches=records,
        archived_bytes=sum(x['archived_bytes'] for x in records),
        verified_restore_bytes=sum(x['verified_restore_bytes'] for x in records),
        source_confirmed_released_allocated_bytes=sum(x['source_confirmed_released_allocated_bytes'] for x in records),
        source_df_free_before_after=[dict(batch_id=x['batch_id'], **x['source_df_free_before_after']) for x in records if x['source_df_free_before_after']],
        protected_source_copy_logical_bytes=sum(x['archived_bytes'] for x in records if x['source_action'].startswith('SOURCE_KEEP')),
        global_source_candidate_bytes='UNKNOWN_SOURCE_OWNER_INVENTORY_ONLY',
        source_release_accounting='Separate independently pinned source receipts; never inferred from archived bytes',
        native_164_verified=False)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--source-actions', type=Path, help='explicit pinned independent receipt descriptors')
    args = parser.parse_args()
    data = inventory(json.loads(args.source_actions.read_text()) if args.source_actions else None)
    if args.write:
        raw = json.dumps(data, sort_keys=True).encode()
        name = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '_' + hashlib.sha256(raw).hexdigest()[:12] + '.json'
        folder = ARCHIVE / 'infrastructure' / 'indexes'
        mkdirs(ARCHIVE, folder)
        path = folder / name
        atomic_json(path, data)
        print(json.dumps(dict(path=str(path), sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
            projects=data['projects'], archived_bytes=data['archived_bytes'],
            verified_restore_bytes=data['verified_restore_bytes'],
            source_confirmed_released_allocated_bytes=data['source_confirmed_released_allocated_bytes'],
            source_df_free_before_after=data['source_df_free_before_after'])))
    else:
        print(json.dumps(data, indent=2))

if __name__ == '__main__':
    main()
