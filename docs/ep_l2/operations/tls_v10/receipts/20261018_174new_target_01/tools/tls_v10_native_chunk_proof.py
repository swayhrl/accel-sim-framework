"""Independently restore one accepted V9 chunk; never claim whole-file proof.

No uploader, source operation, cleanup or daemon. Production calls only read an
exact real164 V9 chunk and write an owned native proof under the V10 tmpfs.
All-file group restoration remains the unchanged V9 native_restore function.
"""
import os
from pathlib import Path
import stat

import v9_transaction as v9

NATIVE_ROOT = Path('/root/tls-v10-native-restore-20261018-target01')
RAW_CAP = 128 * 1024**2


def hex_digest(value):
    return isinstance(value, str) and len(value) == 64 and all(c in '0123456789abcdef' for c in value)


def prove_chunk(manifest, txid, relative_path, offset, length, chunk_sha256,
                archive_chunk, destination, *, fixture=False, crash=None):
    """Exclusive, resumable native proof of CHUNK_RANGE_ONLY, with no deletion.

    A complete owned orphan is hash-checked before adoption; incomplete or
    corrupt orphans HOLD. Repetition rehashes the native proof and never copies
    over it. A failed/incomplete original group cannot become RESTORE_VERIFIED.
    """
    v9.require(hex_digest(txid) and v9.validate_manifest(manifest) == txid, 'manifest/txid disagreement')
    v9.require(crash is None or fixture, 'fault injection is synthetic-only')
    v9.require(hex_digest(chunk_sha256), 'chunk SHA encoding')
    v9.require(type(offset) is int and type(length) is int and
               offset >= 0 and 0 < length <= RAW_CAP, 'raw chunk range/cap')
    v9.relpath(relative_path)
    rows = {r['relative_path']: r for r in manifest['files']}
    v9.require(relative_path in rows, 'chunk outside exact selector')
    original = rows[relative_path]
    v9.require(offset + length <= original['size'], 'range exceeds original file')
    key = v9.digest(relative_path.encode()) + '.%016d' % offset
    source = v9.no_symlinks(archive_chunk)
    dest = v9.no_symlinks(destination)
    base = Path(manifest.get('destination_path_on_174new', manifest['genuine164_destination_root']))
    v9.require(source in [base / (txid + '.partial') / 'chunks' / key,
                          base / txid / 'chunks' / key], 'not the bound accepted V9 chunk')
    if fixture:
        v9.fixture_root(base); v9.fixture_root(dest)
    else:
        v9.require(os.readlink('/proc/self/ns/mnt') == 'mnt:[4026535153]', 'wrong target namespace')
        v9.mount_identity(source)
        v9.require(dest == NATIVE_ROOT / 'chunk_proofs' / txid / key, 'wrong native proof destination')
        import json
        import subprocess
        mount = json.loads(subprocess.check_output(
            ['findmnt', '-J', '-T', str(NATIVE_ROOT), '-o', 'TARGET,SOURCE,FSTYPE'], text=True))['filesystems'][0]
        v9.require((mount['target'], mount['source'], mount['fstype']) ==
                   (str(NATIVE_ROOT), 'tls-v10-target-native-proof', 'tmpfs'), 'native proof mount changed')
        mem = int(next(line.split()[1] for line in Path('/proc/meminfo').read_text().splitlines()
                       if line.startswith('MemAvailable:'))) * 1024
        current = int(Path('/sys/fs/cgroup/memory.current').read_text())
        maximum = int(Path('/sys/fs/cgroup/memory.max').read_text())
        v9.require(mem - length >= 64 * 1024**3 and maximum - current >= length, 'native proof RAM admission')
    throttle = v9.Throttle()
    v9.require(source.lstat().st_size == length, 'archive chunk length')
    v9.require(v9.hash_file(source, throttle=throttle) == chunk_sha256, 'archive chunk SHA')
    archive_identity = v9.identity(source.lstat())
    reservation = dict(schema='TLS_V10_NATIVE_CHUNK_PROOF_RESERVATION_V1', txid=txid,
                       manifest_sha256=v9.digest(v9.canonical(manifest)), relative_path=relative_path,
                       original_sha256=original['sha256'], original_size=original['size'],
                       offset=offset, length=length, chunk_sha256=chunk_sha256,
                       numeric_metadata={k: original[k] for k in ('uid', 'gid', 'mode', 'mtime_ns')},
                       proof_scope='CHUNK_RANGE_ONLY', source_action='SOURCE_KEEP')
    if not dest.exists():
        # Its parents are an owned proof namespace, never a source/experimental tree.
        dest.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        v9.no_symlinks(dest.parent)
        dest.mkdir(mode=0o700)
        v9.exclusive_json(dest / 'RESERVATION.json', reservation)
    else:
        v9.no_symlinks(dest / 'RESERVATION.json')
        v9.require(dest.is_dir() and (dest / 'RESERVATION.json').exists(), 'unreserved existing native tree')
        v9.require((dest / 'RESERVATION.json').read_bytes() == v9.canonical(reservation), 'native proof reservation drift')
    payload = v9.no_symlinks(dest / 'payload')
    partial = v9.no_symlinks(dest / 'payload.partial')
    reused = payload.exists()
    if not reused:
        if not partial.exists():
            with source.open('rb') as inp, partial.open('xb') as out:
                remaining = length
                while remaining:
                    limit = min(remaining, 1024**2)
                    if crash == 'during_copy':
                        limit = min(limit, max(1, length // 2))
                    block = inp.read(limit)
                    v9.require(block, 'archive chunk shortened during copy')
                    out.write(block); throttle(len(block))
                    remaining -= len(block)
                    if crash == 'during_copy':
                        out.flush(); os.fsync(out.fileno())
                        raise v9.Hold('synthetic injected interruption during native chunk copy')
                v9.require(not inp.read(1), 'archive chunk grew during copy')
                out.flush(); os.fsync(out.fileno())
            v9.require(v9.identity(source.lstat()) == archive_identity, 'archive chunk identity drift during copy')
            if crash == 'after_copy':
                raise v9.Hold('synthetic injected interruption after native chunk copy')
        v9.require(partial.lstat().st_size == length and
                   v9.hash_file(partial, throttle=throttle) == chunk_sha256, 'incomplete/corrupt owned native orphan HOLD')
        os.chown(partial, original['uid'], original['gid'])
        os.chmod(partial, original['mode'])
        os.utime(partial, ns=(original['mtime_ns'], original['mtime_ns']), follow_symlinks=False)
        v9.rename_noreplace(partial, payload)
        if crash == 'after_finalize':
            raise v9.Hold('synthetic injected interruption after native chunk finalize')
    # Do not fix metadata on an existing final proof: drift is a HOLD.
    s = payload.lstat()
    v9.require(stat.S_ISREG(s.st_mode) and s.st_nlink == 1 and s.st_size == length, 'native final type/size/link drift')
    v9.require((s.st_uid, s.st_gid, stat.S_IMODE(s.st_mode), s.st_mtime_ns) ==
               tuple(original[k] for k in ('uid', 'gid', 'mode', 'mtime_ns')), 'native final metadata drift')
    v9.require(v9.hash_file(payload, throttle=throttle) == chunk_sha256, 'native reopen chunk SHA')
    receipt = dict(schema='TLS_V10_NATIVE_CHUNK_RESTORE_RECEIPT_V1', status='RESTORE_VERIFIED',
                   proof_scope='CHUNK_RANGE_ONLY', **{k: reservation[k] for k in
                   ('txid', 'manifest_sha256', 'relative_path', 'original_sha256', 'original_size',
                    'offset', 'length', 'chunk_sha256', 'numeric_metadata')},
                   native_payload=str(payload), native_metadata_verified=True,
                   ctime='PROVENANCE_ONLY_NOT_RESTORABLE',
                   original_full_file_restored=False, complete_group_restored=False,
                   source_action='SOURCE_KEEP', source_release_authorized=False)
    v9.exclusive_json(dest / 'RESTORE_RECEIPT.json', receipt)
    return dict(receipt=receipt, reused_existing_native_proof=reused)
