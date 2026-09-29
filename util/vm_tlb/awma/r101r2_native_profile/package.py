#!/usr/bin/env python3
"""Build compact R101R2 review pack and raw/JIT hash index."""
from __future__ import annotations

import csv
import hashlib
import shutil
from pathlib import Path

ROOT = Path('/data/c16/awma/r101r2_s128_native_profile_20260929')
PACK = Path('/home/huangrulin/workspace/worktrees/accel-sim-awma-r101r2-s128-native-profile-109-v1/docs/vm_tlb/review_packs/AWMA_R101R2_S128_NATIVE_EXECUTION_PROFILE_109_V1')


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
    rows = []
    for directory in ('raw', 'cache', 'logs'):
        for path in sorted((ROOT / directory).rglob('*')):
            if path.is_file():
                rows.append({'node164_relative_path': path.relative_to(ROOT).as_posix(),
                             'size_bytes': path.stat().st_size, 'sha256': sha(path),
                             'kind': directory})
    with (PACK / 'RAW_DATA_INDEX.tsv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), delimiter='\t', lineterminator='\n')
        writer.writeheader(); writer.writerows(rows)
    with (PACK / 'SHA256SUMS').open('w') as stream:
        for path in sorted(PACK.iterdir()):
            if path.is_file() and path.name != 'SHA256SUMS':
                stream.write(f'{sha(path)}  {path.name}\n')
    print(f'PACK={PACK} COMPACT_FILES={len(list(PACK.iterdir()))} INDEXED_RAW_FILES={len(rows)}')


if __name__ == '__main__':
    main()
