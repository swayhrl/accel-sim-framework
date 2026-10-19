"""Pure bounded grouping of existing V9 raw ranges; no receiving or READY API.

The result is an inactive planning proposal, not a window, resource admission,
source SHA, bridge inventory or acknowledgment. One manifest/txid per call.
Production still independently admits, hashes and restores every range with
the existing V9 transaction and native-proof functions, serially.
"""
import v9_transaction as v9

RAW_CAP = 128 * 1024**2
MAX_ENTRIES = 128


def plan_batches(manifest, txid, *, raw_cap=RAW_CAP, window_cap=RAW_CAP,
                 max_entries=MAX_ENTRIES, first_range_alone=False):
    v9.require(v9.validate_manifest(manifest) == txid, 'manifest/txid conflict')
    v9.require(type(raw_cap) is int and 0 < raw_cap <= RAW_CAP, 'raw cap')
    v9.require(type(window_cap) is int and 0 < window_cap <= RAW_CAP, 'window cap')
    v9.require(type(max_entries) is int and 0 < max_entries <= MAX_ENTRIES, 'entry cap')
    v9.require(type(first_range_alone) is bool, 'canary option type')
    binding = dict(txid=txid, selector_sha256=manifest['selector_sha256'],
                   manifest_sha256=v9.digest(v9.canonical(manifest)))
    batches, current, total, empty = [], [], 0, []

    def flush():
        nonlocal current, total
        if current:
            batches.append(dict(**binding, entries=current, raw_bytes=total))
            current, total = [], 0

    for row in manifest['files']:
        v9.require(type(row['size']) is int and row['size'] >= 0, 'integer file size')
        if row['size'] == 0:
            v9.require(row['sha256'] == v9.digest(b''), 'empty-file SHA')
            empty.append(row['relative_path'])
            continue
        offset = 0
        while offset < row['size']:
            length = min(raw_cap, window_cap, row['size'] - offset)
            if current and (len(current) == max_entries or total + length > window_cap):
                flush()
            current.append(dict(relative_path=row['relative_path'], offset=offset,
                                length=length, original_size=row['size'],
                                original_sha256=row['sha256']))
            total += length
            offset += length
            if first_range_alone and not batches:
                flush()
    flush()
    return dict(schema='TLS_V10_INACTIVE_RAW_BATCH_PLAN_V1', **binding,
                source_root=manifest['source_root'],
                native164_root=manifest['genuine164_destination_root'],
                batches=batches, empty_files=empty,
                raw_cap=raw_cap, window_cap=window_cap, max_entries=max_entries,
                first_range_alone=first_range_alone,
                physical_bridge_cap=256 * 1024**2,
                physical_allocation_proven=False,
                copy_ready=False, receiving_authorized=False,
                source_action='SOURCE_KEEP', source_release_authorized=False)
