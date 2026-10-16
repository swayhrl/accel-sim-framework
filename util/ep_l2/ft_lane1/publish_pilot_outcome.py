"""Publish the existing waiter's final event; no admission or resource polling.

An optional pidfd wait consumes no lease and never starts/retries a build.
Only this lane's clean branch, current matching request and new pack may change.
"""
import argparse
import copy
from datetime import datetime
import fcntl
import hashlib
import json
import os
from pathlib import Path
import select
import signal
import subprocess
import time
from zoneinfo import ZoneInfo

import engineering_pilot as pilot

ROOT = Path('docs/ep_l2/codex_handoff/fast_track_2026_10_16_v1/lane1')
BRANCH = 'hrl/ep-l2-ft20261016-lane1-v1'


def git(*args):
    return subprocess.check_output(['git', *args], cwd=pilot.REPOSITORY, timeout=60)


def classify(request, state, raw):
    result = {'waiter_status': state['status'], 'classification': 'ENGINEERING_ONLY',
              'engineering_binary_sha256': None, 'runtime_ready': False,
              'independent_qualification': False, 'actual_directed_attempts': 0,
              'actual_directed_passes': 0, 'formal_promotion': False,
              'compiler_capable_phase_started': False}
    if state['status'] == 'PILOT_RUNNER_FINISHED_NO_AUTOMATIC_RETRY':
        if raw is None:
            result['status'] = 'ENGINEERING_NOT_STARTED_OR_NO_RECEIPT_REVIEW_REQUIRED'
            return result
        pilot.require(raw['classification'] == 'ENGINEERING_ONLY', 'OUTCOME_CLASSIFICATION_CHANGED')
        pilot.require(raw['pilot_id'] == request['pilot_id'] and raw['identity'] == request['identity'], 'OUTCOME_IDENTITY_MISMATCH')
        pilot.require(raw['runtime_ready'] is False and raw['independent_qualification'] is False,
                      'ENGINEERING_SCIENTIFIC_PROMOTION_REFUSED')
        pilot.require(raw.get('formal_binary_sha256') is None, 'ENGINEERING_FORMAL_BINARY_REFUSED')
        tests = {r['name'] for r in request['planned_directed_commands']}
        executed = [r for r in raw['commands'] if r['name'] in tests]
        result.update(status=raw['status'], engineering_binary_sha256=raw['engineering_binary_sha256'],
            actual_directed_attempts=len(executed), actual_directed_passes=sum(r.get('exit_code') == 0 for r in executed),
            wall_seconds=raw.get('wall_seconds'), sampled_high_water=raw.get('sampled_high_water'),
            lease_released_token_consumed=raw.get('lease_released_token_consumed', False),
            compiler_capable_phase_started=any(r['name'] in {'configure', 'build'} and r.get('process')
                                               for r in raw['commands']))
        if raw['status'] == 'COMPLETE_ENGINEERING_ONLY':
            pilot.require(len(executed) == 21 and all(r.get('exit_code') == 0 for r in executed), 'MISSING_PRODUCER_EXECUTIONS')
    elif state['status'] == 'FORMAL_DRIVER_FINISHED_NO_AUTOMATIC_RETRY':
        # Preserve the producer's original receipt without manufacturing a
        # release contract, independent certificate or scientific acceptance.
        result.update(classification='FORMAL_PRODUCER_BUILD_EVENT_REQUIRES_RELEASE_AUDIT',
                      status='FORMAL_BUILD_RECORDED_RELEASE_FREEZE_PENDING', pilot_cancelled=True,
                      producer_status=raw.get('status') if raw else None,
                      compiler_capable_phase_started=bool(raw.get('compiler_started')) if raw else False,
                      producer_binary_sha256=raw.get('binary_sha256') if raw else None,
                      producing_framework=raw.get('framework_source_commit') if raw else None,
                      producing_core=raw.get('core_source_commit') if raw else None)
    else:
        result['status'] = state['status']
    return result


def merge_receipt(current, request, state, result, pack):
    receipt = copy.deepcopy(current)
    # All formal source/binary/qualification/acceptance fields are retained.
    receipt['task_id'] = 'FT20261017_LANE1_R8_AUTOMATIC_OUTCOME'
    receipt['recorded_at'] = pilot.utc()
    receipt['status'] = result['status']
    receipt['background_worker_running'] = False
    receipt['actual_compiler_started_this_revision'] = bool(result['compiler_capable_phase_started'])
    receipt['gate_waiter'] = dict(state, actual_process_finished=True)
    receipt['engineering_pilot_outcome'] = dict(result, evidence_pack=pack,
                                               pilot_id=request['pilot_id'])
    receipt.setdefault('artifacts', []).append(pack)
    if result['classification'] == 'ENGINEERING_ONLY':
        receipt['engineering_pilot'].update(status=result['status'],
            binary_sha256=result['engineering_binary_sha256'],
            executed_directed_tests=result['actual_directed_attempts'],
            passed_directed_tests=result['actual_directed_passes'],
            resource_high_water=result.get('sampled_high_water'),
            compiler_started=bool(result['compiler_capable_phase_started']),
            formal_runtime_ready=False, formal_application_permission=False)
        receipt.setdefault('validation', {})['engineering_pilot_producer_tests'] = {
            'executed': result['actual_directed_attempts'], 'passed': result['actual_directed_passes'],
            'classification': 'ENGINEERING_EVIDENCE_ONLY_NOT_FORMAL_QUALIFICATION'}
    receipt['next_action'] = ('Engineering evidence only: review any ordinary failure and bounded remediation; '
        'official release/independent11gate/formal resource admission remain separate. '
        'If the formal driver won, audit/freeze its official binary before announcing a release.')
    return receipt


def publish(request_path, state_path):
    request = json.loads(request_path.read_text()); state = json.loads(state_path.read_text())
    pilot.require(pilot.digest(request_path) == state['request_sha256'], 'WAITED_REQUEST_CHANGED')
    pilot.require(state.get('finished_at') is not None, 'WAITER_NOT_FINISHED')
    pilot.require(pilot.digest(pilot.REPOSITORY / ROOT / 'LOW_SPACE_PILOT_REQUEST.json') == state['request_sha256'], 'NEWER_REQUEST_PRESENT')
    pilot.require(git('branch', '--show-current').decode().strip() == BRANCH, 'WRONG_PUBLICATION_BRANCH')
    pilot.require(not git('status', '--porcelain'), 'DIRTY_PUBLICATION_WORKTREE')
    before = git('rev-parse', 'HEAD').decode().strip()
    remote = git('ls-remote', 'origin', 'refs/heads/' + BRANCH).decode().split()[0]
    pilot.require(before == remote, 'REMOTE_CHANGED_NO_AUTOMATIC_MERGE_OR_FORCE')
    engineering = Path(request['output_root']) / 'ENGINEERING_BUILD_RECEIPT.json'
    formal = state_path.parent / 'formal_build_attempt_r1/BUILD_AND_TEST_RECEIPT.json'
    raw_path = formal if state['status'] == 'FORMAL_DRIVER_FINISHED_NO_AUTOMATIC_RETRY' else engineering
    raw = json.loads(raw_path.read_text()) if raw_path.exists() else None
    result = classify(request, state, raw)
    if raw and result.get('engineering_binary_sha256'):
        binary = Path(raw['engineering_binary_path']).resolve()
        pilot.require(binary.is_relative_to(Path(request['build_root']).resolve()), 'BINARY_OUTSIDE_PILOT_BUILD')
        pilot.require(pilot.digest(binary) == result['engineering_binary_sha256'], 'ENGINEERING_BINARY_CHANGED')
    timestamp = datetime.now(ZoneInfo('Asia/Shanghai')).strftime('%Y%m%dT%H%M%S')
    pack = Path('docs/ep_l2/review_packs') / ('FT20261017_LANE1_R8_OUTCOME_' + timestamp)
    full = pilot.REPOSITORY / pack; full.mkdir(exist_ok=False)
    current = json.loads((pilot.REPOSITORY / ROOT / 'RECEIPT.json').read_text())
    (full / 'PRIOR_RECEIPT.json').write_text(json.dumps(current, indent=2) + '\n')
    (full / 'PRIOR_STATUS.md').write_bytes((pilot.REPOSITORY / ROOT / 'STATUS.md').read_bytes())
    (full / 'GATEWAITER_FINAL.json').write_text(json.dumps(state, indent=2) + '\n')
    (full / 'OUTCOME.json').write_text(json.dumps(result, indent=2) + '\n')
    if raw_path.exists():
        (full / 'ACTUAL_BUILD_RECEIPT.json').write_bytes(raw_path.read_bytes())
    logs = []
    for path in sorted(state_path.parent.glob('*.log')):
        logs.append({'path': str(path), 'bytes': path.stat().st_size, 'sha256': pilot.digest(path)})
    (full / 'LOCAL_LOG_MANIFEST.json').write_text(json.dumps(logs, indent=2) + '\n')
    merged = merge_receipt(current, request, state, result, str(pack))
    for name in ['RECEIPT.json', 'RECEIPT_REVIEW_R8.json']:
        (pilot.REPOSITORY / ROOT / name).write_text(json.dumps(merged, indent=2) + '\n')
    if raw and result['classification'] == 'ENGINEERING_ONLY':
        (pilot.REPOSITORY / ROOT / 'ENGINEERING_BUILD_RECEIPT.json').write_text(json.dumps(raw, indent=2) + '\n')
    (pilot.REPOSITORY / ROOT / 'GATEWAITER_STATE.json').write_text(json.dumps(state, indent=2) + '\n')
    status = ('# Lane1 r8 automatic outcome\n\nStatus: ' + result['status'] +
        '\n\nThe unique waiter has finished; no automatic retry is running. Core/Framework/source identities remain in RECEIPT.json.\n\n' +
        'Pilot evidence is ENGINEERING_ONLY. Formal scientific runtime/binary/qualification/accepted-pair fields retain their preceding values; no engineering promotion occurred.\n\n' +
        'Actual directed attempts: ' + str(result['actual_directed_attempts']) + '; passes: ' + str(result['actual_directed_passes']) +
        '. Exact timings/resource samples/binary identity/stop reason: ' + str(pack) + '.\n\n' + merged['next_action'] + '\n')
    (pilot.REPOSITORY / ROOT / 'STATUS.md').write_text(status)
    (full / 'README.md').write_text(status)
    files = sorted(x for x in full.iterdir() if x.is_file())
    (full / 'SHA256SUMS').write_text(''.join(pilot.digest(x) + '  ' + x.name + '\n' for x in files))
    staged = [str(ROOT / p) for p in ['STATUS.md', 'RECEIPT.json', 'RECEIPT_REVIEW_R8.json',
              'ENGINEERING_BUILD_RECEIPT.json', 'GATEWAITER_STATE.json']]
    subprocess.run(['git', 'add', *staged], cwd=pilot.REPOSITORY, check=True, timeout=15)
    subprocess.run(['git', 'add', '-f', str(pack)], cwd=pilot.REPOSITORY, check=True, timeout=15)
    subprocess.run(['git', 'diff', '--cached', '--check'], cwd=pilot.REPOSITORY, check=True, timeout=15)
    subprocess.run(['git', 'commit', '-m', 'ep-l2 lane1 r8: record automatic bounded waiter/build outcome'], cwd=pilot.REPOSITORY, check=True, timeout=30)
    publication = git('rev-parse', 'HEAD').decode().strip()
    subprocess.run(['git', 'push', 'origin', 'HEAD:refs/heads/' + BRANCH], cwd=pilot.REPOSITORY, check=True, timeout=60)
    subprocess.run(['git', 'fetch', '--no-tags', 'origin', BRANCH], cwd=pilot.REPOSITORY, check=True, timeout=60)
    pilot.require(git('rev-parse', 'refs/remotes/origin/' + BRANCH).decode().strip() == publication, 'REMOTE_READBACK_MISMATCH')
    pilot.require(git('show', publication + ':' + str(ROOT/'RECEIPT.json')) ==
                  (pilot.REPOSITORY/ROOT/'RECEIPT.json').read_bytes(), 'REMOTE_RECEIPT_MISMATCH')
    return {'status': 'OUTCOME_PUSHED_AND_READ_BACK', 'publication_sha': publication,
            'pack': str(pack), 'result': result, 'verified_at': pilot.utc()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--request', type=Path, required=True)
    parser.add_argument('--waiter-status', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(); args.output.mkdir(parents=True, exist_ok=False)
    with (pilot.SHARED/'LANE1_OUTCOME_PUBLISHER.lock').open('a+') as singleton:
        fcntl.flock(singleton, fcntl.LOCK_EX | fcntl.LOCK_NB)
        state = json.loads(args.waiter_status.read_text())
        own = {'status': 'WAITING_EXISTING_PIDFD_NO_DISK_OR_GIT_POLL', 'pid': pilot.process_info(os.getpid()),
               'watched_pid': state['pid'], 'request_sha256': state['request_sha256'],
               'source': str(Path(__file__).resolve()), 'source_sha256': pilot.digest(__file__),
               'deadline_unix': state['deadline_unix'] + 120, 'started_at': pilot.utc()}
        pilot.write_json(args.output/'PUBLISHER_STATE.json', own)
        try:
            if not state.get('finished_at'):
                pid = state['pid']['pid']; info = pilot.process_info(pid)
                pilot.require(info['start_ticks'] == state['pid']['start_ticks'], 'WAITER_PID_REUSED')
                descriptor = os.pidfd_open(pid)
                try:
                    pilot.require(pilot.process_info(pid)['start_ticks'] == info['start_ticks'], 'WAITER_PID_CHANGED')
                    ready, _, _ = select.select([descriptor], [], [], max(0, own['deadline_unix'] - time.time()))
                    pilot.require(bool(ready), 'PUBLISHER_EVENT_WAIT_EXPIRED')
                finally:
                    os.close(descriptor)
            with (pilot.SHARED/'LANE1_PUBLICATION.lock').open('a+') as lock:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                own.update(publish(args.request, args.waiter_status))
        except BaseException as error:
            own.update(status='PUBLICATION_HELD_REVIEW_REQUIRED', error=repr(error))
        finally:
            own['finished_at'] = pilot.utc(); pilot.write_json(args.output/'PUBLISHER_STATE.json', own)
            print(json.dumps(own, indent=2))


if __name__ == '__main__':
    main()
