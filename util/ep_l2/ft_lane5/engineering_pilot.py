"""One-use engineering admission. No compiler launch; ordinary admission unchanged.

Lane5 publishes an APPROVED_ENGINEERING_ONLY authorization before register().
Lane1 calls claim -> repeated monitor -> release in finally. No source amendment
is implicit; changed pins stop and require a separately audited campaign update.
"""
import ast
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import signal
import socket
import subprocess
import time
import uuid

from registry import Registry, DEFAULT_ROOT, ACTIVE, canonical, local_resources, process_identity, validate_hash
from run import process_tree_rss

AUTHORITY = '56a0517d3a5941a0a870b50e8c915a8a36b9ee5d'
SCHEMA = 'EPL2_ENGINEERING_PILOT_AUTHORIZATION_V1'
BRANCH = 'refs/heads/hrl/ep-l2-ft20261016-lane5-v1'
PINS = {'core_source_commit': 40, 'framework_source_commit': 40, 'vendor_commit': 40,
        'driver_sha256': 64, 'build_entry_sha256': 64, 'repair_commands_sha256': 64}
BUDGET = ('entry_free_bytes', 'hard_stop_free_bytes', 'max_pilot_allocated_growth_bytes',
          'external_write_reserve_bytes', 'monitor_and_kill_overshoot_bytes',
          'minimum_untouched_emergency_bytes')
GIB = 1024**3


def require(ok, text):
    if not ok:
        raise ValueError(text)


def sha(value):
    return hashlib.sha256(value).hexdigest()


def positive(value):
    return type(value) is int and value > 0


def filesystem(path):
    p = Path(path).resolve()
    st, v = p.stat(), os.statvfs(p)
    records = []
    for line in Path('/proc/self/mountinfo').read_text().splitlines():
        fields = line.split()
        mount = fields[4].replace('\\040', ' ')
        if p == Path(mount) or Path(mount) in p.parents:
            records.append((len(mount), line))
    require(bool(records), 'filesystem mount identity unavailable')
    return {'device': st.st_dev, 'mount_signature': sha(max(records)[1].encode()),
            'available_bytes': v.f_bavail * v.f_frsize}


def allocated(path):
    p = Path(path)
    if not p.exists():
        return 0
    require(not p.is_symlink(), 'pilot output root became a symlink')
    total, seen = 0, set()
    for current, dirs, files in os.walk(p, followlinks=False):
        for name in [Path(current), *(Path(current)/n for n in dirs+files)]:
            st = name.lstat()
            key = st.st_dev, st.st_ino
            if key not in seen:
                seen.add(key)
                total += st.st_blocks * 512
    return total


def protected_inventory():
    result = []
    for path in Path('/proc').iterdir():
        if not path.name.isdigit():
            continue
        try:
            exe, cwd = os.readlink(path/'exe'), os.readlink(path/'cwd')
            text = (exe+' '+cwd).lower()
            if any(k in text for k in ('dtc','c16','decoupled-l1')):
                result.append(process_identity(int(path.name)))
        except (OSError,ValueError):
            continue
    return sorted(result,key=lambda r:r['pid'])


def measure_execution_identity(locations):
    pins = {}
    for field, location in (('core_source_commit','core_repo'),('framework_source_commit','framework_repo'),('vendor_commit','vendor_repo')):
        repo = Path(locations[location]).resolve(strict=True)
        pins[field] = subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True,timeout=1).strip()
        dirty = subprocess.check_output(['git','status','--porcelain','--untracked-files=no','--ignore-submodules=all'],cwd=repo,timeout=1)
        require(not dirty, 'tracked producing source/vendor changed')
    for field, location in (('driver_sha256','driver_path'),('build_entry_sha256','build_entry_path')):
        pins[field] = sha(Path(locations[location]).read_bytes())
    source = Path(locations['repair_commands_path']).read_text()
    functions = [n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name == 'repair_commands']
    require(len(functions)==1, 'ambiguous original repair_commands')
    pins['repair_commands_sha256'] = sha(ast.get_source_segment(source,functions[0]).encode())
    return pins


def sample_live(auth):
    before = time.monotonic()
    disks = {key: filesystem(v['probe_path']) for key,v in auth['filesystems'].items()}
    growth = {key: 0 for key in disks}
    for item in auth['output_roots']:
        growth[item['filesystem']] += allocated(item['path'])
    protected_known = protected_inventory() == sorted(auth['protected_processes'],key=lambda r:r['pid'])
    actual_identity = measure_execution_identity(auth['execution_locations'])
    return {'host': socket.gethostname(), 'boot_id': Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
        'mount_namespace': os.readlink('/proc/self/ns/mnt'), 'resources': local_resources(),
        'filesystems': disks, 'allocated_growth_bytes': growth, 'external_health_known': protected_known,
        'sample_seconds': time.monotonic()-before, 'pilot_rss_bytes':process_tree_rss(os.getpid()),
        'actual_execution_identity':actual_identity}


def verify_publication(auth, publication):
    repo = Path(__file__).resolve().parents[3]
    validate_hash(publication['commit'], 40)
    path = Path(publication['path'])
    require(not path.is_absolute() and '..' not in path.parts and
            str(path).startswith('docs/ep_l2/') and path.name == 'LOW_SPACE_PILOT_AUTHORIZATION.json',
            'unsafe authorization publication path')
    url = 'git@github.com:swayhrl/accel-sim-framework.git'
    live = subprocess.check_output(['git','ls-remote','--exit-code',url,BRANCH], timeout=30, text=True).split()
    require(live == [publication['commit'], BRANCH], 'authorization is not current Lane5 GitHub authority')
    raw = subprocess.check_output(['git','show',publication['commit']+':'+str(path)], cwd=repo, timeout=30)
    require(sha(raw) == publication['sha256'] and json.loads(raw) == auth,
            'forged or changed authorization publication')
    request_path = Path(auth['request']['path'])
    require(not request_path.is_absolute() and '..' not in request_path.parts and
            str(request_path).startswith('docs/ep_l2/') and request_path.name == 'LOW_SPACE_PILOT_REQUEST.json',
            'unsafe Lane1 request publication path')
    request_raw = subprocess.check_output(['git','show',auth['request']['publication_commit']+':'+str(request_path)], cwd=repo, timeout=30)
    require(sha(request_raw) == auth['request']['sha256'], 'published Lane1 request bytes changed')


def validate(auth, request_bytes):
    require(auth.get('schema_version') == SCHEMA and auth.get('status') == 'APPROVED_ENGINEERING_ONLY',
            'not an approved engineering authorization')
    require(auth.get('issuer') == 'lane5' and auth.get('authority_commit') == AUTHORITY,
            'wrong authorization issuer/scope')
    require(bool(re.fullmatch(r'[A-Za-z0-9_-]{8,128}', auth['pilot_id'])), 'invalid pilot ID')
    validate_hash(auth['token'], 64)
    require(auth['request']['sha256'] == sha(request_bytes), 'request bytes mismatch')
    validate_hash(auth['request']['publication_commit'], 40)
    request = json.loads(request_bytes)
    for field in ('pilot_id','host','boot_id','execution_identity','execution_locations','output_roots'):
        require(request[field] == auth[field], 'request/authorization mismatch: '+field)
    for name,n in PINS.items():
        validate_hash(auth['execution_identity'][name], n)
    for location in ('core_repo','framework_repo','vendor_repo','driver_path','build_entry_path','repair_commands_path'):
        require(Path(auth['execution_locations'][location]).is_absolute(), 'absolute producing input locations required')
    require(auth['cpu_units'] == request['cpu_units'] == 2 and
            auth['memory_bytes'] == request['memory_bytes'] == 8*GIB,
            'pilot must reserve exactly2CPU/8GiB')
    require(positive(auth['max_duration_seconds']) and auth['max_duration_seconds'] <= request['max_duration_seconds'],
            'invalid/unbounded campaign duration')
    require(0 < auth['monitor_interval_seconds'] <= 2 and 0 < auth['term_grace_seconds'] <= 3,
            'invalid monitor/stop interval')
    require(type(auth['issued_at_unix']) in (int,float) and type(auth['expires_at_unix']) in (int,float) and
            auth['expires_at_unix'] > auth['issued_at_unix'], 'invalid authorization TTL')
    require(auth.get('scientific_use') == 'FORBIDDEN_ENGINEERING_EVIDENCE_ONLY', 'scientific promotion prohibited')
    require(bool(auth['filesystems']) and bool(auth['output_roots']), 'missing write filesystem accounting')
    require(auth.get('external_inventory_complete') is True and type(auth.get('protected_processes')) is list,
            'missing independently reviewed external inventory')
    devices = set()
    for key,b in auth['filesystems'].items():
        require(type(b['device']) is int and b['device'] not in devices, 'filesystem aliases must share one budget')
        devices.add(b['device']); validate_hash(b['mount_signature'], 64)
        require(all(positive(b[n]) for n in BUDGET), 'all per-filesystem budget terms must be positive integers')
        total = sum(b[n] for n in BUDGET[2:])
        require(b['entry_free_bytes'] >= total, 'pilot envelope does not close')
        require(b['hard_stop_free_bytes'] >= b['minimum_untouched_emergency_bytes'] + b['monitor_and_kill_overshoot_bytes'] and
                b['entry_free_bytes'] > b['hard_stop_free_bytes'], 'unsafe hard-stop reserve')
        require(bool(b.get('evidence')), 'each filesystem needs independently reviewed budget evidence')
    roots = []
    for root in auth['output_roots']:
        p = Path(root['path'])
        require(p.is_absolute() and '..' not in p.parts and root['filesystem'] in auth['filesystems'], 'invalid output root')
        resolved = p.resolve()
        require(not any(resolved == q or resolved in q.parents or q in resolved.parents for q in roots),
                'overlapping output roots double-count growth')
        roots.append(resolved)
    return request


def terminate_owned(process, expected, grace_seconds=1):
    """Only an actual caller-owned child session leader with exact PID identity."""
    require(process.pid != os.getpid() and 0 < grace_seconds <= 3, 'invalid owned process')
    if process.poll() is not None:
        return process.returncode
    require(process_identity(process.pid) == expected and os.getpgid(process.pid) == process.pid,
            'process identity/group mismatch; refuse unrelated signal')
    os.killpg(process.pid, signal.SIGTERM)
    try:
        return process.wait(timeout=grace_seconds)
    except subprocess.TimeoutExpired:
        if process.poll() is None:
            require(process_identity(process.pid) == expected, 'PID changed during stop')
            os.killpg(process.pid, signal.SIGKILL)
        return process.wait(timeout=3)


class PilotRegistry:
    def __init__(self, root=DEFAULT_ROOT, *, sampler=None, publication_verifier=None, clock=None):
        require(Path(root).resolve() != DEFAULT_ROOT.resolve() or
                (sampler is None and publication_verifier is None and clock is None),
                'test dependency injection prohibited for real central registry')
        self.registry = Registry(root)
        self.sample = sampler or sample_live
        self.published = publication_verifier or verify_publication
        self.clock = clock or time.time

    def register(self, auth, request_bytes, publication):
        validate(auth, request_bytes)
        self.published(auth, publication)  # bounded network read outside permanent lock
        require(auth['issued_at_unix'] <= self.clock() < auth['expires_at_unix'], 'expired/not-yet-issued authorization')
        with self.registry.locked() as data:
            records = data.setdefault('engineering_pilots', {})
            require(auth['pilot_id'] not in records, 'pilot ID already registered')
            require(not any(r['authority_commit'] == AUTHORITY for r in records.values()), 'one r8 campaign already registered')
            self._guard(data, auth, self.sample(auth), entry=True)
            require(auth['issued_at_unix'] <= self.clock() < auth['expires_at_unix'], 'authorization expired during registration')
            records[auth['pilot_id']] = {'status':'ISSUED','authority_commit':AUTHORITY,
                'authorization_sha256':sha(canonical(auth)), 'request_sha256':sha(request_bytes),
                'token_sha256':sha(auth['token'].encode()), 'publication':publication, 'consumed':False}

    def _guard(self, data, auth, live, entry):
        policy = data['hosts'][data['authority_host']]
        require(live['host'] == data['authority_host'] == auth['host'] and
                live['boot_id'] == policy['boot_id'] == auth['boot_id'], 'wrong host/boot')
        require(live['mount_namespace'] == auth['mount_namespace'], 'mount namespace changed')
        require(live['external_health_known'], 'protected project state unknown')
        require(live['actual_execution_identity'] == auth['execution_identity'], 'actual source/driver/vendor changed')
        require(live['sample_seconds'] <= auth['monitor_interval_seconds'], 'cannot maintain monitor deadline')
        require(live['pilot_rss_bytes'] <= auth['memory_bytes'], 'pilot process-tree memory cap')
        require(auth['cpu_units'] <= policy['max_build_jobs'] and auth['cpu_units'] <= policy['max_cpu_units'] and
                auth['memory_bytes'] <= policy['max_reserved_memory_bytes'], 'shared CPU/memory quota exceeded')
        require(live['resources']['available_memory_bytes'] - auth['memory_bytes'] >= policy['min_available_memory_bytes'],
                'available memory after pilot reservation below original floor')
        for name,b in auth['filesystems'].items():
            actual = live['filesystems'][name]
            require(actual['device'] == b['device'] and actual['mount_signature'] == b['mount_signature'], 'write filesystem changed')
            threshold = b['entry_free_bytes'] if entry else b['hard_stop_free_bytes']
            require(actual['available_bytes'] > threshold if not entry else actual['available_bytes'] >= threshold,
                    'pilot entry/stop free-space limit: '+name)
            require(live['allocated_growth_bytes'][name] < b['max_pilot_allocated_growth_bytes'], 'pilot allocated growth cap: '+name)
        if entry:
            require(live['resources']['disk_free_bytes'] < policy['min_disk_free_bytes'] + 2*GIB,
                    'formal build headroom reached; cancel pilot and use sole formal entry')
            require(not any(r['status'] in ACTIVE for r in data['runs'].values()) and
                    not any(r['status'] in ACTIVE for r in data.get('resource_leases', {}).values()),
                    'competing EP-L2 run/build/scan lease')
        if not entry:
            require(not any(r['status'] in ACTIVE for r in data['runs'].values()) and
                    not any(r['status'] in ACTIVE and (r.get('kind') != 'ENGINEERING_PILOT' or
                        r.get('pilot_id') != auth['pilot_id']) for r in data.get('resource_leases',{}).values()),
                    'competing heavy allocation appeared during pilot')
        for root in auth['output_roots']:
            path = Path(root['path'])
            require(str(path.resolve()) == root['resolved_path'], 'output path resolution changed')
            parent = path
            while not parent.exists():
                parent = parent.parent
            require(parent.stat().st_dev == auth['filesystems'][root['filesystem']]['device'], 'output root on wrong filesystem')
            if entry:
                require(not path.exists() and not path.is_symlink(), 'pilot needs fresh non-symlink roots')

    def claim(self, auth, request_bytes, execution_identity):
        validate(auth, request_bytes)
        require(execution_identity == auth['execution_identity'], 'wrong actual source/driver/vendor pins')
        now = self.clock()
        require(auth['issued_at_unix'] <= now < auth['expires_at_unix'], 'expired/not-yet-issued authorization')
        with self.registry.locked() as data:
            record = data.get('engineering_pilots', {}).get(auth['pilot_id'])
            require(record and record['status'] == 'ISSUED' and not record['consumed'], 'unknown or replayed pilot token')
            require(record['authorization_sha256'] == sha(canonical(auth)) and
                    record['request_sha256'] == sha(request_bytes) and
                    secrets.compare_digest(record['token_sha256'],sha(auth['token'].encode())), 'forged authorization/token')
            live = self.sample(auth); self._guard(data, auth, live, entry=True)
            now = self.clock()
            require(auth['issued_at_unix'] <= now < auth['expires_at_unix'], 'authorization expired during claim')
            mono = time.monotonic()
            key = uuid.uuid4().hex
            row = {'kind':'ENGINEERING_PILOT','host':auth['host'],'boot_id':auth['boot_id'],
                'owner':'lane1','cpu_units':2,'memory_bytes':8*GIB,'status':'RESERVED',
                'pilot_id':auth['pilot_id'],'lease_id':key,'owner_process':process_identity(os.getpid()),
                'created_at_unix':now,'last_monitor_unix':now,'last_monitor_monotonic':mono,
                'deadline_monotonic':mono+min(auth['expires_at_unix']-now,auth['max_duration_seconds']),
                'deadline_unix':min(auth['expires_at_unix'], now+auth['max_duration_seconds']),
                'entry_available_bytes':{k:v['available_bytes'] for k,v in live['filesystems'].items()}}
            data['resource_leases'][key] = row
            record.update(status='RESERVED',consumed=True,lease_id=key,claimed_at_unix=now)
            return key

    def attach_process(self, key, auth, child):
        require(child.poll() is None and os.getpgid(child.pid) == child.pid, 'child must be a live separate session')
        fields = Path(f'/proc/{child.pid}/stat').read_text().split(') ',1)[1].split()
        require(int(fields[1]) == os.getpid(), 'process is not a direct caller-owned child')
        with self.registry.locked() as data:
            row = data['resource_leases'][key]; record = data['engineering_pilots'][row['pilot_id']]
            require(row.get('kind') == 'ENGINEERING_PILOT' and row['status'] in ACTIVE and
                    row['owner_process'] == process_identity(os.getpid()) and
                    record['authorization_sha256'] == sha(canonical(auth)), 'attach process ownership mismatch')
            require(not row.get('stop_latched'), 'pilot stop already latched')
            require(self.clock() <= row['deadline_unix'] and time.monotonic() <= row['deadline_monotonic'], 'pilot deadline expired')
            require(not self._identity_alive(row.get('child_process')), 'previous pilot command still active')
            ident = process_identity(child.pid)
            row.update(status='RUNNING', child_process=ident)
            row.setdefault('child_history',[]).append(ident)
            record['status'] = 'RUNNING'

    @staticmethod
    def _identity_alive(ident):
        if not ident:
            return False
        try:
            return process_identity(ident['pid']) == ident and Path(f"/proc/{ident['pid']}/stat").read_text().split(') ',1)[1].split()[0] != 'Z'
        except (OSError, ValueError):
            return False

    def monitor(self, key, auth):
        """Return STOP reasons; Lane1 must stop its own child on any exception too."""
        with self.registry.locked() as data:
            row = data['resource_leases'][key]
            record = data['engineering_pilots'][row['pilot_id']]
            require(row.get('kind') == 'ENGINEERING_PILOT' and row['status'] in ACTIVE and
                    row['owner_process'] == process_identity(os.getpid()) and
                    record['authorization_sha256'] == sha(canonical(auth)), 'pilot monitor ownership/authorization mismatch')
            reasons = ['previous STOP latched'] if row.get('stop_latched') else []
            now = self.clock()
            if now > row['deadline_unix'] or time.monotonic() > row['deadline_monotonic']: reasons.append('campaign/authorization deadline')
            if now-row['last_monitor_unix'] > auth['monitor_interval_seconds']: reasons.append('monitor heartbeat deadline')
            live = self.sample(auth)
            mono = time.monotonic()
            if mono-row['last_monitor_monotonic'] > auth['monitor_interval_seconds']: reasons.append('monotonic monitor deadline')
            try:
                self._guard(data,auth,live,entry=False)
            except (ValueError,KeyError,OSError) as e:
                reasons.append(str(e))
            for name,b in auth['filesystems'].items():
                external = max(0,row['entry_available_bytes'][name]-live['filesystems'][name]['available_bytes']-
                                  live['allocated_growth_bytes'][name])
                if external > b['external_write_reserve_bytes']: reasons.append('external reserve exhausted: '+name)
            row.update(last_monitor_unix=now,last_monitor_monotonic=mono,last_observation=live,
                last_stop_reasons=reasons,stop_latched=bool(reasons))
            return {'stop':bool(reasons),'reasons':reasons,'observation':live}

    def release(self, key, auth, terminal, receipt_sha256):
        require(terminal == 'COMPLETE_ENGINEERING_ONLY' or terminal.startswith('PILOT_STOPPED_'), 'invalid engineering terminal')
        validate_hash(receipt_sha256,64)
        with self.registry.locked() as data:
            row = data['resource_leases'][key]; record = data['engineering_pilots'][row['pilot_id']]
            require(row.get('kind') == 'ENGINEERING_PILOT' and row['status'] in ACTIVE and
                    row['owner_process'] == process_identity(os.getpid()) and
                    record['authorization_sha256'] == sha(canonical(auth)), 'pilot release ownership/state mismatch')
            require(terminal != 'COMPLETE_ENGINEERING_ONLY' or not row.get('stop_latched'), 'stopped pilot cannot report engineering success')
            require(not self._identity_alive(row.get('child_process')), 'cannot release while owned pilot child is active')
            row.update(status='RELEASED',terminal=terminal,receipt_sha256=receipt_sha256,released_at_unix=self.clock())
            record.update(status=terminal,consumed=True,receipt_sha256=receipt_sha256)

    def reconcile_dead_owner(self, key, recovery_receipt_sha256):
        """Explicit Lane5 recovery after evidence review; never kill or auto-reclaim."""
        validate_hash(recovery_receipt_sha256,64)
        with self.registry.locked() as data:
            row = data['resource_leases'][key]
            require(row.get('kind') == 'ENGINEERING_PILOT' and row['status'] in ACTIVE, 'not an active pilot lease')
            require(not self._identity_alive(row.get('owner_process')) and
                    not self._identity_alive(row.get('child_process')), 'owner/child still active; no automatic reclamation')
            row.update(status='RELEASED',terminal='PILOT_STOPPED_OWNER_LOST',recovery_receipt_sha256=recovery_receipt_sha256)
            data['engineering_pilots'][row['pilot_id']].update(status='PILOT_STOPPED_OWNER_LOST',consumed=True,
                recovery_receipt_sha256=recovery_receipt_sha256)
