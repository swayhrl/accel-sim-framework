"""PREPARED_NOT_TESTED. Registered post-release two-root lifecycle fixture.

This module has no CLI and no simulation entrypoint. It neither compiles nor
freezes manifests. The coordinator must provide two exact CPU registrations
after AG4 terminal verification and CPU/resource/role admission. This covers
isolated wait queues and real overlapping roots/helpers; global authority,
worker-role admission and negative ownership cases remain separate checks.
"""
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
RAW = Path('/workspace/dtc-evidence-closure-20261019-v1/coordinator')


def identity(pid):
    fields = Path('/proc', str(pid), 'stat').read_text().rsplit(')', 1)[1].split()
    return {'pid': pid, 'start_ticks': int(fields[19]),
            'ppid': int(fields[1]), 'state': fields[0]}


def same(record):
    try:
        live = identity(record['pid'])
    except (OSError, ValueError):
        return False
    return live['start_ticks'] == record['start_ticks'] and live['state'] != 'Z'


def write_new(path, data):
    with Path(path).open('x') as stream:
        stream.write(json.dumps(data, indent=2) + '\n')


def run_two_registered_cpu_roots(requests, output):
    """Only call after gate/role admission; never interpret this as GPU PASS."""
    if len(requests) != 2:
        raise ValueError('EXACTLY_TWO_CPU_ROOTS_REQUIRED')
    output = Path(output).resolve()
    if not output.is_relative_to(RAW / 'cpu-qualification'):
        raise ValueError('CPU_OUTPUT_NOT_ISOLATED')
    if len({Path(r['destination']).resolve() for r in requests}) != 2:
        raise ValueError('CPU_ROOT_DESTINATIONS_MUST_BE_DISTINCT')
    for request in requests:
        if (request.get('purpose') != 'CPU_FIXTURE' or
                request.get('status') != 'EXACT_CPU_FIXTURE_REGISTERED_AFTER_AG4_RELEASE'):
            raise ValueError('POST_RELEASE_EXACT_CPU_REGISTRATION_REQUIRED')
        if not (0 < request['timeout_seconds'] <= 60):
            raise ValueError('BOUNDED_CPU_TIMEOUT_REQUIRED')
    output.mkdir(parents=True, exist_ok=False)
    children = []
    overlap = None
    interrupted = []
    previous = {s: signal.signal(s, lambda number, frame: interrupted.append(number))
                for s in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP)}
    failure = None
    shared = any('shared_cpu_registry' in request for request in requests)
    registry_path = output / 'GUARDS.json'
    registry = {'purpose': 'EXACT_TWO_CPU_ROOTS_NOT_SIMULATION',
                'manager': identity(os.getpid()), 'guards': []}
    def publish_registry():
        temp = registry_path.with_suffix('.tmp')
        temp.write_text(json.dumps(registry, indent=2) + '\n')
        os.replace(temp, registry_path)
    if shared:
        if not all(Path(r['shared_cpu_registry']).resolve() == registry_path for r in requests):
            raise ValueError('CPU_REGISTRY_DESTINATION_MISMATCH')
        publish_registry()
    try:
        for index, request in enumerate(requests):
            path = output / ('request-' + str(index) + '.json')
            write_new(path, request)
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            stdout = (output / ('guard-' + str(index) + '.stdout')).open('xb')
            stderr = (output / ('guard-' + str(index) + '.stderr')).open('xb')
            try:
                proc = subprocess.Popen(
                    [sys.executable, '-I', '-B', str(HERE / 'cpu_guard_entry.py'),
                     str(path), digest], stdin=subprocess.DEVNULL,
                    stdout=stdout, stderr=stderr, close_fds=True,
                    env={'PATH': '/usr/bin:/bin', 'LANG': 'C', 'LC_ALL': 'C',
                         'CUDA_VISIBLE_DEVICES': ''})
            finally:
                stdout.close()
                stderr.close()
            row = {'proc': proc, 'identity': None,
                   'pidfd': None, 'request': request,
                   'signal_sent': False}
            children.append(row)
            row['identity'] = identity(proc.pid)
            row['pidfd'] = os.pidfd_open(proc.pid)
            if shared:
                dest = Path(request['destination'])
                registry['guards'].append(dict(row['identity'],
                    request_path=str(path), request_sha256=digest,
                    argv=[sys.executable, '-I', '-B', str(HERE / 'cpu_guard_entry.py'), str(path), digest],
                    active_path=str(dest.parent / (dest.name + '.active.json'))))
                publish_registry()
        deadline = time.monotonic() + 75
        while any(row['proc'].poll() is None for row in children):
            if interrupted or time.monotonic() > deadline:
                failure = 'CPU_PARENT_INTERRUPTED_OR_BOUND_EXCEEDED'
                break
            observed = []
            for row in children:
                dest = Path(row['request']['destination'])
                active = dest.parent / (dest.name + '.active.json')
                if not active.is_file():
                    break
                value = json.loads(active.read_text())
                if (value['guard']['pid'] != row['identity']['pid'] or
                        value['guard']['start_ticks'] != row['identity']['start_ticks'] or
                        value['root']['ppid'] != row['identity']['pid'] or
                        not same(value['guard']) or not same(value['root'])):
                    break
                observed.append(value)
            if len(observed) == 2 and overlap is None:
                overlap = {'monotonic_ns': time.monotonic_ns(), 'roots': observed,
                           'classification': 'TWO_EVENT_CONFIRMED_ROOTS_OBSERVED_LIVE'}
                write_new(output / 'ACTUAL_OVERLAP.json', overlap)
            time.sleep(.025)
    except BaseException as exc:
        failure = repr(exc)
    finally:
        # Signal only direct children spawned here, via instance-bound pidfds.
        # Their handlers request the reused engine's event-proven cleanup.
        for row in children:
            if row['proc'].poll() is None and failure:
                try:
                    if row['pidfd'] is None:
                        # Still an unreaped direct Popen child if pidfd setup failed.
                        row['proc'].terminate()
                    else:
                        signal.pidfd_send_signal(row['pidfd'], signal.SIGTERM)
                except ProcessLookupError:
                    pass
                row['signal_sent'] = True
        for row in children:
            try:
                row['proc'].wait(timeout=5 if failure else 75)
            except subprocess.TimeoutExpired:
                failure = 'OWN_GUARD_CLEANUP_UNRESOLVED'
            finally:
                if row['pidfd'] is not None:
                    os.close(row['pidfd'])
        for number, handler in previous.items():
            signal.signal(number, handler)
    terminals = []
    for row in children:
        terminal = Path(row['request']['destination']) / 'TERMINAL.json'
        value = json.loads(terminal.read_text()) if terminal.is_file() else None
        terminals.append({'guard_identity': row['identity'],
                          'guard_returncode': row['proc'].poll(),
                          'guard_still_same_instance_live': (same(row['identity'])
                              if row['identity'] is not None else None),
                          'guard_signal_sent': row['signal_sent'],
                          'engine_terminal': value})
    complete = len(terminals) == 2 and overlap is not None and not failure
    for row in terminals:
        result = row['engine_terminal'] or {}
        complete = complete and (row['guard_returncode'] == 0 and
                    not row['guard_still_same_instance_live'] and
                    result.get('status') == 'PASS_GUARDED_NATURAL_EXIT0' and
                    result.get('owned_children_live') == 0 and
                    not result.get('unconfirmed_wait_pids') and
                    not result.get('ownership', {}).get('pending'))
    report = {'status': 'PASS_CPU_TWO_ROOT_LIFECYCLE_ONLY' if complete else 'CPU_INCOMPLETE',
              'failure': failure, 'actual_overlap': overlap, 'terminals': terminals,
              'simulation_starts': 0, 'performance_accepted': False,
              'production_authority_qualified': False,
              'missing': ['production cross-root observer negative controls',
                          'three exact external worker role admission',
                          'full dispatcher/ledger/family publication qualification']}
    write_new(output / 'CPU_RESULT.json', report)
    return report
