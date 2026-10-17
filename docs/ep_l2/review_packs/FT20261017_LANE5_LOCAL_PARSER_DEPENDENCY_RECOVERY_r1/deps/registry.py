"""Central, flock-serialized EP-L2 allocation; Git snapshots confer no ownership."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import socket
import tempfile
import time
import uuid

DEFAULT_ROOT = Path('/workspace/ep_l2_ft20261016_shared')
IDENTITY_FIELDS = {
    'core_source_commit', 'framework_source_commit', 'binary_sha256',
    'runtime_config_sha256', 'trace_content_sha256', 'workload', 'epoch_range',
    'feature_vector', 'ideal_vector', 'termination_contract',
}
ACTIVE = {'RESERVED', 'RUNNING'}
TERMINAL = {'COMPLETE_VALID', 'FAILED', 'TIMEOUT', 'RESOURCE_LIMIT', 'INCOMPLETE'}
R19 = 'EPL2_DOWNSTREAM_HEADROOM_R19'
PARALLEL = 'EPL2_PARALLEL_POTENTIAL_20261017_V1'
R19_DEADLINE = 1792256956
PARALLEL_ABSOLUTE_DEADLINE = 1792332000  # 2026-10-18 14:00:00 UTC
PARALLEL_PROFILES = {'B16_BANKED','U_WB16','B16_OFF','U_OFF','I_WB','I_META','I_WB_META','I_READ_HIT',
    'I_MEM_ALL_DATA','S64','U_CAP16','P2','ROP40_H0','L1_32_H0','ICNT2_H0',
    'WAD256_Q4','I_BANK','I_L2_SERVICE','NATIVE_OFF_CONTROL'}


def attempt_count(row):
    return 1 + len(row.get('attempt_history', []))


def now():
    return datetime.now(timezone.utc).isoformat()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=False, allow_nan=False).encode()


def run_key(identity):
    if set(identity) != IDENTITY_FIELDS:
        raise ValueError('incomplete/extra identity fields: ' + str(set(identity) ^ IDENTITY_FIELDS))
    for name in ('core_source_commit', 'framework_source_commit'):
        validate_hash(identity[name], 40)
    for name in ('binary_sha256', 'runtime_config_sha256', 'trace_content_sha256'):
        validate_hash(identity[name], 64)
    for name in ('feature_vector', 'ideal_vector', 'termination_contract'):
        if not isinstance(identity[name], dict) or not identity[name]:
            raise ValueError(name + ' must be an explicit nonempty object')
    if not isinstance(identity['epoch_range'], dict) or not identity['epoch_range']:
        raise ValueError('explicit epoch/full-application identity required')
    if not isinstance(identity['workload'], str) or not identity['workload']:
        raise ValueError('workload required')
    return hashlib.sha256(canonical(identity)).hexdigest()


def validate_hash(value, length):
    if not isinstance(value, str) or len(value) != length or any(c not in '0123456789abcdef' for c in value):
        raise ValueError('invalid content/source digest')


def write_json(path, value):
    path = Path(path)
    fd, name = tempfile.mkstemp(prefix='.' + path.name, dir=path.parent)
    try:
        with os.fdopen(fd, 'w') as stream:
            json.dump(value, stream, sort_keys=True, indent=2, allow_nan=False)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
        directory = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def local_resources():
    mem = {}
    for line in Path('/proc/meminfo').read_text().splitlines():
        key, value = line.split(':', 1)
        mem[key] = int(value.split()[0]) * 1024
    cap = Path('/sys/fs/cgroup/memory.max').read_text().strip()
    current = int(Path('/sys/fs/cgroup/memory.current').read_text())
    available = mem['MemAvailable']
    if cap != 'max':
        available = min(available, int(cap) - current)
    stat = os.statvfs('/workspace')
    return {'available_memory_bytes': available,
            'disk_free_bytes': stat.f_bavail * stat.f_frsize,
            'share_disk_free_bytes': os.statvfs('/root/share').f_bavail * os.statvfs('/root/share').f_frsize}


def process_identity(pid):
    # /proc stat field 22 survives pid reuse; commands can contain spaces/parentheses.
    stat = Path(f'/proc/{pid}/stat').read_text()
    fields = stat[stat.rfind(')') + 2:].split()
    return {'pid': pid, 'start_ticks': int(fields[19]),
            'boot_id': Path('/proc/sys/kernel/random/boot_id').read_text().strip()}


class Registry:
    def __init__(self, root=DEFAULT_ROOT):
        self.root = Path(root)

    @contextmanager
    def locked(self):
        # Refuse absent registry rather than initializing a second authority.
        if not (self.root / 'RUN_REGISTRY.json').is_file():
            raise ValueError('central registry missing; no implicit initialization')
        with (self.root / 'REGISTRY.lock').open('a+') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            data = json.loads((self.root / 'RUN_REGISTRY.json').read_text())
            if data['authority_host'] != socket.gethostname():
                raise ValueError('remote host must use central dispatcher; local registry is not cross-host lock')
            yield data
            data['updated_at'] = now()
            write_json(self.root / 'RUN_REGISTRY.json', data)

    def snapshot(self):
        with self.locked() as data:
            return json.loads(json.dumps(data))

    @staticmethod
    def admission(data, host, cpu, memory, scan, kind, resources):
        policy = data['hosts'][host]
        live = [r for r in data['runs'].values() if r['host'] == host and r['status'] in ACTIVE]
        leases = [r for r in data.get('resource_leases', {}).values()
                  if r['host'] == host and r['status'] in ACTIVE]
        all_live = live + leases
        if any(r.get('kind') == 'ENGINEERING_PILOT' for r in leases):
            raise ValueError('exclusive engineering pilot active; ordinary heavy admission blocked')
        if kind == 'simulation':
            if len(live) >= policy['max_simulators']:
                raise ValueError('shared simulator quota full')
            if policy['scan_exclusive'] and (scan and live or any(r['scan'] for r in live)):
                raise ValueError('scan needs exclusive EP-L2 simulator slot')
        if sum(r['cpu_units'] for r in all_live) + cpu > policy['max_cpu_units']:
            raise ValueError('shared CPU quota full')
        if sum(r['memory_bytes'] for r in all_live) + memory > policy['max_reserved_memory_bytes']:
            raise ValueError('shared memory reservation quota full')
        if resources['available_memory_bytes'] - memory < policy['min_available_memory_bytes']:
            raise ValueError('available memory safety floor')
        if resources['disk_free_bytes'] < policy['min_disk_free_bytes']:
            raise ValueError('workspace free-space safety floor')
        if resources.get('share_disk_free_bytes', 2**60) < 40 * 2**30:
            raise ValueError('Share free-space safety floor')
        if kind == 'build' and cpu > policy['max_build_jobs']:
            raise ValueError('build jobs exceed shared policy')

    def claim(self, identity, owner, result_directory, resources=None, cpu=1, memory=None, experiment=None, client_binding=None, retry_checkpoint=None):
        if owner not in {'lane1', 'lane2', 'lane3', 'lane4', 'lane5', 'lane6'}:
            raise ValueError('explicit lane owner required')
        if type(cpu) is not int or cpu < 1:
            raise ValueError('positive CPU allocation required')
        key = run_key(identity)
        host = socket.gethostname()
        with self.locked() as data:
            previous = data['runs'].get(key)
            if previous is not None and retry_checkpoint is None:
                return False, previous
            history = []
            if retry_checkpoint is not None:
                path=Path(retry_checkpoint['path'])
                if hashlib.sha256(path.read_bytes()).hexdigest()!=retry_checkpoint['sha256']:
                    raise ValueError('retry decision checkpoint changed')
                recovery=json.loads(path.read_text())
                if (previous is None or owner!='lane5' or previous['owner']!=owner
                    or previous['status'] not in {'FAILED','TIMEOUT','RESOURCE_LIMIT','INCOMPLETE'}
                    or previous['identity']!=identity or previous['lease_id']!=recovery.get('previous_lease_id')
                    or recovery.get('run_key')!=key or not recovery.get('engineering_reason')
                    or str(result_directory)!=recovery.get('new_result_directory')
                    or str(result_directory)==previous['result_directory']):
                    raise ValueError('retry requires exact failed terminal/owner/identity/new evidence directory')
                if (experiment is None and previous.get('experiment_id') is not None) or (experiment is not None and any(previous.get(k)!=v for k,v in experiment.items())):
                    raise ValueError('retry cannot change campaign, condition, cell or deadline')
                history=previous.get('attempt_history',[])+[{k:v for k,v in previous.items() if k!='attempt_history'}]
            if experiment is not None:
                self.check_experiment(data, experiment, identity, owner, retry_key=key if retry_checkpoint else None)
            policy = data['hosts'][host]
            if policy['boot_id'] != Path('/proc/sys/kernel/random/boot_id').read_text().strip():
                raise ValueError('host reboot: Lane 5 must reconcile preserved reservations')
            memory = memory if memory is not None else policy['default_run_memory_bytes']
            if type(memory) is not int or memory <= 0:
                raise ValueError('positive memory allocation required')
            self.admission(data, host, cpu, memory, identity['workload'] == 'scan',
                           'simulation', resources if resources is not None else local_resources())
            output_root = Path(result_directory).parent
            if output_root == Path('/workspace/ep_l2_potential20261017_lane5_results'):
                if (output_root.stat().st_dev != Path('/workspace').stat().st_dev or
                        output_root.stat().st_dev == Path('/root/share').stat().st_dev):
                    raise ValueError('new output must use actual workspace filesystem')
                stat = os.statvfs(output_root)
                pending_output = sum(policy['default_run_output_limit_bytes'] for r in data['runs'].values()
                    if r['status'] in ACTIVE and Path(r['result_directory']).parent == output_root)
                if stat.f_bavail * stat.f_frsize - pending_output - policy['default_run_output_limit_bytes'] < policy['min_disk_free_bytes']:
                    raise ValueError('workspace floor plus concurrent output growth budget')
            row = {'run_key': key, 'identity': identity, 'owner': owner, 'host': host,
                   'boot_id': policy['boot_id'], 'lease_id': uuid.uuid4().hex,
                   'status': 'RESERVED', 'created_at': now(), 'cpu_units': cpu,
                   'memory_bytes': memory, 'scan': identity['workload'] == 'scan',
                   'result_directory': str(result_directory), 'process': None}
            if retry_checkpoint is not None:
                row['attempt_history']=history
                row['retry_checkpoint']=retry_checkpoint
            if client_binding is not None: row['client_binding'] = json.loads(json.dumps(client_binding))
            if experiment is not None: row.update(experiment)
            data['runs'][key] = row
            return True, row

    def register_parallel_campaign(self, cells, authority_commit):
        """Exactly-once T0 under the existing lock. Never rewrite old runs/leases."""
        validate_hash(authority_commit, 40)
        if len(cells) != 50 or len({c['cell_id'] for c in cells}) != 50:
            raise ValueError('exact published 50 seed cells required')
        if any(c['experiment_id'] != PARALLEL for c in cells):
            raise ValueError('wrong seed campaign')
        with self.locked() as data:
            campaigns = data.setdefault('campaigns', {})
            if PARALLEL in campaigns:
                if campaigns[PARALLEL]['seed_cells'] != cells or campaigns[PARALLEL]['authority_commit'] != authority_commit:
                    raise ValueError('campaign immutable registration differs')
                return campaigns[PARALLEL]
            stamp = time.time()
            entry = {'experiment_id': PARALLEL, 't0_unix': stamp,
                'deadline_unix': min(stamp + 86400, PARALLEL_ABSOLUTE_DEADLINE),
                'maximum_starts': 72, 'seed_cells': cells, 'extra_cells': [],
                'authority_commit': authority_commit, 'registered_at': now()}
            campaigns[PARALLEL] = entry
            return entry

    def register_native_off_control(self, identity, checkpoint):
        """One explicit new-source all-OFF canary, charged to the new72 budget."""
        key = run_key(identity)
        proof = Path(checkpoint['path'])
        if hashlib.sha256(proof.read_bytes()).hexdigest() != checkpoint['sha256']:
            raise ValueError('canary selection checkpoint changed')
        with self.locked() as data:
            campaign = data.get('campaigns', {}).get(PARALLEL)
            if not campaign or time.time() >= campaign['deadline_unix']:
                raise ValueError('missing/expired new campaign')
            cell = {'cell_id':'E_NATIVE_OFF_LOCAL_R1','experiment_id':PARALLEL,
                    'mode':'NATIVE_OFF_CONTROL','condition':'H0',
                    'workload_alias':identity['workload'], 'expected_run_key':key,
                    'selection_checkpoint':checkpoint}
            old = next((c for c in campaign['extra_cells'] if c['cell_id']==cell['cell_id']),None)
            if old is not None:
                if old != cell: raise ValueError('canary registration cannot be rebound')
                return old
            if len(campaign['extra_cells']) >= 22:
                raise ValueError('additional cell budget exhausted')
            campaign['extra_cells'].append(cell)
            return cell

    @staticmethod
    def check_experiment(data, experiment, identity, owner, retry_key=None):
        base = {'experiment_id', 'regime', 'deadline_unix'}
        name = experiment.get('experiment_id')
        if owner != 'lane5':
            raise ValueError('full applications require Lane5 dispatcher')
        if name == R19:
            if (set(experiment) != base or experiment['regime'] not in {'Q4','D4','D2','D8','L25'}
                    or experiment['deadline_unix'] != R19_DEADLINE):
                raise ValueError('unknown or altered r19 experiment allocation')
            deadline, cap = R19_DEADLINE, 24
        elif name == PARALLEL:
            if set(experiment) != base | {'cell_id','profile'}:
                raise ValueError('explicit parallel cell/profile allocation required')
            campaign = data.get('campaigns', {}).get(PARALLEL)
            if not campaign or experiment['deadline_unix'] != campaign['deadline_unix']:
                raise ValueError('unregistered campaign or altered deadline')
            cell = next((c for c in campaign['seed_cells'] + campaign['extra_cells']
                if c['cell_id'] == experiment['cell_id']), None)
            if (not cell or experiment['profile'] not in PARALLEL_PROFILES
                    or cell['workload_alias'] != identity['workload']
                    or cell['condition'] != experiment['regime']
                    or cell['mode'] != experiment['profile']):
                raise ValueError('unknown or mismatched positive campaign cell')
            if cell.get('expected_run_key',run_key(identity)) != run_key(identity):
                raise ValueError('extra cell exact runtime identity differs')
            if any(r.get('experiment_id') == PARALLEL and r.get('cell_id') == experiment['cell_id'] and r.get('run_key') != retry_key
                    for r in data['runs'].values()):
                raise ValueError('cell already attempted; audited retry required')
            deadline, cap = campaign['deadline_unix'], campaign['maximum_starts']
        else:
            raise ValueError('unknown experiment allocation')
        if time.time() >= deadline:
            raise ValueError('bounded experiment deadline')
        if sum(attempt_count(r) for r in data['runs'].values() if r.get('experiment_id') == name) >= cap:
            raise ValueError('campaign full-application cap includes failed/reserved runs')

    def update(self, key, lease_id, status, **fields):
        if status not in TERMINAL | {'RUNNING'}:
            raise ValueError('invalid status')
        if set(fields) - {'process', 'exit_code', 'detail', 'raw_log_sha256', 'result_receipt_sha256'}:
            raise ValueError('identity/owner/resource mutation prohibited')
        with self.locked() as data:
            row = data['runs'][key]
            if row['lease_id'] != lease_id or row['status'] not in ACTIVE:
                raise ValueError('ownership mismatch or immutable terminal record')
            if status == 'RUNNING' and (row['status'] != 'RESERVED' or not fields.get('process')):
                raise ValueError('running needs the real process identity')
            row.update(fields)
            row.update(status=status, updated_at=now())

    def build_lease(self, owner, cpu=4, memory=8 * 1024**3):
        if owner not in {'lane1', 'lane2', 'lane3', 'lane4', 'lane5', 'lane6'}:
            raise ValueError('explicit lane owner required')
        if type(cpu) is not int or cpu < 1 or type(memory) is not int or memory < 1:
            raise ValueError('positive resource allocation required')
        host = socket.gethostname()
        with self.locked() as data:
            self.admission(data, host, cpu, memory, False, 'build', local_resources())
            key = uuid.uuid4().hex
            data['resource_leases'][key] = {'host': host, 'owner': owner, 'cpu_units': cpu,
                'memory_bytes': memory, 'status': 'RESERVED', 'created_at': now()}
            return key

    def release_build(self, key, owner):
        with self.locked() as data:
            row = data['resource_leases'][key]
            if row.get('kind') == 'ENGINEERING_PILOT':
                raise ValueError('engineering pilot requires its audited release path')
            if row['owner'] != owner or row['status'] != 'RESERVED':
                raise ValueError('build lease ownership/state mismatch')
            row.update(status='RELEASED', updated_at=now())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=DEFAULT_ROOT)
    sub = parser.add_subparsers(dest='action', required=True)
    sub.add_parser('snapshot')
    key = sub.add_parser('key')
    key.add_argument('identity', type=Path)
    build = sub.add_parser('build-claim')
    build.add_argument('--owner', required=True)
    build.add_argument('--jobs', type=int, default=4)
    release = sub.add_parser('build-release')
    release.add_argument('--owner', required=True)
    release.add_argument('lease_id')
    args = parser.parse_args()
    registry = Registry(args.root)
    if args.action == 'key':
        print(run_key(json.loads(args.identity.read_text())))
    elif args.action == 'build-claim':
        print(registry.build_lease(args.owner, cpu=args.jobs))
    elif args.action == 'build-release':
        registry.release_build(args.lease_id, args.owner)
    else:
        print(json.dumps(registry.snapshot(), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
