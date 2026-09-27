#!/usr/bin/env python3
"""Create the compact R101 review pack and indexed raw payload manifest."""
from __future__ import annotations

import csv
import hashlib
import shutil
from pathlib import Path

ROOT = Path('/data/c16/awma/r101_fixed_ns_intermediate_lifecycle_20260927')
PACK = Path('/home/huangrulin/workspace/worktrees/accel-sim-awma-r101-fixed-ns-v1/docs/vm_tlb/review_packs/AWMA_R101_FIXED_NS_INTERMEDIATE_LIFECYCLE_V1')


def digest(path: Path) -> str:
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
    aliases = {
        'R101_GRADIENT_MICROSTATE_RECEIPT.json': 'R101_GRADIENT_MICROSTATE_RECEIPT_DISCOVERY.json',
        'NUMERICAL_QUALIFICATION.tsv': 'NUMERICAL_QUALIFICATION_DISCOVERY.tsv',
    }
    for destination, source in aliases.items():
        shutil.copy2(ROOT / source, PACK / destination)
    # Preserve the TSV schema while making not-applicable pair columns explicit.
    for name in (
        'NUMERICAL_QUALIFICATION.tsv',
        'NUMERICAL_QUALIFICATION_DISCOVERY.tsv',
        'NUMERICAL_QUALIFICATION_HOLDOUT.tsv',
    ):
        path = PACK / name
        path.write_text(path.read_text().replace('\t\t\n', '\tNOT_APPLICABLE\tNOT_APPLICABLE\n'))
    indexed = []
    for directory in ('raw', 'source'):
        for path in sorted((ROOT / directory).rglob('*')):
            if path.is_file():
                indexed.append({
                    'node164_relative_path': path.relative_to(ROOT).as_posix(),
                    'size_bytes': path.stat().st_size,
                    'sha256': digest(path),
                    'kind': directory,
                })
    with (PACK / 'RAW_DATA_INDEX.tsv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(indexed[0]), delimiter='\t', lineterminator='\n')
        writer.writeheader()
        writer.writerows(indexed)
    with (PACK / 'SHA256SUMS').open('w') as stream:
        for path in sorted(PACK.iterdir()):
            if path.is_file() and path.name != 'SHA256SUMS':
                stream.write(f'{digest(path)}  {path.name}\n')
    print(f'pack={PACK} compact_files={len(list(PACK.iterdir()))} indexed_raw_source_files={len(indexed)}')


if __name__ == '__main__':
    main()
