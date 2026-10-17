#!/usr/bin/env python3
"""Read-only dispatcher audit. Writes only an explicitly named NEW AB receipt.
No signals (including signal 0), flock attempts, helper execution or trace reads.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone, timedelta
import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess

PID, START = 1425986, 584741606
OLD = Path('/workspace/worktrees/accel-sim-decoupled-l1-fast64')
RUNS = Path('/workspace/fast64-primary-r4')
LOCK = RUNS / '.fast64_4_2d_core41_autodispatch_v1.lock'
PACK = Path(__file__).resolve().parents[1]
FW = PACK.parents[3]

def digest(data):
    return hashlib.sha256(data).hexdigest()

def proc(pid):
    p = Path('/proc') / str(pid)
    try:
        raw = (p / 'stat').read_text()
        f = raw[raw.rfind(')') + 2:].split()
        args = [x for x in (p / 'cmdline').read_bytes().decode(errors='replace').split('\0') if x]
        result = {'pid': pid, 'state': f[0], 'ppid': int(f[1]),
                  'pgrp': int(f[2]), 'session': int(f[3]), 'start_ticks': int(f[19]),
                  'argv': args}
        for item in ('exe', 'cwd'):
            try:
                result[item] = os.readlink(p / item)
            except OSError:
                result[item] = 'UNAVAILABLE'
        result['same_expected_incarnation'] = pid == PID and result['start_ticks'] == START
        return result
    except (OSError, ValueError, IndexError):
        return None

def info(path, with_hash=False):
    p = Path(path)
    row = {'path': str(p), 'exists': p.exists()}
    if not p.exists():
        return row
    s = p.stat()
    row.update(device=s.st_dev, inode=s.st_ino, mode=oct(s.st_mode & 0o777),
               size=s.st_size, mtime_ns=s.st_mtime_ns, directory=p.is_dir())
    if with_hash and p.is_file():
        row['sha256'] = digest(p.read_bytes())
    return row

def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args], timeout=30)

parser = argparse.ArgumentParser()
parser.add_argument('--output', required=True, choices=['OBSERVATION_INITIAL.json', 'OBSERVATION_FINAL.json'])
args = parser.parse_args()
destination = PACK / args.output
assert not destination.exists(), 'Preserve old observations; do not overwrite'
started = datetime.now(timezone(timedelta(hours=8))).isoformat()
before = proc(PID)
assert before and before['same_expected_incarnation'], 'Identity changed: UNRESOLVED_OWNER; re-audit'

script = OLD / 'util/dtc_l1/auto_dispatch_fast64_4_2d_core41_v1.sh'
script_data = script.read_bytes()
loaded_data = Path(f'/proc/{PID}/fd/255').read_bytes()
script_identity = info(script, True)
script_identity.update(fd255_target=os.readlink(f'/proc/{PID}/fd/255'),
                       fd255_sha256=digest(loaded_data), fd255_matches_disk=loaded_data == script_data,
                       frozen_framework='18a68dcccd795f1b6cda75504e9450d00c9cee02',
                       git_blob=git(OLD, 'rev-parse', '18a68dcccd795f1b6cda75504e9450d00c9cee02:util/dtc_l1/auto_dispatch_fast64_4_2d_core41_v1.sh').decode().strip())
assert script_data == git(OLD, 'show', '18a68dcccd795f1b6cda75504e9450d00c9cee02:util/dtc_l1/auto_dispatch_fast64_4_2d_core41_v1.sh')
helpers = []
for name, expected in [
    ('dispatch_fast64_4_2d_core41_v1.sh', 'e26f090f076f7929d4933aad743964c757ddabfa0514858768e365add286b441'),
    ('monitor_fast64_repaired_core_row_v2.sh', '266a489c246512d5d321d77c2ef6e10794b0b0deb4e6aa7bb9bd2ee3f37b67ff'),
    ('audit_fast64_future_precompute_resources_v3.sh', '2a806549ebbe1870609f03fab396a4b78f01945091683f7cfa93e2f447470355')]:
    row = info(OLD / 'util/dtc_l1' / name, True)
    row.update(expected_sha256=expected, pinned_hash_matches=row.get('sha256') == expected)
    helpers.append(row)

lock_stat = LOCK.stat()
fd9_stat = Path(f'/proc/{PID}/fd/9').stat()
assert (fd9_stat.st_dev, fd9_stat.st_ino) == (lock_stat.st_dev, lock_stat.st_ino)
fdinfo = Path(f'/proc/{PID}/fdinfo/9').read_text()
same_inode = []
all_procs, races = {}, 0
for p in Path('/proc').iterdir():
    if not p.name.isdigit():
        continue
    pid = int(p.name)
    row = proc(pid)
    if not row:
        races += 1
        continue
    all_procs[pid] = row
    try:
        for fd in (p / 'fd').iterdir():
            try:
                s = fd.stat()
                if (s.st_dev, s.st_ino) == (lock_stat.st_dev, lock_stat.st_ino):
                    same_inode.append({'pid': pid, 'start_ticks': row['start_ticks'],
                                       'ppid': row['ppid'], 'argv': row['argv'], 'fd': fd.name,
                                       'target': os.readlink(fd),
                                       'fdinfo': (p / 'fdinfo' / fd.name).read_text()})
            except OSError:
                pass
    except OSError:
        pass

descendants = set()
changed = True
while changed:
    changed = False
    for pid, row in all_procs.items():
        if pid != PID and (row['ppid'] == PID or row['ppid'] in descendants) and pid not in descendants:
            descendants.add(pid)
            changed = True

related, simulators = [], []
for pid, row in all_procs.items():
    argv = row['argv']
    is_sim = Path(row['exe'].removesuffix(' (deleted)')).name == 'accel-sim.out' or any(
        '\n' not in a and Path(a).name == 'accel-sim.out' for a in argv)
    exact_related = pid == PID or pid in descendants or any(
        '\n' not in a and any(n in a.lower() for n in ('core41', '2dconvolution', 'monitor_fast64_repaired_core_row_v2'))
        for a in argv)
    old_control = any('\n' not in a and ('fast64' in a.lower()) for a in argv)
    if is_sim:
        simulators.append(row)
    if exact_related or old_control:
        row = dict(row)
        row['relation'] = ('TARGET' if pid == PID else 'TARGET_DESCENDANT' if pid in descendants
                           else 'RELATED_CORE41_CONTROL_PRESERVE' if exact_related else 'OTHER_FAST64_CONTROL_PRESERVE')
        # Inline shell programs are not needed in the small receipt.
        row['argv'] = [a if '\n' not in a else '[inline shell program omitted; not a target]' for a in argv]
        related.append(row)

base = OLD / 'docs/dtc_l1/fast64/generated/fast64_3_repair_v1/fast64_3_2DConvolution_base_core41d740e8_a1_v1.json'
structural = base.with_name('FAST64_3_2DCONVOLUTION_BASE_STRUCTURAL_METRICS_V1.json')
artifacts = [info(base), info(structural)]
for mode in ('io', 'oo'):
    stem = f'fast64_4_primary_2dconvolution_{mode}_core41d740e8_a1_v1'
    for suffix in ('', '.launcher.log', '.supervisor.tsv', '.closeout.pid', '.closeout.log'):
        artifacts.append(info(RUNS / (stem + suffix)))
    artifacts.append(info(OLD / 'docs/dtc_l1/fast64/generated/fast64_4_primary_core41_v1' / (stem + '.json')))

log = RUNS / 'fast64_4_2d_core41_autodispatch_v1.log'
log_st = log.stat()
counts, first, last = Counter(), {}, {}
h = hashlib.sha256()
with log.open('rb') as stream:
    remaining, pending = log_st.st_size, b''
    while remaining:
        data = stream.read(min(1024 * 1024, remaining))
        assert data, 'log truncated during snapshot'
        h.update(data)
        remaining -= len(data)
        pending += data
        lines = pending.split(b'\n')
        pending = lines.pop()
        for raw in lines:
            line = raw.decode(errors='replace')
            event = line.split('\t', 1)[0]
            counts[event] += 1
            first.setdefault(event, line)
            last[event] = line

downstream = []
for path in ['/tmp/dtc-fast64-invalidate-formal-41d740e8/accel-sim.out',
             '/tmp/fast64-runners/bf9a84c8aab54ccd5d00a8465d69669cfac78012b783c3cfd9e0e4433062e6af/run_fast64_trace_v2.sh',
             str(OLD / 'configs/dtc_l1/fast64/FAST64_IO.config'),
             str(OLD / 'configs/dtc_l1/fast64/FAST64_OO.config')]:
    downstream.append(info(path, True))
core41 = Path('/workspace/worktrees/gpgpu-sim-decoupled-l1-m5')
after = proc(PID)
assert after and after['start_ticks'] == before['start_ticks'], 'PID incarnation changed during read'
assert after['argv'] == before['argv'], 'Target command changed during read'
assert script.read_bytes() == script_data, 'Script changed during read'
end_lock_stat = LOCK.stat()
assert (end_lock_stat.st_dev, end_lock_stat.st_ino) == (lock_stat.st_dev, lock_stat.st_ino)
receipt = {'schema': 1, 'goal': 'DTC_LANE_AB_OLD_DISPATCH_AUTHORITY_AUDIT_174_V1',
           'observation_started_at_shanghai': started,
           'observation_finished_at_shanghai': datetime.now(timezone(timedelta(hours=8))).isoformat(),
           'host': socket.gethostname(), 'uid': os.getuid(),
           'boot_id': Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
           'target_before': before, 'target_after': after, 'same_incarnation': True,
           'script_identity': script_identity, 'pinned_helpers': helpers,
           'lock_file': info(LOCK), 'target_fd9_target': os.readlink(f'/proc/{PID}/fd/9'),
           'target_fdinfo9': fdinfo, 'target_fdinfo9_sha256': digest(fdinfo.encode()),
           'same_inode_open_fds': same_inode,
           'global_proc_locks_matches': [line for line in Path('/proc/locks').read_text().splitlines()
                                          if ':' + str(lock_stat.st_ino) + ' ' in line],
           'descendants': [all_procs[x] for x in sorted(descendants)],
           'related_control_processes': related, 'all_observed_accel_simulators': simulators,
           'proc_scan': {'visible_processes': len(all_procs), 'unreadable_or_exit_races': races,
                         'atomic_snapshot': False, 'scope': 'visible /proc namespace, not other hosts/namespaces'},
           'expected_artifacts': artifacts,
           'base_file_gate': 'FALSE_BOTH_FILES_ABSENT' if not base.exists() and not structural.exists() else 'REQUIRES_REVIEW',
           'log_prefix': {'path': str(log), 'device': log_st.st_dev, 'inode': log_st.st_ino,
                          'prefix_bytes': log_st.st_size, 'prefix_sha256': h.hexdigest(),
                          'event_counts': dict(counts), 'first_by_event': first, 'last_by_event': last,
                          'incomplete_trailing_bytes': len(pending), 'current_size_after_read': log.stat().st_size},
           'downstream_file_identities': downstream,
           'legacy_core_head': git(core41, 'rev-parse', 'HEAD').decode().strip(),
           'legacy_core_status_porcelain': git(core41, 'status', '--porcelain').decode(),
           'actions_by_AB': {'signals_including_zero': 0, 'lock_acquisitions_or_unlocks': 0,
                             'lock_file_deletions': 0, 'legacy_script_modifications': 0,
                             'simulator_or_helper_executions': 0, 'trace_reads': 0,
                             'goal_or_authority_takeovers': 0},
           'limitations': 'No absence claim for deleted historical artifacts or non-visible namespaces. Observation is time-bounded, not permission to ignore a live lock.'}
destination.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + '\n')
print(json.dumps({'receipt': str(destination), 'same_incarnation': True,
                  'fd9_flock_present': 'FLOCK' in fdinfo, 'descendants': sorted(descendants),
                  'same_inode_fd_holders': [r['pid'] for r in same_inode],
                  'base_file_gate': receipt['base_file_gate'], 'log_event_counts': dict(counts),
                  'visible_simulator_count': len(simulators)}))
