"""Wait only for this task's archive SHA worker, finalize cleanup, then one A65 lease."""
import json
import os
from pathlib import Path
import subprocess
import time
from paths import R, W, CLEANUP, save


def main():
    assert not (R / 'pipeline_started.json').exists()
    save('pipeline_started.json', {'epoch': time.time(), 'PID': os.getpid(),
                                   'GPU_lock_polling': False,
                                   'waits_for': 'owned durable 164 SHA receipt only'})
    until = time.monotonic() + 7200
    while True:
        query = subprocess.run(['ssh', '-n', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=10',
                                'hrl174new', 'test', '-f',
                                '/tmp/aiarch_109_firstbatch_sha_20261016_lane_m_v1/final.json'],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=20)
        if query.returncode == 0:
            break
        assert time.monotonic() < until, 'ARCHIVE_READ_ONLY_VERIFY_WAIT_LIMIT'
        time.sleep(20)
    with (CLEANUP / 'finalize.log').open('w') as log:
        subprocess.run(['python3', str(CLEANUP / 'finalize.py')], check=True,
                       stdout=log, stderr=subprocess.STDOUT)
    assert json.loads((CLEANUP / 'finished.json').read_text())['status'] == 'PASS_FIRST_BATCH_CLEANUP'
    env = os.environ.copy()
    env['A65_CONTROLLER_PID'] = str(os.getpid())
    with (R / 'supervisor.log').open('w') as log:
        subprocess.run(['python3', str(W / 'tools/aiarch_a65/gpu_supervisor.py')],
                       check=True, env=env, stdout=log, stderr=subprocess.STDOUT)
    save('pipeline_observations_ready.json', {'epoch': time.time(),
                                             'automatic_next_GPU_task': False,
                                             'review_raw_before_closeout': True})
    print('CLEANUP_AND_A65_OBSERVATIONS_READY_FOR_RAW_REVIEW', flush=True)


if __name__ == '__main__':
    main()
