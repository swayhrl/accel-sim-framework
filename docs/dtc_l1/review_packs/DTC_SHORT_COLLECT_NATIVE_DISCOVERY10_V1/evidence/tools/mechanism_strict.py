"""Pure Short Collect closed-result verifier. No registry, launcher, or model API.

The caller must supply a frozen, independently admitted spec and the exact
registered intent/receipt. The historical whole-input population checker is
reused with only its 270 -> 271 option count assertion changed.
"""
import gzip
import hashlib
import json
import re
import types
from pathlib import Path

ROOT = Path('/root/data/dtc_short_collect_native_discovery10_v1_20261109')
REGISTRY = Path('/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json')
EPOCH = Path('/root/data/ep_l2_dtc_l1_native_v2/control/CURRENT_SCIENCE_EPOCH.json')

OLD_POP = Path('/root/data/dtc_main_v100_sweep_20261025_v1/tools/sweep_strict_cap1m.py')
OLD_POP_SHA = '87ee4025dce16a909a30c9e94a10dcaad14d3e71b3846371edd3be15a9b0bac5'
OLD_LEGACY = Path('/root/data/ep_l2_dtc_l1_native_v2/DTC/src/owner-control/docs/dtc_l1/iscas2027/evidence_closure_20261019_v1/execution/prepared_ag6/ag6_strict.py')
OLD_LEGACY_SHA = '9039c1d0df66210ad9c8fba325bc5e6d9ae10bd67981d7668c18a4576b81b3e4'
SWITCH = '-gpgpu_dtc_l1_short_collect_first'
COUNTER = re.compile(r'^DTC_SHORT_COLLECT_V1 enabled=([01]) choice_decision_different=(\d+) eligible_choice_different=(\d+)\s*$', re.M)


def need(ok, code):
    if not ok:
        raise ValueError(code)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_bytes())


def registered_join(spec, intent, done, *, registry=REGISTRY, epoch=EPOCH, root=ROOT):
    """Frozen spec, one-use ledger, and global authority join; pure read-only."""
    root, registry, epoch = Path(root), Path(registry), Path(epoch)
    spec_path = root / 'control/specs' / (spec['cohort'] + '.json')
    need(sha(spec_path) == intent['spec_sha256'] and read(spec_path) == spec,
         'FROZEN_REGISTERED_SPEC_SHA')
    current = read(epoch)
    need(sha(registry) == current['native_registry_sha256'], 'REGISTRY_EPOCH_SHA')
    request = read(registry)['registered_future_requests'][spec['request']]
    need(request['admitted_specs'][spec['cohort']] == sha(spec_path), 'REGISTRY_SPEC_SHA')
    consumed = request['consumed'][spec['cohort']]
    intent_path = root / 'control/qualification_ledger' / (spec['cohort'] + '.INTENT.json')
    done_path = root / 'control/qualification_ledger' / (spec['cohort'] + '.DONE.json')
    receipt = consumed['execution_receipt']
    need(read(intent_path) == intent and read(done_path) == done and
         consumed['intent_sha256'] == sha(intent_path) and
         consumed['uuid'] == intent['uuid'] and
         receipt['path'] == str(done_path) and receipt['sha256'] == sha(done_path),
         'REGISTRY_LEDGER_CLOSED_JOIN')
    return dict(registry_sha256=sha(registry),spec_sha256=sha(spec_path),
                intent_sha256=sha(intent_path),done_sha256=sha(done_path))


def mechanism_counters(raw, mode, expected_kernels):
    need(mode in ('OFF', 'ON'), 'MODE_SCOPE')
    blocks = list(re.finditer(r'^kernel_name = (\S+)[ \t]*$', raw, re.M))
    need(len(blocks) == expected_kernels and expected_kernels > 0, 'KERNEL_COUNT')
    rows = []
    for index, match in enumerate(blocks):
        block = raw[match.start():blocks[index + 1].start() if index + 1 < len(blocks) else len(raw)]
        matches = COUNTER.findall(block)
        need(len(matches) == 1, 'MECHANISM_COUNTER_ONE_PER_KERNEL')
        enabled, different, eligible = map(int, matches[0])
        need(enabled == (mode == 'ON'), 'MECHANISM_MODE_ECHO')
        need(0 <= eligible <= different, 'MECHANISM_COUNTER_ORDER')
        need(mode == 'ON' or (different == 0 and eligible == 0), 'OFF_MECHANISM_EXPOSURE')
        rows.append(dict(kernel=match.group(1), choice_decision_different=different,
                         eligible_choice_different=eligible))
    return rows


def classify_closed_failure(intent, done, output):
    """Preserve a consumed negative without fabricating process or cycles."""
    output = Path(output)
    need(intent['request'] == done['request'] and
         intent['cohort'] == done['cohort'] and
         intent['uuid'] == done['uuid'] and intent['output'] == str(output),
         'NEGATIVE_IDENTITY_JOIN')
    need(read(output / 'NATIVE_EXIT.json') == done and
         done['new_attempt_consumed'] == 1 and done['automatic_retry'] is False,
         'NEGATIVE_ONE_USE_EXIT_JOIN')
    need(done['stop_reason'] is not None or done['launcher_wait_returncode'] != 0 or
         done['native_simulator_observed'] is False, 'NEGATIVE_REQUIRES_ACTUAL_FAILURE')
    pid_path = output / 'NATIVE_SIMULATOR_PID_AND_MAPS.json'
    if not done['native_simulator_observed']:
        need(not pid_path.exists(), 'BEFORE_PID_MUST_NOT_SYNTHESIZE_PID')
    if (output / 'raw.log.gz').exists():
        need(sha(output / 'raw.log.gz') == done['raw_sha256'], 'NEGATIVE_RAW_SHA')
    return dict(schema='DTC_SHORT_COLLECT_NATIVE_NEGATIVE_V1',
                status='STOP_UNACCEPTED_NO_RETRY', request=intent['request'],
                cohort=intent['cohort'], uuid=intent['uuid'],
                failure_class=('BEFORE_NATIVE_PID' if not done['native_simulator_observed']
                               else 'OBSERVED_NATIVE_STOP_OR_NONZERO'),
                stop_reason=done['stop_reason'], returncode=done['launcher_wait_returncode'],
                accepted_cycles=None, performance_accepted=False, SOURCE_KEEP=True)


def _population(raw, spec, domain):
    need(sha(OLD_POP) == OLD_POP_SHA and sha(OLD_LEGACY) == OLD_LEGACY_SHA,
         'PINNED_WHOLE_INPUT_CHECKER_DRIFT')
    source = OLD_POP.read_text()
    anchor = "len(s['expected_options'])==270"
    need(source.count(anchor) == 1, 'POPULATION_ANCHOR_COUNT')
    transformed = source.replace(anchor, "len(s['expected_options'])==271", 1)
    need(transformed.replace("len(s['expected_options'])==271", anchor, 1) == source,
         'POPULATION_TRANSFORM_NOT_EXACT')
    module = types.ModuleType('short_collect_pinned_population')
    module.__file__ = str(OLD_POP)
    exec(compile(transformed, str(OLD_POP) + ':SHORT_COLLECT_271', 'exec'), module.__dict__)
    legacy = types.ModuleType('short_collect_unchanged_legacy')
    legacy.__file__ = str(OLD_LEGACY)
    exec(compile(OLD_LEGACY.read_bytes(), str(OLD_LEGACY), 'exec'), legacy.__dict__)
    return module.population(raw, spec, domain, legacy), hashlib.sha256(transformed.encode()).hexdigest()


def closed(spec, intent, done, output, domain, *, full_population=True):
    """Verify one new registered native result. Never accepts an old Oracle identity."""
    output = Path(output)
    need(spec['request'] == intent['request'] == done['request'], 'REQUEST_JOIN')
    need(spec['cohort'] == intent['cohort'] == done['cohort'], 'COHORT_JOIN')
    need(sha(spec['input_binding_path']) == spec['input_binding_sha256'], 'INPUT_BINDING_SHA')
    binding = read(spec['input_binding_path'])
    need(binding['qualification'] == domain, 'INPUT_DOMAIN_EXACT_JOIN')
    need(binding['input_digest'] == domain['input_digest'] == spec['input_digest'],
         'INPUT_DIGEST_BINDING')
    if full_population:
        registered_join(spec, intent, done)
    need(not spec['cohort'].startswith('E2-DTCORACLE-'), 'OLD_ORACLE_IDENTITY')
    need(intent['uuid'] == done['uuid'] and intent['output'] == str(output), 'UUID_OUTPUT_JOIN')
    need(intent['automatic_retry'] is False and intent['consumed_before_launcher_fork'] == 1,
         'ONE_USE_CHARGED_IDENTITY')
    need(read(output / 'NATIVE_EXIT.json') == done, 'NATIVE_EXIT_JOIN')
    need(done['stop_reason'] is None and done['launcher_wait_returncode'] == 0 and
         done['native_simulator_observed'] is True, 'NATURAL_NATIVE_EXIT')
    need(sha(output / 'raw.log.gz') == done['raw_sha256'], 'CLOSED_GZIP_SHA')
    raw_bytes = gzip.decompress((output / 'raw.log.gz').read_bytes())
    need(hashlib.sha256(raw_bytes).hexdigest() == done['raw_uncompressed_sha256'] and
         len(raw_bytes) == done['raw_uncompressed_bytes'], 'CLOSED_RAW_SHA')
    raw = raw_bytes.decode('utf-8')
    launch, pid = read(output / 'NATIVE_LAUNCH.json'), read(output / 'NATIVE_SIMULATOR_PID_AND_MAPS.json')
    need(launch['scientific_qualification_uuid'] == pid['uuid'] == intent['uuid'], 'ACTUAL_PROCESS_UUID')
    if full_population:
        need(launch['spec_sha256'] == intent['spec_sha256'], 'LAUNCH_FROZEN_SPEC_SHA')
    need(launch['argv'][-len(spec['native_simulator_argv']):] == spec['native_simulator_argv'], 'ACTUAL_ARGV')
    need(spec['native_simulator_argv'][0] in pid['maps'], 'ACTUAL_BINARY_MAP')
    need(pid['mnt_namespace'] == spec['execution_mnt_namespace'], 'ACTUAL_MOUNT_NAMESPACE')
    if full_population:
        late = read(output / 'NATIVE_SIMULATOR_VERIFIED_LATE_MAPS.json')
        need((late['pid'],late['start_ticks'],late['mnt_namespace']) ==
             (pid['pid'],pid['start_ticks'],pid['mnt_namespace']), 'ACTUAL_LATE_MAP_IDENTITY')
        need(late['maps'] == pid['maps'] or all(path in late['maps'] for path in
             [spec['binary_path'], spec['libcudart_path'], spec['loader_path']]),
             'ACTUAL_LATE_MAP_RUNTIME')
    binding_path = spec['runtime_binding_path']
    need(sha(binding_path) == spec['runtime_sha256'], 'RUNTIME_BINDING_SHA')
    binding = read(binding_path)
    files = binding.get('runtime_files', binding.get('files'))
    need(isinstance(files, list) and files, 'RUNTIME_BINDING_FILES')
    for row in files:
        path = row.get('actual_realpath', row.get('realpath', row.get('path')))
        need(path is not None and sha(path) == row['sha256'], 'RUNTIME_FILE_SHA')
        if row.get('role') != 'strace':
            need(path in pid['maps'], 'ACTUAL_MAPPED_RUNTIME')
    need(sha(spec['binary_path']) == spec['binary_sha256'], 'FROZEN_BINARY_SHA')
    need(spec['binary_path'] in pid['maps'], 'FROZEN_BINARY_ACTUAL_MAP')
    need(spec['core_commit'][:7] in raw and spec['framework_commit'] in raw, 'SOURCE_ECHO')
    need(len(spec['expected_options']) == 271 and spec['expected_options'][SWITCH] ==
         ['1' if spec['mode'] == 'ON' else '0'], 'EXACT_NEW_OPTION')
    rows = mechanism_counters(raw, spec['mode'], spec['expected']['kernels'])
    progress = []
    with gzip.open(output / 'progress.jsonl.gz', 'rt') as stream:
        for line in stream:
            item = json.loads(line)
            need(item['seq'] == len(progress) + 1 and
                 (item['pid'], item['start_ticks'], item['generation']) ==
                 (pid['pid'], pid['start_ticks'], intent['uuid']), 'PROGRESS_PROCESS_GENERATION')
            need(item['input'] == spec['original_environment']['DTC_AG7_INPUT_SHA'] and
                 item['roi'] == spec['original_environment']['DTC_AG7_ROI_SHA'], 'PROGRESS_INPUT_ROI')
            if progress:
                need(item['mono_ns'] > progress[-1]['mono_ns'] and
                     item['completed'] >= progress[-1]['completed'], 'PROGRESS_MONOTONIC')
            progress.append(item)
    need(progress and progress[-1]['end'] == 'NATURAL' and
         progress[-1]['completed'] == spec['expected']['instructions'], 'FULL_NATURAL_PROGRESS')
    result = None
    transformed_sha = None
    if full_population:
        result, transformed_sha = _population(raw, spec, domain)
        need(result['instructions'] == spec['expected']['instructions'] and
             result['CTA'] == spec['expected']['CTA'] and
             result['kernel_count'] == spec['expected']['kernels'], 'WHOLE_INPUT_COUNTS')
        trace = (output / 'actual_file_process_network.log').read_text()
        need('connect(' not in trace and '"/usr/bin/ssh"' not in trace and
             '"/bin/ssh"' not in trace, 'NO_SCIENCE_NETWORK')
        need(all(row['path'] in trace for row in domain['rows']), 'ALL_INPUT_MEMBERS_READ')
        resources = 0
        guard_sha = sha(ROOT / 'tools/route_guard.py')
        preflight_sha = sha(output / 'PRE_FORK_ADMISSION.json')
        with gzip.open(output / 'RESOURCE_SAMPLES.jsonl.gz', 'rt') as stream:
            for line in stream:
                item = json.loads(line)
                need((item['pid'],item['start_ticks'],item['uuid'],item['cohort']) ==
                     (pid['pid'],pid['start_ticks'],intent['uuid'],intent['cohort']),
                     'RUNTIME_SAMPLE_PROCESS_GENERATION')
                need(item['guard_sha256'] == guard_sha and
                     item['preflight_sha256'] == preflight_sha, 'RUNTIME_GUARD_SOURCE_PIN')
                need(item['status'] == 'PASS' and not item['stop_reasons'] and
                     item['physical_RAM_pass'] and item['physical_disk_pass'] and
                     item['process_tree_observed_rss_bytes'] <=
                     spec['limits']['max_process_tree_rss_bytes'], 'RUNTIME_RESOURCE_FAIL')
                resources += 1
        need(resources > 0, 'RUNTIME_GUARD_SAMPLES_MISSING')
    return dict(schema='DTC_SHORT_COLLECT_NATIVE_STRICT_V1',
                status='NATURAL_STRICT_ACCEPTED' if full_population else 'CPU_SYNTHETIC_ONLY',
                request=intent['request'], cohort=intent['cohort'], uuid=intent['uuid'],
                mode=spec['mode'], program=spec['program'], raw_sha256=done['raw_sha256'],
                cycles=None if result is None else result['cycles'], full_population=result,
                population_transform_sha256=transformed_sha, mechanism_counters=rows,
                eligible_choice_different=sum(row['eligible_choice_different'] for row in rows),
                SOURCE_KEEP=True, numerical_values='UNPROVEN')
