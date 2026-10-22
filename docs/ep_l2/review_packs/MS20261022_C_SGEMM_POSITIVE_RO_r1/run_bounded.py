#!/usr/bin/env python3
"""Finite offline Python child under the existing original E resource API.

No controller, application token, native executable, or dependency watcher.
Administrative C/test lease is used because that is the existing work API's
supported non-build class; the actual child command is always this offline
line-oracle Python adapter. Resource guard ends with its one child.
"""
import datetime
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

E = Path('/workspace/worktrees/accel-sim-ep-l2-ms20261019-e-eval-v1')
sys.path.insert(0, str(E/'util/ep_l2/mechanism_e'))
import coordinator

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
OUT = coordinator.OUTPUT / 'C_SGEMM_RO_POSITIVE_20261022_r1'
CAP = 256*2**20


def write(name, value):
    (OUT/name).write_text(json.dumps(value,indent=2)+'\n')


if __name__ == '__main__':
    producer = subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD'],text=True).strip()
    for name in ('single_pass_oracle.py','run_bounded.py','check_adapter.py'):
        path = HERE/name
        assert path.read_bytes() == subprocess.check_output(['git','-C',str(ROOT),'show',producer+':'+str(path.relative_to(ROOT))])
    forecast = json.loads((HERE/'RESOURCE_PREFLIGHT.json').read_text())
    assert not OUT.exists(), 'preserve old revision; never rerun into existing output'
    coord = coordinator.Coordinator()
    lease = coord.reserve_work('C','test',1,CAP,CAP,str(OUT),result_growth_bytes=CAP)
    OUT.mkdir()
    write('LEASE.json',dict(**lease,actual_work='OFFLINE_PYTHON_LINE_CERTIFICATION_NOT_NATIVE_OR_BUILD'))
    pre_usage = coordinator.output_usage()
    child = None; failure = None; started = time.monotonic()
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', TMPDIR=str(OUT/'tmp'), SQLITE_TMPDIR=str(OUT/'tmp'))
    (OUT/'tmp').mkdir()
    try:
        # Tiny new adapter correctness checks share the same accounted lease.
        controls = subprocess.run([sys.executable,str(HERE/'check_adapter.py'),str(OUT/'adapter_controls')],
                                  cwd=ROOT,env=env,capture_output=True,text=True,timeout=30)
        (OUT/'adapter_controls.stdout').write_text(controls.stdout)
        (OUT/'adapter_controls.stderr').write_text(controls.stderr)
        controls.check_returncode()
        cmd = [sys.executable,str(HERE/'single_pass_oracle.py'),
               '--commandlist',forecast['input']['commandlist'], '--body',forecast['input']['body'],
               '--expected-sha256',forecast['input']['body_expected_sha256'],
               '--output',str(OUT/'oracle'), '--producer',producer,
               '--expected-records',str(forecast['input']['saved_expected_instruction_records'])]
        write('ACTUAL_COMMAND.json',dict(command=cmd,producer_commit=producer,pre_usage=pre_usage,
                                       actual_native_starts=0,actual_application_starts=0))
        with (OUT/'progress.log').open('w') as stdout, (OUT/'stderr.log').open('w') as stderr:
            child = subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=stdout,stderr=stderr,start_new_session=True)
            coord.bind_work_process(lease['lease_id'],'C',child.pid)
            write('CHILD.json',dict(pid=child.pid,started_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                                   work='ONE_OFFLINE_PASS_NOT_NATIVE',lease_id=lease['lease_id']))
            while child.poll() is None:
                free = os.statvfs('/workspace').f_bavail * os.statvfs('/workspace').f_frsize
                allocated = sum(p.stat().st_blocks*512 for p in OUT.rglob('*') if p.is_file())
                if free <= lease['disk_floor_bytes']+lease['monitor_reserve_bytes'] or allocated >= CAP:
                    failure = dict(reason='WORKSPACE_STOP_RESERVE' if free <= lease['disk_floor_bytes']+lease['monitor_reserve_bytes'] else 'OWN_GROWTH_CAP',
                                   free_bytes=free,allocated_bytes=allocated)
                    os.killpg(child.pid,signal.SIGTERM)
                    try: child.wait(timeout=lease['termination_grace_seconds'])
                    except subprocess.TimeoutExpired:
                        os.killpg(child.pid,signal.SIGKILL);child.wait()
                    break
                time.sleep(lease['monitor_interval_seconds'])
            code = child.wait()
            if code and failure is None: failure=dict(reason='OFFLINE_CHILD_FAILED',returncode=code)
    except BaseException as e:
        failure=dict(reason=type(e).__name__,detail=str(e))
        if child is not None and child.poll() is None:
            os.killpg(child.pid,signal.SIGTERM)
            try:child.wait(timeout=3)
            except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);child.wait()
    finally:
        allocated = sum(p.stat().st_blocks*512 for p in OUT.rglob('*') if p.is_file())
        result = dict(status='COMPLETE_OFFLINE_MODEL_PROOF_NOT_E_QUALIFIED' if failure is None else 'MISSING_OR_UNSUPPORTED_NO_RETRY',
                      failure=failure,elapsed_seconds=time.monotonic()-started,
                      allocated_bytes_before_final_receipt=allocated,post_usage=coordinator.output_usage(),
                      growth_reservation_bytes=CAP,lease_id=lease['lease_id'],producer_commit=producer,
                      native_application_build_starts=0,body_rescans_or_backup_scans=0)
        write('RUN_RECEIPT.json',result)
        coord.release_work(lease['lease_id'],'C',result,no_child_started=child is None)
        write('LEASE_RELEASED.json',dict(lease_id=lease['lease_id'],status='RELEASED'))
        print(json.dumps(result),flush=True)
    sys.exit(0 if failure is None else 1)
