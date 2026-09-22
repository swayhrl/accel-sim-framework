#!/usr/bin/env python3
"""Create a hash-bound transfer manifest for V40 node164 admission."""
import hashlib
import json
from pathlib import Path

ROOT = Path('/data/c16/olmoe_v40/typed_sweep/formal_admission')
SHARDS = ROOT / 'FORMAL_243_SHARDS.jsonl'


def digest(path):
    value = hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            value.update(block)
    return value.hexdigest()


def main():
    artifacts = []
    for name in ('FORMAL_243_SUMMARY.json', 'FORMAL_243_ANALYSIS.json', 'FORMAL_243_SHARDS.jsonl', 'FORMAL_243_PER_SHARD_ANALYSIS.jsonl'):
        path = ROOT / name
        artifacts.append({'kind': 'formal_summary', 'path': str(path), 'bytes': path.stat().st_size, 'sha256': digest(path)})
    for shard in (json.loads(line) for line in SHARDS.read_text().splitlines() if line):
        attempt = Path(shard['attempt_root'])
        for name in ('trace.bin', 'ADDRESS_CONTEXT.json', 'SUPERVISOR_RECEIPT.json', 'result.json', 'stdout.log', 'output.sha256', 'C16WARP1_FORMAL_VALIDATOR_RECEIPT.json'):
            path = attempt / name
            if not path.is_file(): raise SystemExit(f'missing required artifact: {path}')
            artifacts.append({'kind': 'shard_artifact', 'static_index': shard['static_index'], 'classification': shard['classification'],
                              'path': str(path), 'bytes': path.stat().st_size, 'sha256': digest(path)})
    manifest = {'schema_version': 1, 'status': 'LOCAL_CLOSE_READY_FOR_NODE164_ADMISSION',
                'formal_admission_concurrency': 1, 'evidence_condition': 'actual JIT variant A',
                'artifact_count': len(artifacts), 'artifacts': artifacts,
                'transfer_warning': 'No rsync exit status is admission; require destination hash verification, catalog receipt, and positive ACK.'}
    (ROOT / 'NODE164_TRANSFER_MANIFEST.json').write_text(json.dumps(manifest, indent=2, sort_keys=True) + '\n')
    with (ROOT / 'SHA256SUMS').open('w') as handle:
        for item in sorted(artifacts, key=lambda value: value['path']): handle.write(f"{item['sha256']}  {item['path']}\n")
    print(json.dumps({'artifact_count': len(artifacts), 'manifest_sha256': digest(ROOT / 'NODE164_TRANSFER_MANIFEST.json')}))


if __name__ == '__main__':
    main()
