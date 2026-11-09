"""Bounded read-only old pool arithmetic for this Goal's archive HOLD."""
import datetime
import importlib.util
import json
import os
from pathlib import Path

import mechanism_outbox as outbox

old=outbox.primitive()
path=old.ROOT/'tools/sweep_native.py'
spec=importlib.util.spec_from_file_location('r0_pool_resources_only',path)
native=importlib.util.module_from_spec(spec)
spec.loader.exec_module(native)
pool=native.resources({'cohort':'COPY_ONLY'},False)
reservation=2*1024*1024
free=os.statvfs(outbox.ROOT).f_bavail*os.statvfs(outbox.ROOT).f_frsize
base=5*1024**3+reservation+1024**3+pool['other_outstanding_write_reservations_bytes']
required=max(pool['required_free_bytes'],base)
receipt=dict(schema='DTC_SHORT_COLLECT_R0_ARCHIVE_GATE_ARITHMETIC_V1',
             utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
             status='HOLD' if not free>required else 'PASS',
             native_free_bytes=free,old_pool_required_free_bytes=pool['required_free_bytes'],
             other_outstanding_write_reservations_bytes=pool['other_outstanding_write_reservations_bytes'],
             reservation_bytes=reservation,local_safety_floor_bytes=5*1024**3,
             metadata_and_spool_reserve_bytes=1024**3,
             explicit_formula_bytes=base,applied_required_free_bytes=required,
             strict_greater_than_required=free>required,
             peer_identity_details_included=False,model_starts=0,archive_writes=0)
output=outbox.ROOT/'evidence/R0_TRUE164_GATE_ARITHMETIC.json'
with output.open('x') as stream:
    json.dump(receipt,stream,indent=2,sort_keys=True)
    stream.write('\n');stream.flush();os.fsync(stream.fileno())
print(json.dumps(receipt,indent=2,sort_keys=True))
