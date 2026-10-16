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


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def head(path):
    return subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=path, text=True).strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--core', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--build', type=Path,
        default=Path('/workspace/build/ep-l2-ft20261016-lane1-r0-1'))
    parser.add_argument('--execute', action='store_true')
    args = parser.parse_args()
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
        'binary_sha256': None, 'tests': [], 'jobs': 2,
        'build_growth_reserve_bytes': 2 * 1024**3, 'compiler_started': False}
    lease = None

    def save():
        (args.out / 'BUILD_AND_TEST_RECEIPT.json').write_text(json.dumps(report, indent=2) + '\n')

    def run(command, name, timeout=900):
        record = {'command': command, 'log': str(args.out / (name + '.log'))}
        report.setdefault('commands', []).append(record)
        save()
        with Path(record['log']).open('x') as stream:
            process = subprocess.Popen(command, stdout=stream, stderr=subprocess.STDOUT,
                cwd=args.out, env=environment, start_new_session=True)
            record['process'] = process_identity(process.pid)
            start = time.monotonic()
            try:
                while process.poll() is None:
                    resources = local_resources()
                    if resources['disk_free_bytes'] < report['disk_floor_bytes'] or \
                       resources['available_memory_bytes'] < report['memory_floor_bytes']:
                        record['resource_stop'] = resources
                        raise RuntimeError('unchanged resource floor crossed; stop only owned process')
                    if time.monotonic() - start > timeout:
                        raise RuntimeError('owned build/test timeout')
                    time.sleep(0.2)
            finally:
                if process.poll() is None:
                    os.killpg(process.pid, signal.SIGTERM)
                    try:
                        process.wait(timeout=3)
                    except subprocess.TimeoutExpired:
                        os.killpg(process.pid, signal.SIGKILL)
                        process.wait()
            record.update(exit_code=process.returncode, log_sha256=digest(record['log']))
            save()
            assert process.returncode == 0, (name, process.returncode)
        return record

    try:
        for tree in (fw, args.core):
            assert not subprocess.check_output(['git', 'status', '--porcelain',
                '--untracked-files=no'], cwd=tree), 'dirty producing source'
        with registry.locked() as state:
            policy = state['hosts'][state['authority_host']]
            report.update(disk_floor_bytes=policy['min_disk_free_bytes'],
                          memory_floor_bytes=policy['min_available_memory_bytes'])
            resources = local_resources()
            report['resources_before'] = resources
            active_builds = {k:r for k,r in state['resource_leases'].items() if r['status'] in ACTIVE}
            report['active_builds'] = active_builds
            if resources['disk_free_bytes'] < report['disk_floor_bytes'] + report['build_growth_reserve_bytes']:
                report['status'] = 'RESOURCE_HOLD_WORKSPACE_DISK_AND_BUILD_GROWTH'
                return
            if active_builds:
                report['status'] = 'RESOURCE_HOLD_EXISTING_BUILD_NO_DUPLICATE_COMPILE'
                return
        if not args.execute:
            report['status'] = 'ADMISSION_HEADROOM_PRESENT_NOT_EXECUTED'
            return
        assert not args.build.exists(), 'use a new build root; never overwrite a prior build'
        lease = registry.build_lease('lane1', cpu=2, memory=8 * 1024**3)
        report['lease_id'] = lease
        assert local_resources()['disk_free_bytes'] >= report['disk_floor_bytes'] + report['build_growth_reserve_bytes']
        environment = dict(os.environ, GPGPUSIM_ROOT=str(args.core),
            CUDA_INSTALL_PATH='/usr/local/cuda-11.8', ACCELSIM_CONFIG='release',
            PATH='/usr/local/cuda-11.8/bin:' + os.environ['PATH'],
            OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1')
        report['status'] = 'CONFIGURING'
        run(['cmake', '-S', str(fw / 'gpu-simulator'), '-B', str(args.build),
             '-DCUDAToolkit_ROOT=/usr/local/cuda-11.8'], 'configure')
        report['status'] = 'BUILDING'
        report['compiler_started'] = True
        targets = ['accel-sim.out', 'ep_l2_ft_memcpy_clock', 'ep_l2_ft_host_prefill',
                   'ep_l2_ft_directed', 'ep_l2_ft_partition']
        run(['cmake', '--build', str(args.build), '--target', *targets, '-j2'], 'build')
        report['binary'] = str(args.build / 'accel-sim.out')
        report['binary_sha256'] = digest(report['binary'])
        report['framework_build_stamp'] = (args.build / 'accelsim_version.h').read_text()
        report['status'] = 'PRODUCER_TESTING'
        base = str(args.core / 'configs/tested-cfgs/SM7_QV100/gpgpusim.config')
        overlay = str(args.core / 'tests/ep_l2/ft_wbuf.config')
        for mode in (1,2):
            for c in (8,16):
                command = [str(args.build / 'gpgpu-sim/ep_l2_ft_host_prefill'), base, overlay, str(mode), str(c)]
                report['tests'].append(run(command, f'host_prefill_{mode}_{c}', 180))
                for offset in (0,4096):
                    command = [str(args.build / 'gpgpu-sim/ep_l2_ft_memcpy_clock'), base, overlay,
                               str(mode), str(c), str(offset)]
                    report['tests'].append(run(command, f'physical_clock_{mode}_{c}_{offset}', 180))
                command = [str(args.build / 'gpgpu-sim/ep_l2_ft_memcpy_clock'), base, overlay,
                           str(mode), str(c), '4096', 'warm_hit']
                report['tests'].append(run(command, f'warm_clock_{mode}_{c}', 180))
                command = [str(args.build / 'gpgpu-sim/ep_l2_ft_partition'), base, overlay, str(mode), str(c)]
                report['tests'].append(run(command, f'partition_{mode}_{c}', 180))
        report['tests'].append(run([str(args.build / 'gpgpu-sim/ep_l2_ft_directed'), base, overlay], 'ft_directed', 180))
        assert head(fw) == report['framework_source_commit'] and head(args.core) == report['core_source_commit']
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
