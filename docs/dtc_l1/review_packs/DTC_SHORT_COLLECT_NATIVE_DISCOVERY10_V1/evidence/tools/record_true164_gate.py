"""Read-only production archive gate readback. No archive or science writes."""
import datetime
import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path

import mechanism_outbox as outbox

root=outbox.ROOT
mount=json.loads(subprocess.check_output(['findmnt','-J','-T','/root/share/mnt164'],text=True))['filesystems'][0]
local=shutil.disk_usage(root)
remote=shutil.disk_usage('/root/share/mnt164')
try:
    decision=outbox.gate(2*1024*1024)
    status='PASS'
    reason=None
except Exception as exc:
    status='HOLD'
    reason=f'{type(exc).__name__}: {exc}'
    decision=None
receipt=dict(schema='DTC_SHORT_COLLECT_R0_TRUE164_ADMISSION_READBACK_V1',
             utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
             status=status,reason=reason,requested_archive_reservation_bytes=2*1024*1024,
             host=os.uname().nodename,native_device=root.stat().st_dev,
             true164_mount=dict(fstype=mount['fstype'],source=mount['source']),
             native_free_bytes=local.free,true164_free_bytes=remote.free,
             production_gate_decision=decision,
             mechanism_outbox_sha256=hashlib.sha256(Path(outbox.__file__).read_bytes()).hexdigest(),
             new_science_requests=0,new_science_uuids=0,new_model_starts=0,
             true164_archive_writes_from_this_probe=0,
             typed_restore_from_this_probe=0)
path=root/'evidence/R0_TRUE164_GATE_READBACK.json'
with path.open('x') as stream:
    json.dump(receipt,stream,indent=2,sort_keys=True)
    stream.write('\n')
    stream.flush();os.fsync(stream.fileno())
print(json.dumps(receipt,indent=2,sort_keys=True))
