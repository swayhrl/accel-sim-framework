"""Verify one owner registry transaction from copied before/after bytes."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).parent
read = lambda name: json.loads((root / name).read_bytes())
sha = lambda name: hashlib.sha256((root / name).read_bytes()).hexdigest()
before = read('NATIVE_SCIENCE_REGISTRY_READONLY_SNAPSHOT.json')
after = read('NATIVE_SCIENCE_REGISTRY_AFTER_READONLY.json')
epoch_before = read('CURRENT_SCIENCE_EPOCH_READONLY_SNAPSHOT.json')
epoch_after = read('CURRENT_SCIENCE_EPOCH_AFTER_READONLY.json')
intent = read('DTC_STAGE48_CLOSEOUT_INTENT.json')
done = read('DTC_STAGE48_CLOSEOUT_COMMITTED.json')
request = 'DTC_STAGE_IIA_REMAINING48_CH_MATCH_20261104_V1'
old_rows = before['registered_future_requests']
new_rows = after['registered_future_requests']
assert set(old_rows) == set(new_rows)
assert {k: v for k, v in old_rows.items() if k != request} == {k: v for k, v in new_rows.items() if k != request}
assert {k: v for k, v in before.items() if k != 'registered_future_requests'} == {k: v for k, v in after.items() if k != 'registered_future_requests'}
old, new = old_rows[request], new_rows[request]
assert {k: v for k, v in old.items() if k != 'reserved_write_bytes'} == {k: v for k, v in new.items() if k not in ('reserved_write_bytes', 'owner_native_write_closeout')}
assert old['reserved_write_bytes'] == 9395240960 and new['reserved_write_bytes'] == 268435456
assert old['reserved_write_bytes'] - new['reserved_write_bytes'] == done['released_commitment_bytes'] == 9126805504
assert done['before_registry_sha256'] == sha('NATIVE_SCIENCE_REGISTRY_READONLY_SNAPSHOT.json')
assert done['after_registry_sha256'] == sha('NATIVE_SCIENCE_REGISTRY_AFTER_READONLY.json')
assert done['before_epoch_sha256'] == sha('CURRENT_SCIENCE_EPOCH_READONLY_SNAPSHOT.json')
assert done['after_epoch_sha256'] == sha('CURRENT_SCIENCE_EPOCH_AFTER_READONLY.json')
assert done['intent_sha256'] == sha('DTC_STAGE48_CLOSEOUT_INTENT.json')
assert epoch_before['native_registry_sha256'] == done['before_registry_sha256']
assert epoch_after['native_registry_sha256'] == done['after_registry_sha256']
assert {k: v for k, v in epoch_before.items() if k not in ('native_registry_sha256', 'request_revision')} == {k: v for k, v in epoch_after.items() if k not in ('native_registry_sha256', 'request_revision')}
assert len(intent['details']) == 1 and len(intent['details'][0]['evidence']['cohorts']) == 48
assert intent['details'][0]['evidence']['metadata_retained_bytes'] == 268435456
assert done['source_release_bytes'] == done['model_starts'] == 0
proof = {
    'status': 'PASS', 'changed_requests': [request], 'unchanged_request_count': len(old_rows) - 1,
    'other_registry_fields_identical': True, 'epoch_unrelated_fields_identical': True,
    'before_registry_sha256': done['before_registry_sha256'],
    'after_registry_sha256': done['after_registry_sha256'],
    'before_epoch_sha256': done['before_epoch_sha256'],
    'after_epoch_sha256': done['after_epoch_sha256'],
    'formal_commitment_released_bytes': done['released_commitment_bytes'],
    'physical_bytes_released': 0, 'models_started': 0,
}
(root / 'STAGE48_TRANSACTION_READBACK.json').write_text(json.dumps(proof, indent=2) + '\n')
print(json.dumps(proof))
