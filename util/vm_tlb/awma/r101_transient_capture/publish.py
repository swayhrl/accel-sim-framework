#!/usr/bin/env python3
"""Storage-only node164 publication with two-stage full SHA verification."""
from __future__ import annotations

import csv
import hashlib
import subprocess
import sys
from pathlib import Path

ROOT = Path('/data/c16/awma/r101_transient_l2_sim_capture_20260927')
WORKTREE = Path('/home/huangrulin/workspace/worktrees/accel-sim-awma-r101-transient-l2-sim-capture-109-v1')
PACK = WORKTREE / 'docs/vm_tlb/review_packs/AWMA_R101_TRANSIENT_L2_SIM_CAPTURE_109_V1'
HOST = 'hrl174new'  # existing SSHFS storage gateway to node164; no GPU/simulator invocation
DEST = '/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/r101_transient_l2_sim_capture_20260927'


def run(*args: str) -> None:
    print('RUN', ' '.join(args), flush=True)
    subprocess.run(args, check=True)


def sha(path: Path) -> str:
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            value.update(block)
    return value.hexdigest()


def verify_remote(manifest: str, expected: int) -> None:
    result = subprocess.run(['ssh', HOST, f'cd {DEST} && sha256sum -c {manifest}'],
                            check=True, capture_output=True, text=True)
    lines = result.stdout.splitlines()
    assert len(lines) == expected and all(line.endswith(': OK') for line in lines)
    print(f'{manifest}_VERIFIED={expected}', flush=True)


def main() -> None:
    package = WORKTREE / 'util/vm_tlb/awma/r101_transient_capture/package.py'
    run(sys.executable, str(package))
    rows = []
    with (PACK / 'RAW_DATA_INDEX.tsv').open(newline='') as stream:
        rows = list(csv.DictReader(stream, delimiter='\t'))
    assert rows
    raw_lines = []
    for row in rows:
        path = ROOT / row['node164_relative_path']
        assert path.is_file() and sha(path) == row['sha256']
        raw_lines.append(f"{row['sha256']}  {row['node164_relative_path']}\n")
    raw_manifest = ROOT / 'RAW_SHA256SUMS'
    raw_manifest.write_text(''.join(raw_lines))
    run('ssh', HOST, 'mkdir', '-p', DEST)
    for directory in ('raw', 'bin', 'build', 'cache', 'logs'):
        run('rsync', '-rt', '--partial', str(ROOT / directory) + '/',
            f'{HOST}:{DEST}/{directory}/')
    run('rsync', '-t', str(raw_manifest), f'{HOST}:{DEST}/RAW_SHA256SUMS')
    verify_remote('RAW_SHA256SUMS', len(rows))
    (ROOT / 'TRANSFER_RECEIPT.md').write_text(
        '# Transfer receipt\n\n'
        f'Node164 durable root: `{DEST}`. '
        f'{len(rows)} raw/build/cache/log files were copied via the already-running '
        '`hrl174new` SSHFS storage gateway and independently re-read on node164 with SHA256: '
        '**all PASS**. No 174 GPU or simulator command was invoked. '
        'Compact review-pack files are included in the final node164 SHA manifest.\n'
    )
    run(sys.executable, str(package))
    run('rsync', '-rt', str(PACK) + '/', f'{HOST}:{DEST}/review_pack/')
    lines = raw_lines + [f'{sha(raw_manifest)}  RAW_SHA256SUMS\n']
    for path in sorted(PACK.iterdir()):
        if path.is_file():
            lines.append(f'{sha(path)}  review_pack/{path.name}\n')
    full_manifest = ROOT / 'NODE164_SHA256SUMS'
    full_manifest.write_text(''.join(lines))
    run('rsync', '-t', str(full_manifest), f'{HOST}:{DEST}/NODE164_SHA256SUMS')
    verify_remote('NODE164_SHA256SUMS', len(lines))
    print(f'NODE164_PUBLICATION_COMPLETE DEST={DEST} RAW={len(rows)} ALL={len(lines)}', flush=True)


if __name__ == '__main__':
    main()
