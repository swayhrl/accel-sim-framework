#!/usr/bin/env python3
"""Storage-only node164 publication and per-file SHA reread."""
from __future__ import annotations

import csv
import hashlib
import subprocess
import sys
from pathlib import Path

ROOT = Path('/data/c16/awma/r101r2_s128_native_profile_20260929')
WORKTREE = Path('/home/huangrulin/workspace/worktrees/accel-sim-awma-r101r2-s128-native-profile-109-v1')
PACK = WORKTREE / 'docs/vm_tlb/review_packs/AWMA_R101R2_S128_NATIVE_EXECUTION_PROFILE_109_V1'
HOST = 'hrl174new'  # existing node164 SSHFS storage gateway, not a GPU/simulator run
DEST = '/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/r101r2_s128_native_profile_20260929'


def run(*args: str) -> None:
    print('RUN', ' '.join(args), flush=True)
    subprocess.run(args, check=True)


def sha(path: Path) -> str:
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            value.update(block)
    return value.hexdigest()


def verify(name: str, expected: int) -> None:
    check = subprocess.run(['ssh', HOST, f'cd {DEST} && sha256sum -c {name}'],
                           check=True, capture_output=True, text=True)
    rows = check.stdout.splitlines()
    assert len(rows) == expected and all(row.endswith(': OK') for row in rows)
    print(f'{name}_VERIFIED={expected}', flush=True)


def main() -> None:
    package = WORKTREE / 'util/vm_tlb/awma/r101r2_native_profile/package.py'
    run(sys.executable, str(package))
    with (PACK / 'RAW_DATA_INDEX.tsv').open(newline='') as stream:
        index = list(csv.DictReader(stream, delimiter='\t'))
    assert index
    raw_lines = []
    for row in index:
        path = ROOT / row['node164_relative_path']
        assert path.is_file() and sha(path) == row['sha256']
        raw_lines.append(f"{row['sha256']}  {row['node164_relative_path']}\n")
    raw_manifest = ROOT / 'RAW_SHA256SUMS'
    raw_manifest.write_text(''.join(raw_lines))
    run('ssh', HOST, 'mkdir', '-p', DEST)
    for directory in ('raw', 'cache', 'logs'):
        run('rsync', '-rt', '--partial', str(ROOT / directory) + '/',
            f'{HOST}:{DEST}/{directory}/')
    run('rsync', '-t', str(raw_manifest), f'{HOST}:{DEST}/RAW_SHA256SUMS')
    verify('RAW_SHA256SUMS', len(index))
    (ROOT / 'TRANSFER_RECEIPT.md').write_text(
        '# Transfer receipt\n\n'
        f'Node164 durable root: `{DEST}`. '
        f'All {len(index)} raw/JIT/log members were re-read from node164 and SHA256 verified: '
        '**PASS**. The storage gateway was used only for files; no 174 GPU or simulator execution. '
        'The final manifest also covers every compact review-pack file.\n'
    )
    run(sys.executable, str(package))
    run('rsync', '-rt', str(PACK) + '/', f'{HOST}:{DEST}/review_pack/')
    lines = raw_lines + [f'{sha(raw_manifest)}  RAW_SHA256SUMS\n']
    for path in sorted(PACK.iterdir()):
        if path.is_file():
            lines.append(f'{sha(path)}  review_pack/{path.name}\n')
    full = ROOT / 'NODE164_SHA256SUMS'
    full.write_text(''.join(lines))
    run('rsync', '-t', str(full), f'{HOST}:{DEST}/NODE164_SHA256SUMS')
    verify('NODE164_SHA256SUMS', len(lines))
    print(f'NODE164_PUBLICATION_COMPLETE RAW={len(index)} ALL={len(lines)} DEST={DEST}', flush=True)


if __name__ == '__main__':
    main()
