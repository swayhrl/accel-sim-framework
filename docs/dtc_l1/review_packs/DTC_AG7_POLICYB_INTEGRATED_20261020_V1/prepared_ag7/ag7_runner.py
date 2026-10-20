"""Source-only BA callback/strict closure helpers; no CLI or admission bypass.

All authority objects and legacy modules are source-frozen by the sole root
controller. A static identity pass occurs before admission, not inside its last
five-second fork window. No helper creates UUIDs, a budget, or a replacement run.
"""
import hashlib
import json
import os
from pathlib import Path
import time

GIB = 1024 ** 3
PASS = 'PASS_CURRENT_NO_OTHER_DTC_DISPATCH_AUTHORITY'
PENDING = 'PENDING_QUARANTINED_NO_AUTHORITY_PASS'
MAX_CGROUP_MEMBERS = 4096


def require(value, message):
    if not value:
        raise ValueError(message)


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(65536), b''):
            digest.update(block)
    return digest.hexdigest()


def write(path, value):
    with Path(path).open('x') as stream:
        stream.write(json.dumps(value, sort_keys=True, indent=2) + '\n')


def parsed_iostat(raw):
    rows = {}
    for line in raw.splitlines():
        device, *fields = line.split()
        require(device not in rows, 'DUPLICATE_CGROUP_IO_DEVICE')
        rows[device] = {key: int(value) for key, value in (field.split('=') for field in fields)}
    return rows


class RuntimeSampler:
    """Original all-project authority snapshot plus bounded actual I/O scope.

    Two membership reads are a bounded sampling interval, not an atomic kernel
    snapshot. Exited instances remain in evidence; a live member with unreadable
    identity/io or an added second-pass member we cannot bind fails scope closed.
    Counters describe instances/devices; they do not prove storage harm absent.
    """
    def __init__(self, authority, identity_reader, resource_module, output_root, pilot_acceptance):
        self.authority = authority
        self.identity = identity_reader
        self.resources = resource_module
        self.output = Path(output_root)
        self.owner = identity_reader(os.getpid())
        self.pilot = pilot_acceptance
        self.reviews = {}
        self.previous_process_io = {}
        self.previous_device_io = {}
        self.first_oom = None

    def scope(self, snapshot):
        began = time.monotonic_ns()
        cg = Path('/sys/fs/cgroup')
        membership = Path('/proc/self/cgroup').read_text().strip()
        first = {int(value) for value in (cg / 'cgroup.procs').read_text().split()}
        require(len(first) <= MAX_CGROUP_MEMBERS, 'CGROUP_INVENTORY_BOUND_EXCEEDED')
        rows, unresolved, ended = {}, [], []

        def read_member(pid):
            try:
                before = self.identity(pid)
                q = Path('/proc') / str(pid)
                current_membership = (q / 'cgroup').read_text().strip()
                io = {key: int(value) for key, value in
                      (line.split(':') for line in (q / 'io').read_text().splitlines())}
                after = self.identity(pid)
                require(before['start_ticks'] == after['start_ticks'], 'IO_INSTANCE_CHANGED_DURING_READ')
                require(current_membership == '0::/', 'CGROUP_MEMBER_OUTSIDE_REGISTERED_SCOPE')
                require(all(type(value) is int and value >= 0 for value in io.values()), 'INVALID_PROCESS_IO')
                key = (pid, before['start_ticks'])
                prior = self.previous_process_io.get(key)
                delta = None if prior is None else {k: io[k] - prior[k] for k in io if k in prior}
                require(delta is None or all(v >= 0 for v in delta.values()), 'PROCESS_IO_COUNTER_REVERSED')
                self.previous_process_io[key] = io
                rows[pid] = dict(pid=pid, start_ticks=before['start_ticks'], state=after['state'],
                    cgroup=current_membership, io=io, io_delta=delta,
                    attribution='EXACT_PROCESS_INSTANCE_COUNTERS_NOT_DEVICE_LATENCY_OR_HARM')
            except (FileNotFoundError, ProcessLookupError):
                ended.append(dict(pid=pid, reason='ABSENT_DURING_BOUNDED_SAMPLE_NO_LIVE_IDENTITY_CLAIM'))
            except (OSError, ValueError, KeyError, TypeError) as error:
                unresolved.append(dict(pid=pid, reason=repr(error)))

        for pid in sorted(first):
            read_member(pid)
        second = {int(value) for value in (cg / 'cgroup.procs').read_text().split()}
        require(len(second) <= MAX_CGROUP_MEMBERS, 'CGROUP_INVENTORY_BOUND_EXCEEDED')
        for pid in sorted(second - first):
            read_member(pid)
        missing = second - set(rows)
        # A member absent after its read may have exited. It is no longer live,
        # and confers no current authority or invented zero IO. Check once only.
        for pid in sorted(missing):
            try:
                live = self.identity(pid)
                if live['state'] != 'Z':
                    unresolved.append(dict(pid=pid, reason='CURRENT_CGROUP_MEMBER_UNBOUND'))
            except (FileNotFoundError, ProcessLookupError):
                pass
        self.previous_process_io = {(r['pid'], r['start_ticks']): r['io']
                                    for r in rows.values() if r['pid'] in second}
        raw = (cg / 'io.stat').read_text()
        devices = parsed_iostat(raw)
        device_delta = {}
        for device, counters in devices.items():
            previous = self.previous_device_io.get(device)
            device_delta[device] = None if previous is None else {
                k: value - previous[k] for k, value in counters.items() if k in previous}
            if device_delta[device] is not None and any(v < 0 for v in device_delta[device].values()):
                unresolved.append(dict(device=device, reason='DEVICE_IO_COUNTER_REVERSED'))
        self.previous_device_io = devices
        output_device = os.stat(self.output).st_dev
        return dict(known_scope=membership == '0::/' and not unresolved,
            monotonic_interval_ns=[began, time.monotonic_ns()], membership=membership,
            first_members=sorted(first), second_members=sorted(second), process_instances=list(rows.values()),
            absent_during_sample=ended, unresolved=unresolved, io_stat_raw=raw,
            io_stat=devices, io_stat_delta=device_delta,
            output_filesystem_device=output_device,
            output_filesystem_major_minor=str(os.major(output_device)) + ':' + str(os.minor(output_device)),
            device_attribution='CGROUP_DEVICE_COUNTERS_NOT_EXCLUSIVE_SIMULATOR_ATTRIBUTION',
            impact_observability='HOST_GLOBAL_GUARD_AND_BOUNDED_EPISODE_ARE_REGISTERED_CONSERVATIVE_SURROGATE',
            atomic_scope_snapshot=False, external_task_harm_absence_proven=False)

    def sample(self, local):
        if callable(getattr(self, 'current_controller_check', None)):
            require(self.current_controller_check() is True, 'ROOT_CONTROLLER_IMAGE_IDENTITY_FAILED')
        # Registration, manager role, lock semantics, old history and review
        # function source are verified by ExplicitAG7Authority without rewriting
        # any legacy reviewer condition. No peer or simulator is discovered/adopted.
        key = id(local)
        if key not in self.reviews:
            self.reviews[key] = self.authority.bind_review(local, peer_provider=lambda: [])
        snapshot, verdict = self.reviews[key](self.owner)
        snapshot = self.resources.enrich(snapshot, self.output)
        snapshot['ag7_io_scope'] = self.scope(snapshot)
        if self.first_oom is None:
            self.first_oom = dict(host=snapshot['host_oom_kill'],
                cgroup=dict(snapshot['cgroup']['events']))
        return snapshot, verdict

    def io_impact(self, point, ownership, pid, current):
        scope = current.get('ag7_io_scope', {})
        acceptance = self.pilot
        accepted = (isinstance(acceptance, dict) and
            acceptance.get('BA_explicit_conservative_pilot_surrogate_accepted') is True and
            acceptance.get('host_io_three_ge30s_preserved') is True and
            acceptance.get('maximum_cgroup_high_episode_s') == 1800 and
            acceptance.get('no_external_task_harm_claim') is True)
        reasons = []
        if current['host_MemAvailable_bytes'] < 8 * GIB:
            reasons.append('OBSERVED_HOST_HEADROOM_DANGER')
        if self.first_oom is None or current['host_oom_kill'] != self.first_oom['host'] or any(
            current['cgroup']['events'][k] != self.first_oom['cgroup'][k] for k in ('oom', 'oom_kill')):
            reasons.append('OBSERVED_NEW_OOM_OR_MISSING_BASELINE')
        members = scope.get('process_instances', [])
        own_instances = {(p, row['start_ticks']) for p, row in ownership.confirmed.items()}
        return dict(known_scope=scope.get('known_scope') is True,
            harm_detected=bool(reasons), detected_harm_reasons=reasons,
            conservative_host_episode_profile_accepted=accepted,
            observed_own_instances=[r for r in members if (r['pid'], r['start_ticks']) in own_instances],
            other_current_instances=[r for r in members if (r['pid'], r['start_ticks']) not in own_instances],
            membership_interval_ns=scope.get('monotonic_interval_ns'),
            measured_harmlessness=False, shared_cgroup_scope=True,
            no_harm_inference_from_progress_or_low_host_PSI=True,
            safety_basis='EXPLICIT_BA_REGISTERED_HOST_GLOBAL_PLUS_1800S_EPISODE_SURROGATE')


def current_guard_checks(point, ownership, pid, current, authority, *, mapping_manifests,
                         identity_reader, expected_output_device, expected_remaining_write_bytes,
                         interrupted, ledger_is_current):
    """Actual current checks consumed by RuntimePolicyB, no blanket true dict."""
    live = identity_reader(pid)
    instance = ownership.confirmed.get(pid)
    same = bool(instance and live['start_ticks'] == instance['start_ticks'] and
                live['tracer_pid'] == ownership.tracer)
    unknown = []
    for child, proven in ownership.confirmed.items():
        try:
            actual = identity_reader(child)
            exe = os.readlink('/proc/' + str(child) + '/exe')
            if actual['start_ticks'] != proven['start_ticks'] or exe not in mapping_manifests:
                unknown.append(child)
        except (FileNotFoundError, ProcessLookupError):
            # Confirmed but not yet reaped cannot be granted current identity.
            unknown.append(child)
    output = Path(point['destination'])
    streams = [output / 'ENGINE/stdout', output / 'ENGINE/stderr']
    stream_limits = [point['stdout_bound_bytes'], point['stderr_bound_bytes']]
    output_ok = all(not path.exists() or path.stat().st_size <= limit
                    for path, limit in zip(streams, stream_limits))
    return dict(authority=authority['status'] in (PASS, PENDING) and ledger_is_current is True,
        identity=same and os.readlink('/proc/' + str(pid) + '/exe') == point['runtime_path'],
        mapper=same and not unknown and (output / 'ENGINE/MAP_EVENTS.jsonl').exists(),
        output_limits=output_ok,
        output_device=current['output_filesystem_device'] == expected_output_device,
        expected_growth=(current['disk_free_bytes'] - expected_remaining_write_bytes > 5 * GIB),
        explicit_abort_clear=not interrupted, ownership=same and not unknown)


def collect_actual(*, point, run, engine, runtime, receiver, terminal, last_fault,
                   ownership, dispatch, sampler, legacy_close, legacy_strict, strict_adapter,
                   registration_bytes, registration_sha256, provenance_bytes,
                   identity_receipt, publication_head, final_static_check,
                   expected_base_decision_sha256):
    """Actual receipt join; every scientific validator executes before acceptance.

    final_static_check() must refresh exact source/runtime/input/config identity
    via the actual validator, compare its frozen science/runtime registration,
    and verify unchanged publication. Returning claimed JSON is insufficient.
    provenance_bytes has old_preregistration/science_manifest/kernel_audit/
    metric_dictionary already authenticated by original parser pins.
    """
    run = Path(run)
    require(ownership is not None, 'NO_ACTUAL_OWNERSHIP_LIFECYCLE')
    current, authority = sampler.sample(ownership)
    # The terminated root cannot have a new live /proc identity. Its exact exit
    # instance and completed mapper/event closure replace live-instance checks.
    natural = dispatch['actual_guard_natural_exit_zero'] is True
    mapping_receipt = None
    failure = None
    try:
        require(natural and not dispatch['stopped'], 'ACTUAL_GUARD_STOP_OR_NONNATURAL_EXIT')
        require(receiver is not None and receiver.terminal == 'NATURAL', 'NO_FRESH_NATURAL_PRODUCER_TERMINAL')
        require(receiver.last_semantic['completed'] == point['expected_instructions'],
                'PRODUCER_FINAL_SEMANTIC_COMPLETION_DOES_NOT_EQUAL_WHOLE_INPUT')
        mapping_receipt = legacy_close.close_mapping(run / 'ENGINE', identity_receipt['mapping_manifests'])
        with (run / 'ENGINE/MAP_EVENTS.jsonl').open() as stream:
            for line in stream:
                event = json.loads(line)
                require(not (event.get('stage') == 'EXEC_EVENT' and
                    event.get('exe') == point['runtime_path'] and event['pid'] != engine['root_pid']),
                    'FINAL_UNREGISTERED_SECOND_OWN_SIMULATOR_EXEC')
        write(run / 'MAPPING_CLOSURE.json', mapping_receipt)
        checks = dict(authority=authority['status'] == PASS,
            identity=engine['identity_pass'] is True,
            mapper=mapping_receipt['status'] == 'PASS_ACTUAL_CLOSED_GUARD_EVENT_MAPPING_EXIT_JOIN',
            output_limits=True,  # Run_one checked full evidence bounds before natural return; recheck below.
            output_device=current['output_filesystem_device'] == point['output_filesystem_device'],
            expected_growth=current['disk_free_bytes'] > 5 * GIB,
            explicit_abort_clear=not dispatch['stopped'],
            ownership=not ownership.confirmed and not ownership.pending)
        sizes = {name: (run / name).stat().st_size for name in
            ('ENGINE/stdout', 'ENGINE/stderr', 'ENGINE/MAP_EVENTS.jsonl', 'RESOURCE_MONITOR.jsonl', 'PROGRESS.jsonl')}
        checks['output_limits'] = (sizes['ENGINE/stdout'] <= point['stdout_bound_bytes'] and
            sizes['ENGINE/stderr'] <= point['stderr_bound_bytes'] and
            sum(sizes.values()) + mapping_receipt['map_payload_bytes'] <= point['maximum_attempt_output_bytes'])
        impact = sampler.io_impact(point, ownership, engine['root_pid'], current)
        decision = runtime.observe(current, last_fault, last_fault,
            progress=receiver.last_semantic, safety_checks=checks, io_impact=impact)
        write(run / 'RESOURCE_FINAL.json', dict(snapshot=current, authority=authority, decision=decision))
        require(decision['decision'] != 'STOP' and authority['status'] == PASS,
                'ACTUAL_FINAL_RESOURCE_AUTHORITY_OR_PROGRESS_FAILED')
        require(final_static_check() is True, 'FINAL_SOURCE_INPUT_RUNTIME_PUBLICATION_IDENTITY_FAILED')
    except Exception as error:
        failure = repr(error)
        terminal.observe(actual_stop=True)
    write(run / 'RUN_TERMINAL.json', dict(returncode=engine['returncode'],
        forced_reason=engine.get('forced_reason') or failure,
        identity_pass=engine['identity_pass'] is True and failure is None, engine=engine))
    if failure:
        result = dict(status='HOLD_AG7_ACTUAL_CLOSURE_FAILED', point=point['point'],
            attempt_uuid=point['attempt_uuid'], reason=failure, performance_accepted=False,
            scientific_strict_pass=False, cycles='UNAVAILABLE', automatic_retry=False)
        write(run / 'STRICT.json', result)
        return result
    start = json.loads((run / 'RUN_START.json').read_text())
    require(start['publication_head'] == publication_head and
        start['point'] == point['point'] and start['attempt_uuid'] == point['attempt_uuid'] and
        start['argv'] == identity_receipt['validated_argv'], 'ACTUAL_START_PUBLICATION_IDENTITY_JOIN')
    engine_start = json.loads((run / 'ENGINE/START.json').read_text())
    require(engine_start['argv'] == start['argv'] and engine_start['environment'] == start['environment'],
            'ACTUAL_GUARD_ARGV_FULL_ENVIRONMENT_JOIN')
    expected_env = dict(point['runtime_environment'])
    expected_env['DTC_AG7_PROGRESS_FD'] = start['environment']['DTC_AG7_PROGRESS_FD']
    require(start['environment'] == expected_env, 'OBSERVATIONAL_CHANNEL_ENVIRONMENT_CHANGED')
    samples = 0
    with (run / 'RESOURCE_MONITOR.jsonl').open() as stream:
        for line in stream:
            row = json.loads(line)
            require(row['decision']['decision'] != 'STOP' and row['authority']['status'] in (PASS, PENDING)
                and row['snapshot']['ag7_io_scope']['known_scope'] is True,
                'RUNTIME_SAFETY_AUTHORITY_OR_IO_SCOPE_FAILED')
            samples += 1
    require(samples > 0, 'NO_ACTUAL_RUNTIME_RESOURCE_OBSERVATION')
    report = strict_adapter.parse_attempt(legacy_strict, point['point'],
        stdout=(run / 'ENGINE/stdout').read_bytes(), stderr=(run / 'ENGINE/stderr').read_bytes(),
        run_start=(run / 'RUN_START.json').read_bytes(), run_terminal=(run / 'RUN_TERMINAL.json').read_bytes(),
        engine_terminal=(run / 'ENGINE/TERMINAL.json').read_bytes(),
        registration=registration_bytes, registration_sha256=registration_sha256,
        expected_framework_version=identity_receipt['expected_embedded_framework_version'],
        expected_base_decision_sha256=expected_base_decision_sha256,
        **provenance_bytes)
    closures = dict(strict_complete=report['scientific_strict_pass'] is True,
        runtime_identity_complete=natural, input_roi_complete=True,
        source_options_complete=report['scientific_strict_pass'] is True,
        guard_safety_complete=True, event_loader_complete=mapping_receipt is not None,
        single_instance_lifetime_complete=True, no_prior_stop=not dispatch['stopped'])
    closure = terminal.observe(producer_end=receiver.terminal, run_ended=True,
        natural_exit_zero=natural, closure=closures)
    report.update(terminal_closure=closure, resource_samples=samples, publication_head=publication_head,
        performance_accepted=report['scientific_strict_pass'] is True and closure['state'] == 'COMPLETE_CANDIDATE',
        mapping_closure_sha256=sha(run / 'MAPPING_CLOSURE.json'),
        runtime_resource_monitor_sha256=sha(run / 'RESOURCE_MONITOR.jsonl'),
        final_resource_sha256=sha(run / 'RESOURCE_FINAL.json'),
        input_runtime_identity_sha256=sha(run / 'INPUT_RUNTIME_IDENTITY.json'),
        progress_sha256=sha(run / 'PROGRESS.jsonl'),
        acceptance_scope='ACTUAL_AG7_FULL_INPUT_OWN_SOURCE_BOUND_GUARD_AND_POLICY_B_CLOSURE')
    if report['performance_accepted']:
        report.update(status='PASS_ACTUAL_REGISTERED_AG7_FULL_STRICT_EVIDENCE',
            BASE_cycles=point['imported_BASE_cycles'],
            speedup_exact=dict(numerator=point['imported_BASE_cycles'], denominator=report['cycles']))
    write(run / 'STRICT.json', report)
    return report
