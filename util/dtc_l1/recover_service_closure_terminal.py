#!/usr/bin/env python3
"""Recover a missing wrapper receipt from original time(1) evidence, never rerun."""
import argparse
from datetime import datetime, timezone
import fcntl
import hashlib
import json
from pathlib import Path
import re
import time
from collect_service_closure_attempts import collect, sha


def write(path, obj):
    with path.open('x') as f:
        json.dump(obj,f,indent=2);f.write('\n')


def recover(run):
    if (run/'RUN_TERMINAL.json').exists():
        return True
    start = json.loads((run/'RUN_START.json').read_text())
    spec = start['spec']
    pid = json.loads((run/'PID.json').read_text())
    for p in Path('/proc').glob('[0-9]*/cmdline'):
        try:
            argv = p.read_bytes().split(b'\0')
            exe = argv[0].decode(errors='replace')
            if (exe.endswith('/accel-sim.out') or exe=='/usr/bin/time') and str(run).encode() in b' '.join(argv):
                return False
            if p.parent.name==str(pid['runner_pid']) and b'service_closure_attempt.py' in b' '.join(argv):
                return False
        except OSError:
            pass
    resource = (run/'resource.time').read_text()
    status = re.findall(r'^\s*Exit status:\s*(\d+)\s*$',resource,re.M)
    if not status:
        return False  # No observed exit code means no recovery/acceptance.
    assert len(status)==1
    lock = (run.parent/'locks'/(start['identity']+'.lock')).open('a')
    fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    assert not (run/'RUN_TERMINAL.json').exists()
    assert json.loads((run/'SPEC.json').read_text())==spec
    assert hashlib.sha256(json.dumps(spec,sort_keys=True).encode()).hexdigest()==start['identity']
    assert sha(run/'immutable_runner.py')==start['runner_sha256']
    binary = run.parent/'binaries'/spec['runtime_sha256']/'accel-sim.out'
    assert sha(binary)==spec['runtime_sha256']
    for i,c in enumerate(spec['configs']):
        assert sha(run/f'config-{i}.config')==c['sha256']
    assert sha(Path(spec['trace_list']))==spec['trace_list_sha256']
    for m in spec['members']:
        assert Path(m['path']).stat().st_size==m['bytes'] and sha(Path(m['path']))==m['sha256']
    assert str(binary) in resource
    utc=datetime.now(timezone.utc).isoformat()
    audit=dict(attempt_uuid=start['attempt_uuid'],recovered_utc=utc,
        reason='Original wrapper absent; independently timed simulator finished without a wrapper receipt.',
        observed_time_exit_status=int(status[0]),original_pid_receipt=pid,
        no_live_owned_timed_process=True,no_reexecution=True,
        stdout_sha256=sha(run/'simulator.stdout'),stderr_sha256=sha(run/'simulator.stderr'),
        resource_sha256=sha(run/'resource.time'),start_sha256=sha(run/'RUN_START.json'),
        terminal_time_basis='Recovery observation UTC, not an invented exact simulator exit timestamp.')
    write(run/'TERMINAL_RECOVERY_V1.json',audit)
    write(run/'RUN_TERMINAL.json',dict(attempt_uuid=start['attempt_uuid'],
        exit_status=int(status[0]),terminal_utc=utc,recovered=True,
        recovery_receipt='TERMINAL_RECOVERY_V1.json',
        stdout_sha256=audit['stdout_sha256'],stderr_sha256=audit['stderr_sha256'],
        resource_sha256=audit['resource_sha256']))
    write(run/'RECOVERED_VALIDATION_V1.json',collect(run))
    print(json.dumps(dict(run=str(run),status='RECEIPT_RECOVERED_NOT_RERUN')),flush=True)
    return True


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--run',action='append',required=True)
    ap.add_argument('--watch',action='store_true')
    a=ap.parse_args()
    while True:
        done=[recover(Path(p)) for p in a.run]
        if all(done) or not a.watch:
            return
        time.sleep(10)


if __name__=='__main__':
    main()
