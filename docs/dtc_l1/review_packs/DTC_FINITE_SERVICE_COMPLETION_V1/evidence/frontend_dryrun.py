"""Static Gate C binary/config preflight. No registry, UUID, or launcher writes."""
import argparse
import hashlib
import json
from pathlib import Path

import first4_route

HERE = Path(__file__).resolve().parent
WITNESS = 'GESUMMV'
ROUTE = HERE / 'first4_GESUMMV.static.json'
CONFIG_DIR = HERE / 'frozen_configs'
BINARY = Path('/root/data/dtc_finite_service_completion_v1_20261109/build/frozen_candidate_9a0de9b9/framework/accel-sim.out')
LIBCUDART = Path('/root/data/dtc_finite_service_completion_v1_20261109/build/frozen_candidate_9a0de9b9/core/libcudart.so')
BINARY_SHA = 'a9ec6f231d9491690eb913d1cb69d7d2dae0f769f8854efc4df0512b5f1fd00c'
LIBCUDART_SHA = '43b3dc2f3e04d577e6c682f632691aca637b2670aee52c18b809f4d4c4e64860'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def encoded(value):
    return (json.dumps(value, sort_keys=True, indent=2) + '\n').encode()


def require(condition, label):
    if not condition:
        raise RuntimeError(label)


def put_exact(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        require(path.read_bytes() == content, 'EXISTING_FREEZE_DIFFERS:' + str(path))
    else:
        path.write_bytes(content)


def build():
    route = first4_route.route(WITNESS)
    require(ROUTE.read_bytes() == encoded(route), 'STATIC_ROUTE_DRIFT')
    require(sha(BINARY) == BINARY_SHA, 'NEW_BINARY_SHA')
    require(sha(LIBCUDART) == LIBCUDART_SHA, 'NEW_LIBCUDART_SHA')
    configs = []
    for cell in route['cells']:
        spec = json.loads(Path(cell['historical_DH_P0_source_spec_path']).read_bytes())
        source_configs = spec['configs']
        require(len(source_configs) == 4, 'BASE_CONFIG_COUNT')
        require(cell['effective_options_count'] == 271, 'EFFECTIVE_OPTION_COUNT')
        require(all(sha(Path(c['path'])) == c['sha256'] for c in source_configs), 'BASE_CONFIG_SHA')
        configs.append(source_configs)
    require(all(c == configs[0] for c in configs), 'PAIR_BASE_CONFIGS_DIFFER')
    files = {}
    base = []
    for index, source in enumerate(configs[0]):
        src = Path(source['path'])
        target = CONFIG_DIR / ('config-' + str(index) + '.config')
        content = src.read_bytes()
        files[str(target)] = content
        base.append({'path': str(target), 'sha256': hashlib.sha256(content).hexdigest(),
                     'historical_source_path': str(src), 'historical_source_sha256': source['sha256']})
    modes = {}
    for mode, value in [('OFF', '0'), ('ON', '1')]:
        target = CONFIG_DIR / ('candidate-' + mode.lower() + '.config')
        content = ('-gpgpu_dtc_l1_short_collect_first ' + value + '\n').encode()
        files[str(target)] = content
        modes[mode] = {'path': str(target), 'sha256': hashlib.sha256(content).hexdigest(),
                       'value': value, 'full_config_paths': [r['path'] for r in base] + [str(target)]}
    manifest = {'schema': 'DTC_GATE_C_FIRST4_STATIC_FRONTEND_DRYRUN_V1',
                'status': 'STATIC_ONLY_NO_REQUEST_NO_UUID_NO_MODEL',
                'goal_commit': first4_route.GOAL_COMMIT,
                'route_path': str(ROUTE), 'route_sha256': sha(ROUTE),
                'witness': WITNESS, 'binary': {'path': str(BINARY), 'sha256': BINARY_SHA},
                'libcudart': {'path': str(LIBCUDART), 'sha256': LIBCUDART_SHA},
                'base_configs': base, 'candidate_configs': modes,
                'cells': [{'program': c['program'], 'mode': c['mode'],
                           'input_digest': c['input_digest'],
                           'config_paths': modes[c['mode']]['full_config_paths'],
                           'effective_options_count': c['effective_options_count']}
                          for c in route['cells']],
                'unresolved': ['new_native_registry_request', 'fresh_one_use_UUIDs',
                               'sole_dispatcher_and_parent_lease', 'launcher_layout_and_actual_argv',
                               'runtime_guard', 'new_strict', 'true164_SOURCE_KEEP',
                               'typed_native_restore', 'independent_Gate_C_review']}
    return files, manifest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--freeze', action='store_true')
    args = parser.parse_args()
    files, manifest = build()
    if args.freeze:
        for path, content in files.items():
            put_exact(Path(path), content)
        put_exact(HERE / 'FRONTEND_DRYRUN_MANIFEST.json', encoded(manifest))
    else:
        for path, content in files.items():
            if Path(path).exists():
                require(Path(path).read_bytes() == content, 'FROZEN_CONFIG_DRIFT:' + path)
        p = HERE / 'FRONTEND_DRYRUN_MANIFEST.json'
        if p.exists():
            require(p.read_bytes() == encoded(manifest), 'FROZEN_MANIFEST_DRIFT')
    print('PASS_STATIC_FRONTEND witness=' + WITNESS + ' cells=4 binary=' + BINARY_SHA +
          ' libcudart=' + LIBCUDART_SHA + ' registry_writes=0 model_starts=0')


if __name__ == '__main__':
    main()
