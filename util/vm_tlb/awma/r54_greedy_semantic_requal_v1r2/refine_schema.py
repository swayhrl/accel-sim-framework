#!/usr/bin/env python3
import csv,hashlib,json,shutil
from pathlib import Path
root=Path('/data/c16/awma/r54_greedy_semantic_requal_v1r2_20260927')
path=root/'R54_EXACT_STATE_SCHEMA.tsv'
initial=root/'raw/R54_EXACT_STATE_SCHEMA_PROBE_INITIAL.tsv'
initial.parent.mkdir(exist_ok=True)
if not initial.exists():shutil.copy2(path,initial)
with initial.open(newline='') as f:rows=list(csv.DictReader(f,delimiter='\t'))
for row in rows:
    field=row['field_path'];layer=row['layer_type']
    if layer=='linear_attention' and "['conv_kernel_size']" in field:
        row['state_class']='POSITION_OR_LENGTH'
        row['exact_continuation_required']='YES'
        row['recurrent_snapshot_inclusion']='METADATA'
    if layer=='linear_attention' and "['record_past']" in field:
        row['state_class']='INIT_FLAG'
        row['exact_continuation_required']='YES'
        row['recurrent_snapshot_inclusion']='METADATA'
    if layer=='full_attention' and "['is_initialized']" in field:
        row['recurrent_snapshot_inclusion']='NO_SEPARATE_PREFIX_KV'
with path.open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n')
    w.writeheader();w.writerows(rows)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
data={'initial_schema_sha256':sha(initial),'final_schema_sha256':sha(path),
 'refinement':'source-backed classification of GDN conv_kernel_size and record_past as exact continuation metadata; full-attention initialization stays with separately resident KV',
 'tensor_shapes_and_hashes_changed':False,
 'snapshot_implementation_changed':False,
 'formal_preregistration_schema_sha256':json.loads((root/'R54_PREREGISTRATION.json').read_text())['schema_sha256']}
assert data['initial_schema_sha256']==data['formal_preregistration_schema_sha256']
(root/'R54_STATE_SCHEMA_REFINEMENT.json').write_text(json.dumps(data,indent=2,sort_keys=True)+'\n')
print(json.dumps(data,indent=2))
