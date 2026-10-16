"""Single visible Lane1 waiter, bounded48h,600s cadence, no waiting lease.

Default is one read-only inspection. --watch --execute-authorized enables only
the r7 formal path or independently authorized r8 engineering path.
"""
import argparse
import fcntl
import json
import os
from pathlib import Path
import signal
import subprocess
import time

import engineering_pilot as pilot

STOP = False


def central_snapshot():
    with (pilot.SHARED / 'REGISTRY.lock').open('r') as lock:
        fcntl.flock(lock, fcntl.LOCK_SH | fcntl.LOCK_NB)
        data = json.loads((pilot.SHARED / 'RUN_REGISTRY.json').read_text())
    pilot.require(data['authority_host'] == pilot.socket.gethostname(), 'CENTRAL_HOST_MISMATCH')
    policy = data['hosts'][data['authority_host']]
    pilot.require(policy['boot_id'] == pilot.boot_id(), 'CENTRAL_BOOT_MISMATCH')
    active = {k: v for k, v in data['resource_leases'].items() if v['status'] in {'RESERVED', 'RUNNING'}}
    runs = {k: v for k, v in data['runs'].items() if v['status'] in {'RESERVED', 'RUNNING'}}
    return {'policy': policy, 'active_builds': active, 'active_runs': runs,
            'workspace': pilot.filesystem('/workspace'), 'available_memory_bytes': pilot.available_memory()}


def formal_ready(state):
    policy = state['policy']
    return (state['workspace']['available_bytes'] >= max(48 * pilot.GIB, policy['min_disk_free_bytes']) + 2 * pilot.GIB
            and state['available_memory_bytes'] - 8 * pilot.GIB >= max(64 * pilot.GIB, policy['min_available_memory_bytes'])
            and not state['active_builds'] and not state['active_runs'])


def pause(seconds):
    end = time.monotonic() + seconds
    while not STOP and time.monotonic() < end:
        time.sleep(min(1, end - time.monotonic()))


def wait_owned_child(process, engineering):
    signalled = False
    while True:
        try:
            return process.wait(timeout=1)
        except subprocess.TimeoutExpired:
            if STOP and not signalled:
                # Pilot handles TERM through its monitored stop event. The
                # frozen formal Python entry uses INT/finally to stop its own
                # separate CMake group and release its own central lease.
                process.send_signal(signal.SIGTERM if engineering else signal.SIGINT)
                signalled = True


def authorization_from_lane5(request, cache):
    subprocess.run(['git', 'fetch', '--no-tags', 'origin', 'hrl/ep-l2-ft20261016-lane5-v1'],
                   cwd=pilot.REPOSITORY, check=True, timeout=45, stdout=subprocess.DEVNULL)
    ref = pilot.git('rev-parse', pilot.LANE5_REF).decode().strip()
    path = 'docs/ep_l2/codex_handoff/fast_track_2026_10_16_v1/lane5/LOW_SPACE_PILOT_AUTHORIZATION.json'
    found = subprocess.run(['git', 'cat-file', '-e', ref + ':' + path], cwd=pilot.REPOSITORY,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=15)
    if found.returncode:
        return None
    raw = pilot.git('show', ref + ':' + path); data = json.loads(raw)
    if data.get('pilot_id') != request['pilot_id']:
        return None
    target = cache / ('LANE5_AUTHORIZATION_' + ref + '.json')
    if not target.exists():
        with target.open('xb') as stream:
            stream.write(raw)
    return ref, target, data


def run_formal(request, state, output, status):
    # The waiter does not claim an outer lease: the original entry owns it.
    with (pilot.SHARED / 'LANE1_BUILD_EXECUTION.lock').open('a+') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        pilot.require(formal_ready(central_snapshot()), 'FORMAL_RECHECK_FAILED')
        cancellation = Path(request['cancellation_marker_path'])
        cancellation.parent.mkdir(parents=True, exist_ok=True)
        with cancellation.open('x') as stream:
            json.dump({'pilot_id': request['pilot_id'], 'request_sha256': pilot.digest(status['request_path']),
                       'status': 'CANCELLED_FORMAL_ENTRY_WON', 'utc': pilot.utc()}, stream)
        official = Path(request['official_driver_path'])
        pilot.require(pilot.digest(official) == pilot.OFFICIAL_DRIVER_SHA, 'OFFICIAL_DRIVER_CHANGED')
        for tree, expected in [(request['official_framework_path'], pilot.FRAMEWORK),
                               (request['official_core_path'], pilot.CORE)]:
            pilot.require(pilot.git('rev-parse', 'HEAD', cwd=tree).decode().strip() == expected, 'FORMAL_SOURCE_CHANGED')
            pilot.require(not pilot.git('status', '--porcelain', '--untracked-files=no', cwd=tree), 'FORMAL_SOURCE_DIRTY')
        command = ['python3', str(official), '--core', request['official_core_path'],
                   '--out', str(output / 'formal_build_attempt_r1'), '--execute']
        status.update(status='FORMAL_DRIVER_INVOKED_ONCE', command=command, pilot_cancelled=True)
        pilot.write_json(output / 'GATEWAITER_STATUS.json', status)
        with (output / 'FORMAL_DRIVER.log').open('x') as log:
            process = subprocess.Popen(command, cwd=request['official_framework_path'],
                stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
            status['child'] = pilot.process_info(process.pid)
            pilot.write_json(output / 'GATEWAITER_STATUS.json', status)
            code = wait_owned_child(process, engineering=False)
        status.update(status='FORMAL_DRIVER_FINISHED_NO_AUTOMATIC_RETRY', exit_code=code)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--request', type=Path, required=True)
    parser.add_argument('--watch', action='store_true')
    parser.add_argument('--execute-authorized', action='store_true')
    parser.add_argument('--max-seconds', type=int, default=48 * 3600)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args(); request = json.loads(args.request.read_text())
    pilot.require(0 < args.max_seconds <= 48 * 3600, 'WAITER_TIME_LIMIT')
    pilot.require(pilot.digest(__file__) == request['identity']['gate_waiter_sha256'], 'WAITER_SOURCE_CHANGED')
    if not args.watch:
        print(json.dumps({'status': 'DRY_RUN_NO_WAITER_STARTED', 'state': central_snapshot()}, indent=2)); return
    pilot.require(args.output is not None, 'WAITER_OUTPUT_REQUIRED')
    pilot.no_symlink_path(args.output)
    with (pilot.SHARED / 'LANE1_GATEWAITER.lock').open('a+') as singleton:
        fcntl.flock(singleton, fcntl.LOCK_EX | fcntl.LOCK_NB)
        args.output.mkdir(parents=True, exist_ok=False)
        pid = pilot.process_info(os.getpid())
        status = {'status': 'WAITING_RESOURCE_OR_LANE5_AUTHORIZATION', 'pid': pid,
            'boot_id': pilot.boot_id(), 'started_at': pilot.utc(), 'request_path': str(args.request.resolve()),
            'request_sha256': pilot.digest(args.request), 'deadline_unix': time.time() + args.max_seconds,
            'cadence_seconds': 600, 'waiting_lease': None, 'automatic_execution_enabled': args.execute_authorized,
            'source': str(Path(__file__).resolve()), 'source_sha256': pilot.digest(__file__),
            'pilot_id': request['pilot_id'], 'invocations': 0}
        pilot.write_json(args.output / 'GATEWAITER_STATUS.json', status)
        pointer = pilot.SHARED / 'LANE1_GATEWAITER_STATUS.json'
        pilot.write_json(pointer, dict(status, output=str(args.output)))
        try:
            while not STOP and time.time() < status['deadline_unix']:
                pilot.require(pilot.digest(args.request) == status['request_sha256'], 'REQUEST_CHANGED_WHILE_WAITING')
                pilot.audit_sources(request)
                state = central_snapshot()
                status['last_observed_at'] = pilot.utc(); status['last_state'] = state
                if formal_ready(state) and args.execute_authorized:
                    status['status'] = 'FORMAL_FIRST_SAMPLE_PASS_WAIT_60_SECONDS'
                    pilot.write_json(args.output / 'GATEWAITER_STATUS.json', status)
                    pause(60)
                    if not STOP and formal_ready(central_snapshot()):
                        run_formal(request, state, args.output, status); status['invocations'] += 1; break
                if not state['active_builds'] and not state['active_runs']:
                    authorization = authorization_from_lane5(request, args.output)
                    if authorization:
                        publication, path, data = authorization
                        status['lane5_authorization_publication'] = publication
                        if data.get('status') == 'NO_SAFE_PILOT_ENVELOPE':
                            status['status'] = 'NO_SAFE_PILOT_ENVELOPE_FORMAL_WAITER_ONLY'
                        elif args.execute_authorized:
                            pilot.validate_authorization(request, data, pilot.digest(args.request))
                            # Freshly recheck before the runner makes its unique central claim.
                            current = central_snapshot()
                            if formal_ready(current):
                                status['status'] = 'FORMAL_ENTRY_PRIORITY_RECHECK_PENDING'
                            elif not current['active_builds'] and not current['active_runs']:
                                status.update(status='AUTHORIZED_PILOT_RUNNER_INVOKED_ONCE', invocations=1)
                                pilot.write_json(args.output / 'GATEWAITER_STATUS.json', status)
                                command = ['python3', request['pilot_driver_path'], '--request', str(args.request.resolve()),
                                    '--pilot-id', request['pilot_id'], '--authorization', str(path),
                                    '--authorization-publication', publication, '--execute-once']
                                with (args.output / 'PILOT_RUNNER.log').open('x') as stream:
                                    process = subprocess.Popen(command, stdout=stream, stderr=subprocess.STDOUT,
                                        cwd=pilot.REPOSITORY, start_new_session=True)
                                    status['child'] = pilot.process_info(process.pid)
                                    pilot.write_json(args.output / 'GATEWAITER_STATUS.json', status)
                                    status['exit_code'] = wait_owned_child(process, engineering=True)
                                status['status'] = 'PILOT_RUNNER_FINISHED_NO_AUTOMATIC_RETRY'; break
                pilot.write_json(args.output / 'GATEWAITER_STATUS.json', status)
                pilot.write_json(pointer, dict(status, output=str(args.output)))
                pause(600)
            else:
                status['status'] = 'WAITER_STOPPED_BY_SIGNAL' if STOP else 'RESOURCE_WAIT_EXPIRED'
        except BaseException as error:
            status['status'] = 'WAITER_STOPPED_FAIL_CLOSED'; status['error'] = repr(error)
        finally:
            status['finished_at'] = pilot.utc()
            pilot.write_json(args.output / 'GATEWAITER_STATUS.json', status)
            pilot.write_json(pointer, dict(status, output=str(args.output)))
            print(json.dumps(status, indent=2))


def stop(signum, frame):
    global STOP
    STOP = True


if __name__ == '__main__':
    signal.signal(signal.SIGTERM, stop); signal.signal(signal.SIGINT, stop)
    main()
