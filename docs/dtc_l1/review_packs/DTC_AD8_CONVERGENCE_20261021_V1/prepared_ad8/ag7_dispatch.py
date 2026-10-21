"""Prepared AG7 single-point adapter; no CLI, release, manifest or UUID creation.

The sole BA controller must supply source-frozen dependencies and authenticated
callbacks, fresh heavy R2, publication, budget, and scientific eligibility. This
module cannot grant itself authority. Importing performs no work. A returned
COMPLETE_CANDIDATE is still not a scientific/performance PASS. The controller
must retain its existing exclusive authority lock through this whole call.
"""
import json
from pathlib import Path
import socket
import time

EVIDENCE = Path('/workspace/dtc-ag8-ad-convergence-174-v1')
ORDER = ('AD_GEMM', 'AD_Gaussian')
GIB = 1024 ** 3
AUTH_PASS = 'PASS_CURRENT_NO_OTHER_DTC_DISPATCH_AUTHORITY'
AUTH_PENDING = 'PENDING_QUARANTINED_NO_AUTHORITY_PASS'
ENV_KEYS = ('DTC_AG7_POLICY_B_PROGRESS', 'DTC_AG7_GENERATION',
            'DTC_AG7_INPUT_SHA', 'DTC_AG7_ROI_SHA')
REQUIRED_HOOKS = ('pre_fork', 'consume_start', 'verify_consumed', 'sample',
                  'guard_checks', 'io_impact', 'validate_root_image')


def require(value, reason):
    if not value:
        raise ValueError(reason)


def write_new(path, value):
    with Path(path).open('x') as stream:
        json.dump(value, stream, sort_keys=True)
        stream.write('\n')


def append(path, value):
    with Path(path).open('a') as stream:
        stream.write(json.dumps(value, sort_keys=True) + '\n')


def run_one(point, *, baseline, mapping_manifests, deps, hooks):
    """One consumed, unretryable guarded point. Root alone may call this.

    point: registered point/attempt_uuid/destination/runtime_path/validated_argv,
      runtime_environment (all ENV_KEYS), output limits (stdout_bound_bytes,
      stderr_bound_bytes, maximum_attempt_output_bytes). Runtime FD must not be
      preregistered as a guessed integer: pre_fork validates its observational
      FD binding and exact full environment, then RUN_START records that binding.
    deps: frozen run_guarded/resource_module/proc_reader/receiver_module/
      runtime_module. No live unreviewed module is imported here.
    hooks: authenticated BA callbacks named REQUIRED_HOOKS. pre_fork must verify
      remote/source/BASE/W1/W2/full R2/current authority and exclusive controller
      lock; consume_start atomically persists the separate AG7 ledger exactly
      once and returns {consumed: True, attempt_uuid: ...}; verify_consumed
      authenticates that ledger row and unstarted eligible fixed prefix.
    sample, guard_checks and io_impact use original all-project scope and actual
      ownership. validate_root_image binds loader/image/input/ROI generation.
    No callback may infer authority or IO impact merely from semantic progress.
    """
    require(all(callable(hooks.get(k)) for k in REQUIRED_HOOKS), 'MISSING_TRUSTED_CONTROLLER_HOOK')
    require(all(k in deps for k in ('run_guarded', 'resource_module', 'proc_reader',
                                    'receiver_module', 'runtime_module')), 'MISSING_FROZEN_DEPENDENCY')
    require(point['point'] in ORDER and isinstance(point['attempt_uuid'], str), 'UNREGISTERED_AG7_POINT')
    run = Path(point['destination']).resolve()
    require(run.is_relative_to(EVIDENCE) and run != EVIDENCE and not run.exists(),
            'NEW_INDEPENDENT_ATTEMPT_DESTINATION_REQUIRED')
    require(Path(point['runtime_path']).is_absolute() and
            point['validated_argv'][0] == point['runtime_path'], 'EXACT_REGISTERED_EXECUTABLE_REQUIRED')
    for key in ('stdout_bound_bytes', 'stderr_bound_bytes', 'maximum_attempt_output_bytes'):
        require(type(point[key]) is int and point[key] > 0, 'REGISTERED_OUTPUT_LIMIT_REQUIRED:' + key)
    env = dict(point['runtime_environment'])
    require(all(key in env for key in ENV_KEYS) and env['DTC_AG7_POLICY_B_PROGRESS'] == '1',
            'EXPLICIT_REGISTERED_TELEMETRY_SCOPE_REQUIRED')
    require('DTC_AG7_PROGRESS_FD' not in env, 'DYNAMIC_CHANNEL_FD_MUST_BE_BOUND_AT_RELEASE')
    rx, tx = socket.socketpair(socket.AF_UNIX, socket.SOCK_DGRAM)
    receiver = None
    engine = None
    consumed = None
    stopped = []
    terminal = deps['runtime_module'].TerminalClosure()
    started_ns = baseline['monotonic_ns']
    runtime = None
    next_sample_ns = 0
    last_fault = 0
    event_offset = 0
    map_bytes = 0
    packet_count = 0
    root_binding = None
    last_ownership = None
    natural_exit_defer_ns = None
    tx_open = True
    record_bytes = 0
    try:
        runtime = deps['runtime_module'].RuntimePolicyB(baseline, EVIDENCE,
            resource_module=deps['resource_module'], started_ns=started_ns, opt_in=True)
        rx.setblocking(False)
        rx.setsockopt(socket.SOL_SOCKET, socket.SO_PASSCRED, 1)
        tx.setblocking(False)
        tx.set_inheritable(True)
        env['DTC_AG7_PROGRESS_FD'] = str(tx.fileno())
        require(hooks['pre_fork'](point, env, baseline) is True, 'ALL_RELEASE_AND_HEAVY_R2_GATES_REQUIRED')
        require(0 <= time.monotonic_ns() - started_ns <= 5 * 10**9, 'FRESH_FINAL_R2_REQUIRED')
        run.mkdir(parents=True, exist_ok=False)
        require(run.stat().st_dev == baseline['output_filesystem_device'], 'OUTPUT_FILESYSTEM_CHANGED')
        write_new(run / 'FINAL_PRE_FORK.json', baseline)
        start = dict(point=point['point'], attempt_uuid=point['attempt_uuid'],
            order=point['order'], source_core=point['core_commit'], retries=0,
            config_copies=point['config_copies'], publication_head=point['publication_head'],
            argv=point['validated_argv'], environment=env, timeout_seconds=21600,
            channel_kind='AF_UNIX_SOCK_DGRAM_NONBLOCKING_SCM_CREDENTIALS',
            conservative_start_consumed=True, automatic_retry=False,
            qualification_canary=False, policy_profile=dict(deps['runtime_module'].PROFILE))
        # Ledger consumption precedes the exclusive start receipt and fork.
        # Any failure here is conservatively spent, never a replacement start.
        consumed = hooks['consume_start'](point, start)
        require(isinstance(consumed, dict) and consumed.get('consumed') is True and
                consumed.get('attempt_uuid') == point['attempt_uuid'], 'EXACT_AG7_CONSUMPTION_RECEIPT_REQUIRED')
        write_new(run / 'RUN_START.json', start)
        write_new(run / 'INPUT_RUNTIME_IDENTITY.json', point['identity_receipt'])

        def stop(reason):
            stopped.append(reason)
            terminal.observe(actual_stop=True)
            return reason

        def check_output_and_exec(root_pid):
            nonlocal event_offset, map_bytes
            events = run / 'ENGINE/MAP_EVENTS.jsonl'
            if events.exists():
                with events.open('rb') as stream:
                    stream.seek(event_offset)
                    for line in stream:
                        event = json.loads(line)
                        if 'maps' in event:
                            name = event['maps']
                            require(Path(name).name == name, 'INVALID_GUARD_MAP_PATH')
                            map_bytes += (run / 'ENGINE/maps' / name).stat().st_size
                        if (event.get('stage') == 'EXEC_EVENT' and
                                event.get('exe') == point['runtime_path'] and event['pid'] != root_pid):
                            return 'UNREGISTERED_SECOND_OWN_SIMULATOR_EXEC'
                    event_offset = stream.tell()
            sizes = {}
            for name in ('ENGINE/stdout', 'ENGINE/stderr', 'ENGINE/MAP_EVENTS.jsonl',
                         'ENGINE/OOM_MONITOR.jsonl', 'RESOURCE_MONITOR.jsonl', 'PROGRESS.jsonl'):
                path = run / name
                sizes[name] = path.stat().st_size if path.exists() else 0
            if sizes['ENGINE/stdout'] > point['stdout_bound_bytes'] or sizes['ENGINE/stderr'] > point['stderr_bound_bytes']:
                return 'OWN_ATTEMPT_STREAM_OUTPUT_BOUND'
            if map_bytes + sum(sizes.values()) > point['maximum_attempt_output_bytes']:
                return 'OWN_ATTEMPT_EVIDENCE_OUTPUT_BOUND'
            return None

        def capability(target, argv, environment):
            require(hooks['verify_consumed'](point, consumed) is True, 'EXACT_CURRENT_AG7_LEDGER_REQUIRED')
            require(target == point['runtime_path'] and argv == point['validated_argv'] and environment == env,
                    'EXACT_SINGLE_REGISTERED_POINT_REQUIRED')
            require(not (run / 'ENGINE/FORK_CHILD.json').exists(), 'NO_SECOND_FORK')
            require(hooks['pre_fork'](point, env, baseline) is True, 'LAST_MOMENT_RELEASE_FAILED')
            require(0 <= time.monotonic_ns() - started_ns <= 5 * 10**9, 'FINAL_R2_STALE_NO_FORK')

        def drain(now_ns):
            nonlocal packet_count, record_bytes
            state = receiver.drain(time.monotonic_ns)
            for row in state['records']:
                encoded = json.dumps(row, sort_keys=True) + '\n'
                record_bytes += len(encoded.encode())
                require(record_bytes <= 8 * 1024**2, 'BOUNDED_PROGRESS_OUTPUT_EXCEEDED')
                with (run / 'PROGRESS.jsonl').open('a') as stream:
                    stream.write(encoded)
                packet_count += 1
            if state['terminal'] is not None:
                terminal.observe(producer_end=state['terminal'])
            return state

        def defer_proven_zombie(pid, ownership):
            nonlocal natural_exit_defer_ns
            if receiver is None or receiver.terminal != 'NATURAL' or pid not in ownership.confirmed:
                return False
            try:
                fields = Path('/proc/' + str(pid) + '/stat').read_text().rsplit(')', 1)[1].split()
            except (FileNotFoundError, ProcessLookupError):
                return False
            if (fields[0] != 'Z' or int(fields[19]) != root_binding['start_ticks'] or
                    ownership.confirmed[pid]['start_ticks'] != root_binding['start_ticks']):
                return False
            if natural_exit_defer_ns is None:
                natural_exit_defer_ns = time.monotonic_ns()
            require(time.monotonic_ns() - natural_exit_defer_ns <= 2 * 10**9,
                    'NATURAL_ROOT_REAP_HANDOFF_EXCEEDED_2S')
            return True

        def observer(pid, full_hint, ownership):
            nonlocal receiver, next_sample_ns, last_fault, root_binding, tx_open, last_ownership, natural_exit_defer_ns
            try:
                last_ownership = ownership
                if callable(hooks.get('abort_requested')) and hooks['abort_requested']():
                    return stop('EXPLICIT_CANONICAL_CONTROLLER_ABORT')
                now_ns = time.monotonic_ns()
                if receiver is None:
                    require(pid in ownership.confirmed, 'ACTUAL_ROOT_NOT_EVENT_CONFIRMED')
                    ownership.same(pid)
                    instance = ownership.confirmed[pid]
                    require(hooks['validate_root_image'](point, pid, instance) is True,
                            'ACTUAL_ROOT_IMAGE_INPUT_ROI_NOT_BOUND')
                    root_binding = dict(pid=pid, start_ticks=instance['start_ticks'],
                        generation=env['DTC_AG7_GENERATION'], input=env['DTC_AG7_INPUT_SHA'],
                        roi=env['DTC_AG7_ROI_SHA'], proven_actual_root=True)
                    receiver = deps['receiver_module'].TelemetryReceiver(
                        rx, root_binding, started_ns=started_ns, opt_in=True)
                    write_new(run / 'ACTUAL_PRODUCER_BINDING.json', root_binding)
                    # Only the already forked child retains its sender end.
                    tx.close()
                    tx_open = False
                ownership.same(pid)
                extra = check_output_and_exec(pid)
                if extra:
                    return stop(extra)
                quick = runtime.quick_stop()
                if quick:
                    return stop(quick)
                state = drain(now_ns)
                if terminal.state == 'STOP_UNACCEPTED':
                    return stop(terminal.reason)
                if now_ns < next_sample_ns:
                    return None
                current, authority = hooks['sample'](ownership)
                require(authority['status'] in (AUTH_PASS, AUTH_PENDING), 'RUNTIME_GLOBAL_AUTHORITY_NOT_CLOSED')
                own = deps['proc_reader'](pid)
                # NATURAL is still only a producer candidate. A proven zombie
                # can exit during all-project sampling; leave wait/reap to the
                # original guard instead of inventing a new live /proc image.
                # This one finite handoff never renews telemetry/retirement or
                # resource clocks, and cannot hide a lingering helper forever.
                if (receiver.terminal == 'NATURAL' and own is not None and
                        own['state'] == 'Z' and own['start_ticks'] == root_binding['start_ticks']):
                    if defer_proven_zombie(pid, ownership):
                        return None
                natural_exit_defer_ns = None
                fault = own['majflt']
                current_checks = hooks['guard_checks'](point, ownership, pid, current)
                current_impact = hooks['io_impact'](point, ownership, pid, current)
                decision = runtime.observe(current, fault, last_fault,
                    progress=state['latest_semantic'], safety_checks=current_checks, io_impact=current_impact)
                last_fault = fault
                next_sample_ns = current['monotonic_ns'] + min(10, decision['next_full_sample_seconds']) * 10**9
                append(run / 'RESOURCE_MONITOR.jsonl', dict(snapshot=current, authority=authority,
                    decision=decision, own=own, producer=root_binding,
                    packets=packet_count, shared_cgroup_attribution_is_not_process_attribution=True))
                if decision['decision'] == 'STOP':
                    return stop(';'.join(decision['stop_reasons']))
                return None
            except Exception as error:
                if isinstance(error, (FileNotFoundError, ProcessLookupError)):
                    try:
                        if defer_proven_zombie(pid, ownership):
                            return None
                    except Exception:
                        pass
                return stop('POLICY_B_OBSERVER_FAIL_CLOSED:' + repr(error))

        engine = deps['run_guarded'](point['validated_argv'], env, mapping_manifests,
            run / 'ENGINE', 'SIMULATION', 21600, capability, observer)
        # Guard has already closed and reaped. This packet join cannot invent
        # a natural exit, ownership closure, or scientific strict receipt.
        if receiver is None:
            terminal.observe(actual_stop=True)
            stopped.append('NO_ACTUAL_PRODUCER_BINDING')
        else:
            try:
                drain(time.monotonic_ns())
            except Exception as error:
                stopped.append('FINAL_TELEMETRY_FAIL_CLOSED:' + repr(error))
                terminal.observe(actual_stop=True)
        natural = (engine.get('status') == 'PASS_GUARDED_NATURAL_EXIT0' and
            engine.get('returncode') == 0 and engine.get('forced_reason') is None and
            engine.get('identity_pass') is True and engine.get('owned_children_live') == 0 and
            not engine.get('unconfirmed_wait_pids') and
            isinstance(engine.get('ownership'), dict) and
            not engine['ownership'].get('confirmed') and not engine['ownership'].get('pending'))
        # Final resource/authority/strict receipt join belongs to the controller.
        # Intentionally do not pass run_ended=True here without all strict keys.
        join = terminal.observe(actual_stop=bool(stopped) or not natural)
        result = dict(point=point['point'], attempt_uuid=point['attempt_uuid'], engine=engine,
            terminal=join, actual_guard_natural_exit_zero=natural, stopped=stopped,
            packet_count=packet_count, producer_binding=root_binding,
            producer_terminal=None if receiver is None else receiver.terminal,
            latest_progress=None if receiver is None else receiver.last_semantic,
            scientific_acceptance=False, performance_accepted=False,
            requires_controller_final_resource_authority_strict_join=True,
            consumed_start=consumed, automatic_retry=False)
        write_new(run / 'DISPATCH_JOIN_PENDING.json', result)
        if callable(hooks.get('finalize')):
            result['finalized'] = hooks['finalize'](point=point, run=run, engine=engine,
                runtime=runtime, receiver=receiver, terminal=terminal,
                last_fault=last_fault, ownership=last_ownership, dispatch=result)
        return result
    except BaseException as error:
        if run.exists() and not (run / 'DISPATCH_EXCEPTION.json').exists():
            write_new(run / 'DISPATCH_EXCEPTION.json', dict(reason=repr(error), engine=engine,
                consumed_start=consumed, scientific_acceptance=False, automatic_retry=False))
        raise
    finally:
        if tx_open:
            tx.close()
        rx.close()
