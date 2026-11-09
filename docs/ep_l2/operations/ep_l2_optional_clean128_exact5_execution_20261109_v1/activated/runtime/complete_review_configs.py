#!/usr/bin/env python3
"""Complete the already published review package's exact config overlays and index."""
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path('/root/data/ep_l2_full_workload_performance_20261027_v1/research/optional_clean128_exact5_execution_20261109_v1')
DEST = ROOT / 'review/docs/ep_l2/operations/ep_l2_optional_clean128_exact5_execution_20261109_v1/activated'
for case in sorted((ROOT / 'cases').glob('EP_PERF_CLEAN128_STENCIL_*')):
    for source in sorted((case / 'env').glob('config-*.config')):
        target = DEST / source.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
for name in ('stage_review_package.py', 'complete_review_configs.py'):
    source = ROOT / 'runtime' / name
    shutil.copyfile(source, DEST / source.relative_to(ROOT))

index = []
for target in sorted(DEST.rglob('*')):
    if not target.is_file() or target.name == 'REVIEW_FILE_INDEX.json':
        continue
    relative = target.relative_to(DEST)
    source = ROOT / relative
    data = target.read_bytes()
    assert source.is_file() and source.read_bytes() == data, relative
    index.append({'path': str(relative), 'sha256': hashlib.sha256(data).hexdigest(),
                  'bytes': len(data)})
(DEST / 'REVIEW_FILE_INDEX.json').write_text(json.dumps({
    'schema': 'EP_L2_EXACT5_ACTIVATED_REVIEW_INDEX_V1',
    'source_execution_root': str(ROOT), 'files': index,
}, ensure_ascii=False, sort_keys=True, separators=(',', ':')) + '\n', encoding='utf-8')
print(json.dumps({'files': len(index), 'total_bytes': sum(x['bytes'] for x in index)}))
