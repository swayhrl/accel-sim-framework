#!/usr/bin/python3
"""PREPARED_NOT_TESTED: foreground configure/build only; coordinator release needed.
Required interpreter: /usr/bin/python3 -I -B, launched with the published clean env.
"""
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import time

SOURCE = Path('/workspace/worktrees/gpgpu-sim-iscas2027-dtc-sem1-core-174-v1')
OUTPUT = Path('/workspace/dtc-evidence-closure-20261019-v1/sem1/implementation-r1')
BUILD = OUTPUT / 'build'
EXPECTED_CORE = '1fcf5113c08a27b64ccca872c4a8fba4c12c1ece'
MAX_BYTES = 512 * 1024**2
MAX_SINGLE_FILE = 128 * 1024**2
MAX_LOG_BYTES = 16 * 1024**2
FREE_FLOOR = 5 * 1024**3
# Actual OUTPUT mount must stay strictly above5GiB. Admission also budgets the
# existing512MiB output ceiling and128MiB single-file reserve; no10GiB floor.
START_FLOOR = FREE_FLOOR + MAX_BYTES + MAX_SINGLE_FILE
# No inherited PYTHON*, LD_*, CMAKE*, MAKEFLAGS, compiler or Git environment.
CLEAN_ENV = {'PATH': '/usr/bin:/bin', 'LANG': 'C', 'LC_ALL': 'C',
             'TMPDIR': str(OUTPUT/'tmp'), 'CUDA_VISIBLE_DEVICES': ''}
CONTROLLER_ENV = {'PATH': '/usr/bin:/bin', 'LANG': 'C', 'LC_ALL': 'C'}
COMMANDS = {
    'configure': ['/usr/bin/cmake', '-S', str(SOURCE), '-B', str(BUILD),
        '-DCMAKE_CXX_COMPILER=/usr/bin/g++', '-DCMAKE_BUILD_TYPE=Release',
        '-DCMAKE_CXX_FLAGS_RELEASE=-O1 -g0', '-DCMAKE_EXPORT_COMPILE_COMMANDS=ON',
        '-DGPGPUSIM_BUILD_DTC_L1_TESTS=OFF',
        '-DGPGPUSIM_SEM1_CONDITIONAL_VALUES=ON',
        '-DCUDAToolkit_ROOT=/usr/local/cuda-11.8'],
    'build': ['/usr/bin/nice', '-n', '19', '/usr/bin/ionice', '-c', '2', '-n', '7',
        '/usr/bin/cmake', '--build', str(BUILD), '--target',
        'dtc_l1_sem1_values_ldst', '-j1'],
}

def free_bytes():
    info = os.statvfs(OUTPUT)
    return info.f_bavail * info.f_frsize

def output_bytes():
    total = 0
    for base, dirs, files in os.walk(OUTPUT, followlinks=False):
        for name in files:
            path = Path(base) / name
            try:
                if not path.is_symlink():
                    total += path.stat().st_size
            except FileNotFoundError:
                pass
    return total

def limits():
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    resource.setrlimit(resource.RLIMIT_FSIZE, (MAX_SINGLE_FILE, MAX_SINGLE_FILE))
    resource.setrlimit(resource.RLIMIT_AS, (4 * 1024**3, 4 * 1024**3))

def instance(pid):
    """A numeric PID alone never establishes ownership; retain start+session."""
    try:
        text = Path('/proc', str(pid), 'stat').read_text()
        fields = text[text.rfind(')')+2:].split()
        record = dict(pid=int(pid), state=fields[0], ppid=int(fields[1]),
            pgrp=int(fields[2]), session=int(fields[3]), start_ticks=int(fields[19]))
        try:
            record['exe'] = os.readlink('/proc/%s/exe' % pid)
        except OSError:
            record['exe'] = None
        return record
    except (FileNotFoundError, ProcessLookupError):
        return None

def same_instance(a, b):
    return a is not None and b is not None and all(
        a[k] == b[k] for k in ('pid', 'start_ticks', 'pgrp', 'session'))

def group_instances(root):
    if root is None:
        return []
    result = []
    for path in Path('/proc').iterdir():
        if not path.name.isdigit():
            continue
        record = instance(path.name)
        if record and record['pgrp'] == root['pgrp'] and record['session'] == root['session']:
            result.append(record)
    return sorted(result, key=lambda r: (r['pid'], r['start_ticks']))

def signal_unreaped(proc, root, sig):
    # This parent is the only waiter. Until wait/poll reaps its direct child,
    # the matching PID/PGID remains reserved even if that child has become Z.
    if proc.returncode is not None or not same_instance(root, instance(proc.pid)):
        return False
    os.killpg(root['pgrp'], sig)
    return True

def interrupted(signum, frame):
    raise InterruptedError('controller signal %s' % signum)

def main():
    if (os.path.realpath(sys.executable) != os.path.realpath('/usr/bin/python3')
            or not sys.flags.isolated or not sys.dont_write_bytecode):
        raise SystemExit('require /usr/bin/python3 -I -B')
    if dict(os.environ) != CONTROLLER_ENV:
        raise SystemExit('require env -i PATH=/usr/bin:/bin LANG=C LC_ALL=C')
    if len(sys.argv) != 2 or sys.argv[1] not in COMMANDS:
        raise SystemExit('configure|build required; no test/simulator mode exists')
    phase = sys.argv[1]
    actual = subprocess.check_output(['/usr/bin/git', '-C', str(SOURCE),
        'rev-parse', 'HEAD'], text=True, env=CLEAN_ENV).strip()
    dirty = subprocess.check_output(['/usr/bin/git', '-C', str(SOURCE),
        'status', '--porcelain'], text=True, env=CLEAN_ENV)
    if actual != EXPECTED_CORE or dirty:
        raise SystemExit('fixed clean source required')
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT/'tmp').mkdir(exist_ok=True)
    if free_bytes() < START_FLOOR or output_bytes() >= MAX_BYTES:
        raise SystemExit('BLOCKED_BUILD_RESOURCE: start reserve/floor/output limit')
    log = OUTPUT / (phase + '.log')
    if log.exists():
        raise SystemExit('preserve prior evidence: reviewed new output identity required')
    if phase == 'configure' and BUILD.exists():
        raise SystemExit('fresh ABI build directory required')
    if phase == 'build' and not (BUILD/'CMakeCache.txt').exists():
        raise SystemExit('configure receipt/source identity required first')
    signal.signal(signal.SIGTERM, interrupted)
    started = time.monotonic()
    budget = 60 if phase == 'configure' else 1200
    reason = None
    peak = output_bytes()
    seen = {}
    boot_id = Path('/proc/sys/kernel/random/boot_id').read_text().strip()
    with log.open('wb') as stream:
        proc = subprocess.Popen(COMMANDS[phase], cwd=SOURCE, env=CLEAN_ENV,
            stdout=stream, stderr=subprocess.STDOUT, start_new_session=True,
            preexec_fn=limits)
        root = instance(proc.pid)  # before the first poll/wait can reap it
        terminal_before_reap = root
        try:
            (OUTPUT/(phase+'.start.json')).write_text(json.dumps(dict(
                boot_id=boot_id, root_start=root, argv=COMMANDS[phase], env=CLEAN_ENV,
                controller_environment=CONTROLLER_ENV,
                controller=instance(os.getpid()), started_time_ns=time.time_ns()), indent=2)+'\n')
            if root is None or root['pgrp'] != proc.pid or root['session'] != proc.pid:
                raise RuntimeError('missing exact start/new-session identity')
            while True:
                observed_root = instance(proc.pid)
                if same_instance(root, observed_root):
                    terminal_before_reap = observed_root
                for record in group_instances(root):
                    seen[(record['pid'],record['start_ticks'])] = record
                # poll may reap. No signal may follow a successful reap.
                if proc.poll() is not None:
                    break
                current = output_bytes(); peak = max(peak, current)
                if current > MAX_BYTES:
                    reason = 'BLOCKED_BUILD_RESOURCE_OUTPUT_512MiB'
                elif free_bytes() <= FREE_FLOOR:
                    reason = 'BLOCKED_BUILD_RESOURCE_FREE_NOT_ABOVE_5GiB'
                elif log.stat().st_size > MAX_LOG_BYTES:
                    reason = 'BLOCKED_BUILD_RESOURCE_LOG_16MiB'
                elif time.monotonic() - started > budget:
                    reason = 'BUILD_TIMEOUT'
                if reason:
                    if not signal_unreaped(proc, root, signal.SIGTERM):
                        reason = 'CLEANUP_UNRESOLVED_ROOT_IDENTITY'
                    try:
                        proc.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        if not signal_unreaped(proc, root, signal.SIGKILL):
                            reason = 'CLEANUP_UNRESOLVED_ROOT_IDENTITY'
                    break
                time.sleep(0.2)
        except BaseException as error:
            reason = 'CONTROLLER_EXCEPTION: ' + repr(error)
        finally:
            # No poll in this guard: it might reap the ownership token.
            if proc.returncode is None:
                observed_root = instance(proc.pid)
                if same_instance(root, observed_root):
                    terminal_before_reap = observed_root
                if not signal_unreaped(proc, root, signal.SIGKILL):
                    reason = 'CLEANUP_UNRESOLVED_ROOT_IDENTITY'
                    # Only this still-owned direct Popen child; no group-number
                    # fallback. Missing group identity must remain unresolved.
                    proc.kill()
            code = proc.wait()
            terminal = dict(start_identity=root, exit=code, reaped=True,
                            reaped_time_ns=time.time_ns())
            # AFTER REAP: inspect and report only. Never signal this old PGID.
            leftovers = group_instances(root)
            current_root = instance(proc.pid)
            if leftovers:
                reason = 'CLEANUP_UNRESOLVED_GROUP_INSTANCES'
    final_bytes = output_bytes(); peak = max(peak, final_bytes)
    if reason is None and (final_bytes > MAX_BYTES or
            free_bytes() <= FREE_FLOOR or
            log.stat().st_size > MAX_LOG_BYTES):
        reason = 'BLOCKED_BUILD_RESOURCE_FINAL_BOUNDARY'
    receipt = dict(phase=phase, argv=COMMANDS[phase], env=CLEAN_ENV, core=actual,
        boot_id=boot_id, root_start=root, root_last_observed_before_reap=terminal_before_reap,
        root_terminal=terminal, controller_environment=CONTROLLER_ENV,
        root_current_after_reap=current_root, group_instances_seen=list(seen.values()),
        current_group_instances_after_reap=leftovers, post_reap_signals=0,
        exit=code, reason=reason, elapsed=time.monotonic()-started,
        peak_sampled_output_bytes=peak, final_output_bytes=final_bytes,
        final_free_bytes=free_bytes(), samples_not_filesystem_quota=True,
        output_disk_hard_floor_bytes=FREE_FLOOR, output_disk_start_reserve_bytes=START_FLOOR,
        output_disk_rule='ACTUAL_OUTPUT_MOUNT_FREE_STRICTLY_GREATER_THAN_5GiB',
        simulator_starts=0, tests_started=0)
    (OUTPUT/(phase+'.receipt.json')).write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt))
    return 0 if code == 0 and reason is None else 1

if __name__ == '__main__':
    sys.exit(main())
