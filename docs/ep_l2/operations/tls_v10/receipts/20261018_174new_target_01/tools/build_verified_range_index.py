"""Metadata-only recovery index of closed, Git-published P9 range windows.

Does not read scientific payloads, receive data, or authorize Source release.
Full-original reassembly and the absent-path all-file native restore remain pending.
"""
import hashlib
import json
import subprocess
import tls_target as t

M = t.get('SOURCE_TLS_V10_P9_PUBLIC_TARGET_TRANSACTION_MANIFEST.json')
reserved = t.get('TLS_V10_P9_PUBLIC_TARGET_ROOT_RESERVED.json')
head = t.git('rev-parse', 'HEAD').decode().strip()
assert t.git('rev-parse', 'origin/' + t.BRANCH).decode().strip() == head
windows = []
names = []
for number in range(1, 34):
    w = 'TLS_V10_P9_PUBLIC_B%04d' % number
    if not (t.BASE / (w + '_BRIDGE_CLEANUP_COPY16.json')).exists():
        break
    windows.append(w)
    names += [w + '_' + s for s in
              ('DEST_VERIFIED.json', 'RESTORE_VERIFIED.json', 'BRIDGE_CLEANUP_COPY16.json')]
assert windows
prefix = t.BASE.relative_to(t.REPO).as_posix() + '/'
raw = subprocess.check_output(['git', 'cat-file', '--batch'], cwd=t.REPO,
    input=''.join(head + ':' + prefix + n + '\n' for n in names).encode())
pos = 0
for name in names:
    end = raw.index(b'\n', pos)
    header = raw[pos:end].split()
    assert len(header) == 3 and header[1] == b'blob'
    size = int(header[2]); body = raw[end + 1:end + 1 + size]
    assert body == (t.BASE / name).read_bytes(), name
    pos = end + size + 2
assert pos == len(raw)
frozen = {r['relative_path']: r for r in M['files']}
entries = []
for w in windows:
    D = t.get(w + '_DEST_VERIFIED.json')
    R = t.get(w + '_RESTORE_VERIFIED.json')
    C = t.get(w + '_BRIDGE_CLEANUP_COPY16.json')
    assert D['status'] == 'DEST_VERIFIED' and R['status'] == 'RESTORE_VERIFIED'
    assert all(x['txid'] == reserved['txid'] for x in (D, R, C))
    assert all(x['source_originals'] == 'SOURCE_KEEP' for x in (D, R, C))
    assert C['target_dest_receipt_sha256'] == t.sha(t.BASE / (w + '_DEST_VERIFIED.json'))
    assert C['target_restore_receipt_sha256'] == t.sha(t.BASE / (w + '_RESTORE_VERIFIED.json'))
    ds = D.get('entries', [D]); rs = R.get('entries', [R])
    assert len(ds) == len(rs)
    for d, r in zip(ds, rs):
        proof = r['native_chunk_proof']['receipt']
        for k in ('relative_path', 'offset', 'length'):
            assert d[k] == r[k] == proof[k]
        row = frozen[d['relative_path']]
        sha = d['archived_close_reopen_sha256']
        assert sha == proof['chunk_sha256']
        assert proof['original_sha256'] == row['sha256']
        assert proof['numeric_metadata'] == {k: row[k] for k in ('uid', 'gid', 'mode', 'mtime_ns')}
        assert proof['native_metadata_verified'] and not proof['original_full_file_restored']
        assert proof['proof_scope'] == 'CHUNK_RANGE_ONLY'
        archive = d['archived_chunk_path']
        assert archive.startswith(M['destination_path_on_174new'] + '/')
        key = hashlib.sha256(d['relative_path'].encode()).hexdigest() + '.%016d' % d['offset']
        assert archive.endswith('/chunks/' + key)
        entries.append(dict(relative_path=d['relative_path'], offset=d['offset'], length=d['length'],
            source_path=M['source_root'] + '/' + d['relative_path'], original_size=row['size'],
            original_frozen_full_sha256=row['sha256'], chunk_sha256=sha,
            archive_path_on_174new=archive, archive_path_native164=archive.replace('/root/share/mnt164', '/home/shared', 1),
            volatile_native_range_proof=proof['native_payload'], native_numeric_metadata=proof['numeric_metadata'],
            native_receipt_sha256=r['native_restore_receipt_sha256'], window_id=w,
            target_proof_git_commit=C['target_proof_git_commit'], source_ACK_git_commit=C['source_ACK_git_commit'],
            source_ACK_sha256=C['source_ACK_sha256'],
            dest_receipt_sha256=C['target_dest_receipt_sha256'], restore_receipt_sha256=C['target_restore_receipt_sha256']))
entries.sort(key=lambda r: (r['relative_path'], r['offset']))
assert len({(r['relative_path'], r['offset']) for r in entries}) == len(entries)
coverage = []
for name, row in frozen.items():
    offset = 0
    ranges = [r for r in entries if r['relative_path'] == name]
    for r in ranges:
        assert r['offset'] == offset and r['length'] > 0
        offset += r['length']
    assert offset <= row['size']
    coverage.append(dict(relative_path=name, original_size=row['size'], accepted_prefix_bytes=offset,
        nonempty_original_fully_range_covered=bool(row['size'] and offset == row['size']),
        full_original_reassembled_and_restored=False))
out = dict(schema='TLS_V10_P9_CLOSED_RANGE_RECOVERY_INDEX_V1', utc=t.now(),
    basis_target_Git_commit=head, txid=reserved['txid'], selector_sha256=M['selector_sha256'],
    canonical_manifest_sha256=reserved['canonical_manifest_sha256'], source_originals='SOURCE_KEEP',
    proof_scope='CHUNK_RANGES_ONLY_NOT_FULL_ORIGINAL_OR_GROUP_RESTORE', closed_windows=windows,
    range_count=len(entries), archived_and_native_range_verified_bytes=sum(r['length'] for r in entries),
    nonempty_originals_fully_range_covered=sum(r['nonempty_original_fully_range_covered'] for r in coverage),
    full_original_reassembled_and_restored_count=0, full_group_verified=False,
    native_proofs_volatile=True, durable_archive_and_inventory_on_genuine164=True,
    source_files_deleted_by_target=0, source_workspace_science_release_bytes=0,
    entries=entries, coverage=coverage)
t.save('TLS_V10_P9_PUBLIC_CLOSED_RANGE_RECOVERY_INDEX.json', out)
print(json.dumps({k: out[k] for k in ('range_count', 'archived_and_native_range_verified_bytes',
                                    'nonempty_originals_fully_range_covered', 'basis_target_Git_commit')}))
