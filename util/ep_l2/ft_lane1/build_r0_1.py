"""Build/locally validate one isolated R0.1 candidate under Lane5 admission.

No daemon, implicit retry or independent-qualification claim. A resource hold
still writes a verifiable receipt without invoking CMake or a compiler.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

CORE_CANDIDATE = 'c948184504d82b80e23eb3f4ff6cdfd328ba9355'
PYBIND11_COMMIT = 'f90c430c3a1ce8f08c09942a5a1c3a797bb2295b'
FRAMEWORK_ROOT = Path('/workspace/worktrees/accel-sim-ep-l2-ft20261016-lane1-r0-1')
BUILD_ROOT = Path('/workspace/build/ep-l2-ft20261016-lane1-r0-1')
DISK_FLOOR = 48 * 1024**3
MEMORY_FLOOR = 64 * 1024**3
BUILD_GROWTH = 2 * 1024**3


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def head(path):
    return subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=path, text=True).strip()


def admission_hold(policy, resources, active_builds):
    # A shared policy edit cannot silently lower this release's frozen floors.
    disk_floor = max(DISK_FLOOR, policy['min_disk_free_bytes'])
    memory_floor = max(MEMORY_FLOOR, policy['min_available_memory_bytes'])
    if resources['disk_free_bytes'] < disk_floor + BUILD_GROWTH:
        return 'RESOURCE_HOLD_WORKSPACE_DISK_AND_BUILD_GROWTH'
    if resources['available_memory_bytes'] - 8 * 1024**3 < memory_floor:
        return 'RESOURCE_HOLD_AVAILABLE_MEMORY_WITH_RESERVATION'
    if active_builds:
        return 'RESOURCE_HOLD_EXISTING_BUILD_NO_DUPLICATE_COMPILE'
    return None


def repair_commands(build, core):
    base = str(core / 'configs/tested-cfgs/SM7_QV100/gpgpusim.config')
    overlay = str(core / 'tests/ep_l2/ft_wbuf.config')
    commands = []
    for mode in (1, 2):
        for c in (8, 16):
            prefix = [base, overlay, str(mode), str(c)]
            commands.append((f'host_prefill_{mode}_{c}',
                [str(build / 'gpgpu-sim/ep_l2_ft_host_prefill'), *prefix]))
            for offset in (0, 4096):
                commands.append((f'physical_clock_{mode}_{c}_{offset}',
                    [str(build / 'gpgpu-sim/ep_l2_ft_memcpy_clock'), *prefix, str(offset)]))
            commands.append((f'warm_clock_{mode}_{c}',
                [str(build / 'gpgpu-sim/ep_l2_ft_memcpy_clock'), *prefix, '4096', 'warm_hit']))
            commands.append((f'partition_{mode}_{c}',
                [str(build / 'gpgpu-sim/ep_l2_ft_partition'), *prefix]))
    commands.append(('ft_directed',
        [str(build / 'gpgpu-sim/ep_l2_ft_directed'), base, overlay]))
    return commands


def run_owned(command, name, out, environment, report, save, resources_now,
              process_identity, timeout=900):
    record = {'command': command, 'log': str(out / (name + '.log'))}
    report.setdefault('commands', []).append(record)
    save()
    process = None
    start = time.monotonic()
    try:
        with Path(record['log']).open('x') as stream:
            process = subprocess.Popen(command, stdout=stream, stderr=subprocess.STDOUT,
                cwd=out, env=environment, start_new_session=True)
            record['process'] = process_identity(process.pid)
            while process.poll() is None:
                resources = resources_now()
                if resources['disk_free_bytes'] < report['disk_floor_bytes'] or \
                   resources['available_memory_bytes'] < report['memory_floor_bytes']:
                    record['resource_stop'] = resources
                    raise RuntimeError('unchanged resource floor crossed; stop only owned process')
                if time.monotonic() - start > timeout:
                    raise RuntimeError('owned build/test timeout')
                time.sleep(0.2)
        if process.returncode:
            raise RuntimeError(f'{name} exited {process.returncode}')
        return record
    except BaseException as error:
        record['error'] = repr(error)
        raise
    finally:
        if process is not None:
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGTERM)
                try:
                    process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait()
            record['exit_code'] = process.returncode
        # Include failure/timeout/floor-stop logs as well as successful logs.
        if Path(record['log']).exists():
            record['log_sha256'] = digest(record['log'])
        record['wall_seconds'] = time.monotonic() - start
        save()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--core', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--build', type=Path,
        default=BUILD_ROOT)
    parser.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    args.core = args.core.resolve()
    args.out = args.out.resolve()
    args.build = args.build.resolve()
    args.out.mkdir(parents=True, exist_ok=False)
    fw = Path(__file__).resolve().parents[3]
    client = json.loads(Path('/workspace/ep_l2_ft20261016_shared/CLIENT_CONTRACT.json').read_text())
    assert digest(client['registry_client']) == client['registry_client_sha256']
    sys.path.insert(0, str(Path(client['registry_client']).parent))
    from registry import Registry, ACTIVE, local_resources, process_identity
    registry = Registry(client['canonical_root'])
    report = {'status': 'PREFLIGHT', 'owner': 'lane1', 'release': 'R0.1',
        'framework_source_commit': head(fw), 'core_source_commit': head(args.core),
        'framework_worktree': str(fw), 'core_worktree': str(args.core),
        'build': str(args.build), 'independent_qualification': False,
        'binary_sha256': None, 'tests': [], 'jobs': 2, 'runtime_ready': False,
        'build_growth_reserve_bytes': BUILD_GROWTH, 'compiler_started': False,
        'compiler_started_definition': 'entered CMake configure (may invoke compiler detection) or build',
        'trace_identity': None, 'application_runs': 0}
    lease = None

    def save():
        (args.out / 'BUILD_AND_TEST_RECEIPT.json').write_text(json.dumps(report, indent=2) + '\n')

    def run(command, name, timeout=900):
        if name not in ('configure', 'build'):
            report.setdefault('test_executables', {})[command[0]] = digest(command[0])
        return run_owned(command, name, args.out, environment, report, save,
                         local_resources, process_identity, timeout)

    try:
        if report['core_source_commit'] != CORE_CANDIDATE:
            raise ValueError('R0.1 requires the exact published Core candidate')
        if fw != FRAMEWORK_ROOT.resolve() or args.build != BUILD_ROOT.resolve():
            raise ValueError('production source/build paths are frozen; alternative needs review')
        for tree in (fw, args.core):
            assert not subprocess.check_output(['git', 'status', '--porcelain',
                '--untracked-files=no'], cwd=tree), 'dirty producing source'
        vendor = (fw / 'gpu-simulator/extern/pybind11').resolve()
        report['pybind11'] = {'path': str(vendor), 'commit': head(vendor)}
        if report['pybind11']['commit'] != PYBIND11_COMMIT:
            raise ValueError('pybind11 must match the frozen R0 dependency')
        assert not subprocess.check_output(['git', 'status', '--porcelain',
            '--untracked-files=no'], cwd=vendor), 'dirty pybind11 dependency'
        inputs = [(args.core, p) for p in (
            'configs/tested-cfgs/SM7_QV100/gpgpusim.config', 'tests/ep_l2/ft_wbuf.config',
            'tests/ep_l2/test_ft_host_prefill.cc', 'tests/ep_l2/test_ft_memcpy_clock.cc',
            'tests/ep_l2/test_ft_partition.cc', 'tests/ep_l2/test_ft_wbuf.cc')]
        inputs += [(fw, f'tests/ep_l2/ft20261016/r0_1/{p}.config')
                   for p in ('b16_banked', 'u_wb16', 'b8_banked', 'u_wb8')]
        report['input_sha256'] = {str(root / p): digest(root / p) for root, p in inputs}
        report['driver_sha256'] = digest(__file__)
        report['planned_tests'] = repair_commands(args.build, args.core)
        with registry.locked() as state:
            policy = state['hosts'][state['authority_host']]
            report.update(disk_floor_bytes=max(DISK_FLOOR, policy['min_disk_free_bytes']),
                          memory_floor_bytes=max(MEMORY_FLOOR, policy['min_available_memory_bytes']))
            resources = local_resources()
            report['resources_before'] = resources
            active_builds = {k:r for k,r in state['resource_leases'].items() if r['status'] in ACTIVE}
            report['active_builds'] = active_builds
            hold = admission_hold(policy, resources, active_builds)
            if hold:
                report['status'] = hold
                return
        if not args.execute:
            report['status'] = 'ADMISSION_HEADROOM_PRESENT_NOT_EXECUTED'
            return
        assert not args.build.exists(), 'use a new build root; never overwrite a prior build'
        lease = registry.build_lease('lane1', cpu=2, memory=8 * 1024**3)
        report['lease_id'] = lease
        with registry.locked() as state:
            # Close the gap between preflight and the central lease acquisition.
            others = {k:r for k,r in state['resource_leases'].items()
                      if k != lease and r['status'] in ACTIVE}
            hold = admission_hold(state['hosts'][state['authority_host']], local_resources(), others)
            if hold:
                report['status'] = hold
                return
        environment = dict(os.environ, GPGPUSIM_ROOT=str(args.core),
            CUDA_INSTALL_PATH='/usr/local/cuda-11.8', ACCELSIM_CONFIG='release',
            PATH='/usr/local/cuda-11.8/bin:' + os.environ['PATH'],
            OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1')
        report['status'] = 'CONFIGURING'
        report['compiler_started'] = True
        run(['cmake', '-S', str(fw / 'gpu-simulator'), '-B', str(args.build),
             '-G', 'Unix Makefiles', '-DCUDAToolkit_ROOT=/usr/local/cuda-11.8'], 'configure')
        report['status'] = 'BUILDING'
        report['compiler_started'] = True
        targets = ['accel-sim.out', 'ep_l2_ft_memcpy_clock', 'ep_l2_ft_host_prefill',
                   'ep_l2_ft_directed', 'ep_l2_ft_partition']
        run(['cmake', '--build', str(args.build), '--target', *targets, '-j2'], 'build')
        report['binary'] = str(args.build / 'accel-sim.out')
        report['binary_sha256'] = digest(report['binary'])
        report['framework_build_stamp'] = (args.build / 'accelsim_version.h').read_text()
        flags = sorted(args.build.rglob('flags.make'))
        assert flags and all('-DNDEBUG' not in p.read_text() for p in flags), 'assertions must be enabled'
        report['assertion_flags_sha256'] = {str(p): digest(p) for p in flags}
        report['status'] = 'PRODUCER_TESTING'
        for name, command in report['planned_tests']:
            report['tests'].append(run(command, name, 180))
        assert head(fw) == report['framework_source_commit'] and head(args.core) == report['core_source_commit']
        assert all(digest(path) == sha for path, sha in report['input_sha256'].items())
        for tree in (fw, args.core):
            assert not subprocess.check_output(['git', 'status', '--porcelain',
                '--untracked-files=no'], cwd=tree), 'source changed during build'
        assert head(vendor) == PYBIND11_COMMIT
        assert not subprocess.check_output(['git', 'status', '--porcelain',
            '--untracked-files=no'], cwd=vendor), 'dependency changed during build'
        report['status'] = 'PRODUCER_TESTS_PASS_NOT_INDEPENDENTLY_QUALIFIED'
    except Exception as error:
        report['status'] = 'FAILED_RETAIN_DIAGNOSTICS_NO_RUNTIME_RELEASE'
        report['error'] = repr(error)
        raise
    finally:
        if lease:
            registry.release_build(lease, 'lane1')
        report['resources_after'] = local_resources()
        save()
        print(json.dumps({k:report[k] for k in ('status','compiler_started','binary_sha256')}, indent=2), flush=True)


if __name__ == '__main__':
    main()
