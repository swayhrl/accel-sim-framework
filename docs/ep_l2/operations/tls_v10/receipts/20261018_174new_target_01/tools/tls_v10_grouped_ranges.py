"""Serial range adapter over V9 accept_chunk and the verified native proof.

No sender, cleanup, window creator, source gate or permission evaluator.
Production caller must independently authenticate Source Git/bridge READY,
fresh scoped admission, original window and current global resource/lock state.
This adapter only checks exact frozen range bindings and performs serial I/O.
"""
from pathlib import Path
import stat

import v9_transaction as v9
import tls_v10_native_chunk_proof as native

ID_KEYS = ('dev', 'inode', 'nlink', 'size', 'allocated', 'uid', 'gid', 'mode', 'mtime_ns', 'ctime_ns')
RAW_CAP = 128 * 1024**2


def accept_group(transfer, window, entries, *, native_parent, fixture=False, crash_after=None):
    v9.require(crash_after is None or fixture, 'synthetic fault injection only')
    m = transfer.manifest
    v9.require(window['txid'] == transfer.txid and
               window['selector_sha256'] == m['selector_sha256'] and
               window['canonical_manifest_sha256'] == v9.digest(v9.canonical(m)), 'group binding mismatch')
    expected = window['ranges']
    v9.require(0 < len(expected) == len(entries) <= 128, 'range count/cap')
    v9.require(all(type(e['offset']) is int and type(e['length']) is int and
                   e['offset'] >= 0 and 0 < e['length'] <= RAW_CAP for e in expected), 'range type/cap')
    v9.require(sum(e['length'] for e in expected) <= RAW_CAP, 'window raw byte cap')
    seen, seen_bridge, bounds, checked = set(), set(), {}, []
    allocated = 0
    for want, ready in zip(expected, entries):
        name = v9.relpath(want['relative_path']).as_posix()
        v9.require(name in transfer.rows, 'range outside frozen group')
        row = transfer.rows[name]
        for key in ('relative_path', 'offset', 'length'):
            v9.require(ready[key] == want[key] and type(ready[key]) is type(want[key]), 'READY/window range mismatch')
        v9.require(want['offset'] + want['length'] <= row['size'], 'range outside original file')
        v9.require(want['original_sha256'] == row['sha256'] and want['original_size'] == row['size'], 'original SHA/size mismatch')
        v9.require(set(ready['source_identity']) == set(ID_KEYS) and
                   all(type(v) is int for v in ready['source_identity'].values()) and
                   ready['source_identity'] == {k: row[k] for k in ID_KEYS}, 'frozen source identity mismatch')
        v9.require(ready['source_full_sha256'] == row['sha256'], 'source full-file SHA mismatch')
        v9.require(native.hex_digest(ready['chunk_sha256']), 'chunk SHA encoding')
        if want['offset'] == 0 and want['length'] == row['size']:
            v9.require(ready['chunk_sha256'] == row['sha256'], 'whole original chunk SHA mismatch')
        key = (name, want['offset'])
        v9.require(key not in seen, 'duplicate range')
        seen.add(key)
        span = (want['offset'], want['offset'] + want['length'])
        v9.require(all(span[1] <= a or span[0] >= b for a, b in bounds.get(name, [])), 'overlapping ranges')
        bounds.setdefault(name, []).append(span)
        p = v9.no_symlinks(ready['bridge_path'])
        v9.require(str(p) == want['bridge_path'] and str(p) not in seen_bridge, 'bridge path binding/duplicate')
        seen_bridge.add(str(p))
        if fixture:
            v9.fixture_root(p)
        else:
            v9.require(p == Path(window['bridge_root']) / ('range-%04d.bin' % len(checked)), 'wrong window bridge payload')
        s = p.lstat()
        v9.require(stat.S_ISREG(s.st_mode) and s.st_nlink == 1 and s.st_size == want['length'], 'bridge type/link/size')
        identity = v9.identity(s)
        v9.require(set(ready['bridge_identity']) == set(ID_KEYS) and
                   all(type(v) is int for v in ready['bridge_identity'].values()) and
                   identity == ready['bridge_identity'], 'bridge frozen identity mismatch')
        v9.require(fixture or identity['dev'] == 2431, 'wrong bridge filesystem')
        allocated += identity['allocated']
        checked.append((want, ready, p, identity))
    v9.require(allocated <= 256 * 1024**2, 'bridge payload allocation cap')
    result = []
    for want, ready, p, identity in checked:
        name = want['relative_path']; offset = want['offset']
        key = v9.digest(name.encode()) + '.%016d' % offset
        chunk = transfer.work / 'chunks' / key
        reused = chunk.exists()
        accepted = transfer.accept_chunk(name, offset, p, ready['chunk_sha256'], txid=transfer.txid)
        v9.require(v9.hash_file(chunk, throttle=transfer.throttle) == ready['chunk_sha256'], 'NAS reopen SHA')
        proof = native.prove_chunk(m, transfer.txid, name, offset, want['length'], ready['chunk_sha256'],
                                   chunk, Path(native_parent) / transfer.txid / key, fixture=fixture)
        v9.require(v9.identity(p.lstat()) == identity, 'bridge changed during acceptance')
        result.append(dict(range=want, bridge_path=str(p), bridge_identity=identity,
                           archive_chunk=str(chunk), accepted=accepted,
                           reused_archive_chunk=reused, native_proof=proof))
        if crash_after == len(result):
            raise v9.Hold('synthetic interruption after %d verified ranges' % len(result))
    return dict(schema='TLS_V10_GROUPED_RANGE_ACCEPTANCE_V1', txid=transfer.txid,
                selector_sha256=m['selector_sha256'], manifest_sha256=v9.digest(v9.canonical(m)),
                entries=result, range_count=len(result), raw_bytes=sum(e['length'] for e in expected),
                payload_allocated_bytes=allocated, proof_scope='COLLECTION_OF_CHUNK_RANGES',
                complete_group_archived=False, complete_group_native_restored=False,
                source_originals='SOURCE_KEEP', bridge_cleanup_performed=False,
                source_files_deleted=0, original_source_release_performed=False)
