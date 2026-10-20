"""E-admitted isolated incremental RO origin repair. No CMake/replay/application.

Compile one new finite fixture and one changed gpu-cache.cc translation unit.
All old objects, archives, binaries, raw results and generated banners are read-only.
The new archive replaces precisely one member; all other members are verified.
"""
import argparse
import datetime
import fcntl
import importlib.util
import json
import os
from pathlib import Path
import resource
import shlex
import shutil
import socket
import subprocess
import sys
import time

sys.dont_write_bytecode = True
from build_common_a import sha, git, put, HERE, REPO, HANDOFF, SHARED, CAMPAIGN, AUTHORITY, GIB
from common_resource_guard import check_runtime, finalize_limit

SPEC = HANDOFF/'full_system_v2/RO_ORIGIN_INCREMENTAL_SPEC_r26.json'


def flags(path):
    lines = Path(path).read_text().splitlines()
    values = {line.split(' = ', 1)[0]: line.split(' = ', 1)[1]
              for line in lines if ' = ' in line}
    result = shlex.split(' '.join(values[k] for k in ('CXX_DEFINES', 'CXX_INCLUDES', 'CXX_FLAGS')))
    assert '-O3' in result and '-g3' in result and '-DNDEBUG' not in result
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--admission', type=Path)
    p.add_argument('--via-e-api', action='store_true',
        help='ordinary new lease granted directly by E published reserve_work; no manual approval file')
    p.add_argument('--affected-native', action='store_true',
        help='relink three unchanged fixture objects to the sealed repaired archive and run only the20 affected cases')
    p.add_argument('--joint-vrw', action='store_true',
        help='compile the previously unrun shared V/RO/W controlled partition fixture; no main/library rebuild')
    p.add_argument('--joint-gdb', action='store_true',
        help='one bounded GDB replay of the already failed controlled fixture; no compilation or application')
    p.add_argument('--terminal-control', action='store_true',
        help='read frozen logs and test E-only runtime-dump parser proposal; no simulation/acceptance')
    p.add_argument('--own-pending-spec', type=Path)
    p.add_argument('--own-pending', action='store_true', help='Core27 single-member WAD own-pending guard repair, finite oldred/newgreen only')
    p.add_argument('--execute', action='store_true')
    a = p.parse_args()
    assert sum((a.own_pending,a.terminal_control,a.joint_gdb,a.joint_vrw,a.affected_native)) <= 1
    readonly_test = a.joint_gdb or a.terminal_control
    spec_path = ((a.own_pending_spec or HANDOFF/'full_system_v2/WAD_PENDING_REPAIR_SPEC_r39.json') if a.own_pending else
        HANDOFF/'full_system_v2/E_RUNTIME_DUMP_CONTROL_SPEC_r36.json' if a.terminal_control else
        HANDOFF/'full_system_v2/VRW_FAILED_FIXTURE_GDB_SPEC_r34.json' if a.joint_gdb else
        HANDOFF/'full_system_v2/VRW_SHARED_FIXTURE_SPEC_r32.json' if a.joint_vrw else
        HANDOFF/'full_system_v2/RO_ORIGIN_AFFECTED_SPEC_r27.json' if a.affected_native else SPEC)
    spec = json.loads(spec_path.read_text())
    build, old, core, runtime = (Path(spec[k]) for k in ('build', 'retained_build', 'core', 'framework'))
    out = a.out.resolve()
    assert out.parent == Path('/workspace/ep_l2_ms20261019_e_results')
    assert not out.exists() and not build.exists()
    assert spec['campaign_id'] == CAMPAIGN and spec['authority'] == AUTHORITY
    assert not git(core, 'status', '--porcelain', '--untracked-files=no')
    fixture_core = spec.get('fixture_source_core_commit', spec['core_source_commit'])
    assert git(core, 'rev-parse', 'HEAD') == fixture_core
    assert git(core, 'diff', '--name-only', spec['old_fixture_core'], fixture_core).splitlines() == spec['allowed_changed_paths']
    if fixture_core != spec['core_source_commit']:
        for tree in ('src','libcuda','CMakeLists.txt'):
            assert git(core,'rev-parse',fixture_core+':'+tree)==git(core,'rev-parse',spec['core_source_commit']+':'+tree)
    assert git(core, 'diff', '--name-only', spec['runtime_producer_core'], spec['old_fixture_core'], '--', 'src', 'libcuda') == ''
    assert git(runtime, 'rev-parse', 'HEAD') == spec['framework_source_commit']
    assert git(runtime/'gpu-simulator/extern/pybind11', 'rev-parse', 'HEAD') == spec['vendor']
    retained = spec['retained_files_sha256']
    for path, digest in retained.items():
        assert sha(path) == digest, 'retained asset changed: '+path
    bindings = {str(spec_path): sha(spec_path), str(Path(__file__)): sha(__file__),
        str(HERE/'common_resource_guard.py'): sha(HERE/'common_resource_guard.py'),
        str(HERE/'check_ro_origin_case.py'): sha(HERE/'check_ro_origin_case.py')}
    if a.own_pending or a.affected_native or a.joint_vrw or readonly_test:
        bindings[str(HERE/'check_native_case.py')] = sha(HERE/'check_native_case.py')
        parent_path = Path(spec['parent_receipt'])
        assert sha(parent_path) == spec['parent_receipt_sha256']
        parent = json.loads(parent_path.read_text())
        assert parent['status'] == 'OLD_RED_NEW_GREEN_MAIN_COMPILED_PENDING_AFFECTED_QUALIFICATION'
        assert parent['lease_released'] and parent['retained_assets_unchanged']
        assert parent['core_source_commit'] == spec.get('parent_core_source_commit',spec['core_source_commit'])
        assert parent['binary_sha256'] == sha(parent['binary']) == spec['new_main_sha256']
        assert parent['new_archive_sha256'] == sha(spec['new_archive'])
        assert len(parent['tests']) == 6 and all(t['expectation_verified'] for t in parent['tests'])
    if a.own_pending:
        bindings[str(HERE/'check_wad_guard_case.py')] = sha(HERE/'check_wad_guard_case.py')
        for key,digest in spec['extra_bindings'].items(): bindings[key]=digest
    if a.terminal_control:
        bindings.update(spec['control_bindings'])
        bindings[str(HERE/'replay_runtime_metrics_proposal.py')] = sha(HERE/'replay_runtime_metrics_proposal.py')
    if a.joint_gdb:
        bindings[str(HERE/'capture_vrw_abort.gdb')] = sha(HERE/'capture_vrw_abort.gdb')
        failed = json.loads(Path(spec['failed_native_receipt']).read_text())
        assert sha(spec['failed_native_receipt']) == spec['failed_native_receipt_sha256']
        assert failed['actual_exit'] == -6 and not failed['expectation_verified']
        assert sha(failed['command'][0]) == failed['binary_sha256'] == spec['failed_native_binary_sha256']
    bindings.update(spec['input_sha256'])
    for name in spec['allowed_changed_paths']:
        bindings[str(core/name)] = sha(core/name)
    for path, digest in bindings.items():
        assert sha(path) == digest
    identity = dict(campaign_id=CAMPAIGN, authority=AUTHORITY,
        control_source_commit=git(REPO, 'rev-parse', 'HEAD'), driver_sha256=sha(__file__),
        spec_sha256=sha(spec_path), core_source_commit=spec['core_source_commit'],
        fixture_source_core_commit=fixture_core,
        framework_source_commit=spec['framework_source_commit'], vendor=spec['vendor'],
        retained_runtime_core=spec['runtime_producer_core'],
        retained_main_sha256=spec['retained_main_sha256'],
        build_directory=str(build), output_directory=str(out))
    expected = dict(identity, owner='A', phase='A_WAD_OWN_PENDING_INCREMENTAL' if a.own_pending else
        'A_RETAINED_LOG_E_PARSER_CONTROL' if a.terminal_control else
        'A_FAILED_SHARED_VRW_GDB' if a.joint_gdb else
        'A_SHARED_VRW_CONTROLLED_PARTITION' if a.joint_vrw else
        'A_RO_ORIGIN_AFFECTED20' if a.affected_native else 'A_RO_ORIGIN_INCREMENTAL_OLD_RED_NEW_GREEN',
        approved=True, full_applications_permitted=False, execution_host=socket.gethostname(),
        reserved_cpu_units=1, reserved_memory_bytes=8*GIB,
        reserved_build_growth_bytes=spec['build_growth_bytes'],
        reserved_result_bytes=spec['result_growth_bytes'],
        workspace_disk_policy=spec['expected_E_workspace_policy'])
    if not a.execute:
        print(json.dumps(dict(status='REQUEST_ONLY_NO_COMPILE_NATIVE_OR_LEASE',
            expected_E_admission=expected, planned_native_cases=spec['cases'],
            command_scope='one gpu-cache.cc compile, unchanged fixture links, Core27oldred/newgreen, finite affected checks, new mainlink; no fullapp' if a.own_pending else
                'one bounded retained-log parsercontrol, no simulator/CPP/acceptance' if a.terminal_control else
                'oneGDB replay ofexactfailedfinitefixture; no compilation/main/application' if a.joint_gdb else
                'one previouslyunrun V/R/W controlledfixture compile/link/case; no production/main rebuild' if a.joint_vrw else
                'three links+20 affected native; no C++ compilation/main relink' if a.affected_native else
                'one fixture object, old link, one gpu-cache object, copied single-member archive, new link, six native cases, new main link'), indent=2))
        return
    assert a.via_e_api != bool(a.admission), 'choose published E API or exact E file, never an implicit grant'
    admission_bytes = None
    admission = None
    if a.admission:
        assert a.admission.is_file()
        admission_bytes = a.admission.read_bytes()
        admission = json.loads(admission_bytes)
        for key, value in expected.items():
            assert admission.get(key) == value, 'E admission mismatch: '+key
        assert admission['results_budget_status'] == 'PASS'
    assert not git(REPO, 'status', '--porcelain', '--untracked-files=no')
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    out.mkdir()
    report = dict(identity, schema='EP_L2_A_RO_ORIGIN_REPAIR_RECEIPT_V1', status='PREFLIGHT',
        compiler_started=False, application_starts=0, independent_qualification=False,
        commands=[], tests=[], retained_assets_unchanged=False,
        requested_E_resources={k:v for k,v in expected.items() if k != 'approved'},
        admission_method='PUBLISHED_E_RESERVE_WORK_API' if a.via_e_api else 'E_FILE_AND_PUBLISHED_API',
        admission_sha256=sha(a.admission) if a.admission else None,
        memory_floor_bytes=64*GIB)
    save = lambda: put(out/'RECEIPT.json', report)
    registry = lease = lock = None
    active = dict(pid=None, ever_started=False)
    try:
        client = json.loads((SHARED/'mechanism_study_20261019_v1/CLIENT_CONTRACT.json').read_text())
        if a.own_pending: assert client['source_publication_commit']==spec['E_source_expected']
        api = Path(client['resource_lease_api'])
        assert sha(api) == client['resource_lease_api_sha256']
        if admission:
            assert sha(api) == admission['resource_client_sha256']
        sys.path.insert(0, str(api.parent))
        from coordinator import Coordinator, tooling_binding, retained_tree_bytes, local_resources
        from run import process_tree_rss
        tooling_binding()
        registry = Coordinator()
        policy = registry.work_disk_policy()
        assert policy == spec['expected_E_workspace_policy']
        bindings.update({str(Path(client['execution_worktree'])/name): digest
                         for name, digest in client['source_files'].items()})
        supervisor = runtime/spec['supervisor']
        assert sha(supervisor) == spec['supervisor_sha256']
        bindings[str(supervisor)] = spec['supervisor_sha256']
        module = importlib.util.spec_from_file_location('origin_owned_supervisor', supervisor)
        guard = importlib.util.module_from_spec(module)
        module.loader.exec_module(guard)
        report.update(E_source_publication=client['source_publication_commit'],
            E_resource_api_sha256=sha(api), E_workspace_disk_policy=policy,
            authorized_task_floor_bytes=policy['disk_floor_bytes'],
            monitor_reserve_bytes=policy['monitor_reserve_bytes'],
            disk_floor_bytes=policy['disk_floor_bytes']+policy['monitor_reserve_bytes'])
        lock = open('/workspace/ep_l2_ms20261019_shared/A_BUILD.lock', 'a+')
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)

        bounded_deadline = time.monotonic()+1800

        def resources():
            assert time.monotonic() < bounded_deadline, 'bounded incremental build/native lifetime exceeded'
            if admission:
                assert time.time() < admission['valid_until_unix'] and a.admission.read_bytes() == admission_bytes
            for path, digest in bindings.items():
                assert sha(path) == digest, 'bound source/input changed: '+path
            live = local_resources()
            share = os.statvfs('/root/share')
            written = retained_tree_bytes(out)
            built = None if readonly_test else retained_tree_bytes(build) if build.exists() else 0
            rss = process_tree_rss(active['pid']) if active['pid'] else 0
            check_runtime(report, out, live, share.f_bavail*share.f_frsize, written, built, rss,
                spec['result_growth_bytes'], spec['build_growth_bytes'], spec['build_growth_bytes'],
                memory_limit=8*GIB)
            if built is not None:
                report['own_build_bytes_peak'] = max(built, report.get('own_build_bytes_peak', 0))
            report['own_result_bytes_peak'] = max(written, report.get('own_result_bytes_peak', 0))
            return live

        resources()
        growth = spec['build_growth_bytes']+spec['result_growth_bytes']
        allocation = registry.reserve_work('A', 'test' if readonly_test else 'build', 1, 8*GIB, growth,
            out if readonly_test else build,
            result_growth_bytes=spec['result_growth_bytes'])
        lease = allocation['lease_id']
        report.update(lease_id=lease, resource_allocation=allocation,
            E_central_admission='GRANTED_BY_PUBLISHED_RESERVE_WORK',
            E_results_and_shared_resource_gate='PASS_AT_ATOMIC_RESERVATION')
        assert allocation['role'] == 'A' and allocation['kind'] == ('MECHANISM_TEST' if readonly_test else 'MECHANISM_BUILD')
        assert allocation['experiment_id'] == CAMPAIGN
        assert allocation['cpu_units'] == 1 and allocation['memory_bytes'] == 8*GIB
        assert allocation['disk_growth_bytes'] == growth
        assert allocation['result_growth_bytes'] == spec['result_growth_bytes']
        assert all(allocation[k] == value for k, value in policy.items())
        resources()
        if not readonly_test:
            build.mkdir()
        temp_root = out if readonly_test else build
        temp = temp_root/'tmp'
        temp.mkdir()
        env = dict(os.environ, GPGPUSIM_ROOT=str(core), CUDA_INSTALL_PATH='/usr/local/cuda-11.8',
            TMPDIR=str(temp), TMP=str(temp), TEMP=str(temp), XDG_CACHE_HOME=str(temp_root/'cache'),
            PYTHONDONTWRITEBYTECODE='1', PYTHONPYCACHEPREFIX=str(temp_root/'cache/python'),
            CCACHE_DISABLE='1', CCACHE_DIR=str(temp_root/'cache/ccache'), CUDA_CACHE_DISABLE='1',
            CUDA_CACHE_PATH=str(temp_root/'cache/cuda'), OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1')
        if a.joint_gdb:
            report['GDB_child_only_environment_removed'] = {
                key:env.pop(key) for key in ('PYTHONHOME','PYTHONPATH') if key in env}
        report['environment_write_roots'] = {key: env[key] for key in ('TMPDIR','TMP','TEMP',
            'XDG_CACHE_HOME','PYTHONPYCACHEPREFIX','CCACHE_DIR','CUDA_CACHE_PATH')}

        def bind(pid):
            active.update(pid=pid, ever_started=True)
            return registry.bind_work_process(lease, 'A', pid)

        def run(command, name, timeout=600):
            try:
                resources()
                row = guard.run_owned(command, name, out, env, report, save, resources, bind, timeout)
                resources()
                return row
            finally:
                active['pid'] = None

        if a.own_pending:
            report.update(status='LINKING_CORE27_OLD_RED',parent_core_source_commit=spec['parent_core_source_commit'],
                parent_main_sha256=spec['new_main_sha256'],scope='FINITE_NATIVE_REPAIR_NOT_APP_OR_E_ACCEPTANCE',
                trace='NO_APPLICATION_TRACE_EXECUTED',old_assertions_preserved=True)
            save()
            archive=Path(spec['new_archive'])
            fixture_objects={}
            def link_target(target, destination, library):
                command=shlex.split((old/'gpgpu-sim/CMakeFiles'/ (target+'.dir')/'link.txt').read_text())
                if target in spec['missing_fixture_targets'] and target not in fixture_objects:
                    source=spec['missing_fixture_targets'][target]['source']
                    obj=build/(target+'.fixture.o')
                    ccflags=[x.replace(spec['retained_core'],str(core)) for x in flags(old/'gpgpu-sim/CMakeFiles'/(target+'.dir')/'flags.make')]
                    run(['/usr/bin/c++',*ccflags,'-c',str(core/source),'-o',str(obj)],target+'_fixture_compile')
                    fixture_objects[target]=obj
                for i,word in enumerate(command):
                    if i and command[i-1]=='-o': command[i]=str(destination)
                    elif word.endswith('.a') and not word.startswith('/'):
                        command[i]=str(library) if word.endswith('/libgpgpusim.a') else str(old/'gpgpu-sim'/word)
                    elif word.endswith('.o') and not word.startswith('/'):
                        command[i]=str(fixture_objects[target]) if target in fixture_objects else str(old/'gpgpu-sim'/word)
                run(command,destination.name+'_link')
            def case_run(case, executable):
                detail=out/(case['id']+'.native.json')
                run([sys.executable,'-B',str(HERE/'check_wad_guard_case.py'),
                    '--case-json',json.dumps(case),'--receipt',str(detail),'--',str(executable),*case['arguments']],case['id'],180)
                row=json.loads(detail.read_text());assert row['expectation_verified'] and row['binary_sha256']==sha(executable)
                report['tests'].append(dict(evidence=str(detail),sha256=sha(detail),**row));save()
            if spec.get('old_red_native_receipt'):
                detail=Path(spec['old_red_native_receipt']);assert sha(detail)==spec['old_red_native_receipt_sha256']
                row=json.loads(detail.read_text());old_exe=Path(row['command'][0])
                assert row['actual_exit']==-6 and row['expectation_verified'] and all(row['terminal_checks'].values())
                assert row['command'][1:]==spec['cases'][0]['arguments'] and row['case']==spec['cases'][0]['id']
                assert sha(old_exe)==row['binary_sha256'] and sha(row['raw_log'])==row['raw_log_sha256']
                report['tests'].append(dict(evidence=str(detail),sha256=sha(detail),reused_verified_old_red=True,**row));save()
            else:
                old_exe=build/'ep_l2_ms_victim_production_core27_old'
                link_target('ep_l2_ms_victim_production',old_exe,archive)
                case_run(spec['cases'][0],old_exe)
            if spec.get('retained_compiled_archive'):
                new_archive=Path(spec['retained_compiled_archive'])
                assert sha(new_archive)==spec['retained_compiled_archive_sha256']
                partial=Path(spec['retained_partial_receipt']);assert sha(partial)==spec['retained_partial_receipt_sha256']
                partial_report=json.loads(partial.read_text());assert partial_report['lease_released'] and len(partial_report['archive_members'])==22
                report['archive_members']=partial_report['archive_members']
                executables={key:Path(value) for key,value in spec['retained_test_executables'].items()}
                report.update(status='COMPILING_ONLY_TWO_SUPPORTED_FIXTURE_SELECTORS',compiler_started=True);save()
                for target in spec['missing_fixture_targets']:
                    destination=build/target;link_target(target,destination,new_archive);executables[target]=destination
                if spec.get('retained_main'):
                    main_binary=Path(spec['retained_main']);assert sha(main_binary)==spec['retained_main_sha256']
                    report.update(binary=str(main_binary),binary_sha256=sha(main_binary),new_archive=str(new_archive),new_archive_sha256=sha(new_archive),main_relinked=False)
                else:
                    report.update(status='LINKING_NEW_MAIN_BEFORE_REMAINING_FINITE_CHECKS');save()
                    command=shlex.split((old/'CMakeFiles/accel-sim.out.dir/link.txt').read_text())
                    for i,word in enumerate(command):
                        if i and command[i-1]=='-o':command[i]=str(build/'accel-sim.out')
                        elif word.endswith('.o') or (word.endswith('.a') and not word.startswith('/')):
                            command[i]=str(new_archive) if word.endswith('/libgpgpusim.a') else str(old/word)
                    run(command,'new_main_link')
                    report.update(binary=str(build/'accel-sim.out'),binary_sha256=sha(build/'accel-sim.out'),new_archive=str(new_archive),new_archive_sha256=sha(new_archive))
                save()
                for case in spec['cases'][1:]:
                    if case['id'] in spec['completed_new_cases']:
                        detail=Path(spec['completed_new_cases'][case['id']]);row=json.loads(detail.read_text())
                        assert row['expectation_verified'] and row['actual_exit']==0 and all(row['terminal_checks'].values())
                        assert sha(row['raw_log'])==row['raw_log_sha256']
                        report['tests'].append(dict(evidence=str(detail),sha256=sha(detail),reused_verified_same_archive=True,**row));save()
                    else:case_run(case,executables[case['target']])
                if spec.get('observer_pair_case_ids'):
                    lines=[]
                    for name in spec['observer_pair_case_ids']:
                        record=next(row for row in report['tests'] if row['case']==name)
                        raw=Path(record['raw_log']).read_text(errors='replace')
                        values=[line for line in raw.splitlines() if line.startswith('A_COMMON_FIXTURE|SEMANTIC|')]
                        assert len(values)==1;lines.append(values[0])
                    assert len(lines)==2 and lines[0]==lines[1]
                    report['observer_on_off_semantic_equal']=True;report['observer_semantic_fingerprint']=lines[0]
                for path,digest in retained.items():assert sha(path)==digest
                report.update(status='CORE27_OLD_RED_FIXED_NEW_GREEN_MAIN_COMPILED_PENDING_E',
                    retained_assets_unchanged=True,test_binaries={key:dict(path=str(value),sha256=sha(value)) for key,value in executables.items()},
                    production_translation_units_compiled=0,prior_production_translation_units_reused=1,
                    fixture_translation_units_compiled=len(fixture_objects),new_source_passes=len(spec['cases'])-1,
                    reused_new_source_case_passes=len(spec['completed_new_cases']),fresh_new_source_case_passes=len(spec['cases'])-1-len(spec['completed_new_cases']),
                    old_source_expected_asserts=1,generated_build_string_unchanged=True,original_banner_is_not_new_producer_identity=True,
                    E006_samecause='SAME_ASSERTION_ONLY_PENDING_E_COUNTED_REPLAY_STACK',full_applications_by_A=0)
                return

            report.update(status='COMPILING_ONE_GPU_CACHE_MEMBER',compiler_started=True);save()
            compile_flags=[x.replace(spec['retained_core'],str(core)) for x in flags(old/'gpgpu-sim/src/gpgpu-sim/CMakeFiles/gpgpusim.dir/flags.make')]
            run(['/usr/bin/c++',*compile_flags,'-c',str(core/'src/gpgpu-sim/gpu-cache.cc'),'-o',str(build/'gpu-cache.cc.o')],'changed_gpu_cache_compile')
            new_archive=build/'libgpgpusim.a';shutil.copy2(archive,new_archive)
            run(['/usr/bin/ar','r',str(new_archive),str(build/'gpu-cache.cc.o')],'one_member_archive')
            names=subprocess.check_output(['/usr/bin/ar','t',str(archive)],text=True).splitlines()
            assert names==subprocess.check_output(['/usr/bin/ar','t',str(new_archive)],text=True).splitlines()
            import hashlib
            report['archive_members']={}
            for name in names:
                hashes=[hashlib.sha256(subprocess.check_output(['/usr/bin/ar','p',str(f),name])).hexdigest() for f in (archive,new_archive)]
                assert (hashes[0]!=hashes[1]) == (name=='gpu-cache.cc.o')
                report['archive_members'][name]=dict(old_sha256=hashes[0],new_sha256=hashes[1])
            executables={}
            for target in sorted({case['target'] for case in spec['cases'][1:]}):
                exe=build/target;link_target(target,exe,new_archive);executables[target]=exe
            report.update(status='EXECUTING_AFFECTED_FINITE_NATIVE');save()
            for case in spec['cases'][1:]:case_run(case,executables[case['target']])
            command=shlex.split((old/'CMakeFiles/accel-sim.out.dir/link.txt').read_text())
            for i,word in enumerate(command):
                if i and command[i-1]=='-o': command[i]=str(build/'accel-sim.out')
                elif word.endswith('.o') or (word.endswith('.a') and not word.startswith('/')):
                    command[i]=str(new_archive) if word.endswith('/libgpgpusim.a') else str(old/word)
            run(command,'new_main_link')
            for path,digest in retained.items():assert sha(path)==digest,'retained changed: '+path
            report.update(status='CORE27_OLD_RED_FIXED_NEW_GREEN_MAIN_COMPILED_PENDING_E',
                retained_assets_unchanged=True,binary=str(build/'accel-sim.out'),binary_sha256=sha(build/'accel-sim.out'),
                new_archive=str(new_archive),new_archive_sha256=sha(new_archive),old_red_binary=str(old_exe),old_red_binary_sha256=sha(old_exe),
                test_binaries={key:dict(path=str(value),sha256=sha(value)) for key,value in executables.items()},
                production_translation_units_compiled=1,fixture_translation_units_compiled=len(fixture_objects),
                new_source_passes=len(spec['cases'])-1,old_source_expected_asserts=1,
                generated_build_string_unchanged=True,original_banner_is_not_new_producer_identity=True,
                E006_samecause='SAME_ASSERTION_ONLY_CAUSAL_STACK_PENDING_E_EXACT_DELIVERY',full_applications_by_A=0)
            return

        if a.terminal_control:
            report.update(status='BOUNDED_E_PARSER_PROPOSAL_CONTROL',compiler_started=False,
                application_correctness=False,scope='READ_ONLY_RETAINED_LOG_NO_SIMULATOR_OR_E_ACCEPTANCE')
            save()
            detail=out/'PARSER_CONTROL.json'
            run([sys.executable,'-B',str(HERE/'replay_runtime_metrics_proposal.py'),
                '--spec',str(spec_path),'--out',str(detail)],'retained_log_parser_control',120)
            result=json.loads(detail.read_text())
            assert result['status']=='PROPOSED_E_PARSER_CONTROLS_PASS_NOT_APPLICATION_ACCEPTANCE'
            for path,digest in retained.items():assert sha(path)==digest
            report.update(status=result['status'],control_result=str(detail),control_result_sha256=sha(detail),
                controls=result['controls'],retained_assets_unchanged=True,accepted_application_result=False,
                central_science_ledger_edited=False,live_E_source_edited=False)
            return

        if a.joint_gdb:
            report.update(status='DIAGNOSING_EXACT_FAILED_CONTROLLED_FIXTURE', compiler_started=False,
                native_expected_failure_only=True, application_correctness=False,
                failed_native_receipt=spec['failed_native_receipt'],
                scope='GDB_FINITE_CONTROLLED_PARTITION_NOT_FULL_APPLICATION')
            save()
            run(['/usr/bin/gdb','-q','-nx','-batch','-x',str(HERE/'capture_vrw_abort.gdb'),
                '--args',*failed['command']], 'failed_fixture_gdb',180)
            text = (out/'failed_fixture_gdb.log').read_text(errors='replace')
            assert 'SIGABRT' in text and 'VRW_FRAME|function=' in text and 'submit_ro' in text
            for path,digest in retained.items():
                assert sha(path)==digest,'retained asset changed: '+path
            report.update(status='FAILED_CONTROLLED_FIXTURE_GDB_CAPTURED_NO_PASS',
                observed_frame_lines=[s for s in text.splitlines() if s.startswith('VRW_')],
                retained_assets_unchanged=True,native_success_claim=False,
                full_application_starts=0)
            return

        if a.joint_vrw:
            report.update(status='COMPILING_PREVIOUSLY_UNRUN_SHARED_VRW_FIXTURE', compiler_started=True,
                binary=parent['binary'], binary_sha256=parent['binary_sha256'],
                scope='CONTROLLED_PRODUCTION_PARTITION_EXTERNAL_VERSION_REFERENCE_NOT_NATIVE_DRAM_OR_APP',
                independent_C_synthetic_scope_review='PENDING_NOT_WAIVED',
                parent_receipt=str(parent_path), parent_receipt_sha256=sha(parent_path))
            save()
            compile_args = [s.replace(spec['retained_core'], str(core)) for s in
                flags(old/'gpgpu-sim/CMakeFiles/ep_l2_ms_victim_native.dir/flags.make')]
            run(['/usr/bin/c++', *compile_args, '-c', str(core/spec['fixture_source']),
                '-o', str(build/'joint_fixture.o')], 'joint_fixture_compile')
            args = shlex.split((old/'gpgpu-sim/CMakeFiles/ep_l2_ms_victim_native.dir/link.txt').read_text())
            command = []
            exe = build/'ep_l2_ms_vrw_interleave'
            for i, word in enumerate(args):
                if word.endswith('.o'):
                    word = str(build/'joint_fixture.o')
                elif i and args[i-1] == '-o':
                    word = str(exe)
                elif word.endswith('.a') and not word.startswith('/'):
                    word = spec['new_archive'] if word.endswith('/libgpgpusim.a') else str(old/'gpgpu-sim'/word)
                command.append(word)
            run(command, 'joint_fixture_link')
            case = spec['cases'][0]
            detail = out/(case['id']+'.native.json')
            run([sys.executable,str(HERE/'check_native_case.py'),'--expected-exit','0',
                '--required-terminal',case['required_terminal'],'--receipt',str(detail),
                '--',str(exe),*case['arguments']],case['id'],120)
            row = json.loads(detail.read_text())
            assert row['expectation_verified'] and sha(exe) == row['binary_sha256']
            report['tests'].append(dict(case=case['id'],evidence=str(detail),sha256=sha(detail),**row))
            for path,digest in retained.items():
                assert sha(path)==digest, 'retained asset changed: '+path
            report.update(status='SHARED_VRW_CONTROLLED_FIXTURE_PASS_PENDING_C_E_REVIEW',
                retained_assets_unchanged=True,fixture_binary=str(exe),fixture_sha256=sha(exe),
                production_recompiled=False,main_relinked=False,application_correctness=False,
                native_DRAM_timing_or_bytes_claim=False)
            return

        if a.affected_native:
            report.update(status='RELINKING_THREE_AFFECTED_FIXTURES', compiler_started=False,
                link_only=True, binary=parent['binary'], binary_sha256=parent['binary_sha256'],
                parent_receipt=str(parent_path), parent_receipt_sha256=sha(parent_path))
            save()
            for target in spec['targets']:
                args = shlex.split((old/f'gpgpu-sim/CMakeFiles/{target}.dir/link.txt').read_text())
                command = []
                for i, word in enumerate(args):
                    if i and args[i-1] == '-o':
                        word = str(build/target)
                    elif word.endswith('.o') or (word.endswith('.a') and not word.startswith('/')):
                        word = spec['new_archive'] if word.endswith('/libgpgpusim.a') else str(old/'gpgpu-sim'/word)
                    command.append(word)
                run(command, 'link_'+target)
            fixture_hashes = {target:sha(build/target) for target in spec['targets']}
            signatures = []
            for case in spec['cases']:
                detail = out/(case['id']+'.native.json')
                native_command = [str(build/case['target']), *case['native_command'][1:]]
                report['status'] = 'AFFECTED_NATIVE_'+case['id']
                save()
                run([sys.executable, str(HERE/'check_native_case.py'), '--expected-exit', str(case['expected_exit']),
                    '--required-terminal', case['required_terminal'], '--receipt', str(detail), '--', *native_command],
                    case['id'], case['timeout_seconds'])
                row = json.loads(detail.read_text())
                assert row['expectation_verified'] and row['binary_sha256'] == fixture_hashes[case['target']]
                report['tests'].append(dict(case=case['id'], target=case['target'], suite=case['suite'],
                    evidence=str(detail), sha256=sha(detail), **row))
                if case.get('compare_group') == 'F_observer':
                    lines = [line for line in Path(row['raw_log']).read_text().splitlines()
                             if line.startswith('A_COMMON_FIXTURE|SEMANTIC|')]
                    assert len(lines) == 1
                    signatures.append(dict(case=case['id'], line=lines[0]))
                save()
            assert len(signatures) == 2 and signatures[0]['line'] == signatures[1]['line']
            for path, digest in retained.items():
                assert sha(path) == digest, 'retained asset changed: '+path
            report.update(status='AFFECTED_RO20_ACTUAL_PASS_PENDING_E_QUALIFICATION',
                fixture_binary_sha256=fixture_hashes, observer_semantics=signatures,
                retained_assets_unchanged=True, native_exit0_passes=len(report['tests']),
                old_native_passes_not_relabelled=True, new_CPP_translation_units=0,
                main_relinked=False, original64_all_fresh=False)
            return

        def compile_flags(path):
            return [s.replace(spec['retained_core'], str(core)) for s in flags(path)]

        def link_command(target, new_archive=False):
            ref = old/'gpgpu-sim/CMakeFiles/ep_l2_ro_partition.dir/link.txt'
            args = shlex.split(ref.read_text())
            result = []
            for i, word in enumerate(args):
                if word.endswith('test_ro_partition.cc.o'):
                    word = str(build/'origin_fixture.o')
                elif i and args[i-1] == '-o':
                    word = str(build/target)
                elif word.endswith('.a') and not word.startswith('/'):
                    word = str(old/'gpgpu-sim'/word)
                    if new_archive and word.endswith('/src/gpgpu-sim/libgpgpusim.a'):
                        word = str(build/'libgpgpusim.a')
                result.append(word)
            return result

        report.update(status='COMPILING_ONE_NATIVE_FIXTURE', compiler_started=True)
        save()
        run(['/usr/bin/c++', *compile_flags(old/'gpgpu-sim/CMakeFiles/ep_l2_ro_partition.dir/flags.make'),
            '-c', str(core/'tests/ep_l2/test_ro_detailed_origin.cc'), '-o', str(build/'origin_fixture.o')], 'fixture_compile')
        run(link_command('ep_l2_ro_detailed_origin_old'), 'old_link')
        old_exe = build/'ep_l2_ro_detailed_origin_old'

        def native(case, exe):
            detail = out/(case['id']+'.native.json')
            command = [str(exe), *spec['native_input_arguments'], str(case['T']), str(case['M'])]
            report['status'] = 'NATIVE_'+case['id']
            save()
            run([sys.executable, str(HERE/'check_ro_origin_case.py'), '--expected-exit', str(case['exit']),
                '--required-terminal', case['terminal'], '--receipt', str(detail), '--', *command], case['id'], 120)
            row = json.loads(detail.read_text())
            assert row['expectation_verified'] and row['binary_sha256'] == sha(exe)
            report['tests'].append(dict(case=case['id'], evidence=str(detail), sha256=sha(detail), **row))
            save()

        for case in spec['cases'][:2]:
            native(case, old_exe)
        run(['/usr/bin/c++', *compile_flags(old/'gpgpu-sim/src/gpgpu-sim/CMakeFiles/gpgpusim.dir/flags.make'),
            '-c', str(core/'src/gpgpu-sim/gpu-cache.cc'), '-o', str(build/'gpu-cache.cc.o')], 'changed_gpu_cache_compile')
        old_archive = old/'gpgpu-sim/src/gpgpu-sim/libgpgpusim.a'
        new_archive = build/'libgpgpusim.a'
        shutil.copy2(old_archive, new_archive)
        run(['/usr/bin/ar', 'r', str(new_archive), str(build/'gpu-cache.cc.o')], 'one_member_archive')
        # All original archive members other than the recompiled translation unit
        # must remain byte-identical, without extracting another large data tree.
        old_names = subprocess.check_output(['/usr/bin/ar', 't', str(old_archive)], text=True).splitlines()
        new_names = subprocess.check_output(['/usr/bin/ar', 't', str(new_archive)], text=True).splitlines()
        assert old_names == new_names and old_names.count('gpu-cache.cc.o') == 1
        import hashlib
        archive_members = {}
        for name in old_names:
            hashes = [hashlib.sha256(subprocess.check_output(['/usr/bin/ar','p',str(f),name])).hexdigest()
                      for f in (old_archive,new_archive)]
            assert (hashes[0] != hashes[1]) == (name == 'gpu-cache.cc.o')
            archive_members[name] = dict(old_sha256=hashes[0], new_sha256=hashes[1])
        report['archive_members'] = archive_members
        run(link_command('ep_l2_ro_detailed_origin_new', True), 'new_link')
        for case in spec['cases'][2:]:
            native(case, build/'ep_l2_ro_detailed_origin_new')
        # Same retained actual frontend objects and unchanged archives; only the
        # reviewed gpu-cache member is replaced. No configure or version update.
        command = shlex.split((old/'CMakeFiles/accel-sim.out.dir/link.txt').read_text())
        for i, word in enumerate(command):
            if i and command[i-1] == '-o':
                command[i] = str(build/'accel-sim.out')
            elif word.endswith('.o') or (word.endswith('.a') and not word.startswith('/')):
                command[i] = str(new_archive) if word.endswith('/libgpgpusim.a') else str(old/word)
        run(command, 'new_main_link')
        for path, digest in retained.items():
            assert sha(path) == digest, 'retained asset changed: '+path
        report.update(status='OLD_RED_NEW_GREEN_MAIN_COMPILED_PENDING_AFFECTED_QUALIFICATION',
            retained_assets_unchanged=True, binary_sha256=sha(build/'accel-sim.out'),
            binary=str(build/'accel-sim.out'), old_native_sha256=sha(old_exe),
            new_native_sha256=sha(build/'ep_l2_ro_detailed_origin_new'),
            new_archive_sha256=sha(new_archive), native_passes=len(report['tests']),
            changed_archive_members=['gpu-cache.cc.o'],
            generated_build_string_unchanged=True, original_banner_is_not_new_producer_identity=True)
    except BaseException as error:
        report.update(status='RESOURCE_LIMIT' if report.get('resource_limit') else 'STOPPED_OR_FAILED_REPAIR_NOT_RELEASED', error=repr(error))
        raise
    finally:
        if lease:
            registry.release_work(lease, 'A', 'A RO origin repair exited; '+str(out/'RECEIPT.json'),
                no_child_started=not active['ever_started'])
            report['lease_released'] = True
        if lock:
            lock.close()
        report['finished_UTC'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        finalize_limit(report, out)
        save()
        print(report['status'])


if __name__ == '__main__':
    main()
