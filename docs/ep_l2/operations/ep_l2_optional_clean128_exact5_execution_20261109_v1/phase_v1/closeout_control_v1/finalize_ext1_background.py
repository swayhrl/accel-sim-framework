#!/usr/bin/env python3
"""Wait for the sole EXT1 accept monitor, then publish one final review commit."""
import datetime
import json
import os
import subprocess
import time
from pathlib import Path

R = Path('/root/data/ep_l2_full_workload_performance_20261027_v1/research/optional_clean128_exact5_execution_20261109_v1')
N = Path('/root/data/ep_l2_dtc_l1_native_v2')
CASE = 'EP_PERF_CLEAN128_STENCIL_WV_EXT1_20261110_V1'
REQ = 'EP_L2_OPTIONAL_CLEAN128_STENCIL_EXT1_20261110_V1'
CONTROL = R / 'control'
STATUS = CONTROL / 'EXT1_FINAL_PUBLICATION_STATUS.json'
LOG = CONTROL / 'EXT1_FINAL_PUBLICATION.log'
MONITOR = CONTROL / 'EXT1_BACKGROUND_MONITOR_STATUS.json'
SCRIPT = R / 'runtime/publish_ext1_final.py'
MONITOR_PID = 1603132


def read(path):
    return json.loads(path.read_bytes())


def write(status, **details):
    value = {'schema': 'EP_L2_EXT1_FINAL_PUBLICATION_WATCH_V1',
             'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
             'status': status, 'request': REQ, 'cohort': CASE,
             'automatic_retry': False, **details}
    tmp = STATUS.with_name('.' + STATUS.name + '.tmp')
    with tmp.open('w') as stream:
        json.dump(value, stream, sort_keys=True)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(tmp, STATUS)


def live(pid):
    try:
        state = (Path('/proc') / str(pid) / 'stat').read_text().rsplit(')', 1)[1].split()[0]
        return state not in ('Z', 'X')
    except OSError:
        return False


def main():
    assert not LOG.exists(), 'publication already attempted; stop'
    deadline = time.monotonic() + 52 * 3600
    while time.monotonic() < deadline:
        monitor = read(MONITOR)
        state = monitor['status']
        if state == 'ACCEPT_ARCHIVE_COMMAND_FINISHED':
            assert monitor['returncode'] == 0 and monitor['registry_state'] == 'CLOSED_ACCEPTED'
            registry = read(N / 'control/science_authority/NATIVE_SCIENCE_REGISTRY.json')
            request = registry['registered_future_requests'][REQ]
            assert request['budget'] == 1 and request['remaining'] == 0
            assert set(request['consumed']) == {CASE}
            assert request['consumed'][CASE]['state'] == 'CLOSED_ACCEPTED'
            assert CASE not in read(CONTROL / 'DISPATCH_CLAIMS.json')['claims']
            write('FINAL_PUBLICATION_START', uuid=monitor['uuid'])
            with LOG.open('xb') as output:
                result = subprocess.run(['/usr/bin/python3', '-B', str(SCRIPT)],
                                        stdin=subprocess.DEVNULL, stdout=output,
                                        stderr=subprocess.STDOUT, cwd='/root/workspace',
                                        timeout=2 * 3600)
            write('FINAL_PUBLICATION_FINISHED' if result.returncode == 0 else 'FINAL_PUBLICATION_FAILED_STOP',
                  uuid=monitor['uuid'], returncode=result.returncode, log=str(LOG))
            return
        if state in ('MONITOR_EXCEPTION_STOP', 'SUPERVISOR_GONE_WITHOUT_NATURAL_DONE_STOP',
                     'BOUND_48H_MONITOR_STOP', 'TERMINAL_WITHOUT_AUTO_RETRY'):
            write('MONITOR_STOP_NO_PUBLICATION', monitor_status=state)
            return
        if not live(MONITOR_PID):
            write('MONITOR_PROCESS_GONE_NO_PUBLICATION', monitor_status=state)
            return
        write('WAITING_FOR_ACCEPTED_ARCHIVE', monitor_status=state, monitor_pid=MONITOR_PID)
        time.sleep(90)
    write('BOUND_52H_PUBLICATION_WATCH_STOP')


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        write('PUBLICATION_EXCEPTION_STOP', reason=repr(error))
        raise
