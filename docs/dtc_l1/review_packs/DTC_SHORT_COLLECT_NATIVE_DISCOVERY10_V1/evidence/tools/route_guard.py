"""Short-Collect candidate preflight and runtime safety. Import is inert.

Fresh true164 and peer checks occur before the registry EX transaction. The
10-second runtime sampler reads local proc/statvfs only and never FUSE.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import time

from route_authority import BINARY, CORE, FRAMEWORK, LIB, Hold, need, read, sha

GIB = 1024 ** 3
MIB = 1024 ** 2
TRUE164 = 'admin-wcx@10.208.130.164:/home/shared'
TERMINAL = {'COMPLETE', 'CLOSED', 'STOP_UNACCEPTED', 'COMPAT_PARTIAL_COMPLETE'}


def _bounded_json(argv, timeout=5):
    try:
        return json.loads(subprocess.check_output(argv, text=True, timeout=timeout))
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, json.JSONDecodeError) as exc:
        raise Hold('BOUNDED_RESOURCE_OR_MOUNT_QUERY_HOLD') from exc


def verify_runtime(spec):
    need(spec['core_commit'] == CORE and spec['framework_commit'] == FRAMEWORK,
         'FROZEN_SOURCE_DRIFT')
    need(spec['binary_sha256'] == BINARY and spec['libcudart_sha256'] == LIB,
         'FROZEN_BINARY_OR_LIB_DRIFT')
    binding_path = Path(spec['runtime_binding_path'])
    need(sha(binding_path) == spec['runtime_sha256'], 'RUNTIME_BINDING_SHA_DRIFT')
    binding = read(binding_path)
    need(binding['candidate_core'] == CORE and binding['framework_commit'] == FRAMEWORK,
         'RUNTIME_BINDING_SOURCE_DRIFT')
    files = {row['role']: row for row in binding['runtime_files']}
    need(set(files) == {'binary', 'libcudart', 'loader', 'strace'},
         'EXACT_RUNTIME_MEMBERS_REQUIRED')
    for role, key in [('binary', 'binary'), ('libcudart', 'libcudart'), ('loader', 'loader')]:
        path = Path(spec[key + '_path'])
        need(path.resolve() == Path(files[role]['realpath']).resolve()
             and sha(path) == spec[key + '_sha256'] == files[role]['sha256'],
             'RUNTIME_FILE_DRIFT:' + role)
    need(sha(files['strace']['realpath']) == files['strace']['sha256'],
         'STRACE_SHA_DRIFT')
    need(spec['native_simulator_argv'][0] == spec['binary_path'], 'ARGV_BINARY_DRIFT')
    need(len(spec['expected_options']) == spec['expected_options_count'] == 271,
         'EFFECTIVE_OPTIONS_271_REQUIRED')
    need(spec['expected_options']['-gpgpu_dtc_l1_short_collect_first'] ==
         (['1'] if spec['mode'] == 'ON' else ['0']), 'CANDIDATE_SWITCH_DRIFT')
    for path in spec['config_paths']:
        need(sha(path) == spec['config_sha256'][path], 'CONFIG_SHA_DRIFT:' + path)
    need(set(spec['config_paths']) == set(spec['native_simulator_argv'][i + 1]
         for i, item in enumerate(spec['native_simulator_argv'][:-1]) if item == '-config'),
         'ARGV_CONFIG_SET_DRIFT')
    return {'status': 'FROZEN_RUNTIME_AND_OPTIONS_PASS', 'runtime_binding_sha256': sha(binding_path),
            'binary_sha256': BINARY, 'libcudart_sha256': LIB,
            'options': 271, 'candidate_switch': spec['mode']}


def verify_input(spec):
    binding_path = Path(spec['input_binding_path'])
    need(sha(binding_path) == spec['input_binding_sha256'], 'INPUT_BINDING_SHA_DRIFT')
    binding = read(binding_path)
    q = binding['qualification']
    need(q['status'] == 'BODY_COMPLETE_SHA_AND_BASIC_FORMAT_PASS' and not q['issues'],
         'FROZEN_INPUT_BODY_QUALIFICATION_HOLD')
    need(binding['input_digest'] == spec['input_sha256'] == spec['input_digest'],
         'INPUT_DIGEST_DRIFT')
    trace = Path(spec['trace_entry'])
    need(str(trace) == q['trace_entry'] and sha(trace) == spec['trace_kernelslist_sha256'],
         'TRACE_COMMANDLIST_SHA_DRIFT')
    mount = _bounded_json(['findmnt', '-J', '-T', str(trace)])['filesystems'][0]
    need(mount['fstype'] == 'fuse.sshfs' and mount['source'] == TRUE164,
         'GENUINE164_TRACE_MOUNT_REQUIRED')
    for row in q['rows']:
        path = Path(row['path'])
        st = path.stat()
        need([st.st_size, st.st_mtime_ns] == row['full_SHA_current_size_mtime'],
             'TRACE_MEMBER_CURRENT_IDENTITY_DRIFT')
        with path.open('rb') as stream:
            need(bool(stream.read(1)), 'TRACE_MEMBER_UNREADABLE')
    return {'status': 'FROZEN_FULL_BODY_SHA_BOUND_GENUINE164_INPUT',
            'input_digest': spec['input_digest'], 'kernels': len(q['rows']),
            'binding_sha256': sha(binding_path)}


def local_sample(root):
    root = Path(root)
    v = os.statvfs(root)
    mem = int(next(line.split()[1] for line in Path('/proc/meminfo').read_text().splitlines()
                   if line.startswith('MemAvailable:'))) * 1024
    cur = int(Path('/sys/fs/cgroup/memory.current').read_text())
    max_text = Path('/sys/fs/cgroup/memory.max').read_text().strip()
    maximum = None if max_text == 'max' else int(max_text)
    return {'observed_unix': time.time(), 'native_free_bytes': v.f_bavail * v.f_frsize,
            'native_free_inodes': v.f_favail, 'host_MemAvailable_bytes': mem,
            'cgroup_current_bytes': cur, 'cgroup_max_bytes': maximum,
            'cpu_allowed': sorted(os.sched_getaffinity(0)), 'true164_queries': 0,
            'registry_queries': 0}


def peer_reservation(registry, own_request):
    rows = []
    for key, row in registry['registered_future_requests'].items():
        if key == own_request or row.get('state') in TERMINAL:
            continue
        amount = row.get('reserved_write_bytes')
        need(type(amount) is int and amount >= 0, 'UNKNOWN_ACTIVE_PEER_WRITE_RESERVATION')
        rows.append({'request': key, 'reserved_write_bytes': amount})
    return rows


def archive_capacity(archive_root, needed_bytes):
    archive_root = Path(archive_root)
    need(archive_root.is_relative_to(Path('/root/share/mnt164')),
         'ARCHIVE_OUTSIDE_TRUE164_MOUNT')
    mount = _bounded_json(['findmnt', '-J', '-T', str(archive_root)])['filesystems'][0]
    need(mount['fstype'] == 'fuse.sshfs' and mount['source'] == TRUE164,
         'TRUE164_ARCHIVE_MOUNT_REQUIRED')
    code = ('import os,json,sys;v=os.statvfs(sys.argv[1]);'
            'print(json.dumps({"free_bytes":v.f_bavail*v.f_frsize}))')
    free = _bounded_json(['/usr/bin/python3', '-c', code, str(archive_root)])['free_bytes']
    need(free > needed_bytes + GIB, 'TRUE164_ARCHIVE_CAPACITY_HOLD')
    return {'status': 'TRUE164_CAPACITY_PASS', 'mount': mount['source'],
            'free_bytes': free, 'required_bytes': needed_bytes + GIB}


def preflight(spec, store, root, archive_root, request):
    runtime = verify_runtime(spec)
    source = verify_input(spec)
    registry, epoch = store.snapshot()
    own = registry['registered_future_requests'].get(request)
    need(own is not None and own['state'] in ('ARMED', 'RUNNING'),
         'REQUEST_NOT_ARMED')
    peers = peer_reservation(registry, request)
    local = local_sample(root)
    limits = spec['limits']
    own_write = 2 * limits['max_result_directory_bytes'] + GIB
    need(own_write <= own['reserved_write_bytes'], 'OWN_WRITE_RESERVATION_TOO_SMALL')
    need(type(spec['host_cpu']) is int and spec['host_cpu'] in local['cpu_allowed'],
         'HOST_CPU_NOT_ADMITTED')
    need(limits['max_process_tree_vms_bytes'] >= limits['max_process_tree_rss_bytes'] > 0,
         'BAD_MEMORY_LIMITS')
    peer_bytes = sum(row['reserved_write_bytes'] for row in peers)
    required = 5 * GIB + own_write + peer_bytes
    need(local['native_free_bytes'] > required and local['native_free_inodes'] >= 100000,
         'NATIVE_DISK_OR_INODE_HOLD')
    need(local['host_MemAvailable_bytes'] > 64 * GIB + limits['max_process_tree_rss_bytes'],
         'HOST_MEMORY_HEADROOM_HOLD')
    if local['cgroup_max_bytes'] is not None:
        need(local['cgroup_max_bytes'] - local['cgroup_current_bytes'] >
             48 * GIB + limits['max_process_tree_rss_bytes'], 'CGROUP_MEMORY_HEADROOM_HOLD')
    archive = archive_capacity(archive_root, own_write)
    return {'status': 'SHORT_COLLECT_PRE_FORK_ADMISSION_PASS_NO_MODEL',
            'runtime': runtime, 'input': source, 'local': local, 'peers': peers,
            'native_required_free_bytes': required, 'archive': archive,
            'request': request, 'cohort': spec['cohort']}


def locked_admission(registry, q, cohort, spec_sha):
    """Pure lock-held check. No SH reader, FUSE, proc or resource sampler."""
    need(q['state'] in ('ARMED', 'RUNNING') and q['remaining'] > 0,
         'LOCKED_REQUEST_HOLD_NO_CONSUME')
    need(q['admitted_specs'].get(cohort) == spec_sha and cohort not in q['consumed'],
         'LOCKED_COHORT_SPEC_HOLD_NO_CONSUME')
    need(q['remaining'] == q['budget'] - len(q['consumed']), 'LOCKED_BUDGET_DRIFT')
    return True


def runtime_safety(root, output, limit_bytes):
    """10-second local cadence; caller may stop only its own model on failure."""
    sample = local_sample(root)
    used = sum(path.stat().st_size for path in Path(output).rglob('*') if path.is_file())
    reasons = []
    if sample['native_free_bytes'] <= 5 * GIB:
        reasons.append('USER_NATIVE_5GIB_FLOOR')
    if sample['native_free_inodes'] < 100000:
        reasons.append('NATIVE_INODE_FLOOR')
    if used > limit_bytes:
        reasons.append('OWN_RESULT_CAP')
    sample.update(own_result_bytes=used, status='STOP_OWN_MODEL' if reasons else 'PASS',
                  stop_reasons=reasons, true164_queries=0, registry_queries=0)
    return sample
