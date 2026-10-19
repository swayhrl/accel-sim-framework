"""PREPARED_NOT_EXECUTED. Parent finite qualifier for four SEM1 view mocks.

Copy unchanged with the two payload sources into prepared_sem1_view_qualification_v2.
Only fixed readonly Git tooling children are permitted. No target/fixture/model
Popen, ptrace, external signal, new root, process adoption or runtime experiment.
Own SIGALRM bounds publication, full CPUAdmission and exactly four pure groups.
Payload imports happen only after the unchanged complete fresh R2 admission.
"""
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone


HERE = Path(__file__).resolve().parent
EX = HERE.parent
FW = HERE.parents[5]
EXPECTED_FW = Path('/workspace/worktrees/accel-sim-iscas2027-dtc-closure-exec-174-v1')
ENGINE = EX / 'prepared_runtime'
REGISTRATION = EX / 'SEM1_VIEW_CPU_REGISTRATION_V2.json'
OUTPUT = Path('/workspace/dtc-evidence-closure-20261019-v1/coordinator/sem1-view-qualification-v2')
PUBLICATION = Path(str(OUTPUT) + '-prereg/PUBLICATION_READBACK.json')
BRANCH = 'hrl/iscas2027-dtc-closure-exec-174-v1'
READBACK = 'refs/dtc-closure-readback/sem1-view-qualification-v2'
ENV = {'PATH': '/usr/bin:/bin', 'LANG': 'C', 'LC_ALL': 'C'}
TIMEOUT = 90
OUTPUT_BOUND = 1024**2
ROLE = 'SEM1_VIEW_CPU_QUALIFICATION_V2'
PRODUCER_COMMIT = 'e5cb0112ffda877a7e998b4bf4fd44e094eb4ae5'
PAYLOAD_SHA256 = {
    'fixture_terminal_view.py': '49971f39da0cf4054fbab144fca5c8d0ba38244bc5461eb58d002320c2d1a2e6',
    'test_fixture_terminal_view.py': 'c6964476b9bef585dbad16b21814e09d5af4c6b17d13783ba3b5d24b2f56d706',
}
CASES = (
    'test_group1_only_same_retained_unreaped_pidfd_Z_is_eligible',
    'test_group2_only_authority_projects_own_Z_preserving_all_resources',
    'test_group3_generic_foreign_failure_is_never_terminal_success',
    'test_group4_absent_own_and_second_foreign_failure_remain_STOP',
)
OLD39 = (
    'prepare_ag5_fixture_v2.py', 'shared_cpu_context.py', 'qualify_two_real_roots.py',
    'freeze_cpu_manifests.py', 'qualification_reuse_v2.py',
    'qualify_ag5_changed_dispatch_v2.py', 'qualify_shared_cpu_authority_v2.py',
    'qualify_real_cpu_roles_v2.py', 'FROZEN_AUTHORITY_ADAPTER_BINDING.json', 'README.md',
    'cpu_admission_v2.py', 'cpu_guard_entry.py', 'shared_authority.py',
    'external_cpu_role_manager.py', 'frozen_guarded_process.py.txt',
    'external_cpu_launch_view.py', 'PREPARED_SOURCE_SHA256.json',
    'freeze_cpu_manifests_v2.py', 'qualify_shared_cpu_authority.py', 'multi_root_cpu.py',
    'test_shared_authority.py', 'EXACT_EXTERNAL_ROLE_CONTRACTS.json',
    'ENGINE_SOURCE_BINDING.json', 'test_retired_pid_dispatch.py',
    'legacy_authority_runtime.py',
    'legacy_authority_evidence/ADDITIONAL_EXTERNAL_PROJECT_LOCK_BINDINGS.json',
    'legacy_authority_evidence/frozen_review_authority.py.txt',
    'legacy_authority_evidence/AA5_AUTHORITY_AND_FLOCK_AUDIT.json',
    'legacy_authority_evidence/EXTERNAL_PROJECT_LOCK_BINDING.json',
    'legacy_authority_evidence/SOURCE_BINDINGS.json',
    'legacy_authority_evidence/frozen_audit_site.py.txt',
    'vendor/freeze_static.py', 'vendor/authority_cpu.cc', 'vendor/authority_cpu_ag5_v2.cc',
    'vendor/mapping_roles.py', 'vendor/common.py', 'vendor/ownership.py',
    'vendor/oom_watchdog.py', 'vendor/guarded_process.py',
)


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode()


def sha(path, limit=2 * 1024**2):
    path = Path(path)
    require(path.is_file() and path.stat().st_size <= limit,
            'ONLY_BOUNDED_SOURCE_OR_METADATA_FILES:' + str(path))
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(deadline, *args):
    remaining = deadline - time.monotonic()
    require(remaining > 0, 'SEM1_VIEW_TOTAL_BOUND')
    # Fixed readonly Git tooling only. Never a test/root/fixture launcher.
    return subprocess.check_output([
        '/usr/bin/git', '--no-optional-locks', '-C', str(FW),
        '-c', 'core.fsmonitor=false', *args],
        env=ENV, text=True, timeout=remaining).strip()


def publication(deadline):
    require(PUBLICATION.stat().st_size <= 256 * 1024 and
            REGISTRATION.stat().st_size <= 256 * 1024, 'COMPACT_PUBLISHED_METADATA_REQUIRED')
    receipt = json.loads(PUBLICATION.read_bytes())
    head, tree = receipt['head'], receipt['tree']
    require(receipt['branch'] == BRANCH and receipt['readback_ref'] == READBACK and
            receipt['fetched_head'] == head and receipt['fetched_tree'] == tree,
            'EXACT_PARENT_PUBLICATION_READBACK_REQUIRED')
    require(git(deadline, 'rev-parse', 'HEAD') == head ==
            git(deadline, 'rev-parse', READBACK) and
            git(deadline, 'rev-parse', 'HEAD^{tree}') == tree ==
            git(deadline, 'rev-parse', READBACK + '^{tree}'),
            'PUBLICATION_HEAD_TREE_DEDICATED_REF_CHANGED')
    require(not git(deadline, 'status', '--porcelain'), 'CLEAN_SOURCE_REQUIRED')
    require(git(deadline, 'ls-remote', '--exit-code', 'origin', 'refs/heads/' + BRANCH)
            .splitlines() == [head + '\trefs/heads/' + BRANCH],
            'REMOTE_EXACT_PARENT_BRANCH_HEAD_CHANGED')
    files = receipt['files']
    require(isinstance(files, dict) and 43 <= len(files) <= 100,
            'COMPACT_FULL_SOURCE_AND_REGISTRATION_PUBLICATION_REQUIRED')
    for relative in files:
        path = FW / relative
        require(not Path(relative).is_absolute() and path.resolve().is_relative_to(FW)
                and path.resolve() == path, 'EXACT_PUBLISHED_FILE_PATH_REQUIRED')
    listed = git(deadline, 'ls-tree', '-r', '--full-tree', head, '--', *files).splitlines()
    blobs = {}
    for line in listed:
        item, relative = line.split('\t', 1)
        mode, kind, blob = item.split()
        require(kind == 'blob' and mode == '100644', 'REGULAR_SOURCE_BLOB_REQUIRED')
        blobs[relative] = blob
    require(set(blobs) == set(files), 'PUBLISHED_BLOB_POPULATION_CHANGED')
    for relative, binding in files.items():
        require(blobs[relative] == binding['blob'] and
                sha(FW / relative) == binding['sha256'],
                'PUBLISHED_SOURCE_OR_BLOB_CHANGED:' + relative)
    require(str(REGISTRATION.relative_to(FW)) in files, 'REGISTRATION_NOT_PUBLISHED')
    registration = json.loads(REGISTRATION.read_bytes())
    expected = {str(ENGINE / name) for name in OLD39}
    expected.update(str(HERE / name) for name in
                    ('qualify_view.py', 'fixture_terminal_view.py', 'test_fixture_terminal_view.py'))
    sources = registration['source_sha256']
    require(len(OLD39) == 39 and len(expected) == 42 and set(sources) == expected
            and len(canonical(sources)) <= 64 * 1024, 'EXACT_UNCHANGED39_PLUS_NEW3_SOURCE_CLOSURE_REQUIRED')
    for absolute, expected_sha in sources.items():
        path = Path(absolute)
        relative = str(path.relative_to(FW))
        require(relative in files and files[relative]['sha256'] == expected_sha,
                'SOURCE_BINDING_NOT_IN_REMOTE_PUBLICATION:' + absolute)
    for name, expected_sha in PAYLOAD_SHA256.items():
        require(sources[str(HERE / name)] == expected_sha,
                'EXACT_SEM1_PRODUCER_VIEW_TEST_COPY_REQUIRED:' + name)
    require(registration['status'] == 'REGISTERED_FOR_SEM1_VIEW_CPU_QUALIFICATION_ONLY' and
            registration['producer_commit'] == PRODUCER_COMMIT and
            registration['timeout_seconds'] == TIMEOUT and
            registration['output_bound_bytes'] == OUTPUT_BOUND and
            registration['output'] == str(OUTPUT) and
            registration['publication'] == str(PUBLICATION) and
            registration['admission']['disk_floor_exclusive_bytes'] == 5 * 1024**3 and
            registration['new_target_roots'] == registration['simulation_starts'] == 0 and
            registration['declared_case_names'] == list(CASES) and
            registration['environment'] == ENV, 'FIXED_FINITE_FOUR_MOCK_CPU_ROLE_REQUIRED')
    roles = registration['gate_roles']
    require(len(roles) == 1 and roles[0]['name'] == ROLE and
            roles[0]['cwd'] == str(FW) and roles[0]['executable'] == '/usr/bin/python3.10' and
            roles[0]['argvs'] == [['/usr/bin/python3.10', '-I', '-B', str(HERE / 'qualify_view.py')]] and
            roles[0]['source_sha256'] == sources and
            sha(roles[0]['executable'], 16 * 1024**2) == roles[0]['executable_sha256'],
            'EXACT_SOURCE_BOUND_FOREGROUND_SELF_ROLE_REQUIRED')
    return registration, receipt


def module_binding(module, path, sources):
    require(Path(module.__file__).resolve() == path and sha(path) == sources[str(path)],
            'ACTUAL_IMPORTED_FILE_OR_SOURCE_CHANGED:' + str(path))


def four_groups(view, tests):
    # These public methods execute pure mocks only; __init__ is never called.
    import unittest
    require(tests.FixtureTerminalView is view.FixtureTerminalView and
            tests.eligible_terminal is view.eligible_terminal and
            tests._OwnRootTerminal is view._OwnRootTerminal and
            tests.OwnRootIdentityUnresolved is view.OwnRootIdentityUnresolved,
            'TESTS_MUST_BIND_ACTUAL_REGISTERED_VIEW_MODULE')
    case = tests.PureTerminalViewBoundaries
    require(unittest.TestLoader().getTestCaseNames(case) == list(CASES),
            'ONLY_FOUR_DECLARED_BOUNDARY_GROUPS')
    result = unittest.TestResult()
    result.failfast = True
    unittest.TestSuite([case(name) for name in CASES]).run(result)
    failures = [{'case': str(test), 'detail': detail[-4096:]} for test, detail in
                result.failures + result.errors]
    return dict(status='PASS_FOUR_DECLARED_PURE_VIEW_GROUPS_ONLY' if
        result.wasSuccessful() and result.testsRun == 4 and not result.skipped
        else 'STOP_PURE_VIEW_BOUNDARY_QUALIFICATION',
        actual_groups_started=result.testsRun,
        actual_case_names=list(CASES[:result.testsRun]), failures=failures,
        skipped=[str(test) for test, reason in result.skipped],
        unexpected_successes=[str(test) for test in result.unexpectedSuccesses],
        declared_synthetic=True, actual_pidfd_or_live_process_qualification=False,
        actual_fixture_cases=0, new_target_roots=0, simulation_starts=0)


def main():
    require(FW == EXPECTED_FW and HERE.name == 'prepared_sem1_view_qualification_v2' and
            sys.argv == [str(HERE / 'qualify_view.py')] and Path.cwd() == FW and
            dict(os.environ) == ENV and sys.executable == '/usr/bin/python3.10' and
            sys.flags.isolated and sys.flags.dont_write_bytecode,
            'EXACT_PARENT_ENTRY_CWD_ARGV_CLEAN_ENV_REQUIRED')
    require(signal.getitimer(signal.ITIMER_REAL) == (0.0, 0.0),
            'MUST_NOT_REPLACE_ACTIVE_TIMER')
    prior_handler = signal.getsignal(signal.SIGALRM)
    def own_timeout(number, frame):
        raise TimeoutError('SEM1_VIEW_QUALIFICATION_90S_TOTAL_BOUND')
    signal.signal(signal.SIGALRM, own_timeout)
    signal.setitimer(signal.ITIMER_REAL, TIMEOUT)
    began = time.monotonic()
    deadline = began + TIMEOUT
    written = 0
    created = False
    report = dict(status='STOP_SEM1_VIEW_CPU_QUALIFICATION', admission_calls=0,
                  actual_groups_started=0, declared_synthetic=True,
                  actual_pidfd_or_live_process_qualification=False,
                  actual_fixture_cases=0, new_target_roots=0, simulation_starts=0,
                  no_retry=True)
    def write(name, value):
        nonlocal written
        data = canonical(value) + b'\n'
        limit = OUTPUT_BOUND if name == 'ENTRY_TERMINAL.json' else OUTPUT_BOUND - 128 * 1024
        require(written + len(data) <= limit, 'COMPACT_OUTER_OUTPUT_BOUND')
        with (OUTPUT / name).open('xb') as stream:
            stream.write(data)
        written += len(data)
    try:
        OUTPUT.mkdir(parents=True, exist_ok=False)
        created = True
        write('ENTRY_START.json', dict(utc=datetime.now(timezone.utc).isoformat(),
            pid=os.getpid(), argv=sys.argv, cwd=str(FW), timeout_seconds=TIMEOUT,
            output_bound_bytes=OUTPUT_BOUND, scope='FOUR_PURE_SEM1_VIEW_MOCK_GROUPS_ONLY'))
        registration, published = publication(deadline)
        binding = dict(registration_sha256=sha(REGISTRATION), publication_sha256=sha(PUBLICATION),
            publication_head=published['head'], publication_tree=published['tree'],
            source_sha256=registration['source_sha256'])
        report.update(binding)
        write('SOURCE_PUBLICATION_BINDING.json', dict(binding, readback_ref=READBACK,
            remote_branch=BRANCH, clean=True))
        # Only necessary frozen admission bootstrap imports precede fresh R2.
        sys.path.insert(0, str(ENGINE / 'vendor'))
        sys.path.insert(0, str(ENGINE))
        from cpu_admission_v2 import CPUAdmission
        import cpu_admission_v2
        module_binding(cpu_admission_v2, ENGINE / 'cpu_admission_v2.py', registration['source_sha256'])
        gate = CPUAdmission(registration, registration['gate_roles'])
        for name, path in (
                ('shared_authority', ENGINE / 'shared_authority.py'),
                ('legacy_authority_runtime', ENGINE / 'legacy_authority_runtime.py'),
                ('ownership', ENGINE / 'vendor/ownership.py')):
            module_binding(sys.modules[name], path, registration['source_sha256'])
        report['admission_calls'] = 1
        admitted = gate.admit(OUTPUT / 'admission')
        report['admission_sha256'] = sha(OUTPUT / 'admission/ADMISSION.json')
        if not admitted:
            report['status'] = 'WAIT_RESOURCE_OR_AUTHORITY_ZERO_VIEW_GROUPS'
        else:
            require(publication(deadline) == (registration, published),
                    'PUBLICATION_CHANGED_AFTER_FRESH_ADMISSION')
            require('fixture_terminal_view' not in sys.modules and
                    'test_fixture_terminal_view' not in sys.modules,
                    'PAYLOAD_MUST_NOT_BE_PREIMPORTED_OR_SHADOWED')
            sys.path.insert(0, str(HERE))
            import fixture_terminal_view
            import test_fixture_terminal_view
            for module in (fixture_terminal_view, test_fixture_terminal_view):
                module_binding(module, HERE / (module.__name__ + '.py'), registration['source_sha256'])
            result = four_groups(fixture_terminal_view, test_fixture_terminal_view)
            report['actual_groups_started'] = result['actual_groups_started']
            write('VIEW_TARGETED.json', dict(result,
                actual_imported_sources={module.__name__: dict(path=str(Path(module.__file__).resolve()),
                    sha256=sha(Path(module.__file__)))
                    for module in (fixture_terminal_view, test_fixture_terminal_view)}))
            require(result['status'] == 'PASS_FOUR_DECLARED_PURE_VIEW_GROUPS_ONLY',
                    'FOUR_TARGETED_PURE_GROUPS_REQUIRED')
            require(time.monotonic() < deadline and publication(deadline) == (registration, published),
                    'SOURCE_PUBLICATION_OR_TOTAL_BOUND_CHANGED_BEFORE_TERMINAL')
            report['status'] = 'PASS_SEM1_VIEW_FOUR_PURE_GROUPS_ONLY'
    except BaseException as error:
        report.update(status='STOP_SEM1_VIEW_CPU_QUALIFICATION', error=repr(error)[:4096])
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, prior_handler)
        if created:
            report['wall_seconds_nonperformance'] = time.monotonic() - began
            write('ENTRY_TERMINAL.json', report)
    print(json.dumps(dict(status=report['status'], output=str(OUTPUT),
        admission_calls=report['admission_calls'], actual_groups_started=report['actual_groups_started'],
        actual_fixture_cases=0, new_target_roots=0, simulation_starts=0)), flush=True)
    return 0 if report['status'] == 'PASS_SEM1_VIEW_FOUR_PURE_GROUPS_ONLY' else 3


if __name__ == '__main__':
    sys.exit(main())
