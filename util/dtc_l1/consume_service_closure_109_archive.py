#!/usr/bin/env python3
"""Independently verify the pinned 109 archive; extract to a fresh namespace."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import tarfile


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', required=True)
    a = ap.parse_args()
    root = Path(a.root)
    receipt = json.loads((root/'git-receipts/DURABLE_STORE_RECEIPT.json').read_text())
    index = json.loads((root/'git-receipts/RAW_PAYLOAD_INDEX.json').read_text())
    archive = root/'dtc_native_coverage_109_v1_20261016.tar.gz'
    assert archive.stat().st_size == receipt['archive_bytes']
    assert hashlib.file_digest(archive.open('rb'),'sha256').hexdigest() == receipt['archive_sha256']
    lookup = {r['relative_path']:r for r in index}
    assert len(lookup) == len(index) == 285
    output = root/'payload-verified-v2'
    output.mkdir(exist_ok=False)
    verified = set()
    index_verified = False
    with tarfile.open(archive) as t:
        for m in t:
            if m.isdir():
                continue
            assert m.isfile() and not m.name.startswith('/') and '..' not in PurePosixPath(m.name).parts
            data = t.extractfile(m).read()
            if m.name == 'PAYLOAD_FILES.json':
                assert not index_verified
                assert digest(data) == receipt['index_sha256'] and json.loads(data) == index
                index_verified = True
            else:
                assert m.name not in verified
                r = lookup[m.name]
                assert len(data) == r['bytes'] and digest(data) == r['sha256'], m.name
                verified.add(m.name)
            target = output/m.name
            target.parent.mkdir(parents=True,exist_ok=True)
            with target.open('xb') as f:
                f.write(data)
    assert verified == set(lookup) and index_verified
    result = dict(producer_commit='890fb0be7e681a60419c49ca0a7aa85731d8c164',
        status='PASS_CONSUMER_BYTE_IDENTITY_ONLY_NOT_SIMULATOR_ADMISSION',
        source='read-only SCP from gpu109; no producer restart',
        archive_sha256=receipt['archive_sha256'],archive_bytes=archive.stat().st_size,
        index_sha256=receipt['index_sha256'],files_verified=len(verified),
        payload_bytes=sum(r['bytes'] for r in index),payload_root=str(output),
        native_reruns=0,gpu_jobs_launched=0,
        preserved_initial_audit_failure=str(root/'AUDIT_A1_FAILURE_PRESERVED.json'))
    with (root/'CONSUMER_ARCHIVE_VERIFICATION_V2.json').open('x') as f:
        json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
