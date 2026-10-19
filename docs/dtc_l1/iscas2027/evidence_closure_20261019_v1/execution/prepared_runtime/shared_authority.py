"""PREPARED_NOT_TESTED. Minimal exact-role and peer view for frozen AG4 review.

No process creation, signal, lock, matrix or dispatch APIs. The caller must bind
this source, the frozen legacy reviewer, exact role contracts and registered
peer guard instances before use. Removing a recognized control from the legacy
classification view NEVER removes it from the all-project resource snapshot.
"""
import hashlib
import json
import os
from pathlib import Path
import time

CONFIRM_SECONDS = 2.0

class AuthorityReject(ValueError):
    pass

def require(value, reason):
    if not value:
        raise AuthorityReject(reason)

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def fresh_process(pid, identity_reader):
    """Read current control attributes between two instance identity checks."""
    before = identity_reader(pid)
    q = Path('/proc') / str(pid)
    row = dict(before, argv=[v.decode(errors='surrogateescape') for v in
                   (q / 'cmdline').read_bytes().split(b'\0') if v],
               cwd=os.readlink(q / 'cwd'), exe=os.readlink(q / 'exe'))
    after = identity_reader(pid)
    require(before['start_ticks'] == after['start_ticks'] and after['state'] != 'Z',
            'CPU_ROLE_INSTANCE_CHANGED_DURING_READ')
    return row

def exact_cpu_role(process, roles, identity_reader, process_reader=None):
    """Match fresh executable, argv, cwd, source closure and current instance.

    The saved snapshot is only a candidate. Re-read all mutable process fields
    before accepting; matching a PID/start_ticks alone cannot freeze an exec.
    process_reader is an explicit declared-fixture adapter in offline tests.
    """
    matches = []
    for role in roles:
        if process.get('argv') not in role['argvs'] or process.get('cwd') != role['cwd'] or process.get('exe') != role['executable']:
            continue
        fresh = (process_reader(process['pid']) if process_reader else
                 fresh_process(process['pid'], identity_reader))
        require(fresh['start_ticks'] == process['start_ticks'], 'CPU_ROLE_PID_REUSED')
        require(fresh['state'] != 'Z', 'CPU_ROLE_ALREADY_TERMINAL')
        require(fresh.get('argv') in role['argvs'] and fresh.get('cwd') == role['cwd'] and
                fresh.get('exe') == role['executable'], 'CPU_ROLE_CURRENT_ATTRIBUTES_CHANGED')
        require(sha(role['executable']) == role['executable_sha256'], 'CPU_ROLE_EXECUTABLE_CHANGED')
        for path, digest in role['source_sha256'].items():
            require(sha(path) == digest, 'CPU_ROLE_SOURCE_CHANGED:' + path)
        matches.append(role['name'])
    require(len(matches) <= 1, 'AMBIGUOUS_EXACT_CPU_ROLE')
    return matches[0] if matches else None

class SharedOwnership:
    """Event-confirmed local ownership plus exact registered peer snapshots.

    Every peer must already have its guard executable/argv/source/launch identity
    checked by the caller. Fresh stat/status identity is still required here.
    A stopped tracee of a registered guard lacking parent-event confirmation is
    PENDING for at most2s, never CONFIRMED or authority PASS. This view cannot
    authorize a signal, resume or process adoption in the local guard.
    """
    def __init__(self, local, identity_reader, monotonic=time.monotonic):
        self.local = local
        self.identity = identity_reader
        self.monotonic = monotonic
        self.peers = []
        self.waiting = {}

    def update_peers(self, peers):
        guards = set()
        for peer in peers:
            key = (peer['guard']['pid'], peer['guard']['start_ticks'])
            require(key not in guards, 'DUPLICATE_PEER_GUARD')
            require(peer['registered_source_and_launch_verified'] is True,
                    'PEER_REGISTRATION_NOT_VERIFIED')
            guards.add(key)
        self.peers = peers

    @property
    def pending(self):
        peers = [p['ownership']['pending'] for p in self.peers if p['ownership']['pending']]
        return dict(local=self.local.pending, shared=self.waiting, peers=peers) if self.local.pending or self.waiting or peers else {}

    def classify(self, process):
        pid = process['pid']
        live = self.identity(pid)
        require(live['start_ticks'] == process['start_ticks'], 'SHARED_PROCESS_PID_REUSED')
        if pid in self.local.confirmed or live['tracer_pid'] == self.local.tracer:
            return self.local.classify(process)
        for peer in self.peers:
            guard = peer['guard']
            current = self.identity(guard['pid'])
            require(current['start_ticks'] == guard['start_ticks'], 'SHARED_GUARD_PID_REUSED')
            require(current['state'] != 'Z', 'SHARED_GUARD_TERMINAL')
            if live['tracer_pid'] != guard['pid']:
                continue
            require(peer['age_seconds'] <= CONFIRM_SECONDS, 'PEER_OWNERSHIP_SNAPSHOT_STALE')
            key = (pid, live['start_ticks'])
            confirmed = next((r for r in peer['ownership']['confirmed'] if r['pid'] == pid), None)
            if confirmed:
                require(confirmed['start_ticks'] == live['start_ticks'], 'PEER_CONFIRMED_PID_REUSED')
                require(confirmed['tracer_pid'] == guard['pid'], 'PEER_CONFIRMED_TRACER_CHANGED')
                require(confirmed['tgid'] == live['tgid'], 'PEER_CONFIRMED_THREAD_GROUP_CHANGED')
                require(not any(r['pid'] == pid and r['start_ticks'] == live['start_ticks']
                                for r in peer['ownership'].get('retired', [])),
                        'PEER_RETIRED_INSTANCE_NOT_DISPATCHABLE')
                self.waiting.pop(key, None)
                return 'CONFIRMED'
            # Parent-event proof is absent. Merely knowing the tracer cannot
            # promote the process; the unchanged legacy reviewer sees pending.
            require(live['state'] in ('t', 'T'), 'UNCONFIRMED_PEER_NOT_STOPPED')
            first = self.waiting.setdefault(key, self.monotonic())
            require(self.monotonic() - first <= CONFIRM_SECONDS,
                    'SHARED_PARENT_EVENT_CONFIRMATION_TIMEOUT')
            return 'PENDING'
        return 'UNKNOWN'

    def close_absent_pending(self):
        """Drop only freshly absent/changed instances; never signal them."""
        for key in list(self.waiting):
            try:
                live = self.identity(key[0])
            except FileNotFoundError:
                self.waiting.pop(key)
                continue
            if live['start_ticks'] != key[1] or live['state'] == 'Z':
                self.waiting.pop(key)


def review_with_exact_roles(snapshot, legacy_review, own_owner, ownership,
                            roles, identity_reader, legacy_pack, legacy_output_sources=None,
                            process_reader=None, external_launch_view=None,
                            require_external_launch_binding=False, callback_sample_id=None):
    """Delegate unchanged history/FLOCK checks after exact current-role binding.

    legacy_review must be the published source-bound AG4 review function. Reject
    controls under its retired pack first, so its old pack-prefix own exception
    cannot confer execution authority to a new or restarted AG4 control.
    """
    ownership.close_absent_pending()
    accepted = []
    terminal_external = []
    retained = []
    retired = Path(legacy_pack).resolve()
    legacy_sources = legacy_output_sources or {}
    legacy_names = {Path(p).name for p in legacy_sources}
    for process in snapshot['processes']:
        try:
            role = exact_cpu_role(process, roles, identity_reader, process_reader)
        except (FileNotFoundError, ProcessLookupError):
            # A vanished snapshot row confers no live observation. Current
            # processes/resources remain in the untouched original snapshot.
            try:
                fresh = identity_reader(process['pid'])
            except (FileNotFoundError, ProcessLookupError):
                continue
            require(fresh['start_ticks'] == process['start_ticks'], 'CPU_ROLE_PID_REUSED')
            require(fresh['state'] == 'Z', 'CPU_ROLE_DISAPPEARED_BUT_STILL_LIVE')
            continue
        if role:
            require(not process['is_simulator'], 'CPU_ROLE_CANNOT_BE_SIMULATOR')
            from external_cpu_launch_view import ROLE_NAMES
            if require_external_launch_binding and role in ROLE_NAMES:
                require(external_launch_view is not None, 'EXTERNAL_CPU_ROLE_WITHOUT_ADMITTED_DIRECT_LAUNCH')
                observation = dict(external_launch_view.observe(role, process,
                                      callback_sample_id=callback_sample_id))
                if observation['live_observation']:
                    accepted.append(observation)
                else:
                    # A missing manager cannot make a still-live worker vanish.
                    try:
                        current = identity_reader(process['pid'])
                    except (FileNotFoundError, ProcessLookupError):
                        current = None
                    require(current is None or current['state'] == 'Z',
                            'EXTERNAL_MANAGER_NOT_CURRENT_WITH_LIVE_CPU_ROLE')
                    terminal_external.append(observation)
                continue
            accepted.append({'role': role, 'pid': process['pid'],
                             'start_ticks': process['start_ticks'],
                             'classification': 'EXACT_REGISTERED_CPU_CONTROL_ONLY'})
            continue
        for argument in process.get('argv', []):
            if '\n' in argument or not argument.endswith(('.py', '.sh')):
                continue
            path = Path(argument)
            if not path.is_absolute():
                path = Path(process['cwd']) / path
            resolved = str(path.resolve())
            if path.name in legacy_names:
                require(resolved in legacy_sources, 'LEGACY_HELPER_BASENAME_IS_NOT_PATH_AUTHORITY')
                require(sha(resolved) == legacy_sources[resolved], 'LEGACY_HELPER_SOURCE_CHANGED')
            if path.resolve().is_relative_to(retired):
                raise AuthorityReject('RETIRED_AG4_PACK_IS_NOT_NEW_CONTROL_AUTHORITY')
        retained.append(process)
    classified = dict(snapshot, processes=retained)
    owner_for_lock = {k: own_owner[k] for k in ['pid', 'start_ticks']} if own_owner else None
    result = legacy_review(classified, owner_for_lock, ownership)
    # No filtered resource snapshot is returned to the resource policy.
    return dict(result, exact_external_CPU_controls=accepted,
                terminal_external_CPU_controls=terminal_external,
                all_project_resource_population_unchanged=True,
                original_process_count=len(snapshot['processes']),
                classification_process_count=len(retained),
                simulation_permission_from_CPU_roles=False)


def verified_peer_view(launch, active_path, expected_request_sha256,
                       expected_guard_argv, expected_guard_executable_sha256,
                       source_sha256, process_reader, identity_reader, now_ns):
    """Bind an own-manager launch to a fresh source-bound guard observation.

    launch must come from the current sole coordinator's direct Popen instance
    registration, never discovery by basename/PPID. Expected request, argv and
    source hashes come from the immutable published CPU/family contract.
    """
    require(launch['request_sha256'] == expected_request_sha256, 'PEER_REQUEST_CHANGED')
    observed = process_reader(launch['pid'])
    require(observed['start_ticks'] == launch['start_ticks'], 'PEER_LAUNCH_PID_REUSED')
    require(observed['argv'] == expected_guard_argv, 'PEER_GUARD_ARGV_CHANGED')
    require(sha(observed['exe']) == expected_guard_executable_sha256, 'PEER_GUARD_ELF_CHANGED')
    for path, digest in source_sha256.items():
        require(sha(path) == digest, 'PEER_GUARD_SOURCE_CHANGED:' + path)
    current = identity_reader(launch['pid'])
    require(current['start_ticks'] == launch['start_ticks'] and current['state'] != 'Z',
            'PEER_GUARD_NOT_CURRENT_LIVE_INSTANCE')
    # The producer replaces active JSON atomically; pre-first-observation means
    # no confirmation is available, not an authority PASS. Its traced stop can
    # only become finite PENDING in SharedOwnership.
    try:
        with Path(active_path).open('r') as stream:
            data = json.load(stream)
    except FileNotFoundError:
        return {'guard': current, 'ownership': {'confirmed': [], 'pending': []},
                'age_seconds': 0, 'registered_source_and_launch_verified': True,
                'first_observation_missing': True}
    require(data['guard']['pid'] == launch['pid'] and
            data['guard']['start_ticks'] == launch['start_ticks'], 'PEER_OBSERVER_INSTANCE_CHANGED')
    age = (now_ns - data['monotonic_ns']) / 1e9
    require(0 <= age <= CONFIRM_SECONDS, 'PEER_OWNERSHIP_SNAPSHOT_STALE')
    return {'guard': current, 'ownership': data['ownership'], 'age_seconds': age,
            'registered_source_and_launch_verified': True,
            'first_observation_missing': False}


def bind_current_review(local, identity_reader, peer_provider, project_CPU_tracees=False,
                        exact_controller_roles_provider=None, external_launch_view_provider=None):
    """Create the exact frozen-review callback; no dispatch permission.

    peer_provider supplies verified_peer_view outputs from the sole manager's
    current Popen registrations. It is intentionally injected: a global scanner
    must never discover/adopt another root by name, path or PPID.
    """
    from legacy_authority_runtime import (bind_frozen_procedures, DATA,
                                          exact_legacy_output_sources)
    contracts = json.loads((Path(__file__).parent / 'EXACT_EXTERNAL_ROLE_CONTRACTS.json').read_text())
    proc, snapshot, legacy_review = bind_frozen_procedures()
    shared = SharedOwnership(local, identity_reader)
    legacy_sources = exact_legacy_output_sources()
    def review_now(own_owner):
        shared.update_peers(peer_provider())
        current = snapshot()
        classification = current
        if project_CPU_tracees:
            # Same declared projection used by frozen AG4 CPU qualification:
            # all /proc identity and parent-event proofs remain actual. The
            # untouched original snapshot is returned for resource accounting.
            candidate_tracers = {local.tracer} | {p['guard']['pid'] for p in shared.peers}
            processes = []
            for process in current['processes']:
                row = dict(process)
                try:
                    live = identity_reader(row['pid'])
                except FileNotFoundError:
                    continue
                if live['start_ticks'] != row['start_ticks']:
                    continue
                if row['pid'] in local.confirmed or live['tracer_pid'] in candidate_tracers:
                    row['is_simulator'] = True
                    row['declared_CPU_candidate_projection'] = True
                processes.append(row)
            classification = dict(current, processes=processes)
        controls = contracts['roles'] + (exact_controller_roles_provider() if exact_controller_roles_provider else [])
        result = review_with_exact_roles(classification, legacy_review, own_owner, shared,
                                         controls, identity_reader, DATA,
                                         legacy_sources,
                                         external_launch_view=(external_launch_view_provider() if external_launch_view_provider else None),
                                         require_external_launch_binding=True,
                                         callback_sample_id=str(time.monotonic_ns()))
        return current, result
    return review_now
