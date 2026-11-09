"""Shared exact5 Native authority primitives; importing performs no writes."""
import contextlib
import copy
import datetime
import fcntl
import hashlib
import importlib.util
import json
import os
import pathlib
import uuid

P = pathlib.Path
ROOT = P('/root/data/ep_l2_full_workload_performance_20261027_v1/research/optional_clean128_exact5_execution_20261109_v1')
NATIVE = P('/root/data/ep_l2_dtc_l1_native_v2')
REG = NATIVE / 'control/science_authority/NATIVE_SCIENCE_REGISTRY.json'
EPOCH = NATIVE / 'control/CURRENT_SCIENCE_EPOCH.json'
FRONTEND_GOAL = 'EP_L2_FULL_WORKLOAD_PERFORMANCE_POTENTIAL_EXPLORATION_V1'
GOAL = 'EP_L2_OPTIONAL_CLEAN128_EXACT5_EXECUTION_V1'
REQUESTS = {
    'GEMM': 'EP_L2_OPTIONAL_CLEAN128_GEMM3_20261109_V1',
    'stencil': 'EP_L2_OPTIONAL_CLEAN128_STENCIL2_20261109_V1',
}
COHORTS = {
    'EP_PERF_CLEAN128_GEMM_WV_EXT0_20261109_V1': 'GEMM',
    'EP_PERF_CLEAN128_GEMM_WV_EXT1_20261109_V1': 'GEMM',
    'EP_PERF_CLEAN128_GEMM_WV_EXT2_20261109_V1': 'GEMM',
    'EP_PERF_CLEAN128_STENCIL_WV_EXT0_20261109_V1': 'stencil',
    'EP_PERF_CLEAN128_STENCIL_WV_EXT2_20261109_V1': 'stencil',
}
G = 1 << 30
M = 1 << 20
GLOBAL_MAIN_ADMISSION_LOCK = P('/root/data/ep_l2_full_workload_performance_20261027_v1/execution_performance_first_20261103_v1/control/ADMISSION.lock')
GLOBAL_MAIN_RESTORE_WINDOW_LOCK = P('/root/data/ep_l2_full_workload_performance_20261027_v1/execution_performance_first_20261103_v1/control/ARCHIVE_SHARED_WINDOW.lock')


def need(ok, reason):
    if not ok:
        raise RuntimeError(reason)


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def sha(path):
    digest = hashlib.sha256()
    with P(path).open('rb') as stream:
        for block in iter(lambda: stream.read(M), b''):
            digest.update(block)
    return digest.hexdigest()


def read(path):
    def pairs(items):
        result = {}
        for key, value in items:
            need(key not in result, 'duplicate JSON key')
            result[key] = value
        return result
    return json.loads(P(path).read_bytes(), object_pairs_hook=pairs,
                      parse_constant=lambda value: need(False, 'nonfinite JSON'))


def encoded(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'),
                       ensure_ascii=False, allow_nan=False) + '\n').encode()


def put(path, value, exclusive=False):
    path = P(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = encoded(value)
    target = path if exclusive else path.with_name('.' + path.name + '.' + str(uuid.uuid4()))
    with target.open('xb') as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    if not exclusive:
        os.replace(target, path)
    directory = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)
    return {'path': str(path), 'sha256': hashlib.sha256(data).hexdigest()}


def ref(path):
    return {'path': str(path), 'sha256': sha(path)}


def exact(item):
    need(sha(item['path']) == item['sha256'], 'immutable reference drift')
    return read(item['path'])


def module(item, name):
    need(sha(item['path']) == item['sha256'], 'module drift')
    spec = importlib.util.spec_from_file_location(name, item['path'])
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


@contextlib.contextmanager
def locked(path, nonblock=False):
    path = P(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a+b') as handle:
        fcntl.flock(handle, fcntl.LOCK_EX | (fcntl.LOCK_NB if nonblock else 0))
        yield


def request_for_case(case):
    need(case in COHORTS, 'not one of the five exact cohorts')
    return REQUESTS[COHORTS[case]]


def authority():
    for unused in range(3):
        before = sha(REG)
        registry, epoch = read(REG), read(EPOCH)
        if before == sha(REG) == epoch['native_registry_sha256']:
            need(epoch['epoch'] == 2 and epoch['state'] == 'NATIVE_SCIENCE_ACTIVE',
                 'Native epoch inactive')
            need(epoch['holder'] == os.uname().nodename, 'Native holder changed')
            return registry, epoch
    raise RuntimeError('Native authority changed during read')


def remaining(row):
    if 'remaining' in row:
        return row['remaining']
    used = row.get('consumed', 0)
    return max(0, row.get('budget', 0) - (used if type(used) is int else len(used)))


def transaction(request_id, operation, mutate):
    """Update exactly one already registered family; retain all other rows."""
    need(request_id in REQUESTS.values(), 'request outside exact five')
    with locked(NATIVE / 'control/science_authority/REGISTRY_UPDATE.lock'):
        registry, epoch = authority()
        need(request_id in registry['registered_future_requests'], 'family not registered')
        previous = {'registry_sha256': sha(REG), 'epoch_sha256': sha(EPOCH)}
        peers = {key: copy.deepcopy(row) for key, row in
                 registry['registered_future_requests'].items() if key != request_id}
        protected = {key: copy.deepcopy(value) for key, value in registry.items()
                     if key not in ('registered_future_requests', 'new_scientific_budget_remaining')}
        result = mutate(registry)
        need({key: row for key, row in registry['registered_future_requests'].items()
              if key != request_id} == peers, 'another owner/family row changed')
        need({key: value for key, value in registry.items()
              if key not in ('registered_future_requests', 'new_scientific_budget_remaining')} == protected,
             'protected Native registry field changed')
        for path in (REG, EPOCH):
            old = NATIVE / 'control/science_authority/request_history' / (path.stem + '.' + sha(path) + '.json')
            if not old.exists():
                with old.open('xb') as stream:
                    stream.write(path.read_bytes())
        registry['new_scientific_budget_remaining'] = sum(
            remaining(row) for row in registry['registered_future_requests'].values())
        put(REG, registry)
        epoch['native_registry_sha256'] = sha(REG)
        epoch['new_budget_remaining'] = registry['new_scientific_budget_remaining']
        epoch['request_revision'] = {'request_id': request_id, 'operation': operation,
                                     'utc': now(), **previous}
        put(EPOCH, epoch)
        put(ROOT / 'control/authority_events' / (str(uuid.uuid4()) + '.json'),
            {'request_id': request_id, 'operation': operation, 'utc': now(),
             'previous': previous, 'new_registry_sha256': sha(REG),
             'new_epoch_sha256': sha(EPOCH), 'foreign_rows_preserved': True}, True)
        return result


if __name__ == '__main__':
    reg, epoch = authority()
    matching = [name for name in reg['registered_future_requests'] if name in REQUESTS.values()]
    print(json.dumps({'status': 'READ_ONLY_EXACT5_COMMON_PREFLIGHT_PASS',
                      'epoch': epoch['epoch'], 'registered_families': matching,
                      'model_starts': 0}, sort_keys=True))
