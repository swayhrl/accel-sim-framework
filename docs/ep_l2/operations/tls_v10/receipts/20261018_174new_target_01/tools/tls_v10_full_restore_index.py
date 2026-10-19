"""Read-only all-file archive/native index on top of the unchanged V9 tools.

Never receives, restores, grants source release, or modifies either tree.
An owned absent-before-restore reservation is required. Source release gates
remain independently owned by old174, including current source hashes/readers.
"""
import json
import os
from pathlib import Path
import stat
import subprocess

import v9_transaction as v9

NATIVE_ROOT = Path('/root/tls-v10-native-restore-20261018-target01')
META_KEYS = ('uid', 'gid', 'mode', 'mtime_ns')


def inventory(root):
    files, directories = set(), {'.'}
    v9.require(stat.S_ISDIR(root.lstat().st_mode), 'not a real directory')
    for parent, names, regular in os.walk(root, followlinks=False):
        for name in names + regular:
            p = Path(parent) / name
            v9.no_symlinks(p)
            s = p.lstat()
            rel = p.relative_to(root).as_posix()
            if stat.S_ISDIR(s.st_mode):
                directories.add(rel)
            else:
                v9.require(stat.S_ISREG(s.st_mode) and s.st_nlink == 1, 'nonregular/hardlinked file')
                files.add(rel)
    return files, directories


def audit_full_restore(manifest, txid, archive_tree, native_tree, *, fixture=False):
    v9.require(v9.validate_manifest(manifest) == txid, 'manifest/txid mismatch')
    archive = v9.no_symlinks(archive_tree)
    native = v9.no_symlinks(native_tree)
    base = Path(manifest.get('destination_path_on_174new', manifest['genuine164_destination_root']))
    v9.require(archive == base / txid / 'tree', 'not the bound finalized archive tree')
    if fixture:
        v9.fixture_root(archive); v9.fixture_root(native)
    else:
        v9.require(os.readlink('/proc/self/ns/mnt') == 'mnt:[4026535153]', 'wrong target namespace')
        v9.mount_identity(archive)
        v9.require(native == NATIVE_ROOT / 'full_groups' / txid / 'tree', 'wrong independent native destination')
        mount = json.loads(subprocess.check_output(
            ['findmnt', '-J', '-T', str(native), '-o', 'TARGET,SOURCE,FSTYPE'], text=True))['filesystems'][0]
        v9.require((mount['target'], mount['source'], mount['fstype']) ==
                   (str(NATIVE_ROOT), 'tls-v10-target-native-proof', 'tmpfs'), 'native restore mount changed')
    expected_seal = dict(txid=txid, manifest_sha256=v9.digest(v9.canonical(manifest)),
                         policy='EXCLUSIVE_CREATE_COMMIT_MARKER_LAST', files=len(manifest['files']),
                         selector_sha256=manifest['selector_sha256'])
    v9.require(v9.no_symlinks(archive.parent / 'COMMIT.json').read_bytes() ==
               v9.canonical(expected_seal), 'archive not committed / commit mismatch')
    v9.require(v9.no_symlinks(archive.parent / 'manifest.json').read_bytes() ==
               v9.canonical(manifest), 'archive manifest drift')
    reservation = dict(schema='TLS_V10_FULL_NATIVE_RESTORE_RESERVATION_V1', txid=txid,
                       manifest_sha256=v9.digest(v9.canonical(manifest)),
                       native_tree=str(native), destination_absent_before_restore=True,
                       source_originals='SOURCE_KEEP')
    v9.require(v9.no_symlinks(native.parent / 'RESTORE_RESERVATION.json').read_bytes() ==
               v9.canonical(reservation), 'missing or changed absent-destination reservation')
    expected_inventory = ({r['relative_path'] for r in manifest['files']},
                          {r['relative_path'] for r in manifest['directories']})
    v9.require(inventory(archive) == expected_inventory, 'archive exact file/directory coverage')
    v9.require(inventory(native) == expected_inventory, 'native exact file/directory coverage')
    throttle = v9.Throttle()
    files, directories = [], []
    for row in manifest['files']:
        a = archive / row['relative_path']; n = native / row['relative_path']
        ai = v9.identity(a.lstat()); ni = v9.identity(n.lstat())
        v9.require(ai['size'] == ni['size'] == row['size'], 'original/archive/native size mismatch')
        v9.require(v9.hash_file(a, expected=ai, throttle=throttle) == row['sha256'] and
                   v9.hash_file(n, expected=ni, throttle=throttle) == row['sha256'], 'full original SHA mismatch')
        v9.require(all(ni[k] == row[k] for k in META_KEYS), 'native original numeric metadata mismatch')
        files.append(dict(relative_path=row['relative_path'], source_path=manifest['source_root'] + '/' + row['relative_path'],
                          original_frozen_identity=row, archive_path=str(a), archive_sha256=row['sha256'],
                          archive_observed_identity=ai, archive_metadata_projection_not_source_metadata=True,
                          native_path=str(n), native_sha256=row['sha256'], native_identity=ni,
                          source_numeric_metadata_restored=True, whole_original_file_verified=True))
    for row in manifest['directories']:
        n = native / row['relative_path']; s = n.lstat()
        actual = dict(uid=s.st_uid, gid=s.st_gid, mode=stat.S_IMODE(s.st_mode), mtime_ns=s.st_mtime_ns)
        v9.require(all(actual[k] == row[k] for k in META_KEYS), 'native directory numeric metadata mismatch')
        directories.append(dict(relative_path=row['relative_path'], original_frozen_metadata=row,
                                native_path=str(n), native_numeric_metadata=actual, verified=True))
    return dict(schema='TLS_V10_ALL_FILE_ARCHIVE_NATIVE_RESTORE_INDEX_V1',
                status='ALL_FILES_ARCHIVE_AND_NATIVE_RESTORE_VERIFIED', txid=txid,
                selector_sha256=manifest['selector_sha256'], manifest_sha256=v9.digest(v9.canonical(manifest)),
                source_file_inventory_sha256=manifest.get('source_file_inventory_sha256'),
                source_directory_inventory_sha256=manifest.get('source_directory_inventory_sha256'),
                archive_tree=str(archive), native_tree=str(native), files=files, directories=directories,
                file_count=len(files), directory_count=len(directories),
                original_logical_bytes=sum(r['size'] for r in manifest['files']),
                full_file_SHA_and_numeric_metadata_verified=True,
                ctime='SOURCE_PROVENANCE_ONLY_NOT_RESTORABLE',
                current_source_identity_and_readers_not_certified_by_target=True,
                target_has_source_unlink_authority=False, source_release_performed=False)
