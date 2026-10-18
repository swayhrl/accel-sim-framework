"""Pure TLS selector normalization for the existing V9 receiver; no I/O executor.

Inputs are immutable original source JSONL bytes and their publication commit.
Output does not grant COPY_READY, resource admission, or source deletion.
"""
import argparse
import json
from pathlib import Path, PurePosixPath
import re

import v9_transaction as v9

SOURCE_FS = 'old174|mnt:[4026534768]|dev156|workspace-overlay'
NATIVE_BASE = '/home/shared/huangrulin/host174_storage_recovery/tls_v10'
PRIMARY = '/workspace/worktrees/accel-sim-tls-cache'
V5 = '/workspace/worktrees/accel-sim-tls-cache-v5-observe'
DYNAMIC = '/workspace/worktrees/accel-sim-tls-dynamic-way'
GPGPU_DYNAMIC = '/workspace/worktrees/gpgpu-sim-tls-dynamic-way'
GROUPS = {
    'P9_PUBLIC': PRIMARY + '/hw_run/tls-cache-p9-public-v1',
    'P9_MATRIX_V3': PRIMARY + '/hw_run/tls-cache-p9/matrix-v3',
    'P9_MATRIX_V4': PRIMARY + '/hw_run/tls-cache-p9/matrix-v4',
    'P9_MATRIX_PRE_V2': PRIMARY + '/hw_run/tls-cache-p9/matrix-pre-v2',
    'P9_PAPER_V4': PRIMARY + '/hw_run/tls-cache-p9/paper-v4',
    'PRIMARY_BUILD': PRIMARY + '/gpu-simulator/build',
    'V5_RESULTS': V5 + '/hw_run/tls-cache-p9-v5',
    'V5_BUILD': V5 + '/gpu-simulator/build',
    'DYNAMIC_FRAMEWORK_RESULTS': DYNAMIC + '/hw_run/tls-way-static',
    'DYNAMIC_FRAMEWORK_BUILD': DYNAMIC + '/gpu-simulator/build',
    'DYNAMIC_FRAMEWORK_BIN': DYNAMIC + '/gpu-simulator/bin',
    'DYNAMIC_GPGPU_BUILD': GPGPU_DYNAMIC + '/build',
}
for version in ('p0', 'p1', 'p3', 'p4', 'p5', 'p6', 'p7', 'p8'):
    GROUPS['PRIMARY_' + version.upper()] = PRIMARY + '/hw_run/tls-cache-' + version
for name in ('tls-cache-spmv-smoke-v1', 'tls-cache-v100-smoke-v1',
             'tls-cache-v100-smoke-v2', 'tls-cache-v100-smoke-v3',
             'tls-cache-v100-smoke-v4'):
    GROUPS['PRIMARY_' + name.upper().replace('-', '_')] = PRIMARY + '/hw_run/' + name


def hex_string(value, length):
    return isinstance(value, str) and re.fullmatch('[0-9a-f]{%d}' % length, value) is not None


def normalize_row(row, root, kind):
    v9.require(row.get('schema') == 'TLS_V10_OLD174_EXACT_SOURCE_ENTRY_V1', 'original row schema')
    v9.require(row.get('type') == kind and row.get('source_action') == 'SOURCE_KEEP', 'type/source action')
    rel = row['relative_path']
    v9.relpath(rel, root_ok=kind == 'directory')
    expected = root if rel == '.' else str(PurePosixPath(root) / rel)
    v9.require(row['source_root'] == root and row['source_path'] == expected, 'source path/root drift')
    v9.require(hex_string(row['source_commit'], 40), 'source code provenance commit')
    numeric = ['dev', 'inode', 'nlink', 'uid', 'gid', 'size_bytes', 'allocated_bytes', 'mtime_ns', 'ctime_ns']
    v9.require(all(type(row[k]) is int for k in numeric), 'noninteger identity')
    v9.require(row['dev'] == 156 and row['inode'] > 0 and row['nlink'] > 0, 'source identity/device')
    v9.require(all(row[k] >= 0 for k in ['uid', 'gid', 'size_bytes', 'allocated_bytes']), 'negative size/ownership')
    v9.require(row['allocated_bytes'] % 512 == 0, 'invalid source st_blocks')
    v9.require(isinstance(row['mode_octal'], str) and re.fullmatch(r'0o[0-7]{1,4}', row['mode_octal']) is not None, 'mode encoding')
    mode = int(row['mode_octal'], 8)
    if kind == 'regular':
        v9.require(row['nlink'] == 1 and hex_string(row['sha256'], 64), 'file link/SHA policy')
    else:
        v9.require(row['sha256'] is None, 'directory content SHA is not a file SHA')
    result = dict(relative_path=rel, type=kind, dev=row['dev'], inode=row['inode'],
                  nlink=row['nlink'], uid=row['uid'], gid=row['gid'], mode=mode,
                  mtime_ns=row['mtime_ns'], ctime_ns=row['ctime_ns'],
                  size=row['size_bytes'], allocated=row['allocated_bytes'])
    if kind == 'regular':
        result['sha256'] = row['sha256']
    return result


def build_manifest(files_raw, directories_raw, frozen_commit, group):
    v9.require(group in GROUPS, 'group not independently enumerated')
    v9.require(hex_string(frozen_commit, 40), 'frozen publication commit')
    v9.require(isinstance(files_raw, bytes) and isinstance(directories_raw, bytes), 'raw JSONL bytes required')
    root = GROUPS[group]
    original_files = [json.loads(line) for line in files_raw.splitlines()]
    original_dirs = [json.loads(line) for line in directories_raw.splitlines()]
    files = [normalize_row(r, root, 'regular') for r in original_files]
    dirs = [normalize_row(r, root, 'directory') for r in original_dirs]
    v9.require(dirs, 'root directory metadata required')
    # Preserve the exact frozen order. Sorting would silently change the selector.
    selector = v9.digest(v9.canonical(files))
    native = NATIVE_BASE + '/20261018_' + group + '_' + selector
    # Mirror the source builder's minimal V9 manifest exactly, with the native
    # root in the five-field identity and the mounted alias in a separate field.
    manifest = dict(source_filesystem_identity=SOURCE_FS,
                    source_root=root, source_frozen_commit=frozen_commit,
                    source_file_inventory_sha256=v9.digest(files_raw),
                    source_directory_inventory_sha256=v9.digest(directories_raw),
                    selector_sha256=selector, genuine164_destination_root=native,
                    destination_path_on_174new='/root/share/mnt164' + native[len('/home/shared'):],
                    files=files, directories=dirs,
                    source_originals_action='SOURCE_KEEP_NO_RELEASE_AUTHORITY')
    txid = v9.validate_manifest(manifest)
    dirpaths = {d['relative_path'] for d in dirs}
    for d in dirs:
        for parent in PurePosixPath(d['relative_path']).parents:
            v9.require(parent.as_posix() in dirpaths, 'missing empty-directory parent metadata')
    return manifest, txid


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--files', required=True)
    parser.add_argument('--directories', required=True)
    parser.add_argument('--frozen-commit', required=True)
    parser.add_argument('--group', choices=sorted(GROUPS), required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    manifest, txid = build_manifest(Path(args.files).read_bytes(), Path(args.directories).read_bytes(),
                                    args.frozen_commit, args.group)
    # Exclusive local control creation; this CLI has no SSH, source write or unlink.
    with Path(args.output).open('xb') as stream:
        stream.write(v9.canonical(manifest))
    print(json.dumps(dict(txid=txid, manifest_sha256=v9.digest(v9.canonical(manifest)),
                          native164_root=manifest['genuine164_destination_root'],
                          source_action='SOURCE_KEEP', copy_ready=False)))


if __name__ == '__main__':
    main()
