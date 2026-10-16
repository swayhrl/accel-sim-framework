"""V7 complete-project receipt coverage and non-overwriting target restore drill.

Read-only plan by default. Source original paths are data, never write targets.
--verify-all rehashes archived files. --execute-restore needs full coverage and
writes only a fresh independent directory under the authorized archive root.
It does not establish native old174 metadata restoration or release permission.
"""
import argparse
import ctypes
import hashlib
import json
import os
from pathlib import Path
import subprocess
import re

from archive_receiver import ARCHIVE, BRIDGE, check_resources, relative, require, sha, mkdirs

def read_zstd_jsonl(path, expected):
    raw = Path(path).read_bytes()
    require(hashlib.sha256(raw).hexdigest() == expected, 'source manifest SHA256 mismatch')
    z = ctypes.CDLL('libzstd.so.1')
    z.ZSTD_decompress.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_void_p, ctypes.c_size_t]
    z.ZSTD_decompress.restype = ctypes.c_size_t
    z.ZSTD_isError.argtypes = [ctypes.c_size_t]
    z.ZSTD_isError.restype = ctypes.c_uint
    buffer = ctypes.create_string_buffer(64 * 1024**2)
    length = z.ZSTD_decompress(buffer, len(buffer), raw, len(raw))
    require(not z.ZSTD_isError(length), 'metadata decompression failed or exceeds 64MiB bound')
    rows = [json.loads(line) for line in buffer.raw[:length].decode().splitlines()]
    return [r for r in rows if 'source_path' in r and 'sha256' in r]

def plan(mapping, project_id, rows, receipts):
    require(re.fullmatch('[A-Za-z0-9][A-Za-z0-9_.-]{0,63}', project_id) is not None, 'unsafe project id')
    require(mapping['destination_archive_root'] == str(ARCHIVE), 'project map archive root mismatch')
    project = next(p for p in mapping['projects'] if p['id'] == project_id)
    source_root = Path(project['original_realpath'])
    archive_root = Path(project['archive_realpath_on_174new'])
    archive_root.relative_to(ARCHIVE)
    require(archive_root.resolve() == archive_root, 'archive root path mapping contains symlink')
    require(len(rows) == project['regular_file_count'], 'source scope count mismatch')
    verified = {}
    for path in receipts:
        data = json.loads(Path(path).read_text())
        require(data['status'] == 'DEST_VERIFIED' and data['verification_level'] == 'SSHFS_READBACK_VERIFIED',
                'unverified receipt supplied')
        for f in data['files']:
            if f['source_path'] not in verified:
                verified[f['source_path']] = f
            else:
                require(verified[f['source_path']]['destination_sha256'] == f['destination_sha256'],
                        'conflicting source receipt digest')
    output, missing = [], []
    for row in rows:
        rel = relative(row['relative_path'])
        require(Path(row['source_path']) == source_root / rel and row['nlink'] == 1,
                'source structure or hardlink scope mismatch')
        dest = archive_root / rel
        item = verified.get(row['source_path'])
        if item is None:
            missing.append(row['relative_path'])
        else:
            require(item['destination_path'] == str(dest) and item['size_bytes'] == row['size_bytes']
                    and item['destination_sha256'] == row['sha256'] == item['source_sha256'],
                    'full-project path/hash coverage mismatch')
            require(dest.resolve() == dest and dest.lstat().st_size == row['size_bytes'], 'archive changed')
        output.append(dict(relative_path=str(rel), source_original_path=row['source_path'],
            archive_path=str(dest), size_bytes=row['size_bytes'], sha256=row['sha256'],
            source_owner=row.get('owner'), source_mode=row.get('mode'), source_uid=row.get('uid'),
            source_gid=row.get('gid')))
    return project, output, missing

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--map', required=True)
    p.add_argument('--project', required=True)
    p.add_argument('--source-manifest', required=True)
    p.add_argument('--expected-manifest-sha256', required=True)
    p.add_argument('--receipt', action='append', default=[])
    p.add_argument('--verify-all', action='store_true')
    p.add_argument('--execute-restore', action='store_true')
    args = p.parse_args()
    mapping = json.loads(Path(args.map).read_text())
    rows = read_zstd_jsonl(args.source_manifest, args.expected_manifest_sha256)
    project, files, missing = plan(mapping, args.project, rows, args.receipt)
    result = dict(schema='STORAGE_OPS_V7_PROJECT_COVERAGE_AND_RESTORE_PLAN', project_id=args.project,
        source_manifest_sha256=args.expected_manifest_sha256, expected_files=len(files),
        verified_receipt_files=len(files)-len(missing), missing_files=len(missing), missing_sample=missing[:12],
        original_path=project['original_realpath'], archive_path=project['archive_realpath_on_174new'],
        allocated_regular_file_upper_bound_bytes=sum(r['allocated_bytes'] for r in rows),
        actual_source_df_gain_bytes=0, source_action='SOURCE_KEEP', source_release_authorized=False,
        old174_native_restore_status='NOT_RUN_REQUIRES_SOURCE_OWNER_AND_BRIDGE_REVERSE_HANDSHAKE',
        old174_no_overwrite_restore_location=project['restore_staging_path'],
        native_file_metadata_complete=all(f['source_mode'] is not None and f['source_uid'] is not None
                                         and f['source_gid'] is not None for f in files),
        all_files_dest_verified=not missing, fresh_archive_rehash_bytes=0, verified_restore_bytes=0,
        state='ALL_FILES_DEST_VERIFIED' if not missing else 'PROJECT_ARCHIVE_INCOMPLETE')
    if args.verify_all or args.execute_restore:
        require(not missing, 'full project is not archived; no restore or source release')
        check_resources()
        import fcntl
        lock = os.open(BRIDGE / '.TARGET_RECEIVER.lock', os.O_RDWR | os.O_NOFOLLOW)
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            os.nice(19)
            restore = ARCHIVE / 'infrastructure' / 'restore_tests' / 'cold_projects' / (
                args.project + '_' + args.expected_manifest_sha256[:12])
            if args.execute_restore:
                require(not os.path.lexists(restore), 'refuse to overwrite an existing restore target')
            for f in files:
                digest, snap = sha(Path(f['archive_path']))
                require(digest == f['sha256'] and snap['size'] == f['size_bytes'], 'archived file mismatch')
                result['fresh_archive_rehash_bytes'] += f['size_bytes']
                if args.execute_restore:
                    dest = restore / relative(f['relative_path'])
                    mkdirs(ARCHIVE, dest.parent)
                    run = subprocess.run(['nice','-n','19','ionice','-c','3','rsync','-aH',
                        '--no-owner','--no-group','--fsync','--bwlimit=30m','--',f['archive_path'],str(dest)],
                        capture_output=True, timeout=180)
                    require(run.returncode == 0, 'restore copy failed')
                    got, restored = sha(dest)
                    require(got == f['sha256'], 'restored file mismatch')
                    result['verified_restore_bytes'] += restored['size']
            if args.execute_restore:
                result.update(state='FULL_CONTENT_RESTORE_VERIFIED_METADATA_AND_NATIVE_SOURCE_STILL_PENDING',
                    target_independent_restore_path=str(restore), native_server_metadata_verified=False)
        finally:
            os.close(lock)
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
