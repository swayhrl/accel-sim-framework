#!/usr/bin/env python3
"""Publish R101 raw/compact authority to node164 and verify every payload hash."""
from __future__ import annotations

import csv
import hashlib
import subprocess
from pathlib import Path

ROOT = Path('/data/c16/awma/r101_fixed_ns_intermediate_lifecycle_20260927')
PACK = Path('/home/huangrulin/workspace/worktrees/accel-sim-awma-r101-fixed-ns-v1/docs/vm_tlb/review_packs/AWMA_R101_FIXED_NS_INTERMEDIATE_LIFECYCLE_V1')
DEST = '/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/r101_fixed_ns_intermediate_lifecycle_20260927'
HOST = 'hrl174new'


def run(*args: str) -> None:
    print('RUN', ' '.join(args), flush=True)
    subprocess.run(args, check=True)


def sha256(path: Path) -> str:
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            value.update(block)
    return value.hexdigest()


def main() -> None:
    lines = []
    with (PACK / 'RAW_DATA_INDEX.tsv').open(newline='') as stream:
        for row in csv.DictReader(stream, delimiter='\t'):
            path = ROOT / row['node164_relative_path']
            assert path.is_file() and sha256(path) == row['sha256']
            lines.append(f"{row['sha256']}  {row['node164_relative_path']}\n")
    for path in sorted(PACK.iterdir()):
        if path.is_file():
            lines.append(f'{sha256(path)}  review_pack/{path.name}\n')
    manifest = ROOT / 'NODE164_SHA256SUMS'
    manifest.write_text(''.join(lines))
    run('ssh', HOST, 'mkdir', '-p', DEST)
    for directory in ('raw', 'source'):
        run('rsync', '-rt', '--partial', str(ROOT / directory) + '/', f'{HOST}:{DEST}/{directory}/')
    run('rsync', '-rt', str(PACK) + '/', f'{HOST}:{DEST}/review_pack/')
    run('rsync', '-t', str(manifest), f'{HOST}:{DEST}/NODE164_SHA256SUMS')
    remote_command = f'cd {DEST} && sha256sum -c NODE164_SHA256SUMS'
    result = subprocess.run(['ssh', HOST, remote_command], check=True, capture_output=True, text=True)
    checks = result.stdout.splitlines()
    assert len(checks) == len(lines)
    assert all(line.endswith(': OK') for line in checks)
    print(f'NODE164_VERIFIED={len(checks)} DEST={DEST}', flush=True)


if __name__ == '__main__':
    main()
