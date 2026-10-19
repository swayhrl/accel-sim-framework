"""A-only finite build/directeds. Plan-only by default; E admission required.

No application commands, daemon, retry, cleanup or alternative-host execution.
Reuse the exact historical resource-stop process supervisor, not its old Goal.
"""
import argparse
import datetime
import fcntl
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import resource
import socket
import subprocess
import sys
import time

sys.dont_write_bytecode = True
REPO = Path(__file__).resolve().parents[3]
HANDOFF = REPO / 'docs/ep_l2/codex_handoff/mechanism_study_2026_10_19_v1/a'
CAMPAIGN = 'EPL2_MECHANISM_STUDY_20261019_V1'
CORE = Path('/workspace/worktrees/gpgpu-sim-ep-l2-ms20261019-a-core-v1')
RUNTIME = Path('/workspace/worktrees/accel-sim-ep-l2-ms20261019-a-runtime-v1')
FRAMEWORK = '197741be9be9b8e390a557d639503b416d8e95f0'
VENDOR = 'f90c430c3a1ce8f08c09942a5a1c3a797bb2295b'
R1_RELEASE = HANDOFF / 'full_system_v2/previous_r5/RELEASE.json'
R1_RELEASE_SHA256 = '6a7a87e7c6f3f73d22622ba380d2c99bb8ef659b13e5ea6c8ed562d79ecdbc99'
TARGETS = ['accel-sim.out', 'ep_l2_ms_local_service', 'ep_l2_ms_partition',
           'ep_l2_ms_mode_guard', 'ep_l2_ms_observer', 'ep_l2_ft_directed',
           'ep_l2_ft_host_prefill', 'ep_l2_ft_memcpy_clock', 'ep_l2_ft_a1',
           'ep_l2_common_delta_r16']


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def git(root, *args):
    return subprocess.check_output(['git', *args], cwd=root, text=True).strip()


def put(path, value):
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(json.dumps(value, indent=2) + '\n')
    temp.replace(path)


def frozen_r1_release(path=None):
    # V2's top-level RELEASE describes the new common-source candidate. It
    # cannot select this frozen R1-only entry. Bind its retained exact bytes
    # instead; a missing/changed archive must fail, never fall back to V2.
    path = R1_RELEASE if path is None else Path(path)
    assert sha(path) == R1_RELEASE_SHA256, 'frozen R1 release bytes changed'
    selected = json.loads(path.read_text())
    assert selected['core_source_commit'] == '17e7e224954e44a968a0447bcdfea91e3b2e5a96'
    assert selected['runtime_framework_commit'] == FRAMEWORK
    assert selected['vendor_pybind11_commit'] == VENDOR
    return selected


def planned_tests(build, out):
    inputs = out / 'inputs'
    inputs.mkdir()
    # Directed fixtures override only their documented local geometry/ROP.
    # Real application overlays in HANDOFF/profiles never receive these edits.
    fixture_options = (CORE / 'tests/ep_l2/ft_wbuf.config').read_text()
    profiles = json.loads((HANDOFF / 'PROFILE_INDEX.json').read_text())['profiles']
    tests = []
    base = str(CORE / 'configs/tested-cfgs/SM7_QV100/gpgpusim.config')
    for row in profiles:
        name = row['profile'] + '_observer' + str(row['observer'])
        overlay = inputs / (name + '.config')
        overlay.write_text(fixture_options + (HANDOFF / row['overlay']).read_text())
        mode, diagnostic = str(row['mode']), str(row['diagnostic'])
        if not row['observer']:
            tests.append((name + '_local', [str(build / 'gpgpu-sim/ep_l2_ms_local_service'),
                base, str(overlay), mode, diagnostic], 'EPL2MS_TEST|LOCAL|'))
        args = [base, str(overlay), mode, '16', '0', '0', '1', diagnostic, str(row['observer'])]
        tests.append((name + '_partition', [str(build / 'gpgpu-sim/ep_l2_ms_partition'),
            *args, 'service'], 'MS_PARTITION_REAL_FIFOS_BANK_INTERVENTION_FIXED_PIPELINE_NATIVE_PASS'))
        if not row['observer']:
            latency_overlay = inputs / (name + '_ROP7.config')
            latency_overlay.write_text(overlay.read_text() + '-gpgpu_l2_rop_latency 7\n')
            latency_args = [base, str(latency_overlay), mode, '16', '0', '0', '1', diagnostic, '0']
            tests.append((name + '_fixed_latency', [str(build / 'gpgpu-sim/ep_l2_ms_partition'),
                *latency_args, 'latency7'], 'EPL2MS_TEST|LATENCY|rop=7|cold_lower_reads=1|later_response_cycle=1|'))
        if row['mode'] == 1:
            tests.append((name + '_capacity', [str(build / 'gpgpu-sim/ep_l2_ms_partition'),
                *args, 'capacity'], 'MS_PARTITION_CAPACITY_NATIVE_PASS'))
    tests.append(('bounded_observer', [str(build / 'gpgpu-sim/ep_l2_ms_observer')],
                  'MS_OBSERVER_BOUNDED_IDENTITY_FIRST_WAIT_AND_DISABLED_NATIVE_PASS'))
    ordinary = str(CORE / 'tests/ep_l2/ft_wbuf.config')
    tests.append(('affected_default_OFF', [str(build / 'gpgpu-sim/ep_l2_ft_directed'), base, ordinary],
                  'PASS'))
    for mode in ['1', '2']:
        tests.append(('host_prefill_' + mode, [str(build / 'gpgpu-sim/ep_l2_ft_host_prefill'),
            base, ordinary, mode, '16'], 'PASS'))
        for offset in ['0', '4096']:
            tests.append(('physical_clock_' + mode + '_' + offset,
                [str(build / 'gpgpu-sim/ep_l2_ft_memcpy_clock'), base, ordinary, mode, '16', offset],
                'violations=0|max_grants_per_physical_bank_cycle=1'))
        tests.append(('stale_return_' + mode, [str(build / 'gpgpu-sim/ep_l2_ft_a1'),
            base, ordinary, mode, '16'], 'PASS'))
    for variant in ['b1-read-first', 'b1-atomic-first', 'b1-multi', 'b1-b16', 'b1-dirty', 'b1-version-only']:
        tests.append((variant, [str(build / 'gpgpu-sim/ep_l2_common_delta_r16'),
            base, ordinary, variant], 'PASS B1'))
    # Reuse actual atomic-sector driver with each affected diagnostic family;
    # its mode selection is explicit, not inherited from a parent PASS.
    for profile, variants in [('S_COPY_FREE', ['b1-b16']), ('S_L2_DATA_FREE', ['b1-b16']),
                              ('U_L2_DATA_FREE', ['b1-read-first', 'b1-atomic-first', 'b1-dirty', 'b1-version-only'])]:
        for variant in variants:
            tests.append((profile + '_' + variant, [str(build / 'gpgpu-sim/ep_l2_common_delta_r16'),
                base, str(inputs / (profile + '_observer0.config')), variant], 'PASS B1'))
    invalid = [('both_diagnostics', '1', '-gpgpu_ep_l2_diag_copy_free 1\n-gpgpu_ep_l2_diag_l2_data_free 1\n'),
               ('U_copy', '2', '-gpgpu_ep_l2_diag_copy_free 1\n'),
               ('legacy_observer', '0', ''),
               ('P2_observer', '1', '-gpgpu_ep_l2_bank_ops 2\n'),
               ('S64_observer', '1', '-gpgpu_ep_l2_static_s64 1\n'),
               ('MQ2_observer', '1', '-gpgpu_ep_l2_mq2 1\n'),
               ('old_ideal_observer', '1', '-gpgpu_ep_l2_ideal_meta 1\n')]
    guard_prefix = 'EP-L2 mechanism study supports finite P1 S/U'
    for name, mode, extra in invalid:
        overlay = inputs / ('REJECT_' + name + '.config')
        overlay.write_text((inputs / 'S_observer1.config').read_text() + extra)
        tests.append(('reject_' + name, [str(build / 'gpgpu-sim/ep_l2_ms_mode_guard'),
            base, str(overlay), mode, name, guard_prefix], 'MS_NATIVE_GUARD_PASS|case=' + name))
    return [{'case': n, 'command': c, 'required_terminal': t} for n, c, t in tests]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--build', required=True, type=Path)
    parser.add_argument('--admission', type=Path)
    parser.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    out, build = args.out.resolve(), args.build.resolve()
    assert out.is_relative_to('/workspace') and build.is_relative_to('/workspace')
    assert not build.exists(), 'fresh build root required; preserve old builds'
    out.mkdir(parents=True, exist_ok=False)
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    report = {'schema': 'EPL2_MS_A_BUILD_AND_DIRECTED_V1', 'campaign_id': CAMPAIGN,
              'status': 'PLAN_ONLY_NOT_COMPILED_NOT_RUN', 'compiler_started': False,
              'application_starts': 0, 'independent_qualification': False,
              'core_source_commit': git(CORE, 'rev-parse', 'HEAD'),
              'framework_source_commit': FRAMEWORK, 'driver_source_commit': git(REPO, 'rev-parse', 'HEAD'),
              'driver_sha256': sha(__file__), 'core': str(CORE), 'framework': str(RUNTIME),
              'build': str(build), 'jobs': 2, 'disk_floor_bytes': 48 * 2**30,
              'memory_floor_bytes': 64 * 2**30, 'commands': [], 'tests': []}
    save = lambda: put(out / 'RECEIPT.json', report)
    lease = None
    lock = None
    registry = None
    try:
        report['planned_tests'] = planned_tests(build, out)
        save()
        if not args.execute:
            return
        assert args.admission and args.admission.is_file(), 'E admission required; no compiler'
        admission_bytes = args.admission.read_bytes()
        approval = json.loads(admission_bytes)
        for key, value in {'campaign_id': CAMPAIGN, 'owner': 'A',
                           'authority_host': 'huangrulin-174',
                           'phase': 'A_BUILD_AND_DIRECTED', 'approved': True,
                           'full_applications_permitted': False,
                           'core_source_commit': report['core_source_commit'],
                           'framework_source_commit': FRAMEWORK,
                           'driver_sha256': report['driver_sha256']}.items():
            assert approval.get(key) == value, 'E admission identity mismatch: ' + key
        assert approval['results_budget_status'] == 'PASS'
        assert approval['reserved_result_bytes'] >= 128 * 2**20
        report['E_admission'] = {'path': str(args.admission), 'sha256': sha(args.admission)}
        assert socket.gethostname() == 'huangrulin-174', 'original174 only'
        selected = frozen_r1_release()
        report['R1_selection_release'] = {'path': str(R1_RELEASE),
            'sha256': R1_RELEASE_SHA256, 'top_level_V2_release_is_not_R1_selection': True}
        assert selected['core_source_commit'] == report['core_source_commit']
        assert git(RUNTIME, 'rev-parse', 'HEAD') == FRAMEWORK
        vendor = RUNTIME / 'gpu-simulator/extern/pybind11'
        assert git(vendor, 'rev-parse', 'HEAD') == VENDOR
        for tree in [CORE, RUNTIME, vendor]:
            assert not git(tree, 'status', '--porcelain', '--untracked-files=no'), 'dirty source'
        cl = json.loads(Path('/workspace/ep_l2_ft20261016_shared/CLIENT_CONTRACT.json').read_text())
        assert sha(cl['registry_client']) == cl['registry_client_sha256'], 'central binding changed'
        sys.path.insert(0, str(Path(cl['registry_client']).parent))
        from registry import Registry, local_resources, process_identity
        extension = json.loads(Path('/workspace/ep_l2_ft20261016_shared/mechanism_study_20261019_v1/CLIENT_CONTRACT.json').read_text())
        extension_path = Path(extension['resource_lease_api'])
        assert sha(extension_path) == extension['resource_lease_api_sha256'], 'new E resource API changed'
        assert approval['resource_client_sha256'] == sha(extension_path), 'E admission uses another resource adapter'
        assert approval['build_directory'] == str(build) and approval['output_directory'] == str(out), 'unbound outputs'
        assert out.is_relative_to('/workspace/ep_l2_ms20261019_e_results'), 'new results must be accounted'
        assert approval['reserved_build_growth_bytes'] == 2 * 2**30
        assert approval['reserved_result_bytes'] == 128 * 2**20
        sys.path.insert(0, str(extension_path.parent))
        from coordinator import Coordinator, tooling_binding, retained_tree_bytes
        from run import process_tree_rss
        tooling_binding()
        registry = Coordinator()
        report['registry_binding'] = cl
        guard_path = RUNTIME / 'util/ep_l2/ft_lane1/build_r0_1.py'
        spec = importlib.util.spec_from_file_location('frozen_ms_owned_supervisor', guard_path)
        guard = importlib.util.module_from_spec(spec); spec.loader.exec_module(guard)
        report['reused_supervisor_sha256'] = sha(guard_path)
        lock = open('/workspace/ep_l2_ms20261019_shared/A_BUILD.lock', 'a+')
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)

        active_child = {'pid': None, 'ever_started': False}

        def resources():
            assert args.admission.read_bytes() == admission_bytes, 'E admission changed'
            assert time.time() < approval['valid_until_unix'], 'E admission expired'
            live = local_resources()
            share = os.statvfs('/root/share')
            assert share.f_bavail * share.f_frsize >= 40 * 2**30, 'Share floor crossed'
            assert live['disk_free_bytes'] >= report['disk_floor_bytes'], 'workspace floor crossed'
            assert live['available_memory_bytes'] >= report['memory_floor_bytes'], 'memory floor crossed'
            # Bounded own outputs only; never scan old experiment trees.
            written = retained_tree_bytes(out)
            built = retained_tree_bytes(build) if build.exists() else 0
            report['own_build_bytes_peak'] = max(report.get('own_build_bytes_peak', 0), built)
            assert built < approval['reserved_build_growth_bytes'], 'reserved own build growth crossed'
            if active_child['pid'] is not None:
                rss = process_tree_rss(active_child['pid'])
                report['own_process_tree_rss_peak'] = max(report.get('own_process_tree_rss_peak', 0), rss)
                assert rss <= 8 * 2**30, 'own process tree exceeded shared RAM lease'
            report['own_result_bytes_peak'] = max(report.get('own_result_bytes_peak', 0), written)
            assert written < 128 * 2**20, 'reserved own result budget crossed'
            return live

        before = resources()
        assert before['disk_free_bytes'] >= 50 * 2**30, '48GiB plus2GiB build reserve'
        assert before['available_memory_bytes'] - 8 * 2**30 >= report['memory_floor_bytes']
        # One lease in the original central registry: compile growth and
        # new-results growth are both reserved atomically, without a second lease.
        allocation = registry.reserve_work('A', 'build', 2, 8 * 2**30,
            2 * 2**30 + 128 * 2**20, build, result_growth_bytes=128 * 2**20)
        lease = allocation['lease_id']
        report['lease_id'] = lease; report['resource_owner'] = 'mechanism_A'
        report['resource_allocation'] = allocation
        assert resources()['disk_free_bytes'] >= 50 * 2**30, 'second disk check after lease'
        environment = dict(os.environ, GPGPUSIM_ROOT=str(CORE),
            CUDA_INSTALL_PATH='/usr/local/cuda-11.8', ACCELSIM_CONFIG='release',
            PATH='/usr/local/cuda-11.8/bin:' + os.environ['PATH'],
            OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1')
        def bound_child_identity(pid):
            active_child['pid'] = pid; active_child['ever_started'] = True
            return registry.bind_work_process(lease, 'A', pid)
        def run(command, name, timeout):
            try:
                return guard.run_owned(command, name, out, environment, report, save,
                                       resources, bound_child_identity, timeout)
            finally:
                active_child['pid'] = None
        report.update(status='CONFIGURING', compiler_started=True); save()
        run(['cmake', '-S', str(RUNTIME / 'gpu-simulator'), '-B', str(build),
             '-G', 'Unix Makefiles', '-DCUDAToolkit_ROOT=/usr/local/cuda-11.8'], 'configure', 600)
        report['status'] = 'BUILDING'; save()
        run(['cmake', '--build', str(build), '--target', *TARGETS, '-j2'], 'build', 1800)
        flags = sorted(build.rglob('flags.make'))
        assert flags and all('-DNDEBUG' not in p.read_text() for p in flags)
        report['assertion_flags_sha256'] = {str(p): sha(p) for p in flags}
        report['binary'] = str(build / 'accel-sim.out')
        report['binary_sha256'] = sha(report['binary'])
        report['status'] = 'DIRECTED_TESTING'; save()
        semantics = {}
        for case in report['planned_tests']:
            row = run(case['command'], case['case'], 180)
            text = Path(row['log']).read_text()
            assert case['required_terminal'] in text, 'missing native completion: ' + case['case']
            row['executable_sha256'] = sha(case['command'][0])
            report['tests'].append({'case': case['case'], **row})
            lines = [line for line in text.splitlines() if line.startswith('EPL2MS_TEST|SEMANTIC|')]
            if lines:
                assert len(lines) == 1
                semantics[case['case']] = lines[0]
            save()
        for name, line in semantics.items():
            if '_observer0_' in name:
                assert semantics[name.replace('_observer0_', '_observer1_')] == line, 'observer changed cycles/semantics'
        for tree, expected in [(CORE, report['core_source_commit']), (RUNTIME, FRAMEWORK), (vendor, VENDOR)]:
            assert git(tree, 'rev-parse', 'HEAD') == expected
            assert not git(tree, 'status', '--porcelain', '--untracked-files=no')
        report['status'] = 'PRODUCER_FINITE_PASS_PENDING_E_INDEPENDENT_QUALIFICATION'
    except BaseException as error:
        report['status'] = 'STOPPED_OR_FAILED_NO_RUNTIME_RELEASE'
        report['error'] = repr(error)
        raise
    finally:
        if lease:
            registry.release_work(lease, 'A', 'A owned build/directeds exited; receipt ' + str(out / 'RECEIPT.json'),
                no_child_started=not active_child['ever_started'])
            report['lease_released'] = True
        if lock:
            lock.close(); report['own_lock_released'] = True
        report['finished_UTC'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        save()
        print(report['status'])


if __name__ == '__main__':
    main()
