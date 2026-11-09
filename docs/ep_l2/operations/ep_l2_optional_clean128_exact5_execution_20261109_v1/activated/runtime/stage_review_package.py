#!/usr/bin/env python3
"""Copy only small exact5 review artifacts into the dedicated Git worktree."""
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path('/root/data/ep_l2_full_workload_performance_20261027_v1/research/optional_clean128_exact5_execution_20261109_v1')
REVIEW = ROOT / 'review'
DEST = REVIEW / 'docs/ep_l2/operations/ep_l2_optional_clean128_exact5_execution_20261109_v1/activated'
BRANCH = 'hrl/ep-l2-optional-clean128-exact5-20261109-v1'
assert subprocess.check_output(['git', '-C', str(REVIEW), 'branch', '--show-current'], text=True).strip() == BRANCH
assert not subprocess.check_output(['git', '-C', str(REVIEW), 'status', '--porcelain'], text=True).strip()
assert not DEST.exists()

files = []
files += [ROOT / 'control' / name for name in (
    'ACTIVATION_MANIFEST.json', 'ACTIVATION_MANIFEST.version1.json',
    'USER_AUTHORIZATION.json', 'USER_REQUEST.txt', 'NATIVE_ENTRY_ROUTE_EXACT5.json',
    'RESOURCE_BINDING_AMENDMENT_GEMM_V2.json',
    'RESOURCE_BINDING_AMENDMENT_STENCIL_V2.json', 'DISPATCH_CLAIMS.json')]
files += sorted((ROOT / 'control').glob('STAGED_ADMISSION_*.json'))
files += sorted((ROOT / 'documents').glob('*.json'))
files += [ROOT / 'documents/RESOURCE_HOLD_REPORT_20261109.md']
files += sorted((ROOT / 'runtime').glob('*.py'))
for family in ('gemm', 'stencil'):
    folder = ROOT / 'runtime' / ('host_' + family + '_bound_v2')
    files += sorted(folder.glob('*.py'))
    files += [folder / 'native_b1']
for case in sorted((ROOT / 'cases').glob('EP_PERF_CLEAN128_*')):
    files += sorted((case / 'control').glob('FROZEN_SPEC*.json'))
    files += sorted((case / 'control').glob('NATIVE_PRELAUNCH_QUALIFICATION*.json'))
    files += sorted((case / 'env').glob('config-4.config'))

index = []
for source in files:
    assert source.is_file() and not source.is_symlink(), source
    data = source.read_bytes()
    assert len(data) <= 500_000, source
    relative = source.relative_to(ROOT)
    target = DEST / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    assert target.read_bytes() == data
    index.append({'path': str(relative).replace('\\', '/'),
                  'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)})
(DEST / 'REVIEW_FILE_INDEX.json').write_text(
    json.dumps({'schema': 'EP_L2_EXACT5_ACTIVATED_REVIEW_INDEX_V1',
                'source_execution_root': str(ROOT), 'files': index},
               ensure_ascii=False, sort_keys=True, separators=(',', ':')) + '\n', encoding='utf-8')
print(json.dumps({'review_dir': str(DEST), 'files': len(index),
                  'total_bytes': sum(item['bytes'] for item in index)}))
