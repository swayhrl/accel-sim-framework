"""Explicit AG7 read-only identity adapter, no execution/authority/budget API.

Uses the frozen original Reader and _check_inputs rather than changing their
constants. Static ELF dependency discovery uses readelf, never target execution.
The caller alone owns fresh R2, immutable publication, UUIDs and BA acceptance.
"""
import copy
import importlib.util
import json
from pathlib import Path
import sys
import time

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
OLD = REPO / 'docs/dtc_l1/iscas2027/evidence_closure_20261019_v1/execution'
EVIDENCE = Path('/workspace/dtc-ag7-policyb-integrated-174-v1')
BUILD_RESULT_SHA = 'c1b070525d2ed264e70000c3e61f059b87a03d7b8b7d1ad17357abdde7ac25dd'
EXPECTED_FRAMEWORK_ECHO = 'accelsim-AG7-policyB-observational-framework-Core-c8090115'


def _load(name, path, sha=None):
    import hashlib
    data = Path(path).read_bytes()
    if sha is not None and hashlib.sha256(data).hexdigest() != sha:
        raise ValueError('FROZEN_SOURCE_CHANGED:' + str(path))
    module = importlib.util.module_from_spec(importlib.util.spec_from_file_location(name, path))
    exec(compile(data, str(path), 'exec'), module.__dict__)
    return module


def validate_all_identity(*, own_root=EVIDENCE, prepare_configs=False):
    """Current checks for all four point specifications; no UUID materialization.

    prepare_configs permits only creation of exact independent config copies.
    With False all sixteen copies must already exist. Caller persists the
    returned compact receipt and manifests; current per-fork checks remain due.
    """
    started = time.monotonic_ns()
    own_root = Path(own_root).resolve()
    if own_root != EVIDENCE:
        raise ValueError('EXACT_AG7_OWN_ROOT_REQUIRED')
    original = _load('ag7_original_identity', OLD / 'prepared_ag6/ag6_input_runtime_identity.py',
                     '315755007bacd7b635fab96ed01206272921ebd820202fe0a21ef3af37c6f5f4')
    join = _load('ag7_identity_data_join', HERE / 'input_identity.py')
    executable = json.loads((OLD / 'AG6_EXECUTABLE_PREREGISTRATION_V2.json').read_text())
    binding = executable['identity_contract']
    reader = original.Reader()
    prereg = reader.artifact(binding['preregistration'], original.PREREG_SHA)
    artifacts = {name: reader.artifact(binding['artifacts'][name], sha, text=name == 'input_members')
                 for name, sha in original.ARTIFACT_SHAS.items()}
    inputs = original._check_inputs(reader, prereg, artifacts['input_stats'], artifacts['input_members'])
    sources = artifacts['sources']
    original.require(len(sources) == 702 and len({(r['repository'], r['path']) for r in sources}) == 702 and
                     sum(r['repository'] == 'Core' for r in sources) == 650,
                     'EXACT_702_ORIGINAL_SOURCE_CLOSURE_REQUIRED')
    for row in sources:
        root = Path(binding['source_roots'][row['repository']]).resolve(strict=True)
        path = (root / row['path']).resolve(strict=True)
        original.require(path.is_relative_to(root), 'ORIGINAL_SOURCE_ESCAPES_ROOT')
        reader.read(path, row['sha256'])
    # Preserve the original complete source audit; independently bind the actual
    # AG7 compiled Framework, substituting only reviewed cc and adding header.
    current_framework = 0
    for row in sources:
        if row['repository'] != 'Framework':
            continue
        expected = join.CC_SHA if row['path'] == 'gpu-simulator/accel-sim.cc' else row['sha256']
        reader.read(REPO / row['path'], expected)
        current_framework += 1
    original.require(current_framework == 52, 'EXACT_52_FRAMEWORK_SOURCES_REQUIRED')
    reader.read(REPO / 'gpu-simulator/ag7_policyb_progress.h', join.HEADER_SHA)
    reader.read(EVIDENCE / 'build/accelsim_version.h',
                '3f40117a359734f88fb8d4ea7f657462af34606d7514c42e0b8fe3a7e8a90a04')
    for name in ('combined-final', 'trace-final'):
        reader.read(original.BUILD_ROOT / name / 'compile_commands.json',
                    artifacts['build']['compile_commands_sha'][name])
    build = json.loads(reader.read(EVIDENCE / 'evidence/w2_build_admission_1/RESULT.json',
                                   BUILD_RESULT_SHA, keep=True))
    for row in build['reused_main_and_parser_objects']:
        reader.read(row['path'], row['sha256'])
    original.require(len(build['reused_main_and_parser_objects']) == 3, 'EXACT_THREE_REUSED_OBJECTS_REQUIRED')
    # Freeze with the original exact mapping implementation and original static
    # readelf resolver; no target/loader execution or ldd is used.
    vendor = OLD / 'prepared_runtime/vendor'
    mapping = _load('mapping_roles', vendor / 'mapping_roles.py',
                    '1409539bad1d173c4bf48463c5465f54e8aba89db736e27bae745fd7a7f07155')
    previous_mapping = sys.modules.get('mapping_roles')
    sys.modules['mapping_roles'] = mapping
    try:
        static = _load('ag7_freeze_static', vendor / 'freeze_static.py',
                       '4667b417d5011c32061361736627dce9efa307ef19064b57675c2b7f0d906362')
        new_root_manifest, static_objects = static.freeze_executable(join.NEW_RUNTIME,
                                              str(Path(join.CORE_LIBRARY).parent))
    finally:
        if previous_mapping is None:
            sys.modules.pop('mapping_roles', None)
        else:
            sys.modules['mapping_roles'] = previous_mapping
    manifests = copy.deepcopy(artifacts['runtime'])
    del manifests[join.OLD_RUNTIME]
    manifests[join.NEW_RUNTIME] = new_root_manifest
    # Keep every original helper manifest, plus actual content/stat checking of
    # all unique current files in the full simulator/helper closure.
    rows = {}
    for manifest in manifests.values():
        mapping.validate_manifest(manifest)
        for row in manifest['files']:
            prior = rows.setdefault(row['path'], row)
            original.require(all(prior[k] == row[k] for k in ('sha256', 'identity', 'kind', 'role')),
                             'INCONSISTENT_FULL_RUNTIME_JOIN')
    runtime_join = join.runtime_bridge_data(artifacts['runtime'], manifests, build)
    points = {}
    for point in join.POINTS:
        spec = next(row for row in prereg['ordered_points'] if row['point'] == point)
        science = join.science_identity_data(prereg, artifacts['BASE_' + spec['workload']], point)
        configs = []
        for ordinal, expected in enumerate(spec['configs']):
            data = reader.read(expected['path'], expected['sha256'], keep=True)
            destination = own_root / 'configs' / point / ('config-' + str(ordinal) + '.config')
            original.require(destination.resolve().is_relative_to(own_root) and
                             destination.resolve() != Path(expected['path']).resolve(),
                             'CONFIG_NOT_IN_EXACT_NEW_OWN_ROOT')
            if prepare_configs and not destination.exists():
                destination.parent.mkdir(parents=True, exist_ok=True)
                with destination.open('xb') as stream:
                    stream.write(data)
            reader.read(destination, expected['sha256'])
            configs.append(dict(path=str(destination), sha256=expected['sha256'], source_path=expected['path']))
        original.require(len(configs) == len({row['path'] for row in configs}) == 4,
                         'EXACT_FOUR_CONFIGS_REQUIRED')
        argv = [join.NEW_RUNTIME, '-trace', science['trace_list']]
        for row in configs:
            argv.extend(['-config', row['path']])
        points[point] = dict(science, runtime_path=join.NEW_RUNTIME,
            runtime_sha256=join.NEW_RUNTIME_SHA, runtime_library_path=join.CORE_LIBRARY,
            runtime_library_sha256=join.CORE_LIBRARY_SHA, validated_argv=argv,
            validated_environment=science['runtime_environment'], config_copies=configs,
            expected_embedded_framework_version=EXPECTED_FRAMEWORK_ECHO,
            expected_embedded_core_version=spec['expected_embedded_core_version'])
    for row in artifacts['input_stats']:
        original._trace_stat(row)
    reader.finish()
    for row in rows.values():
        mapping.verify_file(row)
    receipt = dict(status='PASS_CURRENT_AG7_STATIC_IDENTITY_BRIDGE_NOT_BA_ACCEPTANCE',
        points=points, inputs=inputs, trace_members_stat_checked=511, trace_body_bytes_read=0,
        original_source_files_sha_checked=702, current_Framework_source_files_sha_checked=52,
        observational_header_and_version_checked=2, matching_original_compile_command_files=2,
        reused_object_files_sha_checked=3, exact_runtime_files_checked=len(rows),
        runtime_manifest_delta_join=runtime_join, source_model_core_unchanged=True,
        source_noninterference_review='PRODUCER_INDEPENDENT_SOURCE_REVIEW.md',
        build_result_sha256=BUILD_RESULT_SHA, regular_file_bytes_read=reader.bytes_read,
        model_execution_starts=0, simulator_starts=0, resource_admission=False,
        BA_scoped_comparator_acceptance=False, scientific_acceptance=False,
        actual_simulator_mapping_observation=False,
        monotonic_interval_ns=[started, time.monotonic_ns()])
    return receipt, manifests, static_objects


def validate_identity(point):
    """Fresh current check; caller keeps the full result and applies new UUID."""
    receipt, manifests, _objects = validate_all_identity(prepare_configs=False)
    if point not in receipt['points']:
        raise ValueError('UNKNOWN_AG7_POINT')
    return dict(receipt['points'][point], current_identity_receipt=receipt), manifests
