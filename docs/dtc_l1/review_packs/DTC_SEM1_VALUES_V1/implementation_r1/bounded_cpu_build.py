#!/usr/bin/env python3
"""PREPARED_NOT_TESTED: foreground SEM1 configure/build only; no sim/test dispatch.
Run only after coordinator registers this exact file and grants CPU/resource role.
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
FREE_FLOOR = 2 * 1024**3
# Polling disk admission is a guard, not a filesystem quota. Reserve an extra
# 128MiB for one in-progress writer; cannot promise a hard aggregate disk cap.
START_FLOOR = FREE_FLOOR + MAX_BYTES + MAX_SINGLE_FILE
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

def main():
    if len(sys.argv) != 2 or sys.argv[1] not in COMMANDS:
        raise SystemExit('configure|build required; no test or simulator mode exists')
    phase = sys.argv[1]
    actual = subprocess.check_output(['git', '-C', str(SOURCE), 'rev-parse', 'HEAD'], text=True).strip()
    dirty = subprocess.check_output(['git', '-C', str(SOURCE), 'status', '--porcelain'], text=True)
    if actual != EXPECTED_CORE or dirty:
        raise SystemExit('fixed clean source required')
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT/'tmp').mkdir(exist_ok=True)
    if free_bytes() < START_FLOOR or output_bytes() >= MAX_BYTES:
        raise SystemExit('BLOCKED_BUILD_RESOURCE: start reserve/floor/output limit')
    log = OUTPUT / (phase + '.log')
    if log.exists():
        raise SystemExit('preserve prior phase evidence: use reviewed new output identity')
    if phase == 'configure' and BUILD.exists():
        raise SystemExit('fresh ABI build directory required')
    if phase == 'build' and not (BUILD/'CMakeCache.txt').exists():
        raise SystemExit('configure receipt/source identity required first')
    env = dict(os.environ, TMPDIR=str(OUTPUT/'tmp'), CUDA_VISIBLE_DEVICES='')
    started = time.monotonic()
    budget = 60 if phase == 'configure' else 1200
    reason = None
    peak = output_bytes()
    with log.open('wb') as stream:
        proc = subprocess.Popen(COMMANDS[phase], cwd=SOURCE, env=env, stdout=stream,
            stderr=subprocess.STDOUT, start_new_session=True, preexec_fn=limits)
        try:
            while proc.poll() is None:
                current = output_bytes(); peak = max(peak, current)
                if current > MAX_BYTES:
                    reason = 'BLOCKED_BUILD_RESOURCE_OUTPUT_512MiB'
                elif free_bytes() < FREE_FLOOR + MAX_SINGLE_FILE:
                    reason = 'BLOCKED_BUILD_RESOURCE_FREE_RESERVE'
                elif log.stat().st_size > MAX_LOG_BYTES:
                    reason = 'BLOCKED_BUILD_RESOURCE_LOG_16MiB'
                elif time.monotonic() - started > budget:
                    reason = 'BUILD_TIMEOUT'
                if reason:
                    os.killpg(proc.pid, signal.SIGTERM)
                    try:
                        proc.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        os.killpg(proc.pid, signal.SIGKILL)
                    break
                time.sleep(0.2)
        finally:
            if proc.poll() is None:
                os.killpg(proc.pid, signal.SIGKILL)
            code = proc.wait()
            # A terminated build root is not permission for detached helpers.
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
    final_bytes = output_bytes()
    peak = max(peak, final_bytes)
    if reason is None and (final_bytes > MAX_BYTES or
                           free_bytes() < FREE_FLOOR + MAX_SINGLE_FILE or
                           log.stat().st_size > MAX_LOG_BYTES):
        reason = 'BLOCKED_BUILD_RESOURCE_FINAL_BOUNDARY'
    receipt = dict(phase=phase, argv=COMMANDS[phase], core=actual, exit=code,
        reason=reason, elapsed=time.monotonic()-started, peak_sampled_output_bytes=peak,
        final_output_bytes=final_bytes, final_free_bytes=free_bytes(),
        samples_not_filesystem_quota=True, simulator_starts=0, tests_started=0)
    (OUTPUT/(phase+'.receipt.json')).write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt))
    return 0 if code == 0 and reason is None else 1

if __name__ == '__main__':
    sys.exit(main())
