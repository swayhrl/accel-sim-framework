"""Independently recover frozen stage members from the completed 164 gzip/tar.

No extraction or scientific-source writes. --execute holds the existing receiver
lock and consumes the sole pipeline. Default only validates the frozen manifest.
Native permissions and native old174 import remain separate evidence.
"""
import argparse
import csv
import gzip
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import sys
import tarfile
import time

MANIFEST_SHA = 'bca6dfc2b43f4715ce0c6e55d4faa8ae11f3f4c7be7b96279e5671489004f274'
ARCHIVE_SHA = '9feffb121c304412ea7b8289e9ae0c7cabff5aef2098ff025fb65af2f43653ca'
ARCHIVE_BYTES = 17943970556
MEMBER_BYTES = 66331215249
RATE = 30 * 1024**2
BLOCK = 4 * 1024**2


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def expected_members(raw, expected_sha=MANIFEST_SHA, expected_count=13):
    require(hashlib.sha256(raw).hexdigest() == expected_sha, 'frozen manifest SHA mismatch')
    rows = list(csv.DictReader(io.StringIO(raw.decode()), delimiter='\t'))
    require(len(rows) == expected_count, 'stage file count mismatch')
    members, markers, paths = {}, [], set()
    for row in rows:
        path = PurePosixPath(row['relative_path_under_decoupled_l2_extract'])
        require(not path.is_absolute() and '..' not in path.parts and len(path.parts) > 2,
                'unsafe stage relative path')
        require(str(path) not in paths, 'duplicate frozen stage path')
        paths.add(str(path))
        if int(row['logical_bytes']) == 0:
            require(path.parts[1] == '.decoupled_l2_stage_complete' and
                    row['sha256'] == hashlib.sha256(b'').hexdigest(), 'invalid marker')
            markers.append(row)
        else:
            require(path.parts[1] == 'polybench', 'unexpected nonempty stage subtree')
            member = '/'.join(path.parts[1:])
            require(member not in members, 'duplicate frozen tar member mapping')
            members[member] = row
    return members, markers


class RateDigestReader:
    def __init__(self, stream, check):
        self.stream, self.check = stream, check
        self.digest, self.count = hashlib.sha256(), 0
        self.started = self.last_report = time.monotonic()

    def read(self, size=-1):
        raw = self.stream.read(BLOCK if size < 0 else min(size, BLOCK))
        self.digest.update(raw)
        self.count += len(raw)
        delay = self.count / RATE - (time.monotonic() - self.started)
        if delay > 0:
            time.sleep(delay)
        if time.monotonic() - self.last_report >= 30:
            self.check()
            print(json.dumps({'progress': 'RESTORE_STREAM', 'compressed_bytes': self.count}),
                  file=sys.stderr, flush=True)
            self.last_report = time.monotonic()
        return raw


def recover_members(stream, expected):
    seen, recovered = {}, 0
    with tarfile.open(fileobj=stream, mode='r|') as archive:
        for member in archive:
            name = member.name.removeprefix('./')
            if name not in expected:
                continue
            row = expected[name]
            require(name not in seen and member.isfile() and member.size == int(row['logical_bytes']),
                    'duplicate/nonregular/wrong-size selected tar member: ' + name)
            digest, count = hashlib.sha256(), 0
            content = archive.extractfile(member)
            require(content is not None, 'selected member cannot be read')
            with content:
                while True:
                    raw = content.read(BLOCK)
                    if not raw:
                        break
                    digest.update(raw)
                    count += len(raw)
            require(count == int(row['logical_bytes']) and digest.hexdigest() == row['sha256'],
                    'recovered member SHA256 mismatch: ' + name)
            seen[name] = dict(size_bytes=count, sha256=digest.hexdigest())
            recovered += count
    require(set(seen) == set(expected), 'incomplete selected member recovery')
    return seen, recovered


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', required=True)
    parser.add_argument('--receiver-bundle', required=True)
    parser.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    members, markers = expected_members(Path(args.manifest).read_bytes())
    require(len(members) == 11 and len(markers) == 2 and
            sum(int(r['logical_bytes']) for r in members.values()) == MEMBER_BYTES,
            'wrong production stage scope')
    if not args.execute:
        print(json.dumps(dict(status='READ_ONLY_RESTORE_PLAN_PASS', members=11, markers=2,
                              source_action='SOURCE_KEEP', data_written_bytes=0)))
        return
    import fcntl
    sys.path.insert(0, args.receiver_bundle)
    from archive_receiver import ARCHIVE, BRIDGE, check_resources, now
    check_resources()
    lock = os.open(BRIDGE/'.TARGET_RECEIVER.lock', os.O_RDWR | os.O_NOFOLLOW)
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        require(not any(BRIDGE.glob('*/files')), 'another bridge data phase is active')
        whole_raw = (ARCHIVE/'infrastructure/project_receipts/POLYBENCH_WHOLE_ARCHIVE_DEST_VERIFIED.json').read_bytes()
        whole = json.loads(whole_raw)
        require(whole['status'] == 'WHOLE_ARCHIVE_DEST_VERIFIED' and
                whole['size_bytes'] == ARCHIVE_BYTES and whole['destination_sha256'] == ARCHIVE_SHA,
                'whole archive receipt absent or inconsistent')
        path = ARCHIVE/'Decoupled-L2/old174/workspace/worktrees/accel-sim-decoupled-l2/hw_run/decoupled-l2-pretraces/polybench.tgz'
        require(str(path) == whole['destination_path'] and path.resolve(strict=True) == path and
                not path.is_symlink() and path.stat().st_size == ARCHIVE_BYTES, 'wrong archive path/size')
        before = path.stat()
        with path.open('rb') as raw_stream:
            reader = RateDigestReader(raw_stream, check_resources)
            with gzip.GzipFile(fileobj=reader, mode='rb') as decompressed:
                seen, recovered = recover_members(decompressed, members)
                while decompressed.read(BLOCK):
                    pass
            while reader.read(BLOCK):
                pass
        after = path.stat()
        require((before.st_size, before.st_mtime_ns) == (after.st_size, after.st_mtime_ns),
                'archive size/mtime changed during recovery')
        require(reader.count == ARCHIVE_BYTES and reader.digest.hexdigest() == ARCHIVE_SHA and
                recovered == MEMBER_BYTES, 'complete compressed hash/size or stage total mismatch')
        print(json.dumps(dict(schema='STORAGE_OPS_R10_POLYBENCH_STREAMING_RESTORE_V1',
            status='ALL_11_STAGE_MEMBERS_RECOVERED_SHA256_VERIFIED', completed_at_utc=now(),
            archive_path=str(path), archive_bytes=reader.count, archive_sha256=reader.digest.hexdigest(),
            whole_receipt_sha256=hashlib.sha256(whole_raw).hexdigest(), stage_manifest_sha256=MANIFEST_SHA,
            recovered_trace_members=seen, recovered_trace_bytes=recovered, gzip_eof_crc_checked=True,
            method='rate-limited 164 gzip/tar streaming content recovery to hash; no native files materialized',
            maximum_compressed_read_bytes_per_second=RATE, native_stage_restore=False,
            empty_marker_and_numeric_metadata_status='SEPARATE_PRESERVATION_RECEIPT; native application pending',
            data_written_bytes=0, scientific_source_action='SOURCE_KEEP', source_released_bytes=0)))
    finally:
        os.close(lock)


if __name__ == '__main__':
    main()
