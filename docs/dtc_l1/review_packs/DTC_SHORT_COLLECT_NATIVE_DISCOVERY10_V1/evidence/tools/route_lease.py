"""Private exact Short-Collect dispatcher lease and actual process guard.

Import is inert. The only production qualification lock is the existing native
global lock; a substitute file cannot confer science permission.
"""
from __future__ import annotations

import fcntl
import hashlib
import json
import os
from pathlib import Path
import re

NATIVE_LOCK = Path('/root/data/ep_l2_dtc_l1_native_v2/control/qualification_ledger/NATIVE_QUALIFICATION.lock')


class Hold(RuntimeError):
    pass


def need(value, reason):
    if not value:
        raise Hold(reason)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def process(pid, proc=Path('/proc')):
    base = Path(proc) / str(pid)
    try:
        fields = (base / 'stat').read_text().rsplit(')', 1)[1].split()
        return {
            'pid': pid, 'ppid': int(fields[1]), 'state': fields[0],
            'start_ticks': int(fields[19]),
            'cmdline': (base / 'cmdline').read_bytes().replace(b'\0', b' ').decode(errors='replace'),
            'exe': os.readlink(base / 'exe'),
        }
    except FileNotFoundError:
        return None


def actual_flock(path, pid, fd, proc=Path('/proc')):
    path = Path(path)
    st = path.stat()
    root = Path(proc) / str(pid)
    target = root / 'fd' / str(fd)
    need(target.stat().st_dev == st.st_dev and target.stat().st_ino == st.st_ino,
         'LEASE_FD_DEVICE_INODE_MISMATCH')
    need(os.readlink(target) == str(path), 'LEASE_FD_PATH_MISMATCH')
    rows = []
    for line in (root / 'fdinfo' / str(fd)).read_text().splitlines():
        if not line.startswith('lock:'):
            continue
        values = line.split()
        if len(values) < 9 or values[2] != 'FLOCK':
            continue
        major, minor, inode = values[6].split(':')
        device = os.makedev(int(major, 16), int(minor, 16))
        if (device, int(inode)) == (st.st_dev, st.st_ino):
            need(values[3:6] == ['ADVISORY', 'WRITE', str(pid)]
                 and values[7:] == ['0', 'EOF'], 'LEASE_NOT_EXCLUSIVE_KERNEL_FLOCK')
            rows.append(line)
    need(len(rows) == 1, 'EXACT_ONE_EXCLUSIVE_FLOCK_REQUIRED')
    return {'path': str(path), 'fd': fd, 'device': st.st_dev, 'inode': st.st_ino,
            'kernel_record': rows[0]}


def ancestry(pid, parent_pid, parent_start, proc=Path('/proc')):
    chain, seen = [], set()
    for _ in range(64):
        need(pid > 0 and pid not in seen, 'LEASE_ANCESTRY_CYCLE_OR_MISSING')
        seen.add(pid)
        row = process(pid, proc)
        need(row is not None and row['state'] != 'Z', 'LEASE_ANCESTRY_PROCESS_MISSING')
        chain.append({'pid': pid, 'start_ticks': row['start_ticks']})
        if pid == parent_pid:
            need(row['start_ticks'] == parent_start, 'LEASE_PARENT_GENERATION_DRIFT')
            return chain
        pid = row['ppid']
    raise Hold('LEASE_PARENT_NOT_ACTUAL_ANCESTOR')


def verify_lease(lease_path, *, request, controller_path, caller_pid=None,
                 lock_path=NATIVE_LOCK, proc=Path('/proc'), fixture_only=False):
    lease_path, controller_path, lock_path = map(Path, (lease_path, controller_path, lock_path))
    if not fixture_only:
        need(lock_path == NATIVE_LOCK, 'ACTUAL_GLOBAL_QUALIFICATION_LOCK_REQUIRED')
        need(lease_path.stat().st_dev == controller_path.stat().st_dev,
             'LEASE_CONTROLLER_NATIVE_DEVICE_MISMATCH')
    lease = json.loads(lease_path.read_bytes())
    need(lease.get('schema') == 'DTC_SHORT_COLLECT_PRIVATE_DISPATCH_LEASE_V1'
         and lease.get('request') == request, 'EXACT_PRIVATE_LEASE_IDENTITY')
    parent_pid, parent_start = lease['pid'], lease['start_ticks']
    parent = process(parent_pid, proc)
    need(parent is not None and parent['state'] != 'Z' and parent['start_ticks'] == parent_start,
         'LEASE_PARENT_NOT_LIVE_GENERATION')
    need(lease['controller_sha256'] == sha(controller_path)
         and lease['controller_path'] == str(controller_path.resolve())
         and str(controller_path.resolve()) in parent['cmdline'], 'LEASE_ACTUAL_CONTROLLER_DRIFT')
    reference = actual_flock(lock_path, parent_pid, lease['qualification_fd'], proc)
    need(reference['device'] == lease['qualification_device']
         and reference['inode'] == lease['qualification_inode'], 'LEASE_LOCK_IDENTITY_DRIFT')
    chain = ancestry(os.getpid() if caller_pid is None else caller_pid, parent_pid, parent_start, proc)
    return {'request': request, 'parent_pid': parent_pid, 'parent_start_ticks': parent_start,
            'qualification_lock': reference, 'actual_ancestry': chain}


def make_lease(request, controller_path, qualification_fd, *, lock_path=NATIVE_LOCK,
               fixture_only=False):
    """Call only after parent actually acquired EX flock on the global FD."""
    controller_path, lock_path = Path(controller_path).resolve(), Path(lock_path)
    if not fixture_only:
        need(lock_path == NATIVE_LOCK, 'ACTUAL_GLOBAL_QUALIFICATION_LOCK_REQUIRED')
    parent = process(os.getpid())
    need(parent is not None and str(controller_path) in parent['cmdline'],
         'TRUE_CONTROLLER_PROCESS_REQUIRED')
    reference = actual_flock(lock_path, os.getpid(), qualification_fd)
    return {
        'schema': 'DTC_SHORT_COLLECT_PRIVATE_DISPATCH_LEASE_V1',
        'request': request, 'pid': os.getpid(), 'start_ticks': parent['start_ticks'],
        'controller_path': str(controller_path), 'controller_sha256': sha(controller_path),
        'qualification_fd': qualification_fd, 'qualification_device': reference['device'],
        'qualification_inode': reference['inode'], 'kernel_flock_record': reference['kernel_record'],
    }


def acquire_global_qualification(*, lock_path=NATIVE_LOCK, fixture_only=False):
    if not fixture_only:
        need(Path(lock_path) == NATIVE_LOCK, 'ACTUAL_GLOBAL_QUALIFICATION_LOCK_REQUIRED')
    handle = Path(lock_path).open('r+b')
    try:
        fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        actual_flock(lock_path, os.getpid(), handle.fileno())
        return handle
    except BaseException:
        handle.close()
        raise


def verify_child(snapshot, spec, intent, *, proc=Path('/proc')):
    """Bind one actual process generation, mapped simulator, loader and cudart."""
    need(snapshot.get('uuid') == intent['uuid'] and snapshot.get('cohort') == intent['cohort'],
         'CHILD_UUID_COHORT_DRIFT')
    pid = snapshot.get('pid')
    need(type(pid) is int and pid > 1, 'ACTUAL_CHILD_PID_REQUIRED')
    current = process(pid, proc)
    need(current is not None and current['start_ticks'] == snapshot.get('start_ticks'),
         'ACTUAL_CHILD_GENERATION_DRIFT')
    base = Path(proc) / str(pid)
    actual_namespace = os.readlink(base / 'ns/mnt')
    actual_maps = (base / 'maps').read_text()
    actual_cwd = os.readlink(base / 'cwd')
    actual_environ = (base / 'environ').read_bytes().split(b'\0')
    actual_limits = (base / 'limits').read_text()
    need(snapshot.get('mnt_namespace') == actual_namespace == spec['execution_mnt_namespace'],
         'CHILD_MOUNT_NAMESPACE_DRIFT')
    need(snapshot.get('maps') == actual_maps, 'CHILD_MAPS_NOT_ACTUAL')
    need(snapshot.get('cmdline') == current['cmdline'], 'CHILD_CMDLINE_NOT_ACTUAL')
    need(actual_cwd == intent['output'], 'CHILD_CWD_NOT_OWN_OUTPUT')
    need(b'CUDA_VISIBLE_DEVICES=' in actual_environ and
         ('LD_LIBRARY_PATH=' + spec['host_launcher_layout']['library_path']).encode() in actual_environ and
         ('DTC_AG7_GENERATION=' + intent['uuid']).encode() in actual_environ,
         'CHILD_ENV_NOT_EXACT_PRIVATE_RUNTIME')
    need('Max core file size        0' in actual_limits,
         'CHILD_CORE_DUMP_NOT_DISABLED')
    cmdline = current['cmdline']
    need(spec['binary_path'] in cmdline or spec['binary_path'] in actual_maps,
         'ACTUAL_BINARY_NOT_BOUND')
    need(spec['binary_path'] in actual_maps, 'ACTUAL_BINARY_MAP_MISSING')
    need(spec['libcudart_path'] in actual_maps, 'ACTUAL_PRIVATE_CUDART_MAP_MISSING')
    need(spec['loader_path'] in actual_maps, 'ACTUAL_PRIVATE_LOADER_MAP_MISSING')
    for key in ('binary_path', 'libcudart_path', 'loader_path'):
        path = Path(spec[key])
        need(path.is_file() and sha(path) == spec[key.replace('_path', '_sha256')],
             'ACTUAL_MAPPED_FILE_SHA_DRIFT:' + key)
    return {'status': 'ACTUAL_CHILD_IDENTITY_PASS', 'pid': pid,
            'start_ticks': current['start_ticks'], 'uuid': intent['uuid']}
