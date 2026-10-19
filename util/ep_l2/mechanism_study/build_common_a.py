"""A's sole common build/native entry. Default plan only, no applications/waiter.

New build/native leases consume E's formally published campaign-only5GiB
policy plus its monitor reserve. Historical named authorizations remain intact;
resuming the exact failed build or successful native producer needs a NEW lease.
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
import shutil
import socket
import subprocess
import sys
import time

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
from common_resource_guard import check_runtime, finalize_limit
REPO = HERE.parents[2]
HANDOFF = REPO / 'docs/ep_l2/codex_handoff/mechanism_study_2026_10_19_v1/a'
SPEC_PATH = HANDOFF / 'full_system_v2/COMMON_NATIVE_BUILD_SPEC_r6.json'
CAMPAIGN = 'EPL2_MECHANISM_STUDY_20261019_V1'
AUTHORITY = 'b2e5328aca825d6e9ebfe09e46fa208957834636'
SHARED = Path('/workspace/ep_l2_ft20261016_shared')
GIB = 2**30


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def git(root, *args):
    return subprocess.check_output(['git', *args], cwd=root, text=True).strip()


def put(path, value):
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, indent=2) + '\n')
    temporary.replace(path)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--build', type=Path, required=True)
    p.add_argument('--suite', choices=['main', 'all', 'diagnostics'], default='main')
    p.add_argument('--phase', choices=['combined', 'build', 'native'], default='combined')
    p.add_argument('--build-receipt', type=Path)
    p.add_argument('--resume-failed-build', action='store_true',
                   help='only the exact failed test-only build frozen in this spec; fresh E lease required')
    p.add_argument('--disk-authorization-id')
    p.add_argument('--admission', type=Path)
    p.add_argument('--execute', action='store_true')
    a = p.parse_args()
    out, build = a.out.resolve(), a.build.resolve()
    assert out.is_relative_to('/workspace') and build.is_relative_to('/workspace')
    assert not out.is_relative_to(build) and not build.is_relative_to(out)
    assert a.suite != 'diagnostics' or a.phase == 'native'
    assert not a.resume_failed_build or a.phase == 'build'
    assert not a.disk_authorization_id, 'new ordinary5GiB leases require E admission; historical named authorizations are not replayed'
    if a.phase == 'native':
        assert a.build_receipt and a.build_receipt.is_file() and build.is_dir(), 'exact retained build receipt required'
    elif not a.resume_failed_build:
        assert not build.exists(), 'fresh build required; preserve old builds'
    out.mkdir(parents=True, exist_ok=False)
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    spec = json.loads(SPEC_PATH.read_text())
    assert spec['campaign_id'] == CAMPAIGN and spec['authority'] == AUTHORITY
    assert spec['jobs'] == 2 and spec['memory_bytes'] == 8*GIB
    assert spec['disk_floor_bytes'] == 5*GIB and spec['memory_floor_bytes'] == 64*GIB
    assert spec['Share_floor_bytes'] == 40*GIB and spec['remote_execution'] is False
    assert spec['build_growth_bytes'] + spec['result_growth_bytes'] <= 7*GIB//2
    core, runtime = Path(spec['core']), Path(spec['framework'])
    vendor = runtime / 'gpu-simulator/extern/pybind11'
    native_only = a.phase == 'native'
    assert not a.execute or not spec.get('failed_build_recovery_manifest') or native_only or a.resume_failed_build, \
        'this recovery spec executes only its exact incremental build or retained native stage'
    cpu, memory = (1, spec['native_memory_bytes']) if native_only else (2, spec['memory_bytes'])
    growth = spec['result_growth_bytes'] + (0 if native_only else spec['build_growth_bytes'])
    bindings = {str(f): sha(f) for f in [Path(__file__), SPEC_PATH,
        HERE/'common_native_plan.py', HERE/'check_native_case.py', HERE/'common_resource_guard.py']}
    assert sha(HERE/'common_resource_guard.py') == spec['resource_guard_sha256']
    report = dict(schema='EP_L2_A_COMMON_BUILD_NATIVE_RECEIPT_V1', campaign_id=CAMPAIGN,
        authority=AUTHORITY, release_id=spec['release_id'], status='PLAN_ONLY_NOT_COMPILED_NOT_RUN',
        driver_source_commit=git(REPO,'rev-parse','HEAD'), driver_sha256=sha(__file__),
        spec_sha256=sha(SPEC_PATH), planner_sha256=sha(HERE/'common_native_plan.py'),
        checker_sha256=sha(HERE/'check_native_case.py'), core_source_commit=spec['core_source_commit'],
        resource_guard_sha256=sha(HERE/'common_resource_guard.py'),
        framework_source_commit=spec['framework_source_commit'], vendor_commit=spec['vendor'],
        core=str(core), framework=str(runtime), build=str(build), output=str(out), suite=a.suite, phase=a.phase,
        jobs=1 if native_only else 2, reserved_cpu_units=cpu, reserved_memory_bytes=memory,
        disk_floor_bytes=5*GIB, authorized_task_floor_bytes=5*GIB, memory_floor_bytes=64*GIB,
        reserved_build_growth_bytes=0 if native_only else spec['build_growth_bytes'],
        reserved_result_bytes=spec['result_growth_bytes'], compiler_started=False,
        native_invocations_attempted=0, native_invocations_completed=0, application_starts=0,
        runtime_ready=False, independent_qualification=False, commands=[], tests=[],
        trace_identity='SYNTHETIC_DIRECTED_FIXTURES_NOT_APPLICATION_TRACE', main_producer_pass=False)
    identity = {k: report[k] for k in ['campaign_id','authority','core_source_commit',
        'framework_source_commit','vendor_commit','driver_source_commit','driver_sha256',
        'spec_sha256','planner_sha256','checker_sha256','suite','phase']}
    identity.update(build_directory=str(build), output_directory=str(out))
    recovery = None
    baseline_bytes = 0
    baseline_result_bytes = 0
    if a.resume_failed_build:
        recovery = json.loads((HANDOFF / spec['failed_build_recovery_manifest']).read_text())
        assert recovery['build_directory'] == str(build) and build.is_dir()
        assert sha(HANDOFF / spec['failed_build_recovery_manifest']) == spec['failed_build_recovery_manifest_sha256']
        failed = json.loads(Path(recovery['failed_receipt']).read_text())
        assert sha(recovery['failed_receipt']) == recovery['failed_receipt_sha256']
        assert failed['status'] == 'STOPPED_OR_FAILED_NO_RUNTIME_RELEASE' and failed['lease_released']
        assert failed['error'] == "RuntimeError('build exited 2')" and failed['compiler_started']
        assert failed['native_invocations_attempted'] == failed['application_starts'] == 0
        assert failed['build'] == str(build) and failed['suite'] == a.suite == 'all'
        assert failed['output'] == recovery['failed_result_directory']
        assert failed['core_source_commit'] == recovery['failed_core_source_commit']
        for k in ['framework_source_commit', 'vendor_commit']:
            assert failed[k] == report[k]
        delta = subprocess.check_output(['git', 'diff', '--binary',
            recovery['failed_core_source_commit'], spec['core_source_commit']], cwd=core)
        assert hashlib.sha256(delta).hexdigest() == recovery['allowed_core_diff_sha256']
        assert git(core,'diff','--name-only',recovery['failed_core_source_commit'],
                   spec['core_source_commit']).splitlines() == recovery['allowed_changed_paths']
        # Input snapshots cover every retained object, executable, generated
        # file, cache and makefile. They are checked before central admission;
        # the consumed old lease/token is never reused.
        actual_files = {f.relative_to(build).as_posix(): f for f in build.rglob('*')
                        if f.is_file() and not f.is_symlink()}
        assert set(actual_files) == set(recovery['build_files'])
        actual_links = {f.relative_to(build).as_posix(): os.readlink(f)
                        for f in build.rglob('*') if f.is_symlink()}
        assert actual_links == recovery['build_symlinks']
        for name, f in actual_files.items():
            row = recovery['build_files'][name]
            assert f.stat().st_size == row['bytes'] and sha(f) == row['sha256'], name
            baseline_bytes += row['bytes']
        assert baseline_bytes == recovery['baseline_build_bytes']
        assert baseline_bytes + spec['build_growth_bytes'] == spec['build_total_capacity_bytes']
        result_inventories = dict(recovery.get('earlier_result_inventories', {}))
        assert recovery['failed_result_directory'] not in result_inventories
        result_inventories[recovery['failed_result_directory']] = recovery['failed_result_files']
        for root, inventory in result_inventories.items():
            result_root = Path(root)
            result_files = {f.relative_to(result_root).as_posix(): f
                            for f in result_root.rglob('*') if f.is_file() and not f.is_symlink()}
            assert set(result_files) == set(inventory)
            assert not any(f.is_symlink() for f in result_root.rglob('*'))
            for name, f in result_files.items():
                row = inventory[name]
                assert f.stat().st_size == row['bytes'] and sha(f) == row['sha256']
                bindings[str(f)] = row['sha256']
                baseline_result_bytes += row['bytes']
        assert baseline_result_bytes == recovery['baseline_result_bytes']
        assert baseline_result_bytes + spec['result_growth_bytes'] == spec['result_total_capacity_bytes']
        identity.update(failed_build_receipt_sha256=recovery['failed_receipt_sha256'],
                        retained_build_manifest_sha256=spec['failed_build_recovery_manifest_sha256'],
                        incremental_build_only=True)
        report.update(failed_build_recovery=spec['failed_build_recovery_manifest'],
                      baseline_build_bytes=baseline_bytes,
                      baseline_result_bytes=baseline_result_bytes,
                      build_total_capacity_bytes=spec['build_total_capacity_bytes'])
    report['build_identity'] = identity
    save = lambda: put(out/'RECEIPT.json',report)
    lease = registry = lock = None
    active = dict(pid=None,ever_started=False)
    try:
        assert git(core,'rev-parse','HEAD') == spec['core_source_commit']
        assert git(runtime,'rev-parse','HEAD') == spec['framework_source_commit']
        from common_native_plan import prepare
        cases, inputs = prepare(spec,HANDOFF,core,build,out,a.suite)
        report.update(planned_tests=cases,input_sha256=inputs,planned_native_invocations=len(cases),
            planned_main_invocations=sum(c['suite']=='main' for c in cases),
            planned_diagnostic_invocations=sum(c['suite']=='diagnostics' for c in cases))
        prior = None
        if native_only:
            prior_bytes = a.build_receipt.read_bytes()
            prior = json.loads(prior_bytes)
            assert prior['status'] == 'COMPILED_BUILD_ONLY_PENDING_NATIVE'
            for k in ['core_source_commit','framework_source_commit','vendor_commit','spec_sha256',
                      'driver_sha256','planner_sha256','checker_sha256','build']:
                assert prior[k] == report[k], 'retained producing build identity changed: '+k
            assert sha(prior['binary']) == prior['binary_sha256']
            for c in cases:
                f = c['native_command'][0]
                assert sha(f) == prior['test_binary_sha256'][f], 'missing/changed retained native executable'
            report.update(binary=prior['binary'],binary_sha256=prior['binary_sha256'],
                retained_build_receipt=dict(path=str(a.build_receipt.resolve()),sha256=sha(a.build_receipt)),
                producing_build_control_commit=prior['driver_source_commit'])
        save()
        if not a.execute:
            return
        # New leases consume E's formally published, campaign-only5GiB
        # amendment. Historical named records are preserved, never replayed.
        assert not a.disk_authorization_id, 'new ordinary policy requires fresh E admission; no historical token replay'
        assert a.admission and a.admission.is_file(), 'fresh exact E admission required; no compiler/native'
        approval_bytes = a.admission.read_bytes()
        approval = json.loads(approval_bytes)
        assert socket.gethostname()==spec['execution_host'],'current E API is original174 only'
        assert out.is_relative_to('/workspace/ep_l2_ms20261019_e_results')
        assert build.parent.exists() and out.parent.stat().st_dev==Path('/workspace').stat().st_dev
        assert build.parent.stat().st_dev==Path('/workspace').stat().st_dev
        assert not git(REPO,'status','--porcelain','--untracked-files=no'),'publish clean control source first'
        def sources_exact():
            for tree,h in [(core,spec['core_source_commit']),(runtime,spec['framework_source_commit']),
                           (vendor,spec['vendor'])]:
                assert git(tree,'rev-parse','HEAD')==h and not git(tree,'status','--porcelain','--untracked-files=no')
        sources_exact()
        old = json.loads((SHARED/'CLIENT_CONTRACT.json').read_text())
        assert sha(old['registry_client'])==old['registry_client_sha256']
        sys.path.insert(0,str(Path(old['registry_client']).parent))
        from registry import local_resources
        from run import process_tree_rss
        client = json.loads((SHARED/'mechanism_study_20261019_v1/CLIENT_CONTRACT.json').read_text())
        api = Path(client['resource_lease_api'])
        assert client['authority_commit']==AUTHORITY and sha(api)==client['resource_lease_api_sha256']
        assert sha(api)==approval['resource_client_sha256']
        sys.path.insert(0,str(api.parent))
        from coordinator import Coordinator,tooling_binding,retained_tree_bytes
        tooling_binding() # Includes exact published E disk_policy.py bytes.
        registry = Coordinator()
        policy = registry.work_disk_policy() # Read-only; A never adopts/amends E state.
        assert policy == spec['expected_E_workspace_policy'], 'E has not published/adopted this exact ordinary policy'
        assert policy['disk_floor_bytes']==5*GIB
        assert policy['monitor_reserve_bytes']>=128*2**20
        # Actual imported run_owned uses these exact poll/termination intervals.
        assert policy['monitor_interval_seconds']==.2 and policy['termination_grace_seconds']==3
        stop_floor,monitor=policy['disk_floor_bytes'],policy['monitor_reserve_bytes']
        expected = dict(identity,owner='A',phase='A_COMMON_'+a.phase.upper(),approved=True,
            full_applications_permitted=False,execution_host=spec['execution_host'],
            control_source_commit=report['driver_source_commit'],reserved_cpu_units=cpu,
            reserved_memory_bytes=memory,reserved_build_growth_bytes=report['reserved_build_growth_bytes'],
            reserved_result_bytes=spec['result_growth_bytes'],workspace_disk_policy=policy)
        for k,value in expected.items():
            assert approval.get(k)==value,'E admission identity mismatch: '+k
        assert approval['results_budget_status']=='PASS'
        if native_only:
            assert approval['retained_build_receipt_sha256']==sha(a.build_receipt)
        valid_until=approval['valid_until_unix']
        report.update(E_admission=dict(path=str(a.admission),sha256=sha(a.admission)),
            E_source_publication=client['source_publication_commit'],E_resource_api_sha256=sha(api),
            E_workspace_disk_policy=policy,authorized_task_floor_bytes=stop_floor,
            monitor_reserve_bytes=monitor,disk_floor_bytes=stop_floor+monitor)
        bindings.update({str(Path(client['execution_worktree'])/f):h for f,h in client['source_files'].items()})
        bindings.update({str(HANDOFF/f):h for f,h in spec['control_files_SHA256'].items()})
        bindings.update({str(core/f):h for f,h in spec['core_inputs_SHA256'].items()})
        bindings.update(inputs)
        guard_path = runtime/spec['supervisor']
        assert sha(guard_path)==spec['supervisor_SHA256']
        bindings[str(guard_path)] = spec['supervisor_SHA256']
        module = importlib.util.spec_from_file_location('frozen_common_supervisor',guard_path)
        guard = importlib.util.module_from_spec(module);module.loader.exec_module(guard)
        lock = open('/workspace/ep_l2_ms20261019_shared/A_BUILD.lock','a+')
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        def resources():
            assert time.time()<valid_until,'E admission expired'
            if approval_bytes is not None:
                assert a.admission.read_bytes()==approval_bytes,'E admission changed'
            for f,h in bindings.items():
                assert sha(f)==h,'bound source/config/tool changed: '+f
            live = local_resources();share = os.statvfs('/root/share')
            written = retained_tree_bytes(out)
            built = None if native_only else (retained_tree_bytes(build) if build.exists() else 0)
            rss = process_tree_rss(active['pid']) if active['pid'] is not None else 0
            prior_results = sum(retained_tree_bytes(Path(root)) for root in result_inventories) if recovery else None
            check_runtime(report,out,live,share.f_bavail*share.f_frsize,written,built,rss,
                spec['result_growth_bytes'],spec['build_growth_bytes'],
                spec.get('build_total_capacity_bytes',spec['build_growth_bytes']),
                baseline_build=baseline_bytes,baseline_results=baseline_result_bytes,
                prior_results=prior_results,memory_limit=memory)
            report['own_result_bytes_peak'] = max(written,report.get('own_result_bytes_peak',0))
            if built is not None:
                report['own_build_bytes_peak'] = max(built,report.get('own_build_bytes_peak',0))
            if active['pid'] is not None:
                report['own_process_tree_rss_peak'] = max(rss,report.get('own_process_tree_rss_peak',0))
            return live
        before = resources()
        assert before['disk_free_bytes']>=stop_floor+growth+monitor
        assert before['available_memory_bytes']-memory>=64*GIB
        allocation = registry.reserve_work('A','test' if native_only else 'build',cpu,memory,growth,
            out if native_only else build,result_growth_bytes=spec['result_growth_bytes'],
            disk_authorization_id=None,build_identity=None)
        lease = allocation['lease_id'];report.update(lease_id=lease,resource_owner='mechanism_A',resource_allocation=allocation)
        assert all(allocation[k]==v for k,v in policy.items()), 'new lease policy differs from frozen E ordinary policy'
        assert resources()['disk_free_bytes']>=stop_floor+growth+monitor
        temp_root = out if native_only else build
        (temp_root/'tmp').mkdir(parents=True,exist_ok=bool(recovery))
        env = dict(os.environ,GPGPUSIM_ROOT=str(core),CUDA_INSTALL_PATH='/usr/local/cuda-11.8',
            ACCELSIM_CONFIG='release',PATH='/usr/local/cuda-11.8/bin:'+os.environ['PATH'],
            TMPDIR=str(temp_root/'tmp'),XDG_CACHE_HOME=str(temp_root/'cache'),PYTHONDONTWRITEBYTECODE='1',
            TMP=str(temp_root/'tmp'),TEMP=str(temp_root/'tmp'),
            PYTHONPYCACHEPREFIX=str(temp_root/'cache/python'),CCACHE_DISABLE='1',CCACHE_DIR=str(temp_root/'cache/ccache'),
            CUDA_CACHE_DISABLE='1',CUDA_CACHE_PATH=str(temp_root/'cache/cuda'),OMP_NUM_THREADS='1',
            OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
        report['build_environment'] = {k:env.get(k) for k in ['GPGPUSIM_ROOT','CUDA_INSTALL_PATH','PATH',
            'CC','CXX','CFLAGS','CXXFLAGS','LDFLAGS','LD_LIBRARY_PATH','TMPDIR','TMP','TEMP','XDG_CACHE_HOME']}
        def bind(pid):
            active.update(pid=pid,ever_started=True);return registry.bind_work_process(lease,'A',pid)
        def run(command,name,timeout):
            try:
                resources()
                r = guard.run_owned(command,name,out,env,report,save,resources,bind,timeout)
                resources();return r
            finally:
                active['pid'] = None
        def linked_identity(name):
            row = run(['ldd',str(build/'accel-sim.out')],name,20);libs={}
            for line in Path(row['log']).read_text().splitlines():
                for token in line.split():
                    if token.startswith('/') and Path(token).is_file():
                        libs[str(Path(token).resolve())] = sha(token)
            return libs
        if not native_only:
            if recovery:
                # Incremental make may relink the embedded build version. Keep
                # the prior unqualified main binary before any such overwrite;
                # this copy counts against the already leased result ceiling.
                resources()
                original = build/'accel-sim.out'
                preserved = out/'INHERITED_MAIN_PRE_COMPILE.elf'
                previous_sha = recovery['build_files']['accel-sim.out']['sha256']
                assert sha(original)==previous_sha
                shutil.copyfile(original,preserved)
                assert sha(preserved)==previous_sha
                report['preserved_inherited_main'] = dict(path=str(preserved),sha256=previous_sha,
                    bytes=preserved.stat().st_size,qualified=False,counted_in_result_growth=True)
                resources();save()
            report.update(status='INCREMENTAL_BUILD_PREPARING' if recovery else 'CONFIGURING',compiler_started=True);save()
            if not recovery:
                run(['cmake','-S',str(runtime/'gpu-simulator'),'-B',str(build),'-G','Unix Makefiles',
                     '-DCUDAToolkit_ROOT=/usr/local/cuda-11.8'],'configure',600)
            run(['c++','--version'],'compiler_version',20);run(['cmake','--version'],'cmake_version',20)
            targets = sorted({c['target'] for c in cases})
            report['status']='BUILDING';save()
            command=['cmake','--build',str(build),'--target','accel-sim.out',*targets,'-j2']
            if recovery:
                command += ['--','-k'] # Collect remaining independent compile errors; nonzero never releases a binary.
            report['build_keep_going']=bool(recovery);save()
            run(command,'build',2400)
            flags = sorted(build.rglob('flags.make'))
            assert flags and all('-DNDEBUG' not in f.read_text() for f in flags),'native assertions disabled'
            report['assertion_flags_sha256'] = {str(f):sha(f) for f in flags}
            report.update(binary=str(build/'accel-sim.out'),binary_sha256=sha(build/'accel-sim.out'),
                test_binary_sha256={str(build/'gpgpu-sim'/t):sha(build/'gpgpu-sim'/t) for t in targets})
            report['dynamic_library_sha256'] = linked_identity('linked_libraries')
            sources_exact();assert sha(build/'accel-sim.out')==report['binary_sha256']
            if a.phase=='build':
                report['status']='COMPILED_BUILD_ONLY_PENDING_NATIVE';save()
                put(out/'BUILD_ONLY_RECEIPT.json',dict(report))
                return
        else:
            report['dynamic_library_sha256'] = linked_identity('native_linked_libraries')
            assert report['dynamic_library_sha256']==prior['dynamic_library_sha256'],'retained binary now links different libraries'
        # Build and native both use E's new ordinary5GiB policy, separately leased.
        # Resumed native validates the exact retained successful producing build.
        assert report['E_workspace_disk_policy']==policy and report['authorized_task_floor_bytes']==5*GIB
        completed=[];semantics={}
        for group in ['main','diagnostics']:
            selected = [c for c in cases if c['suite']==group]
            if not selected:continue
            report['status']='NATIVE_TESTING_'+group.upper();save()
            for case in selected:
                executable=Path(case['native_command'][0]);binary_sha=sha(executable)
                detail=out/(case['id']+'.native.json')
                cmd=[sys.executable,str(HERE/'check_native_case.py'),'--expected-exit',str(case['expected_exit']),
                    '--required-terminal',case['required_terminal'],'--receipt',str(detail),'--',*case['native_command']]
                report['native_invocations_attempted']+=1
                row=run(cmd,case['id'],case['timeout_seconds']);result=json.loads(detail.read_text())
                assert result['expectation_verified'] and result['actual_exit']==case['expected_exit']
                assert result['binary_sha256']==binary_sha==sha(executable)
                raw=detail.with_suffix('.native.log').read_text()
                if case.get('compare_group'):
                    prefix='A_COMMON_FIXTURE|SEMANTIC|' if case['compare_group']=='F_observer' else 'EPL2MS_TEST|SEMANTIC|'
                    lines=[s for s in raw.splitlines() if s.startswith(prefix)];assert len(lines)==1
                    semantics.setdefault(case['compare_group'],[]).append(lines[0])
                completed.append(dict(case=case['id'],scope=case['scope'],suite=group,
                    expected_exit=case['expected_exit'],native_evidence=str(detail),native_evidence_sha256=sha(detail),**row))
                report.update(tests=completed,native_invocations_completed=len(completed));save()
            sources_exact();assert sha(build/'accel-sim.out')==report['binary_sha256']
            if group=='main':
                for name,sigs in semantics.items():
                    assert len(sigs)==2 and sigs[0]==sigs[1],'observer changed native cycles/semantics: '+name
                report.update(main_producer_pass=True,status='MAIN_PRODUCER_PASS_PENDING_E_INDEPENDENT_QUALIFICATION');save()
                put(out/'MAIN_NATIVE_RECEIPT.json',dict(report))
                report['main_checkpoint_sha256']=sha(out/'MAIN_NATIVE_RECEIPT.json')
        assert len(completed)==len(cases)
        report['status']='PRODUCER_FINITE_PASS_PENDING_E_INDEPENDENT_QUALIFICATION'
    except BaseException as error:
        report['status']='RESOURCE_LIMIT' if report.get('resource_limit') else 'STOPPED_OR_FAILED_NO_RUNTIME_RELEASE';report['error']=repr(error)
        raise
    finally:
        if lease:
            registry.release_work(lease,'A','A common '+a.phase+' exited; '+str(out/'RECEIPT.json'),
                                  no_child_started=not active['ever_started'])
            report['lease_released']=True
        if lock:lock.close();report['own_lock_released']=True
        report['finished_UTC']=datetime.datetime.now(datetime.timezone.utc).isoformat()
        finalize_limit(report,out)
        save();print(report['status'])


if __name__=='__main__':
    main()
