#!/usr/bin/env python3
"""Bounded Lane2 release-event listener. Never a disk waiter or build launcher."""
import argparse
from datetime import datetime, timedelta, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import time

LANE1_REF = 'refs/remotes/origin/hrl/ep-l2-ft20261016-lane1-v1'
LANE5_REF = 'refs/remotes/origin/hrl/ep-l2-ft20261016-lane5-v1'
LANE1_RECEIPT = 'docs/ep_l2/codex_handoff/fast_track_2026_10_16_v1/lane1/RECEIPT.json'
ACCEPTANCE = 'docs/ep_l2/codex_handoff/fast_track_2026_10_16_v1/lane5/APPLICATION_ACCEPTANCE.json'
BINARY_ROOTS = (Path('/workspace/build/ep-l2-ft20261016-lane1-r0-1'),
                Path('/workspace/results/ep_l2_ft20261016/lane1'))


def digest(path):
    value = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            value.update(block)
    return value.hexdigest()


def inspect_release(receipt, acceptance, expected_core, expected_framework,
                    binary_roots=BINARY_ROOTS):
    """Detect a candidate event only; even READY does not grant admission."""
    result = {'admission_granted': False, 'independent_qualification': False,
              'resource_check_performed': False, 'compiler_or_simulator_started': False}

    def state(name, detail):
        return dict(result, state=name, detail=detail)

    if receipt.get('lane_id') != 1:
        return state('IDENTITY_REFUSED', 'not a Lane1 receipt')
    if (acceptance.get('schema_version') != 'EPL2_SCIENTIFIC_ACCEPTANCE_V2' or
            acceptance.get('authority', {}).get('lane_id') != 5 or
            not isinstance(acceptance.get('withdrawn_releases'), list)):
        return state('ACCEPTANCE_AUTHORITY_REFUSED', 'current Lane5 V2 authority required')
    core, framework = receipt.get('core_source_commit'), receipt.get('framework_source_commit')
    binary_sha = receipt.get('binary_sha256')
    for old in acceptance['withdrawn_releases']:
        if (core and core == old.get('core_source_commit')) or (
                binary_sha and binary_sha == old.get('binary_sha256')):
            return state('WITHDRAWN_RELEASE_REFUSED', 'old Core/binary is scientifically suspended')
    if core != expected_core or framework != expected_framework:
        return state('SOURCE_REBIND_REQUIRED', 'official source/Framework changed; re-audit before runtime')
    if receipt.get('runtime_ready') is not True or binary_sha is None:
        return state('WAIT_OFFICIAL_BINARY', 'pinned source has no published ready binary')
    if not isinstance(binary_sha, str) or not re.fullmatch(r'[0-9a-f]{64}', binary_sha):
        return state('BINARY_IDENTITY_REFUSED', 'published SHA256 is missing or malformed')
    if any(word in str(receipt.get('status', '')).upper()
           for word in ('FAILED', 'SUSPENDED', 'WITHDRAWN')):
        return state('PRODUCER_STATE_REFUSED', 'producer receipt reports failure/suspension')
    binary = receipt.get('binary_path', receipt.get('binary'))
    if not isinstance(binary, str):
        return state('BINARY_PATH_REQUIRED', 'read exact producer build receipt; do not guess a path')
    path = Path(binary).resolve()
    if not any(path.is_relative_to(root.resolve()) for root in binary_roots):
        return state('BINARY_PATH_REFUSED', 'binary outside the declared Lane1 namespace')
    if not path.is_file():
        return state('BINARY_LOCAL_MISSING', 'published path not present in this namespace')
    if digest(path) != binary_sha:
        return state('BINARY_HASH_REFUSED', 'local bytes differ from published identity')
    return dict(result, state='RELEASE_CANDIDATE_VERIFIED', binary_path=str(path),
                binary_sha256=binary_sha,
                detail='event only: inspect exact producer gates, source and current shared admission next')


def bounds(interval, duration):
    if not 600 <= interval <= 900:
        raise ValueError('release checks must be 10–15 minutes apart')
    if not interval <= duration <= 48 * 3600:
        raise ValueError('finite horizon required, between one interval and 48 hours')


def atomic_json(path, value):
    temporary = path.with_suffix('.pending')
    temporary.write_text(json.dumps(value, indent=2) + '\n')
    temporary.replace(path)


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args], timeout=90)


def fetch_event(repo, core, framework):
    remote = git(repo, 'remote', 'get-url', 'origin').decode().strip()
    if remote not in ('git@github.com:swayhrl/accel-sim-framework.git',
                      'https://github.com/swayhrl/accel-sim-framework.git'):
        raise ValueError('unexpected Framework origin')
    git(repo, 'fetch', '--no-tags', 'origin',
        'hrl/ep-l2-ft20261016-lane1-v1', 'hrl/ep-l2-ft20261016-lane5-v1')
    one = git(repo, 'rev-parse', LANE1_REF).decode().strip()
    five = git(repo, 'rev-parse', LANE5_REF).decode().strip()
    receipt_bytes = git(repo, 'show', one + ':' + LANE1_RECEIPT)
    authority_bytes = git(repo, 'show', five + ':' + ACCEPTANCE)
    return dict(inspect_release(json.loads(receipt_bytes), json.loads(authority_bytes), core, framework),
                lane1_publication=one, lane5_publication=five,
                receipt_sha256=hashlib.sha256(receipt_bytes).hexdigest(),
                acceptance_sha256=hashlib.sha256(authority_bytes).hexdigest(),
                observed_utc=datetime.now(timezone.utc).isoformat())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--lock', type=Path, required=True)
    parser.add_argument('--expected-core', required=True)
    parser.add_argument('--expected-framework', required=True)
    parser.add_argument('--interval-seconds', type=int, default=600)
    parser.add_argument('--duration-seconds', type=int, default=1200)
    args = parser.parse_args()
    bounds(args.interval_seconds, args.duration_seconds)
    for identity in (args.expected_core, args.expected_framework):
        if not re.fullmatch(r'[0-9a-f]{40}', identity):
            raise ValueError('exact source commits required')
    # The permanent file is never removed; a kernel lock prevents duplicate listeners.
    with args.lock.open('a+') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        args.out.mkdir(parents=True, exist_ok=False)
        start = datetime.now(timezone.utc)
        receipt = {'status': 'DEPENDENCY_WAIT_ACTIVE', 'pid': os.getpid(),
            'start_ticks': int(Path('/proc/self/stat').read_text().rsplit(')', 1)[1].split()[19]),
            'started_utc': start.isoformat(),
            'deadline_utc': (start + timedelta(seconds=args.duration_seconds)).isoformat(),
            'lock': str(args.lock.resolve()), 'kind': 'READ_ONLY_RELEASE_EVENT_NOT_DISK_WAITER',
            'interval_seconds': args.interval_seconds, 'duration_seconds': args.duration_seconds,
            'listener_source_commit': git(args.repo, 'rev-parse', 'HEAD').decode().strip(),
            'listener_source_sha256': digest(__file__), 'expected_core': args.expected_core,
            'expected_framework': args.expected_framework, 'events': [],
            'disk_gate_waiter_created': False, 'build_lease_acquired': False,
            'compiler_or_simulator_started': False, 'process_active': True}
        target = args.out / 'WAIT_RECEIPT.json'

        def stopped(signum, frame):
            raise InterruptedError('owned dependency wait stopped by signal ' + str(signum))

        signal.signal(signal.SIGTERM, stopped)
        signal.signal(signal.SIGINT, stopped)
        end = time.monotonic() + args.duration_seconds
        try:
            while True:
                event = fetch_event(args.repo, args.expected_core, args.expected_framework)
                receipt['events'].append(event)
                atomic_json(target, receipt)
                print(json.dumps(event), flush=True)
                if event['state'] != 'WAIT_OFFICIAL_BINARY':
                    receipt['status'] = event['state']
                    break
                if time.monotonic() >= end:
                    receipt['status'] = 'DEPENDENCY_WAIT_EXPIRED'
                    break
                next_check = min(end, time.monotonic() + args.interval_seconds)
                while time.monotonic() < next_check:
                    if (args.out / 'STOP').exists():
                        raise InterruptedError('owned STOP file detected')
                    time.sleep(min(5, max(0, next_check - time.monotonic())))
        except InterruptedError as error:
            receipt.update(status='DEPENDENCY_WAIT_STOPPED', error=str(error))
        except Exception as error:
            receipt.update(status='DEPENDENCY_WAIT_ERROR_FAIL_CLOSED', error=repr(error))
            raise
        finally:
            receipt.update(process_active=False, finished_utc=datetime.now(timezone.utc).isoformat())
            atomic_json(target, receipt)
            print(json.dumps({'status': receipt['status'], 'events': len(receipt['events']),
                              'process_active': False}), flush=True)


if __name__ == '__main__':
    main()
