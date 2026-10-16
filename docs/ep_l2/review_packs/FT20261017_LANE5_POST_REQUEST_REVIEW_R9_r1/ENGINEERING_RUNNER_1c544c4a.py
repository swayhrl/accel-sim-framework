"""One authorized ENGINEERING_ONLY campaign. Default: read-only dry-run.

Lane5 owns the separate central admission adapter and one-use ledger. This
runner never patches the production driver, Registry.admission or shared JSON.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import fcntl
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import sys
import threading
import time

sys.dont_write_bytecode = True
GIB = 1024**3
CORE = 'c948184504d82b80e23eb3f4ff6cdfd328ba9355'
FRAMEWORK = '3ab150b3e99ff3ed759b8cdc5154cfb5744042a7'
VENDOR = 'f90c430c3a1ce8f08c09942a5a1c3a797bb2295b'
OFFICIAL_DRIVER_SHA = '9b9943c65d41b5776075d8488414b0c2f55b3dcab8a22801eab966397578a82c'
SHARED = Path('/workspace/ep_l2_ft20261016_shared')
REPOSITORY = Path(__file__).resolve().parents[3]
LANE5_REF = 'refs/remotes/origin/hrl/ep-l2-ft20261016-lane5-v1'
TARGETS = ['accel-sim.out', 'ep_l2_ft_memcpy_clock', 'ep_l2_ft_host_prefill',
           'ep_l2_ft_directed', 'ep_l2_ft_partition']
STOP_REQUESTED = threading.Event()


class Stop(RuntimeError):
    pass


def require(condition, reason):
    if not condition:
        raise Stop(reason)


def utc():
    return datetime.now(timezone.utc).isoformat()


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def write_json(path, data):
    path = Path(path)
    temporary = path.with_name('.' + path.name + '.new')
    with temporary.open('w') as stream:
        json.dump(data, stream, indent=2, allow_nan=False)
        stream.write('\n'); stream.flush(); os.fsync(stream.fileno())
    temporary.replace(path)


def git(*arguments, cwd=REPOSITORY):
    return subprocess.check_output(['git', *arguments], cwd=cwd, timeout=15,
                                   env=dict(os.environ, GIT_OPTIONAL_LOCKS='0'))


def boot_id():
    return Path('/proc/sys/kernel/random/boot_id').read_text().strip()


def process_info(pid):
    p = Path('/proc') / str(pid)
    raw = (p / 'stat').read_text()
    fields = raw[raw.rfind(')') + 2:].split()
    io = {}
    for line in (p / 'io').read_text().splitlines():
        key, value = line.split(':', 1); io[key] = int(value)
    return {'pid': pid, 'ppid': int(fields[1]), 'pgrp': int(fields[2]),
            'state': fields[0], 'start_ticks': int(fields[19]),
            'cpu_ticks': int(fields[11]) + int(fields[12]),
            'rss_bytes': int(fields[21]) * os.sysconf('SC_PAGE_SIZE'), 'io': io}


def processes(group=None, external=False, include_fd=False):
    rows = []
    for path in Path('/proc').iterdir():
        if not path.name.isdigit():
            continue
        try:
            if group is not None:
                raw = (path / 'stat').read_text()
                if int(raw[raw.rfind(')') + 2:].split()[2]) != group:
                    continue
            if external:
                exe = (path / 'exe').resolve(strict=True)
                if exe.name not in {'accel-sim.out', 'cc1plus', 'cc1', 'cmake', 'make', 'ninja'}:
                    continue
            row = process_info(int(path.name))
            if row['state'] == 'Z' or group is not None and row['pgrp'] != group:
                continue
            if external:
                row['executable'] = str(exe)
                row['command'] = (path / 'cmdline').read_bytes().replace(b'\0', b' ').decode(errors='replace')[:2000]
                if include_fd:
                    row['observed_fd_targets'] = []
                    for fd in list((path / 'fd').iterdir())[:64]:
                        try:
                            row['observed_fd_targets'].append(os.readlink(fd))
                        except FileNotFoundError:
                            pass
            rows.append(row)
        except (FileNotFoundError, ProcessLookupError):
            # A naturally completed process is not a reason to stop another job.
            continue
        except PermissionError as error:
            raise Stop('EXTERNAL_PROCESS_STATE_UNKNOWN') from error
    return rows


def available_memory():
    mem = {}
    for line in Path('/proc/meminfo').read_text().splitlines():
        key, value = line.split(':', 1)
        mem[key] = int(value.split()[0]) * 1024
    maximum = Path('/sys/fs/cgroup/memory.max').read_text().strip()
    current = int(Path('/sys/fs/cgroup/memory.current').read_text())
    return min(mem['MemAvailable'], int(maximum) - current) if maximum != 'max' else mem['MemAvailable']


def filesystem(path):
    p = Path(path); st = p.stat(); fs = os.statvfs(p)
    return {'path': str(p), 'realpath': str(p.resolve()), 'device': st.st_dev,
            'fsid': fs.f_fsid, 'block_bytes': fs.f_frsize,
            'available_bytes': fs.f_bavail * fs.f_frsize,
            'free_including_reserved_bytes': fs.f_bfree * fs.f_frsize,
            'total_bytes': fs.f_blocks * fs.f_frsize}


def allocated(roots):
    total, seen = 0, set()
    for root in roots:
        p = Path(root)
        if not p.exists():
            continue
        require(not p.is_symlink(), 'OUTPUT_ROOT_IS_SYMLINK')
        for directory, dirs, files in os.walk(p, followlinks=False):
            for entry in [Path(directory), *(Path(directory) / name for name in files)]:
                st = entry.lstat(); identity = (st.st_dev, st.st_ino)
                if identity not in seen:
                    seen.add(identity); total += st.st_blocks * 512
            dirs[:] = [name for name in dirs if not (Path(directory) / name).is_symlink()]
    return total


def no_symlink_path(path):
    p = Path(path)
    require(p.is_absolute(), 'ABSOLUTE_PATH_REQUIRED')
    for component in [p, *p.parents]:
        require(not component.is_symlink(), 'SYMLINK_IN_OUTPUT_PATH')


def audit_sources(request):
    require(request['identity']['core_source_commit'] == CORE, 'WRONG_CORE')
    require(request['identity']['framework_source_commit'] == FRAMEWORK, 'WRONG_FRAMEWORK')
    require(request['identity']['vendor_commit'] == VENDOR, 'WRONG_VENDOR')
    for name, commit in [('core', CORE), ('framework', FRAMEWORK), ('vendor', VENDOR)]:
        tree = request['source_paths'][name]
        require(git('rev-parse', 'HEAD', cwd=tree).decode().strip() == commit, 'SOURCE_HEAD_MISMATCH_' + name)
        require(not git('status', '--porcelain', '--untracked-files=no', cwd=tree), 'DIRTY_SOURCE_' + name)
    official = Path(request['source_paths']['framework']) / 'util/ep_l2/ft_lane1/build_r0_1.py'
    require(digest(official) == OFFICIAL_DRIVER_SHA, 'OFFICIAL_DRIVER_CHANGED')
    require(digest(__file__) == request['identity']['pilot_driver_sha256'], 'PILOT_DRIVER_CHANGED')
    source = git('show', request['identity']['driver_source_commit'] +
                 ':util/ep_l2/ft_lane1/engineering_pilot.py')
    require(hashlib.sha256(source).hexdigest() == request['identity']['pilot_driver_sha256'], 'PILOT_DRIVER_SOURCE_MISMATCH')
    for path, expected in request['input_sha256'].items():
        require(digest(path) == expected, 'INPUT_CHANGED_' + path)
    spec = importlib.util.spec_from_file_location('frozen_lane1_build', official)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    expected = [{'name': n, 'command': c} for n, c in
                module.repair_commands(Path(request['build_root']), Path(request['source_paths']['core']))]
    require(len(expected) == 21 and expected == request['planned_directed_commands'], 'DIRECTED_MATRIX_CHANGED')
    require(request['cmake_targets'] == TARGETS, 'CMAKE_TARGETS_CHANGED')
    return module


def validate_authorization(request, authorization, request_sha, now=None):
    now = time.time() if now is None else now
    require(authorization['schema_version'] == 'EPL2_ENGINEERING_PILOT_AUTHORIZATION_V1' and
            authorization['status'] == 'APPROVED_ENGINEERING_ONLY' and authorization['issuer'] == 'lane5', 'NOT_AUTHORIZED')
    require(authorization['authority_commit'] == '56a0517d3a5941a0a870b50e8c915a8a36b9ee5d', 'WRONG_AUTHORITY')
    for key in ('pilot_id', 'host', 'boot_id', 'execution_identity', 'execution_locations', 'output_roots'):
        require(authorization[key] == request[key], 'AUTHORIZATION_BINDING_' + key)
    require(authorization['request']['sha256'] == request_sha, 'REQUEST_DIGEST_MISMATCH')
    require(request['host'] == socket.gethostname() and request['boot_id'] == boot_id(), 'HOST_BOOT_MISMATCH')
    require(authorization['issued_at_unix'] <= now < authorization['expires_at_unix'], 'AUTHORIZATION_TTL')
    require(authorization['cpu_units'] == 2 and authorization['memory_bytes'] == 8 * GIB, 'RESOURCE_QUOTA_CHANGED')
    require(0 < authorization['max_duration_seconds'] <= request['max_duration_seconds'], 'TIME_CAP_CHANGED')
    require(0 < authorization['monitor_interval_seconds'] <= 2, 'MONITOR_INTERVAL')
    require(authorization['scientific_use'] == 'FORBIDDEN_ENGINEERING_EVIDENCE_ONLY', 'SCIENTIFIC_PROMOTION_PROHIBITED')
    require(set(authorization['filesystems']) == set(request['proposed_envelope']), 'FILESYSTEM_SET_CHANGED')
    for name, caps in authorization['filesystems'].items():
        required = ('entry_free_bytes', 'hard_stop_free_bytes', 'max_pilot_allocated_growth_bytes',
                    'external_write_reserve_bytes', 'monitor_and_kill_overshoot_bytes',
                    'minimum_untouched_emergency_bytes')
        require(all(type(caps[k]) is int and caps[k] > 0 for k in required), 'NONPOSITIVE_BUDGET')
        needed = sum(caps[k] for k in required[2:])
        require(caps['entry_free_bytes'] >= needed, 'INSUFFICIENT_ENVELOPE_' + name)
        require(caps['hard_stop_free_bytes'] >= caps['minimum_untouched_emergency_bytes'] +
                caps['monitor_and_kill_overshoot_bytes'], 'STOP_DOES_NOT_PROTECT_EMERGENCY')
        require(caps['entry_free_bytes'] > caps['hard_stop_free_bytes'], 'NO_ENTRY_STOP_MARGIN')
        proposed = request['proposed_envelope'][name]
        require(caps['max_pilot_allocated_growth_bytes'] <= proposed['max_pilot_allocated_growth_bytes'], 'GROWTH_CAP_EXPANDED')
        require(caps['hard_stop_free_bytes'] >= proposed['hard_stop_free_bytes'], 'STOP_MARGIN_REDUCED')
        for key in ('external_write_reserve_bytes', 'monitor_and_kill_overshoot_bytes',
                    'minimum_untouched_emergency_bytes'):
            require(caps[key] >= proposed[key], 'REQUESTED_RESERVE_REDUCED_' + key)


class Lane5PilotAdapter:
    """Thin caller bridge to the published Lane5 API; never register or amend."""
    def __init__(self, api, module, request_bytes, authorization):
        self.api = api; self.module = module; self.request_bytes = request_bytes
        self.request = json.loads(request_bytes); self.authorization = authorization

    def claim(self, request, authorization, observed):
        require(request == self.request and authorization == self.authorization, 'ADAPTER_INPUT_CHANGED')
        measured = self.module.measure_execution_identity(request['execution_locations'])
        key = self.api.claim(authorization, self.request_bytes, measured)
        return {'lease_id': key, 'owner': 'lane1', 'pilot_id': request['pilot_id']}

    def record_process(self, key, pilot_id, identity, child=None):
        require(pilot_id == self.request['pilot_id'] and child is not None, 'DIRECT_CHILD_REQUIRED')
        self.api.attach_process(key, self.authorization, child)

    def heartbeat(self, key, pilot_id, observed):
        require(pilot_id == self.request['pilot_id'], 'PILOT_ID_CHANGED')
        check = self.api.monitor(key, self.authorization)
        require(not check['stop'], 'LANE5_STOP_LATCHED: ' + '; '.join(check['reasons']))

    def finish(self, key, pilot_id, report):
        require(pilot_id == self.request['pilot_id'], 'PILOT_ID_CHANGED')
        terminal = report['status']
        require(terminal == 'COMPLETE_ENGINEERING_ONLY' or terminal.startswith('PILOT_STOPPED_'), 'INVALID_TERMINAL')
        directory = Path(self.request['audit_control_root']); no_symlink_path(directory)
        path = directory / 'PRE_RELEASE_ENGINEERING_RECEIPT.json'
        report['pre_release_receipt_path'] = str(path)
        raw = (json.dumps(report, indent=2, allow_nan=False) + '\n').encode()
        receipt_sha = hashlib.sha256(raw).hexdigest()
        try:
            directory.mkdir(parents=True, exist_ok=True)
            with path.open('xb') as stream:
                stream.write(raw); stream.flush(); os.fsync(stream.fileno())
        except OSError as error:
            report['pre_release_journal_error'] = repr(error)
            print(raw.decode(), file=sys.stderr, flush=True)
        # Release is attempted even when the result filesystem/journal failed.
        self.api.release(key, self.authorization, terminal, receipt_sha)
        report['central_lease_receipt_sha256'] = receipt_sha


def load_adapter(request, authorization, publication, authorization_file_sha256, request_bytes):
    # The independent Lane5 branch and central client binding must both agree.
    require(publication and len(publication) == 40, 'MISSING_LANE5_PUBLICATION')
    subprocess.run(['git', 'merge-base', '--is-ancestor', publication, LANE5_REF],
                   cwd=REPOSITORY, check=True, timeout=15)
    auth_path = 'docs/ep_l2/codex_handoff/fast_track_2026_10_16_v1/lane5/LOW_SPACE_PILOT_AUTHORIZATION.json'
    published = git('show', publication + ':' + auth_path)
    require(hashlib.sha256(published).hexdigest() == authorization_file_sha256, 'FORGED_AUTHORIZATION')
    client = json.loads((SHARED / 'CLIENT_CONTRACT.json').read_text())
    module_path = client.get('engineering_pilot_module')
    require(module_path is not None, 'LANE5_PILOT_ADAPTER_NOT_PUBLISHED')
    expected = request['lane5_api_dependency']
    require(client['engineering_pilot_source_commit'] == expected['module_source_commit'] and
            client['engineering_pilot_module_sha256'] == expected['module_sha256'] and
            client['registry_client_sha256'] == expected['registry_client_sha256'], 'LANE5_API_REVISION_REQUIRES_REQUEST_REBIND')
    require(digest(module_path) == client['engineering_pilot_module_sha256'], 'ADAPTER_CONTENT_CHANGED')
    data = git('show', client['engineering_pilot_source_commit'] + ':util/ep_l2/ft_lane5/engineering_pilot.py')
    require(hashlib.sha256(data).hexdigest() == client['engineering_pilot_module_sha256'], 'ADAPTER_SOURCE_MISMATCH')
    subprocess.run(['git', 'merge-base', '--is-ancestor', client['engineering_pilot_source_commit'], LANE5_REF],
                   cwd=REPOSITORY, check=True, timeout=15)
    for path_key, hash_key in [('registry_client', 'registry_client_sha256'),
                               ('runner', 'runner_sha256'), ('acceptance_module', 'acceptance_module_sha256')]:
        require(digest(client[path_key]) == client[hash_key], 'LANE5_DEPENDENCY_CHANGED_' + path_key)
    sys.path.insert(0, str(Path(module_path).parent))
    spec = importlib.util.spec_from_file_location('lane5_engineering_adapter', module_path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    module.validate(authorization, request_bytes)
    return Lane5PilotAdapter(module.PilotRegistry(SHARED), module, request_bytes, authorization)


def observation(request, group=None):
    rows = processes(group=group) if group is not None else []
    fs = {}
    for name, item in request['filesystems'].items():
        fs[name] = filesystem(item['path'])
        fs[name]['pilot_allocated_bytes'] = allocated(item['owned_roots'])
    external = [r for r in processes(external=True) if r['pgrp'] != group]
    return {'utc': utc(), 'monotonic': time.monotonic(), 'filesystems': fs,
            'external_processes': external,
            'available_memory_bytes': available_memory(), 'owned_processes': rows,
            'owned_rss_bytes': sum(r['rss_bytes'] for r in rows),
            'owned_cpu_ticks': sum(r['cpu_ticks'] for r in rows)}


def check_resources(request, authorization, initial, current, entry=False):
    floor = 64 * GIB + (8 * GIB if entry else 0)
    require(current['available_memory_bytes'] >= floor, 'MEMORY_SAFETY_FLOOR')
    require(current['owned_rss_bytes'] <= 8 * GIB, 'OWN_RSS_CAP')
    for name, item in current['filesystems'].items():
        before = initial['filesystems'][name]; caps = authorization['filesystems'][name]
        require((item['device'], item['fsid']) == (before['device'], before['fsid']), 'FILESYSTEM_ID_CHANGED')
        require((item['device'], item['fsid']) ==
                (request['filesystems'][name]['device'], request['filesystems'][name]['fsid']), 'REQUEST_FILESYSTEM_ID_CHANGED')
        floor = caps['entry_free_bytes'] if entry else caps['hard_stop_free_bytes']
        require(item['available_bytes'] > floor if not entry else item['available_bytes'] >= floor, 'DISK_STOP_' + name)
        own_growth = max(0, item['pilot_allocated_bytes'] - before['pilot_allocated_bytes'])
        require(own_growth <= caps['max_pilot_allocated_growth_bytes'], 'OWN_GROWTH_CAP_' + name)
        # Net contraction is an observable stop trigger, NOT a gross external IO bound.
        net_external = max(0, before['available_bytes'] - item['available_bytes'] - own_growth)
        require(net_external <= caps['external_write_reserve_bytes'], 'EXTERNAL_NET_GROWTH_CAP_' + name)


def stop_owned_group(process):
    if process is None:
        return
    members = processes(group=process.pid)
    if not members:
        process.poll(); return
    expected = getattr(process, '_pilot_start_ticks', None)
    if expected is not None:
        try:
            require(process_info(process.pid)['start_ticks'] == expected, 'OWN_PROCESS_IDENTITY_CHANGED')
        except FileNotFoundError:
            known = getattr(process, '_pilot_known_members', {})
            require(any(known.get(r['pid']) == r['start_ticks'] for r in members), 'OWN_GROUP_IDENTITY_UNKNOWN')
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    deadline = time.monotonic() + 3
    while time.monotonic() < deadline:
        process.poll()
        if not processes(group=process.pid):
            return
        time.sleep(0.05)
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    process.wait(timeout=5)


def child_launcher(command, cpus, maximum_file_bytes):
    # Avoid preexec_fn in a process that also runs the monitor watchdog thread.
    code = ('import json,os,resource,sys; '
            'os.sched_setaffinity(0,json.loads(sys.argv[1])); '
            'os.setpriority(os.PRIO_PROCESS,0,10); '
            'resource.setrlimit(resource.RLIMIT_CORE,(0,0)); '
            'n=int(sys.argv[2]); resource.setrlimit(resource.RLIMIT_FSIZE,(n,n)); '
            'os.execvpe(sys.argv[3],sys.argv[3:],os.environ)')
    return [sys.executable, '-c', code, json.dumps(cpus), str(maximum_file_bytes), *command]


def monitored_command(command, name, request, authorization, adapter, lease,
                      baseline, campaign_start, report, out, environment):
    log = out / (name + '.log')
    record = {'name': name, 'command': command, 'started_at': utc(), 'log': str(log)}
    report['commands'].append(record)
    process = None; completed = threading.Event(); stalled = threading.Event()
    last_sample = [time.monotonic()]
    def watchdog():
        while not completed.wait(0.1):
            if time.monotonic() - last_sample[0] > 2:
                stalled.set(); stop_owned_group(process); return
    try:
        cpus = sorted(os.sched_getaffinity(0))[:2]
        require(len(cpus) == 2, 'INSUFFICIENT_CPU_AFFINITY')
        adapter.heartbeat(lease['lease_id'], request['pilot_id'], observation(request))
        with log.open('x') as stream:
            last_sample[0] = time.monotonic()
            record['launch_command'] = child_launcher(command, cpus, request['max_single_file_bytes'])
            process = subprocess.Popen(record['launch_command'], cwd=out, env=environment,
                stdout=stream, stderr=subprocess.STDOUT, start_new_session=True)
            record['process'] = process_info(process.pid)
            process._pilot_start_ticks = record['process']['start_ticks']
            process._pilot_known_members = {process.pid: process._pilot_start_ticks}
            record['process']['boot_id'] = boot_id(); record['cpu_affinity'] = cpus
            thread = threading.Thread(target=watchdog, daemon=True); thread.start()
            adapter.record_process(lease['lease_id'], request['pilot_id'], record['process'], child=process)
            with (out / 'RESOURCE_SAMPLES.jsonl').open('a') as samples:
                while True:
                    current = observation(request, process.pid)
                    process._pilot_known_members.update({r['pid']: r['start_ticks'] for r in current['owned_processes']})
                    require(not stalled.is_set(), 'MONITOR_STALLED')
                    require(not STOP_REQUESTED.is_set(), 'OWNER_REQUESTED_STOP')
                    require(time.time() < authorization['expires_at_unix'], 'AUTHORIZATION_EXPIRED')
                    require(time.monotonic() - campaign_start < authorization['max_duration_seconds'], 'CAMPAIGN_TIMEOUT')
                    check_resources(request, authorization, baseline, current)
                    require(sum(p.stat().st_size for p in out.glob('*.log')) <= request['max_logical_log_bytes'], 'LOG_BYTES_CAP')
                    # Lane5 rechecks the central permanent-lock authority/lease.
                    adapter.heartbeat(lease['lease_id'], request['pilot_id'], current)
                    samples.write(json.dumps(current, separators=(',', ':')) + '\n'); samples.flush()
                    update_peaks(report, current, baseline)
                    write_json(out / 'ENGINEERING_BUILD_RECEIPT.json', report)
                    last_sample[0] = time.monotonic()
                    if process.poll() is not None:
                        break
                    time.sleep(min(0.2, authorization['monitor_interval_seconds'] / 4))
            require(not processes(group=process.pid), 'OWN_DESCENDANT_STILL_RUNNING')
            require(process.returncode == 0, 'COMMAND_FAILED_' + name)
        return record
    except BaseException as error:
        record['error'] = repr(error)
        raise
    finally:
        completed.set()
        if process is not None:
            stop_owned_group(process); process.wait(timeout=5)
            record['exit_code'] = process.returncode
        if log.exists():
            record['log_sha256'] = digest(log)
        record['finished_at'] = utc()
        write_json(out / 'ENGINEERING_BUILD_RECEIPT.json', report)


def update_peaks(report, current, baseline):
    peak = report.setdefault('sampled_high_water', {'owned_rss_bytes': 0, 'filesystems': {}})
    peak['owned_rss_bytes'] = max(peak['owned_rss_bytes'], current['owned_rss_bytes'])
    peak['minimum_available_memory_bytes'] = min(peak.get('minimum_available_memory_bytes',
        current['available_memory_bytes']), current['available_memory_bytes'])
    for name, row in current['filesystems'].items():
        first = baseline['filesystems'][name]
        item = peak['filesystems'].setdefault(name, {'maximum_allocated_growth_bytes': 0,
                                                    'minimum_available_bytes': row['available_bytes']})
        item['maximum_allocated_growth_bytes'] = max(item['maximum_allocated_growth_bytes'],
            row['pilot_allocated_bytes'] - first['pilot_allocated_bytes'])
        item['minimum_available_bytes'] = min(item['minimum_available_bytes'], row['available_bytes'])


def execute(request, request_sha, authorization, adapter, module):
    original_affinity = os.sched_getaffinity(0)
    require(len(original_affinity) >= 2, 'INSUFFICIENT_CPU_AFFINITY')
    baseline = observation(request)
    check_resources(request, authorization, baseline, baseline, entry=True)
    require(baseline['filesystems']['workspace']['available_bytes'] < 50 * GIB,
            'FORMAL_ENTRY_AVAILABLE_CANCEL_PILOT')
    build = Path(request['build_root']); out = Path(request['output_root'])
    for p in (build, out):
        no_symlink_path(p); require(not p.exists(), 'PRIOR_OUTPUT_MUST_BE_PRESERVED')
    require(not Path(request['cancellation_marker_path']).exists(), 'PILOT_ALREADY_CANCELLED')
    lease = adapter.claim(request, authorization, baseline)
    report = {'status': 'ENGINEERING_ONLY_STARTING', 'classification': 'ENGINEERING_ONLY',
        'pilot_id': request['pilot_id'], 'request_sha256': request_sha, 'identity': request['identity'],
        'runtime_ready': False, 'independent_qualification': False, 'formal_binary_sha256': None,
        'engineering_binary_sha256': None, 'commands': [], 'lease': lease,
        'started_at': utc(), 'initial_resources': baseline, 'application_runs': 0,
        'accepted_scientific_pairs': 0, 'pilot_source_paths': request['source_paths']}
    start = time.monotonic()
    try:
        # Include the monitor/controller in the same two-CPU physical envelope.
        os.sched_setaffinity(0, sorted(original_affinity)[:2])
        report['runner_cpu_affinity'] = sorted(os.sched_getaffinity(0))
        require(lease['owner'] == 'lane1' and lease['pilot_id'] == request['pilot_id'], 'BAD_LEASE_IDENTITY')
        require(not Path(request['cancellation_marker_path']).exists(), 'PILOT_ALREADY_CANCELLED')
        after_lease = observation(request)
        check_resources(request, authorization, baseline, after_lease, entry=True)
        require(after_lease['filesystems']['workspace']['available_bytes'] < 50 * GIB,
                'FORMAL_ENTRY_AVAILABLE_CANCEL_PILOT')
        # The adapter must hold the unique central lease, not a private lock only.
        adapter.heartbeat(lease['lease_id'], request['pilot_id'], observation(request))
        build.mkdir(parents=True, exist_ok=False); out.mkdir(parents=True, exist_ok=False)
        temporary = build / 'tmp'; temporary.mkdir()
        environment = dict(os.environ, GPGPUSIM_ROOT=request['source_paths']['core'],
            CUDA_INSTALL_PATH='/usr/local/cuda-11.8', ACCELSIM_CONFIG='release',
            PATH='/usr/local/cuda-11.8/bin:' + os.environ['PATH'],
            OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1',
            TMPDIR=str(temporary), TMP=str(temporary), TEMP=str(temporary), CCACHE_DISABLE='1',
            CUDA_CACHE_DISABLE='1', PYTHONDONTWRITEBYTECODE='1', GIT_OPTIONAL_LOCKS='0')
        commands = [('configure', ['cmake', '-S', str(Path(request['source_paths']['framework']) / 'gpu-simulator'),
                     '-B', str(build), '-G', 'Unix Makefiles', '-DCUDAToolkit_ROOT=/usr/local/cuda-11.8']),
                    ('build', ['cmake', '--build', str(build), '--target', *TARGETS, '-j2']),
                    *module.repair_commands(build, Path(request['source_paths']['core']))]
        report['planned_commands'] = commands
        for name, command in commands:
            audit_sources(request)
            if name not in ('configure', 'build'):
                flags = list(build.rglob('flags.make'))
                require(flags and all('-DNDEBUG' not in p.read_text() for p in flags), 'ASSERTIONS_DISABLED')
                report.setdefault('test_executable_sha256', {})[command[0]] = digest(command[0])
            report['status'] = 'ENGINEERING_ONLY_' + name.upper()
            monitored_command(command, name, request, authorization, adapter, lease,
                              baseline, start, report, out, environment)
            if name == 'build':
                report['engineering_binary_sha256'] = digest(build / 'accel-sim.out')
                report['engineering_binary_path'] = str(build / 'accel-sim.out')
        audit_sources(request)
        binary = build / 'accel-sim.out'; report['engineering_binary_sha256'] = digest(binary)
        report['engineering_binary_path'] = str(binary)
        report['framework_build_stamp'] = (build / 'accelsim_version.h').read_text()
        report['compile_commands_sha256'] = digest(build / 'compile_commands.json')
        report['status'] = 'COMPLETE_ENGINEERING_ONLY'
    except BaseException as error:
        report['status'] = 'PILOT_STOPPED_' + (str(error) if isinstance(error, Stop) else type(error).__name__)
        report['error'] = repr(error)
    finally:
        report['finished_at'] = utc(); report['wall_seconds'] = time.monotonic() - start
        try:
            report['final_resources'] = observation(request)
        except BaseException as error:
            report['final_monitor_error'] = repr(error)
            report['status'] = 'PILOT_STOPPED_FINAL_MONITOR_FAILED'
        try:
            adapter.finish(lease['lease_id'], request['pilot_id'], report)
            report['lease_released_token_consumed'] = True
        except BaseException as error:
            report['lease_release_error'] = repr(error)
            report['status'] = 'PILOT_STOPPED_LEASE_RELEASE_REQUIRES_LANE5'
        os.sched_setaffinity(0, original_affinity)
        try:
            if out.is_dir():
                write_json(out / 'ENGINEERING_BUILD_RECEIPT.json', report)
            else:
                print(json.dumps(report, indent=2))
        except OSError as error:
            print(json.dumps({'receipt_write_error': repr(error), 'receipt': report}), file=sys.stderr)
    return report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--request', type=Path, required=True)
    p.add_argument('--pilot-id', required=True)
    p.add_argument('--authorization', type=Path)
    p.add_argument('--authorization-publication')
    p.add_argument('--execute-once', action='store_true')
    args = p.parse_args(); raw_request = args.request.read_bytes()
    request = json.loads(raw_request); request_sha = hashlib.sha256(raw_request).hexdigest()
    require(args.pilot_id == request['pilot_id'], 'PILOT_ID_MISMATCH')
    module = audit_sources(request)
    require(request['host'] == socket.gethostname() and request['boot_id'] == boot_id(), 'HOST_BOOT_MISMATCH')
    observed = observation(request)
    if not args.execute_once:
        print(json.dumps({'status': 'DRY_RUN_NO_LEASE_NO_COMPILER', 'classification': 'ENGINEERING_ONLY',
            'pilot_id': args.pilot_id, 'resources': observed,
            'production_directed_count': len(module.repair_commands(Path(request['build_root']), Path(request['source_paths']['core']))),
            'authorization_present': args.authorization is not None}, indent=2))
        return
    require(args.authorization is not None, 'LANE5_AUTHORIZATION_REQUIRED')
    authorization = json.loads(args.authorization.read_text())
    validate_authorization(request, authorization, request_sha)
    adapter = load_adapter(request, authorization, args.authorization_publication, digest(args.authorization), raw_request)
    with (SHARED / 'LANE1_BUILD_EXECUTION.lock').open('a+') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        require(digest(args.request) == request_sha, 'REQUEST_CHANGED_DURING_PREFLIGHT')
        report = execute(request, request_sha, authorization, adapter, module)
    print(json.dumps({k: report[k] for k in ('status', 'engineering_binary_sha256', 'runtime_ready')}, indent=2))
    require(report['status'] == 'COMPLETE_ENGINEERING_ONLY', 'ENGINEERING_CAMPAIGN_DID_NOT_COMPLETE')


if __name__ == '__main__':
    signal.signal(signal.SIGTERM, lambda *args: STOP_REQUESTED.set())
    signal.signal(signal.SIGINT, lambda *args: STOP_REQUESTED.set())
    main()
