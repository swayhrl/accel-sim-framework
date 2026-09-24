#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
from pathlib import Path

REPO = Path('/root/workspace/accel-sim-framework-awma-bottleneck-observatory-v1')
RUNTIME = Path('/root/awma_bottleneck_observatory_v1_runtime')
PACK = REPO / 'docs/vm_tlb/review_packs/AWMA_BOTTLENECK_OBSERVATORY_V1'


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    rows = []
    for path in sorted((RUNTIME / 'runs').glob('*/*/L*/*')):
        if not path.is_file() or path.name == 'gpgpu_inst_stats.txt':
            continue
        relative = path.relative_to(RUNTIME / 'runs')
        target, translation, run_name = relative.parts[:3]
        level, tag = run_name.split('_', 1)
        rows.append({
            'category': 'FORMAL_RUN', 'target': target,
            'translation': translation, 'level': level, 'tag': tag,
            'artifact': path.name, 'path': str(path), 'sha256': sha256(path),
            'bytes': path.stat().st_size,
            'status': 'FORMAL' if 'overhead_' in tag or
                'retrospective_locked' in tag or 'directed_locked' in tag
                else 'DIAGNOSTIC',
        })
    source_files = (
        RUNTIME / 'bin/unified_accel-sim.out', RUNTIME / 'FINAL_BINARY.sha256',
        RUNTIME / 'observatory_core_build_hotpath_final.log',
        RUNTIME / 'observatory_accelsim_build_hotpath_final.log',
        RUNTIME / 'src/gpgpu-sim/src/gpgpu-sim/bottleneck_observatory.h',
        RUNTIME / 'src/gpgpu-sim/src/gpgpu-sim/bottleneck_observatory.cc',
        RUNTIME / 'src/gpgpu-sim/src/gpgpu-sim/shader.cc',
        RUNTIME / 'src/gpgpu-sim/src/gpgpu-sim/gpu-sim.cc',
        RUNTIME / 'src/gpgpu-sim/src/gpgpu-sim/l2cache.cc',
        RUNTIME / 'src/gpgpu-sim/src/gpgpu-sim/dram.cc')
    for path in source_files:
        rows.append({
            'category': 'BUILD_OR_SOURCE', 'target': '', 'translation': '',
            'level': '', 'tag': '', 'artifact': path.name, 'path': str(path),
            'sha256': sha256(path), 'bytes': path.stat().st_size,
            'status': 'FORMAL'})
    PACK.mkdir(parents=True, exist_ok=True)
    fields = ('category', 'target', 'translation', 'level', 'tag', 'artifact',
              'path', 'sha256', 'bytes', 'status')
    with (PACK / 'RAW_DATA_INDEX.tsv').open('w', newline='') as out:
        writer = csv.DictWriter(out, fieldnames=fields, delimiter='\t',
                                lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)
    checksum_path = PACK / 'SHA256SUMS'
    lines = []
    for path in sorted(PACK.iterdir()):
        if path.is_file() and path != checksum_path:
            lines.append(f'{sha256(path)}  {path.name}')
    checksum_path.write_text('\n'.join(lines) + '\n')
    print(f'indexed={len(rows)} pack_hashes={len(lines)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
