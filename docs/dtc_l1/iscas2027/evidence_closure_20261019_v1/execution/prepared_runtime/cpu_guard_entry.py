"""PREPARED_NOT_TESTED. One CPU root per process; no simulator entrypoint.

Not authorized for execution while AG4's same-container gate is closed.
Invoked only by the later registered CPU qualifier, after exact source/file
and runtime-manifest binding. No matrix, performance UUID or dispatch loop.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import signal
import shutil
import sys
import time

HERE = Path(__file__).resolve().parent
RAW = Path('/workspace/dtc-evidence-closure-20261019-v1/coordinator')


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('request', type=Path)
    parser.add_argument('request_sha256')
    args = parser.parse_args()
    if digest(args.request) != args.request_sha256:
        raise ValueError('CPU_REQUEST_CHANGED')
    request = json.loads(args.request.read_text())
    if request['purpose'] != 'CPU_FIXTURE':
        raise ValueError('CPU_ENTRY_CANNOT_START_SIMULATOR')
    if request['status'] != 'EXACT_CPU_FIXTURE_REGISTERED_AFTER_AG4_RELEASE':
        raise ValueError('CPU_RELEASE_AND_ROLE_REGISTRATION_REQUIRED')
    destination = Path(request['destination']).resolve()
    if not destination.is_relative_to(RAW / 'cpu-qualification'):
        raise ValueError('CPU_DESTINATION_NOT_ISOLATED')
    for relative, sha in request['prepared_source_sha256'].items():
        path = (HERE / relative).resolve()
        if not path.is_relative_to(HERE) or digest(path) != sha:
            raise ValueError('PREPARED_CPU_SOURCE_CHANGED:' + relative)
    required = {'cpu_guard_entry.py', 'vendor/common.py',
                'vendor/guarded_process.py', 'vendor/ownership.py',
                'vendor/mapping_roles.py', 'vendor/oom_watchdog.py'}
    if not required <= set(request['prepared_source_sha256']):
        raise ValueError('CPU_ENGINE_SOURCE_CLOSURE_INCOMPLETE')
    manifests_path = Path(request['manifests_path'])
    if digest(manifests_path) != request['manifests_sha256']:
        raise ValueError('CPU_MAPPING_MANIFEST_CHANGED')
    manifests = json.loads(manifests_path.read_text())
    # Import only the exact prepared engine whose file identities were checked.
    sys.path.insert(0, str(HERE / 'vendor'))
    from guarded_process import run_guarded
    from ownership import identity
    from common import write
    interrupted = []
    previous = {s: signal.signal(s, lambda number, frame: interrupted.append(number))
                for s in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP)}
    active = destination.parent / (destination.name + '.active.json')
    last = [0.0]
    shared = [None]
    if 'shared_cpu_registry' in request:
        sys.path.insert(0, str(HERE))
        from legacy_authority_runtime import bind_frozen_procedures
        from shared_cpu_context import CPUContext
        from shared_authority import bind_current_review
        proc, _, _ = bind_frozen_procedures()
        context = CPUContext(request, identity, proc)
        shared[0] = context

    def observe(pid, full, ownership):
        if interrupted:
            return 'CPU_COORDINATOR_SIGNAL:' + str(interrupted[0])
        if shutil.disk_usage(destination).free <= 5 * 1024**3:
            return 'USER_DISK_FLOOR_AT_OR_BELOW_5GiB'
        used = sum(p.stat().st_size for p in destination.rglob('*') if p.is_file())
        if used > request['output_bound_bytes']:
            return 'CPU_REGISTERED_OUTPUT_BOUND_EXCEEDED'
        available = next(int(line.split()[1]) * 1024
                         for line in Path('/proc/meminfo').read_text().splitlines()
                         if line.startswith('MemAvailable:'))
        maximum = Path('/sys/fs/cgroup/memory.max').read_text().strip()
        current = int(Path('/sys/fs/cgroup/memory.current').read_text())
        headroom = int(maximum) - current if maximum != 'max' else available
        if min(available, headroom) < 8 * 1024**3:
            return 'CPU_RUNTIME_MEMORY_BELOW_8GiB'
        if time.monotonic() - last[0] >= .1:
            own = ownership.same(pid) if pid in ownership.confirmed else None
            row = {'guard': identity(os.getpid()), 'root': own,
                   'ownership': ownership.snapshot(),
                   'monotonic_ns': time.monotonic_ns(),
                   'status': 'CPU_LIFECYCLE_ONLY_NOT_AUTHORITY_ADMISSION'}
            temp = active.with_suffix('.tmp')
            write(temp, row)
            os.replace(temp, active)
            last[0] = time.monotonic()
        if shared[0] is not None and full:
            from shared_authority import bind_current_review
            if not hasattr(observe, 'shared_review'):
                context = shared[0]
                observe.shared_review = bind_current_review(
                    ownership, identity, context.peers, project_CPU_tracees=True,
                    exact_controller_roles_provider=context.controller_roles)
            snapshot, verdict = observe.shared_review(identity(os.getpid()))
            with (destination / 'SHARED_AUTHORITY.jsonl').open('a') as stream:
                stream.write(json.dumps(verdict) + '\n')
            if verdict['status'] == 'STOP_AUTHORITY_NOT_CLOSED':
                return 'CPU_SHARED_AUTHORITY_NOT_CLOSED'
        return None

    try:
        result = run_guarded(request['argv'], request['environment'], manifests,
                             destination, 'CPU_FIXTURE',
                             request['timeout_seconds'], observer=observe)
        print(json.dumps(result), flush=True)
        return 0 if result['status'] == 'PASS_GUARDED_NATURAL_EXIT0' else 1
    finally:
        for number, handler in previous.items():
            signal.signal(number, handler)


if __name__ == '__main__':
    sys.exit(main())
