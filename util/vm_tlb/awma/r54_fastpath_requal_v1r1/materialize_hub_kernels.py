#!/usr/bin/env python3
import csv
import hashlib
import json
import os
import sys
import traceback
from pathlib import Path

ROOT = Path('/data/c16/awma/r54_fastpath_requal_v1r1_20260927')
OUT = ROOT / 'provenance'
OUT.mkdir(parents=True, exist_ok=True)

from transformers.integrations.hub_kernels import get_kernel_mapping_transformers
from kernels import Mode
import kernels

ops = [
    'causal_conv1d_fn',
    'causal_conv1d_update',
    'chunk_gated_delta_rule',
    'fused_recurrent_gated_delta_rule',
]

rows = []
mapping = get_kernel_mapping_transformers()
for op in ops:
    repo = mapping[op]['cuda'][Mode.INFERENCE]
    row = {
        'operation': op,
        'repo_id': repo._repo_id,
        'mapped_layer_name': repo.layer_name,
        'requested_version': repo._version,
        'requested_revision': repo._revision or '',
        'resolved_revision': '',
        'load_status': 'NOT_ATTEMPTED',
        'loaded_object': '',
        'loaded_module': '',
        'loaded_source_file': '',
        'error': '',
    }
    try:
        row['resolved_revision'] = repo._resolve_revision()
        obj = repo.load()
        row['load_status'] = 'MATERIALIZED'
        row['loaded_object'] = getattr(obj, '__qualname__', repr(obj))
        row['loaded_module'] = getattr(obj, '__module__', '')
        module = sys.modules.get(row['loaded_module'])
        row['loaded_source_file'] = getattr(module, '__file__', '') if module else ''
    except Exception as exc:
        row['load_status'] = 'FAILED'
        row['error'] = repr(exc)
        traceback.print_exc()
    rows.append(row)

fields = list(rows[0])
with (OUT / 'HUB_KERNEL_PROVENANCE_PREEXEC.tsv').open('w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=fields, delimiter='\t', lineterminator='\n')
    w.writeheader()
    w.writerows(rows)

hash_rows = []
for base in [Path(os.environ['HF_HOME']), Path(kernels.__file__).resolve().parent]:
    for p in sorted(base.rglob('*')):
        if not p.is_file():
            continue
        h = hashlib.sha256()
        with p.open('rb') as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b''):
                h.update(chunk)
        hash_rows.append({'base': str(base), 'path': str(p), 'size_bytes': p.stat().st_size, 'sha256': h.hexdigest()})
with (OUT / 'HUB_KERNEL_MATERIALIZED_FILES.tsv').open('w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['base','path','size_bytes','sha256'], delimiter='\t', lineterminator='\n')
    w.writeheader()
    w.writerows(hash_rows)

print(json.dumps({'rows': rows, 'hashed_files': len(hash_rows)}, indent=2))
if any(r['load_status'] != 'MATERIALIZED' for r in rows):
    raise SystemExit(2)
