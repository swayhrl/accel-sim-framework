"""Run ONLY after the canonical controller has completed and been reaped.

Report engineering only: no simulator/fixture/authority/import of a controller,
preflight, UUID, budget mutation, signal, retry, target execution or raw stdout
read. Reads completed own evidence and writes compact Git review artifacts.
This helper is deliberately outside the published source/dispatch closure.
"""
import hashlib
import json
import math
from pathlib import Path
from fractions import Fraction
from datetime import datetime, timezone, timedelta

ROOT = Path('/workspace/dtc-ag7-policyb-integrated-174-v1')
EVIDENCE = ROOT / 'evidence'
REPO = Path('/workspace/worktrees/accel-sim-iscas2027-dtc-ag7-policyb-integrated-174-v1')
PACK = REPO / 'docs/dtc_l1/review_packs/DTC_AG7_POLICYB_INTEGRATED_20261020_V1'
ORDER = ('AE_GEMM', 'AE_Gaussian', 'AD_GEMM', 'AD_Gaussian')
GOAL = 'DTC_AG7_POLICY_B_INTEGRATED_V1'
O = 'K0/OO128/Tag64x8/AE0/AD0'
MAX_JSON = 4 * 1024 ** 2
MAX_JSONL = 128 * 1024 ** 2


def require(value, reason):
    if not value:
        raise ValueError(reason)


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 ** 2), b''):
            h.update(block)
    return h.hexdigest()


def read(path, optional=False):
    path = Path(path)
    if optional and not path.exists():
        return None
    require(path.is_file() and path.stat().st_size <= MAX_JSON,
            'BOUNDED_COMPLETED_JSON_REQUIRED:' + str(path))
    return json.loads(path.read_text())


def ref(path, optional=False):
    path = Path(path)
    if optional and not path.exists():
        return dict(path=str(path), available=False)
    require(path.is_file(), 'EVIDENCE_REFERENCE_MISSING:' + str(path))
    # Never consume stdout/stderr/maps/trace/binary payloads. Their authenticated
    # hashes, when available, are already in STRICT or mapping-closure receipts.
    require(path.name not in ('stdout', 'stderr') and path.suffix not in ('.traceg', '.so', '.out'),
            'RAW_PAYLOAD_READ_FORBIDDEN')
    require(path.stat().st_size <= MAX_JSONL, 'EVIDENCE_TOO_LARGE_FOR_COMPACT_FINALIZER')
    return dict(path=str(path), available=True, bytes=path.stat().st_size, sha256=sha(path))


def exact_instance_state(pid, ticks):
    """Read only the exact previously owned PID; reused PID is not adopted."""
    require(type(pid) is int and pid > 0 and type(ticks) is int and ticks > 0,
            'EXACT_OWN_INSTANCE_PROOF_REQUIRED')
    try:
        text = Path('/proc', str(pid), 'stat').read_text()
    except FileNotFoundError:
        return dict(pid=pid, start_ticks=ticks, state='ABSENT_OWN_INSTANCE', live=False)
    fields = text[text.rfind(')') + 2:].split()
    current_ticks = int(fields[19])
    same = current_ticks == ticks
    return dict(pid=pid, start_ticks=ticks, observed_start_ticks=current_ticks,
                state=('OWN_INSTANCE_STILL_PRESENT_' + fields[0]) if same else 'PID_REUSED_NOT_OWN_INSTANCE',
                live=same)


def lines(path, reference):
    """One bounded binary stream supplies both exact raw SHA and summary rows."""
    path = Path(path)
    if not path.exists():
        reference.update(path=str(path), available=False)
        return
    before = path.stat()
    require(before.st_size <= MAX_JSONL, 'BOUNDED_COMPLETED_JSONL_REQUIRED')
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        while True:
            line = stream.readline(1024 ** 2 + 1)
            if not line:
                break
            require(len(line) <= 1024 ** 2, 'OVERSIZE_COMPLETED_JSONL_RECORD')
            digest.update(line)
            if line.strip():
                try:
                    row = json.loads(line)
                    require(isinstance(row, dict), 'JSONL_RECORD_NOT_OBJECT')
                    yield row
                except (ValueError, UnicodeError) as error:
                    yield {'_summary_parse_error': type(error).__name__}
    after = path.stat()
    require(all(getattr(before, k) == getattr(after, k) for k in
            ('st_dev', 'st_ino', 'st_size', 'st_mtime_ns', 'st_ctime_ns')),
            'COMPLETED_JSONL_CHANGED_DURING_FINALIZATION')
    reference.update(path=str(path), available=True, bytes=before.st_size,
                     sha256=digest.hexdigest(), summary_and_hash_stream_passes=1)


def pressure(snapshot, domain):
    source = snapshot['pressure'] if domain == 'host' else snapshot['cgroup_pressure_parsed']
    return float(source['io']['full']['avg10'])


def resource_summary(path):
    result = dict(samples=0, warnings=0, stop_decisions=0, stop_reasons=[],
                  maximum_host_io_full_avg10=None, maximum_cgroup_io_full_avg10=None,
                  host_io_high_samples=0, cgroup_io_high_samples=0,
                  minimum_disk_free_bytes=None, maximum_resource_sample_gap_ns=None,
                  reversed_resource_timestamps=0, authority_failure_samples=0,
                  authority_nonpass_samples=0, authority_status_counts={}, warning_reasons=[],
                  malformed_records=0, unknown_io_scope_samples=0,
                  source_reference={}, attribution='SHARED_CGROUP_NOT_SIMULATOR_EXCLUSIVE')
    first = last = None
    for row in lines(path, result['source_reference']):
        try:
            snapshot, decision = row['snapshot'], row['decision']
            stamp = snapshot['monotonic_ns']
            require(type(stamp) is int and stamp > 0, 'INVALID_RESOURCE_TIMESTAMP')
            kind = decision['decision']
            require(kind in ('CONTINUE', 'WARN', 'STOP'), 'UNKNOWN_RESOURCE_DECISION')
        except (KeyError, TypeError, ValueError):
            result['malformed_records'] += 1
            continue
        first = stamp if first is None else first
        if last is not None:
            gap = stamp - last
            result['reversed_resource_timestamps'] += gap <= 0
            result['maximum_resource_sample_gap_ns'] = max(
                result['maximum_resource_sample_gap_ns'] or 0, gap)
        last = stamp
        result['samples'] += 1
        result['warnings'] += kind == 'WARN'
        result['stop_decisions'] += kind == 'STOP'
        result['stop_reasons'] += [r for r in decision.get('stop_reasons', []) if r not in result['stop_reasons']]
        result['warning_reasons'] += [r for r in decision.get('warnings', []) if r not in result['warning_reasons']]
        result['unknown_io_scope_samples'] += snapshot.get('ag7_io_scope', {}).get('known_scope') is not True
        authority = row.get('authority', {}).get('status', 'UNAVAILABLE')
        if not isinstance(authority, str):
            authority = 'MALFORMED'
        result['authority_status_counts'][authority] = result['authority_status_counts'].get(authority, 0) + 1
        result['authority_nonpass_samples'] += authority != 'PASS_CURRENT_NO_OTHER_DTC_DISPATCH_AUTHORITY'
        result['authority_failure_samples'] += authority not in (
            'PASS_CURRENT_NO_OTHER_DTC_DISPATCH_AUTHORITY', 'PENDING_QUARANTINED_NO_AUTHORITY_PASS')
        free = snapshot.get('disk_free_bytes')
        if type(free) is int and free >= 0:
            result['minimum_disk_free_bytes'] = free if result['minimum_disk_free_bytes'] is None else min(
                result['minimum_disk_free_bytes'], free)
        else:
            result.setdefault('unknown_disk_samples', 0)
            result['unknown_disk_samples'] += 1
        for domain in ('host', 'cgroup'):
            try:
                value = pressure(snapshot, domain)
                require(math.isfinite(value) and 0 <= value <= 100, 'INVALID_IO_PRESSURE')
            except (KeyError, TypeError, ValueError):
                result.setdefault('unparsed_pressure_samples', 0)
                result['unparsed_pressure_samples'] += 1
                continue
            key = 'maximum_' + domain + '_io_full_avg10'
            result[key] = value if result[key] is None else max(result[key], value)
            result[domain + '_io_high_samples'] += value > 25
    result['monotonic_interval_ns'] = [first, last]
    result['first_monotonic_ns'], result['last_monotonic_ns'] = first, last
    return result


def progress_summary(path):
    result = dict(records=0, phases=[], terminal_labels=[], producer_gaps_over30s=0,
                  sequence_continuous=True, completion_counter_monotonic=True,
                  first_sequence=None, last_sequence=None, first_completed_counter=None,
                  last_completed_counter=None, first_monotonic_ns=None, last_monotonic_ns=None,
                  maximum_producer_record_gap_ns=None, malformed_records=0, terminal=None,
                  reversed_producer_timestamps=0,
                  source_reference={}, counters_are_diagnostic_not_performance=True,
                  consumer_freshness_not_reconstructed_from_producer_records_alone=True)
    previous = None
    for row in lines(path, result['source_reference']):
        try:
            require(all(type(row[key]) is int and row[key] >= 0 for key in
                    ('seq', 'mono_ns', 'completed')) and isinstance(row['phase'], str) and
                    isinstance(row['end'], str), 'MALFORMED_PROGRESS_RECORD')
        except (KeyError, TypeError, ValueError):
            result['malformed_records'] += 1
            continue
        result['records'] += 1
        if result['first_sequence'] is None:
            result['first_sequence'] = row['seq']
            result['first_completed_counter'] = row['completed']
            result['first_monotonic_ns'] = row['mono_ns']
        result['last_sequence'], result['last_completed_counter'] = row['seq'], row['completed']
        result['last_monotonic_ns'] = row['mono_ns']
        if row['phase'] not in result['phases']:
            result['phases'].append(row['phase'])
        if row['end'] != 'NONE':
            result['terminal_labels'].append(row['end'])
            result['terminal'] = row['end']
        if previous is not None:
            result['sequence_continuous'] &= row['seq'] == previous['seq'] + 1
            result['completion_counter_monotonic'] &= row['completed'] >= previous['completed']
            gap = row['mono_ns'] - previous['mono_ns']
            result['reversed_producer_timestamps'] += gap <= 0
            result['maximum_producer_record_gap_ns'] = max(result['maximum_producer_record_gap_ns'] or 0, gap)
            result['producer_gaps_over30s'] += gap > 30 * 10**9
        previous = row
    return result


def compact_traffic(value):
    if not isinstance(value, dict):
        return 'UNAVAILABLE'
    require(len(json.dumps(value)) <= 65536, 'TRAFFIC_SUMMARY_TOO_LARGE')
    return value


def write_json(path, value):
    data = json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + '\n'
    require(len(data.encode()) <= MAX_JSON, 'COMPACT_ARTIFACT_SIZE_LIMIT')
    Path(path).write_text(data)


def main():
    # Terminal must already exist. Never poll, sleep, wait, inspect active raw,
    # dispatch or force closure on behalf of a still-running controller.
    terminal_path = EVIDENCE / 'w3_controller_once/CONTROLLER_TERMINAL.json'
    terminal = read(terminal_path)
    require(terminal.get('canonical_task') == '/root' and terminal.get('status') in
            ('COMPLETE_AG7_STOP', 'AG7_HOLD_OR_STOP'), 'CANONICAL_FINAL_CONTROLLER_RECEIPT_REQUIRED')
    gate = read(EVIDENCE / 'W3_REGISTRATION_GATE_PASS.json')
    owner = gate['controller_owner']
    controller = exact_instance_state(owner['pid'], owner['start_ticks'])
    require(not controller['live'], 'CONTROLLER_NOT_REAPED_FINALIZER_MUST_NOT_RUN_YET')
    manifest_path = PACK / 'AG7_FOUR_POINT_MANIFEST.json'
    manifest = read(manifest_path)
    ledger_path = EVIDENCE / 'AG7_BUDGET_LEDGER.json'
    ledger = read(ledger_path)
    require(ledger['goal'] == manifest['goal'] == GOAL and
            ledger['manifest_sha256'] == sha(manifest_path), 'EXACT_FINAL_LEDGER_MANIFEST_JOIN')
    specs = manifest['points']
    require(tuple(p['point'] for p in specs) == ORDER and
            manifest['maximum_new_starts'] == ledger['maximum_new_starts'] == 4 and
            manifest['maximum_simultaneous_simulators'] == 1 and
            len({p['attempt_uuid'] for p in specs}) == 4, 'FIXED_FOUR_POINT_REGISTRATION_REQUIRED')
    entries = ledger['entries']
    require(len(entries) == ledger['consumed_start_slots'] <= 4 and
            tuple(x['point'] for x in entries) == ORDER[:len(entries)], 'FINAL_FIXED_PREFIX_LEDGER')
    actual = sum(x['actual_fork'] is True for x in entries)
    unknown = sum(x['actual_fork'] is None for x in entries)
    require(ledger['actual_forks'] == actual and ledger['unresolved_fork_slots'] == unknown and
            terminal['confirmed_actual_starts_minimum'] == actual and
            terminal['unresolved_fork_slots'] == unknown, 'FINAL_ACTUAL_START_COUNTS_DO_NOT_JOIN')
    records, accepted_metrics, owned_states = [], [], []
    for index, entry in enumerate(entries):
        spec = specs[index]
        require(entry['attempt_uuid'] == spec['attempt_uuid'] and entry['consumed'] is True,
                'ENTRY_IS_NOT_THE_REGISTERED_OWN_POINT')
        run = Path(entry['destination']).resolve()
        require(run == Path(spec['destination']).resolve() and run.is_relative_to(ROOT),
                'FINALIZER_CANNOT_READ_FOREIGN_ATTEMPT')
        start = read(run / 'RUN_START.json', optional=True)
        child = read(run / 'ENGINE/CHILD.json', optional=True)
        engine = read(run / 'ENGINE/TERMINAL.json', optional=True)
        strict = read(run / 'STRICT.json', optional=True)
        if start is not None:
            require(start['point'] == spec['point'] and start['attempt_uuid'] == spec['attempt_uuid'],
                    'REGISTERED_START_IDENTITY_MISMATCH')
        if child is not None:
            state = exact_instance_state(child['pid'], child['start_ticks'])
            owned_states.append(state)
            require(not state['live'], 'OWN_SIMULATOR_INSTANCE_REMAINS_PRESENT')
        if engine is not None:
            require(engine.get('owned_children_live') == 0 and not engine.get('unconfirmed_wait_pids', []),
                    'ENGINE_LIFECYCLE_NOT_CLOSED_FOR_REPORT')
            for instance in engine.get('owned_process_exit_instances', []):
                state = exact_instance_state(instance['pid'], instance['start_ticks'])
                owned_states.append(state)
                require(not state['live'], 'OWN_HELPER_INSTANCE_REMAINS_PRESENT')
        qualified = bool(strict is not None and engine is not None and
            strict.get('status') == 'PASS_ACTUAL_REGISTERED_AG7_FULL_STRICT_EVIDENCE' and
            strict.get('performance_accepted') is True and strict.get('scientific_strict_pass') is True and
            strict.get('terminal_closure', {}).get('state') == 'COMPLETE_CANDIDATE' and
            engine.get('status') == 'PASS_GUARDED_NATURAL_EXIT0' and engine.get('returncode') == 0 and
            engine.get('identity_pass') is True)
        require(entry['accepted'] is qualified, 'LEDGER_ACCEPTANCE_AND_FULL_STRICT_DISAGREE')
        references = {name: ref(run / name, optional=True) for name in (
            'RUN_START.json', 'FINAL_PRE_FORK.json', 'INPUT_RUNTIME_IDENTITY.json',
            'ACTUAL_PRODUCER_BINDING.json', 'ENGINE/START.json', 'ENGINE/FORK_CHILD.json',
            'ENGINE/CHILD.json', 'ENGINE/TERMINAL.json', 'RUN_TERMINAL.json',
            'DISPATCH_JOIN_PENDING.json', 'DISPATCH_EXCEPTION.json', 'STRICT.json',
            'RESOURCE_FINAL.json', 'MAPPING_CLOSURE.json')}
        resource = resource_summary(run / 'RESOURCE_MONITOR.jsonl')
        progress = progress_summary(run / 'PROGRESS.jsonl')
        references['RESOURCE_MONITOR.jsonl'] = resource['source_reference']
        references['PROGRESS.jsonl'] = progress['source_reference']
        record = dict(point=spec['point'], attempt_uuid=spec['attempt_uuid'],
            consumed=True, actual_fork=entry['actual_fork'], accepted=qualified,
            local_destination=str(run), references=references,
            strict_status=None if strict is None else strict.get('status'),
            strict_failure=None if strict is None else strict.get('reason', strict.get('failure')),
            engine_status=None if engine is None else engine.get('status'),
            engine_forced_reason=None if engine is None else engine.get('forced_reason'),
            resource_observation=resource, progress_observation=progress,
            unaccepted_cycles_and_ratios='UNAVAILABLE_NOT_EXTRACTED')
        records.append(record)
        if qualified:
            require(strict['progress_sha256'] == references['PROGRESS.jsonl']['sha256'] and
                    strict['runtime_resource_monitor_sha256'] == references['RESOURCE_MONITOR.jsonl']['sha256'],
                    'ACCEPTED_STRICT_AND_COMPLETED_RAW_HASHES_DO_NOT_JOIN')
            require(strict['attempt_uuid'] == spec['attempt_uuid'] and strict['point'] == spec['point'] and
                type(strict['cycles']) is int and strict['cycles'] > 0 and
                strict['BASE_cycles'] == spec['imported_BASE_cycles'], 'QUALIFIED_CYCLE_BASE_IDENTITY_MISMATCH')
            ratio = Fraction(strict['BASE_cycles'], strict['cycles'])
            accepted_metrics.append(dict(point=spec['point'], attempt_uuid=spec['attempt_uuid'],
                BASE_cycles=strict['BASE_cycles'], cycles=strict['cycles'],
                speedup_exact=dict(numerator=ratio.numerator, denominator=ratio.denominator),
                speedup_decimal=float(ratio), CTA=strict.get('CTA'),
                active_instructions=strict.get('active_instructions'), kernel_count=strict.get('kernel_count'),
                traffic=compact_traffic(strict.get('traffic')), strict_sha256=sha(run / 'STRICT.json')))
    accepted = len(accepted_metrics)
    require(ledger['accepted'] == terminal['accepted'] == accepted, 'FINAL_ACCEPTED_COUNTS_DO_NOT_JOIN')
    require(ledger.get('old_AG6_consumed') == terminal.get('old_AG6_consumed') == 1 and
            ledger.get('old_AG6_three_UUIDs_sealed') is terminal.get('old_AG6_three_UUIDs_sealed') is True and
            ledger.get('BA_original_consumed') == terminal.get('BA_original_consumed') == 0,
            'HISTORICAL_BOUNDARIES_CHANGED')
    complete = actual == accepted == len(entries) == 4 and unknown == 0
    selection = None
    if complete:
        selection = read(ROOT / 'AG7_SELECTION_V1.json')
        require(selection['status'] == 'COMPLETE_FOUR_ARM_AG7_SELECTION' and
                selection['own_UUIDs'] == [s['attempt_uuid'] for s in specs] and
                selection['F'] == ledger['F'] == terminal['F'] and
                terminal['status'] == 'COMPLETE_AG7_STOP', 'COMPLETE_SELECTION_RECEIPTS_DO_NOT_JOIN')
    else:
        require(ledger['F'] is None and terminal['F'] is None, 'INCOMPLETE_COHORT_CANNOT_SELECT_F')
    minimum_blocker = terminal.get('reason')
    for record in records:
        if not record['accepted']:
            minimum_blocker = (record['engine_forced_reason'] or
                ';'.join(record['resource_observation']['stop_reasons']) or
                record['strict_failure'] or minimum_blocker)
            break
    final_jobs = dict(scope='EXACT_PREVIOUSLY_OWNED_CONTROLLER_AND_GUARD_INSTANCES_ONLY',
        observed_at_beijing=datetime.now(timezone(timedelta(hours=8))).isoformat(),
        controller=controller, owned_guard_instances=owned_states,
        active_owned_instances=0, global_foreign_jobs_reaudited=False,
        final_global_authority='RECORDED_CONTROLLER_RESOURCE_RECEIPTS_NOT_NEW_DISPATCH_AUTHORITY')
    snapshot = dict(ledger, status='FINAL_IMMUTABLE_REVIEW_SNAPSHOT',
                    private_ledger_reference=ref(ledger_path), private_ledger_modified_by_finalizer=False)
    cohort = dict({key: value for key, value in terminal.items() if key != 'results'},
        controller_terminal_reference=ref(terminal_path),
        detailed_results_kept_in_local_STRICT_receipts=True,
        publication_status='STOP_AWAITING_UNIFIED_SCIENTIFIC_REVIEW',
        minimum_recorded_blocker=minimum_blocker,
        cohort_complete_four_qualified=complete, accepted_metric_rows=accepted,
        final_owned_jobs=final_jobs, no_background_workflow=True)
    # Compute/verify all input joins above before touching Git artifacts.
    write_json(PACK / 'AG7_BUDGET_LEDGER.json', snapshot)
    write_json(PACK / 'AG7_COHORT_TERMINAL.json', cohort)
    write_json(PACK / 'PER_START_EVIDENCE.json', dict(points=records,
        raw_payloads_copied_to_Git=False, stdout_stderr_maps_trace_or_binary_read=False))
    write_json(PACK / 'ACCEPTED_METRICS.json', dict(accepted=accepted, rows=accepted_metrics,
        incomplete_or_failed_cycles_not_extracted=True, final_selection_valid=complete))
    write_json(PACK / 'FINAL_OWNED_JOBS.json', final_jobs)
    if selection is not None:
        write_json(PACK / 'AG7_SELECTION_V1.json', selection)
    else:
        require(not (PACK / 'AG7_SELECTION_V1.json').exists(), 'STALE_SELECTION_FILE_REQUIRES_ROOT_REVIEW')
    count = str(actual) if unknown == 0 else '>=' + str(actual) + ' (' + str(unknown) + ' unresolved slots)'
    reason = minimum_blocker
    rows = '\n'.join('| ' + r['point'] + ' | ' + str(r['cycles']) + ' | ' +
        str(r['BASE_cycles']) + '/' + str(r['cycles']) + ' |' for r in accepted_metrics)
    metrics_text = ('\n\n| Qualified point | Whole-input cycles | BASE/ON |\n|---|---:|---:|\n' + rows) if rows else ''
    final_text = (selection['F'] + '；四点全部完整合格后按冻结规则选择。') if complete else 'F=null，O仍为临时候选；未完成4/4，不作最终AE/AD选择。'
    report = ('# AG7 Policy B integrated：最终STOP\n\n' +
        ('四点完整合格；结果提交统一科学裁决。' if complete else '在首次实际科学/资源/安全/闭合失败或准入HOLD后停止；未启动点保持封存。') +
        '\n\n原huangrulin-174，BA `/root` 唯一派发。AG7确认实际启动 ' + count + '/4，接受 ' + str(accepted) +
        '/4；消耗槽位 ' + str(len(entries)) + '/4，无重试、替代、免费canary或预算返还。' +
        '\n\n' + final_text + metrics_text +
        '\n\n停止原因：`' + str(reason if reason is not None else 'COMPLETE_FOUR_ACCEPTED_ARMS_STOP') + '`。' +
        '\n\nPolicy B仅显式opt-in，默认OFF。原host全局I/O三资格点保护保留；cgroup压力为有界告警。采样约10秒（最大间隔30秒），进展新鲜度30秒、无退休上限600秒、连续cgroup高压上限1800秒及总期限7200秒均保持预注册值。完成指令来自同线程coherent计数；不以CPU活动、trace消费或日志增长冒充语义进展。' +
        '\n\nCPU协议/producer/guard资格与源、输入、270选项、原Core库及新Framework运行时的比较桥见本包资格/身份/BA决定文件；CPU合成计数不构成模拟科学结果。真实首AE_GEMM已计入正式4次预算。失败点不提取周期或速度。' +
        '\n\n已完成自有精确controller/guard实例只读存活检查：活动自有实例0；没有借此重新授予派发权限或宣称审计全部外部任务。旧AG6仍1/4消耗、0接受、三个UUID封存；BA原0/32独立。原selection/44行/GM12/T7/U2及Hotspot/Btree边界不变。' +
        '\n\n证据入口：[cohort terminal](AG7_COHORT_TERMINAL.json)、[ledger](AG7_BUDGET_LEDGER.json)、[per-start references](PER_START_EVIDENCE.json)、[accepted metrics](ACCEPTED_METRICS.json)。无raw stdout/maps/jsonl/trace/二进制进入Git。远端最终HEAD/tree/blob回读由root在提交后另行记录。\n')
    (PACK / 'LATEST_REPORT.md').write_text(report)
    risks = '''# Risks and scope at final STOP

Policy B remains experimental, default OFF and limited to the frozen four-arm
pilot. The 10/30/600/1800/7200-second bounds are prior engineering safety choices,
not empirically optimal production thresholds. The host/global I/O guard and
bounded cgroup episode are the explicitly accepted conservative surrogate;
retirement is not proof that unrelated shared-cgroup tasks were unharmed.
Per-process I/O, PSI and device counters retain attribution limitations.

Only whole-input, exact-source/input/ROI/options and naturally closed strict
accepted points may supply cycles or BASE/ON ratios. Any missing, stopped,
contradictory or otherwise incomplete point prevents final four-arm selection.
Historical AG3/AG4 executor limitations remain disclosed; their old PASS scope
is not expanded. The new Framework-only observer bridge preserves original
Core-library bytes and source/model transitions under reviewed build/runtime
contracts; it is not formal compiler/libc verification or a native value proof.

Protection covers identity/ownership/authority/mapper, stale or reversed
telemetry, bounded no-retirement and I/O episodes, host/cgroup memory/swap/OOM,
disk/device/output bounds, deadline and unnatural/late contradictory exits.
One completed pilot does not establish general production qualification over
all workloads, long parsing phases, hardware/ISA/coherence or numerical values.
No new primary application GM, formal R/N results or DC hardware area claim.

Final evidence is compact hashes and local references; protected raw files stay
in the independent output root. Remaining work requires scientific review of
the recorded outcome and any explicitly requested further production scope or
new simulation budget. No automatic continuation, restart or reuse of sealed
AG6/AG7 identities is authorized. BA's original32 budget remains separate.
'''
    (PACK / 'RISKS_AND_SCOPE.md').write_text(risks)
    index = []
    for path in sorted(PACK.rglob('*')):
        if not path.is_file() or '__pycache__' in path.parts or path.name in ('FILES_SHA256.tsv', 'PUBLICATION_READBACK.json'):
            continue
        require(not path.is_symlink() and path.stat().st_size <= MAX_JSON,
                'UNEXPECTED_LARGE_OR_SYMLINK_GIT_PAYLOAD')
        require(path.suffix not in ('.jsonl', '.traceg', '.so', '.out', '.pyc'),
                'RAW_PAYLOAD_MUST_NOT_ENTER_REVIEW_PACK')
        index.append(sha(path) + '\t' + str(path.relative_to(PACK)) + '\t' + str(path.stat().st_size))
    (PACK / 'FILES_SHA256.tsv').write_text('sha256\tpath\tbytes\n' + '\n'.join(index) + '\n')
    print(json.dumps(dict(status='COMPACT_FINAL_REVIEW_PACK_WRITTEN_NOT_PUBLISHED',
        confirmed_actual_starts=actual, unresolved_fork_slots=unknown, accepted=accepted,
        F=terminal['F'], raw_payloads_copied=0, helper_simulator_starts=0,
        active_owned_instances=0, root_must_publish_and_read_back_exact_remote_HEAD=True)))


if __name__ == '__main__':
    main()
