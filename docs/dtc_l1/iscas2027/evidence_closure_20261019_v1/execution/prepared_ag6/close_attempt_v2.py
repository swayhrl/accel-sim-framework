"""PREPARED_NOT_EXECUTED. Close one own canonical guard's actual evidence.

The production caller has already independently verified its immutable source,
capability, registration, complete input/runtime identity and actual execution.
This module joins the actual files, event ancestry and scientific bytes. It
does not turn arbitrary claimed JSON identities into execution permission.
"""
import hashlib
import json
from pathlib import Path
import re

from ag6_strict import parse_attempt

HERE = Path(__file__).resolve().parent
EXECUTION = HERE.parent


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(65536), b''):
            digest.update(block)
    return digest.hexdigest()


def close_mapping(engine, mappings):
    root = json.loads((engine / 'CHILD.json').read_text())
    fork = json.loads((engine / 'FORK_CHILD.json').read_text())
    terminal = json.loads((engine / 'TERMINAL.json').read_text())
    start = json.loads((engine / 'START.json').read_text())
    require(fork['pid'] == root['pid'] == terminal['root_pid'] and
            fork['fork_monotonic_ns'] == root['fork_monotonic_ns'] and
            root['actual_fork'] is True and root['real_simulator'] is True,
            'ACTUAL_DIRECT_FORK_ROOT_RECEIPT_JOIN')
    expected_manifests = {path: hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()
                          for path, value in mappings.items()}
    require(start['purpose'] == 'SIMULATION' and start['manifests_sha'] == expected_manifests,
            'ACTUAL_GUARD_MANIFEST_SOURCE_JOIN')
    root_key = (root['pid'], root['start_ticks'])
    proven = {root_key}
    current = {root['pid']: root_key}
    map_rows = {}
    image_rows = []
    last_closed_image = {}
    inherited_image = {}
    proof_count = 0
    event_digest = hashlib.sha256()
    events = engine / 'MAP_EVENTS.jsonl'
    with events.open('rb') as stream:
        for line in stream:
            event_digest.update(line)
            row = json.loads(line)
            if row.get('proof') == 'PTRACE_GETEVENTMSG_FROM_CONFIRMED_PARENT':
                parent = (row['parent_pid'], row['parent_start_ticks'])
                child = (row['new_owned_pid'], row['child_start_ticks'])
                require(parent in proven and row['event'] in (1, 2, 3),
                        'CURRENT_EVENT_CONFIRMED_PARENT_ANCESTRY')
                require(child not in proven, 'DUPLICATE_CHILD_INSTANCE_PROOF')
                proven.add(child)
                current[child[0]] = child
                inherited_image[child] = last_closed_image.get(parent)
                proof_count += 1
            if 'maps' in row:
                require(row['pid'] in current and row['exe'] in mappings,
                        'MAP_NOT_EVENT_PROVEN_REGISTERED_IMAGE')
                name = row['maps']
                require(re.fullmatch(r'[0-9]{6}_pid[0-9]+\.maps', name) is not None,
                        'GUARD_MAP_FILE_NAME_CHANGED')
                path = engine / 'maps' / name
                require(name not in map_rows and sha(path) == row['maps_sha256'],
                        'ACTUAL_CLOSED_MAP_PAYLOAD_CHANGED')
                map_rows[name] = dict(sha256=row['maps_sha256'], bytes=path.stat().st_size,
                    instance=list(current[row['pid']]), image=row['exe'])
                image_rows.append(dict(instance=list(current[row['pid']]), image=row['exe'],
                    stage=row['stage'], cache_present=row['cache_present'],
                    removed_files=row['removed_files'], startup_closed=row['startup_closed']))
                if row['startup_closed']:
                    last_closed_image[current[row['pid']]] = row['exe']
    exits = terminal['owned_process_exit_instances']
    exit_keys = {(row['pid'], row['start_ticks']) for row in exits}
    retired = {(row['pid'], row['start_ticks']) for row in terminal['ownership']['retired']}
    require(len(exit_keys) == len(exits) and proven == exit_keys == retired and
            all(row['returncode'] == 0 for row in exits), 'PROVEN_INSTANCE_EXIT_RETIREMENT_JOIN')
    require(not terminal['ownership']['confirmed'] and not terminal['ownership']['pending'] and
            terminal['owned_children_live'] == 0 and not terminal['unconfirmed_wait_pids'],
            'ACTUAL_CURRENT_OWNERSHIP_NOT_DRAINED')
    require(len(map_rows) == terminal['snapshots'] and
            set(map_rows) == {p.name for p in (engine / 'maps').iterdir()},
            'COMPLETE_ACTUAL_MAP_PAYLOAD_POPULATION')
    for instance, image in {(tuple(r['instance']), r['image']) for r in image_rows}:
        rows = [r for r in image_rows if tuple(r['instance']) == instance and r['image'] == image]
        independently_loaded = (any(r['cache_present'] for r in rows) and
                                any('/etc/ld.so.cache' in r['removed_files'] for r in rows))
        inherited = (inherited_image.get(instance) == image and any(
            r['stage'] == 'INHERITED_FORK_CLONE_STOP' and r['startup_closed'] for r in rows))
        require((independently_loaded or inherited) and any(r['startup_closed'] for r in rows),
                'EARLY_CACHE_APPEAR_UNMAP_OR_ACTUAL_PARENT_INHERITANCE_REQUIRED')
    return dict(status='PASS_ACTUAL_CLOSED_GUARD_EVENT_MAPPING_EXIT_JOIN',
        root_instance=list(root_key), event_proofs=proof_count, exit_instances=len(exits),
        map_payloads=len(map_rows), map_payload_bytes=sum(r['bytes'] for r in map_rows.values()),
        map_events_sha256=event_digest.hexdigest(), map_payload_index=map_rows,
        observed_kernel_PID_reuse='NOT_INFERRED_FROM_SYNTHETIC_CPU_CASES',
        per_resume_generation_log='UNAVAILABLE_GUARD_SOURCE_ENFORCES_CURRENT_INSTANCE_EACH_RESUME')


def collect(run, point, *, manifest, publication_head, identity_receipt):
    run = Path(run)
    start = json.loads((run / 'RUN_START.json').read_text())
    require(start['publication_head'] == publication_head and
            start['point'] == identity_receipt['point'] == point['point'] and
            start['attempt_uuid'] == identity_receipt['attempt_uuid'] == point['attempt_uuid'] and
            start['argv'] == identity_receipt['validated_argv'], 'ACTUAL_START_IDENTITY_PUBLICATION_JOIN')
    require(identity_receipt['status'] == 'PASS_PRELAUNCH_IDENTITY_ONLY' and
            identity_receipt['binding_sha256'] == manifest['identity_contract_sha256'],
            'CURRENT_FROZEN_INPUT_RUNTIME_CONFIG_IDENTITY_REQUIRED')
    engine = run / 'ENGINE'
    engine_start = json.loads((engine / 'START.json').read_text())
    require(engine_start['argv'] == start['argv'] and
            engine_start['environment'] == identity_receipt['validated_environment'],
            'ACTUAL_EXECUTION_ARGV_ENVIRONMENT_JOIN')
    mapping_path = Path(manifest['mapping_manifest_path'])
    require(sha(mapping_path) == manifest['mapping_manifest_sha256'], 'FROZEN_MAPPING_CHANGED')
    mapping_receipt = close_mapping(engine, json.loads(mapping_path.read_text()))
    with (run / 'MAPPING_CLOSURE.json').open('x') as stream:
        stream.write(json.dumps(mapping_receipt, indent=2) + '\n')
    final_resource = json.loads((run / 'RESOURCE_FINAL.json').read_text())
    require(final_resource['decision']['decision'] != 'STOP' and
            final_resource['authority']['status'] == 'PASS_CURRENT_NO_OTHER_DTC_DISPATCH_AUTHORITY',
            'ACTUAL_FINAL_RESOURCE_AND_AUTHORITY_REQUIRED')
    monitor_sha = sha(run / 'RESOURCE_MONITOR.jsonl')
    samples = 0
    with (run / 'RESOURCE_MONITOR.jsonl').open() as stream:
        for line in stream:
            row = json.loads(line)
            require(row['decision']['decision'] != 'STOP' and row['authority']['status'] in
                ('PASS_CURRENT_NO_OTHER_DTC_DISPATCH_AUTHORITY', 'PENDING_QUARANTINED_NO_AUTHORITY_PASS'),
                'ACTUAL_RUNTIME_RESOURCE_OR_GLOBAL_AUTHORITY_FAILED')
            samples += 1
    require(samples > 0, 'ACTUAL_RUNTIME_OBSERVATION_REQUIRED')
    report = parse_attempt(point['point'],
        stdout=(engine / 'stdout').read_bytes(), stderr=(engine / 'stderr').read_bytes(),
        run_start=(run / 'RUN_START.json').read_bytes(),
        run_terminal=(run / 'RUN_TERMINAL.json').read_bytes(),
        engine_terminal=(engine / 'TERMINAL.json').read_bytes(),
        preregistration=(EXECUTION / 'AG6_FOUR_POINT_IDENTITY_PREREGISTRATION_V2.json').read_bytes(),
        science_manifest=(EXECUTION / 'ag6_final_prep_intake/AG6_FOUR_ARM_SCIENCE_PROPOSAL.json').read_bytes(),
        kernel_audit=(HERE / 'identity_metadata/KERNEL_BODY_AUDIT.tsv').read_bytes(),
        metric_dictionary=(EXECUTION / 'ag6_final_prep_intake/FROZEN_METRIC_DICTIONARY.tsv').read_bytes())
    if report['scientific_strict_pass']:
        report.update(status='PASS_ACTUAL_REGISTERED_AG6_FULL_STRICT_EVIDENCE',
            performance_accepted=True, acceptance_scope='ACTUAL_OWN_SOURCE_BOUND_REGISTERED_ATTEMPT',
            publication_head=publication_head, input_runtime_identity_sha256=sha(run / 'INPUT_RUNTIME_IDENTITY.json'),
            mapping_closure_sha256=sha(run / 'MAPPING_CLOSURE.json'),
            runtime_resource_monitor_sha256=monitor_sha,
            final_resource_sha256=sha(run / 'RESOURCE_FINAL.json'),
            resource_samples=samples, BASE_cycles=point['imported_BASE_cycles'],
            speedup_exact=dict(numerator=point['imported_BASE_cycles'], denominator=report['cycles']))
    return report
