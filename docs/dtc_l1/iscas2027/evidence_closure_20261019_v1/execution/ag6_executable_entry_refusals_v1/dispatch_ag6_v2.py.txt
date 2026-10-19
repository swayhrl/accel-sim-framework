"""PREPARED_NOT_RELEASED. Sole-coordinator four-point sequential AG6 runner.

There is no fallback or rerun of a consumed start. A later explicit foreground
session may continue only the unstarted suffix after a verified accepted prefix. An
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
                                   env=ENV, text=True, timeout=30).strip()


def publication():
    receipt = json.loads((COHORT / 'preregistration/EXECUTABLE_PUBLICATION_READBACK.json').read_text())
    head = receipt['head']
    require(receipt['tree'] == receipt['fetched_tree'] == git('rev-parse', 'HEAD^{tree}'),
            'EXACT_EXECUTABLE_TREE_READBACK_REQUIRED')
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
        for source, digest in data.get('prepared_source_sha256', {}).items():
            require(manifest['source_sha256'].get(source) == digest,
                    'QUALIFIED_SOURCE_DIFFERS_FROM_PRODUCTION:' + source)
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


def accepted_prefix(points, manifest, published, release_sha):
    starts = budget(points)
    results = []
    relative = str(MANIFEST.relative_to(FRAMEWORK))
    for point, start in zip(points, starts):
        run = Path(point['destination'])
        require(run.parent == COHORT / 'attempts' and
                start == json.loads((run / 'RUN_START.json').read_text()), 'CONSUMED_ATTEMPT_PATH_CHANGED')
        require(start['point'] == point['point'] and start['order'] == point['order'] and
                start['source_core'] == point['core_commit'] and start['conservative_start_consumed'] is True and
                start['executable_manifest_sha256'] == release_sha, 'CONSUMED_START_IDENTITY_CHANGED')
        head = start['publication_head']
        require(len(head) == 40 and all(c in '0123456789abcdef' for c in head) and
                git('rev-parse', head + ':' + relative) == published['files'][relative]['blob'],
                'CONSUMED_START_NOT_SAME_IMMUTABLE_EXECUTABLE')
        result = json.loads((run / 'STRICT.json').read_text())
        terminal = json.loads((run / 'RUN_TERMINAL.json').read_text())
        engine = json.loads((run / 'ENGINE/TERMINAL.json').read_text())
        require(result['performance_accepted'] is True and result['scientific_strict_pass'] is True and
                result['point'] == point['point'] and result['attempt_uuid'] == point['attempt_uuid'] and
                result['publication_head'] == head, 'CONSUMED_ROW_NOT_ACCEPTED_NO_RERUN')
        require(terminal['returncode'] == engine['returncode'] == 0 and terminal['forced_reason'] is None and
                terminal['identity_pass'] is True and terminal['engine'] == engine and
                engine['status'] == 'PASS_GUARDED_NATURAL_EXIT0' and engine['owned_children_live'] == 0 and
                not engine['unconfirmed_wait_pids'] and not engine['ownership']['confirmed'] and
                not engine['ownership']['pending'], 'CONSUMED_ROW_NOT_CLOSED_NO_RERUN')
        for filename, key in [('INPUT_RUNTIME_IDENTITY.json', 'input_runtime_identity_sha256'),
                              ('MAPPING_CLOSURE.json', 'mapping_closure_sha256'),
                              ('RESOURCE_FINAL.json', 'final_resource_sha256'),
                              ('RESOURCE_MONITOR.jsonl', 'runtime_resource_monitor_sha256')]:
            require(sha(run / filename) == result[key], 'ACCEPTED_PREFIX_RECEIPT_CHANGED:' + filename)
        for filename, key in [('ENGINE/stdout','stdout'), ('ENGINE/stderr','stderr'),
                              ('RUN_START.json','RUN_START'), ('RUN_TERMINAL.json','RUN_TERMINAL'),
                              ('ENGINE/TERMINAL.json','ENGINE_TERMINAL')]:
            require(sha(run / filename) == result['receipt_sha256'][key],
                    'ACCEPTED_PREFIX_ACTUAL_SCIENCE_BYTES_CHANGED:' + filename)
        results.append(result)
    return results


class PrestartWait(ValueError):
    """No conservative start consumed for this pending point; never auto-retry."""


def main():
    require(sys.argv == [str(HERE / 'dispatch_ag6_v2.py'), '--dispatch'] and
            dict(os.environ) == ENV, 'EXACT_EXPLICIT_AG6_FOREGROUND_ENTRY_REQUIRED')
    manifest, published, points = publication()
    require(not (COHORT / 'COHORT_TERMINAL.json').exists(), 'TERMINAL_COHORT_NO_RESTART')
    release_sha = sha(MANIFEST)
    (COHORT / 'attempts').mkdir(exist_ok=True)
    require(os.stat(COHORT / 'attempts').st_dev == os.stat(COHORT).st_dev,
            'ACTUAL_ATTEMPT_PARENT_FILESYSTEM_NOT_REGISTERED')
    session = COHORT / 'dispatch_sessions' / (str(time.time_ns()) + '-' + str(os.getpid()))
    session.mkdir(parents=True, exist_ok=False)
    write(session / 'SESSION_START.json', dict(utc=now(), publication_head=published['head'],
        executable_manifest_sha256=release_sha, fixed_points=[dict(point=p['point'], attempt_uuid=p['attempt_uuid']) for p in points],
        automatic_retry=False))
    def recheck_publication():
        current_manifest, _, current_points = publication()
        require(sha(MANIFEST) == release_sha and current_manifest == manifest and current_points == points,
                'SESSION_EXECUTABLE_OR_FIXED_SCIENCE_CHANGED')
    sys.path.insert(0, str(ENGINE_SOURCE / 'vendor'))
    sys.path.insert(0, str(ENGINE_SOURCE))
    sys.path.insert(0, str(HERE))
    from guarded_process import run_guarded
    from mapping_roles import validate_manifest
    from ownership import identity
    from shared_authority import bind_current_review
    from cpu_admission_v2 import NoOwnedChildren
    from legacy_authority_runtime import bind_frozen_procedures
    from resources_v2 import enrich, checks, paired, Runtime
    from ag6_input_runtime_identity import validate_identity
    from close_attempt_v2 import collect
    from selection_v2 import select_v2
    def selection_boundaries_once():
        path = COHORT / 'SELECTION_BOUNDARY_QUALIFICATION.json'
        source_hashes = {name: sha(HERE / name) for name in
                         ('selection_v2.py', 'selection_boundary_cases.py')}
        if path.exists():
            proof = json.loads(path.read_text())
            require(proof['status'] == 'PASS_FOUR_PURE_SELECTION_BOUNDARIES_ONLY' and
                    proof['source_sha256'] == source_hashes, 'SELECTION_BOUNDARY_SOURCE_CHANGED')
            return
        import selection_v2
        from selection_boundary_cases import run_boundary_cases
        proof = run_boundary_cases(selection_v2,
            preregistration=(EXECUTION / 'AG6_FOUR_POINT_IDENTITY_PREREGISTRATION_V2.json').read_bytes(),
            base_decision=(EXECUTION / 'BASE_REUSE_DECISION_V2.json').read_bytes(),
            old_selection=(EXECUTION / 'SELECTION.json').read_bytes())
        proof.update(source_sha256=source_hashes, publication_head=published['head'],
                     gate_scope='AFTER_CURRENT_FULL_PAIRED_R2_BEFORE_ANY_RESERVED_START')
        write(path, proof)
        require(proof['status'] == 'PASS_FOUR_PURE_SELECTION_BOUNDARIES_ONLY',
                'SELECTION_ARITHMETIC_BOUNDARY_FAILURE_ZERO_MODEL')
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
    def footprint(point, current):
        expected = manifest['expected_attempt_output_bytes'][point]
        require(type(expected) is int and expected > 0, 'REGISTERED_ATTEMPT_WRITE_ESTIMATE_REQUIRED')
        return dict(expected_attempt_output_bytes=expected, disk_floor_exclusive_bytes=5 * 1024**3,
                    actual_output_free_bytes=current['disk_free_bytes'],
                    available_above_floor_bytes=current['disk_free_bytes'] - 5 * 1024**3)
    def admit(point):
        dest = session / 'admissions' / point
        dest.mkdir(parents=True, exist_ok=False)
        first, auth1 = sample(empty)
        estimate1 = footprint(point, first)
        write(dest / 'FIRST.json', dict(snapshot=first, authority=auth1, write_footprint=estimate1))
        preliminary = checks(first)
        preliminary['attempt_write_margin'] = estimate1['available_above_floor_bytes'] >= estimate1['expected_attempt_output_bytes']
        preliminary['authority'] = auth1['status'] == 'PASS_CURRENT_NO_OTHER_DTC_DISPATCH_AUTHORITY'
        require(preliminary['authority'] and preliminary['original174'], 'ADMISSION_AUTHORITY_OR_SITE_NOT_CLOSED')
        if not all(preliminary.values()):
            write(dest / 'DECISION.json', dict(status='WAIT_NO_NEW_START_FIRST', checks=preliminary,
                  write_footprint=estimate1, automatic_retry=False))
            return None
        time.sleep(10.1)
        if interrupted:
            raise PrestartWait('COORDINATOR_SIGNAL_NO_NEW_DISPATCH')
        second, auth2 = sample(empty)
        estimate2 = footprint(point, second)
        write(dest / 'SECOND.json', dict(snapshot=second, authority=auth2, write_footprint=estimate2))
        values = paired(first, second)
        values['first_attempt_write_margin'] = preliminary['attempt_write_margin']
        values['second_attempt_write_margin'] = estimate2['available_above_floor_bytes'] >= estimate2['expected_attempt_output_bytes']
        values['first_authority'] = preliminary['authority']
        values['second_authority'] = auth2['status'] == 'PASS_CURRENT_NO_OTHER_DTC_DISPATCH_AUTHORITY'
        require(values['second_authority'] and values['second_original174'] and values['same_output_filesystem'],
                'ADMISSION_AUTHORITY_SITE_OR_FILESYSTEM_CHANGED')
        good = all(values.values())
        write(dest / 'DECISION.json', dict(status='PASS_FULLSIM_ADMISSION_ONLY' if good
              else 'WAIT_NO_NEW_START_PAIR', checks=values, write_footprints=[estimate1,estimate2], automatic_retry=False))
        return second if good else None
    results = []
    failure = None
    waiting = None
    lock_acquired = False
    interrupted = []
    old_handlers = {s: signal.signal(s, lambda n, f: interrupted.append(n))
                    for s in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP)}
    try:
        # This one exact path is already recognized by the unchanged reviewer.
        # No foreign lock acquisition or deletion is performed.
        with (RAW / 'AG_execution.lock').open('a') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            lock_acquired = True
            try:
                write(session / 'AUTHORITY_ACTIVE.json', dict(owner=owner,
                      publication_head=published['head'], maximum_active_simulators=1))
                require(not (COHORT / 'COHORT_TERMINAL.json').exists(), 'TERMINAL_COHORT_NO_RESTART')
                results = accepted_prefix(points, manifest, published, release_sha)
                write(session / 'ACCEPTED_PREFIX.json', dict(results=results,
                    strict_sha256={p['point']:sha(Path(p['destination']) / 'STRICT.json') for p in points[:len(results)]}))
                for point in points[len(results):]:
                    if interrupted:
                        raise PrestartWait('COORDINATOR_SIGNAL_NO_NEW_DISPATCH')
                    recheck_publication()
                    identity_receipt = validate_identity(manifest['identity_contract'], point['point'])
                    run = Path(point['destination'])
                    require(run.parent == COHORT / 'attempts', 'EXACT_AG6_ATTEMPT_PATH')
                    require(not run.exists(), 'PRESERVE_UNCONSUMED_OR_CONSUMED_ATTEMPT_DIRECTORY')
                    stage = session / 'preflight' / point['point']
                    stage.mkdir(parents=True, exist_ok=False)
                    argv = identity_receipt['validated_argv']
                    copies = identity_receipt['config_copies']
                    mapping_path = Path(manifest['mapping_manifest_path'])
                    require(sha(mapping_path) == manifest['mapping_manifest_sha256'],
                            'AG6_MAPPING_MANIFEST_CHANGED')
                    mappings = json.loads(mapping_path.read_text())
                    for mapping in mappings.values():
                        validate_manifest(mapping)
                    require(identity_receipt['validated_environment'] == point['runtime_environment'],
                            'EXACT_IDENTITY_VALIDATED_ENVIRONMENT_REQUIRED')
                    write(stage / 'INPUT_RUNTIME_IDENTITY.json', identity_receipt)
                    admitted = admit(point['point'])
                    if interrupted:
                        raise PrestartWait('COORDINATOR_SIGNAL_NO_NEW_DISPATCH')
                    if admitted is None:
                        raise PrestartWait('WAIT_RESOURCE_NO_NEW_START')
                    selection_boundaries_once()
                    recheck_publication()
                    baseline, authority = sample(empty)
                    final_estimate = footprint(point['point'], baseline)
                    final_checks = checks(baseline)
                    final_checks['attempt_write_margin'] = final_estimate['available_above_floor_bytes'] >= final_estimate['expected_attempt_output_bytes']
                    final_checks['authority'] = authority['status'] == 'PASS_CURRENT_NO_OTHER_DTC_DISPATCH_AUTHORITY'
                    final_checks['no_new_host_OOM'] = baseline['host_oom_kill'] == admitted['host_oom_kill']
                    final_checks['no_new_cgroup_OOM'] = all(baseline['cgroup']['events'][k] ==
                        admitted['cgroup']['events'][k] for k in ('oom', 'oom_kill'))
                    write(stage / 'FINAL_PRE_FORK.json', dict(snapshot=baseline,
                          authority=authority, checks=final_checks, write_footprint=final_estimate))
                    require(final_checks['authority'] and final_checks['original174'], 'FINAL_AUTHORITY_OR_SITE_NOT_CLOSED')
                    require(baseline['output_filesystem_device'] == admitted['output_filesystem_device'],
                            'FINAL_OUTPUT_FILESYSTEM_CHANGED')
                    if not all(final_checks.values()):
                        raise PrestartWait('FINAL_PRE_FORK_R2_NO_NEW_START')
                    if interrupted:
                        raise PrestartWait('COORDINATOR_SIGNAL_NO_NEW_DISPATCH')
                    if not 0 <= time.monotonic_ns() - baseline['monotonic_ns'] <= 5 * 10**9:
                        raise PrestartWait('FINAL_PREPARATION_SAMPLE_STALE_NO_NEW_START')
                    runtime = Runtime(baseline, COHORT)
                    next_sample = [0.0]
                    last_fault = [0]
                    event_offset = [0]
                    map_bytes = [0]
                    def check_exec_roots(root_pid):
                        # Forked popen helpers inherit the simulator image before
                        # exec. Only an actual nonroot exec of the simulator is
                        # a second model. Guard-written EXEC_EVENT rows follow
                        # kernel exec events and precede resumption.
                        with (run / 'ENGINE/MAP_EVENTS.jsonl').open('rb') as stream:
                            stream.seek(event_offset[0])
                            for line in stream:
                                row = json.loads(line)
                                if 'maps' in row:
                                    map_bytes[0] += (run / 'ENGINE/maps' / row['maps']).stat().st_size
                                if (row.get('stage') == 'EXEC_EVENT' and
                                        row.get('exe') == point['runtime_path'] and
                                        row['pid'] != root_pid):
                                    return 'UNREGISTERED_SECOND_OWN_SIMULATOR_EXEC'
                            event_offset[0] = stream.tell()
                        sizes = {name: (run / name).stat().st_size for name in
                                 ('ENGINE/stdout', 'ENGINE/stderr', 'ENGINE/MAP_EVENTS.jsonl')}
                        for name in ('ENGINE/OOM_MONITOR.jsonl', 'RESOURCE_MONITOR.jsonl'):
                            path = run / name
                            sizes[name] = path.stat().st_size if path.exists() else 0
                        if (sizes['ENGINE/stdout'] > manifest['stdout_bound_bytes'] or
                                sizes['ENGINE/stderr'] > manifest['stderr_bound_bytes']):
                            return 'OWN_ATTEMPT_STREAM_OUTPUT_BOUND'
                        if map_bytes[0] + sum(sizes.values()) > manifest['maximum_attempt_output_bytes']:
                            return 'OWN_ATTEMPT_EVIDENCE_OUTPUT_BOUND'
                        return None
                    def observer(pid, full_hint, ownership):
                        if interrupted:
                            return 'COORDINATOR_SIGNAL:' + str(interrupted[0])
                        extra_root = check_exec_roots(pid)
                        if extra_root:
                            return extra_root
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
                    # All planned static/input/publication/resource/interrupt
                    # checks are complete before creating a canonical attempt.
                    if interrupted:
                        raise PrestartWait('COORDINATOR_SIGNAL_NO_NEW_DISPATCH')
                    if not 0 <= time.monotonic_ns() - baseline['monotonic_ns'] <= 5 * 10**9:
                        raise PrestartWait('FINAL_PREPARATION_SAMPLE_STALE_NO_NEW_START')
                    run.mkdir(parents=True, exist_ok=False)
                    require(run.stat().st_dev == baseline['output_filesystem_device'],
                            'ACTUAL_NEW_ATTEMPT_FILESYSTEM_CHANGED')
                    write(run / 'INPUT_RUNTIME_IDENTITY.json', identity_receipt)
                    write(run / 'FINAL_PRE_FORK.json', dict(snapshot=baseline, authority=authority,
                          checks=final_checks, write_footprint=final_estimate))
                    try:
                        # Conservative exclusive consumption immediately before
                        # the single guarded fork; even a failed fork consumes
                        # this reservation and can never be replaced.
                        write(run / 'RUN_START.json', dict(utc=now(), order=point['order'],
                            point=point['point'], attempt_uuid=point['attempt_uuid'], argv=argv,
                            input_identity=identity_receipt, config_copies=copies,
                            source_core=point['core_commit'], timeout_seconds=7200, retries=0,
                            publication_head=published['head'], executable_manifest_sha256=release_sha,
                            dispatch_session=str(session), conservative_start_consumed=True))
                        def capability(target, actual_argv, environment):
                            require(not interrupted, 'COORDINATOR_SIGNAL_NO_FORK')
                            require(manifest['released_publication_reference'] == 'refs/dtc-closure-readback/ag6-v2-executable',
                                    'EXACT_ALREADY_VERIFIED_RELEASE_REQUIRED')
                            require(budget(points)[-1]['attempt_uuid'] == point['attempt_uuid'],
                                    'EXACT_CURRENT_CONSERVATIVE_START_REQUIRED')
                            require(target == point['runtime_path'] and actual_argv == argv and
                                    environment == point['runtime_environment'], 'EXACT_AG6_TARGET_REQUIRED')
                            require(not (run / 'ENGINE/FORK_CHILD.json').exists(), 'NO_SECOND_CHILD')
                            require(time.monotonic_ns() - baseline['monotonic_ns'] <= 5 * 10**9,
                                    'FINAL_R2_SAMPLE_STALE_NO_FORK')
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
                        result = collect(run, point, manifest=manifest,
                            publication_head=published['head'], identity_receipt=identity_receipt)
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
                if len(results) == 4:
                    receipt_paths = [Path(point['destination']) / 'STRICT.json' for point in points]
                    selected = select_v2([path.read_bytes() for path in receipt_paths],
                        base_cycles={'GEMM':1071405, 'Gaussian':3278356},
                        preregistration=(EXECUTION / 'AG6_FOUR_POINT_IDENTITY_PREREGISTRATION_V2.json').read_bytes(),
                        base_decision=(EXECUTION / 'BASE_REUSE_DECISION_V2.json').read_bytes(),
                        old_selection=(EXECUTION / 'SELECTION.json').read_bytes())
                    require(selected['status'] == 'FINAL_F_FROM_COMPLETE_FOUR_POINT_AG6_SCREEN',
                            'SELECTION_FIXED_INPUT_RECEIPT_JOIN_FAILED')
                    selected.update(executable_manifest_sha256=release_sha,
                        publication_head=published['head'],
                        actual_STRICT_receipts=[dict(path=str(path), sha256=sha(path)) for path in receipt_paths],
                        scope='TWO_INPUT_DISCOVERY_SCREEN_ONLY_NOT_PRIMARY_P8_OR_INDEPENDENT_VALIDATION')
                    write(COHORT / 'SELECTION_V2.json', selected)
            except PrestartWait as error:
                waiting = repr(error)
            except BaseException as error:
                failure = repr(error)
            finally:
                consumed = len(list((COHORT / 'attempts').glob('*/RUN_START.json')))
                complete = (not failure and not waiting and consumed == len(results) == 4 and
                            all(r['performance_accepted'] is True for r in results))
                if not failure and not waiting and not complete:
                    failure = 'INCOMPLETE_OR_INCONSISTENT_FIXED_FOUR_POINT_RESULTS'
                terminal = dict(utc=now(),
                    status='STOP' if failure else 'PAUSED_PRESTART_NO_NEW_START' if waiting else 'COMPLETE_FOUR_POINT_AG6_DISCOVERY',
                    reason=failure or waiting, consumed_starts=consumed,
                    actual_fork_children=len(list((COHORT / 'attempts').glob('*/ENGINE/FORK_CHILD.json'))),
                    results=results, executable_manifest_sha256=release_sha,
                    fixed_UUIDs=[p['attempt_uuid'] for p in points],
                    next_point=points[len(results)]['point'] if waiting and len(results)<4 else None,
                    automatic_retry=False, replacement_or_BA_transfer=False)
                write(session / 'SESSION_TERMINAL.json', terminal)
                if failure or complete:
                    if not (COHORT / 'COHORT_TERMINAL.json').exists():
                        write(COHORT / 'COHORT_TERMINAL.json', terminal)
    finally:
        try:
            write(session / 'AUTHORITY_RELEASE.json', dict(utc=now(), owner=owner,
                own_lock_acquired=lock_acquired,
                own_lock_closed=bool(lock_acquired and lock.closed),
                foreign_signals=0, automatic_dispatch=False,
                execution_authority_from_release=False))
        finally:
            for number, handler in old_handlers.items():
                signal.signal(number, handler)
    return 3 if failure or waiting else 0


if __name__ == '__main__':
    sys.exit(main())
