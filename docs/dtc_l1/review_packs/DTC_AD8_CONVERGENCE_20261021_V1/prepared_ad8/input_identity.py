"""Pure AG7 identity joins; caller authenticates the small input manifests.

No IO, model/trace read, UUID generation, budget mutation, authority or launch.
Old AG6 receipt identifiers are provenance only and never returned as AG7 IDs.
These joins supplement current original Reader/input/source/runtime checks.
"""
import copy
import hashlib
import json

CORE = 'c8090115bd57512b1b23fca7d925301fa620c751'
ORIGINAL_FRAMEWORK = '8e43c75a5e2eb60a8466084602b7df8117111e89'
OLD_RUNTIME = '/workspace/dtc-lane-ag3-aead-screen-174-v1/build/trace-final/accel-sim.out'
NEW_RUNTIME = '/workspace/dtc-ag7-policyb-integrated-174-v1/build/accel-sim.out'
CORE_LIBRARY = '/workspace/dtc-lane-ag3-aead-screen-174-v1/build/combined-final/libcudart.so'
CORE_LIBRARY_SHA = 'aee7c03cf30c2e9c2c9577165e019ce1dde929a668ca84882b5286415989cec2'
NEW_RUNTIME_SHA = '1004880fd7f01f815eb55d3e23fee451d95bb90eef7ecfb19ec8fd9531b9bd6c'
CC_SHA = '06fd9c2566060a2886ed5f4ecf46a49cfffafda42645b323f8aa69a9001a2516'
HEADER_SHA = '9e51b117e535fcdbcf8c1bcd5aa94a82cea65ee78f4d32485f1c3a451f7158f1'
BASE_CYCLES = {'GEMM': 1071405, 'Gaussian': 3278356}
POINTS = ('AE_GEMM', 'AE_Gaussian', 'AD_GEMM', 'AD_Gaussian')


class IdentityReject(ValueError):
    pass


def require(value, reason):
    if not value:
        raise IdentityReject(reason)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True,
        separators=(',', ':'), ensure_ascii=True).encode()).hexdigest()


def science_identity_data(preregistration, base, point):
    """Join authenticated original science data without inheriting old UUIDs.

    Caller must authenticate original prereg/BASE JSON with pinned Reader
    digests, re-run _check_inputs and current config/source checks, and register
    new UUIDs independently. This function does not read or replace those checks.
    """
    try:
        require(point in POINTS, 'UNKNOWN_AG7_POINT')
        points = preregistration['ordered_points']
        require(tuple(x['point'] for x in points) == POINTS, 'FIXED_FOUR_POINT_ORDER_CHANGED')
        spec = next(x for x in points if x['point'] == point)
        require(spec['core_commit'] == CORE and spec['framework_source'] == ORIGINAL_FRAMEWORK,
                'ORIGINAL_SCIENCE_SOURCE_ANCHOR_CHANGED')
        require(spec['retries'] == 0 and spec['timeout_seconds'] == 7200 and
                spec['full_processing_window'] == 'ALL_COMMANDS_ALL_KERNELS_ALL_CTA_NO_PREFIX_NATURAL_EXIT0',
                'ORIGINAL_FULL_INPUT_CONTRACT_CHANGED')
        workload, arm = spec['workload'], spec['arm']
        require(workload in BASE_CYCLES and arm in ('AE', 'AD') and point == arm + '_' + workload,
                'ARM_WORKLOAD_MISMATCH')
        require(base['workload'] == workload and base['recorded_cycles'] == BASE_CYCLES[workload] ==
                base['independently_reparsed_cycles'] == spec['imported_BASE_cycles'], 'BASE_CYCLE_JOIN_FAILED')
        require(base['UUID'] == spec['imported_BASE_UUID'] and
                base['commands'] == spec['expected_commands'] and
                base['kernels'] == spec['expected_kernels'] and
                base['CTA'] == spec['expected_CTA'] and
                base['active_thread_instructions'] == spec['expected_instructions'], 'BASE_FULL_INPUT_JOIN_FAILED')
        options = copy.deepcopy(base['effective_options'])
        require(len(options) == 270 and options['-gpgpu_dtc_l1_tag_hash_bankrow'] == ['0'] and
                options['-gpgpu_dtc_l1_progressive_wakeup'] == ['0'], 'EXACT_OFF_BASE_OPTIONS_REQUIRED')
        toggle = '-gpgpu_dtc_l1_tag_hash_bankrow' if arm == 'AE' else '-gpgpu_dtc_l1_progressive_wakeup'
        options[toggle] = ['1']
        require(options == spec['expected_full_effective_options'] and
                spec['option_deltas_from_same_input_BASE'] == {toggle: {'BASE': ['0'], 'ON': ['1']}},
                'ALL_270_OPTIONS_OR_SINGLE_ARM_DELTA_CHANGED')
        return dict(status='PASS_SCIENCE_DATA_JOIN_ONLY', point=point, core_commit=CORE,
            original_framework=ORIGINAL_FRAMEWORK, workload=workload, arm=arm,
            comparator_cycles=BASE_CYCLES[workload], options=options,
            options_sha256=digest(options), trace_list=spec['trace_list'],
            trace_list_sha256=spec['trace_list_sha256'], expected_commands=copy.deepcopy(spec['expected_commands']),
            expected_kernels=spec['expected_kernels'], expected_instructions=spec['expected_instructions'],
            expected_CTA=spec['expected_CTA'], configs=copy.deepcopy(spec['configs']),
            runtime_environment=copy.deepcopy(spec['runtime_environment']),
            runtime_echo_observed=False, current_inputs_checked=False,
            current_runtime_checked=False, resource_admission=False, execution_authority=False,
            scientific_acceptance=False, simulator_starts=0)
    except IdentityReject:
        raise
    except (KeyError, TypeError, ValueError, StopIteration) as error:
        raise IdentityReject('MALFORMED_SCIENCE_IDENTITY_DATA') from error


def _files(manifests):
    files = {}
    for target, manifest in manifests.items():
        require(manifest['target'] == target and manifest['cache_mode'] == 'PRESENT_REQUIRED_EARLY',
                'LOADER_CACHE_CONTRACT_CHANGED')
        for row in manifest['files']:
            previous = files.setdefault(row['path'], row)
            require(all(previous[k] == row[k] for k in ('sha256', 'identity', 'role', 'kind')),
                    'INCONSISTENT_RUNTIME_MANIFEST_ENTRY')
    return files


def runtime_bridge_data(original_manifests, new_manifests, build_receipt):
    """Check exact allowed manifest delta; no filesystem truth is invented.

    Caller must authenticate current generated manifests and revalidate every
    row with Reader plus actual per-exec mapping/loader observation. This data
    join is not a current image check or a BA comparator acceptance decision.
    """
    try:
        require(set(original_manifests) == {OLD_RUNTIME, '/usr/bin/dash', '/usr/bin/cat'} and
                set(new_manifests) == {NEW_RUNTIME, '/usr/bin/dash', '/usr/bin/cat'},
                'EXACT_RUNTIME_TARGET_CLOSURE_CHANGED')
        before, after = _files(original_manifests), _files(new_manifests)
        require(len(before) == len(after) == 12 and '/etc/ld.so.cache' in after,
                'EXACT_12_RUNTIME_FILES_REQUIRED')
        require(set(after) == (set(before) - {OLD_RUNTIME}) | {NEW_RUNTIME},
                'UNAPPROVED_RUNTIME_DEPENDENCY_DELTA')
        for path in set(before) - {OLD_RUNTIME}:
            require(all(before[path][k] == after[path][k] for k in ('sha256', 'identity', 'role', 'kind')),
                    'NONFRAMEWORK_RUNTIME_BYTES_OR_IDENTITY_CHANGED:' + path)
        require(after[NEW_RUNTIME]['sha256'] == NEW_RUNTIME_SHA and
                after[NEW_RUNTIME]['role'] == before[OLD_RUNTIME]['role'] and
                after[NEW_RUNTIME]['kind'] == before[OLD_RUNTIME]['kind'], 'NEW_FRAMEWORK_BUILD_JOIN_FAILED')
        require(after[CORE_LIBRARY]['sha256'] == CORE_LIBRARY_SHA and
                build_receipt['original_core_library_unchanged']['sha256'] == CORE_LIBRARY_SHA and
                build_receipt['Core_compile_starts'] == 0 and build_receipt['simulator_starts'] == 0,
                'ORIGINAL_CORE_LIBRARY_OR_NO_MODEL_BUILD_CONTRACT_CHANGED')
        require(build_receipt['status'] == 'FRAMEWORK_ONLY_BUILD_PASS_NOT_EXECUTED' and
                build_receipt['binaries']['accel-sim.out']['path'] == NEW_RUNTIME and
                build_receipt['binaries']['accel-sim.out']['sha256'] == NEW_RUNTIME_SHA,
                'REAL_FRAMEWORK_BUILD_RECEIPT_REQUIRED')
        for target in ('/usr/bin/dash', '/usr/bin/cat'):
            require(new_manifests[target]['interpreter'] == original_manifests[target]['interpreter'],
                    'HELPER_INTERPRETER_CHANGED')
        require(new_manifests[NEW_RUNTIME]['interpreter'] == original_manifests[OLD_RUNTIME]['interpreter'],
                'SIMULATOR_INTERPRETER_CHANGED')
        return dict(status='PASS_RUNTIME_MANIFEST_DELTA_JOIN_ONLY',
            allowed_delta='ONLY_FRAMEWORK_ROOT_ELF_WITH_INDEPENDENT_NONINTERFERENCE_BRIDGE',
            framework_elf=NEW_RUNTIME, framework_sha256=NEW_RUNTIME_SHA,
            unchanged_core_library_sha256=CORE_LIBRARY_SHA,
            common_runtime_files=11, exact_runtime_files=12,
            current_file_hash_and_stat_validation=False, actual_mapping_observation=False,
            BA_scoped_comparator_acceptance=False, scientific_acceptance=False,
            execution_authority=False)
    except IdentityReject:
        raise
    except (KeyError, TypeError, ValueError) as error:
        raise IdentityReject('MALFORMED_RUNTIME_BRIDGE_DATA') from error
