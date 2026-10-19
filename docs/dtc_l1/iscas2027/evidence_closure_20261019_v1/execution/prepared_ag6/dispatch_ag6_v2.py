"""PREPARED_NOT_RELEASED. Sole-coordinator four-point sequential AG6 runner.

There is deliberately no fallback or resume after a consumed start. An
executable registration, current qualification receipts, exact remote readback,
fresh complete R2 and exclusive coordinator lock are all required before fork.
CPU qualifications never supply this capability. No additional simulator is
used to test this runner. Importing this module performs no work.
"""
import fcntl
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone

HERE = Path(__file__).resolve().parent
EXECUTION = HERE.parent
FRAMEWORK = HERE.parents[5]
ENGINE_SOURCE = EXECUTION / 'prepared_runtime'
RAW = Path('/workspace/dtc-evidence-closure-20261019-v1/coordinator')
COHORT = RAW / 'ag6-v2'
ORDER = ['AE_GEMM', 'AE_Gaussian', 'AD_GEMM', 'AD_Gaussian']
ENV = {'PATH': '/usr/bin:/bin', 'LANG': 'C', 'LC_ALL': 'C'}
MANIFEST = EXECUTION / 'AG6_EXECUTABLE_PREREGISTRATION_V2.json'


def require(value, reason):
    if not value:
        raise ValueError(reason)


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for data in iter(lambda: stream.read(65536), b''):
            digest.update(data)
    return digest.hexdigest()


def write(path, value):
    with Path(path).open('x') as stream:
        stream.write(json.dumps(value, indent=2) + '\n')


def now():
    return datetime.now(timezone.utc).isoformat()


def git(*args):
    return subprocess.check_output(['/usr/bin/git', '-C', str(FRAMEWORK), *args],
                                   env=ENV, text=True).strip()


def publication():
    receipt = json.loads((COHORT / 'preregistration/EXECUTABLE_PUBLICATION_READBACK.json').read_text())
    head = receipt['head']
    require(receipt['fetched_head'] == head ==
            git('rev-parse', 'refs/dtc-closure-readback/ag6-v2-executable'),
            'EXACT_AG6_EXECUTABLE_REMOTE_READBACK_REQUIRED')
    require(not git('status', '--porcelain') and git('rev-parse', 'HEAD') == head,
            'EXACT_CLEAN_EXECUTABLE_SOURCE_REQUIRED')
    for relative, binding in receipt['files'].items():
        path = FRAMEWORK / relative
        require(sha(path) == binding['sha256'] and
                git('rev-parse', head + ':' + relative) == binding['blob'],
                'EXECUTABLE_PUBLISHED_SOURCE_CHANGED:' + relative)
    relative = str(MANIFEST.relative_to(FRAMEWORK))
    require(relative in receipt['files'], 'EXECUTABLE_MANIFEST_NOT_PUBLISHED')
    manifest = json.loads(MANIFEST.read_text())
    require(manifest['status'] == 'EXECUTABLE_AG6_ONLY_FOUR_NEW_STARTS' and
            manifest['maximum_simultaneous_simulators'] == 1 and
            manifest['maximum_new_starts'] == 4 and manifest['replacement_starts'] == 0,
            'EXACT_SINGLE_WORKER_FOUR_START_RELEASE_REQUIRED')
    for path, digest in manifest['source_sha256'].items():
        require(sha(path) == digest, 'EXACT_EXECUTABLE_CLOSURE_CHANGED:' + path)
    for row in manifest['qualification_receipts']:
        require(sha(row['path']) == row['sha256'], 'QUALIFICATION_RECEIPT_CHANGED')
        data = json.loads(Path(row['path']).read_text())
        require(data['status'] == row['required_status'], 'MISSING_ACTUAL_QUALIFICATION')
        # Each receipt is admitted separately and bound to the exact qualified
        # source/registration; a status string is never enough.
        for key, value in row['required_bindings'].items():
            require(data.get(key) == value, 'QUALIFICATION_SOURCE_BINDING_CHANGED:' + key)
    decision = EXECUTION / 'BASE_REUSE_DECISION_V2.json'
    require(sha(decision) == manifest['BASE_decision_sha256'], 'BASE_DECISION_CHANGED')
    require(json.loads(decision.read_text())['status'] ==
            'PASS_BOTH_SCOPED_IMPORTED_BASES_FOR_AG6_ONLY_NO_DISPATCH_PERMISSION',
            'BOTH_INDEPENDENT_BASES_REQUIRED')
    identity = EXECUTION / 'AG6_FOUR_POINT_IDENTITY_PREREGISTRATION_V2.json'
    require(sha(identity) == manifest['identity_preregistration_sha256'],
            'REGISTERED_FOUR_UUID_OR_SCIENCE_CHANGED')
    points = json.loads(identity.read_text())['ordered_points']
    require([p['point'] for p in points] == ORDER and
            len({p['attempt_uuid'] for p in points}) == 4, 'FIXED_FOUR_POINT_ORDER')
    require(sha(EXECUTION / 'SELECTION.json') == manifest['old_selection_sha256'],
            'ORIGINAL_SELECTION_MUST_REMAIN_UNCHANGED')
    return manifest, receipt, points


def budget(points):
    rows = [json.loads(p.read_text()) for p in (COHORT / 'attempts').glob('*/RUN_START.json')]
    rows.sort(key=lambda x: x['order'])
    require(len(rows) <= 4 and len({r['attempt_uuid'] for r in rows}) == len(rows),
            'AG6_CAP_OR_DUPLICATE_UUID')
    require([r['attempt_uuid'] for r in rows] ==
            [p['attempt_uuid'] for p in points[:len(rows)]], 'AG6_START_PREFIX_CHANGED')
    return rows


def main():
    require(sys.argv == [str(HERE / 'dispatch_ag6_v2.py'), '--dispatch'] and
            dict(os.environ) == ENV, 'EXACT_EXPLICIT_AG6_FOREGROUND_ENTRY_REQUIRED')
    manifest, published, points = publication()
    require(not budget(points), 'PRIOR_AG6_START_NO_RESTART_OR_REPLACEMENT')
    require(not (COHORT / 'COHORT_TERMINAL.json').exists(), 'TERMINAL_COHORT_NO_RESTART')
    sys.path.insert(0, str(ENGINE_SOURCE / 'vendor'))
    sys.path.insert(0, str(ENGINE_SOURCE))
    sys.path.insert(0, str(HERE))
    from guarded_process import run_guarded
    from ownership import identity
    from shared_authority import bind_current_review
    from cpu_admission_v2 import NoOwnedChildren
    from legacy_authority_runtime import bind_frozen_procedures
    from resources_v2 import enrich, checks, paired, Runtime
    from ag6_input_runtime_identity import verify_identity
    from ag6_strict_v2 import collect
    owner = identity(os.getpid())
    proc_reader, _, _ = bind_frozen_procedures()
    manager_role = manifest['coordinator_role']
    review_cache = {}
    def review(local):
        key = id(local)
        if key not in review_cache:
            review_cache[key] = bind_current_review(local, identity, lambda: [],
                exact_controller_roles_provider=lambda: [manager_role])
        snapshot, verdict = review_cache[key](owner)
        return enrich(snapshot, COHORT), verdict
    empty = NoOwnedChildren()
    def sample(local):
        current, verdict = review(local)
        return current, verdict
    def admit(point):
        dest = COHORT / 'admissions' / point
        dest.mkdir(parents=True, exist_ok=False)
        first, auth1 = sample(empty)
        write(dest / 'FIRST.json', dict(snapshot=first, authority=auth1))
        preliminary = checks(first)
        preliminary['authority'] = auth1['status'] == 'PASS_CURRENT_NO_OTHER_DTC_DISPATCH_AUTHORITY'
        if not all(preliminary.values()):
            write(dest / 'DECISION.json', dict(status='WAIT_NO_NEW_START_FIRST', checks=preliminary))
            return None
        time.sleep(10.1)
        second, auth2 = sample(empty)
        write(dest / 'SECOND.json', dict(snapshot=second, authority=auth2))
        values = paired(first, second)
        values['first_authority'] = preliminary['authority']
        values['second_authority'] = auth2['status'] == 'PASS_CURRENT_NO_OTHER_DTC_DISPATCH_AUTHORITY'
        good = all(values.values())
        write(dest / 'DECISION.json', dict(status='PASS_FULLSIM_ADMISSION_ONLY' if good
              else 'WAIT_NO_NEW_START_PAIR', checks=values, automatic_retry=False))
        return second if good else None
    results = []
    failure = None
    interrupted = []
    old_handlers = {s: signal.signal(s, lambda n, f: interrupted.append(n))
                    for s in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP)}
    try:
        # This one exact path is already recognized by the unchanged reviewer.
        # No foreign lock acquisition or deletion is performed.
        with (RAW / 'AG_execution.lock').open('a') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            write(COHORT / 'AUTHORITY_ACTIVE.json', dict(owner=owner,
                  publication_head=published['head'], maximum_active_simulators=1))
            try:
                for point in points:
                    require(not interrupted, 'COORDINATOR_SIGNAL_NO_NEW_DISPATCH')
                    publication()
                    identity_receipt = verify_identity(manifest['identity_contract'], point)
                    admitted = admit(point['point'])
                    require(admitted is not None, 'WAIT_RESOURCE_OR_AUTHORITY_NO_NEW_START')
                    publication()
                    run = Path(point['destination'])
                    require(run.parent == COHORT / 'attempts', 'EXACT_AG6_ATTEMPT_PATH')
                    run.mkdir(parents=True, exist_ok=False)
                    argv = [point['runtime_path'], '-trace', point['trace_list']]
                    copies = []
                    for index, entry in enumerate(point['configs']):
                        require(sha(entry['path']) == entry['sha256'], 'CONFIG_CHANGED')
                        path = run / ('config-' + str(index) + '.config')
                        shutil.copyfile(entry['path'], path)
                        path.chmod(0o444)
                        copies.append(dict(path=str(path), sha256=sha(path)))
                        argv.extend(['-config', str(path)])
                    baseline, authority = sample(empty)
                    final_checks = checks(baseline)
                    final_checks['authority'] = authority['status'] == 'PASS_CURRENT_NO_OTHER_DTC_DISPATCH_AUTHORITY'
                    final_checks['no_new_host_OOM'] = baseline['host_oom_kill'] == admitted['host_oom_kill']
                    final_checks['no_new_cgroup_OOM'] = all(baseline['cgroup']['events'][k] ==
                        admitted['cgroup']['events'][k] for k in ('oom', 'oom_kill'))
                    require(all(final_checks.values()), 'FINAL_PRE_FORK_R2_OR_AUTHORITY_STOP')
                    write(run / 'FINAL_PRE_FORK.json', dict(snapshot=baseline,
                          authority=authority, checks=final_checks))
                    runtime = Runtime(baseline, COHORT)
                    next_sample = [0.0]
                    last_fault = [0]
                    def observer(pid, full_hint, ownership):
                        if interrupted:
                            return 'COORDINATOR_SIGNAL:' + str(interrupted[0])
                        quick = runtime.quick_stop()
                        if quick:
                            return quick
                        if time.monotonic() < next_sample[0]:
                            return None
                        current, auth = sample(ownership)
                        owned = proc_reader(pid) if pid in ownership.confirmed else None
                        fault = owned['majflt'] if owned else last_fault[0]
                        decision = runtime.observe(current, fault, last_fault[0])
                        last_fault[0] = fault
                        next_sample[0] = time.monotonic() + decision['next_full_sample_seconds']
                        with (run / 'RESOURCE_MONITOR.jsonl').open('a') as stream:
                            stream.write(json.dumps(dict(snapshot=current, authority=auth,
                                decision=decision, own=owned)) + '\n')
                        if decision['decision'] == 'STOP':
                            return ';'.join(decision['stop_reasons'])
                        if auth['status'] == 'STOP_AUTHORITY_NOT_CLOSED':
                            return 'RUNTIME_GLOBAL_AUTHORITY_NOT_CLOSED'
                        require(auth['status'] in ('PASS_CURRENT_NO_OTHER_DTC_DISPATCH_AUTHORITY',
                            'PENDING_QUARANTINED_NO_AUTHORITY_PASS'), 'UNKNOWN_AUTHORITY_STATUS')
                        return None
                    engine = None
                    try:
                        # Conservative exclusive consumption immediately before
                        # the single guarded fork; even a failed fork consumes
                        # this reservation and can never be replaced.
                        write(run / 'RUN_START.json', dict(utc=now(), order=point['order'],
                            point=point['point'], attempt_uuid=point['attempt_uuid'], argv=argv,
                            input_identity=identity_receipt, config_copies=copies,
                            source_core=point['core_commit'], timeout_seconds=7200, retries=0,
                            publication_head=published['head'], conservative_start_consumed=True))
                        def capability(target, actual_argv, environment):
                            publication()
                            require(budget(points)[-1]['attempt_uuid'] == point['attempt_uuid'],
                                    'EXACT_CURRENT_CONSERVATIVE_START_REQUIRED')
                            require(target == point['runtime_path'] and actual_argv == argv and
                                    environment == point['runtime_environment'], 'EXACT_AG6_TARGET_REQUIRED')
                            require(not (run / 'ENGINE/FORK_CHILD.json').exists(), 'NO_SECOND_CHILD')
                            require(time.monotonic_ns() - baseline['monotonic_ns'] <= 5 * 10**9,
                                    'FINAL_R2_SAMPLE_STALE_NO_FORK')
                        mapping_path = Path(manifest['mapping_manifest_path'])
                        require(sha(mapping_path) == manifest['mapping_manifest_sha256'],
                                'AG6_MAPPING_MANIFEST_CHANGED')
                        mappings = json.loads(mapping_path.read_text())
                        engine = run_guarded(argv, point['runtime_environment'], mappings,
                            run / 'ENGINE', 'SIMULATION', 7200, capability, observer)
                        final, auth = sample(empty)
                        decision = runtime.observe(final, last_fault[0], last_fault[0])
                        write(run / 'RESOURCE_FINAL.json', dict(snapshot=final,
                            authority=auth, decision=decision))
                        require(auth['status'] == 'PASS_CURRENT_NO_OTHER_DTC_DISPATCH_AUTHORITY',
                                'FINAL_AUTHORITY_NOT_CLOSED')
                        write(run / 'RUN_TERMINAL.json', dict(returncode=engine['returncode'],
                            forced_reason=engine['forced_reason'] or ('FINAL_RESOURCE_STOP'
                                if decision['decision'] == 'STOP' else None),
                            identity_pass=engine['identity_pass'], engine=engine))
                        result = collect(run, point)
                        write(run / 'STRICT.json', result)
                        results.append(result)
                        print(json.dumps(dict(point=point['point'], status=result['status'],
                            cycles=result.get('cycles'))), flush=True)
                        require(result['performance_accepted'], 'PER_ARM_STRICT_FAIL_STOP')
                    except BaseException as error:
                        write(run / 'WRAPPER_EXCEPTION.json', dict(utc=now(), reason=repr(error),
                            engine=engine, no_retry=True))
                        if not (run / 'RUN_TERMINAL.json').exists():
                            write(run / 'RUN_TERMINAL.json', dict(returncode=None,
                                forced_reason=repr(error), identity_pass=False, engine=engine))
                        if not (run / 'STRICT.json').exists():
                            write(run / 'STRICT.json', dict(status='HOLD_STRICT_FAILED',
                                performance_accepted=False, cycles='UNAVAILABLE', reason=repr(error)))
                        raise
            except BaseException as error:
                failure = repr(error)
            finally:
                write(COHORT / 'COHORT_TERMINAL.json', dict(utc=now(),
                    status='STOP' if failure else 'COMPLETE_FOUR_POINT_AG6_DISCOVERY',
                    reason=failure, consumed_starts=len(budget(points)),
                    actual_fork_children=len(list((COHORT / 'attempts').glob('*/ENGINE/FORK_CHILD.json'))),
                    results=results, automatic_retry=False, replacement_or_BA_transfer=False))
        write(COHORT / 'AUTHORITY_RELEASE.json', dict(utc=now(), owner=owner,
            own_lock_closed=True, foreign_signals=0, automatic_dispatch=False))
    finally:
        for number, handler in old_handlers.items():
            signal.signal(number, handler)
    return 3 if failure else 0


if __name__ == '__main__':
    sys.exit(main())
