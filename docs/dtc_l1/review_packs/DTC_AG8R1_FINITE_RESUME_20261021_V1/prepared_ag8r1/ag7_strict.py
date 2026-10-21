"""Pure AG7 registration adapter over all original AG6 scientific validators.

The caller supplies the SHA-frozen original pure parser module and exact bytes.
Old frozen_inputs is called unchanged against its original provenance. Only
explicit AG7 UUID/runtime/observational metadata is substituted in a separate
specification; no original function/global constant is patched or skipped.
"""
import copy
import hashlib
import re
import uuid
from wall_contract_guard import guard_contract as wall_guard_contract

ORDER = ('AD_GEMM', 'AD_Gaussian')
NEW_RUNTIME = '/workspace/dtc-ag7-policyb-integrated-174-v1/build/accel-sim.out'
NEW_RUNTIME_SHA = '1004880fd7f01f815eb55d3e23fee451d95bb90eef7ecfb19ec8fd9531b9bd6c'
OBS_KEYS = frozenset(('DTC_AG7_POLICY_B_PROGRESS', 'DTC_AG7_GENERATION',
                     'DTC_AG7_INPUT_SHA', 'DTC_AG7_ROI_SHA'))
ALLOWED_FIELDS = frozenset(('attempt_uuid', 'new_attempt_uuid', 'cohort',
    'runtime_path', 'runtime_sha256', 'runtime_environment', 'expected_embedded_framework_version',
    'destination', 'resource_policy_version', 'status', 'BASE_eligibility_decision_sha256', 'order', 'timeout_seconds'))
POLICY_VERSION = 'AG8R1_USER_IO_WARNING_FRESH30_NO_RETIRE600_WALL21600_V2'
REGISTRATION_STATUS = 'RESERVED_AG8R1_NOT_EXECUTABLE_WITHOUT_CURRENT_C2_R2'


def frozen_inputs(legacy, point, *, registration, registration_sha256,
                  old_preregistration, science_manifest, kernel_audit,
                  metric_dictionary, expected_framework_version, expected_base_decision_sha256):
    legacy.require(hashlib.sha256(registration).hexdigest() == registration_sha256,
                   'FROZEN_AG7_REGISTRATION_CHANGED')
    original, expected, dictionary = legacy.frozen_inputs(point, old_preregistration,
        science_manifest, kernel_audit, metric_dictionary)
    old = legacy.json_bytes(old_preregistration)
    manifest = legacy.json_bytes(registration)
    points = manifest['points']
    legacy.require(tuple(p['point'] for p in points) == ORDER and
        manifest['maximum_new_starts'] == 2 and manifest['maximum_simultaneous_simulators'] == 1,
        'EXACT_AG7_ORDER_FOUR_START_SINGLE_ROOT')
    old_ids = {p['attempt_uuid'] for p in old['ordered_points']} | {p['attempt_uuid'] for p in __import__('json').loads((__import__('pathlib').Path(__file__).resolve().parents[2] / 'DTC_AG7_POLICYB_INTEGRATED_20261020_V1/AG7_FOUR_POINT_MANIFEST.json').read_text())['points']}
    ids = [p['attempt_uuid'] for p in points]
    legacy.require(len(set(ids)) == 2 and not set(ids) & old_ids,
                   'NEW_AG7_UUIDS_REQUIRED_OLD_AG6_SEALED')
    for attempt in ids:
        legacy.require(str(uuid.UUID(attempt)) == attempt, 'INVALID_REGISTERED_UUID')
    new = next(p for p in points if p['point'] == point)
    legacy.require(new['new_attempt_uuid'] == new['attempt_uuid'] and
        new['cohort'] == 'AG8R1_FINITE_RESOURCE_CONTINUATION', 'EXACT_NEW_AG7_POINT_IDENTITY')
    legacy.require(new['destination'] == '/workspace/dtc-ag8r1-finite-resume-174-v1/attempts/' +
        point + '_' + new['attempt_uuid'] and new['resource_policy_version'] == POLICY_VERSION and
        new['status'] == REGISTRATION_STATUS and new['order'] == ORDER.index(point) and
        new['timeout_seconds'] == 21600, 'EXACT_AD8_DESTINATION_PROFILE_WALL_REGISTRATION_STATE')
    legacy.require(re.fullmatch('[0-9a-f]{64}', expected_base_decision_sha256) is not None and
        new['BASE_eligibility_decision_sha256'] == expected_base_decision_sha256,
        'EXACT_NEW_SCOPED_BASE_DECISION_REQUIRED')
    legacy.require(all(key in new and new[key] == value
        for key, value in original.items() if key not in ALLOWED_FIELDS),
        'ORIGINAL_WHOLE_SCIENCE_FIELD_CHANGED')
    legacy.require(new['runtime_path'] == NEW_RUNTIME and new['runtime_sha256'] == NEW_RUNTIME_SHA,
                   'EXACT_AUDITED_AG7_FRAMEWORK_BUILD_REQUIRED')
    legacy.require(isinstance(expected_framework_version, str) and expected_framework_version and
        new['expected_embedded_framework_version'] == expected_framework_version,
        'FRAMEWORK_EMBEDDED_VERSION_NOT_BOUND_TO_CURRENT_IDENTITY')
    env = new['runtime_environment']
    legacy.require(set(env) == set(original['runtime_environment']) | OBS_KEYS and
        all(env[k] == v for k, v in original['runtime_environment'].items()) and
        env['DTC_AG7_POLICY_B_PROGRESS'] == '1', 'EXACT_ORIGINAL_ENV_PLUS_OBSERVATIONAL_OPT_IN')
    for key in ('DTC_AG7_INPUT_SHA', 'DTC_AG7_ROI_SHA'):
        legacy.require(re.fullmatch('[0-9a-f]{64}', env[key]) is not None,
                       'EXACT_REGISTERED_INPUT_ROI_DIGEST')
    legacy.require(re.fullmatch('[A-Za-z0-9_.:-]{1,64}', env['DTC_AG7_GENERATION']) is not None,
                   'EXACT_REGISTERED_GENERATION')
    return copy.deepcopy(new), expected, dictionary


def parse_attempt(legacy, point, *, stdout, stderr, run_start, run_terminal,
                  engine_terminal, registration, registration_sha256,
                  old_preregistration, science_manifest, kernel_audit,
                  metric_dictionary, expected_framework_version, expected_base_decision_sha256):
    """Every original scientific/terminal check remains mandatory; no dispatch."""
    unavailable = legacy.UNAVAILABLE
    report = dict(point=point, status='HOLD_AG7_STRICT_FAILED', scientific_strict_pass=False,
        performance_accepted=False, cycles=unavailable,
        acceptance_scope='SUPPLIED_BYTES_SCIENTIFIC_CHECKS_ONLY',
        parent_identity_authority_resource_closure_required=True,
        no_dispatch_or_retry_permission=True,
        common_metric_scope='LAST_CUMULATIVE_FINAL_SNAPSHOT_NOT_SUM_OF_KERNEL_SNAPSHOTS')
    try:
        spec, expected, dictionary = frozen_inputs(legacy, point, registration=registration,
            registration_sha256=registration_sha256, old_preregistration=old_preregistration,
            science_manifest=science_manifest, kernel_audit=kernel_audit,
            metric_dictionary=metric_dictionary, expected_framework_version=expected_framework_version,
            expected_base_decision_sha256=expected_base_decision_sha256)
        report.update(attempt_uuid=spec['attempt_uuid'], arm=spec['arm'], workload=spec['workload'])
        start = legacy.json_bytes(run_start)
        legacy.require(start['attempt_uuid'] == spec['attempt_uuid'] and start['point'] == point,
                       'FOREIGN_START_CANNOT_CONSUME_THIS_RESERVATION')
        report['budget_observation'] = dict(reserved_start_slots=1,
            actual_fork_children_from_guard=unavailable,
            actual_fork_count_definition='ROOT_PID_PROVES_ONE_DIRECT_FORK_ELSE_ONLY_EXPLICIT_GUARD_FIELD',
            failed_or_partial_start_refunded=False, new_simulations_launched_by_parser=0)
        report['receipt_sha256'] = dict(stdout=legacy.digest(stdout), stderr=legacy.digest(stderr),
            RUN_START=legacy.digest(run_start), RUN_TERMINAL=legacy.digest(run_terminal),
            ENGINE_TERMINAL=legacy.digest(engine_terminal))
        terminal, engine = legacy.json_bytes(run_terminal), legacy.json_bytes(engine_terminal)
        fork_field = engine.get('actual_fork_children')
        actual_children = (1 if type(engine.get('root_pid')) is int and engine['root_pid'] > 0
            else fork_field if type(fork_field) is int and fork_field in (0, 1) else unavailable)
        report['budget_observation']['actual_fork_children_from_guard'] = actual_children
        guard = wall_guard_contract(start, terminal, engine, spec)
        text = legacy.decoded(stdout)
        legacy.require(not re.search(legacy.FORBIDDEN, legacy.decoded(stderr), re.I),
                       'forbidden_stderr_runtime_signature')
        legacy.require(spec['expected_embedded_core_version'] in text, 'actual_Core_embedded_version')
        legacy.require(spec['expected_embedded_framework_version'] in text, 'actual_Framework_embedded_version')
        parsed = legacy.parse_full(text, spec, expected)
        options = parsed['effective_options']
        legacy.require(len(options) == 270 and options == spec['expected_full_effective_options'],
                       'all_270_effective_options_exact_population_and_values')
        fixed = {'mode': '3', 'invalidate_on_source_event': '0', 'finite_service': '1',
            'oo_pib_entries': '128', 'logical_sets': '64', 'logical_ways': '8',
            'physical_lines': '640', 'allocation_width': '4',
            'tag_hash_bankrow': '1' if spec['arm'] == 'AE' else '0',
            'progressive_wakeup': '1' if spec['arm'] == 'AD' else '0'}
        legacy.require(all(options['-gpgpu_dtc_l1_' + key] == [value] for key, value in fixed.items()),
                       'K0_OO128_64x8_640_AE_ONLY_OR_AD_ONLY')
        pipeline = legacy.pipeline_contract(text, spec['arm'], parsed['final_metrics'])
        report.update(status='PASS_AG7_SUPPLIED_BYTES_SCIENTIFIC_STRICT_ONLY', scientific_strict_pass=True,
            cycles=parsed['cycles'], CTA=parsed['CTA'], active_instructions=parsed['active_instructions'],
            kernels=parsed['kernels'], kernel_count=parsed['kernel_count'],
            final_metrics=parsed['final_metrics'], traffic=parsed['traffic'], effective_options=options,
            guard_terminal_check=guard, AD_diagnostic=pipeline,
            typed_statistics=legacy.typed_statistics(parsed['final_metrics'], parsed['traffic'], pipeline, dictionary),
            K1_only_fields='UNAVAILABLE_K0_NOT_PRINTED', numeric_load_values='UNAVAILABLE',
            actual_collection_WB_overlap='UNAVAILABLE_NO_DIRECT_COUNTER',
            private_terminal_generation_sector_receipts='UNAVAILABLE')
    except (ValueError, KeyError, TypeError, IndexError, StopIteration) as error:
        report['failure'] = type(error).__name__ + ':' + str(error)
    return report
