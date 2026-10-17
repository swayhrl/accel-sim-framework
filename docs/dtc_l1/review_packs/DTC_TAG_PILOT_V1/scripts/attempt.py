#!/usr/bin/env python3
"""One locked, immutable simulation attempt; no background resubmission."""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import uuid
import sys
import signal
from datetime import datetime, timezone


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()


def now():
    return datetime.now(timezone.utc).isoformat()


def write(path, obj):
    with path.open('x') as f:
        json.dump(obj, f, indent=2)
        f.write('\n')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--spec', required=True)
    ap.add_argument('--root', required=True)
    a = ap.parse_args()
    spec = json.loads(Path(a.spec).read_text())
    root = Path(a.root).resolve()
    # Lane T wrapper only: consume fixed UUID and foreground authority.
    sys.path.insert(0, '/workspace/worktrees/accel-sim-iscas2027-dtc-tag-pilot-174-v1/docs/dtc_l1/review_packs/DTC_TAG_PILOT_V1/scripts')
    import common
    assert root == common.ROOT / 'attempts'
    gate = json.loads((common.ROOT / 'EXECUTION_GATE.json').read_text())
    assert gate['status'] == 'PASS_FOR_PREREGISTERED_SEVEN_ONLY'
    authority = json.loads((common.ROOT / 'AUTHORITY_ACTIVE.json').read_text())
    owner = common.proc(authority['pid'])
    assert owner and owner['start_ticks'] == authority['start_ticks']
    assert common.sha(common.PACK / 'PRE_REGISTRATION.tsv') == gate['plan_sha256']
    import csv
    with (common.PACK / 'PRE_REGISTRATION.tsv').open() as stream:
        registered = list(csv.DictReader(stream, delimiter='\t'))
    matching = [row for row in registered if row['label'] == spec['label'] and row['attempt_uuid'] == spec['attempt_uuid']]
    assert len(matching) == 1
    assert common.sha(Path(a.spec)) == matching[0]['spec_sha256']
    common.source_check()
    root.mkdir(parents=True, exist_ok=True)
    admission_holds = root / 'ROW_ADMISSION_HOLDS.json'
    if admission_holds.exists():
        holds = json.loads(admission_holds.read_text())
        if spec['label'] in holds['held_labels']:
            raise SystemExit('ROW_ADMISSION_HOLD: ' + spec['label'] + '; ' + holds['reason'])
    identity = hashlib.sha256(json.dumps(spec, sort_keys=True).encode()).hexdigest()
    locks = root / 'locks'
    locks.mkdir(exist_ok=True)
    with (locks / (identity + '.lock')).open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        for p in root.glob('*/RUN_START.json'):
            old = json.loads(p.read_text())
            if old['identity'] == identity:
                raise RuntimeError('attempt already exists; inspect and reuse or register an explicit retry: ' + str(p.parent))
        for key in ['runtime', 'trace_list']:
            assert digest(spec[key]) == spec[key + '_sha256'], key
        for cfg in spec['configs']:
            assert digest(cfg['path']) == cfg['sha256'], cfg['path']
        for member in spec['members']:
            assert Path(member['path']).stat().st_size == member['bytes'], member['path']
            assert digest(member['path']) == member['sha256'], member['path']
        attempt = spec['attempt_uuid']
        assert str(uuid.UUID(attempt)) == attempt
        run = root / (spec['label'] + '_' + attempt)
        run.mkdir(exist_ok=False)
        shutil.copy2(__file__, run / 'immutable_runner.py')
        (run / 'immutable_runner.py').chmod(0o555)
        write(run / 'SPEC.json', spec)
        # Freeze a content-addressed binary so a later build cannot replace it.
        binaries = root / 'binaries' / spec['runtime_sha256']
        binaries.mkdir(parents=True, exist_ok=True)
        binary = binaries / 'accel-sim.out'
        if not binary.exists():
            temporary = binaries / ('copy-' + attempt)
            shutil.copy2(spec['runtime'], temporary)
            temporary.chmod(0o555)
            try:
                os.link(temporary, binary)
            except FileExistsError:
                pass
            temporary.unlink()
        assert digest(binary) == spec['runtime_sha256']
        command = ['/usr/bin/time', '-v', '-o', str(run / 'resource.time'),
                   str(binary), '-trace', spec['trace_list']]
        for i, cfg in enumerate(spec['configs']):
            dest = run / f'config-{i}.config'
            shutil.copy2(cfg['path'], dest)
            dest.chmod(0o444)
            command += ['-config', str(dest)]
        start = dict(attempt_uuid=attempt, identity=identity, launch_utc=now(),
                     spec=spec, runner_sha256=digest(run / 'immutable_runner.py'),
                     command=command, classification=spec['classification'])
        write(run / 'RUN_START.json', start)
        print(str(run), flush=True)
        with (run / 'simulator.stdout').open('xb') as out, (run / 'simulator.stderr').open('xb') as err:
            proc = subprocess.Popen(command, cwd=run, stdout=out, stderr=err,
                                    start_new_session=True, preexec_fn=lambda: os.nice(10))
            write(run / 'PID.json', dict(runner_pid=os.getpid(), runner_start_ticks=common.proc(os.getpid())['start_ticks'], process_pid=proc.pid, process_start_ticks=common.proc(proc.pid)['start_ticks']))
            termination_reason = 'NATURAL_PROCESS_RETURN'
            try:
                code = proc.wait(timeout=spec['wall_timeout_seconds'])
            except subprocess.TimeoutExpired:
                termination_reason = 'PREREGISTERED_WALL_TIMEOUT_PRESERVED_NO_RETRY'
                os.killpg(proc.pid, signal.SIGTERM)
                try:
                    proc.wait(timeout=30)
                except subprocess.TimeoutExpired:
                    os.killpg(proc.pid, signal.SIGKILL)
                    proc.wait()
                code = 124
        write(run / 'RUN_TERMINAL.json', dict(attempt_uuid=attempt, exit_status=code, termination_reason=termination_reason,
              terminal_utc=now(), stdout_sha256=digest(run / 'simulator.stdout'),
              stderr_sha256=digest(run / 'simulator.stderr'), resource_sha256=digest(run / 'resource.time')))
        text = (run / 'simulator.stdout').read_text(errors='replace')
        instructions = re.findall(r'^gpu_tot_sim_insn\s*=\s*(\d+)', text, re.M)
        cycles = re.findall(r'^gpu_tot_sim_cycle\s*=\s*(\d+)', text, re.M)
        checks = dict(natural_exit=code == 0, instructions=bool(instructions) and int(instructions[-1]) == spec['expected_instructions'],
                      cycles=bool(cycles) and int(cycles[-1]) > 0,
                      runtime_identity=digest(binary) == spec['runtime_sha256'],
                      trace_list_identity=digest(spec['trace_list']) == spec['trace_list_sha256'],
                      no_assertion='Assertion' not in (run / 'simulator.stderr').read_text(errors='replace'))
        validation = dict(attempt_uuid=attempt, scope='TERMINAL_IDENTITY_AND_INSTRUCTION_CHECK_ONLY',
                          checks=checks, status='PASS' if all(checks.values()) else 'FAIL',
                          instructions=int(instructions[-1]) if instructions else None,
                          cycles=int(cycles[-1]) if cycles else None)
        write(run / 'VALIDATION.json', validation)
        print(json.dumps(validation), flush=True)
        if not all(checks.values()):
            raise SystemExit(1)


if __name__ == '__main__':
    main()
