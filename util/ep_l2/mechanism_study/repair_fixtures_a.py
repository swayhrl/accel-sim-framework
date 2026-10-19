"""Exact two-target fixture repair; E admission required, no application launch.

The retained main belongs to its original Core. Test-only source changes never
retag that binary. Unchanged native evidence remains immutable and separate.
"""
import argparse
import datetime
import fcntl
import importlib.util
import json
import os
from pathlib import Path
import resource
import socket
import sys
import time

sys.dont_write_bytecode = True
from build_common_a import sha, git, put, HERE, REPO, HANDOFF, SHARED, CAMPAIGN, AUTHORITY, GIB
from common_resource_guard import check_runtime, finalize_limit

SPEC = HANDOFF/'full_system_v2/COMMON_FIXTURE_REPAIR_SPEC_r1.json'


def verify_source(spec):
    core = Path(spec['core'])
    old, new = spec['runtime_producer_core'], spec['fixture_source_core']
    assert git(core, 'diff', '--name-only', old, new).splitlines() == spec['allowed_changed_paths']
    for name, oid in spec['production_tree_ids'].items():
        assert git(core, 'rev-parse', old+':'+name) == git(core, 'rev-parse', new+':'+name) == oid
    for root, commit in [(core,new),(Path(spec['framework']),spec['framework_source_commit']),
                         (Path(spec['framework'])/'gpu-simulator/extern/pybind11',spec['vendor'])]:
        assert git(root,'rev-parse','HEAD') == commit
        assert not git(root,'status','--porcelain','--untracked-files=no')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--admission', type=Path)
    parser.add_argument('--execute', action='store_true')
    a = parser.parse_args()
    spec = json.loads(SPEC.read_text())
    out = a.out.resolve()
    build, core, runtime = (Path(spec[k]) for k in ['build','core','framework'])
    assert out.parent == Path('/workspace/ep_l2_ms20261019_e_results') and not out.exists()
    assert spec['campaign_id']==CAMPAIGN and spec['authority']==AUTHORITY
    verify_source(spec)
    prior_path = Path(spec['producing_build_receipt'])
    assert sha(prior_path)==spec['producing_build_receipt_sha256']
    prior = json.loads(prior_path.read_text())
    assert prior['status']=='COMPILED_BUILD_ONLY_PENDING_NATIVE'
    assert prior['core_source_commit']==spec['runtime_producer_core']
    assert prior['binary_sha256']==spec['runtime_binary_sha256']==sha(build/'accel-sim.out')
    for path, digest in prior['test_binary_sha256'].items():
        assert sha(path)==digest, 'retained test changed before repair: '+path
    for path, digest in prior['dynamic_library_sha256'].items():
        assert sha(path)==digest, 'retained dynamic library changed: '+path
    flags = {str(f):sha(f) for f in build.rglob('flags.make')}
    archives = {str(f):sha(f) for f in build.rglob('*.a') if f.is_file()}
    assert flags==prior['assertion_flags_sha256']
    assert all('-DNDEBUG' not in Path(f).read_text() for f in flags)
    native_path = Path(spec['previous_native_receipt'])
    assert sha(native_path)==spec['previous_native_receipt_sha256']
    native = json.loads(native_path.read_text())
    inputs = dict(native['input_sha256'])
    for path, digest in inputs.items(): assert sha(path)==digest
    cases = [dict(c) for c in native['planned_tests'] if c['target'] in spec['targets']]
    for case in cases:
        if case['id'] in spec['terminal_corrections']:
            case['required_terminal']=spec['terminal_corrections'][case['id']]
    cases += spec['additional_cases']
    assert len(cases)==30 and len({c['id'] for c in cases})==30
    for rel,digest in spec['fixture_file_sha256'].items(): assert sha(core/rel)==digest
    from build_common_a import SPEC_PATH
    assert sha(SPEC_PATH)==spec['previous_spec_sha256']
    bindings = {str(p):sha(p) for p in [Path(__file__),SPEC,HERE/'build_common_a.py',
        HERE/'common_resource_guard.py',HERE/'check_native_case.py',SPEC_PATH]}
    bindings.update(inputs)
    bindings.update({str(core/p):h for p,h in spec['fixture_file_sha256'].items()})
    identity = dict(campaign_id=CAMPAIGN, authority=AUTHORITY,
        control_source_commit=git(REPO,'rev-parse','HEAD'), driver_sha256=sha(__file__),
        spec_sha256=sha(SPEC), runtime_producer_core=spec['runtime_producer_core'],
        fixture_source_core=spec['fixture_source_core'], runtime_binary_sha256=prior['binary_sha256'],
        framework_source_commit=spec['framework_source_commit'],vendor=spec['vendor'],
        build_directory=str(build),output_directory=str(out))
    expected = dict(identity,owner='A',phase='A_FIXTURE_REPAIR',approved=True,
        full_applications_permitted=False,execution_host=spec['execution_host'],
        reserved_cpu_units=2,reserved_memory_bytes=8*GIB,
        reserved_build_growth_bytes=spec['build_growth_bytes'],
        reserved_result_bytes=spec['result_growth_bytes'],workspace_disk_policy=spec['expected_E_workspace_policy'])
    if not a.execute:
        print(json.dumps(dict(status='REQUEST_ONLY_NO_COMPILE_NATIVE_OR_LEASE',
            expected_E_admission=expected, planned_native_cases=[c['id'] for c in cases],
            preserved_runtime_producer=spec['runtime_producer_core']),indent=2))
        return
    assert a.admission and a.admission.is_file()
    approval_bytes=a.admission.read_bytes();approval=json.loads(approval_bytes)
    for key,value in expected.items(): assert approval.get(key)==value, 'E admission mismatch: '+key
    assert approval['results_budget_status']=='PASS'
    assert socket.gethostname()==spec['execution_host']
    assert not git(REPO,'status','--porcelain','--untracked-files=no')
    assert build.stat().st_dev==out.parent.stat().st_dev==Path('/workspace').stat().st_dev
    resource.setrlimit(resource.RLIMIT_CORE,(0,0))
    out.mkdir()
    report=dict(identity,schema='EP_L2_A_FIXTURE_REPAIR_RECEIPT_V1',status='PREFLIGHT',
        binary=str(build/'accel-sim.out'),binary_sha256=prior['binary_sha256'],
        runtime_core_is_not_retagged=True,production_tree_ids=spec['production_tree_ids'],
        compiler_started=False,application_starts=0,independent_qualification=False,
        native_invocations_attempted=0,native_invocations_completed=0,commands=[],tests=[],
        old_passes_reused=0,planned_tests=cases,input_sha256=inputs,
        memory_floor_bytes=64*GIB,E_admission=dict(path=str(a.admission),sha256=sha(a.admission)))
    save=lambda:put(out/'RECEIPT.json',report)
    lease=registry=lock=None
    active=dict(pid=None,ever_started=False)
    try:
        client=json.loads((SHARED/'mechanism_study_20261019_v1/CLIENT_CONTRACT.json').read_text())
        api=Path(client['resource_lease_api'])
        assert sha(api)==client['resource_lease_api_sha256']==approval['resource_client_sha256']
        sys.path.insert(0,str(api.parent))
        from coordinator import Coordinator,tooling_binding,retained_tree_bytes,local_resources
        from run import process_tree_rss
        tooling_binding();registry=Coordinator();policy=registry.work_disk_policy()
        assert policy==spec['expected_E_workspace_policy']
        assert policy['disk_floor_bytes']==5*GIB and policy['monitor_reserve_bytes']==2*GIB
        assert policy['monitor_interval_seconds']==.2 and policy['termination_grace_seconds']==3
        bindings.update({str(Path(client['execution_worktree'])/p):h for p,h in client['source_files'].items()})
        supervisor=runtime/spec['supervisor'];assert sha(supervisor)==spec['supervisor_SHA256']
        bindings[str(supervisor)]=spec['supervisor_SHA256']
        module=importlib.util.spec_from_file_location('fixture_repair_supervisor',supervisor)
        guard=importlib.util.module_from_spec(module);module.loader.exec_module(guard)
        baseline=retained_tree_bytes(build);assert baseline==spec['baseline_build_bytes']
        growth=spec['build_growth_bytes']+spec['result_growth_bytes']
        report.update(E_source_publication=client['source_publication_commit'],E_resource_api_sha256=sha(api),
            E_workspace_disk_policy=policy,authorized_task_floor_bytes=5*GIB,
            monitor_reserve_bytes=2*GIB,disk_floor_bytes=7*GIB,baseline_build_bytes=baseline)
        lock=open('/workspace/ep_l2_ms20261019_shared/A_BUILD.lock','a+')
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        def resources():
            assert time.time()<approval['valid_until_unix'] and a.admission.read_bytes()==approval_bytes
            for path,digest in bindings.items():assert sha(path)==digest,'bound source/input changed: '+path
            live=local_resources();share=os.statvfs('/root/share')
            written,built=retained_tree_bytes(out),retained_tree_bytes(build)
            rss=process_tree_rss(active['pid']) if active['pid'] else 0
            check_runtime(report,out,live,share.f_bavail*share.f_frsize,written,built,rss,
                spec['result_growth_bytes'],spec['build_growth_bytes'],spec['build_total_capacity_bytes'],
                baseline_build=baseline,memory_limit=8*GIB)
            report['own_build_bytes_peak']=max(built,report.get('own_build_bytes_peak',0))
            report['own_result_bytes_peak']=max(written,report.get('own_result_bytes_peak',0))
            return live
        assert resources()['disk_free_bytes']>=7*GIB+growth
        allocation=registry.reserve_work('A','build',2,8*GIB,growth,build,
            result_growth_bytes=spec['result_growth_bytes'])
        lease=allocation['lease_id'];report.update(lease_id=lease,resource_allocation=allocation)
        assert all(allocation[k]==v for k,v in policy.items())
        assert resources()['disk_free_bytes']>=7*GIB+growth
        temp=build/'tmp';temp.mkdir(exist_ok=True)
        env=dict(os.environ,GPGPUSIM_ROOT=str(core),CUDA_INSTALL_PATH='/usr/local/cuda-11.8',
            PATH='/usr/local/cuda-11.8/bin:'+os.environ['PATH'],ACCELSIM_CONFIG='release')
        env.update(TMPDIR=str(temp),TMP=str(temp),TEMP=str(temp),XDG_CACHE_HOME=str(build/'cache'),
            PYTHONDONTWRITEBYTECODE='1',PYTHONPYCACHEPREFIX=str(build/'cache/python'),
            CCACHE_DISABLE='1',CCACHE_DIR=str(build/'cache/ccache'),CUDA_CACHE_DISABLE='1',
            CUDA_CACHE_PATH=str(build/'cache/cuda'),OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
        report['environment_write_roots']={k:env[k] for k in ['TMPDIR','TMP','TEMP','XDG_CACHE_HOME',
            'PYTHONPYCACHEPREFIX','CCACHE_DIR','CUDA_CACHE_PATH']}
        def bind(pid):
            active.update(pid=pid,ever_started=True);return registry.bind_work_process(lease,'A',pid)
        def run(command,name,timeout):
            try:
                resources();row=guard.run_owned(command,name,out,env,report,save,resources,bind,timeout)
                resources();return row
            finally:active['pid']=None
        report.update(status='FIXTURE_ONLY_COMPILING',compiler_started=True);save()
        run(['cmake','--build',str(build),'--target',*spec['targets'],'-j2','--','-k'],'two_fixture_build',1200)
        verify_source(spec)
        assert sha(build/'accel-sim.out')==prior['binary_sha256']
        for path,digest in prior['test_binary_sha256'].items():
            if Path(path).name not in spec['targets']:assert sha(path)==digest,'unaffected executable changed'
        assert {str(f):sha(f) for f in build.rglob('flags.make')}==flags
        assert {str(f):sha(f) for f in build.rglob('*.a') if f.is_file()}==archives, 'production archive changed'
        for path,digest in prior['dynamic_library_sha256'].items():assert sha(path)==digest
        report.update(status='FIXTURE_COMPILED_NATIVE_PENDING',
            test_binary_sha256={p:sha(p) for p in prior['test_binary_sha256']},
            assertion_flags_sha256=flags,dynamic_library_sha256=prior['dynamic_library_sha256'],
            production_archive_sha256=archives,unaffected_binaries_byte_identical=True)
        put(out/'FIXTURE_BUILD_RECEIPT.json',dict(report));save()
        for case in cases:
            detail=out/(case['id']+'.native.json')
            command=[sys.executable,str(HERE/'check_native_case.py'),'--expected-exit',str(case['expected_exit']),
                '--required-terminal',case['required_terminal'],'--receipt',str(detail),'--',*case['native_command']]
            report['native_invocations_attempted']+=1
            error=None
            try:run(command,case['id'],case['timeout_seconds'])
            except RuntimeError as problem:
                if report.get('resource_limit') or not detail.is_file():raise
                resources() # Never continue after a source, admission or resource failure.
                if json.loads(detail.read_text())['expectation_verified']:raise
                error=repr(problem) # A scientific case failure does not suppress other finite diagnostics.
            result=json.loads(detail.read_text())
            assert result['binary_sha256']==sha(case['native_command'][0])
            extra_ok=all(t in Path(result['raw_log']).read_text() for t in case.get('additional_terminals',[]))
            report['tests'].append(dict(case=case['id'],suite=case['suite'],native_evidence=str(detail),
                native_evidence_sha256=sha(detail),expectation_verified=result['expectation_verified'] and extra_ok,
                additional_terminals_verified=extra_ok,error=error))
            report['native_invocations_completed']+=1;save()
        verify_source(spec);assert sha(build/'accel-sim.out')==prior['binary_sha256']
        report['status']='AFFECTED_FIXTURES_PASS_PENDING_AGGREGATE_AND_E' if all(
            row['expectation_verified'] for row in report['tests']) else 'AFFECTED_FIXTURES_FAILED_NO_QUALIFICATION'
    except BaseException as error:
        report['status']='RESOURCE_LIMIT' if report.get('resource_limit') else 'STOPPED_OR_FAILED_NO_RUNTIME_RELEASE'
        report['error']=repr(error);raise
    finally:
        if lease:
            registry.release_work(lease,'A','A two-target repair exited; '+str(out/'RECEIPT.json'),
                no_child_started=not active['ever_started']);report['lease_released']=True
        if lock:lock.close();report['own_lock_released']=True
        report['finished_UTC']=datetime.datetime.now(datetime.timezone.utc).isoformat()
        finalize_limit(report,out);save();print(report['status'])


if __name__=='__main__':main()
