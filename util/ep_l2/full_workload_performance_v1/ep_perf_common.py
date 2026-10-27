"""Independent EP performance host utilities. Importing never starts science."""
import contextlib, copy, datetime, fcntl, hashlib, importlib.util, json, os, pathlib, uuid

P = pathlib.Path
ROOT = P('/root/data/ep_l2_full_workload_performance_20261027_v1')
NATIVE = P('/root/data/ep_l2_dtc_l1_native_v2')
REG = NATIVE / 'control/science_authority/NATIVE_SCIENCE_REGISTRY.json'
EPOCH = NATIVE / 'control/CURRENT_SCIENCE_EPOCH.json'
GOAL = 'EP_L2_FULL_WORKLOAD_PERFORMANCE_POTENTIAL_EXPLORATION_V1'
G = 1024**3
M = 1024**2


def need(ok, message):
    if not ok:
        raise RuntimeError(message)


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def sha(path):
    h = hashlib.sha256()
    with P(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(M), b''):
            h.update(chunk)
    return h.hexdigest()


def read(path):
    def pairs(items):
        value = {}
        for key, item in items:
            need(key not in value, 'duplicate JSON key')
            value[key] = item
        return value
    return json.loads(P(path).read_bytes(), object_pairs_hook=pairs,
                      parse_constant=lambda x: need(False, 'nonfinite JSON'))


def encoded(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'),
                       ensure_ascii=False, allow_nan=False) + '\n').encode()


def put(path, value, exclusive=False):
    path = P(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = encoded(value)
    if exclusive:
        with path.open('xb') as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
    else:
        tmp = path.with_name('.' + path.name + '.' + str(uuid.uuid4()))
        with tmp.open('xb') as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(tmp, path)
    fd = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)
    return dict(path=str(path), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))


def ref(path):
    return dict(path=str(path), sha256=sha(path))


def exact(item):
    need(sha(item['path']) == item['sha256'], 'immutable reference drift ' + item['path'])
    return read(item['path'])


def module(item, name):
    need(sha(item['path']) == item['sha256'], 'module drift ' + item['path'])
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


def authority():
    for unused in range(3):
        digest = sha(REG)
        registry, epoch = read(REG), read(EPOCH)
        if digest == sha(REG) == epoch['native_registry_sha256']:
            need(epoch['epoch'] == 2 and epoch['state'] == 'NATIVE_SCIENCE_ACTIVE', 'epoch inactive')
            need(epoch['holder'] == os.uname().nodename, 'native holder mismatch')
            return registry, epoch
    raise RuntimeError('authority snapshot changed; admission only HOLD')


def remaining(value):
    if 'remaining' in value:
        return value['remaining']
    spent = value.get('consumed', 0)
    return max(0, value.get('budget', 0) - (spent if type(spent) is int else len(spent)))


def transaction(operation, function):
    """Only this Goal's single request may change; all other science preserved."""
    with locked(NATIVE / 'control/science_authority/REGISTRY_UPDATE.lock'):
        registry, epoch = authority()
        previous = dict(registry_sha256=sha(REG), epoch_sha256=sha(EPOCH))
        peers = {key: copy.deepcopy(value) for key, value in registry['registered_future_requests'].items()
                 if key != GOAL}
        history = copy.deepcopy((registry['old_source_history'], registry['qualification_history']))
        top = {key: copy.deepcopy(value) for key, value in registry.items()
               if key not in ('registered_future_requests', 'new_scientific_budget_remaining')}
        for path in [REG, EPOCH]:
            archive = NATIVE / 'control/science_authority/request_history' / (path.stem + '.' + sha(path) + '.json')
            if not archive.exists():
                with archive.open('xb') as stream:
                    stream.write(path.read_bytes())
        result = function(registry)
        need({key: value for key, value in registry['registered_future_requests'].items() if key != GOAL} == peers,
             'foreign registry row changed')
        need((registry['old_source_history'], registry['qualification_history']) == history, 'old history changed')
        need({key: value for key, value in registry.items()
              if key not in ('registered_future_requests', 'new_scientific_budget_remaining')} == top,
             'protected registry field changed')
        registry['new_scientific_budget_remaining'] = sum(remaining(v) for v in registry['registered_future_requests'].values())
        put(REG, registry)
        epoch['native_registry_sha256'] = sha(REG)
        epoch['new_budget_remaining'] = registry['new_scientific_budget_remaining']
        epoch['request_revision'] = dict(request_id=GOAL, operation=operation, utc=now(), **previous)
        put(EPOCH, epoch)
        put(ROOT / 'control/authority_events' / (str(uuid.uuid4()) + '.json'),
            dict(goal=GOAL, operation=operation, utc=now(), previous=previous,
                 new_registry_sha256=sha(REG), new_epoch_sha256=sha(EPOCH), foreign_rows_preserved=True), True)
        return result


def publish_own_write_carrier(claims):
    """Caller holds own admission lock. No static historical pool is added."""
    future = sum(row['remaining_write_bytes'] for row in claims.values())
    window = max([read(ROOT/'cases'/case/'control/FROZEN_SPEC.json')['limits']['result_bytes']
                  for case in claims] or [0])
    reserve = future + window + (2*M if claims else 0)
    def publish(registry):
        registry['registered_future_requests'][GOAL]['reserved_write_bytes'] = reserve
    transaction('RECONCILE_REAL_REMAINING_WRITES_AND_ONE_RESTORE_WINDOW',publish)
    return reserve
