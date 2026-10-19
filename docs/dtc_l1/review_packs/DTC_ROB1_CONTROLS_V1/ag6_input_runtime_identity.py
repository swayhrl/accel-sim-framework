"""PREPARED_NOT_EXECUTED: read-only AG6 identity check, no CLI or launch API.

The parent must pin the binding JSON in its own immutable dispatch closure.
This returns an identity receipt only; it cannot grant execution authority.
Trace bodies are never opened. Their historical SHA provenance is joined to
current stat identity, following the original strict input_identity contract.
"""
import copy
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import stat
import time

CORE = 'c8090115bd57512b1b23fca7d925301fa620c751'
FRAMEWORK = '8e43c75a5e2eb60a8466084602b7df8117111e89'
POINTS = ('AE_GEMM', 'AE_Gaussian', 'AD_GEMM', 'AD_Gaussian')
PREREG_SHA = '844591f608ff99203b22f7f7cb958e1c7633726c3e351da7b7407dd53edee38e'
ARTIFACT_SHAS = {
    'input_stats': '35700a52c852a81fabd26c0fb28d220be98646f5ca3d46fde7c9191f65aadd89',
    'input_members': 'c1412fd32722f8c95a45c30242d2dfd1abb3b45f4673b5beb3edd27af63c6bc5',
    'sources': 'c238c7908f1769a148973019af51c255a0357df7ad9f1764f8ff4c18ef65d79b',
    'build': '0f66fb68264ac061b4800b7c134b82d7a73b10e96d3993dc59fdea552826142a',
    'runtime': 'b417b486017a281c46df924cf2791afdb5378000188c64382fe116df76b0f84b',
    'BASE_GEMM': '1ace49e4e93e2251e04434dcf28761002dabeb8601c12c14f33be82a1c155c95',
    'BASE_Gaussian': '9bbfad8fc70fb54b02dfc406e57bfed9d9373bf1143950e667f28a716fbf18d2',
}
TRACE_STAT_KEYS = ('st_dev', 'st_ino', 'st_size', 'st_mtime_ns', 'st_ctime_ns')
FILE_STAT_KEYS = TRACE_STAT_KEYS + ('st_mode', 'st_uid', 'st_gid', 'st_nlink')
IDENTITY_FIELDS = dict(device='st_dev', inode='st_ino', size='st_size',
    mode='st_mode', uid='st_uid', gid='st_gid', mtime_ns='st_mtime_ns',
    ctime_ns='st_ctime_ns', nlink='st_nlink')
BUILD_ROOT = Path('/workspace/dtc-lane-ag3-aead-screen-174-v1/build')
OWN_ROOT = Path('/workspace/dtc-evidence-closure-20261019-v1/coordinator/ag6-v2')
MAX_FILE = 64 * 1024**2
MAX_TOTAL = 512 * 1024**2


class IdentityReject(ValueError):
    pass


def require(value, reason):
    if not value:
        raise IdentityReject(reason)


def canonical_sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True,
        separators=(',', ':'), ensure_ascii=True).encode()).hexdigest()


def signature(value):
    return {key: getattr(value, key) for key in FILE_STAT_KEYS}


class Reader:
    def __init__(self):
        self.bytes_read = 0
        self.checked = {}

    def read(self, path, expected, *, keep=False):
        """Bounded regular-file hash; reject replacement/mutation during read."""
        path = Path(path)
        require(path.is_absolute(), 'ABSOLUTE_FILE_REQUIRED:' + str(path))
        before = path.stat()
        require(stat.S_ISREG(before.st_mode) and before.st_size <= MAX_FILE,
                'BOUNDED_REGULAR_FILE_REQUIRED:' + str(path))
        require(self.bytes_read + before.st_size <= MAX_TOTAL, 'IDENTITY_READ_BUDGET')
        digest = hashlib.sha256()
        chunks = []
        count = 0
        with path.open('rb') as stream:
            require(signature(os.fstat(stream.fileno())) == signature(before),
                    'FILE_CHANGED_BEFORE_OPEN:' + str(path))
            while True:
                block = stream.read(min(1024**2, MAX_FILE - count + 1))
                if not block:
                    break
                count += len(block)
                require(count <= MAX_FILE and self.bytes_read + count <= MAX_TOTAL,
                        'IDENTITY_READ_BUDGET')
                digest.update(block)
                if keep:
                    chunks.append(block)
            require(signature(os.fstat(stream.fileno())) == signature(before),
                    'FILE_CHANGED_DURING_READ:' + str(path))
        require(count == before.st_size and signature(path.stat()) == signature(before),
                'FILE_CHANGED_AFTER_READ:' + str(path))
        require(digest.hexdigest() == expected, 'FILE_SHA_CHANGED:' + str(path))
        self.bytes_read += count
        self.checked[str(path)] = signature(before)
        return b''.join(chunks) if keep else signature(before)

    def artifact(self, descriptor, expected, *, text=False):
        require(descriptor['sha256'] == expected, 'UNTRUSTED_ARTIFACT_DIGEST')
        data = self.read(descriptor['path'], expected, keep=True)
        return data.decode('utf-8') if text else json.loads(data)

    def finish(self):
        for path, expected in self.checked.items():
            require(signature(Path(path).stat()) == expected,
                    'FILE_CHANGED_BEFORE_RECEIPT:' + path)


def _trace_stat(row):
    expected = row['stat_identity']
    require(set(expected) == set(TRACE_STAT_KEYS), 'INCOMPLETE_TRACE_STAT_PROVENANCE')
    current = Path(row['path']).stat()  # never open a trace body
    require(stat.S_ISREG(current.st_mode), 'TRACE_NOT_REGULAR:' + row['path'])
    require({key: getattr(current, key) for key in TRACE_STAT_KEYS} == expected,
            'POST_SHA_TRACE_MUTATION:' + row['path'])


def _check_inputs(reader, prereg, stats_rows, member_text):
    require(len(stats_rows) == 511, 'COMPLETE_511_MEMBER_PROVENANCE_REQUIRED')
    table = list(csv.DictReader(io.StringIO(member_text), delimiter='\t'))
    require(len(table) == 511, 'COMPLETE_511_MEMBER_SHA_TABLE_REQUIRED')
    by_key = {(row['workload'], int(row['ordinal'])): row for row in table}
    require(len(by_key) == 511, 'DUPLICATE_MEMBER_SHA_ROW')
    seen = set()
    paths = set()
    lists = {}
    for row in stats_rows:
        key = (row['workload'], row['ordinal'])
        require(key not in seen and row['path'] not in paths, 'DUPLICATE_INPUT_MEMBER')
        seen.add(key); paths.add(row['path'])
        original = by_key[key]
        require(row['identity'] == original['identity'] == 'PASS_FRESH_SHA256' and
                row['expected_sha256'] == row['actual_sha256'] ==
                original['expected_sha256'] == original['actual_sha256'] and
                row['path'] == original['path'] and row['bytes'] == int(original['bytes']) ==
                row['stat_identity']['st_size'] and
                row['active_thread_instructions'] == int(original['active_thread_instructions']) and
                row['complete_ctas'] == int(original['complete_ctas']),
                'INPUT_SHA_STAT_PROVENANCE_JOIN_FAILED:' + str(key))
        _trace_stat(row)
    require(seen == set(by_key), 'INPUT_MEMBER_SET_CHANGED')
    for workload, count in [('GEMM', 1), ('Gaussian', 510)]:
        specs = [p for p in prereg['ordered_points'] if p['workload'] == workload]
        require(len(specs) == 2, 'EXPECTED_TWO_ARMS_PER_INPUT')
        spec = specs[0]
        require(all(p['trace_list'] == spec['trace_list'] and
                    p['trace_list_sha256'] == spec['trace_list_sha256'] and
                    p['expected_commands'] == spec['expected_commands'] for p in specs),
                'ARM_INPUT_VECTOR_CHANGED')
        commands = reader.read(spec['trace_list'], spec['trace_list_sha256'], keep=True).decode().splitlines()
        commands = [line.strip() for line in commands if line.strip()]
        require(commands == spec['expected_commands'] and len(commands) == count + 3,
                'COMPLETE_TRACE_COMMAND_VECTOR_CHANGED')
        require(all(line.startswith('MemcpyHtoD,') for line in commands[:3]) and
                commands[3:] == ['kernel-' + str(i) + '.traceg' for i in range(1, count + 1)],
                'TRACE_COMMAND_ORDER_CHANGED')
        selected = sorted((r for r in stats_rows if r['workload'] == workload), key=lambda r:r['ordinal'])
        require([r['ordinal'] for r in selected] == list(range(1, count + 1)) and
                [r['path'] for r in selected] == [str(Path(spec['trace_list']).parent / name) for name in commands[3:]],
                'TRACE_LIST_TO_MEMBER_PATH_JOIN_FAILED')
        require(sum(r['active_thread_instructions'] for r in selected) == spec['expected_instructions'] and
                sum(r['complete_ctas'] for r in selected) == spec['expected_CTA'], 'FULL_INPUT_COUNTS_CHANGED')
        lists[workload] = dict(members=count, commands=commands,
                              trace_list_sha256=spec['trace_list_sha256'])
    return lists


def _check_runtime(reader, manifests, spec, build):
    require(set(manifests) == {spec['runtime_path'], '/usr/bin/dash', '/usr/bin/cat'},
            'RUNTIME_TARGET_CLOSURE_CHANGED')
    files = {}
    for target, manifest in manifests.items():
        require(manifest['target'] == target and manifest['cache_mode'] == 'PRESENT_REQUIRED_EARLY',
                'LOADER_CACHE_CONTRACT_CHANGED')
        for entry in manifest['files']:
            prior = files.setdefault(entry['path'], entry)
            require(all(prior[k] == entry[k] for k in ('sha256', 'identity', 'role', 'kind')),
                    'INCONSISTENT_RUNTIME_MANIFEST_ENTRY')
    require(len(files) == 12 and '/etc/ld.so.cache' in files, 'EXACT_12_RUNTIME_FILES_REQUIRED')
    for path, entry in files.items():
        current = reader.read(path, entry['sha256'])
        expected = entry['identity']
        require(set(IDENTITY_FIELDS) | {'major', 'minor'} == set(expected), 'INCOMPLETE_RUNTIME_STAT')
        require(all(current[attr] == expected[key] for key, attr in IDENTITY_FIELDS.items()) and
                os.major(current['st_dev']) == expected['major'] and os.minor(current['st_dev']) == expected['minor'],
                'RUNTIME_STAT_CHANGED:' + path)
    require(files[spec['runtime_path']]['sha256'] == spec['runtime_sha256'] ==
            build['ELFs'][spec['runtime_path']]['sha256'] and
            files[spec['runtime_library_path']]['sha256'] == spec['runtime_library_sha256'] ==
            build['ELFs'][spec['runtime_library_path']]['sha256'], 'RUNTIME_BUILD_JOIN_FAILED')
    return [{'path': p, 'sha256': e['sha256'], 'role': e['role'], 'identity': e['identity']}
            for p, e in sorted(files.items())]


def validate_identity(binding, point):
    """Return receipt or raise; parent pins this binding, persists result itself.

    binding: {preregistration:{path,sha256}, artifacts:{name:{path,sha256}},
      source_roots:{Core:absolute,Framework:absolute},
      own_config_copies:{point:[{path,sha256,source_path}, ...]}}.
    All artifact digests and the preregistration are independently fixed here.
    No receipt from a prior point replaces any current check.
    """
    try:
        return _validate(copy.deepcopy(binding), point)
    except IdentityReject:
        raise
    except (OSError, ValueError, KeyError, TypeError, OverflowError) as error:
        raise IdentityReject('IDENTITY_MATERIAL_MISSING_OR_MALFORMED:' + repr(error)) from error


def _validate(binding, point):
    began = time.monotonic_ns()
    require(point in POINTS, 'UNKNOWN_AG6_POINT')
    reader = Reader()
    prereg = reader.artifact(binding['preregistration'], PREREG_SHA)
    require(tuple(p['point'] for p in prereg['ordered_points']) == POINTS, 'FOUR_POINT_ORDER_CHANGED')
    spec = next(p for p in prereg['ordered_points'] if p['point'] == point)
    require(spec['core_commit'] == CORE and spec['framework_source'] == FRAMEWORK and
            spec['retries'] == 0 and spec['timeout_seconds'] == 7200 and
            spec['full_processing_window'] == 'ALL_COMMANDS_ALL_KERNELS_ALL_CTA_NO_PREFIX_NATURAL_EXIT0',
            'FIXED_SCIENCE_CHANGED')
    artifacts = {name:reader.artifact(binding['artifacts'][name], digest, text=name=='input_members')
                 for name, digest in ARTIFACT_SHAS.items()}
    build = artifacts['build']
    require(build['core_commit'] == CORE and build['framework_source'] == FRAMEWORK and
            build['source_files_sha'] == ARTIFACT_SHAS['sources'] and build['assertions_enabled'] is True,
            'BUILD_SOURCE_ANCHOR_CHANGED')
    base = artifacts['BASE_' + spec['workload']]
    options = copy.deepcopy(base['effective_options'])
    require(len(options) == 270 and base['workload'] == spec['workload'] and
            base['UUID'] == spec['imported_BASE_UUID'] and
            base['recorded_cycles'] == spec['imported_BASE_cycles'] and
            base['commands'] == spec['expected_commands'], 'BASE_OPTION_INPUT_JOIN_FAILED')
    toggle = '-gpgpu_dtc_l1_tag_hash_bankrow' if spec['arm'] == 'AE' else '-gpgpu_dtc_l1_progressive_wakeup'
    require(spec['arm'] in ('AE', 'AD') and options[toggle] == ['0'], 'BASE_TOGGLE_NOT_OFF')
    options[toggle] = ['1']
    require(options == spec['expected_full_effective_options'] and len(options) == 270 and
            spec['option_deltas_from_same_input_BASE'] == {toggle:{'BASE':['0'], 'ON':['1']}},
            'ALL_270_OPTIONS_OR_SOLE_DELTA_CHANGED')
    copies = binding['own_config_copies'][point]
    require(len(copies) == len(spec['configs']) == 4, 'EXACT_FOUR_CONFIG_COPIES_REQUIRED')
    for expected, actual in zip(spec['configs'], copies):
        require(Path(actual['path']).is_absolute() and
                actual['source_path'] == expected['path'] and actual['sha256'] == expected['sha256'] and
                Path(actual['path']).resolve().is_relative_to(OWN_ROOT) and
                Path(actual['path']).resolve() != Path(expected['path']).resolve(),
                'CONFIG_COPY_NOT_EXACT_OWN_MATERIALIZATION')
        reader.read(expected['path'], expected['sha256'])
        reader.read(actual['path'], expected['sha256'])
    require(len({r['path'] for r in copies}) == 4, 'DUPLICATE_CONFIG_COPY')
    argv = [spec['runtime_path'], '-trace', spec['trace_list']]
    for actual in copies:
        argv.extend(['-config', actual['path']])
    lists = _check_inputs(reader, prereg, artifacts['input_stats'], artifacts['input_members'])
    sources = artifacts['sources']
    require(len(sources) == 702 and len({(r['repository'],r['path']) for r in sources}) == 702 and
            sum(r['repository']=='Core' for r in sources) == 650 and
            sum(r['repository']=='Framework' for r in sources) == 52, 'EXACT_SOURCE_CLOSURE_REQUIRED')
    for row in sources:
        root = Path(binding['source_roots'][row['repository']])
        require(root.is_absolute(), 'ABSOLUTE_SOURCE_ROOT_REQUIRED')
        root = root.resolve(strict=True)
        path = (root / row['path']).resolve(strict=True)
        require(root.is_absolute() and path.is_relative_to(root), 'SOURCE_ESCAPES_REGISTERED_ROOT')
        reader.read(path, row['sha256'])
    for name in ('combined-final', 'trace-final'):
        reader.read(BUILD_ROOT / name / 'compile_commands.json', build['compile_commands_sha'][name])
    runtime = _check_runtime(reader, artifacts['runtime'], spec, build)
    for row in artifacts['input_stats']:
        _trace_stat(row)
    reader.finish()
    return dict(status='PASS_PRELAUNCH_IDENTITY_ONLY', point=point, attempt_uuid=spec['attempt_uuid'],
        preregistration_sha256=PREREG_SHA, binding_sha256=canonical_sha(binding),
        artifact_sha256=dict(ARTIFACT_SHAS), core_commit=CORE, framework_source=FRAMEWORK,
        config_copies=copies, expected_effective_options_sha256=canonical_sha(options), options=270,
        validated_argv=argv, validated_environment=spec['runtime_environment'],
        option_basis='FROZEN_ACTUAL_BASE_PLUS_EXACT_SINGLE_ARM_DELTA', runtime_echo_observed=False,
        inputs=lists, trace_members_stat_checked=511, trace_body_bytes_read=0,
        source_files_sha_checked=702, matching_build_compile_command_files=2, runtime_files=runtime,
        regular_file_bytes_read=reader.bytes_read, monotonic_interval_ns=[began,time.monotonic_ns()],
        stat_stability_not_fresh_trace_body_hash=True, mapping_observation_performed=False,
        resource_admission=False, execution_authority=False, simulator_starts=0,
        historical_executor_recertified=False)
