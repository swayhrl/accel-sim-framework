#!/usr/bin/env python3
"""Compact R101R1 review pack and raw/build/cache/log hash index."""
from __future__ import annotations

import csv
import hashlib
import shutil
from pathlib import Path

ROOT = Path('/data/c16/awma/r101_l2_lifetime_control_v1r1_20260927')
PACK = Path('/home/huangrulin/workspace/worktrees/accel-sim-awma-r101-l2-lifetime-control-v1r1/docs/vm_tlb/review_packs/AWMA_R101_L2_LIFETIME_CONTROL_V1R1')


def sha(path: Path) -> str:
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            value.update(block)
    return value.hexdigest()


def main() -> None:
    PACK.mkdir(parents=True, exist_ok=True)
    for path in sorted(ROOT.iterdir()):
        if path.is_file() and path.suffix in {'.json', '.tsv', '.md'}:
            shutil.copy2(path, PACK / path.name)
    entries = []
    for directory in ('raw', 'build', 'cache', 'logs'):
        for path in sorted((ROOT / directory).rglob('*')):
            if path.is_file():
                entries.append({
                    'node164_relative_path': path.relative_to(ROOT).as_posix(),
                    'size_bytes': path.stat().st_size,
                    'sha256': sha(path),
                    'kind': directory,
                })
    with (PACK / 'RAW_DATA_INDEX.tsv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(entries[0]), delimiter='\t', lineterminator='\n')
        writer.writeheader()
        writer.writerows(entries)
    with (PACK / 'SHA256SUMS').open('w') as stream:
        for path in sorted(PACK.iterdir()):
            if path.is_file() and path.name != 'SHA256SUMS':
                stream.write(f'{sha(path)}  {path.name}\n')
    print(f'PACK={PACK} COMPACT_FILES={len(list(PACK.iterdir()))} INDEXED_FILES={len(entries)}')


if __name__ == '__main__':
    main()
